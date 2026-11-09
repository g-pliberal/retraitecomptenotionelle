# Un seuil en euros sous lequel aucune pension déjà servie ne baisse : qui il protège, ce qu'il coûte, ce que le droit en dit

**Reprise, au 9 novembre 2026.** L'étude est faite ; rien n'est décidé, ni le
modèle ni le site ne sont touchés. Quatre seuils (1 050 €, 1 200 €, 1 500 €,
la médiane à 1 563 €) et trois règles (tranche, plancher, lissage) sont
chiffrés au modèle, le stock relevé en mémoire (« Les calculs, en entier »).
La tranche à 1 050 € perd 53 % de la baisse. Au propriétaire, en fin de note
(« Ce que le propriétaire tranche ») : le principe, la règle, le niveau, qui
paie, l'assiette, l'articulation avec la garantie, la relecture d'un
juriste. Puis ses réponses en décisions, et une session du modèle écrit le
seuil au scénario 6 seul, le test d'abord ; aucune avant.

*Le 9 novembre 2026, action 186, chantier 2. Le propriétaire demande de
chiffrer une piste : la baisse des pensions servies à la bascule (décisions 2
et 3) ne toucherait que la part de la pension au-dessus d'un seuil, comme une
tranche d'impôt. Quatre seuils : 1 050 € (la garantie), 1 200 €, 1 500 €, et
la pension médiane. La session a lu les décisions 29, 30, 49, 86 et 87, le
chantier 2 et les notes `2026-11-07-deux-lectures-et-reprise.md`,
`…-deux-lectures-au-modele.md`, `…-indexation-scenario-6.md` et
`…-complementaires-baisse-avant-integration.md`. Le modèle est celui de
`main` au commit `70f923b` ; aucune ligne n'en change, ni du site. Les calculs
sont des scripts tenus hors du dépôt, sur les réglages de la page Coût,
variante rétroactive ; le seul réglage changé, en mémoire, est le niveau du
stock à la bascule. La note propose ; le propriétaire tranche.*

**Les marques.** **(publié)** : lu par la session dans le document cité, ou
dans la donnée certifiée du dépôt qui le recopie. **(dépôt)** : un réglage ou
une sortie du modèle tel qu'il est. **(calcul)** : fait ici, et posé en entier
dans « Les calculs, en entier ». Un tableau porte sa marque dans sa légende.

## L'essentiel

1. **La tranche protège tout le monde, et c'est ce qui la rend chère.** Avec
   un seuil à 1 050 €, 31 % des retraités ne perdent rien, 5,4 millions de
   personnes (calcul). Mais les 69 % restants gardent eux aussi leurs
   premiers 1 050 € intacts. La baisse perd 53 % de ce qu'elle économise :
   61 Md€ sur 115 en 2026 (calcul). À la médiane, 1 563 €, elle en perd 71 %.
2. **La dette de 2070 monte de 50 à 66 points de PIB.** Sur la base de la
   page Coût, au taux de 18 %, elle passe de 103 points à 152 (seuil de
   1 050 €) ou 169 (médiane) (calcul au modèle). Avec la part de TVA et la
   LVT, de 1 point à 51 ou 67.
3. **Sous la décision 29, la lecture A partage la facture, la lecture B la
   met toute sur les cotisants.** Seuil à 1 050 € : le taux de la lecture A
   monte de 0,8 point et sa réserve de 2070 fond de 71 à 40 points ; celui de
   la lecture B monte de 2,0 points, 74 € par mois au salaire moyen (calcul).
4. **Pour ceux qui restent touchés, la baisse est divisée par deux** : 15,5 %
   en moyenne au lieu de 29,9 %, avec un seuil à 1 050 € ; 9 % pour une
   pension de 1 500 €, 19,5 % pour 3 000 € (calcul).
5. **Deux autres règles protègent les mêmes personnes pour bien moins.** Un
   plancher (aucune pension ne passe sous le seuil) perd 18 % de la baisse à
   1 050 €, mais ramène au même montant toutes les pensions entre 1 050 et
   1 500 €. Un lissage (au-dessus du seuil, la baisse ne prend que la moitié
   de chaque euro) en perd 31 %, sans écraser personne (calcul).
6. **En droit, le seuil aide sur trois points et n'en règle pas deux.** Il
   écarte le grief de privation des moyens d'existence, il répond au grief
   d'inégalité s'il a la forme d'une tranche, et la CEDH a admis en 2023 une
   baisse serbe bâtie exactement ainsi. Il ne change rien à ce qui a fait
   tomber les baisses portugaises de 2013 et 2014 : une baisse définitive.
   Et il ouvre un risque devant le Conseil constitutionnel, qui regarde si
   les pensions reflètent encore les cotisations. À faire relire par un
   spécialiste de droit public.

## La règle, posée

Pour un retraité dont la pension du droit en vigueur vaut `p`, et dont le
compte notionnel justifie `f × p` (en moyenne `f` = 0,70 : la baisse est de
30 %), avec un seuil `s` :

| Règle | Pension servie | Une pension de 1 500 €, seuil à 1 050 € |
|---|---|---|
| Sans seuil (le modèle) | `f × p` | 1 051 € (−29,9 %) |
| **La tranche** (la piste) | `min(p, s) + f × (p − s)` au-dessus de `s` | 1 050 + 0,70 × 450 = 1 365 € (−9,0 %) |
| Le plancher | le plus grand de `f × p` et de `min(p, s)` | 1 051 € (−29,9 %) |
| Le lissage à 50 % | le plus grand de `f × p` et de `p − 0,5 × (p − s)` | 1 500 − 225 = 1 275 € (−15,0 %) |

Aucune des trois n'a d'effet de seuil au sens strict : un euro de pension en
plus ne fait jamais perdre plus d'un euro. Elles diffèrent par ce qu'elles
font au-dessus du seuil. La tranche laisse à tous la même franchise. Le
plancher met au seuil toutes les pensions entre `s` et `s / f` : à 1 050 €,
la pension de 1 050 € et celle de 1 499 € finissent toutes deux à 1 050 €.
Le lissage garde l'ordre des pensions et rejoint la baisse entière à
2 618 € pour un seuil de 1 050 € (calcul).

Le seuil ne vaut que pour le stock, les pensions servies à la bascule : c'est
la lettre de la décision 2 et de la décision 86. Il suit les prix, comme le
stock dans le modèle.

## Qui est protégé

Tableau (calcul), sur la distribution des pensions de droit direct de la
DREES portée à 2026 ; effectifs sur les 17,3 millions de retraités de droit
direct de fin 2024 (publié, panorama 2026 de la DREES).

| Seuil, euros de 2026 par mois | Retraités dont la pension ne baisse pas | Soit | Femmes | Hommes | Parmi les résidents en France |
|---|---:|---:|---:|---:|---:|
| 1 050 € | 31,4 % | 5,4 millions | 44,6 % | 16,7 % | 28,3 % |
| 1 200 € | 37,4 % | 6,5 millions | 51,9 % | 21,1 % | 34,5 % |
| 1 500 € | 47,8 % | 8,3 millions | 63,2 % | 30,6 % | 45,3 % |
| 1 563 €, la médiane | 50,0 % | 8,65 millions | 65,3 % | 32,9 % | 47,6 % |
| La garantie telle qu'elle est : 1 050 € seul, 800 € en couple | 26,7 % | 4,6 millions | | | 23,5 % |

**La pension médiane.** La DREES publie, à l'échantillon interrégimes de
retraités de 2020, une pension médiane de droit direct de 1 329 € brut par
mois pour tous les retraités, 1 382 € pour ceux qui résident en France,
majorations pour enfants comprises (publié). Sans ces majorations, la
grandeur de la distribution et du modèle, la médiane vaut 1 294 € et 1 344 €
(calcul). Portée en euros de 2026, 1 563 € et 1 625 € (calcul). La note
retient 1 563 €, la médiane de tous ceux que la baisse touche. Le classeur
de la DREES n'a pas pu être retéléchargé (son portail a coupé chaque
connexion de la session) : la médiane est lue dans la donnée certifiée du
dépôt, `data/reference/macro/pensions_residence.csv`. Le panorama 2026, lui,
a été relu : il ne donne pas la médiane, mais 34 % de retraités résidant en
France sous 1 000 € fin 2020 (publié), que la distribution redonne à
34,8 % (calcul).

**La pondération du recensement** ne joue que pour la dernière ligne. La
garantie vaut 800 € par personne et 1 050 € pour qui vit seul ; le
recensement, pesé comme dans `docs/chiffrage_plf.md`, donne 56,0 % de femmes
et 29,0 % d'hommes vivant seuls parmi ses bénéficiaires (dépôt). Un seuil
calqué sur la garantie, 1 050 € ou 800 € selon le foyer, protège 26,7 % des
retraités et perd 47 % de la baisse (calcul). Il demande de connaître le
foyer de chaque retraité, que les caisses ne connaissent pas.

**Les retraités qui résident à l'étranger** sont 0,9 million (publié), et
plus de huit sur dix sont sous 1 050 € (calcul) : leur pension française est
courte, 437 € en moyenne (publié). Le seuil les protège presque tous, sans
rien savoir de leurs autres pensions.

## L'économie perdue

**En 2026.** Le stock du scénario 6 vaut 268,4 Md€ de droits directs
(dépôt) ; sa baisse, 114,7 Md€ (calcul). Tableau (calcul) : la part perdue
vient de la distribution ; les milliards, du coût du modèle, le stock relevé
d'autant.

| Seuil | Part de la baisse perdue | Pensions servies en plus | Garantie en moins | Net, en 2026 | Baisse qui reste |
|---|---:|---:|---:|---:|---:|
| 1 050 € | 53,3 % | 61,2 Md€ | −3,1 Md€ | 58,1 Md€, 1,90 point de PIB | 53,5 Md€ |
| 1 200 € | 59,0 % | 67,7 Md€ | −3,4 Md€ | 64,3 Md€, 2,10 points | 47,0 Md€ |
| 1 500 € | 68,9 % | 79,0 Md€ | −3,8 Md€ | 75,2 Md€, 2,45 points | 35,7 Md€ |
| 1 563 € | 70,7 % | 81,1 Md€ | −3,9 Md€ | 77,2 Md€, 2,52 points | 33,6 Md€ |

L'économie de 2026 que la page Coût tire de la baisse, garantie déduite, est
de 104 Md€ (dépôt). Le seuil à 1 050 € en laisse 46.

**Année après année.** Le stock s'éteint : 99 % des droits directs du
scénario 6 en 2026, 81 % en 2030, 40 % en 2040, 14 % en 2050 (dépôt). Le
coût du seuil s'éteint avec lui. Net de la garantie, en milliards d'euros
courants (calcul au modèle) :

| Seuil | 2026 | 2030 | 2035 | 2040 | 2050 | 2060 | Cumul 2026-2070 | En euros de 2026 | Moyenne, points de PIB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 050 € | 58,1 | 53,7 | 47,5 | 38,6 | 17,1 | 2,4 | 1 099 | 913 | 0,60 |
| 1 200 € | 64,3 | 59,5 | 52,6 | 42,8 | 19,0 | 2,7 | 1 216 | 1 011 | 0,67 |
| 1 500 € | 75,2 | 69,5 | 61,4 | 49,9 | 22,1 | 3,1 | 1 420 | 1 180 | 0,78 |
| 1 563 € | 77,2 | 71,3 | 63,0 | 51,3 | 22,7 | 3,2 | 1 458 | 1 212 | 0,80 |

## La baisse qui reste pour les autres

Sous la tranche, la baisse d'une pension, au `f` de l'ensemble (calcul) :

| Pension du droit en vigueur | Sans seuil | 1 050 € | 1 200 € | 1 500 € | 1 563 € |
|---|---:|---:|---:|---:|---:|
| 1 200 € | −29,9 % | −3,7 % | 0 | 0 | 0 |
| 1 500 € | −29,9 % | −9,0 % | −6,0 % | 0 | 0 |
| 2 000 € | −29,9 % | −14,2 % | −12,0 % | −7,5 % | −6,5 % |
| 2 500 € | −29,9 % | −17,4 % | −15,6 % | −12,0 % | −11,2 % |
| 3 000 € | −29,9 % | −19,5 % | −18,0 % | −15,0 % | −14,3 % |
| 4 000 € | −29,9 % | −22,1 % | −21,0 % | −18,7 % | −18,2 % |
| 5 000 € | −29,9 % | −23,7 % | −22,8 % | −21,0 % | −20,6 % |

En moyenne, pour les retraités au-dessus du seuil (calcul) :

| Seuil | Leur baisse moyenne | En part de leur pension | Taux qu'il faudrait prendre au-dessus du seuil pour garder toute l'économie |
|---|---:|---:|---:|
| Sans seuil, tous | 518 € par mois | 29,9 % | |
| 1 050 € | 353 € par mois | 15,5 % | 62 % |
| 1 200 € | 339 € par mois | 14,2 % | 70 % |
| 1 500 € | 309 € par mois | 11,9 % | 91 % |
| 1 563 € | 304 € par mois | 11,5 % | 97 % |

La dernière colonne mesure ce qu'on perd : pour retrouver toute l'économie
avec un seuil à la médiane, il faudrait retirer 97 % de chaque euro au-dessus
de 1 563 €. Ce ne serait plus la règle du chantier 2, « nous ne reprenons
pas un euro cotisé » ; la note ne le propose pas.

Le modèle donne aux femmes une baisse plus forte qu'aux hommes, 37,2 %
contre 24,7 % (dépôt, calcul), parce qu'elles ont plus de durée validée sans
cotisation. Le seuil corrige en partie cet écart : 45 % des femmes sont sous
1 050 €, contre 17 % des hommes.

## L'effet sur le partage de la décision 29

Sur la base de la page Coût, avec la part de TVA et la LVT centrale
(décisions 79 à 81), comme la dernière partie de
`2026-11-07-deux-lectures-au-modele.md`. Tableau (calcul au modèle). Le taux
est constant de 2026 à 2070, la règle tenue en moyenne.

| Sous la tranche | Sans seuil | 1 050 € | 1 200 € | 1 500 € | 1 563 € |
|---|---:|---:|---:|---:|---:|
| **Lecture A** : taux cotisé et crédité | 21,22 % | 22,06 % | 22,14 % | 22,30 % | 22,33 % |
| Solde de la caisse en 2026, points de PIB | +0,71 | −0,92 | −1,10 | −1,40 | −1,46 |
| En déficit | jamais | 2026 à 2032 | 2026 à 2034 | 2026 à 2037 | 2026 à 2037 |
| Réserve en 2070, points de PIB | 70,6 | 39,7 | 36,2 | 30,6 | 29,6 |
| **Lecture B** : taux cotisé et crédité | 15,94 % | 17,92 % | 18,13 % | 18,49 % | 18,56 % |
| Solde de la caisse en 2026 | −1,54 | −2,69 | −2,82 | −3,03 | −3,07 |
| En déficit jusqu'en | 2059 | 2055 | 2055 | 2054 | 2054 |
| Dette en 2070 | 47,1 | 52,5 | 53,1 | 54,3 | 54,4 |
| **Programme, 18 %** : solde de la caisse en 2026 | −0,66 | −2,66 | −2,87 | −3,24 | −3,31 |
| Solde moyen 2026-2070 | +0,09 | −0,54 | −0,61 | −0,72 | −0,74 |
| Dette en 2070 | 1,2 | 50,7 | 56,0 | 65,2 | 66,9 |
| **Tout au déficit** : taux | 26,42 % | 26,42 % | 26,42 % | 26,42 % | 26,42 % |

- **Lecture A.** La règle donne la moitié de l'économie au déficit, l'autre
  aux cotisants. L'économie baisse, les deux moitiés aussi : le taux monte
  de 0,8 à 1,1 point, 31 à 41 € par mois au salaire moyen (3 732 € brut,
  dépôt), et la réserve de 2070 perd 31 à 41 points de PIB. Surtout, la
  caisse n'est plus en excédent dès 2026 : elle commence par un déficit de
  0,9 à 1,5 point de PIB, et y reste sept à douze ans, quand l'avantage de
  la lecture A était de n'en avoir aucun.
- **Lecture B.** La règle fixe le déficit, la moitié de celui du droit en
  vigueur ; tout ce que le seuil coûte va donc aux cotisants. Le taux monte
  de 2,0 à 2,6 points, 74 à 98 € par mois au salaire moyen. À 1 200 €, il
  rejoint les 18 % du programme. Ce taux de plus ouvre des droits : la
  pension des actifs monte avec lui, et la dette de 2070 bouge peu.
- **Tout au déficit.** Le taux ne bouge pas : le seuil est payé par la
  réserve seule.
- **Sans la TVA ni la LVT**, les écarts sont les mêmes : la lecture A passe
  de 25,31 % à 26,15 % (seuil de 1 050 €) ou 26,42 % (médiane), la lecture B
  de 20,76 % à 22,74 % ou 23,38 %.

Le seuil ne change pas le choix entre A et B ; il en change le prix. Devant
les juges, il déplace aussi l'argument d'urgence de la décision 6 : sous A,
la caisse rouvre un déficit ; à 18 %, elle y reste jusqu'en 2055 et finit
avec 51 à 67 points de dette.

## L'effet sur la dette de 2070

Tableau (calcul au modèle), en points de PIB ; le droit en vigueur finit à
66 points (dépôt).

| Sous la tranche | Sans seuil | 1 050 € | 1 200 € | 1 500 € | 1 563 € |
|---|---:|---:|---:|---:|---:|
| Page Coût, 18 %, sans TVA ni LVT | 102,8 | 152,4 | 157,7 | 166,8 | 168,5 |
| 18 %, avec la part de TVA et la LVT centrale | 1,2 | 50,7 | 56,0 | 65,2 | 66,9 |
| Lecture A, avec la TVA et la LVT (négatif : une réserve) | −70,6 | −39,7 | −36,2 | −30,6 | −29,6 |
| Lecture B, avec la TVA et la LVT | 47,1 | 52,5 | 53,1 | 54,3 | 54,4 |

Au taux de 18 %, le seuil ajoute 50 points de dette à 1 050 €, 66 à la
médiane : le coût tombe dans les premières années, et porte intérêt
quarante ans. Avec la TVA et la LVT, un seuil à la médiane ramène la
proposition à la dette du droit en vigueur. Sous les lectures A et B, le
taux absorbe une part du coût, et la dette bouge moins.

## Deux autres règles, pour comparer

Tableau (calcul) : la part perdue sur la distribution, le reste au modèle,
au taux de 18 %, base de la page Coût.

| Seuil | Règle | Part de la baisse perdue | Net en 2026 | Cumul 2026-2070, Md€ courants | Dette 2070 | Baisse d'une pension de 1 500 € | de 2 500 € |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 050 € | Tranche | 53,3 % | 58,1 Md€ | 1 099 | 152,4 | −9,0 % | −17,4 % |
| | Lissage à 50 % | 31,1 % | 33,7 Md€ | 640 | 131,8 | −15,0 % | −29,0 % |
| | Plancher | 18,0 % | 19,5 Md€ | 370 | 119,6 | −29,9 % | −29,9 % |
| 1 200 € | Tranche | 59,0 % | 64,3 Md€ | 1 216 | 157,7 | −6,0 % | −15,6 % |
| | Lissage à 50 % | 37,8 % | 41,1 Md€ | 778 | 138,0 | −10,0 % | −26,0 % |
| | Plancher | 23,2 % | 25,2 Md€ | 477 | 124,4 | −20,0 % | −29,9 % |
| 1 500 € | Tranche | 68,9 % | 75,2 Md€ | 1 420 | 166,8 | 0 | −12,0 % |
| | Lissage à 50 % | 50,8 % | 55,3 Md€ | 1 045 | 150,0 | 0 | −20,0 % |
| | Plancher | 35,0 % | 38,0 Md€ | 720 | 135,4 | 0 | −29,9 % |
| 1 563 € | Tranche | 70,7 % | 77,2 Md€ | 1 458 | 168,5 | 0 | −11,2 % |
| | Lissage à 50 % | 53,3 % | 58,1 Md€ | 1 099 | 152,4 | 0 | −18,7 % |
| | Plancher | 37,7 % | 40,9 Md€ | 775 | 137,9 | 0 | −29,9 % |

Sans seuil, la dette de 2070 est de 102,8 points (dépôt). Les trois règles
protègent les mêmes retraités, ceux du tableau « Qui est protégé ».

## Le seuil et la garantie vieillesse

Le scénario 6 a déjà un plancher : la garantie. Elle n'est pas le seuil, sur
six points. Elle se demande, et le modèle suppose qu'un ayant droit sur deux
la réclame (dépôt), quand le seuil s'applique d'office. Elle s'ouvre à
65 ans. Elle exige de résider en France. Elle vaut 800 € en couple. Elle se
reprend sur la succession (décision 30), quand une pension gardée par le
seuil ne se reprend pas. Elle vaut aussi pour les pensions nouvelles.

En 2026, la baisse fait passer sous la garantie 2,05 millions de retraités
de plus : 5,54 millions d'ayants droit, contre 3,48 millions si les pensions
restaient ce qu'elles sont (dépôt, calcul). Dès que le seuil est au moins à
1 050 €, plus personne ne passe sous la garantie du fait de la baisse. La
garantie coûte alors 8,7 Md€ au lieu de 14,1, au recours du modèle (calcul
sur la distribution) : 5,4 Md€ de moins, quel que soit le seuil.

Le modèle n'en voit qu'une partie. Il déplace toute la distribution d'un
même rapport, et ne sait pas qu'un seuil relève d'abord le bas : il compte
3,2 Md€ de garantie en moins pour la tranche à 1 050 €, 1,2 Md€ pour le
plancher (dépôt). Le coût net de 2026 est donc surestimé d'environ 2 Md€
pour la tranche et 4 Md€ pour le plancher, et la dette de 2070 d'environ 2
et 4 points (calcul, ordre de grandeur). Le plancher à 1 050 € coûte, net,
plutôt 15 Md€ que 19,5 en 2026.

Si la garantie est servie d'office (décision 20), elle coûte 28,2 Md€ en
2026 sans seuil, 17,3 Md€ avec (calcul) : le seuil lui épargne 10,9 Md€. Le
plancher à 1 050 € ne coûte alors plus que 10 Md€ nets en 2026. La garantie
d'office paie déjà la moitié d'un plancher ; elle paie moins d'un cinquième
d'une tranche.

## Le droit, lu aux sources

Les textes ont été lus le 9 novembre 2026 sur les sites des trois
juridictions (les adresses sont dans « Les sources »). Les citations sont
exactes ; ce qu'elles valent pour le programme est une lecture de la
session, à faire relire par un spécialiste de droit public.

### Le Conseil constitutionnel

Aucune des décisions lues ne porte sur une baisse en euros de pensions déjà
liquidées. Les précédents portent sur leur revalorisation.

- **Le cadre** (décision 2013-682 DC, considérant 14) : le législateur « ne
  saurait, sans motif d'intérêt général suffisant, ni porter atteinte aux
  situations légalement acquises ni remettre en cause les effets qui peuvent
  légitimement être attendus de telles situations ». Et le onzième alinéa du
  Préambule de 1946 (décision 2003-483 DC, considérant 7) « implique la mise
  en oeuvre d'une politique de solidarité nationale en faveur des
  travailleurs retraités », le législateur gardant le choix des modalités ;
  revaloriser les pensions de 0,3 % en 2019, sous l'inflation, ne le
  méconnaît pas (décision 2018-776 DC, paragraphe 46).
- **Un seuil est admis** (décision 2014-698 DC, considérants 16 et 17). Le
  gel des pensions de 2014 épargnait les retraités dont le total des
  pensions ne dépassait pas 1 200 € par mois, avec une revalorisation
  réduite de moitié entre 1 200 et 1 205 €. Le Conseil : « le législateur a
  entendu préserver les faibles pensions de retraite » ; la mesure ne vaut
  que pour 2014 et « est d'une ampleur maximale de 7 euros par mois » ; elle
  « ne crée pas de rupture caractérisée de l'égalité devant les charges
  publiques ».
- **Mais un seuil durable touche au caractère contributif** (décision
  2019-795 DC, paragraphes 59 à 69). La revalorisation de 2020 épargnait les
  pensions totales d'au plus 2 000 €, « 77 % des assurés ». Le Conseil
  l'admet, après avoir écrit : « Les niveaux relatifs des prestations
  versées à chaque assuré doivent également, dans le cadre d'un régime
  contributif de cotisations sociales, refléter les écarts de
  contribution » ; la mesure « modifie durablement les niveaux relatifs des
  prestations » et « affecte ainsi, par ses conséquences, le caractère
  contributif des régimes d'assurance vieillesse ». Elle passe « compte tenu
  de son caractère exceptionnel et limité » : une seule année, 14 € par mois
  au plus, et « un mécanisme de lissage des effets de seuil ».
- **Les revenus modestes peuvent être traités à part** (décision 2017-756
  DC, paragraphe 15) : la hausse de la CSG épargnait « les pensions de
  retraite ou d'invalidité des personnes à revenus modestes », différence
  « justifiée par la différence de situation ».

*Ce qu'un seuil y change.* Il sert un but que le Conseil a reconnu deux
fois, préserver les faibles pensions, et il répond au onzième alinéa : la
baisse ne retire à personne ses moyens d'existence. Le critère admis est le
total des pensions de la personne, tous régimes, droits directs et dérivés.
Le risque est au paragraphe 63 de 2019 : un seuil permanent, de plusieurs
centaines d'euros par mois, n'est ni exceptionnel ni limité. La réponse du
programme serait que la baisse elle-même rapproche les pensions des
cotisations, et que le seuil n'en excepte qu'une part. La tranche s'y prête
le mieux : la franchise est la même pour tous, l'ordre et les écarts des
pensions sont gardés au-dessus du seuil. Le plancher s'y prête le moins : il
rend égales des pensions que des cotisations inégales ont ouvertes.

### La CEDH, article 1 du Protocole n° 1

- **Le critère** (Béláné Nagy c. Hongrie, Grande Chambre, 13 décembre 2016,
  paragraphe 117, sur une pension d'invalidité) : « la suppression de
  l'intégralité d'une pension risque d'enfreindre les dispositions de
  l'article 1 du Protocole n° 1, à l'inverse d'une réduction raisonnable » ;
  mais « le critère du juste équilibre ne saurait uniquement reposer, dans
  l'abstrait, sur le montant ou le pourcentage de la réduction ».
- **La Grèce** (Koufaki et ADEDY c. Grèce, décision du 7 mai 2013). La
  requérante individuelle était une fonctionnaire en activité, dont le
  salaire passait de 2 435,83 € à 1 885,79 € : cette baisse « n'est pas d'un
  niveau tel qu'elle risque d'exposer la requérante à des difficultés de
  subsistance » (paragraphe 46). Pour les pensions, portées par le syndicat,
  la Cour relève que « la suppression du 13e et du 14e mois de pension est
  compensée, pour les personnes percevant moins de 2 500 EUR par mois, par
  la création d'une prime unique de 800 EUR par an » (paragraphe 47). Elle
  donne « un poids particulier » à l'arrêt du Conseil d'État grec, pour qui
  « l'absence de caractère seulement provisoire de la réduction des salaires
  et pensions était justifiée », le but étant « d'assainir les finances
  publiques de l'Etat de manière durable » (paragraphe 44).
- **Le Portugal** (Da Conceição Mateus et Santos Januário, décision du
  8 octobre 2013). Les treizième et quatorzième mois étaient intacts sous
  600 € de pension, réduits entre 600 et 1 100 €, suspendus au-dessus. Les
  requérants perdaient 10,8 % et 10,7 % de leur pension annuelle. La Cour :
  une atteinte « limited both in time and in quantitative terms (less than
  11% of their total social security benefits) », pour trois ans
  (paragraphe 28). De même pour la contribution extraordinaire de solidarité
  (da Silva Carvalho Rico, décision du 1er septembre 2015) : 4,6 % de la
  pension, deux ans.
- **La Serbie, le précédent le plus proche** (Žegarac et autres c. Serbie,
  décision du 17 janvier 2023). La loi de 2014 est une tranche : rien sous
  25 000 dinars par mois, 22 % de la part entre 25 000 et 40 000, 25 % de la
  part au-dessus ; 61,2 % des retraités étaient sous le seuil
  (paragraphes 7 et 50). La Cour juge la méthode ni déraisonnable ni
  disproportionnée (paragraphe 102) et écarte la discrimination, parce que
  « pensioners with higher pensions also benefited from this exemption – as
  their pensions were reduced only in respect of the amounts above this
  minimum amount » (paragraphe 107). Mais elle retient que les requérants
  n'ont supporté que « temporarily what was a reasonable and commensurate
  reduction in their pensions, rather than a total suspension of their
  pensions or the permanent reduction of their pensions by a significant
  amount » (paragraphe 103) : la loi a duré un peu moins de quatre ans.

*Ce qu'un seuil y change.* Il règle le critère de la subsistance, que la
Cour regarde dans chaque affaire, et celui de la discrimination s'il a la
forme d'une tranche : c'est le motif même de Žegarac. Il ramène aussi la
baisse des pensions moyennes vers les ordres de grandeur que la Cour a
admis : 9 % à 1 500 €, 14 % à 2 000 €, avec un seuil à 1 050 €. Il ne règle
pas l'autre moitié du raisonnement, la durée. Les baisses portugaises et
serbe admises étaient temporaires. Seule Koufaki admet une baisse durable,
de 23 % sur un salaire (calcul), au nom d'un assainissement durable et dans
une crise aiguë. Aucune des décisions lues ne juge une baisse définitive de
15 à 30 % de pensions de retraite.

### Le Tribunal constitutionnel portugais

- **Admise** (arrêt 187/2013 du 5 avril 2013) : la contribution
  extraordinaire de solidarité, annuelle, sur les pensions à partir de
  1 350 €, jugée « appropriate and proportional », sans rien de
  confiscatoire. Reconduite en 2014 avec un seuil abaissé à 1 000 €, et
  admise encore (arrêt 572/2014).
- **Censurée, malgré un seuil** (arrêt 862/2013 du 19 décembre 2013, à
  l'unanimité) : la « convergence », une baisse de 10 % des pensions de la
  caisse des fonctionnaires au-dessus de 600 €. Le Tribunal écrit qu'aucune
  règle constitutionnelle n'interdit de réduire des pensions déjà
  reconnues, et que garantir le contenu minimal du droit à pension peut
  demander d'en baisser le montant. Il censure parce que la baisse ne
  touchait qu'un régime, qu'elle était sans terme, et qu'elle était « uma
  mera medida avulsa de redução de despesa », hors de toute réforme
  d'ensemble. Deux juges n'auraient censuré que ce qui frappait les plus
  modestes.
- **Censurée, malgré un plancher** (arrêt 575/2014 du 14 août 2014) : la
  « contribution de soutenabilité », 2 à 3,5 % de toutes les pensions
  publiques, avec une clause qui interdisait de faire passer une pension
  sous 1 000 €. Définitive, elle « merely cuts the amount of pensions
  without taking account of other relevant factors » ; il ne suffit pas
  d'invoquer la soutenabilité, il faut la démontrer.

*Ce qu'un seuil y change.* Peu. Le Portugal a censuré deux baisses qui
avaient un seuil ou un plancher, et admis une contribution qui en avait un :
ce qui les sépare est la durée, non le seuil. Les trois reproches faits aux
baisses censurées comptent davantage pour le programme : il touche tous les
régimes, ce qui lève le premier ; il recalcule chaque pension sur ses
cotisations au lieu de retirer un pourcentage, ce qui répond au troisième ;
il est définitif, et là-dessus le seuil ne dit rien. L'étude actuarielle
publiée du dépôt est la démonstration que l'arrêt 575/2014 demande.

### Ce que la relecture du chantier 2 corrige

Le chantier 2 citait ces précédents de mémoire. Trois précisions. Koufaki
et ADEDY ne juge la baisse d'aucune pension individuelle : la requérante
était en activité. Béláné Nagy porte sur une pension d'invalidité supprimée,
non sur une retraite. L'arrêt du Conseil d'État grec de 2015 n'a pas été
relu ; la décision Koufaki rapporte celui du 20 février 2012, qui rejetait
les recours.

## Ce que la note n'établit pas

- **Une baisse uniforme par sexe.** Le calcul prête à chaque femme la même
  baisse, à chaque homme la sienne. Le modèle ne dit pas si les petites
  pensions baissent plus que les grandes ; si c'est le cas, le seuil coûte
  davantage. Entre la baisse uniforme et la baisse par sexe, la part perdue
  bouge de 1,7 point pour la tranche, de 3 points pour le plancher.
- **Les seuls droits directs.** La distribution ne compte pas la réversion,
  que le scénario 6 garde (décision 16). Un seuil sur le total des pensions
  protégerait moins de monde : 4,4 millions de personnes touchent un droit
  dérivé (publié).
- **La forme de 2020.** La distribution est celle de 2020, déplacée d'un
  seul rapport jusqu'en 2026, 1,2085 (calcul). Elle met la pension moyenne
  de 2026 à 1 734 € ; la DREES publie 1 693 € fin 2024, majorations
  comprises (publié). Le niveau est peut-être trop haut de quelques pour
  cent ; chaque pour cent déplace d'un demi-point la part des retraités
  protégés (calcul).
- **La part perdue est tenue constante** de 2026 à 2070 : le seuil suit les
  prix, et le stock est supposé vieillir sans changer de forme. Les femmes,
  aux pensions plus basses, vivent plus longtemps : la part perdue monte
  sans doute avec le temps.
- **La baisse d'un coup en 2026**, comme la page Coût. Par cinquièmes
  (décision 87), le coût du seuil serait plus faible les quatre premières
  années.
- **Les lectures A et B** ajoutent à la dépense de chaque taux ce que le
  seuil coûte à 18 %. Contrôlé sur un coût calculé d'un coup, au taux de
  22,30 % et au seuil de 1 500 € : l'écart ne dépasse pas 0,002 point de PIB
  (calcul).
- **Les pensions qui montent** (1,5 % des retraités,
  `2026-11-09-pensions-qui-montent.md`) ne sont pas distinguées.

## Les calculs, en entier

**La distribution.** Les parts par tranche de 100 € de la pension brute de
droit direct, par sexe, fin 2020 (publié, `distribution_pensions.csv`) ;
chaque tranche uniforme. La tranche ouverte, au-delà de 4 500 €, est une
masse placée là où la moyenne retombe sur celle que la DREES publie :
1 122 € pour les femmes, 1 784 € pour les hommes, 1 435 € pour tous
(publié) ; soit 5 224 €, 5 792 € et 5 744 € (calcul). La part des femmes :
52,8 % (publié).

**De 2020 à 2026.** Les prix : × 1,1751 (dépôt). La pension moyenne par tête
du droit en vigueur, en euros constants : × 1,0284 (dépôt, la masse du
modèle hors réversion sur ses têtes). Ensemble : × 1,2085 (calcul). Pension
moyenne de 2026 : 1 356 € pour les femmes, 2 156 € pour les hommes, 1 734 €
pour tous (calcul).

**La baisse.** `f` = 0,7006 : les droits directs du scénario 6 sur ceux du
droit en vigueur en 2026, année où le stock en fait 99 % (dépôt). Par sexe,
comme la garantie du modèle : `f_F / f_H` = 0,8343 (dépôt), la moyenne
tenue ; d'où `f_F` = 0,6279 et `f_H` = 0,7526 (calcul). Baisse moyenne par
tête : 0,5278 × 0,3721 × 1 356 + 0,4722 × 0,2474 × 2 156 = 266 + 252 =
518 € par mois (calcul).

**La part perdue, tranche à 1 050 €.** Ce que la tranche laisse à chacun
est `(1 − f) × min(p, s)`. La moyenne de `min(p, 1 050)` vaut 837,3 € pour
les femmes, 957,9 € pour les hommes (calcul). Perdu par tête :
0,5278 × 0,3721 × 837,3 + 0,4722 × 0,2474 × 957,9 = 164,4 + 111,9 =
276,3 € par mois. Part perdue : 276,3 / 518,2 = 53,3 %. Pour 1 200 €, 1 500 €
et 1 563 €, les moyennes de `min(p, s)` sont 914,7 et 1 079,6 ; 1 041,8 et
1 302,7 ; 1 064,3 et 1 345,7.

**Le plancher et le lissage** : la même somme, avec `max(0, min(p, s) −
f × p)` pour le plancher (146,5 € et 33,7 € à 1 050 €, soit 18,0 %), et
`max(0, (1 − f) × p − 0,5 × (p − s))` au-dessus du seuil pour le lissage.

**Le taux qui garderait l'économie** : la baisse moyenne, divisée par la
moyenne de ce qui dépasse le seuil.

**Au modèle.** Relever le stock de la part perdue revient à multiplier ses
pensions du scénario 6 par `1 + x`, avec `x` = part perdue × `(1 − f) / f` :
0,2280, 0,2522, 0,2943 et 0,3021 pour la tranche. Le coût reçoit ce niveau
par son option d'indexation (`indexation_programme.py`, la voie « avant »,
`baisse_transition` = `−x`) ; à `x` = 0, il redonne le coût du modèle à
10⁻¹⁶ près. Tout le reste joue : la garantie, ses reprises, le solde, la
dette. Vérification pour 1 050 € : 0,2280 × 268,4 = 61,2 Md€.

**Les lectures de la décision 29** : `scripts/lectures_decision_29.py`, sa
convention de la page Coût, la part de TVA (0,23 point de PIB) et la LVT
centrale (1,3 point) ; la dépense de chaque taux reçoit ce que le seuil
ajoute à 18 %, garantie comprise, et les taux sont résolus de nouveau.

**La garantie de 2026** : le barème du modèle refait sur la distribution des
résidents (il redonne ses 5,54 millions d'ayants droit et ses 14,11 Md€),
puis appliqué aux pensions du droit en vigueur de 2026.

## Les sources

- DREES, *Les retraités et les retraites*, édition 2026, fiches 1 et 5 (le
  miroir du manifeste, empreinte vérifiée) ; EIR 2020, par les données
  certifiées `distribution_pensions.csv` et `pensions_residence.csv`.
- Conseil constitutionnel, décisions 2003-483 DC, 2013-682 DC, 2014-698 DC,
  2017-756 DC, 2018-776 DC et 2019-795 DC,
  `conseil-constitutionnel.fr/decision/<année>/<numéro>DC.htm`.
- CEDH, base HUDOC : Koufaki et ADEDY (001-120092), Da Conceição Mateus et
  Santos Januário (001-128106), da Silva Carvalho Rico (001-157567), Béláné
  Nagy (001-169917), Žegarac et autres (001-223123) ; fiche thématique
  « Mesures d'austérité ».
- Tribunal constitutionnel portugais, arrêts 187/2013, 862/2013, 572/2014 et
  575/2014 : le texte (`tribunalconstitucional.pt/tc/acordaos/<n>.html`) et
  le résumé officiel en anglais (`…/tc/en/acordaos/<n>s.html`).

## Ce que le propriétaire tranche

1. **Le principe.** Un seuil propre à la baisse, ou la garantie seule, qui
   est déjà un plancher mais se demande, attend 65 ans et se reprend sur la
   succession.
2. **La règle.** La tranche, la piste : la plus défendable en droit, la plus
   chère (53 à 71 % de la baisse perdue). Le plancher : trois fois moins
   cher, mais il écrase les pensions voisines du seuil. Le lissage, entre
   les deux. *Proposé : le lissage à 50 % ; il protège les mêmes retraités
   que la tranche, garde l'ordre des pensions, et coûte 34 Md€ en 2026 au
   lieu de 58 pour un seuil à 1 050 €.*
3. **Le niveau.** 1 050 €, 1 200 €, 1 500 € ou la médiane. *Proposé :
   1 050 €, le niveau de la garantie ; sous la tranche, 1 200 € coûte 6 Md€
   de plus en 2026, 1 500 € 17 Md€ de plus.*
4. **Qui paie.** Sous la lecture A, les cotisants et la réserve, à parts
   égales ; sous la lecture B, les cotisants seuls ; à 18 %, la dette.
5. **L'assiette du seuil.** Les seuls droits directs, ou le total des
   pensions de la personne, réversion comprise, comme les lois de 2014 et de
   2019 ; et s'il vaut pour les retraités qui résident à l'étranger.
6. **L'articulation avec la garantie.** Si la garantie est servie d'office
   (décision 20), elle paie déjà la moitié d'un plancher à 1 050 €. Le seuil
   la remplace-t-il pour le stock, et ce qu'il laisse échappe-t-il à la
   reprise sur succession (décision 30) ?
7. **La relecture par un spécialiste de droit public**, avant toute phrase
   publique sur ce que le seuil garantit devant les juges.
