# Hypothesis Tree Reference

Detailed methodology for assumption mapping and validation.

## Overview

A hypothesis tree (or assumption map) is a structured way to identify, prioritize, and test the assumptions underlying a strategy, product, or decision. By making assumptions explicit, teams can focus learning efforts on the riskiest beliefs.

## Core Process

### Step 1: State the Bet

What are you betting on? Express as a clear statement:
- "We believe [X] will succeed because [Y]"
- "Our strategy depends on [A], [B], and [C] being true"

### Step 2: Decompose into Assumptions

Break down into testable components:

| Category | Questions |
|----------|-----------|
| **Desirability** | Do customers want this? Will they pay? |
| **Viability** | Can we make money? Is the model sustainable? |
| **Feasibility** | Can we build/deliver it? Do we have capabilities? |
| **Usability** | Can users figure it out? Will they succeed? |

### Step 3: Assess and Prioritize

For each assumption, rate:
- **Importance (1-10)**: If wrong, how much does it matter?
- **Evidence (1-10)**: How much evidence do we have?

Calculate risk: `Risk = Importance × (10 - Evidence)`

### Step 4: Design Tests

For high-risk assumptions, design experiments.

### Step 5: Learn and Iterate

Update assumptions based on evidence.

## Assumption Categories

### Desirability Assumptions

| Assumption Type | Example |
|-----------------|---------|
| Problem exists | "Customers struggle with X" |
| Problem matters | "This is a top-3 pain point" |
| Willingness to pay | "Customers will pay $Y for this" |
| Switching | "Customers will switch from current solution" |

### Viability Assumptions

| Assumption Type | Example |
|-----------------|---------|
| Revenue model | "We can charge $X per unit" |
| Unit economics | "CAC < LTV/3" |
| Market size | "Market is >$XM" |
| Margins | "Gross margin >50%" |

### Feasibility Assumptions

| Assumption Type | Example |
|-----------------|---------|
| Technical | "We can build this in X months" |
| Operational | "We can deliver at this quality" |
| Resource | "We can hire the needed talent" |
| Partnership | "Partner will agree to terms" |

### Usability Assumptions

| Assumption Type | Example |
|-----------------|---------|
| Learnability | "Users can complete onboarding" |
| Efficiency | "Users can accomplish task in X minutes" |
| Adoption | "X% will use feature regularly" |

## Testing Methods

### Low-Fidelity Tests

| Method | Best For | Cost/Time |
|--------|----------|-----------|
| Interviews | Desirability, understanding | Low |
| Surveys | Validation at scale | Low |
| Landing pages | Demand signals | Low |
| Paper prototypes | Usability concepts | Low |

### Medium-Fidelity Tests

| Method | Best For | Cost/Time |
|--------|----------|-----------|
| Concierge MVP | Service feasibility | Medium |
| Wizard of Oz | Product feasibility | Medium |
| Pre-sales | Willingness to pay | Medium |
| Prototypes | Usability | Medium |

### High-Fidelity Tests

| Method | Best For | Cost/Time |
|--------|----------|-----------|
| Pilot programs | Full validation | High |
| Beta programs | Product-market fit | High |
| A/B tests | Optimization | High |

## Experiment Card Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ EXPERIMENT CARD                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ASSUMPTION                                                                   │
│ We believe: [Statement of belief]                                            │
│ Category: □ Desirability  □ Viability  □ Feasibility  □ Usability           │
│ Importance: _/10    Evidence: _/10    Risk Score: _                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ HYPOTHESIS                                                                   │
│ If we [action], then [outcome], because [reason]                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ EXPERIMENT                                                                   │
│ Method: [How we'll test]                                                     │
│ Metric: [What we'll measure]                                                 │
│ Success threshold: [What number = success]                                   │
│ Fail threshold: [What number = failure]                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ LOGISTICS                                                                    │
│ Duration: [Timeframe]                                                        │
│ Sample size: [How many]                                                      │
│ Resources needed: [What's required]                                          │
│ Owner: [Who's responsible]                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ RESULTS                                                                      │
│ Outcome: [What happened]                                                     │
│ Metric achieved: [Actual number]                                             │
│ Learning: [What we learned]                                                  │
│ Decision: □ Validated  □ Invalidated  □ More testing needed                 │
│ Next step: [What to do now]                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Testing easy ones first | Wasted time | Prioritize by risk |
| Confirmation bias | False validation | Design rigorous tests |
| Weak tests | Inconclusive | Clear success criteria |
| Not acting on results | Wasted learning | Commit to decisions |
| One-time exercise | Stale assumptions | Revisit regularly |

## Sources

- Lean Startup methodology (Eric Ries)
- Assumption Mapping (David Bland)
- Experiment-driven development practices
