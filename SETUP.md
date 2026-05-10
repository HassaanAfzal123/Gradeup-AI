# Gradeup AI - Quick Setup Guide

## Step 1: Copy Environment File

```powershell
cd backend
copy .env.example .env
```

Then edit `.env` and add your **Groq API key**:
- Get it from: https://console.groq.com/
- Replace `GROQ_API_KEY=your-groq-api-key-here` with your actual key

## Step 2: Use SQLite (Easier than PostgreSQL)

In your `.env` file, use this instead of PostgreSQL:

```bash
DATABASE_URL=sqlite:///./gradeup.db
```

## Step 3: Install Dependencies (without PostgreSQL)

```powershell
cd backend
pip install fastapi uvicorn python-multipart aiofiles sqlalchemy alembic pyjwt bcrypt passlib groq chromadb sentence-transformers pypdf python-dotenv pydantic-settings pytest pytest-asyncio pytest-cov httpx python-jose
```

## Step 4: Run the Backend

```powershell
python -m uvicorn main:app --reload
```

## Step 5: Test the API

Open: http://localhost:8000/docs

You'll see all the endpoints:
- **Auth**: Register, Login
- **PDF**: Upload, List, Summarize
- **Chat**: Ask questions
- **Quiz**: Generate & submit
- **Analytics**: View weaknesses

## Frontend Next Steps

The frontend needs updates to work with the new auth system. Key changes:
1. Add Login/Register pages
2. Store JWT tokens
3. Add authentication headers to requests
4. Create dashboard for PDFs
5. Build chat and quiz interfaces

---

## 🎯 What's Ready Now:

✅ Multi-user authentication (JWT)
✅ PostgreSQL/SQLite database
✅ PDF upload & chunking (512 tokens, 50overlap)
✅ ChromaDB with sentence-transformers embeddings
✅ Groq API integration with system prompts
✅ RAG-based Q&A with cosine similarity
✅ Quiz generation from PDFs
✅ Weakness tracking & analytics

## 🔧 To Test:

1. Register: `POST /api/auth/register`
2. Login: Get your token
3. Upload PDF: `POST /api/pdf/upload` (with token)
4. Generate quiz: `POST /api/quiz/generate`
5. Ask questions: `POST /api/chat/ask`

Database tables will be created automatically on first run!
