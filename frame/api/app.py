import secrets

from fastapi import FastAPI, Request
from fastapi.security import HTTPBasic
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from frame.config import cfg
from frame.utils import get_logger
from frame.constants import Environments
from frame.models.base import SessionLocal

logger = get_logger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    logger.info(request.url.path)
    if request.url.path in ("/docs", "/openapi.json"):
        response = await call_next(request)
        return response

    if cfg.env(default=Environments.PROD.value, cast=Environments) == Environments.PROD:
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header is None:
            return JSONResponse(
                status_code=401,
                content={"message": "Message is missing"},
            )
        if not secrets.compare_digest(
            auth_header.encode("utf8"), cfg.api_secret.encode("utf8")
        ):
            return JSONResponse(
                status_code=401,
                content={"message": "Secret is wrong."},
            )
    response = await call_next(request)
    return response


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/hello")
def say_hi():
    return JSONResponse(status_code=200, content={"message": "hi"})
