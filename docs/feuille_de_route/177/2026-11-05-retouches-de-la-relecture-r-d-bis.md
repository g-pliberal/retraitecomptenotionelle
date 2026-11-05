# Retouches de la relecture R-D-bis : deux empreintes, un chiffre qui ne vaut que pour le droit en vigueur, le plafond de la caisse et la cotisation minimale déclarés

File « Retouches 2 », le 5 novembre 2026 : ce que la relecture R-D-bis
(`2026-11-05-relecture-de-d-bis.md`, sur les commits 43cfa28, 5940f86, 18af62f et ca2cb5f)
relève, en quatre écarts faibles. Les index LEGI (à jour au 4 novembre 2026) et JORF (au 5
novembre) de la DILA ont été récupérés dans la session ; chaque texte cité a été rouvert, et
chaque citation écrite dans la fiche confrontée à l'index, espaces ramenées. **Aucune valeur du
modèle ne change** : ni règle, ni donnée, ni test, ni témoin.

## 1. Les deux empreintes de la note `2026-11-05-corrections-de-la-relecture-r-d.md` (écart b)

La note dit que ses cinq écarts sont fermés « en deux commits : 337c5d9 (le plafond) et bc608e4
(la présomption de 2012 à 2018) ». Ces deux empreintes n'existent pas sur `main`
(`git cat-file -t` : « Not a valid object name ») : le rebasage de la session les a récrites. Les
commits qui portent ces deux changements sont :

| Empreinte citée (récrite) | Empreinte sur `main` | Titre |
|---|---|---|
| 337c5d9 | **43cfa28** | Action 177, D-bis : l'indépendant de Mayotte cotise sous le plafond de sa caisse |
| bc608e4 | **5940f86** | Action 177, D-bis : de 2012 à 2018, l'indépendant de Mayotte présumé à la somme des parts de l'article 4 |

La correspondance est celle des titres, vérifiée dans `git log` ; la note citait aussi, à
« commit 337c5d9 » (le plafond, § 1 et l'exemple à 30 000 € × 15,45 %) et « commit bc608e4 » (la
présomption, § 2), les mêmes deux commits. Les deux autres commits de la file sont 18af62f (la
note, le journal de veille, le bloc « Reprise ») et ca2cb5f (le paquet refait sur le dernier
`main`). La note, qui est un récit, n'est pas récrite : elle porte, à sa fin, un renvoi daté vers
celle-ci.

## 2. Le chiffre « 19 353,01 € de 2019 à 2026 au lieu de 29 034,54 € » (écart c)

La note dit : « Le compte du témoin né en 1965 reçoit 16 911,01 € de 2012 à 2018 au lieu de
44 903,58 €, et 19 353,01 € de 2019 à 2026 au lieu de 29 034,54 € ». **Le second chiffre ne vaut
que pour le droit en vigueur** (le compte de `cotisation_annuelle`, le scénario 1) : il y compte
2026 à 3 898,38 € (36 264 × 10,75 %, refait ici : 3 898,38 €). Aux scénarios 2 et 4, 2026 est
au régime unique : le compte du témoin né en 1965 y reçoit, de 2019 à 2025, 15 454,63 € au lieu
de 23 868,09 €, et en 2026 12 514,18 € avant comme après (relecture R-D-bis, § 5). La somme est
cohérente : 19 353,01 − 3 898,38 = 15 454,63. La relecture R-D le disait de même (écart faible c
de R-D-bis). Les chiffres de 2012 à 2018 valent partout : le régime unique ne commence qu'en 2026.
Aucune valeur du modèle n'en dépend : la note donne un chiffre, et il fallait dire son périmètre.

## 3. Ce que la fiche déclare désormais (écarts a et d)

Fiche `data/reference/regles/cotisation_vieillesse_independants_mayotte.yaml`, deux
approximations neuves, une ligne `a_relire` neuve, et la citation du II de l'article 28-2.

**a) L'arrêté du plafond de la caisse, ni lu ni trouvé.** L'article 28-1, I, de l'ordonnance
n° 96-1122 dit : « Son montant, calculé selon des règles prévues par décret, est arrêté par le
ministre chargé de la sécurité sociale. » Recherche au JORF (arrêtés de 2011 à 2026, 14
documents pour « plafond Mayotte cotisations sécurité sociale », tous listés : conventions
nationales et leurs avenants, agrément d'un accord d'assurance chômage, chartes du cotisant
contrôlé, nomenclatures de pièces justificatives) : aucun arrêté ne fixe un plafond de Mayotte.
Une seconde recherche, `Mayotte "plafond de la securite sociale" OR "plafond de cotisations"` en
arrêtés, ne rend que trois documents, listés eux aussi (le plafond de dépenses des chambres de
métiers, l'agrément d'une convention de chômage, le règlement du régime des artistes auteurs) :
aucun non plus. Le plafond que le modèle sert (13 860 € en 2012,
36 264 € en 2026) est donc le barème « Salaire plafond - Mayotte » de la Cnav
(`mayotte_smig_et_plafond.csv`), qui transcrit le texte sans le citer. Deux décrets disent une
règle de calcul, que j'ai relue dans la base de l'index : décret n° 2003-589, article 21
(LEGIARTI000026514398, depuis le 21 octobre 2012), et décret n° 2015-1679, article 1er
(LEGIARTI000031634572) : « fixé à 1 070 euros par mois pour les rémunérations ou gains versés à
compter du 1er janvier 2011. Ce montant est revalorisé chaque année conformément au taux
d'évolution du plafond en vigueur en métropole au 1er janvier de chaque année, majoré de cinq
points et un dixième » (« 5 points et un dixième » au second). **Observation neuve : ils ne
nomment pas le plafond de l'article 28-1.** Le premier vise « Le plafond mentionné au II de
l'article 19 de l'ordonnance du 27 mars 2002 », le second « Le plafond mentionné au I de
l'article 28-6 de l'ordonnance du 20 décembre 1996 ». La fiche le dit : ce que le texte ne
tranche pas, que ce soit le même.

**Le recalcul, refait ici** (les plafonds annuels de `plafond_securite_sociale.csv` divisés par
douze, chaque année partie du montant mensuel de la Cnav de l'année d'avant, évolution du plafond
national plus 0,051) : 1 155,44 € en 2012 pour 1 155 au barème, 1 234,86 pour 1 235, 1 315,19
pour 1 316, 1 400,36 pour 1 400, 1 492,60 pour 1 492, 1 591,74 pour 1 592, 1 693,65 pour 1 694,
1 814,16 pour 1 814, 1 933,91 pour 1 934, 2 032,63 pour 2 033, 2 136,68 pour 2 137, 2 394,36 pour
2 394, **2 645,39 pour 2 644 en 2024**, 2 820,58 pour 2 821, 3 022,37 pour 3 022. Les mêmes
chiffres que R-D-bis : moins d'un euro par mois d'écart, sauf 2024 (1,39 €, soit 16,68 €
d'assiette par an, 1,56 € de cotisation à 9,35 %). Les arrêtés, qui diraient l'arrondi, ne sont
pas lus.

**d) La cotisation forfaitaire minimale de l'article 28-2, II, de 2012 à 2018, non portée.**
Ordonnance n° 96-1122, article 28-2, II, rédaction du 1er janvier 2012 (LEGIARTI000025018560) :
« Lorsque l'application des dispositions qui précèdent conduit à un montant de cotisations
inférieur à un montant minimum fixé par décret, l'assuré est soumis au versement d'une cotisation
forfaitaire minimale égale à ce même montant. » La même phrase figure dans la rédaction du 1er
décembre 2024 (LEGIARTI000046455192). Trois recherches dans l'index LEGI, dans les textes dont le
titre nomme Mayotte (« montant minimum », « cotisation forfaitaire minimale », « cotisation
minimale »), ne rendent que des articles d'ordonnance (28-2 de l'ordonnance n° 96-1122, 23-3 de
l'ordonnance n° 2002-411, qui y soumet les conjoints collaborateurs) : **aucun décret ne fixe ce
montant à l'index**. L'article 4-2, du décret n° 2011-2085, fixe depuis 2019 une autre garantie,
lue : « Elle ne peut être calculée sur une assiette inférieure à 450 fois le salaire horaire
minimum interprofessionnel de croissance applicable à Mayotte » (LEGIARTI000038680068). Le modèle
cotise le taux du revenu, sans plancher, de 2012 à 2018 : l'effet touche les petits revenus
seuls, et n'est pas mesuré.

## 4. Ce qui n'a pas bougé

Les deux moteurs, les données, `cssm_mayotte.yaml`, les témoins. Le paquet lit la fiche : voir la
construction après l'envoi (message de commit).

## À reprendre

- Lire l'arrêté du plafond de chaque année, et le décret du montant minimum de l'article 28-2, II
  (une publication locale, une circulaire de la caisse de sécurité sociale de Mayotte) : la fiche
  l'écrit en `a_relire`.
- Au propriétaire, si l'on veut le plancher de 2012 à 2018 : il faut d'abord le montant.

Sources : LEGI LEGIARTI000025018554, 031324363 (ordonnance n° 96-1122, article 28-1, I) ;
LEGIARTI000025018560, 046455192 (article 28-2) ; LEGIARTI000026514398 (décret n° 2003-589,
article 21) ; LEGIARTI000031634572 (décret n° 2015-1679, article 1er) ; LEGIARTI000038680068
(décret n° 2011-2085, article 4-2) ; LEGIARTI000025021008 (ordonnance n° 2002-411, article 23-3).
JORF : les recherches ci-dessus, sans autre résultat ; l'historique `git log` des empreintes
337c5d9, bc608e4 (inconnues), 43cfa28, 5940f86, 18af62f, ca2cb5f.
