"""La grille des carrières types, refaite par la façade (action 161).

Les tests de la table des agrégats et des affirmations la refaisaient par
``castypes.calculer_cas_types`` sur le simulateur du contexte, que le pilote
et le moteur Python datait et simulait. Le contexte ne bâtit plus que le
simulateur de données seules : la grille se refait ici au portage, chaque
case datée et écartée par lui (``castypes.cases_de_la_grille``), bâtie et
simulée par la façade, qui rend la ``Comparaison`` entière que ces tests
lisent.
"""

from __future__ import annotations

from retraite_notionnelle.castypes import (
    CAS_TYPES, GENERATIONS, ResultatCasTypes, cases_de_la_grille,
)

from facade import Simulateur


def grille_a_la_facade(simulateur: Simulateur | None = None, cas_types=CAS_TYPES,
                       generations=GENERATIONS) -> ResultatCasTypes:
    """La grille cas type × génération, ses cases écartées sous leur motif."""
    simulateur = simulateur or Simulateur()
    options, echecs = cases_de_la_grille(simulateur, cas_types, generations)
    fiches = {cas.code: cas for cas in cas_types}
    return ResultatCasTypes(
        resultats={(code, generation): simulateur.simuler(fiches[code].carriere_a(
            simulateur, generation, option["age_liquidation"]))
            for (code, generation), option in options.items()},
        echecs=echecs)
