# MoSCoW Prioritization Reference

Detailed methodology for MoSCoW prioritization.

## Overview

MoSCoW is a prioritization technique that categorizes requirements into four buckets: Must have, Should have, Could have, and Won't have. Originally developed for DSDM (Dynamic Systems Development Method), it's widely used in agile and project management.

## The Four Categories

| Category | Meaning | Description |
|----------|---------|-------------|
| **Must have** | Non-negotiable | Critical for success; without these, the release/project fails |
| **Should have** | Important | Significant value; painful to exclude but workarounds exist |
| **Could have** | Nice to have | Desirable but not necessary; include if resources allow |
| **Won't have** | Not this time | Explicitly excluded from this scope; may be future consideration |

## Category Details

### Must Have (Mo)

- Minimum viable release
- Legal/compliance requirements
- Core functionality that defines the product
- Without it, the solution doesn't work
- No workaround possible

**Test**: If we don't have this, should we launch at all?

### Should Have (S)

- High-value features
- Important but not critical
- Workarounds exist (manual, temporary)
- Painful to exclude
- Should be planned for

**Test**: Can we work around not having this?

### Could Have (Co)

- Enhancements and improvements
- Nice-to-haves
- Small improvements to experience
- Lower priority than Should
- First to cut if needed

**Test**: Would users notice or care much if this was missing?

### Won't Have (W)

- Explicitly out of scope
- Agreed not to include
- May be future consideration
- Prevents scope creep
- Creates clarity

**Test**: Is this clearly agreed as not in scope?

## Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MoSCoW: [Project/Release]                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ MUST HAVE (Critical for success)                                             │
│ □ [Requirement 1] - Rationale: [Why critical]                               │
│ □ [Requirement 2] - Rationale: [Why critical]                               │
│ □ [Requirement 3] - Rationale: [Why critical]                               │
│                                                                              │
│ Estimated effort: ___% of total capacity                                     │
│ Target: <60% of capacity in Must Have                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ SHOULD HAVE (Important, workarounds exist)                                   │
│ □ [Requirement 1] - Workaround: [What's the alternative]                    │
│ □ [Requirement 2] - Workaround: [What's the alternative]                    │
│                                                                              │
│ Estimated effort: ___% of total capacity                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ COULD HAVE (Desirable, not necessary)                                        │
│ □ [Requirement 1]                                                            │
│ □ [Requirement 2]                                                            │
│                                                                              │
│ Estimated effort: ___% of total capacity                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ WON'T HAVE (Explicitly excluded this time)                                   │
│ ✕ [Requirement 1] - Future: [When might this be considered]                 │
│ ✕ [Requirement 2] - Future: [When might this be considered]                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Allocation Guidelines

### Recommended Distribution

| Category | % of Total Effort |
|----------|-------------------|
| Must Have | ≤60% |
| Should Have | ~20% |
| Could Have | ~20% |
| Won't Have | 0% (excluded) |

### Why 60% Max for Must Have?

- Buffer for estimation errors
- Time for unexpected issues
- Allows inclusion of Should Have items
- Reduces risk of failure

## Decision Matrix

| Question | If Yes → | If No → |
|----------|----------|---------|
| Is it illegal/unsafe without this? | Must | Not Must |
| Does core use case work without it? | Not Must | Must |
| Is there a reasonable workaround? | Not Must | Must |
| Would most users notice/care? | Must/Should | Could |
| Has stakeholder agreed to exclude? | Won't | Discuss |

## Facilitation Tips

### Running a MoSCoW Session

1. **Prepare**: List all requirements/features
2. **Educate**: Explain the categories clearly
3. **Individual vote**: Each person categorizes
4. **Discuss**: Review disagreements
5. **Converge**: Agree as a team
6. **Validate**: Check effort distribution

### Handling Disagreements

| Approach | When to Use |
|----------|-------------|
| Defer to product owner | Clear ownership |
| Vote | Democratic decision |
| Time-box debate | Prevent endless discussion |
| Use criteria | Objective assessment |
| Split the item | Partial Must, rest Could |

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Everything is Must | No prioritization | Force 60% limit |
| Empty Won't Have | No scope clarity | Explicitly exclude items |
| No rationale | Can't revisit decisions | Document reasoning |
| Stakeholder override | Political Must Haves | Stand firm on criteria |
| Ignoring effort | Infeasible plans | Balance priority with capacity |

## MoSCoW vs. Other Methods

| Method | Best For |
|--------|----------|
| MoSCoW | Scope negotiation, time-boxed projects |
| RICE | Numeric comparison, feature prioritization |
| ICE | Quick experiment prioritization |
| Kano | Understanding customer satisfaction |

## Sources

- Clegg, D. & Barker, R. (1994). Case Method Fast-Track: A RAD Approach. Addison-Wesley.
- DSDM (Dynamic Systems Development Method)
- Agile project management practices
