# Retraite à comptes notionnels — modèle français rétroactif

**Ce dépôt répond à une question : que verserait la retraite française si elle
avait toujours été calculée en comptes notionnels, c'est-à-dire au franc le
franc des cotisations réellement versées ?**

Un compte notionnel est un compte virtuel — aucun capital n'est placé, la
répartition reste la répartition. Ce qui change, c'est le calcul du droit :

1. **accumulation** — chaque année, la cotisation retraite effectivement versée
   est inscrite au compte ;
2. **revalorisation** — le solde est revalorisé chaque année selon une règle
   collective ;
3. **liquidation** — `pension = capital notionnel ÷ espérance de vie restante`
   à l'âge de départ.

Il n'y a donc ni minimum, ni majoration, ni trimestre gratuit : ce qui n'a pas
été cotisé n'existe pas, et partir tôt coûte deux fois — moins de cotisations
accumulées, et une rente à servir plus longtemps.

Le modèle calcule **six scénarios pour une même carrière**, afin qu'ils soient
comparables :

| | Scénario | Ce qu'il mesure |
|---|---|---|
| **1** | Système actuel | Le droit en vigueur, minima et majorations compris. C'est la référence. Le total affiché est celui de la **répartition seule** : ce qui relève de la capitalisation (RAFP) est servi à part, à l'identique dans les six scénarios. |
| **2** | Notionnel **rétroactif** depuis 1941 | Contrefactuel : toute la carrière recalculée sur les seules cotisations, comme si la règle avait toujours existé. |
| **3** | Notionnel **à compter de 2026** | Réforme prospective : les droits déjà acquis sont figés — au contributif seul, avantages non contributifs retirés — puis convertis en capital, et les règles notionnelles s'appliquent ensuite. Qui a liquidé avant la bascule garde sa pension telle quelle : c'est ce qui distingue ce scénario du **2**. |
| **4** | Le scénario **2**, part patronale comprise | Le même compte rétroactif, la cotisation de l'employeur en plus : celle de la fiche pour le privé, celle réellement versée — jusqu'à 82,28 % du traitement en 2026 — pour le public. |
| **5** | Le scénario **3**, part patronale comprise | Le même compte prospectif, droits acquis conservés, avec la même part patronale en plus. |
| **6** | La **proposition libérale** : le scénario **4** jusqu'à 2026, puis 18 % pour tous en répartition, 5 % capitalisés, et une garantie vieillesse | Le même compte rétroactif, cotisation entière aux taux réels jusqu'à la bascule, puis un **taux unique de 18 %** à compter de 2026 — salariale et patronale additionnées, le même pour tous les statuts. Par-dessus, deux ajouts. Une **cotisation capitalisée de 5 %**, prélevée sur la même assiette **en plus** de la répartition, placée sur des titres sans risque à des maturités qui raccourcissent à l'approche du départ, servie en rente viagère selon la table du modèle, et **transmissible** aux héritiers tant qu'elle n'est pas liquidée : elle est tenue dans un compartiment distinct, jamais confondue avec la pension notionnelle. Et une **garantie vieillesse** qui remplace l'ASPA : 800 € par mois par personne, plus 250 € d'allocation d'isolement pour qui vit seul, individualisée (la pension du conjoint ne compte pas) et financée par l'impôt. Mêmes âges de départ que le scénario 4. |

Les comptes sont revalorisés, par défaut, sur la croissance de la **masse
salariale** — l'assiette des cotisations, donc le rendement qu'un système en
répartition peut servir sans changer son taux de cotisation. Sept autres règles
sont disponibles, dont le **triple lock inversé** qui a donné son cahier des
charges à ce dépôt : `indexation=triple_lock_inverse`. Le choix pèse lourd,
et le simulateur affiche d'office ce qu'il déplace.

Les scénarios **2 et 3 ne portent au compte que la part salariale** — ce que
l'assuré a supporté lui-même, la même grandeur pour tous les statuts. Les
scénarios **4 et 5 y ajoutent la part patronale**. Pour un non-salarié, qui n'a
pas d'employeur, les quatre se réduisent à deux.

```python
from retraite_notionnelle import Parametres
from retraite_notionnelle.simulateur import Simulateur

simulateur = Simulateur(Parametres())
print(simulateur.simuler(simulateur.carriere_simple(
    annee_naissance=1955, sexe="H", affiliation="agent_sncf",
    age_debut=20, age_liquidation=50,
    niveau_salaire=1.1, profil_carriere="ascendant",
)).tableau())
```

```
Agent de conduite SNCF né en 1955, parti à 50 ans (quinze ans avant l'âge de référence)

Scénario                                                          Courants   Constants   Mensuel    Écart
--------------------------------------------------------------------------------------------------------
1. Système actuel                                                  35,435€     28,280€    2,357€     réf.
2. Notionnel rétroactif, part salariale                             8,483€      6,770€      564€   -76.1%
3. Notionnel dès 2026, part salariale                              27,029€     21,571€    1,798€   -23.7%
4. Notionnel rétroactif, salariale + patronale                     49,581€     39,570€    3,298€   +39.9%
5. Notionnel dès 2026, salariale + patronale                       32,000€     25,539€    2,128€    -9.7%
6. Notionnel rétroactif, 18 % dès 2026, garantie vieillesse        47,051€     37,551€    3,129€   +32.8%
```

> Les scénarios 4 et 5 sont les scénarios 2 et 3, à une différence près et une
> seule : **ce qui alimente le compte**. Même carrière, même indexation, même
> liquidation, mêmes droits acquis figés à la bascule. L'écart entre 2 et 4
> mesure donc exactement une chose — ce que verse l'employeur.
>
> Les scénarios 3 et 5 sont ici identiques au système actuel parce que cet agent
> a liquidé en 2005, avant la bascule : ses droits sont intégralement acquis. Le
> scénario 6 est identique au scénario 4 pour la même raison : aucune de ses
> années n'est cotisée à 18 %, et à 50 ans la garantie vieillesse n'est pas
> ouverte.

> **Le scénario 6 est la proposition du Parti libéral français**, et il se lit
> contre le scénario 4 : même compte rétroactif, cotisation salariale et
> patronale confondues, mêmes âges, même indexation, même liquidation. Trois
> choses changent. Le taux — 18 % pour tous à compter de 2026, là où le
> scénario 4 porte les taux réellement en vigueur de chaque régime ; ce qui a
> été cotisé avant 2026 sous le système actuel reste porté au compte tel quel,
> et qui a liquidé avant n'a aucune année à 18 %. Pour les années d'après, les
> statuts qui cotisaient plus descendent, ceux qui cotisaient moins remontent.
> Un plancher — la seule
> ligne des scénarios notionnels qui ne vienne pas d'une cotisation —, servi à
> partir de 65 ans comme l'ASPA, mais **individualisé** : à 300 € et 1 500 €
> dans un couple, l'ASPA ne sert rien, la garantie sert 500 € au premier. La
> page de simulation détaille la garantie étape par étape, et la page Coût
> compte à part ce que l'impôt en finance.
>
> Et un **pilier capitalisé obligatoire** : 5 % de la même assiette, prélevés
> en plus des 18 %, à compter de 2026. Ils ne passent pas par le compte
> notionnel ; ils constituent un capital, placé sur des titres sans risque et
> logé dans l'enveloppe du PER. Le total prélevé reste inférieur à celui
> d'aujourd'hui : 18 + 5 = 23 %, contre 28 % pour un salarié du privé. Le
> modèle le tient dans un compartiment à part, et les six sorties — tableau,
> page, JSON — affichent toujours deux lignes nommées plutôt qu'une somme.
> Ce qui les sépare n'est pas un détail de présentation : une pension de
> répartition s'éteint avec son titulaire, un capital se transmet.

> **Le scénario 2 n'est pas une proposition de réforme**, et l'écart qu'il
> affiche ne mesure pas l'effet des comptes notionnels. Deux raisons, et aucune
> des deux n'est le passage au notionnel. La première : il ne porte au compte
> que la part salariale — un système notionnel réel serait alimenté par la
> cotisation entière, et c'est le scénario 4 qui la porte. La seconde, plus
> lourde encore : la règle d'indexation retenue, voir
> [« La règle d'indexation domine tout le reste »](#1-la-règle-dindexation-domine-tout-le-reste)
> plus bas. Le modèle permet de séparer ces effets ; c'est même son principal
> résultat.

---

## Ouvrir le simulateur

### 👉 [g-pliberal.github.io/retraitecomptenotionelle](https://g-pliberal.github.io/retraitecomptenotionelle/)

Le site du Parti libéral français le sert aussi, sous
[partiliberalfrancais.fr/retraite/](https://partiliberalfrancais.fr/retraite/) :
la même page, copiée telle quelle. Ce que ce site doit savoir du simulateur —
peu de chose — est dans `docs/integration-partiliberalfrancais.md`.

Rien à installer, rien à lancer : une adresse à ouvrir. Le modèle et ses données
de référence s'exécutent **dans votre navigateur**. Aucune donnée saisie ne
quitte votre machine, puisqu'il n'y a pas de serveur de calcul. Le premier
chargement transfère <!--chiffre:poids_comprime(moteur/donnees.json + moteur/style.css + moteur/js/*.js + index.html)-->679<!--/--> Ko compressés
(<!--chiffre:poids(moteur/donnees.json + moteur/style.css + moteur/js/*.js + index.html)-->4 079<!--/--> Ko bruts) et prend quelques dixièmes
de seconde ; les suivants sont immédiats.

Six pages. **Programme** est l'accueil : la proposition du Parti libéral
français pour les retraites — ce qu'est le système actuel, ce qu'est un compte
notionnel, en quoi il est plus juste et plus lisible, ce qu'il change à la
justice entre générations, ce que devient la garantie vieillesse, et les étapes
qui mènent de l'un à l'autre. Puis **Simuler** (une carrière — en un ou
plusieurs métiers, ou bien **lue sur votre relevé** année par année —, avec le
détail du calcul, la décomposition de l'écart règle par règle et la cascade qui
mène du scénario 1 au scénario 3), **Cas types** (la grille 13 carrières ×
7 générations), **Coût** (ce qui rentre, ce qui sort et ce qui manque —
trois chiffres et deux graphiques en tête de page, qui se lisent au survol et se
téléchargent en image), **Méthode**, **Données** (l'état de fiabilité des
séries). Chacune est bâtie de la même façon : ce qui répond à la question en
tête de page, et tout ce qui la justifie dans des sections repliées qui se
parcourent comme un sommaire. Le site ne porte aucune mention légale : il est
encarté dans partiliberalfrancais.fr, qui l'édite et l'héberge, et qui porte donc
l'identification de l'éditeur, la politique de données personnelles et la
déclaration d'accessibilité. Ce que le dépôt ne peut pas déléguer — la licence
du code, celle des infographies, l'obligation de citer le producteur d'une
série — se lit sous **Données**, section « Licences et réutilisation ».

La simulation vit sous `#/simuler`, et son adresse contient tous ses
paramètres — elle peut être citée ou partagée telle quelle. Chaque résultat est
consultable en JSON au bas de la page.

<details>
<summary>Comment la page fonctionne, et comment on sait qu'elle dit vrai</summary>

`index.html` charge deux choses : `moteur/donnees.json`
(<!--chiffre:poids(moteur/donnees.json)-->2 954<!--/--> Ko — les séries, les
tables de mortalité observées de 1899 à 2024, la pyramide des âges de 1962 à
2070, les <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise|partiel)-->72<!--/--> fiches de régime) et
`moteur/js/`, un portage du modèle en JavaScript sans aucune bibliothèque. Le site est servi depuis la racine
du dépôt, telle quelle : c'est ce que GitHub Pages publie sans aucun réglage, et
`.nojekyll` demande que les fichiers soient servis sans transformation. Rien
n'est chargé depuis un CDN ou un service tiers, ce qu'un test vérifie : le site
fonctionne derrière un réseau fermé, et survivra à la disparition de n'importe
quel hébergeur.

Le site a d'abord exécuté le Python lui-même, par [Pyodide](https://pyodide.org).
C'était le choix le plus sûr — un seul code — mais il faisait télécharger
13,5 Mo d'interpréteur pour faire tourner 263 Ko de modèle, soit cinquante fois le
poids de ce qu'on voulait exécuter.

Le risque d'un portage, c'est qu'il déplace un chiffre sans que rien n'échoue.
Il est traité de front : **le Python de `src/` reste la référence**, et
`scripts/construire_temoins.py` fige depuis lui
<!--chiffre:entrees(tests/temoins/simulations.json:)-->485<!--/--> simulations complètes et
<!--chiffre:entrees(tests/temoins/pages.json:)-->43<!--/--> rendus de page, dans `tests/temoins/`.
`node --test` rejoue le tout côté JavaScript et compare valeur par valeur —
<!--chiffre:a_verifier(le compte des nombres comparés demande de lancer node --test)-->10 615<!--/--> nombres,
dont <!--chiffre:a_verifier(la part identique au bit près demande de lancer node --test)-->97,9<!--/--> % identiques
au bit près, l'écart maximal étant de quelques *ulp* (5 · 10⁻¹⁵ ; un *ulp* vaut
2 · 10⁻¹⁶, la précision d'un flottant). Les pages, elles, sont comparées caractère par caractère : le
formatage à la française reproduit jusqu'à l'arrondi au pair de Python, faute de
quoi un « <!--chiffre:illustration()-->−12,5<!--/--> % » deviendrait
« <!--chiffre:illustration()-->−13<!--/--> % » d'un côté et « <!--chiffre:illustration()-->−12<!--/--> % » de l'autre.

Des cas figés ne prouvent que ce qu'on a pensé à figer. Un second contrôle tire
donc des carrières au hasard — graine fixe, donc reproductible —, les calcule en
Python et les fait recalculer par le site : mêmes chiffres exigés, à 10⁻⁹ près.

`pytest` lance cette comparaison, il n'y a donc qu'une commande à retenir. Les
deux fichiers que charge le site sont produits par
`python scripts/construire_donnees.py` — le paquet de données depuis `data/`, et
`moteur/style.css` depuis la feuille de style du module Python, qui reste écrite
en un seul endroit. Le test `test_le_paquet_est_a_jour` échoue si l'un des deux a
été oublié.

</details>

## Ouvrir le site en local

Le site est un ensemble de fichiers statiques, servis depuis la racine du dépôt.
N'importe quel serveur de fichiers suffit — il n'y a pas de serveur de calcul,
et rien à construire au préalable :

```bash
python -m http.server 8000        # puis http://127.0.0.1:8000
```

## En Python, hors du site

Le site expose le modèle en six pages. Pour l'interroger autrement — un
calcul par lots, une variante de paramètres, un chiffre à vérifier à la main —
le modèle de référence s'appelle directement. La seule dépendance est PyYAML.

```bash
pip install -e .
```

```python
from retraite_notionnelle import Parametres
from retraite_notionnelle.castypes import calculer_cas_types
from retraite_notionnelle.simulateur import Simulateur

simulateur = Simulateur(Parametres())

# Simuler une carrière : cinq informations suffisent
carriere = simulateur.carriere_simple(
    annee_naissance=1960, sexe="H", affiliation="salarie_prive_non_cadre",
    age_debut=20, age_liquidation=62,
)
print(simulateur.simuler(carriere).tableau())

# Au mois près — la date de liquidation commande les mois cotisés de l'année
# du départ, les trimestres qu'ils valident et le diviseur actuariel
simulateur.carriere_simple(
    annee_naissance=1961, mois_naissance=9, sexe="H",
    affiliation="salarie_prive_non_cadre",
    age_debut=20 + 6 / 12, age_liquidation=64 + 7 / 12,
)

# Plusieurs métiers dans une vie : chacun court jusqu'au début du suivant,
# le dernier jusqu'à la liquidation
from retraite_notionnelle.carriere import Metier

print(simulateur.simuler(simulateur.carriere_parcours(
    annee_naissance=1975, sexe="H", age_liquidation=64,
    metiers=[
        Metier("salarie_prive_non_cadre", age_debut=21, niveau_salaire=0.9),
        Metier("contractuel_public", age_debut=34, niveau_salaire=0.8),
        Metier("artisan", age_debut=47, niveau_salaire=1.5),
    ],
)).tableau())

# Le chemin le plus exact : le relevé de carrière, année par année. Rien n'y est
# reconstitué — ni le revenu, en euros de chaque année, ni les trimestres validés.
# C'est ce que le champ « Relevé de carrière » du simulateur reçoit.
from retraite_notionnelle.carriere import LigneRelevee

print(simulateur.simuler(simulateur.carriere_releve(
    annee_naissance=1960, sexe="H", age_liquidation=62,
    releve=[
        LigneRelevee(annee=annee, affiliation="salarie_prive_non_cadre",
                     revenu=20000.0 + 500 * (annee - 1985), trimestres=4)
        for annee in range(1985, 2022)
    ],
)).tableau())

# Le cas général : grille cas type × génération
print(calculer_cas_types(simulateur).tableau())

# Les 62 statuts et les 72 régimes du catalogue
for regime in simulateur.catalogue:
    print(f"{regime.code:<26} {regime.famille:<22} {regime.nom}")
```

Le tableau de bord des données — l'état de fiabilité de chaque série, à lire en
premier — est la page **Données** du site. En Python,
`journal_certification(Parametres().racine_donnees)` produit la même matière.

## En bibliothèque

```python
from retraite_notionnelle import Parametres
from retraite_notionnelle.simulateur import Simulateur

simulateur = Simulateur(Parametres())
carriere = simulateur.carriere_simple(
    annee_naissance=1975, mois_naissance=4, sexe="F",
    affiliation="fonctionnaire_etat",
    age_debut=23, age_liquidation=64 + 7 / 12, part_primes=0.20,
)
print(simulateur.simuler(carriere).tableau())
```

---

## Ce que le modèle fait

| Exigence | Réalisation |
|---|---|
| Comptes notionnels rétroactifs depuis l'origine de la répartition | Origine 1941 (AVTS), paramétrable à 1945 |
| Chaque réforme laisse une trace dans chaque fiche | Un calendrier central des réformes (`data/reference/legislation/reformes.yaml`, 36 entrées de 1945 à 2026) et, par régime, les articles de code ou de décret qui portent ses paramètres (`regimes/pivots.yaml`) ; `scripts/calendrier_regimes.py` lit leurs versions dans l'index LEGI et les confronte aux périodes des fiches, et un test impose que toute réforme touchant un régime soit coupée, absorbée par un drapeau par génération, ou déclarée non appliquée avec sa raison |
| Tous les régimes, actuels **et** disparus | 72 régimes calculés : AGIRC, ARRCO, CANCAVA, ORGANIC, RSI, mines, SEITA, chemins de fer secondaires… — et un [inventaire](docs/regimes.md) de **quatre-vingt-neuf lignes** — tous les régimes obligatoires ayant existé depuis 1930, calculés ou non —, ancré sur `R. 711-1`, qui dit ce qui manque à chacun et pourquoi ; un test le tient aligné sur le catalogue, et ses tableaux sont produits par script |
| Départ trop tôt = pension réduite | Âge de référence à **64 ans** — l'âge légal d'ouverture des droits — à partir de la bascule ; avant elle, un **cliquet** que l'abaissement de 1982 ne fait pas redescendre |
| Régimes à départ précoce traités au même étalon | SNCF à 50 ans = 15 ans d'anticipation ; Opéra à 40 ans = 25 ans |
| Indexation par triple lock inversé, depuis l'origine | `min(inflation, salaire moyen, productivité réelle)`, appliqué aux comptes en constitution. Le modèle s'arrête à la liquidation : il ne revalorise pas les pensions servies, et n'en calcule qu'une, dans les euros de l'année de départ |
| Six résultats comparables | Système actuel / notionnel rétroactif / notionnel prospectif sur la part salariale, puis les deux mêmes comptes notionnels part patronale comprise, puis la proposition libérale — le compte rétroactif à 18 % pour tous, avec une garantie vieillesse individualisée financée par l'impôt |
| Cas particulier **et** cas général | Simulation individuelle + grille 13 cas types × 7 générations |
| Fusion des régimes au cas le plus défavorable | Âge 64/67, 172 trimestres, carrière entière, assiette déplafonnée, zéro avantage |
| Droits acquis respectés à la bascule | Conversion à l'âge de référence par défaut — le seul endroit où l'âge de départ pèse sur les droits d'avant la bascule, donc ce qui empêche de gagner à partir tôt. La référence étant désormais 64 ans, un départ à 64 ans ne perd plus rien et seul un départ plus précoce paie ; l'âge de départ effectif reste offert en variante, et la cascade de calcul est affichée |
| Statuts comparables au même étalon | Les fiches publiques ne portent que la retenue de l'agent ; elle est alignée sur l'effort contributif total du privé, sans quoi on compare un demi-effort à un effort entier |
| Part salariale et part patronale distinguées, pour tous | `part_salariale` dans chaque fiche de salariés — 40,87 % au régime général en 2023, 40 % à l'Agirc-Arrco —, et `sans_employeur` sur les statuts qui cotisent seuls |
| Part employeur du public, quand elle est publiée | Neuf régimes : taux implicite de l'État 1995-2005, taux appelé par le CAS « Pensions » 2006-2026, CNRACL depuis 1948, SNCF 1992-2018, RATP 2007-2025, IEG 2005-2020, mines depuis 1984, Opéra de Paris et Comédie-Française depuis 1992 — portés au compte par les scénarios 4 et 5, et le modèle dit sur combien d'années il a dû s'en passer |
| Capitalisation hors comparaison | Le RAFP et les assurances sociales de 1930 sont PROVISIONNÉS : leur rente sort d'un placement, non de la cotisation des actifs. Une réforme de la répartition ne les atteint pas — ils sont donc retirés des **six** totaux et servis à l'identique, à leur propre barème, affichés à côté |
| Le mois, là où le droit le date | Date de liquidation, année d'entrée et année de départ portées au compte au prorata de leurs mois, trimestres bornés aux trimestres civils écoulés, diviseur lu à l'âge exact, circulaire de revalorisation en vigueur à la date, générations que la loi coupe au 1<sup>er</sup> juillet 1951 et au 1<sup>er</sup> septembre 1961. Le pas du moteur reste l'année, parce que les séries le sont — voir [« Le mois, là où le droit le date »](docs/limites.md#le-mois-là-où-le-droit-le-date) |
| Trimestres acquis par le revenu, pas par le temps | 150 SMIC horaires depuis 2014, 200 avant : un temps très partiel valide moins de quatre trimestres |
| Motif d'interruption lu, pas seulement enregistré | Un chômage indemnisé ouvre des points complémentaires financés par l'UNEDIC ; un chômage non indemnisé n'ouvre rien |
| La carrière peut s'arrêter avant le départ | Une ligne de carrière peut n'être pas un emploi — chômage indemnisé ou non, maladie, accident du travail, maternité, invalidité, élever un enfant, service militaire, inactivité. Sans elle, le calcul supposerait qu'on a travaillé jusqu'au mois du départ |
| Étalon fidèle au droit, minima compris | Le scénario 1 sert le minimum contributif (au taux plein, deux prorata, écrêté), le minimum garanti de la fonction publique, l'ASPA, la majoration pour enfants, les trimestres accordés au titre des enfants — MDA du régime général et des régimes alignés, bonification de la fonction publique —, la surcote parentale de 2023, l'AVPF et la garantie minimale de points de l'Agirc |
| Décote propre à la fonction publique | Article L. 14 : coefficient et âge d'annulation montent en charge de 2006 à 2020, et cet âge est la limite d'âge du grade, non 67 ans |
| Catégorie active et militaires, au lieu d'être traités en sédentaires | Cinq statuts classés — catégorie active et super-active de l'État et de la CNRACL, ouvriers de l'État — et deux statuts militaires. Le classement tient à l'EMPLOI, qu'aucune donnée de carrière ne révèle : il se déclare. Le modèle oppose alors l'âge anticipé ou minoré de l'article L. 24 (57 et 52 ans, 59 et 54 après 2023, avec leurs deux montées en charge), l'âge d'annulation de décote propre au classement (62 et 57 ans, non 67), et la condition de durée de services classés (17 et 27 ans) vérifiée sur la carrière. La pension militaire, elle, ne s'ouvre pas à un âge mais à une durée — 17 ans de services pour un non-officier, 27 pour un officier —, sans surcote et avec la décote du II de l'article L. 14, dix trimestres au plus |
| Chaque régime liquide sur ses années | Le salaire de référence ne balaie plus toute la carrière : un polypensionné ne liquide pas sa pension civile sur son dernier salaire privé |
| Le droit ouvre-t-il ce départ ? | Âge légal du régime ou carrière longue ; sinon le montant est marqué comme un contrefactuel, pas une pension servie |
| Suppression des minima | Ni minimum contributif, ni minimum garanti, ni ASPA : peu cotisé, peu de retraite |
| Suppression des avantages | Ni majorations enfants, ni MDA, ni AVPF, ni bonifications, ni réversion, ni trimestres gratuits |
| Tout le monde peut simuler | 62 statuts d’affiliation, cinq informations suffisent |
| La cotisation de chaque année, pas une moyenne de période | Le compte notionnel reçoit le taux de l'année — 8,5 % en 1967, 12,9 % en 1979, 16,35 % en 1991 au régime général —, lu dans `taux_cotisation_annuels.csv` (1 074 valeurs depuis les barèmes datés d'OpenFisca-France, pour le régime général, les salariés agricoles, les cultes, Mayotte, Saint-Pierre-et-Miquelon, les artisans, les commerçants et le RSI) et appliqué année par année au chargement des fiches, qui gardent leur moyenne pour les années d'avant 1967 |
| Le marin cotise et liquide sur le forfait de sa catégorie | Les vingt salaires forfaitaires des marins sont lus au Journal officiel, arrêté par arrêté depuis 2008 (`salaires_forfaitaires.csv`, 380 montants certifiés) ; le moteur range le marin dans la catégorie la plus proche de son revenu — convention nommée — et cotise comme il liquide sur ce forfait, dans les deux moteurs |
| Avant 1967, la part vieillesse des assurances sociales, datée | Les taux de 1945 à 1966 viennent du tableau du COR d'après la Cnav (6 + 6 en 1945, 6 + 10 en 1947, 6 + 15 en 1966), et la part vieillesse est la convention nommée de 8,5/21 — celle de l'ordonnance de 1967 —, au niveau estimé ; la retenue des fonctionnaires est à 8,9 % dès 1989 (loi n° 89-18, art. 23), les points CARMF d'avant 1991 valent 1,33 point d'après |
| Un statut ne se déclare qu'aux dates où son régime recrutait | Le menu date chaque statut — « Mineur (recrutés avant septembre 2010) » — et grise ceux que l'entrée saisie ferme ; le calcul refuse un jeune d'aujourd'hui qui se déclarerait mineur, et nomme le statut de droit commun qui porte le même calcul. La fermeture se lit au mois, sur la date d'entrée dans le métier : la loi ferme la RATP « aux recrutés à compter du 1<sup>er</sup> septembre 2023 », et l'article 1<sup>er</sup> de la loi n° 2023-270 ne ferme que cinq régimes — RATP, IEG, clercs de notaires, Banque de France, CESE —, non l'Opéra, la Comédie-Française ni le port de Strasbourg, que le dépôt croyait fermés |
| Un revenu se saisit comme un revenu | « Revenu brut mensuel : 2 900 € », en euros d'aujourd'hui — plus un multiple du salaire moyen que personne ne connaît, resté à un lien de là pour qui raisonne en relatif, montants convertis au passage. Le champ dit **brut** et donne l'échelle chiffrée (SMIC, moyenne, plafond) ; le modèle, lui, ne connaît toujours que le multiple, et l'euro n'entre qu'à un seul endroit |
| Une carrière, plusieurs métiers | On faisait autrefois le même métier toute sa vie, c'est devenu l'exception : la carrière se décrit comme une suite de métiers, chacun avec son statut et son niveau de revenu, et chaque changement fait passer d'un régime à un autre. L'année du changement revient au métier qui en occupe le plus de mois — les régimes liquident à l'année —, mais le revenu porté au compte reste la somme de ce que les deux ont payé |
| Utilisable sans rien installer | Le modèle s'exécute dans le navigateur, sur une simple adresse |
| Étalon confronté à une seconde implémentation | Les cinq familles de régimes qu'expose **OpenFisca-France-Pension** — régime général, pension civile (État et CNRACL), Arrco d'avant 2019, Agirc des cadres, Ircantec — sont rejouées sur cinquante-huit profils par ce modèle écrit par d'autres à partir des mêmes textes ; les régimes alignés (MSA des salariés agricoles, artisans, commerçants), qu'il ne modélise pas, se confrontent à l'oracle du régime général, puisque la loi les calcule comme lui. Durée, décote, taux, proratisation, points, prix d'achat et valeur du point concordent, et chaque confrontation a fait trouver des erreurs des deux côtés — chez nous, le barème de décote de la fonction publique lu à l'année de liquidation au lieu de l'année d'ouverture du droit, la montée en charge 2004-2008 de sa durée de services, l'assiette de la tranche B de l'Ircantec et son coefficient d'anticipation |
| Salaires revalorisés par la circulaire, pas par une règle | Les coefficients qui revalorisent les salaires portés au compte sont LUS dans les circulaires de la Cnav — dix colonnes publiées, perceptions depuis 1930 : la règle « les salaires jusqu'en 1986, les prix depuis » les sur-revaluait de 12 % sur quarante ans, et le salaire de référence retient les N *meilleures* années — changer les coefficients change lesquelles |
| Deux durées là où le droit en a deux | La durée requise pour le taux plein (L. 161-17-3) et la durée maximale prise en compte par la proratisation (R. 351-6), que le modèle confondait |
| Points convertis à leur vraie unité | Les coefficients des fusions sont LUS dans les accords — un point Arrco vaut un point Agirc-Arrco, un point Agirc en vaut 0,347798289 —, et l'unification Arrco de 1999 est traitée comme le changement d'unité qu'elle est |
| Portage vérifié, pas cru sur parole | Le site rejoue 469 simulations témoins figées depuis le modèle Python — chaque statut d’affiliation à six générations, née en 1925, 1935, 1945, 1955, 1965 et 1975, pour que les règles anciennes de chaque régime soient visitées autant que les récentes ; un test oblige ce balayage à couvrir tous les statuts et toutes ces générations |

---

## Six résultats à connaître avant de lire les chiffres

### 1. La règle d'indexation domine tout le reste

Le modèle revalorise **par défaut les comptes sur la croissance de la masse
salariale** — le taux d'équilibre de la répartition, celui que la théorie des
comptes notionnels désigne (voir §1 ter). Ce n'est pas la règle qui a motivé ce
dépôt : celle-là, le **triple lock inversé**, est à un paramètre de distance
(`indexation=triple_lock_inverse`). Un défaut doit être ce qu'on retient faute
d'instruction contraire, pas ce qu'on cherche à démontrer — et c'est bien la
règle demandée qui produit les écarts les plus spectaculaires.

Le triple lock inversé, pris à la lettre, compare deux taux **nominaux**
(inflation, salaire moyen) à un taux **réel** (productivité). Dès que l'inflation
dépasse la productivité — soit presque toute la période 1945-1985 — c'est la
productivité qui l'emporte.

| Règle | Comptes 1941-2025 | Prix | Pouvoir d'achat conservé |
|---|---|---|---|
| Triple lock inversé, littéral | ×4,9 | ×322,2 | **1,5 %** |
| Moyenne des trois taux | ×175,7 | ×322,2 | 54,5 % |
| Triple lock inversé, tout en nominal | ×223,3 | ×322,2 | 69,3 % |
| Indexation sur les prix | ×322,2 | ×322,2 | 100 % |
| Médiane des trois taux | ×397,6 | ×322,2 | 123,4 % |
| **Revalorisation réellement pratiquée** | **×1 538,2** | ×322,2 | **477,4 %** |
| Masse salariale (règle d'équilibre) | ×3 685,1 | ×322,2 | 1 143,7 % |
| PIB nominal | ×3 442,3 | ×322,2 | 1 068,6 % |
| PIB nominal, lissé sur 5 ans (Italie) | ×4 152,7 | ×322,2 | 1 288,8 % |

Une cotisation de 1950 ne conserve donc que 1,5 % de sa valeur réelle. Dans le
scénario rétroactif, **l'essentiel de la baisse affichée vient de la règle
d'indexation, pas du passage aux comptes notionnels**.

C'est la règle telle qu'énoncée, appliquée sans correctif. Pour séparer les deux
effets : `indexation=triple_lock_inverse_nominal` (règle homogène, toujours
austère) ou `indexation=revalorisation_portee_au_compte` (effet propre des
comptes notionnels). Chaque simulation web affiche cette décomposition d'office.

La dernière ligne du tableau est la seule qui ne soit pas une hypothèse : c'est
le coefficient que les arrêtés annuels ont réellement appliqué aux salaires
portés au compte, celui dont le scénario 1 se sert pour son salaire de
référence. Il vaut ×1 538, près de cinq fois les prix, parce que le régime
général a revalorisé sur les **salaires** jusqu'en 1986 et sur les prix
seulement depuis 1987. Ce README, la documentation et le site ont longtemps
désigné `indexation=prix` comme la règle qui neutralise l'indexation :
c'était faux d'un facteur cinq, et cela imputait aux comptes notionnels un
écart qui venait encore du choix de la revalorisation.

Ce que la correction déplace est plus modeste que ce facteur cinq ne le
suggère, et il faut le dire aussi : les cotisations d'une carrière se
concentrent sur ses dernières années — en euros courants, une année de fin de
carrière pèse dix à trente fois une année de début —, et c'est là que les deux
règles coïncident. Sur le scénario rétroactif, pour un salarié du privé non
cadre entré à 20 ans et parti à 62 :

| Génération | Carrière | Ligne de référence « Prix » | Ligne corrigée | Écart |
|---|---|---|---|---|
| 1920 | 1940-1982 | -89,9 % | -84,7 % | **+5,2 pt** |
| 1930 | 1950-1992 | -89,0 % | -87,5 % | +1,5 pt |
| 1945 | 1965-2007 | -85,1 % | -85,1 % | 0,0 pt |
| 1958 | 1978-2020 | -81,0 % | -81,4 % | **-0,4 pt** |
| 1990 | 2010-2052 | -78,3 % | -78,3 % | 0,0 pt |

L'écart change même de signe pour les carrières entièrement postérieures à
1987 : depuis 1990 les arrêtés ont revalorisé un peu moins vite que les prix
(×1,69 contre ×1,80), l'indexation légale étant assise sur l'inflation de
l'année précédente. L'erreur portait donc sur l'indice cumulé et sur ce qu'on
en disait, pas sur l'ordre de grandeur des résultats — mais une ligne de
référence fausse reste une ligne de référence fausse, et c'est sur elle que
reposait la phrase « l'écart entre la ligne Prix et le système actuel mesure
l'effet propre des comptes notionnels ».

### 1 bis. Le minimum n'est pas la seule statistique : médiane et moyenne

Le minimum de trois séries est une règle sévère par construction. Deux variantes
gardent **exactement les mêmes trois termes** et ne changent que ce qu'on en
retient — `indexation=mediane_trois_taux` et `indexation=moyenne_trois_taux`.
Elles isolent donc le coût du choix du minimum, à termes inchangés. Le résultat
n'est pas celui qu'on attend :

- la **médiane** est presque toujours l'inflation (43 années sur 85) ou le
  salaire moyen (20) : deux taux **nominaux**. Elle suit donc les prix et les
  dépasse même légèrement — ×397,6 contre ×322,2 — parce que le salaire moyen
  l'emporte quand la productivité est forte. Sur les 85 années, elle ne passe
  sous l'inflation que 18 fois, contre 61 pour le minimum. **Ce n'est plus une
  règle d'austérité** ; c'est, en pratique, une indexation prix-salaires ;
- la **moyenne** est plus sévère que la médiane, et même que les prix — ×175,7,
  soit 54,5 % du pouvoir d'achat. La raison n'est pas la statistique mais le
  mélange : la moyenne incorpore **un tiers de productivité réelle chaque
  année**, y compris pendant les années à dix ou vingt points d'inflation, là où
  le minimum et la médiane ne retiennent le terme réel que les années où il
  gagne. Le taux obtenu n'est en outre celui d'aucun agrégat observé.

Autrement dit : si l'objectif est d'adoucir la règle sans la vider, la médiane
le fait ; la moyenne, elle, est un objet composite dont la sévérité vient d'un
artefact de construction plutôt que d'un choix assumé. Les deux sont disponibles
dans le formulaire, et le tableau « D'où vient l'écart » de chaque simulation
les affiche côte à côte.

### 1 ter. La règle que la théorie désigne : la masse salariale

Les six règles précédentes sont des choix. Il en existe une septième qui n'en
est pas un : en répartition, le rendement qu'un système peut servir sans changer
son taux de cotisation est **la croissance de son assiette** — la masse
salariale, soit le salaire moyen multiplié par l'emploi salarié (Samuelson 1958,
Aaron 1966). C'est le taux d'indexation des comptes notionnels suédois,
italiens, polonais et lettons, à des variantes près, et c'est le seul candidat
qui découle d'un argument plutôt que d'une intention.

`indexation=masse_salariale` la sert, depuis les salaires et traitements bruts
des comptes nationaux (D11, INSEE, idbank 011785411, certifiés depuis 1950).
Sur 1941-2025 elle vaut **×3 685, soit onze fois les prix** : l'emploi salarié a
doublé depuis 1950, et cette croissance-là s'ajoute chaque année à celle des
salaires. C'est de très loin la règle la plus généreuse du tableau — une règle
d'équilibre, pas une règle d'austérité.

Deux réserves, à lire avant de s'en servir :

- **elle crédite le compte d'un rendement collectif, alors que les scénarios 2
  et 3 n'y versent qu'une cotisation partielle.** Le taux d'équilibre est celui
  du système entier ; y adosser la seule part salariale mélange deux périmètres.
  C'est aux scénarios 4 et 5, qui portent la cotisation entière, qu'elle se
  compare sans biais — et l'écart au système actuel y passe de -81 % à -51 %
  pour la génération 1930, de -69 % à -41 % pour 1945 ;
- **1930-1949 est estimé**, faute de comptes nationaux : ces vingt années
  supposent l'emploi salarié constant et reprennent la variation du salaire
  moyen. La fiabilité `estimee` le dit et se propage jusqu'au résultat.

Pour les curieux, une neuvième règle : **`indexation=pib_nominal`**,
l'assiette la plus large — elle capte ce que la masse salariale perd quand la
valeur ajoutée se déplace vers les revenus non salariaux.

### 1 quater. Le lissage pluriannuel, qui n'est pas une règle

Le lissage applique une moyenne glissante de N années au taux que la règle
produit — **n'importe laquelle des neuf**, et N est libre, de 1 à 30 ans. Ce
n'est donc pas une dixième règle
mais un réglage orthogonal, et il répond à une question que le choix de la règle
ne pose pas : la **loterie de cohorte**.

Sur le PIB nominal brut, une cotisation de 1980 vaut ×5,44 à une liquidation de
2019 et **×5,18 en 2020** : attendre un an fait *perdre*, parce que l'année
traversée s'est mal passée. Rien dans la carrière ne le justifie — c'est le
calendrier qui tranche. Avec `lissage=5`, le recul disparaît (×6,64 puis
×6,71) : le trou de 2020 est absorbé par les quatre années qui l'entourent. Sur
1950-2025, le PIB nominal brut compte deux années où liquider plus tard rapporte
moins ; lissé sur trois ou cinq ans, aucune.

C'est le mécanisme des comptes notionnels italiens —
`indexation=pib_nominal&lissage=5` **est** la règle italienne, dont le modèle
ne reprend que le taux, pas le reste du système (décalage de publication de
deux ans, coefficients de transformation, planchers). Mais rien n'oblige à le
réserver au PIB : le lissage s'applique aussi bien au triple lock inversé qu'à
la masse salariale.

Une réserve de lecture, valable pour toutes les lignes lissées du tableau
ci-dessus : sur quatre-vingts ans, une moyenne glissante **n'est pas neutre**.
Elle revient à mesurer la croissance depuis une base reculée d'environ la moitié
de la fenêtre, ce qui gonfle le cumul d'une vingtaine de pour cent à cinq ans —
sans qu'aucune série ait changé. Sur une carrière, l'écart entre lissé et non
lissé reste d'un à deux points (règle par défaut, génération 1930 : -81,5 % sans
lissage, -80,2 % à trois ans, -79,1 % à cinq).

Et un résultat qui recadre tout le reste : même sous cette règle, le scénario
rétroactif reste 70 à 81 % en dessous du système actuel (scénario 2), et 28 à
51 % en dessous avec la cotisation entière (scénario 4). L'indexation explique
donc une part importante de l'écart, mais pas la totalité : le reste tient à ce
que le système actuel sert plus qu'un compte strictement contributif.

### 2. La fusion augmente les cotisations des indépendants

Le régime unique applique 25,73 % sur assiette déplafonnée. Pour les professions
libérales et les indépendants, qui cotisent aujourd'hui moins et sous plafond,
c'est une forte hausse de prélèvement — et donc de pension. C'est la seule ligne
du tableau des cas types qui progresse ; le résultat est correct, mais il traduit
un effort contributif accru, pas un avantage accordé.

### 3. La part patronale pèse plus lourd que la part salariale

Une cotisation retraite a deux parts, et le modèle sait maintenant les
distinguer **symétriquement**, public et privé. C'est ce qui sépare les
scénarios 2 et 3 des scénarios 4 et 5, et rien d'autre.

Cela n'a pas toujours été possible. Les fiches de régime ne portaient pas la
même grandeur selon le secteur : le total salarié + employeur pour le privé, la
seule retenue de l'agent pour la fonction publique. Le modèle refermait cet
écart de périmètre par une convention — prêter au public la part employeur du
privé — qui rendait les statuts comparables au prix d'un chiffre inventé. Deux
séries l'en dispensent :

- **`part_salariale`** dans les fiches : la fraction du taux que l'assuré
  supporte. 40,87 % au régime général en 2023, 40 % à l'Agirc-Arrco par la règle
  40-60 de l'ANI du 17 novembre 2017, 100 % pour un non-salarié qui paie tout.
- **La contribution employeur du public**, que le dépôt soutenait introuvable
  avant 2006. C'était vrai de l'État, et faux du reste : la CNRACL est une
  caisse depuis 1947 et publie son taux depuis 1948 ; l'État a un taux
  *implicite* reconstitué par le PLF 2011 depuis 1995 ; depuis 2006 le taux est
  appelé par décret — 49,90 %, puis 74,28 % de 2013 à 2024, 78,28 % en 2025 et
  **82,28 % en 2026** ; la SNCF publie ses composantes T1 et T2 de 2007 à 2018,
  et son taux d'avant est dans le décret qui fixe les cotisations des régimes
  spéciaux — 28,44 % de 1992 à 2006. **Six régimes s'y sont ajoutés**, tous lus
  au *Journal officiel* : la RATP (2007-2025) et les IEG (2005-2020), dont
  l'employeur verse depuis l'adossement ce que les mêmes salariés coûteraient
  au régime général et à l'Agirc-Arrco, arrêté par arrêté ; les mines, 7,75 % à
  la charge de l'exploitant sans bouger depuis 1984 ; l'Opéra de Paris et la
  Comédie-Française, 8,80 % en 1992 et 9,56 % en 2026.

```python
comparaison = simulateur.simuler(simulateur.carriere_simple(
    annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
    age_debut=22, age_liquidation=64,
    part_primes=0.2, profil_carriere="ascendant",
))
print(comparaison.tableau())

# Le détail par régime du scénario 1, que la page « Simuler » affiche aussi
for pension in comparaison.actuel.pensions_par_regime:
    print(f"{pension.regime:<28} {pension.montant:>10,.0f} €   {pension.detail}")
```

```
Fonctionnaire d'État née en 1975, 20 % de primes, partie à 64 ans

Scénario                                                          Courants   Constants   Mensuel    Écart
--------------------------------------------------------------------------------------------------------
1. Système actuel                                                  35,435€     28,280€    2,357€     réf.
2. Notionnel rétroactif, part salariale                             8,483€      6,770€      564€   -76.1%
3. Notionnel dès 2026, part salariale                              27,029€     21,571€    1,798€   -23.7%
4. Notionnel rétroactif, salariale + patronale                     49,581€     39,570€    3,298€   +39.9%
5. Notionnel dès 2026, salariale + patronale                       32,000€     25,539€    2,128€    -9.7%
6. Notionnel rétroactif, 18 % dès 2026, garantie vieillesse        47,051€     37,551€    3,129€   +32.8%
--------------------------------------------------------------------------------------------------------
   hors répartition (RAFP), servi à part, identique aux 6           1,506€      1,202€      100€         
--------------------------------------------------------------------------------------------------------
   + rente du pilier capitalisé, scénario 6 seul                    1,633€      1,303€      109€         
   = total servi par le scénario 6                                 48,684€     38,854€    3,238€   +37.4%

Qui verse la cotisation, en euros courants cumulés :
  part salariale           139,912 €   scénarios 2 et 3
  part patronale           579,314 €   soit 81% du total
  total                    719,225 €   scénarios 4 et 5
  contribution employeur publique trouvée sur 29 année(s)
```

Le scénario 6 reste ici un peu sous le scénario 4 sur sa ligne de répartition,
et c'est le taux, pas la garantie : jusqu'en 2025 son compte est celui du 4, aux
taux réels, et ce n'est que sur les années 2026-2038, cotisées à 18 % au lieu
des 82,28 % que l'État verse, qu'il s'en écarte. La pension contributive dépasse
de toute façon le plancher. Les treize années cotisées au pilier capitalisé
ajoutent 1 633 € par an, servis à part : le total du scénario 6 repasse ainsi
au-dessus du scénario 4, mais les deux lignes ne promettent pas la même chose —
la seconde s'éteint avec sa titulaire, le capital de la première se serait
transmis.

L'employeur verse ici 79 % du total. C'est l'ordre de grandeur d'un taux
d'**équilibre**, et c'est la limite du scénario 4 : 82,28 % ne signifie pas
qu'un fonctionnaire acquiert 82 % de son traitement en droits nouveaux, mais
qu'il faut aujourd'hui cette contribution pour payer les pensions
d'aujourd'hui — démographie et engagements hérités compris.

Quatre limites à connaître. Pour le public, la série couvre neuf régimes :
sept autres — FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg,
SEITA, chemins de fer secondaires — voient leur part patronale **estimée** par
l'effort d'un salarié du privé, et le modèle affiche sur combien d'années.
Aucun des neuf n'est couvert sur toute sa durée : l'État commence en 1995, la
RATP en 2007, les mines en 1984, et les IEG s'arrêtent en 2020, où le texte
cesse de chiffrer. Ces taux sont ceux de l'**employeur**, non ceux de
l'équilibre — la contribution que l'État verse par ailleurs à la RATP, aux
mines et à l'Opéra n'y est pas —, à la seule exception de la ligne de l'État,
dont le taux est précisément un taux d'équilibre. Enfin, à compter de la
bascule le régime unique remplace tous les régimes : après 2026 la part
patronale est celle du statut pivot privé, et non celle d'un employeur public
qui, par construction, n'existe plus.

Un quatrième réglage conserve l'ancienne convention, comme contrefactuel :
`part_cotisation=totale_alignee` prête au public la part employeur du privé,
et fait retrouver à un fonctionnaire et à un salarié de même rémunération
exactement la même pension.

---

### 4. Depuis 1959, la retraite a coûté quinze mille milliards

La page **Coût** répond à la question inverse de tout le reste du site : non pas
« que toucherait cet assuré ? », mais « qu'est-ce que tout cela a coûté ? ». Les
dépenses viennent des Comptes de la protection sociale de la DREES, risque
vieillesse-survie, **certifiées de 1959 à 2024** et recontrôlées contre l'API à
chaque exécution.

| | Millions d'euros |
|---|---|
| Dépense 2024, risque vieillesse-survie entier | **426,7 Md €** |
| dont répartition obligatoire | **398,8 Md €** |
| dont dépendance, capitalisation, minimum vieillesse | 27,9 Md € |
| Part du PIB en 2024 | 14,5 % |
| Cumul 1959-2024, en euros constants de 2026 | **14 987 Md €** |

C'est la deuxième ligne — la répartition obligatoire seule — qu'il faut
rapprocher des « quelque 420 milliards » que l'on cite d'ordinaire pour l'année
en cours : le total publié est plus large, et la ventilation par système dit
exactement de combien.

La ventilation couvre 1990-2024 : de 1981 à 1989 la DREES publie une autre
nomenclature, dont les périmètres ne se raccordent pas à ceux d'après. Personne
n'ayant publié le raccord, ces neuf années restent une impasse, et le total,
lui, les couvre.

Sur cette dépense observée, le modèle applique le rapport des masses de pension
entre systèmes — les treize cas types croisés avec dix-neuf générations, pondérés
par l'effectif réel de chaque génération et par celui des retraités de la caisse
de chaque cas type :

| Système | Cumul 1959-2024, euros de 2026 | Écart |
|---|---|---|
| 1. Système actuel | 14 987 Md € | réf. |
| 2. Notionnel rétroactif, part salariale | 2 842 Md € | −81,0 % |
| 3. Notionnel dès 2026, part salariale | 14 987 Md € | +0,0 % |
| 4. Notionnel rétroactif, salariale + patronale | 6 598 Md € | −56,0 % |
| 5. Notionnel dès 2026, salariale + patronale | 14 987 Md € | +0,0 % |
| 6. Notionnel rétroactif, 18 % dès 2026, garantie vieillesse | 7 218 Md € | −51,8 % |
| *dont garantie vieillesse du 6, vue par les cas types* | *621 Md €* | |

**Les scénarios 3 et 5 coûtent exactement ce que coûte le système actuel**, et
ce n'est pas un défaut du calcul : leur bascule est fixée à 2026, aucune pension
servie avant cette date n'en est modifiée, puisque les droits acquis sont
conservés. Une réforme prospective ne commence à compter qu'au premier assuré
qui liquide après elle — et cela vaut de toute réforme des retraites qui
respecte les droits acquis, pas seulement de celle-ci. Le calcul n'est d'ailleurs
pas écrit en dur : la page teste l'égalité des courbes, et les séparerait si la
bascule était avancée avant la dernière année observée.

L'écart du scénario 2 ne mesure pas, lui non plus, l'effet des comptes
notionnels : il mesure la part salariale seule — le scénario 4, qui ajoute la
part patronale, coûte 132 % de plus — et la règle d'indexation, dont le résultat
1 ci-dessus montre qu'elle domine tout. Le scénario 6 est ici le scénario 4
plus sa garantie vieillesse : aucune pension servie avant 2026 n'a une année
cotisée à 18 %.

**Les cas types ne pèsent plus d'un poids égal.** Chacun porte l'effectif des
retraités de sa caisse, publié par la DREES et lu année par année : l'agent de
conduite pèse 0,7 % et non 7,7 %, les quatre carrières du privé 63 % à elles
quatre. Ce que la convention égalitaire valait est désormais mesuré plutôt
qu'argumenté — elle donne −78,3 % au scénario 2 contre −81,0 %, et −59,8 % au
scénario 4 contre −56,0 %. Le sens du biais n'était donc pas celui qu'on
annonçait : la surreprésentation des départs très précoces faisait bien du
scénario 4 un plancher, mais elle faisait du scénario 2 un plafond.

**La garantie vieillesse du scénario 6 ne se chiffre pas sur des cas types.**
C'est une allocation différentielle : son coût est celui de la queue basse de la
distribution des pensions, et treize carrières ne décrivent pas une distribution.
Les 621 milliards de la ligne en italique sont un chiffre faux — cinq cas types
sur treize liquident à 65 ans ou après, et aucun aux générations anciennes. Le
barème appliqué à la distribution que publie
l'échantillon interrégimes de la DREES coûte **18,4 milliards par an** aux
pensions d'aujourd'hui, 32,2 si l'on sert à tous l'allocation d'isolement, et
**33 à 59 milliards par an** aux pensions du scénario 6 : la page Coût donne les
quatre chiffres et dit ce que chacun suppose.

Les poids de génération, eux, ne sont pas supposés non plus : ce sont les
effectifs de la **pyramide des âges de l'INSEE**, observés jusqu'en 2023. Reste
une limite énoncée sur la page : avant 1975 la reconstitution repose sur deux ou
trois générations. La dépense observée est certifiée ; ce qu'on en tire est
**estimé**, et ne peut pas être autre chose — aucune institution ne publie le
coût d'un système qui n'a pas existé.

### 5. Une réforme prospective ne fait rien économiser tout de suite, et beaucoup ensuite

Le passé ne se change pas ; l'avenir, si. La page **Coût** projette donc les six
systèmes jusqu'en **2070**, horizon des projections de population de l'INSEE — ni
plus, ni moins : c'est la source qui borne la page, pas une décision du dépôt.

La méthode ne change pas d'un mot. Le coût d'un système reste la dépense du
système actuel multipliée par le rapport des masses de pension ; ce qui change
est d'où vient cette dépense. Jusqu'en 2024 elle est **observée** ; au-delà, le
modèle la produit lui-même, **ancrée** sur cette dernière année publiée — les
deux expressions coïncident exactement à la jonction, si bien qu'aucune courbe
ne saute. Ce qui les fait bouger ensuite est ce qui doit les faire bouger : la
pyramide des âges, et les pensions que chaque génération acquiert.

| Système | Coût 2070 | Part du PIB 2070 | Cumul 2025-2070 | Écart |
|---|---|---|---|---|
| 1. Système actuel | 718 Md € | **19,4 %** | 25 864 Md € | réf. |
| 2. Notionnel rétroactif, part salariale | 223 Md € | 6,0 % | 7 640 Md € | −70,5 % |
| 3. Notionnel dès 2026, part salariale | 309 Md € | **8,3 %** | 18 128 Md € | −29,9 % |
| 4. Notionnel rétroactif, salariale + patronale | 497 Md € | 13,4 % | 18 135 Md € | −29,9 % |
| 5. Notionnel dès 2026, salariale + patronale | 512 Md € | 13,8 % | 21 642 Md € | −16,3 % |
| 6. Notionnel rétroactif, 18 % dès 2026, garantie vieillesse | 381 Md € | 10,3 % | 16 125 Md € | −37,7 % |

Trois choses à lire dans ce tableau.

**Le système actuel monte, et le contrôle externe s'est dégradé deux fois.** Il
passe de 13,6 % du PIB en 2024 à 19,4 % en 2070, alors que le nombre de
personnes de 65 ans ou plus rapporté aux 20-64 ans passe de 0,39 à 0,62. Le COR,
qui projette la même grandeur avec un modèle de population complet, trouve
**13,9 % en 2024 et 14,2 % en 2070** (rapport annuel de juin 2025). L'écart
d'arrivée était de deux points tant que les cas types pesaient d'un poids égal ;
il est passé à quatre quand ils ont porté les effectifs de leur caisse, puis à
cinq quand chacun s'est mis à liquider à l'âge de SA génération. Les deux fois,
ce n'est pas le calcul qui s'est dégradé : c'est **une compensation accidentelle
qui a disparu**. L'ancienne convention égalitaire donnait un sixième du poids à
des carrières qui liquident à 52 et 57 ans, ce qui masquait un défaut ancien —
le modèle faisait liquider chaque cas type à l'âge légal d'AUJOURD'HUI, quelle
que soit sa génération.

**Ce défaut-là est corrigé, et il n'était pas la cause.** Un cas type ne porte
plus un âge de départ mais une règle : la plupart partent au taux plein de leur
génération, ceux dont un statut commande le départ à l'âge que ce statut ouvre,
le militaire à une durée de services. La génération 1940 part désormais à 60 ans
et non à 64, et l'agent de conduite né en 2000 — embauché après la fermeture du
statut SNCF — part à 63 ans au régime général, par la porte de la carrière
longue. La trajectoire 2070 est montée de 18,3 à 19,3 % au lieu de revenir vers
14,2, puis à 19,5 quand la règle a appris la carrière longue et les trimestres
pour enfants, et redescend à 19,4 avec la suspension de la réforme de 2023
(LFSS 2026), qui fait partir plus tôt les générations 1964 à 1970 : le diagnostic que
[`docs/feuille_de_route.md`](docs/feuille_de_route.md) avait posé était juste sur
le défaut et faux sur son sens, et c'est la mesure qui le dit.
[`docs/limites.md`](docs/limites.md) §5 ter porte le chiffrage et la piste qui
reste — le taux de remplacement du modèle ne recule pas, celui du COR recule.

**Une réforme prospective met une génération à produire son effet.** Le scénario
3 ne fait rien économiser en 2026 — les droits acquis sont conservés —, et
10,9 points de PIB en 2070. Décider vite ne fait pas économiser vite ; cela fait
économiser longtemps.

**L'écart entre 3 et 5 mesure encore une seule chose** : ce que verse
l'employeur. Le scénario 5 économise cinq points et demi de PIB de moins que le
scénario 3, parce que son compte est alimenté par la cotisation entière.

Ce que la projection suppose est écrit sur la page et dans
[`docs/limites.md`](docs/limites.md) §5 ter : la démographie de l'INSEE
(scénario central, seize autres existent), un PIB qui suit les hypothèses du COR
**corrigées du recul de la population d'âge actif** — 10 % d'ici 2070 —, un taux
de couverture constant, et aucune règle de pilotage. Rien de tout cela n'est
certifié et ne peut l'être : une projection est une hypothèse, et la page
l'affiche parce qu'un ordre de grandeur documenté vaut mieux qu'un silence.

### 6. Un coût n'est pas un solde, et le coefficient d'équilibre le dit

Les cinq résultats qui précèdent disent ce qui SORT. Un système de répartition
se juge pourtant à son solde. La page Coût pose donc le second terme, et en tire
le **coefficient d'équilibre** de chaque système : le facteur par lequel il
faudrait multiplier toutes ses pensions pour que l'année tombe juste.

Les ressources ne viennent pas de la DREES, et ce n'est pas un choix : **les
Comptes de la protection sociale ne ventilent pas leurs ressources par risque.**
Une « recette du risque vieillesse » n'a pas de définition comptable, les
cotisations d'un régime polyvalent n'étant affectées à aucun risque. Ce qui
existe est le compte du *système de retraite*, que le COR consolide chaque année
depuis les rapports à la Commission des comptes de la Sécurité sociale. On lui
prend les **deux** colonnes, dépenses et ressources : un solde ne se fabrique pas
en soustrayant deux périmètres. Le sien — régimes légalement obligatoires, FSV
compris — vaut 13,86 % du PIB en 2024 contre 13,59 % pour la répartition
obligatoire de la DREES ; les deux se recoupent à 0,28 point, ce qui vaut
contrôle et non identité.

| Système | Solde 2025 | Solde moyen 2026-2070 | Coefficient 2070 |
|---|---|---|---|
| 1. Système actuel | −0,17 % du PIB | **−1,13 %** | **0,84** |
| 2. Notionnel rétroactif, part salariale | +8,78 % | +7,49 % | 2,27 |
| 3. Notionnel dès 2026, part salariale | −1,32 % | +1,01 % | **1,62** |
| 4. Notionnel rétroactif, salariale + patronale | +2,95 % | +1,00 % | 1,02 |
| 5. Notionnel dès 2026, salariale + patronale | −1,33 % | −0,93 % | 0,99 |
| 6. Notionnel rétroactif, 18 % dès 2026, garantie vieillesse | +2,95 % | **−0,88 %** | **1,00** |

**Le solde du système actuel est celui que le COR publie**, au dixième près :
5,1 milliards de besoin de financement en 2025. C'est la vérification que le
raccord entre deux périmètres ne triche pas — le rapport du scénario 1 vaut un
par construction, donc son solde doit être le solde publié, et il l'est.

**Un coefficient supérieur à un n'est pas une économie, c'est une marge.** Un
système notionnel réel *applique* son coefficient : il ne laisse pas dormir un
excédent, il relève les pensions jusqu'à l'équilibre. Lire les 1,87 du
scénario 3 en 2070 comme une économie de 46 % est donc un contresens : à
prélèvement inchangé, ce système servirait autant que le nôtre, mais **autrement
réparti entre les carrières** — ce qui est exactement ce que le reste de ce dépôt
mesure. Le modèle calcule ce facteur ; il ne l'applique jamais, et toutes les
courbes de coût des sections précédentes sont celles d'un système qui ne se
pilote pas.

**Un quart des ressources n'est pas cotisé, et cette part grandit.** 77 % des
ressources de 2025 sont des cotisations — en comptant la contribution
d'équilibre que l'État verse au régime de ses fonctionnaires, que le modèle
porte déjà au compte des scénarios 4 et 5 — contre 80 % en 2004 ; les impôts et
taxes affectés passent de 7 % à 15 %. Un compte notionnel ne sait créditer que
la part cotisée, et c'est ce qui borne la lecture de tout ce tableau.

**La recette suit le droit.** Le poste
« transferts d'organismes extérieurs » est ventilé par celui qui paie, lu dans
les rapports à la Commission des comptes de la Sécurité sociale : la branche
famille verse 10,9 milliards en 2024 pour l'assurance vieillesse des parents au
foyer et les majorations pour enfants, l'assurance chômage 3,9 milliards pour
les points de retraite complémentaire des chômeurs. Les scénarios notionnels
suppriment les premiers droits et ne portent rien au compte pendant une année
de chômage ; leur coefficient ne compte donc pas ces recettes : elles leur
sont retirées, année par année de 2013 à 2024, à part constante des ressources
avant et sur tout l'horizon projeté. C'est pourquoi les scénarios 3 et 5 sont
déjà en déficit en 2025, où ils servent encore les pensions du système actuel,
et pourquoi le scénario 3 vaut 1,62 en 2070 et non 1,94. Le système actuel,
lui, encaisse tout, et son solde reste celui du COR.

**La recette suit aussi le TAUX, et cela ne concerne que le scénario 6.** Il
remplace tous les taux de cotisation par un seul, 18 %, parts salariale et
patronale additionnées. Sur les carrières de la grille, le droit en vigueur en
prélève **28,7 %** en moyenne : 27,9 % pour un salarié non cadre du privé sous
le plafond, chiffre que le COR publie dans son rapport annuel et que le modèle
retrouve à huit dixièmes de point, et bien davantage pour un fonctionnaire,
dont l'employeur verse 74,28 % du traitement. La part cotisée des ressources,
77 % du total, est donc multipliée par **0,63** à compter de la bascule. Cela
change le sens du tableau pour ce scénario : son excédent moyen passe de
+2,11 % du PIB à −0,88 %, et son coefficient de 2070 de 1,29 à 1,00. Il est le
seul des trois systèmes rétroactifs à ne pas afficher de marge, et il reste
au-dessus du système actuel, qui est à −1,13 % — d'un quart de point, non plus
d'un point et quart. Les quatre autres scénarios notionnels ne changent que ce qui
est PORTÉ AU COMPTE, non ce qui est PRÉLEVÉ : l'employeur verse sa part dans
tous les cas, et leur recette ne bouge pas.

**Dix-huit pour cent de quoi ?** De l'assiette des revenus d'activité :
salaires et traitements bruts plus revenu mixte des non-salariés, **1 249 Md€
en 2024**, soit 42,6 % du PIB. Elle est certifiée chez l'INSEE
(`assiette_activite.csv`) et recoupée par une seconde route qui ne doit rien à
l'INSEE — l'inversion du tableau 2.11 du rapport du COR, à 3,9 % près. Le
système de retraite y prélève aujourd'hui 32,8 % de ressources en tout ; la
proposition en prélèverait 18. Le modèle sait aussi calculer la lecture
inverse, où les 18 % subissent la même déperdition que les taux légaux
d'aujourd'hui — allègements généraux, assiettes réduites : le scénario 6 y
serait déficitaire de 1,72 % du PIB. Cette lecture suppose que la proposition
garde la même architecture d'exonérations, ce que son texte ne dit pas ;
`docs/limites.md` §5 dit ce qui sépare les deux.

**Et la recette suit le droit jusqu'au bout.** Le fonds de solidarité
vieillesse finance par la CSG deux choses que les scénarios notionnels ne
servent pas : des trimestres pour des périodes non travaillées (15,2 Md€ en
2024) et le minimum vieillesse (4,3 Md€). Il échappait à la règle parce que sa
recette n'arrive pas par un transfert mais par l'impôt. Il y est entré le
19 septembre 2026, et le retrait total passe d'un demi-point de PIB à **1,17 %**
— ce qui coûte 0,64 point de solde moyen à chacun des cinq scénarios
notionnels.

**Et les pensions LIQUIDÉES suivent la règle d'indexation, comme le compte qui
les a produites.** Un système notionnel a deux règles d'indexation — celle du
compte pendant la carrière, celle de la pension une fois servie — et le modèle
n'en portait qu'une : ses masses figeaient la pension en euros constants pour
toute la retraite, soit une indexation sur les PRIX qui ne disait pas son nom.
C'est la loi pour le scénario 1 et pour la garantie vieillesse, qui suivent
l'article L. 161-25 ; ce n'est pas la proposition, où la pension suit la masse
salariale, 0,7 point par an au-dessus des prix. Les cinq scénarios notionnels
payaient donc moins que leur propre contrat, d'un dixième environ sur une
retraite. Corrigé le 19 septembre 2026 : **un point de PIB de solde moyen pour
le scénario 6**, qui passe de +0,12 % à −0,88 %, et l'équilibre du scénario 5
avec.

---

## Les données

Vingt-huit institutions sont recensées dans [`data/sources.yaml`](data/sources.yaml) :
INSEE, COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de
l'État, Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France, Institut des politiques
publiques, et les sites des institutions dont le régime n'est dans aucun texte
de l'index.

**Chaque valeur porte son niveau de fiabilité** — `certifiee`, `haute`,
`moyenne`, `estimee` — et la fiabilité d'un résultat est celle de son maillon le
plus faible. `Parametres.fiabilite_minimale` fait échouer la simulation plutôt
que de produire un chiffre trompeur.

Une valeur n'est `certifiee` que si elle a été **confrontée à la source
elle-même**, téléchargée depuis le producteur. Une transcription tierce, même
sourcée et reprise automatiquement, plafonne à `haute`.

Quand deux institutions publient le même chiffre, quatre critères disent
laquelle aller chercher : le **producteur** prime sur le repreneur, l'**observé**
sur le projeté, le **montant servi** sur le montant calculé, le **recontrôlable**
sur le saisi. Ils sont écrits en tête de
[`data/sources.yaml`](data/sources.yaml) et détaillés dans
[`docs/methodologie.md`](docs/methodologie.md). Ce n'est pas un classement
d'institutions mais de natures de données : l'INSEE pour ce qu'il **mesure**, le
COR pour ce qu'il **décide**.

| Donnée | Période certifiée | Producteur |
|---|---|---|
| Inflation, salaire moyen, masse salariale, productivité | 1950-2025 | INSEE, Banque de données macroéconomiques |
| Espérance de vie à 0 et 60 ans | 1946-2025 | INSEE |
| Espérance de vie à 65 ans | 1960-2024 | OCDE (l'INSEE ne la publie pas) |
| Espérances de vie projetées | 2026-2125 | INSEE, projections de population 2026 (dérivées de ses quotients par âge) |
| Quotients de mortalité par âge | 1986-2024 | Eurostat |
| Quotients de mortalité par âge | 1899-1985, et 95-104 ans jusqu'en 1997 | INED, tables de Vallin et Meslé |
| Plafond de la Sécurité sociale | 2002-2025 | INSEE |
| Valeurs du point de l'Ircantec | 1971-2021 | Caisse des dépôts, qui gère le régime |
| Valeurs du point des avocats | 2017-2026 | CNBF, ses barèmes annuels |
| Valeur du point des professions libérales | 2021-2025 | CNAVPL, ses recueils statistiques |
| Taux des deux tranches du régime de base des libéraux | 2020-2026 | CNAVPL, le tableau des cotisations de ses recueils |
| Valeur du point de la complémentaire agricole | 2005-2024 | code rural D. 732-166, base LEGI de la DILA |
| Minimum contributif et plafond d'écrêtement | ancres 2007-2014 | code de la sécurité sociale, base LEGI de la DILA |
| Âge d'ouverture et coefficient de minoration, par génération | 1900-1975 | code de la sécurité sociale `D. 161-2-1-9` et `R. 351-27`, base LEGI |
| Durée d'assurance requise, par génération | 1958-1975 | code de la sécurité sociale `L. 161-17-3`, base LEGI |
| Bornes du départ pour carrière longue | depuis 2023 | code de la sécurité sociale `L. 351-1-1` et `D. 351-1-1`, base LEGI |
| Valeurs du point de l'Agirc | 1947-2018 | Agirc-Arrco, sa compilation des valeurs de point |
| Valeurs du point du RAFP | 2005-2026 | ERAFP, dont le conseil d'administration les fixe |
| Point d'indice de la fonction publique | 1996-2027 | décret n° 85-1148, article 3, base LEGI |
| SMIC horaire | 1997-2017, sauf 2002 | décrets de relèvement du SMIC, base LEGI |
| Valeurs du point de l'Arrco, et de l'UNIRS qui en tient lieu avant 1999 | 1999-2018 et 1961-1998 | Agirc-Arrco, la même compilation |
| Durée maximale prise en compte par la proratisation, par génération | avant 1944 à 1947 | code de la sécurité sociale `R. 351-6`, base LEGI |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | code de la sécurité sociale `R. 351-29-1`, base LEGI |
| Durée d'assurance requise, générations 1953-1957 | 1953-1957 | décrets d'application des lois de 2003 et de 2010, base LEGI |
| Contribution employeur de la CNRACL | 1993-2028 | décret n° 91-613, article 5 II, base LEGI |
| Contribution employeur de la CNRACL | 1984-1988 | décret n° 47-1846 du 19 septembre 1947, article 3, base LEGI |
| Montant du minimum vieillesse (ASPA) | ancres 2006-2020 | code de la sécurité sociale `D. 815-1`, base LEGI |
| Durée d'assurance requise, générations 1934-1942 | 1934-1942 | code de la sécurité sociale `R. 351-45` II, base LEGI |
| Minimum garanti, traitement de référence | 2004 et année courante | Service des retraites de l'État |
| Décote de la fonction publique, coefficient et âge d'annulation | 2006-2019 | loi n° 2003-775, article 66 III, base LEGI |
| Barème du minimum garanti, montée en charge | 2004-2013 | loi n° 2003-775, article 66 V, base LEGI |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | code de la sécurité sociale `R. 351-9`, base LEGI |
| Plafond de la Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | décrets portant fixation du plafond, base **JORF** |
| Contribution employeur de la SNCF (T1 + T2) | 2007-2011 | arrêtés annuels du taux T1 (**JORF**) et décret n° 2007-1056, article 2 IV (LEGI) |

Ce qu'**OpenFisca-France** garde, ce sont les périodes que le *Journal officiel*
lui-même ne rend pas : le plafond de la Sécurité sociale des années dont la
notice ancienne ne porte pas le montant de janvier, le point d'indice d'avant
1996, le SMIC d'avant 1997 et d'après 2017, le barème du minimum garanti. Ce
sont des transcriptions, pas des sources primaires : elles plafonnent au niveau
`haute`.

**Le reste est désormais lu dans le décret qui le fixe.** Le SMIC et le point
d'indice ne sont pas des articles de code — le premier est relevé par un décret
annuel, le second par l'article 3 du décret du 24 octobre 1985 —, mais la base
LEGI garde les uns et les autres, datés. Là où la chaîne des textes est
complète, la valeur passe à `certifiee` ; là où le dump en saute un, l'année
reste à la transcription plutôt que d'être devinée. C'est le cas de 2002 pour le
SMIC, dont l'arrondi en euros — 6,67 € et non 6,6651 € — vient d'un texte de
conversion absent de la base, et des années d'avant 1996 pour le point d'indice,
dont deux relèvements manquent.

**Le plafond de la Sécurité sociale a suivi le même chemin, et par l'autre
porte.** Il n'est pas dans LEGI, qui ne garde que les codes : il est dans le
*Journal officiel* lui-même, dont la DILA ouvre un second dump. La chaîne des
décrets y est complète depuis 1963, et **trente et une années d'avant 2002** en
sont lues, qui confirment la transcription à l'euro près. Ce qui reste dehors
tient à la rédaction et non à l'accès : avant 1963 le décret ne nomme pas
l'année qu'il commande, et sept années plus récentes ou bien n'ont pas de
notice, ou bien n'annoncent qu'un taux, ou bien laissent leur tableau en image.
`docs/limites.md` les dit une à une.

**Les valeurs du point de l'Agirc et de l'Arrco en venaient aussi, et elles
viennent désormais de la caisse qui les a décidées.** Elles pèsent, dans la
pension d'un salarié du privé, plus lourd que tous les autres barèmes réunis, et
la fédération publie chaque automne l'historique complet des siens — le régime
unifié depuis 2019, l'Agirc depuis 1947, l'Arrco depuis 1999, et les caisses
qu'elle a fédérées, dont l'UNIRS dont le barème tient lieu de point Arrco avant
l'unification. Ces 260 valeurs sont donc lues chez le producteur, et le
recontrôle a confirmé la transcription à cinq centièmes de millime près — l'écart
tenant à ce qu'elle arrondissait la conversion en euros quand le document donne
le franc exact. Elles restent en outre recoupées à la série que l'INSEE publie
depuis 2001 : sur les 42 années communes, les deux ne divergent pas une fois.

```bash
python scripts/fetch/insee_bdm.py               # séries longues INSEE (BDM)
python scripts/fetch/oecd_esperance_vie.py      # espérance de vie à 65 ans
python scripts/fetch/eurostat_mortalite.py      # tables de mortalité par âge
python scripts/fetch/openfisca_plafond.py       # plafond ancien
python scripts/fetch/openfisca_cotisations.py   # taux de cotisation du RG, du public, des non-salariés
python scripts/fetch/openfisca_points.py        # valeurs du point, depuis 1947
python scripts/fetch/openfisca_point_indice.py  # point d'indice, minimum garanti
python scripts/fetch/dila_legi_point_indice.py  # point d'indice, dans son décret (index LEGI)
python scripts/fetch/dila_legi_smic.py          # SMIC, dans ses décrets (index LEGI)
python scripts/fetch/dila_legi_duree_requise.py # durée requise 1953-1957 (index LEGI)
python scripts/fetch/dila_legi_cnracl.py        # contribution employeur CNRACL (index LEGI)
python scripts/fetch/dila_legi_decote_fonction_publique.py  # décote FP (index LEGI)
python scripts/fetch/dila_legi_minimum_garanti.py  # barème du minimum garanti, dans l'index LEGI
python scripts/fetch/erafp_valeurs_point.py     # valeurs du point du RAFP, par l'ERAFP
python scripts/fetch/jorf_plafond_securite_sociale.py  # plafond ancien, dans ses décrets (index JORF)
python scripts/fetch/sncf_contribution_employeur.py  # contribution SNCF, dans les deux index
python scripts/fetch/dila_legi_minimum_vieillesse.py  # montant de l'ASPA, dans le code (index LEGI)
python scripts/fetch/sre_minimum_garanti.py     # référence du minimum garanti, par le service qui la sert
python scripts/fetch/cdc_ircantec.py            # barèmes Ircantec, par son gestionnaire
python scripts/fetch/cnbf_baremes.py            # valeurs du point des avocats
python scripts/fetch/cnavpl_recueils.py         # valeur du point des libéraux
python scripts/fetch/dila_legi_msa.py           # point agricole (index LEGI)
python scripts/fetch/dila_legi_minimum_contributif.py   # minimum contributif (index LEGI)
python scripts/fetch/dila_legi_parametres_retraite.py   # âges, durées, décotes, carrière longue (index LEGI)
python scripts/fetch/ined_vallin_mesle.py       # quotients de mortalité d'avant 1986
python scripts/fetch/eurostat_hicp.py           # contrôle croisé de l'inflation
python scripts/veille_droit.py                  # d'abord : ce qui a vieilli dans le registre du droit (veille.yaml)
python scripts/fetch/openfisca_regime_general.py  # contre-expertise du scénario 1 : régime général
python scripts/fetch/openfisca_fonction_publique.py  # la même, pension civile (État, CNRACL)
python scripts/fetch/openfisca_arrco.py         # la même, Arrco 1999-2018
python scripts/fetch/openfisca_agirc.py        # la même, Agirc des cadres
python scripts/fetch/openfisca_ircantec.py     # la même, Ircantec des non-titulaires
python scripts/fetch/openfisca_minimum_contributif.py  # montants du minimum contributif
python scripts/fetch/openfisca_parametres_generation.py  # durée requise, âge d'annulation, par génération
python scripts/fetch/cnav_revalorisation_salaires.py  # revalorisation des salaires portés au compte
python scripts/fetch/agirc_arrco_valeurs_point.py  # valeurs du point, par la fédération

python scripts/fetch/dila_index.py jorf --recuperer   # l'index plein texte du JO, publié (1 min)
python scripts/fetch/dila_index.py legi --recuperer   # le même pour LEGI
python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale") FRS' --jusqu 1981

python scripts/verifier_donnees.py              # confronte, sans rien écrire
python scripts/verifier_donnees.py --appliquer  # aligne sur la source et certifie
```

> **Chercher dans le Journal officiel sans le retélécharger.** Les scripts
> `dila_legi_*` et `jorf_*` lisaient le dump global de la DILA en flux — 1,1 à
> 1,7 Go, une demi-heure par passe, pour un dump qui n'a pas changé depuis
> juillet 2025 ; ils lisent l'index depuis le 17 septembre 2026, `--dump`
> gardant l'ancienne voie. `scripts/fetch/dila_index.py` construit une fois
> une base SQLite FTS5 du champ social du JORF et de LEGI (titres et textes,
> tenue à jour par les incréments quotidiens), publiée comme fichier de la
> release `index-dila` du dépôt par le workflow GitHub Actions `index-dila.yml`
> (chaque lundi, ou à la demande) d'où `--recuperer` la rapatrie en une minute ;
> `dila_cherche.py` y répond en quelques millisecondes, par des extraits et
> non des textes entiers. La certification, elle, continue de lire le dump :
> l'index n'en garde que ce qui touche au champ du dépôt.

> **Ce qui reste saisi à la main :** le salaire moyen et la productivité
> d'avant 1950, les taux de cotisation d'avant 1967 et ceux des régimes autres
> que le privé, les montants servis des trois minima — transcrits de leur
> publication, et préférés à toute projection parce qu'ils disent ce qui a été
> payé — et les barèmes que personne ne publie en série. L'âge d'annulation de
> la décote, lui, n'est pas saisi mais CALCULÉ : l'article `L. 351-8` le définit
> comme l'âge d'ouverture majoré de cinq ans, et le vérificateur le recalcule à
> chaque exécution depuis la table certifiée.
> Les autres tables par génération, elles, ne sont plus saisies : elles sont
> lues dans le texte des articles du code, dans la base LEGI de la DILA.
> `docs/limites.md` dit, pour chaque limite restante, dans quel sens elle joue
> et de combien, et recense les sources essayées sans succès, pour éviter de les
> rechercher deux fois.
> Lire [`docs/limites.md`](docs/limites.md) avant de citer un chiffre.

---

## Organisation

```
data/
  sources.yaml                  manifeste des sources institutionnelles
  reference/
    macro/                      inflation, salaire moyen, productivité, plafond, PIB,
                                dépenses de retraite observées, ressources et solde
                                du système de retraite, pyramide des âges,
                                projections
    mortalite/                  espérances de vie et quotients par âge observés
    regimes/                    72 fiches de régime + schéma + valeurs du point,
                                et l'inventaire de tous les régimes (inventaire.yaml)
    legislation/                âges et durées par génération, barèmes des
                                minima, décote de la fonction publique,
                                catégorie active et pension militaire,
                                carrière longue, contribution employeur des
                                régimes publics, profils d'affiliation,
                                prélèvements sur salaire hors retraite
  brut/                         téléchargements bruts, non versionnés
  derive/                       calibrations et journal de certification

src/retraite_notionnelle/
  config.py                     toutes les décisions de modélisation, en un seul endroit
  carriere.py                   description d'une carrière, trois niveaux de précision
  donnees/                      chargement, fiabilité, macro, mortalité, régimes,
                                courbe des taux sans risque et frais d'épargne retraite
  moteur/                       indexation, âge de référence, conversion, fusion, compte,
                                pilier de capitalisation obligatoire
  scenarios/                    système actuel, comptes notionnels
  simulateur.py                 façade et restitution
  remuneration.py               la fiche de paie d'un actif : coût du travail,
                                revenu brut, revenu net, en quatre profils —
                                la seule grandeur du dépôt qui ne soit pas
                                une pension
  castypes.py                   cas général
  cout.py                       ce que chaque système a coûté, coûterait,
                                et le solde qu'il laisserait
  web/
    pages.py                    contenu des pages — sans autre dépendance que le moteur
    gabarit.py                  rendu HTML et feuille de style

index.html                      le site : charge les données, puis le moteur JavaScript
.nojekyll                       servir les fichiers sans transformation
moteur/                         ce que le navigateur charge, et rien d'autre
  donnees.json                  séries, tables, régimes et inventaire (2874 Ko, produit par script)
  style.css                     extraite de gabarit.py (produite par script)
  js/                           portage du modèle, sans bibliothèque ni étape de build

docs/
  methodologie.md               ce que le modèle calcule, et pourquoi ainsi
  limites.md                    ce qu'il ne calcule pas, et ce qui reste à certifier
  veille_droit.md               comment le scénario 1 reste le droit applicable : le registre, le script, la règle

tests/                          1077 tests Python
  temoins/                      chiffres et pages figés depuis le modèle Python,
                                et les relevés d'OpenFisca-France-Pension qui
                                servent de contre-expertise au scénario 1
  js/                           le portage rejoué contre ces témoins (node --test)
```

---

## Principales options

Ce sont les champs de `Parametres`. Le formulaire du site les expose sous
« Options de modélisation », et l'adresse de la page les porte tous : une
simulation se cite telle quelle.

```python
mode_indexation        ModeIndexation.{TRIPLE_LOCK_INVERSE
                       | TRIPLE_LOCK_INVERSE_NOMINAL | MEDIANE_TROIS_TAUX
                       | MOYENNE_TROIS_TAUX | REVALORISATION_PORTEE_AU_COMPTE
                       | PRIX | SALAIRES | MASSE_SALARIALE | PIB_NOMINAL}
                       défaut : MASSE_SALARIALE
lissage_indexation     moyenne glissante appliquée à la règle choisie (défaut 1,
                       aucun lissage). PIB_NOMINAL lissé sur 5 ans est la règle
                       italienne
mode_age_reference     ModeAgeReference.{CLIQUET_LEGAL
                       | CLIQUET_PUIS_ESPERANCE_VIE | LEGAL_SANS_CLIQUET}
age_conversion_droits_acquis  AgeConversionDroitsAcquis.{REFERENCE | LIQUIDATION}
part_cotisation        PartCotisation.{SALARIALE | TOTALE | TOTALE_ALIGNEE}
table_conversion       TableConversion.{UNISEXE | PAR_SEXE}
scenario_projection    cor_reference | cor_productivite_basse
                       | cor_productivite_haute   (défaut : cor_reference,
                       scénario de référence du COR, productivité 0,7 %)
annee_bascule          année de passage au régime unique (défaut 2026)
annee_euros_constants  année des euros constants (défaut 2026)
fiabilite_minimale     refuse de calculer sous un certain niveau de fiabilité
```

`Comparaison.dictionnaire()` donne le résultat en structure de données plutôt
qu'en tableau — c'est ce que la page publie sous « Les résultats complets en
JSON ».

---

## Tests

```bash
python -m pytest tests
```

<!--chiffre:tests()-->1077<!--/--> tests couvrent le chargement et la fiabilité des données, la
règle de certification, la calibration des tables de mortalité et sa concordance
avec les tables observées, les propriétés du moteur (monotonie du diviseur,
cliquet de l'âge de référence, règles de fusion), le comportement des scénarios,
le rendu des pages et la fraîcheur de ce que charge le site. Ce compte-là est
recalculé à chaque contrôle de la prose — un nombre que rien ne recoupe finit
toujours par mentir. Aucun test n'accède au réseau : les sources sont simulées.

Une vingtaine d'entre eux tiennent l'accessibilité : contrastes mesurés dans les
deux thèmes, titres et en-têtes de ligne des tableaux, étiquettes et groupes du
formulaire, zones défilantes atteignables au clavier, absence d'information
enfermée dans une infobulle, et focus reposé après chaque rendu. Le site ne
déclare plus son accessibilité — cette déclaration appartient à l'éditeur du
site d'accueil —, mais il continue de la mesurer à chaque modification : une
promesse écrite se périme, ces contrôles-là non.

Deux d'entre eux lancent `node` pour rejouer le calcul côté JavaScript — les
cas-témoins figés, puis des carrières tirées au hasard ; ils sont ignorés si
`node` est absent. On peut exécuter les premiers seuls :

```bash
node --test tests/js/moteur.test.js
```

---

## Licence

Le code est sous licence Apache 2.0 ; les infographies, graphiques, tableaux
et textes que le site affiche sont sous [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr)
(reprise et adaptation libres, à condition de citer le site et de republier
toute version modifiée sous la même licence) ; le nom et le logo du Parti
Libéral Français ne sont couverts par aucune des deux — voir [LICENSE](LICENSE).
Les données publiques référencées restent
soumises aux licences de leurs producteurs respectifs (licence ouverte Etalab
pour la plupart), qui imposent toutes la citation de la source : elle est dans
[`data/sources.yaml`](data/sources.yaml), valeur par valeur.
