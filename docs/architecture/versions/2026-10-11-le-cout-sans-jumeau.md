# Version du 11 octobre 2026 : le coût sans jumeau

Les deux moteurs ne sont plus jumeaux sur le coût (§ 7.1). Coût, Carrières
types et Droits non cotisés ont perdu leurs réglages libres, sur la décision
du propriétaire du 10 octobre (action 150) : elles ne montrent plus que la
référence, et ce qu'elles en lisent — le coût agrégé, chaque année de sa
cascade et sa vue des flux, le coût des avantages non contributifs, les
carrières types, les départs qui classent les écarts — ne se calcule plus
qu'en Python. `scripts/construire_donnees.py` le fige dans
`data/derive/agregats.json`, que le paquet porte à côté du bilan figé, et les
deux langages le lisent par les mêmes accesseurs, `donnees/agregats.py` et
`moteur/js/agregats.js`, qui ne calculent rien qu'une règle décide. Le
JavaScript ne copie plus que ce qui dépend de la saisie du lecteur, une
carrière (principe 4) : `cout.js`, `avantages.js`, `castypes.js` et
`population.js` sont partis, avec les tests de parité du coût et les témoins
des pages sous d'autres réglages. Le site qui reçoit un paquet d'une autre
version que la sienne le redemande une fois, puis dit au lecteur de
recharger la page : plus aucune page ne refait chez lui un calcul qu'un vieux
paquet ne porterait pas. Le § 8 le dit de la page Coût et des réglages du
simulateur, et le § 7.7 trouve le coefficient d'équilibre dans `cout.py` ;
les consignes de `src/` et de `moteur/` cessent de demander le portage du
coût, et disent où s'ajoute un chiffre d'une page qui agrège.
