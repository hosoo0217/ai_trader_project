# News Filter

## Why News Filter Exists
The news filter is a safety layer for paper trading and backtesting.

Its goal is to block entries around high-impact news periods where price can move aggressively and unpredictably.

For v1, it uses manual event windows only:
- no live trading
- no real broker
- no external API
- no economic calendar API

## High-Impact News Examples
Typical high-impact events include:
- Non-Farm Payrolls (NFP)
- CPI inflation release
- FOMC rate decision and statement
- Central bank press conference

These events can create fast spikes, spread expansion, and slippage-like behavior in simulation assumptions.

## Why Apex Futures Scalping Should Avoid News Spikes
Apex-style futures scalping is sensitive to sudden volatility changes.

When news hits, micro-structure can shift quickly and invalidate normal entry logic.

Blocking around high-impact windows helps preserve discipline and keeps paper results more realistic.

## Why Spot Gold Should Also Be Careful Around News
Spot Gold can react strongly to macroeconomic releases and central-bank communication.

Even swing or intraday research can be distorted if entries happen in chaotic event windows.

The filter helps avoid false confidence from trades taken during unstable conditions.

## v1 Behavior Summary
- Invalid or missing current time blocks trading.
- Disabled filter allows trading with reason: News filter disabled.
- HIGH impact events block by default inside their manual time windows.
- MEDIUM and LOW impact events block only when enabled in config.
- Disabled events are ignored.
- If no active blocking event is present, trading is allowed.

## Future Plan
Future versions can integrate an economic calendar API after full validation.

Planned improvements:
- automatic event ingestion
- symbol-specific event relevance
- profile-specific news blocking rules
- richer event categorization and severity handling
