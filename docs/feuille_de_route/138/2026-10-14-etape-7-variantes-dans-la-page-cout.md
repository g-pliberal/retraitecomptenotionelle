# Étape 7, quatrième partie : les hypothèses d'espérance de vie basse et haute dans la page Coût

**La demande.** Le propriétaire, le 14 octobre 2026, l'action 147 close sur
l'écart déclaré à l'horizon : « action 138, étape 7, les variantes
d'espérance de vie basse et haute dans la page Coût […]. Le modèle et ses
chiffres ; leur affichage revient à une session du site. » C'est le point 1
de « Ce qui reste » de la troisième partie (note du 13 octobre), moins les
pages. Ni `pages.js`, ni `index.html`, ni la saisie ne sont touchés.

**Ce que la source publie, lu le jour même.** L'INSEE publie chaque scénario
des projections de population 2026 sur sa page : les six qui ne diffèrent du
central que par une composante sur
https://www.insee.fr/fr/statistiques/8990856, dont `14_ev_basse.xlsx` et
`13_ev_haute.xlsx`, de même disposition que `00_central.xlsx` (onglets
`population`, `deces`, `hyp_mortaliteF`…). La pyramide du 1er janvier 2025 est
la même sous les trois hypothèses, qui tiennent les décès de 2024 pour
observés ; elles s'écartent dès 2026. En 2070, les 65 ans et plus sont
19,25 millions sous la basse, 21,08 sous la centrale, 23,03 sous la haute ;
les 85 ans et plus, 4,32, 5,41 et 6,79 millions ; les 20-64 ans, 33,87, 34,08
et 34,22 millions.

**Ce qui est fait.**

- *Le récupérateur* (`scripts/fetch/insee_projections_population.py`) lit
  aussi les deux classeurs (`--variantes BASSE HAUTE` hors réseau, et sans
  argument avec le central), tire de chacun les deux séries du central, les
  contrôle comme lui, puis vérifie que les deux scénarios couvrent les mêmes
  cases, ne diffèrent pas avant 2026, et que la basse compte chaque année
  projetée moins de 65 ans ou plus que la haute.
- *La certification* écrit `population_par_age_variantes.csv` (4 950
  effectifs) et `population_active_variantes.csv` (90), de 2026 à 2070, au
  niveau `projetee`. `sources.yaml`, la méthodologie et la ligne des limites
  (`1-certification.md`) le disent ; l'en-tête des quotients des variantes
  ne dit plus que la page Coût les ignore.
- *La pyramide* : `Population(racine, hypothese_esperance_vie)` remplace par
  ceux de la variante les effectifs et les 20-64 ans d'après 2025 ; une
  hypothèse inconnue, ou une variante dont le fichier manque, est refusée.
  `memoire.cout`, `memoire.avantages`, `leviers` et `contexte` la construisent
  sous l'hypothèse des paramètres ; `calculer_cout` et `calculer_avantages`
  refusent une pyramide d'une autre hypothèse que leur simulateur
  (`Population.verifier_hypothese`), et `pour_la_projection` ne refuse plus
  rien.
- *La dépense du COR suit la variante.* La base du système actuel est la
  dépense que le COR projette, sous la seule mortalité centrale : sous une
  variante, elle ne bougeait pas, et les autres systèmes, tirés d'elle par
  leur rapport de masses, portaient seuls la longévité — la proposition
  semblait coûter moins sous la haute, et son solde s'améliorer de
  0,65 point en 2070. Chaque année projetée, elle est désormais multipliée
  par ce que la pyramide de la variante change à la masse du système
  actuel, les mêmes pensions comptées dans les deux pyramides
  (`AvenirAnnuel.facteur_esperance_vie`, 0,919 et 1,085 en 2070), dans la
  trajectoire comme dans le bilan. Les ressources du COR ne bougent pas, ni
  les arrivées tardives : sous les variantes, leur manque ne bouge que de
  deux dix-millièmes au plus. Sous la centrale, le facteur vaut un : aucun
  chiffre de la page ne bouge.
- *Les tests* : la pyramide suit l'hypothèse, commune jusqu'en 2025, une
  variante absente refusée (`test_donnees.py`) ; la page Coût sous les deux
  variantes, ci-dessous, et le refus d'une pyramide d'une autre hypothèse
  (`test_cout.py`, `test_moteur.py`).
- *Le registre* : les cinq points sur ce que le diviseur absorbe d'un choc de
  longévité (modello_rgs, modele_lettonie, ageing_report, fus23,
  maquette_globale_cor) passent à `repris`, avec la mesure.

**Ce que la variante déplace, mesuré le jour même**, en part de PIB, sous les
réglages de la page (basse / centrale / haute) :

| | 2050 | 2070 | solde 2070 | solde moyen 2026-2070 |
|---|---|---|---|---|
| Système actuel | 13,78 / 14,37 / 15,04 | 14,05 / 15,30 / 16,61 | −1,14 / −2,39 / −3,70 | −0,58 / −1,13 / −1,75 |
| Proposition (notionnel libéral) | 9,87 / 9,70 / 9,48 | 8,06 / 8,10 / 8,10 | +0,11 / +0,06 / +0,07 | −1,14 / −1,01 / −0,82 |
| Compte rétroactif | 4,59 / 4,49 / 4,37 | 4,63 / 4,61 / 4,54 | +7,31 / +7,33 / +7,40 | +7,90 / +7,98 / +8,09 |
| Compte prospectif | 10,82 / 11,04 / 11,35 | 6,77 / 7,03 / 7,36 | +5,18 / +4,91 / +4,58 | +1,83 / +1,65 / +1,41 |

Le rapport de dépendance (65 ans et plus sur 20-64 ans) passe, en 2070, de
0,619 à 0,568 et 0,673.

- *Le système actuel* bouge de −1,25 et +1,31 point en 2070 ; le COR publie
  −1,00 et +1,05 (14,30 et 16,35 %, rapport annuel 2026, fig. 2.18 à 2.20). Le
  modèle va dans le même sens, un quart plus fort : sa masse suit la seule
  pyramide, sans les rétroactions du COR (âges de départ, effectifs par
  régime).
- *La proposition* ne bouge pas en 2070 : son diviseur absorbe trois ans
  d'espérance de vie, en dépense comme en solde. Avant, la transition la fait
  un peu bouger — 2050 : +0,17 point sous la basse, −0,22 sous la haute, où
  ses nouvelles pensions, plus petites sous la haute, pèsent plus que ses
  têtes en plus — et son solde moyen sur 2026-2070 va de −1,14 à −0,82. C'est
  le résultat que l'Ageing Report publie pour la Lettonie (+0,1 point pour
  deux ans d'espérance de vie) et que le RGS publie pour l'Italie.
- *Le compte prospectif* garde les pensions liquidées avant la bascule, sans
  diviseur : sa dépense suit la longévité à moitié en 2070.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les pages*, par la session qui les tient : la page Coût sous les deux
   variantes (un réglage à côté du scénario macroéconomique, ou un tableau
   des trois), et les pages du simulateur (« Ce qui devrait s'écrire dans les
   pages », note du 13 octobre). La page qui agrège n'a plus à rester sous la
   centrale.
2. *Les variantes de fécondité et de migration* de la page Coût, que le
   registre demande avec les mêmes figures du COR : les classeurs
   `11_fec_haute.xlsx` à `16_smi_bas.xlsx`, sur la même page de l'INSEE, ont
   la même disposition. Elles ne touchent pas le diviseur, mais la recette et
   les arrivées tardives : ce n'est pas le geste de ce jour.
3. *La mortalité différentielle* des cas types, *les départs qui suivent
   l'espérance de vie*, *la queue observée* de 85 à 98 ans, *2025* sous la
   loi seule : inchangés.
