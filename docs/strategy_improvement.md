# Strategy Improvement Suggestions

Strategy Improvement Suggestions review saved session trend results and AI Coach
trend reviews, then produce safe research ideas for a human to inspect.

This is not live trading. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create orders, generate trade signals,
or automatically change strategy rules.

## Why This Exists

Session history can reveal patterns that are hard to see from one run. For
example, many blocked sessions may mean a filter is working correctly, or it may
mean one part of the decision framework needs better test data.

The suggestion engine turns those repeated patterns into beginner-readable
research notes.

## Human Approval Is Required

Every suggestion requires human approval before any future strategy change.
The engine can say what might be worth reviewing, but it cannot change rules by
itself.

This keeps the system safe:

- Suggestions are educational notes.
- Suggestions are not trade signals.
- Suggestions are not automatic configuration changes.
- A human must decide what to test next.

## How Blocked Reasons Help

Blocked sessions are useful because they show where the system protected the
paper/demo/backtest account. Repeated blocked reasons can also show where more
research is needed.

Examples:

- `SESSION` blockers may suggest reviewing session filter settings and weekday
  samples.
- `SMC` blockers may suggest checking sample data or swing detection quality.
- `ORDER_FLOW` blockers may suggest checking footprint CSV quality and order
  flow alignment.
- `SPREAD` blockers may suggest reviewing spread thresholds.
- `NEWS` blockers may suggest reviewing news filter timing.
- High execution rate may suggest reviewing performance, drawdown, and risk
  metrics before trusting the pass rate.

## Output

The engine returns:

- status
- suggestions
- summary
- warnings
- reasons

Each suggestion includes:

- category
- priority
- suggestion text
- reason
- risk
- human approval requirement

## Future Plan

Later versions can turn these research notes into human-approved strategy change
proposals. Those proposals should still be reviewed, tested, and approved before
they affect any paper/backtest decision logic.
