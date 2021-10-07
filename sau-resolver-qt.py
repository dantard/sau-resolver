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
    def __init__(self):
        self.layout = QVBoxLayout()
        self.layout2 = QFormLayout()
        self.tab = QWidget()
        self.widgets = []
        self.dic = {}
        self.tab.setLayout(self.layout)
        self.my_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)


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

    def add_line_edit(self, name="test", text=""):
        edit = QLineEdit(text)
        self.append(edit, name)

    def add_text_edit(self, name="test", text=""):
        edit = QTextEdit(text)
        edit.setReadOnly(True)
        self.append(edit, name)


# CONFIG
opt_fdt_control = "1/(s+2)/(s+3)/(s+5)"

config = configparser.RawConfigParser()
config.read('sau-resolver-qt.ini')
try:
    opt_fdt_control = config.get("Config", "opt_fdt_control")
except:
    pass
#####


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

        self.tab_root_locus = Tab()
        self.tab_root_locus.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")

        self.tab_step = Tab()
        self.tab_step.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")

        self.tab_routh = Tab()
        self.tab_routh.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_routh.add_text_edit("Resultado")

        self.tab_control = Tab()
        self.tab_control.add_line_edit("FdT", opt_fdt_control)
        self.tab_control.add_line_edit("s*", "-4+8j")
        self.tab_control.add_line_edit("Cero", "0")
        self.tab_control.add_text_edit("Resultado")

        self.tab_root_locus_all = Tab()
        self.tab_root_locus_all.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_root_locus_all.add_text_edit("Resultado")

        self.tab_error = Tab()
        self.tab_error.add_line_edit("FdT", "1/(s^3+3*s^2+2*s+1)")
        self.tab_error.add_line_edit("Objetivo de error", "0.1")
        self.tab_error.add_line_edit("Polo")
        self.tab_error.add_line_edit("s*")
        self.tab_error.add_text_edit("Resultado")

        self.tab_systems = Tab()
        self.tab_systems.add_line_edit("Entrada", "Vr")
        self.tab_systems.add_line_edit("Variables", "T,Ve,I,W")
        self.tab_systems.add_line_edit("eq1", "Vr-R*I-L*s*I-Ve=0")
        self.tab_systems.add_line_edit("eq2", "T-J*s*W-B*W=0")
        self.tab_systems.add_line_edit("eq3", "Ve-Ke*W=0")
        self.tab_systems.add_line_edit("eq4", "T-Ki*I=0")
        self.tab_systems.add_line_edit("eq5")
        self.tab_systems.add_text_edit("Resultado")


        self.tab.addTab(self.tab_systems.tab, "Sistemas")#0
        self.tab.addTab(self.tab_step.tab, "Escalón")#1
        self.tab.addTab(self.tab_routh.tab, "Routh")#2
        self.tab.addTab(self.tab_root_locus.tab, "LdlR")#3
        self.tab.addTab(self.tab_root_locus_all.tab, "LdlR 2")#4
        self.tab.addTab(self.tab_control.tab, "Control")#5
        self.tab.addTab(self.tab_error.tab, "Error")#6

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
                print("---")
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
                for i in range(5):
                    eq = self.tab_systems.get("eq" + str(i + 1))
                    if eq is not None:
                        eqs.append(eq)
                resolver.solve_equation_system(self.tab_systems.get("Entrada"), vars, eqs)

                self.tab_systems.set("Resultado", f.getvalue())

        # Save Config
        try:
            config.add_section("Config")
        except:
            pass
        config.set("Config", "opt_fdt_control", self.tab_control.get("FdT"))
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
