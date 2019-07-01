# -*- coding: utf-8 -*-
#
from webcamProcessing import WebcamProcessing
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import numpy as np
from asservissement import *
from encodersEcartTiks import *

OFFSET_LENT = 30
OFFSET_MOYEN = 40
OFFSET_RAPIDE = 60

class Controler(QThread):
    def __init__(self,webcam):
        super().__init__()
        self.webcam = webcam
        self.webcam.dataFromImage.connect(self.tracking)
        self.lesOffsets = []
        self.asservissement = Asservissement()
        self.trackingEnCours = False

    def avancerDansRang(self):
        self.webcam.nbNonDetections = 3
        self.trackingEnCours = True
        while self.trackingEnCours:
            self.webcam.traiterImage()

    # Quand le traitement de l'image retourne les informations de tracking permettant l'asservissement dans le rang de maïs
    def tracking(self, finRangee, offset, milieuImage):
        if finRangee:
            self.trackingEnCours = False  # On a fini de se déplacer dans ce rang de maïs, on doit passer à l'étape suivante
        else:
            self.lesOffsets.append(offset)
            if len(self.lesOffsets)>5: # On veut faire une moyenne glissante sur 5 offsets
                self.lesOffsets = self.lesOffsets[1:] # On supprime le premier élément
            offsetMoyen = np.mean(self.lesOffsets)
            # On avance tout droit
            if milieuImage - OFFSET_LENT < offsetMoyen < milieuImage + OFFSET_LENT:
                self.asservissement.corrigerVitesseMoteur(TOUT_DROIT)
            # On tourne à gauche
            elif milieuImage - OFFSET_MOYEN < offsetMoyen <= milieuImage - OFFSET_LENT:
                self.asservissement.corrigerVitesseMoteur(A_GAUCHE,LENT)
            elif milieuImage - OFFSET_RAPIDE < offsetMoyen <= milieuImage - OFFSET_MOYEN:
                self.asservissement.corrigerVitesseMoteur(A_GAUCHE,MOYEN)
            elif offsetMoyen <= milieuImage - OFFSET_RAPIDE:
                self.asservissement.corrigerVitesseMoteur(A_GAUCHE, RAPIDE)
            # On tourne à droite
            elif milieuImage + OFFSET_LENT < offsetMoyen <= milieuImage + OFFSET_MOYEN:
                self.asservissement.corrigerVitesseMoteur(A_DROITE,LENT)
            elif milieuImage + OFFSET_MOYEN < offsetMoyen <= milieuImage + OFFSET_RAPIDE:
                self.asservissement.corrigerVitesseMoteur(A_DROITE,MOYEN)
            elif offsetMoyen >= milieuImage + OFFSET_RAPIDE:
                self.asservissement.corrigerVitesseMoteur(A_DROITE, RAPIDE)

    def demiTour(self):
        print("============== Début du demi tour")
        # Lecture des commandes depuis le fichier
        lesCmd = []
        file = open("commandes.txt", "r")
        lesVitesses = file.readline().split(',')
        vitesseAvance = int(lesVitesses[0])
        vitesseTourne = int(lesVitesses[1])
        vitesseTourneAutre = int(lesVitesses[2])
        vitesseTourneLight = int(lesVitesses[3])
        vitesseTourneLightAutre = int(lesVitesses[4])
        for ligneCmd in file:
            l = ligneCmd.split(',')
            lesCmd.append((l[0], float(l[1])))
        file.close()
        # On rejoue les commandes lues
        encoders=Encoders()
        encoders.start()
        for (cmd, duree) in lesCmd:
            while encoders.pulseMG != dureee :
                if cmd == 'a':
                    print('Avance')
                    self.asservissement.avancer(vitesseAvance)
                elif cmd == 'g':
                    print('Gauche')
                    self.asservissement.tourner(vitesseTourne, vitesseTourneAutre)  # A gauche
                elif cmd == 'd':
                    print('Droite')
                    self.asservissement.tourner(vitesseTourneAutre, vitesseTourne)  # A droite
                elif cmd == 'm':
                    print('Légèrement à gauche')
                    self.asservissement.tourner(vitesseTourneLight, vitesseTourneLightAutre)  # Légèrement à gauche
                elif cmd == 'k':
                    print('Légèrement à droite')
                    self.asservissement.tourner(vitesseTourneLightAutre, vitesseTourneLight)  # Légèrement à droite
            encoders.pulseMG=0
        self.asservissement.stopper()
        print("============== Fin du demi tour")

    # On quitte tout
    def finEpreuve(self):
        print("Fin de l'épreuve")
        self.asservissement.toutArreter()
        self.exit()

    # La fonction principale qui déroule toutes les phases de l'épreuve
    def run(self):
        self.avancerDansRang()
        #self.demiTour()
        #self.avancerDansRang()
        self.finEpreuve()

#####################################################################################################
if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    webcam = WebcamProcessing()
    controler = Controler(webcam)
    controler.start()   # Lance la séquence de toutes les épreuves
    app.exec_()