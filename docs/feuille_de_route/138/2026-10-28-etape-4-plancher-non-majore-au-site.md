# Étape 4, suite de la seizième partie : le plancher que les majorations de 1972 à 1982 ne relèvent pas, que la carte de la pension d'aujourd'hui dit

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le dernier point « Au site » du bloc de
l'étape, « le plancher non majoré », détaillé au point 3 du « Ce qui reste »
de la seizième partie (`2026-10-25-etape-4-majorations-comparees-au-plancher.md`)
— la phrase de la carte qui dirait le plancher que les majorations ne relèvent
pas (`plancher_non_majore`). Ce point seul, à la suite des études, de l'enfant
né après le départ, des révisions, de la catégorie, de la période et de son
moment.

**La carte.** La demande disait celle de la réversion. `plancher_non_majore`
est un champ de `RegimeServi`, ce que « faire vivre » mène de la pension du
retraité jusqu'à l'échéance ; la réversion, calculée « avant comparaison au
minimum », garde la pension des cotisations, majorée, et ne lit aucun plancher
(seizième partie). La seule carte qui montre la revalorisation de chaque
régime est « Votre pension, de votre départ à aujourd'hui »
(`pensionDAujourdhui`) : c'est elle que la phrase complète, et la carte de la
réversion ne change pas.

**Ce qui est fait.**

- *La carte* (`pages.js`) : la cellule « Règle suivie » du régime dont le
  plancher n'a pas toutes les majorations dit ce qu'il en retire, par mois,
  aux euros de la page : « coefficients de l'article L. 161-23-1, date après
  date (moins 15,33 € : portée à la pension minimum, plancher que les
  majorations forfaitaires de 1972 à 1982 comprises dans sa revalorisation ne
  relèvent pas) ». Sans elle, le montant du départ, multiplié par la
  revalorisation de sa ligne, donnait plus que celui de 2026, sans que rien dise
  pourquoi. Le plancher est le plus haut de ceux que la liquidation a comparés
  (`PensionRegime.planchers`), le premier à égalité : la pension minimum avant
  l'AVTS de l'ex-invalide, comme le dit le détail de la liquidation. Son nom, et
  ce que les majorations en relèvent, viennent de `PLANCHERS_NON_MAJORES`,
  comme la fiche les répartit : rien de la pension minimum ni de l'AVTS ; de la
  pension d'invalidité, les seuls 6 % et 4 % de 1982, qui « ne relèvent pas
  toutes ».
- *Le test* (`test_web_revues.py`), posé à la main depuis les circulaires et vu
  rouge : le salarié parti en avril 1970, porté à la pension minimum,
  20,96 € × 12,9220 × 6/106 = 15,33 € ; l'ex-invalide d'avril 1969 porté à la
  pension minimum, 19,69 € × 13,8886 × 6/106 = 15,48 € ; celui que sa pension
  d'invalidité relève, et les 6 % de 1982 avec elle, sans parenthèse.

**Les mesures.** Le premier touche en 2026 255,54 € par mois du régime
général, au lieu des 270,85 € que sa revalorisation mènerait ; l'ex-invalide,
258,01 € au lieu de 273,47 € ; l'ASPA, qui les porte l'un et l'autre à
1 043,59 € par mois, leur rend l'écart. Aucun témoin de page ne bouge : les
douze qui portent la carte se rendent à l'identique, aucun n'étant porté à un
plancher non majoré, et les neuf pages toutes faites restent à jour
(`construire_pages.py --verifier`). Dans Chromium, par le pilote de
`test_ecrans.py`, aux cinq largeurs, dépliants fermés et ouverts, les pages des
deux premiers ne débordent pas, ne chevauchent aucune case et ne lèvent ni
erreur ni alerte ; à 390 points, la parenthèse se lit sous la règle de la
ligne repliée. Ici, sur les fichiers fabriqués de `main`, périmés, échouent
avant comme après ce commit les sept confrontations de `-m rapide` (le pont,
les coupures au mois, la surcote parentale, le cycle de vie) et, au niveau
`site`, les témoins du portage (`simulations.json` périmé, 102 écarts sur
909 cas).

**Ce qui reste.**

1. *Au site*, ce que les notes des révisions (point 2 de leur « Ce qui reste »)
   et de la période (point 2) ont vu en chemin, à des sessions suivantes.
2. *Au site*, vu en chemin : la carte de la réversion dit « de minimum
   contributif » la part que la réversion ne compte pas ; l'étape « compléter »
   écrit sous ce code la pension minimum d'avant avril 1983 et le plancher de
   la pension substituée, que le libellé de leur avantage nomme (« Pension
   minimum (AVTS) », « Plancher de la pension substituée »).
3. *Au site*, vu en chemin : la composition sous le montant du système 1
   (`etagesActuels`) mène chaque ligne par son seul coefficient ; la somme
   dépasse alors le total de ce que le plancher retire, et la page la tait. Le
   retraité de 1970 n'en lit aucune, quand l'ex-invalide que sa pension
   d'invalidité relève lit « 459 € de retraite de base + 22 € de retraite
   complémentaire + 563 € de minimum vieillesse ». À la lecture du code, de
   même pour toute ligne que « faire vivre » révise (la révision du minimum, la
   majoration de 2023, le relèvement des exploitants, les plans, la majoration
   pour conjoint, le maximum du jour) : la pension servie de chaque régime
   (`aujourd_hui`) la rendrait.
