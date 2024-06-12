# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

""" This module contains the different parameters sets for each behavior. """


class Cautious(object):
    """Class for Cautious agent."""

    max_speed = 40
    speed_lim_dist = 6
    speed_decrease = 12
    safety_time = 3
    min_proximity_threshold = 12
    braking_distance = 6
    tailgate_counter = 0


class Normal(object):
    """Class for Normal agent."""

    max_speed = 70
    """The maximum speed in km/h your vehicle will be able to reach."""

    speed_lim_dist = 3
    """"Value in km/h that defines how far your vehicle's target speed will be from the current speed limit (e.g., if the speed limit is 30km/h and 
    speed_lim_dist is 10km/h, then the target speed will be 20km/h)"""

    speed_decrease = 12
    """How quickly in km/h your vehicle will slow down when approaching a slower vehicle ahead."""

    safety_time = 3
    """Time-to-collision; an approximation of the time it will take for your vehicle to collide with one in front if it brakes suddenly."""

    min_proximity_threshold = 12
    """The minimum distance in meters from another vehicle or pedestrian before your vehicle performs a maneuver such as avoidance, or tailgating."""

    braking_distance = 5
    """The distance from a pedestrian or vehicle at which your vehicle will perform an emergency stop."""

    tailgate_counter = -1
    """A counter to avoid tailgating too quickly after the last tailgate."""


class Aggressive(object):
    """Class for Aggressive agent."""

    max_speed = 70
    speed_lim_dist = 1
    speed_decrease = 8
    safety_time = 2
    min_proximity_threshold = 8
    braking_distance = 4
    tailgate_counter = -1


class Anomaly(object):
    """Class for Anomaly agent."""

    max_speed = 80
    speed_lim_dist = 1
    speed_decrease = 6
    safety_time = 2
    min_proximity_threshold = 6
    braking_distance = 4
    tailgate_counter = -1
