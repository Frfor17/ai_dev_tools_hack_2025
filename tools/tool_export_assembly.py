import FreeCAD as App
import FreeCADGui as Gui
import Mesh
import Part
import os

@mcp.tool()
def export_assembly_tool(
    assembly_name: str,
    file_path: str,
    export_format: str = "STEP",
    export_mode: str = "assembly"
):
    """MCP-инструмент для экспорта сборки в различные форматы."""
    result = export_assembly(assembly_name, file_path, export_format, export_mode)
    return result  # Структурированный ответ


def export_assembly(assembly_name, file_path, export_format="STEP", export_mode="assembly"):
    """
    Экспортирует сборку или её детали в файл указанного формата.
    
    Args:
        assembly_name (str): Имя объекта сборки (App::Part с Type="Assembly").
        file_path (str): Полный путь для сохранения файла (включая расширение).
        export_format (str): Формат экспорта: "STEP", "STL", "IGES", "OBJ", "SVG" (для чертежей TechDraw).
        export_mode (str): Режим экспорта:
                           - "assembly": одна сборка как единое целое (для STEP/IGES).
                           - "parts": каждая деталь в отдельный файл (только для STL/OBJ).
                           - "exploded": все детали в один файл (для STL/OBJ).
    
    Returns:
        dict: Детальный отчёт об операции экспорта.
    """
    try:
        doc = App.ActiveDocument
        if not doc:
            return {
                "success": False,
                "message": "Нет активного документа FreeCAD.",
                "exported_file": None,
                "format": export_format
            }

        # 1. Находим сборку
        assembly = doc.getObject(assembly_name)
        if not assembly:
            return {
                "success": False,
                "message": f"Сборка '{assembly_name}' не найдена в документе.",
                "exported_file": None,
                "format": export_format
            }

        # 2. Подготавливаем путь и проверяем расширение
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir)  # Создаём каталог, если его нет

        base_name, _ = os.path.splitext(file_path)
        exported_files = []  # Список созданных файлов

        # 3. В зависимости от формата и режима выполняем экспорт
        if export_format.upper() == "STEP":
            # STEP поддерживает сборки как единое целое
            if not file_path.lower().endswith('.step') and not file_path.lower().endswith('.stp'):
                file_path = base_name + '.step'
            
            # Собираем список всех деталей в сборке для экспорта
            shapes_to_export = []
            for obj in assembly.OutListRecursive:
                if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                    shapes_to_export.append(obj.Shape)
            
            # Создаём составную форму (Compound) из всех деталей
            compound = Part.makeCompound(shapes_to_export)
            compound.exportStep(file_path)
            exported_files.append(file_path)
            
            message = f"Сборка экспортирована в STEP: {file_path}"

        elif export_format.upper() == "STL":
            # Для STL определяем режим экспорта
            if export_mode == "assembly":
                # Все детали как один файл STL
                if not file_path.lower().endswith('.stl'):
                    file_path = base_name + '.stl'
                
                mesh = Mesh.Mesh()
                for obj in assembly.OutListRecursive:
                    if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                        mesh.addMesh(Mesh.Mesh(obj.Shape.tessellate(0.1)))
                
                mesh.save(file_path)
                exported_files.append(file_path)
                message = f"Сборка экспортирована как единый STL: {file_path}"

            elif export_mode == "parts":
                # Каждая деталь в отдельный файл
                for obj in assembly.OutListRecursive:
                    if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                        part_file = os.path.join(file_dir, f"{obj.Name}.stl")
                        Mesh.export([obj], part_file)
                        exported_files.append(part_file)
                
                message = f"Детали экспортированы в отдельные STL файлы: {len(exported_files)} файлов"

            elif export_mode == "exploded":
                # Все детали в один файл STL (но разделённые)
                if not file_path.lower().endswith('.stl'):
                    file_path = base_name + '.stl'
                
                mesh_list = []
                for obj in assembly.OutListRecursive:
                    if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                        mesh_list.append(obj)
                
                Mesh.export(mesh_list, file_path)
                exported_files.append(file_path)
                message = f"Все детали сборки экспортированы в один STL: {file_path}"

        elif export_format.upper() == "IGES":
            # IGES экспорт
            if not file_path.lower().endswith('.iges') and not file_path.lower().endswith('.igs'):
                file_path = base_name + '.iges'
            
            shapes_to_export = []
            for obj in assembly.OutListRecursive:
                if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                    shapes_to_export.append(obj.Shape)
            
            compound = Part.makeCompound(shapes_to_export)
            compound.exportIges(file_path)
            exported_files.append(file_path)
            message = f"Сборка экспортирована в IGES: {file_path}"

        elif export_format.upper() == "OBJ":
            # OBJ экспорт (3D форма для графики)
            if not file_path.lower().endswith('.obj'):
                file_path = base_name + '.obj'
            
            mesh_list = []
            for obj in assembly.OutListRecursive:
                if hasattr(obj, 'Shape') and not obj.Shape.isNull():
                    mesh_list.append(obj)
            
            Mesh.export(mesh_list, file_path)
            exported_files.append(file_path)
            message = f"Сборка экспортирована в OBJ: {file_path}"

        elif export_format.upper() == "SVG" and hasattr(App, "TechDraw"):
            # Экспорт 2D чертежа из TechDraw (если есть чертёж)
            from TechDraw import writeDXF, writeSvg
            if not file_path.lower().endswith('.svg'):
                file_path = base_name + '.svg'
            
            # Ищем первый объект TechDraw в документе
            techdraw_page = None
            for obj in doc.Objects:
                if obj.TypeId.startswith("TechDraw::DrawPage"):
                    techdraw_page = obj
                    break
            
            if techdraw_page:
                techdraw_page.saveSVG(file_path)
                exported_files.append(file_path)
                message = f"Чертёж экспортирован в SVG: {file_path}"
            else:
                return {
                    "success": False,
                    "message": "В документе не найдена страница TechDraw для экспорта.",
                    "exported_file": None,
                    "format": export_format
                }

        else:
            return {
                "success": False,
                "message": f"Неподдерживаемый формат экспорта: {export_format}",
                "exported_file": None,
                "format": export_format
            }

        # 4. Возвращаем успешный результат
        return {
            "success": True,
            "message": message,
            "exported_file": exported_files[0] if len(exported_files) == 1 else exported_files,
            "files_count": len(exported_files),
            "format": export_format,
            "mode": export_mode,
            "file_size": os.path.getsize(exported_files[0]) if exported_files and os.path.exists(exported_files[0]) else 0
        }

    except Exception as e:
        error_msg = f"Ошибка при экспорте сборки: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "exported_file": None,
            "format": export_format
        }