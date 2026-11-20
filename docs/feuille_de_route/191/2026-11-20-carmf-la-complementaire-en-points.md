# La complémentaire des médecins se compte en points depuis 1996

Le 20 novembre 2026, sur le constat de la relecture des régimes du même jour
(rang 2, les complémentaires des libéraux), et selon la règle du propriétaire
(« on corrige tout ce qui est faux »).

**Lu.** Le règlement du régime complémentaire de la CARMF, approuvé par
l'arrêté du 10 juillet 2026, dans ses deux rédactions (LEGIARTI000054437501,
puis LEGIARTI000054890209, en vigueur depuis le 25 septembre 2026, qui ne
corrige que des renvois). Article 3 : « Le montant de la retraite d'un médecin
s'obtient en multipliant le nombre de points acquis, alloués ou rachetés, par
la valeur du point ». « La chronologie des chiffres de la CARMF 2025 », relue
sur le PDF de la caisse : la cotisation maximale attribue dix points chaque
année de 1996 à 2025 (page 26), et la valeur du point y est donnée par année
(pages 59, 60 et 95).

**Le moteur** ne comptait pas de points : il portait chaque cotisation aux
prix de l'année du départ et appliquait au tout le rendement de cette seule
année. La limite était déclarée (« Un rendement unique là où il faudrait une
série », `docs/limites/4-regimes-incomplets.md`), non mesurée pour les
médecins. Le point a renchéri bien plus vite que les prix : 686,02 € en 1996,
1 039,60 € en 2010, 1 723 € en 2026.

**Corrigé, sans une ligne du moteur.** Un récupérateur,
`scripts/fetch/carmf_chronologie.py`, lit le PDF de la caisse et verse dans
`valeurs_point.csv` le prix du point (le dixième de la cotisation maximale),
un taux d'appel de 1 et la valeur du point, de 1996 à 2025, certifiés par
`verifier_donnees.py` ; 2026 est saisie depuis les chiffres clés du site
(19 849 € pour 11,52 points, 77,14 €), au niveau moyen. La fiche porte, de
1996 à 2012, le plafond de revenu de la caisse, qui n'était pas trois plafonds
et demi de la Sécurité sociale avant 2011.

**Ce qui bouge.** Né en janvier 1964, libéral de 1996 à janvier 2026, au
plafond, parti à 62 ans : 300,96 points à 77,14 €, soit 23 216,02 € par an,
contre 19 515,26 € (+ 19 %). Né le 10 mai 1964, installé à 22 ans, parti à
63 ans : 16 065,65 € contre 14 056,14 €. Quinze témoins du scénario 1, tous
des médecins, montent de 0,20 à 2,86 % de leur pension totale ; aucun ne
baisse. Sept tests anciens, figés sur l'ancien calcul, sont reposés.

**Reste.** Les années d'avant 1996, où un forfait de quatre points et une
proportionnelle à plancher achètent à deux prix : elles restent au rendement
de l'année du départ, et la fiche y fait cotiser tout le revenu. Le revenu de
l'avant-dernière année, que la caisse retient. La majoration de 13 % de
l'inapte et de l'invalide (articles 2 et 4), le versement unique sous vingt
points (article 5), la réversion (articles 10 à 18), non relus contre le
moteur. Les autres caisses servies par un rendement, la CIPAV d'abord.
