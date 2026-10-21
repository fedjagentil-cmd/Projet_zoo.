
import os
import sys

from PyQt6.QtWidgets import QApplication

from interface.main_window import MainWindow

if __name__ == "__main__":
    dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_csv = os.path.join(dossier, "animaux.csv")

    app = QApplication(sys.argv)
    fenetre = MainWindow(chemin_csv)
    fenetre.show()
    sys.exit(app.exec())
