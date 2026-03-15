import os
import time
from typing import List, Dict, Any
from endee import Endee, Precision

class VectorDBManager:
    """Manages interactions with the Endee Vector Database."""

    def __init__(self, index_name: str = "resume_index", dimension: int = 1536):
        self.host = os.getenv("ENDEE_HOST", "http://localhost:8080")
        self.token = os.getenv("NDD_AUTH_TOKEN", "")
        self.index_name = index_name
        self.dimension = dimension
        
        if self.token:
            self.client = Endee(self.token)
        else:
            self.client = Endee()
        
        self.client.set_base_url(f"{self.host}/api/v1")
        self.index = None

    def initialize_index(self):
        """Creates the index if it doesn't exist."""
        print(f"Initializing index '{self.index_name}' in Endee...")
        try:
            # Check if index exists by trying to get it
            self.index = self.client.get_index(name=self.index_name)
            print(f"Index '{self.index_name}' already exists.")
        except Exception:
            print(f"Index '{self.index_name}' not found. Creating...")
            try:
                self.client.create_index(
                    name=self.index_name, 
                    dimension=self.dimension, 
                    space_type="cosine", 
                    precision=Precision.INT8
                )
                self.index = self.client.get_index(name=self.index_name)
                print(f"Index '{self.index_name}' created successfully.")
            except Exception as e:
                print(f"Error creating index: {e}")
                raise

    def upsert_resumes(self, resumes: List[Dict[str, Any]]):
        """
        Upserts resumes into the index.
        Each resume dict should have: 'id', 'vector', and 'meta' (dict with 'text', 'name', etc.)
        """
        if not self.index:
            self.initialize_index()
        
        print(f"Upserting {len(resumes)} resumes to '{self.index_name}'...")
        self.index.upsert(resumes)
        print("Upsert complete.")

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Performs similarity search."""
        if not self.index:
            self.initialize_index()
        
        print(f"Searching for top {top_k} matches...")
        results = self.index.query(vector=query_vector, top_k=top_k)
        return results

if __name__ == "__main__":
    # Example usage:
    # db = VectorDBManager()
    # db.initialize_index()
    pass
