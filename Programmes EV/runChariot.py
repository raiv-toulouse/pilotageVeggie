# -*- coding: utf-8 -*-
#
from pythonStepperMotor.stepperMotor import StepperMotor
from pythonElectroVanne.electroVanne import ElectroVanne
from pythonRpiCamera.rpiCamera import RpiCamera
from threading import Thread
import time



class TestChariot(Thread):
    def __init__(self, camera, stepperMotor, electroVanne):
        super().__init__()
        self.camera = camera
        self.stepperMotor = stepperMotor
        self.electroVanne = electroVanne

        self._isRunning = True

    # La fonction principale qui déroule toutes les phases des épreuves du chariot
    def run(self):
        print('je suis run')
        while self._isRunning:
            self.camera.traiterImage()
            if len(self.camera.cX) != 0 or len(self.camera.cY) != 0:
                print('je suis if ', self.camera.cX, len(self.camera.cX), self.camera.cX[0])
                for i in range(len(self.camera.cX)):
                    if 10 <= self.camera.cY[i] <= 300:
                        self.camera.cX[i]
                        if self.camera.cX[i] <= 90:
                            steps = 10
                        elif self.camera.cX[i] <= 240:
                            steps = 20
                        elif self.camera.cX[i] <= 425:
                            steps = 30
                        elif self.camera.cX[i] <= 575:
                            steps = 40
                        else:
                            steps = 50

                        self.stepperMotor.step(steps, True)  # steps, dir = True ==> Right direction
                        self.electroVanne.spray(True)  # steps, dir = True ==> Right direction
                        time.sleep(0.1)
                        self.electroVanne.spray(False)  # steps, dir = False ==> Left direction
                        self.stepperMotor.step(steps, False)  # steps, dir = False ==> Left direction


    def stop(self):
        print("Fin")
        self._isRunning = False
        time.sleep(0.2)
        self.stepperMotor.cleanGPIO()
        self.electroVanne.cleanGPIO()


#####################################################################################################
if __name__ == "__main__":
    camera = RpiCamera()
    stepperMotor = StepperMotor([22, 17, 27])  # [stepPin, directionPin, enablePin]
    electroVanne = ElectroVanne(18)  # Connecteur 12

    test = TestChariot(camera, stepperMotor, electroVanne)
    test.start()   # Lance la séquence de toutes les épreuves
    time.sleep(5)
    test.stop()






