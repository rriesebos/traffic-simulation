import math
from vehicle import Vehicle, Obstacle


class IDM:
    # Minimum gap between two vehicles [m], 1000+ meters models free road
    MINIMUM_GAP = 2

    # Exponent to control decrease of acceleration as desired velocity is approached
    ACCELERATION_EXPONENT = 4

    def calculate_acceleration(self, vehicle: Vehicle, next_vehicle: Vehicle):
        if vehicle is None or isinstance(vehicle, Obstacle):
            return 0

        if next_vehicle is not None:
            # If there is a vehicle in front, take it in to account when calculating the acceleration
            delta_velocity = vehicle.velocity - next_vehicle.velocity
            desired_distance = ((vehicle.velocity * vehicle.desired_time_headway)
                                + (vehicle.velocity * delta_velocity)
                                / (2 * math.sqrt(vehicle.max_acceleration * vehicle.comfortable_deceleration)))

            desired_gap = self.MINIMUM_GAP + max(0, desired_distance)
            acceleration_interaction = (desired_gap / max(vehicle.gap, self.MINIMUM_GAP)) ** 2
            if vehicle.gap >= desired_gap:
                acceleration_interaction = 0
        else:
            # No car in front, so there is no "interaction" variable needed
            acceleration_interaction = 0

        acceleration_free_road = 1 - (vehicle.velocity / vehicle.desired_velocity) ** self.ACCELERATION_EXPONENT
        new_acceleration = vehicle.max_acceleration * (acceleration_free_road - acceleration_interaction)

        return new_acceleration


class Gipps:
    # Minimum gap between two vehicles [m]
    MINIMUM_GAP = 2

    def __init__(self, delta_t):
        self.delta_t = delta_t

    def calculate_acceleration(self, vehicle: Vehicle, next_vehicle: Vehicle):
        if vehicle is None or isinstance(vehicle, Obstacle):
            return 0

        if next_vehicle is None:
            return 1 - (vehicle.velocity / vehicle.desired_velocity)

        velocity_safe = ((-vehicle.comfortable_deceleration * self.delta_t)
                         + (math.sqrt(vehicle.comfortable_deceleration ** 2 * self.delta_t ** 2 + next_vehicle.velocity ** 2
                                      + 2 * vehicle.comfortable_deceleration * (vehicle.gap - self.MINIMUM_GAP))))

        new_velocity = min(velocity_safe, min(vehicle.velocity + vehicle.max_acceleration * self.delta_t,
                                              vehicle.desired_velocity))
        new_acceleration = (new_velocity - vehicle.velocity) / self.delta_t

        return new_acceleration
