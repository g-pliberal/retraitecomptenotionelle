"""La majoration pour conjoint à charge (L. 351-13 ; action 138, étape 17).

La pension du régime général est majorée quand le conjoint à charge du
titulaire a soixante-cinq ans et ne bénéficie d'aucun avantage de vieillesse :
4 000 F par an depuis le 1er juillet 1976, 609,80 € depuis 2002, proratisés par
la durée d'assurance depuis le 1er mars 1975, sans revalorisation ; supprimée à
compter du 1er janvier 2011, elle reste servie à qui l'avait au 31 décembre 2010
(fiche ``majoration_conjoint_a_charge``).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.droit import completer
from retraite_notionnelle.droit.commun import majoration_du_conjoint
from retraite_notionnelle.revalorisation import faire_vivre
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Un salarié du privé né en 1930, parti à soixante-cinq ans en 1995 avec la
#: durée entière, et son conjoint, sans ressources.
SANS_CONJOINT = {"naissance": "1930-03-15", "debut": "1952-09", "liquidation": "1995-04"}
PARTI_EN_1995 = {**SANS_CONJOINT, "ressources_conjoint": "0"}


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


def _simuler(contexte, **requete):
    saisie = Saisie.depuis_requete(requete)
    return saisie, contexte.simuler(saisie)


def _general(comparaison):
    return next(p for p in comparaison.actuel.pensions_par_regime
                if p.regime == "regime_general")


def _majoration(comparaison):
    return next((a for a in comparaison.actuel.avantages_appliques
                 if a.code == "majoration_conjoint_a_charge"), None)


# -- la fiche ----------------------------------------------------------------------

def test_la_fiche_date_le_prorata_et_la_suppression():
    """Entière avant le 1er mars 1975 ; en 150es jusqu'au décret du 12 janvier
    2007 ; sur la durée qui proratise la pension ensuite ; rien pour les
    pensions prenant effet depuis 2011. 4 000 F depuis 1976, 609,80 € depuis
    2002."""
    fiches = Simulateur().scenario_actuel.fiches_datees
    nom = completer.FICHE_DU_CONJOINT
    assert not fiches.regle(nom, "1948-06-01")["existe"]
    assert [fiches.regle(nom, date)["prorata"]
            for date in ("1960-01-01", "1975-03-01", "2007-02-01")] == [
        "aucun", 150, "duree_requise"]
    assert not fiches.regle(nom, "2011-01-01")["existe"]
    montants = fiches.regle(nom, "1990-01-01")["montants"]
    assert majoration_du_conjoint(montants, "1980-01-01") == pytest.approx(4000 / 6.55957)
    assert majoration_du_conjoint(montants, "2026-01-01") == 609.80


# -- la date d'effet ---------------------------------------------------------------

def test_le_conjoint_de_soixante_cinq_ans_ouvre_la_majoration_au_depart(contexte):
    _, sans = _simuler(contexte, **SANS_CONJOINT)
    _, avec = _simuler(contexte, **PARTI_EN_1995, conjoint="1928")
    assert _majoration(sans) is None
    majoration = _majoration(avec)
    assert majoration.montant == pytest.approx(4000 / 6.55957)
    assert _general(avec).montant == pytest.approx(_general(sans).montant + majoration.montant)
    assert "majoration pour conjoint à charge" in _general(avec).detail


def test_sans_ressources_dites_rien(contexte):
    requete = {**PARTI_EN_1995, "conjoint": "1928"}
    del requete["ressources_conjoint"]
    _, comparaison = _simuler(contexte, **requete)
    assert _majoration(comparaison) is None
    assert _general(comparaison).conjoint == ()


def test_les_ressources_du_conjoint_s_en_retranchent_et_la_duree_la_proratise(contexte):
    """Parti en 2008 avec 130 trimestres au régime général, qui en proratise
    154 : 609,80 × 130/154, moins les 100 € que le conjoint déclare."""
    _, comparaison = _simuler(contexte, naissance="1945-03-15", debut="1975-09",
                              liquidation="2008-04", conjoint="1943",
                              ressources_conjoint="100")
    assert "× 130/154" in _general(comparaison).detail
    assert _majoration(comparaison).montant == pytest.approx(609.80 * 130 / 154 - 100)


def test_avant_1975_la_majoration_est_entiere(contexte):
    _, comparaison = _simuler(contexte, naissance="1910-03-15", debut="1930-09",
                              liquidation="1972-04", conjoint="1905", ressources_conjoint="0")
    assert _majoration(comparaison).montant == pytest.approx(1850 / 6.55957)


def test_le_droit_ouvert_a_compter_de_2011_n_est_pas_servi(contexte):
    """La retraite qui prend effet en 2011 n'y a pas droit ; celle de 2009 non
    plus quand le conjoint n'a soixante-cinq ans qu'en 2011, et y a droit quand
    il les a en novembre 2010 (circulaire Cnav n° 2011-9)."""
    _, en_2011 = _simuler(contexte, naissance="1950-03-15", debut="1972-09",
                          liquidation="2011-04", conjoint="1940", ressources_conjoint="0")
    assert _general(en_2011).conjoint == ()
    _, tard = _simuler(contexte, naissance="1947-03-15", debut="1970-09",
                       liquidation="2009-04", conjoint="1946-02", ressources_conjoint="0")
    assert _general(tard).conjoint == ()
    _, a_temps = _simuler(contexte, naissance="1947-03-15", debut="1970-09",
                          liquidation="2009-04", conjoint="1945-11", ressources_conjoint="0")
    assert _general(a_temps).conjoint[0][0] == "2010-12-01"


# -- les échéances ------------------------------------------------------------------

def test_la_majoration_s_ouvre_aux_soixante_cinq_ans_du_conjoint_et_reste_nominale(contexte):
    """Le conjoint né en juin 1932 a soixante-cinq ans en juin 1997 : rien au
    départ de 1995, la majoration à compter de juillet 1997, 609,80 € en 2026,
    que la revalorisation de la pension ne mène pas."""
    saisie, comparaison = _simuler(contexte, **PARTI_EN_1995, conjoint="1932-06")
    _, sans = _simuler(contexte, **SANS_CONJOINT)
    assert _majoration(comparaison) is None
    assert _general(comparaison).conjoint[0] == ("1997-07-01", pytest.approx(4000 / 6.55957))
    assert "à compter de juillet 1997" in _general(comparaison).detail
    simulateur = contexte.simulateur(saisie.parametres(contexte.base))

    def general(resultat, annee):
        vivante = faire_vivre(simulateur, resultat.carriere, resultat.actuel, annee)
        return next(r for r in vivante.regimes if r.regime == "regime_general")

    assert general(comparaison, 1996).aujourd_hui == pytest.approx(
        general(sans, 1996).aujourd_hui)
    for annee, majoration in ((1997, 4000 / 6.55957), (2026, 609.80)):
        assert general(comparaison, annee).aujourd_hui == pytest.approx(
            general(sans, annee).aujourd_hui + majoration)


def test_la_majoration_du_depart_ne_se_revalorise_pas(contexte):
    saisie, comparaison = _simuler(contexte, **PARTI_EN_1995, conjoint="1928")
    simulateur = contexte.simulateur(saisie.parametres(contexte.base))
    vivante = faire_vivre(simulateur, comparaison.carriere, comparaison.actuel, 2026)
    general = next(r for r in vivante.regimes if r.regime == "regime_general")
    assert general.conjoint_au_depart == pytest.approx(4000 / 6.55957)
    assert general.aujourd_hui == pytest.approx(
        (general.au_depart - general.conjoint_au_depart) * general.coefficient + 609.80)
    donnees = {r["regime"]: r for r in vivante.donnees()["regimes"]}
    assert donnees["regime_general"]["majoration_conjoint_a_charge"] == 609.80
    assert "majoration_conjoint_a_charge" not in donnees["arrco"]


# -- les deux moteurs ---------------------------------------------------------------

CAS = [
    {**PARTI_EN_1995, "conjoint": "1928"},
    {**PARTI_EN_1995, "conjoint": "1932-06"},
    {"naissance": "1945-03-15", "debut": "1975-09", "liquidation": "2008-04",
     "conjoint": "1943", "ressources_conjoint": "100"},
    {"naissance": "1910-03-15", "debut": "1930-09", "liquidation": "1972-04",
     "conjoint": "1905", "ressources_conjoint": "0"},
]


def test_les_deux_moteurs_servent_la_meme_majoration(contexte):
    """Le résultat entier, aujourd'hui compris, est le même en Python et en
    JavaScript."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini

    attendus = [{"requete": cas, "resultat": _fini(
        contexte.simuler(Saisie.depuis_requete(cas)).dictionnaire())} for cas in CAS]
    texte = json.dumps(attendus, ensure_ascii=False)
    assert "majoration_conjoint_a_charge" in texte
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]
