"""Инструмент для получения информации о CAD системах."""

import os
from typing import Dict, Any
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars
from cad_client import cad_client

@mcp.tool(
    name="cad_systems_info",
    description="""📝 Получить информацию о доступных CAD системах.

Показывает статус подключения к различным CAD системам:
- Onshape
- Blender API

Помогает диагностировать проблемы с подключением.
"""
)
async def cad_systems_info(ctx: Context = None) -> ToolResult:
    """
    📝 Получает информацию о настройках CAD систем.
    
    Returns:
        ToolResult: Статус подключения к CAD системам
    """
    await ctx.info("🚀 Проверяем настройки CAD систем")
    
    info = []
    structured_info = {
        "systems": {},
        "recommendations": []
    }
    
    # Проверяем Onshape
    onshape_configured = all([
        cad_client.onshape_url,
        cad_client.onshape_key,
        cad_client.onshape_secret
    ])
    
    if onshape_configured:
        info.append("✅ Onshape: настроен (URL, ключ и секрет указаны)")
        structured_info["systems"]["onshape"] = {
            "status": "configured",
            "url": cad_client.onshape_url is not None,
            "key": cad_client.onshape_key is not None,
            "secret": cad_client.onshape_secret is not None
        }
    else:
        info.append("❌ Onshape: не настроен (добавьте ONSHAPE_API_URL, ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY в .env)")
        structured_info["systems"]["onshape"] = {"status": "not_configured"}
        structured_info["recommendations"].append("Настройте Onshape API ключи в .env файле")
    
    # Проверяем Blender
    blender_configured = cad_client.blender_url is not None
    
    if blender_configured:
        info.append("✅ Blender API: настроен")
        structured_info["systems"]["blender"] = {
            "status": "configured",
            "url": True,
            "token": cad_client.blender_token is not None
        }
    else:
        info.append("❌ Blender API: не настроен (добавьте BLENDER_API_URL в .env)")
        structured_info["systems"]["blender"] = {"status": "not_configured"}
        structured_info["recommendations"].append("Настройте Blender API URL в .env файле")
    
    info.append("\n💡 Рекомендации:")
    info.append("1. Создайте файл .env на основе .env.example")
    info.append("2. Добавьте свои API ключи")
    info.append("3. Для Blender: запустите с включенным REST API")
    
    text_content = "\n".join(info)
    
    await ctx.info("✅ Проверка настроек завершена")
    
    return ToolResult(
        content=[TextContent(type="text", text=text_content)],
        structured_content=structured_info,
        meta={"timestamp": "now"}
    )