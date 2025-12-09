from typing import Generator
from fastapi import Depends
from app.core.config import settings
from app.infrastructure.freecad_client import FreeCADClient
from app.services.cad_service import CADService

class DIContainer:
    """Контейнер зависимостей."""
    
    def __init__(self):
        self._freecad_client = None
        self._cad_service = None
    
    @property
    def freecad_client(self) -> FreeCADClient:
        """Возвращает клиент FreeCAD (Singleton)."""
        if self._freecad_client is None:
            self._freecad_client = FreeCADClient(settings.freecad_path)
            self._freecad_client.connect()
        return self._freecad_client
    
    @property
    def cad_service(self) -> CADService:
        """Возвращает CAD сервис."""
        if self._cad_service is None:
            self._cad_service = CADService(self.freecad_client)
        return self._cad_service

# Глобальный экземпляр контейнера
container = DIContainer()

# FastAPI зависимости
def get_cad_service() -> Generator[CADService, None, None]:
    """Зависимость для получения CAD сервиса."""
    yield container.cad_service