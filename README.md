# 자전거 용품 관리 (PyQt6 + SQLite)

간단한 PyQt6 GUI 앱으로 자전거용품을 SQLite(`MyProduct` 테이블)로 관리합니다.

사용법

1. 의존성 설치

```bash
pip install -r requirements.txt
```

2. 실행

```bash
python bike_products.py
```

기능

- 입력: 이름, 가격 입력 후 `입력` 버튼으로 추가 (id 자동 생성)
- 수정: 테이블에서 항목 선택 후 값 변경 후 `수정`
- 삭제: 테이블에서 항목 선택 후 `삭제`
- 검색: 이름으로 부분 검색
- 하단 리스트: `QTableWidget`으로 전체/검색 결과 표시
