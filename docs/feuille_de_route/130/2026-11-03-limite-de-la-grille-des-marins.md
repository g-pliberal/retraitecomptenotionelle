# La limite de la grille des marins d'avant 2008, déclarée

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la file
M1 de corriger ce que la relecture indépendante
(`2026-11-03-relecture-abattement-des-marins.md`) a trouvé dans l'abattement du
salaire des marins (commit e5dd612), puis d'écrire, comme limite déclarée de la
grille des salaires forfaitaires, que la grille d'avant 2008 est estimée et
paraît trop basse, avec ses sources et son effet possible sur les pensions.
Pendant la session, elle fait savoir que la session M1 d'origine a déjà pris la
relecture en compte (57aa927 : l'affirmation restreinte à 2008-2026, la lettre
de l'article 7 contre le barème A, l'arrondi du barème B, la note datée, la
ligne des limites, un test) : ne reste que la limite de la grille. C'est tout ce
que cette étape publie ; ce qu'elle avait écrit avant le message, et que
57aa927 couvre, est abandonné.

## Ce qui a été relu

Chaque source rouverte ici, dans les index de la DILA récupérés et mis à jour
(JORF à l'incrément du 3 novembre 2026, 20261103-002311 ; LEGI à celui du
2 novembre, aucun depuis) :

| Texte | Identifiant | Ce qu'il dit, mot pour mot |
|---|---|---|
| Arrêté du 29 décembre 1994, article 1er | JORFARTI000001974748 | « Les salaires forfaitaires […] sont modifiés, pour compter du 1er janvier 1995, conformément au tableau ci-joint. » Le tableau (JORFARTI000001344200) n'est dans l'index que par son titre, « BASE DE CALCUL DES CONTRIBUTIONS, » |
| Arrêté du 31 janvier 1995, article 1er | JORFARTI000002373607 | « Pour le salaire forfaitaire par mois de la 13e catégorie, au lieu de: << 14 773,03 >>, lire: << 14 733,03 >>. » |
| Arrêté du 30 juin 1995 | JORFARTI000001014013, JORFARTI000001014119 | « pour compter du 1er juillet 1995 » ; « Vous pouvez consulter le tableau dans le JO no 0164 du 16/07/95 Page 10596 » |
| Arrêté du 2 janvier 2006, article 1 | JORFARTI000001105232 | « sont modifiés, pour compter du 1er janvier 2006, conformément au tableau ci-dessous : » ; le tableau (JORFARTI000001490692) n'est dans l'index que par son titre |
| Son rectificatif, publié le 21 janvier 2006 | JORFARTI000001490715 | « article 1er, dans le tableau, 2e sous-colonne, en ce qui concerne la 10e catégorie, au lieu de : « 25 243,53 », lire : « 25 243,83 ». » |
| Arrêté du 26 décembre 2006 | JORFARTI000002473548, JORFARTI000002075984 | « pour compter du 1er janvier 2007 » ; tableau absent |
| Arrêté du 31 décembre 2007, article 1 | JORFARTI000017964781 | « pour compter du 1er janvier 2008 » ; « CATÉGORIES SALAIRES FORFAITAIRES Par an Par jour », la 10e « 25 980,90 72,17 », la 13e « 33 126,69 », la 20e « 59 899,76 » |
| Arrêté du 19 mars 2026, article 1 | JORFARTI000053743024 | la 13e « 42 510,19 », la 20e « 76 867,05 » |
| Décret n° 2001-1203 du 17 décembre 2001 | JORFTEXT000000580421 | « les références monétaires aux unités nationales qui figurent dans les textes réglementaires devront être lues à compter du 1er janvier 2002 comme des références à l'euro, en appliquant le taux de conversion de 6,55957 F pour un euro, avec arrondissement à la deuxième décimale » ; il vise le règlement (CE) n° 2866/98 du 31 décembre 1998 |
| Décret n° 85-1148, article 3 | LEGIARTI000006454440 (1er décembre 1994 au 18 février 1995) | « afférents à l'indice 100 majoré et soumis aux retenues pour pension est fixée à 31 422 F à compter du 1er décembre 1994 » |

Relu aussi, pour vérifier ce que 57aa927 écrit : le barème B de l'annexe V du
décret n° 2023-519 (JORFARTI000047749261 : « 208 12 287,27 »), l'article 5 du
décret n° 85-1148 (LEGIARTI000047781303), son article 7 (LEGIARTI000006454537,
538, 549, 550) et son article 8 (LEGIARTI000006454571 : « l'indice majoré 169
(indice brut 100) » en mai et juin 2001), les décrets n° 86-166
(LEGIARTI000006455048, JORFTEXT000000881232), n° 2001-370
(JORFARTI000002487322) et n° 2001-559 (JORFARTI000002402166), l'article 1er du
décret n° 48-1108 (LEGIARTI000006561748, jusqu'au 25 avril 2008), le paquet de
e5dd612 (version 38, sans `indice_100`) et de 144a622 (version 39). Tout ce que
57aa927 en tire est conforme, à une précision près : la vingtième de 2005 est à
75,11 % du plafond, « au plus 75,1 % », non « sous 75,1 % » — corrigé dans la
fiche.

## Ce qu'on sait, ce qu'on ne sait pas, posé à la main

**Ce qu'on sait.** Deux montants réels, chacun dans un rectificatif.

- La 13e catégorie du 1er janvier 1995 : 14 733,03 par mois, en francs — le
  rectificatif n'écrit pas l'unité ; c'est le franc des textes réglementaires,
  que le décret n° 2001-1203 fait lire en euros « à compter du 1er janvier
  2002 » —, soit 14 733,03 × 12 = 176 796,36 F par an, et 176 796,36 /
  6,55957 = 26 952,43 €. Le modèle prend la 13e de 2008 ramenée par le salaire
  moyen : 33 126,69 × 20 944,65 / 29 486,72 = 33 126,69 × 0,710308 =
  23 530,15 €. Le réel est 26 952,43 / 23 530,15 = 1,14544 fois le modèle,
  14,5 % plus haut ; le modèle, 23 530,15 / 26 952,43 = 0,87303 fois le réel,
  12,7 % plus bas.
- La 10e catégorie du 1er janvier 2006 : 25 243,83, dans la « 2e sous-colonne »
  que le rectificatif ne nomme pas. Sa grandeur est celle d'un forfait annuel —
  la 10e du 1er janvier 2008 vaut 25 980,90 € par an et 72,17 € par jour — :
  une déduction. Le modèle : 25 980,90 × 28 043,44 / 29 486,72 = 25 980,90 ×
  0,951054 = 24 709,23 €. Le réel est 25 243,83 / 24 709,23 = 1,02164 fois le
  modèle, 2,2 % plus haut ; le modèle, 2,1 % plus bas.
- La structure de la grille lue : la 20e vaut 59 899,76 / 33 126,69 = 1,808202
  fois la 13e en 2008, et 76 867,05 / 42 510,19 = 1,808203 en 2026.
- Le plafond du 1er janvier 1995, au droit : l'indice majoré 158 (article 7,
  depuis le 1er août 1991), le point de 31 422 F pour cent points (article 3) ;
  8 × 158 × 314,22 = 397 174,08 F = 60 548,80 €.

**Ce qu'on ne sait pas.** La 20e catégorie d'aucune année d'avant 2008 ;
l'écart des autres années (deux points, rien avant 1995, rien entre 1995 et
2006) ; la structure de la grille d'avant 2008, le nombre de ses catégories et
leurs rapports ; la grille du 1er juillet 1995, majorée, au Journal officiel
imprimé seulement ; l'unité de la sous-colonne de 2006, déduite de sa grandeur.

**Ce que la limite fait aux pensions.** Le forfait de chaque année d'avant 2008
fait l'assiette des cotisations du marin — ce que son compte reçoit aux
scénarios en comptes notionnels (`Compte.cotisation_annuelle`) — et le salaire
de référence d'une pension qui prend effet avant 2008. Tant que le revenu du
marin tombe dans la grille, la convention du forfait le plus proche du revenu le
range plus haut qu'elle ne le ferait sur la grille réelle, et le forfait reste
près du revenu : l'écart s'amortit, à une catégorie près. Au-delà de la
vingtième, il ne s'amortit plus : le modèle prend 59 899,76 × 0,710308 =
42 547,27 € en 1995, quand la vingtième réelle, si elle suit l'écart de la
treizième et la structure de 2008, vaudrait 26 952,43 × 1,808202 = 48 735,45 €
— un salaire de référence et une pension plus bas que le droit de 1 −
42 547,27 / 48 735,45 = 12,7 % au plus pour le marin des plus hautes catégories
qui part en 1995 ; de 2,1 % en 2006 si l'écart de la dixième vaut pour lui. Non
mesuré sur les cohortes.

**Ce qu'elle fait au plafond de R. 11, 3°.** La vingtième réelle de 1995 ainsi
estimée serait à 48 735,45 / 60 548,80 = 80,5 % du plafond. Sur la grille du
modèle, refaite par le moteur Python année par année au plafond du 1er janvier
(du 1er décembre en 1985), le rapport de la vingtième au plafond reste entre
65,6 % (1985) et 75,11 %, le plus haut, en 2005 : 55 160,27 € pour
8 × 174 × 52,7558 = 73 436,07 €. Relevée tout entière de l'écart de 1995 — le
plus grand des deux, appliqué à toutes les années et à toutes les catégories —,
la vingtième resterait sous 75,11 % × 1,14544 = 86,04 %, soit sous 86,1 %, en
2005 ; pour atteindre le plafond, il faudrait une grille 1 / 0,7511 = 1,3313
fois celle du modèle, encore 1,3313 / 1,14544 = 1,162 fois la grille relevée.
Avant 1985, les seuils de la fiche se refont : 4 520,45 / (8 × 7,3907) =
76,455 en 1968, 19 230,64 / (8 × 23,3948) = 102,751 en 1980, le plus haut ;
relevés, 76,455 × 1,14544 = 87,57 et 102,751 × 1,14544 = 117,69, soit 87,6 et
117,7. La conclusion — aucune catégorie n'atteint le plafond — reste très
probable sous la grille relevée, et n'est prouvée par aucun texte avant 2008.

## Ce qui est fait

- **La fiche** `marins_salaire_de_reference`, à l'approximation des arrêtés
  annuels : l'écart dit ce que l'index garde, cité mot pour mot, et ce qu'il ne
  dit pas ; l'effet, après celui que 57aa927 mesure, dit l'effet possible sur
  les pensions et les comptes, le plafond sous la grille relevée, les seuils
  d'avant 1985 relevés. L'effet d'ensemble ne dit plus la grille « exacte » que
  depuis 2008. Une question au propriétaire dans `a_relire`, une lecture du
  jour, une ligne d'historique ; « sous 75,1 % » devient « au plus 75,1 % ».
- **Les limites** : la ligne des marins de `docs/limites/4-regimes-incomplets.md`
  dit le sens de l'erreur — la grille d'avant 2008 paraît trop basse, le forfait
  des plus hautes catégories en est sous-estimé —, sans chiffre nu, le
  document étant au régime de l'état ; les montants sont dans la fiche.
- **Trois tests** dans `tests/test_marins.py`, vus rouges sur la fiche de
  57aa927, verts sur la nouvelle : la grille du modèle est sous les deux
  montants réels, et la fiche écrit les forfaits, les écarts et la vingtième
  estimée de 1995 ; de 1985 à 2007, la vingtième reste sous le plafond même
  relevée de l'écart de 1995, et la fiche écrit les deux rapports ; avant 1985,
  la fiche écrit les seuils, et leur relèvement. Les chiffres de la limite ne
  vieillissent plus en silence.
- Rien d'autre : ni la note de M1, que 57aa927 a corrigée, ni son journal, ni
  le code. Aucune règle de calcul ne change.

## Ce qui attend le propriétaire

Une question : faut-il chercher les barèmes réels d'avant 2008 ? Ils sont au
Journal officiel imprimé — les fac-similés de Légifrance, que l'outil n'atteint
pas (403 à curl, tableaux en image). La vingtième catégorie de quelques années
(1986, 1995, 2000, 2005) suffirait à prouver que le plafond n'a pas été
atteint ; la grille entière, à corriger l'estimation. Avis : le plafond n'en
dépend guère, la marge restant voisine de 14 % sous l'écart le plus
défavorable ; la grille, davantage, qui fait les cotisations portées au compte
de chaque marin pour ses années d'avant 2008, et la pension des plus hautes
catégories liquidée avant 2008. Si le parti doit chiffrer les marins d'avant
2008, la lecture vaut d'être faite, par quelqu'un qui peut ouvrir les
fac-similés.
