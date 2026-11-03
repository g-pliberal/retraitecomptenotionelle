"""L'Ircantec, lue au droit.

Deux fiches de la carte, lues au droit le 3 novembre 2026 (action 130) dans
les treize rédactions de l'article 16 de l'arrêté du 30 décembre 1970, de sa
publication, le 9 février 1971, à celle du 14 septembre 2023, et dans les
arrêtés qui les ont faites, au Journal officiel : le coefficient
d'anticipation (`coefficient_anticipation_ircantec`), que l'Ircantec applique
aussi aux points de l'IPACTE et de l'IGRANTE qu'elle a repris le 1er janvier
1971, et les deux majorations des points d'après l'âge du taux plein
(`surcote_ircantec`).

Chaque paramètre d'une version porte le nom du champ de la période qui le
porterait, ou celui d'une constante du portage, qui fait foi
(`moteur/js/droit/liquider.js`). Les fiches de régime en portent la valeur
sur chaque année que la version couvre en entier : `regimes/ircantec.yaml`,
ses deux séries de périodes, une par tranche ; `regimes/ipacte.yaml` et
`regimes/igrante.yaml`, une période chacune, que le moteur lit encore après
leur fermeture (`droit/commun.periode_de_liquidation`). Sinon, la fiche
déclare l'écart, et le test qui suit `ECARTS_DECLARES` le tient, cas par cas.
"""

from __future__ import annotations

import csv
import functools
import json
import re
from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

ANTICIPATION, SURCOTE = "coefficient_anticipation_ircantec", "surcote_ircantec"
LOT = (ANTICIPATION, SURCOTE)
REFERENCE = RACINE_DONNEES / "reference"
PORTAGE = Path(__file__).resolve().parents[1] / "moteur" / "js" / "droit" / "liquider.js"
#: La création de l'IPACTE, et la dernière année que les confrontations
#: parcourent.
DEBUT, HORIZON = 1951, 2050
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")

#: Les paramètres que sert le portage, et non une période : le nom de sa
#: constante, ou rien, quand il ne sert pas ce que le paramètre dit — une
#: table par année d'âge, un trimestre de quatre-vingt-dix jours : il compte
#: au trimestre, en mois.
DU_PORTAGE = {
    "coefficient_plancher": "COEFFICIENT_ANTICIPATION_PLANCHER",
    "paliers_d_anticipation": "PALIERS_ANTICIPATION",
    "majoration_par_trimestre_ecoule": "SURCOTE_IRCANTEC_AGE",
    "majoration_par_trimestre_cotise": "SURCOTE_IRCANTEC_DUREE",
    "coefficients_par_annee_d_age": None,
    "trimestre_en_jours": None,
}
#: Le paramètre qu'un test à lui confronte au dépôt : la durée que la seconde
#: table lit de 1983 à 2003.
A_PART = {"duree_de_la_seconde_table_trimestres"}

#: Les versions du coefficient qui couvrent une année entière, celles d'avant
#: le 1er avril 1983 parmi elles, et celles d'après le 1er juillet 2011.
COUVRANTES = ("ipacte_et_igrante", "arrete_de_1970", "femmes_de_la_loi_de_1977",
              "escalier_au_trimestre_1983", "retraite_anticipee_2004", "ages_de_2010",
              "compte_de_prevention_2018", "ancres_fixes_2023")
AVANT_1983 = ("ipacte_et_igrante", "arrete_de_1970", "anciens_combattants_1976",
              "travailleurs_manuels_1977", "femmes_de_la_loi_de_1977",
              "ordonnance_du_26_mars_1982", "structure_financiere_1983")
DEPUIS_2011 = ("ages_de_2010", "compte_de_prevention_2018", "ancres_fixes_2023")
FERMES = ("ipacte", "igrante")

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ qu'elle lit et que le dépôt porte autrement, les régimes où il le
#: porte autrement (tous, ou le portage, sans eux), et l'article que cite
#: l'approximation qui le déclare. Le modèle liquide l'Ircantec avec la
#: pension de base, jamais avant l'âge d'ouverture de sa période, quand
#: l'article ouvre l'anticipation dix ans avant l'âge du taux plein ; il lit
#: l'escalier au trimestre, que l'arrêté du 26 juillet 1983 crée, quand les
#: rédactions d'avant ne lisaient qu'une table par année d'âge ; il exonère
#: dès 1951 qui a la durée, dans la période unique de l'IPACTE et de
#: l'IGRANTE, quand l'article ne le fait qu'« à compter du 1er avril 1983 » ;
#: il y garde soixante-cinq ans après le 1er juillet 2011 ; il compte en mois
#: le trimestre de la surcote, de quatre-vingt-dix jours depuis 2023.
ECARTS_DECLARES = [
    *[(ANTICIPATION, version, "anticipation_maximale_annees", None, "article 16, I")
      for version in COUVRANTES],
    *[(ANTICIPATION, version, champ, None, "article 16, I")
      for version in AVANT_1983
      for champ in ("coefficients_par_annee_d_age", "paliers_d_anticipation")],
    *[(ANTICIPATION, version, "duree_requise_par_generation", FERMES, "6° c)")
      for version in ("ipacte_et_igrante", "arrete_de_1970", "femmes_de_la_loi_de_1977")],
    *[(ANTICIPATION, version, "age_taux_plein_par_generation", FERMES, "L. 351-8")
      for version in DEPUIS_2011],
    (SURCOTE, "precisions_de_2023", "trimestre_en_jours", None, "IV, 3°"),
]


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _version(nom: str, identifiant: str) -> dict:
    return next(v for v in _versions(nom) if v["id"] == identifiant)


def _bornes(version: dict) -> list:
    return version["bornes"]["liquidation.date_effet"]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1951."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


@functools.cache
def _periodes_du_regime(code: str) -> tuple[dict, ...]:
    return tuple(yaml.safe_load((REFERENCE / "regimes" / f"{code}.yaml")
                                .read_text(encoding="utf-8"))["periodes"])


def _periodes(code: str, annee: int) -> list[dict]:
    """Les périodes qui liquident dans ce régime une pension de l'année : les
    deux tranches de l'Ircantec ; la période de la dernière année d'un régime
    fermé, après elle ; rien avant sa première."""
    periodes = _periodes_du_regime(code)
    annee = min(annee, max(9999 if p["fin"] is None else p["fin"] for p in periodes))
    return [p for p in periodes
            if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"])]


def _constante(nom: str):
    """Une constante du portage, sa valeur littérale."""
    trouve = re.search(rf"^const {nom} = (.+);$", PORTAGE.read_text(encoding="utf-8"), re.M)
    assert trouve, f"le portage ne définit plus {nom}"
    return json.loads(trouve.group(1))


def _valeur(valeur):
    """Une valeur comparable : un barème, liste dans le YAML, en tuple."""
    return tuple(_valeur(v) for v in valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str, code: str | None) -> set:
    """Ce que le dépôt porte pour ce champ : la constante du portage, ou les
    valeurs des périodes du régime sur les années que la version couvre en
    entier ; rien si elle n'en couvre aucune."""
    if champ in DU_PORTAGE:
        constante = DU_PORTAGE[champ]
        return {None if constante is None else _valeur(_constante(constante))}
    return {_valeur(periode.get(champ))
            for annee in _annees_entieres(*_bornes(version))
            for periode in _periodes(code, annee)}


def _declare(nom: str, version: str, champ: str, code: str | None) -> bool:
    return any((n, v, c) == (nom, version, champ) and (regimes is None or code in regimes)
               for n, v, c, regimes, _ in ECARTS_DECLARES)


def _en_toutes_lettres(jour: date) -> str:
    return f"{'1er' if jour.day == 1 else jour.day} {MOIS[jour.month - 1]} {jour.year}"


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Chaque fiche du lot couvre toute date d'effet ; chaque version commence
    le jour où entre en vigueur le texte qui la fait naître (`nee_de`), qu'elle
    cite parmi ses textes, ou le jour que ce texte fixe, et qu'il cite : « à
    compter du 1er avril 1983 », plus tôt que sa publication, « à compter du
    1er janvier 2010 », plus tard."""
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
                debut = _bornes(version)[0]
                assert (texte["en_vigueur"] == debut
                        or f"compter du {_en_toutes_lettres(debut)}" in str(texte.get("citation"))
                        ), (nom, version["id"])


def test_les_periodes_et_le_portage_portent_ce_que_chaque_version_lit():
    """Sur chaque année que la version couvre en entier, les périodes de chacun
    de ses régimes portent la valeur que la version lit, sous le même nom ; le
    portage, la constante qui la sert ; sinon, l'écart est déclaré."""
    for nom in LOT:
        regimes = carte.fiches()[nom]["regimes"]
        for version in _versions(nom):
            for champ, lu in (version["contenu"].get("parametres") or {}).items():
                if champ in A_PART:
                    continue
                for code in [None] if champ in DU_PORTAGE else regimes:
                    portes = _portes(version, champ, code)
                    if portes and not _declare(nom, version["id"], champ, code):
                        assert portes == {_valeur(lu)}, (nom, version["id"], champ, code)


@pytest.mark.parametrize("nom, version, champ, regimes, article", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, regimes,
                                                             article):
    """La version lit une valeur que le dépôt ne porte pas, dans les régimes
    nommés ; une approximation de la fiche touche cette version et cite
    l'article qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = _version(nom, version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    codes = [None] if champ in DU_PORTAGE else (regimes or fiche["regimes"])
    portes = set().union(*(_portes(lue, champ, code) for code in codes))
    assert portes and valeur not in portes, (nom, version, champ)
    assert any(version in (a.get("version") or []) and article in str(a.get("textes") or "")
               for a in fiche.get("approximations") or []), (nom, version, article)


def _lignes(relatif: str) -> list[dict]:
    with (REFERENCE / relatif).open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(ligne for ligne in flux if not ligne.startswith("#")))


def _escalier(manquants: int) -> float:
    """Le coefficient du portage pour un nombre de trimestres d'anticipation,
    lu dans ses paliers."""
    coefficient, precedent = 1.0, 0
    for borne, pas in _constante("PALIERS_ANTICIPATION"):
        coefficient -= max(0, min(manquants, borne) - precedent) * pas
        precedent = borne
    return round(coefficient, 6)


def test_la_table_de_1970_est_l_escalier_aux_annees_revolues():
    """« AGES COEFFICIENTS : 55 ans 0,43 […] 64 ans 0,96 » : la table de
    l'arrêté du 30 décembre 1970, que les rédactions suivent jusqu'au 31 août
    1983, est l'escalier du portage à chaque anniversaire ; entre deux, elle
    garde le coefficient de l'âge révolu, que le portage relève à chaque
    trimestre, jusqu'à 5,25 points de plus — l'écart que la fiche déclare."""
    table = _version(ANTICIPATION, "arrete_de_1970")["contenu"]["parametres"][
        "coefficients_par_annee_d_age"]
    assert len(table) == 10
    assert [round(c, 6) for c in table] == [_escalier(4 * (65 - age)) for age in range(55, 65)]
    entre_deux = max(_escalier(4 * (65 - age) - t) - table[age - 55]
                     for age in range(55, 65) for t in range(1, 4))
    assert round(entre_deux, 6) == 0.0525


def test_les_ancres_fixes_de_2023_tombent_sur_l_escalier_du_portage():
    """La rédaction du 14 septembre 2023 ancre l'escalier à soixante-deux ans,
    0,78, et à soixante-quatre, 0,88, et non plus à l'âge légal : pour toute
    génération qui atteint après ce jour l'âge du 1° de L. 351-8, soixante-sept
    ans, ce sont vingt et douze trimestres avant lui, où le portage, qui
    ancre ses paliers sur l'âge du taux plein, rend les mêmes coefficients ;
    et 0,43 dix ans avant."""
    ages = {float(l["generation"]): float(l["age"])
            for l in _lignes("legislation/age_annulation_decote.csv")}

    def age(generation: int) -> float:
        """La ligne de la génération, ou de la dernière qui la précède."""
        return ages[max(g for g in ages if g <= generation)]

    tardives = {age(g) for g in range(1950, 2001) if g + 1 + age(g) > 2023 + 8.5 / 12}
    assert tardives == {67.0}
    assert (_escalier(4 * (67 - 62)), _escalier(4 * (67 - 64)), _escalier(40)) == (0.78, 0.88, 0.43)
    assert _constante("COEFFICIENT_ANTICIPATION_PLANCHER") == _escalier(40)


def test_la_seconde_table_de_1983_lit_trente_sept_ans_et_demi():
    """De 1983 à 2003, le II de l'article 16 ouvre la seconde table à la durée
    « comprise entre trente-deux ans et demi et trente-sept ans et demi », et
    assimile à soixante-cinq ans l'âge où l'agent « aurait effectivement
    compté trente-sept années et demie d'assurance » ; le modèle y lit la
    durée du régime général de la génération (`duree_requise_par_generation`).
    Elles sont égales pour toute génération de soixante à soixante-cinq ans
    jusqu'en 1993 ; la loi du 22 juillet 1993 relève la seconde d'un trimestre
    par génération dès 1934 : de 1994 à 2003, la fiche déclare l'écart."""
    lignes = _lignes("legislation/duree_assurance_requise.csv")
    durees = {int(float(l["generation"])): int(l["trimestres"]) for l in lignes}

    def duree(generation: int) -> int:
        return durees[max(g for g in durees if g <= generation)]

    lues = [(version, version["contenu"]["parametres"].get("duree_de_la_seconde_table_trimestres"))
            for version in _versions(ANTICIPATION)]
    lues = [(version, lu) for version, lu in lues if lu]
    assert {lu for _, lu in lues} == {150}
    ecarts = {annee for version, lu in lues for annee in _annees_entieres(*_bornes(version))
              if any(duree(annee - age) != lu for age in range(60, 66))}
    assert min(ecarts) == 1994 and max(ecarts) == 2003
    fiche = carte.fiches()[ANTICIPATION]
    touchees = {version["id"] for version, _ in lues
                if set(_annees_entieres(*_bornes(version))) & ecarts}
    assert any(touchees <= set(a.get("version") or []) and "1994" in str(a.get("ecart"))
               for a in fiche.get("approximations") or []), touchees
