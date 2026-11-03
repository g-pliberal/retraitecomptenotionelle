# Relecture de la limite de la grille des marins d'avant 2008 (file M1-bis)

File R-M1-bis, le 3 novembre 2026. Il s'agit d'une relecture indépendante du commit 8cf8615
(session M1-bis, note `2026-11-03-limite-de-la-grille-des-marins.md`), qui déclare
la limite de la grille des salaires forfaitaires des marins d'avant 2008. Chaque
texte a été rouvert ici, sans rien reprendre de la session ni de mémoire, dans les
index de la DILA récupérés et mis à jour : JORF à l'incrément du 3 novembre 2026
(20261103-002311), LEGI à celui du 2 novembre (20261102-213929), aucun incrément
depuis. Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** Les citations sont **conformes**, mot pour mot. Chaque chiffre de la
limite se refait à la main depuis les textes et les données du modèle, à trois
centimes d'arrondi près. Les trois tests sont verts, y compris sous la garde des
présomptions. Le commit ne touche ni le code ni un témoin. Les six écarts de R-M1
sont corrigés ou déclarés. **Écarts relevés :**

- **Un moyen** (point 3) : le 14,5 % et le 12,7 % se mesurent sur la grille du
  1er janvier 1995. Or l'arrêté du 30 juin 1995, « portant majoration », la modifie
  « pour compter du 1er juillet 1995 ». Le « 12,7 % au plus » d'un départ en 1995
  ne vaut donc que jusqu'au 30 juin, et la fiche ne dit pas ce sens.
- **Deux faibles.** La ligne de `docs/limites/` dit « sous-estimé », sans la
  condition que la fiche pose (point 6). Le deuxième test prend le plafond au code,
  au lieu de le poser ; refait ici, il est exact (point 4).
- **Deux négligeables.** Trois résultats ont un centime d'écart avec les facteurs
  arrondis que la note écrit (point 2). La phrase citée du décret n° 2001-1203 est
  un paragraphe d'explication, et non un article (point 1).

## 1. Les citations, mot pour mot

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| Arrêté du 29 décembre 1994, art. 1er | JORFARTI000001974748 (publié le 5 janvier 1995) | « Les salaires forfaitaires servant de base au calcul des contributions des armateurs, des cotisations et des pensions des marins du commerce, de la pêche et de la plaisance sont modifiés, pour compter du 1er janvier 1995, conformément au tableau ci-joint. » : **conforme**, la note marquant ce qu'elle élide. Le tableau, JORFARTI000001344200, ne porte que « BASE DE CALCUL DES CONTRIBUTIONS, » : **conforme**. |
| Arrêté du 31 janvier 1995, art. 1er | JORFARTI000002373607 (publié le 17 février 1995) | Il modifie « Le tableau figurant à l'article 1er de l'arrêté du 29 décembre 1994 » ; « Pour le salaire forfaitaire par mois de la 13e catégorie, au lieu de: << 14 773,03 >>, lire: << 14 733,03 >>. » : **conforme**. Aucune unité n'y est écrite : **conforme** à ce que dit la note. |
| Arrêté du 30 juin 1995 | JORFARTI000001014013, JORFARTI000001014119 (publiés le 16 juillet 1995) | Le titre, « portant majoration des salaires forfaitaires » ; « pour compter du 1er juillet 1995 » ; « Vous pouvez consulter le tableau dans le JO no 0164 du 16/07/95 Page 10596 » : **conforme**. Ses deux autres articles, le visa (JORFARTI000001977662) et l'exécution (JORFARTI000001594620), n'ont aucun montant. |
| Arrêté du 2 janvier 2006, art. 1 | JORFARTI000001105232 (publié le 7 janvier 2006) | « sont modifiés, pour compter du 1er janvier 2006, conformément au tableau ci-dessous : » : **conforme**. Son tableau, JORFARTI000001490692, ne porte que son titre : **conforme**. |
| Son rectificatif | JORFARTI000001490715 (publié le 21 janvier 2006) | « Rectificatif au Journal officiel du 7 janvier 2006, […] article 1er, dans le tableau, 2e sous-colonne, en ce qui concerne la 10e catégorie, au lieu de : « 25 243,53 », lire : « 25 243,83 ». » : **conforme**, et la date de publication aussi. |
| Arrêté du 26 décembre 2006 | JORFARTI000002473548, JORFARTI000002075984 | « pour compter du 1er janvier 2007 » ; le second article ne porte que le titre, sans tableau : **conforme**. |
| Arrêté du 31 décembre 2007, art. 1 | JORFARTI000017964781 | « pour compter du 1er janvier 2008 » ; « CATÉGORIES SALAIRES FORFAITAIRES Par an Par jour », « 10 25 980,90 72,17 », « 13 33 126,69 », « 20 59 899,76 » : **conforme**. Ce sont aussi les montants de `regimes/salaires_forfaitaires.csv`. |
| Arrêté du 19 mars 2026, art. 1 | JORFARTI000053743024 | « 13 42 510,19 », « 20 76 867,05 » : **conforme**. |
| Décret n° 2001-1203 | JORFTEXT000000580421 | « les références monétaires aux unités nationales qui figurent dans les textes réglementaires devront être lues à compter du 1er janvier 2002 comme des références à l'euro, en appliquant le taux de conversion de 6,55957 F pour un euro, avec arrondissement à la deuxième décimale » : **conforme** ; « Vu le règlement (CE) no 2866/98 du 31 décembre 1998 » : **conforme**. **Négligeable** : dans l'index, la phrase vient après les signatures et la mention « Rectificatif au JO du 23-02-2002 page 3475 ». C'est un paragraphe d'explication, et non un article : le taux est celui du règlement que le décret vise. La conversion n'en change pas. |
| Décret n° 85-1148, art. 3, au 1er janvier 1995 | LEGIARTI000006454440 (du 1er décembre 1994 au 18 février 1995) | « afférents à l'indice 100 majoré et soumis aux retenues pour pension est fixée à 31 422 F à compter du 1er décembre 1994 » : **conforme**. |
| Le même décret, art. 7, au 1er janvier 1995 | LEGIARTI000006454542 (du 1er août 1991 au 20 février 1998) | « le traitement afférent à l'indice majoré 158 (indice brut 100) » : **conforme**. |
| Art. 3 et 7 au 1er janvier 2005, pour le plafond de 2005 | LEGIARTI000006454455 (du 1er janvier 2004 au 18 janvier 2005) ; LEGIARTI000006454552 (du 1er juillet 2004 au 18 janvier 2005) | « 5 275,58 Euros à compter du 1er janvier 2004 » ; « l'indice majoré 174 (indice brut 100) » : les deux facteurs du plafond de 2005 sont **conformes**. |

Les autres arrêtés de 1994, 1995 et 2006 que l'index porte ont été cherchés :
`"salaires forfaitaires" marins`, publiés en 1994, 1995, 2005 et 2006. Il n'y en a
pas d'autre. Il n'y a donc pas de majoration en cours d'année 2006 ; il y en a
une, celle du 1er juillet 1995, en 1995 (point 3).

## 2. Les chiffres refaits à la main

Ce que le modèle prend, c'est le forfait de 2008 de l'arrêté multiplié par le
rapport des salaires moyens du modèle. Ces salaires moyens ont été relus ici :
1995, 20 944,65 € ; 2006, 28 043,44 € ; 2008, 29 486,72 € ; 1968, 2 225,27 € ;
1980, 9 466,62 € ; 1985, 14 944,37 € ; 2005, 27 153,62 €. Le point vient de
`legislation/point_indice_fonction_publique.csv`, l'indice de
`legislation/indice_100_fonction_publique.csv`.

| Chiffre de la note et de la fiche | Refait | Constat |
|---|---|---|
| 14 733,03 × 12 = 176 796,36 F ; / 6,55957 = 26 952,43 € | 176 796,36 ; 26 952,431 | conforme |
| 33 126,69 × 0,710308 = 23 530,15 € | facteur 0,7103079 ; 23 530,149 | conforme |
| 1,14544 (+14,5 %) ; 0,87303 (−12,7 %) | 1,145442 ; 0,873025 | conforme |
| 25 980,90 × 0,951054 = 24 709,23 € | facteur 0,9510535 ; 24 709,226 aux salaires moyens non arrondis | conforme. **Négligeable** : avec les chiffres que la note écrit, 25 980,90 × 28 043,44 / 29 486,72 = 24 709,22, et 25 980,90 × 0,951054 = 24 709,24 |
| 1,02164 (+2,2 %) ; −2,1 % | 1,021636 ; 2,118 % | conforme |
| 59 899,76 / 33 126,69 = 1,808202 ; 76 867,05 / 42 510,19 = 1,808203 | 1,8082024 ; 1,8082029 | conforme |
| 8 × 158 × 314,22 = 397 174,08 F = 60 548,80 € | 397 174,08 ; 60 548,798 | conforme. Au point du modèle (47,9025 €), le plafond vaut 60 548,76 €, et 80,5 % n'en bouge pas |
| 59 899,76 × 0,710308 = 42 547,27 € | 42 547,272 | conforme |
| 26 952,43 × 1,808202 = 48 735,45 € | 48 735,451 sans arrondi | conforme. **Négligeable** : avec les deux facteurs arrondis qu'écrit la note, on trouve 48 735,44 |
| 1 − 42 547,27 / 48 735,45 = 12,7 % | 12,697 %, qui est aussi 1 − 1 / 1,14544 : la vingtième suit la treizième par construction | conforme, sous l'hypothèse posée (point 3) |
| 48 735,45 / 60 548,80 = 80,5 % | 80,49 % | conforme |
| 2005 : 8 × 174 × 52,7558 = 73 436,07 € ; 55 160,27 € ; 75,11 % | 73 436,074 ; 55 160,266 ; 75,113 % | conforme. Les deux facteurs du plafond sont au droit (point 1) |
| 1985 : 65,6 % | 30 358,21 / (8 × 150 × 38,5544 = 46 265,28) = 65,62 % | conforme. C'est le point du 1er janvier, que la fiche déclare : au point du droit, 26 428 F (LEGIARTI000006454423), on trouve 62,8 % |
| Le plus haut de 1985 à 2007 : 2005 | refait année par année (1er décembre en 1985, 1er janvier ensuite) : de 65,62 % (1985) à 75,11 % (2005) ; 73,59 % en 2004, 71,28 % en 2006 | conforme |
| 75,11 % × 1,14544 = 86,04 %, « sous 86,1 % » ; 1 / 0,7511 = 1,3313 ; 1,3313 / 1,14544 = 1,162 | 86,038 % ; 1,33132 ; 1,16228 | conforme |
| 4 520,45 / (8 × 7,3907) = 76,455 ; 19 230,64 / (8 × 23,3948) = 102,751 ; × 1,14544 : 87,57 et 117,69 | 76,4550 ; 102,7506 ; 87,575 ; 117,695 | conforme. **Négligeable** : avec le salaire moyen de 1980 arrondi au centime, la vingtième de 1980 vaut 19 230,63 |

## 3. Le second semestre 1995 : « 12,7 % au plus » n'est pas établi (écart moyen)

Le seul montant réel de 1995, « 14 733,03 » F par mois, est celui du tableau de
l'arrêté du 29 décembre 1994. Ce tableau vaut « pour compter du 1er janvier 1995 ».
L'arrêté du 30 juin 1995, « portant majoration des salaires forfaitaires servant de
base au calcul des contributions des armateurs, des cotisations et des pensions »,
le remplace « pour compter du 1er juillet 1995 » (JORFARTI000001014013). Son tableau
n'est pas dans l'index. Le modèle, lui, n'a qu'une grille pour toute l'année 1995.

Sur le second semestre 1995, le forfait réel dépasse donc celui du 1er janvier : le
titre de l'arrêté dit une majoration, mais son montant n'est pas lu. L'écart du
modèle y est donc plus grand que 14,5 % sur la treizième, et que 12,7 % sur la
vingtième ainsi estimée. Ce n'est pas lu, et non vérifié, faute de texte. Trois
phrases s'écartent de ce que l'arrêté implique :

- « un salaire de référence et une pension plus bas que le droit de 12,7 % au plus
  pour le marin des plus hautes catégories qui part en 1995 » (fiche, `effet` de
  l'approximation des arrêtés annuels ; note ; journal de M1-bis). R. 11 prend
  « le salaire forfaitaire correspondant […] à la catégorie »
  (LEGIARTI000006791987), et l'arrêté du 30 juin 1995 sert de base aux
  « pensions » depuis le 1er juillet. Sous l'hypothèse même de la fiche, un départ
  à partir du 1er juillet 1995 dépasse donc 12,7 %, d'un montant inconnu.
- Les cotisations du second semestre 1995, assises sur la grille majorée, sont
  sous-estimées de plus de 12,7 % au-delà de la vingtième. Ni la fiche (« le
  forfait de chaque année d'avant 2008 fait l'assiette des cotisations du
  marin ») ni le journal de M1-bis (« les cotisations portées au compte notionnel
  de même ») ne le disent.
- « l'écart de 1995 — le plus grand des deux » est exact : c'est le plus grand des
  deux points mesurés. En revanche, « la marge restant voisine de 14 % sous l'écart
  le plus défavorable » (la note, question au propriétaire) en dit trop : la grille
  relevée de 14,5 % n'est pas la plus défavorable que permettent les textes de 1995.

La fiche cite l'arrêté du 30 juin 1995 parmi ce que l'index « ne dit pas ». Elle ne
dit ni que c'est une majoration, ni ce qu'elle fait aux deux chiffres. Il faudrait
écrire : « 12,7 % pour un départ du 1er janvier au 30 juin 1995 ; davantage
ensuite, la grille du 1er juillet 1995 étant majorée, d'un montant non lu ». Aucun
calcul du modèle n'en dépend. La conclusion sur le plafond reste ce que la fiche en
dit : très probable, non prouvée.

## 4. Les trois tests

- **Verts** : `tests/test_marins.py`, 53 réussis ; sous
  `PRESOMPTIONS_DECALEES=1`, 53 réussis.
- **Vus rouges sur la fiche de 57aa927** : c'est ce que dit la note, et le diff le
  confirme. Chaque test cherche une phrase que 8cf8615 ajoute : « 2e sous-colonne »,
  « sous 86,1 % du plafond de 1985 à 2007 (2005) », « monteraient de 76,5 et 102,8
  à 87,6 et 117,7 ». Je ne l'ai pas rejoué.
- **D'où viennent les valeurs.**
  - Les montants réels viennent des textes : `14733.03 * 12 / 6.55957` et
    `25243.83`, avec leurs identifiants. Le plafond de 1995 aussi :
    `8 * 158 * 314.22 / 6.55957`.
  - Le forfait du modèle est posé dans le test, à partir du forfait de 2008 du CSV
    (celui de l'arrêté) et du salaire moyen du modèle. On le confronte ensuite à ce
    que rend `grilles.forfait`. Puisqu'il s'agit de ce que le modèle prend, c'est la
    bonne source.
  - La structure vient des grilles de 2008 et de 2026, lues ; les seuils d'avant
    1985 du point et du forfait posés : **conforme**.
- **Écart faible** : le deuxième test prend le plafond de chaque année de 1985 à
  2007 au code (`liquider.plafond_du_salaire_de_reference`), au lieu de le poser
  (8 × indice × point, depuis les deux CSV). Ce sont donc le code et le texte de la
  fiche que le test lie, et non la fiche et le droit. Refaits ici à la main, les
  vingt-trois rapports sont ceux du code : le plus haut en 2005 (75,11 %), le plus
  bas en 1985 (65,62 %). La valeur est juste ; le test ne la tiendrait pas si le
  code changeait avec la fiche.
- **Le commit ne touche ni code ni témoin.** Il touche cinq fichiers : la fiche, la
  note, le journal, `docs/limites/4-regimes-incomplets.md` et `tests/test_marins.py`.
  « Aucune règle de calcul ne change » : **conforme**. Depuis, seul 7621be3
  (action 131) a touché `docs/limites/4-regimes-incomplets.md`, et pas la ligne des
  marins. 8cf8615 est sur `origin/main`.
- `python -m pytest -m rapide` : 4 242 réussis, 6 sautés. Sous la garde des
  présomptions : 4 044 réussis, 204 sautés. Aucun échec.

## 5. Les écarts de R-M1

| Écart de R-M1 | Constat |
|---|---|
| Moyen, point 4 : « aucune catégorie de 1985 à 2026 », non prouvé avant 2008 | **Corrigé.** La fiche dit : « nul de 2008 à 2026, prouvé sur les grilles publiées […] de 1985 à 2007 […] très probable, non démontré » ; l'effet d'ensemble dit : « de 1985 à 2007, rien de ce que le modèle calcule n'est abattu, mais sur une grille qu'il estime ». Le journal de M1 restreint l'affirmation (« de 2008 à 2026, sur les grilles publiées »), et la note de M1 a sa section « Après la relecture R-M1 ». Le récit de M1 garde « sous 75,1 % » (ligne 175) : c'est un récit, gelé, et la correction (« au plus 75,1 % ») est dans la fiche, la note et le journal de M1-bis. **Conforme** à la règle des récits. |
| Faible, point 5 : le paquet absent du commit | **Déclaré** dans la note de M1 (« Le paquet n'était pas dans le commit »). |
| Faible, point 6 : la limite absente de `docs/limites/` | **Corrigé.** La ligne des marins dit « le traitement de l'indice 100 d'avant le 5 novembre 1985 », l'abattement de R. 11, 3°, « au point du 1er janvier », et désormais le sens de l'erreur de la grille. |
| Faible, point 2 : la lettre de l'article 7 contre le barème A | **Déclaré** dans la fiche (approximation « décret n° 85-1148, article 7 ; décret n° 82-1105, barème A »). |
| Négligeable, point 3 : 98 298,14 € contre 98 298,16 € | **Déclaré** dans la fiche (« le plafond de 2026 vaut 98 298,14 € au lieu de 98 298,16 € »). |
| Négligeable, point 1 : la fin de l'article 1er du décret n° 48-1108 | **Corrigé** : « rédaction en vigueur jusqu'au 25 avril 2008 ». |
| Hors tâche : −14,5 % et −2,2 % sur la grille estimée | **Déclaré** : c'est l'objet de 8cf8615. |

## 6. Ce que la limite déclare, ce qui reste non vérifié

**Dans la fiche : conforme.** L'écart dit ce que l'index garde, cité, et ce qu'il ne
dit pas : la vingtième d'aucune année d'avant 2008, l'écart des autres années, la
structure, la grille du 1er juillet 1995. L'unité de la sous-colonne de 2006 est
déduite de sa grandeur, et dite déduite. Les sources nomment ce qui n'est pas lu :
les tableaux des arrêtés de 1985 à 2007, au Journal officiel imprimé. Une question
est posée au propriétaire. Ces barèmes n'ont pas été cherchés ici, comme demandé.
Le 403 de Légifrance n'a pas été rejoué.

**Dans `docs/limites/4-regimes-incomplets.md` : écart faible.** La colonne du sens
dit que la grille « paraît trop basse », puis que « le forfait des plus hautes
catégories d'avant 2008 […] en est sous-estimé », sans condition. Or l'index ne
porte la vingtième d'aucune année d'avant 2008, et les deux montants réels sont une
treizième et une dixième. La fiche, elle, écrit « si elle suit l'écart de la
treizième et la structure de 2008 ». Il faudrait la même condition, par exemple
« paraît en être sous-estimé ». La ligne ne porte aucun chiffre nu : **conforme** au
régime de l'état.

## Ce qui attend

- Écrire, dans la fiche, la note et le journal de M1-bis, que le 12,7 % et le
  14,5 % valent du 1er janvier au 30 juin 1995, et que l'écart est plus grand
  ensuite, la grille du 1er juillet 1995 étant majorée d'un montant non lu (point 3).
- Donner à la ligne des limites la condition de la fiche (point 6). Poser dans le
  deuxième test le plafond de chaque année, de 1985 à 2007, depuis les deux séries,
  au lieu de le prendre au code (point 4).
- La question au propriétaire demeure : les tableaux des arrêtés de 1985 à 2007, au
  Journal officiel imprimé. Celui du 30 juin 1995 dirait de combien le second
  semestre 1995 s'écarte.
