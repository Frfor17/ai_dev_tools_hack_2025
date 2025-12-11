import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

def start_fastapi():
    """Запуск FastAPI сервера."""
    print("🚀 Запуск FastAPI сервера...")
    subprocess.run([sys.executable, "ai_dev_tools_hack_2025/main.py"])

def start_agent_cli():
    """Запуск CLI интерфейса агента."""
    time.sleep(3)  # Даем время FastAPI запуститься
    print("\n🤖 Запуск CLI интерфейса агента...")
    subprocess.run([sys.executable, "ai_dev_tools_hack_2025/ai_agent/agent.py"])

def open_browser():
    """Открыть браузер с документацией API."""
    time.sleep(5)
    webbrowser.open("http://localhost:8001/docs")

if __name__ == "__main__":
    print("=" * 60)
    print("CAD System Launcher")
    print("=" * 60)
    
    # Запускаем FastAPI в основном потоке
    fastapi_thread = Thread(target=start_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Даем время на запуск
    time.sleep(2)
    
    # Открываем документацию в браузере
    browser_thread = Thread(target=open_browser)
    browser_thread.start()
    
    # Запускаем CLI агента
    print("\n1. FastAPI сервер запущен: http://localhost:8001")
    print("2. MCP сервер запущен: порт 8000")
    print("3. Swagger UI: http://localhost:8001/docs")
    print("4. Agent API: POST http://localhost:8001/api/agent/query")
    print("\nВыберите опцию:")
    print("1. Запустить CLI интерфейс агента")
    print("2. Протестировать агента через HTTP")
    print("3. Только сервер (без CLI)")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == "1":
        start_agent_cli()
    elif choice == "2":
        subprocess.run([sys.executable, "ai_dev_tools_hack_2025/ai_agent/test_agent.py"])
    else:
        print("\nСерверы запущены. Для выхода нажмите Ctrl+C")
        try:
            fastapi_thread.join()
        except KeyboardInterrupt:
            print("\nЗавершение работы...")