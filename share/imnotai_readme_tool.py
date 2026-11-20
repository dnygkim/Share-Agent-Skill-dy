# imnotai_readme_tool.py — share/imnotai-upstream-sync.sh 보조 (README 조립 · 릴리즈노트 행 · 버전 표기)
#   python -X utf8 -I share/imnotai_readme_tool.py <명령> ...
# 명령
#   assemble  <우리 README.md|-> <원본 README.md> <out> <row|-> <full_sha> <date> <ver_label>
#             우리 머리말(제목 · 릴리즈노트 · 참고 줄 · 기준 커밋 표식) + 원본 한국어 README 그대로
#   root-row  <root README.md> <row text> <YYYY.MM.DD>   「릴리즈노트 현황」 표 맨 위에 im-not-ai 행 추가
#   versions  <ver> <file>...                            「Humanize KR(vX · MIT)」 · 「…epoko77-ai/im-not-ai)(vX · MIT)」 버전 표기 갱신
import os
import re
import sys

UP = "https://github.com/epoko77-ai/im-not-ai"
README_MARK = "<!-- upstream-readme:start"


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def release_rows(readme):
    m = re.search(r"^## 릴리즈노트\s*\n", readme, re.M)
    if not m:
        return []
    rows = []
    for ln in readme[m.end():].split("\n"):
        s = ln.strip()
        if not s:
            if rows:
                break
            continue
        if not s.startswith("|"):
            break
        rows.append(s)
    return [r for r in rows if not re.match(r"^\|\s*요약내용", r) and not re.match(r"^\|[\s:|-]+\|$", r)]


def cmd_assemble(ours, upstream, out, row, full_sha, date, ver_label):
    old = rd(ours) if ours != "-" and os.path.exists(ours) else ""
    rows = release_rows(old)
    if row != "-":
        rows.insert(0, row)
    short = full_sha[:7]
    head = [
        f"# [im-not-ai]({UP}) — Humanize KR 한글 AI 티 제거기 (백업)",
        "",
        "## 릴리즈노트",
        "",
        "| 요약내용 | 업데이트 일자 | 소유자 |",
        "|---|---|---|",
        *rows,
        "",
        f"> **참고:** [epoko77-ai/im-not-ai]({UP}) 원본 리포(MIT 라이선스) 백업 · 기준 **{ver_label}** · "
        f"커밋 [`{short}`]({UP}/commit/{full_sha})({date}) · 매주 금요일 23:00 원본 깃허브 확인 후 바뀐 파일 1:1 반영 · "
        "이 줄 아래 = 원본 README.md(한국어) 그대로 · 설치는 아래 「설치 (Install)」의 Claude Code 플러그인 방식",
        "",
        f"<!-- upstream-sha: {full_sha} -->",
        f"{README_MARK} — 이 줄 아래 = 원본 README.md 그대로 (공유 리포 share/imnotai-upstream-sync.sh 가 갱신) -->",
        "",
    ]
    wr(out, "\n".join(head) + rd(upstream).lstrip("\n"))


def cmd_root_row(root, text, date):
    t = rd(root)
    m = re.search(r"^## 릴리즈노트 현황.*$", t, re.M)
    if not m:
        print("루트 README 「릴리즈노트 현황」 표 없음 — 행 추가 생략")
        return
    sep = re.compile(r"^\|:---\|.*$", re.M).search(t, m.end())
    if not sep:
        print("루트 README 표 구분선 없음 — 행 추가 생략")
        return
    row = (f"| <sub>스킬</sub> | <sub>[im-not-ai](skills/im-not-ai/README.md)</sub> | "
           f"<sub>{text}</sub> | <sub>{date}</sub> | <sub>김단영</sub> |")
    wr(root, t[:sep.end()] + "\n" + row + t[sep.end():])


def cmd_versions(ver, *files):
    for p in files:
        if not os.path.exists(p):
            continue
        t = rd(p)
        n = re.sub(r"(Humanize KR\()v[0-9][0-9.]*( · MIT\))", r"\g<1>" + ver + r"\g<2>", t)
        n = re.sub(r"(epoko77-ai/im-not-ai\)\()v[0-9][0-9.]*( · MIT\))", r"\g<1>" + ver + r"\g<2>", n)
        if n != t:
            wr(p, n)
            print(f"버전 표기 갱신: {os.path.basename(p)} → {ver}")


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    {"assemble": cmd_assemble, "root-row": cmd_root_row, "versions": cmd_versions}[c](*a)
