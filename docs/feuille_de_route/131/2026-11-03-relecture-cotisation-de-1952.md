# Relecture de la cotisation agricole de 1952

File R-K, vague 6, le 3 novembre 2026 : relecture indépendante du travail de la file K
(commits 79cbb6f, 737ea2f et 9386b3d ; note `2026-11-03-cotisation-de-1952.md`, renvoi au bout
de `2026-11-03-corrections-de-la-relecture-r-k.md`, fiche `cotisation_agricole_de_1952`).
Rien n'est repris de K ni de mémoire. Chaque texte est rouvert dans les index LEGI (à jour au
2 novembre 2026) et JORF (au 3 novembre 2026) de la DILA, récupérés ici
(`dila_index.py --recuperer`). Chaque chiffre est refait à la main, ou par un script de
brouillon hors du dépôt. L'effet sur le coût est isolé en refaisant le paquet dans un worktree
jetable, au dernier main, où 1952 reprend 8,5 %. Aucune règle, donnée ni test n'est modifié.

**Verdict : conforme sur l'essentiel.** L'article 45 est cité mot pour mot et appliqué comme il
le dit. Les valeurs des tests et les deux effets annoncés se refont au centime. Le coût passé
se refait au million près et ne doit rien à un autre commit. Deux écarts moyens, dont un
antérieur à K (§ 2 et § 5), et cinq écarts faibles (§ 2, 6, 7, 8).

## 1. Les textes : conforme

- Article 45 (LEGIARTI000019272803, du 19 octobre 1952, sans fin) : « Pour l'exercice 1952, les
  cotisations professionnelles visées aux articles 20 et 21 de la loi du 10 juillet 1952 sont
  égales à la moitié des cotisations annuelles. » La citation est exacte dans la note, la fiche
  et le test. La moitié est celle « des cotisations annuelles », les deux cotisations
  professionnelles : la personnelle de l'exploitant (article 20 de la loi, que nomme l'article
  14 du décret) et celle qui est assise sur le revenu cadastral (article 21, articles 17 et 22).
- Articles 5, 14, 15, 16, 22 et 23, rédactions du 19 octobre 1952 : citations exactes ; les
  coupures « [...] » des articles 5 et 22 n'ôtent rien qui change le sens. Dates exactes :
  article 14 jusqu'au 3 septembre 1972, 16 jusqu'au 22 avril 2005, 23 jusqu'au 9 juillet 1975.
- L'article 22 vise le chef et sa famille : les articles 8 et 9 qu'il cite n'ont à l'index que
  leurs rédactions du 8 août 1953, les exploitants (LEGIARTI000006763709) et « les membres de la
  famille de l'exploitant, à savoir le conjoint, les ascendants, descendants, frères, soeurs ou
  alliés au même degré » (LEGIARTI000006763710). K le dit.
- Les articles absents en 1952 (8, 9, 13, 18, 20, 29 et 30, « de 1953 à 1974 ») : liste exacte.
  Les articles 8 et 9 datent de 1953, 13 et 29 de 1964, 18 et 20 de 1965, 30 de 1974.
- Décret n° 99-875, article 2 (LEGIARTI000006779656, du 23 février 2001 au 2 mars 2002) ; décret
  n° 55-753, article 18 (LEGIARTI000006763581, du 3 juin 1955 au 22 avril 2005) : citations
  exactes. Ni l'un ni l'autre n'était en vigueur en 1952. K ne s'en sert que pour dater le
  régime du 1er juillet 1952, et il présente la demi-année comme une déduction.
- Loi n° 52-401, article 19 (LEGIARTI000006319216) : « une loi spéciale avant le 15 juin
  1952 », exact.
- Au JORF, la loi n° 52-799 n'a que sa notice (JORFTEXT000000512405) et un article sans texte
  (JORFARTI000001681101). L'arrêté du 23 juillet 1953 n'a que son titre, « TAUX DES
  COTISATIONS », et la mention « ASSURANCE VIEILLESSE AGRICOLE » (JORFTEXT000000435389). Aucun
  autre texte de 1952 ou 1953 sur ces cotisations (recherche plein texte). Ce que dit K est
  exact.

## 2. D'où viennent 4,25 % et 8,5 % : un écart moyen antérieur à K, un écart faible de K

4,25 % est la moitié de 8,5 %, la cotisation annuelle que le modèle donne à toutes ses périodes
de 1952 à 2002. Le texte dit « la moitié des cotisations annuelles », et le modèle prend bien la
moitié de sa propre cotisation annuelle. Mais aucune source ne justifie 8,5 % dans le dépôt :
- aucune note des périodes de `msa_non_salaries.yaml`, aucune fiche ni aucune limite ne le
  justifie (recherche de « 8,5 % » et de « 0.085 ») ; la source du régime, `msa_parametres`
  (`data/sources.yaml`), est la page d'accueil de la MSA ;
- le taux est là depuis le premier dépôt des fichiers (bdaecdbc, 8 septembre 2026,
  `non_salaries.yaml`, une période de 1952 à 2002), sans aucune note.

**Moyen, antérieur à K.** Toute cotisation agricole d'avant 2003 dépend de ce taux, dans les six
scénarios : les points tirés du rendement au scénario 1, le compte des scénarios 2 à 6. À porter
au propriétaire, avec la loi n° 52-799 et l'arrêté du 23 juillet 1953 au fac-similé.

**Faible, de K.** Pour cette convention, la note et la fiche du régime renvoient à « la période
de 1974 à 1985 ». Or ses notes déclarent l'assiette bornée au plafond, pas le taux. L'approximation
de la fiche donne pour effet « celui de la convention, que la fiche du régime déclare », alors
qu'aucune fiche ne déclare cette convention.

## 3. Les valeurs des tests : conforme

- 0,085 × 100 / 2 = 4,25 € pour 1952 ; 0,085 × 100 = 8,50 € pour 1953. Les 100 € sont sous le
  plafond, et l'article 45 ne distingue pas le collaborateur.
- Au scénario 1 : 8,50 × 9,154 266 (le coefficient de prix du moteur, de 1952 à 1990) =
  77,81 €, comme le dit la note.
- Le rouge est refait ici, dans le worktree jetable, 1952 remis à 8,5 % et le paquet refait. Le
  test échoue sur « {'msa_non_salaries': 8.5} == {'msa_non_salaries': 4.25} », la raison
  attendue. Sans paquet refait, il échoue déjà, sur l'accord des deux moteurs.

## 4. Les deux effets annoncés : conforme

Le témoin `statut_exploitant_agricole_1925` (né en janvier 1925, parti en février 1989, chef de
1952 à 1972), avec la carrière tirée de sa requête :
- revenu de 1952 : 554,335 9 € ; cotisation : 0,0425 × 554,335 9 = 23,559 3 € ; revalorisée
  aux prix de 1989 par le coefficient 8,855 739 du moteur : 208,634 8 € (417,269 6 € à 8,5 %) ;
- au rendement de 6 % (`rendements_points.csv`, régime agricole, de 1952 à 2100, « estimee »),
  sa pension proportionnelle perd 0,06 × 208,634 8 = 12,518 1 € ;
- majoration de D. 732-77 : P = 0,06 × 15 376,188 0 / 2,473 812 / 21 = 17,758 8, contre 17,999 8
  avant. Le taux reste de 5 % (entre 15 et 19,51) ; la majoration passe de 46,754 5 € à
  46,128 6 €, soit 0,625 9 € de moins ;
- ensemble, 13,144 0 €. Le témoin passe de 4 462,105 6 à 4 448,961 6 €, soit 13,143 99 € :
  exact. Son détail se refait : 2 014,25 € de forfait + 0,06 × 39 809,68 € + 46,13 € ;
- le collaborateur né en 1925 passe de 4 415,351 1 à 4 402,833 0 €, soit 12,518 1 €, sans
  majoration. Aux scénarios 2 à 6, les deux témoins passent de 1 112,565 3 à 1 109,558 8 €
  (−0,27 %) ;
- deux témoins seulement sur 930 changent entre 8ea1ce7 et 79cbb6f : exact.

## 5. La moyenne P compte 1952 pour une année entière : écart moyen

D. 732-77 (LEGIARTI000006597491, du 22 avril 2005 au 1er janvier 2026) borne la période « entre
le 1er juillet 1952 et le 31 décembre 1972 », et « Le terme P [...] représente le nombre annuel
moyen de points acquis par l'assuré au cours de la période mentionnée au premier alinéa ».
L'année 1952 n'entre dans la période que pour six mois. C'est une lecture, pas une citation :
le texte ne dit pas comment compter une année partielle.

Avant K, la cotisation entière, comptée pour une année, donnait le même P que la lecture des six
mois, pour un revenu constant. Depuis K, la demi-cotisation comptée pour une année entière
abaisse P de 2,4 % pour un chef de 1952 à 1972 (20,5 / 21), et davantage pour un chef de peu
d'années. La fiche `retraite_proportionnelle_msa` déclare la convention et cite la période. Mais
elle ne lui prête d'effet que pour le « chef de peu d'années », et « rien » pour le témoin.

Mesuré ici, sur le profil du témoin : l'assiette plafonnée borne P vers 18,5 points, même à
trois fois son revenu. Seul le seuil de 15 points peut donc se franchir. Un chef de 1952 à 1972
dont le P sur 20,5 années va de 15,00 à 15,37 tombe sous 15 points au modèle, et perd ses 5 %
entiers. Pour P = 15,2 : 0,05 × 15,2 × 2,473 812 × 21 = 39,5 € par an, en euros de 1989. Les
départs de 1986 à 1988, dont la valeur de service est plus basse, n'ont pas été mesurés.

**Moyen.** La lecture qui colle à la période compte 1952 pour 0,5 dans P, ce qui va avec la
demi-cotisation. Le choix revient au propriétaire : compter 1952 pour 0,5 dans P, ou garder la
convention et en déclarer la bande d'effet.

## 6. Le coût passé : il se refait ; unité et mécanisme manquent (écart faible)

- **Le calcul** (`cout.py`, `scripts/mesures_prose.py`, `cumul_passe`). Pour chaque année publiée,
  de 1959 à 2024 : la dépense observée, multipliée par le rapport entre la masse du scénario et
  celle du scénario 1 dans la grille des carrières types (`_rapports`), puis ramenée en euros
  de 2026 (`annee_euros: 2026`). Le cumul est la somme de ces années, en millions d'euros
  constants de 2026. Le scénario 1 est la dépense observée : par construction, il ne bouge pas.
- **Refait.** Somme des écarts annuels d'`agregats.json` entre 8ea1ce7 et 79cbb6f, chaque année
  multipliée par son coefficient : −2 563,0 M€ au scénario 2, −2 412,0 aux scénarios 4 et 6,
  +731,9 à la garantie, 0 au scénario 1. Les cumuls passent de 2 764,826 à 2 762,263 Md€
  (affichés 2 765 → 2 762), de 6 386,968 à 6 384,556 (6 387 → 6 385) et de 1 376,437 à
  1 377,169 (1 376 → 1 377).
- **L'écart ne vient pas d'un autre commit.** M4 (8ea1ce7) avait changé des règles des
  fonctionnaires sans refaire `agregats.json`, que K a ensuite refait. Le paquet refait ici, dans
  le worktree au dernier main où 1952 reprend 8,5 %, redonne au million près les mêmes écarts
  (−2,563, −2,412 et +0,732 Md€), avec les mêmes carrières types. La baisse annuelle est lisse,
  sans bosse après 2011 : −26 M€ en 1959, −70 M€ vers 1980, −0,8 M€ en 2024, en euros de 2026.
  Les avantages bougent chaque année d'un même rapport sur toutes leurs lignes (5,2
  millionièmes en 2015, minimum garanti et catégorie active compris), sauf le minimum vieillesse
  (+0,18 % à +0,43 %). C'est un effet d'échelle plus le minimum vieillesse, pas M4.
- **Plausibilité, observation pour la session du coût.** Moins de 0,1 % du cumul du scénario 2,
  pour la moitié de la cotisation d'une seule année, payée par des cotisants restés à la
  retraite jusque vers 2020 : l'ordre de grandeur n'a rien d'absurde. Il ne se borne pas par une
  source, car le dépôt n'a aucun effectif de cotisants agricoles avant 2010.
  Un point surprend. Dans la grille, en 1990, la masse du scénario 1 baisse de 0,007 7 %,
  et celle du compte de 0,037 9 % de cette même masse, soit cinq fois plus. La première baisse
  se lit aussi dans la reconstitution de 1990 (172 715,3 → 172 701,8 M€). Le témoin, lui, perd
  quatre fois plus au scénario 1 qu'au compte (13,14 € contre 3,01 €). C'est cette inversion qui
  fait baisser le coût des scénarios 2 à 6. À la proportion du témoin, le scénario 2 baisserait
  dix fois moins, et les scénarios 4 et 6 monteraient. Explication probable, non démontrée : les
  minima du scénario 1 (minimum vieillesse, qui monte, et majorations des petites retraites
  agricoles) amortissent la perte des chefs modestes, alors que le compte n'a pas de minimum.
- **Faible.** La note de K écrit « 2 765 → 2 762 Md € » sans dire qu'il s'agit d'euros constants
  de 2026. Elle donne « 240,22 → 238,19 » (millions d'euros de 1959) et « 104 274,10 →
  104 273,30 » (millions d'euros de 2024) sans unité. L'arrondi affiché suggère −3 Md€ quand
  l'écart est de −2,56. Elle ne dit pas que la reconstitution de 1990 passe de −9,6 à −9,7 %
  (`docs/limites/5-ter-trajectoire.md`, −9,644 → −9,651 %, au bord de l'arrondi), ni le
  mécanisme ci-dessus.

## 7. Les tests et le paquet : conforme, un écart faible

- `python -m pytest -m rapide` : 4 322 réussis, 6 sautés, 13 en échec, tous dans
  `test_pages_en_dossier.py` (les pages toutes faites, que GitHub refait). Sous
  `PRESOMPTIONS_DECALEES=1` : 4 123 réussis, 205 sautés, les mêmes 13 échecs.
- Les fichiers qui lisent les fichiers touchés (`grep -l`) et les confrontations de la zone :
  `test_conditions_selon_l_age`, `test_donnees`, `test_minima_agricoles`, `test_net_pensions`,
  `test_pension_minimum_avant_1983`, `test_prelevements_historiques`, `test_prose`,
  `test_regle_de_chacun`, `test_simulateur`, `test_sources_a_explorer`, `test_oracle`,
  `test_destinie`, `test_estimation_officielle`, `test_verification`, `test_pont`, `test_carte`,
  `test_contrats`, `test_saisie_de_la_reversion_agricole`. `test_cout` et `test_affirmations`
  sont laissés à GitHub. Résultat : 1 220 réussis, 1 sauté, 3 en échec dans `test_prose.py`.
  Deux sont attendus : le tableau de bord, et un chiffre ancré du README (le poids des scripts,
  916 → 918 Ko, qui vient de `moteur/js` et pas de K). Le troisième est
  `test_le_chiffrage_plf_n_est_pas_perime`.
- **Faible : ce dernier échec vient de K.** Dans le worktree où 1952 reprend 8,5 %,
  `chiffrage_plf.py --verifier` répond « le chiffrage est à jour ». Au dernier main, quatre
  cellules de `docs/chiffrage_plf.csv` bougent à la troisième décimale (par exemple 41,232 →
  41,231 en 2052, variante rétroactive). K ne l'a ni refait ni signalé ; GitHub le refait.
- `python scripts/construire_donnees.py` puis `git status` : rien à commiter. Le paquet de main
  (5 905 Ko) et `agregats.json` sont à jour.
- 79cbb6f ne change aucun code : la règle est écrite en données, que les deux moteurs lisent
  dans le même paquet.

## 8. Ce que le texte ne tranche pas : déclaré, deux écarts faibles

- Le montant et l'assiette réels de 1952 (loi n° 52-799, articles 19 à 21, au fac-similé du
  Journal officiel du 11 juillet 1952) sont déclarés : dans l'approximation de la fiche, dans
  ses `a_relire`, au § 6 de la note de K et dans son journal de veille. Conforme. La raison de
  la moitié, la « double cotisation » de l'article 19 et les points de la moitié sont dits
  déduits ou convenus. Conforme.
- **Faible.** La fiche est `transcrite` et n'a aucune rédaction non lue (`textes.py
  --non-lues`) ; elle n'apparaît donc pas dans la sortie de `veille_droit.py`. Ce qu'il lui
  reste à lire au fac-similé n'y sera pas rappelé. Six fiches `transcrite` sur trente portent
  ainsi des approximations, contre 142 fiches `approchee`.
- **Faible.** L'arrondi de l'article 23 : 10 / 100 / 6,559 57 = 0,015 24 €, et non « moins de
  0,015 € ». L'article 22 appelle la cotisation cadastrale par semestre : l'arrondi de « la
  cotisation réclamée » peut donc jouer deux fois par an (0,030 € au plus). Sans effet notable.

## 9. Les deux écarts faibles de R-K-bis : corrigés

La fiche `retraite_proportionnelle_msa` dit que la demi-année se déduit du 1er juillet 1952. La
limite ne dit plus que le régime « ne couvre que la seconde moitié ». La ligne `manque` dit
« n'est pas appliqué : R. 732-69, lu », dans `msa_non_salaries.yaml`, `inventaire.yaml` et
`docs/regimes.md`. La note de K-bis reste telle quelle, avec un renvoi daté.

## À reprendre

- Au propriétaire : la moyenne P de D. 732-77 doit-elle compter 1952 pour 0,5 (§ 5) ? Et d'où
  vient le taux de 8,5 % d'avant 2003 (§ 2) ?
- À la session du coût : l'inversion entre le scénario 1 et le compte dans la grille (§ 6).
- À la file K, ou à la suivante : préciser l'unité du coût dans la note, refaire
  `chiffrage_plf` (GitHub le fait), corriger le renvoi du taux de 8,5 % et la borne de
  l'arrondi.
