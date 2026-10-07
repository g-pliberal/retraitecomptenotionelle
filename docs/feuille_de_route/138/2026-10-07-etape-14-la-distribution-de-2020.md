# Étape 14, première partie : les pensions de 2020, simulées contre publiées

**Reprise, au 7 octobre 2026.** Fait : la validation publique — chaque grille
de la page Coût lue en 2020, en têtes, sa distribution des pensions confrontée
à celle que l'EIR publie (`grille_large.py --distribution`) ; trouvé en chemin,
le niveau « faible » qui arrêtait les deux moteurs pour les mères de l'IEG, de
la RATP et de la CRPCEN. Reste, dans cet ordre : la population (action 136,
étape 6, seconde moitié), qui commence par ce que la mesure accuse — le salaire
des femmes, une dispersion de carrière, les générations — et se juge sur elle
sans s'y caler ; les départs choisis ; le recours à l'ASPA ; la confrontation
pension par pension, au CASD. Au propriétaire : les réglages de la page Coût
(action 150), l'habilitation au CASD. Détail : plus bas, « Ce qui reste ».

**Le 7 octobre 2026, la demande.** Le propriétaire : « 138.14 ». L'étape :
« Ce qui demande une population ou des microdonnées, avec l'action 136 (étape
6) : une population simulée, des départs choisis, la validation sur des
pensions réelles (l'EIR, au CASD) ». Le registre y range quatorze points de
douze modèles, en quatre familles : la population (Destinie 2, TRAJECTOiRE,
Pensionsmodellen, T-DYMM deux fois, FUS23, ILO/PENSIONS), les départs (PRISME,
SESIM, T-DYMM), la validation (CALIPER, Oscar, MOSART) et le recours à l'ASPA
(Ines).

**Par où commencer : la validation.** Une population doit redonner les
pensions qu'on observe avant de projeter quoi que ce soit, et la mesure qui le
dit juge ensuite chaque pas. Elle n'a pas besoin du CASD : l'EIR publie la
distribution des pensions de droit direct par sexe, en tranches de cent euros —
le tableau 1 du classeur de 2020, « y compris majoration pour trois enfants »,
relu le jour même sur l'API de la DREES —, et la moyenne et les quantiles des
résidents en France ; le dépôt les certifie déjà (`distribution_pensions.csv`,
`pensions_residence.csv`). Ce que MOSART fait sur les déclarations fiscales, le
dépôt le fait sur elles.

**Ce qui est fait.**

- *La mesure* (`scripts/grille_large.py`, « La distribution des pensions,
  contre celle de l'enquête »). Chaque grille lue l'année de l'enquête en
  têtes — celles que la page compte : chaque cohorte pesée par son effectif
  INSEE, chaque cas type par son poids de la page, recalé sur les groupes du
  COR —, chaque pension de droit direct du scénario 1, sans ASPA, revalorisée
  comme la page la revalorise et ramenée en euros de 2020 ; puis, sexe par
  sexe, la moyenne, les quantiles publiés et le plus grand écart des fonctions
  de répartition aux bornes des tranches (Kolmogorov). `--distribution` s'en
  tient à la simulation, sans la page : sept secondes pour la grille du dépôt,
  sept minutes pour la grille élargie, sur quatre cœurs. Deux tests en
  tiennent la mécanique : ses têtes et ses euros sont ceux de `cout._masses`,
  la complétude des cohortes ôtée ; l'enquête, mise en atomes au milieu de ses
  tranches, se redonne elle-même, sans écart aux bornes et à une tranche près
  sur les quantiles.
- *Ce qu'elle trouve*, en euros de 2020 par mois ; la part sous 900 €, et
  l'écart de Kolmogorov, en points, à la borne où il tombe (positif : la grille
  a trop de retraités sous elle).

  | 2020 | moyenne | d1 | médiane | d9 | sous 900 € | Kolmogorov |
  |---|---|---|---|---|---|---|
  | EIR, résidents en France | 1 536 | 402 | 1 382 | 2 730 | 30,0 % | |
  | grille du dépôt, 13 cas types | 1 792 | 939 | 1 690 | 3 124 | 8,4 % | −22,4 à 1 400 € |
  | grille élargie, 791 | 1 436 | 478 | 1 197 | 2 603 | 31,3 % | +9,9 à 1 300 € |
  | femmes, EIR | 1 177 | 283 | 1 013 | 2 229 | 45,3 % | |
  | femmes, grille du dépôt | 1 682 | 1 591 | 1 690 | 1 812 | 0,0 % | −68,3 à 1 400 € |
  | femmes, grille élargie | 1 329 | 386 | 1 126 | 2 435 | 35,9 % | −11,1 à 800 € |
  | hommes, EIR | 1 957 | 872 | 1 745 | 3 242 | 12,1 % | |
  | hommes, grille du dépôt | 1 810 | 902 | 1 785 | 3 464 | 9,8 % | +8,8 à 1 100 € |
  | hommes, grille élargie | 1 558 | 647 | 1 229 | 2 768 | 26,1 % | +26,6 à 1 300 € |

- *Ce qu'elle accuse.* La grille du dépôt n'a pas de bas : 8 % de ses
  retraités sous 900 € quand l'EIR en compte 30 %, une moyenne de 17 % trop
  haute, et pour toutes femmes une carrière, l'interrompue, à 0,9 fois le
  salaire moyen. Ce que la page en tire tient pourtant : ses masses sont
  ancrées sur la dépense observée, et ce qui dépend du bas — la garantie, le
  minimum vieillesse — se chiffre sur la distribution de l'EIR, non sur la
  grille. La grille élargie a un bas, au mauvais sexe : ses femmes touchent 13 %
  de trop, ses hommes 20 % de moins, et l'écart des sexes y est de 15 % quand
  l'EIR en mesure 40. Les axes en séparent les causes probables. Chaque sexe
  reçoit le salaire de son cas type, celui des deux sexes ensemble : les
  hommes de la grille du dépôt, à carrière complète, touchent déjà 7 % de
  moins que ceux de l'EIR, et les durées de l'EIR seules (l'axe des
  interruptions) laissent les femmes à 1 441 €. Et l'axe des salaires étale
  chaque cas type sur toute la coupe du privé, quand les treize cas types en
  couvrent déjà les niveaux : il fait tomber la médiane des hommes de 1 785 € à
  1 299, quand l'EIR la met à 1 745.
- *Trouvé en chemin : « faible ».* Les versions supposées des bonifications
  pour enfants de l'IEG et de la RATP (pensions d'avant juillet 2008) et de la
  CRPCEN (d'avant le 30 décembre 1990) portaient `fiabilite: faible` dans les
  paramètres que les deux moteurs lisent, qui ne connaissent que quatre
  niveaux : le calcul de toute mère de ces régimes partie avant ces dates
  s'arrêtait sur « niveau de fiabilité inconnu ». Elles portent `estimee`, le
  niveau d'une reconstitution, et un test exige qu'une fiabilité lue soit un
  niveau connu (`test_carte.py`). La grille du dépôt n'a pas de ces mères ; la
  grille élargie en perdait 182 couples, les grilles des femmes et des
  interruptions 13 chacune, et les mesures de l'étape 6 de l'action 136 ont été
  faites sans elles. Aucun témoin ne bouge ; le paquet du site, que GitHub
  refait, porte les fiches corrigées.
- *La mesure de l'étape 6 de l'action 136, refaite* sur le modèle du jour, les
  182 couples rendus. La grille élargie déplace l'écart des années observées de
  −2,51 points au scénario 2 et de −4,94 aux scénarios 4 et 6 (−4,55 et −8,03
  le 5 octobre) ; la part du PIB en 2070 ne bouge plus au système actuel, que
  l'action 147 a depuis calé sur le COR (15,30 %), et baisse de 0,21 point à la
  proposition (+0,11 le 5 octobre) ; le solde moyen de la proposition passe de
  −0,75 à −0,40 point de PIB (de −0,52 à −0,25) ; la garantie vieillesse
  prend 0,085 point de PIB en 2070, un quart de plus (0,051) ; le passé se
  refait à 12,8 % au pire depuis 2000, contre 16,4 % sur la grille du dépôt
  (12,9 et 19,9). Le modèle ayant changé entre-temps, ces écarts ne disent pas
  le seul correctif ; ils disent que la population reste justifiée. Ils
  précèdent l'étape 3 de l'action, publiée le même soir, qui ramène à la
  moitié la part des reportés en emploi : la page dit depuis −0,90 point de
  solde moyen à la proposition, sur la grille du dépôt. La distribution de
  2020, qui ne lit que le scénario 1, n'en bouge pas.
- *Le registre.* Le point de MOSART, la distribution simulée confrontée à
  l'observée, est repris, la mesure et son verdict écrits à son point ; les
  treize autres restent à reprendre.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population* (action 136, étape 6, seconde moitié), tirée des
   distributions publiées, génération par génération, et jugée sur la mesure,
   sans s'y caler, ce qui la viderait de son sens. D'abord ce qu'elle accuse :
   le salaire des femmes rapporté à celui des hommes (INSEE, salaire en
   équivalent temps plein par sexe, une source à certifier), et une dispersion
   de carrière au lieu de la coupe de l'année ; puis les parts de l'EIR par
   génération, où elles se publient — la durée par génération et par sexe est
   déjà là (`duree_assurance_generations.csv`). La grille élargie en est le
   premier jet, et son script l'outil.
2. *La page qui lit ses agrégats*, quand le propriétaire aura tranché ce que
   deviennent ses réglages (action 150).
3. *Les départs choisis* (PRISME, SESIM, T-DYMM) : l'âge de départ de chaque
   génération selon la distribution publiée des âges de départ, au lieu du seul
   taux plein.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension* (CALIPER, Oscar) : l'EIR et l'EIC au
   CASD, sur une habilitation que seul le propriétaire peut demander ; en
   attendant, les agrégats publiés du flux de pensions de l'État (annexe
   « pensions » du PLF).
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`) :
   la mesure, et ce que la population en aura corrigé.
