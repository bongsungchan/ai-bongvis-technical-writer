---
description: Bongvis 설정 — 개인/조직 설정 생성, 비밀 취급, 설정 승격
argument-hint: [env|custom|promote]
---

`bongvis/IDENTITY.md` 3절의 규칙을 따른다. `$ARGUMENTS` 로 서브커맨드가 없으면 하나씩 번호로 묻고 보기는 a/b/c 로 매긴다: a) `env`(비밀 설정) b) `custom`(개인·조직 설정) c) `promote`(개인→조직 승격).

## env

새 자격정보를 만들기 전에 **이미 있는 것부터 찾는다.** 순서를 건너뛰지 않는다 — 프로젝트마다 이미 동작하는 게시 경로가 있을 수 있고, 그걸 두고 새 변수명을 만들면 자격정보가 중복되고 실제로는 아무것도 안 쓰인다.

1. **기존 게시 스크립트/코드를 찾는다.** `confluence`, `atlassian`, `wiki` 같은 키워드로 프로젝트를 grep 해서 이미 게시를 수행하는 스크립트가 있는지 확인한다. 있으면 그 스크립트를 읽어 **실제로 쓰는 환경변수 이름**과 base URL 처리 방식(환경변수인지, 코드에 하드코딩인지)을 그대로 파악한다. 추측하지 않는다.
2. **기존 `.env` 를 확인한다.** 스크립트가 참조하는 변수명이 이미 `.env` 에 있으면 그걸로 끝 — 새로 만들지 않는다. (예: Confluence 전용 변수가 없어도 `JIRA_EMAIL`/`JIRA_API_TOKEN` 처럼 Atlassian 계정 공용 토큰을 이미 쓰고 있을 수 있다.)
3. **MCP Atlassian 커넥터가 연결돼 있는지** 확인한다. 있으면 그것을 우선하고 `.env` 토큰은 요구하지 않는다.
4. 위 셋 다 없을 때만 새 변수를 제안한다 — 이때도 변수명을 이 플러그인이 임의로 정하지 않고, 그 프로젝트에 이미 있는 네이밍 관례(예: `JIRA_*` 접두사를 쓰는 프로젝트면 `CONFLUENCE_*` 대신 `JIRA_*` 로 맞춘다)를 먼저 물어서 따른다.
5. 어느 경로든 확정되면 `bongvis.team.json` 의 `publish.method`(`script`/`mcp`/`rest`), `publish.script_path`, `publish.credential_vars` 에 **실제 값**을 기록한다. 토큰 값 자체는 절대 기록하지 않는다 — 변수 이름만 기록한다.
6. `.env` 파일과 `.gitignore` 를 확인해 `.gitignore` 에 `.env` 항목이 없으면 추가하고 알린다. 묻지 않는다.
7. 설정 내용을 화면에 보여줄 때 토큰 값은 항상 `****` 로 가린다.

## custom

1. `~/.bongvis/user.json` 이 없으면 `templates/user.schema.json` 을 기준으로 질문해서 만든다: 애칭, 대화 말투, 기본 언어.
2. 프로젝트의 `bongvis.team.json` 이 없으면 `templates/team.schema.json` 을 기준으로 빈 골격을 만든다 — `publish.targets` 는 Stage 1이므로 빈 배열로 둔다.
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
