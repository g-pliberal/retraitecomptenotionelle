# Étape 4, thème « Accords internationaux et d'outre-mer », sous-thèmes « Règlements européens » et « Accords d'outre-mer » : les exposés et leurs références

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 de 14 h 11 à 14 h 31 UTC, par
  `_obtenir`, `_reference` et `_fenetre` de `scripts/fetch/cnav_legislation.py`, sans écrire le
  registre par le script : `/expose`, `/liste`, `/mises-a-jour`, les collections des fenêtres, et
  trois références que seule lie la liste des personnes qui relèvent des règlements. Les 39
  exposés sont servis à la date que le registre porte (`dateModification`, du 24 octobre 2025
  au 21 septembre 2026). Les liens de la base sont ceux de ses routes, sans chemin du site
  SharePoint de la caisse.
- *La lecture* : les 39 exposés, en entier, par cette session. « Règlements européens » (24) :
  le champ d'application des règlements n° 883/2004 et n° 1408/71, l'application d'un règlement
  neuf, la conversion des périodes, l'instruction des demandes, l'allocation supplémentaire,
  l'allocation de veuvage (trois), la pension de vieillesse de veuve ou de veuf, la majoration
  forfaitaire pour charge d'enfant (trois), la majoration pour tierce personne (deux), la
  retraite personnelle (six : anciens règlements, attributions successives, minimum, mode de
  calcul, montant de la retraite communautaire), la réversion (quatre). « Accords d'outre-mer »
  (15) : Mayotte (4), la Nouvelle-Calédonie (4), la Polynésie française (3),
  Saint-Pierre-et-Miquelon (4). Lues aussi : les quatre listes des règlements (organismes de
  liaison, pays de l'Union, pays de l'Espace économique européen, personnes qui relèvent des
  règlements) ; les fenêtres « Année civile », « Dates d'application de l'accord sur l'Espace
  économique européen aux règlements 883/2004 et 987/2009 », « Etats tiers liés à la France et
  au Luxembourg », « Prestations de même nature ou de nature différente » ; les avis 181, 183 et
  237 ; le début de la lettre Cnav du 18 novembre 2009 (`LE_CN_18112009`, l'accord avec la Suisse
  et l'élargissement de l'Union) ; la première page de la décision n° 1/2012 du 31 mars 2012
  (`decision_cmeee_01_2012_31032012.pdf`, le PDF de la base). Chacun confronté aux fiches
  `totalisation_des_periodes_etrangeres`, `pension_proratisee` et
  `minimum_contributif_international`, qui citent déjà quatre de ces exposés (« Mode de calcul »,
  « Montant de la retraite communautaire », « Attributions successives », « Anciens
  règlements ») ; à `reversion`, `majoration_forfaitaire_reversion`, `minimum_vieillesse`,
  `residence_et_minimum_vieillesse` ; au tableau `legislation/accords_internationaux.yaml` ; aux
  régimes `cssm_mayotte`, `cafat_nouvelle_caledonie`, `cps_polynesie`,
  `cps_saint_pierre_et_miquelon` ; au code : la pension nationale liquidée sans les trimestres
  qu'un accord compare (`src/retraite_notionnelle/droit/liquidation.py:326`), comparée à la
  proratisée, chacune à son minimum (`droit/completer.py:1673`) ; la durée du taux, celle de
  toute la carrière, tous régimes de la carrière compris, plus les trimestres étrangers
  (`Durees.pour_le_taux`, `droit/compter.py:442`) ; la réversion, sur les pensions servies au
  défunt (`reversion`, `droit/reversion.py:1738`), sa part du minimum sur les durées françaises
  (`_part_du_minimum`, `droit/reversion.py:1547`) ; leurs jumeaux de `moteur/js/droit/`
  (`etranger.js`, `compter.js`, `liquider.js`, `completer.js`). Les textes, à l'index LEGI à
  jour au 2 novembre 2026 et JORF au 3 : décret n° 2005-1050, articles 11 à 15 et 19, et
  l'article 12 de sa rédaction du 1er avril 2022 (LEGIARTI000045183571), le même ; décret
  n° 2002-1371, article 1er (« Il prendra effet à compter du premier jour du mois suivant sa
  publication au Journal officiel », LEGIARTI000006215187, en vigueur le 22 novembre 2002) et
  son annexe, l'accord, articles 1er, 2, 7 à 10, 16, 28 et 49 (LEGIARTI000006780905) ; décret
  n° 2011-512, articles 1er, 2 et 13, et les rédactions de l'article 13 du 1er janvier et du
  1er août 2026 ; article L. 14 du code des pensions civiles et militaires de retraite
  (LEGIARTI000048844775).
- *Le rapprochement de l'index.* 20 exposés lient Légifrance 77 fois, sous 53 identifiants ;
  aucun ne lie EUR-Lex. 50 se trouvent à l'index, et chacun concorde avec son ancre par le
  numéro de l'article ou du texte, à deux réserves près (ci-dessous, « Ce que la base sert de
  travers »). Les six liens vers le texte du décret n° 2002-1371 (LEGITEXT000005633571) pour ses
  « art.7 », « art.9 », « art. 10 », « art. 28 », « art.16 », « art.2 » mènent à l'accord
  annexé, que LEGI porte en un seul article (« Annexe »), où chacun de ces articles se lit. Le
  décret n° 66-846 est au JORF (JORFTEXT000000335372), « Texte totalement abrogé », sans ses
  articles. 3 sont absents : les articles 2224 et 355 du code civil, hors du champ social de
  l'index, et l'article 48 de l'ordonnance n° 2002-411 (LEGIARTI000006698354), absent aussi par
  le numéro, quand son texte (LEGITEXT000005632514) et son article 5 y sont. Hors de Légifrance :
  le CLEISS (pages des organismes de liaison, formulaires) et ameli.fr, non lus.
- *Les sorts*, sous la convention de la note du premier thème. 39 exposés : 34 `limite` — ceux
  de la retraite personnelle aux trois fiches de la coordination ; ceux du champ d'application
  au tableau des accords et à la totalisation ; la conversion à la totalisation ; ceux de la
  réversion à `reversion` ; ceux de l'allocation de veuvage, de la pension de vieillesse de veuve
  ou de veuf et de la majoration pour tierce personne, que le modèle ne sert pas, à la limite
  (« avantages de survivant », et `docs/limites/ecarts-au-droit-positif.md`, « Restent dehors
  [...] la majoration pour tierce personne ») ; la majoration pour charge d'enfant à sa fiche ;
  l'allocation supplémentaire à `minimum_vieillesse` et `residence_et_minimum_vieillesse` ;
  chaque exposé d'outre-mer à la fiche de son régime, à la totalisation ou à `reversion` —, et
  à la limite neuve quand il dit ce que le modèle ne sert pas ; 5 `hors_modele`, l'instruction
  des demandes (règlements, et les quatre territoires), une procédure. 5 listes : celles de
  l'Union et de l'Espace économique européen `limite`, au tableau des accords et à la
  totalisation ; celle des personnes qui relèvent des règlements `limite`, à la totalisation et
  à la limite ; les deux listes des organismes de liaison, des règlements et des accords (que
  lient les exposés d'outre-mer), `hors_modele`. 4 fenêtres : « Année civile » `hors_modele`,
  définition du lexique ; les trois compléments `limite`. 3 avis `hors_modele` : l'accord sur
  l'Espace économique européen appliqué à la Croatie (183, 2014), le revenu annuel moyen de la
  retraite communautaire (237, 2021), le barème de conversion des monnaies (181, 2026), déjà
  rangé. Les objets d'autres thèmes que ces exposés lient restent tels : 10 exposés `limite` ou
  `recoupe`, et 3 encore `a_lire` (la liquidation unique, le paiement, les réfugiés et
  apatrides) ; 2 listes `limite` (régimes de base obligatoires, régimes spéciaux), sans
  extension ; 5 barèmes ; 4 fenêtres déjà rangées.
- *Les références*, toutes celles que lient les objets rangés ici, qui leur donnent leurs
  renvois. 77 `a_lire` sont rangées : 73 `limite`, dont les 9 que seule liait la liste des
  personnes qui relèvent des règlements (note 1 de la circulaire Cnav 2010/54, circulaires Cnav
  2003/27, 2011/62 et son annexe, le règlement n° 1231/2010, 2013/17, instruction ministérielle
  2012/2, lettre Cnav du 18 novembre 2009, décision n° 1/2012, article 2 du règlement
  n° 883/2004) ; 4 `hors_modele`, que seule lie l'instruction des demandes : la circulaire
  Cnav 2010/54 entière, ses notes 9 et 10, l'article 4 du règlement n° 987/2009. 26 déjà
  `limite` portaient les renvois ; 31 les étendent (ci-dessous).
- *Les renvois qui s'étendent* (31 références), chaque fois des fichiers nommés :
  `pension_proratisee` et `totalisation_des_periodes_etrangeres` : circulaires Cnav 2004/8,
  2012/17 ; avec `minimum_contributif_international` : 89/94, 2013/16, 20/94 (et
  `ecarts-au-droit-positif.md`), circulaire ministérielle 93/62 du 13 juillet 1993 (de même),
  instruction ministérielle 2002/5 (et le tableau des accords) ; avec la limite :
  circulaire Cnav 2014/64 ; `totalisation_des_periodes_etrangeres`, `minimum_contributif_international`
  et la limite : 2004/29 ; `minimum_contributif_international` et `pension_proratisee` :
  2005/30, 2009/17 ; `pension_proratisee` seule : 2005/17, 2018/4 ; `pension_proratisee`,
  `totalisation_des_periodes_etrangeres` et le tableau : règlement n° 1408/71 entier ;
  `totalisation_des_periodes_etrangeres` et le tableau : circulaire ministérielle 94/22,
  règlement n° 859/2003 ; `totalisation_des_periodes_etrangeres` seule : article 2 du
  règlement n° 1408/71 ; le tableau seul : circulaire Cnav 2012/44 ; la circulaire Cnav 2010/54,
  note 2 (totalisation, tableau, `ecarts-au-droit-positif.md`, `reversion`), note 3
  (totalisation, `majoration_forfaitaire_reversion`), note 4 (`pension_proratisee`,
  totalisation), note 6 (`pension_proratisee`, totalisation, tableau, `reversion`) ;
  `reversion` : circulaire Cnav 15/95 ; `majoration_forfaitaire_reversion` : circulaires Cnav
  2001/16, 2004/22, 44/94, lettre ministérielle du 26 février 1990, réponse à la question écrite
  du 21 octobre 1991 ; l'outre-mer : instruction ministérielle 2003/3 (`cafat_nouvelle_caledonie`,
  totalisation, `reversion`, tableau), circulaire Cnav 2016/7 (`cps_saint_pierre_et_miquelon`,
  totalisation, la limite, `reversion`, tableau), circulaire Cnav 2017/27 (les quatre régimes,
  totalisation, `pension_proratisee`, `minimum_contributif_international`).
- *Les limites* (`docs/limites/3-systeme-actuel.md`), neuves : « règlements européens », ce que
  le modèle ne sert pas des règlements ; « accords d'outre-mer », les trimestres des quatre
  territoires comptés à toute date et pour tout régime.

**Ce que la lecture a trouvé, sans écart.** La pension proratisée de l'exposé « Montant de la
retraite communautaire » est celle de `pension_proratisee` : « Retraite théorique x (Durée
d'assurance au régime général (sans AVS) ÷ Durée d'assurance de la retraite globale) », « Ces
durées sont limitées à la durée d'assurance maximum » ; le nombre d'années du salaire moyen
réduit avant le 1er juillet 2022, « Nombre d'années retenues x (Durée d'assurance au régime
général non limitée ÷ Durée d'assurance tous régimes) », et non réduit depuis, hors d'une
première retraite ou d'une retraite progressive d'avant (versions `reglement_883_2004` et
`salaire_moyen_lura_2022`). Le minimum, de même : « Minimum x (Durée totale d'assurance ÷ Durée
d'assurance maximum au régime général) », puis « Minimum x (Durée d'assurance au régime général
÷ Durée totale d'assurance non limitée) », et « Les périodes d'assurance, d'emploi ou de
résidence validées par un État membre sont retenues en tant que durée cotisée », ce que la
version `minimum_majore_2004` cite. La majoration pour enfants « comprise dans la comparaison » :
proportionnelle à chaque pension, elle ne change pas laquelle l'emporte. La réversion : « La
retraite de réversion nationale et la retraite de réversion proratisée sont comparées » ; la
proratisée vaut 54 % de la pension théorique au prorata de celle du défunt, son minimum entier
réduit à ses trimestres au régime général sur ceux de tous les États ; le modèle sert 54 % de la
pension servie au défunt — la plus élevée de ses deux —, son minimum réduit sur ses seules
durées françaises, ce qui donne le même montant hors des ressources et des règles de non-cumul, la part du
minimum de la nationale étant la plus grande des deux. Les dates d'application des règlements de
la liste de l'Espace économique européen, État par État (du 1er janvier 1959 au 1er juillet
2013, la fin au 1er janvier 2021 pour le Royaume-Uni), sont celles du tableau des accords pour
les 30 autres États ; la majoration de la réversion de 11,1 % est dans `reversion`, les âges de
l'enfant à charge dans `majoration_forfaitaire_reversion`. L'outre-mer : chaque décret réduit la
pension théorique « au prorata de la durée des périodes d'assurance et assimilées accomplies au
regard de la législation qu'elle applique, avant la réalisation du risque, par rapport à la
durée totale des périodes accomplies sous la législation des deux territoires », et « Cette
durée totale est plafonnée à la durée maximale éventuellement requise par la législation
qu'elle applique pour le bénéfice d'une prestation complète » (décret n° 2005-1050, article 12,
dans ses deux rédactions ; accord calédonien, article 7 ; décret n° 2011-512, article 13). La
pension théorique valant le salaire moyen au taux de toute la durée, multiplié par la durée
plafonnée sur la durée maximum, le prorata sur la même durée plafonnée la ramène à la durée du
régime général sur la durée maximum : ce que le modèle calcule en comptant les trimestres du
territoire dans la durée tous régimes ; et la pension nationale, à son taux de la seule durée
française, ne la dépasse pas. Le salaire moyen, sur les seuls salaires du régime général
(décret n° 2005-1050, article 15 : « les salaires ou les revenus constatés pendant les périodes
d'assurance accomplies sous la législation qu'elle applique »). Ce que d'autres ont déjà déclaré,
que ces exposés touchent : les règlements servis à qui n'est pas ressortissant d'un État membre
(lettre de la Cnav du 11 août 1987), que la liste des personnes qui relèvent des règlements et
les deux exposés du champ d'application disent aux ressortissants, réfugiés et apatrides ; la
règle d'une année, non servie (règlement n° 883/2004, article 57 ; règlement n° 1408/71,
article 48, que cite l'exposé du montant : « Si la période d'assurance dans un État est
inférieure à 1 an et ne permet pas l'attribution d'une retraite au titre de la législation
nationale de cet État, elle est retenue pour la retraite théorique par les autres États. Elle
est négligée pour le prorata temporis ») ; l'allocation supplémentaire dans un autre État de la
Communauté avant juin 1992 (point non tranché de G14) ; la conversion des périodes étrangères
par année civile, et non sur le relevé de l'autre institution (approximation de la
totalisation) ; un seul accord à la fois, quand l'exposé du montant totalise depuis le
1er septembre 2008 les périodes d'un État tiers lié à la France et au Luxembourg
(approximation de la totalisation) ; la réversion du régime général, ses ressources déclarées,
la pension de vieillesse de veuve ou de veuf (note du thème « Avantages liés au décès de
l'assuré ») ; le versement forfaitaire unique, que l'exposé des attributions successives dit
révisé (thème « Retraite personnelle de base ») ; l'âge de vingt et un ans de l'enfant qui a
interrompu ses études pour maladie (approximation de `majoration_forfaitaire_reversion`).

**Un point non tranché, aux sessions du modèle** (rien n'a été corrigé) : *les trimestres de
Polynésie française et de Saint-Pierre-et-Miquelon dans la décote d'un fonctionnaire.* La
coordination avec la Polynésie s'applique, pour la France, « aux régimes spéciaux sauf les
régimes des fonctionnaires de l'État, magistrats, militaires, fonctionnaires territoriaux et
hospitaliers, ouvriers des établissements industriels de l'État » (exposé « Champ d'application
- Polynésie française », décret n° 94-1146, article 2) ; celle de Saint-Pierre-et-Miquelon ne
vise ces fonctionnaires et ouvriers de l'État que pour « les prestations en nature des
assurances maladie et maternité » (décret n° 2011-512, article 2, II) — « Sont exclus », parmi les régimes français, « les
fonctionnaires civils et militaires de l'État, magistrats de l'ordre judiciaire, les
fonctionnaires relevant de la caisse nationale de retraite des agents des collectivités
locales (CNRACL) et les ouvriers de l'État » (exposé « Champ d'application - Saint-Pierre et
Miquelon »). Le modèle compte les trimestres de ces régimes dans la durée que lit le taux de
tout régime (`Durees.pour_le_taux`, `droit/compter.py:442`), celui du fonctionnaire compris.
Les deux lectures : le code des pensions compte « la durée d'assurance et des périodes reconnues
équivalentes validées dans un ou plusieurs autres régimes de retraite de base obligatoires »
(L. 14, I), dont la caisse de prévoyance sociale de Polynésie ou de Saint-Pierre-et-Miquelon
peut être, et le modèle a raison ; la coordination, qui fait seule compter les périodes d'un
territoire dans l'autre, en exclut ces régimes, et leurs trimestres n'y comptent pas. *Cas
posé* : fonctionnaire de l'État né en 1960, 120 trimestres de services et 40 à la caisse de
Polynésie, parti à soixante-deux ans en 2022 sur un traitement indiciaire de 30 000 € par an ;
durée requise, 167 trimestres ; âge d'annulation de la décote, soixante-sept ans. Pension
avant décote : 30 000 × 75 % × 120 / 167 = 16 167,66 €. Avec les trimestres de Polynésie (160) :
décote de min(167 − 160, (67 − 62) × 4) = 7 trimestres, 8,75 %, pension de 14 752,99 € ; sans
eux (120) : min(47, 20) = 20 trimestres, 25 %, pension de 12 125,75 € ; soit 14 752,99 − 12 125,75 = 2 627,24 € par an
d'écart. Aucun texte lu ne tranche si ces caisses sont des « régimes de retraite de base
obligatoires » au sens de L. 14.

**Ce que la base sert de travers.** L'exposé « Calcul de la retraite personnelle -
Nouvelle-Calédonie » date l'ancien calcul « Avant le 01/12/2012 », quand l'accord qui le
remplace « prendra effet à compter du premier jour du mois suivant sa publication » (décret
n° 2002-1371, article 1er, en vigueur le 22 novembre 2002), le 1er décembre 2002, que dit
l'exposé du champ d'application (« a pris effet le 01/12/2002 ») ; le même exposé lie
« Décret 66/846 du 14/11/1966 art. 6, art 9 », et « art 9 » mène au décret n° 2002-1371 ; le
« art.1 » du décret n° 2002-1371 de l'exposé du champ d'application calédonien, qui vise
l'accord (« Article 1er Champ d'application territorial et personnel »), mène à l'article 1er
du décret, qui l'approuve. La liste des personnes qui relèvent des règlements range sous
« Accord CE/Suisse » la « Décision 1/2012 », que la base titre « Décision du Comité mixte de
l'EEE n° 1/2012 du 31/03/2012 », quand son PDF est la « DÉCISION No 1/2012 DU COMITÉ MIXTE
INSTITUÉ PAR L'ACCORD ENTRE LA COMMUNAUTÉ EUROPÉENNE ET SES ÉTATS MEMBRES, D'UNE PART, ET LA
CONFÉDÉRATION SUISSE ». Deux exposés de la réversion citent la « Circulaire Cnav 2010/54 du
31/05/2010 », au lien de celle du 21 mai 2010 ; « Règles de non cumul - règlements européens »,
la « Circulaire Cnav 2005/17 du 11/04/2004 », au lien de celle du 11 avril 2005 ; le « § 1411 »
et le « § 1412 » de la « Circulaire Cnav 2006/38 du 08/06/2006 » mènent à la circulaire Cnav
2006/37 du même jour ; « Circulaire ministérielle 20/94 du 31/01/1994 », dans l'exposé de la
majoration pour tierce personne, mène à la circulaire Cnav 20/94. La fenêtre des États tiers
liés à la France et au Luxembourg écrit « Boznie-Herzégovine ». L'exposé du calcul de la
retraite à Saint-Pierre-et-Miquelon, du 24 octobre 2025, ne porte pas les deux rédactions de
l'article 13 du décret n° 2011-512 de 2026 : les majorations de durée pour enfant d'un
territoire comptées dans l'autre pour la surcote (1er janvier), puis aussi pour les meilleures
années et la carrière longue (1er septembre, décret n° 2026-700, article 5).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et les
deux limites neuves. Les références prennent les renvois des objets rangés ici qui les lient,
sans ceux des barèmes, des avis, ni des fiches qui les citent par leur numéro. Les circulaires
et les règlements que lient ces exposés ne sont pas relus en entier ; le décret n° 66-846, que
le JORF de l'index porte sans ses articles, n'est pas lu, ni ce qui faisait compter, avant
chaque coordination, les périodes des territoires ; ni les deux rédactions de 2026 de l'article
13 du décret n° 2011-512, ni ce que l'article 12 du décret n° 2005-1050 change au 1er avril
2022 hors du renvoi au code, ne sont confrontés au modèle. La différence de calcul entre les
règlements n° 1408/71 et n° 883/2004 pour les États de l'Espace économique européen et la
Suisse, du 1er mai 2010 à leur passage au second, n'est pas lue : le modèle leur applique les
règles de sa version `reglement_883_2004`.
