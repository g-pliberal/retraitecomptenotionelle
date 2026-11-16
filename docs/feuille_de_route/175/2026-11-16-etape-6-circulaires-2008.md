# Étape 6, circulaires de 2008 : les 60 références sans thème de la quinzième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2008 : 60, comme la note de 2007 les
  comptait.
- *La lecture* : les 60, relues par l'API le 16 novembre 2026 vers 12 h 25 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 44 en page,
  16 en PDF lus au site (`/Pdf/<nom>`) par leur texte (`pdftotext`). Cinq PDF sont des
  scans, lus à l'image, sans citation vérifiable : les annexes des circulaires Cnav
  n° 2008/16, 2008/33 et 2008/63, et les deux annexes de la n° 2008/57 (16 pages en
  tout). 25 circulaires de la Cnav et 8 de leurs pièces ; 6 circulaires ministérielles
  et 1 pièce ; 10 lettres ministérielles ; 4 diffusions d'instructions ministérielles ;
  6 circulaires du RSI.
- *Qui a lu* : les 60 en entier, par quatre agents de la session sur Opus, un lot par
  origine (la Cnav ; les circulaires ministérielles ; les lettres et diffusions ; le RSI),
  lancés ensemble, sur une consigne commune (les raisons du registre et les renvois déjà
  employés, avec leur effectif ; les rangements de 2006 et 2007 pour précédents ; la note
  de 2007). Les 120 citations des textes servis ont été retrouvées mot pour mot, par
  script, dans le texte servi (blancs normalisés), chaque raison hors modèle dans le
  registre, chaque renvoi dans le dépôt. La session a relu elle-même les passages, le
  code et les séries qui décident des écarts (plus bas).
- *Les sorts* : 60 références rangées, 31 `limite`, 29 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 60 lignes, les colonnes
  `sort` et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : la durée requise de 2009 à 2012 et la carrière longue (lettre
  ministérielle du 7 juillet, circulaires RSI n° 2008/056 et 2008/059) ; le trimestre de
  2009, 1 742 € (n° 2008/62) ; le plafond de l'inapte (n° 2008/28 et 2008/36) ; les
  seuils de la CSG de 2009 (n° 2008/35) ; la revalorisation de 1,008 au 1er septembre
  (lettre du 31 juillet) ; la récupération de l'ASPA sur la succession (n° 2008/17) ; les
  veuves de guerre (n° 2008/49) ; la polygamie et la réversion (annexes 2 et 3 de la
  n° 2008/14) ; R. 173-17 et les cultes (lettre du 31 mars) ; R. 173-4-3 étendu aux
  régimes européens (circulaire ministérielle n° 2008/219, circulaire RSI n° 2008/053) ;
  la résidence (n° 2008/245) ; le volontariat associatif (n° 2008/52) ; les stagiaires
  (n° 2007/236, datée de 2008 au registre) ; le travail dissimulé redressé au forfait
  (n° 2008/255) ; les cotisations arriérées (n° 2008/17 ministérielle) ; le versement
  pour la retraite — des diplômes étrangers (lettre du 25 juillet), hors du taux de la
  carrière longue après le 12 octobre 2008 (lettre du 31 octobre) ; la majoration pour
  enfant handicapé (lettre du 1er avril) ; le dernier salaire du cumul emploi-retraite
  (lettre du 2 avril) ; le rétablissement des élèves d'une école militaire (lettre du
  24 avril, annexe de la n° 2008/33) ; les entretiens franco-allemands (n° 2008/57) ; les
  rentes des retraites ouvrières et paysannes (n° 2008/3) ; au RSI, le tutorat du cédant
  et la prime de transmission (n° 2008/013), le micro-social de 2008 (n° 2008/017), le
  rachat Madelin du conjoint collaborateur (n° 2008/022).
- *Hors modèle* : les monnaies (8) ; la fraude et le droit de communication (4) ;
  l'application administrative d'une convention bilatérale (3 : l'Algérie, le Mali) ;
  l'instruction coordonnée de la demande (2 : les formulaires E 205 allemands) ; la
  retenue à la source (2) ; la demande ou le paiement d'un versement (2) ; une chacune, la
  procédure pénale, la tenue du relevé de carrière (le travail dissimulé diffusé par la
  n° 2008/7), le versement exceptionnel de 200 €, l'allocation de retour à l'activité,
  les institutions de la coordination (la Finlande), les avantages en nature, le secret
  professionnel, le paiement au Mali.

**Les montants relus, conformes.** Le SMIC de 8,63 € et de 8,71 €
(`smic_horaire_releves.csv`, lignes 76 et 77) ; le trimestre de 2009, 1 742 € ; le
plafond de 2008 ; le seuil de la CSG de 9 560 € (`csg_pensions_seuils.csv`, ligne 84) ;
la revalorisation de 1,008 (`revalorisation_pensions.csv`, ligne 111) et les coefficients
des salaires au 1er septembre 2008 ; les durées requises de 161 à 164
(`duree_assurance_requise.csv`, lignes 113 à 116) ; au RSI, le taux de base des
commerçants de 2008, 16,65 %, les 25 années du revenu annuel moyen de la génération 1953,
les coefficients de minoration, les durées de référence. Sans série au dépôt : le RMI,
la limite de récupération de l'ASPA, les plafonds des veuves de guerre, le minimum
garanti du code du travail, le plafond horaire de 2007.

**Le candidat de 2007, confirmé.** La carrière longue partie avant 2009, à qui le modèle
oppose 161 à 164 trimestres au lieu de 160 (note de 2007). La lettre ministérielle du
7 juillet réserve la durée par génération aux pensions « prenant effet à compter du
1er janvier 2009 », et l'étend à la durée cotisée de la carrière longue et à la retraite
anticipée des handicapés. Les circulaires RSI n° 2008/056 et 2008/059 : « l'assuré doit
justifier de 168 trimestres quel que soit l'âge de départ à la retraite », de 2004 à 2008,
dont 168, 164 ou 160 cotisés ; l'exemple d'un né en janvier 1952 parti au 1er octobre
2008 : « 168 trimestres d'assurance dont 168 cotisés ». Le code relu :
`src/retraite_notionnelle/droit/ouvrir.py`, lignes 510 à 527, et son jumeau
`moteur/js/droit/ouvrir.js`, lignes 404 à 415, lisent la table par la seule génération ;
`scenarios/actuel.py`, lignes 2212 à 2218, ne fixe 160 avant 2009 qu'aux fonctionnaires.
La n° 2008/056 donne aussi, en règle générale, 163 trimestres de référence au né en
1951, sans dire si elle vaut pour une pension anticipée de 2008 : la proratisation reste
à trancher au texte.

**Un écart neuf** (candidat), voisin, pour les sessions du modèle, sans y toucher.

- *Les nés de 1953 à 1955 partis avant le décret de leur génération, à 164 trimestres.*
  Lettre ministérielle du 7 juillet : « Dans l'attente de la publication de ce décret, la
  durée d'assurance applicable aux générations 1953 et suivantes reste celle applicable à
  la génération 1952. » Les décrets sont du 30 décembre 2010 (1953 et 1954) et du
  1er août 2011 (1955) (`scripts/fetch/dila_legi_duree_requise.py`, lignes 24 et 25).
  La table (`duree_assurance_requise.csv`, lignes 117 à 119 : 165, 165, 166) ne porte pas
  de date d'effet, et le moteur l'oppose dès 2009 aux départs anticipés de ces
  générations (carrière longue, handicap). Rien ne le déclare. À relire au Journal
  officiel avec la date d'application que chaque décret se donne.

**Candidats plus étroits**, non trouvés déclarés, à trancher au texte.

- *Le micro-social de 2008, sans assiette minimale.* Circulaire RSI n° 2008/017 : les
  droits « restent calculés avant prise en compte du plafonnement » des cotisations, donc
  sur les cotisations normales, assiette minimale comprise. Le code
  (`src/retraite_notionnelle/carriere.py`, ligne 742) n'oppose l'assiette minimale à
  aucune ligne « micro », à toute année, et la saisie admet le micro-fiscal depuis 2007
  (`moteur/js/saisie.js`, lignes 361 à 372) ; confirme et précise le candidat de 2007
  (circulaire RSI n° 2007/091).
- *La complémentaire des artisans et commerçants pendant le cumul, avant 2009* : le
  tuteur rétribué « n'est pas autorisé à percevoir » sa RCO ou sa NRCO (circulaire RSI
  n° 2008/013), contre la version supposée `servie_entiere_avant_2009` de
  `cumul_emploi_retraite_complementaire_des_independants.yaml` (lignes 29 à 44), comme la
  n° 2007/109 ; le tutorat, douze mois de cumul hors des seuils (D. 634-13-2), candidat
  de 2007, confirmé.
- *Le partage du dépassement du plafond de réversion* : R. 173-17 le répartit au prorata
  (lettre ministérielle du 31 mars), le code l'impute régime après régime
  (`src/retraite_notionnelle/droit/reversion.py`, lignes 1950 et 1951) ; même total,
  autre partage ; candidat de 2007, confirmé.
- *La résidence du conjoint pour l'ASPA servie avec la majoration pour conjoint à
  charge* (circulaire ministérielle n° 2008/245) : la fiche
  `residence_et_minimum_vieillesse.yaml` (lignes 115 à 118) ne lit que la résidence de
  l'assuré.
- *Les périodes allemandes non datées* (n° 2008/57 : l'activité de faible importance, le
  partage des droits au divorce), qui comptent pour le taux quand la saisie demande un
  début et une fin ; la présomption de `totalisation_des_periodes_etrangeres.yaml`
  (lignes 112 à 116) les couvre en partie.

**Écarts relevés, déjà déclarés.** La récupération de l'ASPA (`minimum_vieillesse.yaml`,
lignes 234 à 242) ; les veuves de guerre (`docs/limites/3-systeme-actuel.md`, lignes 494
et 495) ; la polygamie (même fichier, lignes 468 et 469, 657 et 658) ; les seuils des DOM
de la CSG (`csg_des_pensions_selon_le_revenu.yaml`, lignes 88 à 99) ; le volontariat
associatif (`service_civique.yaml`, lignes 182 à 186) ; le stagiaire et le travail
dissimulé au forfait (`docs/limites/3-systeme-actuel.md`, lignes 159 à 163) ; les
cotisations arriérées et les rachats (même fichier, lignes 303 à 324) ; la majoration
pour enfant handicapé (lignes 416 à 419) ; le dernier salaire du cumul
(`cumul_emploi_retraite_et_retraite_progressive.yaml`, lignes 316 à 322) ; R. 173-4-3
étendu (`pension_proratisee.yaml`, lignes 223 à 242) ; la résidence en général
(`residence_et_minimum_vieillesse.yaml`, lignes 96 à 107) ; l'abattement de la RCO en
2009, 12,25 % pour le né en 1949 (circulaire RSI n° 2008/059), quand le modèle applique
7 % (`abattement_rci.yaml`, lignes 31 à 42, dont la question ouverte des lignes 75 à 80
trouve là une réponse partielle). Le plafond de l'inapte, l'écart que la note de 2003 a
dit neuf, n'est encore porté par aucune fiche ni limite.

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : les rentes ouvrières et paysannes, l'annexe de la n° 2008/33 et la lettre du
24 avril (le modèle rétablit les services que la saisie déclare militaires), les
entretiens franco-allemands, la lettre du 25 juillet et la circulaire RSI n° 2008/022
(des rachats), la n° 2008/017 ministérielle (preuves et formulaires), la n° 2007/236
ministérielle (l'assiette), la n° 2008/255 (le relevé de carrière), la prime de
transmission de la n° 2008/013 (une aide de l'État, comme l'indemnité de départ de 2007).
En `hors_modele`, quand `limite` se défendrait : la diffusion n° 2008/7 (le travail
dissimulé, comme la n° 2008/255 rangée en `limite`), les avantages en nature
(n° 2008/37, que lisent aussi les ressources de l'ASPA). Les raisons des textes de fraude
et de procédure pénale se seraient échangées.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2008/16 par la n° 2009/21, la n° 2008/52 par la
  n° 2010/55, la n° 2008/61 par la n° 2009/20, la n° 2008/65 par la n° 2013/32 ; la
  circulaire RSI n° 2008/013 « annule et remplace » la n° 2007/081.
- Des dates fausses au registre : la circulaire RSI n° 2008/056 « du 11/09/2009 » pour
  2008 ; la n° 2008/36 « du 11/07/2008 » pour le 17 juillet ; la n° 2008/32 du 3 juillet
  pour le 4 ; la circulaire ministérielle n° 2007/236, du 14 juin 2007, rangée en 2008.
- Des doublons et des pièces séparées : le PDF de la circulaire ministérielle n° 2008/17
  double la page `CR_MIN_200817_23012008.aspx`, déjà rangée, et embarque le formulaire
  que l'annexe sert une seconde fois ; les annexes 2 et 3 de la n° 2008/14 et celle de la
  n° 2008/33 sont à la période sans leur circulaire, rangée d'avant.
- Une pièce d'une autre date : la diffusion n° 2008/6 lie une annexe de la diffusion
  n° 2011/8 (circulaire ministérielle n° 2011/323), non lue.
- Des annexes annoncées et non servies : la circulaire DSS/5C n° 2008/61 jointe à une
  diffusion, l'interministérielle du 28 juillet, la circulaire DACG n° 2007-04 ; la
  circulaire n° 2008/219 jointe à la circulaire RSI n° 2008/053, la lettre du 7 juillet
  aux n° 2008/056 et 2008/059.
- Des erreurs : la « loi n° 2008-1786 » pour 2007-1786 (n° 2008/255) ; L. 3232-1 et
  L. 3232-3 du code du travail cités l'un pour l'autre (même circulaire) ; la loi pour
  l'égalité des chances dite « 2006-296 » (n° 2007/236) ; le « décret 2004-232 du
  17 mars 2003 » (n° 2008/056) ; le décret n° 2007-966 daté tantôt du 14, tantôt du
  15 mai (n° 2008/017) ; l'arrangement franco-malien daté de 1978, avant la convention de
  1979 qu'il applique (n° 2008/63) ; des formulaires E 205 allemands qui sont des
  spécimens fictifs (n° 2008/57).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les décrets du 30 décembre 2010 et
du 1er août 2011 n'ont pas été relus au Journal officiel, ni R. 173-17, ni D. 634-13-2 ;
les moteurs n'ont tourné sur aucun cas.
