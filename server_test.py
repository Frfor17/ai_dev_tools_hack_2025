#!/usr/bin/env python3
"""
Тест для выявления зависания при запуске сервера.
"""

import sys
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

print("🔍 Тест запуска сервера")

# Импортируем все необходимые модули
print("1. Импортируем модули...")
from fastapi import FastAPI
import uvicorn
import asyncio
import threading
from mcp_instance import mcp
from common_logic import core

print("   ✅ Все модули импортированы")

# Создаем приложение
print("2. Создаем FastAPI приложение...")
app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Test"}

print("   ✅ Приложение создано")

# Тестируем запуск MCP сервера
print("3. Тестируем запуск MCP сервера...")
try:
    mcp_thread = threading.Thread(target=lambda: mcp.run(transport="streamable-http", host="0.0.0.0", port=8000), daemon=True)
    mcp_thread.start()
    print("   ✅ MCP сервер запущен в потоке")
except Exception as e:
    print(f"   ❌ Ошибка запуска MCP: {e}")

# Тестируем запуск FastAPI сервера
print("4. Тестируем запуск FastAPI сервера...")
print("   ⚠️  Если сервер запустится, он будет висеть в этом терминале")
print("   ⚠️  Нажмите Ctrl+C для остановки")

try:
    uvicorn.run(app, host="0.0.0.0", port=8001)
    print("   ✅ FastAPI сервер запущен")
except Exception as e:
    print(f"   ❌ Ошибка запуска FastAPI: {e}")

print("5. Тест завершен")