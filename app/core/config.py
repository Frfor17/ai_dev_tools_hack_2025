from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Конфигурация приложения."""
    
    # FreeCAD
    freecad_path: str = r'C:\Program Files\FreeCAD 1.0\bin'
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # MCP
    mcp_server_name: str = "CAD-Server"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()