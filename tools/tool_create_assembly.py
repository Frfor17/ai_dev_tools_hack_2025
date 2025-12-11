

@mcp.tool()
def create_assembly_tool(name: str = "MyRobotAssembly"):
    """MCP-инструмент для создания сборки."""
    result = create_assemble(name)
    return result["message"]  # Или весь result в зависимости от формата ответа