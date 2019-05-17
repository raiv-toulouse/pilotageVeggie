
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class SliderAvecLabel(QWidget):
    lesSliders = []

    def __init__(self,parent=None):
        super(SliderAvecLabel, self).__init__(parent)
        horizLayout = QHBoxLayout()
        self.texte = QLabel()
        self.texte.setAlignment(Qt.AlignLeft)
        horizLayout.addWidget(self.texte)
        self.valeur = QLabel()
        self.valeur.setAlignment(Qt.AlignRight)
        horizLayout.addWidget(self.valeur)
        vertLayout = QVBoxLayout()
        vertLayout.addLayout(horizLayout)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        vertLayout.addWidget(self.slider)
        self.setLayout(vertLayout)
        SliderAvecLabel.lesSliders.append(self)

    def uiSetup(self,min,max,pos,texte):
        self.texte.setText(texte)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.slider.setValue(pos)
