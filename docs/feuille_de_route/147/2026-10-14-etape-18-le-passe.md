# Étape 18, le passé : les −16 % de 2009 en trois facteurs, déclarés

**Le 14 octobre 2026 : aucun calcul ne bouge. L'écart de la reconstitution
de 2009, −16,4 %, se décompose, contre l'enquête annuelle auprès des caisses
(EACR) : −6,1 % de têtes, −11,0 % de pension de droit direct par tête,
−0,1 % de réversion. Les têtes font de 2009 le pire (les départs anticipés pour
carrière longue, que la grille ne connaît pas) ; la pension par tête fait le
gros de l'écart, d'un bout à l'autre de la fenêtre. Rien de ce qui le
comblerait ne tient dans une session sans déborder sur d'autres territoires :
c'est déclaré, et une méthode, une sonde et un test le tiennent.**

- *Mesuré d'abord*, sous les réglages des tests (`memoire.cout`, Python 3.11).
  La reconstitution vaut −11,7 % en 2004, monte à −16,4 % en 2009, revient à
  −3,8 % en 2020. Rapportées à la dépense observée de la DREES, groupe par
  groupe et à 2024 : le privé (Cnav, Agirc-Arrco, RCI contre régime général,
  Agirc-Arrco, salariés agricoles et autres non-salariés) −22 % en 2000,
  −19 % en 2009, et fait 13,7 des 16,4 points de 2009 ; la FPE passe de
  +11 % en 2004 à −14 % en 2009, pour 3,2 points — la dépense observée de
  l'État fait +9,8 % réels en 2006, l'année du compte d'affectation spéciale
  « Pensions », quand ses têtes dans le modèle reculent de 7 % de 2007 à
  2009.
- *Les trois facteurs* (`Avenir.reconstitution_decomposee`). L'EACR
  (`regimes/effectifs_retraites.csv`, caisse `tous_regimes`) compte les
  PERSONNES qui ont un droit direct, de 2004 à 2024 ; `macro/droits_derives.csv`
  la masse de la réversion. Le produit des trois rapports est la
  reconstitution, au millième de point :

  | | 2004 | 2006 | 2007 | 2009 | 2010 | 2012 | 2015 | 2018 | 2020 | 2022 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | reconstitution | −11,7 | −15,1 | −16,0 | −16,4 | −14,7 | −10,6 | −9,5 | −5,9 | −3,8 | +0,9 |
  | têtes | +0,2 | −2,9 | −4,2 | −6,1 | −6,1 | −3,2 | −4,5 | −3,7 | −1,7 | −0,7 |
  | pension par tête | −10,2 | −11,7 | −11,8 | −11,0 | −9,0 | −7,9 | −5,2 | −2,4 | −2,2 | +1,7 |
  | réversion | −1,9 | −0,9 | −0,6 | −0,1 | −0,2 | +0,3 | 0,0 | +0,1 | 0,0 | −0,2 |

- *Les têtes.* Elles suivent l'enquête en 2004, s'en écartent jusqu'en 2009
  et 2010, puis y reviennent. Celles de la Cnav, contre la caisse : −4,1 %
  en 2004, −9,2 % en 2009, −5,5 % en 2012. C'est le dessin des départs
  anticipés pour carrière longue, ouverts en 2004 et resserrés en 2009 : l'âge
  conjoncturel de départ des hommes tombe de 60,06 à 59,88 ans de 2004 à 2008,
  et remonte à 60,15 en 2010 (`macro/age_conjoncturel_depart.csv`). La grille
  n'en a pas : ses cas types partent à l'âge du taux plein. Vraisemblable,
  non démontré : le dépôt n'a pas les départs anticipés par année.
- *La pension par tête.* Elle croît, de 2004 à 2024, de dix points de plus
  dans le modèle que dans les comptes : le défaut que la décomposition du COR
  situe aussi dans l'avenir (étape 2). Mesuré hors du dépôt, sous
  `memoire.modele_modifie()`, en remplaçant `coefficient_actuel` : servir aux
  pensions du scénario 1, jusqu'au dernier barème, les coefficients de la
  Cnav (`legislation/revalorisation_pensions.csv`, moyenne de l'année, la
  tranche de 2 000 à 2 008 € en 2020) à toute la part qui n'est pas en
  points, déflatés des prix, et à la part de l'Agirc-Arrco la valeur de
  service de l'Arrco puis de l'Agirc-Arrco (raccordée en 1999, où l'Arrco
  change d'unité) :

  | | 1990 | 2000 | 2004 | 2009 | 2015 | 2020 | 2023 | dérive 2050 | dérive 2070 |
  |---|---|---|---|---|---|---|---|---|---|
  | aujourd'hui | −24,3 | −14,4 | −11,7 | −16,4 | −9,5 | −3,8 | +2,5 | 0,986 | 1,008 |
  | la Cnav seule | −16,9 | −10,9 | −9,1 | −14,0 | −7,2 | −3,1 | −0,1 | 1,001 | 1,023 |
  | l'Agirc-Arrco seule | −23,0 | −13,8 | −11,3 | −15,9 | −9,0 | −3,8 | +3,1 | 0,995 | 1,018 |
  | les deux | −15,4 | −10,3 | −8,6 | −13,5 | −6,7 | −3,1 | −0,1 | 1,010 | 1,033 |

  Une pension liquidée avant 2014 vaut, en 2024, 5 % de moins que la même
  revalorisée sur les prix. La correction est du droit (le scénario 1 est le
  droit applicable), mais elle ne rend que trois des seize points, et elle
  déplace l'horizon : le stock érodé s'éteint, et la masse du modèle remonte
  sur celle du COR, la pension relative de 2070 de 0,848 à 0,869 — au-delà
  du cliquet de 3 % de la décomposition. Le reste, sept à huit points, tient
  aux pensions que la grille sert aux générations anciennes, trop basses au
  regard de la dépense : les chantiers de la nuit sur l'AVPF de 1972 à 1982
  (action 131) et la pension minimum d'avant avril 1983 (138.6) y touchent.
- *Écarté, mesuré.* (a) Les poids des cas types aux bords de l'EACR : les
  civils et militaires de l'État n'y paraissent qu'en 2010, la CNRACL en
  2011, le RCI en 2013, la CNAVPL en 2020, et leur effectif est reconduit à
  plat avant ; les prolonger à rebours par des croissances plausibles (2,5 %,
  0, 5, 1 et 4,5 % l'an) déplace 2009 de 0,1 point et 2000 de −0,5 : rien.
  (b) La réversion avant 2010, la part du COR de 2010 reconduite : l'EACR la
  fait baisser de 13,3 % de la dépense de répartition en 2004 à 11,7 % en
  2009 ; la suivre relèverait 2004 de deux points et laisserait 2009.
- *Ce qui est fait.* `Avenir.reconstitution_decomposee` (`cout.py`) rend les
  trois facteurs ; la sonde `reconstitution` les dit
  (`facteur=retraites|pension|reversion`, `mesures_prose.py`) ;
  `test_la_reconstitution_se_decompose_en_tetes_pension_et_reversion`
  (`tests/test_cout.py`) garde l'identité et chacun sous un cliquet (6,5,
  12 et 2 %) ; la limite 5 ter porte un paragraphe ancré sur la sonde. Aucun
  calcul ne bouge, aucun témoin, aucun rendu de page.
- *Ce qui reste.* (1) Les revalorisations servies au scénario 1 : une
  `coefficient_actuel` historique jusqu'au dernier barème, la Cnav, la
  fonction publique (son propre fichier avant 2009), les régimes en points
  par leur valeur de service, et le même coefficient dans la masse du stock
  des réformes prospectives (`MASSE_STOCK`), qui est la pension du scénario
  1 ; `cycle_de_vie.py` et l'engagement (`cout.py`, vers la ligne 4216) la
  lisent aussi, et le portage du cycle de vie (138.9) suit. À faire dans une
  session qui accepte de relever le cliquet de la pension relative, la
  correction démasquant le défaut de l'horizon. (2) Les départs anticipés
  pour carrière longue de 2004 à 2008, à la grille (action 152).
  (3) Les pensions des générations anciennes, après l'AVPF et la pension
  minimum.
- *Au propriétaire.* Rien de neuf à trancher. La correction (1) changera les
  chiffres de la proposition, dont le coût est celui du COR multiplié par le
  rapport de sa masse à celle du scénario 1 : le stock érodé abaisse la
  seconde, et relève ce coût dans les années 2030 — de combien, ce n'est pas
  mesuré.
