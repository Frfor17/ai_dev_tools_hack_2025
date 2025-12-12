#!/usr/bin/env python3
"""
Глубокая диагностика импорта FreeCAD
"""

import sys
import os

def test_direct_import():
    """Прямой импорт FreeCAD"""
    print("🔍 Пробуем прямой импорт FreeCAD...")
    
    try:
        import FreeCAD
        print(f"✅ УСПЕШНО: FreeCAD импортирован")
        print(f"   Версия: {FreeCAD.Version()}")
        print(f"   Путь: {FreeCAD.__file__}")
        return True
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

def test_common_logic_import():
    """Импорт через common_logic"""
    print("\n🔍 Пробуем импорт через common_logic...")
    
    try:
        from common_logic import core
        result = core.connect()
        print(f"✅ Результат подключения: {result}")
        return result["success"]
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

def test_tool_import():
    """Импорт через tool_assemble_robot"""
    print("\n🔍 Пробуем импорт через tool_assemble_robot...")
    
    try:
        # Импортируем tool_assemble_robot
        from tools.tool_assemble_robot import get_or_create_document
        
        # Пробуем вызвать функцию, которая импортирует FreeCAD
        doc = get_or_create_document("test_doc")
        print(f"✅ УСПЕШНО: get_or_create_document работает")
        print(f"   Документ: {doc}")
        return True
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_import():
    """Тестируем импорт функций из tool_assemble_robot"""
    print("\n🔍 Пробуем импорт функций из tool_assemble_robot...")
    
    try:
        from tools.tool_assemble_robot import create_component_from_spec, assemble_robot_from_spec
        print(f"✅ УСПЕШНО: Функции импортированы")
        print(f"   create_component_from_spec: {create_component_from_spec}")
        print(f"   assemble_robot_from_spec: {assemble_robot_from_spec}")
        return True
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sys_path():
    """Проверяем sys.path"""
    print("\n🔍 Проверяем sys.path...")
    
    from common_logic import core
    
    print(f"   Путь к FreeCAD: {core.freecad_path}")
    print(f"   В sys.path: {core.freecad_path in sys.path}")
    
    if core.freecad_path in sys.path:
        print("   ✅ Путь добавлен в sys.path")
    else:
        print("   ❌ Путь НЕ добавлен в sys.path")
    
    print(f"   Первые 10 элементов sys.path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"     {i+1}. {path}")

def main():
    """Основная диагностика"""
    print("=" * 60)
    print("ГЛУБОКАЯ ДИАГНОСТИКА ИМПОРТА FREECAD")
    print("=" * 60)
    
    # Проверяем sys.path
    check_sys_path()
    
    # Тестируем разные способы импорта
    tests = [
        ("Прямой импорт", test_direct_import),
        ("Через common_logic", test_common_logic_import),
        ("Через tool_assemble_robot (get_or_create_document)", test_tool_import),
        ("Через tool_assemble_robot (функции)", test_function_import),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # Анализ результатов
    print("\n" + "=" * 60)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ УСПЕШНО" if result else "❌ ОШИБКА"
        print(f"{status}: {test_name}")
    
    # Выводим рекомендации
    if not results["Прямой импорт"] and results["Через common_logic"]:
        print("\n🔧 ВЫВОД:")
        print("   FreeCAD импортируется ТОЛЬКО через common_logic.connect()")
        print("   Это означает, что FreeCAD требует специальной инициализации")
        print("   Проблема в том, что tool_assemble_robot пытается импортировать FreeCAD напрямую")
        
        print("\n🔧 РЕШЕНИЕ:")
        print("   1. Нужно изменить tool_assemble_robot.py")
        print("   2. Вместо прямого импорта FreeCAD, использовать common_logic.core")
        print("   3. Убедиться, что FreeCAD подключен перед использованием")
    
    if results["Через tool_assemble_robot (get_or_create_document)"]:
        print("\n✅ ХОРОШО:")
        print("   Функция get_or_create_document работает!")
        print("   Это означает, что проблема только в прямом импорте FreeCAD")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()