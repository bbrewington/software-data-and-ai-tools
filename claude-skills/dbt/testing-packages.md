# Package Integration Tests

When developing dbt packages (reusable macros, generic tests, or models), integration tests validate that your package works correctly across different warehouse targets.

## When You Need This

This guide is for **package authors** who are building:
- Reusable macros (like dbt-utils)
- Custom generic tests
- Cross-database utility functions
- Installable models (like Fivetran source packages)

If you're building a standard dbt project (not a package), see the other testing guides instead.

## Project Structure

```
my_dbt_package/
├── macros/
│   ├── my_macro.sql
│   └── my_generic_test.sql
├── models/                         # Optional: if package includes models
│   └── ...
├── integration_tests/              # Nested dbt project for testing
│   ├── dbt_project.yml
│   ├── profiles.yml                # Or use environment variables
│   ├── packages.yml                # References parent package
│   ├── seeds/
│   │   ├── input_data.csv          # Mock input data
│   │   └── expected_output.csv     # Expected results
│   ├── models/
│   │   └── test_my_macro.sql       # Models that exercise your macros
│   └── macros/
│       └── test_macro_unit.sql     # Macro unit tests
├── dbt_project.yml                 # Package definition
├── packages.yml                    # Package dependencies
├── supported_adapters.env          # SUPPORTED_ADAPTERS=postgres,snowflake,bigquery
└── tox.ini                         # Test automation
```

## Integration Test Pattern

The standard pattern involves three components:

### 1. Seed Files (Mock Input Data)

```csv
# integration_tests/seeds/input_customers.csv
customer_id,email,created_at
1,alice@example.com,2024-01-01
2,BOB@EXAMPLE.COM,2024-01-02
3,  charlie@example.com  ,2024-01-03
4,,2024-01-04
```

### 2. Models (Exercise Your Macros)

```sql
-- integration_tests/models/test_clean_email.sql
-- Tests the clean_email macro from the package

select
    customer_id,
    {{ clean_email('email') }} as email_cleaned
from {{ ref('input_customers') }}
```

### 3. Expected Output Seeds

```csv
# integration_tests/seeds/expected_clean_email.csv
customer_id,email_cleaned
1,alice@example.com
2,bob@example.com
3,charlie@example.com
4,
```

### 4. Tests (Validate Results)

```yaml
# integration_tests/models/_models.yml
version: 2

models:
  - name: test_clean_email
    description: Integration test for clean_email macro
    tests:
      - dbt_utils.equality:
          compare_model: ref('expected_clean_email')
```

## Configuration

### Integration Tests dbt_project.yml

```yaml
# integration_tests/dbt_project.yml
name: my_package_integration_tests
version: '1.0.0'
config-version: 2

profile: integration_tests

# Reference the parent package
vars:
  # Allow overriding source schema for testing
  my_package_source_database: "{{ target.database }}"
  my_package_source_schema: "{{ target.schema }}"

seeds:
  my_package_integration_tests:
    +schema: "{{ target.schema }}"
```

### Integration Tests packages.yml

```yaml
# integration_tests/packages.yml
packages:
  # Reference parent package by local path
  - local: ../
  
  # Include test utilities
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
```

### Profiles Configuration

```yaml
# integration_tests/profiles.yml
integration_tests:
  target: postgres
  outputs:
    postgres:
      type: postgres
      host: "{{ env_var('POSTGRES_HOST', 'localhost') }}"
      port: 5432
      user: "{{ env_var('POSTGRES_USER', 'postgres') }}"
      password: "{{ env_var('POSTGRES_PASSWORD', 'postgres') }}"
      dbname: "{{ env_var('POSTGRES_DB', 'postgres') }}"
      schema: dbt_integration_tests
      threads: 4

    snowflake:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      schema: dbt_integration_tests
      threads: 4

    bigquery:
      type: bigquery
      method: service-account
      project: "{{ env_var('GCP_PROJECT') }}"
      dataset: dbt_integration_tests
      keyfile: "{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}"
      threads: 4
```

## Running Integration Tests

### Manual Execution

```bash
# From integration_tests directory
cd integration_tests

# Install dependencies (including the parent package)
dbt deps

# Load seed data
dbt seed --target postgres

# Run models that test the package
dbt run --target postgres

# Run tests to validate results
dbt test --target postgres

# Or all at once
dbt build --target postgres --full-refresh
```

### Automated with tox

```ini
# tox.ini (in package root)
[tox]
envlist = dbt_integration_{postgres,snowflake,bigquery}
skipsdist = true

[testenv]
changedir = integration_tests
allowlist_externals = dbt
skip_install = true
passenv = 
    DBT_*
    POSTGRES_*
    SNOWFLAKE_*
    GCP_*
    GOOGLE_APPLICATION_CREDENTIALS

[testenv:dbt_integration_postgres]
commands =
    dbt --version
    dbt debug --target postgres
    dbt deps --target postgres
    dbt build --target postgres --full-refresh

[testenv:dbt_integration_snowflake]
commands =
    dbt --version
    dbt debug --target snowflake
    dbt deps --target snowflake
    dbt build --target snowflake --full-refresh

[testenv:dbt_integration_bigquery]
commands =
    dbt --version
    dbt debug --target bigquery
    dbt deps --target bigquery
    dbt build --target bigquery --full-refresh
```

```bash
# Run all adapters
tox

# Run specific adapter
tox -e dbt_integration_postgres

# Run with fresh virtual environment
tox -r -e dbt_integration_postgres
```

### Supported Adapters File

```bash
# supported_adapters.env
SUPPORTED_ADAPTERS=postgres,snowflake,bigquery,redshift
```

## Macro Unit Tests

For testing macro logic directly without building models, use `dbt run-operation`:

### Create Test Macro

```sql
-- integration_tests/macros/test_to_literal.sql

{% macro test_to_literal() %}
    {% set test_cases = [
        {"input": "hello", "expected": "'hello'"},
        {"input": "it's a test", "expected": "'it's a test'"},
        {"input": "", "expected": "''"},
        {"input": "123", "expected": "'123'"},
    ] %}
    
    {% set failures = [] %}
    
    {% for test in test_cases %}
        {% set result = to_literal(test.input) %}
        {% if result != test.expected %}
            {% do failures.append({
                "input": test.input,
                "expected": test.expected,
                "actual": result
            }) %}
        {% endif %}
    {% endfor %}
    
    {% if failures | length > 0 %}
        {% for f in failures %}
            {{ log("FAILED: input='" ~ f.input ~ "' expected='" ~ f.expected ~ "' got='" ~ f.actual ~ "'", info=true) }}
        {% endfor %}
        {{ exceptions.raise_compiler_error("test_to_literal: " ~ failures | length ~ " test(s) failed") }}
    {% else %}
        {{ log("test_to_literal: all " ~ test_cases | length ~ " tests passed", info=true) }}
    {% endif %}
{% endmacro %}
```

### Run Macro Unit Test

```bash
dbt run-operation test_to_literal --target postgres
```

### Comprehensive Macro Testing

```sql
-- integration_tests/macros/test_date_helpers.sql

{% macro test_date_helpers() %}
    {{ log("Running date helper tests...", info=true) }}
    
    {# Test fiscal_quarter macro #}
    {% set q1_result = fiscal_quarter('2024-01-15') %}
    {% if q1_result != 'Q1' %}
        {{ exceptions.raise_compiler_error("fiscal_quarter('2024-01-15') expected 'Q1', got '" ~ q1_result ~ "'") }}
    {% endif %}
    
    {# Test is_weekend macro #}
    {% set weekend_result = is_weekend('2024-01-13') %}  {# Saturday #}
    {% if weekend_result != true %}
        {{ exceptions.raise_compiler_error("is_weekend('2024-01-13') expected true, got " ~ weekend_result) }}
    {% endif %}
    
    {{ log("All date helper tests passed!", info=true) }}
{% endmacro %}
```

## CI/CD Configuration

### GitHub Actions

```yaml
# .github/workflows/integration_tests.yml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  DBT_PROFILES_DIR: ./integration_tests

jobs:
  postgres:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: pip install dbt-postgres

      - name: Run integration tests
        working-directory: integration_tests
        env:
          POSTGRES_HOST: localhost
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        run: |
          dbt deps
          dbt build --target postgres --full-refresh

  snowflake:
    runs-on: ubuntu-latest
    # Only run on main branch (Snowflake costs money)
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: pip install dbt-snowflake

      - name: Run integration tests
        working-directory: integration_tests
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
        run: |
          dbt deps
          dbt build --target snowflake --full-refresh

  bigquery:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: pip install dbt-bigquery

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Run integration tests
        working-directory: integration_tests
        env:
          GCP_PROJECT: ${{ secrets.GCP_PROJECT }}
        run: |
          dbt deps
          dbt build --target bigquery --full-refresh
```

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  integration-test-postgres:
    docker:
      - image: cimg/python:3.11
      - image: cimg/postgres:15.0
        environment:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
    
    steps:
      - checkout
      - run:
          name: Install dbt
          command: pip install dbt-postgres
      - run:
          name: Run integration tests
          working_directory: integration_tests
          environment:
            POSTGRES_HOST: localhost
            POSTGRES_USER: postgres
            POSTGRES_PASSWORD: postgres
            POSTGRES_DB: postgres
          command: |
            dbt deps
            dbt build --target postgres --full-refresh

workflows:
  test:
    jobs:
      - integration-test-postgres
```

## Testing Cross-Database Compatibility

### Adapter-Specific Macros

```sql
-- macros/get_current_timestamp.sql

{% macro get_current_timestamp() %}
    {{ return(adapter.dispatch('get_current_timestamp', 'my_package')()) }}
{% endmacro %}

{% macro default__get_current_timestamp() %}
    current_timestamp
{% endmacro %}

{% macro snowflake__get_current_timestamp() %}
    current_timestamp()
{% endmacro %}

{% macro bigquery__get_current_timestamp() %}
    current_timestamp()
{% endmacro %}
```

### Testing Dispatched Macros

```sql
-- integration_tests/models/test_get_current_timestamp.sql

select
    {{ get_current_timestamp() }} as current_ts,
    case 
        when {{ get_current_timestamp() }} is not null then 'pass'
        else 'fail'
    end as test_result
```

## Best Practices

**Do:**
- Test against multiple database targets (at least Postgres + your primary target)
- Use seeds for reproducible test data
- Include edge cases in seed data (nulls, empty strings, special characters)
- Keep integration tests fast (small seed files)
- Use `dbt_utils.equality` to compare model output to expected seeds
- Document expected behavior in test descriptions

**Don't:**
- Commit credentials to the repository
- Run expensive cloud tests on every PR (use Postgres for PR checks)
- Create seeds with thousands of rows (integration tests should be fast)
- Skip testing on the adapters you claim to support

## Complete Example: Testing a Macro Package

```sql
-- macros/string_utils.sql

{% macro clean_string(column_name) %}
    lower(trim({{ column_name }}))
{% endmacro %}

{% macro mask_email(column_name) %}
    concat(
        left({{ column_name }}, 2),
        '***@',
        split_part({{ column_name }}, '@', 2)
    )
{% endmacro %}
```

```csv
# integration_tests/seeds/input_strings.csv
id,raw_email,raw_name
1,ALICE@EXAMPLE.COM,  Alice Smith  
2,bob@test.org,Bob Jones
3,,  
```

```csv
# integration_tests/seeds/expected_string_utils.csv
id,clean_name,masked_email
1,alice smith,al***@example.com
2,bob jones,bo***@test.org
3,,
```

```sql
-- integration_tests/models/test_string_utils.sql

select
    id,
    {{ clean_string('raw_name') }} as clean_name,
    {{ mask_email('raw_email') }} as masked_email
from {{ ref('input_strings') }}
where raw_email is not null

union all

select
    id,
    {{ clean_string('raw_name') }} as clean_name,
    null as masked_email
from {{ ref('input_strings') }}
where raw_email is null
```

```yaml
# integration_tests/models/_models.yml
version: 2

models:
  - name: test_string_utils
    description: Integration test for string utility macros
    tests:
      - dbt_utils.equality:
          compare_model: ref('expected_string_utils')
```
