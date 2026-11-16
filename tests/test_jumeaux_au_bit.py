"""Chaque fonction gardée des deux côtés rend la même valeur en Python et en
JavaScript, au bit près (action 161, étapes 7b à 7e).

La liste ``scripts/jumeaux_gardees.yaml`` déclare, dans les paires qui restent
après le retrait du moteur Python, les fonctions écrites des deux côtés que la
fabrique, le coût ou une étude lisent en Python pendant que le site les
calcule en JavaScript. Les deux exemplaires ne doivent pas diverger : le
Python les calcule sur le YAML (``data/``), le portage sur le paquet
(``moteur/donnees.json``), et chacune se confronte ici sur une grille
d'arguments déclarée avec elle (:data:`GRILLES`), ou, quand sa forme
l'empêche, par la grille d'une fonction qui l'appelle (:data:`PAR_L_APPELANT`).
Une fonction confrontée ici le dit dans la liste, colonne ``test`` ; une
grille sans cette ligne, ou l'inverse, rougit.

Le portage se lit par ``web/site.py`` : ses objets sont bâtis sur le paquet du
contexte du site, que node garde, et leurs méthodes appelées une à une.
« Au bit près » est la tolérance du moteur Python (``outils_pont``) : nulle
sous Linux x86_64, où GitHub joue la suite, 10⁻¹² en écart relatif ailleurs,
où la libm du système déplace la dernière décimale de quelques flottants.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import enum
import math
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

from outils_pont import TOLERANCE_DU_MOTEUR_PYTHON
from retraite_notionnelle.web import site as site_js

RACINE = Path(__file__).resolve().parents[1]
DATA = RACINE / "data"
LISTE = RACINE / "scripts" / "jumeaux_gardees.yaml"
sys.path.insert(0, str(RACINE / "scripts"))

from jumeaux import en_camel  # noqa: E402

CE_TEST = "tests/test_jumeaux_au_bit.py::test_la_fonction_gardee_rend_la_meme_valeur_des_deux_cotes"
PAR_SON_APPELANT = ("tests/test_jumeaux_au_bit.py::"
                    "test_la_fonction_gardee_se_confronte_par_son_appelant")

TAUX = "src/retraite_notionnelle/donnees/taux.py"
MORTALITE = "src/retraite_notionnelle/donnees/mortalite.py"
PATRIMOINE = "src/retraite_notionnelle/donnees/patrimoine.py"
DISTRIBUTION = "src/retraite_notionnelle/donnees/distribution.py"
ASSIETTE = "src/retraite_notionnelle/donnees/assiette.py"
TVA = "src/retraite_notionnelle/donnees/tva.py"
EFFECTIFS = "src/retraite_notionnelle/donnees/effectifs.py"
DEPENSES = "src/retraite_notionnelle/donnees/depenses.py"
COUPLE = "src/retraite_notionnelle/donnees/vie_en_couple.py"
CARACTERISTIQUES = "src/retraite_notionnelle/donnees/caracteristiques.py"
CHARGEMENT = "src/retraite_notionnelle/donnees/chargement.py"
CALENDRIER = "src/retraite_notionnelle/calendrier.py"
CONFIG = "src/retraite_notionnelle/config.py"
MACRO = "src/retraite_notionnelle/donnees/macro.py"
HISTORIQUES = "src/retraite_notionnelle/donnees/prelevements_historiques.py"
FRONTIERE = "src/retraite_notionnelle/frontiere.py"
REGIMES = "src/retraite_notionnelle/donnees/regimes.py"
EQUILIBRE = "src/retraite_notionnelle/donnees/equilibre.py"
BILAN = "src/retraite_notionnelle/donnees/bilan.py"
CONTEXTE = "src/retraite_notionnelle/contexte.py"
CONTRIBUTIONS = "src/retraite_notionnelle/contributions_equilibre.py"


class _Racine:
    """L'argument qui vaut ``data/`` en Python et le paquet en JavaScript."""

    def __repr__(self) -> str:
        return "RACINE"


#: À la place d'un argument : la racine des données en Python, le paquet
#: dans le portage, pour une fonction de module qui lit l'une ou l'autre.
SOURCE = _Racine()


class SousRacine(str):
    """À la place d'un argument : ce dossier de ``data/`` en Python, le paquet
    dans le portage — ``reference/macro``, d'où le Python lit les comptes du
    COR que le paquet porte."""


class Jour(str):
    """Un jour, en date ISO : ``datetime.date`` en Python, la chaîne même au
    portage, qui compare ses dates ISO comme des chaînes."""


class Nommes(dict):
    """Les arguments nommés d'un appel, en dernier dans son n-uplet : passés
    par leur nom en Python, à la suite des autres et dans leur ordre au
    portage, qui n'a que des arguments positionnels."""


class EnTable(Nommes):
    """Des arguments nommés que le portage reçoit en une seule table, comme
    les champs changés de ``morceauDAnnees``."""


class Objet(str):
    """À la place d'un argument : l'objet de ce nom (:func:`_python`), de
    chaque côté — une période passée à ``morceau_d_annees``."""


#: La classe Python de chaque genre d'objet bâti sur ``data/`` seul, et le
#: module du portage où sa classe, du même nom, se bâtit sur le paquet.
CLASSES = {
    "assiette": ("assiette", "AssietteActivite"),
    "tva": ("tva", "AssietteTva"),
    "effectifs": ("effectifs", "EffectifsRetraites"),
    "depenses": ("depenses", "DepensesRetraite"),
    "couple": ("vie_en_couple", "VieEnCouple"),
    "caracteristiques": ("caracteristiques", "CaracteristiquesRetraites"),
}


#: Les modules confrontés fonction par fonction : le module Python, et celui
#: du portage.
MODULES = {
    "patrimoine": ("donnees.patrimoine", "patrimoine"),
    "distribution": ("donnees.distribution", "distribution"),
    "calendrier": ("calendrier", "calendrier"),
    "frontiere": ("frontiere", "frontiere"),
    "regimes": ("donnees.regimes", "regimes"),
    "equilibre": ("donnees.equilibre", "equilibre"),
    "bilan": ("donnees.bilan", "bilan"),
}


# -- les objets confrontés -------------------------------------------------------

def _python(nom: str):
    """L'objet Python d'un nom de :data:`OBJETS`, bâti sur le YAML."""
    import importlib
    from retraite_notionnelle.donnees import distribution, mortalite, patrimoine, taux
    genre, _, detail = nom.partition(":")
    if genre == "module":
        return importlib.import_module(f"retraite_notionnelle.{MODULES[detail][0]}")
    if genre == "date":
        from retraite_notionnelle.calendrier import DateMois
        return DateMois(*map(int, detail.split("-")))
    if genre == "classe":
        from retraite_notionnelle.calendrier import DateMois
        return {"DateMois": DateMois}[detail]
    if genre == "parametres":
        from retraite_notionnelle.config import PARAMETRES_DEFAUT
        return PARAMETRES_DEFAUT
    if genre == "macro":
        from retraite_notionnelle.donnees.macro import DonneesMacro
        return DonneesMacro(DATA, detail or None)
    if genre in ("regime", "regime_moyen"):
        from retraite_notionnelle.donnees.regimes import CatalogueRegimes
        return _catalogue_python(genre == "regime_moyen")[detail]
    if genre == "periode":
        code, _, rang = detail.rpartition("/")
        return _objet_python(f"regime:{code}").periodes[int(rang)]
    if genre == "employeurs":
        from retraite_notionnelle.donnees.regimes import ContributionsEmployeurPubliques
        return ContributionsEmployeurPubliques(DATA)
    if genre == "historiques":
        from retraite_notionnelle.donnees.prelevements_historiques import (
            charger_prelevements_historiques)
        historiques = charger_prelevements_historiques(DATA)
        if not detail:
            return historiques
        groupe, _, serie = detail.partition("/")
        return getattr(historiques, groupe)[serie]
    if genre == "courbe":
        return taux.CourbeTauxSansRisque(DATA, float(detail))
    if genre == "mortalite":
        return mortalite.DonneesMortalite(DATA)
    if genre == "patrimoine":
        if not detail:
            return patrimoine.PatrimoineMenages(DATA)
        return _objet_python("patrimoine").distribution(detail)
    if genre in CLASSES:
        import importlib
        module, classe = CLASSES[genre]
        return getattr(importlib.import_module(
            f"retraite_notionnelle.donnees.{module}"), classe)(DATA)
    if genre == "serie":
        return _serie(_objet_python, detail)
    if genre == "comptes":
        from retraite_notionnelle.donnees.equilibre import ComptesRetraite
        return ComptesRetraite(DATA, variante=detail)
    if genre == "decomposition":
        from retraite_notionnelle.donnees.equilibre import DecompositionDepense
        return DecompositionDepense(DATA / "reference" / "macro")
    if genre == "bilan":
        from retraite_notionnelle.donnees.bilan import charger_bilan
        bilan = charger_bilan(DATA)
        return bilan.engagements if detail == "engagements" else bilan.assiette
    if genre == "contexte":
        from retraite_notionnelle.contexte import Contexte
        return Contexte()
    if genre == "contribution":
        from retraite_notionnelle.contributions_equilibre import (
            charger_contributions_equilibre)
        return charger_contributions_equilibre(DATA)[detail]
    if genre == "pensions":
        # Le paquet porte la distribution des retraités qui résident en
        # France, comme la fabrique la lit (``_distribution_pensions_sexes``).
        return distribution.DistributionPensions(DATA, detail, residence="france")
    raise KeyError(nom)


def _javascript(nom: str):
    """L'objet du portage d'un nom de :data:`OBJETS`, bâti sur le paquet."""
    genre, _, detail = nom.partition(":")
    if genre == "module":
        return site_js.module(MODULES[detail][1])
    if genre == "date":
        return site_js.module("calendrier").DateMois(*map(int, detail.split("-")))
    if genre == "classe":
        return getattr(site_js.module("calendrier"), detail)
    if genre == "parametres":
        return site_js.module("config").PARAMETRES_DEFAUT
    if genre == "macro":
        return site_js.module("macro").DonneesMacro(_paquet(), detail or None)
    if genre in ("regime", "regime_moyen"):
        return _catalogue_javascript(genre == "regime_moyen").obtenir(detail)
    if genre == "periode":
        code, _, rang = detail.rpartition("/")
        return _periodes_javascript(code)[int(rang)]
    if genre == "employeurs":
        return site_js.module("regimes").ContributionsEmployeurPubliques(_paquet())
    if genre == "historiques":
        historiques = site_js.module("prelevements-historiques").chargerPrelevementsHistoriques(
            _paquet())
        if not detail:
            return historiques
        groupe, _, serie = detail.partition("/")
        return getattr(historiques, groupe)[serie]
    if genre == "courbe":
        return site_js.module("taux").CourbeTauxSansRisque(_paquet(), float(detail))
    if genre == "mortalite":
        return site_js.module("mortalite").DonneesMortalite(_paquet())
    if genre == "patrimoine":
        if not detail:
            return site_js.module("patrimoine").PatrimoineMenages(_paquet())
        return _objet_javascript("patrimoine").distribution(detail)
    if genre in CLASSES:
        module, classe = CLASSES[genre]
        return getattr(site_js.module(module.replace("_", "-")), classe)(_paquet())
    if genre == "serie":
        return _serie(_objet_javascript, detail)
    if genre == "pensions":
        return site_js.module("distribution").DistributionPensions(_paquet(), detail)
    if genre == "comptes":
        return site_js.module("equilibre").ComptesRetraite(_paquet(), detail)
    if genre == "decomposition":
        return _objet_javascript("comptes:reference").decomposition
    if genre == "bilan":
        bilan = site_js.module("bilan").charger_bilan(_paquet()["bilan_equilibre"])
        return bilan.engagements if detail == "engagements" else bilan.assiette
    if genre == "contexte":
        return site_js.site().contexte
    if genre == "contribution":
        lues = site_js.module("contributions-equilibre").charger_contributions_equilibre(
            _paquet())
        return next(c for c in lues["contributions"] if c["code"] == detail)
    raise KeyError(nom)


def _serie(objet, detail: str):
    """Une série annuelle d'un objet de données, de chaque côté : « effectifs/
    <caisse> », celle des retraités d'une caisse, mesurée (ponctuelle) ;
    « depenses/total », la dépense publiée (en escalier)."""
    porteur, _, nom = detail.partition("/")
    if porteur == "effectifs":
        return objet("effectifs").serie(nom)
    return getattr(objet(porteur), nom)


@lru_cache(maxsize=None)
def _objet_python(nom: str):
    return _python(nom)


@lru_cache(maxsize=None)
def _objet_javascript(nom: str):
    return _javascript(nom)


@lru_cache(maxsize=None)
def _catalogue_python(taux_moyens: bool):
    from retraite_notionnelle.donnees.regimes import CatalogueRegimes
    return CatalogueRegimes(DATA, taux_moyens=taux_moyens)


@lru_cache(maxsize=None)
def _catalogue_javascript(taux_moyens: bool):
    return site_js.module("regimes").CatalogueRegimes(_paquet(), {"tauxMoyens": taux_moyens})


@lru_cache(maxsize=None)
def _periodes_javascript(code: str):
    return _objet_javascript(f"regime:{code}").periodes


@lru_cache(maxsize=1)
def _paquet():
    return site_js.site().contexte.paquet


# -- les grilles -----------------------------------------------------------------

@dataclass(frozen=True)
class Grille:
    """Une fonction gardée et ce sur quoi elle se confronte.

    ``objets`` : les objets qui la portent (:func:`_python`) ; ``appels`` : ses
    arguments, un n-uplet par appel, ou ``None`` pour une propriété ;
    ``champs`` : pour une valeur qui est un objet, les attributs qu'on en
    compare — « nom:a,b » lit les attributs ``a`` et ``b`` de l'objet, ou de
    chaque objet de la liste, que porte ``nom`` ; ``sauf`` : les clés d'une
    valeur qui est une table, ou de ses objets, que le portage n'a pas ;
    ``lire`` : ce qu'on compare d'une valeur, ``lire(valeur, côté)``, quand les
    deux côtés la rendent sous deux formes ;
    ``module_js`` : au portage, la méthode est une fonction de ce module, qui
    reçoit l'objet en premier argument et les arguments nommés en une table
    (``avec`` des paramètres) ; ``en_liste`` : au portage, une table dont
    ces clés, dans cet ordre, sont le n-uplet que rend le Python ;
    ``nom_js`` : au portage, la fonction porte ce nom, et non celui du Python
    mis à sa manière ; ``cle_du_paquet`` : au portage, :data:`SOURCE` est
    cette clé du paquet, et non le paquet entier."""

    objets: tuple[str, ...]
    appels: tuple[tuple, ...] | None = None
    champs: tuple[str, ...] = ()
    sauf: tuple[str, ...] = ()
    module_js: str | None = None
    en_liste: tuple[str, ...] = ()
    lire: Callable | None = None
    nom_js: str | None = None
    cle_du_paquet: str | None = None


def _pas(debut: float, fin: float, pas: float) -> list[float]:
    return [debut + rang * pas for rang in range(int(round((fin - debut) / pas)) + 1)]


def _populations_mortalite() -> list[tuple[str, str]]:
    """Les populations et les sexes qu'une seule espérance publiée cale, et
    qui ont un facteur unique. Celles publiées à plusieurs âges — les types de
    pension de la Cnav — ont leurs facteurs par tranche d'âge
    (:func:`_populations_par_age`)."""
    from retraite_notionnelle.donnees.mortalite import DonneesMortalite
    mortalite = DonneesMortalite(DATA)
    return [(population, sexe) for population in mortalite.populations
            for sexe in DonneesMortalite.SEXES
            if not mortalite._publiee_par_age(population, sexe)]


def _populations_par_age() -> list[tuple[str, str]]:
    """Les populations et les sexes publiés à plusieurs âges (action 161,
    étape 9l) : les types de pension de la Cnav."""
    from retraite_notionnelle.donnees.mortalite import DonneesMortalite
    mortalite = DonneesMortalite(DATA)
    return [(population, sexe) for population in mortalite.populations
            for sexe in DonneesMortalite.SEXES
            if mortalite._publiee_par_age(population, sexe)]


def _populations_patrimoine() -> list[str]:
    from retraite_notionnelle.donnees.patrimoine import PatrimoineMenages
    return list(PatrimoineMenages(DATA).populations)


def _contribution(valeur, cote: str):
    """La contribution d'un employeur public : un objet en Python, un tableau
    au portage — taux, nature, fiabilité, et ``true`` pour les militaires."""
    if valeur is None:
        return None
    if cote == "python":
        return [valeur.taux, valeur.nature, int(valeur.fiabilite), valeur.militaire]
    return [valeur[0], valeur[1], valeur[2], len(valeur) > 3 and valeur[3]]


#: Ce qu'on compare d'une période de régime : qui elle est, ses années et
#: son mode de calcul. Le paquet n'écrit pas les champs restés à leur
#: défaut, que le portage lit par ``??`` : la grille s'en tient aux champs
#: que chaque période porte des deux côtés.
CHAMPS_DE_LA_PERIODE = ("regime", "debut", "fin", "type_calcul", "age_ouverture",
                        "age_taux_plein", "taux_cotisation_retraite", "part_salariale",
                        "assiette", "effet")


def _morceau(valeur, cote: str):
    """Un morceau de période : une période en Python, la fiche dont le portage
    la bâtira, sans ``date_effet`` quand ses dates sont celles de ses années."""
    champs = tuple(c for c in CHAMPS_DE_LA_PERIODE if c != "effet")
    lu = _champs(valeur, champs)
    lu["date_effet"] = getattr(valeur, "date_effet", None)
    return lu


def _scenarios_du_bilan() -> list[str]:
    """Les systèmes que la table du bilan porte, lus dans la table même."""
    import json
    brut = json.loads((DATA / "derive" / "equilibre.json").read_text(encoding="utf-8"))
    return sorted(brut["annees"][0]["coefficients"])


def _bilan(valeur, cote: str):
    """Ce que le bilan chargé porte, champ par champ : ses années et leurs
    tables par système, l'assiette, l'engagement acquis, les écarts médians
    et les carrières d'exemple. Le Python se lit dans ses tables, que ses
    accesseurs, partis avec le moteur, ne lisent plus ; le portage, par les
    siens, où le nom privé d'une table est celui d'une méthode ou d'un
    accesseur (``ressources``, ``sensibilite``)."""
    scenarios = _scenarios_du_bilan()
    tables = (("_coefficients", "coefficient"), ("_soldes", "solde"),
              ("_ressources", "ressources_de"), ("_depenses", "depense"))

    def par_systeme(ligne, table, accesseur):
        if cote == "python":
            return [getattr(ligne, table).get(s, 0.0) for s in scenarios]
        return [getattr(ligne, accesseur)(s) for s in scenarios]

    annees = [[ligne.annee, ligne.projete, ligne.part_contributive, ligne.pib,
               *[par_systeme(ligne, *paire) for paire in tables]]
              for ligne in valeur.annees]
    acquis, ecarts = valeur.engagements, valeur.ecarts
    sensibilite = acquis._sensibilite if cote == "python" else acquis.sensibilite()
    return {
        "annees": annees,
        "bornes": [valeur.premiere_annee, valeur.derniere_annee,
                   valeur.derniere_annee_observee, valeur.premiere_annee_projetee,
                   valeur.pib, valeur.annee_pib],
        "assiette": [valeur.assiette.derniere_annee,
                     valeur.assiette.part_pib(valeur.assiette.derniere_annee)],
        "engagements": [acquis.annee, acquis.horizon, acquis.retraites, acquis.actifs,
                        acquis.hors_projection, acquis.publie, sensibilite],
        "ecarts": [ecarts.a_venir, ecarts.a_venir_volontaire, ecarts.deja_liquidees,
                   ecarts.cases_a_venir, ecarts.cases_deja_liquidees],
        "exemples": [[dict(e.saisie), e.fiche.annee, e.fiche.brut, e.fiche.net,
                      e.fiche.retraite_totale, e.fiche.retraite_employeur,
                      e.coefficient_euros_constants, e.pension_actuel, e.pension_financee]
                     for e in valeur.exemples],
    }


#: Les années où l'on lit ce qu'un accesseur du contexte rend.
ANNEES_DU_CONTEXTE = tuple(range(2000, 2071, 5))


def _par_annee(methode: str):
    """Ce qu'une donnée rendue par le contexte dit, chaque année de
    :data:`ANNEES_DU_CONTEXTE`, par une méthode déjà confrontée ici."""
    def lire(valeur, cote: str):
        return [getattr(valeur, methode)(annee) for annee in ANNEES_DU_CONTEXTE]
    return lire


def _comptes_du_contexte(valeur, cote: str):
    return [valeur.variante, _par_annee("depense")(valeur, cote),
            _par_annee("ressource")(valeur, cote)]


def _parametres(valeur, cote: str):
    """Les paramètres d'un simulateur : la racine des données n'est qu'au
    Python."""
    return _sans(_en_python(valeur.parametres), ("racine_donnees",))


def _grilles() -> dict[tuple[str, str], Grille]:
    courbes = ("courbe:0.0", "courbe:0.006")
    horizons = sorted(set(_pas(0.0, 60.0, 0.25)) | {0.1, 29.9, 30.0, 30.1, 100.0})
    differes = (0, 0.5, 1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 40, 50)
    durees = (0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 35, 40)

    mortalite = ("mortalite",)
    sexes = ("H", "F")
    populations = _populations_mortalite()
    calees = sorted({p for p, _ in populations})
    niveaux = [p for p in calees if p.startswith("niveau_de_vie")]
    autres = [p for p in calees if not p.startswith("niveau_de_vie")
              and all((p, sexe) in populations for sexe in sexes)]
    departs = [(age, annee) for age in (55.0, 60.0, 62.5, 65.0, 67.25, 80.0)
               for annee in (1990.0, 2010.0, 2025.0, 2041.5, 2070.0)]
    generations = (True, False)
    par_age = _populations_par_age()
    cnav = sorted({p for p, _ in par_age})
    choix_populations = (None, autres[0], niveaux[0], niveaux[-1], cnav[0], cnav[-1])

    tous = ("patrimoine",)
    par_population = tuple(f"patrimoine:{p}" for p in _populations_patrimoine())
    pensions = tuple(f"pensions:{sexe}" for sexe in ("ensemble", "F", "H"))

    from retraite_notionnelle.donnees.depenses import CODES_SYSTEMES
    annees = tuple((annee,) for annee in range(1945, 2081))
    depenses = _objet_python("depenses")
    annees_publiees = tuple((annee,) for annee in depenses.annees())
    caisses = _objet_python("effectifs").caisses()
    modes = sorted({mode for _, _, mode in _objet_python("couple")._parts})
    survie = [math.exp(-0.0004 * rang ** 2) for rang in range(45)]
    expositions = ([1.0], [0.0, 0.0], survie, [1.0, 0.75, 0.5, 0.25, 0.0])
    # Le paquet ne porte que les indicateurs que le site lit, ceux que la
    # fabrique y écrit : les grilles s'en tiennent à eux.
    indicateurs = tuple(tuple(cle.split("|")) for cle in sorted(
        _paquet()["caracteristiques_retraites"]["valeurs"])) if site_js.disponible() else ()
    trois_sexes = (("F",), ("H",), ("ensemble",))
    series = ("serie:depenses/total", *(f"serie:effectifs/{c}" for c in caisses))

    ages = tuple((age,) for age in _pas(0.0, 120.0, 0.0625)
                 + [62.999, 63.0001, 64.58, 66.5 + 1 / 24, 67 - 1e-9])
    macros = ("macro:", "macro:cor_productivite_basse", "macro:ocde_2025")
    reperes = (1950, 1972, 1990, 2000, 2010, 2020, 2024, 2025, 2030, 2050, 2080)
    paires_d_annees = tuple((de, a) for de in reperes for a in reperes)
    jours = tuple((Jour(f"{annee}-{mois:02d}-01"),) for annee in range(1945, 2031)
                  for mois in (1, 7)) + ((Jour("1991-01-31"),), (Jour("1991-02-01"),))
    from retraite_notionnelle.donnees.prelevements_historiques import (
        charger_prelevements_historiques)
    historiques = charger_prelevements_historiques(DATA)
    codes = tuple(_catalogue_python(False)._regimes)
    regimes = tuple(f"regime:{code}" for code in codes) + tuple(
        f"regime_moyen:{code}" for code in codes)
    periodes = tuple(f"periode:{code}/{rang}" for code in codes
                     for rang in range(len(_catalogue_python(False)[code].periodes)))
    annees_des_regimes = tuple((annee,) for annee in (
        *range(1850, 2101, 5), 1945, 1946, 1972, 1983, 1993, 2003, 2004, 2012, 2019, 2023, 2026))
    series_historiques = tuple(f"historiques:{groupe}/{serie}"
                               for groupe in ("pensions", "salaires", "independants")
                               for serie in getattr(historiques, groupe))

    from retraite_notionnelle.donnees.equilibre import (
        ORGANISMES, POSTES, POSTES_TRANSFERTS, variantes_disponibles)
    variantes = ("reference", *variantes_disponibles(DATA / "reference" / "macro"))
    tous_les_comptes = tuple(f"comptes:{v}" for v in variantes)
    comptes = _objet_python("comptes:reference")
    annees_du_compte = tuple((annee,) for annee in comptes.annees())
    decomposition = _objet_python("decomposition")
    grandeurs = sorted({g for g, _ in decomposition.series})
    groupes = sorted({g for _, g in decomposition.series})
    reperes_cor = (2000, 2002, 2010, 2020, 2024, 2025, 2026, 2030, 2040, 2045, 2050, 2070, 2071)
    taux_cor = sorted({g for taux in decomposition.croissances.values() for g in taux})
    from retraite_notionnelle.contributions_equilibre import charger_contributions_equilibre
    contributions = tuple(f"contribution:{c.code}"
                          for c in charger_contributions_equilibre(DATA).contributions)

    return {
        # La courbe des taux : sans prime de terme, et avec celle du réglage
        # « primé » (0,6 point à trente ans).
        (TAUX, "prime"): Grille(courbes, tuple((h,) for h in horizons)),
        (TAUX, "zero_continu"): Grille(courbes, tuple((h,) for h in horizons)),
        (TAUX, "zero_neutre"): Grille(courbes, tuple((h,) for h in horizons)),
        (TAUX, "forward_neutre"): Grille(courbes, tuple(
            (d, n) for d in differes for n in durees)),
        (TAUX, "maturite_maximale"): Grille(courbes),
        (TAUX, "placement"): Grille(courbes, tuple(
            (annee, duree) for annee in range(2015, 2091, 5)
            for duree in (1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 50)),
            champs=("taux", "differe", "duree", "fiabilite")),

        # La mortalité : les lois, les cellules, les courbes et les populations.
        # Les populations publiées à plusieurs âges ont leurs facteurs par
        # tranche d'âge (action 161, étape 9l).
        (MORTALITE, "loi"): Grille(mortalite, tuple(
            (annee, sexe) for annee in range(1940, 2131, 5) for sexe in sexes),
            champs=("a", "b", "k", "annee", "sexe", "fiabilite")),
        (MORTALITE, "_survie_cellule"): Grille(mortalite, tuple(
            (age, annee, sexe) for age in range(0, 121, 5)
            for annee in range(1950, 2131, 10) for sexe in sexes)),
        (MORTALITE, "survie_annuelle"): Grille(mortalite, tuple(
            (age, annee, sexe, facteur) for age in (20.0, 55.5, 60.0, 64.75, 85.25, 104.0, 119.5)
            for annee in (1960.0, 2003.5, 2025.0, 2072.25) for sexe in sexes
            for facteur in (1.0, 0.85, 1.3))),
        (MORTALITE, "courbe_survie"): Grille(mortalite, tuple(
            (age, annee, sexe, generation, population) for age, annee in departs
            for sexe in sexes for generation in generations
            for population in choix_populations)),
        (MORTALITE, "_courbe_brute"): Grille(mortalite, tuple(
            (age, annee, sexe, generation, facteur) for age, annee in departs
            for sexe in sexes for generation in generations for facteur in (1.0, 1.15))),
        (MORTALITE, "courbe_survie_unisexe"): Grille(mortalite, tuple(
            (age, annee, generation, population) for age, annee in departs
            for generation in generations for population in choix_populations)),
        (MORTALITE, "courbe"): Grille(mortalite, tuple(
            (age, annee, sexe, generation) for age, annee in departs
            for sexe in (None, *sexes) for generation in generations)),
        (MORTALITE, "esperance_residuelle"): Grille(mortalite, tuple(
            (age, annee, sexe, generation, population) for age, annee in departs
            for sexe in (None, *sexes) for generation in generations
            for population in choix_populations)),
        (MORTALITE, "populations"): Grille(mortalite),
        (MORTALITE, "_reference_population"): Grille(mortalite, tuple(populations)),
        (MORTALITE, "cible_population"): Grille(mortalite, tuple(populations)),
        (MORTALITE, "facteur_population"): Grille(mortalite, tuple(populations)),
        (MORTALITE, "facteurs_par_age"): Grille(mortalite, tuple(populations + par_age)),
        (MORTALITE, "_publiee_par_age"): Grille(mortalite, tuple(populations + par_age)),
        # La bissection, dès l'âge seul ou sous des tranches plus âgées déjà
        # calées, comme le portage la refait quand le paquet n'a pas les
        # facteurs par tranche.
        (MORTALITE, "_caler"): Grille(mortalite, (
            (65.0, 2017, "H", 16.5), (62.0, 2017, "F", 23.4, ((65, 0.95), (80, 1.1))),
            (80.0, 2017, "H", 8.5, ((85, 0.9),)))),
        (MORTALITE, "population_niveau_de_vie"): Grille(mortalite, tuple(
            (rapport,) for rapport in _pas(0.0, 4.0, 0.05))),
        (MORTALITE, "population_niveau_de_vie_euros"): Grille(mortalite, tuple(
            (montant,) for montant in _pas(0.0, 8000.0, 50.0))),

        # Le patrimoine des ménages : le quantile de la loi normale, chaque
        # population et la grille de ses rangs.
        (PATRIMOINE, "quantile_normal"): Grille(("module:patrimoine",), tuple(
            (p,) for p in [1e-12, 1e-6, 0.001, 0.02425, 0.97575, 0.999, 1 - 1e-6]
            + _pas(0.0005, 0.998, 0.0025))),
        (PATRIMOINE, "populations"): Grille(tous),
        (PATRIMOINE, "annee"): Grille(tous, tuple((p,) for p in _populations_patrimoine())),
        (PATRIMOINE, "statistiques"): Grille(tous, tuple(
            (p,) for p in _populations_patrimoine())),
        (PATRIMOINE, "distribution"): Grille(tous, tuple(
            (p,) for p in _populations_patrimoine()),
            champs=("population", "annee", "patrimoine", "quantiles", "mediane", "moyenne")),
        (PATRIMOINE, "forme"): Grille(par_population),
        (PATRIMOINE, "grille"): Grille(par_population),

        # La distribution des pensions, par sexe.
        (DISTRIBUTION, "part_sous"): Grille(pensions, tuple(
            (montant,) for montant in _pas(0.0, 7000.0, 25.0) + [-10.0, 1e5])),

        # L'assiette de l'activité, sur les années publiées et au-delà, où
        # le taux de prélèvement se lit à la dernière année publiée.
        (ASSIETTE, "annee_de_reference"): Grille(("assiette",), annees),
        (ASSIETTE, "montant"): Grille(("assiette",), annees),
        (ASSIETTE, "part_pib"): Grille(("assiette",), annees),
        (ASSIETTE, "taux_prelevement"): Grille(("assiette",), tuple(
            (ressources, annee) for ressources in (0.0, 0.1373, 0.14)
            for (annee,) in annees)),

        # L'assiette de la TVA, nette et brute.
        (TVA, "assiettes"): Grille(("tva",), ((True,), (False,))),
        (TVA, "montant"): Grille(("tva",), ((True,), (False,))),
        (TVA, "part_pib"): Grille(("tva",), ((True,), (False,))),

        # Les effectifs de retraités, par caisse.
        (EFFECTIFS, "caisses"): Grille(("effectifs",), ((),)),
        (EFFECTIFS, "serie"): Grille(("effectifs",), tuple((c,) for c in caisses),
                                     champs=("nom", "interpolation",
                                             "premiere_annee", "derniere_annee")),
        (EFFECTIFS, "effectif"): Grille(("effectifs",), tuple(
            (c, annee) for c in caisses for (annee,) in annees)),

        # La dépense de retraite, son total, ses systèmes et sa réversion.
        (DEPENSES, "annees"): Grille(("depenses",), ((),)),
        (DEPENSES, "depense"): Grille(("depenses",), annees),
        (DEPENSES, "depense_systeme"): Grille(("depenses",), tuple(
            (code, annee) for code in CODES_SYSTEMES for (annee,) in annees_publiees)),
        (DEPENSES, "fiabilite"): Grille(("depenses",), annees),
        (DEPENSES, "part_pib"): Grille(("depenses",), annees_publiees),
        (DEPENSES, "repartition"): Grille(("depenses",), annees_publiees),
        (DEPENSES, "part_repartition"): Grille(("depenses",), annees),
        (DEPENSES, "reversion"): Grille(("depenses",), annees),

        # La vie en couple, par âge, et sa moyenne sur des expositions.
        (COUPLE, "part"): Grille(("couple",), tuple(
            (age, sexe, mode) for age in _pas(40.0, 110.0, 0.5)
            for sexe in sexes for mode in modes)),
        (COUPLE, "part_moyenne"): Grille(("couple",), tuple(
            (sexe, exposition, debut, mode) for sexe in sexes
            for exposition in expositions for debut in (60, 65, 70) for mode in modes)),

        # La série annuelle, lue en ses années, avant, entre et après elles.
        (CHARGEMENT, "brut"): Grille(series, annees, champs=("valeur", "fiabilite")),
        (CHARGEMENT, "fiabilite"): Grille(series, annees),
        (CHARGEMENT, "prolongee"): Grille(series, tuple(
            (valeur, jusqu_a, fiabilite) for valeur in (0.0, 1234.5)
            for jusqu_a in (1990, 2030, 2070) for fiabilite in (0, 2)),
            # Le nom d'une série n'est qu'une étiquette des messages d'erreur,
            # que le paquet ne porte pas : « total » au portage.
            champs=("interpolation", "premiere_annee", "derniere_annee")),

        # Les caractéristiques des retraités de la DREES.
        (CARACTERISTIQUES, "valeur"): Grille(("caracteristiques",), indicateurs),
        (CARACTERISTIQUES, "part_femmes"): Grille(("caracteristiques",)),
        (CARACTERISTIQUES, "part_non_cotisee"): Grille(("caracteristiques",), trois_sexes),
        (CARACTERISTIQUES, "part_majorations"): Grille(("caracteristiques",), trois_sexes),
        (CARACTERISTIQUES, "beneficiaires_minimum"): Grille(("caracteristiques",), tuple(
            (sexe, Nommes(regime_principal=principal)) for (sexe,) in trois_sexes
            for principal in (True, False))),
        (CARACTERISTIQUES, "rapport_deplacement"): Grille(("caracteristiques",), ((),)),

        # Le calendrier : les âges en années et mois, les mois en rangs.
        (CALENDRIER, "decomposer"): Grille(("module:calendrier",), ages),
        (CALENDRIER, "formater_age"): Grille(("module:calendrier",), ages),
        # L'arrondi au mois, au demi-mois exact surtout, qui compte le mois
        # qui suit des deux côtés (fiche `date_effet_mois_suivant`).
        (CALENDRIER, "en_mois"): Grille(("module:calendrier",), tuple((age,) for age in sorted(
            {n + k / 24 for n in range(16, 80) for k in range(24)}
            | {n / 8 for n in range(800)} | {0.1 * n for n in range(1000)}))),
        (CALENDRIER, "depuis_rang"): Grille(("classe:DateMois",), tuple(
            (rang,) for rang in range(1900 * 12, 2101 * 12, 7)), champs=("annee", "mois")),
        (CALENDRIER, "rang"): Grille(tuple(
            f"date:{annee}-{mois}" for annee in (1900, 1946, 1999, 2000, 2026, 2100)
            for mois in range(1, 13))),

        # Les paramètres : une copie modifiée, un champ ou plusieurs.
        (CONFIG, "avec"): Grille(("parametres",), (
            (Nommes(taux_cotisation_liberal=0.2),),
            (Nommes(scenario_projection="cor_productivite_basse"),),
            (Nommes(prime_terme_trente_ans=0.006, taux_capitalisation_obligatoire=0.05),),
            (Nommes(),)), sauf=("racine_donnees",), module_js="config"),

        # La macroéconomie, sous chaque scénario de projection : prix, salaire
        # moyen, SMIC, revalorisation des salaires portés au compte.
        (MACRO, "coefficient_prix"): Grille(macros, paires_d_annees),
        (MACRO, "coefficient_salaire_moyen"): Grille(macros, paires_d_annees),
        (MACRO, "smic_annuel"): Grille(macros, tuple((annee,) for annee in range(1950, 2081))),
        (MACRO, "coefficient_revalorisation_salaires"): Grille(macros, paires_d_annees),
        (MACRO, "coefficient_revalorisation_portee_au_compte"): Grille(macros, tuple(
            (de, a, mois) for de, a in paires_d_annees for mois in (1, 4, 10))),
        (MACRO, "coefficient_revalorisation_par_rapport"): Grille(macros, tuple(
            (de, a, mois) for de, a in paires_d_annees for mois in (1, 4, 10))),
        # Le portage rend la colonne avec sa date d'effet, que le Python ne
        # rend pas : on en compare les coefficients et la dernière année.
        (MACRO, "colonne_de_revalorisation_en_vigueur"): Grille(macros, tuple(
            (annee, mois) for annee in range(1945, 2081, 3) for mois in (1, 4, 10)),
            en_liste=("coefficients", "derniere")),

        # Les prélèvements d'hier : chaque série, en chaque jour d'une grille.
        (HISTORIQUES, "en_vigueur"): Grille(series_historiques, jours),
        (HISTORIQUES, "valeur"): Grille(series_historiques, tuple(
            (*jour, cle) for jour in jours for cle in ("taux", "deductible", "plafond"))),
        (HISTORIQUES, "csg_deductible_pension"): Grille(("historiques",), tuple(
            (*jour, taux) for jour in jours for taux in ("plein", "median", "reduit"))),

        # Les régimes : la période de chaque année, sous les taux de la fiche
        # et sous les taux moyens des entreprises (``dater_les_taux_moyens``).
        (REGIMES, "periode"): Grille(regimes, annees_des_regimes,
                                    champs=CHAMPS_DE_LA_PERIODE),
        (REGIMES, "periodes_actives"): Grille(regimes, annees_des_regimes,
                                              champs=CHAMPS_DE_LA_PERIODE),
        (REGIMES, "couvre"): Grille(periodes, tuple((annee,) for annee in (
            1800, 1900, 1945, 1946, 1972, 1983, 1993, 2003, 2004, 2019, 2026, 2100))),
        (REGIMES, "effet"): Grille(periodes),
        (REGIMES, "taux_cotisation_salarie"): Grille(periodes),
        (REGIMES, "bornes_assiette_en_pass"): Grille(periodes, ((),)),
        (REGIMES, "morceau_d_annees"): Grille(("module:regimes",), tuple(
            (Objet(periode), debut, fin, EnTable(champs))
            # Des périodes datées au jour, et d'autres à l'année.
            for periode, morceaux in (
                ("periode:regime_general/16", ((1979, 1980), (1981, 1982), (1979, 1982))),
                ("periode:regime_general/17", ((1983, 1983),)),
                ("periode:cps_saint_pierre_et_miquelon/19", ((2017, 2019), (2020, 2022))),
                ("periode:cps_saint_pierre_et_miquelon/22", ((2026, 2030), (2027, None))),
                ("periode:cnracl/0", ((1945, 1960), (1961, 1983))))
            for debut, fin in morceaux
            for champs in ({}, {"taux_cotisation_retraite": 0.1})),
            lire=_morceau),
        (REGIMES, "taux"): Grille(("employeurs",), tuple(
            (regime, annee, militaire)
            for regime in ("cnracl", "fonction_publique_etat", "ieg", "sncf", "inconnu")
            for annee in range(1940, 2081, 2) for militaire in (False, True)),
            lire=_contribution),


        # Les comptes du COR, sous chaque variante : la dépense, la ressource,
        # la structure des ressources, les transferts, les engagements.
        (EQUILIBRE, "variantes_disponibles"): Grille(("module:equilibre",), (
            (SousRacine("reference/macro"),),)),
        (EQUILIBRE, "variante_du_scenario"): Grille(("module:equilibre",), tuple(
            (scenario, SousRacine("reference/macro"))
            for scenario in (None, "", "reference", "inconnu", *variantes))),
        (EQUILIBRE, "annees"): Grille(tous_les_comptes, ((),)),
        (EQUILIBRE, "depense"): Grille(tous_les_comptes, annees_du_compte),
        (EQUILIBRE, "ressource"): Grille(tous_les_comptes, annees_du_compte),
        (EQUILIBRE, "fiabilite"): Grille(tous_les_comptes, annees_du_compte),
        (EQUILIBRE, "part"): Grille(tous_les_comptes, tuple(
            (poste.code, annee) for poste in POSTES for (annee,) in annees_du_compte)),
        (EQUILIBRE, "part_contributive"): Grille(tous_les_comptes, annees_du_compte),
        (EQUILIBRE, "annees_engagements"): Grille(tous_les_comptes, ((),)),
        (EQUILIBRE, "engagements"): Grille(tous_les_comptes, tuple(
            (annee, regime) for annee in comptes.annees_engagements()
            for regime in ("tous_regimes", "repartition"))),
        (EQUILIBRE, "premiere_annee_transferts"): Grille(tous_les_comptes),
        (EQUILIBRE, "derniere_annee_transferts"): Grille(tous_les_comptes),
        (EQUILIBRE, "transfert"): Grille(tous_les_comptes, tuple(
            (poste.code, annee) for poste in POSTES_TRANSFERTS
            for annee in comptes.annees_transferts())),
        (EQUILIBRE, "transfert_organisme"): Grille(tous_les_comptes, tuple(
            (organisme.code, annee) for organisme in ORGANISMES
            for annee in comptes.annees_transferts())),
        (EQUILIBRE, "transfert_part_pib"): Grille(tous_les_comptes, tuple(
            (organisme.code, annee) for organisme in ORGANISMES
            for annee in comptes.annees_transferts())),
        (EQUILIBRE, "transfert_supprime_part_pib"): Grille(tous_les_comptes, tuple(
            (annee, Nommes(par_impot=par_impot, organisme=organisme))
            for annee in comptes.annees_transferts() for par_impot in (None, True, False)
            for organisme in (None, *(o.code for o in ORGANISMES)))),
        # Ce qui fait la dépense chez le COR : les grandeurs par groupe, leurs
        # indices, et les croissances par sous-période.
        (EQUILIBRE, "valeur"): Grille(("decomposition",), tuple(
            (grandeur, groupe, annee) for grandeur in (*grandeurs, "inconnue")
            for groupe in groupes for annee in reperes_cor)),
        (EQUILIBRE, "indice"): Grille(("decomposition",), tuple(
            (grandeur, groupe, depuis, annee) for grandeur in grandeurs for groupe in groupes
            for depuis in reperes_cor for annee in reperes_cor)),
        (EQUILIBRE, "periodes"): Grille(("decomposition",), ((),)),
        (EQUILIBRE, "indice_croissance"): Grille(("decomposition",), tuple(
            (grandeur, depuis, annee) for grandeur in taux_cor
            for depuis in reperes_cor for annee in reperes_cor)),

        # Le bilan figé, chargé de chaque côté : du JSON du dépôt en Python, de
        # la clé du paquet au portage ; l'engagement acquis qu'en lit la prose.
        (BILAN, "charger_bilan"): Grille(("module:bilan",), ((SOURCE,),),
                                         cle_du_paquet="bilan_equilibre", lire=_bilan),
        (BILAN, "part_pib"): Grille(("bilan:engagements",), tuple(
            (scenario,) for scenario in (*_scenarios_du_bilan(), "inconnu"))),
        (BILAN, "ecart_pour"): Grille(("bilan:engagements",), tuple(
            (cible,) for cible in _pas(0.0, 6.0, 0.01))),

        # Le contexte de la fabrique : ce que rend chacun de ses accesseurs,
        # lu par des méthodes que ces grilles confrontent déjà.
        (CONTEXTE, "assiette"): Grille(("contexte",), ((),), lire=_par_annee("montant")),
        (CONTEXTE, "depenses"): Grille(("contexte",), ((),), lire=_par_annee("depense")),
        (CONTEXTE, "comptes"): Grille(("contexte",), ((),), lire=_comptes_du_contexte),
        (CONTEXTE, "simulateur"): Grille(("contexte",), ((),), lire=_parametres),

        # Les contributions d'équilibre, par ce qu'elles prélèvent : le barème
        # de chaque mois, que le portage n'exporte pas, sur des règles que
        # chaque côté charge à sa manière.
        (CONTRIBUTIONS, "montant"): Grille(contributions, tuple(
            (annee, assiette, 40000.0, cadre, salarie)
            for annee in (1995, 2000, 2001, 2002, 2010, 2018, 2019, 2020, 2026)
            for assiette in (0.0, 20000.0, 40000.0, 100000.0, 200000.0, 400000.0)
            for cadre in (False, True) for salarie in (False, True)),
            module_js="contributions-equilibre", nom_js="montantDeLaContribution"),

        # La frontière contributive, chargée de chaque côté.
        (FRONTIERE, "charger_frontiere"): Grille(("module:frontiere",), ((SOURCE,),), champs=(
            "annees:annee,assiette_md,taux,total_md,salariale_md,patronale_md",
            "tranches:nom,acquisitif,verse_sous_plafond,verse_au_dessus,part_sous_plafond",
            "pourcentage_appel", "source_complementaire", "lu_le")),
    }


GRILLES = _grilles()

#: Les fonctions gardées que leur forme empêche de confronter seules, et la
#: grille de la fonction qui les appelle des deux côtés, par laquelle elles se
#: confrontent : un chargeur dont le portage rend des tables brutes, une
#: fonction que le portage n'exporte pas, deux signatures qui diffèrent.
#: La grille de l'appelant peut être celle d'une fonction qui n'est pas
#: gardée, comme ``montant`` des contributions, que le portage écrit
#: ``montantDeLaContribution``.
PAR_L_APPELANT = {
    (HISTORIQUES, "charger_prelevements_historiques"): (
        (HISTORIQUES, "valeur"),
        "le portage rend des tables, dont chaque série se lit par la grille de valeur"),
    (CONTRIBUTIONS, "charger_contributions_equilibre"): (
        (CONTRIBUTIONS, "montant"),
        "le portage rend des tables brutes, que montantDeLaContribution lit"),
    (CONTRIBUTIONS, "bareme"): (
        (CONTRIBUTIONS, "montant"),
        "contributions-equilibre.js ne l'exporte pas : le barème de chaque mois"),
    (REGIMES, "_en_vigueur"): (
        (REGIMES, "taux"),
        "les deux côtés n'ont pas la même signature ; taux le lit à chaque année"),
    (REGIMES, "dater_les_taux_moyens"): (
        (REGIMES, "periode"),
        "le catalogue aux taux moyens le fait courir sur chaque régime"),
    (CONTEXTE, "_donnee"): (
        (CONTEXTE, "comptes"),
        "la mémoire des données du contexte, que comptes, assiette et dépenses lisent"),
}

#: Les fonctions dont les deux exemplaires ne disent pas la même chose, et
#: pourquoi : leur confrontation est attendue rouge (``xfail`` strict), et
#: rougit la suite le jour où ils se rejoignent, pour qu'on retire la ligne.
ECARTS_DECLARES = {
    (BILAN, "ecart_pour"):
        "l'interpolation ne s'associe pas de même : (Δécart × Δvaleur) / largeur "
        "en Python, Δécart × (Δvaleur / largeur) au portage — un écart au dernier "
        "bit, sur l'écart de taux que la prose cite et que le site n'écrit pas",
}


# -- la comparaison --------------------------------------------------------------

def _en_python(valeur):
    """Une valeur Python dans la forme que JSON donne au portage."""
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
        return {champ.name: _en_python(getattr(valeur, champ.name))
                for champ in dataclasses.fields(valeur)}
    if isinstance(valeur, dict):
        return {cle: _en_python(v) for cle, v in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_en_python(v) for v in valeur]
    return valeur


def ecarts(relu, attendu, chemin: str = "", tolerance: float = 0.0) -> list[str]:
    """Où ``relu`` (le portage) diffère de ``attendu`` (le Python).

    Un nombre vaut un nombre, entier ou flottant : JSON n'écrit pas « 0.0 »,
    et le JavaScript n'a qu'un type. Deux flottants sont égaux au bit près, à
    ``tolerance`` près en écart relatif si elle n'est pas nulle ; deux NaN
    sont égaux. Un booléen n'est pas un nombre."""
    nombre = (int, float)
    if isinstance(attendu, bool) or isinstance(relu, bool):
        return [] if relu is attendu else [f"{chemin} : {relu!r} au portage, {attendu!r} en Python"]
    if isinstance(attendu, nombre) and isinstance(relu, nombre):
        a, b = float(relu), float(attendu)
        if a == b or (math.isnan(a) and math.isnan(b)):
            return []
        if tolerance and math.isfinite(a) and math.isfinite(b) and (
                abs(a - b) <= tolerance * max(abs(a), abs(b))):
            return []
        return [f"{chemin} : {relu!r} au portage, {attendu!r} en Python"]
    if isinstance(attendu, dict) and isinstance(relu, dict):
        if sorted(map(str, relu)) != sorted(map(str, attendu)):
            return [f"{chemin} : clés {sorted(map(str, relu))} au portage, "
                    f"{sorted(map(str, attendu))} en Python"]
        relus = {str(cle): valeur for cle, valeur in relu.items()}
        return [e for cle in attendu
                for e in ecarts(relus[str(cle)], attendu[cle], f"{chemin}.{cle}", tolerance)]
    if isinstance(attendu, list) and isinstance(relu, list):
        if len(relu) != len(attendu):
            return [f"{chemin} : {len(relu)} éléments au portage, {len(attendu)} en Python"]
        return [e for rang, (lu, element) in enumerate(zip(relu, attendu))
                for e in ecarts(lu, element, f"{chemin}[{rang}]", tolerance)]
    if relu == attendu and type(relu) is type(attendu):
        return []
    return [f"{chemin} : {relu!r} au portage, {attendu!r} en Python"]


def _champs(objet, champs: tuple[str, ...]):
    if objet is None:
        return None
    if isinstance(objet, (list, tuple)):
        return [_champs(element, champs) for element in objet]
    lus = {}
    for champ in champs:
        nom, _, sous = champ.partition(":")
        valeur = getattr(objet, nom)
        if sous:
            noms = tuple(sous.split(","))
            valeur = ([_champs(v, noms) for v in valeur] if isinstance(valeur, (list, tuple))
                      else _champs(valeur, noms))
        lus[nom] = valeur
    return lus


def _sans(valeur, sauf: tuple[str, ...]):
    if isinstance(valeur, dict):
        return {cle: _sans(v, sauf) for cle, v in valeur.items() if cle not in sauf}
    if isinstance(valeur, list):
        return [_sans(v, sauf) for v in valeur]
    return valeur


def _appeler(appeler, arguments: tuple, source, cote: str):
    """Un appel de la grille : :data:`SOURCE` remplacée, :class:`Nommes`
    passés par leur nom en Python, à leur rang au portage."""
    def objet(nom):
        return (_objet_python if cote == "python" else _objet_javascript)(nom)

    positionnels = [source if a is SOURCE else
                    (DATA / a if cote == "python" else _paquet()) if isinstance(a, SousRacine) else
                    objet(a) if isinstance(a, Objet) else
                    dt.date.fromisoformat(a) if isinstance(a, Jour) and cote == "python" else
                    str(a) if isinstance(a, Jour) else a
                    for a in arguments if not isinstance(a, Nommes)]
    nommes = next((a for a in arguments if isinstance(a, Nommes)), Nommes())
    if cote == "python":
        return appeler(*positionnels, **nommes)
    if isinstance(nommes, EnTable):
        return appeler(*positionnels, dict(nommes))
    return appeler(*positionnels, *nommes.values())


def _valeurs(fonction: str, grille: Grille, objet: str, cote: str):
    """Ce que rend, d'un côté, la fonction sur chaque point de sa grille."""
    if cote == "python":
        porteur, nom, source = _objet_python(objet), fonction, DATA
    else:
        porteur, nom, source = (_objet_javascript(objet), grille.nom_js or en_camel(fonction),
                                _paquet()[grille.cle_du_paquet] if grille.cle_du_paquet
                                else _paquet())
    if grille.appels is None:
        valeurs = [getattr(porteur, nom)]
    elif grille.module_js and cote == "javascript":
        fonction_js = getattr(site_js.module(grille.module_js), nom)
        valeurs = [fonction_js(porteur, *[a for a in arguments if not isinstance(a, Nommes)],
                               *[dict(a) for a in arguments if isinstance(a, Nommes)])
                   for arguments in grille.appels]
    else:
        appeler = getattr(porteur, nom)
        valeurs = [_appeler(appeler, arguments, source, cote) for arguments in grille.appels]
    if grille.lire:
        valeurs = [grille.lire(valeur, cote) for valeur in valeurs]
    if grille.champs:
        valeurs = [_champs(valeur, grille.champs) for valeur in valeurs]
    if grille.en_liste and cote == "javascript":
        valeurs = [valeur if valeur is None else [valeur[cle] for cle in grille.en_liste]
                   for valeur in valeurs]
    return [_sans(_en_python(valeur), grille.sauf) for valeur in valeurs]



@pytest.mark.parametrize(("fichier", "fonction"), [
    pytest.param(fichier, nom, id=f"{Path(fichier).stem}.{nom}", marks=(
        [pytest.mark.xfail(strict=True, reason=ECARTS_DECLARES[(fichier, nom)])]
        if (fichier, nom) in ECARTS_DECLARES else []))
    for fichier, nom in sorted(GRILLES)])
def test_la_fonction_gardee_rend_la_meme_valeur_des_deux_cotes(fichier, fonction):
    """Le Python sur le YAML et le portage sur le paquet rendent la même
    valeur, au bit près, en chaque point de la grille de la fonction."""
    if not site_js.disponible():
        pytest.skip("node absent : le portage n'est pas confrontable ici")
    grille = GRILLES[(fichier, fonction)]
    tous = []
    for objet in grille.objets:
        python = _valeurs(fonction, grille, objet, "python")
        portage = _valeurs(fonction, grille, objet, "javascript")
        appels = grille.appels or ((),)
        for arguments, lu, attendu in zip(appels, portage, python):
            tous += [f"{objet} {arguments} {e}"
                     for e in ecarts(lu, attendu, tolerance=TOLERANCE_DU_MOTEUR_PYTHON)]
    assert not tous, f"{len(tous)} écarts ; les premiers :\n" + "\n".join(tous[:15])


@pytest.mark.parametrize(("fichier", "fonction"), [
    pytest.param(fichier, nom, id=f"{Path(fichier).stem}.{nom}")
    for fichier, nom in sorted(PAR_L_APPELANT)])
def test_la_fonction_gardee_se_confronte_par_son_appelant(fichier, fonction):
    """Une fonction gardée que sa forme empêche de confronter seule l'est par
    la grille d'une fonction qui l'appelle des deux côtés, rejouée ici : le
    Python l'appelle, et le portage aussi, sous son nom."""
    appelant, _ = PAR_L_APPELANT[(fichier, fonction)]
    assert appelant in GRILLES, appelant
    # Elle est appelée en Python hors de sa définition : par l'appelant, ou,
    # pour un chargeur, par les objets de ce test, que l'appelant confronte.
    sources = (RACINE / fichier).read_text(encoding="utf-8") + Path(__file__).read_text(
        encoding="utf-8")
    assert f"{fonction}(" in sources.replace(f"def {fonction}(", ""), fonction
    test_la_fonction_gardee_rend_la_meme_valeur_des_deux_cotes(*appelant)


def _declarees(liste: dict, test: str) -> set[tuple[str, str]]:
    return {(fichier, nom) for fichier, paire in liste.items()
            for nom, entree in ((paire or {}).get("gardees") or {}).items()
            if (entree or {}).get("test") == test}


def test_chaque_grille_est_declaree_dans_la_liste_et_reciproquement():
    """La colonne ``test`` de la liste nomme ce test pour chaque fonction
    gardée qui a sa grille ici, et pour elles seules ; et le test de
    l'appelant pour chaque fonction confrontée par son appelant. Une grille
    qui n'est pas celle d'une fonction gardée est celle d'un appelant."""
    liste = yaml.safe_load(LISTE.read_text(encoding="utf-8")) or {}
    gardees = {(fichier, nom) for fichier, paire in liste.items()
               for nom in ((paire or {}).get("gardees") or {})}
    appelants = {appelant for appelant, _ in PAR_L_APPELANT.values()}
    assert set(GRILLES) <= gardees | appelants, sorted(set(GRILLES) - gardees - appelants)
    assert set(PAR_L_APPELANT) <= gardees, sorted(set(PAR_L_APPELANT) - gardees)
    avec_grille = set(GRILLES) & gardees
    declarees = _declarees(liste, CE_TEST)
    assert declarees == avec_grille, {
        "grille sans la ligne test": sorted(avec_grille - declarees),
        "ligne test sans grille": sorted(declarees - avec_grille)}
    par_l_appelant = _declarees(liste, PAR_SON_APPELANT)
    assert par_l_appelant == set(PAR_L_APPELANT), {
        "confrontée par son appelant sans la ligne test":
            sorted(set(PAR_L_APPELANT) - par_l_appelant),
        "ligne test sans appelant": sorted(par_l_appelant - set(PAR_L_APPELANT))}


def test_l_ecart_d_un_bit_se_voit():
    """La comparaison rougit au dernier bit d'un flottant, et ne confond ni un
    booléen avec un nombre, ni deux longueurs."""
    un = 0.1 + 0.2
    assert ecarts(un, 0.30000000000000004) == []
    assert ecarts(math.nextafter(un, 1.0), un)
    assert ecarts(0, 0.0) == [] and ecarts(float("nan"), float("nan")) == []
    assert ecarts(True, 1)
    assert ecarts([1.0], [1.0, 2.0])
    assert ecarts({"a": 1.0}, {"b": 1.0})
    assert ecarts(math.nextafter(un, 1.0), un, tolerance=1e-12) == []
