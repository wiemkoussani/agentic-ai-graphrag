"""Neo4j database client and connection management."""
import os
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase as Neo4jGraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jClient:
    """Client for interacting with Neo4j database."""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = Neo4jGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = []
                for record in result:
                    records.append(dict(record))
                return records
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def get_graph_info(self) -> Dict[str, Any]:
        """Get metadata about the knowledge graph."""
        node_count_query = "MATCH (n) RETURN count(n) as count"
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"
        node_types_query = "CALL db.labels() YIELD label RETURN collect(label) as labels"
        rel_types_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
        
        node_count = self.execute_query(node_count_query)[0].get("count", 0)
        rel_count = self.execute_query(rel_count_query)[0].get("count", 0)
        node_types = self.execute_query(node_types_query)[0].get("labels", [])
        rel_types = self.execute_query(rel_types_query)[0].get("types", [])
        
        return {
            "node_count": node_count,
            "relationship_count": rel_count,
            "node_types": node_types,
            "relationship_types": rel_types
        }
    
    def create_vector_index(self, index_name: str = "embeddings", label: str = "Node"):
        """Create a vector index for embeddings."""
        query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (n:{label})
        ON n.embedding
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """
        try:
            self.execute_query(query)
            print(f"✅ Created vector index: {index_name}")
        except Exception as e:
            print(f"Note: Vector index may already exist or Neo4j version doesn't support it: {e}")



