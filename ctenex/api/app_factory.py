from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ctenex import __version__
from ctenex.api.v1.controllers.exchange import router as exchange_router
from ctenex.api.v1.controllers.status import router as status_router
from ctenex.domain.matching_engine import MatchingEngine
from ctenex.settings.application import get_app_settings

settings = get_app_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    app.state.matching_engine = MatchingEngine()
    app.state.matching_engine.start()
    yield
    # Clean up the ML models and release the resources
    app.state.matching_engine.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        description=settings.project_description,
        docs_url="/",
        lifespan=lifespan,
    )
    register_cors(app)
    register_routers(app)
    return app


def register_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI) -> None:
    app.include_router(status_router)
    app.include_router(exchange_router)
