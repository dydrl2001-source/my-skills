---
name: card-news
description: Use when the user requests Korean card news, social carousel images, or a series of text cards as PNGs. Applies to 카드뉴스 제작 and multi-card social posts, rather than general slide decks or website layouts.
---

# 카드뉴스

사용자의 메시지를 읽기 쉬운 여러 장의 카드로 정리하고 PNG로 만든다. 카드 수, 비율, 문구, 브랜드 색상이 주어졌다면 그대로 따른다. 정보가 충분하면 합리적인 기본값으로 진행한다.

## 제작

- 사용자가 제공한 사실과 출처를 바탕으로 카드별 제목·본문을 작성한다. 날짜·가격·인용·통계를 지어내지 않는다. 가상 행사와 예시 수치는 결과에서도 예시로 표시한다.
- 한 카드의 핵심 메시지를 먼저 정하고 표지 → 설명 → 필요한 행동의 흐름으로 배치한다. 구성 판단이 필요할 때 [시각 구성](references/composition.md)을 읽는다.
- 사진·일러스트는 선택 자산이다. 사용자 이미지나 사용 가능한 이미지 도구로 준비하고 권리·출처를 확인한다. 이미지 생성 도구와 특정 Midjourney 버전은 필수 조건이 아니다.
- [JSON 사양](references/spec.md)에 맞춰 UTF-8 파일을 저장한다. 셸과 Python 3.11+(3.12 권장), Pillow가 필요하다. Pillow가 없다면 실행 환경을 설명하고 명시적인 설치 단계로 해결한다. 렌더러는 네트워크 호출이나 자동 설치, 문구 생성 API를 사용하지 않는다.

```text
python <skill-directory>/scripts/render_cards.py spec.json --output NEW_DIRECTORY
python <skill-directory>/scripts/render_cards.py spec.json --output NEW_DIRECTORY --font /path/to/font.ttf
```

출력 부모 폴더는 있어야 하며 출력 폴더 자체는 새 경로여야 한다. 기본값은 600×600, 동봉 나눔고딕이다. 공백 없는 한국어·영어도 문자 단위로 줄바꿈하며 최소 크기까지 맞춘다. 맞지 않으면 문구를 줄이거나 카드를 나누어 다시 실행한다. 내용을 조용히 자르지 않는다.

## 확인과 전달

이미지 확인 도구로 PNG를 직접 열어 문구, 줄바꿈, 대비, 사진 크롭, 번호를 확인한다. 특히 혼합 언어·이모지·사용자 폰트의 글리프를 살핀다. 동봉 폰트가 모든 문자나 컬러 이모지를 지원하지는 않는다. 실행 도구가 없다면 사양과 문구를 제공하고 PNG 생성·검수를 했다고 말하지 않는다.

최종 답변에는 이미지 미리보기와 결과 경로를 제시한다. `manifest.json`의 성공 상태, 폰트, 카드별 크기와 측정된 줄 경계를 확인하고, 실패했다면 JSON 오류와 해결할 입력을 설명한다. 제작·검수 권한이 게시나 외부 전송 권한을 뜻하지 않는다.

동봉 폰트의 [라이선스 전문](assets/fonts/OFL.txt)과 [구현 출처](references/provenance.md)를 함께 보존한다.
