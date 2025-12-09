from fastapi import APIRouter, Depends, HTTPException
from app.services.cad_service import CADService
from app.domain.models import CreateShapeRequest, OperationResult, ShapeType
from app.core.dependencies import get_cad_service

router = APIRouter(prefix="/api/cad", tags=["CAD"])

@router.get("/documents")
async def get_documents(
    cad_service: CADService = Depends(get_cad_service)
):
    """Получить список документов."""
    docs = await cad_service.get_documents()
    return {"documents": [doc.dict() for doc in docs]}

@router.get("/create-shape")
async def create_shape(
    shape_type: str = "cube",
    size: float = 10.0,
    cad_service: CADService = Depends(get_cad_service)
) -> OperationResult:
    """Создать фигуру."""
    try:
        request = CreateShapeRequest(
            shape_type=ShapeType(shape_type.lower()),
            size=size
        )
        return await cad_service.create_shape(request)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Некорректные параметры: {str(e)}"
        )