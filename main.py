from fastapi import FastAPI, HTTPException
import httpx
import uvicorn
from common_logic import core
import asyncio
from mcp_instance import mcp
import threading
import math
from dotenv import load_dotenv
import os
load_dotenv()

api_key = '821aa690d020da50bdb5919c1b49afd9'


# Импорт всех инструментов для регистрации
from tools import tool_create_cube, tool_create_cylinder, tool_create_shapes, tool_create_sphere, tool_documents, tool_status, tool_open_document, tool_save_document, tool_close_document, tool_create_complex_shape,tool_test_shape

app = FastAPI(title="CAD API Gateway")

@app.get("/api/mcp/status")
async def get_mcp_status():
    """Получить статус MCP сервера."""
    return {
        "status": "running",
        "tools": ["get_mcp_status", "get_documents", "create_shape", "create_cube", "create_sphere", "create_cylinder", "open_document", "save_document", "close_document", "create_complex_shape","tool_test_shape"],
        "description": "CAD MCP Server for FreeCAD operations"
    }

@app.get("/api/cad/documents")
async def get_documents():
    """Получить документы из FreeCAD."""
    result = await core.get_onshape_documents()
    return {"result": result}

@app.get("/api/cad/create-shape")
async def create_shape(
    shape_type: str = "cube", 
    size: float = 10.0,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0
):
    """
    Создать фигуру в FreeCAD в указанных координатах.
    
    Parameters:
    - shape_type: Тип фигуры (cube, sphere, cylinder)
    - size: Размер фигуры в мм
    - x, y, z: Координаты центра фигуры (в мм)
    """
    # Валидация параметров
    if size <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Размер должен быть положительным числом"
        )
    
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип фигуры. Доступно: {', '.join(valid_shapes)}"
        )
    
    # Вызов метода из common_logic с координатами
    result = await core.create_simple_shape(
        shape_type.lower(), 
        size,
        x,
        y,
        z
    )
    
    return {
        "result": result,
        "parameters": {
            "shape_type": shape_type,
            "size": size,
            "x": x,
            "y": y,
            "z": z
        }
    }

@app.get("/")
async def root():
    return {
        "message": "FreeCAD API Gateway",
        "endpoints": {
            "documents": "/api/cad/documents",
            "create_shape": "/api/cad/create-shape?shape_type=cube&size=10",
            "create_cube_15mm": "/api/cad/create-shape?shape_type=cube&size=15",
            "create_sphere": "/api/cad/create-shape?shape_type=sphere&size=20",
            "create_cylinder": "/api/cad/create-shape?shape_type=cylinder&size=10"
        },
        "notes": "Размер указывается в миллиметрах"
    }

@app.get("/api/cad/create-complex-shape")
async def create_complex_shape(
    shape_type: str,
    num_points: int = None,
    inner_radius: float = None,
    outer_radius: float = None,
    height: float = None,
    teeth: int = None,
    module: float = None,
    major_radius: float = None,
    minor_radius: float = None
):
    """
    Создать сложную 3D-фигуру в CAD системе.
    
    Поддерживаемые типы фигур:
    - star (звезда): требуется num_points, inner_radius, outer_radius, height
    - gear (шестеренка): требуется teeth, module, outer_radius, height
    - torus (тор): требуется major_radius, minor_radius
    """
    # Валидация типа фигуры
    valid_shapes = ["star", "gear", "torus"]
    if shape_type.lower() not in valid_shapes:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип фигуры. Доступно: {', '.join(valid_shapes)}"
        )
    
    # Проверяем подключение к FreeCAD
    if not core.freecad:
        result = core.connect()
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка подключения к FreeCAD: {result.get('error', 'Неизвестная ошибка')}"
            )
    
    # Проверяем наличие открытого документа
    if not core.current_doc:
        raise HTTPException(
            status_code=400,
            detail="Нет открытого документа. Сначала откройте документ с помощью /api/cad/open-document"
        )
    
    try:
        doc = core.current_doc
        
        if shape_type.lower() == "torus":
            # Проверка параметров
            if major_radius is None or minor_radius is None:
                raise HTTPException(
                    status_code=400,
                    detail="Для тора требуются major_radius и minor_radius"
                )
            if major_radius <= 0 or minor_radius <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Радиусы должны быть положительными"
                )
            if minor_radius >= major_radius:
                raise HTTPException(
                    status_code=400,
                    detail="minor_radius должен быть меньше major_radius"
                )
            
            # Создание тора
            torus = core.part.makeTorus(major_radius, minor_radius)
            obj = doc.addObject("Part::Feature", f"Torus_{major_radius}x{minor_radius}")
            obj.Shape = torus
            doc.recompute()
            
            result_message = f"Тор создан с большим радиусом {major_radius} мм и малым радиусом {minor_radius} мм"
            
        elif shape_type.lower() == "star":
            if num_points is None or inner_radius is None or outer_radius is None or height is None:
                raise HTTPException(
                    status_code=400,
                    detail="Для звезды требуются num_points, inner_radius, outer_radius, height"
                )
            if num_points < 5 or num_points % 2 == 0:
                raise HTTPException(
                    status_code=400,
                    detail="num_points для звезды должно быть нечетным числом >=5"
                )
            if inner_radius <= 0 or outer_radius <= 0 or height <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Радиусы и высота должны быть положительными"
                )
            if inner_radius >= outer_radius:
                raise HTTPException(
                    status_code=400,
                    detail="inner_radius должен быть меньше outer_radius"
                )
            
            # Создание звезды
            import math
            points = []
            for i in range(num_points * 2):
                angle = i * math.pi / num_points
                radius = inner_radius if i % 2 == 0 else outer_radius
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                points.append(core.freecad.Vector(x, y, 0))
            
            # Замыкаем контур
            points.append(points[0])
            
            # Создаем полигон
            wire = core.part.makePolygon(points)
            face = core.part.Face(wire)
            
            extruded = face.extrude(core.freecad.Vector(0, 0, height))
            obj = doc.addObject("Part::Feature", f"Star_{num_points}pts")
            obj.Shape = extruded
            doc.recompute()
            
            result_message = f"Звезда создана с {num_points} лучами, высотой {height} мм"
            
        elif shape_type.lower() == "gear":
            if teeth is None or module is None or outer_radius is None or height is None:
                raise HTTPException(
                    status_code=400,
                    detail="Для шестеренки требуются teeth, module, outer_radius, height"
                )
            if teeth < 3:
                raise HTTPException(
                    status_code=400,
                    detail="teeth должно быть >=3"
                )
            if module <= 0 or outer_radius <= 0 or height <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="module, outer_radius и height должны быть положительными"
                )
            # В реальном проекте нужно использовать более сложную геометрию
            cylinder = core.part.makeCylinder(outer_radius, height)
            obj = doc.addObject("Part::Feature", f"Gear_{teeth}teeth")
            obj.Shape = cylinder
            doc.recompute()
            
            result_message = f"Упрощенная шестеренка создана с {teeth} зубьями, высотой {height} мм. Для точной геометрии используйте специализированные библиотеки."
        
        return {
            "result": result_message,
            "parameters": {
                "shape_type": shape_type,
                "num_points": num_points,
                "inner_radius": inner_radius,
                "outer_radius": outer_radius,
                "height": height,
                "teeth": teeth,
                "module": module,
                "major_radius": major_radius,
                "minor_radius": minor_radius
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания сложной фигуры: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "FreeCAD API Gateway",
        "endpoints": {
            "documents": "/api/cad/documents",
            "create_shape": "/api/cad/create-shape?shape_type=cube&size=10",
            "create_cube_15mm": "/api/cad/create-shape?shape_type=cube&size=15",
            "create_sphere": "/api/cad/create-shape?shape_type=sphere&size=20",
            "create_cylinder": "/api/cad/create-shape?shape_type=cylinder&size=10",
            "create_complex_shape": "/api/cad/create-complex-shape?shape_type=star&num_points=5&inner_radius=10&outer_radius=20&height=5",
            "open_document": "/api/cad/open-document?file_path=test.FCStd",
            "save_document": "/api/cad/save-document?file_path=test.FCStd",
            "close_document": "/api/cad/close-document",
            "create_test_shape": "/api/cad/create-test-shape?shape_type=cube&size=10&file_name=my_test.FCStd",
            "create_test_cube": "/api/cad/create-test-shape?shape_type=cube&size=15",
            "create_test_sphere": "/api/cad/create-test-shape?shape_type=sphere&size=20",
            "create_test_cylinder": "/api/cad/create-test-shape?shape_type=cylinder&size=10&size=30",
        },
        "notes": "Размер указывается в миллиметрах. Для test_shape можно указать имя файла или оно будет сгенерировано автоматически"
    }

@app.get("/api/cad/open-document")
async def open_document(file_path: str):
    if not file_path:
        raise HTTPException(status_code=400, detail="Путь к файлу обязателен")
    result = await core.open_document(file_path)
    return {"result": result}

@app.get("/api/cad/save-document")
async def save_document(file_path: str = None):
    result = await core.save_document(file_path)
    return {"result": result}

@app.get("/api/cad/close-document")
async def close_document():
    result = await core.close_document()
    return {"result": result}

@app.get("/api/cad/create-test-shape")
async def create_test_shape_endpoint(
    shape_type: str = "cube",
    size: float = 10.0,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    file_name: str = None
):
    """
    Создать тестовую 3D-фигуру и сохранить в файл.
    
    Parameters:
    - shape_type: Тип фигуры (cube, sphere, cylinder)
    - size: Размер фигуры в мм
    - x, y, z: Координаты центра фигуры (в мм)
    - file_name: Имя файла (если None, будет сгенерировано автоматически)
    """
    # Валидация параметров
    if size <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Размер должен быть положительным числом"
        )
    valid_shapes = ["cube", "sphere", "cylinder"]
    if shape_type.lower() not in valid_shapes:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип фигуры. Доступно: {', '.join(valid_shapes)}"
        )
    if not file_name:
        import uuid
        file_name = f"test_{shape_type}_{size}mm_{uuid.uuid4().hex[:8]}.FCStd"
    elif not file_name.lower().endswith('.fcstd'):
        raise HTTPException(
            status_code=400,
            detail="Файл должен иметь расширение .FCStd"
        )
    
    try:
        open_result = await core.open_document(file_name)
        create_result = await core.create_simple_shape(
            shape_type.lower(), 
            size,
            x,
            y,
            z
        )
        save_result = await core.save_document(file_name)
        close_result = await core.close_document()
        return {
            "success": True,
            "result": "Тестовая фигура создана и сохранена успешно",
            "details": {
                "file": file_name,
                "shape_type": shape_type,
                "size": size,
                "coordinates": {"x": x, "y": y, "z": z},
                "open_result": open_result,
                "create_result": create_result,
                "save_result": save_result,
                "close_result": close_result
            },
            "message": (
                f"✅ Файл создан: {file_name}\n"
                f"📐 Тип фигуры: {shape_type}\n"
                f"📏 Размер: {size} мм\n"
                f"📍 Координаты: ({x}, {y}, {z}) мм\n"
                f"📄 Открытие документа: {open_result}\n"
                f"🎯 Создание фигуры: {create_result}\n"
                f"💾 Сохранение: {save_result}\n"
                f"🚪 Закрытие: {close_result}"
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании тестовой фигуры: {str(e)}"
        )
    
@app.post("/api/agent/query")
async def agent_query(query_request: dict):
    """
    Обработка запроса через AI агента с выполнением команд.
    
    Пример тела запроса:
    {
        "query": "Создай куб размером 20мм"
    }
    """
    try:
        query = query_request.get("query", "").strip()
        
        if not query:
            return {
                "success": False,
                "error": "Запрос не может быть пустым"
            }
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            return {
                "success": False,
                "error": "OPENROUTER_API_KEY не найден в .env"
            }
        
        # 1. Получаем ответ от LLM
        system_prompt = """Ты - AI ассистент для CAD системы FreeCAD.

        Доступные команды и их параметры:
        1. create_test_shape(shape_type='cube', size=20, file_name=None) - создать тестовую фигуру
        2. get_mcp_status() - проверить статус MCP сервера
        3. get_documents() - получить список документов
        4. open_document(file_path='test.FCStd') - открыть документ
        5. create_shape(shape_type='cube', size=20, x=0, y=0, z=0) - создать фигуру в документе
        6. save_document(file_path=None) - сохранить документ
        7. close_document() - закрыть документ

        ВАЖНО: При создании фигур (create_shape) всегда сначала открывай документ, 
        затем создавай фигуру, затем сохраняй и закрывай документ.
        
        Ответь ТОЛЬКО в формате JSON:
        {{
            "command": "имя_команды",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }},
            "explanation": "Краткое объяснение на русском",
            "requires_document": true/false
        }}

        Если команда не требует параметров, оставь "parameters": {{}}.
        Поле "requires_document": true для команд, требующих открытого документа."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8001"
        }
        
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt.format(query=query)},
                {"role": "user", "content": query}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"OpenRouter error: {response.status_code}",
                    "details": response.text[:200]
                }
            
            data = response.json()
            llm_response = data["choices"][0]["message"]["content"]
            
            # 2. Пытаемся распарсить JSON ответ LLM
            import json as json_lib
            try:
                # Убираем возможные лишние символы
                cleaned_response = llm_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:-3].strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:-3].strip()
                
                command_data = json_lib.loads(cleaned_response)
                command = command_data.get("command")
                parameters = command_data.get("parameters", {})
                explanation = command_data.get("explanation", "")
                requires_document = command_data.get("requires_document", False)
                
            except (json_lib.JSONDecodeError, KeyError):
                # Если не удалось распарсить, возвращаем только текст
                return {
                    "success": True,
                    "query": query,
                    "result": llm_response,
                    "executed": False,
                    "note": "Не удалось распознать команду для выполнения"
                }
            
            # 3. Выполняем команду через MCP сервер
            mcp_results = []
            
            # Функция для работы с документами
            async def handle_document_operations(command_type, cmd_params):
                """Обработка команд, требующих работы с документом"""
                import uuid
                
                # Определяем имя файла
                file_name = parameters.get("file_name", f"auto_{command_type}_{uuid.uuid4().hex[:8]}.FCStd")
                
                # Шаг 1: Открываем документ
                open_result = await client.get(
                    "http://localhost:8001/api/cad/open-document",
                    params={"file_path": file_name}
                )
                mcp_results.append({"open_document": open_result.json()})
                
                # Шаг 2: Выполняем команду создания
                if command_type == "create_shape":
                    create_result = await client.get(
                        "http://localhost:8001/api/cad/create-shape",
                        params=cmd_params
                    )
                    mcp_results.append({"create_shape": create_result.json()})
                elif command_type == "create_test_shape":
                    create_result = await client.get(
                        "http://localhost:8001/api/cad/create-test-shape",
                        params=cmd_params
                    )
                    mcp_results.append({"create_test_shape": create_result.json()})
                
                # Шаг 3: Сохраняем документ
                save_result = await client.get(
                    "http://localhost:8001/api/cad/save-document",
                    params={"file_path": file_name}
                )
                mcp_results.append({"save_document": save_result.json()})
                
                # Шаг 4: Закрываем документ
                close_result = await client.get("http://localhost:8001/api/cad/close-document")
                mcp_results.append({"close_document": close_result.json()})
                
                return file_name
            
            if command == "create_test_shape":
                # Проверяем параметры
                shape_type = parameters.get("shape_type", "cube")
                size = parameters.get("size", 20)
                file_name = parameters.get("file_name")
                
                mcp_params = {"shape_type": shape_type, "size": size}
                if file_name:
                    mcp_params["file_name"] = file_name
                
                file_used = await handle_document_operations("create_test_shape", mcp_params)
                
            elif command == "get_mcp_status":
                mcp_response = await client.get("http://localhost:8001/api/mcp/status")
                mcp_results.append(mcp_response.json())
                
            elif command == "get_documents":
                mcp_response = await client.get("http://localhost:8001/api/cad/documents")
                mcp_results.append(mcp_response.json())
                
            elif command == "open_document":
                file_path = parameters.get("file_path", "test.FCStd")
                mcp_response = await client.get(
                    "http://localhost:8001/api/cad/open-document",
                    params={"file_path": file_path}
                )
                mcp_results.append(mcp_response.json())
                
            elif command == "create_shape" or requires_document:
                shape_type = parameters.get("shape_type", "cube")
                size = parameters.get("size", 20)
                x = parameters.get("x", 0)
                y = parameters.get("y", 0)
                z = parameters.get("z", 0)
                
                cmd_params = {
                    "shape_type": shape_type,
                    "size": size,
                    "x": x,
                    "y": y,
                    "z": z
                }
                
                file_used = await handle_document_operations("create_shape", cmd_params)
                
            elif command == "save_document":
                file_path = parameters.get("file_path")
                mcp_params = {}
                if file_path:
                    mcp_params["file_path"] = file_path
                mcp_response = await client.get(
                    "http://localhost:8001/api/cad/save-document",
                    params=mcp_params
                )
                mcp_results.append(mcp_response.json())
                
            elif command == "close_document":
                mcp_response = await client.get("http://localhost:8001/api/cad/close-document")
                mcp_results.append(mcp_response.json())
                
            else:
                return {
                    "success": True,
                    "query": query,
                    "result": llm_response,
                    "executed": False,
                    "note": f"Команда '{command}' не поддерживается для автоматического выполнения"
                }
            
            # 4. Формируем финальный ответ
            result_data = {
                "success": True,
                "query": query,
                "llm_response": llm_response,
                "command": command,
                "parameters": parameters,
                "explanation": explanation,
                "executed": True,
                "mcp_results": mcp_results,
            }
            
            # Добавляем информацию о файле, если он был создан
            if command in ["create_shape", "create_test_shape"] or requires_document:
                result_data["file_created"] = file_used if 'file_used' in locals() else "Неизвестный файл"
                result_data["full_response"] = (
                    f"{explanation}\n\n"
                    f"Файл: {file_used if 'file_used' in locals() else 'Неизвестный'}\n"
                    f"Результат выполнения:\n{mcp_results}"
                )
            else:
                result_data["full_response"] = f"{explanation}\n\nРезультат выполнения:\n{mcp_results}"
            
            return result_data
            
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Ошибка обработки: {str(e)}",
            "traceback": traceback.format_exc(),
            "query": query_request.get("query", "")
        }
@app.get("/api/agent/help")
async def agent_help():
    """Получить справку по использованию агента."""
    return {
        "endpoint": "/api/agent/query",
        "method": "POST",
        "description": "Обработка запросов на естественном языке через AI агента",
        "example_request": {
            "query": "Создай куб размером 20мм в новом файле test_cube.FCStd"
        },
        "available_operations": [
            "Создание простых фигур (куб, сфера, цилиндр)",
            "Создание сложных фигур (звезда, шестеренка, тор)",
            "Открытие/сохранение/закрытие документов",
            "Проверка статуса системы",
            "Получение списка документов"
        ]
    }

if __name__ == "__main__":
    # Запуск MCP сервера в отдельном потоке
    mcp_thread = threading.Thread(target=lambda: mcp.run(transport="streamable-http", host="0.0.0.0", port=8000), daemon=True)
    mcp_thread.start()

    print("=" * 60)
    print("FreeCAD FastAPI Server запущен")
    print("MCP Server запущен на порту 8000")
    print("=" * 60)
    print("Swagger UI: http://localhost:8001/docs")
    print("Тест документов: http://localhost:8001/api/cad/documents")
    print("Создать куб 15мм: http://localhost:8001/api/cad/create-shape?shape_type=cube&size=15")
    print("Создать сферу 20мм: http://localhost:8001/api/cad/create-shape?shape_type=sphere&size=20")
    print("Создать тор: http://localhost:8001/api/cad/create-complex-shape?shape_type=torus&major_radius=30&minor_radius=10")
    print("Создать звезду: http://localhost:8001/api/cad/create-complex-shape?shape_type=star&num_points=5&inner_radius=10&outer_radius=20&height=5")
    print("Создать шестеренку: http://localhost:8001/api/cad/create-complex-shape?shape_type=gear&teeth=12&module=2&outer_radius=20&height=5")
    print("Создать тестовый куб: http://localhost:8001/api/cad/create-test-shape?shape_type=cube&size=15")
    print("Создать тестовую сферу: http://localhost:8001/api/cad/create-test-shape?shape_type=sphere&size=20&x=10&y=10&z=10")
    print("Создать тестовый цилиндр: http://localhost:8001/api/cad/create-test-shape?shape_type=cylinder&size=10&size=25&file_name=my_cylinder.FCStd")
    print("Статус MCP: http://localhost:8001/api/mcp/status")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001)