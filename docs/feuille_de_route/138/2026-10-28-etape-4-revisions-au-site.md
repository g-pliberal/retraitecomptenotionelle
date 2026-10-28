# Étape 4, suite des dixième à treizième parties : les révisions au site, les quatre champs qui les disent et la carte qui dit chacune, sur ses ressources

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le point « Au site » du bloc de l'étape
« les révisions, leurs quatre champs », détaillé au point 2 du « Ce qui reste »
de la douzième partie (`2026-10-24-etape-4-ressources-qui-varient.md`) et au
point 5 de la treizième (`2026-10-24-etape-4-trois-mois-de-chaque-revision.md`)
— les quatre champs que la saisie lit de l'adresse depuis le 24 octobre, et la
phrase de la carte qui dirait les révisions et leurs ressources. Ce point seul,
à la suite des études et de l'enfant né après le départ.

**Ce qui est fait.**

- *Le formulaire* (`conjointFormulaire`) : dans le dépliant « Conjoint et
  réversion », chacun sous ce qu'il fait cesser ou varier — « Fin de son
  activité » (`activite_conjoint_fin`) et « Changements de ses revenus
  d'activité » (`activite_conjoint_variations`) sous ses revenus d'activité ;
  « Fin de cette union » (`nouvelle_union_fin`) sous « Depuis » ; « Changements
  des ressources de son nouveau conjoint »
  (`ressources_nouveau_conjoint_variations`) sous ces ressources. Un exemple
  sous chacun, l'explication dans sa bulle. L'aide de « Depuis » disait que le
  régime général ne compte le ménage que formé quand la réversion commence,
  ce que le modèle ne fait plus depuis la dixième partie : elle dit la
  révision qu'il ouvre le mois qui suit.
- *La carte de la réversion* (`reversionDuConjoint`) : la ligne qui se révise
  sous le plafond (R. 353-1-1) dit chaque révision, ce qu'elle retire ou ajoute
  à la précédente, à sa date, et les ressources qu'elle retient, par an, aux
  euros de la page ; puis jusqu'à quand elle reste révisable, le mois de sa
  dernière révision (`derniere_revision`), ou sa retraite quand il travaille
  sans la dater (circulaire Cnav n° 2007-35, § 222) : « 58 € de moins à partir
  de février 2033, révisée sur 21 700 € de ressources par an ; 117 € de moins
  à partir d'avril 2033, révisée sur 23 100 € ; révisable jusqu'à sa
  retraite ». Le modèle compte chaque réduction depuis la date d'effet ; la
  carte dit l'écart à la précédente, qui s'additionne comme les autres parts
  de la ligne, sans recomposer ce que la ligne sert. Elle élide aussi « à
  partir d'avril », « d'août », « d'octobre ».
- *Les tests* : `test_web_saisie.py` — les quatre champs, chacun sous le sien,
  rendus tels qu'écrits ; `test_web.py` — le veuf de 2030 qui gagne 30 000 €, sa
  réversion écrêtée à 333 € par mois sous le plafond de 2 080 fois 12,02 €, dont
  le salaire passe à 33 000 €, tombe à 27 000 € ou reste à 30 000 € en janvier
  2033, révisée le 1er février puis le 1er avril, posé à la main, révisable
  jusqu'à sa retraite, ou jusqu'en juin 2034 quand il la date de mars ; le
  budget de mots du simulateur tout déplié, de 7 310 à 7 350, les quatre champs
  en ajoutant 41.
- *Un témoin de page* : `simuler_reversion_revisee`, au formulaire entier — le
  veuf de 2030 dont le salaire change puis cesse, pacsé en 2034 avec une
  conjointe dont les ressources changent, seul de nouveau en 2037 —, que la
  fabrique de GitHub refait.

**Les mesures.** Dans Chromium, aux cinq largeurs de `test_ecrans.py`,
dépliants fermés et ouverts, le simulateur du témoin `simuler_reversion_revisee`
— les quatre champs remplis, sept révisions sur la ligne du régime général — ne
déborde pas, ne chevauche aucune case et ne lève aucune erreur ; la seule alerte
est celle qu'`ALERTES_ADMISES` déclare. La carte du veuf de 2015 remarié en 2018
(témoin de simulation `reversion_revisee_quand_l_apport_du_menage_change`) dit
enfin ses trois révisions : 522 € de moins en juin 2018, puis 321 € et 202 € de
plus en février et en avril 2020, aux euros de 2026. Le simulateur tout déplié
passe de 7 309 à 7 350 mots : le premier envoi, faute d'avoir joué en entier les
fichiers des tests du site, en portait 7 361, au-delà de son budget, que le
deuxième commit répare. Ici, sur le paquet et les témoins périmés, échouent
avant comme après ces commits : sept confrontations de `-m rapide` (le pont, les
coupures au mois, la surcote parentale, le cycle de vie) et, dans les fichiers
du site, les témoins du portage (102 écarts sur 909 cas), les carrières tirées
au hasard, le paquet et la page des données.

**Ce qui reste.**

1. *Au site*, les autres points du bloc : la catégorie ; la période et son
   moment ; le plancher non majoré.
2. *Au site*, vu en chemin : le motif de la ligne écrêtée dit « avec les
   ressources du ménage » dès qu'une union est dite, même formée après la date
   d'effet, quand la carte dit ensuite la révision qui suit sa formation ; la
   ligne ne dit pas si son plafond est celui du ménage, que la page ne doit pas
   recalculer. La carte ne dit pas révisable la réversion d'un survivant qui
   travaille sans que rien change : sans révision, elle ne distingue pas une
   réversion toujours révisable d'une réversion hors des règles de ressources.
   Ailleurs, la phrase de la pension d'un départ à venir écrit « à partir de
   août 2039 ».
3. *Au modèle*, inchangé : le décès supposé avant l'enfant né après lui (note
   `2026-10-28-etape-4-enfant-ne-apres-le-depart.md`).
