"""L'agent de la Banque de France dont l'emploi ouvre le droit cinq ans plus tôt
(action 191 ; première des trois approximations de `decote_banque_de_france`).

Le règlement annexé au décret n° 2007-262 du 27 février 2007 ouvre le droit à
pension, à son article 26, à l'agent qui a « au moins l'âge de cinquante-cinq
ans s'il appartient à l'une des catégories dont la nomenclature est fixée par
délibération du conseil général » (rédaction d'origine, LEGIARTI000006778516).
Le décret n° 2012-701 du 7 mai 2012 porte cet âge à cinquante-sept ans, relevé
par semestre de naissance (article 72, I, 2°, LEGIARTI000025882187), le décret
n° 2014-669 du 23 juin 2014 décale ce relèvement de cinq générations
(LEGIARTI000029138467), et le décret n° 2023-693 du 28 juillet 2023 en fait
l'âge de L. 161-17-2 « abaissé de cinq années », relevé par génération, pour
les pensions prenant effet depuis le 1er janvier 2025 (LEGIARTI000047909725).

Sa décote s'annule cinq ans plus tôt aussi : le tableau de 2007 lui donne sa
colonne, « pour les agents dont les droits sont ouverts à l'âge de 55 ans » ;
depuis le 9 mai 2012, « pour les agents appartenant à une des catégories visées
au quatrième alinéa de l'article 26, l'âge visé au 2° est minoré de 20
trimestres » (article 70), comme la limite d'âge de l'article 32.

Les valeurs attendues sont lues dans ces textes et posées à la main : le taux
est de 75 %, diminué du coefficient par trimestre qui sépare l'âge de la
liquidation de l'âge d'annulation, la durée manquante étant ici toujours plus
longue (carrière commencée à vingt-huit ans). La saisie ne dit pas cette
catégorie par défaut, et rien ne change alors.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.web.site import rendre

from facade import Simulateur, ouvrir
from outils_pont import saisie_du_portage


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, naissance, mois, depart, active=True):
    return simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, sexe="H",
        affiliation="agent_banque_de_france", age_debut=28, age_liquidation=depart,
        invalidite={"banque": "active"} if active else None)


def _age(simulateur, naissance, mois, depart, active=True) -> float:
    return ouvrir.age_ouverture_droit(
        simulateur.scenario_actuel, _carriere(simulateur, naissance, mois, depart, active))


def _taux(simulateur, naissance, mois, depart, active=True) -> float:
    carriere = _carriere(simulateur, naissance, mois, depart, active)
    return simulateur.scenario_actuel.calculer(carriere).taux_liquidation


# -- l'âge d'ouverture ----------------------------------------------------------

@pytest.mark.parametrize("naissance, mois, depart, age", [
    # Pension de 2010, règlement de 2007 : « cinquante-cinq ans ».
    (1954, 1, 56, 55),
    # Pension de janvier 2013, décret de 2012 : « cinquante-cinq ans et neuf
    # mois pour les agents nés au premier semestre 1957 ».
    (1957, 1, 56, 55.75),
    # Le même, pension de 2015 : le décret de 2014 rend « cinquante-cinq ans
    # pour les agents nés avant le 1er janvier 1961 ».
    (1957, 1, 58, 55),
    # Décret de 2014 : « cinquante-cinq ans et neuf mois pour les agents nés au
    # premier semestre 1962 » ; cinquante-sept ans « aux agents nés à compter du
    # 1er juillet 1964 ».
    (1962, 1, 57, 55.75),
    (1964, 7, 58, 57),
    # Pensions depuis 2025, décret de 2023 : « cinquante-sept ans pour les agents
    # nés avant le 1er janvier 1968 », « cinquante-sept ans et six mois pour les
    # agents nés en 1969 », l'âge de L. 161-17-2 abaissé de cinq années, soit
    # cinquante-neuf ans, « aux agents nés à compter du 1er janvier 1975 ».
    (1967, 6, 58, 57),
    (1969, 1, 58, 57.5),
    (1975, 1, 60, 59),
])
def test_l_emploi_classe_ouvre_le_droit_a_l_age_de_l_article_72(
        simulateur, naissance, mois, depart, age):
    assert _age(simulateur, naissance, mois, depart) == pytest.approx(age)


def test_sans_la_categorie_l_age_reste_celui_du_modele(simulateur):
    """La question n'est pas posée par défaut : l'agent garde l'âge d'avant."""
    assert _age(simulateur, 1962, 1, 62, active=False) >= 60
    assert _age(simulateur, 1962, 1, 62, active=False) > _age(simulateur, 1962, 1, 62)


def test_la_pension_part_au_depart_saisi_avant_soixante_ans(simulateur):
    """Né en janvier 1962, parti à cinquante-sept ans en 2019 : la pension de la
    Banque est servie dès le départ, avec dix-neuf trimestres de décote jusqu'à
    61 ans et 9 mois ; sans la catégorie, vingt, le plafond de l'article 32."""
    carriere = _carriere(simulateur, 1962, 1, 57)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    banque = {p.regime: p for p in resultat.pensions_par_regime}["banque_de_france"]
    assert banque.montant > 0
    assert resultat.taux_liquidation == pytest.approx(0.75 * (1 - 19 * 0.0125))
    assert _taux(simulateur, 1962, 1, 57, active=False) == pytest.approx(
        0.75 * (1 - 20 * 0.0125))


# -- la décote ------------------------------------------------------------------

@pytest.mark.parametrize("naissance, mois, depart, trimestres, coefficient", [
    # « Jusqu'au 31 décembre 2008. Sans objet » : cinquante-cinq ans en janvier 2008.
    (1953, 1, 55, 0, 0.0),
    # « Du 1er janvier 2009 au 30 juin 2009. 0,125 % 61 ans 56 ans ».
    (1954, 1, 55, 4, 0.00125),
    (1954, 1, 56, 0, 0.0),
    # « Du 1er janvier 2011 au 30 juin 2011. 0,375 % 62 ans 57 ans » : parti à
    # cinquante-cinq ans et demi, en juillet 2011.
    (1956, 1, 55.5, 6, 0.00375),
])
def test_le_tableau_de_2007_lui_donne_la_colonne_des_agents_a_55_ans(
        simulateur, naissance, mois, depart, trimestres, coefficient):
    assert _taux(simulateur, naissance, mois, depart) == pytest.approx(
        0.75 * (1 - trimestres * coefficient))


@pytest.mark.parametrize("naissance, mois, depart, trimestres, coefficient", [
    # « 1er semestre 1955 0,875 % Lim. âge - 7 trimestres » : limite d'âge de
    # 64 ans et 9 mois (statut, article 241), soit 63 ans, minorés de vingt
    # trimestres : 58 ans. Parti à 57 ans et demi, en juillet 2012.
    (1955, 1, 57.5, 2, 0.00875),
    # « 1er semestre 1958 1,250 % Lim. âge - 5 trimestres » : 66 ans et 3 mois
    # moins cinq trimestres, 65 ans, minorés de vingt trimestres : 60 ans.
    (1958, 1, 58, 8, 0.0125),
    (1958, 1, 60, 0, 0.0),
    # « 1er semestre 1962 1,250 % Lim. âge - 1 trimestre » : 67 ans moins un
    # trimestre, minorés de vingt : 61 ans et 9 mois. Parti à 57 ans, en 2019.
    (1962, 1, 57, 19, 0.0125),
    # Né depuis 1963 : l'article 32 seul, « la limite d'âge est minorée de vingt
    # trimestres », 62 ans. Parti à 58 ans, en 2022.
    (1964, 1, 58, 16, 0.0125),
])
def test_depuis_2012_son_age_d_annulation_est_minore_de_vingt_trimestres(
        simulateur, naissance, mois, depart, trimestres, coefficient):
    assert _taux(simulateur, naissance, mois, depart) == pytest.approx(
        0.75 * (1 - trimestres * coefficient))


def test_sans_la_categorie_la_decote_reste_celle_de_droit_commun(simulateur):
    """Né en janvier 1958, parti à 62 ans : douze trimestres jusqu'à 65 ans, à
    1,25 % ; l'agent de la catégorie, qui a passé 60 ans, n'en a aucune."""
    assert _taux(simulateur, 1958, 1, 62, active=False) == pytest.approx(0.75 * (1 - 12 * 0.0125))
    assert _taux(simulateur, 1958, 1, 62) == pytest.approx(0.75)


# -- la saisie et le formulaire -------------------------------------------------

_AGENT = {"naissance": "1962", "debut": "28", "liquidation": "57",
          "statut": "agent_banque_de_france"}


def test_la_saisie_porte_la_categorie_et_la_reecrit():
    saisie = saisie_du_portage({**_AGENT, "banque": "active"})
    assert saisie.banque == "active"
    requete = saisie.requete()
    assert "banque=active" in requete.split("&")
    relue = saisie_du_portage(dict(c.split("=", 1) for c in requete.split("&")))
    assert relue.banque == "active"
    assert saisie.invalidite_declaree()["banque"] == "active"
    sans = saisie_du_portage(_AGENT)
    assert sans.banque == ""
    assert not any(c.startswith("banque=") for c in sans.requete().split("&"))


def test_la_question_ne_parait_qu_a_l_agent_de_la_banque():
    """Comme le menu de l'indice : avec une période d'agent titulaire de la
    Banque de France, ou une réponse déjà dite."""
    assert 'name="banque"' in rendre("/simuler", _AGENT)[1]
    salarie = {**_AGENT, "statut": "salarie_prive_non_cadre", "liquidation": "64"}
    assert 'name="banque"' not in rendre("/simuler", salarie)[1]
    assert 'name="banque"' in rendre("/simuler", {**salarie, "banque": "active"})[1]


def test_le_simulateur_sert_la_pension_de_l_agent_parti_a_57_ans():
    corps = rendre("/simuler", {**_AGENT, "banque": "active"})[1]
    assert "Saisie refusée" not in corps
