import sys
import os

class FreeCADCore:
    """Минимальный клиент для работы с FreeCAD."""
    
    def __init__(self, freecad_path=None):
        self.freecad_path = freecad_path or r'C:\Program Files\FreeCAD 1.0\bin'
        self.freecad = None
        self.part = None
        self.current_doc = None

    async def open_document(self, file_path: str):
        """Открыть существующий документ FreeCAD или создать новый если не существует."""
        if not self.freecad:
            result = self.connect()
            if not result["success"]:
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        import os
        
        try:
            if self.current_doc:
                self.freecad.closeDocument(self.current_doc.Name)
                self.current_doc = None
            
            if not file_path.lower().endswith('.fcstd'):
                return "Ошибка: Файл должен иметь расширение .FCStd"
            
            if os.path.exists(file_path):
                self.current_doc = self.freecad.openDocument(file_path)
                return f"Документ открыт: {self.current_doc.Name}"
            else:
                # Создать новый документ
                doc_name = os.path.splitext(os.path.basename(file_path))[0]
                self.current_doc = self.freecad.newDocument(doc_name)
                # Сохранить сразу, чтобы файл существовал
                self.current_doc.saveAs(file_path)
                return f"Создан новый документ и сохранен по пути: {file_path}. Теперь открыт: {self.current_doc.Name}"
        
        except Exception as e:
            return f"Ошибка открытия/создания документа: {str(e)}"

    async def save_document(self, file_path: str = None):
        """Сохранить текущий документ FreeCAD."""
        if not self.current_doc:
            return "Нет открытого документа для сохранения"
        
        try:
            if file_path:
                self.current_doc.saveAs(file_path)
                return f"Документ сохранен как: {file_path}"
            else:
                self.current_doc.save()
                return "Документ сохранен"
        except Exception as e:
            return f"Ошибка сохранения документа: {str(e)}"

    async def close_document(self):
        """Закрыть текущий документ FreeCAD."""
        if not self.current_doc:
            return "Нет открытого документа для закрытия"
        
        try:
            self.freecad.closeDocument(self.current_doc.Name)
            self.current_doc = None
            return "Документ закрыт"
        except Exception as e:
            return f"Ошибка закрытия документа: {str(e)}"
        
    def connect(self):
        """Подключение к FreeCAD."""
        # 1. Добавляем путь
        if self.freecad_path not in sys.path:
            sys.path.append(self.freecad_path)
        
        # 2. Пытаемся импортировать
        try:
            import FreeCAD
            import Part
            
            self.freecad = FreeCAD
            self.part = Part
            
            return {
                "success": True,
                "version": '.'.join(map(str, FreeCAD.Version()[0:3])),
                "message": f"✅ FreeCAD загружен"
            }
            
        except ImportError as e:
            return {
                "success": False,
                "error": f"Ошибка импорта: {e}",
                "suggestion": "Проверьте путь к FreeCAD"
            }
    
    async def get_onshape_documents(self):
        """Метод для совместимости с FastAPI кодом."""
        # Сначала подключаемся, если ещё не подключены
        if not self.freecad:
            result = self.connect()
            if not result["success"]:
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        try:
            # Получаем документы из FreeCAD
            docs = []
            for doc in self.freecad.listDocuments().values():
                docs.append({
                    "name": doc.Name,
                    "object_count": len(doc.Objects)
                })
            
            if docs:
                return f"Документы FreeCAD: {docs}"
            else:
                return "Нет открытых документов"
                
        except Exception as e:
            return f"Ошибка получения документов: {str(e)}"
        
    async def create_simple_shape(self, shape_type="cube", size=1.0, x=0.0, y=0.0, z=0.0):
        """Создать фигуру в FreeCAD только внутри открытого документа с указанными координатами."""
        # Сначала подключаемся, если ещё не подключены
        if not self.freecad:
            result = self.connect()
            if not result["success"]:
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        if not self.current_doc:
            return "Ошибка: Нет открытого документа. Сначала откройте документ с помощью open_document."
        
        try:
            doc = self.current_doc
            
            if shape_type.lower() == "cube":
                # Для куба координаты указывают его начальную точку (один из углов)
                shape = self.part.makeBox(size, size, size, self.freecad.Vector(x, y, z))
                obj_name = f"Cube_{size}mm_{x}_{y}_{z}"
            elif shape_type.lower() == "sphere":
                # Для сферы координаты указывают центр
                shape = self.part.makeSphere(size/2, self.freecad.Vector(x, y, z))
                obj_name = f"Sphere_{size}mm_{x}_{y}_{z}"
            elif shape_type.lower() == "cylinder":
                # Для цилиндра координаты указывают центр основания
                shape = self.part.makeCylinder(size/2, size, self.freecad.Vector(x, y, z))
                obj_name = f"Cylinder_{size}mm_{x}_{y}_{z}"
            else:
                return f"Неизвестный тип фигуры: {shape_type}. Доступно: cube, sphere, cylinder"
            
            # Добавляем объект в документ
            obj = doc.addObject("Part::Feature", obj_name)
            obj.Shape = shape
            doc.recompute()
            
            return f"Создана {shape_type} размером {size} мм в точке ({x}, {y}, {z}) в документе {doc.Name}."
            
        except Exception as e:
            return f"Ошибка создания фигуры: {str(e)}"

    def create_rectangle_sketch(self, width=10.0, height=5.0):
        """Создать простой прямоугольный скетч."""
        if not self.freecad:
            return {"success": False, "error": "FreeCAD не подключен"}
        
        try:
            # Импортируем нужные модули
            import Part
            import Sketcher
            
            # Создаём новый документ
            doc = self.freecad.newDocument("SketchDocument")
            
            # Создаём тело для скетча
            body = doc.addObject('PartDesign::Body', 'Body')
            
            # Создаём скетч
            sketch = doc.addObject('Sketcher::SketchObject', 'RectangleSketch')
            sketch.Support = (doc.XY_Plane, [''])
            sketch.MapMode = 'FlatFace'
            body.addObject(sketch)
            
            # Создаём прямоугольник в скетче
            p1 = self.freecad.Vector(-width/2, -height/2, 0)
            p2 = self.freecad.Vector(width/2, -height/2, 0)
            p3 = self.freecad.Vector(width/2, height/2, 0)
            p4 = self.freecad.Vector(-width/2, height/2, 0)
            
            # Добавляем линии прямоугольника
            sketch.addGeometry(Part.LineSegment(p1, p2), False)
            sketch.addGeometry(Part.LineSegment(p2, p3), False)
            sketch.addGeometry(Part.LineSegment(p3, p4), False)
            sketch.addGeometry(Part.LineSegment(p4, p1), False)
            
            # Добавляем горизонтальные и вертикальные ограничения
            sketch.addConstraint(Sketcher.Constraint('Horizontal', 0))
            sketch.addConstraint(Sketcher.Constraint('Horizontal', 2))
            sketch.addConstraint(Sketcher.Constraint('Vertical', 1))
            sketch.addConstraint(Sketcher.Constraint('Vertical', 3))
            
            # Добавляем размеры
            sketch.addConstraint(Sketcher.Constraint('DistanceX', 1, 1, 1, 2, width))
            sketch.addConstraint(Sketcher.Constraint('DistanceY', 0, 1, 0, 2, height))
            
            # Добавляем равенство противоположных сторон
            sketch.addConstraint(Sketcher.Constraint('Equal', 0, 2))
            sketch.addConstraint(Sketcher.Constraint('Equal', 1, 3))
            
            # Фиксируем центр в точке (0,0)
            sketch.addConstraint(Sketcher.Constraint('Symmetric', 1, 1, 0, 1, -1))
            
            doc.recompute()
            
            # Сохраняем
            filename = f"sketch_rectangle_{width}x{height}.FCStd"
            doc.saveAs(filename)
            
            return {
                "success": True,
                "document": doc.Name,
                "sketch": sketch.Name,
                "width": width,
                "height": height,
                "file": filename,
                "message": f"✅ Создан скетч прямоугольника {width}x{height} мм"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка создания скетча: {str(e)}"
            }

    def create_cube(self, size=10.0, doc_name="TestDocument", x=0.0, y=0.0, z=0.0):
        """Создать куб в указанных координатах."""
        if not self.freecad or not self.part:
            return {"success": False, "error": "FreeCAD не подключен"}
        
        try:
            # Создаём новый документ
            doc = self.freecad.newDocument(doc_name)
            
            # Создаём куб в указанных координатах
            cube = self.part.makeBox(size, size, size, self.freecad.Vector(x, y, z))
            
            # Добавляем объект в документ
            obj = doc.addObject("Part::Feature", f"Cube_{size}mm_{x}_{y}_{z}")
            obj.Shape = cube
            doc.recompute()
            
            # Сохраняем для проверки
            test_file = f"test_cube_{size}_at_{x}_{y}_{z}.FCStd"
            doc.saveAs(test_file)
            
            return {
                "success": True,
                "document": doc.Name,
                "object": obj.Name,
                "volume": cube.Volume,
                "position": {"x": x, "y": y, "z": z},
                "file": test_file,
                "message": f"✅ Создан куб {size}x{size}x{size} мм в точке ({x}, {y}, {z})"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка создания: {str(e)}"
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
        test_result = self.create_cube(10, "TestDocument", 5, 5, 5)
        
        if test_result["success"]:
            print(f"\n🎉 ВСЁ РАБОТАЕТ!")
            print(f"   Документ: {test_result['document']}")
            print(f"   Объём куба: {test_result['volume']:.2f} мм³")
            print(f"   Позиция: ({test_result['position']['x']}, {test_result['position']['y']}, {test_result['position']['z']})")
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