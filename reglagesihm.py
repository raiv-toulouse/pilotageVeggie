# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from webcamProcessing import WebcamProcessing
from sliderAvecLabel import SliderAvecLabel
from PyQt5.QtCore import pyqtSignal


## Classe IHM

class IhmTracking(QWidget):
    chgtSeuils =  pyqtSignal(int,int,int,int,int,int)
     def __init__(self, webcam):
        super(self.__class__, self).__init__()
        webcam.imageAvailable.connect(self.majImageCouleur)
        loadUi('ihm.ui', self)
        self.btnSauverFichier.clicked.connect(self.enregistrerHSV)
        self.sliderHmin.uiSetup(0, 180, webcam.Hmin, "H min :")
        self.sliderHmax.uiSetup(0, 180, webcam.Hmax, "H max :")
        self.sliderSmin.uiSetup(0, 255, webcam.Smin, "S min :")
        self.sliderSmax.uiSetup(0, 255, webcam.Smax, "S max :")
        self.sliderVmin.uiSetup(0, 255, webcam.Vmin, "V min : ")
        self.sliderVmax.uiSetup(0, 255, webcam.Vmax, "V max : ")
        for slider in SliderAvecLabel.lesSliders:
            slider.slider.valueChanged.connect(self.seuilChange)
        webcam.ajoutIhm(self)
        
        
    def lireHSV(self):
        Hmin = self.sliderHmin.slider.value()
        Hmax = self.sliderHmax.slider.value()
        Smin = self.sliderSmin.slider.value()
        Smax = self.sliderSmax.slider.value()
        Vmin = self.sliderVmin.slider.value()
        Vmax = self.sliderVmax.slider.value()
        return Hmin,Hmax,Smin,Smax,Vmin,Vmax
        
        
    def enregistrerHSV(self):
        file = open("reglagesHSV.txt", "w")
        Hmin, Hmax, Smin, Smax, Vmin, Vmax = self.lireHSV()
        file.write("{},{},{},{},{},{}".format(Hmin, Hmax, Smin, Smax, Vmin, Vmax))
        file.close()
        
    def seuilChange(self):
        Hmin, Hmax, Smin, Smax, Vmin, Vmax = self.lireHSV()
        self.chgtSeuils.emit(Hmin,Hmax,Smin,Smax,Vmin,Vmax)
        
    # Affichage de l'image seuillée sur l'écran
    def majImageCouleur(self,img):
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        mQImage = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
        pix = QPixmap.fromImage(mQImage)
        self.zoneImage.setPixmap(pix)
        
        
####################################################################################################################
if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    webcam = WebcamProcessing()
    w = IhmTracking(webcam)
    w.show()
    #sys.exit(app.exec_())

        
        
        
        
        
        