# Étape 4, dixième partie : la réversion révisée quand le ménage ou les ressources du survivant changent avant sa retraite, ou sans elle, et sa dernière révision à l'âge légal

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la troisième vague
des sessions du jour : le premier point du bloc de l'étape — la révision de la
réversion quand le ménage ou les ressources du survivant changent avant sa
retraite, ou sans elle —, le point 1 du « Ce qui reste » de la neuvième partie.
Les majorations de 1976 et 1977 viendront dans une autre session ; les champs que
le bloc renvoie au site ne sont pas de celle-ci.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« révision avant sa retraite » ; fiche `reversion`).

- *La révision.* La réversion attribuée depuis juillet 2004 « est révisée à
  partir du 1er jour du mois qui suit la date de modification des ressources »
  (exposé « Condition de ressources » ; circulaire Cnav n° 2010/58, § 21, et son
  exemple : l'activité cessée le 15 février 2008, la révision au 1er mars), et
  « le remariage du bénéficiaire entraîne la révision de la retraite de réversion
  pour tenir compte des ressources du nouveau ménage ». À cinquante-cinq ans, la
  caisse interroge le survivant « pour appliquer cette mesure aux pensions de
  réversion en cours de service », l'abattement de 30 % de ses revenus d'activité
  (circulaire n° 2007/35, § 221). La réversion attribuée avant juillet 2004, « dans
  tous les autres cas » que sa retraite, n'est pas révisée.
- *La dernière révision.* R. 353-1-1, b, dans sa rédaction de 2026 : « A la date
  à laquelle il atteint l'âge prévu par l'article L. 161-17-2, lorsqu'il ne peut
  pas prétendre à de tels avantages », que la caisse applique « à compter du 1er
  jour du mois qui suit l'âge légal » — soixante ans avant la génération de
  juillet 1951, soixante-deux dès 1955 (circulaire n° 2012/25, annexe 1). À cet
  âge, qui a travaillé sans liquider tous ses droits garde sa réversion
  « révisable jusqu'à ce que ces droits soient liquidés », qui « indique n'avoir
  exercé aucune activité professionnelle » la voit figée (circulaire n° 2007/35,
  § 222) ; qui jouit de toutes ses retraites depuis plus de trois mois à la date
  d'effet, dès elle (circulaire n° 2010/58, § 24).
- *Aucun exemple chiffré.* Le troisième cas du § 322 de la circulaire n° 2005/17
  — la survivante de 1953 qui n'a jamais cotisé, figée à soixante ans, au 1er
  septembre 2013 — entre au témoin des exemples officiels en écart connu : depuis
  2011, l'âge de sa génération est de soixante et un ans et deux mois, et le
  modèle la fige au 1er novembre 2014, comme la circulaire n° 2012/25 modifie le
  § 322. L'exemple de la cessation d'activité attend que la saisie la date.

**Ce qui est fait.**

- *Le modèle* (`droit/reversion.py`, `_revisions`, qui remplace
  `_revision_a_la_retraite`, `_derniere_revision`, et leurs jumeaux) : la
  réversion attribuée depuis juillet 2004, ou que la retraite du survivant a
  recalculée aux règles de 2004, se révise le premier jour du mois qui suit
  chaque changement que la chronologie date — sa retraite, le ménage qu'il forme,
  ses cinquante-cinq ans quand il a des revenus d'activité —, sous le plafond de
  ce jour, ses ressources d'alors comptées ; un changement du jour même d'une
  révision ne compte qu'à celle du mois qui suit. Les réversions des régimes
  alignés déjà chiffrés y comptent à leur montant de ce jour (`_servie_au`). La
  dernière révision : trois mois après sa retraite datée ; sa date d'effet quand
  il a des retraites sans date ; le mois qui suit son âge légal quand il n'a ni
  retraites ni activité ; aucune quand il travaille sans retraite datée. La ligne
  écrit `revisions`, `(jour, ce qu'elle retire)`, et garde dans `revision_effet`
  et `reduction_de_la_revision` la dernière, que lit la majoration de 11,1 %.
- *Les présomptions* : `retraites_du_survivant_servies` dit ses retraites
  servies depuis plus de trois mois ; `survivant_sans_droit_propre`, neuve, tient
  pour n'avoir jamais travaillé qui n'a ni retraites, ni activité, ni retraite
  datée (vocabulaire, § 5.6 de l'architecture, fiche).
- *Les tests* : dans `test_reversion.py`, quinze cas de plus, posés à la main —
  le remariage de 2018 du veuf qui travaille (1,6 fois 2 080 fois 9,88 €, ramené
  aux euros de 2015) ; la veuve de 1953 sans ressources, remariée avant, au mois,
  et après son âge légal ; les sept âges de l'annexe 1 ; le remariage dans les
  trois mois de sa retraite, qui relève la réversion ; les cinquante-cinq ans qui
  la rendent entière ; la réversion d'avant 2004 que l'union ne touche pas ; cinq
  saisies aux deux moteurs, au bit près. Trois témoins de simulation neufs.
- *La fiche* `reversion` : ses écarts déclarés, une lecture de plus (circulaires
  n° 2007/35, 2010/58, § 21, 2012/25, annexe 1), son code ; la page des limites.

**Les mesures.** Aucune pension ne bouge, sur 897 témoins, ni aucun rendu de
page, ni aucun montant de réversion. Dix-neuf lignes gagnent leur dernière
révision : huit survivants aux retraites non datées, figés à leur date d'effet ;
onze sans ressources, figés à leur âge légal — le survivant né en 1975 en
février 2039 —, ou dès leur date d'effet quand ils l'ont passé. Le veuf remarié en mai 2018
(`reversion_revisee_a_sa_retraite`) a une révision de plus, en juin, sans effet,
sa révision de 2020 inchangée. Les trois témoins neufs : le veuf de 2015 qui
travaille et se remarie en 2018 garde 2 119,68 € de ses 7 317,99 € (en euros de
2015), toujours révisable ; la veuve de 2010, remariée en septembre 2014, 2 034,15 €
de ses 7 049,14 € (en euros de 2010), figée au 1er novembre ; la veuve de 2006,
écrêtée à 2 702,40 €, la voit portée en octobre 2008, à cinquante-cinq ans, à
6 667,51 €.

**Ce qui reste.**

1. *De la révision* : quand le ménage se défait, ou que les ressources varient
   autrement — la cessation d'activité de l'exemple de la circulaire n° 2010/58,
   § 21 —, ce que la chronologie, puis la saisie, doivent d'abord dater ; le droit
   personnel liquidé après la dernière révision d'abord fixée, qui la révise
   encore (§ 24) ; la révision de la majoration de 11,1 % (R. 353-13) et celle de
   la complémentaire des indépendants ; la retraite d'inaptitude substituée à la
   pension d'invalidité du survivant.
2. *Au site* : la phrase de la carte qui dirait les révisions et la dernière
   (`revisions`, `derniere_revision`), comme celle de la limite de cumul.
3. Les points 3 de la septième partie et ceux de la huitième.
