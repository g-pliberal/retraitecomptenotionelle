"""La clause de sauvegarde de la carrière longue de 2023, et le taux plein de
la retraite anticipée pour carrière longue.

Décret n° 2023-436 du 3 juin 2023, article 8 : « les assurés nés entre le
1er septembre 1961 et le 31 décembre 1963 et qui justifient, avant le
1er septembre 2023, d'une durée d'assurance mentionnée aux articles D. 16-1 et
D. 16-2 du code des pensions civiles et militaires de retraite, D. 732-40 du
code rural et de la pêche maritime et L. 161-17-3, D. 351-1-1 et D. 351-1-2 du
code de la sécurité sociale, dans leur rédaction antérieure à l'entrée en
vigueur du présent décret, peuvent demander à bénéficier, pour une pension
prenant effet à compter du 1er septembre 2023, d'un âge d'ouverture du droit à
pension abaissé dans les conditions prévues » aux mêmes articles « dans leur
rédaction antérieure ».

Circulaire Cnav n° 2023-14 du 10 juillet 2023, point 9.2 : les trimestres de
l'AVPF ne comptent pas dans la durée acquise avant le 1er septembre 2023 ;
« la retraite est calculée au taux plein, conformément aux dispositions de
l'article L. 351-8, 4° ter » ; la durée de proratisation « doit tenir compte de
l'augmentation de la durée nécessaire pour obtenir le taux plein ». Ses trois
exemples sont les cas d'ici. Le 4° ter de L. 351-8, « les assurés dont l'âge
[…] est abaissé dans des conditions prévues à l'article L. 351-1-1 », vaut pour
les pensions prenant effet à compter du 1er septembre 2023 ; L. 14 du code des
pensions et L. 732-25 du code rural écrivent la même chose à la même date, et
l'Agirc-Arrco suit le taux plein du régime général (accord du 17 novembre
2017, article 84, 3).
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois

import facade
from facade import Simulateur, departs
from outils_pont import Saisies


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: Le salarié du privé de la saisie, au salaire moyen.
_SALARIE = {"sexe": "H", "enfants": "0", "salaire": "1", "unite_revenu": "moyen",
            "profil": "plat", "statut": "salarie_prive_non_cadre"}


def _liquide(simulateur: Simulateur, **saisie):
    carriere = Saisies().carriere({**_SALARIE, **saisie})
    return carriere, simulateur.scenario_actuel.calculer(carriere)


def _pension(resultat, regime: str):
    return next(p for p in resultat.pensions_par_regime if p.regime == regime)


def test_l_exemple_1_de_la_circulaire_part_au_taux_plein_sur_168_trimestres(simulateur):
    """« Assuré né le 4/02/1962. Il réunit uniquement 168 trimestres cotisés au
    30/06/2023. […] A sa demande, il peut obtenir une RACL à effet du
    1/10/2023, à 61 ans et 7 mois. La retraite sera calculée au taux plein. La
    durée de proratisation sera égale à 168/169. » La rédaction de 2023 lui
    demande les 169 trimestres de sa génération, qu'il n'a pas."""
    carriere, resultat = _liquide(
        simulateur, naissance="1962-02-04", debut="1981-01", liquidation="2023-10",
        interruptions="2023:2023:sans_activite")
    assert facade.trimestres_actuels(carriere) == 168
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.liquidation_ouverte
    assert resultat.age_ouverture_opposable == 60.0
    assert resultat.taux_liquidation == 0.5
    assert resultat.trimestres_requis == 169
    assert _pension(resultat, "regime_general").detail.endswith("taux 50.000% × 168/169")
    # L'Agirc-Arrco sert sans coefficient d'anticipation la pension de qui a
    # celle du régime général au taux plein (accord de 2017, article 84, 3).
    assert "anticipation" not in _pension(resultat, "arrco").detail


def test_l_exemple_2_de_la_circulaire_part_a_soixante_ans(simulateur):
    """« Assurée née le 13/10/1963. Elle réunit 168 trimestres cotisés au
    30/06/2023 et 4 trimestres de majoration de durée d'assurance pour enfant.
    […] A sa demande, elle peut obtenir une RACL à effet du 1/11/2023, à
    60 ans. La retraite sera calculée au taux plein. La durée de proratisation
    sera égale à 170/170. » La rédaction de 2023 lui demande soixante ans et
    trois mois, et 170 trimestres cotisés. Entrée en novembre 1981 à 0,6 fois
    le salaire moyen, elle gagne cette année-là 1 074 €, qui valent deux
    trimestres de 200 heures au SMIC du 1er janvier 1981, 2,254721 € (R. 351-9
    CSS : 1 074 / 450,94 = 2,4) ; puis quatre par an de 1982 à 2022."""
    carriere, resultat = _liquide(
        simulateur, sexe="F", enfants="1", salaire="0.6", naissance="1963-10-13",
        debut="1981-11", liquidation="2023-11")
    # 2 + 164 + 2 = 168 au 30 juin 2023, et le troisième trimestre civil de 2023.
    assert facade.trimestres_actuels(carriere) == 169
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.age_ouverture_opposable == 60.0
    assert resultat.taux_liquidation == 0.5
    assert _pension(resultat, "regime_general").detail.endswith("taux 50.000% × 170/170")


def test_l_exemple_3_de_la_circulaire_n_a_pas_la_clause(simulateur):
    """« Assurée née le 4/02/1963. Elle réunit uniquement 164 trimestres
    cotisés au titre de son activité au 30/06/2023 et 4 trimestres d'AVPF. […]
    Elle ne pourra pas bénéficier de la clause de sauvegarde au 01/10/2023. »
    Ses droits s'étudient sous la rédaction de 2023, qui lui demande 170
    trimestres : elle en a 168, l'AVPF comprise."""
    carriere, resultat = _liquide(
        simulateur, sexe="F", enfants="1", naissance="1963-02-04", debut="1981-01",
        liquidation="2023-10",
        interruptions="1990:1990:education_enfant, 2023:2023:sans_activite")
    # 164 de son activité et 4 de l'AVPF.
    assert facade.trimestres_actuels(carriere) == 168
    assert resultat.motif_ouverture == "non_ouverte"


def test_la_clause_ne_garde_rien_a_qui_est_ne_apres_1963(simulateur):
    """« Les assurés nés entre le 1er septembre 1961 et le 31 décembre 1963 » :
    née le 15 janvier 1964, elle a en août 2023 les 169 trimestres que la
    rédaction d'avant demandait à sa génération pour partir à soixante ans.
    Celle de 2023 lui en demande 171, à soixante ans et six mois : en février
    2024, à soixante ans, son droit n'est pas ouvert. Entrée en décembre 1980
    à 0,6 fois le salaire moyen, elle gagne cette année-là 473 €, qui valent
    un trimestre de 200 heures au SMIC du 1er janvier 1980, 1,971166 €
    (R. 351-9 CSS : 473 / 394,23 = 1,2) ; puis quatre par an de 1981 à 2022."""
    carriere, resultat = _liquide(
        simulateur, sexe="F", salaire="0.6", naissance="1964-01-15", debut="1980-12",
        liquidation="2024-02", interruptions="2023:2023:sans_activite")
    assert facade.trimestres_actuels(carriere) == 169
    assert resultat.motif_ouverture == "non_ouverte"


def test_la_clause_garde_son_age_au_fonctionnaire(simulateur):
    """L'article 8 nomme D. 16-1 et D. 16-2 du code des pensions : le
    fonctionnaire de l'exemple 1 part de même, et sa pension ne porte pas de
    coefficient de minoration, qui « n'est pas applicable aux assurés dont
    l'âge […] est abaissé dans les conditions prévues à l'article L. 25 bis »
    (L. 14, I, rédaction du 1er septembre 2023)."""
    carriere, resultat = _liquide(
        simulateur, statut="fonctionnaire_etat", naissance="1962-02-04", debut="1981-01",
        liquidation="2023-10", interruptions="2023:2023:sans_activite")
    assert facade.trimestres_actuels(carriere) == 168
    assert resultat.motif_ouverture == "carriere_longue"
    assert "décote" not in _pension(resultat, "fonction_publique_etat").detail


def test_le_regime_qui_attend_ne_garde_la_date_d_avant_qu_aux_generations_de_la_clause(
        simulateur):
    """Partie de l'hôpital en août 2023 avec les 169 trimestres que la
    rédaction d'avant demandait aux nés de 1964, elle est née le 15 janvier
    1964 : l'article 8 ne lui garde pas les soixante ans de cette rédaction, et
    la rédaction de 2023 lui demande 171 trimestres à soixante ans et six mois,
    celle de 2026 170, qu'elle n'a pas. Son régime général la sert donc à son
    âge légal : soixante-deux ans et neuf mois pour une pension prenant effet
    à compter du 1er septembre 2026 (L. 161-17-2, loi n° 2025-1403), atteints
    le 15 octobre 2026, soit le 1er novembre 2026 — et non le 1er février
    2024, ses soixante ans de la rédaction d'avant. Entrée en novembre 1981
    au salaire moyen, elle gagne cette année-là 1 791 €, qui valent trois
    trimestres de 200 heures au SMIC du 1er janvier 1981, 2,254721 €
    (R. 351-9 CSS : 1 791 / 450,94 = 3,97) ; puis 164 de 1982 à 2022, et deux
    en 2023 avant la date d'effet."""
    carriere = Saisies().carriere({
        "sexe": "F", "enfants": "0", "salaire": "1", "unite_revenu": "moyen",
        "profil": "plat", "statut": "salarie_prive_non_cadre",
        "metier2_statut": "fonctionnaire_territorial_hospitalier_actif",
        "metier2_debut": "1995-01", "naissance": "1964-01-15", "debut": "1981-11",
        "liquidation": "2023-08"})
    assert facade.trimestres_actuels(carriere) == 169
    lus = [(depart.date, sorted(depart.regimes))
           for depart in departs.departs(simulateur.scenario_actuel, carriere)]
    assert lus[1] == (DateMois(2026, 11), ["arrco", "arrco_tranche_2", "regime_general"])
