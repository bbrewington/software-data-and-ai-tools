# Wardley Map Reference

Detailed methodology for strategic positioning using Wardley Maps.

## Overview

A Wardley Map is a visual representation of the components needed to serve a user need, showing both their visibility to users (value chain) and their evolutionary stage. Created by Simon Wardley, it enables strategic analysis of competitive positioning, build/buy decisions, and future evolution.

## Map Structure

### Axes

| Axis | Description | Range |
|------|-------------|-------|
| **Y-axis (Value Chain)** | Visibility to user | Top (visible) → Bottom (invisible) |
| **X-axis (Evolution)** | Component maturity | Left (novel) → Right (commodity) |

### Visual Layout

```
                    EVOLUTION →
    Genesis   Custom-Built   Product   Commodity
       │           │           │           │
Visible│           │           │           │
   ↑   │    ○──────┼───────────┼──────○    │
   │   │    │      │           │           │
   │   │    │      │     ○     │           │
Value  │    │      ○     │     │           │
Chain  │    │             │    │           │
   │   │    │             ○────┼───────○   │
   │   │    │                  │       │   │
   ↓   │    │                  │       │   │
Invisible           ○──────────┼───────┼───○
       │           │           │           │
```

## Evolution Stages

| Stage | Characteristics | Competition | Focus |
|-------|-----------------|-------------|-------|
| **Genesis** | Novel, poorly understood, constantly changing | Ideas | Exploration |
| **Custom-Built** | Emerging, learning, divergent approaches | Features | Differentiation |
| **Product** | More defined, competition on features | Market share | Scale |
| **Commodity** | Standardized, volume operations | Price | Efficiency |

### Evolution Indicators

| Aspect | Genesis | Custom | Product | Commodity |
|--------|---------|--------|---------|-----------|
| Certainty | Low | Emerging | Converging | High |
| Failure rate | High | Moderate | Low | Very low |
| Market | Undefined | Growing | Mature | Saturated |
| Change | Rapid | Moderate | Slow | Very slow |

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ WARDLEY MAP: [Value Chain Name]                                              │
│ User Need: [What need are we serving?]                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ VISIBLE   │ Genesis    Custom-Built    Product    Commodity                 │
│           │                                                                  │
│   [User Need]                                                                │
│       │                                                                      │
│       ○ [Component A]                                                        │
│       │                                                                      │
│       ├──○ [Component B]                                                    │
│       │      │                                                               │
│       │      └──○ [Component C]                                             │
│       │              │                                                       │
│       └──────────────┴──○ [Component D]                                     │
│                              │                                               │
│                              └──────────────────○ [Component E]             │
│                                                                              │
│ INVISIBLE │                                                                  │
│           ├──────────────┼──────────────┼──────────────┼──────────────│     │
│           Genesis    Custom-Built    Product    Commodity                    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ KEY INSIGHTS                                                                 │
│ 1. [Component X] is evolving toward [Stage] - Implication: [What it means] │
│ 2. [Gap/Opportunity identified]                                              │
│ 3. [Strategic move to consider]                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ STRATEGIC PLAYS                                                              │
│ Build: [Components to develop in-house]                                      │
│ Buy: [Components to source externally]                                       │
│ Outsource: [Components to commoditize]                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Building a Wardley Map

### Step 1: Identify the User Need
What need are you serving? Start from the user's perspective.

### Step 2: Map the Value Chain
List all components needed to serve that need, from visible to invisible.

### Step 3: Position on Evolution
For each component, determine its evolutionary stage based on characteristics.

### Step 4: Draw Dependencies
Connect components that depend on each other.

### Step 5: Analyze and Strategize
Look for patterns, movement, and opportunities.

## Strategic Patterns

### Common Patterns to Spot

| Pattern | Description | Strategic Response |
|---------|-------------|-------------------|
| **Inertia** | Resistance to evolution | Plan for disruption |
| **Co-evolution** | Practices evolve with components | Watch for enablers |
| **Componentization** | Products becoming platforms | Consider ecosystem |
| **Industrialization** | Custom → Product → Commodity | Decide build vs. buy |

### Gameplay Moves

| Move | Description | When to Use |
|------|-------------|-------------|
| **Open source** | Commoditize to gain advantage | When component benefits from standardization |
| **Ecosystem** | Build platform, enable others | When you control key component |
| **Tower** | Build unique capability on commodity | When differentiation matters |
| **Land grab** | Move fast on evolving component | When timing is critical |

## Build vs. Buy Analysis

| Component Stage | Recommendation | Reasoning |
|-----------------|----------------|-----------|
| Genesis | Build/Partner | Need control, no market |
| Custom-Built | Build/Customize | Differentiation |
| Product | Buy/License | Faster, established |
| Commodity | Outsource/Utility | Cost efficiency |

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Wrong anchor | Map makes no sense | Start from real user need |
| Static view | Miss evolution | Update maps regularly |
| Too detailed | Overwhelming | Focus on key components |
| No action | Analysis paralysis | Derive specific moves |
| Solo mapping | Bias | Map with diverse team |

## Wardley Map vs. Other Tools

| Tool | Wardley Map Adds |
|------|------------------|
| Value Chain (Porter) | Evolution dimension |
| SWOT | Component-level analysis |
| BCG Matrix | Value chain context |
| Business Model Canvas | Strategic positioning |

## Reading a Wardley Map

### Questions to Ask

1. Where is evolution happening?
2. What are the dependencies?
3. Where do we have inertia?
4. What can be commoditized?
5. Where is our differentiation?
6. What's moving into commodity that we still build?

## Sources

- Wardley, S. (2017). Wardley Maps. CC BY-SA 4.0.
- Simon Wardley's blog and research
- Strategic mapping practices
