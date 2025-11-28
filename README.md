# Backend Framework Practice Assignment - FastAPI

전북대학교 백엔드 프레임워크 실습 과제용 FastAPI 프로젝트입니다.  
FastAPI를 사용하여 POST / GET / PUT / DELETE 메소드별 2개씩, 총 8개의 API를 구현하고,  
요청 로깅 미들웨어와 다양한 HTTP 응답 코드, 표준화된 응답 포맷을 적용했습니다.

---

## 1. Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn

---

## 2. 프로젝트 구조

- `main.py`  
  - FastAPI 앱 진입점
  - 미들웨어 정의 (요청 로깅)
  - User / Item 관련 API 엔드포인트 구현
  - 공통 응답 포맷 함수 (`success`, `error`)
  - 인메모리 DB (`users_db`, `items_db`)

---

## 3. 실행 방법 (How to Run)

1. 패키지 설치

```bash
pip install fastapi uvicorn

