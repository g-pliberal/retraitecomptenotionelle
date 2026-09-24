# Méthodologie

Ce document décrit ce que le modèle calcule, et pourquoi il le calcule ainsi.
Chaque décision contestable y est nommée, justifiée, et rattachée au paramètre
qui permet d'en changer.

---

## 1. Ce qu'est un compte notionnel

Un compte notionnel est un compte **virtuel**. Aucun capital n'est placé : les
cotisations de l'année financent les pensions de l'année, comme dans toute
répartition. Ce qui change, c'est la façon de calculer le droit.

Pour chaque assuré :

1. **Accumulation** — chaque année, la cotisation retraite effectivement versée
   est inscrite au compte ;
2. **Revalorisation** — le solde est revalorisé chaque année à un taux
   d'indexation défini par la règle collective ;
3. **Liquidation** — la pension annuelle vaut

   ```
   pension = capital notionnel / coefficient de conversion
   ```

Le coefficient de conversion est l'espérance de vie résiduelle à l'âge de
liquidation, lue sur une table de génération.

Trois propriétés en découlent, et ce sont elles qui répondent au cahier des
charges :

- **la pension est strictement proportionnelle aux cotisations** — aucun effet
  de seuil, aucun palier, aucun minimum ;
- **partir plus tôt coûte deux fois** — moins de cotisations accumulées, et une
  rente à servir plus longtemps ;
- **rien n'est gratuit** — un droit non financé par une cotisation n'existe pas.

---

## 2. Périmètre temporel

L'origine par défaut est **1941**, date de l'allocation aux vieux travailleurs
salariés : premier dispositif français où les cotisations des actifs financent
directement les prestations des retraités. Le paramètre
`annee_debut_repartition` accepte 1945 (ordonnances créant la Sécurité sociale)
pour qui préfère cette borne.

Les régimes antérieurs figurent au catalogue mais sont traités à part :

- les **assurances sociales de 1930** étaient en capitalisation individuelle —
  leur ruine par l'inflation des années 1940 est précisément ce qui a motivé le
  passage à la répartition. Elles sont marquées `hors_repartition` ;
- les **pensions civiles de 1853** étaient versées sur crédits budgétaires
  courants, donc fonctionnellement en répartition : elles sont incluses.

---

## 3. L'indexation

### La règle par défaut, et la règle demandée

Le modèle revalorise les comptes, par défaut, sur la **croissance de la masse
salariale** : l'assiette des cotisations, donc le rendement qu'un système en
répartition peut servir sans changer son taux de cotisation. C'est la règle que
la théorie des comptes notionnels désigne, et la section « La règle d'équilibre »
plus bas la détaille.

```
taux d'indexation (défaut) = croissance nominale de la masse salariale
```

Ce n'est pas la règle qui a motivé ce dépôt. Celle-là est le **triple lock
inversé** — `indexation=triple_lock_inverse` —, et c'est elle que décrit tout
le reste de cette section, parce que c'est elle qui pose les questions de
méthode les plus difficiles :

```
taux d'indexation = min( inflation , croissance du salaire moyen , productivité réelle )
```

Pourquoi ce n'est pas elle le défaut : un défaut est ce qu'on retient faute
d'instruction contraire, pas ce qu'on cherche à démontrer. La règle demandée est
une proposition, et une proposition se compare à un point de référence qu'elle
n'a pas choisi.

La règle d'indexation, quelle qu'elle soit, s'applique à la revalorisation des **comptes en cours de constitution**,
depuis 1941. Elle ne s'applique pas aux pensions déjà liquidées — non par
choix, mais parce que le modèle n'a pas de phase postérieure à la liquidation :
il calcule une pension à la date de départ, dans les euros de cette année-là,
et s'arrête. Les cinq scénarios sont donc lus au même instant, ce qui les rend
comparables ; ce que la règle ferait aux pensions servies reste hors du modèle,
et `docs/limites.md` le dit. Un paramètre `indexer_pensions_liquidees` figurait
en tête de la configuration et laissait croire le contraire : il n'était lu
nulle part, et il a été retiré.

Une convention à connaître, parce qu'elle vaut un pour cent : une cotisation
versée l'année *t* est revalorisée de *t*+1 **jusqu'à l'année de liquidation
incluse**. Le compte est arrêté à la fin de l'année de départ, pas à son début.
La docstring de `Indexation.coefficient` annonçait l'inverse alors que le code
a toujours fait ainsi ; c'est le texte qui a été corrigé.

### Ce qu'elle produit, et pourquoi il faut le savoir

Deux des trois termes sont nominaux, le troisième est réel. Dès que l'inflation
dépasse la croissance de la productivité — c'est-à-dire pendant la quasi-totalité
de la période 1945-1985 — c'est la productivité réelle qui l'emporte, et le
compte suit de très loin : revalorisé de <!--chiffre:mesure(taux_indexation?regle=triple_lock_inverse&annee=1946)-->14,0<!--/--> % en 1946 quand les prix
montent de <!--chiffre:mesure(taux_indexation?regle=prix&annee=1946)-->51,9<!--/--> %, de <!--chiffre:mesure(taux_indexation?regle=triple_lock_inverse&annee=1981)-->1,3<!--/--> % en 1981 quand ils montent de
<!--chiffre:mesure(taux_indexation?regle=prix&annee=1981)-->13,4<!--/--> %.

Mesure sur la période complète, 1941-2025 :

<!-- indexation:debut -->
| Règle | Revalorisation cumulée 1941-2025 | Prix | Pouvoir d'achat conservé |
|---|---|---|---|
| Triple lock inversé, littéral | ×4,9 | ×322,2 | **1,5 %** |
| Moyenne des trois taux | ×175,7 | ×322,2 | 54,5 % |
| Triple lock inversé, tout en nominal | ×223,3 | ×322,2 | 69,3 % |
| Indexation sur les prix | ×322,2 | ×322,2 | 100,0 % |
| Médiane des trois taux | ×397,6 | ×322,2 | 123,4 % |
| Revalorisation réellement pratiquée | ×1 538,2 | ×322,2 | 477,4 % |
| Masse salariale (règle d'équilibre) | ×3 685,1 | ×322,2 | 1 143,7 % |
| PIB nominal | ×3 442,3 | ×322,2 | 1 068,3 % |
| PIB nominal lissé sur 5 ans (Italie) | ×4 152,7 | ×322,2 | 1 288,8 % |
<!-- indexation:fin -->

Ces chiffres sont ceux que produit la commande citée ci-dessus, et le
tableau les a longtemps donnés périmés — ×243,7 et ×318,6, valeurs d'une
révision antérieure des séries INSEE, quand le README, lui, portait les bonnes.
Deux documents ne peuvent pas dire deux chiffres pour la même mesure : c'est le
genre d'écart qu'un lecteur ne peut pas arbitrer.

Autrement dit, sous la règle littérale, **une cotisation versée en 1950 ne vaut
presque plus rien à la liquidation**. Le scénario rétroactif mesure alors
davantage l'effet de la règle d'indexation que celui du passage aux comptes
notionnels.

C'est un résultat, pas un défaut : la règle a été appliquée telle qu'énoncée.
Mais l'interprétation doit en tenir compte. Deux moyens de faire la part des
choses :

- `indexation=triple_lock_inverse_nominal` ramène la productivité en termes
  nominaux avant de prendre le minimum : la règle reste austère, mais homogène ;
- `indexation=revalorisation_portee_au_compte` isole l'effet propre des
  comptes notionnels, indexation neutralisée.

### La seule ligne qui ne soit pas une hypothèse

Ce paragraphe désignait `indexation=prix` comme la règle neutralisant
l'indexation. C'était une erreur, et elle valait un facteur cinq. Le régime
général ne revalorise les salaires portés au compte sur les prix que **depuis
1987** : avant, les arrêtés annuels suivaient les salaires. Le coefficient
réellement appliqué vaut ×<!--chiffre:mesure(cumul_indexation?regle=revalorisation_portee_au_compte&de=1940&a=2025)-->1 538<!--/--> sur 1941-2025, contre ×<!--chiffre:mesure(cumul_indexation?regle=prix&de=1940&a=2025)-->322,2<!--/--> pour les prix.
Comparer le compte notionnel à une indexation sur les prix ne le comparait donc
pas au droit positif ; cela lui opposait une troisième règle, jamais appliquée,
et imputait aux comptes notionnels un écart qui venait encore de l'indexation.

Le mode `revalorisation_portee_au_compte` sert les coefficients des arrêtés
eux-mêmes (`data/reference/legislation/revalorisation_salaires.csv`), par le
rapport de deux années consécutives dans la colonne publiée — exactement la
grandeur dont le scénario 1 se sert pour revaloriser les salaires de son salaire
de référence. Hors de la plage publiée, il retombe sur l'approximation légale :
les salaires jusqu'en 1986, les prix depuis. La question qu'il pose est la seule
qui ne suppose rien : **et si le compte notionnel avait rapporté exactement ce
que le droit en vigueur a accordé ?**

Ce que la correction déplace est modeste, et le dire fait partie de la
correction : les cotisations se concentrent sur les dernières années d'une
carrière, où les deux règles coïncident. La ligne de référence du scénario
rétroactif passe de <!--chiffre:mesure(ecart?scenario=2&generation=1920&indexation=prix)-->-91,2<!--/--> % à <!--chiffre:mesure(ecart?scenario=2&generation=1920&indexation=revalorisation_portee_au_compte)-->-86,2<!--/--> % pour la génération 1920, de
<!--chiffre:mesure(ecart?scenario=2&generation=1930&indexation=prix)-->-89,3<!--/--> % à <!--chiffre:mesure(ecart?scenario=2&generation=1930&indexation=revalorisation_portee_au_compte)-->-87,5<!--/--> % pour 1930, ne bouge pas pour 1945
(<!--chiffre:mesure(ecart?scenario=2&generation=1945&indexation=prix)-->-84,8<!--/--> % contre <!--chiffre:mesure(ecart?scenario=2&generation=1945&indexation=revalorisation_portee_au_compte)-->-84,8<!--/--> %), et l'écart s'inverse pour
les carrières entièrement postérieures à 1987 (<!--chiffre:mesure(ecart?scenario=2&generation=1958&indexation=prix)-->-80,5<!--/--> % à <!--chiffre:mesure(ecart?scenario=2&generation=1958&indexation=revalorisation_portee_au_compte)-->-81,0<!--/--> % pour
1958) : depuis 1990, les arrêtés revalorisent un peu moins vite que les prix
(×<!--chiffre:mesure(cumul_indexation?regle=revalorisation_portee_au_compte&de=1990&a=2025)-->1,69<!--/--> contre ×<!--chiffre:mesure(cumul_indexation?regle=prix&de=1990&a=2025)-->1,79<!--/-->), l'indexation légale étant assise sur l'inflation de l'année
précédente. Le facteur cinq est celui de l'indice cumulé sur 1941-2025, pas
celui du résultat.

Une réserve de composition : le modèle compose ce mode année par année, comme
tous les autres, alors que la caisse arrondit ses colonnes à trois décimales. Le
produit des taux annuels s'écarte de <!--chiffre:mesure(composition_revalorisation?de=1940&a=2025)-->0,04<!--/--> % du coefficient lu directement de
bout en bout sur 1941-2025. C'est le prix de l'uniformité du moteur, et c'est
deux ordres de grandeur sous les écarts que ce mode sert à mesurer.

### Changer de statistique : médiane et moyenne

Le minimum est une statistique parmi d'autres. Deux variantes gardent les
**mêmes trois termes** — mêmes séries, même mélange nominal/réel — et ne
changent que ce qu'on en retient :

```
mediane_trois_taux :  médiane( inflation , salaire moyen , productivité réelle )
moyenne_trois_taux :  moyenne( inflation , salaire moyen , productivité réelle )
```

L'écart avec la règle littérale mesure alors exactement ce que coûte le choix du
minimum, à termes inchangés. Ce que les données disent, sur 1941-2025 :

- la **médiane** est l'inflation 43 années sur 85 et le salaire moyen 20 :
  autrement dit, un taux nominal dans trois cas sur quatre. Elle ne passe sous
  l'inflation que 18 années sur 85, contre 61 pour le minimum, et son cumul
  dépasse celui des prix (×<!--chiffre:mesure(cumul_indexation?regle=mediane_trois_taux&de=1940&a=2025)-->397,6<!--/--> contre ×<!--chiffre:mesure(cumul_indexation?regle=prix&de=1940&a=2025)-->322,2<!--/-->) parce que le salaire moyen
  l'emporte quand la productivité est forte. **La médiane n'est plus une règle
  d'austérité** : c'est en pratique une indexation intermédiaire entre prix et
  salaires, dont le taux reste un taux observé — propriété que le minimum a
  aussi, et que la moyenne n'a pas ;
- la **moyenne** est plus sévère que la médiane, et même que les prix
  (×<!--chiffre:mesure(cumul_indexation?regle=moyenne_trois_taux&de=1940&a=2025)-->175,7<!--/-->, soit <!--chiffre:mesure(conserve?regle=moyenne_trois_taux)-->54,5<!--/--> % du pouvoir d'achat). Non parce qu'elle serait « au milieu », mais
  parce qu'elle incorpore **un tiers de productivité réelle chaque année**, y
  compris pendant les années à dix ou vingt points d'inflation, là où le minimum
  et la médiane ne retiennent le terme réel que les années où il gagne. Sa
  sévérité est donc un effet du mélange nominal/réel, pas un choix assumé — et
  le taux qu'elle produit n'est celui d'aucun agrégat publié. C'est la variante
  la plus fragile des trois sur le plan économique ; elle est fournie pour être
  mesurée, pas recommandée.

### La règle d'équilibre : la masse salariale

Toutes les règles ci-dessus sont des choix ; celle-ci découle d'un argument. En
répartition, le taux de rendement interne soutenable est la croissance de
l'assiette des cotisations — la masse salariale, soit le salaire moyen
multiplié par l'emploi salarié (Samuelson 1958, Aaron 1966). C'est le seul taux
qui laisse le système en équilibre sans toucher au taux de cotisation, et c'est
donc celui que la théorie des comptes notionnels désigne pour revaloriser les
comptes. Les systèmes notionnels réels s'en approchent : indice de revenu par
tête en Suède, PIB nominal lissé sur cinq ans en Italie, masse salariale
d'assiette en Pologne et en Lettonie.

`indexation=masse_salariale` la sert depuis les salaires et traitements bruts
du total des branches (D11, comptes nationaux base 2020, idbank 011785411),
pris **en niveau** et non par tête : `data/reference/macro/masse_salariale.csv`,
certifié de 1950 à 2025 par `scripts/verifier_donnees.py`. Les vingt années
1930-1949 sont estimées — les comptes nationaux ne remontent pas plus haut, et
aucune série d'emploi salarié ne couvre la guerre : elles reprennent la
variation du salaire moyen, c'est-à-dire supposent l'emploi salarié constant.
Au-delà de 2025, la projection reconduit le salaire moyen nominal, l'emploi
salarié étant supposé constant : le COR ne publie pas d'hypothèse d'emploi long
terme dont on puisse se réclamer, et ses hypothèses de population active ont
changé deux fois en deux ans.

Sur 1941-2025 la règle vaut ×3 685, onze fois les prix : l'emploi salarié a été
multiplié par 2,14 depuis 1950, et cette croissance s'ajoute chaque année à
celle des salaires. C'est de loin la plus généreuse des règles disponibles.

Une incohérence de périmètre, qu'il faut connaître : ce taux est le rendement du
système **entier**, alors que les scénarios 2 et 3 ne portent au compte que la
part salariale de la cotisation. Adosser un rendement collectif à une cotisation
partielle mélange deux périmètres ; les scénarios 4 et 5, qui portent la
cotisation entière, sont ceux auxquels cette règle se compare sans biais.

### L'assiette la plus large : le PIB nominal

`indexation=pib_nominal` sert le PIB approche produit en prix courants
(idbank 011779992, `data/reference/macro/pib_nominal.csv`, certifié 1950-2025 ;
1930-1949 estimé selon la même convention que la masse salariale). Son intérêt
sur la masse salariale : l'assiette capte le déplacement de la valeur ajoutée
vers les revenus non salariaux, que la masse salariale, elle, subit. Son cumul
sur 1941-2025 vaut ×3 442,3, un peu en dessous de la masse salariale.

### Le lissage pluriannuel, qui n'est pas une règle

`lissage=N` (paramètre `lissage_indexation`) applique une moyenne géométrique
glissante de N années au taux que la règle produit — **n'importe laquelle des
neuf**. C'est un réglage orthogonal, et non une dixième règle : il ne change pas
ce qu'on mesure, il change la façon dont une année isolée se répercute.

Ce qu'il vise est la **loterie de cohorte**. Une cotisation de 1980 vaut, à la
liquidation, ×5,44 en 2019 et ×5,18 en 2020 : sur le PIB nominal brut, attendre
un an fait *perdre*, parce que l'année traversée s'est mal passée. Sur
1950-2025, deux années sont dans ce cas ; lissées sur trois ou cinq ans, plus
aucune (×6,64 puis ×6,71 pour les deux mêmes liquidations). Rien dans la
carrière ne justifiait l'écart : c'est le calendrier qui tranchait, et le
lissage lui retire ce pouvoir.

L'ordre des opérations compte, et il est fixé dans `Indexation.taux` :

1. la **règle** produit le taux de l'année ;
2. le **lissage** en prend la moyenne géométrique sur la fenêtre ;
3. le **plancher**, s'il y en a un, s'applique au résultat — un plancher qu'une
   moyenne pourrait repasser sous le seuil ne serait pas un plancher.

La fenêtre se saisit librement dans le formulaire : n'importe quel entier de
1 à <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=LISSAGE_MAXIMUM)-->30<!--/--> ans. La borne haute n'est pas une limite du
moteur mais un garde-fou de sens — au-delà d'une trentaine d'années la moyenne
couvre presque toute une carrière, tous les millésimes reçoivent à peu près le
même taux, et ce n'est plus un lissage mais un taux fixe reconstitué.

La fenêtre est tronquée au début des séries plutôt qu'indisponible : en deçà de
la première année publiée, `SerieAnnuelle` répète sa première valeur, et une
moyenne glissante qui l'avalerait ferait passer une extrapolation pour une
observation.

**La règle italienne s'écrit donc `indexation=pib_nominal&lissage=5`** —
c'est exactement ce que l'Italie applique à ses comptes notionnels. Le modèle
n'en reprend que le taux : ni le décalage de publication de deux ans, ni les
coefficients de transformation, ni les planchers.

Une réserve, à connaître avant de lire un cumul lissé : sur quatre-vingts ans,
une moyenne glissante n'est pas neutre. Le produit des moyennes glissantes
revient à mesurer la croissance depuis une base reculée d'environ la moitié de
la fenêtre, ce qui gonfle le coefficient d'une vingtaine de pour cent à cinq ans
— sans qu'aucune série ait changé. C'est ce qui fait passer le PIB nominal de
×<!--chiffre:mesure(cumul_indexation?regle=pib_nominal&de=1940&a=2025)-->3 442,3<!--/--> à ×<!--chiffre:mesure(cumul_indexation?regle=pib_nominal&lissage=5&de=1940&a=2025)-->4 152,7<!--/--> dans le tableau plus haut, alors qu'il croît *moins* vite
que la masse salariale (×<!--chiffre:mesure(cumul_indexation?regle=masse_salariale&de=1940&a=2025)-->3 685,1<!--/-->). Sur une carrière, l'écart entre lissé et non
lissé retombe à un ou deux points : règle par défaut, génération 1930,
<!--chiffre:mesure(ecart?scenario=2&generation=1930)-->-83,8<!--/--> % sans lissage, <!--chiffre:mesure(ecart?scenario=2&generation=1930&lissage=3)-->-82,7<!--/--> % à trois ans, <!--chiffre:mesure(ecart?scenario=2&generation=1930&lissage=5)-->-81,8<!--/--> % à cinq.

Aucun plancher n'est appliqué par défaut : le taux peut être négatif, ce qui est
la conséquence logique de la règle (`plancher_indexation`).

### Au-delà de 2025

Les séries observées s'arrêtent en 2025. Geler la dernière valeur serait une
hypothèse implicite et fausse. Le modèle projette donc explicitement, selon le
jeu de scénarios du Conseil d'orientation des retraites
(`data/reference/macro/hypotheses_projection.yaml`) : inflation <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> % et
productivité réelle **<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.productivite_reelle*100)-->0,7<!--/--> %** dans le scénario de référence, **<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_basse.productivite_reelle*100)-->0,4<!--/--> %** et
**<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_haute.productivite_reelle*100)-->1,0<!--/--> %** dans les deux variantes. C'est la nomenclature que le COR retient
depuis son rapport de juin 2025 — celui-là même qui abandonne la variante à
<!--chiffre:illustration()-->1,3<!--/--> %, « prenant note du ralentissement structurel de la productivité » — et
qu'il reconduit à l'identique en juin 2026. Toute année projetée porte la
fiabilité la plus basse, qui se propage jusqu'au résultat.

**Le site affiche une fourchette, pas un nombre seul.** Sous les cinq scénarios,
un bloc rejoue la même carrière sous les trois hypothèses de productivité et
donne l'amplitude — pour la génération 2000, entrée à <!--chiffre:illustration()-->21<!--/--> ans et partant à
<!--chiffre:illustration()-->64<!--/--> ans, la pension du scénario 2 va de <!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=basse)-->639<!--/--> € à <!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=haute)-->803<!--/--> € par mois, soit
<!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=amplitude)-->25,7<!--/--> % d'écart. Il dit aussi combien d'années du compte tombent après la
dernière observation : <!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=projetees)-->39<!--/--> sur <!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=annees)-->44<!--/-->, soit <!--chiffre:mesure(fourchette?generation=2000&depart=64&debut=21&quoi=part)-->88,6<!--/--> % du calcul. Quand la liquidation précède cette année-là, le bloc le
dit et ne montre aucune fourchette — **aucune hypothèse n'entre alors dans le
chiffre**, et c'est la chose la plus utile qu'on puisse dire à un lecteur qui
s'en méfie.

Cette fourchette n'est **pas un intervalle de confiance** : elle ne fait varier
que la productivité, laisse l'inflation à <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> %, l'emploi sur la trajectoire
retenue — celle du scénario de référence du COR par défaut, constant en
variante — et la législation inchangée. C'est une mesure de sensibilité à un
paramètre, et la page l'écrit — l'avenir peut sortir de la fourchette. Le
même bloc dit ensuite ce que l'emploi projeté pèse à part, en rejouant le
système 2 sous l'autre trajectoire ; le système 1 n'y bouge pas, puisqu'il
ne lit pas l'emploi.

La dernière année observée n'est pas codée en dur : elle est **déduite des
séries**, comme la dernière que les trois assiettes portent au-dessus de
`estimee`. Le fichier d'hypothèses la déclare aussi de son côté, et un test
exige que les deux coïncident : une déclaration que rien ne contrôle finit par
mentir.

Deux écarts avec la source, assumés et détaillés dans le fichier
d'hypothèses : le COR raisonne en productivité **horaire**, le modèle en
productivité **par tête**, seule série que l'INSEE publie de 1950 à 2025 ; le
COR atteint sa cible **en 2040**, le modèle l'applique **dès 2026**, sans
trajectoire de convergence. L'emploi, que le modèle a longtemps supposé
constant, suit désormais la trajectoire de référence du COR, l'emploi constant
restant en variante. Et l'inflation de <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> % est une convention reconduite des
rapports antérieurs du COR — ce n'est pas la cible de la BCE, qui est de
<!--chiffre:illustration()-->2<!--/--> % symétrique depuis 2021, et les documents publics de juin 2025 et de juin 2026 ne la
restatent pas.

---

## 4. L'âge de référence

### La construction

L'âge de référence est l'âge auquel une liquidation est réputée « à l'heure ».
Il se lit en deux temps, séparés par l'année de bascule.

**À partir de la bascule, il vaut <!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans** : l'âge légal d'ouverture des droits
que la loi du 14 avril 2023 a fixé, et que la génération <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:generation?age=64.00)-->1969<!--/--> sera la première à
atteindre — l'article 105 de la loi n° 2025-1403 du 30 décembre 2025, qui
suspend la réforme, en a retardé la montée d'un trimestre par génération. C'est
le défaut du modèle. Le
système proposé ne reconduit pas le taux plein à <!--chiffre:maximum(data/reference/legislation/ages_reference.csv:age_taux_plein_legal)-->67<!--/--> ans, parce que le taux plein
est une condition de **durée d'assurance** — un nombre de trimestres — et qu'un
compte notionnel n'a pas cette notion : il n'a qu'un capital et un diviseur.
Reconduire <!--chiffre:maximum(data/reference/legislation/ages_reference.csv:age_taux_plein_legal)-->67<!--/--> ans aurait été importer dans le système proposé une borne que rien
n'y justifie.

**Avant la bascule, il est bâti à cliquet** : c'est le maximum de tous les âges
de taux plein observés jusqu'à l'année considérée, et il ne redescend jamais.
<!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:age)-->64<!--/--> ans n'existe dans aucun droit avant que la génération 1969 l'atteigne ;
une liquidation de 1990 se mesure donc à son époque, et non à la nôtre.

| Période | Âge du taux plein en droit | Âge de référence retenu |
|---|---|---|
| 1945-1981 | <!--chiffre:cellule(data/reference/legislation/ages_reference.csv:age_taux_plein_legal?annee=1945)-->65<!--/--> ans | <!--chiffre:mesure(age_reference?annee=1950)-->65<!--/--> ans |
| 1982-2010 | **<!--chiffre:cellule(data/reference/legislation/ages_reference.csv:age_taux_plein_legal?annee=1982)-->60<!--/--> ans** (ordonnance du 26 mars 1982) | **<!--chiffre:mesure(age_reference?annee=1990)-->65<!--/--> ans** — le cliquet tient |
| 2011-2016 | montée en charge 65 → 67 | 65 → <!--chiffre:mesure(age_reference?annee=2020)-->67<!--/--> ans |
| 2017-2025 | <!--chiffre:cellule(data/reference/legislation/ages_reference.csv:age_taux_plein_legal?annee=2017)-->67<!--/--> ans | <!--chiffre:mesure(age_reference?annee=2020)-->67<!--/--> ans |
| 2026- | <!--chiffre:maximum(data/reference/legislation/ages_reference.csv:age_taux_plein_legal)-->67<!--/--> ans | **<!--chiffre:mesure(age_reference?annee=2026)-->65<!--/--> ans** — l'âge fixe prend le relais |

Conséquences directes sur la période à cliquet, conformes à la demande :

- une liquidation à <!--chiffre:illustration()-->60<!--/--> ans en 1990 est une **anticipation de <!--chiffre:mesure(age_reference?annee=1990&depart=60)-->5<!--/--> ans** ;
- un agent de conduite parti à <!--chiffre:illustration()-->50<!--/--> ans en 1990 anticipe de **<!--chiffre:mesure(age_reference?annee=1990&depart=50)-->15<!--/--> ans** ;
- un danseur de l'Opéra parti à <!--chiffre:illustration()-->40<!--/--> ans anticipe de **<!--chiffre:mesure(age_reference?annee=1990&depart=40)-->25<!--/--> ans**.

### Comment l'écart pèse sur la pension

Il ne faut **pas** ajouter une décote par-dessus, et le modèle ne le fait pas
par défaut. L'anticipation est déjà sanctionnée deux fois, mécaniquement :

1. les années non travaillées n'ont produit aucune cotisation ;
2. la rente est servie plus longtemps, donc le diviseur est plus élevé.

Ordre de grandeur du second effet seul : cinq ans d'anticipation sur
<!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans en 2026 augmentent le diviseur de <!--chiffre:mesure(anticipation?avance=5&annee=2026&quoi=esperance)-->4,6<!--/--> années d'espérance de vie, soit
une pension annuelle inférieure de <!--chiffre:mesure(anticipation?avance=5&annee=2026)-->17<!--/--> %. En ajoutant les cinq années de
cotisations manquantes sur une carrière de <!--chiffre:illustration()-->42<!--/--> ans, la perte totale approche
<!--chiffre:mesure(anticipation?avance=5&annee=2026&carriere=42)-->27<!--/--> %.

Une décote explicite supplémentaire reste disponible
(`ModeCoefficientEcart.EXPLICITE`), mais c'est alors une double peine assumée.

### Ce que l'âge de référence déplace, et ce qu'il ne déplace pas

Il ne pèse sur AUCUNE pension des quatre systèmes que le site compare : le
scénario 1 ne le lit jamais, et les scénarios rétroactifs recalculent toute la
carrière sans rien figer. Il ne pèse que sur les deux scénarios **prospectifs**,
et par un seul canal — le diviseur auquel les droits acquis sont convertis à la
bascule (§5). Partout ailleurs, il est une grandeur affichée : l'écart
d'anticipation que le rapport de simulation imprime.

Ce canal unique n'est pas léger pour autant. Un âge de référence plus bas
prend un diviseur plus élevé, donc un capital d'ouverture plus gros, et le
cadeau va tout entier aux générations de transition. Le défaut suit l'âge légal
de départ de la proposition, <!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans : moins que les <!--chiffre:maximum(data/reference/legislation/ages_reference.csv:age_reference)-->67<!--/--> ans du
cliquet, et les deux scénarios prospectifs dépensent donc davantage qu'avec
lui. Leurs soldes moyens sont, sous le défaut, de <!--chiffre:mesure(solde_moyen?scenario=3)-->+1,80<!--/--> et <!--chiffre:mesure(solde_moyen?scenario=5)-->+0,20<!--/--> % du
PIB, contre <!--chiffre:mesure(solde_moyen?scenario=1)-->−1,13<!--/--> pour le système actuel.

### Variantes

- `fixe_apres_bascule` (défaut) — la règle décrite ci-dessus ;
- `cliquet_legal` — le cliquet sur toute la période, sans âge fixe après la
  bascule ;
- `cliquet_puis_esperance_vie` — après la bascule, l'âge de référence suit
  l'espérance de vie de façon à stabiliser le rapport durée de retraite / durée
  de carrière ;
- `legal_sans_cliquet` — contrefactuel reproduisant le droit positif.

---

## 5. Le coefficient de conversion

```
G(a, L) = Σ_t  (probabilité de survie t années après la liquidation) × (1+ν)^(-t)
```

- **Table de génération**, pas table du moment. À chaque année vécue est
  appliquée la mortalité de l'année civile correspondante. Une table du moment
  sous-estimerait la longévité des générations récentes de <!--chiffre:mesure(table_mortalite?age=64&annee=2040&quoi=moment)-->1,4<!--/--> à <!--chiffre:mesure(table_mortalite?age=64&annee=2000&quoi=moment)-->2<!--/--> ans pour
  une liquidation à <!--chiffre:illustration()-->64<!--/--> ans entre 2040 et 2000, et surestimerait donc leur
  pension d'autant.
- **Table unisexe** par défaut. C'est la pratique des systèmes notionnels suédois
  et italien. Une table sexuée est actuariellement exacte mais réduirait la
  pension des femmes de <!--chiffre:mesure(table_mortalite?age=64&annee=2040&quoi=sexe)-->5<!--/--> à <!--chiffre:mesure(table_mortalite?age=64&annee=2000&quoi=sexe)-->10<!--/--> % à capital identique, sur les mêmes dates, et serait contraire au
  principe de non-discrimination. `--table par_sexe` permet de mesurer l'écart.
- **Table par niveau de vie** par défaut, depuis le 21 septembre 2026, et
  c'est un choix qui se désactive d'un mot. Une table de population générale
  — la même espérance de vie pour l'ouvrier et pour le cadre — transfère à
  qui vit plus longtemps, et qui vit plus longtemps est aussi qui a le plus
  cotisé : le diviseur commun coûte au régime quatre à cinq dixièmes de point
  de PIB, et les prend aux modestes. Le modèle rattache donc chaque carrière
  au vingtile de niveau de vie où son salaire la place (bullet suivant) et
  lui sert le diviseur de ce vingtile, stock compris : les scénarios
  rétroactifs recalculent tout le monde ainsi. L'interrupteur est
  `Parametres.population_conversion` : `None` rend la table commune partout,
  sur le site sous « Population générale, la même pour tous », et les scripts
  de mesure la posent pour chiffrer ce que le défaut déplace. Une population
  nommée s'impose aussi à toute carrière, pour mesurer :
  `population=fonctionnaires_civils_etat` remplace la table par celle des
  pensionnés civils de l'État, dont le Service des retraites de
  l'État publie l'espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans (<!--chiffre:cellule(data/reference/mortalite/esperances_vie_populations.csv:valeur?population=fonctionnaires_civils_etat&sexe=F&annee=2024)-->24,68<!--/--> ans pour les femmes, <!--chiffre:cellule(data/reference/mortalite/esperances_vie_populations.csv:valeur?population=fonctionnaires_civils_etat&sexe=H&annee=2024)-->21,16<!--/-->
  pour les hommes en 2024, un an de plus que l'INSEE à la population
  générale). La table n'est pas reconstruite : un facteur sur la force de
  mortalité de la table générale — la survie de chaque cellule élevée à cette
  puissance, 0,85 pour les deux sexes — est calé sur l'année observée pour
  reproduire l'espérance publiée, puis tenu constant sur toutes les années,
  faute d'observation ailleurs. `scripts/mortalite_population.py` en tire le
  transfert, cas type par cas type et sur les six scénarios : pour le
  fonctionnaire sédentaire né en 1975, <!--chiffre:mesure(mortalite_population?population=fonctionnaires_civils_etat&cas=fonctionnaire_sedentaire&generation=1975&quoi=annees)-->1,3<!--/--> an de rente de plus, soit <!--chiffre:mesure(mortalite_population?population=fonctionnaires_civils_etat&cas=fonctionnaire_sedentaire&generation=1975&quoi=ecart&abs=1)-->5,2<!--/--> % de
  pension notionnelle à capital égal, et <!--chiffre:mesure(mortalite_population?population=fonctionnaires_civils_etat&cas=fonctionnaire_sedentaire&generation=1975&quoi=transfert)-->47 573<!--/--> € sur la vie sous le système
  actuel, qui ne connaît aucun diviseur et transfère donc autant.
- **L'axe du revenu, par les tables de l'INSEE.** L'INSEE publie des tables
  de mortalité par VINGTILE de niveau de vie (Insee Résultats, mai 2025 ;
  `mortalite/esperances_vie_niveau_de_vie.csv`, lu par
  `scripts/fetch/insee_mortalite_niveau_de_vie.py`) : à <!--chiffre:illustration()-->65<!--/--> ans en 2020-2024,
  <!--chiffre:cellule(data/reference/mortalite/esperances_vie_niveau_de_vie.csv:valeur?periode=2020-2024&sexe=H&vingtile=1&mesure=e65)-->15,1<!--/--> ans pour les <!--chiffre:illustration()-->5<!--/--> % d'hommes les plus modestes contre <!--chiffre:cellule(data/reference/mortalite/esperances_vie_niveau_de_vie.csv:valeur?periode=2020-2024&sexe=H&vingtile=20&mesure=e65)-->22,1<!--/--> pour les <!--chiffre:illustration()-->5<!--/--> %
  les plus aisés, <!--chiffre:cellule(data/reference/mortalite/esperances_vie_niveau_de_vie.csv:valeur?periode=2020-2024&sexe=F&vingtile=1&mesure=e65)-->20,15<!--/--> contre <!--chiffre:cellule(data/reference/mortalite/esperances_vie_niveau_de_vie.csv:valeur?periode=2020-2024&sexe=F&vingtile=20&mesure=e65)-->25,2<!--/--> chez les femmes. Chaque vingtile est une
  population du diviseur, `niveau_de_vie_v01` à `_v20`, calée non sur sa
  valeur brute mais sur son rapport à l'ensemble de l'étude — qui vit un à
  trois dixièmes de moins que la population générale certifiée, par son champ
  et sa méthode. Un cas type y est RATTACHÉ par une convention et non par une
  mesure : son salaire rapporté au salaire moyen, appliqué au niveau de vie
  mensuel moyen des vingt vingtiles, désigne le vingtile dont le niveau de vie
  moyen est le plus proche (`population_niveau_de_vie`). Le niveau de vie est
  celui d'un ménage par unité de consommation, et un salaire n'en dit qu'une
  partie : la convention place le SMIC au quatrième vingtile, le salaire
  moyen au treizième, le cadre au dix-neuvième. Le résultat, pour la
  génération 1975 (`scripts/mortalite_population.py --niveau-de-vie`) : le
  salarié au SMIC a <!--chiffre:mesure(mortalite_population?population=vingtile&cas=smic_carriere_complete&generation=1975&quoi=annees&abs=1)-->2,7<!--/--> ans de rente de MOINS que la table commune ne lui
  en compte, l'exploitant agricole <!--chiffre:mesure(mortalite_population?population=vingtile&cas=exploitant_agricole&generation=1975&quoi=annees&abs=1)-->3,3<!--/--> de moins, le cadre <!--chiffre:mesure(mortalite_population?population=vingtile&cas=cadre&generation=1975&quoi=annees&abs=1)-->2,4<!--/--> de plus, le
  libéral <!--chiffre:mesure(mortalite_population?population=vingtile&cas=profession_liberale&generation=1975&quoi=annees&abs=1)-->2,8<!--/--> de plus. Un diviseur commun transfère donc des modestes vers
  les aisés : <!--chiffre:mesure(mortalite_population?population=vingtile&cas=smic_carriere_complete&generation=1975&quoi=ecart&abs=1)-->11,2<!--/--> % de pension notionnelle à capital égal pour le SMIC,
  <!--chiffre:mesure(mortalite_population?population=vingtile&cas=profession_liberale&generation=1975&quoi=ecart&abs=1)-->11,1<!--/--> % dans l'autre sens pour le libéral, et sur la vie <!--chiffre:mesure(mortalite_population?population=vingtile&cas=smic_carriere_complete&generation=1975&quoi=transfert&abs=1)-->43 177<!--/--> € retirés
  au premier et <!--chiffre:mesure(mortalite_population?population=vingtile&cas=profession_liberale&generation=1975&quoi=transfert&abs=1)-->165 486<!--/--> € ajoutés au second sous le système actuel — qui
  transfère autant que les autres, n'ayant aucun diviseur pour le savoir.
  Cette mesure est celle que le défaut applique désormais ; ses chiffres
  restent ceux de la table commune contre le vingtile, et
  `scripts/mortalite_population.py` les recalcule en posant la table commune.
  Le rattachement peut aussi se faire **par la pension**
  (`rattachement_niveau_de_vie="pension"`, sur le site « Rattachement au
  niveau de vie ») : le RANG de la pension brute parmi les retraités, lu
  dans la distribution des pensions de la DREES
  (`macro/distribution_pensions.csv`, la pension ramenée aux euros du
  millésime au rythme du salaire moyen), le vingtile étant celui de ce rang.
  Comparer une pension aux niveaux de vie de la population entière l'aurait
  classée presque toujours en bas, une pension étant plus petite qu'un
  salaire ; le rang parmi les retraités suppose, lui, que le niveau de vie
  d'un retraité suit sa pension, ce qui néglige le conjoint et le
  patrimoine. C'est circulaire sous un compte notionnel, la pension
  dépendant du diviseur, et le modèle itère jusqu'au point fixe, six tours
  au plus. Par la pension, le SMIC à carrière complète monte au sixième
  vingtile — <!--chiffre:mesure(part_pensions_sous?borne=1500&annee=2020)-->59<!--/--> % des retraités touchaient moins de <!--chiffre:illustration()-->1 500<!--/--> € en 2020 —, le salaire
  moyen au onzième, le cadre reste au dix-neuvième, et les régimes à départ
  précoce descendent, leur pension étant plus petite que leur salaire ne
  le laissait croire.
  Ce que le défaut suppose est écrit avec lui : un salaire n'est pas un niveau
  de vie de ménage, et le facteur de chaque vingtile est tenu constant dans
  le temps.
- **ν = 0** par défaut. La rente est actualisée au taux auquel elle sera ensuite
  revalorisée ; les deux étant identiques, ils se compensent et le diviseur se
  réduit à l'espérance de vie résiduelle. Le résultat est directement lisible.
- **Pas de réversion**, donc pas de rente sur deux têtes : la demande est
  explicite sur ce point.

Les tables elles-mêmes sont décrites au §9.

---

## 6. Les neutralisations

> **L'inventaire complet de ce que le scénario 1 sert au-delà de la cotisation
> — trente-neuf dispositifs, avec leur base légale et le moyen d'en chiffrer le
> coût — est dans `data/reference/legislation/avantages_non_contributifs.yaml`,
> et `docs/avantages_non_contributifs.md` le commente.** Le tableau ci-dessous
> ne porte que les quinze champs de `Neutralisations`, qui sont une déclaration
> d'intention de réforme et non une liste du droit positif.

Sont **supprimés** dans les scénarios notionnels — tous activés par défaut dans
`Neutralisations` :

| Supprimé | Raison invoquée dans la demande |
|---|---|
| minimum contributif, minimum garanti, ASPA, PMR | supprimer les effets de seuil |
| majoration pour trois enfants et plus | avantage sans cotisation |
| majoration de durée d'assurance, AVPF | l'aide doit être versée au moment de la difficulté |
| pension de réversion | seules les cotisations comptent |
| bonifications, catégorie active | avantage sans cotisation |
| périodes assimilées (chômage, maladie, service militaire) | pas de cotisation, pas de droit |
| trimestres assimilés au régime de base | pas de cotisation, pas de droit |
| garantie minimale de points (Agirc) | droit gratuit |
| carrières longues | dispositif d'âge, remplacé par l'actuariel |
| décote et surcote | remplacées par le coefficient de conversion |

La page de simulation affiche désormais leur effet en euros, ligne à ligne :
sous-total contributif, puis chaque avantage, puis le total. Les lignes
s'additionnent exactement, et l'écart avec les scénarios notionnels devient
lisible — ce qu'ils retirent, c'est précisément la somme de ces lignes.

Les drapeaux ci-dessus ne sont pas lus par le scénario 1 : ils décrivent ce que
les scénarios notionnels retirent, pas ce que le droit en vigueur accorde. Les
lire des deux côtés amputait l'étalon du minimum contributif, de la majoration
pour trois enfants et de la MDA, c'est-à-dire précisément de ce qui protège les
carrières que le notionnel pénalise le plus : l'écart mesuré s'en trouvait
minoré.

**Mais ce tableau a longtemps annoncé retirer ce que le scénario 1 ne servait
pas.** On ne retire pas ce qui n'a jamais été mis, et cinq lignes étaient dans
ce cas : le minimum garanti, l'ASPA, l'AVPF, la garantie minimale de points et
la carrière longue. Elles sont désormais calculées. L'état exact, ligne à
ligne :

| Ligne du tableau | Le scénario 1 la sert-il ? |
|---|---|
| minimum contributif | oui, réservé au taux plein, deux prorata, écrêté |
| minimum garanti | oui, barème de l'article L. 17 |
| ASPA | oui, à partir de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, barème d'une personne seule, ligne séparée |
| PMR (retraite agricole) | **non** — voir `docs/limites.md` |
| majoration pour trois enfants | oui, plafonnée en euros à la complémentaire |
| majoration de durée d'assurance | oui, attribuée dans un régime |
| AVPF | oui, salaire forfaitaire au SMIC porté au compte |
| pension de réversion | **non** — elle ne concerne pas l'assuré lui-même |
| bonifications, catégorie active | **non** — elles supposent des informations que le modèle n'a pas |
| périodes assimilées | oui, motif par motif — et ce qu'elles ouvrent en services, à part |
| garantie minimale de points | oui, <!--chiffre:partout(data/reference/regimes/complementaires_prive.yaml:regimes.*.periodes.*.points_minimum_annuels)-->120<!--/--> points par an de 1989 à 2018 |
| carrières longues | oui, pour dire si le droit ouvre la liquidation |
| décote et surcote | oui, barème propre à la fonction publique compris |
| coefficient de solidarité Agirc-Arrco | **non** — dispositif éteint, voir `docs/limites.md` |

Une seule exception, et elle est explicite : la valorisation des droits acquis
du scénario 3 appelle le scénario 1 avec `avantages_non_contributifs=False`,
parce qu'elle mesure du contributif pur.

Le critère retenu pour une période non cotisée est **le versement effectif de
cotisations**, pas la nature de la période — et c'est bien ainsi que le modèle
la traite, motif par motif
(`data/reference/legislation/periodes_non_travaillees.csv`). Deux droits sont à
distinguer, et ils ne suivent pas la même règle :

- les **trimestres assimilés** comptent dans la durée d'assurance du régime de
  base sans aucune cotisation. Ils protègent de la décote et entrent dans la
  proratisation, mais n'ajoutent aucun salaire au compte, donc rien au salaire
  de référence. Le scénario 1 les conserve, les scénarios notionnels les
  suppriment. Le chômage NON indemnisé n'en ouvre que sous les limites de
  l'article R. 351-12 : rien avant 1980, la première période à un an — un an et
  demi pour les périodes postérieures à 2010 —, chaque période ultérieure à un
  an si elle suit un chômage indemnisé, cinq ans pour l'assuré de cinquante-cinq
  ans qui a vingt ans de cotisations, et rien sinon ;
- les **points complémentaires** ne sont pas tous de la même nature, et c'est
  qui les paie qui les sépare. Pendant un chômage indemnisé, l'Unédic verse de
  vraies cotisations à l'Agirc-Arrco, calculées sur le salaire d'avant
  l'interruption : ces points sont acquis dans tous les scénarios, y compris
  en notionnel, puisque des cotisations ont bien été versées — et après la
  bascule aussi, où le compte porte ce que l'Unédic verse, jamais le taux
  unifié entier ni le pilier capitalisé, que personne ne paie. Pendant une
  maladie, une maternité, une invalidité ou un accident du travail, l'Agirc-
  Arrco attribue ses points « sans contrepartie de cotisations » (guide
  Agirc-Arrco n° 6, février 2017) : le scénario 1 les sert, les scénarios
  notionnels non. Jusqu'au 23 septembre 2026, le modèle les portait au compte
  comme payés, et après la bascule portait l'année entière au taux unifié.

- les **services de la fonction publique** sont une troisième case, et la même
  période n'y compte pas de la même façon. La pension de l'État ne se proratise
  pas sur la durée d'assurance mais sur les services et bonifications
  (article L. 13 du code des pensions), et l'article L. 9 en écarte « le temps
  passé dans une position statutaire ne comportant pas l'accomplissement de
  services effectifs au sens de l'article L. 5 », hors une liste fermée :
  congés de maladie, de maternité, d'accident de service et de maladie
  professionnelle du fonctionnaire en activité, congé parental dans la limite
  de trois ans par enfant, détachement. Le chômage n'est pas une position
  statutaire, et n'y ouvre donc rien.

- les **trimestres réputés cotisés** sont la quatrième case, et elle ne sert
  qu'à une chose : la carrière longue, qui ne compte pas la durée d'assurance
  mais celle qui a donné lieu à cotisations. L'article D. 351-1-2 y ajoute une
  liste fermée de périodes qu'il RÉPUTE cotisées, chacune sous sa propre limite,
  comptée sur toute la carrière et tous régimes confondus : service national,
  incapacité temporaire, chômage indemnisé, invalidité et assurance vieillesse
  des parents au foyer. La maternité est la seule que le décret n'écrête pas, et
  le chômage NON indemnisé la seule période assimilée qu'il ne reprenne jamais.

Une année de chômage indemnisé n'est donc pas vide à l'Agirc-Arrco alors
qu'elle l'est à la CNAV ; une année de chômage non indemnisé est vide partout.
Et les mêmes cinq années de chômage, qui valident vingt trimestres de durée
d'assurance à la CNAV, n'ouvrent aucun service à l'État et quatre trimestres
seulement à la carrière longue.

### La validation des trimestres

Un trimestre ne s'acquiert pas par le temps qui passe mais par un **montant
cotisé** : 150 fois le SMIC horaire depuis 2014, 200 fois entre 1972 et 2013,
dans la limite de quatre par année civile. Une année à temps très partiel en
valide donc moins de quatre. Le montant commande le nombre, les MOIS en
commandent le plafond : l'année du point de départ et celle de l'entrée dans la
vie active sont incomplètes, et ne valident que les trimestres civils écoulés —
un départ au 1<sup>er</sup> août en laisse deux derrière lui, si gros que soit
le salaire de ces sept mois. La série du SMIC horaire vient d'OpenFisca-France
(`scripts/fetch/openfisca_smic.py`), transcription du *Journal officiel* : elle
plafonne à la fiabilité `haute`.

---

## 7. La fusion des régimes

À compter de l'année de bascule (2026 par défaut), les régimes disparaissent au
profit d'un régime unique construit **au cas le plus défavorable** :

| Paramètre | Règle | Valeur 2026 |
|---|---|---|
| âge d'ouverture | le plus élevé | <!--chiffre:mesure(fusion?champ=age_ouverture)-->65<!--/--> ans |
| âge du taux plein | le plus élevé | <!--chiffre:mesure(fusion?champ=age_taux_plein)-->67,5<!--/--> ans |
| durée requise | la plus longue | <!--chiffre:mesure(fusion?champ=duree_requise_trimestres)-->172<!--/--> trimestres |
| salaire de référence | le moins avantageux | carrière entière |
| assiette | la plus large | déplafonnée |
| avantages non contributifs | aucun | — |

**Le taux de cotisation fait exception, et c'est le seul.** Le retenir « au plus
défavorable » n'aurait pas de sens : un taux plus faible réduit les droits, mais
réduit tout autant les prélèvements. Retenir le maximum n'est pas meilleur : ce
maximum est aujourd'hui le taux d'équilibre d'une caisse publique
(<!--chiffre:mesure(fusion?champ=taux_cotisation_retraite&critere=le_plus_eleve)-->41,2<!--/--> %), fixé pour combler un déficit et non pour ouvrir des droits. Le
régime fusionné retient donc la **somme des taux d'un statut pivot** — régime
général <!--chiffre:mesure(fusion?pivot=regime_general)-->17,96<!--/--> % + Agirc-Arrco <!--chiffre:mesure(fusion?pivot=agirc_arrco)-->7,87<!--/--> % =
**<!--chiffre:mesure(fusion?champ=taux_cotisation_retraite)-->25,83<!--/--> %** — c'est-à-dire l'effort contributif réel d'un salarié pour une
retraite complète. Modifiable par `RegleFusion.critere_taux`.

Le régime unique **hérite aussi de la répartition salarié/employeur** de ses
régimes pivots : <!--chiffre:mesure(fusion?champ=taux_cotisation_salarie)-->10,45<!--/--> % de part salariale sur <!--chiffre:mesure(fusion?champ=taux_cotisation_retraite)-->25,83<!--/--> % en 2026. Ce n'est pas une
décision de la fusion mais la conséquence de ce qui la compose, et c'est elle
qui, après la bascule, sépare le scénario 5 du scénario 3. Une exception : un
assuré qui n'avait pas d'employeur — artisan, libéral — n'en gagne pas un en
changeant de régime ; le taux unique lui est alors intégralement personnel.

**Conséquence à connaître.** Ce taux appliqué à une assiette déplafonnée
augmente fortement les cotisations des indépendants et des professions
libérales, qui cotisent aujourd'hui à taux plus faible et sur assiette plafonnée.
Leur pension notionnelle monte en proportion : c'est pour eux la seule ligne du
tableau des cas types qui progresse. Le résultat est correct, il faut seulement
savoir qu'il traduit une hausse de prélèvement, pas un cadeau.

---

## 8. Les six scénarios

### Scénario 1 — le système actuel

Étalon en droit constant. Approximation documentée, pas un simulateur officiel
(voir `docs/limites.md` §3).

Les régimes en annuités suivent la formule `taux × salaire de référence ×
durée / durée requise`. Les **régimes en points** sont calculés en points, et
non par un rendement moyen :

```
points acquis en année t = cotisation(t) / (taux d'appel(t) × salaire de référence(t))
pension                  = Σ points × valeur de service (année de liquidation)
```

Le taux d'appel est le décalage, invisible ailleurs, entre ce qui est prélevé et
ce qui ouvre des droits : depuis la fusion de 2019, cotiser <!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:valeur*100?regime=agirc_arrco&mesure=taux_appel)-->127<!--/--> € n'acquiert que
<!--chiffre:illustration()-->100<!--/--> € de points, et l'Agirc en demandait déjà <!--chiffre:cellule(data/reference/regimes/valeurs_point.csv:valeur*100?regime=agirc&annee=1995&mesure=taux_appel)-->125<!--/--> en 1995. L'ignorer
surestimerait la retraite complémentaire d'un bon quart.

Un régime fermé ne sert plus ses points : ils passent à son successeur, au
coefficient que l'accord de fusion a fixé. Le modèle refait ce chemin (UNIRS →
Arrco → Agirc-Arrco, Agirc → Agirc-Arrco, IPACTE et IGRANTE → Ircantec) à
partir de `regimes/conversions_points.csv`, où **ces coefficients sont lus et
non plus devinés**.

Les deviner coûtait cher, et de deux façons. Le modèle prenait le rapport entre
la dernière valeur de service du régime d'origine et la **première** du
successeur ; or les séries `arrco` et `ircantec` sont rétro-remplies bien avant
leur fusion — la première depuis 1957 avec les valeurs de l'UNIRS, la seconde
depuis 1949 avec celles de l'IPACTE. On comparait donc deux valeurs distantes
de quarante ou soixante-dix ans : le point UNIRS ressortait **quinze fois** trop
cher pour toute liquidation postérieure à 1998, le point IPACTE **cinquante-quatre
fois** trop cher au-delà de 2022. Jusqu'à 35 % de la pension du scénario 1 n'avait
alors aucune existence, et la case « SMIC carrière complète, génération 1940 » de
la grille de cas types en était atteinte. Et là même où les deux bornes tombaient
juste, la valeur du successeur était celle du 31 décembre quand la conversion
s'opère au 1<sup>er</sup> janvier : un pour cent de trop peu sur tous les points
d'avant 2019.

**L'unification Arrco du 1<sup>er</sup> janvier 1999 n'est pas une fusion mais un
changement d'unité**, et c'est le défaut le plus lourd que ce fichier corrige.
Les valeurs d'achat et de service portées ici pour les années antérieures sont
celles de l'UNIRS, la plus grosse des quarante-cinq caisses Arrco ; celles
d'après 1999 sont celles du régime unifié, dont la valeur de service a été fixée
à 6,55957 F, soit exactement 1 €. Le moteur accumulait des points dans la
première unité et les liquidait dans la seconde : cent euros cotisés en 1998
produisaient 30,31 € de pension annuelle quand les mêmes cent euros de 1999 n'en
produisaient que 11,15 — un facteur 2,7 en une année, pour une opération que la
formule officielle rendait neutre par construction. Le coefficient, 0,387464,
est la valeur du point UNIRS au 31 décembre 1998. La correction abaisse la
pension du scénario 1 de 1,3 % pour un cadre né en 1975 à 17 % pour les
générations nées entre 1940 et 1955.

Les régimes dont le dépôt n'a pas les barèmes — CNAVPL, MSA, CNBF, RCI, RAFP —
gardent l'ancienne approximation : `pension = cotisations revalorisées ×
rendement instantané`, où le rendement est `valeur de service / (taux d'appel ×
salaire de référence)`.

#### Ce que chaque régime liquide, et sur quoi

Le salaire de référence porte sur **les seules années passées dans ce
régime-là**. Un régime ne liquide que ce qui lui a été déclaré : la pension
civile se calcule sur le traitement des six derniers mois de service, pas sur le
dernier salaire d'une carrière poursuivie ailleurs. Le modèle a longtemps pris
toute la carrière, si bien qu'un agent SNCF passé au régime général liquidait sa
pension spéciale sur son dernier salaire de salarié — vingt pour cent de trop
sur un cas type — pendant que le prorata de durée, lui, restait celui du régime.

**Les salaires portés au compte sont revalorisés par les coefficients que la
Cnav publie**, lus dans `legislation/revalorisation_salaires.csv`. Cette grandeur
commande le salaire annuel moyen deux fois plutôt qu'une : la moyenne porte sur
les N MEILLEURES années, et « meilleures » se juge sur des salaires revalorisés
— changer les coefficients ne déplace donc pas seulement le niveau de chaque
année, cela change lesquelles sont retenues.

Le modèle les approchait par « les salaires jusqu'en 1986, les prix depuis », ce
qu'ont fait les arrêtés dans les grandes lignes. Mais seulement dans les grandes
lignes : ils ont connu des revalorisations semestrielles, des gels, des
revalorisations exceptionnelles, et des changements du délai d'application.
L'approximation **sur-revalorise les salaires anciens de <!--chiffre:mesure(approximation_revalorisation?de=1970&a=2018)-->17,4<!--/--> % sur 1970-2018**,
et gonflait d'autant le salaire de référence de toute carrière en comportant.

La source est la circulaire annuelle de revalorisation de la Cnav, qui publie la
table entière : c'est la caisse qui les applique qui les publie. Le dépôt a
d'abord repris la table d'OpenFisca-France-Pension, à qui il manque la
revalorisation exceptionnelle de 4 % du 1<sup>er</sup> juillet 2022 — de 3 à
5,5 % d'écart avec la circulaire sur toutes les perceptions postérieures à 1990,
et jusqu'à 17 % sur les années 1950. Une seconde implémentation est une
contre-expertise, pas une source.

**Le coefficient se lit dans une colonne**, par rapport de deux de ses valeurs :
l'arrêté annuel applique un coefficient unique à tous les salaires déjà portés au
compte, quelle que soit leur année de perception. Une colonne suffirait donc en
théorie à reconstruire toutes les autres — en pratique la caisse arrondit sa
table à trois décimales et repart chaque année de la précédente, si bien que la
reconstruction dérive avec la distance — `limites.md` en donne la mesure. Le
dépôt garde donc les **<!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes publiées** d'octobre 2017 à janvier 2026. Le
modèle sert la colonne EN VIGUEUR À LA DATE DE LIQUIDATION — la plus récente
dont la date d'effet ne lui est pas postérieure, dans son année — et l'écart est
alors nul ; il ancre sinon sur la plus proche, ce qui réduit la dérive.
C'est le mois qui désigne la colonne, et il faut qu'il le fasse : deux
circulaires portent l'année 2022, celle du 1<sup>er</sup> juillet dépassant
celle du 1<sup>er</sup> janvier de <!--chiffre:mesure(ecart_colonnes?de=2022-01-01&a=2022-07-01)-->3,9<!--/--> % au moins.

Trois bornes demeurent : avant 2017 aucune circulaire n'est accessible et la
dérive y est invérifiable ; après 2026 le coefficient est ancré sur la dernière
colonne et prolongé par l'approximation ; et le modèle raisonne à l'année,
retenant l'état au 1<sup>er</sup> janvier, quand la revalorisation s'appliquait
au 1<sup>er</sup> avril de 2009 à 2013 puis au 1<sup>er</sup> octobre jusqu'en
2017 — ce que `docs/limites.md` chiffre. Les régimes qui liquident sur le
dernier traitement ou sur les six derniers mois ne portent aucun salaire à un
compte : l'approximation y reste la règle.

#### Le taux plein, et ce qui l'ouvre

Trois choses distinctes, que le modèle confondait :

* **l'âge d'OUVERTURE des droits**, en deçà duquel aucune liquidation n'est
  possible — sauf carrière longue ;
* **la durée requise**, qui ouvre le taux plein à l'âge d'ouverture ;
* **l'âge d'ANNULATION de la décote**, qui l'ouvre sans condition de durée.

**La durée requise et la durée de proratisation sont deux paramètres, et le
modèle les confondait.** La première (L. 161-17-3) commande le TAUX : en deçà,
la décote s'applique. La seconde (R. 351-6) est le DÉNOMINATEUR qui réduit la
pension d'une carrière incomplète. La loi du 22 juillet 1993 a fait monter la
première de <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1900)-->150<!--/--> à <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1943)-->160<!--/--> trimestres pour les générations 1934 à 1943 ; elle n'a
touché à la seconde que pour les générations 1944 à 1948, et de deux trimestres
par génération — <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1900)-->150<!--/--> avant 1944, puis <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1944)-->152<!--/-->, <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1945)-->154<!--/-->, <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1946)-->156<!--/-->, <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1947)-->158<!--/-->, <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1948)-->160<!--/-->. Un assuré né en
1945 ayant validé <!--chiffre:tenu(test_la_proratisation_ne_penalise_pas_une_carriere_qui_atteint_sa_duree)-->156<!--/--> trimestres se voit donc opposer <!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1945)-->160<!--/--> trimestres pour le
taux, et il est décoté de quatre, mais <!--chiffre:cellule(data/reference/legislation/duree_proratisation.csv:trimestres?generation=1945)-->154<!--/--> pour la proratisation : son
coefficient vaut 1, et non 156/160. Le modèle lui retirait <!--chiffre:tenu(test_la_proratisation_ne_penalise_pas_une_carriere_qui_atteint_sa_duree)-->2,5<!--/--> % de pension de
base que le droit ne retire pas. La table est dans
`legislation/duree_proratisation.csv`, et elle est réservée aux régimes alignés
sur le code de la sécurité sociale : la fonction publique et les régimes
spéciaux ont la leur, calendaire (L. 13 du code des pensions), qui n'est pas
modélisée.

Le taux plein par la durée est une création de l'ordonnance du 26 mars 1982.
Avant elle, le taux ne dépendait QUE de l'âge : <!--chiffre:tenu(test_le_taux_d_avant_1983_ne_depend_que_de_l_age)-->20<!--/--> % à <!--chiffre:tenu(test_le_taux_d_avant_1983_ne_depend_que_de_l_age)-->60<!--/--> ans majorés de quatre
points par année différée jusqu'en 1971, puis — loi Boulin — <!--chiffre:tenu(test_le_taux_d_avant_1983_ne_depend_que_de_l_age)-->25<!--/--> % à <!--chiffre:tenu(test_le_taux_d_avant_1983_ne_depend_que_de_l_age)-->60<!--/--> ans et
<!--chiffre:tenu(test_le_taux_d_avant_1983_ne_depend_que_de_l_age)-->50<!--/--> % à 65. Une carrière de quarante ans liquidée à <!--chiffre:illustration()-->60<!--/--> ans en 1975 était servie
au même taux réduit qu'une carrière de vingt.

La **fonction publique** n'a pas la décote du régime général. L'article L. 14 du
code des pensions lui donne la sienne, et rien n'y coïncide : elle n'existe qu'à
compter de 2006, son coefficient monte d'un huitième de point par an jusqu'à
<!--chiffre:maximum(data/reference/legislation/decote_fonction_publique.csv:coefficient*100)-->1,25<!--/--> % en 2015, et son âge d'annulation n'est pas un âge en propre mais la
**limite d'âge du grade**, diminuée d'un nombre de trimestres décroissant
jusqu'à s'annuler en 2020. Et ces deux paramètres se lisent à l'année où le
droit s'ouvre, non à celle du départ — « année au cours de laquelle sont réunies
les conditions mentionnées au I et au II de l'article L. 24 », titre le tableau
de la loi de 2003. Un sédentaire né en 1952, dont le droit s'ouvre en 2012, voit
sa décote s'annuler à <!--chiffre:tenu(test_la_decote_de_la_fonction_publique_est_celle_de_l_article_l14)-->63<!--/--> ans et neuf mois, pas à 67, et la garde s'il part plus
tard. La même loi fait monter la durée de services du pourcentage maximum de
150 à <!--chiffre:maximum(data/reference/legislation/duree_requise_fonction_publique.csv:trimestres)-->160<!--/--> trimestres,
deux par an, pour les droits ouverts de 2004 à 2008
(`legislation/duree_requise_fonction_publique.csv`) ; la durée du régime
général, par génération, ne vaut pour la fonction publique qu'à compter de 2009.

#### La catégorie active et la pension militaire

Le drapeau `categorie_active` a longtemps existé dans la configuration sans
qu'aucun statut le porte : un policier, un aide-soignant, un surveillant
pénitentiaire étaient calculés comme des sédentaires, et l'âge du sédentaire
leur était opposé. Ils ne le sont plus.

**Ce qui ne peut pas se déduire, se déclare.** Le classement d'un emploi en
catégorie active tient à l'EMPLOI, non à la personne ni au régime : un
aide-soignant et un rédacteur territorial cotisent à la même CNRACL, et l'un
liquide cinq ans avant l'autre. Aucune donnée de carrière — revenu, régime,
âge — ne permet de le deviner. C'est donc le STATUT qui le porte, comme il
porte déjà l'absence d'employeur : `legislation/affiliations.yaml` compte cinq
statuts classés — catégorie active et super-active de l'État et de la CNRACL,
ouvriers de l'État — et deux statuts militaires.

**Ce que le classement déplace**, et qui est lu dans
`legislation/categorie_active.csv` :

* l'**âge d'ouverture** — l'âge anticipé de l'article L. 24, I, 1°, « l'âge
  mentionné au premier alinéa de l'article L. 161-17-2 du code de la sécurité
  sociale diminué de cinq années », et l'âge minoré, le même diminué de dix :
  <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active&generation=1960)-->57<!--/--> et <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=super_active&generation=1965)-->52<!--/--> ans avant la réforme de 2023,
  <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active)-->59<!--/--> et <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=super_active)-->54<!--/--> ans après elle, avec les deux
  montées en charge — celle de la loi du 9 novembre 2010, qui part de
  <!--chiffre:minimum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active)-->55<!--/--> et <!--chiffre:minimum(data/reference/legislation/categorie_active.csv:age_ouverture?classement=super_active)-->50<!--/--> ans, et celle du F du XXIV de l'article 10 de la loi du 14 avril 2023,
  trois mois par génération à compter du 1<sup>er</sup> septembre 1966 et du
  1<sup>er</sup> septembre 1971 ;
* l'**âge d'annulation de la décote** — <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_annulation?classement=active)-->62<!--/--> et <!--chiffre:maximum(data/reference/legislation/categorie_active.csv:age_annulation?classement=super_active)-->57<!--/--> ans, la limite d'âge du grade,
  que l'article L. 14 bis a reprise depuis 2023 sous la forme « âge anticipé
  majoré de trois années ». C'est là que le classement pèse le plus : le barème
  de l'article L. 14 retranche ses trimestres de cette limite-là et non de
  <!--chiffre:maximum(data/reference/legislation/age_annulation_decote.csv:age)-->67<!--/--> ans, si bien qu'un agent classé parti à <!--chiffre:illustration()-->60<!--/--> ans subit huit trimestres de
  décote quand un sédentaire du même âge en subit vingt ;
* la **condition de durée** — dix-sept ans de services actifs, vingt-sept de
  services super-actifs. Sans elle, l'assuré reste au droit commun : le texte
  écrit que la faculté « est ouverte à la condition que le fonctionnaire puisse
  se prévaloir, au total, d'au moins dix-sept ans de services accomplis […] dits
  services actifs », et le modèle compte ces années sur la carrière elle-même.

La **surcote** se compte depuis l'âge légal de droit commun pour le
sédentaire : le III de l'article L. 14 ne la donne qu'« au-delà de l'âge
mentionné à l'article L. 161-17-2 ». L'emploi classé a son propre âge : le D
du XXIV de l'article 10 de la loi de 2023 lui donne l'âge anticipé majoré de
cinq années, pour l'actif né à compter du 1<sup>er</sup> septembre 1966, et
l'âge minoré majoré de dix, pour le super-actif né à compter du
1<sup>er</sup> septembre 1971 — l'âge légal de la génération née cinq ou dix
ans plus tôt, non de la sienne —, et soixante-deux ans aux générations
d'avant. La compter depuis <!--chiffre:cellule(data/reference/legislation/categorie_active.csv:age_ouverture?classement=active&generation=1960)-->57<!--/--> ans aurait payé deux fois l'avantage du
classement ; l'attendre à l'âge légal de sa propre génération le lui
retirerait.

**La pension militaire ne s'ouvre pas à un âge mais à une durée.** Le II de
l'article L. 24 : elle est liquidée « lorsqu'un officier […] réunit, à la date
de son admission à la retraite, vingt-sept ans de services effectifs » et
« lorsqu'un militaire non officier […] réunit […] dix-sept ans de services
effectifs » — vingt-cinq et quinze ans avant la loi du 9 novembre 2010, dont le
relèvement est indexé sur l'ANNÉE où l'ancienne durée est atteinte et non sur la
génération (`legislation/duree_services_militaires.csv`, article 4 du décret
n° 2011-2103). C'est le départ le plus précoce du système : un engagé à
dix-huit ans liquide à trente-cinq. Qui n'atteint pas cette durée mais a quinze
ans de services attend l'âge de jouissance différée de l'article L. 25
(`legislation/age_jouissance_militaire.csv`) ; en deçà de quinze ans, il n'y a
pas de pension militaire et c'est l'âge légal qui vaut.

Deux règles suivent le militaire. Il n'a **pas de surcote** — le III de
l'article L. 14 ne la donne qu'au « fonctionnaire civil ». Et sa **décote** est
celle du II du même article, qui ne compte pas des âges : elle oppose « le
nombre de trimestres manquants […] pour atteindre […] la durée de services
militaires effectifs nécessaire pour pouvoir bénéficier d'une liquidation de la
pension […] augmentée d'une durée de services effectifs de dix trimestres »,
dans la limite de dix trimestres et non de vingt. Un sous-officier parti à
quarante ans avec dix-sept ans de services perd les dix trimestres qui le
séparent de dix-neuf ans et demi, non le quart de sa pension.

Ce qui reste dehors est écrit dans `limites.md` : la LIMITE D'ÂGE DE GRADE, qui
ouvre la pension militaire quelle que soit la durée accomplie et qui sert d'âge
d'annulation de la décote au militaire liquidant à cinquante-deux ans ou plus
(L. 14 bis, 4°), suppose de connaître le grade, que la saisie ne demande pas.

#### La cascade des avantages non contributifs, dans l'ordre du droit

L'ordre n'est pas indifférent : chaque étage se calcule sur le résultat du
précédent, et le modèle en prenait deux à l'envers.

1. **AVPF** — la Caisse nationale des allocations familiales cotise au régime
   général pour le parent qui interrompt son activité, sur une assiette
   forfaitaire égale au SMIC. Ce salaire est PORTÉ AU COMPTE : c'est ce qui
   distingue l'AVPF d'une période assimilée, laquelle valide des trimestres sans
   jamais ajouter de salaire. Son effet n'est pas toujours favorable — sur une
   carrière de moins de vingt-cinq années portées au compte, les années au SMIC
   s'ajoutent aux années retenues au lieu de les remplacer, et abaissent la
   moyenne. C'est la règle, et le modèle la montre telle qu'elle est.
2. **Trimestres accordés au titre des enfants** — datés, sexués, et propres à
   chaque famille de régimes (`legislation/majoration_duree_assurance.csv`). La
   majoration de durée d'assurance de l'article L. 351-4 naît avec la loi du
   31 décembre 1971 à un an par enfant, passe à deux ans en 1975, et va à la
   mère : le partage ouvert en 2010 entre maternité et éducation laisse à la
   mère, à défaut d'accord des parents, les mêmes huit trimestres. La fonction
   publique et les régimes spéciaux ne l'appliquent pas : ils servent la
   bonification de l'article L. 12 b, un an par enfant né avant 2004, puis les
   deux trimestres de l'article L. 12 bis pour les enfants nés depuis. Les
   régimes alignés — artisans, commerçants, salariés agricoles — suivent le
   régime général (L. 634-2). Dans tous les cas ces trimestres sont attribués
   DANS un régime et non au-dessus d'eux : ils comptent donc aussi dans sa
   proratisation, pas seulement dans la décote tous régimes confondus.
3. **Minimum contributif** — réservé aux pensions liquidées AU TAUX PLEIN
   (L. 351-10). Deux durées le proratisent, et ce ne sont pas les mêmes : le
   montant de base suit la durée d'assurance acquise dans le régime, sa
   majoration au titre des périodes cotisées suit la seule durée cotisée
   (D. 351-2-2), et cette majoration demande en outre <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=TRIMESTRES_COTISES_MINIMUM_MAJORE)-->120<!--/--> trimestres cotisés
   tous régimes. Il se compare à la pension AVANT surcote, et la surcote,
   calculée sur cette pension, s'ajoute au minimum pour les pensions prenant
   effet depuis le 1er avril 2009 (D. 351-2-1, dernier alinéa) ; avant, elle
   entrait dans la pension comparée au minimum. Il est enfin écrêté de ce qui
   ferait dépasser le plafond de l'article L. 173-2 — plafond auquel se
   comparent les pensions personnelles, majorations pour enfants exclues.
4. **Minimum garanti** de la fonction publique (L. 17) — non pas un plancher
   proratisé mais un barème en escalier sur la durée de services : <!--chiffre:tenu(test_le_minimum_garanti_de_la_fonction_publique_est_servi)-->57,5<!--/--> % de la
   référence à quinze ans, <!--chiffre:tenu(test_le_minimum_garanti_de_la_fonction_publique_est_servi)-->95<!--/--> % à trente, la totalité à quarante. La référence
   est le traitement de l'indice majoré 227 au 1er janvier 2004, revalorisé
   comme les pensions depuis. Il n'est dû qu'au taux plein depuis la loi du
   9 novembre 2010, qui a aussi changé sa première marche : sous quinze ans de
   services, la référence est rapportée, trimestre par trimestre, à la durée
   qui ouvre le pourcentage maximum ; le quinzième de la marche de quinze ans
   par année ne reste qu'à l'invalidité, que le modèle ne sert pas, et à qui
   avait atteint l'âge d'ouverture de ses droits avant 2011.
5. **Surcote parentale** (L. 351-1-2-1) — <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:taux_par_trimestre*100?debut=2023)-->1,25<!--/--> % par trimestre cotisé
   dans l'année qui précède l'âge légal au-delà de la durée requise, quatre au
   plus, dès que l'âge légal atteint <!--chiffre:cellule(data/reference/legislation/surcote_parentale.csv:age_ouverture?debut=2023)-->63<!--/--> ans, à l'assuré qui détient au moins un
   trimestre de majoration pour enfants. C'est la contrepartie du recul de l'âge
   légal voulu par la loi du 14 avril 2023 : l'année de travail qu'elle impose à
   qui avait déjà sa durée ne rapportait rien, la surcote ordinaire ne comptant
   qu'au-delà de l'âge légal. Les deux se cumulent donc sans se recouvrir. Elle
   s'ouvre avec cet âge minimal : rien jusqu'à la génération 1964 ni pour les
   assurés nés au premier trimestre 1965, quatre trimestres au plus ensuite. La fenêtre est datée au mois, les trimestres de chaque année
   répartis sur ses mois. C'est le trimestre pour enfants qui ouvre le droit, et
   non le sexe.
6. **Majoration pour trois enfants et plus** — <!--chiffre:tenu(test_la_majoration_de_10_pour_cent_n_apparait_qu_a_trois_enfants)-->10<!--/--> %, davantage dans la fonction
   publique et dans la plupart des régimes spéciaux, qui ajoutent un
   supplément par enfant au-delà du troisième, calculée sur le montant DÉJÀ
   RELEVÉ par les minima, et plafonnée en euros à la complémentaire. À
   l'Agirc-Arrco, chaque point porte le taux de son année d'acquisition
   (accord du 17 novembre 2017, article 94) : la pension Arrco d'une
   non-cadre née en 1962 et entrée à vingt-deux ans se majore de <!--chiffre:tenu(test_la_majoration_agirc_arrco_suit_la_periode_d_acquisition)-->7,9<!--/--> %
   pour trois enfants, et non de dix pour cent.
7. **Minimum vieillesse** — allocation différentielle qui complète tout le
   reste, majorations comprises, jusqu'au barème d'une personne seule. Servie à
   partir de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, et toujours affichée comme une ligne séparée : ce n'est pas
   une pension mais une aide sociale, soumise à condition de ressources du
   foyer, à demande, et récupérable sur les successions. Le paramètre
   `minimum_vieillesse_dans_le_scenario_actuel` la retire d'un seul geste.

#### Le droit ouvre-t-il cette liquidation ?

Le modèle calculait une pension à n'importe quel âge sans jamais dire si la loi
ouvrait ce départ-là. Un salarié né en 1965 y liquidait à <!--chiffre:illustration()-->58<!--/--> ans une pension
décotée que le droit ne lui aurait pas servie du tout. La question est
maintenant posée, et sa réponse accompagne le montant : l'âge d'ouverture du
régime le plus précoce de la carrière, ou le **départ anticipé pour carrière
longue** de l'article L. 351-1-1 — cinq trimestres validés avant la fin de
l'année civile des seize, dix-huit, vingt ou vingt et un ans, et une durée
cotisée au moins égale à la durée requise.

Quand la liquidation n'est pas ouverte, le montant reste calculé : il faut bien
comparer les trois scénarios sur la même carrière. Mais il ne décrit alors
aucune pension que le système actuel servirait, et la restitution le dit.

### Scénario 2 — comptes notionnels rétroactifs

Compte ouvert à l'entrée dans la vie active, ou en 1941 si la carrière a commencé
avant. Toute la carrière est recalculée. C'est le scénario qui répond à
« qu'aurait été ma retraite si le système avait toujours été notionnel ».

Ce qu'on y porte est la **part salariale** de la cotisation — ce que l'assuré a
supporté lui-même, la même grandeur pour tous les statuts. La part de
l'employeur fait l'objet des scénarios 4 et 5.

### Scénario 3 — comptes notionnels à compter d'aujourd'hui

Les droits acquis à la bascule sont figés selon les règles actuelles, convertis
en capital notionnel d'ouverture, puis le compte fonctionne en notionnel au-delà.

La conversion des droits acquis inverse la formule de liquidation :

```
capital d'ouverture = pension de droits figés × G(âge de conversion, année de bascule)
```

Trois précisions importantes :

- les droits figés sont calculés **sans décote ni surcote d'âge** : on mesure des
  droits déjà ouverts, pas une liquidation anticipée ;
- **l'âge de conversion est un choix, pas une donnée**, et c'est le seul endroit
  du modèle où le passage aux comptes notionnels peut, à lui seul, retirer
  quelque chose à des droits déjà ouverts. Voir ci-dessous ;
- pour un assuré **déjà retraité** à la bascule, ce scénario renvoie sa pension
  actuelle inchangée. Ses droits sont intégralement acquis ; tout autre résultat
  serait dépourvu de sens.

#### L'âge de conversion des droits acquis

Le capital d'ouverture est obtenu en multipliant une pension par un diviseur,
puis il sera redivisé par le diviseur de l'âge réel de liquidation. Si les deux
diviseurs diffèrent, la conversion n'est pas neutre.

| `--conversion-acquis` | Diviseur pris à | Effet sur des droits déjà ouverts |
|---|---|---|
| `reference` (défaut) | l'âge de référence | abattement du rapport des diviseurs si l'assuré part avant cet âge |
| `liquidation` | l'âge de départ effectif | aucun : la conversion est neutre |

Pour un salarié né en 1975, entré à <!--chiffre:illustration()-->21<!--/--> ans et partant à <!--chiffre:illustration()-->62<!--/--> ans, l'âge de
référence est de <!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans : les droits acquis sont convertis au diviseur
`G(64, 2026)`, <!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=62&quoi=diviseur_conversion)-->23,66<!--/--> années, puis servis à `G(62, 2037)`,
<!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=62&quoi=diviseur_service)-->27,50<!--/--> années. L'écart entre les deux, environ <!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=62&quoi=ecart_diviseurs)-->16<!--/--> %, est retiré de
droits que le système actuel aurait servis sans décote — l'anticipation est
payée une seconde fois, sur le passé. La pension du scénario 3 passe de
<!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=62&quoi=pension)-->24 854<!--/--> € à <!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=62&conversion=liquidation&quoi=pension)-->27 464<!--/--> € par an lorsqu'on retient l'autre convention. Un
départ à l'âge de référence lui-même ne sépare pas les deux : le diviseur est
alors le même.

**Le défaut est celui qui fait dépendre le pot du seul passé**, et c'est la
raison de fond. Sur une carrière témoin — né en 1975, homme, salarié du privé
non cadre entré à <!--chiffre:illustration()-->21<!--/--> ans, au salaire moyen et à profil plat, soit trente années
cotisées avant la bascule et un droit figé de <!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=64&quoi=figee)-->19 052<!--/--> € par an —, le pot vaut
sous `reference` **<!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=64&quoi=pot)-->450 853<!--/--> € quel que soit l'âge de départ**. Sous
`liquidation`, le même passé vaudrait **<!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=60&conversion=liquidation&quoi=pot)-->539 966<!--/--> € pour un départ à <!--chiffre:illustration()-->60<!--/--> ans et
<!--chiffre:mesure(droits_acquis?generation=1975&debut=21&depart=67&conversion=liquidation&quoi=pot)-->416 821<!--/--> € pour un départ à <!--chiffre:illustration()-->67<!--/--> ans** : <!--chiffre:mesure(droits_acquis_variation?generation=1975&debut=21&conversion=liquidation&quoi=pot&de=67&a=60)-->30<!--/--> % d'écart pour un passé identique,
parce que le diviseur qui constitue le pot rétrécit avec l'âge. Un test tient
ces deux propriétés.

Cette phrase a longtemps dit l'inverse : que `liquidation` « seule respecte
véritablement les droits acquis ». C'était un excès. Les deux conventions
respectent quelque chose de différent — l'une le CAPITAL que le passé
représente, l'autre la RENTE ANNUELLE qu'il promettait —, et la mesure a
tranché entre elles : sous `liquidation`, le pot rétrécit avec l'âge à peu près
au rythme où les cotisations nouvelles le remplissent, si bien que sept années
de travail supplémentaires ne feraient monter le capital total que de <!--chiffre:mesure(droits_acquis_variation?generation=1975&debut=21&conversion=liquidation&quoi=capital&de=60&a=67)-->1,1<!--/--> %
contre <!--chiffre:mesure(droits_acquis_variation?generation=1975&debut=21&quoi=capital&de=60&a=67)-->28<!--/--> % aujourd'hui. Un compte notionnel promet qu'on retrouve ce qu'on
verse ; c'est cette promesse-là que le défaut tient. Le détail de la mesure est
sous « Ce qui est délibérément en bas » de `feuille_de_route.md`, à l'action 24,
abandonnée pour ce motif.

`liquidation` reste fournie en variante, et le modèle affiche la cascade de
calcul pour que l'écart soit visible plutôt que subi.

Dans les deux cas, l'écart de longévité entre l'année de bascule et l'année de
liquidation subsiste : `G(64, 2039)` dépasse `G(64, 2026)` parce que l'espérance
de vie progresse. C'est un effet de table, pas une pénalité d'âge, et il est
inhérent au principe même des comptes notionnels.

### Le périmètre du taux de cotisation

Les fiches de régime ne stockent pas la même grandeur selon le secteur, et rien
ne le disait :

| Secteur | Ce que porte `taux_cotisation_retraite` | Valeur 2023 |
|---|---|---|
| Privé (régime général + Agirc-Arrco) | total salarié **+ employeur** | <!--chiffre:mesure(taux_statut?regimes=regime_general|agirc_arrco&annee=2023)-->25,6<!--/--> % |
| Fonction publique, régimes spéciaux | retenue de l'agent **seule** | <!--chiffre:mesure(taux_statut?regimes=fonction_publique_etat&annee=2023)-->11,10<!--/--> % à l'État, <!--chiffre:mesure(taux_statut?regimes=sncf&annee=2023)-->10,85<!--/--> % à la SNCF, <!--chiffre:mesure(taux_statut?regimes=mines&annee=2023)-->8,05<!--/--> % aux mines |

Alimenter un compte notionnel avec ces deux grandeurs revient à comparer un
effort contributif complet à un demi-effort. À rémunération et carrière
identiques, un fonctionnaire affichait une pension notionnelle inférieure de
37 % à celle d'un salarié — écart qui ne traduisait aucune règle de retraite.

Le modèle a d'abord refermé cet écart par une **convention** : prêter au public
la part employeur du privé. Elle rendait les statuts comparables, mais au prix
d'un chiffre inventé, et elle interdisait de poser la question la plus simple —
combien l'assuré verse-t-il, et combien son employeur ? Deux séries permettent
aujourd'hui d'y répondre sans rien inventer.

#### `part_salariale` : qui paie quoi, dans les fiches

Chaque période de fiche porte désormais la fraction du taux que l'assuré
supporte lui-même. Le défaut, `1.0`, couvre deux cas où il n'y a rien à
partager : les **non-salariés**, dont la cotisation est intégralement
personnelle, et les périodes **`agent_seul`**, dont le taux est déjà la seule
retenue de l'agent. Toute autre période doit porter une valeur explicite, et
`scripts/verifier_donnees.py` échoue si l'une manque.

| Régime | Période | Part salariale | Origine |
|---|---|---:|---|
| Régime général | 1945-1971 | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=1945)-->34,88<!--/--> % | mesurée sur 1968-1971, OpenFisca ne remontant pas plus haut |
| Régime général | 1972-1982 | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=1972)-->33,43<!--/--> % | OpenFisca, moyenne de période |
| Régime général | 1983-1993 | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=1983)-->43,90<!--/--> % | idem |
| Régime général | 1994-2022 | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=1994&a=2011&stat=min)-->44,41<!--/--> à <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=1994&a=2011&stat=max)-->44,63<!--/--> % | idem |
| Régime général | 2023- | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=regime_general&champ=part_salariale&de=2023)-->44,66<!--/--> % | idem |
| Arrco, Agirc-Arrco | toutes | <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=arrco&de=1961&a=2018)-->40<!--/--> % | règle de répartition 40-60 (ANI du 17 novembre 2017, art. 38) |
| Ircantec, tranche 1 | 1971-2025 | <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=ircantec&de=1971&a=2017&assiette=tranche_1)-->40<!--/--> % | idem ; <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=ircantec&de=2026&assiette=tranche_1)-->39,9<!--/--> % depuis 2026 |
| Ircantec, tranche 2 | toutes | <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=ircantec&de=1971&a=2008&assiette=tranche_2_ircantec&stat=min)-->34<!--/--> à <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=ircantec&de=2009&a=2026&assiette=tranche_2&stat=max)-->35,64<!--/--> % | OpenFisca, moyenne de période |
| Agirc | 1947-1993 | <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=agirc&de=1947&a=1993)-->25<!--/--> % | OpenFisca : un quart, trois quarts |
| Agirc | 1994-2018 | <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=agirc&de=1994&a=2015&stat=min)-->30<!--/--> à <!--chiffre:mesure(fiche_regime?fichier=complementaires_prive&champ=part_salariale&regime=agirc&de=1994&a=2015&stat=max)-->38<!--/--> % | OpenFisca, moyenne de période |
| RAFP | 2005- | <!--chiffre:mesure(fiche_regime?fichier=fonction_publique&regime=rafp&champ=part_salariale&de=2005&a=2011)-->50<!--/--> % | décret 2004-569 : <!--chiffre:mesure(fiche_regime?fichier=fonction_publique&regime=rafp&champ=taux_cotisation_retraite&de=2005&a=2011)-->10<!--/--> %, moitié agent, moitié employeur |
| Assurances sociales, AVTS | 1930-1945 | <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=assurances_sociales&champ=part_salariale&de=1930)-->50<!--/--> % | loi du 30 avril 1930 : <!--chiffre:mesure(fiche_regime?fichier=base_prive&regime=assurances_sociales&champ=taux_cotisation_retraite&de=1930)-->8<!--/--> %, moitié ouvrier moitié patron |

La part est une **moyenne sur la période**, comme le taux lui-même : les fiches
sont découpées par période législative, et les parts salariale et patronale
bougent chacune à son rythme. Le contrôle de vraisemblance les confronte année
par année à OpenFisca, et le fait pour la répartition comme pour le taux.
**Pour le régime général et les fiches qui le suivent** — salariés agricoles,
cultes, Mayotte, Saint-Pierre-et-Miquelon — **et pour les non-salariés depuis
1973**, la moyenne ne sert plus qu'aux années d'avant 1967 : le taux et la part
de chaque année sont lus dans `regimes/taux_cotisation_annuels.csv` et
appliqués au chargement des fiches, période découpée année par année (voir
[`limites.md`](limites.md), « Le compte notionnel recevait une moyenne de
période »). Les lignes du tableau ci-dessus restent celles des fiches ; le
compte, lui, reçoit <!--chiffre:cellule(data/reference/regimes/taux_cotisation_annuels.csv:valeur*100?regime=regime_general&annee=1967&mesure=part_salariale)-->35,3<!--/--> % de part salariale en 1967 et <!--chiffre:cellule(data/reference/regimes/taux_cotisation_annuels.csv:valeur*100?regime=regime_general&annee=2024&mesure=part_salariale)-->44,7<!--/--> % en 2024.

**D'où vient chaque année de cette table.** Le régime général depuis 1982 et
les salariés agricoles depuis 1980 sont **certifiés** : leurs quatre mesures
sont lues dans l'article qui les fixe — article 2 du décret n° 81-1013 puis
`D. 242-4` du code de la sécurité sociale ; article 2 du décret n° 50-444 puis
`D. 741-35` du code rural —, rédaction par rédaction, par
`scripts/fetch/dila_legi_taux_cotisation.py`. Trois conventions les
accompagnent. Le **taux retenu est celui du 1er janvier**, comme partout
ailleurs dans le dépôt : un relèvement du 30 juillet 1986 ne commande que 1987,
et la réforme du 1er février 1991 que 1992. Le **renvoi d'un article à un autre
est suivi** et non recopié : c'est le II de `D. 741-35`, et non une convention
du dépôt, qui aligne les salariés agricoles sur le régime général depuis 2014 —
avant cette date, leur employeur payait un point de moins. Et un **décret qui
fixe le taux sans réécrire l'article** est lu dans la base JORF, à condition
d'être nommé et corroboré : c'est le cas du relèvement temporaire de <!--chiffre:illustration()-->0,2<!--/--> point
du 1er juillet 1987 au 30 juin 1988. Les années d'avant 1982 restent
transcrites d'OpenFisca-France, au niveau `haute` ; `limites.md` dit pourquoi
la base ne permet pas de les dater, et **ce qu'elles valent malgré tout** : la
DATE de chacune de leurs marches est vérifiée contre le *Journal officiel*, par
le décret que l'IPP — source amont d'OpenFisca — nomme en regard. Le décret du
30 juillet 1979, qui relève des taux « à titre exceptionnel » sur une fenêtre
couvrant 1980 et 1981, a longtemps fait tenir ces deux années pour fausses : il
ne touchait que la cotisation maladie, et leurs taux vieillesse sont justes.

**Le drapeau porte sur le STATUT, pas seulement sur le régime.** Un artisan
cotise au régime général, dont la fiche porte la répartition 41/59 d'un salarié.
Le taux y est le bon — un artisan verse à peu près ce que verse le couple
salarié-employeur — mais la répartition ne le concerne pas : lui paie tout.
`affiliations.yaml` marque donc `sans_employeur: true` les cinq statuts
concernés (artisan, commerçant, profession libérale, avocat, exploitant
agricole), et le modèle force alors la part à un.

#### La contribution employeur du public

Elle n'est dans aucune fiche, et le dépôt a longtemps soutenu qu'elle n'existait
pas avant 2006. C'était vrai de l'État, et faux du reste.

- La **CNRACL** est une caisse depuis 1947 : le taux versé par les employeurs
  territoriaux et hospitaliers est fixé par décret et publié depuis 1948 — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=cnracl&annee=1948)-->12<!--/--> %
  à l'origine, <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=cnracl)-->10,2<!--/--> % au creux de 1984, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=cnracl&annee=2025)-->34,65<!--/--> % en 2025, et le décret le
  porte jusqu'à <!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=cnracl)-->43,65<!--/--> % en 2028.
- L'**État** a bien un taux avant 2006, non pas appelé mais **reconstitué** :
  l'annexe « pensions » au PLF 2011 publie, page 26, une série de « taux de
  cotisation employeur implicite » remontant à 1995.
- Depuis 2006 le taux est appelé par décret, et le Service des retraites de
  l'État en publie l'historique : <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2006)-->49,90<!--/--> %, puis <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2013)-->74,28<!--/--> % de 2013 à 2024, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2025)-->78,28<!--/--> %
  en 2025, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2026)-->82,28<!--/--> % en 2026.
- La **SNCF** publie par arrêté les composantes T1 et T2 de la contribution de
  l'entreprise, de 2007 à 2018 ; et avant 2007 son taux est dans le décret qui
  fixe les cotisations des régimes spéciaux — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=sncf&annee=1992)-->28,44<!--/--> % de 1992 à 2006.
- La **RATP** et les **IEG** ont été adossés au régime général en 2005-2006 :
  l'employeur y verse ce que les mêmes salariés coûteraient à la CNAV et à
  l'Agirc-Arrco, et un arrêté annuel l'arrête — <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=ratp)-->17,94<!--/--> % à <!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=ratp)-->19,43<!--/--> % pour la RATP
  de 2007 à 2025, <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=ieg)-->24,25<!--/--> % à <!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=ieg)-->30,42<!--/--> % pour les IEG de 2005 à 2020.
- Les **mines** : <!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=mines)-->7,75<!--/--> % à la charge de l'exploitant, inchangé de 1984 à
  aujourd'hui, dans le décret d'organisation de la sécurité sociale minière.
- L'**Opéra national de Paris** et la **Comédie-Française** : <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=opera_de_paris&annee=1992)-->8,80<!--/--> % en 1992,
  <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=opera_de_paris&annee=2026)-->9,56<!--/--> % en 2026, dans le même décret que la SNCF d'avant 2007.

La série est dans `legislation/contribution_employeur_public.csv`. Quatre
conventions à connaître. L'**assiette ne change pas** : le taux du CAS porte sur
le traitement indiciaire brut et la NBI, à l'exclusion des primes — exactement
l'assiette `hors_primes` des fiches ; et pour les six régimes lus au *Journal
officiel*, c'est le même texte qui fixe la retenue de l'agent et la contribution
de l'employeur, sur la même assiette, ce qui rend leur somme lisible. Le **taux
retenu est celui du 1er janvier**, comme partout ailleurs dans le dépôt ; deux
abattements d'un mois y échappent volontairement, décembre 2009 et décembre
2013, qui soldent l'exercice budgétaire, et les arrêtés annuels de la RATP, des
IEG et de la SNCF y échappent aussi, parce qu'ils datent leur taux par
l'EXERCICE — « fixé à <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=ratp&annee=2024)-->19,43<!--/--> % pour l'exercice 2024 » — et non par une date
d'effet. Pour ceux-là, **c'est le taux définitif qui compte**, non le
provisionnel appelé d'avance : les deux diffèrent de six dixièmes de point pour
la SNCF en 2018. Enfin, **là où la série n'existe pas, le modèle le dit** :
avant 1992 pour la SNCF, avant 1995 pour l'État, avant 1948 pour la CNRACL,
avant 2007 pour la RATP, après 2020 pour les IEG, et pour les sept régimes
spéciaux qui n'en publient aucune, la part patronale est estimée par l'effort
d'un salarié du privé de la même année, la fiabilité retombe à `estimee`, et le
nombre d'années concernées est affiché sous la simulation.

**Ces taux sont ceux de l'employeur, non ceux de l'équilibre.** Lu dans les
décrets le 15 septembre 2026 : trois de ces régimes reçoivent aussi de l'État une contribution qui n'est pas une cotisation
d'employeur et n'entre donc pas dans la série : les droits spécifiques que
l'État finance pour la RATP jusqu'à 45 000 agents, les 22 % des salaires qu'il
verse au régime minier — près de trois fois ce que verse l'exploitant —, la
subvention de l'Opéra. C'est la convention déjà retenue pour la SNCF, dont la
somme T1 + T2 laisse dehors la subvention d'équilibre. La ligne de l'État est la
seule exception : son taux est fixé pour équilibrer le compte d'affectation
spéciale, et il est donc l'un et l'autre.

**Une réserve propre aux mines.** Lu le 15 septembre 2026 : depuis 1991,
l'exploitant doit aussi 1,6 % sur
la TOTALITÉ des rémunérations, en plus des 7,75 % dus dans la limite du plafond.
La fiche du régime minier a une assiette plafonnée, où ces 1,6 % n'ont pas de
place : ils ne sont pas portés, et la contribution de l'employeur minier est
donc, après 1991, un plancher.

La marche 2005 → 2006, où le taux de l'État passe de <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2005)-->59,4<!--/--> % à <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?regime=fonction_publique_etat&annee=2006)-->49,9<!--/--> %, n'est pas
une baisse du coût des droits : c'est un changement de mesure, le périmètre du
taux implicite étant plus étroit que celui du CAS.

### Scénarios 4 et 5 — les mêmes, part patronale comprise

Ce sont **exactement les scénarios 2 et 3**, à une différence près et une
seule : ce qui alimente le compte.

| | Point de départ du compte | Ce qui y est porté |
|---|---|---|
| **2** | origine de la répartition | la part **salariale** seule |
| **3** | année de bascule, droits acquis figés | la part **salariale** seule |
| **4** | origine de la répartition | salariale **et patronale** |
| **5** | année de bascule, droits acquis figés | salariale **et patronale** |

Le 4 se lit donc contre le 2, le 5 contre le 3, et l'écart mesure une chose à la
fois : ce que verse l'employeur. Pour un **non-salarié**, qui n'en a pas, les
quatre scénarios se réduisent à deux — et c'est le test qui le vérifie.

Le paramètre est `part_cotisation`.
Une troisième valeur, `totale_alignee`, conserve l'ancienne convention — part
patronale du public empruntée au privé — comme contrefactuel : elle répond à
« à effort contributif égal, que donnerait la règle notionnelle ? », question
légitime mais différente, et sous elle un fonctionnaire et un salarié de même
rémunération retrouvent exactement la même pension.

Un second paramètre, `contribution_etat`, ne joue que sous `totale` et que pour
l'État. Son taux n'est pas une cotisation mais un taux d'équilibre : il paie
toutes les pensions de l'année, celles que l'agent n'acquiert pas en cotisant
comprises. `retraite_seule`, le défaut depuis le 24 septembre 2026, n'en porte
donc au compte que la part que la Cour des comptes rattache à la retraite de
l'agent lui-même, parce que ce qui n'est pas contributif se finance par
l'impôt et non par le compte ; pour un agent de l'État, l'écart du 4 au 2
mesure cette part, et non tout ce que l'employeur verse. `entiere` porte le
taux versé tel quel, et répond à la question du scénario 4 prise au pied de la
lettre : « et si tout ce qui a été consacré aux pensions avait été porté au
compte des actifs ? ». La part de la Cour vient du tableau n° 15 de son rapport
du 22 septembre 2026 : <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=civils&poste=retraite_stricto_sensu)-->44,1<!--/--> % pour un civil et <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=militaires&poste=retraite_stricto_sensu)-->51,2<!--/--> % pour un militaire en 2025, sur
les <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=fonction_publique_etat)-->78,28<!--/--> % versés pour un civil. Les autres années reçoivent la même
proportion du taux de l'année, qui est une hypothèse — la fiabilité retombe à
`estimee` —, prise sur le taux de chaque population. Celui du militaire est le
sien, <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2025)-->126,07<!--/--> % de la solde en 2025, lu dans les décrets qui le fixent
(`legislation/contribution_employeur_militaires.csv`), et sa part en est
<!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=militaires&poste=retraite_stricto_sensu)-->51,2<!--/--> sur <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2025)-->126,07<!--/-->. Avant 2006, il n'a pas de taux propre : il reçoit le taux
implicite de tout l'État, dont sa part est <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=militaires&poste=retraite_stricto_sensu)-->51,2<!--/--> sur <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=fonction_publique_etat)-->78,28<!--/-->, ce qui garde entre
militaire et civil le rapport que la Cour mesure entre leurs deux parts.
`ConstructeurCompte.parts_retraite_seule` la calcule,
`legislation/contribution_etat_retraite_seule.csv` porte le tableau.

#### Après la bascule, le régime unique tranche

À compter de la bascule il n'y a plus ni fonction publique ni régimes spéciaux :
un seul régime, dont le taux est la somme des taux du statut pivot privé (§7).
Il en **hérite la répartition** salarié/employeur — <!--chiffre:mesure(fusion?champ=taux_cotisation_salarie)-->10,45<!--/--> % de part salariale
sur <!--chiffre:mesure(fusion?champ=taux_cotisation_retraite)-->25,83<!--/--> % en 2026 — et c'est elle qui sépare le scénario 5 du scénario 3 après
la bascule. Il n'y a donc, après la bascule, aucune contribution publique à
retrouver décret par décret : la réforme l'a remplacée.

Une exception, et une seule : un assuré qui n'avait pas d'employeur n'en gagne
pas un en changeant de régime. Un artisan cotise seul avant la bascule ; il
cotise seul après, à un taux plus élevé — c'est déjà ce que dit le modèle (§7),
et la répartition doit le suivre.

#### Ce que ces scénarios ne disent pas

Les taux employeur publics sont des taux d'**équilibre**, fixés pour que le
compte tombe juste. Un taux de <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82,28<!--/--> % ne signifie pas qu'un fonctionnaire
acquiert <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82<!--/--> % de son traitement en droits nouveaux : il signifie qu'il faut
aujourd'hui cette contribution pour payer les pensions d'aujourd'hui,
démographie et engagements hérités compris. Les porter à un compte notionnel
répond à une question précise :

> qu'aurait donné un compte notionnel si **tout ce qui a été consacré aux
> pensions** avait été porté au compte des actifs ?

Et à elle seule. Ce n'est pas une proposition de réforme, pas plus que le
scénario 2 ne l'est.

Une troisième lecture existe — fixer un **taux d'acquisition commun** à tous, le
surplus restant une contribution de transition qui n'ouvre aucun droit — et le
moteur sait la calculer : `source_cotisations = taux_uniforme`. Elle ne figure
pas parmi les scénarios 2 à 5 parce qu'elle ne répond pas à la même question :
elle ne mesure plus ce qui a été versé, mais ce qu'une réforme choisirait de
reconnaître. C'est précisément la question que pose le scénario 6.

### Scénario 6 — la proposition libérale : un taux unique dès la bascule, un pilier capitalisé, et une garantie vieillesse

Le scénario 6 est la proposition du Parti libéral français. C'est **exactement
le scénario 4** — compte rétroactif depuis l'origine de la répartition,
cotisation salariale et patronale confondues, même âge de référence, même
indexation, même coefficient de conversion — à quatre différences près, qui
sont les quatre termes de la proposition : le taux unique, la garantie
vieillesse, le pilier capitalisé, et l'âge légal de départ.

**Un taux unique de <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> %, à compter de la bascule.** Parts salariale et
patronale additionnées, le même pour tous les statuts, prélevé une fois sur la
rémunération — comme le taux d'acquisition commun ci-dessus, mais seulement à
partir de l'année de bascule (`taux_cotisation_liberal`,
`source_cotisations = taux_historiques_puis_uniforme`). Avant la bascule, rien
ne change : ce qui a été cotisé sous le système actuel est porté au compte tel
qu'il a été prélevé, aux taux réels de chaque régime, salariale et patronale
confondues — c'est le scénario 4. Une personne née en 1975, entrée à <!--chiffre:illustration()-->21<!--/--> ans et
partie à <!--chiffre:illustration()-->64<!--/--> ans, cotise donc aux taux réels de chacune de ses années
jusqu'à la bascule, puis à <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % de <!--chiffre:mesure(parametre?nom=annee_bascule)-->2026<!--/--> à son départ, en 2039. Qui a
liquidé avant la bascule n'a aucune année à <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % : son compte est
celui du scénario 4, et seule la garantie peut l'en séparer. Pour les années
d'après, un fonctionnaire, un artisan et un salarié du privé de même
rémunération acquièrent le même capital : les statuts qui cotisaient plus de
<!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % descendent sous le scénario 4, ceux qui cotisaient moins remontent,
d'autant plus que la carrière est récente.

**Une garantie vieillesse, avancée par l'impôt.** Elle remplace l'ASPA et en
garde le principe — une allocation différentielle, qui porte les ressources à
un plancher — et l'âge, <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans. Elle en change deux choses. La première est
que le plancher est **individualisé** : chaque personne est comparée au sien,
sans que la pension du conjoint entre dans le calcul.

| | Plancher mensuel, en euros de <!--chiffre:mesure(parametre?nom=annee_euros_garantie_vieillesse)-->2026<!--/--> |
|---|---|
| Garantie de base, par personne | <!--chiffre:mesure(parametre?nom=garantie_vieillesse_mensuelle)-->800<!--/--> € |
| Allocation d'isolement, pour qui vit seul | + <!--chiffre:mesure(parametre?nom=allocation_isolement_mensuelle)-->250<!--/--> € |
| **Personne seule** | **<!--chiffre:mesure(garantie_foyer?quoi=plancher&personnes=1)-->1 050<!--/--> €** |
| **À deux** | **<!--chiffre:mesure(parametre?nom=garantie_vieillesse_mensuelle)-->800<!--/--> € chacun, soit <!--chiffre:mesure(garantie_foyer?quoi=plancher&personnes=2)-->1 600<!--/--> €** |

Ce que l'individualisation change, à montants égaux, sur les couples de la
proposition :

| Pensions mensuelles des deux personnes | Plancher du foyer, comme l'ASPA | Garantie individualisée |
|---|---:|---:|
| <!--chiffre:illustration()-->300<!--/--> € et <!--chiffre:illustration()-->300<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=300&base=foyer)-->1 000<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=300)-->1 000<!--/--> € |
| <!--chiffre:illustration()-->300<!--/--> € et <!--chiffre:illustration()-->1 500<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=1500&base=foyer)-->0<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=1500)-->500<!--/--> € |
| <!--chiffre:illustration()-->900<!--/--> € et <!--chiffre:illustration()-->900<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=900&conjoint=900&base=foyer)-->0<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=900&conjoint=900)-->0<!--/--> € |
| <!--chiffre:illustration()-->300<!--/--> € et <!--chiffre:illustration()-->5 000<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=5000&base=foyer)-->0<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&conjoint=5000)-->500<!--/--> € |
| personne seule, <!--chiffre:illustration()-->300<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300&base=foyer)-->750<!--/--> € | <!--chiffre:mesure(garantie_foyer?pension=300)-->750<!--/--> € |

La première colonne applique au foyer les montants de la garantie, comme l'ASPA
applique les siens ; ceux de l'ASPA en sont proches — <!--chiffre:cellule(data/reference/legislation/minimum_vieillesse.csv:valeur/12?annee=2026)-->1 043,59<!--/--> € par mois
pour une personne seule en 2026, à quelques euros du plancher d'une personne
seule —, si bien que l'écart entre les deux colonnes est celui de la seule
individualisation. Regarder le foyer, c'est
opposer <!--chiffre:illustration()-->1 800<!--/--> € de ressources au plafond du couple, <!--chiffre:mesure(garantie_foyer?quoi=plancher&personnes=2)-->1 600<!--/--> € : à
<!--chiffre:illustration()-->300<!--/--> € et <!--chiffre:illustration()-->1 500<!--/--> €, le couple le dépasse et ne reçoit rien. La
garantie regarde chacun : le premier reçoit <!--chiffre:mesure(parametre?nom=garantie_vieillesse_mensuelle)-->800<!--/--> − <!--chiffre:illustration()-->300<!--/--> =
<!--chiffre:mesure(garantie_complement?pension=300)-->500<!--/--> €, le second rien. Les deux colonnes
sont calculées par la règle que le moteur applique,
`test_la_garantie_reproduit_le_tableau_de_la_proposition` rejoue la seconde
ligne à ligne, et la page de simulation la recalcule sous les yeux du lecteur.

Les montants sont fixés en euros de <!--chiffre:mesure(parametre?nom=annee_euros_garantie_vieillesse)-->2026<!--/--> (`annee_euros_garantie_vieillesse`) et
ramenés à l'année de liquidation par l'indice des prix — la convention déjà
retenue pour l'ASPA du scénario 1 entre deux ancres de son barème. La
situation de foyer est un paramètre (`situation_foyer`, `seul` par défaut comme
pour l'ASPA du scénario 1, de sorte que les deux planchers se comparent) ; elle
ne joue que sur l'allocation d'isolement.

La garantie est servie **en dernier**, après la pension contributive, et gardée
à part dans le résultat (`garantie_vieillesse`, avec chacune de ses étapes) :
c'est la seule ligne des scénarios notionnels qui ne vienne pas d'une
cotisation. Elle est **avancée par l'impôt** et non par les cotisations, et la
page Coût la compte à part, pour que l'on voie ce que ce scénario retire aux
cotisations et ce qu'il demande au contribuable.

**La seconde chose qu'elle change : c'est une avance.** Ce qu'elle verse est une
créance de l'État, qui porte intérêt et se reprend sur la succession dès le
premier euro, là où l'ASPA n'est récupérée qu'au-delà d'un seuil d'actif net —
et jamais au-delà de ce que la succession contient, les héritiers ne payant pas
de leur poche. La page Coût la donne donc en trois lignes, brute, reprise et
nette. Elle se demande, enfin, comme l'ASPA : le programme retient que
<!--chiffre:mesure(parametre?nom=taux_recours_garantie)-->50<!--/--> % des ayants droit la réclament (`taux_recours_garantie`), l'hypothèse
que la DREES mesure sur l'ASPA. La sous-section « La garantie du scénario 6,
mesure par mesure » de `limites.md` dit comment chacune de ces grandeurs est
établie.

Une réserve, et une méthode. Le modèle liquide et s'arrête : un assuré parti à
<!--chiffre:illustration()-->62<!--/--> ans avant la bascule avec une petite pension reçoit la garantie à <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, et la page de
simulation dit l'année et le montant. Mais une allocation différentielle ne se
chiffre pas sur <!--chiffre:mesure(grille?quoi=cas_types)-->13<!--/--> carrières, parce que son coût est tout entier celui de
la queue basse de la distribution des pensions, et une grille choisie pour
couvrir les configurations du système n'en a pas. La masse de garantie de la
page Coût n'est donc pas tirée des cas types : le barème est appliqué, année
par année, à la distribution que publie l'échantillon interrégimes de retraités
de la DREES, et la grille ne sert qu'à dire de combien cette distribution
bouge — la pension moyenne que la garantie regarde, compte notionnel et rente
capitalisée réunis à partir de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, rapportée à la pension moyenne du
système actuel l'année de l'enquête, un rapport par sexe, les femmes perdant
davantage de droits non cotisés (`GarantieDistribution` dans `cout.py`,
`rapport_deplacement_sexe` dans les paramètres). La forme de la distribution
est tenue constante, le passé comme l'avenir. Elle est celle des retraités qui
RÉSIDENT en France : la garantie remplace l'ASPA et en garde la condition de
résidence (article L. 815-1), quand l'enquête compte aussi les retraités partis
à l'étranger — <!--chiffre:cellule(data/reference/macro/pensions_residence.csv:valeur?annee=2020&residence=etranger&indicateur=effectifs&sexe=ensemble)-->905<!--/--> milliers en 2020, et presque tous sous le plancher,
leur carrière française ayant été courte. L'enquête ne publie pas leur
distribution par tranches, mais leurs quantiles et leur effectif : le dépôt
retire de chaque tranche ce que leur répartition y met (`DistributionPensions`,
`residence="france"`), et les déciles qui en sortent retombent à une vingtaine
d'euros près sur ceux qu'elle publie pour les résidents en France. Jusqu'au 23
septembre 2026, la garantie servait les uns et les autres, et son coût s'en
trouvait gonflé d'un cinquième. Sur le passé, la page Coût ne
voit pas non plus le taux unique — aucune pension servie avant la bascule n'a
une année cotisée à <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % — et la courbe du scénario 6 y est celle du
scénario 4 plus la garantie ; c'est d'ici 2070 que le taux se voit.

#### Le pilier de capitalisation obligatoire

C'est le troisième terme de la proposition, et le seul endroit du modèle où de
l'argent est réellement placé. Tout ce qui suit décrit un compartiment
**distinct** du compte notionnel : il n'entre pas dans le capital notionnel, il
n'est pas divisé par le même capital, il n'apparaît jamais additionné en
silence à une pension de répartition. Le code le tient à part
(`moteur/capitalisation.py`), le résultat le porte à part
(`ResultatNotionnel.capitalisation`), et la somme des deux n'existe que sous un
nom qui le dit (`pension_totale`).

**Ce qui l'alimente.** DEUX cotisations, prélevées à compter de l'année de
bascule (`annee_bascule`, <!--chiffre:mesure(parametre?nom=annee_bascule)-->2026<!--/-->) sur la **même assiette** que la
cotisation notionnelle de l'année, et **en plus** d'elle.

La première est obligatoire : <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> % (`taux_capitalisation_obligatoire`). L'effort
contributif monte donc d'autant, il n'est pas redéployé — la répartition
reçoit toujours ses <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> %, et le compte notionnel du scénario 6 est identique,
au centime, à ce qu'il serait sans le pilier ; un test l'exige. Le total imposé
reste alors inférieur à celui d'aujourd'hui : <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> + <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> = <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal+taux_capitalisation_obligatoire)-->23<!--/--> %, contre <!--chiffre:mesure(fiche?quoi=total&exemple=salaire_moyen)-->28<!--/--> % pour
un salarié du privé au salaire moyen.

La seconde est **volontaire** : <!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> % encore (`taux_capitalisation_volontaire`),
et c'est la seule pièce du modèle que personne n'impose. Elle remet au compte
les <!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> points que la proposition rend, de sorte que l'effort revienne à
<!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> + <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> + <!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> = <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal+taux_capitalisation_obligatoire+taux_capitalisation_volontaire)-->28<!--/--> %, c'est-à-dire à ce qu'il est déjà. Ce n'est pas une
prévision de comportement mais une **convention de comparaison** : sans elle,
le site opposerait deux systèmes qui ne coûtent pas le même prix, et une partie
de l'écart de pension se lirait comme un effet des règles alors qu'elle
viendrait d'un effort moindre. `capitalisation_volontaire=False` la retire, et
la proposition redevient <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> + <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> ; un test le vérifie.

Le pilier ne distingue les deux nulle part ailleurs qu'en **proportion** : même
assiette, même échelle de maturités, mêmes frais, même table de mortalité. Tout
ce qu'il produit étant exactement proportionnel au taux — les frais sont des
pourcentages, l'allocation ne dépend que de l'horizon, aucun seuil n'intervient
—, le capital et la rente se partagent au prorata des deux taux, et
`Capitalisation.part_volontaire` suffit à le dire. Un test compare ce partage
au calcul complet fait à taux réduit.

Deux endroits les séparent, et deux seulement. Sur la **fiche de paie**, les
<!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> points volontaires n'y sont pas : la fiche de la proposition s'arrête aux
<!--chiffre:mesure(fiche?quoi=total&exemple=salaire_moyen&systeme=proposition)-->23<!--/--> points imposés, partagés avec l'employeur, et le net qu'elle
affiche est le net plein. Le placement des <!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> points rendus est chiffré
sous ce net, sur la même assiette que le pilier, et porté en entier par
l'assuré — personne ne cofinance une épargne qu'on décide seul —, si bien
qu'activer la cotisation volontaire ne change ni le coût du travail, ni le
brut, ni la CSG qui est assise dessus, ni le net : seulement ce qui reste à
qui place, d'exactement son montant. Dans les **résultats**, la rente qu'elle
sert est écrite sur sa propre ligne, partout où le total du scénario 6 paraît,
et ce total est annoncé comme un plafond — « retraite jusqu'à » — avec le
plancher écrit sous lui : sans quoi le site montrerait à la fois le salaire de
qui ne place rien et la pension de qui place.

Les années antérieures à la bascule ne versent rien, et qui a liquidé avant n'a
pas de pilier du tout.

Prendre la même assiette n'est pas une commodité : c'est ce qui interdit au
pilier de se construire une base à lui, plafonnée autrement, servie les années
d'interruption, ou pleine l'année du départ. Il lit les assiettes que le compte
notionnel a retenues, et rien d'autre.

**Où il est placé.** Sur des titres sans risque portés jusqu'à leur échéance,
et choisis pour tomber l'année du départ. La courbe retenue est la structure par terme des souverains **AAA de la zone
euro**, estimée et publiée chaque jour ouvré par la BCE
(`data/reference/macro/courbe_taux_sans_risque.csv`, jeu `YC`, modèle de
Svensson, composition continue). L'OAT française rend davantage — <!--chiffre:illustration()-->51<!--/--> points de
base au dix ans le 17 septembre 2026 — mais cet écart rémunère un risque de
crédit, qu'un régime obligatoire promettant une rente ne peut pas compter comme
un rendement acquis. Le choix est donc **prudent**, et il réduit la rente
affichée.

Les versements futurs ne se placent pas aux taux comptants d'aujourd'hui, mais
aux **taux forward implicites** de la même courbe :

```
f(T₁, T₂) = (z(T₂)·T₂ − z(T₁)·T₁) / (T₂ − T₁)
```

où `z(T)` est le taux zéro-coupon continu à l'horizon `T`. Le taux annuel
employé est `exp(f) − 1`. Cette construction dispense le modèle d'une prévision
de taux : le forward n'est pas une opinion, il est arbitré par la courbe
elle-même. Un test vérifie l'identité qui le définit — dix ans puis dix ans
valent vingt ans, à 10⁻¹² près.

Ce qu'elle suppose doit être dit : prendre le forward pour le taux futur est
l'**hypothèse des anticipations pures**, qui néglige la prime de terme. Quand
la courbe monte, le forward excède le taux futur moyen attendu, et le pilier
s'en trouve légèrement flatté. Au-delà de la dernière maturité publiée
(<!--chiffre:mesure(constante?de=retraite_notionnelle.moteur.capitalisation&nom=MATURITE_MAXIMALE)-->30<!--/--> ans), le taux zéro-coupon est prolongé à plat, et tout placement qui
en dépend est déclaré `estimee`.

Elle a un second effet, moins visible et décisif pour ce qui suit : sous les
anticipations pures, **le découpage des maturités n'a aucune conséquence**.
Découper `[t, T]` en un trente ans, en trois dix ans ou en quinze deux ans
accumule exactement `exp(z(T)·T − z(t)·t)` dans les trois cas, parce que c'est
précisément ce que l'arbitrage impose au forward. Les frais n'y changent rien :
un prélèvement annuel de `g` multiplie une ligne par `(1 − g)` autant de fois
qu'elle passe d'années dans l'enveloppe, et ce nombre-là ne dépend pas non plus
du découpage. Un test l'exige sur quatre règles d'allocation que tout sépare,
et il conclut **à <!--chiffre:tenu(test_sous_les_anticipations_pures_l_echelle_est_sans_effet)-->0,01<!--/--> € près, sur <!--chiffre:mesure(allocation?quoi=annees)-->31<!--/--> ans de versements**.

`Parametres.prime_terme_trente_ans` ouvre cette porte, et c'est le seul réglage
sous lequel l'allocation pèse. Il décompose le taux observé en `z(T) = z*(T) +
φ(T)`, où `z*` est la moyenne des taux courts attendus et `φ` le supplément
exigé pour immobiliser son argent `T` années — proportionnel à la maturité,
plafonné à trente ans, nul par défaut. Les forwards se calculent alors sur `z*`,
et la prime de la maturité **achetée** se rajoute au résultat, si bien qu'un
placement comptant rend toujours le taux coté du jour : le paramètre ne corrige
que ce qui n'est pas encore acheté. **Le site publie à `0`**, sous les
anticipations pures.

**Trois régimes de taux, un réglage.** Le site propose ce paramètre comme un
réglage des règles du calcul, « Taux futurs du pilier capitalisé », qui voyage
dans l'adresse et s'applique au simulateur comme aux pages qui agrègent, à côté
de celui des frais : `Parametres.sous_regime_taux` définit une fois les trois
régimes, et le portage les applique sans les redéfinir.

| Réglage | Prime à <!--chiffre:mesure(constante?de=retraite_notionnelle.donnees.taux&nom=MATURITE_PRIME)-->30<!--/--> ans | Ce qu'il dit |
|---|---:|---|
| `forwards` (défaut) | 0 | Les taux à terme de la courbe, tels qu'elle les implique |
| `prime` | <!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_MILIEU&echelle=100)-->0,50<!--/--> pt | La prime retirée, au milieu de la fourchette |
| `prime_haute` | <!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_HAUTE&echelle=100)-->1<!--/--> pt | La prime retirée, au haut de la fourchette |

Il ne traverse que la courbe du PILIER (`Simulateur.courbe_taux_pilier`). Celle
que lit le taux d'emprunt de la dette du chiffrage reste la courbe publiée,
sans retouche : portées sur une courbe commune, ces primes déplaçaient le stock
de dette de tous les systèmes, jusqu'à dix points de PIB sur le système actuel,
qui n'a pas de pilier du tout. Un test tient la séparation.

Le menu ne sert pas qu'à borner une incertitude : il est le seul endroit d'où
l'on voie que **l'allocation des maturités ne vaut rien sous le réglage par
défaut**. Un lecteur qui bascule sur `prime` voit la rente baisser — c'est le
prix de l'hypothèse — et voit du même coup apparaître l'écart entre
l'adossement et un roulement, qui était nul l'instant d'avant.

**L'adossement à l'horizon.** Chaque versement achète **une seule** maturité,
celle qui arrive à échéance l'année du départ :

```
maturité = min(h, 30)
```

où `h` est le nombre d'années restant jusqu'à la liquidation et `30` le bout de
la courbe publiée. Deux propriétés la ferment, et un test tient chacune. Aucune
maturité ne dépasse `h` : un titre arrivant à échéance après le départ devrait
être vendu avant terme, donc à un prix qui n'est plus sans risque. Et aucune
n'arrive à échéance **avant** `h` tant que la courbe couvre l'horizon : il n'y a
alors rien à replacer, donc aucun taux futur à deviner. Les trente maturités de
la BCE étant toutes cotées, l'adossement n'interpole ni n'extrapole en deçà de
trente ans.

| Années avant le départ | Maturité achetée |
|---:|---|
| 40 | le bout de courbe, <!--chiffre:mesure(constante?de=retraite_notionnelle.moteur.capitalisation&nom=MATURITE_MAXIMALE)-->30<!--/--> ans, puis ce qui reste à l'échéance |
| <!--chiffre:mesure(constante?de=retraite_notionnelle.moteur.capitalisation&nom=MATURITE_MAXIMALE)-->30<!--/--> | <!--chiffre:mesure(constante?de=retraite_notionnelle.moteur.capitalisation&nom=MATURITE_MAXIMALE)-->30<!--/--> ans, qui tombe l'année du départ |
| 20 | <!--chiffre:illustration()-->20<!--/--> ans, qui tombe l'année du départ |
| 10 | <!--chiffre:illustration()-->10<!--/--> ans, qui tombe l'année du départ |
| 5 | <!--chiffre:illustration()-->5<!--/--> ans, qui tombe l'année du départ |
| 2 | <!--chiffre:illustration()-->2<!--/--> ans, qui tombe l'année du départ |

**Ce que cette règle a remplacé, et pourquoi.** Jusqu'en septembre 2026, le
pilier pratiquait une échelle de trois maturités — 2, 10 et 30 ans — glissant du
long vers le court à l'approche du départ, aucune ligne ne dépassant les trois
quarts du versement. Deux raisons l'ont fait tomber.

La première est qu'elle **ne déplaçait rien** : c'est l'identité ci-dessus, et
la bascule vers l'adossement l'a confirmée sur les témoins du portage — capital
et rente identiques au centime sur l'ensemble des cas de référence, seule
l'espérance de capital transmis bougeant de +0,19 %, parce qu'elle seule dépend
des encours **intermédiaires**. L'échelle était donc un paramètre libre sans
effet, qu'on pouvait accorder des heures durant sans déplacer un euro de rente.

La seconde est qu'elle importait un raisonnement qui ne vaut pas ici.
Raccourcir la maturité à l'approche du départ « dé-risque » un portefeuille
d'**actions**, dont le prix de vente est incertain. Le pilier n'en détient pas :
il doit un capital à une **date**, et l'actif sans risque d'une dette datée est
le zéro-coupon qui tombe ce jour-là. Rouler du court jusqu'au départ n'est pas
plus prudent — c'est un pari répété sur le taux de chaque replacement, un risque
de réinvestissement que la règle **créait** au lieu de le couvrir, et que le
modèle ne chiffrait nulle part. L'adossement le ramène à zéro tant que la courbe
couvre l'horizon, et à un seul replacement au-delà de trente ans.

Les deux raisons pointent dans le même sens, et la prime de terme donne le
chiffre : à `prime_terme_trente_ans = 0,005` — le milieu de la fourchette que la
littérature retient, voir `docs/limites.md` —, sur la carrière de ce test,
<!--chiffre:mesure(allocation?quoi=annees)-->31<!--/--> ans de versements jusqu'à un départ en 2060, l'adossement rend
**<!--chiffre:mesure(allocation?contre=echelle)-->1,6<!--/--> % de capital de plus** que l'échelle glissante —
<!--chiffre:mesure(allocation?contre=echelle&quoi=rente)-->7<!--/--> € de rente mensuelle — et
**<!--chiffre:mesure(allocation?contre=roule)-->6,2<!--/--> % de plus** qu'un roulement à un an. C'est ce que l'allocation vaut, et elle ne vaut que cela :
sans prime de terme, les trois règles donnent le même euro.

**La convention de date, et pourquoi c'est celle du compte notionnel.** Le
versement d'une année est crédité à la **fin** de cette année : il rapporte de
l'année suivante jusqu'à l'année de liquidation incluse, soit exactement les
années où `Indexation.coefficient` revaloriserait la cotisation notionnelle du
même millésime. Sans cette symétrie, l'écart entre les deux compartiments
contiendrait une année de rendement offerte à l'un des deux, et le lecteur la
prendrait pour un effet de la capitalisation. Sur une courbe plate, le capital
admet alors une forme close que les tests vérifient :

```
K = Σ_a  V_a (1 − f_versement) × [(1 + r)(1 − f_gestion)]^(L − a)
```

**Ce qu'il coûte.** Quatre prélèvements, aux **vraies moyennes du marché** du
PER individuel en 2025, mesurées par l'Observatoire des produits d'épargne
financière (CCSF, Banque de France) sur les remises de l'ACPR, support en
euros, lues sur le rapport lui-même et confrontées par
`scripts/fetch/opef_frais_per.py` : <!--chiffre:mesure(parametre?nom=frais_versement_capitalisation)-->1,09<!--/--> % sur chaque versement et <!--chiffre:mesure(parametre?nom=frais_gestion_capitalisation)-->0,76<!--/--> % par
an sur l'encours, moyennes pondérées par les primes et par l'encours ; <!--chiffre:mesure(parametre?nom=frais_arrerages_capitalisation)-->0,99<!--/--> %
sur chaque arrérage de rente, moyenne sur tous les assureurs déclarants et non
sur les seuls neuf sur vingt qui facturent (<!--chiffre:valeur(data/reference/macro/frais_epargne_retraite.yaml:frais.arrerages.valeur*100)-->2,20<!--/--> %, médiane nulle) ; et
<!--chiffre:mesure(parametre?nom=frais_encours_rente_capitalisation)-->0,52<!--/--> % par an sur la réserve qui porte la rente, un frais que l'OPEF ne mesure
pas et que le rapport du CCSF de 2021 relevait sur <!--chiffre:valeur(data/reference/macro/frais_epargne_retraite.yaml:distributions.encours_de_rentes_non_modelise.ccsf_2021_contrats_facturant)-->22<!--/--> contrats sur <!--chiffre:valeur(data/reference/macro/frais_epargne_retraite.yaml:distributions.encours_de_rentes_non_modelise.ccsf_2021_contrats_panel)-->34<!--/-->, de
<!--chiffre:valeur(data/reference/macro/frais_epargne_retraite.yaml:distributions.encours_de_rentes_non_modelise.minimum_annuel*100)-->0,60<!--/--> à <!--chiffre:valeur(data/reference/macro/frais_epargne_retraite.yaml:distributions.encours_de_rentes_non_modelise.maximum_annuel*100)-->1<!--/--> % par an (`data/reference/macro/frais_epargne_retraite.yaml`).

**Ils baissent, par paliers, et d'abord sur les nouveaux dépôts.** Partout où
une épargne retraite obligatoire existe, les frais sont tombés bien au-dessous
de ceux d'un produit vendu au détail, et par à-coups : plafond de <!--chiffre:illustration()-->0,75<!--/--> % au
Royaume-Uni en 2015 (<!--chiffre:illustration()-->0,48<!--/--> % constatés en 2020), appel d'offres tous les deux
ans au Chili (la commission du gagnant passe de <!--chiffre:illustration()-->1,14<!--/--> % à <!--chiffre:illustration()-->0,77<!--/--> %, <!--chiffre:illustration()-->0,47<!--/--> %,
<!--chiffre:illustration()-->0,41<!--/--> %, remonte à <!--chiffre:illustration()-->0,69<!--/--> % en 2018, puis <!--chiffre:illustration()-->0,46<!--/--> % en 2025), remise imposée aux
gérants en Suède (<!--chiffre:illustration()-->0,31<!--/--> % net en 2013, <!--chiffre:illustration()-->0,11<!--/--> % en 2026). Là où seule la
concurrence joue, la baisse est continue : <!--chiffre:illustration()-->1,04<!--/--> % à <!--chiffre:illustration()-->0,40<!--/--> % pour les fonds
actions américains en vingt-neuf ans, soit <!--chiffre:illustration()-->3,3<!--/--> % par an. Chaque poste a donc
ses paliers `(année, taux)` dans `Parametres` : le frais de gestion suit le
rythme américain par marches de dix ans jusqu'au plancher de l'ERAFP
(<!--chiffre:mesure(parametre?nom=frais_gestion_paliers.3.1)-->0,20<!--/--> %), le frais sur versement rejoint l'assurance-vie, le contrat de
capitalisation puis zéro, le frais sur arrérages s'éteint en vingt ans. Un
frais de gestion étant contractuel, chaque versement entre au tarif de son
année et le garde : les lignes de l'échelle portent le tarif de leur cohorte,
et ne referment chaque année qu'une fraction `convergence_frais_stock` (<!--chiffre:mesure(parametre?nom=convergence_frais_stock)-->0,10<!--/-->)
de leur écart avec le tarif des nouveaux dépôts. L'OPEF montre le mécanisme :
de 2023 à 2025, le frais sur versement, mesuré sur les primes de l'année, a
baissé de <!--chiffre:illustration()-->1,20<!--/--> % à <!--chiffre:illustration()-->1,09<!--/--> %, quand le frais de gestion, mesuré sur tout
l'encours, n'a pas bougé. Le simulateur affiche le coût complet des frais, qui
dépasse les frais prélevés, parce que ce qui est prélevé ne produit plus
d'intérêts ; `docs/limites.md` §5 ante donne les sources de chaque palier et
mesure ce que chaque hypothèse déplace.

**Comment le capital devient une rente.** Par le mécanisme du PER : le capital
est divisé par un coefficient actuariel, la rente est réduite de ce que le
frais annuel sur sa réserve lui retire, puis chaque arrérage supporte ses
frais. Les deux tarifs sont ceux de l'année de la liquidation : la rente est un
contrat, elle garde les frais du jour où elle est souscrite.

```
rente = capital / G(a, L) × Σ p_t / Σ p_t (1 − f_réserve)^(−t) × (1 − f_arrérages)
```

**Six régimes de frais, un réglage.** Le site propose ces frais comme un
réglage des règles du calcul, « Frais du pilier capitalisé », qui voyage dans
l'adresse et s'applique au simulateur comme aux pages qui agrègent :
`Parametres.sous_regime_frais` définit une fois les six régimes (marché 2025
et paliers, paliers avec plafond, paliers avec contrats, marché 2025 figé,
PER vendu, aucun frais), et le portage les applique sans les redéfinir. La
page Coût compte le pilier de tous les cotisants sous ce réglage, par euro
versé : la grille ne lui donne que des rapports, le niveau vient des
cotisations du système 4 ancrées sur le compte du COR.

Prélever `f_réserve` par an sur la réserve d'une rente nivelée, à taux
technique nul, revient à actualiser au taux `−f_réserve` : le facteur du
milieu est le rapport de l'ancien diviseur au nouveau, sur la courbe de survie
du modèle à la liquidation, et il vaut exactement 1 sans frais. Il est appliqué
au diviseur plutôt que substitué à lui, pour que la rente reste comparable au
centime à la pension notionnelle. Au diviseur du modèle, pour un départ à
<!--chiffre:illustration()-->64<!--/--> ans en 2040, <!--chiffre:mesure(parametre?nom=frais_encours_rente_capitalisation)-->0,52<!--/--> % par an valent <!--chiffre:mesure(frais_reserve?age=64&annee=2040)-->7<!--/--> % de rente.

`G` est le diviseur du modèle, sur la même table de génération, unisexe et
au vingtile de niveau de vie de la carrière par défaut, avec un taux technique nul
(`taux_technique_rente_capitalisation`) comme dans la plupart des contrats. Les
deux lignes du scénario 6 partagent alors le **même diviseur** : à capital égal
elles servent le même montant, et tout écart vient d'ailleurs. Un taux
technique positif verserait davantage au début et moins ensuite, à espérance de
coût inchangée, comme `taux_anticipe_conversion` pour la répartition.

**Ce qui se transmet.** Le capital, intégralement, si le cotisant meurt avant
d'avoir liquidé : c'est la règle du PER, et c'est ce qu'une réforme de la
répartition ne peut pas offrir, un compte notionnel n'étant pas un capital mais
un droit. Le modèle en donne deux mesures, toutes deux sur sa propre table de
mortalité : le **capital transmissible** à chaque date, qui est l'encours de
l'année, et l'**espérance du capital transmis** vue de l'ouverture du pilier,

```
E = Σ_t (S_t − S_{t+1}) × ½ (encours d'ouverture + encours de clôture)_t
```

la somme portant sur les années d'accumulation strictement antérieures à la
liquidation — le modèle calcule une pension pour un assuré qui atteint son
départ, et compter l'année du départ ferait servir la rente et transmettre le
capital à la fois. Après la liquidation, la rente est viagère et ne se transmet
pas : une rente réversible ou à annuités garanties serait plus faible, et le
modèle ne la retient pas.

**Le déblocage.** À la retraite, en rente, ou au décès, par l'héritage, et pas
autrement. La proposition retire donc au PER ses sorties anticipées — achat de
la résidence principale, accidents de la vie — et sa sortie en capital : ce qui
est obligatoire ne se récupère pas à volonté. C'est la seule chose que le
pilier change à l'enveloppe existante, avec le caractère obligatoire de la
cotisation.

**Ce que ce compartiment ne fait pas.** Il ne simule aucun risque de marché :
il est placé sans risque par construction, et le seul aléa qui subsiste, celui
de taux futurs s'écartant des forwards d'aujourd'hui, n'est pas chiffré.
L'adossement le réduit sans le supprimer : il ne porte plus que sur les
versements à venir et, au-delà de trente ans d'horizon, sur le replacement du
bout de courbe — les versements déjà faits, eux, sont bloqués jusqu'au départ. Il ne
calcule aucune fiscalité, alors que les versements au PER sont déductibles et
la rente imposable ; tous les montants du modèle sont bruts, ici comme
ailleurs. Et il n'entre pas dans le bilan de la page Coût, parce qu'il ne
finance aucune pension d'aujourd'hui.

**Ce qu'il fait, et qu'on n'attend pas : il réduit la garantie vieillesse.**
Depuis le 19 septembre 2026, le plancher se compare à l'ensemble des ressources
de retraite, rente capitalisée comprise. La question — un pilier capitalisé
doit-il réduire une allocation différentielle ? — est une question de droit,
pas de modèle, et le programme l'a tranchée : une allocation différentielle
compte les ressources et non leur origine, comme l'ASPA d'aujourd'hui compte
une pension personnelle. Les <!--chiffre:mesure(parametre?nom=taux_capitalisation_volontaire)-->5<!--/--> points **volontaires** y entrent comme les
autres, et la conséquence est rude : pour qui reste sous le plancher après
avoir versé, ils ne rapportent **rien** en pension, la garantie les reprenant
euro pour euro. Il leur reste ce que la répartition ne donne à personne, un
capital qui se transmet. Un test fixe les deux cas, sous le plancher et
au-dessus.

---

#### L'âge légal de départ

C'est le quatrième terme de la proposition, posé le 22 septembre 2026 : un âge
légal de départ de <!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans à compter de la bascule
(`age_legal_liberal`). Toute liquidation que la proposition régit — celles qui
prennent effet à compter du 1<sup>er</sup> janvier de la bascule — a lieu à
cet âge au plus tôt. Qui serait parti avant sous le droit en vigueur part à
<!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans sous la proposition ; qui partait à cet âge ou après, et qui a
liquidé avant la bascule, n'est pas touché.

**Le report se calcule en prolongeant la carrière** (`Carriere.prolongee`) :
la dernière année se poursuit jusqu'à l'âge légal — même statut, même nature
de période, même salaire relatif, avancé au rythme du salaire moyen. La
proposition est alors calculée sur cette carrière-là, et sur elle seule : les
scénarios 1 à 5 partent à l'âge saisi. Le simulateur (`Simulateur.simuler`) le
fait d'un seul geste, `Simulateur.carriere_proposition`, et la comparaison
porte les deux carrières (`Comparaison.carriere_de`). Deux grandeurs dépendent
de la date du départ et sont prises à celle de la proposition quand elle est
reportée : le passage aux euros constants, qui ramène chaque montant de SON
année, et le dernier revenu du taux de remplacement. L'écart au système
actuel se lit donc en euros constants.

**Ce que ça fait à une pension.** Dans un compte notionnel, un départ plus
tardif ajoute des cotisations et raccourcit la retraite : le capital grossit,
le diviseur diminue, et la pension mensuelle MONTE. Ce qui se perd, ce sont
les mois de pension d'avant l'âge légal. Qui partait déjà à cet âge ou après
ne gagne rien, faute de décote ou de surcote à déplacer. Et la garantie
vieillesse, ouverte au même âge, est due dès le départ à toute liquidation que
la proposition régit.

**Ce que ça fait au coût** (§8 bis). La grille des cas types porte, pour
chaque couple, la proposition telle que sa génération la vit — son départ, sa
pension, ses cotisations, son pilier — et, quand la bascule passe entre les
cinq cohortes qu'une génération représente, telle que la cohorte de l'autre
côté la vit (`Pensionne.volet`) : une cohorte partie avant la bascule l'est
sans report. Moins de pensions sont servies, plus de cotisations encaissées.
Du côté des recettes, l'assiette que le COR projette est celle des âges
d'aujourd'hui ; elle est élargie du rapport des revenus d'activité de la grille
sous les deux âges (`SoldeAnnuel.facteur_assiette`). C'est un plafond, et
`limites.md` dit pourquoi.

`age_legal_liberal=None` retire la mesure : la proposition part alors aux âges
du scénario 4.

## 8 bis. Du droit individuel au coût collectif

Les huit sections qui précèdent décrivent un calcul de DROIT : ce qu'une carrière
ouvre. La page **Coût** en tire une grandeur collective, et il faut dire
comment, parce que le passage de l'un à l'autre est le moment où un modèle de
carrière peut se mettre à raconter n'importe quoi.

Il n'est pas franchi par une extrapolation. La dépense affichée est
**observée** : les Comptes de la protection sociale de la DREES, risque
vieillesse-survie, 1959-2024, certifiés contre l'API du producteur. Le modèle
n'en calcule pas un euro. Ce qu'il calcule est le seul **rapport** entre cette
dépense et ce que les quatre autres systèmes auraient versé aux mêmes
retraités, et il ne l'applique qu'à la part qui est une pension de
répartition obligatoire — ni l'aide à l'autonomie, ni la retraite
supplémentaire, ni le minimum vieillesse ne sont la pension d'un système (part
lue sur la ventilation depuis 1990, celle de 1990 reconduite avant) :

```
coût du système S en t = pensions de répartition observées en t × (masse S en t / masse actuelle en t)
```

La masse d'une année est reconstituée en croisant les treize cas types avec les
générations de 1880 à 2015, de cinq en cinq. Chaque couple pèse le produit de
trois choses : sa pension en euros constants, l'effectif réel des classes d'âge
que sa génération représente — lu dans la pyramide des âges de l'INSEE, non
supposé —, et le POIDS DE SON CAS TYPE.

Ce troisième terme est le dernier à avoir cessé d'être une convention. Les cas
types ont longtemps pesé à égalité, faute de source ; chacun porte désormais
l'effectif des retraités de sa caisse, que l'enquête annuelle auprès des caisses
de retraite publie de 2004 à 2024. Une caisse réclamée par plusieurs cas types
se partage également entre eux — la Cnav est celle des quatre carrières du
privé —, et c'est la seule part de convention égalitaire qui subsiste.

**Pourquoi un rapport plutôt qu'un niveau.** Le scénario 1 est l'étalon du
modèle, et il est une approximation du droit positif : ses erreurs de niveau
sont documentées au §3 de `limites.md`. Dans un rapport, elles figurent au
numérateur comme au dénominateur et s'annulent en grande partie. Un niveau
agrégé, lui, les porterait entières et s'écarterait de la dépense publiée sans
que rien ne le signale.

**Ce que la méthode suppose**, et que `limites.md` §5 bis chiffre : qu'un
effectif de caisse vaille un effectif de personnes — un polypensionné compte
dans chacune des siennes —, et une reconstitution mince avant 1975. Ni l'une ni
l'autre ne touche le résultat principal de cette moitié de page — l'égalité exacte des
scénarios prospectifs avec le système actuel sur toute la période observée —,
qui ne tient pas à une pondération mais à la définition même d'une réforme
prospective : les droits acquis avant la bascule sont conservés, donc aucune
pension déjà liquidée n'est modifiée.

### Et de là, l'avenir

La seconde moitié de la page projette les mêmes systèmes jusqu'en 2070. La
formule ne change pas d'un terme ; seule change l'origine de la dépense qu'elle
multiplie :

```
jusqu'en 2024   base = dépense de répartition OBSERVÉE
au-delà         base = ancrage × masse actuelle du modèle
                ancrage = base observée en 2024 ÷ masse actuelle en 2024
```

Les deux expressions coïncident EXACTEMENT en 2024 — c'est la définition de
l'ancrage —, si bien que la trajectoire ne saute pas au passage de l'observation
à la projection. Ce qui la fait bouger ensuite est ce qui doit la faire bouger :
la pyramide des âges, et les pensions que chaque génération acquiert sous chaque
système.

Deux précisions d'unité, parce qu'elles sont la source d'erreur la plus facile.
La série projetée est tenue en euros **constants** — les pensions du modèle le
sont déjà, et mêler les deux unités déflaterait deux fois, ce qui fait fondre la
projection d'un tiers. Et le PIB qui sert de dénominateur suit les hypothèses du
COR **composées avec sa trajectoire d'emploi** : une part de PIB met en rapport
deux grandeurs de la même année, dont le numérateur suit une démographie qui
vieillit ; laisser le dénominateur croître comme si l'emploi était constant
mettrait de la démographie d'un côté et pas de l'autre. C'est la même série que
lit l'indexation des comptes : la page se fabriquait auparavant son propre PIB,
corrigé par la population des 20-64 ans, et le dépôt en portait trois.

Ce que la projection suppose, et ce qu'elle vaut face au COR, est écrit dans
`limites.md` §5 ter.

### Et de là, le solde

Un coût n'est pas un solde. La dernière section de la page pose le second terme
du bilan — ce qui est ENCAISSÉ — et en tire, pour chaque système, le facteur qui
l'équilibrerait :

```
solde du système S en t     = ressources en t − dépenses du COR en t × rapport S en t
coefficient d'équilibre de S = ressources en t ÷ (dépenses du COR en t × rapport S en t)
```

**Ces ressources ne viennent pas de la DREES, et c'était le premier obstacle.**
Les Comptes de la protection sociale ne ventilent pas leurs ressources par
risque : ils publient la dépense risque par risque et le financement de
l'ensemble, maladie et famille comprises. Une « recette du risque vieillesse »
n'a pas de définition comptable, les cotisations d'un régime polyvalent n'étant
affectées à aucun risque. Le compte du SYSTÈME DE RETRAITE, lui, est publié —
dépenses, ressources et solde du même ensemble de régimes, sous la même
convention — et par le seul COR, qui consolide chaque année les rapports à la
Commission des comptes de la Sécurité sociale. Le critère 1 s'y applique en deux
temps : le COR n'est pas producteur des comptes de chaque régime, mais il est
le seul à les consolider, si bien que ces valeurs entrent au niveau `haute`.

**On lui prend les DEUX colonnes**, et non les seules ressources. Son périmètre
— régimes légalement obligatoires, FSV compris, RAFP exclu — n'est pas celui de
la dépense affichée plus haut : <!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2024&poste=depenses)-->13,86<!--/--> % du PIB en 2024, <!--chiffre:mesure(depense?annee=2024&quoi=cor)-->407<!--/--> Md€,
contre <!--chiffre:mesure(depense?annee=2024&quoi=part_pib_repartition)-->13,59<!--/--> %, <!--chiffre:mesure(depense?annee=2024&quoi=repartition)-->398,8<!--/--> Md€, pour la répartition obligatoire de la DREES
et <!--chiffre:mesure(depense?annee=2024&quoi=part_pib)-->14,54<!--/--> %, <!--chiffre:mesure(depense?annee=2024)-->427<!--/--> Md€, pour le risque vieillesse-survie entier.
Soustraire l'une de l'autre fabriquerait un solde de deux périmètres ;
en gardant la dépense du COR au dénominateur, le solde du scénario 1 redonne
exactement celui qu'il publie, et le voisinage des deux séries devient un
contrôle externe au lieu d'être un risque. Du modèle, cette section n'emprunte
que le RAPPORT des masses, qui est sans dimension et passe donc d'un périmètre
à l'autre sans rien supposer.

**La recette suit le droit.** Une part des ressources du système actuel paie
des droits qu'aucun scénario notionnel ne sert, et deux payeurs la versent. La
branche famille paie l'assurance vieillesse des parents au foyer et les
majorations pour enfants :
<!--chiffre:mesure(recette?annee=2024&quoi=retrait&payeurs=famille)-->0,4<!--/--> point de PIB, <!--chiffre:mesure(recette?annee=2024&quoi=retrait&payeurs=famille&en=milliards)-->10,9<!--/--> Md€,
<!--chiffre:mesure(recette?annee=2024&quoi=retrait&payeurs=famille&sur=ressources)-->2,7<!--/--> % des ressources en 2024, lus chez celui qui paie dans les
rapports à la Commission des comptes de la Sécurité sociale. Le fonds de
solidarité vieillesse, dont la CNAV reprend les missions au 1er janvier 2026,
finance par la CSG des trimestres pour des périodes non travaillées et le
minimum vieillesse : <!--chiffre:mesure(recette?annee=2024&quoi=retrait&payeurs=solidarite)-->0,7<!--/--> point de plus, <!--chiffre:mesure(recette?annee=2024&quoi=retrait&payeurs=solidarite&en=milliards)-->19,6<!--/--> Md€, qui arrive
par l'impôt et sort donc de la ligne des impôts affectés, non de celle des
transferts. Le troisième payeur, l'assurance chômage, verse les points des
chômeurs — <!--chiffre:mesure(recette?annee=2024&quoi=versement&payeurs=chomage)-->0,1<!--/--> point, <!--chiffre:mesure(recette?annee=2024&quoi=versement&payeurs=chomage&en=milliards)-->3,9<!--/--> Md€ —, et
ceux-là, le compte notionnel les porte : sa recette reste à tous. Le dépôt la
retirait aussi jusqu'au 23 septembre 2026, au motif qu'une année de chômage
ne portait rien au compte, ce qui n'a jamais été le cas. Les scénarios 2 à 6
se voient retirer les deux autres,
<!--chiffre:mesure(recette?annee=2024&quoi=retrait&sur=ressources)-->7,5<!--/--> % des ressources en 2024, année par année de 2013 à 2024 — la
fenêtre où toutes les séries sont publiées —, à part constante des ressources
avant et sur tout l'horizon projeté. Le système actuel encaisse tout, et son
solde reste celui du COR.

**Et ce que la proposition n'encaisse plus, elle ne le garde pas.** Le
scénario 6 ne reconduit ni la contribution d'équilibre de l'État, ni les
subventions d'équilibre, ni les impôts et taxes affectés : un compte notionnel
ne crédite que ce qui est assis sur un revenu d'activité. Rien ne disait ce que
ces recettes devenaient, ce qui revenait à les laisser au budget, c'est-à-dire
à les consacrer au déficit. Décision du 20 septembre 2026, et c'est un
partage : **la moitié est rendue aux salaires, la moitié éteint de la dette**
(`Parametres.part_rendue_aux_salaires`, zéro rendant l'ancienne convention).

Ce qui est rendu l'est dans l'ordre que le droit impose. Deux impôts du poste
seulement sortent d'une rémunération : la **taxe sur les salaires**, dont
l'article L. 131-8, 1° du code de la sécurité sociale verse <!--chiffre:illustration()-->58,35<!--/--> % à la
branche vieillesse dans sa version en vigueur au 1er février 2026, et le
**forfait social**, que l'article L. 241-3, 1° lui donne en entier — ensemble
<!--chiffre:mesure(restitution?quoi=part_du_poste&annee=2024)-->28<!--/--> % du poste en 2024, entre <!--chiffre:mesure(restitution?quoi=part_du_poste&annee=2019)-->27<!--/--> % en 2019 et <!--chiffre:mesure(restitution?quoi=part_du_poste&annee=2020)-->29<!--/--> % en 2020. Ils sont
supprimés. Le solde revient par une baisse de la CSG sur les revenus
d'activité, de <!--chiffre:mesure(restitution?quoi=points_csg&annee=2026)-->1,1<!--/--> point en 2026.

Et il faut dire ce que cette baisse n'est pas. **La CSG sur les revenus
d'activité ne finance aujourd'hui aucune retraite** : ses <!--chiffre:illustration()-->9,20<!--/--> points vont à la
CNAF (0,95), aux régimes obligatoires d'assurance maladie (4,25), à la CADES
(0,45), à l'Unédic (1,47) et à la CNSA (2,08), soit 9,20 exactement, article
L. 131-8, 3°, version en vigueur au 1er février 2026. Ce que la branche
vieillesse encaisse en CSG est assis sur le capital et sur les pensions. La
baisse est donc une dépense fiscale au profit des salariés, financée par une
recette que la retraite abandonne — pas une restitution.

La contribution d'équilibre d'un employeur public suit la même règle, et c'est
`Incidence.PARTAGEE` dans `remuneration.py` : la moitié de ce qu'il cesse de
verser remonte dans le traitement, l'autre moitié paie la dette de pensions
déjà promises. Ni l'incidence intégrale, qui prêterait à un fonctionnaire de
l'État les <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=fonction_publique_etat)-->82,28<!--/--> points que son employeur verse en 2026 comme s'ils avaient
été son salaire différé ; ni l'assiette fixe, qui ne lui en rendrait aucun.

**Rien de tout cela ne déplace un solde du système de retraite** : ces recettes
en étaient déjà sorties. Ce que le partage déplace est la fiche de paie, et le
budget de l'État — que le dépôt ne tient pas, et `docs/limites.md` § 5 ante
quater le dit.

**Le coefficient est calculé, jamais appliqué.** C'est la distinction à tenir :
un système notionnel réel relèverait ses pensions jusqu'à l'équilibre, ou les
abaisserait, par un facteur commun à toutes les pensions de l'année. Un
coefficient supérieur à un n'est donc pas une économie mais une MARGE, et lire
les <!--chiffre:mesure(coefficient?scenario=3&annee=2070)-->1,74<!--/--> du scénario 3 en 2070 comme une économie de <!--chiffre:mesure(coefficient?scenario=3&annee=2070&quoi=economie)-->43<!--/--> % est un contresens : à
prélèvement inchangé, ce système servirait autant que le nôtre, autrement
réparti entre les carrières. Le facteur étant commun, l'appliquer déplacerait
les niveaux sans toucher aux écarts, qui sont l'objet du modèle.

**Et du solde, le stock.** Un solde est un flux ; un déficit qui se répète
devient une dette, et une dette porte intérêt. La section suivante de la page
cumule les soldes projetés de chaque système par la récurrence de toute dette
publique rapportée au PIB :

```
stock(t) = stock(t−1) ÷ (1 + croissance(t)) + intérêts(t) − solde(t)
intérêts(t) = stock(t−1) × taux(t) ÷ (1 + croissance(t))
```

Le stock part de zéro à la dernière année observée — les réserves et la dette
d'aujourd'hui, que le COR chiffre à part, n'y entrent pas — et un stock
négatif est une réserve. Le taux n'est pas choisi : c'est le taux à un an que
la courbe des taux sans risque de la BCE implique pour chaque année, le forward
que le pilier capitalisé lit déjà, prolongé à plat au-delà de la dernière
maturité cotée ; la croissance est celle du PIB nominal de la projection. La
seule sensibilité montrée est celle de ce taux, un point en plus ou en moins,
parce que c'est la seule chose que la section lit au lieu de la calculer. Ce
que la courbe dit d'un système notionnel n'est pas ce qu'il ferait — il se
règle par le coefficient — mais la marge, ou le manque, que ce coefficient
aurait à répartir ; ce qu'elle dit du système actuel est ce que coûte
d'attendre une réforme.

---

## 9. Les données

### Sources

`data/sources.yaml` recense les <!--chiffre:entrees(data/sources.yaml:institutions.*.jeux)-->178<!--/--> jeux de données des
<!--chiffre:entrees(data/sources.yaml:institutions)-->39<!--/--> institutions, avec pour chacun l'URL, le mode
d'accès et l'état d'intégration.

### Quelle source l'emporte

Deux institutions publient souvent le même chiffre. Quatre critères, écrits en
tête du manifeste, disent laquelle il faut aller chercher — dans l'ordre, le
premier qui départage tranchant :

1. **le producteur prime sur le repreneur** — l'INSEE plutôt qu'un rapport qui
   cite l'INSEE ; c'est ce critère qui plafonne à `haute` toute transcription
   tierce, même automatisée ;
2. **l'observé prime sur le projeté** — une projection n'entre que là où
   l'observation manque, et au niveau `estimee` ;
3. **le montant servi prime sur le montant calculé** — ce qu'une caisse a payé
   l'emporte sur ce que son article de loi ferait calculer ;
4. **le recontrôlable prime sur le saisi** — à qualité égale, `acces: api`
   plutôt que `acces: document`.

Ce n'est pas un classement d'institutions mais de natures de données : la même
institution est primaire sur un terrain et secondaire sur l'autre. L'INSEE pour
ce qu'il **mesure**, le COR pour ce qu'il **décide** — ses hypothèses de long
terme, dont il est l'auteur. Jamais le COR comme intermédiaire vers une donnée
INSEE.

### Fiabilité

Aucune valeur ne circule dans le modèle sans son niveau de fiabilité :

| Niveau | Sens |
|---|---|
| `certifiee` | recontrôlée automatiquement contre la source |
| `haute` | valeur publiée, recopiée, non recontrôlée |
| `moyenne` | valeur publiée mais champ ou base incertains |
| `estimee` | reconstitution, ou projection |

La fiabilité d'un résultat est celle de **son maillon le plus faible**.
`Parametres.fiabilite_minimale` fait échouer la simulation plutôt que de
produire un chiffre trompeur. La page **Données** du site en dresse l'état.

Le niveau `certifiee` suppose que la source soit le **producteur** de la donnée
et que la valeur ait été recontrôlée contre elle par
`scripts/verifier_donnees.py`. Une transcription tierce, même sourcée et reprise
automatiquement, plafonne à `haute`. L'état exact figure dans `docs/limites.md`.

### Tables de mortalité

Deux sources, par ordre de priorité, et le partage se fait couple par couple
(année, sexe, âge) — pas en bloc :

1. `data/reference/mortalite/quotients_periode.csv` — les **quotients observés**
   (`annee,sexe,age,qx`). Ils couvrent <!--chiffre:minimum(data/reference/mortalite/quotients_periode.csv:annee)-->1899<!--/-->-<!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:annee)-->2024<!--/-->, une seule source par année : les
   tables de Vallin et Meslé publiées par l'INED jusqu'en 1997, par âge jusqu'à
   <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=1990)-->104<!--/--> ans ; la table de mortalité française diffusée par Eurostat
   ensuite, jusqu'à <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2000)-->84<!--/--> ans pour les millésimes 1998-2013 et <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2020)-->94<!--/--> ans depuis ;
2. partout ailleurs — au-delà du dernier âge publié, et pour les années
   projetées — une table paramétrique de **Gompertz-Makeham**
   `μ(x) = A + B·exp(k(x−60))`, dont *B* et *k* sont ajustés par bissection.

**La cible de cet ajustement est la table RACCORDÉE, pas la loi seule**, et
c'est ce qui a longtemps manqué. Calibrée sur elle-même, la loi n'avait aucune
raison de rendre la queue que la cible implique : elle donnait 11,3 ans
d'espérance résiduelle à 85 ans pour une femme en 2010, quand l'espérance
publiée à 60 ans en implique 7,5. Comme les millésimes 1998-2013 s'arrêtent à
84 ans, la table effectivement lue par le modèle débordait alors l'espérance de
l'INSEE de jusqu'à 2,5 ans.

L'ajustement se fait donc en deux temps. La **forme** de la queue — le
paramètre *k* — vient de la calibration classique sur la loi seule, où e60 et
e65 portent sur toute la plage d'âges et la déterminent sans ambiguïté. Son
**niveau** — le paramètre *B* — est ensuite recalé, à forme constante, pour que
la table raccordée reproduise l'espérance publiée à <!--chiffre:illustration()-->60<!--/--> ans. Là où la queue n'a
pas prise sur la cible — millésimes dont les quotients vont jusqu'à <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age)-->104<!--/--> ans, où
les données décident seules —, le recalage est abandonné plutôt que forcé.

Le raccord est contrôlé, et le contrôle est cette fois réel : un test recalcule
l'espérance de vie à <!--chiffre:illustration()-->60<!--/--> ans par le seul chemin que le moteur emprunte
(`survie_annuelle`, quotients observés puis loi) et la confronte à l'espérance
publiée par l'INSEE, qui vient d'une tout autre chaîne de production. Les deux
concordent à 0,1 an près sur 1990-2024. Le test précédent passait par une
branche qui ne consultait aucun quotient : il comparait la calibration à sa
propre cible et ne pouvait pas échouer.

Ce partage donne la bonne mortalité aux âges qui pilotent le diviseur sans
prétendre décrire la mortalité aux âges jeunes, qui n'entrent pas dans le
calcul.

**Une troisième source, pour les populations particulières.**
`data/reference/mortalite/esperances_vie_populations.csv` porte l'espérance de
vie à <!--chiffre:illustration()-->65<!--/--> ans que certains régimes publient pour leurs propres pensionnés — les
fonctionnaires civils de l'État, par le Service des retraites de l'État,
saisie depuis le projet annuel de performances du programme 741 annexé au
PLF 2026 — et, dans `esperances_vie_niveau_de_vie.csv`, les vingt vingtiles
de niveau de vie de l'INSEE pour 2012-2016 et 2020-2024, avec l'ensemble de
l'étude et le niveau de vie moyen de chaque vingtile. Le modèle n'en fait pas
une table : il cale, sexe par sexe, un facteur sur la force de mortalité de
la table générale de l'année observée, et le tient constant ailleurs. Elles
ne servent qu'à la variante `population_conversion` du §5.

**Les années projetées viennent de l'INSEE, année par année, jusqu'en <!--chiffre:maximum(data/reference/mortalite/esperances_vie.csv:annee)-->2125<!--/-->.**
Ce sont les projections de population **2026**, qui publient les quotients de
mortalité par âge (0 à <!--chiffre:mesure(constante?de=retraite_notionnelle.donnees.mortalite&nom=AGE_TERMINAL)-->120<!--/--> ans) et par année : le dépôt en dérive e0, e60 et
e65, y compris donc l'espérance à <!--chiffre:illustration()-->65<!--/--> ans que l'INSEE ne publie jamais, et la
calibration s'appuie dessus comme sur n'importe quelle autre année. Elles
étaient auparavant saisies à six années rondes depuis un exercice antérieur,
interpolées entre elles et gelées après 2080 — un gel qui arrêtait l'espérance
de vie vingt ans avant la fin de la projection.

La somme des survies se fait **sans le demi-an usuel** : ce classeur indexe ses
quotients par âge atteint dans l'année, qui le comprend déjà. Deux contrôles
l'établissent et le récupérateur les refait à chaque exécution — l'espérance de
vie à la naissance publiée par l'INSEE pour 2070 est retrouvée au centième
(<!--chiffre:cellule(data/reference/mortalite/esperances_vie.csv:valeur?annee=2070&sexe=F&mesure=e0)-->89,5<!--/--> et <!--chiffre:cellule(data/reference/mortalite/esperances_vie.csv:valeur?annee=2070&sexe=H&mesure=e0)-->86,7<!--/--> ans), et la série projetée rejoint l'observée sans marche.

### Unité de compte

Tous les montants sont produits en euros courants de l'année de liquidation
**et** en euros constants de 2026 (`annee_euros_constants`). Sans cette
conversion, comparer une pension liquidée en 1975 à une pension de 2064 n'a
aucun sens : l'écart de niveau des prix dépasse largement l'effet de la réforme
simulée.

### Brut, et pas net

Tout ce que le modèle manipule est **brut** : le revenu saisi, les cotisations
versées, le capital notionnel, les cinq pensions. « Brut » au sens des comptes
nationaux — *salaires et traitements bruts* (D11) rapportés à l'emploi salarié
intérieur, la définition même du salaire moyen par tête qui sert d'unité —,
c'est-à-dire **avant** cotisations salariales, CSG, CRDS et impôt sur le revenu,
et **hors** cotisations patronales, qui s'ajoutent au brut sans en faire partie.

Ce n'est pas une commodité d'affichage : c'est l'assiette sur laquelle les
régimes appellent leurs cotisations, donc la seule grandeur qu'un compte
notionnel puisse enregistrer. Conséquence à retenir en lisant les résultats : le
taux de remplacement rapporte un brut à un brut, et il est mécaniquement plus
bas qu'un taux calculé sur des nets, les pensions étant moins prélevées que les
salaires. Le modèle ne convertit jamais en net, faute d'une série de taux de
prélèvement par statut et par année qui soit du même niveau de preuve que le
reste.

Le revenu d'activité se saisit en **euros d'aujourd'hui** : ce que le métier
paie maintenant. Le modèle, lui, ne connaît que le **multiple du salaire moyen**,
seule unité qui garde son sens sur quatre-vingts ans — un montant n'en a que
rapporté à son année. Le site fait donc une division, et une seule :

```
niveau = revenu mensuel × 12 ÷ salaire moyen annuel
```

Ce niveau suit ensuite le salaire moyen d'une année à l'autre, déformé par le
profil de carrière : le revenu saisi est celui du milieu de carrière, pas celui
de chaque année.

Le multiple reste saisissable pour qui raisonne en relatif : un lien sous les
métiers bascule d'une unité à l'autre. Un **lien** et non un menu, parce qu'un
formulaire HTML ne convertit rien quand on change un menu — le nombre resterait
celui de l'ancienne unité, et « 3 500 » deviendrait 3 500 fois le salaire moyen.
Le lien, lui, porte l'adresse complète, unité et montants déjà traduits, si bien
que la page revient dans l'autre unité en décrivant la même carrière.

L'aller-retour n'est pas exact, et il ne peut pas l'être : le multiple s'écrit au
millième, et un millième de salaire moyen vaut **environ <!--chiffre:mesure(millieme_salaire)-->3,48<!--/--> € par mois**. Un
aller-retour déplace donc le revenu d'un demi-pas au plus, plus l'arrondi à
l'euro — **deux euros par mois** sur tout le domaine accepté, balayé euro par
euro par un test. Le pas du champ et la précision du lien sont tenus par une
même constante (`DECIMALES_MULTIPLE`) : s'ils divergeaient, le lien écrirait un
nombre que le navigateur refuserait de soumettre.

### Arrondis : ce que le droit fait, et ce que le modèle fait

La question se pose parce que la réponse n'est pas celle qu'on attend : **le
droit n'arrondit pas la pension**. Depuis le 1er décembre 1986, les prestations
de vieillesse du régime général sont payées « sur un montant non arrondi
(y compris les centimes) » — décrets n° 86-130 et 86-131 du 28 janvier 1986,
notifiés par la circulaire Cnav 49/86 du 25 juin 1986, qui supprime
explicitement la règle d'arrondi antérieure. Cette règle-là, héritée de
l'article 5 de la loi n° 50-147 du 3 février 1950, portait le total trimestriel
au multiple de 50 centimes immédiatement supérieur (circulaire Cnav 21/71 du
10 juin 1971). Elle n'a plus cours.

Le modèle ne fait donc **aucun arrondi monétaire**, dans aucun des cinq
scénarios, et c'est la lecture conforme au droit pour le scénario 1 comme pour
les autres. Le site affiche les pensions **au centime** là où l'on refait le
calcul, pour la même raison : l'euro rond laissait croire à un arrondi que la
caisse ne fait pas. La vue des résultats, elle — les quatre barres, et ce que le
salaire devient —, les arrondit à l'euro, comme le résumé qui la précède : le
lecteur y lisait deux écritures du même nombre. Sa clé de lecture le dit.

Trois arrondis subsistent en droit, et voici ce que le modèle en fait :

| Arrondi | Fondement | Le modèle |
|---|---|---|
| Trimestres, à l'entier supérieur | CSS art. R. 351-27 | **appliqué** — et il pèse : un trimestre vaut environ <!--chiffre:mesure(poids_trimestre?generation=1965)-->0,6<!--/--> % de la pension |
| Revenus portés au compte, à l'euro le plus proche (la fraction de 0,50 comptée pour 1) | CSS art. L. 133-10, section « Règles d'arrondis » | **non appliqué** — voir `limites.md` |
| Montants anciens en francs, convertis puis arrondis au centime | doctrine Cnav, *Revenu annuel moyen* | **non appliqué** — le relevé se saisit déjà en euros, la conversion se fait donc avant le modèle et hors de lui |

Le revenu annuel moyen lui-même n'est arrondi par aucun texte : il est la somme
des revenus revalorisés des meilleures années divisée par leur nombre, calculée
sur des revenus exprimés en euros.

### Précision des coefficients affichés

Une chaîne de calcul montrée à l'écran doit pouvoir se refaire à la main. Cela
ne dépend pas seulement de l'exactitude du modèle : un coefficient affiché trop
court rend la chaîne infaisable alors même que le calcul est juste. Les
précisions ne sont donc pas décoratives, elles sont **mesurées** — pour chaque
étape, on prend la plus courte au-delà de laquelle le gain s'arrête :

Attention au piège : la mesure doit porter sur les valeurs **affichées**, pas
sur les valeurs exactes du modèle. Faite sur les secondes, elle ignore l'arrondi
des lignes que le lecteur a sous les yeux et fait paraître suffisante une
décimale de moins — c'est ainsi que le diviseur a d'abord été fixé à quatre
décimales alors qu'il en faut cinq.

Écart maximal de la ligne reconstituée depuis l'écran, mesuré le 10 septembre
2026 sur 52 carrières — la mesure qui a fixé les deux constantes :

| Étape | 4 déc. | 5 déc. | 6 déc. | Retenu |
|---|---|---|---|---|
| Droits acquis × diviseur | 2,70 € | **0,57 €** | 0,57 € | <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=DECIMALES_DIVISEUR)-->5<!--/--> (`DECIMALES_DIVISEUR`) |
| Capital ÷ diviseur | 0,10 € | **0,02 €** | 0,02 € | <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=DECIMALES_DIVISEUR)-->5<!--/--> |
| Capital × revalorisation | 62,27 € | 6,47 € | **1,23 €** | <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=DECIMALES_FACTEUR)-->6<!--/--> (`DECIMALES_FACTEUR`) |
| Cotisations × rendement cumulé | 50,92 € | 5,09 € | **1,07 €** | <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=DECIMALES_FACTEUR)-->6<!--/--> |

Au-delà, le gain s'arrête : ce qui reste vient de ce que les **capitaux
s'affichent à l'euro**, ce qui borne toute reconstitution à un demi-euro par
terme. Cette borne-là ne se rachète pas par des décimales — il faudrait afficher
les capitaux au centime, où le centime n'a pas de sens.

Le tableau des neuf règles d'indexation garde deux décimales : son rendement
n'entre dans aucune multiplication affichée, il sert à comparer des règles entre
elles, et neuf lignes à cinq décimales ne se lisent plus.

Un test refait chaque chaîne depuis les seuls nombres AFFICHÉS — cascade du
scénario 1 au scénario 3, compte du scénario 2, mensuel contre annuel des cinq
blocs, lignes contre total du détail par régime, écarts et économies de la page
Coût. Ses bornes se déduisent des précisions ci-dessus plutôt que d'être
choisies : elles suivront si ces précisions changent.

### Ancrage des rémunérations

Les comptes nationaux ne publient que des taux de croissance du salaire moyen.
Le modèle les cumule à partir d'un point d'ancrage — <!--chiffre:mesure(constante?de=retraite_notionnelle.carriere&nom=ANCRAGE_SALAIRE_MOYEN.1)-->40 000<!--/--> € bruts annuels en
2024 — documenté dans `carriere.py`. Ce point déplace proportionnellement tous
les revenus reconstitués, donc toutes les pensions, mais il est **sans effet sur
les rapports entre scénarios**, qui sont l'objet du modèle.

Il commande en revanche la traduction d'un salaire en multiple, et donc les
repères que le site affiche sous le champ — SMIC, salaire moyen, plafond de la
Sécurité sociale — pour que l'échelle soit visible au lieu d'être supposée. Le
SMIC mensuel y est calculé sur <!--chiffre:mesure(constante?de=retraite_notionnelle.web.pages&nom=HEURES_SMIC_PAR_MOIS)-->151,67<!--/--> heures, la durée légale actuelle ; l'année
de référence étant celle du modèle, aucune durée du travail passée n'a à être
supposée.

### Une carrière, plusieurs métiers

On faisait autrefois le même métier toute sa vie, et le modèle n'a longtemps su
décrire que celui-là. Une carrière se décrit désormais comme une **suite de
métiers** (`Carriere.depuis_parcours`) : chacun porte un statut d'affiliation, un
âge de début et un niveau de revenu, court jusqu'au début du suivant, et le
dernier jusqu'à la liquidation. La carrière d'un seul métier en est le cas
particulier — `depuis_profil` n'est plus qu'un appel à un métier, ce qui garantit
que le passé du modèle n'a pas bougé d'un centime.

Ce que le découpage change est exactement ce que le modèle mesure : chaque
changement fait passer d'un régime à un autre, donc d'un taux de cotisation, d'une
assiette et d'un barème à un autre. Un salarié devenu artisan cotise davantage à
sa charge et acquiert moins de droits gratuits ; le compte notionnel enregistre
l'un et le scénario 1 l'autre.

Deux conventions le bornent, l'une et l'autre imposées par la maille des données :

* **le profil de rémunération vaut pour la carrière entière**, changements
  compris. `profil_carriere` décrit une progression de *carrière*, pas d'emploi :
  le niveau propre à chaque métier s'y superpose, il ne remet pas la progression à
  zéro. Un métier deux fois mieux payé que le précédent double le revenu au point
  du changement, il ne renvoie pas l'assuré au bas de sa grille.

  **Il est LU chez l'INSEE, à un âge et à une année**, et ne dépend de rien
  d'autre. Deux séries le portent, parce qu'aucune ne suffit seule :

  - la FORME vient de `profil_salaire_categorie.csv` — salaires du privé par
    âge et par catégorie socioprofessionnelle, 2024. C'est le seul jeu de
    l'INSEE qui croise ces deux dimensions, et donc le seul qui décrive une
    CARRIÈRE : un profil agrégé mélangerait l'effet d'âge et un effet de
    composition, les jeunes étant plus souvent dans les catégories les moins
    payées, si bien que son écart entre les bords vaut 0,46 quand celui des
    ouvriers vaut 0,24. Observé de 26 à 55 ans : ×1,28 pour un ouvrier, ×1,30
    pour un employé, ×1,41 pour une profession intermédiaire, ×1,86 pour un
    cadre ;
  - l'ÉVOLUTION vient de `profil_salaire_age.csv` — séries longues du privé
    par tranche d'âge, 1962-2024. C'est là que se loge l'effet de génération :
    la prime à l'âge valait 1,19 entre les 51-60 ans et les 26-30 ans en 1962,
    1,47 en 2000, 1,35 en 2024. Celui qui est né en 1940 est entré dans la vie
    active au salaire moyen de son temps, celui qui est né en 1960 à 86 % du
    sien.

  **Le public a son propre fichier**, `profil_salaire_statut_public.csv`, lu
  dans le seul jeu de l'INSEE qui croise l'âge et le statut : ×1,11 de <!--chiffre:mesure(constante?de=retraite_notionnelle.carriere&nom=TRANCHES_CATEGORIE.Y_LT30)-->26<!--/--> à
  <!--chiffre:mesure(constante?de=retraite_notionnelle.carriere&nom=TRANCHES_CATEGORIE.Y50T59)-->54,5<!--/--> ans — les centres de ses tranches extrêmes — pour un catégorie C, ×1,22 pour un catégorie B, ×1,56 pour un
  catégorie A, là où le profil du privé qu'on leur servait valait ×1,30.

  **Les régimes spéciaux portent en plus un facteur de secteur**, lu dans
  l'enquête européenne sur la structure des salaires : ×1,38 pour les IEG
  (section « électricité et gaz », qui est le champ de leur statut), ×0,93 pour
  la SNCF et la RATP (section « transports »), ×1,40 pour la Banque de France.
  C'est la seule source qui les approche, elle est agrégée par secteur, et le
  modèle n'en prend qu'un rapport de pentes — ce qui suppose ce rapport
  identique en intra-catégorie et en agrégé. C'est l'hypothèse la plus forte du
  profil salarial ; `limites.md` §1 la nomme, et les mines comme les spectacles
  en sont exclus, leur facteur ne tenant pas d'une vague à l'autre.

  **Et le profil se choisit sur l'AFFILIATION**, non sur un réglage saisi : on
  ne demande pas sa progression de carrière à quelqu'un qui a déjà dit qu'il
  était fonctionnaire de l'État. La table est `PROFIL_PAR_AFFILIATION`, et les
  affiliations publiques prennent le profil de leur VERSANT — aucune ne porte
  le A, le B ou le C, et celui du versant pondère déjà les catégories par leurs
  effectifs. Le profil se lit métier par métier : changer d'affiliation en cours
  de carrière déplace la pente sans rien remettre à zéro. Les quatre noms
  explicites restent, pour une grille qui en sait plus — les cas types
  « sédentaire » et « catégorie active » portent le B et le C que leur
  commentaire annonçait déjà — et pour une carrière qui ne progresse pas, comme
  celle au SMIC.

  On module l'écart à la moyenne et non la valeur : `1 + (forme − 1) ×
  modulation` laisse le profil centré, de sorte que le niveau de revenu saisi
  garde son sens. Le modèle retrouve ainsi les pentes observées à quelques
  centièmes près — ×1,23 contre ×1,25 pour la génération 1940, ×1,37 contre
  ×1,38 pour celle de 1960.

  **Ce que ça a remplacé, et ce que ça a coûté.** Trois nombres écrits à la
  main, sans source : 60 % du niveau saisi au premier emploi, 130 % au dernier,
  190 % pour un cadre. Ils appliquaient une pente de ×1,69 et ×2,42 de 26 à
  55 ans — un tiers de trop —, la même à toutes les générations, et mesurée sur
  la carrière de l'assuré, si bien que travailler plus longtemps rabaissait
  rétroactivement ses propres salaires passés. Les trois réserves qui restent
  sont au §1 de `limites.md` ;
* **une année civile n'a qu'un statut.** Le moteur ne connaît qu'une ligne par
  année — un salaire est déclaré à l'année, les régimes liquident à l'année. L'année
  d'un changement revient donc au métier qui en occupe le plus de mois, et à
  égalité à celui qui l'ouvre ; le **revenu**, lui, reste la somme de ce que les
  deux métiers ont réellement payé, au prorata des mois. C'est la seule
  approximation du découpage, et elle ne porte que sur une année par changement :
  ses cotisations sont calculées au barème d'un régime plutôt qu'au barème
  partagé des deux ;
* **deux activités à la fois se DÉCLARENT, et chacune a sa ligne.** Le
  salarié qui exerce aussi en libéral, le fonctionnaire qui a une activité
  accessoire : un métier marqué `cumul` s'ajoute à l'activité principale au
  lieu de lui succéder, de son âge de début à son âge de fin ou au départ. Le
  modèle ne le devine jamais — un métier qui ne le déclare pas succède au
  précédent. L'année porte alors une ligne par statut, et deux lignes ne
  partagent jamais le leur. Chaque activité cotise à son régime sur son
  revenu, et chaque régime sert ses droits ; ce que le droit compte TOUS
  RÉGIMES ne dépasse pas quatre trimestres par année civile (R. 351-5, et le
  2° de R. 173-4-4-1 pour la liquidation unique des régimes alignés), et la
  liquidation unique somme les revenus d'une même année avant de les écrêter
  une seule fois au plafond. Servi par les deux moteurs, qu'un tirage au
  hasard de parcours cumulés confronte valeur par valeur. Le formulaire le
  propose par un menu « remplace la précédente / s'ajoute à celle en cours »,
  réglé sur « remplace ».

Le formulaire du site en accepte six, ce qui n'est pas une limite du moteur :
au-delà, ce n'est plus une suite de métiers qu'on décrit mais un relevé de
carrière année par année. Celui-ci a son propre champ dans le formulaire — une
ligne par année, `année:régime:revenu:trimestres` — et son propre constructeur,
`Carriere.depuis_releve`. Rempli, il remplace la suite des métiers : plus rien
n'est reconstitué, ni le revenu de chaque année ni les trimestres qu'elle a
validés. C'est le seul chemin où l'euro n'est converti par rien — le formulaire
paramétrique saisit un revenu d'aujourd'hui que le modèle promène ensuite le
long du salaire moyen, quand le relevé donne déjà les euros de chaque année.
