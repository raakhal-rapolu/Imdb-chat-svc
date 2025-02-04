from autogen import AssistantAgent
from database.database import get_db_connection
from chromadb_handler.chromadb_handler import ChromaDBHandler
from utils.constants import gemini_api_key

sql_agent = AssistantAgent(
    name="SQLQueryAgent",
    llm_config={
        "config_list": [
            {
                "model": "gemini-pro",
                "api_key": f'{gemini_api_key}',
                "api_type": "google"
            }
        ],
        "temperature": 0.2,
    },
    system_message="Execute structured SQL queries on IMDb database. which has these colums 	Series_Title,	Released_Year,	Certificate,	Runtime,	Genre,	IMDB_Rating,	Overview,	Meta_score,	Director,	Star1,	Star2,	Star3,	Star4,	No_of_Votes,	Gross-"
)

vector_agent = AssistantAgent(
    name="VectorSearchAgent",
    llm_config={
        "config_list": [
            {
                "model": "gemini-pro",
                 "api_key": f'{gemini_api_key}',
                "api_type": "google"
            }
        ],
        "temperature": 0.2,
    },
    system_message="Retrieve movie data from ChromaDB using vector search."
)


def execute_sql_query(messages):
    query = messages[-1]["content"]  # Extract latest query
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query)

    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  # Get column names
    conn.close()

    # Format results as Markdown table
    formatted_result = "| " + " | ".join(columns) + " |\n"
    formatted_result += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    for row in results:
        formatted_result += "| " + " | ".join(str(cell) for cell in row) + " |\n"

    return formatted_result


sql_agent.register_function({"execute_sql_query": execute_sql_query})


def execute_vector_search(messages):
    query = messages[-1]["content"]  # Extract latest query

    vector_db = ChromaDBHandler()
    search_results = vector_db.collection.query(
        query_embeddings=[vector_db.embedding_model.encode(query).tolist()],
        n_results=5
    )

    # Convert search results into a structured response
    formatted_summary = "### 🔹 Movie Summaries\n\n"
    for i, result in enumerate(search_results['documents'][0]):
        formatted_summary += f"**{i+1}. {result}**\n\n"

    return formatted_summary


vector_agent.register_function({"execute_vector_search": execute_vector_search})

