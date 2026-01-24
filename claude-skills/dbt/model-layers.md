# Model Layers

Organizing dbt models into staging, intermediate, and marts layers.

## Layer Architecture

```
sources/          Raw data definitions (YAML)
    ↓
staging/          1:1 with source, light cleaning
    ↓
intermediate/     Business logic, joins, aggregations
    ↓
marts/            Final analytics tables (facts & dimensions)
```

This pattern is sometimes called "dbtonic layers" or "staging/integration/presentation" -- as compared to medallion architecture (Bronze/Silver/Gold). The principles are similar: progressively transform raw data into analytics-ready assets.

## Layer Guidelines

| Layer | Materialization | Purpose | Business Logic |
|-------|-----------------|---------|----------------|
| **Staging** | `view` | Rename, cast, clean, flatten | None |
| **Intermediate** | Depends on use case | Transform, join, aggregate | Yes |
| **Marts** | `table` or `incremental` | Final output for analysts | Minimal (inherited) |

### Choosing Intermediate Materialization

| Materialization | When to Use | Tradeoffs |
|-----------------|-------------|-----------|
| `ephemeral` | Simple transforms, single downstream consumer | Can't query directly for debugging |
| `view` | Light transforms, data changes frequently | Recomputes on every query |
| `table` | Expensive joins/aggregations, multiple downstream refs | Storage cost, staleness between runs |
| `incremental` | Large intermediate datasets with clear append logic | Complexity, requires maintenance |

**Default advice:** Start with `view`, promote to `table` when you see performance issues or the model is referenced 3+ times downstream.

## Project Structure

```
models/
├── staging/
│   ├── stripe/
│   │   ├── _stripe__sources.yml         # Source definitions
│   │   ├── _stripe__models.yml          # Model tests/docs
│   │   ├── stg__stripe__customers.sql
│   │   ├── stg__stripe__payments.sql
│   │   └── stg__stripe__subscriptions.sql
│   └── hubspot/
│       ├── _hubspot__sources.yml
│       ├── _hubspot__models.yml
│       ├── stg__hubspot__contacts.sql
│       └── stg__hubspot__deals.sql
├── intermediate/
│   ├── customers/
│   │   ├── _int_customers__models.yml
│   │   ├── int_customers__unioned.sql
│   │   └── int_customers__enriched.sql
│   └── orders/
│       ├── _int_orders__models.yml
│       └── int_orders__items_enriched.sql
└── marts/
    ├── core/
    │   ├── _core__models.yml
    │   ├── dim_customers.sql
    │   ├── dim_products.sql
    │   └── fct_orders.sql
    └── finance/
        ├── _finance__models.yml
        ├── fct_payments.sql
        └── fct_monthly_revenue.sql
```

### Naming Conventions

| Layer | Pattern | Examples |
|-------|---------|----------|
| Staging | `stg__<source>__<table>` | `stg__stripe__customers`, `stg__hubspot__contacts` |
| Intermediate | `int_<entity>__<transformation>` | `int_customers__unioned`, `int_orders__enriched` |
| Marts (dims) | `dim_<entity>` | `dim_customers`, `dim_products` |
| Marts (facts) | `fct_<event/process>` | `fct_orders`, `fct_payments` |

## Staging Layer

### Purpose

- 1:1 mapping with source tables
- Rename columns to project conventions
- Cast data types
- Light cleaning (trim, lowercase)
- **No business logic**

### Source Definition

```yaml
# models/staging/stripe/_stripe__sources.yml
version: 2

sources:
  - name: stripe
    description: Stripe payment processing data
    database: "{{ var('stripe_database', target.database) }}"
    schema: "{{ var('stripe_schema', 'stripe') }}"
    
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _fivetran_synced  # Use actual load timestamp
    
    tables:
      - name: customers
        description: Stripe customer records
        identifier: customer  # If source table name differs
        columns:
          - name: id
            description: Stripe customer ID
            tests:
              - unique
              - not_null
          - name: email
            description: Customer email address
          - name: created
            description: Account creation timestamp (Unix epoch)

      - name: payments
        description: Payment transactions
        loaded_at_field: created  # Override for this table
```

**Note on freshness:** Use a column that actually updates when new data arrives (like `_fivetran_synced`, `_loaded_at`, or an event timestamp). Don't use `created_at` on slowly-changing tables—it won't reflect new data loading.

### Staging Model Pattern

```sql
-- models/staging/stripe/stg__stripe__customers.sql
-- Grain: One row per customer

with source as (
    select * from {{ source('stripe', 'customers') }}
),

renamed as (
    select
        -- Primary key
        id as customer_id,

        -- Attributes
        lower(trim(email)) as email,
        name as customer_name,
        currency as default_currency,
        
        -- Booleans
        coalesce(delinquent, false) as is_delinquent,
        
        -- Timestamps (convert Unix epoch to timestamp)
        timestamp_seconds(created) as created_at,
        
        -- Metadata
        _fivetran_synced as synced_at

    from source
)

select * from renamed
```

### What Belongs in Staging

**Do**

- Rename `id` → `customer_id`
- Cast Unix epoch → `timestamp`
- Trim whitespace, lowercase emails
- Handle nulls with `coalesce`
- Add `synced_at` metadata

**Don't**

- Join to other tables
- Calculate derived fields
- Filter rows (except deduplication)
- Aggregate data
- Apply business rules

### Deduplication in Staging

When sources have duplicates, handle them in staging:

```sql
with source as (
    select * from {{ source('stripe', 'customers') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by id
            order by _fivetran_synced desc
        ) as row_num
    from source
),

renamed as (
    select
        id as customer_id,
        ...
    from deduplicated
    where row_num = 1
)

select * from renamed
```

## Intermediate Layer

### Purpose

- Business logic and transformations
- Joins between staging models
- Aggregations and calculations
- Unioning similar sources
- Preparing data for marts

### Pattern: Unioning Multiple Sources

```sql
-- models/intermediate/customers/int_customers__unioned.sql
-- Grain: One row per customer (across all sources)

with stripe_customers as (
    select
        customer_id,
        email,
        customer_name,
        'stripe' as source_system,
        created_at
    from {{ ref('stg__stripe__customers') }}
),

hubspot_contacts as (
    select
        contact_id as customer_id,
        email,
        concat(first_name, ' ', last_name) as customer_name,
        'hubspot' as source_system,
        created_at
    from {{ ref('stg__hubspot__contacts') }}
),

unioned as (
    select * from stripe_customers
    union all
    select * from hubspot_contacts
),

-- Deduplicate across sources (prefer Stripe as system of record)
deduplicated as (
    select
        *,
        row_number() over (
            partition by email
            order by case source_system when 'stripe' then 1 else 2 end
        ) as row_num
    from unioned
)

select
    {{ dbt_utils.generate_surrogate_key(['email']) }} as customer_key,
    customer_id,
    email,
    customer_name,
    source_system,
    created_at
from deduplicated
where row_num = 1
```

### Pattern: Enrichment and Aggregation

```sql
-- models/intermediate/customers/int_customers__enriched.sql
-- Grain: One row per customer

with customers as (
    select * from {{ ref('int_customers__unioned') }}
),

orders as (
    select * from {{ ref('stg__stripe__orders') }}
),

order_metrics as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount_cents) / 100.0 as lifetime_revenue,
        min(created_at) as first_order_at,
        max(created_at) as last_order_at,
        avg(amount_cents) / 100.0 as avg_order_value
    from orders
    where status = 'completed'
    group by customer_id
)

select
    customers.customer_key,
    customers.customer_id,
    customers.email,
    customers.customer_name,
    customers.source_system,
    customers.created_at,
    
    -- Order metrics (with safe defaults)
    coalesce(order_metrics.total_orders, 0) as total_orders,
    coalesce(order_metrics.lifetime_revenue, 0) as lifetime_revenue,
    order_metrics.first_order_at,
    order_metrics.last_order_at,
    order_metrics.avg_order_value,
    
    -- Derived: days since last order
    {{ datediff('order_metrics.last_order_at', 'current_date', 'day') }} as days_since_last_order

from customers
left join order_metrics using (customer_id)
```

### Pattern: Unnesting Arrays

```sql
-- models/intermediate/orders/int_orders__items_enriched.sql
-- Grain: One row per order line item

with orders as (
    select * from {{ ref('stg__stripe__orders') }}
),

-- Unnest line items from order
unnested as (
    select
        orders.order_id,
        orders.customer_id,
        orders.created_at as order_created_at,
        item.product_id,
        item.quantity,
        item.unit_price_cents / 100.0 as unit_price,
        (item.quantity * item.unit_price_cents) / 100.0 as line_total
    from orders
    cross join unnest(orders.line_items) as item
),

-- Enrich with product details
enriched as (
    select
        unnested.*,
        products.product_name,
        products.category
    from unnested
    left join {{ ref('stg__stripe__products') }} as products
        using (product_id)
)

select * from enriched
```

## Marts Layer

### Purpose

- Final output for analysts and BI tools
- Dimensional models (facts and dimensions)
- Optimized for query performance
- Stable contracts for downstream consumers

### Dimension Model Pattern

```sql
-- models/marts/core/dim_customers.sql
-- Grain: One row per customer

{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}

with enriched_customers as (
    select * from {{ ref('int_customers__enriched') }}
),

final as (
    select
        -- Keys
        customer_key,
        customer_id,

        -- Attributes
        email,
        customer_name,
        source_system,
        
        -- Metrics
        total_orders,
        lifetime_revenue,
        first_order_at,
        last_order_at,
        avg_order_value,
        days_since_last_order,

        -- Derived segments
        case
            when lifetime_revenue >= 1000 then 'high_value'
            when lifetime_revenue >= 100 then 'medium_value'
            else 'low_value'
        end as customer_tier,
        
        case
            when total_orders = 0 then 'never_purchased'
            when days_since_last_order <= 30 then 'active'
            when days_since_last_order <= 90 then 'cooling'
            else 'churned'
        end as customer_status,

        -- Timestamps
        created_at,
        current_timestamp() as updated_at

    from enriched_customers
)

select * from final
```

### Fact Model Pattern

```sql
-- models/marts/core/fct_orders.sql
-- Grain: One row per order

{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        contract={'enforced': true}
    )
}}

with orders as (
    select * from {{ ref('stg__stripe__orders') }}
    {% if is_incremental() %}
    where created_at >= (select max(created_at) from {{ this }}) - interval 3 day
    {% endif %}
),

customers as (
    select 
        customer_id, 
        customer_key, 
        customer_tier,
        customer_status
    from {{ ref('dim_customers') }}
),

final as (
    select
        -- Keys
        orders.order_id,
        orders.customer_id,
        customers.customer_key,

        -- Denormalized dimension attributes
        -- NOTE: Including these avoids joins for common filters but creates
        -- update anomalies. If customer_tier changes, historical orders will
        -- show the NEW tier, not the tier at time of order. For point-in-time
        -- accuracy, join to a Type 2 SCD dimension instead.
        customers.customer_tier,
        customers.customer_status,

        -- Measures
        orders.subtotal_cents / 100.0 as subtotal,
        orders.tax_cents / 100.0 as tax,
        orders.shipping_cents / 100.0 as shipping,
        orders.total_cents / 100.0 as total_amount,
        orders.discount_cents / 100.0 as discount_amount,
        orders.item_count,

        -- Timestamps
        orders.created_at,
        orders.updated_at

    from orders
    left join customers using (customer_id)
)

select * from final
```

### Access Control (dbt 1.5+)

Control which models can be referenced by other projects or teams:

```sql
-- Public: can be referenced by any project
{{
    config(
        materialized='table',
        access='public'
    )
}}

-- Protected: can only be referenced within same project (default)
{{
    config(
        materialized='table',
        access='protected'
    )
}}

-- Private: can only be referenced within same directory
{{
    config(
        materialized='view',
        access='private'
    )
}}
```

**Guidance:**
- Marts: typically `public` (these are your stable interfaces)
- Intermediate: typically `protected` or `private` (implementation details)
- Staging: typically `protected` (other projects should use their own staging)

## Model Documentation

### Co-located YAML

Keep YAML files next to related SQL files:

```yaml
# models/marts/core/_core__models.yml
version: 2

models:
  - name: dim_customers
    description: |
      Customer dimension with order metrics and behavioral segments.
      
      **Grain:** One row per customer
      **Update frequency:** Daily
      **Primary consumer:** Marketing analytics, Customer Success
    
    access: public
    
    config:
      contract:
        enforced: true
    
    columns:
      - name: customer_key
        description: Surrogate key for the customer (hash of email)
        data_type: string
        constraints:
          - type: not_null
        tests:
          - unique
          - not_null

      - name: customer_id
        description: Natural key from primary source system
        data_type: string
        tests:
          - unique
          - not_null

      - name: customer_tier
        description: |
          Value segment based on lifetime revenue:
          - high_value: >= $1,000
          - medium_value: >= $100
          - low_value: < $100
        data_type: string
        tests:
          - accepted_values:
              values: ['high_value', 'medium_value', 'low_value']

      - name: customer_status
        description: |
          Activity status based on recency:
          - active: ordered within 30 days
          - cooling: ordered within 90 days
          - churned: no order in 90+ days
          - never_purchased: no orders
        data_type: string
        tests:
          - accepted_values:
              values: ['active', 'cooling', 'churned', 'never_purchased']
```

### Contracts (dbt 1.5+)

Enforce column names and types for stable interfaces:

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
          - type: primary_key
      - name: total_amount
        data_type: float64
        constraints:
          - type: not_null
```

When a contract is enforced:
- Column names and types must match exactly
- Missing columns or type mismatches fail at build time
- Protects downstream consumers from breaking changes

## Quick Reference: Layer Decisions

| Question | Answer |
|----------|--------|
| Where do I rename columns? | Staging |
| Where do I join tables? | Intermediate |
| Where do I apply business rules? | Intermediate (logic) → Marts (final derivations) |
| Where do I aggregate? | Intermediate (if reused) or Marts (if final) |
| Where do I deduplicate? | Staging (source dupes) or Intermediate (cross-source) |
| What should BI tools query? | Marts only |
| What can other dbt projects reference? | Public marts only |
