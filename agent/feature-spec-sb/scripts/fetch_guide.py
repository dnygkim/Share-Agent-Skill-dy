#!/usr/bin/env python3
"""
Feature Spec 가이드를 ETRIBE 서버에서 fetch.

가이드 내용은 stdout으로만 출력되며 디스크에 저장하지 않음.
Claude는 이 출력을 읽어 메모리에서 사용한다.

★ 토큰 없이도 동작한다.
   ~/.etribe/config.json 에 서버 URL·토큰이 있으면 서버 최신본을 쓰고,
   없거나 서버에 못 닿으면 리포의 guides/ 로컬 정본으로 자동 전환한다.
   어느 쪽이든 사용자가 밟는 단계는 같다.

Config (선택): ~/.etribe/config.json
{
  "server_url": "https://your-server.vercel.app",
  "token": "your-team-token"
}

사용 예:
  python3 fetch_guide.py --mode prd --author "김기획"
  python3 fetch_guide.py --mode sb --author "김기획" --feature-id A-02 --action create
  python3 fetch_guide.py --mode all --author "김기획"
  python3 fetch_guide.py --mode prd --author "김기획" --offline   # 토큰 있어도 로컬 강제

★ --author 는 사용 로그 적재용 (필수). 작성자명을 매 작업 시작 시 입력받아 전달.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".etribe" / "config.json"
LOCAL_GUIDE_DIR = Path(__file__).resolve().parent.parent / "guides"

# 모드 → 로컬 정본 파일 (서버 가이드와 같은 역할을 하는 리포 내 파일)
LOCAL_GUIDES = {
    "prd": ["prd-structure.md", "flowchart-rules.md", "features-list.md"],
    "sb": ["sb-writing.md", "features-list.md"],
    "sb-mobile": ["sb-writing.md", "features-list.md"],
    "sb-pc": ["sb-writing.md", "features-list.md"],
    "feature-list": ["features-list.md"],
    "feature-asset": ["features-list.md"],
    "all": ["prd-structure.md", "flowchart-rules.md", "sb-writing.md",
            "features-list.md"],
}


def load_config():
    """~/.etribe/config.json 로드. 없거나 불완전하면 None (→ 로컬 정본 사용)."""
    path = DEFAULT_CONFIG_PATH
    if not path.exists():
        return None
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"[WARN] {path} 를 읽을 수 없어 로컬 가이드를 사용합니다.", file=sys.stderr)
        return None
    # URL을 메신저에서 복사하면 <>가 따라붙는 경우가 있어 벗겨낸다
    url = (cfg.get("server_url") or "").strip().strip("<>").strip().rstrip("/")
    token = (cfg.get("token") or "").strip()
    if not url or not token:
        return None
    return {"server_url": url, "token": token}


def load_local_guides(mode: str) -> dict:
    """리포 guides/ 에서 해당 모드의 정본을 읽는다."""
    names = LOCAL_GUIDES.get(mode, LOCAL_GUIDES["all"])
    out = {}
    for name in names:
        p = LOCAL_GUIDE_DIR / name
        out[name] = p.read_text(encoding="utf-8") if p.exists() else None
    if not any(out.values()):
        sys.exit(
            f"[ERROR] 로컬 가이드를 찾을 수 없습니다: {LOCAL_GUIDE_DIR}\n"
            "  리포가 온전한지 확인하거나, ~/.etribe/config.json 에 서버 URL·토큰을 설정하세요."
        )
    return {"guides": out}


def fetch_guides(server_url: str, token: str, mode: str,
                 author: str = "", feature_id: str = "",
                 action: str = "", project_path: str = "") -> dict:
    """서버에 POST 요청해서 가이드 dict 받기. 사용 로그 메타 동시 전송.

    ★ author 등 한글이 포함될 수 있는 모든 메타는 JSON body로만 전송.
       HTTP 헤더는 ASCII(latin-1)만 허용되어 한글이면 UnicodeEncodeError 발생.
    """
    # 캐시버스터: Vercel 엣지가 동일 URL 응답을 캐시해 구버전 가이드를 내주는 문제 방지.
    # 매 요청 고유 쿼리(_cb) + no-cache 헤더로 항상 최신 가이드 fetch.
    url = server_url.rstrip("/") + "/api?_cb=" + str(time.time_ns())
    body = {
        "mode": mode,
        # 사용 로그용 메타 (서버에서 Notion DB 적재 시 사용, 미설정 시 silent)
        "author": author or "",
        "feature_id": feature_id or "",
        "action": action or "",
        "project_path": project_path or "",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"[WARN] 서버 응답 HTTP {e.code} ({body_text.strip()[:80]}) — "
              f"로컬 가이드로 전환합니다.", file=sys.stderr)
        return None
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        reason = getattr(e, "reason", e)
        print(f"[WARN] 서버에 닿지 못했습니다 ({reason}) — 로컬 가이드로 전환합니다.",
              file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser(description="ETRIBE 가이드 fetch")
    ap.add_argument("--mode", required=True,
                    choices=["prd", "sb", "sb-mobile", "sb-pc", "all",
                             "feature-list", "feature-asset"],
                    help="필요한 가이드 모드. sb=sb-mobile 별칭")
    ap.add_argument("--author", required=True,
                    help="작성자명 (사용 로그용, 매 작업 시작 시 입력)")
    ap.add_argument("--feature-id", default="",
                    help="기능 ID (예: A-02, J-01). 사용 로그용")
    ap.add_argument("--action", default="",
                    choices=["", "create", "edit", "view"],
                    help="작업 종류. 사용 로그용")
    ap.add_argument("--project-path", default="",
                    help="작업 폴더 상대 경로. 사용 로그용")
    ap.add_argument("--format", default="text",
                    choices=["text", "json"],
                    help="출력 포맷 (기본: text)")
    ap.add_argument("--offline", action="store_true",
                    help="서버를 건너뛰고 리포의 guides/ 로컬 정본만 사용")
    args = ap.parse_args()

    payload = None
    cfg = None if args.offline else load_config()
    if cfg:
        payload = fetch_guides(
            cfg["server_url"], cfg["token"], args.mode,
            author=args.author,
            feature_id=args.feature_id,
            action=args.action,
            project_path=args.project_path,
        )
    if payload is None:
        payload = load_local_guides(args.mode)
        print(f"[INFO] 로컬 가이드 사용: {LOCAL_GUIDE_DIR}", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    # text format: 각 가이드를 구분자와 함께 stdout에 출력
    guides = payload.get("guides", {})
    for fname, content in guides.items():
        print(f"=" * 80)
        print(f"=== {fname}")
        print(f"=" * 80)
        if content is None:
            print("[NOT FOUND]")
        else:
            print(content)
        print()


if __name__ == "__main__":
    main()
