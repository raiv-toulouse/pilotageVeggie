# -*- coding: utf-8 -*-
#
from rpiCamera import RpiCamera
from threading import Thread
import time


class TestRpiCamera(Thread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self._isRunning = True

    # La fonction principale qui déroule toutes les phases de l'épreuve
    def run(self):
        while self._isRunning:
            self.camera.traiterImage()
            print(self.camera.cX, self.camera.cY)

    def stop(self):
        print("Fin")
        self._isRunning = False
        time.sleep(0.2)


#####################################################################################################
if __name__ == "__main__":
    camera = RpiCamera()
    test = TestRpiCamera(camera)
    test.start()   # Lance la séquence de toutes les épreuves
    time.sleep(5)
    test.stop()