from collections import namedtuple


"""
VehicleParameters represent a list of parameters related to a vehicle:
    length: Length of a vehicle [m]
    desired_velocity: Desired velocity of a vehicle [m/s]
    desired_time_headway: Desired time gap between the car and the next vehicle [s]
    max_acceleration:  Maximum acceleration [m/s^2]
    comfortable_deceleration: Comfortable deceleration (braking) [m/s^2]
"""
VehicleParameters = namedtuple('VehicleParameters', ['length', 'desired_velocity', 'desired_time_headway',
                                                     'max_acceleration', 'comfortable_deceleration'])


class Vehicle:
    """
    Args:
        position: the position of the front of the vehicle
        velocity: velocity of the vehicle
        traffic_model: traffic model used to update the acceleration
        vehicle_parameters: the length, desired_velocity, desired_time_headway, max_acceleration, and
                            comfortable_deceleration parameters of the vehicle in the given order
        lane_change_model: lane change model used to determine whether the car will change lanes
        next_vehicle: next vehicle on the road, the vehicle in front of this vehicle
        lane: lane the vehicle is currently on
    """
    def __init__(self, position, velocity, acceleration, traffic_model, vehicle_parameters: VehicleParameters,
                 lane_change_model=None, next_vehicle=None, lane=0):
        self.position = position
        self.velocity = velocity

        self.gap = self.calculate_gap(next_vehicle)
        self.acceleration = acceleration

        self.traffic_model = traffic_model
        self.lane_change_model = lane_change_model
        self.length, self.desired_velocity, self.desired_time_headway, self.max_acceleration, \
            self.comfortable_deceleration = vehicle_parameters

        self.next_vehicle = next_vehicle
        self.lane = lane

    def update_position(self, delta_t):
        self.position += delta_t * self.velocity

    def update_velocity(self, delta_t):
        self.velocity = max(0, self.velocity + delta_t * self.acceleration)

    def update_acceleration(self, delta_t):
        self.update_gap()
        self.acceleration = self.traffic_model.calculate_acceleration(self, self.next_vehicle, delta_t)

    def calculate_gap(self, next_vehicle):
        if next_vehicle is None:
            return 0

        return next_vehicle.position - self.position - next_vehicle.length

    def update_gap(self):
        self.gap = self.calculate_gap(self.next_vehicle)

    def update(self, delta_t):
        self.update_acceleration(delta_t)
        self.update_velocity(delta_t)
        self.update_position(delta_t)

    def will_change_lane(self, new_lane, new_next_vehicle, old_prev_vehicle, new_prev_vehicle, delta_t):
        return self.lane_change_model.will_change_lane(self, new_lane, self.next_vehicle, new_next_vehicle,
                                                       old_prev_vehicle, new_prev_vehicle, delta_t)

    def change_lane(self, new_next_vehicle, new_lane):
        self.next_vehicle = new_next_vehicle
        self.lane = new_lane


class Car(Vehicle):
    CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=1.5,
        max_acceleration=0.3,
        comfortable_deceleration=3.0
    )

    def __init__(self, position, velocity, acceleration, traffic_model, lane_change_model=None, next_vehicle=None, lane=0):
        super().__init__(position, velocity, acceleration, traffic_model, self.CAR_PARAMETERS,
                         lane_change_model, next_vehicle, lane)


class Truck(Vehicle):
    TRUCK_PARAMETERS = VehicleParameters(
        length=19,
        desired_velocity=80 / 3.6,
        desired_time_headway=1.7,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position, velocity, acceleration, traffic_model, lane_change_model=None, next_vehicle=None, lane=0):
        super().__init__(position, velocity, acceleration, traffic_model, self.TRUCK_PARAMETERS,
                         lane_change_model, next_vehicle, lane)


class AggressiveCar(Vehicle):
    # Higher desired velocity, max_acceleration, comfortable deceleration and lower desired time headway
    AGGRESSIVE_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=130 / 3.6,
        desired_time_headway=0.5,
        max_acceleration=2.0,
        comfortable_deceleration=5.0
    )

    def __init__(self, position, velocity, acceleration, traffic_model, lane_change_model=None, next_vehicle=None, lane=0):
        super().__init__(position, velocity, acceleration, traffic_model, self.AGGRESSIVE_CAR_PARAMETERS,
                         lane_change_model, next_vehicle, lane)


class CarefulCar(Vehicle):
    # Higher desired time gap and lower comfortable deceleration
    CAREFUL_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=6,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position, velocity, acceleration, traffic_model, lane_change_model=None, next_vehicle=None, lane=0):
        super().__init__(position, velocity, acceleration, traffic_model, self.CAREFUL_CAR_PARAMETERS,
                         lane_change_model, next_vehicle, lane)
