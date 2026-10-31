# 디자인 스킬 3종 검증 및 반영

확인일: 2026-10-31 (한국 시간)

## 이미지 주장과 실제 출처

| 항목 | 확인 결과 | 기존 설치본과 비교 | 반영 |
| --- | --- | --- | --- |
| apple-design | Emil Kowalski의 WWDC 기반 웹 지침. Apple 공식 배포 스킬이 아님. | 로컬 및 personal-agent-skills 0.4.0 캐시에 존재하지만 정본 배포 목록에는 없었음. | 정본에 MIT 원문·라이선스·고정 커밋 출처 추가. 인사만 하고 중단하는 지침을 작업 우선으로 수정. blur 성능 지침 모순 수정. |
| open-design | nexu-io의 별도 앱·워크스페이스. 공식 카탈로그는 151개 패키지를 명시. Claude Code 외 Codex 등도 지원한다고 안내. | 현재 스킬 목록에 open-design은 없음. web-design 및 브랜드 조사 기능과 일부 중복. 앱 설치 여부는 검사하지 않음. | web-design에 선택형 출처 참조 추가. 앱·MCP를 설치하거나 151개 시스템을 복제하지 않음. |
| Web Design Guidelines | Vercel 공식 스킬은 최신 command.md를 읽고 코드 검토하는 절차. 독립 자동 스캐너나 접근성 인증 도구가 아님. | 로컬 및 개인 플러그인 캐시에 존재하지만 정본 배포 목록에는 없었음. | 최신 규칙 조회·한국어 코드 위치 보고·검증 범위 구분을 위한 자체 adapter 추가. upstream 라이선스가 확인되지 않아 원문 재배포 대신 링크 사용. |

이미지의 ★4.8만·★10만+·★3.2만은 평가 점수가 아닌 저장소 스타 수 표기이며 시점에 따라 변합니다. 이번 조사에서 각 이미지의 정확한 스타 수와 촬영 시점을 대조하지 않았습니다. 저장소 전체의 스타를 개별 스킬의 품질·성능 보증으로 사용할 수 없습니다.

## 실제 사용 흐름

1. “Linear 스타일로 만들어줘”: web-design에서 사용자 브랜드를 우선하고 OpenDesign의 실제 선택 패키지와 토큰을 조회. 브랜드 공식 자료인지 커뮤니티 재구성인지 구분.
2. “Apple처럼 움직이는 drawer”: apple-design에서 현재 표시 위치, 재조작, 속도 인계, reduced-motion을 적용하고 대상 환경에서 확인.
3. “배포 전 UI 검사”: web-design-guidelines가 최신 Vercel 규칙으로 코드를 검토하고 파일·라인별 문제를 보고. 배포나 접근성 인증은 별개.

## 검증

- Windows Python 3.12: packaging unittest 3개 통과.
- skill-creator quick_validate: apple-design, web-design-guidelines, web-design 통과.
- 독립 검토: 기존 지침의 출처·전문 절차 공백 확인 후 새 참조의 연결과 시나리오 적용 확인. blur 애니메이션 모순 수정.
- ZIP 생성 및 빌더의 archive integrity 검사 통과: 8개 스킬, 332개 파일.
- 실제 웹 앱 구현·브라우저·키보드·스크린리더 검사는 이번 변경의 대상이 아님.

## 출처

- https://github.com/emilkowalski/skills/blob/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/apple-design/SKILL.md
- https://github.com/nexu-io/open-design
- https://github.com/nexu-io/open-design/blob/main/design-systems/README.md
- https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines/SKILL.md
- https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md

## 배포 구분

정본 버전은 0.5.0으로 설정하고 ZIP을 생성했습니다. 계정 플러그인이나 로컬 설치 사본을 업데이트한 것은 아닙니다. 기존 설치 파일과 레거시 skills/·.claude/는 보존했습니다.

