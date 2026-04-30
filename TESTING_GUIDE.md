# Career Compass — Testing & Deployment Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- ANTHROPIC_API_KEY set in `.env`

### Step 1: Start the FastAPI Backend (Terminal 1)
```bash
cd "c:/Users/callu/Desktop/ANLP Group Project"
python -m uvicorn main:app --reload
```
✓ Backend runs on `http://localhost:8000`

### Step 2: Start the React Frontend (Terminal 2)
```bash
cd "c:/Users/callu/Desktop/ANLP Group Project/frontend"
npm run dev
```
✓ Frontend runs on `http://localhost:5173`

### Step 3: Open in Browser
- Go to `http://localhost:5173`
- You should see the Career Compass landing page
- Click "Get Started →"

---

## 🧪 Automated Testing

### Run Backend Tests
```bash
cd "c:/Users/callu/Desktop/ANLP Group Project"
python test_system.py
```

This tests all 5 endpoints:
- ✓ GET /health
- ✓ POST /api/extract-skills
- ✓ POST /api/match-jobs
- ✓ POST /api/analyze-gaps
- ✓ POST /api/extract-from-pdf

Expected output:
```
✓ PASS | Health Check
✓ PASS | Extract Skills
✓ PASS | Match Jobs
✓ PASS | Analyze Gaps
✓ PASS | Extract From PDF

Passed: 5/5 | Failed: 0/5
```

---

## 📋 Manual Testing Checklist

### Test 1: Text-Based Brain Dump
**Goal:** Verify text input → skill extraction flow

1. Go to `http://localhost:5173`
2. Click "Get Started →"
3. Paste the sample text (or use "Use Sample Text" button)
4. Click "Extract My Skills"
5. **Expected:** Shows 10+ detected skills
6. Click "Find My Job Matches →"
7. Click "Find My Matches"
8. **Expected:** Shows top 6 job matches with scores
9. Click "Generate My Roadmap →"
10. Click "Generate My Roadmap"
11. **Expected:** Shows missing skills + 30-day plan (4 weeks)
12. Test "Download Plan" button

### Test 2: PDF Resume Upload
**Goal:** Verify PDF → text extraction → skill extraction flow

1. Go to Step 1 (Brain Dump page)
2. Click the PDF upload area (or drag-drop a PDF)
3. Select any PDF resume or document
4. **Expected:** Shows "PDF uploaded successfully. X words extracted."
5. The system should automatically extract skills from the PDF
6. **Expected:** Shows 5+ detected skills
7. Complete the flow (Match → Roadmap)

### Test 3: Sample Student Profiles

Test with 5 different brain dumps to validate extraction quality:

#### Profile 1: Data Analyst
```
I completed a Business Analytics degree at UTS. I have strong skills in Excel, SQL, and Tableau. 
In my internship at a financial company, I built dashboards using Power BI and analyzed datasets 
with Python and pandas. I also have AWS and Snowflake experience.
```
**Expected:** Extract: Python, SQL, Tableau, Power BI, Excel, AWS, Snowflake, pandas

#### Profile 2: Software Engineer
```
I've been developing in Python and JavaScript for 3 years. My backend experience includes FastAPI, 
Django, and REST APIs. Frontend work: React, Vue, HTML/CSS. I use Git daily, familiar with CI/CD, 
Docker, and Kubernetes. Recently learning Golang and interested in cloud deployment on AWS.
```
**Expected:** Extract: Python, JavaScript, FastAPI, Django, React, Vue, Git, Docker, Kubernetes, AWS

#### Profile 3: Data Science / ML Specialist
```
Master's in Data Science from UNSW. Proficient in Python, R, and SQL. Machine learning experience 
with scikit-learn, TensorFlow, and PyTorch. Deep learning projects with neural networks. Data 
visualization in Matplotlib, Seaborn, and Plotly. Cloud platforms: Azure and GCP.
```
**Expected:** Extract: Python, R, SQL, scikit-learn, TensorFlow, PyTorch, Machine Learning, Azure, GCP

#### Profile 4: Business Analyst / Product Manager
```
5 years experience in business operations and product management. Skilled in requirements gathering, 
stakeholder management, and Agile/Scrum methodologies. Technical knowledge of APIs, databases, and 
SQL queries. Tools: Jira, Excel, Tableau for dashboards. Recently learned Power BI and data visualization.
```
**Expected:** Extract: SQL, Tableau, Power BI, Jira, Agile, Scrum, Excel, Requirements Gathering

#### Profile 5: DevOps / Cloud Infrastructure
```
DevOps engineer with 6 years experience. Expert in CI/CD pipelines, Jenkins, GitLab. Infrastructure 
as Code: Terraform, Ansible. Containerization: Docker, Kubernetes. Cloud platforms: AWS (EC2, S3, RDS), 
Azure. Monitoring: Prometheus, Grafana. Linux system administration.
```
**Expected:** Extract: Docker, Kubernetes, AWS, Azure, Terraform, CI/CD, Git, Prometheus, Grafana

---

## 🔍 Edge Cases to Test

### Test Empty Input
1. Go to Step 1
2. Click "Extract My Skills" without pasting anything
3. **Expected:** Error message: "Please paste some experience text or upload a resume PDF."

### Test Very Short Input
1. Paste: "I know Python"
2. Click "Extract My Skills"
3. **Expected:** Error message: "Your text is only 3 words. Add more detail..."

### Test No Skills Detected
1. Paste: "The weather is nice today and I like to play sports"
2. Click "Extract My Skills"
3. **Expected:** Message: "No skills were detected. Try adding more specific tool names..."

### Test Invalid PDF
1. Try uploading a non-PDF file (.txt, .doc, etc.)
2. **Expected:** Error: "File must be a PDF"

### Test Navigation Guards
1. Go directly to `http://localhost:5173/matches`
2. **Expected:** Redirected back to `/brain-dump`
3. Go to `http://localhost:5173/roadmap` without completing previous steps
4. **Expected:** Redirected back to `/matches`

---

## 📊 Performance Testing

### Response Times (Expected)
| Endpoint | Time |
|----------|------|
| `/health` | <100ms |
| `/api/extract-skills` | 0.5-1s |
| `/api/match-jobs` | 0.2-0.5s |
| `/api/analyze-gaps` | 5-10s (Claude API call) |
| `/api/extract-from-pdf` | 1-3s |

### Stress Test (Optional)
```bash
# Test extraction 10 times
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/extract-skills \
    -H "Content-Type: application/json" \
    -d '{"text": "I know Python, SQL, and Power BI"}'
  echo "Test $i completed"
done
```

---

## 🐛 Troubleshooting

### Issue: "Backend not running"
```
Error: Failed to connect to http://localhost:8000
```
**Solution:**
```bash
cd "c:/Users/callu/Desktop/ANLP Group Project"
python -m uvicorn main:app --reload
```

### Issue: "ChromaDB not found"
```
Error: Job database not found or empty
```
**Solution:**
```bash
cd "c:/Users/callu/Desktop/ANLP Group Project"
python scripts/ingest_jobs.py
```

### Issue: "ANTHROPIC_API_KEY not found"
```
Error: Secret 'ANTHROPIC_API_KEY' not found
```
**Solution:**
1. Create `.env` file in project root
2. Add: `ANTHROPIC_API_KEY=your_key_here`
3. Restart backend

### Issue: "Module not found" errors
```
ModuleNotFoundError: No module named 'pdfplumber'
```
**Solution:**
```bash
pip install pdfplumber
```

### Issue: React won't load
```
Cannot GET http://localhost:5173
```
**Solution:**
```bash
cd frontend
npm install
npm run dev
```

### Issue: PDF upload returns 413
```
Error: Payload too large
```
**Solution:** FastAPI has a default 25MB limit. Files under 25MB should work fine.

---

## ✅ Final Checklist Before Submission

- [ ] Backend starts without errors: `uvicorn main:app --reload`
- [ ] React frontend starts: `npm run dev`
- [ ] All 5 automated tests pass: `python test_system.py`
- [ ] Brain dump text extraction works (detects 10+ skills)
- [ ] PDF upload works (accepts .pdf files, extracts text)
- [ ] Job matching shows top 6 matches with similarity scores
- [ ] Roadmap generation produces 4-week plan with missing skills
- [ ] Navigation guards prevent skipping steps
- [ ] Download plan button works
- [ ] No console errors in browser DevTools
- [ ] App works on different screen sizes (responsive)

---

## 🌐 Deployment (Optional)

### Deploy Backend to Railway/Heroku
```bash
# Push to GitHub first
git add .
git commit -m "Add PDF resume upload feature"
git push origin main

# Connect to Railway / Heroku
# Set ANTHROPIC_API_KEY in environment variables
# Deploy!
```

### Deploy Frontend to Vercel
```bash
# In frontend/ directory
npm install -g vercel
vercel

# Set VITE_API_URL env var to your backend URL
```

---

## 📞 Support

If tests fail:
1. Check the error message carefully
2. Verify all dependencies are installed: `pip list | grep -E "fastapi|pdfplumber|anthropic|chromadb"`
3. Verify spaCy model is installed: `python -m spacy validate`
4. Check logs in both backend and frontend terminals
5. Restart both servers

Good luck! 🚀
