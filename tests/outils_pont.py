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

import dataclasses
import functools
import hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path

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


#: Le pont du scénario 1 tel quel, que :func:`servi_et_fige` appelle quand
#: une confrontation la met à sa place.
SCENARIO_ACTUEL_DU_PORTAGE = pont.scenario_actuel

#: Le témoin des servis : ce que le portage sert à chaque cas que les
#: confrontations du scénario 1 demandent, sous l'empreinte du cas
#: (:func:`empreinte_du_cas`), avec sa clé, sa requête et ce qui en est servi,
#: ou le motif de son refus. ``scripts/construire_temoins.py`` le refait de
#: ses propres requêtes (action 161, étape 8b).
TEMOIN_DES_SERVIS = Path(__file__).resolve().parent / "temoins" / "servis.json"


def empreinte_du_cas(cas: dict) -> str:
    """L'empreinte de ce que le portage lit d'un cas, sa clé ôtée : deux
    fichiers qui nomment autrement le même cas le partagent."""
    lu = {cle: valeur for cle, valeur in cas.items() if cle != "cle"}
    texte = json.dumps(lu, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]


@functools.cache
def servis_figes() -> dict[str, dict]:
    """Le témoin des servis, tel que le fichier le porte."""
    return json.loads(TEMOIN_DES_SERVIS.read_text(encoding="utf-8"))


def _figer(entrees: dict[str, dict]) -> None:
    """Ajoute des entrées au témoin, sous verrou, et le remplace d'un coup :
    les processus de la suite peuvent figer, et le lire, en même temps."""
    import fcntl  # POSIX seul : figer ne se fait que sous Linux ou macOS

    import tempfile

    verrou = Path(tempfile.gettempdir()) / "temoin_des_servis.verrou"
    with open(verrou, "a", encoding="utf-8") as tenu:
        fcntl.flock(tenu, fcntl.LOCK_EX)
        figes = json.loads(TEMOIN_DES_SERVIS.read_text(encoding="utf-8"))
        figes.update(entrees)
        provisoire = TEMOIN_DES_SERVIS.with_suffix(f".{os.getpid()}.provisoire")
        provisoire.write_text(json.dumps(figes, ensure_ascii=False, sort_keys=True, indent=1)
                              + "\n", encoding="utf-8")
        os.replace(provisoire, TEMOIN_DES_SERVIS)
    servis_figes.cache_clear()


def servi_et_fige(cas: list[dict], paquet: bytes | None = None,
                  ) -> tuple[dict[str, dict], dict[str, str]]:
    """Ce que le portage sert de chaque cas (:func:`pont.scenario_actuel`),
    confronté au témoin des servis (:data:`TEMOIN_DES_SERVIS`) : chaque cas
    doit y être, servi ou refusé de même, au bit près sous Linux x86_64
    (:data:`TOLERANCE_DU_MOTEUR_PYTHON`). Il tient la place du moteur Python
    qui refaisait chaque cas tant qu'il gardait ses jumeaux (action 161,
    étape 8b) : ce que les assertions d'un test ne disent pas, le témoin le
    garde. Sous ``FIGER_SERVIS=1``, un cas absent s'y ajoute. Sur un autre
    paquet que celui du dépôt, il n'y a rien à confronter."""
    servis, refus = SCENARIO_ACTUEL_DU_PORTAGE(cas, paquet)
    if paquet is not None:
        return servis, refus
    figes = servis_figes()
    absents, ecarts = {}, []
    for un_cas in cas:
        cle, empreinte = un_cas["cle"], empreinte_du_cas(un_cas)
        lu = ({"refus": refus[cle]} if cle in refus else {"servi": servis[cle]})
        if empreinte not in figes:
            absents[empreinte] = {"cle": cle, "cas": {k: v for k, v in un_cas.items()
                                                       if k != "cle"}, **lu}
            continue
        fige = {k: v for k, v in figes[empreinte].items() if k in ("servi", "refus")}
        ecarts += [f"{cle}, {ecart}" for ecart in ecarts_d_ecriture(
            json.loads(json.dumps(lu)), fige, tolerance=TOLERANCE_DU_MOTEUR_PYTHON)]
    if absents and os.environ.get("FIGER_SERVIS") == "1":
        _figer(absents)
    elif absents:
        raise AssertionError(
            f"{len(absents)} cas absent(s) du témoin des servis, dont "
            f"{[entree['cle'] for entree in absents.values()][:5]} : les y ajouter par "
            "FIGER_SERVIS=1 python -m pytest <ce fichier>")
    if ecarts:
        raise AssertionError(
            f"le portage ne sert plus ce que le témoin des servis porte ({len(ecarts)} "
            "écart(s)) ; si le déplacement est voulu, le témoin se refait par python "
            "scripts/construire_temoins.py --servis : " + " ; ".join(ecarts[:5]))
    return servis, refus


#: Le pont du droit tel quel, que :func:`droit_et_fige` appelle : un test
#: le remplace par un portage simulé.
DROIT_DU_PORTAGE = pont.droit


#: Le témoin du droit : sous l'empreinte de chaque demande que les tests font
#: au droit à travers le pont (:func:`empreinte_de_la_demande`), les fonctions
#: qu'elle appelle et l'empreinte de ce que le portage en rend et en refuse
#: (action 161, étape 8e). Une variable d'environnement du même nom le
#: déplace, pour que ``construire_temoins.py --droit`` le refasse à part.
TEMOIN_DU_DROIT = Path(os.environ.get(
    "TEMOIN_DU_DROIT", Path(__file__).resolve().parent / "temoins" / "droit.json"))


def empreinte_de_la_demande(appels: dict[str, tuple], parametres=None) -> str:
    """L'empreinte de ce que :func:`pont.droit` envoie au portage : chaque
    appel sous sa clé, ses arguments mis en données comme le pont les écrit,
    les carrières qu'ils nomment, et les paramètres, ``None`` pour les
    réglages de référence."""
    carrieres: list = []
    demandes = [[cle, fonction, *(pont._argument_du_droit(argument, carrieres)
                                  for argument in arguments)]
                for cle, (fonction, *arguments) in appels.items()]
    texte = json.dumps({
        "appels": demandes,
        "carrieres": [pont.carriere_en_donnees(carriere) for carriere in carrieres],
        "parametres": None if parametres is None else pont.parametres_en_donnees(parametres),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]


@functools.cache
def droit_fige() -> dict[str, dict]:
    """Le témoin du droit, tel que le fichier le porte."""
    if not TEMOIN_DU_DROIT.exists():
        return {}
    return json.loads(TEMOIN_DU_DROIT.read_text(encoding="utf-8"))


def _figer_le_droit(empreinte: str, entree: dict) -> None:
    """Écrit une demande au témoin du droit, sous verrou, et le remplace d'un
    coup : les processus de la suite peuvent figer, et le lire, en même
    temps."""
    import fcntl  # POSIX seul : figer ne se fait que sous Linux ou macOS

    import tempfile

    verrou = Path(tempfile.gettempdir()) / "temoin_du_droit.verrou"
    with open(verrou, "a", encoding="utf-8") as tenu:
        fcntl.flock(tenu, fcntl.LOCK_EX)
        figes = (json.loads(TEMOIN_DU_DROIT.read_text(encoding="utf-8"))
                 if TEMOIN_DU_DROIT.exists() else {})
        figes[empreinte] = entree
        provisoire = TEMOIN_DU_DROIT.with_suffix(f".{os.getpid()}.provisoire")
        provisoire.write_text(json.dumps(figes, ensure_ascii=False, sort_keys=True, indent=1)
                              + "\n", encoding="utf-8")
        os.replace(provisoire, TEMOIN_DU_DROIT)
    droit_fige.cache_clear()


def droit_et_fige(appels: dict[str, tuple], parametres=None, paquet: bytes | None = None,
                  ) -> tuple[dict[str, object], dict[str, str]]:
    """Ce que le portage rend de chaque appel du droit (:func:`pont.droit`),
    et les motifs de ceux qu'il refuse, confrontés au témoin du droit
    (:data:`TEMOIN_DU_DROIT`) : la demande doit y être, sous l'empreinte de ce
    que le portage en rend aujourd'hui, chaque flottant lu à douze chiffres
    significatifs (``outils_valeurs.empreinte_de_la_valeur``). Il tient la
    place du jumeau Python qui refaisait chaque appel tant que le moteur
    Python restait (action 161, étape 8e) : ce que les assertions d'un test
    ne disent pas, le témoin le garde. Sous ``FIGER_DROIT=1``, une demande
    absente s'y ajoute, et un rendu qui a bougé s'y refait. Sur un autre
    paquet que celui du dépôt, il n'y a rien à confronter."""
    from outils_valeurs import empreinte_de_la_valeur

    lus, refus = DROIT_DU_PORTAGE(appels, parametres, paquet)
    if paquet is not None:
        return lus, refus
    empreinte = empreinte_de_la_demande(appels, parametres)
    rendu = empreinte_de_la_valeur({"lus": lus, "refus": refus})
    fige = droit_fige().get(empreinte)
    if fige is not None and fige["rendu"] == rendu:
        return lus, refus
    fonctions = sorted({fonction for fonction, *_ in appels.values()})
    if os.environ.get("FIGER_DROIT") == "1":
        _figer_le_droit(empreinte, {"fonctions": fonctions, "rendu": rendu})
        return lus, refus
    if fige is None:
        raise AssertionError(
            f"demande au droit absente du témoin ({', '.join(fonctions)[:200]}) : l'y "
            "ajouter par FIGER_DROIT=1 python -m pytest <ce fichier>")
    raise AssertionError(
        f"le portage ne rend plus ce que le témoin du droit porte ({', '.join(fonctions)[:200]}) ;"
        " si le déplacement est voulu, le témoin se refait par python "
        "scripts/construire_temoins.py --droit")


def fichiers_qui_appellent_le_droit() -> list[str]:
    """Les fichiers de tests qui appellent :func:`droit_et_fige`, nommés sous
    ``tests/`` : ceux que ``construire_temoins.py --droit`` relance."""
    racine = Path(__file__).resolve().parent
    return sorted(chemin.name for chemin in racine.glob("test_*.py")
                  if chemin.name != "test_droit_fige.py"
                  and "droit_et_fige" in chemin.read_text(encoding="utf-8"))


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
