# -*- coding: utf-8 -*-

import serial
import time
from asservissement import Asservissement

AVANT='a'
GAUCHE='g'
DROITE='d'
STOP='s'
QUIT='q'
LIGHT_GAUCHE='k'
LIGHT_DROITE='l'

ass = Asservissement()
# Lecture des commandes depuis le fichier
lesCmd = []
file = open("commandes.txt","r")
lesVitesses = file.readline().split(',')
vitesseAvance = int(lesVitesses[0])
vitesseTourne = int(lesVitesses[1])
vitesseTourneAutre = int(lesVitesses[2])
vitesseTourneLight = int(lesVitesses[3])
vitesseTourneLightAutre = int(lesVitesses[4])
for ligneCmd in file:
    l = ligneCmd.split(',')
    lesCmd.append((l[0],float(l[1])))
file.close()

# On rejoue les commandes lues
for (cmd,duree) in lesCmd:
    if cmd == AVANT:
        ass.avancer(vitesseAvance)
    elif cmd == GAUCHE:
        ass.tourner(vitesseTourneAutre,vitesseTourne)
    elif cmd == DROITE:
        ass.tourner(vitesseTourne,vitesseTourneAutre)
    elif cmd == LIGHT_GAUCHE:
        ass.tourner(vitesseTourneLightAutre, vitesseTourneLight)
    elif cmd == LIGHT_DROITE:
        ass.tourner(vitesseTourneLight,vitesseTourneLightAutre)
    time.sleep(duree)
ass.toutArreter()

