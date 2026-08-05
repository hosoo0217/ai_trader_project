# Local AI Research and Validation Provider Contract

## 1. Record identity and decision state

- Contract ID: `LOCAL-AI-RESEARCH-VALIDATION-PROVIDER-2026-08-05`.
- Contract version: `LOCAL-AI-RESEARCH-VALIDATION-1`.
- Status: `PROPOSED_FOR_INDEPENDENT_AUDIT`.
- Change type: `DOCUMENTATION_ONLY`.
- Global code freeze: `ACTIVE`.
- Trading, dataset-mutation, training, integration, staging, commit, and push
  authorization: `NOT GRANTED`.

This record locks the permitted role of a local language model before any
provider adapter is implemented. It neither approves model training nor connects
the model to strategy, risk, execution, datasets, or production systems.

## 2. Governing decisions and precedence

This contract is subordinate to and must not weaken:

- `docs/mvp_code_freeze.md`;
- `docs/gc_futures_ai_strategy_training_decision.md`;
- `docs/human_approval_workflow.md`;
- `docs/strategy_approval_pipeline.md`; and
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Where wording conflicts, the stricter non-execution, data-integrity,
no-look-ahead, or human-approval rule wins. The local model is not the Version-1
candidate-quality model described in the training decision and is not a
replacement for deterministic analyzers.

## 3. Exact provider boundary

The only provider class reserved by this contract is
`LOCAL_OPENAI_COMPATIBLE`. A conforming provider:

- runs on the same local machine;
- binds only to the loopback address `127.0.0.1`;
- exposes the OpenAI-compatible base URL `http://127.0.0.1:1234/v1`;
- has no automatic cloud, LAN, remote-tunnel, or second-model fallback;
- receives no repository, shell, browser, MCP, broker, email, or filesystem
  tool authority; and
- receives only the explicit immutable request payload supplied for one review.

Binding to `0.0.0.0`, a non-loopback interface, a remote host, or a proxy is a
stop condition. An unavailable local provider fails closed; it does not trigger
a fallback request.

## 4. Current provider evidence, not permanent trust

The provider observed during contract preparation was:

- runtime family: `LM Studio/Bionic local runtime`;
- local server: `127.0.0.1:1234`;
- local model ID: `qwen/qwen3.6-27b`;
- model format/quantization shown by the local UI: `GGUF / Q4_K_M`;
- local CLI version observed: `1.3.3.0`; and
- an OpenAI-compatible chat smoke test returned `LOCAL_OK`.

These observations prove connectivity only. They do not prove model quality,
determinism, safety, fitness for trading research, or future identity. Every run
must bind its actual runtime and model evidence under Section 17. A changed model,
quantization, runtime, endpoint, prompt template, or generation configuration is
a new provider-run identity.

## 5. Modes and default state

The exact modes are:

```text
OFF
RESEARCH_REVIEW
VALIDATION_REVIEW
```

The exact public enum values reserved for a later implementation are:

```text
LocalAIProviderKind: LOCAL_OPENAI_COMPATIBLE
LocalAIReviewMode: OFF, RESEARCH_REVIEW, VALIDATION_REVIEW
LocalAIReviewStatus: INVALID, AMBIGUOUS, UNKNOWN, VALID, NONE
LocalAIDataClassification: PUBLIC, PRIVATE_LOCAL, RESTRICTED_LOCAL
LocalAIEvidenceCompleteness: COMPLETE, BOUNDED
```

`OFF` is the mandatory default. `RESEARCH_REVIEW` may critique an already
assembled immutable research packet. `VALIDATION_REVIEW` may review an already
computed validation packet. Neither active mode grants strategy, data, training,
risk, or execution authority.

## 6. Permitted research and validation duties

Within an explicit review packet, the local model may only:

1. summarize already-computed deterministic evidence;
2. identify internal contradictions, missing explanations, or unclear claims;
3. compare stated methodology with supplied test or report evidence;
4. propose falsifiable hypotheses for later deterministic testing;
5. propose read-only audit questions and negative-control checks;
6. classify a claim as supported, unsupported, uncertain, or malformed within
   the supplied evidence boundary;
7. summarize failed, negative, and out-of-sample evidence without erasing it; and
8. draft non-authoritative review prose for a human reviewer.

The model may not assert that a hypothesis is evidence merely because it sounds
plausible. Any suggested experiment remains a proposal requiring separate scope,
implementation, deterministic tests, and human approval.

## 7. Absolute no-trading-authority boundary

The provider, request, and response schemas must contain no field that can
authorize or drive:

- `BUY`, `SELL`, long, short, directional bias, or trade/no-trade;
- entry, exit, stop, target, trailing stop, or order type;
- position size, leverage, margin, account risk, or capital allocation;
- broker, paper, simulated, replay, or live order submission;
- confidence-to-action thresholds, setup ranking for execution, or PnL targets;
- risk override, session override, safety-gate bypass, or strategy enablement; or
- autonomous selection of a strategy, detector, feature set, or trading setup.

Even a human-approved model response remains a research note. Human approval of
the note does not convert it into trading authority or automatic implementation.

## 8. No tool, network, or hidden-context authority

The local model must be invoked with tools disabled. It may not:

- call the internet, local network, cloud API, broker, Sierra Chart, CME, GitHub,
  OpenAI, Codex, email, or another model;
- execute shell commands or Python;
- browse, create, edit, delete, rename, or discover files;
- query a database, vector store, RAG index, or hidden memory; or
- request secrets, credentials, tokens, account information, or proprietary
  information not already present in the explicit packet.

The controller must treat tool-call syntax in model text as inert text and must
not execute it.

## 9. Immutable input and provider configuration contract

A review receives exactly one `LocalAIProviderConfig` and one
`LocalAIResearchRequest`. All public records are frozen. Their exact field order,
types, and defaults are:

```text
LocalAIProviderConfig
contract_version: str
provider_kind: LocalAIProviderKind
base_url: str
runtime_name: str
runtime_version: str
model_id: str
model_artifact_id: str
model_artifact_sha256: str | None
model_format: str
quantization: str
context_length: int
max_output_tokens: int
temperature: Decimal
top_p: Decimal
top_k: int
seed: int | None
prompt_template_sha256: str
system_prompt_sha256: str
response_schema_version: str

LocalAIArtifactReference
artifact_id: str
artifact_kind: str
sha256: str
byte_count: int
data_classification: LocalAIDataClassification
completeness: LocalAIEvidenceCompleteness
evidence_json: str
evidence_sha256: str
effective_index: int | None = None
effective_timestamp: datetime | None = None

LocalAIResearchRequest
request_id: str
contract_version: str
mode: LocalAIReviewMode
question_id: str
question: str
source_artifacts: tuple[LocalAIArtifactReference, ...] = ()
cutoff_index: int | None = None
cutoff_timestamp: datetime | None = None
postmortem_only: bool = False
```

All non-defaulted configuration fields are required. Numeric generation fields
use exact `Decimal`/integer values and canonical text serialization; booleans are
not accepted as integers. `model_artifact_sha256=None` is permitted only as
explicit unverified provenance and prevents a review from reaching `VALID`.

Inputs are caller-built, immutable, and point-in-time. Every artifact ID is
unique within the caller-supplied tuple. Hashes are lowercase 64-character
SHA-256 values, byte counts are nonnegative integers, and temporal timestamps are
timezone-aware normalized UTC values. At least one effective index or timestamp
is required for temporal evidence. Caller order is causal evidence and is never
silently sorted.

`question` must be limited to a Section 6 duty. Requests for trading action,
dataset mutation, training, tools, secrets, or forbidden output are rejected
before inference. The evidence body is canonical UTF-8 JSON text and must exactly
match `evidence_sha256`; the referenced source artifact must independently match
`sha256` and `byte_count`. The provider cannot follow file paths or URLs.
References without embedded evidence are provenance only and do not give the
provider read access.

## 10. Minimum-necessary and private-data rule

Only the minimum evidence needed for the stated question may enter the prompt.
Secrets, credentials, personal data, broker/account data, unrelated proprietary
code, and unrestricted repository contents are forbidden. Private market-data
evidence stays local and must be explicitly classified. Prompt and response
bodies remain outside Git by default; only approved redacted summaries and
cryptographic lineage metadata may be proposed for version control.

## 11. Dataset immutability boundary

The provider has read-only review access to an explicitly supplied packet. It
must not create, edit, repair, relabel, merge, split, delete, promote, or replace:

- raw, intake, canonical, derived, pilot, training, validation, or OOS data;
- manifests, acquisition records, calendars, roll maps, labels, features, or
  split assignments;
- fixtures, expected outputs, negative examples, or failed evidence; or
- model registries, checkpoints, metrics, reports, or promotion records.

Model text is never a canonical source, ground-truth label, dataset row, feature,
calendar fact, roll decision, or missing-value repair. A proposed correction must
be independently sourced and enter the normal immutable acquisition and review
workflow.

## 12. Training prohibition

This contract authorizes inference-only review. It forbids:

- foundation-model fine-tuning, adapters, LoRA, prompt tuning, or distillation;
- supervised, self-supervised, reinforcement, preference, online, or continual
  learning;
- automatic retraining, pseudo-labeling, synthetic-label generation, or
  self-evaluation loops;
- embedding-index or RAG-corpus construction from project evidence; and
- using model responses as targets, features, rewards, labels, or promotion
  criteria for the project candidate-quality model.

Any future training proposal requires a separate formal decision, data lineage,
leakage audit, evaluation protocol, rollback plan, and explicit authorization.

## 13. No-look-ahead and OOS protection

For a historical effective moment, the packet may contain only evidence available
at or before the locked cutoff. Future bars, later lifecycle states, revised
calendar facts unavailable at that moment, outcome labels, realized PnL, and
post-event explanations are forbidden unless the task is explicitly marked as a
postmortem that cannot feed model or rule selection.

The final locked OOS partition must not be placed in local-model prompts during
hypothesis generation, feature selection, threshold tuning, prompt tuning, or
model selection. Once an OOS result is unsealed, the reviewed candidate version
is immutable; its evidence may be summarized, but it cannot be used to retune and
then re-claim the same partition as untouched OOS.

## 14. Output status and precedence

The exact review statuses and precedence are:

```text
INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE
```

- `INVALID`: malformed schema, identity mismatch, forbidden field, unsafe
  provider state, or independently determinable contradiction.
- `AMBIGUOUS`: two or more incompatible interpretations remain supported by the
  supplied packet.
- `UNKNOWN`: evidence required to answer the question is unavailable or
  intentionally withheld.
- `VALID`: the response is schema-valid and its cited claims are traceable to the
  supplied packet. It does not mean a strategy, trade, dataset, or model is valid.
- `NONE`: the packet is valid but contains no reviewable claim for the question.

No status creates downstream authority. `INVALID`, `AMBIGUOUS`, or `UNKNOWN`
must never be converted to an optimistic default.

The exact reason-token vocabulary is:

```text
PROVIDER_OFF
PROVIDER_UNAVAILABLE
PROVIDER_NON_LOOPBACK
PROVIDER_IDENTITY_MISMATCH
MODEL_ARTIFACT_UNVERIFIED
MODEL_IDENTITY_MISMATCH
MALFORMED_INPUT
MALFORMED_OUTPUT
FORBIDDEN_REQUEST
FORBIDDEN_OUTPUT
TOOL_REQUESTED
SECRET_EXPOSURE
INSUFFICIENT_EVIDENCE
LOOKAHEAD_DETECTED
OOS_BOUNDARY_VIOLATION
SCOPE_BREACH
NO_REVIEWABLE_CLAIM
```

Unknown or free-form reason tokens are `INVALID`. Human-readable detail belongs
in findings, uncertainties, or verification requests and may not replace the
reason vocabulary.

## 15. Exact response contract

`LocalAIResearchReview` is an immutable record with exactly:

```text
contract_version: str
review_id: str
provider_run_id: str
request_id: str
mode: LocalAIReviewMode
source_artifact_ids: tuple[str, ...]
source_hashes: tuple[str, ...]
effective_index: int | None
effective_timestamp: datetime | None
status: LocalAIReviewStatus
response_sha256: str
findings: tuple[str, ...] = ()
uncertainties: tuple[str, ...] = ()
verification_requests: tuple[str, ...] = ()
reasons: tuple[str, ...] = ()
blocking_reasons: tuple[str, ...] = ()
```

The schema deliberately excludes action, direction, confidence, score, risk,
entry, exit, stop, target, size, order, PnL, dataset mutation, training command,
and tool-call fields. Unknown extra fields make the response `INVALID`.

The language model returns only the restricted status/findings/uncertainties/
verification/reason payload. The deterministic controller, not the model,
recomputes `request_id` and `provider_run_id`, copies the ordered source lineage
and request cutoff, validates all reason tokens and finding references, computes
`response_sha256`, computes `review_id`, and constructs the frozen public review.
`response_sha256` is the hash of canonical model payload excluding controller
IDs; `review_id` then binds that response hash without a circular hash. Every
finding must name at least one exact supplied artifact ID. The response effective
index/timestamp must exactly equal the request cutoff; the model cannot move the
effective moment.

## 16. Non-authoritative evidence rule

A model finding is a hypothesis or review comment, never primary evidence. A
claim may influence a later human decision only after its cited source is checked
and the claim is independently reproduced by deterministic code, an approved
source, a test, or a documented human audit. Unverifiable citations, invented
facts, unsupported arithmetic, and claims outside the packet are blocking.

The controller must never silently enrich a response, infer missing citations, or
repair malformed output. Prior valid reviews remain immutable when a later review
fails; the failing review and anything dependent on it are not promoted.

## 17. Provider-run identity and reproducibility

Every invocation requires a deterministic `provider_run_id` over canonical:

- contract version and provider kind;
- exact loopback base URL;
- runtime name and runtime version;
- model ID, model artifact identifier/hash when available, format, and
  quantization;
- prompt-template and system-prompt SHA-256 values;
- request ID, evidence SHA-256, and ordered source hashes;
- context-length limit, max-output-token limit, temperature, top-p, top-k, seed
  when supported, and all other generation parameters; and
- response schema version.

The model may remain nondeterministic despite fixed parameters. Repeatability
must be measured and reported; identical output must not be assumed. A retry is a
new attempt linked to the same request, never a silent replacement of prior
evidence.

## 18. Fail-closed provider behavior

The review is `INVALID` with no promotion when the endpoint is non-loopback, the
configured model does not exactly match the loaded model, required identity
evidence is malformed, a response violates schema, forbidden content is emitted,
or output cannot be parsed safely. Provider unavailable, timeout, context-limit
exhaustion, or missing necessary evidence returns `UNKNOWN` unless independently
determinable invalid evidence requires `INVALID`.

There is no fallback to a cloud service, different model, previous response,
uncited model memory, or permissive parser. Exceptions must be contained and
converted to the locked status/reason vocabulary.

## 19. Separation from Codex, OpenAI, and project models

The local provider is independent of Codex/OpenAI and independent of the future
candidate-quality model. One model may not automatically approve, grade, repair,
train, or promote another. A comparison between their outputs is a human-led
research exercise with explicit immutable inputs; agreement is not proof and
disagreement is not automatically `AMBIGUOUS` without source-backed alternatives.

## 20. Exact future public API and identity reservation

No Python API is authorized now. If a later bounded implementation is approved,
the only reserved keyword-only surface is:

```python
review_local_ai_research(
    *,
    provider: LocalAIProviderConfig,
    request: LocalAIResearchRequest,
) -> LocalAIResearchReview

make_local_ai_provider_run_id(
    *,
    provider: LocalAIProviderConfig,
    request_id: str,
) -> str

make_local_ai_request_id(
    *,
    contract_version: str,
    mode: LocalAIReviewMode,
    question_id: str,
    question_sha256: str,
    source_artifact_ids: tuple[str, ...] = (),
    source_hashes: tuple[str, ...] = (),
    cutoff_index: int | None = None,
    cutoff_timestamp: datetime | None = None,
    postmortem_only: bool = False,
) -> str

make_local_ai_review_id(
    *,
    contract_version: str,
    provider_run_id: str,
    request_id: str,
    source_artifact_ids: tuple[str, ...] = (),
    source_hashes: tuple[str, ...] = (),
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    mode: LocalAIReviewMode | None = None,
    status: LocalAIReviewStatus | None = None,
    response_sha256: str | None = None,
) -> str
```

`PROVIDER_RUN` identity requires every exact `LocalAIProviderConfig` field plus
`request_id`. `REQUEST` identity requires the exact request-builder fields shown
above and recomputes the ordered artifact IDs/hashes from the embedded tuple.
`REVIEW` identity requires every non-default argument of the review builder;
effective moment, mode, status, and response hash are material. Each builder
rejects unknown parameters, malformed hashes, noncanonical timestamps, and
field values that belong to another identity. The supplied IDs in public records
must exactly match recomputation.

All future public dataclasses must be frozen. Expanding this API, adding tools,
or adding action fields requires a new proposal and is not an implementation
detail.

## 21. Reserved future implementation scope

This document changes no implementation scope. A future first adapter, only
after separate audit and explicit freeze lift, is reserved to exactly:

- `ai/local_research_provider.py`;
- `tests/test_local_research_provider.py`; and
- `docs/local_ai_research_validation_checkpoint.md`.

Package exports, `main.py`, configuration, datasets, training pipelines,
candidate generation, decision engines, risk, broker, paper/live execution,
decision trace, SMC context wiring, external APIs, and all other files remain
forbidden. The three reserved paths are not authorized to be created by this
record.

## 22. Inline synthetic exact 36-case future test matrix

The logical matrix count is exactly 36; parameterization may increase collected
tests without changing the logical count.

1. `OFF` returns a canonical `NONE` envelope with `PROVIDER_OFF` and makes no
   provider call.
2. `RESEARCH_REVIEW` accepts a canonical immutable packet.
3. `VALIDATION_REVIEW` accepts a canonical immutable packet.
4. unknown mode is `INVALID`.
5. exact `127.0.0.1:1234/v1` loopback endpoint is eligible.
6. `0.0.0.0`, LAN, remote, proxy, and cloud endpoints are rejected.
7. unavailable server returns `UNKNOWN` with no fallback.
8. configured/loaded model mismatch is `INVALID`.
9. every provider field is required and runtime/model/quantization/generation
   changes create distinct provider-run IDs.
10. exact provider-run, request, and review identity schemas reject cross-kind,
    missing, forbidden, and malformed fields and reproduce deterministic IDs.
11. retries remain separate attempts and do not overwrite prior evidence.
12. non-tuple source references and malformed nested values are `INVALID`.
13. malformed hashes, duplicate IDs, or unequal ID/hash tuples are `INVALID`.
14. naive timestamps and noncanonical UTC moments are rejected or normalized by
    the caller before hashing.
15. caller order is preserved and no silent source sorting occurs.
16. file paths and URLs grant no read authority.
17. tool-call, shell, browser, filesystem, and network requests remain inert and
    invalidate the response when emitted as executable fields.
18. secret, credential, account, or unrelated private-data fields are rejected.
19. BUY/SELL, direction, confidence-to-action, and setup-selection fields are
    rejected.
20. risk, size, entry, exit, stop, target, order, and PnL fields are rejected.
21. dataset edit, label, feature, split, calendar, roll, or manifest mutations are
    rejected.
22. training, fine-tuning, embedding, pseudo-label, or automatic-retraining
    instructions are rejected.
23. model-generated facts cannot become canonical evidence or labels.
24. historical review rejects future bars, outcomes, later states, and PnL.
25. locked OOS evidence is unavailable during hypothesis or tuning review.
26. post-unseal OOS review is postmortem-only and cannot restore untouched status.
27. `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence is exact.
28. `VALID` means schema/evidence traceability only, never trade validity.
29. independent conflicting interpretations yield `AMBIGUOUS` without promotion.
30. missing required evidence yields `UNKNOWN` without optimistic default.
31. later malformed review preserves strictly prior immutable valid reviews.
32. unknown response fields, malformed JSON, and nested exceptions fail closed.
33. prompt/response/evidence/source hashes, byte counts, and ordered source
    lineage reconcile exactly.
34. response repeatability is measured and nondeterminism is not hidden.
35. exact keyword-only signatures, every typed/defaulted frozen field, exact
    enum/reason values, and exports match the contract.
36. exact three-path scope and forbidden imports/wiring remain absent.

All fixtures must be inline and synthetic. External market-data, account, calendar,
email, or model-response fixtures are forbidden for this first adapter matrix.

## 23. Promotion, rollback, and stop conditions

Promotion order is strictly:

1. independent semantic and structural audit of this one document;
2. explicit human acceptance of the provider and no-authority contract;
3. separate read-only implementation-readiness audit;
4. explicit bounded freeze lift for the exact three reserved paths;
5. test-first implementation and focused/full regression evidence;
6. independent final audit before staging; and
7. separate authorization before every commit, push, or integration step.

Rollback means disable the provider (`OFF`), preserve all review and negative
evidence, and return to deterministic research artifacts without altering
datasets or trading systems. Stop immediately on any non-loopback bind, cloud or
tool fallback, secret exposure, look-ahead, OOS contamination, dataset mutation,
training attempt, action field, execution path, unreviewed API expansion,
identity ambiguity, unavailable required provenance, or scope breach.

## 24. Final locked decision and next boundary

The local model is approved by this proposal only as a prospective,
non-authoritative, local-only research and validation reviewer. It owns no source
truth, dataset, training, strategy, risk, or trading authority. The immediate
next permitted action is an independent read-only audit of this exact document.
No Python, tests, fixtures, datasets, configuration, training, integration,
staging, commit, push, or provider wiring is authorized.

Decision token:
`LOCAL_AI_RESEARCH_VALIDATION_PROVIDER_CONTRACT_PROPOSED_FOR_INDEPENDENT_AUDIT`
