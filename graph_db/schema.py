"""Neo4j graph schema definition and constraints."""
from graph_db.client import Neo4jClient


class GraphSchema:
    """Manages the knowledge graph schema."""
    
    def __init__(self, client: Neo4jClient):
        self.client = client
    
    def create_constraints(self):
        """Create unique constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT actor_id IF NOT EXISTS FOR (a:Actor) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT director_id IF NOT EXISTS FOR (d:Director) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT film_id IF NOT EXISTS FOR (f:Film) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT serie_id IF NOT EXISTS FOR (s:Serie) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                self.client.execute_query(constraint)
            except Exception as e:
                print(f"Note: Constraint may already exist: {e}")
        
        print("✅ Graph constraints created")
    
    def get_schema_info(self) -> dict:
        """Get information about the graph schema."""
        return {
            "node_labels": ["Film", "Serie", "Actor", "Director", "Genre"],
            "relationships": [
                "JOUE_DANS",
                "REALISE",
                "APPARTIENT_A_GENRE",
                "A_JOUÉ_AVEC"
            ],
            "properties": {
                "Film": ["id", "name", "year", "duration", "rating", "embedding"],
                "Serie": ["id", "name", "seasons", "episodes", "rating", "embedding"],
                "Actor": ["id", "name", "nationality", "born", "embedding"],
                "Director": ["id", "name", "nationality", "born", "embedding"],
                "Genre": ["id", "name", "embedding"]
            }
        }



