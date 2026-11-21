# Le tri des tests : quatre témoins en double retirés

Le 21 novembre 2026, au même tri des tests que la note de l'action 161 du
même jour (`161/2026-11-21-tri-des-tests-le-moteur-confronte-a-lui-meme.md`).

Quatre des 937 témoins de simulation répétaient au caractère près la requête
d'un autre, et rendaient donc le même résultat au bit près : les boucles du
balayage (`scripts/construire_temoins.py`) repassaient par la valeur de la
base.

- `statut_salarie_prive_non_cadre` : le statut de la base, né en 1975, est le
  témoin `base` lui-même ;
- `liquidation_64` : l'âge de départ de la base ;
- `indexation_triple_lock_inverse` : la règle d'indexation de la base ;
- `bascule_2026` : la bascule de la base, pour la naissance de 1990, est le
  témoin `generation_1990`.

Chaque boucle saute désormais la valeur de la base. Un test de `test_web.py`,
`test_aucun_temoin_ne_repete_la_requete_d_un_autre`, vu rouge sur ces quatre
paires, refuse qu'un témoin répète la requête d'un autre. Régénérés, les
témoins passent de 937 à 933, et aucun autre ne bouge. Les tests qui rejouent
une requête sur cinq (`test_droit.py`, `test_liquidation.py`), dont
l'échantillon se décale, passent (64 tests). Le fichier des témoins est
refait au même commit, sur le `main` du 21 novembre au soir : seuls ces
quatre en partent. Les deux chiffres ancrés du README qui les comptent,
GitHub les refait après l'envoi.
