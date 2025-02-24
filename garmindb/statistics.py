"""Enumeration of types of statistcs that can be downloaded and processed."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import enum


class Statistics(enum.Enum):
    """The types of statistics that can be downloaded and analyzed."""

    monitoring = 1
    steps = 2
    itime = 3
    sleep = 4
    rhr = 5
    weight = 6
    activities = 7
    hydration = 8
    monitoring_fit_files = 9
    activity_fit_files = 10
    activity_summary_files = 11
    include_today = 12
    profile_files = 13
    overwrite_force_daily = 14
    overwrite_force_activities = 15

    @classmethod
    def from_string(cls, string):
        """Return a Statistics created from a string that matches an enum name of value."""
        try:
            return cls(string)
        except Exception:
            return getattr(cls, string)
