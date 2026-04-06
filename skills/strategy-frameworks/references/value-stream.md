# Value Stream Map Reference

Detailed methodology for value stream mapping.

## Overview

A Value Stream Map (VSM) visualizes the flow of materials and information required to deliver a product or service to customers. Originally from lean manufacturing, it identifies waste and improvement opportunities in any process.

## Core Concepts

### Value Stream
The complete set of activities from trigger to delivery that create value for the customer.

### Value-Add vs. Non-Value-Add

| Type | Definition | Examples |
|------|------------|----------|
| **Value-Add (VA)** | Customer would pay for it | Assembly, processing, testing |
| **Non-Value-Add (NVA)** | Waste, no customer value | Waiting, rework, overprocessing |
| **Necessary NVA** | Required but no value | Compliance, approvals |

## The Eight Wastes (DOWNTIME)

| Waste | Description | Signs |
|-------|-------------|-------|
| **D**efects | Errors requiring rework | Quality issues, returns |
| **O**verproduction | Making more than needed | Inventory buildup |
| **W**aiting | Idle time between steps | Queues, delays |
| **N**on-utilized talent | Underusing people | Boredom, low engagement |
| **T**ransportation | Moving materials/info | Handoffs, email chains |
| **I**nventory | Excess WIP or stock | Backlogs, piles |
| **M**otion | Unnecessary movement | Context switching |
| **E**xtra processing | More work than needed | Gold plating, unused features |

## VSM Symbols

### Process Symbols

```
┌─────────┐
│ Process │  Process step
│  Step   │
└─────────┘

    ▼        Material flow
   ───→

   - - →     Information flow (electronic)

   ~~~→      Information flow (manual)

   △         Inventory / queue
  ▲▲▲
```

### Data Box

```
┌─────────────────┐
│ C/T = 5 min     │  Cycle Time
│ C/O = 30 min    │  Changeover Time
│ Uptime = 90%    │  Availability
│ Batch = 100     │  Batch Size
└─────────────────┘
```

### Timeline

```
VA Time:    ═══════════════════════
NVA Time:   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
            │←─────────────── Total Lead Time ──────────────→│
```

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ VALUE STREAM MAP: [Process Name]                                             │
│ Current State / Future State: [Circle one]         Date: [Date]             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Customer]                                              [Supplier]          │
│      │                                                       │               │
│      ▼                                                       ▼               │
│  ┌───────┐    △    ┌───────┐    △    ┌───────┐    △    ┌───────┐           │
│  │ Step  │   ###   │ Step  │   ###   │ Step  │   ###   │ Step  │           │
│  │   1   │─────────│   2   │─────────│   3   │─────────│   4   │           │
│  └───────┘         └───────┘         └───────┘         └───────┘           │
│  C/T: __          C/T: __           C/T: __           C/T: __              │
│  C/O: __          C/O: __           C/O: __           C/O: __              │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIMELINE                                                                     │
│ VA:    ═══     ════     ══════     ═══                                      │
│ NVA:   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                │
│                                                                              │
│ Total Lead Time: ___                                                         │
│ Total VA Time: ___                                                           │
│ VA Ratio: ___% (VA Time ÷ Lead Time)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ IMPROVEMENT OPPORTUNITIES                                                    │
│ 1. [Kaizen burst location] - [Improvement idea]                             │
│ 2. [Kaizen burst location] - [Improvement idea]                             │
│ 3. [Kaizen burst location] - [Improvement idea]                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| Lead Time | Start to finish | Total time in system |
| Cycle Time | Time per unit | Process speed |
| Takt Time | Available time ÷ Demand | Required pace |
| VA Ratio | VA Time ÷ Lead Time | Process efficiency |
| First Pass Yield | Good units ÷ Total units | Quality measure |

## VSM Process

### 1. Define Scope
- Select product family or service
- Define start and end points
- Identify the customer

### 2. Map Current State
- Walk the actual process
- Collect real data (don't estimate)
- Record all steps and queues
- Note information flows

### 3. Identify Waste
- Mark wastes on the map
- Calculate VA ratio
- Find bottlenecks
- Note pain points

### 4. Design Future State
- Eliminate/reduce waste
- Create continuous flow
- Implement pull where possible
- Balance to takt time

### 5. Create Implementation Plan
- Prioritize improvements
- Assign owners
- Set target metrics
- Schedule kaizen events

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Mapping the ideal | Miss real waste | Map what actually happens |
| Estimating data | Inaccurate baseline | Collect real data |
| Too much scope | Overwhelming | Start with one value stream |
| No future state | Analysis without action | Always design target |
| One-time event | No continuous improvement | Regular VSM reviews |

## Software/Knowledge Work Adaptations

| Manufacturing | Knowledge Work Equivalent |
|---------------|---------------------------|
| Inventory | Work in progress (tickets, stories) |
| Batch size | Release size |
| Changeover | Context switching |
| Transport | Handoffs between teams |
| Motion | Tool switching, meetings |

## Sources

- Rother, M. & Shook, J. (1999). Learning to See. Lean Enterprise Institute.
- Toyota Production System
- Lean management practices
