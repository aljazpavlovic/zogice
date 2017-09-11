import random
import math
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox


class QGraphicsViewWMouse(QGraphicsView):
    def __init__(self, *args):
        super(QGraphicsViewWMouse, self).__init__(*args)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, ev):
        global miska
        miska = ev.x(), ev.y()
        super(QGraphicsViewWMouse, self).mouseMoveEvent(ev)

    def mousePressEvent(self, ev):
        global miska, klik
        miska = ev.x(), ev.y()
        klik = True
        super(QGraphicsViewWMouse, self).mousePressEvent(ev)

    def keyPressEvent(self, ev):
        global levo, desno
        super().keyPressEvent(ev)
        levo = ev.key() == Qt.Key_Left
        desno = ev.key() == Qt.Key_Right

    def keyReleaseEvent(self, ev):
        global levo, desno
        super().keyReleaseEvent(ev)
        levo = desno = False


app = QApplication([])
widget = QDialog()
widget.setWindowTitle("Žogice")
widget.setLayout(QVBoxLayout())
widget.layout().setContentsMargins(2, 2, 2, 2)
widget.scene = QGraphicsScene(widget)
widget.scene.setBackgroundBrush(Qt.lightGray)
widget.view = QGraphicsViewWMouse(widget.scene, widget)
widget.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
widget.view.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
widget.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
widget.layout().addWidget(widget.view)
widget.resize(800, 500)
widget.scene.setSceneRect(0, 0, widget.view.width(), widget.view.height())
widget.view.setSceneRect(0, 0, widget.view.width(), widget.view.height())
widget.show()
widget.raise_()
maxX = widget.view.width()
maxY = widget.view.height()
miska = maxX / 2, maxY / 2
klik = False
obnavljaj = True


def nakljucna_barva():
    barve = [Qt.red, Qt.green, Qt.yellow]
    return random.choice(barve)


def obnovi():
    widget.scene.update()
    qApp.processEvents()


def cakaj(sekunde):
    obnovi()
    time.sleep(sekunde)


def krog(x, y, r, barva=nakljucna_barva(), sirina=1):
    ustvari_krog = widget.scene.addEllipse(-r, -r, 2*r, 2*r, QPen(QBrush(barva), sirina))
    ustvari_krog.setPos(x, y)
    if obnavljaj:
        obnovi()
    return ustvari_krog


def konec():
    qApp.exec()


levo = desno = False


class Zoga:
    def __init__(self):
        self.barva = nakljucna_barva()
        self.x = random.randint(30, maxX - 30)
        self.y = random.randint(30, maxY - 30)
        self.kot = random.randint(0, 360)
        self.hitrost = random.randint(50, 150)
        self.radij = 10
        self.zacetni_cas = 0
        self.status = 0
        self.narisi_se()
        self.skrij_se()

    def narisi_se(self):
        self.body = krog(self.x, self.y, self.radij, self.barva, 2)
        if self.status == -1:
            self.body.show()
        self.status = 0

    def skrij_se(self):
        self.body.hide()
        self.status = -1

    def reset(self):
        self.status = 0
        self.hitrost = 5
        self.radij = 10
        self.body.setPos(self.x, self.y)

    def spremeni_kot(self):
        if 0 <= self.kot < 90:
            self.kot = 180 - self.kot
        elif 90 <= self.kot < 180:
            self.kot = -self.kot
        elif 180 <= self.kot < 270:
            self.kot = 180 - self.kot
        elif 270 <= self.kot <= 360:
            self.kot = -self.kot
        else:
            if self.kot < 0:
                self.kot += 360
            if self.kot >= 360:
                self.kot -= 360
            self.spremeni_kot()

    def ce_pride_do_roba(self):
        if self.x <= 0 or self.y <= 0 or self.y >= maxY or self.x >= maxX:
            self.spremeni_kot()
        if self.razdalja_do(kurzor.x, kurzor.y) < 40:
            self.pobarvaj_se()
        self.x += self.hitrost * math.sin(math.radians(self.kot))
        self.y += self.hitrost * math.cos(math.radians(self.kot))
        self.update()

    def update(self):
        if self.status > -1:
            self.body.setPos(self.x, self.y)
        if self.status == -1:
            self.skrij_se()
        if self.status == 1 and self.zacetni_cas < 0:
            self.skrij_se()
            self.status = 2

    def pobarvaj_se(self):
        if self.status == 0:
            self.status = 1
            self.radij = 30
            self.zacetni_cas = 2
            self.body.hide()
            self.body = krog(self.x, self.y, self.radij, self.barva, 2)
            pobarvamo_zogico = self.body.pen().color().lighter()
            pobarvamo_zogico.setAlpha(192)
            self.body.setBrush(pobarvamo_zogico)
            self.hitrost = 0
            kurzor.stevilo_pocenih += 1

    def razdalja_do(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def preveri_vse_razdalje_do_zog(self, zogica):
        self.update()
        if self.status == 1:
            self.zacetni_cas -= 0.02
        elif self.status == 0:
            self.ce_pride_do_roba()
            for k in range(30):
                if zogica[k].status == 1 and self.razdalja_do(zogica[k].x, zogica[k].y) < 40:
                    self.pobarvaj_se()
                    break


class Miska(Zoga):
    def __init__(self):
        self.x = 2000
        self.y = 2000
        self.status = 0
        self.zacetni_cas = 0
        self.stevilo_pocenih = -1
        self.barva = nakljucna_barva()
        self.body = krog(self.x, self.y, 30, self.barva, 2)

    def reset(self):
        self.body.hide()
        self.body = krog(self.x, self.y, 30, self.barva, 2)
        self.update()
        kurzor.status = 0
        self.body.show()
        self.x = 2000
        self.y = 2000
        self.stevilo_pocenih = -1

    def update(self):
        if not klik:
            self.body.setPos(miska[0], miska[1])
        elif self.status == 0:
            self.zacetni_cas = 3
            self.x = miska[0]
            self.y = miska[1]
            self.pobarvaj_se()
        elif self.status == 1:
            if self.zacetni_cas > 0:
                self.zacetni_cas -= 0.02
            else:
                self.body.hide()
                self.x = 2000
                self.y = 2000
                self.status = 2


kurzor = Miska()
zoge = []
seznam_zog = []
for i in range(50):
    zoge.append(Zoga())
    zoge[i].skrij_se()
    seznam_zog.append(0)
nivo = 1
delez = 0.1
while nivo < 11:
    klik = False
    st_zog = 15 + (nivo * 3)
    for i in range(st_zog):
        zoge[i].reset()
        zoge[i].skrij_se()
        seznam_zog[i] = zoge[i].status
        zoge[i].reset()
    kurzor.reset()
    al_ja_al_ne = 1
    QMessageBox.information(None, "NIVO {}".format(nivo), "Poči vsaj {} od {} žog".format(int(st_zog * delez), st_zog))
    for i in range(st_zog):
        zoge[i].narisi_se()
    while al_ja_al_ne:
        for j in range(st_zog):
            seznam_zog[j] = zoge[j].status
            if kurzor.status == 2:
                if 1 in seznam_zog:
                    zoge[j].preveri_vse_razdalje_do_zog(zoge)
                else:
                    for i in range(50):
                        zoge[i].skrij_se()
                    al_ja_al_ne = 0
            else:
                zoge[j].preveri_vse_razdalje_do_zog(zoge)
        cakaj(0.02)
        kurzor.update()
    for i in range(st_zog):
        zoge[i].status = -1
    if kurzor.stevilo_pocenih >= int(st_zog * delez):
        QMessageBox.information(None, "BRAVO", "Počil si {} od {} žog".format(int(st_zog * delez), st_zog))
        al_ja_al_ne = 1
        nivo += 1
        delez += 0.1
    else:
        QMessageBox.information(None, "NEUSPEH", "Počil si le {} od {} žog".format(kurzor.stevilo_pocenih, st_zog))
konec()
