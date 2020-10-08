from traffic_models import IDM
from vehicle import Vehicle

import numpy as np
import matplotlib.pyplot as plt


TIME_STEP = 0.5
MAX_TIME = 100


def main():
    intelligent_driver_model = IDM()
    car_1 = Vehicle(position=10, velocity=100 / 3.6, length=2, traffic_model=intelligent_driver_model)
    car_2 = Vehicle(position=0, velocity=80 / 3.6, length=2, traffic_model=intelligent_driver_model, next_car=car_1)

    car_1_velocities = []
    car_2_velocities = []

    car_1_accelerations = []
    car_2_accelerations = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for _ in time_range:
        car_1.update(TIME_STEP)
        car_2.update(TIME_STEP)

        car_1_velocities.append(car_1.velocity * 3.6)
        car_2_velocities.append(car_2.velocity * 3.6)

        car_1_accelerations.append(car_1.acceleration)
        car_2_accelerations.append(car_2.acceleration)

    plt.plot(time_range, car_1_velocities)
    plt.plot(time_range, car_2_velocities)
    plt.show()

    plt.plot(time_range, car_1_accelerations)
    plt.plot(time_range, car_2_accelerations)
    plt.show()


main()
