from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routes import api_router
from src.web.routes import web_router
from src.core.config import Settings, settings
from src.database.session import init_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class App:
    def __init__(
        self,
        settings: Settings = settings,
        api_router: APIRouter = api_router,
        web_router: APIRouter = web_router,
    ):
        self.__app = FastAPI(
            title=settings.PROJECT_NAME,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=self.lifespan,
        )
        self.__setup_middlewares(settings=settings)
        self.__setup_api_routes(settings=settings, router=api_router)
        self.__setup_web_routes(router=web_router)

    def __setup_middlewares(self, settings: Settings):
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_HOSTS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def __setup_api_routes(self, router: APIRouter, settings: Settings):
        self.__app.include_router(router, prefix=settings.API_V1_STR)

    def __setup_web_routes(self, router: APIRouter):
        self.__app.include_router(router)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        logger.info("Calling init DB...")
        init_db()
        yield

    def __call__(self):
        return self.__app


def create_app() -> FastAPI:
    return App(settings=settings, api_router=api_router, web_router=web_router)()


app = create_app() 

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
