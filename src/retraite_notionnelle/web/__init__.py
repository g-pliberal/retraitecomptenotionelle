"""Le site, vu du Python.

Le site publié ne passe pas par Python : il exécute un portage JavaScript du
modèle (``moteur/js/``), et son texte n'est écrit qu'une fois, là
(docs/architecture.md, § 8). Ce paquet garde ce que le Python en lit :
``site.py``, le pont par lequel les tests, les témoins de pages et les sondes
de la prose lisent le site, et ``releve_lu.py``, le lecteur des relevés de
carrière. L'ancien rendu Python, ``pages.py`` et ``gabarit.py``, retiré à la
phase 8, se relit dans l'historique git au repère ``phase-7``.
"""
