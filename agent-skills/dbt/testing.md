# Testing

Data quality validation patterns for dbt.

## Data Quality Dimensions

| Dimension | Description | dbt Approach |
|-----------|-------------|--------------|
| **Completeness** | No missing values | `not_null` test or contract constraint |
| **Uniqueness** | No duplicates | `unique` test |
| **Validity** | Values in expected range | `accepted_values`, dbt-expectations |
| **Referential** | FK exists in parent | `relationships` test |
| **Freshness** | Data is recent | Source freshness, `dbt_utils.recency` |
| **Consistency** | No contradictions | `dbt_utils.expression_is_true`, singular tests |
| **Accuracy** | Logic produces correct results | Unit tests |

## Testing Pyramid

dbt offers multiple layers of validation, each serving a different purpose:

```
                        /\
                       /  \         Integration Tests
                      /    \        (package development: end-to-end validation)
                     /──────\
                    /        \      Unit Tests
                   /          \     (transformation logic with mocked inputs)
                  /────────────\
                 /              \   Singular Tests
                /                \  (complex business rules, cross-model checks)
               /──────────────────\
              /                    \ Generic Tests (Data Tests)
             /                      \(reusable: unique, not_null, relationships)
            /────────────────────────\
           /                          \ Source Freshness
          /                            \(data pipeline health monitoring)
         /──────────────────────────────\
        /                                \ Contracts
       /                                  \(build-time schema enforcement)
      /────────────────────────────────────\
```

| Layer | When It Runs | What It Validates | Fails Build? |
|-------|--------------|-------------------|--------------|
| **Contracts** | `dbt run` (build time) | Column names, types, constraints | Yes |
| **Source Freshness** | `dbt source freshness` | Data pipeline recency | Configurable |
| **Generic Tests** | `dbt test` / `dbt build` | Data quality patterns | Yes (or warn) |
| **Singular Tests** | `dbt test` / `dbt build` | Custom business rules | Yes (or warn) |
| **Unit Tests** | `dbt test` / `dbt build` | Transformation logic | Yes |
| **Integration Tests** | CI pipeline (packages) | End-to-end package behavior | Yes |

**Volume guidance:**
- Contracts: All marts (enforced), staging optional
- Source freshness: All critical sources
- Generic tests: All keys, critical columns
- Singular tests: Complex business rules that don't fit generic patterns
- Unit tests: Complex transformations, edge cases
- Integration tests: Package development only

## Related Modules

| Module | File | Use When |
|--------|------|----------|
| **Generic Tests** | `testing-generic.md` | Built-in tests, dbt-utils, dbt-expectations, custom generic tests |
| **Unit Tests** | `testing-unit.md` | Testing transformation logic with mocked data (dbt 1.8+) |
| **Singular Tests** | `testing-singular.md` | Complex business rules, cross-model validation |
| **Package Testing** | `testing-packages.md` | Integration tests for dbt package development |

## Contracts vs Tests

dbt 1.5+ introduced contracts that enforce structure at build time. Understanding when to use each:

| Validation | Contract | Test | Notes |
|------------|----------|------|-------|
| Column exists | ✓ | | Contract fails build if column missing |
| Column type | ✓ | | Contract enforces exact type |
| Not null | ✓ | ✓ | Contract is stricter (build fails); test allows warnings |
| Primary key | ✓ | ✓ | Contract marks it; test validates uniqueness |
| Uniqueness | | ✓ | Can't enforce at build time |
| Foreign keys | | ✓ | Requires querying parent table |
| Value ranges | | ✓ | Requires evaluating data |
| Business rules | | ✓ | Requires custom logic |

**Recommendation:** Use contracts for structure (columns, types) and critical not-null constraints. Use tests for everything that requires inspecting actual data values.

```yaml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: string
        constraints:
          - type: not_null
          - type: primary_key  # Declares intent; test validates
        tests:
          - unique  # Actually checks the data

      - name: total_amount
        data_type: float64
        constraints:
          - type: not_null
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

## Source Freshness

```yaml
# models/staging/stripe/_stripe__sources.yml
version: 2

sources:
  - name: stripe
    description: Stripe payment data via Fivetran
    
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _fivetran_synced
    
    tables:
      - name: orders
        freshness:
          # Override: orders should be very fresh
          warn_after: {count: 1, period: hour}
          error_after: {count: 6, period: hour}

      - name: customers
        # Inherits default freshness

      - name: products
        freshness: null  # Disable: products update infrequently
```

```bash
# Check freshness
dbt source freshness

# Check specific source
dbt source freshness --select source:stripe
```

## Test Configuration

### Severity Levels

```yaml
columns:
  - name: customer_id
    tests:
      - unique:
          severity: error  # Fail the run (default)
      - not_null:
          severity: warn   # Warning only, run continues
```

### Store Failures for Debugging

```yaml
columns:
  - name: order_id
    tests:
      - unique:
          config:
            store_failures: true  # Save failing rows to schema
            limit: 100            # Cap stored failures
```

Failed rows go to `<target_schema>_dbt_test__audit.unique_fct_orders_order_id`.

### Scoped Tests (Test Recent Data Only)

```yaml
columns:
  - name: order_id
    tests:
      - unique:
          config:
            where: "created_at >= current_date - interval '7 days'"
```

### Test Metadata

```yaml
columns:
  - name: total_amount
    tests:
      - dbt_utils.expression_is_true:
          expression: ">= 0"
          config:
            tags: ['finance', 'critical']
            meta:
              owner: 'data-team'
              sla: 'p1'
```

## Running Tests

### Basic Commands

```bash
# All tests
dbt test

# Specific model's tests
dbt test --select fct_orders

# Model and all upstream tests
dbt test --select +fct_orders

# Model and all downstream tests
dbt test --select fct_orders+

# Only data tests (generic + singular)
dbt test --select "test_type:data"

# Only unit tests
dbt test --select "test_type:unit"

# Tests by tag
dbt test --select "tag:critical"

# Build and test together
dbt build

# Build with test failures stored
dbt build --store-failures
```

### CI/CD Commands

```bash
# Fail on warnings (for CI)
dbt test --warn-error

# Test only modified models and downstream
dbt test --select state:modified+

# Test with limited concurrency (reduce warehouse load)
dbt test --threads 4
```

## Test Strategy by Environment

| Environment | What to Test | How |
|-------------|--------------|-----|
| **Development** | Models you're actively changing | `dbt test --select <model>` |
| **CI (Pull Request)** | Modified models + downstream | `dbt test --select state:modified+` |
| **Production (each run)** | Critical tests only | `dbt test --select tag:critical` |
| **Production (scheduled)** | Full test suite | `dbt test` on a schedule |

### CI Configuration Example

```yaml
# .github/workflows/dbt_ci.yml
- name: Run dbt tests
  run: |
    dbt test \
      --select state:modified+ \
      --warn-error \
      --store-failures \
      --target ci
```

## Testing Incremental Models

Incremental models need special consideration:

```yaml
models:
  - name: fct_orders
    tests:
      # This tests the FULL table, not just the increment
      - unique:
          column_name: order_id

      # Add a test that specifically validates the incremental logic
      - dbt_utils.recency:
          datepart: hour
          field: created_at
          interval: 6
```

For thorough incremental testing:

```bash
# Test incremental logic by comparing full refresh
dbt run --select fct_orders --full-refresh
dbt test --select fct_orders

# Then test incremental
dbt run --select fct_orders
dbt test --select fct_orders
```

## Quick Reference: What to Test

| Always Test | Sometimes Test | Rarely Test |
|-------------|----------------|-------------|
| Primary keys (unique + not_null) | Optional foreign keys | Every column for not_null |
| Required foreign keys | Numeric ranges | Obvious type constraints |
| Business-critical derived fields | String patterns | Columns covered by contracts |
| Status/enum columns | Row count bounds | Staging layer columns |
| Temporal consistency | Data freshness | Intermediate models |

## Best Practices

**Do:**
- Test primary keys on every model (unique + not_null)
- Use contracts for structure, tests for data validation
- Add tests when you find bugs (regression prevention)
- Use `store_failures` for debugging in production
- Tag critical tests and run them more frequently
- Write unit tests for complex transformation logic

**Don't:**
- Test every column for not_null (diminishing returns)
- Ignore warnings indefinitely (fix or convert to errors)
- Skip source freshness checks
- Hardcode thresholds without understanding the data
- Rely solely on generic tests for complex business rules
