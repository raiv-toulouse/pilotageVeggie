# -*- coding: utf-8 -*-
from motorDCWithSabertooth import *
from encodersEcartTiks import *
import math
import time

VITESSE_DEMARRAGE = 25  # Vitesse au démarrage, pour sortir de la boue!
TEMPS_DEMARRAGE = 3   # Pendant TEMPS_DEMARRAGE secondes
LENT = 2     # Incrément de vitesse qd on veut corriger lentement
MOYEN = 5    # Incrément de vitesse qd on veut corriger moyennement
RAPIDE = 10  # Incrément de vitesse qd on veut corriger rapidement
VITESSE_AVANCE = 18  # Vitesse à laquelle avance le robot normalement, en l'absence de correction

# Ne pas modifier les constantes ci-dessous
A_GAUCHE = -1
TOUT_DROIT = 0
A_DROITE = 1

class Asservissement(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.moteurGauche = MotorDCWithSabertooth(MOTEUR_GAUCHE)
        self.moteurDroit = MotorDCWithSabertooth(MOTEUR_DROIT)
        self.nouvelleConsigne = False
        self.continuerAsservissement = True   # A mettre à False quand on souhaitera arrêter l'asservissement
        self.encoders = Encoders()
        self.vitesseGauche = 0
        self.vitesseDroite = 0
        self.start()

    def avancer(self,vitesse):
        self.nouvelleConsigne = True
        self.vitesseGauche = vitesse
        self.vitesseDroite = vitesse

    def stopper(self):
        self.avancer(0)

    def tourner(self,vitesseGauche,vitesseDroite):
        self.nouvelleConsigne = True
        self.vitesseGauche = vitesseGauche
        self.vitesseDroite = vitesseDroite

    def run(self):
        while self.continuerAsservissement:
            if self.nouvelleConsigne:  # On a demandé un changement de vitesse
                self.moteurGauche.sendSpeedMotor(self.vitesseGauche)
                self.moteurDroit.sendSpeedMotor(self.vitesseDroite)
                self.nouvelleConsigne = False
            else:  # On poursuit l'asservissement en cours
                if self.vitesseDroite != self.encoders.speedMD/0.9:       # asservissement moteur droit
                    self.vitesseDroite=int(self.vitesseDroite+(self.vitesseDroite-self.encoders.speedMD/0.9))
                    self.nouvelleConsigne=True  
                    time.sleep(0.1)
                if self.vitesseGauche != self.encoders.speedMG/0.9:       # asservissement moteur gauche 
                    self.vitesseGauche=int(self.vitesseGauche+(self.vitesseDroite-self.encoders.speedMG/0.9))
                    self.nouvelleConsigne=True 
                    time.sleep(0.1)
                
                time.sleep(0.1)

    def demarrage(self):
        incrementVitesse = VITESSE_DEMARRAGE / TEMPS_DEMARRAGE
        vitesse = 0
        for t in range(TEMPS_DEMARRAGE):
            vitesse += incrementVitesse
            self.avancer(int(vitesse))
            time.sleep(1)

    def corrigerVitesseMoteur(self,sens,incrementVitesse=0):
        vitesse = VITESSE_AVANCE + incrementVitesse
        if sens == A_DROITE:
            self.moteurGauche.sendSpeedMotor(vitesse)
            print('> '*incrementVitesse)
        elif sens == A_GAUCHE:  # A_GAUCHE
            self.moteurDroit.sendSpeedMotor(vitesse)
            print('< '*incrementVitesse)
        else:  # Tout droit
            self.moteurGauche.sendSpeedMotor(vitesse)
            self.moteurDroit.sendSpeedMotor(vitesse)
            print('|')

    def toutArreter(self):
        self.continuerAsservissement = False
        self.moteurGauche.stopMotor()
        self.moteurDroit.stopMotor()
        self.encoders.stopEncoder()
        #self.encoders.join()

    ###############################################################################################################
# Programme de tests
###############################################################################################################

if __name__=="__main__":
    import time
    test=True
    ass = Asservissement()
    ass.encoders.start()
    ass.demarrage()
    time.sleep(5)
    for i in range(10):
        print('MG : ', ass.encoders.speedMG, 'MD : ', ass.encoders.speedMD)
        time.sleep(1)
        
    ass.avancer(10)
    time.sleep(10)
    #ass.tourner(15,30)
    #time.sleep(5)
    #ass.tourner(30,15)
    #ass.avancer(10)
    #time.sleep(5)
    ass.stopper()
    time.sleep(5)
    ass.toutArreter()
    print('fin du test')


