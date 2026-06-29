# Main Change Proposal Review Output

`main.py` can review saved change proposals from `change_proposals.json` and
record the review decision.

This is review logging only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically implement strategy changes.

## How To Review A Saved Proposal

Use `--review-change-proposal` to load saved proposals, select one by index, and
record a review decision.

The selected proposal defaults to index `0`. Use `--change-proposal-index` to
choose another saved proposal.

## ACCEPT Example

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal ACCEPT --change-proposal-index 0 --proposal-reviewed-by Hosoo --proposal-review-notes "Accepted for future work only, still needs implementation plan"
```

`ACCEPT` means the proposal is accepted for future human-reviewed work only. It
does not implement the proposal.

## REJECT Example

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal REJECT --change-proposal-index 0 --proposal-reviewed-by Hosoo --proposal-review-notes "Rejected because data is not enough"
```

`REJECT` means the proposal should not move forward.

## NEEDS_MORE_DATA Example

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal NEEDS_MORE_DATA --change-proposal-index 0 --proposal-reviewed-by Hosoo --proposal-review-notes "Need more saved sessions before review"
```

`NEEDS_MORE_DATA` means more evidence is needed before the proposal can move
forward.

## NEEDS_BACKTEST Example

```powershell
.\venv\Scripts\python.exe main.py --review-change-proposal NEEDS_BACKTEST --change-proposal-index 0 --proposal-reviewed-by Hosoo --proposal-review-notes "Needs more backtesting before implementation"
```

`NEEDS_BACKTEST` means backtesting is required before implementation planning is
considered.

## File Locations

By default, saved proposals are loaded from:

```text
reports/change_proposals.json
```

Review decisions are saved to:

```text
reports/change_proposal_reviews.json
```

Use `--proposal-dir` and `--proposal-review-log-dir` to choose other folders.

## Why ACCEPT Does Not Implement Strategy Changes

`ACCEPT` records that the proposal may move into future human-reviewed work. It
does not edit config, modify filters, update decision logic, place orders, or
generate trade signals.

The output clearly says:

- no strategy rule was changed
- no trade signal was created
- review decision is recorded for future human-reviewed work only
- ACCEPT does not mean automatic implementation

## Why This Protects Capital

This protects capital by keeping proposal review separate from implementation.
A proposal must still go through evidence checks, backtesting, and a separate
human-controlled implementation plan before any strategy behavior changes.

## Future Plan

Future versions can add an implementation plan workflow after backtesting, with
required evidence, risk review, and explicit human signoff.
