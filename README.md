# 🎓 Gradeup AI - RAG-Based Tutoring Platform

**Generative AI course project** — adaptive tutoring with LLMs and retrieval-augmented generation.

A production-grade, multi-user AI tutoring platform with PDF-based learning, intelligent quizzes, and personalized weakness tracking.

## ✨ Features

- 🔐 **User Authentication** - JWT-based secure login/registration
- 📚 **PDF Knowledge Base** - Upload and index PDFs with vector embeddings
- 💬 **AI Chat** - RAG-powered Q&A with source citations
- 📝 **Smart Quizzes** - AI-generated quizzes from your documents
- 📊 **Analytics Dashboard** - Track progress and identify weak concepts
- 🎯 **Multi-User Support** - Complete data isolation per user
- ☁️ **Cloud Database** - Supabase PostgreSQL for production use

---

## 🏗️ Tech Stack

**Backend:**
- FastAPI (REST API)
- PostgreSQL (Supabase)
- ChromaDB (Vector store)
- Groq API (LLM - llama-3.3-70b)
- Sentence Transformers (Embeddings)
- JWT Authentication

**Frontend:**
- React + Vite
- Tailwind CSS
- React Router
- Axios

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- Groq API Key (free at https://console.groq.com/)
- Supabase Account (free at https://supabase.com/)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd project
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy example env file
copy .env.example .env
```

Edit `.env` and add your credentials:

```env
# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres

# Groq API
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# JWT Secret (generate a random string)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Frontend URL (for CORS)
CORS_ORIGINS=http://localhost:5173

# Debug
DEBUG=true
```

#### Get Your Credentials

**Groq API Key:**
1. Go to https://console.groq.com/
2. Sign up/Login
3. Create API Key
4. Copy and paste in `.env`

**Supabase Database URL:**
1. Go to https://supabase.com/ and create account
2. Create new project
3. Go to Settings → Database
4. Copy "Connection string" (URI format)
5. Replace `[YOUR-PASSWORD]` with your database password
6. Paste in `.env`

#### Start Backend

```bash
python -m uvicorn main:app --reload
```

Backend will run at: **http://localhost:8000**
API Docs at: **http://localhost:8000/docs**

---

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Start Frontend

```bash
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## 🎯 Usage

### 1. Register/Login
- Go to http://localhost:5173
- Create an account or login
- You'll be redirected to the dashboard

### 2. Upload PDF
- Go to "My PDFs" page
- Upload a PDF document
- System will automatically extract text, chunk it, and create embeddings

### 3. Chat with PDF
- Click "Chat" on any uploaded PDF
- Ask questions about the content
- Get AI-powered answers with source citations

### 4. Take Quiz
- Click "Quiz" on any PDF
- Enter a topic (e.g., "Machine Learning basics")
- Choose number of questions (1-10)
- AI generates quiz questions from the PDF
- Submit answers and get graded instantly

### 5. View Analytics
- Go to "Analytics" page
- See your stats: total PDFs, quizzes taken, average score
- View weak concepts identified from incorrect answers
- Get personalized study recommendations

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── auth/                 # Authentication (JWT, password hashing)
│   ├── database/             # Database models & connection
│   ├── routers/              # API endpoints
│   │   ├── auth.py          # Login, register
│   │   ├── pdf.py           # PDF upload, list, delete
│   │   ├── chat.py          # RAG Q&A
│   │   ├── quiz.py          # Quiz generation & submission
│   │   └── analytics.py     # Stats & weaknesses
│   ├── services/             # Core services
│   │   ├── groq_client.py   # Groq API integration
│   │   └── rag_service.py   # ChromaDB & RAG logic
│   ├── uploads/              # Uploaded PDF files
│   ├── chroma_db/            # ChromaDB vector store
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PDFLibrary.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── QuizPage.jsx
│   │   │   └── AnalyticsPage.jsx
│   │   ├── utils/            # Utilities (auth)
│   │   └── App.jsx           # Main app with routing
│   ├── package.json
│   └── vite.config.js
│
└── README.md                 # This file
```

---

## 🗄️ Database Schema

**Tables:**
- `users` - User accounts (email, password_hash)
- `pdfs` - Uploaded PDF metadata
- `chats` - Q&A conversation history
- `quizzes` - Generated quizzes and results
- `weaknesses` - Tracked weak concepts per user

All tables are created automatically on first run!

---

## 🔧 API Endpoints

**Authentication:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login (returns JWT)
- `GET /api/auth/me` - Get current user

**PDFs:**
- `POST /api/pdf/upload` - Upload PDF
- `GET /api/pdf/list` - List user's PDFs
- `POST /api/pdf/summarize/{id}` - Summarize PDF
- `DELETE /api/pdf/{id}` - Delete PDF

**Chat:**
- `POST /api/chat/ask` - Ask question (RAG)
- `GET /api/chat/history/{pdf_id}` - Get chat history
- `DELETE /api/chat/{id}` - Delete chat

**Quiz:**
- `POST /api/quiz/generate` - Generate quiz
- `POST /api/quiz/submit` - Submit & grade quiz
- `GET /api/quiz/history` - Get quiz history

**Analytics:**
- `GET /api/analytics/weaknesses` - Get weak concepts
- `GET /api/analytics/progress` - Get overall stats

---

## 🐛 Troubleshooting

### Backend won't start
- Check if `.env` file exists and has correct credentials
- Make sure PostgreSQL/Supabase connection string is correct
- Verify Groq API key is valid

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in backend `.env`
- Verify `API_BASE_URL` in `frontend/src/api/client.js`

### PDF upload fails
- Ensure `uploads/` directory exists in backend folder
- Check file is actually a PDF
- Verify ChromaDB is working (check `chroma_db/` folder)

### Chat returns "couldn't generate answer"
- Check Groq API key is valid
- Verify model name is correct (`llama-3.3-70b-versatile`)
- Check Groq API quota limits

---

## 🚀 Deployment

### Backend (Railway/Render)
1. Create account on Railway.app or Render.com
2. Create new PostgreSQL database service
3. Deploy backend with environment variables from `.env`
4. Update `CORS_ORIGINS` with your frontend URL

### Frontend (Vercel/Netlify)
1. Build frontend: `npm run build`
2. Deploy `dist/` folder to Vercel or Netlify
3. Update API URL in production environment

---

## 📝 License

MIT License - feel free to use this project for learning/commercial purposes!

---

## 🤝 Contributing

Contributions welcome! Please open issues or submit PRs.

---

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **Supabase** for managed PostgreSQL
- **ChromaDB** for vector storage
- **Sentence Transformers** for embeddings

---

## 📧 Contact

For questions or support, open an issue on GitHub.

---

Made with ❤️ using FastAPI, React, and AI
