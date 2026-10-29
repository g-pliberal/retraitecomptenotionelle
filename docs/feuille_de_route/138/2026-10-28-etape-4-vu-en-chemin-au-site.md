# Étape 4, suite des notes du site du 28 octobre : ce qu'elles ont vu en chemin, que les cartes corrigent

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le point « Au site » du bloc de l'étape,
« ce que ses notes ont vu en chemin », que la page corrige avec les champs
qu'elle lit — le point 2 du « Ce qui reste » de la note des révisions
(`2026-10-28-etape-4-revisions-au-site.md`), les points 2 et 3 de celle du
plancher non majoré (`2026-10-28-etape-4-plancher-non-majore-au-site.md`). Ce
qui demandait au modèle un champ neuf, le plafond du ménage et les moments
examinés, allait à une autre session de la vague. Ce point seul.

**Ce qui est fait.**

- *Le motif de la ligne écrêtée* (`reversionDuConjoint`) disait « avec les
  ressources du ménage » dès qu'une union était dite, même formée après la
  date d'effet. Il a lu les dates de l'union, puis, le champ venu du modèle
  dans la même vague (586e240), `plafond_du_menage` : « avec ses ressources »
  quand l'union se forme après la date d'effet, dont la carte dit ensuite la
  révision ; « avec les ressources du ménage » sous le plafond du ménage seul.
- *Révisable sans révision* : la ligne que son plafond mesure à sa date
  d'effet, depuis juillet 2004 (`ressources_examinees_au`), dit jusqu'à quand
  elle reste révisable même quand rien ne la révise — « révisable jusqu'à sa
  retraite », qu'il travaille sans la dater, ou « jusqu'en » le mois de sa
  dernière révision (`derniere_revision`). Rien quand elle est figée dès sa
  date d'effet, ni pour celle que ses ressources ne réduisent pas, ni pour
  celle d'avant juillet 2004 que sa retraite ne recalcule pas.
- *« à partir d'août »* : la phrase d'« En bref » d'un départ à venir élide
  devant avril, août et octobre, par l'aide de la carte de la réversion,
  remontée au module (`deMois`) ; de même, la classe et non le cas, la phrase
  qui dit de quand sont les montants d'un départ de l'année, qui écrivait
  « celle de octobre 2026 ».
- *Le minimum que la réversion ne compte pas* : la cellule de la pension du
  défunt le nomme par le libellé de son avantage dans la liquidation que la
  réversion reverse — « de pension minimum », « du plancher de la pension
  substituée », « de minimum contributif » (`MINIMA_NON_REVERSES`) ; mort
  avant son départ, « de minimum contributif », comme avant.
- *La composition sous le montant du système 1* (`etagesActuels`) : pour qui
  est déjà parti, chaque régime y porte sa pension d'aujourd'hui
  (`aujourd_hui`), avec ce que « faire vivre » y retire ou y ajoute — le
  plancher non majoré, la révision du minimum, la majoration de 2023, les
  relèvements —, et non son montant du départ mené par son seul coefficient.
  La majoration pour enfants reste menée par le coefficient de son régime.
  Tant qu'une pension reste à venir, la ligne se tait, comme avant : elle
  aurait dit « une seule pension, sans complémentaire à part » de qui en
  attend deux autres.
- *Les tests*, vus rouges : `test_web.py` — le veuf de 2030 qui gagne
  30 000 €, pacsé en mars 2034 avec une conjointe qui apporte 16 000 € :
  333 € « avec ses ressources », puis 999,04 € de moins par an sous le plafond
  du ménage, 83 € par mois, à partir d'avril 2034 ; pacsé dès le décès,
  250 € « avec les ressources du ménage », posés à la main ; le même sans
  que rien change, révisable jusqu'à sa retraite, ou jusqu'en juin 2034, sa
  retraite datée de mars, et ses deux complémentaires sans le mot ; le
  minimum nommé pour le salarié parti en avril 1970, l'ex-invalide d'avril
  1969 à la pension minimum, celui que sa pension d'invalidité relève et le
  salarié de 1955 au minimum contributif ; la composition des deux premiers,
  255,54 € et 258,01 € de retraite de base sous 1 044 €, et de la pension au
  minimum contributif majorée en 2023, chacune à l'euro de ce que le chemin de
  la pension écrit ; l'aide-soignante partie de l'hôpital en 2022, dont le
  régime général et l'Arrco attendent l'âge légal, sans ligne ; et, mis à
  jour, la veuve de l'enfant posthume, sans activité ni retraite, révisable
  jusqu'au mois qui suit ses soixante-quatre ans, février 2039.
  `test_web_revues.py` — « à partir d'août 2039 »,
  « d'octobre », « de janvier » ; « celle d'octobre 2026 », « de mars ».

**Les mesures.** Sur le paquet et les témoins refaits ici, que la fabrique
de GitHub refait et qui ne sont pas commités, sept témoins de page bougent de
ces commits, et rien d'autre, contre des témoins refaits du même paquet avec
la page d'avant : l'élision dans `simuler_depart_en_cours_d_annee`,
`simuler_hors_de_france_sans_accord` et `simuler_reversion` ; la composition
qui paraît sous le montant de `simuler_invalidite_categorie` (1 336 € +
182 €) et de `simuler_reversion_agricole` (711 € + 13 € + 320 €, à l'euro du
chemin de sa pension, 710,47 €, 13,05 € et 320,07 €) ; « révisable jusqu'en
février 2039 » dans `simuler_reversion_enfant_posthume` ; « avec ses
ressources » dans `simuler_reversion_revisee`, dont l'union suit la date
d'effet. Aucun témoin de simulation, aucune des neuf pages toutes faites. Le
premier rendu disait « une seule pension » de `simuler_departs_echelonnes` et
de `simuler_demande_de_pension`, dont une pension attend son heure : la garde
l'a tu. Sur ces fichiers, `-m rapide` (3 458 tests) et `-m site` passent, et
les fichiers de la zone (`test_web.py`, `test_web_saisie.py`,
`test_web_revues.py`, `test_reversion.py`), un millier de tests, une fois mis
à jour celui de l'enfant posthume, qui lisait la carte sans « révisable ».
Dans Chromium, par le pilote de
`test_ecrans.py`, aux cinq largeurs, dépliants fermés et ouverts, les
simulations du veuf pacsé en 2034, du salarié parti en 1970, de l'ex-invalide
que sa pension d'invalidité relève et du départ d'août 2039 ne débordent pas,
ne chevauchent aucune case et ne lèvent ni erreur ni alerte ; ouvertes dans la
page, leurs cartes disent ce que les tests lisent.

**Ce qui reste.**

1. *Au site* : les moments examinés (`moments_examines`, que la ligne dit
   depuis 586e240) — la carte qui dirait la demande refusée avant le décès
   (note de la période et de son moment, point 2 de « Ce qui reste »).
2. *Au modèle, puis au site*, vu en chemin : la composition se tait encore
   quand la majoration pour enfants ne suit pas le coefficient du régime qui
   la porte — l'enfant qui n'est plus à charge à l'échéance, à l'Agirc-Arrco,
   la pension datée, le régime porté à un plancher qui en sert une part. Le
   salarié né en 1955, parti à 62 ans, dont les enfants nés en 2005 et 2008
   étaient à charge, n'en lit aucune. La majoration servie aujourd'hui, régime
   par régime, la rendrait.
3. *Au modèle, s'il le faut* : mort avant son départ, la carte dit « de
   minimum contributif » la part du minimum, la liquidation de son décès
   n'étant pas sur la page ; un libellé sur la ligne la nommerait.
