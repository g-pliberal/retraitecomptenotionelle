# La mémoire des calculs sur GitHub, d'une course à l'autre

**Le 12 novembre 2026.** La course de GitHub (`tests.yml`) partait sans
mémoire : 25 min 21 le 11 novembre, dont 5 min 31 de fabrique et 18 min 07 de
suite. Le propriétaire a décidé de la raccourcir (« On raccourci la course »),
ce qui vaut accord pour retoucher le workflow, qui est une garde.

**Mesuré d'abord**, dans un conteneur de session, quatre cœurs comme le
coureur de GitHub, dans l'ordre de la course : `regenerer.py`, la suite
complète, la garde des présomptions.

| | mémoire vide | mémoire des calculs pleine |
|---|---|---|
| la fabrique | 332 s | 89 s |
| la suite complète | 754 s | 410 s |
| la garde des présomptions | 55 s | 58 s |
| en tout | 19 min 01 | 9 min 17 |

La fabrique vide prend ici ce qu'elle prend sur GitHub, à la seconde près ; la
suite y est plus lente, 18 minutes. Dans la fabrique, le paquet passe de 161 s
à 25 s, l'accueil de 63 s à 4 s, la prose de 68 s à 22 s ; les témoins, 30 s,
ne gagnent rien. La mémoire pèse 88 Mo, 144 calculs sous une seule empreinte :
la fabrique ne change pas l'empreinte du modèle. Les deux suites jouent les
mêmes tests, 8098 passés et 76 sautés.

**Ce qui se reprend, et ce qui ne se reprend pas.**

- *La mémoire des calculs seule* (`.cache/calculs`). Le dossier `.cache/`
  porte deux autres mémoires, qui ne rendent pas un calcul mais en dispensent :
  celle de la fabrique (`.cache/fabrique.json`), qui fait sauter les étapes
  dont rien n'a bougé, et les réussites des tests qui ne lisent rien du modèle
  (`.cache/tests`), qui les fait sauter : 34 tests et 22 s de plus à la
  mesure. Elles restent hors de la course, qui refait toute la fabrique et
  joue tous les tests.
- *La clé* est l'empreinte sous laquelle `memoire.py` garde lui-même chaque
  calcul — tout ce que git voit du modèle, de ses données et du portage, octet
  par octet, Python et node —, suivie de la version de PyYAML, seule
  dépendance des calculs, puis du numéro de la course. Une étape la calcule,
  le paquet installé. La course reprend la mémoire la plus récente gardée sous
  la même empreinte et la même version, et aucune autre : une source du modèle
  retouchée, elle part sans mémoire. Un calcul écrit dans un script ou un test
  porte déjà son code dans sa clé, à l'intérieur de la mémoire.
- *Qui écrit la mémoire.* `actions/cache` ne garde qu'au bout d'un job réussi :
  fabrique, suite et garde vertes. L'étape ne joue que sur un envoi (`push`),
  que le workflow n'écoute que sur `main`.
- *Le passage sans mémoire reste.* Une course lancée à la main, ou par l'index
  de la DILA quand il inscrit des textes, le lundi, ne reprend ni ne garde
  rien. Une course verte avec mémoire et rouge sans elle se verrait là.

**Les tests** (`tests/test_outillage.py`), vus rouges, le workflow sans
l'étape : `test_la_course_ne_reprend_que_la_memoire_de_son_modele` joue la
reprise de GitHub sur deux courses, puis une source ou PyYAML changés ;
`test_la_cle_de_la_memoire_de_la_course_est_l_empreinte_du_modele` joue
l'étape sous le shell de GitHub, et exige qu'elle échoue si le calcul échoue ;
`test_une_course_lancee_a_la_main_part_sans_memoire`. Essayés contre deux
défauts : une clé de reprise sans l'empreinte, et l'empreinte calculée dans
la ligne qui l'écrit, où un échec rendrait une clé vide ; chacun rougit son
test.

**Ce que la course y gagnera.** Rien quand le modèle bouge : 12 des 54
derniers commits de sessions sur `main` le touchent. Les 42 autres — la
documentation, les pages du site, les tests, les scripts — partiraient
mémoire pleine, pourvu que la course d'avant ait fini verte.

**Ce qui reste.** Relever sur GitHub la durée de la première course partie
mémoire pleine. Les témoins et le contrôle de la prose, qui ne tiennent pas
aux calculs gardés, sont ce qui reste de plus long dans la fabrique.
