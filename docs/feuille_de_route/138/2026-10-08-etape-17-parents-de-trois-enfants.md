# Étape 17, deuxième partie : le départ anticipé des parents de trois enfants

**Le 8 octobre 2026, la demande.** Le propriétaire : « Action 138, étape 17 : le
départ anticipé du fonctionnaire parent de trois enfants qui avait quinze ans de
services avant 2012, avec la durée et la décote de l'année des conditions ou de
sa génération (point de Destinie 2 au registre, chantier 138.17). Je le fais
passer avant la bonification des militaires, que la note met en tête. »

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre).

- *Le départ.* « La liquidation de la pension intervient : […] 3° Pour les
  femmes fonctionnaires : a) Soit lorsqu'elles sont mères de trois enfants
  vivants » (L. 24, I, rédaction de 1982, et le décret n° 65-773 pour la
  CNRACL dès 1965), avec les quinze ans de services sans lesquels aucune
  pension n'est due ; depuis la loi du 30 décembre 2004, le parent « à condition
  qu'il ait, pour chaque enfant, interrompu son activité » deux mois au moins,
  dans un congé de maternité — celui du régime général compris —, de paternité,
  d'adoption, parental, ou une disponibilité, l'absence de cotisation étant
  assimilée (R. 37). La CNRACL et le FSPOEIE par renvoi.
- *La durée et la décote* sont celles de l'« Année au cours de laquelle sont
  réunies les conditions mentionnées au I et au II de l'article L. 24 » (loi
  n° 2003-775, article 66, II et III) : 150 trimestres et aucune décote pour qui
  les réunit avant 2004, à quelque date qu'il parte.
- *La loi du 9 novembre 2010* abroge le 3° au 1er juillet 2011 et n'en garde le
  bénéfice qu'à qui a quinze ans de services avant le 1er janvier 2012 et trois
  enfants à cette date (article 44, III). Elle lui oppose la durée et la décote
  de l'année où il atteint « l'âge prévu au dernier alinéa du I de l'article 5
  de la loi n° 2003-775 » — soixante ans, dans toutes ses rédactions — « ou, le
  cas échéant, l'âge prévu au I de l'article 22 », cinquante-sept ou
  cinquante-deux ans en catégorie active ; la décote de L. 14, I, si cet âge
  tombe après 2019 ; la durée de la dernière génération fixée si celle de
  l'année ne l'est pas. L'ancien calcul demeure aux demandes présentées avant
  2011 pour une radiation au plus tard le 1er juillet 2011, et à qui était, au
  1er janvier 2011, à moins de cinq ans de son âge d'ouverture — et ceux-là
  gardent l'ancien L. 17, le minimum garanti sans condition (article 44, IV ;
  décret n° 2010-1741 pour la CNRACL et le FSPOEIE). La réponse ministérielle du
  5 juillet 2011 (question n° 97363) le dit en clair.
- *La loi du 14 avril 2023* garde au fonctionnaire qui pouvait liquider avant
  soixante ans, et avant le 1er septembre 2023, la durée d'avant elle (article
  10, XXIV, C, 1°) : 168 trimestres, non 169, à la mère née en 1962.

**Ce qui est fait.**

- *La fiche* `depart_anticipe_parents_trois_enfants`, en quatre versions sur la
  date d'effet — avant 1982, supposée ; 1982 ; la loi du 30 décembre 2004 ; la
  loi du 9 novembre 2010 —, que les deux moteurs lisent (`FichesDatees`) ; un
  bénéficiaire, un calcul ou un classement inconnus les arrêtent. Elle donne
  leur statut à trente-trois rédactions : le cliquet des textes descend à 9 915.
- *Le modèle* (`droit/ouvrir.py`, son jumeau) : `depart_parent_trois_enfants`
  lit la fiche et la carrière — la mère, trois enfants nés, quinze ans dans les
  trois régimes du code des pensions, le militaire écarté — et rend l'âge des
  conditions réunies, l'année des paramètres et l'ancien calcul ;
  `age_ouverture` prend cet âge, `annee_ouverture_des_droits` cette année,
  sans la borner à la liquidation hors de l'ancien calcul ; `duree_requise` lit
  la durée de l'année (`duree_de_l_annee`, que la durée d'avant soixante ans
  partage désormais) ; le minimum garanti garde l'ancien L. 17 au parent de
  l'ancien calcul (`droit/liquider.py`).
- *Les présomptions* : `interruption_d_activite_par_la_mere` vaut aussi pour ce
  départ ; `demande_de_pension_avant_2011` naît, au vocabulaire et au § 5.6 de
  l'architecture, pour la pension qui prend effet au plus tard le 1er juillet
  2011.
- *Le registre* : les points de Destinie 2 et d'OpenFisca-France-Pension,
  repris. Les limites et le tableau de l'architecture le disent.

**Les mesures.** Sur les témoins, aucune pension ne bouge ; deux âges
d'ouverture opposables descendent à la date des conditions réunies, et six
témoins neufs balaient l'ancien calcul, le nouveau, le père et l'active ; le
portage les retrouve. Retirer la fiche (la contrefactuelle du module des
avantages) mesure ce qu'elle sert, à une fonctionnaire de l'État mère de trois
enfants : née en 1953, entrée à vingt-cinq ans, partie à soixante et un, son
départ s'ouvre et elle garde 150 trimestres sans décote, + 22,4 % ; née en 1955,
entrée à trente-huit ans, partie à cinquante-six, 158 trimestres et 0,25 % par
trimestre, ceux de 2007, + 17,4 % ; née en 1965, partie à cinquante ans, son
départ s'ouvre, à la durée de 2025 et vingt trimestres de décote, le même
montant ; née en 1962, partie à soixante-quatre ans, 168 trimestres au lieu de
169, + 0,6 %. Destinie 2 n'a pas été exécuté : les tests rejouent les trois cas
que son code distingue, et la fiche déclare les deux points où il s'écarte du
texte — aucune décote à l'ancien calcul, et le nouveau lu à l'année de l'âge
d'ouverture de la génération, non de ses soixante ans.

**Ce qui reste** de cette partie, hors de l'ordre de l'étape :

1. *Un exemple chiffré publié*, du service des retraites de l'État ou de la
   CNRACL, à rejouer ; la fiche reste approchée sans lui.
2. *Le père* qui a pris un congé parental ou une disponibilité pour chaque
   enfant : un champ de saisie, que la bonification de L. 12, b, lirait aussi.
3. *L'officier parent de trois enfants* (L. 24, II, 1° bis), et l'âge de
   L. 4139-16 du code de la défense qui décide de son ancien calcul.
4. *Les régimes spéciaux* qui avaient leur départ des parents de trois enfants,
   éteint par leurs décrets de 2008 à 2011 : CRPCEN, Comédie-Française, SNCF,
   RATP, IEG, Banque de France, Opéra.
5. *L'inventaire des avantages non contributifs*, qui ne porte pas ce départ, et
   son coût par retrait de la fiche ; et le motif d'ouverture que le site dirait
   « parent de trois enfants » au lieu d'« âge légal » : la zone du site.
