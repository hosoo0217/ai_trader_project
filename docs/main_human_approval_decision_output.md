# Main Human Approval Decision Output

`main.py` can record one human approval decision for a generated strategy
approval request when `--show-session-trend` is used.

This is logging only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or change strategy rules.

## How To Record A Decision

The session trend flow creates strategy improvement suggestions, turns them into
`PENDING` Human Approval Requests, and then records a decision for one request
when `--approval-decision` is provided.

The selected request defaults to index `0`. Use `--approval-request-index` to
choose a different generated request.

## APPROVE Example

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --approval-decision APPROVE --approval-decided-by Hosoo --approval-notes "Review later before changing rules"
```

`APPROVE` means the request was approved as audit data for future
human-reviewed work. It does not apply the suggestion.

## REJECT Example

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --approval-decision REJECT --approval-decided-by Hosoo --approval-notes "Not enough data yet"
```

`REJECT` means the request should not move forward.

## NEEDS_REVIEW Example

```powershell
.\venv\Scripts\python.exe main.py --show-session-trend --approval-decision NEEDS_REVIEW --approval-decided-by Hosoo --approval-notes "Need more backtest sessions"
```

`NEEDS_REVIEW` means more research is needed before a future proposal can be
considered.

## Log Location

By default, decisions are saved to:

```text
reports/human_approval_log.json
```

Use `--approval-log-dir` to choose another output folder.

## Why Approval Does Not Change Strategy

Approval is only recorded for future human-reviewed work. The CLI prints:

- no strategy rule was changed
- no trade signal was created
- approval is only recorded for future human-reviewed work

The approval log does not edit config, change filters, modify decision logic, or
place orders.

## Why This Protects Capital

Decision logging protects capital by keeping a clear audit trail between an AI
suggestion and any future strategy work. Ideas can be approved, rejected, or
marked for more review without bypassing risk controls or changing behavior.

## Future Plan

Future versions can add an approved change proposal workflow. Approved requests
could become reviewed proposals with testing notes, risk review, and explicit
human signoff before any strategy behavior changes.
