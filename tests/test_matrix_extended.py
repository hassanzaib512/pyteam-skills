from pyteam_skills.matrix import build_skill_matrix, _normalize_matrix, build_trends


def _fake_scan():
    return {
        "per_author_skill": {
            "Alice <alice@x>": {"Python": 10.0, "SQL": 5.0},
            "Bob <bob@x>": {"Python": 5.0},
        },
        "trend_monthly": {
            "2024-01": {
                "Alice <alice@x>": {"Python": 8.0},
                "Bob <bob@x>": {"Python": 4.0},
            },
            "2024-02": {"Alice <alice@x>": {"SQL": 5.0}},
        },
        "raw_rows": [],
    }


def test_build_skill_matrix_and_normalize():
    scan = _fake_scan()
    mat = build_skill_matrix(scan)
    assert list(mat.columns) == ["Python", "SQL"]
    assert list(mat.index) == ["Alice <alice@x>", "Bob <bob@x>"]
    norm = _normalize_matrix(mat)
    assert norm.loc["Alice <alice@x>", "Python"] == 100.0
    assert norm.loc["Bob <bob@x>", "Python"] == 50.0


def test_build_trends():
    scan = _fake_scan()
    tr = build_trends(scan)
    # normalized per (month, skill)
    top = tr[(tr["month"] == "2024-01") & (tr["skill"] == "Python")]
    assert set(top["norm"].unique()) == {100.0, 50.0}
