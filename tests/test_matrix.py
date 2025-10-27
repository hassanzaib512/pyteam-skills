"""Normalization smoke test."""

import pandas as pd
from pyteam_skills.matrix import _normalize_matrix


def test_normalize_matrix_1_to_100():
    df = pd.DataFrame({"Python": [10, 5, 0], "SQL": [0, 0, 0]}, index=["A", "B", "C"])
    norm = _normalize_matrix(df)
    assert norm.loc["A", "Python"] == 100.0
    assert norm.loc["B", "Python"] == 50.0
    assert norm.loc["C", "Python"] == 0.0
    assert norm["SQL"].sum() == 0.0
