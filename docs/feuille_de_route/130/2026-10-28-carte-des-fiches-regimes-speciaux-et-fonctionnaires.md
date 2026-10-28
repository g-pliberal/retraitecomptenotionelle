# La carte des fiches : le code des régimes spéciaux et des fonctionnaires, écrit

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui, et dix-sept tournent ensemble. Celle-ci, de
l'action 130 : un premier lot des 57 fiches tirées du registre de veille qui
n'avaient ni code ni régimes (note
`130/2026-10-24-carte-des-fiches-cotisations-cultes-et-durees.md`). Aucun
chiffre du modèle ne bouge : seuls changent les champs `code` et `regimes` de
onze fiches, et un test.

## Ce qui est fait

- **Le test d'abord** : `CODE_ET_REGIMES_ECRITS` (`tests/test_carte.py`), les
  fiches dont le code et les régimes s'écrivent par lots, et le test qui exige
  qu'aucune n'en manque, vu rouge de onze fiches, deux champs chacune, puis
  vert. La liste grandit d'un lot à l'autre ; celle, qui maigrirait, des fiches
  qui en manquent encore arrêterait aussi la fiche qui naît sans eux, une
  découverte, quand le § 9.2 de l'architecture n'arrête qu'une régression. Le
  code des onze, `test_le_code_de_chaque_fiche_tient` le confronte au dépôt.
- **Les onze fiches.** Les régimes spéciaux : la table de 2025 de l'agent de
  conduite de la SNCF et celle de la RATP, avec les trimestres que la SNCF
  retranche à sa décote par la durée (`duree_propre`, `retranche_decote`) ;
  celle des dix-sept ans de services actifs des IEG ; l'âge de référence de
  cinquante-sept ans de la SNCF et de la RATP (`age_taux_plein`, `AgesRegimes`) ;
  les âges par génération et la durée au mois des conditions réunies — tables
  de 2014 et de 2023, calendrier de 2008, âge de lecture des IEG — de la SNCF,
  de la RATP, des IEG et de la CRPCEN. Les fonctionnaires : la durée propre aux
  emplois classés et celle de leur droit ouvert avant soixante ans
  (`derogation_active`, `duree_requise_avant_soixante_ans`), leurs âges et leurs
  services classés (`services_actifs_requis`) ; la durée du militaire, et celle
  du sédentaire parti en carrière longue, avec les portes datées et la durée
  fixe de `CarriereLongue` ; le traitement de la pension différée, revalorisé
  comme les pensions (`coefficient_traitement_differe`) ; les services que L. 9
  retient (`services_fonction_publique`) ; le taux maximum que les seules
  bonifications dépassent (`taux_maximum_bonifie`).
- **Le champ `regimes`**, lu à la règle et au code, aucune de ces fiches n'étant
  nommée par un interrupteur : la SNCF et la RATP, les IEG, ou les quatre
  régimes spéciaux ; l'État, la CNRACL et le FSPOEIE pour six fiches, les trois
  régimes du code des pensions (`REGIMES_CODE_DES_PENSIONS`) ; l'État seul pour
  le militaire ; les cinq régimes de la famille `fonction_publique` pour les
  services, que le code leur applique à tous. La carte passe de 747 manques à
  725 ; ses 106 fiches à mûrir restent.
- **Les tests nommés**, relevés par une sonde de session, hors du dépôt : chaque
  règle neutralisée tour à tour, la suite rapide et les tests des oracles
  rejoués, et les 247 témoins des fonctionnaires et des régimes spéciaux en
  Python. Changent 72 des 73 témoins des emplois classés sans leurs âges, 32
  sans leur durée ; 37 des 54 témoins des régimes spéciaux sans
  leurs âges et leurs durées par génération ; 18 des 193 témoins des
  fonctionnaires sans le taux bonifié, 11 sans la pension différée, 5 sans les
  services de L. 9 ; 7 des 22 militaires ; 6 des 16 agents des IEG ; 3 des 29
  agents de la SNCF et de la RATP. Les fiches nomment alors leurs témoins
  (`tests/temoins/simulations.json`), que le portage rejoue
  (`tests/js/moteur.test.js`).
- **Les trous, que les fiches disent.** Aucun cas posé à la main ne tient la
  durée du militaire, que seuls suivent ses témoins, la grille du coût
  (`test_pont.py`) et les cas types statutaires
  (`test_flux_fonction_publique.py`), ni la table de 2025 de l'agent de
  conduite, que seuls trois témoins suivent, aucun de la RATP. Aucun témoin
  n'atteint l'âge de référence de la SNCF et de la RATP, que le portage ne
  confronte nulle part, ni la carrière longue des fonctionnaires, que
  `test_oracle_carriere_longue_fonction_publique.py` confronte au portage.

L'écriture s'est faite par un outil de session, hors du dépôt, qui a vérifié
qu'aucun autre champ ne bougeait. Les phrases `moteur` disent ce que le code
fait, relu fonction par fonction. L'étape n'écrit aucune règle du scénario 1 :
ni veille, ni entrée au journal. Rien n'est dû aux pages.

## Ce que l'étape laisse

- 46 fiches sans code ni régimes — 19 conformes, 14 transcrites, 12 approchées,
  une à vérifier —, et trois sans régimes
  (`inaptitude_invalidite_penibilite_amiante`, `micro_social_abattement`,
  `rachats_et_versements`) : les lots suivants, qui entrent à
  `CODE_ET_REGIMES_ECRITS`.
- Un cas posé à la main pour la durée du militaire et pour la table de 2025 de
  l'agent de conduite, et un cas qui confronte le portage à l'âge de référence
  de la SNCF et de la RATP : pour une session du modèle.
- `pension_non_salaries_agricoles_2026`, seule fiche de `EN_PROSE`, à la session
  de l'action 131 ; les 106 fiches à lire au droit, et les points ouverts des
  phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
