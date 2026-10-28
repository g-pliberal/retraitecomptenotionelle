# La carte des fiches : le code des droits familiaux, écrit

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après celle
du premier lot, qui a écrit onze fiches. Celle-ci, de l'action 130 : le lot
suivant des 46 fiches tirées du registre de veille qui n'avaient ni code ni
régimes (note
`130/2026-10-28-carte-des-fiches-regimes-speciaux-et-fonctionnaires.md`), les
douze des droits familiaux. Aucun chiffre du modèle ne bouge : seuls changent
les champs `code` et `regimes` de douze fiches, et un test.

## Ce qui est fait

- **Le test d'abord** : `CODE_ET_REGIMES_ECRITS` (`tests/test_carte.py`)
  grandit des douze, vu rouge de douze fiches, deux champs chacune, puis vert ;
  leur code, `test_le_code_de_chaque_fiche_tient` le confronte au dépôt.
- **Les douze fiches.** Les majorations de pension pour enfants : les 10 % du
  régime général, des régimes alignés et des non-salariés agricoles, et le
  plafond en euros de l'Agirc-Arrco (`completer`, `plafond_majoration`) ; les
  taux de l'Agirc-Arrco par année d'acquisition des points
  (`MajorationsEnfantsPoints`) ; la majoration de l'Ircec, celle de la base des
  libéraux et des avocats, et celle des complémentaires de la CAVAMAC, de la
  Cipav et de la CAVEC, au barème commun de `_taux_majoration_enfants` ; les
  barèmes propres des régimes spéciaux et des marins (`taux_majoration_enfants`).
  Les autres droits des parents : la majoration de durée et la surcote parentale
  de la CNAVPL (`majoration_pour_enfants`, `trimestres_de_surcote_parentale`) ;
  les vingt-quatre et vingt-trois meilleures années (`nombre_d_annees_retenues`) ;
  la surcote parentale de ses six régimes ; les deux trimestres d'enfants
  réputés cotisés pour la carrière longue (`CarriereLongue.cotises_reputes`) ;
  le salaire de l'AVPF et son assiette (`DonneesMacro.revenu_avpf`,
  `salaire_de_reference`).
- **Le champ `regimes`**, lu à la règle et au code, aucune de ces fiches n'étant
  nommée par un interrupteur : les régimes dont les périodes déclarent le droit
  (`majoration_enfants`, `mda`, `surcote_parentale`, `avpf`) ou portent le
  barème qu'il lit ; les sept fiches de l'Agirc-Arrco pour son plafond et ses
  taux ; le régime général, les salariés agricoles et les trois régimes du code
  des pensions pour les trimestres réputés cotisés, que `CarriereLongue` oppose
  à toute carrière longue. Celui des vingt-quatre et vingt-trois années vient du
  code : toute période qui compte ses années à la génération, la CAVIMAC et les
  non-salariés agricoles depuis 2026 compris. La carte passe de 725 manques à
  701 ; ses 106 fiches à mûrir restent.
- **Les tests nommés**, relevés par une sonde de session, hors du dépôt : dans
  une copie du dépôt, au paquet du site refait, chaque règle neutralisée tour à
  tour par un interrupteur d'environnement, treize en tout ; la suite rapide,
  quatorze fichiers des oracles et des contrôles, celui des mères
  (`test_scenarios_meres.py`) et les deux du coût des avantages
  (`test_avantages.py`, `test_grille_large.py`), que rien ne fait tomber,
  rejoués ; les 909 témoins en Python, comparés au Python non muté. Changent
  treize témoins sans la majoration du régime général et des alignés, six sans
  le plafond de l'Agirc-Arrco et cinq sans ses taux, douze sans les années des
  parents, douze sans la surcote parentale, un sans la majoration de l'Ircec, un
  sans la durée et la surcote de la CNAVPL ; aucun sous les six autres
  neutralisations. Les fiches nomment ces témoins
  (`tests/temoins/simulations.json`), que le portage rejoue
  (`tests/js/moteur.test.js`), et, à part, les tests qui ne tombent que parce
  qu'ils confrontent les deux moteurs sur des carrières qui portent la règle.
- **Les trous, que les fiches disent.** Aucun témoin, aucun test qui confronte
  les deux moteurs n'atteint le salaire de l'AVPF, le barème des marins, ceux
  des régimes spéciaux au-delà de trois enfants, ni les trimestres d'enfants
  réputés cotisés : leur portage n'est confronté nulle part. Seul
  `test_les_regimes_speciaux_majorent_par_enfant_au_dela_de_trois` tient ces
  barèmes, sans le SEITA ; seul `test_referents.py`, des contrôles, tient les
  trimestres réputés cotisés, et aucun cas de la suite rapide. Aucun cas posé à
  la main ne tient les vingt-quatre et vingt-trois années : seuls les voient les
  témoins, les tests qui confrontent les deux moteurs et celui de la cascade
  (`test_liquidation.py`), dont l'essai sans l'AVPF ne laisse la pension de la
  mère au foyer intacte qu'avec elles. La majoration de la base des libéraux et
  des avocats, et celle des trois sections, n'ont pas de témoin.

L'écriture s'est faite par un outil de session, hors du dépôt, qui a vérifié
qu'aucun autre champ ne bougeait. Les phrases `moteur` disent ce que le code
fait, relu fonction par fonction. L'étape n'écrit aucune règle du scénario 1 :
ni veille, ni entrée au journal. Rien n'est dû aux pages.

## Ce que l'étape laisse

- 34 fiches sans code ni régimes — 15 conformes, 9 transcrites, 9 approchées,
  une à vérifier —, et trois sans régimes
  (`inaptitude_invalidite_penibilite_amiante`, `micro_social_abattement`,
  `rachats_et_versements`) : les lots suivants, qui entrent à
  `CODE_ET_REGIMES_ECRITS`.
- Pour une session du modèle : un témoin, ou un cas qui confronte les deux
  moteurs, pour l'AVPF, la bonification des marins, les régimes spéciaux
  au-delà de trois enfants et les trimestres d'enfants réputés cotisés ; le
  SEITA dans le cas des régimes spéciaux ; un cas posé à la main pour les
  vingt-quatre et vingt-trois années, quand la circulaire de la Cnav en donnera
  l'exemple.
- Pour une lecture du droit : si R. 173-3-2 atteint la CAVIMAC, à qui le code
  retire aussi les années des parents.
- `pension_non_salaries_agricoles_2026`, seule fiche de `EN_PROSE`, à la session
  de l'action 131 ; les 106 fiches à lire au droit, et les points ouverts des
  phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
