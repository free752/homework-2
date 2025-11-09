# homework-2
# Backend Framework Practice (FastAPI)

간단한 Items/Users API로 실습 요구사항을 충족하는 FastAPI 프로젝트입니다.

## 1) Tech Stack
- Python 3.10+, FastAPI, Uvicorn

## 2) 요구사항 매핑
- HTTP 메소드별 API: POST/GET/PUT/DELETE 각 2개 (총 8개)
- 미들웨어: 요청 로깅(RequestLogMiddleware)
- 상태코드 다양성: 2xx(200/201/204), 4xx(400/404), 5xx(500/503)
- 표준 응답 포맷  
  - 성공: `{ "status":"success", "data":{...} }`  
  - 실패: `{ "status":"error", "message":"...", "detail":{...} }`

## 3) 실행 방법
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
