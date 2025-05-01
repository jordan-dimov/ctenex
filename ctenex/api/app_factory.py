from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import StatefulLifespan

from ctenex import __version__
from ctenex.settings.application import get_app_settings

settings = get_app_settings()


def create_app(
    routers: list[APIRouter],
    lifespan: StatefulLifespan[FastAPI] | None = None,
) -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        description=settings.project_description,
        docs_url="/",
        lifespan=lifespan,
    )
    register_cors(app)
    register_routers(app, routers)
    return app


def register_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI, routers: list[APIRouter]) -> None:
    for router in routers:
        app.include_router(router)
