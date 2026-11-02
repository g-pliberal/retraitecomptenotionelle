"""Les régimes spéciaux de la SNCF et de la RATP, lus au droit.

Trois fiches de la carte, lues au droit le 2 novembre 2026 (action 130) dans
les rédactions des décrets du 30 juin 2008 — n° 2008-639 pour la SNCF,
n° 2008-637 pour la RATP — que les décrets n° 2011-291 et n° 2011-292, puis
n° 2014-712 et n° 2014-668, enfin n° 2023-967 et n° 2023-690 modifient, et
dans les tableaux par génération de la CPRPSNCF : l'âge d'annulation de la
décote (`age_reference_decote_sncf_ratp`), l'âge d'où court la surcote
(`age_surcote_sncf_ratp`), la durée qui donne le pourcentage maximum
(`duree_requise_sncf_ratp`). Chaque version dit ce qu'elle lit, et les
données du modèle le portent : les périodes de `regimes/sncf.yaml` et de
`regimes/ratp.yaml`, et les tables qu'elles nomment. Une période couvre des
années entières : une version qui commence en cours d'année se confronte aux
années qu'elle couvre en entier. Le modèle sert l'agent de conduite de la
SNCF et le roulant de la RATP ; ce qu'il fait autrement que le droit, les
fiches le déclarent, et le dernier test le tient, cas par cas.
"""

from __future__ import annotations

from datetime import date

import pytest
import yaml

from retraite_notionnelle.calendrier import DateMois, en_mois
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte
from retraite_notionnelle.scenarios.actuel import (
    AgesRegimes, AgesSurcoteRegimesSpeciaux, CalendriersDureeRequise,
    DecoteRegimesSpeciaux, DureesRequisesRegimes)

REGIMES = ("sncf", "ratp")
PERIODES = {regime: yaml.safe_load((RACINE_DONNEES / "reference" / "regimes" / f"{regime}.yaml")
                                   .read_text(encoding="utf-8"))["periodes"]
            for regime in REGIMES}
#: L'agent que le modèle sert : l'agent de conduite de la SNCF (1° du I de
#: l'article 1er du décret n° 2008-639), le roulant du tableau B de la RATP
#: (2° du II de l'article 6 du décret n° 2008-637).
SERVI = {"sncf": "agents_de_conduite", "ratp": "tableau_b"}
#: La première période des deux fiches de régime.
DEBUT = DateMois(1930, 1)
#: La dernière année que les confrontations parcourent.
HORIZON = 2050


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1930."""
    premiere = DEBUT.annee if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT.annee), HORIZON + 1 if fin is None else fin.year)


def _mois(debut: date | None, fin: date | None) -> list[DateMois]:
    """Les mois de [debut, fin), depuis la première période."""
    premier = DEBUT if debut is None else DateMois(debut.year, debut.month)
    dernier = DateMois(HORIZON, 12) if fin is None else DateMois(fin.year, fin.month).plus_mois(-1)
    return [DateMois.depuis_rang(rang) for rang in range(premier.rang, dernier.rang + 1)]


def _periode(regime: str, annee: int) -> dict:
    return next(p for p in PERIODES[regime]
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


def _tables_d_ages(depuis: int) -> set[tuple[str, str]]:
    """Les tables d'âges que nomment les périodes des deux régimes, de cette
    année à l'horizon."""
    return {(regime, _periode(regime, annee)["age_table"])
            for regime in REGIMES for annee in range(depuis, HORIZON + 1)}


def test_l_age_d_annulation_de_la_decote_est_celui_de_chaque_version():
    """`age_reference_decote_sncf_ratp` : aucune décote sous les règlements
    d'avant le 1er juillet 2008, ni à qui réunit les conditions avant le
    1er juillet 2010 ; puis l'âge minimum d'ouverture majoré de cinq ans,
    diminué de seize trimestres la première année, de deux de moins chaque
    1er juillet jusqu'en 2013 puis d'un, de rien depuis juillet 2024 ; à qui
    les réunit depuis le 1er janvier 2025, cinquante-sept ans pour l'agent de
    conduite et pour le roulant. Le barème des régimes spéciaux, lu au mois où
    les conditions sont réunies (`liquider.millesime_du_bareme`), et les tables
    d'âges que nomment les périodes le portent : une génération qui atteint
    son âge d'ouverture avant 2025 garde l'âge d'avant, quelle que soit
    l'année où elle part, comme la CPRPSNCF l'écrit."""
    bareme = DecoteRegimesSpeciaux(RACINE_DONNEES)
    ages = AgesRegimes(RACINE_DONNEES)
    for version in _versions("age_reference_decote_sncf_ratp"):
        lus, bornes = version["contenu"]["parametres"], version["bornes"]
        if "ouverture_du_droit" not in bornes:
            for regime in REGIMES:
                for annee in _annees_entieres(*bornes["liquidation.date_effet"]):
                    assert _periode(regime, annee)["decote_par_trimestre"] is None, (
                        version["id"], regime, annee)
            continue
        assert bornes["liquidation.date_effet"][0] == date(2008, 7, 1), version["id"]
        ouverture = bornes["ouverture_du_droit"]
        for mois in _mois(*ouverture):
            ligne = bareme.parametres(mois.annee + (mois.mois >= 7))
            if lus.get("majoration_de_l_age_minimum", 0) is None:
                assert ligne is None, (version["id"], str(mois))
                continue
            diminution = _escalier(lus.get("diminution_en_trimestres") or {"": 0},
                                   f"{mois.annee:04d}-{mois.mois:02d}")
            assert ligne is not None and ligne[0] == diminution, (version["id"], str(mois))
        if "majoration_de_l_age_minimum" in lus and lus["majoration_de_l_age_minimum"] is None:
            continue
        debut = ouverture[0].year if ouverture[0] else DEBUT.annee
        fin = ouverture[1].year if ouverture[1] else HORIZON + 1
        confrontees = 0
        for regime, table in _tables_d_ages(max(debut, 2011)):
            for generation in range(1930, 1996):
                age_ouverture, reference, _ = ages.ages(table, generation)
                # Le mois où le dernier-né de la génération, puis le premier,
                # atteint son âge d'ouverture.
                if not (debut <= generation + age_ouverture and generation + 11 / 12
                        + age_ouverture < fin):
                    continue
                confrontees += 1
                if "ages_de_reference" in lus:
                    assert reference == lus["ages_de_reference"][regime][SERVI[regime]], (
                        version["id"], table, generation)
                else:
                    assert reference - age_ouverture == pytest.approx(
                        lus["majoration_de_l_age_minimum"], abs=0.005), (table, generation)
        assert confrontees, version["id"]


def test_l_age_de_la_surcote_est_celui_de_chaque_version():
    """`age_surcote_sncf_ratp` : aucune surcote sous les règlements d'avant le
    1er juillet 2008 ; puis soixante ans ; à compter du 21 mars 2011, l'âge
    légal de soixante-deux ans, abaissé à soixante ans pour les nés avant
    1957 et relevé de quatre mois par génération ; pour les pensions de 2025
    et après, trois mois de plus par génération jusqu'à soixante-quatre ans
    pour 1970. Chaque année qu'une version couvre en entier, la période du
    régime branche l'âge propre de la surcote, et sa table donne à toute
    génération qui peut l'avoir l'âge que la version écrit."""
    surcote = AgesSurcoteRegimesSpeciaux(RACINE_DONNEES)
    confrontees = set()
    for version in _versions("age_surcote_sncf_ratp"):
        lus = version["contenu"]["parametres"]
        for regime in REGIMES:
            for annee in _annees_entieres(*version["bornes"]["liquidation.date_effet"]):
                periode = _periode(regime, annee)
                if lus["ages_de_surcote"] is None:
                    assert periode["surcote_par_trimestre"] is None, (version["id"], regime, annee)
                    confrontees.add(version["id"])
                    continue
                assert periode.get("age_surcote_regimes_speciaux"), (version["id"], regime, annee)
                for generation in range(max(annee - 75, 1900), annee - 50):
                    attendu = _escalier(lus["ages_de_surcote"], generation)
                    modele = surcote.age(generation)[0]
                    if _atteint(annee, generation, attendu, modele):
                        assert modele == pytest.approx(attendu, abs=0.005), (
                            version["id"], annee, generation)
                        confrontees.add(version["id"])
    assert confrontees == {v["id"] for v in _versions("age_surcote_sncf_ratp")}


def test_la_duree_requise_est_celle_de_chaque_version():
    """`duree_requise_sncf_ratp` : cent cinquante trimestres à qui réunit les
    conditions avant le 1er juillet 2008 ; puis le calendrier de la réforme,
    de 151 trimestres à 166 en juillet 2018, le même dans les deux décrets ;
    à compter du 1er juillet 2019, la table par génération de 2014 de chaque
    régime, lue, pour qui réunit les conditions avant cinquante-cinq ans
    (SNCF) ou soixante ans (RATP), à la génération qui atteint cet âge ce
    mois-là ; à compter du 1er janvier 2025, les tables de 2023, celle de
    l'agent de conduite à la SNCF avec ce que le II de l'article 35 retranche
    pour la décote, et, à la RATP, avant soixante ans, la durée par année de
    l'article 23-1. Le pourcentage maximum est de 75 %. Le calendrier et les
    tables du modèle le portent, au mois où les conditions sont réunies ; une
    table ne répond pas avant sa date."""
    calendriers = CalendriersDureeRequise(RACINE_DONNEES)
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    for version in _versions("duree_requise_sncf_ratp"):
        lus = version["contenu"]["parametres"]
        bornes = version["bornes"]["ouverture_du_droit"]
        annees, mois = _annees_entieres(*bornes), _mois(*bornes)
        for regime in REGIMES:
            for annee in annees:
                assert _periode(regime, annee)["taux_plein"] == lus["pourcentage_maximum"], (
                    version["id"], regime, annee)
        if "trimestres" in lus:
            assert {calendriers.trimestres("regimes_speciaux_2008", m.rang)[0]
                    for m in mois} == {lus["trimestres"]}, version["id"]
            for regime in REGIMES:
                assert {_periode(regime, annee)["duree_requise_trimestres"] for annee in annees} == {
                    lus["trimestres"]}, (version["id"], regime)
        if "calendrier" in lus:
            for m in mois:
                assert calendriers.trimestres("regimes_speciaux_2008", m.rang)[0] == _escalier(
                    lus["calendrier"], f"{m.annee:04d}-{m.mois:02d}"), (version["id"], str(m))
            for regime in REGIMES:
                assert {_periode(regime, annee).get("duree_requise_calendrier")
                        for annee in annees} == {"regimes_speciaux_2008"}, (version["id"], regime)
            for nom in ("sncf_2014", "ratp_2014", "sncf_conduite", "ratp", "ratp_avant_60"):
                assert tables.ligne(nom, 1975, mois[-1].rang) is None, (version["id"], nom)
        for cle, nom in TABLES_DU_MODELE.get(version["id"], {}).items():
            table = lus["tables_par_generation"][cle]
            for generation in _generations(table):
                ligne = tables.ligne(nom, generation, DateMois(HORIZON, 1).rang)
                assert (ligne and ligne[0]) == _escalier(table, generation), (nom, generation)
                retranche = _escalier((lus.get("retranche_decote") or {}).get(cle) or {}, generation)
                assert (ligne and ligne[1]) == (ligne and (retranche or 0)), (nom, generation)
            assert tables.ligne(nom, 1980, mois[0].plus_mois(-1).rang) is None, (nom, version["id"])
            assert all(nom in _periode(cle[:4], annee)["duree_requise_table"] for annee in annees), (
                nom, version["id"])
        for regime, nom in AVANT_L_AGE_DU_MODELE.get(version["id"], {}).items():
            age = lus["ages_de_lecture"][regime]
            for m in mois:
                # L'agent qui a cinquante-deux ans ce mois-là, et part avant l'âge de lecture.
                ligne = tables.ligne(nom, m.annee - 52 + (m.mois - 1) / 12, m.rang)
                attendu = (_escalier(lus["duree_avant_l_age_de_lecture"], m.annee)
                           if "duree_avant_l_age_de_lecture" in lus else
                           _escalier(lus["tables_par_generation"][regime],
                                     round(m.annee - age + (m.mois - 1) / 12, 3)))
                assert (ligne and ligne[0]) == attendu, (nom, str(m))
            assert tables.ligne(nom, 1980, mois[0].plus_mois(-1).rang) is None, (nom, version["id"])
            assert all(_periode(regime, annee)["duree_requise_table"][0] == nom
                       for annee in annees), (nom, version["id"])


#: La table du modèle qui porte chaque table d'une version de
#: `duree_requise_sncf_ratp` ; celle des autres agents de la SNCF, que le
#: modèle ne sert pas, n'est pas transcrite.
TABLES_DU_MODELE = {
    "table_de_2014": {"sncf": "sncf_2014", "ratp": "ratp_2014"},
    "tables_de_2023": {"sncf_agents_de_conduite": "sncf_conduite", "ratp": "ratp"},
}
#: La table du modèle, nommée la première par les périodes, qui porte ce que
#: doit l'agent qui part avant l'âge de lecture : la table de 2014, lue à la
#: génération qui atteint cet âge, puis, à la RATP, la durée par année de
#: 2025. Celle de l'article 12-1 de la SNCF n'est pas transcrite : le modèle
#: suit la table de l'agent de conduite, comme la CPRPSNCF, et la fiche
#: déclare l'écart.
AVANT_L_AGE_DU_MODELE = {
    "table_de_2014": {"sncf": "sncf_2014", "ratp": "ratp_2014"},
    "tables_de_2023": {"ratp": "ratp_avant_60"},
}


#: Pour les pensions de 2017 et après, l'agent qui peut partir avant
#: cinquante-cinq ans (SNCF, article 12-1) ou soixante ans (RATP, article
#: 23-1) doit la durée exigée des agents qui atteignent cet âge l'année où son
#: droit s'ouvre : la table de 2014 lue à la génération qui l'atteint ce
#: mois-là, comme la CPRPSNCF l'écrit pour l'agent de conduite — 167
#: trimestres pour le né de novembre 1968 à 1969, 168 pour 1970 et 1971, 169
#: pour 1972 ; à qui réunit les conditions depuis 2025, à la RATP, cent
#: soixante-dix trimestres, un de plus tous les trois ans, cent soixante-douze
#: en 2031. Cas par cas : le régime, le mois de naissance de l'agent, le mois
#: où son droit s'ouvre, l'année où sa pension prend effet, la durée que le
#: droit lui demande, et la version de `duree_requise_sncf_ratp` qui la porte.
AVANT_L_AGE_DE_LECTURE = [
    ("sncf", DateMois(1968, 11), DateMois(2019, 7), 2019, 167, "table_de_2014"),
    ("sncf", DateMois(1969, 12), DateMois(2020, 12), 2020, 167, "table_de_2014"),
    ("sncf", DateMois(1970, 1), DateMois(2021, 5), 2021, 168, "table_de_2014"),
    ("sncf", DateMois(1971, 12), DateMois(2023, 8), 2023, 168, "table_de_2014"),
    ("sncf", DateMois(1972, 1), DateMois(2024, 1), 2024, 169, "table_de_2014"),
    ("sncf", DateMois(1972, 1), DateMois(2024, 1), 2026, 169, "table_de_2014"),
    ("ratp", DateMois(1968, 11), DateMois(2019, 7), 2019, 167, "table_de_2014"),
    ("ratp", DateMois(1970, 1), DateMois(2021, 5), 2021, 168, "table_de_2014"),
    ("ratp", DateMois(1972, 1), DateMois(2024, 1), 2024, 169, "table_de_2014"),
    ("ratp", DateMois(1972, 1), DateMois(2024, 1), 2026, 169, "table_de_2014"),
    ("ratp", DateMois(1973, 1), DateMois(2025, 4), 2025, 170, "tables_de_2023"),
    ("ratp", DateMois(1975, 3), DateMois(2027, 12), 2027, 170, "tables_de_2023"),
    ("ratp", DateMois(1975, 4), DateMois(2028, 1), 2028, 171, "tables_de_2023"),
    ("ratp", DateMois(1977, 10), DateMois(2031, 1), 2031, 172, "tables_de_2023"),
]


@pytest.mark.parametrize("regime, naissance, ouverture, effet, droit, version",
                         AVANT_L_AGE_DE_LECTURE)
def test_qui_part_avant_l_age_de_lecture_doit_la_duree_de_qui_l_atteint(
        regime, naissance, ouverture, effet, droit, version):
    """Le droit de l'agent s'ouvre à l'âge que la table de sa période lui
    donne, avant l'âge de lecture ; la durée que le droit lui demande se lit
    dans la version, à la génération qui atteint cet âge le mois où son droit
    s'ouvre, ou, depuis 2025, à l'année ; le modèle, qui lit ses tables dans
    l'ordre que la période de sa pension nomme, lui oppose la même ; et la
    fiche ne déclare plus d'écart sur cette version pour ce régime."""
    fiche = carte.fiches()["duree_requise_sncf_ratp"]
    lus = next(v for v in fiche["versions"] if v["id"] == version)["contenu"]["parametres"]
    periode = _periode(regime, effet)
    generation = naissance.annee + (naissance.mois - 1) / 12
    age = AgesRegimes(RACINE_DONNEES).ages(periode["age_table"], generation)[0]
    assert naissance.plus_mois(en_mois(age)) == ouverture
    assert age < lus["ages_de_lecture"][regime]
    if "duree_avant_l_age_de_lecture" in lus:
        assert _escalier(lus["duree_avant_l_age_de_lecture"], ouverture.annee) == droit
    else:
        lue = ouverture.annee - lus["ages_de_lecture"][regime] + (ouverture.mois - 1) / 12
        assert _escalier(lus["tables_par_generation"][regime], round(lue, 3)) == droit
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    lignes = [tables.ligne(nom, generation, ouverture.rang)
              for nom in periode["duree_requise_table"]]
    assert next(ligne for ligne in lignes if ligne)[0] == droit
    assert not any(version in (a.get("version") or []) and a.get("regime") == regime
                   for a in fiche.get("approximations") or []), (regime, version)


def test_la_duree_par_annee_de_la_ratp_ne_sert_que_qui_part_avant_soixante_ans():
    """La table qui porte, depuis 2025, la durée par année de l'article 23-1
    (`ratp_avant_60`) se lit à la génération qui a soixante ans le mois où le
    droit s'ouvre ; à qui ouvrirait le sien à soixante ans ou après, elle se
    lirait à sa propre génération, et donnerait 170 trimestres aux nés de 1966
    et 1967 et 171 aux nés de 1968 à 1970, un de moins que l'article 51. Le
    modèle ne sert que le roulant : chaque table d'âges que nomment les
    périodes de 2025 et après, et l'âge qu'elles écrivent, ouvrent son droit
    avant soixante ans."""
    ages = AgesRegimes(RACINE_DONNEES)
    for annee in range(2025, HORIZON + 1):
        periode = _periode("ratp", annee)
        assert periode["duree_requise_table"][0] == "ratp_avant_60", annee
        assert periode["age_ouverture"] < 60, annee
        for generation in range(1940, 2000):
            lu = ages.ages(periode["age_table"], generation)
            assert lu is None or lu[0] is None or lu[0] < 60, (annee, generation)


#: Ce que le modèle fait autrement que le droit, cas par cas : le régime, le
#: mois de naissance de l'agent, le mois où son droit s'ouvre, la durée que
#: le droit lui demande, celle que le modèle lui oppose, et la version de
#: `duree_requise_sncf_ratp` qui déclare l'écart. Depuis 2025, l'article 12-1
#: de la SNCF demande à qui peut partir avant cinquante-cinq ans 170
#: trimestres, un de plus tous les trois ans ; le modèle lit la table de
#: l'agent de conduite à sa génération, comme la CPRPSNCF.
ECARTS_DECLARES = [
    ("sncf", DateMois(1975, 4), DateMois(2028, 1), 171, 170, "tables_de_2023"),
    ("sncf", DateMois(1977, 10), DateMois(2031, 1), 172, 171, "tables_de_2023"),
]


@pytest.mark.parametrize("regime, naissance, ouverture, droit, modele, version", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(regime, naissance, ouverture,
                                                            droit, modele, version):
    """La durée que le droit demande se lit dans la version, à la génération
    qui atteint l'âge de lecture le mois où le droit s'ouvre, ou, depuis
    2025, à l'année ; le modèle, qui lit ses tables dans l'ordre que la
    période nomme, en oppose une autre ; et la fiche déclare l'écart sur
    cette version."""
    fiche = carte.fiches()["duree_requise_sncf_ratp"]
    lus = next(v for v in fiche["versions"] if v["id"] == version)["contenu"]["parametres"]
    generation = naissance.annee + (naissance.mois - 1) / 12
    lue = min(generation, ouverture.annee + (ouverture.mois - 1) / 12 - lus["ages_de_lecture"][regime])
    if version == "tables_de_2023":
        assert _escalier(lus["duree_avant_l_age_de_lecture"], ouverture.annee) == droit
    else:
        assert _escalier(lus["tables_par_generation"][regime], round(lue, 3)) == droit
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    lignes = [tables.ligne(nom, generation, ouverture.rang)
              for nom in _periode(regime, ouverture.annee)["duree_requise_table"]]
    assert next(ligne for ligne in lignes if ligne)[0] == modele
    assert any(version in (a.get("version") or []) and a.get("regime") == regime
               for a in fiche.get("approximations") or []), (regime, version)
