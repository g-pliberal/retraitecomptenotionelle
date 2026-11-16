# Étape 6, circulaires de 2007 : les 120 références sans thème de la quatorzième période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées ; la quatrième, les
circulaires, lettres et instructions sans thème, l'est de 1936 à 2007 (cette note et celles
des périodes d'avant). Restent 498 circulaires, de 2008 à 2026, par période (60 en 2008,
65 en 2009, 66 en 2010, 68 en 2011, 37 en 2012) ; puis, une session par nature : les 96
autres textes, les 74 que la base nomme sans les servir, les 107 accords. Méthode : la
base relue par l'API (`_reference` de `cnav_legislation.py`), les pièces PDF lues au site
sous `/Pdf/<nom>`, chaque texte lu en entier, la citation d'un agent retrouvée par script
dans le texte servi. Candidat neuf, le plus lourd : la carrière longue partie avant 2009,
à qui le modèle oppose 161 à 164 trimestres au lieu de 160 (ici).

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2007 : 120, comme la note de 2006 les
  comptait.
- *La lecture* : les 120, relues par l'API le 16 novembre 2026 vers 12 h 10 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies (la n° 2007/57, refusée une
  fois, l'a été au second appel) : 59 en page, 61 en PDF lus au site (`/Pdf/<nom>`) par
  leur texte (`pdftotext`), en tout 1,66 Mo de texte. Trois PDF sont des scans, lus à
  l'image, sans citation vérifiable : la circulaire DGEFP n° 2007/15 (15 pages, la
  deuxième manque), l'annexe japonaise et coréenne de la circulaire ministérielle
  n° 2007/225 (5 pages), les pages 2 à 12 de la lettre circulaire Acoss n° 2007/101. 32
  circulaires de la Cnav et 24 de leurs pièces ; 8 circulaires ministérielles et
  26 pièces, dont les 22 formulaires SE 351 de la convention franco-tunisienne ;
  6 diffusions d'instructions ministérielles, 1 note d'information ; 7 lettres de la Cnav,
  5 lettres ministérielles ; 10 circulaires du RSI, 1 lettre circulaire de l'Acoss.
- *Qui a lu* : les 120 en entier, par six agents de la session sur Opus, un lot chacun
  (de 275 800 à 276 300 octets, chaque circulaire avec ses pièces), lancés ensemble, sur
  une consigne commune (les raisons du registre et les renvois déjà employés, avec leur
  effectif ; les rangements de 2005 et 2006 pour précédents ; la note de 2006). Les
  108 citations des textes servis ont été retrouvées mot pour mot, par script, dans le
  texte servi (blancs normalisés), chaque raison hors modèle dans le registre, sauf une,
  chaque renvoi dans le dépôt. La session a relu elle-même les passages, le code et les
  fiches qui décident des écarts (plus bas).
- *Les sorts* : 120 références rangées, 34 `limite`, 86 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 120 lignes, les colonnes
  `sort` et `renvoi` seules, vérifié par script). Une raison neuve : l'indemnité de départ
  des commerçants et des artisans (circulaire RSI n° 2007/080), aide de l'État sous
  condition de ressources, que ni l'action sociale des caisses ni l'allocation de chômage
  ne couvrent.

**Par ce qu'elles disent.**

- *En `limite`* : la carrière longue de 2008 (circulaire ministérielle n° 2007/396,
  diffusion n° 2007/9) ; la durée de proratisation et les années du salaire annuel moyen
  gardées aux nés avant 1948 (n° 2007/2 et son annexe) ; le trimestre de 2008 (n° 2007/64) ;
  le plafond de l'inapte (n° 2007/49) ; les seuils de la CSG de 2008 (n° 2007/63) ; l'ASPA
  et l'ASI (circulaire RSI n° 2007/041) ; la réversion — sa seconde étape au 1er juillet
  2006 (circulaire RSI n° 2007/061), ses plafonds de 2008 (n° 2007/71), le changement de
  situation familiale (lettre de la Cnav du 18 avril), la pension de vieillesse de veuve
  en retraite progressive (lettre ministérielle du 30 octobre) ; le cumul emploi-retraite
  — des artisans et commerçants (circulaire RSI n° 2007/109), à la transmission de
  l'entreprise (n° 2007/093), sans cesser l'activité à la SEITA ou à la CRPCEN (lettre
  ministérielle du 18 juin) ; le chômage non indemnisé après vingt ans de cotisations
  (lettre ministérielle du 10 juillet) ; le volontariat associatif (lettre ministérielle
  du 5 décembre) ; le conjoint collaborateur (circulaire RSI n° 2007/013) ; la majoration
  pour conjoint à charge (n° 2007/067) ; les cotisations des indépendants en 2008
  (n° 2007/091) ; l'Accre (n° 2007/027 et 2007/147) ; les stagiaires (Acoss n° 2007/101) ;
  le congé de mobilité (circulaire DGEFP n° 2007/15 et sa page) ; les rentes des retraites
  ouvrières et paysannes (n° 2007/4) ; les accords — la Tunisie (n° 2007/277), le Québec
  (n° 2007/59), la Bulgarie et la Roumanie (diffusion n° 2007/3), les règlements
  n° 1992/2006 et 629/2006 (n° 2007/89, diffusion n° 2007/1), l'Allemagne (lettre de la
  Cnav du 16 mars), le Portugal (lettre du 5 avril), le chômage de l'affilié par accord
  de l'article 17 (lettre du 2 avril).
- *Hors modèle* : l'action sociale (28 : les n° 2007/7, 2007/16, 2007/23, 2007/24,
  2007/25, 2007/26 et leurs pièces) ; les conventions bilatérales dans leur gestion (25 :
  les 22 formulaires SE 351, le Cameroun, le Québec, la lettre de la Cnav du 30 janvier) ;
  les monnaies (8) ; la règle générale de l'administration (5 : archives militaires,
  secret professionnel, documents fiscaux étrangers) ; la procédure pénale (3, une dépêche
  de la justice numérotée en circulaire ministérielle, et ses deux annexes) ; deux chacune,
  la fraude, le paiement au Mali, la demande et son instruction, les institutions de la
  coordination (l'organisme de liaison hongrois, les annexes du règlement n° 1408/71), la
  législation applicable aux salariés japonais et coréens ; une chacune, la convention
  Cnav-Unédic, l'allocation de retour à l'activité, le contrat de professionnalisation, la
  retenue à la source, les avantages en nature, la section comptable des
  artistes-auteurs, l'indemnité de départ.

**Les montants relus, conformes.** Le SMIC de 8,27 € et de 8,44 € ; le plafond de 2007 et
de 2008 ; le trimestre de 2008, 1 688 € (200 heures) ; les plafonds de la réversion de
2008, 17 555,20 € et 28 088,32 € ; les seuils de la CSG de 2008 ; la revalorisation de
2007 ; l'ASPA de 2006 ; la majoration pour conjoint à charge, 609,80 € ; l'assiette
minimale des indépendants, 1 654 € ; la cotisation maladie des non-résidents ; les durées
de proratisation et les années du salaire annuel moyen par génération ; le taux de 54 %.
Deux montants à un centime ou à six près, l'un déclaré : l'ASPA d'une personne seule de
2007, 7 455,30 € par an au texte, 7 455,24 € à la série, douze fois le mensuel
(`minimum_vieillesse.yaml`, lignes 247 à 252) ; celle d'un couple, 13 374,17 € au texte,
13 374,16 € à la série (`minimum_vieillesse_couple.csv`, ligne 41), non déclaré, à relire
au décret.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *La carrière longue partie avant 2009, à 160 trimestres.* Circulaire ministérielle
  n° 2007/396, diffusée par la n° 2007/9 : la hausse de la durée « prévue au III de
  l'article 5 de la loi n° 2003-775 » et « la règle fixée au V du même article » « ne sont
  applicables que pour les pensions prenant effet à compter du 1er janvier 2009 » ; « Pour
  les assurés nés en 1949 et après, la durée d'assurance à retenir pour le calcul demeure
  fixée à 160 trimestres ». C'est le I de R. 351-45 (160 trimestres « quelle que soit la
  date de naissance »), que la fiche `duree_requise_par_generation.yaml` cite (lignes 84
  à 99) sans en tirer l'effet pour ces générations. Le moteur
  (`moteur/js/droit/ouvrir.js`, lignes 404 à 415, et son jumeau
  `src/retraite_notionnelle/droit/ouvrir.py`, lignes 510 à 527) ne ramène à 160 que les
  générations qui en demandent moins ; il oppose donc la table par génération
  (`duree_assurance_requise.csv`, lignes 113 à 116 : 161 à 164) aux nés de 1949 à 1952
  partis avant 2009, en carrière longue ou au titre du handicap. Leur pension est
  proratisée sur un à quatre trimestres de trop, et leur condition de durée, 168
  trimestres pour la carrière longue, relevée d'autant. Rien dans les fiches ni les
  limites ne le déclare.

**Candidats plus étroits**, non trouvés déclarés, à trancher au texte.

- *La complémentaire des artisans et commerçants pendant le cumul, avant 2009.* La
  circulaire RSI n° 2007/109 exige la cessation de toute activité artisanale ou
  commerciale pour l'ouverture et le service de la RCO et de la NRCO. La version
  `servie_entiere_avant_2009` de `cumul_emploi_retraite_complementaire_des_independants.yaml`
  (lignes 29 à 40), statut `supposee`, la sert entière pendant l'activité : le texte de
  2007 contredit l'hypothèse, que la fiche tire de la circulaire n° 2009-044.
- *La fraction de trimestre des périodes étrangères avant 2010.* La lettre de la Cnav du
  5 avril, sous l'article 15 du règlement n° 574/72 : « 3 mois = 13 semaines = 78 jours =
  1 trimestre », la fraction perdue. La fiche `totalisation_des_periodes_etrangeres.yaml`
  (lignes 117 à 120) l'arrondit au trimestre supérieur, d'après le règlement n° 987/2009,
  à toutes les dates.
- *La réversion de juillet 2004 à juin 2006 sans les réversions des régimes visés*,
  candidat de la note de 2006, que la circulaire RSI n° 2007/061 confirme ; la même dit le
  dépassement réparti au prorata entre les réversions des régimes visés (R. 173-17), quand
  le code l'impute régime après régime (`src/retraite_notionnelle/droit/reversion.py`,
  lignes 2075 à 2084 : même total, autre partage), et la réversion d'avant juillet 2004
  basculée sous condition de ressources à l'attribution d'une retraite personnelle,
  non vérifiée dans le code.
- *La révision des pensions bulgares et roumaines* (diffusion n° 2007/3) : les droits
  liquidés avant le 1er janvier 2007 se révisent sur demande à cette date, et une pension
  de date d'effet antérieure se calcule deux fois ; le modèle applique le seul accord en
  vigueur à la date d'effet (`accords_internationaux.yaml`, lignes 34 à 37).
- *Le chômage non indemnisé ultérieur* (lettre ministérielle du 10 juillet) : les vingt
  ans de cotisations comptent les périodes d'autres États membres ; le modèle ne compte
  que les lignes françaises (`src/retraite_notionnelle/carriere.py`, lignes 571 à 574).
- *La retraite anticipée sans cesser l'activité à la SEITA ou à la CRPCEN* tant que le
  droit n'y est pas ouvert (lettre ministérielle du 18 juin) ; *le tutorat du cédant*,
  douze mois de cumul hors des seuils (circulaire RSI n° 2007/093) ; *le plafonnement
  micro-social de 2008* (circulaire RSI n° 2007/091), que `micro_social_abattement.yaml`
  ne décrit qu'à partir de 2009 ; *la ZUS* au seuil du cumul des indépendants (n° 2007/109),
  la fiche ne nommant que la ZRR ; *le chômage en France de l'affilié par accord de
  l'article 17* (lettre de la Cnav du 2 avril) ; *les périodes tunisiennes de moins de 52
  semaines* (formulaire SE 351-17).

**Écarts relevés, déjà déclarés.** Le plafond de l'inapte (n° 2007/49 et 2007/109), l'écart
que la note de 2003 a dit neuf ; l'ASPA — le plafond au-dessus du montant, les anciennes
prestations, l'ASI, la récupération (`minimum_vieillesse.yaml`, lignes 37 à 43 et 235 à
242 ; `docs/limites/3-systeme-actuel.md`, lignes 484 à 487 et 558 à 560) ; les seuils des
DOM de la CSG (`csg_des_pensions_selon_le_revenu.yaml`, lignes 92 à 99) ; le volontariat
associatif (`service_civique.yaml`, lignes 182 à 186) ; l'Accre d'avant 2007
(`docs/limites/3-systeme-actuel.md`, lignes 218 à 229 et 388) ; la génération 1942 à 159
trimestres (`duree_assurance_requise.csv`, lignes 17 à 25) ; la majoration pour conjoint à
charge des indépendants (`majoration_conjoint_a_charge.yaml`, lignes 213 à 217) ; la
pension de vieillesse de veuve (`reversion.yaml`, lignes 1331 à 1336) ; la transmission
d'entreprise (`cumul_emploi_retraite_complementaire_des_independants.yaml`, lignes 185 à
188) ; le conjoint collaborateur — l'assiette minimale, l'affiliation à l'année, le rachat
(`conjoint_collaborateur_independants.yaml`, lignes 150 à 157 et 178 ;
`docs/limites/3-systeme-actuel.md`, ligne 314) ; le congé de mobilité
(`docs/limites/3-systeme-actuel.md`, lignes 384 et 385).

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : la convention tunisienne et le règlement n° 1992/2006 (aucune règle
française touchée), la lettre du 18 juin, la circulaire DGEFP n° 2007/15 (sans citation
vérifiable), l'Accre de décembre (une procédure de demande), les rentes ouvrières et
paysannes (fiche d'un régime hors champ). En `hors_modele`, quand `limite` se défendrait :
le Cameroun, les annexes du règlement n° 1408/71 (l'annexe IV, partie C), les documents
fiscaux étrangers (comme la diffusion n° 2006/4), les attestations du personnel civil
des armées, la lettre de la Cnav du 22 août (reliquats de la fonction publique), la
fraction fictive des artistes-auteurs. L'indemnité de départ aurait pu prendre la raison
de l'action sociale.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2007/30 par la n° 2007/58 (« nulles et non avenues
  les dispositions ») ; la n° 2007/29 par la n° 2007/70, elle-même par la n° 2010/60 ; la
  n° 2005/4 par la n° 2007/8.
- Des pièces d'une autre date : les circulaires RSI n° 2007/041 et 2007/061 servies avec
  des annexes de 2011 et 2012, aux montants parfois tronqués (« 7 18,77 € ») ; une
  entrée en jouissance au « 01/09/2076 ».
- Des annexes annoncées et non servies : l'arrangement général de la convention
  tunisienne (« annexe 0 ») ; la circulaire n° 2007/396 avec sa diffusion n° 2007/9 ; les
  circulaires diffusées par les n° 2007/3, 2007/4 et 2007/5 ; les décrets joints à la
  circulaire RSI n° 2007/091, les annexes 1 et 2 de la n° 2007/013, la circulaire DGEFP
  jointe à la n° 2007/147 ; la circulaire Cnav n° 2007/62, dont seule l'annexe des
  courriers est à la période.
- Des erreurs : la circulaire ministérielle n° 2007/4 datée de 2008 au registre, une
  dépêche de la justice, et la n° 2007/21, de la DGEFP, numérotées « DSS/DACI » ; la
  circulaire RSI n° 2007/013 datée de 2013 ; l'Entente avec le Québec « applicable au
  1er décembre 2003 » en tête, 2006 au corps ; la loi « n° 2006-296 » pour 2006-396
  (Acoss n° 2007/101) ; le « décret n° 206-1205 » (lettre du 5 décembre) ; « L. 1611-1 »
  pour L. 161-1-1 (n° 2007/147) ; la Corse-du-Sud et la Haute-Corse inversées dans la
  liste des ZRR de la n° 2007/109, dont plusieurs exemples écrivent le dépassement à
  l'envers ; des cellules « #DIV/0! » au guide de la n° 2007/23.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les textes que ces circulaires
appliquent n'ont pas été relus au Journal officiel, ni R. 351-45 dans sa rédaction de
2008, ni le règlement n° 574/72 ; les moteurs n'ont tourné sur aucun cas.
