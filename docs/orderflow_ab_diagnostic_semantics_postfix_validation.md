# Order Flow A/B Diagnostic Semantics Post-Fix Validation

This document records post-fix validation results for research-only Order Flow A/B diagnostic semantics.

It is documentation only. It does not change strategy execution, risk rules, broker behavior, live trading behavior, or external API behavior.

## 1. Post-Fix Baseline

- Post-fix commit: `c731b48 fix: display inferred orderflow ab trade side`
- Test baseline after fix: `841 passed`

## 2. Validation Results

### 2.1 5m bearish

- Scenario: bearish / `SELL`
- Order Flow: `BULLISH`
- Confidence: `70`
- A PnL: `-50`
- B executed: `0`
- B blocked by OF confirmation: `5`
- Opposite-bias blocks: `5`
- B PnL: `0`
- Report label: `SELL blocked`

Interpretation:

- Opposite-bias blocking is now correctly counted for bearish/SELL semantics.

### 2.2 5m bullish

- Scenario: bullish / `BUY`
- Order Flow: `BULLISH`
- Confidence: `70`
- A PnL: `-50`
- B executed: `5`
- Opposite-bias blocks: `0`
- B PnL: `-50`

Meaning:

- Aligned Order Flow alone did not prove profitability.

### 2.3 10m bullish

- Scenario: bullish / `BUY`
- Order Flow: `NEUTRAL`
- Confidence: `30`
- A PnL: `-20`
- B executed: `0`
- Neutral blocks: `2`
- B PnL: `0`

### 2.4 10m bearish

- Scenario: bearish / `SELL`
- Order Flow: `NEUTRAL`
- Confidence: `30`
- A PnL: `-20`
- B executed: `0`
- Neutral blocks: `2`
- B PnL: `0`
- Report label: `SELL blocked`

## 3. Conclusion

- A/B diagnostic now correctly models neutral blocking.
- A/B diagnostic now correctly models opposite-bias blocking.
- Trade-side display labels are correct.
- This is still research-only diagnostic behavior.
- Strategy execution was not changed.
- This does not prove profitability.
- The next implementation step should remain test-first and approval-gated.
