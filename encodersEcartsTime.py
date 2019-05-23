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
        self.flagRunning = True  #vérification toujours vrai, on mesure en continue les données des encoders 
        self.pulseMG = 0
        self.speedMG = 0
        self.pulseMD = 0
        self.speedMD = 0
        self.compteur =0        # utiliser pour la moyenne tirée   
        self.speedfinalMG=[]
        self.speedfinalMD=[]
        self.moyennespeedMG=0
        self.moyennespeedMD=0
        self.testMG=0
        self.testMD=0
        gpio.add_event_detect(PIN_A_MOTEUR_GAUCHE, gpio.RISING, callback=self._pulseMG, bouncetime=1)
        gpio.add_event_detect(PIN_A_MOTEUR_DROIT, gpio.RISING, callback=self._pulseMD, bouncetime=1)

    def run(self):
        while self.flagRunning == True:
            self.testMG=self.pulseMG
            self.testMD=self.pulseMD
            
            if self.testMG==1:             # moteur gauche 
                start = time.time() # on lance le chrono 
                
            if self.testMG ==20:
                end = time.time() # on arrête de chrono au deuxième front montant 
                self.speedMG= end - start  # temps entre les deux fronts montants 
                self.speedfinalMG.append(self.speedMG)
                self.pulseMG=0
                self.compteur=self.compteur+1
                
            if self.testMD ==1 :        # moteur droit 
                start= time.time()
                
            if self.testMD == 20:
                end = time.time()
                self.speedMD = end-start
                self.speedfinalMD.append(self.speedMD)  
                self.pulseMD= 0 
                

            if self.compteur >4: # Moyenne des 4 dernières vitesses relevées
                self.moyennespeedMG=((self.speedfinalMG[-4]+self.speedfinalMG[-3]+self.speedfinalMG[-2]+self.speedfinalMG[-1])/196)*980   
                self.moyennespeedMD=((self.speedfinalMD[-4]+self.speedfinalMD[-3]+self.speedfinalMD[-2]+self.speedfinalMD[-1])/196)*980



                
                
                    
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
    
    encoders.start()
    moteurGauche.sendSpeedMotor(10)
    moteurDroit.sendSpeedMotor(60)
    
    for i in range(1000):
        print("======+=======")
        #print(encoders.compteurMG)
        #print(encoders.pulseMG)
        print(encoders.compteur)
        print(encoders.pulseMD)
        print(encoders.moyennespeedMG)
        print(encoders.moyennespeedMD)
        time.sleep(0.01)
            
    moteurGauche.stopMotor()
    moteurDroit.stopMotor()
    encoders.stopEncoder()
    encoders.join()

