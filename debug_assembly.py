#!/usr/bin/env python3
"""
Диагностика проблемы со сборкой робота
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_freecad_import():
    """Тестируем импорт FreeCAD"""
    print("🔍 Тестируем импорт FreeCAD...")
    
    try:
        import FreeCAD
        print(f"✅ FreeCAD импортирован: {FreeCAD}")
        print(f"   Версия: {FreeCAD.Version()}")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта FreeCAD: {e}")
        return False
    except Exception as e:
        print(f"❌ Другая ошибка: {e}")
        return False

def test_part_import():
    """Тестируем импорт Part"""
    print("\n🔍 Тестируем импорт Part...")
    
    try:
        import Part
        print(f"✅ Part импортирован: {Part}")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта Part: {e}")
        return False
    except Exception as e:
        print(f"❌ Другая ошибка: {e}")
        return False

def test_common_logic():
    """Тестируем common_logic"""
    print("\n🔍 Тестируем common_logic...")
    
    try:
        from common_logic import core
        print(f"✅ common_logic импортирован: {core}")
        
        # Пытаемся подключиться
        result = core.connect()
        print(f"   Результат подключения: {result}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Ошибка common_logic: {e}")
        return False

def test_tool_assemble_robot():
    """Тестируем tool_assemble_robot"""
    print("\n🔍 Тестируем tool_assemble_robot...")
    
    try:
        from tools.tool_assemble_robot import assemble_robot, AssembleRobotRequest
        print(f"✅ tool_assemble_robot импортирован")
        
        # Создаем тестовую спецификацию
        test_spec = {
            "robot_type": "wheeled",
            "components": [
                {
                    "name": "chassis",
                    "type": "box",
                    "params": {
                        "length": 120,
                        "width": 80,
                        "height": 40
                    }
                },
                {
                    "name": "wheel",
                    "type": "cylinder",
                    "params": {
                        "radius": 30,
                        "height": 10
                    },
                    "count": 4
                }
            ],
            "assembly_rules": [
                {
                    "from": "wheel_1",
                    "to": "chassis",
                    "constraint": "coincident"
                }
            ]
        }
        
        request = AssembleRobotRequest(
            specification=test_spec,
            document_name="test_robot",
            output_path="test_robot.FCStd"
        )
        
        print(f"   Тестовый запрос создан")
        print(f"   Спецификация: {json.dumps(test_spec, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка tool_assemble_robot: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_assemble_endpoint():
    """Тестируем endpoint из main.py"""
    print("\n🔍 Тестируем assemble-robot endpoint...")
    
    try:
        from main import assemble_robot_from_prompt, AssembleRobotRequest
        print(f"✅ assemble-robot endpoint импортирован")
        
        # Создаем тестовый запрос
        request = AssembleRobotRequest(
            prompt="Создай простого робота с шасси и колесами",
            document_name="test_endpoint_robot",
            output_path="test_endpoint_robot.FCStd"
        )
        
        print(f"   Тестовый запрос endpoint создан")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка assemble-robot endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_freecad_path():
    """Проверяем путь к FreeCAD"""
    print("\n🔍 Проверяем путь к FreeCAD...")
    
    from common_logic import core
    print(f"   Путь в common_logic: {core.freecad_path}")
    print(f"   Папка существует: {os.path.exists(core.freecad_path)}")
    
    if os.path.exists(core.freecad_path):
        files = os.listdir(core.freecad_path)
        print(f"   Файлы в папке: {files[:10]}...")  # первые 10 файлов
    else:
        print(f"   Папка не существует!")
        
    print(f"   sys.path: {sys.path[:5]}...")  # первые 5 элементов

def main():
    """Основная функция диагностики"""
    print("=" * 60)
    print("ДИАГНОСТИКА ПРОБЛЕМЫ СО СБОРКОЙ РОБОТА")
    print("=" * 60)
    
    # Проверяем путь к FreeCAD
    check_freecad_path()
    
    # Тестируем импорты по порядку
    tests = [
        ("Импорт FreeCAD", test_freecad_import),
        ("Импорт Part", test_part_import),
        ("common_logic", test_common_logic),
        ("tool_assemble_robot", test_tool_assemble_robot),
        ("assemble-robot endpoint", test_main_assemble_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ДИАГНОСТИКИ:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    failed_tests = [name for name, result in results.items() if not result]
    
    if failed_tests:
        print(f"\n❌ ПРОБЛЕМЫ НАЙДЕНЫ в: {', '.join(failed_tests)}")
        
        if "Импорт FreeCAD" in failed_tests:
            print("\n🔧 РЕШЕНИЕ для FreeCAD:")
            print("1. Проверьте, что FreeCAD установлен")
            print("2. Убедитесь, что путь в common_logic.py правильный")
            print("3. Попробуйте запустить FreeCAD вручную, чтобы он зарегистрировал DLL")
            print("4. Проверьте переменные окружения PATH")
        
        if "common_logic" in failed_tests:
            print("\n🔧 РЕШЕНИЕ для common_logic:")
            print("1. Проверьте, что FreeCAD импортируется")
            print("2. Убедитесь, что common_logic.py не содержит синтаксических ошибок")
        
        if "tool_assemble_robot" in failed_tests:
            print("\n🔧 РЕШЕНИЕ для tool_assemble_robot:")
            print("1. Проверьте, что все зависимости импортируются")
            print("2. Убедитесь, что Pydantic модели определены правильно")
    else:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Проблема может быть в другом месте.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()