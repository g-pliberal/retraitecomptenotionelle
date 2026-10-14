# La Cnav et service-public : l'abattement du RCI, et un lot qui concorde

**Le 14 octobre 2026 : vingt-trois lignes réservées puis dépouillées.** Le lot
`a_explorer` que le bloc « Reprise » désignait : quatre circulaires de la Cnav,
sa base de législation, dix pages de son site, sept fiches et une actualité de
service-public, et leurs fiches XML ; réservé par un commit seul (d762465,
dont le message dit vingt-deux lignes pour vingt-trois). La fiche du
micro-entrepreneur (F33841) est laissée `a_explorer` à la session de l'action
138.12. Dix-huit lignes sont épuisées, cinq explorées, ce qui leur reste nommé
dans leur note.

- *Ce qui contredit le modèle : l'abattement du RCI.* La circulaire 2026-07
  (point 4.1.2) publie la retraite d'un artisan né le 30 juin 1962, parti au
  1er janvier 2025 avec 162 trimestres pour 169 : 7 % d'abattement sur ses
  points, ceux du RCO d'avant 1997 comme ceux du RCI. C'est l'annexe 2 du
  règlement (arrêté du 9 février 2012, lue dans l'index LEGI en ses versions
  de 2013 et de 2024) : 1 % par trimestre jusqu'à douze, puis 1,25 %, 22 % à
  vingt — le barème d'anticipation de l'Agirc-Arrco. Les fiches `rci`,
  `rco_artisans` et `nric` y appliquent la décote du régime de base, 1,25 %
  par trimestre : 0,9125 au lieu de 0,93. L'exemple entre au témoin en écart
  connu (`cnav_2026_07_abattement_rci_1962`), déclaré par une fiche neuve,
  `abattement_rci`. Le correctif tient aux données — `abattement_points:
  agirc_arrco` sur les périodes de ces régimes, que `liquider.abattement_points`
  sait déjà lire —, mais il déplace toutes les liquidations d'artisans et de
  commerçants avant le taux plein, et les règlements d'avant 2013 (RCO de 1979,
  NRIC de 2004) ne sont pas lus : une étape à lui.
- *Ce qui concorde, et n'apprend rien de plus.* Les coefficients de report des
  salaires de 1942 à 2025 (circulaire 2025-29), au millième ; les âges et les
  durées par génération, annexes 1 et 3 de la 2026-07 ; minimum contributif,
  majoré et plafond, AVPF, plafonds et minimum de la réversion, ASPA, AVTS,
  majoration pour conjoint, versement unique (2025-29 et 2025-33, déjà lues) ;
  le barème de la CSG des pensions et ses demi-parts (F2971, page de la Cnav) ;
  les années retenues pour le salaire annuel moyen ; le chômage non indemnisé
  (F31249) ; les exemples de F19666, F19643, F21552, F16336 et A15703, déjà au
  témoin et inchangés.
- *Ce que le dépôt en prend.* La durée de référence de la réversion d'un
  défunt né en 1964 ou 1965, lue à la date d'effet de la réversion (2026-07,
  point 4.5), dans l'écart déclaré de la fiche `reversion`. Le barème du
  versement pour la retraite, gelé depuis 2013 (2026-04), et les règles de la
  page des rachats, dans `rachats_et_versements`. Le calcul des parents sur
  vingt-quatre et vingt-trois années, que la Cnav n'appliquera que « courant
  2027 », avec rappel, dans `sam_parents_24_23`. L'allocation veuvage, la
  pension d'orphelin et la rente des ROP, aux limites.
- *Ce qui se contredit ailleurs.* Les identifiants `sp_f21552_enfants_salarie`
  et `sp_f16336_montant_salarie` sont croisés : F21552 est le montant, F16336
  les enfants ; les notes le disent, les identifiants restent. A15703 sert à
  « 140 trimestres cotisés » sur 167 le minimum non majoré, 634,02 €, quand 140
  trimestres cotisés passent le seuil de 120 de D. 351-2-1 : le modèle sert le
  majoré proratisé, 757,79 €, et l'exemple n'entre pas au témoin. F2971 compte
  le seuil du taux médian dans la tranche, la loi l'en exclut. Le fichier de
  taux du simulateur des artistes-auteurs pondère par mois les relèvements de
  l'année, que `taux_cotisation_annuels.csv` date au 1er janvier : en 1991, la
  part salariale plafonnée y vaut 7,60 % quand la moyenne de l'année est 6,64 %.
- *La base de législation.* Son API rend 397 barèmes ; 369 ne sont cités nulle
  part au dépôt. Ceux qui touchent le modèle : les taux de droit commun (2014 à
  2026, conformes), les rachats de cotisations année par année, les salaires
  forfaitaires des apprentis (1948 à aujourd'hui), des artistes, des
  journalistes, des employés de maison, des vendeurs à domicile, l'assurance
  volontaire, le pourcentage de minoration par trimestre, la valeur du point
  RVB des commerçants par rachat global, le plafond de cotisation du RCI.
- *Les fiches XML de service-public.* Leur date de dernière modification
  importante est, pour chaque fiche du lot, le `verifie_le` des exemples du
  témoin : un contrôle de veille qui les compare est possible, et ne s'écrit
  pas ici.
- *Le lot proposé au propriétaire, sans saisie.* Le simulateur des cotisations
  arriérées des artistes-auteurs (`cnav_arrierees_artiste_auteur`, nature
  corrigée en `simulateur`) : trois saisies — une période de trois ans en 1980,
  en 1995 et en 2010, sous le plafond — rendraient le coefficient de
  revalorisation et le taux d'actualisation qu'il applique, que le dépôt ne
  sait pas encore servir. À approuver, ou non.
- *Les pages du site.* Rien dans `pages.js` ni dans la saisie. L'exemple du
  micro-entrepreneur de F23369 (12 100 € de chiffre d'affaires, 3 644,78 € de
  revenu cotisé) est signalé à la session de l'action 138.12.
- *Fichiers.* `data/sources_a_explorer.yaml` ; le témoin ; les fiches
  `abattement_rci` (neuve), `reversion`, `rachats_et_versements` et
  `sam_parents_24_23` ; les limites ; le journal de veille.
- *Reste.* Corriger l'abattement du RCI. Le PDF de la Cnav « vos droits à la
  retraite complémentaire » des indépendants. Les barèmes et les exposés de la
  base de législation. Puis le lot suivant du bloc : le CLEISS.
