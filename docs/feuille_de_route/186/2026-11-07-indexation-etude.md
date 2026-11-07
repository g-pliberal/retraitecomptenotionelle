# L'indexation étudiée aux sources, et le partage de l'effort entre actifs et retraités

**Reprise, au 7 novembre 2026.** Le chantier 5 est étudié. Ses pistes sont au
propriétaire (« Les pistes, pour le propriétaire ») : le facteur démographique
et sa valeur α, le plancher en euros, et la garantie en quatre promesses. Ses
réponses s'écrivent en décisions sous le chantier 5 de
`docs/feuille_de_route_programme.md`. Ensuite, une session du modèle écrit le
facteur en paramètre pour le seul scénario 6, et la page Coût chiffre chaque α.
Restent à lire à leur source les textes marqués « non vérifié ».

*Le 7 novembre 2026, le propriétaire ouvre le chantier 5 de l'action 186 :
« Je veux qu'on attaque ce chantier ». La feuille de route du programme y
demande les règles suédoise, allemande, italienne, lettone et polonaise, à
leurs sources, et ce que chacune aurait donné en France depuis 2000, par le
modèle ; au propriétaire, l'indexation des pensions servies et la
formulation de la garantie. Ce rapport sort de deux travaux : une recherche
aux sources étrangères, confiée à un agent qui a lu les lois et les rapports
des caisses, et un calcul sur les séries du modèle. Les notes de l'agent et
le script du calcul sont restés dans le brouillon de la session, hors du
dépôt ; les conventions du calcul sont écrites plus bas. Ce que le rapport
conclut est une piste, pas une décision : le propriétaire tranche
(`docs/feuille_de_route_programme.md`, chantier 5).*

## L'essentiel : la règle des pensions servies dit qui porte quel risque

**Dans un compte notionnel, l'indexation de la pension servie et la pension
de départ sont un seul contrat.** À compte égal, une pension indexée sur la
masse salariale part du capital divisé par l'espérance de vie, 23,6 ans à
64 ans en 2026. Une pension indexée sur les prix peut partir 11 % plus haut,
si le diviseur escompte 0,8 % de croissance réelle : c'est le choix italien.
La pension suédoise, qui escompte 1,6 %, part 23 % plus haut (modèle). La
règle choisie ne décide donc pas de la générosité du système. Elle décide de
qui porte trois risques : une croissance plus faible que prévu, un emploi
qui baisse (l'IA, un chômage de masse), un nombre de retraités par cotisant
qui monte.

**Indexer les pensions servies sur la masse salariale n'est pas une mesure
d'austérité.** Depuis 2000, la masse salariale a crû de 1,4 point par an
au-dessus des prix, parce que l'emploi a crû. Une pension liquidée en 2000
et indexée sur elle vaudrait en 2026 **1,44 fois plus que sur les prix**, en
euros constants. Le droit, lui, lui a servi 4 % de moins que les prix.
Appliquée à tout le stock depuis 2000, cette règle porterait la masse des
pensions d'aujourd'hui **à 18 % de plus, soit environ 78 Md€** (à côté). Les
retraités ne partagent un effort, sous cette règle, que les années où
l'emploi baisse.

**La règle du propriétaire n'est pas celle de la masse salariale.** Selon
cette règle, quand l'âge des actifs recule, les pensions baissent. Or la
réforme de 2023 a reculé l'âge, et les pensions de base ont été revalorisées
de 5,3 % au 1er janvier 2024 (vérifié). La masse salariale, elle, aurait
donné 5,6 %. Seul un **facteur démographique**, comme le facteur allemand de
2004, lie la pension au nombre de retraités par cotisant. Un fait le rend
présentable : **les prix corrigés du facteur allemand, à partir de 2005,
auraient servi de 2000 à 2026, à 0,6 % près, ce que la France a servi** par ses gels et ses
sous-indexations décidés au coup par coup (2014, 2018, 2019, 2020). Le
partage existe donc déjà en France ; il n'est simplement pas écrit.

**Les baisses suédoises sont vérifiées** : les pensions de revenu ont baissé
de **3,0 % en 2010, 4,3 % en 2011 et 2,7 % en 2014**, dont 1,7, 4,5 et
1,6 points dus au seul mécanisme d'équilibre. Le gouvernement les a
compensées en 2010 et 2011 par des baisses d'impôt sur les pensions. Aucun
des cinq pays ne promet un montant, sauf l'Allemagne, qui tient un niveau de
48 % jusqu'en 2031 aux frais de son budget fédéral. Quatre sur cinq
promettent que la pension ne baisse jamais en euros ; la Suède est la seule
qui ne le promet pas.

*Lire les chiffres.* Chaque chiffre porte son origine.
- **(modèle)** : une sortie du modèle du dépôt au commit `e98667e`, sous ses
  réglages par défaut. Ce sont le diviseur de conversion
  (`Convertisseur.coefficient`, génération née en 1962 partie à 64 ans en
  2026) et les séries de prix, de salaire moyen par tête, de masse salariale
  et de PIB nominal (`DonneesMacro`). Ces séries sont observées jusqu'en 2025
  et projetées ensuite sous le scénario de référence du COR de juin 2026 :
  1,75 % d'inflation, 2,45 % de salaire moyen.
- **(à côté)** : un calcul fait hors du modèle, sur ces séries et sur les
  données du dépôt, par un script de la session resté dans son brouillon.
- **(publié)** : un texte de loi ou un chiffre d'un organisme.
- **(non vérifié)** : ce qui n'a pas été lu à sa source.

## Ce que le dépôt fait déjà

**Les comptes.** Par défaut, ils sont revalorisés sur la masse salariale :
les salaires et traitements bruts des comptes nationaux. C'est le taux
d'équilibre d'une répartition, et huit autres règles sont au choix
([README, § 1 à 1 quater](../../../README.md)).

**La pension notionnelle servie.** Une fois liquidée, elle suit la même
règle que le compte
([`RevalorisationServie`](../../../src/retraite_notionnelle/revalorisation.py)).
Le diviseur vaut l'espérance de vie résiduelle, parce que le taux qu'il
escompte, `taux_anticipe_conversion`, est nul par défaut. Ce réglage est
déjà la règle suédoise : avec un taux de 1,6 %, le diviseur passe de 23,6 à
19,2 ans, et la pension servie se revalorise au taux du compte divisé par
1,016. Le modèle peut donc déjà montrer l'un et l'autre profil.

| Taux escompté par le diviseur | Diviseur à 64 ans en 2026 | Pension de départ, à compte égal |
|---|---|---|
| 0 (le défaut : l'espérance de vie) | 23,63 | ×1,000 |
| 0,5 % | 22,09 | ×1,070 |
| 0,8 % | 21,24 | ×1,113 |
| 1,0 % | 20,70 | ×1,142 |
| 1,6 % (la Suède) | 19,20 | ×1,231 |

(modèle)

**Les pensions déjà servies le jour de la bascule.** Elles gardent par
défaut l'indexation sur les prix que le droit leur promet
(`RevalorisationStock.PRIX`, [config.py](../../../src/retraite_notionnelle/config.py)) ;
`REINDEXE` les fait passer à la règle du compte.

**Le scénario 1.** C'est le droit : la pension de base suit les prix
(L. 161-23-1), la complémentaire suit la valeur de service de
l'Agirc-Arrco. Les coefficients de la Cnav depuis 1949 sont dans
[revalorisation_pensions.csv](../../../data/reference/legislation/revalorisation_pensions.csv).
Du 1er janvier 2000 au 1er janvier 2026, ils cumulent ×1,476 quand les prix
cumulent ×1,539 : **le droit a retiré 4,1 % de pouvoir d'achat aux pensions
de base liquidées en 2000** (à côté). La perte vient du gel d'avril 2013 à
octobre 2015, du report de 2018, des 0,3 % de 2019 et de la revalorisation
de 2020 par tranches.

## Cinq pays, à leurs sources

| Pays | Le compte, pendant la carrière | La pension servie | Plancher | Équilibre automatique |
|---|---|---|---|---|
| Suède | le revenu moyen soumis à cotisation, d'une année sur l'autre (depuis 2017) | le même indice, divisé par 1,016 | aucun | oui : le frein, qui a joué de 2010 à 2017, plus une distribution des excédents à partir de 2027 |
| Allemagne | (pas de compte : des points) | le salaire moyen × un facteur de cotisation × un facteur démographique (α = 0,25) ; depuis 2024 et jusqu'en 2031, de quoi tenir 48 % | pas de baisse, rattrapée sur les hausses suivantes | le facteur démographique, neutralisé de 2024 à 2031 |
| Italie | le PIB nominal, en moyenne géométrique sur cinq ans | les prix, à 100, 90 et 75 % selon la tranche de pension | coefficient du compte ≥ 1 avec rattrapage ; pension ≥ 0 | non : seuls les coefficients de conversion suivent l'espérance de vie |
| Lettonie | la masse des salaires soumis à cotisation | les prix + 50 à 80 % de la croissance réelle de la masse salariale, selon la durée d'assurance, sur la part de pension sous le salaire moyen | pas de baisse | non ; gels votés de 2009 à 2012 |
| Pologne | la somme des cotisations, au moins l'inflation | les prix des ménages de retraités + au moins 20 % de la croissance réelle du salaire moyen | pas de baisse | non ; le budget de l'État garantit le fonds |

(publié)

**La Suède.** Les règles sont dans le
[socialförsäkringsbalken](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/socialforsakringsbalk-2010110_sfs-2010-110/),
chapitres 58 et 62.
- Le compte suit l'inkomstindex : la croissance du revenu moyen des 16-65 ans
  soumis à pension, net de la cotisation de 7 % (58 kap. 11 et 12 §§).
  Jusqu'en 2016, c'était la croissance réelle moyenne sur trois ans, plus
  l'inflation.
- La pension servie suit le même indice, divisé par 1,016 (62 kap. 43 §).
- Le frein joue quand le rapport de l'actif (fonds et « actif de
  cotisation ») au passif passe sous 1 (58 kap. 14 à 24 §§). Depuis 2017, il
  n'en reporte que le tiers.
- La loi 2026:1301 ajoute une distribution des excédents au-delà de 1,15.

Le frein a joué de 2010 à 2017. D'après l'[annexe de Pensionsmyndigheten de
2025](https://www.pensionsmyndigheten.se/content/dam/pensionsmyndigheten/pressmeddelanden/Bilaga%20till%20pressmeddelande%20inkomstpensionens%20utveckling2025.pdf),
les pensions servies ont baissé de 3,0 % en 2010, de 4,3 % en 2011 et de
2,7 % en 2014, et monté les autres années. L'agent a refait ces baisses à
partir des indices publiés (133,56 / 137,31 / 1,016 = 0,957 pour 2011).

La [proposition 2009/10:29](https://data.riksdagen.se/dokument/GX0329.html)
part explicitement de ces baisses pour relever l'abattement des plus de
65 ans : le revenu net des retraités reste « ungefär oförändrad » de 2009 à
2010. Pensionsmyndigheten
([2019](https://www.pensionsmyndigheten.se/content/dam/pensionsmyndigheten/blanketter---broschyrer---faktablad/publikationer/rapporter/2019/Finns-det-en-pensionarsskatt.pdf))
le confirme pour 2010 et 2011. Le texte même de la loi de finances pour 2011
n'a pas été lu (non vérifié).

De 2002 à 2026, la pension servie a cumulé +51,6 %, contre +60,4 % pour le
prisbasbelopp, l'indice des prix des prestations. **Les retraités suédois
ont perdu 5,5 % de pouvoir d'achat en vingt-quatre ans**, à peu près ce que
le droit français a retiré aux pensions de base (même annexe).

**L'Allemagne.** Les règles sont dans le SGB VI,
[§ 68](https://www.gesetze-im-internet.de/sgb_6/__68.html) et
[§ 68a](https://www.gesetze-im-internet.de/sgb_6/__68a.html). Au 1er juillet,
la valeur du point est multipliée par trois facteurs :
- le facteur de salaire : la croissance du salaire moyen de t−2 à t−1 ;
- le facteur de cotisation ;
- le facteur démographique : 1 + 0,25 × (1 − RQ(t−1) / RQ(t−2)), où le
  « Rentnerquotient » RQ rapporte les retraités aux cotisants, comptés en
  équivalents.

Quand le nombre de retraités par cotisant monte de 4 %, la pension perd donc
un point de revalorisation : le quart de l'effort démographique va aux
retraités.

La clause de protection interdit toute baisse. La baisse évitée se reprend
ensuite sur les hausses, divisées par deux jusqu'à épuisement, comme en
2021-2022.

La « Haltelinie » ([§ 255e](https://www.gesetze-im-internet.de/sgb_6/__255e.html))
relève la valeur du point pour tenir 48 % de taux de remplacement net avant
impôt. Elle a été prolongée jusqu'à l'adaptation du 1er juillet 2031 par le
« Rentenpaket 2025 », entré en vigueur le 1er janvier 2026
([DRV](https://www.deutsche-rentenversicherung.de/SharedDocs/FAQ/Gesetzesaenderungen/rentenpaket-2025/Rentenpaket-2025.html)).
Depuis 2024, le facteur démographique ne joue donc plus. En 2026, la
revalorisation est de 4,24 %, contre 4,05 % sous la formule ; l'État fédéral
paie l'écart
([DRV](https://www.deutsche-rentenversicherung.de/SharedDocs/FAQ/Gesetzesaenderungen/Rentenanpassung/FAQ-Rentenanpassung-2026/Rentenanpassung-2026.html)).
La référence au Bundesgesetzblatt n'a pas été lue (non vérifié). L'Allemagne
a donc écrit le partage en 2004, puis l'a suspendu vingt ans plus tard,
quand il commençait à mordre.

**L'Italie.** Les règles sont dans la [loi n° 335/1995, art. 1, al. 8 et 9](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1995-08-08;335~art1),
et dans la [loi n° 388/2000, art. 69](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2000-12-23;388~art69),
modifiée par la loi n° 160/2019.
- Le compte suit le PIB nominal, en moyenne géométrique sur cinq ans, avec un
  coefficient jamais sous 1, rattrapé ensuite (décret-loi n° 65/2015). Le
  plancher a joué pour 2013 et pour 2020.
- La pension servie suit les prix : à 100 % jusqu'à quatre fois le minimum,
  90 % de quatre à cinq fois, 75 % au-delà. Elle ne baisse jamais.
- Il n'y a pas de mécanisme d'équilibre.

Le gel de 2012-2013, au-delà de trois fois le minimum
([décret-loi n° 201/2011, art. 24, al. 25](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2011-12-06;201~art24)),
a été annulé par la Cour constitutionnelle (arrêt n° 70/2015). Les motifs de
l'arrêt n'ont pas été lus (non vérifié). Les taux de 2023 (8,1 %) et de 2024
(5,4 %) ne sont connus que de sources secondaires (non vérifié).

**La Lettonie.** Les règles sont dans la loi
[« Par valsts pensijām »](https://likumi.lv/ta/id/38048-par-valsts-pensijam),
art. 12 et 26, et leurs règlements.
- Le compte suit la masse des salaires soumis à cotisation, avec un plancher
  à 1 rattrapé depuis 2016.
- La pension est revalorisée au 1er octobre : les prix, plus 50 % de la
  croissance réelle de la masse salariale (60 % de 30 à 39 ans d'assurance,
  70 % de 40 à 44, 80 % au-delà).
- Seule la part sous le salaire moyen est revalorisée ; jusqu'en 2024,
  c'était la part sous la moitié du salaire moyen.
- La pension a été gelée par la loi de 2009 à 2012. Les indices d'avant 2014
  n'ont pas été lus (non vérifié).

**La Pologne.** Les règles sont dans la loi du 17 décembre 1998 sur les
pensions du FUS ([texte consolidé, 2025](https://eli.gov.pl/api/acts/DU/2025/1749/text/O/D20251749.pdf)).
- Le compte suit la somme des cotisations, au moins l'inflation, et ne
  baisse pas (art. 25).
- Au 1er mars, la pension suit les prix des ménages de retraités, plus
  « au moins » 20 % de la croissance réelle du salaire moyen (art. 88 et 89).
  En 2025 : 103,6 + 1,9 = 105,5 %.
- Il n'y a pas de mécanisme d'équilibre : le budget de l'État garantit la
  solvabilité du fonds.
- Les indices d'avant 2009 n'ont pas été lus (non vérifié).

**La Pologne et la Lettonie sont les deux seuls pays qui revalorisent le
compte sur la masse salariale.** Aucun des cinq ne revalorise la pension
servie sur toute la masse salariale. Les deux qui s'en approchent la
revalorisent sous la croissance du compte : la Suède par la division par
1,016 et un indice qui ignore l'emploi, la Lettonie par une part de 50 à
80 %. Tous les deux ont dû geler ou freiner.

## Ce que chaque règle aurait donné en France depuis 2000

Chaque règle est appliquée aux séries françaises : une pension liquidée le
1er janvier 2000 est suivie jusqu'au 1er janvier 2026. Le taux d'une année
s'applique au 1er janvier suivant, comme la revalorisation légale. Les
règles sont celles des textes, avec cinq approximations, toutes reprises
sous « Ce que la note tient pour fragile » :
- le revenu moyen suédois est lu sur le salaire moyen par tête, sans le
  frein, que la France n'a pas de bilan pour calculer ;
- la règle allemande n'a ni le facteur de cotisation ni la Haltelinie ;
- son rapport retraités/cotisants est celui de la DREES, les retraités de
  droit direct sur l'emploi (2004-2024), puis celui de la Cnav projeté par le
  COR ;
- l'Italie est servie à 100 % ;
- la Lettonie est prise sur toute la pension.

| Règle des pensions servies | ×, en euros courants | ×, en euros constants | face au droit |
|---|---|---|---|
| Le droit (coefficients de la Cnav) | 1,476 | 0,959 | 1,000 |
| Les prix (le texte français ; l'Italie) | 1,539 | 1,000 | 1,042 |
| Les prix × le facteur allemand (α = 0,25), depuis 2005 | 1,485 | 0,965 | **1,006** |
| Les prix × le facteur entier (α = 1), depuis 2005 | 1,332 | 0,866 | 0,902 |
| La Suède (revenu moyen ÷ 1,016) | 1,226 | 0,797 | 0,831 |
| La Pologne (prix + 20 % du réel) | 1,613 | 1,048 | 1,092 |
| La masse salariale par retraité | 1,636 | 1,063 | 1,108 |
| L'Allemagne (salaire moyen × facteur, α = 1), depuis 2005 | 1,547 | 1,006 | 1,048 |
| L'Allemagne (salaire moyen × facteur, α = 0,25), depuis 2005 | 1,755 | 1,140 | 1,189 |
| Le salaire moyen par tête | 1,853 | 1,204 | 1,255 |
| La Lettonie (prix + 50 % du réel de la masse salariale) | 1,883 | 1,224 | 1,276 |
| Le PIB nominal | 2,144 | 1,393 | 1,452 |
| La masse salariale | 2,210 | **1,436** | 1,497 |

(à côté, sur les séries du modèle)

*La masse des pensions.* Pour passer d'une pension à la masse, chaque âge
de 2025, à partir de 62 ans, est pris pour une génération de retraités
liquidée à 62 ans, et pesé par son effectif INSEE ; les générations
liquidées avant 2000 sont suivies depuis 2000. Sous chaque règle, la masse
de 2025, face au droit, serait :
- **la masse salariale** : +18 %, soit environ 78 Md€ de la dépense
  vieillesse-survie de 2024 (426,7 Md€) ;
- **le salaire moyen** : +9 %, soit environ 37 Md€ ;
- **l'Allemagne** (α = 0,25) : +6 %, soit environ 27 Md€ ;
- **la Pologne** : +4 %, soit environ 17 Md€ ;
- **les prix** : +2 %, soit environ 9 Md€ ;
- **les prix × le facteur allemand** : +1 %, soit environ 5 Md€ ;
- **les prix × le facteur entier** : −1 %, soit environ −4 Md€ ;
- **la Suède** : −10 %, soit environ −41 Md€.

C'est un ordre de grandeur. Il suppose que toutes les pensions suivent les
coefficients de la Cnav, et que toutes les générations ont la même pension
(à côté).

*Trois choses à retenir de ce tableau.*
- **Le droit est la règle allemande sans le dire.** Les prix corrigés du
  facteur démographique allemand, à partir de 2005, auraient servi de 2000 à
  2026, à 0,6 % près,
  ce que les gels et les sous-indexations ont servi. Le rapport des
  retraités à l'emploi est passé de 0,494 en 2004 à 0,565 en 2024 (DREES).
  Le quart de cette hausse, retranché des prix, fait à peu près ce que les
  lois votées de 2013 à 2019 ont décidé une à une : le gel de 2014-2015, le
  report de 2018, les 0,3 % de 2019, les tranches de 2020.
- **La règle suédoise, transposée telle quelle, appauvrirait les retraités
  français.** Le 1,6 % suédois escompte une croissance réelle du revenu
  moyen que la France n'a pas eue : 0,73 % par an de 2000 à 2025, et 0,69 %
  projeté par le COR (modèle). Transposée, la norme serait de 0,7 %, pas de
  1,6 %.
- **La masse salariale a été exceptionnelle.** Elle a crû de 1,42 % par an
  au-dessus des prix de 2000 à 2025, parce que l'emploi salarié a crû. Le
  COR n'en attend plus que 0,55 % sur 2026-2070 (modèle), l'emploi
  plafonnant puis baissant après 2040.

*Le cas de 2022 à 2024*, année par année, en % : la colonne Cnav porte ce
qui a été servi dans l'année, et les autres le taux de l'année écoulée,
appliqué au 1er janvier.

| Au 1er janvier de | Cnav | Prix | Masse salariale | Prix × facteur α = 0,25 | Allemagne α = 0,25 | Pologne |
|---|---|---|---|---|---|---|
| 2022 | 1,10 | 1,64 | 7,87 | 2,10 | 2,86 | 2,35 |
| 2023 (dont +4,0 en juillet 2022) | 4,83 | 5,22 | 7,84 | 5,54 | 2,95 | 5,29 |
| 2024 | **5,30** | 4,88 | 5,62 | 4,84 | 4,63 | 4,88 |
| 2025 | 2,20 | 2,00 | 3,12 | 2,02 | 2,66 | 2,13 |
| 2026 | 0,90 | 0,94 | 1,59 | 0,78 | 1,60 | 1,11 |

(à côté ; la Cnav, publié)

Les 5,3 % du 1er janvier 2024 sont vérifiés : ce sont ceux de la circulaire
Cnav 2023/34 du 29 décembre 2023, que le dépôt porte. Aucune règle étudiée
n'aurait fait baisser les pensions cette année-là ; seule la suédoise aurait
servi nettement moins, 3,0 %, par sa division par 1,016. Pendant ces années, l'emploi a crû plus vite que le nombre de
retraités : le facteur démographique aurait même relevé les pensions au
1er janvier 2023. La
pique du 6 novembre, deux ans de plus aux actifs pendant que les pensions
prennent 5,3 %, est exacte. Mais une indexation n'y aurait rien changé :
seule une règle qui lie l'âge des actifs aux pensions l'aurait fait (plus
bas). La réforme de 2023 a d'ailleurs été suspendue en partie : l'âge de
64 ans ne vaut plus qu'à partir de la génération 1969, et la génération 1964
part à 62 ans et 9 mois (loi n° 2025-1403, art. 105,
[age_ouverture_avant_suspension.csv](../../../data/reference/legislation/age_ouverture_avant_suspension.csv)).

## Et d'ici 2070, sous le scénario de référence du COR

Une pension liquidée le 1er janvier 2026, en euros constants, sous chaque
règle :

| Règle | +10 ans | +20 ans | +25 ans | +30 ans |
|---|---|---|---|---|
| Les prix | 1,000 | 1,000 | 1,000 | 1,000 |
| La masse salariale | 1,111 | 1,196 | 1,218 | 1,236 |
| Le salaire moyen par tête | 1,071 | 1,147 | 1,187 | 1,228 |
| L'Allemagne (α = 0,25) | 1,060 | 1,108 | 1,134 | 1,162 |
| La Lettonie (50 %) | 1,053 | 1,092 | 1,102 | 1,110 |
| La Pologne (20 %) | 1,014 | 1,027 | 1,034 | 1,041 |
| L'Allemagne (α = 1) | 1,026 | 0,999 | 0,987 | 0,984 |
| La masse salariale par retraité | 0,989 | 0,975 | 0,957 | 0,939 |
| Les prix × facteur α = 0,25 | 0,990 | 0,966 | 0,955 | 0,946 |
| Les prix × facteur α = 1 | 0,958 | 0,871 | 0,832 | 0,801 |
| La Suède (÷ 1,016) | 0,914 | 0,835 | 0,798 | 0,763 |

(à côté, sur les séries du modèle ; le rapport retraités/cotisants de la
Cnav, projeté par le COR, passe de 0,666 en 2025 à 0,728 en 2040, 0,799 en
2050 et 0,893 en 2070, soit +34 %)

Sous la masse salariale, une pension gagne 22 % de pouvoir d'achat en
vingt-cinq ans. Sous un facteur démographique entier, elle en perd 5 à 17 %,
selon qu'il corrige le salaire ou les prix. Les autres règles sont entre les
deux.

## Le partage de l'effort : qui porte quel risque

Une règle de pension servie se juge à ce qu'elle fait porter aux retraités,
et à ce qu'elle laisse aux cotisants, ou au budget quand le taux de
cotisation est fixe, comme les 18 % de la proposition :

| Ce qui arrive | Les prix (droit, Italie) | La masse salariale (le modèle) | Le revenu moyen ÷ 1,016, avec frein (Suède) | Un facteur démographique (Allemagne) | La masse salariale par retraité |
|---|---|---|---|---|---|
| La croissance des salaires faiblit | cotisants | retraités | retraités | retraités | retraités |
| L'emploi baisse (IA, chômage) | cotisants | **retraités** | cotisants, puis retraités par le frein | retraités en partie, par α | retraités |
| Le nombre de retraités par cotisant monte | cotisants | cotisants | retraités, par le frein | **retraités, pour α** | retraités, en entier |
| L'espérance de vie monte | le diviseur des nouveaux retraités, sous toutes les règles | | | | |

(à côté)

Le compte notionnel met déjà la longévité à la charge de chaque génération
qui part, par son diviseur. Il reste la croissance, l'emploi et le nombre de
retraités par cotisant. **Sous les prix, les cotisants portent tout** : c'est
le diagnostic du 6 novembre, « on a toujours fait payer davantage les
cotisants ».
**Sous la masse salariale, les retraités partagent la croissance et
l'emploi, mais pas la démographie.** Les grosses générations qui partent
pèsent sur les cotisants, ou sur le budget à taux fixe. Il faut un frein ou
un facteur pour que les retraités en portent une part.

*L'IA.* Supposons que l'emploi baisse de 1 % par an de 2030 à 2040,
productivité inchangée. Sous la masse salariale, une pension perd alors
9,6 % face au scénario du COR : en euros constants, elle vaut ×1,002 en
2040, contre ×1,108 sans la baisse (à côté). Sous les prix, elle ne perd
rien, et les 10 % de cotisations manquantes vont au déficit. La piste du
6 novembre tient donc : sous cette règle, les retraités partagent une baisse
de l'emploi, et la garantie vieillesse, qui suit les prix, protège les plus
pauvres. La couverture du risque, elle, n'est pas dans la règle : elle est
dans les recettes hors du travail (chantier 4) et dans le pilier capitalisé,
qui détient le capital.

## La règle du propriétaire, calculée : l'âge des actifs recule, les pensions baissent

La décision 11 garde la règle et demande de revoir son calcul. Il y a deux
façons de l'écrire.

**L'effort égal, mesure par mesure.** La réforme de 2023 devait rapporter
17,7 Md€ en 2030 ([risque_de_defaut.md](../../risque_de_defaut.md), d'après
l'étude d'impact, non relu ici). C'est **3,7 % de la dépense de retraite de
2030** : 14,07 % d'un PIB de 3 428 Md€, soit 482 Md€ (modèle). Un an d'âge
retire d'ailleurs à qui part environ un an de pension sur les 23,6 que le
diviseur escompte à 64 ans, soit **4,2 % de son patrimoine retraite**
(modèle). Les deux chiffres disent la même chose : chaque année d'âge
demandée aux actifs vaut un effort d'environ 4 % sur les pensions servies.
C'est démontrable et simple à dire, mais discrétionnaire : il faut une loi à
chaque fois, et rien n'oblige la suivante à le refaire.

**L'effort automatique : le facteur démographique.** La règle allemande
traduit l'idée sans loi nouvelle. Quand le nombre de retraités par cotisant
monte, la pension perd une fraction α de cette hausse, et les cotisants
portent le reste : α = 0 est le droit écrit, α = 0,25 l'Allemagne, α = 1 un
partage entier. Le facteur est mesurable et publié, et il joue dans les deux
sens. Il aurait relevé les pensions aux 1ers janvier 2022 et 2023, quand l'emploi
croissait plus vite que le nombre de retraités. Un âge des actifs qui recule fait d'ailleurs
baisser le rapport, et monter les pensions : le facteur ne lie pas l'âge aux
pensions, il lie leur cause commune, la démographie, aux deux.

**Dans la proposition, le choix de α change de nature.** Le taux de
cotisation y est fixé à 18 %, et l'âge à 65 ans. L'effort démographique que
les retraités ne portent pas ne va donc plus aux actifs par leur taux ou
leur âge : il va au budget. α = 1, la masse salariale par retraité, rend la
répartition à 18 % autonome. Au-dessous, la part 1 − α est un financement
public, payé par l'impôt, et donc par les retraités aussi, par la TVA. C'est
la question que le chantier 1 pose sous un autre nom.

## « Garantit la retraite » : ce que les pays promettent

- La **Suède** ne promet pas de montant, et le dit : « the value of the
  pension is not guaranteed but may vary » ; c'est le taux de cotisation de
  16 % qui est fixe ([Orange Report 2020](https://www.pensionsmyndigheten.se/statistik/publikationer/orange-report-2020/orange-report-2020.pdf)).
- L'**Allemagne** promet que la pension ne baisse jamais (« Rentengarantie »,
  § 68a), et un niveau de 48 % jusqu'en 2031, payé par le budget fédéral.
- L'**Italie**, la **Lettonie** et la **Pologne** promettent une règle et
  l'absence de baisse en euros. La Lettonie promet aussi une pension minimale
  payée par le budget. En Pologne, le Tribunal constitutionnel protège la
  valeur réelle des pensions.

Trois promesses tiennent dans un compte notionnel, et les trois sont
démontrables :
1. **chaque euro cotisé est inscrit à votre nom, et rapporte ce que rapporte
   l'ensemble des salaires** ;
2. **la même règle vaut pour tous** : aucun régime, aucun statut n'a la
   sienne ;
3. **personne ne descend sous le plancher** : 800 € par mois, suivant les
   prix et payés par l'impôt.

Une quatrième se donne à peu de frais : **votre pension ne baisse jamais en
euros**. C'est la clause de quatre pays sur cinq, avec le rattrapage
allemand sur les hausses suivantes, qui la rend neutre sur la durée. Sous la
masse salariale, elle n'aurait joué en France qu'une fois depuis 2000, en
2021, après la baisse de 4 % de 2020. Mais elle ne vaut qu'après la
transition : les décisions 2 et 3 font baisser les pensions d'aujourd'hui en
cinq ans au plus, et la phrase doit le dire.

Ce qui ne se promet pas : un montant, ou un taux de remplacement. La Suède
dit pourquoi, et l'Allemagne montre ce que coûte la promesse.

## Ce que la note tient pour fragile

- **Le calcul est fait sur la pension de base de la Cnav.** La
  complémentaire, la fonction publique et les régimes spéciaux ont leurs
  propres revalorisations. La masse est donc un ordre de grandeur : elle
  pèse chaque âge par son effectif, non par sa pension, et compte tout
  habitant de 62 ans et plus pour un retraité.
- **Les règles étrangères sont approchées sur des séries françaises.** Le
  salaire moyen par tête remplace le revenu moyen suédois. Le rapport
  retraités/emploi de la DREES remplace le Rentnerquotient allemand, compté
  en équivalents. Le facteur de cotisation allemand, la Haltelinie, les
  tranches italiennes et le plafond letton sont omis.
- **Le calendrier est simplifié.** Le taux de l'année s'applique au
  1er janvier suivant ; l'Allemagne revalorise en juillet, la Pologne en
  mars, la Lettonie en octobre.
- **Le facteur démographique ne joue qu'à partir de 2005**, faute de série
  des retraités avant 2004 dans le dépôt. Au-delà de 2024, il suit le
  rapport de la Cnav projeté par le COR, et non celui de tous les régimes.
- **La projection est celle du scénario de référence du COR**, avec une
  croissance réelle du salaire moyen de 0,7 % par an. Sous une autre
  hypothèse, l'écart entre les règles change d'échelle, pas d'ordre.
- **Les 17,7 Md€ de la réforme de 2023** sont repris de
  `docs/risque_de_defaut.md`, sans relecture de l'étude d'impact.
- **Ce qui n'a pas été lu à sa source** : les motifs de l'arrêt italien
  n° 70/2015 ; les taux italiens de 2000 à 2007, de 2023 et de 2024 ; les
  indices lettons et polonais d'avant 2009 à 2014 ; la loi de finances
  suédoise pour 2011 ; la référence au Bundesgesetzblatt du Rentenpaket
  2025.

## Les pistes, pour le propriétaire

1. **Les comptes : la masse salariale, confirmée.** C'est la règle de la
   Pologne et de la Lettonie, celle que la théorie désigne, et le défaut du
   modèle. Une retouche serait à envisager : un plancher à zéro, rattrapé
   ensuite, comme en Italie, en Lettonie et en Pologne, pour qu'un compte ne
   baisse jamais en euros.
2. **Les pensions servies des nouveaux retraités : la masse salariale, avec
   le diviseur à l'espérance de vie, comme le modèle le fait déjà.** Elle
   partage la croissance et l'emploi, ce que voulait la décision 10, et le
   profil plat des prix ne garde aucun avantage dès que le diviseur est
   juste. Il y faut ajouter **un frein démographique** : retrancher une
   fraction α de la croissance du nombre de retraités, puisque l'emploi est
   déjà dans la masse salariale ; à α = 1, c'est la masse salariale par
   retraité. Sans lui, la répartition à 18 % ne
   s'équilibre pas quand les grosses générations partent, et le budget paie
   la différence.
3. **Les pensions d'aujourd'hui, après leur baisse de transition : les prix
   corrigés du même facteur.** C'est, à 0,6 % près de 2000 à 2026, ce que la
   France a servi par ses lois au coup par coup. Écrire la règle à leur place
   change le fond moins que le message : l'effort devient automatique et
   annoncé, au lieu d'être voté par surprise.
4. **Le paramètre α, au propriétaire.** α = 0,25 est l'Allemagne, et le
   passé français. α = 0,5 serait le partage moitié-moitié que la décision 11
   suggère. α = 1 rend la répartition autonome. D'ici 2070, sous le COR, une
   pension indexée sur les prix y perdrait 5, 10 ou 17 % en vingt-cinq ans.
5. **La garantie** : les trois promesses, plus « votre pension ne baisse
   jamais en euros », dite valable après la transition.

Le modèle n'a pas encore ce facteur. Il faudrait une session du modèle pour
l'écrire en paramètre (α, et la série des retraités par cotisant), pour la
pension servie et pour le stock du scénario 6, le seul où s'appliquent les
règles du programme (décision 28), puis la page Coût en chiffrerait chaque
valeur. Cela vient après les décisions du propriétaire, comme le veut la
feuille de route du programme.
