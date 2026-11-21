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

Le 21 novembre 2026, le propriétaire veut que la page montre TOUT, et que ce
qu'elle montre ne se recopie pas : les régimes que l'inventaire recense, chacun
marqué selon ce que le modèle en calcule et avec ses textes, sont fabriqués
depuis les fiches (``data/reference/regimes/``), et un test refuse la page
qu'un régime du modèle manquerait. La page « Droits non cotisés » tient la
même promesse pour les dispositifs (``avantages_non_contributifs.yaml``).
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import pytest

import yaml

from retraite_notionnelle.avantages import charger_avantages
from retraite_notionnelle.donnees.caisses_du_site import CAISSES, lire
from retraite_notionnelle.donnees.regimes import CatalogueRegimes, charger_inventaire
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
def test_la_page_est_au_menu():
    # Le propriétaire veut voir la page : un onglet du bandeau, au groupe
    # « Pour vérifier », et le pied de chaque page y mène aussi.
    g = module("gabarit")
    assert "/caisses" in g.PAGES
    assert "/caisses" in [chemin for chemin, _ in g.LIENS]
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


# -- Tout ce que les fiches recensent, sur la page ----------------------------

#: Ce que la page dit de chaque couverture de l'inventaire, dans les mots
#: que le propriétaire a choisis le 21 novembre 2026.
STATUTS = {
    "modelise": "calculé en entier",
    "partiel": "calculé en partie",
    "a_modeliser": "pas encore calculé",
    "routage": "calculé par un autre régime",
    "hors_champ": "hors champ",
}


def _texte(code: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", code)))


def _rangees(corps: str) -> dict[str, str]:
    table = re.search(r'<table id="inventaire">.*?</table>', corps, re.S)
    assert table, "la page ne porte pas la table des régimes"
    return dict(re.findall(r'<tr [^>]*data-code="([^"]+)"[^>]*>(.*?)</tr>', table.group(0), re.S))


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_chaque_regime_de_l_inventaire_est_sur_la_page_avec_son_statut():
    lignes = charger_inventaire(DONNEES)
    _, corps = rendre("/caisses")
    rangees = _rangees(corps)
    assert list(rangees) == [ligne.code for ligne in lignes]
    for ligne in lignes:
        rangee = _texte(rangees[ligne.code])
        assert " ".join(ligne.nom.split()) in rangee, ligne.code
        assert STATUTS[ligne.couverture] in rangee, ligne.code


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_chaque_regime_que_le_modele_calcule_est_sur_la_page():
    # Le modèle calcule les régimes du catalogue : chacun a sa ligne, marquée
    # calculée, en entier ou en partie. Une fiche qu'on y ajoute paraît sans
    # que personne ne la recopie, et la page qui l'oublierait échoue ici.
    _, corps = rendre("/caisses")
    rangees = _rangees(corps)
    for regime in CatalogueRegimes(DONNEES):
        assert regime.code in rangees, regime.code
        rangee = _texte(rangees[regime.code])
        assert "calculé en entier" in rangee or "calculé en partie" in rangee, regime.code


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_le_titre_de_la_liste_compte_ce_que_le_modele_calcule():
    lignes = charger_inventaire(DONNEES)
    _, corps = rendre("/caisses")
    entiers = sum(ligne.couverture == "modelise" for ligne in lignes)
    partiels = sum(ligne.couverture == "partiel" for ligne in lignes)
    resume = re.search(r'id="les-regimes".*?<summary>(.*?)</summary>', corps, re.S)
    assert resume, "la liste des régimes n'est pas un dépliant de la page"
    assert _texte(resume.group(1)).strip() == (
        f"Les {len(lignes)} régimes : {entiers} calculés en entier, {partiels} en partie")


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_chaque_regime_cite_ses_textes_et_les_lie_a_legifrance():
    lignes = charger_inventaire(DONNEES)
    _, corps = rendre("/caisses")
    rangees = _rangees(corps)
    for ligne in lignes:
        rangee = rangees[ligne.code]
        for texte in ligne.textes:
            assert " ".join(texte["reference"].split()) in _texte(rangee), ligne.code
            if texte["id"]:
                assert re.search(
                    rf'href="https://www\.legifrance\.gouv\.fr/[a-z]+/[a-z_]+/{texte["id"]}"',
                    rangee), (ligne.code, texte["id"])
    # Les quatre formes d'identifiant, chacune à son adresse : un article de
    # code, un article de loi, une loi au JORF, un article au JORF.
    assert 'href="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006745499"' \
        in rangees["agirc"]
    # « article L. 634-3 du code de la sécurité sociale » est aussi un article
    # de code, que la référence nomme après lui.
    assert any('href="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000036391704"'
               in rangee for rangee in rangees.values())
    assert any('href="https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006756839"'
               in rangee for rangee in rangees.values())
    assert 'href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000877358"' in rangees["cnrv"]
    assert any(re.search(r'href="https://www\.legifrance\.gouv\.fr/jorf/article_jo/JORFARTI\d+"',
                         rangee) for rangee in rangees.values())


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_la_liste_des_regimes_n_est_qu_a_un_endroit():
    # Méthode la portait : elle y renvoie désormais, sans la redire.
    _, methode = rendre("/methode")
    assert '<table id="inventaire">' not in methode
    assert re.search(r'href="\.\./caisses/#les-regimes"', methode)


# -- Les droits non cotisés : chaque dispositif, et ce que le modèle en fait ---

LIBELLES_ETATS = {
    "chiffre": "calculé, chiffré",
    "integre": "calculé, chiffré à part",
    "declare": "déclaré, pas encore calculé",
    "absent": "pas encore calculé",
}


@pytest.mark.skipif(not disponible(), reason="node absent")
def test_chaque_droit_non_cotise_du_modele_est_sur_la_page():
    inventaire = charger_avantages(DONNEES)
    _, corps = rendre("/avantages")
    liste = re.search(r'id="avantages-liste".*?</details>', corps, re.S)
    assert liste
    rangees = [_texte(r) for r in re.findall(r"<tr>(.*?)</tr>", liste.group(0), re.S)]
    for avantage in inventaire.avantages:
        trouvees = [r for r in rangees if r.strip().startswith(avantage.libelle)]
        assert trouvees, avantage.code
        # Un dispositif servi en partie (la réversion, au seul conjoint
        # déclaré) le dit dans les mots des régimes : « calculé en partie ».
        attendu = ("calculé en partie" if avantage.servi_en_partie
                   else LIBELLES_ETATS[avantage.etat_modele])
        assert attendu in trouvees[0], avantage.code
    # Ce que les fiches de régimes déclarent, sous un code ou sous un alias, y
    # mène toujours à une ligne de la page.
    brut = yaml.safe_load((DONNEES / "reference" / "legislation"
                           / "avantages_non_contributifs.yaml").read_text(encoding="utf-8"))
    libelle = {nom: a["libelle"] for a in brut["avantages"]
               for nom in [a["code"], *a.get("alias", [])]}
    for regime in CatalogueRegimes(DONNEES):
        for periode in regime.periodes:
            for code in periode.avantages_non_contributifs or ():
                assert any(r.strip().startswith(libelle[code]) for r in rangees), code
