# Sierra Chart CSV Format Mapping

Real Sierra Chart CSV exports may not use the exact same column names as the
project's sample files. One export might use `time`, another might use
`Date Time`, and footprint volume columns might appear as `Bid Volume`,
`BidVolume`, `bid`, or similar names.

The importer now resolves those variants into one normalized footprint schema.
This is still CSV-only research/backtesting logic. It does not connect to Sierra
Chart live data, CME, brokers, or external APIs.

## Normalized Fields

The importer expects these internal fields:

- `time`
- `open`
- `high`
- `low`
- `close`
- `price`
- `bid_volume`
- `ask_volume`

## Supported Aliases

Time:
- `time`
- `datetime`
- `date_time`
- `timestamp`
- `Date Time`
- `DateTime`

Open, High, Low:
- `open`, `Open`
- `high`, `High`
- `low`, `Low`

Close:
- `close`
- `Close`
- `last`
- `Last`

Price:
- `price`
- `Price`
- `level`
- `Level`

Bid volume:
- `bid_volume`
- `Bid Volume`
- `BidVolume`
- `bid`
- `Bid`
- `bid_vol`

Ask volume:
- `ask_volume`
- `Ask Volume`
- `AskVolume`
- `ask`
- `Ask`
- `ask_vol`

## Normalization Rules

Column matching ignores:

- case
- spaces
- underscores

For example, `Bid Volume`, `bid_volume`, and `BIDVOLUME` resolve to the same
normalized column name.

## Safe Blocking

If any required field cannot be resolved, the importer returns an empty candle
list. This lets the data-quality gate keep Order Flow inactive instead of
allowing bad or incomplete CSV data into decision logic.

## Future Plan

After testing with actual Sierra Chart exported CSV files, the alias list can be
expanded or adjusted. The goal is to support practical export formats while
keeping the importer simple, safe, and research-only.
