# Unit Tests

Unit tests validate transformation logic with mocked inputs—essential for complex business rules. Available in dbt 1.8+.

## When to Use Unit Tests

| Scenario | Unit Test? | Why |
|----------|------------|-----|
| Simple column rename | No | Too trivial, covered by contracts |
| Case statement with 3+ branches | Yes | Edge cases are easy to miss |
| Complex date logic | Yes | Date edge cases are notorious |
| Multi-table join logic | Maybe | If the join logic is complex |
| Aggregations | Maybe | If there's conditional logic |
| Window functions | Yes | Partition/order edge cases |
| Null handling logic | Yes | Null behavior is often surprising |
| Currency/unit conversions | Yes | Rounding and precision issues |

**Rule of thumb:** If you'd write a Python unit test for similar logic, write a dbt unit test.

## Basic Unit Test

```yaml
# models/marts/core/_core__models.yml

unit_tests:
  - name: test_customer_tier_assignment
    description: Verify customer tier logic based on lifetime revenue
    model: dim_customers
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C001', lifetime_revenue: 1500, total_orders: 10}
          - {customer_id: 'C002', lifetime_revenue: 500, total_orders: 5}
          - {customer_id: 'C003', lifetime_revenue: 50, total_orders: 1}
          - {customer_id: 'C004', lifetime_revenue: 0, total_orders: 0}
    expect:
      rows:
        - {customer_id: 'C001', customer_tier: 'high_value'}
        - {customer_id: 'C002', customer_tier: 'medium_value'}
        - {customer_id: 'C003', customer_tier: 'low_value'}
        - {customer_id: 'C004', customer_tier: 'low_value'}
```

## Testing Edge Cases

### Boundary Values

Test exact boundaries where logic changes:

```yaml
unit_tests:
  - name: test_customer_tier_boundaries
    description: Verify tier assignment at exact boundary values
    model: dim_customers
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C1', lifetime_revenue: 1000}    # Exactly at high boundary
          - {customer_id: 'C2', lifetime_revenue: 999.99}  # Just below high
          - {customer_id: 'C3', lifetime_revenue: 100}     # Exactly at medium boundary
          - {customer_id: 'C4', lifetime_revenue: 99.99}   # Just below medium
          - {customer_id: 'C5', lifetime_revenue: 0}       # Zero
          - {customer_id: 'C6', lifetime_revenue: -10}     # Negative (edge case)
    expect:
      rows:
        - {customer_id: 'C1', customer_tier: 'high_value'}
        - {customer_id: 'C2', customer_tier: 'medium_value'}
        - {customer_id: 'C3', customer_tier: 'medium_value'}
        - {customer_id: 'C4', customer_tier: 'low_value'}
        - {customer_id: 'C5', customer_tier: 'low_value'}
        - {customer_id: 'C6', customer_tier: 'low_value'}
```

### Null Handling

Explicitly test null behavior:

```yaml
unit_tests:
  - name: test_null_handling_in_metrics
    description: Verify nulls are handled correctly in derived metrics
    model: dim_customers
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C1', lifetime_revenue: 100, first_order_at: '2024-01-01', last_order_at: '2024-06-01'}
          - {customer_id: 'C2', lifetime_revenue: 0, first_order_at: null, last_order_at: null}  # Never ordered
          - {customer_id: 'C3', lifetime_revenue: 50, first_order_at: '2024-03-01', last_order_at: null}  # Data issue
    expect:
      rows:
        - {customer_id: 'C1', days_as_customer: 152, has_ordered: true}
        - {customer_id: 'C2', days_as_customer: null, has_ordered: false}
        - {customer_id: 'C3', days_as_customer: null, has_ordered: true}
```

### Timestamp Combinations

Test all possible states in milestone tracking:

```yaml
unit_tests:
  - name: test_order_status_derivation
    description: Verify order status handles all timestamp combinations
    model: fct_order_fulfillment
    given:
      - input: ref('stg__orders')
        rows:
          # Normal completed order
          - {order_id: 'O1', ordered_at: '2024-01-01', shipped_at: '2024-01-02', delivered_at: '2024-01-05'}
          # Shipped but not delivered
          - {order_id: 'O2', ordered_at: '2024-01-01', shipped_at: '2024-01-02', delivered_at: null}
          # Not yet shipped
          - {order_id: 'O3', ordered_at: '2024-01-01', shipped_at: null, delivered_at: null}
          # Edge: delivered same day as ordered (express)
          - {order_id: 'O4', ordered_at: '2024-01-01', shipped_at: '2024-01-01', delivered_at: '2024-01-01'}
    expect:
      rows:
        - {order_id: 'O1', fulfillment_status: 'delivered', days_to_deliver: 4}
        - {order_id: 'O2', fulfillment_status: 'in_transit', days_to_deliver: null}
        - {order_id: 'O3', fulfillment_status: 'processing', days_to_deliver: null}
        - {order_id: 'O4', fulfillment_status: 'delivered', days_to_deliver: 0}
```

## Multiple Input Sources

When your model joins multiple refs:

```yaml
unit_tests:
  - name: test_order_enrichment
    description: Verify order enrichment with customer and product data
    model: fct_orders_enriched
    given:
      - input: ref('stg__orders')
        rows:
          - {order_id: 'O1', customer_id: 'C1', product_id: 'P1', quantity: 2, unit_price: 50}
          - {order_id: 'O2', customer_id: 'C2', product_id: 'P2', quantity: 1, unit_price: 100}
      - input: ref('dim_customers')
        rows:
          - {customer_id: 'C1', customer_tier: 'high_value', discount_rate: 0.1}
          - {customer_id: 'C2', customer_tier: 'low_value', discount_rate: 0}
      - input: ref('dim_products')
        rows:
          - {product_id: 'P1', product_name: 'Widget', category: 'Electronics'}
          - {product_id: 'P2', product_name: 'Gadget', category: 'Electronics'}
    expect:
      rows:
        - {order_id: 'O1', gross_amount: 100, discount_amount: 10, net_amount: 90}
        - {order_id: 'O2', gross_amount: 100, discount_amount: 0, net_amount: 100}
```

## Using Fixture Files

For larger test datasets, use CSV fixtures instead of inline YAML:

### Create Fixture Files

```csv
# tests/fixtures/orders_test_input.csv
order_id,customer_id,subtotal_cents,tax_cents,shipping_cents,discount_code
O001,C1,10000,800,500,
O002,C1,10000,800,500,SAVE10
O003,C2,5000,400,500,FREESHIP
O004,C2,100000,8000,0,SAVE10
```

```csv
# tests/fixtures/discounts_test_input.csv
discount_code,discount_type,discount_value
SAVE10,percent,10
FREESHIP,shipping,100
```

```csv
# tests/fixtures/orders_expected_output.csv
order_id,subtotal,tax,shipping,discount,total
O001,100.00,8.00,5.00,0.00,113.00
O002,100.00,8.00,5.00,10.00,103.00
O003,50.00,4.00,0.00,0.00,54.00
O004,1000.00,80.00,0.00,100.00,980.00
```

### Reference Fixtures in Unit Test

```yaml
unit_tests:
  - name: test_order_total_calculation
    description: Verify order totals with various discount scenarios
    model: fct_orders
    given:
      - input: ref('stg__orders')
        format: csv
        fixture: orders_test_input
      - input: ref('stg__discounts')
        format: csv
        fixture: discounts_test_input
    expect:
      format: csv
      fixture: orders_expected_output
```

## Testing Specific Columns

When you only care about certain output columns:

```yaml
unit_tests:
  - name: test_status_logic_only
    description: Only verify status derivation, ignore other columns
    model: fct_orders
    given:
      - input: ref('stg__orders')
        rows:
          - {order_id: 'O1', status_code: 1}
          - {order_id: 'O2', status_code: 2}
          - {order_id: 'O3', status_code: 99}
    expect:
      rows:
        - {order_id: 'O1', status_name: 'pending'}
        - {order_id: 'O2', status_name: 'completed'}
        - {order_id: 'O3', status_name: 'unknown'}
    overrides:
      # Only compare these columns
      columns:
        - order_id
        - status_name
```

## Mocking Current Timestamps

For models that use `current_date` or `current_timestamp`:

```yaml
unit_tests:
  - name: test_days_since_calculation
    description: Verify days_since_last_order calculation
    model: dim_customers
    overrides:
      macros:
        # Mock current_date to a fixed value
        current_date: "cast('2024-06-15' as date)"
    given:
      - input: ref('stg__customers')
        rows:
          - {customer_id: 'C1', last_order_at: '2024-06-10'}
          - {customer_id: 'C2', last_order_at: '2024-05-15'}
    expect:
      rows:
        - {customer_id: 'C1', days_since_last_order: 5}
        - {customer_id: 'C2', days_since_last_order: 31}
```

## Testing Incremental Logic

Unit tests run against the model's full SQL, but you can test incremental-specific branches:

```yaml
unit_tests:
  - name: test_incremental_merge_logic
    description: Verify incremental update handles existing records
    model: fct_orders
    overrides:
      # Force incremental mode
      is_incremental: true
    given:
      - input: ref('stg__orders')
        rows:
          - {order_id: 'O1', status: 'shipped', updated_at: '2024-01-02'}  # Update existing
          - {order_id: 'O2', status: 'pending', updated_at: '2024-01-02'}  # New record
      - input: this  # The existing table (for incremental)
        rows:
          - {order_id: 'O1', status: 'pending', updated_at: '2024-01-01'}
    expect:
      rows:
        - {order_id: 'O1', status: 'shipped'}  # Updated
        - {order_id: 'O2', status: 'pending'}  # Inserted
```

## Running Unit Tests

```bash
# Run all unit tests
dbt test --select "test_type:unit"

# Run unit tests for a specific model
dbt test --select "dim_customers,test_type:unit"

# Run a specific unit test by name
dbt test --select "test_customer_tier_assignment"

# Run unit tests with verbose output
dbt test --select "test_type:unit" --log-level debug
```

## Best Practices

**Do:**
- Test boundary conditions (exact thresholds, zero, negative)
- Test null handling explicitly
- Use descriptive test names that explain the scenario
- Keep test data minimal—only include rows needed to test the logic
- Group related tests in the same YAML file as the model

**Don't:**
- Test trivial logic (simple renames, type casts)
- Duplicate tests that are better handled by generic tests (uniqueness, not null)
- Create overly complex fixtures—if you need 50 rows, question if unit testing is the right approach
- Forget to test error/edge cases (what happens with bad data?)

## Complete Example

```yaml
# models/marts/core/_core__models.yml
version: 2

models:
  - name: dim_customers
    description: Customer dimension with behavioral segments

unit_tests:
  - name: test_customer_tier_assignment
    description: Basic tier assignment based on lifetime revenue
    model: dim_customers
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C1', lifetime_revenue: 1500}
          - {customer_id: 'C2', lifetime_revenue: 500}
          - {customer_id: 'C3', lifetime_revenue: 50}
    expect:
      rows:
        - {customer_id: 'C1', customer_tier: 'high_value'}
        - {customer_id: 'C2', customer_tier: 'medium_value'}
        - {customer_id: 'C3', customer_tier: 'low_value'}

  - name: test_customer_tier_boundaries
    description: Verify exact boundary values
    model: dim_customers
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C1', lifetime_revenue: 1000}
          - {customer_id: 'C2', lifetime_revenue: 999.99}
          - {customer_id: 'C3', lifetime_revenue: 100}
          - {customer_id: 'C4', lifetime_revenue: 99.99}
    expect:
      rows:
        - {customer_id: 'C1', customer_tier: 'high_value'}
        - {customer_id: 'C2', customer_tier: 'medium_value'}
        - {customer_id: 'C3', customer_tier: 'medium_value'}
        - {customer_id: 'C4', customer_tier: 'low_value'}

  - name: test_customer_status_with_nulls
    description: Verify status derivation handles null dates
    model: dim_customers
    overrides:
      macros:
        current_date: "cast('2024-06-15' as date)"
    given:
      - input: ref('int_customers__enriched')
        rows:
          - {customer_id: 'C1', last_order_at: '2024-06-10', total_orders: 5}
          - {customer_id: 'C2', last_order_at: '2024-03-01', total_orders: 2}
          - {customer_id: 'C3', last_order_at: null, total_orders: 0}
    expect:
      rows:
        - {customer_id: 'C1', customer_status: 'active'}
        - {customer_id: 'C2', customer_status: 'churned'}
        - {customer_id: 'C3', customer_status: 'never_purchased'}
```
