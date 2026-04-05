---
name: dbt
description: Use when building dbt models, adding tests, or designing data models. Covers dimensional modeling, model organization (staging/intermediate/marts), testing patterns, and warehouse-specific configurations.
---

# dbt

Patterns for dbt data transformation projects.

## Skill Modules

This skill is organized into the following modules. Read the relevant module(s) based on the task:

| Module | File | Use When |
|--------|------|----------|
| **Data Modeling** | `references/data-modeling.md` | Designing dimensional models, defining grain, facts vs dimensions, SCDs |
| **Model Layers** | `references/model-layers.md` | Organizing staging/intermediate/marts, naming conventions, project structure |
| **Package Testing** | `references/testing-packages.md` | Integration tests for dbt package development |

## Quick Reference

### Commands

```bash
dbt run                          # Run all models
dbt run --select +model_name     # Model + upstream
dbt run --select model_name+     # Model + downstream
dbt run --select tag:daily       # Models with tag
dbt test                         # Run all tests
dbt test --select "test_type:unit"      # Unit tests only
dbt test --select "test_type:data"      # Data tests only
dbt build                        # Run + test in DAG order
dbt build --select state:modified+      # Modified + downstream (CI)
dbt docs generate                # Generate documentation
dbt source freshness             # Check source freshness
```

### Naming Conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Staging | `stg__<source>__<table>` | `stg__stripe__customers` |
| Intermediate | `int_<entity>__<transform>` | `int_customers__enriched` |
| Fact | `fct_<event>` | `fct_orders` |
| Dimension | `dim_<entity>` | `dim_customers` |

### Column Naming

| Type | Convention | Examples |
|------|------------|----------|
| IDs | `<entity>_id` | `customer_id`, `order_id` |
| Timestamps | `<event>_at` | `created_at`, `updated_at`, `shipped_at` |
| Dates | `<event>_date` | `order_date`, `birth_date` |
| Booleans | `is_<state>` or `has_<thing>` | `is_active`, `has_subscription` |
| Amounts | `<name>_<unit>` | `amount_usd`, `quantity_units` |
| Counts | `<thing>_count` | `order_count`, `item_count` |

### Testing Pyramid

```
          Integration Tests  ← Package development only
              Unit Tests     ← Complex transformation logic
           Singular Tests    ← Business rules
           Generic Tests     ← Keys, constraints, patterns
         Source Freshness    ← Pipeline health
             Contracts       ← Schema enforcement
```

### What to Test (Quick Guide)

| Always | Sometimes | Rarely |
|--------|-----------|--------|
| Primary keys (unique + not_null) | Optional FKs | Every column not_null |
| Required foreign keys | Numeric ranges | Columns in contracts |
| Business-critical derived fields | String patterns | Staging columns |
| Status/enum columns | Row count bounds | Intermediate models |

## Best Practices Summary

### Things to do

- DO Define grain for every model (what does one row represent?)
- DO Use staging for renaming/casting only—no business logic
- DO Test primary keys on every model (unique + not_null)
- DO Use contracts for marts (enforce schema at build time)
- DO Add tests when you find bugs (regression prevention)
- DO Document models and columns in YAML
- DO Use incremental models for large tables
- DO Tag critical tests and run them more frequently

### Don't

- DON'T Skip the staging layer
- DON'T Put business logic in staging models
- DON'T Hardcode values (use `{{ var() }}` or `{{ env_var() }}`)
- DON'T Test every column (diminishing returns)
- DON'T Ignore test warnings indefinitely
- DON'T Forget source freshness checks
- DON'T Create circular dependencies between models
