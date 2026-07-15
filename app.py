import os
from flask import Flask, render_template, request, jsonify
import chromadb
from google import genai
# 1. Import dotenv to read your .env file
from dotenv import load_dotenv

# 2. Load the environment variables from .env right at the start
load_dotenv()

app = Flask(__name__)

# Initialize ChromaDB Local Client (persists data in ./chroma_db folder)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# Initialize Gemini Client
# Because load_dotenv() ran above, genai.Client() automatically 
# finds and uses your GEMINI_API_KEY from the environment.
try:
    client = genai.Client()
    MODEL_NAME = "gemini-3.5-flash"
except Exception as e:
    print(f"Initialization Error: Ensure GEMINI_API_KEY is correct in your .env file. Details: {e}")
    client = None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add_document', methods=['POST'])
def add_document():
    """Adds raw text documents to our local vector database with verbose logging."""
    data = request.json
    text = data.get("text")
    doc_id = data.get("id")
    
    if not text or not doc_id:
        print("[WARNING] Document insertion blocked: Missing text or ID.")
        return jsonify({"error": "Missing 'text' or 'id'"}), 400
        
    try:
        print(f"\n--- [ChromaDB Task Started] ID: {doc_id} ---")
        print("[Step 1/3] Raw text payload received successfully.")
        
        # This is where ChromaDB might pause on the first run to download the model
        print("[Step 2/3] Processing text embeddings... (On first run, this download might take 10-30s)")
        
        collection.upsert(
            documents=[text],
            ids=[doc_id]
        )
        
        print("[Step 3/3] Vector successfully written to local disk.")
        print("--- [ChromaDB Task Completed Successfully] ---\n")
        
        return jsonify({"message": f"Successfully added document ID: {doc_id}"}), 200
        
    except Exception as e:
        print(f"[ERROR] Fail during document ingestion: {str(e)}")
        print("--- [ChromaDB Task Failed] ---\n")
        return jsonify({"error": str(e)}), 500


@app.route('/query', methods=['POST'])
def query_rag():
    """Retrieves relevant context from ChromaDB and generates an answer using Gemini."""
    if not client:
        return jsonify({"error": "Gemini client is not initialized. Check your .env configuration."}), 500

    data = request.json
    user_query = data.get("query")
    
    if not user_query:
        return jsonify({"error": "Missing 'query'"}), 400
        
    try:
        # 1. RETRIEVE: Query local ChromaDB vector database for the top 2 matches
        results = collection.query(
            query_texts=[user_query],
            n_results=2
        )
        
        # Pull matching documents
        retrieved_docs = results.get("documents", [[]])[0]
        
        if not retrieved_docs:
            context = "No relevant background documents found in the database."
        else:
            context = "\n---\n".join(retrieved_docs)
            
        # 2. AUGMENT & GENERATE: Construct a grounding prompt for Gemini
        prompt = f"""
        You are a helpful assistant. Use ONLY the following retrieved context to answer the user's question. 
        If the answer cannot be found in the context, politely state that you do not have that information.
        
        [RETIREVED CONTEXT]:
        {context}
        
        [USER QUESTION]:
        {user_query}
        """
        
        # Call the Gemini model using the pre-initialized client
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        return jsonify({
            "answer": response.text,
            "retrieved_context": retrieved_docs
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Flask will pick up FLASK_DEBUG from your .env automatically if run via 'flask run'
    # but hardcoding debug=True here ensures it works seamlessly when running 'python app.py'
    app.run(debug=True, port=5000)