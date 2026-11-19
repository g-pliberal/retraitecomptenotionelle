# Quatre renvois d'âge coupés au jour du texte

Le 19 novembre 2026, sur l'accord du propriétaire (« on corrige tout ce qui
est faux »), les quatre dates que la relecture du 17 novembre avait trouvées
fausses (`2026-11-17-dix-renvois-sensibles.md`) sont corrigées. Aucun code
n'est touché : les fiches de régime savaient déjà dire au jour les pensions
qu'une période liquide (`date_effet`, action 131). Les tests, écrits d'abord
et vus rouges, sont dans `tests/test_renvois_dates_au_jour.py` ; leurs
attendus viennent des textes que la note du 17 cite.

**Banque de France, le 1er avril 2007.** La période de l'ancien régime
liquide jusqu'au 31 mars 2007 ; une période neuve, de 2007, liquide d'avril à
décembre au règlement de 2007 : soixante ans, 151 puis 152 trimestres,
aucune décote. Elle ne sert pas de surcote, et le déclare : l'article 33 ne
majore que les trimestres « effectués après le 1er avril 2007 », deux au
plus en 2007, et le taux plat de la fiche les aurait comptés depuis soixante
ans.

**Artisans et commerçants d'avant 1973, le 7 octobre 2012.** La période de
2004 liquide jusqu'au 6 octobre 2012, celle de 2013 depuis le 7 : l'âge
légal, la durée et l'âge d'annulation de la décote du régime général pour
les pensions de novembre et décembre 2012.

**Cavimac, le 2 novembre 2006.** La période de 2007 liquide depuis le
2 novembre 2006 : l'âge légal pour la pension du 1er décembre 2006.

**Ce qui bouge.** Aucun des 934 témoins de simulation. Les cas touchés sont
étroits : l'agent de la Banque de France parti d'avril à décembre 2007 (âge
d'ouverture de 60 ans et non 55, un ou deux trimestres de durée en plus) ;
l'artisan ou le commerçant né en 1952 parti en novembre ou décembre 2012
avec des droits d'avant 1973 (60 ans et 9 mois et non 60 ans, décote jusqu'à
65 ans et 9 mois) ; le ministre du culte parti le 1er décembre 2006 (60 ans
et non 65). La page Avantages compte une période de plus au catalogue.

**Ce qui reste, et attend le propriétaire.**

- **La surcote de la Banque de France.** Trouvée en corrigeant : de 2008 à
  aujourd'hui, la fiche majore au taux plat tous les trimestres accomplis
  après soixante ans au-delà de la durée, quand l'article 33 du règlement ne
  compte que ceux « effectués après le 1er avril 2007 ». Un agent parti en
  2008 à 63 ans avec sa durée depuis ses 60 ans est majoré de douze
  trimestres au lieu de trois. Il y faut un barème daté, comme celui de la
  fonction publique : une règle du scénario 1, une étape à elle.
- **La Cavimac de janvier à novembre 2006.** La fraction d'après 1997 pouvait
  se liquider seule dès soixante ans ; le modèle ne liquide pas une fraction
  sans l'autre, et garde 65 ans. Il y faut du code.
- **Les artisans et commerçants de juillet 2011 à octobre 2012.** Le décret
  de 2010 voulait l'âge légal dès le 1er juillet 2011 et visait le mauvais
  article ; ce que la caisse a appliqué ne se lit pas dans l'index.
- **Les 55 ans de la Banque de France d'avant 2007**, que l'index ne porte
  pas.
