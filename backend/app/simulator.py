import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class ScenarioState:
    tick: int = 0

    def scenario(self) -> str:
        cycle = self.tick % 480
        if 0 <= cycle < 180:
            return "normal"
        if 180 <= cycle < 260:
            return "deploy_drift"
        if 260 <= cycle < 340:
            return "normal"
        if 340 <= cycle < 420:
            return "db_saturation"
        return "normal"

    def step(self) -> None:
        self.tick += 1


def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def next_event(state: ScenarioState) -> Dict[str, Any]:
    scenario = state.scenario()
    base_latency = 120.0
    base_error = 0.2
    base_cpu = 40.0

    drift = 0.0
    error_bump = 0.0
    cpu_bump = 0.0

    if scenario == "deploy_drift":
        drift = min(120.0, (state.tick % 80) * 1.8)
        error_bump = min(1.2, (state.tick % 80) * 0.015)
        cpu_bump = 10.0
    elif scenario == "db_saturation":
        drift = 220.0 + random.uniform(0, 60)
        error_bump = 2.5 + random.uniform(0, 1.0)
        cpu_bump = 25.0

    latency_ms = base_latency + drift + random.uniform(-8, 8)
    error_rate = max(0.0, base_error + error_bump + random.uniform(-0.05, 0.05))
    cpu_pct = min(100.0, base_cpu + cpu_bump + random.uniform(-4, 4))

    level = "INFO"
    message = random.choice(
        [
            "request completed in time",
            "cache hit on product detail",
            "session validated",
            "api response sent",
        ]
    )

    if scenario == "deploy_drift" and random.random() < 0.35:
        level = "WARN"
        message = random.choice(
            [
                "migration step is slower than expected",
                "schema lock wait observed",
                "warmup cache still building",
            ]
        )
    if scenario == "db_saturation" and random.random() < 0.6:
        level = "ERROR"
        message = random.choice(
            [
                "db timeout on checkout",
                "connection pool exhausted",
                "slow query detected: orders table",
                "deadlock retry triggered",
            ]
        )

    event = {
        "metric": {
            "ts": _now_ts(),
            "latency_ms": round(latency_ms, 2),
            "error_rate": round(error_rate, 3),
            "cpu_pct": round(cpu_pct, 2),
            "scenario": scenario,
        },
        "log": {
            "ts": _now_ts(),
            "level": level,
            "message": message,
            "scenario": scenario,
        },
    }

    state.step()
    return event
