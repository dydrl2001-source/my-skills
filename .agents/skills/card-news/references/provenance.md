# 출처와 라이선스

새 `scripts/render_cards.py`는 이 저장소의 통합 작업에서 새로 작성했다. 기존 컬렉션의 카드뉴스 기능을 검토해 요구사항을 정했으며, 라이선스가 확인되지 않은 기존 렌더러나 Cafe24 폰트 파일을 복사하지 않았다. 기존 `skills/`, `.claude/` 자료는 별도 보존한다. 시각 구성 문서는 이 스킬을 위한 자체 작성 지침이다.

폰트는 Google Fonts의 공식 저장소에서 2026-10-21에 받은 **수정하지 않은** 파일이다. 배포 시 폰트와 라이선스를 함께 유지한다.

- [NanumGothic-Regular.ttf 원본](https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf): `assets/fonts/NanumGothic-Regular.ttf`, 2,054,744 bytes, SHA256 `76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31`.
- [OFL.txt 원본](https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/OFL.txt): `assets/fonts/OFL.txt`, SHA256 `eeacf16032901d0ed0456876ec77b8f0fda6b3fecec7d972f8543eb602e6c30f`. NHN Corporation 저작권과 SIL Open Font License 1.1 전문 및 Reserved Font Names를 보존한다.
- [Pillow ImageFont 공식 문서](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html): TrueType 로딩과 텍스트 경계 측정 API 근거. Pillow는 별도 설치 의존성이며 라이브러리 코드를 이 스킬에 복제하지 않는다.

원격 `main`은 바뀔 수 있으므로 위 체크섬이 동봉 파일의 정확한 식별값이다. 원격 최신 파일을 렌더링 도중 받지 않는다.
