# Reports and .gitignore Safety Review

This document explains how to handle generated reports, logs, exported data, and private files safely in `ai_trader_project`.

It is documentation only. It does not add trading features, change strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

The project can generate local reports and logs during demo, backtest, Order Flow replay, approval, proposal, implementation review, and readiness workflows.

Those files can contain session data, review notes, strategy-improvement ideas, Order Flow summaries, or future private trading data. They should be reviewed before they are committed or shared.

## 2. Why Generated Files Need Care

Generated files may eventually include:

- session notes,
- trading session summaries,
- Order Flow replay output,
- strategy review notes,
- human approval decisions,
- implementation plans,
- real Sierra Chart export details,
- private trading context.

Even when the current files are demo-only, the safe habit is to treat generated outputs as private unless intentionally reviewed and approved for sharing.

## 3. Never Commit

These should never be committed:

- API keys,
- broker credentials,
- account numbers,
- secrets,
- `.env` files,
- private broker exports,
- real account data,
- private API tokens,
- real order execution data,
- private notes that should not be public,
- unreviewed generated reports or logs.

Safety reminder:

- No live trading.
- No broker credentials.
- No real account data.
- No private API keys.
- No real order execution data.

## 4. Be Careful Before Committing

Review these before committing:

- generated files under `reports/`,
- generated logs under `logs/`,
- real Sierra Chart CSV exports,
- broker/platform exports,
- generated JSON/TXT/CSV files,
- any file copied from a real trading platform.

Real Sierra Chart exports should be reviewed before committing. If they include real session data, private workspace details, account identifiers, or broker information, do not commit them.

## 5. Safe To Commit

Usually safe to commit:

- source code,
- tests,
- documentation,
- synthetic/demo sample CSV files used by tests,
- intentionally reviewed example files,
- configuration templates without secrets.

Sample data can be committed only if it is synthetic/demo data and does not contain real account, broker, or private trading information.

## 6. Usually Ignored

Generated reports should usually be ignored unless intentionally kept as examples.

The `.gitignore` should protect:

```gitignore
reports/*.json
reports/*.txt
reports/*.csv
logs/
*.log
.env
secrets/
private_data/
```

These patterns protect generated and private local files without ignoring source docs, tests, or the existing demo CSV files in `data/`.

## 7. How To Check Before Committing

Run:

```powershell
git status --short
```

Review every file listed.

For changed files, inspect the diff:

```powershell
git diff -- README.md docs/
```

For new files, open them and check for secrets or private trading data before staging.

Before committing, ask:

- Is this source code, documentation, or reviewed demo data?
- Does it contain API keys, broker credentials, account numbers, or secrets?
- Does it contain real trading account data?
- Is it a generated report that should stay local?
- Is it needed by tests or examples?

If unsure, do not commit it yet.

## 8. Example Git Status Review

Example safe output:

```text
 M README.md
 M .gitignore
?? docs/reports_gitignore_safety.md
```

These are documentation or ignore-rule changes and can be reviewed normally.

Example risky output:

```text
?? reports/session_history.json
?? reports/trading_session_report.txt
?? data/real_sierra_export.csv
?? .env
```

Do not commit these until they are reviewed. `.env` should never be committed.

## 9. Current Ignore Decision

The project keeps demo CSV files in `data/` available for tests and examples.

The project ignores generated report outputs by extension inside `reports/`:

- `reports/*.json`
- `reports/*.txt`
- `reports/*.csv`

This allows the folder to exist locally while preventing common generated outputs from being accidentally committed.

Decision completed on 2026-07-13: the reviewed runtime-generated JSON and TXT report snapshots were removed from Git tracking with `git rm --cached` while remaining available locally. They are not canonical examples or test fixtures. The existing `reports/*.json`, `reports/*.txt`, and `reports/*.csv` rules prevent these generated snapshots from being added again accidentally.

Check currently tracked report files with:

```powershell
git ls-files reports
```

## 10. Beginner Summary

Some files are written by the program when you run demos, reports, replay, or approval flows. Those files can contain private notes or future real trading data.

Source code, docs, tests, and reviewed demo data are usually okay to commit. Secrets, credentials, account numbers, real broker exports, and unreviewed generated reports are not okay to commit.

When in doubt, check `git status --short`, inspect the file, and keep private generated data out of git.
