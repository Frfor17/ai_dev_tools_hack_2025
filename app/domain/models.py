from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, Optional

class ShapeType(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"
    CYLINDER = "cylinder"

class CreateShapeRequest(BaseModel):
    """Запрос на создание фигуры."""
    shape_type: ShapeType = Field(..., description="Тип фигуры")
    size: float = Field(..., gt=0, description="Размер фигуры в мм")

class DocumentInfo(BaseModel):
    """Информация о документе."""
    name: str
    object_count: int

class OperationResult(BaseModel):
    """Результат операции."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None