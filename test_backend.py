"""Тест бэкенда MCP-сервера."""

import asyncio
import httpx
import sys
import json

async def test_mcp_backend():
    """Тестирование бэкенда MCP-сервера."""
    print("🧪 ТЕСТИРОВАНИЕ БЭКЕНДА MCP-СЕРВЕРА")
    print("="*60)
    
    # Конфигурация
    MCP_URL = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("1. Проверяю доступность сервера...")
        try:
            response = await client.get(f"{MCP_URL}/mcp/tools")
            if response.status_code == 200:
                print(f"   ✅ Сервер доступен (статус {response.status_code})")
            else:
                print(f"   ❌ Сервер отвечает со статусом {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Не удалось подключиться: {e}")
            print(f"   Убедитесь, что сервер запущен: python server.py")
            return False
        
        print("\n2. Получаю список инструментов...")
        try:
            response = await client.get(f"{MCP_URL}/mcp/tools")
            tools = response.json()
            print(f"   ✅ Найдено инструментов: {len(tools)}")
            for tool in tools:
                print(f"      • {tool.get('name', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False
        
        print("\n3. Тестирую инструменты...")
        test_cases = [
            ("list_cad_documents", "GET", {}),
            ("list_blender_objects", "GET", {}),
            ("cad_systems_info", "GET", {}),
            ("create_shape", "POST", {"shape_type": "cube", "size": 1.0}),
        ]
        
        results = []
        
        for tool_name, method, params in test_cases:
            print(f"   🔧 Тестирую {tool_name}...")
            
            try:
                if method == "GET":
                    response = await client.get(f"{MCP_URL}/mcp/tools/{tool_name}")
                else:
                    response = await client.post(
                        f"{MCP_URL}/mcp/tools/{tool_name}",
                        json=params
                    )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"      ✅ Успех (статус {response.status_code})")
                    
                    if "content" in data:
                        print(f"      📄 Есть контент")
                    
                    if "structured_content" in data:
                        print(f"      📊 Есть структурированные данные")
                    
                    results.append((tool_name, True))
                else:
                    print(f"      ❌ Ошибка: статус {response.status_code}")
                    print(f"      Тело ответа: {response.text[:200]}")
                    results.append((tool_name, False))
                    
            except Exception as e:
                print(f"      ❌ Исключение: {e}")
                results.append((tool_name, False))
        
        print("\n4. Проверяю обработку ошибок...")
        
        print("   🧪 Тест с неправильным параметром...")
        try:
            response = await client.post(
                f"{MCP_URL}/mcp/tools/create_shape",
                json={"shape_type": "unknown_shape", "size": 1.0}
            )
            if response.status_code >= 400:
                print(f"      ✅ Ошибка обработана правильно (статус {response.status_code})")
            else:
                print(f"      ⚠️ Неожиданный статус: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Исключение: {e}")
        
        print("\n" + "="*60)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*60)
        
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        for tool_name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {tool_name}")
        
        print(f"\n🎯 Успешно: {successful}/{total}")
        
        if successful == total:
            print("\n🎉 Бэкенд работает корректно!")
            return True
        else:
            print(f"\n⚠️ Есть проблемы с {total - successful} инструментами")
            return False

def run_quick_check():
    """Быстрая проверка без asyncio."""
    import requests
    
    print("🔍 БЫСТРАЯ ПРОВЕРКА MCP-СЕРВЕРА")
    print("="*40)
    
    try:
        response = requests.get("http://localhost:8000/mcp/tools", timeout=5)
        
        if response.status_code == 200:
            print("✅ MCP-сервер доступен")
            tools = response.json()
            print(f"🔧 Инструментов: {len(tools)}")
            
            print("\n🧪 Быстрый тест создания куба...")
            test_response = requests.post(
                "http://localhost:8000/mcp/tools/create_shape",
                json={"shape_type": "cube", "size": 1.0},
                timeout=10
            )
            
            if test_response.status_code == 200:
                print("✅ Тест успешен")
                data = test_response.json()
                print(f"📄 Ответ: {data.get('content', [{}])[0].get('text', '')[:50]}...")
                return True
            else:
                print(f"❌ Тест не пройден: статус {test_response.status_code}")
                return False
        else:
            print(f"❌ Сервер недоступен: статус {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("   Запустите сервер: python server.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("Выберите режим проверки:")
    print("1. Полное тестирование (async)")
    print("2. Быстрая проверка (sync)")
    print("3. Запустить простого агента")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == "1":
        success = asyncio.run(test_mcp_backend())
        sys.exit(0 if success else 1)
    elif choice == "2":
        success = run_quick_check()
        sys.exit(0 if success else 1)
    elif choice == "3":
        print("\nЗапуск простого агента...")
        print("="*60)
        asyncio.run(asyncio.run(main()))
    else:
        print("❌ Неверный выбор")
        sys.exit(1)