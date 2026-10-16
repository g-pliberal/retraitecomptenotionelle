# Étape 3, sixième partie : l'âge des retraités, l'âge où ils partent et leurs conditions de départ, contrôlés sur les tables H, B et C de l'EACR

**La demande.** Vague bis du 16 octobre 2026, session 11 sur 13 : « action
138, étape 3. Le contrôle par l'EACR, après celui d'Ancetre : les tables H, B
et C de l'EACR, lues, certifiées et confrontées aux cas types et à la
population » — le point 1 de « Ce qui reste » de la note du même jour
(`2026-10-16-etape-3-controle-ancetre.md`). Rien n'est écrit dans les pages,
ni dans `cout.py`, ni dans `grille_large.py`, que d'autres sessions tiennent.

**La source.** Les deux classeurs « 62 EACR diffusée » de la DREES, version du
26 mai 2026, que `drees_eacr.py` lit déjà pour le cadrage et les minima. Trois
feuilles, chacune lue seule (`scripts/fetch/drees_eacr_tables.py`, témoin
`tests/temoins/drees_eacr_tables_2026.json`, `data/sources.yaml`,
`drees_eacr_tables`) :

- *H-Conditions_liq* : les départs au taux plein, avec décote, avec surcote,
  en flux et en stock, tous motifs et tous âges, par sexe, de 2015 à 2024 —
  la Cnav, les deux MSA, l'État civil et militaire (cube du SRE),
  l'Agirc-Arrco. Les trois conditions partitionnent les retraités ; la
  surcote manque à l'Agirc-Arrco, qui n'en sert pas, et aux militaires ;
- *B-Liquidants* : les liquidants de 2024 par âge, cinq caisses (Cnav, MSA,
  CNRACL, SSI) ;
- *C-Droits_directs* : tous régimes (`0000`, tiré d'Ancetre 2024), les
  retraités de droit direct et les nouveaux retraités de 2024, par âge et par
  sexe, avec leur pension mensuelle. Quelques âges secrétisés manquent au
  détail, moins d'un pour cent ; au-delà de 95 ans, une seule ligne.

**La mesure** (`retraite_notionnelle.controle_eacr`, `scripts/controle_eacr.py`).
Chaque cohorte de la grille déjà partie en 2024, comptée en têtes comme la
page les compte (poids du cas type fois effectif INSEE), sa pension prise
comme le contrôle d'Ancetre la prend ; rangée par tranche d'âge, et, pour
celles qui partent l'année même, par âge de liquidation. `--population` mesure
de même la population de `grille_large.py` (sept minutes et demie sur quatre
cœurs), et la part de ses retraités du régime général partis décotés. Les
tables comptent des personnes, la grille des têtes de caisse : seules les
parts et les rapports se comparent.

**Ce qu'il trouve**, le 16 octobre 2026.

| Tranche | grille | population | EACR | pension rel., grille | population | EACR |
|---|---:|---:|---:|---:|---:|---:|
| moins de 60 | 2,2 % | 1,9 | 1,2 | 0,94 | 1,09 | 0,97 |
| 60-64 | 12,1 | 11,8 | 11,2 | 0,97 | 1,13 | 1,06 |
| 65-69 | 22,7 | 21,8 | 21,5 | 1,10 | 1,10 | 1,05 |
| 70-74 | 21,5 | 22,0 | 21,6 | 1,04 | 1,02 | 1,03 |
| 75-79 | 17,3 | 17,7 | 19,0 | 1,00 | 0,96 | 1,03 |
| 80-84 | 10,7 | 10,9 | 11,5 | 0,93 | 0,89 | 0,97 |
| 85-89 | 7,9 | 8,1 | 8,3 | 0,88 | 0,85 | 0,87 |
| 90-95 | 4,7 | 4,8 | 4,4 | 0,82 | 0,79 | 0,78 |
| plus de 95 | 1,0 | 1,0 | 1,3 | 0,75 | 0,71 | 0,71 |

| Âge de liquidation | <60 | 60 | 61 | 62 | 63 | 64 | 65 | 66 | 67 | 68+ | âge moyen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| grille | 0 | 0 | 15,1 | 46,1 | 11,6 | 12,6 | 13,0 | 0 | 1,6 | 0 | 62,7 |
| population | 0 | 0 | 0 | 67,7 | 8,8 | 0,3 | 5,2 | 0 | 18,1 | 0 | 63,2 |
| EACR | 4,0 | 5,2 | 8,5 | 26,0 | 18,6 | 7,0 | 7,1 | 5,8 | 10,6 | 7,3 | 63,6 |

| Cnav, 2024 | taux plein | décote | surcote | décote, population |
|---|---:|---:|---:|---:|
| flux | 67,7 % | 13,4 | 18,9 | 5,0 |
| stock | 79,3 | 9,4 | 11,2 | 6,6 |

1. *Le stock est compté aux bons âges.* Chaque tranche, dans la grille comme
   dans la population, à moins de deux points de la table C (1,7 au plus, aux
   75-79 ans) : la couverture que la page suppose constante (limite n° 2 de
   `cout.py`) ne déforme pas la pyramide des retraités en 2024. Le profil de
   la pension selon l'âge suit aussi, qui descend de 1,05 à 0,71 de la
   moyenne ; la population le force aux âges jeunes (1,13 à 60-64 ans pour
   1,06), la grille le creuse (0,97).
2. *Les départs sont trop groupés.* La grille et la population mettent 46 et
   68 % de leurs nouveaux retraités à 62 ans, pour 26 % ; aucun avant 61 ans
   (les carrières longues, 9 % des liquidants de 2024), aucun à 66 ni après
   67 (13 %), et la population, qui ajoute les carrières incomplètes partant
   au taux plein automatique, les met toutes à 67. L'âge moyen de liquidation
   est trop jeune, de 0,9 an dans la grille, de 0,45 dans la population. La
   pension des nouveaux retraités dépasse celle de tous de 11 % dans la
   grille, de 7 % dans la population, pour 1 %. Les agents de conduite et des
   IEG n'ont aucun liquidant en 2024 : leurs générations de grille partent de
   2019 à 2023 puis de 2025 à 2029, l'âge d'ouverture ayant reculé entre
   elles ; et le militaire, parti à 48 ans, n'entre à la page qu'à 50, son
   plancher (`donnees/population.py`).
3. *Ni décote ni surcote dans la grille, trop peu de décote et aucune surcote
   dans la population.* La Cnav décote 13,4 % de ses liquidants de 2024 et en
   surcote 18,9 % ; l'État civil 18,4 et 38,9 %. La population, qui ne fait
   partir décotées que des carrières incomplètes à l'ouverture (part de
   l'EIR, quinzième version de l'étape 14), en décote 5,0 % au régime
   général en flux, 6,6 % en stock, pour 9,4 ; ni l'une ni l'autre ne
   surcote. C'est le point 3 de l'étape 14, « les départs choisis » : la
   surcote et l'âge publié.

**Le test** (`tests/test_controle_eacr.py`, niveau `controle`, le témoin et
la mesure en `rapide`) tient le témoin (chaque table redonne son total), la
mesure sur une grille d'essai, puis, sur la grille du dépôt, chaque tranche du
stock à moins de 2,5 points, le profil qui descend au-delà de 85 ans, l'âge
moyen de liquidation trop jeune d'un demi à un an et demi, la moitié à 62 ans
et rien à 60, 66 ni après 67 : un écart qui se referme dit que la population
a remplacé la grille, ou qu'un âge a bougé. La population n'est pas testée :
sept minutes.

**Au registre.** Le point de `legiretraite` sur les tables E, H, B et C,
coupé le 14 octobre, passe `repris`, au chantier 138.3, avec sa vérification ;
les deux jeux de l'EACR rejoignent son `manifeste`.

**Ce qui reste**, de ce point :

1. *Les âges de départ de la population* : des carrières longues avant 62 ans,
   la surcote, un étalement entre 62 et 67 ans — la cible est ici, par âge, et
   à la Cnav par condition. C'est l'étape 14 (point 3), dans `grille_large.py`.
2. *Les coefficients temporaires de l'Agirc-Arrco* (feuille « Coeff
   Agirc-Arrco » du second classeur), à confronter.
3. *Le tableau 3.2 d'Ancetre par sexe* (note précédente, point 2), et la
   table C par sexe, que le témoin porte.
