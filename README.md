<h1 align="center">EMR Patient Summary Chatbot</h1>
<p align="center"><b>Ask your patient records anything.</b></p>

<p align="center"><img src="assets/architecture.png" alt="How the chatbot works" width="760"></p>

Skip the scrolling through spreadsheets. Type a question like "which patients have diabetes?" and get a plain-English answer built from the matching records. Ask something general instead and it answers from medical knowledge. A hands-on demo of retrieval-augmented generation (RAG) from start to finish.

> **Prototype for learning only.** Uses mock data (100 sample patients). Not for real medical use and not medical advice.

## Why it's interesting

- **Finds records by meaning,** not exact keywords
- **Knows when to look it up:** patient questions use your records, general ones use medical knowledge
- **Shows its sources:** every matching record is listed with a match score
- **Consistent answers:** temperature 0.0, so replies stay strict and repeatable

## How it works

1. **Setup (once):** patient records are turned into one short "story" per patient, converted to embeddings with Gemini, and stored in a MySQL-compatible database (TiDB Cloud).
2. **Each question:** your question is embedded, compared with every stored patient (cosine similarity), and routed:
   - match score above 0.45, or you ask to "list" / "show" / "all" → answer from the top 5 patient records
   - otherwise → answer from general medical knowledge
3. Gemini Flash writes the answer and the Streamlit UI shows it.

## Run it

You need Python 3.10+, a [Google AI Studio](https://aistudio.google.com/) API key, and a MySQL-compatible database.

```bash
git clone https://github.com/Athulya-cloud/health-chatbot-rag-mcp.git
cd health-chatbot-rag-mcp
pip install streamlit mysql-connector-python numpy pandas google-genai
```

Create `my_secrets.py` next to `app.py` with your own keys (never commit this file):

```python
GOOGLE_KEY = "your-google-api-key"
DB_CONFIG = {
    "host": "your-db-host",
    "port": 4000,
    "user": "your-user",
    "password": "your-password",
    "database": "your-database",
    "ssl_disabled": False,
}
```

Create a `patient_vectors` table with columns `patient_id`, `story_text` and `vector_json`, then load the data and start the app:

```bash
python step1_vectorize.py   # builds embeddings -> patient_vectors_dump.json
python step2_upload.py      # uploads them to the database
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501). Stop it with `Ctrl+C`.

## Tech stack

Python, Streamlit, Google Gemini (`text-embedding-004`, Gemini Flash), MySQL / TiDB Cloud, NumPy.

## Dataset

A 100-patient sample of mock EMR data, used for demonstration only.
