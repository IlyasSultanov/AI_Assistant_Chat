import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import router
from app.db.database import async_engine
from app.db.base_class import BaseModel
from app.exceptions.base_ex import BaseEx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения FastAPI.
    
    При запуске приложения создает все таблицы в базе данных.
    При завершении работы приложения выполняет очистку ресурсов.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(BaseEx)
async def base_exception_handler(request: Request, exc: BaseEx):
    """
    Обработчик для кастомных исключений приложения.
    
    Возвращает JSON ответ с кодом статуса и сообщением об ошибке.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    """
    Middleware для логирования HTTP запросов.
    
    Логирует тело запроса для отладки. В продакшене следует использовать
    более продвинутое логирование с фильтрацией чувствительных данных.
    """
    body = await request.body()
    print("REQUEST BODY:", body.decode(errors="ignore"))
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(app, reload=True)
