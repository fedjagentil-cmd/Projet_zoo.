# Gestion des animaux d'un zoo (PyQt6 + CSV + POO)

## Installation et lancement
```
pip install -r requirements.txt
python main.py
```
Lancer la commande depuis le dossier `projet_zoo_pyqt`.

## Choix techniques (à reprendre dans le rapport)
- **PyQt6** : version actuelle et maintenue de PyQt.
- **Colonnes CSV** : identifiant, nom, espece, age, poids, enclos, statut_sante = exactement les 7 attributs de `Animal`.
  Une ligne = un animal ; `to_dict()` produit la ligne, `csv.DictWriter` l'écrit.
- **Encodage UTF-8** : gère les accents (Éléphant, Zèbre). La lecture utilise `utf-8-sig` pour accepter aussi les CSV venant d'Excel.
- **Seuil senior** : 15 ans (choix arbitraire, valable pour la plupart des animaux de zoo ; à justifier dans le rapport).
- **Séparation** : `animal.py` et `gestion_zoo.py` ne connaissent pas PyQt ; `interface/` n'accède jamais au CSV directement.
- **Sauvegarde** : bouton « Enregistrer » (menu Fichier) + proposition d'enregistrer à la fermeture (`closeEvent`).
- **Bonus inclus** : lignes colorées pour « Malade » et « Sous surveillance ».
