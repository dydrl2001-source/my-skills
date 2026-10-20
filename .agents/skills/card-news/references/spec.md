# 로컬 렌더러 JSON 사양

Python 3.11+(3.12 권장)와 Pillow가 필요하다(Pillow 13은 Python 3.11 이상 지원). 실행은 로컬 파일만 읽고 PNG와 manifest를 쓴다. 동봉 폰트는 한국어·라틴 문자용이며 임의 폰트의 문자 지원은 별도 시각 확인이 필요하다.

```json
{
  "width": 600,
  "height": 600,
  "background_color": "#F5F1E8",
  "text_color": "auto",
  "numbering": true,
  "cards": [
    {"title": "함께 걷는 하루", "body": "서로의 이야기를 듣고 마음을 나눕니다."},
    {"title": "일정 예시", "body": "2026년 11월 7일 오후 2시\n가상의 행사 안내입니다.", "background_color": "#183A37"}
  ]
}
```

| 필드 | 기본값 / 허용 범위 |
|---|---|
| `cards` | 필수, 객체 1~24개. 각 카드는 `title` 또는 `body`에 비어 있지 않은 문자열 필요 |
| `width`, `height` | 각각 600 / 정수 256~2048. 전체 출력 면적 최대 4,800만 픽셀 |
| `margin` | 48 / 정수 12~짧은 변의 1/3 |
| `background_color` | `#F5F1E8` / 6자리 HEX, 대소문자 동일 취급 |
| `text_color` | `auto` / `auto` 또는 6자리 HEX |
| `font_size` | 44 / 정수 12~120. 제목의 시작 크기; 본문은 약 65% |
| `min_font_size` | 16 / 정수 12~`font_size`. 제목과 본문의 최소 크기 |
| `numbering` | false / JSON boolean. 오른쪽 아래 `1 / N` |
| `overlay_opacity` | 0.55 / 0~1. 배경 이미지 위 검정 덮개의 불투명도 |

카드별 필드는 `title`, `body`, `background_color`, `text_color`, `background_image`뿐이다. 색상은 전역값을 재정의할 수 있다. `background_image`는 존재하는 로컬 이미지 경로로, 상대경로는 **사양 파일의 폴더**를 기준으로 해석한다. 이미지의 EXIF 회전을 적용한 뒤 중앙 크롭으로 채운다. 투명 영역은 배경색과 합성한다. 누락·손상된 이미지는 실패하며 배경색으로 대체하지 않는다.

기본 자동 글자색은 밝은 단색에서 진한 색, 어두운 단색에서 흰색이다. 이미지에는 흰 글자와 기본 검정 덮개를 사용한다. 덮개를 약하게 하거나 명시적 글자색을 지정하면 해당 사진에서 대비를 직접 확인한다.

사양 최대 1 MiB, 카드당 제목+본문 최대 12,000자, 전체 최대 60,000자. 배경 파일은 각각 20 MB·1,600만 픽셀 이하, 폰트는 20 MB 이하이다. 줄바꿈은 보존하며 탭 등 다른 제어문자는 허용하지 않는다. 알 수 없는 필드는 입력 실수로 보고 거절한다. 기존 출력 폴더를 삭제하거나 덮지 않는다.

성공 시 종료 코드 0, stdout JSON `{"status":"ok","manifest":"절대경로","count":2}`, stderr는 비어 있다. `--help`는 일반 도움말이다. 오류 시 종료 코드 1, stdout은 비어 있고 stderr에 `{"status":"error","code":"...","message":"..."}` 한 줄을 기록한다. 주요 코드는 `invalid_spec`, `text_overflow`, `background_error`, `font_error`, `output_exists`, `output_error`, `dependency_missing`, `arguments_error`, `io_error`이다.

`manifest.json`에는 `status`, `schema_version`, 폰트 절대경로·SHA256·family·style, 카드별 PNG 절대경로·width·height·최종 색상·배경·덮개·번호가 있다. `text`의 각 제목/본문 블록은 실제 사용한 `font_size`와 줄별 원문·`bounds`를 포함한다. 경계는 Pillow 폰트 측정값으로 `[left, top, right, bottom]`, 오른쪽·아래는 제외한다. 임의의 긴 단어는 문자 단위로 나누고 모든 문자를 유지한다. 최소 크기에서도 들어가지 않으면 결과를 만들지 않고 `text_overflow`를 반환한다.
