# Les barèmes de l'IPP : seize séries recoupées, cinq écarts neufs, tous à ses torts

**Le 19 octobre 2026 : une ligne réservée (32fd251), puis recoupée.** C'est
la ligne que le bloc « Reprise » désignait, `ipp_baremes_yaml` : les 155
fichiers de `retraites/` des barèmes de l'IPP, à recouper table par table. Le
dépôt YAML n'a pas bougé depuis le commit `fe2cdff` du 21 septembre, celui
que le registre avait comparé le 1er octobre, famille par famille et par
échantillons. La ligne passe à `epuise`, et son accès à `git`.

- *Ce qui reste du recoupement.* `scripts/fetch/ipp_baremes_retraites.py` lit
  le dépôt de l'IPP (575 paramètres, 3 808 marches, dont 1 526 citent leur
  texte) vers `data/brut/`. `controle_recoupement_ipp`, dans
  `scripts/verifier_donnees.py`, y confronte date par date, sans rien
  certifier, seize séries qu'aucun autre contrôle ne recoupait : les
  revalorisations des pensions (99 marches), des salaires portés au compte
  (93 passages d'une colonne à la suivante, depuis celle de 1952) et des
  pensions civiles (6), les durées
  d'avant 2023 et d'avant la suspension, la catégorie active (12), les
  services actifs (12), la surcote (7), l'assiette de l'AVPF (56), et les
  valeurs de service datées de l'Agirc (95), de l'Arrco (21), de l'UNIRS
  (72), de l'Agirc-Arrco (7) et des points d'avant 1973 des indépendants
  depuis 1988 (36 et 35). Les huit marches où les deux lectures divergent
  sont déclarées, chacune à son constat ; une neuve serait SUSPECTE. Le seuil
  des salaires est d'un demi pour mille : la plus petite revalorisation,
  1,001 en 2015, reste au-dessus. Les cas d'essai sont dans
  `tests/test_verification.py`.
- *Ce que l'IPP a de faux* (E11 à E15 au registre, le dépôt ayant raison
  chaque fois). Ses salaires portés au compte omettent deux marches, 1,04 au
  1er juillet 1983 (arrêté du 29 décembre 1982) et 1,013 au 1er janvier 1989
  (loi n° 89-18, article 10), que sa propre série des pensions porte : cumulés
  depuis 1983, ses coefficients restent 5,35 % en deçà de la Cnav, et
  OpenFisca-France-Pension comme TRAJECTOiRE, qui le copient, sont à relire
  sur ce point. À La Réunion, il lit en anciens francs les « 900 F. C. F. A. »
  de 1948 (R. 753-21), la moitié du vrai. Il abaisse au 1er janvier 2014 la
  durée de la fonction publique des générations 1944 à 1948 (151 à 155
  trimestres), ce que L. 13, dans la rédaction de la loi n° 2014-40, ne fait
  pas. Ses points d'avant 1973 des indépendants avancent une date de six
  mois, décalent une valeur d'un an, recopient en 2011 celle des artisans
  chez les commerçants (8,8124 € pour 12,15131 €), perdent un chiffre en 2012.
  Il date d'avril la valeur de l'UNIRS de janvier 1996, et sa colonne « en
  euros » du salaire de référence de l'UNIRS ne convertit pas la nominale,
  de 1949 à 1957. E2 touche aussi le minimum majoré ; l'AVPF de 2014 est
  arrondie à l'euro.
- *Les tables certifiées par ailleurs*, relues une à une le même jour :
  durées, âges, décote, nombre d'années du salaire annuel moyen et taux
  plein par génération, salaire validant (26 années en métropole, 48
  outre-mer), minimum contributif et son plafond, minimum et majoration de la
  réversion, décote de la fonction publique, Ircantec (78 valeurs de service,
  56 salaires de référence), RAFP, points de l'Agirc et de l'Arrco. Tout
  concorde, hors les écarts connus (E2, E3), les séries où l'IPP s'arrête
  (E6, E9) et deux neufs (E12, E13). La garantie minimale de points, que
  l'IPP fait partir de 1947 et le dépôt de l'accord du 8 décembre 1988, avait
  été pesée le 2 octobre (`garantie_minimale_points_agirc.yaml`) : rien de
  neuf. Les complémentaires des artisans et des commerçants (1979-2012), et
  les points d'avant 1973 avant 1988, viennent de l'IPP lui-même : les
  comparer ne vérifiait qu'une copie.
- *La référence de chaque marche* reste au fichier brut. Pour les pensions du
  régime général, l'IPP cite les textes de la colonne `reference` du dépôt
  jusqu'en 2008 (82 marches) ; ensuite l'instruction ministérielle ou la loi,
  quand le dépôt cite la circulaire de la Cnav qui la transmet. Rien ne se
  contredit, rien à reprendre.
- *Ce que le recoupement montre de la table de la Cnav.* Sa colonne du 1er
  juillet 1990 (`revalorisation_salaires_anciennes.csv`) n'est pas un
  multiple de celle du 1er janvier : ses rapports vont de 1,0086 (salaires de
  1954) à 1,0163 (1962), quand la loi n° 90-86 fixe 1,3 % et que toutes les
  autres colonnes sont des multiples à l'arrondi près. Les colonnes
  suivantes en repartent, jusqu'aux circulaires d'aujourd'hui : c'est la
  table de la caisse, que le dépôt suit. D'où vient l'écart n'est pas lu.
- *Ce qui contredit le dépôt : rien.* Ce qui attend le propriétaire : rien de
  neuf. Aucune saisie : le lot n'a pas de simulateur.
- *Ce que le lot suivant trouvera* : dix-huit lignes `a_explorer`. Les deux
  parcours d'Union Retraite (la retraite progressive, l'expatriation) ; neuf
  modèles du registre, dans les zones de 138.3, 138.5, 138.7 et 153 ; F33841
  (138.12) ; le simulateur du COR, fermé ; cinq qui attendent le propriétaire
  (le lot des simulateurs, Légifrance, Gallica).
- *Fichiers.* `scripts/fetch/ipp_baremes_retraites.py`,
  `scripts/verifier_donnees.py`, `tests/test_verification.py`,
  `data/sources_a_explorer.yaml`, le registre (`baremes_ipp` : E2 complété,
  E11 à E15, le bilan et la note), `docs/limites/1-certification.md` et cette
  note. Ni fiche, ni témoin, ni page, ni journal de veille : aucune règle du
  scénario 1 n'a bougé.
