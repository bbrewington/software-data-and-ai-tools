# RICE Scoring Reference

Detailed methodology for RICE prioritization.

## Overview

RICE is a prioritization framework developed by Intercom that scores initiatives based on Reach, Impact, Confidence, and Effort. It produces a numeric score for objective comparison.

## The Formula

```
RICE Score = (Reach × Impact × Confidence) ÷ Effort
```

## Component Definitions

### Reach

**How many people will this affect per time period?**

| Measure | Examples |
|---------|----------|
| Users/month | 1000 users per month |
| Transactions/quarter | 5000 transactions per quarter |
| Customers/year | 500 customers per year |

Use concrete estimates, not percentages.

### Impact

**How much will this affect each person?**

| Score | Meaning | Description |
|-------|---------|-------------|
| 3 | Massive | Transformative change |
| 2 | High | Significant improvement |
| 1 | Medium | Noticeable improvement |
| 0.5 | Low | Minimal improvement |
| 0.25 | Minimal | Slight improvement |

### Confidence

**How sure are you of your estimates?**

| Score | Meaning | Evidence Level |
|-------|---------|----------------|
| 100% | High | Solid data, proven results |
| 80% | Medium | Some data, reasonable assumptions |
| 50% | Low | Limited data, educated guess |

Be honest—confidence is a discount factor.

### Effort

**How much work will this take?**

Measured in person-months (or person-weeks, person-days). Include all work: design, development, testing, launch.

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ RICE SCORING: [Initiative Name]                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ REACH                                                                        │
│ Estimate: [Number] [users/transactions/customers] per [time period]         │
│ Basis: [How did you estimate this?]                                          │
│ Value: _______                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ IMPACT                                                                       │
│ Expected effect: [Description of impact]                                     │
│ Score: □ 3 (Massive)  □ 2 (High)  □ 1 (Medium)  □ 0.5 (Low)  □ 0.25 (Min)  │
│ Value: _______                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ CONFIDENCE                                                                   │
│ Evidence: [What data supports your estimates?]                               │
│ Score: □ 100% (High)  □ 80% (Medium)  □ 50% (Low)                           │
│ Value: _______                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ EFFORT                                                                       │
│ Work required: [Description of work]                                         │
│ Estimate: _______ person-months                                              │
│ Value: _______                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ RICE SCORE                                                                   │
│ (Reach × Impact × Confidence) ÷ Effort                                       │
│ (___ × ___ × ___) ÷ ___ = ___                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Comparison Table

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ RICE COMPARISON                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Initiative          Reach    Impact  Conf    Effort  RICE Score  Priority   │
│ [Initiative A]      5000     2       80%     3       2666        #1         │
│ [Initiative B]      1000     3       100%    2       1500        #2         │
│ [Initiative C]      10000    0.5     50%     4       625         #3         │
│ [Initiative D]      2000     1       80%     5       320         #4         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Calibration Tips

### Reach
- Use data from similar features
- Check analytics for comparable touchpoints
- Be specific about the time period
- Consider adoption curve

### Impact
- Reference past projects with known impact
- Use team consensus
- Consider both direct and indirect effects
- Don't over-index on new/shiny

### Confidence
- Lower confidence = higher uncertainty = lower score
- Consider: data quality, assumptions, dependencies
- 50% should be your minimum for planning
- Re-score after learning more

### Effort
- Include all disciplines
- Add buffer for unknowns
- Consider dependencies and blockers
- Use planning poker for team alignment

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Inflating impact | Everything is "massive" | Calibrate across projects |
| 100% confidence always | No uncertainty discount | Be honest about unknowns |
| Only dev effort | Underestimate total work | Include all work types |
| Inconsistent reach units | Can't compare | Standardize measurement |
| Gaming the numbers | Loses meaning | Review collectively |

## When to Use RICE

| Good for | Not ideal for |
|----------|---------------|
| Feature prioritization | Strategic decisions |
| Backlog ranking | Technical debt |
| Resource allocation | Compliance requirements |
| Objective comparison | Research projects |

## Sources

- McBride, S. (2016). RICE: Simple prioritization for product managers. Intercom.
- Product management practices
