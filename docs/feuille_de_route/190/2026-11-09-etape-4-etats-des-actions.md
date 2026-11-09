# Étape 4 : les états des actions, une liste fermée

**Le 9 novembre 2026, ce qui est fait.** Les états d'une action sont
déclarés une fois, dans `scripts/reprise.py`, à côté de `TITRE_D_ACTION`
qui les lit : `A_FAIRE`, `EN_COURS`, `CLOS` (fait, abandonnée, archivée) et
`ETATS`, les cinq dans leur ordre. `reprise.etats_inconnus(texte)` rend les
titres d'action, `### <numéro>.`, dont l'état n'est pas l'un d'eux ou ne
s'écrit pas entre accents graves. Les lisent : le tableau de bord, qui
compte désormais les actions par `TITRE_D_ACTION` plutôt que par son propre
motif, et compare à `EN_COURS` ; la conservation, dont `_vivantes` lit
`CLOS` ; `tests/test_prose.py`, dont les trois tests de la feuille de route
ne récrivent plus ni les états clos, ni « en cours », ni le motif du titre.

**Le test, joué à l'envoi.** `pousser.sh` n'est pas touché : le refus vit
dans `test_les_notes_de_la_feuille_de_route_se_rangent_par_action`, qu'il
joue déjà, et qui lisait déjà la feuille de route et l'archive ; son nom ne
change pas. Vu rouge sur la feuille de route et l'archive réelles, l'action
190 récrite `en-cours` et une action de l'archive `faite`, le temps d'un
essai : les deux titres refusés, quand le test des blocs « Reprise », lui,
passait sans voir l'action 190. Un test à part,
`test_un_etat_d_action_hors_du_vocabulaire_se_refuse`, tient
`etats_inconnus` sur un texte écrit à la main : un état mal écrit, un état
sans accents graves, un état clos mal accordé refusés ; un intertitre
`####` ignoré. Il est du niveau `controle`, comme tout `test_prose.py`.

**Ce qui ne bouge pas.** La page du tableau de bord et les lignes vivantes
de la conservation sortent identiques, octet pour octet, avant et après. Le
motif de `_vivantes`, qui lit ligne à ligne hors des blocs de code, reste le
sien : il ne diffère de `TITRE_D_ACTION` que sur un titre que le test
refuse désormais.

**La limite.** `pousser.sh` ne joue ces tests que si un commit touche la
feuille de route ou ses notes : un état récrit dans la seule archive passe
l'envoi, et la suite complète de GitHub le refuse après.
