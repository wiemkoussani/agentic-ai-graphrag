"""Script to initialize Neo4j knowledge graph with sample data."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_db.client import Neo4jClient
from graph_db.schema import GraphSchema
from agent.graphrag import GraphRAGPipeline


def create_sample_data(client: Neo4jClient, graphrag: GraphRAGPipeline):
    """Create sample knowledge graph data for films and series."""
    
    # Sample Films
    films = [
        {"id": "inception", "name": "Inception", "year": 2010, "duration": 148, "rating": 8.8},
        {"id": "interstellar", "name": "Interstellar", "year": 2014, "duration": 169, "rating": 8.6},
        {"id": "matrix", "name": "The Matrix", "year": 1999, "duration": 136, "rating": 8.7},
        {"id": "dark_knight", "name": "The Dark Knight", "year": 2008, "duration": 152, "rating": 9.0},
        {"id": "pulp_fiction", "name": "Pulp Fiction", "year": 1994, "duration": 154, "rating": 8.9},
        {"id": "fight_club", "name": "Fight Club", "year": 1999, "duration": 139, "rating": 8.8},
        {"id": "godfather", "name": "The Godfather", "year": 1972, "duration": 175, "rating": 9.2},
        {"id": "avatar", "name": "Avatar", "year": 2009, "duration": 162, "rating": 7.9},
    ]
    
    # Sample Series
    series = [
        {"id": "breaking_bad", "name": "Breaking Bad", "seasons": 5, "episodes": 62, "rating": 9.5},
        {"id": "game_of_thrones", "name": "Game of Thrones", "seasons": 8, "episodes": 73, "rating": 9.3},
        {"id": "stranger_things", "name": "Stranger Things", "seasons": 4, "episodes": 42, "rating": 8.7},
        {"id": "the_crown", "name": "The Crown", "seasons": 6, "episodes": 60, "rating": 8.7},
        {"id": "dark", "name": "Dark", "seasons": 3, "episodes": 26, "rating": 8.8},
    ]
    
    # Sample Actors
    actors = [
        {"id": "leonardo", "name": "Leonardo DiCaprio", "nationality": "American", "born": 1974},
        {"id": "matt_damon", "name": "Matt Damon", "nationality": "American", "born": 1970},
        {"id": "anne_hathaway", "name": "Anne Hathaway", "nationality": "American", "born": 1982},
        {"id": "keanu_reeves", "name": "Keanu Reeves", "nationality": "Canadian", "born": 1964},
        {"id": "christian_bale", "name": "Christian Bale", "nationality": "British", "born": 1974},
        {"id": "john_travolta", "name": "John Travolta", "nationality": "American", "born": 1954},
        {"id": "brad_pitt", "name": "Brad Pitt", "nationality": "American", "born": 1963},
        {"id": "marlon_brando", "name": "Marlon Brando", "nationality": "American", "born": 1924},
        {"id": "bryan_cranston", "name": "Bryan Cranston", "nationality": "American", "born": 1956},
        {"id": "peter_dinklage", "name": "Peter Dinklage", "nationality": "American", "born": 1969},
        {"id": "millie_bobby", "name": "Millie Bobby Brown", "nationality": "British", "born": 2004},
        {"id": "olivia_colman", "name": "Olivia Colman", "nationality": "British", "born": 1974},
    ]
    
    # Sample Directors
    directors = [
        {"id": "nolan", "name": "Christopher Nolan", "nationality": "British", "born": 1970},
        {"id": "wachowski", "name": "Lana Wachowski", "nationality": "American", "born": 1965},
        {"id": "tarantino", "name": "Quentin Tarantino", "nationality": "American", "born": 1963},
        {"id": "fincher", "name": "David Fincher", "nationality": "American", "born": 1962},
        {"id": "coppola", "name": "Francis Ford Coppola", "nationality": "American", "born": 1939},
        {"id": "cameron", "name": "James Cameron", "nationality": "Canadian", "born": 1954},
        {"id": "gilligan", "name": "Vince Gilligan", "nationality": "American", "born": 1967},
        {"id": "duffer", "name": "Matt Duffer", "nationality": "American", "born": 1984},
    ]
    
    # Sample Genres
    genres = [
        {"id": "sci_fi", "name": "Science Fiction"},
        {"id": "action", "name": "Action"},
        {"id": "thriller", "name": "Thriller"},
        {"id": "drama", "name": "Drama"},
        {"id": "crime", "name": "Crime"},
        {"id": "fantasy", "name": "Fantasy"},
        {"id": "horror", "name": "Horror"},
    ]
    
    print("Creating nodes...")
    
    # Create Film nodes with embeddings
    for film in films:
        text = f"{film['name']} film {film['year']}"
        embedding = graphrag.get_embedding(text)
        query = """
        CREATE (f:Film {
            id: $id,
            name: $name,
            year: $year,
            duration: $duration,
            rating: $rating,
            embedding: $embedding
        })
        """
        client.execute_query(query, {**film, "embedding": embedding})
    
    # Create Series nodes with embeddings
    for serie in series:
        text = f"{serie['name']} series {serie['seasons']} seasons"
        embedding = graphrag.get_embedding(text)
        query = """
        CREATE (s:Serie {
            id: $id,
            name: $name,
            seasons: $seasons,
            episodes: $episodes,
            rating: $rating,
            embedding: $embedding
        })
        """
        client.execute_query(query, {**serie, "embedding": embedding})
    
    # Create Actor nodes with embeddings
    for actor in actors:
        text = f"{actor['name']} actor {actor['nationality']}"
        embedding = graphrag.get_embedding(text)
        query = """
        CREATE (a:Actor {
            id: $id,
            name: $name,
            nationality: $nationality,
            born: $born,
            embedding: $embedding
        })
        """
        client.execute_query(query, {**actor, "embedding": embedding})
    
    # Create Director nodes with embeddings
    for director in directors:
        text = f"{director['name']} director {director['nationality']}"
        embedding = graphrag.get_embedding(text)
        query = """
        CREATE (d:Director {
            id: $id,
            name: $name,
            nationality: $nationality,
            born: $born,
            embedding: $embedding
        })
        """
        client.execute_query(query, {**director, "embedding": embedding})
    
    # Create Genre nodes with embeddings
    for genre in genres:
        text = f"{genre['name']} genre"
        embedding = graphrag.get_embedding(text)
        query = """
        CREATE (g:Genre {
            id: $id,
            name: $name,
            embedding: $embedding
        })
        """
        client.execute_query(query, {**genre, "embedding": embedding})
    
    print("Creating relationships...")
    
    # Actor plays in Film
    actor_film = [
        ("leonardo", "inception"),
        ("leonardo", "interstellar"),
        ("matt_damon", "interstellar"),
        ("anne_hathaway", "interstellar"),
        ("keanu_reeves", "matrix"),
        ("christian_bale", "dark_knight"),
        ("john_travolta", "pulp_fiction"),
        ("brad_pitt", "fight_club"),
        ("marlon_brando", "godfather"),
    ]
    
    for actor_id, film_id in actor_film:
        query = """
        MATCH (a:Actor {id: $actor_id}), (f:Film {id: $film_id})
        CREATE (a)-[:JOUE_DANS]->(f)
        """
        client.execute_query(query, {"actor_id": actor_id, "film_id": film_id})
    
    # Actor plays in Serie
    actor_serie = [
        ("bryan_cranston", "breaking_bad"),
        ("peter_dinklage", "game_of_thrones"),
        ("millie_bobby", "stranger_things"),
        ("olivia_colman", "the_crown"),
    ]
    
    for actor_id, serie_id in actor_serie:
        query = """
        MATCH (a:Actor {id: $actor_id}), (s:Serie {id: $serie_id})
        CREATE (a)-[:JOUE_DANS]->(s)
        """
        client.execute_query(query, {"actor_id": actor_id, "serie_id": serie_id})
    
    # Director directs Film
    director_film = [
        ("nolan", "inception"),
        ("nolan", "interstellar"),
        ("nolan", "dark_knight"),
        ("wachowski", "matrix"),
        ("tarantino", "pulp_fiction"),
        ("fincher", "fight_club"),
        ("coppola", "godfather"),
        ("cameron", "avatar"),
    ]
    
    for director_id, film_id in director_film:
        query = """
        MATCH (d:Director {id: $director_id}), (f:Film {id: $film_id})
        CREATE (d)-[:REALISE]->(f)
        """
        client.execute_query(query, {"director_id": director_id, "film_id": film_id})
    
    # Director directs Serie
    director_serie = [
        ("gilligan", "breaking_bad"),
        ("duffer", "stranger_things"),
    ]
    
    for director_id, serie_id in director_serie:
        query = """
        MATCH (d:Director {id: $director_id}), (s:Serie {id: $serie_id})
        CREATE (d)-[:REALISE]->(s)
        """
        client.execute_query(query, {"director_id": director_id, "serie_id": serie_id})
    
    # Film/Serie belongs to Genre
    film_genre = [
        ("inception", "sci_fi"),
        ("inception", "thriller"),
        ("interstellar", "sci_fi"),
        ("interstellar", "drama"),
        ("matrix", "sci_fi"),
        ("matrix", "action"),
        ("dark_knight", "action"),
        ("dark_knight", "crime"),
        ("pulp_fiction", "crime"),
        ("pulp_fiction", "drama"),
        ("fight_club", "drama"),
        ("fight_club", "thriller"),
        ("godfather", "crime"),
        ("godfather", "drama"),
        ("avatar", "sci_fi"),
        ("avatar", "action"),
    ]
    
    for film_id, genre_id in film_genre:
        query = """
        MATCH (f:Film {id: $film_id}), (g:Genre {id: $genre_id})
        CREATE (f)-[:APPARTIENT_A_GENRE]->(g)
        """
        client.execute_query(query, {"film_id": film_id, "genre_id": genre_id})
    
    serie_genre = [
        ("breaking_bad", "crime"),
        ("breaking_bad", "drama"),
        ("game_of_thrones", "fantasy"),
        ("game_of_thrones", "drama"),
        ("stranger_things", "sci_fi"),
        ("stranger_things", "horror"),
        ("the_crown", "drama"),
        ("dark", "sci_fi"),
        ("dark", "thriller"),
    ]
    
    for serie_id, genre_id in serie_genre:
        query = """
        MATCH (s:Serie {id: $serie_id}), (g:Genre {id: $genre_id})
        CREATE (s)-[:APPARTIENT_A_GENRE]->(g)
        """
        client.execute_query(query, {"serie_id": serie_id, "genre_id": genre_id})
    
    # Actors who worked together
    worked_together = [
        ("leonardo", "matt_damon"),
        ("leonardo", "anne_hathaway"),
        ("matt_damon", "anne_hathaway"),
    ]
    
    for actor1_id, actor2_id in worked_together:
        query = """
        MATCH (a1:Actor {id: $actor1_id}), (a2:Actor {id: $actor2_id})
        CREATE (a1)-[:A_JOUÉ_AVEC]->(a2)
        """
        client.execute_query(query, {"actor1_id": actor1_id, "actor2_id": actor2_id})
    
    print("✅ Sample data created successfully!")


def main():
    """Main function to set up the graph."""
    print("🚀 Setting up Neo4j knowledge graph (Films & Series)...")
    
    try:
        client = Neo4jClient()
        schema = GraphSchema(client)
        graphrag = GraphRAGPipeline(client)
        
        # Create constraints
        print("Creating schema constraints...")
        schema.create_constraints()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        client.execute_query("MATCH (n) DETACH DELETE n")
        
        # Create sample data
        create_sample_data(client, graphrag)
        
        # Try to create vector index
        try:
            client.create_vector_index()
        except:
            print("Note: Vector index creation skipped (may require Neo4j 5.11+)")
        
        # Show graph info
        info = client.get_graph_info()
        print("\n📊 Graph Statistics:")
        print(f"  Nodes: {info['node_count']}")
        print(f"  Relationships: {info['relationship_count']}")
        print(f"  Node Types: {', '.join(info['node_types'])}")
        print(f"  Relationship Types: {', '.join(info['relationship_types'])}")
        
        client.close()
        print("\n✅ Graph setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up graph: {e}")
        raise


if __name__ == "__main__":
    main()
