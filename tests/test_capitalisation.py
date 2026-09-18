"""Tests du pilier de capitalisation obligatoire.

Ce compartiment est le seul du modèle où de l'argent est réellement placé :
une erreur de convention y produit un capital plausible et faux, que rien ne
signale. Les tests ci-dessous vérifient donc, d'abord, des IDENTITÉS — des
égalités que l'arithmétique impose, indépendamment des données —, et seulement
ensuite des ordres de grandeur.
"""

from __future__ import annotations

import math

import pytest
import yaml

from retraite_notionnelle.config import (
    Parametres,
    RACINE_DONNEES,
    TableConversion,
)
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.frais import FraisEpargneRetraite
from retraite_notionnelle.donnees.mortalite import DonneesMortalite
from retraite_notionnelle.donnees.taux import CourbeTauxSansRisque, TauxPlacement
from retraite_notionnelle.moteur.capitalisation import (
    HORIZON_LONG,
    MATURITES,
    ConstructeurCapitalisation,
    repartition,
)
from retraite_notionnelle.moteur.conversion import Convertisseur
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def courbe() -> CourbeTauxSansRisque:
    return CourbeTauxSansRisque(RACINE_DONNEES)


@pytest.fixture(scope="module")
def mortalite() -> DonneesMortalite:
    return DonneesMortalite(RACINE_DONNEES, cache_disque=False)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


class CourbePlate:
    """Courbe fictive à taux unique, pour les tests d'identité.

    Quand toutes les maturités rendent le même taux, l'échelle de maturités
    n'a plus d'effet : le capital admet une forme close, et c'est elle qui
    permet de vérifier la convention de date et l'application des frais sans
    dépendre d'aucune donnée.
    """

    def __init__(self, taux: float) -> None:
        self.taux = taux
        self.annee = 2026
        self.date = "2026-01-01"

    def placement(self, annee_placement: int, duree: int) -> TauxPlacement:
        return TauxPlacement(
            taux=self.taux, differe=max(0, annee_placement - self.annee),
            duree=duree, fiabilite=Fiabilite.CERTIFIEE,
        )


# -- la courbe et ses forwards ------------------------------------------------


def test_la_courbe_lue_est_la_plus_recente_publiee(courbe):
    """Une courbe est un instantané : deux dates ne se mélangent pas."""
    assert courbe.date.startswith("20")
    assert courbe.annee == int(courbe.date[:4])
    assert courbe.maturites[0] == 1
    assert courbe.maturite_maximale >= HORIZON_LONG
    assert courbe.fiabilite_publiee == Fiabilite.CERTIFIEE


def test_le_taux_annuel_est_le_taux_continu_compose(courbe):
    """La BCE publie en composition continue ; le modèle accumule en annuel."""
    for maturite in (1, 5, 10, 30):
        attendu = math.exp(courbe.zero_continu(maturite)) - 1.0
        assert courbe.placement(courbe.annee, maturite).taux == pytest.approx(attendu)


def test_les_forwards_se_chainent_exactement(courbe):
    """Dix ans puis dix ans doivent valoir vingt ans, au centime près.

    C'est l'identité qui définit un taux forward : si elle était fausse, le
    modèle offrirait — ou retirerait — un rendement d'arbitrage à qui replace
    son capital à l'échéance, ce qui est précisément ce que fait l'échelle.
    """
    for depart, duree in ((10, 10), (5, 15), (1, 4), (12, 18)):
        direct = courbe.placement(courbe.annee, depart + duree).taux
        premier = courbe.placement(courbe.annee, depart).taux
        second = courbe.placement(courbe.annee + depart, duree).taux
        assert (1 + premier) ** depart * (1 + second) ** duree == pytest.approx(
            (1 + direct) ** (depart + duree), rel=1e-12
        )


def test_au_dela_de_la_courbe_le_taux_est_prolonge_a_plat_et_declare_estime(courbe):
    maximum = courbe.maturite_maximale
    assert courbe.zero_continu(maximum + 40) == pytest.approx(courbe.zero_continu(maximum))
    assert courbe.placement(courbe.annee, maximum).fiabilite == Fiabilite.CERTIFIEE
    assert courbe.placement(courbe.annee + 1, maximum).fiabilite == Fiabilite.ESTIMEE


def test_une_duree_nulle_est_refusee(courbe):
    with pytest.raises(ValueError):
        courbe.forward_continu(0, 0)


# -- l'échelle de maturités ---------------------------------------------------


def test_la_repartition_est_une_repartition(courbe):
    """Les poids somment à un, et aucune maturité ne dépasse l'horizon."""
    for horizon in range(1, 60):
        parts = repartition(horizon)
        assert sum(poids for _, poids in parts) == pytest.approx(1.0)
        assert all(poids > 0 for _, poids in parts)
        assert max(maturite for maturite, _ in parts) <= horizon


def test_l_allocation_glisse_du_long_vers_le_court():
    """Principalement longue au début, principalement courte à la fin.

    C'est la règle demandée, et elle se vérifie sur la part placée à plus de
    dix ans : elle croît avec l'horizon, sans jamais atteindre la totalité —
    une épargne obligatoire ne se concentre pas sur un seul point de la courbe.
    """
    def part_longue(horizon: int) -> float:
        return sum(p for maturite, p in repartition(horizon) if maturite > 10)

    def part_courte(horizon: int) -> float:
        return sum(p for maturite, p in repartition(horizon) if maturite <= 2)

    longues = [part_longue(h) for h in range(1, 45)]
    assert longues == sorted(longues), "la part longue doit croître avec l'horizon"
    assert part_longue(40) == pytest.approx(0.75)
    assert part_longue(40) < 1.0, "il reste d'autres maturités en début de carrière"
    assert part_longue(10) == 0.0

    courtes = [part_courte(h) for h in range(3, 45)]
    assert courtes == sorted(courtes, reverse=True)
    assert part_courte(2) == pytest.approx(1.0), "à deux ans, tout est court"
    assert part_courte(1) == pytest.approx(1.0)

    assert repartition(0) == ()


def test_les_maturites_de_l_echelle_sont_des_points_cotes(courbe):
    assert set(MATURITES) <= set(courbe.maturites)


# -- l'accumulation, sur une courbe plate -------------------------------------


def _constructeur(taux: float, mortalite, parametres: Parametres):
    return ConstructeurCapitalisation(
        CourbePlate(taux), mortalite, Convertisseur(mortalite, parametres), parametres
    )


def test_le_capital_a_la_forme_close_quand_la_courbe_est_plate(mortalite):
    """Identité de référence : versement crédité en fin d'année, puis
    ``(1 + taux)(1 - frais)`` par année restante.

    Elle vérifie d'un coup la convention de date — un versement ne rapporte pas
    l'année de son versement, exactement comme au compte notionnel —, l'ordre
    des prélèvements et l'absence d'année offerte ou perdue.
    """
    parametres = Parametres()
    constructeur = _constructeur(0.03, mortalite, parametres)
    assiettes = {annee: 30_000.0 for annee in range(2026, 2041)}

    pilier = constructeur.construire(
        assiettes=assiettes, annee_naissance=1990,
        age_liquidation=50.0, annee_liquidation=2040,
    )

    net = 30_000.0 * parametres.taux_capitalisation_obligatoire * (
        1 - parametres.frais_versement_capitalisation
    )
    facteur = (1 + 0.03) * (1 - parametres.frais_gestion_capitalisation)
    attendu = sum(net * facteur ** (2040 - annee) for annee in range(2026, 2041))
    assert pilier.capital == pytest.approx(attendu)

    # Le versement de l'année de liquidation est bien porté, et bien sans
    # intérêt : c'est le dernier terme de la somme, à l'exposant zéro.
    assert pilier.annees[-1].versement_net == pytest.approx(net)
    assert pilier.annees[-1].encours - pilier.annees[-2].encours * facteur == (
        pytest.approx(net)
    )


def test_sans_frais_le_capital_est_celui_de_la_courbe_seule(mortalite):
    parametres = Parametres(
        frais_versement_capitalisation=0.0,
        frais_gestion_capitalisation=0.0,
    )
    constructeur = _constructeur(0.04, mortalite, parametres)
    assiettes = {annee: 40_000.0 for annee in range(2026, 2036)}
    pilier = constructeur.construire(
        assiettes=assiettes, annee_naissance=1990,
        age_liquidation=45.0, annee_liquidation=2035,
    )
    brut = 40_000.0 * parametres.taux_capitalisation_obligatoire
    attendu = sum(brut * 1.04 ** (2035 - annee) for annee in range(2026, 2036))
    assert pilier.capital == pytest.approx(attendu)
    assert pilier.capital_hors_frais == pytest.approx(pilier.capital)
    assert pilier.frais_preleves == 0.0
    assert pilier.taux_rendement_annuel == pytest.approx(0.04)


def test_les_frais_coutent_plus_que_ce_qu_ils_prelevent(mortalite, simulateur):
    """Le coût complet des frais dépasse les frais prélevés.

    La différence est le rendement que les sommes prélevées n'ont pas produit.
    L'afficher évite la lecture naïve « 0,76 % par an, donc 0,76 % en moins ».
    """
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1995, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=23, age_liquidation=64,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    assert pilier.frais_preleves > 0
    assert pilier.cout_des_frais > pilier.frais_preleves
    assert pilier.capital_hors_frais > pilier.capital


def test_le_taux_de_rendement_interne_reconstitue_le_capital(simulateur):
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1995, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=23, age_liquidation=64,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    taux = pilier.taux_rendement_annuel
    reconstitue = sum(
        annee.versement_brut * (1 + taux) ** (pilier.annee_liquidation - annee.annee)
        for annee in pilier.annees
    )
    assert reconstitue == pytest.approx(pilier.capital, rel=1e-6)
    # Frais compris, le pilier rend moins que le taux sans risque à dix ans.
    assert 0.0 < taux < 0.04


# -- la rente et sa table -----------------------------------------------------


def test_la_rente_est_le_capital_divise_puis_ampute_des_frais_d_arrerages(simulateur):
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1992, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    attendu = (pilier.capital / pilier.conversion.diviseur) * (
        1 - pilier.frais_arrerages
    )
    assert pilier.rente_annuelle == pytest.approx(attendu)
    assert pilier.rente_mensuelle == pytest.approx(pilier.rente_annuelle / 12)


def test_au_taux_technique_nul_les_deux_diviseurs_sont_le_meme(simulateur):
    """La rente du PER et la pension notionnelle partagent alors leur table.

    C'est ce qui rend les deux lignes comparables : à capital égal, elles
    servent le même montant, et tout écart vient d'ailleurs — des frais, du
    rendement, de la date des versements.
    """
    assert simulateur.parametres.taux_technique_rente_capitalisation == 0.0
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1992, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    resultat = comparaison.notionnel_liberal
    assert resultat.capitalisation.conversion.diviseur == pytest.approx(
        resultat.conversion.diviseur
    )


def test_un_taux_technique_positif_augmente_la_rente_initiale():
    """Il verse davantage au début et moins ensuite, à coût inchangé."""
    base = Simulateur(Parametres())
    anticipe = Simulateur(Parametres(taux_technique_rente_capitalisation=0.0125))
    carriere = dict(annee_naissance=1992, sexe="H",
                    affiliation="salarie_prive_non_cadre",
                    age_debut=22, age_liquidation=64)
    sans = base.simuler(base.carriere_simple(**carriere)).notionnel_liberal
    avec = anticipe.simuler(anticipe.carriere_simple(**carriere)).notionnel_liberal
    assert avec.capitalisation.capital == pytest.approx(sans.capitalisation.capital)
    assert avec.capitalisation.rente_annuelle > sans.capitalisation.rente_annuelle
    # La pension de répartition, elle, n'a pas bougé d'un centime.
    assert avec.pension_annuelle == pytest.approx(sans.pension_annuelle)


# -- l'héritage ---------------------------------------------------------------


def test_le_capital_transmissible_est_l_encours_de_chaque_annee(simulateur):
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1995, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=23, age_liquidation=64,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    assert all(a.capital_transmissible == a.encours for a in pilier.annees)
    encours = [a.encours for a in pilier.annees]
    assert encours == sorted(encours), "l'encours d'un placement sans risque ne recule pas"
    assert pilier.annees[-1].encours == pytest.approx(pilier.capital)


def test_l_esperance_de_capital_transmis_est_encadree(simulateur):
    """Elle vaut au plus le capital, et au moins zéro — et elle croît avec l'âge.

    Deux carrières identiques, l'une liquidée à 62 ans, l'autre à 67 : la
    seconde accumule plus longtemps et meurt plus souvent avant d'avoir
    liquidé. Les deux effets vont dans le même sens, et l'espérance transmise
    doit donc croître.
    """
    def pilier(age_liquidation: float):
        return simulateur.simuler(simulateur.carriere_simple(
            annee_naissance=1995, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=23, age_liquidation=age_liquidation,
        )).notionnel_liberal.capitalisation

    tot = pilier(62.0)
    tard = pilier(67.0)
    for p in (tot, tard):
        assert 0 < p.esperance_capital_transmis < p.capital
        assert 0 < p.probabilite_deces_avant_liquidation < 0.5
    assert tard.esperance_capital_transmis > tot.esperance_capital_transmis
    assert (tard.probabilite_deces_avant_liquidation
            > tot.probabilite_deces_avant_liquidation)


def test_la_transmission_suit_la_table_du_modele(mortalite):
    """L'espérance transmise se recalcule à la main, sur la même table.

    Elle n'est pas une approximation : c'est la somme, année par année, de la
    probabilité de mourir cette année-là par l'encours moyen de l'année.
    """
    parametres = Parametres()
    constructeur = _constructeur(0.03, mortalite, parametres)
    assiettes = {annee: 30_000.0 for annee in range(2026, 2041)}
    pilier = constructeur.construire(
        assiettes=assiettes, annee_naissance=1990,
        age_liquidation=50.0, annee_liquidation=2040, sexe="H",
    )
    survie = mortalite.courbe(36.0, 2026.0, None, parametres.table_generation)
    attendu = sum(
        (survie[i] - survie[i + 1]) * 0.5 * (a.encours_ouverture + a.encours)
        for i, a in enumerate(pilier.annees[:-1])
    )
    assert pilier.esperance_capital_transmis == pytest.approx(attendu)
    assert pilier.probabilite_deces_avant_liquidation == pytest.approx(
        survie[0] - survie[len(pilier.annees) - 1]
    )


# -- le branchement dans la proposition ---------------------------------------


def test_le_pilier_ne_touche_a_aucun_autre_scenario(simulateur):
    """Seule la proposition le porte ; les cinq autres scénarios l'ignorent."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    for nom in ("notionnel_retroactif", "notionnel_prospectif",
                "notionnel_retroactif_employeur", "notionnel_prospectif_employeur"):
        resultat = getattr(comparaison, nom)
        assert resultat.capitalisation is None
        assert resultat.rente_capitalisation_obligatoire == 0.0
        assert resultat.pension_totale == resultat.pension_annuelle
    assert comparaison.notionnel_liberal.capitalisation is not None


def test_la_pension_de_repartition_ne_bouge_pas_avec_le_pilier():
    """Le retirer ne doit rien changer à ce que la répartition sert.

    C'est la garantie que le pilier s'AJOUTE : s'il déplaçait la pension
    notionnelle d'un centime, c'est qu'il aurait pris quelque chose au compte.
    """
    avec = Simulateur(Parametres())
    sans = Simulateur(Parametres(capitalisation_obligatoire=False))
    carriere = dict(annee_naissance=1990, sexe="F",
                    affiliation="salarie_prive_non_cadre",
                    age_debut=22, age_liquidation=64)
    resultat_avec = avec.simuler(avec.carriere_simple(**carriere)).notionnel_liberal
    resultat_sans = sans.simuler(sans.carriere_simple(**carriere)).notionnel_liberal

    assert resultat_sans.pension_annuelle == pytest.approx(resultat_avec.pension_annuelle)
    assert resultat_sans.capitalisation.capital == 0.0
    assert resultat_sans.pension_totale == pytest.approx(resultat_sans.pension_annuelle)
    assert resultat_avec.pension_totale > resultat_avec.pension_annuelle


def test_rien_avant_l_annee_de_bascule(simulateur):
    """Les années d'avant gardent leurs taux et ne versent rien au pilier."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=64,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    assert pilier.annee_ouverture == simulateur.parametres.annee_debut_capitalisation
    assert min(a.annee for a in pilier.annees) == 2026
    assert all(a.versement_brut == 0 for a in pilier.annees if a.annee < 2026)


def test_qui_a_liquide_avant_la_bascule_n_a_pas_de_pilier(simulateur):
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1940, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=60,
    ))
    pilier = comparaison.notionnel_liberal.capitalisation
    assert pilier.annees == ()
    assert pilier.capital == 0.0
    assert pilier.rente_annuelle == 0.0
    assert comparaison.notionnel_liberal.pension_totale == pytest.approx(
        comparaison.notionnel_liberal.pension_annuelle
    )


def test_la_cotisation_capitalisee_s_ajoute_a_la_meme_assiette(simulateur):
    """Cinq points EN PLUS, sur la même base, la même année.

    Le versement de chaque année doit valoir exactement 5 % de l'assiette sur
    laquelle la cotisation notionnelle a été prélevée. C'est ce qui interdit
    au pilier de se construire une assiette à lui — plafonnée autrement, ou
    servie les années d'interruption.
    """
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    resultat = comparaison.notionnel_liberal
    assiettes = {c.annee: c.assiette_retenue for c in resultat.compte.cotisations}
    for annee in resultat.capitalisation.annees:
        attendue = assiettes.get(annee.annee, 0.0)
        assert annee.assiette == pytest.approx(attendue)
        assert annee.versement_brut == pytest.approx(
            attendue * simulateur.parametres.taux_capitalisation_obligatoire
        )


def test_le_pilier_porte_la_fiabilite_de_ses_frais(simulateur):
    """Un barème saisi plafonne le résultat à ``haute``, comme toute série."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    assert comparaison.notionnel_liberal.capitalisation.fiabilite <= Fiabilite.HAUTE


# -- le barème de frais -------------------------------------------------------


def test_les_frais_du_calcul_sont_ceux_du_fichier_de_reference():
    """Le calcul et la page Données ne peuvent pas dire deux choses.

    Les valeurs sont dans :class:`Parametres`, comme tout ce qui se fait
    varier ; leur source est dans ``frais_epargne_retraite.yaml``. Ce test est
    le seul lien entre les deux, et il doit rester.
    """
    frais = FraisEpargneRetraite(RACINE_DONNEES)
    parametres = Parametres()
    assert frais.valeur("versement") == parametres.frais_versement_capitalisation
    assert frais.valeur("gestion") == parametres.frais_gestion_capitalisation
    assert frais.valeur("arrerages") == parametres.frais_arrerages_capitalisation
    assert frais.fiabilite == Fiabilite.HAUTE
    assert frais.annee_reference >= 2025


def test_le_manifeste_porte_les_deux_sources_du_pilier():
    """La courbe et les frais ont chacun leur entrée, et disent leurs réserves."""
    manifeste = yaml.safe_load(
        (RACINE_DONNEES / "sources.yaml").read_text(encoding="utf-8"))
    par_id = {
        jeu["id"]: jeu
        for institution in manifeste["institutions"].values()
        for jeu in institution.get("jeux", [])
    }

    courbe = par_id["bce_courbe_taux_aaa"]
    assert courbe["statut_integration"] == "certifie"
    assert courbe["acces"] == "api"
    assert "AAA" in courbe["note"] and "risque de crédit" in courbe["note"]

    frais = par_id["opef_rapport_annuel"]
    assert frais["statut_integration"] == "saisi"
    assert "haute" in frais["note"]


# -- vraisemblance ------------------------------------------------------------


def test_le_pilier_pese_ce_qu_une_carriere_entiere_a_cinq_pour_cent_peut_peser(simulateur):
    """Ordre de grandeur, sur une carrière complète cotisée dès la bascule.

    Une personne entrée dans la vie active en 2026 verse 5 % pendant plus de
    quarante ans à un taux de l'ordre de 3 % : la rente doit peser une fraction
    notable de la pension notionnelle, sans jamais s'en approcher — le compte
    notionnel porte, lui, plus de vingt points de cotisation.
    """
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=2004, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    ))
    resultat = comparaison.notionnel_liberal
    part = resultat.rente_capitalisation_obligatoire / resultat.pension_totale
    assert 0.15 < part < 0.40
    assert resultat.capitalisation.rendement_cumule > 1.3


def test_la_table_par_sexe_change_la_rente_et_pas_le_capital():
    """La table ne joue qu'à la liquidation : le capital, lui, est le même."""
    unisexe = Simulateur(Parametres())
    sexuee = Simulateur(Parametres(table_conversion=TableConversion.PAR_SEXE))
    carriere = dict(annee_naissance=1995, sexe="F",
                    affiliation="salarie_prive_non_cadre",
                    age_debut=23, age_liquidation=64)
    a = unisexe.simuler(unisexe.carriere_simple(**carriere)).notionnel_liberal
    b = sexuee.simuler(sexuee.carriere_simple(**carriere)).notionnel_liberal
    assert b.capitalisation.capital == pytest.approx(a.capitalisation.capital)
    # Une femme vit plus longtemps : sa rente baisse sur table sexuée.
    assert b.capitalisation.rente_annuelle < a.capitalisation.rente_annuelle
