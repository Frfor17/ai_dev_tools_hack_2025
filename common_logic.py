import sys
import os
import logging

logger = logging.getLogger(__name__)

class FreeCADCore:
    """Минимальный клиент для работы с FreeCAD."""
    
    def __init__(self, freecad_path=None):
        #   init короче это функция базовая для всех классов, она используется, когда создаёшь объект этого класса
        #    freecad_path = путь к FreeCAD, или если не указан,
        #    то по умолчанию 'C:\Program Files\FreeCAD  1.0\bin'
        self.freecad_path = freecad_path or r'C:\Program Files\FreeCAD  1.0\bin' # где нахуй путь фрикада и почему мне показывает тут ошибку? где ебанный фрикад, тут же указан путь, чё он не пашет
        # Пока мы НЕ подключены к FreeCAD, эти переменные = None
        self.freecad = None # будущий модуль free cad
        self.part = None  # будущий модуль Part
        
    def connect(self):       # self это про себя
        """Подключение к FreeCAD."""
        logger.info(f"Connecting to FreeCAD at {self.freecad_path}") # self.freecad_path - это путь к фрикаду
        
        # 1. Добавляем путь
        if self.freecad_path not in sys.path:
            logger.info(f"Adding FreeCAD path to sys.path: {self.freecad_path}")
            sys.path.append(self.freecad_path)
        
        # 2. Пытаемся импортировать
        try:
            logger.info("Importing FreeCAD...")
            import FreeCAD
            import Part
            logger.info("FreeCAD imported successfully")
            
            self.freecad = FreeCAD
            self.part = Part
            
            version = '.'.join(map(str, FreeCAD.Version()[0:3]))
            logger.info(f"FreeCAD version: {version}")
            
            return {
                "success": True,
                "version": version,
                "message": f"✅ FreeCAD загружен"
            }
            
        except ImportError as e:
            logger.error(f"Failed to import FreeCAD: {e}")
            return {
                "success": False,
                "error": f"Ошибка импорта: {e}",
                "suggestion": "Проверьте путь к FreeCAD"
            }
    
    async def get_onshape_documents(self):
        """Метод для совместимости с FastAPI кодом."""
        logger.info("get_onshape_documents called")
        
        # Сначала подключаемся, если ещё не подключены
        if not self.freecad:
            logger.info("FreeCAD not connected, calling connect()")
            result = self.connect()
            if not result["success"]:
                logger.error(f"Connection failed: {result.get('error', 'Unknown error')}")
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        try:
            logger.info("Getting FreeCAD documents...")
            # Получаем документы из FreeCAD
            docs = []
            for doc in self.freecad.listDocuments().values():
                docs.append({
                    "name": doc.Name,
                    "object_count": len(doc.Objects)
                })
            
            logger.info(f"Found {len(docs)} documents")
            if docs:
                return f"Документы FreeCAD: {docs}"
            else:
                return "Нет открытых документов"
                
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return f"Ошибка получения документов: {str(e)}"
        
    async def create_simple_shape(self, shape_type="cube", size=1.0):
        """Создать фигуру в FreeCAD."""
        logger.info(f"create_simple_shape called with shape_type={shape_type}, size={size}")
        
        # Сначала подключаемся, если ещё не подключены
        if not self.freecad:
            logger.info("FreeCAD not connected, calling connect()")
            result = self.connect()
            if not result["success"]:
                logger.error(f"Connection failed: {result.get('error', 'Unknown error')}")
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        try:
            logger.info(f"Creating FreeCAD document: {shape_type}_{size}")
            # Создаём документ
            doc = self.freecad.newDocument(f"{shape_type}_{size}")
            
            if shape_type.lower() == "cube":
                logger.info("Creating cube")
                shape = self.part.makeBox(size, size, size)
                obj_name = f"Cube_{size}mm"
            elif shape_type.lower() == "sphere":
                logger.info("Creating sphere")
                shape = self.part.makeSphere(size/2)
                obj_name = f"Sphere_{size}mm"
            elif shape_type.lower() == "cylinder":
                logger.info("Creating cylinder")
                shape = self.part.makeCylinder(size/2, size)
                obj_name = f"Cylinder_{size}mm"
            else:
                logger.error(f"Unknown shape type: {shape_type}")
                return f"Неизвестный тип фигуры: {shape_type}. Доступно: cube, sphere, cylinder"
            
            # Добавляем объект в документ
            logger.info(f"Adding object to document: {obj_name}")
            obj = doc.addObject("Part::Feature", obj_name)
            obj.Shape = shape
            doc.recompute()
            
            # Сохраняем файл
            filename = f"{obj_name}.FCStd"
            logger.info(f"Saving file: {filename}")
            doc.saveAs(filename)
            
            logger.info(f"Shape created successfully: {shape_type} {size}mm")
            return f"Создана {shape_type} размером {size} мм. Файл: {filename}"
            
        except Exception as e:
            logger.error(f"Error creating shape: {str(e)}")
            return f"Ошибка создания фигуры: {str(e)}"


    def create_cube(self, size=10.0, doc_name="TestDocument"):
        """Создать куб."""
        if not self.freecad or not self.part:
            return {"success": False, "error": "FreeCAD не подключен"}
        
        try:
            # Создаём новый документ
            doc = self.freecad.newDocument(doc_name)
            
            # Создаём куб
            cube = self.part.makeBox(size, size, size)
            
            # Добавляем объект в документ
            obj = doc.addObject("Part::Feature", f"Cube_{size}mm")
            obj.Shape = cube
            doc.recompute()
            
            # Сохраняем для проверки
            test_file = f"test_cube_{size}.FCStd"
            doc.saveAs(test_file)
            
            return {
                "success": True,
                "document": doc.Name,
                "object": obj.Name,
                "volume": cube.Volume,
                "file": test_file,
                "message": f"✅ Создан куб {size}x{size}x{size} мм"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка создания: {str(e)}"
            }
    
    def create_assemble(self, assembly_name="MyRobotAssembly", create_default_parts=True):
        """
        Создаёт новый документ FreeCAD и добавляет в него объект сборки.
        
        Args:
            assembly_name (str): Имя создаваемой сборки и документа.
            create_default_parts (bool): Создать ли стандартные детали (куб, цилиндр, сфера)
            
        Returns:
            dict: Результат операции с полями 'success', 'message', 'document' и 'assembly'.
        """
        try:
            # АВТОМАТИЧЕСКОЕ ПОДКЛЮЧЕНИЕ, как в create_simple_shape
            if not self.freecad:
                logger.info("FreeCAD not connected, calling connect()")
                result = self.connect()
                if not result["success"]:
                    logger.error(f"Connection failed: {result.get('error', 'Unknown error')}")
                    return {
                        "success": False,
                        "message": f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}",
                        "document": None,
                        "assembly": None,
                        "parts": []
                    }
            # Используем уже подключённые self.freecad и self.part
            if not self.freecad or not self.part:
                return {
                    "success": False,
                    "message": "FreeCAD не подключен. Сначала вызовите connect().",
                    "document": None,
                    "assembly": None,
                    "parts": []
                }
            
            # Создаём новый документ
            doc = self.freecad.newDocument(assembly_name)
            
            # Добавляем объект Модели (App::Part) - это контейнер сборки
            assembly = doc.addObject("App::Part", "Assembly")
            assembly.Label = assembly_name
            
            parts_list = []
            
            # Создаём стандартные детали, если нужно
            if create_default_parts:
                # Создаём базовые детали
                default_parts = [
                    {"type": "Box", "name": "Base", "length": 20, "width": 15, "height": 5},
                    {"type": "Cylinder", "name": "Shaft", "radius": 3, "height": 30},
                    {"type": "Sphere", "name": "Joint", "radius": 8}
                ]
                
                for part_info in default_parts:
                    try:
                        if part_info["type"] == "Box":
                            part = doc.addObject("Part::Box", part_info["name"])
                            part.Length = part_info["length"]
                            part.Width = part_info["width"]
                            part.Height = part_info["height"]
                        elif part_info["type"] == "Cylinder":
                            part = doc.addObject("Part::Cylinder", part_info["name"])
                            part.Radius = part_info["radius"]
                            part.Height = part_info["height"]
                        elif part_info["type"] == "Sphere":
                            part = doc.addObject("Part::Sphere", part_info["name"])
                            part.Radius = part_info["radius"]
                        
                        # Добавляем деталь в сборку
                        assembly.addObject(part)
                        parts_list.append(part_info["name"])
                        
                    except Exception as part_error:
                        print(f"Ошибка при создании детали {part_info['name']}: {part_error}")
            
            # Делаем сборку активным объектом
            doc.recompute()
            
            return {
                "success": True,
                "message": f"Сборка '{assembly_name}' успешно создана" +
                        (f" с {len(parts_list)} деталями" if parts_list else ""),
                "document": doc.Name,
                "assembly": assembly.Name,
                "parts": parts_list
            }
        
        except Exception as e:
            error_msg = f"Ошибка при создании сборки: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "document": None,
                "assembly": None,
                "parts": []
            }


    def test_connection(self):
        """Полный тест подключения (твой оригинальный код)."""
        print(f"🔍 Проверяем путь: {self.freecad_path}")
        print(f"   Папка существует: {'✅' if os.path.exists(self.freecad_path) else '❌'}")
        
        # Подключаемся
        result = self.connect()
        
        if not result["success"]:
            print(f"\n❌ {result['error']}")
            print("\nВозможные причины:")
            print("1. Неправильный путь - проверьте C:\\Program Files\\FreeCAD 1.0\\bin")
            print("2. FreeCAD требует дополнительные DLL - запустите FreeCAD отдельно один раз")
            return result
        
        print(f"\n✅ УСПЕХ! FreeCAD {result['version']} загружен")
        
        # Тестируем создание куба
        test_result = self.create_cube(10, "TestDocument")
        
        if test_result["success"]:
            print(f"\n🎉 ВСЁ РАБОТАЕТ!")
            print(f"   Документ: {test_result['document']}")
            print(f"   Объём куба: {test_result['volume']:.2f} мм³")
            print(f"   Файл: {test_result['file']}")
        else:
            print(f"\n⚠️  Подключение есть, но создание не работает:")
            print(f"   Ошибка: {test_result['error']}")
        
        return {**result, **test_result}

# Глобальный экземпляр для простоты
core = FreeCADCore()

if __name__ == "__main__":
    # Если запускаем этот файл отдельно - тестируем
    core.test_connection()