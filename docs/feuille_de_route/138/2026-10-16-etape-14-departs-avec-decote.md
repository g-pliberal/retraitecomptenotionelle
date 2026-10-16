# Étape 14, deuxième partie : la population part aussi avec une décote, la quinzième version

**Le 16 octobre 2026 : une part des carrières incomplètes de la population
part à l'ouverture du droit, avec une décote, au lieu d'attendre toutes le
taux plein — la part des départs avec décote que l'EIR mesure aux résidents de
chaque sexe, 8,8 % des femmes et 4,5 % des hommes. Sans calage sur les
quintiles, les femmes du premier quintile de la pension en équivalent carrière
complète partent avec une décote à 15,7 %, pour 17,5 dans l'EIR, celles des
autres à 1,9 à 2,9 %, pour 4,6 à 5,4. La pension moyenne des femmes en 2020
passe de 1 340 à 1 317 € par mois (1 177 dans l'EIR), leur premier décile de
491 à 434 € (283) ; celle des hommes de 1 803 à 1 772 €, qui s'éloigne de
l'EIR (1 957). Sur la page, presque rien : l'écart des années observées de la
population passe de −1,47 à −1,36 point au scénario 2.**

Demande : la vague du 16 octobre 2026, session 3, « action 138, étape 14. La
population […], en commençant par ce que la mesure accuse : le salaire des
femmes, puis, si l'étape le permet, une dispersion de carrière et les
générations ».

- *Ce que la demande nommait était fait.* Le salaire des femmes rapporté à
  celui des hommes (`dispersion_salaires_sexe.csv`), une dispersion de
  carrière, les carrières des femmes selon leur génération : l'action 136
  (étape 6, archivée) les a mis dans la population les 11 et 12 octobre, en
  quatorze versions, après la note du 7 octobre qui les demandait. Le bloc
  « Reprise » de l'étape datait d'avant elles. Ce que la mesure accusait
  encore, aux limites (`docs/limites/5-bis-cout-agrege.md`, « La population,
  arrêtée le 12 octobre 2026 ») : les femmes trop haut, et deux manques, les
  départs avec décote et une part au minimum selon la génération. Le premier
  manque est le point 3 de cette étape, les départs choisis, par son bout le
  plus simple ; c'est lui qui est fait.
- *La forme* (`DEPARTS_AVEC_DECOTE`, `parts_avec_decote`,
  `departs_avec_decote`, `scripts/grille_large.py`). Chaque carrière
  incomplète du salariat et des non-salariés (`incomplete`) se dédouble : une
  part, la même pour tout le sexe, part sous la règle `ouverture` des cas
  types, à l'âge où le droit ouvre la liquidation, et le reste au taux plein.
  La part est celle de l'EIR (`part_decote` de `quintiles_eqcc_residents.csv`,
  certifiée), divisée par le poids des carrières incomplètes parmi les
  retraités du sexe, en 2020. Partant sans le taux plein, ces carrières
  perdent aussi le minimum contributif. Deux conventions : la décote se prend
  à l'âge d'ouverture, et la part ne dépend ni du rang de salaire ni de la
  tranche de durée ; les carrières statutaires gardent leur départ.
- *La mesure* (`avec_decote`, `confronter_eqcc`). Chaque cohorte de 2020 est
  marquée décotée quand elle part avant l'âge du taux plein ET à un taux plus
  bas que lui, ou, pour un régime principal en points qui ne dit pas de taux,
  avant lui seulement ; puis rangée par quintile, contre l'EIR. Le seul âge ne
  suffit pas : l'agent de conduite né en 1958 part à cinquante ans au taux de
  75 %, la décote des régimes spéciaux ne mordant qu'aux générations
  suivantes, et l'âge seul comptait 3,1 points d'hommes décotés de trop. Deux
  tests : la part des départs pèse celle de l'EIR, et la mesure se range comme
  l'EIR (`test_grille_large.py`).
- *Ce qu'elle trouve*, en 2020, en euros par mois ; Kolmogorov : le plus grand
  écart des répartitions, et la borne où il tombe. La population « avant » est
  la quatorzième version sur le modèle du jour.

  | | moyenne | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|---|
  | ensemble, EIR | 1 536 | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, avant | 1 568 | 672 | 1 092 | 1 378 | 2 621 | −11,3 pt à 800 |
  | ensemble, quinzième version | 1 541 | 597 | 1 067 | 1 347 | 2 605 | −9,9 pt à 800 |
  | femmes, EIR | 1 177 | 283 | 703 | 1 013 | 2 229 | |
  | femmes, avant | 1 340 | 491 | 923 | 1 243 | 2 262 | −17,6 pt à 800 |
  | femmes, quinzième version | 1 317 | 434 | 907 | 1 237 | 2 253 | −16,0 pt à 800 |
  | hommes, EIR | 1 957 | 872 | 1 374 | 1 745 | 3 242 | |
  | hommes, avant | 1 803 | 901 | 1 241 | 1 587 | 2 890 | +6,9 pt à 1 800 |
  | hommes, quinzième version | 1 772 | 872 | 1 224 | 1 583 | 2 825 | +7,9 pt à 1 700 |

  Les départs avec décote, quintile par quintile de la pension en équivalent
  carrière complète, et ensemble :

  | | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | femmes, EIR | 17,5 % | 4,6 | 4,7 | 4,8 | 5,4 | 8,8 |
  | femmes, quinzième version | 15,7 % | 2,7 | 2,9 | 1,9 | 2,7 | 6,3 |
  | hommes, EIR | 13,6 % | 4,0 | 3,2 | 3,1 | 4,3 | 4,5 |
  | hommes, quinzième version | 19,4 % | 6,1 | 3,9 | 5,6 | 5,8 | 6,9 |

  Au minimum de pension, le premier quintile des femmes tombe de 83,2 à
  72,0 % (65,9 dans l'EIR), le troisième monte de 3,4 à 11,7 (18,1) ; celui
  des hommes, de 71,2 à 57,9 % (48,7). La durée validée du premier quintile
  passe de 31,3 à 30,5 années chez les femmes (28,0), de 36,7 à 35,7 chez les
  hommes (32,0).
- *Pourquoi les parts ne tombent pas sur l'EIR.* Les carrières marquées
  pèsent, en têtes, 9,2 % des femmes, mais 3,3 points d'entre elles ont la
  durée requise dès l'ouverture, avec les huit trimestres de chacun de leurs
  deux enfants — les générations 1945 à 1960 surtout — et partent sans
  décote ; s'y ajoutent 0,5 point de régimes spéciaux. Les hommes marqués
  pèsent 5,0 % et partent tous décotés ; les agents des IEG et de la
  conduite nés à partir de 1955, qui partent à l'ouverture de leur statut, en
  ajoutent 1,9. La part de l'EIR est une entrée, celle de la mesure un
  résultat : la population ne se recale pas sur elle.
- *Ce que la mesure accuse.* Le bas des femmes descend vers l'EIR sans
  l'atteindre : leur premier décile reste à 434 € pour 283, leur pension
  moyenne 12 % au-dessus. Les hommes s'éloignent, leur moyenne déjà 8 % trop
  basse : ce sont les niveaux des cas types statutaires et non salariés, que
  l'action 152 reprend, et les départs à l'ouverture des agents des régimes
  spéciaux, que l'EIR ne voit pas autant décotés.
- *Sur la page*, contre la quatorzième version sur le modèle du jour : l'écart
  des années observées passe de −1,47 à −1,36 point au scénario 2, de −3,15 à
  −2,90 aux scénarios 4 et 6 ; la part du PIB en 2070 ne bouge qu'au
  centième ; la garantie vieillesse de +0,048 à +0,042 point de PIB en 2070 ;
  le passé refait, au pire depuis 2000, de 13,5 à 13,4 %. La page ne lit pas
  la population (action 157).
- *Ce qui ne bouge pas.* Aucun moteur, aucune page, aucun témoin : la
  population n'est lue que par `grille_large.py`. Le registre non plus : aucun
  de ses points « 138.14 » ne nomme les départs avec décote. Les limites
  s'écrivent à la fin de l'étape (point 6).

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : une part au minimum qui suive les générations
   (le minimum contributif de 2023, 15,3 % des liquidants contre 18,8 dans
   l'EACR, note du 12 octobre) ; la décote selon la tranche ou le rang, si une
   source la publie par durée. Les niveaux des cas types statutaires et non
   salariés attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157).
3. *Les départs choisis*, au-delà de la décote (PRISME, SESIM, T-DYMM) :
   l'âge de départ de chaque génération selon la distribution publiée des
   âges de départ (`age_conjoncturel_depart.csv`), et la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension* (CALIPER, Oscar), au CASD, sur une
   habilitation que seul le propriétaire peut demander.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`) :
   la mesure, et ce que la population en aura corrigé, la décote comprise.
