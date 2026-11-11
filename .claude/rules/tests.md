---
paths:
  - "tests/**"
---

# Règle de la suite : comment elle se lance, ce qui tient le test d'abord

Claude Code charge cette règle à la première lecture ou écriture d'un fichier
de `tests/`, en plus de `CLAUDE.md`, qui dit le test d'abord et quels tests
lancer.

- **La suite** se répartit sur les cœurs, et un fichier visé aussi quand il
  est lourd (`POIDS_REPARTI`, dans `pytest_parallele.py`) ; un cas précis ou
  un fichier léger reste en série, `PYTEST_SANS_XDIST=1` force la série.
  `tests/conftest.py` range chaque fichier dans son niveau : un fichier lent
  qui naît s'y range. Les tests du site tiennent en trois fichiers,
  `test_web.py`, `test_web_saisie.py` et `test_web_revues.py`, qui se
  partagent `tests/outils_web.py` ; ce qu'un écran en montre se vérifie dans
  un vrai navigateur, par `test_ecrans.py`.
- **Deux gardes tiennent le test d'abord** : le hook `.claude/hooks/tdd.py`
  refuse une fois par commit la première retouche du code quand pytest n'a vu
  échouer aucun test en train de s'écrire (refaite telle quelle, elle passe) ;
  `pousser.sh` refuse d'envoyer un commit qui change le code sans toucher aux
  tests, sauf s'il le déclare par une ligne `Sans-test: <raison>` de son
  message — un remaniement, un commentaire.
