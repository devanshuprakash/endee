import os
import time
from sentence_transformers import SentenceTransformer
from endee import Endee, Precision

# Sample dataset
data = [
    {"id": "doc1", "text": "Endee is a high-performance open-source vector database built for AI search and retrieval workloads.", "category": "technology"},
    {"id": "doc2", "text": "It is implemented in C++ and optimized for modern CPU targets, including AVX2, AVX512, NEON, and SVE2.", "category": "technology"},
    {"id": "doc3", "text": "Endee supports dense vector retrieval plus sparse search capabilities for hybrid search use cases.", "category": "features"},
    {"id": "doc4", "text": "Vector databases store data as high-dimensional vectors, enabling fast similarity search.", "category": "concept"},
    {"id": "doc5", "text": "RAG (Retrieval-Augmented Generation) uses a vector database to fetch relevant context for LLMs.", "category": "concept"},
    {"id": "doc6", "text": "Docker provides a way to run applications securely isolated in a container.", "category": "technology"},
    {"id": "doc7", "text": "Sentence Transformers are Python modules for state-of-the-art text and image embeddings.", "category": "technology"},
    {"id": "doc8", "text": "Cosine similarity measures the angle between two vectors, commonly used in text analysis.", "category": "mathematics"},
    {"id": "doc9", "text": "Python is a high-level, general-purpose programming language widely used in AI.", "category": "technology"},
    {"id": "doc10", "text": "Flask is a micro web framework written in Python, perfect for building APIs and web apps.", "category": "technology"},
    {"id": "doc11", "text": "Agentic AI refers to autonomous AI systems capable of executing complex multi-step workflows.", "category": "concept"},
    {"id": "doc12", "text": "The moon is Earth's only natural satellite, orbiting at an average distance of 384,400 km.", "category": "science"}
]

def main():
    print("Loading embedding model (all-MiniLM-L6-v2) ...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize Endee Client
    host = os.getenv("ENDEE_HOST", "http://localhost:8080")
    token = os.getenv("NDD_AUTH_TOKEN", "")
    
    print(f"Connecting to Endee at {host}...")
    if token:
        client = Endee(token)
    else:
        client = Endee()
        
    client.set_base_url(f"{host}/api/v1")
    
    index_name = "demo_index"
    
    print(f"Creating index '{index_name}'...")
    try:
        # Give Endee a moment to start if running via compose
        time.sleep(2)
        client.create_index(name=index_name, dimension=384, space_type="cosine", precision=Precision.INT8)
        print("Index created successfully.")
    except Exception as e:
        print(f"Index creation skipped (might already exist) or encountered an error: {e}")
        
    index = client.get_index(name=index_name)
    
    print("Generating vectors and upserting data...")
    vectors_to_upsert = []
    texts = [item["text"] for item in data]
    embeddings = model.encode(texts)
    
    for i, item in enumerate(data):
        doc = {
            "id": item["id"],
            "vector": embeddings[i].tolist(),
            "meta": {
                "text": item["text"],
                "category": item["category"]
            }
        }
        vectors_to_upsert.append(doc)
        
    index.upsert(vectors_to_upsert)
    print(f"Successfully upserted {len(vectors_to_upsert)} documents to the '{index_name}' index in Endee!")

if __name__ == "__main__":
    main()
