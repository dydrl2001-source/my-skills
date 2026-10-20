# 기존 스킬 분석 · 2026-10-21

기준 저장소: [dydrl2001-source/my-skills](https://github.com/dydrl2001-source/my-skills)  
기준 커밋: `96a0c6112228cc44929e1eacaefd4568e3e1ac1b`

기존 `skills/`의 22개 스킬 폴더를 읽고 관련 참조·실행 코드·`.claude` 복사본·백업을 대조했다. 아래 평가는 파일 내용과 구조를 확인한 **정적 분석**이다. 기존 스킬을 실행하거나 추가 패키지를 설치하지 않았고, 기존 스킬·설정·플러그인은 변경하지 않았다. 프레임워크와 외부 서비스의 최신 버전·CLI 호환성은 이번에 외부 검증하지 않았다.

## 판단

활용할 재료는 많지만 전체를 그대로 설치하기보다 목적별로 골라 통합하는 편이 적합하다. 디자인·카드뉴스·요청 구체화의 내용이 특히 유용하다. 개발 전체를 여러 AI로 반복 검토하는 과정은 현재 Superpowers와 engineering-upgrades에 상당 부분 겹치며, 추가 CLI와 계정·세션 관리를 요구한다.

권고하는 순서는 다음과 같다. 이번 분석은 이 통합을 실행한 것이 아니다.

1. **디자인 기획**: `design-prompt-generator-v2`의 업종·사용자 여정·감성·디자인 토큰·컴포넌트 체계를 우선 정리한다. 랜딩페이지의 콘텐츠 구조와 frontend-design의 시각 원칙은 필요한 참조로 통합한다. 실제 브랜드와 접근성 요구를 우선하고 특정 폰트·스택·11개 섹션을 일괄 강제하지 않는다.
2. **카드뉴스**: 두 생성기를 비교 병합한다. 일반판의 번들 한글폰트 처리와 실제 렌더러를 기준 후보로 삼고, 배경 구성 원칙은 Midjourney 지침에서 가져온다. 이미지 제공자, 출력 크기, 번호 표시, 텍스트 배치를 선택 가능하게 한다.
3. **요청 구체화**: `prompt-enhancer`의 기존 프로젝트 조사와 성공 기준을 engineering-upgrades의 보조 체크리스트로 흡수한다. meta-prompt-generator의 재사용 명령 템플릿은 필요한 때만 사용한다. 승인 단계나 개발 절차를 하나 더 붙이지 않는다.
4. **문서 수집·회고**: web-to-markdown과 code-prompt-coach는 수요가 생길 때 개조한다. 전자는 원문·요약·출처를 구분하고 현재 연결된 수집 도구를 사용한다. 후자는 선택한 프로젝트·기간만 분석하고 측정값과 추정값을 구분한다.

## 22개 전체 비교

‘보존’은 지침을 참고할 가치가 있다는 뜻이며, 모든 환경에서 즉시 실행됨을 뜻하지 않는다.

| 스킬 폴더 | 목적·살릴 부분 | 현재 제약 | 권고 |
| --- | --- | --- | --- |
| `card-news-generator` | 한국어 카드뉴스 PNG, 배경·오버레이·번들 폰트 | Pillow 필요. 코드와 지침의 텍스트 폭·번호 처리 차이, 출력 경로 의존 | 통합의 주 구현 후보 |
| `card-news-generator-v2` | 동일한 카드뉴스 제작 | 지침은 일반판과 거의 동일하지만 폰트 처리는 Linux 경로에 묶임 | 일반판과 선택 병합 |
| `design-prompt-generator-v2` | 업종→여정→감성→브랜드→토큰→컴포넌트→상호작용 | 조사 결과를 사실로 쓰기 위한 출처 확인 과정 보강 필요 | 맞춤화 우선 |
| `frontend-design` | 시각적 위계·차별화·완성도 원칙 | 글꼴·레이아웃 금지가 절대적이며 참조한 LICENSE.txt 누락 | 출처 파일 확인 후 필요한 원칙 통합 |
| `landing-page-guide` | 전환 콘텐츠·접근성·반응형 체크 | 11요소와 Next/TS/Tailwind/ShadCN 일괄 강제 | 콘텐츠 참조로 병합 |
| `landing-page-guide-v2` | 위 구조에 강한 디자인 지침 추가 | 794줄로 중복이 크고 참조 코드와 자체 금지 규칙이 충돌 | 축약하여 디자인 묶음에 통합 |
| `midjourney-cardnews-bg` | 중앙 여백·대비·가장자리 구성·주제별 팔레트 | 영문 프롬프트 생성 지침. 이미지 실행 도구는 없고 모델·크기 가정 고정 | 카드뉴스의 선택 참조로 흡수 |
| `gemini-logo-remover` | 사각 마스크 인페인팅 예제 | OpenCV 등 필요. 파일 읽기·저장 검사와 투명도 보존, 결과 검수 부족 | 필요 시 범용 보정 절차로 재작성 |
| `flutter-init` | 도메인·스택 프리셋, 계층별 생성 체크리스트 | Flutter 도구체인 필요. Freezed 버전 설명과 의존성 불일치 | Flutter 프로젝트에서만 개조 |
| `nextjs15-init` | Todo/Blog/Dashboard 등 초기 구조 | latest 생성과 15 고정 예제가 혼재. 별도 API 파일의 데이터 연결 누락 | 버전 정책·예제를 수정한 뒤 사용 |
| `meta-prompt-generator` | 단계·의존성·성공 기준을 재사용 명령으로 구성 | `.claude/commands`, Task, Sonnet과 주제별 에이전트 수에 결합 | 요청 정리용 부분만 병합 |
| `prompt-enhancer` | 기존 코드·관례·유사 기능을 읽고 요구사항 구체화 | 고정 업로드 경로·도구명, 구현 전 항상 승인받도록 지시 | engineering-upgrades에 선택 흡수 |
| `codex` | 다른 에이전트에서 Codex CLI로 위임 | 소문자 파일명, 모델 선택지 고정, 매 명령 후 질문 | 외부 CLI 위임 수요가 있을 때만 개조 |
| `codex-claude-loop` | 구현과 독립 리뷰의 역할 구분 | 반복 호출, 매 변경 리뷰, 회차·시간 종료 기준 없음 | 검토 원칙만 기존 절차에 흡수 |
| `codex-claude-cursor-loop` | 계획·검토·구현을 3개 도구에 분배 | CLI 3종·계정·세션·출력 파싱 필요. 복사본마다 명령이 다름 | 실제 사용 수요 전까지 보류 |
| `code-changelog` | 변경 이력과 HTML 뷰어라는 아이디어 | 필요한 Python 생성기·로거 파일 누락, HonKit 안내와 본문 불일치 | 실행 도구로는 보류, 템플릿만 참고 |
| `code-prompt-coach` | 프롬프트·도구 사용·오류·시간을 회고 | 로컬 Claude JSONL 전용, 1,636줄, 원문 재인용·비용 추정 규칙 개선 필요 | 선택형 회고 스킬로 개조 후보 |
| `workthrough` | 변경 이유·파일·검증을 작업일지에 기록 | 모든 개발 후 자동 기록으로 문서가 과도해질 수 있음 | v2와 병합, 기록 조건 선택 |
| `workthrough-v2` | 간결한 한국어 변경 요약 | v1과 같은 스킬 이름. 간단한 기록에도 VitePress/pnpm 작업 요구 | 요약 형식만 우선 채택 |
| `web-search` | 텍스트·뉴스·이미지 검색 CLI | Claude 경로 고정, 실행 시 의존성 자동 설치, 버전 미고정 | 대체 검색 경로로 필요할 때 개조 |
| `web-to-markdown` | 문서 원본과 AI용 요약을 함께 보관 | 773줄, WebFetch/AskUserQuestion에 결합, 근거 없는 절감 수치 | 기존 수집 도구에 맞춰 축약·통합 |
| `chatgpt-web-research` | 사용자가 지정한 ChatGPT 웹 계정에서 별도 조사 | 로그인된 데스크톱 Chrome·특정 브라우저 스킬·모델 메뉴 필요. 일반 검색을 금지 | 해당 웹 경로를 명시 요청했을 때만 검토 |

## 구체적으로 확인한 문제

### 1. 배포 전에 파일명과 스킬 이름 정리가 필요하다

현재 파일은 YAML로 읽을 수 있지만, 다음은 개인 플러그인 패키지의 `skills/<name>/SKILL.md` 배치와 이름 일치 규칙에 맞춰 수정해야 한다. Windows의 대소문자 무시 탐색 결과를 Linux 파일명으로 착각하면 안 된다.

| 대상 | 실제 상태 |
| --- | --- |
| `skills/codex/skill.md` | 파일명이 소문자 `skill.md` |
| `skills/code-prompt-coach/Skill.md:2` | 파일명이 `Skill.md`, name은 `Prompt Coach` |
| `skills/meta-prompt-generator/SKILL.md:2` | 폴더명과 달리 name은 `메타-프롬프트-생성기` |
| `skills/midjourney-cardnews-bg/SKILL.md:2` | name은 `midjourney-card-news-backgrounds` |
| `skills/workthrough-v2/SKILL.md:2` | name이 `workthrough`여서 v1과 중복 |

루트의 `chatgpt-web-research/`에는 `agents/openai.yaml`만 있고 SKILL.md가 없다. 완성된 별도 스킬로 세지 않았다.

### 2. ‘v2’와 복사본을 최신본으로 단정할 수 없다

- `skills/`에 22개, `.claude/skills/`에 대응 복사본 11개가 있다. SKILL 본문 바이트 기준 9개는 같고, `flutter-init`과 `codex-claude-cursor-loop` 2개는 다르다. 별도 스킬 33개로 세면 중복된다.
- `.claude`의 Flutter판에는 `skills/`판의 Android desugaring·Freezed 관련 보완 일부가 없다. 반대로 Cursor-loop 복사본에는 구조화 출력과 세션 처리 설명이 더 있다. 다만 `.claude/skills/codex-claude-cursor-loop/SKILL.md:71`은 MCP 자동 승인 옵션을 기본 명령에 포함한다. 차이를 검토한 뒤 선택해야 한다.
- 카드 두 SKILL.md의 차이는 이름과 제목뿐이다. 그러나 일반판 `generate_card.py:147`은 번들 폰트를 먼저 찾고, v2 `generate_card.py:143`은 특정 Linux Noto 경로를 찾는다. 일반판 `auto_generator.py:177`은 번호를 제거하지만 v2는 표시한다. 백업에도 별도 개선 흔적이 있다.

### 3. 실행 파일과 코드 예제가 완결되지 않은 항목이 있다

- `skills/code-changelog/SKILL.md:27`은 `create_changelog.py` 실행을, `:34`는 `code_changelog_tracker` import를 지시한다. 필요한 두 Python 파일은 저장소에 없고 해당 폴더에는 SKILL.md와 README.txt만 있다.
- `skills/nextjs15-init/references/setup-guide.md:514`의 `todos`는 `/api/todos/route.ts`의 지역 변수다. 별도 `/api/todos/[id]/route.ts` 예제는 `:548`에서 이를 import하거나 선언하지 않고 `:556`부터 참조한다. 그대로 파일을 나누면 연결이 빠진다. `:577`의 PATCH도 요청 스키마 검사 없이 본문을 합친다.
- `nextjs15-init/SKILL.md:23`은 `create-next-app@latest`를 사용하면서 참조의 `setup-guide.md:36`은 Next 15를 제시한다. `flutter-init/SKILL.md:201`은 Freezed 3 규칙을 강제하면서 참조 `setup-guide.md:184`는 Freezed 2.x를 제시한다. 이는 최신 버전이 무엇인지와 별개인 내부 정합성 문제다.

### 4. 디자인 원칙과 실제 콘텐츠의 근거를 분리해야 한다

- 랜딩페이지 공통 참조 `skills/landing-page-guide/references/component-examples.md:73`에는 2,341개 리뷰, `:77`에는 5,000개 팀, `:222`에는 인물형 후기와 성과 수치가 예제로 들어 있다. 실제 제작에서는 확인된 자료로 대체하거나 데모로 표시해야 한다. 구조를 복사했다고 후기와 성과가 검증되는 것은 아니다.
- 같은 예제 `:49`, `:53`, `:102` 등의 CTA는 실행 동작이 연결되지 않은 버튼이다. 화면뿐 아니라 실제 전환 경로 검증이 필요하다.
- 랜딩 v2는 특정 시각 패턴을 금지하지만 일반판과 해시가 같은 참조 코드는 그 패턴을 사용한다. ‘11요소가 전환을 보장’ 같은 문구도 실측 결과가 아니다.
- `skills/frontend-design/SKILL.md:4`는 LICENSE.txt를 참조하지만 해당 파일이 없다. 배포 전에 출처와 참조 파일을 확인해야 한다.

### 5. 환경 의존과 자동 동작을 줄여야 한다

- `/mnt/user-data`, `~/.claude`, `WebFetch`, `AskUserQuestion`, `Task`, `present_files`를 현재 호스트에서도 사용할 수 있다고 가정하는 지침이 있다. 스킬 지침만 옮겨도 이 도구가 제공되는 것은 아니다.
- `skills/web-search/scripts/search.py:16`부터 실행 중인 인터프리터에 ddgs를 자동 설치하며, 실패하면 `:26`에서 `--break-system-packages`로 재시도한다. gemini-logo-remover도 비슷한 설치를 안내한다. 의존성을 별도 가상환경과 설정 단계로 분리할 필요가 있다.
- `skills/chatgpt-web-research/SKILL.md:20`은 `chrome:control-chrome`을 요구하고, `:78`은 3분 간격 대기와 긴 생성 대기를 지시한다. 현재 세션 스킬 목록에는 그 Chrome 스킬이 없다. 로그인된 Chrome을 전제로 하는 이 경로는 범용 클라우드 조사 스킬로 보기 어렵다. 문서의 모델 표기가 현재 계정에서 실제 제공되는지는 확인하지 않았다.
- 현재 PC의 PATH 점검에서는 Claude·Cursor·Flutter 명령을 찾지 못했다. 다른 경로에 설치됐는지까지 조사한 것은 아니며, 해당 CLI를 요구하는 스킬의 실행 준비가 확인됐다는 뜻은 아니다.

### 6. 사용자와의 대화·리뷰·기록이 과도해질 수 있다

- `prompt-enhancer/SKILL.md:96`부터는 구체화 후 항상 확인을 받고 중단한다. `codex/skill.md:32`는 매 명령 뒤 질문을 요구한다. 이미 주어진 승인과 맥락을 재사용하도록 바꾸는 것이 사용자 선호에 맞다.
- 두 AI loop는 매 변경의 교차 검토와 통과할 때까지 반복을 요구한다. 작업 크기와 무관하게 호출이 늘 수 있고 회차·시간 종료 기준이 없다. 독립 검토가 필요한 경우에 현재 리뷰 절차 안에서 선택하는 편이 낫다.
- `workthrough-v2/SKILL.md:45`부터 단순 요약에도 VitePress 초기화·pnpm 설치/빌드를 붙인다. 기록 템플릿과 사이트 게시 기능을 분리해야 한다.

### 7. 요약·분석의 정확성을 입증하는 장치가 부족하다

- `web-to-markdown/SKILL.md:170`의 ‘토큰 30–50% 절감’은 저장소에서 벤치마크로 확인되지 않았다. 두 번 생성한 문서를 ‘원본’과 ‘최적화본’으로 부르는 것만으로 원문 보존이 보장되지 않는다. 실제 추출 원문과 요약을 구분하고 누락 여부를 확인해야 한다.
- `code-prompt-coach/Skill.md:550`은 전체 프로젝트 30일 로그 분석을 기본 종합 예시에 넣으며 `:1010`부터 낮은 평가의 프롬프트 원문을 재인용하게 한다. 같은 문서의 원문 최소화 방침과 조정이 필요하다. 프로젝트·기간을 한정하고 비밀값 제거 후 일부 예시만 남기는 방식이 적합하다.
- 같은 코치 문서 `:782`의 총비용 288.13달러와 `:798`의 136.74달러를 `:822`에서는 총지출의 91%라고 설명하지만 실제 나눗셈은 약 47.5%다. 예제 합계와 청구 일치 주장도 검증되지 않았다. 고정된 과거 가격표, 샘플 로그 추정, 실제 청구를 구분해야 한다. 이 분석은 현재 요금에 대한 판단을 하지 않았다.

## 검증 범위와 다음 단계

파일명·YAML 필드·폴더 수를 읽고, 복사본을 해시 대조하고, 관련 코드와 예제 연결을 정적으로 검토했다. 스킬이 사용자 작업의 결과를 개선하는지에 대한 실행 비교는 하지 않았다. 기존 CI의 16개 테스트는 현재 개인 패키지의 영상 런타임과 패키징 등을 검증하며, 위 22개 스킬의 기능 테스트가 아니다.

다음 개조에서는 먼저 원본을 하나로 정하고 필요한 항목만 `.agents/skills/`로 옮긴다. 해당 동작을 검증한 뒤 선택 목록과 버전을 갱신해 기존 비공개 플러그인에 별도로 배포한다. 이번 보고서 저장만으로 설치 또는 플러그인 배포를 진행하지 않는다.
