"""La durée requise lue à soixante ans : la CRPCEN, la Comédie-Française et la
Banque de France.

Pour les pensions de 2017 et après, trois textes écrivent la règle que
l'article 9-1 de l'annexe 3 des IEG donne aux agents des IEG (fiche
`regimes_speciaux_par_generation`) : le III de l'article 85 du décret
n° 90-1215 (CRPCEN, LEGIARTI000029134265, « pour les pensions prenant effet à
compter du 1er janvier 2017 », abrogé au 1er janvier 2025), le VI de
l'article 12 du décret n° 68-960 (Comédie-Française, LEGIARTI000029134341,
pour les mêmes pensions, en vigueur), et l'article 31-1 du règlement annexé
au décret n° 2007-262 (Banque de France, écrit en entier depuis le 26 juin
2014, LEGIARTI000029138467, abrogé au 1er janvier 2025, LEGIARTI000047909725).
La durée « est celle qui est en vigueur lorsque les assurés atteignent l'âge
de soixante ans » ; « par dérogation », à qui remplit les conditions de
liquidation avant cet âge, « celle exigée des assurés atteignant l'âge de
soixante ans l'année à compter de laquelle la liquidation peut intervenir ».

Le modèle lisait le calendrier de 2008 au mois où le droit s'ouvre, et les
tables de 2014 de la CRPCEN et de la Banque de France à la génération de
l'assuré. Deux conséquences. Le clerc ou le sociétaire né de mars à juin 1957,
ou de janvier à juin 1958, ouvre son droit après soixante ans, après une
marche du calendrier que ses soixante ans précèdent : il doit la durée de ses
soixante ans, 164 ou 165 trimestres, et non 165 ou 166. Et le clerc ou l'agent
de la Banque qui part avant soixante ans, au titre d'une carrière longue, doit
la durée de la génération qui atteint soixante ans le mois où il réunit les
conditions, et non celle de la sienne.

Les valeurs attendues viennent des textes, recopiés ici : le calendrier de
2008 et les tables de 2014, lus le 2 novembre 2026 dans l'index LEGI.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.scenarios.actuel import (
    CalendriersDureeRequise, DureesRequisesRegimes)
from retraite_notionnelle.simulateur import Simulateur

#: Le calendrier de 2008, au mois où les conditions sont réunies : « 151
#: trimestres pour les personnes remplissant les conditions [...] entre le
#: 1er juillet et le 31 décembre 2008 inclus », puis « elle augmente d'un
#: trimestre au 1er janvier et au 1er juillet de chaque année jusqu'au
#: 1er juillet 2012 inclus, d'un trimestre au 1er décembre 2012, puis d'un
#: trimestre au 1er juillet de chaque année jusqu'à atteindre la durée de 166
#: trimestres au 1er juillet 2018 » (Comédie-Française, V de l'article 12 du
#: décret n° 68-960, LEGIARTI000029134341 ; CRPCEN, I de l'article 85-2 du
#: décret n° 90-1215, LEGIARTI000029134271, les mêmes mots) ; 150 avant.
CALENDRIER_2008 = {
    DateMois(1900, 1): 150,
    DateMois(2008, 7): 151, DateMois(2009, 1): 152, DateMois(2009, 7): 153,
    DateMois(2010, 1): 154, DateMois(2010, 7): 155, DateMois(2011, 1): 156,
    DateMois(2011, 7): 157, DateMois(2012, 1): 158, DateMois(2012, 7): 159,
    DateMois(2012, 12): 160, DateMois(2013, 7): 161, DateMois(2014, 7): 162,
    DateMois(2015, 7): 163, DateMois(2016, 7): 164, DateMois(2017, 7): 165,
    DateMois(2018, 7): 166,
}
#: « A compter du 1er juillet 2019 », la durée par génération, la même dans
#: les deux décrets : 167 trimestres « pour les assurés nés entre le
#: 1er juillet 1959 et le 31 décembre 1960 », 168 pour 1961 à 1963, 169 pour
#: 1964 à 1966, 170 pour 1967 à 1969, 171 pour 1970 à 1972, 172 « à partir du
#: 1er janvier 1973 ».
TABLE_2014 = {1959.5: 167, 1961: 168, 1964: 169, 1967: 170, 1970: 171, 1973: 172}
DEPUIS_LA_TABLE_2014 = DateMois(2019, 7)
#: Banque de France, III de l'article 69 de son règlement (LEGIARTI000029138467),
#: « A compter du 1er janvier 2018 » : 167 trimestres des nés de 1958 à 1960,
#: 168 pour 1961 à 1963, 169 pour 1964 à 1966, 170 pour 1967 à 1969, 171 pour
#: 1970 à 1972, 172 à compter de 1973.
TABLE_2014_BANQUE_DE_FRANCE = {1958: 167, 1961: 168, 1964: 169, 1967: 170, 1970: 171,
                               1973: 172}
DEPUIS_LA_TABLE_2014_BANQUE_DE_FRANCE = DateMois(2018, 1)
#: Le régime, et le métier par lequel une carrière s'y affilie.
AFFILIATION = {"crpcen": "clerc_de_notaire", "comedie_francaise": "personnel_comedie_francaise",
               "banque_de_france": "agent_banque_de_france"}


def _escalier(table: dict, cle):
    """La valeur de la dernière clé qui ne dépasse pas ``cle``."""
    return table[max(k for k in table if k <= cle)]


def _generation(naissance: DateMois) -> float:
    return naissance.annee + (naissance.mois - 1) / 12


def _soixante_ans(naissance: DateMois) -> DateMois:
    return naissance.plus_mois(60 * 12)


def _duree_du_droit(naissance: DateMois, ouverture: DateMois) -> int:
    """La durée que le III de l'article 85 (CRPCEN) et le VI de l'article 12
    (Comédie-Française) demandent, pour une pension de 2017 et après, à qui
    réunit les conditions ce mois-là : celle en vigueur à ses soixante ans,
    ou, s'il les réunit plus tôt, celle des assurés qui atteignent soixante
    ans ce mois-là — le calendrier avant le 1er juillet 2019, la table par
    génération ensuite, lue à la génération qui a soixante ans à cette date."""
    lecture = min(ouverture, _soixante_ans(naissance), key=lambda m: m.rang)
    if lecture.rang < DEPUIS_LA_TABLE_2014.rang:
        return _escalier(CALENDRIER_2008, lecture)
    return _escalier(TABLE_2014, round(lecture.annee - 60 + (lecture.mois - 1) / 12, 3))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _duree_du_modele(simulateur: Simulateur, regime: str, naissance: DateMois,
                     age_liquidation: float) -> tuple[int, DateMois]:
    """La durée que le moteur oppose à la carrière qui liquide à cet âge, et
    le mois où il dit les conditions réunies."""
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance.annee, mois_naissance=naissance.mois, sexe="F",
        affiliation=AFFILIATION[regime], age_debut=22, age_liquidation=age_liquidation,
        niveau_salaire=1.0)
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue[regime].periode(carriere.annee_liquidation)
    ouverture = DateMois.depuis_rang(ouvrir.mois_ouverture_des_droits(scenario, periode, carriere))
    return ouvrir.duree_requise(scenario, periode, carriere)[0], ouverture


#: Qui ouvre son droit après soixante ans, à la CRPCEN (article 84 du décret
#: n° 90-1215) ou à la Comédie-Française (A du I de l'article 51 du décret
#: n° 68-960) : soixante ans et quatre mois pour la génération 1957, soixante
#: ans et huit mois pour 1958, soixante et un ans pour 1959. Cas par cas : le
#: mois de naissance, le mois où le droit s'ouvre, l'âge de la liquidation, et
#: la durée en vigueur à ses soixante ans — le calendrier de 2008 jusqu'en juin
#: 2019, la table de 2014 ensuite. Le modèle rendait 165 aux nés de mars à juin
#: 1957 et 166 aux nés de janvier à juin 1958 : la durée du mois où leur droit
#: s'ouvre, une marche plus haut.
APRES_SOIXANTE_ANS = [
    (DateMois(1957, 1), DateMois(2017, 5), 60 + 4 / 12, 164),
    (DateMois(1957, 3), DateMois(2017, 7), 60 + 4 / 12, 164),
    (DateMois(1957, 6), DateMois(2017, 10), 60 + 4 / 12, 164),
    (DateMois(1957, 7), DateMois(2017, 11), 60 + 4 / 12, 165),
    (DateMois(1958, 1), DateMois(2018, 9), 60 + 8 / 12, 165),
    (DateMois(1958, 6), DateMois(2019, 2), 60 + 8 / 12, 165),
    (DateMois(1958, 7), DateMois(2019, 3), 60 + 8 / 12, 166),
    (DateMois(1959, 1), DateMois(2020, 1), 61.0, 166),
    (DateMois(1959, 7), DateMois(2020, 7), 61.0, 167),
    # La même clerc née en mars 1957, partie à soixante-sept ans : la durée
    # reste celle de ses soixante ans, sous la période de 2024 ; né en janvier
    # 1958, parti en 2025, il garde la durée d'avant, ses conditions réunies
    # avant 2025 (I bis de l'article 85-2).
    (DateMois(1957, 3), DateMois(2017, 7), 67.0, 164),
    (DateMois(1958, 1), DateMois(2018, 9), 67.0, 165),
]


@pytest.mark.parametrize("regime", ["crpcen", "comedie_francaise"])
@pytest.mark.parametrize("naissance, ouverture, age_liquidation, droit", APRES_SOIXANTE_ANS)
def test_qui_ouvre_son_droit_apres_soixante_ans_doit_la_duree_de_ses_soixante_ans(
        simulateur, regime, naissance, ouverture, age_liquidation, droit):
    """La durée posée à la main est celle du texte ; le droit s'ouvre le mois
    où l'âge de la table de la période est atteint, après les soixante ans ;
    et le moteur oppose la durée en vigueur à ces soixante ans."""
    assert _duree_du_droit(naissance, ouverture) == droit
    assert ouverture.rang > _soixante_ans(naissance).rang
    modele, ouvert = _duree_du_modele(simulateur, regime, naissance, age_liquidation)
    assert ouvert == ouverture, (regime, str(naissance))
    assert modele == droit, (regime, str(naissance), age_liquidation)


@pytest.mark.parametrize("regime", ["crpcen", "comedie_francaise"])
def test_generation_par_generation_le_moteur_rend_la_duree_du_texte(simulateur, regime):
    """Chaque mois de naissance de 1955 à 1961, parti le mois où son droit
    s'ouvre, avant, à ou après soixante ans : la durée que le moteur oppose
    est celle des textes, lue au mois de ses soixante ans ou, plus tôt, au
    mois où il réunit les conditions."""
    ecarts = []
    for rang in range(DateMois(1955, 1).rang, DateMois(1961, 12).rang + 1):
        naissance = DateMois.depuis_rang(rang)
        carriere = simulateur.carriere_simple(
            annee_naissance=naissance.annee, mois_naissance=naissance.mois, sexe="F",
            affiliation=AFFILIATION[regime], age_debut=22, age_liquidation=67.0,
            niveau_salaire=1.0)
        scenario = simulateur.scenario_actuel
        periode = simulateur.catalogue[regime].periode(carriere.annee_liquidation)
        ouverture = DateMois.depuis_rang(ouvrir.mois_ouverture_des_droits(
            scenario, periode, carriere))
        modele = ouvrir.duree_requise(scenario, periode, carriere)[0]
        droit = _duree_du_droit(naissance, ouverture)
        if modele != droit:
            ecarts.append((str(naissance), str(ouverture), droit, modele))
    assert ecarts == []


def test_les_tables_lues_a_soixante_ans_sont_le_calendrier_a_soixante_ans():
    """Les tables que les fiches de la CRPCEN et de la Comédie-Française
    nomment pour les pensions de 2017 et après portent, génération par
    génération, la marche du calendrier de 2008 que cette génération atteint à
    soixante ans ; elles ne répondent qu'aux conditions réunies depuis le
    1er janvier 2017 et se lisent, avant soixante ans, à la génération qui les
    atteint."""
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    calendriers = CalendriersDureeRequise(RACINE_DONNEES)
    for nom in ("crpcen_calendrier_a_60", "comedie_francaise_calendrier_a_60"):
        for rang in range(DateMois(1956, 7).rang, DateMois(1959, 6).rang + 1):
            naissance = DateMois.depuis_rang(rang)
            soixante = _soixante_ans(naissance)
            ligne = tables.ligne(nom, _generation(naissance), DateMois(2030, 1).rang)
            assert ligne is not None and ligne[0] == _escalier(CALENDRIER_2008, soixante), (
                nom, str(naissance))
            assert ligne[0] == calendriers.trimestres("regimes_speciaux_2008", soixante.rang)[0]
        assert tables.ligne(nom, 1957.0, DateMois(2016, 12).rang) is None, nom
        # Avant soixante ans, en mars 2018 : la génération de mars 1958.
        assert tables.ligne(nom, 1960.0, DateMois(2018, 3).rang)[0] == 165, nom


#: Qui part avant soixante ans, au titre d'une carrière longue : la durée
#: exigée des assurés qui atteignent soixante ans le mois où il réunit les
#: conditions (III de l'article 85 de la CRPCEN, de 2017 à 2024 ; article 31-1
#: de la Banque de France, de 2014 à 2024), lue dans la table de 2014 à leur
#: génération. Depuis 2025, les deux articles abrogés, la table de 2023 se lit
#: à la génération de l'assuré. Cas par cas : le régime, le mois de naissance,
#: le mois où les conditions sont réunies, et la durée que le droit demande ;
#: le modèle rendait celle de sa propre génération, un trimestre de plus.
AVANT_SOIXANTE_ANS = [
    ("crpcen", DateMois(1961, 7), DateMois(2020, 7), 167),
    ("crpcen", DateMois(1962, 1), DateMois(2021, 1), 168),
    ("crpcen", DateMois(1964, 1), DateMois(2022, 1), 168),
    ("crpcen", DateMois(1967, 1), DateMois(2024, 12), 169),
    ("crpcen", DateMois(1967, 1), DateMois(2025, 1), 172),
    ("banque_de_france", DateMois(1961, 1), DateMois(2020, 1), 167),
    ("banque_de_france", DateMois(1964, 1), DateMois(2023, 1), 168),
    ("banque_de_france", DateMois(1965, 6), DateMois(2025, 1), 171),
]


@pytest.mark.parametrize("regime, naissance, ouverture, droit", AVANT_SOIXANTE_ANS)
def test_qui_part_avant_soixante_ans_doit_la_duree_de_qui_les_atteint(
        regime, naissance, ouverture, droit):
    """La durée posée à la main se lit dans la table de 2014 du texte, à la
    génération qui a soixante ans le mois où les conditions sont réunies ; les
    tables que nomme la période de la pension, dans l'ordre, la rendent."""
    import yaml

    assert ouverture.rang < _soixante_ans(naissance).rang
    lue = round(ouverture.annee - 60 + (ouverture.mois - 1) / 12, 3)
    if ouverture.rang < DateMois(2025, 1).rang:
        table = TABLE_2014 if regime == "crpcen" else TABLE_2014_BANQUE_DE_FRANCE
        assert _escalier(table, lue) == droit
    periodes = yaml.safe_load((RACINE_DONNEES / "reference" / "regimes" / f"{regime}.yaml")
                              .read_text(encoding="utf-8"))["periodes"]
    periode = next(p for p in periodes if p["debut"] <= ouverture.annee
                   and (p["fin"] is None or ouverture.annee <= p["fin"]))
    tables = DureesRequisesRegimes(RACINE_DONNEES)
    lignes = [tables.ligne(nom, _generation(naissance), ouverture.rang)
              for nom in periode["duree_requise_table"]]
    assert next(ligne for ligne in lignes if ligne)[0] == droit, (regime, str(naissance))


def test_le_modele_ouvre_la_carriere_longue_a_la_crpcen_et_a_la_banque_de_france(simulateur):
    """La lecture d'avant soixante ans sert : entré à quinze ans, né en
    janvier 1962, le clerc ou l'agent de la Banque part à cinquante-neuf ans,
    au titre d'une carrière longue."""
    for regime in ("crpcen", "banque_de_france"):
        carriere = simulateur.carriere_simple(
            annee_naissance=1962, mois_naissance=1, sexe="F", affiliation=AFFILIATION[regime],
            age_debut=15, age_liquidation=59.0, niveau_salaire=1.0)
        actuel = simulateur.simuler(carriere).actuel
        assert actuel.motif_ouverture == "carriere_longue", regime
        assert actuel.liquidation_ouverte, regime
