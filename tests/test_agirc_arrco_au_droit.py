"""L'Agirc-Arrco, lue au droit.

Deux fiches de la carte, lues au droit le 3 novembre 2026 (action 130). La
première, la majoration pour enfants nés ou élevés de l'Arrco et de l'Agirc, puis du régime
unifié (`majoration_enfants_agirc_arrco`), dans l'accord du 25 avril 1996
relatif aux régimes de l'Arrco (articles 2 et 11), l'accord du 18 mars 2011
(article 7), l'article 17 de l'annexe A de l'accord du 8 décembre 1961 et
l'article 6 bis de l'annexe I de la convention du 14 mars 1947, dans leur
rédaction de 2012, et l'article 94 de l'accord national interprofessionnel du
17 novembre 2017.

Le taux d'un point tient à la période où il a été acquis et au régime qui l'a
inscrit, tels que l'accord en vigueur à la date d'effet de la pension les
range ; le plafond, à cette date seule. Les versions se coupent donc sur les
deux dates : la date d'effet (`liquidation.date_effet`) choisit l'accord, et
son plafond ; la période (`periode.debut`), le taux. Chaque paramètre porte le
nom de ce qui le porte au dépôt : le barème, la colonne `bareme` de
`legislation/majoration_enfants_points.csv`, lue sur les années d'acquisition
que la version couvre en entier, avant sa date d'effet ; le plafond, les
champs des périodes de chaque régime, lus aux années de liquidation qu'elle
couvre ; ce que le portage tranche lui-même, dans
`moteur/js/droit/completer.js`. Ce que le modèle fait autrement, la fiche le
déclare, et le test qui suit `ECARTS_DECLARES` le tient.

La seconde, les coefficients d'anticipation de l'Agirc et de l'Arrco, puis du
régime unifié (`coefficients_anticipation_agirc_arrco`), dont le moteur lit les
versions à la date d'effet de la pension : ce qui exonère, et rien d'autre.
Ses versions se coupent aux jours où un texte change la règle, du protocole du
14 juin 1976 à l'avenant n° 15 du 16 mars 2023 ; la coupe ne change pas ce que
le moteur lit. Les deux tables des textes, celle des âges et celle des
trimestres manquants, sont l'escalier du portage (`moteur/js/droit/liquider.js`),
et l'âge que la caisse a servi de 2011 à 2018, celui des données.
"""

from __future__ import annotations

import csv
import functools
import json
import re
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

MAJORATION = "majoration_enfants_agirc_arrco"
ANTICIPATION = "coefficients_anticipation_agirc_arrco"
LOT = (MAJORATION, ANTICIPATION)
REFERENCE = RACINE_DONNEES / "reference"
PORTAGE = Path(__file__).resolve().parents[1] / "moteur" / "js" / "droit" / "completer.js"
#: La création de l'Agirc, et la dernière année que les confrontations
#: parcourent.
DEBUT, HORIZON = 1947, 2050
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")
#: Les dates qui décident, fiche par fiche.
DATES = {MAJORATION: {"liquidation.date_effet", "periode.debut"},
         ANTICIPATION: {"liquidation.date_effet"}}

#: Les paramètres que le moteur lit dans la période de la date d'effet ; le
#: barème, lui, se lit à l'année d'acquisition de chaque point.
A_LA_LIQUIDATION = {"plafond_majoration_enfants", "plafond_majoration_annee"}
#: Ce que le portage tranche lui-même : le motif qui le lit dans
#: `completer.js`, et ce qu'il en fait. Le plafond ne s'oppose qu'aux
#: générations que le portage retient, d'une année de naissance entière.
DU_PORTAGE = {
    "plafond_nes_a_compter_du": (r"carriere\.annee_naissance < (\d{4})",
                                 lambda annee: date(int(annee), 1, 1)),
}
#: La date d'effet à compter de laquelle le portage oppose un plafond.
PREMIER_PLAFOND = r"const PREMIER_PLAFOND_MAJORATION = new DateMois\((\d{4}), (\d{1,2})\);"

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ qu'elle lit et que le dépôt porte autrement, et ce que cite
#: l'approximation qui le déclare.
PLAFONNEES = ("accord_de_2011_points_d_avant_1999", "accord_de_2011_points_de_1999_a_2011",
              "accord_de_2011_points_depuis_2012", "regime_unifie_points_d_avant_1999",
              "regime_unifie_points_de_1999_a_2011", "regime_unifie_points_depuis_2012")
ECARTS_DECLARES = [(MAJORATION, version, "plafond_nes_a_compter_du", "2 août 1951")
                   for version in PLAFONNEES]


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _version(nom: str, identifiant: str) -> dict:
    return next(v for v in _versions(nom) if v["id"] == identifiant)


def _bornes(version: dict, nom: str) -> list:
    return version["bornes"].get(nom) or [None, None]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1947."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


def _annees_d_acquisition(version: dict) -> range:
    """Les années d'acquisition que la version couvre en entier, avant la fin
    de ses dates d'effet : un point s'acquiert avant la pension qui le sert."""
    annees = _annees_entieres(*_bornes(version, "periode.debut"))
    fin = _bornes(version, "liquidation.date_effet")[1]
    return range(annees.start, min(annees.stop, HORIZON + 1 if fin is None else fin.year))


@functools.cache
def _lignes_du_bareme() -> tuple[tuple[frozenset, int, int, tuple], ...]:
    chemin = REFERENCE / "legislation" / "majoration_enfants_points.csv"
    with chemin.open(encoding="utf-8", newline="") as flux:
        lignes = csv.DictReader(ligne for ligne in flux if not ligne.startswith("#"))
        return tuple((frozenset(ligne["regimes"].split()), int(ligne["acquis_debut"]),
                      int(ligne["acquis_fin"]), tuple(float(t) for t in ligne["bareme"].split()))
                     for ligne in lignes)


def _bareme_porte(code: str, annee: int) -> set:
    """Les barèmes que la table porte pour les points que le régime inscrit
    cette année ; rien hors d'elle."""
    return {bareme for regimes, debut, fin, bareme in _lignes_du_bareme()
            if code in regimes and debut <= annee <= fin}


@functools.cache
def _periodes_du_regime(code: str) -> tuple[dict, ...]:
    return tuple(yaml.safe_load((REFERENCE / "regimes" / f"{code}.yaml")
                                .read_text(encoding="utf-8"))["periodes"])


def _periodes(code: str, annee: int) -> list[dict]:
    """Les périodes du régime qui couvrent l'année ; rien hors d'elles."""
    return [p for p in _periodes_du_regime(code)
            if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"])]


@functools.cache
def _valeurs_du_point() -> dict[tuple[str, int], float]:
    chemin = REFERENCE / "regimes" / "valeurs_point.csv"
    with chemin.open(encoding="utf-8", newline="") as flux:
        lignes = csv.DictReader(ligne for ligne in flux if not ligne.startswith("#"))
        return {(ligne["regime"], int(ligne["annee"])): float(ligne["valeur"])
                for ligne in lignes if ligne["mesure"] == "valeur_service"}


def _point(code: str, annee: int) -> float:
    return _valeurs_du_point()[code, annee]


def _du_portage(champ: str):
    motif, lire = DU_PORTAGE[champ]
    trouve = re.search(motif, PORTAGE.read_text(encoding="utf-8"))
    assert trouve, (champ, motif)
    return lire(*trouve.groups())


def _valeur(valeur):
    """Une valeur comparable : une liste du YAML, en tuple ; une date, telle."""
    return tuple(_valeur(v) for v in valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str, code: str) -> set:
    """Ce que le dépôt porte pour ce champ, sur les années de liquidation que
    la version couvre en entier ; ce que le portage en tranche ; rien si elle
    n'en couvre aucune."""
    if champ in DU_PORTAGE:
        return {_du_portage(champ)}
    annees = _annees_entieres(*_bornes(version, "liquidation.date_effet"))
    return {_valeur(periode.get(champ)) for annee in annees for periode in _periodes(code, annee)}


def _declare(nom: str, version: str, champ: str) -> bool:
    return any((n, v, c) == (nom, version, champ) for n, v, c, _ in ECARTS_DECLARES)


def _en_toutes_lettres(jour: date) -> str:
    return f"{'1er' if jour.day == 1 else jour.day} {MOIS[jour.month - 1]} {jour.year}"


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Les versions se coupent sur les dates qui décident de la fiche ; chaque
    version commence le jour où entre en vigueur le texte qui la fait naître
    (`nee_de`), qu'elle cite parmi ses textes, ou le jour que ce texte nomme."""
    for nom in LOT:
        assert set(carte.fiches()[nom]["dates_qui_decident"]) == DATES[nom], nom
        for version in _versions(nom):
            assert set(version["bornes"]) <= DATES[nom], (nom, version["id"])
            if not version.get("nee_de"):
                continue
            texte = next((t for t in version.get("textes") or []
                          if t.get("id") == version["nee_de"]), None)
            assert texte is not None, (nom, version["id"])
            debut = max(d for d, _ in version["bornes"].values() if d is not None)
            citation = " ".join(str(texte.get("citation") or "").replace("1 er", "1er").split())
            assert (texte["en_vigueur"] == debut
                    or f"du {_en_toutes_lettres(debut)}" in citation
                    or f"jusqu'au {_en_toutes_lettres(debut - timedelta(days=1))}" in citation
                    ), (nom, version["id"])


def test_le_bareme_de_chaque_version_est_celui_des_points():
    """Chaque ligne du barème d'une version — des régimes, et le taux pour 0 à
    7 enfants et plus — est celle que la table du moteur porte pour les points
    que ces régimes inscrivent, chaque année d'acquisition que la version
    couvre ; et aucun régime de la fiche dont la table porte ces points n'y
    manque."""
    regimes = carte.fiches()[MAJORATION]["regimes"]
    for version in _versions(MAJORATION):
        lignes = version["contenu"]["parametres"]["bareme"]
        lus = {code: tuple(ligne["taux"]) for ligne in lignes for code in ligne["regimes"]}
        assert sum(len(ligne["regimes"]) for ligne in lignes) == len(lus), version["id"]
        annees = _annees_d_acquisition(version)
        assert annees, version["id"]
        for code in regimes:
            portes = set().union(*(_bareme_porte(code, annee) for annee in annees))
            assert portes == ({lus[code]} if code in lus else set()), (version["id"], code, portes)


def test_les_periodes_portent_le_plafond_que_chaque_version_lit():
    """Sur chaque année de liquidation que la version couvre en entier, les
    périodes de ses régimes portent le plafond qu'elle lit, sous le même nom,
    ou le portage le tranche ; sinon, l'écart est déclaré."""
    fiche = carte.fiches()[MAJORATION]
    for version in _versions(MAJORATION):
        parametres = version["contenu"]["parametres"]
        for champ, lu in parametres.items():
            if champ == "bareme":
                continue
            assert champ in A_LA_LIQUIDATION | set(DU_PORTAGE), (version["id"], champ)
            for code in [None] if champ in DU_PORTAGE else fiche["regimes"]:
                portes = _portes(version, champ, code)
                if portes and not _declare(MAJORATION, version["id"], champ):
                    assert portes == {_valeur(lu)}, (version["id"], champ, code, portes)


def test_aucun_plafond_avant_le_1er_janvier_2012():
    """Le portage n'oppose de plafond qu'aux pensions qui prennent effet à
    compter du jour où la première version plafonnée commence ; aucune version
    qui finit avant ne lit de plafond."""
    annee, mois = re.search(PREMIER_PLAFOND, PORTAGE.read_text(encoding="utf-8")).groups()
    premier = date(int(annee), int(mois), 1)
    plafonnees = [v for v in _versions(MAJORATION)
                  if "plafond_majoration_enfants" in v["contenu"]["parametres"]]
    assert sorted(v["id"] for v in plafonnees) == sorted(PLAFONNEES)
    assert min(_bornes(v, "liquidation.date_effet")[0] for v in plafonnees) == premier
    for version in _versions(MAJORATION):
        if version not in plafonnees:
            assert _bornes(version, "liquidation.date_effet")[1] <= premier, version["id"]


@pytest.mark.parametrize("nom, version, champ, cite", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, cite):
    """La version lit une valeur que le dépôt ne porte pas ; une approximation
    de la fiche touche cette version et cite le texte qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = _version(nom, version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    codes = [None] if champ in DU_PORTAGE else fiche["regimes"]
    portes = set().union(*(_portes(lue, champ, code) for code in codes))
    assert portes and valeur not in portes, (nom, version, champ)
    assert any(version in (a.get("version") or []) and cite in str(a.get("ecart") or "")
               for a in fiche.get("approximations") or []), (nom, version, cite)


def test_le_plafond_de_novembre_2016_est_celui_du_guide():
    """« Au 1er novembre 2016, le plafonnement annuel est fixé à 1 031,15 €
    pour le régime Arrco et à 1 028,12 € pour le régime Agirc » (guide n° 9
    de l'Agirc-Arrco, mars 2017) : les 1 000 euros des allocations de 2012,
    au point de 2011, revalorisés comme le point de chacun. La caisse arrondit
    le plafond au centime d'année en année, le modèle d'un coup : un centime
    d'écart au plus, que la fiche déclare."""
    version = _version(MAJORATION, "accord_de_2011_points_depuis_2012")
    plafond = version["contenu"]["parametres"]["plafond_majoration_enfants"]
    annee = version["contenu"]["parametres"]["plafond_majoration_annee"]
    for code, publie in (("arrco", 1031.15), ("agirc", 1028.12)):
        assert abs(plafond * _point(code, 2016) / _point(code, annee) - publie) <= 0.01, code
    assert any("centime" in str(a.get("ecart"))
               for a in carte.fiches()[MAJORATION]["approximations"])


def test_le_plafond_du_regime_unifie_est_le_cumul_des_deux_plafonds():
    """« La majoration pour enfants nés ou élevés est plafonnée au montant du
    cumul des plafonds en vigueur à l'Agirc et à l'Arrco applicables à
    l'entrée en vigueur du présent accord. Ce montant est revalorisé en
    fonction de l'évolution de la valeur du point » (accord du 17 novembre
    2017, article 94) : les deux plafonds de 2018, 2 071,58 euros ensemble,
    revalorisés du point de l'Arrco du 1er janvier 2019 à celui de 2025, font
    les 2 367,48 euros que porte la version, à un centime près."""
    cumul = sum(1000 * _point(code, 2018) / _point(code, 2011) for code in ("agirc", "arrco"))
    assert round(cumul, 2) == 2071.58
    version = _version(MAJORATION, "regime_unifie_points_depuis_2012")
    plafond = version["contenu"]["parametres"]["plafond_majoration_enfants"]
    annee = version["contenu"]["parametres"]["plafond_majoration_annee"]
    assert abs(plafond * _point("arrco", 2018) / _point("agirc_arrco", annee) - cumul) <= 0.01


def _taux(code: str, annee: int, enfants: int) -> float:
    bareme, = _bareme_porte(code, annee)
    return bareme[min(enfants, len(bareme) - 1)]


def test_les_exemples_du_guide_de_2017_tombent_sur_le_bareme():
    """Le guide n° 9 de l'Agirc-Arrco (mars 2017), trois enfants, retraite au
    1er avril 2017. À l'Arrco, au point de 1,2513 euro : 786,04 points de 2012
    à 2017 à 10 %, 1 827,50 de 1999 à 2011 à 5 %, 1 002,23 de 1972 à 1987
    d'une caisse qui majorait de 10 %, 2 000 de 1988 à 1998 d'une caisse qui
    ne majorait pas : 338,11 euros. La table du moteur, qui présume toutes les
    caisses d'avant 1999 au barème de l'accord, en compterait 250,26 de plus —
    l'effet que l'approximation déclare. À l'Agirc, au point de 0,4352 euro :
    10 000 points de 2012 à 2017 à 10 %, 25 000 de 1980 à 2011 à 8 % font
    1 305,60 euros, ramenés au plafond de 1 028,12."""
    point = 1.2513
    lignes = ((786.04, _taux("arrco", 2012, 3)), (1827.50, _taux("arrco", 1999, 3)),
              (1002.23, 0.10), (2000, 0))
    assert round(sum(round(points * point * taux, 2) for points, taux in lignes), 2) == 338.11
    presume = point * 2000 * _taux("arrco", 1988, 3)
    assert round(presume, 2) == 250.26
    assert any("250,26" in str(a.get("effet"))
               for a in carte.fiches()[MAJORATION]["approximations"])
    agirc = 0.4352 * (10000 * _taux("agirc", 2012, 3) + 25000 * _taux("agirc", 1980, 3))
    assert round(agirc, 2) == 1305.60
    plafond = 1000 * _point("agirc", 2016) / _point("agirc", 2011)
    assert round(min(agirc, plafond), 2) in (1028.11, 1028.12)


# -- les coefficients d'anticipation -------------------------------------------

LIQUIDER = Path(__file__).resolve().parents[1] / "moteur" / "js" / "droit" / "liquider.js"
#: Les jours où un texte change la règle, tels que chacun l'écrit : les
#: versions de la fiche se coupent là, et nulle part ailleurs.
COUPES_DE_L_ANTICIPATION = (
    date(1976, 7, 1),   # protocole du 14 juin 1976 : « à partir du 1er juillet 1976 »
    date(1983, 4, 1),   # arrêté du 21 mars 1983 : « APPLICATION A COMPTER DU 01-04-1983 »
    date(1997, 1, 1),   # accord du 23 décembre 1996, article 1er : « à effet du 1er janvier 1997 »
    date(1999, 1, 1),   # accord Arrco du 25 avril 1996, article 10 : « à compter du 1er janvier 1999 »
    date(2004, 1, 1),   # accord du 13 novembre 2003, article 15 : « du 1er janvier 2004 »
    date(2011, 7, 1),   # accord du 18 mars 2011, article 1er : « à compter du 1er juillet 2011 »
    date(2016, 1, 1),   # accord du 30 octobre 2015, article 3 : « à compter du 1er janvier 2016 »
    date(2019, 1, 1),   # accord du 17 novembre 2017 : « applicable au 1er janvier 2019 »
    date(2023, 3, 16),  # avenant n° 15 : « entre en vigueur à la date de sa signature »
)
#: La table de l'article 84, 2, de l'accord du 17 novembre 2017, de « moins 10
#: ans » à « moins 1 trimestre » ; l'article 6 de l'annexe I de la convention
#: de 1947 et l'article 18 de l'annexe A de l'accord de 1961, mis à jour au
#: 1er janvier 2018, écrivent la même.
TABLE_DES_AGES = (
    0.43, 0.4475, 0.465, 0.4825, 0.5, 0.5175, 0.535, 0.5525, 0.57, 0.5875,
    0.605, 0.6225, 0.64, 0.6575, 0.675, 0.6925, 0.71, 0.7275, 0.745, 0.7625,
    0.78, 0.7925, 0.805, 0.8175, 0.83, 0.8425, 0.855, 0.8675, 0.88, 0.89,
    0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99)
#: La table de l'article 85, 3, du même accord, de vingt trimestres manquants
#: à un.
TABLE_DES_TRIMESTRES_MANQUANTS = (
    0.78, 0.7925, 0.805, 0.8175, 0.83, 0.8425, 0.855, 0.8675, 0.88, 0.89,
    0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99)
#: L'âge de la retraite que la caisse servait de 2011 à 2018, génération par
#: génération (sa table créée le 27 décembre 2018) : « 65 ans » avant le
#: 1er juillet 1951, puis « 65 ans 4 mois », « 65 ans 9 mois », « 66 ans 2
#: mois », « 66 ans 7 mois » et « 67 ans » ; en années et en mois.
AGES_DE_LA_CAISSE_EN_2018 = {1951: (65, 0), 1951.5: (65, 4), 1952: (65, 9), 1953: (66, 2),
                             1954: (66, 7), 1955: (67, 0)}
#: Ce que le modèle fait autrement que le droit, chaque fois déclaré : une
#: version que l'approximation touche, et un mot de ce qu'elle dit.
ECARTS_DE_L_ANTICIPATION = (
    ("structure_financiere_de_1996", "salariés en activité"),
    ("accord_du_18_mars_2011", "mères de famille"),
    ("regime_unifie", "mineurs"),
    ("regime_unifie", "report"),
)


def _constante_du_portage(nom: str):
    """Une constante de `liquider.js`, sa valeur littérale."""
    trouve = re.search(rf"^const {nom} = (.+);$", LIQUIDER.read_text(encoding="utf-8"), re.M)
    assert trouve, f"le portage ne définit plus {nom}"
    return json.loads(trouve.group(1))


def _escalier(trimestres: int) -> float:
    """Le coefficient du portage pour tant de trimestres, lu dans ses paliers
    (`coefficientAnticipation`)."""
    coefficient, precedent = 1.0, 0
    for borne, pas in _constante_du_portage("PALIERS_ANTICIPATION"):
        coefficient -= max(0, min(trimestres, borne) - precedent) * pas
        precedent = borne
    return round(coefficient, 6)


def _accord_arrco_de_1996(trimestres: int) -> float:
    """L'article 10 de l'accord Arrco du 25 avril 1996, à tant de trimestres
    avant soixante-cinq ans : 0,43 à cinquante-cinq ans, « majoré de 0,0175
    par trimestre écoulé » jusqu'à soixante, de 0,0125 jusqu'à soixante-deux,
    de 0,01 jusqu'à soixante-cinq."""
    ecoules = 40 - trimestres
    coefficient = 0.43 + 0.0175 * min(ecoules, 20) + 0.0125 * min(max(ecoules - 20, 0), 8)
    return round(coefficient + 0.01 * max(ecoules - 28, 0), 6)


def test_les_versions_de_l_anticipation_se_coupent_aux_jours_des_textes():
    """Les versions se suivent sans trou ni chevauchement, de la première
    pension à aujourd'hui, et ne changent qu'aux jours où un texte change la
    règle ; aucun texte ne reste à rattacher."""
    fiche = carte.fiches()[ANTICIPATION]
    bornes = sorted((_bornes(v, "liquidation.date_effet") for v in fiche["versions"]),
                    key=lambda borne: borne[0] or date.min)
    assert [debut for debut, _ in bornes] == [None, *COUPES_DE_L_ANTICIPATION]
    assert [fin for _, fin in bornes] == [*COUPES_DE_L_ANTICIPATION, None]
    assert not fiche.get("textes_a_rattacher")


def test_la_coupe_ne_change_pas_ce_que_le_moteur_lit():
    """Depuis le 1er avril 1983, chaque version porte ce que la structure
    financière portait : la coupe est une lecture, aucun chiffre du modèle ne
    bouge."""
    versions = [v for v in _versions(ANTICIPATION)
                if (_bornes(v, "liquidation.date_effet")[0] or date.min) >= date(1983, 4, 1)]
    lus = {json.dumps(v["contenu"]["parametres"], sort_keys=True) for v in versions}
    assert len(versions) == len(COUPES_DE_L_ANTICIPATION) - 1
    assert lus == {json.dumps(_version(ANTICIPATION, "structure_financiere")["contenu"]
                              ["parametres"], sort_keys=True)}


def test_la_table_des_ages_est_l_escalier_du_portage():
    """La table de l'accord de 2017 descend de 0,99 un trimestre avant l'âge
    de la retraite à 0,43 dix ans avant : c'est l'escalier du portage,
    trimestre par trimestre, et la formule de l'accord Arrco de 1996 ; son
    plancher est celui du portage."""
    assert len(TABLE_DES_AGES) == 40
    assert [_escalier(t) for t in range(40, 0, -1)] == list(TABLE_DES_AGES)
    assert [_accord_arrco_de_1996(t) for t in range(40, 0, -1)] == list(TABLE_DES_AGES)
    assert _constante_du_portage("COEFFICIENT_ANTICIPATION_PLANCHER") == TABLE_DES_AGES[0]


def test_la_table_des_trimestres_manquants_est_le_bas_de_la_table_des_ages():
    """« 20 0,78 » à « 1 0,99 » (article 85, 3) : les vingt dernières lignes
    de la table des âges, ce qu'écrivaient déjà les annexes de 2011, « en
    assimilant à l'âge » de la retraite « l'âge auquel les intéressés auraient
    effectivement compté le nombre de trimestres d'assurance requis »."""
    assert len(TABLE_DES_TRIMESTRES_MANQUANTS) == 20
    assert TABLE_DES_TRIMESTRES_MANQUANTS == TABLE_DES_AGES[20:]
    assert [_escalier(t) for t in range(20, 0, -1)] == list(TABLE_DES_TRIMESTRES_MANQUANTS)


def test_l_age_de_2011_a_2018_est_celui_que_la_caisse_servait():
    """De 2011 à 2018, l'accord du 18 mars 2011 fige l'âge de la retraite dans
    la rédaction de L. 351-8 et de L. 161-17-2 du jour de l'accord ; la caisse
    a servi celui de la loi du 21 décembre 2011. Les périodes des régimes de
    la fiche lisent l'âge d'annulation de la décote de chaque génération, et
    la table du dépôt porte celui de la caisse, au mois près."""
    chemin = REFERENCE / "legislation" / "age_annulation_decote.csv"
    with chemin.open(encoding="utf-8", newline="") as flux:
        ages = {float(ligne["generation"]): float(ligne["age"])
                for ligne in csv.DictReader(l for l in flux if not l.startswith("#"))}
    for generation, (ans, mois) in AGES_DE_LA_CAISSE_EN_2018.items():
        assert ages[generation] == round(ans + mois / 12, 2), generation
    for code in carte.fiches()[ANTICIPATION]["regimes"]:
        lus = {periode.get("age_taux_plein_par_generation")
               for annee in range(2011, 2019) for periode in _periodes(code, annee)}
        assert lus <= {"age_annulation_decote"}, (code, lus)


@pytest.mark.parametrize("version, mot", ECARTS_DE_L_ANTICIPATION)
def test_ce_que_le_modele_fait_autrement_l_anticipation_le_declare(version, mot):
    """Le modèle exonère dès 1983 qui a la durée, quelle que soit sa
    situation ; il exonère les mêmes catégories dans tous les régimes ; il ne
    connaît ni les mineurs de fond, ni le report des points de la tranche C :
    une approximation touche la version et le dit."""
    fiche = carte.fiches()[ANTICIPATION]
    assert any(version in (a.get("version") or []) and mot in str(a.get("ecart"))
               for a in fiche.get("approximations") or []), (version, mot)
