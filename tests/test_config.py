from pyteam_skills.config import Config


def test_config_roundtrip(tmp_path):
    cfg = Config(ignore_authors=["bot@"], extension_skills={".py": ["Python"]})
    p = tmp_path / "cfg.yml"
    cfg.save(p)
    loaded = Config.from_file(p)
    assert loaded.ignore_authors == ["bot@"]
    assert loaded.extension_skills[".py"] == ["Python"]
