# Medical-Agentic-AI-Chatbot

A Flask-based Retrieval-Augmented-Generation (RAG) medical Q&A chatbot powered by LangChain, Pinecone, OpenAI, and Hugging Face embeddings.

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- Pinecone API key

### STEP 1: Clone the repository

```bash
git clone https://github.com/spandanaravulapalli/Medical-Agentic-AI-Chatbot.git
cd Medical-Agentic-AI-Chatbot
```

### STEP 2: Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### STEP 3: Install dependencies

```bash
pip install -r requirements.txt
```

### STEP 4: Configure environment variables

Create a `.env` file in the project root with your API keys:

```ini
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

**Do NOT commit `.env` to version control.**

### STEP 5: Index documents (one-time setup)

Place your PDF files in the `data/` directory, then run:

```bash
python store_index.py
```

This creates/updates the Pinecone vector index with embeddings from your PDFs.

### STEP 6: Run the application

```bash
python app.py
```

The app will start on `http://localhost:8080`. Open this URL in your browser to access the chat interface.

---

## Architecture

### Data Flow
1. **Document Ingestion** (`src/helper.py`): Load PDFs from `data/`, chunk them (500 tokens, 20 overlap).
2. **Embeddings** (`src/helper.py`): Convert chunks to embeddings using Hugging Face (`sentence-transformers/all-MiniLM-L6-v2`, 384 dims).
3. **Indexing** (`store_index.py`): Upsert embeddings to Pinecone vector store.
4. **Retrieval** (`app.py`): Query index for top 3 similar chunks (k=3).
5. **Generation** (`app.py`): LangChain chain combines retrieval results with LLM (GPT-4o) for response.

### Key Files
- `app.py` — Flask server, RAG chain, routes (`/`, `/get`, `/history`)
- `store_index.py` — Document ingestion and Pinecone indexing
- `src/helper.py` — PDF loading, chunking, embedding functions
- `src/prompt.py` — System prompt for LLM (enforces concise 3-sentence answers)
- `templates/chat.html` — Frontend chat UI with AJAX to `/get`

---

## API Endpoints

### `GET /`
Renders the chat interface (HTML page).

### `POST /get`
Process user message and return LLM response.

**Request:**
```bash
curl -X POST http://localhost:8080/get -d "msg=What is diabetes?"
```

**Response:**
```
Diabetes is a chronic condition where blood glucose levels are abnormally high. Type 1 is autoimmune; Type 2 is insulin resistance. Both require lifestyle changes and medication management.
```

### `GET /history`
Retrieve full chat conversation history.

**Request:**
```bash
curl http://localhost:8080/history
```

**Response:**
```json
{
  "history": [
    {"type": "human", "content": "What is diabetes?"},
    {"type": "ai", "content": "Diabetes is a chronic condition..."}
  ]
}
```

---

### Pinecone dimension mismatch error
The embedding model and Pinecone index must both use **384 dimensions**. If you change the embedding model in `src/helper.py`, update the Pinecone index dimension in `store_index.py` accordingly.

### No responses from LLM
- Verify `OPENAI_API_KEY` and `PINECONE_API_KEY` are set in `.env`.
- Ensure PDFs were indexed: run `python store_index.py` and check Pinecone console.
- Check Flask debug logs in terminal for errors.

---

## Configuration & Customization

### Adjust retrieval results
Edit `app.py`, line ~35:
```python
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 5})  # Change k=3 to k=5 for more results
```

### Change LLM model
Edit `app.py`, line ~47:
```python
chatModel = ChatOpenAI(model="gpt-4-turbo")  # Switch from gpt-4o
```

### Modify system prompt
Edit `src/prompt.py` to customize answer style, tone, or length constraints.

### Rebuild index from scratch
Delete the index from Pinecone console or change `index_name` in `store_index.py`, then re-run:
```bash
python store_index.py
```

---

## Tech Stack

- **Backend**: Flask, LangChain
- **LLM**: OpenAI GPT-4o
- **Vector Database**: Pinecone
- **Embeddings**: Hugging Face (sentence-transformers/all-MiniLM-L6-v2)
- **Frontend**: HTML, CSS, JavaScript (AJAX)

---

## AWS Deployment (Optional)

### Prerequisites
- AWS account with IAM user (EC2 + ECR permissions)
- Docker installed locally
- GitHub account with repository secrets configured

### Steps

1. **Create Pinecone and OpenAI keys** (if not done).

2. **Create ECR repository** in AWS console:
   ```
   medicalbot (save the URI, e.g., 315865595359.dkr.ecr.us-east-1.amazonaws.com/medicalbot)
   ```

3. **Create EC2 instance** (Ubuntu):
   ```bash
   # Install Docker in EC2
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

4. **Configure GitHub Secrets** in your repository settings:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `ECR_REPO` (the URI from step 2)
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`

5. **Configure EC2 as a self-hosted runner** (GitHub Settings → Actions → Runners).

6. **Push to GitHub** to trigger CI/CD pipeline (builds Docker image, pushes to ECR, deploys to EC2).

---

## License

This project is open-source. See LICENSE file for details.

## Support

For issues or questions, open a GitHub issue or contact the maintainers.