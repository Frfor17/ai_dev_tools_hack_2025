"""Инструменты для финансового анализа."""
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
    name="analyze_financial_metrics",
    description="""📊 Анализ финансовых показателей компании.
Рассчитывает ключевые метрики: P/E, ROE, ROA, маржи и другие.
"""
)
async def analyze_financial_metrics(
    symbol: str = Field(..., description="Символ акции компании"),
    period: str = Field(default="annual", description="Период: annual или quarter"),
    ctx: Context = None
) -> ToolResult:
    """Анализирует финансовые показатели компании."""
    await ctx.info(f"📊 Начинаем финансовый анализ {symbol} ({period})")
    await ctx.report_progress(progress=0, total=100)
    try:
        if period not in ["annual", "quarter"]:
            raise ValueError("Период должен быть 'annual' или 'quarter'")
        env = _require_env_vars(["ALPHA_VANTAGE_API_KEY", "FINNHUB_API_KEY"])
        alpha_key = env["ALPHA_VANTAGE_API_KEY"]
        finnhub_key = env["FINNHUB_API_KEY"]
        await ctx.report_progress(progress=20, total=100)
        url = "https://www.alphavantage.co/query"
        params = {"function": "INCOME_STATEMENT", "symbol": symbol, "apikey": alpha_key}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            reports_key = "annualReports" if period == "annual" else "quarterlyReports"
            reports = data.get(reports_key, [])
            if reports:
                latest = reports[0]
                financials = {
                    "revenue": float(latest.get("totalRevenue", 0)),
                    "gross_profit": float(latest.get("grossProfit", 0)),
                    "net_income": float(latest.get("netIncome", 0)),
                    "eps": float(latest.get("eps", 0)),
                    "report_date": latest.get("fiscalDateEnding", ""),
                    "gross_margin": (float(latest.get("grossProfit", 0)) / float(latest.get("totalRevenue", 1))) * 100
                }
            else:
                financials = {"revenue": 0, "gross_profit": 0, "net_income": 0, "eps": 0, "gross_margin": 0, "report_date": ""}
        await ctx.report_progress(progress=40, total=100)
        market_url = "https://finnhub.io/api/v1/quote"
        market_params = {"symbol": symbol, "token": finnhub_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            market_response = await client.get(market_url, params=market_params)
            market_response.raise_for_status()
            market_data = market_response.json()
            current_price = market_data.get('c', 0)
        await ctx.report_progress(progress=60, total=100)
        balance_params = {"function": "BALANCE_SHEET", "symbol": symbol, "apikey": alpha_key}
        async with httpx.AsyncClient(timeout=60.0) as client:
            balance_response = await client.get(url, params=balance_params)
            balance_response.raise_for_status()
            balance_data = balance_response.json()
            balance_reports_key = "annualReports" if period == "annual" else "quarterlyReports"
            balance_reports = balance_data.get(balance_reports_key, [])
            if balance_reports:
                latest_balance = balance_reports[0]
                balance = {
                    "total_assets": float(latest_balance.get("totalAssets", 0)),
                    "total_equity": float(latest_balance.get("totalShareholderEquity", 0))
                }
            else:
                balance = {"total_assets": 0, "total_equity": 0}
        await ctx.report_progress(progress=80, total=100)
        metrics = {}
        if financials["eps"] > 0:
            metrics["pe_ratio"] = current_price / financials["eps"]
        if balance["total_equity"] > 0:
            metrics["roe"] = (financials["net_income"] / balance["total_equity"]) * 100
        if balance["total_assets"] > 0:
            metrics["roa"] = (financials["net_income"] / balance["total_assets"]) * 100
        period_text = "годовой" if period == "annual" else "квартальной"
        formatted_output = f"""
📊 Финансовый анализ {symbol} ({period_text})
💰 Выручка: ${financials['revenue']}
💎 Валовая прибыль: ${financials['gross_profit']}
🏦 Чистая прибыль: ${financials['net_income']}
📈 EPS: ${financials['eps']}
📊 Валовая маржа: {financials['gross_margin']} %
📈 ROE: {metrics.get('roe', 0)} %
💎 ROA: {metrics.get('roa', 0)} %
🔢 P/E: {metrics.get('pe_ratio', 0)}
📅 Дата отчета: {financials['report_date']}
"""
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"✅ Анализ завершен для {symbol}")
        return ToolResult(
            content=[TextContent(type="text", text=formatted_output)],
            structured_content={"financials": financials, "metrics": metrics},
            meta={"symbol": symbol, "period": period, "cache_ttl": 86400}
        )
    except Exception as e:
        await ctx.error(f"❌ Ошибка: {e}")
        raise McpError(ErrorData(code=-32603, message=str(e)))