from fastapi import FastAPI, HTTPException
import uvicorn
from common_logic import core
import asyncio
from mcp_instance import mcp
import threading

# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status

app = FastAPI(title="CAD API Gateway")

@app.get("/api/mcp/status")
async def get_mcp_status():
    """Получить статус MCP сервера."""
    return {
        "status": "running",
        "tools": ["get_mcp_status", "get_documents", "create_shape", "create_cube", "create_sphere", "create_cylinder"],
        "description": "CAD MCP Server for FreeCAD operations"
    }

@app.get("/api/cad/documents")
async def get_documents():
    """Получить документы из FreeCAD."""
    result = await core.get_onshape_documents()
    return {"result": result}

@app.get("/api/cad/create-shape")
async def create_shape(shape_type: str = "cube", size: float = 10.0):
    """
    Создать фигуру в FreeCAD.
    
    Parameters:
    - shape_type: Тип фигуры (cube, sphere, cylinder)
    - size: Размер фигуры в мм
    """
    # Валидация параметров
    if size <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Размер должен быть положительным числом"
        )
    
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип фигуры. Доступно: {', '.join(valid_shapes)}"
        )
    
    # Вызов метода из common_logic
    result = await core.create_simple_shape(shape_type.lower(), size)
    
    return {
        "result": result,
        "parameters": {
            "shape_type": shape_type,
            "size": size
        }
    }

@app.get("/")
async def root():
    return {
        "message": "FreeCAD API Gateway",
        "endpoints": {
            "documents": "/api/cad/documents",
            "create_shape": "/api/cad/create-shape?shape_type=cube&size=10",
            "create_cube_15mm": "/api/cad/create-shape?shape_type=cube&size=15",
            "create_sphere": "/api/cad/create-shape?shape_type=sphere&size=20",
            "create_cylinder": "/api/cad/create-shape?shape_type=cylinder&size=10"
        },
        "notes": "Размер указывается в миллиметрах"
    }

if __name__ == "__main__":
    # Запуск MCP сервера в отдельном потоке
    mcp_thread = threading.Thread(target=lambda: mcp.run(transport="streamable-http", host="0.0.0.0", port=8000), daemon=True)
    mcp_thread.start()

    print("=" * 50)
    print("FreeCAD FastAPI Server запущен")
    print("MCP Server запущен на порту 8000")
    print("=" * 50)
    print("Swagger UI: http://localhost:8001/docs")
    print("Тест документов: http://localhost:8001/api/cad/documents")
    print("Создать куб 15мм: http://localhost:8001/api/cad/create-shape?shape_type=cube&size=15")
    print("Создать сферу 20мм: http://localhost:8001/api/cad/create-shape?shape_type=sphere&size=20")
    print("Статус MCP: http://localhost:8001/api/mcp/status")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8001)