# gestion_zoo.py - Classe GestionZoo : logique métier + persistance CSV
import csv
import os

from animal import Animal, CHAMPS


class ErreurFichier(Exception):
    """Erreur de lecture/écriture du fichier CSV."""


class GestionZoo:
    def __init__(self, chemin_fichier_csv="animaux.csv"):
        self.liste_animaux = []
        self.chemin_fichier_csv = chemin_fichier_csv

    #Gestion des animaux
    def trouver_animal(self, identifiant):
        for animal in self.liste_animaux:
            if animal.identifiant == identifiant:
                return animal
        raise ValueError(f"Aucun animal avec l'identifiant « {identifiant} ».")

    def ajouter_animal(self, animal):
        for existant in self.liste_animaux:
            if existant.identifiant == animal.identifiant:
                raise ValueError(f"L'identifiant « {animal.identifiant} » existe déjà.")
        self.liste_animaux.append(animal)

    def supprimer_animal(self, identifiant):
        animal = self.trouver_animal(identifiant)
        self.liste_animaux.remove(animal)

    def modifier_animal(self, identifiant, nom, espece, age, poids, enclos, statut_sante):
        animal = self.trouver_animal(identifiant)
        animal.modifier_infos(nom, espece, age, poids, enclos, statut_sante)

    def rechercher_animal(self, texte):
        """Retourne les animaux dont un champ contient le texte (liste complète si texte vide)."""
        texte = texte.strip().lower()
        if texte == "":
            return list(self.liste_animaux)
        resultats = []
        for a in self.liste_animaux:
            champs = [a.identifiant, a.nom, a.espece, a.enclos, a.statut_sante]
            if any(texte in c.lower() for c in champs):
                resultats.append(a)
        return resultats

    def afficher_animaux(self):
        """Retourne une liste de textes (un par animal)."""
        lignes = []
        for i in range(len(self.liste_animaux)):
            a = self.liste_animaux[i]
            lignes.append(f"{i + 1}. {a.identifiant} - {a.nom} ({a.espece})")
        return lignes

    # Doyen, plus lourd, classement 
    def doyen(self):
        if len(self.liste_animaux) == 0:
            raise ValueError("Le zoo ne contient aucun animal.")
        return max(self.liste_animaux, key=lambda a: a.age)

    def plus_lourd(self):
        if len(self.liste_animaux) == 0:
            raise ValueError("Le zoo ne contient aucun animal.")
        return max(self.liste_animaux, key=lambda a: a.poids)

    def classer_animaux(self, critere="age", decroissant=True):
        if critere not in ("age", "poids"):
            raise ValueError("Le critère doit être « age » ou « poids ».")
        return sorted(self.liste_animaux, key=lambda a: getattr(a, critere), reverse=decroissant)

    #  Statistiques 
    def afficher_statistiques(self):
        """Retourne un dictionnaire de statistiques (le calcul est fait ici, pas dans l'interface)."""
        par_statut = {s: 0 for s in Animal.STATUTS}
        par_espece = {}
        total = len(self.liste_animaux)
        if total == 0:
            return {"total": 0, "age_moyen": 0.0, "poids_moyen": 0.0,
                    "age_max": 0, "age_min": 0, "poids_max": 0.0, "poids_min": 0.0,
                    "par_statut": par_statut, "par_espece": par_espece}

        ages = [a.age for a in self.liste_animaux]
        poids = [a.poids for a in self.liste_animaux]
        for a in self.liste_animaux:
            par_statut[a.statut_sante] += 1
            par_espece[a.espece] = par_espece.get(a.espece, 0) + 1

        return {"total": total,
                "age_moyen": round(sum(ages) / total, 2),
                "poids_moyen": round(sum(poids) / total, 2),
                "age_max": max(ages), "age_min": min(ages),
                "poids_max": max(poids), "poids_min": min(poids),
                "par_statut": par_statut, "par_espece": par_espece}

    #  Persistance CSV 
    def sauvegarder_dans_csv(self, chemin=None):
        chemin = chemin or self.chemin_fichier_csv
        try:
            with open(chemin, "w", newline="", encoding="utf-8") as f:
                ecrivain = csv.DictWriter(f, fieldnames=CHAMPS)
                ecrivain.writeheader()
                for animal in self.liste_animaux:
                    ecrivain.writerow(animal.to_dict())
        except OSError as e:
            raise ErreurFichier(f"Impossible d'écrire le fichier : {e}")

    def charger_depuis_csv(self, chemin=None):
        """Charge les animaux d'un CSV. Retourne (nb_acceptées, nb_rejetées).
        Les lignes invalides (mal formées, valeurs interdites, id en double) sont ignorées."""
        chemin = chemin or self.chemin_fichier_csv

        # Fichier de travail absent : on le crée avec les en-têtes
        if chemin == self.chemin_fichier_csv and not os.path.exists(chemin):
            self.sauvegarder_dans_csv(chemin)
            return 0, 0

        acceptees = 0
        rejetees = 0
        try:
            with open(chemin, newline="", encoding="utf-8-sig") as f:
                lecteur = csv.DictReader(f)
                if lecteur.fieldnames is None or any(c not in lecteur.fieldnames for c in CHAMPS):
                    raise ErreurFichier("Le fichier n'a pas les colonnes attendues : " + ", ".join(CHAMPS))
                for ligne in lecteur:
                    # Ligne mal formée : trop courte ou trop longue
                    if None in ligne or None in ligne.values():
                        rejetees += 1
                        continue
                    try:
                        animal = Animal(ligne["identifiant"], ligne["nom"], ligne["espece"],
                                        ligne["age"], ligne["poids"], ligne["enclos"],
                                        ligne["statut_sante"])
                        self.ajouter_animal(animal)
                        acceptees += 1
                    except ValueError:
                        rejetees += 1
        except (OSError, csv.Error, UnicodeDecodeError) as e:
            raise ErreurFichier(f"Impossible de lire le fichier : {e}")
        return acceptees, rejetees
