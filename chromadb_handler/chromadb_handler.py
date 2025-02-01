import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer


class ChromaDBHandler:
    """Handles ChromaDB operations: indexing, querying, and deletion."""

    def __init__(self, db_path, collection_name=None):

        self.db_path = db_path
        self.collection_name = collection_name

        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = None
        if collection_name:
            self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def load_and_process_csv(self, file_path):

        df = pd.read_csv(file_path)
        df["Meta_score"] = df["Meta_score"].fillna(0).astype(int)
        df["No_of_Votes"] = df["No_of_Votes"].fillna(0).astype(int)
        df["IMDB_Rating"] = df["IMDB_Rating"].fillna(0.0).astype(float)
        df["Gross"] = df["Gross"].fillna("").astype(str)
        df.fillna("", inplace=True)

        df["text"] = df.apply(lambda row: (
            f"Title: {row['Series_Title']}\n"
            f"Year: {row['Released_Year']}\n"
            f"Certificate: {row['Certificate']}\n"
            f"Runtime: {row['Runtime']}\n"
            f"Genre: {row['Genre']}\n"
            f"IMDB Rating: {row['IMDB_Rating']}\n"
            f"Overview: {row['Overview']}\n"
            f"Meta Score: {row['Meta_score']}\n"
            f"Director: {row['Director']}\n"
            f"Stars: {row['Star1']}, {row['Star2']}, {row['Star3']}, {row['Star4']}\n"
            f"Number of Votes: {row['No_of_Votes']}\n"
            f"Gross Revenue: {row['Gross']}\n"
        ), axis=1)

        return df

    def index_data_into_chroma(self, df):
        """
        Generate embeddings and insert IMDb data into ChromaDB.

        :param df: Preprocessed DataFrame containing movie metadata
        """
        for index, row in df.iterrows():
            embedding = self.embedding_model.encode(row["text"]).tolist()

            metadata = {
                "title": row["Series_Title"],
                "year": str(row["Released_Year"]),
                "certificate": row["Certificate"],
                "runtime": row["Runtime"],
                "genre": row["Genre"],
                "rating": str(row["IMDB_Rating"]),
                "overview": row["Overview"],
                "meta_score": str(row["Meta_score"]),
                "director": row["Director"],
                # "stars": ", ".join([star.strip() for star in [row["Star1"], row["Star2"], row["Star3"], row["Star4"]] if star]),
                "stars": ", ".join([row["Star1"], row["Star2"], row["Star3"], row["Star4"]]),
                "votes": str(row["No_of_Votes"]),
                "gross": row["Gross"]
            }

            self.collection.add(
                ids=[str(index)],
                embeddings=[embedding],
                metadatas=[metadata]
            )

        print(f"Data successfully indexed into ChromaDB collection '{self.collection_name}'!")

    def delete_collection(self):
        """
        Delete the entire ChromaDB collection.
        """
        self.chroma_client.delete_collection(name=self.collection_name)
        print(f"Collection '{self.collection_name}' has been deleted successfully!")

    def get_all_collections(self):
        return [collection.name for collection in self.chroma_client.list_collections()]
