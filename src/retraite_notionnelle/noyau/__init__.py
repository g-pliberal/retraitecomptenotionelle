"""Le noyau de l'architecture : ce qui ne change qu'avec une décision écrite.

``docs/architecture.md``, § 13.1. Ce paquet en porte la part que les données
décrivent, et que les deux moteurs liront de la même façon :

* :mod:`.vocabulaire` — les quatre sortes de dates qui décident, les dates
  nommées, et les listes de valeurs que les contrats emploient
  (``data/reference/vocabulaire/``) ;
* :mod:`.contrats` — les neuf contrats de données de l'annexe C, en schémas
  (``data/reference/contrats/``), et le validateur qui les applique.

Rien ici ne calcule une pension : les résultats du modèle n'en dépendent pas.
"""
