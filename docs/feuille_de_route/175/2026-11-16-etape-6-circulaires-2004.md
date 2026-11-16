# Étape 6, circulaires de 2004 : les 73 références sans thème de la onzième période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées ; la quatrième, les
circulaires, lettres et instructions sans thème, l'est de 1936 à 2004 (cette note et celles
des périodes d'avant). Restent 745 circulaires, de 2005 à 2026, par période (66 en 2005, 61
en 2006, 120 en 2007, 60 en 2008, 65 en 2009) ; puis, une session par nature : les 96
autres textes, les 74 que la base nomme sans les servir, les 107 accords. Méthode : la
base relue par l'API (`_reference` de `cnav_legislation.py`), les pièces PDF lues au site
sous `/Pdf/<nom>`, chaque texte lu en entier, la citation d'un agent retrouvée par script
dans le texte servi. Candidat neuf : la réversion des pensions prenant effet au second
semestre 2004, que le ministre fait servir aux règles d'avant la réforme (ici).

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2004 : 73, comme la note de 2003 les
  comptait.
- *La lecture* : les 73, relues par l'API le 16 novembre 2026 à 11 h 20 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies : 57 en page (549 128 octets de
  texte), 16 en PDF lus au site (`/Pdf/<nom>`) par leur texte (`pdftotext`, 218 358
  octets) ; aucun scan. 28 circulaires de la Cnav, 14 de leurs pièces et la n° 2004/41,
  servie en PDF seul ; la circulaire Cancava n° 2004/15 ; 8 circulaires ministérielles,
  7 diffusions d'instructions ministérielles, 6 lettres de la Cnav, 8 lettres
  ministérielles.
- *Qui a lu* : les 73 en entier, par quatre agents de la session sur Opus, un lot chacun
  (de 190 000 à 193 000 octets), lancés ensemble, sur une consigne commune (les raisons du
  registre et les renvois déjà employés, avec leur effectif ; les rangements de 2003 pour
  précédents). Les 73 citations ont été retrouvées mot pour mot, par script, dans le texte
  servi (blancs normalisés), chaque raison hors modèle dans le registre, chaque renvoi
  dans le dépôt ; les trois exemples de la n° 2004/37, des frises sans phrase, ont pour
  citation leur légende, « Période de référence ». La session a relu elle-même les
  passages et les fiches qui décident des écarts (plus bas).
- *Les sorts* : 73 références rangées, 36 `limite`, 37 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 73 lignes, les colonnes `sort`
  et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : la réforme de 2003 mise en œuvre — la retraite anticipée des assurés
  handicapés (n° 2004/31, lettre de la Cnav du 12 octobre, lettre ministérielle du
  30 août), la surcote (les trois exemples de la n° 2004/37), la décote des artisans par
  génération (Cancava n° 2004/15), le salaire annuel moyen des pluriactifs, le minimum
  contributif et le cumul (lettres ministérielles des 25 mars et 26 novembre, diffusion
  n° 2004/10, n° 2004/13), la carrière longue (périodes canadiennes, lettre du
  1er septembre ; trimestres du Crédit foncier, lettre du 26 avril), la déclaration de la
  majoration de durée pour enfants (annexe de la n° 2004/22), la réversion (n° 2004/34,
  lettre ministérielle du 5 octobre) ; le congé de reclassement (n° 2004/3 et son annexe) ;
  l'élargissement de l'Union au 1er mai 2004 (circulaire ministérielle n° 2004/181,
  diffusion n° 2004/4), l'accord avec la Suisse qui ne s'y étend pas (lettre du
  29 septembre), le règlement n° 883/2004, publié et pas encore applicable (n° 2004/246 et
  sa diffusion), l'arrêt Barreira Pérez (n° 2004/5), la convention avec le Gabon
  (n° 2004/42) ; la contribution de solidarité pour l'autonomie et la cotisation salariale
  déplafonnée (n° 307/2004), la CSG portée à 6,6 % (n° 2004/629) et ses seuils de 2005
  (n° 2004/36) ; le trimestre de 2005 (n° 2004/56), les rentes ouvrières et paysannes
  (n° 2004/59), les plafonds des veuves de guerre (n° 2004/54), le plafond de l'inapte
  (n° 2004/35), l'allocation des travailleurs de l'amiante (n° 2004/41), la majoration
  pour enfant des clercs de notaire (n° 2004/49), les apprentis d'avant 1972 (diffusion
  n° 2004/2), le guichet unique du spectacle occasionnel (n° 2004/123).
- *Hors modèle* : l'action sociale (10 : l'aide ménagère, son complément qualité, ses
  participations horaires, l'évaluation des besoins et leurs pièces) ; les monnaies (4) ;
  les formulaires des accords avec le Canada et les États-Unis (4, n° 2004/39 et ses deux
  pièces, n° 2004/40) ; la tenue du relevé de carrière (4 : la preuve des cotisations, la
  convention d'échange des données de carrière n° 2004/55 et son annexe, le salaire
  reconstitué des artistes) ; le droit des étrangers (3) ; la législation applicable aux
  toreros (2) ; le titre de travail simplifié (2) ; et huit autres, une par raison (les
  avantages en nature, la retenue à la source, l'allocation de l'amiante elle-même,
  l'allocation de retour à l'activité, le secret professionnel, le contrat de
  professionnalisation, la prescription de l'AVPF, le versement exceptionnel de 70 €).

**Les montants relus, conformes.** Le SMIC de 7,61 € au 1er juillet 2004
(`macro/smic_horaire_releves.csv`) ; le trimestre de 2005, 1 522 €
(`legislation/validation_trimestres.csv`) ; le seuil de la CSG de 2005, 7 165 € pour une
part (`legislation/csg_pensions_seuils.csv`) ; le plafond de 2004, 29 712 € ; le minimum
contributif au 1er janvier 2004, 6 511,06 €, et majoré, 6 706,39 € ; les durées requises
et de proratisation des générations 1944 à 1948, et les années du salaire annuel moyen ;
les coefficients de décote des artisans de 1944 à 1953 ; les plafonds des veuves de
guerre, 11 753,71 et 15 908,38 € (la pension de veuve et les allocations de
`legislation/minimum_vieillesse_avant_2007.csv`) ; le plafond de l'inapte, 1 978,60 € par
trimestre, 50 % de 520 fois le SMIC, sans série.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *La réversion des pensions prenant effet au second semestre 2004.* Lettre ministérielle
  du 5 octobre 2004 : « Dans l'attente de la conclusion de cette étude, je vous demande de
  continuer d'ouvrir les droits à pension de réversion et de calculer et verser ces
  pensions sur la base de la réglementation en vigueur avant la loi du 21 août 2003. »
  La fiche `reversion` applique la réforme aux réversions prenant effet depuis le
  1er juillet 2004, et ne nomme ni la lettre ni sa suspension. Si la suspension n'a été
  que provisoire, les décrets de la fin de 2004 reprenant ces réversions, il n'y a pas
  d'écart ; sinon, la caisse sert, pour un décès de l'été 2004, la réversion d'avant
  (condition d'âge, cumul avec la retraite du survivant), le modèle celle de la réforme.
  À trancher au Journal officiel, par les décrets du 24 août et de décembre 2004.

**Écarts relevés, déjà déclarés ou plus petits.**

- *Le plafond de l'inapte* (n° 2004/35, 1 978,60 € par trimestre depuis le 1er juillet
  2004) : l'écart que la note de 2003 a dit neuf, sous l'article R. 352-2.
- *Le plafond de la réversion au SMIC de juillet* (n° 2004/34 : 15 828,80 € au lieu des
  14 955,20 € du modèle) : déclaré dans la fiche `reversion`, lignes 1149 à 1155.
- *Le congé de reclassement* (n° 2004/3 : un trimestre par cinquante jours) : déclaré
  dans `docs/limites/3-systeme-actuel.md`, lignes 383 à 385.
- *La majoration pour enfant des clercs de notaire* (n° 2004/49) : déclarée dans
  `priorite_majorations_enfants.yaml`, lignes 154 à 156 et 205 à 209.
- *La convention avec le Gabon*, une option (n° 2004/42 : « Les caisses de retraite
  doivent faire connaître au demandeur la possibilité d'option »), que le tableau des
  accords range en `comparaison` (`accords_internationaux.yaml`, ligne 433) : sans
  effet, le moteur servant l'une et l'autre de même (`etranger.py`, ligne 66).
- *La cotisation salariale déplafonnée*, née le 1er juillet 2004 (n° 307/2004), que
  `regimes/regime_general.yaml` (ligne 397) compte nulle en 2004 : elle n'ouvre aucun
  droit.

**Points non tranchés, les sorts retenus.** La retraite anticipée des handicapés nés en
1949 : la n° 2004/31 sursoit à leur examen, leur durée « n'est pas à l'heure actuelle
confirmée », quand le modèle leur oppose la durée de 161 trimestres fixée ensuite pour leur
génération (`duree_assurance_requise.csv`) ; ni écart ni conformité, le texte ne disant
rien. Les trimestres du Crédit foncier réputés cotisés pour la carrière longue (lettre du
26 avril), que la fiche `credit_foncier_transfert_1989`, non modélisée, ne dit pas. En
`limite`, quand `hors_modele` se défendrait : le guichet unique du spectacle (n° 2004/123),
la cotisation de solidarité (n° 307/2004), le règlement n° 883/2004 pas encore applicable,
l'accord avec la Suisse (lettre du 29 septembre). En `hors_modele`, quand `limite` se
défendrait : les avantages en nature (n° 2004/9), qui entrent aussi dans les ressources
du minimum et de la réversion ; la prescription de l'AVPF (lettre du 19 avril) ; le
salaire reconstitué des artistes (lettre ministérielle du 13 décembre).

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2004/54 par la n° 2004/58 ; la n° 2004/41 par la
  n° 2012/68 ; la n° 2004/31 et la lettre du 12 octobre par la n° 2018/24 ; la n° 2004/15
  par la n° 2005/5 ; la circulaire ministérielle n° 2004/25 par la n° 2007/21.
- Des annexes annoncées et non servies : l'annexe II de la n° 2004/181, l'accord de la
  n° 2004/248 et de la diffusion n° 2004/5, les circulaires de la direction de la sécurité
  sociale des diffusions n° 2004/2, 2004/4 et 2004/9, la lettre de la diffusion
  n° 2004/6, le spécimen de la lettre du 29 juillet, les annexes de la Cancava n° 2004/15,
  la liste des institutions de la n° 2004/15, le formulaire de la n° 2004/25.
- Des erreurs : l'annexe 1 de la n° 2004/51 titrée « 2ème trimestre » ; le dinar koweïtien
  de la n° 2004/60 à dix fois sa valeur ; la livre syrienne et le franc CFP sans valeur ;
  la grille de 2003 reprise par la n° 2004/14 ; un numérateur de 834 € pour un seuil de
  848 € à la n° 2004/16 ; « jusqu'au 30 juin 2003 » pour 2004 à la n° 307/2004 ; « 20004 »
  à la diffusion n° 2004/9.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les textes que ces circulaires
appliquent n'ont pas été relus au Journal officiel, ni les décrets de la réversion de 2004 ;
les moteurs n'ont tourné sur aucun cas.
