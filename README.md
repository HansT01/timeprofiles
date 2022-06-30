# timeprofiles

This library is designed to assist in quickly debugging bottlenecks in both single-threaded and multi-threaded operations. 

## Installation

```
python -m pip install timeprofiles
```

## Overview

It contains a class called **TimeProfileCollection** for easily storing the time taken for each method to complete, and displaying it as either a table or a diagram. The TimeProfiler class provides two static decorator methods for profiling: one for profiling the entire class, and one for profiling individual methods.

```python
@timeprofiles.profile_class_methods
@timeprofiles.profile_method
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

![plot_profiles example figure](https://raw.githubusercontent.com/HansT01/timeprofiles/main/assets/images/example_fig.png)

## Example usages

The **profile_method** decorator is applied on individual methods or functions.

```python
import timeprofiles as tp
    
class ExampleClass:
    @tp.profile_method
    def my_method():
        # Method content

    @tp.profile_method
    def my_other_method():
        # Method content
```

Alternatively, the **profile_class_methods** decorator can be used to apply the **profile_method** decorator on all class methods. This can be used in conjunction with **profile_ignore** to filter out methods you don't want to profile.

```python
import timeprofiles as tp

@tp.profile_class_methods
class ExampleClass:
    def my_method():
        # Method content

    @tp.profile_ignore
    def my_other_method():
        # Method content
```

Another way of using the profiling decorators is to apply it directly onto an object. In the following example, only the methods called from the example_object will be profiled.

```python
example_obj = tp.profile_class_methods(ExampleClass())
```

After adding the decorators and calling the methods, the **display_profiles** or the **plot_profiles** static methods can be called to visualize the time profiles.

```python
tp.display_profiles(order_by=tp.ORDER_BY_AVERAGE, reverse=False, full_name=True)
tp.plot_profiles()
```

## Known issues

Despite being able to add **profile_class_methods** to an object, **profile_ignore** cannot be used since its implementation relies on attributes, which cannot be updated on objects.

```python
# THIS WILL NOT WORK
tp.profile_ignore(example_obj)
```