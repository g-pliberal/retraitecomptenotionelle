"""Le lecteur des projets annuels de performances, sur des lignes fabriquées.

Aucun test n'ouvre un PDF : les lignes ci-dessous sont celles que
`lecture_pdf.lignes_pdf` a rendues des PAP du PLF 2026 le 20 septembre 2026,
espaces baladeuses et codes Windows-1252 compris. Trois familles à tenir : les
séries annuelles par leur ligne d'années — le libellé sur trois lignes, les
milliers séparés d'espaces ordinaires —, les crédits par action, et les points
en prose cherchés sans aucune espace.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import pap_plf_2026 as pap  # noqa: E402

SECTION_198 = [
    "03 – Régime de retraite du personnel de la SNCF",
    "Hors titre 2 3 225 801 919 3 225 801 919 0 0",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Ratio",
    "0,68 0,68 0,68 0,67 0,66 0,65 0,64 0.63 0.60 0.58 0,57 0,57",
    "démographique",
    "Données moyennes du flux de nouveaux pensionnés :",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Années",
    "35,25 35,50 35,95 36,15 36,45 37,25 37,50 37,50 37,75 38,05 38,27 38,05",
    "validées (a)",
    "Années",
    "34,70 34,95 35,50 35,70 35,95 36,45 36,80 37,10 37,35 37,65 37,84 37,66",
    "cotisées (b)",
    "ratio a/b 1,02 1,02 1,01 1,01 1,01 1,02 1,02 1,01 1,01 1,01 1,01 1,01",
    "Les années validées comprennent les bonifications propres au régime de retraite SNCF.",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Subvention",
    "3 307 3 334 3 311 3 281 3 266 3 271 3 307 3 219 3 385 3 252 3 239 3 245",
    "versée (a)",
    "Pensions",
    "5 268 5 317 5 313 5 289 5 266 5 308 5 327 5 308 5 272 5 218 5 310 5 385",
    "servies (b)",
    "Ratio a/b 0,63 0,63 0,62 0,62 0,62 0,62 0,62 0,61 0,64 0,62 0,61 0,60",
    "En millions d’euros.",
    "04 – Régime de retraite du personnel de la RATP",
    "Hors titre 2 885 633 671 885 633 671 0 0",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Âge 54,46 55,25 54,7 54,8 55,11 55,46 55,86 56,11 56,46 56,81 56,99",
    "57,6 ans",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Trimestres",
    "119.32 121,11 120,73 122,19 121,25 122,91 123,79 124,37 125,6 125,8 127,4 125,2",
    "cotisés (a)",
    "Trimestres",
    "157,68 158,79 158,98 160,32 162,52 163,60 165,02 165,27 167,1 168,3 168,9 168,5",
    "validés (b)",
    "Année 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023",
    "Pensions",
    "992 1 028 1 043 1 059 1 088 1 125 1 153 1 169 1185 1199 1246 1297",
    "servies* (b)",
    "05 – Autres régimes",
    "Hors titre 2 11 244 196 11 244 196 0 0",
]


def test_douze_nombres_aux_milliers_espaces_se_decoupent_par_comptage():
    assert pap.decouper("3 307 3 334 3 311".split(), 3) == [3307, 3334, 3311]
    assert pap.decouper("992 1 028 1 043".split(), 3) == [992, 1028, 1043]
    assert pap.decouper("0,68 0.63 1 041,7".split(), 3) == [0.68, 0.63, 1041.7]
    assert pap.decouper("3 225 801 919 0 0".split(), 3) == [3225801919, 0, 0]
    # Le compte fait foi : onze nombres pour douze colonnes, ce n'est pas une ligne de valeurs.
    assert pap.decouper("54,46 55,25 54,7".split(), 4) is None
    assert pap.decouper("Subvention 3 307".split(), 1) is None


def test_une_ligne_de_valeurs_rend_son_libelle_de_tete():
    assert pap.ligne_de_valeurs("Ratio a/b 0,63 0,63 0,62", 3) == ("Ratio a/b", [0.63, 0.63, 0.62])
    assert pap.ligne_de_valeurs("3 307 3 334", 2) == ("", [3307, 3334])
    assert pap.ligne_de_valeurs("versée (a)", 12) is None


def test_les_series_du_programme_198_suivent_leur_ligne_d_annees():
    lu = pap.series_198(SECTION_198)
    assert lu[(2012, "sncf", "ratio_demographique")] == 0.68
    assert lu[(2019, "sncf", "ratio_demographique")] == 0.63
    assert lu[(2023, "sncf", "annees_validees_flux")] == 38.05
    assert lu[(2023, "sncf", "annees_cotisees_flux")] == 37.66
    assert lu[(2012, "sncf", "subvention_meur")] == 3307
    assert lu[(2023, "sncf", "pensions_servies_meur")] == 5385
    assert lu[(2012, "ratp", "trimestres_cotises_flux")] == 119.32
    assert lu[(2023, "ratp", "trimestres_valides_flux")] == 168.5
    assert lu[(2013, "ratp", "pensions_servies_meur")] == 1028
    assert lu[(2023, "ratp", "pensions_servies_meur")] == 1297
    # Ni le ratio a/b, ni les âges, ni la phrase sur les bonifications ne sont des postes.
    postes = {cle[2] for cle in lu}
    assert "age_moyen_depart_ensemble" not in postes
    assert all(cle[1] in ("sncf", "ratp") for cle in lu)
    assert len([cle for cle in lu if cle[1] == "sncf"]) == 5 * 12


def test_les_credits_par_action_viennent_de_la_ligne_hors_titre_2():
    lu = pap.credits_actions(SECTION_198)
    assert lu == {(2026, "sncf", "credits_etat_meur"): 3225.8,
                  (2026, "ratp", "credits_etat_meur"): 885.6}


def test_les_points_se_cherchent_sans_espace_ni_apostrophe():
    texte = pap.compact(" ".join([
        "La CPRPF compte 110 846 cotisants pour 229 329 pensionnés en 2023, année pour laquelle",
        "Le régime social des marins est en dés équilibre structurel sur la branche retraite, avec un ratio de 0,28 entre le",
        "nombre d’actifs et de pensionnés (29 037 actifs cotisants en 2024 pour 102 001 pensionnés et 102 667 pensions",
        "1 056,8 M€ en 2026 (prévisi on d’atterrissage 2025 de 1 070,8 M€, exécutions à 1 089,3 M€ en 2024, 1 029,8 M€ en",
        "2023, et 1 016,9 M€ en 2022).",
    ]))
    lu = pap.points(texte, pap.POINTS_MISSION)
    assert lu[(2023, "sncf", "cotisants")] == 110846
    assert lu[(2023, "sncf", "pensionnes")] == 229329
    assert lu[(2024, "enim", "ratio_demographique")] == 0.28
    assert lu[(2024, "enim", "pensions_en_paiement")] == 102667
    assert lu[(2025, "enim", "depenses_branche_vieillesse_meur")] == 1070.8
    assert lu[(2022, "enim", "depenses_branche_vieillesse_meur")] == 1016.9


def test_le_compte_d_affectation_speciale_ecrit_ses_apostrophes_en_windows_1252():
    """Sa police rend « s’établir » comme « s\\x92établir » et « M€ » comme
    « M\\x80 » : on les lit comme tels, et « 64 ans et 2 mois » devient 64.17."""
    texte = pap.compact(" ".join([
        "progresser pour s\x92établir à 64 ans et 2 mois en 2024.",
        "La dépense de retraite progressive en 2024 est de 30,02 M\x80. En prenant en compte",
        "Il passe en moyenne de 2 478 \x80 à 2 529 \x80, confirmant la hausse",
    ]))
    lu = pap.points(texte, pap.POINTS_CAS)
    assert lu[(2024, "fonction_publique_etat", "age_moyen_depart_sedentaires")] == 64.17
    assert lu[(2024, "fonction_publique_etat", "retraite_progressive_meur")] == 30.02
    assert lu[(2024, "fonction_publique_etat", "pension_mensuelle_nouveaux_sedentaires_eur")] == 2529
    assert pap.annees_decimales("48anset11mois") == 48.92
    with pytest.raises(ValueError):
        pap.annees_decimales("48 ans")


def test_les_petits_tableaux_du_programme_741_se_lisent_sous_leur_entete():
    lignes = [
        "Civils 2025 2026 2027 2028",
        "Entrées de pensions de",
        "45 990 44 575 43 235 44 030",
        "droit direct",
        "Civils, en M\x80 N=2024 N=2025 N=2026 N=2027 N=2028",
        "Dépenses N-1 49 662 52 523 53 793 53 756 54 016",
        "Dépenses N 52 523 53 793 53 756 54 016 54 454",
    ]
    lu = pap.tableaux_cas(lignes)
    assert lu[(2025, "fonction_publique_etat", "nouvelles_pensions_civiles_droit_direct")] == 45990
    assert lu[(2028, "fonction_publique_etat", "nouvelles_pensions_civiles_droit_direct")] == 44030
    assert lu[(2024, "fonction_publique_etat", "depenses_pensions_civiles_meur")] == 52523
    assert lu[(2028, "fonction_publique_etat", "depenses_pensions_civiles_meur")] == 54454
    assert (2024, "fonction_publique_etat", "depenses_pensions_militaires_meur") not in lu


def test_la_source_du_verificateur_reprend_la_cle_du_csv(monkeypatch):
    chemin = RACINE / "scripts" / "verifier_donnees.py"
    specification = importlib.util.spec_from_file_location("verifier_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_donnees"] = module
    specification.loader.exec_module(module)
    monkeypatch.setattr(module, "_lire_json", lambda nom, script: {
        "serie": {"2023|sncf|subvention_meur": 3245, "2012|ratp|ratio_demographique": 0.89}})
    assert module.source_pap_plf_2026() == {
        ("2012", "ratp", "ratio_demographique"): 0.89,
        ("2023", "sncf", "subvention_meur"): 3245.0,
    }
    # Sans décimales imposées, le vérificateur écrit chaque valeur au plus court.
    certification = next(c for c in module.CERTIFICATIONS if c.nom == "pap_regimes_subventionnes")
    assert certification.niveau == "haute"
    assert certification.format(3307.0) == "3307"
    assert certification.format(0.57) == "0.57"
    assert certification.format(35.25) == "35.25"
