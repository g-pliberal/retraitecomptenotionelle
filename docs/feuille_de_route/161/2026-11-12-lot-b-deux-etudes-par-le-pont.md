# Lot B, première session : `age_conjoncturel.py` et l'option des cas types de `lectures_decision_29.py` passent par le pont

**La pertinence, vérifiée avant d'agir.** Quatre questions, sur 3944fdc puis
5144b68, les deux derniers commits de `main` le 12 novembre 2026.

1. *L'étape était-elle faite ou entamée ?* Non. `scripts/age_conjoncturel.py`
   appelait `calculer_cas_types` (ligne 126), qui date, bâtit et simule en
   Python sans aiguillage (`castypes.py:978` et `979`) ;
   `scripts/lectures_decision_29.py` appelait `carriere_de_la_grille` puis
   `Simulateur.simuler` (lignes 399 et 400). Aucun commit de `main` n'y
   touchait.
2. *Chaque étude a-t-elle encore un lecteur ?* Oui, relu à la ligne citée par
   la note de la question 3. Pour la première :
   `docs/limites/5-hors-du-modele.md:184` écrit la limite et nomme
   `test_age_conjoncturel.py`, dont trois tests la tiennent ;
   `data/sources.yaml:1865` nomme le script ; `scripts/age_depart_csp.py:71`
   et `scripts/cout_age_depart.py:79` importent sa fonction, chacun avec son
   fichier de tests. Pour la seconde :
   `docs/feuille_de_route_programme.md:852` dit que « le calcul se refait
   par » elle et que « le choix entre A et B reste au propriétaire ». Son
   option `--cas-types` n'avait aucun test, comme la note le disait.
3. *Le pont rend-il déjà ce qu'elles lisent ?* Oui, sans demande nouvelle :
   ni `pont.py` ni `pont.mjs` ne changent. La première ne lit que l'année et
   l'âge du départ de chaque case, que rend `castypes.departs_au_portage`
   (`pont.carrieres_de_la_grille` sous `"rendre": "depart"`). La seconde lit
   la pension du scénario 6 et celle de l'étalon en euros constants, l'année
   du départ du scénario 6 et le revenu de 2026 : `pont.carrieres_de_la_grille`
   sous `"rendre": "carriere"` rend la carrière, `pont.grille_du_cout` le
   reste, le taux crédité dans les paramètres de la demande.
4. *Le doute que la note laissait.* `calculer_cas_types` écarte aussi les
   cases dont la simulation échoue, ce que la datation seule ne voit pas.
   Mesuré : sur les 358 cases que la grille garde (13 cas types, 29
   générations), le moteur Python en écarte 19, toutes à la datation — 12
   pour une liquidation antérieure à la répartition, 7 faute de régime
   actif —, aucune à la simulation ; le portage écarte les mêmes 19, sous les
   mêmes motifs, et rend pour les 358 autres la même année et le même âge,
   type de l'âge compris.

L'étape était donc pertinente et sûre ; elle est faite. La recommandation
« garder les douze » n'étant pas confirmée, rien n'est archivé ni retiré :
les deux études gardent leurs sorties, seul change ce qui les calcule.

**Ce qui change.**

- `scripts/age_conjoncturel.py`, `departs_de_la_grille` : une demande au
  portage (`castypes.departs_au_portage`) à la place de `calculer_cas_types`,
  sur le paquet des données du jour (`pont.paquet_des_donnees`), comme le
  coût bâtit sa grille. `age_depart_csp.py` et `cout_age_depart.py`, qui
  l'appellent, passent avec elle sans une ligne changée.
- `scripts/lectures_decision_29.py`, `pensions_des_cas_types` : deux demandes
  au portage, la carrière bâtie puis la simulation, sur le même paquet. Une
  case que le portage écarterait lève une `ValueError` qui la nomme, comme
  `carriere_de_la_grille` en levait une.
- `castypes.calculer_cas_types` ne change pas. Hors des tests, il ne lui
  reste que `scripts/flux_fonction_publique.py:221`, que porte la session
  suivante du lot B.

**Les tests, écrits d'abord et vus rouges** pour la raison attendue — « un
jumeau Python date, bâtit ou simule la grille du coût »
(`outils_pont.empecher_les_jumeaux_du_cout`).

- `tests/test_age_conjoncturel.py`,
  `test_les_departs_de_la_grille_se_datent_au_portage_sans_les_jumeaux` :
  trois cas types sur les 29 générations, dont six cases écartées, et
  l'artisan entré deux ans plus tôt sur trois générations, comme
  `cout_age_depart.py` rejoue la lecture ; les départs lus égalent ceux que
  le moteur Python rendait, puis les jumeaux sont empêchés et l'étude doit
  les rendre seule.
- `tests/test_lectures_decision_29.py`,
  `test_les_cas_types_passent_par_le_portage_sans_le_moteur_python` : les
  neuf cas de l'option, sous le taux du programme et sous 11,23 %, au bit
  près de ce que le moteur Python simulait. Sept secondes : il est rangé au
  niveau complet (`tests/conftest.py`, `EXCEPTIONS`), le reste du fichier
  restant rapide.

Aucun des deux n'ouvre `pont.par_le_jumeau()` : le moteur Python qu'ils
confrontent se calcule sans aiguillage, et rien ne s'ajoute à
`CONFRONTATIONS_DU_JUMEAU`. Ces deux confrontations partent avec le moteur
Python, au lot F.

**Les chiffres, inchangés.** Vérifié en faisant tourner le code avant et
après, la mémoire des calculs coupée (`CALCULS_SANS_MEMOIRE=1`).

- Le tableau de `age_conjoncturel.mesurer`, 21 années : identique, champ par
  champ.
- `age_depart_csp.confronter` et `cout_age_depart.chercher_decalages`,
  écrits en JSON avant et après : identiques à l'octet. Les deux ensemble
  tournaient en 88 s ; ils tournent en 7 s.
- `pensions_des_cas_types` : égale, sous deux taux, à ce que le moteur Python
  rendait (le test). Le tableau de l'option s'écrit
  (`rapport_cas_types`, essayé sous un taux).

**Ce qui n'est pas vérifié.** `lectures_decision_29.py --cas-types` n'a pas
tourné de bout en bout : son coût se recalcule sous chaque taux, plus de
treize minutes d'après la note de la question 3, et ce chemin-là ne change
pas. Les sorties du récit (`186/2026-11-07-deux-lectures-au-modele.md:146` à
`152`) n'ont donc pas été refaites une à une ; le test tient les neuf mêmes
cas sous d'autres taux.

**Ce qui reste, et ce que le propriétaire tranche.**

- Le lot B continue par `flux_fonction_publique.py` (le journal de la
  liquidation, une lecture de plus au pont), puis `scenarios_meres.py` avec
  `cout_avantages.py --par-carriere`, puis `mortalite_population.py`.
- La note de la question 3 rangeait aussi dans cette première session la
  datation de `cycle_de_vie.py` (lignes 174, 370 et 442) : la demande de
  cette session ne la nommait pas, elle n'est pas faite.
- L'option `--cas-types` : la garder, ou la retirer quand le choix entre les
  lectures A et B sera fait, ses sorties étant déjà au récit. Portée, elle ne
  retient plus le moteur Python ; la décision n'a plus rien d'urgent.

**Tests.** `python -m pytest -m rapide` (4 775 passés, 64 sautés) ; les
fichiers de la zone, `test_age_conjoncturel.py`, `test_age_depart_csp.py`,
`test_cout_age_depart.py`, `test_lectures_decision_29.py`,
`test_flux_fonction_publique.py` et `test_stock_age_legal.py` (102 passés) ;
la prose vérifiée (`python scripts/verifier_prose.py --corriger`).
