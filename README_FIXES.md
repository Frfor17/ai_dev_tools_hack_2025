# Решение проблемы с FastAPI сервером

## Проблема
Сервер не запускался, висела вечная загрузка Swagger UI и эндпоинтов.

## Причина
Порты 8000 и 8001 были заняты другими процессами Python:
- Порт 8000: PID 8360
- Порт 8001: PID 2960

## Решение
1. **Изменены порты**:
   - MCP сервер: 8000 → 9000
   - FastAPI сервер: 8001 → 8080

2. **Добавлено опциональное GUI**:
   - GUI вынесено в отдельный файл `gui.py`
   - GUI запускается опционально через переменную окружения `ENABLE_GUI`
   - Если GUI не запускается - это не влияет на работу сервера

3. **Добавлено логирование**:
   - Добавлены подробные логи для диагностики
   - Логи показывают каждый этап работы сервера и FreeCAD

## Как использовать

### Запуск сервера без GUI (рекомендуется)
```bash
# Windows
$env:ENABLE_GUI="false"; python main.py

# Linux/MacOS
ENABLE_GUI=false python main.py
```

### Запуск сервера с GUI
```bash
# Windows
$env:ENABLE_GUI="true"; python main.py

# Linux/MacOS
ENABLE_GUI=true python main.py
```

### Прямой запуск
```bash
python main.py
```
(по умолчанию GUI включено)

## Доступные URL
- **Swagger UI**: http://localhost:8080/docs
- **Статус сервера**: http://localhost:8080/
- **Статус MCP**: http://localhost:8080/api/mcp/status
- **Создать фигуру**: http://localhost:8080/api/cad/create-shape?shape_type=cube&size=15
- **Создать сборку**: POST http://localhost:8080/api/cad/create-assembly?assembly_name=MyRobot

## Примеры запросов

### Создание куба 15мм
```bash
curl "http://localhost:8080/api/cad/create-shape?shape_type=cube&size=15"
```

### Создание сферы 20мм
```bash
curl "http://localhost:8080/api/cad/create-shape?shape_type=sphere&size=20"
```

### Создание сборки
```bash
curl -X POST "http://localhost:8080/api/cad/create-assembly?assembly_name=MyRobot"
```

## Файлы
- `main.py` - Основной сервер (порты изменены на 8080/9000)
- `gui.py` - Опциональный GUI интерфейс
- `common_logic.py` - Логика работы с FreeCAD (добавлены логи)
- `debug_test.py` - Тест для диагностики
- `simple_test.py` - Простой тест импортов
- `server_test.py` - Тест запуска сервера

## Проверка работы
1. Запустите сервер: `python main.py`
2. Откройте в браузере: http://localhost:8080/docs
3. Swagger UI должен загрузиться без зависаний
4. Проверьте эндпоинты через Swagger или curl

## Если GUI мешает
Установите переменную окружения `ENABLE_GUI=false` или удалите файл `gui.py`.

## Статус
✅ **Решено**: Сервер запускается, Swagger работает, все эндпоинты отвечают.