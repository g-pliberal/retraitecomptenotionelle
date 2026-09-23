# Veille du droit : comment le scénario 1 reste le droit applicable

Le scénario 1 est l'étalon de tout le dépôt, et il doit être le droit en
vigueur, pas une lecture qu'on en aurait. Ce document dit comment on s'en
assure, et ce qui s'est passé le jour où on ne s'en était pas assuré.

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

## Les trois pièces

**Le registre** : `data/reference/legislation/veille.yaml`. Une ligne par
règle du scénario 1 — appliquée, approchée, omise ou pas encore lue — avec :

| Champ | Ce qu'il porte |
|---|---|
| `regle` | la règle en une phrase, telle que le droit l'écrit |
| `textes` | les articles et lois qui la fondent |
| `sources` | ce qui a été LU : Légifrance (texte, version), circulaire Cnav, fiche service-public, avec la date de la source |
| `verifie_le` | le jour où le dépôt l'a relue |
| `temoins` | les exemples publiés qui la rejouent (`tests/temoins/exemples_officiels.yaml`) |
| `reformes` | les entrées de `reformes.yaml` qu'elle couvre |
| `etat` | `conforme`, `transcrit`, `approximation`, `manque`, `hors_modele`, `a_verifier` |
| `effet` | qui est touché, et de combien |
| `a_faire` | le prochain geste, ou rien |
| `prochaine_veille` | la date à laquelle il faut relire, quoi qu'il arrive |

Le registre porte aussi les **sources à consulter** à chaque session, et un
**journal** où chaque session consigne ce qu'elle a consulté, trouvé et laissé.

**Le script** : `python scripts/veille_droit.py`. Il imprime les lignes à
revoir — état `a_verifier` ou `manque`, lecture de plus de cent vingt jours,
date de veille passée — et la liste des sources. `--tout` imprime tout,
`--strict` rend 1 s'il reste quelque chose à revoir.

**Le test** : `tests/test_donnees.py` impose la forme du registre, exige que
chaque témoin cité existe, et que toute réforme du calendrier
(`reformes.yaml`) datée de 2023 ou après ait sa ligne. Ajouter une réforme
sans la lire à la source et sans l'inscrire ici fait échouer la suite.

## La règle, pour toute session qui touche au scénario 1

**Au début.** Lancer `python scripts/veille_droit.py`. Lire les lignes à
revoir. Consulter les sources listées pour tout texte paru depuis la dernière
date du journal : loi de financement de l'année et ses décrets, circulaires
Cnav, dates « Vérifié le » des fiches service-public, décrets retraite au
Journal officiel par l'index DILA.

**Pour chaque règle qu'on écrit ou modifie.**

1. Lire le texte sur Légifrance, dans sa version en vigueur à la date d'effet,
   et noter l'identifiant et la date de version.
2. Lire comment la caisse l'applique : circulaire Cnav, fiche service-public,
   documentation SRE ou CNRACL. C'est là que sont les coupures au mois, les
   arrondis, les dates d'effet.
3. Chercher un exemple chiffré publié. S'il existe, il entre dans
   `exemples_officiels.yaml` et le test le rejoue. S'il n'existe pas, la ligne
   du registre reste `transcrit`.
4. Écrire la ligne du registre, ou la mettre à jour : sources, date, état.
5. Donner à la donnée le niveau de fiabilité qu'elle mérite (`certifiee` si
   recontrôlée automatiquement, `haute` si lue, `moyenne` si lue mais
   susceptible d'être dépassée avant recontrôle), et laisser ce niveau
   remonter au résultat.

Ce qui est interdit : déduire une valeur d'une autre sans le dire (« les
lignes intermédiaires suivent le même pas »), citer un texte de mémoire,
appliquer une règle à une population que le texte ne nomme pas, et laisser
une table certifiée sans date.

**À la fin.** Ajouter une entrée au `journal` : la date, ce qui a été
consulté, ce qui a été trouvé, ce qui reste. Mettre à jour `verifie_le` et
`prochaine_veille` des lignes relues. Régénérer les témoins, lancer la suite,
commiter sur `main`.

## Ce que le registre porte aujourd'hui

Le registre porte <!--chiffre:entrees(data/reference/legislation/veille.yaml:entrees)-->60<!--/--> lignes,
et ce qui y est `conforme` a été lu dans le texte comme dans son application,
puis rejoué par les <!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->30<!--/--> exemples publiés
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
