from collections import deque
from typing import Deque, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest

from .config import WINDOW_SIZE, WARMUP_POINTS, RETRAIN_INTERVAL, ANOMALY_THRESHOLD


class AnomalyDetector:
    def __init__(
        self,
        window_size: int = WINDOW_SIZE,
        warmup_points: int = WARMUP_POINTS,
        retrain_interval: int = RETRAIN_INTERVAL,
        threshold: float = ANOMALY_THRESHOLD,
    ) -> None:
        self.window_size = window_size
        self.warmup_points = warmup_points
        self.retrain_interval = retrain_interval
        self.threshold = threshold
        self.history: Deque[List[float]] = deque(maxlen=window_size)
        self.model: Optional[IsolationForest] = None
        self.samples_seen = 0

    def update(self, vector: List[float]) -> Tuple[Optional[float], bool]:
        self.history.append(vector)
        self.samples_seen += 1

        if len(self.history) < self.warmup_points:
            return None, False

        if self.model is None or self.samples_seen % self.retrain_interval == 0:
            self._fit_model()

        score = float(self.model.decision_function([vector])[0])
        is_anomaly = score < self.threshold
        return score, is_anomaly

    def _fit_model(self) -> None:
        data = np.array(self.history)
        self.model = IsolationForest(
            n_estimators=150,
            contamination=0.03,
            random_state=42,
        )
        self.model.fit(data)
