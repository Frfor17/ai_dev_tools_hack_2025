from common_logic import FreeCADCore
from mcp_instance import mcp

@mcp.tool()
def create_assembly_tool(name: str = "MyRobotAssembly"):
    """MCP-инструмент для создания сборки."""
    result = FreeCADCore.create_assemble(name)
    return result["message"]  # Или весь result в зависимости от формата ответа