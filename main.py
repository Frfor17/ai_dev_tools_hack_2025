import logging
import sys
import os
from fastapi import FastAPI, HTTPException, Query
import uvicorn
from common_logic import core
import asyncio
from mcp_instance import mcp
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Меняем на INFO, чтобы не засорять логи
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status

app = FastAPI(title="CAD API Gateway")

@app.get("/api/mcp/status")
async def get_mcp_status():
    """Получить статус MCP сервера."""
    logger.info("GET /api/mcp/status called")
    return {
        "status": "running",
        "tools": ["get_mcp_status", "get_documents", "create_shape", "create_cube", "create_sphere", "create_cylinder"],
        "description": "CAD MCP Server for FreeCAD operations"
    }

@app.get("/api/cad/documents")
async def get_documents():
    """Получить документы из FreeCAD."""
    logger.info("GET /api/cad/documents called")
    result = await core.get_onshape_documents()
    logger.info(f"GET /api/cad/documents result: {result}")
    return {"result": result}

@app.get("/api/cad/create-shape")
async def create_shape(shape_type: str = "cube", size: float = 10.0):
    """
    Создать фигуру в FreeCAD.
    
    Parameters:
    - shape_type: Тип фигуры (cube, sphere, cylinder)
    - size: Размер фигуры в мм
    """
    logger.info(f"GET /api/cad/create-shape called with shape_type={shape_type}, size={size}")
    
    # Валидация параметров
    if size <= 0:
        logger.warning(f"Invalid size: {size}")
        raise HTTPException(
            status_code=400,
            detail="Размер должен быть положительным числом"
        )
    
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        logger.warning(f"Invalid shape_type: {shape_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип фигуры. Доступно: {', '.join(valid_shapes)}"
        )
    
    # Вызов метода из common_logic
    logger.info(f"Calling core.create_simple_shape({shape_type.lower()}, {size})")
    result = await core.create_simple_shape(shape_type.lower(), size)
    logger.info(f"core.create_simple_shape result: {result}")
    
    return {
        "result": result,
        "parameters": {
            "shape_type": shape_type,
            "size": size
        }
    }

# НОВЫЙ ЭНДПОИНТ ДЛЯ СОЗДАНИЯ СБОРКИ
@app.post("/api/cad/create-assembly")
async def create_assembly(
    assembly_name: str = Query(..., description="Имя сборки"),
    create_default_parts: bool = Query(True, description="Создать стандартные детали автоматически")
):
    """
    Создать новую сборку Assembly4 в FreeCAD.
    
    Parameters:
    - assembly_name: Уникальное имя для сборки
    - create_default_parts: Автоматически создать базовые детали (куб, цилиндр, сфера)
    """
    logger.info(f"POST /api/cad/create-assembly called with assembly_name={assembly_name}, create_default_parts={create_default_parts}")
    
    try:
        # Используем синхронный вызов, так как FreeCAD API обычно синхронный
        logger.info(f"Calling core.create_assemble({assembly_name}, {create_default_parts})")
        result = await asyncio.to_thread(core.create_assemble, assembly_name, create_default_parts)
        logger.info(f"core.create_assemble result: {result}")
        
        if result.get("success", False):
            return {
                "status": "success",
                "message": result.get("message", "Сборка создана успешно"),
                "assembly_name": result.get("assembly_name", assembly_name),
                "parts": result.get("parts", []),
                "document": result.get("document_name")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Неизвестная ошибка при создании сборки")
            )
            
    except Exception as e:
        logger.error(f"Error in create_assembly: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании сборки: {str(e)}"
        )


@app.get("/")
async def root():
    logger.info("GET / called")
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
    logger.info("Starting FreeCAD FastAPI Server...")
    
    # Запуск MCP сервера в отдельном потоке
    logger.info("Starting MCP server on port 9000...")
    mcp_thread = threading.Thread(target=lambda: mcp.run(transport="streamable-http", host="0.0.0.0", port=9000), daemon=True)
    mcp_thread.start()
    logger.info("MCP server thread started")

    print("=" * 50)
    print("FreeCAD FastAPI Server запущен")
    print("MCP Server запущен на порту 9000")
    print("=" * 50)
    print("Swagger UI: http://localhost:8080/docs")
    print("Тест документов: http://localhost:8080/api/cad/documents")
    print("Создать сборку: POST /api/cad/create-assembly?assembly_name=MyRobot")
    print("Создать куб 15мм: http://localhost:8080/api/cad/create-shape?shape_type=cube&size=15")
    print("Создать сферу 20мм: http://localhost:8080/api/cad/create-shape?shape_type=sphere&size=20")
    print("Статус MCP: http://localhost:8080/api/mcp/status")
    print("=" * 50)
    
    # Опциональный запуск GUI
    gui_enabled = os.environ.get("ENABLE_GUI", "true").lower() == "true"
    if gui_enabled:
        try:
            logger.info("Starting GUI...")
            import gui
            gui_thread = threading.Thread(target=gui.run_gui, daemon=True)
            gui_thread.start()
            logger.info("GUI thread started")
        except Exception as e:
            logger.warning(f"GUI не удалось запустить: {e}")
            print("⚠️  GUI не удалось запустить (это не критично)")
    
    logger.info("Starting FastAPI server on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)