"""Les barèmes du modèle dans la base de législation de la Cnav (action 175,
étape 2) : chacun confronté à la série du dépôt qu'il double.

Le registre de la base (`data/reference/legislation/cnav/`) dit chaque barème
`recoupe` par l'un de ces tests, à la version qu'il date (`modifie_le`). Les
valeurs sont recopiées du barème ou de la page qu'il joint, lus le 30 octobre
2026 : quand la base en sert une autre version, la veille le dit (étape 5), et
la session qui la relit récrit la table du test. Un écart entre la caisse et la
série se corrige, ou se déclare ici avec sa raison ; un écart qui change le
calcul passe à la session du modèle.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
REGIMES = RACINE / "data" / "reference" / "regimes"


def _csv(chemin: Path) -> list[dict]:
    return list(csv.DictReader(
        ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
        if not ligne.startswith("#")))


def _taux_annuels(regime: str) -> dict[tuple[int, str], float]:
    return {(int(ligne["annee"]), ligne["mesure"]): float(ligne["valeur"])
            for ligne in _csv(REGIMES / "taux_cotisation_annuels.csv")
            if ligne["regime"] == regime}


def _au_1er_janvier(periodes: tuple, annee: int) -> tuple:
    """La période en vigueur au 1er janvier de l'année : la dernière qui a
    commencé ce jour-là ou avant."""
    return [periode for periode in periodes if periode[0] <= f"{annee}-01-01"][-1]


# -- les taux de droit commun --------------------------------------------------

#: « Taux des cotisations de droit commun »
#: (`cotisation_salaire_taux_cotisation_droit_commun_bar.aspx`, version du
#: 25 mars 2026), et, pour avant 2014, les pages de sa page jointe
#: (`listes_baremes/BNL-L_B_TAUXDECOTISATIONS.htm`), une par période
#: (`listes_baremes/cotisation/BNL-TAUX_COTISATIONS*.htm`). L'assurance
#: vieillesse depuis le 1er octobre 1967 : début de la période, puis le salarié
#: et l'employeur sous le plafond, le salarié et l'employeur sur la totalité du
#: salaire, en pour cent. Le barème dit « vieillesse et veuvage » depuis que la
#: cotisation d'assurance veuvage, 0,10 % du salarié sur la totalité de 1981 à
#: juin 2004, y est fondue ; avant, les pages la donnent à part, et elle n'est
#: pas ici : la série ne compte que la vieillesse.
VIEILLESSE = (
    ("1967-10-01", 3.00, 5.50, 0.00, 0.00),   # décret n° 67-803
    ("1968-07-01", 3.00, 5.50, 0.00, 0.00),
    ("1970-08-01", 3.00, 5.75, 0.00, 0.00),
    ("1971-01-01", 3.00, 5.75, 0.00, 0.00),
    ("1974-01-01", 3.00, 7.25, 0.00, 0.00),
    ("1976-01-01", 3.25, 7.50, 0.00, 0.00),
    ("1976-10-01", 3.45, 7.70, 0.00, 0.00),
    ("1977-07-01", 3.45, 7.70, 0.00, 0.00),
    ("1979-01-01", 4.70, 8.20, 0.00, 0.00),
    ("1979-08-01", 4.70, 8.20, 0.00, 0.00),
    ("1980-01-01", 4.70, 8.20, 0.00, 0.00),
    ("1981-01-01", 4.70, 8.20, 0.00, 0.00),
    ("1981-02-01", 4.70, 8.20, 0.00, 0.00),
    ("1981-11-14", 4.70, 8.20, 0.00, 0.00),
    ("1984-01-01", 5.70, 8.20, 0.00, 0.00),
    ("1986-08-01", 6.40, 8.20, 0.00, 0.00),
    ("1987-07-01", 6.60, 8.20, 0.00, 0.00),
    ("1989-01-01", 7.60, 8.20, 0.00, 0.00),
    ("1991-02-01", 6.55, 8.20, 0.00, 1.60),
    ("1991-07-01", 6.55, 8.20, 0.00, 1.60),
    ("1992-01-01", 6.55, 8.20, 0.00, 1.60),
    ("1997-01-01", 6.55, 8.20, 0.00, 1.60),
    ("1998-01-01", 6.55, 8.20, 0.00, 1.60),
    ("2004-07-01", 6.55, 8.20, 0.10, 1.60),
    ("2006-01-01", 6.65, 8.30, 0.10, 1.60),
    ("2012-11-01", 6.75, 8.40, 0.10, 1.60),
    # Le barème lui-même, depuis 2014.
    ("2014-01-01", 6.80, 8.45, 0.25, 1.75),
    ("2015-01-01", 6.85, 8.50, 0.30, 1.80),
    ("2016-01-01", 6.90, 8.55, 0.35, 1.85),
    ("2017-01-01", 6.90, 8.55, 0.40, 1.90),   # « Du 01/01/2017 au 31/12/2023 »
    ("2024-01-01", 6.90, 8.55, 0.40, 2.02),
    ("2025-01-01", 6.90, 8.55, 0.40, 2.02),
    ("2026-01-01", 6.90, 8.55, 0.40, 2.11),
)

#: Avant le 1er octobre 1967, une seule cotisation d'assurances sociales —
#: maladie, maternité, invalidité, vieillesse et décès —, sous le plafond, que
#: les pages d'avant 2014 donnent aussi : début, salarié de moins de 65 ans,
#: employeur, en pour cent. De 1930 à 1935, la cinquième catégorie de salaires
#: cotise 4,44 % de part et d'autre ; depuis juillet 1948, le salarié de plus
#: de 65 ans, 2 %.
ASSURANCES_SOCIALES = (
    ("1930-07-01", 4.00, 4.00),   # loi du 5 avril 1928 modifiée, art. 2
    ("1936-01-01", 3.50, 3.50),   # décret-loi du 28 octobre 1935, art. 40
    ("1937-01-01", 4.00, 4.00),
    ("1945-01-01", 6.00, 6.00),   # arrêté du 14 mai 1945
    ("1947-01-01", 6.00, 10.00),  # arrêté du 24 mars 1947
    ("1948-07-01", 6.00, 10.00),  # loi n° 48-1306, art. 18
    ("1959-01-01", 6.00, 12.50),  # ordonnance n° 58-1374, art. 10
    ("1961-01-01", 6.00, 13.50),  # décret n° 60-1485
    ("1962-01-01", 6.00, 14.25),  # décret n° 61-1525
    ("1966-09-01", 6.00, 15.00),  # arrêté du 29 juillet 1966
)

#: La part vieillesse de la cotisation d'avant 1967, par la convention de la
#: série (`scripts/verifier_donnees.py`, `PART_VIEILLESSE_AVANT_1967`) : celle
#: que le décret de 1967 lui a donnée en séparant les branches, 8,5 points sur
#: 21.
PART_VIEILLESSE_AVANT_1967 = 8.5 / 21.0

#: Ce que la série retient autrement que le taux en vigueur au 1er janvier, et
#: pourquoi : sa valeur, et la raison.
CONVENTIONS_DE_LA_SERIE = {
    (1966, "taux_plafonne"): (
        0.085, "1966 prend le taux du 1er septembre, que 1967 reconduit "
        "(verifier_donnees.source_taux_avant_1967) : 15 % pour l'employeur, et "
        "non 14,25 %"),
    (1966, "part_salariale"): (0.285714, "id."),
    (1967, "part_salariale"): (
        0.352941, "1967 prend, pour l'année entière, le partage de la cotisation "
        "vieillesse du 1er octobre (3 % et 5,5 %), et non celui de la cotisation "
        "d'assurances sociales en vigueur au 1er janvier (6 % et 15 %) ; le taux, "
        "8,5 %, est le même des deux façons"),
}


def _attendus_droit_commun(annee: int) -> dict[str, float]:
    if annee < 1967:
        _, salarie, employeur = _au_1er_janvier(ASSURANCES_SOCIALES, annee)
        return {"taux_plafonne": (salarie + employeur) / 100 * PART_VIEILLESSE_AVANT_1967,
                "part_salariale": salarie / (salarie + employeur),
                "taux_deplafonne": 0.0, "part_salariale_deplafonnee": 0.0}
    if annee == 1967:
        # Au 1er janvier, la cotisation d'assurances sociales, à la part
        # vieillesse de la convention : 21 × 8,5 / 21.
        _, salarie, employeur = _au_1er_janvier(ASSURANCES_SOCIALES, annee)
        return {"taux_plafonne": (salarie + employeur) / 100 * PART_VIEILLESSE_AVANT_1967,
                "part_salariale": salarie / (salarie + employeur),
                "taux_deplafonne": 0.0, "part_salariale_deplafonnee": 0.0}
    _, salarie, employeur, salarie_total, employeur_total = _au_1er_janvier(VIEILLESSE, annee)
    deplafonne = salarie_total + employeur_total
    return {"taux_plafonne": (salarie + employeur) / 100,
            "part_salariale": salarie / (salarie + employeur),
            "taux_deplafonne": deplafonne / 100,
            "part_salariale_deplafonnee": salarie_total / deplafonne if deplafonne else 0.0}


def test_les_taux_de_droit_commun_de_la_cnav_sont_ceux_de_la_serie():
    """Le taux de cotisation vieillesse du régime général, année par année
    (`taux_cotisation_annuels.csv`), est celui que la Cnav publie en vigueur au
    1er janvier, de 1945 à 2026, sous le plafond et sur la totalité, avec le
    partage entre le salarié et l'employeur : le barème depuis 2014, ses pages
    d'avant, et, avant le 1er octobre 1967, la cotisation d'assurances sociales
    à la part vieillesse de la convention. La série les tient de la base LEGI
    depuis 1982 (D. 242-4), d'OpenFisca de 1967 à 1981, du document du COR
    avant : trois sources que la caisse confirme. Ce que la série retient
    autrement se déclare dans `CONVENTIONS_DE_LA_SERIE`."""
    serie = _taux_annuels("regime_general")
    for annee in range(1945, 2027):
        for mesure, attendu in _attendus_droit_commun(annee).items():
            valeur = serie[(annee, mesure)]
            if (annee, mesure) in CONVENTIONS_DE_LA_SERIE:
                convenue, raison = CONVENTIONS_DE_LA_SERIE[(annee, mesure)]
                assert valeur == pytest.approx(convenue, abs=1e-6), (annee, mesure, raison)
                assert valeur != pytest.approx(attendu, abs=1e-6), (
                    f"{annee} {mesure} : la convention ne s'écarte plus de la caisse, "
                    "elle se retire")
                continue
            assert valeur == pytest.approx(attendu, abs=1e-6), (annee, mesure, valeur, attendu)


def test_les_assurances_sociales_de_1930_cotisent_ce_que_la_cnav_publie():
    """La fiche des assurances sociales de 1930 (`assurances_sociales.yaml`)
    porte 8 %, moitié salarié, moitié employeur, de 1930 à 1945 : la Cnav le
    confirme de 1930 à 1935 pour les quatre premières catégories de salaires,
    et de 1937 à 1944. Elle publie aussi 7 % en 1936 et 8,88 % pour la
    cinquième catégorie de 1930 à 1935, que la fiche, d'un seul taux, ne
    distingue pas : un régime capitalisé, hors du compte notionnel, que la
    fiche garde pour dater le début des carrières."""
    import yaml

    fiche = yaml.safe_load((REGIMES / "assurances_sociales.yaml").read_text(encoding="utf-8"))
    (periode,) = fiche["periodes"]
    assert (periode["debut"], periode["fin"]) == (1930, 1945)
    for annee in (*range(1931, 1936), *range(1937, 1945)):
        _, salarie, employeur = _au_1er_janvier(ASSURANCES_SOCIALES, annee)
        assert periode["taux_cotisation_retraite"] == pytest.approx((salarie + employeur) / 100)
        assert periode["part_salariale"] == pytest.approx(salarie / (salarie + employeur))
    _, salarie, employeur = _au_1er_janvier(ASSURANCES_SOCIALES, 1936)
    assert (salarie + employeur) / 100 == pytest.approx(0.07)


# -- les taux des indépendants -------------------------------------------------


def _fiche(code: str) -> dict:
    import yaml

    return yaml.safe_load((REGIMES / f"{code}.yaml").read_text(encoding="utf-8"))


def _taux_de_la_fiche(code: str, annee: int) -> dict[str, float]:
    """Le taux de chaque assiette de la fiche, l'année donnée."""
    return {periode["assiette"]: periode["taux_cotisation_retraite"]
            for periode in _fiche(code)["periodes"]
            if periode["debut"] <= annee <= (periode.get("fin") or 9999)}


#: « Taux de cotisations des travailleurs indépendants »
#: (`ti_cotisation_taux_cotisation_bar.aspx`, version du 3 novembre 2025) et ses
#: éditions : avant 2006, les tables de l'ex-RSI qu'il joint
#: (`ti_cotisation_taux_cotisation_artisan_avant_2007.pdf`,
#: `…_commercant_avant_2007.pdf`) ; de 2006 à 2017, celle de l'édition « de
#: 2006 à 2019 » (`ti_cotisation_taux_cotisation_2006 _2019.pdf`) ; depuis 2018,
#: les éditions elles-mêmes, jusqu'à celle « à compter de 2023 », qui s'arrête
#: à 2025. La retraite de base (RVB), au-dessous de 65 ans, en pour cent : la
#: part du revenu dans la limite du plafond, puis celle qui le dépasse.
RVB_ARTISANS = (
    ("1973-01-01", 8.75, 0.0), ("1974-01-01", 10.25, 0.0), ("1976-01-01", 10.75, 0.0),
    ("1977-01-01", 11.15, 0.0), ("1979-01-01", 12.90, 0.0), ("1982-01-01", 12.90, 0.0),
    ("1984-01-01", 13.90, 0.0), ("1986-07-01", 14.36, 0.0), ("1986-10-01", 14.60, 0.0),
    ("1987-07-01", 14.80, 0.0), ("1989-01-01", 15.80, 0.0), ("1991-01-01", 16.16, 0.0),
    ("1991-04-01", 16.35, 0.0), ("2005-01-01", 16.45, 0.0),
)
RVB_COMMERCANTS = (
    ("1973-01-01", 8.75, 0.0), ("1974-01-01", 10.25, 0.0), ("1976-01-01", 10.75, 0.0),
    ("1976-10-01", 11.15, 0.0), ("1979-01-01", 12.90, 0.0), ("1984-01-01", 13.90, 0.0),
    ("1986-08-01", 14.60, 0.0), ("1987-07-01", 14.80, 0.0), ("1989-01-01", 15.80, 0.0),
    ("1991-01-01", 16.26, 0.0), ("1991-07-01", 16.35, 0.0), ("2004-07-01", 16.45, 0.0),
)
#: Artisans et commerçants ensemble, depuis 2006. La ligne de 2014 de l'édition
#: « de 2006 à 2019 » recopie celle de 2015 (17,40 % et 0,35 %) : le PDF
#: qu'elle joint, et la série, disent 17,15 % et 0,20 %. Pour 2012, le barème
#: ajoute que « le taux de cotisation à appliquer pour l'année 2012 est de
#: 16,68 % » (instruction ministérielle du 29 octobre 2012), la hausse de
#: novembre étalée sur l'année ; la table, comme la série, garde le taux du
#: 1er janvier.
RVB_INDEPENDANTS = (
    ("2006-01-01", 16.65, 0.00), ("2013-01-01", 16.85, 0.00), ("2014-01-01", 17.15, 0.20),
    ("2015-01-01", 17.40, 0.35), ("2016-01-01", 17.65, 0.50), ("2017-01-01", 17.75, 0.60),
    ("2025-01-01", 17.87, 0.72),
)
#: L'année que la base publie en dernier dans ces éditions.
DERNIERE_ANNEE_RVB = 2025

#: En 1991, la cotisation du régime général monte au 1er février (de 15,80 % à
#: 16,35 % du revenu sous le plafond) ; la caisse en étale la hausse sur
#: l'année, à sa façon pour chacun — 16,16 % puis 16,35 % au 1er avril pour
#: l'artisan, 16,26 % puis 16,35 % au 1er juillet pour le commerçant, 16,30 %
#: en moyenne l'un et l'autre —, quand la série garde le taux du 1er janvier
#: du régime général, 15,80 %.
CONVENTIONS_RVB = {("cancava", 1991): 0.158, ("organic", 1991): 0.158}


def test_les_taux_de_base_des_artisans_et_des_commercants_sont_ceux_de_la_caisse():
    """La cotisation de retraite de base des artisans (`cancava`) et des
    commerçants (`organic`) de 1973 à 2005, du RSI (`rsi`) de 2006 à 2017, puis
    de l'un et l'autre au régime général (`regime_general`, mesures
    `_non_salarie`) depuis 2018 : la série porte le taux du 1er janvier que la
    caisse publie. La caisse dit, pour la part du revenu sous le plafond, le
    taux entier ; la série, qui suit le partage du régime général, en retire
    la part qui court sur tout le revenu : 17,75 % sous le plafond et 0,60 %
    au-delà font 17,15 % sous le plafond et 0,60 % sur la totalité. Ce que la
    série retient autrement se déclare dans `CONVENTIONS_RVB`."""
    for regime, table in (("cancava", RVB_ARTISANS), ("organic", RVB_COMMERCANTS)):
        serie = _taux_annuels(regime)
        for annee in range(1973, 2006):
            _, sous_plafond, au_dela = _au_1er_janvier(table, annee)
            attendu = CONVENTIONS_RVB.get((regime, annee), sous_plafond / 100)
            assert serie[(annee, "taux_plafonne")] == pytest.approx(attendu, abs=1e-6), (
                regime, annee)
            assert serie.get((annee, "taux_deplafonne"), 0.0) == au_dela == 0.0
    rsi, general = _taux_annuels("rsi"), _taux_annuels("regime_general")
    for annee in range(2006, DERNIERE_ANNEE_RVB + 1):
        _, sous_plafond, au_dela = _au_1er_janvier(RVB_INDEPENDANTS, annee)
        if annee <= 2017:
            plafonne, totalite = rsi[(annee, "taux_plafonne")], rsi.get((annee, "taux_deplafonne"), 0.0)
        else:
            plafonne = general[(annee, "taux_plafonne_non_salarie")]
            totalite = general[(annee, "taux_deplafonne_non_salarie")]
        assert plafonne + totalite == pytest.approx(sous_plafond / 100, abs=1e-6), annee
        assert totalite == pytest.approx(au_dela / 100, abs=1e-6), annee


#: Les régimes complémentaires, des mêmes tables : le RCO des artisans, en
#: pour cent sous le plafond du régime, puis au-delà (une seule tranche avant
#: 2008, jusqu'à trois puis quatre plafonds de la sécurité sociale) ; la
#: cotisation au NRCO des commerçants, de 2004 à 2012 ; le RCI, depuis 2013.
RCO_ARTISANS = (
    ("1979-01-01", 4.40, None), ("1985-01-01", 4.50, None), ("1997-01-01", 4.90, None),
    ("1998-01-01", 5.30, None), ("1999-01-01", 5.70, None), ("2000-01-01", 6.00, None),
    ("2003-01-01", 6.20, None), ("2004-01-01", 6.70, None), ("2005-01-01", 7.00, None),
    ("2008-01-01", 7.00, 7.00), ("2009-01-01", 7.10, 7.50), ("2010-01-01", 7.20, 7.60),
)
NRCO_COMMERCANTS = (("2004-01-01", 3.50), ("2004-07-01", 4.50), ("2005-01-01", 6.50))
RCI = (("2013-01-01", 7.00, 8.00), ("2025-01-01", 8.10, 9.10))

#: Ce que les fiches portent autrement que la caisse : la valeur de la fiche,
#: et la raison.
ECARTS_COMPLEMENTAIRES = {
    ("rco_artisans", 2008): (
        (0.072, 0.076), "le décret n° 2007-1900 du 26 décembre 2007 réécrit D. 635-7 "
        "à 7,2 % et 7,6 % au 1er janvier 2008, mais son article 1er fixe, « par "
        "dérogation », 7 % et 7 % au titre de 2008 (III et IV), et 7,1 % et 7,5 % "
        "au titre de 2009 : la fiche, qui ne lit que l'article codifié, applique "
        "7,2 % et 7,6 % dès 2008. Un écart qui change les points de 2008 et de "
        "2009 : à la session du modèle"),
    ("rco_artisans", 2009): ((0.072, 0.076), "id."),
    ("nric", 2004): (
        (0.040,), "la fiche porte la moyenne de l'année, 3,5 % jusqu'en juin et "
        "4,5 % ensuite, et non le taux du 1er janvier"),
}


def test_les_taux_des_regimes_complementaires_des_independants_sont_ceux_de_la_caisse():
    """Le RCO des artisans (`rco_artisans`, 1979-2012), le NRCO des commerçants
    (`nric`, 2004-2012) et le RCI (`rci`, depuis 2013) cotisent, année par
    année, ce que la caisse publie ; le plafond propre du RCI, de 2013 à 2024,
    est celui du barème « Plafond de cotisations - Régime complémentaire des
    indépendants » (`ti_cotisation_plafond_cotisation_rci.aspx`). Ce que les
    fiches portent autrement se déclare dans `ECARTS_COMPLEMENTAIRES`, et
    l'écart qui change le calcul passe à la session du modèle."""
    for annee in range(1979, 2013):
        _, premiere, seconde = _au_1er_janvier(RCO_ARTISANS, annee)
        fiche = _taux_de_la_fiche("rco_artisans", annee)
        attendu = (premiere / 100,) if seconde is None else (premiere / 100, seconde / 100)
        if annee >= 2008:
            lu = (fiche["plafonnee"], fiche["tranche_1_4_pass"])
        else:
            (lu,) = [(taux,) for assiette, taux in fiche.items()
                     if assiette in ("plafonnee_3_pass", "plafonnee_4_pass")]
        if ("rco_artisans", annee) in ECARTS_COMPLEMENTAIRES:
            ecart, _ = ECARTS_COMPLEMENTAIRES[("rco_artisans", annee)]
            assert lu == pytest.approx(ecart) and lu != pytest.approx(attendu), annee
            continue
        assert lu == pytest.approx(attendu), annee
    for annee in range(2004, 2013):
        _, taux = _au_1er_janvier(NRCO_COMMERCANTS, annee)
        lu = (_taux_de_la_fiche("nric", annee)["plafonnee_3_pass"],)
        if ("nric", annee) in ECARTS_COMPLEMENTAIRES:
            assert lu == pytest.approx(ECARTS_COMPLEMENTAIRES[("nric", annee)][0]), annee
            assert lu != pytest.approx((taux / 100,)), annee
            continue
        assert lu == pytest.approx((taux / 100,)), annee
    for annee in range(2013, DERNIERE_ANNEE_RVB + 1):
        _, premiere, seconde = _au_1er_janvier(RCI, annee)
        fiche = _taux_de_la_fiche("rci", annee)
        assert (fiche["plafonnee"], fiche["tranche_1_4_pass"]) == pytest.approx(
            (premiere / 100, seconde / 100)), annee
    (premiere,) = [p for p in _fiche("rci")["periodes"]
                   if p["debut"] == 2013 and p["assiette"] == "plafonnee"]
    assert premiere["borne_haute_par_annee"] == PLAFOND_RCI_JUSQU_EN_2024


#: « Plafond de cotisations - Régime complémentaire des indépendants »
#: (`ti_cotisation_plafond_cotisation_rci.aspx`, version du 22 décembre 2025),
#: en euros. La caisse le publie encore pour 2025 (43 891 €) et 2026
#: (44 286 €), quand D. 635-7, depuis le décret n° 2024-688, arrête la
#: première tranche au plafond de la sécurité sociale : la fiche suit le texte
#: (`rci_seuil_premiere_tranche`).
PLAFOND_RCI_JUSQU_EN_2024 = {
    2013: 37032, 2014: 37513, 2015: 37513, 2016: 37546, 2017: 37546, 2018: 37846,
    2019: 37960, 2020: 38340, 2021: 38493, 2022: 38916, 2023: 40784, 2024: 42946,
}


# -- l'assiette minimale et le revenu qui valide un trimestre --------------------

MACRO = RACINE / "data" / "reference" / "macro"
LEGISLATION = RACINE / "data" / "reference" / "legislation"
FRANCS_PAR_EURO = 6.55957


def _serie_annuelle(chemin: Path, colonne: str) -> dict[int, float]:
    return {int(ligne["annee"]): float(ligne[colonne]) for ligne in _csv(chemin)}


def _arrondi(montant: float, pas: float = 1.0) -> float:
    """Arrondi au pas le plus proche, la moitié vers le haut, comme la caisse."""
    import math

    return math.floor(montant / pas + 0.5) * pas


#: « Assiette annuelle minimale des cotisations des travailleurs
#: indépendants » (`ti_cotisation_assiette_minimale_cotisation_bar.aspx`,
#: version du 23 décembre 2025) pour la retraite de base, depuis 2019, et la
#: table de l'ex-RSI qu'il joint (`ti_cotisation_assiette_minimale_cotisation.pdf`)
#: avant : en francs jusqu'en 2001, en euros ensuite. De 1983 à 1996, la table
#: donne un montant par semestre, le même pour l'un et l'autre.
ASSIETTE_MINIMALE_EN_FRANCS = {
    1973: 910, 1974: 1086, 1975: 1350, 1976: 1578, 1977: 1788, 1978: 2012, 1979: 2262,
    1980: 2586, 1981: 2958, 1982: 3630, 1983: 4058, 1984: 4556, 1985: 4872, 1986: 5208,
    1987: 5384, 1988: 5568, 1989: 5752, 1990: 5982, 1991: 6388, 1992: 6532, 1993: 6812,
    1994: 6966, 1995: 7112, 1996: 7396, 1997: 7582, 1998: 7886, 1999: 8044, 2000: 8144,
    2001: 8404,
}
ASSIETTE_MINIMALE_EN_EUROS = {
    2002: 1334, 2003: 1366, 2004: 1438, 2005: 1522, 2006: 1606, 2007: 1654, 2008: 1688,
    2009: 1742, 2010: 1772, 2011: 1800, 2012: 1910, 2013: 1944, 2014: 1971, 2015: 2929,
    2016: 4441, 2017: 4511, 2018: 4569, 2019: 4660, 2020: 4731, 2021: 4731, 2022: 4758,
    2023: 5072, 2024: 5243, 2025: 5346, 2026: 5409,
}

#: Ce que la série de l'assiette minimale (`assiette_minimale_independants.csv`)
#: ne porte pas comme la caisse : deux écarts qui changent le calcul — le
#: revenu porté au compte, et les trimestres validés —, à la session du modèle.
ECARTS_ASSIETTE_MINIMALE = {
    range(1973, 1985): (
        "la caisse applique 200 heures de Smic depuis 1973 ; la série commence en "
        "1985, à la première rédaction de D. 633-2 que porte l'index LEGI, et ne "
        "connaît pas de minimum avant"),
    range(2022, 2023): (
        "le décret n° 2022-1438 du 16 novembre 2022 (art. 1er) fixe pour 2022, « par "
        "dérogation aux articles D. 633-2 et D. 642-4 », une assiette d'au moins "
        "4 758 €, de quoi valider trois trimestres ; la série garde 11,5 % du "
        "plafond, 4 731 €, qui n'en valident que deux"),
}


def _assiette_minimale_de_la_serie(annee: int, smic: dict, plafond: dict) -> float | None:
    for ligne in _csv(LEGISLATION / "assiette_minimale_independants.csv"):
        if "artisan" not in ligne["statuts"].split():
            continue
        if int(ligne["debut"]) <= annee <= int(ligne["fin"] or 9999):
            if ligne["heures_smic"]:
                return float(ligne["heures_smic"]) * smic[annee]
            return float(ligne["part_pass"]) * plafond[annee]
    return None


def test_l_assiette_minimale_des_independants_est_celle_que_la_caisse_publie():
    """La règle de la série — 200 heures du Smic du 1er janvier jusqu'en 2011,
    5,25 %, 7,7 % puis 11,5 % du plafond de 2012 à 2022, 450 heures depuis
    2023 —, appliquée au Smic (`smic_horaire.csv`) et au plafond
    (`plafond_securite_sociale.csv`) du dépôt, redonne à l'unité près ce que
    la caisse publie pour l'artisan et le commerçant, de 1985 à 2026. Les
    écarts qui restent se déclarent dans `ECARTS_ASSIETTE_MINIMALE`."""
    smic = _serie_annuelle(MACRO / "smic_horaire.csv", "smic_horaire")
    plafond = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")
    publiees = {**{annee: montant / FRANCS_PAR_EURO
                   for annee, montant in ASSIETTE_MINIMALE_EN_FRANCS.items()},
                **ASSIETTE_MINIMALE_EN_EUROS}
    ecarts = {annee: raison for annees, raison in ECARTS_ASSIETTE_MINIMALE.items()
              for annee in annees}
    for annee, publiee in sorted(publiees.items()):
        calculee = _assiette_minimale_de_la_serie(annee, smic, plafond)
        if annee < 2002:
            concorde = calculee is not None and _arrondi(
                calculee * FRANCS_PAR_EURO) == ASSIETTE_MINIMALE_EN_FRANCS[annee]
        else:
            concorde = calculee is not None and _arrondi(calculee) == publiee
        assert concorde != (annee in ecarts), (annee, calculee, publiee, ecarts.get(annee))


#: « Revenu validant un trimestre » des indépendants
#: (`ti_prestation_revenu_validant_un_ trimestre_montant_cotisation_bar.aspx`,
#: version du 15 mai 2026), depuis 2019, et la table de l'ex-RSI qu'il joint
#: pour 2014 à 2018 : le revenu qui valide un trimestre, en euros.
REVENU_VALIDANT_UN_TRIMESTRE = {
    2014: 1429.50, 2015: 1441.50, 2016: 1450.50, 2017: 1464.00, 2018: 1482.00,
    2019: 1504.50, 2020: 1522.50, 2021: 1537.50, 2022: 1585.50, 2023: 1690.50,
    2024: 1747.50, 2025: 1782.00, 2026: 1803.00,
}


def test_le_revenu_qui_valide_un_trimestre_d_independant_est_celui_de_la_caisse():
    """L'indépendant valide un trimestre par 150 heures du Smic du 1er
    janvier depuis 2014 (`validation_trimestres.csv`, R. 351-9) : la règle,
    appliquée au Smic du dépôt, redonne au centime ce que la caisse publie."""
    smic = _serie_annuelle(MACRO / "smic_horaire.csv", "smic_horaire")
    heures = {int(ligne["annee"]): float(ligne["heures"])
              for ligne in _csv(LEGISLATION / "validation_trimestres.csv")}
    for annee, publie in REVENU_VALIDANT_UN_TRIMESTRE.items():
        en_vigueur = heures[max(debut for debut in heures if debut <= annee)]
        assert _arrondi(en_vigueur * smic[annee], 0.01) == pytest.approx(publie), annee


# -- les micro-entrepreneurs ----------------------------------------------------

#: « Taux de cotisations globaux des micro-entrepreneurs »
#: (`micro_entrepreneur_taux_cotisation_bar.aspx`, version du 10 novembre 2025)
#: et « Taux de répartition par risques et contributions »
#: (`micro_entrepreneur_taux_repartition_risque.aspx`, même date) : par
#: activité et par date d'effet, le taux global, et les parts de la retraite de
#: base et de la complémentaire, en pour cent. La caisse ne publie la
#: répartition que depuis le 1er octobre 2022 ; avant, `micro_social.yaml` la
#: tient de la circulaire Cnav n° 2025-20.
MICRO_ENTREPRENEURS = {
    "vente": (("2018-01", 12.8, None, None), ("2022-10", 12.3, 41.80, 16.50),
              ("2026-01", 12.3, 43.45, 19.75)),
    "services": (("2018-01", 22.0, None, None), ("2022-10", 21.2, 41.80, 16.50),
                 ("2026-01", 21.2, 43.45, 19.75)),
    "liberal": (("2018-01", 22.0, None, None), ("2022-10", 21.1, 55.50, 0.0),
                ("2024-07", 23.1, 50.75, 7.85), ("2025-01", 24.6, 47.60, 13.0),
                ("2026-01", 25.6, 46.40, 21.0)),
}


def test_les_taux_des_micro_entrepreneurs_sont_ceux_de_la_caisse():
    """`micro_social.yaml` porte, pour la vente, les services commerciaux et
    les libéraux de l'Assurance retraite, les taux globaux et les parts de
    retraite que la caisse publie, à leurs dates d'effet ; ses lignes de 2025,
    qui ne changent que le taux de base, gardent les parts de 2022. Les seuils
    de chiffre d'affaires de 2017 à 2019 sont ceux que la caisse publie."""
    import yaml

    micro = yaml.safe_load((LEGISLATION / "micro_social.yaml").read_text(encoding="utf-8"))
    for activite, publies in MICRO_ENTREPRENEURS.items():
        lignes = micro["versions"][activite]
        for debut, globale, base, complementaire in publies:
            (ligne,) = [ligne for ligne in lignes if ligne["debut"] == debut]
            assert ligne["taux_global"] == pytest.approx(globale / 100), (activite, debut)
            if base is not None:
                assert ligne["part_base"] == pytest.approx(base / 100), (activite, debut)
                assert ligne["part_complementaire"] == pytest.approx(
                    complementaire / 100), (activite, debut)
        dates = [ligne["debut"] for ligne in lignes]
        for ligne in lignes:
            if ligne["debut"] not in {debut for debut, *_ in publies}:
                precedente = lignes[dates.index(ligne["debut"]) - 1]
                assert ligne["debut"] == "2025-01" and (
                    ligne["taux_global"], ligne["part_base"]) == (
                    precedente["taux_global"], precedente["part_base"]), (activite, ligne)
    assert micro["seuils"] == SEUILS_MICRO_ENTREPRENEURS


#: « Chiffre d'affaire des micro-entrepreneurs validant un trimestre »
#: (`micro_entrepreneur_chiffre_affaire_validant_un_trimestre_montant_bar.aspx`,
#: version du 1er juillet 2026), source Urssaf Caisse nationale : le chiffre
#: d'affaires qui valide un, deux, trois et quatre trimestres, en euros.
SEUILS_MICRO_ENTREPRENEURS = {
    "vente": {2017: [3510, 6305, 9120, 20195], 2018: [4085, 7185, 10250, 20430],
              2019: [4137, 7286, 10426, 20740]},
    "services": {2017: [2020, 3635, 5245, 11715], 2018: [2375, 4185, 5975, 11850],
                 2019: [2412, 4239, 6071, 12030]},
    "liberal": {2017: [2320, 4190, 6090, 8875], 2018: [2835, 4990, 7150, 9550],
                2019: [2880, 5062, 7266, 9675]},
}


# -- le pourcentage de minoration ------------------------------------------------

#: « Pourcentage de minoration appliqué au taux plein - Taux réduit »
#: (`retraite_personnelle_pourcentage_minoration_applique_taux_plein_bar.aspx`,
#: version du 25 juillet 2024) : par génération, le coefficient de minoration
#: par trimestre manquant, en pour cent, et le taux de la retraite pour un à
#: vingt trimestres manquants et plus, en pour cent. Deux cellules sont des
#: coquilles de la caisse (`COQUILLES_MINORATION`).
MINORATION = {
    "1953+": (1.25, (
        49.375, 48.750, 48.125, 47.500, 46.875, 46.250, 45.625,
        45.000, 44.375, 43.750, 43.125, 42.500, 41.875, 41.250,
        40.625, 40.000, 39.375, 38.750, 38.125, 37.500,
    )),
    "1952": (1.375, (
        49.3125, 48.6250, 47.9375, 47.2500, 46.5625, 45.8750, 45.1875,
        44.5000, 43.8125, 43.1250, 42.4375, 41.7500, 41.0625, 40.3750,
        39.6875, 39.0000, 38.3125, 37.6250, 36.9375, 36.2500,
    )),
    "1951": (1.5, (
        49.25, 48.50, 47.75, 47.00, 46.25, 45.50, 44.75,
        44.00, 43.25, 42.50, 41.75, 41.00, 40.25, 39.50,
        38.75, 38.00, 37.25, 36.50, 35.75, 35.00,
    )),
    "1950": (1.625, (
        49.1875, 48.3750, 47.5625, 46.7500, 45.9375, 45.1250, 44.3125,
        43.5000, 42.6875, 41.8750, 41.0625, 40.2500, 39.4375, 38.6250,
        37.8125, 37.0000, 36.1875, 35.3750, 34.5625, 33.7500,
    )),
    "1949": (1.75, (
        49.125, 48.250, 47.375, 46.500, 45.625, 44.750, 43.875,
        43.000, 42.125, 41.250, 40.375, 39.500, 38.625, 37.750,
        36.875, 36.000, 35.125, 34.250, 33.375, 32.500,
    )),
    "1948": (1.875, (
        49.0625, 48.1250, 47.1875, 46.2500, 45.3125, 44.3750, 43.4375,
        42.5000, 41.5625, 40.6250, 29.6875, 38.7500, 37.8125, 36.8750,
        35.9375, 35.0000, 34.0625, 33.1250, 32.1875, 31.2500,
    )),
    "1947": (2, (49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30)),
    "1946": (2.125, (
        48.9375, 47.8750, 46.8125, 45.7500, 44.6875, 43.6250, 45.5625,
        41.5000, 40.4375, 39.3750, 38.3125, 37.2500, 36.1875, 35.1250,
        34.0625, 33.0000, 31.9375, 30.8750, 29.8125, 28.7500,
    )),
    "1945": (2.25, (
        48.875, 47.750, 46.625, 45.500, 44.375, 43.250, 42.125,
        41.000, 39.875, 38.750, 37.625, 36.500, 35.375, 34.250,
        33.125, 32.000, 30.875, 29.750, 28.625, 27.500,
    )),
    "1944": (2.375, (
        48.8125, 47.6250, 46.4375, 45.2500, 44.0625, 42.8750, 41.6875,
        40.5000, 39.3125, 38.1250, 36.9375, 35.7500, 34.5625, 33.3750,
        32.1875, 31.0000, 29.8125, 28.6250, 27.4375, 26.2500,
    )),
    "-1943": (2.50, (
        48.75, 47.50, 46.25, 45.00, 43.75, 42.50, 41.25,
        40.00, 38.75, 37.50, 36.25, 35.00, 33.75, 32.50,
        31.25, 30.00, 28.75, 27.50, 26.25, 25.00,
    )),
}
#: Les cellules du barème que sa formule dément, le taux plein (50 %) moins le
#: coefficient par trimestre : (génération, trimestres manquants) → ce que la
#: caisse imprime, et ce que la formule donne.
COQUILLES_MINORATION = {("1948", 11): (29.6875, 39.6875), ("1946", 7): (45.5625, 42.5625)}


def _generations(cle: str) -> range:
    if cle.endswith("+"):
        return range(int(cle[:-1]), 1977)
    if cle.startswith("-"):
        return range(1900, int(cle[1:]) + 1)
    return range(int(cle), int(cle) + 1)


def test_le_pourcentage_de_minoration_est_celui_de_la_caisse():
    """Le coefficient de minoration par génération
    (`coefficient_minoration.csv`, R. 351-27) est celui que la caisse publie,
    de 2,5 % avant 1944 à 1,25 % depuis 1953, et le taux qu'elle sert, de un à
    vingt trimestres manquants, est le taux plein moins ce coefficient par
    trimestre : la formule de la série, aux deux coquilles près de son
    tableau."""
    serie = {int(ligne["generation"]): float(ligne["coefficient"])
             for ligne in _csv(LEGISLATION / "coefficient_minoration.csv")}
    for cle, (coefficient, taux) in MINORATION.items():
        for generation in _generations(cle):
            if generation in serie:
                assert serie[generation] == pytest.approx(coefficient / 100), generation
        assert len(taux) == 20, cle
        for manquants, publie in enumerate(taux, start=1):
            formule = 50 * (1 - coefficient / 100 * manquants)
            if (cle, manquants) in COQUILLES_MINORATION:
                assert (publie, formule) == pytest.approx(
                    COQUILLES_MINORATION[(cle, manquants)]), (cle, manquants)
                continue
            assert publie == pytest.approx(formule), (cle, manquants)
    assert min(serie) <= 1943 and max(serie) >= 1953
