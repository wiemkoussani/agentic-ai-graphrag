# System Architecture Documentation

## Overview

This document describes the architecture of the Agentic AI System with GraphRAG, built using LangGraph, Neo4j, and custom tools.

## System Components

### 1. Frontend (Streamlit Web UI)

**Location**: `app.py`

- **Technology**: Streamlit
- **Design**: Modern blue-themed interface with custom CSS
- **Features**:
  - Real-time chat interface
  - Graph statistics in sidebar
  - Message history with session state
  - Tool usage indicators
  - Example query buttons
  - Responsive design

**Key Files**:
- `app.py`: Main Streamlit application with UI and agent integration
- `.streamlit/config.toml`: Streamlit configuration

### 2. Backend API (FastAPI - Optional)

**Location**: `main.py`

- **Framework**: FastAPI (optional, for API mode)
- **Endpoints**:
  - `POST /ask`: Process user queries through the agent
  - `GET /graph-info`: Retrieve graph metadata
  - `GET /health`: Health check endpoint

**Note**: The main application uses Streamlit which directly integrates with the agent system. FastAPI is available for API-only deployments.

**Features**:
- CORS enabled for frontend communication
- Error handling and validation
- Async request processing

### 3. Agent System (LangGraph)

**Location**: `agent/agent.py`

**Architecture**:
```
User Query
    ↓
Agent Node (LLM with tools)
    ↓
Tool Selection Decision
    ↓
┌─────────┴─────────┐
│                   │
Tool Execution    End
    ↓
Agent Node (Process results)
    ↓
Final Response
```

**Key Components**:
- **State Management**: `AgentState` TypedDict tracks messages, steps, and tools used
- **Tool Binding**: LLM bound with available tools for function calling
- **Conditional Routing**: Graph routes to tools or end based on LLM decision
- **Multi-step Reasoning**: Agent can use multiple tools in sequence

### 4. GraphRAG Pipeline

**Location**: `agent/graphrag.py`

**Hybrid Retrieval Strategy**:

1. **Vector Similarity Search**:
   - Uses SentenceTransformer embeddings (all-MiniLM-L6-v2)
   - Generates embeddings for query and nodes
   - Performs cosine similarity search
   - Returns top-k most similar nodes

2. **Graph Traversal**:
   - Pattern matching on query intent
   - Cypher queries for specific relationship types
   - Multi-hop traversal (up to depth 2)
   - Returns connected subgraphs

3. **Context Construction**:
   - Combines vector and traversal results
   - Deduplicates nodes
   - Builds structured text context
   - Provides source attribution

**Embedding Model**: SentenceTransformer 'all-MiniLM-L6-v2' (384 dimensions)

### 5. Custom Tools

**Location**: `agent/tools.py`

#### Tool 1: Graph Query Tool
- **Purpose**: Query the Neo4j knowledge graph
- **Capabilities**:
  - Natural language to Cypher translation
  - Vector similarity search
  - Graph traversal
  - Hybrid retrieval

#### Tool 2: Calculator Tool
- **Purpose**: Perform mathematical calculations
- **Capabilities**:
  - Basic arithmetic (+, -, *, /)
  - Power operations (**)
  - Parentheses support
  - Input sanitization

#### Tool 3: Web Search Tool
- **Purpose**: Search the web for current information
- **Status**: Mock implementation (ready for API integration)
- **Future**: Can integrate SerpAPI, Tavily, or similar

### 6. Neo4j Knowledge Graph

**Location**: `graph_db/`

**Schema**:

```
Node Types:
- Film: {id, name, year, duration, rating, embedding}
- Serie: {id, name, seasons, episodes, rating, embedding}
- Actor: {id, name, nationality, born, embedding}
- Director: {id, name, nationality, born, embedding}
- Genre: {id, name, embedding}

Relationships:
- (Actor)-[:JOUE_DANS]->(Film)
- (Actor)-[:JOUE_DANS]->(Serie)
- (Director)-[:REALISE]->(Film)
- (Director)-[:REALISE]->(Serie)
- (Film)-[:APPARTIENT_A_GENRE]->(Genre)
- (Serie)-[:APPARTIENT_A_GENRE]->(Genre)
- (Actor)-[:A_JOUÉ_AVEC]->(Actor)
```

**Features**:
- Unique constraints on node IDs
- Vector embeddings stored on nodes
- Vector index for similarity search (Neo4j 5.11+)
- Connection pooling and session management

## Data Flow

### Query Processing Flow

```
1. User submits query via Streamlit UI
   ↓
2. Streamlit app invokes Agent.query() directly
   ↓
3. LangGraph workflow starts:
   a. Agent node receives query
   b. LLM (Groq) analyzes query and selects tools
   c. If tools needed → Tool execution
   d. Results fed back to agent
   e. Agent synthesizes final response
   ↓
4. Response returned to Streamlit
   ↓
5. UI displays response with tool usage info
   ↓
6. Message stored in session state for chat history
```

### GraphRAG Retrieval Flow

```
1. Query received by GraphRAG pipeline
   ↓
2. Generate query embedding
   ↓
3. Parallel execution:
   ├─ Vector Search: Find similar nodes
   └─ Graph Traversal: Find connected nodes
   ↓
4. Combine and deduplicate results
   ↓
5. Build context text
   ↓
6. Return context to agent
```

## LLM Integration

**Model**: Groq (default: llama-3.1-70b-versatile)

**Provider**: Groq API (fast inference, cost-effective)

**Prompting Strategy**:
- System message defines agent capabilities
- Tool descriptions guide tool selection
- Context from GraphRAG included in messages
- Multi-turn conversation support

**Tool Calling**:
- LLM bound with tool schemas
- Automatic tool selection based on query
- Structured tool arguments
- Tool results included in conversation

**Configuration**:
- Model can be changed in `agent/agent.py` (line 22)
- API key stored in `.env` as `GROQ_API_KEY`

## Error Handling

- **Neo4j Connection**: Graceful degradation if connection fails
- **Tool Execution**: Errors caught and returned to agent
- **LLM Errors**: Retry logic and error messages
- **API Errors**: HTTP status codes and error details

## Performance Considerations

1. **Embedding Generation**: Cached where possible
2. **Neo4j Queries**: Indexed lookups, limited result sets
3. **Vector Search**: Top-k limiting, efficient similarity computation
4. **Tool Execution**: Async support for I/O operations
5. **Response Streaming**: Can be extended for real-time updates

## Security

- **Input Sanitization**: Calculator tool sanitizes expressions
- **Environment Variables**: Sensitive data in .env file
- **CORS**: Configurable origins
- **API Keys**: Stored securely, not in code

## Scalability

**Current Limitations**:
- Single Neo4j instance
- Synchronous tool execution
- In-memory state management

**Future Enhancements**:
- Distributed Neo4j cluster
- Async tool execution
- Redis for state management
- Load balancing for API
- Caching layer for embeddings

## Testing

**Test Scenarios** (`tests/test_scenarios.py`):
1. Graph query - actor information
2. Graph query - director relationships
3. Graph query - genre information
4. Calculator tool
5. Complex multi-tool queries
6. Graph traversal (actors who worked together)
7. Film details queries

**Metrics Tracked**:
- Latency per query
- Tool usage accuracy
- Success rate
- Response quality

## Deployment

**Requirements**:
- Python 3.9+
- Neo4j 5.x (local or cloud) - Neo4j Desktop recommended
- Groq API key

**Steps**:
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` file with Neo4j and Groq credentials
3. Initialize graph: `python scripts/setup_graph.py`
4. Start Streamlit app: `streamlit run app.py`
5. App opens automatically at `http://localhost:8501`

**Optional API Mode**:
- Start FastAPI: `uvicorn main:app --reload`
- Access API at `http://localhost:8000`

## Future Enhancements

1. **Agent-to-Agent Communication**: Multi-agent collaboration
2. **MCP (Multi-Context Processing)**: Parallel context queries
3. **Real Web Search**: Integrate SerpAPI or Tavily
4. **Streaming Responses**: Real-time token streaming
5. **Advanced Graph Queries**: More complex Cypher patterns
6. **Evaluation Framework**: Automated quality metrics
7. **User Authentication**: Multi-user support
8. **Conversation History**: Persistent chat sessions

## Diagrams

### Agent Workflow Diagram

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
┌──────▼──────────┐
│  Agent Node     │ (LLM with tools)
│  - Analyze      │
│  - Select tools │
└──────┬──────────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│Tool │ │ End │
│Exec │ │     │
└──┬──┘ └─────┘
   │
┌──▼──────────┐
│  Agent Node │ (Process results)
│  - Synthesize│
│  - Respond  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Response  │
└─────────────┘
```

### GraphRAG Pipeline Diagram

```
┌─────────────┐
│   Query     │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──────┐
│Embed│ │Pattern  │
│Query│ │Match    │
└──┬──┘ └──┬──────┘
   │       │
┌──▼──┐ ┌──▼──────┐
│Vector│ │Cypher  │
│Search│ │Query   │
└──┬──┘ └──┬──────┘
   │       │
   └───┬───┘
       │
┌──────▼──────┐
│  Combine &  │
│  Deduplicate│
└──────┬──────┘
       │
┌──────▼──────┐
│Build Context│
└──────┬──────┘
       │
┌──────▼──────┐
│   Return    │
└─────────────┘
```

## Conclusion

This system demonstrates a complete Agentic AI architecture with:
- Multi-step reasoning via LangGraph
- Hybrid retrieval via GraphRAG
- Tool integration for extended capabilities
- Modern Streamlit web interface with blue theme
- Groq LLM integration for fast inference
- Comprehensive error handling

The architecture is modular, extensible, and ready for production enhancements.



