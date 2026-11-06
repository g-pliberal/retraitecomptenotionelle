# Étape 5, J4-bis : les écarts de la relecture R-J4, repris aux sources (l'âge du graphique 7, les arrondis, les pointeurs, la CNRACL, le test de la garantie sous les présomptions décalées)

**Reprise, au 6 novembre 2026.** Fait (cette note, qui reprend le bloc de
`2026-11-06-etape-5-complements-16-27-15.md`) : les écarts de R-J4 corrigés
aux sources — l'âge du graphique 7 déclaré hypothèse, ses citations mot pour
mot, les arrondis, les deux pointeurs, la CNRACL dite inférence — et le test de
la garantie de la page rendu indépendant du jour de naissance présumé. Reste à
l'étape 5 : les trois erreurs du coût de la note des règles (3 novembre), qui
attendent le propriétaire, avec l'effet sur le coût des écarts de J4, non
mesuré ; les candidats « Au propriétaire » ; à la clôture (étape 7), fiche 21,
fiche 12, jeu `drees_minimum_vieillesse`. Par quoi commencer : la note des règles.

**La demande.** Vague 11, tâche J4-bis, le 6 novembre 2026 : reprendre, contre
la source, les écarts de `2026-11-06-relecture-r-j4.md` (commit 2adae34) dans
le travail de J4 (commit b0f2854), et le défaut du test de J-bis (commit
7b39260) que l'orchestration a vu sous `PRESOMPTIONS_DECALEES=1`. La note de J4
est un récit : je n'y ajoute qu'un renvoi ; ses chiffres et ses phrases que
cette note corrige restent, dans l'ancienne, tels qu'ils étaient.

**Les sources.** `python scripts/fetch/source_locale.py --recuperer` a rapporté
le PDF (SHA-256 `9eb36a06…735e9be`) et l'archive des classeurs
(`ec7503f8…aaf64911`), que `sha256sum` retrouve, ceux de J4 et de R-J4. Le PDF
par `pdftotext -layout`, page à page : le folio imprimé est la page du fichier
moins un. Les classeurs par `openpyxl` (`data_only`) et par `lecture_xlsx`, le
lecteur du dépôt, que `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`
relit.

## 1. Le graphique 7 : ce que la source dit de l'âge de sa formule

**Ce qu'elle dit, mot pour mot** (feuille « F15_Graphique 7 », cellule B38, qui
porte le bloc Note, Lecture, Champ, Sources de l'encadré du folio 144) :

- Note : « La durée de retraite par génération est calculée comme suit : 60 +
  espérance de vie à 60 ans – âge moyen de départ à la retraite de la
  génération (dans le champ des personnes vivantes à 66 ans parmi les
  générations nées en 1950 ou avant, et à 67 ans pour les générations nées en
  1951 ou après). Le scénario de mortalité retenu est le scénario central des
  projections démographiques de l’Insee de 2021. »
- Champ : « Retraités de droit direct, résidant en France, pondérés pour être
  représentatifs des assurés ayant perçu une pension (pour les générations nées
  en 1953 ou avant) et à 67 ans (pour les générations nées en 1954 ou après). »
- Sources : « Drees, EIR 2020 et modèle ANCETRE ; Insee, projections
  démographiques au 1er janvier 2026. »
- Folio 142, note de bas de page 5 (appelée par « passée à la retraite5 ») :
  « La durée moyenne de retraite par génération est calculée en tenant compte
  de l’espérance de vie à 60 ans par génération, qui s’appuie sur le scénario
  central de mortalité des projections démographiques de l’Insee au 1er janvier
  2026. »

**Ce qu'elle ne dit pas : que cet âge soit celui du graphique 5.** La note
nomme « âge moyen de départ à la retraite de la génération » et lui donne un
champ, « les personnes vivantes à 66 ans [...] à 67 ans », sans renvoyer à aucun
graphique (la cellule B38 n'a pas le mot « graphique », hors « démographiques »). Le
graphique 5 (« F15_Graphique 5 », B38, folio 142) définit le sien autrement :
« Âge atteint à la liquidation de la retraite dans le régime pour lequel la
durée validée est la plus élevée. Cet âge n’est pas nécessairement celui à la
première liquidation. » — sans la clause des vivantes à 66 ou 67 ans. Le
graphique 6 (folio 143) la porte, pour ses séries « par régime » : « âgés de 66
ans (ou de 67 ans pour les générations nées après 1951), vivants au 31 décembre
de l’année des 66 ans (ou des 67 ans pour les générations nées après 1951) » ;
sa ligne « Tous régimes confondus » (note 4 : « l’âge moyen de départ à la
retraite dans le régime principal ») prend, elle, le champ du graphique 5. Trois
seuils de génération pour des champs voisins : 1950/1951 (note du graphique 7),
1953/1954 (champs des graphiques 5 et 7), 1951/1952 (champ du graphique 6) —
la source ne les accorde pas.

**Verdict : une hypothèse, non un fait.** J4 a écrit « l'âge étant celui du
graphique 5 au même rang de cellule » et en a tiré « l'espérance de vie à 60
ans que la source suppose » ; R-J4 a relevé que la source ne le dit pas et que
J4 avait remplacé la clause par « (...) ». C'est exact (point 5.1 de R-J4).
Corrigé : la clause est dans le témoin (`15_texte`), et le test l'asserte mot
pour mot, avec la note 5 du folio 142 et la définition du graphique 5 ; il lit
aussi les deux cellules B38 pour établir que la note du graphique 7 porte
« vivantes à 66 ans » et ne renvoie à aucun graphique, quand celle du graphique
5 n'a pas « vivantes ». La docstring et le suivi disent « impliquerait, si son
âge était celui du graphique 5 (hypothèse du test) ».

**Ce qui plaide pour l'hypothèse, calculé à la main.**

- Les hommes, à 0,05 an près aux quatre générations. Durée + âge − 60 contre
  l'espérance du dépôt (`esperance_residuelle(60, génération + 60, sexe, True)`,
  table de l'INSEE du 1er janvier 2026) : 1930, 21,07 + 59,94 − 60 = 21,01 pour
  21,036 (+0,026) ; 1950, 23,87 + 60,01 − 60 = 23,88 pour 23,899 (+0,019) ;
  1955, 23,00 + 61,15 − 60 = 24,15 pour 24,183 (+0,033) ; 1957, 22,94 + 61,55 −
  60 = 24,49 pour 24,443 (−0,047).
- Le graphique 6, « Tous régimes confondus » (ligne 13, de C13 à T13) et le
  graphique 5, « Ensemble » (colonne E) : les mêmes âges. Sur les 15 générations
  qu'ils ont en commun (1940, 1942, 1944, 1946 à 1957), 13 sont identiques au
  centième, 1956 diffère de 0,01 (61,67 et 61,66) et 1957 de 0,03 (T13 = 61,88,
  E36 = 61,85). Le test asserte 1950 (M13 = 60,46 = E29), 1955 (R13 = 61,59 =
  E34) et 1957. Si la formule prenait le graphique 6 : ensemble 1957, 24,67 +
  61,88 − 60 = 26,55 pour 26,334 (−0,216, contre −0,186) ; les autres, inchangées.

**Ce qui la limite.** Les femmes : 1930, 24,99 + 61,86 − 60 = 26,85 pour 26,788
(−0,062) ; 1950, 27,41 + 60,90 − 60 = 28,31 pour 28,116 (−0,194) ; 1955, 26,36 +
62,00 − 60 = 28,36 pour 28,096 (−0,264) ; 1957, 26,43 + 62,12 − 60 = 28,55 pour
28,225 (−0,325), l'écart croissant. Ensemble : −0,018, −0,082, −0,110, −0,186.
Ces douze écarts sont ceux de J4 et de R-J4, refaits ce jour sur le modèle,
au millième. Deux causes possibles que rien ne sépare : la table (J4 : la note
dit 2021, le dépôt lit 2026) ou l'âge de la clause des vivantes à 66 ou 67 ans.

**Un fait de plus sur la table.** J4 écrit « la source se contredit d'une
édition » (2021 à la note, 2026 aux sources). Elle le dit **deux fois**
2026 — la ligne des sources (folio 144) et la note 5 (folio 142) — et une fois
2021 (la note du graphique). L'explication « la DREES aurait pris la table de
2021 » en est affaiblie : si elle a pris celle que deux phrases sur trois
nomment, celle du dépôt, l'édition n'explique rien. C'est une inférence sur
trois mentions, non une preuve ; la publication de l'INSEE de 2021 n'est
toujours pas lue (J4 le disait déjà).

**Le propos de J4 à reprendre, pour qui cite la note** (la note, un récit, reste
telle) : « pour les femmes, le dépôt donne 0,06 à 0,33 an d'espérance de vie à 60
ans de moins que la formule de la DREES ne le suppose » se lit « que la
formule, retournée avec l'âge du graphique 5, ne l'implique ». Sans effet sur
le dépôt : J4 concluait que ce n'est pas une erreur du dépôt, et rien ici ne le
contredit.

## 2. Les cinq écarts faibles

**Les arrondis**, refaits aux cohortes de la grille à pleine précision
(`controle_eacr.controle()`, `Cohorte.nouvelle`, têtes de 2024) ; J4 avait
additionné des valeurs déjà arrondies à un dixième :

| quantité | note de J4 | calcul à la main | exact |
|---|---|---|---|
| têtes, tous régimes | 688 584,9 | 12 298,562 + 11 506,082 + 11 675,104 + 8 103,598 + 96 351,159 + 243 459,058 + 177 235,129 + 110 534,304 + 17 421,806 | **688 584,8** (688 584,801) |
| moins de 57 ans | 23 804,7 | 12 298,562 + 11 506,082 | **23 804,6** (23 804,644) |
| 62 ans | 243 459,0 | 92 457,619 + 24 939,340 + 37 174,035 + 12 841,397 + 37 318,704 + 38 727,963 | **243 459,1** (243 459,058) |
| 62 ans, part | 35,35 % | 243 459,058 ÷ 688 584,801 = 0,353564 | **35,36 %** |
| 63-64 ans | 177 235,2 | 91 167,676 + 86 067,453 | **177 235,1** (177 235,129) |
| régime général, 60 ans | 17,43 % | 96 351,159 ÷ 552 624,878 = 0,174352 | **17,44 %** |

Les deux lignes « 243 459,0 » et « 177 235,2 » ne sont pas dans R-J4, qui n'en
a relevé que quatre ; les autres valeurs de J4 (3,46 ; 2,87 ; 13,99 ; 25,74 ;
16,05 ; 2,53 ; au régime général 30,49 ; 32,07 ; 20,00 ; les distances 27,0 et
31,1) sont exactes à l'arrondi. Ces chiffres n'étaient que dans la note : ni un
test, ni le suivi, ni le témoin ne les reprend.

**Les deux pointeurs de docstring**, corrigés dans le test.

- « (note 5) », test du graphique 3 de la fiche 16 : la feuille « F16_Graphique
  3 », B16, a deux notes numérotées (1 : « Voir champ de la retraite et de
  l’invalidité (annexe 3 et fiche 24). » ; 2 : « Depuis 2020, le régime général
  comprend également les indépendants de l’ex-SSI. »), puis Note, Lecture, Champ,
  Sources. Les résidents à l'étranger sont dans la ligne **Champ** : « Retraités
  résidant en France ou à l’étranger, ayant acquis un premier droit direct dans
  un régime de base en 2024, vivants au 31 décembre. » (folio 147, qui est la
  page 148 du fichier). La docstring la cite.
- « 62,77 … (−0,83) », test de l'âge conjoncturel : Σ poids × âge ÷ Σ poids =
  41,170915 ÷ 0,655833 = 62,77652 (62,78 ; la note de J4 écrit 62,776) ; publié
  63,6 (F15_Graphique 2, C25) ; 62,77652 − 63,6 = −0,82348, soit −0,82. La
  docstring écrivait une troncature, 62,77, et −0,83.

**La cause du poids de la CNRACL** (« parce que la grille pèse chaque cas type
de la population entière … et non de la génération 1953 »), dite pour un fait
dans la note et dans la docstring de J4. Ce que j'établis, par un calcul que le
test refait (poids de `memoire.cout(...).poids`, têtes de la génération 1953
de la grille) :

- Établi : la part d'un régime dans les têtes de la génération 1953 de la grille
  est celle de ses cas types dans les poids de la population entière, à 10⁻³
  près pour les sept régimes — la CNRACL, 12,40 % dans l'un et l'autre ; l'État
  civil, 11,39 % ; le régime général, 65,58 % ; la MSA non-salariés, 4,38 % ; les
  professions libérales, 2,21 % ; les régimes spéciaux, 2,55 % ; les militaires,
  1,48 %. Tous sexes mêlés, la CNRACL pèse 12,40 % pour 7,4 publiés
  (F16_Tableau 2 compl, N30 : 1,68 fois) ; parmi les hommes, 13,91 % pour 5,3
  (N20 : 2,62 fois).
- Établi aussi : la source compte la CNRACL pour **9,3 % des femmes** (N10) et
  5,3 % des hommes (N20) ; 7,4 % de l'ensemble (N30) correspond, à la main, à
  (7,4 − 5,3) ÷ (9,3 − 5,3) = 0,525 de femmes, sur des parts arrondies ; les cas
  types de la CNRACL (deux, `fonctionnaire_actif` et `fonctionnaire_actif~sedentaire`,
  de poids 0,02937 et 0,09461) sont tous des hommes, et la seule femme de la grille pèse
  10,89 % des têtes de 1953 (81 714,64 sur 750 357,0). La répartition par sexe est
  donc une part de l'écart de 2,6 à 1,7.
- Non établi, **inférence** : que les poids de la population entière soient ce
  qui rend la CNRACL trop lourde. Le reste (de 1,0 à 1,7) n'est pas expliqué ;
  des poids de caisse comptant des polypensionnés, ou une CNRACL plus lourde
  dans la population entière que dans la génération 1953, sont des hypothèses
  que rien ne tranche.

La docstring du test dit désormais ÉTABLI et INFÉRÉ.

**« De 0 à −0,25 pour les deux sexes »** (note de J4, graphique 7) : −0,25 est la
borne du test (`-0.25 < ecart < 0.05`), non une mesure. Ensemble, la mesure va de
−0,018 (1930) à −0,186 (1957). Le test pose maintenant `(min, max) == (−0,19,
−0,02)` sur les arrondis au centième, avec un commentaire qui dit de la borne
qu'elle est une marge. Les hommes vont de −0,047 à +0,033, les femmes de −0,062
à −0,325.

**« Tous les cheminots »** (SNCF, graphique 2), cinquième faible de R-J4 : la
colonne I4 de « F15_Graphique 2 » s'appelle « SNCF » (I25 = 59,22) ; la feuille
ne dit pas qu'elle compte tous les cheminots ni seulement les conducteurs. La
phrase de J4 était une lecture ; aucun test ni suivi ne l'a reprise.

## 3. Le test de J-bis sous `PRESOMPTIONS_DECALEES=1`

**Rouge vu**, sur origin/main 420e22c et ce commit sans mon changement :
`PRESOMPTIONS_DECALEES=1 python -m pytest tests/test_controle_drees_panorama.py
-k la_garantie_de_la_page_sert_plus` →
`assert 7590.172403002169 < 7550` à la ligne `assert 7_450 < minima < 7_550`.

**La présomption.** Les trois que la garde décale (`DECALAGES`, `tests/conftest.py`
et `src/retraite_notionnelle/pont.mjs`, que le portage lit sous la variable) :
`jour_de_naissance` 15 → 1, `naissance_des_enfants` 30 → 27,
`mariage_des_conjoints` 27 → 30. Mesure : le portage décale les trois d'un bloc
sous la variable ; j'ai donc rendu `DECALAGES` de `pont.mjs` pilotable par
l'environnement **le temps de la mesure**, relancé `memoire.avantages()` avec
chaque présomption décalée seule, puis rétabli le fichier par `git checkout --
src/retraite_notionnelle/pont.mjs` (`git status` propre ensuite ; aucune garde
touchée). Millions d'euros courants de 2024, `avantages().derniere.lignes` :

| ligne (page : source) | jeu du vocabulaire (jour 15) | jour de naissance au 1er seul | enfants à 27 seuls | mariage à 30 seul | les trois |
|---|---|---|---|---|---|
| minimum vieillesse (lu dans les comptes) | 4 941,15 | 4 941,15 | 4 941,15 | 4 941,15 | 4 941,15 |
| minimum contributif (calculé sur la grille) | 1 563,24 | 1 568,64 | 1 563,24 | 1 563,24 | 1 568,64 |
| minimum garanti (calculé) | 6,66 | 6,68 | 6,66 | 6,66 | 6,68 |
| pension majorée de référence (calculée) | 349,01 | 396,01 | 349,01 | 349,01 | 396,01 |
| complément différentiel de la RCO (calculé) | 636,73 | 677,68 | 636,73 | 636,73 | 677,68 |
| **somme des cinq** | **7 496,79** | **7 590,17** | 7 496,79 | 7 496,79 | **7 590,17** |

La garantie de la page (`mesures_prose._avenir({"annee": "2024"})`,
`COMPOSANTE_GARANTIE`), sous la garde, les trois présomptions décalées ensemble,
passe de 13 929,68 à 13 912,43 (facteur 0,73648 → 0,73714 ;
bénéficiaires 2 800 133 → 2 796 860) ; ce qu'elle coûte de plus que les minima,
de 13 929,68 − 7 496,79 = 6 432,89 à 13 912,43 − 7 590,17 = 6 322,26. Les
autres bornes du test (rapports aux allocataires et aux dépenses, complément
mensuel) tiennent aux deux jeux, et le fichier entier passe aux deux.

**La cause est le jour de naissance présumé**, seul des trois. Le mécanisme est
**inféré**, non vérifié ligne à ligne : la raison de la présomption, au
vocabulaire (`data/reference/vocabulaire/valeurs.yaml`), dit que la pension prend
effet le premier du mois qui suit l'anniversaire, sauf pour qui est né un 1er
(R. 351-37, circulaire Cnav n° 2026-07) et que présumer un autre jour « déplace
les résultats » ; présumer le 1er avance d'un mois l'effet de chaque nouvelle
pension, ce qui allonge, la première année, ce que les minima paient.

**Le choix.** Aucune source ne publie ces trois lignes calculées : la page les
étiquette « calculé sur la grille » (`pages.js`, `remplaces`). La valeur ne se
tire donc pas d'un texte, et la fourchette n'est pas élargie : le test lit le
jour présumé au vocabulaire, comme `test_nee_toute_l_annee_chaque_cohorte_part_le_mois_que_lui_donne_son_droit`
(`tests/test_cout.py`) lit le sien, et écrit la **mesure de chaque jeu**, à la
même marge qu'avant : jour 15, minima de 7 450 à 7 550 (mesuré 7 496,79),
différence de 6 400 à 6 460 (6 432,89) ; jour 1, de 7 540 à 7 640 (7 590,17) et
de 6 290 à 6 350 (6 322,26). Fixer la présomption dans le test aurait demandé de
défaire la garde côté Python et côté portage : exactement ce qu'elle surveille.
La docstring dit le tout, avec la cause marquée inférence. La garde de GitHub
ne rejoue sous la variable que `-m rapide` ; ce fichier, du niveau `controle`,
n'y passe pas, et le défaut ne rougissait donc aucune suite.

## 4. Un fait de la source, hors de la tâche (candidat)

Le texte du folio 142 dit : « Cet âge atteint ainsi 61 ans et 7 mois pour la
génération 1957, soit 1 an et 1 mois de plus que pour la génération 1950. » Les
deux tableaux publiés donnent 60,46 pour 1950 (E29 du graphique 5, M13 du
graphique 6) et 61,85 (E36) ou 61,88 (T13) pour 1957 : 61 ans et 10 mois, soit
1 an et 5 mois de plus. « 61 ans et 7 mois » (61,58) est la valeur de 1955
(61,59) ; 60,46 + 1 an et 1 mois (1,083) = 61,54 aussi. La Lecture du graphique
5 dit 61,9 pour 1957. Une coquille du texte, ou une valeur d'une autre édition
des données : la source ne le dit pas. **À citer avec précaution**, comme les
trois coquilles de J4 ; non corrigé, non confronté.

## 5. Les tests

Le test d'abord, vu rouge pour la raison attendue :

- `test_la_duree_de_retraite_du_depot_est_celle_de_la_drees_…` : rouge, la
  clause absente du témoin (`AssertionError` à la ligne de l'assertion de la
  clause) ; vert après les cinq phrases de `15_texte` et la cellule T13 du
  graphique 6 (1957) ; un second rouge, mon propre test, sur `graphique` : la
  note du graphique 7 contient « démographiques » (l'assertion cherche le mot
  entier). Les cinq phrases ajoutées au témoin sont relues au PDF par
  `test_chaque_citation_du_temoin_est_dans_le_pdf` ; la cellule, par
  `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`.
- `test_la_garantie_de_la_page_sert_plus_…` : rouge sous la variable (ci-dessus),
  vert sous les deux jeux.
- `test_la_grille_part_a_l_age_des_hommes_…` : l'assertion du mécanisme (les
  parts de la grille sont celles des poids) et celle des cellules N10, N20, N30
  passent du premier coup, étant des faits déjà vrais et non un comportement
  changé ; la cellule N10 est ajoutée au témoin.
- Les corrections de docstring (les deux pointeurs, la cause) ne changent aucun
  comportement.

`python -m pytest tests/test_controle_drees_panorama.py
tests/test_drees_panorama.py tests/test_drees_panorama_series.py` : 87 passés
aux deux jeux de présomptions (le second, 1 min 32). Les autres commandes
du brief sont notées au compte rendu.

*Renvoi daté : la relecture R-J4 est dans `2026-11-06-relecture-r-j4.md`, et la
note de J4, `2026-11-06-etape-5-complements-16-27-15.md`, reste telle ;
ses chiffres corrigés ici sont ceux des points 1 et 2.*
