# Live Ops Anomaly Radar

![License](https://img.shields.io/badge/license-MIT-green)

An early-warning system that watches live service metrics and logs, detects unusual behavior before threshold alerts fire, and generates a simple incident summary for faster triage.

## What is this (super simple)
Think of a website that should stay fast. If it starts getting slow or error-prone, you want to know early. This project watches the live data and warns you before the problem becomes big.

## Paint the picture (real-world context)
You are on-call. Everything looks fine, then latency slowly creeps up after a deployment. Threshold alerts have not fired yet, but customers are starting to notice. You need a signal early, plus a clue about the cause.  
This project sits on top of your metrics and logs and acts like a real-time radar: it learns normal behavior, spots drift early, and surfaces a likely root-cause hint from log patterns.

## The problem (plain language)
Normal monitoring uses fixed rules like:
- "Alert me if error rate is above 5%"
- "Alert me if latency is above 500ms"

But real problems start before those numbers are crossed, so the alert comes late and logs are noisy.

## What this project does (simple)
- Collects live metrics (latency, error rate, CPU)
- Collects live logs (text messages from services)
- Learns what "normal" looks like
- Detects unusual behavior early
- Shows a short incident summary on a dashboard

## Example workflow (real-time story)
1) 10:02 PM - Latency ~120ms, errors ~0.2% (normal).  
2) 10:05 PM - New deployment; latency drifts to 180ms, errors to 0.6%.  
3) 10:07 PM - Detector flags early anomaly (no threshold alert yet).  
4) 10:08 PM - Log clustering highlights "DB timeout" spike.  
5) 10:09 PM - Incident card says: "Likely DB saturation after deploy."  
6) 10:10 PM - On-call scales DB or rolls back before outage.

## End-to-end scope (what this repo includes)
**Data & persistence**
- Live data simulator (fake but realistic traffic)
- Ingestion pipeline for metrics and logs
- Store raw events and incidents in SQLite so history survives restarts

**Detection**
- Metrics anomaly detection (Isolation Forest)
- Log clustering (TF-IDF + KMeans) to surface dominant error patterns

**Alerting**
- In-app alert feed and console logs
- Slack webhook alerts are planned (not in v1)

**UI**
- Live dashboard: metrics charts, anomaly timeline, incident cards
- Each incident card includes time, score, and top log cluster

**Infra**
- Docker Compose for one-command setup

## Version 1 (realistic MVP)
This repo is built in stages. Version 1 is intentionally small but real.
- Single service pipeline (one simulator, one detector, one dashboard)
- Two demo scenarios: deployment drift and DB saturation
- SQLite persistence for incidents
- In-app alerts (Slack planned)
- One-command local run with Docker Compose

## Future versions (natural extensions)
- Multiple services + multiple detectors
- Model retraining and drift detection
- Incident severity scoring and SLA impact
- Slack + email + webhook alerting
- Real log sources (e.g., file tailing, OpenTelemetry)
- Role-based views and audit trail

## How it works (flow)
```
Metrics + Logs
      |
   Stream
      |
ML Detector -----> Incident Summarizer
      |                    |
      +----> Alerts + Dashboard
```

## Architecture diagram (simple ASCII)
```
  [Data Simulator]
          |
          v
  +-----------------+
  | Ingestion Layer |
  | (metrics, logs) |
  +-----------------+
          |
          v
  +-----------------+        +--------------------+
  | ML Detector     | -----> | Incident Summarizer|
  | (anomaly score) |        | (log clustering)   |
  +-----------------+        +--------------------+
          |                           |
          v                           v
  +-----------------+        +--------------------+
  | Alerts + API    | -----> | Live Dashboard     |
  | (FastAPI)       |        | (Streamlit)        |
  +-----------------+        +--------------------+
          |
          v
      [SQLite DB]
```

## Repo layout (what each folder does)
- `backend/` - FastAPI service with simulator, detector, storage, API
- `dashboard/` - Streamlit UI that shows live charts and incidents
- `data/` - SQLite database lives here
- `docker-compose.yml` - run everything with one command

## Tech stack (open source)
- Python (FastAPI, scikit-learn)
- UI: Streamlit (live dashboard)
- Storage: SQLite
- Containers: Docker + Compose

## Why it stands out
- Early warning, not just threshold alerts
- Adds context by summarizing log clusters
- Real-time pipeline shows ML + infra maturity

## Status
This repo is a work-in-progress MVP. The goal is to build the full pipeline end-to-end.

## Quickstart
### Supported OS (v1)
- Linux only (tested on Ubuntu). macOS/Windows are not tested in v1.

### Prerequisites
- Docker Engine + Docker Compose
- Python 3.11 (only needed if running without Docker)
- 2 GB RAM free, 1 GB disk free

### Setup (Docker, recommended)
Run the full stack:
```
docker compose up --build
```
Then open:
- Dashboard: http://localhost:8501
- API health: http://localhost:8000/api/health

## Run without Docker (optional)
### Setup (Linux only)
Backend:
```
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Dashboard (new terminal):
```
source .venv/bin/activate
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

### Stopping services
- Docker: press `Ctrl+C` or run `docker compose down`
- Local: press `Ctrl+C` in each terminal

## Demo walkthrough (what you will see)
1) Start the stack and open the dashboard.
2) Watch the metrics chart stabilize at normal levels.
3) A deployment drift scenario begins: latency and error rate rise slowly.
4) The incident feed shows an early anomaly card.
5) A DB saturation scenario begins: error logs spike and a new incident appears.

## Troubleshooting
- Dashboard shows API error: wait 5-10 seconds for the backend to start, then refresh.
- No incidents yet: wait 2-3 minutes; the detector needs warmup data.
- Port conflict: change ports in `docker-compose.yml` if 8000 or 8501 are in use.

## Contributing
Issues and PRs are welcome. If you want to add new scenarios or detectors, open an issue first so we can align on scope.

## FAQ
Q: Why Linux-only in v1?  
A: It keeps the environment consistent for a first release. macOS/Windows support can be added in v2.

Q: Why do incidents take time to appear?  
A: The detector needs warmup data to learn normal behavior.

Q: Is this using real production logs?  
A: v1 uses a simulator to keep the demo self-contained and safe.

## Where data is saved
- SQLite DB lives in `data/ops_radar.db`
- Incidents and metrics are persisted between restarts

## API endpoints (v1)
- `GET /api/metrics?limit=300`
- `GET /api/incidents?limit=50`
- `GET /api/logs?limit=200`
- `GET /api/health`

## Roadmap (next)
- Add Slack webhook alerts
- Add multi-service support and severity scoring
- Add Prometheus + Grafana integration
- Add replay controls and scenario selection
