"""Les saisies des tests, lues par le portage : la saisie n'a qu'un
exemplaire, le JavaScript (action 161, étape 6).

Un test qui éprouve une règle du moteur par une saisie en demande la carrière
au pont (:func:`retraite_notionnelle.pont.carrieres_des_saisies`) : le portage
lit la requête comme le site, en bâtit la carrière et les paramètres, et le
moteur Python la simule, qui garde son jumeau. C'est le chemin des témoins
(``scripts/construire_temoins.py``), sur le même paquet, celui du dépôt : une
donnée retouchée n'y entre qu'à la fabrique suivante
(``python scripts/regenerer.py``). Un test qui éprouve la saisie elle-même —
un refus, une date, l'adresse qu'elle écrit — la lit dans le portage, par
``site()`` (:func:`saisie_du_portage`).

    saisies = Saisies()
    comparaison = saisies.simuler({"naissance": "1965-03-15", "liquidation": "2029-04"})
    carriere = saisies.carriere(requete)
    simulateur = saisies.simulateur(requete)

Ce module n'est pas un fichier de tests, et pytest ne le collecte pas.
"""

from __future__ import annotations

import functools
import json
import math
import platform
import sys

from retraite_notionnelle import pont
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Comparaison, Simulateur
from retraite_notionnelle.web.site import module, site

#: La confrontation du moteur Python au portage, qui fait foi (note de
#: décision 0005) et calcule partout comme la libm de Linux
#: (``moteur/js/libm.js``) : au bit près sous Linux x86_64, où GitHub la joue ;
#: ailleurs, la libm du système déplace la dernière décimale de quelques
#: flottants, et elle tolère 10⁻¹² en écart relatif, les types et les textes
#: restant exacts, comme ``_fichier_a_jour`` (``tests/test_web.py``). Les
#: témoins (``tests/test_pont.py``) et les confrontations aux références
#: extérieures la partagent.
TOLERANCE_DU_MOTEUR_PYTHON = (
    0.0 if sys.platform == "linux" and platform.machine() == "x86_64" else 1e-12)


def ecarts_d_ecriture(relu, attendu, chemin: tuple = (), tolerance: float = 0.0) -> list[str]:
    """Les endroits où ``relu`` ne s'écrit pas comme ``attendu`` : une clé, une
    longueur, un nombre, un texte, un type — « 0 » pour « 0.0 » en est un. Avec
    une ``tolerance``, deux flottants égaux à elle près, en écart relatif,
    s'écrivent de même. Une suite se compare élément par élément, liste ou
    n-uplet, comme JSON les écrit."""
    if isinstance(attendu, dict) and isinstance(relu, dict) and sorted(relu) == sorted(attendu):
        return [ecart for cle in attendu
                for ecart in ecarts_d_ecriture(relu[cle], attendu[cle], (*chemin, cle),
                                               tolerance)]
    if (isinstance(attendu, (list, tuple)) and isinstance(relu, (list, tuple))
            and len(relu) == len(attendu)):
        return [ecart for rang, (lu, element) in enumerate(zip(relu, attendu))
                for ecart in ecarts_d_ecriture(lu, element, (*chemin, f"[{rang}]"), tolerance)]
    if json.dumps(relu) == json.dumps(attendu):
        return []
    if (tolerance and type(relu) is float and type(attendu) is float
            and math.isclose(relu, attendu, rel_tol=tolerance)):
        return []
    return [f"{'.'.join(chemin)} : attendu {json.dumps(attendu)[:60]}, "
            f"lu {json.dumps(relu)[:60]}"]


def scenario_actuel_en_donnees(comparaison: Comparaison) -> dict:
    """Ce que :func:`pont.scenario_actuel` rend du portage, tiré d'une
    comparaison du moteur Python, son jumeau : les mêmes champs, relus sous
    les mêmes types (:func:`pont.scenario_actuel_des_donnees`) — le zéro d'une
    somme vide, que le moteur Python rend entier, y devient « 0.0 », comme
    dans les témoins."""
    actuel, reversion = comparaison.actuel, comparaison.reversion
    date = comparaison.carriere.date_liquidation
    return pont.scenario_actuel_des_donnees({
        "annee_liquidation": date.annee,
        "mois_liquidation": date.mois,
        "coefficient_euros_constants": comparaison.coefficient_euros_constants,
        "actuel": {
            "pension_annuelle": actuel.pension_annuelle,
            "pension_hors_repartition": actuel.pension_hors_repartition,
            "pensions_par_regime": [
                {"regime": pension.regime, "montant": pension.montant,
                 "detail": pension.detail}
                for pension in actuel.pensions_par_regime],
            "avantages_appliques": [
                {"code": avantage.code, "montant": avantage.montant,
                 "par_regime": [[regime, part] for regime, part in avantage.par_regime]}
                for avantage in actuel.avantages_appliques],
            "trimestres_valides": actuel.trimestres_valides,
            "taux_liquidation": actuel.taux_liquidation,
            "liquidation_ouverte": actuel.liquidation_ouverte,
            "motif_ouverture": actuel.motif_ouverture,
        },
        "reversion": None if reversion is None else {
            "annee": reversion.annee,
            "regimes": [{"regime": ligne.regime, "montant": ligne.montant,
                         "date_effet": ligne.date_effet}
                        for ligne in reversion.regimes],
        },
    })


class RefusDuPortage(Exception):
    """Le portage refuse la requête : sa saisie, ou le modèle quand il en
    bâtit la carrière. Le message est son motif, tel que le site l'écrit."""


def _chaines(requete: dict) -> dict[str, str]:
    """Une requête d'adresse ne porte que des chaînes, comme
    ``URLSearchParams`` ; une valeur absente n'y est pas."""
    return {str(cle): str(valeur) for cle, valeur in requete.items() if valeur is not None}


class Saisies:
    """Ce que le contexte du site fait d'une requête, la carrière bâtie par le
    portage, et un simulateur Python par jeu de paramètres, comme lui."""

    def __init__(self) -> None:
        self._simulateurs: dict[Parametres, Simulateur] = {}

    def lire(self, requete: dict, prolonger: bool = True):
        """Les paramètres de la saisie, et la carrière que le site simulerait ;
        ``prolonger=False`` s'en tient aux années d'un relevé."""
        cas = {"cle": "saisie", "requete": _chaines(requete)}
        if not prolonger:
            cas["prolonger"] = False
        lus, refus = pont.carrieres_des_saisies([cas])
        if refus:
            raise RefusDuPortage(refus["saisie"])
        return lus["saisie"]

    def parametres(self, requete: dict) -> Parametres:
        return self.lire(requete)[0]

    def carriere(self, requete: dict, prolonger: bool = True):
        return self.lire(requete, prolonger)[1]

    def simulateur(self, de: dict | Parametres | None = None) -> Simulateur:
        """Le simulateur des paramètres d'une requête, de ``de`` lui-même, ou
        des réglages de référence."""
        parametres = (Parametres() if de is None
                      else self.parametres(de) if isinstance(de, dict) else de)
        if parametres not in self._simulateurs:
            self._simulateurs[parametres] = Simulateur(parametres)
        return self._simulateurs[parametres]

    def simuler(self, requete: dict) -> Comparaison:
        """Les quatre systèmes sur la carrière de la saisie : pour une saisie
        par la pension, celle que le portage trouve en l'inversant, sans le
        niveau trouvé (``niveau_inverse``)."""
        parametres, carriere = self.lire(requete)
        return self.simulateur(parametres).simuler(carriere)

    def scenario_actuel(self, cas: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
        """Ce que :func:`pont.scenario_actuel` sert de chaque cas, ``{"cle",
        "requete", "prolonger"}``, refait au moteur Python tant qu'il garde ses
        jumeaux (action 161) : la carrière que le portage bâtit de la même
        requête, tel quel le relevé que l'appelant a prolongé, simulée par le
        jumeau Python, sous les champs et les types du pont
        (:func:`scenario_actuel_en_donnees`). Puis, sous leur clé, les motifs
        des requêtes que le portage refuse."""
        carrieres, refus = pont.carrieres_des_saisies(cas)
        return ({cle: scenario_actuel_en_donnees(self.simulateur(parametres).simuler(carriere))
                 for cle, (parametres, carriere) in carrieres.items()}, refus)


#: Le pont du scénario 1 tel quel, que :func:`servi_et_refait` appelle quand
#: une confrontation la met à sa place.
SCENARIO_ACTUEL_DU_PORTAGE = pont.scenario_actuel


@functools.cache
def _saisies() -> Saisies:
    """Les saisies du moteur Python que confrontent :func:`servi_et_refait`,
    un simulateur par jeu de paramètres, gardés d'un cas à l'autre."""
    return Saisies()


def servi_et_refait(cas: list[dict], paquet: bytes | None = None,
                    ) -> tuple[dict[str, dict], dict[str, str]]:
    """Ce que le portage sert de chaque cas (:func:`pont.scenario_actuel`), le
    moteur Python confronté tant qu'il garde ses jumeaux (action 161) : il doit
    le refaire au bit près sous Linux x86_64
    (:data:`TOLERANCE_DU_MOTEUR_PYTHON`), et refuser ce que le portage
    refuse, ou la confrontation s'arrête sur ce qui diffère. Une confrontation
    la met à la place du pont : chacun de ses cas éprouve les deux moteurs, et
    aucun chemin que les témoins n'exercent ne perd la vérification du
    Python. Sur un autre paquet que celui du dépôt, il n'y a rien à refaire."""
    servis, refus = SCENARIO_ACTUEL_DU_PORTAGE(cas, paquet)
    if paquet is not None:
        return servis, refus
    refaits, refus_du_python = _saisies().scenario_actuel(cas)
    ecarts = [f"{cle} : le portage le refuse ({refus[cle]}), le moteur Python le sert"
              for cle in refaits if cle in refus]
    ecarts += [f"{cle} : le moteur Python le refuse ({motif}), le portage le sert"
               for cle, motif in refus_du_python.items() if cle in servis]
    ecarts += [f"{cle}, {ecart}" for cle, servi in servis.items() if cle in refaits
               for ecart in ecarts_d_ecriture(refaits[cle], servi,
                                              tolerance=TOLERANCE_DU_MOTEUR_PYTHON)]
    if ecarts:
        raise AssertionError("le moteur Python ne refait pas ce que le portage sert "
                             f"({len(ecarts)} écart(s)) : " + " ; ".join(ecarts[:5]))
    return servis, refus


@functools.cache
def _presomptions():
    """Les présomptions du paquet que le site a lu, lues une fois : le paquet
    entier passe le fil pour qu'on les y prenne."""
    return site().contexte.paquet.presomptions


def refus_de_la_saisie(fragment: str) -> str:
    """Ce que ``pytest.raises(ErreurSite, match=…)`` cherche d'un refus de la
    saisie du portage : ``fragment``, une expression régulière, dans la ligne
    de son motif, et non dans la pile qui la suit."""
    return r"\AErreurSaisie : .*" + fragment


def saisie_du_portage(requete: dict):
    """La saisie du portage, lue d'une requête comme le site la lit, sur les
    présomptions du paquet : un objet du portage, dont les champs se lisent
    et les méthodes s'appellent depuis le Python (``site.py``) ; un refus
    lève ``ErreurSite``, avec son motif."""
    return module("saisie").Saisie.depuis_requete(_chaines(requete), False, _presomptions())
