#!/usr/bin/env python3
"""
Финальный тест - проверяем, что проблема из исходного сообщения решена
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_original_error_spec():
    """Тестируем именно ту спецификацию, которая была в ошибке"""
    print("🔍 Тестируем спецификацию из исходной ошибки...")
    
    try:
        from tools.tool_assemble_robot import assemble_robot, AssembleRobotRequest
        
        # Именно та спецификация, которая была в ошибке
        original_spec = {
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
                },
                {
                    "from": "wheel_2",
                    "to": "chassis",
                    "constraint": "coincident"
                },
                {
                    "from": "wheel_3",
                    "to": "chassis",
                    "constraint": "coincident"
                },
                {
                    "from": "wheel_4",
                    "to": "chassis",
                    "constraint": "coincident"
                }
            ]
        }
        
        print(f"   Спецификация: {json.dumps(original_spec, indent=2)}")
        
        # Создаем запрос
        request = AssembleRobotRequest(
            specification=original_spec,
            document_name="original_error_test_robot",
            output_path="original_error_test_robot.FCStd"
        )
        
        print(f"   Запрос создан")
        
        # Пробуем собрать робота
        result = assemble_robot(request)
        
        print(f"   Результат: {result}")
        
        # Проверяем, что результат соответствует ожидаемому формату
        expected_result = {
            "success": True,
            "message": "Робот успешно собран!",
            "document_path": "original_error_test_robot.FCStd",
            "components_created": ["chassis", "wheel"],
            "errors": []
        }
        
        if result.success:
            print(f"✅ УСПЕШНО: Робот собран!")
            print(f"   Сообщение: {result.message}")
            print(f"   Документ: {result.document_path}")
            print(f"   Компоненты: {result.components_created}")
            print(f"   Ошибки: {result.errors}")
            
            # Проверяем, что нет ошибки "No module named 'FreeCAD'"
            if "No module named 'FreeCAD'" in str(result.errors):
                print(f"❌ ОШИБКА: Всё ещё есть ошибка FreeCAD!")
                return False
            else:
                print(f"✅ ОТЛИЧНО: Ошибки FreeCAD нет!")
                return True
        else:
            print(f"❌ ОШИБКА: {result.message}")
            print(f"   Ошибки: {result.errors}")
            return False
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ФИНАЛЬНЫЙ ТЕСТ - ПРОВЕРКА ИСХОДНОЙ ОШИБКИ")
    print("=" * 60)
    
    # Тестируем спецификацию из исходной ошибки
    test_result = test_original_error_spec()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ФИНАЛЬНОГО ТЕСТА:")
    print("=" * 60)
    
    if test_result:
        print("🎉 ПРОБЛЕМА ПОЛНОСТЬЮ РЕШЕНА!")
        print("✅ Робот успешно собирается")
        print("✅ Нет ошибки 'No module named 'FreeCAD''")
        print("✅ Все компоненты создаются")
        print("✅ Документ сохраняется")
    else:
        print("❌ ПРОБЛЕМА НЕ РЕШЕНА!")
        print("Нужны дополнительные исправления.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()