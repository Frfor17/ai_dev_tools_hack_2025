from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from mcp.types import TextContent, ImageContent

@dataclass
class ToolResult:
    """Результат выполнения инструмента."""
    content: List[TextContent | ImageContent]
    structured_content: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
