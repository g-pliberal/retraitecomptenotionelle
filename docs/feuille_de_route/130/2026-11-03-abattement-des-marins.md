# L'abattement des marins au-delà du plafond de R. 11, 3°, écrit au droit

**La demande.** Le 3 novembre 2026, la session d'orchestration de la quatrième
vague confie à la file M1 l'erreur que la carte des marins avait relevée
(`130/2026-11-02-carte-des-fiches-marins-lus-au-droit.md`, « Ce que l'étape
laisse ») : le modèle liquide le forfait entier, quand le 3° de R. 11 abat le
salaire de référence au-delà de huit fois « le traitement brut correspondant à
l'indice 100 dans la fonction publique ». Décision du propriétaire : corriger
d'après la loi ; mais trancher d'abord, par un document, si cet indice 100 est
l'indice majoré 100, que la note avait pris sans source, ou l'indice brut 100.

## La question tranchée, par l'article 7 du décret n° 85-1148

- **R. 11, relu** (LEGIARTI000006791987, en vigueur depuis le 31 mars 1968,
  sans autre rédaction) : « 3° Lorsque le salaire ainsi défini excède huit fois
  le montant du traitement brut correspondant à l'indice 100 dans la fonction
  publique, la portion dépassant cette limite n'est comptée que pour moitié. »
  L. 5552-19 du code des transports (LEGIARTI000023079221, depuis le
  1er décembre 2010) : « sous réserve d'un abattement au-delà d'un plafond »,
  « cet abattement, ce plafond […] sont fixés par décret en Conseil d'Etat ».
- **L'indice 100** est le plus bas de la hiérarchie générale : « Les indices
  minimum et maximum de la hiérarchie générale sont respectivement égaux à 100
  et à 800 » (décret n° 48-1108 du 10 juillet 1948, article 1er,
  LEGIARTI000006561748).
- **Son traitement**, l'article 7 du décret n° 85-1148 du 24 octobre 1985 le
  dit pour tous les textes qui s'y réfèrent. Rédaction d'origine
  (LEGIARTI000006454537, 5 novembre 1985) : « Pour l'application des
  dispositions législatives et réglementaires se référant au traitement de
  l'indice 100 prévu par le décret du 10 juillet 1948 susvisé, ce traitement
  est constitué par le traitement afférent à l'indice majoré 150 (indice brut
  100). » Depuis le 1er juillet 2008 (décret n° 2008-622, article 2, 3°,
  JORFARTI000019108393) : « Pour l'application des dispositions législatives et
  réglementaires se référant au traitement de l'indice 100 ou de l'indice brut
  100, ce traitement est constitué par le traitement afférent à l'indice majoré
  201. » Depuis le 1er janvier 2024 (décret n° 2023-519, article 2,
  JORFARTI000047749229 ; LEGIARTI000047751780) : l'indice majoré 208. Les
  dérogations du second alinéa — une liste de textes jusqu'en 2003, l'article 65
  de la loi du 11 janvier 1984 depuis 2005 — ne visent pas le code des marins.
- **Réponse : l'indice brut 100**, que l'article 7 constitue de l'indice
  majoré de sa date ; pas l'indice majoré 100. Les vingt-sept rédactions de
  l'article sont lues dans l'index LEGI ; la date d'effet de chaque relèvement,
  dans le décret qui le fait (index JORF) quand la base LEGI date la rédaction
  de sa publication : n° 98-462 (« à compter du 1er juillet 1998 »), n° 99-208,
  n° 99-491, n° 99-943, n° 2001-559, n° 2004-679, n° 2005-726, n° 2006-759,
  n° 2006-1283, n° 2007-1054, n° 2008-400, n° 2008-622, n° 2009-824,
  n° 2023-519. Un piège : en mai et juin 2001, le premier alinéa dit encore 164
  — le décret n° 2001-370 ne le touche pas —, et le n° 2001-559 y remplace un
  « 169 » qu'il ne porte pas ; la série garde 164, le texte en vigueur.
- **Les deux lectures, chiffrées en 2026** : à l'indice majoré 100, le plafond
  vaudrait 8 × 100 × 59,0734 = 47 258,72 €, et les catégories 15 à 20
  (49 285,81 € à 76 867,05 €) le passeraient ; à l'indice brut 100, il vaut
  8 × 208 × 59,0734 = 98 298,14 €, et aucune ne l'atteint, la vingtième étant à
  78,2 % de lui.
- **Ailleurs, rien** : ni le rapport S2023-0865 de la Cour des comptes sur
  l'ÉNIM (exercices 2016 à 2021), ni sept réponses ministérielles sur les
  pensions des marins, ni les pages de l'ENIM (renvoyées à son portail) ne
  chiffrent le plafond. Légifrance et Gallica refusent l'outil de la session.

## Ce qui est fait

- **Le test d'abord**, vu rouge pour la raison attendue, puis vert :
  `tests/test_marins.py` (la série `INDICE_100`, relue rédaction par rédaction
  au LEGI ; le plafond et l'abattement posés à la main ; un marin qui passe le
  plafond ; la déclaration d'avant 1985), et `tests/js/moteur.test.js` (« le
  salaire des marins ne compte que pour moitié au-delà du plafond de R. 11 »).
  Les deux écarts de `ECARTS_DECLARES` sur R. 11, 3° partent : la période les
  porte. L'ancien test, qui mesurait l'abattement à l'indice majoré 100, est
  remplacé par celui qui le mesure au droit.
- **La donnée** : `legislation/indice_100_fonction_publique.csv`, vingt lignes,
  de l'indice majoré 150 au 5 novembre 1985 à 208 au 1er janvier 2024, chacune
  avec son identifiant LEGI, niveau `haute`. La période des marins porte
  `plafond_en_traitements_de_l_indice_100: 8` et `part_au_dela_du_plafond:
  0.5`, déclarés au schéma.
- **Les deux moteurs** : `plafondDuSalaireDeReference` et
  `abattreAuDelaDuPlafond` au portage, `MinimumGaranti.traitementDeLIndice100`
  pour le traitement de l'indice 100 (indice de la date d'effet, point du
  1er janvier de l'année, le dernier connu au-delà de 2027) ; leurs jumeaux
  Python, ligne pour ligne. Le détail du montant dit l'abattement. Le paquet
  porte la série et les deux champs : sa version passe à 39.
- **Un témoin** de plus, `marin_au_dela_du_plafond`, le seul où la règle mord.
- **La fiche** `marins_salaire_de_reference` : l'approximation de R. 11, 3°
  retirée ; les textes de l'article 7 dans ses versions ; deux approximations
  neuves, déclarées — avant le 5 novembre 1985, rien n'est lu ; le point du
  1er janvier, non du jour —, et ses lectures du 3 novembre.

## Les valeurs des tests, posées à la main

Le traitement de l'indice 100 est l'indice majoré de la date fois le point de
l'année (`point_indice_fonction_publique.csv` : 38,5544 en 1985, 43,0973 en
1990, haute, OpenFisca ; 54,4113 en 2008, 59,0734 en 2026, certifiées sur
l'article 3 du décret n° 85-1148) ; le plafond, huit fois plus.

| Date d'effet | Indice majoré | Traitement | Plafond |
|---|---|---|---|
| 1er janvier 2026 | 208 | 208 × 59,0734 = 12 287,2672 € | 98 298,1376 € |
| 1er janvier 1990 | 156 | 156 × 43,0973 = 6 723,1788 € | 53 785,4304 € |
| 1er juin 2008 | 199 | 199 × 54,4113 = 10 827,8487 € | 86 622,7896 € |
| 1er juillet 2008 | 201 | 201 × 54,4113 = 10 936,6713 € | 87 493,3704 € |
| 1er décembre 1985 | 150 | 150 × 38,5544 = 5 783,16 € | 46 265,28 € |
| 1er octobre 1985 | — | non lu | aucun |

L'abattement : 100 000 € en 2026 donnent 98 298,1376 + (100 000 − 98 298,1376)
/ 2 = 98 298,1376 + 850,9312 = 99 149,0688 € ; la vingtième catégorie de 2026,
76 867,05 €, reste entière. Le marin né le 1er janvier 1990, à quatre fois le
salaire moyen, parti le 1er juillet 2045 : vingtième catégorie, 121 749,59 €
dans la grille du modèle (celle de 2026 portée par le salaire moyen, une donnée
du modèle, non du droit) ; il liquide 98 298,1376 + (121 749,59 − 98 298,1376)
/ 2 = 98 298,1376 + 11 725,7262 = 110 023,86 €.

## Ce qui bouge

`regenerer.py`, en 607 secondes : « la prose déclarée dit le vrai », « rien de
perdu ». `resumer_temoins.py` : « 930 témoins de simulation, aucun ne bouge
depuis HEAD ; 1 nouveau. 85 rendus de page, aucun ne change. » Le nouveau,
`marin_au_dela_du_plafond`, écrit « SR 110,023.86 € (forfait 121,749.59 €
compté pour moitié au-delà de 98,298.14 €, R. 11, 3°) × taux 75.000% ×
142/150 » ; le jumeau Python le refait au bit près (`test_pont.py -k refait`).
Le chiffrage n'a rien à changer. Le paquet passe de 5 785 à 5 859 Ko bruts
(796 à 797 Ko compressés), les deux champs de période écrits pour chacune ;
les chiffres ancrés qui le disent sont refaits. Rien de ce que le modèle
calcule de 1985 à 2026 ne bouge : c'est ce que le droit, lu à l'article 7,
voulait.

## Ce que l'étape laisse

- **Avant le 5 novembre 1985**, le traitement de l'indice 100 n'est pas lu : les
  décrets de rémunération qui le fixaient (n° 68-566, n° 70-393, n° 74-652 et
  leurs modifications) ne sont dans les index qu'en analyses. Le modèle n'abat
  pas ; l'effet est nul tant que ce traitement valait au moins celui de l'indice
  majoré 103 (seuils de 76,5 en 1968 à 102,8 en 1980, au point de l'année) — il
  valait celui de l'indice majoré 150 en 1985.
- **En projection**, le point reste à sa valeur de 2027, faute de décret, et la
  grille des marins suit le salaire moyen : la vingtième catégorie passe le
  plafond en 2037, au rapport 1,02. Le droit constant le veut ; mais la grille
  suit le salaire moyen, quand L. 5553-5 la revalorise depuis 2018 par le
  coefficient de L. 161-25, celui des prix : la règle de projection de la grille
  n'est pas de cette étape.
- Les deux petits écarts de la note du 2 novembre (la levée des cinquante-deux
  ans et demi d'avant 1985, la bonification de l'enfant de moins de neuf ans)
  ne sont pas de cette session.
- Une confirmation de l'ENIM reste souhaitable : ni elle, ni la Cour des
  comptes, ni une réponse ministérielle n'écrivent le plafond.
- Le bloc « Reprise » de l'action 130 range encore « l'abattement des marins
  (R. 11, 3°) » parmi ce qui attend le propriétaire : tranché et écrit, il est à
  en retirer par la file E, qui seule récrit ce bloc.
- `regenerer.py --verifier` dira périmé ce que GitHub refait d'un envoi à
  l'autre ; le paquet, les témoins et les chiffres ancrés de cette étape sont
  commités refaits.

## Ce qui attend le propriétaire

Une question, sans urgence : faire lire au Journal officiel imprimé les
décrets de rémunération de 1968 à 1985, pour abattre aussi les pensions
d'avant le 5 novembre 1985 ? Avis : non pour l'instant — l'effet est nul sur
la grille du modèle tant que le traitement de l'indice 100 valait au moins
celui de l'indice majoré 103, et il valait celui de l'indice majoré 150 en
1985. À savoir aussi : en projection, l'abattement mord dès 2037, sous le
point gardé à sa valeur de 2027 ; c'est le droit constant.
