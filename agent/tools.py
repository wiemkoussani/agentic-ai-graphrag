"""Custom tools for the agent."""
import json
import re
from typing import Dict, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from agent.graphrag import GraphRAGPipeline
from graph_db.client import Neo4jClient


# -------------------------
# INPUT SCHEMAS
# -------------------------

class GraphQueryInput(BaseModel):
    """Input for graph query tool."""
    query: str = Field(description="Natural language query about the knowledge graph")
    use_vector_search: bool = Field(default=True, description="Whether to use vector search")


class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')")


class WebSearchInput(BaseModel):
    """Input for web search tool."""
    query: str = Field(description="Search query string")


# -------------------------
# TOOLS
# -------------------------

class GraphQueryTool(BaseTool):
    """Tool for querying the Neo4j knowledge graph."""

    name: str = "graph_query"
    description: str = """
    Use this tool to query the knowledge graph about films, series, actors, directors, 
    and genres. This tool can find information about:
    - Which actors played in which films or series
    - Which directors directed which films or series
    - What genres films and series belong to
    - Which actors worked together
    - Film and series details (year, rating, duration, etc.)
    """
    args_schema: Type[BaseModel] = GraphQueryInput
    
    # Use private attribute (underscore prefix) for custom fields
    _graphrag: Optional[GraphRAGPipeline] = None
    
    def __init__(self, graphrag: GraphRAGPipeline):
        super().__init__()
        # Store as private attribute
        self._graphrag = graphrag
    
    def _run(self, query: str, use_vector_search: bool = True) -> str:
        """Execute the graph query."""
        try:
            if use_vector_search:
                result = self._graphrag.hybrid_retrieval(query, top_k=5)
                return (
                    f"Graph Context:\n{result['context']}\n\n"
                    f"Found {len(result['nodes'])} relevant nodes."
                )
            else:
                result = self._graphrag.graph_traversal(query)
                return f"Graph Traversal Results: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"Error querying graph: {str(e)}"
    
    async def _arun(self, query: str, use_vector_search: bool = True) -> str:
        """Async version."""
        return self._run(query, use_vector_search)


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""

    name: str = "calculator"
    description: str = """
    Use this tool to perform mathematical calculations. 
    Supports basic operations: +, -, *, /, ** (power), and parentheses.
    Example: '2 + 2', '10 * 5', '(3 + 4) * 2'
    """
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """Evaluate the mathematical expression."""
        try:
            # Sanitize input - only allow numbers, operators, and parentheses
            sanitized = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(sanitized)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Async version."""
        return self._run(expression)


class WebSearchTool(BaseTool):
    """Tool for searching the web (mock implementation - can be connected to real API)."""

    name: str = "web_search"
    description: str = """
    Use this tool to search the web for current information, news, or facts 
    that might not be in the knowledge graph. Use this when you need:
    - Current events or news
    - General knowledge not in the graph
    - Verification of facts
    """
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str) -> str:
        """Perform web search (mock implementation)."""
        # Real implementation would call SerpAPI, Tavily, etc.
        return (
            f"[Mock Web Search] Results for '{query}': "
            "This is a placeholder. In production, this would call a real search API."
        )
    
    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)


# -------------------------
# TOOL FACTORY
# -------------------------

def get_tools(graphrag: GraphRAGPipeline) -> list:
    """Get all available tools."""
    return [
        GraphQueryTool(graphrag),
        CalculatorTool(),
        WebSearchTool()
    ]