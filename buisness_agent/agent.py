"""Бизнес-аналитик агент для Evolution AI Agents."""
import os
import json
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

class AnalysisType(str, Enum):
    QUICK = "quick"
    FINANCIAL = "financial"
    COMPREHENSIVE = "comprehensive"

class AgentRequest(BaseModel):
    user_query: str
    analysis_type: AnalysisType = AnalysisType.QUICK
    symbols: List[str] = None

class AgentResponse(BaseModel):
    response: str
    structured_data: Dict[str, Any] = None
    recommendations: List[str] = None
    sources: List[str] = None
    timestamp: datetime = datetime.utcnow()

class BusinessAnalystAgent:
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        self.llm_endpoint = os.getenv("LLM_ENDPOINT", "https://foundation-models.api.cloud.ru/v1/chat/completions")
        self.api_key = os.getenv("EVOLUTION_API_KEY")

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        try:
            analysis = await self._analyze_user_query(request.user_query)
            symbols = request.symbols or analysis.get("companies", ["AAPL"])
            if request.analysis_type == AnalysisType.QUICK:
                result = await self._perform_quick_analysis(symbols)
            elif request.analysis_type == AnalysisType.FINANCIAL:
                result = await self._perform_financial_analysis(symbols)
            else:
                result = await self._perform_comprehensive_analysis(symbols)
            final_response = await self._format_response(result, request.user_query)
            return AgentResponse(
                response=final_response,
                structured_data=result.get("data"),
                recommendations=result.get("recommendations"),
                sources=result.get("sources")
            )
        except Exception as e:
            return AgentResponse(response=f"❌ Ошибка: {str(e)}")

    async def _analyze_user_query(self, query: str) -> Dict[str, Any]:
        prompt = f"""Проанализируй запрос: {query}
Ответ в JSON: {{"companies": ["AAPL"], "information_type": "price"}}"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.llm_endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "evolution-2.0", "messages": [{"role": "user", "content": prompt}]}
            )
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)

    async def _perform_quick_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        results = []
        sources = ["Finnhub API"]
        async with httpx.AsyncClient(timeout=30.0) as client:
            for symbol in symbols:
                response = await client.get(f"{self.mcp_server_url}/mcp/tools/get_stock_price", params={"symbol": symbol})
                if response.status_code == 200:
                    results.append(response.json().get("structured_content", {}))
        return {"data": results, "recommendations": [], "sources": sources}

    async def _perform_financial_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        results = []
        sources = ["Alpha Vantage"]
        async with httpx.AsyncClient(timeout=60.0) as client:
            for symbol in symbols:
                response = await client.get(f"{self.mcp_server_url}/mcp/tools/analyze_financial_metrics", params={"symbol": symbol})
                if response.status_code == 200:
                    results.append(response.json().get("structured_content", {}))
        return {"data": results, "recommendations": [], "sources": sources}

    async def _perform_comprehensive_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        financial = await self._perform_financial_analysis(symbols)
        quick = await self._perform_quick_analysis(symbols)
        return {"data": {**financial["data"][0], **quick["data"][0]}, "recommendations": [], "sources": financial["sources"] + quick["sources"]}

    async def _format_response(self, analysis_result: Dict, query: str) -> str:
        return json.dumps(analysis_result, indent=2)

from fastapi import FastAPI
app = FastAPI()

agent = BusinessAnalystAgent()

@app.post("/analyze", response_model=AgentResponse)
async def analyze(request: AgentRequest):
    return await agent.process_request(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)