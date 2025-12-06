from prometheus_client import Counter

API_CALLS = Counter(
    "mcp_api_calls_total",
    "Total MCP API calls",
    ["service", "endpoint", "status"]
)