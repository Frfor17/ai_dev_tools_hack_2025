"""Тесты для инструментов MCP."""
import pytest
from fastmcp import Context
from tools.market_data import get_market_data
from tools.company_info import get_company_profile
from tools.financial_analysis import analyze_financial_metrics

@pytest.mark.asyncio
async def test_get_market_data():
    ctx = Context()
    result = await get_market_data(symbol="AAPL", interval="1d", ctx=ctx)
    assert result.structured_content["symbol"] == "AAPL"
    assert "current_price" in result.structured_content

# Добавьте аналогичные тесты для других инструментов