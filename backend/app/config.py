import os

APP_NAME = "live-ops-anomaly-radar"

SAMPLE_INTERVAL_SEC = float(os.getenv("SAMPLE_INTERVAL_SEC", "1"))
WARMUP_POINTS = int(os.getenv("WARMUP_POINTS", "120"))
RETRAIN_INTERVAL = int(os.getenv("RETRAIN_INTERVAL", "200"))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "400"))
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "-0.12"))

DB_PATH = os.getenv("DB_PATH", "data/ops_radar.db")
RECENT_LOG_LIMIT = int(os.getenv("RECENT_LOG_LIMIT", "200"))
INCIDENT_COOLDOWN_SEC = int(os.getenv("INCIDENT_COOLDOWN_SEC", "30"))
