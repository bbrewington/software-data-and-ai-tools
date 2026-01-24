# Data Modeling

Dimensional modeling patterns for analytics and data warehousing in the modern data stack.

## Core Concepts

### Grain

**Always define the grain first** — what does one row represent? Every modeling decision flows from this.

| Model | Grain | Why It Matters |
|-------|-------|----------------|
| `fct_orders` | One row per order | Aggregating to customer requires `COUNT(DISTINCT)` |
| `fct_order_items` | One row per item in an order | Can sum quantities directly |
| `dim_customers` | One row per customer (current state) | SCD Type 1 — simple but no history |
| `dim_customers_history` | One row per customer per change | SCD Type 2 — enables point-in-time analysis |

**Grain and incremental models:** Your grain determines your incremental strategy. A transaction fact (`fct_orders`) can use `unique_key = 'order_id'` safely. An accumulating snapshot needs merge logic because rows update over time.

### Facts vs Dimensions

| Type | Purpose | Characteristics | Examples |
|------|---------|-----------------|----------|
| **Fact** | Measurable events/transactions | Numeric measures, foreign keys, timestamps | `fct_orders`, `fct_page_views`, `fct_payments` |
| **Dimension** | Descriptive attributes | Text attributes, hierarchies, slowly changing | `dim_customers`, `dim_products`, `dim_dates` |

**Gray areas exist.** A `dim_customers` table with `lifetime_revenue` is technically a dimension with a fact embedded. That's fine — purity matters less than usability.

### Schema Patterns

**Star Schema**
```
        dim_customers
              │
dim_products──fct_orders──dim_dates
              │
        dim_locations
```
- Central fact table surrounded by dimensions
- Denormalized dimensions for query simplicity
- Still the default starting point for most analytics

**Snowflake Schema**
- Normalized dimensions (e.g., `dim_products` → `dim_categories` → `dim_departments`)
- Modern columnar engines handle these joins efficiently
- Use when dimension hierarchies are complex or shared across facts

**One Big Table (OBT)**
- Fully denormalized: all dimensions pre-joined into the fact
- Appropriate for: embedded analytics, ML feature stores, simple dashboard backends
- Tradeoffs: data duplication, harder to maintain, but eliminates BI tool join complexity

**Choose based on your consumers:** Star schema for flexible BI tools. OBT for embedded analytics or when your consumers can't handle joins.

## Normalization vs Denormalization

### Modern Guidance

The traditional advice — "denormalize for read performance" — was written when joins were expensive. Columnar warehouses (Snowflake, BigQuery, Databricks) have changed the calculus:

| Consideration | Normalize | Denormalize |
|--------------|-----------|-------------|
| Query engine | Row-based / OLTP | Columnar / OLAP (either works) |
| Data consistency | Critical | Acceptable lag |
| Dimension update frequency | High | Low |
| Consumer capability | Can handle joins | Needs flat tables |
| Storage costs | Concern | Not a concern |

### Recommended Approach

```
Sources → Staging (Normalized) → Intermediate (Business Logic) → Marts (Fit for Purpose)
              │                         │                              │
        1:1 with source          Joins, transforms              Star, OBT, or domain-specific
        Clean/rename only        Reusable building blocks       Shaped for consumers
```

**Don't over-denormalize preventively.** Start with a star schema, denormalize further only when you hit real performance issues or consumer limitations.

## Slowly Changing Dimensions (SCD)

### Type 1: Overwrite

Simply update the dimension record. No history preserved.

```sql
-- dim_customers: current state only
select
    customer_id,
    email,
    address,
    updated_at
from {{ ref('stg__customers') }}
```

**Use when:** History doesn't matter (typo corrections, non-critical attributes), or you're just getting started and can add history later.

### Type 2: Add New Row

Add a new row for each change, with validity dates.

```sql
-- dim_customers_history: full change history
select
    customer_id,
    email,
    address,
    valid_from,
    coalesce(valid_to, '9999-12-31'::date) as valid_to,
    valid_to is null as is_current
from {{ ref('stg__customers_history') }}
```

**Use when:** Need point-in-time analysis ("what was their address when they placed this order?")

**Implementation options:**
- dbt snapshots (recommended for most cases)
- Source system CDC
- Manual effective dating

**On surrogate keys:** Type 2 dimensions traditionally use surrogate keys to uniquely identify each version. With dbt:

```sql
-- Option 1: Surrogate key (traditional)
{{ dbt_utils.generate_surrogate_key(['customer_id', 'valid_from']) }} as customer_sk

-- Option 2: Composite natural key (often sufficient)
-- Just use (customer_id, valid_from) as your logical key
-- Many BI tools handle this fine
```

Choose surrogate keys when your BI tool requires a single-column key. Otherwise, composite natural keys reduce complexity.

### Type 3: Add New Column

Track limited history with dedicated columns.

```sql
select
    customer_id,
    email as current_email,
    previous_email,
    email_changed_at
from {{ ref('stg__customers') }}
```

**Use when:** Only need one previous value (rare in practice).

## Dimension Patterns

### Conformed Dimensions

Same dimension used across multiple fact tables. Essential for consistent reporting.

```sql
-- dim_date: shared across all facts
select
    date_day,
    day_of_week,
    day_of_week_name,
    month_start_date,
    month_name,
    quarter,
    year,
    is_weekend,
    is_holiday
from {{ ref('stg__date_spine') }}
```

**Create conformed dimensions for:** dates, customers, products, geographies — anything referenced by multiple facts.

### Role-Playing Dimensions

Same dimension used multiple ways in one fact:

```sql
-- fct_orders references dim_date three times
select
    o.order_id,
    o.order_date,
    o.ship_date,
    o.delivery_date,
    -- BI tool joins to dim_date on each date column
    ...
from {{ ref('stg__orders') }} o
```

No need to duplicate `dim_date` — your BI tool aliases the same dimension for each role.

### Degenerate Dimensions

Dimension values stored directly in fact table (no separate dim needed):

```sql
-- order_number lives in the fact, not a separate dimension
select
    order_item_id,
    order_number,      -- degenerate dimension
    product_id,
    quantity,
    amount
from {{ ref('stg__order_items') }}
```

**Use for:** Transaction identifiers, invoice numbers, confirmation codes — high-cardinality values with no additional attributes.

### Junk Dimensions (Use Sparingly)

Combine low-cardinality flags into one dimension:

```sql
select distinct
    {{ dbt_utils.generate_surrogate_key(['is_gift', 'is_rush', 'is_international']) }} as order_flags_sk,
    is_gift,
    is_rush,
    is_international
from {{ ref('stg__orders') }}
```

**Modern take:** Columnar compression makes this optimization largely unnecessary. Keeping flags directly on the fact table is simpler and performs fine. Consider junk dimensions only if you have many (10+) flags and want to simplify your fact table schema.

## Fact Patterns

### Transaction Facts

One row per discrete event. The most common pattern.

```sql
-- fct_orders: one row per order
select
    order_id,
    customer_id,
    order_date,
    total_amount,
    discount_amount,
    item_count
from {{ ref('stg__orders') }}
```

**Incremental strategy:** Append-only or merge on natural key.

### Periodic Snapshot Facts

Capture state at regular intervals.

```sql
-- fct_inventory_daily: one row per product per warehouse per day
select
    date_day,
    product_id,
    warehouse_id,
    quantity_on_hand,
    quantity_reserved,
    days_of_supply
from {{ ref('int__inventory_snapshots') }}
```

**Use when:** You need to trend a measure over time but the source only shows current state (inventory levels, account balances, pipeline stages).

**Incremental strategy:** Insert new snapshot rows daily; never update historical rows.

### Accumulating Snapshot Facts

Track entity lifecycle through multiple milestones.

```sql
-- fct_order_fulfillment: one row per order, updated as milestones occur
select
    order_id,
    order_placed_at,
    payment_confirmed_at,
    shipped_at,
    delivered_at,
    
    -- Derived metrics
    {{ datediff('order_placed_at', 'shipped_at', 'hour') }} as hours_to_ship,
    {{ datediff('shipped_at', 'delivered_at', 'hour') }} as hours_in_transit
from {{ ref('int__order_milestones') }}
```

**Use when:** Analyzing process efficiency, SLA compliance, funnel conversion.

**Incremental strategy:** Merge on entity key; rows update as new milestones occur.

### Factless Facts

Record events with no measurable quantity.

```sql
-- fct_student_attendance: student was present on date
select
    attendance_id,
    student_id,
    class_id,
    attendance_date
    -- No amount column — the row's existence IS the fact
from {{ ref('stg__attendance') }}
```

**Use when:** Tracking coverage, eligibility, or presence (attendance, promotions in effect, product availability).

## Activity Schema / Event Modeling

For event-driven businesses (SaaS, e-commerce, product analytics), traditional Kimball patterns can feel forced. Consider activity schema as an alternative:

```sql
-- fct_activity_stream: all user actions in one table
select
    activity_id,
    user_id,
    activity_type,        -- 'page_view', 'purchase', 'subscription_started', etc.
    occurred_at,
    activity_attributes   -- VARIANT/JSON for type-specific data
from {{ ref('int__unified_activities') }}
```

**Tradeoffs:**
- Pro: One table to query for user timelines, flexible schema via JSON
- Con: Harder to aggregate, requires discipline around `activity_type` values

**Hybrid approach:** Use activity schema for raw events, then build traditional facts on top for specific analyses.

## Metrics Layer Considerations

### The Shift Away from Pre-Aggregated Marts

Traditional approach — build pre-aggregated tables:

```sql
-- metrics_orders_daily: pre-computed for dashboard performance
select
    order_date,
    region,
    count(*) as order_count,
    sum(amount) as total_revenue
from {{ ref('fct_orders') }}
group by 1, 2
```

**The problem:** You end up with dozens of `metrics_*` tables for different dimensional cuts. Adding a dimension means building new tables.

### Modern Alternative: Semantic Layer

Push metric definitions to a semantic layer (dbt Semantic Layer, Cube, Looker/LookML, AtScale):

```yaml
# dbt Semantic Layer example
metrics:
  - name: revenue
    type: sum
    type_params:
      measure: total_amount
    filter: "is_completed = true"
    
  - name: revenue_per_order
    type: derived
    type_params:
      expr: revenue / order_count
```

**Benefits:**
- Single definition, multiple dimensional cuts
- Consistent metrics across BI tools
- Aggregations computed at query time

**When to still pre-aggregate:**
- Extremely large datasets where query-time aggregation is too slow
- Feeding systems that can't use your semantic layer (exports, reverse ETL)
- Complex calculations that don't fit semantic layer capabilities

## Aggregation Patterns (When You Need Them)

### Pre-Aggregated Rollups

For known, performance-critical queries:

```sql
-- fct_orders_daily: only if semantic layer isn't viable
{{ config(materialized='incremental', unique_key='order_date || region') }}

select
    order_date,
    region,
    count(*) as order_count,
    sum(amount) as revenue,
    count(distinct customer_id) as unique_customers
from {{ ref('fct_orders') }}
{% if is_incremental() %}
where order_date >= (select max(order_date) - interval '3 days' from {{ this }})
{% endif %}
group by 1, 2
```

### Window Functions for Flexible Analysis

Keep calculations in the detail table when possible:

```sql
select
    *,
    sum(amount) over (
        partition by customer_id
        order by order_date
        rows between 29 preceding and current row
    ) as rolling_30d_revenue,
    
    row_number() over (
        partition by customer_id
        order by order_date
    ) as customer_order_number
from {{ ref('fct_orders') }}
```

**Window functions vs pre-aggregation:** Window functions add columns to existing grain. Pre-aggregation changes the grain. Different tools for different problems.

## When to Break the Rules

Modeling principles are guidelines, not laws. Break them intentionally:

| "Rule" | When to Break It |
|--------|------------------|
| Facts should only have foreign keys and measures | Add commonly-filtered dimension attributes to avoid joins in hot paths |
| Use surrogate keys for dimensions | Natural keys are fine when they're stable and your tools support them |
| Normalize dimensions | Pre-join dimensions for OBT when consumers need flat tables |
| One fact per business process | Combine tightly-coupled processes (orders + order_items) when always queried together |
| Avoid derived columns in staging | Calculate cheap derivations early if they're needed everywhere downstream |

**The test:** Can you explain why you're breaking the rule and what tradeoff you're accepting?

## Quick Reference: Model Naming

| Prefix | Purpose | Example |
|--------|---------|---------|
| `stg__` | Staging: 1:1 with source, renamed/typed | `stg__shopify__orders` |
| `int__` | Intermediate: business logic, not exposed | `int__orders_enriched` |
| `dim_` | Dimension: descriptive attributes | `dim_customers` |
| `fct_` | Fact: measurable events | `fct_orders` |
| `rpt_` | Report: wide tables for specific dashboards | `rpt_executive_summary` |
| `metrics_` | Aggregated: pre-computed rollups | `metrics_orders_daily` |