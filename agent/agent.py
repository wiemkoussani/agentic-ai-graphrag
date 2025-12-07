"""LangGraph agent workflow with tool selection and reasoning."""
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agent.tools import get_tools
from agent.graphrag import GraphRAGPipeline


class AgentState(TypedDict):
    """State of the agent workflow."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    steps: Annotated[list, operator.add]
    tools_used: Annotated[list, operator.add]


class AgenticAI:
    """Main agentic AI system using LangGraph."""
    
    def __init__(self, graphrag: GraphRAGPipeline, model_name: str = "llama-3.3-70b-versatile"):
        self.graphrag = graphrag
        self.llm = ChatGroq(model=model_name, temperature=0)
        self.tools = get_tools(graphrag)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent node that processes messages and decides on tool usage."""
        messages = state["messages"]
        
        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            system_msg = SystemMessage(content="""
            You are an intelligent AI assistant with access to a knowledge graph and various tools.
            
            Your capabilities:
            1. Query a knowledge graph about films, series, actors, directors, and genres
            2. Perform mathematical calculations
            3. Search the web for current information
            
            Decision making:
            - Use graph_query tool when questions are about films, series, actors, directors, genres, or their relationships
            - Use calculator tool for mathematical expressions
            - Use web_search tool for current events or information not in the graph
            - You can use multiple tools in sequence if needed
            - Provide clear, comprehensive answers based on the information you retrieve
            
            Always explain your reasoning and cite your sources.
            """)
            messages = [system_msg] + list(messages)
        
        # Get response from LLM
        response = self.llm_with_tools.invoke(messages)
        
        # Track tool usage
        tool_calls = getattr(response, "tool_calls", []) or []
        if tool_calls:
            tool_names = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    tool_names.append(tc.get("name", ""))
                else:
                    tool_names.append(getattr(tc, "name", ""))
            state["tools_used"].extend(tool_names)
            state["steps"].append({
                "step": "tool_selection",
                "tools": tool_names,
                "reasoning": "Agent selected tools based on query analysis"
            })
        
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message has tool calls, continue to tools
        tool_calls = getattr(last_message, "tool_calls", []) or []
        if tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"
    
    def query(self, user_query: str) -> dict:
        """Process a user query through the agent workflow."""
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "steps": [],
            "tools_used": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract final response
        final_message = final_state["messages"][-1]
        response_text = final_message.content if hasattr(final_message, "content") else str(final_message)
        
        return {
            "response": response_text,
            "tools_used": list(set(final_state["tools_used"])),
            "steps": final_state["steps"],
            "message_count": len(final_state["messages"])
        }

