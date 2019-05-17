# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread,QTimer,pyqtSignal,QObject
import cv2
import numpy as np

### Constantes que l'on peut adapter
###
DEBUT_MASK = 120   # Coordonnée Y (en pixel) du début de la bande pour la recherche des maïs
HAUTEUR_MASK = 60  # Hauteur (en pixel) de cette bande
SEUIL_NON_DETECTION = 30  # Nb de non détections de plante consécutives avant de décider que l'on est en bout de rangée
FPS = 5  #Frames Per Second
###

class WebcamProcessing(QObject):
    # Définition des signaux
    dataFromImage = pyqtSignal(bool,int,int)
    imageAvailable = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FPS, FPS)
        self.initSeuilsHSV()
        self.kernel = np.ones((5, 5), np.uint8)
        self.nbNonDetections = 0

    def ajoutIhm(self,ihm):
        self.ihm = ihm
        self.ihm.chgtSeuils.connect(self.majSeuils)

    def majSeuils(self, Hmin, Hmax, Smin, Smax, Vmin, Vmax):
        self.Hmin = Hmin
        self.Hmax = Hmax
        self.Smin = Smin
        self.Smax = Smax
        self.Vmin = Vmin
        self.Vmax = Vmax

    def initSeuilsHSV(self):
        # Initialisation des seuils pour le filtrage HSV
        file = open("reglagesHSV.txt", "r")
        lesReglagesHSV = file.readline().split(',')
        file.close()
        self.Hmin = int(lesReglagesHSV[0])
        self.Hmax = int(lesReglagesHSV[1])
        self.Smin = int(lesReglagesHSV[2])
        self.Smax = int(lesReglagesHSV[3])
        self.Vmin = int(lesReglagesHSV[4])
        self.Vmax = int(lesReglagesHSV[5])

    # Appelée chaque fois qu'une nouvelle image est acquise
    def traiterImage(self):
        imageATraiterExiste, img = self.cam.read() # Lecture de l'image depuis la caméra
        if imageATraiterExiste:
            cvRGBImg,mask = self.genereImageSeuillee(img)
            finRangee,offset,milieuImage = self.calculerParametresPourCorrection(cvRGBImg,mask)
            self.dataFromImage.emit(finRangee,offset,milieuImage) # Envoi des data au controler
            self.imageAvailable.emit(cvRGBImg) # Envoi de l'image à l'éventuelle ihm

    # Seuillage de l'image couleur par rapport aux seuils fixés par les sliders
    # On récupère une image avec uniquement les pixels comris dans [couleurMin,couleurMax]
    def genereImageSeuillee(self,img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        couleurMin = np.array([self.Hmin, self.Smin, self.Vmin])
        couleurMax = np.array([self.Hmax, self.Smax, self.Vmax])
        if self.Hmin < self.Hmax:
            mask = cv2.inRange(hsv, couleurMin, couleurMax)
        else:
            maskMin = cv2.inRange(hsv, np.array([0, 50, 50]), couleurMax)
            maskMax = cv2.inRange(hsv, couleurMin, np.array([180, 255, 255]))
            mask = cv2.bitwise_or(maskMin, maskMax)
        mask = cv2.erode(mask, self.kernel) # Suppression du bruit
        imgMasquee = cv2.bitwise_and(img, img, mask=mask)
        return cv2.cvtColor(imgMasquee, cv2.COLOR_BGR2RGB),mask

    # Retourne les données néccessaires à la correction (offset et milieuImage) ainsi que si l'on est en fin de rangée ou pas
    def calculerParametresPourCorrection(self,cvRGBImg,mask):
        offset = 0  # Valeur bidon utilisée en cas de non détection
        milieuImage = 0  # Valeur bidon utilisée en cas de non détection
        height, width = mask.shape
        # Recherche des plus gros blobs à gauche et à droite
        milieuImage = int(width / 2)
        # On supprime la partie supérieure de l'image
        mask[0:DEBUT_MASK, ] = 0
        # On supprime la partie inférieure de l'image
        mask[DEBUT_MASK + HAUTEUR_MASK:height - 1, ] = 0
        # Image de gauche
        imGauche = mask[DEBUT_MASK:DEBUT_MASK + HAUTEUR_MASK, 0:milieuImage - 1]
        # Image de droite
        imDroite = mask[DEBUT_MASK:DEBUT_MASK + HAUTEUR_MASK, milieuImage:width - 1]
        # Calcul des contours des images gauche et droite
        major = cv2.__version__.split('.')[0]  # check OpenCV version
        if major == '3':
            _, cntsGauche, _ = cv2.findContours(imGauche.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            _, cntsDroit, _ = cv2.findContours(imDroite.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            cntsGauche, _ = cv2.findContours(imGauche.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cntsDroit, _ = cv2.findContours(imDroite.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if cntsGauche and cntsDroit:
            # Calcul du plus gros blob à gauche
            cg = sorted(cntsGauche, key=cv2.contourArea, reverse=True)[0]
            Mg = cv2.moments(cg)
            # Calcul du plus gros blob à droite
            cd = sorted(cntsDroit, key=cv2.contourArea, reverse=True)[0]
            Md = cv2.moments(cd)
            if Mg['m00'] > 0 and Md['m00'] > 0:  # On a pu détecter les deux blobs
                x_g = Mg['m10'] / Mg['m00']  # Abscisse du point à gauche 5centre de gravité du blob)
                x_d = Md['m10'] / Md['m00'] + milieuImage  # Ascisse du point à droite
                offset = int((x_g + x_d) / 2)
                cv2.circle(cvRGBImg, (offset, DEBUT_MASK + int(HAUTEUR_MASK / 2)), 3, (0, 255, 255), -1)
                cv2.line(cvRGBImg, (0, DEBUT_MASK), (width - 1, DEBUT_MASK), (255, 0, 255), 2)
                cv2.line(cvRGBImg, (0, DEBUT_MASK + HAUTEUR_MASK), (width - 1, DEBUT_MASK + HAUTEUR_MASK),
                         (255, 0, 255), 2)
                cv2.circle(cvRGBImg, (int(x_g), DEBUT_MASK + int(HAUTEUR_MASK / 2)), 3, (255, 0, 0), -1)
                cv2.circle(cvRGBImg, (int(x_d), DEBUT_MASK + int(HAUTEUR_MASK / 2)), 3, (255, 0, 0), -1)
                self.nbNonDetections = 0
        else:
            self.nbNonDetections += 1
            print('-------------->> Non détection')
        return self.nbNonDetections > SEUIL_NON_DETECTION , offset, milieuImage
