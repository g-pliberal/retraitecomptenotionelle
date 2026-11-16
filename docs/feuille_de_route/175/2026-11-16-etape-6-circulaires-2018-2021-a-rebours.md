# Étape 6, circulaires de 2018 à 2021 : la lecture à rebours range les 34 références sans thème de ces quatre années

**Reprise, au 16 novembre 2026.** Une seconde lecture des circulaires sans thème
avance à rebours, de 2026 vers le passé, pendant que la première avance depuis
2008. Ce bloc est le sien ; celui de la lecture chronologique reste sous sa note.
2026 à 2018 sont faites : 63 références, un écart neuf, la revalorisation de 10 %
des salaires de Mayotte. Vient ensuite 2017 : 30 circulaires, dans une session
neuve. Les deux lectures s'arrêtent où elles se rejoignent.
Méthode : celle de la note de 2007, la base relue par l'API, chaque texte lu en
entier, chaque citation retrouvée par script dans le texte servi. Détail ici.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2018 à 2021 : 34 (8 en 2018, 10 en 2019,
  7 en 2020, 9 en 2021).
- *La lecture* : les 34, relues par l'API le 16 novembre 2026
  (`/reference/referencesByFileLeafRef/`), toutes servies, toutes en PDF lus au site
  (`/Pdf/<nom>`) par leur texte (`pdftotext`), lus par la session elle-même, sans agent.
  Une exception à la lecture ligne à ligne : la circulaire n° 2018/6, sur la résidence
  des allocataires du minimum (67 Ko), lue par son plan, ses premières pages et par
  recherche des durées qu'elle fixe. Les citations de cette note ont été retrouvées mot
  pour mot, par script, dans le texte servi (blancs normalisés).
- *Les sorts* : 34 références rangées, 15 `limite`, 19 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 34 lignes, les colonnes
  `sort` et `renvoi` seules). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : les plafonds des veuves de guerre de 2018 (n° 2018/13) ; la
  revalorisation de 2019, « soit un coefficient de 1,003 » (n° 2019/3), et celle de 2020,
  1,01 pour qui touche au plus 2 000 € par mois (instruction n° 2019/266), conformes à
  `legislation/revalorisation_pensions.csv` (lignes 119 et 120) ; les seuils de la CSG de
  2022 (lettre du 20 décembre 2021), 11 431 €, 14 944 € et 23 193 € pour une part,
  conformes à `legislation/csg_pensions_seuils.csv` (ligne 97) ; le relevé de carrière
  (n° 2018/21 et 2019/11, mises à jour de la circulaire n° 2017-01) ; la non-acquisition
  de droits après une première pension (n° 2018/19), que
  `droits_apres_la_premiere_pension.yaml` porte ; la validation du chômage depuis le
  1er novembre 2019 (n° 2020/18), que `chomage_non_indemnise.yaml` et
  `fin_indemnisation_chomage.yaml` portent ; l'activité partielle, « un contingent de
  220 heures indemnisées » par trimestre (n° 2021/6), déclarée non servie
  (`docs/limites/3-systeme-actuel.md`, ligne 375) ; les sportifs de haut niveau (n° 2021/26),
  « limité à 16 trimestres sur toute la carrière », que `sportifs_haut_niveau.yaml` porte ;
  l'accord avec le Canada (n° 2019/33), sa pension globale théorique et sa comparaison
  (« Le montant le plus élevé est servi à l'intéressé. »), que
  `totalisation_des_periodes_etrangeres.yaml` porte ; la résidence des allocataires du
  minimum (n° 2018/6), rangée comme la n° 2019/13 qui la remplace ; les frais de santé
  des pensionnés résidant à l'étranger (instruction n° DSS/DACI/2019/173), que
  `cotisation_maladie_des_non_residents.yaml` porte ; les ressources de la réversion des
  indépendants (circulaire RSI n° 2013/021), `reversion.yaml` ; la prolongation, au-delà du
  31 décembre 2021, de la régularisation des cotisations prescrites des artistes-auteurs
  (lettre du 27 décembre 2021), déclarée hors du modèle.
- *Hors modèle* : les taux de change, trimestre par trimestre (16 circulaires) ; la
  revalorisation de l'allocation supplémentaire d'invalidité et de la majoration pour
  tierce personne de 2019 (n° 2019/14) ; la validité des formulaires après le Brexit
  (lettre du 7 octobre 2020) ; le traitement des réclamations, de la médiation et des
  recours (n° 2020/31 : « Le médiateur ne prend pas de décision. »).

**Les montants relus.** Conformes : les coefficients de revalorisation de 2019 et de 2020 ;
les seuils de la CSG de 2022 pour une part en métropole. Les plafonds des veuves de
guerre ne sont pas dans les séries, comme attendu.

**Aucun écart neuf.** Les règles de cette période sont déjà portées par les fiches ou
déclarées dans les limites.

**Candidats plus étroits**, non trouvés déclarés, à trancher au texte.

- *Le maintien transitoire de la prise en charge des soins des pensionnés résidant à
  l'étranger.* L'instruction n° 2019/173 garde affiliés, au-delà du 1er juillet 2019, ceux
  qui l'étaient déjà : « l'affiliation à l'assurance maladie sera maintenue dès que les
  intéressés bénéficient d'une pension rémunérant une durée d'assurance de plus de dix
  ans en France », et ouvre « une période transitoire de trois ans à compter du 1er
  juillet 2019 » pour ceux de cinq à dix ans. `cotisation_maladie_des_non_residents.yaml`
  (version `quinze_ans_ou_competence_exclusive`) ne lit que les quinze ans de L. 160-3 :
  un pensionné parti avant 2019, avec dix à quatorze ans d'assurance, dans un État sans
  convention, devrait la cotisation maladie que le modèle ne lui retient pas ; sa pension
  nette simulée serait trop haute de 3,20 %. Le maintien vient d'une instruction, non du
  code : à confirmer au texte avant d'y toucher.
- *La fin de la période de surcote à la première pension.* La n° 2018/19 (point 2.3) arrête
  la surcote « au dernier trimestre civil précédant la date de non création de nouveaux
  droits ». `droits_apres_la_premiere_pension.yaml` (lignes 143 à 150) garde à lire « la
  circulaire Cnav qui a appliqué L. 161-22-1 A » et celle qui dirait si les trimestres
  d'après le départ ouvrent la surcote : la n° 2018/19, et la n° 2019/26 qui la remplace,
  sont ces textes.

**Points non tranchés, les sorts retenus.** En `limite`, quand `hors_modele` se
défendrait : la n° 2019/11, qui n'est qu'un sommaire des fiches des parties 2 et 4 de la
circulaire n° 2017-01 (reports de salaire, rachats), et la lettre du 27 décembre 2021,
qui ne fait que prolonger une procédure. En `limite` encore, la n° 2019/33, quand la
n° 2020/17, qui la remplace, a été rangée en `hors_modele` par une lecture de thème :
celle-ci porte les règles de calcul de l'accord, non la seule instruction des demandes.

**Ce que la base sert de travers.**

- Neuf circulaires annulées, servies comme textes vivants : la n° 2018/6, par la
  n° 2019/13 ; la n° 2018/19, par la n° 2019/26 ; la n° 2019/3, par la n° 2020-8 ; la
  n° 2019/14, par la n° 2019/15 ; la n° 2019/33, par la n° 2020/17 ; la n° 2020/18, par
  la n° 2020-25 ; la n° 2020/31, par la n° 2020-36 ; la n° 2021/6, par la n° 2021-17 ; la
  n° 2021/26, par la n° 2023/20.
- La circulaire RSI n° 2013/021 du 13 décembre 2013 est datée par le registre du
  13 décembre 2021, d'où sa place dans cette période.
- La n° 2021/16 est au registre sous le nom `circulaire_cnav_2021_16_200422021.pdf`, d'un
  chiffre de trop.
- La n° 2019/11 garde, en fin de texte, le tableau des modifications de la n° 2018/21.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les lois et décrets que ces
circulaires appliquent n'ont pas été relus au Journal officiel ; les circulaires qui les
remplacent ne sont pas de cette lecture ; les moteurs n'ont tourné sur aucun cas.
