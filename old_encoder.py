# -*- coding: utf-8 -*-
import time
import RPi.GPIO as gpio  # https://pypi.python.org/pypi/RPi.GPIO
from threading import Thread

PIN_A_MOTEUR_GAUCHE = 23
PIN_B_MOTEUR_GAUCHE = 24
PIN_A_MOTEUR_DROIT = 27
PIN_B_MOTEUR_DROIT = 22


class Encoder(Thread):
    # pinA = Hall Sensor A, pinB = Hall Sensor B
    def __init__(self, pinA, pinB):
        Thread.__init__(self)
        gpio.setwarnings(False)  # Désactive le mode warning
        # Setup pins
        self.pinA = pinA
        self.pinB = pinB
        gpio.setmode(gpio.BCM)  # use the broadcom layout for the gpio
        gpio.setup(self.pinA, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.pinB, gpio.IN, pull_up_down=gpio.PUD_UP)
        self.flagRunning = True  #
        self.pulse = 0
        self.speed = 0
        gpio.add_event_detect(self.pinA, gpio.RISING, callback=self._pulse, bouncetime=10)

    def run(self):
        start = time.time()
        while self.flagRunning == True:
            if time.time() - start >= 1:
                self.speed = self.pulse
                self.pulse = 0
                start = time.time()

    def _pulse(self, pin):
        self.pulse = self.pulse + 1


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
    decoderMG = Encoder(PIN_A_MOTEUR_GAUCHE, PIN_B_MOTEUR_GAUCHE)  # Pour le moteur de gauche [Hall sensor A Vout (câble blue) broche 16, Hall sensor B Vout (câble move) broche 18]
    decoderMD = Encoder(PIN_A_MOTEUR_DROIT, PIN_B_MOTEUR_DROIT)  # Pour le moteur de droite [Hall sensor A Vout (câble blue) broche 13, Hall sensor B Vout (câble move) broche 15]

    moteurGauche.sendSpeedMotor(20)
    moteurDroit.sendSpeedMotor(20)
    decoderMG.start()
    decoderMD.start()

    for i in range(10):
        print(decoderMG.speed)
        print(decoderMD.speed)
        time.sleep(1)

    moteurGauche.stopMotor()
    moteurDroit.stopMotor()

    decoderMG.stopEncoder()
    decoderMD.stopEncoder()

    decoderMG.join()
    decoderMD.join()
