from common_logic import FreeCADCore
from mcp_instance import mcp
import logging

logger = logging.getLogger(__name__)

@mcp.tool()
def create_assembly_tool(name: str = "MyRobotAssembly"):
    """MCP-инструмент для создания сборки."""
    logger.info(f"create_assembly_tool called with name: {name}")
    
    try:
        # Сначала подключаемся к FreeCAD
        core = FreeCADCore()
        connect_result = core.connect()
        
        if not connect_result["success"]:
            logger.error(f"Failed to connect to FreeCAD: {connect_result.get('error', 'Unknown error')}")
            return f"Ошибка подключения к FreeCAD: {connect_result.get('error', 'Неизвестная ошибка')}"
        
        logger.info("FreeCAD connected successfully")
        
        # Теперь вызываем create_assemble
        result = core.create_assemble(name)
        logger.info(f"create_assemble result: {result}")
        
        return result.get("message", str(result))
        
    except Exception as e:
        logger.error(f"Exception in create_assembly_tool: {str(e)}", exc_info=True)
        return f"Ошибка при создании сборки: {str(e)}"