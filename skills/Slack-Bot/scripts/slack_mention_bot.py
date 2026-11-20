#!/usr/bin/env python3
"""slack_mention_bot.py — 슬랙에서 @봇 멘션으로 들어온 질문에, 정해 둔 자료만 근거로 Claude가 답해 스레드에 단다.

표준 라이브러리만 사용 (Socket Mode WebSocket 직접 구현). 같은 폴더의 config.json · system-prompt.md 를 읽는다.
  pythonw slack_mention_bot.py              상주 실행 (작업 스케줄러가 창 없이 띄운다)
  python  slack_mention_bot.py --check      토큰 두 개가 맞는지만 확인 (슬랙에 연결하지 않음)
  python  slack_mention_bot.py --context    답변 자료만 출력
  python  slack_mention_bot.py --ask "질문"  슬랙 없이 답변만 시험
  python  slack_mention_bot.py --sim 채널 스레드ts|- 시점ts|now 사용자ID "글"
                                            그 스레드 그 시점에 멘션이 온 것처럼 처리 — 게시 대신 화면 출력

- 토큰: config 의 app_token_file (xapp- · connections:write) · bot_token_file (xoxb-), 폴더 secrets_dir (기본 ~/.claude/secrets)
- 답변: claude -p 를 도구 없이 실행 (--tools "" · MCP 끔 · 슬래시 명령 끔 · 세션 저장 안 함) → 파일 · 명령 접근 없음
- 자료: config 의 sources — git_log (커밋 기록, 개인 전용 경로 · 주제 제외) · file (파일 또는 git 특정 시점의 파일)
- 스레드 맥락: 스레드 안 멘션이면 앞선 대화(최근 30개)를 함께 넘긴다 — 권한 channels:history (비공개 채널 groups:history)
- 질문자 · 전달: 묻는 사람(이름 · 관리자/팀원)을 넘기고, 「@이름 에게 알려 줘」 「이 분한테 답변 드려」면 대상을 멘션해 답한다
  — 대상 = @멘션한 사람 · 그 스레드 참여자(이름 · 「이 분」), 3명까지. 이름 해석은 권한 users:read (없으면 @멘션만)
- 진행 표시: 멘션 글에 ⏳(내용 확인 중) 반응 → 답변을 단 뒤 ✅(답변 완료)로 교체, 실패면 ⚠️
  — 권한 reactions:write (없으면 표시만 빠지고 답변은 동작) · config 의 reactions · reaction_working/done/failed
- 기록: config 의 log_file (기본 ~/.claude/<bot_name>-slack.log, 1MB 넘으면 .1 로 교체)
- 원형: 공유 리포 업데이트 안내 봇 (2026-11-13 실사용 · 2026-11-16 스레드 맥락 · 전달 추가 · 2026-11-17 진행 표시 추가)
"""
import base64, json, os, re, shutil, socket, ssl, struct, subprocess, sys, threading, time, urllib.parse, urllib.request
from datetime import datetime

HOME = os.path.expanduser("~")
BASE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.join(BASE, "config.json")
WORK = os.path.join(BASE, "work")
SYS_PROMPT = os.path.join(BASE, "system-prompt.md")

conf = {
    "bot_name": "my-bot",
    "secrets_dir": os.path.join(HOME, ".claude", "secrets"),
    "app_token_file": "",
    "bot_token_file": "",
    "log_file": "",
    "lock_port": 47900,
    "model": "sonnet",
    "claude_config_dir": "",
    "claude_bin": "",
    "default_question": "최근 업데이트 내역 알려줘",
    "fail_message": "지금은 답변을 만들지 못했습니다. 잠시 뒤 다시 멘션해 주세요.",
    "max_context_chars": 60000,
    "sources": [],
    "owner_user_ids": [],        # 관리자 슬랙 ID — 답변 지침이 질문자 권한(관리자 · 팀원)을 구분할 때 사용
    "thread_context": True,      # 스레드 안 멘션이면 앞선 대화를 자료로 넘김
    "thread_max_messages": 30,
    "thread_max_chars": 6000,
    "deliver": True,             # 「@이름 에게 알려 줘」 「이 분한테 답변 드려」 → 대상 멘션 + 답변
    "deliver_max_targets": 3,
    "reactions": True,           # 진행 표시 — 멘션 글에 ⏳ → 답변 후 ✅ (실패 ⚠️), 이모지 이름은 콜론 없이
    "reaction_working": "hourglass_flowing_sand",
    "reaction_done": "white_check_mark",
    "reaction_failed": "warning",
}
if os.path.exists(CONF):
    with open(CONF, encoding="utf-8") as f:
        conf.update(json.load(f))
name = conf["bot_name"]
conf["app_token_file"] = conf["app_token_file"] or f"{name}-app-token"
conf["bot_token_file"] = conf["bot_token_file"] or f"{name}-bot-token"
LOG = os.path.expanduser(conf["log_file"] or os.path.join(HOME, ".claude", f"{name}-slack.log"))
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_log_lock = threading.Lock()
def log(*a):
    line = datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + " ".join(str(x) for x in a)
    with _log_lock:
        try:
            if os.path.exists(LOG) and os.path.getsize(LOG) > 1_000_000:
                os.replace(LOG, LOG + ".1")
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass
    if sys.stdout is not None:  # pythonw 로 돌 때는 None
        try: print(line, flush=True)
        except Exception: pass

def secret(fname):
    with open(os.path.join(os.path.expanduser(conf["secrets_dir"]), fname), encoding="utf-8") as f:
        return f.read().strip()

# ── Slack Web API ─────────────────────────────────────────
def slack(method, token, payload=None):
    req = urllib.request.Request(
        "https://slack.com/api/" + method,
        data=json.dumps(payload or {}).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json; charset=utf-8"},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

# ── 최소 WebSocket 클라이언트 (RFC 6455) ───────────────────
class WS:
    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        host, port = u.hostname, u.port or 443
        path = u.path + ("?" + u.query if u.query else "")
        raw = socket.create_connection((host, port), timeout=30)
        self.s = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self.s.recv(1)
            if not chunk: raise ConnectionError("handshake closed")
            head += chunk
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise ConnectionError("handshake failed: " + head.split(b"\r\n", 1)[0].decode(errors="replace"))
        self.lock = threading.Lock()
        self.s.settimeout(60)

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk: raise ConnectionError("socket closed")
            buf += chunk
        return buf

    def send(self, data, opcode=1):
        if isinstance(data, str): data = data.encode("utf-8")
        head = bytes([0x80 | opcode])
        n = len(data)
        if n < 126: head += bytes([0x80 | n])
        elif n < 65536: head += bytes([0x80 | 126]) + struct.pack("!H", n)
        else: head += bytes([0x80 | 127]) + struct.pack("!Q", n)
        mask = os.urandom(4)
        body = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        with self.lock:
            self.s.sendall(head + mask + body)

    def recv(self):
        """텍스트 메시지 하나를 돌려준다. ping 은 여기서 pong 으로 답한다. 60초 무수신이면 socket.timeout."""
        parts, op0 = [], None
        while True:
            b0, b1 = self._read(2)
            op, ln = b0 & 0x0F, b1 & 0x7F
            if ln == 126: ln = struct.unpack("!H", self._read(2))[0]
            elif ln == 127: ln = struct.unpack("!Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            data = self._read(ln) if ln else b""
            if mask: data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if op == 9: self.send(data, 10); continue
            if op == 10: continue
            if op == 8: raise ConnectionError("server close")
            if op in (1, 2): op0, parts = op, [data]
            elif op == 0: parts.append(data)
            if b0 & 0x80 and op0 is not None:
                return b"".join(parts).decode("utf-8", errors="replace")

    def close(self):
        try: self.s.close()
        except OSError: pass

# ── 답변 자료 (config 의 sources) ──────────────────────────
def git(repo, *args, timeout=30):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
    return r.stdout.decode("utf-8", errors="replace")

def strip_md(t):
    t = re.sub(r"<img[^>]*>", "", t)
    return re.sub(r"</?(sub|div|br)[^>]*>", "", t)

def area_of(path):
    """변경 영역 이름: agent/proposal/README.md → agent/proposal · README.md → README.md"""
    parts = path.split("/")
    return "/".join(parts[:2]) if len(parts) >= 3 else parts[0]

def src_git_log(s):
    """커밋 기록. exclude_paths 경로만 바꾼 커밋은 빼고, private_pattern 주제의 커밋 · 본문 줄도 뺀다."""
    repo, ref = os.path.expanduser(s["repo"]), s.get("ref", "HEAD")
    if s.get("fetch", True):
        try: git(repo, "fetch", "-q", "origin", timeout=40)
        except Exception as e: log("fetch 실패", repo, e)
    excl = re.compile(s["exclude_paths"]) if s.get("exclude_paths") else None
    priv = re.compile(s["private_pattern"], re.I) if s.get("private_pattern") else None
    raw = git(repo, "log", ref, "-n", str(s.get("count", 40)), "--date=format:%Y-%m-%d", "--name-only",
              "--format=%x1e%h%x09%ad%x09%s%n%b%x1f")
    rows = []
    for c in raw.split("\x1e"):
        c = c.strip()
        if not c: continue
        head, _, files = c.partition("\x1f")
        fl = [f.strip() for f in files.splitlines() if f.strip() and not (excl and excl.match(f.strip()))]
        if not fl: continue
        first, _, body = head.strip().partition("\n")
        sha, date, subj = (first.split("\t") + ["", ""])[:3]
        if priv and priv.search(subj.split(":", 1)[0]): continue
        if priv: subj = priv.sub("(개인 설정)", subj)
        bl = [l for l in body.splitlines() if l.startswith("- ") and not (priv and priv.search(l))]
        areas = sorted({area_of(f) for f in fl})
        rows.append(f"- {date} {sha} {subj}  [변경 영역: {', '.join(areas[:6])}]" + "".join("\n  " + l for l in bl))
    return "\n".join(rows)

def src_file(s):
    """파일 내용. repo 를 주면 git 의 ref 시점 파일(git show), start/end 를 주면 그 사이만, private_pattern 줄은 뺀다."""
    if s.get("repo"):
        repo = os.path.expanduser(s["repo"])
        if s.get("fetch", False):
            try: git(repo, "fetch", "-q", "origin", timeout=40)
            except Exception as e: log("fetch 실패", repo, e)
        text = git(repo, "show", f"{s.get('ref', 'HEAD')}:{s['path']}")
    else:
        with open(os.path.expanduser(s["path"]), encoding="utf-8", errors="replace") as f:
            text = f.read()
    if s.get("start") and s.get("end"):
        i = text.find(s["start"])
        if i < 0: return ""
        i = text.find("\n", i) + 1
        j = text.find(s["end"], i)
        text = text[i:j if j >= 0 else None]
    if s.get("private_pattern"):
        priv = re.compile(s["private_pattern"], re.I)
        text = "\n".join(l for l in text.splitlines() if not priv.search(l))
    return strip_md(text)[: int(s.get("max_chars", 15000))]

def build_context():
    out = []
    for s in conf.get("sources", []):
        title = s.get("title") or s.get("type", "자료")
        try:
            if s.get("type") == "git_log": body = src_git_log(s)
            elif s.get("type") == "file": body = src_file(s)
            else: log("알 수 없는 자료 형식", s.get("type")); continue
        except Exception as e:
            log("자료 읽기 실패", title, type(e).__name__, e); continue
        if body.strip(): out.append(f"## {title}\n{body.strip()}")
    return "\n\n".join(out)[: int(conf["max_context_chars"])]

def claude_bin():
    if conf.get("claude_bin"): return os.path.expanduser(conf["claude_bin"])
    found = shutil.which("claude")
    if found: return found
    for p in (os.path.join(HOME, ".local", "bin", "claude.exe"), os.path.join(HOME, ".local", "bin", "claude")):
        if os.path.exists(p): return p
    return "claude"

# ── 스레드 맥락 · 사람 · 멘션 전달 ─────────────────────────
BOT = {"uid": "", "bot_id": ""}  # run() · --sim 에서 auth.test 로 채운다
MENTION = re.compile(r"<@([UW][A-Z0-9]+)(?:\|[^>]*)?>")

def slack_get(method, token, params):
    """읽기 API(conversations.replies · users.list)는 쿼리 문자열로 보낸다"""
    req = urllib.request.Request("https://slack.com/api/" + method + "?" + urllib.parse.urlencode(params),
                                 headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def load_bot_identity(token):
    try:
        r = slack("auth.test", token)
        BOT.update(uid=r.get("user_id", ""), bot_id=r.get("bot_id", ""))
    except Exception as e:
        log("auth.test 실패", e)
    return BOT["uid"]

_users, _users_lock = {"at": 0.0, "list": [], "denied": False}, threading.Lock()

def users_dir(token):
    """워크스페이스 사람 목록 [{id, name, names}] — 메모리에 하루 보관. users:read 권한이 없으면 빈 목록(1시간 뒤 재시도)"""
    with _users_lock:
        age = time.time() - _users["at"]
        if (_users["list"] and age < 86400) or (_users["denied"] and age < 3600):
            return _users["list"]
        out, cursor = [], ""
        try:
            for _ in range(20):
                p = {"limit": 200}
                if cursor: p["cursor"] = cursor
                r = slack_get("users.list", token, p)
                if not r.get("ok"):
                    log("사람 목록 읽기 실패", r.get("error"), r.get("needed") or "")
                    _users.update(at=time.time(), denied=True); return _users["list"]
                for u in r.get("members", []):
                    if u.get("deleted") or u.get("is_bot") or u.get("id") == "USLACKBOT": continue
                    pr = u.get("profile") or {}
                    names = {x.strip() for x in (pr.get("display_name"), pr.get("real_name"), u.get("real_name"),
                                                 pr.get("display_name_normalized"), pr.get("real_name_normalized")) if x and x.strip()}
                    out.append({"id": u["id"], "name": (pr.get("display_name") or pr.get("real_name") or u.get("real_name")
                                                        or u.get("name") or u["id"]).strip(), "names": sorted(names, key=len, reverse=True)})
                cursor = (r.get("response_metadata") or {}).get("next_cursor")
                if not cursor: break
        except Exception as e:
            log("사람 목록 읽기 오류", type(e).__name__, e); return _users["list"]
        _users.update(at=time.time(), list=out, denied=False)
        return out

def user_entry(uid, token):
    return next((u for u in users_dir(token) if u["id"] == uid), None)

def is_owner(uid):
    return bool(uid) and uid in set(conf.get("owner_user_ids") or [])

def label_of(uid, token, labels):
    """사람 표시 — 이름(권한 없으면 「참여자N」) + 관리자 · 팀원"""
    if uid and uid == BOT["uid"]: return f"{conf['bot_name']}(봇)"
    e = user_entry(uid, token)
    nm = e["name"] if e else labels.setdefault(uid, f"참여자{len(labels) + 1}")
    return f"{nm}({'관리자' if is_owner(uid) else '팀원'})"

def readable(text, token, labels):
    """슬랙 원문 → 읽는 글: <@U…> → @이름 · <!here> → @here · <주소|문구> → 문구(주소)"""
    def rep(m):
        u = m.group(1)
        if u == BOT["uid"]: return "@" + conf["bot_name"]
        e = user_entry(u, token)
        return "@" + (e["name"] if e else labels.setdefault(u, f"참여자{len(labels) + 1}"))
    t = MENTION.sub(rep, text or "")
    t = re.sub(r"<!(channel|here|everyone)[^>]*>", r"@\1", t)
    t = re.sub(r"<!subteam\^[A-Z0-9]+(?:\|([^>]*))?>", lambda m: m.group(1) or "@그룹", t)
    t = re.sub(r"<(https?://[^|>]+)\|([^>]+)>", r"\2(\1)", t)
    t = re.sub(r"<(https?://[^>]+)>", r"\1", t)
    return t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

def clean_text(raw, token):
    """질문 본문 — 봇 멘션만 지우고 다른 사람 멘션은 @이름으로 남긴다(전부 지우면 전달 대상이 사라진다)"""
    if not BOT["uid"]:
        raw = MENTION.sub("", raw or "", count=1)  # 봇 ID를 모르면 첫 멘션을 봇으로 본다
    else:
        raw = re.sub(r"<@%s(?:\|[^>]*)?>" % re.escape(BOT["uid"]), "", raw or "")
    return readable(raw, token, {}).strip()

def is_bot_msg(m):
    return bool(m.get("bot_id")) or (BOT["uid"] and m.get("user") == BOT["uid"])

def thread_messages(channel, thread_ts, upto_ts, token):
    """스레드에서 이번 메시지 앞까지 (conversations.replies)"""
    msgs, cursor = [], ""
    for _ in range(5):
        p = {"channel": channel, "ts": thread_ts, "limit": 200}
        if cursor: p["cursor"] = cursor
        r = slack_get("conversations.replies", token, p)
        if not r.get("ok"):
            log("스레드 읽기 실패", r.get("error"), r.get("needed") or ""); break
        msgs += r.get("messages", [])
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor: break
    return [m for m in msgs if float(m.get("ts", 0)) < float(upto_ts or 9e12)]

def thread_block(msgs, token, labels):
    """<스레드_대화> — 최근 N개 · 글자 수 상한, 넘치면 첫 글(스레드 시작)은 두고 오래된 것부터 뺀다"""
    n, cap = int(conf["thread_max_messages"]), int(conf["thread_max_chars"])
    pick = msgs if len(msgs) <= n else [msgs[0]] + msgs[-(n - 1):]
    lines = []
    for m in pick:
        who = f"{conf['bot_name']}(봇)" if is_bot_msg(m) else label_of(m.get("user"), token, labels)
        t = readable(m.get("text", ""), token, labels).strip()
        if len(t) > 700: t = t[:700] + "…"
        lines.append(f"[{datetime.fromtimestamp(float(m['ts'])).strftime('%m/%d %H:%M')}] {who}: {t}")
    while len(lines) > 2 and sum(len(l) + 1 for l in lines) > cap:
        lines.pop(1)
    return "\n".join(lines)

# 전달 지시 — 동사(답 · 전달 · 설명 · 알려 …) + 받는 사람 표시(~한테 · ~에게 · ~께 · 이 분 · ←)
DELIVER_VERB = re.compile(r"(답|대답|답변|회신|전달|설명|안내|알려|말해|공유|보내)")
DELIVER_ADDR = re.compile(r"(한테|에게|께)(?:\s|도|는|만|$)|←|^\s*전달\s*[:：]")
DEICTIC = re.compile(r"(이|그|저)\s*(분|사람)|(질문|문의)\s*(하신|한)\s*분|물어\s*(보신|본)\s*분")

def name_in(name, low):
    """이름이 글에 있는지 — 한글 이름은 2자 이상, 영문은 3자 이상 · 단어 경계"""
    n = (name or "").strip().lower()
    if not n: return False
    if n.isascii():
        return len(n) >= 3 and re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", low) is not None
    return len(n) >= 2 and n in low

def find_targets(raw, text, requester, participants, token):
    """전달 대상 → (계정 ID 목록, 되물을 문구)"""
    if not conf.get("deliver", True): return [], ""
    mx = int(conf["deliver_max_targets"])
    verb, addr = DELIVER_VERB.search(text), DELIVER_ADDR.search(text) or DEICTIC.search(text)
    explicit = []
    for u in MENTION.findall(raw or ""):
        if u not in (BOT["uid"], requester) and u not in explicit: explicit.append(u)
    if explicit:  # 「@대상 가 만든 스킬 뭐야?」처럼 사람을 화제로만 꺼낸 경우는 전달이 아니다
        return (explicit[:mx], "") if (verb or addr) else ([], "")
    if not (verb and addr): return [], ""
    others = [u for u in participants if u not in (requester, BOT["uid"])]
    low = text.lower()
    named = [u for u in others if any(name_in(n, low) for n in ((user_entry(u, token) or {}).get("names") or []))]
    if named: return named[:mx], ""
    outside = [e for e in users_dir(token) if e["id"] not in others and e["id"] != requester and any(name_in(n, low) for n in e["names"])]
    if outside:
        nm = outside[0]["name"]
        return [], f"{nm}님은 이 스레드 참여자가 아니라 이름만으로는 부르지 않습니다 — `@{nm}`처럼 @멘션으로 지정해 주세요"
    if DEICTIC.search(text) and len(others) == 1:
        return others, ""
    if DEICTIC.search(text) or "←" in text:
        lab = {}
        names = ", ".join(label_of(u, token, lab) for u in others[:5])
        return [], "누구에게 답할지 정하지 못했습니다 — `@이름`으로 멘션해 주세요" + (f" (이 스레드 참여자: {names})" if names else "")
    return [], ""

def target_block(targets, msgs, token, labels):
    """<전달_대상> — 대상과 그 사람이 이 스레드에서 한 말(최근 3개, 웃음 · 감탄만 있는 글 제외)"""
    L = []
    for u in targets:
        said = [readable(m.get("text", ""), token, labels).strip() for m in msgs if m.get("user") == u and not is_bot_msg(m)]
        said = [s for s in said if len(re.sub(r"[ㅋㅎㅠㅜ\s.,!?~^]", "", s)) >= 2][-3:]
        L.append(f"- {label_of(u, token, labels)} — 이 스레드에서 한 말: " +
                 (" / ".join(f"「{s[:300]}」" for s in said) if said else "없음(지시 문장에 담긴 내용을 전한다)"))
    return "\n".join(L)

def sanitize(ans):
    """답변에서 사람 · 채널 호출 제거 — 멘션은 프로그램이 대상에게만 붙인다"""
    ans = re.sub(r"<!(channel|here|everyone)(?:\|[^>]*)?>", r"\1", ans)
    ans = re.sub(r"<!subteam\^[A-Z0-9]+(?:\|([^>]*))?>", lambda m: m.group(1) or "그룹", ans)
    return MENTION.sub("", ans)

def ask(question, thread="", asker="", target=""):
    """답변 — thread = 스레드 앞선 대화 · asker = 질문자(이름 · 관리자/팀원) · target = 전달 대상과 그 사람이 한 말"""
    ctx = build_context()
    parts = [f"<자료>\n{ctx}\n</자료>"]
    if thread: parts.append(f"<스레드_대화>\n{thread}\n</스레드_대화>")
    if asker: parts.append(f"<질문자>{asker}</질문자>")
    if target: parts.append(f"<전달_대상>\n{target}\n</전달_대상>")
    parts.append(f"<질문>\n{question}\n</질문>")
    prompt = "\n\n".join(parts)
    env = dict(os.environ)
    if conf.get("claude_config_dir"): env["CLAUDE_CONFIG_DIR"] = os.path.expanduser(conf["claude_config_dir"])
    os.makedirs(WORK, exist_ok=True)
    cmd = [claude_bin(), "-p", "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
           "--no-session-persistence", "--model", conf["model"], "--system-prompt-file", SYS_PROMPT]
    r = subprocess.run(cmd, input=prompt.encode("utf-8"), capture_output=True, timeout=240, cwd=WORK, env=env,
                       creationflags=NO_WINDOW)
    ans = r.stdout.decode("utf-8", errors="replace").strip()
    if r.returncode != 0 or not ans:
        raise RuntimeError(f"claude rc={r.returncode} err={r.stderr.decode('utf-8', errors='replace')[:300]}")
    return ans

# ── 토큰 확인 ─────────────────────────────────────────────
def check():
    ok = True
    for label, fname, method in (("봇 토큰", conf["bot_token_file"], "auth.test"),
                                 ("앱 토큰", conf["app_token_file"], "apps.connections.open")):
        try:
            r = slack(method, secret(fname))
        except Exception as e:
            print(f"{label}: 확인 실패 · {fname} · {type(e).__name__} {e}"); ok = False; continue
        if not r.get("ok"):
            print(f"{label}: 오류 · {fname} · {r.get('error')}"); ok = False
        elif method == "auth.test":
            print(f"{label}: 정상 · 봇 {r.get('user')} · 워크스페이스 {r.get('team')}")
            try:  # 선택 권한 — 없으면 해당 기능만 빠지고 답변은 동작
                req = urllib.request.Request("https://slack.com/api/auth.test",
                                             headers={"Authorization": "Bearer " + secret(fname)}, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    scopes = set((resp.headers.get("x-oauth-scopes") or "").split(","))
                for sc, what in (("channels:history", "스레드 맥락(공개 채널)"), ("users:read", "이름으로 전달 대상 지정"),
                                 ("reactions:write", "진행 표시(⏳ → ✅)")):
                    print(f"  권한 {sc}: {'있음' if sc in scopes else '없음 — ' + what + ' 미동작'}")
            except Exception as e:
                print(f"  권한 확인 실패 · {type(e).__name__}")
        else:
            print(f"{label}: 정상 · Socket Mode 연결 주소 발급")
    return 0 if ok else 1

# ── 멘션 처리 ─────────────────────────────────────────────
_sem = threading.Semaphore(2)
_seen, _seen_lock = [], threading.Lock()

def post(bot_token, channel, thread, text):
    if SIM["on"]:
        print(f"\n──── [게시 예정 · {channel} · 스레드 {thread}] ────\n{text}\n", flush=True); return True
    try:
        r = slack("chat.postMessage", bot_token, {"channel": channel, "thread_ts": thread, "text": text,
                                                  "unfurl_links": False, "unfurl_media": False})
        if not r.get("ok"): log("게시 실패", r.get("error"))
        return bool(r.get("ok"))
    except Exception as e:
        log("게시 오류", e); return False

SIM = {"on": False}

_react = {"denied_at": 0.0}

def react(token, channel, ts, add="", remove=""):
    """진행 표시 — 멘션 글의 이모지 반응 교체(add 를 붙이고 remove 를 뗀다). 실패해도 답변은 그대로 진행"""
    if not conf.get("reactions", True) or not ts: return
    if remove == add: remove = ""
    if SIM["on"]:
        acts = [x for x in ((f"+:{add}:" if add else ""), (f"-:{remove}:" if remove else "")) if x]
        if acts: print(f"[반응 · {channel} · 글 {ts}] {' '.join(acts)}", flush=True)
        return
    if time.time() - _react["denied_at"] < 3600: return  # 권한 없음 — 1시간 뒤 재시도
    for method, nm in (("reactions.add", add), ("reactions.remove", remove)):
        if not nm: continue
        try:
            r = slack(method, token, {"channel": channel, "timestamp": ts, "name": nm})
        except Exception as e:
            log("반응 오류", method, type(e).__name__, e); continue
        err = r.get("error")
        if r.get("ok") or err in ("already_reacted", "no_reaction"): continue
        log("반응 실패", method, nm, err, r.get("needed") or "")
        if err == "missing_scope":
            _react["denied_at"] = time.time(); return

def handle(ev, bot_token):
    """멘션 1건 — 받자마자 ⏳, 답을 단 뒤 ✅ · 답변 실패 · 게시 실패 · 처리 오류면 ⚠️"""
    channel, ts = ev["channel"], ev.get("ts")
    react(bot_token, channel, ts, add=conf.get("reaction_working", ""))
    ok = False
    try:
        ok = answer(ev, bot_token)
    except Exception as e:
        log("처리 오류", type(e).__name__, e)
    react(bot_token, channel, ts, add=conf.get("reaction_done" if ok else "reaction_failed", ""),
          remove=conf.get("reaction_working", ""))

def answer(ev, bot_token):
    """질문 읽기 → 답변 → 스레드 게시. 답변을 제대로 달았으면 True"""
    question = clean_text(ev.get("text", ""), bot_token) or conf["default_question"]
    channel, thread, user = ev["channel"], ev.get("thread_ts") or ev["ts"], ev.get("user")
    msgs, labels = [], {}
    if ev.get("thread_ts") and conf.get("thread_context", True):
        try: msgs = thread_messages(channel, ev["thread_ts"], ev.get("ts"), bot_token)
        except Exception as e: log("스레드 읽기 오류", type(e).__name__, e)
    participants = []
    for m in msgs:
        u = m.get("user")
        if u and not is_bot_msg(m) and u not in participants: participants.append(u)
    try:
        targets, note = find_targets(ev.get("text", ""), question, user, participants, bot_token)
    except Exception as e:
        log("전달 대상 판별 오류", type(e).__name__, e); targets, note = [], ""
    if note:
        log("전달 대상 확인 요청", channel, user, question[:120]); return post(bot_token, channel, thread, note)
    asker = label_of(user, bot_token, labels).replace("(", " · ").rstrip(")")
    log("질문", channel, user, question[:200], ("→ 전달 " + ",".join(targets)) if targets else "", f"스레드 {len(msgs)}개" if msgs else "")
    made = True
    with _sem:
        try:
            ans = sanitize(ask(question, thread_block(msgs, bot_token, labels), asker, target_block(targets, msgs, bot_token, labels)))
        except Exception as e:
            log("답변 실패", e)
            ans, made = conf["fail_message"], False
    if targets:
        ans = " ".join(f"<@{u}>" for u in targets) + " " + ans
    posted = post(bot_token, channel, thread, ans)
    log("답변", "ok" if posted else "실패", len(ans))
    return made and posted

def simulate(argv):
    """--sim 채널 스레드ts|- 시점ts|now 사용자ID 글 — 그 스레드 그 시점에 멘션이 온 것처럼 처리, 게시 대신 화면 출력"""
    ch, tts, at, uid, text = argv[0], argv[1], argv[2], argv[3], " ".join(argv[4:])
    token = secret(conf["bot_token_file"])
    load_bot_identity(token)
    SIM["on"] = True
    ev = {"channel": ch, "user": uid, "text": f"<@{BOT['uid']}> {text}", "ts": f"{time.time():.6f}" if at == "now" else at}
    if tts != "-": ev["thread_ts"] = tts
    handle(ev, token)

def run():
    try:
        lock = socket.socket(); lock.bind(("127.0.0.1", int(conf["lock_port"])))  # 중복 실행 방지
    except OSError:
        log("이미 실행 중 — 종료"); return
    app_token, bot_token = secret(conf["app_token_file"]), secret(conf["bot_token_file"])
    load_bot_identity(bot_token)
    backoff = 5
    while True:
        ws = None
        try:
            r = slack("apps.connections.open", app_token)
            if not r.get("ok"): raise RuntimeError("connections.open: " + str(r.get("error")))
            ws = WS(r["url"]); idle = 0
            log("연결")
            while True:
                try:
                    msg = json.loads(ws.recv()); idle = 0
                except socket.timeout:
                    idle += 1
                    if idle >= 3: raise ConnectionError("응답 없음 — 재연결")
                    ws.send(b"", 9); continue
                if msg.get("envelope_id"):
                    ws.send(json.dumps({"envelope_id": msg["envelope_id"]}))
                t = msg.get("type")
                if t == "hello": backoff = 5
                elif t == "disconnect":
                    log("disconnect", msg.get("reason")); break
                elif t == "events_api":
                    p = msg.get("payload", {}); ev = p.get("event", {})
                    eid = p.get("event_id")
                    with _seen_lock:
                        if eid in _seen: continue
                        _seen.append(eid); del _seen[:-200]
                    if ev.get("type") == "app_mention" and not ev.get("bot_id"):
                        threading.Thread(target=handle, args=(ev, bot_token), daemon=True).start()
        except Exception as e:
            log("연결 오류", type(e).__name__, e)
            time.sleep(backoff); backoff = min(backoff * 2, 120)
        finally:
            if ws: ws.close()

if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8")
        except Exception: pass
    if len(sys.argv) >= 3 and sys.argv[1] == "--ask":
        print(ask(" ".join(sys.argv[2:])))
    elif len(sys.argv) >= 2 and sys.argv[1] == "--context":
        print(build_context())
    elif len(sys.argv) >= 2 and sys.argv[1] == "--check":
        sys.exit(check())
    elif len(sys.argv) >= 7 and sys.argv[1] == "--sim":
        simulate(sys.argv[2:])
    else:
        run()
