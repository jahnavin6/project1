import asyncio
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, Query

from .config import (
    APP_NAME,
    SAMPLE_INTERVAL_SEC,
    RECENT_LOG_LIMIT,
    INCIDENT_COOLDOWN_SEC,
)
from .detector import AnomalyDetector
from .simulator import ScenarioState, next_event
from .storage import (
    init_db,
    insert_incident,
    insert_log,
    insert_metric,
    fetch_recent_metrics,
    fetch_recent_incidents,
    fetch_recent_logs,
)
from .summarizer import summarize_logs

app = FastAPI(title=APP_NAME)


def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RuntimeState:
    def __init__(self) -> None:
        self.scenario = ScenarioState()
        self.detector = AnomalyDetector()
        self.last_incident_ts = None


state = RuntimeState()


async def pipeline_loop() -> None:
    while True:
        event = next_event(state.scenario)
        metric = event["metric"]
        log = event["log"]

        insert_metric(metric)
        insert_log(log)

        vector = [
            metric["latency_ms"],
            metric["error_rate"],
            metric["cpu_pct"],
        ]
        score, is_anomaly = state.detector.update(vector)

        if is_anomaly and _cooldown_elapsed():
            summary = summarize_logs(fetch_recent_logs(RECENT_LOG_LIMIT))
            incident = {
                "ts": _now_ts(),
                "score": round(score or 0.0, 4),
                "summary": (
                    "Anomaly detected: latency "
                    f"{metric['latency_ms']}ms, error "
                    f"{metric['error_rate']}%, cpu "
                    f"{metric['cpu_pct']}%"
                ),
                "top_cluster": summary["top_cluster"],
                "sample_log": summary["sample_log"],
                "scenario": metric["scenario"],
            }
            insert_incident(incident)
            state.last_incident_ts = datetime.now(timezone.utc)

        await asyncio.sleep(SAMPLE_INTERVAL_SEC)


def _cooldown_elapsed() -> bool:
    if state.last_incident_ts is None:
        return True
    elapsed = datetime.now(timezone.utc) - state.last_incident_ts
    return elapsed.total_seconds() >= INCIDENT_COOLDOWN_SEC


@app.on_event("startup")
async def startup_event() -> None:
    init_db()
    asyncio.create_task(pipeline_loop())


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/metrics")
def metrics(limit: int = Query(300, ge=10, le=2000)) -> List[dict]:
    return fetch_recent_metrics(limit)


@app.get("/api/incidents")
def incidents(limit: int = Query(50, ge=1, le=200)) -> List[dict]:
    return fetch_recent_incidents(limit)


@app.get("/api/logs")
def logs(limit: int = Query(200, ge=10, le=2000)) -> List[dict]:
    return fetch_recent_logs(limit)
