# Version du 11 novembre 2026 : les règles à portée de chemin

`CLAUDE.md` tient sous la limite que la documentation de Claude Code lui
vise, deux cents lignes : ce qui ne vaut que pour des fichiers épars le quitte
pour une règle de `.claude/rules/`, que son champ `paths` fait charger à la
lecture ou à l'écriture d'un fichier qui lui répond (§ 9.3). `prose.md` reçoit
les régimes de la prose, « Rien ne se perd » et les conflits du rebasage ;
`documentation.md`, ce qu'une étape écrit et où, le bloc « Reprise » et la
clôture d'une action ; `tests.md`, la mécanique de la suite et les deux gardes
du test d'abord. La relève de la session d'orchestration devient le skill
`orchestration`, et ce qui ne regarde qu'un poste, `docs/poste.md`, qu'une
puce de la racine déclenche. La racine passe de 265 lignes à 194, sans perdre
une règle : elle garde ce qu'une session doit savoir avant son premier geste,
ou avant un geste qui n'ouvre aucun fichier. `verifier_prose.consigne` compte
ces règles parmi les consignes, que la prose tient et que la conservation
suit ; `tests/test_consignes.py` tient la limite et la portée de chaque règle
(action 135, à la demande du propriétaire, qui a approuvé le classement).
