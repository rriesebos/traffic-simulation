class Vehicle:
    def __init__(self, position, velocity, length, traffic_model, next_car=None):
        self.position = position
        self.velocity = velocity
        self.acceleration = 0

        self.length = length

        self.traffic_model = traffic_model

        self.next_car = next_car

    def update_position(self, delta_t):
        self.position += delta_t * self.velocity + 0.5 * self.acceleration * delta_t ** 2

    def update_velocity(self, delta_t):
        self.velocity += max(0, delta_t * self.acceleration)

    def update_acceleration(self):
        # If this vehicle is the leader, do not update the acceleration
        if self.next_car is None:
            return

        self.acceleration = self.traffic_model.calculate_acceleration(self.calculate_gap(),
                                                                      self.velocity,
                                                                      self.next_car.velocity)

    def calculate_gap(self):
        if self.next_car is None:
            return 0

        return self.next_car.position - self.position - self.next_car.length

    def update(self, delta_t):
        self.update_acceleration()
        self.update_velocity(delta_t)
        self.update_position(delta_t)
