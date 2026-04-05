# KPI Tree Reference

Detailed methodology for building KPI/driver trees.

## Overview

A KPI tree (driver tree) breaks down an outcome metric into its component drivers, creating a hierarchy that shows what influences results and where to focus improvement efforts.

## Building a KPI Tree

### Step 1: Define the Outcome

What's the top-level metric? (Revenue, conversion, retention, etc.)

### Step 2: Identify Drivers

What directly causes the outcome to change? Use mathematical relationships.

### Step 3: Decompose Further

For each driver, what drives that? Continue until actionable.

### Step 4: Assign Ownership

Which team owns each lever?

## Common Patterns

### Revenue Tree

```
Revenue = Customers × ARPU
Customers = New + Retained - Churned
ARPU = Price × Frequency
```

### SaaS Revenue

```
MRR = New MRR + Expansion MRR - Churned MRR
New MRR = Leads × Conversion × ACV
```

### Conversion Tree

```
Conversion = Visits × Conversion Rate
Conversion Rate = Consideration × Purchase
```

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ KPI TREE: [Outcome Metric]                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    [Outcome Metric]                                          │
│                         │                                                    │
│           ┌─────────────┼─────────────┐                                      │
│           ▼             ▼             ▼                                      │
│      [Driver 1]   [Driver 2]    [Driver 3]                                   │
│           │             │             │                                      │
│       ┌───┴───┐     ┌───┴───┐     ┌───┴───┐                                 │
│       ▼       ▼     ▼       ▼     ▼       ▼                                 │
│    [Sub]   [Sub] [Sub]   [Sub] [Sub]   [Sub]                                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ KEY LEVERS                                                                   │
│ 1. [Metric] - Owner: [Team] - Current: X - Target: Y                        │
│ 2. [Metric] - Owner: [Team] - Current: X - Target: Y                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Uses

| Application | Benefit |
|-------------|---------|
| Diagnosis | Find underperforming drivers |
| Prioritization | Focus on high-impact levers |
| Alignment | Assign metrics to teams |
| Forecasting | Model impact of changes |

## Sources

- Financial modeling practices
- Product analytics methodology
