"""Repository scanning and aggregation built on PyDriller."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import datetime as dt
import os

from pydriller import Repository

from .config import Config
from .utils import exp_decay, file_skills, matches_any, month_bucket, normalize_author


@dataclass
class FileContribution:
    """A single file contribution inside a commit."""

    path: str
    skills: List[str]
    lines_added: int
    lines_deleted: int
    change_type: str


@dataclass
class CommitRecord:
    """Commit summary with per-file contributions."""

    hash: str
    author: str
    date: str
    files: List[FileContribution]
    total_lines_changed: int


def _find_git_root(start: str) -> Optional[str]:
    """Return the closest parent directory containing a .git folder."""
    p = Path(start).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return str(parent)
    return None


def scan_repo(
    repo_path: str, cfg: Config, now: Optional[dt.datetime] = None
) -> Dict[str, Any]:
    """Scan a repo and return raw commits plus aggregated skill scores and trends."""
    since = dt.datetime.fromisoformat(cfg.time_since) if cfg.time_since else None
    to = dt.datetime.fromisoformat(cfg.time_until) if cfg.time_until else None

    root = _find_git_root(repo_path)
    if root is None:
        raise RuntimeError(f"Path '{repo_path}' is not inside a Git repository.")

    commits: List[CommitRecord] = []
    for commit in Repository(path_to_repo=root, since=since, to=to).traverse_commits():
        author_str = f"{commit.author.name} <{commit.author.email}>"
        norm_author = normalize_author(author_str, cfg.author_aliases)
        if matches_any(norm_author, cfg.ignore_authors):
            continue

        file_contribs: List[FileContribution] = []
        total_changed = 0
        for m in commit.modified_files:
            path = m.new_path or m.old_path or ""
            if not path:
                continue
            skills = file_skills(
                path, cfg.extension_skills, cfg.path_skills, cfg.regex_skills
            )
            added = m.added_lines or 0
            deleted = m.deleted_lines or 0
            total_changed += added + deleted
            ct = (
                str(m.change_type.name)
                if hasattr(m.change_type, "name")
                else str(m.change_type)
            )
            file_contribs.append(FileContribution(path, skills, added, deleted, ct))

        if not file_contribs:
            continue

        commits.append(
            CommitRecord(
                commit.hash,
                norm_author,
                commit.author_date.isoformat(),
                file_contribs,
                total_changed,
            )
        )

    now = now or dt.datetime.now(dt.timezone.utc)
    half_life = cfg.decay_half_life_days

    per_author_skill: Dict[str, Dict[str, float]] = {}
    trend_monthly: Dict[str, Dict[str, Dict[str, float]]] = {}
    raw_rows: List[Dict[str, Any]] = []

    for c in commits:
        when = dt.datetime.fromisoformat(c.date)
        for f in c.files:
            base = (
                cfg.weights.get("lines_changed", 1.0)
                * (f.lines_added + f.lines_deleted)
                + cfg.weights.get("files_touched", 0.0) * 1.0
                + cfg.weights.get("commit_bonus", 0.0)
            )
            decayed = exp_decay(base, when, now, half_life)
            for skill in f.skills:
                per_author_skill.setdefault(c.author, {}).setdefault(skill, 0.0)
                per_author_skill[c.author][skill] += decayed

                month = month_bucket(when)
                trend_monthly.setdefault(month, {}).setdefault(c.author, {}).setdefault(
                    skill, 0.0
                )
                trend_monthly[month][c.author][skill] += decayed

                raw_rows.append(
                    {
                        "commit": c.hash,
                        "author": c.author,
                        "date": c.date,
                        "path": f.path,
                        "skill": skill,
                        "lines_added": f.lines_added,
                        "lines_deleted": f.lines_deleted,
                        "score": decayed,
                    }
                )

    return {
        "commits": [asdict(x) for x in commits],
        "per_author_skill": per_author_skill,
        "trend_monthly": trend_monthly,
        "raw_rows": raw_rows,
        "scanned_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo": os.path.abspath(root),
    }
