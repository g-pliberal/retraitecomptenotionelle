# Étape 6 : les exemples officiels de `test_oracle.py` par le pont — le lot A, les carrières, la liquidation, l'ouverture et le RAFP au portage

**La demande.** Le 1er novembre 2026, la course 1175 verte sur `main`
(cf9fa6e) et le resserrement du dépliant de la page Méthode validé (9c38349),
le propriétaire ouvre le septième et dernier bloc de `test_oracle.py`, les 218
exemples officiels (`_carriere_exemple`, `_mesurer`, `_cumul_exemple`,
`_confronter`), avec la méthode des six premiers : un commit au vert par
famille de fonctions, chaque déclaration vue refusée puis portée dans
`pont.py`, `pont.mjs` et `JUMEAUX_DU_DROIT`, le Python contrôlé au bit près par
`droit_et_refait` et chaque famille par un test sans les jumeaux. Le lot A, les
carrières et les grandeurs de base ; le lot B, les grandeurs spécialisées
(invalidité, réversion, échéancier, cumul, foyer, revalorisation, rémunération,
compte) ; le lot B à la session suivante si le contexte se remplit. Et
corriger la consigne `node --test tests/js/` en `node --test tests/js/*.test.js`.

**Les carrières des exemples** (155e309). `_carriere_exemple` fait dire au
portage le mois d'où les âges se comptent (`calendrier.origine_des_ages`, et
`chronologie.valeur` pour le jour présumé), bâtir la carrière
(`simulateur.carriere_simple`, le simulateur désigné par `pont.SIMULATEUR`,
ses tables par année relues en `Map`) et la liquider. La carrière revient en
Python par `pont.carriere_des_donnees`, où des grandeurs la lisent encore ; sa
relecture (`pont.carriere_relue`) la réécrit en données, pour que le contrôle
la compare champ par champ. Le résultat relu porte désormais ce que `_mesurer`
lit : la durée requise, le type de calcul de chaque pension, le détail de
chaque avantage, les départs inscrits (`actuelEnDonnees`,
`pont.actuel_des_donnees`, et leur miroir `outils_pont.actuel_en_donnees`,
que Destinie 2 et l'estimation officielle partagent) ; `_mesurer` le lit en
dictionnaire. Les deux branches du lot B qui passaient le résultat Python au
cumul et à « faire vivre » le recalculent sur la même carrière
(`actuel.calculer`), le temps de leur tour. `scripts/simulateurs.py`, qui
interroge le scénario 1 par les fonctions de l'oracle, suit la signature
`_carriere_exemple(exemple)` ; `test_simulateurs.py` le tient.
`ecarts_d_ecriture` compare un dataclass champ par champ. Le test sans les
jumeaux bâtit et liquide un exemple de chacune des dix formes : âge de début,
début daté, trimestres à retrouver, conjoint et décès, emploi après le
départ, carrière hors de France, invalidité, temps partiel, interruptions,
enfants. Vu rouge sur la mesure d'avant, remaniée d'abord sans changer de
moteur.

**La recherche des trimestres, et son coût.** 71 exemples ne donnent que
leurs trimestres, et 35 les recherchent encore un trimestre plus tôt : jusqu'à
33 âges de début essayés chacun, dans l'ordre, le premier qui rend le nombre
publié retenu. La première version faisait passer chaque carrière essayée par
le pont, en données, dans les deux sens : le bloc passait de 16 à 48 secondes
en série, et le profil montrait les conversions et les comparaisons de ces
carrières coûter autant que le jumeau Python. D'où `pont.CarriereSimple`, vu
rouge dans `test_pont.py` : la carrière qu'un essai liquide se bâtit de ses
options dans le portage, et le jumeau Python de même, sans passer ; seule la
carrière retenue revient en données. Les essais vont par paquets de huit, dans
l'ordre : le choix est celui d'un essai après l'autre. Le bloc tient en
30 secondes en série, le fichier en 14 secondes en parallèle (7,2 avant le
bloc) : le portage qui calcule, et le Python qui refait tout.

**Bloc par bloc.**

- *L'ouverture* (e45b5a4), 54 mesures : l'âge d'ouverture, le mois où il est
  atteint et la date d'effet au plus tôt (`ouvrir.age_ouverture_droit`,
  `calendrier.en_mois`, `carriere.date_de_l_age`).
- *La liquidation* (d606694), 16 mesures : les années que retient le salaire
  annuel moyen (`liquider.nombre_d_annees_retenues`), la pension rapportée à
  lui et au plafond, la valeur de service au jour du départ, sur la période du
  régime désignée (`pont.Periode`).
- *Le RAFP* (487eef2), 23 mesures : l'âge légal qui l'ouvre
  (`departs.age_legal`), sa majoration, les mois après la retraite de base, sa
  prestation (`liquider.prestation_rafp`, relue par
  `pont.prestation_rafp_des_donnees` sous ses six champs) et le seuil en
  points de sa période (`periode.capital_seuil_points`). Le portage lit le
  rang de la date d'effet : elle lui passe en vraie `DateMois`. Le test sans
  les jumeaux éprouve chaque forme — rente, non ouverte, capital, capital
  fractionné — et l'exemple qui date sa retraite de base.

**La consigne de node** (104df6a). La docstring de `scripts/jumeaux.py` disait
`node --test tests/js/` ; le script lançait déjà les fichiers `*.test.js`. Elle
dit la forme que node 22 accepte. Les consignes des dossiers ne la citaient
pas.

**Le bilan.** 391 des 488 mesures des 218 exemples passent par le pont. Aucun
écart : chaque exemple garde sa valeur publiée, ses tolérances et ses écarts
connus, et le Python refait chaque appel au bit près. Le pont relit
vingt-six fonctions et lectures, dont douze de cette session ; ses arguments
désignent le simulateur, le moteur et ses tables prêtées, la période d'un
régime, une carrière bâtie en Python, une carrière bâtie d'options, une
valeur.

**Ce qui ne change pas.** Aucun fichier fabriqué, aucune règle du moteur, ni
en JavaScript ni en Python ; aucune garde, aucune dépendance, aucune règle du
scénario 1.

**Tests.** `python -m pytest -m rapide`, 3 533 ; les confrontations légères,
`tests/test_pont.py`, `tests/test_jumeaux.py` et `tests/test_simulateurs.py`,
475 ; `node --test tests/js/*.test.js`, 115 essais.

**Ce qui reste : 97 mesures**, que `_mesurer` calcule encore au moteur Python
sur la carrière que le portage a bâtie. Chaque famille se mène comme les
autres : le test sans les jumeaux (`_mesures_sans_les_jumeaux`, avec
`choisis` pour éprouver chaque forme), vu rouge ; la branche par `_rendu` ;
chaque lecture vue refusée par `pont.py`, puis par le portage, puis portée, et
son jumeau dans `JUMEAUX_DU_DROIT` (un dataclass rendu y passe par
`dataclasses.asdict`). Un objet rendu se relit par une fonction qui en vérifie
les champs, comme `prestation_rafp_des_donnees` ; une date passée à une
fonction qui en lit le rang se reconstruit en `DateMois` dans `pont.mjs`.

- *Le relevé*, 6 mesures, la dernière famille du lot A : `points_de_l_annee`
  bâtit sa carrière d'un relevé (`Carriere.depuis_releve`, `LigneRelevee`), à
  déclarer comme `carriere_simple` ; puis trois projections de
  `releve.construire` : les services de chaque fiche des bonifications
  (`durees.emplois`), les services liquidables d'un régime
  (`durees.services_liquidables`), les points de chaque régime
  (`droits.points`).
- *L'invalidité*, 28 mesures : `invalidite.exigences_du_handicap` (24, sur la
  durée requise du résultat) ; `retraite_pour_invalidite` rend la version que
  `pension_du_fonctionnaire_invalide` reçoit — un objet qui passe d'un appel à
  l'autre : une seule fonction déclarée qui les enchaîne dans le portage, ou
  la version relue puis repassée en données.
- *La réversion et l'échéancier*, 42 mesures : `reversion.reversion` (les
  pensions prêtées, leurs fiabilités écrites par leur valeur, les `maxima`) ;
  `Echeancier(simulateur).parcourir(carriere)` pour les dates d'effet et de
  révision de la réversion et les plafonds des nouvelles pensions — une
  projection de ce que le test en lit.
- *Le cumul*, 8 mesures : `cumul.cumuler` reçoit le résultat Python et une
  fonction des pensions de chaque année ; le portage refera le résultat
  lui-même et bâtira la fonction des pensions prêtées.
- *Le foyer, la revalorisation, la rémunération, le compte*, 13 mesures :
  `foyer.foyer_et_net` (le minimum vieillesse), `revalorisation.faire_vivre`
  (la majoration exceptionnelle, sur le résultat que le portage refera),
  `remuneration.fiche_depuis_brut` (les lignes de retraite de la fiche de
  paie), `ConstructeurCompte` sous deux parts de cotisation (le paramètre
  `parametres` de `pont.droit`).
- *À la fin* : la fixture `simulateur`, le paramètre `simulateur` de
  `_mesurer`, de `_confronter` et de `_cumul_exemple`, le simulateur Python de
  la classe de `scripts/simulateurs.py` qui les appelle, et les deux calculs
  Python du résultat que le cumul et « faire vivre » refont, s'en vont avec
  la dernière branche. Restent alors, côté Python, `DateMois` et la
  `Carriere` relue, que le pont lui-même lit.

**Ce qui suit.** Le relevé, puis le lot B, une famille par commit ; puis le
coût daté par le portage ; puis les retraits, par sous-ensemble cohérent.
