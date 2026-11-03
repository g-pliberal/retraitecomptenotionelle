# Les retouches de la relecture R-M1-ter : 1994 déclaré, les points gardés sans l'index

File M1-quater, le 3 novembre 2026. La relecture R-M1-ter (commit 265b237, note
`2026-11-03-relecture-corrections-r-m1-bis.md`) juge conforme le travail de
M1-ter (commits a66e323 et 8a0f035) et relève trois écarts faibles et deux
négligeables. Chacun est repris ici, le texte rouvert dans les index de la DILA,
récupérés puis mis à jour : LEGI à l'incrément du 2 novembre 2026
(20261102-213929), JORF à celui du 3 novembre (20261103-002311), aucun depuis.
Aucun calcul du modèle ne change : ni règle, ni donnée lue par le paquet.

## 1. 1994 : les deux points de l'article 3 (faible)

**Le texte.** La rédaction de l'article 3 du décret n° 85-1148 en vigueur du
21 décembre 1993 au 19 juillet 1994 (LEGIARTI000006454438), relue en entier,
fixe la valeur annuelle du traitement « afférents à l'indice 100 majoré et
soumis aux retenues pour pension » à « 30 926 F à compter du 1er janvier 1994 »,
puis : « Par dérogation à l'alinéa précédent, la valeur annuelle du traitement
et de la solde afférents à l'indice 100 majoré et soumis aux retenues pour
pension est fixée, pour les agents dont l'indice majoré est inférieur ou égal à
275, à 31 018 F à compter du 1er janvier 1994. » La rédaction suivante, du
19 juillet au 1er décembre 1994 (LEGIARTI000006454439), garde les deux
alinéas, à 31 080 F et 31 173 F « à compter du 1er août 1994 ». Des quarante-six
rédactions de l'article 3 que l'index garde, ces deux-là sont les seules à porter
une dérogation. L'article 7 (LEGIARTI000006454542, du 1er août 1991) constitue
le traitement de l'indice 100 par « le traitement afférent à l'indice majoré
158 (indice brut 100) », sans dire quel alinéa de l'article 3 le paie. Le texte
ne tranche pas ; la valeur n'est donc pas changée.

**Calcul posé à la main**, au 1er janvier 1994, à l'indice majoré 158 :

- huit fois l'indice 100 : 8 × 158 = 1 264 points ;
- à l'alinéa général, 309,26 F le point : 1 264 × 309,26 = 379 200 + 11 704,64
  = 390 904,64 F. Comme 6,55957 × 59 593,03 = 390 904,6518 F, qui dépasse de
  0,0118 F, soit 0,0018 €, le plafond vaut 59 593,0282 €, soit **59 593,03 €** ;
- à la dérogation, 310,18 F le point : 1 264 × 310,18 = 391 840 + 227,52
  = 392 067,52 F. Comme 6,55957 × 59 770,31 = 392 067,5324 F, qui dépasse de
  0,0124 F, soit 0,0019 €, le plafond vaut 59 770,3081 €, soit **59 770,31 €** ;
- au modèle, le point de la série, 47,2165 € : 1 264 × 47,2165 = 59 408
  + 273,656 = **59 681,656 €**. Les deux points du texte valent 309,26 / 6,55957
  = 47,14638 € et 310,18 / 6,55957 = 47,28664 € ; leur moyenne, 47,21651 €,
  arrondie au dix-millième, est 47,2165 € : la série porte la moyenne ;
- les écarts : 59 681,656 − 59 593,0282 = 88,6278 €, soit 88,63 €, et
  59 770,3081 − 59 681,656 = 88,6521 €, soit 88,65 €. Le modèle s'écarte donc de
  **88,65 € au plus** de la valeur que le droit retiendra, soit
  88,6521 / 59 681,656 = 0,1485 %, 0,15 % ;
- au salaire de référence : pour un forfait S au-dessus du plafond P, la portion
  au-delà ne compte que pour moitié, et le salaire de référence vaut
  P + (S − P) / 2 = (S + P) / 2. Que P bouge de d, il bouge de d / 2 :
  88,6521 / 2 = 44,3261, soit **44,33 € par an au plus**. Pour un forfait entre
  deux plafonds, l'écart, (S − P) / 2, est plus petit encore.

Les deux chiffres de R-M1-ter, 88,65 € et 44,33 €, sont **confirmés**.

Du 1er août au 30 novembre 1994, les deux points relevés donnent 59 889,78 € et
60 068,99 € : le plafond du modèle, qui garde le point du 1er janvier, est sous
l'un et l'autre, et l'écart tient alors à cette convention, déjà déclarée.

**Ce qui est fait.** La fiche `marins_salaire_de_reference` porte une
approximation de plus, sur la version `code_de_1968`, qui couvre 1994. Elle dit la
convention du modèle, les deux alinéas cités, les trois plafonds, l'écart au plus
sur le plafond et sur le salaire de référence, et que la vingtième catégorie de la
grille du modèle reste sous les deux plafonds. Aucune pension calculée n'en change
donc. S'y ajoutent une source et une ligne d'historique. Le test
`test_en_1994_le_texte_ne_dit_pas_lequel_des_deux_points_fait_le_plafond_et_la_fiche_le_dit`
recalcule ces chiffres, les compare aux valeurs posées ici à la main, relit les deux
rédactions quand l'index est là, et exige que la fiche les écrive. Il a d'abord
échoué, la fiche ne déclarant rien, puis il est passé.

L'en-tête de la série (`legislation/point_indice_fonction_publique.csv`) reste
hors de cette tâche. La ligne des marins de `docs/limites/4-regimes-incomplets.md`
dit « au point du 1er janvier » et renvoie à la fiche : elle n'est pas touchée.

## 2. Le deuxième test, juge sans l'index (faible)

Les vingt-trois points recopiés du texte sont déjà écrits dans le test, avec
leur identifiant LEGIARTI (`POINT_DE_L_ARTICLE_3`). Ce qui manquait, sans l'index,
c'était une copie indépendante à laquelle les confronter. Le test neuf,
`test_sans_l_index_chaque_point_se_recoupe_dans_la_serie_que_le_modele_lit`, la
trouve dans la série que le modèle lit, au dix-millième d'euro où elle s'arrondit.
Il vérifie aussi que le plafond du modèle, ce jour-là, vaut huit fois l'indice de
l'article 7 fois ce point. Deux exceptions sont déclarées :

- le 1er décembre 1985, la série porte le point du 1er janvier 1985, d'avant le
  décret ; ce jour se recoupe par le 1er janvier 1986, qui relève de la même
  rédaction (LEGIARTI000006454423) ;
- en 1994, la série porte la moyenne des deux points (point 1).

Les vingt-trois relectures dans LEGI sont relancées ici, avec l'index : toutes
passent. Les vingt-trois rédactions sont celles que R-M1-ter liste. Pour voir le
test mordre, l'index LEGI a été mis de côté, comme sur GitHub, puis chaque
valeur faussée a été rétablie :

| Ce qui est faussé, sans l'index | Ce qui échoue |
|---|---|
| le point de 1993 pris à la rédaction de février 1993 (…437, « 30 711 F »), l'essai de R-M1-ter | le recoupement : 46,8186 € pour 46,0244 € |
| la série de 2003, mise à 52,4993 € | le recoupement : 52,4933 € pour 52,4993 € |
| la dérogation de 1994, mise à 31 080 F | le recoupement (47,2638 € pour 47,2165 €), et le test de 1994 |
| le point de 1994 pris à la dérogation, 31 018 F, l'essai de R-M1-ter | le test de 1994 |

Sans l'index, `tests/test_marins.py` donne 35 tests verts et 43 sautés : les
vingt-trois relectures de l'article 3 et les vingt de l'article 7. Le fichier
`.github/workflows/tests.yml` n'est pas touché, la question de l'index sur
GitHub étant posée au propriétaire.

## 3. L'arrêté du 2 août 1995 (faible)

La recherche plein texte `"salaires forfaitaires" marins` a été refaite dans le
JORF, sur 1995 et 1996. Elle rend dix-neuf documents. Parmi eux, l'**arrêté du
2 août 1995** « portant classement des officiers des navires transportant des
passagers, armés au long cours ou au cabotage, qui ne sont pas visés par
l'article 3 bis du décret no 52-540 du 7 mai 1952 modifié » (JORFTEXT000000554960,
publié le 30 août 1995). Je l'ai ouvert. L'index n'en porte aucun article : seulement
ses visas (L. 42 du code des marins, articles 3 et 3 bis du décret n° 52-540,
l'avis du conseil supérieur de l'ENIM du 17 juin 1994), ses signatures et une
analyse : « ILS SONT CLASSES EN FONCTION DE LA PUISSANCE ET DE LA JAUGE BRUTE DE
CES NAVIRES,CONFORMEMENT AU TABLEAU Y VISE. LE PRESENT ARRETE EST APPLICABLE AUX
NAVIRES VISES A L'ART. 1 ENTRANT EN FLOTTE POSTERIEUREMENT AU 30-08-1995. » Il
ne porte aucun montant.

La note de M1-ter dit que la recherche « ne donne pas d'autre arrêté » que ceux du
29 décembre 1994, du 31 janvier 1995, du 30 juin 1995 et du 30 décembre 1995.
**Erratum** : elle donne aussi celui-là, un arrêté de classement sans grille. La
conclusion tient : aucune autre grille. La source de la fiche le nomme désormais.
Un renvoi daté est ajouté au bout de la note de M1-ter, sans en rien récrire.

## 4. Les négligeables

**« Plus de 27,49 % »** (note de M1-ter, section 1). Le plafond du 1er novembre
1995 se calcule ainsi : 8 × 158 × 322,44 F = 407 564,16 F, soit 62 132,7557 €.
La vingtième estimée vaut 26 952,4313 × 59 899,76 / 33 126,69 = 48 735,4507 €.
Leur rapport, 1,2748986, donne un seuil de 27,4899 %. Une majoration de 27,4899 %
suffit donc, sans atteindre 27,49 %. **Erratum** : il faut lire « plus de
27,48 % », condition nécessaire arrondie vers le bas. Ce chiffre n'est que dans la
note ; la fiche dit « plus haut au 1er novembre », sans chiffre.

**La borne du semestre.** Le premier test vérifiait que « du 1er janvier au
30 juin 1995 » était écrit quelque part dans la fiche. Il exige désormais la borne
à chacune de ses trois places :

- « cette grille ne vaut que du 1er janvier au 30 juin 1995 » ;
- après « 14,5 % plus haut » ;
- après « de 12,7 % au plus pour le marin des plus hautes catégories dont la
  pension prend effet ».

Chacune ôtée tour à tour de la fiche, le test échoue ; avant, ôter la première ne
faisait rien échouer.

## Relevé en chemin

L'article 7 a, lui aussi, une dérogation en 1991 (LEGIARTI000006454542) : il
remplace l'indice 158 par l'indice majoré 202 (indice brut 175) « dans les cas
suivants ». La liste, lue en entier, comprend :

- des articles du code des pensions civiles et militaires de retraite ;
- le décret n° 66-809 ;
- l'article 65 de la loi du 11 janvier 1984 ;
- le décret du 9 septembre 1965 de la CNRACL ;
- le décret n° 49-1416 ;
- l'article R. 417-9 du code des communes.

Le code des pensions de retraite des marins n'y est pas : l'indice 158 tient.

## Les tests

`tests/test_marins.py` : 78 tests verts, avec l'index et sous
`PRESOMPTIONS_DECALEES=1` ; 35 verts et 43 sautés sans lui. `python -m pytest
-m rapide` : 4 271 verts, 6 sautés ; sous `PRESOMPTIONS_DECALEES=1` : 4 073
verts, 204 sautés. Les tests qui lisent les notes et le journal de veille, et
celui de la conservation : 1 234 verts, 5 sautés. `construire_donnees.py` ne
change rien.

## Sources ouvertes

- Index LEGI, à jour du 2 novembre 2026 : les vingt-trois rédactions de
  l'article 3 du décret n° 85-1148 que nomme `POINT_DE_L_ARTICLE_3`, de
  LEGIARTI000006454423 à LEGIARTI000006454459, avec leurs dates. J'ai lu en
  entier LEGIARTI000006454437, …438, …439 et l'article 7 LEGIARTI000006454542,
  et cherché la dérogation dans les quarante-six rédactions de l'article 3.
- Index JORF, à jour du 3 novembre 2026 : JORFTEXT000000554960 et la recherche
  `"salaires forfaitaires" marins` de 1995 et 1996.
- Dans le dépôt : `legislation/point_indice_fonction_publique.csv` de 1985 à
  2007 ; le plafond du modèle (`liquider.plafond_du_salaire_de_reference`) en
  janvier et en août 1994, et le 1er janvier de chaque année de 1986 à 2007.
