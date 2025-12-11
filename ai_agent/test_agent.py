import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

api_key = '821aa690d020da50bdb5919c1b49afd9'

def test_agent_query():
    """Тестирование агента через HTTP API."""
    url = "http://localhost:8001/api/agent/query"
    
    test_queries = [
        "Проверь статус MCP сервера",
        "Покажи список документов",
        "Создай куб размером 20мм",
        "Создай сферу диаметром 15мм в файле sphere.FCStd",
        "Создай звезду с 5 лучами, внутренний радиус 10мм, внешний 20мм, высота 5мм",
        "Создай шестеренку с 12 зубьями, модуль 2мм, внешний радиус 20мм, высота 5мм",
        "Создай тор с большим радиусом 30мм и малым радиусом 10мм"
    ]
    
    print("Тестирование CAD AI Agent...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nТест {i}: {query}")
        print("-" * 40)
        
        try:
            payload = {
                "query": query,
                "api_key": "821aa690d020da50bdb5919c1b49afd9"  # Замените на реальный ключ или уберите если в env
            }
            
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            
            if response.status_code == 200:
                if data.get("success"):
                    print(f"✅ Успех!")
                    print(f"Ответ: {data['result'][:200]}...")  # Показываем первые 200 символов
                else:
                    print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                print(f"Ответ: {data}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения: {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def test_agent_help():
    """Тестирование справки агента."""
    url = "http://localhost:8001/api/agent/help"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("\n📋 Справка по агенту:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("CAD AI Agent Tester")
    print("=" * 60)
    
    # Тестируем справку
    test_agent_help()
    
    # Тестируем запросы
    input("\nНажмите Enter для начала тестирования запросов...")
    test_agent_query()
    
    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)