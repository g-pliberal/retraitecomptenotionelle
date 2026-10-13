# Étape 7, la population : le jaune 2027 confronté à ce que le modèle suppose, trois recoupements et quatre écarts déclarés

Les tableaux que l'étape 0 rangeait à l'étape 7 ont été relus dans le jaune
annexé au PLF 2027 (`data/brut/34465.pdf`, tiré de la branche `jaune-2027`,
empreinte vérifiée ; `pdftotext -layout` page par page, et en image pour les
graphiques 15 et 16 et le tableau C-7), avec ceux qu'il faut pour les
confronter : le stock par âge (A-2, A-3), les entrées (B-5, B-12). En face, ce
que le modèle suppose de la population des pensionnés publics : la table de
mortalité et ses facteurs de population (`donnees/mortalite.py`), les
retraités que le COR projette aux caisses de la fonction publique
(`donnees/effectifs.py`), les cas types et leurs départs
(`castypes.py`, `avantages.masses_anticipees`), les polypensionnés de la
grille élargie (`scripts/grille_large.py`). Aucune ligne du modèle ne change :
trois tests tiennent ce qui recoupe et ce qui s'écarte, trois paragraphes
datés des limites déclarent le reste.

## Ce qui recoupe, et que trois tests tiennent

- **La mortalité des pensionnés civils de l'État**
  (`test_les_deces_de_2025_recoupent_le_facteur_des_pensionnes_civils`,
  `test_donnees.py`). Le rapport des décès de 2025 (B-13) aux décès que la
  table du modèle attend du stock de fin 2025 (A-2), chaque tranche répartie
  comme la population de l'INSEE au 1er janvier 2026, chaque âge mourant au
  quotient pris à mi-année :

  | Droit direct | Décès 2025 | Table générale, celle du modèle / interpolée | Sous le facteur du modèle |
  |---|---|---|---|
  | Civils de l'État, La Poste comprise | 45 591 | 0,879 / 0,855 | PAP 1,031 / 1,005 ; vingtile 16 : 1,037 / 1,011 |
  | Militaires | 8 617 | 0,955 / 0,901 | vingtile 15 : 1,084 / 1,026 |
  | CNRACL | 30 725 | 0,957 / 0,953 | vingtile 15 : 1,100 / 1,096 |
  | dont territoriale | 17 867 | 0,963 / 0,964 | 1,104 / 1,107 |
  | dont hospitalière | 12 858 | 0,950 / 0,938 | 1,094 / 1,083 |
  | Ouvriers de l'État | 2 399 | 1,027 / 0,976 | — |

  Le facteur que le modèle cale sur l'espérance à 65 ans que le PAP du
  programme 741 publie pour 2024 (0,86 sur la force de mortalité) retrouve les
  décès de l'année suivante à 3 % près : l'hypothèse qui le tient constant
  passe sa première observation. Répartir uniformément les tranches de cinq
  ans abaisse ces rapports d'un point environ.
- **Les retraités que le COR projette aux trois caisses publiques**
  (`test_les_retraites_que_le_cor_projette_recoupent_le_jaune_pensions_2027`).
  La grille les lit au-delà de 2024 (`CAISSES_PROJETEES`). De 2024 à 2025, le
  COR leur projetait +3,1 % à la CNRACL, +0,3 % aux civils et +1,1 % aux
  militaires ; le jaune constate +2,7, +0,1 et +0,5 % (A-3). Et ses tableaux
  bouclent : les entrées de 2025 (B-12) moins les décès (B-13) font la
  variation du stock à 0,03 % près dans les trois régimes.
- **Le militaire, sous soixante ans**
  (`test_les_retraites_de_moins_de_soixante_ans_confrontes_au_jaune_pensions_2027`,
  `test_avantages.py`) : 31,6 % de ses retraités dans la grille en 2025,
  31,5 % au jaune hors invalidité (A-2). Le recalage de l'action 152, étape 1,
  tient.

## Ce qui se déclare

Dans `docs/limites/5-hors-du-modele.md` et `5-bis-cout-agrege.md`, trois
paragraphes datés, déclarés dans `zones.yaml`.

- **L'agent de la CNRACL part trop tôt, et vit trop longtemps.** Il porte
  toute sa caisse, en catégorie active, à l'âge d'ouverture : 12,1 % de ses
  retraités ont moins de soixante ans en 2025, pour 1,3 % au jaune hors
  invalidité et 3,3 % avec. Le B-5 de 2025 compte 27 477 sédentaires partis à
  64,0 ans, 10 597 actifs à 61,0 et 15 054 carrières longues à 62,2. L'agent
  fait 4,4 des 8,3 milliards que le classement sert avant l'âge légal en
  2024, le militaire le reste. Son vingtile de niveau de vie lui prête 13 % de
  décès de moins que la population générale, quand ses retraités n'en ont que
  4 % de moins, et ses hommes autant qu'elle : près d'une année de rente de
  trop à 65 ans pour un homme, une demi-année pour une femme. Les deux
  tiennent au niveau de fin de carrière que l'étape 2 de l'action 152 a
  trouvé trop haut, 0,87 salaire moyen pour 0,75.
- **Le civil de l'État ne part jamais avant l'âge légal**, quand 11 139
  départs de 2025 l'ont devancé (C-1) : 5 909 au titre d'une carrière active
  (11 082 en 2015), 3 687 d'une carrière longue, 1 227 de parents de trois
  enfants, 316 d'un handicap ou d'un motif familial. Les départs anticipés
  pour carrière longue des trois versants, 11 676 en 2025 (23 035 en 2015),
  font 10 % des départs civils de la fonction publique, 20 % en 2016 ; la
  grille n'en sert aucun hors du privé. Ceux des parents de trois enfants,
  2 926 (5 174 en 2015), s'éteignent avec le dispositif.
- **Les polypensionnés.** D'après l'EIR de 2020, parmi les retraités de
  soixante ans ou plus de chaque régime (graphiques 15 et 16) :

  | Une seule pension | Ensemble | Femmes | Hommes | Deux | Trois | Quatre |
  |---|---|---|---|---|---|---|
  | Civils de l'État | 53,8 % | 58,5 % | 47,8 % | 40,7 % | 5,0 % | 0,4 % |
  | Militaires | 40,5 % | 59,7 % | 39,3 % | 47,4 % | 11,1 % | 1,0 % |
  | Ouvriers de l'État | 20,1 % | 25,6 % | 18,7 % | 67,4 % | 11,3 % | 1,3 % |
  | CNRACL | 23,7 % | 27,7 % | 14,7 % | 65,2 % | 10,2 % | 0,9 % |
  | dont territoriale | 14,6 % | 16,6 % | 11,8 % | 71,8 % | 12,3 % | 1,3 % |
  | dont hospitalière | 34,7 % | 37,3 % | 22,9 % | 57,1 % | 7,7 % | 0,5 % |
  | Ircantec | 59,3 % | 63,8 % | 50,8 % | 34,9 % | 4,8 % | 0,4 % |
  | Cnav | 63,1 % | 68,1 % | 57,2 % | 31,7 % | 4,8 % | 0,4 % |

  Touchent aussi une pension du régime général 43,7 % des civils, 51,7 % des
  militaires, 73,7 % des retraités de la CNRACL et 76,5 % des ouvriers de
  l'État ; 8 % des militaires une pension civile de l'État ou de la CNRACL.
  Comptées par régime d'affiliation, ces parts dépassent celles que la grille
  élargie lit par régime principal (`caracteristiques_retraites.csv` : 68 %
  de polypensionnés à la CNRACL, 42 % chez les civils), comme elles le
  doivent. Appliquées aux effectifs de 2024, elles mettent près de deux
  millions de pensionnés publics, 13 %, dans les 14,7 millions de retraités
  de la Cnav, à qui la grille de treize cas types prête une carrière entière
  du privé. Ni l'agent de la CNRACL ni le militaire n'ont de seconde carrière,
  dans aucune des deux grilles.
- **La table de mortalité de 2025.** L'année n'étant ni observée ni projetée,
  le modèle la tient d'une loi de Makeham calée sur e60 et e65 : ses
  quotients dépassent de 7 à 26 % ceux de 2024 et de 2026 de 70 à 80 ans, et
  leur restent de 8 à 33 % inférieurs au-delà de 88 ans. Les droits dérivés
  la démentent : les conjoints survivants des quatre régimes sont morts
  39 905 en 2025, quand elle en attendait 33 000 (rapport 1,21) et une table
  interpolée entre 2024 et 2026, 38 400 (1,04). Sous la table du modèle, la
  réversion semblerait servie à des veuves qui meurent un cinquième plus que
  la population générale ; sous la table interpolée, elles meurent comme
  elle, à 4 % près.

## Ce qui ne se compare pas

- **La pyramide des âges des agents** (graphiques 87 à 91, en image ; le
  texte en donne les chiffres). Le modèle ne porte pas l'âge des cotisants :
  le vieillissement des agents ne l'atteint que par les retraités que le COR
  projette, recoupés plus haut. Le texte va dans le sens du COR : la
  territoriale est la plus âgée, 46 ans en moyenne et 44 % d'agents de
  cinquante ans ou plus, 51 % chez ses fonctionnaires (36 % en 2011), quand le
  COR fait croître de 36 % les retraités de la CNRACL de 2025 à 2040, 34 500
  par an ; la croissance nette de 2025 en est l'ordre, 38 924 (69 650 entrées
  et 30 726 décès). Les militaires ne font que 1 % des agents de cinquante
  ans ou plus, pour 5 % de tous : c'est le départ après dix-sept ou
  vingt-sept ans de services que le cas type porte.
- **La durée moyenne de perception des décédés** (B-13) : 25,7 ans chez les
  civils, 37,6 chez les militaires, 20,4 à la territoriale, 25,4 à
  l'hospitalière. Rapportée à l'âge moyen au décès que le modèle attend de ces
  stocks, elle suppose une première mise en paiement d'un an et demi à quatre
  ans antérieure à celle du stock (A-1) : l'âge de départ des générations
  anciennes. Rien que le modèle calcule.
- **Les caractéristiques des départs anticipés** (C-3, C-6, C-9) : à la
  territoriale, 1,7 % avec décote en 2025, pour 11,3 % des autres départs ;
  à l'hospitalière 9,3 et 14,3 % ; à l'État 18,5 et 19,0 %. Les carrières
  longues de la CNRACL ne se comptent pas pareil d'un tableau à l'autre :
  7 989 départs avant l'âge légal des sédentaires (C-4, C-7), 15 054 parmi les
  départs pour ancienneté (B-5).

## Ce que le document dit contre lui-même

- Le tableau C-7 imprime 279 départs de parents de trois enfants en 2025 à
  l'hospitalière ; ses lignes d'âge en somment 989 (vérifié sur l'image).
- Le C-3 imprime « 14243,4% » pour la durée moyenne de services de 2022, le
  C-6 « 112?5 » pour celle des autres départs de 2024 ; les durées de 2024
  des C-6 et C-9 rompent leurs séries (100,2 à la territoriale, pour 118,6 et
  110,5 ; 110,9 à l'hospitalière, pour 126,1 et 122,4).
- Les titres des C-4 et C-7 disent « entre 2016 et 2025 » sur des séries qui
  commencent en 2015.
- La page 45 renvoie au « graphique 14 » pour les monopensionnés de la CNRACL
  par sexe, qui sont au graphique 16 ; le titre du graphique 15 écrit
  « Réartition ».
- La page 44 range les militaires parmi les régimes à plus de 60 % de
  polypensionnés (59,5 % au graphique 15), et borne les régimes à 80 % quand
  la territoriale en compte 85,4 %.
- Les pages 169 à 171 renvoient aux graphiques 89, 90 et 92 pour les
  graphiques 88, 89 et 91.
- Le B-13 compte 30 726 décès de pensionnés de droit direct de la CNRACL ;
  ses deux versants et ses deux sexes en somment 30 725.

## Ce qui va aux autres étapes

- **Étape 4, seconde partie** (« le stock face à la page Coût, pesé comme
  elle ») : la part des moins de soixante ans y est faite, pesée comme la
  page la pèse, et la mortalité du stock aussi (A-2, B-13) ; l'étape 4 a
  trouvé de son côté, sur le flux, le même départ trop précoce de l'actif de
  la CNRACL.
- **Étape 5, les cas types** : l'agent de la CNRACL, à scinder entre
  sédentaire et actif ou à faire partir à 61 ans (B-5), avec son niveau de
  fin de carrière, qui le range dans son vingtile ; le civil de l'État, sans
  catégorie active ni carrière longue ; le second métier du militaire. Le
  test des moins de soixante ans cédera ce jour-là, et le paragraphe des
  limites avec lui.
- **Une session du modèle, à part** : la table de 2025 interpolée entre les
  quotients observés de 2024 et projetés de 2026, en Python et en
  JavaScript ; les décès des droits dérivés en sont le contrôle.
- **La fiche `categorie_active`** d'`avantages_non_contributifs.yaml` reprend
  la table d'un récit de `docs/avantages_non_contributifs.md` (7,5 Md€ de
  classement en 2024, 13,7 en tout, 3,8 de carrière longue) ; les limites
  portent ceux du jour, ancrés (8,3, 12,5 et 1,9).

*Ce qui reste.* Rien pour l'étape 7.
