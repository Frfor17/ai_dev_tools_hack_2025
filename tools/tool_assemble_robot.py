import json
import os
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

# FreeCAD импортируется через common_logic.core, чтобы избежать ошибок при запуске без FreeCAD

def get_or_create_document(doc_name: str):
    """Получить или создать документ FreeCAD"""
    from common_logic import core
    
    # Сначала убеждаемся, что FreeCAD подключен
    if not core.freecad:
        result = core.connect()
        if not result["success"]:
            raise Exception(f"Не удалось подключиться к FreeCAD: {result.get('error', 'Неизвестная ошибка')}")
    
    try:
        doc = core.freecad.openDocument(doc_name + ".FCStd")
        return doc
    except:
        return core.freecad.newDocument(doc_name)

def get_or_create_body(doc, body_name: str):
    """Получить или создать тело в документе"""
    # Временно возвращаем None, так как тела не используются напрямую
    return None


class AssembleRobotRequest(BaseModel):
    """Запрос на сборку робота из спецификации"""
    specification: Dict[str, Any] = Field(..., description="JSON спецификация робота от AI агента")
    document_name: Optional[str] = Field(None, description="Имя документа FreeCAD")
    output_path: Optional[str] = Field(None, description="Путь для сохранения документа")


class AssembleRobotResponse(BaseModel):
    """Результат сборки робота"""
    success: bool
    message: str
    document_path: Optional[str] = None
    components_created: List[str] = []
    errors: List[str] = []


def create_component_from_spec(body, component_spec: Dict[str, Any]) -> Optional[Any]:
    """
    Создает компонент по спецификации
    
    Args:
        body: Тело FreeCAD для создания компонента
        component_spec: Спецификация компонента из JSON
    
    Returns:
        Созданный компонент или None при ошибке
    """
    try:
        # Используем FreeCAD через common_logic.core
        from common_logic import core
        
        # Убеждаемся, что FreeCAD подключен
        if not core.freecad or not core.part:
            result = core.connect()
            if not result["success"]:
                raise Exception(f"Не удалось подключиться к FreeCAD: {result.get('error', 'Неизвестная ошибка')}")
        
        comp_type = component_spec.get("type", "").lower()
        params = component_spec.get("params", {})
        
        if comp_type == "box":
            length = params.get("length", 10)
            width = params.get("width", 10)
            height = params.get("height", 10)
            return core.part.makeBox(length, width, height)
            
        elif comp_type == "cylinder":
            radius = params.get("radius", 10)
            height = params.get("height", 10)
            return core.part.makeCylinder(radius, height)
            
        elif comp_type == "sphere":
            radius = params.get("radius", 10)
            return core.part.makeSphere(radius)
            
        elif comp_type == "cone":
            radius1 = params.get("radius1", 10)
            radius2 = params.get("radius2", 5)
            height = params.get("height", 10)
            return core.part.makeCone(radius1, radius2, height)
            
        elif comp_type == "torus":
            radius1 = params.get("radius1", 20)
            radius2 = params.get("radius2", 5)
            return core.part.makeTorus(radius1, radius2)
            
        else:
            raise ValueError(f"Неизвестный тип компонента: {comp_type}")
            
    except Exception as e:
        raise Exception(f"Ошибка создания компонента '{component_spec.get('name', 'unknown')}': {str(e)}")


def assemble_robot_from_spec(specification: Dict[str, Any], doc) -> Dict[str, Any]:
    """
    Собирает робота из спецификации
    
    Args:
        specification: JSON спецификация робота
        doc: Документ FreeCAD
    
    Returns:
        Результат сборки
    """
    result = {
        "success": True,
        "components_created": [],
        "errors": [],
        "assembly_rules_applied": 0
    }
    
    try:
        # Используем FreeCAD через common_logic.core
        from common_logic import core
        
        # Убеждаемся, что FreeCAD подключен
        if not core.freecad or not core.part:
            result = core.connect()
            if not result["success"]:
                raise Exception(f"Не удалось подключиться к FreeCAD: {result.get('error', 'Неизвестная ошибка')}")
        
        # Создаем группу для робота
        robot_group = doc.addObject("App::DocumentObjectGroup", "Robot_Assembly")
        robot_group.Label = f"Robot ({specification.get('robot_type', 'unknown')})"
        
        # Создаем компоненты
        components = {}
        component_objects = {}
        
        for i, comp_spec in enumerate(specification.get("components", [])):
            try:
                comp_name = comp_spec.get("name", f"component_{i}")
                comp_count = comp_spec.get("count", 1)
                
                # Создаем компонент
                body = get_or_create_body(doc, comp_name)
                component_shape = create_component_from_spec(body, comp_spec)
                
                if component_shape:
                    # Создаем Part::Feature для компонента
                    part_obj = doc.addObject("Part::Feature", f"{comp_name}_shape")
                    part_obj.Shape = component_shape
                    part_obj.Label = comp_spec.get("name", f"Component {i+1}")
                    
                    # Добавляем в группу
                    robot_group.addObject(part_obj)
                    
                    # Сохраняем ссылку на объект
                    components[comp_name] = part_obj
                    component_objects[f"{comp_name}_1"] = part_obj
                    
                    # Если нужно несколько копий
                    if comp_count > 1:
                        for j in range(2, comp_count + 1):
                            copy_name = f"{comp_name}_{j}"
                            copy_obj = doc.addObject("Part::Feature", copy_name)
                            copy_obj.Shape = component_shape.copy()
                            copy_obj.Label = f"{comp_spec.get('name', f'Component {i+1}')} {j}"
                            robot_group.addObject(copy_obj)
                            component_objects[copy_name] = copy_obj
                    
                    result["components_created"].append(comp_name)
                    
            except Exception as e:
                error_msg = f"Ошибка создания компонента '{comp_spec.get('name', 'unknown')}': {str(e)}"
                result["errors"].append(error_msg)
                result["success"] = False
        
        # Применяем правила сборки
        assembly_rules = specification.get("assembly_rules", [])
        for rule in assembly_rules:
            try:
                from_comp = rule.get("from")
                to_comp = rule.get("to")
                constraint = rule.get("constraint", "coincident")
                
                if from_comp in component_objects and to_comp in component_objects:
                    from_obj = component_objects[from_comp]
                    to_obj = component_objects[to_comp]
                    
                    # Для простоты просто позиционируем компоненты
                    # В реальной системе здесь будут Constraints
                    if constraint == "coincident":
                        # Позиционируем компонент в центр другого
                        to_center = to_obj.Shape.CenterOfMass
                        from_obj.Placement.Base = to_center
                    elif constraint == "distance":
                        distance = rule.get("distance", 0)
                        # Простая позиционирование на расстоянии
                        to_center = to_obj.Shape.CenterOfMass
                        from_obj.Placement.Base = core.freecad.Vector(
                            to_center.x + distance,
                            to_center.y,
                            to_center.z
                        )
                    
                    result["assembly_rules_applied"] += 1
                    
            except Exception as e:
                error_msg = f"Ошибка применения правила сборки '{rule}': {str(e)}"
                result["errors"].append(error_msg)
                result["success"] = False
        
        # Обновляем документ
        doc.recompute()
        
        return result
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Критическая ошибка при сборке: {str(e)}")
        return result


def assemble_robot(request: AssembleRobotRequest) -> AssembleRobotResponse:
    """
    Собирает робота из спецификации и сохраняет в FreeCAD документ
    
    Args:
        request: Запрос с спецификацией и параметрами
    
    Returns:
        Результат операции
    """
    try:
        # Определяем имя документа
        doc_name = request.document_name or f"Robot_Assembly_{uuid.uuid4().hex[:8]}"
        
        # Создаем или получаем документ
        doc = get_or_create_document(doc_name)
        
        # Собираем робота
        assembly_result = assemble_robot_from_spec(request.specification, doc)
        
        # Определяем путь для сохранения
        output_path = request.output_path
        if not output_path:
            # Сохраняем в папку проекта
            output_path = os.path.join(os.getcwd(), f"{doc_name}.FCStd")
        
        # Сохраняем документ
        doc.saveAs(output_path)
        
        # Формируем сообщение
        message = f"Робот успешно собран!\n"
        message += f"Документ: {doc_name}\n"
        message += f"Путь: {output_path}\n"
        message += f"Компонентов создано: {len(assembly_result['components_created'])}\n"
        message += f"Правил сборки применено: {assembly_result['assembly_rules_applied']}\n"
        
        if assembly_result["errors"]:
            message += f"Ошибок: {len(assembly_result['errors'])}\n"
            for error in assembly_result["errors"]:
                message += f"  - {error}\n"
        
        return AssembleRobotResponse(
            success=assembly_result["success"],
            message=message,
            document_path=output_path,
            components_created=assembly_result["components_created"],
            errors=assembly_result["errors"]
        )
        
    except Exception as e:
        return AssembleRobotResponse(
            success=False,
            message=f"Ошибка при сборке робота: {str(e)}",
            errors=[str(e)]
        )


# Регистрация инструмента
def register_tool():
    """Регистрация инструмента в системе"""
    from tools import register_tool as register
    
    register(
        name="assemble_robot",
        description="Собирает робота из JSON спецификации и сохраняет в FreeCAD документ",
        function=assemble_robot,
        request_model=AssembleRobotRequest,
        response_model=AssembleRobotResponse
    )