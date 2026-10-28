# La carte des fiches : le code des libéraux et des indépendants, écrit

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après les
deux premiers lots, onze puis douze fiches. Celle-ci, de l'action 130 : le lot
suivant des 34 fiches tirées du registre de veille qui n'avaient ni code ni
régimes (note `130/2026-10-28-carte-des-fiches-droits-familiaux.md`), les onze
des libéraux, des indépendants et des auteurs. Aucun chiffre du modèle ne
bouge : seuls changent les champs `code` et `regimes` de onze fiches, et un
test.

## Ce qui est fait

- **Le test d'abord** : `CODE_ET_REGIMES_ECRITS` (`tests/test_carte.py`)
  grandit des onze, vu rouge de onze fiches, deux champs chacune, puis vert ;
  leur code, `test_le_code_de_chaque_fiche_tient` le confronte au dépôt.
- **Les onze fiches.** L'assiette minimale de la cotisation de base des
  indépendants et ses dispenses, que la ligne de carrière porte et que les
  régimes de base de sa table opposent (`_ligne_annuelle`, `assiette_minimale`,
  `dispense_assiette_minimale`, `dispense_les_complementaires`) ; les points
  d'ajustement de l'ASV des médecins (`PeriodeRegime.ajustement_total`) ; les
  barèmes de la CNBF, année par année, pension forfaitaire et tranches en euros
  du complémentaire (`liquider_chaque_regime`, `bornes_assiette_en_euros`) ; la
  table d'âges `carpimko_2016` (`AgesRegimes`, `age_taux_plein`,
  `decote_opposable`) et l'assiette de 2026 de la CARPIMKO, demi-plafond
  minimum et rendement de 5,49 % (`PeriodeRegime.assiette_minimale`,
  `Rendements.rendement`) ; le plafond par marches et le minimum de la CAVOM ;
  la seconde tranche de la Cipav (`BORNES_ASSIETTE`) ; la valeur de service de
  la CNAVPL (`ValeursPoint.service_au`, `valeur_du_point`) ; le prix et la
  valeur du point RCI (`ValeursPoint.achat_prolonge`) ; le RAAP au taux aménagé
  des auteurs du RACD et du RACL (`Affiliations.regimes`, `points_de`). Le
  décret n° 2026-418, qui ne change aucun paramètre, a pour code celui des
  régimes qu'il réécrit (`acquerir`, `liquider_chaque_regime`).
- **Le champ `regimes`**, lu à la règle et au code, aucune de ces fiches
  n'étant nommée par un interrupteur : les régimes dont les périodes, les
  tables ou les valeurs du point portent la règle ; pour l'assiette minimale,
  les cinq régimes de base que sa table nomme, et la CARPIMKO et la CAVOM, dont
  les dispenses du RSA, de la prime d'activité et de l'activité saisonnière
  écartent aussi le minimum ; pour le RAAP au taux aménagé, le RAAP, dont il
  emprunte le barème ; pour le décret, les douze régimes complémentaires et
  d'ASV qu'il réécrit et que ses lectures ont confrontés. La carte passe de
  701 manques à 679 ; ses 106 fiches à mûrir restent.
- **Les tests nommés**, relevés par une sonde de session, hors du dépôt : dans
  une copie du dépôt, au paquet du site refait, chaque règle neutralisée tour à
  tour par un interrupteur d'environnement dans les deux moteurs, quatorze
  neutralisations pour dix fiches — les dispenses à part du minimum, le
  rendement de la CARPIMKO à part de son assiette, la structure des deux
  tranches de la Cipav et le minimum de la CAVOM à part de leurs bornes — ; la
  suite rapide et seize fichiers des oracles et des contrôles rejoués ; les 909
  témoins en Python, comparés au Python non neutralisé ; puis, la règle
  neutralisée dans le seul Python, les 183 tests qui confrontent les deux
  moteurs. Changent 59 témoins sans la valeur de service de la CNAVPL d'avant
  2021, 61 sans les valeurs du RCI de 2024 à 2026, onze sans l'ajustement de
  l'ASV, neuf sans le taux aménagé du RAAP, huit sans les barèmes annuels de la
  CNBF, sept sans la seconde tranche de la Cipav, quatre sans l'assiette ou le
  rendement de 2026 de la CARPIMKO, trois sans l'assiette minimale, trois sans
  ses dispenses ; aucun sans les âges de la CARPIMKO, la seconde tranche portée
  à quatre plafonds ni l'assiette de la CAVOM. Les fiches nomment ces témoins
  (`tests/temoins/simulations.json`), que le portage rejoue
  (`tests/js/moteur.test.js`), et, à part, les tests qui ne tombent que parce
  qu'ils confrontent les deux moteurs sur des carrières qui portent la règle.
- **Les trous, que les fiches disent.** Aucun témoin, aucun test n'atteint la
  Cipav au-delà de trois plafonds depuis 2024 : rien ne tient sa seconde
  tranche portée à trois et demi puis à quatre plafonds. Aucun témoin ne
  liquide une pension de la CARPIMKO que ses âges changent, ni de la CAVOM que
  son plafond par marches ou son minimum changent, et aucun cas qui confronte
  les deux moteurs n'y atteint ; seul `test_le_plafond_de_la_cavom_monte_par_marches`
  lit ceux de la CAVOM, aux données. Aucun cas posé à la main ne tient les
  points d'ajustement de l'ASV que la calculette de la CARMF donne, et que
  l'effet de la fiche cite, ni le rendement de 2026 de la CARPIMKO, que seuls
  suivent quatre témoins. Deux écarts au texte, que les phrases `moteur`
  disent sans les trancher : la proportionnelle de la CNBF court sans la
  limite que son barème écrit, 297 549 € en 2026 ; le compte notionnel cotise
  sur le revenu déclaré, sans l'assiette minimale du régime de base, la
  question que la feuille de route réserve déjà au propriétaire.

L'écriture s'est faite par un outil de session, hors du dépôt, qui a vérifié
qu'aucun autre champ ne bougeait. Les phrases `moteur` disent ce que le code
fait, relu fonction par fonction. L'étape n'écrit aucune règle du scénario 1 :
ni veille, ni entrée au journal. Rien n'est dû aux pages.

## Ce que l'étape laisse

- 23 fiches sans code ni régimes — 14 conformes, 4 transcrites, 4 approchées,
  une à vérifier —, et trois sans régimes
  (`inaptitude_invalidite_penibilite_amiante`, `micro_social_abattement`,
  `rachats_et_versements`) : les lots suivants, qui entrent à
  `CODE_ET_REGIMES_ECRITS`.
- Pour une session du modèle : un témoin, ou un cas qui confronte les deux
  moteurs, pour la Cipav au-delà de trois plafonds depuis 2024, pour les âges
  de la CARPIMKO, et pour une cotisation et une pension de la CAVOM ; un cas
  posé à la main pour les points d'ajustement de l'ASV, sur la calculette de
  la CARMF, et pour le rendement de 2026 de la CARPIMKO, quand la caisse en
  publiera le prix du point ; la limite de la proportionnelle de la CNBF, que
  ses périodes ne portent pas.
- `pension_non_salaries_agricoles_2026`, seule fiche de `EN_PROSE`, à la session
  de l'action 131 ; les 106 fiches à lire au droit, et les points ouverts des
  phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
