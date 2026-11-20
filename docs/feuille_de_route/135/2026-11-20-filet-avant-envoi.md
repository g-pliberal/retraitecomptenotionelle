# Le filet des fichiers communs, joué juste avant l'envoi

**Le 20 novembre 2026, la demande.** `main` a été rouge deux fois la veille.
Il était proposé au propriétaire de vérifier avant de publier : une branche,
puis l'envoi une fois la suite complète verte. Lui : « J'ai quand-même des
petits doutes sur les suites. À l'époque, on avait fait ce choix parce qu'on
poussait énormément de choses en même temps. »

**Ce que le relevé a trouvé.**

- *Pourquoi la suite complète suit l'envoi.* L'action 148, le 6 octobre :
  l'heure que prenait un changement venait des boucles « conflit, rebasage,
  régénération, suite complète », reprises dès qu'une autre session avait
  poussé. La note `2026-11-14-correction-sans-attendre-le-verdict.md` :
  attendre le verdict prenait 34 minutes sur les 52 d'une correction.
- *Les rouges.* `.github/verdicts.tsv`, du 6 octobre au 20 novembre :
  92 verdicts rouges sur 518, en 57 épisodes, dont 42 rouges du 15 au
  17 novembre ; un épisode dure le plus souvent de 20 à 45 minutes. La course
  de GitHub en prend une vingtaine.
- *Le premier rouge du 19 novembre* est un croisement : trois envois en seize
  minutes, et un compteur à 1 445 valeurs de repli quand son cliquet en
  admettait 1 442 (`test_cliquets_du_droit_date.py`), avec
  `test_regle_de_chacun.py`. Une branche vérifiée seule ne l'aurait pas vu.
- *Le second* tient à un seul envoi : un cas témoin de plus décale
  l'échantillon de `test_liquidation.py` et de `test_droit.py`, deux tests du
  niveau complet, que la suite rapide ne joue pas.
- *Ces quatre fichiers se rejouent en moins d'une minute*, mesurés dans le
  conteneur de la session, à quatre cœurs : 13 s pour les cliquets et les
  deux tests des sorties figées, 36 s pour la règle de chacun.

**Les trois options soumises**, et leur prix : l'envoi direct avec un filet
d'une minute ; la suite complète avant l'envoi, un chantier à la fois, soit
vingt à trente minutes d'attente et trois envois par heure, quand le soir du
19 en a compté huit en 48 minutes ; le mélange, où seul le chantier des
fichiers communs attend. Le propriétaire, le même jour : « Je suis tes
recommandations », la première.

**Ce qui est fait.** `scripts/pousser.sh`, `main` rattrapé et juste avant
d'envoyer, joue les tests que nomme `tests/filet_avant_envoi.txt` : un lot
par ligne, les lots de front. Rouges, rien ne part, et le message nomme les
tests tombés. Un envoi qui ne touche que `docs/` ou des fichiers `.md` ne
les joue pas. Deux lots : les cliquets et les deux tests des sorties figées ;
la règle de chacun. Les deux tests, dans `tests/test_pousser.py` ; le
premier, `test_il_refuse_deux_chantiers_verts_seuls_et_rouges_reunis`, a été
vu rouge : le script envoyait.

**Ce que le filet ne fait pas.** Il n'a pas été essayé sur les envois du
19 novembre : qu'il les aurait arrêtés est une déduction, des tests tombés.
Il ne voit que les tests de sa liste ; les autres rouges se lisent au verdict
de GitHub, comme avant. Il lit le répertoire de travail, modifications non
commitées comprises. Le hook `Stop` laisse deux minutes au script : le filet
doit rester sous la minute, et un test lent n'y entre pas.

**À reprendre.** Relever sur une semaine les rouges de `main` et les tests
qui tombent, pour les ajouter à la liste ou conclure que le filet ne suffit
pas ; le mélange reste alors l'option suivante.
