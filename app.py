"""Streamlit app for the Agentic AI System with GraphRAG."""
import streamlit as st
import os
import sys
from dotenv import load_dotenv
from graph_db.client import Neo4jClient
from graph_db.schema import GraphSchema
from agent.graphrag import GraphRAGPipeline
from agent.agent import AgenticAI
import time

load_dotenv()

# Page config with blue theme
st.set_page_config(
    page_title="Agentic AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for blue theme
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: rgba(30, 58, 138, 0.95);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .bot-message {
        background: white;
        color: #1f2937;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Tool tags */
    .tool-tag {
        display: inline-block;
        background: #dbeafe;
        color: #1e3a8a;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        background-color: white;
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the agent system (cached)."""
    try:
        neo4j_client = Neo4jClient()
        graphrag = GraphRAGPipeline(neo4j_client)
        agent = AgenticAI(graphrag)
        return neo4j_client, graphrag, agent, None
    except Exception as e:
        return None, None, None, str(e)


def get_graph_info(neo4j_client):
    """Get graph information."""
    if not neo4j_client:
        return None
    try:
        info = neo4j_client.get_graph_info()
        schema = GraphSchema(neo4j_client)
        schema_info = schema.get_schema_info()
        return {**info, "schema": schema_info}
    except:
        return None


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agentic AI System</h1>
        <p style="margin: 0; opacity: 0.9;">Powered by LangGraph, Neo4j GraphRAG & Custom Tools</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize system
    neo4j_client, graphrag, agent, error = initialize_system()
    
    if error:
        st.error(f"❌ Failed to initialize system: {error}")
        st.info("Please check your .env file and ensure Neo4j is running.")
        return
    
    # Sidebar with graph info
    with st.sidebar:
        st.markdown("### 📊 Graph Statistics")
        
        graph_info = get_graph_info(neo4j_client)
        if graph_info:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nodes", graph_info.get("node_count", 0))
                st.metric("Relationships", graph_info.get("relationship_count", 0))
            with col2:
                st.metric("Node Types", len(graph_info.get("node_types", [])))
                st.metric("Rel Types", len(graph_info.get("relationship_types", [])))
            
            st.markdown("---")
            st.markdown("### 🔗 Node Types")
            for node_type in graph_info.get("node_types", []):
                st.markdown(f"- {node_type}")
            
            st.markdown("### 🔗 Relationship Types")
            for rel_type in graph_info.get("relationship_types", []):
                st.markdown(f"- {rel_type}")
        else:
            st.warning("Graph info unavailable")
        
        st.markdown("---")
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "Who acted in Inception?",
            "What films did Christopher Nolan direct?",
            "Calculate 25 * 17 + 100",
            "What genres does Breaking Bad belong to?",
            "Which actors worked with Leonardo DiCaprio?",
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{query}", use_container_width=True):
                st.session_state.user_query = query
    
    # Main chat area
    st.markdown("### 💬 Chat with the Agent")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your Agentic AI assistant. I can help you query the knowledge graph about films and series, perform calculations, and search for information. Try asking me about actors, directors, films, series, genres, or ask me to calculate something!",
                "tools_used": []
            }
        ]
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                tools_html = ""
                if message.get("tools_used"):
                    tools_html = "<div style='margin-top: 0.5rem;'>"
                    for tool in message["tools_used"]:
                        tools_html += f'<span class="tool-tag">{tool}</span>'
                    tools_html += "</div>"
                
                st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                    {tools_html}
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    # Get query from input or session state
    query = ""
    if "user_query" in st.session_state:
        query = st.session_state.user_query
        del st.session_state.user_query
    
    user_input = st.text_input(
        "Type your question here...",
        value=query,
        key="input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([2, 10])
    with col1:
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)
    
    # Process query
    if (send_button and user_input) or ("user_query" in st.session_state and st.session_state.user_query):
        query_to_process = user_input if user_input else st.session_state.get("user_query", "")
        
        if query_to_process:
            # Clear the session state query if it was set
            if "user_query" in st.session_state:
                del st.session_state.user_query
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": query_to_process
            })
            
            # Show processing
            with st.spinner("🤔 Thinking..."):
                try:
                    # Query the agent
                    result = agent.query(query_to_process)
                    
                    # Add assistant response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.get("response", "No response generated."),
                        "tools_used": result.get("tools_used", [])
                    })
                    
                    # Rerun to show new messages
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Sorry, I encountered an error: {str(e)}",
                        "tools_used": []
                    })
                    st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat cleared! How can I help you?",
                "tools_used": []
            }
        ]
        st.rerun()


if __name__ == "__main__":
    main()

