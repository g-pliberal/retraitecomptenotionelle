"""La figure 3B du jaune pensions du PLF 2027, lue sur ses tracés et certifiée.

``scripts/fetch/sre_jaune_ministeres.py`` lit les barres de la figure, que le
document ne chiffre pas ; ``scripts/verifier_donnees.py`` les certifie dans
``data/reference/macro/credits_ministeres.csv``. Le lecteur se tient ici sur
une figure fabriquée : l'échelle se prend sur l'axe, chaque peinture tient sa
place dans l'empilement, et un libellé qui n'est pas le sien arrête tout. Le
fichier certifié, lui, se confronte au texte du document : ce qu'il imprime
s'y retrouve, sauf aux deux points déclarés.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.donnees.credits_ministeres import CreditsMinisteres
from retraite_notionnelle.web.site import ErreurSite, disponible, module

RACINE = Path(__file__).resolve().parents[1]
CSV = RACINE / "data" / "reference" / "macro" / "credits_ministeres.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
from lecture_pdf import Aplat  # noqa: E402
from sre_jaune_ministeres import (  # noqa: E402
    INCOHERENCES_3B, MINISTERES, PARTS, figure_3b, incoherences_3b, intervalle,
)
from sre_jaune_referents import incoherences_declarees  # noqa: E402

GRIS = ("rgb", 0.851, 0.851, 0.851)
PEINTURES = dict(PARTS)


def _lignes(libelles: list[str] | None = None) -> list[str]:
    """Le texte de la page, tel que le lecteur le rend : sans les lettres
    accentuées que la police n'a pas."""
    return ["Figure 3B : Décomposition des crédits budgétaires des ministères selon leur nature",
            "Dcomposition des crdits budgtaires des ministres (PLF 2027)",
            *(libelles or [libelle for _, libelle in MINISTERES]),
            "0% 10% 20% 30% 40% 50% 60% 70% 80% 90% 100%",
            "T2 CAS", "T3 CAS*", "Cotisations salariales",
            "Reste des dpenses de personnel (dpenses de personnel hors T2 CAS et "
            "cotisations salariales)",
            "Reste des dpenses (dpenses hors dpenses de personnel)"]


def _aplats(barres: list[dict[str, float]], ordre=None) -> list[Aplat]:
    """L'axe à 100 points, dix graduations de 20 points — la dernière posée un
    vingtième trop à gauche, comme celle du jaune —, une case de légende hors
    du graphique, puis une barre par ministère, de haut en bas, ses parts
    empilées dans ``ordre``."""
    aplats = [Aplat(GRIS, x, 0.0, x, 200.0, trait=True)
              for x in [100.0 + 20.0 * k for k in range(10)] + [299.95]]
    aplats.append(Aplat(PEINTURES["t2_cas"], 20.0, -30.0, 25.0, -25.0))
    for rang, parts in enumerate(barres):
        y, x = 190.0 - 10.0 * rang, 100.0
        for part in ordre or [code for code, _ in PARTS]:
            if part in parts:
                aplats.append(Aplat(PEINTURES[part], x, y, x + 200.0 * parts[part], y + 7.0))
                x += 200.0 * parts[part]
    return aplats


BARRES = [{"t2_cas": 0.25 - 0.01 * rang, "cotisations_salariales": 0.03,
           "reste_personnel": 0.4, "reste_depenses": 0.32 + 0.01 * rang}
          for rang in range(len(MINISTERES))]


def test_la_figure_se_lit_sur_son_axe_et_rend_chaque_part_a_son_ministere():
    figure = figure_3b(_aplats(BARRES), _lignes())
    assert (figure["origine"], figure["longueur"]) == (100.0, 200.0)
    assert list(figure["ministeres"]) == [code for code, _ in MINISTERES]
    for (code, _), barre in zip(MINISTERES, BARRES):
        assert figure["ministeres"][code] == pytest.approx(barre, abs=1e-6), code


def test_une_part_qui_n_est_pas_a_sa_place_dans_l_empilement_arrete_la_lecture():
    """Les cotisations peintes avant la contribution : la peinture ne dit
    plus la part, et rien ne se lit."""
    ordre = ["cotisations_salariales", "t2_cas", "reste_personnel", "reste_depenses"]
    with pytest.raises(LookupError, match="t2_cas commence"):
        figure_3b(_aplats(BARRES, ordre), _lignes())


def test_un_libelle_qui_n_est_pas_le_sien_ou_une_barre_de_trop_arrete_la_lecture():
    libelles = [libelle for _, libelle in MINISTERES]
    libelles[3] = "Santé"
    with pytest.raises(LookupError, match="Santé"):
        figure_3b(_aplats(BARRES), _lignes(libelles))
    with pytest.raises(LookupError, match="18 barres"):
        figure_3b(_aplats(BARRES + BARRES[:1]), _lignes())


def test_un_chiffre_du_texte_laisse_a_la_part_son_arrondi():
    assert intervalle("32 %") == pytest.approx((0.315, 0.325))
    assert intervalle("25,1 / 89,1") == pytest.approx((25.05 / 89.15, 25.15 / 89.05))
    assert intervalle("< 1 %") == (0.0, 0.01)


def _certifiee() -> dict:
    """La figure telle que le fichier certifié la porte."""
    with CSV.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert {l["annee"] for l in lignes} == {"2027"}
    ministeres: dict[str, dict[str, float]] = {}
    for ligne in lignes:
        ministeres.setdefault(ligne["ministere"], {})[ligne["part"]] = float(ligne["valeur"])
    return {"ministeres": ministeres}


def test_le_fichier_certifie_porte_les_dix_sept_barres_et_leurs_parts():
    """Quatre parts par ministère, et le T3 CAS du seul Enseignement
    supérieur ; chaque barre fait l'axe, sauf la sienne."""
    ministeres = _certifiee()["ministeres"]
    assert set(ministeres) == {code for code, _ in MINISTERES}
    for code, parts in ministeres.items():
        attendues = {"t2_cas", "cotisations_salariales", "reste_personnel", "reste_depenses"}
        if code == "enseignement_superieur":
            attendues.add("t3_cas")
        assert set(parts) == attendues, code


def test_le_fichier_certifie_ne_s_ecarte_du_texte_qu_aux_points_declares():
    """Les parts de l'Éducation nationale et de l'Intérieur que la synthèse,
    les figures B et B bis et la lecture de la figure impriment, la Justice
    au bas de « entre 18 et 28 % », les deux derniers ministères sous 1 % :
    tout s'y retrouve, sauf la barre de l'Enseignement supérieur et la borne
    basse de « entre 20 % et 32 % », déclarées, et que la lecture montre
    encore."""
    messages = incoherences_3b(_certifiee())
    assert incoherences_declarees(messages, INCOHERENCES_3B) == ([], [])
    assert len(messages) == len(INCOHERENCES_3B) == 2


@pytest.mark.skipif(not disponible(), reason="node absent : le portage ne se lit pas")
def test_le_portage_range_les_ministeres_par_ce_qu_ils_versent():
    """Ce que la page montre, que le portage seul calcule sur le paquet
    (``moteur/js/credits-ministeres.js``, note de décision 0005) : du plus au
    moins versé au compte « Pensions » — la contribution employeur, T2 et
    T3 CAS, puis la retenue des fonctionnaires —, la contribution de
    l'Enseignement supérieur comptant celle de ses opérateurs, une part que la
    barre ne trace pas valant zéro, et un ministère absent de la figure
    refusé. L'attendu se calcule ici, sur le fichier certifié, dans l'ordre
    d'addition du portage : de gauche à droite, depuis zéro."""
    ministeres = _certifiee()["ministeres"]

    def contribution(code: str) -> float:
        return 0.0 + ministeres[code]["t2_cas"] + ministeres[code].get("t3_cas", 0.0)

    def au_compte_pensions(code: str) -> float:
        return contribution(code) + ministeres[code]["cotisations_salariales"]

    # Le paquet porte ce que le chargeur du Python lit du fichier certifié.
    chargeur = CreditsMinisteres(RACINE / "data")
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    assert paquet["credits_ministeres"] == {
        "annee": chargeur.annee, "fiabilite": int(chargeur.fiabilite),
        "parts": {f"{code}|{part}": valeur
                  for code, parts in sorted(ministeres.items())
                  for part, valeur in sorted(parts.items())}}
    credits = module("credits-ministeres").CreditsMinisteres(paquet)
    assert credits.annee == chargeur.annee == 2027
    assert list(credits.ministeres) == sorted(
        ministeres, key=lambda code: (-au_compte_pensions(code), code))
    assert list(credits.ministeres[:2]) == ["education_nationale", "interieur"]
    for code in ministeres:
        assert credits.contribution(code) == contribution(code), code
        assert credits.au_compte_pensions(code) == au_compte_pensions(code), code
    assert credits.part("justice", "t3_cas") == 0.0
    assert credits.contribution("enseignement_superieur") == (
        ministeres["enseignement_superieur"]["t2_cas"]
        + ministeres["enseignement_superieur"]["t3_cas"])
    with pytest.raises(ErreurSite, match="ministère absent de la figure 3B : sante"):
        credits.part("sante", "t2_cas")
