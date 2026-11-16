"""Le budget de calcul d'une simulation (docs/architecture.md, § 7.8).

Une constante que le tableau de bord cite et que les tests opposent aux
témoins, ici pour qu'aucun ne l'emprunte au moteur Python (action 161) ; la
liquidation la reprend d'ici.
"""

#: Le nombre déclaré (docs/architecture.md, § 7.8) : les appels de
#: :func:`liquider` qu'une simulation des six scénarios s'accorde PAR DÉPART,
#: liquidations d'essai comprises. Le départ en fait un, et un par avantage que
#: la cascade mesure — les trimestres des enfants, l'AVPF, les points
#: gratuits ; la valorisation des droits acquis, un par scénario prospectif ;
#: et, pour qui est déjà parti à la bascule, les scénarios notionnels refont la
#: liquidation du départ. Quand les régimes liquident à des dates différentes
#: (``droit/departs.py``), chaque départ ouvre ses pensions et fait les siens : le
#: nombre vaut pour chacun, comme pour la pension qu'un assuré mort avant son
#: départ « eût obtenue », liquidée à son décès (``echeancier.py``). Chaque témoin écrit les siens
#: (``tests/temoins/simulations.json``), le portage les refait, et un test
#: refuse qu'un seul dépasse ce nombre, par départ.
APPELS_DECLARES = 6
