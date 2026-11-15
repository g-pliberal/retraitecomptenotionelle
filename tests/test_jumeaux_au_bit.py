"""Chaque fonction gardée des deux côtés rend la même valeur en Python et en
JavaScript, au bit près (action 161, étape 7b).

La liste ``scripts/jumeaux_gardees.yaml`` déclare, dans les paires qui restent
après le retrait du moteur Python, les fonctions écrites des deux côtés que la
fabrique, le coût ou une étude lisent en Python pendant que le site les
calcule en JavaScript. Les deux exemplaires ne doivent pas diverger : le
Python les calcule sur le YAML (``data/``), le portage sur le paquet
(``moteur/donnees.json``), et chacune se confronte ici sur une grille
d'arguments déclarée avec elle (:data:`GRILLES`). Une fonction confrontée ici
le dit dans la liste, colonne ``test`` ; une grille sans cette ligne, ou
l'inverse, rougit.

Le portage se lit par ``web/site.py`` : ses objets sont bâtis sur le paquet du
contexte du site, que node garde, et leurs méthodes appelées une à une.
« Au bit près » est la tolérance du moteur Python (``outils_pont``) : nulle
sous Linux x86_64, où GitHub joue la suite, 10⁻¹² en écart relatif ailleurs,
où la libm du système déplace la dernière décimale de quelques flottants.
"""

from __future__ import annotations

import dataclasses
import enum
import math
import sys
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

TAUX = "src/retraite_notionnelle/donnees/taux.py"
MORTALITE = "src/retraite_notionnelle/donnees/mortalite.py"
PATRIMOINE = "src/retraite_notionnelle/donnees/patrimoine.py"
DISTRIBUTION = "src/retraite_notionnelle/donnees/distribution.py"


class _Racine:
    """L'argument qui vaut ``data/`` en Python et le paquet en JavaScript."""

    def __repr__(self) -> str:
        return "RACINE"


#: À la place d'un argument : la racine des données en Python, le paquet
#: dans le portage, pour une fonction de module qui lit l'une ou l'autre.
SOURCE = _Racine()


# -- les objets confrontés -------------------------------------------------------

def _python(nom: str):
    """L'objet Python d'un nom de :data:`OBJETS`, bâti sur le YAML."""
    from retraite_notionnelle.donnees import distribution, mortalite, patrimoine, taux
    genre, _, detail = nom.partition(":")
    if genre == "module":
        return {"patrimoine": patrimoine, "distribution": distribution}[detail]
    if genre == "courbe":
        return taux.CourbeTauxSansRisque(DATA, float(detail))
    if genre == "mortalite":
        return mortalite.DonneesMortalite(DATA)
    if genre == "patrimoine":
        if not detail:
            return patrimoine.PatrimoineMenages(DATA)
        return _objet_python("patrimoine").distribution(detail)
    if genre == "pensions":
        # Le paquet porte la distribution des retraités qui résident en
        # France, comme la fabrique la lit (``_distribution_pensions_sexes``).
        return distribution.DistributionPensions(DATA, detail, residence="france")
    raise KeyError(nom)


def _javascript(nom: str):
    """L'objet du portage d'un nom de :data:`OBJETS`, bâti sur le paquet."""
    genre, _, detail = nom.partition(":")
    if genre == "module":
        return site_js.module(detail)
    if genre == "courbe":
        return site_js.module("taux").CourbeTauxSansRisque(_paquet(), float(detail))
    if genre == "mortalite":
        return site_js.module("mortalite").DonneesMortalite(_paquet())
    if genre == "patrimoine":
        if not detail:
            return site_js.module("patrimoine").PatrimoineMenages(_paquet())
        return _objet_javascript("patrimoine").distribution(detail)
    if genre == "pensions":
        return site_js.module("distribution").DistributionPensions(_paquet(), detail)
    raise KeyError(nom)


@lru_cache(maxsize=None)
def _objet_python(nom: str):
    return _python(nom)


@lru_cache(maxsize=None)
def _objet_javascript(nom: str):
    return _javascript(nom)


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
    compare."""

    objets: tuple[str, ...]
    appels: tuple[tuple, ...] | None = None
    champs: tuple[str, ...] = ()


def _pas(debut: float, fin: float, pas: float) -> list[float]:
    return [debut + rang * pas for rang in range(int(round((fin - debut) / pas)) + 1)]


def _populations_mortalite() -> list[tuple[str, str]]:
    """Les populations et les sexes que le paquet porte : celles qu'une seule
    espérance publiée cale. Une population publiée à plusieurs âges n'a ses
    facteurs par tranche d'âge que pour le coût, en Python."""
    from retraite_notionnelle.donnees.mortalite import DonneesMortalite
    mortalite = DonneesMortalite(DATA)
    return [(population, sexe) for population in mortalite.populations
            for sexe in DonneesMortalite.SEXES
            if not mortalite._publiee_par_age(population, sexe)]


def _populations_patrimoine() -> list[str]:
    from retraite_notionnelle.donnees.patrimoine import PatrimoineMenages
    return list(PatrimoineMenages(DATA).populations)


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
    choix_populations = (None, autres[0], niveaux[0], niveaux[-1])

    tous = ("patrimoine",)
    par_population = tuple(f"patrimoine:{p}" for p in _populations_patrimoine())
    pensions = tuple(f"pensions:{sexe}" for sexe in ("ensemble", "F", "H"))

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
        # Le paquet ne porte pas les populations publiées à plusieurs âges,
        # que seul le coût lit : elles n'entrent pas dans les grilles.
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
    }


GRILLES = _grilles()

#: Les fonctions dont les deux exemplaires ne disent pas la même chose, et
#: pourquoi : leur confrontation est attendue rouge (``xfail`` strict), et
#: rougit la suite le jour où ils se rejoignent, pour qu'on retire la ligne.
ECARTS_DECLARES = {
    (MORTALITE, "populations"):
        "le paquet ne porte pas les populations publiées à plusieurs âges "
        "(cnav_*), dont seul le coût lit les facteurs par tranche d'âge : "
        "21 populations au portage, 24 en Python",
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
        return [e for cle in attendu
                for e in ecarts(relu[str(cle)], attendu[cle], f"{chemin}.{cle}", tolerance)]
    if isinstance(attendu, list) and isinstance(relu, list):
        if len(relu) != len(attendu):
            return [f"{chemin} : {len(relu)} éléments au portage, {len(attendu)} en Python"]
        return [e for rang, (lu, element) in enumerate(zip(relu, attendu))
                for e in ecarts(lu, element, f"{chemin}[{rang}]", tolerance)]
    if relu == attendu and type(relu) is type(attendu):
        return []
    return [f"{chemin} : {relu!r} au portage, {attendu!r} en Python"]


def _champs(objet, champs: tuple[str, ...]):
    return {champ: getattr(objet, champ) for champ in champs}


def _valeurs(fonction: str, grille: Grille, objet: str, cote: str):
    """Ce que rend, d'un côté, la fonction sur chaque point de sa grille."""
    if cote == "python":
        porteur, nom, source = _objet_python(objet), fonction, DATA
    else:
        porteur, nom, source = _objet_javascript(objet), en_camel(fonction), _paquet()
    if grille.appels is None:
        valeurs = [getattr(porteur, nom)]
    else:
        appeler = getattr(porteur, nom)
        valeurs = [appeler(*(source if a is SOURCE else a for a in arguments))
                   for arguments in grille.appels]
    if grille.champs:
        valeurs = [_champs(valeur, grille.champs) for valeur in valeurs]
    return [_en_python(valeur) for valeur in valeurs]


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


def test_chaque_grille_est_declaree_dans_la_liste_et_reciproquement():
    """La colonne ``test`` de la liste nomme ce test pour chaque fonction qui a
    sa grille ici, et pour elles seules."""
    liste = yaml.safe_load(LISTE.read_text(encoding="utf-8")) or {}
    declarees = {(fichier, nom) for fichier, paire in liste.items()
                 for nom, entree in ((paire or {}).get("gardees") or {}).items()
                 if (entree or {}).get("test") == CE_TEST}
    gardees = {(fichier, nom) for fichier, paire in liste.items()
               for nom in ((paire or {}).get("gardees") or {})}
    assert set(GRILLES) <= gardees, sorted(set(GRILLES) - gardees)
    assert declarees == set(GRILLES), {
        "grille sans la ligne test": sorted(set(GRILLES) - declarees),
        "ligne test sans grille": sorted(declarees - set(GRILLES))}


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
