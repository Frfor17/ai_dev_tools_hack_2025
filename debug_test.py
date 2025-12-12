#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики проблемы с FastAPI сервером.
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

def test_imports():
    """Тестируем импорт модулей по очереди."""
    print("=" * 50)
    print("Тестирование импортов...")
    print("=" * 50)
    
    # 1. Тестируем FastAPI
    print("1. Импортируем FastAPI...")
    start_time = time.time()
    try:
        from fastapi import FastAPI, HTTPException, Query
        print(f"   ✅ FastAPI импортирован за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта FastAPI: {e}")
        return False
    
    # 2. Тестируем uvicorn
    print("2. Импортируем uvicorn...")
    start_time = time.time()
    try:
        import uvicorn
        print(f"   ✅ uvicorn импортирован за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта uvicorn: {e}")
        return False
    
    # 3. Тестируем asyncio
    print("3. Импортируем asyncio...")
    start_time = time.time()
    try:
        import asyncio
        print(f"   ✅ asyncio импортировано за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта asyncio: {e}")
        return False
    
    # 4. Тестируем threading
    print("4. Импортируем threading...")
    start_time = time.time()
    try:
        import threading
        print(f"   ✅ threading импортировано за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта threading: {e}")
        return False
    
    # 5. Тестируем mcp_instance
    print("5. Импортируем mcp_instance...")
    start_time = time.time()
    try:
        from mcp_instance import mcp
        print(f"   ✅ mcp_instance импортировано за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта mcp_instance: {e}")
        return False
    
    # 6. Тестируем common_logic (самый подозрительный)
    print("6. Импортируем common_logic...")
    start_time = time.time()
    try:
        from common_logic import core
        print(f"   ✅ common_logic импортировано за {time.time() - start_time:.2f}с")
    except Exception as e:
        print(f"   ❌ Ошибка импорта common_logic: {e}")
        return False
    
    print("\n✅ Все импорты прошли успешно!")
    return True

def test_core_creation():
    """Тестируем создание core экземпляра."""
    print("\n" + "=" * 50)
    print("Тестирование создания core...")
    print("=" * 50)
    
    try:
        from common_logic import core
        print(f"✅ core создан: {type(core)}")
        print(f"   FreeCAD path: {core.freecad_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания core: {e}")
        return False

def test_fastapi_app():
    """Тестируем создание FastAPI приложения."""
    print("\n" + "=" * 50)
    print("Тестирование создания FastAPI приложения...")
    print("=" * 50)
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test API")
        print("✅ FastAPI приложение создано")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания FastAPI приложения: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("🔍 Диагностика проблемы с FastAPI сервером")
    print("Этот скрипт поможет выявить, на каком этапе происходит зависание")
    
    # Тестируем импорты
    if not test_imports():
        print("\n❌ Проблема с импортами!")
        return
    
    # Тестируем core
    if not test_core_creation():
        print("\n❌ Проблема с созданием core!")
        return
    
    # Тестируем FastAPI
    if not test_fastapi_app():
        print("\n❌ Проблема с FastAPI!")
        return
    
    print("\n🎉 Все тесты пройдены! Проблема может быть в запуске сервера.")
    print("\nСледующие шаги:")
    print("1. Попробуйте запустить: uvicorn main:app --reload --port 8001")
    print("2. Если зависает - проблема в uvicorn.run()")
    print("3. Если не зависает - проблема в блоке if __name__ == '__main__':")

if __name__ == "__main__":
    main()