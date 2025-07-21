class PIDController:
    def __init__(self, Kp=0.5, Ki=0.0, Kd=0.1):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.previous_error = 0
        self.integral = 0

    def reset(self):
        self.previous_error = 0
        self.integral = 0

    def compute(self, error):
        self.integral += error
        derivative = error - self.previous_error
        self.previous_error = error

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        return output
