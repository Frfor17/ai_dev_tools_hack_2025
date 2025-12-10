"""Инструмент для получения списка CAD документов."""

from typing import Optional
from fastmcp import Context
from pydantic import Field
from mcp.types import TextContent

# Импортируем mcp из единого экземпляра
from mcp_instance import mcp

# Импортируем утилиты
from .utils import ToolResult, get_client, FASTAPI_URL


@mcp.tool(
    name="get_cad_documents",
    description="""
    📋 Получить список CAD документов из системы.
    
    Возвращает список всех доступных документов в CAD системе.
    Используется для просмотра существующих проектов и моделей.
    """
)
async def get_documents(
    ctx: Context = None
) -> ToolResult:
    """
    Получает список CAD документов из системы.
    
    Args:
        ctx: Контекст для логирования и отслеживания прогресса
        
    Returns:
        ToolResult: Список документов в структурированном формате
        
    Raises:
        Exception: При ошибке соединения с FastAPI сервером
        
    Examples:
        >>> result = await get_documents()
        >>> print(result.content[0].text)
    """
    if ctx:
        await ctx.info("🔍 Получаем список CAD документов...")
    
    client = await get_client()
    try:
        response = await client.get(f"{FASTAPI_URL}/api/cad/documents")
        response.raise_for_status()
        data = response.json()
        
        documents = data.get('result', [])
        formatted_docs = "\n".join([
            f"📄 {doc.get('name', 'Без названия')} (ID: {doc.get('id', 'N/A')})"
            for doc in documents[:10]  # Ограничиваем вывод
        ]) if documents else "📭 Документы не найдены"
        
        if ctx:
            await ctx.info(f"✅ Получено {len(documents)} документов")
        
        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"📋 CAD документы ({len(documents)}):\n\n{formatted_docs}"
                )
            ],
            structured_content={"documents": documents, "count": len(documents)},
            meta={"endpoint": "/api/cad/documents"}
        )
        
    except Exception as e:
        error_msg = f"Ошибка при получении документов: {str(e)}"
        if ctx:
            await ctx.error(f"❌ {error_msg}")
        return ToolResult(
            content=[TextContent(type="text", text=error_msg)],
            structured_content={"error": str(e)},
            meta={"endpoint": "/api/cad/documents", "error": True}
        )