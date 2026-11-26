# 로컬 실행과 MCP 연결

## 맥미니 설치

터미널에 `codex`, `git`, `node`(20 이상), `npm`, `python3`(3.10 이상)가 있으면 아래 명령으로 두 스킬과 MCP를 설치한다.

```sh
hangul_repo="$HOME/.local/share/codex-hangul/my-skills"
if [ ! -e "$hangul_repo" ]; then
  git clone --depth 1 https://github.com/dydrl2001-source/my-skills.git "$hangul_repo"
fi
bash "$hangul_repo/scripts/install_hangul.sh"
```

이 경로의 저장소는 스킬이 참조하므로 설치 후에도 보관한다. 설치가 끝나면 로컬 Codex에서 각 MCP의 도구를 확인하고, 샘플 HWPX를 만들어 다시 읽어 본다.

## 직접 등록

Node.js 18 이상과 Git이 필요하다. `hwpkit` 소스는 스킬 저장소 밖의 원하는 작업 폴더에 한 번만 내려받는다.

```sh
git clone https://github.com/yuyu04/hwpkit.git
git -C hwpkit checkout --detach bd55ee61010fc98c98ec38e6dced26fb3144661e
```

이 버전에는 실행 의존성과 WebAssembly 엔진이 포함되어 있다. `hwpkit`을 내려받은 위치의 절대 경로를 사용해 로컬 Codex에 연결한다.

```sh
codex mcp add hwpkit -- node "/absolute/path/to/hwpkit/scripts/hwp-mcp.mjs"
codex mcp list
```

`hwpkit` MCP는 읽기·새 문서 생성·미리보기를 제공한다. 기존 HWPX의 텍스트 치환이나 템플릿 채우기를 MCP로 실행하려면 `hwp-mcp`를 연결할 수 있다. 이 서버에는 Node.js 20 이상이 필요하다.

```sh
codex mcp add hwp-mcp -- npx -y hwp-mcp@0.3.0
codex mcp list
```

두 명령은 로컬 Codex 설정에 등록한다. 사용자의 GitHub에 있는 [`hwp-mcp-`](https://github.com/dydrl2001-source/hwp-mcp-)는 해당 MCP의 소스 저장소이며 위 명령은 npm 배포본을 사용한다.
