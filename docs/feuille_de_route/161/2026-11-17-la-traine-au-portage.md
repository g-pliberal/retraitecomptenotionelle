# La traîne au portage : 11 tests dépendent encore de la carrière des règles, au lieu de 63

Action 161, morceau 3 du plan de `2026-11-17-la-facade-transmet-la-carriere-nue.md`
(les tests qui lisent une propriété de règle), sa traîne, menée la nuit du 16
au 17 novembre 2026, sur la consigne du propriétaire d'avancer ce qui ne
demande pas son avis. Aucun fichier de `moteur/` n'est touché, aucune règle
ni donnée : aucun résultat, aucun témoin ne peut bouger.

- **Mesuré d'abord** par la recette de la note de la façade : 63 échecs dans
  23 fichiers, ceux que la note précédente comptait.
- **Huit entrées de la façade** (`tests/facade.py`), servies par le portage
  (`pont.mjs`, `pont.LECTURES_DE_LA_FACADE`) :
  - `carriere.fait`, `facade.fait(carriere, nom)` : ce que la carrière lit de
    sa chronologie, sous le nom de sa lecture Python — l'invalidité, la
    radiation, l'incapacité, l'inaptitude, l'étranger (périodes, pensions,
    résidence, mois en France), la réversion agricole, l'emploi après le
    départ, la retraite progressive, les naissances des enfants, les années
    déclarées, le conjoint, les ex-conjoints, le décès. Une entrée et une
    table de types (`pont.FAITS_DE_LA_CARRIERE`), plutôt que seize entrées.
  - `carriere.parts_retenues` (chaque ligne, dans leur ordre),
    `carriere.qualites_agricoles` (année par année),
    `carriere.duree_de_service`, `carriere.date_de_service`.
  - Trois copies de travail : `carriere.liquidee_au`,
    `carriere.arretee_au_deces`, `carriere.avec_lignes` (les lignes passent
    sur une seconde carrière, qui les porte).
- **Les types des faits** (`PensionDInvalidite`, `RadiationPourInvalidite`,
  `IncapacitePermanente`, `PeriodeALEtranger`, `PensionEtrangere`,
  `ReversionAgricole`, `Conjoint`, `ExConjoint`) quittent `carriere.py` pour
  `types_du_pont/carriere.py`, que `carriere.py` réimporte : la lecture du
  pont les donne sans charger les règles. Déplacés tels quels.
- **Les tests.** `test_facade.py`,
  `test_les_faits_de_la_carriere_se_demandent_au_portage` et
  `test_les_copies_et_les_services_de_la_carriere_se_demandent_au_portage`,
  aux valeurs posées à la main, vus rouges puis verts. Deux valeurs posées
  d'abord étaient fausses, et le code avait raison : la date de service est
  le mois où la durée s'achève (février 2008 pour vingt-cinq ans servis
  depuis mars 1983), et l'âge se compte du mois qui suit la naissance (60 ans
  et 9 mois au 1er janvier 2023 pour un né en mars 1962). `test_facade_jumeau.py`
  confronte chaque entrée au jumeau sur trois carrières.
- **Les fichiers** passés à la façade, sans qu'aucune valeur attendue change :
  `test_invalidite.py`, `test_moteur.py`, `test_etranger.py`,
  `test_chronologie.py`, `test_majoration_enfants_a_charge.py`,
  `test_releve_prolonge.py`, `test_saisie_de_la_reversion_agricole.py`,
  `test_oracle.py`, `test_emploi_retraite.py`, `test_minima_agricoles.py`,
  `test_chomage_complementaires.py`, `test_cumul_activites.py`,
  `test_fiche_date_d_entree.py`, `test_periodes_assimilees.py`,
  `test_independants.py`, `test_minimum_pension_sncf.py`,
  `test_temps_partiel.py`, `test_rafp.py`, `test_retraite_progressive.py`,
  `test_reversion.py`. Les lectures qui passaient déjà par le portage
  (`date_entree`, `trimestres_actuels`, `prolongee`) y vont par leur entrée.
- **Les vérifications.** `python -m pytest -m rapide` : vert (5 701) ; les
  confrontations légères, `test_pont.py` et `test_facade.py` : verts (742).
- **Mesuré de nouveau** sous la carrière nue : 11 échecs, au lieu de 63.

**Ce qui reste.**

1. **La bascule** (morceau 4), huit échecs qui sont les siens : les cinq
   épingles de la classe des règles (`test_pont.py`,
   `test_le_portage_bat_les_carrieres_de_la_grille` ; `test_facade.py`,
   `test_la_carriere_simple_revient_sous_le_type_du_python`,
   `test_la_carriere_du_releve_porte_les_revenus_de_ses_lignes`,
   `test_le_depart_que_la_proposition_reporte_revient_avec_sa_carriere`,
   `test_la_coupure_du_chomage_se_demande_au_portage`), et les trois tests
   du jumeau de `test_facade_jumeau.py` (la comparaison, le scénario 1, la
   proposition), où le simulateur Python reçoit la carrière du portage et
   lit `prolongee` et `date_entree` sur elle : le jumeau la recopie sous la
   classe des règles, comme le font déjà les tests de cette note.
2. **Une question au propriétaire** :
   `test_chronologie.py`, `test_les_copies_de_travail_gardent_leur_chronologie`,
   vérifie que la copie garde la chronologie elle-même (`is`). Passée par le
   portage, la copie en porte une relue, égale et non identique : le test
   ne peut plus vérifier que l'égalité. Le passer à `==`, ou le laisser
   partir avec les règles, change ce qu'il vérifie : laissé tel quel.
