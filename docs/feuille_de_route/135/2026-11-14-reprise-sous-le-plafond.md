# `reprise.py <numéro>` sous le plafond de Bash : une ligne par étape quand leurs blocs n'y tiennent pas

**Le 14 novembre 2026**, à la demande de la session d'orchestration, sur une
décision du propriétaire du même jour : ne pas relever le plafond de la sortie
de Bash pour les actions 138 et 186, mais raccourcir ce que `reprise.py` en
imprime (« On utilise tes recommandations »). Depuis ce matin, une session ne
reçoit que les 2 000 premiers caractères d'une sortie de plus de 10 000, et le
chemin d'un fichier : celle qui ouvrait une étape de ces deux actions ne lisait
plus son bloc « Reprise » d'un seul geste.

**La mesure**, sur `main` à bbc19d0.

| Sortie | Caractères | Octets | Bloc de l'action | Liste des notes | Blocs d'étape |
|---|---|---|---|---|---|
| `reprise.py 138` | 20 466 | 21 125 | 856 | 4 862 | 14 714, pour seize |
| `reprise.py 186` | 17 315 | 17 858 | 1 070 | 4 010 | 12 191, pour vingt et un |

Ce sont les blocs d'étape qui pèsent, non la liste des trente dernières notes.
Aucune autre action en cours ne dépasse : la plus longue ensuite est la 175,
7 708 octets.

**Le remède noté le 13 novembre ne suffisait pas.** Il était d'ôter les blocs
des étapes finies. Les trente-sept blocs ont été lus ici, un à un. Deux
seulement disent leur étape finie, à la 186 : « Cette note n'a plus rien à
faire » (`2026-11-07-planchers-etude.md`, `2026-11-09-rendement-net.md`) ; un
troisième n'attend que la refonte du site (`2026-11-09-protocole-test.md`). À
la 138, deux disent qu'il ne reste rien au site, mais portent des questions au
propriétaire (`2026-10-07-etape-3-reportes-en-emploi.md`,
`2026-10-16-etape-7-naissances-et-migrations-dans-les-pages.md`). Tous les
autres portent un « Reste » — un texte à lire au fac-similé, une session du
modèle ou du site — ou une question qui attend le propriétaire. Pour passer
sous le plafond, il aurait fallu ôter onze des seize blocs de la 138 : des
blocs d'étapes inachevées, dont rien d'autre ne résume ce qui reste. Et la
règle (`.claude/rules/documentation.md`) dit qu'une étape ôte son bloc en
finissant, sans dire où il va.

**Ce qui est fait : aucun bloc n'est ôté, c'est ce que le script imprime qui
change.** `python scripts/reprise.py <numéro>` imprime comme avant le bloc de
l'action, ses trente dernières notes et les blocs de ses étapes inachevées,
tant que le tout tient sous `SORTIE_AU_PLUS`, compté en octets. Sinon, chaque
étape inachevée se réduit à une ligne — le nom de sa note, la date de son
bloc — sous deux lignes qui disent comment lire le bloc d'une étape :
`python scripts/reprise.py 138 etape-14`. Ce mot, ou cette suite de mots, se
cherche entier dans le nom des notes (« etape-1 » ne prend pas « etape-14 ») ;
le script imprime alors le bloc de l'action, les notes dont le nom le porte,
les trente dernières, et le bloc de l'étape s'il y en a un. Plusieurs mots
s'ajoutent. Un mot sans numéro d'action est refusé.

| Sortie | Caractères | Octets |
|---|---|---|
| `reprise.py 138` | 7 006 | 7 282 |
| `reprise.py 186` | 6 465 | 6 689 |
| `reprise.py 138 etape-14` | 7 599 | 7 909 |
| `reprise.py 186 complementaires` | 3 482 | 3 588 |

Les autres actions gardent leur sortie d'avant, au caractère près : leurs
blocs d'étape tiennent.

**Le test**, écrit d'abord et vu rouge :
`test_reprise_tient_une_action_sous_le_plafond_de_bash`
(`tests/test_prose.py`). Sur une feuille de route d'essai, vingt et un blocs
d'étape de plus de 12 000 caractères : la sortie passe sous le plafond, une
ligne par étape ; le mot du nom rend le bloc et les notes d'une étape. Sur le
dépôt, chaque action en cours tient sous le plafond : rouge avant le code
pour la 138 et la 186, et elles seules.

**Constaté dans cette session** : une sortie de 9 500 octets est entrée
entière, une de 11,5 Ko a été rangée dans un fichier. Les tests rapides et
ceux de la prose sont verts.

**Ce qui reste, et ce qui n'est pas vérifié.**

- *Les blocs des étapes finies* restent à ôter par la session de chaque
  action : les trois de la 186 nommés plus haut, et, à la 138, ceux que le
  propriétaire dira clos une fois ses questions répondues. Ce n'est plus une
  affaire de taille.
- *`CLAUDE.md`* dit encore que `reprise.py 138` imprime « les blocs d'une
  action » : c'est vrai quand ils tiennent, et la sortie dit elle-même comment
  lire le bloc d'une étape sinon. Il n'a pas été retouché, une autre session y
  travaillant ce jour.
- *Si Bash compte des caractères ou des octets* n'a pas été établi : le script
  et le test comptent des octets, qui majorent.
- *Le test porte sur le dépôt* : il rougirait `main` si la sortie d'une action
  passait le plafond même réduite. La 138 en est à 7 282 octets ; une étape de
  plus y ajoute une ligne de 70 octets environ, et la liste des notes est
  bornée à trente. Deux numéros à la fois, `reprise.py 138 186`, ne sont pas
  tenus par le test.
