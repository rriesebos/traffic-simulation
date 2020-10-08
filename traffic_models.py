import math


class IDM:
    # Desired velocity of a car [m/s]
    DESIRED_VELOCITY = 100 / 3.6

    # Desired time gap between two cars [s]
    DESIRED_TIME_GAP = 1

    # Minimum gap between two cars [m], 1000+ meters models free road
    MINIMUM_GAP = 2

    # Exponent to control decrease of acceleration as desired velocity is approached
    ACCELERATION_EXPONENT = 4

    # Maximum acceleration [m/s^2]
    MAX_ACCELERATION = 1

    # Comfortable deceleration (braking) [m/s^2]
    COMFORTABLE_DECELERATION = 1.5

    def calculate_acceleration(self, current_gap, velocity, velocity_leader):
        delta_velocity = velocity - velocity_leader
        desired_distance = ((velocity * self.DESIRED_TIME_GAP)
                            + (velocity * delta_velocity)
                            / (2 * math.sqrt(self.MAX_ACCELERATION * self.COMFORTABLE_DECELERATION)))

        desired_gap = self.MINIMUM_GAP + max(0, desired_distance)

        acceleration_free_road = 1 - (velocity / self.DESIRED_VELOCITY) ** self.ACCELERATION_EXPONENT
        acceleration_interaction = (desired_gap / max(current_gap, self.MINIMUM_GAP)) ** 2
        new_acceleration = self.MAX_ACCELERATION * (acceleration_free_road - acceleration_interaction)

        return new_acceleration
