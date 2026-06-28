# Trading Profiles

## Why Profiles Exist
Trading profiles centralize account-level risk and execution settings so the platform can switch behavior safely between account types.

Profiles are configuration only. They do not connect to any broker, execute real trades, or use external APIs.

This project remains research-only:
- backtesting
- paper trading
- scenario validation

## Apex Futures Scalper Profile
Purpose:
- Prop-firm style futures scalping for Gold futures (GC)
- Capital protection first
- Daily target and daily loss discipline

Default characteristics:
- Account type: FUTURES_PROP
- Symbol: GC
- Starting balance: 50000
- Daily profit target: 200
- Max daily loss: 200
- Max consecutive losses: 2
- Max open positions: 1
- Risk per trade: 0.25%
- Reward-to-risk: 1.5
- Point value: 10
- Buy/Sell enabled

## Spot Gold Engine Profile
Purpose:
- XAUUSD intraday and swing-oriented research
- Controlled risk with slightly more flexibility than strict prop settings

Default characteristics:
- Account type: SPOT_GOLD
- Symbol: XAUUSD
- Starting balance: 10000
- Daily profit target: 0 (no fixed cap)
- Max daily loss: 150
- Max consecutive losses: 3
- Max open positions: 1
- Risk per trade: 0.5%
- Reward-to-risk: 2.0
- Point value: 1
- Buy/Sell enabled

## Safe Default Profile
Purpose:
- Conservative fallback when a user has not selected a profile
- Prevent accidental trading behavior in simulation

Default characteristics:
- Enabled: false
- Buy/Sell: false
- Max open positions: 0
- Risk per trade: 0.1%

## Conversion Helpers
The profile module provides helper conversions into existing system configs:
- to_capital_protection_config(profile)
- to_risk_engine_config(profile)
- to_paper_broker_config(profile)

This keeps one source of truth for account settings while reusing existing modules.

## Future Plan
Future versions can add more account presets such as:
- additional futures accounts
- low-balance spot profiles
- scenario-specific research presets

Any future profile should remain safety-first and research-only until full validation is complete.
