# Les pages tirées au hasard, mesurées et laissées telles quelles

**Le 29 octobre 2026.** `test_les_pages_au_hasard_calculent_et_refusent_comme_le_modele`
(`tests/test_web.py`) rend cinquante-deux pages par le portage, quarante
saisies par le revenu et douze par la pension, que la page inverse, et
confronte le refus de chacune à celui que le pont rapporte de la même saisie ;
le moteur Python simule la carrière des dix-sept que la page calcule. Mesuré
sur ce conteneur à quatre cœurs, le test seul fait 11 s : 8,4 s de pages,
1 s de pont, 1,3 s de simulations Python. Dans un processus qui a déjà chargé
le modèle, le pont et le site, comme celui de la suite qui le prend après
d'autres tests du fichier, 8,2 s : 6,9 s de pages, dont 4,1 pour les douze par
la pension, 0,7 s de pont et 0,5 s de Python.

**Pourquoi il reste tel quel.** `moitie_python` ne garderait que le pont et le
Python, 1,2 s sur 8 ; les pages, ce que le test éprouve, se rejoueraient. Ce
peu ne se gagnerait que sur un poste ou un conteneur : GitHub, sans mémoire,
refait tout. Et la durée n'en bougerait pas : le test, au niveau `complet` et
hors de `-m site`, ne tourne en local qu'avec tout `test_web.py`, 101 s à
chaud sur quatre processus, que `test_les_temoins_du_portage_sont_a_jour`
tient à lui seul (70 s), pendant que les 12 s de celui-ci courent sur un
autre. Garder cette moitié ajouterait enfin un quatrième cas au défaut
ci-dessous.

**Ce que la mesure a fait voir.** Le pont lit le paquet du dépôt,
`moteur/donnees.json`, que ni l'empreinte de la mémoire (`memoire.SOURCES`) ni
la clé de `moitie_python` ne lisent. Une moitié calculée sur un paquet en
retard sur `data/`, avant `regenerer.py`, se garde sous l'empreinte des
données nouvelles, et resservirait, les sources inchangées, une fois le paquet
refait. Trois moitiés gardées passent par le pont : `_carrieres_au_hasard`
(`test_web.py`) et les `_python` de `test_droit.py` et de `test_liquidation.py`.
Le remède tiendrait dans `moitie_python`, l'empreinte du paquet dans la clé,
éprouvée d'abord par `test_outillage.py` ; hors de cette tâche, il reste à
faire.

**Ce qui reste**, de l'action : le paquet du dépôt dans la clé de
`moitie_python` ; `actions/cache` sur GitHub, le modèle et l'effort des
sessions, que le propriétaire décide ; la part de l'éclaireur, à relever ; les
leviers 4 et 5.
