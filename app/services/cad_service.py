from typing import List, Dict, Any
from app.infrastructure.freecad_client import FreeCADClient
from app.domain.models import ShapeType, CreateShapeRequest, DocumentInfo, OperationResult
from app.services.factory import ShapeFactoryProducer

class CADService:
    """Сервис для работы с CAD (паттерн Service)."""
    
    def __init__(self, freecad_client: FreeCADClient):
        self.client = freecad_client
        
    async def get_documents(self) -> List[DocumentInfo]:
        """Получает список документов."""
        try:
            docs = self.client.get_documents()
            return [DocumentInfo(**doc) for doc in docs]
        except Exception as e:
            return []
    
    async def create_shape(self, request: CreateShapeRequest) -> OperationResult:
        """Создаёт фигуру."""
        try:
            # Используем фабрику
            factory = ShapeFactoryProducer.get_factory(request.shape_type)
            
            # Создаём фигуру через клиент
            result = self.client.create_shape(
                shape_type=request.shape_type,
                size=request.size
            )
            
            return OperationResult(
                success=True,
                data=result,
                message=f"Создана {request.shape_type.value} размером {request.size} мм"
            )
            
        except ValueError as e:
            return OperationResult(
                success=False,
                error=str(e)
            )
        except Exception as e:
            return OperationResult(
                success=False,
                error=f"Ошибка создания фигуры: {str(e)}"
            )