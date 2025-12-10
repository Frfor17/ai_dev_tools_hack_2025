"""MCP сервер для работы с CAD системой."""

import os
from dotenv import load_dotenv, find_dotenv

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Импортируем единый экземпляр FastMCP
from mcp_instance import mcp

# Импортируем инструменты (они автоматически регистрируются при импорте)
from tools import (
    get_documents,
    create_shape,
    get_mcp_status,
    create_cube,
    create_sphere,
    create_cylinder
)

def main():
    """Запуск MCP сервера."""
    print("=" * 60)
    print("🌐 ЗАПУСК CAD MCP СЕРВЕРА")
    print("=" * 60)
    print("Доступные инструменты:")
    print("  • get_documents() - получить список документов")
    print("  • create_shape(shape_type, size) - создать фигуру")
    print("  • create_cube(size) - создать куб")
    print("  • create_sphere(size) - создать сферу")
    print("  • create_cylinder(size) - создать цилиндр")
    print("  • get_mcp_status() - статус сервера")
    print("=" * 60)
    
    # Запускаем MCP сервер с stdio транспортом
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()