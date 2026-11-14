# Version du 14 novembre 2026 : la course de GitHub en travaux parallèles, son verdict toujours publié

La course de `tests.yml` tenait sur une seule machine : la fabrique, la suite
complète, la garde des présomptions, puis le verdict, que le script ne
poussait pas si `main` avait bougé entre-temps. Elle se partage désormais
(§ 10). La fabrique part du dernier `main` et passe aux travaux suivants son
commit, ce qu'elle a refait — en un correctif — et la mémoire de ses calculs.
La suite se joue en tranches de fichiers entiers (`--tranche`, dans
`pytest_parallele.py`), une par machine, et la garde sur une autre ; chacune
reprend le commit de la fabrique, non la tête du moment. Un dernier travail
rassemble les issues, les sorties et les durées
(`scripts/rassembler_course.py`), réunit les calculs de toutes les machines
pour la mémoire de la course suivante, publie et met le site en ligne.

Le verdict tient à ses sources : `scripts/publier_fabrique.sh` le publie
aussi quand une session a envoyé pendant la course, seul, sur la nouvelle
tête, les fichiers refaits attendant la course suivante ; le verdict d'une
autre course, publié de même, ne compte pas pour un envoi. Le hook
d'ouverture compte les envois venus depuis les sources du verdict. Celui-ci
porte ce que chaque travail a duré. Partie sans mémoire des calculs, la
course écrit ce que chaque fichier de tests a duré
(`.github/durees_suite.tsv`, `scripts/durees_suite.py`) : les tranches de la
course suivante s'y pèsent, le fichier le plus long d'abord, chacun dans la
tranche la moins chargée. `tests/test_outillage.py` et
`tests/test_parallele.py` tiennent le partage, la reprise du commit de la
fabrique, le passage de main entre les travaux et la publication (action 135,
à la décision du propriétaire).
