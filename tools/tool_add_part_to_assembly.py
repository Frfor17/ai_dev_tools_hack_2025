from common_logic import FreeCADCore
from mcp_instance import mcp
import logging

logger = logging.getLogger(__name__)

def add_part_to_assembly(core, assembly_name, part_name=None, part_type="Box"):
    """
    Добавляет деталь (объект) в сборку Assembly4.
    Если детали с таким именем нет, создаёт новую стандартную деталь.

    Args:
        assembly_name (str): Имя сборки (объекта App::Part с Type="Assembly").
        part_name (str, optional): Имя добавляемой детали. Если не существует, будет создана.
        part_type (str): Тип создаваемой детали, если её нет. Варианты: "Box", "Cylinder", "Sphere".

    Returns:
        dict: Результат с полями 'success', 'message', 'assembly', 'part'.
    """
    try:
        # проверяем подключение
        if not core.freecad:
            logger.info("FreeCAD not connected, calling connect()")
            result = core.connect()
            if not result["success"]:
                logger.error(f"Connection failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "message": f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}",
                    "assembly": None,
                    "part": None
                }
            
        doc = core.current_doc
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа. Сначала создайте сборку.",
                "assembly": None,
                "part": None
            }

        # 1. Находим объект сборки
        logger.info(f"Looking for assembly object with name: '{assembly_name}'")
        
        # Сначала получим все объекты в документе для диагностики
        all_objects = [obj.Name for obj in doc.Objects]
        logger.info(f"All objects in document: {all_objects}")
        
        assembly = doc.getObject(assembly_name)
        if not assembly:
            logger.error(f"Assembly object '{assembly_name}' not found in document")
            
            # Попробуем найти объект Assembly (по умолчанию создается с именем "Assembly")
            assembly_by_default = doc.getObject("Assembly")
            if assembly_by_default:
                logger.info(f"Found default assembly object: '{assembly_by_default.Name}' (Type: {assembly_by_default.TypeId})")
                logger.info(f"Assembly Label: {assembly_by_default.Label}")
                logger.info(f"Using default assembly object instead")
                assembly = assembly_by_default
            else:
                logger.error("No default 'Assembly' object found either")
                return {
                    "success": False,
                    "message": f"Сборка с именем '{assembly_name}' не найдена. Доступные объекты: {all_objects}",
                    "assembly": None,
                    "part": None
                }

        # 2. Ищем или создаём деталь
        if part_name and doc.getObject(part_name):
            # Деталь уже существует - используем её
            part = doc.getObject(part_name)
            msg_part = f"Существующая деталь '{part_name}'"
        else:
            # Создаём новую простую деталь
            if not part_name:
                part_name = f"New{part_type}"
            
            if part_type == "Box":
                part = doc.addObject("Part::Box", part_name)
                part.Length = 10.0
                part.Width = 10.0
                part.Height = 10.0
            elif part_type == "Cylinder":
                part = doc.addObject("Part::Cylinder", part_name)
                part.Radius = 5.0
                part.Height = 20.0
            elif part_type == "Sphere":
                part = doc.addObject("Part::Sphere", part_name)
                part.Radius = 7.0
            else:
                return {
                    "success": False,
                    "message": f"Неподдерживаемый тип детали: {part_type}",
                    "assembly": None,
                    "part": None
                }
            msg_part = f"Создана новая деталь '{part_name}' типа {part_type}"

        # 3. Добавляем деталь в сборку (важно для Assembly4)
        assembly.addObject(part)
        
        # 4. Обновляем документ и выделяем деталь для наглядности
        doc.recompute()

        return {
            "success": True,
            "message": f"{msg_part} добавлена в сборку '{assembly_name}' (объект: {assembly.Name}).",
            "assembly": assembly.Name,
            "part": part.Name
        }

    except Exception as e:
        error_msg = f"Ошибка при добавлении детали: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "assembly": None,
            "part": None
        }
    
@mcp.tool()
def add_part_to_assembly_tool(assembly_name: str, part_name: str = None, part_type: str = "Box"):
    """MCP-инструмент для добавления детали в сборку."""
    logger.info(f"add_part_to_assembly_tool called with assembly_name={assembly_name}, part_name={part_name}, part_type={part_type}")

    try:
        core = FreeCADCore()
        connect_result = core.connect()

        if not connect_result["success"]:
            logger.error(f"Failed to connect to FreeCAD: {connect_result.get('error', 'Unknown error')}")
            return f"Ошибка подключения к FreeCAD: {connect_result.get('error', 'Неизвестная ошибка')}"
        
        logger.info("FreeCAD connected successfully")

        # теперь вызываем add_part_to_assembly
        result = add_part_to_assembly(core, assembly_name, part_name, part_type)
        logger.info(f"add_part_to_assembly result: {result}")

        return result.get("message", str(result))
    
    except Exception as e:
        logger.error(f"Exception in add_part_to_assembly_tool: {str(e)}", exc_info=True)
        return f"Ошибка при добавлении детали: {str(e)}"