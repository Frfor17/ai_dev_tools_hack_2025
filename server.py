from mcp_instance import mcp
import httpx

# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status, tools_name, utils, tool_create_sketch
PORT = 8000
HOST = "0.0.0.0"

# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status, tool_open_document, tool_save_document, tool_close_document,tool_create_complex_shape


def main():
    """Запуск MCP сервера с HTTP транспортом."""
    print("=" * 60)
    print("ЗАПУСК CAD MCP СЕРВЕРА")
    print("=" * 60)
    print("Доступные команды:")
    print("  • get_documents() - получить список документов")
    print("  • create_shape(shape_type, size) - создать фигуру")
    print("  • create_cube(size) - создать куб")
    print("  • create_sphere(size) - создать сферу")
    print("  • create_cylinder(size) - создать цилиндр")
    print("  • create_rectangle_sketch(width, height) - создать прямоугольный скетч")
    print("  • get_mcp_status() - статус сервера")
    print(f"MCP Server: http://{HOST}:{PORT}/mcp")
    print("=" * 60)
    
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()