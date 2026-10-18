# Étape 9, quatorzième partie : la pension par étage et le revenu autour du départ, les tableaux 1 et 2 de Typfallsmodellen

**La demande.** Le dernier point du chantier « 138.9 » encore `a_reprendre`
au registre, celui de Typfallsmodellen, le modèle des cas types de
Pensionsmyndigheten : « Il rend la pension par étage, avant et après impôt,
en part du dernier salaire, et le revenu autour du départ » ; le taux de
remplacement après impôt était fait depuis le 13 octobre (138.5). La
révision de 2026 du COR, qui attend sa réponse, n'est pas touchée. Session
de la vague 2b du 18 octobre.

**Ce que dit la source, lue le 18 octobre 2026.** Le manuel (PID289138,
version 2.2 du 27 janvier 2025, téléchargé de Pensionsmyndigheten) et le
portage `mathiasboos/Typfallsmodellen` au commit `bb46d93`, cloné dans le
répertoire de travail de la session, hors du dépôt.

- *Le tableau 1* (« Specificerat resultat över slutlön och
  pensionsinkomst », manuel § 2.1 ; `buildTable1` de `result.ts`) : chaque
  étage — inkomstpension, tilläggspension, premiepension, garantipension,
  inkomstpensionstillägg, tjänstepension, épargne privée — en couronnes
  courantes, de l'année de référence, par mois, et en part du salaire de fin
  de carrière, la moyenne des cinq dernières années en prix constants
  (« Average_Earning », 5 par défaut ; « Slutlön, 62 - 66 års ålder ») ; la
  pension après impôt en part du salaire après impôt des mêmes années. Pour
  l'aide-soignante née en 1960 partie à 67 ans : 51,6 % d'inkomstpension,
  10,4 de premiepension, 4,1 de garantie, 2,2 de supplément, 20,1 de
  pension professionnelle, 88,2 au total ; 80,8 % après impôt.
- *Le tableau 2* (`buildTable2`), que ses deux figures dessinent : chaque
  âge de dix ans avant le départ (« Int(par − 10) ») à la fin du modèle, le
  salaire, chaque étage, le brut, l'impôt communal et l'impôt d'État, le
  net, les prestations et le revenu disponible, en prix constants par
  défaut ; les années au-delà de l'espérance de vie sont grisées.

**Ce qui est fait.**

- *Au modèle* (`cycle_de_vie.py`) : `etages_au_depart` range la pension du
  premier mois servi, annualisée (`pension_au_depart`), par étage — au
  scénario 1, chaque régime à son étage du catalogue (la base, la
  complémentaire, l'intégré), sa part de la majoration pour enfants
  comprise, le RAFP servi à part comme ailleurs dans le module ; un système
  notionnel à son compte (`notionnel`), le scénario 6 à son pilier
  (`capitalise`) ; une réforme prospective, à qui part avant elle, aux
  étages du scénario 1. `pension_par_etage` en fait le tableau 1
  (`PensionParEtage`) : chaque étage en part du dernier revenu annualisé,
  le brut, qui est le taux de remplacement du simulateur, la pension nette
  des prélèvements de l'année du départ sur le dernier revenu net, et, sous
  l'impôt, la pension après l'impôt d'une année entière d'elle seule sur le
  dernier revenu après impôt, le taux net de l'OCDE, que
  `_pension_apres_impot` calcule désormais pour les deux.
  `revenus_autour_du_depart` en fait le tableau 2 (`AnneeAutourDuDepart`) :
  de dix ans avant l'année du départ à dix ans après, en euros de l'année du
  départ, le revenu d'activité, la pension des mois servis, leur net,
  l'impôt du foyer de l'année et ce qu'il laisse.
- *Au portage* (`cycle-de-vie.js`) : leurs jumeaux, `etagesAuDepart`,
  `pensionParEtage`, `revenusAutourDuDepart`, rejoués contre le Python sur
  les sept carrières de la concordance, les six systèmes pour le premier,
  le scénario 1 et le 6 pour le second.
- *Aux cas types* : `python scripts/cycle_de_vie.py --etages [--impot]`
  imprime, système par système, un tableau des treize cas types sur les sept
  générations par étage servi, puis les trois taux de remplacement
  (`scripts/cycle_de_vie.mjs`, mode `etages`). Pour la génération 1960, au
  scénario 1 : le salarié au salaire moyen, 44,0 % de base et 15,8 de
  complémentaire, 59,7 en tout ; le cadre, 17,6 et 24,4 ; le fonctionnaire
  sédentaire, 61,5 d'intégré ; la profession libérale, 8,8 et 21,3.
- *Les tests* : dans `tests/test_cycle_de_vie.py`, l'exemple du manuel
  refait au dixième de point, les étages de chaque système, les trois taux,
  les vingt et une années autour du départ du salarié né le 15 janvier
  1980, parti en février 2044 — onze mois de pension l'année du départ, puis
  chaque année, en euros de 2044, la pension du départ ; la concordance dans
  `tests/test_cycle_de_vie_portage.py` ; les cas types et le tableau
  imprimé dans `tests/test_cycle_de_vie_script.py`. Chacun vu rouge avant
  son code.
- *Le registre* : le point de Typfallsmodellen est `repris`.

**Ce que le dépôt fait autrement, et le dit.** Sa pension n'a ni l'ASPA ni
la garantie vieillesse, que l'impôt finance, comme les autres indicateurs du
module, quand Typfallsmodellen compte sa garantipension ; son dernier revenu
est celui de la dernière année cotisée, annualisé, comme son taux de
remplacement, quand Typfallsmodellen moyenne les cinq dernières années. Son
tableau 2 s'arrête dix ans après le départ ; `annees` le mène plus loin.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La révision de 2026*, à la réponse du COR (note du 18 octobre, « la
   révision de 2026 »), inchangée.
2. Inchangés : la rémunération moyenne par tête du COR, à la session des
   données ; le rendement de −2,9 % du cadre né en 1975 sous le scénario 2.

**Pour les pages** (la session du site). La page des résultats peut montrer,
pour la carrière saisie, la pension du départ par étage en part du dernier
revenu, à côté du taux de remplacement, et le revenu des dix années de part
et d'autre du départ : `pensionParEtage` et `revenusAutourDuDepart`, du
portage, avant ou après impôt.
