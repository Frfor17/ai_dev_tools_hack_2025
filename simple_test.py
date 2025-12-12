#!/usr/bin/env python3
"""
Простой тест для выявления зависания при импорте.
"""

print("1. Начинаем тест...")

print("2. Импортируем sys...")
import sys
print("   ✅ sys импортирован")

print("3. Импортируем os...")
import os
print("   ✅ os импортирован")

print("4. Импортируем logging...")
import logging
print("   ✅ logging импортирован")

print("5. Импортируем FastAPI...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("6. Импортируем uvicorn...")
try:
    import uvicorn
    print("   ✅ uvicorn импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("7. Импортируем asyncio...")
try:
    import asyncio
    print("   ✅ asyncio импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("8. Импортируем threading...")
try:
    import threading
    print("   ✅ threading импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("9. Импортируем mcp_instance...")
try:
    from mcp_instance import mcp
    print("   ✅ mcp_instance импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("10. Импортируем common_logic...")
try:
    from common_logic import core
    print("   ✅ common_logic импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("11. Создаем FastAPI приложение...")
try:
    app = FastAPI(title="Test")
    print("   ✅ FastAPI приложение создано")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("12. Завершаем тест...")