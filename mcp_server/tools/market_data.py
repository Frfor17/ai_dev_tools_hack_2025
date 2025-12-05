import datetime
import os
from typing import Optional
from fastmcp import Context
import httpx
from pydantic import BaseModel, Field
from mcp.types import TextContent
from tools.utils import ToolResult
from mcp_server import mcp
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FINHUB_API_KEY")


class MarketDataRequest(BaseModel):
    """Модель запроса рыночных данных."""
    symbol: str = Field(..., description="Символ акции (например: AAPL, GOOGL)")
    interval: Optional[str] = Field("1d", description="Интервал данных (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M)")
    
@mcp.tool(
    name = 'get_price',
    description = '''Получение цены одной акции для мониторинга в реальном времени
    Пример 
    узнать цену Apple: get_price(symbol='AAPL)'''
)
async def get_price(
    symbol: str = Field(
        ...,
        description="Символ акции"
    ),
    ctx: Context = None
) -> ToolResult:
    """
    Args:
        symbol: Символ акции
        ctx: Контекст для логирования

    Returns:
        ToolResult: Текущая цена акции"""
        
    await ctx.info(f"Запрос цены для {symbol}")
    
    try:
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": symbol, "token": api_key}
        
        async with httpx.AsyncClient(timeout=30) as  client:
            response = await client.get(url, params = params)
            response.raise_for_status()
            data = response.json()
            
        result = {
            "symbol": symbol,
            "price" : data.get('c', 0),
            "change": data.get('d', 0),
            'timestamp': datetime.utcnow().isoformat
        }
        
        await ctx.info(f"Цена ${result['price']}")
        
        return ToolResult(
            content=[TextContent(type='text', text=f"Цена {symbol}: ${result['price']}")],
            structured_content=result
        )
        
    except Exception as e:
        await ctx.error(f'Ошибка {e}')