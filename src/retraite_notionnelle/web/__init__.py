"""Le site, vu du Python.

Le site publié ne passe pas par Python : il exécute un portage JavaScript du
modèle (``moteur/js/``), et son texte n'est écrit qu'une fois, là
(docs/architecture.md, § 8). Ce paquet garde ce que le Python en lit :
``site.py``, le pont par lequel les tests, les témoins de pages, les sondes
de la prose et l'estimation officielle lisent le site, son lecteur des relevés
de carrière compris : son jumeau Python est parti à l'action 161, étape 3.
L'ancien rendu Python, ``pages.py`` et ``gabarit.py``, retiré à la phase 8, se
relit dans l'historique git au repère ``phase-7``.
"""
