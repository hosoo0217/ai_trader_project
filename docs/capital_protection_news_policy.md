# Capital Protection News Policy

## Scope

Documentation-only policy for how manually maintained economic-news protection should behave before any future production enforcement, broker integration, live-data integration, external calendar integration, or simulation expansion.

## Purpose

Define the approved news-event source, update responsibility, audit requirements, impact-level behavior, blocking windows, invalid-data handling, and position-treatment rules for capital protection decisions.

## Current implementation checkpoint

Current news filtering is research-only and manual-only. It evaluates manually configured `NewsEvent` records and does not connect to an external economic-calendar API, official-source feed, broker feed, MT5, Sierra live data, CME live data, or any other live service.

Each event contains a name, UTC event time, impact level, configurable minutes before the event, configurable minutes after the event, and an enabled flag.

The default event window is 30 minutes before through 30 minutes after the configured event time.

The standard default configuration blocks HIGH-impact events and allows MEDIUM- and LOW-impact events. SAFE_DEFAULT or disabled-profile fallback behavior blocks HIGH, MEDIUM, and LOW impact levels conservatively.

A missing or invalid current time returns `INVALID_TIME` and blocks the decision. A naive datetime is interpreted as UTC. An explicitly disabled news filter returns `FILTER_DISABLED` and allows the decision. An explicitly disabled event is ignored.

The supported manual CLI event format is `NAME:TIME:IMPACT`. Valid impact values are `HIGH`, `MEDIUM`, and `LOW`. Invalid event input produces a warning and must not be added to the active event list.

## Approved event source

Version 1 is manual-only.

Each configured event must be transcribed from a clearly identified public economic-calendar or official announcement source by an authorized project operator. The source name, source reference or URL when available, event name, published event time, interpreted UTC time, impact classification, and time of entry must be recorded in an auditable project-side record.

An external calendar API, automatic scraper, automatic feed importer, browser automation workflow, or unattended event updater is not approved.

The manual source record is evidence for offline research and validation only. It does not establish that the source is complete, timely, official, or suitable for live trading.

## Manual update rules

News events must be entered before the relevant offline simulation or paper-flow evaluation begins.

Event time must be normalized to UTC before evaluation. Daylight-saving-time conversion, source timezone, and any source revision must be checked explicitly by the operator.

An event may be enabled only when its name, time, impact level, source, and update timestamp are known.

Corrections must not silently overwrite prior records. A correction must preserve an audit trail showing the original value, corrected value, correction reason, correction time, and operator.

Expired events may be removed from the active configuration only after their audit record is retained.

If the event schedule is incomplete, uncertain, stale, malformed, or unavailable, the dataset must not be represented as fully news-protected.

## Audit requirements

Every offline run that uses news protection must be reproducible from the event list used for that run.

The audit record should include:

- dataset or run identifier;
- event name;
- source name and reference;
- source timezone;
- original published time;
- normalized UTC time;
- impact level;
- minutes blocked before and after;
- enabled or disabled state;
- entry or update timestamp;
- operator or process responsible for the manual entry;
- any warning, correction, omission, or known uncertainty.

The event list and audit record must remain outside `private_data` commits when they contain private, licensed, restricted, or non-public material.

A run with no configured events must be recorded as using an empty manual event list, not described as having verified that no relevant news existed.

## Profile behavior

The standard default profile blocks HIGH-impact events and allows MEDIUM- and LOW-impact events unless explicitly configured otherwise.

SAFE_DEFAULT or disabled-profile fallback behavior blocks HIGH-, MEDIUM-, and LOW-impact events conservatively.

Profile-specific changes to blocked impact levels or event windows must be explicit, documented, and covered by tests. They must not be inferred automatically from symbol, market, strategy, or account type.

## Resolved policy

Version 1 remains manual-only. External economic-calendar feeds and automatic event ingestion are not approved.

Only the impact values `HIGH`, `MEDIUM`, and `LOW` are valid for configured events.

The default blocking window remains 30 minutes before through 30 minutes after an enabled blocking event.

Configured window boundaries are inclusive.

A disabled event must be ignored.

An explicitly disabled filter may allow a new-entry decision and must return a reason indicating that the filter was disabled.

Missing or invalid current time must block conservatively with `INVALID_TIME`.

A naive current time or event time must be treated as UTC. Timezone-aware values must be converted to UTC before comparison.

Malformed manual CLI events must produce a warning and must not enter the active event list.

An invalid event timestamp inside an otherwise loaded event record must be ignored with a recorded reason. It must not crash the evaluation or silently become an active block.

A news block applies to new-entry decisions only. It must not automatically close, reduce, reverse, hedge, move stops, alter targets, or otherwise modify an already-open position.

The filter must not claim complete news coverage unless the manual event source and update process for the evaluated period are documented and auditable.

## Not approved

This policy does not approve live trading, broker connectivity, MT5 integration, Sierra live integration, CME live data, external APIs, automatic economic-calendar ingestion, scraping, unattended updates, real orders, automatic modification of existing positions, or production strategy and risk-behavior changes.

## Test implications

Tests must verify:

- HIGH-impact blocking under the standard default configuration;
- MEDIUM- and LOW-impact allowance under the standard default configuration;
- HIGH-, MEDIUM-, and LOW-impact blocking under SAFE_DEFAULT or disabled-profile fallback behavior;
- inclusive before-and-after event-window boundaries;
- custom event buffer behavior;
- invalid or missing current-time blocking;
- naive datetime interpretation as UTC;
- timezone-aware conversion to UTC;
- explicit disabled-filter allowance;
- disabled-event exclusion;
- valid manual CLI parsing;
- invalid impact and malformed-event warnings;
- exclusion of invalid CLI events from the active list;
- invalid event-time handling;
- new-entry-only blocking;
- no automatic modification of existing positions;
- absence of broker, live-data, or external-calendar dependencies.

## Recommended next step

Validate this policy through reproducible offline simulation and backtest evidence using versioned manual event lists and retained audit records before considering any broader enforcement or integration change.
