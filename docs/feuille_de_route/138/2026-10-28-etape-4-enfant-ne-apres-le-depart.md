# Étape 4, suite de la huitième partie : l'enfant né après le départ, que la saisie reçoit et que la carte de la réversion dit

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le point « Au site » du bloc de l'étape
« l'enfant né après le départ », détaillé au point 1 du « Ce qui reste » de la
huitième partie (`2026-10-24-etape-4-parts-prolongation-et-regime.md`) — la
saisie, qui refuse l'enfant né après le départ, que la majoration compte ; la
page, qui tait une majoration nulle à la date d'effet et servie ensuite. Ce
point seul, à la suite du champ des études
(`2026-10-28-etape-4-etudes-au-site.md`).

**Ce qui est fait.**

- *La saisie* (`verifierNaissances`, `verifierConjoint`) : une naissance n'est
  plus bornée au départ, « où elle ne compterait plus pour rien » : la
  majoration pour enfant à charge de la réversion compte l'enfant né après lui
  (R. 353-10), et le modèle le comptait déjà. Le décès déclaré la borne :
  l'enfant naît au plus tard trois cents jours après lui, que la loi présume
  « conçu pendant la période qui s'étend du trois centième au cent
  quatre-vingtième jour, inclusivement, avant la date de la naissance » (code
  civil, article 311, en vigueur depuis le 1er juillet 2006), comptés du
  dernier jour possible d'un décès dit à l'année ou au mois. La borne vaut
  aussi pour le décès d'avant le départ, que rien ne confrontait aux
  naissances.
- *La carte de la réversion* (`reversionDuConjoint`) : nulle à la date
  d'effet, la majoration que l'enfant né ou redevenu à charge ensuite ouvre se
  taisait. La ligne du régime qui la sert la dit en plus, à sa date, puis ce
  qu'elle devient, comme la majoration de 11,1 % qui commence après la date
  d'effet : « 114 € de plus à partir de mars 2031, majoration pour enfants à
  charge, plus rien à partir de mars 2049 ».
- *Les tests* : `test_web_saisie.py` — le père parti en 2022, dont le fils
  naît en mai 2023 et qui meurt en juin 2035 : la majoration de 113,59 € par
  mois, le barème de 2026, jusqu'au 1er juin 2041 ; les trois cents jours, au
  mois et à l'année, de part et d'autre de la borne ; `test_web.py` — l'enfant
  posthume, né en février 2031 du père mort en juin 2030, sur la ligne du
  régime général.
- *Les témoins* : deux de simulation, `reversion_enfant_ne_apres_le_depart`
  et `reversion_enfant_posthume`, et un de page,
  `simuler_reversion_enfant_posthume`, que la fabrique de GitHub refait.
- *Hors de la tâche, au site* : l'aide du champ des études portait le
  simulateur à seize phrases en tiret, quatorze au plus, et
  `test_les_incises_en_tiret_restent_rares[/simuler]` rougissait depuis le
  champ. Des parenthèses, les mêmes mots ; la page toute faite suit.

**Les mesures.** Avant la fabrique, les deux témoins neufs, simulés au moteur
Python puis au portage, s'accordent au bit près. Dans Chromium, aux cinq
largeurs de `test_ecrans.py`, la carte de l'enfant posthume ne déborde pas et
ne lève aucune erreur. Ici, sur le paquet et les témoins périmés, échouent avant
comme après ces commits : sept confrontations de `-m rapide` (le pont, les
coupures au mois, la surcote parentale, le cycle de vie), et, dans les tests
du site, les témoins du portage (102 écarts sur 909 cas), les carrières tirées
au hasard, le paquet et la page des données.

**Ce qui reste.**

1. *Au site*, les autres points du bloc : les révisions et leurs quatre
   champs ; la catégorie ; la période et son moment ; le plancher non majoré.
2. *Au modèle* : sans décès déclaré, la réversion d'essai suppose le décès au
   départ, ou au 1er janvier de l'année courante (présomption
   `deces_apres_le_depart`), et l'enfant né après lui y compte comme un enfant
   posthume, à sa naissance, même plus de trois cents jours après. La
   présomption pourrait ne pas précéder la dernière naissance dite de plus de
   trois cents jours.
