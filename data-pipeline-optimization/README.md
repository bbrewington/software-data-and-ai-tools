# Data Pipeline Optimization

Taken from Dagster article: https://dagster.io/blog/when-and-when-not-to-optimize-data-pipelines, with corresponding GitHub repo: https://github.com/C00ldudeNoonan/blog-code-snippets/tree/main

## Whether to Optimize

Before touching any code, answer these questions:
1. Am I being yelled at about this? --> Probably should take care of it then.
2. How often does this pipeline run?
    - Once a day? Optimization ROI is probably low
    - Every 5 minutes? The sweet spot
    - Ad-hoc analysis? Don't bother
3. What's the actual business impact?
    - Blocks downstream pipelines? High impact
    - Delays morning dashboard refresh? Medium impact
    - Historical backfill that runs overnight? Low impact
4. Is it even slow?
    - <5 minutes for hourly job? That's fine
    - 4 hours for daily job overnight? Also probably fine
    - 15 minutes for something users are waiting on? Problem

Use this formula to decide:
```text
Runtime Impact = (Pipeline Frequency × Time Saved) × Business Criticality

If Impact < 2 hours/week saved: Don't optimize yet.
If Impact > 1 day/week saved: Optimize now.
```

## (Mostly Python) Profiling tools

- `cProfile`: Built into Python for CPU profiling
- `line_profiler`: Line-by-line profiling for finding hot spots
- `memory_profiler`: Memory usage profiling
- `py-spy`: Production profiling without code changes
- Warehouse query profilers: Snowflake Query Profile, BigQuery Execution Details, Databricks Spark UI

## Python: Useful libraries

- `tenacity`: Exponential backoff and retry logic for resilient I/O operations
- `orjson`: Faster JSON parsing (2-3x faster than standard library)
- `polars`: Fast dataframe library (alternative to pandas)
- `pyspark`: Distributed processing for large datasets

## Use cProfile for CPU-bound operations

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

## Use memory_profiler for memory issues

```python
from memory_profiler import profile

@profile
def load_giant_dataframe():
    """This will show line-by-line memory usage."""
    df = pd.read_csv("10gb_file.csv")  # This will show line-by-line memory
    return df.groupby("key").sum()
```