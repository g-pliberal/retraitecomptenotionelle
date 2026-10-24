# La carte des fiches : le code des cotisations, des cultes et des durées, écrit

**La demande.** Vague du 24 octobre 2026, quatrième salve : le propriétaire
demande une session par tâche qui se mène sans lui, et dix tournent ensemble.
Celle-ci, de l'action 130 : un quatrième lot des 12 fiches que `EN_PROSE`
(`tests/test_carte.py`) tient encore à leur seule phrase `moteur`, hors de
celle de l'action 131, jusqu'à ce que le test confronte leur code au dépôt
comme celui des autres. Aucun chiffre du modèle ne bouge : seuls changent les
champs `code` et `regimes` de onze fiches, `EN_PROSE`, et l'outil qui lit
leurs paramètres.

## Ce qui est fait

- **Les onze fiches**, de 12 à 1, vu rouge — `EN_PROSE` réduit à
  `pension_non_salaries_agricoles_2026`, le test rougissant de quarante-deux
  écarts, quatre par fiche, moins deux pour les deux fiches qui nommaient déjà
  leurs tests —, puis écrites et vertes. Les cotisations et les points :
  l'assiette minimale des exploitants (`acquerir`, `points_msa`,
  `assiette_du_collaborateur`, `PeriodeRegime.repere_assiette`,
  `ConstructeurCompte._cotisation_ligne`) ; les classes des trois
  complémentaires libérales (`ClassesCotisation`, le compte, et la conversion
  du net au brut, `bloc_droit_en_vigueur`) ; la classe spéciale du RAAP ; le
  prorata des points de la CNAVPL ; la retraite proportionnelle agricole — son
  barème, son plancher de seize points, le forfait du collaborateur, son
  coefficient de durée, l'AVTS de R. 732-70 (`MinimumContributif.avts`), les
  années de chef à titre secondaire (`annees_hors_forfait`) — ; le forfait des
  cultes, au salaire annuel moyen de la CAVIMAC (`assiette_de_reference`) et à
  l'Arrco des ministres rémunérés, leur routage et la contribution d'équilibre
  sur le forfait compris. Les quatre sans interrupteur : la date d'effet au
  mois suivant (`origine_des_ages`, les âges de `Carriere`, la présomption du
  jour de naissance au vocabulaire), le temps partiel des fonctionnaires (la
  saisie, la chronologie, la quotité de la ligne, les services, le traitement
  à temps plein ; `aucun` paramètre), les trimestres d'avant 1972 et les
  trimestres retenus de 1972 à 1974 (`liquider_chaque_regime`).
- **Le champ `regimes`** : pour les sept fiches à interrupteur, les régimes
  dont les périodes renvoient à elles ; pour les quatre autres, lu à la règle
  et au code — le régime général, les salariés agricoles et les assurances
  sociales pour les trimestres d'avant 1972 ; le régime général et les
  salariés agricoles pour 1972 à 1974, que leurs périodes bornent ; l'État, la
  CNRACL et le FSPOEIE pour le temps partiel, comme le décompte des services ;
  les 80 régimes que le catalogue calcule pour la date d'effet, que le modèle
  donne à toute pension. La carte passe de 758 manques à 747 ; ses 106 fiches
  à mûrir restent.
- **L'outil** (`tests/outils_carte.py`) lisait tout YAML de `regimes/` comme
  une fiche de régime : les époques des classes,
  `regimes/classes_cotisation_epoques.yaml`, que le catalogue range à part
  (`FICHIERS_HORS_REGIMES`), ne pouvaient se nommer. Il les lit comme une
  donnée, d'abord vu rouge par un cas de plus de
  `test_le_code_d_une_fiche_se_confronte_au_depot`.
- **Les tests nommés** : ceux qui tiennent la règle, et
  `tests/temoins/simulations.json` avec `tests/js/moteur.test.js` là où des
  témoins la suivent. Une sonde de session, hors du dépôt, a ôté chaque
  interrupteur d'une copie des données et rejoué en Python les témoins dont le
  résultat nomme ses régimes : 6 sur 6 changent sans le forfait de l'Arrco des
  cultes, 18 sur 18 sans celui de la CAVIMAC, 32 sur 32 sans les classes, 22
  sur 22 au RAAP, 15 sur 17 sans le barème agricole, 80 sur 109 sans le
  prorata de la CNAVPL. Un témoin de chacune de ces six fiches, lu au détail
  de sa pension, le montre : `statut_artiste_auteur` a ses 120 points de classe
  spéciale, vingt années à six, `statut_exploitant_agricole` ses points
  multipliés par 37,5 / 43, 0,872093. Aucun des 17 témoins agricoles n'atteint l'assiette minimale, que
  `test_simulateur.py` confronte dans les deux moteurs aux 133 points de la
  RCO du chef à 12 000 € ; aucun ne liquide de 1972 à 1974 une pension que le
  plafond borne, et aucun cas n'y confronte le portage. Les deux fiches le
  disent.

Les champs de classe ne sont pas nommés (`AnneeCarriere.outre_mer`, le
`statutsAssuresSociaux` du portage), et les phrases `moteur` restent telles
quelles. L'écriture s'est faite par un outil de session, hors du dépôt, qui a
vérifié qu'aucun autre champ ne bougeait. `conservation.py --depuis HEAD` n'a
rien vu de perdu ; `jumeaux.py` ne voit aucun renvoi mort. L'étape n'écrit
aucune règle du scénario 1 : ni veille, ni entrée au journal. Rien n'est dû
aux pages.

Le lot publié, le bloc « Reprise » de l'action 161 disait que plus rien
n'importe `saisie.py`, son prochain retrait : la date d'effet et le temps
partiel ne nomment plus la saisie que dans son portage, `saisie.js`.

## Ce que l'étape laisse

- `pension_non_salaries_agricoles_2026`, seule fiche de `EN_PROSE`, à la
  session de l'action 131.
- 57 fiches sans code ni régimes — 27 conformes, 17 transcrites, 12 approchées,
  une à vérifier —, et trois qui ont un code sans régimes
  (`inaptitude_invalidite_penibilite_amiante`, `micro_social_abattement`,
  `rachats_et_versements`) : les lots suivants.
- `liquidation_regime_par_regime` nomme 74 régimes, sans les quatre ASV des
  auxiliaires médicaux, des dentistes, des directeurs de laboratoire et des
  sages-femmes, ni les points d'avant 1973 des artisans et des commerçants,
  que le catalogue calcule aussi : à revoir avec elle.
- Le cas qui confronterait le portage au plafond de 1972 à 1974, pour une
  session du modèle.
- Les 106 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
