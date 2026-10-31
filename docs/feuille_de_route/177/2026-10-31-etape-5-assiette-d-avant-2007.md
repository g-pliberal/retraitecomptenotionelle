# Étape 5 : l'assiette d'avant 2007, la régularisation sur le revenu de l'année et ses trois exceptions

**Le 31 octobre 2026, ce qui est fait.** La lecture d'abord, puis la question
au propriétaire, qui a choisi la limite seule : aucune règle ne change, la
fiche `cotisation_vieillesse_independants` tranche la question qu'elle mettait
à relire et passe de `transcrite` à `approchee`, une limite dit les trois
exceptions.

1. *La lecture.* Dans l'index LEGI à jour du 30 octobre 2026, toutes les
   rédactions de D. 633-5, D. 633-6, D. 633-10 et D. 633-11, celles de
   L. 131-6 de 1995 à 2007, R. 634-1, et les articles 1er, 5, 6, 9 et 10 du
   décret n° 73-76 ; dans l'index du JORF, le décret n° 2000-834 du 25 août
   2000. Le texte qui a mis la régularisation en œuvre est le décret de 1973 :
   « Il est procédé le 1er janvier de chaque année et pour la première fois le
   1er janvier 1975 en ce qui concerne les cotisations de l'année 1973 à
   l'ajustement des cotisations provisionnelles [...] sur la base des revenus
   de l'année à laquelle se rapportent ces cotisations » (article 9, rédaction
   du 1er janvier 1978), que D. 633-10 garde de 1985 au 1er janvier 2008 ;
   L. 131-6 ne fait que le porter dans la loi en 1995. R. 634-1 calcule le
   revenu annuel moyen sur « l'ensemble des cotisations versées ». La
   convention du modèle, chaque année sur son propre revenu, est donc celle du
   droit. Trois exceptions :
   - *La première année d'activité, jusqu'en 1999.* L'article 6 du décret
     n° 73-76, puis D. 633-6, assied la cotisation « de l'année ou de la
     fraction d'année de début d'exercice » sur « un revenu forfaitaire égal au
     tiers du plafond », sans la dire provisionnelle, quand celle de l'année
     suivante l'est ; l'ajustement ne vise que les cotisations
     provisionnelles, et n'abaisse celle de la première année que « sur
     demande », si le revenu est moindre (D. 633-10, 1985), ou la régularise
     au plus jusqu'au forfait quand la caisse l'a d'abord réduite, sur
     demande, jusqu'au dixième du plafond (1995). L. 131-6 la rend provisionnelle le 30 décembre 1999 (loi
     n° 99-1140, article 11), et le décret n° 2000-834 aligne D. 633-6 et
     supprime les deux alinéas de D. 633-10 le 1er septembre 2000 ; sa notice :
     « un calcul rectificatif intervenant une fois le revenu connu ».
   - *Les deux dernières années d'une activité qui cesse, jusqu'en 2007.* Ne
     font pas l'objet de l'ajustement « les cotisations des assurés qui ont
     cessé leur activité professionnelle à la date à laquelle l'ajustement
     aurait dû être opéré », ni celles « basées sur un revenu annuel pris en
     compte pour la liquidation d'un avantage de vieillesse » (article 10 du
     décret, D. 633-11 jusqu'au 1er janvier 2008). L'ajustement d'une année se
     faisant au 1er janvier de la deuxième année qui la suit, les deux
     dernières restent sur la base provisionnelle de D. 633-5 : les revenus
     « déclarés l'année précédente », ceux de l'avant-dernière année (1985) ;
     ceux de l'année précédente, la première fraction semestrielle sur
     l'avant-dernière (1995) ; ceux de l'avant-dernière (2004).
   - *L'année du départ.* Les exemples de la caisse « Prise en compte de la
     date d'arrêt du compte » (avant 2015, à partir de 2015, à partir du
     1er avril 2018) retiennent le plus petit de l'encaissé à la date d'arrêt
     du compte et de la cotisation provisionnelle appelée au prorata
     (378 € sur 434,43 € appelés, un trimestre en 2016), et écartent une dette
     ancienne réglée après la date limite, trois mois avant le départ.
   La base de la caisse ne cite ni D. 633-5, ni D. 633-6, ni D. 633-10, ni
   D. 633-11, et n'a pas les circulaires de la réforme de 2007 (décret
   n° 2007-878) ; son exposé « Travailleurs indépendants » ne décrit que le
   calcul d'aujourd'hui. Les textes tranchent seuls.
2. *La question au propriétaire*, posée avec trois réponses : la première
   année au forfait dans les deux moteurs, plafonnée et non imposée, pour
   qu'une année recopiée d'un relevé ne bouge pas ; la limite seule ; la
   première et les deux dernières années, dont le décalage s'appliquerait
   deux fois à une carrière recopiée d'un relevé, qui porte déjà le revenu
   décalé. Il a choisi la limite seule. La question chiffrait la première
   exception à 0,34 % de la pension : mesuré de plus près, ce sont les points
   du RCO, que le modèle tire du même revenu ; la retraite de base ne bouge
   pas (ci-dessous). La réponse n'en change pas.
3. *Ce qui est écrit.* La fiche : trois approximations, la question ôtée de
   `a_relire`, les lectures datées. La limite « assiette provisionnelle des
   artisans et des commerçants » (`docs/limites/3-systeme-actuel.md`). Au
   registre de la Cnav, l'exemple « Détermination des trimestres cotisés »
   `recoupe` (1 000 € de cotisations en 2016, trois trimestres, que
   `tests/test_independants.py` rejoue) et les trois exemples de la date
   d'arrêt du compte `limite`. La liste des textes : D. 633-10 et D. 633-11
   inscrits, et R. 634-1 de 1985 rattaché, d'où le cliquet abaissé d'un.

**Ce que le calcul en reçoit.** Rien : aucune règle ne change. Ce que les
exceptions changeraient, mesuré au moteur Python sur trois carrières, en
substituant à chaque année concernée le revenu que le droit porte au compte :

- un salarié de 1965 à 1979, puis artisan de 1980 à 2004 à 0,8 plafond, parti
  à soixante ans en 2005 : 15 685,19 € par an, dont 7 529,29 € de retraite de
  base des artisans et 2 630,59 € de RCO. L'année 1980 au tiers du plafond ne
  change pas la retraite de base (elle n'est pas parmi les meilleures) ; le
  RCO tombe à 2 576,70 €, mais il suit sa propre assiette (ci-dessous).
  Les années 2003 et 2004 au revenu de 2002 : la retraite de base tombe à
  7 469,95 € (−0,79 %), la pension à 15 616,27 € (−0,44 %) ;
- un artisan de 1973 à 1999 à 1,2 plafond : sa retraite de base ne bouge
  pas, le plafond bornant déjà les deux dernières années ;
- un salarié, commerçant de 1990 à 1994 à 1,5 plafond, puis salarié jusqu'en
  2009 : rien, pour la même raison.

Une première année sans revenu, cas fréquent d'une création, ne valide aucun
trimestre au modèle (le premier artisan, sans revenu en 1980, perdrait 10,6 %
de sa pension par la décote), quand le forfait lui en aurait valu quatre, sauf si l'assuré avait
demandé l'ajustement, ce que le texte lui laisse : la raison pour laquelle la
première réponse plafonnait au forfait sans l'imposer.

**Vu en chemin, non corrigé.**

- Le RCO des artisans : de 1985 à 2004, D. 635-4 assied sa cotisation « sur
  les revenus professionnels non-salariés de l'avant-dernière année civile »,
  et le modèle tire ses points du revenu de l'année. Un écart de la
  complémentaire, à lire avec le règlement du RCO avant toute retouche, que
  la feuille de route ne porte pas encore.
- La rédaction de l'article 6 du décret n° 73-76 d'avant le 1er janvier 1978
  n'est pas dans l'index LEGI, ni dans celui du JORF, qui n'a que le sommaire
  du décret.
- L'exposé « Travailleurs indépendants » reste `a_lire` : il porte aussi le
  micro-entrepreneur et l'assiette depuis 2025, que l'étape n'a pas lus.

**L'étape est faite.** La suite : l'étape 6, le premier trimestre du
micro-entrepreneur en 2014 et en 2015, à trancher d'abord
(`ECARTS_A_LA_GRILLE`) ; l'étape 7 revient à la session du site, l'étape 8 au
modèle.
