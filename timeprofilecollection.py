import inspect
import numpy as np
from matplotlib import pyplot as plt
from functools import wraps
from time import perf_counter
from tabulate import tabulate
from operator import itemgetter

from timeprofile import TimeProfile


class TimeProfileCollection:
    """TimeProfiler is a class for quickly storing the time taken for each method to complete, and displaying it as an easy-to-read table."""

    profiles: dict[function, type[TimeProfile]] = {}

    @staticmethod
    def reset():
        """Resets all profiles."""
        TimeProfileCollection.profiles = {}

    @staticmethod
    def profile_method(f):
        """Method decorator that adds the decorated method to the list of time profiles."""

        @wraps(f)
        def wrapper(*args, **kwargs):
            profiles = TimeProfileCollection.profiles
            if f not in profiles:
                profiles[f] = TimeProfile()

            start = perf_counter()
            result = f(*args, **kwargs)
            end = perf_counter()
            profiles[f].add(start, end)
            return result

        return wrapper

    @staticmethod
    def profile_class_methods(cls):
        """Class decorator for adding profile_method to all contained methods within the class."""

        # https://stackoverflow.com/a/57368193
        for name, method in inspect.getmembers(cls):
            if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
                continue
            setattr(cls, name, TimeProfileCollection.profile_method(method))
        return cls

    ORDER_BY_NAME = 0
    ORDER_BY_CALLS = 1
    ORDER_BY_AVERAGE = 2
    ORDER_BY_LONGEST = 3
    ORDER_BY_BOTTLENECK = 4

    @staticmethod
    def display_profiles(order_by=0, reverse=False, full_name=False):
        """Prints out all profiles to console as a table, ordered by the order_by parameter.

        Args:
            order_by (int, optional): Optional ordering using provided ORDER_BY_ fields. Defaults to ORDER_BY_NAME.
            reverse (bool, optional): Reverse row order? Defaults to False.
            full_name (bool, optional): Display full name of methods? Defaults to False.
        """
        profiles = TimeProfileCollection.profiles
        table = []
        for key in profiles:
            profile = profiles[key]
            n = len(profile)
            elapsed_arr = profile.get_elapsed_arr()
            row = [
                key.__qualname__ if full_name else key.__name__,
                n,
                round(np.sum(elapsed_arr) / n * 1000, 2),
                round(elapsed_arr.max() * 1000, 2),
                round(profile.get_bottleneck() * 1000, 2),
            ]
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
        profiles = TimeProfileCollection.profiles
        earliest, latest = TimeProfileCollection.__get_time_range()
        sorted_profiles = {k: v for k, v in sorted(profiles.items(), key=lambda item: item[1].min(), reverse=reverse)}
        TimeProfileCollection.__plot_data(sorted_profiles, earliest, latest, **kwargs)

    @staticmethod
    def __get_time_range() -> tuple[float, float]:
        """Gets the earliest and latest times for current profiles.

        Returns:
            tuple[float, float]: earliest and latest times in seconds
        """
        profiles = TimeProfileCollection.profiles
        earliest = min([profile.min() for profile in profiles.values()])
        latest = max([profile.max() for profile in profiles.values()])
        return earliest, latest

    @staticmethod
    def __plot_data(
        data: dict[function, type[TimeProfile]],
        earliest: float,
        latest: float,
        full_name=False,
        alpha=0.4,
        fc="#000",
        ec="#000",
        **kwargs,
    ):
        """Plots the data using the matplotlib library.

        Args:
            data (Dict[Callable, List[Tuple[float, float]]]): Data object
            xmin (float): lower x limit
            xmax (float): upper x limit
            full_name (bool, optional): Display full name of methods? Defaults to False.
            **kwargs: ~matplotlib.patches.Polygon properties
        """
        fig, ax = plt.subplots()
        width = 1

        ax.set_xlim(0, latest - earliest)

        for i, pair in enumerate(data.items()):
            starts_arr, ends_arr = pair[1].get_squashed_arr(earliest, latest)
            for x0, x1 in zip(starts_arr, ends_arr):
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
        ax.set_yticklabels([key.__qualname__ if full_name else key.__name__ for key in data.keys()])

        ax.set_title("Method activity gantt chart")
        ax.set_xlabel("Time elapsed (s)")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    from random import randint
    from time import sleep
    import concurrent.futures

    TPC = TimeProfileCollection

    @TPC.profile_class_methods
    class ExampleClass:
        def method_a(self, num):
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                # Run method b as threads
                fs = (executor.submit(self.method_b) for _ in range(0, num))

                # Wait for all futures to complete
                for f in concurrent.futures.as_completed(fs):
                    pass

            self.method_d()

        def method_b(self):
            sleep(randint(0, 10000) / 10000)
            self.method_c()

        def method_c(self):
            sleep(randint(0, 10000) / 10000)

        def method_d(self):
            sleep(randint(0, 10000) / 10000)

        @staticmethod
        def method_e():
            sleep(randint(0, 10000) / 10000)

    example1 = ExampleClass()
    example1.method_a(5)

    TPC.display_profiles(TPC.ORDER_BY_NAME)
    TPC.plot_profiles()
