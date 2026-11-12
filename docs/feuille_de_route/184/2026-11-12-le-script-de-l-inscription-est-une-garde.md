# Le script qui publie l'inscription entre dans les gardes

**La demande, le 11 novembre 2026.** L'étape 4 a écrit
`scripts/publier_inscription.sh`, par lequel GitHub commite sur `main`, chaque
lundi, ce que l'inscription des rédactions écrit. Sa session a relevé qu'il
pousse sur `main` depuis GitHub, comme `publier_fabrique.sh`, sans être dans
la liste des gardes de `scripts/pousser.sh`, et n'y a pas touché : l'accord du
11 novembre ne portait que sur le workflow. La session d'orchestration a posé
la question au propriétaire : « Voulez-vous qu'il y entre ? Cela modifie
`scripts/pousser.sh`, qui est lui-même une garde. Je recommande oui. » Sa
réponse : « oui, ajoute le script aux gardes ».

**Ce qui est fait.** `pousser.sh` refuse désormais un commit qui touche
`scripts/publier_inscription.sh` sans ligne `Garde-modifiée: <raison>`. Le
test `test_une_garde_ne_change_qu_avec_sa_declaration`
(`tests/test_pousser.py`) a reçu ce cas, vu rouge avant la retouche.
`CLAUDE.md` et `docs/architecture.md` nomment le script dans la liste.

**Ce qui n'est pas fait.** La note de l'action 163 qui a créé les gardes, un
récit du 17 octobre 2026, garde sa liste d'alors.
