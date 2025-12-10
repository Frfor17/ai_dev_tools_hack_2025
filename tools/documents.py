from mcp_instance import mcp

@mcp.tool()
async def get_documents() -> str:
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
        return f"Документы: {data.get('result', [])}"
    except Exception as e:
        return f"Ошибка при получении документов: {str(e)}"