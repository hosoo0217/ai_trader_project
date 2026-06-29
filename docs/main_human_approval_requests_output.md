# Main Human Approval Requests Output

`main.py` prints Human Approval Requests when `--show-session-trend` is used.

This output is reporting only. It does not connect to a broker, Sierra Chart,
CME, OpenAI, or any external API. It does not create real orders, generate trade
signals, or change strategy rules.

## How It Appears

When session trend output is requested, `main.py` safely runs this chain:

1. Load saved session history with `SessionHistoryStore`.
2. Analyze it with `SessionTrendAnalyzer`.
3. Create a beginner-readable review with `SessionTrendCoach`.
4. Generate safe research notes with `StrategyImprovementEngine`.
5. Convert those suggestions into `PENDING` approval requests with
   `StrategyApprovalPipeline`.

The Human Approval Requests section appears below Strategy Improvement
Suggestions.

## Why Suggestions Become PENDING Requests

Strategy suggestions are ideas for review, not instructions. Turning them into
`PENDING` approval requests makes the next step clear: a human must inspect the
category, priority, suggestion text, reason, and risk before any future change is
considered.

`PENDING` means the request is waiting for human review.

## No Strategy Change Is Applied

The main output only creates and prints approval requests. It does not approve,
reject, or apply them. It does not edit strategy rules, modify configuration, or
change decision logic.

The output may show that an approval request was created, but it also states
that no strategy rule was changed and that future changes must be reviewed first.

## Why This Protects Capital

This protects capital by keeping research, approval, and strategy behavior
separate. Suggestions can be reviewed without bypassing risk controls, session
filters, spread checks, news filters, SMC, CRT, Order Flow, or the decision
framework.

The platform stays conservative: ideas are surfaced for review before they can
become tested proposals.

## Future Plan

Future versions can add:

- approval decision logging
- approval history output
- links from main output to saved approval records
- reviewed change proposals for approved requests
- summary counts for approved, rejected, and needs-review decisions
