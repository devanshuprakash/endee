# AI Resume Selector (RAG with Endee)

This project is an AI-powered resume screening system built as part of the Endee Internship evaluation. It uses a RAG (Retrieval-Augmented Generation) pipeline to rank resumes against a Job Description.

## 🚀 Key Features
- **Semantic Retrieval**: Uses [Endee Vector Database](https://github.com/endee-io/endee) for fast, metadata-aware vector search.
- **AI-Powered Evaluation**: Uses OpenAI (GPT-4o) to evaluate candidate relevance and provide explanations.
- **Gradio UI**: A modern, easy-to-use interface for uploading resumes and screening candidates.

## 🏗️ System Design
1. **Data Ingestion**: Resumes (PDF, DOCX, TXT) are processed, converted into 1536-dimensional embeddings (OpenAI), and stored in Endee.
2. **Retrieval**: When a JD is provided, it is vectorized and the top relevant resumes are retrieved from Endee using cosine similarity.
3. **LLM Ranking**: The retrieved resumes are sent to GPT-4o along with the JD for a final match score and detailed explanation.

## 🛠️ Setup & Execution

### 1. Prerequisites
- Python 3.9+
- Endee Server running (Local or Docker)
- OpenAI API Key

### 2. Install Dependencies
```bash
pip install -r ai_resume_selector/requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (or inside `ai_resume_selector/`):
```env
OPENAI_API_KEY=your_openai_api_key
ENDEE_HOST=http://localhost:8080
NDD_AUTH_TOKEN=your_token_if_any
```

### 4. Run Endee Server
If you haven't started Endee yet:
```bash
./run.sh
```
(Or use Docker: `docker compose up -d`)

### 5. Launch the Application
```bash
python ai_resume_selector/app.py
```
Open `http://localhost:7860` in your browser.

## 📂 Project Structure
- `resume_processor.py`: Text extraction logic.
- `vector_db_manager.py`: Endee database interface.
- `llm_ranker.py`: OpenAI embedding and ranking logic.
- `app.py`: Gradio interface and pipeline orchestration.
- `samples/`: Sample resumes for testing.
