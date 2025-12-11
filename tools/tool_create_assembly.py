from common_logic import FreeCADCore
from mcp_instance import mcp
import logging

logger = logging.getLogger(__name__)


def create_assemble(core, assembly_name="MyRobotAssembly", create_default_parts=True):
        """
        Создаёт новый документ FreeCAD и добавляет в него объект сборки.
        
        Args:
            assembly_name (str): Имя создаваемой сборки и документа.
            create_default_parts (bool): Создать ли стандартные детали (куб, цилиндр, сфера)
            
        Returns:
            dict: Результат операции с полями 'success', 'message', 'document' и 'assembly'.
        """
        try:
            # АВТОМАТИЧЕСКОЕ ПОДКЛЮЧЕНИЕ, как в create_simple_shape
            if not core.freecad:
                logger.info("FreeCAD not connected, calling connect()")
                result = core.connect()
                if not result["success"]:
                    logger.error(f"Connection failed: {result.get('error', 'Unknown error')}")
                    return {
                        "success": False,
                        "message": f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}",
                        "document": None,
                        "assembly": None,
                        "parts": []
                    }
            # Используем уже подключённые core.freecad и core.part
            if not core.freecad or not core.part:
                return {
                    "success": False,
                    "message": "FreeCAD не подключен. Сначала вызовите connect().",
                    "document": None,
                    "assembly": None,
                    "parts": []
                }
            
            # Создаём новый документ
            doc = core.freecad.newDocument(assembly_name)
            
            # Добавляем объект Модели (App::Part) - это контейнер сборки
            assembly = doc.addObject("App::Part", "Assembly")
            assembly.Label = assembly_name
            
            parts_list = []
            
            # Создаём стандартные детали, если нужно
            if create_default_parts:
                # Создаём базовые детали
                default_parts = [
                    {"type": "Box", "name": "Base", "length": 20, "width": 15, "height": 5},
                    {"type": "Cylinder", "name": "Shaft", "radius": 3, "height": 30},
                    {"type": "Sphere", "name": "Joint", "radius": 8}
                ]
                
                for part_info in default_parts:
                    try:
                        if part_info["type"] == "Box":
                            part = doc.addObject("Part::Box", part_info["name"])
                            part.Length = part_info["length"]
                            part.Width = part_info["width"]
                            part.Height = part_info["height"]
                        elif part_info["type"] == "Cylinder":
                            part = doc.addObject("Part::Cylinder", part_info["name"])
                            part.Radius = part_info["radius"]
                            part.Height = part_info["height"]
                        elif part_info["type"] == "Sphere":
                            part = doc.addObject("Part::Sphere", part_info["name"])
                            part.Radius = part_info["radius"]
                        
                        # Добавляем деталь в сборку
                        assembly.addObject(part)
                        parts_list.append(part_info["name"])
                        
                    except Exception as part_error:
                        print(f"Ошибка при создании детали {part_info['name']}: {part_error}")
            
            # Делаем сборку активным объектом
            doc.recompute()

            filename = f"{assembly_name}.FCStd"
            doc.saveAs(filename)
            
            return {
                "success": True,
                "message": f"Сборка '{assembly_name}' успешно создана" +
                        (f" с {len(parts_list)} деталями" if parts_list else ""),
                "document": doc.Name,
                "assembly": assembly.Name,
                "parts": parts_list
            }
        
        except Exception as e:
            error_msg = f"Ошибка при создании сборки: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "document": None,
                "assembly": None,
                "parts": []
            }

@mcp.tool()
def create_assembly_tool(name: str = "MyRobotAssembly"):
    """MCP-инструмент для создания сборки."""
    logger.info(f"create_assembly_tool called with name: {name}")
    
    try:
        # Сначала подключаемся к FreeCAD
        core = FreeCADCore()
        connect_result = core.connect()
        
        if not connect_result["success"]:
            logger.error(f"Failed to connect to FreeCAD: {connect_result.get('error', 'Unknown error')}")
            return f"Ошибка подключения к FreeCAD: {connect_result.get('error', 'Неизвестная ошибка')}"
        
        logger.info("FreeCAD connected successfully")
        
        # Теперь вызываем create_assemble
        result = create_assemble(core, name)
        logger.info(f"create_assemble result: {result}")
        
        return result.get("message", str(result))
        
    except Exception as e:
        logger.error(f"Exception in create_assembly_tool: {str(e)}", exc_info=True)
        return f"Ошибка при создании сборки: {str(e)}"