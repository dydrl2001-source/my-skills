# 앱·웹 복제 도구

세 도구의 스킬 원본, 필수 참조 파일, MIT 라이선스와 출처를 이 저장소의 `.agents/skills/`에 보관합니다. 앱이나 웹사이트를 만드는 작업은 별도의 프로젝트 폴더에서 진행합니다.

## 도구 선택

| 도구 | 입력과 용도 | 실행 준비 |
| --- | --- | --- |
| [clone-app](../.agents/skills/clone-app/SKILL.md) | 앱 스크린샷을 바탕으로 모바일 화면, 화면 이동, 기기 내 저장 동작 구현 | 전체 Expo 템플릿과 브라우저 도구 |
| [clone-website](../.agents/skills/clone-website/SKILL.md) | 웹 주소를 관찰해 화면과 상호작용을 수정 가능한 코드로 재구현 | 정상 빌드되는 웹 프로젝트와 브라우저 도구 |
| [true-web-clone](../.agents/skills/true-web-clone/SKILL.md) | 공개 HTML·CSS·JS·이미지·폰트·애니메이션을 활용해 원본 동작에 가까운 로컬 복제 | 별도 작업 폴더, 브라우저/Playwright, 로컬 HTTP 서버 |

앱 화면을 바탕으로 만들 때는 `clone-app`, 이후 코드를 계속 수정하며 개발할 웹사이트에는 `clone-website`, 원래 웹사이트의 공개 리소스와 복잡한 동작을 보존하려면 `true-web-clone`을 사용합니다. 서버의 비공개 코드나 계정 데이터는 이 스킬에 포함되지 않습니다.

## GitHub에 포함된 구성

- `.agents/skills/clone-app/`: 복제 워크플로와 전체 Expo 프로젝트 준비 안내.
- `.agents/skills/clone-website/`: 복제 워크플로, 화면 관찰·Framer·모션 참조, 웹 프로젝트 준비 안내.
- `.agents/skills/true-web-clone/`: 복제 워크플로, 3D·복잡한 모션 참조, 문제 해결 문서, 표시용 메타데이터.
- `scripts/install_cloners.sh`: 세 스킬을 로컬 Codex의 스킬 경로에 연결하는 설치 스크립트.

GitHub 원본 추가와 플러그인 배포는 별도입니다. 이 저장소의 `plugin.json`과 패키지 빌더에는 세 스킬이 포함되지만, 계정용 플러그인은 업데이트 도구로 배포해야 반영됩니다.

## 로컬 Codex 연결

macOS 또는 Linux에서 이 저장소를 내려받은 폴더를 유지한 채 실행합니다. 스크립트는 스킬을 연결하며, 앱 의존성이나 브라우저는 각 작업 프로젝트에서 준비합니다.

이미 이 저장소가 있다면 해당 폴더에서 실행합니다.

```sh
bash scripts/install_cloners.sh
```

새로 받는 경우에는 다음 명령을 사용합니다. `my-skills` 폴더가 없는 위치에서 실행합니다.

```sh
git clone https://github.com/dydrl2001-source/my-skills.git my-skills
bash my-skills/scripts/install_cloners.sh
```

기본 설치 경로는 `~/.agents/skills`입니다. 다른 경로는 `CODEX_CLONER_SKILLS_DIR`로 지정합니다. 같은 연결에 대한 재실행은 그대로 유지하고, 다른 파일이나 연결이 이미 있으면 덮어쓰지 않고 중단합니다. 연결된 스킬이 원본을 참조하므로 저장소 폴더는 삭제하거나 옮기지 않습니다.

Codex 클라우드의 다른 프로젝트에서 사용할 때는 필요한 스킬 디렉터리 전체를 그 프로젝트의 `.agents/skills/`에 복사합니다. `SKILL.md`와 함께 `references/`, `agents/`, `LICENSE`, `PROVENANCE.md`도 유지합니다.

## 실제 프로젝트 시작

### 앱 스크린샷에서 시작

[Expo 프로젝트 준비 안내](../.agents/skills/clone-app/references/setup.md)에 따라 전체 템플릿을 별도 폴더에 준비합니다. 스크린샷을 그 프로젝트의 `docs/screenshots/`에 넣고 해당 프로젝트를 열어 요청합니다.

> clone-app으로 이 스크린샷들의 화면과 화면 이동을 구현해줘. 추가·수정·삭제와 기기 내 저장도 작동하게 해줘.

`my-skills` 루트에서 `npm run web`을 실행하지 않습니다. 앱의 스키마, 저장 도우미, Expo 설정과 검증 스크립트가 있는 작업 프로젝트에서 실행합니다.

### 웹 주소에서 시작

[웹 프로젝트 준비 안내](../.agents/skills/clone-website/references/setup.md)에 따라 기존 웹 프로젝트를 열거나 고정 버전의 Next.js 템플릿을 준비합니다.

> clone-website로 이 주소의 화면과 주요 동작을 재현해줘. 데스크톱과 모바일 화면을 비교하면서 수정 가능한 코드로 만들어줘.

공개 리소스와 원래 애니메이션을 활용하는 복제는 별도 작업 폴더에서 요청합니다.

> true-web-clone으로 이 주소를 로컬에서 재현해줘. 공개 리소스와 애니메이션을 보존하고 실제 브라우저에서 확인해줘.

## 고정한 원본 버전

| 원본 저장소 | 커밋 | 라이선스 |
| --- | --- | --- |
| [Birkenpapier/ai-app-cloner](https://github.com/Birkenpapier/ai-app-cloner) | `3a6d932d519773612cf79289c3102082bb76bb41` | MIT |
| [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | `14085f8ba2a15b5e7f509c78dfc4017dbbfced6d` | MIT |
| [SkyNotSilent/true-web-clone](https://github.com/SkyNotSilent/true-web-clone) | `be3c136fd3988e38b72efc3480b382aca0f584c6` | MIT |

각 스킬의 `PROVENANCE.md`에 가져온 경로와 이 저장소에 맞춘 변경을 기록합니다. 원본 업데이트를 가져올 때는 커밋을 명시적으로 변경하고 필수 참조 파일과 프로젝트 전제를 다시 확인합니다.
