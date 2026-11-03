"""Le régime des marins, lu au droit.

Trois fiches de la carte, lues au droit le 2 novembre 2026 (action 130) dans
les rédactions du code des pensions de retraite des marins — le décret
n° 68-292 du 21 mars 1968 le crée en abrogeant la loi du 12 avril 1941, le
décret n° 79-791 du 13 septembre 1979 remplace son article R. 14, le décret
n° 85-1159 du 5 novembre 1985 son article R. 13, le décret n° 99-265 du
1er avril 1999 lui ajoute R. 31 — et dans les articles du code des transports
qui reprennent sa partie législative depuis le 1er décembre 2010 :
l'ouverture de la pension d'ancienneté à cinquante ans et le plafond de ses
annuités avant cinquante-cinq ans (`marins_ouverture_cinquante_ans`), la
bonification pour enfants (`marins_bonification_enfants`), le salaire de
référence (`marins_salaire_de_reference`).

Chaque paramètre d'une version porte le nom du champ de la période qui le
porterait. La fiche de régime `regimes/marins.yaml`, une seule période depuis
1930, en porte la valeur ; sinon, la fiche déclare l'écart, et le test qui
suit `ECARTS_DECLARES` le tient, cas par cas. Une période couvre des années
entières : une version qui commence en cours d'année se confronte aux années
qu'elle couvre en entier.
"""

from __future__ import annotations

import csv
import sqlite3
from datetime import date

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

LOT = ("marins_ouverture_cinquante_ans", "marins_bonification_enfants",
       "marins_salaire_de_reference")
REFERENCE = RACINE_DONNEES / "reference"
PERIODES = yaml.safe_load((REFERENCE / "regimes" / "marins.yaml")
                          .read_text(encoding="utf-8"))["periodes"]
#: La première année de la fiche de régime, et la dernière que les
#: confrontations parcourent.
DEBUT, HORIZON = 1930, 2050
#: Les versions du salaire de référence, qui lisent toutes la règle de R. 11
#: et de R. 12.
SALAIRE = ("loi_du_12_avril_1941", "code_de_1968", "contrats_simultanes")

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ que la version lit et que la période des marins porte autrement, ou
#: ne porte pas, et l'article que cite l'approximation qui le déclare.
#: Avant le 7 novembre 1985, R. 13 plafonne à vingt-cinq annuités toute
#: pension d'ancienneté liquidée avant cinquante-cinq ans, sans l'exception
#: des cinquante-deux ans et demi que le modèle sert dès 1930 ; la
#: bonification ne compte que l'enfant élevé neuf ans, condition que le
#: modèle n'oppose pas ; le salaire de référence est la catégorie des
#: trente-six derniers mois, ou de fonctions supérieures tenues cinq ans, sur
#: des services décomptés au semestre, quand le modèle prend la catégorie de
#: la dernière année, rangée par le revenu, et compte au trimestre.
#: L'abattement au-delà de huit fois le traitement de l'indice 100 (R. 11, 3°),
#: la période le porte depuis le 3 novembre 2026 : il n'est plus un écart.
ECARTS_DECLARES = [
    *[("marins_ouverture_cinquante_ans", version, champ, "R. 13")
      for version in ("loi_du_12_avril_1941", "code_de_1968")
      for champ in ("duree_maximum_levee_age", "duree_maximum_levee_trimestres")],
    ("marins_bonification_enfants", "neuf_ans_d_education", "annees_d_education", "R. 14"),
    ("marins_bonification_enfants", "neuf_ans_d_education", "age_de_fin_d_education", "R. 14"),
    *[("marins_salaire_de_reference", version, champ, article)
      for version in SALAIRE
      for champ, article in (("mois_de_reference", "R. 11"),
                             ("annees_de_fonctions_superieures", "R. 11"),
                             ("mois_du_decompte_des_services", "R. 12"))],
    ("marins_salaire_de_reference", "contrats_simultanes", "contrats_simultanes", "R. 31"),
]

#: Le traitement de l'indice 100, en indice majoré : l'article 7 du décret
#: n° 85-1148 du 24 octobre 1985 le fixe « pour l'application des
#: dispositions législatives et réglementaires se référant au traitement de
#: l'indice 100 prévu par le décret du 10 juillet 1948 » jusqu'au 30 juin
#: 2008, « au traitement de l'indice 100 ou de l'indice brut 100 » depuis :
#: « ce traitement est constitué par le traitement afférent à l'indice majoré
#: 208 » au 1er janvier 2024. La date d'effet de chaque rédaction — celle que
#: le décret modificatif écrit (« à compter du 1er juillet 1998 »…) quand la
#: base LEGI date la rédaction de sa publication —, l'indice qu'elle écrit, et
#: son identifiant LEGI. Une rédaction qui ne change pas l'indice n'y est pas.
#: En mai et juin 2001, l'alinéa dit encore 164 : le décret n° 2001-370 ne le
#: touche pas, et le n° 2001-559, qui y remplace « l'indice majoré 169 », vise
#: un mot qu'il ne porte pas.
INDICE_100 = [
    ("1985-11-05", 150, "LEGIARTI000006454537"),
    ("1986-02-07", 152, "LEGIARTI000006454538"),
    ("1988-10-01", 154, "LEGIARTI000006454539"),
    ("1989-02-01", 155, "LEGIARTI000006454540"),
    ("1990-01-01", 156, "LEGIARTI000006454541"),
    ("1991-08-01", 158, "LEGIARTI000006454542"),
    ("1998-07-01", 160, "LEGIARTI000006454544"),
    ("1999-04-01", 161, "LEGIARTI000006454545"),
    ("1999-07-01", 163, "LEGIARTI000006454546"),
    ("1999-12-01", 164, "LEGIARTI000006454547"),
    ("2001-07-01", 172, "LEGIARTI000006454550"),
    ("2004-07-01", 174, "LEGIARTI000006454552"),
    ("2005-07-01", 186, "LEGIARTI000006454554"),
    ("2006-07-01", 190, "LEGIARTI000006454555"),
    ("2006-11-01", 191, "LEGIARTI000006454556"),
    ("2007-07-01", 194, "LEGIARTI000006454557"),
    ("2008-05-01", 199, "LEGIARTI000018728042"),
    ("2008-07-01", 201, "LEGIARTI000019111495"),
    ("2009-07-01", 203, "LEGIARTI000020817875"),
    ("2024-01-01", 208, "LEGIARTI000047751780"),
]


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _bornes(version: dict) -> list:
    return version["bornes"]["liquidation.date_effet"]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1930."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


def _periode(annee: int) -> dict:
    return next(p for p in PERIODES
                if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"]))


def _valeur(valeur):
    """Une valeur comparable : un barème, liste dans le YAML, en tuple."""
    return tuple(valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str) -> set:
    """Les valeurs que la période des marins porte pour ce champ, sur les
    années que la version couvre en entier ; ``None`` si elle n'en porte pas."""
    return {_valeur(_periode(annee).get(champ)) for annee in _annees_entieres(*_bornes(version))}


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Chaque fiche du lot couvre toute date d'effet ; chaque version commence
    le jour où entre en vigueur le texte qui la fait naître (`nee_de`), qu'elle
    cite parmi ses textes."""
    for nom in LOT:
        versions = _versions(nom)
        assert _bornes(versions[0])[0] is None and _bornes(versions[-1])[1] is None, nom
        for avant, apres in zip(versions, versions[1:]):
            assert _bornes(avant)[1] == _bornes(apres)[0], (nom, apres["id"])
        for version in versions:
            if version.get("nee_de"):
                texte = next((t for t in version.get("textes") or []
                              if t.get("id") == version["nee_de"]), None)
                assert texte is not None, (nom, version["id"])
                assert texte["en_vigueur"] == _bornes(version)[0], (nom, version["id"])


def test_la_periode_des_marins_porte_ce_que_chaque_version_lit():
    """Sur chaque année que la version couvre en entier, la période des marins
    porte la valeur que la version lit, sous le même nom, ou l'écart est
    déclaré."""
    declares = {(nom, version, champ) for nom, version, champ, _ in ECARTS_DECLARES}
    for nom in LOT:
        for version in _versions(nom):
            for champ, lu in (version["contenu"].get("parametres") or {}).items():
                if (nom, version["id"], champ) not in declares:
                    assert _portes(version, champ) == {_valeur(lu)}, (nom, version["id"], champ)


@pytest.mark.parametrize("nom, version, champ, article", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, article):
    """La version lit une valeur — rien, quand le droit n'a pas encore ce que
    le modèle sert — que la période des marins ne porte sur aucune des années
    qu'elle couvre ; une approximation de la fiche touche cette version et
    cite l'article qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = next(v for v in fiche["versions"] if v["id"] == version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    assert valeur not in _portes(lue, champ), (nom, version, champ)
    assert any(version in (a.get("version") or []) and article in str(a.get("textes") or "")
               for a in fiche.get("approximations") or []), (nom, version, article)


def _lignes(relatif: str) -> list[dict]:
    with (REFERENCE / relatif).open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(ligne for ligne in flux if not ligne.startswith("#")))


def test_le_traitement_de_l_indice_100_est_celui_que_fixe_l_article_7_du_decret_85_1148():
    """La série que le modèle lit, `legislation/indice_100_fonction_publique.csv`,
    est celle des rédactions de l'article 7 (`INDICE_100`), date pour date."""
    lignes = _lignes("legislation/indice_100_fonction_publique.csv")
    assert [(l["date_effet"], int(l["indice_majore"]), l["legi"]) for l in lignes] == INDICE_100
    assert {l["fiabilite"] for l in lignes} == {"haute"}


def _texte_legi(identifiant: str) -> str | None:
    base = RACINE_DONNEES / "brut" / "dila" / "legi.sqlite"
    if not base.exists():
        return None
    with sqlite3.connect(base) as connexion:
        ligne = connexion.execute("select texte from doc where id = ?", (identifiant,)).fetchone()
    return ligne[0] if ligne else None


@pytest.mark.parametrize("debut, indice, legi", INDICE_100)
def test_chaque_indice_se_relit_dans_sa_redaction_de_l_article_7(debut, indice, legi):
    """Le premier alinéa de chaque rédaction, dans l'index LEGI du dépôt quand il
    est là : il vise le traitement de l'indice 100, et le constitue de celui de
    l'indice majoré que la série porte."""
    texte = _texte_legi(legi)
    if texte is None:
        pytest.skip("l'index LEGI n'est pas récupéré (dila_index.py legi --recuperer)")
    alinea = texte[texte.index("Pour l'application"):]
    alinea = alinea[:alinea.index(".")]
    assert "se référant au traitement de l'indice 100" in alinea, legi
    assert alinea.endswith(f"constitué par le traitement afférent à l'indice majoré {indice}") \
        or f"l'indice majoré {indice} (indice brut 100)" in alinea, (legi, alinea)


def _indice_au(jour: str) -> int | None:
    connus = [indice for debut, indice, _ in INDICE_100 if debut <= jour]
    return connus[-1] if connus else None


def test_aucune_categorie_n_a_atteint_le_plafond_de_r_11_de_2008_a_2026():
    """R. 11, 3° : « Lorsque le salaire ainsi défini excède huit fois le montant
    du traitement brut correspondant à l'indice 100 dans la fonction publique,
    la portion dépassant cette limite n'est comptée que pour moitié. » Le
    traitement de l'indice 100 est celui de l'indice majoré 208 depuis le
    1er janvier 2024 (article 7 du décret n° 85-1148), au point de 59,0734 €
    (5 907,34 € pour cent points, article 3) : 208 × 59,0734 = 12 287,2672 €,
    et le plafond vaut huit fois plus, 98 298,1376 €. La vingtième catégorie de
    l'arrêté de 2026, 76 867,05 €, en reste loin ; et d'une année à l'autre,
    aucun forfait publié depuis 2008 n'atteint le plafond de son 1er janvier,
    le plus bas de l'année."""
    lus = _versions("marins_salaire_de_reference")[-1]["contenu"]["parametres"]
    points = {int(l["annee"]): float(l["valeur"])
              for l in _lignes("legislation/point_indice_fonction_publique.csv")}
    grilles: dict[int, dict[int, float]] = {}
    for ligne in _lignes("regimes/salaires_forfaitaires.csv"):
        if ligne["regime"] == "marins":
            grilles.setdefault(int(ligne["annee"]), {})[int(ligne["categorie"])] = float(
                ligne["montant_annuel"])
    plafond_2026 = lus["plafond_en_traitements_de_l_indice_100"] * _indice_au("2026-01-01") \
        * points[2026]
    assert round(plafond_2026, 4) == 98298.1376
    assert grilles[2026][20] == 76867.05
    assert sorted(grilles) == list(range(2008, 2027))
    for annee, grille in grilles.items():
        plafond = 8 * _indice_au(f"{annee}-01-01") * points[annee]
        assert max(grille.values()) < plafond, annee


def test_avant_le_5_novembre_1985_le_plafond_n_est_pas_lu_et_la_fiche_le_declare():
    """Les décrets de rémunération de 1968 à 1985 (n° 68-566, n° 70-393,
    n° 74-652 et leurs modifications) ne sont, dans les index du dépôt, qu'en
    analyses : la série s'ouvre sur la rédaction d'origine de l'article 7, au
    5 novembre 1985. Avant, le modèle n'abat pas, et une approximation de la
    fiche le déclare, pour les deux versions qui couvrent ces années."""
    assert INDICE_100[0][0] == "1985-11-05"
    fiche = carte.fiches()["marins_salaire_de_reference"]
    assert any({"loi_du_12_avril_1941", "code_de_1968"} <= set(a.get("version") or [])
               and "85-1148" in str(a.get("textes") or "")
               for a in fiche.get("approximations") or [])


# ---------------------------------------------------------------------------
# L'abattement dans le moteur
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def simulateur():
    from retraite_notionnelle.simulateur import Simulateur

    return Simulateur()


@pytest.mark.parametrize("annee, mois, attendu", [
    # 8 × 208 × 59,0734 : l'indice du 1er janvier 2024, le point de 2026.
    (2026, 1, 98298.1376),
    # 8 × 156 × 43,0973 : l'indice du 1er janvier 1990, le point de 1990.
    (1990, 1, 53785.4304),
    # 8 × 199 × 54,4113, puis 8 × 201 × 54,4113 : le décret n° 2008-622 change
    # l'indice au 1er juillet 2008, le point de l'année reste celui du 1er janvier.
    (2008, 6, 86622.7896),
    (2008, 7, 87493.3704),
    # 8 × 150 × 38,5544 : la rédaction d'origine, au 5 novembre 1985.
    (1985, 12, 46265.28),
    # Avant elle, rien n'est lu.
    (1985, 10, None),
])
def test_le_plafond_est_huit_fois_le_traitement_de_l_indice_100_a_la_date_d_effet(
        simulateur, annee, mois, attendu):
    from retraite_notionnelle.droit import liquider

    moteur = simulateur.scenario_actuel
    periode = moteur.catalogue["marins"].periode(annee)
    plafond = liquider.plafond_du_salaire_de_reference(moteur, periode, annee, mois)
    if attendu is None:
        assert plafond is None
    else:
        assert plafond == pytest.approx(attendu, abs=1e-6)
    # Le régime général n'a pas de tel plafond.
    general = moteur.catalogue["regime_general"].periode(annee)
    assert liquider.plafond_du_salaire_de_reference(moteur, general, annee, mois) is None


def test_la_portion_au_dela_du_plafond_ne_compte_que_pour_moitie():
    """100 000 € au plafond de 2026 : 98 298,1376 + (100 000 − 98 298,1376) / 2
    = 99 149,0688 € ; la vingtième catégorie de 2026, sous le plafond, reste
    entière."""
    from retraite_notionnelle.droit import liquider

    assert liquider.abattre_au_dela_du_plafond(100000.0, 98298.1376, 0.5) == pytest.approx(
        99149.0688, abs=1e-9)
    assert liquider.abattre_au_dela_du_plafond(76867.05, 98298.1376, 0.5) == 76867.05


def test_le_marin_qui_passe_le_plafond_liquide_un_salaire_abattu(simulateur):
    """Un marin né le 1er janvier 1990, à quatre fois le salaire moyen, part à
    cinquante-cinq ans et demi, le 1er juillet 2045 : vingtième catégorie. Son
    forfait, la grille de 2026 portée par le salaire moyen, passe le plafond, que
    le point, sans décret au-delà de 2027, garde à 98 298,1376 € : il liquide le
    plafond et la moitié de ce qui le dépasse, et le détail le dit."""
    from retraite_notionnelle.carriere import salaire_moyen_annuel

    carriere = simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="marin", age_debut=20,
        age_liquidation=55.5, niveau_salaire=4.0, profil_carriere="plat", jour_naissance=1)
    ligne = carriere.ligne(2045)
    forfait, categorie, _ = simulateur.scenario_actuel.grilles.forfait(
        "marins", 2045, ligne.revenu_annualise,
        lambda a: salaire_moyen_annuel(simulateur.macro, a))
    assert categorie == 20 and forfait > 98298.1376
    attendu = 98298.1376 + (forfait - 98298.1376) / 2
    pension = next(p for p in simulateur.scenario_actuel.calculer(carriere).pensions_par_regime
                   if p.regime == "marins")
    assert f"SR {attendu:,.2f} €" in pension.detail
    assert "compté pour moitié au-delà de 98,298.14 €" in pension.detail
