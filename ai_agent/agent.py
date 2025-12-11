import os
import json
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

# Конфигурация OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.3-70b-instruct:free"
# MCP сервер
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CADAgent")

# ============ ИНСТРУМЕНТЫ (БЕЗ ИЗМЕНЕНИЙ) ============
def tool_open_document(file_path: str) -> dict:
    logger.info(f"Открытие документа: {file_path}")
    try:
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/open-document", 
                           params={"file_path": file_path}, timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_save_document(file_path: str = None) -> dict:
    logger.info(f"Сохранение документа: {file_path or 'текущий'}")
    try:
        params = {"file_path": file_path} if file_path else {}
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/save-document", 
                           params=params, timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_close_document() -> dict:
    logger.info("Закрытие документа")
    try:
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/close-document", timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_create_shape(shape_type: str, size: float, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> dict:
    logger.info(f"Создание фигуры: {shape_type}, размер: {size}")
    try:
        params = {"shape_type": shape_type, "size": size, "x": x, "y": y, "z": z}
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/create-shape", params=params, timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_create_complex_shape(
    shape_type: str,
    num_points: int = None,
    inner_radius: float = None,
    outer_radius: float = None,
    height: float = None,
    teeth: int = None,
    module: float = None,
    major_radius: float = None,
    minor_radius: float = None
) -> dict:
    logger.info(f"Создание сложной фигуры: {shape_type}")
    try:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/create-complex-shape", params=params, timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_create_test_shape(
    shape_type: str = "cube",
    size: float = 10.0,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    file_name: str = None
) -> dict:
    logger.info(f"Создание тестовой фигуры: {shape_type}")
    try:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/create-test-shape", params=params, timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_get_documents() -> dict:
    logger.info("Получение списка документов")
    try:
        response = httpx.get(f"{MCP_SERVER_URL}/api/cad/documents", timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

def tool_get_mcp_status() -> dict:
    logger.info("Получение статуса MCP сервера")
    try:
        response = httpx.get(f"{MCP_SERVER_URL}/api/mcp/status", timeout=30.0)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}

# ============ СХЕМЫ ИНСТРУМЕНТОВ ============
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_document",
            "description": "Открыть или создать документ FreeCAD по пути.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Путь к файлу .FCStd"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_document",
            "description": "Сохранить текущий документ, опционально по новому пути.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Новый путь (опционально)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_document",
            "description": "Закрыть текущий документ.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_shape",
            "description": "Создать простую фигуру в текущем документе.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shape_type": {"type": "string", "enum": ["cube", "sphere", "cylinder"]},
                    "size": {"type": "number"},
                    "x": {"type": "number", "default": 0.0},
                    "y": {"type": "number", "default": 0.0},
                    "z": {"type": "number", "default": 0.0}
                },
                "required": ["shape_type", "size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_complex_shape",
            "description": "Создать сложную фигуру в текущем документе.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shape_type": {"type": "string", "enum": ["star", "gear", "torus"]},
                    "num_points": {"type": "integer", "description": "Для star"},
                    "inner_radius": {"type": "number", "description": "Для star"},
                    "outer_radius": {"type": "number", "description": "Для star/gear"},
                    "height": {"type": "number", "description": "Для star/gear"},
                    "teeth": {"type": "integer", "description": "Для gear"},
                    "module": {"type": "number", "description": "Для gear"},
                    "major_radius": {"type": "number", "description": "Для torus"},
                    "minor_radius": {"type": "number", "description": "Для torus"}
                },
                "required": ["shape_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_test_shape",
            "description": "Создать тестовую фигуру и сохранить в файл.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shape_type": {"type": "string", "enum": ["cube", "sphere", "cylinder"]},
                    "size": {"type": "number"},
                    "x": {"type": "number", "default": 0.0},
                    "y": {"type": "number", "default": 0.0},
                    "z": {"type": "number", "default": 0.0},
                    "file_name": {"type": "string"}
                },
                "required": ["shape_type", "size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_documents",
            "description": "Получить список документов.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_mcp_status",
            "description": "Получить статус MCP сервера.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

TOOL_MAP = {
    "open_document": tool_open_document,
    "save_document": tool_save_document,
    "close_document": tool_close_document,
    "create_shape": tool_create_shape,
    "create_complex_shape": tool_create_complex_shape,
    "create_test_shape": tool_create_test_shape,
    "get_documents": tool_get_documents,
    "get_mcp_status": tool_get_mcp_status
}

# ============ АГЕНТ С OPENROUTER ============
class CADAgent:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or MODEL
        self.api_url = OPENROUTER_URL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY не найден. Установите в .env")
        
        logger.info(f"Агент инициализирован с OpenRouter")
        logger.info(f"Модель: {self.model}")
    
    def _call_llm(self, messages, tools=None):
        """Вызов LLM через OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8001",  # Для OpenRouter
            "X-Title": "CAD Agent"  # Для OpenRouter
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.3,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            logger.debug(f"Отправка запроса к LLM")
            response = httpx.post(self.api_url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка LLM: {e}")
            raise
    
    def process_query(self, user_query: str) -> str:
        """Обработка запроса пользователя"""
        logger.info(f"Обработка запроса: {user_query}")
        
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты - AI агент для работы с CAD системой FreeCAD через MCP сервер. "
                    "Используй доступные инструменты для выполнения задач. "
                    "Для создания фигур сначала открывай документ. "
                    "Если пользователь хочет создать фигуру без указания файла, используй create_test_shape. "
                    "Если пользователь хочет создать фигуру в существующем файле, используй open_document → create_shape → save_document. "
                    "Отвечай на русском языке."
                )
            },
            {"role": "user", "content": user_query}
        ]
        
        max_steps = 5
        for step in range(max_steps):
            logger.info(f"Шаг {step + 1}/{max_steps}")
            
            try:
                response_data = self._call_llm(messages, tools=TOOLS)
                
                if "choices" not in response_data:
                    return "Ошибка: не получен ответ от LLM"
                
                message = response_data["choices"][0]["message"]
                
                # Проверяем tool_calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls = message.tool_calls
                elif "tool_calls" in message:
                    tool_calls = message["tool_calls"]
                else:
                    tool_calls = []
                
                if tool_calls:
                    logger.info(f"LLM вызвал {len(tool_calls)} инструмент(ов)")
                    messages.append({
                        "role": "assistant",
                        "content": message.get("content", ""),
                        "tool_calls": tool_calls
                    })
                    
                    for tool_call in tool_calls:
                        # Извлекаем данные инструмента
                        if hasattr(tool_call, 'function'):
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                        else:
                            tool_name = tool_call["function"]["name"]
                            tool_args = json.loads(tool_call["function"]["arguments"])
                        
                        logger.info(f"Выполнение: {tool_name}")
                        
                        if tool_name in TOOL_MAP:
                            try:
                                tool_result = TOOL_MAP[tool_name](**tool_args)
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id", ""),
                                    "name": tool_name,
                                    "content": json.dumps(tool_result, ensure_ascii=False)
                                })
                            except Exception as e:
                                logger.error(f"Ошибка инструмента {tool_name}: {e}")
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id", ""),
                                    "name": tool_name,
                                    "content": json.dumps({"error": str(e)})
                                })
                        else:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.get("id", ""),
                                "name": tool_name,
                                "content": json.dumps({"error": "Инструмент не найден"})
                            })
                else:
                    return message.get("content", "Нет ответа")
                    
            except Exception as e:
                logger.error(f"Ошибка на шаге {step + 1}: {e}")
                return f"Ошибка: {str(e)}"
        
        return "Превышено максимальное количество шагов"

# ============ CLI ИНТЕРФЕЙС ============
def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 60)
    print("🤖 CAD AI Agent - OpenRouter (Бесплатный)")
    print("=" * 60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY не найден в .env")
        print("\nПолучите ключ:")
        print("1. Зарегистрируйтесь на https://openrouter.ai")
        print("2. В настройках создайте API ключ")
        print("3. Добавьте в .env: OPENROUTER_API_KEY=ваш_ключ")
        return
    
    try:
        agent = CADAgent(api_key=api_key)
        print("✅ Агент инициализирован")
        print(f"Модель: {agent.model}")
        print(f"API: OpenRouter (бесплатно)")
        print("=" * 60)
        
        # Тест подключения
        print("Тест подключения...")
        try:
            status = tool_get_mcp_status()
            print(f"✅ MCP статус: OK")
        except Exception as e:
            print(f"⚠️  MCP ошибка: {e}")
        
        print("\nПримеры запросов:")
        print("1. Создай куб 20мм")
        print("2. Проверь статус системы")
        print("3. Покажи список документов")
        print("4. Создай сферу 15мм в test.FCStd")
        print("\nВведите 'exit' для выхода")
        print("=" * 60)
        
        while True:
            query = input("\n💬 Ваш запрос: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("👋 Выход...")
                break
            
            if not query:
                continue
            
            print("⏳ Обработка...")
            try:
                result = agent.process_query(query)
                print(f"\n📝 Результат:\n{result}")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")

if __name__ == "__main__":
    main()