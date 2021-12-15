#!/usr/bin/env python

import sys

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QTextEdit, QTabWidget, QWidget, QLabel, QHBoxLayout, QFormLayout, QTabBar, QStylePainter, QStyle, QStyleOptionTab)
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui, QtWidgets, QtCore


import resolver
import io
from contextlib import redirect_stdout
import configparser


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QTabWidget.West)

class Tab():
    def __init__(self, name="Tab"):
        self.layout = QVBoxLayout()
        self.layout2 = QFormLayout()
        self.layout.addLayout(self.layout2)
        self.tab = QWidget()
        self.widgets = []
        self.dic = {}
        self.tab.setLayout(self.layout)
        self.my_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.name = name
        try:
            config.add_section(name)
        except:
            pass

    def count(self):
        return len(self.dic)

    def append(self, widget, name):
        widget.setFont(self.my_font)
        self.layout2.addRow(QLabel(name), widget)
        #self.layout2.addWidget(widget)
        self.widgets.append(widget)
        self.dic[name] = widget

    def get(self, name):
        res = self.dic[name]
        return res.text() if res.text() != "" else None

    def getf(self, name):
        return float(self.get(name))

    def geti(self, name):
        return int(self.get(name))


    def set(self, name, value):
        res = self.dic[name]
        res.setText(value)

    def getconfig(self, sec, name, default):
        try:
            return config.get(sec, name)
        except:
            return default

    def add_line_edit(self, name="test", text=""):
        text = self.getconfig(self.name, name, text)
        edit = QLineEdit(text)
        self.append(edit, name)

    def add_text_edit(self, name="test", text=""):
        edit = QTextEdit(text)
        edit.setReadOnly(True)
        edit.setMinimumSize(800,600)
        self.append(edit, name)

    def save(self):
        for k, v in self.dic.items():
            try:
                config.set(self.name, k, v.text())
            except:
                pass

# CONFIG
config = configparser.RawConfigParser()
config.read('sau-resolver-qt.ini')


class Tabs():
    def __init__(self, parent=None):
        self.tabs = {}

    def add(self, name):
        self.tabs[name] = Tab(name)
        return self.tabs[name]

class Form(QDialog):
    def tick(self):
        plt.pause(0.00001)

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setMinimumSize(800,600)
        self.tab = VerticalTabWidget() #QTabWidget()
        self.tab.setTabPosition(QTabWidget.West)
        self.button1 = QPushButton("Compute")

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(10)

        layoutmain = QVBoxLayout()
        layoutmain.addWidget(self.tab)
        layoutmain.addWidget(self.button1)

        self.tabs = Tabs()

        tab = self.tabs.add("Raíces Polinomio")
        tab.add_line_edit("Polinomio", "s^2+s+1")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Escalón")
        tab.add_line_edit("FdT", "1/(s^2+s+1)")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Routh")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+K)")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Zona Válida")
        tab.add_line_edit("Ts98% <", "1")
        tab.add_line_edit("S% <", "20")
        tab.add_line_edit("Tp <", "2")
        tab.add_line_edit("Tp >", "0")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Todo Lugar de las raíces")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("K Max", "100")
        tab.add_text_edit("Resultado")


#        tab = self.tabs.add("Lugar de las raíces")
#        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
#        tab.add_line_edit("Ganancia", "")
#        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Proporcional Derivativo")
        tab.add_line_edit("FdT", "10/(s+1)/(s+2)")
        tab.add_line_edit("s*", "-4+8j")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Red de Adelanto")
        tab.add_line_edit("FdT", "10/(s+1)/(s+2)")
        tab.add_line_edit("s*", "-4+8j")
        tab.add_line_edit("Cero", "-6")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Red de Retardo")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("Objetivo de error", "0.1")
        tab.add_line_edit("Polo","-0.1")
        tab.add_line_edit("s*","-4+3j")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Proporcional Integrativo")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("Objetivo de error", "4")
        tab.add_line_edit("s*","-4+3j")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Bode")
        tab.add_line_edit("FdT", "1/(s+2)/(s+1)")
        tab.add_text_edit("Resultado")

        for k,v in self.tabs.tabs.items():
            self.tab.addTab(v.tab, k)#0

        self.setLayout(layoutmain)
        self.button1.clicked.connect(self.greetings)

        resolver.set_blocking(False)


    def greetings(self):
        f = io.StringIO()
        with redirect_stdout(f):

            text = self.tab.tabText(self.tab.currentIndex())
            tab = self.tabs.tabs[text]
#            try:
            if text == "Lugar de las raíces":
                limit = tab.get("Ganancia")
                if limit is not None:
                    resolver.root_locus(tab.get("FdT"), float(limit))
                else:
                    resolver.root_locus(tab.get("FdT"))
            elif text == "Escalón":
                resolver.step_response(tab.get("FdT"))
                tab.set("Resultado", f.getvalue())
            elif text == "Raíces Polinomio":
                resolver.roots(tab.get("Polinomio"))
                tab.set("Resultado", f.getvalue())
            elif text == "Bode":
                resolver.asbode(tab.get("FdT"),6)
                tab.set("Resultado", f.getvalue())
            elif text == "Zona Válida":
                tp_gt = float(tab.getf("Tp >"))
                tp_lt = float(tab.getf("Tp <"))
                tp = -tp_lt if tp_lt!=0 else tp_gt
                resolver.valid_zone(tab.getf("Ts98% <"),tab.getf("S% <"), tp , 0 , 0)
                tab.set("Resultado", f.getvalue())

            elif text == "Routh":
                resolver.routh(tab.get("FdT"))
                tab.set("Resultado", f.getvalue())
            elif text == "Red de Adelanto":
                resolver.compute_controller(tab.get("FdT"), tab.get("s*"), tab.get("Cero"))
                tab.set("Resultado", f.getvalue())
            elif text == "Proporcional Derivativo":
                resolver.compute_controller(tab.get("FdT"), tab.get("s*"), None)
                tab.set("Resultado", f.getvalue())
            elif text == "Todo Lugar de las raíces":
                print("Puntos de ruptúra")
                resolver.rupture_points(tab.get("FdT"))
                print("\nAsíntotas")
                a, b, c = resolver.asynt(tab.get("FdT"))
                if a > 0:
                    resolver.root_locus(tab.get("FdT"), asynt=[a, b], limit=tab.geti("K Max"))
                else:
                    resolver.root_locus(tab.get("FdT"), asynt=None, limit=tab.geti("K Max"))
                print("\nÁngulos de partida y llegada")
                resolver.root_locus_angles(tab.get("FdT"))

                tab.set("Resultado", f.getvalue())
            elif text == "Red de Retardo":
                resolver.compensate_error(tab.get("FdT"),
                                          tab.get("Objetivo de error"),
                                          tab.get("Polo"),
                                          tab.get("s*"))
                tab.set("Resultado", f.getvalue())
            elif text == "Proporcional Integrativo":
                resolver.compensate_error(tab.get("FdT"),
                                          tab.get("Objetivo de error"),
                                          None,
                                          tab.get("s*"))
                tab.set("Resultado", f.getvalue())
            elif text == "Sistemas de Ecuaciones":

                eqs = []
                vars = tab.get("Variables").split(",")
                for i in range(tab.count()-3):
                    eq = tab.get("eq" + str(i + 1))
                    if eq is not None:
                        eqs.append(eq)
                resolver.solve_equation_system(tab.get("Entrada"), vars, eqs)

                tab.set("Resultado", f.getvalue())
#            except Exception as e:
#                print(sys.exc_info()[2])
#                tab.set("Resultado", "Error en los datos de entrada o datos no válidos para este cómputo\n" + str(e))

        for k, v in self.tabs.tabs.items():
            v.save()

        with open('sau-resolver-qt.ini', 'w') as configfile:
            config.write(configfile)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())
