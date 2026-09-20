# Les avantages non contributifs du scénario 1

Le scénario 1 est le droit en vigueur. Un compte notionnel ne sert que ce qui a
été cotisé. **Tout ce qui sépare les deux est ici** : quarante-deux
dispositifs,
sous un code, avec leur base légale, les régimes qui les servent, l'état du
modèle à leur égard et le moyen d'en chiffrer le coût.

L'inventaire est une donnée, pas une prose : il vit dans
`data/reference/legislation/avantages_non_contributifs.yaml`, et
`tests/test_avantages.py` interdit qu'il redevienne partiel. Ce document dit ce
qu'il contient, comment on le chiffre, ce que le chiffrage a donné, et pourquoi
ce résultat n'est pas celui qu'on croit.

## 1. Pourquoi cette liste n'existait pas

Le dépôt en portait trois, et aucune ne contenait les deux autres.

| | Où | Combien | Ce qu'elle sait dire |
|---|---|---|---|
| 1 | `Neutralisations` (`config.py`) | 15 champs booléens | Rien : aucun moteur ne les lit, le docstring le dit. |
| 2 | `avantages_non_contributifs` des fiches de régime | 16 codes, datés, par régime | Ce que chaque régime sert, à quelle date. Six des seize ne commandent aucun calcul. |
| 3 | La cascade `AvantageApplique` (`scenarios/actuel.py`) | 7 codes | **Combien**, en euros, pour une carrière donnée. |

Les trois divergent, et pas par négligence : elles répondent à trois questions
différentes. La première déclare une intention de réforme, la deuxième décrit un
régime, la troisième calcule un montant. Le défaut est qu'aucune ne dit **ce
qu'un dispositif coûte au système**, ni même lesquels manquent — et il en
manquait beaucoup. La réversion, qui est la première dépense non contributive du
système français, est déclarée dans 756 périodes de fiches et servie par aucun
code.

`avantages_non_contributifs.yaml` est leur union, complétée de ce qu'aucune ne
portait, avec pour chaque ligne le moyen de la chiffrer. Un test exige que tout
code employé par l'une des trois ait sa ligne, sous son code ou sous un alias.

## 2. L'état du modèle : quatre mots, et ils ne se valent pas

| État | Combien | Ce que ça veut dire |
|---|---|---|
| **chiffré** | 8 | Le scénario 1 le sert, et la cascade en isole le montant en euros. La somme des lignes chiffrées vaut *exactement* `pension_annuelle − total_contributif` : c'est vérifié à chaque simulation. |
| **intégré** | 11 | Le scénario 1 le sert, mais l'effet passe par un trimestre, un âge ou une assiette. Il ne s'isole qu'en recalculant la pension une seconde fois, avantage retiré. **Huit le sont désormais**, par retrait : voir les §4 bis et 4 ter. Les trois derniers ne sont pas des dispositifs. |
| **déclaré** | 3 | Une fiche de régime le déclare, aucun code ne le sert. La déclaration est une intention — mais la réversion, qui est de ceux-là, a désormais son coût, LU dans les séries de la DREES : voir le §4 quater. |
| **absent** | 20 | Ni déclaré ni servi. C'est un écart au droit positif — que les comptes de la protection sociale comblent pour dix d'entre eux, qu'ils publient poste par poste : voir les §4 quinquies et 4 sexies. |

Et trois façons d'en mesurer le coût : par le **modèle** (la cascade, ou un
recalcul de même nature), par une **série publiée**, ou par **rien** — ce
dernier cas étant une limite qu'il vaut mieux écrire qu'estimer. Quand les deux
premières existent, **la série publiée l'emporte** : c'est le premier critère
de `data/sources.yaml`, et c'est ce qui fait aujourd'hui 87 % du total chiffré.

## 3. La liste

Base légale telle qu'elle a été lue dans l'index LEGI du dépôt, sauf les deux
lignes marquées « à certifier », où la référence est donnée pour la recherche et
non comme une source. Une déduction n'est pas une lecture.

| Dispositif | Base légale | Modèle | Coût mesurable par |
|---|---|---|---|

| **Droits familiaux** | | | |
| Majoration de durée d'assurance pour enfants (MDA) | L. 351-4 CSS; L. 351-5 CSS | chiffré | modèle |
| Bonification pour enfants de la fonction publique | L. 12 b et b bis CPCMR; L. 12 bis CPCMR | chiffré | modèle |
| Majoration de pension pour trois enfants et plus | L. 351-12 CSS; L. 18 CPCMR; accord national interprofessionnel Agirc-Arrco | chiffré | modèle |
| Assurance vieillesse des parents au foyer | L. 381-1 CSS | chiffré | modèle |
| Surcote parentale | L. 351-1-2-1 CSS | chiffré | modèle |
| Salaire annuel moyen calculé sur moins d'années pour les parents | R. 173-3-2 I CSS (décret n° 2026-699 du 29 juillet 2026; article 1er) | intégré | modèle |
| Majoration de durée d'assurance pour congé parental d'éducation | L. 351-5 CSS | absent | — |
| Majoration de durée d'assurance pour enfant handicapé | L. 351-4-1 CSS | absent | — |

| **Minima de pension** | | | |
| Minimum contributif, et sa majoration | L. 351-10 CSS; D. 351-2-1 CSS; L. 173-2 CSS | chiffré | modèle |
| Minimum garanti de la fonction publique | L. 17 CPCMR; loi n° 2003-775 article 66 V | chiffré | modèle |
| Minimum vieillesse (ASPA) | L. 815-1 CSS et suivants; L. 816-2 CSS; L. 161-25 CSS | chiffré | modèle |
| Garantie minimale de points de l'Agirc | accord Agirc du 9 février 1988 | intégré | modèle |
| Pension majorée de référence du régime agricole | L. 732-54-1 code rural | déclaré | — |

| **Périodes non cotisées mais validées** | | | |
| Périodes assimilées | L. 351-3 CSS; R. 351-12 CSS | intégré | modèle |
| Points de complémentaire acquis sans cotisation | accords nationaux interprofessionnels Agirc-Arrco; décret Ircantec | intégré | modèle |
| Validation du service national | L. 351-3 CSS | intégré | modèle |

| **Droits dérivés (survivants)** | | | |
| Pension de réversion | L. 353-1 CSS; L. 38 CPCMR | déclaré | série publiée |
| Majoration de la pension de réversion | L. 353-6 CSS | absent | série publiée |
| Majoration forfaitaire de réversion pour enfant à charge | L. 353-1 CSS | absent | série publiée |
| Allocation veuvage | L. 356-1 CSS | absent | série publiée |
| Pension d'orphelin | L. 40 CPCMR | absent | série publiée |

| **Âge de départ et bonifications de service** | | | |
| Départ anticipé des catégories actives et super-actives | L. 24 I 1° CPCMR; L. 14 bis CPCMR; décret n° 2026-344 du 7 mai 2026 article 3 D | intégré | modèle |
| Retraite anticipée pour carrière longue | L. 351-1-1 CSS; D. 351-1-1 CSS; L. 351-1-1 3° CSS | intégré | modèle |
| Jouissance immédiate de la pension militaire | L. 24 CPCMR; L. 25 CPCMR | intégré | modèle |
| Bonification du cinquième du temps de service des militaires | L. 12 i CPCMR | absent | — |
| Bonification du cinquième des policiers, pompiers et surveillants | statuts particuliers — à certifier; hors CPCMR | absent | — |
| Bonification de dépaysement | L. 12 a CPCMR | absent | — |
| Bénéfices de campagne | L. 12 c CPCMR | absent | — |
| Bonification pour service aérien ou sous-marin commandé | L. 12 d CPCMR | absent | — |
| Retraite anticipée des travailleurs handicapés | L. 351-1-3 CSS; D. 351-1-5 CSS; décret n° 2026-344 article 3 C et G | absent | — |
| Taux plein par inaptitude ou invalidité | L. 351-8 1° bis CSS | absent | — |
| Départ anticipé pour incapacité permanente et compte pénibilité | L. 351-1-4 CSS; L. 4163-1 code du travail | absent | — |
| Cessation anticipée d'activité des travailleurs de l'amiante | loi n° 98-1194 article 41 — à certifier | absent | série publiée |

| **Majorations diverses** | | | |
| Majoration pour assistance d'une tierce personne | L. 355-1 CSS; L. 30 CPCMR | absent | série publiée |
| Majoration pour conjoint à charge | L. 351-13 CSS | absent | série publiée |
| Coefficient de solidarité de l'Agirc-Arrco | accord national interprofessionnel Agirc-Arrco du 30 octobre 2015 | déclaré | — |

| **Écarts structurels au principe contributif** | | | |
| Décote et surcote qui ne sont pas actuarielles | R. 351-27 CSS; L. 14 CPCMR; L. 351-1-2 CSS; D. 351-1-4 CSS | intégré | modèle |
| Rendement servi supérieur à ce que l'assiette peut porter | — | intégré | modèle |
| Impôts, subventions d'équilibre et compensation démographique | — | intégré | série publiée |
Les trois dernières lignes ne sont pas des dispositifs, et aucune caisse ne les
liquide sous un nom. Ce sont les trois façons dont une pension excède la
cotisation sans qu'aucun droit gratuit ne soit en cause, et elles **ne
s'additionnent pas** aux six familles précédentes : elles portent sur la même
pension, vue sous un autre angle. Les compter ensemble serait un double compte.

## 4. Comment on chiffre, et ce que ça a donné

`scripts/cout_avantages.py` porte la décomposition de l'individu à la masse par
la méthode de `cout.py`, sans en changer une ligne :

    coût de l'avantage A en t = dépense OBSERVÉE en t × (masse A / masse totale)

La dépense observée vient de la DREES et n'est pas modélisée ; seule la **part**
l'est. Les poids sont ceux de `cout.py` et pas d'autres : l'effectif INSEE de
chaque classe d'âge pour la génération, les effectifs de caisse de la DREES pour
le cas type.

En milliards d'euros courants de chaque année :

| Année | Dépense | Périodes assimilées | MDA / bonif. | Min. contributif | Catég. active | AVPF | Min. vieillesse | **Total** | **Part** |
|---|---|---|---|---|---|---|---|---|---|
| 1980 | 44,3 | 0,2 | 0,2 | 0,0 | 0,0 | 0,0 | 4,3 | **4,6** | **10,4 %** |
| 1990 | 115,9 | 0,3 | 0,2 | 0,4 | 0,0 | 0,3 | 3,3 | **4,5** | **3,9 %** |
| 2000 | 178,1 | 0,6 | 0,2 | 1,1 | 0,0 | 0,3 | 1,4 | **3,7** | **2,1 %** |
| 2010 | 282,1 | 3,8 | 1,8 | 2,3 | 0,2 | 0,2 | 0,3 | **8,6** | **3,1 %** |
| 2024 | 426,7 | 6,8 | 3,1 | 2,1 | 0,6 | 0,0 | 0,0 | **12,6** | **3,0 %** |

**Ce chiffre ne porte que ce que le modèle CALCULE.** La réversion, qui se lit
au lieu de se calculer, s'y ajoute pour 38,3 milliards : le total chiffré est
donc de **50,9 milliards en 2024**, soit 11,9 % de la dépense. Le COR chiffre
les droits de solidarité à « de l'ordre d'un cinquième des retraites tous
régimes » (rapport du 27 janvier 2010, commandé par l'article 75 de la LFSS
2009), soit 85 milliards sur une dépense de 426,7. On en tient les trois
cinquièmes. Le §4 quater dit d'où vient le plus gros morceau, et le §5 ce qui
manque encore.

## 4 bis. Les deux avantages qui ne se lisaient pas dans la cascade

Les périodes assimilées et la catégorie active sont **servies** par le scénario 1
sans que la cascade les isole : leur effet passe par un trimestre ou par un âge,
non par un montant. Elles se mesurent par **recalcul** — on refait la pension
sans l'avantage, à date de liquidation inchangée, et l'écart est la ligne. C'est
le principe même de la cascade, dont les huit lignes sont déjà des écarts.

Le recalcul se fait à date de départ fixe, et c'est ce qui le rend comparable.
Mais **un avantage d'âge agit deux fois**, et la seconde est de loin la plus
lourde.

**Premier effet — sur le montant.** On refait la pension de l'agent classé avec
le statut sédentaire de mêmes régimes. Résultat : **0,6 Md€ en 2024**, et 868 €
par an pour un agent classé de la génération 1960. C'est petit, et ce n'est pas
une erreur : **la décote est plafonnée à vingt trimestres**, si bien que l'agent
classé parti à 57 ans et l'agent sédentaire parti le même jour butent tous deux
sur le même plafond. Une décote plafonnée ne sait pas dire qui part cinq ans trop
tôt.

**Second effet — sur la durée.** Ce que le classement coûte vraiment, ce sont les
**annuités servies avant l'âge légal**, qu'aucune décote ne rattrape.
`--duree` les compte, à l'âge légal de chaque génération et non à un âge fixe :

| Année | Dépense | Anticipée | Part | Carrière longue | Classement | Régimes spéciaux |
|---|---|---|---|---|---|---|
| 1980 | 44,3 | 3,8 | 8,7 % | 0,0 | 2,6 | 1,3 |
| 1990 | 115,9 | 5,6 | 4,8 % | 0,0 | 3,8 | 1,8 |
| 2000 | 178,1 | 6,6 | 3,7 % | 0,0 | 4,4 | 2,2 |
| 2010 | 282,1 | 9,7 | 3,4 % | 0,0 | 6,5 | 3,2 |
| 2024 | 426,7 | **13,7** | **3,2 %** | 3,8 | 7,5 | 2,4 |

**13,7 milliards en 2024, soit treize fois l'effet de montant.** Et la
composition change : jusqu'aux années 2010 les départs anticipés viennent
entièrement des statuts classés et des régimes spéciaux ; la **carrière longue**
n'apparaît qu'ensuite, et pèse 3,8 milliards en 2024 — mécaniquement, à mesure
que l'âge légal monte au-dessus de l'âge auquel une carrière commencée tôt
réunit sa durée.

> **Une erreur corrigée en construisant la page du site.** Cette table a d'abord
> annoncé 23,7 milliards en 2024, avec un pic qui triplait la bande des régimes
> spéciaux sur les deux dernières années. C'était un effet de bord : chaque
> génération de la grille représente cinq cohortes, et la comparaison opposait
> l'âge de départ de la génération à l'âge légal de chacune des cinq. Comme la
> réforme de 2023 relève cet âge d'un trimestre par génération, les cohortes les
> plus jeunes de chaque tranche devenaient « anticipées » sans que rien n'avance
> leur départ. L'âge légal est désormais lu une fois, pour la génération de la
> grille. Le pic a disparu et la série est continue.

> **Réserve, écrite aussi dans le script.** Ce sont des annuités *anticipées*,
> pas un surcoût *net* : partir tôt, c'est aussi cotiser moins et mourir plus
> tôt en moyenne. Le chiffre dit ce que le système verse avant l'âge légal, non
> ce qu'il économiserait à supprimer ces départs. C'est précisément l'arbitrage
> qu'un coefficient de conversion notionnel rend automatique et que le droit
> actuel ne rend nulle part.

**Un refus, qui est un résultat.** La jouissance immédiate de la pension
militaire n'est pas chiffrée sur le montant, et le script dit pourquoi : la
contrefactuelle naturelle — le même agent en fonctionnaire civil, qui relève des
mêmes régimes — déplace aussi la **durée requise**, 172 trimestres contre 160.
La proratisation change avec le statut, l'écart ne mesure plus l'âge, et il
ressort même négatif. Le garde-fou refuse la ligne, et la refuse **partout** dès
qu'elle est faussée quelque part : une ligne mesurée pour certaines générations
et pas pour d'autres donnerait un agrégat biaisé dont le biais serait invisible.

**Ce que l'avantage vaut à qui le touche.** Quand l'agrégat n'a pas de sens, la
valeur individuelle en a un. `--par-carriere` applique à chaque cas type une dose
commune de cinq années de chômage indemnisé — une **hypothèse**, affichée comme
telle — et mesure ce qu'elles valent :

| Cas type | Âge | Pension | Périodes assimilées | Part |
|---|---|---|---|---|
| SMIC, carrière complète | 60 | 11 919 € | 3 782 € | 32 % |
| Salaire moyen | 63 | 24 436 € | 7 154 € | 29 % |
| Cadre | 65 | 58 259 € | 12 389 € | 21 % |
| Fonctionnaire sédentaire | 64 | 37 513 € | 9 858 € | 26 % |
| Exploitant agricole | 62 | 9 140 € | 1 508 € | 17 % |

Cinq années sans travailler valent entre un sixième et un tiers de la pension.
C'est le chiffre qui dit ce que le dispositif fait ; celui de la table agrégée
dit seulement ce que la grille en sait.

Un dernier sous-produit, obtenu par un détour : le chômage **indemnisé** et le
chômage **non indemnisé** valident les mêmes quatre trimestres, et seul le premier
ouvre des points de complémentaire. L'écart entre les deux **est** la valeur de
ces points — 612 € par an sur la carrière au salaire moyen, contre 7 154 € pour
la validation entière. L'assurance chômage en verse la contrepartie, 3,8 Md€ en
2024 au poste `unedic_agirc_arrco`.

## 4 ter. Les neuf lignes « intégré » qui restaient

Onze avantages sont **servis par le scénario 1 sans que la cascade les isole** :
leur effet passe par un trimestre, un âge ou une assiette, et rien n'en sort
qu'on puisse lire. Deux avaient été mesurés (§ 4 bis). Voici les neuf autres.

### Retirer pour mesurer, par trois voies et pas une de plus

Un avantage qu'on ne lit pas, on le **retire**, et l'écart est la ligne. Le
retrait se fait de trois façons, et aucune ne touche au moteur — c'est la
condition pour que la mesure reste une mesure : si le calcul changeait, on
comparerait deux modèles et non deux droits.

| Voie | Ce qu'on retire | Pour quoi |
|---|---|---|
| **la carrière** | une année de chômage devient une année sans activité | périodes assimilées, points gratuits de complémentaire, service national |
| **le catalogue** | la fiche du régime cesse de déclarer l'avantage | catégorie active, jouissance militaire, garantie minimale de points |
| **une table** | le barème daté est vidé, ou sa date d'effet repoussée | carrière longue, salaire de référence des parents |

La voie du **catalogue** est la plus fidèle des trois : elle ne change que la
*déclaration*, là où le droit l'a lui-même écrite. Un test le vérifie par un
détour : la catégorie active est mesurée une seconde fois en changeant le
**statut** de l'agent pour le statut sédentaire de mêmes caisses, et les deux
chemins — l'un par les données du régime, l'autre par celles de la carrière —
donnent le même euro sur cinq générations.

### Ce que chacune vaut

Génération 1985, en euros par an de pension, à date de départ inchangée. Les
colonnes ne s'additionnent pas : la décote est plafonnée, et deux retraits qui
butent sur le même plafond ne font pas deux fois le premier.

| Ligne | Ce que le retrait fait | Valeur |
|---|---|---|
| Catégorie active | l'âge légal de droit commun est opposé à l'agent classé | **4 530 €** |
| Jouissance militaire | la pension ne s'ouvre plus à la durée de services | **4 420 €** |
| Périodes assimilées | les interruptions ne valident plus rien | **4 526 €** |
| Salaire de référence des parents | retour à vingt-cinq années | **729 €** |
| Garantie minimale de points | le plancher de 120 points est retiré | **205 €** |
| Carrière longue | le barème d'anticipation est vidé | **0 €** |

Et sous une **dose** de cinq années de chômage indemnisé et d'une année de
service national — une hypothèse, affichée comme telle, puisque la grille n'en
porte aucune :

| Ligne | Salaire moyen | Cadre |
|---|---|---|
| Périodes assimilées | 12 062 € | 18 350 € |
| Service national | 2 996 € | 5 693 € |
| Points gratuits de complémentaire | 1 427 € | 8 585 € |

### Trois résultats qu'on n'attendait pas

**La carrière longue ne vaut rien sur le montant.** Le barème vidé, la pension ne
bouge pas d'un euro : un assuré entré tôt réunit sa durée de toute façon, et le
taux plein lui est acquis avec ou sans le dispositif. Ce que la carrière longue
change n'est pas le montant mais la **date**. Elle ouvre la porte ; elle ne
remplit pas la pension. Tout son prix est dans la durée — 3,8 Md€ en 2024, rien
avant 2010.

**Quatre des neuf ne pèsent rien sur la fenêtre publiée**, et aucune de ces
absences n'est un défaut de mesure :

- le salaire de référence des parents ne s'applique qu'aux pensions prenant
  effet à compter de septembre 2026, et la dernière dépense publiée est de 2024 ;
- la garantie minimale de points ne mord que sur les premières années d'une
  carrière de cadre, et n'a existé que de 1989 à 2018 : les carrières concernées
  liquident toutes après 2024 ;
- le service national et les points gratuits de complémentaire ne sont portés
  par aucun cas type, dont un seul connaît une interruption.

**La jouissance militaire se mesure sur certaines générations et se refuse sur
les autres.** Le retrait y déplace aussi la durée requise — 172 trimestres
contre 160, la pension militaire ayant la sienne —, et la proratisation change
avec le droit. Le garde-fou compare les deux durées, refuse la ligne, et la
refuse **partout** dès qu'elle est faussée quelque part : une ligne mesurée pour
certaines générations et pas pour d'autres donnerait un agrégat dont le biais
serait invisible.

### Les trois qui ne sont pas des dispositifs

Elles se chiffrent, mais pas par un retrait — on ne retire pas un barème, on le
remplace ; on ne retire pas une recette, on la lit.

**La décote n'est pas actuarielle, et le résultat renverse l'intuition.** Sur un
fonctionnaire sédentaire de la génération 1965, âge de référence 64,5 ans, en
comparant ce que coûte l'anticipation sous le droit en vigueur et sous le
coefficient de conversion notionnel :

| Départ | Droit actuel | Notionnel | Écart |
|---|---|---|---|
| 62,5 ans | 81,7 % | 84,0 % | **−2,3 pts** (plus dur) |
| 59,5 ans | 59,1 % | 65,5 % | **−6,4 pts** (plus dur) |
| 56,5 ans | 48,0 % | 46,4 % | **+1,5 pt** (plus doux) |
| 54,5 ans | 44,6 % | 39,5 % | **+5,1 pts** |
| 52,5 ans | 40,3 % | 32,7 % | **+7,6 pts** |

La décote **surpunit l'anticipation ordinaire et sous-punit l'anticipation
extrême**, parce qu'elle est plafonnée à vingt trimestres. Or l'anticipation
extrême est exactement celle de la catégorie active (cinq ans), de la
super-active (dix), de la conduite SNCF (douze) et des militaires (vingt). Le
barème est le plus clément là où il devrait l'être le moins.

**Le rendement servi dépasse ce que l'assiette porte, et c'est de très loin le
plus gros de la liste.** La masse du scénario 2 vaut 27,9 % de celle du
scénario 1 en 2024 : l'écart est de 307,5 Md€ sur une dépense de 426,7. Le
scénario 2 ne porte au compte que la part **salariale** ; avec la part
patronale (scénario 4), l'écart tombe à **133,7 Md€**, soit 31,3 % de la
dépense. La seconde est la comparaison honnête avec « ce qui a été cotisé », la
première avec « ce que l'assuré a lui-même supporté ». Ne jamais l'additionner
aux lignes de dispositifs : celles-ci sont comprises dedans.

**Une part du financement n'est pas contributive.** En 2025, les cotisations ne
font que 65,6 % des ressources du système. Le reste : impôts et taxes affectés
15,3 %, contribution d'équilibre de l'État employeur 11,7 %, transferts 3,9 %,
subventions d'équilibre des régimes spéciaux 1,8 %, autres produits 1,7 %. Deux
réserves : les impôts compensent pour l'essentiel des exonérations de
cotisations, et les transferts sont déjà comptés du côté des prestations, sous
l'AVPF et la majoration pour enfants. Le noyau indiscutable est la contribution
d'équilibre et les subventions, **13,5 % des ressources**.

### Ce que tout cela déplace dans l'agrégat : rien

La décomposition annuelle vaut toujours **12,6 Md€ en 2024**, aux mêmes sept
lignes. (C'est la part CALCULÉE du total ; les lignes lues portent le reste, et
le §4 quinquies fait le compte.) Chiffrer les neuf n'a pas déplacé la masse d'un euro, et ce n'était pas
le but : le but était de savoir **pourquoi** chacune vaut ce qu'elle vaut. Sur
les neuf, quatre sont nulles pour des raisons de calendrier ou de composition de
la grille, une est nulle par nature, une est refusée, et trois relèvent d'une
autre grandeur. Une liste qui ne dit pas cela n'est pas une liste : c'est un
tableau de zéros.

## 4 quater. La réversion, lue et non calculée

C'était la deuxième priorité du §6, et de très loin la ligne la plus lourde de
l'inventaire. Elle est chiffrée : **38,3 Md€ en 2024**, soit **9,0 % de la
dépense de retraite**. À elle seule, elle pèse trois fois tout ce que le modèle
mesure par ailleurs, et fait passer le total chiffré de 12,6 à **50,9 Md€, soit
11,9 % de la dépense** contre 3,0 % auparavant. (Le §4 quinquies le porte
ensuite à 93,9 Md€, en lisant huit postes de plus, et le §4 sexies à
95,2 Md€ en en trouvant trois autres.)

| Année | Réversion | Part de la dépense | Total chiffré |
|---|---|---|---|
| 2004 | 25,4 Md€ | 13,5 % | 29,8 Md€ (14,0 %) |
| 2010 | 30,8 Md€ | 10,9 % | 39,4 Md€ (14,0 %) |
| 2020 | 33,9 Md€ | 9,4 % | 44,9 Md€ (12,5 %) |
| 2024 | 38,3 Md€ | 9,0 % | 50,9 Md€ (11,9 %) |

### Elle ne se calcule pas, et c'est structurel

Le modèle décrit une **carrière**, pas un ménage. Il n'a ni conjoint, ni date de
décès, ni ressources du survivant, et ne produira donc jamais une pension de
réversion. Les 756 périodes du catalogue qui déclarent `reversion` sont une
intention que nul code ne sert — c'est l'écart le plus ancien entre les
déclarations du dépôt et ce qu'il calcule, relevé au §1.

Aucune des trois voies de retrait du §4 ter n'y peut rien : on ne retire pas un
avantage qui n'a jamais été servi. La seule issue est de le **lire**.

### La masse est un produit, et chacun de ses termes vient d'une cellule

L'enquête annuelle de la DREES auprès des caisses de retraite (EACR) donne, pour
chaque couple (caisse, année) :

- le **nombre de bénéficiaires** d'un droit dérivé — champ `ddert`, qui compte
  tous ceux qui en touchent un, qu'ils aient ou non une pension de droit direct
  par ailleurs ;
- le **montant mensuel moyen de ce droit-là** — colonne `m2`.

Leur produit, sur douze mois, est la masse. `scripts/fetch/drees_eacr.py` les
lit dans la même feuille et sous la même règle de millésime que les effectifs
qu'il récupérait déjà ; `scripts/verifier_donnees.py` en écrit
`data/reference/macro/droits_derives.csv`, 305 valeurs certifiées de 2004 à
2024.

**Deux pièges, et ils coûtent cher.**

*La colonne.* Le classeur porte aussi `mont`, qui est la pension **totale** du
bénéficiaire, droit direct compris : 745,60 € à la Cnav en 2020 contre 326,70 €
pour la seule part dérivée. La prendre doublerait la masse. Le classeur se
contrôle d'ailleurs lui-même : la moyenne des `m2` du champ « dérivé seul » et
du champ « cumul des deux », pondérée par leurs effectifs, vaut exactement le
`m2` du champ « dérivé total ».

*La somme des caisses.* Un polypensionné touche une réversion à la Cnav **et** à
l'Agirc-Arrco : la somme des effectifs compte deux fois la même veuve, 8,5
millions de bénéficiaires au lieu de 4,4. Les **masses**, elles, s'additionnent
sans double compte, chaque caisse versant la sienne — et leur somme recoupe la
ligne « tous régimes » à 2 % près, ce qui est le contrôle interne de la série.

### Ce qu'elle change au statut de la page

C'est la ligne la plus sûre de tout l'inventaire, et par un renversement qui
mérite d'être dit : **elle est la seule qui ne repose pas sur les treize
carrières types**. Elle dénombre 4,4 millions de personnes réelles. Les huit
lignes mesurées par retrait sont, elles, aussi bonnes que la grille — c'est-à-dire
pas très bonnes, et le §5 dit pourquoi.

La page du site la porte **dans le même tracé que les autres** : une seule
carte réunit tout ce qu'on sait chiffrer, et c'est le total qui doit se lire
d'un coup d'œil. Le prix de cette réunion est la **fenêtre**, qui ne peut aller
plus loin en arrière que la plus jeune des lignes lues : 2004 quand la réversion
était la seule, cinq points seulement depuis que les postes des comptes l'ont
rejointe (§4 quinquies). Le graphique la calcule au lieu de l'écrire, et elle
se resserre donc d'elle-même à chaque ligne lue qui arrive.

Ce prix est plus faible qu'il n'y paraît : les **poids** des carrières types
viennent eux aussi d'une série que la DREES ne publie que de 2004 à 2024 —
avant, la répartition du bord est reconduite et la série tombe au niveau
« estimée ». La fenêtre est donc celle où chaque terme du produit est observé.
Ce que les années antérieures montraient — un minimum vieillesse qui pesait le
tiers de la dépense en 1960 et qui s'est éteint — reste calculé par la commande
d'analyse du dépôt, qui remonte à 1959.

### Ce qui reste hors de portée

La réversion n'est pas tout le droit dérivé. Au moment où ce paragraphe a été
écrit, l'**allocation veuvage**, la **majoration de réversion** et les
**pensions d'orphelin** restaient absentes de l'inventaire chiffré. Les deux
dernières ne le sont plus : les comptes de la protection sociale les publient
poste par poste, 1,22 et 6,45 Md€ en 2024 (§4 quinquies). L'allocation veuvage,
elle, reste rangée dans un poste « autres droits dérivés » qui ne l'isole pas.

## 4 quinquies. Les postes que les comptes publient, et qui remplacent le modèle

Le §5 concluait que la grille de cas types n'est pas une population, et le §6
en tirait une priorité : trouver la distribution des retraités par nombre
d'enfants. **Ce n'était pas la seule issue, et c'était la plus longue.** Les
Comptes de la protection sociale de la DREES publient, depuis 2020, les
sous-postes du risque vieillesse-survie un par un. Huit d'entre eux sont
exactement des lignes de l'inventaire, et ils comptent des personnes réelles.

`data/sources.yaml` tranche le cas dans son premier critère : **le producteur
prime sur le repreneur**. Là où un poste publié existe, il **remplace** la
ligne calculée au lieu de la compléter. L'écart entre les deux dit ce que la
grille coûtait :

| Ligne | Modèle, 2024 | Poste publié, 2024 |
|---|---|---|
| Majoration de pension pour trois enfants et plus | 0,00 Md€ | **7,78 Md€** |
| Minimum vieillesse (ASPA) | ~0,02 Md€ | **4,94 Md€** |
| Taux plein par inaptitude ou invalidité | absent | **22,20 Md€** |
| Pension d'orphelin | absent | **6,45 Md€** |
| Majoration de la pension de réversion | absent | **1,22 Md€** |
| Majoration pour assistance d'une tierce personne | absent | **0,31 Md€** |
| Majoration pour conjoint à charge | absent | **0,07 Md€** |

La majoration pour enfants est le cas d'école : un seul des treize cas types a
des enfants, et il en a deux quand le seuil est à trois. Le modèle chiffrait
donc à zéro, toutes les années de la série, un avantage qui pèse près de huit
milliards. Ce n'était pas une erreur de calcul mais une erreur de **question** :
on demandait à un instrument de rapport de compter une population.

### Ce que cela donne au total

| | 2020 | 2024 |
|---|---|---|
| Dépense observée | 359,5 Md€ | 426,7 Md€ |
| Lignes **lues** (comptes, EACR) | 68,5 Md€ | **81,3 Md€** |
| Lignes **calculées** (retrait sur la grille) | 13,5 Md€ | **12,6 Md€** |
| Total chiffré | 82,0 Md€ | **93,9 Md€** |
| Part de la dépense | 22,8 % | **22,0 %** |

Le §4 sexies porte ce total à **95,2 Md€, soit 22,3 %**, en ajoutant trois
dispositifs que l'inventaire ne portait pas.

Le COR chiffre les droits de solidarité à « de l'ordre d'un cinquième » des
retraites. On y est, et on y arrive par en dessous : ce total reste un
plancher. **Les lignes lues font 87 % du total**, et c'est le résultat le plus
net de ce chantier : ce que le modèle apporte ici n'est pas le chiffre, c'est
la LISTE — savoir ce qu'il faut compter, et sous quel article.

### Ce que la page montre désormais

Trois changements, et le premier est celui que l'utilisateur réclamait.

**Tous sont nommés.** Un tableau par famille, chaque dispositif sur
sa ligne, avec son coût sur la dernière année publiée ou, quand la case est
vide, **la phrase qui dit pourquoi**. Quinze portent un chiffre ; les
vingt-quatre autres portent une raison, et un test du dépôt refuse qu'une
ligne n'ait ni l'un ni l'autre. La page affirmait qu'il existe quarante-deux
avantages et n'en montrait pas la moitié ; un blanc sans raison est une dette,
une raison écrite est une limite.

**Un montant ne paraît qu'une fois.** La MDA du privé et la bonification pour
enfants de la fonction publique sont le même trimestre gratuit sous deux
textes, et la cascade n'en tient qu'une ligne. Le premier dispositif porte le
chiffre ; le second dit où il est, plutôt que de le répéter — un chiffre
imprimé deux fois s'additionne dans la tête du lecteur.

**Chaque case dit d'où elle vient.** « lu » ou « calculé ». Un montant compté
sur des personnes réelles et un montant refait sur treize carrières types ne se
lisent pas avec la même confiance, et la page ne peut pas laisser le lecteur
les confondre.

**Le graphique empile les familles, sur la fenêtre où tout est publié.** Quinze
lignes pour neuf couleurs donnaient six bandes portant la couleur d'une autre,
et les six plus petites tenaient dans l'épaisseur du trait ; les familles sont
le découpage que l'inventaire porte lui-même. Et la fenêtre se **calcule** au
lieu de s'écrire : c'est l'intersection des fenêtres de publication des lignes
lues, 2004 pour la réversion et 2020 pour les sous-postes des comptes. Elle
s'est donc resserrée d'elle-même à cinq points le jour où ces postes sont
arrivés. Les empiler plus tôt aurait dessiné une falaise de quarante milliards
en 2020, où le lecteur aurait vu une explosion de la dépense là où il n'y a
qu'un début de publication.

### Trois pièges rencontrés, et ce qu'ils apprennent

**Le compte annoncé n'était pas le compte montré.** La page disait « 22 des 39
dispositifs portent un chiffre » au-dessus d'un tableau qui montrait quinze
cases pleines. Les deux comptages sont justes et ne mesurent pas la même
chose : le premier compte ce que le modèle SAIT chiffrer, le second ce qui
PORTE un chiffre — un avantage éteint, ou que nul cas type ne porte, se mesure
très bien et vaut zéro. C'est le second que la page annonce désormais, parce
que c'est celui que son tableau montre.

**La ligne de commande et le site avaient divergé.** La commande d'analyse
refaisait la décomposition pour elle seule, à partir des seules masses du
modèle : elle annonçait 12,6 milliards quand la page en annonçait 93,9. L'écart
n'était pas une erreur de calcul mais une différence de périmètre — les postes
lus manquaient d'un côté. Un chiffre qui dépend de la porte par laquelle on
entre n'est pas un chiffre : le calcul vit maintenant dans le modèle, et les
deux portes y mènent.

**Une ligne sans famille disparaîtrait sans bruit.** Le graphique groupe par
famille et écarte, par sécurité, toute ligne dont il ignore la famille. Une
ligne écartée manquerait au total du tracé quand le tableau juste en dessous la
compterait. Un test l'interdit, comme un second interdit qu'une série publiée
ait un trou au milieu, ce qui couperait la fenêtre en deux.

## 4 sexies. Tous, et sur le plus d'années possibles

Deux demandes en une, et elles tirent dans des sens opposés : ajouter des
lignes rapproche de l'exhaustivité, mais chaque ligne nouvelle vient d'une
source dont la fenêtre est plus courte que celle du modèle. Le chantier a donc
buté d'abord sur un défaut, puis sur un choix.

### Le défaut : une falaise cachée à l'intérieur d'une ligne

Le §4 quinquies a posé que le poste publié REMPLACE la ligne calculée. La règle
n'était appliquée qu'aux années que le poste couvre : avant, la ligne gardait sa
valeur calculée. Le minimum vieillesse valait donc **0,02 Md€ en 2019, par le
modèle, et 4,01 Md€ en 2020, par les comptes** — un facteur deux cents à
l'intérieur d'une seule série, invisible tant que le graphique commençait en
2020.

C'est pire qu'une falaise entre deux lignes, parce que personne ne va la
chercher. La règle est donc devenue : **une ligne qui a une fois un poste publié
est publiée sur toute sa longueur**, et sa valeur calculée est jetée même pour
les années que le poste ne couvre pas. Une ligne ne mélange jamais deux
périmètres.

### Le choix : deux tracés plutôt qu'un compromis

Le prix de cette règle est une fenêtre de cinq ans, et une page qui promet
« l'évolution du coût au cours du temps » ne peut pas s'en contenter. Les
sources ne se rejoignent pourtant pas : le modèle calcule depuis 1959, la
réversion se lit depuis 2004, les sous-postes des comptes depuis 2020. Aucune
fenêtre ne contient tout.

Vérifié auprès du producteur plutôt que supposé : l'API des comptes de la
protection sociale ne publie AUCUN sous-poste du risque vieillesse-survie avant
2020, quand le total du risque remonte à 1959. Il n'y a rien à aller chercher
plus loin.

D'où deux tracés, chacun cohérent de bout en bout, et jamais additionnés :

| | Fenêtre | Ce qu'il porte | 2024 |
|---|---|---|---|
| Le **niveau** | 2020-2024 | le meilleur chiffre connu, poste publié où il existe | 95,2 Md€, 22,3 % |
| La **forme** | 1959-2024 | le modèle seul, même calcul d'un bout à l'autre | 13,1 Md€, 3,1 % |

La page dit en toutes lettres que les deux ne se comparent pas : un lecteur qui
verrait 3,1 % sous 22,3 % conclurait que les avantages ont fondu, quand c'est le
champ de la mesure qui change.

Et la forme longue dit quelque chose que le niveau ne dit pas. **Le minimum
vieillesse faisait 31 % de la dépense de retraite en 1959** : il y avait alors
peu de pensions et beaucoup de vieillards sans droits. Il s'éteint à mesure que
les carrières se complètent, et la courbe remonte à partir des années 1980 sous
l'effet des minima de pension et des périodes assimilées. Les dispositifs qui
rattrapent une carrière incomplète ont remplacé ceux qui secouraient une
carrière absente.

### Trois dispositifs que l'inventaire ne portait pas

L'arbre des comptes a été parcouru poste par poste, et trois d'entre eux ne
correspondaient à aucune ligne de l'inventaire. Base légale lue dans l'index
LEGI, version en vigueur :

| Dispositif | Base légale | 2024 |
|---|---|---|
| Indemnité temporaire de retraite outre-mer | décret n° 52-1050 du 10 septembre 1952 art. 1 ; LFR 2008 art. 137 | 0,26 Md€ |
| Retraite du combattant | L. 321-1 et L. 321-2 CPMIVG, D. 321-1 | 0,50 Md€ |
| Majoration de pension des assurés handicapés | L. 351-1-3 CSS | 0,03 Md€ |

La première est la plus nette : une majoration de 35 à 75 % de la pension des
fonctionnaires retraités résidant outre-mer, sans contrepartie de cotisation,
fermée aux nouveaux bénéficiaires depuis 2009. La deuxième n'est pas une
pension, mais les comptes la rangent dans le risque vieillesse-survie, donc dans
le dénominateur que cette page décompose : l'y laisser au numérateur et pas au
dénominateur aurait été un choix, pas une neutralité.

L'inventaire compte donc **quarante-deux dispositifs, dont dix-huit portent un
chiffre** et vingt-quatre une raison écrite.

### Le rapport du SRE, lu : il ne porte pas les bonifications

Le §4 sexies laissait les bonifications de service comme la piste suivante, et
nommait le rapport annuel du Service des retraites de l'État. Quatre éditions
ont été lues — 2019, 2021, 2023, 2024 — plus les deux infographies
« chiffres-clés » de juin 2026. **La piste est fausse** : c'est un rapport
d'*activité*, pas un document statistique. Les bonifications n'y apparaissent
que comme part du contentieux (8 % des nouvelles affaires en 2023, 5,5 % en
2024) et comme jurisprudence. Aucune masse, aucun effectif, aucun trimestre.

Le document qui les publie est le **jaune budgétaire « Pensions de retraite de
la fonction publique »**, et la preuve tient dans son tableur compagnon : celui
du PLF 2012, encore en ligne sur data.gouv.fr, porte une feuille nommée
`bonifications`. Les éditions récentes sont sur budget.gouv.fr, derrière un
pare-feu anti-robot ; le dépôt ne contourne pas. La limite est désormais
**documentée** plutôt qu'ouverte, ce qui vaut mieux qu'une piste qu'on croit
tenir.

Un gain latéral, qui n'était pas cherché. La jurisprudence citée par le rapport
2023 (Conseil d'État, 11 octobre 2023, n° 454135 et suivants) nomme le texte de
la bonification du cinquième des personnels actifs de police, que l'inventaire
portait depuis le début en « statuts particuliers — à certifier ». Lu dans LEGI
et posé : **loi n° 57-444 du 8 avril 1957, articles 1er et 6**, un cinquième du
temps passé en services actifs, plafonné à cinq annuités, et subordonné depuis
le 28 décembre 2023 à la condition de durée de services du onzième alinéa du 1°
du I de l'article L. 24. Une des deux lignes « à certifier » est close.

### Le tableur du jaune, récupéré et lu

Le rapport du SRE n'ayant rien donné, restait le jaune budgétaire. Une seule
édition est publique hors de budget.gouv.fr : celle du PLF 2012, sur
data.gouv.fr. Elle a été récupérée, et sa feuille `bonifications` dit ceci —
pour les pensions **entrées en paiement en 2010**, en bénéficiaires et en
durée moyenne, exprimée en trimestres et calculée sur les seuls bénéficiaires.

| Bonification | Pensions civiles de l'État | Pensions militaires |
|---|---|---|
| *Effectif total de l'année* | *70 095* | *12 912* |
| Du cinquième (militaires) | — | **12 817** — 16,4 trim. |
| Bénéfices de campagne | 1 290 — 3,1 trim. | **10 173** — 12,8 trim. |
| Services aériens ou sous-marins | 250 — 5,2 trim. | **7 188** — 12,8 trim. |
| Pour enfants | 27 251 — 7,6 trim. | 703 — 6,9 trim. |
| Services hors d'Europe | 7 442 — 17,7 trim. | — |
| Enseignement technique | 508 — 12,7 trim. | — |
| Hors article L. 12 CPCMR | 3 477 — **19,1 trim.** | 270 — 4,9 trim. |

**Le chiffre qui saute aux yeux est la bonification du cinquième :
12 817 des 12 912 pensions militaires de l'année, soit 99,3 %**, pour 16,4
trimestres en moyenne. Plus de quatre annuités que personne n'a cotisées,
servies à la quasi-totalité des militaires qui partent. Les bénéfices de
campagne en touchent quatre sur cinq, les services aériens ou sous-marins plus
d'un sur deux. Chez les civils, la plus longue est celle qui ne relève pas de
l'article L. 12 du CPCMR — 19,1 trimestres —, que la note du tableau dit
« principalement attribuées aux policiers et agents de l'administration
pénitentiaire » : c'est la bonification de la loi n° 57-444 lue plus haut.

**Ce n'est pas un coût, et ces chiffres ne sont pas certifiés.** Trois réserves,
et chacune suffirait : c'est un FLUX d'entrée et non un stock de pensions
servies ; ce sont des bénéficiaires et des trimestres, jamais des euros ; et ils
datent de 2010. Ils vivent donc dans les notes de l'inventaire, avec leur date,
et la page ne les affiche pas. Les colonnes de la CNRACL, pour la fonction
publique territoriale et hospitalière, sont d'ailleurs déclarées dans l'en-tête
du tableau et laissées vides par le producteur.

Ils déplacent tout de même quelque chose. L'inventaire disait de ces lignes
« population étroite » ; c'est vrai chez les civils et faux chez les militaires,
où la bonification est la règle et non l'exception. Une ligne sans chiffre
invite à la croire petite.

### L'édition 2026, lue par-dessus l'épaule

Le jaune récent est arrivé par l'utilisateur, qui l'a téléchargé depuis son
propre navigateur et en a montré les pages. Le dépôt ne sait pas le récupérer :
`budget.gouv.fr` refuse les adresses de sortie du proxy, page comme fichier,
`curl` comme navigateur — ce n'est pas le fingerprint du client qui est en
cause mais son adresse IP, et la déguiser serait d'une autre nature que
naviguer. Ces valeurs sont donc **saisies et non certifiées** : aucun script ne
peut les revérifier, et chacune porte son numéro de tableau pour qu'un lecteur
la retrouve.

**Tableau A-7 — bénéficiaires et durée moyenne, pensions en paiement en 2024.**
C'est un *stock*, là où l'édition 2012 ne donnait qu'un flux d'entrée.

| | FPE civiles | FPE militaires | FPT | FPH |
|---|---|---|---|---|
| *Effectif du régime* | *1 654 863* | *406 645* | *800 833* | *630 149* |
| Dépaysement | 180 010 — 17,3 tr. | 447 — 4,2 | 39 933 — 18,7 | 23 874 — 22,1 |
| Enfant | 786 167 — 8,3 | 24 603 — 7,7 | 341 086 — 8,1 | 415 564 — 8,6 |
| Campagne ou cinquième | 88 932 — 4,9 | **404 478 — 27,4** | 6 559 — 3,2 | 2 339 — 3,1 |
| Services aériens ou sous-marins | 8 415 — 7,0 | 202 113 — 16,9 | 2 708 — 9,0 | 54 — 5,6 |
| Enseignement technique | 13 893 — 16,1 | 39 — 12,9 | n.d. | n.d. |
| Hors article L. 12 | 108 453 — 19,1 | 8 126 — 5,5 | n.d. | n.d. |

Le chiffre de 2010 se confirme sur le stock, et en pire : **404 478 des 406 645
pensions militaires en paiement portent une bonification de campagne ou du
cinquième, pour 27,4 trimestres** — près de sept annuités, sur la quasi-totalité
du régime.

**Tableau 50 — le gain sur le montant mensuel de la pension**, flux des
liquidants de 2023. C'est la seule valorisation en euros que le producteur
publie, et elle manquait à tout ce chantier.

| | Dépaysement | Enfant | Campagne | Aérien/SM | Ens. tech. | Cinquième | Non L12 | **Ensemble** |
|---|---|---|---|---|---|---|---|---|
| FPE civils | 266 € | 195 € | 56 € | 157 € | 330 € | n.p. | 312 € | **246 €** |
| Militaires | n.p. | 59 € | 101 € | 69 € | n.p. | 146 € | 59 € | **315 €** |

La colonne « Ensemble » n'est pas une somme : c'est le gain TOTAL des personnes
portant au moins une bonification, dédoublonné par le producteur. C'est elle
qu'il faut prendre, une même pension pouvant en porter plusieurs.

### L'ordre de grandeur, et pourquoi ce n'est pas un coût certifié

En appliquant au stock la proportion de bénéficiaires et le gain par tête :

| | Effectif | Bénéficiaires | Gain mensuel | Masse annuelle |
|---|---|---|---|---|
| FPE civils | 1 654 863 | 56,9 % | 246 € | **2,8 Md€** |
| FPE militaires | 406 645 | 99,6 % | 315 € | **1,5 Md€** |
| | | | | **≈ 4,3 Md€** |

La CNRACL n'est pas valorisable : le tableau 50 y porte « n.d. » pour les
euros, alors que ses effectifs sont connus. Le chiffre ne couvre donc que la
fonction publique d'État.

**Trois réserves, et la première suffit à interdire la certification.** Le
produit croise un STOCK de 2024 avec un gain par tête mesuré sur le FLUX de
2023 : c'est une déduction posée sur deux tableaux, non une valeur lue. Le
dépôt sait faire la différence, et la page n'affiche donc pas ces 4,3 milliards
dans sa colonne de coût, où ils voisineraient des postes publiés qui, eux,
comptent des euros versés.

Le sens du biais se dit tout de même. Le jaune note lui-même « un recul des
bonifications » sur la période récente : les pensions anciennes en portent donc
plutôt plus que celles qui entrent, et 4,3 milliards est un **plancher** pour
le stock. Enfin, un gain de pension n'est pas un surcoût net pour le système —
la même réserve que pour les départs anticipés, écrite au §4 bis.

Ce que la page dit désormais, à défaut d'un montant : sur chacune de ces cinq
lignes, la colonne « pourquoi il manque » porte le dénombrement. « Un militaire
retraité sur deux, 16,9 trimestres » vaut mieux qu'un tiret.

### La dernière base légale, et ce qu'elle corrigeait

L'inventaire portait depuis le début deux lignes dont la base légale disait
« à certifier ». Les bonifications des corps actifs ont été closes par le jaune,
qui nomme les quatre lois. Restait l'article 41 de la loi n° 98-1194 du
23 décembre 1998, pour la cessation anticipée des travailleurs de l'amiante. Il
a été lu, et **il corrigeait la raison inscrite**.

L'inventaire disait de ce dispositif qu'il « relève du risque emploi et non du
risque vieillesse-survie », donc hors du compte que la page décompose. C'est
vrai de l'allocation. Mais le III de l'article crée un fonds qui finance aussi,
*par un versement aux régimes obligatoires de retraite de base*, les dépenses
supplémentaires nées des départs anticipés qu'il permet ; et le II répute la
durée d'assurance remplie au plus tard à soixante-cinq ans. Il y a donc bien une
part vieillesse, identifiée par la loi et financée de l'extérieur — la forme
même des transferts de la branche famille et de l'assurance chômage.

Elle n'est pas chiffrée pour autant : le compte du fonds, publié à la Commission
des comptes de la Sécurité sociale, mêle l'allocation et le versement aux
régimes sans les séparer. La ligne garde donc son tiret, mais sa raison est
désormais exacte.

**Aucune ligne ne porte plus « à certifier ».** Les quarante-deux dispositifs
ont leur base légale lue dans LEGI, version par version. C'est un seuil, et il
mérite d'être dit pour ce qu'il est : lire n'est pas appliquer. Que les textes
soient lus ne dit pas que le modèle les applique, et vingt-quatre dispositifs
restent sans chiffre.


### Il a fallu écrire le lecteur

Le tableur est un classeur Excel 97, et le dépôt en a un lecteur, sans
dépendance. Il ne rendait que les NOMBRES, par un choix assumé et écrit dans son
en-tête : il ne servait qu'à reprendre une grille de quotients de mortalité. La
feuille des bonifications rendait donc trente-sept nombres et pas un libellé,
soit trente-sept nombres dont on ignorait ce qu'ils comptaient. Un nombre sans
son intitulé n'est pas une donnée.

La table des chaînes partagées est désormais décodée. Sa difficulté n'est pas
l'encodage mais la **coupure** : un enregistrement BIFF ne dépasse pas huit
mille octets, la suite passe dans des enregistrements `CONTINUE`, et la coupure
peut tomber au milieu des caractères d'une chaîne — qui recommence alors par un
octet redisant leur largeur, si bien qu'un même mot peut être coupé en latin-1
et reprendre en UTF-16. Mal décodée, la table ne lève aucune erreur : elle
**décale**, et tous les libellés suivants glissent d'un cran sous d'autres
lignes. Un test synthétique force donc ce cas précis. Le lecteur rend maintenant
`float | str`, comme celui des classeurs modernes : les deux se lisent de la
même façon.

### Ce que ces trois lignes apprennent

Elles ne pèsent que 0,8 milliard à elles trois, et ce n'est pas le point. Le
point est qu'elles étaient **publiées depuis 2020 et que personne ne les avait
regardées** : l'inventaire avait été bâti en partant des trois listes du dépôt,
qui décrivent ce que le modèle sait faire, et non en partant de la nomenclature
du producteur, qui décrit ce que le système verse. Les deux ne se recouvrent
pas, et c'est la seconde qui fait foi sur l'exhaustivité.

Le compte de dispositifs a d'ailleurs été retiré de la prose de la page partout
où il n'était pas calculé. Il y était écrit en toutes lettres à huit endroits ;
il s'est périmé d'un coup. Un nombre qui vit dans une phrase est un nombre qui
ment un jour.

## 5. Pourquoi, et c'est le vrai résultat de ce chantier

Deux causes, et elles ne se corrigent pas de la même façon.

**La première est connue et écrite** : vingt-quatre des quarante-deux
dispositifs ne portent pas de chiffre sur la dernière année publiée, et
l'inventaire dit, pour chacun, laquelle des deux raisons s'applique — le modèle
ne sait pas le mesurer, ou aucun poste publié ne l'isole. Ce qui reste vraiment
hors de portée, ce sont les bonifications de service des militaires et des
corps actifs, les départs anticipés pour handicap, la majoration de durée au
titre du congé parental et l'allocation veuvage.

**La seconde ne l'était pas, et c'est le vrai résultat de ce chantier : la
grille de cas types n'a pas d'enfants.** Sur les treize cas types, **un seul**
en a — `carriere_interrompue`, deux enfants. Conséquences mécaniques, et non
accidentelles :

- la **majoration de pension pour trois enfants et plus** valait **zéro toutes
  les années de la série**, parce que le seuil est à trois et qu'aucun cas type
  ne l'atteint. Les comptes de la protection sociale en portent 7,78 milliards
  en 2024 ;
- la **surcote parentale** vaut zéro pour la même raison ;
- l'**AVPF** et la **MDA** ne sont portées que par ce seul cas type, au poids de
  sa caisse. L'AVPF mesurée tombe à 0,0 milliard en 2024 quand la CNAF verse
  5,1 milliards de cotisations à ce titre.

La grille de cas types est faite pour **comparer des systèmes sur une même
carrière** : c'est un instrument de rapport, et les erreurs de niveau
s'annulent au dénominateur. Elle n'est pas faite pour **compter une
population**, et le coût d'un avantage est un compte de population. Le dépôt le
savait déjà pour la garantie vieillesse — les 93 milliards que les cas types en
tiraient étaient un chiffre faux, et le barème a été appliqué à la distribution
DREES pour donner 18,4 milliards.

**La correction a été faite ici, mais par l'autre bout.** Reconstruire une
population par nombre d'enfants, par sexe et par génération était la voie
longue ; lire le poste que la DREES publie était la voie courte, et elle donne
un compte de personnes réelles plutôt qu'un modèle. Là où les deux existent, le
poste publié l'emporte — c'est le premier critère de `data/sources.yaml`, le
producteur prime sur le repreneur. **Les lignes lues font aujourd'hui 87 % du
total chiffré.** Ce que le modèle apporte n'est donc pas le chiffre : c'est la
liste, et l'article sous lequel chercher.

## 6. Ce qu'il faut faire, dans l'ordre

1. **Les droits familiaux se lisent là où ils sont publiés — c'est fait pour
   la majoration de pension**, 7,78 Md€ en 2024 (§4 quinquies). Restent la
   surcote parentale, qui ne paiera qu'à compter de 2026, et la majoration de
   durée au titre du congé parental, qu'aucun poste n'isole. La distribution
   des retraités par nombre d'enfants, par sexe et par génération reste
   souhaitable : elle seule permettrait de vérifier le poste publié au lieu de
   le recopier, et de projeter ce que ces droits deviennent.
2. **La réversion se lit, elle ne se calcule pas — c'est fait.** 38,3 Md€ en
   2024, lus dans l'enquête annuelle de la DREES auprès des caisses (§4 quater).
   La majoration de réversion et les pensions d'orphelin ont suivi par les
   comptes. Reste l'allocation veuvage, qu'un poste fourre-tout absorbe.
3. **Les onze lignes « intégrées » se chiffrent par retrait — c'est fait.** Huit
   le sont, par la carrière, par le catalogue ou par une table (§4 bis et
   4 ter) ; les trois autres ne sont pas des dispositifs et se lisent ailleurs.
   Ce qui reste n'est plus une mesure à faire mais une POPULATION à trouver :
   quatre des huit ne pèsent rien sur la fenêtre publiée, faute de chômeurs,
   d'appelés et de parents dans la grille. C'est le point 1.
4. **Les trois contrôles externes du dépôt doivent être opposés au résultat** :
   `cnaf_avpf` et `cnaf_majorations` pour les droits familiaux, `fsv_cotisations`
   pour le chômage, `unedic_agirc_arrco` pour les points gratuits de
   complémentaire. Aucun ne couvre le même champ que le modèle ; tous doivent
   varier dans le même sens.

## 7. Une contradiction relevée au passage

`Neutralisations` porte `reversion: bool = True`, c'est-à-dire « les scénarios
notionnels retirent la réversion ». Son propre docstring dit, six lignes plus
haut, que le scénario 1 ne la sert pas. **Neutraliser ce que l'étalon n'a jamais
servi ne change rien**, et l'écart annoncé entre les systèmes n'en contient pas
un euro. La ligne reste — elle décrit une intention de réforme, ce qui est son
rôle —, mais l'inventaire la range sous `declare`, et dit pourquoi.

---

Voir aussi : `docs/limites.md` pour les écarts au droit positif,
`docs/veille_droit.md` pour l'obligation de lecture des sources,
`docs/methodologie.md` §6 pour ce que les scénarios notionnels retirent.
