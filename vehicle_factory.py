from vehicle import *
import random


class VehicleFactory:
    """
        Args:
            weights: list of weights with the bias for Cars, Trucks, AggressiveCars and PassiveCars in given order
            default_traffic_model: traffic model passed to the created vehicle in case no traffic model is supplied
            default_lane_change_model: lane change model passed to the created vehicle in case no traffic model is supplied
    """
    def __init__(self, weights, default_traffic_model, default_lane_change_model):
        self.weights = weights
        self.default_traffic_model = default_traffic_model
        self.default_lane_change_model = default_lane_change_model

    def create_vehicle(self, vehicle_type: VehicleType, traffic_model=None, lane_change_model=None):
        if traffic_model is None:
            traffic_model = self.default_traffic_model

        if lane_change_model is None:
            lane_change_model = self.default_lane_change_model

        if vehicle_type is VehicleType.Car:
            return Car(traffic_model=traffic_model, lane_change_model=lane_change_model)
        elif vehicle_type is VehicleType.Truck:
            return Truck(traffic_model=traffic_model, lane_change_model=lane_change_model)
        elif vehicle_type is VehicleType.AggressiveCar:
            return AggressiveCar(traffic_model=traffic_model, lane_change_model=lane_change_model)
        elif vehicle_type is VehicleType.PassiveCar:
            return PassiveCar(traffic_model=traffic_model, lane_change_model=lane_change_model)
        else:
            return Car(traffic_model=traffic_model, lane_change_model=lane_change_model)

    def create_random_vehicle(self, traffic_model=None, lane_change_model=None):
        return self.create_random_vehicles(num=1, traffic_model=traffic_model, lane_change_model=lane_change_model)[0]

    def create_random_vehicles(self, num=1, traffic_model=None, lane_change_model=None):
        vehicle_types = list(VehicleType)
        random_vehicle_types = random.choices(vehicle_types, weights=self.weights, k=num)

        return [self.create_vehicle(vehicle_type, traffic_model, lane_change_model)
                for vehicle_type in random_vehicle_types]
