# Étape 7 : la CARMF avant 2017 et le taux acquis au 31 mars 1983

Les deux règles que l'étape 1 avait signalées, faute de les avoir lues : les départs
jusqu'à 119 ans les atteignaient pour la première fois.

- *La CARMF complémentaire, de 2000 à 2016.* La fiche servait la majoration de
  l'article 32 des statuts, « 5 % par année pleine de différé » au-delà de 65 ans, sans
  plafond : un médecin parti à 116 ans en 2016 en comptait cinquante et une. La caisse
  ne majore pas le départ après 65 ans avant 2017 : sa table « Pourcentage de la
  retraite perçue selon l'âge de départ » (réunions de formation 2018, diapositive 18)
  porte, « Avant réforme », 100 % de 65 à 70 ans, et ses diaporamas de 2008 et de 2015
  disent « Sans minoration à partir de 65 ans », sans rien au-delà. L'article 32 vise le
  médecin « remplissant toutes les conditions », dont celle de « cesser l'exercice de la
  médecine non salariée » (arrêté du 28 septembre 2011) : il majore le temps entre la
  cessation et la demande, que le modèle, où l'on part en cessant, ne connaît pas. Les
  sept périodes de 2000 à 2016 de `carmf_complementaire` ne majorent plus ; la fiche
  `surcote_par_age_seul` le dit, avec la lecture. Le portage le lit dans le paquet.
  Depuis 2017, la table de la caisse (1,30 à 70 ans) confirme qu'elle ne cumule pas
  l'article 32 avec la majoration de l'article 15 : la question de la fiche est close.
- *Le taux acquis au 31 mars 1983, depuis 2004.* L'arrêté du 9 octobre 1986, article 2,
  majore le maximum des pensions « compte tenu des coefficients de majoration acquis » au
  31 mars 1983 ; l'index LEGI le donne en vigueur sans version suivante, et L. 351-1
  garde son cinquième alinéa en 2003 comme en 2010. Le moteur remettait ce coefficient
  à 1 dès qu'une surcote entrait en compte, en 2004 : une carrière née en 1900, au taux
  de 140 %, tombait de 38 946 € en 2003 à 14 856 € en 2004. Il le garde désormais, en
  Python et en JavaScript (`droit/liquider.py`, `liquider.js`), et la surcote s'applique
  à la pension ramenée à ce maximum (circulaire n° 2007-5) : 39 940 € en 2004. Ce que le
  changement corrige aussi : la branche sans barème daté pouvait multiplier le taux, déjà
  acquis, par le coefficient du taux acquis quand aucun trimestre de surcote ne restait.
- *Les tests.* `test_sections_sante.py` : la CARMF ne majore pas un départ à 68 ans en
  2013 ni à 70 ans en 2016. `test_pension_maximale.py` : né en 1917, parti en 2005, la
  pension est ramenée à 55 % du plafond puis surcotée de 4,5 % ; le cas entre dans la
  comparaison des deux moteurs.

## Ce qui reste

- La rédaction d'origine de l'article 32 de la CARMF (Bulletin officiel), et si la
  surcote de 2004 se cumule avec le taux acquis au 31 mars 1983, que ni la circulaire
  n° 2007-5 ni les textes lus ne disent : le moteur les cumule, comme avant.
- Ce que l'étape 6 laissait : la Banque de France, la limite des IEG et de l'Opéra avant
  2008, le statut du mineur ; au site, nommer la fin de l'emploi des trois fiches neuves ;
  pour le propriétaire, la radiation dans les comptes notionnels, l'actif d'avant 2010,
  les choix des étapes 4 et 6.
