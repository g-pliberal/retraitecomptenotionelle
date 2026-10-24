# Étape 3, vingt-troisième partie : le taux effectif dans le modèle — les pensions brutes et nettes de la DREES certifiées, la dépense nette du bilan et du paquet

**La demande.** Septième vague du 24 octobre 2026, cinq autres sessions en
parallèle, une tâche chacune : celle-ci, le premier point sans propriétaire du
bloc de l'étape, le taux effectif — le point 2 de « Ce qui reste » de la note
de la CSG effective (14 octobre), le point 1 de celle de la fourchette et des
leviers (19 octobre) : « un fichier de `data/reference/macro/`, avec sa ligne
de vérification, que `cout.py` lirait », puis, à une session des pages, la
dépense nette à côté de la brute. Ni ce que le bloc réserve au propriétaire,
ni les pages, que tient la session de l'action 173. Le taux ne dépend d'aucun
des choix réservés : il est celui de la DREES, et la dépense nette suit la
brute que la page montre, grille ou naissances de l'année.

**Le fichier, certifié.** `data/reference/macro/pensions_brutes_nettes.csv` :
la pension moyenne brute et la nette du tableau 2.1-a de la DREES (fin 2022),
de droit direct et toutes pensions comprises, de 2008 à 2022, soixante
valeurs, au niveau `certifiee`. Le récupérateur
(`scripts/fetch/drees_pension_nette.py`) dépose désormais les montants qu'il
lit dans `data/brut/drees_pension_nette.json` (`pour_la_certification`), que
`scripts/verifier_donnees.py` confronte au fichier (`source_pensions_brutes_nettes`,
la ligne `pensions_brutes_nettes` de `CERTIFICATIONS`) ; le journal
(`data/derive/certification.json`) le consigne, et le manifeste passe le jeu
`drees_pension_nette` de `controle` à `certifie`. Le portail de la DREES a
coupé ses connexions toute la session : le classeur des montants est venu au
septième essai, celui de l'EACR au douzième, les essais espacés de trente
secondes. Relu, il redonne exactement les montants du témoin du 14 octobre, et
le récupérateur, relancé sur les deux classeurs, le témoin à l'octet.

**Le modèle.** `DepensesRetraite` lit les deux moyennes toutes pensions
comprises : `taux_effectif(annee)` est un moins la nette sur la brute
(`depense_nette.taux_effectifs`), celles de `annee_du_taux_effectif(annee)`,
l'année elle-même de 2008 à 2022, 2022 après — comme l'Ageing Report tient
constante la part qu'il compte reprise —, 2008 avant. Chaque année du bilan
(`SoldeAnnuel`) porte ce taux et son année, et `depense_nette(scenario)` est la
dépense du système diminuée de ce taux : réversion comprise quand il la sert,
sans la garantie vieillesse du scénario 6, qui, comme l'ASPA, n'est ni dans la
dépense ni dans la pension nette de la DREES. Le même taux pour tous les
systèmes, l'hypothèse du site pour la pension nette d'une personne (décision
du 4 octobre 2026). Sous la référence, en points de PIB :

| | 2008 | 2022 | 2026 | 2050 | 2070 |
|---|---|---|---|---|---|
| taux effectif | 6,18 % | 6,81 % | 6,81 % | 6,81 % | 6,81 % |
| système actuel, brut | 12,43 | 13,63 | 14,13 | 14,37 | 15,30 |
| système actuel, net | 11,66 | 12,70 | 13,16 | 13,39 | 14,26 |
| système 6, brut | 6,02 | 8,57 | 8,87 | 9,75 | 8,07 |
| système 6, net | 5,65 | 7,98 | 8,27 | 9,08 | 7,52 |

L'Ageing Report publie 12,8 % du PIB de dépense nette en 2022 pour 14,4 en
brut : il retire 11,1 %, l'impôt sur le revenu compris, que le dépôt
n'agrège pas ; la nette du dépôt n'ôte que les prélèvements sociaux.
L'effet retour (`effet_retour.py`, étape 5) n'en a pas l'usage : il chiffre
les prélèvements sur la distribution des pensions, au barème de chaque année.

**Le paquet.** La table des agrégats fige, à chaque année du bilan, le taux et
son année (`CHAMPS_SOLDE_ANNUEL`) et la dépense nette de chaque système montré
(`PAR_SYSTEME_SOLDE_ANNUEL`, `depenses_nettes_par_systeme`), que lisent
`SoldeAnnuelFige.depense_nette` et son jumeau `depenseNette` de
`moteur/js/agregats.js`. Le paquet passe à la version 33 des deux côtés
(`VERSION`, `VERSION_PAQUET`), refait ici. Aucune page ne le lit encore.

**Les tests**, vus rouges pour la raison attendue avant le code :
`test_depense_nette.py` (rapide) — le récupérateur dépose les montants qu'il
lit, sur des grilles rendues comme celles des classeurs ; le fichier certifié
redonne le témoin, 1 719 € bruts et 1 602 € nets en 2022 ; `DepensesRetraite`
lit le taux de chaque année et tient le dernier ; la dépense nette d'une année
posée à la main ; `test_verification.py`, la source de la certification ;
`test_donnees.py`, le journal ; `test_cout.py`, le bilan complet, vu rouge
sans le branchement de `_solde` ; `test_agregats.py`, la table et ses deux
lecteurs.

**Ce que ça déplace.** Aucun chiffre de page ni témoin de simulation : la
dépense brute, le solde et la dette ne bougent pas. La table des agrégats et
le paquet gagnent leurs clés ; la page Méthode, une série certifiée de plus,
177 séries et 146 452 valeurs, que les chiffres ancrés suivent avec le poids
du paquet. Le paquet et les témoins de pages sont refaits ici ; celui de
Droits non cotisés y prend la retouche de l'étape 9 de l'action 173, que
GitHub n'avait pas encore refaite.

**Ce qui reste**, de cette partie ; le reste de l'étape est dans son bloc.

1. *La page Coût*, à une session du site : la dépense nette à côté de la
   brute, dans le bilan ; et le paragraphe « Et en BRUT, des deux côtés », qui
   dit la masse nette « au plus » au taux plein, 9,1 % (`pages.js`,
   `pensionsNettes.tauxTotal`), quand le bilan figé porte le taux de l'année.
   Puis le registre : `taxipp` et l'Ageing Report passent à `repris`.
2. *Les montants de 2023 et 2024*, que la DREES publie hors du classeur
   (point 1 de la note du 14 octobre) : ils diraient si le taux de 2022, tenu,
   est bas d'un demi-point, comme la CSG de 2023 le laisse croire.
3. *L'impôt sur le revenu des pensions*, agrégé, qui ferait la nette au sens
   de l'Ageing Report (étape 5), et *le taux de chaque système*, que le modèle
   ne projette pas (points 3 et 4 de la note du 14 octobre).
