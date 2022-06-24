# Simple Time Profiler
TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table.
The TimeProfiler class provides two static decorator methods for profiling, one for profiling the entire class, and one for profiling a single method.

```python
@TimeProfiler.profile_class_methods
@TimeProfiler.profile_method
```

The display_profiles static method can then be called to display all time profiles, ordered by a specified column.

```
Name          Calls    Average (ms)    Longest (ms)
----------  -------  --------------  --------------
function_a        5           69.62           93.37
function_b        5           61.61           77.92
function_c        5           43.74           62.15
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
