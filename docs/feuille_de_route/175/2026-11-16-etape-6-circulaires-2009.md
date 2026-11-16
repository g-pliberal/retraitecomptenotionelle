# Étape 6, circulaires de 2009 : les 65 références sans thème de la seizième période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées ; la quatrième, les
circulaires, lettres et instructions sans thème, l'est de 1936 à 2009 (cette note et celles
des périodes d'avant). Une seconde lecture avance à rebours depuis 2026, avec son propre
bloc (note de 2026 à rebours). Restent 371 circulaires, de 2010 à 2025 ; la lecture dans
l'ordre reprend à 2010 (66), puis 2011 (68), 2012 (37), 2013 (44), et s'arrête où elle
rejoint l'autre. Viennent ensuite, une session par nature : les 96 autres textes, les 74
que la base nomme sans les servir, les 107 accords. Méthode : la base relue par l'API
(`_reference` de `cnav_legislation.py`), les pièces PDF lues au site sous `/Pdf/<nom>`,
chaque texte lu en entier, chaque citation vérifiée par script. 2009 n'a qu'un
écart neuf, étroit : l'artisan pensionné pour incapacité à son seul métier, que le
modèle présume inapte (ici).

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2009 : 65, comme la note de 2008 les
  comptait.
- *La lecture* : les 65, relues par l'API le 16 novembre 2026 vers 12 h 40 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 49 en page,
  16 en PDF lus au site (`/Pdf/<nom>`) par leur texte (`pdftotext`). Un PDF est un scan,
  lu à l'image, sans citation vérifiable : l'annexe de la circulaire Cnav n° 2009/64
  (9 pages). 30 circulaires de la Cnav et 5 de leurs pièces ; 7 circulaires
  ministérielles et 5 pièces ; 7 lettres ministérielles ou de la Cnav et un tableau de
  la Cnav titré lettre ; 5 diffusions d'instructions ministérielles ; 5 circulaires du
  RSI.
- *Qui a lu* : les 65 en entier, par quatre agents de la session sur Opus, un lot par
  origine (la Cnav ; les circulaires ministérielles ; les lettres, les diffusions et la
  circulaire n° 2009/278 ; le RSI), lancés ensemble, sur une consigne commune (les
  raisons du registre et les renvois déjà employés, avec leur effectif ; les rangements
  de 2006 à 2008 pour précédents ; les notes de 2007 et 2008). Les 144 citations ont été
  retrouvées mot pour mot, par script, dans le texte servi (blancs normalisés), chaque
  raison hors modèle dans le registre, chaque renvoi dans le dépôt. La session a relu
  elle-même les passages et le code qui décident des écarts (plus bas).
- *Les sorts* : 65 références rangées, 31 `limite`, 34 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 65 lignes, les colonnes
  `sort` et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : la surcote de 1,25 % par trimestre cotisé depuis 2009, aux pensions
  prenant effet depuis le 1er avril (n° 2009/10) ; la revalorisation portée au 1er avril
  (n° 2009/45) ; le trimestre de 2010, 1 772 € (n° 2009/83) ; le minimum contributif
  majoré réservé à 120 trimestres cotisés et la majoration des handicapés hors du minimum
  depuis le 1er avril 2009 (circulaire RSI n° 2009/031) ; le cumul emploi-retraite
  libéralisé (circulaire interministérielle n° 2009/45) ; la retraite progressive prorogée
  jusqu'à la fin de 2009 (n° 2009/7) ; les plafonds de la réversion de 2009 et de 2010
  (n° 2009/2 et 2009/84), son contrôle (n° 2009/39), sa majoration de 11,1 % au
  1er janvier 2010 (n° 2009/82, lettres ministérielles du 17 juin et du 18 décembre) ; la
  polygamie en Algérie (n° 2009/80) ; les versements pour la retraite — hors de la
  carrière longue (n° 2009/27), leur coût (annexes de la n° 2009/12), leur âge limite
  après une retraite progressive (lettre Cnav du 15 mai) — ; les arriérés régularisés sur
  attestation sur l'honneur, quatre trimestres au plus (circulaire n° 2009/278, diffusion
  n° 2009/3) ; le rétablissement des militaires (n° 2009/50 et 2009/58) ; les rentes
  ouvrières et paysannes (n° 2009/3) ; le chômage en France après un travail dans un autre
  État membre (n° 2009/77 ministérielle) ; les États tiers de la convention
  franco-luxembourgeoise (lettre du 25 septembre, diffusion n° 2009/4) et le champ des
  règlements (tableau du 18 novembre) ; le RSA hors des ressources (diffusion n° 2009/5) ;
  la CSG d'un retraité couvert par une organisation internationale (lettre Cnav du
  30 juin) ; au RSI, le tutorat sans prime de transmission (n° 2009/017), l'assiette des
  stagiaires, 1,46 € l'heure (n° 2009/027), la présomption d'inaptitude (n° 2009/032),
  l'ACCRE au micro-social (n° 2009/038).
- *Hors modèle* : les monnaies (8) ; la fraude (5 : la circulaire du 6 mai, ses trois
  annexes, sa diffusion) ; l'application administrative d'une convention bilatérale (4 :
  le Maroc, deux fois, le Chili, les États-Unis) et la Côte d'Ivoire (lettre Cnav du
  29 avril), soit 5 ; la retenue à la source (2) ; les institutions de la coordination
  (2 : le Luxembourg, le Portugal) ; l'activité économique réduite à fin d'insertion (2 :
  la n° 2009/144 et son PDF) ; l'assiette des cotisations (2 : les heures
  supplémentaires, lettre du 23 février et sa diffusion) ; la demande ou le paiement d'un
  versement (2 : les formulaires des n° 2009/71 et 2009/278) ; une chacune, l'instruction
  coordonnée (la Pologne), le RMI et l'allocation de retour à l'activité, le RSTA, le
  paiement aux héritiers, la caisse compétente pour la réversion (l'avenant de la
  n° 2009/64), l'exonération des porteurs de presse.

**Les montants relus, conformes.** Le SMIC de 8,71 € et de 8,86 € ; le trimestre de 2009,
1 742 €, et de 2010, 1 772 € ; les plafonds de la réversion (2 080 heures de SMIC) ; la
surcote de 1,25 % ; la majoration de réversion de 11,1 % sous 2 400 € par trimestre
(`plafond_majoration_reversion.csv`, ligne 11) ; les durées requises de 160 à 164 ; la
revalorisation au 1er avril ; au minimum contributif, les 120 trimestres, la
revalorisation de 1 % ; les dates d'entrée de la Bulgarie, de la Roumanie et de la Suisse
dans les règlements (`accords_internationaux.yaml`, lignes 152, 296 et 328). À un ou deux
centimes près : le minimum contributif au 1er avril 2009, 7 084,02 € et 7 740,88 € dans la
circulaire RSI n° 2009/031, 7 084,00 € et 7 740,87 € dans
`data/reference/legislation/minimum_contributif.csv` (lignes 92 et 115), et de même au
1er septembre 2008 ; la circulaire les calcule par revalorisation du montant d'avant, non
tranché. Sans série au dépôt : le RMI, les rentes ouvrières et paysannes, la base
mensuelle des allocations familiales de 2009, le SMIC au 1er juillet, l'assiette des
stagiaires, les taux du micro-social et de l'ACCRE, la retenue à la source, les frais
d'obsèques.

**Un écart neuf** (candidat), étroit, pour les sessions du modèle, sans y toucher.

- *L'artisan pensionné pour incapacité à son seul métier, présumé inapte par le modèle.*
  Circulaire RSI n° 2009/032 : la substitution d'office « ne joue que dans le cas de la
  pension pour l'invalidité totale et définitive », et « Si la pension en service est une
  pension pour incapacité au métier, la reconnaissance de l'inaptitude sur le plan médical
  doit avoir lieu dans les conditions habituelles. » Le code
  (`src/retraite_notionnelle/droit/invalidite.py`, lignes 106 à 115, `reconnu_inapte`)
  tient pour inapte quiconque déclare une pension d'invalidité, sans en lire le régime ni
  la nature. Ni `inaptitude_au_travail.yaml` (écarts, lignes 202 à 215) ni
  `pension_d_invalidite_substituee.yaml` ne le déclarent ; la distinction n'est lue que
  par `points_invalidite_independants.yaml`, pour les points.

**Candidats d'avant, que 2009 confirme ou date.**

- *La majoration des handicapés hors du minimum contributif depuis le 1er avril 2009
  seulement* : avant, elle « était calculée avant application » du minimum (circulaire
  RSI n° 2009/031) ; le code compare le minimum au montant seul à toutes les dates
  (`src/retraite_notionnelle/droit/liquider.py`, ligne 1561) ; candidat de la note de
  2006, dont 2009 donne la date de bascule.
- *Le tuteur rétribué* : sans sa complémentaire, douze mois de cumul au plus (D. 634-13-2),
  contre « six mois » dans `cumul_emploi_retraite_complementaire_des_independants.yaml`
  (ligne 186) ; la circulaire RSI n° 2009/017 reconduit en 2009 le candidat de 2008.

**Écarts relevés, déjà déclarés.** La majoration de 11,1 % d'une réversion d'effet
antérieur à 2010 (`reversion.yaml`, lignes 1052 à 1058) ; le partage de la réversion du
polygame et son paiement en Algérie (`docs/limites/3-systeme-actuel.md`, lignes 469 et
658) ; les exploitants agricoles et les avocats hors du cumul libéralisé
(`cumul_emploi_retraite_et_retraite_progressive.yaml`, lignes 339 à 341 et 394 et 395) ;
le régime qui valide le chômage (`3-systeme-actuel.md`, lignes 394 à 399) ; les États
tiers du Luxembourg (note des règlements européens, ligne 162) ; les périodes
équivalentes et la subsidiarité du minimum contributif (`minimum_contributif.yaml`,
lignes 575 et 612) ; l'ACCRE (`3-systeme-actuel.md`, ligne 218). La surcote de 1,25 %
réservée aux pensions d'effet depuis le 1er avril 2009 ne fait pas d'écart : le modèle
la date par trimestre civil entier, et aucun de 2009 n'est entier avant cette date.

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : la polygamie en Algérie, le contrôle des ressources de la réversion, le
rétablissement des militaires (des adresses), le § 21 corrigé des versements, sur leurs
précédents ; l'assiette des stagiaires et l'ACCRE (des barèmes de cotisation), la
présomption d'inaptitude (une procédure), sur l'arrêté de 1985 et la n° 2008/017 ; la CSG
de la lettre du 30 juin (une question de champ). En `hors_modele`, quand `limite` se
défendrait : les heures supplémentaires (la phrase sur les trimestres cotisés) ; le RSTA,
que la circulaire exclut des ressources du minimum vieillesse, sur le rangement de son
décret ; l'annexe de la n° 2009/71, quand sa circulaire est en `limite`. La raison de
l'avenant de la n° 2009/64 et celle de la Pologne se seraient échangées avec une voisine.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2009/10 par la n° 2018/4, la n° 2009/21 par la
  n° 2010/50, la n° 2009/45 par la n° 2019/3, la n° 2009/49 par la n° 2010/20, la
  n° 2009/50 par la n° 2009/58, elle-même par la n° 2010/18, la n° 2009/82 par la
  n° 2010-15 ; la n° 2009/39 modifiée par la n° 2012/25.
- Des dates et des titres : la diffusion n° 2009/5 datée du 1er décembre au registre pour
  le 2 ; la circulaire du 6 mai (fraude) sans numéro, quand son nom suggère une
  « 2009/5 » ; le tableau du 18 novembre titré « Lettre Cnav » ; la n° 2009/65 titrée
  « 7/10/2009 » ; l'objet de la n° 2009/77 ministérielle vide.
- Des doublons et des pièces séparées : le PDF du 29 mai double la page de la n° 2009/144 ;
  les annexes des n° 2009/12, 2009/64 et 2009/71 sont à la période sans leur circulaire,
  rangée d'avant ; l'« annexe 1 » de la n° 2009/278 porte les deux formulaires.
- Des annexes annoncées et non servies : la lettre du 15 juin jointe à la n° 2009/285.
- Des erreurs : la majoration du minimum dite de 706,86 € pour 656,86 €, deux fois, des
  exemples faux d'un résultat ou d'une formule, un sommaire qui dit 2012 pour 2011, une
  synthèse titrée « n° 2009/000 » (circulaire RSI n° 2009/031) ; L. 161-1-6 et L. 161-1-8,
  D. 173-1 et R. 173-1 cités l'un pour l'autre (n° 2009/82) ; le résumé de la n° 2009/84
  qui colle un fragment de celui de la n° 2009/82 ; « Ll 14-13 » et « L.1621-14 VII »
  (circulaire du 6 mai) ; un « décret n° 93-1311 du 23 décembre 1998 » pour la Mongolie
  (annexe de la n° 2009/21) ; l'Islande « au sein de l'UE » (lettre du 25 septembre) ; des
  États de l'Union parmi les « pays tiers » (diffusion n° 2009/4) ; « attestations
  d'allocation rétroactive » pour d'affiliation (n° 2009/50 et 2009/58).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Ni D. 634-13-2, ni le règlement
invalidité-décès des artisans, ni le décret du minimum contributif de 2009 n'ont été
relus au Journal officiel ; les moteurs n'ont tourné sur aucun cas.
