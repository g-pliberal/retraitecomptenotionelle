# Étape 6 : les exemples officiels de `test_oracle.py` par le pont — la garde des présomptions au portage, le relevé et le lot B, `test_oracle.py` sans simulateur Python

**La demande.** Le 1er novembre 2026, la garde des présomptions rouge sur
`main` (`presomptions: rouge` dans `.github/etat_suite.yaml`, sur 0e55869), le
propriétaire demande de la réparer d'abord, sans toucher à
`tests/conftest.py`, en faisant décaler au portage les présomptions de son
paquet comme le Python les décale ; puis de finir le septième bloc de
`test_oracle.py`, les 97 mesures que le lot A laissait (note
`2026-11-01-etape-6-les-exemples-officiels-lot-a.md`), une famille par commit
au vert, avec la même méthode ; puis de retirer la fixture `simulateur` et le
simulateur Python de `scripts/simulateurs.py`, devenus inutiles.

**La garde des présomptions** (9891338). Sous `PRESOMPTIONS_DECALEES=1`,
`tests/conftest.py` fait dire au vocabulaire du Python le 1er du mois, les
enfants à vingt-sept ans, le mariage à trente ; le portage lisait les
siennes dans `moteur/donnees.json`, non décalées. Les exemples officiels
passant désormais par le pont, que la garde ne reconnaît pas pour une
confrontation au portage (elle ne saute que les tests qui lancent node
eux-mêmes), trente d'entre eux rougissaient : `attendu 15, lu 1`, et une
naissance d'enfant trois ans plus tôt. `pont.mjs` décale désormais les
présomptions de tout paquet sur lequel il calcule, celui du dépôt comme celui
d'une demande (`sousLaGarde`), et `_signature_du_paquet` porte la garde : le
pont gardé ouvert sans elle se relance sous elle, et inversement. Le test,
vu rouge, est dans `tests/test_pont.py`
(`test_sous_la_garde_des_presomptions_le_portage_les_lit_decalees`) : il lit
chaque valeur décalée par `chronologie.valeur`, sous et sans la garde, et la
compare à `DECALAGES` de `conftest.py`, dont `pont.mjs` garde une copie que le
test tient. La garde entière repasse : 3 375 tests, 166 sautés. La docstring
de `conftest.py` dit encore que le portage n'est pas décalé : vrai des seuls
tests qui lancent node eux-mêmes ; le fichier n'a pas été touché.

**Famille par famille.** Chacune s'ouvre sur son test sans les jumeaux
(`_mesures_sans_les_jumeaux`, avec `choisis` pour en éprouver chaque forme),
vu rouge ; chaque lecture vue refusée par `pont.py`, puis par le portage,
puis portée, et son jumeau dans `JUMEAUX_DU_DROIT`.

- *Le relevé* (31f8207), 6 mesures : la carrière lue sur un relevé
  (`simulateur.carriere_releve`, ses `LigneRelevee` passant par leurs
  champs), déclarée comme `carriere_simple` ; trois projections de
  `releve.construire` : les points de chaque régime (`droits.points`), la
  fiche et les services des emplois classés (`durees.emplois`), les services
  liquidables de régimes nommés.
- *L'invalidité* (0e68c07), 28 mesures : `invalidite.exigences_du_handicap` ;
  la version de la retraite pour invalidité et la pension du fonctionnaire
  invalide, enchaînées dans le portage
  (`invalidite.retraite_pour_invalidite.pension_du_fonctionnaire_invalide`) :
  la version, une fiche du paquet, ne passe pas le pont.
- *La réversion et l'échéancier* (a0c3615), 42 mesures : `reversion.reversion`
  et la réversion que l'échéancier liquide au décès
  (`echeancier.parcourir.reversion`) reviennent entières, sous le dataclass du
  Python (`pont.reversion_des_donnees`) : les champs du portage portent déjà
  les noms du Python, et le contrôle compare chaque champ de chaque régime ;
  les régimes servis en capital passent en ensemble. Le plafond des
  nouvelles pensions de l'activité après le départ, par une projection.
- *Le cumul* (1991f47), 8 mesures : sous les pensions prêtées, sur le
  scénario 1 de la carrière liquidée, que le portage refait
  (`cumul.cumuler.pensions_pretees`), ou tel que l'échéancier le calcule ;
  le cumul revient entier (`pont.cumul_des_donnees`), tranche par tranche.
- *Le foyer, la revalorisation, la paie et le compte* (ebd3495), 13 mesures :
  le minimum vieillesse du foyer ; les majorations exceptionnelles de
  « faire vivre », sur le scénario 1 que le portage refait
  (`pont.majorations_des_donnees`, sans leur montant à l'échéance, que le
  Python dérive) ; les lignes de retraite de la fiche de paie ; la
  cotisation de l'année sous ses deux parts, `_rendu` recevant les paramètres
  du simulateur.
- *La clôture* (75b1732) : l'étage des régimes, que les mois sans pension du
  cumul lisaient au catalogue Python, se lit à celui du portage
  (`scenario_actuel.catalogue.etage`), vu rouge en interdisant
  `CatalogueRegimes.__getitem__` ; la fixture `simulateur`, le paramètre de
  `_mesurer`, de `_confronter` et de `_mesures_sans_les_jumeaux`, et le
  simulateur Python de `scripts/simulateurs.py` s'en vont. Les deux calculs
  Python du résultat, au cumul et à « faire vivre », sont partis avec leur
  famille.

**Le bilan.** Les 488 mesures des 218 exemples passent par le pont, et tout
`test_oracle.py` avec elles. Aucun écart : chaque exemple garde sa valeur
publiée, ses tolérances et ses écarts connus, et le Python refait chaque
appel au bit près. Le pont relit quarante-deux fonctions et lectures, seize
de plus. Un argument qui suit des arguments laissés à leur défaut s'écrit à
sa place, dans l'ordre du jumeau : les `maxima` de la réversion, la carrière
du foyer.

**Ce qui ne change pas.** Aucun fichier fabriqué, aucune règle du moteur, ni
en JavaScript ni en Python ; aucune garde, `tests/conftest.py` compris ;
aucune dépendance, aucune règle du scénario 1.

**Tests.** `python -m pytest -m rapide`, 3 534 ; la garde,
`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`, 3 375, et
`tests/test_oracle.py` sous elle, 277 ; les confrontations légères,
`tests/test_oracle.py`, `tests/test_pont.py`, `tests/test_jumeaux.py`,
`tests/test_simulateurs.py`, `tests/test_destinie.py`,
`tests/test_estimation_officielle.py` et `tests/test_verification.py`, 481.

**Ce qui suit.** Le coût daté par le portage ; puis les retraits, par
sous-ensemble cohérent. `outils_pont.droit_et_refait` et `JUMEAUX_DU_DROIT`
restent tant que les jumeaux Python restent.
