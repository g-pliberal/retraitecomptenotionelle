# Relecture de J4 : les compléments des fiches 16, 27 et 15

**Verdict : tous les chiffres de la source et tous ceux du modèle sont
conformes ; aucun écart grave, un écart moyen (de déclaration, point 5.1),
cinq faibles (point 7), et une réserve sur l'avis (point 8).** Les 174 cellules et les 20 phrases que J4 ajoute au témoin sont
celles du classeur et du PDF, à la feuille, à la ligne et au folio qu'il écrit ;
tous les écarts qu'il chiffre se retrouvent à la main (27,0 et 31,05 points ;
−1,40 an ; la chaîne 47 930 → 70 386 ; 21 022 décès ; −0,82, −3,2 et −7,22 ;
les douze écarts d'espérance de vie) ; ses six tests tirent leur valeur de la
source, passent, et passent sous `PRESOMPTIONS_DECALEES=1`. Son avis « rien à
changer » au coût et à la population est une position de procédure fondée (la
décision 11 attend le propriétaire, le commit ne touche aucun fichier de
`src/` ni de `scripts/`), non une démonstration que ces écarts sont sans effet
sur le coût : il ne l'a pas mesuré, et le dit sans le dire.

**La demande.** Vague 11, tâche R-J4, le 6 novembre 2026 : revérifier, contre
les sources et sans me fier à J4 ni à ma mémoire, le commit `b0f2854` de la
session `session_01FVFLAmE9pQr7BZzrPUWGnD` et sa note
`2026-11-06-etape-5-complements-16-27-15.md`. Je ne modifie ni règle, ni
donnée, ni test, ni note de J4 ; je n'y ajoute qu'un renvoi d'une ligne.

**Les sources, ouvertes pour cette relecture.** `python
scripts/fetch/source_locale.py --recuperer` a rapporté le PDF (miroir de
l'UNSA, SHA-256 `9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`)
et l'archive des classeurs
(`ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`) ; les deux
empreintes sont celles de la note de J4, que `sha256sum` retrouve. Le PDF :
`pdftotext` page à page, le folio imprimé étant la page du fichier moins un
(vérifié aux pieds de page des folios 139, 140, 143, 144, 146 à 148, 226, 227, 229 et 237). Les classeurs :
`openpyxl` (`data_only`), indépendamment de `lecture_xlsx`, le lecteur de J4.
Le modèle : des scripts à moi (non versés) qui prennent les cohortes de
`controle_eacr.controle()`, les poids de `memoire.cout(...)` et les tables de
`Simulateur(Parametres()).mortalite`, les mêmes appels que les fixtures de J4,
et refont les moyennes, les parts et les distances ; ils ne sont donc pas
indépendants de la grille, seulement de l'arithmétique et des cellules.

## 1. Le témoin, cellule par cellule et phrase par phrase

**Conforme.** J'ai relu avec `openpyxl` les 174 cellules que le commit ajoute
au témoin (812 au total contre 638 avant, aucune perdue) : 0 écart. Les neuf
lignes du graphique 3 de la fiche 16 (`C6:K14`), le complément (ligne 6 : 1,7,
2,5, 5,7, 9,1, 29,1, 25,0, 6,9, 5,0, 15,1 ; ligne 17 = ligne 14, cellule pour
cellule), les cellules `C`, `D`, `N` du tableau 2 complémentaire, `C25:K25` du
graphique 2 de la fiche 15, les graphiques 7 et 5 (lignes 9, 29, 34, 36),
`C69`, `C70` et `H24`, `G24` de la fiche 27, `E18`, `H18`, `I18`, `J18`, `K18`
du tableau 5 de la fiche 28 sont ceux que la note cite.

Les 20 phrases, relues au PDF (espaces et coupures de fin de ligne
normalisés), sont toutes dans le folio que J4 donne : 146 (« environ 4 % ont
moins de »), 148 (« 9 % », « 29 % », « 52 % », l'encadré 1 « l'âge considéré
est celui atteint en fin d'année »), 147 (champ et note du graphique 3), 139
(la génération fictive), 140 (« n'est disponible qu'à compter de 2016 »), 143
(« 24 années et 8 mois », 26 et 5, 22 et 11), 144 (la formule de la durée, la
lecture 1930, la ligne des sources « Insee, projections démographiques au 1er
janvier 2026 »), 226 (« 70 660 »), 227 (« vivants au 31 décembre »), 229 (47 930,
27 700, la chaîne des hausses, « 70 660 personnes entrent ») et 237 (« 77 700 »).

## 2. Fiche 16 : le graphique 3 et le tableau 2 complémentaire

**Conforme.** Refait sur `Cohorte.nouvelle` (16 cas types sur 18 liquident en
2024 : les deux fonctionnaires sédentaires n'ont aucune cohorte, comme J4 le
dit) :

| ligne | têtes | mes parts par tranche (<57 ; 57-59 ; 60 ; 61 ; 62 ; 63-64 ; 65 ; 66 ; >66) | distance | J4 |
|---|---|---|---|---|
| tous régimes | 688 584,8 | 3,46 ; 2,87 ; 13,99 ; 0 ; 35,36 ; 25,74 ; 16,05 ; 0 ; 2,53 | **27,02** | 27,0 (27,1 à la main) |
| régime général | 552 624,9 | 0 ; 0 ; 17,44 ; 0 ; 30,49 ; 32,07 ; 20,00 ; 0 ; 0 | **31,05** | 31,1 |
| MSA non-salariés | 37 174,0 | 100 % à 62 ans | 76,9 | 76,9 |
| FPE civils | 20 945,0 | 38,69 % à 57-59 ; 61,31 % à 62 | 75,7 | 75,7 |
| militaires | 12 298,6 | 100 % avant 57 ans | 19,9 | 19,9 |
| CNRACL | 24 939,3 | 100 % à 62 ans | 71,0 | 71,0 |
| SNCF | 11 506,1 | 100 % avant 57 ans | 77,0 | 77,0 |
| professions libérales | 17 421,8 | 100 % après 66 ans | 64,59 | 64,6 |

Les rapports de la note tiennent : 13,99 ÷ 5,8 = 2,41 et 16,05 ÷ 6,6 = 2,43
(« deux fois et demie »), 2,53 pour 14,9 (« six fois trop peu », 5,9).

Tableau 2 complémentaire, hommes nés en 1953 (têtes de 2024, AOD 61 + 2/12 =
61,1667, lue dans `AgesOuverture`) : régime général 62,569 (publié 61,6 :
**+0,97**), neutralisé 62,828 (62,1 : +0,73) ; FPE civils 61,965 (59,9 : +2,07) et
62,611 (62,2 : +0,41) ; CNRACL 62,289 (61,0 : +1,29) et 62,566 (62,1 : +0,47) ;
régimes spéciaux 52,556 (56,5 : −3,94) et 61,167 (61,3 : −0,13) ; militaires
48,0 (48,8 : −0,80) et 61,167 (61,2 : −0,03) ; MSA non-salariés 61,0 (62,0 :
−1,00) et 61,167 (62,3 : −1,13) ; professions libérales 66,0 (64,7 : +1,30).
**La femme** (carrière interrompue, 81 714,64 têtes) : 61 pour 62,4 (**−1,40**) ;
61,1667 pour 62,5 (−1,33). Part des femmes au régime général de la grille :
16,60 %. Parts parmi les hommes : 61,38 (70,5), 12,78 (8,7), 13,91 (5,3 : 2,6
fois), 2,87 (4,3), 4,91 (3,1), 2,48 (1,8), 1,66 (2,2). Tout est à la note.
L'écart de +0,31 an du régime général au tableau 2 est bien la somme de
62,309 (tous sexes, brut) moins 62,0.

Les défauts de la source : « environ 4 % » (3,3 au graphique 3, 4,2 au
complément, 52 % après 62 ans des deux côtés : 51,6 et 52,0) et la ligne 17
du complément recopiée de la ligne 14 sont **réels**, et le PDF imprimé donne
au graphique 3 « 22 21 11 7 35 » pour les professions libérales, non les
« 23 25 24 10 6 » de la SNCF. J4 les déclare sans trancher lequel des deux
« primo-liquidants » est juste : c'est ce que la source permet.

## 3. Fiche 27 : les 70 660 nouveaux allocataires

**Conforme.** Chaîne : 47 930 × 1,25 = 59 912,5 ; × 1,11 = 66 502,9 ; × 1,05 =
69 828,0 ; × 1,008 = 70 386,6 ; bornes 69 422 et 71 360, 70 660 y est. Stock :
723,0 → 754,0 milliers (+31 000) ; 754 460 ÷ 1,043 = 723 356 ; sorties 70 660 −
31 000 = 39 660 (5,5 %) ; avec les cellules exactes (754 460 − 723 356) 39 556,
dans le bornage du test (39 500 à 39 800). Décès : j'ai refait
`recours_aspa.servis(…, 2023)` (722 520 personnes) et la survie à l'âge du
milieu de chaque tranche : 466, 2 256, 3 065, 2 987, 2 978, 3 762, 5 509, soit
**21 022** (2,9 %) ; 18 831 à un an de moins, 26 426 à deux de plus ; rapport
39 660 ÷ 21 022 = 1,89, borné de 1,5 à 2,1 comme J4 l'écrit. Le fichier des
allocataires est bien celui de l'INSEE (`insee_allocataires_minimum_vieillesse`,
recoupé à la DREES). La garantie de la page : 2 833 509 → 2 800 133 (−1,18 %),
facteur 0,7173 → 0,7365 (+2,67 %), effectif 14,13 → 14,39 millions (+1,85 %,
« 1,9 % » à un chiffre). Aucun champ de `GarantieProjetee` ne porte d'entrants,
et rien dans `src/` ni `scripts/` ne compte de « nouveaux allocataires » : « le
dépôt ne calcule pas ce flux » est exact.

**Le 70 700 contre le 77 700.** Le tableau 5 de la fiche 28 donne
55 700 + 14 900 = 70 700 (K18), quand son texte écrit « 77 700 » (folio 237).
**Une preuve de plus que J4 n'a pas citée** : le même folio dit « près de 80 %
des nouveaux allocataires sont des personnes isolées » ; 55 700 ÷ 70 700 =
78,8 %, mais 55 700 ÷ 77 700 = 71,7 %. Le 77 700 est donc très probablement une
coquille, comme J4 le tient, sans que la source le dise.

Une réserve de forme : J4 écrit « effectifs arrondis à la centaine » ; la
source dit seulement « l'ensemble n'est pas forcément égal à la somme … du fait
des arrondis » (note 2). La centaine se déduit des valeurs (5 000 + 10 000 ≠
14 900), elle n'est pas écrite.

## 4. Fiche 15 : l'âge conjoncturel (graphique 2)

**Conforme.** Poids et premiers âges relus de `memoire.cout` et de
`controle_eacr.controle` (âges contigus de leur premier âge à 104 ans pour les
dix-huit cas types). Régime général 62,7764 (publié 63,6 : **−0,824**) ; FPE
civils 63,1778 (63,18 : −0,002) ; CNIEG 57 (60,2 : −3,2) ; SNCF 52 (59,22 :
−7,22). La formule 50 + Σ(1 − taux) de 50 à 69 ans redonne 62,7764 au régime
général, comme la moyenne pondérée. Les huit produits poids × âge et leur
somme (41,1709) de la note sont justes.

## 5. Fiche 15 : la durée de retraite (graphique 7)

**Conforme pour les chiffres.** Les douze écarts de J4 sont les miens, au
centième près (les miens au millième) : femmes −0,062, −0,194, −0,264, −0,325 ; hommes +0,026, +0,019,
+0,033, −0,047 ; ensemble −0,018, −0,082, −0,110, −0,186 (générations 1930,
1950, 1955, 1957). Les mois du texte : 24,67 → 8,0 ; 26,43 → 5,2 ; 22,94 →
11,3. Les durées de la grille (22,740 pour les hommes de 1950, 22,077 pour
ceux de 1955) sont à la note ; elles reposent sur 61,159 et 62,107 ans.

**5.1. Écart moyen, de déclaration : l'hypothèse de l'inversion n'est pas
dite.** J4 déduit « l'espérance de vie à 60 ans que la source suppose » de
`durée + âge − 60`, « l'âge étant celui du graphique 5 au même rang de
cellule ». La source ne dit pas que l'âge de la formule du graphique 7 est celui
du graphique 5 : sa note précise que l'âge moyen est pris « dans le champ des
personnes vivantes à 66 ans parmi les générations nées en 1950 ou avant, et à
67 ans pour les générations nées en 1951 ou après », clause que la note de J4
**remplace par « (...) »** ; l'âge du graphique 5 est « l'âge atteint à la
liquidation dans le régime principal », sans cette clause. Les hommes, à 0,05
an aux quatre générations, plaident pour l'hypothèse ; les femmes (−0,06 à
−0,33, croissant) peuvent venir de la table de l'INSEE ou de ce champ, ce que
rien ne permet de séparer. La conclusion de J4, « ce n'est pas une erreur du
dépôt », reste raisonnable ; « le dépôt donne 0,06 à 0,33 an de moins que la
formule de la DREES ne le suppose » devrait se lire « que la formule, retournée
avec l'âge du graphique 5, ne le suppose ». Sans effet sur le dépôt.

## 6. Les tests

- `python -m pytest -m rapide` : 4 464 passés, 50 sautés. Avec
  `PRESOMPTIONS_DECALEES=1` : 4 259 passés, 255 sautés. Aucun rouge.
- `tests/test_controle_drees_panorama.py`, `test_drees_panorama.py`,
  `test_drees_panorama_series.py` (87 tests) : tous verts. Les sept tests de J4
  (les six de contrôle et `test_les_fiches_15_16_et_27_nomment_leurs_confrontations`),
  avec `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`,
  `test_chaque_citation_du_temoin_est_dans_le_pdf` et
  `test_chaque_fusion_du_temoin_est_celle_du_classeur`, passent aussi sous
  `PRESOMPTIONS_DECALEES=1`.
- Leurs valeurs publiées viennent du témoin, relu aux cellules (point 1) ; les
  bornes (25 à 29 points, ± 0,15 an, 19 000 à 26 500 décès, −0,25 à +0,05) sont
  des bornes sur l'écart déclaré, autour de mesures que j'ai retrouvées à la
  main (27,02, +0,97…, 21 022, −0,19 au plus) : elles ne cachent aucun écart.

**Un rouge qui n'est pas de J4, à voir.** Sous `PRESOMPTIONS_DECALEES=1`,
`tests/test_controle_drees_panorama.py::test_la_garantie_de_la_page_sert_plus_de_monde_et_coute_plus_que_l_aspa_et_l_asv`
(la file J-bis, du 5 novembre) échoue : `assert 7590.17 < 7550` (la somme des
quatre minima, bornée de 7 450 à 7 550). Il échoue de même, à la même valeur,
sur le parent de J4 (`b0f2854^`, vérifié dans un arbre de travail à part, retiré
ensuite), et J4 ne touche pas ce test. La garde de GitHub ne lance que
`-m rapide` sous cette variable : ce test, du niveau `controle`, n'y passe pas.
Candidat, hors de cette tâche : élargir la borne ou la rendre insensible aux
présomptions.

## 7. Les faibles, et ce que la source ne tranche pas

1. **Arrondis de la dernière décimale** dans la note de J4 : 688 584,9 têtes
   (mes cohortes : 688 584,8) ; 23 804,7 (23 804,6) ; 35,35 % à 62 ans (35,36) ;
   17,43 % (17,44) au régime général à 60 ans. Aucune conséquence.
2. **Deux pointeurs de docstring** : dans le test du graphique 3, « (note 5) »
   pour les résidents à l'étranger : la feuille n'a pas de note 5, c'est la ligne
   « Champ » qui le dit ; dans le test de l'âge conjoncturel, « 62,77 … (−0,83) »
   quand la note et le suivi donnent 62,776 (62,78) et −0,82.
3. **Une cause donnée pour un fait** : la CNRACL pèse 2,6 fois sa part publiée
   chez les hommes « parce que la grille pèse chaque cas type de la population
   entière … et non de la génération 1953 ». Je n'ai pas de quoi le démontrer.
   Tous sexes ensemble, la grille donne 12,40 % à la CNRACL pour 7,4 publiés
   (1,7 fois), 11,39 % aux FPE civils pour 9,1, 65,58 % au régime général pour
   72,9, 4,38 % à la MSA non-salariés pour 2,3, 2,21 % aux professions libérales
   pour 1,4 : le rapport tombe de 2,6 à 1,7 quand les sexes se mêlent, de sorte
   que la répartition par sexe (la CNRACL compte 9,3 % des femmes pour 5,3 %
   des hommes, et ses cas types sont tous des hommes) en est une part ; le reste
   n'est pas expliqué. À dire comme hypothèse.
4. **« De 0 à −0,25 pour les deux sexes »** (note, graphique 7) : −0,25 est la
   borne du test ; la mesure va de −0,02 à −0,19.
5. **« La ligne publiée est celle de tous les cheminots »** (SNCF, graphique 2) :
   la source écrit « SNCF » ; « tous les cheminots » est une lecture.
6. **Ce que la source ne tranche pas** est déclaré, sauf le point 5.1 : le bon
   des deux « primo-liquidants », le 77 700 (« nous tenons … pour une
   coquille ; la source ne le dit pas »), le régime principal du tableau 2, le
   taux de retraités par régime, l'édition des projections, le sens d'« entrant »
   et la population vivante au 31 décembre.

## 8. L'avis « rien à changer » au coût et à la population

**Fondé comme position, non démontré comme absence d'effet.**

- *Fondé* : le commit ne touche ni `src/` ni `scripts/` ni aucune table de
  `data/` (fichiers : le suivi YAML, une entrée de journal, trois notes, le
  témoin, le fichier de tests) ; la décision 11 (la grille du coût) attend la
  réponse du propriétaire, et les notes du 5 novembre (fiches 12, 15, 21, puis 16
  et 27) disent la même chose ; la garantie de la page est un stock, vérifié.
- *Non démontré* : « aucun écart ne touche au coût » (message du commit, point 1
  de « Au propriétaire ») dit que rien n'est corrigé, non que le coût est
  insensible. Les écarts de poids (point 7.3) et d'âge (la grille part à un
  âge entier, un cas type par régime) jouent sur la masse de pensions ; J4 ne
  les chiffre pas, et il n'en avait pas la tâche. Aux fins du dossier à
  « justifier avec preuve à l'écrit », la phrase juste est : *les écarts sont
  déclarés, leur effet sur le coût n'est pas mesuré, la décision 11 attend*.
- Le « quand la population de l'étape 14 de l'action 138 aura les âges de la
  source » renvoie à un chantier réel (`age_conjoncturel_depart.csv`, notes de
  l'étape 14), et à un choix que l'étape 4 soumet déjà.

## 9. Ce que je n'ai pas fait

- Les feuilles que J4 dit n'avoir pas lues (fiche 16 : graphiques 1, 2, 4, 5 et
  5 compl. ; fiche 15 : graphiques 1, 3 et 4 ; fiche 28 : tableaux 1 à 4, carte 1)
  ne sont pas relues non plus.
- Le jeu `drees_minimum_vieillesse` du portail : `curl` vers
  `data.drees.solidarites-sante.gouv.fr` rend « Connection reset by peer » (deux
  essais de moi, un de J4) ; les 70 660 restent lus au PDF, non à la source
  primaire. À ouvrir depuis un poste.
- Les cohortes de la grille ne sont pas recalculées de zéro : j'ai pris
  `controle_eacr.controle()` comme J4 ; ce que j'ai refait est l'arithmétique,
  les cellules, les poids et les tables de mortalité appelés.

Disque : le PDF et l'archive sont dans `data/brut/` (hors dépôt, ignoré) ; les
classeurs extraits dans le brouillon de la session, effacés en finissant.
