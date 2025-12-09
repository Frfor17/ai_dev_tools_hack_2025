from mcp.server import FastMCP
from app.core.config import settings

# Создаем единый экземпляр FastMCP
mcp = FastMCP(settings.mcp_server_name)