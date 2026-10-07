# Le contexte, étape 3 : `CLAUDE.md` par zone

**Reprise, au 7 octobre 2026.** Après l'étape 2, dont elle reprend le hook.
`CLAUDE.md`, 18 644 caractères, est relu à chaque appel de chaque session. Les
règles d'une seule zone vont dans un `CLAUDE.md` de son dossier, que Claude
Code ne charge qu'à la première lecture ou retouche d'un fichier de ce
dossier : `src/`, `moteur/`, `data/`. La veille du droit et la recherche dans
le JORF vont dans `docs/veille_droit.md`, une ligne gardant leur déclencheur ;
la liste des fichiers à ne jamais lire en entier cède au hook. Cible : vers
10 000 caractères. Commencer par étendre `conservation.py` aux `CLAUDE.md` des
dossiers, qu'il ne lit pas. Détail : ce fichier.

**Le 7 octobre 2026, ce qui est établi.**

- *Le poids de `CLAUDE.md`, section par section, en caractères* : le
  préambule 753 ; « Git : tout va sur `main` » 4 632 ; « Économiser le
  contexte » 2 035 ; « Travailler » 7 355, dont les mémoires 1 205, la
  documentation 1 104, les tests 828, le Python qui fait foi 733, la prose
  558, les données 554, la mise en route 530, « Rien ne se perd » 483, le site
  457, la proposition 398 ; « Listes de contrôle » 1 288 ; le scénario 1,
  1 388 ; le JORF et LEGI, 1 193.
- *Ce qu'il pèse.* Dans la session qui a écrit l'arbre, le contexte de départ,
  56 000 jetons dont 5 000 à 6 000 pour `CLAUDE.md`, a fait 27 % des jetons
  relus, en 90 appels (étape 1). La part baisse quand la session s'allonge,
  mais toutes la paient.
- *Le mécanisme* (documentation de Claude Code). Un `CLAUDE.md` placé dans un
  sous-dossier ne se charge pas au démarrage, mais quand la session lit ou
  modifie un fichier de ce dossier ; lancer un script qui s'y trouve ne le
  charge pas. Une règle qui doit valoir avant toute lecture, comme la veille
  au début d'une session qui touche au scénario 1, garde donc une ligne à la
  racine.
- *Les zones* sont celles des sessions parallèles (`CLAUDE.md`, « Plusieurs
  sessions en parallèle ») : le modèle et son portage, les données et la
  certification, le site.

**Le plan.**

1. `scripts/conservation.py` ne lit que les `.md` de la racine et de `docs/`
   (`Arbre.documents`) : un paragraphe déplacé vers `src/CLAUDE.md` y serait
   compté perdu. L'étendre d'abord aux `CLAUDE.md` des dossiers, avec son test.
   De même `data/reference/prose/zones.yaml`, où chaque nouveau `CLAUDE.md`
   prend son régime (`etat`, comme celui de la racine), et
   `tests/test_prose.py`, qui exige qu'un document y soit déclaré.
2. `src/CLAUDE.md` : « Le Python de `src/` fait foi », les mémoires, la liste
   de contrôle d'un changement du modèle. `moteur/CLAUDE.md` : le texte du
   site, les listes d'une retouche de `pages.js` et d'un champ de saisie,
   l'outillage d'interface. `data/CLAUDE.md` : les données, la proposition.
3. `docs/veille_droit.md` reçoit les obligations du scénario 1 et la
   recherche dans le JORF ; à la racine reste une ligne : une session qui
   touche au scénario 1 commence par `docs/veille_droit.md`.
4. La liste « ne se lisent jamais en entier » devient la règle du hook de
   l'étape 2, en une phrase. Ce qui ne sert plus qu'aux clones d'avant le
   26 septembre peut passer à `docs/archives/conventions.md`, avec l'histoire
   des autres règles, si le propriétaire le veut.
5. `python scripts/conservation.py --depuis HEAD` reste muet ; puis
   `python scripts/verifier_prose.py --corriger`.

*Les pièges.* `CLAUDE.md` est un document d'état : ses chiffres sont ancrés,
et ceux des nouveaux `CLAUDE.md` le seront. Un changement de `CLAUDE.md` ne
vaut, pour une session, qu'à son prochain démarrage. Ce qu'on retire de la
racine est le règlement du propriétaire : le lui montrer avant de pousser.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.
