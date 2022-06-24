from functools import wraps
import inspect
from time import perf_counter
from typing import Dict, Any, Callable
from tabulate import tabulate
from operator import itemgetter


class TimeProfiler:
    """TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table."""
    
    profiles = {}

    ORDER_BY_NAME = 0
    ORDER_BY_CALLS = 1
    ORDER_BY_AVERAGE = 2
    ORDER_BY_LONGEST = 3

    @staticmethod
    def reset():
        """Resets all profiles."""
        TimeProfiler.profiles = {}

    @staticmethod
    def profile_method(f):
        """Method decorator that adds the decorated method to the list of time profiles."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            result = f(*args, **kwargs)
            end = perf_counter()

            times = TimeProfiler.profiles
            if f not in times:
                times[f] = []
            times[f] += [(end - start) * 1000]

            return result

        return wrapper

    # https://stackoverflow.com/questions/3467526/attaching-a-decorator-to-all-functions-within-a-class/3467879#3467879
    @staticmethod
    def profile_class_methods(cls):
        """Class decorator for adding profile_method to all contained methods within the class."""
        for name, method in inspect.getmembers(cls):
            if (
                not inspect.ismethod(method) and not inspect.isfunction(method)
            ) or inspect.isbuiltin(method):
                continue
            setattr(cls, name, TimeProfiler.profile_method(method))
        return cls

    @staticmethod
    def display_profiles(order_by: int = 0):
        """Prints out all profiles to console as a table, ordered by the order_by parameter.

        Args:
            order_by (int, optional): Optional ordering using provided ORDER_BY_ fields. Defaults to ORDER_BY_NAME.
        """
        times: Dict[Callable, Any] = TimeProfiler.profiles
        table = []
        for key in times:
            row = []

            longest = 0
            sum = 0
            for val in times[key]:
                sum += val
                if val > longest:
                    longest = val

            calls = len(times[key])
            avg = sum / calls

            row += [key.__name__]
            row += [calls]
            row += [round(avg, 2)]
            row += [round(longest, 2)]

            table += [row]

        if order_by == TimeProfiler.ORDER_BY_NAME:
            table.sort(key=itemgetter(order_by))
        else:
            table.sort(key=itemgetter(order_by), reverse=True)

        print(
            tabulate(
                table,
                headers=["Name", "Calls", "Average (ms)", "Longest (ms)"],
                floatfmt=",.2f",
            )
        )


if __name__ == "__main__":

    from random import randint
    from time import sleep

    @TimeProfiler.profile_class_methods
    class ExampleClass:
        @staticmethod
        def function_a():
            sleep(randint(0, 1000) / 10000)

        def function_b(self):
            sleep(randint(0, 1000) / 10000)

        def function_c(self):
            sleep(randint(0, 1000) / 10000)

    calc = ExampleClass()
    for _ in range(0, 5):
        ExampleClass.function_a()
        calc.function_b()
        calc.function_c()

    TimeProfiler.display_profiles(TimeProfiler.ORDER_BY_NAME)
