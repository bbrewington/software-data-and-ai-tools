# Generic Tests

Reusable data quality tests that can be applied to any model or column.

## Built-in Tests

dbt includes four generic tests out of the box:

### Primary Keys

```yaml
columns:
  - name: order_id
    description: Primary key
    tests:
      - unique
      - not_null
```

### Foreign Keys

```yaml
columns:
  - name: customer_id
    description: FK to dim_customers
    tests:
      - not_null
      - relationships:
          to: ref('dim_customers')
          field: customer_id
```

### Accepted Values

```yaml
columns:
  - name: status
    tests:
      - accepted_values:
          values: ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
```

### Not Null

```yaml
columns:
  - name: email
    tests:
      - not_null
```

## dbt-utils Tests

The [dbt-utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/) package provides additional generic tests.

### Installation

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
```

```bash
dbt deps
```

### Table-Level Tests

```yaml
models:
  - name: fct_orders
    tests:
      # Table has recent data
      - dbt_utils.recency:
          datepart: day
          field: created_at
          interval: 1

      # Table is not empty
      - dbt_utils.at_least_one

      # Composite uniqueness
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - order_id
            - line_item_id

      # Row count matches another table
      - dbt_utils.equal_rowcount:
          compare_model: ref('stg__orders')

      # Specific expression is true for all rows
      - dbt_utils.expression_is_true:
          expression: "total_amount = subtotal + tax + shipping - discount"
```

### Column-Level Tests

```yaml
columns:
  - name: total_amount
    tests:
      # Expression evaluates to true
      - dbt_utils.expression_is_true:
          expression: ">= 0"

  - name: end_date
    tests:
      # Compare to another column
      - dbt_utils.expression_is_true:
          expression: ">= start_date"

  - name: email
    tests:
      # Not an empty string
      - dbt_utils.not_empty_string

  - name: status
    tests:
      # At least one row has each value
      - dbt_utils.at_least_one

  - name: customer_id
    tests:
      # Cardinality check
      - dbt_utils.cardinality_equality:
          field: customer_id
          to: ref('dim_customers')
```

### Mutually Exclusive Ranges

Useful for SCD Type 2 dimensions:

```yaml
models:
  - name: dim_customers_history
    tests:
      - dbt_utils.mutually_exclusive_ranges:
          lower_bound_column: valid_from
          upper_bound_column: valid_to
          partition_by: customer_id
          gaps: not_allowed  # or 'allowed', 'required'
```

## dbt-expectations Tests

The [dbt-expectations](https://hub.getdbt.com/calogica/dbt_expectations/latest/) package provides richer validation inspired by Great Expectations.

### Installation

```yaml
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
```

### Table Shape Tests

```yaml
models:
  - name: fct_orders
    tests:
      # Row count within expected range
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 10000000

      # Row count matches another table (with tolerance)
      - dbt_expectations.expect_table_row_count_to_equal_other_table:
          compare_model: ref('fct_orders_previous')
          tolerance_percent: 10

      # Column count
      - dbt_expectations.expect_table_column_count_to_equal:
          value: 15

      # Required columns exist
      - dbt_expectations.expect_table_columns_to_contain_set:
          column_list: ['order_id', 'customer_id', 'total_amount', 'created_at']
```

### Value Range Tests

```yaml
columns:
  - name: total_amount
    tests:
      # Value range with outlier tolerance
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: 0
          max_value: 100000
          mostly: 0.99  # Allow 1% outliers

  - name: quantity
    tests:
      # Integer range
      - dbt_expectations.expect_column_values_to_be_between:
          min_value: 1
          max_value: 1000
          strictly: false  # >= and <= (not > and <)

  - name: created_at
    tests:
      # No future dates
      - dbt_expectations.expect_column_values_to_be_between:
          max_value: "current_date"
```

### String Pattern Tests

```yaml
columns:
  - name: email
    tests:
      # Regex validation
      - dbt_expectations.expect_column_values_to_match_regex:
          regex: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

  - name: phone_number
    tests:
      # Length validation
      - dbt_expectations.expect_column_value_lengths_to_be_between:
          min_value: 10
          max_value: 15

  - name: postal_code
    tests:
      # Exact length
      - dbt_expectations.expect_column_value_lengths_to_equal:
          value: 5

  - name: country_code
    tests:
      # Match regex pattern
      - dbt_expectations.expect_column_values_to_match_regex:
          regex: "^[A-Z]{2}$"
```

### Null Handling Tests

```yaml
columns:
  - name: country_code
    tests:
      # Completeness threshold (95% non-null)
      - dbt_expectations.expect_column_values_to_not_be_null:
          mostly: 0.95

  - name: optional_field
    tests:
      # At least some values exist
      - dbt_expectations.expect_column_values_to_not_be_null:
          mostly: 0.01  # At least 1% populated
```

### Distribution Tests

```yaml
columns:
  - name: status
    tests:
      # Value distribution
      - dbt_expectations.expect_column_distinct_count_to_be_between:
          min_value: 3
          max_value: 10

      # Specific values present
      - dbt_expectations.expect_column_distinct_values_to_contain_set:
          value_set: ['pending', 'completed', 'cancelled']

  - name: amount
    tests:
      # Statistical bounds
      - dbt_expectations.expect_column_mean_to_be_between:
          min_value: 50
          max_value: 500

      - dbt_expectations.expect_column_stdev_to_be_between:
          min_value: 10
          max_value: 100
```

### Aggregate Tests

```yaml
models:
  - name: fct_orders
    tests:
      # Sum of column
      - dbt_expectations.expect_column_sum_to_be_between:
          column_name: total_amount
          min_value: 1000000
          max_value: 100000000

      # Percentage of rows matching condition
      - dbt_expectations.expect_column_proportion_of_unique_values_to_be_between:
          column_name: customer_id
          min_value: 0.5
          max_value: 1.0
```

## Custom Generic Tests

When built-in and package tests don't fit your needs, create custom generic tests.

### Not Null Proportion

Test that a column meets a minimum completeness threshold:

```sql
-- tests/generic/test_not_null_proportion.sql
{% test not_null_proportion(model, column_name, at_least=0.95) %}

with validation as (
    select
        count(*) as total_rows,
        count({{ column_name }}) as non_null_rows
    from {{ model }}
)

select *
from validation
where total_rows > 0
  and (non_null_rows * 1.0 / total_rows) < {{ at_least }}

{% endtest %}
```

Usage:

```yaml
columns:
  - name: phone_number
    tests:
      - not_null_proportion:
          at_least: 0.90  # 90% should have phone
```

### Row Count Delta

Fail if row count changes by more than a threshold:

```sql
-- tests/generic/test_row_count_delta.sql
{% test row_count_delta(model, compare_model, max_delta_percent=10) %}

with current_count as (
    select count(*) as cnt from {{ model }}
),

previous_count as (
    select count(*) as cnt from {{ compare_model }}
)

select
    current_count.cnt as current_rows,
    previous_count.cnt as previous_rows,
    abs(current_count.cnt - previous_count.cnt) * 100.0 
        / nullif(previous_count.cnt, 0) as delta_percent
from current_count
cross join previous_count
where previous_count.cnt > 0
  and abs(current_count.cnt - previous_count.cnt) * 100.0 
      / previous_count.cnt > {{ max_delta_percent }}

{% endtest %}
```

Usage:

```yaml
models:
  - name: fct_orders
    tests:
      - row_count_delta:
          compare_model: ref('fct_orders_snapshot')
          max_delta_percent: 5
```

### Values Match Pattern

Validate string patterns with a tolerance:

```sql
-- tests/generic/test_values_match_pattern.sql
{% test values_match_pattern(model, column_name, pattern, mostly=1.0) %}

with validation as (
    select
        count(*) as total_rows,
        sum(case when regexp_contains({{ column_name }}, r'{{ pattern }}') then 1 else 0 end) as matching_rows
    from {{ model }}
    where {{ column_name }} is not null
)

select *
from validation
where total_rows > 0
  and (matching_rows * 1.0 / total_rows) < {{ mostly }}

{% endtest %}
```

Usage:

```yaml
columns:
  - name: sku
    tests:
      - values_match_pattern:
          pattern: "^[A-Z]{3}-[0-9]{6}$"
          mostly: 0.99
```

### Sequential IDs

Verify IDs are sequential with no gaps:

```sql
-- tests/generic/test_sequential_ids.sql
{% test sequential_ids(model, column_name, allow_gaps=false) %}

with id_stats as (
    select
        min({{ column_name }}) as min_id,
        max({{ column_name }}) as max_id,
        count(*) as row_count,
        count(distinct {{ column_name }}) as distinct_count
    from {{ model }}
)

select *
from id_stats
where distinct_count != row_count  -- duplicates exist
{% if not allow_gaps %}
   or (max_id - min_id + 1) != row_count  -- gaps exist
{% endif %}

{% endtest %}
```

### Column Pair Consistency

Verify two columns are consistent (e.g., city matches state):

```sql
-- tests/generic/test_column_pair_valid.sql
{% test column_pair_valid(model, column_a, column_b, valid_pairs_model) %}

with data as (
    select distinct
        {{ column_a }} as col_a,
        {{ column_b }} as col_b
    from {{ model }}
    where {{ column_a }} is not null
      and {{ column_b }} is not null
),

valid_pairs as (
    select * from {{ valid_pairs_model }}
)

select data.*
from data
left join valid_pairs
    on data.col_a = valid_pairs.{{ column_a }}
   and data.col_b = valid_pairs.{{ column_b }}
where valid_pairs.{{ column_a }} is null

{% endtest %}
```

Usage:

```yaml
models:
  - name: dim_locations
    tests:
      - column_pair_valid:
          column_a: city
          column_b: state
          valid_pairs_model: ref('seed_valid_city_state')
```

## Complete Example

```yaml
# models/marts/core/_core__models.yml
version: 2

models:
  - name: fct_orders
    description: Order fact table
    tests:
      # Table-level tests
      - dbt_utils.recency:
          datepart: hour
          field: created_at
          interval: 6
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 10000

    columns:
      - name: order_id
        tests:
          - unique
          - not_null

      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

      - name: total_amount
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 50000
              mostly: 0.999

      - name: email
        tests:
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
              config:
                where: "email is not null"

      - name: created_at
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              max_value: "current_timestamp()"
```
