"""Matrix builders and exporters (no plotting here)."""

from __future__ import annotations
from typing import Any, Dict, List
import os

import pandas as pd


def _normalize_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize each skill column so the top author is 100 (rounded to 2)."""
    norm = df.copy()
    for col in norm.columns:
        m = float(norm[col].max()) if len(norm[col]) else 0.0
        if m and m > 0:
            norm[col] = (norm[col] / m) * 100.0
    return norm.round(2)


def build_skill_matrix(scan: Dict[str, Any]) -> pd.DataFrame:
    """Build author×skill matrix from aggregated scan dict."""
    data = scan["per_author_skill"]
    skills = sorted({s for a in data for s in data[a]})
    authors = sorted(data.keys())
    mat = pd.DataFrame(0.0, index=authors, columns=skills, dtype=float)
    for a, sm in data.items():
        for s, v in sm.items():
            mat.loc[a, s] = v
    return mat


def build_trends(scan: Dict[str, Any]) -> pd.DataFrame:
    """Build monthly trend rows and add per (month, skill) normalization 1–100."""
    rows: List[Dict[str, Any]] = []
    for month, by_author in scan["trend_monthly"].items():
        for author, by_skill in by_author.items():
            for skill, score in by_skill.items():
                rows.append(
                    {"month": month, "author": author, "skill": skill, "score": score}
                )
    df = pd.DataFrame(rows)
    if not df.empty:
        df["norm"] = (
            df.groupby(["month", "skill"])["score"]
            .transform(lambda s: (s / s.max()) * 100 if s.max() > 0 else 0)
            .round(2)
        )
    return df


def export_csvs(scan: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    """Export matrix, normalized matrix, trends, and raw rows as CSV files."""

    os.makedirs(out_dir, exist_ok=True)
    mat = build_skill_matrix(scan)
    norm = _normalize_matrix(mat)
    trends = build_trends(scan)

    p1 = os.path.join(out_dir, "skill_matrix.csv")
    p2 = os.path.join(out_dir, "skill_matrix_normalized.csv")
    p3 = os.path.join(out_dir, "skill_trends.csv")
    p4 = os.path.join(out_dir, "raw_contributions.csv")

    mat.to_csv(p1)
    norm.to_csv(p2)
    trends.to_csv(p3, index=False)

    pd.DataFrame(scan["raw_rows"]).to_csv(p4, index=False)
    return {
        "skill_matrix": p1,
        "skill_matrix_normalized": p2,
        "skill_trends": p3,
        "raw_contributions": p4,
    }
