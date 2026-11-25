#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guard.py — 민감정보 커밋 · 푸시 차단 검사기 (2026-11-25 신설)

원본 리포(dykim-claude-agents-skills)와 공유 리포(Share-Agent-Skill-dy)가 같은 파일을 쓴다(.githooks/ 는 1:1 미러).
파이썬 3.8+ 표준 라이브러리만 쓴다. 훅에서는 .githooks/_guard.sh 가 부른다.

  guard.py staged              스테이징된 변경(추가된 줄 · 파일 이름 · 새 바이너리) 검사   ← pre-commit
  guard.py msg <파일>          커밋 메시지 검사                                          ← commit-msg
  guard.py push <원격> <URL>   푸시할 커밋 전부 검사(표준 입력 = pre-push 형식)           ← pre-push
  guard.py range <범위>        커밋 범위 검사 (예: origin/main..HEAD)
  guard.py tree [--rev REV]    추적 파일 전체 검사(점검용)
  guard.py history [범위]      이력의 추가된 줄 전체 검사(점검용 · 기본 --all)
  guard.py files <경로…>       임의 파일 검사(--level 로 수준 지정)
  guard.py allow <지문…>       허용 목록에 지문 추가 — 관리자 확인 뒤에만
  guard.py exempt <파일…>      샘플로 확인받은 파일을 가드에서 제외(경로 지문 등록) · 인자 없이 부르면 목록
  guard.py doctor              훅 연결 · 거부 목록 · 미러 제외 목록 일치 점검
  guard.py selftest            규칙 자체 시험

검사 수준(경로마다 자동 판정)
  vendor   외부 스킬 원본 백업              토큰 · 개인키 · 비밀 파일 형식
  sample   샘플로 확인받은 파일(허용 목록)   토큰 · 개인키 · 비밀 파일 형식 — 고객명 · 연락처 · 바이너리 · 예시 경로 차단은 적용하지 않음
  private  원본 리포 전용 경로(메모리 등)   + 비밀값 대입 · 주민번호 · 카드번호
  public   공유 리포 전체 · 원본의 미러 대상 + 연락처 · 거부 목록(고객 · 사업 · 사람 이름) · 내부 링크 · 로컬 경로
                                            · 내용을 검사할 수 없는 새 바이너리

종료 코드: 0 통과 · 1 차단 · 2 실행 오류(훅은 이것도 차단 — 검사를 못 하면 내보내지 않는다)
예외는 .githooks/guard-allow.txt 의 지문으로만 둔다(줄 안 표식 없음). 가드 파일 변경 커밋은 GUARD_ADMIN=1 이 있어야 통과한다.
"""
import argparse
import hashlib
import html
import io
import json
import math
import os
import re
import subprocess
import sys
import zipfile

VERSION = '1.0 (2026-11-25)'

# ───────────────────────── 경로 정책 ─────────────────────────
# 공유 리포 share/mirror-from-source.sh 의 EXCLUDE 와 같은 목록(공유로 나가지 않는 경로). 한쪽을 고치면 다른 쪽도 — doctor 가 대조한다.
MIRROR_EXCLUDE = (
    'agent/danibot', 'skills/danjr', 'persona', 'memory', '.claude', 'CLAUDE.md', 'README.md',
    'install-global.sh', 'push-memory.sh', 'agent/proposal/deck-references/_state.json', 'guard-private',
)
PRIVATE_ONLY = ('.share-exclude',)                         # 미러 스크립트가 따로 빼는 파일
PUBLIC_ANYWAY = ('README.md',)                             # 미러에서 빠지지만 릴리즈노트 행이 공유 README 로 옮겨지는 파일 — public 수준
VENDOR = ('skills/ui-ux-pro-max-skill', 'skills/im-not-ai', 'skills/impeccable', 'skills/toss-design-skill')
VENDOR_OURS = ('사용가이드.html',)                         # 외부 스킬 폴더 안의 우리 문서 — public 수준
GUARD_FILES = ('.githooks/', 'guard-private/')
SOURCE_MARK = '.share-exclude'                             # 이 파일이 있으면 원본 리포
DENY_FILE = 'guard-private/denylist.txt'
DENY_STATE = 'agent/proposal/deck-references/_state.json'  # 제안서 레퍼런스 학습이 쌓는 거부 목록(자동 반영)
ALLOW_FILE = '.githooks/guard-allow.txt'
CANON_REMOTE = re.compile(r'github\.com[:/]+dnygkim/(dykim-claude-agents-skills|Share-Agent-Skill-dy)(\.git)?/?$', re.I)

OFFICE_EXT = ('.pptx', '.xlsx', '.docx', '.pptm', '.xlsm', '.docm')
BINARY_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.tif', '.tiff', '.heic', '.psd', '.ai', '.fig', '.sketch',
              '.pdf', '.hwp', '.hwpx', '.ppt', '.xls', '.doc', '.key', '.numbers', '.pages',
              '.zip', '.7z', '.rar', '.tar', '.gz', '.tgz', '.bz2', '.xz',
              '.mp4', '.mov', '.avi', '.mp3', '.wav', '.m4a', '.webm',
              '.woff', '.woff2', '.ttf', '.otf', '.eot', '.exe', '.dll', '.bin', '.dat', '.pyc')

CLASS_KO = {'S': '토큰 · 개인키', 'G': '비밀값 대입', 'P': '주민번호 · 카드번호', 'C': '연락처', 'I': '내부 링크 · 경로',
            'D': '거부 목록', 'B': '차단 파일', 'U': '검사 불가 파일', 'T': '가드 파일 변경'}
LEVEL_CLASSES = {'vendor': 'SB', 'sample': 'SB', 'private': 'SGPBT', 'public': 'SGPCIDBUT'}
# sample = 사용자가 「샘플로 올려도 된다」고 확인한 파일(허용 목록의 p:경로지문). 고객명 · 연락처 · 바이너리 · 예시 경로 차단을 적용하지 않고
#          토큰 · 개인키 · 비밀 파일 형식만 본다(2026-11-26 「샘플로 업로드한 파일들 다 원복 · 가드 제외하고 진행」).
SAMPLE_KEEP_RULES = ('B-ENV', 'B-KEYFILE', 'B-CREDFILE', 'B-LOCALCONF', 'B-LOCALMEM', 'B-DATABASE')


class GuardError(Exception):
    pass


# ───────────────────────── 규칙 ─────────────────────────
def shannon(s):
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in (s.count(ch) for ch in set(s)))


PLACEHOLDER = re.compile(r'x{4,}|\*{3,}|\.{3,}|_{4,}|-{5,}|0{8,}|1234567|abcdefg|example|sample|dummy|placeholder|your[_-]?'
                         r'|changeme|redacted|masked|fake|test[_-]?(?:key|token)|토큰|여기|발급', re.I)


def real_token(tok):
    """접두어 뒤 본문이 자리표시가 아니고 무작위에 가까운지"""
    if PLACEHOLDER.search(tok):
        return False
    body = re.sub(r'^[A-Za-z]{2,12}[-_.]', '', tok)
    return shannon(body) >= 3.0


def _b(*parts):
    return ''.join(parts)


SECRET_RULES = [  # (id, 정규식, 본문 검증 여부)
    ('S-PRIVKEY', r'-----BEGIN (?:[A-Z0-9]+ ){0,3}PRIVATE KEY(?: BLOCK)?-----', False),
    ('S-AWS-KEYID', r'(?<![A-Z0-9])(?:AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16}(?![A-Z0-9])', True),
    ('S-AWS-SECRET', r'(?i)aws_?secret_?access_?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])', False),
    ('S-GITHUB', r'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{50,255})(?![A-Za-z0-9_])', True),
    ('S-GITLAB', r'(?<![A-Za-z0-9_-])glpat-[A-Za-z0-9_-]{20,}', True),
    ('S-ANTHROPIC', r'(?<![A-Za-z0-9_-])sk-ant-[A-Za-z0-9_-]{24,}', True),
    ('S-OPENAI', r'(?<![A-Za-z0-9_-])sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{40,}', True),
    ('S-SLACK-TOKEN', r'(?<![A-Za-z0-9])xox[abeoprs]-[A-Za-z0-9-]{10,}', True),
    ('S-SLACK-APP', r'(?<![A-Za-z0-9])xapp-\d-[A-Z0-9]{8,}-\d{8,}-[a-f0-9]{16,}', True),
    ('S-SLACK-WEBHOOK', r'https://hooks\.slack\.com/(?:services|workflows|triggers)/[A-Za-z0-9/_-]{24,}', True),
    ('S-DISCORD-WEBHOOK', r'https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d{10,}/[A-Za-z0-9_-]{30,}', True),
    ('S-GOOGLE-API', r'(?<![A-Za-z0-9_-])AIza[0-9A-Za-z_-]{35}(?![A-Za-z0-9_-])', True),
    ('S-GOOGLE-OAUTH', r'(?<![A-Za-z0-9_-])GOCSPX-[A-Za-z0-9_-]{28}(?![A-Za-z0-9_-])', True),
    ('S-GOOGLE-TOKEN', r'(?<![A-Za-z0-9_./-])(?:ya29\.[0-9A-Za-z_-]{30,}|1//0[0-9A-Za-z_-]{40,})', True),
    ('S-GCP-SA', r'"type"\s*:\s*"service_account"', False),
    ('S-NPM', r'(?<![A-Za-z0-9_])npm_[A-Za-z0-9]{36}(?![A-Za-z0-9])', True),
    ('S-PYPI', r'(?<![A-Za-z0-9_-])pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}', False),
    ('S-STRIPE', r'(?<![A-Za-z0-9_])(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}', True),
    ('S-FIGMA', r'(?<![A-Za-z0-9_])figd_[A-Za-z0-9_-]{30,}', True),
    ('S-NOTION', r'(?<![A-Za-z0-9_])(?:secret_[A-Za-z0-9]{43}|ntn_[A-Za-z0-9]{40,})(?![A-Za-z0-9])', True),
    ('S-HF', r'(?<![A-Za-z0-9_])hf_[A-Za-z0-9]{30,}(?![A-Za-z0-9])', True),
    ('S-TELEGRAM', r'(?<![0-9])\d{8,10}:AA[A-Za-z0-9_-]{33}(?![A-Za-z0-9_-])', True),
    ('S-SENDGRID', r'(?<![A-Za-z0-9_])SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}', True),
    ('S-JWT', r'(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', True),
    ('S-AZURE-KEY', r'AccountKey=[A-Za-z0-9+/]{60,}={0,2}', True),
    ('S-URL-CRED', r'(?<![A-Za-z0-9])[a-zA-Z][a-zA-Z0-9+.-]{1,15}://[^\s/:@"\'<>`]{1,64}:[^\s/:@"\'<>`]{3,64}@[A-Za-z0-9.-]+', False),
]
SECRETS = [(i, re.compile(p), chk) for i, p, chk in SECRET_RULES]
S_ANY = re.compile('|'.join('(?:%s)' % p.replace('(?i)', '') for _, p, _ in SECRET_RULES if not p.startswith('(?i)')) +
                   r'|(?i:aws_?secret)')

G_KEYS = (r'pass(?:word|wd|phrase)?|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|secret[_-]?key|client[_-]?secret'
          r'|auth(?:orization)?|bearer|credential|private[_-]?key|비밀번호|패스워드|암호|인증키|토큰|시크릿')
G_ASSIGN = re.compile(r'(?i)(?<![A-Za-z0-9])(?:%s)[A-Za-z0-9_]{0,24}["\'`]?\s*(?::=|=>|[:=])\s*["\'`]?'
                      r'(?:Bearer\s+|Basic\s+)?([A-Za-z0-9+/=_\-.!@#%%^&*~]{8,200})' % G_KEYS)
G_HINT = re.compile(r'(?i)pass|pwd|secret|token|key|auth|bearer|credential|비밀번호|패스워드|암호|인증키|토큰|시크릿')
G_IDENT = re.compile(r'^(?:[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+|[A-Z][A-Z0-9_]*|[a-z]+(?:[_-][a-z0-9]+)+|[A-Za-z]+\d{0,2}'
                     r'|\d+(?:\.\d+)*|[a-z0-9]+(?:-[a-z0-9]+){2,}\.[a-z]{2,4})$')


def generic_secret(val):
    """대입된 값이 실제 비밀값처럼 보이는지 — 식별자 · 환경변수 참조 · 자리표시 · 낱말은 제외"""
    v = val.rstrip('.,;')
    if len(v) < 8 or PLACEHOLDER.search(v) or G_IDENT.match(v):
        return False
    lower, upper = any(c.islower() for c in v), any(c.isupper() for c in v)
    digit, sym = any(c.isdigit() for c in v), any(not c.isalnum() for c in v)
    classes = lower + upper + digit + sym
    if not digit:
        return False
    ent = shannon(v)
    if len(v) >= 20 and ent >= 3.6:
        return True
    return classes >= 3 and ent >= 3.0 and len(v) >= 8


RRN = re.compile(r'(?<![0-9])(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\s?-\s?([1-8]\d{6})(?![0-9])')
CARD = re.compile(r'(?<![0-9-])(?:\d{4}[- ]){3}\d{4}(?![0-9-])')


def rrn_valid(digits):
    w = (2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5)
    return (11 - sum(int(d) * k for d, k in zip(digits[:12], w)) % 11) % 10 == int(digits[12])


def luhn(digits):
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
        alt = not alt
    return total % 10 == 0 and len(set(digits)) > 3


EMAIL = re.compile(r'(?<![A-Za-z0-9._%+/-])[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@((?:[A-Za-z0-9-]+\.)+([A-Za-z]{2,24}))(?![A-Za-z0-9-])')
EMAIL_OK_DOMAIN = re.compile(r'(?i)(?:^|\.)(?:example\.(?:com|org|net|co\.kr)|test\.com|email\.com|domain\.com|company\.com|sample\.com'
                             r'|yourdomain\.com|yourcompany\.com|mail\.com|users\.noreply\.github\.com|anthropic\.com)$|\.(?:local|localhost|internal|lan|test|invalid|example)$')
EMAIL_OK_LOCAL = re.compile(r'(?i)^(?:git|user|username|name|your|you|email|id|hello|info|admin|test|noreply|no-reply|example|someone|xxx+)$')
FILE_TLD = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'css', 'js', 'ts', 'tsx', 'jsx', 'md', 'json', 'html', 'py', 'sh', 'pdf', 'ico'}
PHONE = re.compile(r'(?<![0-9-])(?:01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}|0(?:2|[3-6][1-5]|70|50\d?)-\d{3,4}-\d{4})(?![0-9-])')
PHONE_FAKE = re.compile(r'^(\d)\1*$|12345678|1234567$|00000000|11112222|12341234|56785678|01234567')

LINKS = [
    ('I-GDRIVE', re.compile(r'https?://(?:drive|docs|sheets|slides|forms|script|sites)\.google\.com/[^\s"\'<>)\]]*?'
                            r'(?:/d/|/folders/|[?&]id=|/e/)[A-Za-z0-9_-]{15,}')),
    ('I-FIGMA', re.compile(r'https?://(?:www\.)?figma\.com/(?:file|design|proto|board|slides|make|deck)/[A-Za-z0-9]{15,}')),
    ('I-NOTION', re.compile(r'https?://(?:www\.)?notion\.(?:so|site)/[^\s"\'<>)\]]*[0-9a-f]{32}')),
    ('I-SLACK', re.compile(r'https?://[a-z0-9-]+\.slack\.com/(?:archives|files|team|canvas)/[A-Za-z0-9]+')),
    ('I-CLAUDE-SHARE', re.compile(r'https?://claude\.ai/(?:share|public/artifacts|artifact|code/artifact|chat)/[A-Za-z0-9-]{8,}')),
    ('I-ONEDRIVE', re.compile(r'https?://(?:[a-z0-9-]+\.sharepoint\.com/[^\s"\'<>)\]]+|1drv\.ms/[^\s"\'<>)\]]+|[a-z0-9-]+\.dropbox\.com/s[^\s"\'<>)\]]+)')),
]
USERPATH = re.compile(r'(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]{1,2}|(?<![A-Za-z0-9._-])/[a-z]/)Users[\\/]{1,2}([^\\/\s"\'<>|:*?$%{}()`]+)'
                      r'|(?<![A-Za-z0-9._~-])/(?:Users|home)/([A-Za-z0-9._-]+)(?=/)')
USER_OK = re.compile(r'(?i)^(?:user|users|username|user_?name|name|you|your|me|public|default|shared|runner|ubuntu|root|admin'
                     r'|사용자|사용자명|사용자이름|계정|이름|내이름|홍길동|\.\.\.|xxx+)$')
PRIV_IP = re.compile(r'(?<![0-9.])(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}(?![0-9]|\.[0-9]|/\d)')
IP_OK = {'192.168.0.1', '192.168.1.1', '192.168.0.0', '10.0.0.1', '10.0.0.0', '172.16.0.0', '192.168.0.100', '192.168.1.100'}
I_ANY = re.compile(r'https?://|Users[\\/]|/home/|(?<![0-9.])(?:10|192|172)\.\d')

BLOCK_PATHS = [  # (id, 정규식, 설명) — 모든 수준에 적용
    ('B-WORKDIR', re.compile(r'^agent/[^/]+/(?:input|Input|output|Output|_workspace)/(?!\.gitkeep$)'), '고객 원자료 · 산출물 폴더'),
    ('B-EXAMPLE', re.compile(r'^agent/[^/]+/examples/.*\.html?$'), '과거 고객 완성본 샘플'),
    ('B-ENV', re.compile(r'(?:^|/)\.env(?:\.(?!example$|sample$|template$|dist$)[^/]*)?$'), '환경변수 파일'),
    ('B-CORPUS', re.compile(r'(?:^|/)\.corpus/'), '학습 원문 폴더'),
    ('B-KEYFILE', re.compile(r'(?i)\.(?:pem|p12|pfx|jks|keystore|ppk|kdbx)$|(?:^|/)id_(?:rsa|dsa|ecdsa|ed25519)$'), '개인키 · 인증서'),
    ('B-CREDFILE', re.compile(r'(?i)(?:^|/)(?:credentials?|client_secret[^/]*|service[-_]?account[^/]*|secrets?)\.(?:json|ya?ml|toml|txt|ini)$'
                              r'|(?:^|/)\.(?:npmrc|netrc|pypirc|git-credentials|htpasswd)$'), '자격 증명 파일'),
    ('B-LOCALCONF', re.compile(r'(?:^|/)(?:settings\.local\.json|\.claude\.json|\.credentials\.json)$'), 'PC 전용 설정'),
    ('B-LOCALMEM', re.compile(r'^memory/(?:local-[^/]*\.md|CLAUDE\.md)$'), 'PC 전용 메모리'),
    ('B-DATABASE', re.compile(r'(?i)\.(?:sqlite3?|mdb|accdb|dump)$'), '데이터베이스 파일'),
]


# ───────────────────────── 환경 ─────────────────────────
class Ctx:
    root = ''
    is_source = False
    force_level = None
    private_paths = ()
    deny = None            # (정규식 목록, 개수, 출처) 또는 None
    deny_src = ''
    allow = frozenset()
    exempt = frozenset()   # 샘플로 확인받은 파일의 경로 지문
    redact = False
    admin = False


C = Ctx()


def git(*args, cwd=None, data=None, check=True):
    r = subprocess.run(['git', '-c', 'core.quotepath=off'] + list(args), cwd=cwd or C.root, input=data, capture_output=True)
    if check and r.returncode != 0:
        raise GuardError('git %s 실패: %s' % (' '.join(args[:3]), r.stderr.decode('utf-8', 'replace').strip()[:300]))
    return r.stdout


def u(b):
    return b.decode('utf-8', 'replace')


def setup(args):
    start = getattr(args, 'repo', None) or os.getcwd()
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=start, capture_output=True)
    if r.returncode != 0:
        raise GuardError('깃 리포 안이 아님: %s' % start)
    C.root = u(r.stdout).strip()
    C.is_source = os.path.isfile(os.path.join(C.root, SOURCE_MARK))
    lv = getattr(args, 'level', 'auto')
    C.force_level = None if lv == 'auto' else lv
    C.redact = bool(getattr(args, 'redact', False)) or os.environ.get('GITHUB_ACTIONS') == 'true'
    C.admin = os.environ.get('GUARD_ADMIN') == '1'
    priv = list(MIRROR_EXCLUDE) + list(PRIVATE_ONLY)
    if C.is_source:
        try:
            with open(os.path.join(C.root, SOURCE_MARK), encoding='utf-8') as f:
                for line in f:
                    p = line.split('#', 1)[0].strip().rstrip('/')
                    if p and not p.startswith('/') and '..' not in p:
                        priv.append(p)
        except OSError:
            pass
    C.private_paths = tuple(dict.fromkeys(priv))
    load_allow()
    load_deny(getattr(args, 'denylist', None), getattr(args, 'source', None))


def path_fp(path):
    """샘플 예외용 경로 지문 — 허용 목록에는 경로 대신 이 값만 적는다(파일 이름에 고객명이 있어도 드러나지 않게)"""
    return hashlib.sha256(('SAMPLE-PATH\n' + path.replace('\\', '/')).encode('utf-8')).hexdigest()[:20]


def level_of(path):
    p = path.replace('\\', '/')
    if C.exempt and path_fp(p) in C.exempt:
        return 'sample'
    for v in VENDOR:
        if p == v or p.startswith(v + '/'):
            if p[len(v) + 1:] in VENDOR_OURS:
                break
            return 'vendor'
    if C.force_level:
        return C.force_level
    if C.is_source and p not in PUBLIC_ANYWAY:
        for x in C.private_paths:
            if p == x or p.startswith(x + '/'):
                return 'private'
    return 'public'


def load_allow():
    s, ex = set(), set()
    try:
        with open(os.path.join(C.root, ALLOW_FILE), encoding='utf-8') as f:
            for line in f:
                tok = line.split('#', 1)[0].split()
                if tok and re.fullmatch(r'[0-9a-f]{20}', tok[0]):
                    s.add(tok[0])
                elif tok and re.fullmatch(r'p:[0-9a-f]{20}', tok[0]):
                    ex.add(tok[0][2:])
    except OSError:
        pass
    C.allow = frozenset(s)
    C.exempt = frozenset(ex)


def deny_candidates(explicit, source):
    roots = []
    if source:
        roots.append(source)
    if os.environ.get('GUARD_SOURCE'):
        roots.append(os.environ['GUARD_SOURCE'])
    roots.append(C.root)
    roots.append(os.path.join(os.path.dirname(C.root), 'dykim-claude-agents-skills'))
    roots.append(os.path.join(os.path.expanduser('~'), 'Documents', 'Claude', 'dykim-claude-agents-skills'))
    out = []
    if explicit:
        out.append((explicit, None))
    if os.environ.get('GUARD_DENYLIST'):
        out.append((os.environ['GUARD_DENYLIST'], None))
    for r in roots:
        out.append((os.path.join(r, DENY_FILE), os.path.join(r, DENY_STATE)))
    return out


def load_deny(explicit=None, source=None):
    C.deny, C.deny_src = None, ''
    for path, state in deny_candidates(explicit, source):
        if not os.path.isfile(path):
            continue
        terms, drop = [], set()
        with open(path, encoding='utf-8') as f:
            for line in f:
                t = line.split(' #', 1)[0].strip()
                if not t or t.startswith('#'):
                    continue
                if t.startswith('!'):
                    drop.add(t[1:].strip().lower())
                else:
                    terms.append(t)
        if state and os.path.isfile(state):
            try:
                with open(state, encoding='utf-8') as f:
                    terms += [str(d) for d in json.load(f).get('deny', [])]
            except (OSError, ValueError):
                pass
        C.deny = compile_deny(terms, drop)
        C.deny_src = path
        return


def compile_deny(terms, drop=()):
    sub, sub_left, word_ci, word_cs, rx = set(), set(), set(), set(), []
    for raw in terms:
        t = raw.strip()
        mode = ''
        m = re.match(r'^(w|cs|re):', t)
        if m:
            mode, t = m.group(1), t[m.end():].strip()
        if len(t) < 2 or t.lower() in drop:
            continue
        if mode == 're':
            rx.append(re.compile(t))
        elif mode == 'cs':
            word_cs.add(t)
        elif mode == 'w':
            word_ci.add(t)
        elif t.isascii():
            (word_cs if len(t) <= 4 else word_ci).add(t)
        elif len(t) <= 2:
            sub_left.add(t)
        else:
            sub.add(t)

    def alt(group):
        return '|'.join(re.escape(x) for x in sorted(group, key=len, reverse=True))

    pats = []
    if sub:
        pats.append(re.compile(alt(sub), re.I))
    if sub_left:
        pats.append(re.compile('(?<![가-힣])(?:%s)' % alt(sub_left)))
    if word_ci:
        pats.append(re.compile('(?<![A-Za-z0-9])(?:%s)(?![A-Za-z0-9])' % alt(word_ci), re.I))
    if word_cs:
        pats.append(re.compile('(?<![A-Za-z0-9])(?:%s)(?![A-Za-z0-9])' % alt(word_cs)))
    n = len(sub) + len(sub_left) + len(word_ci) + len(word_cs) + len(rx)
    return (pats + rx, n)


# ───────────────────────── 검사 ─────────────────────────
def fingerprint(rule, path, key):
    return hashlib.sha256(('%s\n%s\n%s' % (rule, path, key)).encode('utf-8')).hexdigest()[:20]


def mask(s):
    s = s.strip()
    return '%s…(%d자)' % (s[:4], len(s)) if len(s) > 8 else '…(%d자)' % len(s)


def finding(rule, path, line, value, key, level, secret=False):
    return {'rule': rule, 'cls': rule[0], 'path': path, 'line': line, 'level': level,
            'value': mask(value) if secret else value.strip()[:80], 'fp': fingerprint(rule, path, key)}


def scan_text(path, lineno, text, level, key=None, classes=None):
    """한 줄 검사 → 발견 목록. key = 지문에 쓸 값(기본: 공백을 정리한 줄 전체)"""
    cls = classes or LEVEL_CLASSES[level]
    out = []
    if len(text) < 6:
        return out
    k = key if key is not None else ' '.join(text.split())
    if S_ANY.search(text):
        for rid, rx, chk in SECRETS:
            for m in rx.finditer(text):
                tok = m.group(0)
                if rid == 'S-URL-CRED':
                    pw = tok.rsplit('@', 1)[0].rsplit(':', 1)[-1]
                    if PLACEHOLDER.search(tok) or re.fullmatch(r'[A-Za-z_]+|\$?\{?[A-Z_]+\}?|<[^>]*>?|\d{1,5}', pw):
                        continue
                elif chk and not real_token(tok):
                    continue
                out.append(finding(rid, path, lineno, tok, k, level, secret=True))
    if 'G' in cls and G_HINT.search(text):
        for m in G_ASSIGN.finditer(text):
            if generic_secret(m.group(1)) and not any(f['cls'] == 'S' for f in out):
                out.append(finding('G-ASSIGN', path, lineno, m.group(1), k, level, secret=True))
    if 'P' in cls:
        for m in RRN.finditer(text):
            d = re.sub(r'\D', '', m.group(0))
            if len(d) == 13 and rrn_valid(d):
                out.append(finding('P-RRN', path, lineno, m.group(0), k, level, secret=True))
        for m in CARD.finditer(text):
            if luhn(re.sub(r'\D', '', m.group(0))):
                out.append(finding('P-CARD', path, lineno, m.group(0), k, level, secret=True))
    if 'C' in cls:
        if '@' in text:
            for m in EMAIL.finditer(text):
                local = m.group(0).split('@', 1)[0]
                if m.group(2).lower() in FILE_TLD or EMAIL_OK_DOMAIN.search(m.group(1)) or EMAIL_OK_LOCAL.match(local):
                    continue
                out.append(finding('C-EMAIL', path, lineno, m.group(0), k, level))
        for m in PHONE.finditer(text):
            d = re.sub(r'\D', '', m.group(0))
            if PHONE_FAKE.search(d[3:] if d.startswith('01') else d) or len(set(d[-8:])) <= 2:
                continue
            out.append(finding('C-PHONE', path, lineno, m.group(0), k, level))
    if 'I' in cls and I_ANY.search(text):
        for rid, rx in LINKS:
            for m in rx.finditer(text):
                out.append(finding(rid, path, lineno, m.group(0), k, level))
        for m in USERPATH.finditer(text):
            name = m.group(1) or m.group(2) or ''
            if not USER_OK.match(name) and not name.startswith(('<', '[', '$', '%', '~')):
                out.append(finding('I-USERPATH', path, lineno, m.group(0), k, level))
        for m in PRIV_IP.finditer(text):
            ip = m.group(0)
            if ip not in IP_OK and all(int(o) <= 255 for o in ip.split('.')):
                out.append(finding('I-PRIVATE-IP', path, lineno, ip, k, level))
    if 'D' in cls and C.deny:
        seen = set()
        for rx in C.deny[0]:
            for m in rx.finditer(text):
                t = m.group(0)
                if t.lower() not in seen:
                    seen.add(t.lower())
                    out.append(finding('D-DENY', path, lineno, t, k, level))
    return out


def scan_path(path, level, new=True):
    """파일 이름 자체 검사 — 차단 경로 + (public) 이름에 든 거부 목록 · 연락처"""
    out = []
    p = path.replace('\\', '/')
    for rid, rx, _ in BLOCK_PATHS:
        if level == 'sample' and rid not in SAMPLE_KEEP_RULES:
            continue
        if rx.search(p):
            out.append(finding(rid, path, 0, p, 'PATH', level))
    if new and level == 'public':
        for f in scan_text(path, 0, p, level, key='PATH', classes='CD'):
            out.append(f)
    return out


def office_text(data):
    """pptx · xlsx · docx 안의 글자 — (구성 파일, 글자) 목록"""
    parts = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            n = info.filename
            if not n.lower().endswith(('.xml', '.rels', '.vml', '.txt')) or info.file_size > 30_000_000:
                continue
            raw = z.read(n).decode('utf-8', 'replace')
            txt = html.unescape(re.sub(r'<[^>]+>', '\n', raw))
            parts.append((n, [s.strip() for s in txt.split('\n') if s.strip()]))
    return parts


def scan_blob(path, data, level, is_binary):
    """내용 전체 검사(새 파일 · 트리 점검용). 글자 파일은 줄마다, 오피스 문서는 안의 글자를 꺼내서"""
    out = []
    low = path.lower()
    if low.endswith(OFFICE_EXT):
        try:
            seen = {}
            for member, chunks in office_text(data):
                for s in chunks:
                    for f in scan_text(path, 0, s, level, key='DOC'):
                        k = (f['rule'], f['value'])
                        if k not in seen:
                            f['fp'] = fingerprint(f['rule'], path, f['value'])
                            f['where'] = member
                            f['count'] = 0
                            seen[k] = f
                        seen[k]['count'] += 1
            out.extend(seen.values())
        except (zipfile.BadZipFile, KeyError, OSError, RuntimeError):
            if 'U' in LEVEL_CLASSES[level]:
                out.append(finding('U-BINARY', path, 0, '열 수 없는 문서', hashlib.sha256(data).hexdigest(), level))
        return out
    if is_binary or low.endswith(BINARY_EXT) or b'\0' in data[:8000]:
        if 'U' in LEVEL_CLASSES[level]:
            out.append(finding('U-BINARY', path, 0, '내용 검사 불가(%s)' % (os.path.splitext(low)[1] or '바이너리'),
                               hashlib.sha256(data).hexdigest(), level))
        return out
    for i, line in enumerate(data.decode('utf-8', 'replace').splitlines(), 1):
        out.extend(scan_text(path, i, line, level))
    return out


HUNK = re.compile(rb'^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')


def unquote(p):
    if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
        body = p[1:-1].encode('utf-8')
        body = re.sub(rb'\\([0-7]{3})', lambda m: bytes([int(m.group(1), 8)]), body)
        body = body.replace(b'\\t', b'\t').replace(b'\\n', b'\n').replace(b'\\"', b'"').replace(b'\\\\', b'\\')
        return body.decode('utf-8', 'replace')
    return p


def added_lines(patch):
    """-U0 패치 → (경로, 줄 번호, 글자). 줄 수를 세어 읽으므로 「++」로 시작하는 본문도 헤더로 착각하지 않는다"""
    path, minus, plus, lineno = None, 0, 0, 0
    for raw in patch.split(b'\n'):
        if minus or plus:
            if raw.startswith(b'\\'):
                continue
            if minus and raw.startswith(b'-'):
                minus -= 1
                continue
            if plus and raw.startswith(b'+'):
                plus -= 1
                if path is not None:
                    yield path, lineno, u(raw[1:]).rstrip('\r')
                lineno += 1
                continue
            minus = plus = 0
        if raw.startswith(b'+++ '):
            p = u(raw[4:]).rstrip('\r')
            p = unquote(p.split('\t')[0] if not p.startswith('"') else p)
            path = None if p == '/dev/null' else (p[2:] if p.startswith('b/') else p)
        elif raw.startswith(b'@@ '):
            m = HUNK.match(raw)
            if m:
                minus = int(m.group(1)) if m.group(1) is not None else 1
                lineno = int(m.group(2))
                plus = int(m.group(3)) if m.group(3) is not None else 1


RENAMES = '-M100%'      # 내용이 완전히 같은 이름 바꿈만 인식 — 같은 수준 안에서 옮긴 파일은 내용을 다시 검사하지 않는다
LEVEL_RANK = {'vendor': 0, 'sample': 0, 'private': 1, 'public': 2}


def parse_z_status(b):
    """--name-status -z → [(상태, 경로, 옛 경로)] — 이름 바꿈(R) · 복사(C)는 경로가 둘"""
    items, out, i = b.split(b'\0'), [], 0
    while i + 1 < len(items):
        st = u(items[i])
        if not st:
            i += 1
        elif st[0] in 'RC' and i + 2 < len(items):
            out.append((st[0], u(items[i + 2]), u(items[i + 1])))
            i += 3
        else:
            out.append((st[0], u(items[i + 1]), None))
            i += 2
    return out


def parse_z_numstat(b):
    """--numstat -z → 바이너리 경로 집합"""
    return {u(e.split(b'\t', 2)[2]) for e in b.split(b'\0') if e.startswith(b'-\t-\t')}


def scan_change(status, binaries, patch, read_blob):
    """변경 한 묶음(스테이징 또는 커밋 하나) 검사"""
    out = []
    for st, path, old in status:
        if st == 'D':
            continue
        level = level_of(path)
        out.extend(scan_path(path, level, new=(st in 'ARC')))
        if old is not None:
            # 내용이 같은 이름 바꿈 — 더 엄한 수준으로 옮겼을 때만(예 memory/ → agent/) 내용 전체를 새 수준으로 검사
            if LEVEL_RANK[level] > LEVEL_RANK[level_of(old)]:
                out.extend(scan_blob(path, read_blob(path), level, path in binaries))
        elif path in binaries or path.lower().endswith(OFFICE_EXT):
            out.extend(scan_blob(path, read_blob(path), level, True))
    binset = set(binaries)
    for path, lineno, text in added_lines(patch):
        if path in binset or path.lower().endswith(OFFICE_EXT):
            continue
        out.extend(scan_text(path, lineno, text, level_of(path)))
    return out


def scan_staged():
    base = ('diff', '--cached', RENAMES, '--diff-filter=ACMRT')
    status = parse_z_status(git(*base, '--name-status', '-z'))
    binaries = parse_z_numstat(git(*base, '--numstat', '-z'))
    patch = git(*base, '-w', '-U0', '--no-color', '--no-ext-diff')   # -w: 줄 끝 문자 · 공백만 바뀐 줄은 새 줄로 보지 않는다
    out = scan_change(status, binaries, patch, lambda p: git('cat-file', 'blob', ':' + p))
    if C.is_source and not C.admin:
        touched = [p for _, p, _ in parse_z_status(git('diff', '--cached', '--no-renames', '--name-status', '-z'))
                   if p.startswith(GUARD_FILES)]
        for p in touched:
            out.append(finding('T-GUARD', p, 0, '가드 파일 변경 — 관리자 확인 뒤 GUARD_ADMIN=1 로 커밋', 'TAMPER', 'private'))
    return out


_EMPTY_TREE = []


def empty_tree():
    if not _EMPTY_TREE:
        _EMPTY_TREE.append(u(git('hash-object', '-t', 'tree', '--stdin', data=b'')).strip())
    return _EMPTY_TREE[0]


def scan_commit(c):
    parents = u(git('rev-list', '--parents', '-n', '1', c)).split()[1:]
    base = ('diff', RENAMES, parents[0] if parents else empty_tree(), c)   # 병합 커밋은 첫 부모 기준
    status = parse_z_status(git(*base, '--name-status', '-z'))
    binaries = parse_z_numstat(git(*base, '--numstat', '-z'))
    patch = git(*base, '-w', '-U0', '--no-color', '--no-ext-diff')
    out = scan_change(status, binaries, patch, lambda p: git('cat-file', 'blob', '%s:%s' % (c, p)))
    msg_level = 'private' if C.is_source and not C.force_level else (C.force_level or 'public')
    for i, line in enumerate(u(git('log', '-1', '--format=%B', c)).splitlines(), 1):
        out.extend(scan_text('(커밋 메시지)', i, line, msg_level))
    for f in out:
        f['commit'] = c[:9]
    return out


def scan_commits(revs):
    out = []
    for c in revs:
        out.extend(scan_commit(c))
    return out


def rev_list(*args):
    return [x for x in u(git('rev-list', '--reverse', *args)).split() if x]


def scan_tree(rev=None):
    out = []
    if rev:
        paths = [p for p in u(git('ls-tree', '-r', '-z', '--name-only', rev)).split('\0') if p]
        modes = {}
        for e in git('ls-tree', '-r', '-z', rev).split(b'\0'):
            if e:
                meta, p = e.split(b'\t', 1)
                modes[u(p)] = u(meta).split()[0]
    else:
        paths = [p for p in u(git('ls-files', '-z')).split('\0') if p]
        modes = {}
    for path in paths:
        if modes.get(path) == '160000':
            continue
        level = level_of(path)
        out.extend(scan_path(path, level))
        try:
            if rev:
                data = git('cat-file', 'blob', '%s:%s' % (rev, path))
            else:
                full = os.path.join(C.root, path)
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
                with open(full, 'rb') as f:
                    data = f.read()
        except (GuardError, OSError):
            continue
        out.extend(scan_blob(path, data, level, False))
    return out


# ───────────────────────── 출력 ─────────────────────────
def filter_allowed(found, use_allow=True):
    seen, out = set(), []
    for f in found:
        key = (f['fp'], f['rule'], f['value'], f.get('commit', ''), f['line'])   # 한 줄에 여러 건이면 모두 보인다
        if key in seen or (use_allow and f['fp'] in C.allow):
            continue
        seen.add(key)
        out.append(f)
    return out


def describe(f):
    loc = f['path'] + (':%d' % f['line'] if f['line'] else '')
    if f.get('commit'):
        loc = '%s @ %s' % (loc, f['commit'])
    extra = ''
    if f.get('count', 0) > 1:
        extra = ' (문서 안 %d곳)' % f['count']
    val = '' if C.redact else '  「%s」' % f['value']
    return '  [%s] %s%s%s  지문 %s' % (f['rule'], loc, extra, val, f['fp'])


def report(found, title, limit=60, stream=None):
    stream = stream or sys.stderr
    if not found:
        return
    by = {}
    for f in found:
        by.setdefault(f['cls'], []).append(f)
    print('✗ %s — %d건' % (title, len(found)), file=stream)
    shown = 0
    for cls in 'TSGPBDCIU':
        if cls not in by:
            continue
        print(' ▸ %s (%d건)' % (CLASS_KO[cls], len(by[cls])), file=stream)
        for f in by[cls]:
            if shown >= limit:
                break
            print(describe(f), file=stream)
            shown += 1
    if len(found) > shown:
        print('  … 외 %d건 (전체: guard.py … --list)' % (len(found) - shown), file=stream)


HELP_BLOCK = '''  → 값을 지우거나 일반화(고객명 · 수치 제거)한 뒤 다시 시도한다. --no-verify 로 넘기지 않는다.
  → 정말 넣어야 하는 값이면 사용자(관리자) 확인을 받은 뒤에만 허용 목록에 지문을 추가한다:
       GUARD_ADMIN=1 로  python .githooks/guard.py allow <지문> …  →  .githooks/guard-allow.txt 커밋'''


def summary(found):
    rows = {}
    for f in found:
        top = f['path'].split('/')
        area = '/'.join(top[:2]) if top[0] in ('agent', 'skills') and len(top) > 2 else top[0]
        rows.setdefault((f['rule'], area), 0)
        rows[(f['rule'], area)] += 1
    for (rule, area), n in sorted(rows.items()):
        print('%5d  %-18s %s' % (n, rule, area))
    print('합계 %d건' % len(found))


# ───────────────────────── 명령 ─────────────────────────
def need_deny(args, strict):
    if C.deny is not None:
        return
    if strict or getattr(args, 'require_denylist', False) or os.environ.get('GUARD_STRICT') == '1':
        raise GuardError('거부 목록(%s)을 찾지 못해 공개 범위 검사를 할 수 없음 — 원본 리포 클론 경로를 --source 또는 '
                         'GUARD_SOURCE 로 알려 주거나 GUARD_DENYLIST 로 파일을 지정' % DENY_FILE)
    print('! 가드: 거부 목록을 찾지 못해 고객 · 사업 이름 검사는 건너뜀(토큰 · 연락처 · 링크 검사는 진행)', file=sys.stderr)


def finish(found, args, title):
    found = filter_allowed(found, not getattr(args, 'no_allow', False))
    if getattr(args, 'json', False):
        json.dump(found, sys.stdout, ensure_ascii=False, indent=1)
        print()
    elif getattr(args, 'summary', False):
        summary(found)
    else:
        report(found, title, limit=100000 if getattr(args, 'list', False) else 60,
               stream=sys.stdout if getattr(args, 'list', False) else sys.stderr)
        if found and not getattr(args, 'audit', False):
            print(HELP_BLOCK, file=sys.stderr)
    return 1 if found else 0


def cmd_staged(args):
    need_deny(args, strict=False)
    return finish(scan_staged(), args, '커밋 차단 — 민감정보')


def cmd_msg(args):
    level = 'private' if C.is_source and not C.force_level else (C.force_level or 'public')
    found = []
    with open(args.file, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            if line.startswith('#'):
                continue
            found.extend(scan_text('(커밋 메시지)', i, line.rstrip('\n'), level))
    return finish(found, args, '커밋 차단 — 메시지에 민감정보')


def cmd_push(args):
    canon = bool(CANON_REMOTE.search(args.url or ''))
    need_deny(args, strict=canon)
    zero = re.compile(r'^0+$')
    revs = []
    for line in sys.stdin.read().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        _, lsha, _, rsha = parts
        if zero.match(lsha):
            continue
        known = (not zero.match(rsha)) and subprocess.run(['git', 'cat-file', '-e', rsha + '^{commit}'],
                                                          cwd=C.root, capture_output=True).returncode == 0
        if known:
            revs += rev_list('%s..%s' % (rsha, lsha))
        else:
            revs += rev_list(lsha, '--not', '--remotes=%s' % (args.remote or 'origin'))
    revs = list(dict.fromkeys(revs))
    return finish(scan_commits(revs), args, '푸시 차단 — 민감정보 (커밋 %d개 검사)' % len(revs))


def cmd_range(args):
    need_deny(args, strict=False)
    revs = rev_list(args.range)
    return finish(scan_commits(revs), args, '차단 — 민감정보 (커밋 %d개 검사)' % len(revs))


def cmd_history(args):
    need_deny(args, strict=False)
    revs = rev_list(*(args.range or ['--all']))
    args.audit = True
    return finish(scan_commits(revs), args, '이력 점검 (커밋 %d개)' % len(revs))


def cmd_tree(args):
    need_deny(args, strict=False)
    args.audit = True
    return finish(scan_tree(args.rev), args, '전체 점검 (%s)' % (args.rev or '작업 폴더의 추적 파일'))


def cmd_files(args):
    need_deny(args, strict=False)
    found = []
    for p in args.paths:
        with open(p, 'rb') as f:
            data = f.read()
        rel = os.path.relpath(os.path.abspath(p), C.root).replace('\\', '/')
        level = C.force_level or level_of(rel)
        found.extend(scan_blob(rel, data, level, False))
    return finish(found, args, '차단 — 민감정보')


def cmd_allow(args):
    if not C.admin:
        raise GuardError('허용 목록 추가는 사용자(관리자) 확인 뒤에만 — 확인을 받았으면 GUARD_ADMIN=1 로 다시 실행')
    path = os.path.join(C.root, ALLOW_FILE)
    have = set(C.allow)
    add = [x for x in args.fps if re.fullmatch(r'[0-9a-f]{20}', x) and x not in have]
    bad = [x for x in args.fps if not re.fullmatch(r'[0-9a-f]{20}', x)]
    if bad:
        raise GuardError('지문 형식이 아님: %s' % ' '.join(bad))
    if add:
        with open(path, 'a', encoding='utf-8', newline='\n') as f:
            for x in add:
                f.write('%s%s\n' % (x, ('  # ' + args.note) if args.note else ''))
    print('허용 목록 +%d건 (%s)' % (len(add), ALLOW_FILE))
    return 0


def cmd_exempt(args):
    """샘플로 확인받은 파일을 가드에서 제외(토큰 · 개인키 검사는 유지). 경로 대신 경로 지문만 적는다"""
    tracked = [p for p in u(git('ls-files', '-z')).split('\0') if p]
    if args.list or not args.paths:
        hit = [p for p in tracked if path_fp(p) in C.exempt]
        print('샘플 예외 %d건(허용 목록) · 그중 지금 추적 중인 파일 %d개' % (len(C.exempt), len(hit)))
        for p in hit:
            print('  ' + p)
        return 0
    if not C.admin:
        raise GuardError('샘플 예외 추가는 사용자(관리자) 확인 뒤에만 — 확인을 받았으면 GUARD_ADMIN=1 로 다시 실행')
    add = []
    for p in args.paths:
        rel = os.path.relpath(os.path.abspath(p), C.root).replace('\\', '/')
        if rel.startswith('..'):
            raise GuardError('리포 밖 경로: %s' % p)
        fp = path_fp(rel)
        if fp not in C.exempt and fp not in add:
            add.append(fp)
    if add:
        with open(os.path.join(C.root, ALLOW_FILE), 'a', encoding='utf-8', newline='\n') as f:
            for x in add:
                f.write('p:%s%s\n' % (x, ('  # ' + args.note) if args.note else ''))
    print('샘플 예외 +%d건 (%s)' % (len(add), ALLOW_FILE))
    return 0


def cmd_doctor(args):
    ok = True

    def line(good, text):
        nonlocal ok
        ok = ok and good
        print('%s %s' % ('✓' if good else '✗', text))

    print('guard.py %s · python %s' % (VERSION, sys.version.split()[0]))
    print('리포: %s (%s)' % (C.root, '원본' if C.is_source else '공유 · 공개 수준'))
    hp = u(git('config', '--get', 'core.hooksPath', check=False)).strip()
    line(hp.replace('\\', '/').rstrip('/').endswith('.githooks'), 'core.hooksPath = %s' % (hp or '(미설정 — git config core.hooksPath .githooks)'))
    for h in ('pre-commit', 'commit-msg', 'pre-push', '_guard.sh'):
        line(os.path.isfile(os.path.join(C.root, '.githooks', h)), '.githooks/%s' % h)
    line(C.deny is not None, '거부 목록: %s' % ('%d개 · %s' % (C.deny[1], C.deny_src) if C.deny else '찾지 못함'))
    print('  허용 목록 지문 %d개 · 샘플 예외 경로 %d개' % (len(C.allow), len(C.exempt)))
    for cand in (os.path.join(os.path.dirname(C.root), 'Share-Agent-Skill-dy'), C.root):
        ms = os.path.join(cand, 'share', 'mirror-from-source.sh')
        if os.path.isfile(ms):
            with open(ms, encoding='utf-8') as f:
                body = f.read()
            m = re.search(r'^EXCLUDE=\(\n(.*?)^\)', body, re.S | re.M)
            listed = {l.split('#', 1)[0].strip() for l in (m.group(1).splitlines() if m else [])} - {''}
            line(listed == set(MIRROR_EXCLUDE), '미러 제외 목록 일치 (%s)' % ('같음' if listed == set(MIRROR_EXCLUDE) else
                 '다름 — 스크립트에만 %s · 가드에만 %s' % (sorted(listed - set(MIRROR_EXCLUDE)), sorted(set(MIRROR_EXCLUDE) - listed))))
            line('guard.py' in body, '미러 스크립트가 가드를 부름')
            break
    return 0 if ok else 1


def cmd_selftest(args):
    C.deny = compile_deny(['가나다은행', 'ZQXJ', 'Qwerty Holdings', '나라'])
    C.allow = frozenset()
    rnd = 'q7Rk2ZpX9mVb4LtY8sWc3NdF6hJg1TaE5uHo0PiK'
    mail = _b('someone.real', '@', 'gmail', '.com')      # 예시 값은 실행할 때 조립한다 — 이 파일도 공개 수준 검사를 받는다
    phone = _b('010-2345', '-6789')
    ip = _b('192.168', '.10.37')
    cases = [  # (수준, 글자, 나와야 할 규칙 또는 None)
        ('vendor', _b('token = ', 'gh', 'p_', rnd[:36]), 'S-GITHUB'),
        ('vendor', _b('xox', 'b-', '8273645910-', rnd[:24]), 'S-SLACK-TOKEN'),
        ('vendor', _b('https://hooks.slack', '.com/services/T01ABCDEF/B02GHIJKL/', rnd[:24]), 'S-SLACK-WEBHOOK'),
        ('vendor', _b('-----BEGIN RSA ', 'PRIVATE KEY-----'), 'S-PRIVKEY'),
        ('vendor', _b('sk-', 'ant-', 'api03-', rnd), 'S-ANTHROPIC'),
        ('vendor', _b('AI', 'za', rnd[:35]), 'S-GOOGLE-API'),
        ('vendor', _b('postgres://admin:', 'S3cr3tPw9', '@db.corp-net.io/app'), 'S-URL-CRED'),
        ('vendor', 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', None),
        ('vendor', 'export GITHUB_TOKEN=$GITHUB_TOKEN', None),
        ('vendor', 'contact: ' + mail, None),
        ('private', _b('SLACK_BOT_TOKEN = "', rnd[:30], '"'), 'G-ASSIGN'),
        ('private', 'password: process.env.DB_PASSWORD', None),
        ('private', 'token = os.environ["SLACK_TOKEN"]', None),
        ('private', 'api_key: YOUR_API_KEY_HERE', None),
        ('private', _b('주민번호 ', '800101', '-', '1234560'), 'P-RRN'),
        ('private', '주민번호 900101-1234567', None),
        ('private', '담당 가나다은행 홍길동 %s %s' % (mail, phone), None),
        ('public', '담당자 메일 ' + mail, 'C-EMAIL'),
        ('public', 'Co-Authored-By: Claude <noreply@anthropic.com>', None),
        ('public', 'git clone git@github.com:owner/repo.git  logo@2x.png  react@18.3.1', None),
        ('public', '연락처 ' + phone, 'C-PHONE'),
        ('public', '예시 010-1234-5678 · 010-0000-0000', None),
        ('public', '가나다은행 제안 건', 'D-DENY'),
        ('public', 'ZQXJ 프로젝트', 'D-DENY'),
        ('public', 'zqxj 소문자 · AZQXJB 붙은 글자', None),
        ('public', 'qwerty holdings 사례', 'D-DENY'),
        ('public', '우리나라 지도 · 나라 장터', 'D-DENY'),
        ('public', '우리나라 지도만', None),
        ('public', _b('https://docs.google', '.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz012345/edit'), 'I-GDRIVE'),
        ('public', _b('https://www.figma', '.com/design/AbCdEfGhIjKlMnOpQrSt12/Name'), 'I-FIGMA'),
        ('public', 'figma.com/design/:fileKey/:fileName', None),
        ('public', _b('C:', '\\Users\\', 'gildong', '\\Documents'), 'I-USERPATH'),
        ('public', 'C:\\Users\\<사용자>\\Documents · ~/Documents · /Users/username/x', None),
        ('public', '서버 %s:8001' % ip, 'I-PRIVATE-IP'),
        ('public', '예: http://192.168.x.x:포트/ · 192.168.0.1 · 10.0.0.0/8', None),
    ]
    fails = 0
    for level, text, want in cases:
        got = [f['rule'] for f in scan_text('t.md', 1, text, level)]
        good = (want in got) if want else (not got)
        if not good:
            fails += 1
            print('✗ [%s] 기대 %s · 결과 %s · %s' % (level, want, got, mask(text)))
    pc = [('agent/x/input/a.pdf', 'B-WORKDIR'), ('agent/x/input/.gitkeep', None), ('.env', 'B-ENV'), ('.env.example', None),
          ('keys/id_rsa', 'B-KEYFILE'), ('conf/credentials.json', 'B-CREDFILE'), ('design/tokens.json', None),
          ('memory/local-x.md', 'B-LOCALMEM'), ('skills/a/가나다은행_견적.md', 'D-DENY')]
    for p, want in pc:
        got = [f['rule'] for f in scan_path(p, 'public')]
        if ((want in got) if want else (not got)) is False:
            fails += 1
            print('✗ 경로 %s · 기대 %s · 결과 %s' % (p, want, got))
    sample = 'agent/x/examples/고객_견적.html'
    C.exempt = frozenset([path_fp(sample)])
    other = 'agent/x/examples/다른_견적.html'
    if (level_of(sample) != 'sample' or scan_path(sample, 'sample')
            or scan_text(sample, 1, '가나다은행 견적 ' + mail, 'sample')
            or 'S-GITHUB' not in [f['rule'] for f in scan_text(sample, 1, _b('gh', 'p_', rnd[:36]), 'sample')]
            or [f['rule'] for f in scan_path(other, level_of(other))] != ['B-EXAMPLE']
            or scan_blob('agent/x/examples/shot.png', b'\x89PNG\0', 'sample', True)):
        fails += 1
        print('✗ 샘플 예외 판정')
    C.exempt = frozenset()
    patch = (b'diff --git a/a.md b/a.md\n--- a/a.md\n+++ b/a.md\n@@ -3,0 +4,2 @@\n+++ not a header\n+second\n'
             b'diff --git a/b.md b/b.md\n--- /dev/null\n+++ b/b.md\n@@ -0,0 +1 @@\n+only\n')
    got = list(added_lines(patch))
    if got != [('a.md', 4, '++ not a header'), ('a.md', 5, 'second'), ('b.md', 1, 'only')]:
        fails += 1
        print('✗ 패치 읽기', got)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('xl/sharedStrings.xml', '<sst><si><t>가나다은행 견적</t></si><si><t>일반 문구</t></si></sst>')
    got = [f['rule'] for f in scan_blob('s.xlsx', buf.getvalue(), 'public', True)]
    if got != ['D-DENY']:
        fails += 1
        print('✗ 오피스 문서', got)
    if [f['rule'] for f in scan_blob('a.png', b'\x89PNG\0\0', 'public', True)] != ['U-BINARY'] or scan_blob('a.png', b'\x89PNG\0', 'private', True):
        fails += 1
        print('✗ 바이너리 수준 판정')
    print('selftest %s — 사례 %d개' % ('통과' if not fails else '실패 %d건' % fails, len(cases) + len(pc) + 3))
    return 1 if fails else 0


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog='guard.py', description='민감정보 커밋 · 푸시 차단 검사기')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--repo')
    common.add_argument('--level', choices=('auto', 'private', 'public'), default='auto')
    common.add_argument('--denylist')
    common.add_argument('--source', help='원본 리포 클론 경로(거부 목록 위치)')
    common.add_argument('--require-denylist', action='store_true')
    common.add_argument('--redact', action='store_true', help='찾은 값을 출력하지 않음')
    common.add_argument('--no-allow', action='store_true', help='허용 목록을 무시')
    common.add_argument('--summary', action='store_true')
    common.add_argument('--list', action='store_true')
    common.add_argument('--json', action='store_true')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('staged', parents=[common]).set_defaults(fn=cmd_staged)
    p = sub.add_parser('msg', parents=[common]); p.add_argument('file'); p.set_defaults(fn=cmd_msg)
    p = sub.add_parser('push', parents=[common]); p.add_argument('remote', nargs='?'); p.add_argument('url', nargs='?'); p.set_defaults(fn=cmd_push)
    p = sub.add_parser('range', parents=[common]); p.add_argument('range'); p.set_defaults(fn=cmd_range)
    p = sub.add_parser('history', parents=[common]); p.add_argument('range', nargs='*'); p.set_defaults(fn=cmd_history)
    p = sub.add_parser('tree', parents=[common]); p.add_argument('--rev'); p.set_defaults(fn=cmd_tree)
    p = sub.add_parser('files', parents=[common]); p.add_argument('paths', nargs='+'); p.set_defaults(fn=cmd_files)
    p = sub.add_parser('allow', parents=[common]); p.add_argument('fps', nargs='+'); p.add_argument('--note', default=''); p.set_defaults(fn=cmd_allow)
    p = sub.add_parser('exempt', parents=[common]); p.add_argument('paths', nargs='*'); p.add_argument('--note', default='')
    p.set_defaults(fn=cmd_exempt)
    sub.add_parser('doctor', parents=[common]).set_defaults(fn=cmd_doctor)
    sub.add_parser('selftest', parents=[common]).set_defaults(fn=cmd_selftest)
    args = ap.parse_args()
    try:
        if args.cmd != 'selftest':
            setup(args)
        return args.fn(args)
    except GuardError as e:
        print('✗ 가드 실행 오류 — %s' % e, file=sys.stderr)
        return 2
    except Exception as e:  # 검사를 못 하면 내보내지 않는다
        print('✗ 가드 실행 오류 — %s: %s' % (type(e).__name__, e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
