from mcp.server.fastmcp import FastMCP
import httpx

# Создаем MCP сервер (без description)
mcp = FastMCP("CAD-Server")

# URL вашего FastAPI сервера
FASTAPI_URL = "http://localhost:8000"

# Асинхронный HTTP клиент (с общим для всех запросов)
_client = None

async def get_client():
    """Создаем или возвращаем HTTP клиент."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

# ============ ИНСТРУМЕНТЫ ДЛЯ РАБОТЫ С CAD ============

@mcp.tool()
async def get_documents() -> str:
    """
    Получить список CAD документов из системы.
    Возвращает список документов в формате JSON.
    """
    client = await get_client()
    try:
        response = await client.get(f"{FASTAPI_URL}/api/cad/documents")
        response.raise_for_status()
        data = response.json()
        return f"Документы: {data.get('result', [])}"
    except Exception as e:
        return f"Ошибка при получении документов: {str(e)}"

@mcp.tool()
async def create_shape(shape_type: str = "cube", size: float = 10.0) -> str:
    """
    Создать 3D-фигуру в CAD системе.
    
    Аргументы:
    - shape_type: Тип фигуры: cube (куб), sphere (сфера), cylinder (цилиндр)
    - size: Размер фигуры в миллиметрах (положительное число)
    """
    # Валидация параметров
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        return f"Ошибка: неподдерживаемый тип фигуры. Используйте: {', '.join(valid_shapes)}"
    
    if size <= 0:
        return "Ошибка: размер должен быть положительным числом"
    
    client = await get_client()
    try:
        # Параметры запроса
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

@mcp.tool()
async def get_mcp_status() -> str:
    """
    Получить статус MCP сервера и доступные инструменты.
    """
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

@mcp.tool()
async def create_cube(size: float = 10.0) -> str:
    """
    Создать куб в CAD системе.
    
    Аргументы:
    - size: Размер куба в миллиметрах (положительное число)
    """
    return await create_shape("cube", size)

@mcp.tool()
async def create_sphere(size: float = 10.0) -> str:
    """
    Создать сферу в CAD системе.
    
    Аргументы:
    - size: Диаметр сферы в миллиметрах (положительное число)
    """
    return await create_shape("sphere", size)

@mcp.tool()
async def create_cylinder(size: float = 10.0) -> str:
    """
    Создать цилиндр в CAD системе.
    
    Аргументы:
    - size: Диаметр цилиндра в миллиметрах (положительное число)
    """
    return await create_shape("cylinder", size)

# ============ ЗАПУСК СЕРВЕРА ============

if __name__ == "__main__":
    print("=" * 60)
    print("CAD MCP Server запущен")
    print(f"Подключение к FastAPI: {FASTAPI_URL}")
    print("=" * 60)
    print("Доступные команды:")
    print("  • get_documents() - получить список документов")
    print("  • create_shape(shape_type, size) - создать фигуру")
    print("  • create_cube(size) - создать куб")
    print("  • create_sphere(size) - создать сферу")
    print("  • create_cylinder(size) - создать цилиндр")
    print("  • get_mcp_status() - статус сервера")
    print("=" * 60)
    
    # Запускаем сервер
    mcp.run(transport='stdio')