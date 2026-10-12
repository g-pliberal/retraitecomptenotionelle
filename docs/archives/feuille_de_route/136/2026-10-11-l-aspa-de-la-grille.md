# Étape 6 : l'ASPA retirée de la grille de la page Coût

**Le 11 octobre 2026 : la page Coût ne sert plus le minimum vieillesse au
scénario 1 de sa grille, que la dépense qu'elle multiplie ne compte pas. Le
correctif ne touche que le Python : depuis l'action 150, le coût n'a plus de
portage JavaScript.**

Demande du propriétaire : « Action 136 : retire de la grille de la page Coût
l'ASPA des premiers non-salariés. »

- *Le correctif.* `Simulateur.pour_la_projection()`, le jumeau que la page
  Coût lit, éteint désormais `minimum_vieillesse_dans_le_scenario_actuel` en
  même temps qu'il allume les conventions du COR : la grille
  (`cout._pensionnes`), les engagements acquis et la revalorisation de la page
  passent tous par lui. Le simulateur individuel et la page Carrières types
  gardent l'ASPA, l'étalon d'un assuré. Le jumeau la servait à l'artisan né de
  1885 à 1905, à l'exploitant agricole de 1890 à 1920, au libéral de 1885 à
  1900 — et non plus jusqu'en 1915, le modèle ayant bougé depuis le
  5 octobre ; il ne la sert plus à aucun couple de la grille.
- *Ce qu'il déplace.* L'écart des années observées, seul : de −79,16 % à
  −78,95 % au scénario 2, de −52,14 % à −51,69 % aux scénarios 4 et 6, quatre
  fois moins que la mesure du 5 octobre ne l'annonçait (0,83 et 1,75 point).
  La projection ne bouge pas à la quatrième décimale — part du PIB en 2070,
  solde moyen, coefficients d'équilibre —, la garantie vieillesse de 2070 de
  deux cent-millièmes de point de PIB. Le passé que la projection refait à
  rebours (action 147) s'éloigne un peu de la dépense observée : −25,4 % en
  1990 au lieu de −24,1, −15,3 % en 2000 au lieu de −14,7, et au pire depuis
  2000, en 2009, 16,6 % au lieu de 16,4. Le minimum vieillesse grossissait la
  masse des plus vieilles cohortes, et cachait d'autant la dérive que
  l'action 147 cherche.
- *Côté JavaScript, rien.* `cout.js` est parti avec l'action 150 : la page lit
  `data/derive/agregats.json`, que `construire_donnees.py` fabrique par le
  même `_pensionnes`, et le portage n'a pas de jumeau de projection —
  `conventions_cor` n'y vaut jamais vrai. Le texte de la page disait déjà que
  le minimum vieillesse n'est « la pension d'aucun des quatre systèmes » ; il
  devient exact. La version du paquet ne monte pas : seules des valeurs
  changent, et GitHub les refait.
- *La grille élargie.* `scripts/grille_large.py` retirait l'ASPA à part
  (`parametres_de_la_grille`) et se comparait à la grille du dépôt sans elle ;
  il se compare désormais à la page elle-même, que la grille du dépôt,
  réécrite en parts, redonne au chiffre près. Le test qui chiffrait l'ASPA de
  la page (`test_l_aspa_des_premieres_generations_ne_touche_que_le_passe`)
  n'a plus d'objet ; `test_cout.py` tient le correctif
  (`test_la_page_ne_sert_pas_le_minimum_vieillesse`).
- *La prose.* La partie 5 bis des limites garde le procès-verbal du
  5 octobre, et dit la correction à sa suite ; la méthodologie (§ 8 bis), que
  la masse du système actuel ne compte pas plus le minimum vieillesse que la
  dépense.

**Ce qui reste** de l'action : la seconde moitié de l'étape 6, la population,
dont le propriétaire tranche la forme ; les étapes 1 à 5.
