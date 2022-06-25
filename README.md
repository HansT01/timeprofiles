# Simple Time Profiler
TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table.
The TimeProfiler class provides two static decorator methods for profiling: one for profiling the entire class, and one for profiling a single method.

```python
@TimeProfiler.profile_class_methods
@TimeProfiler.profile_method
```

The **display_profiles** static method can then be called to display all time profiles, ordered by a specified column.

```
Name        Calls    Average (ms)    Longest (ms)    Total elapsed (ms)
--------  -------  --------------  --------------  --------------------
method_a        5           50.76          107.96                502.00
method_b       10           52.78           93.93                758.04
method_c        5          111.80          155.61                559.05
```

The **plot_profiles** static method can then be called to plot all time profiles as ranges, ordered by earliest method call.

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
TimeProfiler.plot_profiles(reverse=True)
```