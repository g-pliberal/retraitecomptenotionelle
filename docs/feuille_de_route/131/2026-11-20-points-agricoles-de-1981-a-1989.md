# Les points agricoles de 1981 à 1989, au barème du revenu cadastral

Le 20 novembre 2026, la session branche le barème que la fiche
`retraite_proportionnelle_msa` citait sans l'appliquer. L'étape s'est menée
sur Fable 5.2. La lecture d'origine et les trois voies comparées sont dans la
note de passage de main du même jour, au dossier du projet
(`ecarts/2026-11-20-points-agricoles-avant-1990.md`).

**Lu**, par l'index LEGI. Décret n° 80-808 du 14 octobre 1980, article 8
(LEGIARTI000006769209, du 1er janvier 1981 au 21 septembre 1990) : les points
de chaque année, « en fonction des cotisations versées en application du 1°,
b, de l'article 1123 », suivent « le barème annexé ». Annexe
(LEGIARTI000006769235) : 15 points pour un revenu cadastral « au plus égal à
1180 F », 30 « de 1180 F à 5571 F », 45 « de 5571 F à 9830 F », 60 au-delà.
R. 732-69 du code rural le reprend « pour les années 1981 et suivantes »
(LEGIARTI000006597478, LEGIARTI000035918355). Décret n° 92-793, article 20
(LEGIARTI000006776481) : « 5,54 F de revenu professionnel pour 1 F de revenu
cadastral », pour la cotisation de solidarité de 1992.

**Le défaut.** Aucune année d'avant 1990 n'avait de points : le moteur les
servait par le rendement de leurs cotisations, 6 % de 8,5 % du revenu.

**La correction.** Une fiche neuve, `points_agricoles_au_revenu_cadastral`,
porte dans ses versions les seuils, les points et le rapport de 5,54 ; le
moteur les y lit (`pointsAuRevenuCadastral`, `revenuCadastralDeduit`, dans
`acquerir.js`). La période de 1974 de `msa_non_salaries.yaml` est coupée en
1981, et les périodes de 1981 à 1989 nomment le barème. Le revenu cadastral
se déduit du revenu entier de l'année : c'est une convention, que le
propriétaire a retenue le 20 novembre 2026 sur une carte de décision. Le
barème ne vaut que pour la ligne d'exploitant, dont il compte les
cotisations ; le conjoint et l'aide familial restent au rendement. Les
points sont portés à seize pour une pension de 1994 à 2025 (R. 732-73, qui
vise R. 732-69). La période de 1981 à 1985 reçoit la valeur du point des
suivantes, pour servir ces points aux pensions prises alors. Les années
d'avant 1981 restent au rendement.

**Ce qui bouge**, chef d'exploitation né en 1960, installé à vingt ans, parti
à soixante-deux ans, montants annuels de la pension totale, base et
complémentaire, minima compris :

| Revenu | Points de 1981 à 1989 | Avant | Après |
|---|---|---|---|
| la moitié du salaire moyen | 390 | 12 814,86 € | 12 815,17 € |
| le salaire moyen | 540 | 18 969,94 € | 19 889,62 € |
| deux fois le salaire moyen | 540 | 21 594,83 € | 22 217,77 € |

Au demi-salaire moyen, la base gagne 917,89 € et le complément différentiel
de la complémentaire en rend 917,58 : la pension totale ne bouge pas. Au
salaire moyen, rien n'absorbe la hausse, 4,8 %. Né en 1930 et parti à
soixante-cinq ans au salaire moyen : 6 576,73 € avant, 7 152,55 € après,
8,8 % de plus. Quatre témoins de simulation sur 937 bougent, tous
d'exploitants, de 4,43 % à 11,21 %, sans aucune baisse.

**Ce que les minima lisent.** Les plans de 1997 à 2008 et la pension majorée
de référence reconstituent la durée de chef des points au compte : ils lisent
désormais les points du barème. Treize tests de
`tests/test_minima_agricoles.py` posaient des chefs dont la moyenne restait
sous seize points parce que leurs années de 1981 à 1989 n'en avaient pas ;
leurs carrières sont reprises sur une petite exploitation, 6 000 F de revenu
de 1981 à 1989, quinze points par an. Le chef à titre secondaire de 1982 à
1986 part désormais en 1993, avant le plancher de seize points : avec lui,
chaque année secondaire garde un point après les quinze retranchés, et la
durée reconstituée passe la durée agricole.

**Reste.** Les seuils, en francs courants, ne sont relevés par aucun texte lu
de 1981 à 1989, et le rapport de 5,54 est celui de 1992 : sur des revenus qui
montent avec les prix, le chef au salaire moyen est à 60 points dès 1981. La
pratique de la caisse n'est pas vérifiée et aucun exemple chiffré n'a été
trouvé. Les décrets d'avant 1981 sont à lire au fac-similé. Le champ de
saisie des points du relevé, qui primeraient, est à écrire, zone du site.
