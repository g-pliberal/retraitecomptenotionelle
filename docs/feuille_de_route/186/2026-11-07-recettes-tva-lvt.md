# Les recettes hors du travail, étudiées aux sources : la TVA sociale et la LVT

**Reprise, au 9 novembre 2026.** Le chantier 4 est tranché (décisions 79
à 81, 105 et 106) et les deux recettes sont au coût du scénario 6 depuis le
9 novembre (`2026-11-09-tva-et-lvt-au-cout.md`) : la part de TVA gardée,
celle de l'Agirc-Arrco seule, 0,36 point de PIB en 2026, en plus des 18 %,
et le point de LVT à sa valeur centrale, 1,31 point. Restent l'abattement et
le plafonnement de la LVT, remis à plus tard, et la suite du plan de
`2026-11-09-recettes-au-modele.md` : la restitution, qui rend encore la
moitié de la TVA gardée (décision 94), et le site, au chantier 9.

*Le 7 novembre 2026, le propriétaire ouvre le chantier 4 de l'action 186 :
« je veux qu'on attaque ce chantier ». La question est celle de
`docs/feuille_de_route_programme.md` : combien rapportent la TVA sociale et
la taxe sur la valeur du terrain (LVT), qui les paie, et en combien de temps
elles se mettent en place. La session a lu les sources, que chaque chiffre
cite, et a fait deux calculs. Le premier passe par le modèle, le second se
fait à côté ; leurs deux scripts sont restés dans son brouillon, hors du
dépôt, et leurs hypothèses sont écrites plus bas. Ce que la note conclut est
une piste, pas une décision : le propriétaire tranche.*

## L'essentiel : la TVA tient tout de suite mais coûte cher, la LVT rapporte plus tard et moins qu'on croit

**Un point de TVA au taux normal rapporte 7,5 Md€ nets en 2025**, et 8,9 Md€
bruts, soit **un quart de point de PIB** (publié, DG Trésor). Les « 8 Md€ » du
programme sont donc le bon ordre de grandeur. Le dépôt retient le net, qui
retranche la TVA que les administrations paient sur leurs propres achats. Le
système de retraite de la proposition, garantie vieillesse comprise, est en
déficit de 1,24 point de PIB en 2026 et de 1,86 au plus bas (variante
rétroactive, modèle). **Il faudrait 4,9 points de taux normal en 2026,
7,4 au pic de 2046, 5,3 en moyenne sur 2026-2070** (modèle) : le taux normal
passerait de 20 % à 25 %, puis à plus de 27 %. Aucun pays de l'Union n'a un
taux aussi haut : la Hongrie, la plus haute, est à 27 %.

Ce besoin dépend pourtant de deux décisions. Dans la proposition, l'État et
la branche famille gardent les versements qu'ils font aujourd'hui aux
retraites, soit 2,26 points de PIB en 2026 : le déficit est celui du
régime, pas celui des finances publiques prises ensemble. Et la
décision 29, prise le même jour, ne fait aller au déficit que la moitié de
la baisse des pensions. Sous ses deux lectures, chiffrées à côté par la
session du chantier 1, les recettes du droit en vigueur restent, et le
besoin fond. La lecture A est en excédent chaque année : la TVA n'a plus de
déficit à combler. La lecture B laisse un déficit de 0,08 point de PIB en
2026 et de 1,19 en 2070, soit 0,3 puis 4,7 points de TVA. La TVA et la LVT
deviennent alors un choix : baisser encore les cotisations. Un point de taux
normal en remplace 0,6 point.

La TVA pèse moins sur les plus de 65 ans que sur les actifs, à consommation
égale. Mais relever le seul taux normal frappe l'énergie, qui y est tout
entière depuis le 1er août 2025.

**La LVT a une assiette plus large que prévu**. Les terrains bâtis valent
7 032 Md€ fin 2025 (publié, Insee, provisoire), dont 6 091 hors
administrations publiques : les 5 800 Md€ du propriétaire étaient ce chiffre
fin 2024. Mais la taxe fait baisser le prix du terrain, et elle remplace une
taxe foncière qui rapporte 42,9 Md€. Le compte se fait capitalisation
comprise, sur un rendement locatif du terrain de 2,5 à 4 %. **À 1 %, la LVT
rapporte 48 à 52 Md€, à peine plus que la taxe foncière : 5 à 9 Md€ de
gain net. À 2 %, elle rapporte 73 à 86 Md€, soit 30 à 43 Md€ nets, 1,0 à
1,4 point de PIB, l'équivalent de 4 à 6 points de TVA** (à côté). Le « 1 %
aux retraites » demande donc un taux de 2 % : à 1 %, les communes perdraient
leur taxe foncière. Le prix du terrain baisse de 30 à 40 % à 2 %, celui d'un
logement de 14 à 19 %.

La LVT a trois obstacles :
- un taux de 2 % fait plus de trois fois le taux effectif moyen du Danemark
  (environ 0,6 %), et deux fois le plafond estonien pour un terrain
  résidentiel (1 %) ;
- le Conseil constitutionnel exige qu'un impôt annuel sur la valeur d'un
  patrimoine soit plafonné au regard du revenu (2012), précisément pour le
  retraité riche en terrain et pauvre en revenus ;
- il faut évaluer chaque parcelle. La France attend depuis 1970 la révision
  de ses valeurs locatives, annoncée pour 2028, et le Danemark a mis plus de
  dix ans à refaire les siennes.

La TVA finance donc les premières années, la LVT ensuite, si elle se fait.

*Lire les chiffres.* Chaque chiffre porte son origine. **(modèle)** est une
sortie du modèle du dépôt au commit `e98667e`. Elle vient de deux sources. La
première est la série annuelle du chiffrage de la proposition,
[`docs/chiffrage_plf.csv`](../../chiffrage_plf.csv), variante rétroactive,
colonne `solde_regime_plus_garantie_pib`. La seconde est le rendement d'un
point de TVA que lit [`donnees/tva.py`](../../../src/retraite_notionnelle/donnees/tva.py)
dans [`assiette_tva.csv`](../../../data/reference/macro/assiette_tva.csv),
tenu en part de PIB comme le reste du dépôt. **(à côté)** est un calcul fait
hors du modèle, sur des données publiées et sous les hypothèses L1 à L5. **(publié)** est un chiffre lu à sa source. Les montants sont en euros
courants.

## La TVA

### Ce que rapporte un point

La DG Trésor publie, pour 2025, ce que rapporterait un point de plus sur
chaque taux. Au taux normal, c'est 8 900 M€ bruts et 7 500 M€ nets, la TVA
que paient les administrations sur leurs propres achats retirée
([Trésor-Éco n° 371, septembre 2025](../../../data/reference/macro/assiette_tva.csv),
recopié au dépôt). Rapporté au PIB de 2025 (2 991 Md€), un point de taux
normal vaut **0,251 point de PIB net** et 0,298 brut. Le dépôt tient cette
part constante (modèle) :

| | 2026 | 2030 | 2040 | 2050 | 2060 | 2070 |
|---|---:|---:|---:|---:|---:|---:|
| Un point de taux normal, Md€ nets | 7,7 | 8,6 | 11,3 | 14,1 | 17,3 | 20,9 |
| Solde du régime, garantie comprise, variante rétroactive, points de PIB | −1,24 | −1,15 | −1,75 | −1,81 | −1,12 | −0,12 |
| Points de taux normal pour le combler | 4,9 | 4,6 | 7,0 | 7,2 | 4,4 | 0,5 |
| Soit, Md€ | 38 | 39 | 79 | 102 | 77 | 10 |

Le pic est en 2046, à 7,4 points ; la moyenne sur 2026-2070 est de 5,3
points. Ce chiffrage est statique, comme le Trésor le dit de ses propres
points : la consommation ne baisse pas quand les prix montent, et la hausse
passe entière dans les prix. Le chiffrage du dépôt dit le reste de ce qu'il
omet (`docs/chiffrage_plf.md`, limite 12). À 25 %, le prix de ce qui est
taxé au taux normal monte de 4,2 % si la hausse passe entière.

Trois réserves fixent la portée de ces points :

- **Le périmètre.** Le fait central de `docs/chiffrage_plf.md` décompose
  l'écart avec le droit actuel en 2026. Les recettes que la proposition
  retire aux retraites valent 5,87 points de PIB, dont 2,26 de versements de
  l'État et de la branche famille, que ceux-ci gardent. Versés au régime, ils
  porteraient son solde de 2026 de −1,24 à +1,02 point, sans aucune TVA
  (calcul sur les chiffres du modèle). Le nombre de points de TVA est donc
  d'abord celui des versements qu'on cesse de faire.
- **Le scénario.** Le chiffrage du commit `e98667e` précède les décisions 16
  à 30. Garder les réversions déjà servies jusqu'à extinction coûte de 0,24
  à 0,30 point de PIB en moyenne (note de la réversion), soit environ un
  point de TVA de plus ; une session du modèle l'a porté au coût du
  scénario 6 le même jour, après ce calcul. La décision 29 change tout le
  reste : voir ci-dessous. Le chantier 5 déplacera encore le solde.
- **La TVA déjà affectée.** La sécurité sociale reçoit déjà plus d'un quart
  de la TVA nette, pour compenser les allègements de cotisations : 28,14 %
  prévus pour 2025, soit 60,5 Md€, d'après l'exposé d'un
  [amendement au PLFSS 2025](https://www.assemblee-nationale.fr/dyn/17/amendements/0325/CION-SOC/AS955.pdf).
  Le Sénat compte 49,6 Md€ exécutés, sur un périmètre que la session n'a pas
  éclairci ([rapport sur le PLFSS 2026](https://www.senat.fr/rap/a25-747/a25-7473.html)).
  Une part en va déjà aux retraites : l'Agirc-Arrco en reçoit, par l'Urssaf,
  de l'ordre de 7 Md€ en 2025 (note des complémentaires, chantier 6).
  Affecter une fraction de TVA aux retraites n'a donc rien de neuf en droit :
  c'est une ligne de loi de finances.

### Sous la décision 29, la TVA ne comble plus un déficit : elle remplace des cotisations

Le même jour, le propriétaire a décidé que la baisse des pensions ne va pas
tout entière au déficit : « on baisse seulement de moitié le déficit »
(décision 29). La session du chantier 1 en chiffre deux lectures, à côté du
modèle, en gardant les recettes du droit en vigueur
(`186/2026-11-07-deux-lectures-et-reprise.md`). La lecture A envoie la
moitié de l'économie au déficit, la lecture B divise le déficit par deux.
Elle déclare elle-même ce calcul à refaire au modèle, la dépense suivant le
taux cotisé ; ses soldes donnent pourtant l'ordre de grandeur :

| | 2026 | 2030 | 2040 | 2050 | 2060 | 2070 |
|---|---:|---:|---:|---:|---:|---:|
| Lecture A : solde, points de PIB | +2,23 | +2,17 | +1,47 | +0,99 | +0,98 | +1,14 |
| Lecture B : solde, points de PIB | −0,08 | −0,10 | −0,30 | −0,61 | −0,88 | −1,19 |
| Points de taux normal pour combler B | 0,3 | 0,4 | 1,2 | 2,4 | 3,5 | 4,7 |

Sous la lecture A, aucune TVA n'est nécessaire à l'équilibre. Sous la
lecture B, il en faut peu au début et presque cinq points en 2070. Dans
les deux cas, le rôle de la TVA et de la LVT change. Elles ne comblent plus
le trou de la transition : elles baissent davantage le prélèvement sur le
travail. C'est la TVA sociale au sens propre, celle de l'Allemagne en 2007.
L'assiette des cotisations de la proposition vaut 42,7 points de PIB en 2026
(note du chantier 1). Un point de taux normal (0,251 point de PIB) y
remplace donc **0,6 point de cotisation**. Une LVT à 2 %, 1,0 à 1,4 point de
PIB nets, en remplacerait 2,3 à 3,4 (calcul sur ces chiffres).

### Qui la paie

**Par le revenu, la TVA est régressive à court terme.** Les 10 % les plus
modestes consacrent 12 % de leur revenu disponible à la TVA, les 10 % les
plus aisés 5 %, parce qu'ils épargnent davantage. L'Insee a simulé trois
points de plus au taux normal, de 20 à 23 %. Trois ans après, le niveau de
vie baisse de 0,6 % en moyenne et de 1,4 % sous le premier décile. Les
salaires suivent les prix avec une élasticité d'environ 75 %, et les
prestations sont revalorisées : à moyen terme, la hausse n'accroît que
légèrement les inégalités. L'Insee suppose qu'elle passe aux prix de 50 à
80 % ([Insee Analyses n° 43, février 2019](https://www.insee.fr/fr/statistiques/3713290)).

**Par l'âge, elle pèse moins sur les retraités que sur les actifs.** Le taux
de prélèvement sur la consommation culmine entre 50 et 54 ans, passe sous la
moyenne à partir de 65 ans et décroît fortement après 70 ans. Les taxes sur
la consommation descendent sous 15 % du revenu à partir de 65 ans (Conseil
des prélèvements obligatoires, 2008, repris par le
[COR en octobre 2009](https://cor-retraites.fr/sites/default/files/2019-06/doc-1237.pdf),
d'après l'enquête Budget de famille 2006). L'Insee en donne la raison : la
consommation liée au travail — vêtements, voiture, repas pris dehors — est
plus taxée, en moyenne, que les biens essentiels, alimentation et soins, qui
pèsent davantage chez les âgés. La TVA payée baisse donc bien plus que la
consommation après la retraite
([Georges-Kot, Insee, document de travail G2015/12](https://www.insee.fr/fr/statistiques/1381136)).
Une hausse du seul taux normal fait donc moins payer les retraités qu'on ne
le croit. Le programme y voyait une recette que tous paient, retraités
compris : ils la paient, mais moins que les actifs à consommation égale —
et toujours plus que la cotisation, qu'ils ne paient pas.

**L'indexation décide du reste.** Une pension indexée sur les prix rend au
retraité la hausse de TVA. Indexée sur la masse salariale (décision 10), elle
ne la lui rend que si les salaires suivent les prix ; l'Insee estime qu'ils
la suivent aux trois quarts. Le chantier 5, sur l'indexation, doit tenir
compte de ce point : sans quoi la TVA sociale reprend d'une main ce que
l'indexation rend de l'autre.

**La piste « le seul taux normal » protège l'alimentation, pas l'énergie.**
L'électricité et le gaz sont taxés à 20 % depuis le 1er août 2025,
abonnement compris : la loi de finances pour 2025 a supprimé le taux réduit
de l'abonnement, et la consommation y était déjà
([CCI Paris Île-de-France](https://www.entreprises.cci-paris-idf.fr/actualites/tva-electricite-et-gaz-passage-de-55-20-au-1er-aout-2025)).
Les carburants le sont aussi. Le taux de 5,5 % couvre l'alimentation, pas
l'énergie : la phrase du programme est à corriger.

### En combien de temps

**Une hausse de TVA se vote et s'applique en quelques mois.** En France, la
« TVA sociale » de 2012 portait le taux normal de 19,6 à 21,2 % pour
financer une baisse de cotisations familiales. Votée le 14 mars 2012 pour le
1er octobre, elle a été abrogée avant d'entrer en vigueur, par la loi de
finances rectificative du 16 août 2012
([Legisocial](https://www.legisocial.fr/actualites-sociales/427-publication-de-la-loi-de-finances-rectificatives-pour-2012-les-consequences-en-paye.html)).
L'Allemagne a porté son taux normal de 16 à 19 % le 1er janvier 2007. Un
point a financé la baisse de la cotisation chômage, de 6,5 à 4,2 %. Une
répercussion entière et immédiate aurait relevé de 2,6 % les prix des biens
touchés. Elle a été partielle et étalée, en partie anticipée
([Bundesbank, rapport mensuel d'avril 2008](https://bundesbank.de/resource/blob/706876/cad53885238935c6ac6a12d62b4587e1/472B63F073F071307366337C94F8C870/2008-04-vat-increase-data.pdf),
lu par son résumé). Les hausses passent davantage aux prix que les baisses
([Benzarti, Carloni, Harju et Kosonen, *Journal of Political Economy*, 2020](https://www.nber.org/papers/w23849)).
Une TVA relevée pour la transition se rabaisserait donc mal ensuite : ses
baisses passent peu aux prix.

La directive européenne fixe un taux normal d'au moins 15 % et aucun maximum
([Commission européenne](https://taxation-customs.ec.europa.eu/taxation/vat/vat-directive/vat-rates_en)) ;
le plus haut de l'Union est celui de la Hongrie, 27 %
([Tax Foundation](https://taxfoundation.org/data/all/eu/value-added-tax-vat-rates-europe/)).

## La LVT

### L'assiette : 6 091 Md€ de terrains privés, qui varient vite

Fin 2024, les terrains bâtis valent **6 729 Md€** : 4 043 aux ménages,
1 596 aux sociétés non financières, 186 aux sociétés financières et 903 aux
administrations publiques. Ils ont baissé de 8,6 % en 2023 et de 2,7 % en
2024, quand le bâti montait ([Insee Première n° 2081, figure 2](https://www.insee.fr/fr/statistiques/8661938)).
Fin 2025, ils valent **7 032 Md€** : 4 190, 1 701, 200 et 941 aux mêmes
secteurs ([Insee, patrimoine national 2025, données provisoires de juillet 2026](https://www.insee.fr/fr/statistiques/2830290)).
Hors administrations, dont les terrains ne paient pas la taxe foncière,
l'assiette est de **5 825 Md€ fin 2024 et de 6 091 Md€ fin 2025**. Les 58 Md€ du propriétaire sont 1 % de la première. Les terres agricoles ne
sont pas publiées à part ; elles sont dans les « autres actifs non
produits ».

Chez les ménages, le terrain fait 46,5 % de la valeur des logements (4 190
contre 4 812 Md€ de bâti) : c'est la part qui varie. Une recette assise sur
le terrain suit ses prix. Elle aurait perdu 11 % de 2022 à 2024.

### La taxe qu'elle remplacerait : 42,9 Md€, assis sur des valeurs de 1970

Les taxes foncières ont rapporté **42,9 Md€** au bloc communal en 2024, dont
26,1 payés par les ménages et 16,8 par les autres agents, surtout les
entreprises ; la taxe sur le bâti fait 41,9 Md€ et celle sur le non-bâti
1,3 Md€ ([Fipeco, 29 septembre 2025](https://fipeco.fr/pdf/Taxes%20fonci%C3%A8res.pdf)).
Depuis 2021, tout va aux communes et à leurs groupements. La taxe foncière y
fait 90 % de la fiscalité directe des communes et 40 % de leurs recettes de
fonctionnement ([DGCL, BIS n° 210](https://www.collectivites-locales.gouv.fr/node/2668)).

Son assiette est la valeur locative cadastrale de 1970, revalorisée d'un
coefficient unique. La révision générale de 1990 a été abandonnée, et celle
des locaux d'habitation, décidée en 2013, est annoncée pour 2028 (Fipeco). La
taxe représente 0,34 % du patrimoine immobilier brut des propriétaires en
moyenne : plus de 0,5 % pour les moins bien dotés, 0,22 % pour le centile le
mieux doté (Insee, décembre 2023, cité par Fipeco). Elle est
anti-redistributive : les biens chers des centres anciens ont de faibles
valeurs cadastrales. Rapportée à l'immobilier privé de 2025 (13 447 Md€,
terrain et bâti), elle en vaut 0,32 % (à côté). Une LVT assise sur la valeur
vénale corrigerait cette injustice.

### Ce qu'elle rapporterait, capitalisation comprise

Une taxe annuelle sur le terrain se capitalise : l'offre de terrain ne bouge
pas, et l'acheteur déduit du prix la taxe qu'il paiera à jamais. Avec un
loyer du terrain R, avant taxe foncière, et un prix P₀ d'aujourd'hui, le
rendement est y = R / P₀. Ce prix contient déjà la taxe foncière actuelle,
τ₀ = 0,32 %. Remplacer τ₀ par une LVT au taux t porte le prix à
P₁ = P₀ × y / (y − τ₀ + t). Le calcul du programme partait d'une taxe nulle ;
celui-ci part de la taxe foncière, déjà dans les prix, et donne un peu plus
(à côté) :

| Rendement locatif du terrain y | LVT | Prix du terrain | Prix d'un logement | Produit, Md€ | Net de la taxe foncière, Md€ |
|---|---|---:|---:|---:|---:|
| 2,5 % | 1 % | −21 % | −10 % | 48 | +5 |
| 3 % | 1 % | −19 % | −9 % | 50 | +7 |
| 4 % | 1 % | −15 % | −7 % | 52 | +9 |
| 2,5 % | 2 % | −40 % | −19 % | 73 | +30 |
| 3 % | 2 % | −36 % | −17 % | 78 | +35 |
| 4 % | 2 % | −30 % | −14 % | 86 | +43 |
| *Sans capitalisation, borne haute* | *1 % ; 2 %* | — | — | *61 ; 122* | *+18 ; +79* |
| *Calcul du programme (y = 3 %, sur 5 800 Md€)* | *1 % ; 2 %* | *−25 % ; −40 %* | — | *44 ; 70* | *≈ 0 ; ≈ +30* |

Les hypothèses du calcul :

| | Contenu |
|---|---|
| L1 | Assiette : les terrains bâtis des ménages et des sociétés fin 2025 (6 091 Md€), en euros de 2025 ; ceux des administrations exonérés ; les terres agricoles hors du calcul, quand la taxe retranchée comprend le non-bâti (1,3 Md€). |
| L2 | Capitalisation complète et immédiate au rendement y ; la valeur du bâti, qui n'est plus taxé, n'est pas recalculée. |
| L3 | Aucun abattement, aucune exonération (logement social, construction neuve), aucun plafonnement, un recouvrement complet. |
| L4 | La taxe foncière retranchée est celle de 2024 (42,9 Md€), en comptabilité nationale. |
| L5 | La part du terrain dans la valeur d'un logement est celle des ménages, 46,5 %. |

**Le « dont 1 % aux retraites » demande une LVT à 2 %.** À 1 %, la LVT
rapporte à peine plus que la taxe foncière ; la verser aux retraites
priverait les communes de 90 % de leur fiscalité directe. À 2 %, sur le
rendement central de 3 %, un point va aux retraites (39 Md€, 1,3 point de
PIB de 2025) et un aux communes. Celles-ci perdraient 4 Md€ sur les 42,9
d'aujourd'hui. L'abattement sur le terrain de la résidence principale, que
le programme envisage, réduit tous ces produits. Il n'est pas chiffré : il
faudrait la valeur du terrain de chaque résidence principale, que ni l'Insee
ni la DGFiP ne publient.

Rapporté au besoin de la proposition, le gain net d'une LVT à 2 %, 30 à 43
Md€, vaut 4,0 à 5,7 points de TVA normale (à côté) : à peu près le besoin de
2026, et de la moitié aux trois quarts de celui de 2046.

### Qui la paie

**Le propriétaire du jour de l'annonce, une fois pour toutes.** La taxe fait
baisser le prix du terrain dès qu'on l'annonce. L'acheteur suivant paie un
prix plus bas et la taxe, ce qui revient au même pour lui. Høj, Jørgensen et
Schou trouvent une capitalisation complète au Danemark, en exploitant les
écarts de taux nés des fusions de communes de 2007
([*Fiscal Studies*, 2018](https://ideas.repec.org/a/wly/fistud/v39y2018i2p365-380.html)) ;
le taux d'actualisation implicite y est d'environ 2,3 %. Un document de
travail de 2024, sur la même expérience, ne trouverait aucun effet sur les
prix ([Nielsson, Wroblewski et Yding](https://ckwroblewski.github.io/research/LVT_draft.pdf),
lu par un résumé secondaire). La théorie et l'étude publiée vont dans le sens
du tableau ; le débat empirique reste ouvert.

Cela sert le diagnostic du programme. La LVT reprend aux propriétaires
d'aujourd'hui, souvent âgés, une part de la rente foncière, et rend aux
acheteurs de demain des terrains moins chers. En 2021, 70 % des ménages de
60 à 69 ans et 73 % de ceux de 70 ans ou plus possèdent un bien immobilier,
contre 20 % des moins de 30 ans (Insee, enquête Histoire de vie et
Patrimoine 2021, repris par
[Moneyvox](https://www.moneyvox.fr/immobilier/actualites/88278/etes-vous-devenu-proprietaire-plus-tot-que-la-moyenne)).
Mais l'acheteur récent, endetté, perd le plus : une baisse de 14 à 19 % du
prix de son logement peut dépasser son apport. Et la baisse des prix réduit
d'autant les droits de mutation des départements.

### Le droit

- **Le plafonnement.** Le Conseil constitutionnel juge qu'un impôt annuel du
  type de l'ISF d'avant 2012 ne peut s'établir « sans l'assortir d'un
  dispositif de plafonnement ou produisant des effets équivalents destinés à
  éviter une rupture caractérisée de l'égalité devant les charges publiques »
  ([décision 2012-654 DC du 9 août 2012](https://www.conseil-constitutionnel.fr/decision/2012/2012654DC.htm),
  citée par ses commentateurs, à relire au texte). La loi de finances pour
  2013 en a tiré un plafonnement de l'ISF à 75 % des revenus. Une LVT de 1
  à 2 % de la valeur du terrain, sans égard au revenu, s'expose au même
  grief, pour le retraité riche en terrain et pauvre en revenus. Le
  programme exclut le paiement différé jusqu'à la vente ou la succession
  (décision 5). Reste un plafonnement au revenu, comme celui qui borne déjà
  la taxe foncière de la résidence principale des ménages modestes. Il est
  à relire, comme les exonérations des plus de 75 ans et le dégrèvement des
  65 à 75 ans (articles 1390, 1391, 1391 B et 1391 B ter du code général des
  impôts, de mémoire).
- **L'autonomie des communes.** La taxe foncière est une ressource propre
  des communes, et la Constitution veut que ces ressources restent une
  « part déterminante » de leurs ressources (article 72-2). En prendre la
  moitié pour les retraites demande de leur laisser l'autre (à étudier).
- **L'affectation.** Une fraction d'un impôt d'État se verse à la sécurité
  sociale par la loi de finances, comme la TVA aujourd'hui. Une LVT
  nationale, assise par l'État et partagée, serait une construction neuve.

### Les pays qui taxent le terrain

- **Le Danemark** taxe le terrain seul (la *grundskyld*), au taux de chaque
  commune. Après la réforme de 2024, le taux moyen est tombé de 27 à 7,4
  pour mille : les nouvelles évaluations sont bien plus hautes, et chaque
  commune garde la même recette. La taxe ne porte que sur 80 % de la valeur,
  soit environ 0,6 % de taux effectif, de 3,3 pour mille à Frederiksberg à
  17,7 à Varde ([lex.dk, *grundskyld*](https://lex.dk/grundskyld)). Après
  le rapport sévère de sa Cour des comptes sur les évaluations, en 2013
  ([Rigsrevisionen](https://www.uk.rigsrevisionen.dk/audits-reports-archive/2013/aug/report-on-the-public-property-assessment)),
  le Danemark a refait tout son système d'évaluation. Estimé à 200 M DKK en
  2014, il en coûtait 1,2 Md en 2016 ([Altinget](https://www.altinget.dk/artikel/her-er-kritikken-af-ejendomsvurderingerne)).
  Les nouvelles évaluations n'ont servi qu'à partir de l'impôt de 2024
  (lex.dk), et les suivantes sont encore repoussées en 2026
  ([The Local, juin 2026](https://www.thelocal.dk/20260616/explained-why-is-denmark-delaying-new-property-valuations-once-again)).
- **L'Estonie** taxe le terrain seul, sur l'évaluation générale de 2022. En
  2025, le taux est compris entre 0,1 et 1 % pour un terrain résidentiel, et
  entre 0,1 et 2 % pour les autres. Chaque commune fixe un abattement sur le
  terrain du logement, jusqu'à 1 000 € de taxe, et une limite à la hausse
  annuelle, de 10 à 100 % ([administration fiscale estonienne, janvier 2025](https://emta.ee/en/news/land-tax-subject-several-changes-year) ;
  [ERR, décembre 2025](https://news.err.ee/1609890121/land-tax-to-go-up-for-many-in-2026)).
  Le saut des valeurs de 2022 a dû être amorti par ces limites, et 51 des 79
  communes ont choisi la plus basse, 10 %.
- **Le Territoire de la capitale australienne (Canberra)** remplace depuis
  2012, en vingt ans, les droits de mutation par une taxe locale assise sur
  la valeur du terrain ([Trésor de l'ACT](https://www.treasury.act.gov.au/taxreform)).
  C'est le modèle d'une transition lente. Le gouvernement la dit neutre pour
  les recettes ; ses critiques disent le contraire
  ([bilan de 2019](https://www.treasury.act.gov.au/budget/budget-2019-20/budget-papers/act-tax-reform-program-on-track)).

Aucun des deux pays européens qui taxent le terrain seul n'approche 2 % pour
un logement : une LVT française à 2 % serait sans précédent connu de la
session.

### En combien de temps

Il faut d'abord la valeur du terrain de chaque parcelle, séparée de celle du
bâti. La France n'a ni l'une ni l'autre. Elle a les prix des ventes (DVF),
mais ses bases fiscales datent de 1970, et la révision des seules valeurs
locatives d'habitation, prévue dès 2013, n'est pas faite en 2026. Le
Danemark a mis plus de dix ans à refaire ses évaluations, de 2013 à l'impôt
de 2024. L'Estonie a dû amortir le saut de ses valeurs de 2022. Compter plusieurs années est prudent.
La LVT ne peut pas financer les premières années de la transition : la TVA,
si.

## La piste, qui n'est pas une décision

**L'architecture du 6 novembre tient** : la TVA d'abord, la LVT ensuite. Les
chiffres en changent l'échelle :

1. **La TVA de transition** se vote dans l'année, et chaque point de taux
   normal rapporte un quart de point de PIB. Le scénario 6 tel que le dépôt
   le chiffre en demande de 5 à 7,4 points : un taux normal de 25 à 27,4 %.
   Mais deux choix passent avant elle. Le premier est la lecture de la
   décision 29 : sous A, aucun déficit à combler ; sous B, peu au début. Le
   second est le sort des 2,26 points de PIB que l'État et la branche
   famille cessent de verser, qui, gardés au régime, allègent d'autant la
   TVA. Une fois ces deux choix faits, la TVA sert surtout à baisser encore
   les cotisations, à raison de 0,6 point par point de TVA.
2. **Le seul taux normal** épargne l'alimentation, pas l'énergie. Il pèse
   moins sur les plus de 65 ans que sur les actifs : la « fraternité » y
   joue moins que prévu.
3. **La LVT** n'a de sens pour les retraites qu'à 2 %, avec un point aux
   communes : 30 à 43 Md€ nets, avant l'abattement de la résidence
   principale, que rien ne permet encore de chiffrer. C'est plus de trois
   fois le taux effectif danois. Elle demande un plafonnement au revenu, des années
   d'évaluation, et elle frappe en une fois les propriétaires du jour. Une
   LVT à 1 %, neutre pour les recettes, remplacerait une taxe foncière
   injuste par une taxe juste : c'est une réforme du logement, pas une
   recette des retraites.
4. **La TVA pourrait reculer quand la LVT monte**, comme à Canberra, à
   ceci près que les baisses de TVA passent mal dans les prix. Mieux vaut
   donc une TVA de transition votée avec sa date de baisse.

## Ce que le propriétaire a à trancher

- Le sort des versements de l'État et de la branche famille (2,26 points de
  PIB en 2026) : gardés au régime, ou rendus à leurs payeurs, et alors
  remplacés par la TVA.
- Le rôle de la TVA, une fois la décision 29 lue : combler le déficit
  qu'elle laisse (lecture B), ou baisser encore les cotisations (0,6 point
  par point de TVA) ; sur le seul taux normal, sachant que l'énergie y est ;
  combien de points ; une date de baisse votée avec elle.
- La LVT : à 1 % (réforme du logement, neutre pour les recettes) ou à 2 %
  (un point aux retraites) ; son abattement ; son plafonnement au revenu.

## Ce qui reste à faire

- Recalculer le besoin de TVA quand les décisions 16 à 30 seront au modèle,
  la lecture de la 29 refaite au modèle (une session du modèle), et à chaque
  chantier qui déplace le solde.
- Chiffrer l'abattement de la résidence principale. Il faudrait la valeur du
  terrain par résidence principale, que l'enquête Histoire de vie et
  Patrimoine ou les fichiers fonciers (Cerema) approcheraient.
- La part de la TVA payée par les ménages retraités, par l'enquête Budget de
  famille 2017, et non plus par les taux de 2006.
- Relire aux textes : la décision 2012-654 DC ; les articles 1390 à 1391 B
  ter du code général des impôts ; l'article 72-2 de la Constitution ; le
  montant exécuté de la TVA affectée à la sécurité sociale en 2025.
- Les pays : les taux et le plafond légal danois sur une source officielle,
  que la session n'a pu joindre (skat.dk, vurderingsstyrelsen.dk).

## Ce que le propriétaire a tranché

Le même jour, à la lecture de la note : « on laisse la TVA à 20% et on
officialise la part affectée aux retraites » ; « pour la LVT, on met 2% et
on dédit 1% aux retraites ». Ce sont les décisions 79 et 80 de
`docs/feuille_de_route_programme.md`.

- **La TVA ne monte pas.** La TVA de transition et la TVA qui baisserait
  les cotisations sont écartées. La fraction qui va déjà aux retraites leur
  est affectée en titre : celle de l'Agirc-Arrco, de l'ordre de 7 Md€ en
  2025 (décision 47), et la part de la Cnav dans la fraction de la sécurité
  sociale, à chiffrer. Ce que le dépôt en comprend, à confirmer : la
  proposition la garde, au lieu de la retirer avec les autres impôts
  affectés.
- **La LVT est à 2 %, un point aux retraites, un aux communes.** Sur le
  calcul de cette note, les retraites en reçoivent 36 à 43 Md€ par an (1,2 à
  1,4 point de PIB de 2025), avant tout abattement. Les communes reçoivent
  autant, contre 42,9 Md€ de taxe foncière en 2024. Les prix des terrains
  baissent de 30 à 40 %, ceux des logements de 14 à 19 %.
- **Ce qui en suit pour la transition.** La LVT attend l'évaluation des
  terrains, plusieurs années, et la TVA ne monte pas : les premières années
  n'ont pas de recette nouvelle. Leur équilibre repose sur la lecture de la
  décision 29 et sur le sort des versements de l'État et de la branche
  famille, que le propriétaire n'a pas encore tranché.
- **Restent ouverts** l'abattement de la résidence principale, le
  plafonnement au revenu, l'année d'entrée en vigueur de la LVT, et le
  montant de la part de TVA officialisée.

Puis, à la lecture des décisions 79 et 80 : « oui c'est ça, on garde la
part existante pour les retraites » ; « ne t'inquiète pas pour la LVT, en
quelques mois, on aura fait ça. On sait beaucoup mieux gérer ce genre de
chose de nos jours ». La lecture de la décision 79 est confirmée, et la LVT
entre en vigueur dans les mois qui suivent le vote (décision 81). Les
premières années ont donc une recette nouvelle, le point de LVT des
retraites, 36 à 43 Md€ par an sur le calcul de cette note, et l'année
d'entrée en vigueur n'est plus ouverte. Ce que cette note disait des délais
danois et français reste vrai à sa date ; le risque d'une évaluation
contestée ou plus longue est à suivre au chantier 7.

Enfin, le soir : « pour les recettes, je crois que c'est déjà répondu pour
les versements de l'Etat et la branche famille » ; « pour les détails de la
LVT, on verra plus tard ». La réponse est au chantier 1
(`2026-11-07-deux-lectures-au-modele.md`, sur la base de la page Coût) :
l'État garde les 58 Md€ qu'il ne verse plus, et les impôts affectés suivent
le partage du 20 septembre, moitié aux salaires, moitié à la dette, sauf la
part de TVA des retraites que la décision 79 leur garde. Le besoin de TVA
que cette note chiffrait, en gardant ces versements hors du régime, n'a
plus d'objet : la TVA ne monte pas. L'abattement et le plafonnement de la
LVT attendent.
