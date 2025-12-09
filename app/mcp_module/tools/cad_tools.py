from typing import Dict, Any
from app.mcp_module.instance import mcp
from app.core.dependencies import container
from app.domain.models import CreateShapeRequest, ShapeType
from mcp.types import TextContent
from mcp.shared.exceptions import McpError, ErrorData

@mcp.tool(
    name="get_documents",
    description="📄 Получить список CAD документов из FreeCAD."
)
async def get_documents() -> Dict[str, Any]:
    """Получить список документов."""
    try:
        cad_service = container.cad_service
        docs = await cad_service.get_documents()
        
        if not docs:
            return {
                "content": [TextContent(type="text", text="Нет открытых документов")],
                "structured_content": {"documents": []}
            }
        
        formatted_docs = "\n".join([
            f"• {doc.name} (объектов: {doc.object_count})"
            for doc in docs
        ])
        
        return {
            "content": [TextContent(
                type="text", 
                text=f"📄 Документы FreeCAD:\n{formatted_docs}"
            )],
            "structured_content": {
                "documents": [doc.dict() for doc in docs]
            }
        }
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=-32603,
                message=f"Ошибка получения документов: {str(e)}"
            )
        )

@mcp.tool(
    name="create_shape",
    description="🛠️ Создать 3D-фигуру в CAD системе."
)
async def create_shape(
    shape_type: str = "cube",
    size: float = 10.0
) -> Dict[str, Any]:
    """Создать фигуру."""
    try:
        # Валидация
        try:
            shape_enum = ShapeType(shape_type.lower())
        except ValueError:
            raise McpError(
                ErrorData(
                    code=-32602,
                    message=f"Неподдерживаемый тип фигуры: {shape_type}. "
                    f"Доступно: cube, sphere, cylinder"
                )
            )
        
        if size <= 0:
            raise McpError(
                ErrorData(
                    code=-32602,
                    message="Размер должен быть положительным числом"
                )
            )
        
        # Создание фигуры
        cad_service = container.cad_service
        request = CreateShapeRequest(
            shape_type=shape_enum,
            size=size
        )
        
        result = await cad_service.create_shape(request)
        
        if not result.success:
            raise McpError(
                ErrorData(
                    code=-32603,
                    message=result.error or "Ошибка создания фигуры"
                )
            )
        
        return {
            "content": [TextContent(
                type="text",
                text=f"✅ Фигура создана успешно!\n"
                     f"Тип: {shape_type}\n"
                     f"Размер: {size} мм\n"
                     f"Файл: {result.data.get('filename', 'N/A')}"
            )],
            "structured_content": result.data
        }
        
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=-32603,
                message=f"Неожиданная ошибка: {str(e)}"
            )
        )