#!/usr/bin/env python3
"""Find GitHub issues where you were @mentioned but haven't replied since."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta


def gh_api(endpoint, search=False, retries=3):
    args = ["gh", "api", "--paginate", endpoint]
    if search:
        args = ["gh", "api", endpoint]
    for attempt in range(retries):
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode == 0:
            break
        if attempt < retries - 1 and ("503" in result.stderr or "secondary rate limit" in result.stderr):
            time.sleep(2 ** attempt)
            continue
        print(f"Error calling gh api {endpoint}: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    raw = result.stdout.strip()
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, list):
        return data
    return [data]


def get_username():
    result = subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def find_unanswered(repo, username, since, include_closed=False):
    since_str = since.strftime("%Y-%m-%d")
    mention_tag = f"@{username}"

    repo_qualifier = f"repo:{repo}" if repo else ""
    state_qualifier = "" if include_closed else "+state:open"
    issues = gh_api(
        f"search/issues?q={repo_qualifier}+type:issue+mentions:{username}"
        f"+updated:>={since_str}{state_qualifier}&per_page=100".replace("q=+", "q="),
        search=True,
    )

    results = []

    for issue in issues:
        number = issue["number"]
        title = issue["title"]
        issue_repo = issue["repository_url"].removeprefix("https://api.github.com/repos/")
        comments = gh_api(f"repos/{issue_repo}/issues/{number}/comments?per_page=100")

        # Walk comments chronologically and track mention/reply state.
        # We only care about mentions that happened within our time window.
        pending_mention = None

        for comment in comments:
            created = parse_dt(comment["created_at"])
            author = comment["user"]["login"]
            body = comment.get("body", "")

            if author.lower() == username.lower():
                # User commented — clears any pending mention.
                pending_mention = None
            elif mention_tag.lower() in body.lower() and created >= since:
                # Someone else mentioned the user within our window.
                pending_mention = {
                    "by": author,
                    "at": created,
                    "snippet": body[:150].replace("\n", " "),
                    "comment_url": comment.get("html_url", ""),
                }

        if pending_mention:
            results.append({
                "issue": number,
                "title": title,
                "mentioned_by": pending_mention["by"],
                "mentioned_at": pending_mention["at"],
                "snippet": pending_mention["snippet"],
                "repo": issue_repo,
                "comment_url": pending_mention["comment_url"],
            })

    # Sort by mention date, most recent first.
    results.sort(key=lambda r: r["mentioned_at"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Find issues where you were @mentioned but haven't replied since."
    )
    parser.add_argument("repo", nargs="?", default=None, help="GitHub repo (owner/repo). Omit to search all your repos.")
    parser.add_argument("--user", default=None, help="GitHub username (default: authenticated user)")
    parser.add_argument("--days", type=int, default=14, help="Look back N days (default: 14)")
    parser.add_argument("--include-closed", action="store_true", help="Include closed issues (excluded by default)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    username = args.user or get_username()
    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    results = find_unanswered(args.repo, username, since, args.include_closed)

    if args.json:
        print(json.dumps(results, default=str, indent=2))
        return

    if not results:
        print("No unanswered mentions found.")
        return

    print(f"Found {len(results)} unanswered mention(s):\n")
    for r in results:
        date_str = r["mentioned_at"].strftime("%Y-%m-%d")
        repo_prefix = f"{r['repo']}" if "repo" in r else ""
        print(f"  {repo_prefix}#{r['issue']} — {r['title']}")
        print(f"    Mentioned by @{r['mentioned_by']} on {date_str}")
        print(f"    {r['snippet']}...")
        print(f"    {r['comment_url']}")
        print()


if __name__ == "__main__":
    main()
