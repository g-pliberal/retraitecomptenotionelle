"""Les cultes, lus au droit.

Deux fiches de la carte, lues au droit le 3 novembre 2026 (action 130) : le
salaire annuel moyen de la pension des cultes, fait depuis 1998 de la base
forfaitaire de chaque année (`cultes_salaire_annuel_moyen`), dans l'article 19
de la loi de financement pour 1998, dans les rédactions de R. 721-29, R. 721-30
et R. 721-39-2 du code de la sécurité sociale, de 1998 à 2006, et dans celles
qui les reprennent, R. 382-89, R. 382-90 et R. 382-121 ; la retraite
complémentaire obligatoire du ministre du culte rémunéré
(`cultes_retraite_complementaire`), dans les huit rédactions de L. 921-1, de
1994 à 2023.

Chaque paramètre d'une version porte le nom du champ de la période qui le
porterait, et la fiche de régime en porte la valeur sur chaque année que la
version couvre en entier : `regimes/cavimac.yaml`, `regimes/arrco_cultes.yaml`.
L'année ne se lit pas à la même date pour tous : la base forfaitaire d'une
année, à cette année (`periode.debut`) ; la règle du salaire annuel moyen, à
la date d'effet de la pension (`liquidation.date_effet`), comme le moteur les
lit (`droit/liquider.assiette_de_reference`, `salaire_de_reference`).
Quelques-uns se lisent ailleurs : le taux de cotisation, qui renvoie à celui
de la tranche 1 d'un autre régime, la même année ; les statuts que les
affiliations routent au régime ; les contributions d'équilibre, dans leur
barème. Ce que le modèle ne sert pas, la fiche le déclare, et le test qui suit
`ECARTS_DECLARES` le tient, cas par cas.
"""

from __future__ import annotations

import functools
import re
from datetime import date, timedelta

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte
from retraite_notionnelle.simulateur import Simulateur

SALAIRE, COMPLEMENTAIRE = "cultes_salaire_annuel_moyen", "cultes_retraite_complementaire"
LOT = (SALAIRE, COMPLEMENTAIRE)
REFERENCE = RACINE_DONNEES / "reference"
#: La création du régime des cultes, et la dernière année que les
#: confrontations parcourent.
DEBUT, HORIZON = 1979, 2050
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")
#: Les dates qui décident, fiche par fiche.
DATES = {SALAIRE: {"liquidation.date_effet", "periode.debut"},
         COMPLEMENTAIRE: {"periode.debut"}}

#: Les paramètres que le moteur lit à la date d'effet de la pension ; les
#: autres, à l'année de la période.
A_LA_LIQUIDATION = {"salaire_reference", "salaire_reference_par_generation",
                    "regles_du_salaire_annuel_moyen", "fractions_des_cultes"}
#: Le taux qui renvoie au taux de la tranche 1 d'un autre régime, la même
#: année : la version porte le nom de ce régime.
PAR_RENVOI, RENVOYES = {"taux_cotisation_retraite"}, ("arrco", "agirc_arrco")
#: Les contributions d'équilibre, lues dans leur barème
#: (`legislation/contributions_equilibre_agirc_arrco.yaml`) : le taux de la
#: tranche 1, salarié et employeur, ou rien quand le régime ne la verse pas.
CONTRIBUTIONS = {"contribution_agff": "agff", "contribution_ceg": "ceg"}
#: Ce que le modèle ne sert pas : il n'ajoute pas la garantie mensuelle de
#: rémunération. Le SMIC de chaque mois, il le sert depuis le 3 novembre 2026
#: (`smic_du_mois`, `tests/test_cultes_smic_du_mois.py`).
SANS_SUPPORT = {"garantie_mensuelle_la_plus_elevee"}

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ qu'elle lit et que le dépôt porte autrement, les régimes où il le
#: porte autrement (tous, sans eux), et ce que cite l'approximation qui le
#: déclare.
SMIC_DU_MOIS = ("cent_soixante_neuf_heures", "garantie_mensuelle_de_remuneration",
                "duree_legale_du_travail")
ECARTS_DECLARES = [
    (SALAIRE, "garantie_mensuelle_de_remuneration", "garantie_mensuelle_la_plus_elevee",
     None, "article 32"),
    (COMPLEMENTAIRE, "institution_de_l_arrco", "contribution_agff", None, "10 février 2001"),
]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _version(nom: str, identifiant: str) -> dict:
    return next(v for v in _versions(nom) if v["id"] == identifiant)


def _bornes(version: dict, nom: str) -> list:
    return version["bornes"].get(nom) or [None, None]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1979."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


@functools.cache
def _periodes_du_regime(code: str) -> tuple[dict, ...]:
    return tuple(yaml.safe_load((REFERENCE / "regimes" / f"{code}.yaml")
                                .read_text(encoding="utf-8"))["periodes"])


def _periodes(code: str, annee: int) -> list[dict]:
    """Les périodes du régime qui couvrent l'année ; rien hors d'elles."""
    return [p for p in _periodes_du_regime(code)
            if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"])]


@functools.cache
def _affiliations() -> dict:
    return yaml.safe_load((REFERENCE / "legislation" / "affiliations.yaml")
                          .read_text(encoding="utf-8"))["affiliations"]


def _statuts_affilies(code: str, annee: int) -> tuple[str, ...]:
    """Les statuts que les affiliations routent au régime, cette année."""
    return tuple(sorted(
        statut for statut, affiliation in _affiliations().items()
        for periode in affiliation.get("periodes") or []
        if periode["debut"] <= annee and (periode["fin"] is None or annee <= periode["fin"])
        and code in (periode.get("regimes") or [])))


@functools.cache
def _contributions() -> dict:
    texte = (REFERENCE / "legislation" / "contributions_equilibre_agirc_arrco.yaml"
             ).read_text(encoding="utf-8")
    return {c["code"]: c for c in yaml.safe_load(texte)["contributions"]}


def _contribution(code: str, regime: str, annee: int) -> float | None:
    """Le taux de la contribution sur la tranche 1 au 1er janvier de l'année,
    salarié et employeur, si le régime la verse ; rien sinon."""
    contribution = _contributions()[code]
    jour = date(annee, 1, 1)
    if regime not in contribution["regimes"] or (
            contribution.get("jusqu_au") and jour > contribution["jusqu_au"]):
        return None
    baremes = [b for b in contribution["baremes"] if b["debut"] <= jour]
    if not baremes:
        return None
    tranche = (baremes[-1].get("tous") or baremes[-1]["non_cadres"])[0]
    return round(tranche["salarie"] + tranche["employeur"], 6)


def _renvoi(code: str, champ: str, annee: int) -> set:
    """Le régime dont la tranche 1 porte, cette année, la valeur que porte la
    période du régime ; la valeur elle-même, s'il n'y en a pas un et un seul."""
    portes = set()
    for periode in _periodes(code, annee):
        valeur = periode.get(champ)
        egaux = [r for r in RENVOYES
                 if any(p.get(champ) == valeur for p in _periodes(r, annee)
                        if p.get("assiette") == "tranche_1")]
        portes.add(egaux[0] if len(egaux) == 1 else valeur)
    return portes


def _valeur(valeur):
    """Une valeur comparable : une liste du YAML, en tuple."""
    return tuple(_valeur(v) for v in valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str, code: str) -> set:
    """Ce que le dépôt porte pour ce champ, sur les années que la version
    couvre en entier, à la date qui le décide ; rien si elle n'en couvre
    aucune."""
    if champ in SANS_SUPPORT:
        return {None}
    nom = "liquidation.date_effet" if champ in A_LA_LIQUIDATION else "periode.debut"
    annees = _annees_entieres(*_bornes(version, nom))
    if champ == "statuts_affilies":
        return {_statuts_affilies(code, annee) for annee in annees}
    if champ in CONTRIBUTIONS:
        return {_contribution(CONTRIBUTIONS[champ], code, annee) for annee in annees
                if _periodes(code, annee)}
    if champ in PAR_RENVOI:
        return set().union(*(_renvoi(code, champ, annee) for annee in annees))
    return {_valeur(periode.get(champ)) for annee in annees for periode in _periodes(code, annee)}


def _declare(nom: str, version: str, champ: str, code: str) -> bool:
    return any((n, v, c) == (nom, version, champ) and (regimes is None or code in regimes)
               for n, v, c, regimes, _ in ECARTS_DECLARES)


def _en_toutes_lettres(jour: date) -> str:
    return f"{'1er' if jour.day == 1 else jour.day} {MOIS[jour.month - 1]} {jour.year}"


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Les versions se coupent sur les dates qui décident de la fiche ; chaque
    version commence le jour où entre en vigueur le texte qui la fait naître
    (`nee_de`), qu'elle cite parmi ses textes, ou le jour que ce texte nomme :
    la garantie de rémunération court « du 1er janvier 2002 jusqu'au 30 juin
    2005 », quand la rédaction qui l'écrit entre en vigueur le 26 février
    2004."""
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


def test_les_periodes_portent_ce_que_chaque_version_lit():
    """Sur chaque année que la version couvre en entier, les périodes de son
    régime portent la valeur que la version lit, sous le même nom, ou ce que
    le paramètre renvoie ; sinon, l'écart est déclaré."""
    for nom in LOT:
        regimes = carte.fiches()[nom]["regimes"]
        for version in _versions(nom):
            for champ, lu in (version["contenu"].get("parametres") or {}).items():
                for code in regimes:
                    portes = _portes(version, champ, code)
                    if portes and not _declare(nom, version["id"], champ, code):
                        assert portes == {_valeur(lu)}, (nom, version["id"], champ, code, portes)


@pytest.mark.parametrize("nom, version, champ, regimes, cite", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, regimes, cite):
    """La version lit une valeur que le dépôt ne porte pas ; une approximation
    de la fiche touche cette version et cite le texte qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = _version(nom, version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    portes = set().union(*(_portes(lue, champ, code) for code in (regimes or fiche["regimes"])))
    assert portes and valeur not in portes, (nom, version, champ)
    assert any(version in (a.get("version") or []) and cite in str(a.get("textes") or "")
               for a in fiche.get("approximations") or []), (nom, version, cite)


def test_le_taux_de_base_de_la_caisse_est_la_tranche_1_et_la_ceg():
    """« RCO — Tous cultes - taux de base » 10,02 %, « part collective »
    6,01 %, « part personnelle » 4,01 % (circulaire de la CAVIMAC n° 2026/03) :
    le taux de la tranche 1 de l'Agirc-Arrco que porte la période, et la
    contribution d'équilibre générale de son barème, partagés à 60 et 40 %."""
    periode, = _periodes("arrco_cultes", 2026)
    ceg = _contribution("ceg", "arrco_cultes", 2026)
    taux = periode["taux_cotisation_retraite"] + ceg
    assert round(taux, 4) == 0.1002
    assert round(taux * periode["part_salariale"], 4) == 0.0401
    assert round(taux * (1 - periode["part_salariale"]), 4) == 0.0601


def test_le_smic_des_mois_releve_la_base_d_au_plus_2_9_pour_cent_en_2004(simulateur):
    """De 1998 à 2009, le SMIC n'est relevé qu'au 1er juillet (« A compter du
    1er juillet 1998 […] 40,22 F », et chaque année jusqu'en 2009, décrets lus
    dans l'index JORF) : la base au SMIC de chaque mois passe celle au SMIC de
    janvier de la moitié du relèvement, au plus 2,9 %, en 2004 — l'effet que
    la fiche dit du changement du 3 novembre 2026. Aucune approximation ne
    déclare plus le SMIC de janvier."""
    macro = simulateur.macro
    hausses = {annee: macro.smic_horaire_des_mois(annee) / macro.smic_horaire(annee) - 1
               for annee in range(1998, 2027)}
    pire = max(hausses, key=hausses.get)
    assert (pire, round(hausses[pire], 3)) == (2004, 0.029)
    fiche = carte.fiches()[SALAIRE]
    assert "2,9 %" in str(fiche["effet"]), fiche["effet"]
    assert not any(re.search(r"SMIC (horaire )?du 1er janvier", str(a.get("ecart")))
                   for a in fiche.get("approximations") or [])


def test_la_garantie_de_remuneration_reste_sous_cent_soixante_neuf_heures():
    """La garantie de l'article 32 de la loi n° 2000-37 ne passe pas le SMIC
    de « cent soixante-neuf heures » : le forfait que le modèle compte à la
    durée légale, 1 820 heures par an, lui manque au plus 2 028 / 1 820 − 1,
    11 % — l'effet que l'approximation déclare."""
    heures = {v["id"]: v["contenu"]["parametres"]["assiette_repere_smic"]
              for v in _versions(SALAIRE)
              if "assiette_repere_smic" in (v["contenu"].get("parametres") or {})}
    assert (heures["cent_soixante_neuf_heures"], heures["garantie_mensuelle_de_remuneration"]
            ) == (169 * 12, 35 * 52)
    ecart = heures["cent_soixante_neuf_heures"] / heures["garantie_mensuelle_de_remuneration"] - 1
    assert round(ecart, 2) == 0.11
    approximation = next(a for a in carte.fiches()[SALAIRE]["approximations"]
                         if "garantie_mensuelle_de_remuneration" in (a.get("version") or [])
                         and "article 32" in str(a.get("textes")))
    assert "11 %" in str(approximation["effet"]), approximation["effet"]
