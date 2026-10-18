# Étape 14, huitième partie : les départs choisis — la surcote, et les départs des nés en 1950 et 1953 contre l'EIR

**Le 18 octobre 2026 : la population part aussi après l'âge légal et le taux
plein, avec une surcote, et ses départs se jugent désormais génération par
génération, sur ceux des nés en 1950 et en 1953 que l'EIR publie
(`departs_generations.csv`, certifié). Aucun de ses départs ne surcotait ;
9,2 % de ceux de la génération 1955 le font, pour 14,4 % des nés en 1953, et
la part des départs pris entre l'âge légal et l'âge d'annulation de la décote
passe de 12,9 à 20,0 % (26,6). La mesure accuse surtout les carrières
longues des hommes : 37,1 % de ceux de la génération 1955 partent avant l'âge
légal en carrière longue, pour 28,6 % des nés en 1953 (44,9 % avant), parce
que toutes leurs carrières pleines entrent assez tôt pour y avoir droit. La
page, qui ne lit pas la population, ne bouge pas.**

Demande : la vague du 17-18 octobre 2026, lot 2, lancée par la session
d'orchestration sur la demande du propriétaire, « Fait toutes les tâches qui
n'ont pas besoin de mes décisions » : le point « les autres départs choisis »
du bloc « Reprise » de l'étape — le point 3 de « Ce qui reste », « les
départs choisis, au-delà de la décote : l'âge publié, la surcote » —, sans
choisir d'hypothèse que le propriétaire n'a pas tranchée.

- *Ce qui relève du propriétaire, et ce qui n'en relève pas.* Un départ qui
  suivrait l'incitation — partir plus tard parce que le diviseur ou la
  surcote récompensent l'attente — est un choix de modèle : le registre le dit
  `a_trancher` au point de TRAJECTOiRE (« le comportement inchangé est un
  choix écrit »), et PRISME le fait par 48 équations logistiques
  (`a_reprendre`). Cette session n'y touche pas : chaque carrière part au même
  âge dans chaque scénario, comme avant. Ce qu'elle fait est de la famille des
  départs avec décote du 16 octobre : une part publiée en entrée, des
  conventions déclarées, une mesure qui juge.
- *La source* (`scripts/fetch/drees_departs_generations.py`,
  `macro/departs_generations.csv`, certifiée, `drees_eir_generations`). Le jeu
  des caractéristiques des retraités de la DREES joint, à chaque millésime,
  le classeur d'une génération que l'enquête voit presque toute partie : les
  nés en 1950, en 2016, à 66 ans ; les nés en 1953, en 2020, à 67. Trois
  feuilles de chacun, par sexe : l'âge de liquidation dans le régime
  principal ; la place du départ — avant l'âge légal, à lui, entre lui et
  l'âge d'annulation de la décote, à ce dernier, après ; la condition de
  liquidation — carrière longue, décote, décote inapplicable, surcote,
  invalidité, inaptitude, autre motif, taux plein par l'âge, par la durée ;
  et, dans les deux premières, la part de chaque condition parmi les départs
  de chaque colonne. Le lecteur vérifie que les colonnes redonnent
  l'ensemble ; le classeur laisse un retraité sur cent sans condition connue,
  une femme née en 1953 sur neuf parmi celles parties à 65 ans. Les tests
  (`test_departs_generations.py`) : le lecteur, sur des grilles rendues comme
  les classeurs, et les valeurs que les classeurs impriment.
- *La mesure* (`departs`, `confronter_departs`, `condition_au_depart`,
  `grille_large.py --distribution`, nouveau tableau). La grille 1950 contre
  les nés en 1950, la grille 1955 contre les nés en 1953, la plus proche que
  l'enquête voie : chaque génération comptée à l'âge où l'enquête voit la
  sienne, ses seuls départs déjà pris, chaque cas type au poids de la page et
  à sa survie propre (`cout._survies_alignees`, comme le veut la réparation
  de la nuit, `18cd970`). La place et la condition se comparent pour les deux,
  l'âge pour la première seule : l'âge légal des nés en 1953, 61 ans et
  2 mois, n'est pas celui de la grille 1955, 62 ans. Les conditions de l'EIR
  se lisent parmi les départs dont la condition est connue, en cinq classes :
  la population n'a ni invalides ni inaptes, et ce qu'elle fait partir au
  taux plein d'un statut, l'EIR le dit « décote inapplicable » ; les trois
  vont au « taux plein, autrement », avec le taux plein par la durée.
- *La surcote* (`DEPARTS_AVEC_SURCOTE`, la dix-neuvième version ;
  `parts_avec_surcote`, `attentes_des_surcotes`, `departs_avec_surcote`).
  Chaque carrière du salariat et des non-salariés de trente années validées
  et plus, qui part au taux plein (`peut_surcoter`), se décline : la part de
  son sexe que l'EIR voit surcoter parmi les carrières complètes des nés en
  1953 — 14,2 % des femmes surcotent, dont 87,4 % à carrière complète, quand
  57,3 % de toutes en ont une : 21,7 % ; 17,7 % des hommes — attend après
  l'âge légal ce qu'attendent leurs départs avec surcote ; le reste part au
  taux plein. Les attentes : chaque âge de liquidation des nés en 1953 au
  milieu de l'âge, compté de l'âge légal, en trois groupes — les deux
  premières années, 1 an et 2 mois en moyenne, un tiers des femmes surcotées ;
  le reste d'avant l'année où s'annule la décote, 3 ans et 1 mois, près de la
  moitié ; cette année-là et au-delà, 5 ans et 5 mois, près d'un cinquième.
  Quatre
  conventions. L'attente se compte de l'âge légal, jamais avant le taux plein
  : une carrière longue qui surcote renonce à partir avant l'âge légal. Trois
  attentes et non sept, une par âge : la page pèse ses carrières une à une, à
  un coût qui croît comme leur carré, et sept attentes portaient la mesure de
  13 à 53 minutes ; deux âges par deux âges, la dernière tombait pile à l'âge
  d'annulation, d'où le regroupement autour de lui. La part ne dépend ni du
  rang de salaire, ni de la génération, sinon qu'aucune n'attend avant 2004,
  où naît la surcote (`ANNEE_DE_LA_SURCOTE`, fiche `surcote_regime_general`).
  Les statutaires gardent leur départ. Trois tests (`test_grille_large.py`) :
  la part et les attentes lues dans l'EIR, la déclinaison qui les pèse, et
  le départ d'un homme de la génération 1955 qui surcote au lieu de partir
  en carrière longue, de même qu'une femme, quand la génération 1940 n'attend
  pas.
- *Ce que la mesure trouve*, en part des départs de la génération, la
  génération de l'EIR entre parenthèses ; « avant », la population d'hier :

  | grille 1955 (nés en 1953) | avant | après | EIR |
  |---|---|---|---|
  | avant l'âge légal | 30,2 | 26,4 | 30,9 |
  | à l'âge légal | 40,2 | 35,1 | 31,2 |
  | entre lui et l'âge d'annulation | 12,9 | 20,0 | 26,6 |
  | à l'âge d'annulation | 16,8 | 16,5 | 8,3 |
  | après lui | 0,0 | 2,0 | 3,1 |
  | carrière longue | 21,6 | 17,9 | 20,5 |
  | décote | 3,9 | 4,0 | 10,7 |
  | surcote | 0,0 | 9,2 | 14,4 |
  | taux plein par l'âge | 15,7 | 15,5 | 10,0 |
  | taux plein, autrement | 58,8 | 53,5 | 44,4 |

  Par sexe, la surcote vaut 9,0 % des femmes (14,3) et 9,4 % des hommes
  (14,6) ; la carrière longue, aucune femme (13,0) et 37,1 % des hommes
  (28,6, et 44,9 avant) ; l'âge légal, 59,2 % des femmes (37,5, et 68,2
  avant). La grille 1950, contre les nés en 1950 : 9,1 % de surcotés (11,8),
  17,9 % de carrières longues (11,6 ; 37,0 % des hommes pour 18,3), 18,5 %
  de départs entre l'âge légal et l'âge d'annulation (23,8), et, âge par
  âge, 35,2 % à 60 ans (46,0), 2,8 à 61 (6,8), 4,5 à 63 (3,4), 24,3 à 65
  (12,3). La distribution de 2020 bouge peu : la pension moyenne des hommes
  passe de 1 789 à 1 804 € (EIR 1 957), leur neuvième décile de 2 842 à
  2 945 € (3 242), l'écart de Kolmogorov de +7,0 à +6,1 points à 1 700 € ;
  celle des femmes de 1 336 à 1 337 €.
- *Ce que cela dit.* La surcote rapproche de l'EIR la place des départs :
  ceux d'entre l'âge légal et l'âge d'annulation passent de la moitié de
  ceux de l'EIR aux trois quarts, et l'âge légal des femmes se dégonfle. Il
  en manque un tiers : les statutaires gardent leur départ, quand l'État
  surcote deux fois plus que la Cnav — 38,9 % de ses liquidants civils de
  2024, pour 18,9 % (EACR, table H, note de l'étape 3 du 16 octobre). Le reste
  de l'écart ne tient pas à la surcote :
  - les carrières longues des hommes, deux fois trop nombreuses dans la
    génération 1950, d'un tiers de trop dans la génération 1955. Toutes les
    carrières pleines du salariat privé commencent quarante-quatre années
    environ avant l'âge légal (`ENTREE_SELON_LA_GENERATION`) : à 16 ou 17 ans
    pour ces générations, assez tôt pour y avoir droit ; dans l'EIR, une
    partie entrait plus tard. Les femmes n'en ont aucune (5,1 et 13,0 %) ;
  - les invalides et les inaptes, au taux plein dès l'âge légal sans la
    durée — 7,9 et 7,0 % des nés en 1953 —, que la population fait attendre
    l'âge d'annulation ou partir décotés : d'où le taux plein par l'âge trop
    haut (15,5 % pour 10,0) et l'âge d'annulation deux fois trop chargé ;
  - la décote, d'une part fixe (celle des retraités de 2020), quand elle
    croît d'une génération à l'autre : 6,8 % des nés en 1950, 10,6 % des nés
    en 1953.
- *Trouvé en chemin : la pesée de la page est quadratique.*
  `cout._poids_par_groupe` pèse chaque cas type seul sur toute la grille
  (`_masses_regimes`, et l'alignement des survies, pour chacun) : le coût
  croît comme le carré du nombre de cas types. La population passe de 1 452 à
  2 280 cas types, et sa mesure de 13 à 27 minutes sur quatre cœurs. Une
  pesée en une passe rendrait les mêmes poids ; c'est le code de la page, à
  la session du modèle.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur ni témoin ; les autres grilles, qui gagnent la mesure des
  départs sans changer de carrières ; le registre, dont les points de
  TRAJECTOiRE et de PRISME sur les départs restent ce qu'ils étaient. Aucune
  règle du scénario 1 : l'entrée du journal de veille ne consigne que la
  source.

**Au propriétaire.** Les départs de la population doivent-ils suivre
l'incitation du système simulé — partir plus tard quand le diviseur ou la
surcote récompensent l'attente, plus tôt sous la décote, par un modèle de
choix comme ceux de TRAJECTOiRE et de PRISME —, ou rester, comme aujourd'hui,
au même âge d'un scénario à l'autre ? C'est le point `a_trancher` de
TRAJECTOiRE au registre ; la question rejoint celle des départs qui suivent
l'espérance de vie (étape 7, note du 18 octobre). Cette session n'a rien
choisi.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : les carrières longues — une part des carrières
   pleines des hommes qui entre plus tard, et des femmes qui y ont droit,
   d'après l'âge du premier trimestre validé par génération, si une source
   le publie (EIC) ; les invalides et les inaptes, au taux plein dès l'âge
   légal ; la surcote des statutaires ; la décote selon la génération ; la
   part passagère du revenu des indépendants et la carrière saisonnière des
   salariés agricoles, si une source les publie ; le juge propre des
   artisans, la part des liquidants du RSI au minimum contributif d'avant
   2020 ; la part des générations 1946 à 1953 au minimum ; la fragmentation
   selon la génération ; la décote selon la tranche ou le rang. Les niveaux
   des cas types statutaires et non salariés, et la dispersion des libéraux,
   attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (ci-dessus).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
