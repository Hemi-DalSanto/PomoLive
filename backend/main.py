from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.persona_loader import persona_manager
from app.core.database import init_db
from app.api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa as tabelas do SQLite na subida
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend orquestrador assíncrono para o PomoLive",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta o router de WebSockets
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/personas", tags=["Personas"])
async def list_personas():
    return {
        "default": persona_manager.default_persona_id,
        "personas": persona_manager.list_available_personas()
    }