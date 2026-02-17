#!/usr/bin/env python3
"""
Doc Freshness Checker -- finds stale docs and dead links.

Continuous garbage collection for documentation:
  1. Checks every .md file in docs/ for staleness (90+ days since git modify)
  2. Finds dead internal links (references to files that don't exist)
  3. Reports results as warnings (not blocking)

Usage: python scripts/doc_freshness.py
       make doctor (includes this check)

Based on continuous garbage collection best practices from Anthropic research.
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

STALE_THRESHOLD_DAYS = 90
DOCS_DIR = Path("docs")
PROJECT_ROOT = Path(__file__).parent.parent


def get_git_last_modified(filepath: Path) -> datetime | None:
    """Get the last git commit date for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        if result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip())
    except Exception:
        pass
    return None


def find_internal_links(filepath: Path) -> list[str]:
    """Extract internal markdown links from a file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    links = re.findall(r'\[.*?\]\(([^)]+)\)', content)
    internal = []
    for link in links:
        if link.startswith("http://") or link.startswith("https://"):
            continue
        if link.startswith("#"):
            continue
        internal.append(link.split("#")[0])
    return internal


def check_staleness(docs_path: Path) -> list[dict]:
    """Find docs that haven't been updated in STALE_THRESHOLD_DAYS."""
    stale = []
    cutoff = datetime.now(tz=None) - timedelta(days=STALE_THRESHOLD_DAYS)

    for md_file in sorted(docs_path.glob("*.md")):
        last_modified = get_git_last_modified(md_file)
        if last_modified is None:
            continue
        naive_modified = last_modified.replace(tzinfo=None)
        if naive_modified < cutoff:
            days_old = (datetime.now() - naive_modified).days
            stale.append({
                "file": str(md_file.relative_to(PROJECT_ROOT)),
                "last_modified": last_modified.strftime("%Y-%m-%d"),
                "days_old": days_old,
            })
    return stale


def check_dead_links(docs_path: Path) -> list[dict]:
    """Find internal links that point to non-existent files."""
    dead = []
    for md_file in sorted(docs_path.glob("*.md")):
        links = find_internal_links(md_file)
        for link in links:
            target = (md_file.parent / link).resolve()
            if not target.exists():
                alt_target = (PROJECT_ROOT / link).resolve()
                if not alt_target.exists():
                    dead.append({
                        "source": str(md_file.relative_to(PROJECT_ROOT)),
                        "broken_link": link,
                    })
    return dead


def main():
    print("\nDoc Freshness Check\n")

    docs_path = PROJECT_ROOT / DOCS_DIR
    if not docs_path.is_dir():
        print(f"  {YELLOW}SKIP{RESET}  No docs/ directory found")
        return

    stale = check_staleness(docs_path)
    dead = check_dead_links(docs_path)

    if stale:
        print(f"  {YELLOW}STALE{RESET}  {len(stale)} doc(s) not updated in {STALE_THRESHOLD_DAYS}+ days:")
        for s in stale:
            print(f"         {s['file']} (last modified: {s['last_modified']}, {s['days_old']} days ago)")
    else:
        print(f"  {GREEN}FRESH{RESET}  All docs updated within {STALE_THRESHOLD_DAYS} days")

    if dead:
        print(f"  {RED}DEAD{RESET}   {len(dead)} broken internal link(s):")
        for d in dead:
            print(f"         {d['source']} -> {d['broken_link']}")
    else:
        print(f"  {GREEN}LINKS{RESET}  All internal links valid")

    total_issues = len(stale) + len(dead)
    print(f"\n  {'=' * 40}")
    if total_issues == 0:
        print(f"  {GREEN}All docs fresh and linked correctly{RESET}")
    else:
        print(f"  {YELLOW}{total_issues} issue(s) found{RESET}")
    print(f"  {'=' * 40}\n")


if __name__ == "__main__":
    main()
