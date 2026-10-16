# Étape 3, huitième partie : les civils de l'État pesés sur leurs départs actifs, super-actifs et sédentaires ; l'Ircantec mesurée

**La demande.** Vague quater du 16 octobre 2026, session 7 sur 12 : « action
138, étape 3. Les fonctionnaires actifs de l'État et l'Ircantec, pesés sur
leurs départs par la mécanique que la CNRACL a reçue le 16 octobre
(`GRILLE_DU_COUT`, `parts_caisses`), avec l'action 147 » — le troisième point
de « Ce qui reste » de `2026-10-16-etape-3-cnracl-par-ses-departs.md`. Rien
n'est écrit dans les pages, hors des valeurs de `MESURES_BLOCAGES` que le
changement déplace.

**Le défaut.** La caisse des civils de l'État n'avait qu'un cas type, le
sédentaire de catégorie B, au taux plein des sédentaires : 64,5 ans pour la
génération 1963. Les départs pour ancienneté de 2025 sont pourtant actifs à
21 % (jaune pensions annexé au PLF 2027, tableau B-4) : 5 552 ouverts à
cinquante-sept ans, mis en paiement à 61,9 ans, et 3 347 à cinquante-deux —
policiers, surveillants pénitentiaires —, à 58,3 ans, avec 22,9 trimestres
de bonification du cinquième ; les 28 209 sédentaires et les 4 704 carrières
longues, sédentaires aussi (les actifs du tableau B-3 ne sont que les 8 899
des deux catégories), à 64,4 et 61,4 ans.

**Ce qui est fait.**

- *Deux variantes du sédentaire* (`castypes.FONCTIONNAIRE_ACTIF_ETAT`,
  `FONCTIONNAIRE_SUPER_ACTIF_ETAT`, codes `fonctionnaire_sedentaire~actif` et
  `~super_actif`) : la même carrière de catégorie B, entrée tard dans l'État
  comme le sédentaire, aux statuts `fonctionnaire_etat_actif` et
  `fonctionnaire_etat_super_actif`, au niveau que l'indice de liquidation
  donne (757,9 et 768,2 contre 735,3 aux sédentaires : 1,24 et 1,25 salaire
  moyen). Chacune part au taux plein de sa catégorie : 62 ans et 56,2 ans
  pour la génération 1963, contre 64,5 au sédentaire.
- *Les parts* (`DEPARTS_ETAT_CIVILS_2025`, `PART_ACTIVE_ETAT`,
  `PART_SUPER_ACTIVE_ETAT`) : 13,3 % et 8,0 % de la caisse, le sédentaire
  78,7 %. Comme à la CNRACL, la part est celle du flux, non du stock ; la
  page Cas types, qui n'a que le sédentaire, lui laisse la caisse entière, et
  les poids que le paquet fige le rapportent à lui (`cas_type_affiche`).
- *La grille large* suit d'elle-même : `grille_large.reference()` lit
  `GRILLE_DU_COUT` et `parts_des_caisses` depuis la réparation du 16 octobre ;
  `tests/test_grille_large.py` passe sans retouche.

**Ce que cela déplace**, sous les réglages de la page. Les départs précoces
que le notionnel pénalise font reculer la masse des scénarios notionnels :
le scénario 6 passe de −36,0 à −36,2 % sur l'avenir, son solde moyen de
−1,13 à −1,08 point de PIB, sa dette de 2070 de 77 à 73 % du PIB (82 à 78
dans la seconde lecture), et le coût des 18 % de 2,3 à 2,2 points
(`MESURES_BLOCAGES`, mis à jour). Le passé : le scénario 4 de −53,1 à −53,3 %.
À l'horizon, la pension relative de la FPE passe de +8,0 à +5,1 % de celle du
COR, sa dépense de +22,3 à +19,3 % : les deux cliquets de `test_cout.py`
descendent, et l'écart des deux lectures de la dette de sept à cinq points.

**Le test** (`tests/test_cout.py`) : les départs relus dans le tableau B-4 et
recoupés par le B-3, le partage de la grille du coût et celui de la page, la
somme des trois poids égale à l'ancien poids du sédentaire, les trois âges de
départ dans l'ordre des catégories.

**L'Ircantec, mesurée et laissée.** Elle n'a qu'un cas type, le contractuel
de carrière complète, et les parts déclarées, ramenées à leur somme, lui
rendent toujours la caisse entière : la mécanique n'a rien à partager.
L'Ircantec sert 4 331,8 M€ en 2024 à 2,11 millions de retraités, 171 € par
mois ; le cas type en reçoit 545 € à la génération 1950 et 693 € à la 1960,
en euros de son départ. Ses retraités sont faits de passages : les peser sur
leur masse ferait du contractuel un tiers environ de ses têtes, en
équivalents carrières complètes. C'est un poids qui ne somme plus à la caisse,
contre la règle de `poids_effectifs`, et l'action 147 a écarté les
polypensionnés de la grille parce que les poids sont des parts de personnes
(`docs/archives/feuille_de_route/147/2026-10-13-etape-17-complementaires.md`,
« Essayé, hors du dépôt, et écarté », (b) et (c)). Le choix revient au
propriétaire : rien n'est écrit.

**Ce qui reste**, de ce point :

1. *L'Ircantec*, ci-dessus : un poids en équivalents carrières complètes, ou
   un cas type de passage, à décider avec ce qui reste de l'action 147.
2. *Le départ des super-actifs* : 56,2 ans pour la génération 1963 au taux
   plein du modèle, 58,3 au jaune ; leurs primes, plus lourdes que les 18 %
   du sédentaire (l'indemnité de sujétions spéciales des policiers), que la
   variante ne porte pas.
3. *La part des actifs dans le stock*, que le jaune ne publie pas, comme à la
   CNRACL.
4. *La page* : la table des poids pourrait montrer les trois départs de
   l'État et les deux de la CNRACL ; c'est un texte de `pages.js`, au
   propriétaire de le confier.
