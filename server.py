from mcp_instance import mcp
import httpx

PORT = 8000
HOST = "0.0.0.0"

# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status, tool_create_assembly


def main():
    """Запуск MCP сервера с HTTP транспортом."""
    print("=" * 60)
    print("🌐 ЗАПУСК CAD MCP СЕРВЕРА")
    print("=" * 60)
    print(f"🚀 MCP Server: http://{HOST}:{PORT}/mcp")
    print("=" * 60)
    
    mcp.run(transport="streamable-http", host=HOST, port=PORT)

if __name__ == "__main__":
    main()