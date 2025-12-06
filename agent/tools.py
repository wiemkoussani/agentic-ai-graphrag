"""Custom tools for the agent."""
import json
import re
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from agent.graphrag import GraphRAGPipeline
from graph_db.client import Neo4jClient


class GraphQueryInput(BaseModel):
    """Input for graph query tool."""
    query: str = Field(description="Natural language query about the knowledge graph")
    use_vector_search: bool = Field(default=True, description="Whether to use vector search")


class GraphQueryTool(BaseTool):
    """Tool for querying the Neo4j knowledge graph."""
    
    name = "graph_query"
    description = """
    Use this tool to query the knowledge graph about films, series, actors, directors, 
    and genres. This tool can find information about:
    - Which actors played in which films or series
    - Which directors directed which films or series
    - What genres films and series belong to
    - Which actors worked together
    - Film and series details (year, rating, duration, etc.)
    """
    args_schema = GraphQueryInput
    
    def __init__(self, graphrag: GraphRAGPipeline):
        super().__init__()
        self.graphrag = graphrag
    
    def _run(self, query: str, use_vector_search: bool = True) -> str:
        """Execute the graph query."""
        try:
            if use_vector_search:
                result = self.graphrag.hybrid_retrieval(query, top_k=5)
                return f"Graph Context:\n{result['context']}\n\nFound {len(result['nodes'])} relevant nodes."
            else:
                result = self.graphrag.graph_traversal(query)
                return f"Graph Traversal Results: {json.dumps(result, indent=2)}"
        except Exception as e:
            return f"Error querying graph: {str(e)}"
    
    async def _arun(self, query: str, use_vector_search: bool = True) -> str:
        """Async version."""
        return self._run(query, use_vector_search)


class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')")


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""
    
    name = "calculator"
    description = """
    Use this tool to perform mathematical calculations. 
    Supports basic operations: +, -, *, /, ** (power), and parentheses.
    Example: '2 + 2', '10 * 5', '(3 + 4) * 2'
    """
    args_schema = CalculatorInput
    
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


class WebSearchInput(BaseModel):
    """Input for web search tool."""
    query: str = Field(description="Search query string")


class WebSearchTool(BaseTool):
    """Tool for searching the web (mock implementation - can be connected to real API)."""
    
    name = "web_search"
    description = """
    Use this tool to search the web for current information, news, or facts 
    that might not be in the knowledge graph. Use this when you need:
    - Current events or news
    - General knowledge not in the graph
    - Verification of facts
    """
    args_schema = WebSearchInput
    
    def _run(self, query: str) -> str:
        """Perform web search (mock implementation)."""
        # In a real implementation, this would call a search API like SerpAPI, Tavily, etc.
        # For now, return a mock response
        return f"[Mock Web Search] Results for '{query}': This is a placeholder. In production, this would connect to a real search API like SerpAPI or Tavily."
    
    async def _arun(self, query: str) -> str:
        """Async version."""
        return self._run(query)


def get_tools(graphrag: GraphRAGPipeline) -> list:
    """Get all available tools."""
    return [
        GraphQueryTool(graphrag),
        CalculatorTool(),
        WebSearchTool()
    ]



