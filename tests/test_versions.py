"""La version d'une fiche qui s'applique à une situation : ``noyau/versions.py``.

``docs/architecture.md``, § 4.1. Le moteur lit les versions des fiches qu'il
applique — les trimestres des enfants, la réversion, l'invalidité, les
carrières hors de France, les périodes réputées cotisées — par une seule
fonction, sur les fiches que son paquet porte préparées. Ce test tient la
lecture sur ces fiches : à chaque cas de bascule, la veille et le jour de
chaque borne, une version et une seule s'applique, celle que le partage
désigne.
"""

from __future__ import annotations

import itertools
import json
from datetime import date
from pathlib import Path

import pytest

from retraite_notionnelle.noyau import carte, partage, versions

#: Les fiches dont le portage lit les versions, que son paquet porte préparées.
PAQUET = Path(__file__).resolve().parents[1] / "moteur" / "donnees.json"
LUES = sorted(json.loads(PAQUET.read_text(encoding="utf-8"))["versions_des_fiches"])


@pytest.mark.parametrize("nom", LUES)
def test_une_version_et_une_seule_a_chaque_bascule(nom):
    """La veille et le jour de chaque borne, pour chaque combinaison des dates
    qui décident : exactement la version dont les bornes les contiennent,
    l'exception plutôt que la version dont elle l'est, sauf là où le
    vocabulaire tient la combinaison pour impossible."""
    fiche = carte.fiches()[nom]
    preparee = versions.preparer(fiche)
    noms = fiche["dates_qui_decident"]
    points = {n: sorted({jour for autre, veille, lendemain in partage.bascules(fiche)
                         if autre == n for jour in (veille, lendemain)} | {date(2026, 9, 27)})
              for n in noms}
    for combinaison in itertools.product(*(points[n] for n in noms)):
        situation = dict(zip(noms, combinaison))
        if ("enfant.naissance" in situation and "liquidation.date_effet" in situation
                and situation["enfant.naissance"] > situation["liquidation.date_effet"]):
            continue
        version = versions.applicable(preparee, {n: d.isoformat() for n, d in situation.items()})
        assert version is not None, (nom, situation)
        contiennent = [v for v in fiche["versions"]
                       if all((v["bornes"].get(n, [None, None])[0] is None
                               or v["bornes"][n][0] <= situation[n])
                              and (v["bornes"].get(n, [None, None])[1] is None
                                   or situation[n] < v["bornes"][n][1]) for n in noms)]
        exceptees = {v.get("exception_de") for v in contiennent}
        attendue = [v["id"] for v in contiennent if v["id"] not in exceptees]
        assert [version["id"]] == attendue, (nom, situation)


def test_la_fiche_preparee_ne_garde_que_ce_que_le_moteur_lit():
    fiche = versions.preparer(carte.fiches()["enfants_fonction_publique"])
    assert set(fiche) == {"id", "dates_qui_decident", "versions"}
    l12bis = next(v for v in fiche["versions"] if v["id"] == "l12bis")
    assert l12bis == {
        "id": "l12bis",
        "bornes": {"enfant.naissance": ["2004-01-01", None],
                   "liquidation.date_effet": ["2004-01-01", "2026-09-01"]},
        "exception_de": None,
        "texte": "LEGIARTI000006362697",
        "parametres": {"trimestres_par_enfant": 2, "services_par_enfant": 0,
                       "beneficiaire": "mere", "condition": "accouchement_apres_recrutement",
                       "fiabilite": "moyenne"},
    }


def test_une_date_qui_manque_ou_que_la_fiche_ignore_arrete_la_lecture():
    fiche = versions.preparer(carte.fiches()["majoration_duree_assurance_enfants"])
    with pytest.raises(ValueError, match="dates qui décident"):
        versions.applicable(fiche, {"liquidation.date_effet": "2026-01-01"})
    with pytest.raises(ValueError, match="dates qui décident"):
        versions.applicable(fiche, {"liquidation.date_effet": "2026-01-01",
                                    "enfant.naissance": "2000-01-01",
                                    "assure.naissance": "1960-01-01"})


def test_l_exception_l_emporte_et_deux_versions_sans_elle_arretent():
    fiche = {"id": "essai", "dates_qui_decident": ["liquidation.date_effet"], "versions": [
        {"id": "generale", "bornes": {"liquidation.date_effet": [None, None]},
         "exception_de": None, "texte": None, "parametres": {}},
        {"id": "particuliere", "bornes": {"liquidation.date_effet": ["2020-01-01", None]},
         "exception_de": "generale", "texte": None, "parametres": {}},
    ]}
    assert versions.applicable(fiche, {"liquidation.date_effet": "2019-12-31"})["id"] == "generale"
    assert versions.applicable(fiche, {"liquidation.date_effet": "2020-01-01"})["id"] == "particuliere"
    fiche["versions"][1]["exception_de"] = None
    with pytest.raises(ValueError, match="le partage n'en admet qu'une"):
        versions.applicable(fiche, {"liquidation.date_effet": "2020-01-01"})
