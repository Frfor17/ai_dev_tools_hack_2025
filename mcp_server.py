"""MCP сервер для интеграции с CAD системами."""

import os
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from fastmcp import FastMCP, Context
from mcp_instance import mcp

PORT = int(os.getenv("PORT", "8000"))

from tools.list_cad_documents import list_cad_documents
from tools.list_blender_objects import list_blender_objects
from tools.create_shape import create_shape
from tools.cad_systems_info import cad_systems_info

def main():
    """Запуск MCP сервера с HTTP транспортом."""
    print("=" * 60)
    print("🌐 ЗАПУСК MCP СЕРВЕРА CAD INTEGRATION")
    print("=" * 60)
    print(f"🚀 MCP Server: http://0.0.0.0:{PORT}/mcp")
    print("=" * 60)
    
    # Запускаем MCP сервер с streamable-http транспортом
    mcp.run(transport="streamable-http", host="0.0.0.0", port=PORT, stateless_http=True)

if __name__ == "__main__":
    main()