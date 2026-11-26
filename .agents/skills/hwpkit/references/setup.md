# 로컬 실행과 MCP 연결

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
