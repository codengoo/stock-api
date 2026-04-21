from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import APP_DESCRIPTION, OPENAPI_TAGS


def create_app() -> FastAPI:
    application = FastAPI(
        title="Stock Alert API",
        description=APP_DESCRIPTION,
        version="2.0.0",
        openapi_tags=OPENAPI_TAGS,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    @application.get("/", include_in_schema=False)
    def index():
        return {
            "name": application.title,
            "version": application.version,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }

    return application
