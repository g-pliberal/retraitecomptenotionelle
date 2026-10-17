# Les rouges classés

**Le 17 octobre 2026, la demande.** Le propriétaire, l'étape 1 vérifiée sur
GitHub : « Fait la prochaine étape ».

**Le relevé.** Du 6 au 17 octobre 2026, 170 courses de `tests.yml` ont publié
leur verdict sur `main` : 26 rouges (15 %), en 20 périodes où `main` est
restée rouge, 41,9 h en tout, 8,5 h au plus ; la garde des présomptions a été
rouge deux fois, chaque fois avec la suite. Trois verdicts ne faisaient que
prolonger le précédent : restent 23 causes. Les verdicts sont ceux de
`.github/etat_suite.yaml` à chaque commit du robot (l'historique remonté par
`git fetch --shallow-since=2026-10-05`) ; un échec est nouveau s'il manque au
verdict d'avant ; son niveau, celui que `tests/conftest.py` lui donne ; les
commits d'une course, ceux d'entre les sources du verdict d'avant et les
siennes.

**Ce que la suite rapide, ou un rebasage, auraient vu : rien.** Aucun test
tombé n'est du niveau rapide : tous sont `controle` ou `complet`, et un rouge
de la suite rapide ne part pas, chaque session la jouant. Aucun rouge n'est
établi comme né de deux sessions rebasées l'une sur l'autre : quand une course
en portait plusieurs, chaque cas remonté tient au changement d'une seule
(l'oracle de l'Ircantec, à la limite d'âge de l'étape 151.4 ; un module non
préchargé, au nouveau `droit/categories.js`). Relancer la suite rapide après le
rebasage, la file de fusion de l'article, n'en aurait arrêté aucun.

**Les causes, par famille.** Un verdict en mêle parfois plusieurs : 33 causes
de famille sur 23 verdicts.

| Famille | Causes | Tests tombés | Ce qui l'aurait vu avant l'envoi |
|---|---|---|---|
| Un chiffre que le parcours, l'accueil ou le README écrivent à la main, et que le changement déplace | 13 | `test_parcours` (chiffres et comptes du parcours sur leur page, ses carrières rejouées : « le parcours annonce 1 028 €, la page affiche 1027.00 € »), `test_solde_fusion` et `test_proposition_prospective` (le solde que l'accueil cite), `test_web` (« README.md annonce 74 régimes, le dépôt en compte 76 »), `test_age_conjoncturel`, `test_grille_large` | en partie ces tests, huit secondes à eux tous ; mais quand la valeur attendue vient d'un fichier que GitHub refait (le solde, sous `data/derive/`), une session qui ne régénère pas ne la voit pas bouger |
| Le bloc « Reprise » de la feuille de route | 6 | `test_prose` (chaque action en cours s'ouvre sur son bloc) | ce test, en moins d'une seconde ; mais la feuille de route s'écrit au dernier commit, après les tests |
| Un changement du modèle qui déplace une confrontation | 7 | `test_oracle` (l'Ircantec), `test_destinie`, `test_estimation_officielle`, `test_facteurs_depense`, `test_cout`, `test_verification`, `test_affirmations` | les tests de la zone du modèle, si elle les comptait |
| Le site : un module non préchargé, le menu des statuts | 3 | `test_web`, `test_web_revues` | `pytest -m site`, que la consigne demande après une retouche du site |
| Le portage JavaScript | 1 | `test_web` (le portage retrouve les chiffres du modèle) | les tests du site |
| La comptabilité des tests | 1 | `test_niveaux` (une exception qui ne vise plus aucun test) | ce test, en moins d'une seconde |
| La fabrique | 1 | `scripts/regenerer.py` a échoué | la fabrique seule |
| L'environnement | 1 | `test_hook_tdd` : la copie du dépôt modèle a buté sur le verrou de la maintenance que git détache | rien ; réparé le jour même (`78ea884`) : les dépôts d'essai de `test_hook_tdd.py` et de `test_pousser.py` coupent la maintenance automatique |

La zone : la première famille, la quatrième et la cinquième tombent dans les
tests du site quand le changement venait du modèle ou des données ; c'est
pourquoi les tests de sa zone ne les voyaient pas. Les rouges les plus longs
sont de nuit (8,5 h, 6,6 h, 5,5 h, 3,7 h) : personne ne les répare, et depuis
l'étape 1 ils n'atteignent plus le site.

**Ce que le classement justifie**, au propriétaire de trancher :

1. **Produire les chiffres cités, plutôt que les garder** (13 causes) : ancrer
   ceux du parcours et du README (`<!--chiffre:…-->`), faire lire à l'accueil
   ceux du paquet ; GitHub les refait alors au lieu de rougir. Une étape du site
   et de la prose, la plus rentable.
2. **Le bloc « Reprise » à l'envoi** (6) : `pousser.sh` joue les deux tests de
   la feuille de route, en moins d'une seconde, quand un commit la touche.
3. **Les tests d'une seconde au niveau rapide** (4) : les modules préchargés, le
   nombre de régimes du README, les exceptions des niveaux.
4. **Les confrontations du modèle** (7) : elles ont fait leur travail, sur
   GitHub ; les nommer parmi les tests de la zone du modèle (`src/CLAUDE.md`) si
   leur durée le permet, à mesurer d'abord.
5. **Pas de file de fusion** : rien ne la justifie.

**Ce qui est fait.** Le journal des verdicts, `.github/verdicts.tsv` :
`publier_fabrique.sh` y inscrit chaque course publiée — date, sources, état de
la suite, de la garde —, rempli depuis l'historique pour les 170 courses du
6 au 17 octobre. `python scripts/tableau_de_bord.py --cout` en relève les
rouges, les incidents et le temps passé au rouge, en tout et sur les sept
jours qui finissent au dernier verdict, à côté du coût du travail : comme lui,
ils changent à chaque course, et n'entrent pas dans `docs/etat.md`. Les tests,
dans `tests/test_outillage.py`, sur un journal compté à la main.
