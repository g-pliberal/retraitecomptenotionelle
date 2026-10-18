# Les chiffres en lettres du parcours

**Le 18 octobre 2026, la demande.** La vague du 18 octobre confie à une
session ce que la note des chiffres à unité laissait écrit à la main : les
chiffres en lettres du parcours, que l'ancre ne savait pas tenir — « seize
ans et demi » (65 − 48,5), « dix points » (28 − 18), « cinq points rendus » —,
ses années, et les étiquettes du tableau de Pourquoi changer, que le parcours
paraphrasait.

**L'ancre apprend les lettres** (`scripts/verifier_prose.py`, testé d'abord
dans `tests/test_prose.py`). Une ancre sans chiffre lit son nombre en lettres,
de zéro à 999 999, à la précision qu'il se donne — l'entier, ou la demie quand
il dit « et demi » —, tolérance comprise ; `--corriger` le récrit en lettres,
dans l'orthographe d'avant 1990 que le dépôt écrit, la majuscule et l'unité
gardées, et dit sans rien récrire ce qui ne s'écrit pas en lettres, un
négatif. Une sonde de plus, `difference`, ôte une sonde d'une autre
(`mesure:…;valeur:…`), pour un chiffre que la prose déduit de deux qu'elle
ancre déjà ; les mesures qu'elle cite se calculent d'avance avec les autres.
`scripts/fusionner.py`, que `pousser.sh` appelle au rebasage, fusionne une
valeur en lettres comme un chiffre (`tests/test_fusionner.py`).

**Deux sondes d'années** (`scripts/mesures_prose.py`). `repere … quoi=etiquette`
lit le nombre de l'étiquette d'une fiche de tête, l'année que la page récrit
avec ses données ; `coefficient … quoi=annee`, l'année où un coefficient se
lit, l'horizon par défaut.

**Ce qui est ancré.** « seize ans et demi », sur l'âge légal de la
proposition moins l'âge de radiation du militaire, dans le paquet ; « dix
points », sur le taux de la fiche de paie moins celui de la proposition,
27,98 − 18 ; les trois « cinq points rendus », sur
`taux_capitalisation_volontaire` ; les statuts du menu, les treize carrières
et les sept générations de Cas types, et leurs bornes, 1940 et 2000, sur le
paquet ; les six « 2070 », sur l'horizon du coefficient ou sur l'étiquette de
Pourquoi changer ; « en 2025 », sur l'étiquette de Coût ; 1941, la bascule de
2026, deux fois, et les euros de 2026, sur les paramètres.

**Ce qui avait dérivé.** Les statuts du menu : « soixante-deux », pour 73.
Les étiquettes des repères de Pourquoi changer, que la page avait récrites le
17 octobre — « Promis au-delà de ce que VOS cotisations achèteraient », « Que
les recettes du SYSTÈME ne couvriront pas en 2070 » —, et la précision
d'« Encaissé pour le payer », « cotisations et impôts ».

**Les étiquettes, tenues.** `test_les_reperes_du_parcours_portent_l_etiquette_de_leur_page`
exige que chaque ligne d'un tableau de repères porte, mot pour mot,
l'étiquette de la fiche que son ancre lit, et sa précision. Il est du filet
`-m site` (`SITE`, dans `tests/conftest.py`) : une retouche des pages qui
change une étiquette le fait tomber avant l'envoi, et la session des pages
reprend le parcours avec elle.

**Ce qui reste écrit à la main.** Les saisies (1975, 1996, 1998, 2000, 2022,
2039, 2064, 64 ans) ; les dates des récits (20, 23 et 24 septembre 2026) ;
les années que les ancres prennent en argument — 2026 du taux de l'État, 2004
et 2025 de « Qui paie ? », les générations de Cas types ; les débuts des
séries, 1959 et 1831, qu'aucune sonde ne lit, faute de minimum sur un JSON ;
les réformes que Pourquoi changer aligne, de 1993 à 2023. En lettres : les
durées de la présentation ; les comptes de la structure des pages — neuf
règles d'indexation, treize questions, quatre cartes, justes au 18 octobre ;
les citations de la page — « une réforme tous les huit ans », « plus de
quatre cent mille euros », « vingt-sept ans et demi de services », du libellé
du cas type ; les approximations — « doublé en vingt ans », « un peu plus de
la moitié », « pendant trente ans ». Et les noms des onglets, que le parcours
garde d'avant : Risque, Cas types, Avantages, Données, pour Pourquoi changer,
Carrières types, Droits non cotisés, Méthode et sources (`TITRES`, dans
`pages.js`) ; les titres de ses sections, que `PAGES_DES_SECTIONS` nomme, les
portent aussi.

**Vérifié.** `tests/test_parcours.py`, `tests/test_prose.py`,
`tests/test_fusionner.py` et `tests/test_niveaux.py` passent, 98 tests ; la
suite rapide aussi, 2 752 ; `verifier_prose.py` ne relevait plus que
« soixante-deux », corrigé.
