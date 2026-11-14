# L'envoi refusé quand deux sessions ont refait le paquet

**Le 14 novembre 2026, le défaut.** La file des trente corrections de
l'action 130 menait deux sessions de front. Chacune corrige une caisse et
refait le paquet, `moteur/donnees.json`, où les deux moteurs lisent leurs
règles. Quand la seconde envoyait, `scripts/pousser.sh` la rebasait sur
`main`, et, le conflit ne portant que sur un fichier fabriqué, gardait le
paquet de `main` — celui de l'autre session — et jetait le sien. `main`
recevait la correction sans le paquet qui la porte : le test de la correction,
qui joue les deux moteurs, y était rouge.

**Ce que cela a coûté.** Quatre commits de réparation ce jour-là, « le paquet
refait après le rebasage » : `bfaefef` (lignes 14 et 21 de la file), `469e070`
(ligne 22), `c449999` (ligne 15), `926b4c2` (ligne 17). Entre le rebasage et
la réparation, `main` est resté sans paquet à jour 2 minutes pour la ligne 15
(13 h 29 à 13 h 31 UTC) et 8 minutes pour la ligne 17 (14 h 28 à 14 h 36) ;
les deux autres ne se chronomètrent pas à l'historique. `.github/verdicts.tsv`
ne porte aucun rouge sur ces envois : GitHub refait le paquet avant de jouer
la suite, et le site n'a pas bougé. Le rouge était celui de la suite rapide,
pour toute session qui rattrapait `main` dans l'intervalle, et, sans la
réparation à la main, il aurait duré jusqu'au commit de GitHub, une course
entière.

**Les autres fichiers fabriqués** que `.gitattributes` marque `-merge`
reçoivent le même traitement : la version de `main`. Les quatre incidents
portent sur le paquet seul, le seul qu'un moteur lit pour calculer ; les
témoins, les pages toutes faites, le tableau de bord et l'inventaire restent
réglés seuls, comme l'action 148 l'a voulu.

**La réparation, décidée par le propriétaire dans la session.** `pousser.sh`
refuse, sans rien pousser, le conflit sur un fichier fabriqué que
`.gitattributes` marque `refaire=<son script>`, et le message donne le geste :
`git rebase origin/main` ; à chaque arrêt, `python
scripts/construire_donnees.py`, `git add -A`, `git rebase --continue` ; puis
les tests et `bash scripts/pousser.sh`. Trois fichiers portent la marque, ceux
que ce script écrit : `moteur/donnees.json`, `data/derive/equilibre.json`,
`data/derive/agregats.json`. Le test,
`test_une_correction_ne_part_jamais_avec_le_paquet_d_une_autre`
(`tests/test_pousser.py`), a été vu rouge : le script envoyait la correction
avec le paquet de l'autre.

**Les voies écartées.** Refaire le paquet dans `pousser.sh` : 2 min 33 mesurées
dans le conteneur, mémoire des calculs vide, quand le hook de fin de tour
coupe à 120 s. Refuser pour tout fichier fabriqué : les refus à répétition que
l'action 148 a ôtés. Laisser GitHub refaire et ne plus comparer avant :
le test de la correction lit lui-même le paquet. Fusionner les deux paquets
clé par clé : juste seulement quand les deux corrections sont indépendantes.

**Ce qui reste.** `CLAUDE.md`, « Git : tout va sur `main` », énumère ce que
`pousser.sh` refuse et dit qu'il « règle seul, au rebasage, ce que les scripts
écrivent » : la phrase attend son exception, que cette session, tenue à ses
fichiers, n'a pas écrite. Une autre cause laisse `main` sans fichier fabriqué
à jour, hors de cette étape : une session envoie une source sans refaire ce
que la suite rapide compare (l'inventaire, `docs/regimes.md`, une page toute
faite), ce que la règle lui permet ; la note du 14 novembre sur le report de
la Cipav, à l'action 130, en porte deux cas.
