import inspect
from typing import Callable
from colorhash import ColorHash
from matplotlib.patches import Rectangle
import numpy as np
from matplotlib import pyplot as plt
from functools import wraps
from time import perf_counter
from tabulate import tabulate
from operator import itemgetter

from timeprofiles.timeprofile import TimeProfile
from timeprofiles.zoompan import ZoomPan


__all__ = [
    "profiles",
    "profile_method",
    "profile_class_methods",
    "profile_ignore",
    "add",
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
    """Adds a start and end time to profiles. Creates a new profile object if key does not exist."""

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
    """Prints out all profiles to console as a table with the method name, or optionally the full name,
    ordered by the order_by parameter. Use the provided ORDER_BY_ fields for the order_by parameter."""

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


def __get_time_range() -> tuple[float, float]:
    """Gets the earliest and latest times for current profiles."""

    values = profiles.values()
    if not values:
        return 0, 1
    earliest = min([profile.min() for profile in values])
    latest = max([profile.max() for profile in values])
    return earliest, latest


def plot_profiles(
    full_name=False,
    alpha=0.4,
    reverse=False,
    ec="#000",
    **kwargs,
):
    """Plots the profiles as a range bar chart with the method name, or optionally the full name, ordered by first call.
    Extra kwargs will be passed into the matplotlib's Rectangle object."""

    fig, ax = plt.subplots()
    width = 1

    earliest, latest = __get_time_range()
    data = {k: v for k, v in sorted(profiles.items(), key=lambda item: item[1].min(), reverse=reverse)}

    for i, pair in enumerate(data.items()):
        starts_arr, ends_arr = pair[1].get_normalized_arr(earliest)
        for x0, x1 in zip(starts_arr, ends_arr):
            ax.add_patch(
                Rectangle((x0, i - width / 2), x1 - x0, width, alpha=alpha, fc=ColorHash(pair[0]).hex, ec=ec, **kwargs)
            )

    ax.set_ylim(-0.5, len(data) - 0.5)
    ax.set_xlim(0, latest - earliest)

    ax.set_yticks(np.arange(0, len(data)))
    ax.set_yticklabels([key.__qualname__ if full_name else key.__name__ for key in data.keys()])

    ax.set_title("Method activity")
    ax.set_xlabel("Time elapsed (s)")

    # Add zoom and pan events
    zp = ZoomPan()
    zp.zoom_factory(ax)
    zp.pan_factory(ax)

    plt.tight_layout()
    plt.show()


def plot_merged(full_name=False, alpha=0.6, ec="#000", **kwargs):
    """Plots the profiles as a range bar chart with the method name, or optionally the full name, ordered by first call.
    Extra kwargs will be passed into the matplotlib's Rectangle object."""

    fig, ax = plt.subplots()
    width = 1

    earliest, latest = __get_time_range()

    data: list[tuple[float, float, Callable]] = []
    for k in profiles:
        starts, ends = profiles[k].get_normalized_merged(earliest)
        for start, end in zip(starts, ends):
            data += [(start, end, k)]

    data.sort()
    stack = []
    for d in data:
        i = None
        for j in range(0, len(stack) + 1):
            if j == len(stack):
                stack += [None]
                i = j
                break
            if d[0] >= stack[j][1]:
                i = j
                break
        stack[i] = d
        ax.add_patch(
            Rectangle(
                (d[0], i),
                d[1] - d[0],
                width,
                alpha=alpha,
                fc=ColorHash(d[2]).hex,
                ec=ec,
                label=d[2].__qualname__ if full_name else d[2].__name__,
                **kwargs,
            )
        )

    ax.set_ylim(0, len(stack))
    ax.set_xlim(0, latest - earliest)

    ax.set_yticks(np.arange(0, len(stack) + 1))

    ax.set_title("Method activity (merged)")
    ax.set_xlabel("Time elapsed (s)")

    # combine labels by key https://stackoverflow.com/a/13589144
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # Add zoom and pan events
    zp = ZoomPan()
    zp.zoom_factory(ax)
    zp.pan_factory(ax)

    plt.tight_layout()
    plt.show()
