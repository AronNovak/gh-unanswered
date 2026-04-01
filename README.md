# gh-unanswered

[![PyPI](https://img.shields.io/pypi/v/gh-unanswered)](https://pypi.org/project/gh-unanswered/)

Find GitHub issues where you were @mentioned but haven't replied since.

Unlike notification-based tools, this walks comments chronologically — if you commented first, then someone mentioned you again later, it correctly flags the issue as unanswered.

## Install

```bash
pip install gh-unanswered
```

Requires [GitHub CLI](https://cli.github.com/) (`gh`) authenticated and Python 3.9+.

## Usage

```bash
gh-unanswered                             # all repos, last 14 days
gh-unanswered owner/repo                   # specific repo
gh-unanswered --days 30                    # custom time window
gh-unanswered --user someone               # check for another user
gh-unanswered --json                       # machine-readable output
```

## How it works

1. Searches for issues where you're mentioned, updated within the time window
2. Fetches all comments for each issue
3. Walks comments in chronological order:
   - Your comment clears any pending mention
   - Someone else's `@you` mention (within the time window) sets a pending mention
4. Reports issues where a mention is still pending at the end

## Example output

```
Found 2 unanswered mention(s):

  Gizra/project#48 — Fix sync queue
    Mentioned by @alice on 2026-03-25
    @you Could you take a look at this?...
    https://github.com/Gizra/project/issues/48

  other-org/repo#12 — Update deployment
    Mentioned by @bob on 2026-03-20
    @you This is ready for your review...
    https://github.com/other-org/repo/issues/12
```

## License

MIT
