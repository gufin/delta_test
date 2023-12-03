import uvicorn
from fastapi import FastAPI

from app.core.containers import Container
from app.core.settings import settings
from app.endpoints.api import orders


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.project_name,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
    )
    container = Container()
    container.config.from_pydantic(settings)
    application.container = container
    application.include_router(orders.router)

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
    )
