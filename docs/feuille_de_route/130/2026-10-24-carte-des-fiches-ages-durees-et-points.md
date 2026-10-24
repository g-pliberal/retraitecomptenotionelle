# La carte des fiches : le code des âges, des durées et des régimes en points, écrit

**La demande.** Vague du 24 octobre 2026, troisième salve : le propriétaire
demande une session par tâche qui se mène sans lui, et huit tournent ensemble.
Celle-ci, de l'action 130 : un troisième lot des 23 fiches que `EN_PROSE`
(`tests/test_carte.py`) tient encore à leur seule phrase `moteur`, jusqu'à ce
que le test confronte leur code au dépôt comme celui des autres ; les lots
suivants viendront dans d'autres sessions. Aucun chiffre du modèle ne bouge :
seuls changent les champs `code` et `regimes` de onze fiches, et `EN_PROSE`.

## Ce qui est fait

- **Un lot de onze fiches**, de 23 à 12, vu rouge — `EN_PROSE` resserré
  d'abord, le cliquet rougissant de quarante-cinq écarts, quatre par fiche et
  un de plus pour les paramètres que portent les versions des coefficients de
  l'Agirc-Arrco —, puis écrit et vert. Les âges et les durées par génération :
  l'âge d'annulation de la décote, `age_taux_plein` et la table
  `AgesAnnulationDecote` ; l'âge légal, `age_ouverture_commun` et
  `AgesOuverture` ; la durée requise, `duree_requise` et `DureesRequises`, avec
  les dates d'effet de la loi de 2023 et de la suspension ; l'un et l'autre
  sous les droits contrefactuels, par `TableRecouverte` et
  `ScenarioActuel._sous_le_droit`, avec les tables d'avant la réforme de 2023
  et d'avant la suspension ; le dénominateur de la proratisation,
  `duree_proratisation` et `DureesProratisation`, son numérateur,
  `Durees.plafond`, et les années de l'exploitant agricole que la fiche
  décrit, par les méthodes de `Carriere` ; la durée majorée après l'âge du
  taux plein, `duree_majoree_apres_taux_plein`, `trimestres_d_ajournement` et
  `regimes_qui_bornent_la_duree_majoree`. Les coefficients des régimes en
  points, tous par `abattement_points` : les coefficients d'anticipation de
  l'Agirc-Arrco, de l'Ircantec et du RCI, deux tables,
  `_coefficient_anticipation` et `coefficient_pour_age`, et ce qui exonère,
  `exonerations_agirc_arrco` ; la décote du régime général sur les points de
  la CNAVPL et de la MSA, `abattement_regime_de_base` et
  `CoefficientsMinoration` ; la surcote de l'Ircantec, `surcote_ircantec` et
  `_fenetre_ircantec` ; la majoration par l'âge seul des sections libérales,
  `surcote_points`, `age_de_la_duree_atteinte` et
  `AgesRegimes.age_surcote_maximum`.
- **Le champ `regimes`**, que ces fiches n'avaient pas : les régimes dont les
  périodes renvoient à elles par un interrupteur, d'un seul (l'Ircantec) à
  quarante-huit (l'âge légal). La carte passe de 769 manques à 758 ; ses 106
  fiches à mûrir restent.
- **Les paramètres** : pour les quatre fiches d'une table par génération, la
  table, `legislation/*.csv`, et non le champ de la période qui ne sert que de
  repli, qu'il aurait fallu nommer jusque dans quarante-huit fiches de
  régime ; pour les autres, les champs que la règle lit dans les périodes ; et
  les paramètres des versions des coefficients de l'Agirc-Arrco.
- **Les tests nommés** : ceux qui tiennent la règle — `test_simulateur.py`,
  `test_donnees.py` pour les tables, `test_oracle.py` pour les exemples publiés
  que la fiche cite, `test_droits_contrefactuels.py`,
  `test_ircantec_minoration.py`, `test_exonerations_agirc_arrco.py`,
  `test_invalidite.py`, `test_sections_liberales.py`, `test_sections_sante.py`
  — ; et, pour les onze, `tests/js/moteur.test.js` avec
  `tests/temoins/simulations.json`. Une sonde de session, hors du dépôt, a
  rejoué les 897 témoins en Python et relevé ceux où la règle change ce que sa
  fonction rend : de 5 (le coefficient de l'Ircantec) à 328 (l'âge légal). Un
  témoin par fiche a été vérifié sur le détail de sa pension :
  `chomage_avant_1967` proratise sur 154 trimestres pour 160 requis,
  `cumul_artisan` abat le RCI de 0,78, `statut_contractuel_public_1955` majore
  l'Ircantec de 1,0375, `statut_medecin_liberal_1955` la CARMF de 1,10.

Les champs de classe, que l'outil ne lit pas, ne sont pas nommés :
`Droits.abattus` et `Droits.points_abattus`, que la fiche de l'Agirc-Arrco
cite, ni `Carriere.au_deces`. L'écriture s'est faite par un outil de session,
hors du dépôt, comme aux lots précédents. `conservation.py --depuis HEAD` n'a
rien vu de perdu ; `jumeaux.py` ne voit aucun renvoi mort. L'index LEGI n'a
pas été remis à jour : l'étape n'écrit aucune règle du scénario 1, et le
journal de veille n'a pas d'entrée. Rien n'est dû aux pages.

## Ce que l'étape laisse

- Les 12 fiches de `EN_PROSE`. `pension_non_salaries_agricoles_2026` est à
  la session de l'action 131. Deux lots se dessinent : les cotisations et les
  points des libéraux, de la MSA et des cultes (`assiette_minimale_agricole`,
  `cotisation_par_classes_liberales`, `cultes_retraite_complementaire`,
  `cultes_salaire_annuel_moyen`, `points_au_prorata_des_cotisations`,
  `raap_classe_speciale`, `retraite_proportionnelle_msa`) ; les quatre sans
  interrupteur (`date_effet_mois_suivant`, `temps_partiel_fonction_publique`,
  `trimestres_avant_1972`, `trimestres_retenus_1972_1974`), dont le champ
  `regimes` ne se lit pas aux renvois des périodes.
- Les limites de l'outil, inchangées.
- Les 106 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
