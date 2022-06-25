from functools import wraps
import inspect
import sys
from time import perf_counter
from typing import Any, Dict, Callable, List, Tuple
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
            profiles = TimeProfiler.profiles
            if f not in profiles:
                profiles[f] = []

            # List used over tuples to guarantee call order
            pair = [None, None]
            profiles[f] += [pair]

            pair[0] = perf_counter()
            result = f(*args, **kwargs)
            pair[1] = perf_counter()
            return result

        return wrapper

    @staticmethod
    def profile_class_methods(cls):
        """Class decorator for adding profile_method to all contained methods within the class."""

        # https://stackoverflow.com/a/57368193
        for name, method in inspect.getmembers(cls):
            if (
                not inspect.ismethod(method) and not inspect.isfunction(method)
            ) or inspect.isbuiltin(method):
                continue
            setattr(cls, name, TimeProfiler.profile_method(method))
        return cls

    @staticmethod
    def display_profiles(order_by=0, reverse=False):
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

            calls = len(profiles[key])
            avg = sum / calls
            bottleneck = TimeProfiler.__calculate_bottleneck(profiles[key])

            row += [key.__name__]
            row += [calls]
            row += [round(avg * 1000, 2)]
            row += [round(longest * 1000, 2)]
            row += [round(bottleneck * 1000, 2)]

            table += [row]

        table.sort(key=itemgetter(order_by), reverse=reverse)

        print(
            tabulate(
                table,
                headers=[
                    "Name",
                    "Calls",
                    "Average (ms)",
                    "Longest (ms)",
                    "Bottleneck (ms)",
                ],
                floatfmt=",.2f",
            )
        )

    @staticmethod
    def plot_profiles(reverse=False, **kwargs):
        """Plots the profiles as a range bar chart, ordered by first call.

        Args:
            reverse (bool, optional): Reverse order? Defaults to False.
            **kwargs: ~matplotlib.patches.Polygon properties
        """
        earliest, latest = TimeProfiler.__get_time_range()
        new_profiles = TimeProfiler.__squash_profiles(earliest, latest)

        # Sort by first 'start' time
        sorted_profiles = dict(
            sorted(new_profiles.items(), key=lambda item: item[1], reverse=reverse)
        )
        TimeProfiler.__plot_data(sorted_profiles, 0, latest - earliest, **kwargs)

    @staticmethod
    def __get_time_range() -> Tuple[float, float]:
        """Returns the time range across all profiles.

        Returns:
            Tuple[float, float]: earliest time (s), latest time (s)
        """
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
        """Prepares the profiles to be read by __plot_data.

        Args:
            earliest (float): Starting time
            latest (float): Ending time

        Returns:
            Dict[str, List[Tuple[float, float]]]: Data object
        """

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
    def __calculate_bottleneck(profile: List[Tuple[float, float]]) -> float:
        n = len(profile)

        starts: List[float] = []
        ends: List[float] = []
        for start, end in profile:
            starts += [start]
            ends += [end]
        starts.sort()
        ends.sort()

        bottleneck = 0
        j = 0
        for i in range(0, n):
            if i == n - 1 or starts[i + 1] > ends[i]:
                bottleneck += ends[i] - starts[j]
                j = i + 1
        return bottleneck

    @staticmethod
    def __plot_data(
        data: Dict[Callable, List[Tuple[float, float]]],
        xmin: float,
        xmax: float,
        alpha=0.4,
        fc="#000",
        ec="#000",
        **kwargs
    ):
        """Plots the data using the matplotlib library.

        Args:
            data (Dict[Callable, List[Tuple[float, float]]]): Data object
            xmin (float): lower x limit
            xmax (float): upper x limit
            **kwargs: ~matplotlib.patches.Polygon properties
        """
        fig, ax = plt.subplots()
        width = 1

        ax.set_xlim(xmin, xmax)

        for i, pair in enumerate(data.items()):
            for value in pair[1]:
                x0, x1 = value
                ax.axhspan(
                    ymin=i - width / 2,
                    ymax=i + width / 2,
                    xmin=x0,
                    xmax=x1,
                    alpha=alpha,
                    fc=fc,
                    ec=ec,
                    **kwargs,
                )

        ax.set_yticks(np.arange(0, len(data)))
        ax.set_yticklabels(data.keys())

        ax.set_title("Time profile ranges")
        ax.set_xlabel("Time elapsed (s)")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    from random import randint
    from time import sleep
    import concurrent.futures

    @TimeProfiler.profile_class_methods
    class ExampleClass:
        def method_a(self, num):
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                fs = (executor.submit(self.method_b) for _ in range(0, num))
                for f in concurrent.futures.as_completed(fs):
                    pass

        def method_b(self):
            sleep(randint(0, 10000) / 10000)
            self.method_c()

        def method_c(self):
            sleep(randint(0, 10000) / 10000)

        def method_d(self):
            sleep(randint(0, 10000) / 10000)

    calc = ExampleClass()

    # calc.method_a(10)

    for _ in range(0, 5):
        calc.method_c()
        calc.method_d()

    for _ in range(0, 5):
        calc.method_c()

    TimeProfiler.display_profiles(TimeProfiler.ORDER_BY_NAME)
    TimeProfiler.plot_profiles()
