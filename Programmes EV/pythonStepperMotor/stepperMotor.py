import time
import RPi.GPIO as gpio  # https://pypi.python.org/pypi/RPi.GPIO


# import exitHandler #uncomment this and line 58 if using exitHandler

class StepperMotor:
    # pins = [stepPin, directionPin, enablePin]
    def __init__(self, pins):  # instantiate stepper
        gpio.setwarnings(False)  # Désactive le mode warning

        # Setup pins
        self.pins = pins
        self.stepPin = self.pins[0]
        self.directionPin = self.pins[1]
        self.enablePin = self.pins[2]

        gpio.setmode(gpio.BCM)  # use the broadcom layout for the gpio

        # Set gpio pins
        gpio.setup(self.stepPin, gpio.OUT)
        gpio.setup(self.directionPin, gpio.OUT)
        gpio.setup(self.enablePin, gpio.OUT)

        gpio.output(self.enablePin, True)  # Set enable to high (i.e. power is NOT going to the motor)

    # Clears GPIO settings
    def cleanGPIO(self):
        gpio.output(self.enablePin, False)
        print('Stop StepperMotor')

    def step(self, steps, sens):
        gpio.output(self.directionPin, sens)  # set direction : True or False <==> Right or Left

        stepCounter = 0
        while stepCounter < steps:
            # turning the gpio on and off tells the easy driver to take one step
            gpio.output(self.stepPin, True)
            # time.sleep(0.001)
            gpio.output(self.stepPin, False)
            stepCounter = stepCounter + 1

            time.sleep(0.05)  # Wait before taking the next step thus controlling rotation speed

        gpio.output(self.stepPin, True)

        print("stepperDriver complete (" + str(steps) + " steps)")