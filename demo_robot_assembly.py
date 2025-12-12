#!/usr/bin/env python3
"""
Демонстрационный скрипт для сборки робота из текстового описания
"""

import requests
import json
import time

def demo_robot_assembly():
    """Демонстрация полного цикла: от текста до FreeCAD документа"""
    
    print("🤖 Демонстрация сборки робота из текстового описания")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Шаг 1: Генерация спецификации
    print("\n📝 Шаг 1: Генерация JSON-спецификации")
    print("Текстовое описание: 'Создай четырёхколёсного робота-исследователя'")
    
    spec_response = requests.post(
        f"{base_url}/api/ai/generate-spec",
        json={
            "prompt": "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм."
        },
        timeout=30
    )
    
    if spec_response.status_code == 200:
        spec_result = spec_response.json()
        print("✅ Спецификация успешно сгенерирована!")
        print("\n📋 JSON-спецификация:")
        print(json.dumps(spec_result["specification"], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Ошибка генерации: {spec_response.status_code}")
        return
    
    # Шаг 2: Сборка робота
    print("\n🏗️ Шаг 2: Сборка робота в FreeCAD")
    print("Запрос на создание документа 'demo_robot.FCStd'...")
    
    assemble_response = requests.post(
        f"{base_url}/api/ai/assemble-robot",
        json={
            "prompt": "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм.",
            "document_name": "demo_robot",
            "output_path": "demo_robot.FCStd"
        },
        timeout=60
    )
    
    if assemble_response.status_code == 200:
        assemble_result = assemble_response.json()
        print("✅ Робот успешно собран!")
        print(f"\n📄 Результат:")
        print(f"   - Успешно: {assemble_result['success']}")
        print(f"   - Путь к файлу: {assemble_result['document_path']}")
        print(f"   - Компоненты: {', '.join(assemble_result['components_created'])}")
        print(f"   - Ошибки: {len(assemble_result['errors'])}")
        
        if assemble_result['errors']:
            print("   ⚠️ Ошибки:")
            for error in assemble_result['errors']:
                print(f"      - {error}")
        
        print(f"\n💡 Инструкция:")
        print(f"   1. Откройте FreeCAD")
        print(f"   2. Откройте файл: {assemble_result['document_path']}")
        print(f"   3. Вы увидите собранного робота с шасси и 4 колёсами!")
        print(f"   4. Можете изучать, редактировать и экспортировать модель")
        
    else:
        print(f"❌ Ошибка сборки: {assemble_response.status_code}")
        print(f"   Текст ошибки: {assemble_response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 Демонстрация завершена!")
    print("\n💡 Дополнительные возможности:")
    print("   - Измените текстовое описание для создания других роботов")
    print("   - Используйте Swagger UI: http://localhost:8001/docs")
    print("   - Протестируйте другие endpoints API")

def test_different_robots():
    """Тестирование разных типов роботов"""
    
    print("\n\n🧪 Тестирование разных типов роботов")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    test_cases = [
        {
            "name": "Четырёхколёсный робот",
            "prompt": "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм.",
            "filename": "wheeled_robot.FCStd"
        },
        {
            "name": "Робот-манипулятор",
            "prompt": "Создай спецификацию для робота-манипулятора с основанием 200x150x50 мм, двумя сегментами руки длиной 300 мм и 200 мм, и захватом.",
            "filename": "arm_robot.FCStd"
        },
        {
            "name": "Гусеничный робот",
            "prompt": "Создай спецификацию для гусеничного робота с корпусом 200x120x60 мм и двумя гусеницами.",
            "filename": "tracked_robot.FCStd"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Описание: {test_case['prompt'][:60]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/ai/assemble-robot",
                json={
                    "prompt": test_case["prompt"],
                    "document_name": f"robot_{i}",
                    "output_path": test_case["filename"]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Создан файл: {result['document_path']}")
                print(f"   🧩 Компоненты: {', '.join(result['components_created'])}")
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Исключение: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено!")
    print("💡 Все созданные файлы можно открыть в FreeCAD")

if __name__ == "__main__":
    demo_robot_assembly()
    test_different_robots()