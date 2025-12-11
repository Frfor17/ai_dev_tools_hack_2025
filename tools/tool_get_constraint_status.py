import FreeCAD as App

@mcp.tool()
def get_constraint_status_tool(assembly_name: str):
    """MCP-инструмент для получения детального статуса ограничений в сборке."""
    result = get_constraint_status(assembly_name)
    # Возвращаем структурированный ответ, удобный для анализа
    return result  # Можно напрямую вернуть словарь, если клиент ждёт JSON



def get_constraint_status(assembly_name):
    """
    Анализирует и возвращает подробный статус всех ограничений в сборке Assembly4.
    
    Args:
        assembly_name (str): Имя объекта сборки (App::Part с Type="Assembly").
        
    Returns:
        dict: Структурированный отчёт о состоянии сборки и её ограничений.
    """
    try:
        doc = App.ActiveDocument
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа.",
                "assembly_status": "error",
                "details": {}
            }

        # 1. Находим сборку
        assembly = doc.getObject(assembly_name)
        if not assembly:
            return {
                "success": False,
                "message": f"Сборка с именем '{assembly_name}' не найдена.",
                "assembly_status": "error",
                "details": {}
            }

        # 2. Инициализируем сборщик данных
        constraints_data = []
        assembly_status = "unknown"
        message = ""

        # 3. Собираем информацию о каждом объекте-ограничении в сборке
        for obj in assembly.OutListRecursive:
            if obj.TypeId == "Assembly::Constraint":
                constraint_info = {
                    "name": obj.Name,
                    "type": getattr(obj, "Type", "Unknown"),
                    "first": getattr(obj, "First", ""),
                    "second": getattr(obj, "Second", ""),
                    "offset": getattr(obj, "Offset", 0.0),
                    "satisfied": getattr(obj, "Satisfied", False),
                    "error_message": getattr(obj, "ErrorMessage", "")
                }
                constraints_data.append(constraint_info)

        # 4. Пытаемся получить глобальный статус сборки через решатель
        try:
            import a2p_solversystem
            solver = a2p_solversystem.SolverSystem()
            
            # Анализируем сборку без её решения (сухая проверка)
            status_code = solver.check(assembly)
            
            # Расшифровка кодов статуса (основано на логике Assembly4)
            status_messages = {
                0: ("fully_constrained", "Сборка полностью определена (стабильна)."),
                1: ("under_constrained", "Сборка недоопределена (детали имеют свободу перемещения)."),
                2: ("over_constrained", "Сборка переопределена (есть конфликтующие ограничения)."),
                -1: ("solver_error", "Ошибка решателя при анализе.")
            }
            
            assembly_status, message = status_messages.get(status_code, ("unknown", f"Получен неизвестный код статуса: {status_code}"))
            
        except ImportError:
            # Если решатель недоступен, даём оценку на основе данных об ограничениях
            if not constraints_data:
                assembly_status = "no_constraints"
                message = "В сборке нет ограничений. Добавьте ограничения между деталями."
            else:
                satisfied_constraints = sum(1 for c in constraints_data if c["satisfied"])
                if satisfied_constraints == len(constraints_data):
                    assembly_status = "appears_ok"
                    message = f"Все {len(constraints_data)} ограничений отмечены как 'Satisfied', но проверка решателем не выполнена."
                else:
                    assembly_status = "has_issues"
                    message = f"Только {satisfied_constraints} из {len(constraints_data)} ограничений отмечены как 'Satisfied'."

        return {
            "success": True,
            "message": f"Статус сборки '{assembly_name}': {message}",
            "assembly_status": assembly_status,  # Ключевой итоговый статус
            "constraints_count": len(constraints_data),
            "constraints": constraints_data,     # Детали по каждому ограничению
            "recommendation": _generate_recommendation(assembly_status, constraints_data)
        }

    except Exception as e:
        error_msg = f"Неожиданная ошибка при получении статуса сборки: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "assembly_status": "error",
            "details": {}
        }

def _generate_recommendation(status, constraints):
    """Генерирует рекомендацию на основе статуса сборки."""
    recommendations = {
        "fully_constrained": "Сборка готова. Можете экспортировать её или продолжить добавление деталей.",
        "under_constrained": "Добавьте дополнительные ограничения, чтобы убрать свободу перемещения деталей.",
        "over_constrained": "Удалите или измените конфликтующие ограничения. Найдите ограничения, помеченные как неудовлетворённые (Satisfied=False).",
        "no_constraints": "Используйте инструмент 'apply_constraint', чтобы связать детали между собой.",
        "appears_ok": "Для полной уверенности убедитесь, что установлен верстак Assembly4 и его решатель (a2p_solversystem).",
        "has_issues": "Проверьте ограничения с Satisfied=False. Возможно, указаны неверные геометрические элементы или несовместимые типы ограничений."
    }
    return recommendations.get(status, "Проверьте корректность установки Assembly4.")