# Étape 5, les compléments des fiches 16, 27 et 15 : le graphique 3 et le tableau 2 complémentaire, les 70 660 nouveaux allocataires, les graphiques 2 et 7, confrontés au dépôt

**Reprise, au 6 novembre 2026.** Fait (cette note, qui reprend les blocs de
`2026-11-05-etape-5-fiches-12-15-21.md` et de `2026-11-05-etape-5-fiches-16-27.md`) :
les fiches 16 (graphique 3, tableau 2 complémentaire), 27 (les 70 660 nouveaux
allocataires) et 15 (graphiques 2 et 7), confrontées par six tests du niveau
`controle` ; au suivi, elles restent `confronte`. Reste à l'étape 5 : les trois
erreurs du coût de la note des règles (3 novembre), qui attendent le propriétaire,
et les candidats « Au propriétaire » de ces notes. Pour la clôture (étape 7) :
fiche 21 (tableau 3, graphique 2, encadré 2), fiche 12 (feuilles de l'édition
précédente), jeu `drees_minimum_vieillesse` du portail (fiche 27 ; non joint
depuis le nuage). Par quoi commencer : la note des règles. Détail : plus bas.

**La demande.** Vague 11, tâche J4, le 6 novembre 2026 : les trois compléments
que les notes `2026-11-05-etape-5-fiches-16-27.md` (corrigée par
`2026-11-05-j-bis-corrections-de-r-j3.md`) et `2026-11-05-etape-5-fiches-12-15-21.md`
laissaient — le graphique 3 et le tableau 2 complémentaire de la fiche 16, les
70 660 nouveaux allocataires de la fiche 27, les graphiques 2 et 7 de la fiche
15 —, chacun avec sa cellule ou sa phrase citée, confronté à ce que le dépôt en
tire par un test du niveau `controle` dont la valeur attendue vient de la
source. Un écart se déclare ; aucun n'est corrigé, et aucun ne touche au coût
(`cout.py`) ni à la population (`donnees/population.py`).

**Les sources, ouvertes le 6 novembre 2026.** `python scripts/fetch/source_locale.py
--recuperer` a rapporté le PDF du miroir de l'UNSA (SHA-256 `9eb36a06…735e9be`) et
l'archive des classeurs (`ec7503f8…aaf64911`), tous deux ceux du manifeste, que
`sha256sum` retrouve. Le PDF, par `pdftotext -layout` page à page : le folio
imprimé est la page du fichier moins un. Les classeurs, par `lecture_xlsx`, le
lecteur du dépôt, que `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`
relit au bit près. Chaque valeur écrite plus bas est relue à la cellule ou à la
page, aucune de mémoire ; ce qui n'a pas été lu est dit à la fin.

## 1. Fiche 16, le graphique 3 et ses compléments

**Ce que la source donne.** « F16_Graphique 3 » (EACR 2024), folio 147,
« Répartition des nouveaux retraités de 2024, selon leur âge au 31 décembre »,
en %, neuf tranches en colonnes C à K (moins de 57 ans, 57 à 59, 60, 61, 62,
63 à 64, 65, 66, plus de 66) et neuf lignes de régime, de 6 à 14. L'âge est
« celui atteint en fin d'année » (folio 148, encadré 1), l'âge de liquidation
de la grille (année de la liquidation moins année de naissance). Lignes
publiées, en % :

| ligne | <57 | 57-59 | 60 | 61 | 62 | 63-64 | 65 | 66 | >66 |
|---|---|---|---|---|---|---|---|---|---|
| tous régimes (C6 à K6) | 1,6 | 1,7 | 5,8 | 9,3 | 29,3 | 25,1 | 6,6 | 5,0 | 14,9 |
| régime général (7) | 0,1 | 0,2 | 5,5 | 9,6 | 28,5 | 27,8 | 7,2 | 4,5 | 16,7 |
| MSA non-salariés (9) | 0,0 | 0,1 | 3,4 | 11,2 | 23,0 | 25,4 | 6,6 | 4,9 | 25,2 |
| FPE civils (10) | 2,2 | 6,8 | 4,1 | 8,0 | 17,5 | 35,3 | 8,9 | 5,7 | 11,5 |
| FPE militaires (11) | 80,1 | 16,8 | 0,5 | 0,2 | 0,6 | 0,1 | 0,0 | 0,1 | 1,6 |
| CNRACL (12) | 0,2 | 5,2 | 6,4 | 9,9 | 29,0 | 30,9 | 6,7 | 3,9 | 7,8 |
| SNCF (13) | 23,0 | 25,3 | 24,2 | 10,3 | 5,7 | 8,2 | 2,1 | 1,1 | 0,1 |
| CNAVPL (14) | 0,0 | 0,04 | 1,58 | 1,29 | 22,39 | 21,28 | 11,27 | 6,73 | 35,41 |

La ligne 8 (MSA salariés) est au témoin ; la grille n'a pas de cas type de ce
régime. Le texte (folio 146) : « parmi les primo-liquidants d'un droit direct,
environ 4 % ont moins de [60 ans] » ; (folio 148) « 9 % ont liquidé un premier
droit au cours de l'année de leurs 61 ans, 29 % l'ont fait l'année de leurs 62
ans et plus de la moitié (52 %) après cet âge ». Champ de la feuille :
« Retraités résidant en France ou à l'étranger, ayant acquis un premier droit
direct dans un régime de base en 2024, vivants au 31 décembre ».

**La mesure.** Les nouveaux retraités de 2024 de la grille, `Cohorte.nouvelle`
(`controle_eacr.controle`, la mesure de la fiche 18 et de `test_controle_eacr.py`),
à leurs têtes de 2024. Le calcul posé à la main, tous régimes (688 584,9 têtes) :
moins de 57 ans, militaire 12 298,6 + SNCF 11 506,1 = 23 804,7 (3,46 %) ; 57 à 59,
agent des IEG 11 675,1 + fonctionnaire super-actif 8 103,6 = 19 778,7 (2,87 %) ;
60 ans, le Smic 96 351,2 (13,99 %) ; 62 ans, carrière interrompue 92 457,6 +
exploitant 37 174,0 + CNRACL actif 24 939,3 + État civil actif 12 841,4 + inapte
37 318,7 + ex-invalide 38 728,0 = 243 459,0 (35,35 %) ; 63-64, salaire moyen
91 167,7 + cadre 86 067,5 = 177 235,2 (25,74 %) ; 65 ans, artisan 40 444,6 +
contractuel 70 089,7 = 110 534,3 (16,05 %) ; plus de 66, le libéral à 67 ans
17 421,8 (2,53 %) ; 61 et 66 ans, rien. Régime général (552 624,9) : 60 ans
17,43 %, 62 ans (168 504,3) 30,49 %, 63-64 32,07 %, 65 ans 20,00 %.

La distance entre deux répartitions est la moitié de la somme des écarts, par
tranche, en points. Tous régimes : ½ (1,9 + 1,2 + 8,2 + 9,3 + 6,1 + 0,6 + 9,5 +
5,0 + 12,4) = 27,1 (27,0 au calcul complet). Régime général : ½ (0,1 + 0,2 +
11,9 + 9,6 + 2,0 + 4,3 + 12,8 + 4,5 + 16,7) = 31,1. Un régime dont toute la ligne
est dans une tranche a pour distance 100 moins la part publiée de cette tranche
(la somme des autres parts publiées est ce complément) : SNCF 100 − 23,0 = 77,0 (le
conducteur, 52 ans) ; MSA non-salariés 100 − 23,0 = 77,0 (76,9, la ligne somme 99,8) ;
CNRACL 100 − 29,0 = 71,0 (62 ans) ; professions libérales 100 − 35,41 = 64,6
(67 ans) ; militaires 100 − 80,1 = 19,9 (48 ans). L'État civil tient deux
tranches, 57-59 ans (38,7 %) et 62 ans (61,3 %) : ½ (2,2 + 31,9 + 4,1 + 8,0 +
43,8 + 35,3 + 8,9 + 5,7 + 11,5) = 75,7.

**Ce que cela dit.** La grille ne fait partir personne à 61 ni à 66 ans (la
source en compte 9,3 et 5,0 %), deux fois et demie trop à 60 ans (14,0 pour
5,8) et à 65 ans (16,1 pour 6,6), six fois trop peu après 66 ans (2,5 pour
14,9). Chaque régime autre que le général n'y a qu'un âge de départ, ou deux :
c'est la grille, un cas type par régime. Réserve de la mesure : la grille compte
des cohortes de cinq générations, et deux de ses dix-huit cas types, le
fonctionnaire sédentaire de l'État civil et sa variante active de la CNRACL,
n'ont aucune cohorte qui liquide en 2024 (celle de 1960 part en 2023, la suivante
en 2025, au pas de l'âge d'ouverture) : l'instantané d'une année est irrégulier,
d'où les « 100 % à 62 ans » de la CNRACL, et la mesure lissée est l'âge
conjoncturel (section 3). Le test (`test_la_grille_met_chaque_regime_de_2024_a_un_ou_deux_ages_quand_la_source_les_etale`)
le dit et le borne : 25 à 29 points tous régimes, 29 à 33 au régime général.

**Les deux défauts de la source.** (1) Le graphique 3 donne 1,6 + 1,7 = 3,3 %
avant 60 ans ; son complément, « F16_Graphique 3 compl » (ligne 6), 1,7 + 2,5 =
4,2 ; le texte dit « environ 4 % ». Ils s'accordent sur le reste : 5,8 et 5,7 %
à 60 ans, 9,3 et 9,1 à 61, 29,3 et 29,1 à 62, 25,1 + 6,6 + 5,0 + 14,9 = 51,6 et
25,0 + 6,9 + 5,0 + 15,1 = 52,0 après 62 ans, soit 52 % de part et d'autre. La
source ne dit pas lequel des deux est juste ; les tests lisent le graphique 3,
celui de la page imprimée (ses étiquettes arrondies, « 2 2 6 9 29 25 7 5 15 »,
sont les siennes). (2) Au complément, la ligne des professions libérales (17)
est celle de la SNCF (14) cellule pour cellule : 23,0, 25,3, 24,2, 10,3, 5,7, 8,2,
2,1, 1,1, 0,1 ; au graphique 3, les professions libérales sont à 0, 0,04, 1,58,
1,29, 22,39, 21,28, 11,27, 6,73, 35,41 (« 22 21 11 7 35 » sur la page imprimée,
lue au `pdftotext -layout`). Une ligne recopiée à tort. Test :
`test_le_graphique_3_complementaire_repete_la_sncf_pour_la_cnavpl_et_la_source_dit_4_pour_cent_de_moins_de_60_ans`.

**Le tableau 2 complémentaire** (« F16_Tableau 2 compl », EIR 2020, nés en 1953
résidant en France) est le tableau 2 par sexe : colonnes C (âge moyen), D (après
neutralisation des départs avant l'AOD, 61 ans et 2 mois) et N (part du régime
parmi les retraités du sexe). Cellules lues : femmes, régime général C7 = 62,4,
D7 = 62,5, N7 = 75,1 ; hommes, régime général C16 = 61,6, D16 = 62,1, N16 =
70,5 ; FPE civils C18 = 59,9, D18 = 62,2, N18 = 8,7 ; FPE militaires C19 = 48,8,
D19 = 61,2, N19 = 2,2 ; CNRACL C20 = 61,0, D20 = 62,1, N20 = 5,3 ; régimes
spéciaux C21 = 56,5, D21 = 61,3, N21 = 4,3 ; MSA non-salariés C22 = 62,0, D22 =
62,3, N22 = 3,1 ; CNAVPL C23 = 64,7, D23 = 64,7, N23 = 1,8 ; plus les lignes
« Femmes » (C6 = 61,8, D6 = 62,4) et « Hommes » (C15 = 61,0, D15 = 62,1). Le
bloc « Ensemble » du complément (lignes 25 à 34) redonne le tableau 2 (C26 =
62,0, C28 = 60,0, C30 = 59,8, C25 = 61,4), que la note du 5 novembre a lu.

*La mesure et le calcul posé à la main.* Les cas types nés en 1953 (têtes de
2024, hommes 668 642,36, femme 81 714,64), l'AOD de 61 + 2 ÷ 12 = 61,1667.
Hommes du régime général (410 394,18 têtes : Smic 60 ans 81 415,76 ; inapte 61,
32 982,51 ; ex-invalide 61, 34 228,02 ; salaire moyen 62, 81 333,30 ; cadre 64,
77 716,68 ; artisan 65, 37 584,60 ; contractuel 65, 65 133,31) :
Σ âge × têtes = 25 677 983,2 ; ÷ 410 394,18 = 62,569 ; publié 61,6 : +0,97.
Neutralisé : on ajoute 1,1667 × 81 415,76 = 94 985,1 et 0,1667 × 67 210,53 =
11 201,8, soit 25 784 170,1 ÷ 410 394,18 = 62,827 ; publié 62,1 : +0,73. État
civil (85 477,82) : (63 × 67 330,81 + 60 × 11 349,31 + 55 × 6 797,70) ÷ 85 477,82 =
5 296 673,1 ÷ 85 477,82 = 61,965 ; publié 59,9 : +2,07 ; neutralisé (4 241 841,0 +
18 147,01 × 61,1667) ÷ 85 477,82 = 62,611 ; publié 62,2 : +0,41. CNRACL (93
032,59) : (60 × 22 041,55 + 63 × 70 991,04) ÷ 93 032,59 = 5 794 928,5 ÷ 93 032,59 =
62,289 ; publié 61,0 : +1,29 ; neutralisé 62,566 (le calcul de la note du 5
novembre) ; publié 62,1 : +0,47. Régimes spéciaux (19 158,53) : (50 × 9 364,87 + 55 ×
9 793,66) ÷ 19 158,53 = 52,556 ; publié 56,5 : −3,94 ; neutralisé 61,1667 ; publié
61,3 : −0,13. Militaires : 48 pour 48,8 : −0,80 ; neutralisé 61,1667 pour 61,2 :
−0,03. MSA non-salariés : 61 pour 62,0 : −1,00 ; neutralisé 61,1667 pour 62,3 :
−1,13. Professions libérales : 66 pour 64,7 : +1,30. La femme, la carrière
interrompue : 61 pour 62,4 : −1,40 ; neutralisé 61,1667 pour 62,5 : −1,33. Parts
parmi les hommes : régime général 410 394,2 ÷ 668 642,4 = 61,38 % (70,5 publiés),
État civil 12,78 (8,7), CNRACL 13,91 (5,3 : 2,6 fois), régimes spéciaux 2,87
(4,3), MSA non-salariés 4,91 (3,1), professions libérales 2,48 (1,8), militaires
1,66 (2,2).

*Ce que cela dit.* L'écart de +0,31 an du régime général au tableau 2 est la somme
d'écarts de signe contraire : les hommes de la grille partent trop tard (+0,97),
sa seule femme trop tôt (−1,40), et la grille n'a que 16,6 % de femmes au régime
général (81 714,64 ÷ 492 108,83). Aux fonctions publiques, la grille part
aussi trop tard (+2,07 à l'État civil, +1,29 à la CNRACL), pour la raison de la
note du 5 novembre : ses fonctionnaires partent à l'âge de leurs collègues
sédentaires. Aux régimes spéciaux, aux militaires et à la MSA non-salariés elle
part trop tôt ; neutralisés, les régimes spéciaux (−0,13) et les militaires
(−0,03) s'accordent à la source. La CNRACL pèse 2,6 fois sa part publiée chez les
hommes, parce que la grille pèse chaque cas type de la population entière, par
ses têtes de caisse, et non de la génération 1953. Le test
(`test_la_grille_part_a_l_age_des_hommes_de_chaque_regime_et_de_sa_seule_femme_et_les_pese_autrement`)
borne chaque écart à ± 0,15 an de la mesure.

*Ce que la source ne tranche pas.* Le régime principal est celui qui représente
plus de la moitié de la carrière (note du tableau), non la caisse du dernier
départ ; la grille n'a aucun polypensionné. Le complément ne donne pas, pour les
femmes, les lignes de l'État civil, de la CNRACL ni des régimes spéciaux que la
grille n'a pas : seul le régime général de la femme est confronté.

## 2. Fiche 27, les 70 660 nouveaux allocataires

**Ce que la source donne.** Le chiffre n'est pas au classeur de la fiche 27 ; il
est au texte. Folio 226 : « Le nombre de nouveaux allocataires augmente
légèrement en 2024 (+0,8 %) pour atteindre 70 660 ». Folio 229 : « En 2024, 70 660
personnes entrent dans le dispositif », après « Entre 2015 et 2017, le nombre de
nouveaux allocataires est resté stable à environ 27 700 individus par an »,
« pour atteindre 47 930 individus en 2020 » et « La hausse se poursuit en 2021 (+25
%), puis dans une moindre mesure les années suivantes (+11 % en 2022, +5 % en 2023
et +0,8 % en 2024) ». Folio 227, encadré 1 : les données « permettent de décrire
la population des bénéficiaires des allocations du minimum vieillesse vivants au
31 décembre de chaque année ». Le stock : « F27_Graphique 1 », C69 = 723,0 (2023)
et C70 = 754,0 (2024), en milliers ; « F27_Tableau 1 », H24 = 4,3 (évolution
2023-2024, %), G24 = 754 460.

**Le recoupement par la fiche 28.** « F28_Tableau 5 », folio 237, « Répartition
par tranche d'âge des nouveaux allocataires de l'Aspa, selon le sexe et la
situation conjugale, fin 2024 », ligne « Effectifs » (18) : personnes seules E18 =
55 700, en couple H18 = 14 900, femmes I18 = 39 000, hommes J18 = 31 600,
**ensemble K18 = 70 700** ; champ « Nouveaux allocataires du minimum vieillesse
dans le champ de l'enquête (voir fiche 26) », effectifs arrondis à la centaine.
70 700 est 70 660 à l'arrondi. **Mais le texte de la même fiche 28, folio 237, écrit
« Parmi les 77 700 nouveaux allocataires de l'Aspa en 2024, 35 % ont moins de 65
ans »** : 7 000 de plus que son tableau (77 700 − 70 700) et que la fiche 27. Les
35 % sont ceux de K6 (34,67). Nous tenons 77 700 pour une coquille ; la source ne le
dit pas.

**Le calcul posé à la main.**

- *La chaîne des hausses.* 47 930 × 1,25 = 59 912,5 ; × 1,11 = 66 502,9 ; × 1,05 =
  69 828,0 ; × 1,008 = 70 386,6. Les taux sont arrondis à l'unité (± 0,5 point) et
  le dernier au dixième (± 0,05) : au plus bas, 47 930 × 1,245 × 1,105 × 1,045 ×
  1,0075 = 69 422 ; au plus haut, 47 930 × 1,255 × 1,115 × 1,055 × 1,0085 = 71 360.
  70 660 y est. Le chiffre est cohérent avec la chaîne du texte.
- *Les sorties.* Le stock passe de 723 000 à 754 000 : +31 000, soit +4,3 % (754 460
  ÷ 1,043 = 723 356, à 356 de 723 000, dans l'arrondi des deux). Les entrées étant
  70 660, les sorties de l'année sont 70 660 − 31 000 = 39 660, soit 5,5 % du stock
  de fin 2023.
- *Les décès que les tables du dépôt donnent à ce stock.* Les allocataires de fin
  2023 par âge et par sexe sont ceux de l'INSEE (`allocataires_minimum_vieillesse.csv`,
  722 520 personnes, à 480 des 723,0 milliers du graphique 1 ; le total de 2024 est
  celui que `test_recours_aspa.py` recoupe à la DREES).
  Probabilité de décéder dans l'année, `DonneesMortalite.survie(âge, 2024, 1, sexe)`,
  table de génération, à l'âge du milieu de la tranche. Décès par tranche, deux
  sexes ensemble : 61-64 ans 466 (61 680 allocataires) ; 65-69, 2 256 (200 910) ;
  70-74, 3 065 (189 140) ; 75-79, 2 987 (119 720) ; 80-84, 2 978 (68 250) ; 85-89,
  3 762 (46 340) ; 90 ans ou plus, 5 509 (36 480) : 21 022, 2,9 % du stock. Si les
  âges moyens des tranches étaient plus bas d'un an ou plus hauts de deux, 18 831 et
  26 426 : le test borne de 19 000 à 26 500.

**Ce que cela dit.** Les sorties de 2024 sont 1,5 à 2,1 fois les décès que les
tables du dépôt donnent à ce stock (39 660 ÷ 21 022 = 1,89). La source ne distingue
pas la part de l'excès de mortalité des allocataires sur la population de leur âge
(ils sont pauvres), la part des sorties autres que le décès (perte du droit,
entrée dans un autre dispositif, changement de caisse), ni ce qu'est un entrant
— première entrée, retour, changement de caisse. Elle ne tranche pas non plus si
les « personnes qui entrent » sont comptées vivantes au 31 décembre, comme le
stock : les sorties ci-dessus supposent que oui.

**Ce que le dépôt ne calcule pas.** La garantie de la page est un stock, aucun de
ses champs ne compte des entrants : il n'y a rien à confronter aux 70 660, et rien
n'est corrigé. Son stock de bénéficiaires recule de 2 833 509 (2023) à 2 800 133
(2024), −1,2 %, quand celui de l'ASV et de l'Aspa avance de 4,3 % (`mesures_prose._avenir`,
le facteur des pensions du système 4 passe de 0,7173 à 0,7365, plus vite que
l'effectif, de 14,13 à 14,39 millions, +1,9 %). La source donne pour l'Aspa les
revalorisations exceptionnelles de 2018 à 2020 (folio 226) ; la garantie, qui n'a pas
de plafond de ressources, n'en a pas l'équivalent. Ce n'est pas un écart du modèle :
la garantie n'est pas l'Aspa.

**Ce que je n'ai pas pu faire.** Le jeu `drees_minimum_vieillesse` du portail de la
DREES (`data/sources_a_explorer.yaml`), dix-huit classeurs de l'enquête, qui
porteraient les entrants par âge, par sexe et par caisse : `curl` vers
`data.drees.solidarites-sante.gouv.fr` a rendu « Connection reset by peer »
(un essai, non répété) ; le jeu est à ouvrir depuis un poste. Les 70 660 sont donc
lus à deux endroits du panorama (textes et tableau 5), non à la source primaire de
l'enquête. Le tableau 5 de la fiche 28 donne aussi l'âge des entrants (24,09 % à
62 ans, 17,98 % à 65 ans, 34,67 % avant 65 ans : K15, K16, K6), que le dépôt ne
confronte pas.

## 3. Fiche 15, les graphiques 2 et 7

**Graphique 2, l'âge conjoncturel par régime.** « F15_Graphique 2 », ligne 25
(2024), folio 140 : régime général C25 = 63,6 ; Agirc-Arrco F25 = 63,43 ; FPE civils
G25 = 63,18 ; CNIEG H25 = 60,2 ; SNCF I25 = 59,22 ; RATP J25 = 56,89 ; Banque de
France K25 = 61,64. Encadré 1 (folio 139) : l'âge conjoncturel de départ est « égal à
l'âge moyen de départ d'une génération fictive qui aurait, à chaque âge fin entre
50 et 70 ans, la même probabilité d'être à la retraite que les générations ayant
atteint ces âges au cours de l'année d'observation ». Note 2 : « Cet âge n'est
disponible qu'à compter de 2016 » pour les fonctionnaires civils de l'État.

*La mesure.* Le taux de retraités à l'âge a est, pour un régime, la part de ses cas
types dont la cohorte de cet âge est déjà partie en 2024 ; l'âge conjoncturel est
50 + Σ(1 − taux) de 50 à 69 ans, c'est-à-dire la moyenne, pesée du poids de chaque
cas type (`memoire.cout(...).poids`), du plus jeune âge où sa cohorte est retraitée
(`Cohorte.age` minimal des cohortes déjà parties de `controle_eacr.controle`). Le test
vérifie que les âges de chaque cas type se suivent sans trou jusqu'à 69 ans au
moins. Régime général : Smic 60 (poids 0,108503) ; carrière interrompue 62
(0,108901), inapte 62 (0,043956), ex-invalide 62 (0,045616) ; salaire moyen 63
(0,108393) ; cadre 64 (0,103573) ; artisan 65 (0,050089) ; contractuel 65 (0,086803) :
Σ poids = 0,655833 ; Σ poids × âge = 6,51018 + 6,751862 + 2,725272 + 2,828192 +
6,828759 + 6,628672 + 3,255785 + 5,642195 = 41,170915 ; ÷ 0,655833 = 62,776 ; publié
63,6 : −0,82. État civil : sédentaire 64 (0,089732), sédentaire~actif 62 (0,015125),
super-actif 57 (0,009059) : 5,742848 + 0,93775 + 0,516363 = 7,196961 ÷ 0,113916 =
63,178 ; publié 63,18 : −0,00. CNIEG : l'agent des IEG, 57 ; publié 60,2 : −3,2.
SNCF : le conducteur, 52 ; publié 59,22 : −7,22.

*Ce que cela dit.* Le régime général de la grille est un peu plus jeune que la source
(−0,82), la CNIEG et la SNCF beaucoup (le cas type de la SNCF est le conducteur, parti
à 52 ans, quand la ligne publiée est celle de tous les cheminots). L'accord de
l'État civil (63,178 pour 63,18) est numérique, non une preuve : la grille y mêle un
sédentaire à 64, un actif à 62 et un super-actif à 57 pour tomber, par les poids, sur
la valeur publiée. La grille n'a pas de cas type pour l'Agirc-Arrco, la RATP ni la
Banque de France. *Ce que la source ne tranche pas* : si le taux de retraités d'un
régime est celui de ses assurés ou de la population de l'âge ; ni comment elle
traite les polypensionnés, qui comptent dans plusieurs régimes. Test :
`test_l_age_conjoncturel_de_la_grille_est_celui_de_ses_cas_types_au_premier_age_ou_leur_cohorte_est_retraitee`.

**Graphique 7, l'espérance de durée de retraite.** « F15_Graphique 7 », folio 144,
par génération, femmes C, hommes D, ensemble E : 1930 (ligne 9) 24,99, 21,07,
23,02 ; 1950 (29) 27,41, 23,87, 25,63 ; 1955 (34) 26,36, 23,00, 24,66 ; 1957 (36)
26,43, 22,94, 24,67. La note : « La durée de retraite par génération est calculée
comme suit : 60 + espérance de vie à 60 ans − âge moyen de départ à la retraite de
la génération (...). Le scénario de mortalité retenu est le scénario central des
projections démographiques de l'Insee de 2021 », quand la ligne des sources écrit
« Insee, projections démographiques au 1er janvier 2026 » : la source se contredit
d'une édition. La lecture : « 23,0 années pour la génération née en 1930 (25,0
années pour les femmes et 21,1 années pour les hommes) », que les cellules
retrouvent à l'arrondi ; le texte (folio 143), « 24 années et 8 mois » pour la
génération 1957, « 26 années et 5 mois » pour les femmes, « 22 années et 11 mois »
pour les hommes, que 24,67 (0,67 × 12 = 8,0 mois), 26,43 (0,43 × 12 = 5,2) et 22,94
(0,94 × 12 = 11,3) retrouvent.

*La mesure.* La formule de la source se retourne : l'espérance de vie à 60 ans
qu'elle suppose est durée + âge moyen de départ − 60, l'âge étant celui du
graphique 5 au même rang de cellule (« F15_Graphique 5 », C femmes, D hommes, E
ensemble, lignes 9, 29, 34, 36). Celle du dépôt est la table de génération de ses
projections de l'INSEE (2026), `DonneesMortalite.esperance_residuelle(60,
génération + 60, sexe)`. Posé à la main :

| génération | sexe | durée (G7) + âge (G5) − 60 | dépôt | dépôt − source |
|---|---|---|---|---|
| 1930 | femmes | 24,99 + 61,86 − 60 = 26,85 | 26,788 | −0,06 |
| 1930 | hommes | 21,07 + 59,94 − 60 = 21,01 | 21,036 | +0,03 |
| 1930 | ensemble | 23,02 + 60,91 − 60 = 23,93 | 23,912 | −0,02 |
| 1950 | femmes | 27,41 + 60,90 − 60 = 28,31 | 28,116 | −0,19 |
| 1950 | hommes | 23,87 + 60,01 − 60 = 23,88 | 23,899 | +0,02 |
| 1950 | ensemble | 25,63 + 60,46 − 60 = 26,09 | 26,008 | −0,08 |
| 1955 | femmes | 26,36 + 62,00 − 60 = 28,36 | 28,096 | −0,26 |
| 1955 | hommes | 23,00 + 61,15 − 60 = 24,15 | 24,183 | +0,03 |
| 1955 | ensemble | 24,66 + 61,59 − 60 = 26,25 | 26,140 | −0,11 |
| 1957 | femmes | 26,43 + 62,12 − 60 = 28,55 | 28,225 | −0,33 |
| 1957 | hommes | 22,94 + 61,55 − 60 = 24,49 | 24,443 | −0,05 |
| 1957 | ensemble | 24,67 + 61,85 − 60 = 26,52 | 26,334 | −0,19 |

*Ce que cela dit.* L'espérance de vie à 60 ans du dépôt est celle de la source à 0,1
an près pour les hommes aux quatre générations, de 0 à −0,25 pour les deux sexes ;
plus basse pour les femmes, de plus en plus (−0,06, −0,19, −0,26, −0,33). Je n'ai
pas de quoi dire si c'est l'édition des projections (la note de la source dit 2021,
le dépôt lit celle de 2026) ou autre chose ; ce n'est pas une erreur du dépôt, dont
les espérances sont contrôlées aux espérances que l'INSEE publie
(`scripts/fetch/insee_projections_mortalite.py`). La grille, elle, a une durée de
retraite plus courte, parce qu'elle part plus tard : les hommes nés en 1950 partent
à 61,159 ans (têtes 651 256,13), la source à 60,01 (graphique 5) ; la durée de la
grille est 23,899 − (61,159 − 60) = 22,740, la source 23,87 : −1,13 an, dont
l'espérance de vie ne compte que +0,02 et l'âge de départ −1,15. Nés en 1955 : 62,107
(682 020,43 têtes) pour 61,15, 24,183 − 2,107 = 22,077 pour 23,00 : −0,92. La seule
femme (carrière interrompue, 79 589,87 et 83 349,57 têtes) part à 60 puis à 62
ans, pour 60,9 et 62,0 : 28,116 − 0 = 28,116 pour 27,41 (+0,71) ; 28,096 − 2 =
26,096 pour 26,36 (−0,26). Test :
`test_la_duree_de_retraite_du_depot_est_celle_de_la_drees_a_quelques_dixiemes_pres_et_la_grille_part_trop_tard`.

## Au propriétaire

1. **Rien qui touche au coût ni à la population.** Les écarts relevés sont ceux
   des cas types, comme aux fiches 7, 8, 12, 15, 16, 18 et 21 : la grille part à un
   âge entier par cas type, un cas type par régime, quand la population de
   l'étape 14 de l'action 138 aura les âges de la source. Mon avis : rien à changer
   (décision 11).
2. **Un écart de mortalité à regarder, sans urgence.** Pour les femmes, le dépôt
   donne 0,06 à 0,33 an d'espérance de vie à 60 ans de moins que la formule de la
   DREES ne le suppose (générations 1930 à 1957). Mon avis : ce n'est pas une erreur,
   les tables du dépôt sont celles de l'INSEE ; la note de la DREES dit 2021, sa ligne
   de sources 2026. Je n'ai pas lu la publication de l'INSEE de 2021 : à vérifier si
   la durée de retraite des femmes entre dans une page.
3. **Trois coquilles de la source, à citer avec précaution** : le « environ 4 % »
   du texte de la fiche 16 (graphique 3, 3,3 % ; son complément, 4,2 %) ; la ligne
   recopiée du graphique 3 complémentaire ; le « 77 700 nouveaux allocataires » de
   la fiche 28 (son tableau, 70 700). Les tests les déclarent, avec la cellule et
   la page ; si la DREES publie un erratum, les valeurs du témoin se reprennent.

**Candidats, hors de cette tâche.** (a) Le jeu `drees_minimum_vieillesse` du
portail, à ouvrir depuis un poste : les entrants par âge et par caisse, le seul
endroit où les 70 660 se liraient à la source primaire. (b) Les feuilles de la
fiche 16 que je n'ai pas lues (graphiques 1, 2, 4, 5 et 5 compl.), de la fiche 15
(graphiques 1, 3 et 4) et de la fiche 28 (tableaux 1 à 4, carte 1) restent à
confronter, ou à écarter, à la clôture (étape 7). (c) Le tableau 5 de la fiche 28
donne l'âge des nouveaux allocataires (62 et 65 ans surtout) : la population de
l'étape 14 pourrait s'y caler.

## Les tests

Dans `tests/test_controle_drees_panorama.py`, sept tests neufs ou récrits, chacun
vu rouge pour la raison attendue (le témoin n'avait pas la ligne, le suivi ne
nommait pas le test), puis vert :

- `test_la_grille_met_chaque_regime_de_2024_a_un_ou_deux_ages_quand_la_source_les_etale`
  (fiche 16, graphique 3) ;
- `test_le_graphique_3_complementaire_repete_la_sncf_pour_la_cnavpl_et_la_source_dit_4_pour_cent_de_moins_de_60_ans` ;
- `test_la_grille_part_a_l_age_des_hommes_de_chaque_regime_et_de_sa_seule_femme_et_les_pese_autrement`
  (tableau 2 complémentaire) ;
- `test_les_nouveaux_allocataires_du_minimum_vieillesse_sont_un_flux_que_le_depot_ne_calcule_pas`
  (fiche 27) ;
- `test_l_age_conjoncturel_de_la_grille_est_celui_de_ses_cas_types_au_premier_age_ou_leur_cohorte_est_retraitee`
  (fiche 15, graphique 2) ;
- `test_la_duree_de_retraite_du_depot_est_celle_de_la_drees_a_quelques_dixiemes_pres_et_la_grille_part_trop_tard`
  (fiche 15, graphique 7) ;
- `test_les_fiches_15_16_et_27_nomment_leurs_confrontations` (le suivi ; il remplace
  `test_les_fiches_16_et_27_nomment_leurs_confrontations`).

Le témoin `tests/temoins/drees_panorama_2026_confrontations.json` reçoit six entrées de
valeurs (`16_graphique_3`, 81 cellules ; `16_graphique_3_compl`, 27 ;
`16_tableau_2_compl`, 28 ; `15_graphique_2`, 7 ; `15_graphique_7`, 24 ; `28_tableau_5`, 5)
et trois cellules dans des entrées qui existaient (`27_graphique_1`, 2023 ;
`27_tableau_1`, H24), soit 174 cellules, relues au bit près ; et trois entrées de
citations (`15_texte`, `16_graphique_3`, `28_texte`, 15 phrases) avec cinq phrases de
plus à `27_texte`, relues au PDF. Il ne perd aucune ligne (vérifié : tout ce qu'il
portait, il le porte). Au suivi (`data/reference/drees_panorama_2026.yaml`), les
fiches 15, 16 et 27 restent `confronte` et nomment leurs tests nouveaux ; leur
« Restent » est remplacé.

*Relecture du 6 novembre 2026 (R-J4) : chiffres conformes, un écart moyen de déclaration (point 5.1) et cinq faibles ; voir `2026-11-06-relecture-r-j4.md`.*
