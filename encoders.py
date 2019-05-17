# -*- coding: utf-8 -*-
import time
import RPi.GPIO as gpio  # https://pypi.python.org/pypi/RPi.GPIO
from threading import Thread

PIN_A_MOTEUR_GAUCHE = 23
PIN_B_MOTEUR_GAUCHE = 24
PIN_A_MOTEUR_DROIT = 27
PIN_B_MOTEUR_DROIT = 22

#
# Pour le moteur de gauche [Hall sensor A Vout (câble blue) broche 16, Hall sensor B Vout (câble move) broche 18]
# Pour le moteur de droite [Hall sensor A Vout (câble blue) broche 13, Hall sensor B Vout (câble move) broche 15]
#
class Encoders(Thread):
    def __init__(self):
        Thread.__init__(self)
        gpio.setwarnings(False)  # Désactive le mode warning
        # Setup pins
        gpio.setmode(gpio.BCM)  # use the broadcom layout for the gpio
        gpio.setup(PIN_A_MOTEUR_GAUCHE, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(PIN_B_MOTEUR_GAUCHE, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(PIN_A_MOTEUR_DROIT, gpio.IN, pull_up_down=gpio.PUD_UP)  # Inutilisée pour le moment car on ne se préocupe pas du sens de rotation
        gpio.setup(PIN_B_MOTEUR_DROIT, gpio.IN, pull_up_down=gpio.PUD_UP)
        self.flagRunning = True  #
        self.pulseMG = 0
        self.speedMG = 0
        self.pulseMD = 0
        self.speedMD = 0
        gpio.add_event_detect(PIN_A_MOTEUR_GAUCHE, gpio.RISING, callback=self._pulseMG, bouncetime=10)
        gpio.add_event_detect(PIN_A_MOTEUR_DROIT, gpio.RISING, callback=self._pulseMD, bouncetime=10)

    def run(self):
        start = time.time()
        while self.flagRunning == True:
            if time.time() - start >= 1:
                self.speedMG = self.pulseMG
                self.speedMD = self.pulseMD
                self.pulseMG = 0
                self.pulseMD = 0
                start = time.time()

    def _pulseMG(self, pin):
        self.pulseMG = self.pulseMG + 1

    def _pulseMD(self, pin):
        self.pulseMD = self.pulseMD + 1

    def stopEncoder(self):
        self.flagRunning = False
        time.sleep(2)  # pour permettre à la méthode run du thread de se terminer correctement
        gpio.cleanup()

###############################################################################################################
# Programme de tests
###############################################################################################################

if __name__=="__main__":
    from motorDCWithSabertooth import *
    import time

    moteurGauche = MotorDCWithSabertooth(MOTEUR_GAUCHE)
    moteurDroit = MotorDCWithSabertooth(MOTEUR_DROIT)
    encoders = Encoders()
    moteurGauche.sendSpeedMotor(5)
    moteurDroit.sendSpeedMotor(30)
    encoders.start()
    for i in range(10):
        print("======+=======")
        print(encoders.speedMG)
        print(encoders.speedMD)
        time.sleep(1)
    moteurGauche.stopMotor()
    moteurDroit.stopMotor()
    encoders.stopEncoder()
    encoders.join()

