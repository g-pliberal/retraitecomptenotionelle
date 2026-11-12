# L'impôt sur le revenu de l'effet retour par le pont : le coût le demande au moteur JavaScript

L'effet retour du coût ne calcule plus l'impôt sur le revenu en Python : il
le demande au portage (`moteur/js/impot-revenu.js`), par le pont, un lot par
année, et un second de 1991 à 2014. Le coût de référence est identique au
bit, nombre par nombre. `impot_revenu.py` n'est pas retiré : ses tests le
tiennent encore, et eux seuls. Rien n'est gardé en correctif, et rien
n'attend une décision du propriétaire.

**La demande.** La ligne « l'impôt » de la table des décisions du 12 novembre
(`2026-11-12-les-decisions-du-proprietaire.md`), la session C2 de la note de
la question 1 (`2026-11-12-question-1-la-zone-grise.md`) : la demande au
pont, par année, `EffetRetour` branché. La relecture de la paire était faite
(`2026-11-12-relecture-la-garantie-et-l-impot.md`), et sa confrontation
directe écrite (`tests/test_relecture_zone_grise.py`).

## Ce qui change

- **Le pont** (`pont.py`, `impot` ; `pont.mjs`, `impotsDesFoyers`) : une
  demande de plus, `impot`. Elle porte une liste de `(année des revenus,
  foyer)`, le foyer en données sous les noms du portage
  (`{"declarants": [{"pensions": 30000.0, "age": 70}]}`), sous les
  paramètres du simulateur, avec la dernière année du barème et son
  indexation, les prix ou le salaire moyen. Le portage lit le barème au
  paquet, le projette une fois par simulateur, et rend de chaque foyer son
  impôt, dans la monnaie de l'année, et s'il est mis en recouvrement
  (`pont.ImpotDemande`) ; rien pour une année sans barème. Un foyer que
  l'impôt refuse arrête le lot et lève `ValueError`, du message du portage.
  Le bloc est à part des deux côtés, sous son titre ; rien d'autre du pont
  n'est remanié.
- **L'effet retour** (`effet_retour.py`) : `chiffrer` prélève d'abord toutes
  les pensions de l'année — celles du système actuel, puis de chaque
  scénario qui déplace la masse — par `_prelevements_des`, puis lit ses
  taux. `_preleves` écarte ce que la mémoire a déjà et prélève le reste
  ensemble ; `_impots_de` en fait le lot du pont. `_preleve`, `_impot` et
  `_prelevements` en sont le cas d'un seul. Avant 2026
  (`_preleves_historiques`, qui remplace `_preleve_historique`), la tranche
  de CSG se lit d'abord sans l'impôt là où il ne la change pas : depuis
  2015 partout, et de 1998 à 2014 sous le seuil d'exonération. Les autres
  pensions passent au taux plein dans le premier lot, et celles que l'impôt
  range ailleurs repassent dans un second, sous leur part déductible.
- **Ce que la classe ne porte plus** : `EffetRetour.baremes`, la chronique
  des barèmes projetée en Python. Elle garde `annees_imposees`, de la
  première année lue au fichier des barèmes à la dernière demandée : hors
  d'elles, l'impôt vaut zéro sans rien demander. `_impot(…, detail=True)`
  rend ce que le pont relit, non plus le calcul entier de `ImpotDuFoyer`.
- **Les en-têtes** de `impot_revenu.py`, de `effet_retour.py`, de `pont.py`
  et de `pont.mjs` disent qui calcule l'impôt du coût.

## Les lots, mesurés

Un coût de référence, sans mémoire : 81 années chiffrées, 105 lots, 16 430
impôts, 0,42 seconde dans le pont. Soit un lot par année, et un second pour
chacune des 24 années de 1991 à 2014. La note de la question 1 comptait
18 830 impôts : les 2 400 de moins sont ceux que le Python calculait au
taux plein avant de les refaire, quand la tranche ne dépendait pas de
l'impôt.

| | avant | après |
|---|---:|---:|
| le coût de référence, deux mesures | 30,7 et 31,2 s | 29,2 et 29,6 s |
| dont l'effet retour (`chiffrer`) | 1,17 et 1,26 s | 0,60 et 0,60 s |
| dont l'impôt | 0,80 et 0,86 s | 0,41 et 0,42 s |

## Ce qui est vérifié

*En faisant tourner le code.*
- Le coût de référence, comptes compris, écrit nombre par nombre par un
  essai jetable hors du dépôt : 37 629 valeurs, dont 3 078 de l'effet
  retour, la même empreinte avant et après le branchement.
- Trois impôts posés à la main sur le barème des revenus de 2024, que le
  portage rend : 1 365 €, 0 € et 3 587 € (le détail du calcul est dans le
  test).
- Les taux d'une année, les mêmes par lot que pension par pension, au bit,
  sur cinq années : 2030, 2020, 2010, 1995 et 1985.
- Le paquet refait par `python scripts/construire_donnees.py`, en 3 minutes
  20 : `data/derive/agregats.json`, `moteur/donnees.json`,
  `data/derive/equilibre.json` et les calibrations, identiques à l'octet.
  Aucun témoin déplacé, aucun fichier fabriqué modifié.

*En lisant le code.* Le portage projette le barème comme le Python le
faisait (`BaremesImpotRevenu.chronique`, des deux côtés) : la relecture du
12 novembre l'avait confronté au bit sur 40 000 foyers, de 1960 à 2070.

*Non mesuré.* Le coût sur des données d'ailleurs — une copie retouchée,
`Parametres(racine_donnees=…)`. Le pont y lance node à chaque demande, sur
leur paquet : un quart de seconde, mesuré sur une demande vide, soit, par
déduction, une trentaine de secondes de plus pour les 105 lots d'un coût. La garantie y échappait,
qui se passe du paquet ; l'impôt lit le sien.

## Tests

- `tests/test_pont.py` : le pont calcule l'impôt de chaque foyer, valeurs
  posées à la main et types relus, année sans barème comprise ; le barème
  projeté suit l'indexation demandée ; le refus d'un foyer et son message.
- `tests/test_effet_retour.py` : l'impôt d'une année se demande par lot — un
  seul en 2030, en 2020 et en 1985, deux en 2010 et en 1995 —, chaque
  pension une fois, et rend les mêmes taux que pension par pension ; sans
  node, l'effet retour s'arrête, sans repli.

Chaque test neuf a été vu rouge pour la raison attendue : `pont.impot`
n'existait pas ; sans node, le Python calculait encore. Sous
`PRESOMPTIONS_DECALEES=1`, la suite saute elle-même les quatre qui font
calculer le portage (« le portage lit ses présomptions dans le paquet ») ;
le cinquième passe.
La suite rapide, 4 888 passés ; les fichiers du coût et de la zone
(`test_effet_retour.py` en entier, `test_cout.py`,
`test_facteurs_depense.py`, `test_affirmations.py`,
`test_controle_drees_panorama.py`, `test_agregats.py`, `test_pont.py`,
`test_relecture_zone_grise.py`), 1 037 passés.

## Ce qui reste

1. **`impot_revenu.py` attend son retrait.** Plus rien de ce que le dépôt
   fabrique ne l'appelle. Le tiennent : `tests/test_impot_revenu.py`,
   `tests/test_referents.py` (`impot_aux_parametres`, `impot_du_bareme`),
   `tests/test_cycle_de_vie_portage.py` (`impot_du_foyer`) et
   `tests/test_relecture_zone_grise.py`. Les porter demande au pont le
   calcul entier d'un foyer, étape par étape : `pont.impot` n'en rend que
   deux valeurs, et s'étendra alors.
2. **La projection du barème en Python** (`donnees/impot_revenu.py` :
   `chronique`, `parametres`, `croissance_macro`) n'a plus d'appelant hors
   des tests non plus. Le chargeur reste : la fabrique écrit le paquet par
   lui, et l'effet retour y lit la première année.
3. **Les commentaires du portage renvoient encore au Python** (« voir
   `decote` dans le Python », cinq fois dans `impot-revenu.js`) : au
   retrait, ces explications sont à reporter, comme celles de la garantie
   l'ont été.
4. **Le coût sur des données d'ailleurs**, ci-dessus : une demande pour
   toutes les années, la boucle de `cout._avenir` refaite en deux passes, le
   ramènerait à deux lots. Non fait : l'étape demandait un lot par année,
   et je n'ai pas relevé qui chiffre un coût entier sur de telles données.
5. **La suite de l'action** : la revalorisation servie, puis le retrait.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
agrégat, aucun chiffre du site ; aucune règle du scénario 1 ; aucune garde.
