# Étape 3, septième partie : la CNRACL pesée sur ses départs actifs et sédentaires, et les parts déclarées des caisses partagées

**La demande.** Vague ter du 16 octobre 2026, session 11 sur 13 : « action
138, étape 3. Les retraités par régime, et le poids de chaque cas type de la
page Coût selon les masses plutôt qu'à parts égales (`castypes.poids_effectifs`)
— la CNRACL n'y est pondérée que sur un seul départ, le lourd que le
classement par poids garde » (`2026-10-09-classement-par-poids.md`, la ligne
« La CNRACL pondérée sur un seul départ »). Rien n'est écrit dans les pages,
ni dans `grille_large.py`, que d'autres sessions tiennent.

**Le défaut.** La caisse de la CNRACL, 1,47 million de retraités de droit
direct fin 2025 (jaune pensions annexé au PLF 2027, tableau A-1), n'avait
qu'un cas type : l'agent de catégorie active, qui part au taux plein du
classement — 62 ans pour les générations nées après 1963. Les départs pour
ancienneté de 2025 sont pourtant à 20 % seulement en catégorie active
(10 597), à 52 % sédentaires (27 477, mis en paiement à 64,0 ans) et à 28 %
en carrière longue (15 054, sédentaires aussi : le tableau B-3bis ne compte
d'actifs que les 10 597 premiers ; tableau B-5). Le départ précoce est celui
que le notionnel pénalise le plus : l'économie de la page était surestimée,
d'un signe connu.

**Ce qui est fait.**

- *Les parts déclarées* (`CasType.parts_caisses`, `castypes.parts_des_caisses`).
  Une caisse que plusieurs cas types réclament se partage selon la part que
  chacun déclare, quand elle se publie, et également sinon. Ou tous les
  réclamants d'une caisse dans la grille déclarent, ou aucun ; les parts sont
  ramenées à leur somme, si bien que l'actif, seul de sa caisse sur la page
  Cas types ou dans une grille réduite, la porte entière. Un partage à demi
  déclaré lève. La Cnav reste partagée également entre les quatre carrières
  du privé : rien de publié ne dit leur proportion.
- *L'agent sédentaire de la CNRACL* (`castypes.AGENT_SEDENTAIRE_CNRACL`, code
  `fonctionnaire_actif~sedentaire`) : la même carrière de catégorie C, hors de
  l'emploi classé (`fonctionnaire_territorial_hospitalier`), au niveau de
  0,87 salaire moyen (l'indice 489,5 des sédentaires contre 508 aux actifs),
  au taux plein des sédentaires : 64,5 ans pour la génération 1963, 65 ans
  ensuite. Il entre tard à la caisse, après dix-sept ans sous contrat
  (`entree_cnracl_sedentaire`, `macro/hypotheses_projection.yaml`) : les
  sédentaires et les carrières longues, qu'il porte ensemble, partent en 2025
  avec 99,2 trimestres de services en moyenne, l'actif avec 127,6 ; ce sont
  des polypensionnés. Il porte 80 % de la caisse, l'actif 20 %
  (`PART_ACTIVE_CNRACL`, tirée de `DEPARTS_CNRACL_2025`, qu'un test relit dans
  `caracteristiques_fonction_publique.csv`). La part est celle du flux, non
  du stock, que le jaune ne partage pas : les retraités les plus âgés
  comptaient plus d'actifs — les infirmiers l'étaient tous avant 2010 —, mais
  la page Coût se joue dans la projection, que le flux d'aujourd'hui fait.
- *La grille du coût* (`castypes.GRILLE_DU_COUT`) : les treize cas types et
  cette variante. C'est le défaut de `calculer_cout`, de
  `calculer_engagements`, de `memoire.cout`, et des contrôles d'Ancetre et de
  l'EACR, qui lisent la grille de la page. La page Cas types et ses treize
  carrières ne changent pas ; les poids que le paquet fige
  (`agregats.figer_cout`) rapportent la variante à l'actif dont elle porte le
  code (`cas_type_affiche`), si bien que la table « Ce que chaque carrière
  type pèse » montre la CNRACL entière sur la ligne de l'actif.

**Ce que cela déplace**, sous les réglages de la page. Le calage par groupe
(`_poids_par_groupe`) garde la masse de la CNRACL à la dépense que le COR lui
donne en 2025 ; le sédentaire, à la pension de caisse plus petite, y reçoit
plus de têtes, et la CNRACL pèse 12,5 % des poids de 2024 au lieu de 9,8. Le
rapport des scénarios au système actuel monte : celui du scénario 6, de 71,17
à 71,50 % en 2025, de 75,07 à 75,96 en 2040, de 73,60 à 74,09 en 2050, de
56,27 à 56,48 en 2070 ; celui du scénario 4, de 79,93 à 80,56 en 2040 et de
71,62 à 72,11 en 2070. L'économie de la proposition recule d'autant. À
l'horizon, la dépense de la CNRACL passe de +13,3 à +7,5 % de celle du COR,
qui fait monter l'âge de départ de la caisse avec ses sédentaires ; la
pension relative d'ensemble, de +5,4 à +5,7 %, le départ plus tardif
relevant la pension. Les deux cliquets suivent (`test_cout.py`).

**Le test** (`tests/test_cout.py`) : la part relue dans le jaune, le partage
de la grille du coût et celui de la page, la somme des deux poids égale à
l'ancien poids de l'actif, le partage à demi déclaré qui lève.

**Ce qui reste**, de ce point :

1. *La part des actifs dans le stock*, que le jaune ne publie pas : la part
   du flux de 2025 la sous-estime pour les générations parties avant 2010 ;
   un délai d'entrée qui varie par génération, de même.
2. *La page.* La table des poids pourrait montrer les deux départs de la
   CNRACL sur deux lignes ; c'est un texte de `pages.js`, que la session des
   pages tient (au propriétaire de la confier).
3. *Les autres caisses d'un seul départ* : les civils de l'État, que le seul
   sédentaire de catégorie B porte quand les actifs y partent à 57 et 52 ans
   (tableau B-4) ; la même mécanique les partagerait. L'Ircantec, et peser
   par les masses plutôt que par les têtes au-delà du calage par groupe, avec
   ce qui reste de l'action 147 (les polypensionnés).
