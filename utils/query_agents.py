import sqlite3

from autogen import AssistantAgent

from chromadb_handler.chromadb_handler import ChromaDBHandler
# from database.database import get_db_connection
from utils.constants import gemini_api_key, chroma_path, groq_api_key

# Connect to the SQLite database
conn = sqlite3.connect('imdb_movies.db')
cur = conn.cursor()

# Execute a PRAGMA statement to get the table schema
cur.execute("PRAGMA table_info(movies);")

# Fetch all results
schema = cur.fetchall()

# Close the connection
cur.close()
conn.close()

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
    system_message=f"Execute structured SQL queries on IMDb database. Schema for the database table movies is {schema}"
)

nlp_agent = AssistantAgent(
    name="NLPQueryAgent",
    llm_config={
        "config_list": [
            {
                # Let's choose the Llama 3 model
                "model": "llama3-8b-8192",
                # Put your Groq API key here or put it into the GROQ_API_KEY environment variable.
                "api_key": groq_api_key,
                # We specify the API Type as 'groq' so it uses the Groq client class
                "api_type": "groq",
            }
        ],
        "temperature": 0.2,
    },
    system_message="Your task is to take structured SQL query results and explain them in a conversational and engaging way. "
                   "Provide a natural language summary as if you were chatting with a user. Keep it informative but also friendly. "
                   "If there are patterns, trends, or interesting insights in the data, highlight them."
                   "\n\nFor example, if given a list of top movies based on certain criteria, describe them in a way that feels like "
                   "you're recommending or analyzing them for the user. Use full sentences, avoid overly technical jargon, and make "
                   "it sound engaging."
                   "\n\nExample:\n"
                   "**User's Query:** 'Top 10 movies with over 1M votes but lower gross earnings.'\n\n"
                   "**SQL Result:**\n"
                   "| title | gross | votes |\n"
                   "| --- | --- | --- |\n"
                   "| Se7en | 100,125,643 | 1,445,096 |\n"
                   "| Pulp Fiction | 107,928,762 | 1,826,188 |\n"
                   "| The Wolf of Wall Street | 116,900,694 | 1,187,498 |\n"
                   "| Inglourious Basterds | 120,540,719 | 1,267,869 |\n"
                   "| Shutter Island | 128,012,934 | 1,129,894 |\n\n"

                   "**Response:**\n"
                   "'It looks like you’re interested in highly rated movies that had massive audience engagement but didn’t dominate "
                   "at the box office! Here are some great picks:\n\n"
                   "*Se7en* (1995) - This dark psychological thriller, starring Brad Pitt and Morgan Freeman, amassed over 1.4M votes, "
                   "yet its box office earnings were around $100M.\n"
                   "*Pulp Fiction* (1994) - A cult classic by Quentin Tarantino with an impressive 1.8M votes but only $107M in earnings. "
                   "It’s considered one of the greatest films ever made!\n"
                   "*The Wolf of Wall Street* (2013) - Despite its wild story and star power (Leonardo DiCaprio), it brought in about $116M, "
                   "which is relatively low for its scale.\n"
                   "*Inglourious Basterds* (2009) - Another Tarantino hit, with over 1.2M votes and $120M in box office revenue.\n"
                   "*Shutter Island* (2010) - A psychological thriller by Martin Scorsese, with more than 1.1M votes but only $128M in earnings.\n\n"
                   "Interestingly, many of these movies have strong cult followings and are widely regarded as masterpieces, despite not "
                   "having the highest box office numbers. Want more details on any of these films? 😊'"

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
    conn = sqlite3.connect('imdb_movies.db')
    cur = conn.cursor()
    try:
        cur.execute(query)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []

    except Exception as e:
        print(f"SQL Query Error: {e}")
        results, columns = [], []  # Ensure fallback if the query fails
        return None, 202

    conn.close()
    print(results, columns)

    if not results or not columns:
        print("SQL query returned no results. Falling back to Vector Search...")
        return None, 202

    # Format results as Markdown table
    formatted_result = "| " + " | ".join(columns) + " |\n"
    formatted_result += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    for row in results:
        formatted_result += "| " + " | ".join(str(cell) for cell in row) + " |\n"

    message_history = [{"role": "user", "content": formatted_result}]

    response = nlp_agent.generate_reply(messages=message_history)["content"]
    return response, 200


sql_agent.register_function({"execute_sql_query": execute_sql_query})


def execute_vector_search(messages):
    query = messages[-1]["content"]  # Extract latest query
    vector_db = ChromaDBHandler(db_path=chroma_path, collection_name="imdb_chatbot")
    search_results = vector_db.collection.query(
        query_embeddings=[vector_db.embedding_model.encode(query).tolist()],
        n_results=5
    )
    retrieved_movies = search_results["metadatas"][0]

    # Format structured response
    context = "\n\n".join([
        f"Title: {movie.get('title', 'N/A')}\n"
        f"Year: {movie.get('year', 'N/A')}\n"
        f"Certificate: {movie.get('certificate', 'N/A')}\n"
        f"Runtime: {movie.get('runtime', 'N/A')}\n"
        f"Genre: {movie.get('genre', 'N/A')}\n"
        f"IMDB Rating: {movie.get('rating', 'N/A')}\n"
        f"Overview: {movie.get('overview', 'N/A')}\n"
        f"Meta Score: {movie.get('meta_score', 'N/A')}\n"
        f"Director: {movie.get('director', 'N/A')}\n"
        f"Stars: {movie.get('stars', 'N/A')}\n"
        f"Number of Votes: {movie.get('votes', 'N/A')}\n"
        f"Gross Revenue: {movie.get('gross', 'N/A')}"
        for movie in retrieved_movies
    ])

    return context


vector_agent.register_function({"execute_vector_search": execute_vector_search})

