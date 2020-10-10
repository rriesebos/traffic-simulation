from traffic_models import IDM
from vehicle import *

import numpy as np
import matplotlib.pyplot as plt


TIME_STEP = 0.5
MAX_TIME = 100


def main():
    intelligent_driver_model = IDM()

    # TODO: Change dummy data to randomly? generated list
    car_1 = Car(position=50, velocity=100 / 3.6, traffic_model=intelligent_driver_model)
    car_2 = Car(position=20, velocity=80 / 3.6, traffic_model=intelligent_driver_model, next_vehicle=car_1)
    truck_1 = Truck(position=10, velocity=60 / 3.6, traffic_model=intelligent_driver_model, next_vehicle=car_2)
    vehicle_list = [car_1, car_2, truck_1]

    velocities = []
    accelerations = []
    positions = []
    gap = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for _ in time_range:
        velocities_temp = []
        accelerations_temp = []
        positions_temp = []
        gap_temp = []

        for vehicle in vehicle_list:
            vehicle.update(delta_t=TIME_STEP)
            velocities_temp.append(vehicle.velocity * 3.6)
            accelerations_temp.append(vehicle.acceleration)
            positions_temp.append(vehicle.position)
            gap_temp.append(vehicle.gap)

        velocities.append(velocities_temp)
        accelerations.append(accelerations_temp)
        positions.append(positions_temp)
        gap.append(gap_temp)

    plt.plot(time_range, velocities)
    plt.show()

    plt.plot(time_range, accelerations)
    plt.show()
    
    plt.plot(time_range, positions)
    plt.show()

    plt.plot(time_range, gap)
    plt.show()

main()
