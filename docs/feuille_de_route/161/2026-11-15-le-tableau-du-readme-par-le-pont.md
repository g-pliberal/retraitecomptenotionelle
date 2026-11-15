# Le tableau du § 3 du README par le pont : la fabrique le met en forme, l'adresse du site remplace l'appel Python

Les deux exemples du README, l'agent de conduite de l'introduction et la
fonctionnaire du § 3, ne montrent plus d'appel au simulateur Python. Chacun
donne l'adresse du simulateur du site pour sa carrière, et son tableau est
ce que le portage simule de cette adresse. Les tableaux sont restés à
l'octet.

**La consigne.** Le point 1 de la note de décision 0008 : la seconde voie de
`2026-11-12-lot-a-les-sondes-par-le-pont.md`, « La question laissée au
propriétaire ».

**Ce qui change.**

- `scripts/construire_tableaux_md.py` simule chaque exemple par
  `pont.simulations`, sur la requête de l'adresse (`REQUETES`,
  `adresse_du_site`), et met en forme le résultat (`_Tableau`) : les six
  scénarios, la ligne hors répartition, le pilier et son total, qui verse
  la cotisation. C'est la mise en forme de `Comparaison.tableau()`, réduite
  aux lignes que le README reprend ; les titres des scénarios se lisent des
  univers, en données. Le bloc produit porte le lien vers le site.
- L'adresse `naissance=1975` (sans jour), `unite_revenu=moyen`, rend le
  même résultat, champ pour champ, que la carrière des sondes de la prose
  (`mesures_prose.EXEMPLES`) ; avec `naissance=1975-01-01`, le site liquide
  un mois plus tôt et les chiffres changent. `montants=brut` affiche sur le
  site les montants bruts du tableau sans changer le résultat.
- `README.md` : les deux blocs `python` partent, une phrase les remplace ;
  la boucle du détail par régime aussi, le site l'affiche.
- `construire_tableaux_md.py` n'entre plus dans le moteur Python :
  `ENTREES_DE_LA_FABRIQUE` le déclare vide, et toute la fabrique est hors du
  moteur Python sauf le chargeur des âges de `construire_donnees.py`.

**Les tests.** Vus rouges d'abord : la liste des entrées
(`tests/test_entrees_du_moteur.py`) et
`test_les_exemples_du_README_donnent_l_adresse_du_site_qu_ils_simulent`
(`tests/test_prose.py`), qui vérifie l'adresse dans chaque bloc, l'égalité
du résultat de l'adresse et de celui de la sonde, et l'absence d'appel
Python dans l'introduction et le § 3.
`test_le_README_montre_la_simulation_que_le_modele_calcule_vraiment`
(`tests/test_web.py`) confronte encore le README au `tableau()` du jumeau ;
il passe, et partira avec les tests du moteur Python.

**Ce qui reste.** `Comparaison.tableau()` n'a plus de lecteur dans la
fabrique ; il part au retrait, avec son test de `test_simulateur.py`. La
section « En Python, hors du site » du README appelle encore le simulateur
Python : elle n'était pas de cette étape, et se tranche au retrait.
L'étape suivante : le code mort du portage (`2026-11-12-le-code-mort.md`).
