import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QTextEdit, QTabWidget, QWidget)
from PySide6.QtGui import QFontDatabase
import resolver
import io
from contextlib import redirect_stdout




class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.setFixedSize(800,600)

        self.tab = QTabWidget()
        self.edit3 = QLineEdit("-4+8j")
        self.edit_zero = QLineEdit("0")
        self.edit4 = QTextEdit("")
        self.edit5 = QTextEdit("")

        self.edit = QLineEdit("1/(s^3+s^2+3*s+2)")
        self.edit2 = QTextEdit("")
        self.button1 = QPushButton("Compute")

        # Create layout and add widgets
        layoutmain = QVBoxLayout()
        layoutmain.addWidget(self.edit)
        layoutmain.addWidget(self.tab)
        layoutmain.addWidget(self.button1)

        self.tab0 = QWidget()
        layout = QVBoxLayout()
        self.tab0.setLayout(layout)

        self.tab1 = QWidget()
        layout = QVBoxLayout()
        self.tab1.setLayout(layout)

        self.tab2 = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.edit2)
        self.tab2.setLayout(layout)

        self.tab3 = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.edit3)
        layout.addWidget(self.edit_zero)
        layout.addWidget(self.edit4)
        self.tab3.setLayout(layout)

        self.tab4 = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.edit5)
        self.tab4.setLayout(layout)

        self.tab.addTab(self.tab0, "Root Locus")
        self.tab.addTab(self.tab1, "Step")
        self.tab.addTab(self.tab2, "Routh")
        self.tab.addTab(self.tab3, "Control")
        self.tab.addTab(self.tab4, "Root Locus all")

        my_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        #my_font = QFont("Courier", 12)
        self.edit2.setFont(my_font)
        self.edit4.setFont(my_font)
        self.edit5.setFont(my_font)

        # Set dialog layout
        self.setLayout(layoutmain)
        # Add button signal to greetings slot
        self.button1.clicked.connect(self.greetings)

    # Greets the user
    def greetings(self):
        f = io.StringIO()
        with redirect_stdout(f):

            if self.tab.currentIndex() == 0:
                resolver.root_locus(self.edit.text())
            elif self.tab.currentIndex() == 1:
                resolver.step_response(self.edit.text())
            elif self.tab.currentIndex() == 2:
                resolver.routh(self.edit.text())
                self.edit2.setText(f.getvalue())
            elif self.tab.currentIndex() == 3:
                resolver.compute_controller(self.edit.text(), self.edit3.text(), self.edit_zero.text())
                self.edit4.setText(f.getvalue())
            elif self.tab.currentIndex() == 4:
                resolver.root_locus_angles(self.edit.text())
                resolver.rupture_points(self.edit.text())
                print("---")
                resolver.asynt(self.edit.text())
                self.edit5.setText(f.getvalue())
        #print(out)

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())