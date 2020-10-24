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

    car_1 = Car(position=50, velocity=100 / 3.6, traffic_model=intelligent_driver_model,
                lane_change_model=mobil_model)
    car_2 = Car(position=20, velocity=80 / 3.6, traffic_model=intelligent_driver_model,
                lane_change_model=mobil_model, next_vehicle=car_1)
    truck_1 = Truck(position=10, velocity=60 / 3.6, traffic_model=intelligent_driver_model,
                    lane_change_model=mobil_model, next_vehicle=car_2)
    car_1.prev_vehicle = car_2
    car_2.prev_vehicle = truck_1
    vehicle_list = [car_1, car_2, truck_1]

    road = Road(length=200000, num_lanes=2, vehicles=vehicle_list, time_step=TIME_STEP)
    road.add_obstacle(0, 5000)

    velocities = []
    accelerations = []
    positions = []
    gap = []
    lanes = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for _ in time_range:
        velocities_temp = []
        accelerations_temp = []
        positions_temp = []
        gap_temp = []
        lanes_temp = []

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
