# -*- coding: utf-8 -*-
"""제안서 레퍼런스(deck-references) 주간 학습 도구 — 클라우드 예약 작업 · 수동 실행 공용

  정리:  python3 scripts/deckref_tool.py extract <Drive 읽기 결과 파일> --out <폴더> [--max-chars 60000]
         → Drive 커넥터 read_file_content 결과(JSON {fileContent} · 원문 텍스트 · HTML 어느 쪽이든)를
           text.txt(장 단위 본문) · css.txt(HTML 덱 스타일) · tokens.txt(CSS 변수) 로 나누고 data URI 제거
  상태:  python3 scripts/deckref_tool.py state show
         python3 scripts/deckref_tool.py state learn --id <파일ID> --title <제목> --project <건 이름>
                 --modified <ISO> --kind pdf|pptx|html|gslides --deny "고객사명,서비스명"   → 다음 R-번호 출력
         python3 scripts/deckref_tool.py state skip --id <파일ID> --title <제목> --reason <사유>
         python3 scripts/deckref_tool.py state backlog --add <ID,ID…> | --remove <ID,ID…> | --file ids.txt
         python3 scripts/deckref_tool.py state finish --watermark <ISO> [--note <한 줄>]
  점검:  python3 scripts/deckref_tool.py check            (공개 리포로 가는 md 파일의 금지 패턴)
  반영:  python3 scripts/deckref_tool.py publish --share <공유 리포 경로> [--message <커밋 제목>] [--dry-run]
         → deck-references 밖 변경이 있으면 중단 · check 통과 · 커밋 · 푸시(rebase 재시도) · 공유 리포 부분 반영

_state.json 은 비공개 상태(파일 ID · 제목 · 건 이름 · 거부 목록) — 공유 리포 미러에서 제외된다.
"""
import argparse
import datetime as dt
import html as H
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # 원본 리포 루트
REF = ROOT / 'agent' / 'proposal' / 'deck-references'
STATE = REF / '_state.json'
REL = 'agent/proposal/deck-references'
KST = dt.timezone(dt.timedelta(hours=9))


def now_kst():
    return dt.datetime.now(KST)


# ───────────────────────── extract ─────────────────────────

MD_ESC = re.compile(r'\\([\\`*_{}\[\]()#+\-.!<>|~"\'=:;/@$%&,^?])')
DATA_URI = re.compile(r'data:[a-zA-Z]+/[a-zA-Z0-9.+-]+(?:;[a-zA-Z0-9=.-]+)*;base64,[A-Za-z0-9+/=\s]{40,}')
BLOCK = re.compile(r'</?(?:div|p|li|ul|ol|tr|td|th|table|h[1-6]|section|header|footer|br|figure|figcaption|dt|dd|blockquote)\b[^>]*>', re.I)


def load_input(p):
    raw = Path(p).read_text(encoding='utf-8', errors='replace')
    try:
        d = json.loads(raw)
        if isinstance(d, dict) and 'fileContent' in d:
            return d['fileContent'], d.get('title', '')
        if isinstance(d, list) and d and isinstance(d[0], dict) and 'text' in d[0]:   # MCP content 배열
            inner = ''.join(x.get('text', '') for x in d)
            try:
                dd = json.loads(inner)
                return dd.get('fileContent', inner), dd.get('title', '')
            except ValueError:
                return inner, ''
    except ValueError:
        pass
    return raw, ''


def strip_tags(s):
    s = BLOCK.sub('\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s)
    s = re.sub(r'[ \t ]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()


def cmd_extract(a):
    text, title = load_input(a.input)
    if '\\<' in text or '\\#' in text or '\\-' in text:
        text = MD_ESC.sub(r'\1', text)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    text = DATA_URI.sub('data:[생략]', text)
    is_html = bool(re.search(r'<(?:html|section|style|div)\b', text[:200000], re.I))
    # 큰 HTML 은 커넥터가 태그를 걷은 글로 돌려주고 CSS 가 본문 앞에 글자로 붙어 온다 → 그 CSS 도 떼어 낸다
    css_text_blocks = []
    if not re.search(r'<style\b', text[:200000], re.I):
        rx = re.compile(r'(?m)^[ \t]*(?::root|[.#*@a-zA-Z][^{}\n]{0,200})\{[^{}]{0,4000}\}[ \t]*$')
        css_text_blocks = [m.group(0) for m in rx.finditer(text) if ':' in m.group(0)]
        if len(css_text_blocks) >= 5:
            text = rx.sub('', text)
            is_html = True
        else:
            css_text_blocks = []
    info = {'title': title, 'kind': 'html' if is_html else 'text', 'chars_in': len(text)}
    if is_html:
        info['complete'] = bool(re.search(r'</html>', text[-2000:], re.I)) if not css_text_blocks else None
        css = '\n'.join(m.group(1) for m in re.finditer(r'<style\b[^>]*>(.*?)</style>', text, re.S | re.I))
        opens = list(re.finditer(r'<style\b[^>]*>', text, re.I))
        if opens and len(opens) > len(re.findall(r'</style>', text, re.I)):
            css += '\n' + text[opens[-1].end():]        # 커넥터가 중간에서 자른 큰 덱 — 닫히지 않은 <style> 끝까지
            text = text[:opens[-1].start()]              # 본문은 그 앞까지만
            info_cut = True
        else:
            info_cut = False
        if css_text_blocks:
            css = '\n'.join(css_text_blocks)
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        css = re.sub(r'\s+', ' ', css).replace('}', '}\n')
        toks, seen = [], set()
        for m in re.finditer(r'(--[A-Za-z0-9_-]+)\s*:\s*([^;}{]+)', css):
            k = (m.group(1), m.group(2).strip())
            if k not in seen:
                seen.add(k)
                toks.append(f'{k[0]}: {k[1]}')
        fonts = sorted(set(re.findall(r'font-family\s*:\s*([^;}{]+)', css)))
        sizes = sorted(set(re.findall(r'font-size\s*:\s*([0-9.]+px)', css)), key=lambda x: float(x[:-2]))
        (out / 'css.txt').write_text(css[:a.css_chars] + ('\n[TRUNCATED]' if len(css) > a.css_chars else ''), encoding='utf-8')
        (out / 'tokens.txt').write_text('\n'.join(toks[:300]) + '\n\n# font-family\n' + '\n'.join(fonts[:20])
                                        + '\n\n# font-size\n' + ' '.join(sizes), encoding='utf-8')
        body = re.sub(r'<(script|style|head)\b.*?</\1>', ' ', text, flags=re.S | re.I)
        body = re.sub(r'<!--.*?-->', ' ', body, flags=re.S)
        parts = re.split(r'(?=<section\b)', body, flags=re.I)
        chunks, n = [], 0
        for part in parts:
            m = re.match(r'<section\b([^>]*)>', part, re.I)
            t = strip_tags(part)
            if not t:
                continue
            if m:
                n += 1
                attrs = m.group(1)
                code = (re.search(r'data-code="([^"]*)"', attrs) or [None, ''])[1] if re.search(r'data-code="([^"]*)"', attrs) else ''
                cls = (re.search(r'class="([^"]*)"', attrs) or [None, ''])[1] if re.search(r'class="([^"]*)"', attrs) else ''
                chunks.append(f'## p{n} {code} ({cls})\n{t}')
            else:
                chunks.append(t)
        body_text = '\n\n'.join(chunks)
        info['slides'] = n
        info['css_chars'] = len(css)
        info['tokens'] = len(toks)
        if info_cut:
            info['complete'] = False
            info['note'] = '커넥터가 CSS 중간에서 자름 — 본문 없음, 디자인 토큰만 학습(본문은 같은 건 PDF 판으로)'
    else:
        body_text = re.sub(r'\n\s*\n+', '\n', text).strip()
    trunc = len(body_text) > a.max_chars
    (out / 'text.txt').write_text(body_text[:a.max_chars] + ('\n[TRUNCATED]' if trunc else ''), encoding='utf-8')
    info['text_chars'] = len(body_text)
    info['truncated'] = trunc
    (out / 'info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(info, ensure_ascii=False))


# ───────────────────────── state ─────────────────────────

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {'version': 1, 'root': '', 'exclude': [], 'watermark': '', 'last_run': '', 'next_ref': 1,
            'learned': {}, 'skipped': {}, 'backlog': [], 'deny': [], 'runs': []}


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def split_list(v):
    return [x.strip() for x in (v or '').split(',') if x.strip()]


def cmd_state(a):
    s = load_state()
    if a.op == 'show':
        print(json.dumps({'watermark': s['watermark'], 'last_run': s['last_run'], 'learned': len(s['learned']),
                          'skipped': len(s['skipped']), 'backlog': len(s['backlog']), 'next_ref': f"R-{s['next_ref']:04d}",
                          'root': s['root'], 'exclude': s['exclude'], 'runs': s['runs'][-3:]}, ensure_ascii=False, indent=1))
        return
    if a.op == 'learn':
        if not a.id:
            sys.exit('--id 필요')
        prev = s['learned'].get(a.id)
        ref = prev['ref'] if prev else f"R-{s['next_ref']:04d}"
        if not prev:
            s['next_ref'] += 1
        s['learned'][a.id] = {'ref': ref, 'title': a.title or '', 'project': a.project or '', 'modified': a.modified or '',
                              'kind': a.kind or '', 'learned': now_kst().date().isoformat()}
        s['backlog'] = [x for x in s['backlog'] if x != a.id]
        s['skipped'].pop(a.id, None)
        for d in split_list(a.deny) + ([a.project] if a.project else []):
            if d and d not in s['deny']:
                s['deny'].append(d)
        save_state(s)
        print(ref)
        return
    if a.op == 'skip':
        s['skipped'][a.id] = {'title': a.title or '', 'reason': a.reason or '', 'date': now_kst().date().isoformat()}
        s['backlog'] = [x for x in s['backlog'] if x != a.id]
        save_state(s)
        print('skipped', a.id)
        return
    if a.op == 'backlog':
        add = split_list(a.add)
        if a.file:
            add += [x.strip() for x in Path(a.file).read_text(encoding='utf-8').split() if x.strip()]
        rem = set(split_list(a.remove))
        bl = [x for x in s['backlog'] if x not in rem]
        for x in add:
            if x not in bl and x not in s['learned'] and x not in s['skipped']:
                bl.append(x)
        s['backlog'] = bl
        save_state(s)
        print('backlog', len(bl))
        return
    if a.op == 'finish':
        today = now_kst().date().isoformat()
        learned_today = [v['ref'] for v in s['learned'].values() if v.get('learned') == today]
        if a.watermark:
            s['watermark'] = a.watermark
        s['last_run'] = today
        s['runs'].append({'date': today, 'learned': len(learned_today), 'backlog': len(s['backlog']), 'note': a.note or ''})
        s['runs'] = s['runs'][-60:]
        save_state(s)
        print(json.dumps(s['runs'][-1], ensure_ascii=False))
        return
    sys.exit('알 수 없는 state 명령')


# ───────────────────────── check ─────────────────────────

CHECKS = [
    ('data URI', re.compile(r'data:[a-z]+/[a-z0-9.+-]+;base64', re.I)),
    ('base64 덩어리', re.compile(r'[A-Za-z0-9+/]{160,}={0,2}')),
    ('이메일', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')),
    ('전화번호', re.compile(r'\b0\d{1,2}[-. ]\d{3,4}[-. ]\d{4}\b')),
    ('금액', re.compile(r'\d[\d,.]*\s*(?:원|만\s?원|억\s?원|천만\s?원|백만\s?원)(?![가-힣])')),
    ('드라이브 링크', re.compile(r'(?:drive|docs)\.google\.com/', re.I)),
]


def cmd_check(a=None):
    s = load_state()
    deny = [d for d in s.get('deny', []) + split_list(getattr(a, 'deny', '') if a else '') if len(d) >= 2]
    bad = []
    files = sorted(p for p in REF.glob('*.md'))
    for p in files:
        t = p.read_text(encoding='utf-8')
        if len(t.encode('utf-8')) > 200_000:
            bad.append(f'{p.name}: 파일이 200KB 초과')
        for i, line in enumerate(t.splitlines(), 1):
            for name, rx in CHECKS:
                if rx.search(line):
                    bad.append(f'{p.name}:{i} [{name}] {line.strip()[:120]}')
            low = line.lower()
            for d in deny:
                if d.lower() in low:
                    bad.append(f'{p.name}:{i} [거부 목록 「{d}」] {line.strip()[:120]}')
    others = [p.name for p in REF.iterdir() if p.is_file() and p.suffix not in ('.md',) and p.name != '_state.json']
    for o in others:
        bad.append(f'{o}: md 외 파일(이미지 · 원문 금지)')
    if bad:
        print('CHECK FAIL', len(bad))
        for b in bad[:80]:
            print(' -', b)
        return 1
    print(f'CHECK OK — md {len(files)}개 · 거부 목록 {len(deny)}개')
    return 0


# ───────────────────────── publish ─────────────────────────

def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        raise SystemExit(f'git {" ".join(args)} 실패: {r.stderr.strip()[:400]}')
    return r.stdout.strip()


def cmd_publish(a):
    st = git('-c', 'core.quotepath=off', 'status', '--porcelain')
    paths = [ln[3:].strip().strip('"') for ln in st.splitlines() if ln.strip()]
    outside = [p for p in paths if not p.startswith(REL)]
    if outside:
        sys.exit('deck-references 밖 변경이 있어 중단:\n  ' + '\n  '.join(outside[:20]))
    if not paths:
        print('변경 없음 — 커밋 생략')
    if cmd_check(a) != 0:
        sys.exit('check 실패 — 커밋하지 않음')
    if a.dry_run:
        print('dry-run: 커밋 · 푸시 생략', paths)
        return
    if paths:
        if not git('config', 'user.email', check=False):
            git('config', 'user.name', 'proposal-deckref')
            git('config', 'user.email', 'proposal-deckref@users.noreply.github.com')
        git('config', 'core.hooksPath', '.githooks')
        git('add', '-A', '--', REL)
        msg = a.message or f'deck-references: 제안서 레퍼런스 주간 학습 {now_kst().date().isoformat()}'
        git('commit', '-q', '-m', msg)
        for i in range(3):
            r = subprocess.run(['git', 'push', '-q', 'origin', 'HEAD:main'], cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 0:
                break
            git('fetch', '-q', 'origin')
            rb = subprocess.run(['git', 'rebase', '-q', 'origin/main'], cwd=ROOT, capture_output=True, text=True)
            if rb.returncode != 0:
                subprocess.run(['git', 'rebase', '--abort'], cwd=ROOT)
                sys.exit('rebase 충돌 — 푸시 못 함')
        else:
            sys.exit('푸시 3회 실패')
        print('원본 리포', git('log', '-1', '--format=%h %s'))
    if a.share:
        sh = Path(a.share) / 'share' / 'mirror-from-source.sh'
        r = subprocess.run(['bash', str(sh), '--only', REL, str(ROOT)], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        print((r.stdout + r.stderr).strip()[-1500:])
        if r.returncode != 0:
            sys.exit('공유 리포 부분 반영 실패')


def main():
    ap = argparse.ArgumentParser(description='deck-references 주간 학습 도구')
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract')
    e.add_argument('input')
    e.add_argument('--out', required=True)
    e.add_argument('--max-chars', type=int, default=60000)
    e.add_argument('--css-chars', type=int, default=30000)
    s = sub.add_parser('state')
    s.add_argument('op', choices=['show', 'learn', 'skip', 'backlog', 'finish'])
    for k in ('id', 'title', 'project', 'modified', 'kind', 'deny', 'reason', 'add', 'remove', 'file', 'watermark', 'note'):
        s.add_argument('--' + k)
    c = sub.add_parser('check')
    c.add_argument('--deny', default='')
    p = sub.add_parser('publish')
    p.add_argument('--share')
    p.add_argument('--message')
    p.add_argument('--deny', default='')
    p.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'extract':
        cmd_extract(a)
    elif a.cmd == 'state':
        cmd_state(a)
    elif a.cmd == 'check':
        sys.exit(cmd_check(a))
    else:
        cmd_publish(a)


if __name__ == '__main__':
    main()
