# Testing Guide for Gradeup AI

## Quick Start Testing

### 1. Run Backend (with LangChain)
```bash
cd backend
python -m uvicorn main:app --reload
```

**What to look for:**
- ✅ "Logging configured successfully" (JSON logging working)
- ✅ "Gradeup AI ready" message
- ✅ No errors about LangChain imports

**Check logs:**
```bash
# View logs in real-time
type logs\app.log
```

### 2. Run Automated Tests
```bash
# From backend directory
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov

# Run specific test file
pytest tests/test_auth.py -v
```

**Expected output:**
```
tests/test_auth.py::test_register_success PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_integration.py::test_health_check PASSED
...
```

### 3. Run Frontend
```bash
cd frontend
npm run dev
```

**Access at:** http://localhost:5173

### 4. Test Docker Compose
```bash
# From project root
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Stop services
docker-compose down
```

## Testing New LangChain Features

### Test 1: Chat with LangChain RAG
1. Upload a PDF
2. Go to Chat
3. Ask a question
4. **Difference:** Answers now use LangChain RetrievalQA chain
5. Check `logs/app.log` for structured logs

### Test 2: Quiz Generation with Agent
1. Go to Quiz page
2. Select PDF + difficulty
3. Leave topic empty (tests new optional feature)
4. **Difference:** Questions generated via LangChain agent
5. Check console for cleaner error handling

### Test 3: Logging
```bash
# View JSON logs
type backend\logs\app.log

# Each log entry looks like:
{
  "timestamp": "2024-12-28T14:30:00Z",
  "level": "INFO",
  "message": "Quiz generation requested",
  "user_id": "123",
  "pdf_id": "456",
  "difficulty": "medium"
}
```

## Verify Documentation

### Architecture Diagram
```bash
# Open in markdown viewer
code docs/ARCHITECTURE.md
```
**Contains:**
- Mermaid diagram of system
- Component descriptions
- Data flow diagrams

### Engineering Report
```bash
code docs/ENGINEERING_REPORT.md
```
**Contains:**
- Problem statement
- Technical implementation
- Testing & deployment

## Common Issues

### Issue: "LangChain not found"
**Fix:** `pip install langchain langchain-groq langchain-community`

### Issue: Tests fail with database error
**Fix:** Tests use SQLite in-memory DB, should work automatically

### Issue: Docker Compose fails
**Fix:** Ensure Docker Desktop is running

### Issue: No logs appearing
**Fix:** Logs created after first API request, try accessing `/health`

## Success Criteria

✅ Backend starts without errors
✅ Logs appear in JSON format
✅ Tests pass (at least basic auth tests)
✅ Frontend loads successfully
✅ Docker Compose brings up all services
✅ Documentation renders correctly
