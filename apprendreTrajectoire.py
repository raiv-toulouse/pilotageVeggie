# -*- coding: utf-8 -*-

import serial
import sys,os,time
from asservissement import Asservissement
from encodersEcartTiks import *
# ENVIRONNEMENT !!
if sys.platform.startswith("linux"):
    isLINUX = True
    import tty
    import termios
else:
    isLINUX = False
    import msvcrt

SAUVEGARDE_FICHIER = True # Veut-on sauvegarder les commandes dans un fichier?

# Ne pas modifier les constantes ci-dessous
AVANT='o'
GAUCHE='i'
DROITE='p'
STOP='s'
QUIT='q'
LIGHT_GAUCHE='k'
LIGHT_DROITE='m'

VITESSE_AVANCE = 25
VITESSE_TOURNE = 30  # Pas plus que 63
VITESSE_TOURNE_AUTRE = 0
VITESSE_TOURNE_LIGHT = 20
VITESSE_TOURNE_LIGHT_AUTRE = 5

typesDeCommandes = {AVANT:'a',GAUCHE:'g',DROITE:'d',STOP:'s',QUIT:'q',LIGHT_GAUCHE:'k',LIGHT_DROITE:'l'}


def enregistrerCommande(cmd,lesCmd,lesTik,dernierEnregistrement):
    dt = encoders.pulseMG
    if dernierEnregistrement == 0:
        tik = 0
    else:
        tik = dt - dernierEnregistrement
        lesTik.append(tik)
    lesCmd.append(typesDeCommandes[cmd])
    return dt

def getChar():
    "saisie d'un caractère sans retour chariot"
    if isLINUX:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)
    else:
        return msvcrt.getch()

ass = Asservissement()
lesCmd = []
lesTik = []
dernierEnregistrement = 0
continuer = True
commandeCourante = STOP
encoders = Encoders()
encoders.start()
# Mémorisation des commandes envoyées au robot
while(continuer):
    cmd = getChar()
    if (cmd in typesDeCommandes) and (cmd != commandeCourante): # On vient de changer de commande
        commandeCourante = cmd
        dernierEnregistrement = enregistrerCommande(cmd,lesCmd,lesTik,dernierEnregistrement)
    if cmd == AVANT:
        ass.avancer(VITESSE_AVANCE)
    elif cmd == GAUCHE:
        ass.tourner(VITESSE_TOURNE_AUTRE, VITESSE_TOURNE)
    elif cmd == DROITE:
        ass.tourner(VITESSE_TOURNE, VITESSE_TOURNE_AUTRE)
    elif cmd == LIGHT_GAUCHE:
        ass.tourner(VITESSE_TOURNE_LIGHT_AUTRE, VITESSE_TOURNE_LIGHT)
    elif cmd == LIGHT_DROITE:
        ass.tourner(VITESSE_TOURNE_LIGHT, VITESSE_TOURNE_LIGHT_AUTRE)
    elif cmd == STOP:
        ass.stopper()
    elif cmd == QUIT:
        continuer = False
        ass.toutArreter()
if SAUVEGARDE_FICHIER:
    print('SAUVEGARDE_FICHIER')
    # On stocke maintenant ces commandes dans un fichier
    file = open("commandes.txt","w")
    file.write("{},{},{},{},{}\n".format(VITESSE_AVANCE, VITESSE_TOURNE, VITESSE_TOURNE_AUTRE, VITESSE_TOURNE_LIGHT, VITESSE_TOURNE_LIGHT_AUTRE))
    for i in range(len(lesTik)):
        print(i)
        if lesCmd[i]!=typesDeCommandes[STOP]:
            file.write(str(lesCmd[i])+","+str(lesTik[i])+'\n')
    file.close()
