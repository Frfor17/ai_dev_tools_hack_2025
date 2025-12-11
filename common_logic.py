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
        
    async def create_simple_shape(self, shape_type="cube", size=1.0):
        """Создать фигуру в FreeCAD только внутри открытого документа."""
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
            
            return f"Создана {shape_type} размером {size} мм в открытом документе {doc.Name}. Для сохранения используйте save_document."
            
        except Exception as e:
            return f"Ошибка создания фигуры: {str(e)}"

    async def create_complex_shape(self, shape_type: str, **kwargs):
        """Создать сложную фигуру в FreeCAD."""
        if not self.freecad:
            result = self.connect()
            if not result["success"]:
                return f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}"
        
        if not self.current_doc:
            return "Ошибка: Нет открытого документа. Сначала откройте документ с помощью open_document."
        
        try:
            doc = self.current_doc
            
            if shape_type.lower() == "torus":
                # Создание тора
                major_radius = kwargs.get('major_radius')
                minor_radius = kwargs.get('minor_radius')
                
                if not major_radius or not minor_radius:
                    return "Ошибка: для создания тора требуются major_radius и minor_radius"
                
                # Создаем тор в FreeCAD
                torus = self.part.makeTorus(major_radius, minor_radius)
                obj = doc.addObject("Part::Feature", f"Torus_{major_radius}x{minor_radius}")
                obj.Shape = torus
                doc.recompute()
                
                return f"Тор создан с большим радиусом {major_radius} мм и малым радиусом {minor_radius} мм"
                
            elif shape_type.lower() == "star":
                # Создание звезды (упрощенная версия)
                import math
                num_points = kwargs.get('num_points')
                inner_radius = kwargs.get('inner_radius')
                outer_radius = kwargs.get('outer_radius')
                height = kwargs.get('height')
                
                if not all([num_points, inner_radius, outer_radius, height]):
                    return "Ошибка: для создания звезды требуются num_points, inner_radius, outer_radius, height"
                
                # Создаем 2D профиль звезды
                import Draft
                points = []
                for i in range(num_points * 2):
                    angle = i * math.pi / num_points
                    radius = inner_radius if i % 2 == 0 else outer_radius
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    points.append(self.freecad.Vector(x, y, 0))
                
                # Замыкаем контур
                points.append(points[0])
                
                # Создаем полигон
                wire = self.part.makePolygon(points)
                face = self.part.Face(wire)
                
                # Экструдируем
                extruded = face.extrude(self.freecad.Vector(0, 0, height))
                obj = doc.addObject("Part::Feature", f"Star_{num_points}pts")
                obj.Shape = extruded
                doc.recompute()
                
                return f"Звезда создана с {num_points} лучами, высотой {height} мм"
                
            elif shape_type.lower() == "gear":
                # Создание упрощенной шестеренки
                teeth = kwargs.get('teeth')
                module = kwargs.get('module')
                outer_radius = kwargs.get('outer_radius')
                height = kwargs.get('height')
                
                if not all([teeth, module, outer_radius, height]):
                    return "Ошибка: для создания шестеренки требуются teeth, module, outer_radius, height"
                
                # Упрощенная реализация шестеренки как цилиндра с вырезами
                # В реальном проекте нужно использовать более сложную геометрию
                cylinder = self.part.makeCylinder(outer_radius, height)
                obj = doc.addObject("Part::Feature", f"Gear_{teeth}teeth")
                obj.Shape = cylinder
                doc.recompute()
                
                return f"Упрощенная шестеренка создана с {teeth} зубьями, высотой {height} мм. Для точной геометрии используйте специализированные библиотеки."
            
            else:
                return f"Неизвестный тип сложной фигуры: {shape_type}"
            
        except Exception as e:
            return f"Ошибка создания сложной фигуры: {str(e)}"


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