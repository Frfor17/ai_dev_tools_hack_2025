"""MCP сервер для бизнес-аналитики и рыночных данных."""
import os
from dotenv import load_dotenv, find_dotenv
# Load environment variables
load_dotenv(find_dotenv())
from fastmcp import FastMCP, Context
# Импортируем единый экземпляр FastMCP
from mcp_instance import mcp
# Константы
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
# Импортируем инструменты
from tools.market_data import get_market_data, get_stock_price, get_market_quote
from tools.company_info import get_company_profile, get_company_news
from tools.financial_analysis import analyze_financial_metrics

@mcp.prompt()
def company_analysis_prompt(company: str = "") -> str:
    """Генерация промпта для анализа компании."""
    return f"""Проанализируйте компанию {company} и предоставьте:
1. Текущую рыночную позицию
2. Ключевые финансовые показатели
3. Основные риски и возможности
4. Рекомендацию по инвестициям"""

def main():
    """Запуск MCP сервера с HTTP транспортом."""
    print("=" * 60)
    print("🌐 ЗАПУСК MCP СЕРВЕРА ДЛЯ БИЗНЕС-АНАЛИТИКИ")
    print("=" * 60)
    print(f"🚀 MCP Server: http://{HOST}:{PORT}/mcp")
    print("=" * 60)
    print("📊 Доступные инструменты:")
    print("- get_stock_price: Получение текущей цены акции")
    print("- get_company_profile: Информация о компании")
    print("- analyze_financial_metrics: Анализ финансовых показателей")
    print("=" * 60)
    
    # Запускаем MCP сервер с streamable-http транспортом
    mcp.run(transport="streamable-http", host=HOST, port=PORT, stateless_http=True)

if __name__ == "__main__":
    main()