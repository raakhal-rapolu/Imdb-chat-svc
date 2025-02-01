import chromadb

from sentence_transformers import SentenceTransformer

# Load sentence transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")



# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="/home/raakhal-rapolu/PycharmProjects/imdb-chatbot-svc/chromadb_handler")

# Create a collection
collection = chroma_client.get_or_create_collection(name="imdb_chatbot")


def retrieve_movie(query, top_k=3):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results

# Example query
query = "When did The Matrix release?"
retrieved_results = retrieve_movie(query)

print(retrieved_results)

for i, result in enumerate(retrieved_results["documents"][0]):
    print(f"Movie {i+1}: {result}")
    print(f"Metadata: {retrieved_results['metadatas'][0][i]}")
    print()
