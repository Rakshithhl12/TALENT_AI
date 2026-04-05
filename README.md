# 🚀 TalentAI Enterprise Recruitment Platform — v2.0

AI-powered resume screening, job matching, interview scheduling, and HR analytics.
**Full MySQL backend · Real-time data · Claude AI Chatbot**

---

## 📁 Project Structure

```
TalentAI_Complete/
├── app.py                        ← Main Streamlit entry point
├── requirements.txt
├── setup_mysql.sql               ← Run this FIRST to create DB + seed data
├── .streamlit/
│   └── config.toml               ← Dark theme
├── database/
│   └── database.py               ← All MySQL queries (connection pool + CRUD)
├── pages/
│   ├── dashboard.py              ← Real-time KPIs + charts
│   ├── resume_upload.py          ← Upload PDF/DOCX → parse → score → MySQL
│   ├── resume_ranking.py         ← Live ranked candidates + status updates
│   ├── bulk_processing.py        ← Bulk re-score / status update / delete
│   ├── job_matching.py           ← Role-based matching + JD management
│   ├── interview_scheduler.py    ← Schedule/manage interviews in MySQL
│   ├── analytics.py              ← 6 real-time Plotly charts from MySQL
│   ├── report_generation.py      ← CSV + multi-sheet Excel export
│   └── chatbot.py                ← Claude AI chatbot with live DB context
└── utils/
    ├── resume_parser.py          ← PDF/DOCX text + metadata extraction
    └── bert_scorer.py            ← BERT similarity (TF-IDF fallback)
```

---

## ⚡ Quick Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MySQL credentials

Edit **`database/database.py`** → `DB_CONFIG`:

```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "YOUR_MYSQL_PASSWORD",   # ← change this
    "database": "talentai_db",
}
```

### 3. Create database & seed sample data

```bash
mysql -u root -p < setup_mysql.sql
```

This creates:
- `talentai_db` database
- `candidates`, `job_roles`, `interviews` tables
- 10 sample candidates, 5 job roles, 4 interviews

### 4. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🔧 Module Guide

| Module | What it does |
|--------|-------------|
| **Dashboard** | Live KPI metrics (total, shortlisted, hired, avg score) + 3 charts |
| **Resume Upload** | Upload PDF/DOCX → auto-extract name/email/skills → score vs JD → save to MySQL |
| **Resume Ranking** | View all candidates ranked by AI score; update status inline |
| **Bulk Processing** | Re-score all resumes, bulk status change, bulk delete |
| **Role-Based Matching** | Add job roles to DB; live-match all candidates against any JD |
| **Interview Scheduler** | Schedule interviews from shortlisted pool; manage status |
| **Analytics** | Trend lines, pie charts, scatter, skill frequency — all from MySQL |
| **Report Generation** | Download CSV or multi-sheet Excel for any report type |
| **HR Chatbot** | Ask Claude AI questions about HR + your live candidate data |

---

## 🤖 Scoring Engine

The app uses **BERT semantic similarity** (`sentence-transformers/all-MiniLM-L6-v2`)
to compute how well a resume matches a job description.

If `sentence-transformers` is not installed or fails to load (e.g., no internet
for model download), it automatically falls back to **TF-IDF cosine similarity**
so the app always works.

---

## 🗄️ MySQL Tables

### `candidates`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto ID |
| name | VARCHAR | Candidate name |
| email | VARCHAR UNIQUE | Email |
| phone | VARCHAR | Phone number |
| role | VARCHAR | Applied role |
| skills | TEXT | Extracted skills |
| experience | FLOAT | Years of experience |
| score | FLOAT | AI match score (0–1) |
| status | VARCHAR | Pending/Shortlisted/Rejected/Hired/On Hold |
| resume_text | LONGTEXT | Full extracted resume text |
| uploaded_at | DATETIME | When added |

### `job_roles`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto ID |
| title | VARCHAR | Job title |
| description | TEXT | Full JD |
| required_skills | TEXT | Skills list |
| min_experience | FLOAT | Min years required |

### `interviews`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto ID |
| candidate_id | INT FK | Links to candidates.id |
| candidate_name | VARCHAR | Denormalised name |
| role | VARCHAR | Role interviewed for |
| interview_date | DATE | Scheduled date |
| interview_time | TIME | Scheduled time |
| interviewer | VARCHAR | Interviewer / panel |
| mode | VARCHAR | Online / In-Person / Phone |
| status | VARCHAR | Scheduled/Completed/Cancelled |
| notes | TEXT | Agenda / instructions |

---

## 🔑 HR Chatbot (Claude AI)

The chatbot pulls **live stats from MySQL** before every request and sends them
as context to Claude claude-sonnet-4-20250514. It can answer questions like:

- *"Who are the top 5 candidates for Data Scientist?"*
- *"How many candidates are pending review?"*
- *"Write interview questions for an ML Engineer role."*
- *"What's our hiring accuracy this month?"*

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `MySQL connection refused` | Start MySQL: `sudo service mysql start` |
| `Access denied for user root` | Check password in `DB_CONFIG` |
| `No module named sentence_transformers` | `pip install sentence-transformers` — app uses TF-IDF fallback until installed |
| `streamlit: command not found` | `pip install streamlit` then try `python -m streamlit run app.py` |
| BERT model slow first load | It downloads ~90MB model on first use; subsequent runs are instant |
