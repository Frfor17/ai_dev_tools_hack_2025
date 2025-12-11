# create_rectangle_sketch_tool Endpoint

## Описание
Эндпоинт для создания прямоугольного скетча в CAD системе (FreeCAD) через MCP сервер.

## Функция
- **Имя функции:** `create_rectangle_sketch_tool`
- **Тип:** MCP Tool (асинхронная)
- **Расположение:** `tools/tool_create_sketch.py`

## Параметры
- `width` (float, по умолчанию 10.0): Ширина прямоугольника в миллиметрах
- `height` (float, по умолчанию 5.0): Высота прямоугольника в миллиметрах

## Примеры использования

### Через Python
```python
from tools.tool_create_sketch import create_rectangle_sketch_tool

# Создать прямоугольник 20x15 мм
result = await create_rectangle_sketch_tool(width=20.0, height=15.0)
print(result)
```

### Через MCP клиент
```python
# Подключение к MCP серверу
client = await mcp.connect()

# Вызов инструмента
result = await client.call_tool("create_rectangle_sketch_tool", {
    "width": 25.0,
    "height": 10.0
})

print(result)
```

## Что делает функция
1. Подключается к FreeCAD (если еще не подключен)
2. Создает новый документ
3. Добавляет тело (Body) для скетча
4. Создает скетч на плоскости XY
5. Рисует прямоугольник с заданными размерами
6. Добавляет геометрические ограничения:
   - Горизонтальные линии (0 и 2)
   - Вертикальные линии (1 и 3)
   - Размеры по X и Y осям
   - Равенство противоположных сторон
   - Симметричность относительно центра
7. Пересчитывает документ
8. Сохраняет файл в формате `.FCStd`

## Возвращаемое значение
- **Успешно:** Строка с сообщением об успехе и именем файла
  ```
  ✅ Скетч прямоугольника 20.0x15.0 мм успешно создан! Файл: sketch_rectangle_20.0x15.0.FCStd
  ```
- **Ошибка:** Строка с сообщением об ошибке
  ```
  ❌ Ошибка создания скетча: FreeCAD не подключен
  ```

## Создаваемые файлы
Файлы сохраняются в формате:
```
sketch_rectangle_{width}x{height}.FCStd
```

Примеры:
- `sketch_rectangle_10.0x5.0.FCStd`
- `sketch_rectangle_20.0x15.0.FCStd`

## Требования
- Установленный FreeCAD
- Правильный путь к FreeCAD (по умолчанию: `C:\Program Files\FreeCAD 1.0\bin`)
- Доступ к Python API FreeCAD

## Запуск сервера
```bash
python server.py
```

После запуска сервера, инструмент будет доступен как:
```
create_rectangle_sketch(width, height)
```

## Тестирование
Для тестирования работы endpoint используйте:
```bash
python test_sketch_endpoint.py
```

## Интеграция
Endpoint автоматически регистрируется при импорте в `server.py`:
```python
from tools import ..., tool_create_sketch