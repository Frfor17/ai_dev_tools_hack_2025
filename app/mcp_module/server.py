import asyncio
from mcp.server import FastMCP
from app.mcp_module.instance import mcp

async def run_mcp_server(transport: str = "stdio"):
    """Запустить MCP сервер."""
    if transport == "stdio":
        # Запуск сервера в режиме stdio для MCP
        await mcp.run_stdio_async()
    else:
        # Другие транспорты, если нужно
        pass

def run_mcp_server_sync(transport: str = "stdio"):
    """Синхронная обертка для запуска MCP сервера."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_mcp_server(transport))
    finally:
        loop.close()