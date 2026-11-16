# Les scripts sur le simulateur de données : dix-neuf scripts et le coût des avantages quittent le simulateur Python

Action 161, suite de `2026-11-16-le-simulateur-de-donnees-seules.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé ; aucune règle n'est
retirée, le moteur Python reste en place.

- Les scripts des groupes 1 et 2 du tri
  (`2026-11-16-le-tri-des-scripts-et-des-modules.md`) bâtissent un
  `SimulateurDeDonnees` au lieu du `Simulateur` : `age_conjoncturel`,
  `age_depart_csp`, `controle_eacr`, `cout_age_depart`, `cout_avantages`,
  `cycle_de_vie`, `estimation_officielle`, `facteurs_depense`,
  `flux_fonction_publique`, `garantie_par_sexe`, `indexation_scenario_6`,
  `mesures_accueil`, `mortalite_population`, `part_minimum_contributif`,
  `proposition_prospective`, `sensibilite_comptes`, `solde_fusion`,
  `stock_age_legal`, `tableau_de_bord`.
- Les modules qu'ils appellent de même : `avantages` (ses signatures),
  `controle_ancetre`, `controle_eacr`, `facteurs_depense`, `leviers`, et
  `memoire.avantages`, le coût des avantages.
- `SCENARIOS_NOTIONNELS`, tiré des univers du noyau, passe sous
  `donnees/simulateur.py` ; `simulateur.py` le reprend de là, le même objet.
- Restent sur le simulateur Python : `mesures_prose` et `lectures_du_modele`,
  qui appellent `simuler` ; `grille_large`, `scenarios_meres`, `recours_aspa`,
  `lectures_decision_29`, `mesurer_surcote`, `fetch/trajectoire.py`, non
  sondés ou qui calculent ; `contexte.simulateur`, que la fabrique
  (`construire_donnees.py`) et le bilan du compte lisent, laissé à leur zone.

**Vérifié.** Les dix-huit scripts lancés sans argument, chacun sous la sonde,
avant et après, mémoire des calculs vidée entre les deux : sortie identique,
octet pour octet, et la sonde rend la même liste (rien du moteur Python, ou
les seuls types de `carriere`). `estimation_officielle` ne se lance pas sans
relevé : ses tests le couvrent.

**Tests.** `tests/test_chargeurs_a_part.py` (1 de plus, rapide) : ni ces
scripts ni ces modules n'importent le simulateur Python, et la mémoire ne le
bâtit plus. Vu rouge, puis vert. `python -m pytest -m rapide` et les tests de
ces scripts : verts.

**Reste.** Le retrait des règles, avec l'accord du propriétaire ; avant lui,
les scripts qui calculent encore (point 1 à 3 du tri) et `contexte`.
