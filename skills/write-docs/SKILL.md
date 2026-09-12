---
name: write-docs
description: 회의록/ADR/PRD/FRD/TDD 를 새로 쓰거나 개정한다. "문서 써줘", "ADR 만들어줘", "회의록 정리해줘", "이거 문서화해줘" 같은 자연어 요청에서 사용한다. 슬래시 커맨드 `/write`, `/revise` 와 동일한 절차를 따른다.
---

# write-docs

이 스킬은 `commands/write.md`(신규 작성)와 `commands/revise.md`(개정)의 절차를 그대로 수행한다. 사용자가 슬래시 커맨드 없이 자연어로 문서 작성을 요청했을 때 진입점이 된다.

## 판단

- "새로 만들어줘/작성해줘" 류 → `/write` 절차
- "고쳐줘/이어써줘/업데이트해줘" + 기존 문서를 가리킴 → `/revise` 절차
- 문서 종류가 불명확하면 추측하지 말고 `bongvis/IDENTITY.md` 6-1절의 다섯 종류 중 무엇인지 먼저 묻는다.

## 반드시 지키는 것

- `templates/<종류>.json` 없이 문서를 쓰지 않는다.
- 필수 섹션(`required: true`)이 비면 되묻는다. 추측으로 채우지 않는다.
- 대화 말투를 문서 본문에 넣지 않는다.
- 로컬 미리보기 없이 게시하지 않는다.

세부 절차는 `commands/write.md` / `commands/revise.md` 를 참조한다.
