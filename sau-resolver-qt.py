#!/usr/bin/env python

import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QTextEdit, QTabWidget, QWidget, QLabel, QHBoxLayout, QFormLayout)
from PySide6.QtGui import QFontDatabase
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

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.setMinimumSize(800,600)
        #self.setFixedSize(800, 600)

        self.tab = QTabWidget()
        self.button1 = QPushButton("Compute")

        # Create layout and add widgets
        layoutmain = QVBoxLayout()
        layoutmain.addWidget(self.tab)
        layoutmain.addWidget(self.button1)

        self.tab_root_locus = Tab("tab_root_locus")
        self.tab_root_locus.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")

        self.tab_step = Tab("tab_step")
        self.tab_step.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")

        self.tab_routh = Tab("tab_routh")
        self.tab_routh.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_routh.add_text_edit("Resultado")

        self.tab_control = Tab("tab_control")
        self.tab_control.add_line_edit("FdT", "1/(s+1)")
        self.tab_control.add_line_edit("s*", "-4+8j")
        self.tab_control.add_line_edit("Cero", "0")
        self.tab_control.add_text_edit("Resultado")

        self.tab_root_locus_all = Tab("tab_root_locus_all")
        self.tab_root_locus_all.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_root_locus_all.add_text_edit("Resultado")

        self.tab_error = Tab("tab_error")
        self.tab_error.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_error.add_line_edit("Objetivo de error", "0.1")
        self.tab_error.add_line_edit("Polo")
        self.tab_error.add_line_edit("s*")
        self.tab_error.add_text_edit("Resultado")

        self.tab_systems = Tab("tab_systems")
        self.tab_systems.add_line_edit("Entrada", "Vr")
        self.tab_systems.add_line_edit("Variables", "T,Ve,I,W")
        self.tab_systems.add_line_edit("eq1", "Vr-R*I-L*s*I-Ve=0")
        self.tab_systems.add_line_edit("eq2", "T-J*s*W-B*W=0")
        self.tab_systems.add_line_edit("eq3", "Ve-Ke*W=0")
        self.tab_systems.add_line_edit("eq4", "T-Ki*I=0")
        self.tab_systems.add_line_edit("eq5")
        self.tab_systems.add_line_edit("eq6")
        self.tab_systems.add_line_edit("eq7")
        self.tab_systems.add_line_edit("eq8")
        self.tab_systems.add_text_edit("Resultado")

        self.tab.addTab(self.tab_systems.tab, "Sistemas")#0
        self.tab.addTab(self.tab_step.tab, "Escalón")#1
        self.tab.addTab(self.tab_routh.tab, "Routh")#2
        self.tab.addTab(self.tab_root_locus.tab, "LdlR")#3
        self.tab.addTab(self.tab_root_locus_all.tab, "LdlR 2")#4
        self.tab.addTab(self.tab_control.tab, "Control")#5
        self.tab.addTab(self.tab_error.tab, "Error")#6

        self.tabs = [self.tab_systems]
        self.tabs.append(self.tab_step)
        self.tabs.append(self.tab_routh)
        self.tabs.append(self.tab_root_locus)
        self.tabs.append(self.tab_root_locus_all)
        self.tabs.append(self.tab_control)
        self.tabs.append(self.tab_error)

        # Set dialog layout
        self.setLayout(layoutmain)
        # Add button signal to greetings slot
        self.button1.clicked.connect(self.greetings)

    # Greets the user
    def greetings(self):
        f = io.StringIO()
        with redirect_stdout(f):

            if self.tab.currentIndex() == 3:
                resolver.root_locus(self.tab_root_locus.get("FdT"))
            elif self.tab.currentIndex() == 1:
                resolver.step_response(self.tab_step.get("FdT"))
            elif self.tab.currentIndex() == 2:
                resolver.routh(self.tab_routh.get("FdT"))
                self.tab_routh.set("Resultado", f.getvalue())
            elif self.tab.currentIndex() == 5:
                resolver.compute_controller(self.tab_control.get("FdT"), self.tab_control.get("s*"), self.tab_control.get("Cero"))
                self.tab_control.set("Resultado", f.getvalue())
            elif self.tab.currentIndex() == 4:
                resolver.root_locus_angles(self.tab_root_locus_all.get("FdT"))
                resolver.rupture_points(self.tab_root_locus_all.get("FdT"))
                print("")
                resolver.asynt(self.tab_root_locus_all.get("FdT"))
                self.tab_root_locus_all.set("Resultado", f.getvalue())
            elif self.tab.currentIndex() == 6:
                resolver.compensate_error(self.tab_error.get("FdT"),
                                          self.tab_error.get("Objetivo de error"),
                                          self.tab_error.get("Polo"),
                                          self.tab_error.get("s*"))
                self.tab_error.set("Resultado", f.getvalue())
            elif self.tab.currentIndex() == 0:

                eqs = []
                vars = self.tab_systems.get("Variables").split(",")
                for i in range(self.tab_systems.count()-3):
                    eq = self.tab_systems.get("eq" + str(i + 1))
                    if eq is not None:
                        eqs.append(eq)
                resolver.solve_equation_system(self.tab_systems.get("Entrada"), vars, eqs)

                self.tab_systems.set("Resultado", f.getvalue())

        for i in self.tabs:
            i.save()

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
