---
name: hwpkit
description: 한글 HWP/HWPX 문서에서 본문과 표를 읽고, Markdown 원고로 새 .hwp/.hwpx를 만들거나 페이지를 미리 본다. 한글 파일 요약, 강의안·보고서 내보내기, 문서 모양 확인에 사용한다. 기존 HWPX 양식 편집에는 hwpx-editing을 사용한다.
---

# HWPKit

연결된 `hwpkit` MCP가 있으면 `hwp_read`, `hwp_write`, `hwp_preview`를 사용한다. 없으면 [로컬 실행 및 MCP 연결](references/setup.md)에 따라 고정 버전의 Node.js 도구를 사용한다.

| 작업 | CLI | 결과 |
| --- | --- | --- |
| 본문과 표 읽기 | `node <hwpkit>/scripts/hwp-read.mjs <문서>` | 읽기 순서로 추출한 텍스트 |
| 새 문서 만들기 | `node <hwpkit>/scripts/hwp-write.mjs <원고.md> <결과.hwp>` | 출력 확장자에 맞는 `.hwp` 또는 `.hwpx` |
| 페이지 미리 보기 | `node <hwpkit>/scripts/hwp-preview.mjs <문서> <출력폴더> --pages 1` | SVG. `--png`를 추가하면 Chrome 계열 브라우저로 PNG도 생성 |

새 문서를 만들 때 Markdown 제목, 문단, 목록, 표를 사용한다. 읽기 도구에서 복잡한 표와 다단 배치는 텍스트로 펼쳐진다. 생성 후 파일을 다시 읽어 본문과 표가 들어갔는지 확인하고, 서식이 중요한 부분은 미리보기에서 점검한다. `.hwpx` 생성 시 문단 안의 부분 강조는 원본 엔진에서 보존되지 않을 수 있다. 제출 양식이 정한 확장자를 사용하고 기존 파일을 편집할 때는 원본을 보존한다.
