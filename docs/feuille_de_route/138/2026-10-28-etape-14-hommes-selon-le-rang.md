# Étape 14, suite de la seizième partie : les natures des hommes selon le rang, à la pente de leur génération

**Le 28 octobre 2026 : les natures des hommes d'une carrière pleine suivent
désormais leur rang, à la pente de leur génération ; la trente-quatrième
version, sur `main` (aa4955c). La feuille « QuintilesEQCC » des classeurs des
nés en 1950 et en 1953 entre au dépôt, 540 valeurs certifiées (50e136e) : leur
masse assimilée descend avec le rang, comme celle des femmes, quand celle du
stock de 2020 remonte au haut des rangs des hommes. La part de maladie, d'AVPF
et de chômage d'une classe de centiles suit la masse de sa classe dans la
génération : 1,52 fois celle de l'échantillon à la classe p10 en 1950, 0,80
fois aux classes p50 à p99 ; 1,75 et 0,66 fois en 1953. Nés en 1955, les
hommes de la classe p10 comptent 3,47 années de ces natures, et non 2,13, ceux
des classes p90 à p99 1,33 ; leurs carrières pleines partent en carrière
longue pour 54,7 et 77,6 %, et non 66,3 et 73,6 ; en tout un peu moins, 27,75 %
des hommes et non 28,30 (EIR 28,3), sur une pesée approchée. Les pensions au
départ ne bougent pas. Le plafond de chaque génération ne coupe rien : il
reste celui du stock. La version reste ; la page ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, un point du bloc de l'étape, et lui
seul : « les hommes selon le rang — la pente des natures des hommes selon le
rang, avec le plafond de chaque génération, que ses classeurs publient pour
1950 et 1953, à certifier, s'il vaut de couper le haut des rangs » (« Ce qui
reste », point 1, de la note de la vingtième partie,
`2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`).

- *Ce qui était.* La vingt-septième version (`NATURES_SELON_LE_RANG`,
  `("F",)`) donne aux femmes leurs natures selon le rang, à la masse
  assimilée que l'EIR mesure aux rangs du stock des résidents de 2020
  (`quintiles_eqcc_residents.csv`). Les hommes gardaient la même part à
  chaque rang : la masse du stock remonte au haut des leurs — 12,5 % de la
  durée validée hors majorations aux deux premiers quintiles de la pension en
  équivalent carrière complète, 4,9 % au troisième, 7,5 au quatrième, 9,8 au
  cinquième —, que les classeurs de leurs générations, lus le 24 octobre sans
  être certifiés, ne trouvaient pas (note de la treizième partie). Nés en
  1950, ils comptaient 1,69 année de maladie, d'AVPF et de chômage à chaque
  classe, nés en 1955, 2,13.
- *La donnée* (`scripts/fetch/drees_departs_generations.py`,
  `quintiles_eqcc_generations.csv`, `tests/test_departs_generations.py`,
  50e136e). Le récupérateur des classeurs d'une génération lit aussi leur
  feuille « QuintilesEQCC », comme celle de tous les retraités
  (`quintiles_de_la_feuille`, que `lire_quintiles_eqcc` appelle désormais) :
  chaque génération rangée en elle-même, tous lieux de résidence, chacun de
  ses quintiles comptant le cinquième de ses retraités ; par quintile et par
  sexe, les effectifs, la proratisation, les pensions, la part au minimum, la
  durée validée hors majorations et ses tranches, la durée validée, la durée
  cotisée, la part des départs en carrière longue et avec décote. 540
  valeurs, certifiées par `scripts/verifier_donnees.py`, le journal complété
  de la seule série ; la fiche `drees_eir_generations` le dit. Le portail a
  coupé dix-sept des dix-neuf téléchargements à la main ; le récupérateur,
  lancé ensuite, a lu les deux classeurs du premier coup. Deux tests de plus,
  vus rouges : le lecteur, sur une feuille rendue comme celle des nés en
  1953, et le fichier certifié, sur ce que les classeurs impriment. La masse
  des hommes, en pour cent de la durée validée hors majorations, années
  validées hors majorations et cotisées entre parenthèses :

  | hommes | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | stock des résidents de 2020 | 12,5 | 12,5 | 4,9 | 7,5 | 9,8 |
  | nés en 1950 | 10,7 (28 ; 25) | 10,5 (38 ; 34) | 4,9 (41 ; 39) | 4,9 (41 ; 39) | 4,9 (41 ; 39) |
  | nés en 1953 | 16,7 (30 ; 25) | 12,5 (40 ; 35) | 4,8 (42 ; 40) | 7,1 (42 ; 39) | 4,9 (41 ; 39) |

  L'EIR arrondit ses durées à l'année : la masse d'un quintile se lit à une
  année près, la pente non — deux fois plus d'années assimilées aux deux
  premiers quintiles qu'aux trois derniers.
- *La trente-quatrième version* (`NATURES_DES_HOMMES_SELON_LE_RANG`,
  `pentes_des_generations`, `quintiles_eqcc_des_generations`, aa4955c). La
  part des hommes d'une classe de centiles qui ont de la maladie, de l'AVPF
  ou du chômage est celle de l'échantillon interrégimes de cotisants,
  multipliée par le rapport de la masse de sa classe dans leur génération
  (`parts_assimilees_des_classes` sur les quintiles de la génération) à celle
  de toutes les carrières pleines des hommes, chacune à la masse de sa classe
  dans la génération, pesée par sa part de la Cnav, comme sous
  `masses_moyennes` : 6,11 % en 1950, 7,44 % en 1953. Le facteur des nés en
  1950 vaut jusqu'à cette génération, celui des nés en 1953 après, en droite
  ligne entre eux (`natures_au_rang`, son facteur en paires) ; le service ne
  change pas ; chacun de ceux qui en ont garde les années de l'échantillon.
  Les femmes gardent la vingt-septième version, à la pente du stock. La masse
  de chaque classe de la tranche de quarante années et plus, en pour cent, et
  son facteur :

  | | p10 | p25 | p50 | p75 | p90 à p99 |
  |---|---|---|---|---|---|
  | stock des résidents de 2020 | 11,32 | 7,40 | 6,52 | 8,80 | 9,76 |
  | nés en 1950 | 9,26 | 7,55 | 4,88 | 4,88 | 4,88 |
  | facteur de 1950 | 1,52 | 1,24 | 0,80 | 0,80 | 0,80 |
  | nés en 1953 | 13,05 | 8,71 | 5,96 | 6,04 | 4,88 |
  | facteur de 1953 | 1,75 | 1,17 | 0,80 | 0,81 | 0,66 |

  Les années de maladie, d'AVPF et de chômage par homme de chaque classe,
  service compris, ses têtes comptées :

  | | p10 | p25 | p50, p75 | p90 à p99 |
  |---|---|---|---|---|
  | nés en 1950, avant | 1,69 | 1,69 | 1,69 | 1,69 |
  | nés en 1950, avec | 2,49 | 1,89 | 1,49 | 1,49 |
  | nés en 1955, avant | 2,13 | 2,13 | 2,13 | 2,13 |
  | nés en 1955, avec | 3,47 | 2,60 | 1,80 | 1,33 |

- *Le plafond de chaque génération, mesuré, et laissé.* Prendre pour plafond
  la masse de la classe dans sa génération, et non dans le stock, ne coupe
  rien. Sans la pente, il ne tient nulle part en 1950 ; en 1955, aux classes
  p90 à p99, deux années par homme et non quatre, il ramène les natures à
  0,87 fois les leurs, et l'arrondi des années de chaque nature les leur rend
  toutes, trois de chômage, quatre de maladie. Avec la pente, le haut des
  rangs passe dessous : 1,49 et 1,33 année pour deux. Le haut des rangs ne
  vaut pas d'être coupé : le plafond reste la masse du stock, quatre années de
  la carrière de la classe p99, 9,76 % de 43.
- *Les tests.* Un de plus,
  `test_les_natures_des_hommes_suivent_la_masse_de_leur_generation` : les
  masses des classes p50 à p99 des nés en 1950 et p90 à p99 des nés en 1953,
  2/41 ; les moyennes de leurs carrières pleines, leurs têtes comptées, 6,11
  et 7,44 % ; les rapports des classes p10 et p99 ; les classes de quinze qui
  ont de la maladie et du chômage, posées à la main — nés en 1950, deux et
  quatre à la classe p99, trois et sept à la classe p10 ; nés en 1955, quatre
  et dix à la classe p10, une et quatre à la classe p99 — ; aux générations
  1945 à 1960, la part de chaque nature à chaque classe et sur toutes, à un
  trentième près ; le plafond du stock. Vu rouge sans la version. Le test des
  femmes perd ce qu'il disait des hommes, la même part à chaque rang ; celui
  du chômage à sa part (vingt-quatrième version), qui juge l'homme de la
  classe p50 né en 1950, ôte la trente-quatrième, comme la vingt-cinquième et
  la vingt-sixième. Les 86 tests de la population passent, en 2 min 05 s sur
  quatre cœurs.
- *Trouvé en chemin.* La population grandit : des parts qui changent d'une
  classe à l'autre font plus de classes de nature, 18 946 cas types sur la
  tête du jour (aa4955c) et non 16 874, 12,3 % de plus, que la mesure entière
  paiera en temps. Et la version prend le numéro trente-quatre : une autre
  session de la vague a donné le trente-trois, le même jour, à la surcote des
  statutaires, poussée juste avant elle. Le test de celle-ci,
  `test_un_fonctionnaire_civil_qui_surcote_part_avec_la_surcote_moyenne_de_sa_categorie`,
  passe sur aa4955c et tombe sur 02f3ea9, le pilote de la descente du site,
  avec ou sans la trente-quatrième : le super-actif poly né en 1960 y part à
  64,9 ans, quand le test l'attend avant 62,15, son taux plein de 59,75 ans
  et ses 2,4 années d'attente.
- *La mesure.* Un pilote hors du dépôt, sur la tête de 96ce7b7 : la
  population construite telle quelle, puis sous trois variantes branchées par
  remplacement de fonctions —
  le plafond de chaque génération sans la pente, la pente au plafond du
  stock, l'une et l'autre —, le code du dépôt redonnant ensuite la deuxième à
  l'identique ; le départ (`condition_au_depart`) et la pension au départ de
  chacune des 2 856 carrières pleines des hommes qui portent des natures,
  nées en 1950 et en 1955, au scénario 1, sur quatre cœurs, 47 à 84 s, sans
  échec ; chacune pesée de ses têtes de 2020 (`poids_effectifs`), sans sa
  survie propre ni l'âge où l'enquête voit sa génération, que la mesure
  entière (`grille_large.py --grille population --distribution`) prendrait,
  en deux heures et demie par arbre. La carrière longue des hommes s'y
  rapporte à toutes leurs têtes de 2020. Ce qu'elle trouve, en pour cent :

  | | sans la version | avec |
  |---|---|---|
  | nés en 1950, carrières pleines parties en carrière longue | 37,8 | 37,5 |
  | dont la classe p10 | 35,4 | 32,7 |
  | dont les classes p50 à p99 | 38,2 | 38,6 |
  | nés en 1955, carrières pleines parties en carrière longue | 72,4 | 71,0 |
  | dont la classe p10 | 66,3 | 54,7 |
  | dont la classe p25 | 73,3 | 69,3 |
  | dont les classes p50 et p75 | 73,6 | 74,7 |
  | dont les classes p90 à p99 | 73,6 | 77,6 |
  | hommes nés en 1950 en carrière longue (EIR 18,2) | 14,75 | 14,65 |
  | hommes nés en 1955 (EIR, nés en 1953 : 28,3) | 28,30 | 27,75 |
  | pension moyenne au départ des nés en 1950, € par an | 19 575 | 19 573 |
  | des nés en 1955 | 21 595 | 21 594 |

  La pente fait passer la carrière longue du bas des rangs au haut : la
  classe p10, du chômage pour deux tiers de ses hommes nés en 1955, en perd
  ce que les trimestres réputés cotisés (D. 351-1-2) ne rendent pas ; le haut
  la gagne. En tout, elle s'éloigne un peu de l'EIR, comme celle des femmes
  sous la vingt-septième version (2,3 % et non 2,8 en 1950, EIR 5,1) : la
  version suit la masse que l'EIR mesure à chaque rang, non un total. L'EIR
  range la carrière longue autrement : 5,5 % des hommes nés en 1953 au
  premier quintile, 41,8 % au troisième, 23,3 % au cinquième ; la population,
  dont les carrières pleines entrent au même âge à chaque rang, en monte la
  part avec lui.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les femmes ; les carrières des
  hommes qui ne sont pas pleines ; le plafond ; le registre, dont aucun point
  « 138.14 » ne nomme les natures des périodes assimilées. Aucune règle du
  scénario 1 ne change : pas d'entrée au journal de veille. La suite rapide
  compte sept rouges du portage, sur la tête du jour avec ou sans la version :
  son paquet de données date d'avant les données des régimes de 917c5a3, et
  GitHub le refait après l'envoi.

**Ce qui reste** de l'étape : celui de la note de la vingtième partie, moins
les hommes selon le rang et ce que les autres sessions de la vague du
28 octobre mènent ; et deux pistes que cette mesure ouvre, à la population :

1. *La carrière longue selon le rang*, que les classeurs des générations
   publient désormais par quintile (`part_carriere_longue`), contre la
   population rangée dans sa génération par quintile de sa pension en
   équivalent carrière complète, ce que la mesure ne fait pas encore — elle
   range le stock de 2020 —, et l'entrée selon le rang, que l'EIR voit plus
   tardive au cinquième quintile.
2. *Les femmes à la pente de leur génération*, plus raide au bas que celle du
   stock — 22,2 et 23,6 % de la classe p10 nées en 1950 et en 1953, pour
   19,5 —, que la vingt-septième version garde.
