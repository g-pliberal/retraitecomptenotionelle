# Étape 4, suite de la dix-septième partie : la demande examinée avant le décès, que la carte de la réversion dit

**Le 29 octobre 2026, la demande.** La vague du 28 octobre, une session par
tâche qui se mène sans le propriétaire : le point « Au site » du bloc de
l'étape, la demande refusée avant le décès — le point 1 du « Ce qui reste » de
la note des moments examinés au modèle
(`2026-10-28-etape-4-moments-et-menage-au-modele.md`), que reprend le point 1
de celle de ce qui a été vu en chemin
(`2026-10-28-etape-4-vu-en-chemin-au-site.md`). Le plafond du ménage, l'autre
moitié de ce point 1, la carte le dit depuis cette dernière note. Ce point seul,
sans rien recalculer.

**Ce qui est fait.**

- *La carte de la réversion* (`reversionDuConjoint`) : quand la ligne a examiné
  la demande avant le décès (`moments_examines`), la phrase des ressources
  retenues dit pourquoi ce sont celles du décès, comme elle disait pourquoi
  douze mois et non trois : « ressources des trois mois qui précèdent votre
  décès : 0 € par an, celles des mois qui précèdent sa demande dépassant le
  plafond ». Refusée à la demande comme au décès, les deux raisons ensemble :
  « ressources des douze mois qui précèdent votre décès : 40 000 € par an,
  celles des trois derniers et celles des mois qui précèdent sa demande
  dépassant le plafond ». Avant juillet 1974, le décès seul, sans rien de plus.
  La ligne ne dit pas les ressources de la demande, que la carte tait.
- *Ce que ce montant suppose* dit la présomption qui date la demande
  (`reversion_demandee_le_mois_avant_sa_date_d_effet`) dès que la ligne l'a
  examinée, que ses mois soient retenus ou non ; elle ne la disait que des
  mois de la demande retenus.
- *Le test* (`test_web.py`,
  `test_avant_juillet_2004_la_carte_dit_les_mois_de_la_demande_ou_du_deces`),
  posé à la main depuis la circulaire n° 31/75, § 233, R. 353-1 et l'exposé de
  la Cnav (« Si les ressources examinées à la date de la demande et à la date
  du décès dépassaient le plafond autorisé, la demande était rejetée »), et vu
  rouge : la veuve de 1996 sans activité au décès, qui en prend une en 1997,
  retenue au décès après sa demande ; la même, active à 40 000 € par an du
  décès à sa demande, refusée aux deux moments, en euros de 1996 ; et, pour
  garde, la veuve de 1972, au décès seul, sans demande ni présomption.

**Les mesures.** `-m site` passe, témoins du portage et pages toutes faites
compris : aucun témoin ne bouge, aucune ligne des témoins n'ayant examiné la
demande avant le décès ; `-m rapide` et les trois fichiers du site
(`test_web.py`, `test_web_saisie.py`, `test_web_revues.py`) passent. Dans
Chromium, par le pilote de `test_ecrans.py`, aux cinq largeurs, dépliants
fermés et ouverts, les cartes des trois veuves ne débordent pas, ne
chevauchent aucune case et ne lèvent ni erreur ni alerte ; ouvertes dans la
page, elles disent ce que le test lit.

**Ce qui reste.**

1. *Vu en chemin, à la saisie* : elle refuse une variation des revenus
   d'activité du conjoint qui précède le décès (« elle le suit ») ; ses
   ressources d'avant le décès ne changent donc pas d'un mois à l'autre, et
   les douze mois du décès ne s'y retiennent que pour refuser, jamais pour
   ouvrir. Le survivant dont l'activité a changé dans l'année du décès ne se
   décrit pas.
2. *Au propriétaire*, inchangé : les décrets agricoles de 1976 et 1977 ; le
   choix de la date de la demande ; le décès supposé avant l'enfant né après
   lui.
