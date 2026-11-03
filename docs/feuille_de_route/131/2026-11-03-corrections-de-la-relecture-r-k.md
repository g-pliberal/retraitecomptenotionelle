# Corrections de la relecture R-K : la majoration des points de chef de 1952 à 1972

File K-bis, le 3 novembre 2026 : les cinq écarts faibles de la relecture R-K (note
`2026-11-03-relecture-majoration-de-1986-a-2025.md`) des commits 7621be3 et 5835f0d de la
file K. Chaque texte a été rouvert ici dans les index LEGI (à jour au 2 novembre 2026) et
JORF (au 3 novembre 2026) de la DILA, récupérés, par `scripts/fetch/dila_cherche.py`,
sans rien reprendre de mémoire ni de R-K. Aucun calcul ne change : les écarts étaient de
rédaction ou de déclaration. Les deux fiches, la limite et les notes du paquet seulement.

## 1. Deux phrases de la fiche du régime, récrites d'après R. 732-69 et R. 732-66

R. 732-69, rédaction du 22 avril 2005 au 28 octobre 2017 (LEGIARTI000006597478), lu ici :
le nombre de points des cotisations d'avant la loi n° 90-85 « est déterminé selon le barème
suivant pour les années 1981 et suivantes : REVENU CADASTRAL NOMBRE DE POINTS », de 15 à
60 points, et « Pour les années antérieures à 1981, le nombre de points résulte des
dispositions des décrets n° 65-346 du 30 avril 1965, n° 67-570 du 21 juin 1967, n° 74-443
du 15 mai 1974 et n° 75-97 du 10 février 1975 ». L'index JORF n'a que les notices des
n° 67-570 (JORFTEXT000000514415) et 74-443 (JORFTEXT000000328985) ; les n° 65-346 et
75-97, cherchés par numéro et par date, n'y sont que cités.

- « aucun point ne s'acquiert par barème avant 1990 » (période de 1986 à 1989) devient :
  le modèle n'applique aucun barème avant 1990, mais ces années en ont un, celui de
  R. 732-69, cité mot pour mot. La même erreur, dans la période de 1974 à 1985 (« LE BARÈME
  DE POINTS N'EXISTE QU'À PARTIR DE 1990 »), est corrigée avec elle : R. 732-70 ne vaut
  qu'« A compter du 1er janvier 1990 », et les années d'avant ont le barème de R. 732-69.
- « une même année vaut les mêmes points quelle que soit la date du départ » devient :
  cotisations et valeur suivant les mêmes prix, au rendement de 6 % que
  `rendements_points.csv` donne au régime de 1952 à 2100, les points d'une même année ne
  changent avec la date du départ que par le rapport de 150 trimestres à la durée requise,
  que la valeur de service porte au moteur depuis 1990 (`liquider.py`, `coefficient_duree`),
  comme R. 732-66 (LEGIARTI000006597475, de 2007 à 2017) applique au point « le rapport de
  trente-sept et demi sur » la durée : à 172 trimestres, 172/150 fois les points d'un
  départ de 1989.
- La fiche des règles rangeait le décret n° 68-571 parmi ceux du barème : R. 732-69 ne le
  nomme pas, et sa notice (JORFTEXT000000330850) dit « VALIDATION D'ANNUITES
  SUPPLEMENTAIRES ». La liste suit R. 732-69, et une lecture le cite.
- La limite (`docs/limites/4-regimes-incomplets.md`) disait aussi « le barème de points
  n'est pas lu » et « au fac-similé » pour toutes ces années : récrite de même.

Reste inexacte à la lettre, et laissée : la ligne `manque` de la fiche du régime (« Le
barème en points d'avant 1990 n'est pas lu »), qui descend à `inventaire.yaml`, à
`docs/regimes.md` et à `docs/etat.md` ; elle se lit « pas appliqué » et se corrigera avec
l'inventaire.

## 2. L'identifiant du décret n° 86-1084

`dila_cherche.py legi --texte LEGITEXT000006065220` rend « Décret n°86-1084 du 7 octobre
1986 relatif à l'harmonisation des pensions de retraite [...] », dont les visas citent « le
décret n° 81-790 du 18 août 1981 portant relèvement exceptionnel des retraites
proportionnelles des personnes non-salariées de l'agriculture ». Une recherche de « 81-790 »
dans LEGI ne trouve que des textes qui le visent (décrets n° 86-1084, 94-714, 97-163, 98-125
et suivants, et le décret n° 2005-368, article 3, 65°) : il n'y a pas de texte. Au JORF, sa
seule notice, JORFTEXT000000335107. La fiche attache désormais LEGITEXT000006065220 et
JORFTEXT000000870113 au décret n° 86-1084, et JORFTEXT000000335107 au n° 81-790.

## 3. Le 1er juillet 1952

Ce que disent les textes, lus ici :

- D. 732-77 (LEGIARTI000006597491) et l'article 2 du décret n° 86-1084
  (LEGIARTI000006769405) : les points « acquis [...] au titre de la période comprise entre
  le 1er juillet 1952 et le 31 décembre 1972 » ; P, « le nombre annuel moyen de points
  acquis par l'assuré au cours de la période ».
- Le 1er juillet 1952 est le jour où le régime naît : « la date de création du régime
  d'assurance vieillesse des professions non salariées agricoles, à savoir le 1er juillet
  1952 pour la métropole » (décret n° 99-875, article 2, LEGIARTI000006779656, de 2001 à
  2002). Aucun point du régime ne la précède : la borne n'exclut rien de ce que le modèle
  compte.
- L'exercice 1952 n'a qu'une demi-année : « Pour l'exercice 1952, les cotisations
  professionnelles visées aux articles 20 et 21 de la loi du 10 juillet 1952 sont égales
  à la moitié des cotisations annuelles » (décret n° 52-1166, article 45,
  LEGIARTI000019272803).
- Les points de 1952 relèvent des décrets auxquels R. 732-69 renvoie pour les années
  antérieures à 1981, non lus ; la loi n° 52-799 n'est à l'index JORF que par sa notice
  (JORFTEXT000000512405), et rien ne dit laquelle des cotisations de ses articles 19 à 21
  donnait des points. Aucun texte ne dit non plus si P compte 1952 pour une année ou pour
  une demie.

Le texte ne tranche donc pas comment compter les points de cette demi-année : déclaré dans
`a_relire` de la fiche `retraite_proportionnelle_msa`, comme convention, sans changer le
calcul. Effet chiffré pour le témoin de chef né en 1925 (`statut_exploitant_agricole_1925`,
parti en février 1989, chef de 1952 à 1972), le seul des trois témoins que la majoration
touche qui ait 1952,
par un script de brouillon qui reprend sa carrière au portage et les cotisations que le
moteur Python passe à `majoration_des_points_de_1952_a_1972_d_avant_2026` :

| Lecture | Cotisations de la période | P | T | Majoration |
|---|---|---|---|---|
| le modèle : 1952 entière, une année | 15 584,82 € | 15 584,82 × 0,06 / 2,473 812 / 21 = 18,00 | 5 % | 0,05 × 935,09 = 46,75 € |
| la moitié de 1952, une année | 15 584,82 − 417,27 / 2 = 15 376,19 € | 922,57 / 2,473 812 / 21 = 17,76 | 5 % | 0,05 × 922,57 = 46,13 € |
| la moitié de 1952, une demi-année | 15 376,19 € | 922,57 / 2,473 812 / 20,5 = 18,19 | 5 % | 46,13 € |

La cotisation de 1952, revalorisée aux prix de 1989, vaut 417,27 € au modèle (10,12
points). Effet au plus pour ce témoin : 46,75 − 46,13 = 0,63 € par an (0,6259), en euros
de 1989 ; dans le reste de sa pension proportionnelle, la moitié de la cotisation de 1952
vaut 417,27 × 0,06 / 2 = 12,52 € par an. En général : T fois la pension de cette moitié,
45 % au plus, et le déplacement de P, qui peut faire passer un seuil au chef de peu
d'années.

Ce que ce point laisse ouvert, au-delà de la majoration : le modèle prélève en 1952 la
cotisation d'une année entière, partout dans la pension proportionnelle, quand le décret
n° 52-1166 n'en demande que la moitié. Ce serait un calcul à corriger dans une étape à
lui, avec la question des années au prorata de l'exploitant, déjà posée au propriétaire.

## 4. L'arrondi

Ni D. 732-77 ni l'article 2 ne disent s'il faut arrondir T ou les points majorés ;
R. 732-67 (LEGIARTI000053328816, depuis 2026), lu ici : « Sauf si le résultat est déjà
entier, les nombres de points annuels ainsi obtenus sont arrondis aux entiers
supérieurs ». Le modèle n'arrondit ni l'un ni l'autre : déclaré comme convention dans
`a_relire`, avec son effet au plus, posé à la main :

- T au centième de point : |ΔT| ≤ 0,005 point, la majoration bouge de 0,005 % au plus de
  la pension des années de la période ; au point entier, de 0,5 % au plus. Pour les
  témoins : 5 % et 5 % ne bougent pas ; 15,9985 % → 16 % : 0,0015 % × 553,99 = 0,008 €.
- Le total des points majorés arrondi à l'entier : un point au plus, une valeur de
  service, 2,473 812 € (1989), 2,982 180 € (1999), 3,447 601 € (2009), 4,589 € au plus
  en 2025.
- Chaque année arrondie à l'entier supérieur, comme depuis 2026 : un point au plus par
  année de chef de la période, 21, 17 et 7 pour les trois témoins.

## 5. Le paquet de 7621be3

Le commit 7621be3 portait, seul, le paquet d'avant (la période de 1986 à 1989 sans valeur
de service) ; 5835f0d l'a refait 28 minutes plus tard, et la suite de GitHub l'a dit vert.
Rien à faire. Ici, les notes de la fiche du régime entrent au paquet : refait par
`python scripts/construire_donnees.py`, deux notes changées, rien d'autre, et commité avec
les fiches.

## Les tests

Aucun comportement ne change : pas de test nouveau. `python -m pytest -m rapide` : 4 242
réussis, 6 sautés ; sous `PRESOMPTIONS_DECALEES=1` : 4 044 réussis, 204 sautés ; ceux de
la zone (`test_simulateur.py -k` la majoration et le régime agricole,
`test_minima_agricoles.py`, `test_saisie_de_la_reversion_agricole.py`,
`test_regle_de_chacun.py`, `test_contrats.py`, `test_pension_minimum_avant_1983.py`) : verts.

La question de D. 732-76 au propriétaire demeure, non traitée ici.
