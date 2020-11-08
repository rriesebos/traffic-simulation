from vehicle import *


class MOBIL:
    DEFAULT_POLITENESS_FACTOR = 0.5
    DEFAULT_RIGHT_BIAS = 0

    # Time before another lane change is allowed
    MIN_LAST_CHANGE_DELTA = 30

    """
    Args:
        politeness_factor: factor of how polite leader vehicles are
        right_bias: bias to drive right [m/s^2]
    """
    def __init__(self, politeness_factor=DEFAULT_POLITENESS_FACTOR, right_bias=DEFAULT_RIGHT_BIAS):
        self.politeness_factor = politeness_factor
        self.right_bias = right_bias

    def will_change_lane(self, vehicle, new_lane, old_next_vehicle: Vehicle, new_next_vehicle: Vehicle,
                         old_prev_vehicle: Vehicle, new_prev_vehicle: Vehicle, time):
        # Do not changes lanes if the vehicle 'just'  changed lanes
        if time - vehicle.last_lane_change_time < self.MIN_LAST_CHANGE_DELTA:
            return False

        traffic_model = vehicle.traffic_model
        if new_prev_vehicle is not None:
            # Check if gap to new previous vehicle is sufficient
            if new_prev_vehicle.calculate_gap(vehicle) < traffic_model.MINIMUM_GAP:
                return False

            # Safety criterion: lane changing should not lead to dangerous deceleration
            new_acc_new_prev_vehicle = traffic_model.calculate_acceleration(new_prev_vehicle, vehicle)
            if new_acc_new_prev_vehicle < -new_prev_vehicle.comfortable_deceleration:
                return False

        # Check if gap to new next vehicle is sufficient
        if new_next_vehicle is not None and vehicle.calculate_gap(new_next_vehicle) < traffic_model.MINIMUM_GAP:
            return False

        # Avoid obstacles
        if isinstance(old_next_vehicle, Obstacle) and isinstance(new_next_vehicle, Obstacle):
            return vehicle.calculate_gap(new_next_vehicle) >= vehicle.calculate_gap(old_next_vehicle)

        # Safety criterion: lane changing should not lead to dangerous deceleration
        new_acc = traffic_model.calculate_acceleration(vehicle, new_next_vehicle)
        if new_acc < -vehicle.comfortable_deceleration:
            return False

        # Incentive criterion: lane changes should be net beneficial
        acceleration_change = new_acc - vehicle.acceleration
        acceleration_change_old_prev = (traffic_model.calculate_acceleration(old_prev_vehicle, old_next_vehicle)
                                        - 0 if old_prev_vehicle is None else old_prev_vehicle.acceleration)
        acceleration_change_new_prev = (traffic_model.calculate_acceleration(new_prev_vehicle, vehicle)
                                        - 0 if new_prev_vehicle is None else new_prev_vehicle.acceleration)

        is_right = int(new_lane > vehicle.lane)
        return (acceleration_change + self.politeness_factor
                * (acceleration_change_old_prev + acceleration_change_new_prev)) > (vehicle.max_acceleration
                                                                                    - (is_right * self.right_bias))
