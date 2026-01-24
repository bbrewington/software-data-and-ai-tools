# Singular Tests

Singular tests are custom SQL queries that validate specific business rules. Use them when generic tests don't fit your validation needs.

## When to Use Singular Tests

| Scenario | Use Singular Test? | Alternative |
|----------|-------------------|-------------|
| Complex multi-column validation | Yes | — |
| Cross-model consistency check | Yes | `relationships` (if simple FK) |
| Business rule with exceptions | Yes | — |
| Aggregate validation (daily totals) | Yes | — |
| Temporal consistency | Yes | — |
| Simple column validation | No | Generic test |
| Pattern matching | No | `dbt_expectations` |

**Rule of thumb:** If you need to write custom SQL with joins, subqueries, or complex conditions, use a singular test.

## Basic Structure

Singular tests are SQL files that return failing rows. If the query returns any rows, the test fails.

```sql
-- tests/assert_order_amounts_positive.sql

-- Returns rows where the business rule is violated
select
    order_id,
    total_amount
from {{ ref('fct_orders') }}
where total_amount < 0
```

## File Organization

```
tests/
├── generic/                    # Custom generic tests (reusable)
│   ├── test_not_null_proportion.sql
│   └── test_row_count_delta.sql
├── staging/                    # Tests for staging models
│   └── assert_no_duplicate_source_ids.sql
├── marts/                      # Tests for mart models
│   ├── assert_order_dates_logical.sql
│   └── assert_customer_revenue_matches.sql
└── cross_model/                # Tests spanning multiple models
    └── assert_all_orders_have_customers.sql
```

Alternative: co-locate tests with models:

```
models/
└── marts/
    └── core/
        ├── fct_orders.sql
        ├── fct_orders.yml
        └── tests/
            └── assert_order_dates_logical.sql
```

## Common Patterns

### Temporal Consistency

Validate that dates follow logical order:

```sql
-- tests/assert_order_dates_logical.sql

select 
    order_id,
    ordered_at,
    shipped_at,
    delivered_at
from {{ ref('fct_orders') }}
where shipped_at < ordered_at           -- Can't ship before ordering
   or delivered_at < shipped_at         -- Can't deliver before shipping
   or delivered_at < ordered_at         -- Can't deliver before ordering
   or ordered_at > current_timestamp()  -- No future orders
```

### Referential Integrity (Complex)

When the `relationships` test isn't flexible enough:

```sql
-- tests/assert_active_orders_have_active_customers.sql

-- All non-cancelled orders should belong to active customers

with orders as (
    select distinct customer_id 
    from {{ ref('fct_orders') }}
    where status != 'cancelled'
      and created_at >= current_date - interval '90 days'
),

active_customers as (
    select customer_id 
    from {{ ref('dim_customers') }}
    where is_active = true
)

select orders.customer_id
from orders
left join active_customers using (customer_id)
where active_customers.customer_id is null
```

### Aggregate Consistency

Verify rollups match detail:

```sql
-- tests/assert_daily_revenue_matches_orders.sql

with order_totals as (
    select
        date_trunc('day', created_at) as revenue_date,
        sum(total_amount) as order_revenue
    from {{ ref('fct_orders') }}
    group by 1
),

daily_revenue as (
    select
        revenue_date,
        total_revenue
    from {{ ref('fct_daily_revenue') }}
)

select
    coalesce(o.revenue_date, d.revenue_date) as revenue_date,
    o.order_revenue,
    d.total_revenue,
    abs(coalesce(o.order_revenue, 0) - coalesce(d.total_revenue, 0)) as difference
from order_totals o
full outer join daily_revenue d using (revenue_date)
where abs(coalesce(o.order_revenue, 0) - coalesce(d.total_revenue, 0)) > 0.01
```

### Business Rule Validation

Enforce business logic that can't be expressed as constraints:

```sql
-- tests/assert_subscription_dates_valid.sql

-- Subscription end date must be after start date
-- Trial subscriptions must be <= 30 days
-- Annual subscriptions must be ~365 days

select
    subscription_id,
    subscription_type,
    started_at,
    ends_at,
    {{ datediff('started_at', 'ends_at', 'day') }} as duration_days
from {{ ref('fct_subscriptions') }}
where ends_at <= started_at  -- Invalid: end before start
   or (subscription_type = 'trial' and {{ datediff('started_at', 'ends_at', 'day') }} > 30)
   or (subscription_type = 'annual' and {{ datediff('started_at', 'ends_at', 'day') }} not between 360 and 370)
```

### Mutually Exclusive Categories

Ensure entities belong to exactly one category:

```sql
-- tests/assert_products_single_category.sql

select
    product_id,
    count(distinct category_id) as category_count
from {{ ref('bridge_product_categories') }}
group by product_id
having count(distinct category_id) != 1
```

### Anomaly Detection

Flag statistical outliers:

```sql
-- tests/assert_no_revenue_anomalies.sql

with daily_stats as (
    select
        date_trunc('day', created_at) as order_date,
        sum(total_amount) as daily_revenue
    from {{ ref('fct_orders') }}
    where created_at >= current_date - interval '30 days'
    group by 1
),

bounds as (
    select
        avg(daily_revenue) as mean_revenue,
        stddev(daily_revenue) as stddev_revenue
    from daily_stats
)

select
    ds.order_date,
    ds.daily_revenue,
    b.mean_revenue,
    b.stddev_revenue,
    (ds.daily_revenue - b.mean_revenue) / nullif(b.stddev_revenue, 0) as z_score
from daily_stats ds
cross join bounds b
where abs((ds.daily_revenue - b.mean_revenue) / nullif(b.stddev_revenue, 0)) > 3
```

### Data Completeness Over Time

Ensure no gaps in time series:

```sql
-- tests/assert_no_missing_daily_records.sql

with date_spine as (
    select date_day
    from {{ ref('dim_date') }}
    where date_day >= '2024-01-01'
      and date_day < current_date
),

actual_dates as (
    select distinct date_trunc('day', created_at) as date_day
    from {{ ref('fct_orders') }}
)

select date_spine.date_day as missing_date
from date_spine
left join actual_dates using (date_day)
where actual_dates.date_day is null
```

### Cross-Source Reconciliation

Compare data between sources:

```sql
-- tests/assert_payment_totals_match_stripe.sql

with our_totals as (
    select
        date_trunc('day', created_at) as payment_date,
        sum(amount) as our_total
    from {{ ref('fct_payments') }}
    where created_at >= current_date - interval '7 days'
    group by 1
),

stripe_totals as (
    select
        date_trunc('day', created) as payment_date,
        sum(amount) / 100.0 as stripe_total  -- Stripe uses cents
    from {{ ref('stg__stripe__charges') }}
    where status = 'succeeded'
      and created >= current_date - interval '7 days'
    group by 1
)

select
    coalesce(o.payment_date, s.payment_date) as payment_date,
    o.our_total,
    s.stripe_total,
    abs(coalesce(o.our_total, 0) - coalesce(s.stripe_total, 0)) as difference
from our_totals o
full outer join stripe_totals s using (payment_date)
where abs(coalesce(o.our_total, 0) - coalesce(s.stripe_total, 0)) > 1.00  -- Allow $1 tolerance
```

## Test Configuration

### In YAML

```yaml
# models/marts/core/_core__models.yml
version: 2

models:
  - name: fct_orders

tests:
  - name: assert_order_dates_logical
    description: Verify temporal consistency of order lifecycle dates
    config:
      severity: error
      tags: ['critical', 'orders']
      
  - name: assert_daily_revenue_matches_orders
    description: Reconcile daily revenue rollup with order detail
    config:
      severity: warn
      tags: ['reconciliation']
      where: "revenue_date >= current_date - interval '7 days'"
```

### In SQL File

```sql
-- tests/assert_order_dates_logical.sql

{{
    config(
        severity='error',
        tags=['critical', 'orders'],
        meta={'owner': 'data-team'}
    )
}}

select 
    order_id,
    ordered_at,
    shipped_at
from {{ ref('fct_orders') }}
where shipped_at < ordered_at
```

## Using Variables and Macros

### Parameterized Tests

```sql
-- tests/assert_recent_data_exists.sql

{% set min_days = var('freshness_threshold_days', 1) %}

select 1
from {{ ref('fct_orders') }}
having max(created_at) < current_timestamp - interval '{{ min_days }} days'
```

### Reusable Test Logic

```sql
-- macros/test_helpers.sql

{% macro get_orphaned_records(child_model, child_key, parent_model, parent_key) %}

with child as (
    select distinct {{ child_key }} as key_value
    from {{ ref(child_model) }}
    where {{ child_key }} is not null
),

parent as (
    select {{ parent_key }} as key_value
    from {{ ref(parent_model) }}
)

select child.key_value
from child
left join parent using (key_value)
where parent.key_value is null

{% endmacro %}
```

```sql
-- tests/assert_orders_have_customers.sql

{{ get_orphaned_records('fct_orders', 'customer_id', 'dim_customers', 'customer_id') }}
```

## Running Singular Tests

```bash
# Run all singular tests
dbt test --select "test_type:singular"

# Run specific test
dbt test --select assert_order_dates_logical

# Run tests in a directory
dbt test --select "path:tests/marts/*"

# Run tests by tag
dbt test --select "tag:critical"

# Run tests for a model (includes singular tests that ref it)
dbt test --select fct_orders
```

## Best Practices

**Do:**
- Name tests clearly: `assert_<what_should_be_true>`
- Include helpful columns in output (makes debugging easier)
- Add descriptions explaining the business rule
- Use `config()` to set severity and tags
- Scope tests to recent data when full-table scans are expensive

**Don't:**
- Use singular tests for simple validations (use generic tests)
- Return `select *` — only return columns needed for debugging
- Forget to handle nulls in comparisons
- Create tests that are expensive to run without scoping

## Complete Example

```sql
-- tests/marts/assert_subscription_lifecycle_valid.sql

{{
    config(
        severity='error',
        tags=['subscriptions', 'critical'],
        description='Validates subscription business rules'
    )
}}

/*
Business Rules:
1. End date must be after start date
2. Trial subscriptions: 7-30 days
3. Monthly subscriptions: 28-31 days
4. Annual subscriptions: 360-370 days
5. Cancelled subscriptions must have cancellation reason
*/

with subscriptions as (
    select
        subscription_id,
        subscription_type,
        status,
        started_at,
        ends_at,
        cancelled_at,
        cancellation_reason,
        {{ datediff('started_at', 'ends_at', 'day') }} as duration_days
    from {{ ref('fct_subscriptions') }}
)

select
    subscription_id,
    subscription_type,
    status,
    started_at,
    ends_at,
    duration_days,
    cancellation_reason,
    case
        when ends_at <= started_at then 'end_before_start'
        when subscription_type = 'trial' and duration_days not between 7 and 30 then 'invalid_trial_duration'
        when subscription_type = 'monthly' and duration_days not between 28 and 31 then 'invalid_monthly_duration'
        when subscription_type = 'annual' and duration_days not between 360 and 370 then 'invalid_annual_duration'
        when status = 'cancelled' and cancellation_reason is null then 'missing_cancellation_reason'
    end as violation_type
from subscriptions
where ends_at <= started_at
   or (subscription_type = 'trial' and duration_days not between 7 and 30)
   or (subscription_type = 'monthly' and duration_days not between 28 and 31)
   or (subscription_type = 'annual' and duration_days not between 360 and 370)
   or (status = 'cancelled' and cancellation_reason is null)
```
