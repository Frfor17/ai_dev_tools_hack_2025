from mcp_instance import mcp
import httpx

FASTAPI_URL = "http://localhost:8000"
_client = None

async def get_client():
    """Создаем или возвращаем HTTP клиент."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

if __name__ == "__main__":
    print("=" * 60)
    print("CAD MCP Server запущен")
    print(f"Подключение к FastAPI: {FASTAPI_URL}")
    print("=" * 60)
    print("Доступные команды:")
    print("  • get_documents() - получить список документов")
    print("  • create_shape(shape_type, size) - создать фигуру")
    print("  • create_cube(size) - создать куб")
    print("  • create_sphere(size) - создать сферу")
    print("  • create_cylinder(size) - создать цилиндр")
    print("  • get_mcp_status() - статус сервера")
    print("=" * 60)

    mcp.run(transport='stdio')