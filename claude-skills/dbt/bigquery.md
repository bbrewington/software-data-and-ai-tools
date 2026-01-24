# BigQuery Configuration

BigQuery-specific patterns for dbt including partitioning, clustering, and incremental strategies.

## Partitioning

Partitioning divides a table into segments for query performance and cost optimization.

### Time-Based Partitioning

```sql
{{
    config(
        materialized='table',
        partition_by={
            "field": "created_at",
            "data_type": "timestamp",
            "granularity": "day"
        }
    )
}}
```

### Date Partitioning

```sql
{{
    config(
        partition_by={
            "field": "order_date",
            "data_type": "date"
        }
    )
}}
```

### Integer Range Partitioning

```sql
{{
    config(
        partition_by={
            "field": "customer_id",
            "data_type": "int64",
            "range": {
                "start": 0,
                "end": 1000000,
                "interval": 1000
            }
        }
    )
}}
```

### When to Partition

| Scenario | Recommendation |
|----------|----------------|
| Large table frequently filtered by date | Partition by that date field |
| Need to expire old data | Partition + set expiration |
| Small table with infrequent date filters | Don't partition |

> **Note:** Changing partitioning (adding to unpartitioned table, changing granularity) requires a full table rebuild via `--full-refresh`, not an in-place change.

## Clustering

Clustering sorts data within partitions for efficient filtering.

```sql
{{
    config(
        materialized='table',
        partition_by={
            "field": "created_at",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by=['project_id', 'dataset_name']
    )
}}
```

### Clustering Guidelines

- Max 4 clustering columns
- Order by filter frequency (most filtered first)
- Works best with high-cardinality columns
- Combine with partitioning for best results

### When to Cluster

| Scenario | Cluster By |
|----------|------------|
| Filter by user_id | `cluster_by=['user_id']` |
| Filter by region then category | `cluster_by=['region', 'category']` |
| GROUP BY product_id | `cluster_by=['product_id']` |

## Incremental Strategies

### Merge (Default)

Best for late-arriving data and updates.

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge'
    )
}}

select *
from {{ ref('stg__orders') }}

{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

### Merge with Update Columns

Only update specific columns on merge:

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        merge_update_columns=['status', 'updated_at', 'total_amount']
    )
}}
```

Or exclude specific columns (update everything except):

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        merge_exclude_columns=['created_at', 'customer_id']  -- Never update these
    )
}}
```

> **Warning:** `merge_exclude_columns` support on BigQuery may be inconsistent. Verify behavior in your environment before relying on it. Using `merge_update_columns` (explicit include list) is more reliable.

### Insert Overwrite

Best for reprocessing entire partitions:

```sql
{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        partition_by={
            "field": "event_date",
            "data_type": "date"
        }
    )
}}

select
    *,
    date(created_at) as event_date
from {{ ref('stg__events') }}

{% if is_incremental() %}
where event_date >= date_sub(current_date(), interval 3 day)
{% endif %}
```

Using `_dbt_max_partition` (adapter-native approach):

```sql
{% if is_incremental() %}
where event_date >= _dbt_max_partition
{% endif %}
```

### Strategy Comparison

| Strategy | Use Case | Handles Updates | Partition Required |
|----------|----------|-----------------|-------------------|
| `merge` | Updates to existing rows | Yes | No |
| `insert_overwrite` | Reprocess full partitions | Via overwrite | Yes |
| `append` | Insert-only (logs, events) | No | No |

## Full Incremental Example

```sql
-- models/marts/fct_jobs.sql
{{
    config(
        materialized='incremental',
        unique_key='job_id',
        incremental_strategy='merge',
        partition_by={
            "field": "creation_time",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by=['user_email', 'project_id'],
        merge_update_columns=['state', 'end_time', 'total_bytes_processed']
    )
}}

with source as (
    select * from {{ ref('stg__info_schema__jobs') }}

    {% if is_incremental() %}
    -- Only process new/updated jobs
    where creation_time > (select max(creation_time) from {{ this }})
       or end_time > (select max(end_time) from {{ this }})
    {% endif %}
)

select
    job_id,
    project_id,
    user_email,
    state,
    creation_time,
    start_time,
    end_time,
    total_bytes_processed,
    total_slot_ms,
    cache_hit
from source
```

## Macros

### INFORMATION_SCHEMA Accessor

```sql
-- macros/info_schema.sql
{% macro info_schema(info_schema_type, dataset=none, region='region-us') %}
    {%- if dataset is not none -%}
        `{{ target.project }}`.`{{ dataset }}`.INFORMATION_SCHEMA.{{ info_schema_type }}
    {%- else -%}
        `{{ target.project }}`.`{{ region }}`.INFORMATION_SCHEMA.{{ info_schema_type }}
    {%- endif -%}
{% endmacro %}

-- Usage:
-- {{ info_schema('TABLES') }}
-- {{ info_schema('COLUMNS', dataset='my_dataset') }}
```

### Limit Data in Dev

```sql
-- macros/limit_data_in_dev.sql
{% macro limit_data_in_dev(column_name, days=3) %}
    {% if target.name == 'dev' %}
        where {{ column_name }} >= timestamp_sub(current_timestamp(), interval {{ days }} day)
    {% endif %}
{% endmacro %}

-- Usage (only when no existing WHERE clause):
-- select * from source
-- {{ limit_data_in_dev('created_at', days=7) }}
```

> **Note:** This macro injects a `WHERE` clause directly. Use only when the query doesn't already have a `WHERE`. For queries with existing filters, use `AND` logic instead.

### Generate Date Spine

```sql
-- macros/date_spine.sql
{% macro date_spine(start_date, end_date) %}
    select date_day
    from unnest(
        generate_date_array(
            {{ start_date }},
            {{ end_date }}
        )
    ) as date_day
{% endmacro %}
```

## Cost Optimization

### Query Cost Factors

| Factor | Impact | Optimization |
|--------|--------|--------------|
| Bytes scanned | Direct cost | Partition + cluster |
| Table size | Storage cost | Use incremental |
| Slot usage | Concurrent queries | Optimize SQL |

### Cost-Saving Patterns

**1. Always filter on partition column:**
```sql
-- Good: Uses partition pruning
where created_at >= '2024-01-01'

-- Bad: Scans all partitions
where date(created_at) >= '2024-01-01'
```

**2. Select only needed columns:**
```sql
-- Good
select order_id, customer_id, amount from orders

-- Bad
select * from orders
```

**3. Use approximate functions for large data:**
```sql
-- Good for estimates
select approx_count_distinct(user_id) from events

-- Exact but expensive
select count(distinct user_id) from events
```

**4. Avoid repeated full table scans:**
```sql
-- Use intermediate models instead of CTEs that scan repeatedly
-- Create int__ model for complex logic used multiple times
```

## Table Options

### Require Partition Filter

```sql
{{
    config(
        partition_by={"field": "created_at", "data_type": "timestamp"},
        require_partition_filter=true  -- Queries must filter on partition
    )
}}
```

### Partition Expiration

```sql
{{
    config(
        partition_by={"field": "created_at", "data_type": "timestamp"},
        partition_expiration_days=90  -- Auto-delete partitions older than 90 days
    )
}}
```

### Labels

```sql
{{
    config(
        labels={
            'team': 'analytics',
            'env': target.name
        }
    )
}}
```

## dbt_project.yml Defaults

```yaml
# dbt_project.yml
models:
  my_project:
    staging:
      +materialized: view
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +partition_by:
        field: created_at
        data_type: timestamp
        granularity: day
```
