"""Le régime spécial des industries électriques et gazières, lu au droit.

Trois fiches de la carte, lues au droit le 29 octobre 2026 (action 130) dans
les rédactions de l'annexe 3 du statut national du personnel — celle de 1946,
puis celles des décrets n° 2008-627, n° 2011-290, n° 2014-698 et n° 2023-692 :
l'âge d'ouverture de l'agent actif et l'âge d'où court sa surcote
(`age_ouverture_ieg_actifs`), l'âge d'annulation de sa décote
(`age_reference_decote_ieg`), la durée qui lui donne le pourcentage maximum
(`duree_requise_ieg`). Chaque version dit ce qu'elle lit, et les données du
modèle le portent : les périodes de `regimes/ieg.yaml` et les tables qu'elles
nomment. Une période du régime couvre des années entières : une version qui
commence en cours d'année se confronte aux années qu'elle couvre en entier, et
le second semestre de 2008, que le modèle liquide sous la période d'avant la
réforme, est une approximation que les fiches déclarent.
"""

from __future__ import annotations

from datetime import date

import pytest
import yaml

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte
from retraite_notionnelle.scenarios.actuel import (
    AgesRegimes, AgesSurcoteRegimesSpeciaux, CalendriersDureeRequise,
    DecoteRegimesSpeciaux, DureesRequisesRegimes)

PERIODES = yaml.safe_load((RACINE_DONNEES / "reference" / "regimes" / "ieg.yaml")
                          .read_text(encoding="utf-8"))["periodes"]
#: Le régime naît du statut national, en vigueur au 1er juin 1946.
NAISSANCE = DateMois(1946, 6)
#: La dernière année que les confrontations parcourent.
HORIZON = 2050


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1946."""
    premiere = NAISSANCE.annee if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, NAISSANCE.annee), HORIZON + 1 if fin is None else fin.year)


def _mois(debut: date | None, fin: date | None) -> list[DateMois]:
    """Les mois de [debut, fin), depuis la naissance du régime."""
    premier = NAISSANCE if debut is None else DateMois(debut.year, debut.month)
    dernier = DateMois(HORIZON, 12) if fin is None else DateMois(fin.year, fin.month).plus_mois(-1)
    return [DateMois.depuis_rang(rang) for rang in range(premier.rang, dernier.rang + 1)]


def _periode(annee: int) -> dict:
    return next(p for p in PERIODES
                if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"]))


def _escalier(table: dict, cle):
    """Une table en escalier : la valeur de la dernière clé qui ne dépasse pas
    ``cle``, comme le modèle lit ses tables par génération ; rien en deçà de
    la première."""
    retenues = [k for k in table if k <= cle]
    return table[max(retenues)] if retenues else None


def _generations(table: dict) -> list[float]:
    """Les générations, de semestre en semestre, de trois ans avant la première
    marche d'une table à cinq ans après la dernière."""
    return [annee / 2 for annee in range(2 * (int(min(table)) - 3), 2 * (int(max(table)) + 6))]


def _atteint(annee: int, generation: int, *ages: float) -> bool:
    """L'agent de cette génération peut-il avoir, le 31 décembre de cette
    année, le plus jeune de ces âges ? Sinon, aucun ne le touche encore."""
    return annee - generation + 1 > min(ages)


def test_l_age_de_l_actif_et_celui_de_sa_surcote_sont_ceux_de_chaque_version():
    """`age_ouverture_ieg_actifs` : cinquante-cinq ans de 1946 au 21 mars 2011,
    puis le calendrier par génération du 2° du V de l'article 45, cinquante-sept
    ans pour 1967, que la rédaction de 2025 prolonge jusqu'à cinquante-neuf ans
    pour 1975 ; aucune surcote avant le 1er juillet 2008, puis au-delà de
    soixante ans, enfin de l'âge du 1° du I de l'article 16, que le 1° du V
    relève par génération jusqu'à soixante-quatre ans pour 1970. Chaque année
    qu'une version couvre en entier, la période du régime donne à toute
    génération qui peut y avoir l'âge l'âge que la version écrit."""
    ages = AgesRegimes(RACINE_DONNEES)
    surcote = AgesSurcoteRegimesSpeciaux(RACINE_DONNEES)
    confrontes = set()
    for version in _versions("age_ouverture_ieg_actifs"):
        lus = version["contenu"]["parametres"]
        for annee in _annees_entieres(*version["bornes"]["liquidation.date_effet"]):
            periode = _periode(annee)
            for generation in range(max(annee - 75, 1900), annee - 50):
                attendu = _escalier(lus["ages_des_actifs"], generation)
                modele = (ages.ages(periode["age_table"], generation)[0]
                          if periode.get("age_table") else periode["age_ouverture"])
                if _atteint(annee, generation, attendu, modele):
                    assert modele == pytest.approx(attendu, abs=0.005), (
                        version["id"], annee, generation)
                    confrontes.add(version["id"])
                if lus["ages_de_surcote"] is None:
                    assert periode["surcote_par_trimestre"] is None, (version["id"], annee)
                    continue
                assert periode.get("age_surcote_regimes_speciaux"), (version["id"], annee)
                attendu = _escalier(lus["ages_de_surcote"], generation)
                modele = surcote.age(generation)[0]
                if _atteint(annee, generation, attendu, modele):
                    assert modele == pytest.approx(attendu, abs=0.005), (
                        version["id"], annee, generation)
    assert confrontes == {v["id"] for v in _versions("age_ouverture_ieg_actifs")}


def test_l_age_d_annulation_de_la_decote_est_celui_de_chaque_version():
    """`age_reference_decote_ieg` : aucune décote à qui réunit les conditions
    avant le 1er juillet 2010 ; puis l'âge minimum d'ouverture majoré de cinq
    ans, diminué de seize trimestres la première année, de deux de moins chaque
    1er juillet jusqu'en 2013 puis d'un, de rien depuis juillet 2024 ; à qui les
    réunit depuis le 1er janvier 2025, majoré de trois ans, et soixante-deux ans
    pour l'actif né avant 1975. Le barème des régimes spéciaux, lu au mois où
    les conditions sont réunies (`liquider.millesime_du_bareme`), et les tables
    d'âges que nomment les périodes le portent."""
    bareme = DecoteRegimesSpeciaux(RACINE_DONNEES)
    ages = AgesRegimes(RACINE_DONNEES)
    for version in _versions("age_reference_decote_ieg"):
        lus = version["contenu"]["parametres"]
        bornes = version["bornes"]["ouverture_du_droit"]
        for mois in _mois(*bornes):
            ligne = bareme.parametres(mois.annee + (mois.mois >= 7))
            if lus["majoration_de_l_age_minimum"] is None:
                assert ligne is None, (version["id"], str(mois))
                continue
            diminution = _escalier(lus.get("diminution_en_trimestres") or {"": 0},
                                   f"{mois.annee:04d}-{mois.mois:02d}")
            assert ligne[0] == diminution, (version["id"], str(mois))
        if lus["majoration_de_l_age_minimum"] is None:
            continue
        tables = {_periode(annee)["age_table"] for annee in _annees_entieres(*bornes)}
        assert tables, version["id"]
        for table in tables:
            for generation in range(1930, 1996):
                ouverture, reference, _ = ages.ages(table, generation)
                if generation < 1975 and "age_des_actifs_nes_avant_1975" in lus:
                    assert reference == lus["age_des_actifs_nes_avant_1975"], (table, generation)
                else:
                    assert reference - ouverture == pytest.approx(
                        lus["majoration_de_l_age_minimum"], abs=0.005), (table, generation)


def test_la_duree_requise_est_celle_de_chaque_version():
    """`duree_requise_ieg` : cent cinquante trimestres, trente-sept annuités et
    demie à 2 %, à qui réunit les conditions avant le 1er juillet 2008 ; puis le
    calendrier du I de l'article 45, de 151 trimestres à 166 en juillet 2018 ;
    à compter du 1er juillet 2019, la table par génération de 2014, lue à la
    génération qui a soixante ans le mois où le droit s'ouvre (article 9-1) ;
    à compter du 1er janvier 2025, une table par durée de services actifs, et
    l'ancienne règle en deçà de sa première génération. Le pourcentage maximum
    est de 75 %. Le calendrier de 2008 et les tables du modèle le portent, au
    mois où les conditions sont réunies."""
    calendriers = CalendriersDureeRequise(RACINE_DONNEES)
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    for version in _versions("duree_requise_ieg"):
        lus = version["contenu"]["parametres"]
        bornes = version["bornes"]["ouverture_du_droit"]
        annees, mois = _annees_entieres(*bornes), _mois(*bornes)
        for annee in annees:
            assert _periode(annee)["taux_plein"] == lus["pourcentage_maximum"], (version["id"], annee)
        if "trimestres" in lus:
            assert {calendriers.trimestres("regimes_speciaux_2008", m.rang)[0]
                    for m in mois} == {lus["trimestres"]}, version["id"]
            assert {_periode(annee)["duree_requise_trimestres"] for annee in annees} == {
                lus["trimestres"]}, version["id"]
        if "calendrier" in lus:
            for m in mois:
                assert calendriers.trimestres("regimes_speciaux_2008", m.rang)[0] == _escalier(
                    lus["calendrier"], f"{m.annee:04d}-{m.mois:02d}"), (version["id"], str(m))
            assert {_periode(annee).get("duree_requise_calendrier") for annee in annees} == {
                "regimes_speciaux_2008"}, version["id"]
        if "table_par_generation" in lus:
            for generation in _generations(lus["table_par_generation"]):
                ligne = tables.ligne("ieg_2014", generation, DateMois(HORIZON, 1).rang)
                assert (ligne and ligne[0]) == _escalier(lus["table_par_generation"], generation), (
                    generation)
            assert tables.ligne("ieg_2014", 1973, mois[0].plus_mois(-1).rang) is None
            # L'actif né en novembre 1963 a cinquante-cinq ans et huit mois en
            # juillet 2019 : il lit la génération qui a soixante ans ce mois-là.
            ouverture = mois[0]
            lue = ouverture.annee - lus["age_de_lecture"] + (ouverture.mois - 1) / 12
            assert tables.ligne("ieg_2014", 1963 + 10 / 12, ouverture.rang)[0] == _escalier(
                lus["table_par_generation"], lue)
            assert {tuple(_periode(annee)["duree_requise_table"]) for annee in annees} == {
                ("ieg_2014",)}, version["id"]
        if "tables_par_services_actifs" in lus:
            for services, table in lus["tables_par_services_actifs"].items():
                nom = f"ieg_actif_{services}"
                for generation in _generations(table):
                    ligne = tables.ligne(nom, generation, mois[0].rang)
                    assert (ligne and ligne[0]) == _escalier(table, generation), (nom, generation)
                    assert tables.ligne(nom, generation, mois[0].plus_mois(-1).rang) is None
            assert {tuple(_periode(annee)["duree_requise_table"]) for annee in annees} == {
                ("ieg_actif_17", "ieg_2014")}, version["id"]
