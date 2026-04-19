
import os
import json
from dotenv import load_dotenv
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

load_dotenv()

def check():
    store = Neo4jPropertyGraphStore(
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        url=os.getenv("NEO4J_URI"),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )
    
    with store.client.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
        print("--- Products ---")
        result = session.run("MATCH (p:Product) RETURN p.name as name, p.sku as sku LIMIT 20")
        for record in result:
            print(f"- {record['name']} ({record['sku']})")
            
        print("\n--- Ingredients for 'L-Tyrosine' ---")
        result = session.run("MATCH (p:Product {sku: 'designs-for-health-l-tyrosine'})-[:CONTAINS]->(i:Ingredient) RETURN i.name as name")
        for record in result:
            print(f"- {record['name']}")

        print("\n--- Searching for 'Tyrosine' via keyword ---")
        result = session.run("MATCH (i:Ingredient) WHERE toLower(i.name) CONTAINS 'tyrosine' RETURN i.name as name")
        for record in result:
            print(f"- {record['name']}")

if __name__ == "__main__":
    check()
