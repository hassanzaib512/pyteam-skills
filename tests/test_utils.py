import datetime as dt
from datetime import timezone
from pyteam_skills.utils import (
    normalize_author,
    matches_any,
    exp_decay,
    file_skills,
    month_bucket,
)


def test_normalize_author_alias():
    assert normalize_author("Foo <bar@x>", {"foo <bar@x>": "Foo Bar"}) == "Foo Bar"


def test_matches_any():
    assert matches_any("alice@example.com", ["alice@", "bot@"])
    assert not matches_any("bob@example.com", ["alice@", "bot@"])


def test_exp_decay_tzsafe():
    when = dt.datetime(2024, 1, 1, tzinfo=timezone.utc)
    now = dt.datetime(2024, 1, 31, tzinfo=timezone.utc)
    out = exp_decay(100.0, when, now, half_life_days=30.0)
    assert out < 100.0 and out > 0.0


def test_file_skills_precedence():
    path = "frontend/src/app.tsx"
    ext_map = {".tsx": ["React", "TypeScript"], ".ts": ["TypeScript"]}
    path_map = {"frontend/": ["React", "JavaScript"]}
    regex_map = {r"^frontend/src/.*\.tsx$": ["React"], r".*\.ts$": ["TypeScript"]}
    # regex first match wins
    assert file_skills(path, ext_map, path_map, regex_map) == ["React"]
    # path prefix wins when no regex
    assert file_skills(
        "frontend/foo.py", {".py": ["Python"]}, {"frontend/": ["React"]}, {}
    ) == ["React"]
    # extension fallback
    assert file_skills("foo.py", {".py": ["Python"]}, {}, {}) == ["Python"]
    # Other fallback
    assert file_skills("unknown.zzz", {}, {}, {}) == ["Other"]


def test_month_bucket():
    d = dt.datetime(2023, 7, 15, tzinfo=timezone.utc)
    assert month_bucket(d) == "2023-07"
