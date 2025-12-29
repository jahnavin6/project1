import time
from typing import List, Dict

import pandas as pd
import requests
import streamlit as st

API_BASE = "http://backend:8000/api"

st.set_page_config(page_title="Live Ops Anomaly Radar", layout="wide")

st.title("Live Ops Anomaly Radar")
st.write("Early-warning signals from live metrics and logs.")

with st.sidebar:
    st.header("Controls")
    limit = st.slider("Metrics window", 100, 1000, 300, step=50)
    refresh_seconds = st.slider("Refresh interval (seconds)", 1, 10, 3)
    auto_refresh = st.checkbox("Auto refresh", value=True)


def _get(path: str, params: Dict[str, int]) -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE}{path}", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"API error: {exc}")
        return []


metrics = _get("/metrics", {"limit": limit})
incidents = _get("/incidents", {"limit": 50})

if metrics:
    df = pd.DataFrame(metrics)
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts")

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest latency (ms)", f"{df['latency_ms'].iloc[-1]:.2f}")
    col2.metric("Latest error rate (%)", f"{df['error_rate'].iloc[-1]:.3f}")
    col3.metric("Latest CPU (%)", f"{df['cpu_pct'].iloc[-1]:.2f}")

    st.subheader("Live metrics")
    st.line_chart(df[["latency_ms", "error_rate", "cpu_pct"]])

    st.subheader("Scenario (latest)")
    st.write(df["scenario"].iloc[-1])

st.subheader("Incident feed")
if incidents:
    for incident in reversed(incidents):
        with st.expander(f"{incident['ts']} - {incident['scenario']}"):
            st.write(incident["summary"])
            st.write(f"Score: {incident['score']}")
            st.write(f"Top cluster: {incident['top_cluster']}")
            st.write(f"Sample log: {incident['sample_log']}")
else:
    st.write("No incidents yet.")

if auto_refresh:
    time.sleep(refresh_seconds)
    st.experimental_rerun()
