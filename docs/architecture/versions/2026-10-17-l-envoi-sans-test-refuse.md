# Version du 17 octobre 2026 : l'envoi sans test refusé

Le test d'abord a une seconde garde, que le propriétaire a demandée le jour
même de la première (« durcis le hook : refuser l'envoi sans test dans
pousser.sh ») : `scripts/pousser.sh` refuse, sans rien pousser, un commit qui
change le code — `src/`, `moteur/`, `scripts/`, `.claude/hooks/` — sans
toucher aux tests, hors des témoins fabriqués, sauf s'il le déclare par une
ligne `Sans-test: <raison>` de son message, un remaniement ou un commentaire
(§ 10). Ce qui est du code et ce qui est un test, un seul fichier le dit aux
deux gardes : `.claude/hooks/tdd.py` (action 162).
