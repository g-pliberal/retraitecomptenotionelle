# Étape 6, circulaires de 2011 : les 68 références sans thème de la dix-huitième période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées ; la quatrième, les
circulaires, lettres et instructions sans thème, l'est de 1936 à 2011 (cette note et celles
d'avant). Une seconde lecture avance à rebours et a fait 2018 à 2026, avec son propre bloc
(note de 2018 à 2021 à rebours). Restent 176 circulaires, de 2012 à 2017 ; la lecture dans
l'ordre reprend à 2012 (37), puis 2013 (44), 2014 (26), et s'arrête où elle rejoint
l'autre. Viennent ensuite, une session par nature : les 96 autres textes, les 74 que la
base nomme sans les servir, les 107 accords. Méthode : celle de la note de 2010, chaque
texte lu en entier, chaque citation vérifiée par script. 2011 a
deux écarts neufs : le cumul des retraités anticipés d'avant juillet 2011, et la
génération de la réversion d'un assuré mort avant son départ, depuis juillet 2011 (ici).

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2011 : 68, comme la note de 2010 les
  comptait. Toutes sont de 2011.
- *La lecture* : les 68, relues par l'API le 16 novembre 2026 vers 13 h 15 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 31 en page,
  37 en PDF lus au site (`/Pdf/<nom>`) par leur texte (`pdftotext -layout`). Deux PDF sont
  des scans, lus à l'image, sans citation vérifiable : la lettre ministérielle du 14 mars
  2011 et l'instruction fiscale 5 F-12-11 jointe à la n° 2011/57. 19 circulaires de la
  Cnav et 28 de leurs pièces ; 7 textes servis pour 5 circulaires ministérielles ;
  4 diffusions d'instructions ministérielles ; 4 lettres ministérielles et 2 de la Cnav ;
  4 circulaires du RSI.
- *Qui a lu* : les 68 en entier, par cinq agents de la session sur Opus, un lot par
  origine (deux de circulaires de la Cnav ; leurs pièces, avec leurs circulaires mères pour
  contexte ; les textes ministériels ; le RSI), lancés ensemble, sur une consigne commune
  (les raisons du registre et les renvois déjà employés, avec leur effectif ; les
  rangements de 2008 à 2010 pour précédents ; les notes de 2009 et 2010). Les 177
  citations ont été retrouvées mot pour mot, par script, dans le texte servi (blancs
  normalisés), chaque raison hors modèle dans le registre, chaque renvoi dans le dépôt. La
  session a relu elle-même les passages, le code et les fiches qui décident des écarts
  neufs (plus bas).
- *Les sorts* : 68 références rangées, 32 `limite`, 36 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 68 lignes, les colonnes
  `sort` et `renvoi` seules, écrites par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : les plafonds de ressources de la réversion au 1er janvier 2011
  (n° 2011/1) ; le salaire qui valide un trimestre, 1 800 € (n° 2011/2) ; le report de
  l'âge légal et de l'âge du taux plein, et ses dérogations (n° 2011/24, la n° 2011/017 du
  RSI, ses neuf fiches) ; la retraite anticipée des handicapés (n° 2011/25 et son tableau,
  n° 2011/63, RSI n° 2011/013) ; la durée requise des nés de 1953 et 1954 (RSI
  n° 2011/015) ; la fin de l'indemnisation du chômage (n° 2011/41) ; la retraite pour
  pénibilité (n° 2011/49 et son tableau des taux) ; l'allocation des travailleurs de
  l'amiante (n° 2011/56) ; la résidence des anciennes allocations du minimum vieillesse
  (n° 2011/58, lettre du 7 avril) ; l'âge de l'ASPA des inaptes et assimilés
  (n° 2011/59) ; le cumul emploi-retraite après le relèvement des âges (n° 2011/61) ; les
  deux tableaux de la carrière longue (n° 2011/16) ; le barème du versement pour la
  retraite (n° 2011/17) ; les âges de la réversion (n° 2011/69) ; les trois schémas de la
  convention franco-marocaine (n° 2011/78) ; la revalorisation du 1er avril (n° 2011/108) ;
  la CSG et la cotisation maladie des pensionnés d'organisations internationales
  (diffusion n° 2011/2, lettre du 8 février) ; EUMETSAT et la Banque africaine de
  développement parmi ces organisations (lettre Cnav du 28 février) ; les arriérés
  d'apprentissage (lettre Cnav du 1er mars) ; le rachat du volontariat de solidarité
  internationale (lettre du 11 février) ; le service civique (lettre du 14 mars) ; le
  micro-social (RSI n° 2011/011).
- *Hors modèle* : la fraude et les pénalités (14 : les 10 courriers de la n° 2011/68, la
  n° 2011/142 servie trois fois, la diffusion n° 2011/5) ; les monnaies (4) ; une règle de
  procédure (3 : la contrainte de la n° 2011/35, son modèle, celui de la n° 2011/68) ; une
  aide à l'insertion (3 : le RSTA deux fois, l'allocation de retour à l'activité) ; la
  demande de retraite (4 : les trois attestations de la n° 2011/21, la procédure de la
  pénibilité) ; une règle générale de l'administration (4 : la procuration et son imprimé,
  les échanges électroniques deux fois) ; la justice pénale (2 : la dissimulation du
  visage) ; une chacune, l'assurance volontaire maladie (l'attestation de la n° 2011/44) et
  l'impôt sur le revenu (l'instruction fiscale de la n° 2011/57).

**Les montants relus, conformes.** Le SMIC de 9,00 € (`smic_horaire.csv`, ligne 83) ; les
plafonds de la réversion, 18 720 € et 29 952 € (`reversion.yaml`, lignes 698 et 699) ; les
200 heures du trimestre (`validation_trimestres.csv`, ligne 28) ; la revalorisation du
1er avril 2011 (`revalorisation_pensions.csv`, ligne 114) ; l'âge légal et l'âge du taux
plein des nés au second semestre 1951 et depuis 1956 (`age_ouverture_requis.csv`, lignes
125 et 130 ; `age_annulation_decote.csv`, lignes 37 et 41) ; les durées de 1951 à 1954
(`duree_assurance_requise.csv`, lignes 115 à 118) ; les âges et durées de la carrière
longue, depuis 1951 (`carriere_longue.csv`, lignes 119 à 154) ; les durées et le taux de
80 % de la retraite des handicapés (`retraite_anticipee_handicap.yaml`, lignes 129 à
132) ; les seuils de 20 % et 10 % de la pénibilité ; le 1,6 SMIC et les six mois du cumul ;
les six mois de résidence de l'ASPA ; la date d'effet de la convention franco-marocaine
(`accords_internationaux.yaml`, ligne 479) ; l'ordre d'affectation du forfait micro-social
(`micro_social.yaml`, ligne 98). Sans série au dépôt : les taux de change, le RSTA,
l'allocation de retour à l'activité, le barème des versements, la liste des organisations
internationales, les 68 trimestres de la pénibilité.

**Des âges périmés, non des écarts.** Les circulaires de la première moitié de 2011 (n° 2011/24,
2011/25, 2011/41, 2011/59, 2011/69, RSI n° 2011/017) portent le calendrier de 2010, quatre
mois par génération, que la loi n° 2011-1906 et le décret de décembre 2011 ont accéléré
avant qu'aucun des nés de 1952 à 1955 ne l'atteigne ; le dépôt suit le calendrier accéléré,
à bon droit.

**Deux écarts neufs** (candidats), pour les sessions du modèle, sans y toucher.

- *Le cumul des retraités anticipés d'avant le 1er juillet 2011.* Circulaire Cnav
  n° 2011/61, point 33 : « aux assurés qui ont obtenu une retraite anticipée avant le 1er
  juillet 2011 et qui souhaitent reprendre une activité salariée, le report de l'âge légal
  et de l'âge d'obtention du taux plein ne s'applique pas » ; le cumul total s'ouvre à
  60 ans avec la durée, à 65 ans sans elle. Le modèle lit l'âge de la génération
  (`src/retraite_notionnelle/droit/cumul.py`, lignes 575 à 577), et applique la limite du
  cumul de quatre mois à deux ans de trop aux nés de juillet 1951 à 1955 partis en carrière
  longue ou handicapés avant juillet 2011. Rien au dépôt ne le nomme.
- *La génération de la réversion d'un assuré mort avant son départ, depuis le 1er juillet
  2011.* Circulaire RSI n° 2011/017 : le décret n° 2011-620 « modifie la rédaction de
  l'article R.353-3 » pour renvoyer aux règles des personnes atteignant « leur 57 ème
  anniversaire » l'année du décès. `reversion.yaml` (lignes 1158 à 1166) déclare la règle
  de la génération des soixante ans pour les décès du 1er juillet 2004 au 30 juin 2011, et
  rien après : le modèle prend toujours la génération du défunt.

**Candidats d'avant, que 2011 confirme.**

- *La durée des nés de 1953 à 1955 partis avant le décret de leur génération* (écart 1 bis
  de la note des écarts lourds, ligne 16) : 164 trimestres pour une demande reçue avant
  2011, 165 provisoires pour 1955 et 1956 (n° 2011/24, 2011/25 et son tableau, RSI
  n° 2011/015). Il n'est déclaré dans aucune fiche.
- *Le plafond de la réversion au SMIC de la date de la demande* (note de 2002, ligne 81) : sans
  effet en 2011 avant le SMIC du 1er décembre.

**Écarts relevés, déjà déclarés.** La pénibilité (`ecarts-au-droit-positif.md`, lignes 453 à
457 ; `3-systeme-actuel.md`, ligne 83) ; l'allocation des travailleurs de l'amiante
(`3-systeme-actuel.md`, lignes 438 à 444) ; la majoration de L. 814-2 hors de France
(`3-systeme-actuel.md`, lignes 560 et 561) ; l'âge de l'ASPA des inaptes
(`minimum_vieillesse.yaml`, lignes 256 à 260) ; la reconnaissance de travailleur handicapé
(`retraite_anticipee_handicap.yaml`, lignes 288 à 301) ; le rachat des périodes à
l'étranger et les arriérés (`3-systeme-actuel.md`, lignes 310 et 317) ; la réversion
partagée d'un polygame (`3-systeme-actuel.md`, ligne 658) ; les abattements du RCO et du
NRCO (`abattement_rci.yaml`, lignes 32 à 41).

**Points non tranchés.**

- *Le barème du NRCO.* La n° 2011/017 du RSI donne 0,9625 à quatre trimestres manquants et
  0,8362 à vingt, quand le modèle applique le barème du RCI (0,96 et 0,78) ; la fiche
  `abattement_rci.yaml` dit la table du NRCO non publiée : ces deux points peuvent la
  nourrir, pour les sessions des données.
- *Les organisations internationales* : EUMETSAT et la Banque africaine de développement
  s'ajoutent en 2011 ; le dépôt n'en tient pas la liste.
- *Les sorts retenus*, quand l'autre se défendrait. En `limite` : l'allocation des
  travailleurs de l'amiante, la fin du chômage, le micro-social, le service civique, les
  arriérés d'apprentissage, le barème des versements, sur leurs précédents. En
  `hors_modele` : les attestations de la n° 2011/21 et la procédure de la pénibilité,
  formulaires ; l'attestation de résidence de la n° 2011/44.

**Ce que la base sert de travers.**

- Des dates : la n° 2011/017 du RSI datée du 14 juin en tête, du 14 juillet par la base ;
  la n° 2011/69 datée du 30 septembre pour le 7 octobre ; la lettre Cnav du 1er mars cite
  la circulaire DSS du 23 janvier 2008 au « 28 janvier » ; la diffusion n° 2011/2 nomme
  la lettre du 8 février 2011 « n° 13397/2010 ».
- Des mentions d'annulation : les n° 2011/24 (par la 2012/6), 2011/25 (2012/13), 2011/35
  (2017/17), 2011/41 (2012/31), 2011/49 (2012/63), 2011/56 (2012/42), 2011/58 (2018/6),
  2011/59 (2012/19), 2011/61 (en partie, 2012/27), 2011/63 (2018/24), la n° 2011/017 du
  RSI (2023/19).
- Des doublons : la n° 2011/142 servie en deux PDF identiques octet pour octet, que la
  page ministérielle et la diffusion n° 2011/5 lient chacune sous un nom ; l'attestation
  « taux supérieur à 80 % » qui répète les deux autres pièces de la n° 2011/21 ; le
  fichier « annexe_32.5 » pour l'annexe 2.5.
- Des textes non servis : les circulaires du 2 mars et n° 2011/108, que les pages ne lient
  qu'à Légifrance et circulaires.gouv.fr ; les trois annexes de la n° 2011/017 du RSI ;
  les taux de change, renvoyés à la base.
- Des erreurs : « 57 ans » pour 56 ans aux nés de 1953 dans l'annexe 2 de la n° 2011/16,
  sans effet ; « Age en 2010 » sur le barème de 2011 ; des exemples faux dans la
  n° 2011/017 du RSI (une inaptitude avant l'âge légal, 2016 pour 2014, « 62 ans et 8
  mois » pour 60 ans et 8 mois, un arrondi « supérieur » qui est inférieur) ; le « 1er juin
  1951 » pour le 1er juillet dans la n° 2011/013 du RSI ; des coquilles (« Le n° 2011-354 »,
  « décret n° décret », « Janvier 20 23 »).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Ni R. 353-3, ni le texte qui fonde le point 33 de la
n° 2011/61 (le cumul des retraités anticipés) n'ont été relus au Journal officiel ;
les moteurs n'ont tourné sur aucun cas.
