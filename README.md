# Simple Time Profiler
TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table.
The TimeProfiler class provides two static decorator methods for profiling: one for profiling the entire class, and one for profiling a single method.

```python
@TimeProfiler.profile_class_methods
@TimeProfiler.profile_method
```

The display_profiles static method can then be called to display all time profiles, ordered by a specified column.

```
Name        Calls    Average (ms)    Longest (ms)    Total elapsed (ms)
--------  -------  --------------  --------------  --------------------
method_a        5           45.41           71.97                453.34
method_b        5           57.92           94.26                464.53
method_c        5           52.49           76.91                262.49
```

# Example usages

```python
from simpleprofiler import TimeProfiler

@TimeProfiler.profile_class_methods
class ExampleClass:
    # Class content

TimeProfiler.display_profiles(TimeProfiler.ORDER_BY_AVERAGE)
```

```python
from simpleprofiler import TimeProfiler
    
class ExampleClass:
    @TimeProfiler.profile_method
    def my_method():
        # Method content

TimeProfiler.display_profiles(TimeProfiler.ORDER_BY_AVERAGE)
```
