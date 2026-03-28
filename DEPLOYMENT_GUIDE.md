# GIFT Linear Equations Tutor - Deployment Guide
## Free Server Deployment with Python Backend

---

## 📋 QUICK OVERVIEW

Your tutoring app will:
1. **Frontend**: HTML/CSS/JS (interactive tutor) - served as static file
2. **Backend**: Python Flask + SQLite - stores student session data
3. **Database**: SQLite (no separate DB server needed - free!)
4. **Hosting**: Render.com, Railway.app, or PythonAnywhere (all free tier)

**Total Cost**: $0 (completely free)

---

## ✅ PHASE 1: PREPARE YOUR LOCAL FILES

### Step 1.1: Create Project Directory
```bash
mkdir gift-tutor-deployment
cd gift-tutor-deployment
```

### Step 1.2: Copy Backend Files
```bash
# Copy these files to your project folder:
- app.py                              # (provided - Flask backend)
- requirements.txt                    # (provided - Python dependencies)
- ET605_Linear_Equations_fixed.html   # (your original file)
```

### Step 1.3: Modify Your HTML to Send Data to Backend

Find this function in your HTML (around line 3124):
```javascript
function copyPayload() {
  navigator.clipboard.writeText(JSON.stringify(window._payload, null, 2))
    .then(() => { document.querySelector('.btn-copy').textContent = '(check) Copied!'; setTimeout(() => document.querySelector('.btn-copy').textContent = 'Copy JSON', 2000); })
    .catch(() => alert('Copy failed -- please select text manually.'));
}
```

**REPLACE IT WITH:**
```javascript
const API_ENDPOINT = localStorage.getItem('apiEndpoint') || 'http://localhost:5000';

function copyPayload() {
  navigator.clipboard.writeText(JSON.stringify(window._payload, null, 2))
    .then(() => { document.querySelector('.btn-copy').textContent = '(check) Copied!'; setTimeout(() => document.querySelector('.btn-copy').textContent = 'Copy JSON', 2000); })
    .catch(() => alert('Copy failed -- please select text manually.'));
}

async function saveSessionToDatabase() {
  // NEW FUNCTION: Called when session ends
  const btn = document.querySelector('[data-save-btn]');
  if (!btn) return;
  
  btn.disabled = true;
  btn.textContent = '📤 Saving...';
  
  try {
    const response = await fetch(`${API_ENDPOINT}/api/submit-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(window._payload)
    });
    
    if (response.ok) {
      const result = await response.json();
      btn.textContent = '✅ Saved!';
      console.log('Session saved:', result);
      alert(`✅ Session saved! ID: ${result.session_id}`);
    } else {
      throw new Error('Failed to save session');
    }
  } catch (error) {
    console.error('Save error:', error);
    btn.textContent = '❌ Save Failed';
    alert(`⚠️ Could not save to database: ${error.message}\n\nYou can still see your JSON above.`);
  }
}
```

### Step 1.4: Add Save Button to Report Screen

Find the report screen HTML (search for `id="reportName"`). Inside the button area, add:
```html
<button class="btn-primary" data-save-btn onclick="saveSessionToDatabase()" style="margin-top: 1rem; background: var(--teal);">
  📤 Save Session to Database
</button>
```

---

## 🚀 PHASE 2: DEPLOY BACKEND (Choose One Option)

### **OPTION A: RENDER.COM (Easiest - Recommended)**

#### Step 2A.1: Setup on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account (easy!)
3. Create a new GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   git remote add origin https://github.com/YOUR-USERNAME/gift-tutor.git
   git push -u origin main
   ```

#### Step 2A.2: Create Render Service
1. On Render dashboard, click **"New Web Service"**
2. Connect your GitHub repository
3. Fill in:
   - **Name**: `gift-tutor-backend`
   - **Root Directory**: (leave blank)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Click **"Create Web Service"**
5. Wait ~3 minutes for deployment
6. **Copy your URL** (will look like: `https://gift-tutor-backend.onrender.com`)

#### Step 2A.3: Update Frontend URL
In your HTML file, update:
```javascript
const API_ENDPOINT = 'https://gift-tutor-backend.onrender.com';
```

---

### **OPTION B: RAILWAY.APP**

#### Step 2B.1: Setup
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project → Deploy from GitHub repo
4. Select your `gift-tutor` repo
5. Railway auto-detects Flask app

#### Step 2B.2: Environment Variables
1. In Railway dashboard, go to **Variables**
2. Add:
   ```
   FLASK_ENV=production
   ```

#### Step 2B.3: Get URL
- Your app URL appears in Railway dashboard
- Update HTML with this URL

---

### **OPTION C: PYTHONANYWHERE (Most Beginner-Friendly)**

#### Step 2C.1: Setup
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up (free tier available)
3. **Web** → **Add a new web app**
4. Choose: **Flask** → **Python 3.x**

#### Step 2C.2: Upload Files
1. Go to **Files** tab
2. Upload your project files:
   - `app.py`
   - `requirements.txt`
   - `ET605_Linear_Equations_fixed.html`

#### Step 2C.3: Install Dependencies
1. Open **Bash console**
2. Run:
   ```bash
   cd /home/YOUR_USERNAME
   pip install --user -r requirements.txt
   ```

#### Step 2C.4: Configure Web App
1. Go to **Web** tab
2. Edit WSGI configuration file
3. Replace contents with:
   ```python
   import sys
   path = '/home/YOUR_USERNAME'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
4. Save and reload web app
5. Your URL: `https://YOUR_USERNAME.pythonanywhere.com`

---

## 📁 PHASE 3: SERVE HTML FRONTEND

### Option A: Host HTML on Same Server (Simplest)

**Modify `app.py`** - Add this BEFORE the `@app.route` decorators:

```python
@app.route('/')
def serve_html():
    """Serve the main tutoring application"""
    return send_file('ET605_Linear_Equations_fixed.html', mimetype='text/html')

@app.route('/api/health', methods=['GET'])
def health():
    ...
```

Then:
1. Place `ET605_Linear_Equations_fixed.html` in the same folder as `app.py`
2. Redeploy to Render/Railway/PythonAnywhere
3. Access at: `https://your-domain.com/`

### Option B: Host HTML Separately (More Flexible)

Use **Netlify, Vercel, or GitHub Pages**:

1. Create folder `public/` with your HTML
2. Deploy to Netlify (drag & drop):
   - Go to [netlify.com](https://netlify.com)
   - Drag your HTML file
   - Get a free URL
3. Update in HTML:
   ```javascript
   const API_ENDPOINT = 'https://gift-tutor-backend.onrender.com';
   ```

---

## 🗄️ PHASE 4: VERIFY DATABASE & API

### Step 4.1: Test Backend is Running
```bash
curl https://your-backend-url.com/health
# Response: {"status":"ok","message":"GIFT Tutor Backend is running"}
```

### Step 4.2: Test Data Submission
Use Postman or curl:
```bash
curl -X POST https://your-backend-url.com/api/submit-session \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test001",
    "session_id": "sess_abc123",
    "chapter_id": "linear_eq_1",
    "timestamp": "2024-01-01T10:00:00Z",
    "correct_answers": 15,
    "wrong_answers": 5,
    "questions_attempted": 20,
    "total_questions": 50,
    "hints_used": 3,
    "time_spent_seconds": 1800
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Session saved successfully",
  "session_id": "sess_abc123",
  "db_id": 1
}
```

---

## 📊 PHASE 5: VIEW YOUR DATA

### Access Student Sessions
```
GET: https://your-backend-url.com/api/student/test001/sessions
```

### View Global Statistics
```
GET: https://your-backend-url.com/api/stats
```

### Export All Data as CSV
```
GET: https://your-backend-url.com/api/export/csv
```

### View Specific Session
```
GET: https://your-backend-url.com/api/sessions/sess_abc123
```

---

## 🛠️ PHASE 6: LOCAL TESTING (Before Deployment)

### Step 6.1: Install Dependencies Locally
```bash
pip install -r requirements.txt
```

### Step 6.2: Run Backend Locally
```bash
python app.py
```
Should see:
```
✓ Database initialized successfully
 * Running on http://0.0.0.0:5000/
```

### Step 6.3: Test Frontend
1. Open `ET605_Linear_Equations_fixed.html` in browser
2. Go through a sample session
3. Click "Save Session to Database"
4. Check backend console for success message

### Step 6.4: Check SQLite Database
```bash
sqlite3 instance/tutor.db
sqlite> SELECT * FROM sessions;
```

---

## 📝 FILE STRUCTURE

After setup, your project should look like:
```
gift-tutor-deployment/
├── app.py                              # Flask backend
├── requirements.txt                    # Dependencies
├── ET605_Linear_Equations_fixed.html   # Frontend (modified)
├── instance/
│   └── tutor.db                        # SQLite database (auto-created)
└── .gitignore                          # (Optional - see below)
```

### Create `.gitignore`
```
instance/
__pycache__/
*.pyc
.env
.DS_Store
```

---

## 🔒 SECURITY NOTES

1. **CORS is enabled** - for frontend/backend communication
2. **SQLite is local** - data stored on server, no external DB needed
3. **For Production**:
   - Use environment variables for sensitive config
   - Add authentication for admin endpoints
   - Use HTTPS (automatic on Render, Railway, PythonAnywhere)

---

## 🚨 TROUBLESHOOTING

### Backend not responding
- Check logs in Render/Railway dashboard
- Verify `requirements.txt` matches your Python version
- Ensure `app.py` has no syntax errors

### Data not saving
- Check browser console (F12) for errors
- Verify API endpoint URL is correct
- Check backend logs for database errors

### Database errors
- Delete `instance/tutor.db` and restart
- Backend will auto-create empty database

### CORS errors
- Already handled in code with `CORS(app)`
- If still getting errors, check your request headers

---

## 📞 NEXT STEPS

After deployment:
1. Share your HTML URL with students
2. Students enter name & ID
3. Complete tutoring session
4. Click "Save Session to Database"
5. View results at `/api/student/{student_id}/sessions`

**Test with a few students first**, then scale up!

---

## 💡 OPTIONAL ENHANCEMENTS

### Add Admin Dashboard
```python
@app.route('/admin/dashboard')
def admin_dashboard():
    stats = Session.query.all()
    return render_template('dashboard.html', stats=stats)
```

### Send Completion Emails
```python
from flask_mail import Mail, Message

@app.after_request
def send_completion_email(student_email):
    msg = Message('Tutor Session Completed', recipients=[student_email])
    mail.send(msg)
```

### Generate Performance Reports
Export data to PDF/Excel for teacher review.

---

**✅ You're all set! Follow the phases in order and you'll have a fully functional free tutoring app.**
