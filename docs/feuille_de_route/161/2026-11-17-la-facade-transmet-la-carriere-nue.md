# La façade transmet la carrière nue : 306 des 476 tests qui lisaient la carrière des règles n'en dépendent plus

Action 161, premier morceau de « la carrière que le pont relit » (la fin de
l'étape 4, `2026-11-16-le-python-seul-debranche.md`), mené la nuit du 16 au
17 novembre 2026, sur la consigne du propriétaire d'avancer ce qui ne demande
pas son avis. Aucun fichier de `src/` ni de `moteur/` n'est touché : aucun
résultat, aucune donnée, aucun témoin ne peut bouger.

- **La mesure.** `pont.carriere_des_donnees` rendu sous la carrière nue
  (`types_du_pont.carriere.Carriere`) au lieu de celle des règles
  (`carriere.Carriere`), le temps d'une course de `pytest -m rapide` : 476
  échecs, dont 308 levés par la façade des tests elle-même (`tests/facade.py`,
  `_argument_de_regle`), qui ne savait transmettre au portage qu'une carrière
  de la classe des règles (`NonTransmissible`), et non le type du pont dont
  elle hérite. Le portage n'en lit pourtant que les champs
  (`pont.carriere_en_donnees`).
- **Le changement.** `tests/facade.py` reconnaît la carrière par le type nu, à
  la transmission d'un argument et au retour d'une règle qui rend la carrière
  reçue. La carrière des règles, qui en hérite, passe comme avant.
- **Le test.** `tests/test_facade.py`,
  `test_une_regle_recoit_la_carriere_nue_comme_celle_des_regles` : une
  carrière nue, recopiée champ à champ, reçoit de `ouvrir.duree_requise` et
  `ouvrir.age_ouverture` ce que reçoit celle des règles (166 trimestres,
  62 ans pour un assuré né en 1955). Vu rouge (`NonTransmissible`), puis vert.
  `python -m pytest -m rapide` : vert (5 694).
- **Mesuré de nouveau** sous la carrière nue : 170 échecs, au lieu de 476.

**Ce qui reste : les 170, en quatre morceaux, une session chacun.**

1. **Le dictionnaire de la comparaison** (32 échecs, surtout
   `test_reversion.py`) : `types_du_pont/comparaison.py`, ligne 463, lit
   `carriere.trimestres_actuels`, une propriété de règle. Le portage écrit
   déjà ce nombre (`moteur/js/simulateur.js`, `trimestres_actuels`) : la
   comparaison relue doit le tenir du portage. Toucher au type du pont et à ce
   que le portage transmet : vérifier à l'octet les témoins.
2. **Le simulateur Python lui-même** (16 échecs) : `simulateur.py`, ligne 416
   (`prolongee`), et `donnees/affiliations.py`, ligne 167 (`date_entree`),
   appelés par des tests encore sur le simulateur Python. Chacun passe à la
   façade, ou part avec les règles.
3. **Les tests qui lisent une propriété de règle** (près de 120, dans 25
   fichiers) : `test_simulateur.py` (43 : `trimestres_retenus`, `prolongee`,
   `annee_de_cessation_agricole`…), `test_priorite_enfants.py` (22 :
   `date_entree`), puis une traîne d'un à six par fichier. Chaque lecture se
   demande au portage, par une entrée de la façade, ou part avec les règles.
   Plusieurs sessions, fichier par fichier, en commençant par les deux gros.
4. **La bascule** : `carriere_des_donnees` rend la carrière nue, et les deux
   tests qui épinglent la classe des règles (`test_pont.py`, ligne 372 ;
   `test_facade.py`, `test_la_carriere_simple_revient_sous_le_type_du_python`)
   la suivent. Elle vient en dernier, à zéro échec.

La recette de la mesure : remplacer, dans `carriere_des_donnees`,
`return Carriere(` par `return CarriereNue(`, lancer
`python -m pytest -m rapide --tb=line`, regrouper les lignes
`fichier:ligne: AttributeError`, puis rétablir.
