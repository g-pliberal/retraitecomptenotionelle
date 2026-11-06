# J5-bis : les écarts de la relecture R-J5, repris aux sources (le régime général de la fiche 1, les révisions de la fiche 21, « aucune erreur du dépôt », treize faibles)

**Reprise, au 6 novembre 2026.** Fait (cette note, qui reprend les blocs de
`2026-11-06-etape-5-bis-corrections-de-r-j4.md` et de `2026-11-06-etape-7-solde-du-suivi.md`) :
les trois écarts moyens et les treize faibles de R-J5, repris aux sources et au suivi.
Reste à l'action 178, par le propriétaire : l'étape 5 (les trois erreurs du coût,
`2026-11-03-etape-5-regles.md`, avec l'effet des écarts de J4, non mesuré) ; le jeu
`drees_minimum_vieillesse` du portail, à ouvrir depuis son poste (connexion refusée à
J4, R-J4 et J5) ; s'il le veut, l'un des candidats de la section 5 de la note de J5.
Par quoi commencer : la note des règles.

**La demande.** Vague 11, tâche J5-bis, le 6 novembre 2026 : reprendre aux sources
les écarts que R-J5 (`2026-11-06-relecture-r-j5.md`, commit a5b3ac0) a trouvés dans
le travail de J5 (`2026-11-06-etape-7-solde-du-suivi.md`, commit cef7bfa) et de J4-bis
(`2026-11-06-etape-5-bis-corrections-de-r-j4.md`, commit 9429683). L'exigence du
propriétaire (3 novembre) : aucune erreur ; un document source à la clé ; jamais la
mémoire ; de quoi justifier par écrit tout le système.

**Les sources, ouvertes pour cette tâche.** `python scripts/fetch/source_locale.py
--recuperer` : le PDF (SHA-256
`9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`, le miroir de
l'UNSA) et l'archive des 36 classeurs
(`ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`), que
`sha256sum` a retrouvées. Le PDF par `pdftotext` (le folio imprimé est la page du
fichier moins un : « Drees 299 » au pied de la page 300) ; les classeurs par
`openpyxl` (`data_only`), puis, pour les cellules ajoutées au témoin, par
`lecture_xlsx` du dépôt, les deux lectures étant comparées cellule par cellule à la
fabrication (aucun écart). La table C de l'EACR n'est pas dans l'archive : elle se
lit au témoin du dépôt (`tests/temoins/drees_eacr_tables_2026.json`).

## 1. Écart moyen 1 : le régime général de la fiche 1 (13,2 contre 14,1)

**La source.** Annexe 3, « Création de la SSI et fusion avec le régime général »
(folio 299) :

> « Ce régime a lui-même disparu fin 2019, suite à son intégration au régime général
> de la Sécurité sociale. [...] À partir de 2020, seul le régime général total existe.
> Par ailleurs, les effectifs du régime général après intégration des indépendants de
> l'ex-SSI sont estimés dans le passé à partir du modèle ANCETRE : un individu
> polypensionné du régime général et de la SSI ne compte qu'une fois dans le régime
> général. »

La feuille « F01_Tableau 2 compl » (B29, note 2 de la ligne CNAV) renvoie à cette
annexe : « Voir annexe 3, note sur la fusion de la CNAV et de la SSI » (le PDF,
folio 23 : « Voir annexe 3, note sur l'intégration de la SSI au régime général »).
La cellule I8 vaut 13,2 ; H8 (2020-2024), 4,9.

**Le calcul, posé à la main.** Cadrage (`effectifs_retraites.csv`) : Cnav 2014 =
12 922 464, 2020 = 14 052 675, 2024 = 14 744 736. 14 744 736 ÷ 12 922 464 = 1,14102,
soit +14,10 % ; 14 744 736 ÷ 14 052 675 = 1,04925, soit +4,92 % (publié 4,9 : la même
base, post-intégration, concorde). Pour que 14 744 736 fasse 13,2 % de plus,
arrondi à 13,15-13,25 : 14 744 736 ÷ 1,1325 = 13 019 634 et ÷ 1,1315 = 13 031 141,
soit 97 170 à 108 677 personnes de plus que les 12 922 464 du cadrage (de 0,75 à
0,84 %). L'en-tête du cadrage écrit lui-même que la Cnav « porte le code 0010
jusqu'en 2019 puis 0015, sur un champ légèrement plus large ».

**Ce qui est établi, ce qui ne l'est pas.** Établi : l'écart est de périmètre, et la
source en donne le mécanisme (un régime général de 2014 reconstitué avec les
indépendants de l'ex-SSI). Non établi : la base de 2014 de la DREES, qu'aucune page
ni feuille ne publie ; l'ordre de grandeur de l'écart (97 à 109 mille, 0,8 % de la
base) est compatible avec ce mécanisme, non démontré. Dit au suivi (fiche 1, `solde`),
pas « point non tranché ». Le dépôt n'a pas d'erreur ici : le cadrage sert à pondérer
les cas types (son en-tête), non à mesurer une évolution à travers 2020. Pinné :
`test_l_ecart_du_regime_general_de_la_fiche_1_est_celui_de_la_reconstitution_de_2014_de_l_annexe_3`.

## 2. Écart moyen 2 : les feuilles « REVISIONS » de la fiche 21

Les cinq feuilles « REVISIONS » lisent « DONNEES PANORAMA 2025 » et « REVISIONS
ENTRE PANORAMA 2026 ET 2025 ». Lues cellule par cellule :

| feuille | génération du bloc de 2025 (titre, B2) | feuille de 2026 (B2) | 2025 + révision = 2026 |
|---|---|---|---|
| Graphique 1 | « Personnes nées en 1942, 1946, 1950, 1954 ou 1958 » (Champ, C34) | idem | 144 cellules (J5) |
| Tableau 1 | 1942, 1946, 1950 | 1942, 1946, 1950 et 1954 | **43 cellules** (45 de D7:H15, hors E13 et E15, « <1 » en texte) |
| Tableau 2 | « génération née en 1950 », « EIC 2017 » | « génération née en 1954 », « EIC 2021 » (PDF, folio 186) | **9 cellules** (trois lignes : 0,98 + 0,74 = 1,72 ; 6,99 + 1,87 = 8,86 ; 2,77 + 1,48 = 4,25) |
| Graphique 2 | « génération née en 1950 » | « génération née en 1954 » (PDF, folio 188 : « Source > Drees, EIC 2021 ») | **432 cellules** (femmes C8:J25, hommes C30:J47, ensemble C52:J69, contre les feuilles de 2026) |
| Tableau 3 | « génération 1950 », « EIC 2017 » | « nées en 1954 », « EIC 2021 » (PDF, folio 189) | **48 cellules** (C8:H15) |

**R-J5 écrivait « les quatre lignes comparables du tableau 2 (10, 13, 14, 16) » : il
y en a trois.** La ligne 16, « Ensemble », vaut 100 en 2025 (C16:E16) et 100 dans le
bloc des révisions (H16:J16), qui devrait y valoir 0 : 100 + 100 n'est pas 100. C'est le
même défaut que la colonne « Total » des révisions du tableau 1 (R7:R15, 100 en
chaque ligne). Les neuf cellules des trois autres lignes se vérifient.

**Ce que dit « Synthese »** (D3, E3, F3, mot pour mot) : « 1954 dans Pano 2026, vs
1950 auparavant » pour le tableau 2, le graphique 2 et le tableau 3. Origine des
écarts : tableau 3 (F4), « - Quasi exclusivement du fait du changement de génération » ;
graphique 2 (E4), « - Quasi exclusivement du fait du changement de génération et des
règles de liquidation différentes (recul progressif de l'AOD entre générations 1950 et
1955) » ; tableau 2 (D4), « - Principalement changement méthodologique [...] - Dans une
moindre mesure, impact du changement de sources (EIC 2021) et de génération (1954 vs
1950 précédemment) ». Au graphique 2 la révision va jusqu'à 42,04 points (S18, femmes,
60 ans, « Retraite ») : c'est le recul de l'âge d'ouverture des droits entre les
générations 1950 et 1954, non une correction. **Le tableau 1 (générations 1946 et 1950
communes, la génération 1942 de l'EIC 2013 dans les deux éditions, révision 0 à chaque
cellule M7:Q9) et le graphique 1 sont de vraies révisions** ; les trois autres ne le
sont pas, et ne se citent pas comme « la DREES a révisé ».

**Les défauts de la source, lus et épinglés.** Colonne « Total » du tableau 1 et ligne
« Ensemble » du tableau 2 écrites 100 pour 0 ; `#VALUE!` en N20 du tableau 1 ;
`#REF!` en H8:J8 du tableau 2 (relus à `openpyxl`, `lecture_xlsx` ne lit pas les
cellules d'erreur) ; « Synthese » minore deux maxima, « jusqu'à 2,8 point » (C2) pour
2,91 (M11, hommes de 1946, en emploi), « jusqu'à 3 points » (F2) pour 3,93 (N9,
femmes, hors cumul emploi-retraite). Deux étiquettes « EIC 2021 ; GEN 1950 » (L99) et
« EIC 2021 ; GEN 1954 » (L158) restent au graphique 2 des révisions, sans donnée
dessous : les blocs de travail qui auraient départagé le changement de source et le
changement de génération sont vides. Dit au suivi (fiche 21, `solde`). Pinné :
`test_trois_des_quatre_feuilles_de_revisions_de_la_fiche_21_comparent_deux_generations`.

## 3. Écart moyen 3 : « aucune erreur du dépôt »

Le message de cef7bfa dit « aucune erreur du dépôt » ; le suivi (fiche 15), « Aucune
erreur du modèle ». La note de J5 disait plus juste : « aucune de ces lectures
contraires n'est intenable : aucune n'est déclarée erreur du dépôt ni de la DREES ».
**La formule retenue au suivi : « aucune erreur établie, trois écarts non expliqués »**,
c'est-à-dire que rien de ce qui a été confronté n'a été prouvé faux, et que trois
écarts du dépôt à la source ne sont ni expliqués ni tranchés. Je ne les tranche pas.

1. **Le taux de retraités par âge** (fiches 15 et 16). Le panorama, au 31 décembre
   2024 (« F15_Graphique 4 », ligne 26 ; Champ : « Retraités de droit direct, résidant
   en France » ; Sources : « Drees, EIR, modèle ANCETRE ; Insee, bilan
   démographique »), donne 48,12 % à 62 ans et 94,30 % à 67 ans. La table C de
   l'EACR rapportée à la population du 1er janvier 2025 du dépôt (une projection,
   `population_par_age.csv`) : 412 125 ÷ 848 498 = 48,57 %, soit +0,45 point ;
   762 868 ÷ 791 100 = 96,43 %, soit +2,13 points (63 ans +0,78 ; 64 ans +1,05 ; 65 ans
   +1,34 ; 66 ans +1,53). L'écart croît avec l'âge. L'explication du test de J5 (la
   source compte les résidents en France, la table C tous les retraités, dont 5 % à
   l'étranger) a une base : le tableau 3 de la fiche 3 (folio 38) donne 95 / 5 pour
   « l'ensemble des bénéficiaires d'une pension de droit direct » ; mais c'est une
   part tous âges, la part des résidents à l'étranger à 62 ou 67 ans n'est dans aucune
   page. Plausible, non démontrée.
2. **L'âge conjoncturel du portail** (`age_conjoncturel_depart.csv`, 63 valeurs :
   21 années de 2004 à 2024, trois séries) contre « F15_Graphique 1 » (lignes 5 à 7) :
   **20 valeurs diffèrent de plus de 0,005 an**, toutes de 2004 à 2013 et pour les
   femmes et l'ensemble (2004, femmes : -0,01 ; 2013, femmes : 61,44 contre 61,54, soit
   -0,10 ; 2013, ensemble : -0,05) ; les hommes, et toutes les séries de 2014 à 2024,
   sont identiques au centième. R-J5 écrivait « de 2004 à
   2021 » : c'est de 2004 à 2013. La source ne dit pas laquelle des deux séries est
   révisée.
3. **Six classes à un point** (fiche 16, « F16_Graphique 5 compl », colonnes O et AD,
   génération 1953, contre le tableau 1 de `retraites_generations.csv`) : six écarts
   d'un point sur **seize comparaisons** (huit classes regroupées, deux sexes), non
   « six classes sur neuf » : femmes, 60 ans (12 contre 11), 61 ans (45 contre 44),
   66 ans ou plus (13 contre 13 + 1 = 14) ; hommes, 60 ans (21 contre 20), 63 à 65 ans
   (8 + 4 = 12 contre 13), 66 ans ou plus (8 contre 8 + 1 = 9). Les deux séries sont des
   entiers. Trois écarts portent sur des classes regroupées (femmes et hommes, 66 ans
   ou plus ; hommes, 63 à 65 ans), où une somme d'entiers arrondis peut s'écarter d'un
   point de l'entier arrondi de la somme ; trois sur une classe seule (60 ans des deux
   sexes, 61 ans des femmes), que le seul arrondi n'explique pas (une même valeur
   arrondie donne un même entier) : deux calculs légèrement différents, deux
   millésimes. La source ne départage pas.

Au suivi (fiches 15 et 16, `solde`) : « Aucune erreur établie, trois écarts du dépôt à la
source non expliqués, ni tranchés ni disculpés ». Pinné : les assertions ajoutées aux
tests existants (63 valeurs, 20 écarts, seize comparaisons).

## 4. Les treize faibles de R-J5 (section 9), un par un

| n° | R-J5 | ce que j'ai lu | suite |
|---|---|---|---|
| 1 | les lignes 2 (PIB) et 9 (« A DECIDER ») de la liste des défauts n'en sont pas | PIB : « F10_Graphique1 », ligne 9, « PIB en valeur (en milliards) », 2023 = 2 826,542, 2024 = 2 919,9 contre 2 833,826 et 2 935,236 au dépôt (-0,26 et -0,52 %) ; 1990-2022 identiques. B19 : « Source > Drees, CPS, données semi-définitives pour 2023 et provisoires pour 2024 » : **la note porte sur les CPS, non sur le PIB**, dont la feuille ne dit ni la source ni le millésime. R-J5 écrivait « un autre millésime de l'INSEE, non dit » en s'appuyant sur cette note : c'est l'explication la plus simple, non lue à la source. « A DECIDER » : C7 et F7 de « Synthese », fiche 12 : une note de travail | repris : au suivi (fiches 10 et 12) l'écart du PIB est « écart déclaré, non tranché, et non un défaut de la source » ; « A DECIDER » est « une note de travail restée dans le classeur ». La liste de la note de J5 (section 3, « Les défauts de la source ») est plus large que sa matière ; sa note ne se récrit pas |
| 2 | CNRACL et Ircantec : le défaut est imprimé | PDF folio 37 (page 38, `pdftotext -layout`) : « CNRACL 145 51 196 147 0,0 0,1 0,2 4 » ; « Ircantec 206 43 250 209 0,0 -0,1 -0,2 6 ». Classeur « F03_Tableau 2 », G12:I13 = 0,016 ; 0,093 ; 0,23 ; -0,01 ; -0,068 ; -0,155, format `0.0` ; « F03_Tableau 2 compl », G15:I16 = 1,6 ; 9,3 ; 23 ; -1 ; -6,8 ; -15,5 : exactement le centuple. Le tableau 2 imprime donc les fractions arrondies au dixième ; la source ne dit pas laquelle des deux feuilles est la bonne | repris : suivi fiche 3 ; test `test_le_folio_37_imprime_les_evolutions_de_la_cnracl_et_de_l_ircantec_en_fractions_arrondies` (regex sur le PDF, saute sans `pdftotext`) |
| 3 | fiche 23 : l'annexe 3 tranche | « F23_Graphique 1 » B26 : « depuis 2020 » ; « F23_Graphique 1 compl. » B27 : « La SSI intègre le régime général en 2021. Cependant, les données du régime général portent uniquement sur le champ des salariés dans ce tableau » ; annexe 3 (folio 299) : « fin 2019 », « À partir de 2020 ». Le « 2021 » est celui d'une note de champ | repris : suivi fiche 23 ; test `test_les_tableaux_3_et_4_de_la_fiche_28_sont_de_fin_2020_et_l_annexe_3_date_la_ssi` |
| 4 | « 61,63 » recopié de travers | « F15_Graphique 1 » : L4 = 2013, L5 = 61,44 ; M4 = 2014, M5 = **61,63**. Le dépôt, 2013 femmes : 61,54 ; écart 61,44 − 61,54 = -0,10. La note de J5 (« 2013, femmes : 61,63 − 0,10 ») mêle la valeur de 2014 du panorama et l'écart de 2013 | repris ici : la valeur juste est **61,54 au dépôt, 61,44 au panorama, 2013, femmes**. Le 61,63 n'est ni au suivi ni dans un test (recherché) : seule la note de J5 le porte, et elle ne se récrit pas |
| 5 | « 4 406,64 = 3 836,17 + 570,46 » | 3 836,17 + 570,46 = 4 406,63 ; « F03_Tableau 1 » E26 et « F03_Tableau 2 compl » E6 = 4 406,64 : un centième d'arrondi de la source. Le test de J5 le dit déjà (« le dernier centième près ») | laissé : l'écart est d'un centième, dit par le test ; la note de J5 ne se récrit pas |
| 6 | fiche 17, une cellule vide non dite | « F17_ Graphique 3 compl », J27 (« Départ au taux plein pour autre motif », hommes, génération 1942) : vide ; le témoin range 11 cellules aux hommes pour cette modalité, 12 aux femmes ; 12 × 9 − 1 = 107 | repris : suivi fiche 17 ; le test passe de `vus >= 100` à `vus == 107` |
| 7 | « six classes sur neuf » | section 3, point 3 : six écarts sur seize comparaisons | repris : suivi fiche 16 ; le test compte ses comparaisons |
| 8 | fiche 28 : « fin 2020 » non dit | « F28_Tableau 3 » B2 : « [...] selon le type de pension, fin 2020 » ; « F28_Tableau 4 » B2 : « [...] non allocataires, fin 2020 » ; « Source > Drees, EIR 2020 » | repris : suivi fiche 28 (« tous deux de fin 2020, non de 2024 ») ; test des dates |
| 9 | fiche 21 : `#VALUE!`, `#REF!`, « Total », « Synthese » minore | section 2 | repris : suivi fiche 21 |
| 10 | les zéros : la preuve ne vaut que pour la CANSSM | Cadrage : CANSSM 2019 = 120 139, 2020 = 112 628, 2024 = 86 133 (86 133 ÷ 112 628 = 0,7647, -23,5 %) : un vrai zéro 2014-2024 supposerait 2014 = 86 133, donc +39,5 % jusqu'en 2019 (120 139 ÷ 86 133 = 1,395) et +30,8 % jusqu'en 2020 (112 628 ÷ 86 133 = 1,308 ; 1 ÷ 0,765 = 1,307, d'après le -23,5 % arrondi publié, d'où le 30,7 de J5), quand la série baisse de 2019 à 2020. Banque de France : 2016 = 13 521, 2024 = 14 769 ; un vrai zéro supposerait 14 769 en 2014, donc -8,5 % jusqu'en 2016 (13 521 ÷ 14 769 = 0,9155), puis +9,2 %. Enim : 2020 = 65 575, 2024 = 62 598, rien avant. L'annexe 3 et les notes de la feuille ne disent rien de ces trois lignes | repris : suivi fiche 1 (« à ne pas citer » maintenu pour les trois ; l'argument chiffré dit pour chacune sa force : peu vraisemblable, peu plausible, non contredit) ; docstring du test |
| 11 | le « rouge » du test d'abord | Les 29 tests de J5 ont échoué d'abord faute de témoin, non pour une valeur : un fait de procédure, passé | laissé : un récit ne se refait pas, et aucun chiffre n'en dépend. Cette fois : le test du suivi (`test_le_suivi_dit_ce_que_les_sources_prouvent…`) a été lancé seul et vu échouer sur la phrase « la note renvoie à la SSI » avant les retouches du suivi ; les tests de faits (révisions, annexe 3, folio 142) passent d'emblée, puisqu'ils disent la source, et chaque valeur du témoin est relue à l'archive par `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule` |
| 12 | graphique 5 de la fiche 15, « après 1954 » | « F15_Graphique 5 » B38, Champ : « (pour les générations nées en 1953 ou avant) et à 67 ans (pour les générations nées après 1954) » ; « F15_Graphique 7 » B38 : « (pour les générations nées en 1953 ou avant) et à 67 ans (pour les générations nées en 1954 ou après) » : la génération 1954 est dans aucune clause du graphique 5 | laissé : un trou de la source dans une clause de champ que ni le suivi ni un calcul du dépôt n'emploient ; la lecture « 1953/1954 » de J4-bis est une convention de lecture, que cette ligne dit ; rien à porter |
| 13 | docstring du test de J4-bis : « trois des quatre minima » | `moteur/js/pages.js:13330` : la page retire **quatre** minima, dont celui des exploitants agricoles, qui est **deux** lignes de la cascade (`pension_majoree_reference`, `complement_differentiel_rco`) : cinq lignes. Le jour de naissance déplace trois des quatre minima (contributif, garanti, exploitants agricoles) et quatre des cinq lignes ; le minimum vieillesse, lu dans les comptes, ne bouge pas. **La docstring est exacte ; R-J5 a compté les lignes, non les minima.** Les valeurs de J4-bis (4 941,15 / 1 563,24 → 1 568,64 / 6,66 → 6,68 / 349,01 → 396,01 / 636,73 → 677,68 ; 7 496,79 et 7 590,17) sont celles du test, qui passe aux deux jeux | repris : la docstring dit désormais « quatre minima, cinq lignes » et « quatre lignes sur cinq » |

**Un fait de source de plus, que R-J5 a nommé et que le suivi porte** : le folio 142
écrit « Cet âge atteint ainsi 61 ans et 7 mois pour la génération 1957, soit 1 an et 1
mois de plus que pour la génération 1950 ». « F15_Graphique 5 » donne 60,46 (1950, E29),
61,59 (1955, E34) et 61,85 (1957, E36) : 61 ans et 7 mois, 61,583, est la valeur de 1955,
et « 1 an et 1 mois de plus que 1950 » (61,583 − 60,46 = 1,12 an) lui est cohérent ;
la génération 1957 vaut 61 ans et 10 mois (0,85 × 12 = 10,2 mois), 1 an et 5 mois de
plus (1,39 an). Coquille du texte ou autre édition : la source ne dit pas laquelle ; à ne
pas citer pour 1957. Suivi fiche 15 ; test
`test_le_texte_du_folio_142_donne_61_ans_et_7_mois_pour_la_generation_1957_quand_le_graphique_5_donne_61_85`.

## 5. Ce que j'ai corrigé de R-J5, et ce que je n'ai pas repris

- **Corrigé** : « quatre lignes comparables du tableau 2 » (trois ; section 2) ;
  « de 2004 à 2021 » (de 2004 à 2013 ; section 3) ; « un autre millésime de l'INSEE »
  (la note citée porte sur les CPS ; ligne 1 du tableau de la section 4) ;
  « quatre lignes sur cinq » dit mal la docstring de J4-bis, qui compte des minima
  (ligne 13).
- **Non revérifié par moi, pris à R-J5 ou à J5 sans le dire exact** : les 4 209 cellules
  du témoin de J5 (la suite le fait : `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`
  passe sur l'archive) ; l'âge conjoncturel de 63 valeurs refait des taux (le test de
  J5 le fait, il passe) ; la fiche 17 (sexe du taux de liquidation, « sans la marge de
  0,1 point », que le test de J5 se donne) ; la fiche 10 refaite à la main ; les
  chiffres de J4-bis (arrondis, CNRACL) et l'isolement du jour de naissance présumé
  (j'ai relancé les tests aux deux jeux, non l'arbre de travail jetable de R-J5).
- **Hors de la tâche, non traités** : le jeu `drees_minimum_vieillesse` ; la
  publication de l'INSEE de 2021 (note du graphique 7) ; le classeur A-Cadrage de
  l'EACR ; les trois erreurs du coût.

## 6. Les tests, et ce qui a changé

- `tests/test_drees_panorama_solde.py` : 29 → 35 tests. Six neufs : annexe 3, révisions
  de la fiche 21, folio 142, dates (fiches 28, 23 et 12), folio 37, et les mots du
  suivi. Des assertions de plus aux tests existants : 63 valeurs et 20 écarts
  (âge conjoncturel), seize comparaisons (graphique 5 complémentaire), 107 cellules
  (fiche 17). Deux docstrings reprises (fiche 1).
- `tests/temoins/drees_panorama_2026_solde.json` : des cellules et trois citations de
  plus (annexe 3, folio 142), lues du PDF et de l'archive, qu'aucun test ne laisse
  sans relecture. Aucune valeur de J5 ne change.
- `tests/test_controle_drees_panorama.py` : la docstring de la garantie seulement.
- `data/reference/drees_panorama_2026.yaml` : dix `solde` (fiches 1, 3, 10, 12, 15, 16,
  17, 21, 23, 28), des mots, aucune valeur.
- Les blocs « Reprise » de l'étape 5-bis et de l'étape 7 sont ôtés (ils n'avaient plus
  d'objet, ou leur objet est au bloc de cette note) ; un renvoi daté d'une ligne au bout
  de la note de J5.
