from traffic_models import *
from lane_change_models import *
from vehicle import *
from road import *

import numpy as np
import matplotlib.pyplot as plt

TIME_STEP = 0.5
MAX_TIME = 600


def main():
    intelligent_driver_model = IDM()
    mobil_model = MOBIL(right_bias=0)
    vehicle_factory = VehicleFactory(weights=[1.0, 0, 0, 0],
                                     default_traffic_model=intelligent_driver_model,
                                     default_lane_change_model=mobil_model)

    vehicle_list = [vehicle_factory.create_vehicle(vehicle_type=VehicleType.PassiveCar)]

    road = Road(length=200000, num_lanes=1, vehicles=vehicle_list, time_step=TIME_STEP)
    road.add_obstacle(0, 5000)

    velocities = []
    accelerations = []
    positions = []
    gap = []
    lanes = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for t in time_range:
        velocities_temp = []
        accelerations_temp = []
        positions_temp = []
        gap_temp = []
        lanes_temp = []

        if t == 175:
            road.remove_obstacle(0, 5000)

        for vehicle in road.vehicles:
            if isinstance(vehicle, Obstacle):
                continue

            velocities_temp.append(vehicle.velocity * 3.6)
            accelerations_temp.append(vehicle.acceleration)
            positions_temp.append(vehicle.position)
            gap_temp.append(vehicle.gap)
            lanes_temp.append(vehicle.lane)

        velocities.append(velocities_temp)
        accelerations.append(accelerations_temp)
        positions.append(positions_temp)
        gap.append(gap_temp)
        lanes.append(lanes_temp)

        road.update()

    plt.plot(time_range, velocities)
    plt.show()

    plt.plot(time_range, accelerations)
    plt.show()

    plt.plot(time_range, positions)
    plt.show()

    plt.plot(time_range, gap)
    plt.show()

    plt.plot(time_range, lanes)
    plt.show()


main()
