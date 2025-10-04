# Starting the WeBWorK Application

## Prerequisites

Make sure you have:
- ✅ Conda environment activated: `conda activate pytorch-5090`
- ✅ Database created: `python scripts/import_problems.py`
- ✅ PS1 problems imported: `python scripts/import_ps1.py`
- ✅ Node/pnpm installed: `pnpm install` (run once)

## Quick Start

### 1. Start Backend (Terminal 1/PowerShell)

**Windows (PowerShell):**
```powershell
cd D:\pg\apps\backend
C:\Users\mdahl\.conda\envs\pytorch-5090\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or with conda active:**
```bash
conda activate pytorch-5090
cd d:/pg/apps/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
[DEBUG] Python path: C:\Users\mdahl\.conda\envs\pytorch-5090\python.exe
[SUCCESS] Database rendering router loaded!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 2. Start Frontend (Terminal 2/PowerShell)

**Windows (PowerShell):**
```powershell
cd D:\pg
pnpm dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Open Browser
Navigate to: **http://localhost:5173**

You should see:
- **182 total problems** (157 Tutorial + 25 PS1)
- **Collection tabs**: All, Tutorial, Problem Set 1
- **Search bar** and **subject filters**

## Troubleshooting

### Backend Error: "Database not found"
Run the import scripts first:
```bash
cd d:/pg
python scripts/import_problems.py
python scripts/import_ps1.py
```

### Frontend Error: "HTTP error! status: 422"

**This means the backend is NOT running!** The frontend is trying to reach `/api/*` endpoints but the backend server on port 8000 is not responding.

**Solution**: Start the backend in Terminal 1 first (see step 1 above)

**Verify backend is running:**
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"ok"}

# Or test in PowerShell:
Invoke-WebRequest -Uri http://localhost:8000/api/health
# Should return: StatusCode: 200
```

If you see connection errors, the backend is not running. Go back to step 1.

### Backend Import Errors
Make sure you're in the correct environment:
```bash
# Activate your conda environment
conda activate pytorch-5090

# Install dependencies
cd d:/pg
pip install -e packages/pg_renderer
pip install -e apps/backend[dev]
```

## API Endpoints

Once running, you can test these endpoints:

- Health: http://localhost:8000/api/health
- Search: http://localhost:8000/api/problems/search?limit=10
- Collections: http://localhost:8000/api/problems/collections/list
- Docs: http://localhost:8000/docs (FastAPI automatic documentation)

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Backend**: Changes to `.py` files auto-reload
- **Frontend**: Changes to `.tsx` files auto-update in browser

### Viewing Logs
- **Backend**: Logs appear in Terminal 1
- **Frontend**: Logs in Terminal 2 + Browser console (F12)

### Database Queries
View database directly:
```bash
sqlite3 problems.db
.tables
SELECT COUNT(*) FROM problems;
.quit
```
