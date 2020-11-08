from vehicle_factory import VehicleFactory
from vehicle import Obstacle
import random


class Road:
    DEFAULT_NUM_LANES = 1
    DEFAULT_TIME_STEP = 0.5
    DEFAULT_INSERTION_GAP = 10
    DEFAULT_INSERTION_CHANCE = 0.5

    """
    Args:
        length: length of the road [m]
        num_lanes: number of lanes the road has
        vehicles: list of vehicles sorted by their longitudinal position on the road, in decreasing order
                  i.e. the first vehicle on the road has index 0, the vehicle behind it has index 1 and so on
        vehicle_factory: object used to generate new vehicles, if None no new vehicles are generated
        time_step: time step for the simulation
    """
    def __init__(self, length, num_lanes=DEFAULT_NUM_LANES, vehicles=None, vehicle_factory: VehicleFactory = None,
                 insertion_gap=DEFAULT_INSERTION_GAP, insertion_chance=DEFAULT_INSERTION_CHANCE,
                 time_step=DEFAULT_TIME_STEP):
        self.length = length
        self.num_lanes = num_lanes

        self.vehicles = [] if vehicles is None else vehicles
        self.sort_vehicles()

        self.vehicle_factory = vehicle_factory
        self.insertion_gap = insertion_gap

        self.insertion_chance = insertion_chance
        self.time_step = time_step

        self.removed_vehicle_count = 0

    def update(self):
        self.update_accelerations()
        self.change_lanes()
        self.update_positions_velocities()

        self.sort_vehicles()

        self.generate_new_vehicles()

    def update_accelerations(self):
        for vehicle in self.vehicles:
            vehicle.update_acceleration()

    def change_lanes(self):
        for i, vehicle in enumerate(self.vehicles):
            if vehicle.lane_change_model is None or isinstance(vehicle, Obstacle):
                continue

            # Note: lanes are indexed from left to right
            new_lanes = [vehicle.lane - 1, vehicle.lane + 1]
            for new_lane in new_lanes:
                # Check if the new lane is valid
                if not 0 <= new_lane < self.num_lanes:
                    continue

                new_next_vehicle = self.get_next_vehicle(new_lane, i)
                new_prev_vehicle = self.get_prev_vehicle(new_lane, i)

                if vehicle.will_change_lane(new_lane, new_next_vehicle, new_prev_vehicle):
                    if vehicle.prev_vehicle is not None:
                        vehicle.prev_vehicle.next_vehicle = vehicle.next_vehicle

                    if vehicle.next_vehicle is not None:
                        vehicle.next_vehicle.prev_vehicle = vehicle.prev_vehicle

                    vehicle.change_lane(new_next_vehicle, new_prev_vehicle, new_lane)

                    if new_prev_vehicle is not None:
                        new_prev_vehicle.next_vehicle = vehicle

                    if new_next_vehicle is not None:
                        new_next_vehicle.prev_vehicle = vehicle

                    break

    def update_positions_velocities(self):
        vehicle_indices_to_delete = []
        for i in range(len(self.vehicles)):
            vehicle = self.vehicles[i]
            vehicle.update_position(self.time_step)

            if vehicle.position > self.length:
                vehicle_indices_to_delete.append(i)
                continue

            vehicle.update_velocity(self.time_step)

        self.removed_vehicle_count += len(vehicle_indices_to_delete)

        # Remove vehicles from road that reached the end of the road
        for i in vehicle_indices_to_delete:
            del self.vehicles[i]

    def sort_vehicles(self):
        self.vehicles.sort(key=lambda x: x.position, reverse=True)

    def get_next_vehicle(self, lane, index):
        if lane >= self.num_lanes:
            return None

        if not self.vehicles or not 0 < index <= len(self.vehicles):
            return None

        if len(self.vehicles) == 1 and self.vehicles[0].lane == lane:
            return self.vehicles[0]

        for i in range(index - 1, -1, -1):
            vehicle = self.vehicles[i]

            if vehicle.lane == lane:
                return vehicle

        return None

    def get_prev_vehicle(self, lane, index):
        if lane >= self.num_lanes:
            return None

        if not self.vehicles or not 0 <= index < len(self.vehicles):
            return None

        for i in range(index + 1, len(self.vehicles)):
            vehicle = self.vehicles[i]

            if vehicle.lane == lane:
                return vehicle

        return None

    def generate_new_vehicles(self):
        if self.vehicle_factory is None:
            return

        for lane in range(self.num_lanes):
            if random.random() > self.insertion_chance:
                continue

            new_vehicle = self.vehicle_factory.create_random_vehicle()
            new_vehicle.lane = lane

            next_vehicle = self.get_next_vehicle(lane, len(self.vehicles))

            if next_vehicle is None:
                distance = self.length
            else:
                distance = new_vehicle.calculate_gap(next_vehicle)

            if distance >= self.insertion_gap:
                if next_vehicle is not None:
                    new_vehicle.next_vehicle = next_vehicle
                    next_vehicle.prev_vehicle = new_vehicle

                self.vehicles.append(new_vehicle)

    """
        Args:
            at_position: position at which to measure the traffic flow [m]
            current_time: current time elapsed in the simulation
            
        Returns:
            The traffic flow [vehicles/hour]
    """
    def get_traffic_flow(self, at_position, current_time):
        if not 0 <= at_position <= self.length:
            return -1

        vehicles_passed_point = (sum(vehicle.position > at_position for vehicle in self.vehicles)
                                 + self.removed_vehicle_count)
        return vehicles_passed_point / (current_time / 3600)

    def add_obstacle(self, lane, at_position):
        if not 0 <= lane < self.num_lanes:
            return

        obstacle = Obstacle()
        obstacle.lane = lane
        obstacle.position = at_position

        if self.vehicles:
            for i, vehicle in enumerate(self.vehicles):
                if vehicle.position < at_position and vehicle.lane == lane:
                    next_vehicle = vehicle.next_vehicle
                    if next_vehicle is not None:
                        next_vehicle.prev_vehicle = obstacle

                    vehicle.next_vehicle = obstacle
                    obstacle.prev_vehicle = vehicle
                    vehicle.update_gap()
                    break

        self.vehicles.append(obstacle)
        self.sort_vehicles()

    def remove_obstacle(self, lane, at_position):
        if not 0 <= lane < self.num_lanes:
            return

        if self.vehicles:
            obstacle = None
            for i, vehicle in enumerate(self.vehicles):
                if isinstance(vehicle, Obstacle) and vehicle.position == at_position and vehicle.lane == lane:
                    if vehicle.prev_vehicle is not None:
                        vehicle.prev_vehicle.next_vehicle = vehicle.next_vehicle

                    if vehicle.next_vehicle is not None:
                        vehicle.next_vehicle.prev_vehicle = vehicle.prev_vehicle

                    break

            if obstacle is not None:
                self.vehicles.remove(obstacle)
