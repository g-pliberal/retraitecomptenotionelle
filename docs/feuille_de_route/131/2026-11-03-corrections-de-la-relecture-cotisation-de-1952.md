# Corrections de la relecture R-K : la cotisation agricole de 1952 et le taux de 8,5 % d'avant 2003

File K-bis, vague 6, le 3 novembre 2026 : les écarts que la relecture R-K
(`2026-11-03-relecture-cotisation-de-1952.md`, commit 5cda0b8) relève dans le travail de la
file K (`2026-11-03-cotisation-de-1952.md`). Chaque texte cité a été ouvert ici, dans les index
LEGI (à jour au 2 novembre 2026) et JORF (au 3 novembre 2026) de la DILA, récupérés
(`dila_index.py --recuperer`), par `dila_cherche.py` et une lecture directe de l'index ; chaque
citation de la fiche neuve a été comparée, par un script, au texte de l'index, mot pour mot.
Aucune règle du modèle ne change, ni aucun calcul : les deux écarts moyens se déclarent, avec
leur question au propriétaire, et les écarts faibles se corrigent dans les fiches.

## 1. Le taux de 8,5 % d'avant 2003 : aucun texte ne le fixe (écart moyen, antérieur à K)

Le modèle prélève 8,5 % du revenu de l'année borné au plafond de 1953 à 2002, la moitié en
1952 (`msa_non_salaries.yaml`, cinq périodes). Les textes de chaque année ont été cherchés et
lus, période par période. Aucun ne fixe ce taux. Ce qu'ils disent est dans une fiche neuve,
`cotisation_vieillesse_agricole_avant_2003` (`approchee`), qui cite mot pour mot 80 articles.

- **Avant 1983 : pas à l'index.** La loi n° 52-799, dont les articles 19 à 21 fixent les
  cotisations, n'y est que par sa notice (JORFTEXT000000512405), comme l'arrêté du 23 juillet
  1953 « TAUX DES COTISATIONS » (JORFTEXT000000435389). De 1952 à 1982, le JORF de l'index n'a
  de ces textes que des notices, sans les montants (le décret n° 82-396 du 11 mai 1982,
  JORFTEXT000000519366, y est sans texte). LEGI n'a l'article 1123 du code rural que depuis sa
  rédaction du 5 juillet 1980 (LEGIARTI000006581056) : une « double cotisation
  professionnelle », l'une par membre non salarié, l'autre « à la charge de chaque exploitation
  ou entreprise et dont le montant global est fixé chaque année dans le budget annexe des
  prestations sociales agricoles ». Aucun décret annuel de financement n'y est avant le
  décret n° 83-664 du 21 juillet 1983.
- **De 1983 à 1989 : des montants en revenu cadastral.** Les sept décrets annuels (n° 83-664,
  84-585, 85-735, 86-596, 87-612, 88-688, 89-510), lus article par article, fixent la
  cotisation du a de l'article 1123 en francs par tranche de revenu cadastral (de 340 F à
  860 F en 1983, article 10, LEGIARTI000006764296 ; jusqu'à 2 010 F en 1989, article 10,
  LEGIARTI000006774422), et le plafond du revenu cadastral qui sert d'assiette à la cotisation
  cadastrale de l'article 1125 (23 359 F en 1983, 31 448 F en 1989, article 9 de chacun).
  Aucun taux sur le revenu ; aucun ne donne le montant de la cotisation cadastrale par franc
  de revenu cadastral, dont l'article 1123 dit le « montant global » fixé au budget annexe.
- **De 1990 à 1992 : une assiette mixte.** Décrets n° 90-765, 91-912 et 92-793 : en 1990 et
  1991, le a reste un montant par tranche ; le b a une part cadastrale (article 1125) et une
  part de 2,25 % (1990), puis de 7,41 % (1991), des revenus bornés au plafond ; le c (article
  1123 depuis le 20 janvier 1991) porte sur leur totalité, 1,155 % en 1991, 1,28 % en 1992 ;
  en 1992, le b est 8,105 % des revenus bornés au plafond (article 1125 : « Son taux est fixé
  par décret »), et le a ajoute un second élément de 1,23 %. S'y ajoute la cotisation
  complémentaire, fixée par arrêté préfectoral autour d'un taux moyen.
- **De 1993 à 2002 : trois taux.** Les dix décrets annuels (n° 93-1153 à 2002-1228) : le a
  (1° de L. 731-42 depuis 2000), borné au plafond, 3,06 % en 1993, 3,10 % en 1994 et 1995,
  3,2 % de 1996 à 2002 ; le b (2°, puis a du 2°), borné au plafond, 8,140 %, 8,36 %, 8,27 %,
  8,445 % de 1996 à 1998, 8,44 % de 1999 à 2002 ; le c (3°), sur la totalité des revenus,
  1,306 %, 1,34 %, 1,26 %, 1,29 % de 1996 à 2002 ; la complémentaire, autour de 2,30 % à
  2,53 % de la partie plafonnée et de 0,16 % à 0,25 % de la totalité.
- **En 2003**, le décret n° 2003-1033 reprend les taux de 2002 (articles 12, 13, 16 et 17,
  LEGIARTI000006781102, 103, 106 et 107). Le modèle, lui, passe de 8,5 % en 2002 à 17,37 % en
  2003 : cette lecture ne retrouve pas ce taux, et ne le change pas (hors de la tâche).

Ce que l'écart touche. Au scénario 1, avant 1990, le rendement de 6 % tire les points de
cette cotisation : 8,5 % × 6 % = 0,51 % du revenu borné au plafond par année de chef,
revalorisé ; depuis 1990, le barème de R. 732-71 tire les points de l'assiette, non du taux
(vérifié au moteur : un chef de 1990 à 2002 sort « 869.00 points × valeur de service »). Aux
scénarios 2 à 6, le compte reçoit ces 8,5 %. Posé à la main, pour un revenu sous le plafond en
1996 : les trois cotisations nationales prélèvent 3,2 + 8,445 + 1,29 = 12,935 %, et 15,715 %
avec la complémentaire au taux moyen (2,53 + 0,25) ; 8,5 / 12,935 = 66 % et 8,5 / 15,715 =
54 % de ce qui est prélevé. Effet sur le coût : non mesuré.

**Rien n'est changé dans le modèle**, et la question est au propriétaire (§ 6) : quels taux
porter au compte, et quelle convention avant 1993, sans le revenu cadastral. La fiche du
régime le dit dans ses périodes de 1952, de 1974 à 1985 et de 1990 à 2002 ; la limite
(`docs/limites/4-regimes-incomplets.md`, ligne des non-salariés agricoles), aussi.

## 2. La moyenne P compte 1952 pour une année : le texte ne tranche pas (écart moyen)

Lu à chaque version qui compte. Pour les pensions prises du 1er juillet 1986 au 21 avril
2005, l'article 2 du décret n° 86-1084 (LEGIARTI000006769405) ; du 22 avril 2005 au
31 décembre 2025, D. 732-77 (LEGIARTI000006597491) : « Le terme P [...] représente le nombre
annuel moyen de points acquis par l'assuré au cours de la période mentionnée au premier
alinéa », celle « comprise entre le 1er juillet 1952 et le 31 décembre 1972 ». Depuis 2026,
R. 732-67 (LEGIARTI000053328816) vise les conditions « relatives au nombre moyen de leurs
points au titre de l'ensemble de la période comprise entre le 1 er juillet 1952 et le 31
décembre 1972 ». La rédaction de 2026 de D. 732-77 (LEGIARTI000053365517) traite d'autre
chose. Aucun de ces textes ne dit comment compter une année que la période ne couvre qu'à
moitié ; les décrets n° 97-163 (article 2, LEGIARTI000006771705) et 2002-297 (article 5,
LEGIARTI000006780505), qui calculent un « nombre annuel moyen de points » pour d'autres
majorations, le disent pour eux (« en divisant le nombre de points retenu en application du
2° du I par la durée reconstituée »), et ne valent pas pour celle-ci. **Le calcul est gardé**, et les deux lectures
sont déclarées dans la fiche `retraite_proportionnelle_msa` (`a_relire`, « Les points de
1952 »), renvoyées de `cotisation_agricole_de_1952`.

Les deux lectures, S étant les points des n années de chef de la période :
(A) 1952 compte pour une année, P = S / n, la convention du modèle, avant 2026 comme depuis ;
(B) 1952 compte pour une demie, comme sa cotisation, P = S / (n − 0,5), plus haut de
S / (n − 0,5) − S / n = S / (2n(n − 0,5)).

Effet de A au lieu de B, posé à la main :
- au seuil de quinze points, le chef dont S va de 15(n − 0,5) à 15n perd ses 5 %. De 1952 à
  1972, n = 21 : S de 15 × 20,5 = 307,5 à 15 × 21 = 315 points ; P de 307,5 / 21 = 14,64 à 15
  sous A, de 15 à 315 / 20,5 = 15,37 sous B. Il perd 0,05 × S × la valeur de service : pour
  un départ de 1989 (2,473 812 €), 0,05 × 307,5 × 2,473 812 = 38,03 € à 0,05 × 315 ×
  2,473 812 = 38,96 € par an ; en euros de 2025 (4,589 €), 70,56 € à 72,28 € ;
- de 19,51 à 27,34 points, le taux baisse de 3,19 × S / (2n(n − 0,5)) points. Un chef de 1952
  sans interruption n'y arrive pas : au plafond chaque année de 1952 à 1972, P = 18,18 au
  moteur (S = 381,813 4), pour des départs d'août 1986, de 1989, de 1994 et de 1999 (les
  points d'avant 1990 ne changent pas avec la date du départ à durée requise de 150
  trimestres), soit 381,813 4 / 20,5 = 18,63 sous B : 5 % dans les deux cas. Un chef de 1952,
  puis de 1966 à 1972 seulement, au plafond, parti en 1989, y arrive : S = 176,660 2 sur
  n = 8 ; P = 22,08 sous A, 176,660 2 / 7,5 = 23,55 sous B ; T = 3,19 × 22,082 5 − 57,23 =
  13,21 % et 3,19 × 23,554 7 − 57,23 = 17,91 % ; la pension de ces points, 176,660 2 ×
  2,473 812 = 437,02 € ; la majoration, 57,75 € sous A et 78,27 € sous B : 20,52 € de moins
  par an ;
- le témoin `statut_exploitant_agricole_1925` (chef de 1952 à 1972, parti en 1989) : P =
  17,76 sous A, 18,19 sous B, 5 % dans les deux cas : rien.

R-K écrivait 39,5 € pour P = 15,2 (0,05 × 15,2 × 2,473 812 × 21) : si P = 15,2 se compte sur
20,5 années, comme sous B, S = 311,6 et la perte est 0,05 × 311,6 × 2,473 812 = 38,54 €.
Les valeurs S, P et la valeur de service viennent d'un script de brouillon, hors du dépôt, qui
lit les points que le moteur Python passe à la majoration
(`majoration_des_points_de_1952_a_1972_d_avant_2026`) ; les taux et les euros sont refaits à
la main. Une lettre de la MSA qui dirait comment elle compte 1952 trancherait (§ 6).

## 3. Les écarts faibles

- **Le renvoi du taux à « la période de 1974 à 1985 »**, qui ne déclarait que l'assiette :
  cette période déclare désormais le taux (« LE TAUX DE 8,5 % EST UNE CONVENTION »), et la
  période de 1952, comme l'approximation de `cotisation_agricole_de_1952`, renvoient à la fiche
  neuve ; l'effet de cette approximation dit « non mesuré, la cotisation réelle de 1952 ne se
  chiffrant pas sans la loi n° 52-799 », et non plus « celui de la convention, que la fiche du
  régime déclare ».
- **L'unité et le mécanisme du coût passé**, que la note de K ne dit pas. Vérifié ici :
  `cumul_passe` (`scripts/mesures_prose.py`) est le « Cumul du coût d'un système sur les années
  observées, en Md€ constants », et `agregats.json` porte `annee_euros: 2026` ; le tableau du
  README le titre « Cumul 1959-2024, euros de 2026 ». Les cumuls d'`agregats.json`, relus aux
  deux commits : scénario 2, 2 764 825,8 → 2 762 262,8 M€, soit −2 563,0 M€, −2,56 Md€ en
  euros constants de 2026 (et non −3, que suggère l'arrondi « 2 765 → 2 762 ») ; scénarios 4 et
  6, 6 386 968,0 → 6 384 556,0 M€, −2 412,0 M€ ; garantie, 1 376 437,0 → 1 377 168,9 M€,
  +731,9 M€ ; scénario 1 inchangé, 13 766 728,8 M€. Les deux chiffres sans unité de K,
  « 240,22 → 238,19 » et « 104 274,10 → 104 273,30 », sont les `couts` de l'année
  (`cout.annees`, 1959 et 2024), en millions d'euros de cette année-là, à côté de la dépense
  observée de 1959, 2 208,6. Le mécanisme, que dit le README : « Sur la part de cette dépense
  observée qui est une pension de répartition obligatoire, le modèle applique le rapport des
  masses de pension entre systèmes », celui de la grille des cas types, et le scénario 1 est
  la dépense observée. L'inversion que R-K relève dans la grille, entre le scénario 1 et le
  compte, est laissée à la session du coût, comme le veut la tâche. La note de K reste telle,
  avec un renvoi daté à celle-ci.
- **La fiche absente de `veille_droit`** : `cotisation_agricole_de_1952`, `transcrite`, lue le
  3 novembre 2026, sans rédaction non lue, n'est pas « à relire » (`carte.a_relire` : état
  `a_verifier` ou `manquante`, lecture de plus de cent vingt jours, relecture passée,
  rédaction en vigueur non lue) ; elle y reparaîtra d'elle-même le 3 mars 2027. Ce qu'elle
  laisse au fac-similé, la loi n° 52-799, est désormais rappelé par la fiche neuve, que
  `veille_droit.py` imprime dès aujourd'hui, avec sa question au propriétaire et ce qui reste
  à lire au fac-similé : elle cite L. 731-42, dont la rédaction du 28 février 2025
  (LEGIARTI000051284150), en vigueur, n'est coupée en aucune version, puisqu'elle régit les
  cotisations depuis 2026, hors de son objet. Les rédactions de l'article 1123 du 31 décembre 1988 et du
  10 juillet 1999, et la première de L. 731-42, y sont déclarées sans effet, avec le mot à
  mot qui le montre. Rien n'est changé au script.
- **La borne de l'arrondi** de l'article 23 : 10 anciens francs = 0,10 franc, et 0,10 /
  6,559 57 = 0,015 24 € par cotisation réclamée ; l'article 22 réclame la cotisation
  cadastrale par semestre et ajoute la cotisation personnelle à celle du second : deux
  réclamations par an au plus, moins de 2 × 0,015 24 = 0,030 5 € par an. Corrigé dans
  `cotisation_agricole_de_1952`.
- `docs/chiffrage_plf.csv`, que R-K trouve périmé : laissé à GitHub, comme le veut la tâche.

## 4. Ce qui change dans le dépôt

- Fiche neuve `cotisation_vieillesse_agricole_avant_2003` : six versions (avant le régime ;
  avant 1983, supposée ; 1983 à 1989 ; 1990 à 1992 ; 1993 à 2002 ; depuis 2003), 80 textes
  cités mot pour mot, trois déclarés sans effet, cinq approximations, la question au
  propriétaire. `carte.controler()`
  n'y trouve rien, `carte.manques()` rien, `outils_carte.ecarts` rien.
- `msa_non_salaries.yaml` : les notes des périodes de 1952, de 1974 à 1985 et de 1990 à 2002.
  Le paquet refait (`construire_donnees.py`) ne change que ces trois notes ; `agregats.json`
  ne bouge pas.
- `cotisation_agricole_de_1952` : l'approximation du taux, la borne de l'arrondi, la moyenne
  P, l'historique. `retraite_proportionnelle_msa` : « Les points de 1952 », les deux lectures.
- `docs/limites/4-regimes-incomplets.md` : la ligne des non-salariés agricoles, le taux
  (ancré sur la fiche du régime) et son effet, non mesuré.

## 5. Les tests

Aucun comportement ne change, aucun code non plus : pas de test neuf. Sur l'état commité :
`python -m pytest -m rapide`, 4 330 réussis, 6 sautés, 13 en échec, tous de
`test_pages_en_dossier.py` (les pages toutes faites de Coût, d'Avantages et de Méthode, que
GitHub refait). Sous `PRESOMPTIONS_DECALEES=1`, sans ce fichier : 4 059 réussis, 205 sautés,
aucun échec. Les tests de la zone et ceux qui lisent les fichiers touchés (`test_oracle`,
`test_destinie`, `test_estimation_officielle`, `test_verification`, `test_pont`,
`test_conditions_selon_l_age`, `test_minima_agricoles`, `test_pension_minimum_avant_1983`,
`test_prelevements_historiques`, `test_regle_de_chacun`, `test_simulateur`, `test_carte`,
`test_contrats`, `test_donnees`, `test_prose`, `test_outillage`, `test_versions`,
`test_univers`, `test_jumeaux`, `test_saisie_de_la_reversion_agricole`,
`test_sources_a_explorer`, `test_net_pensions`, `test_textes`) : 1 346 réussis, 1 sauté,
3 en échec dans `test_prose.py`, que GitHub refait : le tableau de bord, `chiffrage_plf.csv`
(périmé depuis K), et le poids du paquet dans quatre chiffres ancrés (5 905 → 5 907 Ko, les
trois notes de la fiche du régime). `verifier_prose.py` ne relève que ces quatre ancres.

## 6. Les questions au propriétaire

1. **Le taux du compte avant 2003.** Faut-il porter au compte des scénarios 2 à 6, de 1993 à
   2002, la somme des taux lus, et lesquels : le a et le b, bornés au plafond (11,20 % à
   11,645 %), le c, sur la totalité du revenu (1,26 % à 1,34 %), la complémentaire, que chaque
   département fixe autour d'un taux moyen ? Et quelle convention avant 1993, où la cotisation
   est assise en tout ou partie sur le revenu cadastral, que le modèle n'a pas ? Pour les
   années d'avant 1983 : la loi n° 52-799 (Journal officiel du 11 juillet 1952), l'arrêté du
   23 juillet 1953 et les textes de financement de 1953 à 1982, au fac-similé. Le taux de
   17,37 % de 2003, que le décret n° 2003-1033 ne donne pas, appelle la même question.
2. **1952 dans la moyenne P.** Compter 1952 pour une année (A, le modèle) ou pour une demie
   (B) ? Le texte ne tranche pas ; une lettre à la MSA le pourrait. L'effet de A est au plus
   de 5 % de la pension des points de 1952 à 1972 (38 à 39 € par an pour un départ de 1989),
   pour une bande étroite de chefs, et de quelques points de taux pour des carrières
   interrompues après 1952.
