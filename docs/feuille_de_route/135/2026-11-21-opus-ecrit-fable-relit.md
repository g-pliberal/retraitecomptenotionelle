# Opus 5.5 écrit une règle du scénario 1, Fable 5.2 la relit

**Le 21 novembre 2026.** Le propriétaire a décidé : « On travaille sous
Opus 5.5 et on fait relire par Fable ». Le dépôt disait encore la règle du
9 novembre (note « Fable 5.2 pour une règle du scénario 1 ») : chaque session
lancée ce jour-là a relevé la contradiction et hésité.

- `CLAUDE.md`, « Le scénario 1 est le droit applicable » : l'étape se mène
  sur Opus 5.5 et se relit sur Fable 5.2 avant d'être publiée, l'un et
  l'autre à `high` ; la bascule se fait par `/model opus`, et l'agent qui
  écrit une telle règle reçoit `model: opus`.
- Le skill `claude-api`, qui recense les choix de modèle du dépôt, le dit.
- La note de décision 0009, gelée, reçoit un rectificatif daté ; le bloc
  « Reprise » de l'action 191 dit « sur Opus 5.5 et relue sur Fable 5.2 ».
- Rien ne change dans `.claude/settings.json` : Fable 5.2 et Opus 5.5 y
  sont déjà à `high`. Les notes datées d'avant restent telles quelles.

**Ouvert, au propriétaire.** La phrase ne dit pas comment se fait la
relecture (une session à part ou un agent `model: fable`), qui relit quand
l'étape est elle-même une relecture, ni ce qui vaut hors du scénario 1.
