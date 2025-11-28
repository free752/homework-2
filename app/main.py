from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

app = FastAPI()

# -------------------------
# 공통 응답 포맷
# -------------------------
def success(data=None):
    return {"status": "success", "data": data}


def error(message: str, detail=None):
    return {"status": "error", "message": message, "detail": detail}


# -------------------------
# 미들웨어: 요청 로그
# -------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()  # ✅ 요청이 들어온 시점 기록

    response = await call_next(request)

    duration_ms = (time.time() - start) * 1000  # ✅ 처리 시간(ms) 계산
    print(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)")

    return response


# -------------------------
# 데이터 클래스
# -------------------------
class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class ItemCreate(BaseModel):
    name: str
    price: float
    owner_id: int | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


# -------------------------
# 임시 DB (메모리)
# -------------------------
users_db: dict[int, dict] = {}
items_db: dict[int, dict] = {}
next_user_id = 1
next_item_id = 1


# =========================================================
# POST (2개)
# =========================================================

# POST 1: 유저 생성 (201, 400, 500)
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    global next_user_id

    # 400 예시: 이메일 형식이 이상한 경우
    if "@" not in payload.email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error("invalid email format", {"email": payload.email}),
        )

    try:
        user_id = next_user_id
        next_user_id += 1
        users_db[user_id] = {
            "id": user_id,
            "name": payload.name,
            "email": payload.email,
        }
        return success(users_db[user_id])
    except Exception as e:
        # 500 예시
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error("internal server error", {"reason": str(e)}),
        )


# POST 2: 아이템 생성 (201, 400, 503)
@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    global next_item_id

    # 400 예시: 가격이 음수
    if payload.price < 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error("price must be >= 0", {"price": payload.price}),
        )

    # 503 예시: 특정 이름으로 생성 시 강제로 서비스 중단 시나리오
    if payload.name.lower() == "maintenance":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error("item service is under maintenance"),
        )

    item_id = next_item_id
    next_item_id += 1
    items_db[item_id] = {
        "id": item_id,
        "name": payload.name,
        "price": payload.price,
        "owner_id": payload.owner_id,
    }
    return success(items_db[item_id])


# =========================================================
# GET (2개)
# =========================================================

# GET 1: 유저 상세 조회 (200, 404)
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error("user not found", {"user_id": user_id}),
        )
    return success(user)


# GET 2: 아이템 목록 조회 (200)
@app.get("/items")
def list_items():
    return success(list(items_db.values()))


# =========================================================
# PUT (2개)
# =========================================================

# PUT 1: 유저 정보 수정 (200, 400, 404)
@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    user = users_db.get(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error("user not found", {"user_id": user_id}),
        )

    if payload.name is None and payload.email is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error("nothing to update"),
        )

    if payload.name is not None:
        user["name"] = payload.name
    if payload.email is not None:
        if "@" not in payload.email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error("invalid email format", {"email": payload.email}),
            )
        user["email"] = payload.email

    return success(user)


# PUT 2: 아이템 정보 수정 (200, 400, 404)
@app.put("/items/{item_id}")
def update_item(item_id: int, payload: ItemUpdate):
    item = items_db.get(item_id)
    if not item:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error("item not found", {"item_id": item_id}),
        )

    if payload.name is None and payload.price is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error("nothing to update"),
        )

    if payload.name is not None:
        item["name"] = payload.name
    if payload.price is not None:
        if payload.price < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error("price must be >= 0", {"price": payload.price}),
            )
        item["price"] = payload.price

    return success(item)


# =========================================================
# DELETE (2개)
# =========================================================

# DELETE 1: 유저 삭제 (204, 404)
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error("user not found", {"user_id": user_id}),
        )

    del users_db[user_id]
    # 204는 바디 없이 응답
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# DELETE 2: 아이템 삭제 (204, 404)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    item = items_db.get(item_id)
    if not item:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error("item not found", {"item_id": item_id}),
        )

    del items_db[item_id]
    # 204는 바디 없이 응답
    return Response(status_code=status.HTTP_204_NO_CONTENT)