"""Le site, vu du Python.

Le site publié ne passe pas par Python : il exécute un portage JavaScript du
modèle (``moteur/js/``), et son texte n'est écrit qu'une fois, là
(docs/architecture.md, § 8). Ce paquet garde ce que le Python en lit :
``site.py``, le pont par lequel les tests, les témoins de pages et les sondes
de la prose lisent le site, et ``releve_lu.py``, le lecteur des relevés de
carrière. ``pages.py`` et ``gabarit.py``, l'ancien rendu Python, ne servent
plus qu'à comparer les deux rendus, jusqu'à ce que la phase 8 les retire.
"""
