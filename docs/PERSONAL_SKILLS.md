# 내 작업 도구

같은 스킬 원본을 Codex 저장소와 계정용 플러그인에 배포하기 위한 개인 패키지입니다. 원본 저장소는 https://github.com/dydrl2001-source/my-skills 이며, 저장소 변경과 계정용 플러그인 배포는 별도 단계입니다.

| 스킬 | 용도 |
| --- | --- |
| diagram-design | HTML/SVG 기반 다이어그램 작성 |
| engineering-upgrades | 개발 용어, 모듈 인터페이스, 요구사항과 표준 리뷰 |
| video-reader | 영상의 시간별 프레임, 모아보기, 로컬 음성 전사 |

## Codex 클라우드

이 저장소를 GitHub 연결에 허용하고 Codex 환경의 저장소로 선택합니다. `.agents/skills/`와 `AGENTS.md`가 함께 체크아웃됩니다. 다른 프로젝트에서 사용하려면 그 프로젝트에도 `.agents/skills/`를 복사하거나 환경 설정 단계에서 이 저장소를 안전하게 가져와야 합니다. 스킬 전용 저장소를 만들었다고 모든 프로젝트에 자동 적용되지는 않습니다.

영상 분석이 필요하면 환경의 설정 스크립트에 다음을 넣습니다. Python 3.10–3.13과 `venv`가 필요하며, 3.12를 권장합니다.

```sh
python3 .agents/skills/video-reader/scripts/setup.py
python3 .agents/skills/video-reader/scripts/run.py doctor
```

설정 시 PyPI에, 영상 수집 시 해당 영상 사이트에 접근할 수 있어야 합니다. 음성 모델은 처음 사용할 때 Hugging Face에서 내려받습니다. 실행 단계의 네트워크를 끄는 환경에서는 설정 단계에서 모델을 미리 준비하고 로컬 영상을 사용하세요. 로그인이나 플랫폼 제한으로 Instagram 링크가 실패할 수 있습니다.

## 계정용 플러그인

원본 스킬은 `.agents/skills/` 한 곳에서 관리합니다. 아래 명령은 플러그인 규격에 맞게 ZIP 안에서 `skills/`로 배치합니다.

```sh
python3 scripts/build_plugin.py --output ../personal-agent-skills-0.1.0.zip
```

생성한 플러그인을 설치한 계정의 지원되는 ChatGPT/Codex 화면에서 사용할 수 있습니다. 실제 도구 제공 여부는 실행 환경에 따릅니다. 특히 영상 스킬은 Python·셸·이미지 확인 도구가 필요하고, 설치만으로 클라우드 영상 서버가 생기지 않습니다. 모바일은 접속 화면일 수 있지만 실행 환경의 도구가 필요합니다. 플러그인에 API 키나 로그인 세션은 포함하지 않습니다.

Windows의 기존 `run.ps1`과 `setup.ps1`도 사용할 수 있습니다. Linux/macOS는 `scripts/run.py`와 `scripts/setup.py`를 사용합니다. 런타임은 Windows에서 `%LOCALAPPDATA%/CodexVideoReader`, Unix에서 `${XDG_CACHE_HOME:-~/.cache}/CodexVideoReader`에 저장되고 `VIDEO_READER_HOME`으로 변경할 수 있습니다.

## 확인

영상 런타임의 Python으로 `python -m unittest discover -s tests -v`를 실행합니다. 테스트는 자체 생성 색상 영상을 사용합니다. GitHub Actions 설정은 Windows와 Ubuntu에서 같은 테스트를 실행하도록 준비했습니다. 실제 CI 결과를 확인하기 전에는 Linux 실행이 검증됐다고 간주하지 마세요.

## 출처

`diagram-design`은 [Cathryn Lavery의 프로젝트](https://github.com/cathrynlavery/diagram-design)를 포함합니다(MIT, 해당 폴더의 LICENSE). `engineering-upgrades`는 [Matt Pocock의 skills](https://github.com/mattpocock/skills)의 일부 원칙을 통합했습니다(MIT 및 provenance 참조). `video-reader`는 이 작업에서 작성했으며 의존 패키지는 각자의 라이선스를 따릅니다.

공식 안내: [스킬](https://learn.chatgpt.com/docs/build-skills), [플러그인](https://learn.chatgpt.com/docs/plugins).

