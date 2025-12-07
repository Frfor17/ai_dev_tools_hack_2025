"""Клиент для работы с CAD системами."""

import os
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

class CADClient:
    def __init__(self):
        # Конфигурация Onshape
        self.onshape_url = os.getenv("ONSHAPE_API_URL")
        self.onshape_key = os.getenv("ONSHAPE_ACCESS_KEY")
        self.onshape_secret = os.getenv("ONSHAPE_SECRET_KEY")
        
        # Или конфигурация другого CAD
        self.blender_url = os.getenv("BLENDER_API_URL")
        self.blender_token = os.getenv("BLENDER_API_TOKEN")
        
    async def get_onshape_documents(self) -> List[Dict[str, Any]]:
        """Получить список документов из Onshape."""
        if not all([self.onshape_url, self.onshape_key, self.onshape_secret]):
            raise ValueError("Не настроены ключи Onshape API в .env файле")
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.onshape_key}"
                }
                response = await client.get(
                    f"{self.onshape_url}/api/documents",
                    headers=headers
                )
                response.raise_for_status()
                documents = response.json()
                
                return [
                    {"name": doc.get("name"), "id": doc.get("id")}
                    for doc in documents.get("items", [])[:5]
                ]
                
        except Exception as e:
            raise RuntimeError(f"Ошибка при запросе к Onshape API: {str(e)}")
    
    async def get_blender_objects(self) -> List[Dict[str, Any]]:
        """Получить список объектов из Blender (если запущен API сервер)."""
        if not self.blender_url:
            raise ValueError("Не настроен URL Blender API")
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.blender_token:
                    headers["Authorization"] = f"Bearer {self.blender_token}"
                    
                response = await client.get(
                    f"{self.blender_url}/api/objects",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError:
            raise ConnectionError("Не удалось подключиться к Blender API. Убедитесь, что Blender запущен с включенным API.")
        except Exception as e:
            raise RuntimeError(f"Ошибка Blender API: {str(e)}")
    
    async def create_simple_shape(self, shape_type: str = "cube", size: float = 1.0) -> Dict[str, Any]:
        """Создать простую фигуру (имитация)."""
        shapes = ["cube", "sphere", "cylinder", "cone"]
        if shape_type.lower() not in shapes:
            raise ValueError(f"Неизвестный тип фигуры. Доступные: {', '.join(shapes)}")
        
        return {
            "shape_type": shape_type,
            "size": size,
            "status": "created",
            "message": f"Создана {shape_type} размера {size} в CAD системе"
        }

# Глобальный экземпляр клиента
cad_client = CADClient()