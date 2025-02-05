import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
from utils.constants import EMBED_MODEL, RERANK_MODEL, chroma_path



class RetrievalHandler:
    def __init__(
            self,
            collection_name: str = "imdb_chatbot",
            embed_model: str = EMBED_MODEL,
            re_rank_model: str = RERANK_MODEL,
    ):
        """
        Initializes the retrieval handler with:
          - ChromaDB for vector search.
          - BM25 for keyword search (using a combination of all metadata fields).
          - A cross-encoder re-ranker for fusing the results.

        Args:
            collection_name (str): Name of the ChromaDB collection.
            embed_model (str): Model for computing vector embeddings.
            re_rank_model (str): Cross-encoder model used for re-ranking.
        """
        self.collection_name = collection_name

        self.embedding_model = SentenceTransformer(embed_model)

        self.re_ranker = CrossEncoder(re_rank_model)

        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        self.initialize_bm25_retriever()

    def combine_metadata(self, meta: dict) -> str:
        """
        Combines all desired metadata fields into a single string.
        This string will be used for BM25 indexing and for re-ranking.
        """
        fields = [
            ("title", "Title"),
            ("year", "Year"),
            ("certificate", "Certificate"),
            ("runtime", "Runtime"),
            ("genre", "Genre"),
            ("rating", "IMDB Rating"),
            ("overview", "Overview"),
            ("meta_score", "Meta Score"),
            ("director", "Director"),
            ("stars", "Stars"),
            ("votes", "Votes"),
            ("gross", "Gross Revenue")
        ]
        combined_parts = []
        for key, label in fields:
            value = meta.get(key, "")
            if value:
                combined_parts.append(f"{label}: {value}")
        return "\n".join(combined_parts)

    def encode_query(self, query: str):
        return self.embedding_model.encode(query).tolist()

    def vector_search(self, query: str, top_k: int = 10):
        """
        Performs vector-based semantic search using ChromaDB.
        Returns a list of metadata dictionaries (one per retrieved document).
        """
        query_embedding = self.encode_query(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        if results and "metadatas" in results and results["metadatas"]:
            return results["metadatas"][0]
        return []

    def initialize_bm25_retriever(self):
        """
        Initializes the BM25 retriever from the metadata stored in ChromaDB.
        Instead of using just the "overview" field, we build a combined text from all fields.
        """
        stored = self.collection.get()  # Retrieve all stored items.
        if stored and "metadatas" in stored and stored["metadatas"]:
            texts = []
            metadatas = []
            for meta in stored["metadatas"]:
                combined_text = self.combine_metadata(meta)
                texts.append(combined_text)
                metadatas.append(meta)
            self.keyword_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
        else:
            self.keyword_retriever = None

    def keyword_search(self, query: str, top_k: int = 3):
        """
        Performs BM25 keyword search.
        Returns a list of Document objects.
        """
        if not self.keyword_retriever:
            return []
        docs = self.keyword_retriever.invoke(query)
        return docs[:top_k]

    def convert_document(self, doc):
        """
        Converts a result from either vector search (a dict) or BM25 (a Document)
        into a unified dictionary format with keys: 'title' and 'combined'.
        'combined' is a string that includes all the metadata fields.
        """
        if isinstance(doc, Document):
            meta = doc.metadata
        elif isinstance(doc, dict):
            meta = doc
        else:
            return {"title": str(doc)[:50], "combined": str(doc)}

        title = meta.get("title", "")
        combined = self.combine_metadata(meta)
        return {"title": title, "combined": combined}

    def merge_results(self, vector_results, keyword_results):
        """
        Merges vector and keyword results into a single list.
        Duplicate documents (by title) are removed, with priority given to vector search.
        """
        merged = {}
        for res in vector_results:
            doc = self.convert_document(res)
            key = doc["title"]
            merged[key] = doc
        # add BM25 results if not already present.
        for res in keyword_results:
            doc = self.convert_document(res)
            key = doc["title"]
            if key not in merged:
                merged[key] = doc
        return list(merged.values())

    def re_rank_results(self, query: str, results: list):
        """
        Re-ranks the combined results using the cross-encoder re-ranker.
        Each candidate is paired with the query and its combined metadata text is scored.
        """
        pairs = [(query, doc["combined"]) for doc in results]
        scores = self.re_ranker.predict(pairs)
        for doc, score in zip(results, scores):
            doc["score"] = score
        re_ranked = sorted(results, key=lambda x: x["score"], reverse=True)
        return re_ranked

    def hybrid_search(self, query: str, top_k_vector: int = 10, top_k_keyword: int = 5, top_k_final: int = 10):
        """
        Executes the hybrid retrieval pipeline:
          1. Performs vector search via ChromaDB.
          2. Performs BM25 keyword search using combined metadata text.
          3. Merges and de-duplicates results.
          4. Re-ranks the merged results using the cross-encoder.

        Returns the top_k_final re-ranked results.
        """
        vector_results = self.vector_search(query, top_k=top_k_vector)
        keyword_results = self.keyword_search(query, top_k=top_k_keyword)
        merged_results = self.merge_results(vector_results, keyword_results)
        re_ranked_results = self.re_rank_results(query, merged_results)
        return re_ranked_results[:top_k_final]


# -------------------------
# Example usage (for testing):
# -------------------------
if __name__ == "__main__":
    handler = RetrievalHandler()
    sample_query = "When did The Matrix release?"
    final_results = handler.hybrid_search(sample_query)
    for idx, res in enumerate(final_results, start=1):
        print(f"Result {idx}:")
        print(f"Title: {res['title']}")
        print(f"Score: {res.get('score', 0):.4f}")
        print(f"Combined Metadata Snippet: {res['combined'][:200]}")
        print("-" * 80)
