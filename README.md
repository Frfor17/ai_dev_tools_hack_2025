# ai_dev_tools_hack_2025
репо для хака (https://changellenge.com/championships/ai-devtools-hack/)

# 🚀 CAD AI Assistant System

**Говори с ИИ — получай 3D-модели в FreeCAD**

Система, которая позволяет управлять CAD (FreeCAD) через AI-ассистентов в VS Code (Continue.dev/Roo Code) или напрямую через API.

---

## 🎯 Что это такое?

### Коротко
Это **мост между AI-ассистентом и CAD-системой**. Ты говоришь в чате VS Code что-то вроде "Создай куб 20мм", и система:
1. 📡 AI-ассистент отправляет команду в MCP-сервер
2. 🔌 MCP-сервер делает запрос к FastAPI
3. 🛠️ FastAPI выполняет команду в FreeCAD
4. 📦 Возвращает результат обратно в чат

### Компоненты
| Файл | Что делает | Кто использует |
|------|------------|----------------|
| `mcp_server.py` | Переводчик между AI и API | Continue.dev / Roo Code |
| `main.py` | Веб-интерфейс и API | Браузер / другие программы |
| `common_logic/core.py` | Работа с FreeCAD | Оба сервера выше |

---

## 🏗️ Архитектура за 1 минуту(сломано)

┌─────────────────────────────────────────────┐
│ ТВОЙ AI-АССИСТЕНТ │
│ (Continue.dev / Roo Code) │
└─────────────────────┬───────────────────────┘
│ MCP протокол (stdio)
▼
┌─────────────────────────────────────────────┐
│ MCP Сервер (mcp_server.py) │
│ • Принимает команды от AI │
│ • Превращает в HTTP-запросы │
└─────────────────────┬───────────────────────┘
│ HTTP запросы
▼
┌─────────────────────────────────────────────┐
│ FastAPI Сервер (main.py) │
│ • REST API для всех операций │
│ • Валидация и логика │
└─────────────────────┬───────────────────────┘
│ FreeCAD API
▼
┌─────────────────────────────────────────────┐
│ FreeCAD (через common_logic) │
│ • Создание 3D-моделей │
│ • Работа с документами │
└─────────────────────────────────────────────┘


---

## ⚡ Быстрый старт

### 1. Установка (один раз)
```bash
# Клонируем проект (если есть)
git clone <ваш-репозиторий>
cd ai_dev_tools_hack_2025

# Создаем виртуальное окружение
python -m venv venv

# Активируем (Windows)
venv\Scripts\activate

# Устанавливаем зависимости
pip install fastapi uvicorn httpx mcp[cli]

2. Настройка FreeCAD

# В файле common_logic/core.py проверь путь:
self.freecad_path = r'C:\Program Files\FreeCAD 1.0\bin'
# Если FreeCAD установлен в другом месте - поменяй

3. Запуск (каждый раз)

# Терминал 1: Запуск API
python main.py

# Терминал 2: Запуск MCP сервера
python mcp_server.py

4. Настройка AI-ассистента

Создай файл C:\Users\ТВОЕ_ИМЯ\.continue\config.json:

{
  "version": "0.1.0",
  "models": [...],
  "mcpServers": {
    "cad-server": {
      "command": "python",
      "args": ["C:\\полный\\путь\\к\\mcp_server.py"]
    }
  }
}





ВОТ КАК ОНО ВЫГЛЯДИТ КОРОЧЕ:

┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│  AI Assistant   │◄──────────────────►│   MCP Server    │
│ (Roo Code    )  │                    │ (mcp_server.py) │
└─────────────────┘                    └────────┬────────┘
                                                │ HTTP
                                                ▼
┌─────────────────┐                    ┌─────────────────┐
│     User        │                    │   FastAPI       │
│  (Browser/curl) │◄──────────────────►│    (main.py)    │
└─────────────────┘     REST API       └────────┬────────┘
                                                 │
                                                 ▼
                                         ┌─────────────────┐
                                         │   FreeCAD       │
                                         │ (common_logic)  │
                                         └─────────────────┘

## 🛠️ Доступные команды

### Через AI-ассистент (Continue.dev / Roo Code)
- `get_documents()` - получить список документов
- `create_shape(shape_type, size)` - создать фигуру
- `create_cube(size)` - создать куб
- `create_sphere(size)` - создать сферу
- `create_cylinder(size)` - создать цилиндр
- `create_rectangle_sketch(width, height)` - создать прямоугольный скетч
- `get_mcp_status()` - статус сервера

### Через REST API (FastAPI)
- `GET /` - статус сервера
- `GET /documents` - список документов
- `POST /create-shape` - создать фигуру
- `POST /create-cube` - создать куб
- `POST /create-sphere` - создать сферу
- `POST /create-cylinder` - создать цилиндр
- `POST /create-sketch` - создать скетч

## 📝 Примеры использования

### Создание прямоугольного скетча
```python
# Через AI-ассистент
create_rectangle_sketch(width=20.0, height=15.0)

# Через REST API
POST /create-sketch
{
  "width": 20.0,
  "height": 15.0
}
```

### Создание 3D фигур
```python
# Куб 10мм
create_cube(size=10.0)

# Сфера 15мм
create_sphere(size=15.0)

# Цилиндр 20мм
create_cylinder(size=20.0)
```

## 📁 Структура проекта
```
ai_dev_tools_hack_2025/
├── main.py                 # FastAPI сервер
├── mcp_server.py          # MCP сервер для AI-ассистентов
├── common_logic/          # Логика работы с FreeCAD
│   ├── __init__.py
│   └── core.py            # FreeCADCore класс
├── tools/                 # Инструменты для MCP
│   ├── __init__.py
│   ├── tool_create_cube.py
│   ├── tool_create_sphere.py
│   ├── tool_create_cylinder.py
│   ├── tool_create_sketch.py    # Новый инструмент для скетчей
│   └── ...
├── docs/                  # Документация
│   └── create_rectangle_sketch_tool.md
├── test_sketch_endpoint.py # Тест для нового endpoint
└── README.md
```

## 🧪 Тестирование нового endpoint
```bash
# Запуск теста для скетча
python test_sketch_endpoint.py
```