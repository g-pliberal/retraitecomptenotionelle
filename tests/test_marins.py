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
import math
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


#: Les mois où la série, qui suit la lettre de l'article 7, s'écarte du barème A
#: du décret n° 82-1105 que le dépôt tient (`grilles/bareme/indices.csv`) pour
#: l'indice brut 100 — mois : (série, barème). De décembre 1985 à février 1986,
#: le barème que le décret n° 86-166 remplace « à compter du 1er janvier 1985 »
#: donne déjà 152, quand l'article 7 dit 150 jusqu'au 7 février 1986 ; en mai et
#: juin 2001, le barème donne 169, quand le premier alinéa de l'article 7, que le
#: décret n° 2001-370 ne touche pas, dit encore 164.
ECARTS_AU_BAREME_A = {
    "1985-12-01": (150, 152), "1986-01-01": (150, 152), "1986-02-01": (150, 152),
    "2001-05-01": (164, 169), "2001-06-01": (164, 169),
}


def test_la_serie_ne_s_ecarte_du_bareme_a_que_la_ou_la_fiche_le_declare():
    """Au premier de chaque mois, de décembre 1985 à décembre 2026, l'indice de
    la série est celui que le barème A donne à l'indice brut 100, sauf aux mois
    de `ECARTS_AU_BAREME_A` ; et la fiche déclare ce choix de la lettre de
    l'article 7 contre le barème."""
    bareme = [(l["debut"], l["fin"] or "9999-12-31", int(l["indice_majore"]))
              for l in _lignes("grilles/bareme/indices.csv") if l["indice_brut"] == "100"]
    ecarts = {}
    for annee in range(1985, 2027):
        for mois in range(1, 13):
            jour = f"{annee}-{mois:02d}-01"
            if jour < "1985-12-01":
                continue
            lu = next(indice for debut, fin, indice in bareme if debut <= jour <= fin)
            if _indice_au(jour) != lu:
                ecarts[jour] = (_indice_au(jour), lu)
    assert ecarts == ECARTS_AU_BAREME_A
    fiche = carte.fiches()["marins_salaire_de_reference"]
    assert any("barème A" in str(a.get("ecart")) and "2001-370" in str(a.get("ecart"))
               for a in fiche.get("approximations") or [])


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


# ---------------------------------------------------------------------------
# La grille d'avant 2008, estimée : la limite que la fiche déclare
# ---------------------------------------------------------------------------

#: Les deux seuls montants réels de la grille d'avant 2008 que l'index JORF du
#: dépôt garde, chacun dans un rectificatif : l'année, la catégorie, le forfait
#: annuel en euros, l'identifiant. « Pour le salaire forfaitaire par mois de la
#: 13e catégorie, au lieu de: << 14 773,03 >>, lire: << 14 733,03 >> » (arrêté
#: du 31 janvier 1995, qui corrige celui du 29 décembre 1994, « pour compter du
#: 1er janvier 1995 ») : 14 733,03 × 12 = 176 796,36 F par an, au taux de
#: « 6,55957 F pour un euro » (paragraphe d'explication publié avec le décret
#: n° 2001-1203, après ses signatures). « en ce qui concerne la 10e
#: catégorie, au lieu de : « 25 243,53 », lire : « 25 243,83 » » (rectificatif de
#: l'arrêté du 2 janvier 2006, « pour compter du 1er janvier 2006 »).
GRILLE_REELLE_AVANT_2008 = [
    (1995, 13, 14733.03 * 12 / 6.55957, "JORFARTI000002373607"),
    (2006, 10, 25243.83, "JORFARTI000001490715"),
]
#: La grille du 1er janvier 1995 ne vaut que six mois : l'arrêté du 30 juin 1995
#: « portant majoration des salaires forfaitaires » les modifie « pour compter du
#: 1er juillet 1995, conformément au tableau ci-joint » (article 1er), tableau
#: que l'index ne porte pas (« Vous pouvez consulter le tableau dans le JO no 0164
#: du 16/07/95 Page 10596 ») ; l'arrêté du 30 décembre 1995, « pour compter du
#: 1er janvier 1996 » (article 1er).
GRILLES_DE_1995 = ("JORFARTI000001014013", "JORFARTI000001014119", "JORFARTI000001593286")
#: Le plafond de R. 11, 3° au 1er janvier 1995, au droit : l'indice majoré 158
#: de l'article 7 (depuis le 1er août 1991), au point de « 31 422 F » pour cent
#: points (article 3, LEGIARTI000006454440), huit fois : 397 174,08 F.
PLAFOND_DU_1ER_JANVIER_1995 = 8 * 158 * 314.22 / 6.55957
#: Le plafond du droit au second semestre 1995, jusqu'au 31 octobre : l'indice
#: majoré 158 (article 7, LEGIARTI000006454542), au point de « 31 799 F à compter
#: du 1er mars 1995 » (article 3, LEGIARTI000006454441), huit fois : 401 939,36 F.
PLAFOND_DU_1ER_JUILLET_1995 = 8 * 158 * 317.99 / 6.55957
#: Le point de cent indices majorés que l'article 3 du décret n° 85-1148 « est
#: fixée à » le 1er janvier de chaque année de 1986 à 2007, et le 1er décembre
#: 1985 : jour : (ce que la rédaction en vigueur ce jour-là écrit, rédaction). En
#: 1994, l'alinéa suivant fixe 31 018 F « pour les agents dont l'indice majoré est
#: inférieur ou égal à 275 » : le texte ne dit pas lequel des deux fait le
#: traitement de l'indice 100 ; le test prend 30 926 F, le plus bas, qui ne peut
#: que relever le rapport du forfait au plafond.
POINT_DE_L_ARTICLE_3 = {
    "1985-12-01": ("26428 F", "LEGIARTI000006454423"),
    "1986-01-01": ("26428 F", "LEGIARTI000006454423"),
    "1987-01-01": ("26428 F", "LEGIARTI000006454423"),
    "1988-01-01": ("26 719 F", "LEGIARTI000006454426"),
    "1989-01-01": ("27 523 F à compter du 1er septembre 1988", "LEGIARTI000006454428"),
    "1990-01-01": ("28 270 F à compter du 1er janvier 1990", "LEGIARTI000006454431"),
    "1991-01-01": ("28 973 F à compter du 1er décembre 1990", "LEGIARTI000006454433"),
    "1992-01-01": ("29 408 F à compter du 1er novembre 1991", "LEGIARTI000006454434"),
    "1993-01-01": ("30 190 F à compter du 1er octobre 1992", "LEGIARTI000006454436"),
    "1994-01-01": ("30 926 F à compter du 1er janvier 1994", "LEGIARTI000006454438"),
    "1995-01-01": ("31 422 F à compter du 1er décembre 1994", "LEGIARTI000006454440"),
    "1996-01-01": ("32 244 F à compter du 1er novembre 1995", "LEGIARTI000006454442"),
    "1997-01-01": ("32 244 F à compter du 1er novembre 1995", "LEGIARTI000006454442"),
    "1998-01-01": ("32 567 F à compter du 1er octobre 1997", "LEGIARTI000006454444"),
    "1999-01-01": ("32 990 F à compter du 1er novembre 1998", "LEGIARTI000006454446"),
    "2000-01-01": ("33 419 F à compter du 1er décembre 1999", "LEGIARTI000006454448"),
    "2001-01-01": ("33 586 F à compter du 1er décembre 2000", "LEGIARTI000006454449"),
    "2002-01-01": ("5 181,75 Euros à compter du 1er janvier 2002", "LEGIARTI000006454452"),
    "2003-01-01": ("5 249,33 Euros à compter du 1er décembre 2002", "LEGIARTI000006454454"),
    "2004-01-01": ("5 275,58 Euros à compter du 1er janvier 2004", "LEGIARTI000006454455"),
    "2005-01-01": ("5 275,58 Euros à compter du 1er janvier 2004", "LEGIARTI000006454455"),
    "2006-01-01": ("5 371,10 Euros à compter du 1er novembre 2005", "LEGIARTI000006454458"),
    "2007-01-01": ("5 397,95 Euros à compter du 1er juillet 2006", "LEGIARTI000006454459"),
}


def _plafond_du_texte(jour: str) -> float:
    """Huit fois (R. 11, 3°) le traitement de l'indice majoré que l'article 7 fait
    correspondre à l'indice 100 ce jour-là (`INDICE_100`), au point de l'article 3
    (`POINT_DE_L_ARTICLE_3`) : cent points, en francs jusqu'en 2001, au taux de
    6,55957 F pour un euro."""
    ecrit, _ = POINT_DE_L_ARTICLE_3[jour]
    montant, unite = ecrit.split(" à compter")[0].rsplit(" ", 1)
    cent_points = float(montant.replace(" ", "").replace(",", "."))
    return 8 * _indice_au(jour) * cent_points / 100 / (6.55957 if unite == "F" else 1)


@pytest.mark.parametrize("jour", POINT_DE_L_ARTICLE_3)
def test_chaque_point_se_relit_dans_sa_redaction_de_l_article_3(jour):
    """Dans l'index LEGI du dépôt quand il est là : la rédaction de l'article 3
    est celle du décret n° 85-1148, en vigueur ce jour-là, et fixe le point de
    cent indices à ce que `POINT_DE_L_ARTICLE_3` en écrit."""
    ecrit, legi = POINT_DE_L_ARTICLE_3[jour]
    base = RACINE_DONNEES / "brut" / "dila" / "legi.sqlite"
    if not base.exists():
        pytest.skip("l'index LEGI n'est pas récupéré (dila_index.py legi --recuperer)")
    with sqlite3.connect(base) as connexion:
        debut, fin, num, titre, texte = connexion.execute(
            "select date, fin, num, titre, texte from doc where id = ?", (legi,)).fetchone()
    assert num == "3" and "85-1148" in titre, legi
    assert debut <= jour < (fin or "9999-12-31"), (legi, debut, fin)
    assert "afférents à l'indice 100 majoré" in texte
    assert f"est fixée à {ecrit}" in texte or f"puis à {ecrit}" in texte, legi


def _euros(montant: float) -> str:
    return f"{montant:,.2f}".replace(",", " ").replace(".", ",")


def _dixiemes(valeur: float, vers_le_haut: bool = False) -> str:
    arrondi = math.ceil(valeur * 10) / 10 if vers_le_haut else round(valeur, 1)
    return f"{arrondi:.1f}".replace(".", ",")


def _forfait_estime(simulateur, annee: int, categorie: int) -> float:
    """Le forfait d'une catégorie une année que la grille ne publie pas : celui de
    2008, lu, ramené par le salaire moyen, tel que le moteur le range."""
    from retraite_notionnelle.carriere import salaire_moyen_annuel
    from retraite_notionnelle.donnees.chargement import Fiabilite

    moyen = lambda a: salaire_moyen_annuel(simulateur.macro, a)  # noqa: E731
    de_2008 = next(float(l["montant_annuel"])
                   for l in _lignes("regimes/salaires_forfaitaires.csv")
                   if l["regime"] == "marins" and l["annee"] == "2008"
                   and int(l["categorie"]) == categorie)
    estime = de_2008 * moyen(annee) / moyen(2008)
    forfait, rangee, fiabilite = simulateur.scenario_actuel.grilles.forfait(
        "marins", annee, estime, moyen)
    assert rangee == categorie and forfait == pytest.approx(estime, rel=1e-12)
    assert fiabilite == Fiabilite.ESTIMEE
    return forfait


def _limite_de_la_grille() -> str:
    fiche = carte.fiches()["marins_salaire_de_reference"]
    limite = next(a for a in fiche["approximations"] if "arrêtés annuels" in str(a["textes"]))
    return limite["ecart"] + " " + limite["effet"]


def _ecart_de_1995(simulateur) -> float:
    annee, categorie, reel, _ = GRILLE_REELLE_AVANT_2008[0]
    return reel / _forfait_estime(simulateur, annee, categorie)


def test_la_grille_d_avant_2008_est_sous_les_deux_montants_reels_et_la_fiche_le_dit(
        simulateur):
    """Avant 2008, la grille du modèle est celle de 2008 ramenée par le salaire
    moyen. Les deux montants réels que l'index garde la dépassent : 26 952,43 €
    pour la 13e catégorie du 1er janvier 1995, 25 243,83 € pour la 10e du
    1er janvier 2006. La fiche déclare la limite : les deux rectificatifs, les
    forfaits que le modèle prend, les écarts, et ce qu'ils font de la vingtième
    de 1995 — 48 735,45 € à la structure de 2008, 80,5 % du plafond du jour.
    Ces chiffres de 1995 ne valent que du 1er janvier au 30 juin : la grille du
    1er juillet, majorée, n'est pas lue, et la fiche le dit, avec ce que la
    majoration devrait atteindre pour que la vingtième passe le plafond du droit
    du second semestre ; et le taux du franc, d'un paragraphe d'explication."""
    dit = _limite_de_la_grille()
    assert "26 952,43 €" in dit and "176 796,36 F" in dit and "2e sous-colonne" in dit
    assert "paragraphe d'explication" in dit and "JORFTEXT000000580421" in dit
    assert "du 1er janvier au 30 juin 1995" in dit
    assert "pour compter du 1er juillet 1995" in dit and "pour compter du 1er janvier 1996" in dit
    assert all(identifiant in dit for identifiant in GRILLES_DE_1995)
    for annee, categorie, reel, identifiant in GRILLE_REELLE_AVANT_2008:
        modele = _forfait_estime(simulateur, annee, categorie)
        assert modele < reel, annee
        assert identifiant in dit and f"le modèle prend {_euros(modele)} €" in dit, annee
        assert f"{_dixiemes(100 * (reel / modele - 1))} % plus haut" in dit, annee
        assert f"de {_dixiemes(100 * (1 - modele / reel))} %" in dit, annee
    vingtieme_1995 = _forfait_estime(simulateur, 1995, 20)
    structure = {annee: _grille(annee)[20] / _grille(annee)[13] for annee in (2008, 2026)}
    assert round(structure[2008], 4) == round(structure[2026], 4)
    estimee = GRILLE_REELLE_AVANT_2008[0][2] * structure[2008]
    assert f"vaut {structure[2008]:.4f} fois la treizième".replace(".", ",") in dit
    assert f"le modèle prend {_euros(vingtieme_1995)} € en 1995" in dit
    assert f"vaudrait {_euros(estimee)} €" in dit
    assert f"à {_dixiemes(100 * estimee / PLAFOND_DU_1ER_JANVIER_1995)} % de celui du 1er janvier 1995" in dit
    assert f"{_euros(PLAFOND_DU_1ER_JANVIER_1995)} €" in dit
    assert f"{_euros(PLAFOND_DU_1ER_JUILLET_1995)} €" in dit
    assert f"la relevait de plus de {_dixiemes(100 * (PLAFOND_DU_1ER_JUILLET_1995 / estimee - 1))} %" in dit


def _grille(annee: int) -> dict[int, float]:
    return {int(l["categorie"]): float(l["montant_annuel"])
            for l in _lignes("regimes/salaires_forfaitaires.csv")
            if l["regime"] == "marins" and int(l["annee"]) == annee}


def test_de_1985_a_2007_la_vingtieme_estimee_reste_sous_le_plafond_meme_relevee(simulateur):
    """De 1985 à 2007, aucune grille n'est lue : que la vingtième catégorie reste
    sous le plafond de R. 11, 3° n'est qu'une estimation. Le plafond se pose
    depuis le texte, au 1er janvier (au 1er décembre en 1985) : huit fois le
    traitement de l'indice majoré de l'article 7, au point de l'article 3
    (`_plafond_du_texte`). Le rapport de la vingtième de la grille du modèle à ce
    plafond culmine en 2005 ; relevée de l'écart du 1er janvier 1995, le plus
    grand des deux montants réels, elle reste sous le plafond. La fiche écrit
    ces deux rapports."""
    rapports = {int(jour[:4]): _forfait_estime(simulateur, int(jour[:4]), 20)
                / _plafond_du_texte(jour) for jour in POINT_DE_L_ARTICLE_3}
    assert sorted(rapports) == list(range(1985, 2008))
    culmine = max(rapports, key=rapports.get)
    ecart = _ecart_de_1995(simulateur)
    assert culmine == 2005 and ecart > 1 and rapports[culmine] * ecart < 1
    point = next(a for a in carte.fiches()["marins_salaire_de_reference"]["approximations"]
                 if "articles 3 et 5" in str(a["textes"]))["effet"]
    assert f"au plus {_dixiemes(100 * rapports[culmine])} % du plafond ({culmine})" in point
    assert (f"sous {_dixiemes(100 * rapports[culmine] * ecart, True)} % du plafond de 1985 à "
            f"2007 ({culmine})") in _limite_de_la_grille()


def test_avant_1985_les_seuils_de_l_indice_100_montent_sous_la_grille_relevee(simulateur):
    """De 1968 à 1984, la vingtième catégorie de la grille du modèle ne passe huit
    fois le traitement de l'indice 100 que s'il était celui d'un indice majoré
    plus bas qu'un seuil : 76,5 en 1968, 102,8 en 1980, le plus haut ; relevés de
    l'écart de 1995, 87,6 et 117,7. La fiche les écrit."""
    points = {int(l["annee"]): float(l["valeur"])
              for l in _lignes("legislation/point_indice_fonction_publique.csv")}
    seuils = {annee: _forfait_estime(simulateur, annee, 20) / (8 * points[annee])
              for annee in range(1968, 1985)}
    plus_haut = max(seuils, key=seuils.get)
    ecart = _ecart_de_1995(simulateur)
    assert plus_haut == 1980
    avant = next(a for a in carte.fiches()["marins_salaire_de_reference"]["approximations"]
                 if "depuis le 5 novembre 1985" in str(a["textes"]))["effet"]
    assert f"{_dixiemes(seuils[1968])} en 1968, à {_dixiemes(seuils[1980])} en 1980" in avant
    assert (f"monteraient de {_dixiemes(seuils[1968])} et {_dixiemes(seuils[1980])} à "
            f"{_dixiemes(seuils[1968] * ecart)} et {_dixiemes(seuils[1980] * ecart)}") \
        in _limite_de_la_grille()
