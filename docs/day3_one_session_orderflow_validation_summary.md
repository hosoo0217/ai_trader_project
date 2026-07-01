# Day3 One-Session Order Flow Validation Summary

This document consolidates Day3 one-session ACSIL validation results after the Order Flow A/B diagnostic fixes.

It is documentation only. It does not change `main.py`, strategy code, risk rules, broker behavior, live trading behavior, or external API behavior.

## 1. Current Checkpoints

- `day3-1day-10m-acsil-validation-checkpoint`
- `day3-1day-5m-acsil-logic-gap-checkpoint`
- `orderflow-ab-diagnostic-semantics-update-checkpoint`
- `orderflow-ab-opposite-bias-fix-checkpoint`
- `orderflow-ab-trade-side-label-fix-checkpoint`
- `orderflow-ab-postfix-validation-checkpoint`
- `day3-1day-1m-acsil-validation-checkpoint`

## 2. Validation Coverage

- 10m bullish/bearish
- 5m bullish/bearish
- 1m bullish/bearish

## 3. Key Findings

- Data quality passed on 1m, 5m, and 10m.
- 10m NEUTRAL / low-confidence Order Flow losing trades were blocked by simulated B.
- 1m NEUTRAL / low-confidence Order Flow losing trades were blocked by simulated B.
- 5m bearish with BULLISH Order Flow was correctly blocked as opposite-bias after the diagnostic fix.
- 5m bullish with BULLISH Order Flow was allowed and still lost.
- Therefore, Order Flow confirmation may improve safety filtering, but does not prove profitability.
- Current implementation remains research-only diagnostic.
- Strategy execution was not changed.

## 4. Conclusion

- A/B diagnostic is now reliable enough for further validation.
- Actual strategy enforcement is still **NOT READY**.
- More independent sessions are required before any enforcement implementation.
- Recommended next step: run Day4 / independent new-session validation using the fixed diagnostic across 1m, 5m, and 10m.
