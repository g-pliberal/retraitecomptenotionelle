# Version du 7 octobre 2026 : les consignes par dossier

`CLAUDE.md` se relit à chaque appel de chaque session : les règles d'une
seule zone le quittent pour le `CLAUDE.md` de son dossier, que Claude Code ne
charge qu'à la première lecture d'un de ses fichiers (§ 9.3). `src/` reçoit
le Python qui fait foi, les mémoires et la liste d'un changement du modèle ;
`moteur/`, le texte du site, l'outillage d'interface et les listes d'une
retouche de `pages.js` et d'un champ de saisie ; `data/`, les données et la
proposition. La procédure de veille, que `CLAUDE.md` résumait, et la
recherche dans le JORF sont dans `docs/veille_droit.md`, qu'une ligne de la
racine déclenche. La racine passe de 18 876 caractères à 12 672, et aucune
session n'en relit plus qu'avant, pas même celle qui charge les trois
consignes (action 135, étape 3 du contexte, à la demande du propriétaire).
`scripts/conservation.py` lit ces consignes, et retrouve une liste puce par
puce, puisque les règles se déplacent une à une.
