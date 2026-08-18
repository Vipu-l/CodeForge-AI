# CodeForge AI

### AI-Powered Repository Code Assistant using RAG and Gemini

CodeForge AI is an AI-powered codebase assistant that allows developers to analyze a GitHub repository and ask natural-language questions about its source code.

Instead of sending an entire repository directly to an LLM, CodeForge AI analyzes and indexes the repository, creates semantic code representations, retrieves relevant source code using vector search and reranking, and provides the retrieved context to Gemini to generate source-grounded answers.

---

## 🚀 Features

- 🔍 GitHub repository analysis
- 🧩 Source-code parsing and semantic chunking
- 🧠 Code embeddings
- 🔎 Semantic vector search
- 🎯 Exact function and code retrieval
- 🔄 Retrieval-Augmented Generation (RAG)
- 📄 Source file and line-number references
- 💾 Persistent repository indexes
- 🤖 Gemini-powered answers
- ⚡ FastAPI backend
- ⚛️ React frontend
- 📊 RAG performance testing

---

## 🏗️ System Architecture

```text
                    GitHub Repository
                           │
                           ▼
                  Repository Analysis
                           │
                           ▼
                    Code Parsing
                           │
                           ▼
                  Semantic Code Chunks
                           │
                           ▼
                     Embeddings
                           │
                           ▼
                    Vector Index
                           │
                           │
                    User Question
                           │
                           ▼
                    Query Embedding
                           │
                           ▼
                  Semantic Retrieval
                           │
                           ▼
                Candidate Augmentation
                           │
                           ▼
                     Reranking
                           │
                           ▼
                 Context Construction
                           │
                           ▼
                         Gemini
                           │
                           ▼
                  Answer + Sources

🔄 How It Works
1. Repository Analysis

The user provides a GitHub repository.

CodeForge AI analyzes the repository and identifies supported source-code files while ignoring unnecessary directories and files.

2. Code Parsing

Source files are parsed into meaningful code units such as:

Modules
Functions
Classes
Methods
Imports

This allows the system to retrieve specific pieces of code instead of treating the entire repository as one large document.

3. Semantic Indexing

The extracted code chunks are converted into embedding representations.

Each indexed document maintains information such as:

File path
Document type
Name
Start line
End line
Source code
Embedding

The resulting documents and embeddings are stored in the repository's vector index.

4. Persistent Index Management

Repository indexes are stored both:

In memory for fast access
On disk for persistence across backend restarts

This allows an already analyzed repository to be loaded again without rebuilding the entire index.

5. User Question

The user asks a natural-language question from the React frontend.

For example:

Show me the exact implementation of get_index().
6. Retrieval

The question is converted into an embedding and used to search the repository index.

The retrieval system combines semantic similarity with additional text-based matching and reranking to identify relevant source-code documents.

7. RAG Context Construction

The most relevant repository documents are selected and assembled into a context.

The context is then used to construct a source-grounded prompt.

8. Gemini

The constructed prompt is sent to Gemini.

Gemini generates the final answer using the retrieved repository context.

9. Sources

The response contains source information that allows the user to trace the answer back to the repository.

Example:

File:
backend/app/services/index_manager.py


Function:
get_index


Lines:
135 - 153
🧠 RAG Pipeline
                  User Question
                       │
                       ▼
                Query Embedding
                       │
                       ▼
                Vector Search
                       │
                       ▼
              Candidate Retrieval
                       │
                       ▼
           Text / Semantic Matching
                       │
                       ▼
                  Reranking
                       │
                       ▼
             Context Construction
                       │
                       ▼
                Prompt Creation
                       │
                       ▼
                    Gemini
                       │
                       ▼
               Generated Answer
                       │
                       ▼
                 Source References
🛠️ Tech Stack
Frontend
React.js
JavaScript
CSS
Vite
Backend
Python
FastAPI
Uvicorn
AI / RAG
Google Gemini
Text Embeddings
Vector Search
Retrieval-Augmented Generation
Semantic Retrieval
Reranking
Repository Processing
Git
Python source parsing
JavaScript / JSX parsing
TypeScript / TSX parsing
Generic source-file parsing
Development
Git
GitHub
VS Code
Postman
📁 Project Structure
CodeForge-AI/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── routes/
│   │   │   ├── question.py
│   │   │   └── repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── code_index_service.py
│   │   │   ├── code_parser.py
│   │   │   ├── embedding_service.py
│   │   │   ├── hnsw_index.py
│   │   │   ├── index_manager.py
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   └── vector_store.py
│   │   │
│   │   └── main.py
│   │
│   ├── rebuild_index.py
│   ├── test_architecture_search.py
│   ├── test_gemini.py
│   ├── test_gemini_models.py
│   ├── test_new_index.py
│   ├── test_rag_performance.py
│   ├── test_saved_index.py
│   ├── test_vector_search.py
│   └── requirements.txt
│
└── frontend/
    │
    ├── src/
    │   ├── App.jsx
    │   └── App.css
    │
    ├── package.json
    └── package-lock.json
⚙️ Installation
1. Clone the Repository
git clone https://github.com/Vipu-l/CodeForge-AI.git
cd CodeForge-AI
🐍 Backend Setup

Navigate to the backend:

cd backend

Create a Python virtual environment:

python -m venv venv
Windows

Activate the virtual environment:

venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
🔑 Environment Variables

Configure your Gemini API key using an environment variable.

Example:

GEMINI_API_KEY=your_api_key_here

If your local implementation uses a .env file, create it inside the backend directory.

Never commit API keys, credentials, or .env files to GitHub.

▶️ Running the Backend

From the backend directory:

uvicorn app.main:app --reload

The backend will be available at:

http://127.0.0.1:8000
⚛️ Frontend Setup

Open a second terminal.

Navigate to the frontend:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend will display the local development URL provided by Vite.

💡 Example Questions

After analyzing a repository, users can ask questions such as:

Exact Implementation
Show me the exact implementation of get_index().
Function Explanation
How does VectorStore.search() work?
Source Retrieval
Show me the exact implementation of ask_question in question.py.
Repository Understanding
How does the repository indexing process work?
Architecture
How does a question travel from the frontend to Gemini?

CodeForge AI retrieves relevant repository context and uses that context to generate the answer.

🔎 Example Retrieved Source

For an exact implementation query such as:

Show me the exact implementation of get_index().

the system can retrieve information similar to:

File:
repositories\CodeForge-AI\backend\app\services\index_manager.py


Function:
get_index


Lines:
135 - 153

The retrieved source can then be presented to the user together with the generated explanation.

🔌 API
Ask a Question
POST /api/questions/ask
Query Parameters
question
repository

Example:

POST /api/questions/ask?question=Show%20me%20the%20exact%20implementation%20of%20get_index()&repository=CodeForge-AI

The endpoint retrieves the repository index and passes the question and index to the RAG pipeline.

💾 Persistent Indexing

CodeForge AI supports persistent repository indexes.

When an index is created, it is maintained in memory and persisted on disk.

Repository
    │
    ▼
Code Index
    │
    ├──────────────► Memory
    │
    └──────────────► Disk
                         │
                         ▼
                   Server Restart
                         │
                         ▼
                   Load Existing Index

This reduces the need to rebuild repository indexes every time the backend restarts.

📊 Performance Testing

The backend includes performance testing utilities for measuring different parts of the RAG pipeline.

Measured stages include:

Index loading
Embedding generation
Vector search
Gemini response time
Total RAG response time

Example test output:

============================================================
CODEFORGE AI RAG PERFORMANCE TEST
============================================================


Index loading time: 0.0043 seconds


Embedding time: 0.0458 seconds


Vector search time: 0.0125 seconds


Retrieved results: 8


[RAG] Embedding: 0.018s
[RAG] Search/Reranking: 0.023s
[RAG] Context: 0.000s
[RAG] Gemini: 2.657s
[RAG] TOTAL: 2.698s


Full RAG response time: 2.6989 seconds

Performance can vary depending on hardware, model loading, network conditions, and Gemini response time.

🧪 Testing

The backend contains several testing utilities for validating different components of the system.

Examples include:

python test_vector_search.py
python test_rag_performance.py
python test_saved_index.py
python test_architecture_search.py
🔐 Source-Grounded Responses

A key objective of CodeForge AI is to ground generated answers in retrieved repository context.

Instead of relying solely on the language model's general knowledge, the RAG pipeline provides relevant repository code to the model.

The generated response can therefore be traced back to:

Repository
    ↓
File
    ↓
Code Document
    ↓
Function / Class / Module
    ↓
Line Range
    ↓
Generated Answer
📌 Key Components
code_parser.py

Responsible for parsing source files and extracting meaningful code structures.

code_index_service.py

Responsible for discovering repository files, parsing them, creating semantic documents, generating embeddings, and building the repository index.

vector_store.py

Provides vector-based storage and retrieval functionality for indexed code documents.

index_manager.py

Manages repository indexes in memory and provides persistent index loading and saving.

rag_service.py

Coordinates the retrieval-augmented generation pipeline, including retrieval, reranking, context construction, and answer generation.

llm_service.py

Handles communication with Gemini and generates answers from constructed prompts.

question.py

Provides the FastAPI endpoint used for repository questions.

App.jsx

Provides the React frontend interface for repository analysis and asking AI questions.

🎯 Project Goals

CodeForge AI was designed to make large codebases easier to understand by allowing developers to interact with repositories using natural language.

The project focuses on combining:

Code Analysis
      +
Semantic Search
      +
RAG
      +
LLMs
      +
Full-Stack Development
🔮 Future Improvements

Possible future improvements include:

Improved multi-file architecture retrieval
Better repository dependency tracking
Incremental repository indexing
Support for larger repositories
Conversation history
Authentication
Cloud deployment
Additional programming-language support
Improved retrieval evaluation
Repository-level dependency graphs
👨‍💻 Author
Vipul Pandey

B.Tech Computer Science & Engineering

GitHub:

https://github.com/Vipu-l

⭐ Project Highlights

CodeForge AI demonstrates practical implementation of:

Retrieval-Augmented Generation
Semantic code search
Vector indexing
Repository analysis
Source-grounded AI responses
LLM integration
Persistent indexing
FastAPI backend development
React frontend development
Full-stack AI application development
📄 License

This project is intended for educational and portfolio purposes.