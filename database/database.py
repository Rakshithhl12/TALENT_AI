"""
database/database.py — TalentAI MySQL Database Layer (Production-Ready)
---------------------------------------------------------------------
Enhancements in this version:
- Environment variable based configuration (security best practice)
- Robust error handling with logging
- Context manager usage for safe connection handling
- Thread-safe connection pooling
- Type hints for maintainability
- Centralized query execution helpers
- Production-ready initialization
"""

import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

import mysql.connector
from mysql.connector import pooling
import streamlit as st

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Database Configuration (Use Environment Variables)
# ------------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "talentai_db"),
}


# ------------------------------------------------------------------
# Connection Pool
# ------------------------------------------------------------------

@st.cache_resource
def get_pool() -> pooling.MySQLConnectionPool:
    """Create and return MySQL connection pool."""
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="talentai_pool",
            pool_size=5,
            **DB_CONFIG,
        )
        logger.info("Database connection pool created successfully")
        return pool
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise


def get_conn():
    """Get connection from pool."""
    return get_pool().get_connection()


@contextmanager
def db_cursor(dictionary: bool = False):
    """Context manager for DB cursor handling."""
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=dictionary)
        yield conn, cur
        conn.commit()
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ------------------------------------------------------------------
# Bootstrap Database
# ------------------------------------------------------------------

def create_database_if_not_exists() -> None:
    """Initialize database and tables."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )

        cur = conn.cursor()

        cur.execute("CREATE DATABASE IF NOT EXISTS talentai_db")
        cur.execute("USE talentai_db")

        # Candidates Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(50),
                role VARCHAR(255),
                skills TEXT,
                experience FLOAT DEFAULT 0,
                score FLOAT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'Pending',
                resume_text LONGTEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # Job Roles Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                required_skills TEXT,
                min_experience FLOAT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Interviews Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                candidate_id INT,
                candidate_name VARCHAR(255),
                role VARCHAR(255),
                interview_date DATE,
                interview_time TIME,
                interviewer VARCHAR(255),
                mode VARCHAR(50) DEFAULT 'Online',
                status VARCHAR(50) DEFAULT 'Scheduled',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id)
                    REFERENCES candidates(id)
                    ON DELETE SET NULL
            )
        """)

        conn.commit()
        cur.close()
        conn.close()

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


# ------------------------------------------------------------------
# Candidate Operations
# ------------------------------------------------------------------

def insert_candidate(
    name: str,
    email: str,
    phone: str,
    role: str,
    skills: str,
    experience: float,
    score: float,
    resume_text: str,
) -> int:

    query = """
        INSERT INTO candidates
        (name, email, phone, role, skills, experience, score, resume_text, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'Pending')
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            phone=VALUES(phone),
            role=VALUES(role),
            skills=VALUES(skills),
            experience=VALUES(experience),
            score=VALUES(score),
            resume_text=VALUES(resume_text),
            updated_at=CURRENT_TIMESTAMP
    """

    with db_cursor() as (conn, cur):
        cur.execute(
            query,
            (
                name,
                email,
                phone,
                role,
                skills,
                experience,
                score,
                resume_text,
            ),
        )
        return cur.lastrowid



def get_all_candidates() -> List[Dict[str, Any]]:

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute("SELECT * FROM candidates ORDER BY score DESC")
        return cur.fetchall()



def update_candidate_status(candidate_id: int, status: str) -> None:

    with db_cursor() as (_, cur):
        cur.execute(
            "UPDATE candidates SET status=%s WHERE id=%s",
            (status, candidate_id),
        )



def delete_candidate(candidate_id: int) -> None:

    with db_cursor() as (_, cur):
        cur.execute(
            "DELETE FROM candidates WHERE id=%s",
            (candidate_id,),
        )


# ------------------------------------------------------------------
# Dashboard Analytics
# ------------------------------------------------------------------

def get_dashboard_stats() -> Optional[Dict[str, Any]]:

    query = """
        SELECT
            COUNT(*) AS total,
            SUM(status='Shortlisted') AS shortlisted,
            SUM(status='Rejected') AS rejected,
            SUM(status='Hired') AS hired,
            SUM(status='Pending') AS pending,
            ROUND(AVG(score)*100, 1) AS avg_score,
            COUNT(DISTINCT role) AS roles
        FROM candidates
    """

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute(query)
        return cur.fetchone()


# ------------------------------------------------------------------
# Job Role Operations
# ------------------------------------------------------------------

def insert_job_role(
    title: str,
    description: str,
    required_skills: str,
    min_experience: float,
) -> None:

    with db_cursor() as (_, cur):
        cur.execute(
            """
            INSERT INTO job_roles
            (title, description, required_skills, min_experience)
            VALUES (%s,%s,%s,%s)
            """,
            (
                title,
                description,
                required_skills,
                min_experience,
            ),
        )



def get_all_job_roles() -> List[Dict[str, Any]]:

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute("SELECT * FROM job_roles ORDER BY created_at DESC")
        return cur.fetchall()


# ------------------------------------------------------------------
# Interview Operations
# ------------------------------------------------------------------

def schedule_interview(
    candidate_id: int,
    candidate_name: str,
    role: str,
    interview_date,
    interview_time,
    interviewer: str,
    mode: str,
    notes: str,
) -> None:

    with db_cursor() as (_, cur):
        cur.execute(
            """
            INSERT INTO interviews
            (candidate_id, candidate_name, role,
             interview_date, interview_time,
             interviewer, mode, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                candidate_id,
                candidate_name,
                role,
                interview_date,
                interview_time,
                interviewer,
                mode,
                notes,
            ),
        )



def get_all_interviews() -> List[Dict[str, Any]]:

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute(
            """
            SELECT * FROM interviews
            ORDER BY interview_date ASC, interview_time ASC
            """
        )
        return cur.fetchall()


# ------------------------------------------------------------------
# Additional Analytics Functions (Required by Dashboard)
# ------------------------------------------------------------------

def get_daily_analytics(days: int = 30) -> List[Dict[str, Any]]:
    """Return daily application counts."""

    query = """
        SELECT
            DATE(uploaded_at) AS event_date,
            COUNT(*) AS applications,
            SUM(status='Shortlisted') AS shortlisted,
            SUM(status='Rejected') AS rejected,
            SUM(status='Hired') AS hired
        FROM candidates
        WHERE uploaded_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(uploaded_at)
        ORDER BY event_date ASC
    """

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute(query, (days,))
        return cur.fetchall()


def get_role_distribution() -> List[Dict[str, Any]]:
    """Return distribution of candidates by role."""

    query = """
        SELECT role, COUNT(*) AS total
        FROM candidates
        GROUP BY role
        ORDER BY total DESC
    """

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute(query)
        return cur.fetchall()


def get_status_distribution() -> List[Dict[str, Any]]:
    """Return distribution of candidates by status."""

    query = """
        SELECT status, COUNT(*) AS total
        FROM candidates
        GROUP BY status
    """

    with db_cursor(dictionary=True) as (_, cur):
        cur.execute(query)
        return cur.fetchall()


# ------------------------------------------------------------------
# System Health Check
# ------------------------------------------------------------------

def test_connection() -> bool:
    """Verify DB connectivity."""
    try:
        with db_cursor() as (_, cur):
            cur.execute("SELECT 1")
            return True
    except Exception:
        return False
