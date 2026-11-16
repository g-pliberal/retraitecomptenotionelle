# Étape 6, circulaires de 2005 : les 66 références sans thème de la douzième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2005 : 66, comme la note de 2004 les
  comptait.
- *La lecture* : les 66, relues par l'API le 16 novembre 2026 à 11 h 34 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies : 54 en page, 12 en PDF lus au
  site (`/Pdf/<nom>`) par leur texte (`pdftotext`), en tout 580 Ko de texte. Un PDF est un
  scan sans texte, le spécimen de l'imprimé de l'ENIM joint à la n° 2005/32 : la session
  l'a lu à l'image, et sa citation n'a pas été vérifiée par script. 26 circulaires de la
  Cnav et 9 de leurs pièces ; 7 circulaires ministérielles et 5 pièces ; 11 diffusions
  d'instructions ministérielles ; 4 lettres de la Cnav, 7 lettres ministérielles.
- *Qui a lu* : les 66 en entier, par quatre agents de la session sur Opus, un lot chacun
  (de 111 700 à 112 200 octets), lancés ensemble, sur une consigne commune (les raisons du
  registre et les renvois déjà employés, avec leur effectif ; les rangements de 2003 et
  2004 pour précédents). Les 65 citations des textes servis ont été retrouvées mot pour
  mot, par script, dans le texte servi (blancs normalisés), chaque raison hors modèle dans
  le registre, chaque renvoi dans le dépôt. La session a relu elle-même les passages et
  les fiches qui décident des écarts (plus bas).
- *Les sorts* : 66 références rangées, 32 `limite`, 34 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 66 lignes, les colonnes `sort`
  et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : la réforme de 2003 mise en œuvre — la retraite anticipée des assurés
  handicapés et les cartes d'invalidité militaires (lettres de la Cnav des 24 février et
  21 mars), la majoration de durée pour enfant handicapé (lettres ministérielles des
  25 janvier, 25 mars et 13 septembre, diffusion n° 2005/15), la surcote (lettre de la
  Cnav du 14 février), l'assurance volontaire et la carrière longue (diffusion n° 2005/11,
  lettre ministérielle du 20 juillet), la retraite progressive et le cumul (diffusion
  n° 2005/13, lettre ministérielle du 27 septembre), les maîtres du privé (lettre
  ministérielle du 4 avril) ; la revalorisation de 2006 (n° 2005/57), les plafonds de la
  réversion (n° 2005/54) et des veuves de guerre (n° 2005/56), les seuils de la CSG de 2006
  (n° 2005/26), la CSG à 6,6 % (diffusion n° 2005/1), la cotisation salariale déplafonnée
  (diffusion n° 2005/6), la cotisation maladie des non-résidents (n° 2005/78, diffusion
  n° 2005/5) ; le trimestre de 2006 (n° 2005/48), le plafond de l'inapte (n° 2005/34) ; les
  périodes des marins signalées par l'ENIM (n° 2005/32 et ses deux pièces), les
  réservistes affiliés rétroactivement (n° 2005/45 et son annexe), l'apprentissage minier
  d'avant 1972 (n° 2005/508) ; le règlement n° 647/2005 (n° 2005/287, diffusion
  n° 2005/10), l'avenant à l'accord avec le Gabon (diffusion n° 2005/9) ; la priorité de
  la CRPCEN pour la majoration pour enfants (lettre de la Cnav du 26 août).
- *Hors modèle* : les monnaies (7) ; le bulletin de paie simplifié (6, la circulaire du
  30 juin, ses quatre annexes et la diffusion n° 2005/16) ; l'action sociale (5) ; les
  conventions bilatérales dans leur gestion (3 : l'Algérie, la Croatie, les formulaires du
  Gabon) ; la législation applicable aux postiers d'Andorre (2) ; le droit des étrangers
  (2) ; les avantages en nature (2) ; et sept autres, une par raison (l'allocation de
  retour à l'activité, le secret professionnel, les sections de la CNAVPL, la lettre type
  aux institutions étrangères, les oppositions sur les pensions, la retenue à la source,
  le paiement aux héritiers).

**Les montants relus, conformes.** Le SMIC de 8,03 € au 1er juillet 2005 ; le trimestre
de 2006, 1 606 € ; le plafond de 2005, 2 516 € par mois ; la CSG à 6,6 %, 6,2 % et 3,8 %,
et le seuil de 2006, 7 286 € pour une part ; le coefficient de revalorisation de 1,018 au
1er janvier 2006 et les coefficients de salaires de 1947 à 2005 ; le minimum contributif,
6 760,82 €, et majoré, 7 172,54 € ; le minimum de réversion, 3 048,20 €, et son plafond,
16 702,40 € ; le versement forfaitaire unique, 139,85 € ; la majoration pour enfant,
86,21 € ; le minimum vieillesse de 2006 ; la cotisation maladie des non-résidents (3,2 %,
4,2 %, 3,9 %, 3,7 %) ; les 168 trimestres d'un départ à 56 ans en 2005
(`legislation/carriere_longue.csv`) ; les taux de cotisation vieillesse de 6,55 et 8,20 %
sous plafond, 0,10 et 1,60 % sur tout le salaire. Absents des séries, sans qu'il en
manque une : la majoration pour tierce personne, les coefficients d'avant 1947.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *Les maîtres du privé entrés au RETREP avant 2004.* Lettre ministérielle du 4 avril 2005,
  aux bénéficiaires du RETREP, du REGREPT et de l'allocation temporaire de l'enseignement
  agricole privé « dont l'avantage temporaire a pris effet avant le 1er janvier 2004 » :
  « je vous demande de neutraliser les nouvelles mesures relatives à l'allongement de la
  durée de référence prise en compte dans le calcul de la pension de vieillesse du régime
  général » ; la pension se proratise sur 150 trimestres, et sur 160 pour ceux nés depuis
  1949 dont l'avantage a pris effet en 2004. Le modèle proratise sur la durée de la
  génération (`legislation/duree_proratisation.csv`), et la fiche
  `retrep_avantages_temporaires`, non modélisée, ne dit pas cette tolérance. L'écart ne
  touche que qui déclarerait un avantage temporaire, que la saisie ne connaît pas.

**Un candidat écarté.** La diffusion n° 2005/13 règle le cumul emploi-retraite du
titulaire d'une retraite progressive par « la mise en paiement de la retraite complète »,
quand la fiche `cumul_emploi_retraite_et_retraite_progressive` se borne sur
`liquidation.date_effet` : la fiche `retraite_progressive` (ligne 22) fait de cette date
celle du départ, « où la pension complète se liquide ». Conforme.

**Écarts relevés, déjà déclarés.**

- *Le plafond de l'inapte* (n° 2005/34, 2 087,80 € par trimestre depuis le 1er juillet
  2005) : l'écart que la note de 2003 a dit neuf, sous l'article R. 352-2.
- *La majoration de durée pour enfant handicapé* (L. 351-4-1), que le modèle ne sert pas :
  `docs/limites/3-systeme-actuel.md`, lignes 416 à 419.
- *La cotisation maladie des non-résidents à 2,8 % jusqu'en 2004*, et la condition des
  quinze ans d'avant 2019, que le modèle ne lit pas (n° 2005/78, diffusions n° 2005/5 et
  2005/15) : l'hypothèse « nette aux règles d'aujourd'hui » de la fiche
  `cotisation_maladie_des_non_residents` (ligne 30).
- *La priorité de la CRPCEN* pour la majoration pour enfants (lettre du 26 août) :
  `priorite_majorations_enfants.yaml`, ligne 205.
- *Les seuils des DOM et les demi-parts de la CSG* (n° 2005/26) :
  `csg_des_pensions_selon_le_revenu.yaml`, lignes 88 à 96 ; *le plafond des veuves de
  guerre* (n° 2005/56) : `docs/limites/3-systeme-actuel.md`, lignes 494 et 495.

**La suspension de la réversion de 2004**, que la note de 2004 laisse ouverte : aucune des
66 ne dit quand ni comment elle a pris fin. Seul indice : la n° 2005/54 applique en
décembre 2005 les plafonds de la réforme (1,6 fois celui d'une personne seule « pour une
personne remariée ou ayant une vie maritale »), la suspension ayant donc cessé avant 2006.
Reste à dire, au Journal officiel, si les réversions du second semestre 2004 ont été
reprises aux règles nouvelles.

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : le règlement n° 647/2005, l'avenant franco-gabonais, l'apprentissage minier
d'avant 1972, les réservistes. En `hors_modele`, quand `limite` se défendrait : le bulletin
de paie simplifié, rangé sous « le droit du travail » comme la circulaire de 2004 qu'il
suit ; les avantages en nature (n° 2005/9, circulaire ministérielle n° 2005/389), rangés
comme ceux de 2004.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2005/20 par la n° 2010/90 ; la n° 2005/10 par la
  n° 2010/32 ; la n° 2005/50 par la n° 2009/49 ; les lettres de la Cnav des 24 février et
  21 mars par la n° 2018/24 ; l'annexe II quater de la n° 2005/45 par celle de la
  n° 2006/16 ; la n° 2005/46, qui annule une première n° 2005-46 du 29 septembre, non
  servie.
- Des annexes annoncées et non servies : les circulaires de la direction de la sécurité
  sociale des diffusions n° 2005/5, 2005/9, 2005/10, 2005/11, 2005/12, 2005/13 et 2005/16 ;
  les 102 questions-réponses de la n° 2005/389, dont le PDF n'a que la lettre de
  couverture ; les taux de change des n° 2005/19, 2005/41 et 2005/47, renvoyés à la base.
- Des erreurs : les annexes 2-1 et 2-2 de la circulaire du 30 juin prennent le plafond de
  2004, 2 476 €, pour assiette des charges plafonnées, au lieu de 2 516 € ; les quatre PDF
  de ces annexes débordent chacun sur la voisine ; la n° 2005/16 calcule ses seuils au taux
  de 2,8 %, périmé en 2005 ; l'annexe de la n° 2005/4 donne treize sections à la CNAVPL, la
  n° 2005/46 onze ; le registre date la n° 2005/56 du 22 décembre, le texte du 26.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les textes que ces circulaires
appliquent n'ont pas été relus au Journal officiel, ni les décrets de la réversion de 2004 ;
les moteurs n'ont tourné sur aucun cas.
