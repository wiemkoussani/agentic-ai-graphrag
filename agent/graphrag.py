"""GraphRAG pipeline for hybrid retrieval using vector similarity and Cypher queries."""
import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from graph_db.client import Neo4jClient
from dotenv import load_dotenv

load_dotenv()


class GraphRAGPipeline:
    """GraphRAG pipeline combining vector search and graph traversal."""
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
        # Use a smaller model for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text."""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def vector_search(self, query: str, top_k: int = 5, label: str = "Node") -> List[Dict[str, Any]]:
        """Perform vector similarity search in Neo4j."""
        query_embedding = self.get_embedding(query)
        
        # Get all nodes with embeddings and calculate similarity manually
        # This approach works with all Neo4j versions
        cypher_query = f"""
        MATCH (n:{label})
        WHERE n.embedding IS NOT NULL
        RETURN n
        LIMIT 200
        """
        all_nodes = self.client.execute_query(cypher_query)
        
        # Calculate cosine similarity manually
        query_vec = np.array(query_embedding)
        results = []
        
        for record in all_nodes:
            node_data = record.get("n", {})
            # Handle Neo4j node objects
            if hasattr(node_data, 'items'):
                node = dict(node_data)
            elif isinstance(node_data, dict):
                node = node_data
            else:
                continue
                
            if "embedding" in node and node["embedding"]:
                try:
                    node_vec = np.array(node["embedding"])
                    # Calculate cosine similarity
                    dot_product = np.dot(query_vec, node_vec)
                    norm_query = np.linalg.norm(query_vec)
                    norm_node = np.linalg.norm(node_vec)
                    
                    if norm_query > 0 and norm_node > 0:
                        similarity = dot_product / (norm_query * norm_node)
                        results.append({
                            "n": node,
                            "similarity": float(similarity)
                        })
                except Exception as e:
                    # Skip nodes with invalid embeddings
                    continue
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return results[:top_k]
    
    def graph_traversal(self, query: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Perform graph traversal using Cypher queries based on query intent."""
        query_lower = query.lower()
        
        # Pattern matching for different query types
        if "act" in query_lower or "actor" in query_lower or "played" in query_lower or "joué" in query_lower:
            cypher = """
            MATCH (a:Actor)-[:JOUE_DANS]->(content)
            RETURN a, content
            LIMIT 20
            """
        elif "direct" in query_lower or "director" in query_lower or "réalisé" in query_lower:
            cypher = """
            MATCH (d:Director)-[:REALISE]->(content)
            RETURN d, content
            LIMIT 20
            """
        elif "genre" in query_lower or "type" in query_lower:
            cypher = """
            MATCH (content)-[:APPARTIENT_A_GENRE]->(g:Genre)
            RETURN content, g
            LIMIT 20
            """
        elif "film" in query_lower or "movie" in query_lower:
            cypher = """
            MATCH (f:Film)
            OPTIONAL MATCH (a:Actor)-[:JOUE_DANS]->(f)
            OPTIONAL MATCH (d:Director)-[:REALISE]->(f)
            RETURN f, a, d
            LIMIT 20
            """
        elif "serie" in query_lower or "series" in query_lower or "show" in query_lower:
            cypher = """
            MATCH (s:Serie)
            OPTIONAL MATCH (a:Actor)-[:JOUE_DANS]->(s)
            OPTIONAL MATCH (d:Director)-[:REALISE]->(s)
            RETURN s, a, d
            LIMIT 20
            """
        elif "worked" in query_lower or "together" in query_lower or "collabor" in query_lower:
            cypher = """
            MATCH (a1:Actor)-[:A_JOUÉ_AVEC]->(a2:Actor)
            RETURN a1, a2
            LIMIT 20
            """
        else:
            # Generic query - get connected subgraph
            cypher = """
            MATCH path = (start)-[*1..2]-(connected)
            WHERE start.name CONTAINS $query OR connected.name CONTAINS $query
            RETURN path
            LIMIT 20
            """
            return self.client.execute_query(cypher, {"query": query})
        
        return self.client.execute_query(cypher)
    
    def hybrid_retrieval(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform hybrid retrieval combining vector search and graph traversal."""
        # Vector search
        vector_results = self.vector_search(query, top_k=top_k)
        
        # Graph traversal
        traversal_results = self.graph_traversal(query)
        
        # Combine and deduplicate
        context_nodes = {}
        
        for result in vector_results:
            node_data = result.get("n", {})
            # Handle Neo4j node objects
            if hasattr(node_data, 'items'):
                node = dict(node_data)
            elif isinstance(node_data, dict):
                node = node_data
            else:
                continue
                
            node_id = node.get("id") or node.get("name")
            if node_id:
                context_nodes[node_id] = {
                    "node": node,
                    "similarity": result.get("similarity", 0),
                    "source": "vector"
                }
        
        for result in traversal_results:
            # Extract nodes from traversal results
            for key, value in result.items():
                # Handle Neo4j node objects
                if hasattr(value, 'items'):
                    node = dict(value)
                elif isinstance(value, dict):
                    node = value
                else:
                    continue
                    
                if "id" in node or "name" in node:
                    node_id = node.get("id") or node.get("name")
                    if node_id and node_id not in context_nodes:
                        context_nodes[node_id] = {
                            "node": node,
                            "similarity": 0.5,  # Default for traversal
                            "source": "traversal"
                        }
        
        # Build context text
        context_text = self._build_context(context_nodes.values())
        
        return {
            "context": context_text,
            "nodes": list(context_nodes.values()),
            "vector_count": len([n for n in context_nodes.values() if n["source"] == "vector"]),
            "traversal_count": len([n for n in context_nodes.values() if n["source"] == "traversal"])
        }
    
    def _build_context(self, nodes: List[Dict]) -> str:
        """Build a text context from retrieved nodes."""
        context_parts = []
        
        for node_info in nodes:
            node = node_info.get("node", {})
            
            # Determine node type from properties or labels
            node_type = "Node"
            if "nationality" in node or "born" in node:
                if "seasons" in node or "episodes" in node:
                    node_type = "Serie"
                elif "year" in node or "duration" in node:
                    node_type = "Film"
                elif "seasons" not in node and "episodes" not in node and "year" not in node and "duration" not in node:
                    # Check if it's Actor or Director by checking relationships
                    node_type = "Actor"  # Default, could be Director too
            elif "year" in node or "duration" in node:
                node_type = "Film"
            elif "seasons" in node or "episodes" in node:
                node_type = "Serie"
            elif "name" in node and "nationality" not in node and "year" not in node:
                node_type = "Genre"
            
            # Extract properties
            name = node.get("name", "Unknown")
            props = {k: v for k, v in node.items() if k not in ["embedding", "id"] and v is not None}
            
            context_parts.append(f"{node_type}: {name}")
            for key, value in props.items():
                if value:
                    context_parts.append(f"  - {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else "No relevant context found."

