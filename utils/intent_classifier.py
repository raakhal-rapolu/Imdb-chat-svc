from autogen import AssistantAgent
from utils.constants import gemini_api_key


intent_classifier = AssistantAgent(
    name="QueryRouter",
    llm_config={
        "config_list": [
            {
                "model": "gemini-pro",
                "api_key": f'{gemini_api_key}',
                "api_type": "google"
            }
        ],
        "temperature": 0.3,
    },
    system_message="""Classify if the query is best suited for 'SQLQueryAgent' (structured queries) or 'VectorSearchAgent' (semantic searches). Respond with 'SQL' or 'VECTOR'. 

**Guidelines:**
- Use **SQL** when the query requires structured data retrieval based on specific filters, sorting, or aggregations from a database (e.g., numeric comparisons, categorical selections, ranking).
- Use **VECTOR** when the query involves semantic understanding, natural language interpretation, or similarity-based searches (e.g., understanding movie plots, finding conceptually related items).

**Examples:**

    **SQL Queries (Structured Retrieval):**
    These queries require exact filtering, sorting, or numerical operations that can be executed with structured databases.

    1. What year was *Inception* released? → **SQL** (Direct lookup)
    2. Show the top 5 highest-rated action movies from 2015. → **SQL** (Filtered ranking)
    3. List the top 10 romance films released between 2000-2010 sorted by IMDb rating. → **SQL** (Filtered retrieval)
    4. Find thriller movies with a meta score above 80 and an IMDb rating over 7.5. → **SQL** (Multi-condition filtering)
    5. Identify directors who have directed at least three movies grossing over $400M. → **SQL** (Aggregation & filtering)
    6. List the top-grossing films with over 500K votes but earnings below $50M. → **SQL** (Filtering & ranking)

    **Vector Search Queries (Semantic Understanding):**
    These queries require contextual meaning, thematic understanding, or summarization beyond structured data.

    7. Find movies in the comedy genre where the plot involves time travel. → **VECTOR** (Concept-based search using movie overview)
    8. Summarize the key themes of Christopher Nolan’s top-rated sci-fi movies. → **VECTOR** (Requires plot understanding & summarization)
    9. Recommend drama films that explore themes of loneliness and self-discovery. → **VECTOR** (Semantic similarity search)
    10. Which movies depict artificial intelligence in a philosophical manner? → **VECTOR** (Conceptual search)
    11. Find horror movies where the protagonist is trapped in a time loop. → **VECTOR** (Plot-based search)
    12. What are some animated films that explore deep existential themes? → **VECTOR** (Theme-based search)
    
    
Respond with only 'SQL' or 'VECTOR' as the classification output.
"""
)


def classify_query(user_query):
    message_history = [{"role": "user", "content": user_query}]

    response = intent_classifier.generate_reply(messages=message_history)

    if isinstance(response, str):
        response = {"content": response.strip().upper()}

    return response.get("content", "").upper()



