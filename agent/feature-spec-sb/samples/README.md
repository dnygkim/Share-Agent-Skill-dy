# samples — HTML로 추출된 화면설계 파일

새 화면을 그릴 때 **패턴으로 참고하는 완성 예시**를 모아둔 곳이다.
작성 규칙 자체는 `SKILL.md`와 `rules/`에 있고, 여기 있는 건 그 규칙이 실제로 적용된 결과물이다.

## 두 종류가 있다

| 폴더 | 형태 | 쓰는 법 |
|---|---|---|
| `admin/` | **화면 본문만** (`*.src.html`) — 시트 골격·템플릿 CSS 없음 | `build_admin_sb.py`가 템플릿과 결합해 완성 SB로 만든다. 새 어드민 화면을 쓸 때 이 마크업을 본뜬다 |
| `b2c/` | **완성된 화면설계서** (단독 HTML) — 브라우저로 바로 열림 | 결과물이 어떻게 나오는지 확인용. 양식·번호 매김·Description 작성 수준의 기준선 |

`admin/`은 KT AX 화면만 수록했다 (타 고객 샘플 미포함).

## b2c/ — 범용 B2C 예시

회원가입 4단계(약관 동의 → 본인 인증 → 정보 입력 → 완료)를 모바일·PC 양쪽으로 뽑은 것이다.
같은 `A-01_screens.json` 하나로 두 벌을 만들었으므로 **내용은 같고 양식만 다르다** — PC/모바일
차이를 비교할 때 이 쌍을 본다.

| 경로 | 내용 |
|---|---|
| `b2c/A-01_screens.json` | 입력 원본. 이 파일로 아래 결과를 언제든 재생성할 수 있다 |
| `b2c/mobile/` | 모바일 4장 (캔버스 390px) |
| `b2c/pc/` | PC 4장 (캔버스 1440px) |
| `b2c/long-page/` | 공지 80행짜리 긴 화면 1장 — **캔버스 세로에 상한이 없다는 것**을 확인하는 예시 |

`A-01-003`(정보 입력)에는 이탈 확인 모달이 들어 있다. 모달을 별도 파일로 빼지 않고
메인 캔버스 우측에 서브 캔버스로 붙이는 방식(`SKILL.md` §4.3)의 실물 예시다.

## 재생성

```bash
python scripts/generate_sb.py --variant mobile --input samples/b2c/A-01_screens.json --output <출력폴더>
python scripts/generate_sb.py --variant pc     --input samples/b2c/A-01_screens.json --output <출력폴더>
```

이 예시들은 화면당 24개 항목(시트 골격·메타 헤더 값·캔버스 치수·로고 무결성·배지와 Description
번호 1:1·HTML-to-Figma 규칙)을 검사해 전 항목을 통과한 상태다.
