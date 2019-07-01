import time
import RPi.GPIO as gpio  # https://pypi.python.org/pypi/RPi.GPIO


# import exitHandler #uncomment this and line 58 if using exitHandler

class ElectroVanne:
    # Pins = [stepPin, directionPin, enablePin]
    def __init__(self, pin):  # instantiate stepper
        gpio.setwarnings(False)  # Désactive le mode warning

        # Setup pin
        self.tensionPin = pin

        gpio.setmode(gpio.BCM)  # use the broadcom layout for the gpio

        gpio.setup(self.tensionPin, gpio.OUT)  # Set gpio pins


    #  Clears GPIO settings
    def cleanGPIO(self):
        print('Stop Electro-vanne')
        # gpio.cleanup()

    def spray(self, flag):
        if flag == True:
            gpio.output(self.tensionPin, gpio.HIGH)
        else:
            gpio.output(self.tensionPin, gpio.LOW)


        print("Pulverization " + str(flag))