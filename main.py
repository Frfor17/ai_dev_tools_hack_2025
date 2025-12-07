from fastapi import FastAPI, HTTPException
import uvicorn
from cad_client import cad_client
import asyncio

app = FastAPI(title="CAD API Gateway")

@app.get("/api/cad/documents")
async def get_documents():
    """Получить документы CAD."""
    result = await cad_client.get_onshape_documents()
    return {"result": result}

@app.get("/api/cad/blender-objects")
async def get_blender_objects():
    """Получить объекты Blender."""
    result = await cad_client.get_blender_objects()
    return {"result": result}

@app.post("/api/cad/create-shape")
async def create_shape(shape_type: str = "cube", size: float = 1.0):
    """Создать фигуру в CAD."""
    if size <= 0:
        raise HTTPException(status_code=400, detail="Размер должен быть положительным")
    
    result = await cad_client.create_simple_shape(shape_type, size)
    return {"result": result}

@app.get("/api/cad/info")
async def get_cad_info():
    """Информация о доступных CAD системах."""
    info_lines = []
    
    if cad_client.onshape_key:
        info_lines.append("Onshape: настроен")
    if cad_client.blender_url:
        info_lines.append("Blender API: настроен")
        
    return {
        "available_systems": info_lines,
        "note": "Настройте ключи в .env файле"
    }

@app.get("/")
async def root():
    return {
        "message": "CAD API Gateway",
        "endpoints": {
            "documents": "/api/cad/documents",
            "blender_objects": "/api/cad/blender-objects",
            "create_shape": "/api/cad/create-shape",
            "info": "/api/cad/info"
        }
    }

if __name__ == "__main__":
    print("CAD FastAPI Server запущен: http://localhost:8000")
    print("Swagger: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)