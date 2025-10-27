"""Config dataclass and YAML I/O.

Auto-generated housekeeping docstrings; no logic changed."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml


@dataclass
class Config:
    ignore_authors: List[str] = field(default_factory=list)
    extension_skills: Dict[str, List[str]] = field(default_factory=dict)
    path_skills: Dict[str, List[str]] = field(default_factory=dict)
    regex_skills: Dict[str, List[str]] = field(default_factory=dict)
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "lines_changed": 1.0,
            "files_touched": 0.3,
            "commit_bonus": 0.2,
        }
    )
    decay_half_life_days: float = 120.0
    time_since: Optional[str] = None
    time_until: Optional[str] = None
    author_aliases: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.__dict__, f, sort_keys=False)
