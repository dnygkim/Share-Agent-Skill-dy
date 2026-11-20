#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corpus.py — 산출물 집단기억(corpus) 동기화·검색·저장 엔진.

브랜치 분리: 도구 코드는 `etribe` 브랜치, corpus 데이터는 **별도 `corpus` 브랜치**(orphan).
corpus.py는 gitignored `.corpus/`(= corpus 브랜치만 single-branch 클론)에서 읽고/쓰고/push한다.
→ 도구 브랜치(etribe)가 산출물 커밋으로 더러워지지 않는다.

.corpus/                                       # = corpus 브랜치 루트 (섹션 원자 구조)
  INDEX.md                                     # 진입점(케이스→프로젝트→패턴)
  index.jsonl                                  # 1줄=1산출물 메타(append-only) — search는 이것만 읽음
  cases/{유형}.md                              # 케이스 종합(범위·확인·공수 밴드)
  estimates/ scope/ questions/ ia/ approach/ direction/ overview/ infra/   # 프로젝트별 섹션 원자
  dev-notes/decisions/{id}.md                  # 설계 의도·결정 이력
  patterns/{slug}.md                           # 프로젝트 횡단 재사용
  deliverables/{id}/report.html + workspace/   # 원본 풀 산출물 + 중간물 미러
  # 커밋: 원자 단위 kb({type}):{id}|… + 태그 kb/{id} (한 덩어리 통커밋 금지)

id 규칙(권장): `{고객slug}-{주제slug}[-vN]` (예: woongjin-direct, snu-sdn). 같은 프로젝트 재작업은
  같은 id로 덮어써 최신화, 완전 별건은 새 id. ORCHESTRATOR가 시작 시 id 확정 → snapshot/save 동일 id 사용.

서브커맨드:
    pull                                  # corpus 브랜치 클론/갱신
    search --domain X --tags a,b,c [--top 5]   # index.jsonl만 조회(중간물 스냅샷은 검색에 안 잡힘)
    snapshot --id ID --ws _workspace/{slug} [--stage NAME]  # 단계/게이트 완료 시 중간물 커밋(index 불변)
    save --html PATH --meta META.json [--ws _workspace/{slug}]  # 최종 환원: 섹션 원자별 커밋 + report + 태그
    put-html --id ID --html PATH [--note "사유"]          # 최종 HTML 생성/수정 시 빠른 버전 커밋·push(태그 이동)
    get --id ID [--out PATH] [--rev 태그/해시]            # 최신(또는 특정 버전) HTML 받아 보기 + 버전 이력

.env(gitignored): CORPUS_GIT_TOKEN, CORPUS_GIT_REMOTE, CORPUS_GIT_BRANCH(기본 corpus).
토큰은 GitLab 표준 oauth2:<token> 으로 주입. 절대 커밋 금지.
"""
import sys, os, json, subprocess, argparse, shutil

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.path.join(ROOT, ".corpus")          # corpus 브랜치 클론(gitignored)
INDEX = os.path.join(CDIR, "index.jsonl")
DELIV = os.path.join(CDIR, "deliverables")


def _env(key, default=None):
    envf = os.path.join(ROOT, ".env")
    if os.path.isfile(envf):
        with open(envf, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == key:
                        return v.strip().strip('"').strip("'")
    return os.environ.get(key, default)


def _branch():
    return _env("CORPUS_GIT_BRANCH") or "corpus"


def _clean_remote():
    r = _env("CORPUS_GIT_REMOTE")
    if not r:
        g = subprocess.run(["git", "-C", ROOT, "remote", "get-url", "origin"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        r = g.stdout.strip() if g.returncode == 0 else ""
    return r


def _authed(remote):
    token = _env("CORPUS_GIT_TOKEN")
    if token and remote.startswith(("http://", "https://")):
        rest = remote.split("://", 1)[1]
        return f"https://oauth2:{token}@{rest}"   # GitLab 표준, https 강제
    return remote


def _gitc(*args, check=False):
    r = subprocess.run(["git", "-C", CDIR, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.stderr.write(f"[git -C .corpus {' '.join(args)}] {r.stderr.strip()}\n")
    return r


def _ensure(pull=True):
    """corpus 브랜치를 .corpus/ 에 준비(없으면 클론, 있으면 갱신). 실패해도 best-effort."""
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    if os.path.isdir(os.path.join(CDIR, ".git")):
        if pull:
            _gitc("pull", "--rebase", authed, br)
        return True
    # 최초: corpus 브랜치만 single-branch 클론
    r = subprocess.run(["git", "clone", "--branch", br, "--single-branch", authed, CDIR],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write(f"[clone corpus 실패] {r.stderr.strip()}\n")
        return False
    _gitc("remote", "set-url", "origin", remote)         # 토큰 없는 clean URL로 교체
    _gitc("config", "user.email", "harness@etribe.local")
    _gitc("config", "user.name", "harness-agent")
    return True


def _commit_push(msg):
    """변경분을 corpus 브랜치에 commit + push(충돌 대비 pull --rebase 후 1회 재시도)."""
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    _gitc("add", "-A")
    c = _gitc("commit", "-m", msg)
    if c.returncode != 0 and "nothing to commit" in (c.stdout + c.stderr):
        return True, "변경 없음(스냅샷 동일)"
    _gitc("pull", "--rebase", authed, br)
    r = _gitc("push", authed, f"HEAD:{br}")
    if r.returncode != 0:
        _gitc("pull", "--rebase", authed, br)
        r = _gitc("push", authed, f"HEAD:{br}")
    return r.returncode == 0, (r.stderr.strip() if r.returncode != 0 else "")


def _mirror_ws(mid, ws):
    """_workspace/{slug} 전체를 deliverables/{id}/workspace/ 로 미러(최신 상태로 덮어씀)."""
    if not ws or not os.path.isdir(ws):
        return False
    dest = os.path.join(DELIV, mid, "workspace")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    # report 중간본(html)·spec(json)·분석(md) 등 작업물 일체. __pycache__ 류만 제외.
    shutil.copytree(ws, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    return True


def cmd_pull(_):
    ok = _ensure(pull=True)
    if ok:
        print("[OK] corpus 준비됨 (.corpus/)")
    elif not _env("CORPUS_GIT_TOKEN"):
        print("[WARN] corpus 미연결 — .env의 CORPUS_GIT_TOKEN 없음(테스트 폴더는 .env 필요). 선례 참조 없이 진행")
    else:
        print("[WARN] corpus 미연결(오프라인/원격 오류) — 로컬 캐시로 진행")
    return 0


def cmd_snapshot(a):
    """작업 중간물 스냅샷 — 단계/게이트 완료 시 _workspace를 corpus에 커밋(검색 인덱스는 불변)."""
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패 — 스냅샷 보류(중간물은 _workspace/에 안전)", file=sys.stderr)
        return 1
    if not _mirror_ws(a.id, a.ws):
        print(f"[ERROR] 작업폴더 없음: {a.ws}", file=sys.stderr)
        return 1
    stage = f" [{a.stage}]" if a.stage else ""
    ok, note = _commit_push(f"kb(snapshot): {a.id} [{a.stage or 'gate'}]")
    print(f"[OK] 중간물 스냅샷: {a.id}{stage} ({note or _branch()})" if ok
          else f"[WARN] .corpus 로컬 저장됨, push 실패(나중 재시도 가능): {note}")
    return 0


def _load_index():
    rows = []
    if os.path.isfile(INDEX):
        with open(INDEX, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: rows.append(json.loads(line))
                    except json.JSONDecodeError: pass
    return rows


def cmd_search(a):
    _ensure(pull=True)
    # 쿼리 토큰: --tags + 자유어(positional query 또는 --q). 공백·쉼표 모두 분리.
    qpos = " ".join(a.query) if isinstance(getattr(a, "query", None), list) else (getattr(a, "query", "") or "")
    raw = " ".join(filter(None, [a.tags or "", getattr(a, "q", "") or "", qpos]))
    terms = [t.strip().lower() for t in raw.replace(",", " ").split() if t.strip()]
    scored = []
    for row in _load_index():
        feats = [str(f).lower() for f in (row.get("features") or row.get("tags") or [])]
        blob = " ".join(str(row.get(k, "")) for k in
                        ("topic", "domain", "project_case", "scope_in", "type", "doc_type")).lower() + " " + " ".join(feats)
        score = 0
        for t in terms:                       # ★ 부분매칭: '리뉴얼'이 '홈페이지리뉴얼'에도 걸림
            if any(t in f or f in t for f in feats): score += 2   # 태그/feature 매칭 가중
            elif t in blob: score += 1                            # 본문(topic·domain·scope) 매칭
        if a.domain and a.domain.lower() in (row.get("domain", "") or "").lower():
            score += 2
        if a.type and a.type == row.get("type"):
            score += 1
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda x: -x[0])
    top = scored[: a.top]
    if not top:
        print("[]  (유사 과거 산출물 없음 - 신규 패턴)")
        return 0
    out = []
    for s, r in top:
        est, act = r.get("total_mm"), r.get("actual_mm")
        rid = r["id"]
        path = r.get("path")
        # 새 산출물 작성에 바로 쓰는 참고 카드: 밴드(공수/기간/인원)+직군+범위+케이스+교훈
        item = {"score": s, "id": rid, "topic": r.get("topic"),
                "type": r.get("type"), "domain": r.get("domain"), "project_case": r.get("project_case"),
                "total_mm": est, "actual_mm": act, "months": r.get("months"), "headcount": r.get("headcount"),
                "role_breakdown": r.get("role_breakdown"),
                "design_level": r.get("design_level"), "staffing": r.get("staffing"),
                "scope_in": r.get("scope_in"), "scope_out": r.get("scope_out"),
                "data_gaps": r.get("data_gaps"), "confidence": r.get("confidence"),
                "lesson": r.get("lesson"), "features": r.get("features"),
                # 섹션 원자(작고 구조화 — 이것부터). '범위→확인→공수' 사슬.
                "ref_scope": f"scope/{rid}.md", "ref_questions": f"questions/{rid}.md",
                "ref_estimate": f"estimates/{rid}.md", "ref_ia": f"ia/{rid}.md",
                "ref_decision": f"dev-notes/decisions/{rid}.md", "ref_report": path}
        # blind-spot: 과거 실제공수가 산정 대비 20%↑ 초과면 과소산정 경고
        if isinstance(est, (int, float)) and isinstance(act, (int, float)) and est and act > est * 1.2:
            item["⚠️under_estimated"] = f"과거 산정 {est} → 실제 {act} (+{round((act/est-1)*100)}%) — 유사 산정 시 버퍼 검토"
        out.append({k: v for k, v in item.items() if v is not None})
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("\n# 새 건 작성: 먼저 cases/{유형}.md(INDEX 참조)에서 범위·확인·공수 밴드 → 유사 건 ref_scope→ref_questions→ref_estimate 사슬 → patterns/ 적용. report.html은 최후.", file=sys.stderr)
    return 0


def _wfile(rel, text):
    full = os.path.join(CDIR, rel); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text); return rel

def _atoms_from_meta(meta):
    """리치 meta → 섹션 정렬 원자 파일들 생성. (atomtype, [relpaths], 커밋설명) 리스트 반환.
       meta에 해당 섹션 필드가 있을 때만 그 원자를 만든다(없으면 생략)."""
    mid = meta["id"]; cl = meta.get("client",""); case = meta.get("project_case","")
    tags = meta.get("tags") or meta.get("features") or []
    def fm(title, typ, sens="confidential"):
        return (f"---\ntitle: {title}\ntype: {typ}\ntags: [{', '.join(tags[:8])}]\n"
                f"client: {cl}\nproject: {mid}\ncase: {case}\nsensitivity: {sens}\n---\n\n")
    chain = (f"\n> **사슬**: 범위[[scope/{mid}]]→확인[[questions/{mid}]]→공수[[estimates/{mid}]] · "
             f"ia[[ia/{mid}]]·방향[[direction/{mid}]]·접근[[approach/{mid}]]·의도[[dev-notes/decisions/{mid}]]\n")
    def bl(x): return "".join(f"- {i}\n" for i in x) if isinstance(x,(list,tuple)) else (x or "")
    A = []
    # 공수(항상)
    A.append(("estimate", [_wfile(f"estimates/{mid}.md", fm(f"{cl} 공수","estimate")+
        f"# 공수 — {meta.get('topic','')}\n\n- **밴드**: {meta.get('total_mm','?')} M/M · {meta.get('months','?')}개월 · {meta.get('headcount','?')}명\n"
        f"- **직군**: {meta.get('role_breakdown','')}\n- **케이스**: {case}\n- **디자인/상주**: {meta.get('design_level','')} / {meta.get('staffing','')}\n"
        f"- **신뢰도**: {meta.get('confidence','')}\n\n원본 `deliverables/{mid}/report.html` · [[patterns/estimate-anchoring-band]]"+chain)],
        f"{meta.get('total_mm','?')}M/M·{meta.get('months','?')}M·{meta.get('headcount','?')}명"))
    if meta.get("scope_in"):
        A.append(("scope",[_wfile(f"scope/{mid}.md", fm(f"{cl} 범위·전제","scope")+
            f"# 범위·전제 — {cl}\n\n**포함**: {meta.get('scope_in','')}\n\n**제외(out-of-scope)**: {meta.get('scope_out','')}\n\n"
            f"**전제/신뢰도**: {meta.get('confidence','')}\n\n[[patterns/legacy-boundary-rnr-table]]"+chain)], "범위 in/out"))
    if meta.get("questions") or meta.get("data_gaps"):
        A.append(("questions",[_wfile(f"questions/{mid}.md", fm(f"{cl} 확인 질문","questions")+
            f"# 꼭 확인할 것(사전질의·데이터갭) — {cl}\n\n{bl(meta.get('questions') or meta.get('data_gaps'))}"+chain)], "확인사항"))
    if meta.get("ia_summary") or meta.get("domain"):
        A.append(("ia",[_wfile(f"ia/{mid}.md", fm(f"{cl} IA","ia")+
            f"# IA 구조 — {cl}\n\n- 도메인: {meta.get('domain','')}\n- 케이스: {case}\n- IA: {meta.get('ia_summary','(report.html)')}\n\n원본 `deliverables/{mid}/report.html`"+chain)], "IA 구조"))
    if meta.get("approach"):
        A.append(("approach",[_wfile(f"approach/{mid}.md", fm(f"{cl} 개발 제안","approach")+
            f"# 개발 제안·접근·연계 — {cl}\n\n{bl(meta.get('approach'))}"+chain)], "개발 제안"))
    if meta.get("direction"):
        A.append(("direction",[_wfile(f"direction/{mid}.md", fm(f"{cl} 방향성","direction")+
            f"# 방향성(AS-IS→TO-BE·제약) — {cl}\n\n{meta.get('direction','')}\n"+chain)], "방향성"))
    if meta.get("overview"):
        A.append(("overview",[_wfile(f"overview/{mid}.md", fm(f"{cl} 개요","overview")+
            f"# 대상 개요·배경 — {cl}\n\n{meta.get('overview','')}\n"+chain)], "개요·배경"))
    if meta.get("infra"):
        A.append(("infra",[_wfile(f"infra/{mid}.md", fm(f"{cl} 인프라·연동","infra")+
            f"# 인프라/아키텍처·외부연동 — {cl}\n\n{meta.get('infra','')}\n\n원본 `deliverables/{mid}/report.html`"+chain)], "인프라·연동"))
    if isinstance(meta.get("decisions"), dict):
        d = meta["decisions"]; t = fm(f"{cl} 설계 의도·결정","adr")+f"# 설계 의도\n{d.get('intent','')}\n\n# 주요 결정·수정 이력\n\n| 단계 | 변경 | 의도 |\n|---|---|---|\n"
        for row in d.get("decisions",[]): t += "| "+" | ".join(str(x) for x in row)+" |\n"
        t += "\n# 재사용 체크포인트\n"+bl(d.get("reuse",[]))+chain
        A.append(("decision",[_wfile(f"dev-notes/decisions/{mid}.md", t)], "의도·결정 이력"))
    return A

def cmd_save(a):
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패 — 저장 보류(산출물은 output/에 안전)", file=sys.stderr)
        return 1
    with open(a.meta, encoding="utf-8") as f:
        meta = json.load(f)
    mid = meta["id"]; cl = meta.get("client",""); case = meta.get("project_case") or meta.get("doc_type","")
    dest = os.path.join(DELIV, mid); os.makedirs(dest, exist_ok=True)
    shutil.copy(a.html, os.path.join(dest, "report.html"))
    if getattr(a, "ws", None):
        _mirror_ws(mid, a.ws)
    meta["path"] = f"deliverables/{mid}/report.html"
    # index.jsonl — ★ 같은 id면 교체(update), 없으면 추가(append). 재작업 시 중복 방지(버전은 git 히스토리).
    idx_rows = _load_index(); replaced = False
    for i, r in enumerate(idx_rows):
        if r.get("id") == mid: idx_rows[i] = meta; replaced = True; break
    if not replaced: idx_rows.append(meta)
    with open(INDEX, "w", encoding="utf-8") as f:
        for r in idx_rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    # ★ 원자 단위 커밋 — git log --grep 검색이 정밀해지도록 원자마다 1커밋
    for atype, paths, extra in _atoms_from_meta(meta):
        _gitc("add", *paths)
        _gitc("commit", "-m", f"kb({atype}): {mid} | {cl} | {case} | {extra}")
    # 원본+인덱스 커밋(검색 가능한 요약 메시지) + 태그
    tg = ",".join((meta.get("tags") or meta.get("features") or [])[:4])
    _gitc("add", f"deliverables/{mid}", "index.jsonl")
    _gitc("commit", "-m", f"kb(report): {mid} | {cl} | {case} | {meta.get('total_mm','?')}M/M | {meta.get('domain','')} | {tg}")
    _gitc("tag", "-f", f"kb/{mid}")
    _gitc("pull", "--rebase", authed, br)
    r = _gitc("push", authed, f"HEAD:{br}")
    if r.returncode != 0:
        _gitc("pull", "--rebase", authed, br); r = _gitc("push", authed, f"HEAD:{br}")
    if r.returncode == 0:
        _gitc("push", "-f", authed, "--tags")
    n_atoms = sum(len(p) for _, p, _ in _atoms_from_meta(meta))
    print(f"[OK] corpus 저장+push: {mid} (원자 {n_atoms}커밋 + report, tag kb/{mid})" if r.returncode == 0
          else f"[WARN] .corpus 로컬 저장됨, push 실패(수동 push 필요): {r.stderr.strip()}")
    return 0


def cmd_feedback(a):
    """실제공수 피드백 기록 — 견적의 누적 자기보정 루프(운영 하네스 history-manager 패턴)."""
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패", file=sys.stderr); return 1
    rows = _load_index(); hit = None
    for r in rows:
        if r.get("id") == a.id:
            r["actual_mm"] = a.actual
            if a.lesson: r["lesson"] = a.lesson
            hit = r
    if not hit:
        print(f"[ERROR] id 없음: {a.id}", file=sys.stderr); return 1
    with open(INDEX, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # 피드백을 공수 원자(estimates/{id}.md)에 남긴다(meta.md 폐기 → 원자 구조)
    est = os.path.join(CDIR, "estimates", f"{a.id}.md")
    if os.path.isfile(est):
        note = f"\n## 실제 공수 피드백\n- **actual_mm**: {a.actual}"
        if hit.get("total_mm"): note += f" (산정 {hit['total_mm']} → 실제 {a.actual})"
        if a.lesson: note += f"\n- **교훈**: {a.lesson}"
        with open(est, "a", encoding="utf-8") as f:
            f.write(note + "\n")
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    _gitc("add", "-A"); _gitc("commit", "-m", f"kb(feedback): {a.id} | actual={a.actual} | {a.lesson or ''}"[:120])
    _gitc("pull", "--rebase", authed, br); r = _gitc("push", authed, f"HEAD:{br}")
    print(f"[OK] 피드백 기록: {a.id} 실제 {a.actual} M/M" if r.returncode == 0
          else f"[WARN] 로컬 기록됨, push 실패: {r.stderr.strip()}")
    return 0


def cmd_put_html(a):
    """최종 HTML 생성/수정 시 자동 버전 커밋·push (HTML만 빠르게 버전 올리기 — 다중 사용자·버전관리).
       atom 재생성은 save가, HTML 단독 버전 갱신은 이 명령이 담당."""
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패 — 커밋 보류(HTML은 로컬에 안전)", file=sys.stderr); return 1
    dest = os.path.join(DELIV, a.id); os.makedirs(dest, exist_ok=True)
    shutil.copy(a.html, os.path.join(dest, "report.html"))
    note = (a.note or "수정").strip()
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    _gitc("add", f"deliverables/{a.id}/report.html")
    c = _gitc("commit", "-m", f"kb(report): {a.id} | {note}")
    if c.returncode != 0 and "nothing to commit" in (c.stdout + c.stderr):
        print(f"[OK] 변경 없음(동일 HTML): {a.id}"); return 0
    _gitc("tag", "-f", f"kb/{a.id}")
    _gitc("pull", "--rebase", authed, br); r = _gitc("push", authed, f"HEAD:{br}")
    if r.returncode != 0:
        _gitc("pull", "--rebase", authed, br); r = _gitc("push", authed, f"HEAD:{br}")
    if r.returncode == 0: _gitc("push", "-f", authed, "--tags")
    print(f"[OK] HTML 버전 커밋+push: {a.id} ({note}, tag kb/{a.id})" if r.returncode == 0
          else f"[WARN] 로컬 커밋됨, push 실패(수동 push): {r.stderr.strip()}")
    return 0

def cmd_get(a):
    """최신(또는 특정 버전) 최종 HTML을 git에서 받아 보여준다 — 다중 사용자 환경에서 '최신 보자' 요청 대응."""
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패 — 최신본 받기 실패", file=sys.stderr); return 1
    rel = f"deliverables/{a.id}/report.html"; src = os.path.join(CDIR, rel)
    if a.rev:   # 특정 과거 버전(커밋 해시/태그)
        r = _gitc("show", f"{a.rev}:{rel}")
        if r.returncode != 0: print(f"[ERROR] {a.rev}에 {rel} 없음", file=sys.stderr); return 1
        outp = a.out or os.path.join(os.getcwd(), f"{a.id}_{a.rev}.html")
        open(outp, "w", encoding="utf-8").write(r.stdout)
    else:
        if not os.path.isfile(src): print(f"[ERROR] id 없음: {a.id}", file=sys.stderr); return 1
        outp = a.out or src
        if a.out: shutil.copy(src, a.out)
    # 버전 정보(최근 이력)
    log = _gitc("log", "-5", "--format=%h %ci %s", "--", rel).stdout
    print(f"[OK] 최신 HTML: {outp}")
    print("# 버전 이력(git log):"); print(log.strip() or "  (이력 없음)")
    return 0

def cmd_propose(a):
    """수정 제안 누적 — feedback-curator가 만든 '오너용 수정 제안'을 검토 큐(feedback/proposals.md)에 쌓는다.
       에이전트를 고치지 않는다 — 오너가 나중에 모아서 /harness로 반영 판단."""
    if not _ensure(pull=True):
        print("[ERROR] corpus 준비 실패 — 제안 보류", file=sys.stderr); return 1
    rel = "feedback/proposals.md"
    full = os.path.join(CDIR, rel); os.makedirs(os.path.dirname(full), exist_ok=True)
    if not os.path.isfile(full):
        open(full, "w", encoding="utf-8").write("# 수정 제안 큐 (feedback-curator → 오너 검토 → /harness 반영 판단)\n\n")
    open(full, "a", encoding="utf-8").write(f"- [ ] {a.note}\n")   # 체크박스: 오너가 반영하면 체크
    remote = _clean_remote(); authed = _authed(remote); br = _branch()
    _gitc("add", rel); _gitc("commit", "-m", f"kb(propose): {a.note[:70]}")
    _gitc("pull", "--rebase", authed, br); r = _gitc("push", authed, f"HEAD:{br}")
    print(f"[OK] 수정 제안 기록: {rel} (오너 검토 큐)" if r.returncode == 0 else f"[WARN] 로컬 기록됨, push 실패: {r.stderr.strip()}")
    return 0

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pull")
    s = sub.add_parser("search"); s.add_argument("query", nargs="*", help="자유어 쿼리(공백 구분)"); s.add_argument("--q", default=""); s.add_argument("--domain", default=""); s.add_argument("--tags", default=""); s.add_argument("--type", default=""); s.add_argument("--top", type=int, default=5)
    s = sub.add_parser("save"); s.add_argument("--html", required=True); s.add_argument("--meta", required=True); s.add_argument("--ws", default="", help="작업 중간물 폴더(_workspace/{slug}) 동봉")
    s = sub.add_parser("snapshot"); s.add_argument("--id", required=True); s.add_argument("--ws", required=True, help="_workspace/{slug}"); s.add_argument("--stage", default="", help="단계명(예: 02_architect)")
    s = sub.add_parser("feedback"); s.add_argument("--id", required=True); s.add_argument("--actual", type=float, required=True); s.add_argument("--lesson", default="")
    s = sub.add_parser("put-html"); s.add_argument("--id", required=True); s.add_argument("--html", required=True); s.add_argument("--note", default="", help="수정 사유(커밋 메시지)")
    s = sub.add_parser("get"); s.add_argument("--id", required=True); s.add_argument("--out", default="", help="저장 경로(미지정 시 .corpus 내 경로 표시)"); s.add_argument("--rev", default="", help="특정 버전(커밋해시/태그). 미지정=최신")
    s = sub.add_parser("propose"); s.add_argument("--note", required=True, help="오너용 수정 제안 한 줄(제목|규칙|대상)")
    a = ap.parse_args()
    return {"pull": cmd_pull, "search": cmd_search, "save": cmd_save, "snapshot": cmd_snapshot,
            "feedback": cmd_feedback, "put-html": cmd_put_html, "get": cmd_get, "propose": cmd_propose}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
