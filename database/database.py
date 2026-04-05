"""
database/database.py — TalentAI MySQL Database Layer
Deployable on Streamlit Cloud via st.secrets.
Credentials read from .streamlit/secrets.toml (local) or Streamlit Cloud secrets.
"""

import streamlit as st
import mysql.connector
from mysql.connector import pooling

# ── Read credentials from st.secrets ──────────────────────
# Local:  .streamlit/secrets.toml
# Cloud:  Streamlit Cloud → App Settings → Secrets
def _cfg():
    try:
        db = st.secrets["mysql"]
        return {
            "host":     db.get("host",     "localhost"),
            "port":     int(db.get("port", 3306)),
            "user":     db.get("user",     "root"),
            "password": db.get("password", ""),
            "database": db.get("database", "talentai_db"),
        }
    except Exception:
        # Fallback for local dev without secrets file
        return {
            "host":     "localhost",
            "port":     3306,
            "user":     "root",
            "password": "Rakshith@123",
            "database": "talentai_db",
        }


@st.cache_resource
def _get_pool():
    cfg = _cfg()
    return pooling.MySQLConnectionPool(
        pool_name="talentai",
        pool_size=5,
        **cfg,
    )


def get_conn():
    return _get_pool().get_connection()


# ── Bootstrap ──────────────────────────────────────────────

def create_database_if_not_exists():
    cfg = _cfg()
    # Connect without specifying DB first so we can CREATE it
    bare = mysql.connector.connect(
        host=cfg["host"], port=cfg["port"],
        user=cfg["user"], password=cfg["password"],
    )
    cur = bare.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`")
    cur.execute(f"USE `{cfg['database']}`")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255)  NOT NULL,
            email       VARCHAR(255)  UNIQUE,
            phone       VARCHAR(50),
            role        VARCHAR(255),
            skills      TEXT,
            experience  FLOAT         DEFAULT 0,
            score       FLOAT         DEFAULT 0,
            status      VARCHAR(50)   DEFAULT 'Pending',
            resume_text LONGTEXT,
            uploaded_at DATETIME      DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_roles (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            title            VARCHAR(255) NOT NULL,
            description      TEXT,
            required_skills  TEXT,
            min_experience   FLOAT DEFAULT 0,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            candidate_id    INT,
            candidate_name  VARCHAR(255),
            role            VARCHAR(255),
            interview_date  DATE,
            interview_time  TIME,
            interviewer     VARCHAR(255),
            mode            VARCHAR(50)  DEFAULT 'Online',
            status          VARCHAR(50)  DEFAULT 'Scheduled',
            notes           TEXT,
            created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL
        )
    """)
    bare.commit()
    cur.close()
    bare.close()


# ── Candidates ─────────────────────────────────────────────

def insert_candidate(name, email, phone, role, skills, experience, score, resume_text):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO candidates (name,email,phone,role,skills,experience,score,resume_text,status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'Pending')
        ON DUPLICATE KEY UPDATE
            name=VALUES(name), phone=VALUES(phone), role=VALUES(role),
            skills=VALUES(skills), experience=VALUES(experience),
            score=VALUES(score), resume_text=VALUES(resume_text),
            updated_at=CURRENT_TIMESTAMP
    """, (name,email,phone,role,skills,experience,score,resume_text))
    conn.commit(); cid = cur.lastrowid
    cur.close(); conn.close()
    return cid


def get_all_candidates():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM candidates ORDER BY score DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def get_candidates_by_role(role):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM candidates WHERE role=%s ORDER BY score DESC", (role,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def update_candidate_status(candidate_id, status):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE candidates SET status=%s WHERE id=%s", (status, candidate_id))
    conn.commit(); cur.close(); conn.close()


def delete_candidate(candidate_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM candidates WHERE id=%s", (candidate_id,))
    conn.commit(); cur.close(); conn.close()


def get_dashboard_stats():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            COUNT(*)                        AS total,
            SUM(status='Shortlisted')       AS shortlisted,
            SUM(status='Rejected')          AS rejected,
            SUM(status='Hired')             AS hired,
            SUM(status='Pending')           AS pending,
            ROUND(AVG(score)*100,1)         AS avg_score,
            COUNT(DISTINCT role)            AS roles
        FROM candidates
    """)
    row = cur.fetchone(); cur.close(); conn.close()
    return row


# ── Job Roles ──────────────────────────────────────────────

def insert_job_role(title, description, required_skills, min_experience):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO job_roles (title,description,required_skills,min_experience)
        VALUES (%s,%s,%s,%s)
    """, (title, description, required_skills, min_experience))
    conn.commit(); cur.close(); conn.close()


def get_all_job_roles():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM job_roles ORDER BY created_at DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def get_job_role_titles():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT title FROM job_roles ORDER BY title")
    rows = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows or ["Data Scientist","Data Analyst","ML Engineer","Backend Developer","Frontend Developer"]


def delete_job_role(role_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM job_roles WHERE id=%s", (role_id,))
    conn.commit(); cur.close(); conn.close()


# ── Interviews ─────────────────────────────────────────────

def schedule_interview(candidate_id, candidate_name, role,
                       interview_date, interview_time, interviewer, mode, notes):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO interviews
            (candidate_id,candidate_name,role,interview_date,
             interview_time,interviewer,mode,notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (candidate_id,candidate_name,role,interview_date,
          interview_time,interviewer,mode,notes))
    conn.commit(); cur.close(); conn.close()


def get_all_interviews():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM interviews ORDER BY interview_date ASC, interview_time ASC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def update_interview_status(interview_id, status):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE interviews SET status=%s WHERE id=%s", (status, interview_id))
    conn.commit(); cur.close(); conn.close()


def delete_interview(interview_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM interviews WHERE id=%s", (interview_id,))
    conn.commit(); cur.close(); conn.close()


# ── Analytics ──────────────────────────────────────────────

def get_daily_analytics(days=30):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            DATE(uploaded_at)           AS event_date,
            COUNT(*)                    AS applications,
            SUM(status='Shortlisted')   AS shortlisted,
            SUM(status='Rejected')      AS rejected,
            SUM(status='Hired')         AS hired
        FROM candidates
        WHERE uploaded_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(uploaded_at)
        ORDER BY event_date ASC
    """, (days,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def get_role_distribution():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT role, COUNT(*) AS total FROM candidates GROUP BY role ORDER BY total DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def get_score_distribution():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            CASE
                WHEN score>=0.8 THEN 'Excellent (80-100%)'
                WHEN score>=0.6 THEN 'Good (60-79%)'
                WHEN score>=0.4 THEN 'Average (40-59%)'
                ELSE 'Low (<40%)'
            END AS band,
            COUNT(*) AS total
        FROM candidates
        GROUP BY band
        ORDER BY MIN(score) DESC
    """)
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows


def get_status_distribution():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT status, COUNT(*) AS total FROM candidates GROUP BY status")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows
