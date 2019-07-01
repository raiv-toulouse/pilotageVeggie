# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time

### Constantes que l'on peut adapter
###
FPS = 10  #Frames Per Second
###

class RpiCamera(object):

    def __init__(self):
        super().__init__()

        w2c = np.loadtxt('w2c.txt')  # load color model
        self.w2cMax = np.amax(w2c, axis=1)  ## retourne la plus grande proba de p(w|z)
        self.w2cIdx = np.argmax(w2c, axis=1)  ## retourne l'indice de la plus grande proba de p(w|z)

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FPS, FPS)
        time.sleep(1)

        self.kernel = np.ones((5, 5), np.uint8)

        self.cX = None
        self.cY = None

    # Appelée chaque fois qu'une nouvelle image est acquise
    def traiterImage(self):
        ret, img = self.camera.read()  # Lecture de l'image depuis la caméra cv2.imwrite('img.jpg', img)
        cv2.imshow('Mask', img), cv2.waitKey(0), cv2.destroyAllWindows()
        if ret:
            # start = time.time()
            self.cX, self.cY = self.weedsDetection(img)
            # print(time.time() - start)


    def weedsDetection(self, img):
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # convertir l'image de l'espace couleur RGB en HSV

        # hsvNorm = np.zeros(hsv.shape)
        # hsvNorm = cv2.normalize(hsv, hsvNorm, 0, 255, cv2.NORM_MINMAX)  # Mettre l'image entre 0..255
        hsvNorm = img
        outIdx, outMax = self.im2c(hsvNorm)  # Applique une segmentation : extraire la couleur de la plante

        cX, cY = self.getCoordinates(outIdx, outMax)  # Calculer les coordonnées en pixels de différents blobs

        return(cX, cY)  # Return the coordinates of centre of weed

    def getCoordinates(self, outIdx, outMax):
        mask = cv2.inRange(outMax, 0.65, 1)

        # 4 = l'index pour designer la couleur verte (une plante)
        # mask = cv2.inRange(outIdx, 4, 4);  cv2.imshow('outIdx', mask), cv2.waitKey(0), cv2.destroyAllWindows()

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.dilate(mask, self.kernel, iterations=1)  # cv2.imshow('Mask', mask), cv2.waitKey(0), cv2.destroyAllWindows()

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours in the binary image

        # Filtred image using area threshold = 100 and Calculate moments of binary image
        cX, cY = [], []
        for c in contours:
            if cv2.contourArea(c) >= 100:
                M = cv2.moments(c)

                #  Calculate x,y coordinate of center
                cX.append(int(M["m10"] / M["m00"]))
                cY.append(int(M["m01"] / M["m00"]))

        return(cX, cY)

    def im2c(self, img):
        img = img[55:, :, :]  # Une partie de la tolle est visible par la caméra est supprimer

        RR = img[:, :, 2];  RR = RR.flatten(order='F')
        GG = img[:, :, 1];  GG = GG.flatten(order='F')
        BB = img[:, :, 0];  BB = BB.flatten(order='F')

        indexImg = np.floor(RR / 8) + 32 * np.floor(GG / 8) + 32 * 32 * np.floor(BB / 8)
        indexImg = indexImg.astype(int)

        outIdx = self.w2cIdx[indexImg]
        outMax = self.w2cMax[indexImg]

        outIdx = np.reshape(outIdx, (img.shape[0], img.shape[1]), order='F')
        outMax = np.reshape(outMax, (img.shape[0], img.shape[1]), order='F')

        return(outIdx, outMax)