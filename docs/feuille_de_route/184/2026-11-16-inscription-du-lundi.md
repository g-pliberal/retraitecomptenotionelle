# L'inscription du lundi 16 novembre, et son heure de départ

**Ce qui a tourné.** La tâche planifiée `index-dila.yml`, prévue à 4 h UTC,
est partie à 12 h 19 UTC (run 43865448833), en succès ; le lundi 9 novembre,
elle était partie à 12 h 22. Elle a commité sur `main` (`6771d65`) 68
rédactions nouvelles et 4 textes : l'arrêté du 1er octobre 2007 (45),
le décret n° 71-542 (9), l'arrêté du 13 avril 2011 (8), le décret n° 74-436
(6), sur l'index LEGI mis à jour jusqu'à l'incrément du 16 novembre à
10 h 49. Puis elle a lancé `tests.yml` sur ce commit (run 43865765637).

**L'heure.** GitHub ne garantit pas l'heure d'une tâche planifiée, et retarde
d'abord celles qui tombent à heure pile, où les dépôts se pressent. Le cron
passe de `0 4 * * 1` à `17 4 * * 1`, et le test du workflow
(`test_dila_kali.py`) le dit. Accord du propriétaire, le 16 novembre 2026 :
« Oui », à la proposition de décaler le cron sur `17 4 * * 1`.
