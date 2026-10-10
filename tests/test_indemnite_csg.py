"""Tests de ce que la fiche de paie d'un agent public portait mal jusqu'au
10 octobre 2026 : la RAFP, l'indemnité compensatrice de la hausse de la CSG,
et l'assiette du taux d'équilibre de l'État (action 138, étape 12).

L'indemnité se vérifie d'abord contre ses textes — l'exemple du réexamen de
2019 que donne la circulaire du 15 janvier 2018, au centime, et les trois
coefficients du décret n° 2017-1889, que la circulaire dérive des taux de la
CSG et de la CRDS —, puis sur la fiche : dans le brut, hors de la retenue,
dans la RAFP. La RAFP se vérifie sous les deux systèmes, la proposition la
gardant ; le taux d'équilibre, sur le seul traitement.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.carriere import Affiliations
from retraite_notionnelle.donnees.indemnite_csg import charger_indemnite_csg
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import (
    ConstructeurFiche,
    beneficiaire_indemnite_csg,
    bloc_droit_en_vigueur,
    bloc_taux_unique,
    charger_prelevements,
    fiche_depuis_brut,
    smic_annuel,
)
from retraite_notionnelle.simulateur import Simulateur

PARAMETRES = Parametres()
RACINE = PARAMETRES.racine_donnees
ANNEE = PARAMETRES.annee_bascule


@pytest.fixture(scope="module")
def table():
    return charger_indemnite_csg(RACINE)


@pytest.fixture(scope="module")
def pieces():
    return {
        "macro": DonneesMacro(RACINE, PARAMETRES.scenario_projection),
        "catalogue": CatalogueRegimes(RACINE),
        "affiliations": Affiliations(RACINE),
    }


def _ligne(fiche, code: str, employeur: bool = False) -> float:
    return sum(ligne.employeur if employeur else ligne.salarie
               for ligne in fiche.lignes if ligne.code == code)


# -- l'indemnité, contre ses textes -------------------------------------------


def test_le_reexamen_de_2019_rejoue_l_exemple_de_la_circulaire(table):
    """« un adjoint administratif principal […] ayant perçu une rémunération
    brute annuelle 2017 de 23 500 € et bénéficiant d'une indemnité
    compensatrice de 17 € par mois » : sa rémunération de 2018 portée à
    25 200 €, « le montant actualisé de l'indemnité compensatrice est de
    18,23 € par mois » ; réduite à 23 200 €, « le montant […] n'évolue pas »
    (circulaire du 15 janvier 2018, VI). La circulaire ne dit pas sa CES : on
    la déduit des 17 €."""
    deduits = table.taux_hausse_csg * 23_500 - 17.0 * 12 / table.coefficient
    progresse = table.montants({2017: 23_500, 2018: 25_200, 2019: 25_200}, deduits)
    assert progresse[2018] / 12 == pytest.approx(17.0, abs=1e-9)
    assert round(progresse[2019] / 12, 2) == 18.23
    recule = table.montants({2017: 23_500, 2018: 23_200, 2019: 23_200}, deduits)
    assert recule[2019] == pytest.approx(recule[2018], rel=1e-12)


def test_les_trois_coefficients_sont_ceux_des_taux_de_la_csg(table):
    """1,6702 % = 1,7 × 98,25 % ; 1,1053 = 1 / (1 − 9,7 % × 98,25 %) ; 0,76 %
    = (1,7 − 1) × 98,25 % × 1,1053 (circulaire, annexes 1 et 3), sur la CSG,
    la CRDS et l'abattement que la fiche de paie de l'agent prélève."""
    profil = charger_prelevements(RACINE).profil("agent_seul")
    assiette = 1.0 - profil.abattement_frais[0].taux
    assert table.taux_hausse_csg == pytest.approx(0.017 * assiette, abs=1e-6)
    assert table.coefficient == pytest.approx(
        1.0 / (1.0 - (profil.csg + profil.crds) * assiette), abs=1e-4)
    assert table.taux_recrutes == pytest.approx(
        (0.017 - table.taux_ces) * assiette * table.coefficient, abs=1e-5)


def test_la_ces_de_2017_suit_son_seuil_et_son_plafond(table):
    """1 % de la rémunération nette de ses cotisations, dans la limite de
    quatre plafonds (L. 5423-27), rien sous le traitement de l'indice majoré
    313 (R. 5423-52)."""
    plafond = 39_228.0
    seuil = table.seuil_ces_annuel
    assert seuil == pytest.approx(313 * 56.2323)
    assert table.contribution_de_solidarite(30_000, 3_000, seuil - 1, plafond) == 0.0
    assert table.contribution_de_solidarite(30_000, 3_000, seuil, plafond) == pytest.approx(270.0)
    assert table.contribution_de_solidarite(200_000, 20_000, 150_000, plafond) == pytest.approx(
        0.01 * 4 * plafond)


def test_un_agent_recrute_depuis_2018_touche_0_76_pour_cent_puis_les_reevaluations(table):
    """II et III de l'article 2 : 0,76 % de sa première rémunération. Pas de
    réexamen en 2019, réservé aux agents du I ; en 2020, seulement si la
    rémunération a progressé ; depuis 2021, dans les deux sens."""
    montants = table.montants({2018: 30_000, 2019: 31_000, 2020: 31_000,
                               2021: 30_000, 2022: 33_000})
    assert montants[2018] == pytest.approx(0.0076 * 30_000)
    assert montants[2019] == pytest.approx(montants[2018])
    assert montants[2020] == pytest.approx(montants[2018] * 31_000 / 30_000)
    assert montants[2021] == pytest.approx(montants[2020])
    assert montants[2022] == pytest.approx(montants[2021] * 30_000 / 31_000)
    baisse_2020 = table.montants({2018: 30_000, 2019: 29_000, 2020: 29_000})
    assert baisse_2020[2020] == pytest.approx(baisse_2020[2018])


def test_une_annee_sans_paie_reporte_le_reexamen(table):
    """La circulaire reporte au retour le réexamen de l'agent qui n'est pas
    payé au 1er janvier : l'indemnité ne bouge pas tant que les deux années
    comparées ne le sont pas."""
    montants = table.montants({2017: 30_000, 2018: 30_000, 2022: 36_000, 2023: 36_000,
                               2024: 40_000})
    assert montants[2022] == montants[2023] == pytest.approx(montants[2018])
    assert montants[2024] == pytest.approx(montants[2018])
    assert 2020 not in montants


# -- la fiche de paie d'un agent public ---------------------------------------


def test_seuls_les_agents_publics_a_retenue_la_touchent(pieces):
    """Fonctionnaires, militaires, ouvriers de l'État ; ni le contractuel, dont
    la maladie et la CES de 2017 absorbaient presque tout, ni le marin ou
    l'artiste de l'Opéra, qui ne sont pas des agents publics."""
    oui = ("fonctionnaire_etat", "fonctionnaire_territorial_hospitalier", "militaire",
           "policier", "aide_soignant", "sapeur_pompier_professionnel", "ouvrier_etat")
    non = ("contractuel_public", "marin", "personnel_opera", "salarie_prive_non_cadre",
           "artisan")
    for statut in oui:
        assert beneficiaire_indemnite_csg(pieces["affiliations"], pieces["catalogue"],
                                          statut, ANNEE), statut
    for statut in non:
        assert not beneficiaire_indemnite_csg(pieces["affiliations"], pieces["catalogue"],
                                              statut, ANNEE), statut


def test_l_indemnite_est_dans_le_brut_hors_de_la_retenue_et_dans_la_rafp(pieces):
    """Elle s'ajoute au revenu, ne grossit pas la retenue pour pension, entre
    dans la RAFP quand les primes laissent de la place sous les 20 % du
    traitement, et ne laisse au net que ce que la CSG, la CRDS et la RAFP lui
    prennent."""
    revenu, indemnite = 40_000.0, 400.0

    def fiche(indemnite: float, part_primes: float):
        return fiche_depuis_brut(RACINE, pieces["macro"], pieces["catalogue"],
                                 pieces["affiliations"], "fonctionnaire_etat", ANNEE,
                                 revenu, part_primes, indemnite)

    sans, avec = fiche(0.0, 0.10), fiche(indemnite, 0.10)
    assert avec.brut == pytest.approx(revenu + indemnite)
    assert _ligne(avec, "fonction_publique_etat") == pytest.approx(
        _ligne(sans, "fonction_publique_etat"), rel=1e-12)
    assert _ligne(avec, "rafp") - _ligne(sans, "rafp") == pytest.approx(0.05 * indemnite)
    csg = _ligne(avec, "csg_crds") - _ligne(sans, "csg_crds")
    assert avec.net - sans.net == pytest.approx(indemnite - csg - 0.05 * indemnite)
    # Au-delà du plafond de 20 % du traitement, la RAFP ne prend plus rien.
    plafonnees = fiche(0.0, 0.25), fiche(indemnite, 0.25)
    assert _ligne(plafonnees[1], "rafp") == pytest.approx(_ligne(plafonnees[0], "rafp"))


def test_la_fonctionnaire_de_l_exemple_touche_son_indemnite_et_paie_la_rafp():
    """La fonctionnaire du README, née en 1975, entrée à vingt-deux ans, un
    cinquième de primes : en poste fin 2017, elle relève du I de l'article 2.
    Sa fiche de 2026 porte l'indemnité, de l'ordre de 0,8 % de son revenu, et
    la RAFP sur ses primes, plafonnées à 20 % du traitement, sous les deux
    systèmes, au même taux de la rémunération entière."""
    simulateur = Simulateur(PARAMETRES)
    remuneration = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat", age_debut=22,
        age_liquidation=64, part_primes=0.2, profil_carriere="ascendant")).remuneration
    annee = remuneration.reference
    actuelle, proposee = annee.droit_en_vigueur, annee.proposition
    revenu = actuelle.brut - annee.indemnite_csg
    assert 0.006 * revenu < annee.indemnite_csg < 0.010 * revenu
    traitement = 0.8 * revenu
    assert _ligne(actuelle, "rafp") == pytest.approx(0.05 * 0.20 * traitement, rel=1e-9)
    assert _ligne(actuelle, "rafp", employeur=True) == pytest.approx(
        _ligne(actuelle, "rafp"), rel=1e-12)
    assert _ligne(proposee, "rafp") / proposee.brut == pytest.approx(
        _ligne(actuelle, "rafp") / actuelle.brut, rel=1e-9)
    assert remuneration.indemnite_csg_mensuelle == pytest.approx(annee.indemnite_csg / 12)


def test_sans_isoler_la_capitalisation_la_proposition_remplace_la_rafp():
    """Quand le compte convertit la RAFP en capital notionnel, elle est de la
    répartition : le taux unique la remplace, et la fiche de la proposition ne
    la prélève plus."""
    parametres = replace(PARAMETRES, isoler_capitalisation=False)
    simulateur = Simulateur(parametres)
    annee = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat", age_debut=22,
        age_liquidation=64, part_primes=0.2)).remuneration.reference
    assert _ligne(annee.droit_en_vigueur, "rafp") > 0.0
    assert _ligne(annee.proposition, "rafp") == 0.0


# -- le taux d'équilibre de l'État, sur le seul traitement ---------------------


def test_le_taux_d_equilibre_ne_porte_que_sur_le_traitement(pieces):
    """La contribution de l'État est une part du traitement, l'assiette de la
    retenue, sans les primes (``contribution_employeur_public.csv``) : ce
    qu'elle libère sous la proposition se calcule sur lui seul. À part de
    traitement de 80 %, une rémunération de 50 000 € libère 82,28 % de
    40 000 €, moins la part patronale du taux unique sur les 50 000 €."""
    profil = charger_prelevements(RACINE).profil("agent_seul")
    constructeur = ConstructeurFiche(profil)
    macro, catalogue, affiliations = pieces["macro"], pieces["catalogue"], pieces["affiliations"]
    plafond, smic = macro.plafond_securite_sociale(ANNEE), smic_annuel(macro, ANNEE)
    brut, taux = 50_000.0, 0.8228
    actuel = bloc_droit_en_vigueur(catalogue, affiliations, "fonctionnaire_etat", ANNEE, 0.0)
    fiche = constructeur.fiche(ANNEE, brut, plafond, smic, actuel)

    def traitement_propose(part_traitement: float) -> float:
        propose = bloc_taux_unique(
            PARAMETRES.taux_cotisation_liberal, 0.0, PARAMETRES.part_salariale_taux_unique,
            part_rendue_aux_salaires=1.0, contribution_equilibre_actuelle=taux,
            part_traitement=part_traitement)
        return constructeur.brut_partage(fiche, plafond, smic, propose)

    patronal = PARAMETRES.taux_cotisation_liberal * (1.0 - PARAMETRES.part_salariale_taux_unique)
    # Tout ce qui est libéré revient (part rendue de un) : le nouveau brut
    # épuise la dépense d'aujourd'hui, traitement et taux d'équilibre.
    for part in (1.0, 0.8):
        depense = fiche.cout_du_travail + taux * part * brut
        assert traitement_propose(part) * (1.0 + patronal) == pytest.approx(depense, rel=1e-9)
