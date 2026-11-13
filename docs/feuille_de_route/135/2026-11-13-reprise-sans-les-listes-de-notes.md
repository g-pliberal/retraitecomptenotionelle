# `reprise.py` sans les listes de notes, et la course de GitHub relevée

**Le 13 novembre 2026.** Demandé par le propriétaire, par la session
d'orchestration : `CLAUDE.md` envoie la session qui cherche quoi faire à
`python scripts/reprise.py`, dont la sortie dépassait tout le contexte de
départ d'une session.

**Le constat, refait** sur `main` à cc760a7. Sans numéro, le script imprimait
197 318 octets, 190 477 caractères en 1 840 lignes. Les listes de notes en
faisaient 855 lignes : 272 pour l'action 138, 110 pour la 130, 73 pour la 161.
Vingt-huit actions sont en cours.

**Ce que le défaut coûtait vraiment.** La sortie n'entrait pas dans le
contexte. L'outil Bash d'une session web l'écarte : « Output too large
(192.7KB) », le tout rangé dans un fichier du conteneur, sous
`/root/.claude/projects/…/tool-results/`, et seuls ses deux premiers
kilo-octets montrés. La session voyait donc le bloc de l'action 47 et le début
de celui de la 89, rien des vingt-six autres. Elle ne payait les 50 000 à
60 000 jetons estimés que si elle relisait ensuite ce fichier par fenêtres.
Le seuil est à 31 000 caractères au plus : une sortie de cette taille,
essayée, est écartée de même (« 31.2KB »). Il n'a pas été cherché plus bas, et
aucun réglage du dépôt ne le fixe.

**Ce qui est fait.** Sans numéro, le script n'imprime plus que les blocs
« Reprise », celui de chaque action en cours et ceux de ses étapes
inachevées ; les notes d'une action tiennent en une ligne : « Notes : 34, dans
docs/feuille_de_route/135/ ; \`python scripts/reprise.py 135\` les liste. »
Avec un numéro, rien ne change : la sortie de `reprise.py 135` est la même à
l'octet près avant et après. Le test,
`test_sans_numero_reprise_n_imprime_que_les_blocs` (`tests/test_prose.py`),
joue les deux appels sur une feuille de route de trois actions écrite pour
lui, la sortie attendue posée à la main ; il a été vu rouge, la liste
imprimée. `main` prend pour cela la racine du dépôt en argument.

**La mesure, après** : 72 989 octets, 70 916 caractères en 985 lignes. C'est
2,7 fois moins, et c'est encore plus du double du seuil : sans numéro, la
sortie reste écartée, deux kilo-octets montrés. Le gain réel est pour la
session qui relit le fichier écarté, 73 Ko au lieu de 197.

**Les documents mis d'accord** : la phrase de `CLAUDE.md` (« Au démarrage, le
bloc « Reprise » seul »), qui reste à 194 lignes, et le point 3 de la carte du
dépôt. Restent vrais tels quels, et laissés : le premier paragraphe de
`CLAUDE.md`, le préambule de la feuille de route, l'architecture (§ 9), les
agents `eclaireur` et `Explore`, qui citent `reprise.py <action>`. Aucun hook
ni réglage ne cite le script ; `pousser.sh` ne nomme qu'un test voisin,
inchangé.

**Ce qui reste, jugé sans le faire.**

- *Sans numéro, les blocs seuls ne tiendront pas sous le seuil.* Les 70 916
  caractères se partagent ainsi : 25 962 pour les vingt-huit blocs d'action,
  dont 5 278 pour celui de la 130, que sa session récrit ; 34 012 pour
  quarante-sept blocs d'étape ; le reste en titres et en renvois. Tous les
  blocs d'action à 150 mots et aucun bloc d'étape, la sortie ferait encore
  30 000 caractères environ. Pour qu'elle entre en entier, il faudrait un
  sommaire : une ligne par action — son numéro, son titre, la date de son
  bloc, ses notes, ses étapes inachevées —, 5 Ko environ, la session lisant
  ensuite `reprise.py <numéro>`. C'est au propriétaire d'en décider :
  `CLAUDE.md` promet aujourd'hui les blocs.
- *Les blocs d'étape.* L'action 186 en porte vingt-trois (14 433 caractères),
  datés du 7 au 10 novembre ; la 138, seize (13 268), datés du 13 octobre au
  6 novembre. Un bloc d'étape s'ôte quand l'étape finit : ceux d'octobre sont
  à revoir par la session de chaque action. Non vérifié ici, étape par étape.
- *Avec un numéro*, `reprise.py 138`, l'exemple que donne `CLAUDE.md`, imprime
  58 916 caractères, dont les trois quarts pour ses 272 notes : il est écarté
  lui aussi. Les autres passent : 22 803 pour la 186, 19 244 pour la 130,
  14 290 pour la 161.
- *Les blocs d'action de plus de 150 mots*, au décompte du script : 130 (913),
  158 (183), 151 (167), 131 (162). Tous sont datés d'avant le 11 novembre, et
  gardent la règle d'avant jusqu'à ce que la session de leur action les
  récrive. Celui de la 184, du 12 novembre, est à 150 mots juste.

**La course de GitHub, relevée** par l'API (`list_workflow_jobs`), revérifiée
ce jour. La note du 12 novembre attendait la durée de la première course
servie par la mémoire des calculs.

| | course n° 1749, le 12 à 17 h 17 UTC | course n° 1753, le 12 à 21 h 49 UTC |
|---|---|---|
| la fabrique | 1 min 11 | 6 min 05 |
| la suite complète | 14 min 38 | 21 min 53 |
| la garde des présomptions | 1 min 28 | 1 min 35 |
| le job, du début à la fin | 17 min 37 | 29 min 58 |

La première (43267895988) est partie mémoire pleine, à en juger par sa
fabrique ; la seconde (43314082381) sans mémoire, le modèle ayant bougé. Donc
17 min 37, et non les 9 min 17 mesurées en session : la suite reste longue
sur GitHub même mémoire pleine, 14 min 38 contre 410 s. Sans mémoire, elle est
passée de 18 min 07 le 11 novembre à 21 min 53 le 12. La session
d'orchestration relève qu'une seule des six dernières courses vertes est
partie mémoire pleine, l'action 161 touchant le modèle à presque chaque
envoi : non revérifié ici. `tests.yml` est une garde, et n'a pas été touché ;
le propriétaire n'a rien décidé là-dessus.
