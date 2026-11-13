#!/usr/bin/env python3
"""slack_mention_bot.py — 슬랙에서 @봇 멘션으로 들어온 질문에, 정해 둔 자료만 근거로 Claude가 답해 스레드에 단다.

표준 라이브러리만 사용 (Socket Mode WebSocket 직접 구현). 같은 폴더의 config.json · system-prompt.md 를 읽는다.
  pythonw slack_mention_bot.py              상주 실행 (작업 스케줄러가 창 없이 띄운다)
  python  slack_mention_bot.py --check      토큰 두 개가 맞는지만 확인 (슬랙에 연결하지 않음)
  python  slack_mention_bot.py --context    답변 자료만 출력
  python  slack_mention_bot.py --ask "질문"  슬랙 없이 답변만 시험

- 토큰: config 의 app_token_file (xapp- · connections:write) · bot_token_file (xoxb-), 폴더 secrets_dir (기본 ~/.claude/secrets)
- 답변: claude -p 를 도구 없이 실행 (--tools "" · MCP 끔 · 슬래시 명령 끔 · 세션 저장 안 함) → 파일 · 명령 접근 없음
- 자료: config 의 sources — git_log (커밋 기록, 개인 전용 경로 · 주제 제외) · file (파일 또는 git 특정 시점의 파일)
- 기록: config 의 log_file (기본 ~/.claude/<bot_name>-slack.log, 1MB 넘으면 .1 로 교체)
- 원형: 공유 리포 업데이트 안내 봇 (2026-11-13 실사용)
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

def ask(question):
    ctx = build_context()
    prompt = f"<자료>\n{ctx}\n</자료>\n\n<질문>\n{question}\n</질문>"
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
        else:
            print(f"{label}: 정상 · Socket Mode 연결 주소 발급")
    return 0 if ok else 1

# ── 멘션 처리 ─────────────────────────────────────────────
_sem = threading.Semaphore(2)
_seen, _seen_lock = [], threading.Lock()

def handle(ev, bot_token):
    question = re.sub(r"<@[A-Z0-9]+>", "", ev.get("text", "")).strip() or conf["default_question"]
    channel, thread = ev["channel"], ev.get("thread_ts") or ev["ts"]
    log("질문", channel, ev.get("user"), question[:200])
    with _sem:
        try:
            ans = ask(question)
        except Exception as e:
            log("답변 실패", e)
            ans = conf["fail_message"]
    try:
        r = slack("chat.postMessage", bot_token, {"channel": channel, "thread_ts": thread, "text": ans,
                                                  "unfurl_links": False, "unfurl_media": False})
        log("답변", "ok" if r.get("ok") else r.get("error"), len(ans))
    except Exception as e:
        log("게시 실패", e)

def run():
    try:
        lock = socket.socket(); lock.bind(("127.0.0.1", int(conf["lock_port"])))  # 중복 실행 방지
    except OSError:
        log("이미 실행 중 — 종료"); return
    app_token, bot_token = secret(conf["app_token_file"]), secret(conf["bot_token_file"])
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
    else:
        run()
