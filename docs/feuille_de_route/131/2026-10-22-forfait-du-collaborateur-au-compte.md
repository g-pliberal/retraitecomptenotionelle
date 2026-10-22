# Le forfait du collaborateur au compte : ce que le régime prélève pour le collaborateur et l'aide familial

**La demande.** La vague du 22 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, à la demande du propriétaire (« Lance une
session par action qui n'a pas besoin de moi »), une session par action
qu'une session peut avancer seule ; celle-ci tient l'action 131, et le premier
des restes du bloc « Reprise » que les notes désignent : celui que la note du
18 octobre (`2026-10-18-ce-que-l-exploitant-verse-au-compte.md`, « Restes,
trouvés en chemin ») avait laissé, et qu'aucune note suivante n'a pris. Le
compte portait la cotisation du collaborateur et de l'aide familial sur leur
revenu, quand le régime la prélève sur un forfait.

**La règle, lue** (index LEGI du dépôt, mis à jour au 22 octobre). Code rural,
L. 731-42, rédaction du 11 novembre 2010 (LEGIARTI000023034860) : l'AVI, « due
pour chaque personne non salariée âgée d'au moins seize ans », est calculée
« en pourcentage des revenus professionnels du chef d'exploitation », sous le
plafond, 800 SMIC au moins (D. 731-120, 1°), à 3,2 % puis 3,32 %
(D. 731-121) ; pour l'aide familial et le collaborateur, au b du 2°,
« l'assiette de ces cotisations est déterminée forfaitairement » : 400 SMIC
(D. 731-120, 3°), au taux de l'AVA du chef (D. 731-123, LEGIARTI000026140073) ;
la part déplafonnée, au 3°, n'est due que du chef. Depuis 2026
(LEGIARTI000051284150 ; D. 731-123, LEGIARTI000053296672), une seule
cotisation, sur un forfait de 600 SMIC, « égal à la somme des taux » du chef.
À la RCO, 1 200 SMIC (D. 732-155, II). La MSA l'applique ainsi : l'AVA
« Assise sur 400 SMIC soit 4 228€ pour les collaborateurs et les aides
familiaux », la RCO sur une « Assiette forfaitaire de 1200 SMIC », l'AVI du
collaborateur à 3,32 % sur 800 SMIC au moins (barème des non-salariés
agricoles de 2022, MSA d'Auvergne).

**Ce qui est fait.** `ConstructeurCompte._cotisation_ligne`
(`_cotisationLigne`) : dans la branche des taux du droit en vigueur, après le
plancher et l'assiette minimale, l'assiette du collaborateur et de l'aide
familial est leur forfait, porté au SMIC de l'année et à la part que la ligne
cotise, celui que les droits lisent depuis le 16 octobre (étape 138.8) :
`acquerir.assiette_du_collaborateur` (`assietteDuCollaborateur`), que le
compte importe de `droit/` — le premier import du compte Python vers `droit/` ;
le JavaScript en avait déjà (`carriere.js`, `droit/preparer.js`). Avant 2004,
le revenu saisi reste, comme aux droits. Le taux uniforme et le régime fusionné
gardent le revenu, comme ils écartent le plancher. Un test, dans les deux
moteurs (`test_simulateur.py`,
`test_le_compte_porte_la_cotisation_du_collaborateur_sur_son_forfait`) : la
collaboratrice à 12 000 € par an verse au compte pour 2023 les 17,37 % de
400 SMIC horaires à 11,27 €, 783,04 €, et les 4 % de 1 200 SMIC, 540,96 €, et
non 2 084,40 € et 820,46 € ; pour 2026, 600 SMIC à 12,02 €, 1 252,72 € et
576,96 € ; pour 2003, les 17,37 % de son revenu. La fiche
`assiette_minimale_agricole` le dit, et l'écart qui reste ; la partie des
limites (`ecarts-au-droit-positif.md`) ne dit plus que le modèle prend les
cotisations du collaborateur sur son revenu.

**La classe.** Le compte ignorait une assiette que les droits lisent. Il prend
déjà celles des cultes, des marins, des classes, du micro-entrepreneur et de
la garantie minimale de points. Il ne prend pas l'assiette minimale des
indépendants (D. 633-2, D. 642-4 ; `AnneeCarriere.assiette_minimale_base`),
que `acquerir.assiette_minimale` sert aux droits : l'artisan à 1 000 € en
2023, dont le minimum est de 450 SMIC, 5 071,50 €, porte au compte 177,50 € à
la base, quand le régime prélève 900,19 € au même taux. Une autre règle, une
autre fiche, d'autres témoins : inscrite au bloc « Reprise », pour une session.

**Ce qui bouge** (`resumer_temoins.py`, après `regenerer.py`). Rien aux
scénarios 1, 3 et 5 : les droits lisaient déjà le forfait. Six des 889 témoins
de simulation aux scénarios 2 et 4, tous des collaborateurs agricoles,
−44,55 % en médiane, de −32,07 % (`statut_collaborateur_agricole_1945`) à
−59,33 % (`statut_collaborateur_agricole_1965`) ; quatre au scénario 6, de
−10,53 % (`statut_collaborateur_agricole`) à −59,10 %
(`statut_collaborateur_agricole_1955`). Ces témoins donnent au collaborateur
le salaire moyen pour revenu, dont l'ancien compte prélevait les 17,37 % et les
4 % comme d'un chef. Un rendu de page sur 79, `simuler_reversion_agricole`. Ni
le paquet ni les agrégats du coût ne bougent ; le poids du chargement que cite
le README passe de 1 735 à 1 736 Ko. Le portage rend les 889 témoins refaits au
bit près (`tests/js/comparer.mjs`). Les fichiers fabriqués, refaits pour
mesurer, ne sont pas commités : GitHub les refait.

**Restes, trouvés en chemin.** L'AVI du collaborateur, assise jusqu'en 2025 sur
les revenus du chef, que le modèle ne connaît pas et ne sépare pas de l'AVA :
le compte prend tout le taux du régime sur le forfait de l'AVA, 783,04 € en
2023, quand l'AVI au minimum, 299,33 €, et l'AVA, 520,67 €, en font 820,00 €,
et davantage à mesure que le chef gagne ; la fiche le déclare. Le taux de base
des exploitants depuis 2026, que L. 731-42 aligne sur celui des indépendants
(D. 633-3 : 17,15 % sous le plafond, 0,72 % au-delà), et celui du
collaborateur de 2026 à 2028, que le II de l'article 5 du décret n° 2025-1417
fixe et qui n'est pas lu : le modèle garde 17,37 %. L'assiette minimale des
indépendants au compte (« La classe »).

**Ce qui attend le propriétaire.** Rien de neuf.
