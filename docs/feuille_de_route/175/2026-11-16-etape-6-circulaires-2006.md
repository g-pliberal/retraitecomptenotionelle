# Étape 6, circulaires de 2006 : les 61 références sans thème de la treizième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2006 : 61, comme la note de 2005 les
  comptait.
- *La lecture* : les 61, relues par l'API le 16 novembre 2026 vers 11 h 50 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies : 48 en page, 13 en PDF lus au
  site (`/Pdf/<nom>`) par leur texte (`pdftotext`), en tout 504 Ko de texte. Trois PDF
  sont des scans sans texte, les formulaires SE 130-05, SE 130-09 et SE 130-14 de la
  circulaire ministérielle n° 2006/372 (huit pages) : lus à l'image, sans citation
  vérifiable. 33 circulaires de la Cnav et 6 de leurs pièces ; 3 circulaires
  ministérielles et 3 pièces ; 4 diffusions d'instructions ministérielles ; 2 lettres de
  la Cnav, 6 lettres ministérielles ; 3 circulaires du RSI, 1 lettre circulaire de
  l'Acoss.
- *Qui a lu* : les 61 en entier, par quatre agents de la session sur Opus, un lot chacun
  (de 94 000 à 94 600 octets, chaque circulaire avec ses pièces), lancés ensemble, sur une
  consigne commune (les raisons du registre et les renvois déjà employés, avec leur
  effectif ; les rangements de 2004 et 2005 pour précédents). Les 58 citations des textes
  servis ont été retrouvées mot pour mot, par script, dans le texte servi (blancs
  normalisés), chaque raison hors modèle dans le registre, chaque renvoi dans le dépôt. La
  session a relu elle-même les passages et les fiches qui décident des écarts (plus bas).
- *Les sorts* : 61 références rangées, 30 `limite`, 31 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 61 lignes, les colonnes `sort`
  et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : le cumul emploi-retraite — l'activité de faible importance (n° 2006/18
  et 2006/27), le plancher de 160 % du SMIC (lettre ministérielle du 26 décembre) ; le
  salaire annuel moyen écrêté au plafond (n° 2006/58, lettre ministérielle du
  1er septembre, qui dit aussi le maximum avant la surcote) ; la réversion — le tableau
  des législations de la réforme de 2004 (annexe 1 de la n° 2006/37), le schéma
  communautaire (annexe de la n° 2006/38), les plafonds de 2007 (n° 2006/69), le régime
  local d'Alsace-Moselle (lettre ministérielle du 23 février, diffusion n° 2006/2) ; la
  retraite anticipée des assurés handicapés (n° 2006/50, circulaire RSI n° 2006/055) ; les
  ressources étrangères des prestations sous condition (circulaire ministérielle
  n° 2006/367, diffusion n° 2006/4) ; les veuves de guerre (n° 2006/53 et 2006/77) ; le
  plafond de l'inapte (n° 2006/40) ; le trimestre de 2007 (n° 2006/61) ; les seuils de la
  CSG (n° 2006/59) ; le rétablissement des fonctionnaires — les attestations militaires
  (n° 2006/16), les révoqués (n° 2006/54), les élèves des écoles des armées (lettre
  ministérielle du 12 juin) ; le formulaire inter-régimes de la carrière longue (lettre de
  la Cnav du 18 août) ; les artistes-auteurs de 1977 à 1994 (lettres ministérielles des
  13 juillet et 28 septembre) ; l'apprentissage minier d'avant 1972 (diffusion n° 2006/1) ;
  les arbitres sportifs (lettre circulaire Acoss n° 2006/118) ; le Portugal (n° 2006/2),
  le règlement n° 629/2006 (circulaire ministérielle n° 2006/249), l'accord avec la
  Suisse étendu aux dix (lettre de la Cnav du 24 avril).
- *Hors modèle* : les monnaies (8) ; l'action sociale (7 : la n° 2006/1 et ses trois
  annexes, la n° 2006/15, la n° 2006/25 et son annexe) ; les conventions bilatérales dans
  leur gestion (8 : le Maroc deux fois, Israël, l'Andorre — la circulaire ministérielle
  n° 2006/372, ses trois formulaires et la diffusion n° 2006/3) ; la retenue à la source (2) ; les avantages en
  nature (2) ; le rachat aidé des conjoints de bateliers (2, circulaires RSI) ; la caisse
  compétente pour la réversion (n° 2006/48) ; l'allocation de retour à l'activité
  (n° 2006/5).

**Les montants relus, conformes.** Le SMIC de 8,03 € et de 8,27 € ; le plafond de 2006,
2 589 € par mois, et de 2007, 2 682 € ; le trimestre de 2007, 1 654 € (200 heures) ; les
plafonds de la réversion de 2007, 17 201,60 € et 27 522,56 € ; la CSG, 7 417 € pour une
part et 11 379 € pour deux ; la revalorisation de 2005, 2 % ; l'AVTS de 2006 ; la part
salariale vieillesse de 6,65 % ; la cotisation maladie des non-résidents de 3,2 % ; les
durées et le tiers de la retraite anticipée des assurés handicapés ; le taux de 54 %.
Absents des séries, sans qu'il en manque une : le point de PMI, le plafond de l'inapte,
le RMI, la franchise des arbitres, les barèmes de l'action sociale.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *Le plancher du cumul emploi-retraite à 160 % du SMIC dès 2007.* Lettre ministérielle du
  26 décembre 2006 : l'article 105 de la loi de financement pour 2007 retient, quand le
  dernier revenu « est inférieur à 160% du salaire minimum de croissance », ce montant
  comme plafond, et « les régimes relevant de cet article doivent donc en faire
  application à compter du 1er janvier 2007 », soit « 2007 euros », pour les pensions
  prises depuis 2004 et les arrérages postérieurs au 31 décembre 2006. La fiche
  `cumul_emploi_retraite_et_retraite_progressive` garde le plancher d'un SMIC
  (`part_du_smic: 1.0`, version `plafond_du_dernier_salaire_2004`, bornée par
  `periode.debut` avant 2009) et ne passe à 160 % qu'avec `cumul_liberalise_2009`. Aucune
  fiche ni limite ne cite la loi n° 2006-1640. Deux ans de plancher trop bas pour qui
  reprend une activité à petit salaire.

**Trois candidats plus étroits**, non trouvés déclarés, à trancher au texte.

- *La réversion de 2004 à 2006 sans les réversions des « régimes visés ».* L'annexe 1 de la
  n° 2006/37 distingue « PR V1 = PR réforme 1ère étape (condition de ressources mais
  exclusion des PR des régimes visés) » et « PR V2 = PR réforme 2ème étape (condition de
  ressources y compris les PR des régimes visés) », la seconde pour une réversion ou un
  droit personnel pris après le 1er juillet 2006. Le modèle compte aux ressources, dès
  juillet 2004, les réversions des autres régimes de base (`reversion.yaml`, lignes 1100
  et 1101), sans version coupée en juillet 2006. Reste à lire, au Journal officiel, quels
  régimes le décret n° 2004-858 visait, et jusqu'à quand.
- *La retraite anticipée des assurés handicapés portée au minimum après la majoration.* La
  circulaire RSI n° 2006/055 (2.4.2) : « Lorsque la pension majorée est inférieure au
  minimum contributif [...] celle-ci est portée au montant de ce minimum », comme la fiche
  le dit de D. 351-1-5, II, en 2006 (`retraite_anticipee_handicap.yaml`, lignes 98 à 105).
  Le code compare le minimum au montant calculé seul, puis ajoute la majoration
  (`src/retraite_notionnelle/droit/liquider.py`, lignes 1561 à 1563, d'après la circulaire
  Cnav n° 2026-18), à toutes les dates. La même circulaire majore d'un tiers les points
  d'avant 1973 acquis en situation de handicap (décret n° 73-937, art. 3 quater, II), que
  la fiche ne nomme pas.
- *Le fonctionnaire révoqué avant 2004*, sans droit à pension (anciens L. 58 et L. 59 du
  code des pensions), rétabli au régime général (n° 2006/54) ; et le « reliquat de jours »
  de la fonction publique compté en trimestres cotisés (lettre de la Cnav du 18 août) :
  aucun « révoqu » ni « reliquat » de cette sorte dans les fiches ni les limites ; la
  saisie ne dit ni l'un ni l'autre.

**Un candidat écarté.** Le salaire annuel moyen écrêté au plafond (décret n° 2005-1351),
pour les salaires perçus depuis 2005 et, par la tolérance de la lettre ministérielle du
1er septembre, les pensions prises depuis 2007, quand le modèle écrête tous les salaires
(`salaire_annuel_moyen.yaml`, ligne 18). La n° 2006/58 vise les reports au compte
supérieurs au plafond : plusieurs employeurs, décalages de paie, rappels. Une carrière du
dépôt n'a qu'un salaire par année, cotisé sous le plafond : l'écrêtement ne change rien
avant 2005, comme la LURA le dit (`docs/limites/ecarts-au-droit-positif.md`, lignes 132
à 135).

**Écarts relevés, déjà déclarés.**

- *L'activité de faible importance* (n° 2006/18 et 2006/27) :
  `cumul_emploi_retraite_et_retraite_progressive.yaml`, lignes 295 à 308 ; les assurés
  logés par l'employeur et les activités littéraires ou scientifiques accessoires n'y
  sont pas nommés, même écart.
- *Le plafond de l'inapte* (n° 2006/40, 2 150,20 € par trimestre) : l'écart que la note
  de 2003 a dit neuf.
- *Le SMIC de la date d'effet de la réversion* (n° 2006/69) : `reversion.yaml`, lignes
  1150 à 1157 ; *les seuils des DOM et le quart de part de la CSG* (n° 2006/59) :
  `csg_des_pensions_selon_le_revenu.yaml` ; *le plafond des veuves de guerre* (n° 2006/53
  et 2006/77) : `docs/limites/3-systeme-actuel.md`, lignes 494 et 495.
- *La réversion du régime local d'Alsace-Moselle* (lettre du 23 février) : hors champ,
  `regimes/regime_local_alsace_moselle.yaml`, ligne 18 ; *les cotisations arriérées des
  artistes-auteurs* : `docs/limites/3-systeme-actuel.md`, lignes 316 à 318 ; *le maximum
  avant la surcote* (lettre du 1er septembre) : `pension_maximale_regime_general.yaml`,
  lignes 239 à 246 ; *la retraite anticipée fictive et la réversion sur la pension non
  majorée* : `retraite_anticipee_handicap.yaml`, lignes 312 à 317 ; *l'EEE et la Suisse
  comme un seul accord* : `totalisation_des_periodes_etrangeres.yaml`, lignes 295 à 304 ;
  *le service national des fonctionnaires dans la carrière longue* :
  `carriere_longue_reputes_cotises_autres.yaml`, lignes 195 et 196.

**La suspension de la réversion de 2004**, que les notes de 2004 et 2005 laissent ouverte :
l'annexe 1 de la n° 2006/37 en dit la pratique à la caisse. Une « période transitoire »,
« du 01/07/2004 au 29/03/2005 au RG », où « en raison de la parution tardive des textes,
les anciennes dispositions ont continué à être appliquées » ; ces réversions « ont pu être
révisées pour application de la réforme dès lors que les nouvelles dispositions étaient
plus favorables ». La reprise n'était donc pas générale. Reste à le recouper au Journal
officiel.

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : le Portugal (n° 2006/2), le règlement n° 629/2006, l'accord avec la Suisse,
les arbitres sportifs, les élèves des écoles des armées. En `hors_modele`, quand `limite`
se défendrait : la caisse compétente pour la réversion (n° 2006/48), rangée sous la raison
déjà employée.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2006/18 par la n° 2006/27, elle-même par la
  n° 2017-18 ; la n° 2006/19 par la n° 2006/26 ; la n° 2006/50 par la n° 2018/24 ; la
  n° 2006/58 par la n° 2007/19 ; la n° 2006/60 par la n° 2010/80 ; le point 351 de la
  n° 2006/2 par la n° 2020-12. L'annexe de la n° 2006/46, remplacée par la n° 2006/60, est
  servie dans son ancienne liste.
- Des annexes annoncées et non servies avec leur diffusion : la circulaire DSS n° 367
  (diffusion n° 2006/4), la n° 2005-508 (diffusion n° 2006/1), la n° 2006/372 et ses
  formulaires (diffusion n° 2006/3), servis à part ; la lettre du 23 février (diffusion
  n° 2006/2), servie à part ; les conventions des deux circulaires RSI sur les bateliers,
  non servies ; les taux de change des n° 2006/7, 2006/20, 2006/28, 2006/36, 2006/39,
  2006/56, 2006/62 et 2006/70, renvoyés à la base. Le formulaire SE 130-14 s'arrête sur un
  titre « Instructions » vide.
- Des erreurs : l'exemple de la n° 2006/18 compte avec le SMIC de 2004 au lieu de celui de
  2005 ; l'« Objet » de la circulaire ministérielle n° 2006/249 est celui de la n° 2006/367 ;
  la lettre ministérielle du 13 juillet porte 1992 pour 1994, que celle du 28 septembre
  corrige ; la circulaire RSI n° 2006/055 cite un décret « 2005-1174 » pour 2005-1774 et
  L. 643-3-3 pour L. 634-3-3 ; la circulaire RSI n° 2006/028 est datée du 27 juillet, son
  nom du 26 ; les n° 2006/19 et 2006/26 citent la loi néo-calédonienne sous deux numéros.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les textes que ces circulaires
appliquent n'ont pas été relus au Journal officiel, ni la loi n° 2006-1640, ni le décret
n° 2004-858 ; les moteurs n'ont tourné sur aucun cas.
