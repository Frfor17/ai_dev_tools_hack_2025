import os
import json
from typing import Type, Optional
from pydantic import BaseModel, Field

from openai import OpenAI

# --- ФУНКЦИЯ ДЛЯ ГЕНЕРАЦИИ JSON-СПЕЦИФИКАЦИИ ---
async def generate_spec_with_agent(user_prompt: str) -> dict:
    """
    Генерирует JSON-спецификацию робота по текстовому описанию.
    
    Args:
        user_prompt: Текстовое описание робота на естественном языке
        
    Returns:
        dict: Результат с полем 'success', 'specification' и 'message'
    """
    try:
        api_key = "Mzg0NDkwN2YtYzljYi00OTQ3LTk5ZGMtMjZmMTg2ZGQyZGVj.8984011dd7d9b60dc3497114858335b4"
        url = "https://foundation-models.api.cloud.ru/v1"
        
        client = OpenAI(api_key=api_key, base_url=url)
        
        # Системный промпт для генерации JSON
        system_prompt_content = """Ты — инженер-робототехник. Твоя единственная задача — преобразовывать описания роботов в строгий JSON по следующей схеме:
        {
          "robot_type": "wheeled | tracked | legged | arm",
          "components": [
            {"name": "chassis", "type": "box", "params": {"length": 100, "width": 60, "height": 30}},
            {"name": "wheel", "type": "cylinder", "params": {"radius": 20, "height": 10}, "count": 4}
          ],
          "assembly_rules": [
            {"from": "wheel_1", "to": "chassis", "constraint": "coincident"}
          ]
        }
        Отвечай ТОЛЬКО валидным JSON, без пояснений, Markdown-разметки или бэктиков (```json ... ```)."""
        
        response = client.chat.completions.create(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            max_tokens=2500,
            temperature=0.1,
            presence_penalty=0,
            top_p=0.95,
            messages=[
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Извлекаем ответ
        spec_json = response.choices[0].message.content.strip()
        
        # Проверяем валидность JSON
        spec = json.loads(spec_json)
        
        return {
            "success": True,
            "specification": spec,
            "raw_output": spec_json
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "specification": None,
            "message": f"Ошибка парсинга JSON: {str(e)}",
            "raw_output": spec_json if 'spec_json' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "specification": None,
            "message": f"Ошибка при генерации спецификации: {str(e)}"
        }

# --- СИНХРОННАЯ ВЕРСИЯ ФУНКЦИИ ---
def generate_spec_with_agent_sync(user_prompt: str) -> dict:
    """
    Синхронная версия функции для генерации JSON-спецификации робота.
    Используется в FastAPI endpoint.
    
    Args:
        user_prompt: Текстовое описание робота на естественном языке
        
    Returns:
        dict: Результат с полем 'success', 'specification' и 'message'
    """
    import asyncio
    return asyncio.run(generate_spec_with_agent(user_prompt))

# --- 4. ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
if __name__ == "__main__":
    # Пример вызова
    test_prompt = "Создай спецификацию для четырёхколёсного робота-исследователя с размерами шасси 120x80x40 мм и колёсами диаметром 60 мм."
    
    import asyncio
    result = asyncio.run(generate_spec_with_agent(test_prompt))
    
    if result["success"]:
        print("✅ Спецификация успешно создана:")
        print(json.dumps(result["specification"], indent=2, ensure_ascii=False))
    else:
        print("❌ Ошибка:", result.get("message", "Неизвестная ошибка"))
        print("Вывод агента:", result.get("raw_output", ""))