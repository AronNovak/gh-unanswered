# gh-unanswered

Find GitHub issues where you were @mentioned but haven't replied since.

Unlike notification-based tools, this walks comments chronologically — if you commented first, then someone mentioned you again later, it correctly flags the issue as unanswered.

## Requirements

- Python 3.9+
- [GitHub CLI](https://cli.github.com/) (`gh`) authenticated

## Usage

```bash
python3 unanswered.py                             # all repos, last 14 days
python3 unanswered.py owner/repo                   # specific repo
python3 unanswered.py --days 30                    # custom time window
python3 unanswered.py --user someone               # check for another user
python3 unanswered.py --json                       # machine-readable output
```

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
