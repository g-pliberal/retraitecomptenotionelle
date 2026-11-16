# Étape 6, circulaires de 2012 : les 37 références sans thème de la dix-neuvième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2012 : 37, comme la note de 2011 les
  comptait. Toutes sont de 2012.
- *La lecture* : les 37, relues par l'API le 16 novembre 2026 vers 13 h 40 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 17 en page,
  par le HTML du champ `contenu`, 20 en PDF lus au site (`/Pdf/<nom>`) par leur texte
  (`pdftotext -layout`). Deux PDF sont des scans, lus à l'image, sans citation
  vérifiable : la circulaire interministérielle du 28 mars 2012 jointe à la n° 2012/35,
  et l'annexe de la lettre Cnav du 6 septembre 2012. 16 circulaires de la Cnav et 9 de
  leurs pièces, une lettre de la Cnav, une note d'information ; 2 circulaires et 2
  lettres ministérielles ; 6 circulaires du RSI.
- *Qui a lu* : la session elle-même, sans agent, chaque texte en entier. Les 63
  citations relevées ont été retrouvées mot pour mot, par script, dans le texte servi
  (blancs normalisés), chaque raison hors modèle dans le registre, chaque renvoi dans le
  dépôt. La session a relu le code et les fiches qui décident des écarts (plus bas).
- *Les sorts* : 37 références rangées, 21 `limite`, 16 `hors_modele` ; le registre seul
  a changé (`data/reference/legislation/cnav/references.csv`, 37 lignes, les colonnes
  `sort` et `renvoi` seules, écrites et vérifiées par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : le salaire qui valide un trimestre, « 1 844,00 euros » (n° 2012/3) ;
  les plafonds de la réversion au 1er janvier 2012 (n° 2012/4) ; les rentes ouvrières et
  paysannes (n° 2012/12) ; le barème des versements pour la retraite (n° 2012/11, son
  barème, circulaire RSI n° 2012/005) et celui des rachats déposés en 2011 et 2012
  (n° 2012/81, deux annexes) ; le cumul emploi-retraite après le relèvement des âges
  (n° 2012/27) ; la revalorisation du 1er avril 2012 et l'ASPA à 777,16 € (circulaire
  interministérielle jointe à la n° 2012/35) ; les plafonds opposables aux veuves de
  guerre (n° 2012/36) ; le passage de l'allocation des travailleurs de l'amiante à la
  retraite (n° 2012/42) ; les indemnités journalières de maternité au salaire annuel de
  base, à 125 % (n° 2012/59), et celles du congé lié au distilbène (lettre ministérielle
  du 22 mai) ; les conditions de la carrière longue au 1er novembre 2012 (n° 2012/60,
  annexe 2) ; les taux d'incapacité de la pénibilité (n° 2012/63, annexe 1) ; la qualité
  d'assuré social des périodes assimilées (lettre Cnav du 26 septembre) ; les règlements
  européens appliqués à la Suisse au 1er avril 2012 (circulaire DSS/DACI n° 2012/207) ;
  au RSI, la réversion après la réforme de 2010 (n° 2012/008), la fin du minimum de
  réversion d'une pension servie en versement forfaitaire unique (n° 2012/016), la
  résidence de l'ASPA à Saint-Barthélemy et Saint-Martin (n° 2012/017), l'allocation
  personnalisée d'autonomie hors des ressources (n° 2012/019).
- *Hors modèle* : les monnaies (4 : les taux de change des quatre trimestres) ; une aide
  à l'insertion (3 : le RSTA deux fois, l'allocation de retour à l'activité) ; la demande
  de retraite (3 : la demande unique des assurés de la Cavimac, le tableau de procédure
  de la pénibilité, les attestations de reconnaissance de travailleur handicapé jointes à
  la lettre Cnav du 6 septembre) ; la retenue à la source (2 : la n° 2012/58 et sa liste
  des conventions fiscales) ; une chacune, l'organisation des caisses (la rémunération
  des médecins de la commission de la pénibilité, n° 2012/33), la tenue du relevé de
  carrière (le report des contrats d'apprentissage, note d'information n° 2012/11),
  l'indemnité de départ des commerçants et artisans (RSI n° 2012/009), l'assiette des
  cotisations (les sommes versées par un tiers à l'employeur, circulaire DSS/5B
  n° 2012/56).

**Les montants relus, conformes.** Le SMIC de 9,22 € au 1er janvier 2012
(`data/reference/macro/smic_horaire.csv`, ligne 84) et de 9,40 € au 1er juillet
(`smic_horaire_releves.csv`, ligne 80) ; le plafond de 36 372 € (`plafond_securite_sociale.csv`,
ligne 139) ; les plafonds de la réversion, 2 080 fois le SMIC et 1,6 fois ce montant, que
`reversion.yaml` calcule (lignes 101 et 117) ; le minimum de réversion de 3 359,40 €
(`minimum_reversion.csv`, ligne 103) ; la revalorisation de 1,021 au 1er avril 2012
(`revalorisation_pensions.csv`, ligne 115) ; l'ASPA à 9 325,98 € par an
(`minimum_vieillesse.csv`, ligne 84) ; les âges et durées de la carrière longue au
1er novembre 2012 (`carriere_longue.csv`, lignes 155 à 170) ; l'âge de la majoration de
réversion, celui du taux plein du survivant (`droit/reversion.py`, ligne 1716), l'âge
limite de la majoration pour enfant (`majoration_forfaitaire_reversion.yaml`, ligne 151) et
celui de la dernière révision des ressources (`reversion.yaml`, ligne 682). Sans série au
dépôt : les taux de change, le RSTA, l'allocation de retour à l'activité, les rentes
ouvrières et paysannes, les barèmes des versements et des rachats, la retenue à la
source, les plafonds des veuves de guerre.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *La qualité d'assuré social des périodes assimilées.* Lettre Cnav du 26 septembre
  2012 (annulée et remplacée par la lettre du 5 décembre 2013, encore à lire) : « La
  condition d'assujettissement préalable est remplie dès lors qu'un versement de
  cotisation, si minime soit-il, est intervenu avant la période à valider », et une
  activité non salariée entre la dernière cotisation et la période assimilée fait perdre
  cette qualité, sauf affiliation postérieure au début du chômage indemnisé. Le modèle
  valide les années sans emploi que la saisie déclare (`docs/limites/3-systeme-actuel.md`,
  lignes 356 à 374) sans rien exiger avant elles : ni le moteur ni une fiche ne nomment
  la condition. Effet attendu étroit : la période assimilée qui ouvre une carrière, ou
  qui suit une activité indépendante.

**Candidats d'avant, que 2012 confirme ou précise.**

- *La génération de la réversion d'un assuré mort avant son départ* (note de 2011). La
  circulaire RSI n° 2012/008 en donne la règle entière depuis le 1er juillet 2011 :
  « l’application des dispositions opposables aux personnes atteignant leur 57 »e
  anniversaire « l’année du décès de l’assuré », sauf si celles de la génération du
  défunt sont connues ; et « C’est bien à la date d’effet de la pension de réversion que
  l’on détermine si la durée de référence opposable à » sa génération est connue, avec
  trois tableaux (annexe 1). Le modèle, qui prend toujours la génération du défunt
  (`reversion.yaml`, lignes 1158 à 1166), ne s'en écarte donc que pour le défunt dont le
  décret de génération n'était pas paru : né en 1965 et mort en 2011, la caisse prend
  165 trimestres et vingt-cinq années, ceux des nés de 1954. La même circulaire dit que
  les caisses, « à l’instar du Régime Général », furent « autorisées à appliquer »
  « l’ancienne réglementation » des soixante ans tant que leurs outils n'étaient pas
  prêts : la pratique a pu suivre l'ancienne règle quelque temps.
- *Le cumul des retraités anticipés d'avant le 1er juillet 2011* (note de 2011) : la
  n° 2012/27, point 33, le redit dans les mêmes mots que la n° 2011/61, et ajoute « Il
  convient de retenir les âges en vigueur à la date d’effet de la retraite anticipée,
  c’est-à-dire 60 ans (âge légal) ou 65 ans (âge d’obtention du taux plein) ».

**Écarts relevés, déjà déclarés.** Les indemnités journalières de maternité, que le
modèle ne porte pas au salaire annuel moyen (`salaire_annuel_moyen.yaml`, lignes 227 à
231) ; le minimum de réversion d'une pension sous le seuil du versement forfaitaire unique
(`reversion.yaml`, lignes 1035 à 1041) ; la pénibilité et l'allocation des travailleurs
de l'amiante (`3-systeme-actuel.md`) ; la résidence de l'ASPA
(`residence_et_minimum_vieillesse.yaml`).

**Points non tranchés.**

- *Les sorts retenus*, quand l'autre se défendrait. En `limite` : les plafonds des veuves
  de guerre (avec la fiche du minimum vieillesse et la limite de la majoration de
  L. 814-2), le passage de la Suisse aux règlements de 2004, que le modèle ne distingue
  pas des anciens. En `hors_modele` : les attestations de reconnaissance de travailleur
  handicapé, formulaires comme celles de la n° 2011/21, quand la lettre qu'elles
  illustrent est en `limite` ; la rémunération des médecins de la commission de la
  pénibilité, rangée avec l'organisation des caisses.
- *Le RSI hors de R. 353-3* : la n° 2012/008 note que R. 634-5, qui gardait au RSI la
  génération des soixante ans « jusqu'au 31 décembre 2012 », n'a pas été modifié, le
  ministère demandant d'appliquer R. 353-3 ; à relire au texte avec l'écart.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2012/42 (par la 2012/68), la n° 2012/59 (2015/16),
  la lettre Cnav du 26 septembre (lettre du 5 décembre 2013).
- Des erreurs : l'âge légal « qui varie entre 65 et 67 ans » pour 60 et 62, la « loi
  2011-1906 du 31 mai 2011 » pour le 21 décembre et le « décret du 30 mai 2011 » pour le
  31 (RSI n° 2012/008) ; l'article L. 351-3 pour L. 353-1 (RSI n° 2012/016) ; la « loi
  n° 2011-1330 » pour 2010-1330 (n° 2012/27, point 51) ; un exemple de rachat demandé en
  2014 au barème de 2012, arrondi « à l'euro inférieur » quand la règle dit au plus
  proche (RSI n° 2012/005) ; des coquilles (« 201 0 », « domicilées », « Mesdameset »).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Ni L. 351-3 ni R. 634-5 n'ont été
relus au Journal officiel ; les moteurs n'ont tourné sur aucun cas.
