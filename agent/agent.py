"""Минимальный агент для проверки MCP-сервера."""

import asyncio
import httpx
from typing import Dict, Any

class SimpleCADAgent:
    """Простой агент для тестирования MCP-сервера."""
    
    def __init__(self, mcp_url: str = "http://localhost:8000"):
        self.mcp_url = mcp_url
        self.client = httpx.AsyncClient(timeout=30.0)
        print(f"🤖 Агент инициализирован. MCP сервер: {mcp_url}")
    
    async def test_all_tools(self):
        """Протестировать все инструменты MCP-сервера."""
        print("\n🧪 ТЕСТИРУЕМ ИНСТРУМЕНТЫ MCP...")
        
        tests = [
            ("list_cad_documents", "GET", {}, "Получение документов CAD"),
            ("list_blender_objects", "GET", {}, "Получение объектов Blender"),
            ("cad_systems_info", "GET", {}, "Информация о системах"),
            ("create_shape", "POST", {"shape_type": "cube", "size": 1.0}, "Создание куба"),
            ("create_shape", "POST", {"shape_type": "sphere", "size": 2.0}, "Создание сферы"),
        ]
        
        results = []
        
        for tool_name, method, params, description in tests:
            print(f"\n🔧 Тест: {description}")
            print(f"   Инструмент: {tool_name}")
            
            try:
                if method == "GET":
                    response = await self.client.get(
                        f"{self.mcp_url}/mcp/tools/{tool_name}"
                    )
                else: 
                    response = await self.client.post(
                        f"{self.mcp_url}/mcp/tools/{tool_name}",
                        json=params
                    )
                
                response.raise_for_status()
                data = response.json()
                
                print(f"   ✅ Успех! Статус: {response.status_code}")
                
                if "content" in data and data["content"]:
                    text = data["content"][0]["text"] if isinstance(data["content"], list) else str(data["content"])
                    print(f"   📄 Ответ: {text[:100]}...")
                else:
                    print(f"   📄 Ответ: {data}")
                
                results.append((tool_name, True, response.status_code))
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                results.append((tool_name, False, str(e)))

        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")

        success = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        for tool_name, success, status in results:
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {tool_name}: {status}")
        
        print(f"\n🎯 Успешно: {success}/{total} тестов")
        
        return success == total

    async def interactive_test(self):
        """Интерактивное тестирование."""
        print("\n🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ")
        print("Команды:")
        print("  docs     - Получить документы CAD")
        print("  objects  - Получить объекты Blender")
        print("  info     - Информация о системах")
        print("  cube     - Создать куб")
        print("  sphere   - Создать сферу")
        print("  test     - Запустить все тесты")
        print("  exit     - Выход")


        while True:
            cmd = input("\n▶️  Команда: ").strip().lower()
            
            if cmd == "exit":
                print("👋 Выход...")
                break
            elif cmd == "test":
                await self.test_all_tools()
            elif cmd in ["docs", "documents"]:
                await self.call_tool("list_cad_documents")
            elif cmd == "objects":
                await self.call_tool("list_blender_objects")
            elif cmd == "info":
                await self.call_tool("cad_systems_info")
            elif cmd == "cube":
                await self.call_tool("create_shape", {"shape_type": "cube", "size": 1.0})
            elif cmd == "sphere":
                await self.call_tool("create_shape", {"shape_type": "sphere", "size": 2.0})
            else:
                print("❌ Неизвестная команда. Доступные: docs, objects, info, cube, sphere, test, exit")

    async def call_tool(self, tool_name: str, params: Dict[str, Any] = None):
        """Вызвать конкретный инструмент."""
        print(f"\n🔧 Вызываю {tool_name}...")

        try:
            if params:
                response = await self.client.post(
                    f"{self.mcp_url}/mcp/tools/{tool_name}",
                    json=params
                )
            else:
                response = await self.client.get(
                    f"{self.mcp_url}/mcp/tools/{tool_name}"
                )

            response.raise_for_status()
            data = response.json()

            print(f"✅ Статус: {response.status_code}")

            self._pretty_print_response(data)

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def _pretty_print_response(self, data: Dict[str, Any]):
        """Красиво вывести ответ."""
        print("\n📦 ОТВЕТ:")
        print("-" * 40)

        if "content" in data and data["content"]:
            if isinstance(data["content"], list):
                for content in data["content"]:
                    if content.get("type") == "text":
                        print(content.get("text", ""))
            else:
                print(data["content"])

        if "structured_content" in data and data["structured_content"]:
            print("\n📊 Структурированные данные:")
            import json
            print(json.dumps(data["structured_content"], indent=2, ensure_ascii=False))

        if "meta" in data and data["meta"]:
            print("\n📌 Метаданные:")
            import json
            print(json.dumps(data["meta"], indent=2, ensure_ascii=False))

        print("-" * 40)

    async def check_mcp_status(self):
        """Проверить статус MCP-сервера."""
        print("🔍 Проверяю доступность MCP-сервера...")

        try:
            response = await self.client.get(f"{self.mcp_url}/mcp/tools")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ MCP-сервер доступен. Инструменты: {len(data)}")
                for tool in data:
                    print(f"   • {tool.get('name', 'unknown')}")
                return True
            else:
                print(f"⚠️ MCP-сервер отвечает со статусом {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Не удалось подключиться к MCP-серверу: {e}")
            print("   Убедитесь, что MCP-сервер запущен:")
            print("   python server.py")
            return False

    async def close(self):
        """Закрыть соединения."""
        await self.client.aclose()
        
async def main():
    """Основная функция."""
    print("="*60)
    print("🤖 ПРОСТОЙ АГЕНТ ДЛЯ ТЕСТИРОВАНИЯ MCP-СЕРВЕРА")
    print("="*60)

    agent = SimpleCADAgent()

    try:
        if not await agent.check_mcp_status():
            print("\n❌ MCP-сервер недоступен. Завершаем работу.")
            return

        print("\nВыберите режим:")
        print("1. Автоматическое тестирование всех инструментов")
        print("2. Интерактивный режим")
        
        choice = input("\nВаш выбор (1 или 2): ").strip()

        if choice == "1":
            success = await agent.test_all_tools()
            if success:
                print("\n🎉 Все тесты пройдены успешно!")
            else:
                print("\n⚠️ Некоторые тесты не прошли.")
        elif choice == "2":
            await agent.interactive_test()
        else:
            print("❌ Неверный выбор.")

    finally:
        await agent.close()
        print("\n👋 Агент завершил работу.")

if __name__ == "__main__":
    asyncio.run(main())