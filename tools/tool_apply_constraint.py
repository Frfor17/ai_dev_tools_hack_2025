import FreeCAD as App
import FreeCADGui as Gui



@mcp.tool()
def apply_constraint_tool(
    assembly_name: str,
    part1_name: str,
    element1: str,
    part2_name: str,
    element2: str,
    constraint_type: str = "Coincident",
    offset: float = 0.0
):
    """MCP-инструмент для применения ограничения между деталями."""
    result = apply_constraint(assembly_name, part1_name, element1, part2_name, element2, constraint_type, offset)
    return {
        "status": "success" if result["success"] else "error",
        "detail": result["message"],
        "data": {"constraint": result["constraint"]}
    }




def apply_constraint(assembly_name, part1_name, element1, part2_name, element2, constraint_type="Coincident", offset=0.0):
    """
    Накладывает ограничение между двумя деталями в сборке Assembly4.
    
    Args:
        assembly_name (str): Имя объекта сборки (App::Part).
        part1_name (str): Имя первой детали.
        element1 (str): Геометрический элемент первой детали (напр., "Face1", "Edge3", "Vertex5").
        part2_name (str): Имя второй детали.
        element2 (str): Геометрический элемент второй детали.
        constraint_type (str): Тип ограничения. Основные: "Coincident", "Concentric", "Parallel", "PlaneParallel", "PlaneDistance".
        offset (float): Смещение для типов ограничений с расстоянием (например, "PlaneDistance").
        
    Returns:
        dict: Результат с полями 'success', 'message', 'constraint'.
    """
    try:
        doc = App.ActiveDocument
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа.",
                "constraint": None
            }
        
        # 1. Находим сборку и детали
        assembly = doc.getObject(assembly_name)
        part1 = doc.getObject(part1_name)
        part2 = doc.getObject(part2_name)
        
        if not assembly or not part1 or not part2:
            return {
                "success": False,
                "message": f"Не найдены объекты: сборка '{assembly_name}', детали '{part1_name}' или '{part2_name}'.",
                "constraint": None
            }
        
        # 2. Создаём имя для нового ограничения
        constraint_name = f"Constraint_{part1_name}_{part2_name}_{constraint_type}"
        
        # 3. Добавляем объект ограничения Assembly4
        #    Тип объекта зависит от версии Assembly4. "Assembly::Constraint" — распространённый.
        constraint = doc.addObject("Assembly::Constraint", constraint_name)
        
        # 4. Настраиваем свойства ограничения
        constraint.Type = constraint_type
        constraint.First = f"{part1_name}.{element1}"
        constraint.Second = f"{part2_name}.{element2}"
        
        if constraint_type in ["PlaneDistance", "Distance"]:
            constraint.Offset = offset
        
        # 5. Добавляем ограничение в сборку и обновляем
        assembly.addObject(constraint)
        doc.recompute()
        
        return {
            "success": True,
            "message": f"Ограничение '{constraint_type}' создано между {part1_name}.{element1} и {part2_name}.{element2}.",
            "constraint": constraint.Name
        }
        
    except Exception as e:
        error_msg = f"Ошибка при создании ограничения: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "constraint": None
        }