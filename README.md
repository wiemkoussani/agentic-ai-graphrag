# Generative AI Agentic System with GraphRAG

A comprehensive Agentic AI system that combines LangGraph workflows, custom tools, and a GraphRAG pipeline connected to Neo4j.

## 🏗️ Architecture

```
┌─────────────┐
│   Web UI    │ (React/HTML - Blue Theme)
└──────┬──────┘
       │
┌──────▼──────┐
│  FastAPI    │ (/ask, /graph-info)
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   LangGraph Agent       │
│  - Tool Selection       │
│  - Reasoning            │
│  - Multi-step Workflow  │
└──────┬──────────────────┘
       │
   ┌───┴───┬──────────┬──────────┐
   │       │          │          │
┌──▼──┐ ┌─▼───┐  ┌───▼───┐  ┌───▼───┐
│Graph│ │Search│  │Calc  │  │Other  │
│Tool │ │Tool  │  │Tool  │  │Tools  │
└──┬──┘ └─────┘  └──────┘  └───────┘
   │
┌──▼──────────────┐
│  GraphRAG       │
│  - Vector Search│
│  - Cypher Query │
└──┬──────────────┘
   │
┌──▼──────┐
│  Neo4j  │
│  Graph  │
└─────────┘
```

## 📋 Features

- **Multi-step Agent Workflow**: LangGraph-based agent with intelligent tool selection
- **Neo4j Knowledge Graph**: Tech company knowledge graph with relationships
- **GraphRAG Pipeline**: Hybrid retrieval using vector similarity and Cypher queries
- **Custom Tools**: Graph query tool, web search tool, calculator tool
- **FastAPI Backend**: RESTful API with `/ask` and `/graph-info` endpoints
- **Beautiful Web UI**: Modern blue-themed chat interface
- **Agent-to-Agent Interaction**: Optional multi-agent collaboration

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Neo4j Database (local or cloud)
- Groq API key

### Installation

1. **Install dependencies**:
```bash
cd pfe
pip install -r requirements.txt
```

2. **Run setup helper** (optional):
```bash
python setup.py
```

3. **Configure environment**:
Create a `.env` file in the project root:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

4. **Initialize Neo4j Graph**:
```bash
python scripts/setup_graph.py
```

5. **Start the Streamlit app**:
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 📁 Project Structure

```
pfe/
├── app.py                  # Streamlit application (main UI)
├── main.py                 # FastAPI application (optional API mode)
├── agent/
│   ├── __init__.py
│   ├── agent.py           # LangGraph agent workflow
│   ├── tools.py           # Custom tool implementations
│   └── graphrag.py        # GraphRAG pipeline
├── graph_db/
│   ├── __init__.py
│   ├── client.py          # Neo4j connection
│   └── schema.py          # Graph schema definition
├── scripts/
│   └── setup_graph.py     # Graph initialization script
├── app.py                 # Streamlit application (main UI)
├── tests/
│   └── test_scenarios.py  # Test scenarios
└── docs/
    └── architecture.md    # Detailed documentation
```

## 🧪 Test Scenarios

Run test scenarios:
```bash
python tests/test_scenarios.py
```

## 📊 Graph Schema

```
(Actor)-[:JOUE_DANS]->(Film)
(Actor)-[:JOUE_DANS]->(Serie)
(Director)-[:REALISE]->(Film)
(Director)-[:REALISE]->(Serie)
(Film)-[:APPARTIENT_A_GENRE]->(Genre)
(Serie)-[:APPARTIENT_A_GENRE]->(Genre)
(Actor)-[:A_JOUÉ_AVEC]->(Actor)
```

## 🔧 API Endpoints

### POST /ask
Query the agent with a natural language question.

**Request**:
```json
{
  "query": "Who acted in Inception and who directed it?"
}
```

**Response**:
```json
{
  "response": "Inception stars Leonardo DiCaprio and was directed by Christopher Nolan...",
  "tools_used": ["graph_query", "vector_search"],
  "steps": [...]
}
```

### GET /graph-info
Get metadata about the knowledge graph.

**Response**:
```json
{
  "node_count": 150,
  "relationship_count": 200,
  "node_types": ["Film", "Serie", "Actor", "Director", "Genre"],
  "relationship_types": ["JOUE_DANS", "REALISE", "APPARTIENT_A_GENRE", "A_JOUÉ_AVEC"]
}
```

## 📝 Documentation

See `docs/architecture.md` for detailed system architecture and design decisions.

## 🎥 Demo

See the demo video for a complete walkthrough of the system.

## 📄 License

MIT License

