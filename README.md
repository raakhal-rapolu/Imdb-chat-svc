# IMDB Chatbot Service

## Overview
IMDB Chatbot Service is a **Gen AI-powered conversational bot** that leverages **IMDB movie data** to answer various movie-related queries. The bot uses **LLMs like OpenAI, Gemini, and Groq** to generate intelligent responses. It is built using **Flask** for the backend and **Streamlit** for the frontend.

## Features
- **Conversational chatbot** to answer movie-related queries
- **Multiple LLM integrations** (Llama, Gemini, Groq)
- **Vector store indexing** using **ChromaDB**
- **REST API with Swagger documentation**
- **Streamlit UI for interactive chatbot experience**

---

## **Installation Guide**

### **1. Install Poetry**
Poetry is used for package and environment management.

Follow the installation guide for your OS:  
[Poetry Installation Guide](https://python-poetry.org/docs/#installation)

Once installed, verify by running:
```sh
poetry --version
```

### **2. Clone the Repository**
```sh
git clone <repository_link>
cd imdb-chatbot-svc
```

### **3. Install Dependencies using Poetry**
```sh
poetry install
```

### **4. Install and Run Ollama**
Ollama is required for serving Llama models.

#### **For Linux & macOS:**
```sh
curl -fsSL https://ollama.com/install.sh | sh
```
#### **For Windows:**
Download and install from the official guide:  
[Ollama Installation Guide](https://ollama.com)

#### **Start Ollama Server**
```sh
ollama serve
```

---

## **Configuration & Environment Setup**

1. **Create an environment file** in the root directory:
```sh
touch .env
```
2. **Add API keys & Paths** to `.env`:
```sh
GEMINI_API_KEY=''
GROQ_API_KEY=''
```
3. **Set up local ChromaDB path**:
```sh
export CHROMADB_PATH='imdb-chatbot-svc/chromadb_handler'
export TMP_DIR='imdb-chatbot-svc/tmp'
```
4. **Load environment variables**:
```sh
source ~/.env
```

---

## **Running the Application**

### **Start Flask Backend**
```sh
poetry run task imdb-svc-backend
```
**Swagger UI URL:**  
[http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/](http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/)

### **Start Streamlit Frontend**
```sh
poetry run task imdb-svc-frontend
```

---

## **API Endpoints**

### **1. LLM Inference APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/imdb-chatbot-svc/chat` | Chat with the bot |
| **POST** | `/imdb-chatbot-svc/gemini-imdb-chat` | IMDB chat with Gemini |
| **POST** | `/imdb-chatbot-svc/gemini-text-inference` | General text inference with Gemini |
| **POST** | `/imdb-chatbot-svc/groq-imdb-chat` | IMDB chat with Groq |
| **POST** | `/imdb-chatbot-svc/imdb-chat` | IMDB chatbot using ChromaDB |

### **2. Vector Store Indexing APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/index/collections` | List all indexed collections |
| **POST** | `/index/create_index` | Upload CSV and create index |
| **POST** | `/index/delete_index` | Delete a collection |

---

## **Indexing IMDB Dataset**
### **1. Create Index**
- Use the `/index/create_index` endpoint.
- Upload the IMDB CSV file and specify `collection_name`.
- Example: **`imdb_chatbot`**

### **2. Delete Index**
- Use the `/index/delete_index` endpoint.
- Provide `collection_name` as input.

---

## **Using the Streamlit Chatbot**
Once the Streamlit frontend is running, you can **ask questions relevant to the IMDB dataset**.

Example queries:
1. _When did The Matrix release?_
2. _What are the top 5 movies of 2019 by meta score?_
3. _Top horror movies with a meta score above 85 and IMDB rating above 8._
4. _Summarize the movie plots of Steven Spielberg’s top-rated sci-fi movies._

---

## **Troubleshooting**
### **1. Poetry Not Found**
If `poetry` is not recognized:
```sh
export PATH="$HOME/.local/bin:$PATH"
```

### **2. Ollama Not Running**
Ensure the server is running:
```sh
ollama serve
```

### **3. Missing Environment Variables**
Reload environment variables:
```sh
source ~/.env
```

---

## **License**
This project is licensed under the MIT License.

---

## **Contact**
For any issues, please contact:  
**Raakhal Rapolu** - raakhal.rapolu@gmail.com