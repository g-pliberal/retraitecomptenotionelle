"""Le pilote (docs/architecture.md, § 7.7) : ce que le droit ne décide pas.

Le moteur ne devine rien : il liquide la demande qu'on lui fait. Hors de lui,
un pilote fixe le reste.

* LES COMPORTEMENTS : partir au taux plein, à l'âge où le droit s'ouvre,
  après une durée de services. :func:`age_de_depart` interroge le moteur, au
  besoin plusieurs fois, jusqu'à un point fixe ; il ne lui faut qu'un âge, et
  il n'interroge donc que l'étape « ouvrir le droit »
  (:func:`~retraite_notionnelle.droit.ouvrir.age_ouverture_droit`,
  :func:`~retraite_notionnelle.droit.ouvrir.age_taux_plein_droit`), sans rien
  liquider. La date qu'il trouve devient celle du départ de la carrière, que
  l'échéancier traite (:mod:`~retraite_notionnelle.echeancier`).
* LES POPULATIONS : aujourd'hui les cas types pondérés, que
  :mod:`~retraite_notionnelle.castypes` décrit ; des tirages, des couples et
  des décès simulés demain, sans changer le moteur.
* LES CASCADES de neutralisations, et les paramètres qui dépendent d'une
  population — le coefficient d'équilibre, que la page Coût calcule sans
  l'appliquer — restent dans leurs modules
  (:mod:`~retraite_notionnelle.avantages`, :mod:`~retraite_notionnelle.cout`).

Son jumeau est ``moteur/js/pilote.js``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .droit import ouvrir

if TYPE_CHECKING:
    from .castypes import CasType
    from .simulateur import Simulateur


#: Les deux façons de dater le départ d'un cas type.
#:
#: ``droit`` est celle des résultats affichés : chaque génération liquide à
#: l'âge que SON droit lui ouvre. ``absolu`` est l'ancienne, gardée non comme
#: repli mais comme variante — l'âge écrit dans la grille, le même pour toutes
#: les générations, qui faisait partir la génération 1940 à soixante-quatre ans
#: en 2004 alors que la loi ne les lui a jamais demandés.
VARIANTES_LIQUIDATION: tuple[str, ...] = ("droit", "absolu")

#: Nombre de fois que l'âge de liquidation est rapproché de l'âge d'ouverture.
#: Il en faut plus d'une : l'âge qu'une fiche de régime oppose dépend de
#: l'ANNÉE de liquidation — celle de la SNCF et celle des IEG montent d'un
#: trimestre par millésime —, si bien que déplacer l'âge déplace la réponse.
#: Deux passes suffisent partout dans la grille ; les deux autres sont la marge.
PASSES_LIQUIDATION = 4


def age_de_depart(simulateur: Simulateur, cas: CasType, generation: int,
                  variante: str = "droit") -> float:
    """L'âge auquel le cas type ``cas`` liquide, étant née en ``generation``.

    **Pourquoi ce n'est pas un nombre.** Un cas type décrit une carrière,
    pas une date : « le salarié au salaire moyen » n'est pas « celui qui
    part à soixante-quatre ans », c'est celui qui part quand la loi le lui
    permet. Écrire l'âge revenait à faire partir à soixante-quatre ans une
    génération née en 1940 — c'est-à-dire en 2004, sous un droit qui en
    demandait soixante —, et à donner au modèle un stock de retraités trop
    vieux au départ de la projection, donc trop rapide à croître.

    **Comment la réponse est trouvée.** L'âge d'ouverture dépend de la
    carrière, laquelle dépend de l'âge de liquidation : la question tourne
    en rond, et on la résout par un POINT FIXE. On part de l'âge écrit, on
    demande au scénario 1 ce que le droit oppose à cette liquidation-là, on
    recommence. Deux garde-fous : le nombre de passes est borné, et une
    descente n'est retenue que si l'âge plus précoce est lui-même ouvert.
    Le second n'est pas décoratif — la CANCAVA ouvrait à soixante-cinq ans
    jusqu'en 1972 et à soixante à partir de 1973, si bien qu'un artisan né
    en 1910 « ouvre » à soixante ans un droit que son année de départ lui
    refuse. Dans ce cas la règle ne descend pas plus bas que l'âge que ce
    départ-là confirme, et reste où elle est s'il n'y en a pas de plus
    précoce.
    """
    if variante not in VARIANTES_LIQUIDATION:
        raise ValueError(
            f"variante de liquidation inconnue : {variante!r} "
            f"(attendu : {VARIANTES_LIQUIDATION})"
        )
    if variante == "absolu":
        return cas.age_liquidation
    if cas.regle_liquidation == "services":
        return cas.age_debut + cas.ecart_liquidation
    if cas.regle_liquidation not in ("ouverture", "taux_plein"):
        raise ValueError(
            f"règle de liquidation inconnue : {cas.regle_liquidation!r}"
        )
    age = cas.age_liquidation
    for _ in range(PASSES_LIQUIDATION):
        propose = age_propose(simulateur, cas, generation, age)
        if propose is None or abs(propose - age) < 1e-9:
            break
        if propose > age:
            age = propose
            continue
        confirme = age_propose(simulateur, cas, generation, propose)
        if confirme is None:
            break
        if confirme > propose + 1e-9:
            # L'âge plus précoce n'est pas ouvert sous SES règles, mais le
            # droit peut s'ouvrir entre les deux : depuis la suspension de
            # 2026, la durée opposable dépend de la date d'effet, et un né
            # en 1965 que la règle de 2027 ferait partir à 60 ans et 9 mois
            # part à 61 ans sous celle de 2026. On essaie donc l'âge que le
            # droit oppose alors, s'il reste plus précoce que l'âge retenu.
            if confirme < age - 1e-9:
                age = confirme
                continue
            break
        age = propose
    return age


def age_propose(simulateur: Simulateur, cas: CasType, generation: int,
                age: float) -> float | None:
    """Ce que la règle du cas type oppose à sa carrière liquidée à ``age``,
    décalé : la seule question que le pilote pose au moteur, à l'étape
    « ouvrir le droit », sans rien liquider."""
    actuel = simulateur.scenario_actuel
    carriere = cas._carriere(simulateur, generation, age)
    reference = (
        ouvrir.age_taux_plein_droit(actuel, carriere)
        if cas.regle_liquidation == "taux_plein"
        else ouvrir.age_ouverture_droit(actuel, carriere)
    )
    return None if reference is None else reference + cas.ecart_liquidation
