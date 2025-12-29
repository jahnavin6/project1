import os
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any

from .config import DB_PATH


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)


@contextmanager
def _conn_ctx():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    with _conn_ctx() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                error_rate REAL NOT NULL,
                cpu_pct REAL NOT NULL,
                scenario TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                scenario TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                score REAL NOT NULL,
                summary TEXT NOT NULL,
                top_cluster TEXT NOT NULL,
                sample_log TEXT NOT NULL,
                scenario TEXT NOT NULL
            )
            """
        )


def insert_metric(metric: Dict[str, Any]) -> None:
    with _conn_ctx() as conn:
        conn.execute(
            """
            INSERT INTO metrics (ts, latency_ms, error_rate, cpu_pct, scenario)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                metric["ts"],
                metric["latency_ms"],
                metric["error_rate"],
                metric["cpu_pct"],
                metric["scenario"],
            ),
        )


def insert_log(log: Dict[str, Any]) -> None:
    with _conn_ctx() as conn:
        conn.execute(
            """
            INSERT INTO logs (ts, level, message, scenario)
            VALUES (?, ?, ?, ?)
            """,
            (log["ts"], log["level"], log["message"], log["scenario"]),
        )


def insert_incident(incident: Dict[str, Any]) -> None:
    with _conn_ctx() as conn:
        conn.execute(
            """
            INSERT INTO incidents (ts, score, summary, top_cluster, sample_log, scenario)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                incident["ts"],
                incident["score"],
                incident["summary"],
                incident["top_cluster"],
                incident["sample_log"],
                incident["scenario"],
            ),
        )


def fetch_recent_metrics(limit: int) -> List[Dict[str, Any]]:
    with _conn_ctx() as conn:
        cur = conn.execute(
            """
            SELECT ts, latency_ms, error_rate, cpu_pct, scenario
            FROM metrics
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "ts": row[0],
            "latency_ms": row[1],
            "error_rate": row[2],
            "cpu_pct": row[3],
            "scenario": row[4],
        }
        for row in rows[::-1]
    ]


def fetch_recent_logs(limit: int) -> List[Dict[str, Any]]:
    with _conn_ctx() as conn:
        cur = conn.execute(
            """
            SELECT ts, level, message, scenario
            FROM logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "ts": row[0],
            "level": row[1],
            "message": row[2],
            "scenario": row[3],
        }
        for row in rows[::-1]
    ]


def fetch_recent_incidents(limit: int) -> List[Dict[str, Any]]:
    with _conn_ctx() as conn:
        cur = conn.execute(
            """
            SELECT ts, score, summary, top_cluster, sample_log, scenario
            FROM incidents
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "ts": row[0],
            "score": row[1],
            "summary": row[2],
            "top_cluster": row[3],
            "sample_log": row[4],
            "scenario": row[5],
        }
        for row in rows[::-1]
    ]


def fetch_last_incident_ts() -> str:
    with _conn_ctx() as conn:
        cur = conn.execute(
            """
            SELECT ts
            FROM incidents
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    return row[0] if row else ""
