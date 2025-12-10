"""Инструмент для получения статуса MCP сервера."""

from typing import Optional
from fastmcp import Context
from mcp.types import TextContent

# Импортируем mcp из единого экземпляра
from mcp_instance import mcp

# Импортируем утилиты
from .utils import ToolResult, get_client, FASTAPI_URL


@mcp.tool(
    name="get_mcp_server_status",
    description="""
    📊 Получить статус MCP сервера и доступные инструменты.
    
    Проверяет подключение к FastAPI серверу и отображает доступные инструменты.
    """
)
async def get_mcp_status(
    ctx: Context = None
) -> ToolResult:
    """
    Получает статус MCP сервера и информацию о доступных инструментах.
    
    Args:
        ctx: Контекст для логирования
        
    Returns:
        ToolResult: Статус сервера и список инструментов
        
    Examples:
        >>> result = await get_mcp_status()
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info("📡 Проверяем статус MCP сервера...")
    
    client = await get_client()
    try:
        response = await client.get(f"{FASTAPI_URL}/api/mcp/status")
        response.raise_for_status()
        data = response.json()
        
        tools_list = "\n".join([f"  • {tool}" for tool in data.get("tools", [])])
        status_text = (
            f"📊 Статус MCP сервера:\n\n"
            f"🔧 Состояние: {data.get('status', 'unknown')}\n"
            f"🌐 FastAPI: {FASTAPI_URL}\n\n"
            f"🛠️ Доступные инструменты:\n{tools_list}"
        )
        
        if ctx:
            await ctx.info("✅ Статус получен успешно")
        
        return ToolResult(
            content=[TextContent(type="text", text=status_text)],
            structured_content={
                "status": data.get('status'),
                "tools": data.get('tools', []),
                "fastapi_url": FASTAPI_URL
            },
            meta={"endpoint": "/api/mcp/status"}
        )
        
    except Exception as e:
        error_msg = f"❌ Не удалось получить статус: {str(e)}\nУбедитесь, что FastAPI сервер запущен на {FASTAPI_URL}"
        if ctx:
            await ctx.error(error_msg)
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={
                "endpoint": "/api/mcp/status",
                "fastapi_url": FASTAPI_URL,
                "error": True
            }
        )