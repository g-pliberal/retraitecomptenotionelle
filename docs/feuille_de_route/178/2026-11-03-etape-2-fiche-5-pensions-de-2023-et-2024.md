# Étape 2, la fiche 5 : la pension moyenne brute et nette de 2023 et 2024, et le taux effectif de la page Coût

**La demande.** Vague 5 du 3 novembre 2026 : le propriétaire a dit oui à la
question de l'étape 2 — porter à `pensions_brutes_nettes.csv` les montants de
2023 et 2024 de la fiche 5 du panorama de la DREES, édition 2026, et ajouter à
`scripts/verifier_donnees.py` une source d'appoint, comme celle de l'âge
conjoncturel. Exigence : chaque valeur lue à sa cellule, pendant la session.

**La source, ouverte.** L'archive `drees_panorama_retraites_2026_classeurs.zip`,
téléchargée de son miroir (release `documents-apportes`), a l'empreinte du
manifeste, `ec7503f8…aaf64911` ; son membre `fiche_05.xlsx`, celle de son
champ `contenu`, `e7cdfaf8…babf0af2`. Feuille « F05_Tableau 1 compl_bis »,
titre (B2) : « Tableau 1 complémentaire bis. Montant mensuel moyen de la
pension des retraités résidant en France ou à l'étranger » ; champ (B31) :
« Retraités ayant perçu un droit direct au cours de l'année n, résidant en
France ou à l'étranger, vivants au 31 décembre de l'année » ; sources :
« Drees, EIR, modèle ANCETRE ». Les cases sont des entiers, sans formule, au
format `#,##0`. Colonnes de l'ensemble : I, droit direct majoration comprise,
brute ; L, sa nette ; O, pension totale (droit direct, droit dérivé et
majoration), brute ; R, sa nette. Ligne 27, 2023 ; ligne 28, 2024.

| | brute directe | nette directe | brute totale | nette totale |
|---|---|---|---|---|
| 2023 | 1 608 (I27) | 1 495 (L27) | 1 764 (O27) | 1 643 (R27) |
| 2024 | 1 693 (I28) | 1 573 (L28) | 1 855 (O28) | 1 727 (R28) |

En euros courants par mois. Les soixante valeurs de 2008 à 2022 (lignes 12 à
26, mêmes colonnes) sont, à l'euro près, toutes celles que le fichier certifie
du tableau 2.1-a ; lues deux fois, par `openpyxl` et par le lecteur du dépôt
(`lecture_xlsx`), sans écart.

**Le champ, et pourquoi celui-là.** Le tableau 1 imprimé (folio 55, page 56
du fichier PDF, ouvert ici à l'empreinte du manifeste, `9eb36a06…735e9be` ; feuille
« F05_Tableau 1 » du classeur) ne compte que les résidents en France : 1 752 €
bruts et 1 626 € nets de droit direct fin 2024 (F27, G27), 1 920 € et 1 785 €
toutes pensions (J27, K27), les mêmes au PDF. Le fichier porte, depuis le 24 octobre, les
retraités résidant en France ou à l'étranger : c'est le champ du tableau 2.1-a
qu'il certifie, et le tableau 1 aurait cassé la série en 2023. Hypothèse, non
prouvée ici : la dépense à laquelle le modèle applique le taux compte aussi les
pensions servies à l'étranger, qui ne paient pas la CSG ; aucune source du
dépôt ne le dit (l'en-tête de `pensions_droits.csv` est muet), et le choix du
champ n'en dépend pas.

**Ce qui est fait**, test d'abord, chaque test vu rouge pour la raison
attendue avant le code.

1. *Le récupérateur* (`scripts/fetch/drees_panorama_classeurs.py`,
   `lire_pensions_moyennes`) lit la feuille par ses en-têtes et dépose la
   série `pensions_moyennes`, de 2004 à 2024, dans
   `data/brut/drees_panorama_2026.json` ; le titre « … résidant en France ou à
   l'étranger » est exigé, et celui du tableau des seuls résidents arrête la
   lecture. Test : la feuille réduite à cinquante-deux cases, chacune
   confrontée au classeur.
2. *La source d'appoint* (`source_pensions_brutes_nettes_panorama`,
   certification `pensions_brutes_nettes_panorama`) ne donne que les années
   qui suivent la dernière du tableau 2.1-a, 2022 quand il n'est pas là ; le
   portail de la DREES a coupé la connexion (comme le 24 octobre), le tableau
   n'a donc pas été relu. Les huit valeurs, ajoutées au niveau `certifiee` par
   `verifier_donnees.py --appliquer`, et le journal, qui ne gagne que leur
   trace.
3. *Le modèle* : `DepensesRetraite` les lit sans changement de code ; le taux
   de chaque année est celui de son année publiée, désormais jusqu'en 2024, et
   la projection tient celui de 2024. Le paquet, refait.

**Le taux effectif, posé à la main** (un moins la nette sur la brute, toutes
pensions comprises) :

* 2022 : (1 719 − 1 602) / 1 719 = 117 / 1 719 = 6,806 % ;
* 2023 : (1 764 − 1 643) / 1 764 = 121 / 1 764 = 6,859 % ;
* 2024 : (1 855 − 1 727) / 1 855 = 128 / 1 855 = 6,900 %.

Il monte de 0,094 point de 2022 à 2024, de 6,8 % à 6,9 % à l'arrondi du
dixième. De droit direct seul, il irait de 6,90 % à 7,09 % ; le modèle prend
la pension totale.

**Ce que la page Coût affiche, avant et après.** Aucune ligne de
`pages.js` ni de `cout.py` ne change : la page lit le taux que le bilan figé
porte, et le modèle, la dernière année du fichier. Le paragraphe « Et en
BRUT, des deux côtés » disait « Ces prélèvements en prennent 6,8 % […] : ce
que la DREES mesure en 2022, dernière année publiée […]. La masse nette […]
vaut donc 12,75 % du PIB en 2024, 374 Md €, contre 13,68 % en brut,
401 Md € » ; il dit « 6,9 % […] : ce que la DREES mesure en 2024 […] 12,73 %
du PIB en 2024, 374 Md € », le brut inchangé. À la main : la masse de 2024,
401 426 M€ sur un PIB de 2 935 236 M€, 13,676 % ; nette, 401 426 × (1 −
128 / 1 855) = 373 727 M€, 12,732 % du PIB (avant : 374 104 M€, 12,745 %). La
ligne « Pour mémoire, dépenses nettes des prélèvements sociaux des retraités »
du bilan de 2026 passe de 393,8 Md €, 13,16 % du PIB et 93,2 % des dépenses à
393,4 Md €, 13,15 % et 93,1 % pour le système actuel, de 247,6 Md €, 8,28 % et
93,2 % à 247,4 Md €, 8,27 % et 93,1 % pour la proposition. La dépense brute,
le solde et la dette ne bougent pas ; ni aucun témoin de simulation. La page
Méthode compte une série certifiée de plus.

**Ce que la source ne tranche pas.** La note du 14 octobre (action 138,
étape 3, « Une réserve sur 2023 ») tenait le taux de 2022 « sans doute bas
d'un demi-point » : la borne par les têtes d'Ancetre sautait de 5,4 % à 6,1 %
en 2023 (22,3 % d'exonérés de droit direct contre 30,3 %), et la CSG des
retraites de la CCSS, 23,7 Md€ en 2023, faisait 6,3 % des masses de la DREES,
« à quoi la CRDS, la CASA et la cotisation maladie ajoutent près d'un point ».
La DREES mesure 6,86 % en 2023, +0,05 point : selon sa mesure, le demi-point
n'y est pas. Mais les chiffres de la CCSS, tels que la note les cite, mènent
vers 7,3 % environ : reste un écart d'environ 0,4 point que la mesure de la
DREES n'explique pas. Le panorama ne dit pas pourquoi le compte de la CCSS et
le sien diffèrent, ni d'où vient la
baisse des exonérés d'Ancetre 2023 : ces deux points restent ouverts, et ces
chiffres de la CCSS et d'Ancetre n'ont pas été relus ici, seulement cités de
la note. La feuille dit aussi (B31) : « Après correction d'une erreur dans
les taux de prélèvements appliqués, la pension nette a été révisée pour les
années 2020 à 2022 par rapport à l'édition précédente de cet ouvrage. » Les
nets du fichier pour ces années, venus du tableau 2.1-a, sont ceux de
l'édition 2026 à l'euro près : les révisés.

**Les tests** : `test_drees_panorama_2024.py` (le lecteur, les huit valeurs à
leur cellule, le relais des sources), `test_depense_nette.py` (le fichier, le
taux de 2023 et 2024 posé à la main, la projection au taux de 2024),
`test_cout.py` et `test_agregats.py` (le bilan et sa table, 2024 et 128 /
1 855), `test_web.py` (la ligne du bilan de la bascule et la masse nette des
sources, au taux de 2024), `test_donnees.py` (le journal).
