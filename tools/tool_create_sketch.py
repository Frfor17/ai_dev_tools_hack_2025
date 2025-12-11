from mcp_instance import mcp
from ..common_logic import FreeCADCore

# Инициализируем клиент для работы с FreeCAD
freecad_client = FreeCADCore()

@mcp.tool()
async def create_rectangle_sketch_tool(width: float = 10.0, height: float = 5.0) -> str:
    """
    Создать прямоугольный скетч в CAD системе.
        
    Аргументы:
    - width: Ширина прямоугольника в миллиметрах (положительное число)
    - height: Высота прямоугольника в миллиметрах (положительное число)
    """
    # Используем созданный клиент для создания скетча
    result = freecad_client.create_rectangle_sketch(width, height)
    
    if result["success"]:
        return f"✅ Скетч прямоугольника {width}x{height} мм успешно создан! Файл: {result['file']}"
    else:
        return f"❌ Ошибка создания скетча: {result['error']}"
