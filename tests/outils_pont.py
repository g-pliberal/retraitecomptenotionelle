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

import contextlib
import dataclasses
import functools
import json
import math
import platform
import sys

from retraite_notionnelle import calendrier, chronologie, pont
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.regimes import BORNES_ASSIETTE
from retraite_notionnelle.droit import (cumul, departs, foyer, invalidite, liquider,
                                        ouvrir, releve, reversion)
from retraite_notionnelle.echeancier import Echeancier
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.remuneration import fiche_depuis_brut
from retraite_notionnelle.revalorisation import faire_vivre
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
    n-uplet, comme JSON les écrit ; un dataclass, de même type, champ par
    champ."""
    if any(dataclasses.is_dataclass(valeur) and not isinstance(valeur, type)
           for valeur in (relu, attendu)):
        if type(relu) is not type(attendu):
            return [f"{'.'.join(map(str, chemin))} : attendu un {type(attendu).__name__}, "
                    f"lu un {type(relu).__name__}"]
        relu, attendu = ({champ.name: getattr(valeur, champ.name)
                          for champ in dataclasses.fields(valeur)} for valeur in (relu, attendu))
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
    return [f"{'.'.join(map(str, chemin))} : attendu {json.dumps(attendu)[:60]}, "
            f"lu {json.dumps(relu)[:60]}"]


#: Les jumeaux Python qui datent, bâtissent et simulent la grille du coût : le
#: pilote, l'ouverture du droit qu'il interroge, les constructeurs de
#: carrières, la projection des primes et le moteur Python.
JUMEAUX_DU_COUT = (("pilote", "age_de_depart"), ("pilote", "point_fixe"),
                   ("pilote", "descendre"), ("ouvrir", "age_ouverture_droit"),
                   ("ouvrir", "age_taux_plein_droit"), ("ouvrir", "age_annulation_droit"),
                   ("Simulateur", "carriere_simple"), ("Simulateur", "carriere_parcours"),
                   ("Simulateur", "simuler"), ("Simulateur", "proposition"),
                   ("Carriere", "prolongee"), ("castypes", "primes_projetees"))


def empecher_les_jumeaux_du_cout(monkeypatch) -> None:
    """Les jumeaux de :data:`JUMEAUX_DU_COUT` empêchés de calculer : ce que le
    coût demande de sa grille, seul le portage peut le rendre."""
    from retraite_notionnelle import castypes, pilote
    from retraite_notionnelle.carriere import Carriere
    from retraite_notionnelle.droit import ouvrir

    objets = {"pilote": pilote, "ouvrir": ouvrir, "Simulateur": Simulateur,
              "Carriere": Carriere, "castypes": castypes}

    def interdit(*_, **__):
        raise AssertionError("un jumeau Python date, bâtit ou simule la grille du coût")

    for objet, nom in JUMEAUX_DU_COUT:
        monkeypatch.setattr(objets[objet], nom, interdit)


def actuel_en_donnees(actuel) -> dict:
    """Le résultat du scénario 1 du moteur Python (``ResultatActuel``) tel que
    le portage écrit le sien (``actuelEnDonnees`` de ``pont.mjs``), avant sa
    relecture sous les types du pont (:func:`pont.actuel_des_donnees`)."""
    return {
        "pension_annuelle": actuel.pension_annuelle,
        "pension_hors_repartition": actuel.pension_hors_repartition,
        "pensions_par_regime": [
            {"regime": pension.regime, "montant": pension.montant,
             "type_calcul": pension.type_calcul, "detail": pension.detail}
            for pension in actuel.pensions_par_regime],
        "avantages_appliques": [
            {"code": avantage.code, "montant": avantage.montant, "detail": avantage.detail,
             "par_regime": [[regime, part] for regime, part in avantage.par_regime],
             "par_regime_sans_anticipation": [
                 [regime, part] for regime, part in avantage.par_regime_sans_anticipation],
             "a_charge": [[depuis, [[regime, part] for regime, part in parts]]
                          for depuis, parts in avantage.a_charge]}
            for avantage in actuel.avantages_appliques],
        "trimestres_valides": actuel.trimestres_valides,
        "trimestres_requis": actuel.trimestres_requis,
        "taux_liquidation": actuel.taux_liquidation,
        "liquidation_ouverte": actuel.liquidation_ouverte,
        "motif_ouverture": actuel.motif_ouverture,
        "departs": [{"date_effet": depart.date_effet, "motif": depart.motif}
                    for depart in actuel.departs],
    }


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
        "actuel": actuel_en_donnees(actuel),
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


def _pension_pour_invalidite(moteur, regime: str, carriere, *valeurs):
    """La version de la retraite pour invalidité d'un régime, puis la pension
    du fonctionnaire qu'elle sert, sous ses autres arguments — la pension, le
    traitement, l'année : ce que le portage enchaîne ; aucune pension sans
    version."""
    version = invalidite.retraite_pour_invalidite(moteur, regime, carriere)
    return None if version is None else invalidite.pension_du_fonctionnaire_invalide(
        moteur, carriere, version, *valeurs)


def _en_dictionnaire(objet):
    """Un dataclass rendu, par ses champs, comme le portage l'écrit ; ``None``
    tel quel."""
    return None if objet is None else dataclasses.asdict(objet)


def _reversion(moteur, pensions, carriere, annee, deces_suppose=None, en_capital=(), *autres):
    """La réversion que des pensions ouvrent, ses régimes servis en capital en
    ensemble, comme le portage les lit."""
    return _en_dictionnaire(reversion.reversion(moteur, pensions, carriere, annee, deces_suppose,
                                                frozenset(en_capital), *autres))


def _parcourue(simulateur: Simulateur, carriere) -> Echeancier:
    """L'échéancier du simulateur, la carrière parcourue."""
    echeancier = Echeancier(simulateur)
    echeancier.parcourir(carriere)
    return echeancier


def _cumul_des_pensions_pretees(moteur, carriere, liquidee, pretees: dict,
                                annee_courante: int):
    """Le cumul de l'activité après le départ, chaque régime servant chaque
    année la pension prêtée, sans majoration pour enfants, sur le scénario 1
    de la carrière liquidée : ce que le portage refait."""
    return _en_dictionnaire(cumul.cumuler(moteur, carriere, moteur.calculer(liquidee),
                                          lambda annee: (dict(pretees), 0.0), annee_courante))


def _lignes_de_retraite(simulateur: Simulateur, statut: str, annee: int, brut: float):
    """Les lignes de retraite de la fiche de paie d'un revenu brut annuel,
    ``(code, part du salarié)`` ; aucune sans fiche."""
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations, statut, annee, brut)
    return None if fiche is None else tuple((ligne.code, ligne.salarie)
                                            for ligne in fiche.lignes if ligne.retraite)


def _plafonds_apres_le_depart(simulateur: Simulateur, carriere):
    """Le plafond de chaque nouvelle pension que l'activité après le départ
    constitue, ``(regime, plafond)`` ; aucune sans activité."""
    droits = _parcourue(simulateur, carriere).au_depart.droits_apres_depart
    return None if droits is None else tuple((p.regime, p.plafond) for p in droits.pensions)


#: Le jumeau Python de chaque fonction du droit que le pont fait appeler
#: (``FONCTIONS_DU_DROIT`` de ``pont.mjs``, :data:`pont.LECTURES_DU_DROIT`),
#: sous les mêmes arguments, que :func:`droit_et_refait` lui fait refaire tant
#: qu'il reste (action 161) : une fonction de plus au pont y déclare le sien.
JUMEAUX_DU_DROIT = {
    "calendrier.en_mois": calendrier.en_mois,
    "calendrier.origine_des_ages": lambda naissance, jour: dataclasses.asdict(
        calendrier.origine_des_ages(naissance, jour)),
    "carriere.date_de_l_age": lambda carriere, age: dataclasses.asdict(
        carriere.date_de_l_age(age)),
    "departs.age_legal": departs.age_legal,
    "chronologie.valeur": chronologie.valeur,
    "compte.cotisation_annuelle.par_regime": lambda simulateur, carriere, annee: (
        ConstructeurCompte(simulateur.macro, simulateur.catalogue, simulateur.affiliations,
                           simulateur.indexation, simulateur.parametres)
        .cotisation_annuelle(carriere, annee).par_regime),
    "cumul.cumuler.pensions_pretees": _cumul_des_pensions_pretees,
    "echeancier.parcourir.au_depart.cumul": lambda simulateur, carriere: _en_dictionnaire(
        _parcourue(simulateur, carriere).au_depart.cumul),
    "echeancier.parcourir.reversion": lambda simulateur, carriere: _en_dictionnaire(
        _parcourue(simulateur, carriere).reversion),
    "echeancier.parcourir.au_depart.droits_apres_depart.pensions": _plafonds_apres_le_depart,
    "foyer.foyer_et_net.minimum_vieillesse":
        lambda *valeurs: foyer.foyer_et_net(*valeurs).minimum_vieillesse,
    "invalidite.exigences_du_handicap": invalidite.exigences_du_handicap,
    "invalidite.retraite_pour_invalidite.pension_du_fonctionnaire_invalide":
        _pension_pour_invalidite,
    "ouvrir.age_ouverture_droit": ouvrir.age_ouverture_droit,
    "ouvrir.duree_requise": ouvrir.duree_requise,
    "periode.capital_seuil_points": lambda periode: periode.capital_seuil_points,
    "liquider.duree_proratisation": liquider.duree_proratisation,
    "liquider.majoration_rafp": liquider.majoration_rafp,
    "liquider.mois_apres_le_depart": liquider.mois_apres_le_depart,
    "liquider.nombre_d_annees_retenues": liquider.nombre_d_annees_retenues,
    "liquider.prestation_rafp": lambda *valeurs: dataclasses.asdict(
        liquider.prestation_rafp(*valeurs)),
    "liquider.decote_opposable": liquider.decote_opposable,
    "liquider.salaire_de_reference": liquider.salaire_de_reference,
    "liquider.trimestres_de_decote": liquider.trimestres_de_decote,
    "liquider.valeur_du_point": liquider.valeur_du_point,
    "regimes.BORNES_ASSIETTE": lambda: BORNES_ASSIETTE,
    "releve.construire.droits.points":
        lambda moteur, carriere: releve.construire(moteur, carriere).droits.points,
    "releve.construire.durees.emplois": lambda moteur, carriere: tuple(
        (emploi.fiche, emploi.services)
        for emploi in releve.construire(moteur, carriere).durees.emplois),
    "releve.construire.durees.services_liquidables": lambda moteur, carriere, membres: (
        releve.construire(moteur, carriere).durees.services_liquidables(tuple(membres))),
    "releve.construire.lignes.citations": lambda moteur, carriere: tuple(
        (ligne["id"], ligne.get("fiche"), ligne.get("version"))
        for ligne in releve.construire(moteur, carriere).lignes()),
    "remuneration.fiche_depuis_brut.lignes_de_retraite": _lignes_de_retraite,
    "reversion.reversion": _reversion,
    "revalorisation.faire_vivre.majorations": lambda simulateur, carriere, annee: [
        dataclasses.asdict(majoration) for majoration in faire_vivre(
            simulateur, carriere, simulateur.scenario_actuel.calculer(carriere),
            annee).majorations],
    "scenario_actuel.ages_annulation_decote.age":
        lambda moteur, generation: moteur.ages_annulation_decote.age(generation),
    "scenario_actuel.ages_ouverture.age":
        lambda moteur, generation: moteur.ages_ouverture.age(generation),
    "scenario_actuel.calculer": lambda moteur, carriere, *drapeaux: actuel_en_donnees(
        moteur.calculer(carriere, *drapeaux)),
    "scenario_actuel.catalogue.etage": lambda moteur, code: moteur.catalogue[code].etage,
    "scenario_actuel.catalogue.periodes": lambda moteur, code: [
        {"debut": periode.debut, "fin": periode.fin, "assiette": periode.assiette,
         "taux_cotisation_retraite": periode.taux_cotisation_retraite,
         "part_salariale": periode.part_salariale}
        for periode in moteur.catalogue[code].periodes],
    "scenario_actuel.macro.plafond_securite_sociale":
        lambda moteur, annee: moteur.macro.plafond_securite_sociale(annee),
    "scenario_actuel.minimum_garanti.montant":
        lambda moteur, *valeurs: moteur.minimum_garanti.montant(*valeurs),
    "scenario_actuel.valeurs_point.achat":
        lambda moteur, *valeurs: moteur.valeurs_point.achat(*valeurs),
    "scenario_actuel.valeurs_point.service":
        lambda moteur, *valeurs: moteur.valeurs_point.service(*valeurs),
    "simulateur.carriere_releve": lambda simulateur, options: pont.carriere_en_donnees(
        simulateur.carriere_releve(**options)),
    "simulateur.carriere_simple": lambda simulateur, options: pont.carriere_en_donnees(
        simulateur.carriere_simple(**options)),
}

def _fusionne(simulateur: Simulateur, annee: int, critere: str | None) -> dict:
    from retraite_notionnelle.moteur.fusion import CritereTaux, RegleFusion, fusionner

    regle = RegleFusion() if critere is None else RegleFusion(critere_taux=CritereTaux(critere))
    return dataclasses.asdict(fusionner(simulateur.catalogue, annee, regle))


def _taux_de_la_tranche_1(simulateur: Simulateur, code: str, annee: int) -> float:
    from retraite_notionnelle.moteur.fusion import _taux_total

    return _taux_total(min(simulateur.catalogue[code].periodes_actives(annee),
                           key=lambda periode: periode.bornes_assiette_en_pass()[0]))


def _restitution(simulateur: Simulateur):
    from retraite_notionnelle.restitution import Restitution

    return Restitution(simulateur.parametres.racine_donnees,
                       simulateur.parametres.part_rendue_aux_salaires)


def _salaire_moyen_annuel(simulateur: Simulateur, annee: int) -> float:
    from retraite_notionnelle.carriere import salaire_moyen_annuel

    return salaire_moyen_annuel(simulateur.macro, annee)


def _parts_retraite_seule(simulateur: Simulateur) -> tuple[float, float, float]:
    parts = simulateur.constructeur_employeur.parts_retraite_seule
    return parts[False, False], parts[True, True], parts[True, False]


def _sans_non_finis(valeur):
    """Une valeur telle que node l'écrit : « null » pour un nombre non fini
    (``_fini`` de ``scripts/construire_temoins.py``)."""
    if isinstance(valeur, float) and not math.isfinite(valeur):
        return None
    if isinstance(valeur, dict):
        return {cle: _sans_non_finis(element) for cle, element in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_sans_non_finis(element) for element in valeur]
    return valeur


def _simulee(simulateur: Simulateur, carriere) -> dict:
    """La carrière simulée au moteur Python, telle que le pont la rend aux
    sondes (``"simulateur.simuler"`` de ``pont.mjs``)."""
    comparaison = simulateur.simuler(carriere)
    resultat = comparaison.dictionnaire()
    remuneration = comparaison.remuneration

    def fiche(lue) -> dict:
        return {"brut": lue.brut, "net": lue.net, "retraite_salarie": lue.retraite_salarie,
                "retraite_employeur": lue.retraite_employeur}

    return _sans_non_finis({
        "resultat": resultat,
        "diviseurs": {scenario: getattr(comparaison, scenario).conversion.diviseur
                      for scenario in resultat["scenarios"] if scenario != "actuel"},
        "remuneration": None if remuneration is None else {
            "annee": remuneration.reference.annee,
            "gain_net": remuneration.reference.gain_net,
            "droit_en_vigueur": fiche(remuneration.reference.droit_en_vigueur),
            "proposition": fiche(remuneration.reference.proposition),
            "indemnite_csg_mensuelle": remuneration.indemnite_csg_mensuelle,
        },
    })


def _garantie_vieillesse(simulateur: Simulateur, carriere, pension: float) -> dict:
    garantie = simulateur.scenario_liberal._garantie_vieillesse(carriere, pension)
    return {"plancher_annuel": garantie.plancher_annuel, "complement": garantie.complement}


def _pilier(simulateur: Simulateur, assiettes: dict, annee_naissance: int,
            age_liquidation: float, annee_liquidation: int, repartitions: dict | None) -> dict:
    """Le pilier capitalisé d'une suite d'assiettes au moteur Python, sous sa
    règle d'allocation ou sous celle que la demande décrit, par horizon."""
    from retraite_notionnelle.moteur.capitalisation import ConstructeurCapitalisation

    modele = simulateur.constructeur_capitalisation
    constructeur = modele if repartitions is None else ConstructeurCapitalisation(
        modele.courbe, modele.mortalite, modele.convertisseur, modele.parametres,
        lambda horizon: tuple(map(tuple, repartitions.get(horizon, ()))))
    pilier = constructeur.construire(assiettes, annee_naissance, age_liquidation,
                                     annee_liquidation)
    return {"capital": pilier.capital, "rente_mensuelle": pilier.rente_mensuelle,
            "annees_cotisees": pilier.annees_cotisees}


#: Le jumeau Python de chaque règle que les sondes de la prose et les mesures
#: de l'accueil demandent au pont (:data:`pont.LECTURES_DES_SONDES`).
JUMEAUX_DES_SONDES = {
    "age_reference.age": lambda simulateur, annee: simulateur.age_reference.age(annee),
    "conversion.coefficient.esperance_residuelle": lambda simulateur, age, annee: (
        simulateur.convertisseur.coefficient(age, annee).esperance_residuelle),
    "conversion.effet_anticipation": lambda simulateur, age, reference, annee: (
        simulateur.convertisseur.effet_anticipation(age, reference, annee)),
    "indexation.coefficient": lambda simulateur, depart, arrivee: (
        simulateur.indexation.coefficient(depart, arrivee)),
    "capitalisation.facteur_encours_rente": lambda simulateur, frais, age, annee: (
        simulateur.constructeur_capitalisation._facteur_encours_rente(
            frais, age, annee, None, None)),
    "carriere.salaire_moyen_annuel": _salaire_moyen_annuel,
    "restitution.part_du_poste":
        lambda simulateur, annee: _restitution(simulateur).part_du_poste(annee),
    "restitution.annuelle.points_csg":
        lambda simulateur, annee: _restitution(simulateur).annuelle(annee).points_csg,
    "compte.parts_retraite_seule": _parts_retraite_seule,
    "fusion.fusionner": _fusionne,
    "fusion.taux_total.tranche_1": _taux_de_la_tranche_1,
    "simulateur.simuler": _simulee,
    "notionnel.garantie_vieillesse": _garantie_vieillesse,
    "capitalisation.construire": _pilier,
}
JUMEAUX_DU_DROIT.update(JUMEAUX_DES_SONDES)


def _niveau_relatif(simulateur: Simulateur, carriere) -> float:
    from retraite_notionnelle.moteur.conversion import niveau_relatif

    return niveau_relatif(carriere, simulateur.macro)


#: Le jumeau Python de la règle que l'étude de la mortalité demande au pont
#: (:data:`pont.LECTURES_DE_LA_MORTALITE`).
JUMEAUX_DE_LA_MORTALITE = {
    "conversion.niveau_relatif": _niveau_relatif,
}
JUMEAUX_DU_DROIT.update(JUMEAUX_DE_LA_MORTALITE)


def _dates(depuis: str, jusqu_a: str, *suite) -> tuple:
    """Les arguments d'une revalorisation entre deux dates, que le pont passe
    en dates ISO et que le jumeau Python lit en dates."""
    import datetime

    return (datetime.date.fromisoformat(depuis), datetime.date.fromisoformat(jusqu_a), *suite)


def _decrets_de_la_fonction_publique(moteur, *valeurs):
    from retraite_notionnelle.revalorisation import produit

    revalorisations = moteur.revalorisations_pensions
    return produit(revalorisations.retenues(revalorisations.fonction_publique,
                                            *_dates(*valeurs)))


#: Le jumeau Python de chaque règle du moteur que l'histoire du droit demande
#: au pont (:data:`pont.LECTURES_DE_L_HISTOIRE_DU_DROIT`).
JUMEAUX_DE_L_HISTOIRE_DU_DROIT = {
    "scenario_actuel.revalorisations_pensions.generale":
        lambda moteur, *valeurs: moteur.revalorisations_pensions.generale(*_dates(*valeurs)),
    "scenario_actuel.revalorisations_pensions.retenues.fonction_publique.produit":
        _decrets_de_la_fonction_publique,
    "scenario_actuel.minimum_garanti.ratio_point_indice":
        lambda moteur, *valeurs: moteur.minimum_garanti.ratio_point_indice(*valeurs),
    "scenario_actuel.conversions_points.echelle":
        lambda moteur, *valeurs: moteur.conversions_points.echelle(*valeurs),
}
JUMEAUX_DU_DROIT.update(JUMEAUX_DE_L_HISTOIRE_DU_DROIT)

#: Le pont du droit tel quel, que :func:`droit_et_refait` appelle quand une
#: confrontation la met à sa place.
DROIT_DU_PORTAGE = pont.droit


@functools.cache
def _simulateur_du_droit(parametres: Parametres) -> Simulateur:
    """Le simulateur Python d'un jeu de paramètres que :func:`droit_et_refait`
    confronte, gardé d'un appel à l'autre."""
    return Simulateur(parametres)


@functools.cache
def _scenarios_neutralises(simulateur: Simulateur) -> dict:
    """Les variantes du scénario 1 que la mesure des avantages non
    contributifs liquide (``avantages.scenarios_neutralises``), bâties une
    fois par simulateur."""
    from retraite_notionnelle.avantages import scenarios_neutralises

    return scenarios_neutralises(simulateur)


def _moteur_du_jumeau(simulateur: Simulateur, moteur: pont.Moteur):
    """Le moteur du scénario 1 du simulateur Python, ou la variante que la
    mesure des avantages en neutralise (``pont.Moteur.neutralisant``)."""
    if moteur.neutralise is None:
        return simulateur.scenario_actuel
    return _scenarios_neutralises(simulateur)[moteur.neutralise]


def _argument_du_jumeau(simulateur: Simulateur, argument):
    """Un argument d'un appel du droit tel que le jumeau Python le reçoit : le
    moteur du scénario 1, ou sa variante neutralisée, et la période d'un
    régime, ceux du simulateur Python ; une carrière, que le Python a bâtie,
    ou une valeur, telle quelle."""
    if isinstance(argument, pont.Moteur):
        return _moteur_du_jumeau(simulateur, argument)
    if argument is pont.SIMULATEUR:
        return simulateur
    if isinstance(argument, pont.CarriereSimple):
        return simulateur.carriere_simple(**argument.options)
    if isinstance(argument, pont.Periode):
        return simulateur.catalogue[argument.code].periode(argument.annee)
    return argument


@contextlib.contextmanager
def _prets_au_jumeau(simulateur: Simulateur, arguments):
    """Les tables que les arguments d'un appel prêtent au moteur
    (``pont.Moteur.pretant``), prêtées au moteur Python le temps de l'appel,
    comme un test les lui prête (``monkeypatch.setattr``), puis rendues."""
    gardees = []
    try:
        for argument in arguments:
            if not isinstance(argument, pont.Moteur):
                continue
            moteur = _moteur_du_jumeau(simulateur, argument)
            for table, preteuse in argument.prets:
                if not hasattr(moteur, table):
                    raise AttributeError(f"le moteur Python ne porte pas la table {table}")
                gardees.append((moteur, table, getattr(moteur, table)))
                setattr(moteur, table, getattr(moteur, preteuse))
        yield
    finally:
        for moteur, table, gardee in reversed(gardees):
            setattr(moteur, table, gardee)


def droit_et_refait(appels: dict[str, tuple], parametres=None, paquet: bytes | None = None,
                    ) -> tuple[dict[str, object], dict[str, str]]:
    """Ce que le portage rend de chaque appel du droit (:func:`pont.droit`),
    son jumeau Python confronté tant qu'il reste (action 161) : ce qu'il rend,
    relu sous le type que le pont déclare (:func:`pont.relu_du_droit`), doit
    s'écrire au bit près sous Linux x86_64 comme ce que le portage a rendu
    (:data:`TOLERANCE_DU_MOTEUR_PYTHON`), et un appel que le portage refuse,
    le jumeau doit le refuser, ou la confrontation s'arrête sur ce qui
    diffère. Les exemples d'OpenFisca et des caisses (``tests/test_oracle.py``)
    le passent à leurs mesures au lieu du pont : aucun appel ne perd la
    vérification du Python. Sur un autre paquet que celui du dépôt, il n'y a
    rien à refaire."""
    lus, refus = DROIT_DU_PORTAGE(appels, parametres, paquet)
    if paquet is not None:
        return lus, refus
    sans_jumeau = sorted({fonction for fonction, *_ in appels.values()}
                         - set(JUMEAUX_DU_DROIT))
    if sans_jumeau:
        raise ValueError(f"fonctions du droit sans jumeau Python : {', '.join(sans_jumeau)} "
                         "(outils_pont.JUMEAUX_DU_DROIT)")
    simulateur = _simulateur_du_droit(Parametres() if parametres is None else parametres)
    ecarts = []
    for cle, (fonction, *arguments) in appels.items():
        jumeau = functools.partial(JUMEAUX_DU_DROIT[fonction], *(
            _argument_du_jumeau(simulateur, argument) for argument in arguments))
        if cle in refus:
            try:
                with _prets_au_jumeau(simulateur, arguments):
                    jumeau()
            except Exception:
                continue
            ecarts.append(f"{cle} : le portage le refuse ({refus[cle]}), le jumeau Python le rend")
            continue
        with _prets_au_jumeau(simulateur, arguments):
            refait = pont.relu_du_droit(fonction, jumeau())
        ecarts += ecarts_d_ecriture(refait, lus[cle], (cle,), tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
    if ecarts:
        raise AssertionError("le jumeau Python ne refait pas ce que le portage rend "
                             f"({len(ecarts)} écart(s)) : " + " ; ".join(ecarts[:5]))
    return lus, refus


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
