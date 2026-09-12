# technical-writer

기술 문서 작성을 돕는 Claude Code 플러그인. 코드와 커밋을 근거로 README·API 문서·릴리즈 노트를 쓰고, 기존 문서를 코드와 대조해 검수한다.

## 설치

```
/plugin marketplace add ~/Documents/ai-bongvis/technical-writer
/plugin install technical-writer@ai-bongvis
```

## 구성

| 종류 | 이름 | 역할 |
|---|---|---|
| Skill | `write-docs` | 코드를 읽고 문서 작성·갱신 |
| Skill | `review-docs` | 문서를 코드와 대조해 오류 검출 |
| Command | `/docs [경로]` | 대상 경로 문서화 |
| Command | `/release-notes [git 범위]` | 커밋 범위로 릴리즈 노트 작성 |

## 구조

```
.claude-plugin/
  plugin.json        # 플러그인 메타데이터
  marketplace.json   # 로컬 마켓플레이스 정의
commands/            # 슬래시 커맨드
skills/              # 스킬 (SKILL.md + 참고 자료)
```
