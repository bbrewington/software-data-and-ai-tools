# Kano Model Reference

Detailed methodology for feature categorization using customer satisfaction analysis.

## Overview

The Kano Model, developed by Professor Noriaki Kano, classifies features based on how they affect customer satisfaction. It reveals that not all features create value in the same way—some delight, some satisfy, and some are simply expected.

## The Five Categories

| Category | Also Called | Customer Reaction |
|----------|-------------|-------------------|
| **Must-be** | Basic, Expected | Absent = Frustrated. Present = Not impressed |
| **Performance** | One-dimensional, Linear | More = Better (proportional satisfaction) |
| **Attractive** | Delighters, Exciters | Absent = OK. Present = Delighted |
| **Indifferent** | Neutral | Doesn't affect satisfaction either way |
| **Reverse** | Adverse | Feature actually decreases satisfaction |

## Category Details

### Must-be (Basic)

- Table stakes; customers expect these
- Absence causes strong dissatisfaction
- Presence doesn't increase satisfaction
- Competitive parity—everyone has them
- Investment: Ensure coverage, don't over-invest

**Examples**: Security, basic reliability, core functionality

### Performance (One-Dimensional)

- More is better (linear relationship)
- Drives competitive differentiation
- Customers explicitly request these
- Can measure and compare
- Investment: Optimize for advantage

**Examples**: Speed, storage, price

### Attractive (Delighters)

- Customers don't expect them
- Absence doesn't cause dissatisfaction
- Presence creates delight
- Differentiation opportunity
- Investment: Strategic innovation

**Examples**: Unexpected features, exceptional service, surprise gifts

### Indifferent

- Customers don't care
- No impact on satisfaction
- Waste of resources
- Investment: Eliminate or minimize

### Reverse

- Some customers actively dislike
- Feature decreases satisfaction
- May indicate wrong customer segment
- Investment: Reconsider or make optional

## Kano Questionnaire

For each feature, ask two questions:

### Functional Question
"If [feature] is present, how do you feel?"

### Dysfunctional Question
"If [feature] is absent, how do you feel?"

### Response Options
1. I like it
2. I expect it
3. I'm neutral
4. I can tolerate it
5. I dislike it

## Evaluation Table

| | **Dysfunctional** |||||
|---|---|---|---|---|---|
| **Functional** | Like | Expect | Neutral | Tolerate | Dislike |
| Like | Q | A | A | A | O |
| Expect | R | I | I | I | M |
| Neutral | R | I | I | I | M |
| Tolerate | R | I | I | I | M |
| Dislike | R | R | R | R | Q |

**Key**: M=Must-be, O=One-dimensional, A=Attractive, I=Indifferent, R=Reverse, Q=Questionable

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ KANO ANALYSIS: [Product/Feature Set]                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ MUST-BE (Basics - Required but not differentiating)                          │
│ Feature                   Functional    Dysfunctional    Classification      │
│ [Feature 1]               [Response]    [Response]       Must-be             │
│ [Feature 2]               [Response]    [Response]       Must-be             │
│ Priority: High (ensure coverage)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ PERFORMANCE (Linear - More is better)                                        │
│ [Feature 1]               [Response]    [Response]       Performance         │
│ [Feature 2]               [Response]    [Response]       Performance         │
│ Priority: High (competitive advantage)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ ATTRACTIVE (Delighters - Unexpected pleasures)                               │
│ [Feature 1]               [Response]    [Response]       Attractive          │
│ [Feature 2]               [Response]    [Response]       Attractive          │
│ Priority: Medium (strategic innovation)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ INDIFFERENT (Don't invest here)                                              │
│ [Feature 1]               [Response]    [Response]       Indifferent         │
│ Priority: Low (minimize investment)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ REVERSE (Reconsider these)                                                   │
│ [Feature 1]               [Response]    [Response]       Reverse             │
│ Action: [Make optional / Remove / Segment]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Strategic Implications

### Investment Priority

| Category | Investment Strategy |
|----------|---------------------|
| Must-be | Meet threshold, don't over-invest |
| Performance | Invest to beat competition |
| Attractive | Selective investment for differentiation |
| Indifferent | Minimize or eliminate |
| Reverse | Remove or make optional |

### Category Decay

Over time, Attractive → Performance → Must-be

- Yesterday's delight is today's expectation
- Continuous innovation required
- Monitor category shifts

## Running a Kano Study

### Sample Size
- 20-30 respondents for directional insights
- 100+ for statistical significance

### Analysis
1. Collect responses
2. Classify each response using evaluation table
3. Aggregate across respondents
4. Assign category based on plurality

### Visualization

Plot features on satisfaction chart:
- X-axis: Presence/implementation level
- Y-axis: Customer satisfaction
- Different curves for each category

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Only asking what customers want | Miss the "why" | Use dysfunctional question |
| Ignoring context | Wrong segment | Segment your analysis |
| Static analysis | Categories shift | Reassess periodically |
| Treating all Must-be equal | Over-investment | Threshold thinking |
| Chasing only Delighters | Missing basics | Balance the portfolio |

## Sources

- Kano, N. et al. (1984). Attractive Quality and Must-be Quality. Journal of the Japanese Society for Quality Control.
- Product management and quality practices
