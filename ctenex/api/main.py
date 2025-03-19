from loguru import logger

from ctenex.api.app_factory import create_app
from ctenex.settings.application import get_app_settings

settings = get_app_settings()

app = create_app()


def main():
    _reload = settings.environment == "dev"
    logger.info(f"Running in {settings.environment} mode")

    uvicorn.run(
        app="ctenex.api.main:app",
        host=str(settings.api.api_host),
        port=settings.api.api_port,
        reload=_reload,
    )


if __name__ == "__main__":
    import uvicorn

    main()
