from collections import Counter
from typing import Dict, List

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def summarize_logs(logs: List[Dict[str, str]]) -> Dict[str, str]:
    if len(logs) < 5:
        return {
            "top_cluster": "not enough logs for clustering",
            "sample_log": "insufficient log volume for clustering",
        }

    texts = [log["message"] for log in logs]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(texts)

    n_clusters = min(3, len(texts))
    if n_clusters <= 1:
        return {
            "top_cluster": "log patterns are uniform",
            "sample_log": texts[0],
        }

    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = model.fit_predict(tfidf)

    counts = Counter(labels)
    top_label = counts.most_common(1)[0][0]
    top_indices = [i for i, label in enumerate(labels) if label == top_label]

    centroid = model.cluster_centers_[top_label]
    terms = vectorizer.get_feature_names_out()
    top_terms = [terms[i] for i in centroid.argsort()[-4:][::-1]]

    sample_log = texts[top_indices[0]]
    return {
        "top_cluster": ", ".join(top_terms),
        "sample_log": sample_log,
    }
