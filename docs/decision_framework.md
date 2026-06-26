# Decision Framework

This document defines the architectural foundation for the AI Trading Platform. Its purpose is to ensure that every analytical module contributes to one unified decision structure called DecisionContext.

## 1. Design Purpose

The platform must remain:
- Modular: each module owns a specific analytical domain.
- Scalable: new modules can be added without breaking the decision flow.
- Testable: each module can be validated independently through its context output.
- Explainable: every decision can be traced to the evidence provided by each domain.

The core rule is simple:

> Future modules must integrate through DecisionContext rather than directly communicating with each other.

---

## 2. Core Architectural Principle

Every module produces a structured context object that represents its view of the market at a given moment.

These context objects are then combined into a single DecisionContext, which becomes the shared input to the Decision Engine.

The Decision Engine does not replace the modules. It orchestrates, validates, reconciles, and produces the final decision.

---

## 3. DecisionContext

DecisionContext is the unified contract for the platform.

It represents the complete state of analysis at a specific decision point and is the only structure that should be consumed by the Decision Engine.

### Purpose

DecisionContext is the single source of truth for:
- what the market is doing,
- how much risk is acceptable,
- what order flow is suggesting,
- how smart money concepts are framing structure,
- how candle range theory is interpreting range behavior,
- and what decision should be made.

### Responsibilities

DecisionContext should contain:
- a snapshot of the current market environment,
- the outputs from all major analysis modules,
- the current risk posture,
- the decision-ready evidence set,
- and the final decision metadata.

### Design Intent

DecisionContext should be:
- deterministic for a given input snapshot,
- extensible as new modules are added,
- and independent from any single module implementation.

---

## 4. Context Domains

The platform is divided into domain-specific contexts. Each module contributes one context object.

### 4.1 MarketContext

MarketContext captures the broad market environment.

#### Information it should provide
- Market regime or bias
- Trend direction and strength
- Volatility level
- Momentum or momentum quality
- Timeframe alignment
- Market structure summary
- General confidence or evidence strength

#### Purpose

This context answers the question:
- What is the market broadly doing right now?

It provides the base environment against which all other modules are interpreted.

---

### 4.2 RiskContext

RiskContext captures the risk and capital protection view of the decision.

#### Information it should provide
- Maximum acceptable exposure
- Risk per trade constraints
- Position sizing guidance
- Stop-loss validity
- Take-profit validity
- Daily loss or drawdown limits
- No-trade conditions
- Capital protection constraints

#### Purpose

This context answers the question:
- Is this decision acceptable from a risk perspective?

RiskContext is a gating layer. Even when a signal is attractive, the decision may be rejected or reduced if risk rules are not satisfied.

---

### 4.3 OrderFlowContext

OrderFlowContext captures the pressure behind price movement.

#### Information it should provide
- Buying vs. selling pressure
- Aggressive participation signals
- Imbalance or absorption signals
- Volume-based confirmation or rejection
- Exhaustion or continuation clues
- Short-term pressure shifts
- Execution-related context

#### Purpose

This context answers the question:
- What is the immediate buying or selling pressure behind the move?

It provides a real-time view of participation and pressure that may not be obvious from price structure alone.

---

### 4.4 SMCContext

SMCContext captures the smart money interpretation of market structure and liquidity.

#### Information it should provide
- Market structure state
- Break of Structure or Change of Character signals
- Liquidity considerations
- Order block or zone relevance
- Fair Value Gap relevance
- Premium and discount zone interpretation
- Structural bias or invalidation conditions

#### Purpose

This context answers the question:
- What is the likely structural intent of the market from a smart money perspective?

It adds a higher-level view of market behavior based on liquidity, imbalance, and structure.

---

### 4.5 CRTContext

CRTContext captures candle range behavior and range-based market interpretation.

#### Information it should provide
- Range state and quality
- Expansion or contraction behavior
- Manipulation or trap-like patterns
- Range-based continuation or reversal clues
- Candle structure significance
- Confirmation or invalidation conditions tied to range behavior

#### Purpose

This context answers the question:
- How is price behaving within and around its candle ranges?

It contributes a range-based perspective that complements structure, order flow, and risk analysis.

---

## 5. How the Modules Contribute

Each module should produce its own context object independently.

The module responsibilities are:
- observe the market through its domain,
- produce a structured interpretation,
- attach confidence and evidence quality,
- and contribute that context to DecisionContext.

### Integration Rules

The following rules must be preserved:
- Modules do not directly call other modules for decision logic.
- Modules do not mutate each other’s internal state.
- Each module exposes a clean context output contract.
- DecisionContext becomes the shared integration layer.

This ensures that the system can evolve without tightly coupling modules together.

---

## 6. How the Decision Engine Combines the Contexts

The Decision Engine is responsible for combining all context objects into one coherent decision.

### Its role is not to replace the modules.

Instead, it should:
- receive each context object,
- validate that the contexts are complete and compatible,
- reconcile overlapping signals,
- identify conflicts between domains,
- apply risk gating,
- and produce a final decision with rationale.

### Decision Engine responsibilities

The Decision Engine should:
1. Collect the MarketContext, RiskContext, OrderFlowContext, SMCContext, and CRTContext.
2. Normalize the evidence into a common decision frame.
3. Compare the directional bias from each domain.
4. Resolve contradictions by weighting evidence and confidence.
5. Apply risk constraints before finalizing a trade decision.
6. Produce a decision outcome such as:
   - enter,
   - hold,
   - exit,
   - avoid,
   - or no-trade.
7. Provide a human-readable explanation of why the decision was made.

### Decision logic principle

The Decision Engine should treat each context as a perspective rather than a command.

A strong signal from one domain should not automatically override the others. The engine should combine them into a unified view.

---

## 7. Decision Output

The final output of the system should be a decision that is grounded in all major perspectives.

A good decision output should include:
- the selected action,
- the main reasons behind it,
- the risk status,
- the evidence from each domain,
- and any conditions that would invalidate or change the decision.

This makes the system suitable for both research and explanation.

---

## 8. Why This Architecture Matters

This framework makes the platform:
- easier to extend with new analytical modules,
- easier to test in isolation,
- easier to explain to users,
- and more resilient to architecture drift.

The key architectural promise is that each module contributes evidence, while the Decision Engine owns synthesis.

---

## 9. Architectural Summary

The platform should be designed around the following sequence:

1. Market data is observed.
2. Each module produces its own context object.
3. All context objects are placed into DecisionContext.
4. The Decision Engine evaluates the combined evidence.
5. A final decision is produced with explanation and risk awareness.

This structure ensures that the platform remains coherent, modular, and future-ready.
