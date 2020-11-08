from collections import namedtuple
from enum import Enum
import math


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


class VehicleType(Enum):
    Car = 1
    Truck = 2
    AggressiveCar = 3
    PassiveCar = 4


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
    def __init__(self, position, velocity, vehicle_parameters: VehicleParameters, traffic_model,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        self.position = position
        self.velocity = velocity

        self.traffic_model = traffic_model
        self.lane_change_model = lane_change_model
        self.length, self.desired_velocity, self.desired_time_headway, self.max_acceleration, \
            self.comfortable_deceleration = vehicle_parameters

        self.next_vehicle = next_vehicle
        self.prev_vehicle = prev_vehicle
        self.lane = lane

        if lane_change_model is None:
            self.last_lane_change_time = 0
        else:
            self.last_lane_change_time = -lane_change_model.MIN_LAST_CHANGE_DELTA

        self.gap = self.calculate_gap(next_vehicle)
        if self.traffic_model is None:
            self.acceleration = 0
        else:
            self.acceleration = traffic_model.calculate_acceleration(self, next_vehicle)

    def update_position(self, delta_t):
        self.position += delta_t * self.velocity
        self.update_gap()

    def update_velocity(self, delta_t):
        self.velocity = max(0, self.velocity + delta_t * self.acceleration)

    def update_acceleration(self):
        if self.traffic_model is None:
            return

        self.acceleration = self.traffic_model.calculate_acceleration(self, self.next_vehicle)

    def calculate_gap(self, next_vehicle):
        if next_vehicle is None:
            return math.inf

        return next_vehicle.position - self.position - next_vehicle.length

    def update_gap(self):
        self.gap = self.calculate_gap(self.next_vehicle)

    def update(self, delta_t):
        self.update_acceleration()
        self.update_velocity(delta_t)
        self.update_position(delta_t)

    def will_change_lane(self, new_lane, new_next_vehicle, new_prev_vehicle, time):
        if self.lane_change_model is None:
            return False

        return self.lane_change_model.will_change_lane(self, new_lane, self.next_vehicle, new_next_vehicle,
                                                       self.prev_vehicle, new_prev_vehicle, time)

    def change_lane(self, new_next_vehicle, new_prev_vehicle, new_lane, time):
        self.next_vehicle = new_next_vehicle
        self.prev_vehicle = new_prev_vehicle
        self.lane = new_lane

        self.last_lane_change_time = time


class Car(Vehicle):
    CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=1.5,
        max_acceleration=0.3,
        comfortable_deceleration=3.0
    )

    def __init__(self, position=0, velocity=CAR_PARAMETERS.desired_velocity, traffic_model=None,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        super().__init__(position, velocity, self.CAR_PARAMETERS, traffic_model,
                         lane_change_model, next_vehicle, prev_vehicle, lane)


class Truck(Vehicle):
    TRUCK_PARAMETERS = VehicleParameters(
        length=19,
        desired_velocity=80 / 3.6,
        desired_time_headway=1.7,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position=0, velocity=TRUCK_PARAMETERS.desired_velocity, traffic_model=None,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        super().__init__(position, velocity, self.TRUCK_PARAMETERS, traffic_model,
                         lane_change_model, next_vehicle, prev_vehicle, lane)


class AggressiveCar(Vehicle):
    # Higher desired velocity, max_acceleration, comfortable deceleration and lower desired time headway
    AGGRESSIVE_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=130 / 3.6,
        desired_time_headway=0.5,
        max_acceleration=2.0,
        comfortable_deceleration=5.0
    )

    def __init__(self, position=0, velocity=AGGRESSIVE_CAR_PARAMETERS.desired_velocity, traffic_model=None,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        super().__init__(position, velocity, self.AGGRESSIVE_CAR_PARAMETERS, traffic_model,
                         lane_change_model, next_vehicle, prev_vehicle, lane)


class PassiveCar(Vehicle):
    # Higher desired time gap and lower comfortable deceleration
    PASSIVE_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=6,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position=0, velocity=PASSIVE_CAR_PARAMETERS.desired_velocity, traffic_model=None,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        super().__init__(position, velocity, self.PASSIVE_CAR_PARAMETERS, traffic_model,
                         lane_change_model, next_vehicle, prev_vehicle, lane)


class Obstacle(Vehicle):
    OBSTACLE_PARAMETERS = VehicleParameters(
        length=0,
        desired_velocity=0,
        desired_time_headway=0,
        max_acceleration=0,
        comfortable_deceleration=0
    )

    def update_position(self, delta_t):
        return self.position

    def update_velocity(self, delta_t):
        return 0

    def update_acceleration(self):
        return 0

    def will_change_lane(self, new_lane, new_next_vehicle, new_prev_vehicle, time):
        return False

    def __init__(self, position=0, velocity=OBSTACLE_PARAMETERS.desired_velocity, traffic_model=None,
                 lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0):
        super().__init__(position, velocity, self.OBSTACLE_PARAMETERS, traffic_model,
                         lane_change_model, next_vehicle, prev_vehicle, lane)
