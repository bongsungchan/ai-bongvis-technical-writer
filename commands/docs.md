---
description: 대상 경로의 기술 문서를 작성하거나 갱신한다
argument-hint: [파일 또는 모듈 경로]
---

`$ARGUMENTS` 를 문서화 대상으로 삼아 `write-docs` 스킬을 따른다.

인자가 비어 있으면 현재 변경사항(`git diff`, `git status`)을 대상으로 삼고, 어떤 문서를 어느 범위로 쓸지 먼저 사용자에게 확인한다.
