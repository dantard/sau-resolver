#!/usr/bin/env python

import sys

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QTextEdit, QTabWidget, QWidget, QLabel, QHBoxLayout, QFormLayout)
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import QTimer

import resolver
import io
from contextlib import redirect_stdout
import configparser

class Tab():
    def __init__(self, name="Tab"):
        self.layout = QVBoxLayout()
        self.layout2 = QFormLayout()
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
        self.layout.addLayout(self.layout2)
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
        self.tab = QTabWidget()
        self.button1 = QPushButton("Compute")

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(10)

        layoutmain = QVBoxLayout()
        layoutmain.addWidget(self.tab)
        layoutmain.addWidget(self.button1)

        self.tabs = Tabs()
        tab = self.tabs.add("Zona Válida")
        tab.add_line_edit("Ts <", "1")
        tab.add_line_edit("S% <", "20")
        tab.add_line_edit("Tp <", "0")
        tab.add_line_edit("Tp >", "0")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Lugar de las raíces")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("Ganancia", "")
        tab.add_text_edit("Resultado")


        tab = self.tabs.add("Escalón")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Routh")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Controlador")
        tab.add_line_edit("FdT", "1/(s+1)")
        tab.add_line_edit("s*", "-4+8j")
        tab.add_line_edit("Cero", "0")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Todo Lugar de las raíces")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("K Max", "")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Error")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        tab.add_line_edit("Objetivo de error", "0.1")
        tab.add_line_edit("Polo")
        tab.add_line_edit("s*")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Sistemas de Ecuaciones")
        tab.add_line_edit("Entrada", "Vr")
        tab.add_line_edit("Variables", "T,Ve,I,W")
        tab.add_line_edit("eq1", "Vr-R*I-L*s*I-Ve=0")
        tab.add_line_edit("eq2", "T-J*s*W-B*W=0")
        tab.add_line_edit("eq3", "Ve-Ke*W=0")
        tab.add_line_edit("eq4", "T-Ki*I=0")
        tab.add_line_edit("eq5")
        tab.add_line_edit("eq6")
        tab.add_line_edit("eq7")
        tab.add_line_edit("eq8")
        tab.add_text_edit("Resultado")

        tab = self.tabs.add("Bode")
        tab.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
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

            if text == "Lugar de las raíces":
                limit = tab.get("Ganancia")
                if limit is not None:
                    resolver.root_locus(tab.get("FdT"), float(limit))
                else:
                    resolver.root_locus(tab.get("FdT"))
            elif text == "Escalón":
                resolver.step_response(tab.get("FdT"))
                tab.set("Resultado", f.getvalue())
            elif text == "Bode":
                resolver.asbode(tab.get("FdT"),6)
                tab.set("Resultado", f.getvalue())
            elif text == "Zona Válida":
                tp = tab.getf("Tp >") - tab.getf("Tp <")
                resolver.valid_zone(tab.getf("Ts <"),tab.getf("S% <"), tp , 0 , 0)
                tab.set("Resultado", f.getvalue())

            elif text == "Routh":
                resolver.routh(tab.get("FdT"))
                tab.set("Resultado", f.getvalue())
            elif text == "Controlador":
                resolver.compute_controller(tab.get("FdT"), tab.get("s*"), tab.get("Cero"))
                tab.set("Resultado", f.getvalue())
            elif text == "Todo Lugar de las raíces":
                resolver.root_locus_angles(tab.get("FdT"))
                resolver.rupture_points(tab.get("FdT"))
                print("")
                a, b, c = resolver.asynt(tab.get("FdT"))
                resolver.root_locus(tab.get("FdT"), asynt=[a, b], limit=tab.geti("K Max"))
                tab.set("Resultado", f.getvalue())
            elif text == "Error":
                resolver.compensate_error(tab.get("FdT"),
                                          tab.get("Objetivo de error"),
                                          tab.get("Polo"),
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

        for k,v in self.tabs.tabs.items():
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
