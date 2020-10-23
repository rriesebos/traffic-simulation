from traffic_models import *
from lane_change_models import *
from road import *
from vehicle_factory import VehicleFactory

import numpy as np
import matplotlib.pyplot as plt

TIME_STEP = 0.5
MAX_TIME = 1800


def main():
    intelligent_driver_model = IDM()
    mobil_model = MOBIL(right_bias=0.4)

    vehicle_factory = VehicleFactory(weights=[1.0, 0, 0, 0],
                                     default_traffic_model=intelligent_driver_model,
                                     default_lane_change_model=mobil_model)

    road = Road(length=8000, num_lanes=3, vehicle_factory=vehicle_factory, insertion_gap=10, insertion_chance=0.5,
                time_step=TIME_STEP)
    road.add_obstacle(0, 200)
    road.add_obstacle(1, 200)
    road.add_obstacle(2, 400)

    traffic_flow = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for time in time_range:

        if time > 0 and time % 60 == 0:
            traffic_flow.append(road.get_traffic_flow(at_position=10, current_time=time))

        print(f'Vehicles on the road: {len(road.vehicles)}')
        # print(f'{time}: {[(vehicle.position, vehicle.lane) for vehicle in road.vehicles]}')

        road.update()

    plt.plot([time / 60 for time in time_range if time % 60 == 0 and time > 0], traffic_flow)
    plt.show()


main()
