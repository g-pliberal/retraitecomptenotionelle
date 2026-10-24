# Étape 4, treizième partie : les majorations de 1976 et 1977 aux salariés agricoles, l'Alsace-Moselle et l'ancien invalide, lus ; les trois mois de chaque révision

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la sixième vague des
sessions du jour : le premier point du bloc de l'étape — les majorations de 1976
et de 1977 aux salariés agricoles, l'Alsace-Moselle (décret n° 76-405), l'ancien
invalide — et, si leurs textes ne se lisent que sur le fac-similé du Journal
officiel, le point suivant : les trois mois que la caisse examine avant chaque
révision. Ce que le bloc renvoie au site n'est pas de cette session.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre, « trois
mois de chaque révision » ; fiches `majorations_forfaitaires_1972_1982` et
`reversion`).

- *Les salariés agricoles.* Leurs lois ne les nomment pas, mais deux décrets leur
  ont étendu les majorations : le décret n° 76-727 du 28 juillet 1976, qui porte
  « majoration des pensions de vieillesse dues au titre des parag. 1, 2 et 2 bis »
  du décret n° 51-727, et le décret n° 77-966 du 19 août 1977, « rendant
  applicables, au régime des assurances sociales agricoles, les dispositions de la
  loi » n° 77-657. L'index du Journal officiel n'en garde que la notice ; l'index
  LEGI n'en porte aucun article, ni dans l'article 1er bis du décret n° 51-727
  (rédaction du 26 août 1977), ni dans le décret n° 50-1225 : leur date d'effet et
  leurs conditions sont au fac-similé, au propriétaire.
- *L'Alsace-Moselle.* La loi n° 75-1279 « est applicable aux assurés
  ressortissant au code local » (article 7) ; le décret n° 76-405, qui l'adapte,
  règle la retraite anticipée des travailleurs manuels et des mères de famille
  (articles 1er à 3, 5) et la majoration de l'article 5 de la loi (article 4), non
  celle de son article 3. La loi n° 77-657 ne nomme pas ces assurés, et l'index ne
  porte aucun décret qui la leur étende. La pension du code local, « une somme de
  base et [...] des majorations proportionnelles aux cotisations ou au salaire »
  (L. 357-2), sans durée maximum, est hors du champ du modèle ; leur pension du
  régime général est majorée comme toute autre.
- *L'ancien invalide.* Les quatre circulaires (n° 2/72, 15/76, 64/77, 79/82) disent
  la même chose : la majoration « s'applique uniquement à la pension de vieillesse
  résultant des cotisations », qu'une « nouvelle comparaison devrait, en principe »,
  opposer à la pension d'invalidité « afin de servir le montant le plus élevé ».
  L'ex-invalide des deuxième et troisième groupes, dont la pension substituée vaut
  50 % du salaire annuel moyen, plus que la pension majorée sur la durée maximum —
  46,30 % au plus avant 1972 —, ne l'a donc pas ; en 1982, les 6 % et les 4 % vont à
  tous les ex-invalides. Le refus est l'effet d'un plancher, non une règle à part :
  le modèle majore la pension de vieillesse, comme la loi le dit, et ne la compare
  pas, faute du plancher de la pension substituée (fiche
  `pension_d_invalidite_substituee`), du groupe et du montant de la pension
  d'invalidité. Refuser la majoration sans ce plancher éloignerait la pension du
  modèle de celle que la caisse sert.
- *Les trois mois.* « Les ressources sont examinées sur les 3 mois qui précèdent
  cette date de révision » (exposé « Condition de ressources ») ; les revenus
  d'activité « pour leur montant réellement perçu », les avantages viagers « pour
  leurs montants théoriques », les ressources d'après un changement de situation
  familiale « transposées sur 3 mois », « Tous les mois sont considérés comme valant
  30 jours » (circulaire RSI n° 2007/061, annexe 3, § 6.1, 6.2 et 7). Son exemple est
  chiffré : droit propre au 1er avril 2006, révision au 1er mai, (1 500 + 1 000 +
  600) / 3 = 1 033,33 € par mois, « Et non 2 500 € / 3 + 600 € = 1 433,33 € » — « la
  méthode retenue par le régime général », qui comptait le droit propre entier,
  jusqu'à la circulaire Cnav n° 2010/58 (§ 22) : depuis le 30 juin 2010, « les
  sommes réellement perçues au titre du nouvel avantage ». Aucun texte ne dit ce que
  la caisse fait des trois mois après la première révision : elle réexamine au
  changement déclaré, aux contrôles de cinquante-cinq ans, de l'âge légal et de
  l'âge du taux plein augmenté de trois mois, et à la dernière révision.

**Ce qui est fait.**

- *La fiche des majorations de 1972 à 1982* : ses deux écarts récrits — l'ancien
  invalide, une comparaison au plancher que le modèle ne fait pas ; l'Alsace-Moselle,
  sans effet sur ce qu'il calcule ; les salariés agricoles, leurs deux décrets à
  lire —, l'article 4 de la loi n° 75-1279 et l'article 2 de la loi n° 82-599
  rattachés, l'article 7 et L. 357-1 et L. 357-2 sans effet ; le cliquet des textes
  descend à 9 530.
- *Le modèle* (`droit/reversion.py`, et son jumeau) : chaque révision d'après juillet
  2004 compte les ressources des trois mois qui la précèdent, en mois de trente
  jours (`_ressources_des_trois_mois`, `_percu`, `_en_mois`) — les revenus d'activité
  et ceux du nouveau conjoint tels que perçus, les retraites du survivant pour ce
  qu'elles servent depuis leur jour, ou entières au régime général avant le 1er
  juillet 2010, que les versions disent (`retraites_entieres_a_la_revision`), les
  ressources transposées depuis le ménage formé ou défait dans la période ; puis une
  révision de plus le premier mois dont les trois mois ne portent plus que ce qui
  suit chaque changement compté tel que perçu (`_apres_les_trois_mois`) — pour une
  retraite, c'est la dernière révision, trois mois après elle, celle de l'exemple
  de la circulaire n° 2010/58, § 24 —, quand elle change quelque chose. C'est la
  lecture du modèle, déclarée dans la fiche : sans elle, les revenus d'avant le
  changement pèseraient jusqu'au suivant. Le recalcul aux règles de 2004 garde ses
  ressources de l'année entière. Chaque ligne dit les ressources de chacune de ses
  révisions (`ressources_des_revisions`), que le paquet porte.
- *Les tests* : au témoin des exemples officiels, l'exemple de la circulaire RSI
  deux fois — 1 033,33 € au régime des indépendants, 1 433,33 € au régime général de
  2006 —, sous une grandeur neuve de l'oracle
  (`ressources_retenues_mensuelles_aux_revisions`), vus rouges avant le code ;
  l'exemple de la fin d'activité de la circulaire n° 2010/58 (§ 21) se lit à la
  première révision. Dans `test_reversion.py`, sept cas récrits sur les trois mois
  posés à la main, et les jours des révisions confrontés aux deux moteurs.
- *La fiche* `reversion` : ses deux écarts des révisions, une lecture, l'historique ;
  la page des limites.

**Les mesures.** Aucune pension ne bouge, sur les 907 témoins de simulation, ni
aucun rendu de page de ce fait. Onze réversions changent, en euros de l'année du
décès : sept ne gagnent que les ressources de leurs révisions ; quatre voient la
révision du mois qui suit le changement, qui compte encore les mois d'avant lui,
la laisser où elle était, et la suivante faire ce que la première faisait. La
veuve de 2006 qui commence une activité en mars 2007 garde sa réversion entière
le 1er avril, 4 666,67 € de revenus retenus, et la voit réduite de 3 770,07 € le
1er juin ; le veuf dont le salaire passe à 25 000 € en mars 2018, entière le 1er
avril, réduite de 4 430,69 € le 1er juin ; le veuf remarié en 2018 qui prend sa
retraite en juillet 2020, entière le 1er août, un mois de ses retraites compté,
réduite de 4 237,91 € le 1er octobre, à sa dernière révision ; le veuf dont la
conjointe voit ses ressources tomber à 12 000 € en janvier 2020 n'a plus, le 1er
février, que 2 071,25 € de réduction, 27 833,33 € retenus, et sa réversion
entière le 1er avril. Le portage rejoue les 907 témoins au bit près ; les deux
exemples du RSI tombent justes.

**Ce qui reste.**

1. *Au propriétaire* : lire au fac-similé les décrets n° 76-727 (Journal officiel du
   4 août 1976) et n° 77-966 (du 26 août 1977) ; lus, les salariés agricoles entrent
   dans les majorations de 1976 et de 1977 des versions `avant_1972` et `en_1972`.
2. La majoration de l'article 5 de la loi n° 75-1279, aux travailleurs manuels et aux
   mères de famille partis avant juillet 1976 à un taux réduit, dont les taux sont
   au décret n° 76-404, en notice seule : aucune fiche ne la porte.
3. Le plancher de la pension substituée à l'invalidité, que la comparaison des
   circulaires suppose, avec le groupe de la pension d'invalidité.
4. *De la révision* : ce que la caisse fait des trois mois après la première
   révision, que le modèle lit ; les trois ou douze mois de la date d'effet
   (R. 353-1) ; le droit personnel liquidé après la dernière révision d'abord fixée ;
   la révision de la majoration de 11,1 % (R. 353-13) et celle de la complémentaire
   des indépendants ; la retraite d'inaptitude substituée à la pension d'invalidité
   du survivant ; la réversion que la fin de l'union rendrait dans les régimes qui la
   retirent au remariage.
5. *Au site* : les quatre champs du formulaire, et la phrase de la carte qui dirait
   les révisions et leurs ressources.
