# Le minimum contributif : les régimes alignés réunis, et le montant moyen

**Le 11 octobre 2026 : la série de l'EACR complétée, la part des régimes
alignés et le complément moyen, et la confrontation refaite.**

- *La demande.* Suite de la note du même jour
  (`2026-10-11-minimum-contributif.md`) : certifier le montant moyen du
  minimum servi, que le récupérateur lisait sans que rien le certifie, et la
  part des régimes alignés réunis, le champ de TRAJECTOiRE ; puis opposer
  l'une et l'autre au modèle et à TRAJECTOiRE. Le portail de données de la
  DREES répond aussi aux sessions du cloud : le récupérateur s'y est relancé,
  et la documentation de l'EACR (version du 18 mai 2026) y est jointe au jeu,
  quand le site de la DREES les refuse.
- *Ce que dit la documentation.* La colonne `m1` de la table E-Minima est,
  pour les régimes du privé, le « montant moyen de mico » : le complément que
  le minimum ajoute, en euros bruts par mois, comme tous les montants de
  l'enquête (128 € à la Cnav en 2012, 137,7 € en 2023). La Cnav et la Sécurité
  sociale des indépendants y sont deux régimes jusqu'en 2019, un seul
  ensuite, sous le code 0015, que les données portent dès les liquidants de
  2019 : 32 287 de plus que l'ancien code, dont 32 751 au titre de la
  liquidation unique, ce que la SSI liquidait. La liquidation unique (Lura,
  pensions prenant effet depuis le 1er juillet 2017) explique la hausse de la
  pension moyenne des liquidants de la MSA salariés à partir de 2017.
- *Le montant, certifié.* `regimes/minimum_contributif_montant.csv`, 35
  valeurs de 2012 à 2023, sous la règle des deux codes de la Cnav ; un
  contrôle rejette toute valeur au-delà du plus haut minimum majoré mensuel
  de l'année (`legislation/minimum_contributif.csv`) : la MSA salariés de
  2022, qui recopie l'effectif (13 227 ; 5 771 ; 7 456 pour 741,64 €), et elle
  seule. 2024 n'a pas de montant, l'estimation de la DREES ne portant que
  l'effectif. À la MSA salariés, 34 à 47 € de 2012 à 2017, 74 € en 2018, 95 à
  99 € depuis 2019 : avant la Lura, chaque caisse proratisait son minimum à
  sa part de la carrière, et 96 % de ses liquidants de 2012 étaient
  polypensionnés, dit l'Études et résultats n° 1297 ; depuis, la caisse qui
  liquide sert un seul minimum.
- *Les régimes alignés, depuis 2019.* Une caisse `regimes_alignes` de la
  série existante, 12 valeurs : 20,4 % en 2019, 18,4 % en 2020, 17,95 % en
  2021, 18,9 % en 2022, 18,8 % en 2023, 18,6 % dans l'estimation de 2024 ;
  25,2 % des femmes et 12,2 % des hommes en 2022 et en 2023. La somme des deux
  caisses ne compte des personnes qu'à partir de 2019 : la liquidation unique
  s'installe en deux ans, 19 % du flux de la MSA salariés en 2017, 60 % en
  2018, 72 % en 2019, 76 à 78 % ensuite (modalité `Liq = Lura` du cadrage) ;
  son minimum moyen n'atteint qu'en 2019 son niveau d'après la Lura ; et 2019
  est la première année où la Cnav porte le même code, 0015, indépendants
  compris, au numérateur et au dénominateur. Avant, le numérateur de la Cnav
  vient du code 0015 et son dénominateur de l'ancien : le nouveau compte 3 580
  bénéficiaires de plus que l'ancien en 2016, 5 686 en 2017, 8 496 en 2018 —
  des dossiers traités plus tard, ou les liquidations uniques de la SSI, que
  l'ancien dénominateur ne compte pas. Rien ne le tranche ; la part certifiée
  de la Cnav en 2018 en serait grossie de 1,3 point au plus. La même règle, les
  années où les deux caisses passent le contrôle, donne aux régimes alignés
  un montant moyen pondéré par leurs bénéficiaires (6 valeurs : 133,6 € en
  2023). Le journal de certification a reçu les deux traces seules (142
  séries, 70 326 valeurs), les séries voisines de l'EACR restant identiques ;
  le parcours de présentation suit.
- *Contre le modèle.* `scripts/part_minimum_contributif.py` lit les deux
  fichiers, passe les montants en euros de 2023, et imprime la part des
  régimes alignés, l'écart, et le minimum moyen par année de liquidation. La
  grille élargie surestime la part de 1,9 point en 2019, 3,1 en 2020, 4,0 en
  2021, 4,7 en 2022, 5,8 en 2023, 9,0 contre l'estimation de 2024. Son
  minimum moyen, au-dessus de l'observé jusqu'en 2021 (144 € de 2023 contre
  135), passe dessous en 2022 et en 2023 (123 contre 134) : 104 € pour ses
  femmes, 149 pour ses hommes, contre 138 et 124. La masse par liquidant, part
  fois gain, y est de 30 à 34 € de 2023 par mois de 2019 à 2023, contre 24 à
  28 € observés : un cinquième à près d'un tiers de trop.
- *Contre TRAJECTOiRE.* Recomptée sur les régimes alignés, sa surestimation
  est de près de sept points (25,7 % sans la réforme, pour 18,9 et 18,8 %
  observés en 2022 et en 2023), au lieu de sept à huit contre le seul régime
  général ; onze et demi avec la réforme contre l'estimation de 2024 (30 %
  pour 18,6). Son gain moyen est sous l'observé : 110 € courants de 2024
  avant le relèvement, 108 € de 2023, pour 135 à 139 € observés de 2019 à
  2021 ; 136 € après, 133 € de 2023. La masse par liquidant n'est donc
  surestimée que de 10 à 14 % (27,7 € contre 24,2 et 25,1 € en 2021 et en
  2023). Pour la génération 1975, la grille sert 138 € à ses femmes et 189 € à
  ses hommes, lui 106 et 82.
- *Où c'est écrit.* Les en-têtes des deux fichiers et leurs certifications
  (`scripts/verifier_donnees.py`) ; le registre des modèles (`trajectoire`,
  dernier écart, recompté) ; la limite du coût agrégé, un paragraphe daté,
  déclaré récit ; le manifeste (`drees_eacr`) ; les tests
  (`tests/test_part_minimum_contributif.py`).
- *Ce qui reste.* L'estimation de 2024, part et montant, que la campagne de
  2025 remplacera ; la part de la Cnav en 2017 et en 2018, que les
  liquidations uniques de la SSI grossissent peut-être ; et, pour une
  population (action 136, étape 6), un salaire lié au sexe, que le montant
  réclame autant que la part.
