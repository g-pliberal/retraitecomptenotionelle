# Étape 7 : le solde du suivi du panorama de la DREES, treize fiches lues feuille à feuille et recoupées à ce que le dépôt porte

**Reprise, au 6 novembre 2026.** Fait : les feuilles non lues des fiches 1, 3,
10, 12, 15, 16, 17, 21, 23 et 28, lues à la source et recoupées par 29 tests
neufs (`tests/test_drees_panorama_solde.py`, témoin
`tests/temoins/drees_panorama_2026_solde.json`) ; les fiches 22, 25 et 27 n'en
avaient plus ; chaque fiche porte son `solde` au suivi. Reste : le jeu
`drees_minimum_vieillesse`, à ouvrir depuis le poste du propriétaire ; les trois
erreurs du coût (note des règles, 3 novembre) et l'effet des écarts de J4, qui
attendent le propriétaire ; les candidats de la section 5 ; la relecture R-J5.
Par quoi commencer : la section 5, si le propriétaire veut l'un des candidats.

**La demande.** Vague 12, tâche J5, le 6 novembre 2026 : solder le suivi
`data/reference/drees_panorama_2026.yaml` — les neuf fiches rangées à l'étape 7
(01, 03, 10, 16, 17, 22, 23, 25, 27), les feuilles des fiches 15, 16 et 28 que
J4 et J4-bis nomment, la fiche 21, la fiche 12 et le jeu
`drees_minimum_vieillesse` — en lisant chaque feuille à la source, en disant ce
que le dépôt en tire et en rangeant chaque fiche au suivi, avec pour chaque
chiffre tiré le test qui le recoupe. L'exigence du propriétaire (3 novembre) :
« aucune erreur [...] toujours vérifier avec un document source à la clé et ne
jamais faire confiance à ta propre mémoire ».

**Les sources.** `python scripts/fetch/source_locale.py --recuperer` a rapporté le
PDF (SHA-256 `9eb36a06…735e9be`) et l'archive des classeurs (`ec7503f8…aaf64911`),
que `sha256sum` retrouve : ceux de J4 et de J4-bis. Le PDF par `pdftotext
-layout`, page à page : le folio imprimé est la page du fichier moins un. Les
classeurs par `openpyxl` (`data_only`) pour l'exploration, par `lecture_xlsx`, le
lecteur du dépôt, pour le témoin, que `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`
relit au bit près. Le témoin est fabriqué par un script de brouillon, hors dépôt,
qui lit chaque cellule : aucune valeur n'est saisie à la main.

## 1. Ce qui a été lu, feuille par feuille

« Lues » : ouvertes, dimensionnées, leur titre, leurs en-têtes, leurs notes et
leurs chiffres relevés ce jour. « Recoupée » : un test la confronte à un fichier du
dépôt ou à une autre feuille.

| fiche | feuilles lues le 6 novembre | verdict |
|---|---|---|
| 01 | Graphique 2 (flux), Tableau 2 compl, Carte 1, Tableau 3, Graphique 4 (pyramide) | quatre recoupées ; la carte 1 (100 lignes de départements) hors champ |
| 03 | Tableau 1, Tableau 2, Tableau 2 compl, Graphique 1 (flux), Tableau 3, Graphique 3 (pyramide) | six recoupées, entre elles et à la table C |
| 10 | Tableau encadré 1, Graphique encadré 1, Tableau 1, Graphique1, Tableau 2, Graphique 2 | six recoupées |
| 12 | Synthese, Graphique 1 (2) à Graphique 5 (2) | lues ; copies de travail de l'édition précédente, non tirées ; Graphique 1 (2) confronté |
| 15 | Graphique 3, Graphique 3 compl, Graphique 4 | trois recoupées |
| 16 | Graphique 1, Graphique 2, Graphique 4, Graphique 5 compl | quatre recoupées |
| 17 | Graphique 2, Graphique 3 compl, Tableau compl - Surcote (colonnes D à H), Tableau compl - Decote (colonnes D à G) | quatre recoupées |
| 21 | Graphique encadré 2, Tableau encadré 2, Synthese, F21_Graphique 1 REVISIONS | recoupées ; Tableau 1, Tableau 2, Tableau 3 et Graphique 2 REVISIONS lues par leurs en-têtes seuls |
| 23 | Graphique 1 compl. | recoupée |
| 28 | Tableau 1, Tableau 2, Tableau 3, Tableau 4, Carte 1 | tableaux 1 et 2 recoupés ; 3 et 4 lus sans contrepartie ; carte hors champ |
| 22, 25, 27 | — | aucune feuille ne reste : toutes lues aux étapes 2, 5 et 6 |

Les feuilles « REVISIONS » de la fiche 21 autres que celle du graphique 1 n'ont pas
été vérifiées cellule par cellule : je ne le prétends pas.

## 2. Les recoupements, un par un

Chaque test cite dans sa docstring la feuille, la cellule et le calcul ; je ne
reprends ici que les chiffres qui décident.

**Fiche 10 (folios 99 à 102).** Encadré 1, feuille « F10_Tableau encadré 1 » :
C5 = 426,7, D5 = 395,3, C7 = 359,7, C17 = 41,7 milliards d'euros. Le dépôt :
`depenses_retraite.csv` 2024, 426 665,3 M€ → 426,7 ; `pensions_droits.csv` 2024,
359 717,10 → 359,7 et 41 709,29 → 41,7 ; somme 401 426,39 → 401,4, que les
en-têtes des deux fichiers écrivaient déjà. Le « 93 % » du texte (folio 99) : 395,3
÷ 426,7 = 0,9264. PIB (« F10_Graphique1 », ligne 9) : de 1990 à 2022 identique au
million à `pib_courant.csv` (33 années) ; 2023 : 2 826,542 ÷ 2 833,826 = 0,99743, −0,26 % ;
2024 : 2 919,900 ÷ 2 935,236 = 0,99478, −0,52 %. La source ne dit pas le millésime de son
PIB : écart déclaré, non tranché. La part de 2024 : 395 338,73 ÷ 2 935 236 = 13,469 %
(13,5 publié), de 2023 : 370 465,23 ÷ 2 833 826 = 13,073 % (13,1) : l'arrondi les
rend identiques. La comparaison européenne (« F10_Graphique encadré 1 », E29 =
14,61) : 426 665,3 ÷ 2 919 900 = 14,612 % avec le PIB du panorama, 14,536 % avec celui
du dépôt. Les évolutions du tableau 2 : 370 465,23 ÷ 352 661,25 = 1,05048, 6,714 %
pour 2023-2024, 5,048 % pour 2022-2023 ; (395 338,73 ÷ 105 934,19)^(1/34) = 1,03949.
La cellule D7 de « F10_Tableau 2 » est du texte, « 5,0 ».

**Fiche 1 (folios 22, 23, 25, 27 et 29).** Pyramide (« F01_Graphique 4 », C5:D14) : la table C
de l'EACR (`tests/temoins/drees_eacr_tables_2026.json`, séries `ddir`) donne, sur 17 298 245
retraités, les femmes à 0,052 %, 0,071, 0,247, 5,279, 11,139, 11,381, 10,058, 6,206,
4,836 et 3,871 % par classes d'âge, les hommes à 0,224, 0,217, 0,394, 5,922, 10,391,
10,204, 8,915, 5,287, 3,457 et 1,849 % : chaque cellule publiée est à moins de 0,05
(le plus éloigné, 1,849 pour 1,8, à 0,049). La dernière classe est « tout ce qui reste » : les
âges de la table C ne vont pas jusqu'au bout sans la clé « plus de 95 ». Tableau 2
complémentaire : 18 caisses et le total, l'effectif à mille près (CNAV 14 744 736 →
14 745), les évolutions de 2023-2024 et de 2020-2024 à 0,05 point ; 2014-2024 pour 14 lignes.
Le régime général : le cadrage donne +14,1 %, la source +13,2 % : 0,9 point,
la note 2 renvoie à l'annexe 3 sur l'« intégration de la SSI au régime général ». Banque de
France, CANSSM, Enim : 0 publié, sans 2014 au cadrage ; pour la CANSSM, +30,7 % entre
2014 et 2020 (1 ÷ 0,765 = 1,307) seraient nécessaires à un vrai zéro, quand elle perd
23,5 % de 2020 à 2024 : je lis un zéro non disponible, sans pouvoir le prouver. Flux :
la variation publiée est la différence des stocks du tableau 1 à un millier près
(2005 : 13 263 − 12 961 = 302 pour 302,2) ; 2018-2020 « nd ». 2024 : 717,6 (C24) =
« 718 000 primo-liquidants » (folio 29) ; la table C compte 857 880 liquidants, soit
140,28 mille de plus.

**Fiche 3 (folios 36 à 39).** Tableau 1 (E26) : 4 406,64 mille bénéficiaires d'un
droit dérivé fin 2024 = 3 836,17 + 570,46 ; les tableaux 2 (E6) et 2 compl (E6) la
redonnent, le tableau 3 l'arrondit à 4 407 ; les 3 861,5 mille résidant en France (I26)
font 87,63 % (87,6, E9 du tableau 3). Graphique 1 : 4 406,64 − 4 368,15 = 38,49
pour 38,5 en 2024. Graphique 3 : les quatre colonnes de la pyramide font 100,1 ;
886 × 95,3 % ÷ 4 407 = 19,2 % de femmes en droit dérivé seul. Âges des bénéficiaires
d'un droit direct (colonne F du tableau 3) : 1,206, 11,201, 43,114, 30,466 et 14,013 %
à la table C pour 1,2, 11,2, 43,1, 30,5 et 14,0.

**Fiche 28 (folios 232 et 235).** Tableau 1, colonne G : 62 800, 208 600, 200 500,
129 500, 70 300, 45 700 et 36 400 allocataires ; le classeur de l'INSEE du dépôt
(`allocataires_minimum_vieillesse.csv`, 2024, femmes + hommes) donne 62,831 ; 208,574 ;
200,523 ; 129,514 ; 70,277 ; 45,744 ; 36,445 mille, total 753,908 (publié 753 900,
G14). 754 460 − 753 908 = 552 : l'écart déjà noté à la fiche 27. Tableau 2 : 77,04 %
de personnes seules (E15) = 50,636 + 26,406 (femmes seules + hommes seuls) ; 56,36 % de
femmes (I15) ; chaque cellule des 7 classes d'âge est au centième. La part dans la
population (colonne F) : 753 900 ÷ 17 291 318 (dépôt, 1er janvier 2024) = 4,36 %,
÷ 17 579 342 (projection au 1er janvier 2025) = 4,29 % ; publié 4,32 % ; la source
cite « Insee, estimation de la population (France) au 1er janvier 2025 » (folio 232).

**Fiche 15 (folios 140 et 141).** L'âge conjoncturel de « F15_Graphique 1 » (lignes 5
à 7) est 50 + Σ de 50 à 70 ans de (1 − taux/100), par les taux de « F15_Graphique 3 »
(ensemble) et de « F15_Graphique 3 compl » (femmes, hommes) : 2024, 62,951 pour
62,95 ; 2004, 60,584 pour 60,58 ; 2014, 61,357 pour 61,36 ; les 63 valeurs de 2004
à 2024 à 0,0049 an au plus. Le bloc « Ensemble » du complément (lignes 57 à 77) diffère
du graphique 3 en 2023 à 16 âges sur 21 (62 ans : 55,79 contre 55,60 ; 69 ans : +0,32) ; l'âge qu'on
en tire, 62,733, n'est pas le publié, 62,75. Le dépôt garde, jusqu'en 2022, l'âge du
portail (`age_conjoncturel_depart.csv`) : jusqu'à 0,10 an de plus que le panorama
(2013, femmes : 61,63 − 0,10).

**Fiche 16 (folios 146, 147 et 149).** Les taux de retraités de 62 à 67 ans, 2024 et
2023, sont les mêmes chiffres dans « F16_Graphique 1 » (lignes 8 et 9), « F15_Graphique 4 »
(lignes 25 et 26) et « F15_Graphique 3 » (colonnes V et W) : 48,12 ; 70,71 ; 78,94 ;
84,79 ; 86,69 ; 94,30. La table C rapportée à la population du 1er janvier 2025 du
dépôt : 412 125 ÷ 848 498 = 48,57 % à 62 ans, +0,45 point ; +2,13 à 67 ans. Les taux de
nouveaux retraités de 2024 de la ligne 15 du graphique 1 sont ceux de la colonne W
du graphique 2 ; ceux de 2023 diffèrent à 19 âges sur 21, jusqu'à 0,60 point à 62 ans
(30,53 contre 29,93 %). Graphique 4 : 0,07 + 0,06 + 0,06 + 0,29 = 0,48 (femmes,
50-56 ans), comme 0,03 + 0,03 + 0,08 + 0,03 + 0,07 + 0,07 + 0,17 au graphique 1.
Complément du graphique 5, génération 1953 : six classes sur neuf à un point du tableau 1
du dépôt (femmes, 60 ans : 12 contre 11).

**Fiche 17 (folios 156 et 158).** Complément du graphique 3 : pour 12 générations et 9
modalités, la part de l'ensemble que le dépôt porte est entre celles des femmes et des
hommes à 0,1 point (1952, décote : 9,9 entre 11,8 et 7,9). Graphique 2 (génération 1957) :
le régime général 13,2 / 16,2 contre 13,1 / 16,1 au dépôt, les fonctionnaires civils de
l'État 16,6 / 25,6 contre 15,8 / 28,2, la MSA salariés 5,9 contre 5,1 en décote : le champ
du graphique 2 est « au moins un droit direct dans un régime de base », celui des
graphiques 4 et 5 « un droit direct dans le régime, [...] l'année de leurs 67 ans ». Les
moyennes de trimestres (régime général : décote 10,3, entre 52 × 1 + 40 × 10 + 8 × 19 ÷ 100 =
6,04 et 52 × 9 + 40 × 18 + 8 × 20 ÷ 100 = 13,48 ; surcote 7,7 au moins 5,15) restent dans
les bornes de leur ventilation.

**Fiche 21 (folios 190 et 191).** « F21_Graphique 1 REVISIONS » : 2025 + révision = 2026
pour 144 cellules (1946, femmes, absence : 15,47 − 0,34 = 15,13) ; la plus forte, 1,34
point. Encadré 2 : 27,97 + 46,51 + 24,23 + 14,69 − 13,40 = 100,00 ; la ligne « Somme »
est le total des 17 âges à 0,02 près.

**Fiche 23 (folio 204).** Complément du graphique 1 : à chaque âge de 61 à 80
ans, la colonne CNAV de « F23_Graphique 1 » est entre les femmes et les hommes
(65 ans : 7,5 entre 7,8 et 7,1).

**Fiche 12 (folio 114).** « Graphique 1 (2) », 1946 : 37,6 ; 44,1 ; 41,0 ; la feuille publiée et le
dépôt (`durees_validees_actifs.csv`) : 37,4 ; 44,0 ; 40,7.

## 3. Les défauts de la source, et ce qu'elle ne tranche pas

À citer avec précaution, chacun épinglé par un test :

1. Fiche 10, « F10_Tableau 2 », D7 : « 5,0 » est du texte, non un nombre.
2. Fiche 10 : le PIB de 2023 et 2024 n'est pas celui de `pib_courant.csv` (−0,26 et
   −0,52 %). Millésime non dit. **Point non tranché.**
3. Fiche 1, tableau 2 compl : trois évolutions 2014-2024 écrites 0 (Banque de
   France, CANSSM, Enim), à ne pas citer ; le régime général à 13,2 contre 14,1 au
   cadrage (la SSI) : **point non tranché**.
4. Fiche 3, tableau 2 : les évolutions de la CNRACL et de l'Ircantec sont des
   fractions (0,016, −0,01) quand le complément les écrit en pour cent (1,6, −1).
5. Fiche 15, complément du graphique 3 : le bloc « Ensemble » de 2023 n'est pas le
   graphique 3 (16 âges).
6. Fiche 16 : les taux de nouveaux retraités de 2023 diffèrent entre le graphique 1
   (« Ensemble (2023) ») et le graphique 2 à 19 âges : **deux millésimes, non
   tranché.**
7. Fiche 17, graphique 2 : le champ dit « secteur privé » et donne des colonnes de la
   fonction publique ; ses parts par régime ne sont pas celles des graphiques 4 et 5.
   **Deux lectures, non tranché.**
8. Fiche 23 : les deux feuilles ne datent pas l'intégration de la SSI de la même année
   (2020, 2021).
9. Fiche 12, « Synthese » : « A DECIDER » aux figures 2 et 5 : ce qui fut décidé pour
   l'édition 2026, le classeur ne le dit pas. **Non tranché.**

Aucune de ces lectures contraires n'est « intenable » : aucune n'est déclarée
erreur du dépôt ni de la DREES.

## 4. Le jeu `drees_minimum_vieillesse`

Le portail de la DREES (`data/sources_a_explorer.yaml`, jeu
`1377_le-minimum-vieillesse`) a refusé la connexion à J4 (« Connection reset by peer »).
Un seul essai de ce jour, une requête `HEAD` sur la page du jeu, a rendu HTTP 200 ; je
n'ai pas été plus loin, comme demandé : c'est une page, non les dix-huit classeurs.
**À ouvrir depuis le poste du propriétaire.**

## 5. Ce qui n'est pas tiré à `data/reference/`, et pourquoi

Chaque candidat demande la chaîne complète de l'étape 6 (lecture dans
`drees_panorama_classeurs.py`, certification dans `verifier_donnees.py`, jeu au
manifeste) et aucun calcul du dépôt ne lit ces chiffres aujourd'hui ; je ne les porte
pas sans décision :

- le sexe du taux de liquidation (fiche 17, complément du graphique 3), à
  `retraites_generations.csv` ;
- le cumul par sexe de 2022 (fiche 23), à `cumul_emploi_retraite_profil.csv` ;
- les flux de nouveaux retraités de droit direct et de droit dérivé (fiches 1 et 3) ;
- les trimestres moyens de décote et de surcote (fiche 17), pour la grille ;
- les tableaux 3 et 4 de la fiche 28 (type de pension et carrière des allocataires du
  minimum vieillesse), à confronter à la garantie de la proposition ;
- les pensions de retraite du champ PRRO, 1990-2024 (fiche 10).

**Candidat nommé, non traité** (J4-bis) : le folio 142 écrit « 61 ans et 7 mois » pour la
génération 1957, quand les tableaux donnent 61,85 et 61,88 ; il n'a pas croisé ma route.

## 6. Les tests

`tests/test_drees_panorama_solde.py`, 29 tests, tous vus rouges d'abord — le témoin
n'existait pas — puis verts une fois le témoin fabriqué ; les attentes viennent des
cellules et des calculs de la section 2, posés à la main avant d'être écrits. Plusieurs
attentes sont des écarts de la source, épinglés après les avoir mesurés (section 3) :
elles bougent si la DREES publie un erratum. Lancés : les cinq fichiers de tests de la
DREES, sous les deux jeux de présomptions ; `tests/test_controle_drees_panorama.py` ;
`python -m pytest -m rapide`, sous les deux jeux ; la prose.
