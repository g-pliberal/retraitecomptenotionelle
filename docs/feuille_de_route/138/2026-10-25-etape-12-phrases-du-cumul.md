# Étape 12, quatorzième partie : les phrases du cumul aux pages — le RCI et sa complémentaire réduite, son versement unique, le notaire libéral, les mois hors de la suspension

**Le 25 octobre 2026, la demande.** Quinzième vague du lot du 24 octobre, une
session par tâche, que le propriétaire a demandé de mener sans lui : celle-ci,
le point des pages du bloc de l'étape, les phrases que les notes du 23 et du
24 octobre laissent sous « Pour les pages » (`…-cumul-et-versement-unique-du-rci.md`,
`…-la-classe-du-cumul.md`, `…-suspension-des-non-salaries.md`). Le site seul :
aucune règle ne change, ni le moteur.

**Ce que la page disait.** `cumulEmploiRetraite` rangeait dans la base toute
pension hors de l'Agirc-Arrco, et n'avait de phrase que pour le sort d'une base.

- *Le RCI, compté avec la base.* L'artisan de 2024 (`cumul_artisan_2024`) lisait
  « votre pension est réduite du dépassement, 171 € par mois en moyenne » sur
  toute son activité, base et complémentaire ensemble, quand la complémentaire,
  servie entière jusqu'en juin 2024, perd depuis juillet le dépassement comme la
  base ; celui de 2028 (`cumul_artisan_carriere_longue_2028`), « réduite de tout
  votre revenu d'activité, 2 306 € », la somme des deux.
- *Le notaire libéral*, sous le seuil (`cumul_notaire_cprn_2022`), et le dentiste
  de 2008, que les statuts de la CARCDSF suspendent dès la reprise : « le modèle
  n'a pas encore lu la règle de cumul de votre régime pour cette activité : votre
  pension est servie entière », par la phrase par défaut, quand ils perdent
  6 667 € et 7 494 €.
- *Les mois hors de la suspension* (`cumul_commercant_mois_suspendus_2013`) : la
  même phrase par défaut, d'août à novembre 2013 et de janvier à septembre 2014.
- *Le versement unique* : « une nouvelle pension de 21 € par an à la retraite
  complémentaire des indépendants — 0 trimestres, au taux plein — », au lieu de
  340 € en une fois (`seconde_pension_artisane_au_minimum_2026`).

**Ce qui est fait** (`moteur/js/pages.js`).

- *La complémentaire du non-salarié, à part.* `cumulEmploiRetraite` sépare de la
  base le RCI, le RCO et le NRCO, et la complémentaire de chaque section libérale
  (`COMPLEMENTAIRES_DU_NON_SALARIE`), et dit son sort après celui de la base, avec
  ce qu'elle perd (`sortDeLaComplementaireDuNonSalarie`) : suspendue avec elle,
  « pour la même durée » ; servie entière quand la base n'est que réduite
  (`base_reduite`) ; depuis juillet 2024, réduite « aussi » ; pour une première
  pension de 2027, « ce que votre pension de base n'en absorbe pas », ou servie
  entière quand la base absorbe toute la réduction (`imputee_sur_la_base`) ; non
  servie au notaire libéral (`notaire_liberal`) ; suspendue dès la reprise
  (`reprise`), la phrase sœur, que la note de la classe pose avec elle ; réduite,
  de son montant, pour les autres sections. Une période change avec le sort de la
  complémentaire : juillet 2024 coupe l'activité de l'artisan en deux.
- *Les mois hors de la suspension* (`hors_des_mois_suspendus`) : combien de mois
  le dépassement de l'année suspend — « qu'un mois, le dernier », « que 3 mois, les
  derniers » —, ou qu'il « n'atteint pas un mois de votre pension nette », sans
  minimum pour le libéral ; ces périodes se disent année par année.
- *Le versement unique* (`droitsDuCumul`) : la seconde retraite du RCI se dit en
  points, comme celle de l'Agirc-Arrco, et, sous quarante, « versée en une fois »,
  son capital.
- *Tests* : dix dans `tests/test_web.py` (« le cumul emploi-retraite »), sur dix
  carrières — sept témoins de simulation, l'artisan de 2028 à 30 % du salaire
  moyen, le dentiste de 2008, le médecin de 2012 à 15 % au-delà du plafond —,
  posés sur les règles des trois notes (la moitié du plafond, le plafond du
  libéral, les mois de D. 634-11-5, le seuil de quarante points de la fiche), les
  montants pris aux tranches du modèle Python ; vus rouges, chacun pour la phrase
  qui manquait.

**Mesuré.** Aucun témoin ne bouge, de page ni de simulation. L'artisan de 2024
lit deux périodes : 154 € de base par mois jusqu'en juin 2024, puis 114 € de base
et 114 € de complémentaire ; celui de 2028, 1 946 € de base et 360 € de
complémentaire ; le médecin de la CARMF (`cumul_medecin_carmf_2017`), 489 € et
481 €, au lieu de 970 € d'une seule pension.

**Ce qui reste.**

1. Aux pages : l'Ircantec, que la page compte encore avec la base — sa réduction
   d'août à décembre 2020 dans « chaque pension de base est réduite du
   dépassement, 1 131 € » (`cumul_contractuelle_ircantec_2020`), et rien de son
   allocation servie entière depuis 2021 (`sans_le_troisieme_alinea`). La RCO
   agricole, « règle non lue » comme la base de l'exploitant, n'en demande pas.
2. Les restes du bloc : la veille du projet de loi de financement pour 2027 ; au
   propriétaire, le RCO et le NRCO d'avant 2009 (action 89) et la part de base de
   l'ordre de D. 133-4 de 2016 à 2019.
