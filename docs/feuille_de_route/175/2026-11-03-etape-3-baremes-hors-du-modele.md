# Étape 3 : les barèmes hors du modèle

**Le 3 novembre 2026, ce qui est fait.** 219 des 228 barèmes que l'étape 2
laissait `a_lire` sont rangés — 127 `hors_modele`, 84 `limite`, 8 `recoupe` —,
et les 495 pages jointes qui restaient (436 `hors_modele`, 59 `limite`) : le
registre n'a plus aucun document `a_lire`. Chaque barème a été relu par
l'API, à la version que le registre date, qui était partout celle du jour.

- *Les taux de change et de conversion, triés d'abord* : 85 barèmes et 422
  pages — la valeur des monnaies étrangères, trimestre par trimestre depuis
  1990, et les taux des règlements européens publiés au Journal officiel de
  l'Union. Ils convertissent ce qu'un assuré perçoit à l'étranger, une
  pension, une ressource, que la saisie porte en euros
  (`minimum_contributif_international`) : `hors_modele`. Aucune de ces tables
  ne convertit les anciens francs ni la monnaie d'un département d'outre-mer ;
  le franc CFP et le franc comorien y figurent comme les monnaies des autres
  pays. Le
  franc CFA de La Réunion reste ce que `cnav_avts.py` en fixe, deux anciens
  francs.
- *Les limites*, déclarées dans `docs/limites/3-systeme-actuel.md` : les
  rachats et les versements pour la retraite (42 barèmes et 26 pages, avec la
  fiche `rachats_et_versements`, pas encore modélisée), cotisations arriérées
  et stages d'études compris ; les assiettes forfaitaires et les taux réduits
  des salariés, dont l'entrée nomme désormais le personnel hôtelier au
  pourboire, les concierges, les assistants maternels, les dockers, les
  centres de vacances, les formateurs occasionnels, les stagiaires, les
  professions médicales à temps partiel et les collaborateurs occasionnels du
  service public (26 barèmes et 33 pages) ; deux entrées neuves, les aidants
  (l'assurance vieillesse des aidants, depuis le 1er septembre 2023) et
  l'Algérie (la validation gratuite d'avant le 1er juillet 1962, sur un salaire
  forfaitaire) ; les forfaits de début d'activité des DOM de 2023 à 2025,
  rangés comme ceux de 2020 à 2022 à l'étape 2. Les autres renvoient aux
  fiches qui disent déjà ce que le modèle n'en sert pas : l'allocation
  supplémentaire d'invalidité (`minimum_vieillesse`, `inaptitude_au_travail`),
  la majoration pour tierce personne (`retraite_anticipee_handicap`,
  `pension_d_invalidite_substituee`), l'abattement des revenus professionnels
  de l'ASPA et le plafond du premier étage d'avant 2007
  (`minimum_vieillesse`), le revenu minimal de la retraite progressive
  (`retraite_progressive`).
- *Hors du modèle*, chacun avec sa raison : l'allocation de veuvage, la
  pension de vieillesse de veuve ou de veuf, la pension d'orphelin, le minimum
  de la pension d'invalidité, les plafonds propres aux veuves de guerre, les
  retraites ouvrières et paysannes de 1910, les avantages en nature, les
  abandons de créances, la fraction saisissable, le recours contre tiers,
  l'avance du minimum contributif, l'annulation des cotisations qu'un régime
  spécial reprend, les coefficients qui revalorisent les allocations du
  minimum (le modèle en lit les montants), et les seuils de la CSG des années
  passées.
- *Recoupés* : quatre barèmes que des tests d'autres actions confrontaient
  déjà sans que le registre le dise — le maximum de la retraite personnelle
  (`test_pension_maximale.py`, coquille de 1965 comprise), le plafond de
  ressources de la réversion (`test_reversion.py`), le seuil du versement
  forfaitaire unique (`test_versements_uniques.py`, à quatre dates), les
  seuils de la CSG de 2026 (`test_net_pensions.py`) — ; et, par deux tests
  neufs de `tests/test_cnav_baremes.py`, la majoration de durée après l'âge
  du taux plein, ses soixante coefficients rejoués par le moteur, et les taux
  des prélèvements de 2026 avec les seuils de la CRDS et de la Casa.

**Ce que la lecture a trouvé.** Neuf barèmes que le modèle sert restent
`a_lire`, faute d'être de l'étape : huit de Mayotte — le minimum contributif,
son plafond, le maximum, le minimum, le maximum et le plafond de la réversion,
le montant et le plafond de l'allocation spéciale pour personnes âgées —, que
la fiche `mayotte_pension_de_base` dit servir, et qui vont à l'étape 4 avec le
thème Mayotte, comme les barèmes des indépendants de Mayotte à l'étape 2 ; et
les coefficients de revalorisation de la pension d'invalidité, appliqués au
1er avril depuis 2020 (1,008 en 2026), quand le moteur revalorise la pension
d'invalidité d'avant le 31 mai 1983, plancher de la pension substituée, comme
une pension de vieillesse (`invalidite.pension_d_invalidite_servie`) : un
écart possible, que la fiche `pension_d_invalidite_substituee` ne déclare
pas, à la session du modèle. Le seuil du versement forfaitaire unique n'est
confronté qu'à quatre de ses soixante et onze dates : une confrontation
entière irait à `tests/test_cnav_baremes.py`.

**Ce qui reste.** Les neuf barèmes ci-dessus ; les exposés, les listes, les
fenêtres et les références, aux étapes 4 et 6 ; la veille, à l'étape 5.
Aucun fichier d'une autre file n'a été touché.
