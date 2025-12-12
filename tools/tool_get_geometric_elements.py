from common_logic import FreeCADCore
from mcp_instance import mcp
import logging

logger = logging.getLogger(__name__)



def get_geometric_elements(core, part_name):
    """
    Возвращает список всех геометрических элементов (грани, рёбра, вершины) указанной детали.
    
    Args:
        part_name (str): Имя детали в активном документе.
        
    Returns:
        dict: Результат с полями 'success', 'message', 'part', и списками 'faces', 'edges', 'vertices'.
    """
    try:
        if not core.freecad:
            result = core.connect()
            if not result["success"]:
                return {
                    "success": False,
                    "message": f"Ошибка подключения: {result.get('error')}",
                    "part": part_name,
                    "faces": [],
                    "edges": [],
                    "vertices": []
                }
                
                
            doc = core.current_doc
            if not doc:
                return {
                    "success": False,
                    "message": f"Ошибка подключения: {result.get('error')}",
                    "part": part_name,
                    "faces": [],
                    "edges": [],
                    "vertices": []
                }
        
        part = doc.getObject(part_name)
        if not part:
            return {
                "success": False,
                "message": f"Деталь с именем '{part_name}' не найдена в документе.",
                "part": part_name,
                "faces": [],
                "edges": [],
                "vertices": []
            }

        # 2. Проверяем, есть ли у детали геометрия (Shape)
        if not hasattr(part, "Shape") or part.Shape.isNull():
            return {
                "success": False,
                "message": f"Деталь '{part_name}' не содержит геометрической формы (Shape).",
                "part": part_name,
                "faces": [],
                "edges": [],
                "vertices": []
            }

        # 3. Извлекаем элементы из формы (Shape)
        shape = part.Shape
        
        # Готовим списки с именами в формате, который ожидает Assembly4 (например, "Face1")
        faces = [f"Face{i+1}" for i in range(len(shape.Faces))]
        edges = [f"Edge{i+1}" for i in range(len(shape.Edges))]
        vertices = [f"Vertex{i+1}" for i in range(len(shape.Vertexes))]

        return {
            "success": True,
            "message": f"Геометрия детали '{part_name}' проанализирована.",
            "part": part_name,
            "faces": faces,
            "edges": edges,
            "vertices": vertices
        }

    except Exception as e:
        error_msg = f"Ошибка при получении геометрии детали '{part_name}': {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "part": part_name,
            "faces": [],
            "edges": [],
            "vertices": []
        }
    


@mcp.tool()
def get_geometric_elements_tool(part_name: str):
    """MCP-инструмент для получения списка геометрических элементов детали."""
    core = FreeCADCore()
    connect_result = core.connect()
    if not connect_result["success"]:
        return {
            "success": False,
            "message": f"Ошибка подключения: {connect_result.get('error')}",
            "part": part_name,
            "faces": [],
            "edges": [],
            "vertices": []
        }
    result = get_geometric_elements(core, part_name)
    return result