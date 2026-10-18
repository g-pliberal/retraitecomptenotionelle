# Étape 3, douzième partie : la date de chaque cohorte dans `cout.py`, celle que le droit de sa génération donne au cas type

**La demande.** Vague du 18 octobre 2026, « 138.3, les cohortes de
`cout.py` » : le point 1 de « Ce qui reste » de la note « la grille » du même
jour. La grille du coût ne simule qu'une génération sur cinq, née en janvier,
et faisait partir les cinq cohortes qu'elle représente à son âge, la date
décalée d'autant ; `facteurs_depense.py` mesurait l'erreur à part
(`par_generation`), `cout.py` la portait dans ses têtes et ses masses. Ni
l'Ircantec, ni la page Coût, ni la table des poids de `pages.js`.

**Ce que fait la grille, désormais.** Chaque cohorte part l'année que le droit
de sa génération donne au cas type (`cout._departs`, `Pensionne.departs`,
`Pensionne.liquidation`), tirée comme celle de la génération simulée
(`castypes.carriere_de_la_grille`, sous les conventions de projection) ; une
cohorte que la grille ne sait pas simuler garde la date de la grille. Sa
pension reste celle de la génération simulée. Sur les 1 704 cohortes voisines
des 426 couples de la grille, 102 partent une autre année :

- d'un an, 87 cohortes, dont, sous la suspension de 2026 (loi n° 2025-1403,
  art. 105 ; L. 161-17-3), celles de 1966 et 1967 de huit cas types, plus
  tard, à 172 trimestres au lieu des 170 de la génération de janvier 1965 ;
  celles de 1961 et 1962 de six cas types, plus tard, à 168 et 169 trimestres
  au lieu des 167 de la génération 1960 ; plus tôt, celles de 1963 et 1964 du
  salarié au SMIC à carrière complète et du sédentaire devenu super-actif ;
- de deux à neuf ans, quinze cohortes dont la génération change de régime ou
  de règle : l'agent de conduite de la SNCF né en 1998 ou 1999, embauché au
  statut avant sa fermeture de 2020, part à 54 ans, en 2052 et 2053, quand la
  génération 2000 qui le représente, embauchée après, part à 63 ans ; les
  autres sont nées avant 1930.

La proposition fait partir chaque cohorte à son âge légal à elle quand elle
reporte la génération simulée, sauf à partir plus tard, et l'année du droit
en vigueur sinon (`Pensionne.depart_liberal`) ; le côté de la bascule est celui
du départ de la cohorte (`Pensionne.volet`), et l'autre volet se calcule dès
qu'une cohorte tombe de l'autre côté (`_autre_volet`). La survie propre des
cas types court du départ de chaque cohorte (`_survies`), l'engagement acquis
(`calculer_engagements`) et le pilier (`_masses_pilier`) la datent de même.
Ce que versent les cohortes reste au calendrier de la grille, décalé
d'autant (`_masses_cotisations`) : la recette ne se lit qu'en rapport, et les
deux barèmes y suivent le même calendrier.

La même erreur, chez ceux qui relisent la grille (la classe, pas le cas) :
`facteurs_depense.retraites_par_age` compte les têtes de `cout.py` à leur
date, sans plus d'option `par_generation` ni de `departs_par_generation` ; les
contrôles sur Ancetre et l'EACR (l'âge de départ de chaque cohorte compris),
le bilan du compte, `scripts/flux_fonction_publique.py` et
`scripts/grille_large.py` lisent `Pensionne.liquidation`. Le coût des
avantages a sa propre grille, que rien de cette partie ne touche (« Ce qui
reste »).

**La mesure.** Les retraités du modèle sous la référence du COR, en millions,
tous âges et de moins de 65 ans, la grille datée de ses deux façons sur les
mêmes poids :

| Retraités | 2020 | 2024 | 2025 | 2026 | 2030 | 2035 | 2055 | 2070 |
|---|---|---|---|---|---|---|---|---|
| à la date de la grille | 16,27 | 17,18 | 17,34 | 17,48 | 18,21 | 18,61 | 20,75 | 21,94 |
| dont moins de 65 ans | 2,55 | 2,43 | 2,32 | 2,17 | 1,90 | 1,34 | 1,28 | 1,22 |
| chacune à sa génération | 16,33 | 17,03 | 17,09 | 17,28 | 17,93 | 18,61 | 20,77 | 21,94 |
| dont moins de 65 ans | 2,60 | 2,28 | 2,07 | 2,08 | 1,61 | 1,34 | 1,30 | 1,22 |

La grille comptait 0,15 million de retraités de trop en 2024, l'année où la
masse du modèle s'ancre sur la dépense, 0,25 million en 2025, d'où la dérive
se compte, et 0,28 million en 2030, tous de moins de 65 ans ; rien en 2035 ni
en 2070.

L'écart de couverture de 2022-2030 à l'AWG, que la note « la grille »
départageait à 0,54 point dont 0,18 de la grille, n'est plus que de 0,34
(`python scripts/facteurs_depense.py --sans-suspension`, en points de PIB,
positif quand le modèle recule moins) :

| L'écart de 2022-2030, départagé | 65 ans et plus | Moins de 65 ans | Couverture |
|---|---|---|---|
| le périmètre | −0,01 | +0,09 | +0,08 |
| la suspension | +0,07 | 0,00 | +0,07 |
| ce qui reste | +0,08 | +0,11 | +0,19 |
| l'écart | +0,14 | +0,20 | +0,34 |

**Ce que ça déplace.** Mesuré sur `main` au 18 octobre (7af072b) par
`python scripts/regenerer.py` puis `resumer_temoins.py` : aucun des 883
témoins de simulation ; 59 rendus de page sur 76, ceux qui citent le coût ;
les mêmes chiffres sur la base où le commit s'est rebasé, que les sessions du
jour n'avaient pas fait bouger. La masse de 2024 sur laquelle le modèle
s'ancre perd les retraités partis trop tôt, et sa trajectoire propre monte :
15,60 % du PIB en 2070 au lieu de 15,42 (15,3 au COR) ; celle de 2025, d'où
la dérive se compte, en perd plus encore : la dérive de 2070 vaut 1,050 au
lieu de 1,033, et ne passe sous un qu'en 2026, et non plus en 2027. Le passé
se refait mieux :
l'écart de la reconstitution passe de −17,4 à −15,9 % en 1990, de −10,2 à
−8,4 % en 2000, de −13,1 à −11,9 % en 2009, de −2,6 à −1,0 % en 2020 ; en
2009, les têtes de −6,2 à −5,4 %. De 2025 à 2070, les retraités du modèle
croissent de 28,4 % au lieu de 26,5 (27,6 au COR), sa pension moyenne relative
recule de 12,3 % au lieu de 12,8 (17,2 au COR). La page Coût, en première
lecture : la proposition a un solde moyen de −1,12 % du PIB au lieu de −1,08,
une dette de 76 % en 2070 au lieu de 73, un coefficient d'équilibre de 0,996
au lieu de 0,998 ; les autres systèmes bougent d'un milliard au plus en 2070.
En seconde lecture, que la dérive multiplie : −1,38 % au lieu de −1,17, une
dette de 92 % au lieu de 78, 8,6 % du PIB en 2070 au lieu de 8,4 ; la
fourchette des deux lectures passe de cinq à seize points de dette.

Trois écarts au COR que des cliquets tiennent remontent, parce qu'un défaut en
masquait un autre : en 2025, d'où ils partent, la grille faisait partir le
cadre de 1961, le fonctionnaire sédentaire de l'État et l'agent sédentaire de
la CNRACL de 1962, qui partent en 2026. À l'horizon, la pension relative de
l'Agirc-Arrco s'écarte de +23,8 % au lieu de +21,4, la dépense de la FPE de
+22,4 % au lieu de +18,9, celle de la CNRACL de +11,2 % au lieu de +7,5. Les
nouveaux retraités de 2024 de la grille partent plus jeunes encore que ceux
de l'EACR, à 62,3 ans au lieu de 62,7 (63,6 publiés) : entré à 18 ans, le
salarié au SMIC né en 1964 part au titre des carrières longues à 60 ans et 9
mois, en 2024, et non plus à 61 ans, en 2025, et sa cohorte fait à elle seule
18 % des départs de l'année, à 60 ans, quand l'EACR en compte 5 %.

Les tests. En suite rapide, `test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation`
(un couple posé à la main : têtes, masses, régimes, revalorisation, survie,
volet, départ de la proposition) et
`test_la_grille_date_chaque_cohorte_au_droit_de_sa_generation` (le salarié au
salaire moyen de 1963 à 1967, tiré de L. 161-17-3 : 2026, 2027, 2028, 2030,
2031) ; les contrôles d'Ancetre et de l'EACR et le compte des têtes de
`facteurs_depense` reçoivent une cohorte qui part plus tard que la grille. En
contrôle, chaque borne déplacée a son histoire écrite à côté : le cliquet de
la reconstitution descend de 13,5 à 12 % ; ceux de l'Agirc-Arrco, de la FPE
et de la CNRACL montent à 24, 23 et 12 % ; la dérive de l'horizon et l'écart
de l'affirmation `cout.vigilance_cor` (« à six points près ») passent sous six
points au lieu de quatre ; la fourchette de la dette, de 4 à 9 points à 12 à
20 ; la survie du vingtile date chaque cohorte (le cadre de 1961 part en
2026) ; le test de l'EACR dit les départs à 60 ans ; la couverture de
2022-2030, portée au périmètre de l'AWG, s'en écarte de moins de 0,15 point.
L'affirmation `cout.borne_basse` — « Les chiffres de la proposition ont une
fourchette, étroite. », dix points de dette et un quart de point de solde au
plus — devient `contredite` (action 138), sous le contrôle `fourchette_elargie`
qui tombera quand la fourchette se resserrera ; `fourchette_haute_derive` ne
garde que la multiplication par la dérive, pour `cout.ecart_propre`. La suite
complète, jouée avant l'envoi dans un worktree régénéré, ne rougissait que de
ces bornes.

**Ce qui reste**, de cette partie ; les points 2 et 3 de la note du 17
octobre demeurent.

1. *Les 0,19 point qui restent* (point 2 de la note « la grille ») : les
   naissances de l'année, l'entrée dans l'emploi de Destinie, les départs
   hors du taux plein.
2. *Le coût des avantages* (`avantages.py`) a sa propre grille, qui date
   encore ses cohortes à la génération simulée, décalée d'autant : la même
   erreur, à porter de même.
3. *La pension et la cotisation de la génération simulée.* Une cohorte qui
   part un an plus tard touche la pension de la grille, et ne verse rien
   l'année de plus ; les agents de conduite de 1998 et 1999 touchent, dès
   2052, la pension du régime général de la génération 2000. Une grille
   d'une génération par an, de 1958 à 1972, les ôterait, au prix de cinq fois
   plus de calcul sur ces quinze ans.
4. *Pour une session des pages* : la phrase de la page Coût « Les chiffres
   de la proposition ont une fourchette, étroite. », que le modèle contredit
   désormais (seize points de dette entre les deux lectures) — la récrire,
   puis rendre `cout.borne_basse` à l'état `verifiee` ; et, comme avant, les
   leviers et le taux effectif. Le reste de la page suit le paquet.
