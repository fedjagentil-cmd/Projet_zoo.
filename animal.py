# animal.py 

CHAMPS = ["identifiant", "nom", "espece", "age", "poids", "enclos", "statut_sante"]


class Animal:
    """Représente un animal du zoo avec validation des données."""

    STATUTS = ("Bon", "Sous surveillance", "Malade")
    SEUIL_SENIOR = 15  

    def __init__(self, identifiant, nom, espece, age, poids, enclos, statut_sante):
        valeurs = Animal.valider(identifiant, nom, espece, age, poids, enclos, statut_sante)
        (self.identifiant, self.nom, self.espece, self.age,
         self.poids, self.enclos, self.statut_sante) = valeurs

    @staticmethod
    def valider(identifiant, nom, espece, age, poids, enclos, statut_sante):
        """Vérifie les contraintes. Lève ValueError avec un message clair si une règle est violée.
        Retourne les valeurs nettoyées (texte sans espaces, age en int, poids en float)."""
        identifiant = str(identifiant).strip()
        nom = str(nom).strip()
        espece = str(espece).strip()
        enclos = str(enclos).strip()
        statut_sante = str(statut_sante).strip()

        if identifiant == "":
            raise ValueError("L'identifiant ne peut pas être vide.")
        if nom == "":
            raise ValueError("Le nom ne peut pas être vide.")
        if espece == "":
            raise ValueError("L'espèce ne peut pas être vide.")

        try:
            age = int(str(age).strip())
        except ValueError:
            raise ValueError("L'âge doit être un nombre entier.")
        if age < 0 or age > 100:
            raise ValueError("L'âge doit être compris entre 0 et 100.")

        try:
            poids = float(str(poids).strip().replace(",", "."))
        except ValueError:
            raise ValueError("Le poids doit être un nombre.")
        if not poids > 0:
            raise ValueError("Le poids doit être strictement supérieur à 0.")

        if enclos == "":
            raise ValueError("L'enclos doit être renseigné.")
        if statut_sante not in Animal.STATUTS:
            raise ValueError("Le statut de santé doit être : " + ", ".join(Animal.STATUTS) + ".")

        return identifiant, nom, espece, age, poids, enclos, statut_sante

    def modifier_infos(self, nom, espece, age, poids, enclos, statut_sante):
        """Modifie l'animal (l'identifiant ne change pas). Rien n'est modifié si une valeur est invalide."""
        _, nom, espece, age, poids, enclos, statut_sante = Animal.valider(
            self.identifiant, nom, espece, age, poids, enclos, statut_sante)
        self.nom = nom
        self.espece = espece
        self.age = age
        self.poids = poids
        self.enclos = enclos
        self.statut_sante = statut_sante

    def est_senior(self):
        return self.age >= Animal.SEUIL_SENIOR

    def afficher_infos(self):
        senior = "Oui" if self.est_senior() else "Non"
        return (f"Identifiant : {self.identifiant}\n"
                f"Nom : {self.nom}\n"
                f"Espèce : {self.espece}\n"
                f"Âge : {self.age} an(s)\n"
                f"Poids : {self.poids} kg\n"
                f"Enclos : {self.enclos}\n"
                f"Statut de santé : {self.statut_sante}\n"
                f"Senior : {senior}")

    def to_dict(self):
        """Convertit l'animal en dictionnaire = une ligne du fichier CSV."""
        return {
            "identifiant": self.identifiant,
            "nom": self.nom,
            "espece": self.espece,
            "age": self.age,
            "poids": self.poids,
            "enclos": self.enclos,
            "statut_sante": self.statut_sante,
        }
