"""La garantie d'une population, pour les tests : elle ne s'écrit qu'en
JavaScript (``moteur/js/garantie.js``, note de décision 0007, action 161).

Un test qui éprouve son barème — le manque moyen d'une tranche, le coût sur
une distribution, d'un sexe ou de deux, la pension moyenne — le demande au
pont (:func:`retraite_notionnelle.pont.garantie`), comme le coût : ces
fonctions gardent la signature que le Python leur donnait, et ne passent au
portage que les arguments qu'on leur donne, pour que ceux qu'il tient par
défaut, le barème différentiel, restent les siens. Un refus du barème lève
``ValueError``, du message du portage.

Ce module n'est pas un fichier de tests, et pytest ne le collecte pas.
"""

from __future__ import annotations

from retraite_notionnelle import pont


def _donnes(*valeurs) -> list:
    """Les arguments facultatifs qu'un test a donnés : ceux de la fin qu'il
    tait ne passent pas, et un que le test tait avant un autre vaut un, ce
    que le portage lui donne."""
    donnes = list(valeurs)
    while donnes and donnes[-1] is None:
        donnes.pop()
    return [1.0 if valeur is None else valeur for valeur in donnes]


def _un(fonction: str, *arguments):
    [rendu] = pont.garantie([(fonction, *arguments)])
    return rendu


def manque_moyen(borne_inferieure, borne_superieure, plancher,
                 part_retrait_entier=None, taux_retrait=None):
    """``manqueMoyen`` : la part de la tranche que la garantie sert, et le
    complément moyen sur toute la tranche."""
    return _un("manque_moyen", borne_inferieure, borne_superieure, plancher,
               *_donnes(part_retrait_entier, taux_retrait))


def cout_garantie(distribution, effectif_total, plancher_mensuel, facteur=None, *,
                  part_retrait_entier=None, taux_retrait=None):
    """``coutGarantie`` : le barème appliqué à la distribution."""
    return _un("cout_garantie", distribution, effectif_total, plancher_mensuel,
               *_donnes(facteur, part_retrait_entier, taux_retrait))


def cout_garantie_par_sexe(femmes, hommes, part_femmes, effectif_total, plancher_mensuel,
                           facteur, rapport, plancher_majore=None, part_seule=None, *,
                           part_retrait_entier=None, taux_retrait=None):
    """``coutGarantieParSexe`` : le barème appliqué aux deux sexes à part."""
    return _un("cout_garantie_par_sexe", femmes, hommes, part_femmes, effectif_total,
               plancher_mensuel, facteur, rapport, plancher_majore, part_seule,
               *_donnes(part_retrait_entier, taux_retrait))


def pension_moyenne(distribution) -> float:
    """``pensionMoyenne`` : la pension moyenne de la distribution."""
    return _un("pension_moyenne", distribution)
