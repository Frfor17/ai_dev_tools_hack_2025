import uvicorn
import sys
import os

# Add the project root directory to sys.path to make 'app' importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.endpoints import cad, mcp_status
from app.mcp_module.server import run_mcp_server_sync
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения."""
    # Запуск MCP сервера в отдельном потоке
    mcp_thread = threading.Thread(
        target=run_mcp_server_sync,
        daemon=True,
        kwargs={"transport": "stdio"}
    )
    mcp_thread.start()
    
    yield
    
    # Очистка ресурсов
    pass

app = FastAPI(
    title="CAD API Gateway",
    version="2.0.0",
    lifespan=lifespan
)

# Подключаем эндпоинты
app.include_router(cad)
app.include_router(mcp_status)

@app.get("/")
async def root():
    return {
        "message": "FreeCAD API Gateway v2.0",
        "endpoints": {
            "documents": "/api/cad/documents",
            "create_shape": "/api/cad/create-shape?shape_type=cube&size=10",
            "mcp_status": "/api/mcp/status"
        }
    }

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 FreeCAD FastAPI Server v2.0 запущен")
    print("=" * 50)
    print(f"📚 Swagger UI: http://localhost:{settings.api_port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )