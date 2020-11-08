from traffic_models import *
from lane_change_models import *
from road import *
import os

import numpy as np
import matplotlib.pyplot as plt

TIME_STEP = 0.5
MAX_TIME = 600

NUM_LANES = 1

SCENARIO_NAME = 'braking'


def plot(time_range, velocities, accelerations, positions, gap, lanes, labels, traffic_model, num_lanes):
    if not os.path.exists(SCENARIO_NAME):
        os.makedirs(SCENARIO_NAME)

    plt.plot(time_range, velocities)
    plt.title("Velocities over time")
    plt.xlabel("Time in seconds")
    plt.ylabel("Velocity in km/h")
    plt.legend(labels, loc="lower right")
    plt.savefig(f'{SCENARIO_NAME}/velocities_{traffic_model}.png')
    plt.show()

    plt.plot(time_range, accelerations)
    plt.title("Accelerations over time")
    plt.xlabel("Time in seconds")
    plt.ylabel(r"Acceleration in $\mathregular{m/s^2}$")
    plt.legend(labels, loc="lower right")
    plt.savefig(f'{SCENARIO_NAME}/accelerations_{traffic_model}.png')
    plt.show()

    plt.plot(time_range, positions)
    plt.title("Positions over time")
    plt.xlabel("Time in seconds")
    plt.ylabel("Position in meters")
    plt.legend(labels, loc="lower right")
    plt.savefig(f'{SCENARIO_NAME}/positions_{traffic_model}.png')
    plt.show()

    plt.plot(time_range, gap)
    plt.title("Gap to front vehicles over time")
    plt.xlabel("Time in seconds")
    plt.ylabel("Gap in meters")
    plt.legend(labels, loc="lower right")
    plt.savefig(f'{SCENARIO_NAME}/gaps_{traffic_model}.png')
    plt.show()

    plt.plot(time_range, lanes)
    plt.title("Lanes over time")
    plt.xlabel("Time in seconds")
    plt.ylabel("Lane (indexed from left to right)")
    plt.yticks([i for i in range(num_lanes)])
    plt.legend(labels, loc="lower right")
    plt.savefig(f'{SCENARIO_NAME}/lanes_{traffic_model}.png')
    plt.show()


def main():
    traffic_model = IDM()
    mobil_model = MOBIL(right_bias=0.6)
    vehicle_factory = VehicleFactory(weights=[1.0, 0, 0, 0],
                                     default_traffic_model=traffic_model,
                                     default_lane_change_model=mobil_model)

    vehicle_list = vehicle_factory.create_random_vehicle_row(num=5, spacing=200, lane=0)
    road = Road(length=200000, num_lanes=NUM_LANES, vehicles=vehicle_list, time_step=TIME_STEP)

    road.add_obstacle(0, 5000)

    velocities = []
    accelerations = []
    positions = []
    gap = []
    lanes = []

    time_range = np.arange(0, MAX_TIME, TIME_STEP)
    for time in time_range:
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

        road.update(time)

    labels = [f'{v.__class__.__name__} {i + 1}'
              for i, v in enumerate([veh for veh in vehicle_list if not isinstance(veh, Obstacle)])]
    traffic_model_name = traffic_model.__class__.__name__
    plot(time_range, velocities, accelerations, positions, gap, lanes, labels, traffic_model_name, num_lanes=NUM_LANES)


main()
