from electroVanne import ElectroVanne
import time


# [stepPin, directionPin, enablePin]
testElectroVanne = ElectroVanne(18)  # Connecteur 12
time.sleep(0.1)

# Test Electrovanne
testElectroVanne.spray(True)  # steps, dir = True ==> Right direction
time.sleep(0.1)
testElectroVanne.spray(False)  # steps, dir = False ==> Left direction

time.sleep(0.1)
testElectroVanne.cleanGPIO()
