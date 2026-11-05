# Corrections de la relecture R-D : le plafond de la caisse de Mayotte, et une présomption plus prudente de 2012 à 2018 (file D-bis)

*Le 5 novembre 2026, file D-bis de la vague 7, sur Opus.* La relecture R-D
(`2026-11-05-relecture-independant-de-mayotte.md`) avait trouvé le taux de
l'indépendant de Mayotte conforme et son assiette fausse : un écart grave, un
moyen, trois faibles. Les cinq sont fermés, en deux commits : 337c5d9 (le
plafond) et bc608e4 (la présomption de 2012 à 2018). `veille_droit.py` lancé ;
l'index LEGI récupéré, puis mis à jour au 4 novembre 2026.

**Les textes, relus dans l'index.**

- Ordonnance n° 96-1122, article 28-1, I, dans ses quatre rédactions
  (LEGIARTI000025018554 du 1er janvier 2012, LEGIARTI000025023101 du
  1er janvier 2015, LEGIARTI000031324363 du 16 octobre 2015,
  LEGIARTI000051284545 du 28 février 2025) : « Il est créé un plafond de
  cotisations de sécurité sociale à Mayotte. Il est fixé à intervalles qui ne
  peuvent être inférieurs au semestre ni supérieurs à l'année, dans des
  conditions prévues par décret. Son montant, calculé selon des règles prévues
  par décret, est arrêté par le ministre chargé de la sécurité sociale. »
- Article 28-2, I, 1° (LEGIARTI000025018560, depuis le 1er janvier 2012) : les
  cotisations « assises sur les rémunérations et revenus d'activité définis à
  l'article 28-1, dans la limite du plafond prévu au deuxième alinéa du I de
  l'article 28-1, qui sont dues par tout employeur […] et par tout assuré,
  ainsi que par les travailleurs indépendants agricoles et non agricoles » ;
  son II : « Un décret fixe les taux des cotisations prévues au 1° du I ».
- Décret n° 2011-2085, article 4-2, I (LEGIARTI000038680068,
  LEGIARTI000053297541) : l'assiette « dans la limite du plafond prévu au I de
  l'article 28-1 ».
- Article 4, rédaction du 1er janvier 2012 (LEGIARTI000025097520) : « Le taux
  des cotisations mentionnées aux articles 28-2 […] ANNÉE civile COTISATION AU
  RÉGIME d'assurance vieillesse obligatoire de base […] Salariale Patronale
  […] 2012 4,11 % 9,90 % » ; rédaction du 21 octobre 2012
  (LEGIARTI000026514552) : « 2012 4,00 % 9,90 % », « 2013 4,11 % 9,90 % », …,
  « 2018 4,66 % 9,90 % », sans note qui en fasse remonter l'effet ; la
  rédaction de 2026 (LEGIARTI000053469930) ne couvre que 2026 à 2036.
- Le plafond de la caisse, `legislation/mayotte_smig_et_plafond.csv`, relu à
  sa source : `scripts/fetch/cnav_mayotte.py` relancé sur le barème « Salaire
  plafond - Mayotte » de la Cnav, le fichier reste identique (13 860 € en 2012,
  20 328 € en 2018, 21 768 € en 2019, 23 208 € en 2020, 31 728 € en 2024,
  36 264 € en 2026).

**1. Le plafond (grave), commit 337c5d9.** Les deux moteurs bornaient la
cotisation de l'indépendant au plafond de la Sécurité sociale. Ils prennent
désormais, pour l'assuré sans employeur de `cssm_mayotte`, le plafond de la
caisse (`plafond_de_cotisations(annee, mayotte=True)`), au compte
(`_bornes_proratisees`, `_bornesProratisees`) et dans la fiche de paie
(`bloc_droit_en_vigueur`, `blocDroitEnVigueur`). Depuis 2012 : l'article 28-2
borne déjà les cotisations des indépendants, et le statut n'existe pas avant.
Valeurs attendues, posées à la main et vues rouges avant le code :

- 30 000 € en 2020 : 23 208 × 6,55 % = 1 520,124, soit 1 520,12 € (rendu avant :
  30 000 × 6,55 % = 1 965 €), au compte et sur la fiche de paie, dans les deux
  moteurs ;
- 50 000 € en 2024 : 31 728 × 9,35 % = 2 966,568, soit 2 966,57 € (avant :
  46 368 × 9,35 % = 4 335,41 €).

**2. La présomption de 2012 à 2018 (moyen), commit bc608e4.** Aucun texte lu ne
donne à l'indépendant un taux propre avant 2019. L'ancienne présomption, la
série du régime général (14,95 % à 15,45 % sous le plafond, plus 1,70 % à 2,30 %
sur la totalité), dépassait toute lecture de l'article 4 et cotisait au-dessus
du plafond, que l'article 28-2 exclut. La nouvelle, la plus prudente que les
textes permettent : la somme des parts salariale et patronale que l'article 4
fixe à la vieillesse de base, sous le plafond de la caisse, rien au-dessus.
Elle prend le taux que l'article 4 fixe à la cotisation que l'article 28-2 met
à la charge de l'indépendant, seul débiteur faute d'employeur, sans y ajouter
le partage entre deux débiteurs qu'aucun texte ne lui applique. **Ce que les
textes ne tranchent pas, et qui reste présumé** : l'indépendant pouvait ne
devoir que la part salariale (4,00 % à 4,66 %), que la patronale (9,90 %), ou
rien avant l'article 4-2 ; la somme est le plus haut de ces taux, et aucun ne
la dépasse. Elle est versée au niveau `estimee`, et la fiche la déclare
(`supposee`, fiabilité faible, `a_relire`). Pour 2012, la rédaction en vigueur
le 31 décembre, celle du 21 octobre : la cotisation de l'indépendant est
annuelle, sur le revenu de l'année ; la rédaction du 1er janvier écrivait
4,11 %, en vigueur du 1er juillet, date de l'affiliation, au 21 octobre, et la
fiche le déclare (écart faible a). À la main :

| Année | Part salariale + patronale | Taux |
|---|---|---|
| 2012 | 4,00 % + 9,90 % | 13,90 % |
| 2013 | 4,11 % + 9,90 % | 14,01 % |
| 2014 | 4,22 % + 9,90 % | 14,12 % |
| 2015 | 4,33 % + 9,90 % | 14,23 % |
| 2016 | 4,44 % + 9,90 % | 14,34 % |
| 2017 | 4,55 % + 9,90 % | 14,45 % |
| 2018 | 4,66 % + 9,90 % | 14,56 % |

- 10 000 € en 2012 : 10 000 × 13,90 % = 1 390,00 € (avant : 10 000 × 14,95 % +
  10 000 × 1,70 % = 1 665 €) ;
- 30 000 € en 2018 : 20 328 × 14,56 % = 2 959,7568, soit 2 959,76 € (avant le
  commit 337c5d9 : 30 000 × 15,45 % + 30 000 × 2,30 % = 5 325 €).

Le récupérateur `scripts/fetch/dila_legi_taux_mayotte.py` lit aussi l'article 4
(deux premières colonnes de son tableau, qui doit ouvrir sur la vieillesse de
base et ses deux parts) ; il rend, sur l'index, les sept valeurs ci-dessus,
toutes de LEGIARTI000026514552. `verifier_donnees.py` les verse par une
certification à part, `taux_cotisation_mayotte_presume`, niveau `estimee` : 14
valeurs ajoutées. Le même passage date le journal de certification du jour : le
commit de la file D l'avait laissé au 3 novembre sous une série vérifiée le 5,
ce que `test_journal_de_certification_est_lisible` voyait rouge.

**3. Les écarts faibles.** a) 4,11 % en 2012 : déclaré, ci-dessus. b) La ligne
`manque` de `cssm_mayotte.yaml` dit le plafond et le taux de chacun, et le
commentaire de `TAUX_ALIGNES` (`verifier_donnees.py`) dit ce que le dépôt lit de
l'article 4. c) Les tests voient le plafond : quatre tests neufs se placent
au-dessus du plafond de la caisse, dans les deux moteurs, et un cinquième voit
que la table dit `estimee` de 2012 à 2018.

**Ce qui bouge.** Aux témoins, depuis e0ccbf9 : aucune pension du scénario 1 ;
aux scénarios 2 et 4, les cinq indépendants de Mayotte baissent, de −2,92 %
(`independante_mayotte_assiette_minimale`, sous le plafond, par le seul taux de
2012 à 2018) à −63,40 % (`statut_independant_mayotte_1955`, dont le compte ne
porte que 2012 à 2018) ; −14,15 % pour `statut_independant_mayotte`, −23,02 %
pour celui né le 20 septembre 1968, −33,74 % pour celui né en 1965 ; au scénario
6, le seul témoin de 1955, −63,40 %. Le plafond seul en faisait −11,54 % à
−48,84 % sur quatre témoins. Le compte du témoin né en 1965 reçoit 16 911,01 €
de 2012 à 2018 au lieu de 44 903,58 €, et 19 353,01 € de 2019 à 2026 au lieu de
29 034,54 € (2019 : 21 768 × 5,85 % = 1 273,43 € ; 2026 : 36 264 × 10,75 % =
3 898,38 €). Aucun témoin du salarié de Mayotte ne bouge. Le rendu `methode`
compte une série et quatorze valeurs de plus. Le coût : les chiffres ancrés du
README, refaits sur le dépôt après les deux commits, rendent 2 763 Md € au lieu
de 2 762 au scénario 2, et 6 386 au lieu de 6 385 aux scénarios 4 et 6 ; ces
ancres datent de la dernière course de GitHub, que d'autres commits déplacent
aussi : la part de ces deux commits n'est pas isolée. GitHub les refait.

**Vu en chemin, non corrigé : l'erreur de classe.** Le salarié de Mayotte
cotise encore sous le plafond de la Sécurité sociale, quand l'article 28-2,
relu ici dans sa rédaction de 2012, le borne depuis le 1er janvier 2012 au
plafond de la caisse, et à la série du régime général, quand l'article 4 lui
donne ses deux parts. Hors de la zone de cette file ; inscrit au bloc
« Reprise ».
