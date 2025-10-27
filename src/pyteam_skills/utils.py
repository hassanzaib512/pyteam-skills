"""Utility helpers for author normalization, matching, decay, and skill detection."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional
import datetime as dt
import re


def normalize_author(author: str, aliases: Dict[str, str]) -> str:
    """Return normalized author using exact-match aliases (case-insensitive)."""
    if not author:
        return "Unknown"
    for old, new in (aliases or {}).items():
        if author.lower() == old.lower():
            return new
    return author


def matches_any(s: str, substrings: Iterable[str]) -> bool:
    """True if *any* substring occurs (case-insensitive) inside *s*."""
    if not s:
        return False
    return any((sub or "").lower() in s.lower() for sub in (substrings or []))


def exp_decay(
    weight: float, when: dt.datetime, now: Optional[dt.datetime], half_life_days: float
) -> float:
    """Apply exponential decay with a given half-life (in days)."""
    when_utc = (
        when.astimezone(timezone.utc)
        if when.tzinfo
        else when.replace(tzinfo=timezone.utc)
    )
    if now is None:
        now = datetime.now(timezone.utc)
    now_utc = (
        now.astimezone(timezone.utc) if now.tzinfo else now.replace(tzinfo=timezone.utc)
    )
    days = (now_utc - when_utc).total_seconds() / 86400.0
    if not half_life_days or half_life_days <= 0:
        return weight
    return weight * (0.5 ** (days / float(half_life_days)))


def file_skills(
    path: str,
    ext_map: Dict[str, List[str]],
    path_map: Dict[str, List[str]],
    regex_map: Dict[str, List[str]],
) -> List[str]:
    """Determine skills for a file path with precedence."""
    # 1) regex overrides (first match wins)
    for pattern, skills in (regex_map or {}).items():
        if re.match(pattern, path):
            return skills

    # 2) path prefix overrides (longest prefix wins)
    matched: Optional[List[str]] = None
    best_len = -1
    for prefix, skills in (path_map or {}).items():
        if path.startswith(prefix) and len(prefix) > best_len:
            matched = skills
            best_len = len(prefix)
    if matched:
        return matched

    # 3) extension mapping
    for ext, skills in (ext_map or {}).items():
        if path.endswith(ext):
            return skills

    # 4) fallback
    return ["Other"]


def month_bucket(d: dt.datetime) -> str:
    """Return YYYY-MM string for a datetime."""
    return d.strftime("%Y-%m")
