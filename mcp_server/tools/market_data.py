"""Инструменты для работы с рыночными данными."""
import os
from typing import Dict, Any
from datetime import datetime
import httpx
from fastmcp import Context
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars, format_api_error
from mcp.shared.exceptions import McpError, ErrorData
@mcp.tool(
    name="get_market_data",
    description="""📊 Получение текущих рыночных данных по акции.
Позволяет получить актуальные данные о цене акции, объеме торгов, изменениях за день.
Использует Finnhub API для получения реальных рыночных данных.
"""
)
async def get_market_data(
    symbol: str = Field(..., description="Символ акции (например: AAPL, GOOGL)"),
    interval: str = Field(default="1d", description="Интервал данных: 1m, 5m, 1d, 1w"),
    ctx: Context = None
) -> ToolResult:
    """Получает текущие рыночные данные по указанной акции."""
    await ctx.info(f"🚀 Начинаем получение рыночных данных для {symbol}")
    await ctx.report_progress(progress=0, total=100)
    try:
        valid_intervals = {"1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M"}
        if interval not in valid_intervals:
            raise ValueError(f"Недопустимый интервал: {interval}")
        env = _require_env_vars(["FINNHUB_API_KEY"])
        api_key = env["FINNHUB_API_KEY"]
        await ctx.report_progress(progress=25, total=100)
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": symbol, "token": api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        await ctx.report_progress(progress=75, total=100)
        result = {
            "symbol": symbol,
            "current_price": round(data.get('c', 0), 2),
            "high": round(data.get('h', 0), 2),
            "low": round(data.get('l', 0), 2),
            "open": round(data.get('o', 0), 2),
            "previous_close": round(data.get('pc', 0), 2),
            "change": round(data.get('d', 0), 2),
            "change_percent": round(data.get('dp', 0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        change_emoji = "📈" if result["change"] >= 0 else "📉"
        formatted_output = f"""
{change_emoji} Рыночные данные для {symbol}
💰 Цена: ${result['current_price']}
📅 Изменение: ${result['change']} ({result['change_percent']}%)
⬆️ Максимум: ${result['high']}
⬇️ Минимум: ${result['low']}
🚪 Открытие: ${result['open']}
📊 Предыдущее закрытие: ${result['previous_close']}
⏰ Обновлено: {result['timestamp']}
"""
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"✅ Данные успешно получены для {symbol}")
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content=result,
            meta={"symbol": symbol, "interval": interval, "cache_ttl": 60}
        )
    except ValueError as e:
        await ctx.error(f"❌ Ошибка валидации: {e}")
        raise McpError(ErrorData(code=-32602, message=str(e)))
    except httpx.HTTPStatusError as e:
        error_msg = format_api_error(e.response.text, e.response.status_code)
        await ctx.error(f"❌ HTTP ошибка: {error_msg}")
        raise McpError(ErrorData(code=-32603, message=error_msg))
    except Exception as e:
        await ctx.error(f"❌ Ошибка: {e}")
        raise McpError(ErrorData(code=-32603, message=str(e)))

@mcp.tool(
    name="get_stock_price",
    description="""💰 Получение текущей цены акции.
Быстрый способ получить только текущую цену акции без дополнительных данных.
"""
)
async def get_stock_price(
    symbol: str = Field(..., description="Символ акции (например: AAPL)"),
    ctx: Context = None
) -> ToolResult:
    """Получает текущую цену акции."""
    market_data = await get_market_data(symbol=symbol, ctx=ctx)
    if market_data.structured_content:
        price = market_data.structured_content.get("current_price", 0)
        change = market_data.structured_content.get("change", 0)
        change_percent = market_data.structured_content.get("change_percent", 0)
        change_emoji = "📈" if change >= 0 else "📉"
        formatted_output = f"""
{change_emoji} {symbol}
💰 Текущая цена: ${price}
📊 Изменение: ${change} ({change_percent}%)
"""
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content={"symbol": symbol, "price": price, "change": change, "change_percent": change_percent},
            meta={"source": "finnhub"}
        )
    raise McpError(ErrorData(code=-32603, message="Не удалось получить данные"))

@mcp.tool(
    name="get_market_quote",
    description="""📈 Получение биржевой котировки.
Полная котировка акции с детальной информацией о торгах.
"""
)
async def get_market_quote(
    symbol: str = Field(..., description="Символ акции"),
    ctx: Context = None
) -> ToolResult:
    """Получает полную биржевую котировку."""
    await ctx.info(f"📈 Запрашиваем котировку для {symbol}")
    await ctx.report_progress(progress=0, total=100)
    try:
        env = _require_env_vars(["FINNHUB_API_KEY"])
        api_key = env["FINNHUB_API_KEY"]
        await ctx.report_progress(progress=30, total=100)
        url = "https://finnhub.io/api/v1/stock/profile2"
        params = {"symbol": symbol, "token": api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            profile_data = response.json()
        await ctx.report_progress(progress=60, total=100)
        market_data = await get_market_data(symbol=symbol, ctx=ctx)
        result = {
            "symbol": symbol,
            "company_name": profile_data.get("name", "Неизвестно"),
            "exchange": profile_data.get("exchange", "Неизвестно"),
            "currency": profile_data.get("currency", "USD"),
            "market_cap": profile_data.get("marketCapitalization", 0),
            "share_outstanding": profile_data.get("shareOutstanding", 0),
            **market_data.structured_content
        }
        formatted_output = f"""
🏢 {result['company_name']} ({symbol})
💰 Цена: ${result['current_price']} {result['currency']}
📊 Биржа: {result['exchange']}
📈 Изменение: ${result['change']} ({result['change_percent']}%)
💎 Рыночная капитализация: ${result['market_cap']}
📊 Акций в обращении: {result['share_outstanding']}
📊 Диапазон дня: Максимум ${result['high']}, Минимум ${result['low']}, Открытие ${result['open']}
"""
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"✅ Котировка получена для {symbol}")
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content=result,
            meta={"symbol": symbol, "cache_ttl": 120}
        )
    except Exception as e:
        await ctx.error(f"❌ Ошибка: {e}")
        raise McpError(ErrorData(code=-32603, message=str(e)))