from mcp_instance import mcp
from .utils import ToolResult

@mcp.tool()
async def get_documents() -> ToolResult:
    """
    Получить список CAD документов из системы.
    Возвращает список документов в формате JSON.
    """
    from server import get_client, FASTAPI_URL
    client = await get_client()
    try:
        response = await client.get(f"{FASTAPI_URL}/api/cad/documents")
        response.raise_for_status()
        data = response.json()
        return ToolResult(
            content=f"Документы: {data.get('result', [])}",
            structured_content={"documents": data.get('result', [])},
            meta={"status": "success"}
        )
    except Exception as e:
        return ToolResult(
            content=f"Ошибка при получении документов: {str(e)}",
            structured_content={"error": str(e)},
            meta={"status": "error"}
        )