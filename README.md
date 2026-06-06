# 📚 Wisdom Library — Setup Guide

## Folder Structure
```
wisdom-library/
├── app.py            ← Flask backend (API routes)
├── database.py       ← SQLite database logic
├── index.html        ← Frontend UI
├── requirements.txt  ← Python dependencies
└── wisdom_library.db ← Auto-created on first run
```

---

## Step 1 — Install Python
Make sure Python 3.8+ is installed.
Check with: `python --version`

Download from https://python.org if needed.

---

## Step 2 — Create a Virtual Environment (recommended)
```bash
cd wisdom-library
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

---

## Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Step 4 — Run the App
```bash
python app.py
```

You'll see:
```
✅ Wisdom Library running at http://localhost:5000
```

---

## Step 5 — Open in Browser
Go to: **http://localhost:5000**

That's it! The database (`wisdom_library.db`) is created automatically on first run.

---

## API Endpoints (for reference)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/students | Get all students |
| POST | /api/students | Add a student |
| PUT | /api/students/:id | Update a student |
| DELETE | /api/students/:id | Delete a student |
| GET | /api/attendance/:date | Get attendance for a date |
| POST | /api/attendance | Mark single attendance |
| POST | /api/attendance/bulk | Mark all present/absent |
| GET | /api/fees?month=YYYY-M | Get fee status for month |
| POST | /api/fees | Update fee status |
| GET | /api/stats?date=&month= | Dashboard stats |

---

## Notes
- Data is stored in `wisdom_library.db` (SQLite file) — no external database needed.
- To reset all data, just delete `wisdom_library.db` and restart.
- The app runs on port `5000` by default.