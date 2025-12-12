#!/usr/bin/env python3
"""
Тестовый скрипт для проверки сборки робота из JSON спецификации
"""

import asyncio
import json
import requests
import time

# Тестовая спецификация робота
test_specification = {
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

async def test_generate_spec():
    """Тест генерации спецификации через AI агент"""
    print("🧪 Тестируем генерацию спецификации...")
    
    from ai_agent import generate_spec_with_agent
    
    prompt = "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм."
    
    result = await generate_spec_with_agent(prompt)
    
    if result["success"]:
        print("✅ Спецификация успешно сгенерирована")
        print(json.dumps(result["specification"], indent=2, ensure_ascii=False))
        return result["specification"]
    else:
        print("❌ Ошибка генерации спецификации:", result.get("message", ""))
        return None

def test_assemble_robot():
    """Тест сборки робота из спецификации"""
    print("\n🤖 Тестируем сборку робота...")
    
    from tools.tool_assemble_robot import assemble_robot, AssembleRobotRequest
    
    request = AssembleRobotRequest(
        specification=test_specification,
        document_name="test_robot",
        output_path="test_robot.FCStd"
    )
    
    result = assemble_robot(request)
    
    print("Результат сборки:")
    print(f"✅ Успешно: {result.success}")
    print(f"📄 Сообщение: {result.message}")
    print(f"📁 Путь к файлу: {result.document_path}")
    print(f"🧩 Компоненты: {result.components_created}")
    if result.errors:
        print(f"⚠️ Ошибки: {result.errors}")
    
    return result.success

def test_api_endpoints():
    """Тест API endpoints"""
    print("\n🌐 Тестируем API endpoints...")
    
    base_url = "http://localhost:8001"
    
    # Тест генерации спецификации
    try:
        response = requests.post(
            f"{base_url}/api/ai/generate-spec",
            json={
                "prompt": "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм."
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация спецификации через API успешна")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка генерации: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
    
    # Тест сборки робота
    try:
        response = requests.post(
            f"{base_url}/api/ai/assemble-robot",
            json={
                "prompt": "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм.",
                "document_name": "api_test_robot",
                "output_path": "api_test_robot.FCStd"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Сборка робота через API успешна")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка сборки: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ошибка API: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов сборки робота")
    print("=" * 60)
    
    # Тест AI агента
    spec = asyncio.run(test_generate_spec())
    
    # Тест сборки
    if spec:
        success = test_assemble_robot()
        if success:
            print("✅ Тест сборки прошел успешно!")
        else:
            print("❌ Тест сборки провалился")
    
    # Тест API
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 Тесты завершены")
    print("💡 Теперь вы можете открыть созданный файл в FreeCAD и увидеть собранного робота!")