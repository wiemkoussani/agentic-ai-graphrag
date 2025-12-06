"""FastAPI backend for the Agentic AI system."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from graph_db.client import Neo4jClient
from graph_db.schema import GraphSchema
from agent.graphrag import GraphRAGPipeline
from agent.agent import AgenticAI

load_dotenv()

app = FastAPI(
    title="Agentic AI System API",
    description="API for the Generative AI Agentic System with GraphRAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
neo4j_client = None
graphrag = None
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global neo4j_client, graphrag, agent
    
    try:
        neo4j_client = Neo4jClient()
        graphrag = GraphRAGPipeline(neo4j_client)
        agent = AgenticAI(graphrag)
        print("✅ Agentic AI system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global neo4j_client
    if neo4j_client:
        neo4j_client.close()


class QueryRequest(BaseModel):
    """Request model for /ask endpoint."""
    query: str


class QueryResponse(BaseModel):
    """Response model for /ask endpoint."""
    response: str
    tools_used: list
    steps: list
    message_count: int


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Process a user query through the agent system."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.query(request.query)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/graph-info")
async def get_graph_info():
    """Get metadata about the knowledge graph."""
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j client not initialized")
    
    try:
        info = neo4j_client.get_graph_info()
        schema = GraphSchema(neo4j_client)
        schema_info = schema.get_schema_info()
        
        return {
            **info,
            "schema": schema_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph info: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "neo4j_connected": neo4j_client is not None,
        "agent_ready": agent is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



