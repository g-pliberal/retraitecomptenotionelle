# Les avantages non contributifs du scénario 1

Le scénario 1 est le droit en vigueur. Un compte notionnel ne sert que ce qui a
été cotisé. **Tout ce qui sépare les deux est ici** : trente-neuf dispositifs,
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
| **intégré** | 11 | Le scénario 1 le sert, mais l'effet passe par un trimestre, un âge ou une assiette. Il ne s'isole qu'en recalculant la pension une seconde fois, avantage retiré. **Deux le sont désormais** — les périodes assimilées et la catégorie active : voir le §4 bis. |
| **déclaré** | 3 | Une fiche de régime le déclare, aucun code ne le sert. La déclaration est une intention. |
| **absent** | 17 | Ni déclaré ni servi. C'est un écart au droit positif. |

Et trois façons d'en mesurer le coût : par le **modèle** (la cascade, ou un
recalcul de même nature), par une **série publiée**, ou par **rien** — ce
dernier cas étant une limite qu'il vaut mieux écrire qu'estimer.

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

**Ce chiffre reste faux, et il faut dire de quelle façon.** Le COR chiffre les
droits de solidarité à « de l'ordre d'un cinquième des retraites tous régimes »
(rapport du 27 janvier 2010, commandé par l'article 75 de la LFSS 2009). Un
cinquième de 426,7 milliards fait 85 milliards. Le modèle en mesure 12,6.

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
| 2024 | 426,7 | **23,7** | **5,6 %** | 5,6 | 8,8 | 9,3 |

**23,7 milliards en 2024, soit quinze fois l'effet de montant.** Et la
composition change : jusqu'aux années 2010 les départs anticipés viennent
entièrement des statuts classés et des régimes spéciaux ; la **carrière longue**
n'apparaît qu'ensuite, et pèse 5,6 milliards en 2024 — mécaniquement, à mesure
que l'âge légal monte au-dessus de l'âge auquel une carrière commencée tôt
réunit sa durée.

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

## 5. Pourquoi, et c'est le vrai résultat de ce chantier

Deux causes, et elles ne se corrigent pas de la même façon.

**La première est connue et écrite** : vingt-neuf des trente-neuf dispositifs
ne sont pas chiffrés, et l'inventaire dit lesquels. La réversion pèse à elle
seule plus que tout ce qui est mesuré ici, et le modèle ne peut pas la voir —
il décrit une carrière, pas un ménage. Les périodes assimilées, la catégorie
active, les bonifications de service sont dans le même cas, chacune pour sa
raison propre.

**La seconde ne l'était pas, et elle est plus grave : la grille de cas types n'a
pas d'enfants.** Sur les treize cas types, **un seul** en a — `carriere_interrompue`,
deux enfants. Conséquences mécaniques, et non accidentelles :

- la **majoration de pension pour trois enfants et plus** vaut **zéro toutes les
  années de la série**, parce que le seuil est à trois et qu'aucun cas type ne
  l'atteint. La CNAF rembourse pourtant 5,9 milliards à ce titre en 2025
  (`macro/transferts_retraite.csv`, poste `cnaf_majorations`), et ce n'est que la
  part du régime général ;
- la **surcote parentale** vaut zéro pour la même raison ;
- l'**AVPF** et la **MDA** ne sont portées que par ce seul cas type, au poids de
  sa caisse. L'AVPF mesurée tombe à 0,0 milliard en 2024 quand la CNAF verse
  5,1 milliards de cotisations à ce titre.

La grille de cas types est faite pour **comparer des systèmes sur une même
carrière** : c'est un instrument de rapport, et les erreurs de niveau
s'annulent au dénominateur. Elle n'est pas faite pour **compter une population**,
et le coût d'un avantage est un compte de population. Le dépôt le savait déjà
pour la garantie vieillesse — les 93 milliards que les cas types en tiraient
étaient un chiffre faux, et le barème a été appliqué à la distribution DREES
pour donner 18,4 milliards. **La même correction est due ici, et pour la même
raison.**

## 6. Ce qu'il faut faire, dans l'ordre

1. **Les droits familiaux se chiffrent sur une structure de population, pas sur
   les cas types.** Il faut la distribution des retraités par nombre d'enfants,
   par sexe et par génération. Sans elle, toute la première famille vaut zéro ou
   presque, et c'est la plus documentée du système français.
2. **La réversion se lit, elle ne se calcule pas.** La DREES publie la masse des
   droits dérivés par régime et par sexe dans le panorama « Les retraités et les
   retraites ». C'est la seule ligne de l'inventaire dont le coût s'obtienne sans
   aucun recalcul — et c'est la plus lourde.
3. **Les onze lignes « intégrées » se chiffrent par recalcul**, exactement comme
   les huit lignes de cascade : on recalcule la pension sans l'avantage, et
   l'écart est la ligne. Les périodes assimilées et la catégorie active sont les
   deux plus lourdes, et les deux les plus faciles — le modèle sert déjà les
   deux, il suffit de les retirer.
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
