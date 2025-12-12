#!/usr/bin/env python3
"""
Тест исправленной сборки робота
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixed_assembly():
    """Тестируем исправленную сборку робота"""
    print("🔍 Тестируем исправленную сборку робота...")
    
    try:
        from tools.tool_assemble_robot import assemble_robot, AssembleRobotRequest
        
        # Создаем тестовую спецификацию (та же, что в ошибке)
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
        
        print(f"   Спецификация: {json.dumps(test_spec, indent=2)}")
        
        # Создаем запрос
        request = AssembleRobotRequest(
            specification=test_spec,
            document_name="test_fixed_robot",
            output_path="test_fixed_robot.FCStd"
        )
        
        print(f"   Запрос создан")
        
        # Пробуем собрать робота
        result = assemble_robot(request)
        
        print(f"   Результат: {result}")
        
        if result.success:
            print(f"✅ УСПЕШНО: Робот собран!")
            print(f"   Сообщение: {result.message}")
            print(f"   Документ: {result.document_path}")
            print(f"   Компоненты: {result.components_created}")
            if result.errors:
                print(f"   Ошибки: {result.errors}")
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

def test_endpoint():
    """Тестируем endpoint из main.py"""
    print("\n🔍 Тестируем assemble-robot endpoint...")
    
    try:
        from main import assemble_robot_from_prompt, AssembleRobotRequest
        
        # Создаем тестовый запрос
        request = AssembleRobotRequest(
            prompt="Создай простого робота с шасси и колесами",
            document_name="test_endpoint_robot",
            output_path="test_endpoint_robot.FCStd"
        )
        
        print(f"   Запрос endpoint создан")
        
        # Пробуем вызвать endpoint
        result = assemble_robot_from_prompt(request)
        
        print(f"   Результат endpoint: {result}")
        
        if result["success"]:
            print(f"✅ УСПЕШНО: Endpoint работает!")
            print(f"   Сообщение: {result['message']}")
            print(f"   Документ: {result['document_path']}")
            print(f"   Компоненты: {result['components_created']}")
            if result.get('errors'):
                print(f"   Ошибки: {result['errors']}")
            return True
        else:
            print(f"❌ ОШИБКА в endpoint: {result['message']}")
            return False
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ СБОРКИ РОБОТА")
    print("=" * 60)
    
    # Тестируем сборку
    assembly_result = test_fixed_assembly()
    
    # Тестируем endpoint
    endpoint_result = test_endpoint()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    print(f"{'✅ УСПЕШНО' if assembly_result else '❌ ОШИБКА'}: Сборка робота")
    print(f"{'✅ УСПЕШНО' if endpoint_result else '❌ ОШИБКА'}: Endpoint")
    
    if assembly_result and endpoint_result:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Проблема решена!")
    else:
        print("\n❌ ТЕСТЫ ПРОВАЛЕНЫ! Нужны дополнительные исправления.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()