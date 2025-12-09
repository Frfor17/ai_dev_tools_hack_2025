from fastapi import APIRouter

router = APIRouter(prefix="/api/mcp", tags=["MCP"])

@router.get("/status")
async def get_mcp_status():
    """Получить статус MCP сервера."""
    return {
        "status": "running",
        "server_name": "CAD-Server",
        "version": "2.0.0"
    }