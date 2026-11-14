# La course de GitHub en travaux parallèles, son verdict toujours publié

**Le 14 novembre 2026, la demande.** Le propriétaire : « Qu'est-ce qui peut
encore être amélioré sur la vitesse de construction et sur l'économie de
tokens ? », puis, le relevé lu : « Appliquons toutes tes recommandations ».
`tests.yml`, `publier_fabrique.sh` et le hook `etat-suite.sh` sont des
gardes : c'est l'accord que leur retouche demande.

**Ce que le relevé a trouvé.** Lu sur les courses du jour, par l'outil
`actions_list` de GitHub.

- *La course s'était allongée.* Sans mémoire des calculs, 47 min 04 (la
  course 1795 : la fabrique 7 min 50, la suite 36 min 02, la garde 2 min 55),
  contre 29 min 58 le 12 novembre ; avec mémoire, 19 min 46, contre 17 min 37.
  Chaque correction de l'action 130 change le modèle, et part donc sans
  mémoire.
- *Le verdict ne sortait plus.* `publier_fabrique.sh` ne poussait rien quand
  `main` avait bougé pendant la course, et deux files de corrections
  envoyaient tous les quarts d'heure. De 12 h 12 à 16 h 40 UTC : 47 commits,
  trois courses finies — une verte à 14 h 52, deux rouges à 15 h 25 et
  16 h 12 —, aucune publiée. Le hook d'ouverture disait toujours « verte ».
- *Les fichiers fabriqués recommités.* Sur ces 47 commits, 10 ne font que
  refaire des fichiers fabriqués après un rebasage, et 18 touchent
  `moteur/donnees.json`. C'est la consigne des deux files (la note
  `2026-11-14-correction-sans-attendre-le-verdict.md`) ; le remède est une
  course plus courte, qui publie ces fichiers avant l'envoi suivant.
- *Rien ne disait où passait le temps de la suite.* Mesurée dans le conteneur
  de la session, à quatre cœurs, mémoire vide, par `--junitxml` : la fabrique
  439 s, la suite 25 min 32, soit 5 746 secondes de processus sur 251
  fichiers, dont 55 % dans cinq d'entre eux
  (`test_indexation_scenario_6.py`, `test_facade_jumeau.py`,
  `test_grille_large.py`, `test_cout.py`, `test_facteurs_depense.py`). Deux
  tests durent 538 s et 476 s à eux seuls ; 22 passent la minute.

**Ce qui est fait.**

- *Le verdict se publie toujours.* Dépassée par un envoi, la course publie
  son verdict seul, sur la nouvelle tête, sans les fichiers refaits ; le
  verdict d'une autre course ne compte pas pour un envoi, sans quoi chaque
  verdict aurait retenu les fichiers de la course suivante. Le hook
  d'ouverture compte les envois venus depuis les sources du verdict, les
  commits du robot à part, et un rouge le dit aussi.
- *Le verdict porte les durées* de la fabrique, de la suite, de chaque
  tranche et de la garde, en secondes (`durees:` dans
  `.github/etat_suite.yaml`).
- *La course en cinq travaux* : la fabrique ; la suite en quatre tranches et
  la garde, chacune sur sa machine, sur le commit, les fichiers et les
  calculs de la fabrique ; le travail qui publie. `--tranche 2/4`
  (`pytest_parallele.py`) garde les fichiers entiers, dont les tests
  partagent des calculs lourds.
- *Les durées par fichier de tests*, `.github/durees_suite.tsv`, que la
  course écrit quand elle part sans mémoire (`scripts/durees_suite.py`) : les
  tranches de la suivante s'y pèsent, et une session y lit où passe le temps
  sans appeler GitHub. Le tableau envoyé avec cette étape est celui de la
  seconde course d'essai.

**Les deux essais**, lancés à la main sur la branche de la session, donc
sans mémoire, avant tout envoi sur `main`.

| | en tout | la fabrique | les tranches | la garde |
|---|---|---|---|---|
| une seule machine (course 1795) | 47 min 04 | 470 s | 2 162 s | 175 s |
| premier essai, tranches non pesées | 28 min 06 | 450 s | 462, 227, 525 et 1 170 s | 199 s |
| second essai, tranches pesées | 18 min 56 | 350 s | 732, 420, 550 et 531 s | 134 s |

Le premier a publié le verdict, quatre fichiers refaits et le tableau des
durées. Pendant le second, la session a poussé un commit : la course a
publié son verdict seul, sur ce commit. La fabrique a duré deux minutes de
moins au second essai, sur le même modèle : les machines de GitHub ne se
valent pas, et l'écart entre 47 et 19 minutes ne tient pas qu'au partage.

**Ce qui n'est pas fait, et pourquoi.**

- *Refuser neuf outils du serveur de sessions*, que le relevé proposait : le
  propriétaire les a gardés exprès le 11 novembre (la note
  `2026-11-11-contexte-de-depart.md`, et `APPELES` dans
  `tests/test_reglages_claude.py`). Proposition retirée.
- *La mémoire des calculs indexée plus finement que le modèle* : à rouvrir
  sur le tableau des durées, quand quelques courses de `main` l'auront écrit.

**Ce qui reste.**

- Relever, sur les premières courses de `main`, la durée de la course avec
  et sans mémoire, et si la mémoire réunie des cinq machines se reprend bien.
- La tranche la plus longue tient à son test le plus long, non au nombre de
  machines : raccourcir les deux tests de huit et neuf minutes, ou les
  découper, avant d'ajouter des tranches.
- Le tableau des durées change à chaque course sans mémoire, ligne par
  ligne : s'il gêne dans l'historique, l'arrondir davantage.
