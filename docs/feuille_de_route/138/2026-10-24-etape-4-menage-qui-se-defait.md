# Étape 4, onzième partie : la réversion révisée quand le ménage du survivant se défait, ou que son activité cesse

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la quatrième vague des
sessions du jour : le premier point du bloc de l'étape — la révision de la
réversion quand le ménage du survivant se défait ou que ses ressources varient,
événements à dater d'abord dans la chronologie —, le point 1 du « Ce qui reste »
de la dixième partie. Les majorations de 1976 et 1977 viendront dans une autre
session ; ce que le bloc renvoie au site n'est pas de celle-ci.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« ménage qui se défait » ; fiche `reversion`).

- *La révision.* La réversion attribuée depuis juillet 2004 « est révisable en
  cas de variation dans le montant des ressources » (R. 353-1-1), « à partir du
  1er jour du mois qui suit la date de modification des ressources » (exposé
  « Condition de ressources ») : « Un assuré titulaire d'une pension de réversion
  nous informe le 20 mars 2008 qu'il a cessé son activité professionnelle le 15
  février 2008 : date d'effet de la révision = 1er mars 2008 » (circulaire Cnav
  n° 2010/58, § 21).
- *Le ménage qui se défait.* Un changement de situation familiale compte par ses
  conséquences « sur le plafond de ressources à retenir (personne seule ou
  ménage), ainsi que sur le montant des ressources elles-mêmes » : « décès du
  conjoint, du concubin, du partenaire pacsé », « divorce », « conclusion ou
  résiliation d'un Pacs », « début ou fin du concubinage » (lettre de la Cnav du
  18 avril 2007) ; les époux, concubins ou partenaires « séparés de fait avec
  résidence distincte » se comptent comme des célibataires (R. 815-27, auquel
  R. 353-1 renvoie ; circulaire n° 2009/11, § 31). Quand la situation change dans
  la période de référence, les ressources d'après le changement se transposent
  sur toute la période : au divorce du 1er décembre, « le salaire du conjoint doit
  être ignoré, et le décompte doit s'effectuer en retenant le plafond de
  ressources personne seule » ; au mariage du même jour, il compte pour les trois
  mois (circulaire n° 2005/17, § 146).
- *Aucun exemple chiffré* d'une réversion révisée. Trois exemples entrent au
  témoin des exemples officiels : la cessation d'activité de la circulaire
  n° 2010/58, § 21, datée ; les deux cas du § 146, par les ressources que la
  caisse retient à la date d'effet. La cessation et le divorce, vus rouges sous
  la règle d'avant ; le mariage, déjà juste.

**Ce qui est fait.**

- *La chronologie* (`chronologie.py`, et son jumeau) : la fin de l'activité du
  survivant (`fin_d_activite`) et celle de sa nouvelle union
  (`nouvelle_union_fin`) finissent les faits de ses ressources, [début, fin) comme
  toute période, chacune après le début de son fait ; deux accesseurs,
  `fin_d_activite` et `fin_du_menage`, et deux champs du conjoint
  (`carriere.py`).
- *Le modèle* (`droit/reversion.py`, et son jumeau) : le mois qui suit la fin du
  ménage et celle de l'activité révisent la réversion, comme sa formation ; le
  ménage défait ne compte plus — plafond d'une personne seule, ressources de
  l'ancien conjoint ignorées —, ni les revenus de l'activité cessée, à la date
  d'effet comme aux révisions (`_ressources_du_plafond`, `_venu`) ; les
  cinquante-cinq ans n'abattent plus rien quand l'activité a cessé avant eux.
  L'union défaite avant le jour où la majoration pour enfant d'avant 2004
  s'attribuerait ne la refuse plus.
- *La saisie* (`saisie.js`, la seule que lise encore le dépôt, l'action 161
  retirant la saisie Python) : `activite_conjoint_fin` et `nouvelle_union_fin`,
  lus, vérifiés — chacun suppose ce qu'il finit, et le suit —, gardés dans
  l'adresse.
- *Les tests* : dans `test_chronologie.py`, les deux fins et leurs refus, aux
  deux moteurs ; dans `test_reversion.py`, le veuf pacsé dont le pacs se rompt,
  posé à la main (2 080 fois 9,61 €, puis 10,25 €, ramené aux euros de 2015), la
  veuve qui cesse son activité, le ménage défait avant sa retraite, ou après sa
  dernière révision, la réversion d'avant 2004 qu'il ne touche pas, la majoration
  pour enfant, neuf refus de la saisie, l'adresse, deux saisies aux deux moteurs ;
  deux témoins de simulation neufs.
- *La fiche* `reversion` : ses écarts déclarés, deux lectures de plus, ses
  exemples ; la page des limites.

**Les mesures.** Aucune pension ne bouge, sur les 902 témoins d'avant, ni aucun
rendu de page, ni aucune réversion : aucun ne datait la fin d'un ménage ni celle
d'une activité. Les deux témoins neufs : le veuf de 2015 qui gagne 25 000 €, sa
réversion écrêtée à 2 488,80 €, pacsé en septembre 2015, la voit portée en
octobre à 4 482,08 € sous le plafond du ménage, puis ramenée en avril 2021, le
pacs rompu, à 3 295,56 € (en euros de 2015), toujours révisable ; la veuve de
2006, écrêtée à 2 702,40 €, son activité cessée en février 2008, la voit portée
dès mars à 6 667,51 €, entière, sept mois avant que ses cinquante-cinq ans ne le
fassent sans elle. Le cliquet des textes descend à 9 543 : la fiche cite R. 353-1
et R. 815-27.

**Ce qui reste.**

1. *De la révision* : les ressources qui varient autrement — une activité
   reprise, un salaire ou les ressources du nouveau conjoint qui changent —, que
   ni la chronologie ni la saisie ne datent encore ; les trois mois que la caisse
   examine avant la révision, qui peuvent porter des revenus de l'activité
   cessée ; le droit personnel liquidé après la dernière révision d'abord fixée
   (§ 24) ; la révision de la majoration de 11,1 % (R. 353-13) et celle de la
   complémentaire des indépendants ; la retraite d'inaptitude substituée à la
   pension d'invalidité du survivant ; la réversion que la fin de l'union
   rendrait dans les régimes qui la retirent au remariage, à lire régime par
   régime.
2. *Au site* : les deux champs du formulaire (`activite_conjoint_fin`,
   `nouvelle_union_fin`), et la phrase de la carte qui dirait les révisions.
3. Les points 3 de la septième partie et ceux de la huitième.
