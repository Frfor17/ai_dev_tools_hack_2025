from mcp_instance import mcp

@mcp.tool()
async def get_mcp_status() -> str:
    """
    Получить статус MCP сервера и доступные инструменты.
    """
    from server import get_client, FASTAPI_URL
    client = await get_client()
    try:
        response = await client.get(f"{FASTAPI_URL}/api/mcp/status")
        response.raise_for_status()
        data = response.json()

        tools_list = "\n".join([f"  - {tool}" for tool in data.get("tools", [])])
        return (f"📊 Статус MCP сервера:\n"
                f"Состояние: {data.get('status', 'unknown')}\n"
                f"Доступные инструменты:\n{tools_list}")
    except Exception as e:
        return f"Не удалось получить статус: {str(e)}\nУбедитесь, что FastAPI сервер запущен на {FASTAPI_URL}"