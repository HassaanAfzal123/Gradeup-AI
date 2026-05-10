# Quick Test Script

## 1. Test Backend API Directly

Open: http://localhost:8000/docs

Try registering a user:
1. Find `POST /api/auth/register`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "quicktest@example.com",
  "password": "test123"
}
```
4. Click "Execute"

## 2. If Backend Works, Issue is Frontend

Check browser console (F12) for:
- Network errors
- CORS errors
- TypeError

## 3. Quick Fix - Restart Frontend

```powershell
# Stop frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

## 4. Alternative - Test with Simple HTML

Create `test.html` in frontend folder:
```html
<!DOCTYPE html>
<html>
<body>
<button onclick="testRegister()">Test Register</button>
<script>
async function testRegister() {
  try {
    const response = await fetch('http://localhost:8000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'test@test.com', password: 'test123' })
    });
    const data = await response.json();
    alert('Success: ' + JSON.stringify(data));
  } catch (error) {
    alert('Error: ' + error.message);
  }
}
</script>
</body>
</html>
```

Open `test.html` in browser and click the button.
