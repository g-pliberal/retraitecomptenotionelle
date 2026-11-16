# Étape 6, circulaires de 2017 : la lecture à rebours range les 30 références sans thème de l'année

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2017 : 30, dont 19 fiches de la circulaire
  carrière n° 2017/1.
- *La lecture* : les 30, relues par l'API le 16 novembre 2026
  (`/reference/referencesByFileLeafRef/`), toutes servies (la fiche 4.3, refusée une fois,
  l'a été au second appel), toutes en PDF lus au site (`/Pdf/<nom>`) par leur texte
  (`pdftotext`), 327 Ko en tout, lus en entier par la session elle-même, sans agent. La
  lettre ministérielle du 28 septembre 2017 est un scan, lu par sa reconnaissance de
  caractères, imparfaite : on n'en cite rien. Les citations de cette note ont été
  retrouvées mot pour mot, par script, dans le texte servi (blancs normalisés).
- *Les sorts* : 30 références rangées, 26 `limite`, 4 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 30 lignes, les colonnes
  `sort` et `renvoi` seules, chaque renvoi trouvé dans le dépôt par script). Aucune
  raison neuve.

**Par ce qu'elles disent.**

- *Les fiches de la circulaire carrière n° 2017/1*, rangées comme leurs versions
  courantes, déjà au registre : les anciennes versions (« V1 ») des fiches 3.6 (Accre),
  3.16 (service national), 3.17 (périodes de guerre), 3.29 (périodes indemnisées par la
  Caisse des Français de l'étranger), 6.2a et 6.2b (majorations pour enfants), toutes
  « Remplacée par la circulaire Cnav 2018-21 du 22/08/2018 » ; les principes (1.1, 6.1) ;
  le chômage indemnisé (3.2), réputé cotisé pour la carrière longue « dans la limite de
  4 trimestres », que `carriere_longue_reputes_cotises_autres.yaml` porte ; le chômage non
  indemnisé (3.3), « dans la limite d'un an et demi, sans que plus de six trimestres
  d'assurance puissent être comptés à ce titre », que `chomage_non_indemnise.yaml` porte ;
  les six rachats (4.1 à 4.6 : affiliation tardive, anciens détenus, activité hors de
  France, rapatriés, indemnité de soins aux tuberculeux, tierce personne) et la
  régularisation de l'apprentissage d'avant le 1er juillet 1972 (4.12), que les limites
  déclarent (`3-systeme-actuel.md`, « rachats et versements ») ; la majoration du compte
  professionnel de prévention (6.6 et son ancienne version), « Un trimestre de majoration
  de durée d'assurance correspond à 10 points », déclarée dans les limites et lue par
  `carriere_longue_reputes_cotises_autres.yaml`.
- *En `limite`, le reste* : la non-acquisition de droits après une première pension
  (n° 2017/19), que la n° 2018/19 remplace et que `droits_apres_la_premiere_pension.yaml`
  porte ; l'accord avec le Brésil (n° 2017/23), sa pension globale théorique et sa
  comparaison (« Seul le montant le plus élevé est servi à l'intéressé. »), rangé comme
  la n° 2019/24 qui la remplace ; les plafonds des veuves de guerre de 2017 (n° 2017/28),
  comme ceux de 2018 ; la retraite progressive des salariés de plusieurs employeurs au
  1er janvier 2018 (n° 2017/43), dont la décote bornée (« le coefficient de minoration du
  taux plein (50 %) ne peut excéder 25 % ») et le plancher de la pension définitive, que
  `retraite_progressive.yaml` porte ; la revalorisation du 1er octobre 2017 (instruction
  n° DSS/SD3A/2017/272), « revalorisées du coefficient de 1,008 au 1er octobre 2017 » ; le
  barème progressif de la surcote de 2007 (circulaire RSI n° 2007/023), 0,75 %, 1 % puis
  1,25 % après soixante-cinq ans, que `surcote_regime_general.yaml` porte ; la commission
  nationale qui valide rétroactivement des périodes de handicap pour la retraite anticipée
  (lettre ministérielle du 28 septembre 2017), que `retraite_anticipee_handicap.yaml`
  déclare non représentée.
- *Hors modèle* : les taux de change des quatre trimestres de 2017 (n° 2017/2, 2017/16,
  2017/26, 2017/33), sous la raison déjà employée.

**Les montants relus.** Conforme : le coefficient de 1,008 au 1er octobre 2017
(`legislation/revalorisation_pensions.csv`, ligne 118). Les plafonds des veuves de guerre
ne sont pas dans les séries, comme attendu.

**Aucun écart neuf.** Les règles de cette année sont portées par les fiches ou déclarées
dans les limites. Un point seulement, non un écart : la retraite progressive de plusieurs
employeurs fait la somme des quotités (n° 2017/43, point 2.3.2) ; la saisie, qui ne dit
qu'une quotité, la reçoit déjà sommée.

**Ce que la base sert de travers.**

- Des textes annulés servis comme vivants : les n° 2017/19 (par la n° 2018/19), 2017/23
  (par la n° 2019/24), 2017/43 (par la n° 2018/31), et les fiches « V1 », que la base sert
  à côté de leur version courante, comme la fiche 6.6.
- La circulaire RSI n° 2007/023 du 15 février 2007 est datée par le registre du
  15 février 2017, d'où sa place dans cette période.
- La fiche 6.6 courante, quoique datée du 13 janvier 2017, est « Mise à jour par la
  circulaire Cnav 2018/21 du 22 août 2018 ».

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les lois et décrets que ces
circulaires appliquent n'ont pas été relus au Journal officiel ; les moteurs n'ont tourné
sur aucun cas.
