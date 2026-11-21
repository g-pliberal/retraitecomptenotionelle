# Action 194 : la décote du régime général, quatre parties prouvées

Le 21 novembre 2026. Session sur Opus 5.5, comme Gilles l'a choisi pour ces
briefs (le dépôt veut Fable 5.2 pour une règle du scénario 1 : aucune règle
n'a changé ici, aucun point n'a demandé Fable). Posée sur `main` 50929356.

## Ce qui est fait

**Le découpage** (rangement, paquet identique au bit près). La fiche
`decote_regime_general` a cinq versions à la date d'effet :
`avant_l_ordonnance_de_1982` (supposée, renvoie à `decote_avant_1983`),
`ordonnance_de_1982` [1983-04-01, 2004) : 2,5 % ; `loi_de_2003` [2004, 2026) :
le II de R. 351-27 par génération ; `decret_de_2025` [janvier, août 2026) ;
`decret_de_2026` depuis le 1er août 2026 : 1,25 %. Le moteur lit toujours
`coefficient_minoration.csv` à la génération ; `tests/test_decote_versions.py`
confronte la table à chaque version. Le cliquet des rédactions citées sans
réponse descend de 431 à 430 (R. 351-27 du 1er août 2026 a sa version).

**Une lecture corrigée dans la fiche, sans effet.** Elle disait que le décret
n° 2025-1409 donnait 1,25 % à tous dès 2026. Il abroge le II (son article 2,
I, 29°, e) et laisse au texte le seul « 2,5 % pour les pensions ayant pris
effet avant le 1er janvier 2004 » : de janvier à juillet 2026, R. 351-27 ne
fixe aucun coefficient aux pensions d'après 2003. La caisse applique 1,25 %
(circulaire 2026-07, point 4.1.1) ; le décret n° 2026-699 l'écrit dès le 1er
août. Aucun résultat n'en dépend : toute génération qu'une décote atteint
encore en 2026, née après 1952, avait 1,25 % sous le II abrogé.

**Quatre grilles indépendantes**, 93 cas,
`data/reference/preuves/grille_decote_<version>.yaml` : 24, 48, 7, 14 cas ;
grandeur `taux_liquidation`, sur une carrière d'un seul régime aux trimestres
donnés. Les quatre parties sont au cliquet ; la carte passe de 15 à 19.

## Comment la grille s'est faite

Un agent sans le contexte de la session (Opus 5.5), dans
`/home/user/aveugle-decote`, a reçu la consigne, 59 cas (naissance, date
d'effet, trimestres) et les index LEGI et JORF du 16 novembre 2026. Il a
trouvé seul R. 351-27 et ses neuf rédactions, l'article 70 du décret n° 45-179
de 1982, l'ordonnance n° 82-270, R. 351-45, L. 351-8, la loi de 2003, le
décret n° 2004-144, L. 161-17-3 et les décrets de 2025 et 2026 ; il a proposé
34 cas. Pendant ce temps, la session travaillait dans une autre copie du
dépôt ; le guetteur de celle de `/home/user` n'a noté aucune ouverture.
**Accord sur les 93 cas du premier coup**, durées requises, âges
d'annulation, trimestres et coefficients compris.

Ce qu'il dit que le texte ne tranche pas, et la grille : le coefficient de
janvier à juillet 2026 (retenu 1,25 %, avec la caisse) ; le jour où l'âge
d'annulation est atteint (le jour anniversaire, non la veille : né le 2
janvier 1956, pension du 1er octobre 2022, deux trimestres et 48,75 %, un si
l'on comptait la veille) ; la dérogation de R. 351-45, III au né en décembre
1942 parti le 1er janvier 2003 (159 trimestres, 45 %).

## Ce que la grille ne prouve pas

La durée « tous régimes » : les cas n'ont qu'un régime. Les exceptions au
taux plein (inaptitude, handicap, carrière longue…), que chaque cas déclare
absentes. Le plafond de vingt trimestres, que le texte n'écrit pas et qui ne
mord sur aucun cas (fiche `plafond_des_trimestres_de_decote`).

## Coût

Trois commits, 14 fichiers ; une session aveugle de dix minutes ; environ
une heure et demie en tout.
