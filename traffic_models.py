import math
from vehicle import Vehicle


class IDM:
    # Minimum gap between two vehicles [m], 1000+ meters models free road
    MINIMUM_GAP = 2

    # Exponent to control decrease of acceleration as desired velocity is approached
    ACCELERATION_EXPONENT = 4

    def calculate_acceleration(self, vehicle: Vehicle):
        if vehicle.next_vehicle is not None:
            # If there is a vehicle in front, take it in to account when calculating the acceleration
            delta_velocity = vehicle.velocity - vehicle.next_vehicle.velocity
            desired_distance = ((vehicle.velocity * vehicle.desired_time_headway)
                                + (vehicle.velocity * delta_velocity)
                                / (2 * math.sqrt(vehicle.max_acceleration * vehicle.comfortable_deceleration)))
    
            desired_gap = self.MINIMUM_GAP + max(0, desired_distance)
            acceleration_interaction = (desired_gap / max(vehicle.gap, self.MINIMUM_GAP)) ** 2
        else:
            # No car in front, so there is no "interaction" variable needed
            acceleration_interaction = 0
        
        acceleration_free_road = 1 - (vehicle.velocity / vehicle.desired_velocity) ** self.ACCELERATION_EXPONENT
        new_acceleration = vehicle.max_acceleration * (acceleration_free_road - acceleration_interaction)

        return new_acceleration
