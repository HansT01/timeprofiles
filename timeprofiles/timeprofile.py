import numpy as np
import numpy.typing as npt


class TimeProfile:
    """TimeProfile is a class specifically for storing instances of time profiles."""

    def __init__(self, starts: list[float] = None, ends: list[float] = None):
        """Class constructor.
        If a starts and ends list is given, they must have the same length.

        Args:
            starts (list[float], optional): Starts list. Defaults to None.
            ends (list[float], optional): Ends list. Defaults to None.

        Raises:
            Exception: Raises exception if the input starts and ends lists do not have the same length.
        """
        if (bool(starts) != bool(ends)) or (starts and ends and len(starts) != len(ends)):
            raise Exception("Input lists do not have the same length")

        if starts is None and ends is None:
            self.__starts = []
            self.__ends = []
        else:
            for i in range(len(starts)):
                if ends[i] < starts[i]:
                    raise Exception("End time must be after start time.")
            self.__starts = starts
            self.__ends = ends

        self.__starts_arr = None
        self.__ends_arr = None
        self.__updated_arr = False

        self.__starts_merged = []
        self.__ends_merged = []
        self.__updated_merged = False

    def __len__(self) -> int:
        """Gets the number of elements in the profile object."""
        return len(self.__starts)

    def __repr__(self):
        return str([(start, end) for (start, end) in zip(self.__starts, self.__ends)])

    @property
    def profile(self) -> tuple[list[float], list[float]]:
        """Gets the profile lists.

        Returns:
            tuple[list[float], list[float]]: Starts and ends list.
        """
        return self.__starts, self.__ends

    @property
    def profile_arr(self) -> tuple[npt.NDArray, npt.NDArray]:
        """Gets the profile numpy arrays.

        Returns:
            tuple[npt.NDArray, npt.NDArray]: Starts and ends arrays.
        """
        if not self.__updated_arr:
            self.__update_arr()
        return self.__starts_arr, self.__ends_arr

    @property
    def profile_merged(self) -> tuple[list[float], list[float]]:
        if not self.__updated_merged:
            self.__update_merged()
        return self.__starts_merged, self.__ends_merged

    def add(self, start: float, end: float):
        """Adds new start and end times to profile."""
        if end < start:
            raise Exception("End time must be after start time.")
        self.__starts += [start]
        self.__ends += [end]
        self.__updated_arr = False
        self.__updated_merged = False

    def clear(self):
        """Clears the current profiles from memory."""
        self.__starts = []
        self.__ends = []
        self.__updated_arr = False
        self.__updated_merged = False

    def min(self) -> float:
        """Gets the minimum time value in the profile.

        Returns:
            float: Minimum time value.
        """
        return self.profile_arr[0].min()

    def max(self) -> float:
        """Gets the maximum time value in the profile.

        Returns:
            float: Maximum time value.
        """
        return self.profile_arr[1].max()

    def __update_arr(self):
        """Creates new numpy arrays from python lists."""
        self.__starts_arr = np.array(self.__starts)
        self.__ends_arr = np.array(self.__ends)
        self.__updated_arr = True

    def __update_merged(self):
        """Clears and adds new profile values to merged profiles."""
        starts, ends = self.profile

        n = len(self)
        starts_sorted = sorted(starts)
        ends_sorted = sorted(ends)

        self.__starts_merged.clear()
        self.__ends_merged.clear()

        j = 0
        for i in range(0, n):
            if i == n - 1 or starts_sorted[i + 1] > ends_sorted[i]:
                self.__starts_merged += [starts_sorted[j]]
                self.__ends_merged += [ends_sorted[i]]
                j = i + 1
        self.__updated_merged = True

    def get_bottleneck(self) -> float:
        """Gets the bottleneck of the profile.
        The bottleneck is the total active time, excluding overlaps.

        Returns:
            float: Bottleneck.
        """
        starts_merged, ends_merged = self.profile_merged
        return sum([end - start for start, end in zip(starts_merged, ends_merged)])

    def get_squashed_arr(self, min: float, max: float) -> tuple[npt.NDArray, npt.NDArray]:
        """Gets a squashed array of this profile.
        The squashed array ranges from 0 to 1, as a ratio between the min and max value.

        For example, a start and end time of 4 to 6, between a min and max value of 2 and 10, would become 0.25 and 0.5.

        Args:
            min (float): min value of a given time frame
            max (float): max value of a given time frame

        Returns:
            tuple[npt.NDArray, npt.NDArray]: Starts and ends array.
        """
        starts_arr, ends_arr = self.profile_arr
        time_frame = max - min
        new_starts: npt.NDArray = (starts_arr - min) / time_frame
        new_ends: npt.NDArray = (ends_arr - min) / time_frame
        return new_starts, new_ends

    def get_squashed_merged(self, min: float, max: float) -> tuple[list[float], list[float]]:
        starts, ends = self.profile_merged
        time_frame = max - min
        new_starts = [(start - min) / time_frame for start in starts]
        new_ends = [(end - min) / time_frame for end in ends]
        return new_starts, new_ends

    def get_elapsed_arr(self) -> npt.NDArray:
        """Gets the time elapsed array of this profile.
        Time elapsed is the start time subtracted from the end time.

        Returns:
            npt.NDArray: Time elapsed array.
        """
        starts_arr, ends_arr = self.profile_arr
        return ends_arr - starts_arr
