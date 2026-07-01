# Order Flow Confirmation Design Approval Checklist

This document defines the required design approval checklist before any future Order Flow confirmation implementation.

It is documentation only. It does not change `main.py`, strategy code, `orderflow/*.py`, risk rules, or trading/integration behavior.

## 1. Proposed Final Blocking Semantics Decision Matrix

Implementation is not approved until this matrix is explicitly accepted.

### BUY / bullish trade

- [ ] OF BULLISH + high confidence: **ALLOW**
- [ ] OF NEUTRAL: **BLOCK**
- [ ] OF BEARISH: **BLOCK**
- [ ] OF low confidence: **BLOCK**

### SELL / bearish trade

- [ ] OF BEARISH + high confidence: **ALLOW**
- [ ] OF NEUTRAL: **BLOCK**
- [ ] OF BULLISH: **BLOCK**
- [ ] OF low confidence: **BLOCK**

## 2. Data-Quality Behavior

- [ ] If Order Flow data quality fails: **BLOCK**
- [ ] If Order Flow CSV is missing while strategy requires confirmation: **BLOCK**
- [ ] If Order Flow context cannot be computed: **BLOCK**
- [ ] If Order Flow module is inactive by config: explicit behavior is documented and approved before implementation

## 3. Required Implementation Tests Before Code Merge

- [ ] BUY allowed with BULLISH high-confidence OF
- [ ] BUY blocked with BEARISH OF
- [ ] BUY blocked with NEUTRAL OF
- [ ] BUY blocked with low-confidence OF
- [ ] SELL allowed with BEARISH high-confidence OF
- [ ] SELL blocked with BULLISH OF
- [ ] SELL blocked with NEUTRAL OF
- [ ] SELL blocked with low-confidence OF
- [ ] Data-quality failed blocks
- [ ] Missing Order Flow data blocks
- [ ] A/B report separates neutral, low-confidence, opposite-bias, and data-quality blocks

## 4. Day3 Validation Evidence (Design Input)

- [ ] 10m one-session supported NEUTRAL/low-confidence blocking as safety evidence
- [ ] 5m one-session revealed simple bias alignment is not enough
- [ ] 5m bearish revealed opposite-bias blocking was not modeled by current A/B diagnostic
- [ ] Therefore implementation remains **NOT READY** until this checklist is approved

## 5. Approval Status

- Status: **PENDING HUMAN APPROVAL**
- [ ] HOSOO explicitly approves this checklist before any code implementation
- [ ] No strategy or risk code may change before approval

## 6. Safety Reminder

- No implementation in this step.
- No strategy/risk/live/broker changes in this step.
- No `private_data` commits.
- No generated report commits.
