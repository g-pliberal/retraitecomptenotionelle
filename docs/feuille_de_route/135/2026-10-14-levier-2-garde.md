# Le levier 2, étape 5 : la garde des présomptions sur GitHub

**Le 14 octobre 2026, la demande** (session de nuit, n° 18) : rejouer à
chaque envoi `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` dans
`.github/workflows/tests.yml`, après « La suite complète », et décider si son
verdict va dans `.github/etat_suite.yaml`, que le hook de démarrage affiche.

- *Dix tests nés depuis le 13 octobre.* Rejouée avant d'être câblée, la
  garde en a fait tomber dix, tous écrits la veille ou le jour même :
  huit de `test_coupures_au_mois.py` (avril 1983, le report et les enfants de
  la CAVEC, le RACL rejoignant l'Ircec) et deux de `test_cycle_de_vie.py`
  (l'impôt de l'année du départ). Né un 1er, l'assuré part le mois de son
  anniversaire, et non le suivant : chaque date d'effet recule d'un mois, et
  le salarié né en janvier 1980 part en janvier 2044, sans salaire l'année du
  départ. Le 15 se déclare dans l'outil qui construit la carrière, `_calculer`
  et `_comparaison`. Aucun montant ni aucune date attendus n'ont changé.
  C'est la preuve de la garde : sans elle, un lot par semaine.
- *L'étape.* « La garde des présomptions » suit « La suite complète », sous
  `shell: bash` (le tube dans `tee`, `pipefail`), et seulement si la
  fabrication a réussi. Une vingtaine de secondes ici, sur quatre cœurs.
- *Le verdict, à part.* La garde s'écrit dans `etat_suite.yaml` sous sa
  propre clé, `presomptions: vert | rouge | non_jouee`, et, rouge, ses échecs
  sous `presomptions_echecs`. Elle ne touche pas `etat` : une garde rouge ne
  dit rien de faux des fichiers fabriqués, qu'une suite verte a vérifiés, et
  les retenir figerait les chiffres de toutes les sessions pour un test mal
  daté. Mais elle rend la course rouge (« Le verdict »), le titre du commit
  du robot le dit (« garde des présomptions ROUGE »), et le hook de démarrage
  l'affiche, avec les tests à faire déclarer leur date.
- *Les tests* (`test_outillage.py`) : l'étape de la garde, comme celle de la
  suite, échoue sous le shell de GitHub quand pytest échoue ; elle suit la
  suite et passe son issue au script ; `publier_fabrique.sh`, joué dans un
  dépôt jetable qui pousse sur un dépôt nu, écrit une garde rouge à part
  d'une suite verte ; le hook sépare les échecs de l'une et de l'autre.

- *La première nuit.* Rejouée sur `main` une heure plus tard, la garde a
  fait tomber deux fichiers nés entre-temps. `test_pension_minimum_avant_1983.py`
  déclare le 15 dans `_calculer`. `test_cycle_de_vie_portage.py` confronte le
  Python au portage dans une fixture, que la garde ne lisait pas : elle lit
  désormais aussi les fixtures que le test demande (`_confronte_au_portage`,
  `tests/conftest.py`). La course du 14 octobre à 3 h 27, sur `91ab5fc`, a
  écrit `presomptions: vert`, sous une suite rouge pour d'autres causes.

**Ce qui reste.** les fiches de règles dans
l'empreinte, la fin du portage rejoué (notes du 10 octobre), `actions/cache`
au propriétaire.
