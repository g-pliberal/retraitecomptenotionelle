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
garde les **sources à consulter** à chaque session. Le **journal**, où chaque
session consigne ce qu'elle a consulté, trouvé et laissé, tient une entrée par
fichier, dans `data/reference/legislation/journal_de_veille/` : depuis le
6 octobre 2026 (action 148), deux sessions qui consignent leur veille le même
jour n'écrivent plus au même endroit.

**Le script** : `python scripts/veille_droit.py`, une vue de la carte. Il
imprime les fiches à relire — état `a_verifier` ou `manquante`, lecture de
plus de cent vingt jours, date de relecture passée — et la liste des sources.
Chacune y vient avec ses questions ouvertes, sauf celle qui n'est à relire
que pour une rédaction non lue (étape 4, plus bas), qui tient en une ligne.
`--tout` imprime tout, `--strict` rend 1 s'il reste quelque chose à relire.
Il compare aussi la base de législation de la Cnav à son registre,
`data/reference/legislation/cnav/` (`scripts/fetch/cnav_veille.py`, action
175) : ce qu'elle a changé depuis — un barème ou un exposé dont la date a
changé depuis son sort, un objet neuf ou parti, une circulaire nouvelle, une
référence que sa recherche sert sans que le registre la porte —, et ce que le
registre garde à lire. Une base qui ne répond pas se dit d'une ligne ;
`--sans-cnav` ne la demande pas.

**Les tests** : `tests/test_carte.py` impose la forme des fiches, exige que
chaque exemple cité existe, et que toute réforme du calendrier
(`reformes.yaml`) datée de 2023 ou après ait sa fiche ; `tests/test_donnees.py`
tient le journal ; `tests/test_cnav_legislation.py`, le registre de la base de
la Cnav et sa veille. Ajouter une réforme sans la lire à la source et sans
l'inscrire dans une fiche fait échouer la suite.

## La règle, pour toute session qui touche au scénario 1

**Au début.** Lancer `python scripts/veille_droit.py`. Lire les fiches à
relire. Les rédactions parues entrent dans la liste de contrôle des textes,
« à examiner », sans que la session ait à le faire : chaque lundi, GitHub met
à jour l'index LEGI, lance `python scripts/textes.py --inscrire` et commite
ce qu'elle écrit (`.github/workflows/index-dila.yml`,
`scripts/publier_inscription.sh`) ; `data/reference/textes/inscription.yaml`
dit jusqu'où l'index a été lu. Reste à la session l'inscription qui ne peut
pas attendre le lundi : quand elle cite dans une fiche un texte que la liste
ne tient pas encore, ou qu'elle lit un texte paru dans la semaine, elle
récupère l'index (`python scripts/fetch/dila_index.py legi --recuperer`, puis
`--mettre-a-jour`) et lance `--inscrire` elle-même. Un texte général, dont la
retraite n'occupe que quelques articles, se déclare dans `perimetre.yaml`
(`textes_generaux`) avant de l'inscrire : il n'entre alors que par les
articles cités. Consulter les sources listées pour tout texte paru depuis la
dernière date du journal : loi de financement de l'année et ses décrets,
circulaires Cnav, dates « Vérifié le » des fiches service-public, décrets
retraite au Journal officiel par l'index DILA. Ce que le script dit de la base
de la Cnav entre au registre par `python scripts/fetch/cnav_legislation.py` :
le neuf à lire, ce qui attend avec sa date du jour ; ce qui a changé depuis son
sort se relit, par le script ou le test que le registre nomme, et le sort
avec.

**Pour chaque règle qu'on écrit ou modifie.**

1. Lire le texte sur Légifrance, dans sa version en vigueur à la date d'effet,
   et noter l'identifiant et la date de version.
2. Lire comment la caisse l'applique : circulaire Cnav, fiche service-public,
   documentation SRE ou CNRACL. C'est là que sont les coupures au mois, les
   arrondis, les dates d'effet.
3. Chercher un exemple chiffré publié. S'il existe, il entre dans
   `exemples_officiels.yaml` avant la moindre ligne du code, et le test qui
   le rejoue se voit échouer (le test d'abord, `CLAUDE.md`) ; le code le fait
   passer. S'il n'existe pas, la fiche reste `transcrite`, et le test d'abord
   est un cas posé à la main depuis le texte. Si le modèle ne le reproduit
   pas, il entre quand même, en écart connu : la valeur que rend le modèle
   et l'explication, dans son champ `ecart_connu`, et la fiche passe à
   `approchee` ou `a_verifier`.
4. Écrire la fiche, ou la mettre à jour : lectures, dates, état. Chaque
   rédaction lue y prend son statut, par son identifiant : citée par une
   version, sans effet avec le mot à mot qui le montre (`dila_cherche.py legi
   --num <article> --diff`), ou à rattacher. C'est
   ce qui fait baisser le cliquet des textes (`python scripts/textes.py`).
   Les rédactions en vigueur ou à venir que la fiche n'a pas lues des
   articles qu'elle cite, et leur mot à mot, sont dans `python
   scripts/textes.py --non-lues <fiche>`, les passées avec `--toutes` ;
   une rédaction « (texte inchangé) » s'y déclare sans effet. La veille
   compte parmi les fiches à relire celles qui en ont une en vigueur ou à
   venir.
5. Donner à la donnée le niveau de fiabilité qu'elle mérite (`certifiee` si
   recontrôlée automatiquement, `haute` si lue, `moyenne` si lue mais
   susceptible d'être dépassée avant recontrôle), et laisser ce niveau
   remonter au résultat.

Ce qui est interdit : déduire une valeur d'une autre sans le dire (« les
lignes intermédiaires suivent le même pas »), citer un texte de mémoire,
appliquer une règle à une population que le texte ne nomme pas, et laisser
une table certifiée sans date.

**À la fin.** Écrire l'entrée du journal, dans un fichier neuf de
`journal_de_veille/` nommé de la date et du sujet de la session
(`2026-10-06-action-148-etape-2.yaml`) : `date`, `session`, ce qui a été
consulté (`consulte`), ce qui a été trouvé (`trouve`), ce qui reste
(`reste`). Mettre à jour `sources.lu_le` et `sources.prochaine_relecture` des
fiches relues. Lancer `python -m pytest -m rapide` et les tests de sa zone,
commiter sur `main` : GitHub refait les témoins et joue la suite complète.

Une fiche `transcrite` attend son exemple. Une fiche `manquante` ou
`approchee` est mesurée dans `limites.md`. Une fiche `a_verifier` est ce que
la session n'a pas pu finir de lire, et c'est par elle que la suivante
commence : `python scripts/veille_droit.py` le dit. Combien de fiches la
carte porte, dans quel état, et combien d'exemples les rejouent : le tableau
de bord, `docs/etat.md`.

## Chercher dans le JORF ou LEGI

Ne pas retélécharger les dumps de la DILA : l'index plein texte du champ
social se récupère en une minute depuis la release `index-dila` du dépôt, que
le workflow `index-dila.yml` tient à jour chaque lundi. Si `--recuperer`
répond qu'aucun index n'est publié, lancer ce workflow (onglet Actions, « Run
workflow ») : une session ne peut pas publier elle-même.

```bash
python scripts/fetch/dila_index.py jorf --recuperer      # une fois par session
python scripts/fetch/dila_index.py jorf --mettre-a-jour  # les incréments parus depuis
python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale")' --jusqu 1981
python scripts/fetch/dila_cherche.py jorf --texte JORFTEXT000000568533 --motif mensuel
python scripts/fetch/dila_cherche.py legi '"sur la base de" heures' --num R351-9
python scripts/fetch/dila_cherche.py legi --num L161-17-2                  # son histoire
python scripts/fetch/dila_cherche.py legi --num L161-17-2 --diff           # mot à mot
python scripts/fetch/dila_cherche.py legi --num L161-17-2 --le 2026-03-01  # ce jour-là
```

Lire les extraits, pas les textes : `--compter` d'abord si la requête est
large, `--limite` ensuite, `--texte ID --motif` pour ne lire que les fenêtres
utiles. L'histoire d'un article se lit sans requête (action 184) : `--num`
seul liste ses versions, texte par texte, et `--titre` départage deux codes
qui portent le même numéro ; `--diff` imprime ce que chaque version change,
mot à mot, ou « (texte inchangé) » ; `--motif` suit une expression de version
en version. `--le` rend la version en vigueur un jour donné, la précédente, et
les phrases où le texte dit à quoi il s'applique : la version en vigueur le
jour d'effet d'une pension n'est pas toujours celle qui la régit, et c'est
cette phrase, lue, qui le dit. Chaque réponse rappelle, sur la sortie
d'erreur, le jour où l'index s'arrête. L'index ne contient que le champ social (`THEMATIQUE` dans
`dila_index.py`) : ce qu'il ne trouve pas peut exister dans le dump, que les
scripts de certification lisent encore par leur option `--dump`.

KALI, la base des conventions collectives, qui porte les accords Agirc-Arrco,
se lit par les mêmes commandes (action 184, étape 5) :

```bash
python scripts/fetch/dila_index.py kali --recuperer
python scripts/fetch/dila_index.py kali --mettre-a-jour
python scripts/fetch/dila_cherche.py kali '"valeur de service"' --titre agirc-arrco
python scripts/fetch/dila_cherche.py kali --num 92 --dans KALITEXT000036731682 --diff
python scripts/fetch/dila_cherche.py kali --num 92 --dans KALITEXT000036731682 --le 2026-11-01
```

Elle est dans l'index entière, sans filtre : ne rien y trouver dit que KALI ne
l'a pas. Chaque ligne y ajoute l'état du document — « en vigueur étendu »,
« remplacé », « périmé » —, le numéro de sa convention (IDCC) et le texte qui
porte l'article. Un numéro n'y désigne un article que dans son texte :
l'histoire d'un article se demande par `--num` et `--dans KALITEXT…`,
l'identifiant que la recherche imprime ; `--dans` et `--idcc` bornent aussi
une recherche. L'accord du 17 novembre 2017, qui fonde le régime Agirc-Arrco,
est `KALITEXT000036731682`. Sa mise à jour reconstruit l'index, en quelques
minutes, quand la DILA a renouvelé son dump.
