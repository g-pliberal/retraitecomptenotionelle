# Relecture de J : les fiches 12, 15 et 21

**Verdict : les chiffres sont conformes ; trois écarts de déclaration, aucun
de chiffre.** Les 44 cellules neuves du témoin, et les 490 autres, sont celles
des classeurs ; chaque valeur de la grille que la note donne (21,43 ; 38,30 ;
61,03 ; 62,09 ; 86,10 ; 90,79 et le reste de ses tableaux), je l'ai
recalculée par mon propre script et retrouvée ; les citations du PDF sont
mot pour mot, aux folios dits ; les 76 tests passent, aucun sauté. Les écarts :
« 45 cellules » alors que le témoin en a 44 (faible, point 1.5) ; deux cellules
dites « écrites en texte » qui sont des nombres (faible, point 1.6) ; le champ
du graphique 1 de la fiche 21, que la source dit « hors retraités dès 50 ans »
et que la grille de la note ne retire pas, de sorte que 86,1 % en emploi
devient 88,5 % dans ce champ (faible à moyenne, point 3.2). Le sens de chaque
écart ne change nulle part. Cinq autres points sont négligeables (point 4).

**La demande.** Vague 9, file R-J2, le 5 novembre 2026 : revérifier, contre les
sources et sans se fier à J ni à la mémoire, le commit `3b36b08` de la session
`session_01FVFLAiG73venRrPPTrNaQT` et sa note
`2026-11-05-etape-5-fiches-12-15-21.md`. Rien n'est modifié : ni règle, ni
donnée, ni test, ni note. Les écarts se décrivent ici ; une correction irait
dans une note neuve.

**Les sources, ouvertes pour cette relecture.**
`python scripts/fetch/source_locale.py --recuperer` a rapporté le PDF du
miroir de l'UNSA (`9eb36a06…735e9be`) et l'archive des trente-six classeurs
(`ec7503f8…aaf64911`), aux empreintes du manifeste, que `sha256sum` retrouve.
Le classeur des nés en 1953 (EIR 2020), je l'ai téléchargé de l'API de la
DREES à l'adresse que cite la note : 195 574 octets, SHA-256
`d5e8b8776768e31a3a8a0490bf749fc6615d12a8d25716e57a658dd16f94c5e0`, celui de
la note de l'action 138. Je lis les classeurs de l'archive avec `openpyxl`
(`data_only`) et celui de l'EIR par un lecteur XML minimal à moi
(`openpyxl` y échoue : un dessin manque à l'archive) ; ni l'un ni l'autre n'est
`lecture_xlsx`, le lecteur de J : les lectures sont indépendantes. Le PDF passe
par `pdftotext`, page à page (la page du fichier est l'imprimée plus un).

## 1. Les écarts de la relecture R-J (point 1 de la demande)

**1.1. Les huit cellules à 58,7 : conforme.** Je cherche toute cellule
numérique à 0,05 près de 58,7 dans les trente-six classeurs : huit, les mêmes
que la note, aux mêmes cellules, aux mêmes valeurs :

| classeur, feuille, cellule | valeur |
|---|---|
| `fiche_05`, « F05_Graphique 1 », R8 | 58,7089 |
| `fiche_08`, « F08_Tableau compl encadré 2 », G12 | 58,6854 |
| `fiche_12`, « F12_Graphique 2 », L10 | 58,7 |
| `fiche_12`, « Graphique 2 (2) », N93 | 58,7 |
| `fiche_15`, « F15_Graphique 6 », C12 et D12 (C5 : 1940, D5 : 1941) | 58,7 |
| `fiche_21`, « F21_Tableau 1 REVISIONS », D12 | 58,73 |
| `fiche_21`, « F21_Tableau 2 REVISIONS », E8 | 58,68 |

Aucune n'est une part de carrières complètes : pension nette en % du revenu net
(R8, titre B2), euros de majoration (G12, en-tête G6), rythme de validation
(L10, en-tête L5 « Entre 30 et 49 ans »), âge de départ (C12, ligne
« CNRACL »), part en emploi (D12, en-tête D6), passage direct à la retraite
(E8, B8). Le texte du PDF n'a ni « 58,7 » ni « 58.7 » (recherche sur le texte
de `pdftotext`, césures défaites).

**1.2. L'origine du 58,7 % : conforme.** Classeur des nés en 1953, feuille
« Naissance-Résidence » : K18 = 58,7 (A18 « Femme », B18 « Carrière complète »,
C18 « Part d'assurés à carrière complète (en %) », K1 « Retraités résidents en
France »). Ses voisines, lues : K17 = 65,1, L17 = 63,4, L18 = 57,3, K19 = 72,2,
L19 = 70,0. Face à « F11_Graphique 2 » : H25 = 58, J25 = 65, E25 = 63, C25 = 57,
I25 = 72, D25 = 69 ; face à « F11_Graphique 2 compl » : H25 = 64, J25 = 70,
E25 = 69, C25 = 63, I25 = 77, D25 = 75. Les six écarts à la proratisation
valent 0,7 ; 0,1 ; 0,4 ; 0,3 ; 0,2 ; 1,0 point (de 0,1 à 1,0, comme la note), et
de 4,8 à 5,7 points sous « compl » (5,3 ; 4,9 ; 5,6 ; 5,7 ; 4,8 ; 5,0). Le
classeur n'a aucune note : 202 chaînes, aucune ne dit « requise », « note »,
« champ » ou « définition » ; seuls « Carrière complète », « Part d'assurés à
carrière complète (en %) » et « Coeficient de proratisation moyen » parlent de
complétude. La note a raison : la source ne donne pas la définition de la
carrière complète de ce classeur.

**1.3. La feuille « compl » se contredit, et 1942 vaut −1 : conforme.** B2 de
« F11_Graphique 2 compl » : « … en fonction de la durée requise … » ; son B27 et
sa lecture : « au sens de la proratisation à 100 % ». E15 vaut 58 dans les deux
feuilles. L'écart de la colonne E, « compl » moins « Graphique 2 », recalculé
pour les dix-huit générations : +4, +5, +4, +5, +4 (1926 à 1934), +3 (1936),
+2 (1938), 0 (1940), **−1 (1942 : E16 = 59 contre 60)**, +2 (1944), +4 (1946),
puis +6, +6, +7, +6, +7, +6, +6 (1947 à 1953) : la note a raison, et la
relecture R-J, « de 0 à 2 points de 1938 à 1944 », se trompait (ligne 254 de
sa note). La phrase de l'annexe 3 est au folio 300, mot pour mot : « La
proportion de carrières complètes selon cette définition est proche de celle
du premier cas, sauf concernant les générations pour lesquelles les durées
requises pour le taux plein et les durées requises pour une proratisation à
100 % diffèrent (générations 1934 à 1948) » ; l'annexe 4 est le glossaire, au
folio 301 (sommaire, ligne « Annexe 4 • Glossaire … 301 »).

**1.4. 552 625, « deux cinquièmes », « 1,1 point » : conforme.** Les têtes des
nouveaux retraités du régime général de la grille (`controle_eacr.controle()`,
cohortes `nouvelle`, régime principal `regime_general`, huit cas types) : artisan
40 444,63 ; cadre 86 067,45 ; carrière interrompue 92 457,62 ; contractuel
70 089,68 ; salaire moyen 91 167,68 ; Smic 96 351,16 ; ex-invalide 38 727,96 ;
inapte 37 318,70 ; **somme 552 624,88, soit 552 625**. 24,19 / 17,4 = 1,3902 :
39 % de trop, deux cinquièmes (un tiers serait 1,333). L'évolution 2014-2024 de
la grille, recalculée par mon script (le portage du test, hors du test) :
1 826,70 puis 1 913,93 euros de 2024, soit +4,775 %, contre 3,7 à F15 de
« F05_Tableau 2 » : 1,075 point, « à 1,1 point près » est juste ; les deux
autres évolutions, +3,750 contre 3,9 (D15) et +1,357 contre 1,1 (E15), sont à
0,15 et 0,26 point. Dans « F08_Tableau encadré 2 », F6:F29 se somme à 503 936
et F30 dit 503 942 ; C6:C29 fait 788 666, C30 aussi (point 5.4 (d) de la note).

**1.5. Le compte des cellules neuves : écart, faible.** La note (« 45 cellules
au témoin », deux fois : la reprise et « Les tests ») et le commit disent 45 ;
le suivi ne donne aucun compte. Le témoin du commit a 534 cellules, celui du parent 490 :
**44 neuves**, aucune modifiée (`12_graphique_1` : 14 ; `15_graphique_5` : 6 ;
`15_graphique_6` : 12 ; `21_graphique_1` : 7 ; `21_tableau_2` : 5). Aucune cellule
ne manque aux tests : c'est le compte qui est faux d'une unité. À corriger là
où il est dit.

**1.6. « D10 et E10 sont écrits en texte » : écart, faible.** La note (point 5
de « Ce que la source ne tranche pas ») dit qu'à « F12_Graphique 1 », D10 et E10
sont du texte (« 44 », « 42 ») que `lecture_xlsx` convertit. Dans le XML de la
feuille, `<c r="D10" s="242"><v>44</v></c>` et `<c r="E10" s="243"><v>42</v></c>` :
des nombres, sans type `s` ni `str`, du même style (format « 0.0 ») que C10 et
F10, qui valent 40,1 et 19,8 ; aucune cellule des lignes 7 à 28, colonnes C à K,
n'est du texte, et aucun texte « 44 » ou « 42 » n'est dans le classeur. Les
valeurs du témoin, 44,0 et 42,0, sont les bonnes ; c'est l'anomalie que la note
prête à la source qui n'existe pas. À retirer de la liste.

## 2. Les valeurs du modèle et les tests (point 2 de la demande)

**2.1. Les valeurs de la grille : conforme.** Mon script (`controle_eacr.controle()`
et `Simulateur.pour_la_projection`, la méthode que la note décrit) donne, nés en
1950 comme en 1954 : première année complète 21,4259 (femmes 21, hommes 21,4780),
38,2962 trimestres à 30 ans (40 ; 38,088), 18 cohortes, 730 846 et 744 485 têtes ;
par cas type, les couples de la note (18 et 52 ; 20 et 44 ; 21 et 40 ; 22 et 36 ;
23 et 32 ; 24 et 28 ; 27 et 16), un par un. Âge de départ, nés en 1950 puis
1955 : 61,0329 et 62,0949 (femmes 60 et 62 ; hommes 61,1591 et 62,1065) ; régime
général 61,4740 et 62,6112 ; MSA non-salariés 60 et 62 ; État civil 61,1778 et
61,9655 ; militaires 48 et 48 ; CNRACL 61,5262 et 62,2892 ; les âges de chaque
cas type, un par un (fonctionnaire actif 60 et 60 ; sa variante sédentaire 62
et 63 ; super-actif 55 ; militaire 48 ; SNCF 50 ; IEG 55 …). Les écarts « 1,5 à
2,4 ans » des fonctionnaires : 61,53 − 59,1 = 2,43 ; 62,29 − 60,0 = 2,29 ;
61,18 − 59,2 = 1,98 ; 61,97 − 60,5 = 1,47. Nés en 1954 à 59 ans : en emploi
86,102 % (femmes 100, hommes 84,404), chômage 0, absents 4,396, maladie ou
invalidité 4,562, retraités 4,941 ; de 50 ans au départ, passage direct 90,792 %
(100 ; 89,631), 95,088 sans l'inapte (100 ; 94,436), aucune interruption
intercalée, départ à 66 ans au plus tard.

**2.2. Les tests : conforme.** `python -m pytest
tests/test_controle_drees_panorama.py` : 40 réussis ; avec
`tests/test_drees_panorama.py` et `tests/test_drees_panorama_series.py` : 76
réussis, aucun sauté (les classeurs et le PDF sont en place, donc
`test_chaque_valeur_du_temoin_est_celle_de_sa_cellule` et
`test_chaque_citation_du_temoin_est_dans_le_pdf` ont tourné). Je lis les trois
tests neufs (lignes 733, 796 et 934) : chacun calcule la valeur du modèle
(`_moyenne_des_tetes` des cohortes, `trimestres_par_annee`, `age_liquidation`,
`_interruption`) et la compare à une cellule du témoin
(`temoin["valeurs"]["12_graphique_1"][…]`, `["15_graphique_5"]`,
`["15_graphique_6"]`, `["21_graphique_1"]`, `["21_tableau_2"]`) ; les nombres
du modèle (21,4 ; 38,3 ; 61,03 ; 62,09 ; 86 ; 91) ne sont que dans les
docstrings, jamais dans une assertion. Les seuls nombres littéraux des
assertions sont `0`, et des constantes de la source ou de sa définition :
quatre trimestres par année complète, 50 ans (le champ), 59 ans, 67 ans. Réserve, sans écart : le test
n'asserte que le sens, il ne rougirait donc pas si l'écart doublait ; la note le
dit (« le test n'asserte que le sens de l'écart »). Que les trois tests aient
été « vus rouges pour la raison attendue » (le témoin n'avait pas ses clés), je
ne peux pas le rejouer après coup ; le témoin du parent n'a bien aucune des 44
cellules, le rouge était donc un `KeyError`, non un rouge du modèle.

## 3. Les bornes des fiches 5 et 8, et la source de la fiche 21

**3.1. Les nouvelles bornes : conforme.** Dans les quatre tests de J (lignes 355,
551, 593 et 633), chaque borne est une cellule du témoin ou son sens : la
pension de la grille contre `publie[ligne]["pension"]` (sens +1 ou −1, au lieu
de rapports à ± 0,08) ; l'ensemble 2024 contre C15 (1 647) ; les évolutions
contre D15, E15 et F15 (3,9 ; 1,1 ; 3,7), par `|grille − publiée| < |publiée|`
(0,15 < 3,9 ; 0,26 < 1,1 ; 1,075 < 3,7, vérifiés plus haut) ; l'écart entre
femmes et hommes du régime général contre G5 (−27) et de l'Agirc-Arrco contre
G6 (−52) ; la part au minimum contre C21 (17,4), D8 (21), D7 (11) ; l'âge de
liquidation contre E12 de « F08_Tableau 3 » (62,6) ; la part d'inaptes contre
E9 (36) ; les pensions contre E7 (750) et K7 (1 830) de « F08_Tableau 4 » ;
au régime général des nés en 1953, la part de la grille entre D7 (12) et C7
(35) de « F08_Tableau 2 » ; cette part, je l'ai recalculée avec les fixtures du
test : 23,2465 %, soit les 23,25 % de la note. Je relis ces cellules : toutes
sont celles du témoin. Restent dans ces tests, sans que la note les compte, trois seuils
littéraux sur des cellules : `> 4` (G21, H21, I21 de « F08_Graphique 1 » : 4,5 ;
6,8 ; 23,5), `< 20` (J21 : 18,4) et `> 25` (D6 de « F08_Tableau 1 » : 30). Ils
bornent la source, non le modèle, et sont vrais. « Deux cinquièmes » et « 1,1 point » : points 1.4.

**3.2. Le champ du graphique 1 de la fiche 21 : écart, faible à moyenne.** La
source (B40 de « F21_Graphique 1 ») : « Champ > Personnes nées en 1942, 1946,
1950, 1954, 1958 ou 1962 ayant été affiliées au moins une fois … à l'EIC,
**hors absents et retraités dès 50 ans** » ; c'est mot pour mot le champ du
tableau 2 (B18 de « F21_Tableau 2 »). La note l'applique au tableau 2 (« Le
champ de la grille au tableau 2 ôte le militaire (48 ans) et l'agent de la
SNCF (50 ans) ») et le test du tableau 1 de l'étape 4 aussi (`50 <
age_liquidation`) ; mais elle mesure le graphique 1 sur les dix-huit cas types,
militaire et SNCF compris (744 485 têtes). Dans le champ de la source, avec la
règle même de la note (`age_liquidation > 50`, 724 164 têtes) : **en emploi
88,518 %** (hommes 87,071 ; femmes 100), chômage 0, absents 4,519, maladie ou
invalidité 4,690, **retraités 2,273** (hommes 2,560), au lieu de 86,102 ;
4,396 ; 4,562 ; 4,941. Le sens ne change pas (88,5 > 68,29 ; 0 < 7,55 ;
2,27 < 7,86 ; 4,52 < 9,71 ; 4,69 < 6,19) et le test reste vert ; mais le chiffre
que la note, la docstring et le suivi donnent (« 86,1 % », « 4,9 % retraités »)
n'est pas celui du champ de la source, et la note ne dit rien du champ du
graphique 1. À déclarer, avec les deux mesures.

## 4. Ce que la source ne tranche pas : déclaré ? (point 4 de la demande)

Les cinq points de la note sont bien des choses que la source ne tranche pas, et
sont déclarés ; la lecture de la source ajoute des précisions, toutes de
gravité négligeable :

- **« À 30 ans » (point 1 de la note).** Déclaré, les deux lectures sont
  mesurées (chaque cas type perd quatre trimestres sans l'année des 30 ans :
  52, 44, 40, 36, 32, 28 et 16 deviennent 48, 40, 36, 32, 28, 24 et 12, mes
  chiffres). Précision :
  la source penche pour la lecture que la grille retient ; l'âge est « atteint
  au 31 décembre de l'année » (B30) et le champ dit « présents sur le marché du
  travail avant 30 ans inclus ».
- **Ce que mesure « compl ».** Déclaré (point 5.3 de la note), mais l'annexe 3
  (folios 299-300) définit un « premier cas », la durée d'assurance tous
  régimes comparée à la durée requise pour le taux plein, et un « second », la
  proratisation, « retenu dans l'ouvrage » ; le titre de la feuille, « en
  fonction de la durée requise », nomme le premier, que son B27 et sa lecture
  contredisent. La note ne cite que la phrase « proche … sauf 1934 à 1948 ». La
  conclusion, que la source ne le tranche pas, tient : les données ne sont pas
  « proches » hors 1934-1948 (+4 à +7 points).
- **Le polypensionné au graphique 6.** « Le graphique 6 compte, par régime, les
  retraités de la caisse, polypensionnés compris » est rangé parmi ce que la
  source ne tranche pas, mais écrit comme un fait ; la source dit « retraités
  titulaires d'une pension de droit direct » (champ) et « données par caisse
  issues de l'EACR » (renvoi 4) : l'inférence est raisonnable, elle n'est pas
  écrite.
- **Les interruptions après 45 ans** (« les seules interruptions de la grille
  après 45 ans sont l'inactivité de l'inapte, dès 49 ans, et l'invalidité de
  l'ex-invalide, dès 46 ans ») : l'inapte a aussi un chômage indemnisé à 45 et
  48 ans (`castypes.py`, interruptions de 21 à 48 ans de trois en trois, puis
  l'inactivité dès 49). La conclusion tient : aucune interruption ne commence
  entre 50 ans et le départ, et aucun cas type ne finit au chômage.
- **Le tableau 5.1 de la note** (les huit cellules) omet, pour trois d'entre
  elles, le bloc qui les qualifie : L10 et N93 de la fiche 12 sont des
  *femmes* (C4 « Femmes » ; les hommes commencent en S4), et N93 est dans un
  bloc que la feuille intitule (A89) « VERSION R … (à oublier) » ; G12 de la
  fiche 8 est celui des femmes qui *ne* bénéficient *pas* du minimum contributif
  (F5:H5 sous C4:H4) ; D12 de la fiche 21 est la génération 1946 (B11). Et la
  note de « F11_Graphique 2 compl » dit « (voir annexe 4) », celle de la feuille
  voisine « (voir annexe 3) » : « est celle de la feuille voisine » vaut au
  numéro de l'annexe près. Aucune valeur, aucune conclusion n'en dépend.

**Conforme, sans écart** : les citations du PDF (folio 141 : « Le relèvement de
l'AOD pour les catégories actives de la fonction publique (de 55 à 57 ans avec la
réforme des retraites de 2010) » et l'intertitre « augmente de 1 an et 1 mois
entre les générations 1950 et 1957 » ; folio 142 : « Cet âge atteint ainsi 61 ans
et 7 mois pour la génération 1957, soit 1 an et 1 mois de plus que pour la
génération 1950 ») ; la contradiction de la fiche 15 (E36 = 61,85 ; B38 :
« 61,9 » ; S13 = 61,67 et E35 = 61,66 ; T13 = 61,88 et E36 = 61,85 ; E34 − E29 =
61,59 − 60,46 = 1,13) ; la remarque sur `castypes.py` (le commentaire du
fonctionnaire actif dit bien « départs de 2025 », tableau B-5, et la note dit
qu'elle ne l'a pas rouvert) ; le suivi (86,1 ; 90,8 ; 21,4 ; 38,3 ; 61,03 ; 62,09
justes) ; le message du commit (cinq lignes, auteur `noreply`) ; le candidat de
la note de l'action 138 : les lignes « Femme » de « Naissance-Résidence » sont
bien 18, 186 et 189 (K18 = 58,7 ; K186 = 40,0 ; K189 = 1,8), et la note de
l'étape 14 écrit 17, 185 et 188 (les lignes 185 et 188 sont des « Ensemble » :
40,0 et 1,6) ; ses valeurs sont justes.

## 5. Les cellules citées une à une

Plus de soixante-dix cellules, avec la valeur lue (les 534 du témoin sont de
plus relues en bloc par `openpyxl` : 532 nombres égaux à 10⁻⁹ près, deux
libellés égaux). `fiche_11` ; « F11_Graphique 2 » : H25 58, C25 57, I25 72, D25
69, J25 65, E25 63, E15 58, E16 60 ; « F11_Graphique 2 compl » : H25 64, C25 63,
I25 77, D25 75, J25 70, E25 69, E15 58, E16 59. EIR 1953, « Naissance-Résidence » :
K17 65,1, L17 63,4, K18 58,7, L18 57,3, K19 72,2, L19 70,0. `fiche_12`, « F12_Graphique
1 » : C9 40,4, D9 45,2, E9 42,8, F9 19,3, G9 18,9, H9 19,1, K9 1,4, C10 40,1, D10
44, E10 42, F10 19,8, G10 19,3, H10 19,5, K10 1,9 ; E7 38,3 (génération 1942) ;
« F12_Graphique 2 », L10 58,7. `fiche_15`, « F15_Graphique 5 » : C29 60,9, D29
60,01, E29 60,46, C34 62, D34 61,15, E34 61,59, E35 61,66, E36 61,85 ;
« F15_Graphique 6 » : M6 61, R6 62,5, M8 60,4, R8 62,3, M10 59,2, R10 60,5, M11
46,8, R11 46,8, M12 59,1, R12 60, M13 60,46, R13 61,59, S13 61,67, T13 61,88, C12
58,7. `fiche_21`, « F21_Graphique 1 » : F34 68,29, E34 7,55, C34 9,71, G34 6,19, I34
7,86, F10 68,1, F22 68,47 ; « F21_Tableau 2 » : E5 58,35, C5 54,87, D5 61,74, E8
19,27, E14 4,81 ; « F21_Tableau 1 REVISIONS » D12 58,73 ; « F21_Tableau 2 REVISIONS »
E8 58,68. `fiche_05`, « F05_Graphique 1 » R8 58,7089 ; « F05_Tableau 2 » : C15 1 647,
D15 3,9, E15 1,1, F15 3,7, G5 −27, G6 −52. `fiche_08` : « F08_Tableau compl encadré
2 » G12 58,6854 ; « F08_Tableau encadré 2 » F30 503 942, C30 788 666 ; « F08_Tableau 2 »
C7 35, D7 12. Toutes égales à ce que la note, le suivi et le témoin en écrivent.

## Candidats, hors de cette tâche

- Des tests de l'étape 4, que la note de J ne dit pas toucher, gardent des
  bornes tirées de la mesure du modèle et non de la cellule : fiche 4
  (`0.25 < … < 0.6`, `8.0 < … < 11.0`, `3.0 < … < 9.0`), fiche 7
  (`1.2 < … < 1.4`), fiche 11 (`0.03 < … < 0.06`), fiche 18
  (`1.15 < … < 1.45`), fiche 21, tableau 1 (`15 < … < 21`, `0.4 < … < 0.6`,
  `0.65 < … < 0.9`).
- Le suivi dit la fiche 15 `confronte` alors que ses graphiques 2 et 7 ne le
  sont pas ; il le dit en toutes lettres (« Restent, sans confrontation ») : un
  statut, pas une erreur.

*Ce que je n'ai pas fait* : rejouer les tests de J « vus rouges » ; rouvrir le
tableau B-5 du jaune pensions du PLF 2027 (que J n'a pas rouvert non plus) ;
lancer la suite complète, que GitHub lance.
