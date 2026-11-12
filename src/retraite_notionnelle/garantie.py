"""Le barème de la garantie vieillesse, pour une personne.

La garantie vieillesse du scénario 6 est une allocation SOUS CONDITION DE
RESSOURCES : elle porte la pension à un plancher — 800 € par mois, plus 250 €
d'allocation d'isolement pour qui vit seul —, et, depuis le 9 novembre 2026
(décisions 100 à 102 du programme), elle est DÉGRESSIVE : la pension lui est
retirée en entier jusqu'à la moitié du plancher, de moitié au-delà, et elle
s'éteint à une fois et demie le plancher (:func:`complement_garantie`).

Ce module ne garde que ce barème, que le moteur Python d'une carrière lit
encore (``scenarios/notionnel.py``, ``revalorisation.py``) et qui partira
avec lui. Ce que la garantie coûte sur la distribution des pensions — le
manque moyen d'une tranche, le coût d'une population, d'un sexe ou de deux —
ne s'écrit qu'en JavaScript, ``moteur/js/garantie.js``, qui en porte les
conventions (note de décision 0007, action 161) : le coût le demande au
pont, par lot (:func:`~.pont.garantie`, ``GarantieDistribution`` de
``cout.py``).
"""

from __future__ import annotations


def complement_garantie(plancher: float, ressources: float,
                        part_retrait_entier: float, taux_retrait: float) -> float:
    """Le complément que la garantie sert à des ressources données : son barème.

    DÉGRESSIF, à la forme suédoise (décisions 100 et 102 du programme, 9
    novembre 2026). Jusqu'au pivot, ``part_retrait_entier`` du plancher, chaque
    euro de ressources retire un euro de garantie ; au-delà, il n'en retire que
    ``taux_retrait``, et le complément s'éteint à
    ``pivot + (plancher - pivot) / taux_retrait``. Le plancher est celui de la
    personne, isolement compris : la forme s'y applique en entier. À un et un,
    c'est la garantie différentielle, ``max(0, plancher - ressources)``, au bit
    près. Jumeau de ``complementGarantie`` (``moteur/js/garantie.js``), qui
    fait foi pour une carrière.
    """
    pivot = part_retrait_entier * plancher
    if ressources <= pivot:
        return max(0.0, plancher - ressources)
    return max(0.0, plancher - pivot - taux_retrait * (ressources - pivot))
