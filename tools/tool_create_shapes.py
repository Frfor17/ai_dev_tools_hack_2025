from mcp_instance import mcp
import httpx
from utils import ToolResult, validate_shape_type, validate_size

@mcp.tool()
async def create_shape(shape_type: str = "cube", size: float = 10.0) -> ToolResult:
    """
    Создать 3D-фигуру в CAD системе.
    
    Аргументы:
    - shape_type: Тип фигуры: cube (куб), sphere (сфера), cylinder (цилиндр)
    - size: Размер фигуры в миллиметрах (положительное число)
    """
    from server import get_client, FASTAPI_URL
    
    if not validate_shape_type(shape_type):
        valid_shapes = ["cube", "sphere", "cylinder"]
        return ToolResult(
            content=f"Ошибка: неподдерживаемый тип фигуры. Используйте: {', '.join(valid_shapes)}",
            structured_content={"error": "invalid_shape_type"},
            meta={"status": "validation_error"}
        )
    
    if not validate_size(size):
        return ToolResult(
            content="Ошибка: размер должен быть положительным числом",
            structured_content={"error": "invalid_size"},
            meta={"status": "validation_error"}
        )
    
    client = await get_client()
    try:
        params = {"shape_type": shape_type.lower(), "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        data = response.json()
        
        result_text = (f"✅ Фигура создана успешно!\n"
                      f"Тип: {data.get('parameters', {}).get('shape_type', 'неизвестно')}\n"
                      f"Размер: {data.get('parameters', {}).get('size', 'неизвестно')} мм\n"
                      f"Результат: {data.get('result', 'успешно')}")
        
        return ToolResult(
            content=result_text,
            structured_content=data,
            meta={
                "shape_type": shape_type,
                "size": size,
                "status": "success"
            }
        )
    except httpx.HTTPStatusError as e:
        error_text = f"HTTP ошибка: {e.response.status_code} - {e.response.text}"
        return ToolResult(
            content=error_text,
            structured_content={"error": str(e)},
            meta={"status": "error"}
        )
    except Exception as e:
        error_text = f"Ошибка при создании фигуры: {str(e)}"
        return ToolResult(
            content=error_text,
            structured_content={"error": str(e)},
            meta={"status": "error"}
        )