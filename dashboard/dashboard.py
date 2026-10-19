#!/usr/bin/env python3
"""Generate the repository's robotics engineering dashboard README."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "dashboard" / "config.json"
TEMPLATE_PATH = ROOT / "dashboard" / "README_TEMPLATE.md"
BAR_WIDTH = 20


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def progress_bar(percent: int) -> str:
    completed = round(BAR_WIDTH * percent / 100)
    return f"`{percent:3d}%` `{'█' * completed}{'░' * (BAR_WIDTH - completed)}`"


def markdown_table_rows(rows: list[list[str]]) -> str:
    return "\n".join(f"| {left} | {right} |" for left, right in rows)


def fetch_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MazeBot-Engineering-Dashboard",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=12) as response:
        return json.load(response)


def local_repository_stats() -> dict[str, Any]:
    tracked_files = [name for name in git_output("ls-files").splitlines() if name]
    contributors = [
        line for line in git_output("shortlog", "-sne", "HEAD").splitlines() if line
    ]
    return {
        "tracked_files": len(tracked_files),
        "commits": int(git_output("rev-list", "--count", "HEAD")),
        "contributors": len(contributors),
    }


def local_recent_commits(limit: int = 5) -> list[dict[str, str]]:
    output = git_output(
        "log",
        f"-{limit}",
        "--date=short",
        "--pretty=format:%h%x1f%ad%x1f%s",
    )
    commits = []
    for line in output.splitlines():
        parts = line.split("\x1f", 2)
        if len(parts) == 3:
            commits.append(
                {"sha": parts[0], "date": parts[1], "message": parts[2], "url": ""}
            )
    return commits


def github_data(
    repository: str, token: str | None, errors: list[str]
) -> tuple[dict[str, Any] | None, list[dict[str, str]] | None]:
    base_url = f"https://api.github.com/repos/{repository}"
    metadata = None
    commits = None
    for label, url in (
        ("repository metadata", base_url),
        ("recent commits", f"{base_url}/commits?per_page=5"),
    ):
        try:
            response = fetch_json(url, token)
            if label == "repository metadata":
                metadata = response
            else:
                commits = [
                    {
                        "sha": item["sha"][:7],
                        "date": item["commit"]["author"]["date"][:10],
                        "message": item["commit"]["message"].splitlines()[0],
                        "url": item["html_url"],
                    }
                    for item in response
                ]
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            errors.append(f"GitHub {label} unavailable ({exc}).")
    return metadata, commits


def render(config: dict[str, Any], offline: bool = False) -> tuple[str, list[str]]:
    errors: list[str] = []
    local_stats = local_repository_stats()
    recent = local_recent_commits()
    metadata = None

    if not offline:
        metadata, github_commits = github_data(
            config["repository"], os.environ.get("GITHUB_TOKEN"), errors
        )
        if github_commits is not None:
            recent = github_commits

    if metadata:
        stats = [
            ("Stars", str(metadata["stargazers_count"])),
            ("Forks", str(metadata["forks_count"])),
            ("Open issues", str(metadata["open_issues_count"])),
            ("GitHub repository size", f'{metadata["size"]:,} KB'),
            ("Tracked files", f'{local_stats["tracked_files"]:,}'),
            ("Git commits", f'{local_stats["commits"]:,}'),
            ("Contributors in local history", f'{local_stats["contributors"]:,}'),
        ]
    else:
        stats = [
            ("Stars / forks / open issues", "Unavailable offline"),
            ("Tracked files", f'{local_stats["tracked_files"]:,}'),
            ("Git commits", f'{local_stats["commits"]:,}'),
            ("Contributors in local history", f'{local_stats["contributors"]:,}'),
        ]

    milestones = config["milestones"]
    overall = round(sum(item["progress"] for item in milestones) / len(milestones))
    milestone_rows = "\n".join(
        f'| {item["name"]} | {item["status"]} | {progress_bar(item["progress"])} | {item["evidence"]} |'
        for item in milestones
    )
    commit_rows = []
    for commit in recent:
        message = commit["message"].replace("|", "\\|")
        label = f'`{commit["sha"]}` {message}'
        if commit["url"]:
            label = f'[{label}]({commit["url"]})'
        commit_rows.append(f'| {commit["date"]} | {label} |')

    image = config["image"]
    video = config["video"]
    media = (
        f'![Maze course](<{image}>)\n\n'
        f'[View the MazeBot run video](<{video}>)'
    )
    values = {
        "project_name": config["project_name"],
        "subtitle": config["subtitle"],
        "updated_at": datetime.now(timezone.utc).date().isoformat() + " UTC",
        "specifications": markdown_table_rows(config["specifications"]),
        "pinout": markdown_table_rows(config["pinout"]),
        "overall_progress": (
            f'**Estimated engineering milestone completion: {overall}%**  \n'
            f'{progress_bar(overall)}  \n'
            f'Average of {len(milestones)} configured milestone estimates.'
        ),
        "milestones": milestone_rows,
        "tuning": "\n".join(
            f"| {name} | {value} | {purpose} |" for name, value, purpose in config["tuning"]
        ),
        "future_improvements": "\n".join(f"- {item}" for item in config["future_improvements"]),
        "statistics": "\n".join(f"| {name} | {value} |" for name, value in stats),
        "recent_commits": (
            "| Date | Commit |\n|---|---|\n" + "\n".join(commit_rows)
            if commit_rows
            else "No commits were available in the local history."
        ),
        "media": media,
        "contributors": "\n".join(f"- {item}" for item in config["contributors"]),
        "advisor": config["advisor"],
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    remaining_tokens = [
        token for token in ("{{", "}}") if token in template
    ]
    if remaining_tokens:
        raise ValueError(f"Unresolved template token(s): {', '.join(remaining_tokens)}")
    return template.rstrip() + "\n", errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use local Git history only; do not call the GitHub API.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "README.md",
        help="Output Markdown file (default: repository README.md).",
    )
    args = parser.parse_args()

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        markdown, errors = render(config, offline=args.offline)
        args.output.write_text(markdown, encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Dashboard generation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {args.output}")
    for error in errors:
        print(f"Warning: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
