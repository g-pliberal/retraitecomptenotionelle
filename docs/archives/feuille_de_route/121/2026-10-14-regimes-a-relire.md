# Les régimes à relire : quinze sur dix-sept, texte en main

**Le 14 octobre 2026, quinze des dix-sept régimes que
`tests/test_regle_de_chacun.py` déclarait `A_RELIRE` en sortent, texte en main
(index LEGI à jour du 11 octobre 2026).** Leur durée se lit, comme à la
Comédie-Française, à la date où l'assuré réunit les conditions, et non à sa
génération ; l'âge de la Banque est la table de son règlement, et non la table
commune. Ce qui varie encore avec l'année du départ est l'entrée en vigueur
d'un texte, déclarée à l'année d'effet (`A_L_ANNEE_D_EFFET`). La MSA des
non-salariés a, elle aussi, sa durée propre, que la fiche empruntait au
régime général ; la CARMF et l'ASV s'ouvrent à l'âge légal de la génération,
et non à soixante-deux ans. La CNAVPL, la CNBF, la CAVIMAC, la CARPIMKO et la
CPRN ne basculent qu'à l'entrée en vigueur de leurs textes, comme la
Comédie-Française en 1993 et les cinq complémentaires en 1983. Restent à relire
la durée de la CARMF et celle du CESE.

## L'Opéra national de Paris

Le V de l'article 14 du décret n° 68-382 est, mot pour mot, celui de la
Comédie-Française : 151 trimestres « pour les personnes remplissant les
conditions définies à l'article 6 entre le 1er juillet et le 31 décembre
2008 », un de plus par semestre jusqu'en 2012, puis chaque 1er juillet jusqu'à
166 en 2018 (rédaction du décret n° 2008-1497, LEGIARTI000020056984) ; « à
compter du 1er juillet 2019 », la table par génération, 167 trimestres des nés
du 1er juillet 1959 à 172 à compter de 1973, lue à soixante ans par le VI
(LEGIARTI000029135692, puis LEGIARTI000029135161). La fiche lisait la table
commune, par génération. Elle lit désormais le calendrier de 2008
(`regimes_speciaux_2008`) et la table `opera_de_paris_2014`
(`legislation/duree_requise_regimes_speciaux.csv`).

Présomption déclarée : le A de la table ne nomme que les 4° et 5° de
l'article 6, musiciens et autres catégories ; la fiche, qui suit le ballet,
lui lit la même table, la seule que le décret écrive. Le B (assurés du 4° du I
de l'article 52) n'est pas transcrit.

L'âge, lui, compte à l'année d'effet : le décret n° 2002-347 du 12 mars 2002
ouvre le droit « à quarante ans d'âge pour les artistes du ballet » dès le
14 mars 2002 (LEGIARTI000006765539), au lieu de quarante-cinq pour les hommes,
sans disposition transitoire sur l'âge d'ouverture — son V ne règle que la
mise à la retraite d'office.

## La Banque de France

Le règlement annexé au décret n° 2007-262 écrit ses propres tables, que la
fiche remplaçait par celles de la fonction publique et du régime général.

- **L'âge** (article 72) : soixante ans pour les agents nés avant 1956, trois
  mois de plus par semestre jusqu'à soixante-deux ans pour les nés à compter
  du 1er juillet 1959 (décret n° 2012-701, LEGIARTI000042384599) ; puis
  soixante-deux ans avant 1963, trois mois par génération jusqu'à l'âge de
  L. 161-17-2, soixante-quatre ans, à compter de 1970 (décret n° 2023-693,
  LEGIARTI000047909725), son VI gardant l'ancienne règle à qui réunit les
  conditions avant 2025. Table `banque_de_france`
  (`legislation/ages_regimes.csv`). La fiche donnait soixante ans et neuf mois
  à un agent né en 1952, et, en 2023-2024, soixante-deux ans à tous.
- **La durée** (article 69) : « fixée en fonction de la date à laquelle
  l'agent est susceptible de liquider sa pension » — 150 trimestres jusqu'au
  31 mars 2007, puis un de plus par trimestre ou semestre jusqu'à 166 au
  1er juillet 2014 (calendrier `banque_de_france_2007`) ; « à compter du
  1er janvier 2018 », 167 trimestres des nés de 1958 à 172 à compter de 1973
  (`banque_de_france_2014`) ; « à compter du 1er janvier 2025 », 169, 170 et
  171 pour 1963, 1964 et 1965 (`banque_de_france_2023`). La fiche donnait 160
  trimestres à un agent né en 1948, qui a soixante ans en 2008 et en doit 153.

Présomption déclarée : 172 trimestres pour les nés de 1966 à 1972, la durée de
l'article 31, que le IV rejoint une génération après le régime général (et le
V, pour les actifs, cinq ans plus tard). À la lettre, le III, que le décret de
2023 n'abroge pas, leur donnerait encore 169 à 171 trimestres, moins qu'aux nés
de 1965. `tests/test_cnracl.py` attendait déjà 172 pour un agent né en 1967.

Ce qui varie encore : la fiche fait commencer le règlement en 2008, avec sa
période, et garde avant les cinquante-cinq ans et les 150 trimestres de
l'ancien régime, que LEGI ne porte pas. Le règlement vaut, lui, depuis le
printemps 2007 (son article 69 compte « jusqu'au 31 mars 2007 ») : c'est
déclaré à l'année d'effet, de 2008 à 2012 — les nés de 1949 à 1952, qui
partaient à cinquante-cinq ans, ne peuvent plus partir avant soixante, et leur
premier départ sous le règlement tombe de 2009 à 2012.

## La MSA des non-salariés agricoles

L'âge compte à l'année d'effet : la loi n° 86-19 du 6 janvier 1986 ouvre la
pension à soixante ans pour les pensions « prenant effet postérieurement au
1er janvier 1986 » (article 11, LEGIARTI000006757038), ce que la fiche disait
déjà ; seule la génération 1920, qui partait à soixante-cinq ans en 1985, le
montre.

La durée, elle, était fausse. R. 732-39 du code rural (LEGIARTI000006597424,
puis LEGIARTI000024113166) écrit la durée en deçà de laquelle la pension est
minorée : 150 trimestres pour l'assuré né avant 1944, 152 pour 1944, deux de
plus par génération jusqu'à 160 pour 1948, « pour les pensions prenant effet
avant le 1er janvier 2009 » ; après, « la limite mentionnée au deuxième alinéa
de l'article L. 351-1 », la durée de proratisation du régime général, qui
porte les mêmes nombres. La fiche opposait, à compter de 2004, la durée du
taux plein du régime général : 151 à 160 trimestres aux nés de 1934 à 1943,
160 aux nés de 1944 à 1947. Table `msa_non_salaries_2005`, branchée sur les
périodes de 2004 et après.

Le moteur apprend pour cela qu'une table propre peut s'arrêter : une ligne sans
trimestres (ici, la génération 1949) la fait taire, et la table commune
reprend (`DureesRequisesRegimes`, en Python et dans `moteur/js/regimes.js`).
Les deux moteurs concordent (`test_liquidation.py`, `test_minima_agricoles.py`,
paquet refait en local) ; les témoins du portage sont à refaire par GitHub.

## La CNAVPL, la CNBF, la CAVIMAC, la CARPIMKO et la CPRN : l'année d'effet

Aucune valeur n'y change ; chacune bascule à l'entrée en vigueur d'un texte,
désormais déclarée avec lui dans `A_L_ANNEE_D_EFFET`.

- **CNAVPL** : le régime en points « entre en vigueur le 1er janvier 2004 »
  (loi n° 2003-775, article 96, I, LEGIARTI000006758646) ; L. 643-3 ouvre la
  pension à l'âge de L. 351-1 et renvoie, pour la durée, au « deuxième alinéa
  de l'article L. 351-1 », la durée du taux plein (R. 351-27) : la table que
  la fiche lit est la bonne.
- **CNBF** : L. 723-10-1, même âge, même durée, « entre en vigueur le
  1er janvier 2004 » (loi n° 2003-775, article 97, II, JORFARTI000002429604).
- **CAVIMAC** : le décret n° 2006-1325 abaisse à soixante ans l'âge de la
  pension d'avant 1998 dès sa publication, le 1er novembre 2006, sans
  disposition transitoire (JORFARTI000001085913) ; la fiche coupe au
  1er janvier 2007. La fiche est aussi celle de la session de l'action 119 :
  elle n'est pas touchée ici.
- **CARPIMKO** : l'article 12 quater des statuts (arrêté du 31 juillet 2015,
  publié le 2 octobre, JORFARTI000031255547) ouvre la retraite à soixante ans
  aux générations 1955 et antérieures ; la fiche le sert à partir de 2016, et
  lit avant l'âge légal de la génération, faute d'avoir lu les statuts de 1968
  modifiés.
- **CPRN** : l'article 18 des statuts diffère l'âge légal de vingt-quatre mois
  pour les nés à compter de 1954 (arrêté du 16 décembre 2013), puis revient à
  l'âge légal (arrêté du 29 novembre 2023, en vigueur le 1er janvier 2024).

## La CARMF et l'ASV : l'âge de la génération

Depuis la retraite en temps choisi (1er janvier 2017), les deux régimes
« s'ouvrent à taux plein à l'âge légal », et la majoration court de
soixante-deux ans (arrêtés du 22 mars 2017 et règlement du 10 juillet 2026).
Les fiches portaient soixante-deux ans comme âge d'ouverture, pour placer la
majoration : l'âge des nés de 1947 à 1954 passait de soixante à soixante-deux
ans d'une année de départ à l'autre, et les nés de 1962 et après s'ouvraient
avant leur âge légal. La majoration a son propre champ (`surcote_age_debut:
62`) ; l'âge d'ouverture est désormais l'âge légal de la génération
(`age_ouverture_par_generation`). La durée de l'ASV, elle, disparaît bien au
1er janvier 2017, « sans décote ni durée » : année d'effet de l'arrêté du
1er décembre 2016.

## La Comédie-Française de 1993 et les complémentaires de 1983

- **Comédie-Française** : le décret n° 93-430 du 22 mars 1993
  (JORFTEXT000000345623) récrit l'article 6 du décret n° 68-960 — soixante ans
  pour les artistes aux appointements dès le 25 mars 1993, au lieu de
  cinquante-cinq pour les hommes (LEGIARTI000006765430) —, sans disposition
  transitoire dans aucun de ses huit articles. De 1994 à 1997, la même
  bascule, au premier départ que le décret ouvre aux nés de 1934 à 1937.
- **Agirc, Agirc des entreprises nouvelles, Arrco, sa tranche 2, Ircantec** :
  « à compter du 1er avril 1983 », la durée du taux plein au régime de base
  annule le coefficient d'anticipation (accord ASF du 4 février 1983 ; arrêté
  du 30 décembre 1970, article 16, 6° c), LEGIARTI000006381610, pour
  l'Ircantec). Avant, l'âge seul : la période ne porte aucune durée, et les
  160 trimestres que le test relevait sont le repli du moteur, que
  l'abattement par l'âge seul ne consulte pas (`liquider.py`, `par_age_seul`).

## Ce qui reste à relire

- **La durée de la CARMF**, de 1930 à 1939 : l'article 15 des statuts minore
  par l'âge seul depuis 2000, et la durée n'y joue plus ; avant 2000, la fiche
  lit la durée de la génération, sans avoir lu les statuts d'alors.
- **Le CESE** : l'article 17 de son règlement fixe un taux par annuité selon la
  date du MANDAT (2,11 % jusqu'au 31 août 2004, 2,02 % jusqu'au 30 septembre
  2010, puis 1,95, 1,90, 1,85 et 1,82 %), que la fiche écrit en durée requise
  par année de départ. Il faut au moteur un taux par annuité acquise, qu'il n'a
  pas : un chantier du modèle, à mener avec son jumeau JS.

## Ce qui reste

- Dans le registre `A_RELIRE` : la durée de la CARMF et le CESE (ci-dessus).
  L'index JORF ne porte, pour la CARMF d'avant 2000, que des résumés
  d'arrêtés ; ses statuts d'alors sont à chercher ailleurs (la caisse, le
  Journal officiel en fac-similé).
- Banque de France : l'ancien régime, avant 2007 (âge, durée) ; la coupure de
  la fiche au 1er avril 2007 plutôt qu'en 2008 ; l'âge d'annulation de la
  décote (article 34, et le III de l'article 72), qui reste celui de la
  fonction publique ; les catégories à nomenclature, cinq ans plus bas ; ce que
  la Banque applique aux nés de 1966 à 1972.
- Opéra : ce que la caisse applique au ballet, aux chœurs et aux emplois à
  fatigues exceptionnelles après juillet 2019, que le A ne nomme pas.
- Pour les pages (session du site) : la méthode, « Ce que le système 1
  applique du droit en vigueur », pourrait dire que la durée de l'Opéra et de
  la Banque de France, comme celle des autres régimes spéciaux, se lit à la
  date où l'assuré réunit les conditions.
