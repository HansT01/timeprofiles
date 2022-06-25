# Simple Time Profiler
TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table.
The TimeProfiler class provides two static decorator methods for profiling: one for profiling the entire class, and one for profiling a single method.

```python
@TimeProfiler.profile_class_methods
@TimeProfiler.profile_method
```

The **display_profiles** static method is used to display all time profiles, ordered by a specified column.

```
Name        Calls    Average (ms)    Longest (ms)    Bottleneck (ms)
--------  -------  --------------  --------------  -----------------
method_a        1        1,504.80        1,504.80           1,504.80
method_b        5        1,027.98        1,456.32           1,456.32
method_c        5          436.64          757.97           1,115.18
method_d        1           45.95           45.95              45.95
```

The **plot_profiles** static method is used to plot all time profiles as ranges, ordered by earliest method call.

![plot_profiles example figure](/assets/images/example_fig.png)

# Example usages

The **profile_method** decorator is to be applied on methods or functions.

```python
from simpleprofiler import TimeProfiler
    
class ExampleClass:
    @TimeProfiler.profile_method
    def my_method():
        # Method content

    @TimeProfiler.profile_method
    def my_other_method():
        # Method content
```

Alternatively, the **profile_class_methods** decorator can be used to apply the **profile_method** decorator on all class methods.

```python
from simpleprofiler import TimeProfiler

@TimeProfiler.profile_class_methods
class ExampleClass:
    def my_method():
        # Method content

    def my_other_method():
        # Method content
```

After adding the decorators and calling the methods, the **display_profiles** or the **plot_profiles** static methods can be called to visualize the time profiles for each method.

```python
TimeProfiler.display_profiles(order_by=TimeProfiler.ORDER_BY_AVERAGE, reverse=True)
TimeProfiler.plot_profiles(fc="yellow", ec="black")
```