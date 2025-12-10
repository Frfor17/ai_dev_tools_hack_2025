from mcp_instance import mcp
from .utils import ToolResult

@mcp.tool()
async def get_mcp_status() -> ToolResult:
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
        result_text = (f"📊 Статус MCP сервера:\n"
                      f"Состояние: {data.get('status', 'unknown')}\n"
                      f"Доступные инструменты:\n{tools_list}")
        
        return ToolResult(
            content=result_text,
            structured_content=data,
            meta={"status": "success"}
        )
    except Exception as e:
        error_text = f"Не удалось получить статус: {str(e)}\nУбедитесь, что FastAPI сервер запущен на {FASTAPI_URL}"
        return ToolResult(
            content=error_text,
            structured_content={"error": str(e)},
            meta={"status": "error"}
        )