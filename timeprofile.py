import numpy as np
import numpy.typing as npt


class TimeProfile:
    def __init__(self, starts: list[float] = None, ends: list[float] = None):
        if (bool(starts) != bool(ends)) or (starts and ends and len(starts) != len(ends)):
            raise Exception("Input lists do not have the same length")

        self.__starts = [] if starts is None else starts
        self.__ends = [] if ends is None else ends

        self.__starts_arr = None
        self.__ends_arr = None
        self.__updated = False

    def __len__(self) -> int:
        return len(self.__starts)

    @property
    def profile(self) -> tuple[list[float], list[float]]:
        return self.__starts, self.__ends

    @property
    def profile_arr(self) -> tuple[npt.NDArray, npt.NDArray]:
        if not self.__updated:
            self.__update_arr()
        return self.__starts_arr, self.__ends_arr

    def __update_arr(self):
        self.__starts_arr = np.array(self.__starts)
        self.__ends_arr = np.array(self.__ends)
        self.__updated = True

    def add(self, start: float, end: float):
        self.__starts += [start]
        self.__ends += [end]
        self.__updated = False

    def clear(self):
        self.__starts = []
        self.__ends = []
        self.__updated = False

    def min(self) -> float:
        return self.profile_arr[0].min()

    def max(self) -> float:
        return self.profile_arr[1].max()

    def get_bottleneck(self) -> float:
        starts_arr, ends_arr = self.profile_arr
        n = len(starts_arr)
        starts = np.sort(starts_arr)
        ends = np.sort(ends_arr)

        bottleneck = 0
        j = 0
        for i in range(0, n):
            if i == n - 1 or starts[i + 1] > ends[i]:
                bottleneck += ends[i] - starts[j]
                j = i + 1
        return bottleneck

    def get_squashed_arr(self, min: float, max: float) -> tuple[npt.NDArray, npt.NDArray]:
        starts_arr, ends_arr = self.profile_arr
        time_frame = max - min
        new_starts: npt.NDArray = (starts_arr - min) / time_frame
        new_ends: npt.NDArray = (ends_arr - min) / time_frame
        return new_starts, new_ends

    def get_elapsed_arr(self) -> npt.NDArray:
        starts_arr, ends_arr = self.profile_arr
        return ends_arr - starts_arr
