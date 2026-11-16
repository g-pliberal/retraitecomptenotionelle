"""Les types que le pont échange avec le moteur JavaScript (action 161, étape 1
du retrait des règles Python).

Le pont relit sous ces types ce que calcule le portage. Ils logeaient dans les
fichiers de règles, que le retrait supprimera ; ils ont désormais ces modules,
qui ne chargent aucun fichier de règles (``tests/test_types_du_pont.py``), et
les fichiers de règles les réimportent le temps du retrait. ``Carriere`` y
loge nue : ses règles restent dans ``carriere.py``, sur une classe qui en
hérite, le temps du retrait.
"""
