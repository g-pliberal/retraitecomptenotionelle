# Étape 17, cinquième partie : les versements uniques des petites pensions

**Le 8 octobre 2026, la demande.** Le propriétaire : « D'abord le versement
forfaitaire unique du régime général, abrogé par la loi n° 2014-40 (TRAJECTOiRE
le garde à tort après 2016, voir son écart au registre). Ensuite les capitaux
des petites complémentaires : Arrco et Agirc jusqu'en 2018, Agirc-Arrco jusqu'à
100 points, Ircantec sous 300 points (points de Destinie 2 et de TRAJECTOiRE). »

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ; les
fiches citent chaque texte).

- *Le versement forfaitaire unique* (R. 351-26, décret n° 45-0179, article 72,
  avant 1985) : la pension de vieillesse dont le montant annuel, « y compris le
  cas échéant les avantages complémentaires », est inférieur à 175 F au
  1er juillet 1974, revalorisés comme les pensions, « ne peut être servie » ;
  un versement de quinze fois ce montant la remplace. Le barème de la Cnav en
  donne chaque valeur, de 175 F à 156,24 € en octobre 2015, et la caisse le
  revalorise encore : 183,01 € en 2026. La loi n° 2014-40 (article 44, V)
  abroge L. 351-9 pour « les assurés dont l'ensemble des pensions prend effet
  à compter du 1er janvier 2016 » : la Cnav ne le verse plus qu'à « l'assuré
  dont la 1re retraite prend effet avant 2016 ». TRAJECTOiRE le garde à tous ;
  Destinie 2 l'arrête en 2015, sans la suite.
- *L'Agirc-Arrco* (accord du 17 novembre 2017, article 107) : l'allocation «
  inférieure ou égale » à l'équivalent de cent points n'est pas attribuée ;
  l'assuré reçoit sa valeur viagère, l'allocation annuelle, coefficients et
  majorations compris, par un coefficient de son âge révolu, d'une table que
  chaque mois de décembre renouvelle ; le versement supprime la réversion.
  Avant 2019, selon la fiche RET-B100 des éditions GERESO, qui date le
  dispositif de 2004 : l'Arrco jusqu'à cent points, l'Agirc sous cinq cents,
  minorés ou non, sur une table plus basse — celle de Destinie 2.
- *L'Ircantec* (arrêté du 30 décembre 1970, article 25) : sous 500 points
  jusqu'en 1975, 100 jusqu'en septembre 2008, 300 depuis, les points au
  salaire de référence de l'année qui précède ; versé à l'agent, le capital
  supprime le droit du conjoint, depuis 1971.

**Ce qui est fait.**

- *Trois fiches*, en versions à la date d'effet, lues par les deux moteurs
  (`FichesDatees`) : `versement_forfaitaire_unique`, ses seuils au barème de
  la Cnav et la condition de la première retraite depuis 2016 ;
  `versement_unique_agirc_arrco`, ses allocations — l'Arrco et l'Agirc avant
  2019, un seul groupe depuis —, sa mesure, en points ou en euros, et ses six
  tables de coefficients ; `versement_unique_ircantec`, ses trois seuils.
- *Le modèle* (`verser_en_capital`, à la fin de « compléter tous régimes », et
  son jumeau) remplace la petite pension par un capital, que la pension du
  régime porte (`PensionRegime.capital`), avec la formule qui le dit ; son
  montant annuel reste celui de la pension remplacée, comme pour le capital du
  RAFP. La retraite progressive n'est jamais remplacée. Les pensions que des
  départs précédents servent disent leur date d'effet (`PensionServie`) : la
  première retraite de base s'y lit.
- *La réversion* : celle de l'Agirc-Arrco depuis 2019 et celle de l'Ircantec à
  toute date ne suivent plus un droit direct versé en capital
  (`rien_apres_un_capital`, que les moteurs lisaient pour le RAFP).
- *Le registre* : le point de Destinie 2 et celui de TRAJECTOiRE sur les
  complémentaires, repris.
- *Les tests* (`tests/test_versements_uniques.py`, douze) : les seuils, les
  tables et leurs bouts ; une pension de 93,18 € en 2015, remplacée par quinze
  annuités ; une de 10 € en 2018, servie ; celle de 2017 d'une fonctionnaire
  partie en 2012, remplacée ; l'Arrco de 2015 et de 2018, l'Agirc-Arrco de 2022
  sous et au-dessus de cent points, l'Ircantec de 2022 ; la retraite
  progressive ; la réversion ; six requêtes dans les deux moteurs.

**Les mesures.** Deux trimestres en 1970, une pension de 93,18 € par an en
2015 au minimum contributif : 1 397,77 € en une fois. La pension de 3,14 € en
2017 d'une fonctionnaire partie en 2012 : 47,16 €. L'Arrco de 27,95 points en
2015 : 594,53 €, 17,0 annuités ; l'Agirc-Arrco de 30,72 € en 2022, sous les
128,41 € de cent points : 801,71 €, 26,1 annuités à 64 ans ; l'Ircantec de
116,41 points en 2022 : 585,30 €, au salaire de référence de 2021. Sur les 763
témoins de simulation, un seul bouge, `enfants_fonctionnaire_un_an_puis_prive`
: son Ircantec de 236,88 points, versé en 2026 en un capital de 1 358,51 €, que
sa formule dit ; aucune pension ne bouge, ni aucune page. Les deux moteurs
concordent sur les six requêtes du test.

**Ce que la vérification a trouvé.**

- Le registre croyait le versement de la Cnav « jusqu'en 2015 » : il vaut
  encore pour la pension d'après 2016 de qui a pris une retraite avant, et son
  seuil se revalorise toujours.
- L'accord dit « inférieur ou égal » à cent points, les circulaires des
  coefficients « inférieur à » : le modèle suit l'accord.
- La table de 2022 (circulaire n° 2021-9-DRJ) n'est plus servie par le site
  de l'Agirc-Arrco, ni par les archives de l'Internet Archive ; celle de 2019
  n'est pas trouvée. Les écarts qu'elles laissent sont déclarés.
- `textes.py` : douze rédactions rattachées, le cliquet descend à 9 890.

**Ce qui reste**, de cette partie :

1. La réversion versée en capital (article 107, et l'article 25 de l'Ircantec
   pour le conjoint), et la règle de la réversion d'avant 2019 après un capital.
2. Les tables de 2019 et de 2022 ; les accords de l'Arrco et de l'Agirc
   d'avant 2004.
3. Le capital comme composante versée une fois au journal, que « faire vivre »
   ne mène plus, pour le RAFP comme pour les autres.
4. Les versements forfaitaires des régimes alignés et spéciaux que l'index
   nomme ; le remboursement des cotisations de L. 161-22-2, sur demande.
5. Pour l'étape 4 : le seuil de L. 351-9, que la réversion du régime général
   lit (L. 353-1), est désormais à la fiche du versement forfaitaire.
6. Les limites, à la fin de l'étape : les trois fiches sont approchées.
