# Étape 4, troisième partie : le plafond du ménage et l'abattement des revenus d'activité

**Le 9 octobre 2026, la demande.** Le propriétaire : « Action 138, étape 4 : le
plafond du ménage ». C'est le point suivant de « Ce qui reste » (note du 7
octobre) : le plafond du ménage, 1,6 fois celui d'une personne seule, quand le
survivant vit en couple, et l'abattement de 30 % de ses revenus d'activité
après cinquante-cinq ans (R. 353-1), que la fiche `reversion` déclarait
absents, et que la saisie ne disait pas.

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
fiches `reversion` et `reversion_rci`).

- *Le ménage.* L. 353-1 ouvre la réversion « si ses ressources personnelles ou
  celles du ménage n'excèdent pas des plafonds fixés par décret », depuis la
  loi du 21 août 2003, pour les réversions qui prennent effet à compter du 1er
  juillet 2004 ; D. 353-1-1, dans sa seule rédaction, fixe celui du ménage à
  « 1,6 fois le plafond » d'une personne seule. Le ménage est « du couple
  marié, des partenaires pacsés ou des concubins » (circulaire Cnav
  n° 2005-17, § 141), et « toutes les ressources du demandeur ou du ménage
  sont retenues » (exposé « Évaluation des ressources »). Avant juillet 2004,
  les ressources personnelles seules, « sans tenir compte des avantages de
  réversion » (R. 353-1, rédactions de 1985 et de 1990).
- *L'abattement.* « Les revenus d'activité du conjoint survivant font l'objet
  d'un abattement de 30 % s'il est âgé de 55 ans ou plus » : R. 353-1 l'écrit
  dans la rédaction du décret n° 2004-1447 du 23 décembre 2004, publié le 30
  (JORF, article 1er), et non dans celle du 25 août. La Cnav l'applique
  « dès lors que l'assuré a 55 ans ou plus, quel que soit l'âge atteint au
  moment où ces revenus ont été perçus » (circulaire n° 2006-37, § 7, qui
  revient sur la n° 2005-17, § 1442), et son exemple le chiffre : 1 000 euros
  par mois retenus au 1er août et au 1er septembre 2006, 700 au 1er octobre,
  pour un survivant de cinquante-cinq ans le 15 septembre.
- *Le barème.* Le plafond de la Cnav, « personne seule » et « couple », depuis
  le 1er juillet 2004 : 25 001,60 et 40 002,56 euros en 2026, que
  service-public dit aussi (fiche F13104). En 2004, la caisse a pris « à titre
  dérogatoire » le SMIC du 1er juillet (circulaire n° 2005-17, § 145).
- *La complémentaire des indépendants.* L'article 17 de son règlement : des
  ressources « personnelles ou du ménage », « appréciées selon [...] R. 353-1
  et R. 353-1-1 », sous le plafond que le CPSTI fixe, sans plafond propre au
  ménage (circulaire Cnav n° 2026-01, § 9).
- *Destinie 2* (`Retraite.cpp`, au commit `4c1d34b`) sert 1,6 fois le plafond
  au seul remarié, et abat de 30 % tout salaire, sans regarder l'âge.

**Ce qui est fait.**

- *La saisie* (deux moteurs) : trois champs du bloc « Conjoint et réversion »
  — « Dont ses revenus d'activité » (`activite_conjoint`), une part de ses
  ressources ; « Après votre décès, il vit » (`nouvelle_union` : seul, remarié,
  pacsé, en concubinage) ; « Ressources de son nouveau conjoint »
  (`ressources_nouveau_conjoint`), qui suppose l'union. La saisie refuse ce
  qui ne tient pas, avec les mots du modèle, et l'adresse les garde.
- *La chronologie* : deux faits des ressources du survivant, à la date du décès
  comme elles — la part de son activité (`nature: revenus_d_activite`), et son
  ménage (`nature: menage`, la forme de l'union et ce que le nouveau conjoint
  apporte). Le ménage est un fait du survivant, sans date : le modèle ne
  calcule la réversion qu'à sa date d'effet. Le nouveau conjoint n'y est pas
  encore une personne liée (§ 5.1) : l'union datée, avec la naissance qu'elle
  demande, viendra avec le remariage, quand la réversion se suivra dans le
  temps. `Conjoint` porte `revenus_d_activite`, `nouvelle_union` et
  `ressources_du_nouveau_conjoint`.
- *Le modèle* (`droit/reversion.py`, `_ressources_du_plafond`, et son jumeau) :
  les revenus d'activité abattus de 30 % quand le survivant a cinquante-cinq
  ans à la date d'effet ; en couple, les ressources du nouveau conjoint en
  plus, sous le plafond multiplié par `facteur_menage` — 1,6 au régime général
  depuis juillet 2004, 1 à la RCI ; la majoration de 11,1 % ne compte plus ces
  revenus d'activité pour des retraites. Avant juillet 2004, les réversions des
  autres régimes de base ne comptent plus aux ressources du régime général :
  le moteur les y comptait. Chaque ligne dit son `plafond` et ses
  `ressources_retenues`.
- *La fiche* `reversion` : la version `reforme_2004` est coupée au 1er janvier
  2005, première date d'effet après le décret, dans une version
  `abattement_2005` ; les paramètres `abattement_activite` et
  `abattement_activite_age` ; l'approximation « le survivant vit seul »
  remplacée par ce qui reste ; la présomption `survivant_seul`, au vocabulaire
  et au § 5.6, et `ressources_du_survivant` étendue au nouveau conjoint. La
  fiche `reversion_rci` reçoit les mêmes paramètres, et cite l'article 17.
- *La page* : la carte de la réversion ne suppose plus que le conjoint vit seul
  quand la saisie dit le contraire ; une réversion réduite l'est « avec les
  ressources du ménage ».
- *Les tests* : le barème de la Cnav, seul et couple, de 2005 à 2026, au
  centime, pour les trois formes d'union ; l'écrêtement du ménage ; les
  ressources personnelles d'avant 2004, sans le ménage ni les réversions ;
  l'abattement à ses quatre bornes ; la majoration de 11,1 % ; la RCI ; la
  saisie, l'adresse, la page, la chronologie des deux moteurs ; l'exemple de la
  circulaire n° 2006-37, rejoué à ses trois dates (`exemples_officiels.yaml`) ;
  deux témoins de simulation, `reversion_menage` et
  `reversion_revenus_d_activite`.

**Les mesures.** Aucune pension des six scénarios ne bouge, sur 772 témoins, ni
aucune réversion des témoins : ils gagnent les deux champs, et
`reversion_maximum_des_pensions`, décès de mai 2005, passe de la version
`reforme_2004` à `abattement_2005`, au même montant. La veuve du témoin
`reversion_ressources_declarees`, 15 000 euros de ressources, reçoit du
régime général 8 441,60 euros, écrêtés au plafond d'une personne seule ;
pacsée à un conjoint qui en a 16 000, 6 506,56 euros sous le plafond du
ménage (−22,9 %) ; salariée seule, son salaire abattu, la réversion entière,
9 592,50 euros (+13,6 %). Les pages du formulaire gagnent les trois champs,
repliés avec le bloc ; le budget de mots du formulaire vierge ne bouge pas.

**Ce qui reste.**

1. *De l'étape 4, dans l'ordre* : la réversion d'un assuré mort avant son
   départ (R. 353-6) ; le partage entre ex-conjoints et le remariage — où le
   ménage déclaré servira, et le nouveau conjoint deviendra une personne de la
   chronologie, avec une union datée — ; L. 353-5 et D. 355-1, avec lesquelles
   les retraites personnelles du survivant sortiront de ses ressources d'avant
   juillet 2004 ; les majorations forfaitaires d'avant 1995 et 1982.
2. *Du plafond* : la révision de la réversion quand le ménage ou les
   ressources changent, jusqu'à sa date de dernière révision (R. 353-1-1) ;
   les trois mois de la période de référence, les douze à défaut ; le plafond
   de 2004 au SMIC de juillet ; les ressources que le droit de l'allocation
   supplémentaire exclut, et la majoration pour enfants des retraites du
   survivant, que la saisie ne distingue pas.
