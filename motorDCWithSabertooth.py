# -*- coding: utf-8 -*-
import serial

LIAISON_SERIE_ACTIVE = False
SERIAL_PORT_LINUX = '/dev/ttyAMA0'
MOTEUR_GAUCHE = 192  # Indique la vitesse pour commander le moteur gauche à la vitesse 0
MOTEUR_DROIT = 64    # Indique la vitesse pour commander le moteur droit à la vitesse 0


# Classe permettant le control d'un moteur DC avec la carte Sabertooth (donc par communication série)
class MotorDCWithSabertooth():

    def __init__(self, vitesseNulle):
        self.vitesseNulle = vitesseNulle
        self.vitesseCourante = 0
        if LIAISON_SERIE_ACTIVE:
            self.ser = serial.Serial(SERIAL_PORT_LINUX, baudrate=9600, timeout=1)  # Init serial port on raspberry Pi card

    def sendSpeedMotor(self, vitesse):
        self.vitesseCourante = vitesse + self.vitesseNulle
        if LIAISON_SERIE_ACTIVE:
            self.ser.write(self.vitesseCourante.to_bytes(1, byteorder='big'))

    # A n'utiliser qu'à la fin du programme car on déconnecte la liaison série
    # Pour arrêter temporairement le moteur, faire : sendSpeedMotor(0)
    def stopMotor(self):
        self.vitesseCourante = 0
        self.sendSpeedMotor(0)
        #if LIAISON_SERIE_ACTIVE:  En commentaire car pb si on cherche à stopper 2 moteurs (le premier ferme la liaison série, nécessaire pour stopper le deuxième)
        #    self.ser.close()

    def getSpeed(self):
        return self.vitesseCourante - self.vitesseNulle

###############################################################################################################
# Programme de tests
###############################################################################################################

if __name__=="__main__":
    import time
    moteurGauche = MotorDCWithSabertooth(MOTEUR_GAUCHE)
    moteurDroit = MotorDCWithSabertooth(MOTEUR_DROIT)
    moteurGauche.sendSpeedMotor(20)
    moteurDroit.sendSpeedMotor(15)
    time.sleep(5)
    moteurGauche.sendSpeedMotor(0)
    for vit in range(15,30):
        moteurDroit.sendSpeedMotor(vit)
        time.sleep(1)
    moteurGauche.stopMotor()
    moteurDroit.stopMotor()
