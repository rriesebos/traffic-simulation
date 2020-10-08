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
        next_vehicle: next vehicle on the road, the vehicle in front of this vehicle
    """
    def __init__(self, position, velocity, traffic_model, vehicle_parameters: VehicleParameters, next_vehicle=None):
        self.position = position
        self.velocity = velocity
        self.acceleration = 0
        self.gap = 0

        self.traffic_model = traffic_model
        self.length, self.desired_velocity, self.desired_time_headway, self.max_acceleration, \
            self.comfortable_deceleration = vehicle_parameters

        self.next_vehicle = next_vehicle

    def update_position(self, delta_t):
        self.position += delta_t * self.velocity + 0.5 * self.acceleration * delta_t ** 2

    def update_velocity(self, delta_t):
        self.velocity += max(0, delta_t * self.acceleration)

    def update_acceleration(self):
        # If this vehicle is the leader, do not update the acceleration
        if self.next_vehicle is None:
            return

        self.acceleration = self.traffic_model.calculate_acceleration(self)

    def update_gap(self):
        if self.next_vehicle is None:
            return self.gap

        self.gap = self.next_vehicle.position - self.position - self.next_vehicle.length

    def update(self, delta_t):
        self.update_gap()
        self.update_acceleration()
        self.update_velocity(delta_t)
        self.update_position(delta_t)


class Car(Vehicle):
    CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=1.5,
        max_acceleration=0.3,
        comfortable_deceleration=3.0
    )

    def __init__(self, position, velocity, traffic_model, next_vehicle=None):
        super().__init__(position, velocity, traffic_model, self.CAR_PARAMETERS, next_vehicle)


class Truck(Vehicle):
    TRUCK_PARAMETERS = VehicleParameters(
        length=19,
        desired_velocity=80 / 3.6,
        desired_time_headway=1.7,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position, velocity, traffic_model, next_vehicle=None):
        super().__init__(position, velocity, traffic_model, self.TRUCK_PARAMETERS, next_vehicle)


class AggressiveCar(Vehicle):
    # Higher desired velocity, max_acceleration, comfortable deceleration and lower desired time headway
    AGGRESSIVE_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=130 / 3.6,
        desired_time_headway=0.5,
        max_acceleration=2.0,
        comfortable_deceleration=5.0
    )

    def __init__(self, position, velocity, traffic_model, next_vehicle=None):
        super().__init__(position, velocity, traffic_model, self.AGGRESSIVE_CAR_PARAMETERS, next_vehicle)


class CarefulCar(Vehicle):
    # Higher desired time gap and lower comfortable deceleration
    CAREFUL_CAR_PARAMETERS = VehicleParameters(
        length=5,
        desired_velocity=100 / 3.6,
        desired_time_headway=6,
        max_acceleration=0.3,
        comfortable_deceleration=2.0
    )

    def __init__(self, position, velocity, traffic_model, next_vehicle=None):
        super().__init__(position, velocity, traffic_model, self.CAREFUL_CAR_PARAMETERS, next_vehicle)
