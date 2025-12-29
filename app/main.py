from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.feedback import router as feedback_router

from app.core.config import settings
from app.api.v1.router import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Backend API for RAM Companion (MVP).",
    )

    # CORS: pour que le frontend (plus tard) puisse appeler l'API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # MVP: permissif, on restreindra en prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router)
    app.include_router(feedback_router, prefix="/api/v1")

    @app.get("/", tags=["root"])
    def root():
        return {"message": "RAM Companion API is running. Go to /docs"}

    return app


app = create_app()
