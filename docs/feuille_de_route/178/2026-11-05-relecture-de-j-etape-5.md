# Relecture de J, étape 5 : les chiffres des fiches 5 et 8 du panorama, revérifiés aux classeurs de la DREES

**Verdict : les chiffres sont conformes.** Les 283 valeurs du témoin de J, et
dix-neuf autres du même fichier, sont celles des cellules des classeurs, une à
une ; chaque pension, chaque part et chaque évolution de la grille que la note
donne, je les ai recalculées et retrouvées à l'identique ; les citations du PDF
sont mot pour mot, aux folios dits. Quelques écarts, tous de rédaction ou de
déclaration, aucun de chiffre : trois touchent à ce que la source ne tranche
pas, de gravité faible, l'un faible à moyenne (points 5.1 à 5.3) ; quatre
autres sont négligeables (5.4) ; une réserve de forme sur les bornes des
tests (point 2).

**La demande.** Vague 9, file R-J, le 5 novembre 2026 : revérifier, contre les
sources et sans se fier à J ni à la mémoire, le commit `bd130db` de la session
`session_01FVFLAmPoFfjQwSx8Bqg7kN` et sa note
`2026-11-05-etape-5-fiches-5-et-8.md`. Rien n'est modifié : ni règle, ni
donnée, ni test. Les écarts se décrivent ici ; une correction irait dans une
note neuve.

**Les sources, ouvertes pour cette relecture.** Le dépôt n'avait pas les
classeurs (`data/brut/` vide, la note le dit à demi-mot) :
`python scripts/fetch/source_locale.py --recuperer` les a rapportés de la
release `documents-apportes`, le PDF du miroir de l'UNSA et l'archive des
trente-six classeurs, aux empreintes du manifeste, que `sha256sum` retrouve :
PDF `9eb36a06…735e9be`, archive `ec7503f8…aaf64911`, celles que la note de J
cite. Je lis les classeurs avec `openpyxl` (`data_only`), non avec
`lecture_xlsx`, le lecteur de J : les deux lectures sont indépendantes. Le PDF
passe par `pdftotext`, page à page (la page du fichier est l'imprimée plus un).

## 1. Les cellules des classeurs contre la note : conforme

Soixante-dix cellules citées une à une, avec la valeur que la note en écrit
(toutes égales) ; le fichier est `fiche_05.xlsx`, `fiche_08.xlsx` ou
`fiche_11.xlsx` de l'archive.

**Fiche 5, « F05_Tableau 2 »** (pension brute mensuelle de droit direct, hors
majoration pour trois enfants ou plus, 2024, résidents en France ou à
l'étranger ; évolutions en euros constants, corrigées du glissement de
décembre : renvoi 6, B16) :

| cellule | valeur | cellule | valeur | cellule | valeur |
|---|---|---|---|---|---|
| C5 régime général | 777 | C10 FPE civils | 2 342 | C14 prof. libérales | 1 369 |
| C6 Agirc-Arrco | 542 | C11 Ircantec | 149 | C15 ensemble | 1 647 |
| C7 MSA salariés | 301 | C12 CNRACL | 1 470 | D5 / E5 / F5 | 4,4 / 1,2 / 2,8 |
| C8 MSA NS, base | 438 | C13 rég. spéciaux | 1 888 | D15 / E15 / F15 | 3,9 / 1,1 / 3,7 |
| C9 MSA NS, compl. | 137 | E13 / F13 | 1,4 / 9,6 | E9 / F9 | 41,5 / 71,6 |
| G5 / G6 / G15 | −27 / −52 / −35 | D12 / E12 / F12 | 3,6 / −2,3 / −4,4 | F6 | −2,9 |

Les renvois de la note sont justes : renvoi 5 « Professions libérales :
CNAVPL, CNBF » (B16), renvoi 4 pour les régimes spéciaux.

**Fiche 5, « F05_Tableau 4 »** (fin 2024, résidents en France, majoration
comprise, arrondi à la dizaine : B2 et la Note) : H6 2 100, H8 2 020, H10
2 750, H11 2 920, H12 2 010, H14 2 970, H16 1 040, H17 3 220, les huit de la
colonne « carrières complètes ensemble » que la note oppose à la grille. Le
renvoi 5 (B22) dit : « La carrière est considérée comme complète si la durée
d'assurance tous régimes est au moins égale à la durée requise pour le taux
plein (dans un des régimes d'affiliation au moins). »

**Fiche 8, « F08_Graphique 1 »** (ligne 21, « 2024 (p) » ; B23 : « Pour le
régime général et la MSA salariés, les valeurs pour 2024 sont estimées ») :
C21 17,4, D21 35,6, G21 4,5, H21 6,8, I21 23,5, J21 18,4.

**Fiche 8, « F08_Tableau 1 »** (nés en 1953, résidant en France, vivants au
31 décembre 2020, EIR 2020 : Champ) : D8 21, C8 25, D6 30, C6 34, D7 11, C7 15.
**« F08_Tableau 2 »**, colonne E : E7 25 (régime général), E11 22 (CNRACL),
E14 27 (MSA non-salariés), E8 6 (État civil), E9 10 (militaires), E12 1
(régimes spéciaux). **« F08_Tableau 3 »** : E12 62,6 et K12 61,6 (âge de
liquidation moyen), E9 36 (inaptitude ou invalidité). **« F08_Tableau 4 »** (le
nom de la feuille porte une espace finale) : E7 750 et K7 1 830 (pension de
droit direct, majoration pour trois enfants comprise : Note B17).

**Fiche 8, « F08_Tableau encadré 2 »** : C30 788 666, D30 55,6369…, F30
503 942, G30 45,7853…, et la ligne 2023 : C29 20 281, D29 63,718…, E29
727,515…. Le calcul de la note, (788 666 × 55,64 + 503 942 × 45,79) × 12 =
803,48 millions d'euros, je le refais : 803 482 565 ; avec les valeurs non
arrondies des cellules, 803 424 732. « De l'ordre de 0,8 milliard » tient.
La coquille est établie : la lecture de la feuille (B32) dit « ayant liquidé
leurs droits en 2020 », pour les valeurs de la ligne 2023 ; le PDF, folio 82,
dit « en 2023 » (et son total : 788 666, 56, 731, 503 942, 46, 854, les
arrondis des mêmes cellules).

**Fiche 11** : « F11_Graphique 2 », C25 57 (femmes nées en 1953, ensemble des
retraités) et H25 58 (résidentes en France) ; « F11_Graphique 2 compl », C25 63
et H25 64. Les colonnes sont celles que la note dit (C7 « Femmes », H7 « Femmes »
sous « Retraités résidant en France »).

## 2. Les cinq tests : conformes, avec une réserve sur les bornes

Lancés le 5 novembre 2026 sur `origin/main` (8a460df), avec les tests du
témoin et des citations et celui qui nomme les confrontations :
`python -m pytest tests/test_controle_drees_panorama.py -k "sert_trop_a_chaque_regime
or tableau_4_de_la_fiche_5 or porte_au_minimum_trop or met_au_minimum_ses_hommes
or beneficiaires_du_minimum_de_la_grille or chaque_valeur_du_temoin or
chaque_citation_du_temoin or nomme_ses_confrontations"` : **11 passed**, aucun
sauté (les classeurs et le PDF étaient là).

D'où vient la valeur attendue de chacun :

- `test_le_tableau_4_de_la_fiche_5_est_le_tableau_3_2_du_cor` : **de la
  source seule**. Il compare, valeur pour valeur, les 90 du classeur (témoin)
  et celles du COR (`cor_pension_regime_principal_2026.json`) : deux sources
  qui se recoupent, aucune sortie du code. J'ai relu les 90 cellules au
  classeur (point 3).
- `test_la_grille_sert_trop_a_chaque_regime_…`,
  `…_porte_au_minimum_trop_…`, `…_met_au_minimum_ses_hommes_…`,
  `…_beneficiaires_du_minimum_de_la_grille_touchent_trop` : **la valeur
  publiée vient du classeur** (par le témoin, relu cellule à cellule), et le
  test n'asserte sur elle que par un rapport borné. **Les bornes, elles, sont
  la mesure du modèle** : « rapport mesuré le 5 novembre 2026 » à ± 0,08
  (`TABLEAU_2_DE_LA_FICHE_5`), 1,25 à 1,55 pour le régime général, 2,6 à 3,4
  pour les hommes, et le jeu des trois cas types au minimum, que le test
  fixe tel que le code le rend. C'est la convention du dépôt de l'« écart
  déclaré » : le test épingle l'écart que la note décrit, il ne dit pas ce
  que le modèle devrait donner. Au sens strict de la règle « la valeur
  attendue vient de la source, jamais de ce que rend le code », ces bornes
  n'y sont pas ; la source de ce qui est confronté, elle, y est. **Gravité :
  faible**, et sans conséquence : si le modèle bouge, le test rougit et
  l'écart se re-déclare ; si la source change, le témoin rougit.

## 3. Les 283 valeurs du témoin : conformes

Plus que les vingt demandées : je les ai comparées **toutes**, par mon propre
lecteur. Le témoin porte 283 cellules pour les clés de J (`05_tableau_2` 55,
`05_tableau_4` 90, `08_graphique_1` 18, `08_tableau_1` 33, `08_tableau_2` 30,
`08_tableau_3` 33, `08_tableau_4` 15, `08_encadre_2` 9 : le compte de la note),
et dix-neuf de plus que d'autres étapes y ont mises (fiche 11 : 16, 2 et 1).
Les 302 sont égales à leur cellule, au bit près, sans un seul écart. Un
échantillon de vingt-quatre, toutes les onze cellules à partir de la
quatrième, avec le chemin du témoin :

| chemin du témoin | feuille, cellule | témoin | classeur |
|---|---|---|---|
| 05_tableau_2 / régime général, évol. 2014-2024 | F05_Tableau 2, F5 | 2,8 | 2,8 |
| 05_tableau_2 / MSA salariés, écart F/H | F05_Tableau 2, G7 | −13 | −13 |
| 05_tableau_2 / FPE civils, pension | F05_Tableau 2, C10 | 2 342 | 2 342 |
| 05_tableau_2 / CNRACL, évol. 2023-2024 | F05_Tableau 2, D12 | 3,6 | 3,6 |
| 05_tableau_2 / prof. libérales, évol. 2020-2024 | F05_Tableau 2, E14 | −6,9 | −6,9 |
| 05_tableau_4 / ensemble, carr. complètes, femmes | F05_Tableau 4, F6 | 1 770 | 1 770 |
| 05_tableau_4 / régime général, tous, ensemble | F05_Tableau 4, E8 | 1 610 | 1 610 |
| 05_tableau_4 / FPE civils, tous, hommes | F05_Tableau 4, D10 | 2 820 | 2 820 |
| 05_tableau_4 / CNRACL, tous, femmes | F05_Tableau 4, C12 | 1 790 | 1 790 |
| 05_tableau_4 / MSA salariés, carr. complètes, ensemble | F05_Tableau 4, H13 | 2 070 | 2 070 |
| 05_tableau_4 / autre non-salarié, carr. complètes, hommes | F05_Tableau 4, G15 | 1 670 | 1 670 |
| 05_tableau_4 / prof. libérales, carr. complètes, femmes | F05_Tableau 4, F17 | 2 540 | 2 540 |
| 05_tableau_4 / monopensionnés, tous, ensemble | F05_Tableau 4, E19 | 1 680 | 1 680 |
| 08_graphique_1 / régime général, 2013 | F08_Graphique 1, C10 | 25,3 | 25,3 |
| 08_graphique_1 / régime général, 2024 | F08_Graphique 1, C21 | 17,4 | 17,4 |
| 08_tableau_1 / toutes carrières, hommes, rég. principal | F08_Tableau 1, D7 | 11 | 11 |
| 08_tableau_1 / carrières complètes, hommes, au moins un régime | F08_Tableau 1, C11 | 10 | 10 |
| 08_tableau_1 / monopensionnés à carrière complète, hommes | F08_Tableau 1, C15 | 4 | 4 |
| 08_tableau_2 / régime général, ensemble | F08_Tableau 2, E7 | 25 | 25 |
| 08_tableau_2 / CNRACL, hommes | F08_Tableau 2, D11 | 20 | 20 |
| 08_tableau_3 / inaptitude, aucun minimum | F08_Tableau 3, K9 | 8 | 8 |
| 08_tableau_3 / part non cotisée, rég. principal | F08_Tableau 3, E17 | 29 | 29 |
| 08_tableau_4 / équivalent carrière complète, aucun minimum | F08_Tableau 4, K9 | 1 890 | 1 890 |
| 08_encadre_2 / sans minimum contributif, majoration | F08_Tableau encadré 2, G30 | 45,78525145750899 | 45,78525145750899 |

## 4. Les écarts de la note : refaits à la main, conformes

Les chiffres de la grille eux-mêmes, hors tests, j'ai recalculés avec les
fonctions du dépôt (`_servie_par_regime`, `_moyenne_de_la_grille` du fichier
de tests, sur `GRILLE_DU_COUT`) : 937,65 ; 853,25 ; 726,47 ; 209,40 ; 2 226,85 ;
220,76 ; 1 118,22 ; 2 407,81 ; 1 913,93 tous régimes ; 844,62 et 1 369,57 aux
professions libérales (somme : 2 214,19) ; les évolutions 2023-2024, 2020-2024
et 2014-2024 de chaque régime (RG 5,0 / 2,7 / 5,6, CNRACL 3,8 / −0,7 / −1,6,
régimes spéciaux 3,0 / −2,5 / −4,4…) ; 1 328,89 et 878,98 au régime général,
497,48 et 953,58 à l'Agirc-Arrco : **tous ceux de la note, au centime**.
Les rapports, à la main, à partir d'elles et des cellules du point 1 :

- régime général : 937,65 / 777 = 1,2067, soit +20,7 %, **21 %** ; « 938
  contre 777 » : 937,65 arrondi à 938 ✓ ;
- MSA non-salariés, base : 726,47 / 438 = 1,6586, soit +65,9 %, **66 %** : le
  haut de la fourchette ; Agirc-Arrco 853,25 / 542 = 1,574 (+57,4 %), MSA
  compl. 1,528, Ircantec 220,76 / 149 = 1,482, régimes spéciaux 2 407,81 /
  1 888 = 1,275 : tous entre 21 et 66 ✓ ;
- État civil : 2 226,85 / 2 342 = 0,9508, soit **−4,9 %**, « −5 % » ✓ ;
- CNRACL : 1 118,22 / 1 470 = 0,7607, soit **−23,9 %**, « −24 % » ✓ ;
- tous régimes : 1 913,93 / 1 647 = 1,1621, « 16 % de plus » ✓ ; évolutions
  de 3,75 contre 3,9, de 1,36 contre 1,1, de 4,78 contre 3,7 : écarts de 0,15,
  0,26 et 1,08 point ✓ ;
- les évolutions par régime : régimes spéciaux, 2014-2024, −4,4 − 9,6 =
  **−14,0 points**, MSA non-salariés base −0,3 → +7,5, soit **+7,8**, « +8 » ✓ ;
- femmes et hommes : 1 328,89 / 878,98 = 1,5119, **+51,2 %** ; 497,48 /
  953,58 = 0,5217, **−47,8 %** ✓ ;
- la fiche 8 : 1 044,0 / 750 = 1,392 (« deux cinquièmes de plus », 39 %) ;
  2 136,9 / 1 830 = 1,1677 (« un sixième », 16,7 %) ; 32,64 / 11 = 2,97 (« trois
  fois ») ; 29,09 / 21 = 1,385 ✓.

Les parts de la fiche 8, recalculées de même (`controle_eacr.controle`,
`Simulateur.pour_la_projection`) : régime général 24,19 %, dont Cnav seule
30,24 % (442 091 têtes), État civil 0 %, militaires 0 %, CNRACL 0 %, MSA
non-salariés 100 % ; nés en 1953, 788 082 têtes, 29,09 % ensemble, 0 % des
femmes, 32,64 % des hommes, régime général 23,25 %, CNRACL 76,31 % ; âges de
liquidation 61,28 et 62,06 ; répartition des bénéficiaires 37,3 / 32,5 / 15,1
/ 15,05 % : **tous ceux de la note**. `scripts/part_minimum_contributif.py
--grille reference` donne bien dix-huit carrières et, en 2024, 10,8 % au
minimum, 0,0 % des femmes, 12,0 % des hommes.

## 5. Ce que la source ne tranche pas : déclaré en partie

La note déclare bien : la complémentaire des professions libérales, le
glissement de décembre, la part de l'indice et du renouvellement dans l'écart
des évolutions, et que l'annexe 3 retient la proratisation quand le tableau 4
retient la durée d'assurance. Ces citations sont exactes : page 299, « Dans
cet ouvrage, la carrière d'un assuré est dite complète si la somme des
coefficients de proratisation dans ses régimes de base est supérieure ou égale
à 100 %. Il s'agit de l'une des définitions possibles » ; page 300, « Cette
définition est celle retenue dans l'ouvrage » ; page 60, le renvoi 5 du
tableau 4 ; page 82, la coquille. Quatre choses manquent ou sont inexactes :

**5.1. « Ni dans aucune cellule de ses trente-six classeurs, cherché à 0,05
près » est faux à la lettre. Gravité : faible** (le fond tient). Huit cellules
valent 58,7 à 0,05 près : `fiche_05` « F05_Graphique 1 » R8 (58,709, la
pension nette moyenne de l'ensemble des retraités en % du revenu d'activité
net moyen, 2023), `fiche_08` « F08_Tableau compl encadré 2 » G12 (58,685, un
montant moyen de majoration en euros, liquidants de 2005), `fiche_12`
« F12_Graphique 2 » L10 (58,7, le rythme de validation des femmes de la
génération 1950, de 30 à 49 ans) et « Graphique 2 (2) » N93 (le même
rythme, génération 1950, colonne « Entre 30 et 49 ans », lu dans un autre
bloc de la feuille), `fiche_15` « F15_Graphique 6 » C12 et D12 (58,7, l'âge
moyen de départ à la CNRACL des générations 1940 et 1941), `fiche_21`
« F21_Tableau 1 REVISIONS » D12 (58,73, la part « en emploi » de l'ensemble
l'année avant la liquidation) et « F21_Tableau 2 REVISIONS » E8 (58,68, le
passage direct de l'emploi à la retraite, génération 1950). **Aucune des huit
ouvertes n'est une part de carrières complètes**, et le PDF n'a
pas « 58,7 » : l'affirmation que le chiffre n'est pas dans le panorama tient,
mais la phrase aurait dû dire « aucune cellule qui soit une part de
carrières complètes ».

**5.2. D'où vient le 58,7 % n'est pas dit. Gravité : faible.** La note de
l'action 138, étape 14 (`2026-11-05-etape-14-calage-de-la-duree-des-femmes.md`,
tableau, ligne 17), le donne : c'est l'« EIR 2020, caractéristiques des
retraités nés en 1953 », feuille « Naissance-Résidence », « Part d'assurés à
carrière complète (en %) », femmes résidentes en France, 58,7 — un autre
fichier de la DREES (jeu 3013), que le panorama n'embarque pas. La note de J
l'appelle « introuvable » sans dire qu'il a une source ailleurs, ni qu'il ne
se range pas sur la fiche 11 : **58,7 s'arrondit à 59, la cellule H25 des
résidentes dit 58**, et la définition de la carrière complète du fichier de
3013, la note de l'action 138 le dit, n'est pas donnée. (Je n'ai pas rouvert
ce fichier ici : seule la note de l'action 138 en est le témoin ; ce que je
vérifie, c'est que le panorama n'a pas ce chiffre et que H25 vaut 58.)

**5.3. La feuille « F11_Graphique 2 compl » n'est pas ce que la note laisse
croire. Gravité : faible à moyenne**, parce que ses 63 % et 64 % sont écrits
« au sens de la durée requise » comme un fait. Son titre (B2) dit « en
fonction de la durée requise » ; mais sa Note et sa Lecture (B27, copiées de la
feuille voisine) disent « la somme des coefficients de proratisation… (voir
annexe 4) » et « au sens de la proratisation à 100 % ». Et les deux séries
ne se comportent pas comme l'annexe 3 le dit : elle écrit que les deux
proportions sont proches « sauf pour les générations 1934 à 1948 », or
l'écart de l'ensemble (compl moins proratisation) est de 4 à 5 points de 1926
à 1934, de 0 à 2 points de 1938 à 1944, et de **6 à 7 points de 1947 à 1953**,
la génération de la question (femmes nées en 1953 : 57 contre 63 ; résidentes
58 contre 64). La note de J cite « surtout pour les générations 1934 à 1948 »
sans le dire. Ce que mesure la feuille « compl » — et si le 63 est la durée
d'assurance requise atteinte — est donc ce que la source ne tranche pas, et
c'était à ajouter à « Ce que la source ne tranche pas ». Le 57 % de la
fiche 11 est, lui, la proratisation, sans doute possible (B2 et la Lecture).

**5.4. Négligeables.** (a) **552 626 têtes** du régime général : la somme
exacte des huit cas types est 552 624,9, soit 552 625 ; 552 626 est la somme
des huit parts arrondies (40 445 + 86 067 + 92 458 + 70 090 + 91 168 + 96 351 +
38 728 + 37 319) ; un écart d'une tête sur 552 625. (b) « La grille n'a pas
de majoration pour enfants » : elle n'a aucun cas type à trois enfants ou
plus, donc aucune majoration de 10 % de la pension, ce qui est ce que le
tableau 2 exclut ; mais `carriere_interrompue` a deux enfants, dont les
trimestres de majoration de durée sont dans sa pension : la phrase vaut pour
la majoration pour trois enfants, non pour tout l'effet des enfants. (c)
La docstring du test des nouveaux retraités dit « un tiers de trop » pour
24,19 % contre 17,4 % : le rapport est 1,39, « deux cinquièmes ». (d) **Dans
la source** : au tableau de l'encadré 2, la somme des cellules F6:F29 est
503 936, quand F30 et le total du PDF disent 503 942 (la colonne C, elle, se
somme bien à 788 666) : six unités d'écart, qui ne changent pas l'ordre de
grandeur du calcul.

## 6. Les affirmations sur le modèle, hors de la source, revérifiées

- **« Le coût ne sert pas la majoration exceptionnelle de 2023 au stock »** :
  `grep -i exceptionnelle src/retraite_notionnelle/cout.py` ne trouve rien ;
  `RevalorisationServie` (`revalorisation.py`, ligne 1595 à la fin) ne nomme
  que « majorations forfaitaires » de 1972 à 1982, pas celle de 2023. Exact.
- **« L'échéancier du salarié au Smic de la génération 1955 l'inscrit au 1er
  septembre 2023, 1 199,88 euros par an »** : relu au journal de
  `proj.echeancier(cas.construire(proj, 1955))` pour `smic_carriere_complete` :
  composante `majoration_exceptionnelle_regime_general`, effet au
  2023-09-01, montant annuel 1 199,88 EUR, « loi n° 2023-270, article 18, V :
  100,00 € par mois au prorata de la durée cotisée, 99,99 € sous les
  plafonds ». Exact. Aucun test ne la couvre ; la note le range en
  « candidat », ce qui est juste.
- **« Aucune source plus fine que “40 ans et plus” pour la durée validée des
  femmes »** : les titres des trente-six classeurs ne donnent, sur la durée,
  que des moyennes (fiche 11, graphiques 1, 3 et 4 ; fiche 12, graphique 4 ;
  fiche 14, tableau 2 pour les durées requises), et la fiche 28, tableau 4, a
  bien les lignes « ayant validé moins de 80 trimestres (20 années) » et « plus
  de 160 trimestres (40 années) » (B12, B13) pour les allocataires du minimum
  vieillesse seuls. Exact.

## Ce que cette relecture ne fait pas

Elle ne revérifie ni l'EIR 2020 des nés en 1953 (jeu 3013 de la DREES), dont
le 58,7 % ne vient que de la note de l'action 138, ni le tableau 3.2 du COR
(le test dit que ses quatre-vingt-dix valeurs sont celles du classeur, et le
classeur est relu ici), ni les fiches 12, 15 et 21, ni les pages du site. Elle
ne mesure pas la population de `grille_large.py`, que J n'a pas mesurée non
plus. Candidats pour le propriétaire : aucun nouveau défaut du modèle ; les
écarts 5.1 à 5.3 se corrigent par une ligne dans la note qui reprendra
l'étape 5, sans rien changer aux chiffres.
