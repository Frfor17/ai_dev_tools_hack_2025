import httpx
from mcp_instance import mcp

@mcp.tool()
async def create_shape(shape_type: str = "cube", size: float = 10.0) -> str:
    """
    Создать 3D-фигуру в CAD системе.
    
    Аргументы:
    - shape_type: Тип фигуры: cube (куб), sphere (сфера), cylinder (цилиндр)
    - size: Размер фигуры в миллиметрах (положительное число)
    """
    from server import get_client, FASTAPI_URL
    
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        return f"Ошибка: неподдерживаемый тип фигуры. Используйте: {', '.join(valid_shapes)}"
    
    if size <= 0:
        return "Ошибка: размер должен быть положительным числом"
    
    client = await get_client()
    try:
        params = {"shape_type": shape_type.lower(), "size": size}
        response = await client.get(f"{FASTAPI_URL}/api/cad/create-shape", params=params)
        response.raise_for_status()
        data = response.json()
        
        return (f"✅ Фигура создана успешно!\n"
                f"Тип: {data.get('parameters', {}).get('shape_type', 'неизвестно')}\n"
                f"Размер: {data.get('parameters', {}).get('size', 'неизвестно')} мм\n"
                f"Результат: {data.get('result', 'успешно')}")
    except httpx.HTTPStatusError as e:
        return f"HTTP ошибка: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Ошибка при создании фигуры: {str(e)}"