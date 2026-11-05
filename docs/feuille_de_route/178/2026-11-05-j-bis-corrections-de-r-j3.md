# J-bis, les corrections de la relecture R-J3 : la garantie de la page, sur quelles pensions et à quel coût net, face à l'Aspa et à l'ASV (fiche 27)

**Le 5 novembre 2026 : la relecture R-J3 a raison sur le point moyen, et sur
les quatre faibles, que j'ai tous refaits ; je ne suis en désaccord qu'avec
ses valeurs à « pensions servies », qu'elle donne par un calcul de session et
que je donne, bornées, par la fonction du dépôt. Le chiffre de la page (2,80
millions de bénéficiaires, 14,31 milliards constants de 2026) est calculé sur
les pensions du système 4, le facteur 0,7365, non sur les pensions servies :
3,71 fois les allocataires de l'ASV et de l'Aspa, 3,12 fois les personnes avec
leurs conjoints, 3,03 fois leurs dépenses, en euros de même base. À pensions
servies, de 1,85 à 2,83 fois les allocataires et de 1,27 à 2,38 fois les
dépenses ; à l'estimation, 2,4 et 2,0. Le coût de la garantie est brut des
minima qu'elle remplace : net des quatre minima de la page, 6,43 milliards
courants de 2024, et non « 14,3 − 4,8 = 9,5 ».**

Demande : la vague 10, tâche J-bis, lancée par la session d'orchestration le 5
novembre 2026 : corriger, dans le commit `bf7098a` (note
`2026-11-05-etape-5-fiches-16-27.md`), ce que la relecture R-J3
(`2026-11-05-relecture-r-j3.md`, commit `cd362c9`) relève. Règle : ne pas se
fier à la relecture, rouvrir, refaire les calculs, dire le désaccord avec la
preuve.

**Ce que j'ai rouvert, et comment.** Le PDF du miroir de l'UNSA (SHA-256
`9eb36a06…735e9be`, celui du manifeste), folio 226, note 1 ; les classeurs
(`test_chaque_valeur_du_temoin_est_celle_de_sa_cellule` relit les 104 cellules
au bit près et passe) ; le code, aux lignes que R-J3 nomme, et les valeurs du
dépôt par ses propres fonctions, sans script versé : `mesures_prose._avenir`
pour la ligne de 2024, `garantie.cout_garantie` pour le barème, `memoire.avantages`
pour les minima, `macro.coefficient_prix` pour les euros.

## 1. Point moyen : de quelles pensions est calculé le chiffre de la page

**Je suis d'accord, et je le prouve par le code.** La ligne de 2024 de la page
porte `GarantieProjetee.facteur` = 0,736480 (2020 : 0,6222 ; 2026 : 0,7632 selon
R-J3, non refaits ici), `effectif` = 14 393 071,46, `beneficiaires` = 2 800
133,24, `ayants_droit` = 5 600 266,47, `cout_constants` = 14 307,10 M€. Le
facteur est celui par lequel la distribution des pensions de l'EIR 2020 est
déplacée avant le barème (`garantie.py`, docstring : « À `facteur = 1`, le
barème est appliqué aux pensions TELLES QU'ELLES SONT : c'est ce que la
garantie coûterait aujourd'hui, en remplacement de l'ASPA ») ; la page le dit
elle-même : « Garantie vieillesse, aux pensions du système 4 en … »
(`moteur/js/pages.js`, `lignesRemplaces`, vers la ligne 13341). Ma phrase,
dans la note et dans le test, disait « aujourd'hui » du chiffre de la page : le
champ était mal nommé.

**À pensions servies, par la fonction du dépôt.** `garantie.cout_garantie(
simulateur.distribution, effectif, plancher, facteur)`, avec l'effectif de la
page (14 393 071), la distribution de l'EIR 2020 (millésime 2020), les deux
planchers de la page ramenés aux euros de 2020 (`coefficient_prix(2026, 2020)` =
0,850999 : 800 → 680,80 ; 1 050 → 893,55), le recours de 50 % et le passage aux
euros constants de 2026 (`coefficient_prix(2020, 2026)` = 1,175089) :

| facteur | plancher | part sous le plancher | ayants droit | bénéficiaires (50 %) | coût constants de 2026 (50 %) |
|---|---|---|---|---|---|
| 0,7365 (la page) | 800 € | 31,19 % | 4 489 498 | 2 244 749 | 8 984 M€ |
| 0,7365 (la page) | 1 050 € | 44,07 % | 6 343 422 | 3 171 711 | 17 123 M€ |
| 1 (pensions servies) | 800 € | 19,42 % | 2 795 134 | 1 397 567 | 6 019 M€ |
| 1 (pensions servies) | 1 050 € | 29,67 % | 4 269 908 | 2 134 954 | 11 246 M€ |

La page mêle les deux planchers (le recensement dit qui vit seul, âge par âge
et par sexe, `_garantie_distribution`) : son chiffre est entre eux au facteur
0,7365, 2 244 749 < 2 800 133 < 3 171 711 et 8 984 < 14 307 < 17 123 — comme
`test_affirmations.py` le vérifie de son côté. Posé à la main, ce que cela
donne aux pensions servies (le test l'asserte) :

- bénéficiaires ÷ allocataires : 1 397 567 ÷ 754 460 = 1,85 ; 2 134 954 ÷ 754 460
  = 2,83 ;
- coût courants de 2024 = coût constants de 2026 × 0,973620 (`coefficient_prix(
  2026, 2024)`) : 6 019 × 0,973620 = 5 860 ; 11 246 × 0,973620 = 10 949 ;
  ÷ 4 600 (les 4,6 milliards de la DREES, en M€) : 1,27 et 2,38 ;
- le poids du plancher de qui vit seul que la page donne à son chiffre :
  (2 800 133 − 2 244 749) ÷ (3 171 711 − 2 244 749) = 0,599 pour les
  bénéficiaires ; (14 307 − 8 984) ÷ (17 123 − 8 984) = 0,654 pour le coût ;
  gardé au facteur 1 : 1 397 567 + 0,599 × (2 134 954 − 1 397 567) = 1 839 337
  bénéficiaires, 2,44 fois les allocataires ; 6 019 + 0,654 × (11 246 − 6 019) =
  9 437 M€ constants de 2026, 9 188 M€ courants, 2,00 fois les 4 600. **C'est
  une estimation par interpolation, non une mesure** : elle suppose que la
  part de qui vit seul pèse pareil aux deux facteurs, ce que la page, qui
  pèse par sexe, ne garantit pas.

**Où je diffère de R-J3, sans désaccord de fond.** Elle donne un seul ordre de
grandeur (« environ 1,7 à 1,9 million », 2,3 à 2,5 fois ; 9,5 milliards, 2,1
fois, 2,0 de même base), tiré d'un rapport de 0,62 à 0,67 sur le chiffre de la
page. Ses rapports sont les miens : 1 397 567 ÷ 2 244 749 = 0,623 et 2 134 954 ÷
3 171 711 = 0,673 pour les bénéficiaires ; 6 019 ÷ 8 984 = 0,670 et 11 246 ÷
17 123 = 0,657 pour le coût. Ses valeurs absolues du tableau (15 291 et 29 144
M€) sont avant le recours et en euros de 2020 : 8 984 ÷ 0,5 × 0,850999 =
15 291. La seule différence est que je donne les bornes que le dépôt
calcule (1,85 à 2,83 fois), plus larges, avec l'estimation (2,4) dedans.

## 2. Les quatre points faibles

1. **Euros.** Le coût de la page est en euros constants de 2026 ; `AvenirAnnuel
   .cout` le rend en euros courants de 2024 : 14 307,10 × 0,973620 = 13 929,68
   M€ (le dépôt rend 13 929,677739 ; `moteur/js/agregats.js`, vers la ligne 406 : `cout`
   lit « couts », `coutConstants` « couts_constants »). Même base : 13 929,68 ÷
   4 600 = 3,028 (2,996 à 3,062 pour 4,55 à 4,65). Les « 3,11 » de ma note, du
   commit et du suivi comparaient deux bases d'euros ; **3,03**. La source ne dit
   pas « courants » pour les dépenses d'ASV et d'Aspa (folio 230) : c'est une
   inférence, dite au test. Le complément moyen est repris en courants : 13
   929,68 M€ ÷ 2 800 133 ÷ 12 = 414,5 € par mois (426 en constants) ; l'Aspa,
   527 ; 4 600 M€ ÷ 754 460 ÷ 12 = 508,1 € pour l'ASV et l'Aspa ensemble.
2. **Allocataires ou personnes.** Je compare les deux, et je dis pourquoi.
   754 460 est le nombre des allocataires, ce que la DREES publie au tableau 1
   (G24) et l'unité de l'Aspa (un allocataire par foyer). La garantie est
   individuelle (800 € par personne) : ses bénéficiaires sont des personnes.
   Le folio 226, note 1 : « En tenant compte, en outre, des éventuels conjoints
   de ces allocataires, environ 897 810 personnes bénéficieraient du minimum
   vieillesse, d'après l'enquête sur les bénéficiaires des minima sociaux 2018
   de la Drees (voir fiche 28) » : c'est une estimation de la DREES, tirée
   d'une enquête de 2018, non un dénombrement de 2024. 2 800 133 ÷ 897 810 =
   3,119. Le rapport par personne est celui qui compare l'unité de la garantie ;
   celui par allocataire, 3,71, la seule donnée publiée sans hypothèse. La
   phrase est au témoin (la huitième de `27_texte`), relue au PDF par
   `test_chaque_citation_du_temoin_est_dans_le_pdf`.
3. **Le lapsus.** Confirmé. 22 041,55 × 61,1667 = 1 348 208,9 (1 348 208,1 avec
   61 + 2 ÷ 12 en fraction exacte) ; ma note écrivait 1 348 195,8. La somme
   exacte : 1 348 208,1 + 4 472 435,5 (70 991,04 × 63) = 5 820 643,6 ; ÷ 93 032,59
   = 62,5656 : le résultat, 62,566, ne bouge pas.
4. **« 117 » pour 115.** Mon erreur d'écriture. Les cinq fichiers de tests du
   panorama passent à 115 (`test_controle_drees_panorama.py`, 45 ;
   `test_drees_panorama.py`, `_2024`, `_eic`, `_series`, 70) ; avec
   `test_syntaxe_ancien_python.py`, 2 tests, 117. J'avais remplacé le bon nombre
   par la somme des six fichiers sans le dire. Relancés aujourd'hui, après les
   corrections : 115 et 2.

## 3. La question laissée ouverte : tranchée, et vérifiée

**Le coût de la garantie est brut du minimum vieillesse et des autres minima
qu'elle remplace.** Je l'ai relu moi-même :

- `garantie.py`, `cout_garantie` : `cout_annuel_meur = manque_mensuel ×
  effectif_total × 12 / 1e6`, où le manque d'une tranche est le plancher moins
  la pension ; aucun terme d'ASPA ni d'ASV.
- `cout.py`, `GarantieDistribution.chiffrer` : `cout_constants =
  chiffre.cout_annuel_meur × vers_constants × taux_recours` ; rien n'est
  retranché.
- La page ne retire les minima que dans le tableau « Ce que la garantie
  vieillesse remplace » (`pages.js`, `remplaces`, vers 13324-13349) : quatre
  minima — minimum vieillesse (lu dans les comptes), minimum contributif,
  minimum garanti, minima des exploitants (pension majorée de référence et
  complément différentiel de la RCO) — de `garantieBrute`, « Ce que l'impôt
  paierait en plus ».
- Les valeurs de 2024, `memoire.avantages().derniere` (M€) : minimum vieillesse
  4 941,15 ; minimum contributif 1 563,24 ; minimum garanti 6,66 ; pension
  majorée de référence 349,01 ; complément différentiel de la RCO 636,73 :
  4 941,15 + 1 563,24 + 6,66 + 349,01 + 636,73 = 7 496,79. La garantie en
  courants de 2024 : 13 929,68. Net : 13 929,68 − 7 496,79 = **6 432,89 M€**.
  Le test l'asserte (7 450 < minima < 7 550 ; 6 400 < net < 6 460).

**Ce que je n'ai pas fait.** Je n'ai pas lancé la page : le JavaScript lit les
mêmes minima par `contexte.avantages().derniere`, que je n'ai pas exécuté ; je
lis les valeurs côté Python (`memoire.avantages`), la source de ce tableau. Mon
« 14,3 − 4,8 = 9,5 » est retiré : il retranchait des euros courants de 2024
d'euros constants de 2026 et un seul minimum sur quatre.

**Un écart que personne n'explique.** La page lit 4,94 milliards pour le
minimum vieillesse (les comptes, 2024) ; la DREES, 4,6 (ASV et Aspa) ou 4,8
(premier étage compris). Candidat (d) de R-J3, non traité.

## 4. Ce que j'ai changé

- `tests/test_controle_drees_panorama.py` : le test de la fiche 27, vu rouge
  (le témoin n'avait pas la phrase des 897 810), est récrit et renommé
  `test_la_garantie_de_la_page_sert_plus_de_monde_et_coute_plus_que_l_aspa_et_l_asv`
  (l'ancien nom disait « quatre fois » et « trois fois ») : il dit le facteur,
  les deux comparaisons, les euros, les bornes aux deux planchers à pensions
  servies, et le net des quatre minima ; sa docstring dit sur quelles pensions
  chaque chiffre est calculé.
- `tests/temoins/drees_panorama_2026_confrontations.json` : une phrase de
  citation de plus, 14 en tout, relue au PDF ; aucune ligne retirée.
- `data/reference/drees_panorama_2026.yaml`, fiche 27 : la `confrontation` et
  `confronte_par` suivent le test.
- Mon ancienne note (`2026-11-05-etape-5-fiches-16-27.md`) : le bloc « Reprise »
  à jour et un renvoi daté au bout ; son corps ne change pas.

Vérifié : les cinq fichiers de tests du panorama, 115 passent ; le test de
syntaxe de Python 3.11, 2 ; `python -m pytest -m rapide`, 4 428 passent, dont
aucun rouge hors les 11 de `test_pages_en_dossier.py`, que GitHub refait.
