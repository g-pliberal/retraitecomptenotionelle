# Étape 3, deuxième partie : la décomposition dépendance × couverture × prestation, confrontée à l'Ageing Report de 2024

**La demande.** Le propriétaire, le 13 octobre 2026 : « Action 138, étape 3 :
la décomposition dépendance × couverture × prestation, confrontée à l'Ageing
Report de 2024. Écris-la à part de cout.py, que l'action 147 récrit, en lisant
ses sorties. La CNRACL est réglée par l'action 152 (note de son étape 2). » En
parallèle, l'action 152 tient `castypes.py`, `cas_types_csp.yaml` et
`grille_large.py`, l'action 147 `cout.py`, une seule session `pages.js` et
`index.html` : rien n'y est écrit, et ce qui devrait l'être dans les pages est
plus bas. C'est le point 1 de « Ce qui reste » de la première partie : registre,
`ageing_report` (points 1 et 2), et `maquette_globale_cor`, à relire.

**Ce que l'Ageing Report publie, lu le jour même.** La fiche France de 2024, le
volume 1 (Institutional Paper 279) et l'annexe statistique des fiches pays, sur
le site de la Commission. La dépense de pensions publique brute — vieillesse et
anticipées, minimum vieillesse compris, invalidité et survivants — passe de
14,4 % du PIB en 2022 à 13,6 % en 2070 (tableau 7). Sa décomposition (figure 4,
équation 1 ; encadré I.1.1 du volume 1) :

    dépense / PIB = (65 ans et plus / 20-64 ans) × (pensionnés / 65 ans et plus)
                  × (pension moyenne / PIB par heure travaillée des 20-74 ans)
                  × (20-64 ans / heures travaillées des 20-74 ans)

De 2022 à 2070 (tableau 9 ; annexe, feuille FRb) : dépendance +6,04 points,
couverture −2,21, prestation −3,40, marché du travail −1,05, résidu −0,26. La
couverture se partage en celle des 65 ans et plus (−0,33) et celle des plus
jeunes rapportée aux 50-64 ans (−4,98), fois l'effet de cohorte (−5,44), trois
effets qui ne s'ajoutent pas ; le marché du travail en taux d'emploi (−0,92),
intensité (+0,02) et carrières au-delà de 64 ans (−0,15). L'annexe porte tout cela année par année, sans
arrondi, avec les séries qui le font : pensionnés (20,3 millions en 2022, 24,6
en 2070), dépendance (38,2 % puis 57,8 %), emploi, population EUROPOP2023
(fécondité de 1,82 puis 1,79, solde migratoire de 80 000 à 100 000 par an après
2025), productivité horaire de 1,03 % par an en moyenne.

**La formule de ses effets, retrouvée.** Ni la fiche ni le volume 1 ne disent
comment un effet se chiffre. Essayées sur les séries de l'annexe : le
logarithme du facteur fois la dépense de 2022 (6,006 pour la dépendance, contre
6,039 publié), la même chose année par année (5,858), la variation relative
année par année (5,894)… La bonne est la variation relative sur des pas de cinq
ans — 2022, 2025, 2030, …, 2070 —, multipliée par la dépense au début du pas :
elle redonne la dépendance, la couverture, la couverture des 65 ans et plus et
le taux d'emploi à 6·10⁻⁵ point près, l'arrondi de l'annexe, à chacune des dix
années publiées. Le résidu est ce que la somme des effets laisse de la
variation ; il porte les produits croisés, négatifs quand la dépendance monte
et que le reste baisse. La prestation et le marché du travail ne se refont
pas : ils se rapportent aux heures et au PIB en niveau, que l'annexe ne publie
pas ; rapportée au salaire moyen (le « benefit ratio » du tableau 10, de 47,1 à
37,3 %), la prestation ferait −3,20 au lieu de −3,40.

**Ce qui est fait.**

- *`src/retraite_notionnelle/facteurs_depense.py`*, à part de `cout.py`, dont il
  lit les sorties sans y toucher : `annees_du_modele` tire de `Cout.avenir` la
  dépense, le PIB, les retraités (`tetes`) et la dépendance de chaque année,
  avec les 20-64 ans de l'INSEE et un indice d'emploi — la masse salariale sur
  le salaire moyen par tête, soit l'emploi salarié des comptes nationaux puis
  la trajectoire d'emploi du COR, celle dont la page fait croître son PIB ;
  `decomposer` chiffre les effets comme l'AWG (`effet`), sur la trajectoire
  PROPRE du modèle (`base_modele`) : celle que la page affiche change de
  périmètre en 2025, de la DREES au COR, et ses têtes ne sont pas celles du
  modèle. Chaque système en tire sa dépense par son rapport de masses
  (`masse_du_scenario`), garantie vieillesse à part, comme la page.
- *Le témoin* `tests/temoins/ageing_report_france.json`, écrit par
  `scripts/fetch/ageing_report.py` depuis l'annexe (feuilles FRa et FRb, par
  `lecture_xlsx.py`, sans dépendance) : vingt-huit séries de 2022 à 2070 et la
  décomposition cumulée. Au manifeste, `ageing_report_france`, sous une
  institution nouvelle, `commission_europeenne` ; au sas, `ageing_report_2024`
  passe à `explore`.
- *Les tests*, `tests/test_facteurs_depense.py` : en suite rapide, la formule
  sur les séries de l'AWG, le témoin et ses identités, l'arithmétique ; en
  contrôle, l'identité sur les six systèmes du modèle — le produit des quatre
  facteurs refait sa part de PIB à 10⁻¹² près —, la confrontation à l'AWG
  (chaque effet de son signe, à moitié près) et la prestation sous la
  productivité haute (à un demi-point près).
- *`scripts/facteurs_depense.py`* imprime la confrontation en Markdown, sous-période
  par sous-période, et les six systèmes (`--systemes`).
- *Le registre* : `ageing_report`, points 1 et 2, repris ; `maquette_globale_cor`,
  point 1, relu et repris — l'action 147 l'avait fait (étapes 2, 5 et 13), sans
  le dire au registre, et son chiffre de 18,24 % en 2070 n'est plus celui du
  modèle (14,84 %).

**Ce que la confrontation montre.** Le système actuel, de 2022 à 2070, en points
de PIB (`python scripts/facteurs_depense.py`) :

| 2022-2070 | Ageing Report 2024 | modèle, productivité 0,7 % | modèle, productivité 1,0 % |
|---|---|---|---|
| Dépense | −0,88 | +1,32 | +0,51 |
| Dépendance | +6,04 | +7,03 | +6,85 |
| Couverture | −2,21 | −1,72 | −1,70 |
| Prestation | −3,40 | −3,03 | −3,67 |
| Marché du travail | −1,05 | −0,72 | −0,71 |
| Résidu | −0,26 | −0,24 | −0,26 |

La dépense du modèle va de 13,52 à 14,84 % du PIB sous la référence du COR,
celle de la page, et à 14,03 % sous sa variante haute ; celle de l'AWG de 14,45
à 13,57 %. Les niveaux ne se comparent pas — l'AWG compte l'invalidité, un
point de PIB, et le minimum vieillesse —, les variations des facteurs si.

- *La dépendance* pousse plus fort dans le modèle : les 65 ans et plus des
  projections de l'INSEE de 2026, rapportés aux 20-64 ans, croissent de 64,7 %
  de 2022 à 2070, ceux d'Eurostat de 2023 de 51,6 %. L'écart naît après 2050
  (+1,20 contre +0,46 de 2050 à 2060, +1,32 contre +0,68 de 2060 à 2070), quand
  arrivent à vingt ans les générations nées après 2030 : la fécondité de
  l'INSEE, 1,45 enfant par femme selon le rapport du COR de juin 2026, est sous
  celle d'Eurostat, 1,8, quand son solde migratoire, +150 000, est au-dessus ;
  l'espérance de vie reste à comparer. Un effet des données, que le modèle ne
  choisit pas.
- *La couverture* recule moins : −12,0 % pour le modèle (1,202 retraité par
  personne de 65 ans et plus, puis 1,058), −14,6 % pour l'AWG (1,412, puis
  1,206). L'écart tient presque entier à 2022-2030 (−0,84 contre −1,38 ; de 2030
  à 2070, −0,88 contre −0,83). Trois causes, à départager : l'AWG fait jouer la
  réforme de 2023 entière, quand le modèle porte sa suspension par la LFSS pour
  2026 (64 ans à la génération 1969 au lieu de 1968 : écart déjà au registre) ;
  chez Destinie, ceux qui partent jusqu'en 2040 ont fini leurs études plus
  tard, et partent plus tard (fiche, § 3.3), quand les carrières types
  commencent au même âge à chaque génération (limite n° 2 de `cout.py`) ; et le
  périmètre, l'AWG comptant les
  pensionnés de réversion seule, d'invalidité et non résidents — 20,3 millions
  en 2022, pour 17,1 millions de retraités au modèle.
- *La prestation* recule de 20,1 % sous la référence du COR, −3,03 points ;
  sous sa variante haute, 1,0 % par an, proche des 1,03 % de l'AWG, de 24,5 %,
  −3,67 points, quand l'AWG fait −3,40. À productivité égale, la mécanique du
  modèle — pensions servies sur les prix, valeur de service de l'Agirc-Arrco
  que le COR projette — retient la dépense comme Destinie, un peu plus. La
  productivité seule déplace l'effet de 0,64 point, et la dépense de 2070 de
  0,8 (14,84 puis 14,03 %) ; à 0,4 %, la variante basse, 15,73 %.
- *Le marché du travail* retient moins : le taux d'emploi des 20-64 ans de
  l'AWG gagne cinq points, de 74,0 à 79,0 %, son chômage descend à 6,3 % ; celui
  du COR reste à 7,0 % à partir de 2040, et son emploi recule de 6 % d'ici 2070.
- *Le résidu*, −0,24 contre −0,26 : celui de la formule, non une erreur.

À productivité proche, l'écart restant, 1,39 point, tient à la dépendance
(+0,81), à la couverture (+0,51) et au marché du travail (+0,34), la prestation
le réduisant (−0,27). Rien n'y désigne une erreur de la mécanique du modèle :
ce sont des hypothèses, sauf la couverture, qui reste à départager.

**Les six systèmes**, sous la référence du COR (`--systemes`), de 2022 à 2070 :

| 2022-2070 | 1. | 2. | 3. | 4. | 5. | 6. |
|---|---|---|---|---|---|---|
| Dépense | +1,32 | +1,21 | −6,71 | +2,02 | −2,78 | −0,09 |
| Dépendance | +7,03 | +1,99 | +5,81 | +4,76 | +6,34 | +4,39 |
| Couverture | −1,72 | −0,45 | −1,58 | −1,09 | −1,61 | −1,04 |
| Prestation | −3,03 | −0,08 | −9,79 | −1,03 | −6,47 | −2,77 |
| Marché du travail | −0,72 | −0,19 | −0,66 | −0,47 | −0,67 | −0,45 |
| Résidu | −0,24 | −0,05 | −0,49 | −0,15 | −0,37 | −0,22 |

La proposition (6) passe de 8,00 à 7,91 % du PIB : sa prestation recule de
28,0 %, et avec la couverture et l'emploi elle compense la dépendance. Elle est
presque insensible à la productivité : 7,91 % en 2070 dans la trajectoire du
modèle sous les trois jeux du COR, 8,12 à 8,18 % sur la page, quand celle du
système actuel va de 14,03 à 15,73 % — ses pensions servies suivent la règle de
son compte, non les prix.
Sa couverture est celle du droit en vigueur : `AvenirAnnuel` ne compte pas à
part les départs que son âge légal de 65 ans reporte, et sa prestation porte
ce que le report change.

**Ce que ça déplace.** Rien : aucun chiffre de page, aucun témoin du site ; un
témoin de plus, celui de l'Ageing Report, que rien ne lit hors des tests.

**Ce qui devrait s'écrire dans les pages**, pour la session qui tient
`pages.js` et `index.html`. Sur la page Coût, près du dépliant des quatre
systèmes, une section « D'où vient la dépense » : le tableau des effets de
2022 à 2070 pour le système actuel et la proposition, et la colonne de
l'Ageing Report, avec ces phrases, chiffres ancrés sur une sonde à écrire :
« L'Ageing Report de 2024 fait baisser la dépense de la France de 0,9 point de
PIB d'ici 2070, quand le COR et le modèle la font monter. La démographie
l'explique d'abord : la population de l'INSEE de 2026 vieillit plus que celle
d'Eurostat de 2023. À productivité égale, les pensions du système actuel
reculent autant dans les deux. » ; et, pour la proposition : « Sa dépense ne
dépend presque pas de la productivité : ses pensions suivent son compte. » Il y
faudrait d'abord la décomposition dans le paquet : `construire_donnees.py` la
figerait dans `data/derive/agregats.json` sous les réglages de référence, lue
par `donnees/agregats.py` et `moteur/js/agregats.js`, comme le reste du coût,
qui ne se calcule qu'en Python.

**Ce qui reste**, de cette partie ; le reste de l'étape 3 est dans la note de la
première.

1. *La couverture de 2022-2030*, à départager entre la suspension de la LFSS
   pour 2026, l'entrée dans l'emploi des carrières types et le périmètre : un
   univers sans la suspension, ou la couverture des seuls 65 ans et plus, le
   diraient.
2. *Les têtes par âge et celles de la proposition*, que `cout.py` exposerait
   dans `AvenirAnnuel` (les moins de 65 ans à part, et les départs que l'âge
   légal de 65 ans reporte) : la couverture se partagerait comme chez l'AWG, et
   la proposition aurait la sienne. À demander à l'action 147, ou après elle.
3. *L'Ageing Report sous la démographie et l'emploi de l'AWG* : la productivité
   est approchée par la variante haute du COR ; EUROPOP2023 et l'emploi de
   l'AWG demanderaient leurs séries en variante de la population et de la
   trajectoire d'emploi.
4. *Le flux des pensions nouvelles* (fiche, tableau 14 ; `ageing_report`,
   point 4) et *la dépense nette* (tableau 7 ; point 6), celle-ci avec la CSG
   effective, le point 3 de la première partie.
5. *La partie 5 ter des limites*, à la fin de l'étape : « Le taux de couverture
   est supposé constant » reste vrai des générations, mais la couverture des
   65 ans et plus recule désormais, mesurée, de 12 % ; et le contrôle externe
   y gagnerait l'Ageing Report à côté du COR. Avec une sonde de
   `mesures_prose.py` pour les effets.
