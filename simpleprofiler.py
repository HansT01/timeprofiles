from functools import wraps
import inspect
import sys
from time import perf_counter
from typing import Dict, Any, Callable, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from tabulate import tabulate
from operator import itemgetter


class TimeProfiler:
    """TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table."""

    profiles: Dict[Callable, List[Tuple[float, float]]] = {}

    ORDER_BY_NAME = 0
    ORDER_BY_CALLS = 1
    ORDER_BY_AVERAGE = 2
    ORDER_BY_LONGEST = 3
    ORDER_BY_TOTAL_ELAPSED = 4

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

            profiles = TimeProfiler.profiles
            if f not in profiles:
                profiles[f] = []
            profiles[f] += [(start, end)]

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
        profiles = TimeProfiler.profiles
        table = []
        for key in profiles:
            row = []

            longest = 0
            sum = 0

            earliest = sys.maxsize
            latest = 0

            for start, end in profiles[key]:
                elapsed = end - start
                sum += elapsed
                if elapsed > longest:
                    longest = elapsed
                if start < earliest:
                    earliest = start
                if end > latest:
                    latest = end

            calls = len(profiles[key])
            avg = sum / calls
            total = latest - earliest

            row += [key.__name__]
            row += [calls]
            row += [round(avg * 1000, 2)]
            row += [round(longest * 1000, 2)]
            row += [round(total * 1000, 2)]

            table += [row]

        if order_by == TimeProfiler.ORDER_BY_NAME:
            table.sort(key=itemgetter(order_by))
        else:
            table.sort(key=itemgetter(order_by), reverse=True)

        print(
            tabulate(
                table,
                headers=[
                    "Name",
                    "Calls",
                    "Average (ms)",
                    "Longest (ms)",
                    "Total elapsed (ms)",
                ],
                floatfmt=",.2f",
            )
        )

    @staticmethod
    def plot_profiles():
        earliest, latest = TimeProfiler.__get_time_range()
        new_profiles = TimeProfiler.__squash_profiles(earliest, latest)
        TimeProfiler.__plot_data(new_profiles, 0, latest - earliest)

    @staticmethod
    def __get_time_range() -> Tuple[float, float]:
        profiles = TimeProfiler.profiles

        # Get earliest and latest times
        earliest = sys.maxsize
        latest = 0
        for key in profiles:
            for start, end in profiles[key]:
                if start < earliest:
                    earliest = start
                if end > latest:
                    latest = end

        return earliest, latest

    @staticmethod
    def __squash_profiles(
        earliest: float,
        latest: float,
    ) -> Dict[str, List[Tuple[float, float]]]:

        profiles = TimeProfiler.profiles
        new_profiles: Dict[str, List[Tuple[float, float]]] = {}
        time_frame = latest - earliest

        # Fill in new_profiles with normalized times
        for key in profiles:
            new_key = key.__name__
            if new_key not in new_profiles:
                new_profiles[new_key] = []

            for start, end in profiles[key]:
                new_start = (start - earliest) / time_frame
                new_end = (end - earliest) / time_frame
                new_profiles[new_key] += [(new_start, new_end)]

        return new_profiles

    @staticmethod
    def __plot_data(
        data: Dict[Callable, List[Tuple[float, float]]], ymin: float, ymax: float
    ):
        fig, ax = plt.subplots()
        width = 1

        ax.set_ylim(ymin, ymax)

        for i, pair in enumerate(data.items()):
            for value in pair[1]:
                y0, y1 = value
                ax.axvspan(xmin=i - width / 2, xmax=i + width / 2, ymin=y0, ymax=y1)

        ax.set_xticks(np.arange(0, len(data)))
        ax.set_xticklabels(data.keys())
        plt.show()


if __name__ == "__main__":

    from random import randint
    from time import sleep

    @TimeProfiler.profile_class_methods
    class ExampleClass:
        def method_b(self):
            sleep(randint(0, 1000) / 10000)

        @staticmethod
        def method_a():
            sleep(randint(0, 1000) / 10000)

        def method_c(self):
            sleep(randint(0, 2000) / 10000)

    calc = ExampleClass()

    for _ in range(0, 5):
        ExampleClass.method_a()
        calc.method_b()

    for _ in range(0, 5):
        calc.method_b()

    for _ in range(0, 5):
        calc.method_c()

    TimeProfiler.display_profiles(TimeProfiler.ORDER_BY_NAME)
    TimeProfiler.plot_profiles()
