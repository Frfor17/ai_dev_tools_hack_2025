#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы endpoint create_rectangle_sketch_tool
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.tool_create_sketch import create_rectangle_sketch_tool

async def test_sketch_endpoint():
    """Тестируем endpoint для создания прямоугольного скетча."""
    print("🧪 Тестируем endpoint create_rectangle_sketch_tool...")
    print("=" * 60)
    
    try:
        # Тестируем с разными параметрами
        test_cases = [
            {"width": 10.0, "height": 5.0},
            {"width": 20.0, "height": 15.0},
            {"width": 5.0, "height": 5.0}
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\nТест {i}: width={params['width']}mm, height={params['height']}mm")
            print("-" * 40)
            
            result = await create_rectangle_sketch_tool(
                width=params["width"], 
                height=params["height"]
            )
            
            print(f"Результат: {result}")
            
            # Проверяем, что файл создан
            if "Файл:" in result:
                filename = result.split("Файл: ")[1].strip()
                if os.path.exists(filename):
                    print(f"✅ Файл {filename} успешно создан!")
                else:
                    print(f"⚠️  Файл {filename} не найден")
            
            print()
        
        print("🎉 Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sketch_endpoint())