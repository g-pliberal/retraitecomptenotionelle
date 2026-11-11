# `CLAUDE.md` sous 200 lignes

**Le 11 novembre 2026, à la demande du propriétaire**, deuxième des quatre
chantiers de la note `2026-11-11-plateforme-claude.md`. Le `CLAUDE.md` de la
racine passe de 265 lignes à 194, et de 16 892 caractères à 11 858, sans
perdre une règle. Ce qui ne vaut que pour une partie du dépôt le quitte pour
trois règles à portée de chemin, sous `.claude/rules/` ; la relève de la
session d'orchestration, pour un skill ; ce qui ne regarde qu'un poste, pour
`docs/poste.md`. `tests/test_consignes.py` tient la limite.

**La source.** `memory.md`, dans la documentation de Claude Code : « target
under 200 lines per CLAUDE.md file. Longer files consume more context and
reduce adherence. Move instructions that matter for only part of the codebase
into path-scoped rules, which load only when Claude works with matching
files. » Un import `@chemin` range sans alléger : le fichier importé se
charge avec celui qui l'importe. Une règle sans champ `paths` se charge à
l'ouverture, comme la racine. Une procédure va dans un skill, dont seule la
description pèse au départ.

**Le classement**, soumis au propriétaire avant tout déplacement, et approuvé
en entier. La racine faisait alors 259 lignes, et les candidats relevés
d'avance — la prose, la documentation, le clone d'avant le 26 septembre, les
branches `claude/*`, la relève — n'en ôtaient que 35 des 60 à trouver. S'y
sont ajoutés « Rien ne se perd », le détail des conflits du rebasage, la
mécanique de la suite, les deux gardes du test d'abord et la façon de récrire
le bloc « Reprise ».

| Ce qui part | Où | Ce qui en reste à la racine |
|---|---|---|
| « La prose », « Rien ne se perd », ce que `pousser.sh` règle seul au rebasage, le conflit d'ancres | `.claude/rules/prose.md` | « Jamais `git checkout --theirs` sur un fichier de prose » : le geste n'ouvre aucun fichier |
| « La documentation, au plus court », la façon de récrire le bloc « Reprise », la clôture d'une action | `.claude/rules/documentation.md` | le chemin de la note et de l'entrée du journal, « la session qui avance l'action le récrit », le message de commit de cinq lignes |
| la répartition de la suite, les niveaux, les tests du site, les deux gardes du test d'abord | `.claude/rules/tests.md` | le test d'abord, et quels tests lancer |
| le clone d'avant le 26 septembre 2026, les branches `claude/*`, les deux `git config` | `docs/poste.md` | une puce, qui y renvoie et nomme le cas grave de `pousser.sh` |
| la relève de la session d'orchestration | le skill `orchestration` | une puce, qui dit la règle en une phrase et nomme le skill |

Restent entiers à la racine : la publication sur `main` et ce que
`pousser.sh` refuse, « Économiser le contexte », la mise en route, les
dépendances, les listes de contrôle, le scénario 1. La puce « Les consignes
d'une zone » devient l'index des règles.

**Le mécanisme, vu en vrai** dans cette session web (Claude Code 2.1.322),
sur des règles d'essai puis sur les vraies.

- Une règle se charge à l'outil Read, à l'outil Write, et à un `head` ou un
  `sed -n` lancés seuls sur un fichier de sa portée. Elle ne se charge ni à
  l'outil Grep, ni à une commande composée (`cd … && head … | cut`), ni à une
  écriture par heredoc, ni à un script qui lit le fichier, `reprise.py`
  compris. D'où la dernière phrase de l'index : qui ne travaille que par eux
  lit la règle d'abord.
- À l'écriture, la règle arrive avec le résultat du Write, donc après lui. La
  racine garde ce qu'il faut savoir avant d'écrire : le chemin de la note, et
  que la session récrit le bloc « Reprise ».
- La lecture d'une note, `docs/feuille_de_route/135/…`, a chargé ensemble
  `prose.md` et `documentation.md`. C'est le cas ordinaire : une session lit
  dès ses premiers appels la note que son bloc « Reprise » nomme.
- Les quatre formes de motif se chargent comme la documentation les décrit :
  `/README.md` pour le fichier de la racine, `CLAUDE.md` à toute profondeur,
  `.claude/rules/**` malgré le dossier caché, un chemin exact.
- Une règle créée en cours de session vaut aussitôt, et le skill est apparu
  dans la liste des skills dès son fichier écrit.

**Rien de perdu.** `python scripts/conservation.py --depuis HEAD` retrouve
les puces parties entières — « La prose », « Rien ne se perd », le clone, les
branches — et signale les neuf paragraphes de la racine découpés exprès, avec
le tableau de la carte du dépôt, dont une ligne change. Ces neuf-là sont
vérifiés proposition par proposition : des 186 de l'ancienne racine, 179 se
retrouvent mot pour mot dans ce qui la remplace. Les 7 autres sont les
reformulations voulues : le renvoi à « La documentation, au plus court »
devenu le chemin de la note, « Deux gardes tiennent la règle » devenu « le
test d'abord », l'index et ses deux phrases, le sujet de deux phrases du bloc
« Reprise », le point final du titre de la relève.

**L'outillage.** `verifier_prose.consigne` compte `.claude/rules/*.md`, à
toute profondeur, parmi les consignes : la prose les tient en régime `etat`,
la conservation les suit, et l'étape « prose » de la fabrique les lit, sans
quoi un chiffre ancré d'une règle aurait pu dériver sans que le poste le voie.
Le reste de `.claude/` reste à l'outillage : le skill n'est pas suivi.
`tests/test_consignes.py`, dans la suite rapide, tient quatre choses : moins
de 200 lignes pour la racine, chaque consigne de dossier et chaque règle, en
lignes de la largeur que `reprise.py` donne au bloc « Reprise » ; un fichier
du dépôt qui réponde à chaque motif de chaque règle ; la règle que charge
chaque sorte de fichier ; la racine qui nomme chaque règle, la page du poste
et le skill.

**Ce que le propriétaire doit savoir.**

- *Le gain est d'adhérence, peu de jetons.* La racine perd 30 % de ses
  caractères, mais les deux règles de `docs/` reviennent dans presque toute
  session, à sa première note lue.
- *Les éclaireurs les reçoivent aussi*, malgré `omitClaudeMd`, quand ils
  lisent un fichier de leur portée (`sub-agents.md`). Leur carte nomme
  désormais `.claude/rules/`. La comparaison que prévoit la note
  `2026-11-11-eclaireurs-sans-le-claude-md-racine.md` se fera donc avec ces
  règles en place.
- *Le clone d'avant le 26 septembre* était resté à la racine le 7 octobre, à
  la demande du propriétaire, parce que `pousser.sh` y renvoie dans le cas
  grave. Il part cette fois : la puce « Sur un poste » nomme le cas grave et
  mène à la page.
- *La consigne d'écriture du bloc « Reprise »*, arrivée à la racine le même
  jour par le troisième chantier, a suivi le classement : elle est dans
  `documentation.md`. La racine garde la mesure, 150 mots.
- *`pousser.sh`*, quand il refuse une feuille de route, renvoie encore à
  `CLAUDE.md` ; la règle des notes est dans `documentation.md`, que l'index
  nomme. Le message n'a pas été retouché : c'est une garde.
- *Un fil de projet claude.ai* ne charge ni ces règles, ni les `CLAUDE.md` de
  dossier, ni les hooks (`claude-projects.md`).
- *Après une compaction*, la racine est réinjectée ; une règle ne revient
  qu'à la prochaine lecture d'un fichier de sa portée.

**Reste.** Rien pour ce chantier. La marge est de cinq lignes : une règle de
plus à la racine en déplace une autre.
