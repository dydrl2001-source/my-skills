# 내 작업 도구

같은 스킬 원본을 Codex 저장소와 계정용 플러그인에 배포하기 위한 개인 패키지입니다. 원본 저장소는 https://github.com/dydrl2001-source/my-skills 이며, 저장소 변경과 계정용 플러그인 배포는 별도 단계입니다.

| 스킬 | 용도 |
| --- | --- |
| web-design | 브랜드·사용자 흐름·웹 화면·실제 CTA를 함께 설계 |
| card-news | 한글 카드뉴스 PNG 생성, 배경·번호·크기 선택 |
| diagram-design | HTML/SVG 기반 다이어그램 작성 |
| engineering-upgrades | 개발 용어, 모듈 인터페이스, 요구사항과 표준 리뷰 |
| video-reader | 영상의 시간별 프레임, 모아보기, 로컬 음성 전사 |
| emil-design-eng | Emil Kowalski의 UI 디테일, 컴포넌트, 애니메이션 구현·리뷰 기준 |

웹디자인 스킬과 Figma·브라우저 도구의 역할, 실제 요청 예시는 [웹디자인 사용법](WEB_DESIGN_SETUP.md)을 참고하세요.

## Codex 클라우드

이 저장소를 GitHub 연결에 허용하고 Codex 환경의 저장소로 선택합니다. `.agents/skills/`와 `AGENTS.md`가 함께 체크아웃됩니다. 다른 프로젝트에서 사용하려면 그 프로젝트에도 `.agents/skills/`를 복사하거나 환경 설정 단계에서 이 저장소를 안전하게 가져와야 합니다. 스킬 전용 저장소를 만들었다고 모든 프로젝트에 자동 적용되지는 않습니다.

영상 분석이 필요하면 환경의 설정 스크립트에 다음을 넣습니다. Python 3.11–3.13과 `venv`가 필요하며, 3.12를 권장합니다. Pillow 13의 최소 Python 요구사항에 맞춘 범위입니다.

```sh
python3 .agents/skills/video-reader/scripts/setup.py
python3 .agents/skills/video-reader/scripts/run.py doctor
```

설정 시 PyPI에, 영상 수집 시 해당 영상 사이트에 접근할 수 있어야 합니다. 음성 모델은 처음 사용할 때 Hugging Face에서 내려받습니다. 실행 단계의 네트워크를 끄는 환경에서는 설정 단계에서 모델을 미리 준비하고 로컬 영상을 사용하세요. 로그인이나 플랫폼 제한으로 Instagram 링크가 실패할 수 있습니다.

## 계정용 플러그인

원본 스킬은 `.agents/skills/` 한 곳에서 관리합니다. 아래 명령은 플러그인 규격에 맞게 ZIP 안에서 `skills/`로 배치합니다.

```sh
python3 scripts/build_plugin.py --output ../personal-agent-skills-0.3.0.zip
```

생성한 플러그인을 설치한 계정의 지원되는 ChatGPT/Codex 화면에서 사용할 수 있습니다. 실제 도구 제공 여부는 실행 환경에 따릅니다. 특히 영상 스킬은 Python·셸·이미지 확인 도구가 필요하고, 설치만으로 클라우드 영상 서버가 생기지 않습니다. 모바일은 접속 화면일 수 있지만 실행 환경의 도구가 필요합니다. 플러그인에 API 키나 로그인 세션은 포함하지 않습니다.

Windows의 기존 `run.ps1`과 `setup.ps1`도 사용할 수 있습니다. Linux/macOS는 `scripts/run.py`와 `scripts/setup.py`를 사용합니다. 런타임은 Windows에서 `%LOCALAPPDATA%/CodexVideoReader`, Unix에서 `${XDG_CACHE_HOME:-~/.cache}/CodexVideoReader`에 저장되고 `VIDEO_READER_HOME`으로 변경할 수 있습니다.

## 확인

카드뉴스는 `.agents/skills/card-news/SKILL.md`의 JSON 입력 규격을 사용합니다. Pillow가 있는 Python 환경에서 실행하며, 이미 설정한 영상 런타임의 Python도 재사용할 수 있습니다. 별도 환경이 필요하면 Python 가상환경을 만든 뒤 `.agents/skills/card-news/requirements.txt`를 설치합니다. 생성한 PNG를 실제로 열어 확인하고, 출력 폴더는 새 경로를 사용합니다. 나눔고딕 글꼴과 OFL 라이선스가 함께 포함됩니다.

영상 런타임의 Python으로 `python -m unittest discover -s tests -v`를 실행합니다. 테스트는 자체 생성 색상 영상을 사용합니다. GitHub Actions 설정은 Windows와 Ubuntu에서 같은 테스트를 실행하도록 준비했습니다. 실제 CI 결과를 확인하기 전에는 Linux 실행이 검증됐다고 간주하지 마세요.

## 출처

`diagram-design`은 [Cathryn Lavery의 프로젝트](https://github.com/cathrynlavery/diagram-design)를 포함합니다(MIT, 해당 폴더의 LICENSE). `engineering-upgrades`는 [Matt Pocock의 skills](https://github.com/mattpocock/skills)의 일부 원칙을 통합했습니다(MIT 및 provenance 참조). `video-reader`는 이 작업에서 작성했으며 의존 패키지는 각자의 라이선스를 따릅니다.

`web-design`과 `card-news`는 기존 스킬 분석을 바탕으로 새로 정리한 개인 통합본입니다. 선택 이유와 보류 항목은 [통합 안내](INTEGRATION_0.2.0.md)를 참고하세요. 새 카드 렌더러는 Python/Pillow로 작성했고, 포함한 [Nanum Gothic](https://github.com/google/fonts/tree/main/ofl/nanumgothic)은 원본 OFL.txt와 함께 배포합니다.

공식 안내: [스킬](https://learn.chatgpt.com/docs/build-skills), [플러그인](https://learn.chatgpt.com/docs/plugins).

`emil-design-eng`는 [Emil Kowalski의 skills](https://github.com/emilkowalski/skills)에서 가져온 MIT 라이선스 원본입니다. 고정한 커밋과 파일은 해당 스킬의 PROVENANCE.md에 기록했습니다.

