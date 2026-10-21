# interface/animal_dialog.py - Formulaire modal d'ajout / modification
from PyQt6.QtWidgets import (QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)

from animal import Animal


class AnimalDialog(QDialog):
    def __init__(self, parent=None, animal=None, modification=False):
        super().__init__(parent)
        self.setWindowTitle("Modifier un animal" if modification else "Ajouter un animal")
        self.setModal(True)
        self.animal = None

        self.champ_id = QLineEdit()
        self.champ_nom = QLineEdit()
        self.champ_espece = QLineEdit()
        self.champ_age = QLineEdit()
        self.champ_poids = QLineEdit()
        self.champ_enclos = QLineEdit()
        self.combo_statut = QComboBox()
        self.combo_statut.addItems(Animal.STATUTS)

        formulaire = QFormLayout()
        formulaire.addRow("Identifiant :", self.champ_id)
        formulaire.addRow("Nom :", self.champ_nom)
        formulaire.addRow("Espèce :", self.champ_espece)
        formulaire.addRow("Âge (ans) :", self.champ_age)
        formulaire.addRow("Poids (kg) :", self.champ_poids)
        formulaire.addRow("Enclos / habitat :", self.champ_enclos)
        formulaire.addRow("Statut de santé :", self.combo_statut)

        
        if animal is not None:
            self.champ_id.setText(animal.identifiant)
            self.champ_nom.setText(animal.nom)
            self.champ_espece.setText(animal.espece)
            self.champ_age.setText(str(animal.age))
            self.champ_poids.setText(str(animal.poids))
            self.champ_enclos.setText(animal.enclos)
            self.combo_statut.setCurrentText(animal.statut_sante)
        if modification:
            self.champ_id.setEnabled(False)  # l'identifiant ne se modifie pas

        bouton_valider = QPushButton("Valider")
        bouton_annuler = QPushButton("Annuler")
        bouton_valider.clicked.connect(self.valider)
        bouton_annuler.clicked.connect(self.reject)

        boutons = QHBoxLayout()
        boutons.addStretch()
        boutons.addWidget(bouton_valider)
        boutons.addWidget(bouton_annuler)

        principal = QVBoxLayout(self)
        principal.addLayout(formulaire)
        principal.addLayout(boutons)

    def valider(self):
        try:
            self.animal = Animal(self.champ_id.text(), self.champ_nom.text(),
                                 self.champ_espece.text(), self.champ_age.text(),
                                 self.champ_poids.text(), self.champ_enclos.text(),
                                 self.combo_statut.currentText())
        except ValueError as erreur:
            QMessageBox.warning(self, "Données invalides", str(erreur))
            return 
        self.accept()
