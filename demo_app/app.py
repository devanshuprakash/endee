import os
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
from endee import Endee

app = Flask(__name__)

# Load model globally to avoid reloading on each request
print("Loading sentence-transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

# Setup Endee Client
host = os.getenv("ENDEE_HOST", "http://localhost:8080")
token = os.getenv("NDD_AUTH_TOKEN", "")

if token:
    client = Endee(token)
else:
    client = Endee()
    
client.set_base_url(f"{host}/api/v1")
INDEX_NAME = "demo_index"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query_text = data.get("query", "")
    top_k = data.get("top_k", 5)
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
        
    try:
        # Convert query into a vector representation
        query_vector = model.encode(query_text).tolist()
        
        # Connect to the index and search
        index = client.get_index(name=INDEX_NAME)
        results = index.query(vector=query_vector, top_k=top_k)
        
        return jsonify({"results": results})
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
