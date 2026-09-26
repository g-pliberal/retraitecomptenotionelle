# Veille du droit : comment le scénario 1 reste le droit applicable

Le scénario 1 est l'étalon de tout le dépôt : le droit en vigueur à la date
d'effet de la pension, tel que la caisse l'applique, et non une lecture qu'on
en aurait. Cette page dit la procédure qui s'en assure. Ce qui l'a fait
naître — des âges légaux certifiés, et faux, le 17 septembre 2026 — est
raconté dans `docs/archives/veille_droit.md`.

Trois principes la fondent.

1. **Une valeur n'est pas juste parce qu'elle est certifiée : elle l'est à la
   date de sa certification.** Chaque règle porte la date de sa dernière
   lecture, et un script dit lesquelles ont vieilli.
2. **Une déduction n'est pas une lecture, une mémoire n'est pas une source.**
   Ce qui entre dans le scénario 1 a été lu dans le texte sur Légifrance, et
   dans la circulaire ou la fiche qui l'applique. Sans les deux, la fiche le
   dit (`transcrite`, `a_verifier`), et ce niveau remonte jusqu'au résultat
   affiché.
3. **L'exemple publié par la caisse est la seule contre-expertise officielle
   et reproductible** : il se rejoue, et il entre même quand le modèle ne le
   reproduit pas, en écart connu.

## Les trois pièces

**La carte des règles** : `data/reference/regles/`, une fiche par règle du
scénario 1 — appliquée, approchée, omise ou pas encore lue. La fiche suit le
contrat de l'architecture (`docs/architecture.md`, § 6 et annexe C) ; ce que
la veille y lit :

| Champ | Ce qu'il porte |
|---|---|
| `intitule` | la règle en une phrase, telle que le droit l'écrit |
| `textes_a_rattacher` | les articles et lois qui la fondent, tant qu'ils ne sont pas coupés en versions |
| `sources.lectures` | ce qui a été LU : Légifrance (texte, version), circulaire Cnav, fiche service-public, avec la date de la source |
| `sources.lu_le` | le jour où le dépôt l'a relue |
| `sources.prochaine_relecture` | la date à laquelle il faut relire, quoi qu'il arrive |
| `sources.a_relire` | les questions ouvertes, le prochain geste |
| `exemples` | les exemples publiés qui la rejouent (`tests/temoins/exemples_officiels.yaml`) |
| `reformes` | les entrées de `reformes.yaml` qu'elle couvre |
| `etat` | `conforme`, `transcrite`, `approchee`, `manquante`, `pas_encore_modelisee`, `a_verifier` |
| `effet` | qui est touché, et de combien |

Les fiches ont repris le 26 septembre 2026 les lignes du registre de veille,
sous le même identifiant. Le registre, `data/reference/legislation/veille.yaml`,
garde les **sources à consulter** à chaque session, et le **journal** où chaque
session consigne ce qu'elle a consulté, trouvé et laissé.

**Le script** : `python scripts/veille_droit.py`, une vue de la carte. Il
imprime les fiches à relire — état `a_verifier` ou `manquante`, lecture de
plus de cent vingt jours, date de relecture passée — et la liste des sources.
`--tout` imprime tout, `--strict` rend 1 s'il reste quelque chose à relire.

**Les tests** : `tests/test_carte.py` impose la forme des fiches, exige que
chaque exemple cité existe, et que toute réforme du calendrier
(`reformes.yaml`) datée de 2023 ou après ait sa fiche ; `tests/test_donnees.py`
tient le journal. Ajouter une réforme sans la lire à la source et sans
l'inscrire dans une fiche fait échouer la suite.

## La règle, pour toute session qui touche au scénario 1

**Au début.** Lancer `python scripts/veille_droit.py`. Lire les fiches à
relire. Mettre à jour l'index LEGI (`python scripts/fetch/dila_index.py legi
--mettre-a-jour`), puis `python scripts/textes.py --inscrire` : les
rédactions parues depuis entrent dans la liste de contrôle des textes, « à
examiner ». Consulter les sources listées pour tout texte paru depuis la
dernière date du journal : loi de financement de l'année et ses décrets,
circulaires Cnav, dates « Vérifié le » des fiches service-public, décrets
retraite au Journal officiel par l'index DILA.

**Pour chaque règle qu'on écrit ou modifie.**

1. Lire le texte sur Légifrance, dans sa version en vigueur à la date d'effet,
   et noter l'identifiant et la date de version.
2. Lire comment la caisse l'applique : circulaire Cnav, fiche service-public,
   documentation SRE ou CNRACL. C'est là que sont les coupures au mois, les
   arrondis, les dates d'effet.
3. Chercher un exemple chiffré publié. S'il existe, il entre dans
   `exemples_officiels.yaml` et le test le rejoue. S'il n'existe pas, la
   fiche reste `transcrite`. Si le modèle ne le reproduit pas, il entre
   quand même, en écart connu : la valeur que rend le modèle et
   l'explication, dans son champ `ecart_connu`, et la fiche passe à
   `approchee` ou `a_verifier`.
4. Écrire la fiche, ou la mettre à jour : lectures, dates, état. Chaque
   rédaction lue y prend son statut, par son identifiant : citée par une
   version, sans effet avec le mot à mot qui le montre, ou à rattacher. C'est
   ce qui fait baisser le cliquet des textes (`python scripts/textes.py`).
5. Donner à la donnée le niveau de fiabilité qu'elle mérite (`certifiee` si
   recontrôlée automatiquement, `haute` si lue, `moyenne` si lue mais
   susceptible d'être dépassée avant recontrôle), et laisser ce niveau
   remonter au résultat.

Ce qui est interdit : déduire une valeur d'une autre sans le dire (« les
lignes intermédiaires suivent le même pas »), citer un texte de mémoire,
appliquer une règle à une population que le texte ne nomme pas, et laisser
une table certifiée sans date.

**À la fin.** Ajouter une entrée au `journal` : la date, ce qui a été
consulté, ce qui a été trouvé, ce qui reste. Mettre à jour `sources.lu_le`
et `sources.prochaine_relecture` des fiches relues. Régénérer les témoins,
lancer la suite, commiter sur `main`.

Une fiche `transcrite` attend son exemple. Une fiche `manquante` ou
`approchee` est mesurée dans `limites.md`. Une fiche `a_verifier` est ce que
la session n'a pas pu finir de lire, et c'est par elle que la suivante
commence : `python scripts/veille_droit.py` le dit. Combien de fiches la
carte porte, dans quel état, et combien d'exemples les rejouent : le tableau
de bord, `docs/etat.md`.
