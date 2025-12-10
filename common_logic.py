import sys
import os

class FreeCADCore:
    """Минимальный клиент для работы с FreeCAD."""
    
    def __init__(self, freecad_path=None):
        self.freecad_path = freecad_path or r'C:\Program Files\FreeCAD 1.0\bin'
        self.freecad = None
        self.part = None
        
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
        
    async def create_simple_shape(self, shape_type="cube", size=1.0):
        """Создать фигуру в FreeCAD."""
        # Сначала подключаемся, если ещё не подключены
        if not self.freecad:
            result = self.connect()
            if not result["success"]:
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        try:
            # Создаём документ
            doc = self.freecad.newDocument(f"{shape_type}_{size}")
            
            if shape_type.lower() == "cube":
                shape = self.part.makeBox(size, size, size)
                obj_name = f"Cube_{size}mm"
            elif shape_type.lower() == "sphere":
                shape = self.part.makeSphere(size/2)
                obj_name = f"Sphere_{size}mm"
            elif shape_type.lower() == "cylinder":
                shape = self.part.makeCylinder(size/2, size)
                obj_name = f"Cylinder_{size}mm"
            else:
                return f"Неизвестный тип фигуры: {shape_type}. Доступно: cube, sphere, cylinder"
            
            # Добавляем объект в документ
            obj = doc.addObject("Part::Feature", obj_name)
            obj.Shape = shape
            doc.recompute()
            
            # Сохраняем файл
            filename = f"{obj_name}.FCStd"
            doc.saveAs(filename)
            
            return f"Создана {shape_type} размером {size} мм. Файл: {filename}"
            
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
            # Точки прямоугольника: (x1, y1), (x2, y2)
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