"""Le lecteur du rapport de l'OPEF, sur le texte que pypdf lui rend.

Aucun test n'ouvre le document : le texte ci-dessous est celui que pypdf a
rendu des tableaux T6 et T7 du rapport 2026 le 20 septembre 2026, coquille du
rapport comprise (« Autre fraiss »). La forme est celle des trois tableaux de
frais du chapitre 2, et c'est elle que le lecteur reconnaît.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "fetch"))
import opef_frais_per as opef  # noqa: E402

TABLEAU_PER = """T7  Frais liés aux PER individuels en 2024 et 2025
(en %)
Types de frais – moyennes pondérées Frais 2024 Frais 2025
Frais ponctuels – frais sur versements – en % des versements effectués
Support fonds en euros 1,16 1,09
Support fonds Eurocroissance 1,86 1,91
Supports en unité de compte (hors produits structurés) : 1,62 1,51
dont gestion libre 1,28 1,22
dont autres modes de gestion a) 1,81 1,69
Supports en unité de compte : produits structurés 1,52 1,76
Frais récurrents – frais de gestion des contrats – en % des assiettes de prélèvement
Support fonds en euros 0,77 0,76
Support fonds Eurocroissance 0,72 0,72
Supports en unité de compte (hors produits structurés) : 0,91 0,91
dont gestion libre 0,93 0,89
dont autres modes de gestion a) 0,90 0,92
Supports en unité de compte : produits structurés 0,93 0,94
Autre fraiss
Frais d'arbitrage – en % du montant total arbitré dans l'année :
dont gestion libre 0,08 0,07
dont autres modes de gestion a) 0,00 0,00
Frais sur arrérages de rente (moyenne non pondérée) b)
 – en % du montant de chaque rente 2,19 2,20
Notes : a) Gestion pilotée, gestion pilotée profilée, gestion déléguée et gestion sous mandat.
b) Sur les 20 organismes déclarants, 9 ont reporté une facturation effective pour l'établissement de frais sur arrérages de rente.
Les moyennes présentées dans le tableau ne tiennent compte que de ces 9 cas.
Source : ACPR,  les frais liés aux PER à points et aux PER souscrits dans le cadre d'une entreprise ne sont pas pris en compte dans
ces statistiques.
"""

TABLEAU_CAPITALISATION = """T6  Frais liés aux contrats de capitalisation en 2024 et 2025
(en %)
Types de frais – moyennes pondérées Frais 2024 Frais 2025
Frais ponctuels – frais sur versements – en % des versements effectués
Support fonds en euros 0,17 0,19
Support fonds eurocroissance 0,61 0,53
Frais récurrents – frais de gestion des contrats – en % des assiettes de prélèvement
Support fonds en euros 0,67 0,70
Autre frais
Frais sur arrérages de rente (moyenne non pondérée) b)
 – en % du montant de chaque rente 2,94 2,94
b) Sur les 18 organismes déclarants, 5 ont reporté une facturation effective pour l'établissement de frais sur arrérages de rente.
Source : ACPR.
"""


def test_le_tableau_du_per_se_lit_par_exercice():
    table = opef.lire_tableau(TABLEAU_PER, opef.TABLEAUX["per_individuel"])
    assert table["exercices"] == {
        2024: {"versement": 0.0116, "gestion": 0.0077, "arrerages": 0.0219},
        2025: {"versement": 0.0109, "gestion": 0.0076, "arrerages": 0.0220},
    }


def test_la_moyenne_des_arrerages_dit_sur_combien_d_organismes_elle_porte():
    table = opef.lire_tableau(TABLEAU_PER, opef.TABLEAUX["per_individuel"])
    assert table["arrerages_organismes_declarants"] == 20
    assert table["arrerages_organismes_facturant"] == 9


def test_chaque_tableau_est_lu_dans_sa_propre_fenetre():
    """Deux tableaux dans le même texte : chacun rend ses valeurs, pas celles de l'autre."""
    texte = TABLEAU_CAPITALISATION + "\n" + TABLEAU_PER
    capi = opef.lire_tableau(texte, opef.TABLEAUX["capitalisation"])
    per = opef.lire_tableau(texte, opef.TABLEAUX["per_individuel"])
    assert capi["exercices"][2025] == {"versement": 0.0019, "gestion": 0.0070,
                                       "arrerages": 0.0294}
    assert per["exercices"][2025]["versement"] == 0.0109


def test_un_tableau_absent_est_une_erreur_et_non_un_zero():
    with pytest.raises(LookupError):
        opef.lire_tableau(TABLEAU_PER, opef.TABLEAUX["assurance_vie"])


def test_l_ordre_des_blocs_est_verifie():
    """Si les frais récurrents précédaient les ponctuels, versement et gestion s'intervertiraient."""
    inverse = TABLEAU_PER.replace("Frais ponctuels", "Frais RÉCURRENTS", 1) \
                         .replace("Frais récurrents", "Frais ponctuels", 1) \
                         .replace("Frais RÉCURRENTS", "Frais récurrents", 1)
    with pytest.raises(LookupError):
        opef.lire_tableau(inverse, opef.TABLEAUX["per_individuel"])


def test_la_saisie_du_depot_est_celle_du_document():
    """Le fichier de référence porte les valeurs 2025 du tableau T7, au dix-millième."""
    tables = {"per_individuel": opef.lire_tableau(TABLEAU_PER, opef.TABLEAUX["per_individuel"])}
    assert opef.confronter(tables) == []


def test_un_ecart_de_saisie_est_nomme(tmp_path):
    reference = tmp_path / "frais.yaml"
    reference.write_text(
        "annee_reference: 2025\nfrais:\n  versement: {valeur: 0.0116}\n"
        "  gestion: {valeur: 0.0076}\n  arrerages: {valeur: 0.0220}\n",
        encoding="utf-8",
    )
    tables = {"per_individuel": opef.lire_tableau(TABLEAU_PER, opef.TABLEAUX["per_individuel"])}
    ecarts = opef.confronter(tables, reference)
    assert len(ecarts) == 1 and ecarts[0].startswith("versement")
