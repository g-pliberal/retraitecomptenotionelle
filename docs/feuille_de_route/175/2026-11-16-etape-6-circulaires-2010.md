# Étape 6, circulaires de 2010 : les 66 références sans thème de la dix-septième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2010 : 66, comme la note de 2009 les
  comptait. Deux n'en sont pas, que le registre date mal : la circulaire ministérielle
  n° 2009/191, du 3 juillet 2009, datée du 4 janvier 2010, sa date d'application ; la
  lettre ministérielle du 28 mars 2011, datée du 4 octobre 2010. Elles sont lues ici.
- *La lecture* : les 66, relues par l'API le 16 novembre 2026 vers 13 h UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 37 en page,
  29 en PDF lus au site (`/Pdf/<nom>`) par leur texte (`pdftotext -layout`), aucun scan.
  29 circulaires de la Cnav et 20 de leurs pièces (dont 13 schémas et la note technique 8
  de la n° 2010/54) ; 2 circulaires ministérielles, 7 lettres ministérielles, 2 diffusions
  d'instructions ministérielles ; 6 circulaires du RSI.
- *Qui a lu* : les 66 en entier, par quatre agents de la session sur Opus, un lot par
  origine (les circulaires de la Cnav ; leurs pièces ; les textes ministériels ; le RSI),
  lancés ensemble, sur une consigne commune (les raisons du registre et les renvois déjà
  employés, avec leur effectif ; les rangements de 2006 à 2009 pour précédents ; les notes
  de 2008 et 2009). Les 204 citations ont été retrouvées mot pour mot, par script, dans le
  texte servi (blancs normalisés), chaque raison hors modèle dans le registre, chaque
  renvoi dans le dépôt. La session a relu elle-même les passages et la fiche qui décident
  de l'écart neuf et des points ouverts (plus bas).
- *Les sorts* : 66 références rangées, 38 `limite`, 28 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 66 lignes, les colonnes
  `sort` et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : les rentes ouvrières et paysannes de 2010 et 2011 (n° 2010/1 et
  2010/89) ; la retraite progressive à 150 trimestres prorogée jusqu'à la fin de 2010
  (n° 2010/4) ; le rétablissement des militaires, ses adresses (n° 2010/18, 2010/31,
  2010/71) ; les régimes étrangers équivalents de R. 173-4-3 (n° 2010/30) et le champ des
  règlements (son annexe 1, servie deux fois) ; la résidence pour l'ASPA, 180 jours ou le
  foyer permanent (n° 2010/49) ; le barème des rachats (n° 2010/52) et celui des
  versements pour la retraite (annexes de la n° 2010/25) ; les entretiens
  franco-allemands (n° 2010/53) ; la polygamie en Algérie (n° 2010/65) ; le congé de
  mobilité (n° 2010/82) ; les schémas de liquidation sous les règlements, du minimum, de
  la réversion, du veuvage, de la tierce personne, et la cotisation maladie des
  pensionnés (n° 2010/54, 13 pièces), comme leurs notes mères ; les périodes des
  organisations internationales (circulaire DSS/DACI n° 2010/85) ; le volontariat
  associatif à 50 % du plafond trimestriel (lettre du 5 février) ; la maladie et
  l'invalidité des maîtres du privé (lettre du 19 avril) ; la revalorisation de 0,9 % et
  l'ASPA à 708,95 € (lettre du 24 mars) ; l'enfant né sans vie (lettre du 28 mars 2011) ;
  les arriérés d'apprentissage d'avant 1972 (lettre du 30 décembre) ; au RSI, le
  micro-social des départements d'outre-mer (n° 2010/003), le RSA hors des ressources
  (n° 2010/005), la suspension du cumul plafonné bornée aux mois d'activité (n° 2010/013),
  le plan d'apurement des dettes d'outre-mer (n° 2010/014), la majoration de réversion de
  11,1 % (n° 2010/016).
- *Hors modèle* : les monnaies (6) ; l'application administrative d'une convention
  bilatérale (5 : la Croatie, le Japon, les accords, le Maroc, la lettre de la caisse
  algérienne) ; l'instruction coordonnée (3 : la Pologne, la Bulgarie et sa déclaration) ;
  les institutions de la coordination (2 : le Danemark, la Suède) ; une aide à
  l'insertion (2 : l'allocation de retour à l'activité, le RSTA) ; la retenue à la source
  (2 : la n° 2010/50 et sa liste des conventions fiscales) ; l'organisation des caisses
  (2 : la mission nationale de contrôle, au ministère et au RSI) ; une règle de procédure
  (2 : la contrainte, la question prioritaire de constitutionnalité) ; une procédure de
  demande (2 : le formulaire des organisations internationales, le schéma de la note
  technique 9) ; une chacune, le remboursement entre institutions (l'Autriche),
  l'assurance maladie (la diffusion n° 2010/3), la prime exceptionnelle de 100 € des
  Antilles.

**Les montants relus, conformes.** Le SMIC de 8,86 € (`smic_horaire.csv`, ligne 82) ; les
plafonds de 2004, 2005, 2007 et 2010 (`plafond_securite_sociale.csv`, lignes 131 à 137) ;
la revalorisation de 1,009 au 1er avril 2010 (`revalorisation_pensions.csv`, ligne 113) et
celle des salaires portés au compte ; l'ASPA à 708,95 € par mois (`minimum_vieillesse.csv`,
ligne 82) ; la réversion à 54 %, sa majoration de 11,1 % sous 800 € par mois
(`plafond_majoration_reversion.csv`, ligne 11), son plafond de 18 428,80 € ; la
cotisation maladie des non-résidents, 3,2 % ; les 150 trimestres de la retraite
progressive ; les 90 jours par trimestre et les quatre trimestres par an des
organisations internationales (`totalisation_des_periodes_etrangeres.yaml`, lignes 167 à
171) ; les dates d'entrée dans les règlements de la Bulgarie, de la Roumanie, de la Suisse
et des dix États de 2004 (`accords_internationaux.yaml`). Sans série au dépôt : les rentes
ouvrières et paysannes, le RMI et l'allocation de retour à l'activité, le RSTA, la retenue
à la source, les barèmes des rachats et des versements, les taux du micro-social de 2010.

**Un écart neuf** (candidat), étroit, pour les sessions du modèle, sans y toucher.

- *L'abandon de cotisations des indépendants d'outre-mer, qui minore leurs droits.*
  Circulaire RSI n° 2010/014 : l'article 32 de la loi n° 2009-594 ouvre aux indépendants
  des départements d'outre-mer, pour leurs dettes d'avant le 1er avril 2009, un plan
  d'apurement qui « peut prévoir un abandon partiel des créances constatées au 31 décembre
  2008 dans la limite de 50% », et « les droits aux prestations de retraite seront minorés
  dans les mêmes proportions ». Le modèle tient les cotisations pour versées
  (`cotisation_vieillesse_independants.yaml`, lignes 172 et 173) ; la limite des
  indépendants des départements d'outre-mer (`docs/limites/3-systeme-actuel.md`, lignes
  190 à 196) dit la cotisation impayée, non cet abandon, que rien au dépôt ne nomme.

**Candidats d'avant, que 2010 confirme.**

- *Le cumul propre aux pensionnés pour inaptitude, abrogé au 1er janvier 2009* : la
  circulaire RSI n° 2010/013 le dit ; relevé par les notes de 2003 et des écarts lourds
  (ligne 131), il n'est déclaré dans aucune fiche.

**Écarts relevés, déjà déclarés.** La majoration de 11,1 % d'une réversion d'effet
antérieur à 2010 et la subsidiarité (`reversion.yaml`, lignes 1052 à 1058) ; le foyer
permanent et la suppression rétroactive de l'ASPA (`residence_et_minimum_vieillesse.yaml`,
lignes 96 à 104) ; la polygamie en Algérie, la réversion proratisée sans clause de
réduction, le veuvage, la tierce personne, l'assurance volontaire superposée, la
liquidation qui se répète et le cas de trois États sous les règlements, le congé de
mobilité, la maladie et l'invalidité validées par jours (`3-systeme-actuel.md`) ; le
volontariat associatif (`service_civique.yaml`, lignes 182 à 186) ; la suspension des
revenus de 2004 à 2007 et les jours des commerçants
(`cumul_emploi_retraite_et_retraite_progressive.yaml`, lignes 367 à 378).

**Points non tranchés.**

- *La surcote des trimestres des organisations internationales.* La circulaire
  ministérielle n° 2010/85 dit que ces trimestres « peuvent également permettre
  l'amélioration de la surcote » ; la circulaire Cnav n° 2010/42, que suit
  `totalisation_des_periodes_etrangeres.yaml` (lignes 158 à 166), les réserve au taux et
  les exclut de toute autre durée. Les deux textes se contredisent ; la fiche suit la
  caisse, ce que le scénario 1 demande, sans le dire.
- *L'enfant né sans vie.* La lettre du 28 mars 2011 ouvre la majoration de pension et la
  majoration de durée d'assurance sur un acte d'enfant sans vie. Aucune fiche ne dit si la
  saisie doit déclarer un tel enfant ; à trancher par les sessions du site.
- *Les sorts retenus*, quand l'autre se défendrait. En `limite` : les rentes ouvrières et
  paysannes, les adresses des militaires, les entretiens franco-allemands, la polygamie,
  le barème des rachats, le micro-social d'outre-mer, le RSA, le plan d'apurement, sur
  leurs précédents ; le veuvage et la tierce personne de la n° 2010/54, sur leurs notes
  mères. En `hors_modele` : l'annexe 1 de la n° 2010/42, un formulaire, quand sa
  circulaire est en `limite` ; la liste des accords de la n° 2010/70.

**Ce que la base sert de travers.**

- Des dates : les deux textes d'une autre année (plus haut) ; les n° 2010/36 et 2010/37
  datées de janvier pour avril ; les PDF RSI nommés « 08012003 » et « 19012009 » pour
  2010 ; la n° 2010/1 qui se date de 2009 ; l'annexe 2 de la n° 2010/30 dite modifiée par
  une n° 2012/26 « du 14/02/2012 », du 14 mars selon `pension_proratisee.yaml`.
- Des mentions d'annulation : la n° 2010/18 par la n° 2010/31, elle-même par la
  n° 2010/71 ; la n° 2010/49 par la n° 2018/6 ; la n° 2010/52 par la n° 2010/56 ; la
  n° 2010/82 par la n° 2022/14 ; la n° 2010/50 annule la n° 2009/21. La lettre du
  5 février dit fausse la n° 2008/52, rangée sans le dire.
- Des doublons et des pièces séparées : l'annexe 1 de la n° 2010/30 servie sous deux
  noms ; les pièces des n° 2010/25, 2010/32, 2010/35, 2010/42 et 2010/50 rangées sans leur
  circulaire ou après elle ; des schémas de réversion sous les notes 3 et 4 ; les titres
  « note technique 228, 268, 269 » pour les points 28, 68 et 69 de la note 2.
- Des annexes annoncées et non servies : celles des n° 2010/30, 2010/35, de la
  n° 2009/191, des diffusions n° 2010/3 et 2010/4, de la lettre du 16 avril, de la
  n° 2010/016 du RSI (annexes 4 et 9), de la n° 2010/014 (courriers vides).
- Des erreurs : des calculs faux dans les n° 2010/50 et 2010/013 du RSI ; la date d'effet
  de la majoration de réversion rapportée à R. 351-12 pour R. 353-13 ; la loi
  « n° 2009-1654 » pour la n° 2009-594 ; le « décret n° 2008-800 du 9 janvier 2008 » ; le
  décret mongol de 1993 daté de 1998, reconduit de 2009 ; l'OCDE nommée « Organisation
  européenne de coopération économique ».

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Ni l'article 32 de la loi
n° 2009-594, ni R. 352-2, ni L. 161-19-1 n'ont été relus au Journal officiel ; les moteurs
n'ont tourné sur aucun cas.
