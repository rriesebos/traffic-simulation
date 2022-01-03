# Traffic simulation


## Implementation
In this section the implementation of the traffic model is explained and the most important features are highlighted. The traffic simulation is implemented in Python.

### Longitudinal models
Two longitudinal car-following models were implemented: the Intelligent Driven Model (IDM) [^1] and Gipps' model [^2]. These models are classified as longitudinal because they are only concerned with the length-wise characteristic of traffic modelling, i.e. they only control the acceleration and deceleration (negative acceleration) of vehicles. As these models are both car-following models, the acceleration for the next time-step solely depends on the vehicle in consideration and the next vehicle on the road (referred to as the leading vehicle/leader). This leads to both models only having one method, with the following signature:
```
calculate_acceleration(self, vehicle: Vehicle, next_vehicle: Vehicle)
```
This function will calculate and return the new acceleration.

### Lane changing model
To account for vehicles wanting to move in the crosswise direction, i.e. change lane, the MOBIL lane changing model [^3] is used. This model decides if a vehicle wants to change lanes based on two criteria:
- the potential new target lane is more attractive (incentive criterion),
- the change can be performed safely (safety criterion). 

If both criteria are satisfied, a lane change is performed. Both the incentive and safety criteria use the current previous and next vehicles, as fll as the previous and next vehicles after a potential lane change. As such, the method signature is:
```
will_change_lane(self, vehicle, new_lane, old_next_vehicle: Vehicle, new_next_vehicle: Vehicle,
                 old_prev_vehicle: Vehicle, new_prev_vehicle: Vehicle, time)
```
This function will return a boolean indicating whether the vehicle wants to change lane or not. An additional feature is a controllable 'right bias'. This right bias will influence the lane change decision, and cause the vehicle to more readily make lane changes to the right, based on the provided value. This is done to simulate European laws where sticking to a left lane is discouraged. For left driving countries the right bias can be negative, leading to a left bias. A final parameter that can be controlled is the 'politeness factor'. More polite vehicles will more readily change lanes to accommodate other vehicles. For example, if a truck is driving on the left, and there is no right bias, it will still change to the right lane if a vehicle with a higher max speed is hindered by it.

### Vehicles
Different vehicles are implemented as children of the [`Vehicle`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle.py) class. [`Vehicle`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle.py) objects are instantiated with a longitudinal traffic model, an optional lane change model and five vehicle parameters used in the provided models. The vehicle parameters are as follows:
- the **length** of the vehicle;
- the **desired velocity**, corresponding to the speed limit;
- the **desired time headway**, i.e. the minimum distance to the next vehicle expressed in time;
- the **maximum acceleration**;
- the **comfortable deceleration**, the maximum deceleration after braking.

These parameters define the behaviour of the vehicle and differ for different types of vehicles. By varying the vehicle parameters, four types of vehicles were defined:
- **Cars**, length of 5 meters and a desired velocity of 100 km/h (the max speed on Dutch highways).
- **Trucks**, longer vehicles with a length of 19 meters. The desired velocity is lower than cars with 80 km/h, and the comfortable deceleration is also lower.
- **Aggressive cars**, lower time headway than regular cars and a higher comfortable deceleration. Their desired velocity is 130 km/h.
- **Passive cars**, cars that drive more carefully. The comfortable deceleration is similar to that of trucks and the desired time headway is much higher. The max acceleration is lower.

One additional class that inherits from the [`Vehicle`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle.py) class is the `Obstacle` class. While this is not a real vehicle, it can be modelled as such &mdash; a stationary vehicle with a length of zero.

All vehicles continuously keep track of innate properties such as their position on the road, the lane they are in, and their current velocity and acceleration. Furthermore, each vehicle keeps track of the next and previous vehicles in the same lane as them, as well as the gap between them and the next vehicle. Vehicles have methods to update their position, velocity, gap and lane. They use the provided longitudinal model to update their acceleration and the lane change model to decide whether they want to change lanes.

Because each vehicle keeps track of the next and previous vehicle, they can be seen as list nodes of a doubly linked list. This property is used to speed up computation in the implementation of roads, as discussed in the next section.

Following the discussed properties of a vehicle, the [`Vehicle`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle.py) class constructor signature is as follows:
```
__init__(self, position, velocity, vehicle_parameters: VehicleParameters, traffic_model,
         lane_change_model=None, next_vehicle=None, prev_vehicle=None, lane=0)
```
Where `VehicleParameters` is a named tuple. As an example, the `VehicleParameters` for regular cars are as follows:
```
CAR_PARAMETERS = VehicleParameters(
    length=5,
    desired_velocity=100 / 3.6,
    desired_time_headway=1.5,
    max_acceleration=0.3,
    comfortable_deceleration=3.0
)
```

### Road
To simulate larger amounts of vehicles, and properly integrate the lane changing model, a [`Road`](https://github.com/rriesebos/traffic-simulation/blob/master/road.py) class was added.

A road is defined by the length of the road and the number of lanes. Furthermore, the [`Road`](https://github.com/rriesebos/traffic-simulation/blob/master/road.py) class keeps track of the vehicles on the road using a list of vehicles sorted by their longitudinal position on the road, in decreasing order. I.e. the first vehicle on the road has index 0, the vehicle behind it has index 1 and so on. The `update()` method is used to update all vehicles on the road, and is defined as follows:
```
def update(self):
    self.update_accelerations()
    self.change_lanes()
    self.update_positions_velocities()

    self.sort_vehicles()

    self.generate_new_vehicles()
```
First, the acceleration of all vehicles is updated using the longitudinal model of each vehicle. 
Next, lane changes are performed for each vehicle. To do so, the list of vehicles is enumerated, and for each vehicle the lane changing model is used to check both adjacent lanes. Because of the aforementioned doubly linked list structure for the vehicles, the current next and previous vehicles are known and we do not have to iterate over the vehicle list to obtain them &mdash; improving computation time. The next and previous vehicles after a potential lane change **do** have to be computed however. This is done by iterating over the vehicle list, starting at the position of the current vehicle, until we find a vehicle that is in the same lane. Once all the vehicles affected by a lane change are obtained, the lane changing model is used to decide whether the vehicle wants to change lanes. If it does, all the previous and next vehicles are updated.
After changing lanes for all vehicles, the positions and velocities of the all vehicles are updated. This is done after changing lanes because the lane changing model anticipates future situations.
When all the vehicles are updated, we re-sort the vehicle list in order to keep it in descending order &mdash; allowing us to find the next and previous vehicles for a given lane.
Finally, new vehicles are generated and placed on the road (inserted in the vehicle list).

The generation of new vehicles allows us to easily simulate large amounts of vehicles. New vehicles, are generated by the [`VehicleFactory`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle_factory.py) class. The vehicle factory class is initialized with a list of weights representing the probability of generating each vehicle type. Furthermore, the default traffic model and lane changing models are passed as arguments to the factory class to be used for new cars if none are provided. In line with the Factory design pattern, the [`VehicleFactory`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle_factory.py) class has a `create_vehicle()` method that creates an instance of the passed in vehicle type. Additionally, methods exist to create random vehicles with a probability based on the provided weights.
Going back to the [`Road`](https://github.com/rriesebos/traffic-simulation/blob/master/road.py) class, upon instantiating a road, a [`VehicleFactory`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle_factory.py) object is provided that is used in the `generate_new_vehicles()` method. In this method we iterate over all the lanes and insert a new, randomly generated (by the [`VehicleFactory`](https://github.com/rriesebos/traffic-simulation/blob/master/vehicle_factory.py)) vehicle if the distance between the new vehicle and the next vehicle (that is already on the road) is above a certain insertion gap. Furthermore, an insertion chance controls the probability that a vehicle is actually inserted. This insertion chance is considered for each lane, so that we do not always spawn new vehicles.

While we spawn new vehicles at the start of the road, we remove vehicles if they reach the end of the road. This allows us to calculate the traffic flow at a certain point on the road. The traffic flow is calculated by summing all the vehicles ahead of the 'checkpoint', and dividing them by the current time in hours, giving us a traffic flow rate in vehicles per hour. We keep track of the amount of vehicles removed from the road, as they are included in the vehicle count ahead of a checkpoint.

One more important thing to mention, is the `add_obstacle()` method. This method is used to add `Obstacle` objects at certain positions, updating the affected vehicles. Adding obstacles to the road enables a wide range of possible situations.


### Model parameters
The model parameters are listed below.
- Time step: the time increment between each simulation step [s]
- Max time: the maximum simulation time [s]
- Longitudinal traffic model
- Lane changing model (optional)
- Vehicle factory (optional):
    - Weights: list of weights with the probabilities for each vehicle type
    - Default longitudinal traffic model
    - Default lane changing model
- Road:
    - Length: length of the road [m]
    - Number of lanes
    - Vehicle list (optional)
    - Vehicle factory (optional)
    - Insertion gap (optional)
    - Insertion chance (optional)


### Simulation
Looking at [simulation.py](https://github.com/rriesebos/traffic-simulation/blob/master/simulation.py), to simulate traffic we instantiate a longitudinal traffic model and a lane changing model with a certain right bias. We also instantiate a vehicle factory using the instantiated models as default models, and pass in a list of weights for each vehicle type. Then, we instantiate a road, passing in the length, number of lanes, vehicle factory, insertion gap and the insertion chance. Optionally, we add obstacles to the road. Noteworthy is that we can also instantiate the road without a vehicle factory, and use a pre-defined list of vehicles instead.

After setting up the simulation, we have a time loop to perform the simulation. In each iteration of this loop the `update()` method is called on the road, and traffic properties are stored to use in a visualisation step after the time loop.

[^1]: M. Treiber, A. Hennecke, and D. Helbing. Congested traffic states in empirical observations and microscopic simulations. _Physical review E_, 62(2):1805, 2000.

[^2]: P. G. Gipps. A behavioural car-following model for computer simulation. _Transportation Research Part B: Methodological_, 15(2):105–111, 1981.

[^3]: M. Treiber and D. Helbing. MOBIL: General lane-changing model for carfollowing models. _Disponível Acesso Dezembro_, 2016.
