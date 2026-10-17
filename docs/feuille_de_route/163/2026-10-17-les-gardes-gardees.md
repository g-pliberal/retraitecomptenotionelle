# Les gardes gardées

**Le 17 octobre 2026, la demande.** Le propriétaire : « fais l'étape 6 ».

**Ce que `pousser.sh` refuse.** Un commit à publier qui touche une garde du
dépôt — les workflows de GitHub (`.github/workflows/`), les hooks
(`.claude/hooks/`) et leurs réglages (`.claude/settings.json`, par lesquels
une session pourrait en couper un), `scripts/pousser.sh` et
`scripts/publier_fabrique.sh`, qui publie le verdict et ouvre la mise en
ligne — sans une ligne `Garde-modifiée: <raison>` dans son message, la raison
non vide. Le refus nomme le commit et les gardes qu'il touche, et dit comment
déclarer l'accord, une fois obtenu. Chez Anthropic, tout fichier de CI exige
une personne ; ici, sans pull request, le seul accord possible est celui que
le propriétaire donne dans la conversation, avant.

**Ce que ce n'est pas.** Un verrou : la session peut écrire la ligne seule,
comme `Sans-test:`. C'est un ralentisseur, qui l'arrête au moment d'envoyer,
et une trace : `git log --grep='^Garde-modifiée:'` liste chaque garde changée,
et pourquoi. Le message se lit dans une variable, par une expression de bash,
et non par un tube que `pipefail` ferait mentir.

**Vérifié.** `tests/test_pousser.py`, sur un atelier : pour chacune des cinq
gardes, l'envoi refusé, puis accepté une fois le commit déclaré ; les autres
cas de l'envoi restent verts. Ce commit-ci, qui touche `pousser.sh`, porte la
première déclaration : la demande du propriétaire.
