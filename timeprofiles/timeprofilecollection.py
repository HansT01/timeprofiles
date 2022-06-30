import inspect
from typing import Callable
from colorhash import ColorHash
import numpy as np
from matplotlib import pyplot as plt
from functools import wraps
from time import perf_counter
from tabulate import tabulate
from operator import itemgetter

from timeprofiles.timeprofile import TimeProfile


__all__ = [
    "profile_method",
    "profile_class_methods",
    "profile_ignore",
    "clear",
    "print_profiles",
    "plot_profiles",
    "plot_merged",
    "ORDER_BY_NAME",
    "ORDER_BY_CALLS",
    "ORDER_BY_AVERAGE",
    "ORDER_BY_LONGEST",
    "ORDER_BY_BOTTLENECK",
]


profiles: dict[Callable, type[TimeProfile]] = {}


def add(f: Callable, start: float, end: float):
    if f not in profiles:
        profiles[f] = TimeProfile()
    profiles[f].add(start, end)


def clear():
    """Clears all profiles."""
    profiles.clear()


def profile_ignore(f):
    setattr(f, "__profile_ignore__", True)
    return f


def profile_method(f: Callable):
    """Method decorator that adds the decorated method to the list of time profiles."""
    if hasattr(f, "__profile_ignore__"):
        return f

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            result = f(*args, **kwargs)
        finally:
            end = perf_counter()
            add(f, start, end)
        return result

    return wrapper


def profile_class_methods(cls):
    """Class decorator for adding profile_method to all contained methods within the class."""
    if hasattr(cls, "__profile_ignore__"):
        return cls

    # https://stackoverflow.com/a/57368193
    for name, method in inspect.getmembers(cls):
        # if inspect.isbuiltin(method):
        if inspect.ismethod(method) or inspect.isfunction(method):
            setattr(cls, name, profile_method(method))
        if inspect.isclass(method) and name != "__class__":
            setattr(cls, name, profile_class_methods(method))
    return cls


ORDER_BY_NAME = 0
ORDER_BY_CALLS = 1
ORDER_BY_AVERAGE = 2
ORDER_BY_LONGEST = 3
ORDER_BY_BOTTLENECK = 4


def print_profiles(order_by=0, reverse=False, full_name=False):
    """Prints out all profiles to console as a table, ordered by the order_by parameter.

    Args:
        order_by (int, optional): Optional ordering using provided ORDER_BY_ fields. Defaults to ORDER_BY_NAME.
        reverse (bool, optional): Reverse row order? Defaults to False.
        full_name (bool, optional): Display full name of methods? Defaults to False.
    """
    table = []
    for key in profiles:
        profile = profiles[key]
        n = len(profile)
        elapsed_arr = profile.get_elapsed_arr()
        row = [
            key.__qualname__ if full_name else key.__name__,
            n,
            round(np.sum(elapsed_arr) / n * 1000.0, 2),
            round(elapsed_arr.max() * 1000.0, 2),
            round(profile.get_bottleneck() * 1000.0, 2),
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


def plot_profiles(reverse=False, **kwargs):
    """Plots the profiles as a range bar chart, ordered by first call.

    Args:
        reverse (bool, optional): Reverse order? Defaults to False.
        **kwargs: ~matplotlib.patches.Polygon properties
    """
    earliest, latest = __get_time_range()
    sorted_profiles = {k: v for k, v in sorted(profiles.items(), key=lambda item: item[1].min(), reverse=reverse)}
    __plot_data(sorted_profiles, earliest, latest, **kwargs)


def __get_time_range() -> tuple[float, float]:
    """Gets the earliest and latest times for current profiles.

    Returns:
        tuple[float, float]: earliest and latest times in seconds
    """
    values = profiles.values()
    if not values:
        return 0, 1
    earliest = min([profile.min() for profile in values])
    latest = max([profile.max() for profile in values])
    return earliest, latest


def __plot_data(
    data: dict[Callable, type[TimeProfile]],
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
                fc=ColorHash(pair[0]).hex,
                ec=ec,
                **kwargs,
            )

    ax.set_yticks(np.arange(0, len(data)))
    ax.set_yticklabels([key.__qualname__ if full_name else key.__name__ for key in data.keys()])

    ax.set_title("Method activity")
    ax.set_xlabel("Time elapsed (s)")

    plt.tight_layout()
    plt.show()


def plot_merged(**kwargs):
    fig, ax = plt.subplots()
    width = 1

    earliest, latest = __get_time_range()
    ax.set_xlim(0, latest - earliest)

    p = profiles
    data = {}
    for k in p:
        data[k] = p[k].profile_merged

    for i, pair in enumerate(data.items()):
        starts_arr, ends_arr = pair[1].get_squashed_arr(earliest, latest)
        for x0, x1 in zip(starts_arr, ends_arr):
            ax.axhspan(
                ymin=i - width / 2,
                ymax=i + width / 2,
                xmin=x0,
                xmax=x1,
                **kwargs,
            )

    ax.set_yticks(np.arange(0, len(data)))
    # ax.set_yticklabels([key.__qualname__ if full_name else key.__name__ for key in data.keys()])

    ax.set_title("Method activity")
    ax.set_xlabel("Time elapsed (s)")

    plt.tight_layout()
    plt.show()
