import sys
import os
from typing import Dict, Any
from app.core.exceptions import CADConnectionError
from app.domain.models import ShapeType

class FreeCADClient:
    """Адаптер для работы с FreeCAD (паттерн Adapter)."""
    
    def __init__(self, freecad_path: str):
        self.freecad_path = freecad_path
        self._freecad = None
        self._part = None
        self._connected = False
        
    def _ensure_connected(self) -> None:
        """Проверяет подключение к FreeCAD."""
        if not self._connected:
            self.connect()
    
    def connect(self) -> None:
        """Подключается к FreeCAD."""
        try:
            if self.freecad_path not in sys.path:
                sys.path.append(self.freecad_path)
            
            import FreeCAD
            import Part
            
            self._freecad = FreeCAD
            self._part = Part
            self._connected = True
            
        except ImportError as e:
            raise CADConnectionError(f"Ошибка подключения к FreeCAD: {e}")
    
    def get_documents(self) -> list:
        """Получает список документов."""
        self._ensure_connected()
        docs = []
        for doc in self._freecad.listDocuments().values():
            docs.append({
                "name": doc.Name,
                "object_count": len(doc.Objects)
            })
        return docs
    
    def create_shape(self, shape_type: ShapeType, size: float) -> Dict[str, Any]:
        """Создаёт фигуру в FreeCAD."""
        self._ensure_connected()
        
        doc = self._freecad.newDocument(f"{shape_type.value}_{size}")
        
        if shape_type == ShapeType.CUBE:
            shape = self._part.makeBox(size, size, size)
            obj_name = f"Cube_{size}mm"
        elif shape_type == ShapeType.SPHERE:
            shape = self._part.makeSphere(size/2)
            obj_name = f"Sphere_{size}mm"
        elif shape_type == ShapeType.CYLINDER:
            shape = self._part.makeCylinder(size/2, size)
            obj_name = f"Cylinder_{size}mm"
        else:
            raise ValueError(f"Неизвестный тип фигуры: {shape_type}")
        
        obj = doc.addObject("Part::Feature", obj_name)
        obj.Shape = shape
        doc.recompute()
        
        filename = f"{obj_name}.FCStd"
        doc.saveAs(filename)
        
        return {
            "document_name": doc.Name,
            "object_name": obj.Name,
            "filename": filename,
            "volume": shape.Volume
        }