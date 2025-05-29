import fastapi
import uvicorn
from fastapi import FastAPI
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from phone_app.admin.setup import setup_admin
from phone_app.db.database import SessionLocal
from phone_app.api.endpoints import auth, phone
from starlette.middleware.sessions import SessionMiddleware




async def init_redis():
    return redis.Redis.from_url("redis://localhost", encoding='utf-8', decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await FastAPILimiter.init(redis)
    yield
    await redis.aclose()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

phone_app = fastapi.FastAPI(title='Phone', lifespan=lifespan)
phone_app.add_middleware(SessionMiddleware, secret_key='SECRET_KEY')
setup_admin(phone_app)

phone_app.include_router(auth.auth_router)
phone_app.include_router(phone.phone_router)



if __name__ == '__main__':
    uvicorn.run(phone_app, host='127.0.0.1', port=8000)