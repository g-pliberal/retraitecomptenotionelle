# Veille du droit — ce qui l'a fait naître, et ce que le registre portait

*Archive, gelée.* Deux sections de `docs/veille_droit.md`, déplacées telles
quelles le 26 septembre 2026, quand la phase 1 de l'architecture a raccourci
la procédure (`docs/architecture.md`, annexe B) : le récit du jour où le
scénario 1 s'est trouvé faux, et l'état du registre tel que la page le
disait. L'état du registre se lit désormais dans le tableau de bord,
`docs/etat.md`.

## Ce qui s'est passé le 17 septembre 2026

Les âges légaux et les durées requises du dépôt étaient **certifiés** : lus
automatiquement dans la base LEGI, confrontés ligne à ligne, journalisés. Ils
étaient faux pour tout assuré né de 1964 à 1968. La loi de financement de la
sécurité sociale pour 2026, votée le 30 décembre 2025, avait suspendu la
réforme de 2023 ; ses décrets étaient du 7 mai 2026 ; le dump LEGI que le
récupérateur avait lu était du 13 juillet 2025. Une certification est vraie à
une date, et rien dans le dépôt ne disait que cette date était dépassée.

C'est le premier exemple chiffré publié par service-public qui l'a fait voir :
« né en 1964, 62 ans et 9 mois, 170 trimestres », là où le dépôt disait
63 ans et 171. Sans cet exemple, l'erreur aurait été servie à chaque
utilisateur né dans ces années.

Trois leçons, qui sont devenues trois outils.

1. **Une valeur n'est pas juste parce qu'elle est certifiée : elle est juste
   à la date de sa certification.** Chaque règle porte donc maintenant la
   date de sa dernière lecture, et un script dit lesquelles ont vieilli.
2. **Une déduction n'est pas une lecture, une mémoire n'est pas une source.**
   Ce qui entre dans le scénario 1 a été lu dans le texte sur Légifrance, et
   dans la circulaire ou la fiche qui l'applique. Sans les deux, la ligne le
   dit (`transcrit`, `a_verifier`), et ce niveau remonte jusqu'au résultat
   affiché.
3. **L'exemple publié par la caisse est la seule contre-expertise officielle
   et reproductible.** Il n'y a pas de simulateur officiel interrogeable ;
   il y a des exemples, et ils se rejouent.

## Ce que le registre porte aujourd'hui

Le registre porte <!--chiffre:entrees(data/reference/legislation/veille.yaml:entrees)-->98<!--/--> lignes,
et ce qui y est `conforme` a été lu dans le texte comme dans son application,
puis rejoué par les <!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->54<!--/--> exemples publiés
que `exemples_officiels.yaml` transcrit. Le 17 septembre 2026, l'action 27 a
fait relire au récupérateur, dans l'index LEGI du dépôt tenu à jour des
incréments de la DILA, les articles que la suspension a réécrits : les lignes
redescendues au niveau `moyenne` sont toutes redevenues `certifiee`, sans
qu'un chiffre bouge, et le récupérateur ne lit plus le dump global de
juillet 2025.

Ce qui est `transcrit` attend son exemple. Ce qui est `manque` ou
`approximation` est mesuré dans `limites.md`. Ce qui est `a_verifier` est ce
que la session n'a pas pu finir de lire, et c'est par là que la suivante
commence — `python scripts/veille_droit.py` le dit.
