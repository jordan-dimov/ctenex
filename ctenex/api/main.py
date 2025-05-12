from loguru import logger

from ctenex.api.app_factory import create_app
from ctenex.api.controllers.status import router as status_router
from ctenex.api.v1.controllers.exchange import router as stateless_exchange_router
from ctenex.api.v1.in_memory.controllers.exchange import (
    router as stateful_exchange_router,
)
from ctenex.api.v1.in_memory.lifespan import lifespan
from ctenex.settings.application import get_app_settings

settings = get_app_settings()

host = settings.api.api_host
port = settings.api.api_port
base_url = str(settings.api.base_url)

app = create_app(routers=[])

stateful_app_path = "/v1/stateful/"
stateful_app = create_app(
    lifespan=lifespan,
    routers=[status_router, stateful_exchange_router],
)
stateful_app_url = f"{base_url}{stateful_app_path}"
app.mount(stateful_app_path, stateful_app)

stateless_app_path = "/v1/stateless/"
stateless_app = create_app(
    routers=[status_router, stateless_exchange_router],
)
stateless_app_url = f"{base_url}{stateless_app_path}"
app.mount(stateless_app_path, stateless_app)


app.openapi_tags = [
    {
        "name": "v1/stateful",
        "externalDocs": {
            "description": "Stateful API",
            "url": stateful_app_url,
        },
    },
    {
        "name": "v1/stateless",
        "externalDocs": {
            "description": "Stateless API",
            "url": stateless_app_url,
        },
    },
]


def main():
    _reload = settings.environment == "dev"
    logger.info(f"Running in {settings.environment} mode")

    uvicorn.run(
        app="ctenex.api.main:app",
        host=str(host),
        port=port,
        reload=_reload,
    )


if __name__ == "__main__":
    import uvicorn

    main()
