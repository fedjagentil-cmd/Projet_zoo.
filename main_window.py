# interface/main_window.py - Fenêtre principale (affichage uniquement, la logique est dans GestionZoo)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                             QPushButton, QLabel, QMessageBox, QFileDialog, QHeaderView,
                             QAbstractItemView, QDialog)

from gestion_zoo import GestionZoo, ErreurFichier
from interface.animal_dialog import AnimalDialog

ENTETES = ["Identifiant", "Nom", "Espèce", "Âge", "Poids (kg)", "Enclos", "Statut de santé"]
COULEURS = {"Malade": QColor("#deecc4"), "Sous surveillance": QColor("#e3fb83"),"Bon": QColor("#e8f8cd"),}


class MainWindow(QMainWindow):
    def __init__(self, chemin_csv):
        super().__init__()
        self.setWindowTitle("Gestion des animaux du zoo")
        self.resize(950, 600)

        self.zoo = GestionZoo(chemin_csv)   # une seule instance de GestionZoo
        self.modifie = False                # des changements non enregistrés ?
        self.classement_decroissant = True

        self.onglets = QTabWidget()
        self.setCentralWidget(self.onglets)
        self.onglets.addTab(self.creer_onglet_animaux(), "Animaux")
        self.onglets.addTab(self.creer_onglet_classement(), "Classement")
        self.onglets.addTab(self.creer_onglet_statistiques(), "Statistiques")
        self.creer_menu()

        self.charger_au_demarrage()
        self.rafraichir()

    # ---------- Construction de l'interface ----------
    def creer_onglet_animaux(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher (nom, espèce, enclos, statut...)")
        self.champ_recherche.textChanged.connect(self.rafraichir)
        layout.addWidget(self.champ_recherche)

        self.table_animaux = QTableWidget()
        self.configurer_tableau(self.table_animaux, ENTETES)
        self.table_animaux.cellDoubleClicked.connect(self.afficher_animal)
        layout.addWidget(self.table_animaux)

        boutons = QHBoxLayout()
        for texte, action in [("Ajouter", self.ajouter), ("Afficher", self.afficher_animal),
                              ("Modifier", self.modifier), ("Supprimer", self.supprimer)]:
            bouton = QPushButton(texte)
            bouton.clicked.connect(action)
            boutons.addWidget(bouton)
        layout.addLayout(boutons)
        return page

    def creer_onglet_classement(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        haut = QHBoxLayout()
        haut.addWidget(QLabel("Classer par :"))
        self.combo_critere = QComboBox()
        self.combo_critere.addItems(["Âge", "Poids"])
        self.combo_critere.currentIndexChanged.connect(self.rafraichir)
        haut.addWidget(self.combo_critere)
        bouton_inverser = QPushButton("Inverser l'ordre")
        bouton_inverser.clicked.connect(self.inverser_ordre)
        haut.addWidget(bouton_inverser)
        haut.addStretch()
        layout.addLayout(haut)

        self.table_classement = QTableWidget()
        self.configurer_tableau(self.table_classement, ["Rang"] + ENTETES)
        layout.addWidget(self.table_classement)
        return page

    def creer_onglet_statistiques(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.label_stats = QLabel()
        layout.addWidget(self.label_stats)
        layout.addStretch()
        bouton_doyen = QPushButton("Doyen du zoo")
        bouton_doyen.clicked.connect(self.montrer_doyen)
        layout.addWidget(bouton_doyen)
        return page

    def creer_menu(self):
        menu = self.menuBar().addMenu("Fichier")
        for texte, action in [("Importer CSV", self.importer_csv),
                              ("Exporter CSV", self.exporter_csv),
                              ("Enregistrer", self.enregistrer)]:
            qaction = QAction(texte, self)
            qaction.triggered.connect(action)
            menu.addAction(qaction)

    def configurer_tableau(self, tableau, entetes):
        tableau.setColumnCount(len(entetes))
        tableau.setHorizontalHeaderLabels(entetes)
        tableau.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tableau.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tableau.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    # ---------- Affichage ----------
    def remplir_tableau(self, tableau, animaux, avec_rang=False):
        tableau.setRowCount(len(animaux))
        for ligne, a in enumerate(animaux):
            valeurs = [a.identifiant, a.nom, a.espece, str(a.age), str(a.poids), a.enclos, a.statut_sante]
            if avec_rang:
                valeurs = [str(ligne + 1)] + valeurs
            for colonne, valeur in enumerate(valeurs):
                case = QTableWidgetItem(valeur)
                if a.statut_sante in COULEURS:       # alerte visuelle (bonus)
                    case.setBackground(COULEURS[a.statut_sante])
                tableau.setItem(ligne, colonne, case)

    def rafraichir(self, *args):
        """Met à jour tous les tableaux et les statistiques."""
        self.remplir_tableau(self.table_animaux, self.zoo.rechercher_animal(self.champ_recherche.text()))

        critere = "age" if self.combo_critere.currentIndex() == 0 else "poids"
        classes = self.zoo.classer_animaux(critere, self.classement_decroissant)
        self.remplir_tableau(self.table_classement, classes, avec_rang=True)

        s = self.zoo.afficher_statistiques()
        texte = (f"Nombre total d'animaux : {s['total']}\n"
                 f"Âge moyen : {s['age_moyen']:.2f} ans\n"
                 f"Poids moyen : {s['poids_moyen']:.2f} kg\n"
                 f"Âge maximum : {s['age_max']} ans   |   Âge minimum : {s['age_min']} ans\n"
                 f"Poids maximum : {s['poids_max']} kg   |   Poids minimum : {s['poids_min']} kg\n\n"
                 "Par statut de santé :\n")
        for statut, nombre in s["par_statut"].items():
            texte += f"   - {statut} : {nombre}\n"
        texte += "\nPar espèce :\n"
        for espece, nombre in s["par_espece"].items():
            texte += f"   - {espece} : {nombre}\n"
        self.label_stats.setText(texte)

    def identifiant_selectionne(self):
        """Retourne l'identifiant de la ligne choisie, ou None (avec un message)."""
        ligne = self.table_animaux.currentRow()
        if ligne < 0:
            QMessageBox.information(self, "Sélection", "Veuillez d'abord sélectionner un animal.")
            return None
        return self.table_animaux.item(ligne, 0).text()

    # ---------- Actions ----------
    def ajouter(self):
        animal = None
        while True:
            dialogue = AnimalDialog(self, animal)
            if dialogue.exec() != QDialog.DialogCode.Accepted:
                return
            animal = dialogue.animal
            try:
                self.zoo.ajouter_animal(animal)
                break
            except ValueError as erreur:    # identifiant déjà utilisé
                QMessageBox.warning(self, "Erreur", str(erreur))
        self.modifie = True
        self.rafraichir()

    def afficher_animal(self, *args):
        identifiant = self.identifiant_selectionne()
        if identifiant is None:
            return
        try:
            animal = self.zoo.trouver_animal(identifiant)
            QMessageBox.information(self, "Fiche de l'animal", animal.afficher_infos())
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur", str(erreur))

    def modifier(self):
        identifiant = self.identifiant_selectionne()
        if identifiant is None:
            return
        try:
            animal = self.zoo.trouver_animal(identifiant)
            dialogue = AnimalDialog(self, animal, modification=True)
            if dialogue.exec() != QDialog.DialogCode.Accepted:
                return
            n = dialogue.animal
            self.zoo.modifier_animal(identifiant, n.nom, n.espece, n.age, n.poids, n.enclos, n.statut_sante)
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur", str(erreur))
            return
        self.modifie = True
        self.rafraichir()

    def supprimer(self):
        identifiant = self.identifiant_selectionne()
        if identifiant is None:
            return
        reponse = QMessageBox.question(self, "Confirmation",
                                       f"Supprimer l'animal « {identifiant} » ?")
        if reponse != QMessageBox.StandardButton.Yes:
            return
        try:
            self.zoo.supprimer_animal(identifiant)
        except ValueError as erreur:
            QMessageBox.warning(self, "Erreur", str(erreur))
            return
        self.modifie = True
        self.rafraichir()

    def inverser_ordre(self):
        self.classement_decroissant = not self.classement_decroissant
        self.rafraichir()

    def montrer_doyen(self):
        try:
            doyen = self.zoo.doyen()
            lourd = self.zoo.plus_lourd()
        except ValueError as erreur:
            QMessageBox.information(self, "Doyen du zoo", str(erreur))
            return
        QMessageBox.information(self, "Doyen du zoo",
                                "Animal le plus âgé :\n" + doyen.afficher_infos() +
                                "\n\n-----------------\n\nAnimal le plus lourd :\n" + lourd.afficher_infos())

    # ---------- Fichiers CSV ----------
    def charger_au_demarrage(self):
        try:
            acceptees, rejetees = self.zoo.charger_depuis_csv()
            if rejetees > 0:
                QMessageBox.warning(self, "Chargement",
                                    f"{acceptees} ligne(s) chargée(s), {rejetees} ligne(s) rejetée(s).")
        except ErreurFichier as erreur:
            QMessageBox.critical(self, "Erreur de fichier", str(erreur))

    def enregistrer(self):
        try:
            self.zoo.sauvegarder_dans_csv()
            self.modifie = False
            return True
        except ErreurFichier as erreur:
            QMessageBox.critical(self, "Erreur de fichier", str(erreur))
            return False

    def importer_csv(self):
        chemin, _ = QFileDialog.getOpenFileName(self, "Importer un CSV", "", "Fichiers CSV (*.csv)")
        if chemin == "":
            return
        try:
            acceptees, rejetees = self.zoo.charger_depuis_csv(chemin)
        except ErreurFichier as erreur:
            QMessageBox.critical(self, "Erreur d'import", str(erreur))
            return
        self.modifie = True
        self.rafraichir()
        QMessageBox.information(self, "Rapport d'import",
                                f"Lignes importées : {acceptees}\nLignes rejetées : {rejetees}")

    def exporter_csv(self):
        chemin, _ = QFileDialog.getSaveFileName(self, "Exporter vers un CSV", "animaux_export.csv",
                                                "Fichiers CSV (*.csv)")
        if chemin == "":
            return
        try:
            self.zoo.sauvegarder_dans_csv(chemin)
            QMessageBox.information(self, "Export", "Export terminé.")
        except ErreurFichier as erreur:
            QMessageBox.critical(self, "Erreur d'export", str(erreur))

    def closeEvent(self, event):
        if not self.modifie:
            event.accept()
            return
        B = QMessageBox.StandardButton
        reponse = QMessageBox.question(self, "Quitter", "Enregistrer les modifications avant de quitter ?",
                                       B.Save | B.Discard | B.Cancel)
        if reponse == B.Cancel:
            event.ignore()
        elif reponse == B.Save:
            if self.enregistrer():
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
