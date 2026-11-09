# Étape 1 : la carte mesurée, le domaine du cumul choisi, la retraite progressive lue dans sa fiche

**La demande.** Le 9 novembre 2026, le propriétaire ouvre le chantier : rendre
les fiches de la carte des règles exécutables, domaine par domaine. Cette
étape mesure, choisit le premier domaine, en convertit une première tranche
et inscrit l'action.

## Ce que le dépôt en disait déjà

Rien ne demande de changer le noyau. Le contrat de la version porte déjà
`contenu`, « paramètres lus, chacun avec sa date qui décide » (annexe C.2) ;
ajouter un paramètre évolue sans décision (§ 13.2) ; la fiche remplace « les
commentaires juridiques du code » (§ 6.5). L'action 130 a confronté le champ
`code` de chaque fiche au dépôt (`130/2026-10-23-carte-des-fiches-code-confronte.md`) :
sa clause des paramètres dit déjà, fiche par fiche, où vit chaque valeur.

## La mesure, au commit 80a32b9

Le moteur lit une fiche par quatre voies, et non deux :

- `versions_des_fiches`, 25 fiches, par les classes d'un domaine
  (`MajorationsPourEnfants`, `Reversions`, `Invalidites`,
  `CarrieresHorsDeFrance`, `CarriereLongue`) ;
- `fiches_datees`, 51 fiches, par `FichesDatees` ;
- une clé du paquet à elle, 3 fiches : `minimum_contributif`,
  `pension_majoree_reference` et `complement_differentiel_rco`, chacune sous
  la clé `fiche` de sa classe (`MinimumContributif.regle`) ;
- les interrupteurs, 49 fiches : une période de régime renvoie à la fiche,
  dont `code.interrupteurs` donne la valeur (`resoudre_les_renvois`,
  `donnees/regimes.py`) ; la date y reste celle de la période, non d'une
  version. 45 de ces fiches ne sont lues par aucune des trois autres voies.

Sur les 272 fiches (263 du droit réel, 9 de la proposition) :

| Domaine | Fiches | Lues par leurs versions | Paramètres non lus | Versions sans paramètres | Sans versions | À interrupteurs |
|---|---|---|---|---|---|---|
| (sans domaine) | 71 | 0 | 1 | 1 | 69 | 23 |
| points | 24 | 3 | 12 | 9 | 0 | 4 |
| age | 22 | 18 | 3 | 1 | 0 | 1 |
| decote_surcote | 22 | 7 | 15 | 0 | 0 | 15 |
| cotisations | 22 | 0 | 12 | 10 | 0 | 1 |
| enfants | 15 | 10 | 2 | 3 | 0 | 0 |
| coordination | 14 | 2 | 1 | 11 | 0 | 0 |
| salaire_de_reference | 14 | 6 | 2 | 6 | 0 | 3 |
| minima | 14 | 11 | 0 | 3 | 0 | 1 |
| duree | 12 | 5 | 2 | 5 | 0 | 1 |
| reversion | 10 | 10 | 0 | 0 | 0 | 0 |
| cumul | 9 | 0 | 9 | 0 | 0 | 0 |
| proposition | 9 | 0 | 0 | 9 | 0 | 0 |
| periodes_assimilees | 8 | 4 | 0 | 4 | 0 | 0 |
| depart_anticipe | 5 | 2 | 0 | 3 | 0 | 0 |
| revalorisation | 1 | 1 | 0 | 0 | 0 | 0 |
| **Total** | **272** | **79** | **59** | **65** | **69** | **49** |

Après l'étape : 80 lues, 58 à paramètres non lus, `fiches_datees` à 52.

## Ce qui contredit les mesures de la demande

- **79 fiches lues, et non 76.** `minimum_contributif` alimente le paquet
  par une autre voie : sa valeur n'est pas écrite deux fois, sauf la règle de
  repli `REGLE_DU_MINIMUM_EN_VIGUEUR`, dans les deux moteurs, qui redit sa
  version `avpf_et_ava_2023`.
- **Les interrupteurs sont une quatrième voie**, que la demande ne compte
  pas : une clé de période n'est pas toujours une seconde source, elle est
  parfois un renvoi à la fiche.
- **71 fiches n'ont pas de domaine**, et 69 pas de versions : elles sont à
  l'ancien contrat, et ne se rangent ni ne se convertissent avant d'y être.
- **Les paramètres déjà portés sont partiels.** Une version n'écrit souvent
  que ce qui change, et renvoie en prose à la précédente (« la version
  tranches_1988 »). `applicable` rendant une version et une seule, chaque
  version doit se suffire : la conversion commence par compléter les
  paramètres. `retraite_progressive` en portait cinq noms, elle en porte
  quatorze.
- **Les trois fonctions géantes ne portent pas tout.** Le domaine choisi vit
  dans des modules à lui : sortir le code d'une fonction géante ne s'est pas
  éprouvé à cette étape.

## Le choix : le domaine `cumul`

Neuf fiches, toutes avec des paramètres sur chaque version, aucune lue. Le
doublon y est le plus net : le code nomme en constantes les identifiants des
versions et recalcule de ses propres dates laquelle vaut. Le risque y est le
plus faible : trois paires de modules hors des fonctions géantes
(`progressive`, 278 et 268 lignes ; `seconde`, 556 et 449 ; `cumul`, 1 228 et
977), loin de la proposition et du coût, où travaille l'action 186.
`decote_surcote`, plus riche (quinze fiches), vit dans `liquider_chaque_regime`
et attend des décisions du propriétaire sur les sections libérales.

## La tranche convertie : `retraite_progressive`

- **La fiche.** Ses huit versions portent tous leurs paramètres : `existe`,
  `age` (et `age_plancher`), `duree_requise`, `fraction` (`par_tranches` avec
  ses `tranches`, ou `complement_de_la_quotite`), `quotite_minimum`,
  `quotite_maximum`, `quotite_des_fonctionnaires`, `regimes_ouverts`,
  `regimes_liquides`, `pension_complete`, `pension_complete_sans_plancher`.
  Les bornes des versions étaient déjà, au jour près, les sept dates du code.
- **Le moteur.** `regle(moteur, date)`, dans `droit/progressive.js` et son
  jumeau, rend les paramètres de la version qui vaut ; `ageMinimum`,
  `dureeRequise`, `regimesOuverts`, `regimesLiquides`, `fraction`,
  `recalculee` et `initiales` y lisent leur valeur, et reçoivent le moteur.
  Sont parties des deux modules : six dates, la table des durées, quatre
  listes de régimes, les seuils et les bornes de quotité. Une valeur que le
  moteur ne connaît pas, ou la fiche absente du paquet, arrête le calcul.
- **Le paquet.** `retraite_progressive` entre à `FichesDatees.NOMS` ; le
  paquet refait ne change que par elle.

## Ce qui est vérifié, et comment

- Le test du portage, `tests/js/retraite-progressive.test.js`, vu rouge sur
  ses sept essais, puis vert ; ses jumeaux de
  `tests/test_retraite_progressive.py`, vus rouges contre l'ancien module.
  Les valeurs attendues sont celles des textes que la fiche cite (R. 351-39,
  R. 351-41, L. 351-15, D. 161-2-24, D. 351-15, décret n° 2025-681).
- Les témoins refaits par le portage (`construire_temoins.py`) : aucun
  fichier ne bouge. Le paquet refait : seule `fiches_datees` change, d'une
  fiche. Les agrégats : identiques.
- `python -m pytest -m rapide` (4 636 passés) ; `tests/test_pont.py -k refait` ;
  `test_liquidation.py`, `test_oracle.py`, `test_destinie.py`,
  `test_estimation_officielle.py`, `test_verification.py`,
  `test_moteur_a_part.py`, `test_carte.py` ; les 145 essais de `tests/js/`.
  La suite complète est à GitHub.

## La trouvaille, gardée et déclarée

Du 18 décembre 2014 au 1er septembre 2023, l'assuré qui travaille aussi dans
la fonction publique l'année de sa demande reçoit les bornes de quotité du
fonctionnaire, de 50 à 90 %, quand R. 351-41 ne connaît que 40 à 80 % et que
le fonctionnaire n'a la retraite progressive qu'en 2023. La conversion garde
ce résultat (`quotite_des_fonctionnaires` de la version
`fraction_complementaire_2014`) et l'écrit aux approximations de la fiche,
effet non mesuré. Au propriétaire : le corriger est une règle du scénario 1.

## Ce que l'étape laisse

- `decote_maximum` reste sans lecteur : aucun code n'écrit la borne de 25 %,
  que l'arithmétique des régimes tient (approximation déjà déclarée).
- Le rebasage de `pousser.sh` garde le `moteur/donnees.json` de `main` : entre l'envoi et la
  fabrique de GitHub, le paquet de `main` n'a pas la fiche, et une retraite
  progressive y arrête le calcul au lieu d'être refusée.
- L'étape 2 et l'ordre des domaines : le bloc de l'action.
