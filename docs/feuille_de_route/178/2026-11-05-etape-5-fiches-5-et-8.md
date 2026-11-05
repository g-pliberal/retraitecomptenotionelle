# Étape 5, les fiches 5 et 8 : la pension par régime et les minima de pension, confrontés à la grille

**Reprise, au 5 novembre 2026.** Fait (cette note) : les fiches 5, par
régime (tableaux 2 et 4), et 8, confrontées à la grille de la page Coût,
chacune par un test du niveau `controle`, les 283 valeurs au témoin de
l'étape 4 ; au suivi, les deux fiches passent à `confronte`. Reste à l'étape
5 : les trois erreurs du coût de la note des règles (3 novembre) ; deux
candidats de plus pour le propriétaire, plus bas « Au propriétaire » ; les
fiches 12, 15 et 21 et le solde du suivi, que l'orchestration confie à
d'autres sessions. Par quoi commencer : la note des règles. Détail : plus
bas.

**La demande.** File J, le 5 novembre 2026 : confronter au modèle les fiches
5 (par régime : tableaux 2 et 4) et 8 du panorama de la DREES, édition 2026,
et elles seules ; chercher dans le PDF la définition de la « carrière
complète » de la DREES, et une source plus fine que « 40 ans et plus » pour
la durée validée des femmes (question de la file I). Aucune règle ne change :
un écart se décrit.

**La source, ouverte.** Le site de la DREES répondait 503 le 5 novembre,
selon la consigne de l'orchestration, qui n'a pas été éprouvé ici :
`python scripts/fetch/source_locale.py --recuperer` a rapporté l'archive des
classeurs de la release `documents-apportes`, empreinte
`ec7503f8…aaf64911`, et le PDF du miroir de l'UNSA, `9eb36a06…735e9be`,
celles du manifeste. Chaque valeur est lue par `lecture_xlsx`, le lecteur du
dépôt, à sa cellule, et recopiée au témoin
`tests/temoins/drees_panorama_2026_confrontations.json` (clés `05_tableau_2`,
`05_tableau_4`, `08_graphique_1`, `08_tableau_1` à `08_tableau_4`,
`08_encadre_2`) ; `test_chaque_valeur_du_temoin_est_celle_de_sa_cellule` les
relit au bit près, et `test_chaque_citation_du_temoin_est_dans_le_pdf`, les
trois phrases ajoutées. Les pages sont celles imprimées (folio), la page du
fichier PDF étant la suivante.

**La mesure.** La grille de la page Coût, au scénario 1, comme
`controle_eacr.controle` la prend : chaque cohorte de chaque cas type, pesée du
poids de son cas type fois son effectif INSEE. La pension qu'un régime sert,
par `cout._masses_regimes` : sa masse sur ses têtes, en 2014, 2020, 2023 et
2024, rangées sous le régime de tête de `RevalorisationServie`. La pension
tous régimes, par `controle_eacr.cohortes`. Tout est porté en euros de 2024
(ou de 2020 pour la fiche 8, tableaux 3 et 4) par `coefficient_prix`, qui
suit l'indice des prix en moyenne annuelle (`ipc_annuel.csv`) ; la DREES
corrige ses évolutions par le glissement de décembre (renvoi 6 du tableau 2).
Une pension est au minimum quand le droit lui applique un des avantages de
`MINIMA_DE_PENSION` (minimum contributif, minimum garanti, pension majorée de
référence, complément différentiel, minimum de la SNCF), chacun inscrit
seulement s'il relève la pension (`droit/completer.py`, ligne 1969 pour le
minimum garanti), lu au jumeau Python (`Simulateur.pour_la_projection`),
comme `scripts/part_minimum_contributif.py` le lit.

**Fiche 5, tableau 2** (feuille « F05_Tableau 2 », brut, droit direct hors
majoration pour enfants, 2024, résidents en France ou à l'étranger ; la
grille n'a pas de majoration pour enfants). Pension mensuelle en euros, puis
évolution en euros constants, en %, la grille d'abord :

| régime | publiée | grille | rapport | 2023-2024 | 2020-2024 | 2014-2024 |
|---|---|---|---|---|---|---|
| régime général | 777 (C5) | 937,65 | 1,207 | +5,0 / +4,4 (D5) | +2,7 / +1,2 (E5) | +5,6 / +2,8 (F5) |
| Agirc-Arrco | 542 (C6) | 853,25 | 1,574 | +3,0 / +1,1 (D6) | +1,3 / +0,2 (E6) | +4,1 / −2,9 (F6) |
| MSA non-salariés, base | 438 (C8) | 726,47 | 1,659 | +4,0 / +4,1 (D8) | +1,9 / +1,6 (E8) | +7,5 / −0,3 (F8) |
| MSA non-salariés, compl. | 137 (C9) | 209,40 | 1,528 | +8,5 / +2,2 (D9) | +26,9 / +41,5 (E9) | +59,7 / +71,6 (F9) |
| État, civils | 2 342 (C10) | 2 226,85 | 0,951 | +3,5 / +4,0 (D10) | −0,1 / −1,2 (E10) | +2,1 / −3,4 (F10) |
| Ircantec | 149 (C11) | 220,76 | 1,482 | +5,9 / +5,0 (D11) | +6,9 / +2,9 (E11) | +14,8 / +12,6 (F11) |
| CNRACL | 1 470 (C12) | 1 118,22 | 0,761 | +3,8 / +3,6 (D12) | −0,7 / −2,3 (E12) | −1,6 / −4,4 (F12) |
| régimes spéciaux | 1 888 (C13) | 2 407,81 | 1,275 | +3,0 / +4,6 (D13) | −2,5 / +1,4 (E13) | −4,4 / +9,6 (F13) |
| tous régimes | 1 647 (C15) | 1 913,93 | 1,162 | +3,75 / +3,9 (D15) | +1,36 / +1,1 (E15) | +4,78 / +3,7 (F15) |

L'État civil ne compte que les trois cas types de la caisse
`fonction_publique_etat_civile`, sans le militaire ; les régimes spéciaux réunissent la SNCF et les IEG, chacune à ses têtes. La
grille n'a pas de salarié agricole (C7, 301 euros) ; aux professions
libérales (C14, 1 369 euros ; renvoi 5 : « CNAVPL, CNBF »), elle sert 844,62
euros de base et 2 214,19 de base et de complémentaire : la source ne dit pas
ce que la ligne compte de complémentaire, et la publiée tombe entre les deux.

*Les écarts et leur cause.* La grille sert trop à chaque régime, de 21 à 66
%, sauf à l'État civil et à la CNRACL : elle compte des têtes de caisse à
carrière complète, quand le régime moyenne aussi les petites pensions de ses
polypensionnés, que la grille n'a pas (fiche 13, déjà déclaré), et des
carrières courtes (fiche 11) ; à l'État et à la CNRACL, ses cas types sont
des carrières modestes de leur régime, ce que `test_controle_ancetre.py`
disait déjà (« la catégorie B, l'aide-soignant, le militaire du rang »). Les évolutions de chaque régime s'écartent dans les deux sens,
de −14 points (régimes spéciaux, 2014-2024) à +8 (MSA non-salariés, base) :
la revalorisation de chaque régime étant celle du panorama
(`test_les_revalorisations_du_panorama_sont_celles_du_depot`), l'écart tient
à ce qui renouvelle le stock de la grille — ses cohortes, leurs poids — et à
l'indice des prix ; la source ne permet pas de séparer les deux. Tous
régimes, la grille suit la DREES à 0,15 point sur un an, 0,26 sur quatre,
1,08 sur dix. L'écart entre femmes et hommes (G) : au régime général, la
seule femme de la grille, à carrière interrompue, touche 1 328,89 euros et
ses hommes 878,98, +51,2 %, quand la DREES mesure −27 % (G5) : les hommes de
la grille y comptent les fonctionnaires, les contractuels et l'artisan, qui
n'y ont qu'une part ; à l'Agirc-Arrco, 497,48 contre 953,58, −47,8 %, pour
−52 % (G6) ; tous régimes, −5,0 % pour −35 % (G15), ce que les fiches 6 et 7
déclarent déjà.

**Fiche 5, tableau 4** (feuille « F05_Tableau 4 », C6:H20, fin 2024,
résidents en France, droit direct majoration comprise, arrondi à la
dizaine). Ses quatre-vingt-dix valeurs sont, une à une, celles du tableau 3.2
du rapport du COR de juin 2026 que le dépôt lit depuis le 16 octobre
(`tests/temoins/cor_pension_regime_principal_2026.json`), et
`test_controle_ancetre.py` les confronte déjà à la grille ; le test neuf ne
fait que recouper les deux sources. Pour mémoire, la grille par régime
principal (`controle_ancetre.controle()`, le 5 novembre), contre les
carrières complètes : tous régimes 1 946 euros pour 2 100 (H6), 0,93 ;
régime général 1 988 pour 2 020 (H8), 0,98 ; État civil 2 381 pour 2 750
(H10), 0,87 ; militaires 1 691 pour 2 920 (H11), 0,58 ; CNRACL 1 571 pour
2 010 (H12), 0,78 ; régimes spéciaux 2 453 pour 2 970 (H14), 0,83 ; MSA
non-salariés 883 pour 1 040 (H16), 0,85 ; professions libérales 2 266 pour
3 220 (H17), 0,70. *Une remarque sur la source* : ce tableau définit la
carrière complète par la durée d'assurance (renvoi 5, citée plus bas),
quand l'annexe 3 dit retenir dans l'ouvrage celle du coefficient de
proratisation ; les deux diffèrent surtout pour les générations 1934 à 1948.

**Fiche 8, graphique 1** (feuille « F08_Graphique 1 », ligne 21, « 2024
(p) », la part des nouveaux retraités de 2024 dont la pension est portée à
un minimum ; régime général et MSA salariés estimés). Les nouveaux retraités
de 2024 de la grille, rangés par la caisse de leur cas type :

| régime | publié | grille | têtes de la grille |
|---|---|---|---|
| régime général (Cnav, artisan, contractuel) | 17,4 % (C21) | 24,19 % | 552 626 |
| dont Cnav seule | | 30,24 % | 442 091 |
| MSA salariés | 35,6 % (D21) | aucun cas type | |
| État, civils | 4,5 % (G21) | 0 % | 20 945 |
| État, militaires | 6,8 % (H21) | 0 % | 12 299 |
| CNRACL | 23,5 % (I21) | 0 % | 24 939 |
| MSA non-salariés | 18,4 % (J21) | 100 % | 37 174 |

Au minimum : le salarié au Smic (génération 1965 de la grille, à 60 ans) et
l'inapte (1960, à 62 ans), au minimum contributif ; l'exploitant agricole
(1960, à 62 ans), au complément différentiel. La variante sédentaire du
fonctionnaire actif de la CNRACL (`fonctionnaire_actif~sedentaire`), seule
au minimum garanti, ne part pas en 2024. Les mêmes cas types, que
`scripts/part_minimum_contributif.py --grille reference` pèse aux personnes
de 2020 (dix-huit carrières), portent au minimum 10,8 % de leurs liquidants
du régime général de 2024, aucune femme et 12,0 % des hommes : la part
dépend des poids, faute de population. La population de
`scripts/grille_large.py` (`--grille population`) n'est pas mesurée ici :
lancée, la mesure tournait encore après trente-trois minutes, et a été
arrêtée.

**Fiche 8, tableaux 1 et 2** (nés en 1953, résidant en France, vivants fin
2020, EIR 2020 ; la grille, ses cohortes nées en 1953 vivantes en 2020,
788 082 têtes). Tous les minima de la grille sont dans le régime de la seule
caisse de son cas type : la colonne qui se compare est celle du régime
principal.

| | publié, régime principal | publié, au moins un régime | grille |
|---|---|---|---|
| ensemble | 21 % (D8) | 25 % (C8) | 29,09 % |
| femmes | 30 % (D6) | 34 % (C6) | 0 % |
| hommes | 11 % (D7) | 15 % (C7) | 32,64 % |

Par régime principal (« F08_Tableau 2 », colonne E) : régime général 25 %
(E7), grille 23,25 % ; CNRACL 22 % (E11), grille 76,31 % ; MSA non-salariés
27 % (E14), grille 100 % ; État civil 6 % (E8), militaires 10 % (E9),
régimes spéciaux 1 % (E12), grille 0 %.

**Fiche 8, tableaux 3 et 4** (même champ, colonnes E pour ceux qui ont un
minimum dans leur régime principal, K pour ceux qui n'en ont aucun). Les
bénéficiaires de la grille — le salarié au Smic, 37,3 % de leurs têtes, la
variante sédentaire du fonctionnaire actif, 32,5 %, l'inapte au Smic, 15,1 %, l'exploitant,
15,05 % — touchent 1 044,0 euros de 2020 par mois, pour 750 (E7), deux
cinquièmes de plus ; les autres, 2 136,9 pour 1 830 (K7), un sixième de
plus. Ils ont liquidé à 61,28 ans, pour 62,6 (E12), les autres à 62,06 pour
61,6 (K12) : les cas types partent au premier âge du taux plein. Partis pour
inaptitude ou invalidité : 15,1 % (l'inapte), pour 36 % (E9).

**Fiche 8, encadré 2** (« F08_Tableau encadré 2 », la majoration
exceptionnelle des petites pensions, à la CNAV, en 2024). 788 666
bénéficiaires au minimum contributif (C30), 55,64 euros bruts par mois en
moyenne (D30) ; 503 942 sans lui (F30), 45,79 euros (G30). Si chacun la
touche douze mois : (788 666 × 55,64 + 503 942 × 45,79) × 12 = 803 millions
d'euros en 2024. Le modèle la sert à une carrière : l'échéancier du salarié
au Smic de la génération 1955 l'inscrit au 1er septembre 2023, 1 199,88 euros
par an. Le coût, non : `cout.py` ne la nomme pas, ni `RevalorisationServie`
(`revalorisation.py`), et la masse du stock y est la pension du départ
revalorisée (`coefficient_servi`). Le coût calant sa masse de 2024 sur la
dépense observée (`controle_ancetre.py`, en tête), l'effet sur la page n'est
pas mesuré ici. *Une coquille du classeur* : sa lecture (B32) dit « ayant
liquidé leurs droits en 2020 » pour 20 281 bénéficiaires, 64 euros et 728
euros, les valeurs de la ligne 2023 (C29, D29, E29) ; le PDF dit « en 2023 »
(page 82).

**La carrière complète de la DREES** (question de la file I). Annexe 3,
« Notion de carrière complète », page 299 : « Dans cet ouvrage, la carrière
d’un assuré est dite complète si la somme des coefficients de proratisation
dans ses régimes de base est supérieure ou égale à 100 %. Il s’agit de l’une
des définitions possibles². » Page 300 : « Dans un premier cas, une carrière
complète peut être définie en comparant la durée d’assurance tous régimes
validée par un retraité avec la durée requise pour le taux plein de la
génération à laquelle il appartient. […] À l’échelle tous régimes, un
retraité est considéré comme bénéficiant d’une carrière complète si sa durée
d’assurance tous régimes est supérieure ou égale au nombre de trimestres
requis dans au moins un des régimes de base. Dans un second cas, en
référence à la durée de service, la carrière est considérée comme complète
si la somme des coefficients de proratisation dans les régimes de base est
supérieure ou égale à 100 %. Cette définition est celle retenue dans
l’ouvrage. La proportion de carrières complètes selon cette définition est
proche de celle du premier cas, sauf concernant les générations pour
lesquelles les durées requises pour le taux plein et les durées requises
pour une proratisation à 100 % diffèrent (générations 1934 à 1948). » Le
tableau 4 de la fiche 5 prend l'autre (renvoi 5, page 60) : « La carrière
est considérée comme complète si la durée d’assurance tous régimes est au
moins égale à la durée requise pour le taux plein (dans un des régimes
d’affiliation au moins). »

Le chiffre de 58,7 % n'est pas dans le panorama : ni dans le texte du PDF,
ni dans aucune cellule de ses trente-six classeurs, cherché à 0,05 près.
Pour les femmes nées en 1953, la fiche 11 (graphique 2, EIR 2020) donne 57 %
au sens de la proratisation (« F11_Graphique 2 », C25, résidant en France
ou à l'étranger), 58 % pour les résidentes (H25) ; au sens de la durée
requise, 63 % et 64 % (« F11_Graphique 2 compl », C25 et H25). Une source
plus fine que « 40 ans et plus » pour la durée validée des femmes n'y est
pas non plus : le panorama ne donne que des durées moyennes, par sexe et par
génération (fiche 11, graphique 3, que le dépôt lit du COR ; fiche 6,
tableau 1), et, pour les seuls allocataires du minimum vieillesse, les parts
de moins de 80 et de plus de 160 trimestres (fiche 28, tableau 4).

**Ce que la source ne tranche pas.** Ce que la ligne des professions
libérales du tableau 2 compte de complémentaire ; l'écart que fait, sur une
année, le glissement de décembre au lieu de la moyenne annuelle des prix,
que le dépôt ne porte pas ; la part, dans l'écart des évolutions par régime,
de l'indice et du renouvellement du stock.

**Au propriétaire, des candidats** (rien n'est corrigé). 1. Le coût ne sert
pas la majoration exceptionnelle de 2023 au stock, quand le modèle la sert à
une carrière : de l'ordre de 0,8 milliard d'euros par an selon l'encadré 2.
2. La grille n'a aucune femme au minimum, sert le minimum à tous ses
exploitants et à aucun fonctionnaire partant en 2024, et en met trois
quarts à la CNRACL chez les nés en 1953 : comme pour les fiches 7 et 18,
corriger la grille ou attendre la population de l'étape 14 de l'action 138
est le choix que l'étape 4 lui soumet déjà. La grille de la page n'est pas
touchée (décision 11).

**Les tests**, chacun vu rouge pour la raison attendue (le témoin ne portait
pas les fiches 5 et 8, le suivi les disait `a_confronter`), puis vert : dans
`tests/test_controle_drees_panorama.py`,
`test_la_grille_sert_trop_a_chaque_regime_sauf_aux_fonctionnaires`,
`test_le_tableau_4_de_la_fiche_5_est_le_tableau_3_2_du_cor`,
`test_la_grille_porte_au_minimum_trop_de_nouveaux_retraites_et_aucun_fonctionnaire`,
`test_la_grille_met_au_minimum_ses_hommes_nes_en_1953_et_aucune_femme`,
`test_les_beneficiaires_du_minimum_de_la_grille_touchent_trop`, et
`test_chaque_fiche_de_l_etape_4_nomme_ses_confrontations`, qui n'attend plus
que la fiche 15.
