import os

from pyteam_skills.dashboard import generate_dashboard


def test_generate_dashboard_writes_files(tmp_path):
    scan = {
        "per_author_skill": {"A <a@x>": {"Python": 1.0}},
        "trend_monthly": {"2024-01": {"A <a@x>": {"Python": 1.0}}},
        "raw_rows": [],
        "repo": "/tmp/repo",
        "scanned_at": "2024-01-01T00:00:00Z",
    }
    out = tmp_path / "dash"
    paths = generate_dashboard(scan, str(out))
    assert os.path.exists(paths["index_html"])
    assert os.path.exists(paths["data_json"])
    # index should include embedded JSON script
    with open(paths["index_html"], "r", encoding="utf-8") as f:
        page = f.read()
    assert '<script id="data-script" type="application/json">' in page
