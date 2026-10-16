# Étape 9, suite de la huitième partie : la maladie des pensions de la SNCF et des mines, sur la fiche de paie du site et sous le plafond de 2010

**La demande.** Vague bis du 16 octobre 2026, session 6 sur 13 : le point 1
de « Ce qui reste » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`) — la cotisation
maladie des pensions de la SNCF (0,70 %) et des mines (0,50 %), que la fiche
de paie du site ne prélevait pas, et le plafond de la SNCF dans l'histoire.
Les pages (`pages.js`) étaient à la session 1 : rien n'y est écrit.

**Ce que disent les textes, relus le jour même dans les index de la DILA.**

- *La SNCF* : « 0,70 % du montant trimestriel de la pension inférieur à un
  plafond fixé à 5 128 euros » (décret n° 2007-1056, art. 7, IV), rédaction
  du décret n° 2010-1362 du 10 novembre 2010 (art. 3, JORFARTI000023036949),
  en vigueur le 14 novembre ; inchangée dans toutes les versions de LEGI
  jusqu'à celle du 3 août 2025 (LEGIARTI000052041125). Le VII, que la
  huitième partie n'avait pas lu : les plafonds sont « réduits de moitié
  concernant les titulaires d'une pension de réversion et revalorisés dans
  les mêmes conditions que les pensions ». Les 5 128 € sont donc ceux de
  2010, et non ceux d'aujourd'hui.
- *Les mines* : 0,50 % des pensions de vieillesse, d'invalidité et de
  réversion « ainsi que leurs avantages accessoires », sans plafond (décret
  n° 46-2769, art. 91, 3°, a, LEGIARTI000037456798).
- *Les exonérations* : R. 711-15 (LEGIARTI000006752049) donne aux pensionnés
  des régimes spéciaux celles du régime général, D. 242-9 : sous le seuil du
  taux réduit de CSG et pour l'allocataire de l'ASPA, comme la cotisation des
  complémentaires.
- *Le non-résident* paie d'autres taux : 3,90 % sous le plafond et 3,20 %
  au-delà à la SNCF (art. 7, IV, second alinéa), 3,70 % aux mines.
- *Le plafond revalorisé* : ni la CPRP SNCF ni l'IPP ne le publient (la
  table « cotisations du secteur public, SNCF » de l'IPP n'a que les taux
  des actifs) ; le dépôt le calcule du texte.

**Ce qui est fait.**

- *La donnée* (`prelevements_remuneration.yaml`, `pensions`) :
  `maladie_regimes_speciaux`, la SNCF à 0,70 % sous 25 582 € par an en 2026
  — 4 × 5 128 € multipliés par chaque revalorisation de L. 161-23-1 depuis le
  14 novembre 2010 (1,2472 ; la tranche de 2020, 1 %, d'une pension
  mensuelle de la taille du plafond, 1 827 €) — et les mines à 0,50 %.
- *Le modèle* (`remuneration.py`, `contexte.py`, et leurs jumeaux) :
  `MaladieRegimeSpecial`, et `Montants`, dont le taux de la personne prend la
  cotisation sur la part de sa pension du scénario 1 que ces régimes servent,
  sous le plafond, à la tranche du foyer ; `pension_du_regime` la prend sur la
  seule ligne de son régime, au plafond de moitié avec `reversion` ; un autre
  départ (`net_d_un_depart`) garde la part du sien. Le non-résident ne la
  paie pas.
- *L'histoire* (`maladie_des_pensions.py`, `prelevements_historiques.yaml`) :
  la série `maladie_sncf` s'arrête le 14 novembre 2010, et
  `maladie_sncf_sous_plafond` prend le relais, sur la part de la pension sous
  le plafond — la pension du départ menée par les prix en euros de 2026,
  année du plafond, les deux suivant ensuite les mêmes revalorisations
  (`_parts_assujetties`, avec l'année de la liquidation).
  `taux_de_prelevement` y ajoute la SNCF et les mines : l'année courante est
  de nouveau la dernière marche de l'histoire.
- *Les tests* : `test_prelevements_historiques.py` (l'agent de la SNCF, le
  plafond refait de `revalorisation_pensions.csv`, la fiche de paie du site,
  le relais des deux séries) ; `test_net_pensions.py`, les deux moteurs sur
  cinq pensions. `cycle-de-vie.js` retrouve le Python à l'identique sur un
  agent parti en 2000 au double du salaire moyen (vérifié à la main, hors de
  la suite : `test_cycle_de_vie_portage.py` était à la session 2).

**Ce que montrent les mesures** (scénario 1, taux plein, prélèvements de
l'année) :

- *L'agent de la SNCF* né en 1935, parti à 55 ans en 1990 au salaire moyen :
  97,4 % de sa pension sous le plafond, 9,78 % de prélèvements depuis 2011
  au lieu de 9,80 %. Au double du salaire moyen : 48,7 %, 9,44 %.
- *La huitième partie* comparait la pension de 2026 (25 282 €) au plafond
  de 2010 (20 512 €), et concluait qu'on prélevait 0,70 % de tout quand le
  texte n'en prendrait que 0,57 % : revalorisé, le plafond (25 582 €) couvre
  presque toute cette pension.
- *Le site* : un agent né en 1965, parti à 57 ans au triple du salaire
  moyen, paie 9,1 % et une cotisation de moins de 0,70 % de sa pension. Les
  témoins, en brut, ne bougent pas.

**Ce qui reste.**

1. *À une session des pages* (`moteur/js/pages.js`) : passer
   `reversion = true` à `montants.pensionDuRegime` dans la réversion (vers la
   ligne 5270), pour le plafond de moitié ; et, dans `compositionActuelle`,
   l'assiette de la SNCF et des mines de chaque étage, que `netDAssiette`
   prend jusque-là au prorata du montant — exact sur le total, approché d'un
   étage à l'autre pour qui a aussi une complémentaire.
2. *Le non-résident* de la SNCF et des mines, à ses taux de L. 131-9.
3. *Les avantages accessoires* des mines, dont la majoration pour enfants,
   que le dépôt laisse hors de l'assiette, comme pour les complémentaires.
4. *Le plafond de 2027*, à refaire au 1er janvier avec la revalorisation :
   `test_le_plafond_de_la_sncf_est_celui_du_texte_revalorise` le réclame, et
   une valeur publiée par la caisse, si elle se trouve.
5. *Inchangés*, de la huitième partie : les décrets au fac-similé, au
   propriétaire ; ce que les textes ne disent pas ; la limite 5 ante ter (2).
