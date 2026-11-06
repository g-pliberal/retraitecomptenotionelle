# J5-ter : la suite rouge de main, l'âge conjoncturel de 2024 de la fiche 15 attendu à 62,951 pour 62,9515

**La demande.** Vague 11, tâche J5-ter, le 6 novembre 2026 : la suite complète de GitHub
et sa garde des présomptions sont rouges sur `main` (course 42158939001, sources
40d3fbc) par un seul test, de la file J : `test_l_age_conjoncturel_de_la_fiche_15_est_50_plus_les_parts_de_non_retraites_du_graphique_3`
(`tests/test_drees_panorama_solde.py`, écrit par J5, commit cef7bfa, repris par J5-bis,
commit 9967c49) : `assert 62.9515 == 62.951 ± 5.0e-04`. Réparer cela, et rien d'autre.
L'exigence du propriétaire (3 novembre) : aucune erreur ; un document source à la clé ;
jamais la mémoire ; de quoi justifier par écrit tout le système.

**Ce qui a échoué, et pourquoi.** Deux causes, dont la première est la vraie.

1. *La valeur attendue était fausse.* La somme exacte est 62,9515 (calcul plus bas) ; J5
   l'avait tronquée à 62,951 dans le docstring, dans l'assertion
   (`approx(62.951, abs=0.0005)`) et dans sa note
   (`2026-11-06-etape-7-solde-du-suivi.md`, section de la fiche 15 : « 2024, 62,951 pour
   62,95 ; 2004, 60,584 ; 2014, 61,357 »). La relecture R-J5 l'avait écrit juste
   (`2026-11-06-relecture-r-j5.md`, section 6 : « 2024 : 62,9515 »). La tolérance de
   0,0005 autour de 62,951 va donc jusqu'à 62,9515 pile : la valeur vraie est *sur* la
   borne.
2. *Sur la borne, le dernier bit de la somme flottante décide, et il dépend de la version
   de Python.* Depuis Python 3.12, `sum()` additionne les flottants en compensant les
   erreurs d'arrondi ; `sum()` de 3.11 ne le fait pas. Les mêmes 21 termes
   `1 - part / 100` donnent, relevé aux deux versions : `50 + sum(...)` = 62,951499999999996
   sous Python 3.13 (écart à 62,951 : 0,000499999999995 ≤ 0,0005, vert) et
   62,9515 sous Python 3.11 (écart : 0,00050000000000239 > 0,0005, rouge). GitHub lance la
   suite sous 3.11 (`.github/workflows/tests.yml`, ligne 61), les postes et les
   conteneurs sous 3.13.

   *Une correction au diagnostic de l'orchestration* : elle écrivait que 3.11 rend
   62,95150000000002, au-dessus de la borne. Relevé ici : 3.11 rend 62,9515 exactement
   (et 3.13 62,951499999999996, au-dessous). Le mécanisme est le même (la somme flottante
   qui dépend de la version, sur une borne), le sens des chiffres est l'inverse ; ce
   n'est pas un défaut de `fsum` ou de `sum`, c'est une valeur attendue fausse posée
   pile à la limite de sa tolérance.

**Les sources, ouvertes pour cette tâche.** `python scripts/fetch/source_locale.py
--recuperer` : l'archive des 36 classeurs du panorama de la DREES
(`drees_panorama_retraites_2026_classeurs.zip`, SHA-256
`ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`, que `sha256sum` a
retrouvée), classeur `fiche_15.xlsx`, feuilles « F15_Graphique 1 » (lignes 5 à 7, C à W,
2004 à 2024 : femmes, hommes, ensemble), « F15_Graphique 3 » (ensemble, lignes 5 à 25,
de 50 à 70 ans) et « F15_Graphique 3 compl » (femmes, lignes 7 à 27 ; hommes, 32 à 52 ;
ensemble, 57 à 77), lues par `scripts/fetch/lecture_xlsx.py` cellule par cellule, et non
par le témoin ; sommes refaites en `Fraction`, donc sans flottant. Le script
(`ecarts_exacts.py`, dans le scratchpad de la session) n'est pas versé au dépôt : le
test, qui lit le témoin, et le calcul ci-dessous suffisent à le refaire.

**Le calcul posé à la main.** L'âge conjoncturel est 50 + Σ de 50 à 70 ans de
(1 − part ÷ 100), soit 50 + 21 − (Σ des parts) ÷ 100 = 71 − S ÷ 10 000, où S est la somme
des 21 parts en centièmes de point (chaque cellule du classeur est à deux décimales ; le
script l'a contrôlé, sinon il s'arrêtait).

- *2024, ensemble* (feuille « F15_Graphique 3 », colonne W, lignes 5 à 25) : 0,88 ;
  0,95 ; 1,06 ; 1,17 ; 1,24 ; 1,28 ; 1,61 ; 2,10 ; 3,04 ; 4,06 ; 8,84 ; 19,45 ; 48,12 ;
  70,71 ; 78,94 ; 84,79 ; 86,69 ; 94,30 ; 97,05 ; 99,50 ; 99,07. Somme, posée en
  cumulant : 0,88 ; 1,83 ; 2,89 ; 4,06 ; 5,30 ; 6,58 ; 8,19 ; 10,29 ; 13,33 ; 17,39 ;
  26,23 ; 45,68 ; 93,80 ; 164,51 ; 243,45 ; 328,24 ; 414,93 ; 509,23 ; 606,28 ; 705,78 ;
  **804,85 %** (S = 80 485). Âge : 71 − 8,0485 = **62,9515**. Publié (« F15_Graphique 1 »,
  W7) : 62,95. Écart 0,0015.
- *2004, ensemble* (colonne C) : S = 104 155 (1 041,55 %) ; 71 − 10,4155 = **60,5845**
  (J5 : « 60,584 ») ; publié 60,58.
- *2014, ensemble* (colonne M) : S = 96 431 (964,31 %) ; 71 − 9,6431 = **61,3569**
  (J5 : « 61,357 ») ; publié 61,36.
- *Les 63 valeurs* (21 années × femmes, hommes, ensemble) : le plus éloigné du publié est
  à 49 ÷ 10 000 = **0,0049 an** (hommes, 2011 : 71 − S ÷ 10 000 = 60,4651 pour 60,47 ;
  puis ensemble 2019, 62,2252 pour 62,23, 0,0048 ; hommes 2020, 62,0753 pour 62,08, 0,0047).
  Aucun écart n'atteint 0,005 : la borne `abs=0.00501` de la boucle est à 0,00011 de
  marge, que les 1e-14 du flottant ne touchent pas, sous aucune version ; `ecart_max ==
  approx(0.0049, abs=0.0001)` tient de même (la valeur exacte est 0,0049).
- *2023, deuxième test du fichier* (`test_le_bloc_ensemble_du_complement…`) : 71 − S ÷
  10 000 = 62,7333 avec le bloc « Ensemble » du complément (S = 82 667), 62,7541 avec le
  graphique 3 (S = 82 459) ; publié 62,75. Ses valeurs, 62,733 à 0,0005 près et 62,754 dans
  son docstring, sont des arrondis justes à trois décimales, à 0,0003 de la valeur exacte :
  elles ne touchent pas la borne et restent telles.

**Ce qui change.** Dans `tests/test_drees_panorama_solde.py`, ce test seul : le docstring
dit les valeurs exactes (62,9515 ; 60,5845 ; 61,3569 ; le plus éloigné, hommes 2011,
60,4651 pour 60,47 ; la coquille « 50 + 20,951 » devient « 50 + 12,9515 »,
puisque 62,9515 − 50 = 12,9515) ; l'assertion de 2024 compte en centièmes entiers
(`sum(centiemes) == 80485`, et `71 - sum(centiemes) / 10000 == approx(62.9515, abs=1e-9)`),
après avoir contrôlé que chaque part est à deux décimales. Une somme d'entiers ne dépend
d'aucune version ; la division finale est une opération IEEE, la même partout. Le test
fait toujours ce qu'il faisait (retrouver l'âge de 2024 aux parts de la source), à sa
valeur exacte. Ni donnée, ni fiche, ni prose, ni témoin ne bougent.

**Vérifié.** Le test d'abord : l'ancien test, sous Python 3.11 (environnement jetable,
`uv venv --python /usr/bin/python3.11`, `pip install -e '.[dev]'`), échoue sur `assert 62.9515 ==
62.951 ± 5.0e-04`, comme sur GitHub ; sous 3.13, vert, par la borne. Le test corrigé,
sous 3.11 et sous 3.13 : vert. Contrôle par mutation : l'attendu remis à 62,951 (tolérance
1e-9), le test échoue sous 3.13 (« 62.951499999999996 == 62.951 ± 1.0e-09 ») ; rétabli.
Les fichiers de tests de la file J (`grep -l -i drees tests/test_*.py`, 36 fichiers), en
entier, tous niveaux : sous 3.11, 1 989 passent, 2 sautent, 1 échoue ; sous 3.13, les
mêmes. Le rouge est `test_les_temoins_du_portage_sont_a_jour` (`pages.json` périmé, que
GitHub refait par `regenerer.py`), le même aux deux versions ; les deux sauts sont ceux de
TRAJECTOIRE et d'Ines, qui ne se rejouent que sur demande (R installé). Aucune autre
comparaison de la file J n'échoue sous 3.11 : aucune n'est posée pile sur sa borne,
rien d'autre n'est donc corrigé. `python -m pytest -m rapide` sous 3.13 : 4 516 passent,
11 échouent, tous dans `tests/test_pages_en_dossier.py` (les pages toutes faites, que
GitHub refait) ; avec `PRESOMPTIONS_DECALEES=1`, les mêmes 11 et 4 311 passent. Le
fichier du test, sous 3.11 avec `PRESOMPTIONS_DECALEES=1` : 35 sur 35.

**Ce que la source ne tranche pas.** Rien de nouveau : les 63 valeurs de 2004 à 2024 sont
retrouvées au demi-centième près, ce que la DREES arrondit ; la source ne dit pas par
quelle règle d'arrondi (au plus proche, vers le bas) elle a publié, et aucun des 63 écarts
n'est à 0,005 pile, ce qui laisse la règle indifférente ici.

**Candidat, non fait (une garde, au propriétaire).** Les postes (Python 3.13) et GitHub
(3.11) ne lancent pas les tests sous la même version ; une valeur à la borne d'une
tolérance en a fait la preuve. Lancer la suite de GitHub sous deux versions (3.11 et 3.13)
la ferait voir plus tôt : c'est une retouche de `.github/workflows/tests.yml`, une garde, et
cette tâche n'y touche pas.
