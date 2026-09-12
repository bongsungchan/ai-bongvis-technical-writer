# Bongvis

개발 문서(회의록·ADR·PRD·FRD·TDD)를 정확성 우선으로 작성·개정·검수하는 Claude Code 플러그인.

| 정본 | 내용 |
|---|---|
| [`bongvis/IDENTITY.md`](bongvis/IDENTITY.md) | 정체성·원칙 — 무엇을 지키는가 |
| [`bongvis/HOUSE-STYLE.md`](bongvis/HOUSE-STYLE.md) | 작성·게시 실무 규칙 — 어떻게 쓰는가 (**검증됨**, 90점 통과 2건) |
| [`scripts/`](scripts/) | 검증된 도구 — HTML 산출·Confluence storage 변환·Mermaid 테마 |

## 설치

```
/plugin marketplace add ~/Documents/ai-bongvis/technical-writer
/plugin install bongvis@ai-bongvis
```

## 명령

| 명령 | 역할 |
|---|---|
| `/write` | 새 문서 작성 (회의록·ADR·PRD·FRD·TDD) |
| `/revise` | 기존 문서 개정 (원본 이어쓰기) |
| `/setup` | 개인/조직 설정 생성, 비밀 취급, 설정 승격 |
| `/train` | 문서 피드백 입력, 템플릿 규칙 개정 |

슬래시 커맨드 없이 "ADR 써줘"처럼 자연어로 요청해도 `write-docs` 스킬이 같은 절차를 수행한다.

## 구조

```
.claude-plugin/
  plugin.json        # 플러그인 메타데이터 (name: bongvis)
  marketplace.json    # 로컬 마켓플레이스 정의
bongvis/
  IDENTITY.md          # 정체성·규칙 규격 (정본)
commands/              # /write /revise /setup /train
skills/write-docs/      # 자연어 트리거 진입점
templates/              # 문서 종류별 JSON 템플릿 + 설정 스키마
```

## 현재 단계

Stage 1(개인·로컬 전용) 구현 기준. Confluence 게시·`/train import`·`/setup promote` 는 `bongvis/IDENTITY.md` 10절 Stage 2/3 항목이며, 커맨드 골격은 있으나 실 연동은 아직 없다.
