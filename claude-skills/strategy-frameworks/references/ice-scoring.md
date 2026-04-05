# ICE Scoring Reference

Detailed methodology for ICE prioritization.

## Overview

ICE is a simple prioritization framework that scores initiatives on Impact, Confidence, and Ease. Popularized by Sean Ellis for growth experiments, it provides quick, intuitive scoring.

## The Formula

```
ICE Score = (Impact + Confidence + Ease) ÷ 3
```

Or multiplicative:
```
ICE Score = Impact × Confidence × Ease
```

All factors rated 1-10.

## Component Definitions

### Impact

**How much will this move the needle?**

| Score | Meaning |
|-------|---------|
| 10 | Game-changing impact on key metric |
| 7-9 | Significant positive effect |
| 4-6 | Moderate improvement |
| 1-3 | Minimal expected impact |

Consider: Which metric? By how much?

### Confidence

**How sure are you this will work?**

| Score | Meaning | Evidence |
|-------|---------|----------|
| 10 | Certain | Proven elsewhere, strong data |
| 7-9 | Likely | Good evidence, some assumptions |
| 4-6 | Possible | Limited data, reasonable hypothesis |
| 1-3 | Uncertain | Gut feel, unvalidated |

Consider: What's the evidence? What could go wrong?

### Ease

**How easy is this to implement?**

| Score | Meaning |
|-------|---------|
| 10 | Trivial (hours of work) |
| 7-9 | Easy (days of work) |
| 4-6 | Moderate (weeks of work) |
| 1-3 | Hard (months of work, complex) |

Consider: Time, cost, dependencies, complexity.

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ICE SCORING: [Initiative Name]                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ IMPACT                                                                       │
│ Target metric: [Which metric will this affect?]                              │
│ Expected change: [How much improvement?]                                     │
│ Score (1-10): ___                                                            │
│ Rationale: [Why this score?]                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ CONFIDENCE                                                                   │
│ Evidence: [What supports this will work?]                                    │
│ Risks: [What could cause it to fail?]                                        │
│ Score (1-10): ___                                                            │
│ Rationale: [Why this score?]                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ EASE                                                                         │
│ Work required: [What needs to be done?]                                      │
│ Dependencies: [What else is needed?]                                         │
│ Score (1-10): ___                                                            │
│ Rationale: [Why this score?]                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ICE SCORE                                                                    │
│ Average: (I + C + E) ÷ 3 = (___ + ___ + ___) ÷ 3 = ___                      │
│ -or-                                                                         │
│ Product: I × C × E = ___ × ___ × ___ = ___                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Comparison Table

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ICE COMPARISON                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Experiment              Impact  Confidence  Ease   ICE Score   Priority     │
│ [Experiment A]          8       7           9      8.0         #1           │
│ [Experiment B]          9       6           6      7.0         #2           │
│ [Experiment C]          6       8           7      7.0         #3           │
│ [Experiment D]          10      4           3      5.7         #4           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ICE vs. RICE

| Aspect | ICE | RICE |
|--------|-----|------|
| Factors | 3 | 4 |
| Reach | Not explicit | Explicit |
| Scoring | 1-10 scale | Mixed units |
| Complexity | Simpler | More rigorous |
| Best for | Quick prioritization | Detailed analysis |
| Common use | Growth experiments | Feature planning |

## Calibration Tips

### Impact
- Anchor to your key metric
- Compare to past wins: "Is this bigger than X?"
- Consider both magnitude and likelihood
- Don't double-count with confidence

### Confidence
- Start at 5 (neutral) and adjust
- Evidence raises score
- Unknowns lower score
- Prior similar work raises score

### Ease
- Inverse of effort
- Include all work (not just dev)
- Consider opportunity cost
- Account for dependencies

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Always high impact | No differentiation | Force rank against each other |
| Ignoring evidence | Overconfident | Document reasoning |
| Forgetting dependencies | Underestimate difficulty | Consider full scope |
| Solo scoring | Bias | Score as a team |
| Skipping rationale | Can't calibrate later | Always document why |

## When to Use ICE

| Good for | Not ideal for |
|----------|---------------|
| Growth experiments | Large initiatives |
| Quick triage | Strategic decisions |
| Brainstorm filtering | Resource planning |
| Early-stage ideas | Detailed estimation |

## Sources

- Ellis, S. Growth hacking methodology.
- Startup and growth team practices
