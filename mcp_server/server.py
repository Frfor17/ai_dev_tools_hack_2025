"""MCP сервер для (вставить нужное)"""

import os
from mcp_server import mcp
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

#тут будут инструменты
from tools.market_data import get_price

def main():
    """Запуск MCP сервера с HTTP транспортом."""

    print("ЗАПУСК MCP СЕРВЕРА ДЛЯ БИЗНЕС-АНАЛИТИКИ")
    print(f"MCP Server: http://{HOST}:{PORT}/mcp")
    print("Доступные инструменты:")
    print("Coming soon")
    
    # Запускаем MCP сервер с streamable-http транспортом
    mcp.run(transport="streamable-http", host=HOST, port=PORT, stateless_http=True)

if __name__ == "__main__":
    main()