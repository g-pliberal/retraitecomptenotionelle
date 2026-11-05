# Relecture de E4 et des chiffres neufs de E3-bis

File R-E5 de la vague 10, le 5 novembre 2026 : relecture indépendante, contre les sources, du
commit c7fbb26 de la session E4 (la CAVP lue au droit : `cavp_minoration_deux_pentes`, notes de
`cavp_complementaire.yaml`, inventaire, `docs/regimes.md`, paquet ; note
`2026-11-05-carte-des-fiches-cavp-lue-au-droit.md`) et des deux montants neufs du commit b1f28db
de la session E3-bis (`carpimko_ages_2015` ; note `2026-11-05-e3-bis-corrections-de-r-e4.md`).
Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour (`dila_index.py --recuperer`,
`--mettre-a-jour` : JORF et LEGI à jour au 5 novembre 2026), lus par `dila_cherche.py --texte`,
`--num`, `--le`, et, pour la liste des textes, par des requêtes directes sur la base de
l'index, sans borne. Chaque citation des deux fiches découpée à ses « [...] », guillemets ôtés
et espaces ramenées, cherchée par un script dans le texte qu'elle nomme (JORF ou LEGI). Chaque
cas des deux notes rejoué par `servi_et_refait` (`tests/outils_pont.py`), le portage servi et
le moteur Python refait au bit près, sur la requête du formulaire (deux salaires moyens,
naissance le 10 du mois, l'âge d'entrée dit), puis de nouveau sous `PRESOMPTIONS_DECALEES=1`.
Chaque montant refait à la main à partir des valeurs servies, à quatre décimales.

## Le verdict

- **E4 : conforme pour l'essentiel.** La liste des textes est complète, les citations et les
  dates exactes, les cinq versions fidèles au texte, chaque montant exact dans les deux
  moteurs, les deux erreurs déclarées prouvées, les deux non-tranchés fondés, le paquet à jour.
  Un écart **moyen** : la majoration des nés jusqu'au 30 juin 1951 de 2011 à 2026, où
  l'article 12 et le tableau des statuts de 2011 se contredisent, sans que la fiche le dise.
  Deux écarts **faibles** sur la liste des textes d'avant 2009.
- **E3-bis : les deux montants sont exacts**, et l'erreur de la majoration avant l'âge légal
  de la base est prouvée. Un écart **moyen** : le non-tranché de « l'âge du taux plein »
  ignore que, depuis le 10 janvier 2024, la table des statuts puis du règlement nomme sa ligne
  « Âge du taux plein ». Un écart **faible** : les 136,90 € sont un minimum.

## A. E4, la CAVP

### La liste des textes : complète

La base de l'index JORF, interrogée sans limite : « pharmaciens » au titre (toutes années), et
au corps « section professionnelle des pharmaciens », « CAVP », « vieillesse des pharmaciens »,
« caisse d'assurance vieillesse des pharmaciens » ; 1 103 documents, triés à la main. Depuis
2007, les arrêtés qui approuvent des statuts ou un règlement de la section sont exactement les
treize de la note : 27 mars 2007, 11 mai 2009, 23 juin 2011, 24 septembre 2012, 4 juin 2015,
30 novembre 2016, 5 juillet 2017, 3 octobre 2019, 19 juin 2023, 19 décembre 2023, 5 mai 2025,
10 juillet 2026, 21 septembre 2026 (JORFTEXT000054888282). Aucun n'est manqué. Les décrets de la
même période qui modifient le décret n° 49-580 (n° 2008-1499, 2014-1446, 2019-288, 2026-418,
article 4) ne touchent que les cotisations, les classes, la capitalisation et le renvoi au
règlement ; aucun ne dit l'âge, la minoration ou l'entrée en jouissance (lu au corps du
2026-418 : « âge » n'y vise que les versements et les rachats en capitalisation).

### Les citations et les dates : conformes

Les dix citations de la fiche se retrouvent mot pour mot ; celle du décret n° 2026-418 joint,
comme elle le dit, l'article 30, qui est un autre document (JORFARTI000054153813, « Le présent
décret entre en vigueur le 1 er juillet 2026. »). L'article 2 de l'arrêté du 11 mai 2009 abroge
bien les arrêtés du 29 décembre 1948 et du 1er juin 1950 (JORFARTI000020694602). Aucun des
quatre arrêtés qui font une version (2009, 2011, 19 décembre 2023, 10 juillet 2026) ni leur
annexe ne fixe de date d'entrée en vigueur (« vigueur », « à compter », « prennent effet »
cherchés) : le lendemain de la publication, 7 juin 2009, 30 juin 2011, 10 janvier 2024,
18 juillet 2026, est juste. L'index LEGI n'a toujours, de l'article 4 du décret n° 49-580, que
la rédaction du 1er janvier 2009 (LEGIARTI000020081472, sans fin) : conforme à la fiche.
`textes.py --non-lues cavp_minoration_deux_pentes` : aucune rédaction non lue.

### Les versions, au texte : conformes

- **2009** (JORFARTI000020694605, partie III, articles 10 à 19, lus en entier) : retraite
  entière « à l'âge de 65 ans » (article 12) ; « dès l'âge de 60 ans », « 1, 25 % par trimestre
  manquant dans la limite de 20 trimestres » pour atteindre 65 ans (article 15) ; l'inapte sans
  coefficient dès 60 ans ; l'entrée en jouissance « au premier jour du trimestre civil qui suit
  cette demande » (article 14) ; « une bonification d'un dixième » pour trois enfants
  (article 17) ; aucune majoration. Conforme.
- **2011** (JORFARTI000024270214) : l'article 15 est « remplacé », sans limite de vingt
  trimestres ; deux pentes pour les nés depuis 1956, le tableau pour les autres ; l'article 12,
  les âges par génération, + 4 % et + 2 %. Le tableau est bien dans l'index, à la fin de
  l'annexe, et le modèle le rend ligne pour ligne : la table `cavp` de `ages_regimes.csv`
  (65 ans et 65 ans au plus de majoration jusqu'à la génération 1951,5, 65 et 66 ans jusqu'en
  1952, 66 et 68 ans de 1953 à 1955, 67 et 70 ans depuis 1956) et les deux pentes redonnent
  chacune de ses lignes (« 61 ― 22,00 % » = 16 × 1,25 % + 4 × 0,5 % ; « 65,25 ― 1,50 % » =
  3 × 0,5 % ; « 66,25 0,50 % » …), refaites une à une. Conforme, sauf le point ci-dessous.
- **2024** (JORFARTI000048880592, partie II lue en entier) : au 6°, « Les quatre derniers
  alinéas sont remplacés par deux alinéas » ; les quatre derniers de l'article 15 de 2011 sont
  ceux de l'inapte et du conjoint inapte, et leurs deux « A titre transitoire » : la minoration
  générale et le tableau demeurent, la carrière longue reçoit la dérogation. L. 643-3 en
  vigueur le 10 janvier 2024 (LEGIARTI000047453031) : II, la carrière longue ; III, le
  handicap ; IV, les 2° et 3° de L. 643-4. Conforme.
- **2026** (JORFARTI000054436087, articles 8 à 15 lus) : la valeur de service « applicable à
  l'âge du taux plein fixé au 1° de l'article L. 351-8 », × 0,96 avant 1953, × 0,96/0,98 de 1953
  à 1955 ; l'article 12, les deux pentes, la dérogation de la carrière longue mot pour mot ;
  l'article 14, le trimestre civil ; l'article 15, « 10 % ». Conforme.
- **Les dix textes sans effet**, rouverts et balayés (articles 8 à 17, « coefficient »,
  « 65 ans », « jouissance », « majoration ») : 2015 touche les articles 3, 4, 4 bis, 4 ter, 6
  et 22 à 36, et l'entrée en jouissance qu'il écrit est celle de la capitalisation
  (article 27) ; 2016, le dernier alinéa de l'article 14 ; 2025, partie III, les articles 1er
  à 9 bis, 14, 16, 18, 21, 29, 36, et à l'article 14 le quatrième alinéa, « payable
  trimestriellement », que l'on compte ou non à part la première phrase ; 2017, 2019, juin
  2023, les statuts généraux ou les classes ; 2012, l'invalidité-décès ; 2007, la
  capitalisation ; 21 septembre 2026, l'article 16 du règlement, la réversion. Conforme.

### Les montants, refaits : conformes

Rejoués le jour même, au centime, dans les deux moteurs, et identiques sous
`PRESOMPTIONS_DECALEES=1` (les naissances sont datées) :

| cas | servi | refait à la main |
|---|---|---|
| né le 10 mars 1965, entré à 19 ans, carrière longue à 62 ans | 11 035,0727 €, 0,81 | / 0,81 × 0,85 = 11 580,01 €, **544,94 €** |
| né le 10 mars 1966, entré à 20 ans, à 63 ans | 12 175,8132 €, 0,86 | / 0,86 × 0,90 = 12 742,13 €, **566,32 €** |
| né le 10 mars 1966, entré à 15 ans, à 58 ans | 10 580,0640 €, 0,75 | / 0,75 × 0,65 = 9 169,39 €, **1 410,68 €** |
| né le 10 mars 1964, entré à 17 ans, à 60 ans | 0,75 | 20 × 1,25 % : 0,75 |
| né le 10 mai 1960, à 67 ans | 14 548,9093 € | / 12 = **1 212,41 €** |
| né le 10 mars 1950, à 65 ans | 12 040,8187 € | / 1,04 : **463,11 €** ; × 0,96 : **481,63 €** |
| né le 10 mars 1954, à 66 ans | 12 890,5635 € | × 1,02 / 1,04 : **247,90 €** ; × 0,96 / 0,98 : **263,07 €** |
| né le 10 mars 1956, à 67 ans | 14 772,9689 € | × 1,04 : **590,92 €** |
| né le 10 mars 1940, à 64 ans, entré à 21 / 30 ans | 10 160,24 € / 7 677,91 € | 1 / 0,95 |
| né le 10 mars 1945, à 64 ans | 10 434,11 €, 0,95 | — |

Les coefficients du tableau (0,85, 0,83, 1,04, 1, 1,06, 1,02, 0,93) aussi. Le cas de 58 ans
donne 1 410,67 € si l'on soustrait les montants arrondis, 1 410,68 € à partir de la valeur
servie : la note a raison.

### Les deux erreurs déclarées : prouvées

1. **La carrière longue depuis le 10 janvier 2024.** Le modèle rend bien les deux pentes
   (0,81 = 12 × 1,25 % + 8 × 0,5 %) et la limite de vingt trimestres (0,75 à 58 ans, au lieu de
   28 × 1,25 %). Le texte : « Par dérogation [...] affectée d'un coefficient de minoration égal
   à - 1,25 % par trimestre manquant jusqu'à l'âge de 65 ans » (2024), « par trimestre
   d'anticipation jusqu'à l'âge de 65 ans » (2026). La dérogation définit le coefficient
   entier (« égal à ») et le borne à 65 ans, là où la règle générale le compte jusqu'à l'âge du
   1° de L. 351-8 ; la limite de vingt trimestres a disparu avec l'article 15 de 2009,
   « remplacé » en 2011. La lecture contraire n'a pas d'appui dans le texte. Prouvée.
2. **La date d'effet.** « L'entrée en jouissance [...] est fixée au premier jour du trimestre
   civil qui suit cette demande », de 2009 (article 14) au règlement (article 14) : une date
   d'effet au 1er juin n'existe pas au texte, la première au plus tôt à 67 ans est le
   1er juillet 2027, sans trimestre entier de majoration. Prouvée ; la même classe que celles
   de la CAVOM et de la CARPIMKO.

### Les non-tranchés déclarés : fondés

- **La valeur de service par génération** : l'article 12 de 2011 majore « le montant de la
  retraite définie à l'article 11 » de 4 % et de 2 % ; l'article 8 de 2026 fait fixer la valeur
  des nés depuis 1956 et la multiplie par 0,96 et 0,96/0,98 pour les autres ; aucun texte lu ne
  dit à quelle génération répondent les 320,75 € et 328,80 € du modèle. Les deux lectures et
  leurs montants sont justes.
- **Le trimestre entamé** : « fonction du nombre de trimestres manquants » (2011), « en
  fonction de l'âge » (2026), un tableau aux seuls trimestres entiers ; le modèle arrondit au
  trimestre supérieur. Au plus 1,25 point : juste.

### Un non-tranché non déclaré : la majoration des nés jusqu'au 30 juin 1951 (moyen)

L'article 12 récrit en 2011 dit : « De façon transitoire : ― les affiliés nés jusqu'au
31 décembre 1952 peuvent bénéficier d'une majoration de leur pension de retraite dans les mêmes
conditions, mais uniquement jusqu'à l'âge permettant d'obtenir une retraite entière augmenté
d'un an » (JORFARTI000024270214). Le tableau annexé à l'article 15, dans la même annexe, dit
pour les « assurés nés avant le 30 juin 1951 inclus » : « Pas de majoration de pension pour un
départ après 65 ans ». Les deux se contredisent pour les nés jusqu'au 30 juin 1951, du
30 juin 2011 au 17 juillet 2026. Le règlement de 2026 tranche pour le tableau (article 12 : « les
affiliés nés avant le 30 juin 1951 inclus ne bénéficient pas d'une majoration de leur pension
de retraite pour un départ après 65 ans »), et le modèle le suit ; mais la fiche, sa version de
2011, `ages_regimes.csv` et le cas `(1950, 67.0, 1.0)` de `test_la_cavp_minore_a_deux_pentes`
ne citent que le tableau, et la note de E4 aussi. Lecture contraire : l'article 12 est le texte
qui crée la majoration, le tableau n'est annexé qu'à l'article des « coefficients
d'anticipation ». Né le 10 mars 1950, parti à 66 ans le 1er avril 2016, entré à 21 ans : le
modèle sert 12 330,5476 €, sans majoration ; l'article 12 donnerait quatre trimestres, 2 %,
12 577,16 €, **246,61 € par an de plus**. Le tableau est la lecture la plus probable (texte
spécial, repris en 2026) ; elle doit être déclarée, avec la contraire, et son montant. Au
propriétaire, par la file E.

### Écarts faibles

- **Les titres d'avant 2009.** La fiche (version `statuts_d_avant_2009`, « hypothese ») ne
  nomme pas l'arrêté du 17 septembre 1956, « APPROBATION DE DISPOSITIONS STATUTAIRES COMPLETANT
  LE REGLEMENT DE LA SECTION PROFESSIONNELLE DES PHARMACIENS » (JORFTEXT000000281088), que ses
  lectures comptent pourtant (« les titres des arrêtés de 1956 à 1990 »). Et l'arrêté du
  6 avril 1989 (JORFTEXT000000318409) est, comme celui de 1990, au Bulletin officiel : « L'ARRETE
  SERA PUBLIE INTEGRALEMENT AU BULLETIN OFFICIEL [...] N0 8920 ».
- **« que les titres ».** L'index porte de quelques-uns un court résumé : 6 juillet 1977,
  « MODIFICATION DES ART. 16, 2, 6 BIS ET 10 DES STATUTS » (trois régimes, JORFTEXT000000664820) ;
  30 décembre 1988, « ENTREE EN VIGUEUR: 01-01-1989 » (JORFTEXT000000498997). Rien qui se lise
  comme une règle ; l'article 10 de 1977 rejoint ceux de 1976, 1979 et 1981 au « à relire ».

## B. E3-bis, les deux montants neufs de la CARPIMKO

### La majoration avant l'âge légal de la base : prouvée ; 136,90 €, un minimum (faible)

Les textes : l'article 11, 2°, a, de 2015 sert à taux plein « Des assurés nés à compter du
1er janvier 1961 liquidant leur pension du régime de base sans abattement », que le 1° de
l'article 12 quater, « Par dérogation aux dispositions de l'article 11 », porte à 60 ans pour la
« GÉNÉRATION 1955 ET ANTÉRIEURE » ; l'article 12 ter fait courir la majoration « au-delà de
l'âge auquel elle aurait pu être liquidée sans abattement » (JORFARTI000031255547, lu en
entier). L. 643-3, I, en vigueur en 2016 (LEGIARTI000028498667) : la pension de base « peut
être demandée à partir de l'âge prévu au premier alinéa de l'article L. 351-1 » ;
D. 161-2-1-9, 5°, le 10 juillet 2016 (LEGIARTI000025089933) : « Soixante et un ans et sept mois
pour les assurés nés en 1954 ». La base ne se liquide pas avant cet âge : la condition du a
n'est pas remplie avant. Dans la seconde lecture, rien ne majore avant 65 ans. Le modèle majore
dès la durée atteinte (le 10 mars 2016, entré le 10 décembre 1974, 165 trimestres) : trois
trimestres civils entiers, d'avril à décembre. La lecture contraire — « liquidant [...] sans
abattement » pour « ayant la durée » — se heurte au vocabulaire du texte lui-même, qui dit la
durée autrement : « par trimestre manquant pour pouvoir liquider la retraite de base à taux
plein » (articles 12 et 12 quater). Prouvée.

Le montant : 5 681,2345 € servis (1,0375, les deux moteurs) ; / 1,0375 × 1,0125 =
5 544,3373 €, **136,90 €** ; × 0,88 / 1,0375 = 4 818,78 €, 862,45 €. Exacts. Mais 136,90 €
suppose la majoration comptée de l'âge où la pension « aurait pu être liquidée sans
abattement » ; comptée de « l'âge du taux plein » de la table (65 ans pour la génération 1955
et antérieure, l'« Age prévu à l'article 11.1 »), le point suivant de la même fiche, elle est
nulle à 62 ans : 5 681,2345 / 1,0375 = 5 475,89 €, **205,35 €**. La fiche donne 136,90 €
« dans le cas posé » : c'est un minimum, à dire comme tel.

### « L'âge du taux plein » de l'article 12 ter : 1 263,99 € exact ; un texte non cité (moyen)

Né le 10 novembre 1959, entré à 20 ans, à 67 ans le 1er décembre 2026 : 7 022,1918 €, 1,25, dans
les deux moteurs ; de 66 ans et 4 mois, le 10 mars 2026, deux trimestres civils entiers
(avril-juin, juillet-septembre), 1,025 : 5 758,20 €, **1 263,99 €**. Exact.

Mais la pension prend effet sous le règlement de 2026 (JORFARTI000054435915), dont l'article 6
nomme la ligne de sa table « Age du taux plein 65 ans 65 ans 4 mois [...] 66 ans 4 mois », et
dont l'article 5 compte la majoration « par trimestre civil entier d'ajournement postérieur à
l'âge du taux plein » ; la table des statuts récrite au 10 janvier 2024 porte déjà « Âge du
taux plein » (JORFARTI000048880643, 6°), là où celle de 2015 disait « Age prévu à
l'article 11.1 ». Pour les pensions qui prennent effet depuis le 10 janvier 2024, le texte nomme
donc lui-même l'âge du taux plein, et c'est celui de la table. La lecture du modèle garde un
appui (l'article 3 sert « à taux plein » dès l'âge de L. 161-17-2 qui liquide sa base sans
abattement, et la première phrase de l'article 5), mais la fiche ne cite pas ce texte, qui pèse
pour l'autre. Le point est à reprendre par la file E : citer la ligne de la table, et dire si,
depuis 2024, il reste non tranché ou devient une erreur ; pour 2015 à 2024, le non-tranché tient.

## Les tests

`tests/test_sections_sante.py`, `tests/test_sections_liberales.py`, `tests/test_carte.py`, en
entier, et `tests/test_web.py::test_le_paquet_est_a_jour` : 117 verts. Sous
`PRESOMPTIONS_DECALEES=1`, les deux premiers : 99 verts, un sauté. `CAVP_HORS_DU_MODELE` déclare
les deux écarts de bornes que la fiche dit.

## Ce que la relecture laisse

- **À la file E** : déclarer dans `cavp_minoration_deux_pentes` (version de 2011) la
  contradiction de l'article 12 et du tableau pour les nés jusqu'au 30 juin 1951, ses deux
  lectures et 246,61 € ; nommer l'arrêté de 1956 et le Bulletin officiel de 1989 ; dans
  `carpimko_ages_2015`, dire 136,90 € un minimum (205,35 € de la table), et citer la ligne
  « Âge du taux plein » des textes de 2024 et 2026 au point de l'article 12 ter.
- **Au propriétaire**, par la file E : un non-tranché neuf, la majoration des nés jusqu'au
  30 juin 1951 de 2011 à 2026 (246,61 € par an dans le cas posé) ; et, depuis 2024, peut-être
  une erreur au lieu d'un non-tranché pour « l'âge du taux plein » de la CARPIMKO. Les autres
  erreurs et non-tranchés de E4 et E3-bis sont fondés tels qu'ils sont dits.
