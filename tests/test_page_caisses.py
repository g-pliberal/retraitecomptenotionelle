"""La page « Les caisses » : chaque caisse de retraite, comment elle marche.

Demandée par le propriétaire le 17 novembre 2026 (action 193) : « je veux les
fonctionnements de chaque caisse », sur la maquette qu'il a validée. La page
montre, pour chaque caisse, combien de cotisants paient pour un retraité,
comment on y gagne des droits, comment la pension se calcule, d'où vient son
argent et qui décide.

Les valeurs attendues viennent des sources, lues à la main dans les fichiers
du dépôt qui les portent : les cotisants et les retraités de 2024 et la
structure de financement de 2023, des compléments du rapport du COR de juin
2024 (``cotisants.csv``, ``retraites_projetes.csv``,
``structure_financement.csv``) ; les réserves de fin 2025, du tableau 2.3 du
rapport du COR de juin 2026 (``reserves_regimes.csv``) ; les prix et valeurs
du point de 2026, des barèmes des caisses (``valeurs_point.csv``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from retraite_notionnelle.donnees.caisses_du_site import CAISSES, lire
from retraite_notionnelle.web.site import disponible, module, rendre

DONNEES = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def caisses() -> dict:
    return lire(DONNEES)


def test_les_effectifs_sont_ceux_du_cor_en_2024(caisses):
    # COR, juin 2024 : 22 410 157 cotisants et 14 830 231 retraités de droit
    # direct au régime général ; aux mines, 765 cotisants pour 89 513 retraités.
    assert caisses["cnav"]["cotisants"] == 22410157
    assert caisses["cnav"]["retraites"] == 14830231
    assert caisses["mines"]["cotisants"] == 765
    assert caisses["mines"]["retraites"] == 89513
    # La fonction publique d'État : civils (1 641 776) et militaires (387 735).
    assert caisses["fpe"]["retraites"] == 1641776 + 387735


def test_le_financement_est_celui_de_2023_regroupe_en_six_postes(caisses):
    # SNCF, 2023 : 36,0 % de cotisations, 60,8 % de subvention de l'État,
    # 1,3 % de compensation démographique et 0,3 % de transferts, soit 1,6 %
    # venus des autres caisses, 0,5 % d'autres produits.
    sncf = caisses["sncf"]["financement"]
    assert sncf["cotisations"] == pytest.approx(0.360, abs=5e-4)
    assert sncf["etat"] == pytest.approx(0.608, abs=5e-4)
    assert sncf["autres_caisses"] == pytest.approx(0.016, abs=5e-4)
    # La CNRACL : 7,1 % de besoin de financement, que personne ne couvre.
    assert caisses["cnracl"]["financement"]["non_finance"] == pytest.approx(0.071, abs=5e-4)
    # La fonction publique d'État : 86,0 % de contribution d'équilibre.
    assert caisses["fpe"]["financement"]["etat"] == pytest.approx(0.860, abs=5e-4)


def test_les_reserves_sont_celles_de_fin_2025(caisses):
    assert caisses["agirc_arrco"]["reserves"] == {"montant_md": 113.6, "mois": 14}
    assert caisses["banque_de_france"]["reserves"] == {"montant_md": 13.4, "mois": 277}
    # Les libéraux : la base (4,1) et les sections (39,0), ensemble ; le COR
    # donne leurs mois séparément, la somme n'en a pas.
    assert caisses["cnavpl"]["reserves"] == {"montant_md": pytest.approx(43.1), "mois": None}
    # Le régime général n'est pas au tableau : il n'a pas de réserves.
    assert caisses["cnav"]["reserves"] is None


def test_le_point_de_2026_est_celui_des_baremes(caisses):
    assert caisses["agirc_arrco"]["point"] == {
        "prix": 20.1877, "valeur": 1.4587, "appel": 1.27}
    assert caisses["ircantec"]["point"] == {
        "prix": 5.787, "valeur": 0.56053, "appel": 1.269643}
    assert caisses["rafp"]["point"] == {"prix": 1.4596, "valeur": 0.05671, "appel": 1.0}
    assert caisses["cnav"]["point"] is None


def test_chaque_caisse_a_toutes_ses_donnees(caisses):
    assert list(caisses) == [c.ident for c in CAISSES]
    for ident, caisse in caisses.items():
        assert caisse["cotisants"] > 0 and caisse["retraites"] > 0, ident
        assert 0.85 < sum(caisse["financement"].values()) < 1.12, ident


def test_le_paquet_porte_les_caisses(caisses):
    import json
    paquet = json.loads((Path(__file__).resolve().parents[1] / "moteur" / "donnees.json")
                        .read_text(encoding="utf-8"))
    assert paquet["caisses"] == caisses


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_la_page_montre_chaque_caisse_et_son_fonctionnement():
    titre, corps = rendre("/caisses")
    assert titre == "Les caisses"
    texte = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps))
    for nom in ("Assurance retraite", "Agirc-Arrco", "CNRACL", "Ircantec", "RAFP",
                "SNCF", "RATP", "Banque de France", "Mines"):
        assert nom in texte, nom
    # Une bulle par caisse, qui mène à sa fiche.
    for c in CAISSES:
        assert f'href="#caisse-{c.ident}"' in corps or f'data-vers="caisse-{c.ident}"' in corps, c.ident
        assert f'id="caisse-{c.ident}"' in corps, c.ident
    # La CNRACL : 2 194 281 cotisants pour 1 387 162 retraités, soit 1,6.
    cnracl = corps[corps.index('id="caisse-cnracl"'):]
    cnracl = cnracl[:cnracl.index("</details>")]
    assert "1,6" in cnracl
    assert "7 €" in re.sub(r"<[^>]+>", "", cnracl).replace("\u00a0", " ").replace("\u202f", " ")
    # La SNCF : 61 € sur 100 viennent de l'État.
    sncf = corps[corps.index('id="caisse-sncf"'):]
    sncf = re.sub(r"<[^>]+>", "", sncf[:sncf.index("</details>")]).replace("\u00a0", " ").replace("\u202f", " ")
    assert "61 €" in sncf
    # L'Agirc-Arrco : 100 € cotisés rapportent 5,69 € de pension par an
    # (100 / 1,27 / 20,1877 × 1,4587).
    aa = corps[corps.index('id="caisse-agirc_arrco"'):]
    aa = re.sub(r"<[^>]+>", "", aa[:aa.index("</details>")]).replace("\u00a0", " ").replace("\u202f", " ")
    assert "5,69 €" in aa


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_la_page_est_au_pied_et_non_au_bandeau():
    # Au bandeau, un onglet de plus le faisait passer sur deux rangées au
    # bureau, et la carte des flux de Coût sortait de l'écran : la page est
    # fabriquée comme les autres, et le pied de chaque page y mène.
    g = module("gabarit")
    assert "/caisses" in g.PAGES
    assert "/caisses" not in [chemin for chemin, _ in g.LIENS]
    # Le lien est relatif à la page rendue : « caisses/ », « ../caisses/ »,
    # ou « ./ » sur la page elle-même.
    assert re.search(r'href="(\.\./caisses/|caisses/|\./)">les caisses</a>', g.pied())


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_les_caisses_viennent_dans_l_ordre_des_familles():
    # Le régime général d'abord, puis l'Agirc-Arrco : l'ordre de la page, et
    # non celui, alphabétique, des clés du paquet.
    _, corps = rendre("/caisses")
    ordre = re.findall(r'id="caisse-([a-z_]+)"', corps)
    assert ordre == [c.ident for c in CAISSES]
