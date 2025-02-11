from typing import IO, Union
from pathlib import Path

from dataclasses import dataclass
import numpy as np

from numpy.typing import NDArray


@dataclass
class TimeSeries:

    dependent_variable: NDArray
    times: NDArray

    def __post_init__(self):

        timesteps = np.diff(self.times)
        if not np.isclose(np.std(timesteps), 0.0):
            raise ValueError("TimeSeries.times must be uniformly spaced")
        if np.isclose(np.mean(timesteps), 0.0):
            raise ValueError("TimeSeries.times must have a timestep greater than zero")

    def save(self, fp: Union[IO, str, Path], header: str = "", delimiter=","):

        """
        Method to save a time series

        Args:
            fp (Union[IO, str, Path]):
                The file-like object, path name, or Path in which to save the TimeSeries instance

            header (str):
                An optional header. Defaults to the empty string

            delimiter (str):
                The delimiting character in the save file. Defaults to a comma

        """
        np.savetxt(
            fp,
            np.vstack((self.times, self.dependent_variable.T)).T,
            delimiter=delimiter,
            header=header,
            comments=""
        )

    @property
    def num_dims(self) -> int:

        """
        The dimensionality of the time series

        Returns:
            int: The dimensionality of the time series
        """

        return self.dependent_variable.shape[1]

    @classmethod
    def from_csv(cls, fp: Union[IO, str, Path], time_index: int = 0):

        """
        Method for loading in a TimeSeries instance from a comma-separated value (csv) file

        Args:
            fp (Union[IO, str, Path]):
                The file-like object, path name, or Path in which to read

            time_index (int):
                The column index corresponding to the time column. Defaults to 0

        Returns:
            TimeSeries: A TimeSeries instance populated by data from the csv file
        """

        data = np.loadtxt(fp, delimiter=",")

        return cls(
            dependent_variable=np.delete(data, obj=time_index, axis=1),
            times=data[:, time_index]
        )

    @property
    def timestep(self) -> float:

        """
        The physical timestep of the time series

        Returns:
            int: The physical timestep of the time series
        """

        return self.times[1] - self.times[0]

    def __eq__(self, other) -> bool:
        return bool(np.all(self.times == other.times) and np.all(
            np.isclose(self.dependent_variable, other.dependent_variable)
        ))

    def __getitem__(self, key):

        return TimeSeries(self.dependent_variable[key], self.times[key])

    def __setitem__(self, key, value):

        if not isinstance(value, TimeSeries):
            raise TypeError("Value must be a TimeSeries object")
        if isinstance(key, slice) and key.stop > len(self.dependent_variable):
            raise ValueError("Slice stop index out of range")
        if isinstance(key, int) and key >= len(self.dependent_variable):
            raise ValueError("Index out of range")

        self.dependent_variable[key] = value.dependent_variable
        self.times[key] = value.times

    def __add__(self, other):

        if not len(self.times) == len(other.times):
            raise ValueError("can only add TimeSeries instances that have the same number of timesteps")

        if not np.all(self.times == other.times):
            raise ValueError("can only add TimeSeries instances that span the same times")

        return TimeSeries(
            dependent_variable=self.dependent_variable + other.dependent_variable,
            times=self.times
        )

    def __sub__(self, other):

        if not len(self.times) == len(other.times):
            raise ValueError("can only subtract TimeSeries instances that have the same number of timesteps")

        if not np.all(self.times == other.times):
            raise ValueError("can only subtract TimeSeries instances that span the same times")

        return TimeSeries(
            dependent_variable=self.dependent_variable - other.dependent_variable,
            times=self.times
        )

    def __rshift__(self, other):

        if self.times[-1] >= other.times[0]:
            raise ValueError("can only concatenate TimeSeries instances with non-overlapping time values")

        return TimeSeries(
            dependent_variable=np.vstack((self.dependent_variable, other.dependent_variable)),
            times=np.hstack((self.times, other.times))
        )