# Relecture de la décote des générations nées depuis 1960

File R-I-ter, vague 6, le 3 novembre 2026 : relecture indépendante des commits
207cb53, 3a04aeb, e12fe03 et 9649199 (session `session_01FVFLAinvhicJVVKHFMBLJz`,
note `2026-11-03-etape-14-decote-depuis-1960-et-ecarts-de-r-i-bis.md`), action
138, étape 14, sur `main` à 9649199. Elle reprend la relecture R-I-bis
(`2026-11-03-relecture-corrections-de-la-relecture-r-i.md`) et la décision 17
du propriétaire (`130/2026-11-03-decisions-du-proprietaire.md`, § 17). Rien
n'est repris de la session I ni de mémoire. Seule cette note est écrite : ni
règle, ni donnée, ni test, ni script, ni bloc « Reprise ».

## Les sources, ouvertes ici

- *Le panorama de la DREES*, « Les retraités et les retraites – Édition 2026 »,
  téléchargé de son miroir (`retraites.unsa.org`, celui de `data/sources.yaml`) :
  9 983 866 octets, SHA-256 `9eb36a06…ad86735e9be`, recalculée, celle du
  manifeste. Lus : la fiche 17, p. 154 à 159 de l'ouvrage (p. 155 à 160 du PDF) ;
  la note 6, p. 155 ; le graphique 4, p. 158, ses notes et son champ.
- *Ses classeurs*, l'archive de la release `documents-apportes` :
  SHA-256 `ec7503f8…aaf64911`, recalculée, celle du manifeste ; `fiche_17.xlsx`,
  feuilles « F17_Graphique 4 » et « F17_Tableau compl - Decote », lues cellule
  par cellule.
- *La documentation de l'EACR*, pièce `documentationeacr_mai2026_pdf` du jeu
  `donnes_eacr` (titre du PDF : « Documentation EACR - version du 18 mai
  2026 ») : 830 452 octets, 40 pages, SHA-256
  `9ae672a82aeb115c60daef5c47098b3c3efaf14ba58a1853ae0d9280de98b8c2`. Lus : la
  table H, p. 24 ; la variable « Age » des tables B (« B-Taux_liq ») et D
  (p. 16 et 19) ; le
  champ de la caisse 0015 (p. 33 et 38).
- *Non ouvert : le classeur « 62 EACR diffusée Part 2 - version du 26 mai
  2026 »*. Le portail de la DREES coupe la connexion de ce conteneur dès la
  poignée de main TLS (`curl: (35) Recv failure: Connection reset by peer`,
  quatre essais) ; l'outil de lecture du web, qui a rendu la liste des pièces
  et la documentation, refuse les fichiers de plus de 10 Mo (« maxContentLength
  size of 10485760 exceeded »), et le classeur en fait 15,7. La table H est
  donc lue ici au témoin, `tests/temoins/drees_eacr_tables_2026.json`, et
  recoupée de trois façons : le panorama, qui publie la même EACR (ci-dessous,
  point 2) ; le témoin d'avant 207cb53 (lu le 16 octobre), dont les blocs
  `conditions_liquidation`, `liquidants_par_age` et `droits_directs_par_age`
  sont identiques à ceux du témoin refait (seule la date de lecture change,
  et `conditions_par_age` s'ajoute) ; et la somme des sexes, qui redonne
  l'ensemble en 2024. Ce qui n'est qu'au classeur (la CNBF, caisse 2201) n'est
  pas vérifié.
- *Au dépôt* : `data/reference/macro/departs_generations.csv` et
  `conditions_selon_l_age_residents.csv` (EIR 2020, fichiers certifiés) ; le
  code, `scripts/grille_large.py`, `src/retraite_notionnelle/facteurs_depense.py`,
  `src/retraite_notionnelle/controle_eacr.py`, `scripts/mesurer_surcote.py` ;
  la sortie de la mesure, `docs/mesures/138/2026-11-03-etape-14-mesure-e12fe03.json`
  et `.txt`.

**Verdict. Conforme sur l'essentiel.** Chaque chiffre des sources que la note
cite se retrouve, à la bonne ligne, la bonne génération, le bon sexe et le bon
champ ; les 13,00, 13,73 et 13,38 % se refont du témoin et du code, et sont
bien le flux de la Cnav de 2024, indépendants compris ; la décomposition des
12,42 % de la génération 1960 et la compensation se refont au centième de la
sortie de la mesure, qui se retrouve à son empreinte, sur un commit de `main` ;
les quatre mutations sont prises. **Écarts, tous faibles** : le résumé parle
d'un « total » que les sources ne publient pas (point 3) ; l'écart du modèle à
sa propre cible pour les générations 1955 et 1960 n'est ni expliqué ni chiffré
(point 2) ; le texte du panorama donne une troisième valeur, 17 %, à l'État
civil de la génération 1957, que la note ne relève pas (point 3). Trois
négligeables.

## 1. Les quatre écarts de R-I-bis

**Les mutations — conforme.** Réintroduites une à une, dans un worktree de
9649199 (le dépôt lui-même intact), `tests/test_grille_large.py -k "mesure_de_la_surcote or mesure_compte"`
lancé après chacune :

| mutation de `scripts/mesurer_surcote.py` | résultat |
|---|---|
| `de_la_table_h(ETAT, "flux", annee)` lu en `M.ANNEE_EACR` | 1 échec, `…lit_ses_sources_annee_par_annee` |
| la décote de la Cnav lue en `"taux_plein"` | 1 échec, le même test |
| « version » et « éteinte » permutées dans `les_deux_grilles` | 1 échec, `…construit_la_version_la_constante_allumee` |
| la règle de 2004 ôtée de `a_la_condition` (`return False`) | 1 échec, `…compte_les_stocks_a_la_condition_et_la_decote_d_apres_1960` |

Sans mutation : 6 réussis. Les trois qui passaient sous R-I-bis, et la
quatrième de la note, sont prises.

**Les stocks à la condition — conforme.** Au témoin, le stock de la Cnav de
2024 surcote pour 1 658 347 / 14 744 736 = 11,25 %, celui de l'État civil pour
370 626 / 1 641 380 = 22,58 %. À la sortie de la mesure (`.txt`, l. 62-63 et
40-41) : 7,81 au drapeau et 7,07 à la condition pour le régime général, 23,52
et 23,03 pour l'État ; écarts 11,25 − 7,81 = 3,44 et 11,25 − 7,07 = 4,18
points, 23,03 − 22,58 = 0,45. Les sources de 2020, refaites à
`conditions_selon_l_age_residents.csv` : 662 / 8 452 = 7,83 % (l. 646, 403),
674 / 7 196 = 9,37 % (l. 647, 404) ; 662 × 38,7 / (8 452 × 22,4) = 13,53 %
et 674 × 40,7 / (7 196 × 23,6) = 16,15 % (l. 628-629, 385-386) ; parmi les
surcotés, 9,2 + 2,1 + 8,8 + 12,3 = 32,4 % des femmes, 7,5 + 1,1 + 6,4 + 9,7 =
24,7 % des hommes (l. 649-653, 673-677). Chaque valeur simulée du tableau de
la note est celle de la sortie (l. 79-88).

**La phrase des départs après 67 ans — conforme.** Refaits : R = 122 368 /
648 346 = 18,874 % (témoin, table H, flux 2024 de la Cnav) ; a = (20 350 +
6 969 + 4 832 + 15 581) / 648 346 = 47 732 / 648 346 = 7,362 % (table B) ;
s = 34,6 % (`departs_generations.csv`, l. 1068 ; 6,0 milliers, l. 1071, sur
757,0, l. 1143) ; m = 10,9113 % (sortie JSON, `regime_general.liquidants_2024.condition`).
Gains a × (s − m) = 1,744 et a × s = 2,547 points ; restes 6,219 et 5,416 ;
bornes 6,559 et 7,362, restes 1,404 et 0,601 ; vu de la Cnav, (122 368 −
0,346 × 47 732) / 600 614 = 17,62 %, 6,71 points au-dessus de m. La phrase
corrigée (« de 1,7 à 2,5 points […] 7,4 au plus […] de 5,4 à 6,2 points »)
est celle que R-I-bis demandait.

**La mesure et son arbre — conforme.** `git rev-parse e12fe03^{tree}` donne
`adb1ff2f8caa67b29cd3c759576175b93a1dca4e` ; e12fe03 est un ancêtre de
`origin/main` (sans `--deepen` : il y est) ; la sortie JSON porte
`"depot": {"commit": "e12fe03a…", "arbre": "adb1ff2f…", "modifie": false}` ;
les deux fichiers ont les empreintes que la note dit (`2938c8ac…edf69e9`,
`47aea4b2…b545885`), recalculées. *Négligeable* : la commande exacte n'est
écrite que dans la note, et son chemin `--json` y est élidé (« … ») ; la
grille et la constante, elles, sont imprimées en tête de la sortie, et ce sont
les valeurs par défaut du script.

## 2. Les 13,00, 13,73 et 13,38 % (décision 17)

**D'où ils viennent — conforme.** Au témoin, caisse 0015, `flux`, 2024 :

| sexe | décote | taux plein | surcote | somme | part |
|---|---|---|---|---|---|
| femmes | 46 637 | 226 331 | 66 672 | 339 640 | 13,7313 % |
| hommes | 40 139 | 212 871 | 55 696 | 308 706 | 13,0023 % |
| ensemble | 86 776 | 439 202 | 122 368 | 648 346 | 13,3842 % |

Les sommes redonnent la ligne « ensemble » de la table (339 640 + 308 706 =
648 346 ; 46 637 + 40 139 = 86 776). Le code les rend tels quels, appelé ici :
`grille_large.decote_du_flux("F")` = 0,137313…, `("H")` = 0,130023… ;
`facteurs_depense.part_decotee_du_flux(temoin)` = 0,133842…, les deux par
`controle_eacr.conditions_publiees`, qui divise par la somme des trois
conditions (`CAISSE_DU_FLUX = "0015"`, `ANNEE_DU_FLUX = 2024`).

**Le bon champ — conforme.** Que la ligne soit le flux des nouveaux retraités
de 2024 de tous âges, le panorama le confirme : son tableau complémentaire
« Décote » (« Nouveaux retraités ayant liquidé leur pension avec une décote »,
« Champ > Nouveaux retraités de chaque année […] vivants au 31 décembre
2024 », « Source > Drees, EACR 2024 ») donne au régime général 13,4, à la MSA
salariés 6,6, à la MSA non-salariés 5,0, à la FPE civils 18,4 — au témoin
13,38, 6,55, 5,00, 18,39. Que ce soit le privé, indépendants compris : la
documentation de l'EACR, p. 33 (« A partir de 2020, il n’existe plus qu’un
seul régime (au code cc ‘0015’), qui verse les pensions des travailleurs du
secteur privé non agricole et des indépendants ») et p. 38 (« 0015 | Base |
Cnav | Régime général, avec SSI | Apparaît en 2020 ») ; le panorama, note 1 du
graphique 4 et du tableau complémentaire. La prémisse de la décision 17 (« ne
vient que des salariés du privé ») est donc à corriger comme la note le fait.
La documentation définit la table H, p. 24 : « La table H-Conditions_liq
contient les effectifs et montants du stock de retraités selon les conditions
de liquidation. Les données sont ventilées par sexe et âge » — citation exacte
de la note ; la variable « Age » n'y est pas définie, quand elle l'est pour
les tables B et D (« âge atteint au 31/12 à partir de 2009 »), comme la note
le dit. *Limite de cette relecture, non écart* : la répartition par sexe
(13,00 et 13,73) ne se recoupe à aucune publication ; elle n'est vérifiée
qu'au témoin, deux fois lu du classeur à des dates différentes.

**Appliqué à toutes les générations nées depuis 1960, tous régimes —
conforme pour la règle.** `decotes_des_generations` rend, sous
`DECOTE_DES_RESIDENTS` (vrai), des paires qui vont, par sexe, des nés en 1953
résidents de l'EIR (11,9 % des femmes, 7,7 % des hommes, `departs_generations.csv`,
l. 1526 et 1538) aux 13,731 et 13,002 % de 1960, en droite ligne ;
`_par_generation` prête la dernière valeur à chaque génération qui la passe ;
`part_decotee_de_la_generation` rend `du_flux` dès 1960 (appelée ici pour
1960, 1965 et 1975 : la même valeur). La part est rapportée à tous les
retraités du sexe (`part_des_incompletes`, `poids_des_incompletes`), puis
portée par les seules jumelles des carrières incomplètes au taux plein
(`parts_des_jumelles`) : elle vaut pour tous les régimes, mais seuls le
salariat et les non-salariés la portent, comme la note le dit.
`GENERATION_DU_FLUX = 1960` : l'âge moyen des nouveaux retraités de 2024 tous
régimes, refait au témoin (table C, `nl_ddir`, âges entiers), 63,60 ans.

**Écart faible : ce que le modèle rend contre sa propre cible.** À 67 ans,
à la condition (sortie `.txt`, l. 169 à 195) : génération 1955, femmes
12,40 pour 12,42, hommes 10,04 pour 9,21 ; génération 1960, femmes 13,10 pour
13,73, hommes 11,66 pour 13,00 ; 1965, femmes 12,59, hommes 8,65. La note
explique 1965 (point 4 de « D'où vient l'écart ») ; elle montre, sans les
expliquer ni les chiffrer, les 0,83 point de trop des hommes de 1955 et les
1,34 point de moins des hommes de 1960 (0,63 chez les femmes). La décision 17
porte sur la cible, et la note ne prétend pas que le modèle la tient ; mais
qui lit « la part que la population prête à toutes les générations nées
depuis 1960, 13,0 % des hommes » doit savoir que la population en rend 11,7 %
à la génération 1960.

## 3. Ce que les sources publient, régime par régime

**Conforme, chiffre par chiffre.** Au témoin (table H, 2024, stock par âge) :
Cnav à 67 ans 85 676 / 653 763 = 13,11 %, femmes 51 069 / 344 675 = 14,82,
hommes 34 607 / 309 088 = 11,20 ; à 64 ans 12,61, 14,29, 10,80 ; État civil à
67 ans 11 159 / 69 758 = 16,00 (femmes 14,83, hommes 17,47), à 64 ans 19,20 ;
militaires 0,19 et 0,92 ; MSA salariés 5,12 et 6,09 ; exploitants 6,57 et
6,12 (femmes 8,52, hommes 5,27, à 67 ans) ; les flux de 2024 de chaque caisse
(18,39, 11,47, 6,55, 5,00). Chaque case du tableau de la note est juste. Au
classeur de la fiche 17, « F17_Graphique 4 », ligne 1957 : régime général
13,1, MSA salariés 5,1, MSA non-salariés 6,6, FPE civils 15,8, CNRACL 8,1 ;
ligne 1955, régime général 12,8 ; ligne 1953, régime général 11,6, tous
régimes 10,7 — la colonne « Tous régimes » s'arrête bien à 1953. Le stock de
2024 à 67 ans redonne au dixième chaque valeur de 1957, sauf l'État civil
(16,00 pour 15,8) : la lecture de l'âge en fin d'année, que la note en tire,
tient. Le champ et la note du graphique sont cités exactement ; la note 6,
p. 155, aussi. Les dix parts du tableau complémentaire « Décote » sont
exactes (13,4 ; 6,6 ; 5,0 ; 18,4 ; 9,5 ; 12,3 ; 15,9 ; 11,4 ; 17,8 ; 9,3). En
2022 et 2023, les sexes de la Cnav ne redonnent pas l'ensemble (343 013 +
327 327 = 670 340 pour 693 238 ; 265 596 + 203 090 = 468 686 pour 692 416) ;
les 184 872 et 261 708 départs de 62 ans de 2024 et de 2022 sont ceux de la
table H par âge.

**Écart faible : une troisième valeur pour l'État civil.** Le texte de la
fiche, p. 155 : « Parmi les assurés nés en 1957, 17 % des retraités du régime
de la FPE civils sont partis avec une décote, contre moins de 15 % dans les
autres principaux régimes (13 % au régime général et 8 % à la CNRACL) ». Le
graphique 4 en donne 15,8, la table H 16,00. La note relève l'écart du
graphique à la table (« Ce que les sources ne tranchent pas »), non celui du
texte, plus grand. Il ne change aucun calcul de la note, qui prend la table
H ; il est à déclarer avec l'autre.

*Négligeable* : l'EIR certifiée donne à la génération 1953 une décote tous
régimes de 10,6 % (`departs_generations.csv`, l. 1171), le graphique 4 10,7 ;
la note cite le graphique, et dit d'où vient la valeur. *Non vérifié* : la
CNBF (caisse 2201 : 123 sur 1 120, 103 sur 421, 119 sur 811), que le témoin
ne garde pas et que seul le classeur porte.

## 4. Les 12,42 % de la génération 1960, et la compensation

**Refaits de la sortie JSON — conforme, et chiffrés.** `pesees.version.generations.1960` :
la décote « tous » vaut 0,124163 ; la somme des poids fois la décote de chaque
groupe la redonne exactement.

| groupe | poids | décote | apport |
|---|---|---|---|
| régime général | 68,415 % | 16,020 % | 10,960 points |
| professions libérales | 3,549 | 18,917 | 0,671 |
| exploitants (MSA non-salariés) | 4,089 | 14,440 | 0,591 |
| régimes spéciaux | 2,482 | 7,833 | 0,194 |
| État civil, CNRACL, militaires | 9,688 ; 10,536 ; 1,240 | 0,00 | 0 |
| ensemble | 100,000 | | 12,416 |

Aux mêmes poids, les parts de la génération 1957 (au témoin : 13,105 ; 15,997 ;
2050 / 31 225 = 6,565 ; 21 / 11 011 = 0,191 ; CNRACL 8,1 au graphique)
donnent 11,640 points sur 93,969 % de la génération ; les 6,031 % qui restent
(libéraux et régimes spéciaux), à 0 et 20 %, mènent à 11,64 et 12,85 % (12,846 ;
la note dit 12,8, juste à l'arrondi près). Il manque à la fonction publique
9,688 × 15,997 + 10,536 × 8,1 = 2,403 points ; le régime général en rend
68,415 × (16,020 − 13,105) = 1,994, les exploitants 4,089 × (14,440 − 6,565) =
0,322. L'explication est une identité, non une affirmation :
12,416 − (11,640 + 0,866) = −0,089 = 1,994 + 0,322 − 2,403 − 0,002 (les
militaires), où 0,866 est l'apport des libéraux et des régimes spéciaux, qui
n'ont pas de source. Elle compare la génération 1960 du modèle à la 1957 des
sources, ce que la note déclare (« Un calcul, non une source : aux poids de
cette génération, les parts publiées de la génération 1957 »). Le tableau des
groupes en 2024 (régime général 17,15 ; 13,36 ; 16,12 ; …, régimes spéciaux
77,92 ; 7,62 ; 0,00) est celui de la sortie, case par case.

**Écart faible : le « total » du résumé.** Le paragraphe d'ouverture écrit :
« Le modèle tombe près du total (génération 1960, 12,4 % tous régimes) par
compensation ». Aucune source ne publie ce total : c'est la fourchette de
11,6 à 12,8 % que la note bâtit des parts par régime aux poids du modèle, et
elle dit elle-même, au point 2 de « D'où vient l'écart », que la moyenne des
parts par régime « n'est pas une part tous régimes, et aucune source ne la
donne ». Qui lit le seul résumé croira à un chiffre publié. À dire : « près
de ce que les parts publiées par régime donnent à ses poids (11,6 à 12,8 %),
non d'un total publié, qui n'existe pas ».

*Négligeable* : « par paquets (à 63 et 65 ans en 2024, aucun à 64, 66 et 67
ans) » omet les 62 ans, où le modèle décote aussi (12,74 %, sortie, l. 120).

## 5. Rien de corrigé : une hypothèse, non une règle

Conforme. `part_decotee_du_flux` ne sert que `scripts/facteurs_depense.py`
(option `--decote-generation`) et la population (`grille_large`), aucun calcul
du site ; la décote de la fonction publique est au dépôt
(`data/reference/legislation/decote_fonction_publique.csv`), et la mesure ne
trouve aucun fonctionnaire de la population qui la déclenche (0,00 % à
l'État, à la CNRACL, aux militaires, à chaque champ). Ce que la note propose
(une cible par génération ou par groupe, des fonctionnaires qui décotent)
relève du propriétaire, avec la décision 11.

## Les tests

Sur 9649199 : `python -m pytest -m rapide`, 4 319 réussis, 56 sautés, 13 en
échec, tous `test_pages_en_dossier.py` (les pages toutes faites, que GitHub
refait) ; `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`, 4 120 réussis,
255 sautés, les mêmes 13 ; `tests/test_controle_eacr.py`,
`tests/test_drees_panorama_2024.py`, `tests/test_facteurs_depense.py` et
`tests/test_grille_large.py`, 173 réussis. Sur b7c82f5 :
`python scripts/construire_donnees.py`, puis `git status` : aucun fichier
suivi modifié. Aucun texte de droit lu : pas d'entrée au journal de veille.
