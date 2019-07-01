from stepperMotor import StepperMotor
import time


# [stepPin, directionPin, enablePin]
testStepperMotor = StepperMotor([22, 17, 27])
time.sleep(0.1)

# Test stepper
testStepperMotor.step(50, False)  # steps, dir = True ==> Right direction
time.sleep(10)
testStepperMotor.step(50, True)  # steps, dir = False ==> Left direction

time.sleep(0.1)
testStepperMotor.cleanGPIO()
