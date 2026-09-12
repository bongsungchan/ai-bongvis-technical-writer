---
description: Bongvis 설정 — 개인/조직 설정 생성, 비밀 취급, 설정 승격
argument-hint: [env|custom|promote]
---

`bongvis/IDENTITY.md` 3절의 규칙을 따른다. `$ARGUMENTS` 로 서브커맨드가 없으면 무엇을 할지 먼저 묻는다: `env`(비밀 설정) / `custom`(개인·조직 설정) / `promote`(개인→조직 승격).

## env

1. 프로젝트 루트에 `.env` 파일과 `.gitignore` 를 확인한다.
2. `.gitignore` 에 `.env` 항목이 없으면 추가하고 알린다. 묻지 않는다.
3. Atlassian(Confluence) 게시가 필요한지 사용자에게 확인한다.
   - MCP Atlassian 커넥터가 이미 연결돼 있으면 그것을 쓰고 `.env` 토큰은 요구하지 않는다.
   - 커넥터가 없으면 `.env` 에 넣을 변수명만 안내한다(`CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`). 토큰 값 자체를 대화창에 입력받지 않는다 — 사용자가 직접 `.env` 파일에 적도록 안내만 한다.
4. 설정 내용을 화면에 보여줄 때 토큰 값은 항상 `****` 로 가린다.

## custom

1. `~/.bongvis/user.json` 이 없으면 `templates/user.schema.json` 을 기준으로 질문해서 만든다: 애칭, 대화 말투, 기본 언어.
2. 프로젝트의 `bongvis.team.json` 이 없으면 `templates/team.schema.json` 을 기준으로 빈 골격을 만든다 — `publish.target` 은 Stage 1이므로 `null` 로 둔다.
3. 용어집(`glossary`)에 넣을 항목이 있는지 묻는다. 없으면 빈 배열로 둔다. 용어집은 조직 층(`bongvis.team.json`)에만 넣는다.
4. 개인 정보(애칭·말투·언어 선호)를 조직 파일에 넣지 않는다. 반대로 게시 대상·용어집을 개인 파일에 넣지 않는다.

## promote (Stage 3)

1. `~/.bongvis/user.json` 과 `.bongvis/training.json` 을 읽어 조직 규칙 후보를 뽑는다: 용어 결정, 문서 구조 변경, 게시 대상, 문체 규칙.
2. 후보를 사람에게 표로 보여주고 무엇을 승격할지 고르게 한다.
3. 고른 항목만 `bongvis.team.json` 으로 옮기고, 옮긴 항목은 개인 층에서 지운다.
4. 애칭·대화 말투·개인 언어 선호는 후보에 올리지 않는다.

## 공통 원칙

- 토큰은 `.json` 파일 어디에도 쓰지 않는다.
- 설정을 새로 만들기 전에 기존 파일이 있으면 먼저 보여주고 덮어쓸지 확인한다.
