class Road:
    DEFAULT_NUM_LANES = 1
    DEFAULT_TIME_STEP = 0.5

    def __init__(self, length, vehicles=None, num_lanes=DEFAULT_NUM_LANES, time_step=DEFAULT_TIME_STEP):
        self.num_lanes = num_lanes
        self.length = length
        self.time_step = time_step

        # List of vehicles sorted by their longitudinal position on the road, in decreasing order
        # I.e. the first vehicle on the road has index 0, the vehicle behind it has index 1 and so on
        self.vehicles = [] if vehicles is None else vehicles

    def update(self):
        self.update_accelerations()
        self.change_lanes()
        self.update_positions_velocities()

        self.vehicles.sort(key=lambda x: x.position, reverse=True)

    def update_accelerations(self):
        for vehicle in self.vehicles:
            vehicle.update_acceleration(self.time_step)

    def change_lanes(self):
        for i, vehicle in enumerate(self.vehicles):
            new_lanes = [vehicle.lane - 1, vehicle.lane + 1]
            for new_lane in new_lanes:
                # Check if the new lane is valid
                if not 0 <= new_lane < self.num_lanes:
                    continue

                new_next_vehicle = self.get_next_vehicle(new_lane, i)
                old_prev_vehicle = self.get_prev_vehicle(vehicle.lane, i)
                new_prev_vehicle = self.get_prev_vehicle(new_lane, i)

                if vehicle.will_change_lane(new_next_vehicle, old_prev_vehicle, new_prev_vehicle):
                    vehicle.change_lane(new_next_vehicle, new_lane)
                    break

    def update_positions_velocities(self):
        for vehicle in self.vehicles:
            vehicle.update_position(self.time_step)
            vehicle.update_velocity(self.time_step)

    def get_next_vehicle(self, lane, index):
        if lane >= self.num_lanes:
            return

        for i in range(index - 1, -1, -1):
            vehicle = self.vehicles[i]

            if vehicle.lane == lane:
                return vehicle

        return None

    def get_prev_vehicle(self, lane, index):
        if lane >= self.num_lanes:
            return

        for i in range(index + 1, len(self.vehicles)):
            vehicle = self.vehicles[i]

            if vehicle.lane == lane:
                return vehicle

        return None
