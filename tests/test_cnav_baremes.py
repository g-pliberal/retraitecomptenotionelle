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


def _en_vigueur(periodes: tuple, jour: str) -> tuple:
    """La période en vigueur le jour dit : la dernière qui a commencé ce
    jour-là ou avant."""
    return [periode for periode in periodes if periode[0] <= jour][-1]


def _au_1er_janvier(periodes: tuple, annee: int) -> tuple:
    return _en_vigueur(periodes, f"{annee}-01-01")


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


# -- le salaire plafond, et la base des points de retraite des commerçants -------

#: « Salaire plafond soumis à cotisations » (`salaire_plafond_soumis_cotisation_bar.aspx`,
#: version du 5 janvier 2026) : chaque relèvement, du 1er juillet 1930 au
#: 1er janvier 2026, et le plafond qu'il fixe, ramené à l'année — le barème le
#: donne à l'année jusqu'en 1946, au mois ensuite —, en anciens francs jusqu'en
#: 1959, en francs jusqu'en 2001, en euros depuis.
PLAFOND = (
    ("1930-07-01", 10800), ("1936-01-01", 12000), ("1937-01-01", 15000),
    ("1938-07-01", 18000), ("1941-04-01", 30000), ("1942-01-01", 42000),
    ("1944-01-01", 48000), ("1944-09-01", 60000), ("1945-04-01", 120000),
    ("1946-10-01", 12 * 12500), ("1947-10-01", 12 * 17000), ("1948-03-01", 12 * 19000),
    ("1949-03-01", 12 * 22000), ("1951-01-01", 12 * 27000), ("1951-10-01", 12 * 34000),
    ("1952-04-01", 12 * 38000), ("1955-10-01", 12 * 44000), ("1958-01-01", 12 * 50000),
    ("1959-01-01", 12 * 55000),
    ("1960-01-01", 12 * 550), ("1960-07-01", 12 * 590), ("1961-01-01", 12 * 600),
    ("1961-04-01", 12 * 700), ("1962-01-01", 12 * 800), ("1963-01-01", 12 * 870),
    ("1964-01-01", 12 * 950), ("1965-01-01", 12 * 1020), ("1966-01-01", 12 * 1080),
    ("1967-01-01", 12 * 1140), ("1968-01-01", 12 * 1200), ("1969-01-01", 12 * 1360),
    ("1970-01-01", 12 * 1500), ("1971-01-01", 12 * 1650), ("1972-01-01", 12 * 1830),
    ("1973-01-01", 12 * 2040), ("1974-01-01", 12 * 2320), ("1975-01-01", 12 * 2750),
    ("1976-01-01", 12 * 3160), ("1977-01-01", 12 * 3610), ("1978-01-01", 12 * 4000),
    ("1979-01-01", 12 * 4470), ("1980-01-01", 12 * 5010), ("1981-01-01", 12 * 5730),
    ("1982-01-01", 12 * 6590), ("1982-07-01", 12 * 7080), ("1983-01-01", 12 * 7410),
    ("1983-07-01", 12 * 7870), ("1984-01-01", 12 * 8110), ("1984-07-01", 12 * 8490),
    ("1985-01-01", 12 * 8730), ("1985-07-01", 12 * 9060), ("1986-01-01", 12 * 9220),
    ("1986-07-01", 12 * 9480), ("1987-01-01", 12 * 9630), ("1987-07-01", 12 * 9840),
    ("1988-01-01", 12 * 9950), ("1988-07-01", 12 * 10110), ("1989-01-01", 12 * 10340),
    ("1989-07-01", 12 * 10540), ("1990-01-01", 12 * 10800), ("1990-07-01", 12 * 11040),
    ("1991-01-01", 12 * 11340), ("1991-07-01", 12 * 11620), ("1992-01-01", 12 * 11870),
    ("1992-07-01", 12 * 12150), ("1993-01-01", 12 * 12360), ("1993-07-01", 12 * 12610),
    ("1994-01-01", 12 * 12680), ("1994-07-01", 12 * 12840), ("1995-01-01", 12 * 12930),
    ("1995-07-01", 12 * 13060), ("1996-01-01", 12 * 13330), ("1996-07-01", 12 * 13540),
    ("1997-01-01", 12 * 13720), ("1998-01-01", 12 * 14090), ("1999-01-01", 12 * 14470),
    ("2000-01-01", 12 * 14700), ("2001-01-01", 12 * 14950),
    ("2002-01-01", 12 * 2352), ("2003-01-01", 12 * 2432), ("2004-01-01", 12 * 2476),
    ("2005-01-01", 12 * 2516), ("2006-01-01", 12 * 2589), ("2007-01-01", 12 * 2682),
    ("2008-01-01", 12 * 2773), ("2009-01-01", 12 * 2859), ("2010-01-01", 12 * 2885),
    ("2011-01-01", 12 * 2946), ("2012-01-01", 12 * 3031), ("2013-01-01", 12 * 3086),
    ("2014-01-01", 12 * 3129), ("2015-01-01", 12 * 3170), ("2016-01-01", 12 * 3218),
    ("2017-01-01", 12 * 3269), ("2018-01-01", 12 * 3311), ("2019-01-01", 12 * 3377),
    ("2020-01-01", 12 * 3428), ("2023-01-01", 12 * 3666), ("2024-01-01", 12 * 3864),
    ("2025-01-01", 12 * 3925), ("2026-01-01", 12 * 4005),
)


def _en_euros(montant: float, annee: int) -> float:
    """Un montant de l'année, en euros : l'ancien franc vaut un centième de
    franc, et le franc 1 / 6,55957 euro."""
    if annee >= 2002:
        return montant
    return montant / FRANCS_PAR_EURO / (100 if annee < 1960 else 1)


def _plafond_de_l_annee(annee: int) -> float:
    """Ce que le plafond fait sur l'année, mois par mois, en euros."""
    return sum(_en_euros(_en_vigueur(PLAFOND, f"{annee}-{mois:02d}-01")[1], annee) / 12
               for mois in range(1, 13))


def test_le_plafond_de_la_serie_est_le_salaire_plafond_de_la_caisse():
    """Le plafond annuel de la série (`plafond_securite_sociale.csv`) est,
    de 1931 à 2026, ce que fait sur l'année, mois par mois, le salaire plafond
    que la caisse date relèvement par relèvement — les deux semestres de 1982 à
    1996, les mois de 1945 à 1961 —, à l'euro près : la série arrondit à l'euro
    ses années d'avant 1963."""
    serie = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")
    for annee in range(1931, 2027):
        assert serie[annee] == pytest.approx(_plafond_de_l_annee(annee), abs=0.5), annee


#: « Base de calcul des points RVB - Commerçant »
#: (`ti_prestation_base_calcul_point_fictif_commercant_bar.aspx`, version du
#: 5 janvier 2026) depuis 2020, et la table de l'ex-RSI qu'il joint pour 1973 à
#: 2019 (`ti_prestation_base_calcul_point_fictif_commercant.pdf`) : « 1/20e
#: PASS », en francs jusqu'en 2001, en euros ensuite.
BASE_POINTS_COMMERCANTS_EN_FRANCS = {
    1973: 1224, 1974: 1392, 1975: 1650, 1976: 1896, 1977: 2166, 1978: 2400, 1979: 2682,
    1980: 3006, 1981: 3438, 1982: 3954, 1983: 4446, 1984: 4866, 1985: 5238, 1986: 5532,
    1987: 5778, 1988: 5970, 1989: 6204, 1990: 6480, 1991: 6804, 1992: 7122, 1993: 7416,
    1994: 7608, 1995: 7758, 1996: 7998, 1997: 8232, 1998: 8454, 1999: 8682, 2000: 8820,
    2001: 8970,
}
BASE_POINTS_COMMERCANTS_EN_EUROS = {
    2002: 1411.20, 2003: 1459.20, 2004: 1485.60, 2005: 1509.60, 2006: 1553.40,
    2007: 1609.20, 2008: 1663.80, 2009: 1715.40, 2010: 1731.00, 2011: 1767.60,
    2012: 1818.60, 2013: 1851.60, 2014: 1877.40, 2015: 1902.00, 2016: 1930.80,
    2017: 1961.40, 2018: 1986.60, 2019: 2026.20, 2020: 2056.80, 2021: 2056.80,
    2022: 2056.80, 2023: 2199.60, 2024: 2318.40, 2025: 2355.00, 2026: 2403.00,
}


def test_un_point_de_retraite_du_commercant_vaut_un_vingtieme_du_plafond():
    """La fiche des commerçants d'avant 1973 (`organic_avant_1973`) ouvre un
    point par vingtième du plafond, vingt au plafond (`points_maximum`), par
    l'équivalence de D. 634-8 : la base de calcul des points que la caisse
    publie de 1973 à 2026 est ce vingtième, celui du plafond du 1er janvier —
    les années de deux plafonds, de 1982 à 1996, le plafond de juillet n'ouvre
    pas de point de plus."""
    (periode,) = [p for p in _fiche("organic_avant_1973")["periodes"] if p["debut"] == 1949]
    assert periode["points_maximum"] == 20 and periode["assiette"] == "plafonnee"
    for annee, base in BASE_POINTS_COMMERCANTS_EN_FRANCS.items():
        assert _au_1er_janvier(PLAFOND, annee)[1] / periode["points_maximum"] == base, annee
    for annee, base in BASE_POINTS_COMMERCANTS_EN_EUROS.items():
        assert _au_1er_janvier(PLAFOND, annee)[1] / periode["points_maximum"] == pytest.approx(
            base), annee


#: « Plafond d'assujettissement avant 1947 »
#: (`plafond_assujettissement_securite_sociale_avant_1947_bar.aspx`, version du
#: 25 juillet 2024) : la rémunération annuelle au-delà de laquelle le salarié
#: n'était pas assuré, en anciens francs, à chaque date d'effet.
PLAFOND_ASSUJETTISSEMENT = (
    ("1930-07-01", 15000), ("1937-01-01", 21000), ("1938-07-01", 30000),
    ("1942-01-01", 42000), ("1944-01-01", 48000), ("1944-09-01", 60000),
    ("1945-04-01", 120000),
)


def test_le_plafond_d_assujettissement_d_avant_1947_est_celui_de_la_caisse():
    """`plafond_assujettissement_avant_1947.csv`, tiré de ce barème le
    18 octobre 2026, en porte chaque année ce que fait le plafond
    mois par mois, en euros — 1930 au montant de juillet, l'année n'ayant pas
    commencé avant."""
    serie = _serie_annuelle(LEGISLATION / "plafond_assujettissement_avant_1947.csv", "valeur")
    assert sorted(serie) == list(range(1930, 1947))
    for annee in range(1930, 1947):
        mois = [_en_vigueur(PLAFOND_ASSUJETTISSEMENT, max("1930-07-01", f"{annee}-{m:02d}-01"))[1]
                for m in range(1, 13)]
        assert serie[annee] == pytest.approx(sum(mois) / 12 / 100 / FRANCS_PAR_EURO), annee



# -- le Smic --------------------------------------------------------------------

#: « Smic horaire » (`smic_smig_smic_bar.aspx`, version du 11 juin 2026) : chaque
#: relèvement depuis la création du Smic, le 1er mars 1970, hors Mayotte, en
#: francs jusqu'en 2001, en euros depuis.
SMIC_HORAIRE = (
    ("1970-03-01", 3.36, "F"), ("1970-07-01", 3.50, "F"), ("1971-01-01", 3.63, "F"),
    ("1971-04-01", 3.68, "F"), ("1971-07-01", 3.85, "F"), ("1971-12-01", 3.94, "F"),
    ("1972-05-01", 4.10, "F"), ("1972-07-01", 4.30, "F"), ("1972-11-01", 4.55, "F"),
    ("1973-02-01", 4.64, "F"), ("1973-07-01", 5.20, "F"), ("1973-10-01", 5.32, "F"),
    ("1973-12-01", 5.43, "F"), ("1974-03-01", 5.60, "F"), ("1974-05-01", 5.95, "F"),
    ("1974-07-01", 6.40, "F"), ("1974-09-01", 6.55, "F"), ("1974-12-01", 6.75, "F"),
    ("1975-03-01", 6.95, "F"), ("1975-06-01", 7.12, "F"), ("1975-07-01", 7.55, "F"),
    ("1975-10-01", 7.71, "F"), ("1976-01-01", 7.89, "F"), ("1976-04-01", 8.08, "F"),
    ("1976-07-01", 8.58, "F"), ("1976-10-01", 8.76, "F"), ("1976-12-01", 8.94, "F"),
    ("1977-04-01", 9.14, "F"), ("1977-06-01", 9.34, "F"), ("1977-07-01", 9.58, "F"),
    ("1977-10-01", 9.79, "F"), ("1977-12-01", 10.06, "F"), ("1978-05-01", 10.45, "F"),
    ("1978-07-01", 10.85, "F"), ("1978-09-01", 11.07, "F"), ("1978-12-01", 11.31, "F"),
    ("1979-04-01", 11.60, "F"), ("1979-07-01", 12.15, "F"), ("1979-09-01", 12.42, "F"),
    ("1979-12-01", 12.93, "F"), ("1980-03-01", 13.37, "F"), ("1980-05-01", 13.66, "F"),
    ("1980-07-01", 14.00, "F"), ("1980-09-01", 14.29, "F"), ("1980-12-01", 14.79, "F"),
    ("1981-03-01", 15.20, "F"), ("1981-06-01", 16.72, "F"), ("1981-09-01", 17.34, "F"),
    ("1981-11-01", 17.76, "F"), ("1982-01-01", 18.15, "F"), ("1982-03-01", 18.62, "F"),
    ("1982-05-01", 19.03, "F"), ("1982-07-01", 19.64, "F"), ("1982-12-01", 20.29, "F"),
    ("1983-03-01", 21.02, "F"), ("1983-06-01", 21.65, "F"), ("1983-07-01", 21.89, "F"),
    ("1983-10-01", 22.33, "F"), ("1984-01-01", 22.78, "F"), ("1984-05-01", 23.56, "F"),
    ("1984-07-01", 23.84, "F"), ("1984-11-01", 24.36, "F"), ("1985-04-01", 24.90, "F"),
    ("1985-05-01", 25.54, "F"), ("1985-07-01", 26.04, "F"), ("1986-06-01", 26.59, "F"),
    ("1986-07-01", 26.92, "F"), ("1987-03-01", 27.57, "F"), ("1987-07-01", 27.84, "F"),
    ("1988-06-01", 28.48, "F"), ("1988-07-01", 28.76, "F"), ("1989-03-01", 29.36, "F"),
    ("1989-07-01", 29.91, "F"), ("1990-04-01", 30.51, "F"), ("1990-07-01", 31.28, "F"),
    ("1990-12-01", 31.94, "F"), ("1991-07-01", 32.66, "F"), ("1992-03-01", 33.31, "F"),
    ("1992-07-01", 34.06, "F"), ("1993-07-01", 34.83, "F"), ("1994-07-01", 35.56, "F"),
    ("1995-07-01", 36.98, "F"), ("1996-05-01", 37.72, "F"), ("1996-07-01", 37.91, "F"),
    ("1997-07-01", 39.43, "F"), ("1998-07-01", 40.22, "F"), ("1999-07-01", 40.72, "F"),
    ("2000-07-01", 42.02, "F"), ("2001-07-01", 43.72, "F"), ("2002-01-01", 6.67, "€"),
    ("2002-07-01", 6.83, "€"), ("2003-07-01", 7.19, "€"), ("2004-07-01", 7.61, "€"),
    ("2005-07-01", 8.03, "€"), ("2006-07-01", 8.27, "€"), ("2007-07-01", 8.44, "€"),
    ("2008-05-01", 8.63, "€"), ("2008-07-01", 8.71, "€"), ("2009-07-01", 8.82, "€"),
    ("2010-01-01", 8.86, "€"), ("2011-01-01", 9.00, "€"), ("2011-12-01", 9.19, "€"),
    ("2012-01-01", 9.22, "€"), ("2012-07-01", 9.40, "€"), ("2013-01-01", 9.43, "€"),
    ("2014-01-01", 9.53, "€"), ("2015-01-01", 9.61, "€"), ("2016-01-01", 9.67, "€"),
    ("2017-01-01", 9.76, "€"), ("2018-01-01", 9.88, "€"), ("2019-01-01", 10.03, "€"),
    ("2020-01-01", 10.15, "€"), ("2021-01-01", 10.25, "€"), ("2021-10-01", 10.48, "€"),
    ("2022-01-01", 10.57, "€"), ("2022-05-01", 10.85, "€"), ("2022-08-01", 11.07, "€"),
    ("2023-01-01", 11.27, "€"), ("2023-05-01", 11.52, "€"), ("2024-01-01", 11.65, "€"),
    ("2024-11-01", 11.88, "€"), ("2025-01-01", 11.88, "€"), ("2026-01-01", 12.02, "€"),
    ("2026-06-01", 12.31, "€"),
)

#: « Smic mensuel » (`smic_smig_smic_mensuel_bar.aspx`, même date), hors
#: Mayotte, depuis le 1er juillet 2005 : le Smic horaire fois 151,67 heures.
SMIC_MENSUEL = (
    ("2005-07-01", 1217.88), ("2006-07-01", 1254.28), ("2007-07-01", 1280.07), ("2008-05-01", 1308.88),
    ("2008-07-01", 1321.02), ("2009-07-01", 1337.70), ("2010-01-01", 1343.77), ("2011-01-01", 1365.00),
    ("2011-12-01", 1393.82), ("2012-01-01", 1398.37), ("2012-07-01", 1425.67), ("2013-01-01", 1430.22),
    ("2014-01-01", 1445.38), ("2015-01-01", 1457.52), ("2016-01-01", 1466.62), ("2017-01-01", 1480.27),
    ("2018-01-01", 1498.47), ("2019-01-01", 1521.22), ("2020-01-01", 1539.42), ("2021-01-01", 1554.58),
    ("2021-10-01", 1589.47), ("2022-01-01", 1603.12), ("2022-05-01", 1645.58), ("2022-08-01", 1678.95),
    ("2023-01-01", 1709.28), ("2023-05-01", 1747.20), ("2024-01-01", 1766.92), ("2024-11-01", 1801.80),
    ("2025-01-01", 1801.80), ("2026-01-01", 1823.03), ("2026-06-01", 1867.02),
)


def test_le_smic_de_la_serie_est_celui_de_la_caisse():
    """Le Smic horaire de la série (`smic_horaire.csv`), celui du 1er janvier
    qui valide les trimestres, est celui que la caisse publie, de 1971 à 2026 ;
    le Smic annuel (`smic_annuel.csv`, de l'INSEE) est, de 2006 à 2025, ce que
    font sur l'année les Smic mensuels de la caisse, au centime d'arrondi
    près."""
    horaire = _serie_annuelle(MACRO / "smic_horaire.csv", "smic_horaire")
    for annee in range(1971, 2027):
        _, montant, unite = _au_1er_janvier(SMIC_HORAIRE, annee)
        en_euros = montant / FRANCS_PAR_EURO if unite == "F" else montant
        assert horaire[annee] == pytest.approx(en_euros, abs=5e-6), annee
    annuel = _serie_annuelle(MACRO / "smic_annuel.csv", "smic_annuel")
    for annee in range(2006, 2026):
        de_la_caisse = sum(_en_vigueur(SMIC_MENSUEL, f"{annee}-{mois:02d}-01")[1]
                           for mois in range(1, 13))
        assert annuel[annee] == pytest.approx(de_la_caisse, abs=0.1), annee


# -- les dix éditions des coefficients de revalorisation des salaires -----------


def _recuperateur(nom: str):
    import importlib.util
    import sys

    dossier = RACINE / "scripts" / "fetch"
    if str(dossier) not in sys.path:
        sys.path.insert(0, str(dossier))
    specification = importlib.util.spec_from_file_location(nom, dossier / f"{nom}.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_une_edition_du_bareme_des_coefficients_se_lit_salaires_seuls():
    """Une édition du barème range ses coefficients sous des titres : ceux
    des salaires, depuis 1947, et ceux des cotisations d'avant 1947, que le
    modèle, qui porte des salaires, ne lit pas. Une cellule écrit les milliers
    avec une espace, porte parfois une espace insécable ou un caractère de
    largeur nulle."""
    module = _recuperateur("cnav_revalorisation_salaires")
    contenu = "".join((
        "<h2>Coefficients applicables aux salaires de 1997 à 2021</h2><table><tbody>",
        "<tr><td>2023</td><td>1,053</td></tr><tr><td>​2022</td><td>​1,103</td></tr>",
        "</tbody></table><h2>Coefficients applicables aux salaires de 1947 à 1962</h2>",
        "<table><tbody><tr><td align=\"center\">1947</td><td>165,572&nbsp;</td></tr></tbody></table>",
        "<h2>Coefficients applicables aux cotisations avant 1947</h2><table><tbody>",
        "<tr><td>1946</td><td>1 771,341</td></tr></tbody></table>"))
    assert module.coefficients_du_bareme(contenu) == {2023: 1.053, 2022: 1.103, 1947: 165.572}


def test_une_edition_du_bareme_qui_contredit_sa_circulaire_arrete_l_ecriture():
    """Chaque édition du barème (`BAREMES`, une par date d'effet) redit la
    colonne de sa circulaire, depuis 1947 : une valeur qui s'en écarte arrête
    l'écriture, sauf la coquille déclarée (`COQUILLES_DES_BAREMES`) — qui se
    retire quand la caisse la corrige."""
    module = _recuperateur("cnav_revalorisation_salaires")
    assert set(module.BAREMES) == {effet for effet, _ in module.CIRCULAIRES}
    colonnes = {"2024-01-01": {1946: 212.561, 1955: 43.054, 2023: 1.053}}
    assert module.confronter_aux_baremes(
        colonnes, {"2024-01-01": {1955: 43.054, 2023: 1.053}}, coquilles={}) == []
    griefs = module.confronter_aux_baremes(
        colonnes, {"2024-01-01": {1955: 40.887, 2023: 1.053}}, coquilles={})
    assert griefs and "1955" in griefs[0] and "40.887" in griefs[0]
    coquilles = {("2024-01-01", 1955): 40.887}
    assert module.confronter_aux_baremes(
        colonnes, {"2024-01-01": {1955: 40.887, 2023: 1.053}}, coquilles=coquilles) == []
    griefs = module.confronter_aux_baremes(
        colonnes, {"2024-01-01": {1955: 43.054, 2023: 1.053}}, coquilles=coquilles)
    assert griefs and "corrig" in griefs[0]
    griefs = module.confronter_aux_baremes(
        colonnes, {"2024-01-01": {2023: 1.053}}, coquilles={})
    assert griefs and "1955" in griefs[0]
    assert module.COQUILLES_DES_BAREMES == {("2024-01-01", 1955): 40.887}


# -- la majoration pour conjoint à charge ----------------------------------------

#: « Majoration pour conjoint à charge - Montant » (`ancienne_prestation_mc_montant_bar.aspx`,
#: version du 7 janvier 2026) : chaque montant annuel à sa date d'effet, en
#: anciens francs jusqu'en 1959, en francs jusqu'en 2001, en euros depuis.
MAJORATION_CONJOINT = (
    ("1948-07-01", 14500, "AF"), ("1948-10-01", 19200, "AF"), ("1949-04-01", 19500, "AF"),
    ("1950-01-01", 22500, "AF"), ("1951-01-01", 26000, "AF"), ("1951-10-01", 29900, "AF"),
    ("1954-01-01", 32900, "AF"), ("1956-01-01", 36190, "AF"), ("1960-01-01", 361.90, "F"),
    ("1962-04-01", 600, "F"), ("1963-07-01", 700, "F"), ("1964-01-01", 900, "F"),
    ("1964-11-01", 1000, "F"), ("1965-07-01", 1100, "F"), ("1966-01-01", 1150, "F"),
    ("1966-07-01", 1250, "F"), ("1967-01-01", 1300, "F"), ("1967-10-01", 1400, "F"),
    ("1968-01-01", 1450, "F"), ("1968-07-01", 1550, "F"), ("1969-10-01", 1650, "F"),
    ("1970-10-01", 1750, "F"), ("1971-10-01", 1850, "F"), ("1972-10-01", 2100, "F"),
    ("1973-07-01", 2250, "F"), ("1974-01-01", 2450, "F"), ("1974-07-01", 3000, "F"),
    ("1975-01-01", 3250, "F"), ("1975-04-01", 3500, "F"), ("1976-01-01", 3750, "F"),
    ("1976-07-01", 4000, "F"), ("2002-01-01", 609.80, "€"),
)


def test_la_majoration_pour_conjoint_a_charge_a_les_montants_de_la_caisse():
    """Chaque version de la fiche `majoration_conjoint_a_charge` qui porte des
    montants porte ceux de la caisse, en euros, à leurs dates — sauf le
    1er janvier 1960, qui ne fait que passer au nouveau franc, et 2002, où
    4 000 F deviennent 609,80 €."""
    import yaml

    fiche = yaml.safe_load((RACINE / "data" / "reference" / "regles"
                            / "majoration_conjoint_a_charge.yaml").read_text(encoding="utf-8"))
    attendus, precedent = [], None
    for debut, montant, unite in MAJORATION_CONJOINT:
        if unite == "€":
            en_euros = montant
        else:
            en_euros = montant / FRANCS_PAR_EURO / (100 if unite == "AF" else 1)
        if precedent is None or abs(en_euros - precedent) > 1e-6:
            attendus.append((debut, en_euros))
        precedent = en_euros
    versions = [version for version in fiche["versions"]
                if "montants" in ((version.get("contenu") or {}).get("parametres") or {})]
    assert len(versions) == 3
    for version in versions:
        montants = version["contenu"]["parametres"]["montants"]
        assert [debut for debut, _ in montants] == [debut for debut, _ in attendus]
        for (debut, lu), (_, attendu) in zip(montants, attendus):
            assert lu == pytest.approx(attendu, abs=1e-6), (version["id"], debut)


# -- les points des régimes complémentaires des indépendants ---------------------

POINTS = RACINE / "data" / "reference" / "regimes" / "valeurs_point.csv"

#: Les tables de l'ex-RSI que joignent les barèmes du point du RCI
#: (`rci_valeur_achat_point_bar.aspx`, `rci_valeur_point_bar.aspx`) : le
#: revenu de référence du RCO des artisans, prix d'un point, par année
#: (`rci_valeur_achat_artisan_avant_2013.pdf`), en francs jusqu'en 2001 ;
REVENU_DE_REFERENCE_RCO = {
    1979: 5.86, 1980: 6.58, 1981: 7.46, 1982: 8.41, 1983: 9.25, 1984: 10.13, 1985: 10.86,
    1986: 11.21, 1987: 11.60, 1988: 12.13, 1989: 12.59, 1990: 13.19, 1991: 13.77,
    1992: 14.24, 1993: 14.64, 1994: 14.87, 1995: 15.04, 1996: 15.38, 1997: 17.46,
    1998: 18.88, 1999: 20.36, 2000: 21.53, 2001: 22.23,
    2002: 3.461, 2003: 3.731, 2004: 3.882, 2005: 4.104, 2006: 4.145, 2007: 4.145,
    2008: 4.207, 2009: 4.500, 2010: 4.692, 2011: 4.79053, 2012: 4.89113,
}
#: la valeur annuelle de son point, à chaque date d'effet
#: (`rci_valeur_point_retraite_artisan_avant_2009.pdf`, puis
#: `…_2009_2012.pdf`, pour les points acquis depuis 1997), en francs jusqu'en
#: 2001 — un semestre commence le 1er janvier ou le 1er juillet ;
VALEUR_DU_POINT_RCO = (
    ("1979-01-01", 0.674), ("1980-01-01", 0.728), ("1980-07-01", 0.786),
    ("1981-01-01", 0.836), ("1981-07-01", 0.880), ("1982-01-01", 0.940),
    ("1982-07-01", 0.996), ("1983-01-01", 1.043), ("1983-07-01", 1.085),
    ("1984-01-01", 1.134), ("1984-07-01", 1.196), ("1985-01-01", 1.232),
    ("1985-07-01", 1.266), ("1986-01-01", 1.282), ("1986-07-01", 1.296),
    ("1987-01-01", 1.322), ("1987-07-01", 1.346), ("1988-01-01", 1.382),
    ("1988-07-01", 1.408), ("1989-01-01", 1.430), ("1989-07-01", 1.466),
    ("1990-01-01", 1.498), ("1990-07-01", 1.536), ("1991-01-01", 1.568),
    ("1991-07-01", 1.598), ("1992-01-01", 1.624), ("1992-07-01", 1.652),
    ("1993-01-01", 1.674), ("1993-07-01", 1.694), ("1994-01-01", 1.710),
    ("1995-01-01", 1.730), ("1996-01-01", 1.761), ("1996-07-01", 1.776),
    ("1997-04-01", 1.8032), ("1999-04-01", 1.8084), ("2000-04-01", 1.8300),
    ("2001-04-01", 1.8672), ("2002-04-01", 0.28728), ("2006-04-01", 0.29012),
    ("2007-12-01", 0.29331), ("2008-04-01", 0.29770), ("2009-04-01", 0.30603),
    ("2010-04-01", 0.30970), ("2011-04-01", 0.31620), ("2012-04-01", 0.32284),
)
#: la valeur du point du NRCO des commerçants
#: (`rci_valeur_point_regime_complementaire_repris_commercant_2004_2012.pdf`) ;
VALEUR_DU_POINT_NRCO = (
    ("2004-01-01", 1.000), ("2005-01-01", 1.016), ("2006-01-01", 1.036),
    ("2007-01-01", 1.055), ("2008-01-01", 1.067), ("2008-12-01", 1.073),
    ("2009-04-01", 1.102), ("2010-04-01", 1.115), ("2011-04-01", 1.138),
    ("2012-04-01", 1.162),
)
#: et la valeur d'achat et la valeur de service du RCI de 2013 à 2019
#: (`rci_valeur_achat_01042013_31122019.pdf`, `rci_valeur_point_2013_2019.pdf`),
#: celle-ci pour les points du NRCO, du RCI et du RCO acquis depuis 1997.
POINT_RCI = (
    ("2013-04-01", 17.309, 1.177), ("2015-10-01", 17.324, 1.178),
    ("2017-10-01", 17.456, 1.187), ("2019-01-01", 17.515, 1.191),
)

#: Ce que la série, tirée des barèmes de l'IPP (`ipp_points_independants.py`),
#: porte autrement que la caisse, au 31 décembre : sa valeur, en euros. Des
#: écarts qui changent le calcul — les points d'une année, ou leur valeur à la
#: liquidation —, à la session du modèle.
ECARTS_POINTS = {
    ("rco_artisans", "salaire_reference", 1997): 2.344666,  # 15,38 F, celui de 1996
    ("rco_artisans", "salaire_reference", 1998): 2.66176,   # 17,46 F, celui de 1997
    ("rco_artisans", "salaire_reference", 2002): 3.382,     # sous celui de 2001
    ("rco_artisans", "salaire_reference", 2009): 4.324,
    ("rco_artisans", "valeur_service", 1996): 0.268463,     # le 1er semestre
    ("rco_artisans", "valeur_service", 2007): 0.29259,
    ("nric", "valeur_service", 2008): 1.067,                # sans le 1er décembre
    ("nric", "valeur_service", 2010): 1.110,
}


def test_les_points_des_complementaires_des_independants_sont_ceux_de_la_caisse():
    """Le prix et la valeur du point du RCO des artisans (1979-2012), la
    valeur du point du NRCO des commerçants (2004-2012) et ceux du RCI de 2013
    à 2019 (`valeurs_point.csv`, la valeur en vigueur au 31 décembre) sont
    ceux que la caisse publie, aux arrondis de l'IPP près, sauf
    `ECARTS_POINTS`. Depuis 2009, la caisse sert aux points du RCO acquis
    avant 1997 une valeur moindre (0,31008 € en 2012 pour ceux de 1979 à
    1996, 0,30582 € pour ceux d'avant 1979 ; 1,132 et 1,112 € au RCI en
    2019) : la série porte celle des points acquis depuis 1997, et l'écart
    est connu (`ipp_points_independants.py`)."""
    serie: dict[tuple[str, str, int], float] = {
        (ligne["regime"], ligne["mesure"], int(ligne["annee"])): float(ligne["valeur"])
        for ligne in _csv(POINTS) if ligne["regime"] in ("rco_artisans", "nric", "rci")}
    attendus: dict[tuple[str, str, int], float] = {}
    for annee, prix in REVENU_DE_REFERENCE_RCO.items():
        attendus[("rco_artisans", "salaire_reference", annee)] = (
            prix / FRANCS_PAR_EURO if annee < 2002 else prix)
    for regime, table, debut, fin in (("rco_artisans", VALEUR_DU_POINT_RCO, 1980, 2012),
                                      ("nric", VALEUR_DU_POINT_NRCO, 2004, 2012)):
        for annee in range(debut, fin + 1):
            jour, valeur = _en_vigueur(table, f"{annee}-12-31")
            attendus[(regime, "valeur_service", annee)] = (
                valeur / FRANCS_PAR_EURO if jour < "2002" else valeur)
    for annee in range(2013, 2020):
        _, prix, valeur = _en_vigueur(POINT_RCI, f"{annee}-12-31")
        attendus[("rci", "salaire_reference", annee)] = prix
        attendus[("rci", "valeur_service", annee)] = valeur
    for cle, attendu in sorted(attendus.items()):
        if cle in ECARTS_POINTS:
            assert serie[cle] == pytest.approx(ECARTS_POINTS[cle], abs=1e-6), cle
            assert serie[cle] != pytest.approx(attendu, abs=5e-5), (cle, "l'écart s'est résorbé")
            continue
        assert serie[cle] == pytest.approx(attendu, abs=5e-5), (cle, serie[cle], attendu)


# -- l'assiette maximale des indépendants ---------------------------------------

#: « Assiette annuelle maximale des cotisations des travailleurs
#: indépendants » (`ti_cotisation_assiette_maximale_cotisation_bar.aspx`,
#: version du 30 juin 2026) et la table de l'ex-RSI qu'il joint, 1973-2019
#: (`ti_cotisation_assiette_maximale_cotisation.pdf`) : jusqu'où chaque régime
#: assied sa cotisation, en plafonds de la sécurité sociale de l'année. Le
#: régime de base, un plafond jusqu'en 2013 ; le RCO des artisans, trois puis
#: quatre ; le NRCO des commerçants, trois ; le RCI, quatre ; le régime des
#: conjoints de commerçants, un.
ASSIETTE_MAXIMALE = {
    "cancava": ((1973, 2005, 1),), "organic": ((1973, 2005, 1),), "rsi": ((2006, 2013, 1),),
    "rco_artisans": ((1979, 1996, 3), (1997, 2012, 4)),
    "nric": ((2004, 2012, 3),), "rci": ((2013, 2025, 4),),
    "organic_conjoints_batiment": ((1973, 2003, 1),),
}
#: Des montants de la table, qui sont ces multiples : (régime, période, montant,
#: unité, plafond de la période).
REPERES_ASSIETTE_MAXIMALE = (
    ("rco_artisans", "1996, 2e semestre", 487440, "F", 162480),
    ("rco_artisans", "1997", 658560, "F", 164640),
    ("rco_artisans", "2003", 116736, "€", 29184),
    ("nric", "2004", 89136, "€", 29712),
    ("rci", "2013", 148128, "€", 37032),
    ("organic_conjoints_batiment", "2003", 29184, "€", 29184),
)
#: L'assiette de la fiche, en plafonds : sa borne haute.
PLAFONDS_D_UNE_ASSIETTE = {
    "plafonnee": 1, "plafonnee_3_pass": 3, "plafonnee_4_pass": 4, "tranche_1_4_pass": 4,
    "plafonnee_033_pass": 1 / 3, "tranche_033_1_pass": 1,
}
#: Les écarts, à la session du modèle : aucun depuis que la fiche du RCO des
#: artisans l'assied sur quatre plafonds dès 1997, comme D. 635-4 dans sa
#: rédaction du 26 février 1997 (LEGIARTI000006738337, action 177).
ECARTS_ASSIETTE_MAXIMALE: dict[tuple[str, int], float] = {}


def test_l_assiette_maximale_des_independants_est_celle_de_la_caisse():
    """Chaque fiche assied la cotisation de chaque année jusqu'au multiple du
    plafond que la caisse publie, sauf `ECARTS_ASSIETTE_MAXIMALE`."""
    for regime, _, montant, unite, plafond in REPERES_ASSIETTE_MAXIMALE:
        assert any(abs(montant / plafond - m) < 1e-9
                   for _, _, m in ASSIETTE_MAXIMALE[regime]), (regime, montant, unite)
    for regime, periodes in ASSIETTE_MAXIMALE.items():
        for debut, fin, multiple in periodes:
            for annee in range(debut, fin + 1):
                lu = max(PLAFONDS_D_UNE_ASSIETTE[assiette]
                         for assiette in _taux_de_la_fiche(regime, annee))
                attendu = ECARTS_ASSIETTE_MAXIMALE.get((regime, annee), multiple)
                assert lu == pytest.approx(attendu), (regime, annee, lu)
                if (regime, annee) in ECARTS_ASSIETTE_MAXIMALE:
                    assert lu != pytest.approx(multiple), (regime, annee, "l'écart s'est résorbé")


# -- le cumul emploi-retraite et la réversion du RCI ----------------------------

REGLES = RACINE / "data" / "reference" / "regles"

#: « Plafond cumul emploi retraite des travailleurs indépendants »
#: (`ti_prestation_plafond_cumul_emploi_retraite_bar.aspx`, version du 5 janvier
#: 2026) et la table de l'ex-RSI qu'il joint pour 2007 à 2019 : le plafond
#: annuel hors des zones de revitalisation, en euros, la moitié du plafond de
#: la sécurité sociale ; dans ces zones, le plafond entier.
CUMUL_INDEPENDANTS = {
    2007: 16092, 2008: 16638, 2009: 17154, 2010: 17310, 2011: 17676, 2012: 18186,
    2013: 18516, 2014: 18774, 2015: 19020, 2016: 19308, 2017: 19614, 2018: 19866,
    2019: 20262, 2020: 20568, 2021: 20568, 2022: 20568, 2023: 21996, 2024: 23184,
    2025: 23550, 2026: 24030,
}


def test_le_plafond_du_cumul_des_artisans_et_commercants_est_celui_de_la_caisse():
    """La fiche du cumul emploi-retraite (`cumul_emploi_retraite_et_retraite_progressive`)
    plafonne les revenus de l'artisan et du commerçant à la moitié du plafond
    de la sécurité sociale, là où elle le fait : c'est le plafond que la caisse
    publie de 2007 à 2026, hors des zones de revitalisation rurale, où il est
    entier — ce que la fiche déclare ne pas appliquer."""
    import yaml

    fiche = yaml.safe_load((REGLES / "cumul_emploi_retraite_et_retraite_progressive.yaml")
                           .read_text(encoding="utf-8"))
    seuils = {version["id"]: version["contenu"]["parametres"]["seuil_independants_en_pass"]
              for version in fiche["versions"]
              if "seuil_independants_en_pass" in ((version.get("contenu") or {})
                                                  .get("parametres") or {})}
    assert seuils and set(seuils.values()) == {0.5}, seuils
    assert "revitalisation rurale, le plafond entier, n'est pas appliqué" in " ".join(
        (REGLES / "cumul_emploi_retraite_et_retraite_progressive.yaml")
        .read_text(encoding="utf-8").split())
    plafond = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")
    for annee, montant in CUMUL_INDEPENDANTS.items():
        assert 0.5 * plafond[annee] == pytest.approx(montant), annee


#: « Plafond de ressources de la retraite de réversion du régime
#: complémentaire des travailleurs indépendants »
#: (`rci_plafond_ressource_retraite_reversion_bar.aspx`, version du 5 janvier
#: 2026) et la table de l'ex-RSI qu'il joint pour 2013 à 2019, en euros par an.
PLAFOND_REVERSION_RCI = {
    2013: 74064, 2014: 75096, 2015: 76080, 2016: 77232, 2017: 78456, 2018: 79464,
    2019: 81048, 2020: 82272, 2021: 82272, 2022: 82272, 2023: 87984, 2024: 92736,
    2025: 94200, 2026: 96120,
}


def test_le_plafond_de_la_reversion_du_rci_est_celui_de_la_caisse():
    """La fiche `reversion_rci` plafonne les ressources du survivant à deux
    plafonds de la sécurité sociale, depuis 2013 : ce que la caisse publie,
    chaque année. Avant 2013, elle ne sert pas la réversion du RCO des
    artisans, dont la caisse publie un plafond propre (35 326 € en 2009)."""
    import yaml

    fiche = yaml.safe_load((REGLES / "reversion_rci.yaml").read_text(encoding="utf-8"))
    plafonds = {version["id"]: ((version.get("contenu") or {}).get("parametres") or {})
                .get("plafond_pass") for version in fiche["versions"]}
    assert plafonds == {"avant_2013": None, "reglement_2013": 2, "plafond_2021": 2}
    plafond = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")
    for annee, montant in PLAFOND_REVERSION_RCI.items():
        assert 2 * plafond[annee] == pytest.approx(montant), annee


# -- Mayotte ----------------------------------------------------------------------


def test_un_bareme_de_mayotte_se_lit_par_date():
    """Les barèmes de Mayotte rangent une valeur par ligne, datée d'un jour,
    d'une période dont seul compte le début, ou d'une année ; un montant écrit
    ses milliers d'une espace, sa virgule décimale, son euro."""
    module = _recuperateur("cnav_mayotte")
    contenu = "".join((
        "<table><tr><th>Date</th><th>Montant horaire Mayotte</th></tr>",
        "<tr><td>01/01/2026</td><td>9,33 €</td><td>Circulaire</td></tr>",
        "<tr><td>​01/07/2004 au 31/12/2010</td><td>​912 €</td>",
        "<td>​10 944 €</td></tr>",
        "<tr><td>2026</td><td>1 399,50 €</td></tr></table>"))
    assert module.lignes(contenu) == [("2026-01-01", 9.33), ("2004-07-01", 912.0),
                                      ("2026-01-01", 1399.50)]
    assert module.lignes(contenu, colonne=2) == [("2004-07-01", 10944.0)]
    assert module.au_1er_janvier([("2004-07-01", 3.48), ("2005-07-01", 3.83),
                                  ("2006-01-01", 4.0)], 2005, 2006) == {2005: 3.48, 2006: 4.0}


def test_le_salaire_qui_valide_un_trimestre_a_mayotte_est_le_smig_fois_les_heures():
    """Un trimestre se valide à Mayotte par 200 heures du Smig mahorais du
    1er janvier jusqu'en 2016, 150 depuis 2017 (décret n° 87-175, art. 3 ;
    décret n° 2003-589, art. 8) : la caisse publie ce produit, et le
    récupérateur n'écrit rien s'il ne le retrouve pas."""
    module = _recuperateur("cnav_mayotte")
    smig = {2016: 7.30, 2017: 7.37}
    assert module.controler(smig, {2016: 1460.0, 2017: 1105.50}) == []
    griefs = module.controler(smig, {2016: 1460.0, 2017: 1474.0})
    assert len(griefs) == 1 and "2017" in griefs[0]


#: « Smic mensuel - Mayotte » : la colonne de la caisse de sécurité sociale de
#: Mayotte (`smic_smig_smic_mensuel_mayotte_bar.aspx`, version du 25 juillet
#: 2024) de 2002 à 2021, puis l'édition suivante
#: (`mayotte_smic_minimum_garanti_smic_mensuel_bar.aspx`, version du
#: 23 décembre 2025) : le salaire brut mensuel de 169 heures, de 151,67 depuis
#: 2018, à chaque date d'effet.
SMIC_MENSUEL_MAYOTTE = (
    ("2002-01-01", 457.99), ("2002-07-01", 481.65), ("2003-01-01", 510.38),
    ("2003-07-01", 534.04), ("2004-01-01", 549.25), ("2004-07-01", 588.12),
    ("2005-07-01", 647.27), ("2006-07-01", 706.42), ("2007-07-01", 826.41),
    ("2008-07-01", 927.81), ("2009-07-01", 1002.17), ("2010-07-01", 1069.77),
    ("2011-01-01", 1086.67), ("2012-01-01", 1130.61), ("2012-07-01", 1154.27),
    ("2013-01-01", 1176.24), ("2014-01-01", 1201.59), ("2015-01-01", 1226.94),
    ("2016-01-01", 1233.70), ("2017-01-01", 1245.53), ("2018-01-01", 1131.43),
    ("2019-01-01", 1148.12), ("2020-01-01", 1161.79), ("2021-01-01", 1173.93),
    ("2021-10-01", 1199.68), ("2022-01-01", 1210.30), ("2022-05-01", 1242.15),
    ("2022-08-01", 1266.42), ("2023-01-01", 1290.68), ("2023-05-01", 1319.50),
    ("2024-01-01", 1334.67), ("2025-01-01", 1361.97), ("2026-01-01", 1415.05),
)


def test_le_smic_mensuel_de_mayotte_est_le_smig_de_la_serie_fois_les_heures():
    """Le Smig horaire de `mayotte_smig_et_plafond.csv`, celui du 1er janvier,
    fait chaque année le Smic mensuel que publient la caisse de Mayotte puis
    la Cnav : fois 169 heures jusqu'en 2017, fois 35 × 52 / 12 depuis 2018 —
    la caisse de Mayotte compte 151,67 heures en 2020 et en 2021."""
    smig = _serie_annuelle(LEGISLATION / "mayotte_smig_et_plafond.csv", "smig_horaire")
    for annee in range(2002, 2027):
        heures = (169,) if annee < 2018 else (35 * 52 / 12, 151.67)
        assert _au_1er_janvier(SMIC_MENSUEL_MAYOTTE, annee)[1] in {
            round(smig[annee] * h, 2) for h in heures}, annee


# -- les dernières valeurs --------------------------------------------------------

#: « Dernières valeurs » (`derniere_valeur_derniere_valeur_bar.aspx`, version du
#: 2 avril 2026) : le récapitulatif que la caisse tient des valeurs de 2026,
#: en euros par an sauf mention.
DERNIERES_VALEURS = {
    "coefficient de revalorisation des retraites": 1.009,
    "salaire qui valide un trimestre": 1803,
    "allocation aux vieux travailleurs salariés": 4059.72,
    "minimum contributif": 9075.50, "minimum contributif majoré": 10847.22,
    "minimum de la réversion": 4019.13,
    "maximum de la retraite personnelle": 24030.00,
    "salaire plafond": 48060.00,
    "ASPA, un allocataire": 12523.14, "ASPA, un allocataire, par mois": 1043.59,
    "ASPA, deux allocataires": 19442.21,
    "majoration pour charge d'enfant, par mois": 113.59,
    "majoration pour conjoint à charge": 609.80,
    "plafond de ressources de la réversion, personne seule": 25001.60,
    "plafond de ressources de la réversion, couple": 40002.56,
    "plafond de la majoration de la réversion, par trimestre": 3020.07,
    "Smic horaire": 12.02,
}


def test_les_dernieres_valeurs_de_la_caisse_sont_celles_des_series():
    """Ce que la caisse récapitule pour 2026 est ce que portent les séries du
    dépôt, chacune lue par son récupérateur ou confrontée par son test. L'ASPA
    d'un allocataire fait, à la série, douze fois le mensuel, six centimes de
    moins que l'annuel publié : la fiche `minimum_vieillesse` le déclare."""
    v = DERNIERES_VALEURS
    revalorisation = {ligne["date_effet"]: float(ligne["coefficient"])
                      for ligne in _csv(LEGISLATION / "revalorisation_pensions.csv")}
    assert revalorisation["2026-01-01"] == v["coefficient de revalorisation des retraites"]
    smic = _serie_annuelle(MACRO / "smic_horaire.csv", "smic_horaire")[2026]
    assert smic == pytest.approx(v["Smic horaire"])
    assert 150 * smic == pytest.approx(v["salaire qui valide un trimestre"])
    avts = {ligne["date"]: float(ligne["valeur"])
            for ligne in _csv(LEGISLATION / "pension_minimum_avant_1983.csv")}
    assert avts["2026-01-01"] == v["allocation aux vieux travailleurs salariés"]
    contributif = {(ligne["mesure"], ligne["date"]): float(ligne["valeur"])
                   for ligne in _csv(LEGISLATION / "minimum_contributif.csv")}
    assert contributif[("montant_base", "2026-01-01")] == v["minimum contributif"]
    assert contributif[("montant_majore", "2026-01-01")] == v["minimum contributif majoré"]
    annuel = {nom: _serie_annuelle(LEGISLATION / f"{nom}.csv", "valeur")[2026] for nom in (
        "minimum_reversion", "minimum_vieillesse", "minimum_vieillesse_couple",
        "majoration_forfaitaire_enfant_reversion", "plafond_majoration_reversion")}
    assert annuel["minimum_reversion"] == pytest.approx(v["minimum de la réversion"])
    assert annuel["minimum_vieillesse"] == pytest.approx(12 * v["ASPA, un allocataire, par mois"])
    assert annuel["minimum_vieillesse"] != pytest.approx(v["ASPA, un allocataire"], abs=0.01)
    assert annuel["minimum_vieillesse_couple"] == pytest.approx(v["ASPA, deux allocataires"])
    assert annuel["majoration_forfaitaire_enfant_reversion"] == pytest.approx(
        12 * v["majoration pour charge d'enfant, par mois"])
    assert annuel["plafond_majoration_reversion"] == pytest.approx(
        v["plafond de la majoration de la réversion, par trimestre"])
    plafond = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")[2026]
    assert plafond == v["salaire plafond"]
    assert 0.5 * plafond == v["maximum de la retraite personnelle"]
    assert 2080 * smic == pytest.approx(v["plafond de ressources de la réversion, personne seule"])
    assert 1.6 * 2080 * smic == pytest.approx(v["plafond de ressources de la réversion, couple"])
    assert MAJORATION_CONJOINT[-1][1] == v["majoration pour conjoint à charge"]


# -- les indépendants des DOM -----------------------------------------------------

#: « Taux de cotisations travailleurs indépendants - DOM » de 2020 à 2024
#: (`ti_cotisation_taux_cotisation_dom_<année>_bar.aspx`, versions du 31 mai
#: 2023 au 30 juin 2026) : la retraite de base sous le plafond et au-delà, le
#: RCI jusqu'à son plafond propre puis jusqu'à quatre plafonds, en pour cent,
#: et ce plafond propre, en euros.
TAUX_DOM = {
    2020: (17.75, 0.60, 7, 8, 38340), 2021: (17.75, 0.60, 7, 8, 38493),
    2022: (17.75, 0.60, 7, 8, 38916), 2023: (17.75, 0.60, 7, 8, 40784),
    2024: (17.75, 0.60, 7, 8, 42946),
}
#: « Assiettes et cotisations minimales des travailleurs indépendants - DOM »
#: (version du 1er juillet 2026), « dans le cas où les seuils d'exonération
#: sont dépassés » : l'assiette minimale de la retraite de base, en euros.
ASSIETTE_MINIMALE_DOM = {2018: 4569, 2019: 4660, 2020: 4731, 2021: 4731, 2022: 4731,
                         2023: 5072, 2024: 5243, 2025: 5346}
#: Leurs tables de 2007 à 2019, jointes (« Info-doc RSI » mis à jour le
#: 27 février 2019) : `ti_cotisation_taux_cotisation_dom_2007_2019.pdf`, la
#: retraite de base sous le plafond et au-delà, en pour cent, et, depuis 2013,
#: le RCI comme `TAUX_DOM` ; `ti_cotisation_assiette_minimale_cotisation_dom.pdf`,
#: l'assiette minimale de la retraite de base (`ASSIETTE_MINIMALE_DOM`, et,
#: de 2009 à 2016, la moitié de celle de la métropole).
TAUX_DOM_AVANT_2020 = {
    2007: (16.65, 0), 2008: (16.65, 0), 2009: (16.65, 0), 2010: (16.65, 0),
    2011: (16.65, 0), 2012: (16.65, 0), 2013: (16.85, 0, 7, 8, 37032),
    2014: (17.15, 0.20, 7, 8, 37513), 2015: (17.40, 0.35, 7, 8, 37513),
    2016: (17.65, 0.50, 7, 8, 37546), 2017: (17.75, 0.60, 7, 8, 37546),
    2018: (17.75, 0.60, 7, 8, 37846), 2019: (17.75, 0.60, 7, 8, 37960),
}
#: L'écart, que la limite des indépendants des DOM déclare : de 2009 à 2016,
#: la table porte la moitié de l'assiette minimale (« (200 SMIC horaire)/2 »,
#: « 5,25 % PASS/2 »…), l'assiette de leur retraite de base étant la moitié
#: du revenu sous le plafond (L. 756-4, rédactions de 2000 à 2016), et garde
#: en 2012 les 200 heures du Smic, quand la métropole passe à 5,25 % du
#: plafond.
ASSIETTE_MINIMALE_DOM_DE_MOITIE = {2009: 871, 2010: 886, 2011: 900, 2012: 922, 2013: 972,
                                   2014: 986, 2015: 1465, 2016: 2221}


def test_l_independant_des_dom_cotise_aux_taux_et_aux_assiettes_de_la_metropole():
    """Ses abattements et ses exonérations mis à part, que le modèle ne sert
    pas (`docs/limites/3-systeme-actuel.md`), l'indépendant des DOM cotise à la
    retraite de base et au RCI aux taux de la série et de la fiche, et sur leurs
    assiettes : la retraite de base sans plafond, 0,60 % au-delà du plafond, le
    RCI jusqu'à quatre plafonds — l'assiette maximale de l'édition des DOM, de
    2020 à 2022 —, et l'assiette minimale de la série. L'édition des DOM garde
    pour 2022 11,5 % du plafond, comme la série, quand le décret n° 2022-1438
    fixe 4 758 €, ce que `ECARTS_ASSIETTE_MINIMALE` déclare. Les tables
    d'avant 2020 disent de même la retraite de base depuis 2007 et le RCI depuis
    2013, mais, de 2009 à 2016, une assiette minimale moitié moindre
    (`ASSIETTE_MINIMALE_DOM_DE_MOITIE`) : un écart de plus, que la limite
    déclare."""
    rsi, general = _taux_annuels("rsi"), _taux_annuels("regime_general")
    (premiere,) = [p for p in _fiche("rci")["periodes"]
                   if p["debut"] == 2013 and p["assiette"] == "plafonnee"]
    for annee, (sous_plafond, au_dela, *complementaire) in {**TAUX_DOM_AVANT_2020,
                                                           **TAUX_DOM}.items():
        if annee <= 2017:
            plafonne = rsi[(annee, "taux_plafonne")]
            totalite = rsi.get((annee, "taux_deplafonne"), 0.0)
        else:
            plafonne = general[(annee, "taux_plafonne_non_salarie")]
            totalite = general[(annee, "taux_deplafonne_non_salarie")]
        assert plafonne + totalite == pytest.approx(sous_plafond / 100), annee
        assert totalite == pytest.approx(au_dela / 100), annee
        if not complementaire:
            continue
        rci, rci_au_dela, plafond_rci = complementaire
        fiche = _taux_de_la_fiche("rci", annee)
        assert (fiche["plafonnee"], fiche["tranche_1_4_pass"]) == pytest.approx(
            (rci / 100, rci_au_dela / 100)), annee
        assert premiere["borne_haute_par_annee"][annee] == plafond_rci, annee
    smic = _serie_annuelle(MACRO / "smic_horaire.csv", "smic_horaire")
    plafond = _serie_annuelle(MACRO / "plafond_securite_sociale.csv", "pass_eur")
    for annee, publiee in ASSIETTE_MINIMALE_DOM.items():
        assert _arrondi(_assiette_minimale_de_la_serie(annee, smic, plafond)) == publiee, annee
    for annee, publiee in ASSIETTE_MINIMALE_DOM_DE_MOITIE.items():
        serie = _arrondi(_assiette_minimale_de_la_serie(annee, smic, plafond))
        regle = _arrondi(200 * smic[annee]) if annee <= 2012 else serie
        assert _arrondi(regle / 2) == publiee != serie, annee
