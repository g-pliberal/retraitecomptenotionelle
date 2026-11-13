# `reprise.py` en sommaire, et les trente dernières notes d'une action

**Le 13 novembre 2026**, à la suite de la note de ce jour sur les listes de
notes. Elle laissait deux choix au propriétaire, qui les a confiés à la
session (« Concernant les choix, je te fais confiance ») : ce que le script
imprime sans numéro, et la sortie de `reprise.py 138`.

**Le défaut qui restait.** L'outil Bash d'une session écarte une sortie trop
longue, dont il ne montre que les deux premiers kilo-octets : constaté à
31 000 caractères. Sans les listes de notes, la sortie sans numéro en faisait
encore 70 916 ; celle de `reprise.py 138`, l'exemple que donne `CLAUDE.md`,
58 916. Ni l'une ni l'autre n'entrait dans le contexte de la session qui la
demandait.

**Sans numéro, le sommaire.** Une ligne par action en cours : son numéro, son
titre, la date de son bloc « Reprise », ses notes et ses étapes inachevées,
sous deux lignes qui renvoient à `reprise.py <numéro>`. Mesuré sur `main` à
05c6df9 : 4 338 octets en 31 lignes, pour vingt-huit actions. Les blocs seuls
n'auraient pas tenu : vingt-huit blocs de 150 mots font déjà 30 000
caractères environ.

**Avec un numéro, les trente dernières notes.** Le bloc de l'action et ceux de
ses étapes inachevées s'impriment comme avant ; la liste des notes s'arrête
aux trente plus récentes, et son en-tête compte les autres : « les 30
dernières de 272 (\`--toutes\` les liste toutes) ». `--toutes` rend la liste
entière. Les sorties les plus longues : 22 055 caractères pour l'action 186,
20 466 pour la 138, 7 103 pour la 161, 5 150 pour la 130. Une sortie de la
taille de celle de la 186, essayée, entre en entier.

**Les tests** (`tests/test_prose.py`), vus rouges, sur une feuille de route de
trois actions écrite pour eux, la sortie attendue posée à la main :
`test_sans_numero_reprise_n_imprime_qu_un_sommaire`, qui tient aussi le
sommaire du dépôt sous 15 000 caractères, la moitié du seuil ;
`test_avec_un_numero_reprise_imprime_les_blocs_et_les_dernieres_notes`. Le
test du matin, qui disait les blocs sans les listes, est remplacé par eux.

**Les documents mis d'accord** : les deux phrases de `CLAUDE.md`, à 196
lignes ; la carte du dépôt, son point 3 et son tableau ; le préambule de la
feuille de route et l'architecture (§ 9), qui disaient que le script, sans
numéro, imprime les blocs.

**Ce qui reste.**

- *Aucun test ne tient la sortie d'une action sous le seuil.* Celle de la 186
  en est à 22 055 caractères, dont les deux tiers pour vingt-quatre blocs
  d'étape ; celle de la 138, à 20 466, dont seize blocs d'étape datés du
  13 octobre au 6 novembre. Un test sur le dépôt rougirait `main` pour une
  session qui ajoute une étape à une autre action : laissé. Les blocs d'étape
  sont à revoir par la session de chaque action, qui ôte ceux des étapes
  finies.
- *Les blocs d'action de plus de 150 mots* — 158, 151, 131 — se récrivent à
  la prochaine session de leur action. Celui de la 130 a été récrit ce jour.
- *La course de GitHub* reste à 17 min 37 mémoire pleine et 30 minutes sans.
  `tests.yml` est une garde : la raccourcir demande l'accord du propriétaire
  sur un changement précis, qu'aucune session n'a encore proposé.
