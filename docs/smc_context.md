# SMC Context Combiner v1

This document explains why and how the SMC context combiner exists.

## Why SMCContext Exists

Market Structure, BOS/CHOCH, and Liquidity Sweep each describe only one part of smart-money behavior.

The SMC context combiner summarizes these pieces into one unified context so the larger decision framework can consume SMC evidence in a consistent format.

## How Evidence Is Combined

The combiner reads three sources:
- Market Structure result
- BOS/CHOCH result
- Liquidity Sweep result

Each source can add bullish or bearish evidence.

### Evidence scoring (v1)

- Market Structure BULLISH adds bullish evidence.
- Market Structure BEARISH adds bearish evidence.
- Latest BOS/CHOCH BULLISH adds bullish evidence.
- Latest BOS/CHOCH BEARISH adds bearish evidence.
- Latest LOW_SWEEP / BULLISH sweep adds bullish evidence.
- Latest HIGH_SWEEP / BEARISH sweep adds bearish evidence.

Bias is then decided as:
- more bullish evidence -> BULLISH
- more bearish evidence -> BEARISH
- equal evidence -> NEUTRAL
- no usable evidence -> UNKNOWN

## Confidence (v1)

Confidence is a simple bounded score (0 to 100):
- aligned evidence raises confidence
- conflicting evidence lowers confidence
- no evidence gives confidence 0

Optional requirements can gate the final context:
- require structure alignment
- require liquidity sweep
- require BOS/CHOCH
- minimum confidence threshold

## Why This Is Still Not an Entry Signal

SMCContext is only a summary layer.

It does not execute trades and should not be used alone for entries.
It must be combined with broader confirmation and risk controls.

## Future Integration Plan

Next iterations are expected to connect SMC context with:
- CRT confirmation
- Order Flow confirmation
- risk gates and safety checks

Longer-term plan:
- produce a richer SMC score
- map that score into DecisionContext with clearer cross-domain weighting
