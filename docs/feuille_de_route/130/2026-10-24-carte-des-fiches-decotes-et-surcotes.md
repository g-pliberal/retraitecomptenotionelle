# La carte des fiches : le code des décotes et des surcotes, écrit

**La demande.** Vague du 24 octobre 2026, seconde salve : le propriétaire
demande une session par tâche qui se mène sans lui, et dix tournent ensemble.
Celle-ci, de l'action 130 : un deuxième lot des 36 fiches que `EN_PROSE`
(`tests/test_carte.py`) tient encore à leur seule phrase `moteur`, jusqu'à ce
que le test confronte leur code au dépôt comme celui des autres ; les lots
suivants viendront dans d'autres sessions. Aucun chiffre du modèle ne bouge :
seuls changent les champs `code` et `regimes` de treize fiches, et `EN_PROSE`.

## Ce qui est fait

- **Un lot de treize fiches**, de 36 à 23, vu rouge — `EN_PROSE` resserré
  d'abord, le cliquet rougissant de cinquante-deux écarts, quatre par fiche —,
  puis écrit et vert : les décotes et les surcotes des régimes de base et des
  régimes spéciaux. Décotes : celle du régime général et des régimes alignés,
  `decote_opposable` et `trimestres_de_decote` dans `liquider_chaque_regime`,
  au coefficient de `CoefficientsMinoration` ; celle de la fonction publique,
  au barème de `DecoteFonctionPublique` lu par `millesime_du_bareme` ; celle
  des régimes spéciaux, `DecoteRegimesSpeciaux`, avec `borne_de_la_duree` et la
  cible abaissée de la SNCF (`retranche_decote`, `duree_propre`) ; celle de
  l'Opéra, au même barème ; celle de la CRPN, sur la durée seule ; celle
  d'avant 1983, `ecart_au_taux_plein`, `taux_plein_des_femmes`,
  `taux_acquis_au_31_mars_1983` ; l'âge de référence des IEG,
  `age_taux_plein`. Surcotes : celles du régime général, de la fonction
  publique et de la CNBF, `coefficient_surcote_datee` au barème daté de
  `SurcoteBaremes`, depuis `age_surcote`, et `surcote_points` des libéraux et
  des exploitants ; celle des régimes spéciaux,
  `trimestres_de_surcote_regimes_speciaux`, et leurs âges propres,
  `AgesSurcoteRegimesSpeciaux` ; l'âge d'ouverture des actifs des IEG, par
  `age_ouverture_commun` et les tables `ieg_actif_2011` et `ieg_actif_2023`.
- **Le champ `regimes`**, que ces fiches n'avaient pas : les régimes dont les
  périodes renvoient à elles par un interrupteur, et, pour la surcote des
  régimes spéciaux, que seule la CRPCEN nomme ainsi, les six que son intitulé
  énumère, dont la règle s'applique à toute période au barème des régimes
  spéciaux. La carte passe de 782 manques à 769 ; ses 106 fiches à mûrir
  restent.
- **Les tests nommés** : ceux qui tiennent la règle dans `test_simulateur.py`,
  `test_oracle.py` (les exemples publiés), `test_sections_juridiques.py`,
  `test_cnracl.py`, `test_fonction_publique_etat.py`,
  `test_coupures_au_mois.py`, `test_pension_maximale.py` ; et
  `tests/js/moteur.test.js` avec `tests/temoins/simulations.json` pour onze
  fiches, dont un témoin rejoué par le portage exerce la règle, vérifié sur le
  détail de sa pension — `generation_coupee_1961_avant` décote au régime
  général, `sncf_surcote_apres_soixante_quatre_ans` surcote depuis
  soixante-quatre ans, `ieg_generation_1965_partie_en_2025` garde l'âge
  d'annulation d'avant 2025, `chomage_apres_65_ans_avant_1983` sert 60 %. La
  CRPN et l'Opéra n'ont aucun témoin qui décote : leurs fiches ne nomment que
  le Python.

Les champs de classe, que l'outil ne lit pas, ne sont pas nommés :
`ScenarioActuel.SURCOTE_DEPUIS` et `SURCOTE_AGE_MAJORE`, dont le portage fait
des constantes de module, ni `Durees.duree_hors_surcote`. L'écriture s'est
faite par un outil de session, hors du dépôt, comme aux lots précédents.
`conservation.py --depuis HEAD` n'a rien vu de perdu ; `jumeaux.py` ne voit
aucun renvoi mort ; seul `docs/etat.md` est périmé, que GitHub refait. L'index
LEGI n'a pas été remis à jour : l'étape n'écrit aucune règle du scénario 1, et
le journal de veille n'a pas d'entrée. Rien n'est dû aux pages.

## Ce que l'étape laisse

- Les 23 fiches de `EN_PROSE`. `pension_non_salaries_agricoles_2026` est à
  la session de l'action 131. Des lots se dessinent : les âges et les durées
  par génération (`age_annulation_decote`, `age_legal_par_generation`,
  `duree_requise_par_generation`, `taux_plein_et_proratisation`,
  `majoration_duree_apres_65_ans`) ; les coefficients de l'Agirc-Arrco et de
  l'Ircantec, et les régimes en points ; les cotisations et les points des
  libéraux, de la MSA et des cultes ; les quatre sans interrupteur
  (`date_effet_mois_suivant`, `temps_partiel_fonction_publique`,
  `trimestres_avant_1972`, `trimestres_retenus_1972_1974`).
- Les limites de l'outil, inchangées.
- Les 106 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
