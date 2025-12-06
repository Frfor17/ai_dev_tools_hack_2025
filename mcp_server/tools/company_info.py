"""Инструменты для получения информации о компании."""
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import httpx
from fastmcp import Context
from mcp.shared.exceptions import McpError, ErrorData
from mcp.types import TextContent
from pydantic import Field
from mcp_instance import mcp
from .utils import ToolResult, _require_env_vars, format_api_error

@mcp.tool(
    name="get_company_profile",
    description="""🏢 Получение профиля компании.
Полная информация о компании: название, страна, валюта, биржа, дата IPO, рыночная капитализация, отрасль, веб-сайт.
"""
)
async def get_company_profile(
    symbol: str = Field(..., description="Символ акции компании"),
    ctx: Context = None
) -> ToolResult:
    """Получает полный профиль компании."""
    await ctx.info(f"🏢 Запрашиваем профиль {symbol}")
    await ctx.report_progress(progress=0, total=100)
    try:
        env = _require_env_vars(["FINNHUB_API_KEY"])
        api_key = env["FINNHUB_API_KEY"]
        await ctx.report_progress(progress=25, total=100)
        url = "https://finnhub.io/api/v1/stock/profile2"
        params = {"symbol": symbol, "token": api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        await ctx.report_progress(progress=75, total=100)
        result = {
            "symbol": symbol,
            "name": data.get("name", "Неизвестно"),
            "country": data.get("country", "Неизвестно"),
            "currency": data.get("currency", "USD"),
            "exchange": data.get("exchange", "Неизвестно"),
            "ipo_date": data.get("ipo", "Неизвестно"),
            "market_capitalization": data.get("marketCapitalization", 0),
            "share_outstanding": data.get("shareOutstanding", 0),
            "web_url": data.get("weburl", ""),
            "industry": data.get("finnhubIndustry", "Неизвестно"),
            "phone": data.get("phone", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        formatted_output = f"""
🏢 {result['name']} ({symbol})
📍 Страна: {result['country']}
💰 Валюта: {result['currency']}
🏛️ Биржа: {result['exchange']}
📅 Дата IPO: {result['ipo_date']}
💎 Рыночная капитализация: ${result['market_capitalization']}
📊 Акций в обращении: {result['share_outstanding']}
🏭 Отрасль: {result['industry']}
🌐 Веб-сайт: {result['web_url']}
📞 Телефон: {result['phone']}
🕐 Обновлено: {result['timestamp']}
"""
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"✅ Профиль получен для {symbol}")
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content=result,
            meta={"symbol": symbol, "cache_ttl": 3600}
        )
    except httpx.HTTPStatusError as e:
        error_msg = format_api_error(e.response.text, e.response.status_code)
        await ctx.error(f"❌ Ошибка: {error_msg}")
        raise McpError(ErrorData(code=-32603, message=error_msg))
    except Exception as e:
        await ctx.error(f"❌ Ошибка: {e}")
        raise McpError(ErrorData(code=-32603, message=str(e)))

@mcp.tool(
    name="get_company_news",
    description="""📰 Получение последних новостей компании.
Свежие новости и пресс-релизы компании за указанный период.
"""
)
async def get_company_news(
    symbol: str = Field(..., description="Символ акции компании"),
    days: int = Field(default=7, ge=1, le=30, description="Количество дней (1-30)"),
    limit: int = Field(default=10, ge=1, le=50, description="Максимум новостей (1-50)"),
    ctx: Context = None
) -> ToolResult:
    """Получает последние новости компании."""
    await ctx.info(f"📰 Ищем новости {symbol} за {days} дней")
    await ctx.report_progress(progress=0, total=100)
    try:
        env = _require_env_vars(["FINNHUB_API_KEY"])
        api_key = env["FINNHUB_API_KEY"]
        await ctx.report_progress(progress=20, total=100)
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        url = "https://finnhub.io/api/v1/company-news"
        params = {"symbol": symbol, "from": from_date, "to": to_date, "token": api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            news_data = response.json()
        await ctx.report_progress(progress=60, total=100)
        news_list = news_data[:limit]
        formatted_news = []
        structured_news = []
        for i, news_item in enumerate(news_list, 1):
            headline = news_item.get("headline", "Без заголовка")
            summary = news_item.get("summary", "Без описания")[:200]
            url = news_item.get("url", "")
            source = news_item.get("source", "Неизвестно")
            date = datetime.fromtimestamp(news_item.get("datetime", 0)).strftime('%Y-%m-%d %H:%M') if news_item.get("datetime") else "Неизвестно"
            formatted_news.append(f"""
{i}. {headline}
📅 Дата: {date}
📰 Источник: {source}
📝 Описание: {summary}...
🔗 Ссылка: {url}
""")
            structured_news.append({
                "headline": headline,
                "summary": summary,
                "url": url,
                "source": source,
                "date": date
            })
        await ctx.report_progress(progress=90, total=100)
        formatted_output = f"""
📰 Последние новости {symbol} (за {days} дней)
{''.join(formatted_news) if formatted_news else "📭 Новостей не найдено."}
📊 Всего новостей: {len(news_list)}
"""
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"✅ Найдено {len(news_list)} новостей для {symbol}")
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content={"symbol": symbol, "news_count": len(news_list), "news": structured_news},
            meta={"symbol": symbol, "days": days, "limit": limit, "cache_ttl": 300}
        )
    except Exception as e:
        await ctx.error(f"❌ Ошибка: {e}")
        raise McpError(ErrorData(code=-32603, message=str(e)))