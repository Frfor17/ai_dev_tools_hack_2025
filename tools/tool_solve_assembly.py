import FreeCAD as App
import FreeCADGui as Gui




@mcp.tool()
def solve_assembly_tool(
    assembly_name: str,
    update_positions: bool = True
):
    """MCP-инструмент для решения сборки и обновления позиций деталей."""
    result = solve_assembly(assembly_name, update_positions)
    return {
        "status": "success" if result["success"] else "error",
        "detail": result["message"],
        "data": {"solved": result["solved"]}
    }

def solve_assembly(assembly_name, update_positions=True):
    """
    Решает сборку Assembly4, вычисляя позиции деталей на основе ограничений.
    Обновляет 3D-вид.

    Args:
        assembly_name (str): Имя объекта сборки (App::Part с Type="Assembly").
        update_positions (bool): Если True, обновляет Placement деталей.

    Returns:
        dict: Результат с полями 'success', 'message', 'solved'.
    """
    try:
        doc = App.ActiveDocument
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа.",
                "solved": False
            }

        # 1. Находим сборку
        assembly = doc.getObject(assembly_name)
        if not assembly:
            return {
                "success": False,
                "message": f"Сборка с именем '{assembly_name}' не найдена.",
                "solved": False
            }

        # 2. Ключевой шаг: решаем сборку через метод Assembly4
        #    Метод solve() может быть у объекта сборки или в отдельном модуле.
        if hasattr(assembly, 'solve'):
            # Способ 1: Если у сборки есть прямой метод solve()
            assembly.solve()
        else:
            # Способ 2: Попытка использовать глобальный решатель Assembly4
            # Импортируем динамически, чтобы избежать ошибок при загрузке
            try:
                import a2p_solversystem
                solver = a2p_solversystem.SolverSystem()
                solver.solve(assembly, update_positions)
            except ImportError:
                return {
                    "success": False,
                    "message": "Не удалось найти модуль решателя a2p_solversystem. Убедитесь, что Assembly4 установлен корректно.",
                    "solved": False
                }

        # 3. Обновляем документ и вид
        doc.recompute()
        Gui.updateGui()  # Обновляем 3D-вид

        return {
            "success": True,
            "message": f"Сборка '{assembly_name}' успешно решена. Позиции деталей обновлены.",
            "solved": True
        }

    except Exception as e:
        error_msg = f"Ошибка при решении сборки: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "solved": False
        }