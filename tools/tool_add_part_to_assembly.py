import FreeCAD as App
import FreeCADGui as Gui
from common_logic import FreeCADCore

def add_part_to_assembly(assembly_name, part_name=None, part_type="Box"):
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
        doc = App.ActiveDocument
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа. Сначала создайте сборку.",
                "assembly": None,
                "part": None
            }

        # 1. Находим объект сборки
        assembly = doc.getObject(assembly_name)
        if not assembly:
            return {
                "success": False,
                "message": f"Сборка с именем '{assembly_name}' не найдена.",
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
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(part)

        return {
            "success": True,
            "message": f"{msg_part} добавлена в сборку '{assembly_name}'.",
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