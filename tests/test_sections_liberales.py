"""Ce que la CNAVPL, la CAVAMAC, la CAVEC et la Cipav servent, lu au texte.

La passe du 23 septembre 2026 sur les dernières sections libérales (action 89)
a lu les pages et le guide de la CNAVPL, les statuts de la CAVAMAC de 2011 et
de 2023 et ceux de la CAVEC depuis 2008 au Journal officiel, et le décret
n° 2026-418 dans ses articles des trois sections. Ce fichier tient ce qu'elle
a corrigé.

**Deux complémentaires minoraient comme le régime de base, et ne le font pas.**
La CAVAMAC compte les années qui séparent de son taux plein — 5 % par tranche
de douze mois jusqu'en 2023, 1,25 % par trimestre manquant jusqu'à 67 ans
depuis 2024 —, la CAVEC les trimestres qui séparent de 65 ans ; la durée
d'assurance n'y ouvre rien. Les fiches laissaient la durée annuler la
minoration : un agent général ou un expert-comptable parti à l'âge légal avec
sa durée ne perdait rien, quand ses statuts lui retirent 15 % ou davantage.

**Trois enfants majorent de 10 %** la complémentaire de la CAVAMAC depuis ses
statuts de 2011, celle de la Cipav depuis 2000 au moins, celle de la CAVEC
depuis l'arrêté du 4 juillet 2025. Aucune fiche ne la portait.

**La CNAVPL rend aux mères la majoration de durée d'assurance** depuis le
1er avril 2010 (L. 643-1-1). Le moteur ne la cherchait que dans les régimes en
annuités ; une libérale qui n'avait cotisé qu'à sa section n'en recevait rien.

**Sa valeur de service est celle qu'elle publie**, datée depuis 2004, et non
la valeur de 2021 déflatée vers le passé.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, LigneRelevee, Metier
from retraite_notionnelle.droit import compter
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              liquidation: float, debut: float = 21.0, sexe: str = "H",
              enfants: int = 0, interruptions: dict[int, str] | None = None):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=1.0)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
        interruptions=interruptions,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient écrit dans le détail d'une pension en points, 1 sans."""
    for marque in ("coefficient d'anticipation ", "coefficient de majoration "):
        if marque in detail:
            return float(detail.split(marque)[1].split()[0])
    return 1.0


def _majoration(resultat, regime: str) -> float:
    """La majoration pour enfants que le scénario 1 sert à ce régime."""
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            return dict(avantage.par_regime).get(regime, 0.0)
    return 0.0


# -- la CAVAMAC ----------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Statuts de 2011, supposés les mêmes avant : taux plein à l'âge légal
    # augmenté de cinq ans — 65 ans pour ces générations —, 5 % par tranche de
    # douze mois d'anticipation, l'année entamée comptant entière.
    (1945, 64.0, 0.95),
    (1945, 63.25, 0.90),
    # La génération 1925 n'est pas dans la table du 1° de L. 351-8 : la fiche
    # lui donne 65 ans, et non les 67 ans d'aujourd'hui.
    (1925, 64.0, 0.95),
    # 2019 : taux plein à 67 ans pour la génération 1955, trois années.
    (1955, 64.0, 0.85),
    (1955, 64.25, 0.85),
    # Depuis 2024 : 1,25 % par trimestre manquant jusqu'à 67 ans.
    (1964, 63.0, 0.80),
    (1975, 64.0, 0.85),
    (1975, 67.0, 1.0),
])
def test_la_cavamac_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                          coefficient):
    """Carrière commencée à 21 ans : la durée est réunie partout, et c'est le
    cas où la fiche ne minorait rien."""
    resultat, pensions = _calculer(simulateur, "agent_general_assurance",
                                   naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(
        coefficient)


def test_la_cavamac_majore_par_annee_pleine_et_depuis_2024_par_annee_cotisee(
        simulateur):
    # Statuts de 2011 : « pour chaque année pleine différée » au-delà du taux
    # plein, 65 ans pour la génération 1950 — deux années à 67 ans.
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1950, 67.0)
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.10)
    # Depuis 2024, « pour chaque année pleine COTISÉE » : deux années de
    # travail au-delà de 67 ans valent 10 %…
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1960, 69.0)
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.10)
    # … et deux années d'attente, rien.
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1960, 69.0,
                            interruptions={2027: "sans_activite",
                                           2028: "sans_activite"})
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.0)


def test_la_cavamac_majore_de_dix_pour_cent_pour_trois_enfants(simulateur):
    resultat, pensions = _calculer(simulateur, "agent_general_assurance", 1960,
                                   67.0, sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == pytest.approx(
        0.10 * pensions["cavamac_complementaire"].montant)
    # Avant les statuts de 2011, rien n'est lu, rien n'est servi.
    resultat, _ = _calculer(simulateur, "agent_general_assurance", 1945, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == 0.0


# -- la CAVEC -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # « Entre 60 et 65 ans, avec application d'un abattement définitif de
    # 1,25 % par trimestre manquant » : neuf trimestres à 62 ans et 9 mois,
    # la durée fût-elle réunie.
    (1964, 62.75, 0.8875),
    (1950, 60.0, 0.75),
    # Avant 2008 aussi : la caisse garde 65 ans depuis 1983.
    (1940, 62.0, 0.85),
    (1961, 65.0, 1.0),
])
def test_la_cavec_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                        coefficient):
    resultat, pensions = _calculer(simulateur, "expert_comptable", naissance,
                                   liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavec_complementaire"].detail) == pytest.approx(
        coefficient)


def test_la_cavec_majore_pour_trois_enfants_depuis_2026(simulateur):
    resultat, pensions = _calculer(simulateur, "expert_comptable", 1961, 65.0,
                                   sexe="F", enfants=3)
    assert _majoration(resultat, "cavec_complementaire") == pytest.approx(
        0.10 * pensions["cavec_complementaire"].montant)
    resultat, _ = _calculer(simulateur, "expert_comptable", 1959, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cavec_complementaire") == 0.0


# -- la Cipav -------------------------------------------------------------------


def test_la_cipav_majore_pour_trois_enfants_depuis_2000(simulateur):
    resultat, pensions = _calculer(simulateur, "profession_liberale", 1945, 65.0,
                                   sexe="F", enfants=3)
    assert _majoration(resultat, "cipav_complementaire") == pytest.approx(
        0.10 * pensions["cipav_complementaire"].montant)
    resultat, _ = _calculer(simulateur, "profession_liberale", 1930, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cipav_complementaire") == 0.0


# -- la CNAVPL ------------------------------------------------------------------


def test_la_cnavpl_donne_aux_meres_leurs_trimestres_depuis_2010(simulateur):
    """Huit trimestres par enfant, portés par un régime en points."""
    avec, pensions = _calculer(simulateur, "profession_liberale", 1964, 62.75,
                               debut=24.0, sexe="F", enfants=2)
    sans, pensions_sans = _calculer(simulateur, "profession_liberale", 1964, 62.75,
                                    debut=24.0, sexe="F")
    assert avec.trimestres_valides - sans.trimestres_valides == 16
    # Sans eux, la décote de la CNAVPL — et celle de la Cipav, qui la suit.
    assert _coefficient(pensions_sans["cnavpl"].detail) < 1.0
    assert _coefficient(pensions["cnavpl"].detail) == pytest.approx(1.0)
    assert _coefficient(pensions["cipav_complementaire"].detail) == pytest.approx(1.0)
    # Avant le 1er avril 2010, la CNAVPL n'en donnait aucun.
    avant, _ = _calculer(simulateur, "profession_liberale", 1948, 60.0,
                         debut=24.0, sexe="F", enfants=2)
    avant_sans, _ = _calculer(simulateur, "profession_liberale", 1948, 60.0,
                              debut=24.0, sexe="F")
    assert avant.trimestres_valides == avant_sans.trimestres_valides


def test_la_majoration_de_duree_n_ouvre_pas_les_bonifications_des_mines(simulateur):
    """Seule `mda` passe par un régime en points : les mines déclarent des
    bonifications, qui entrent aux services qu'elles n'ont pas."""
    periode = simulateur.catalogue["mines"].periode(2020)
    assert periode.type_calcul == "points"
    assert "bonifications" in periode.avantages_non_contributifs
    mere = Carriere.depuis_parcours(
        annee_naissance=1958, sexe="F",
        metiers=[Metier(affiliation="salarie_prive_non_cadre", age_debut=20.0)],
        age_liquidation=62.0, macro=simulateur.macro, nombre_enfants=2,
    )
    actuel = simulateur.scenario_actuel
    assert compter.majoration_pour_enfants(actuel, mere, {"mines": 160}, 2020) is None
    porteur = compter.majoration_pour_enfants(actuel, mere, {"cnavpl": 160}, 2020)
    assert porteur is not None and porteur.regime == "cnavpl"
    assert porteur.trimestres == 16


@pytest.mark.parametrize("annee,valeur", [
    (2004, 0.484), (2005, 0.493), (2008, 0.522), (2014, 0.562),
    # Deux valeurs en 2022 : 0,5795 € au 1er janvier, 0,6027 € au 1er juillet,
    # et c'est celle du 31 décembre qui vaut pour l'année.
    (2022, 0.6027), (2026, 0.6599),
])
def test_la_valeur_de_service_de_la_cnavpl_est_celle_qu_elle_publie(
        simulateur, annee, valeur):
    lue = simulateur.scenario_actuel.valeurs_point.service("cnavpl", annee)
    assert lue is not None and lue[0] == pytest.approx(valeur)


@pytest.mark.parametrize("revenu,points", [(20_000, 238.6), (80_000, 565.5)])
def test_les_points_des_exemples_de_la_cnavpl(simulateur, revenu, points):
    """Page « Comprendre sa retraite » de la CNAVPL, paramètres de 2025 : « Revenu
    annuel de 20 000 € », 236,5 points en tranche 1 et 2,1 en tranche 2 ;
    « 80 000 € », les 557 points du plafond et 8,5. La caisse arrondit le total
    au dixième."""
    carriere = Carriere.depuis_releve(
        annee_naissance=1959, sexe="H",
        releve=[LigneRelevee(annee=2025, affiliation="profession_liberale",
                             revenu=float(revenu))],
        age_liquidation=67.0, macro=simulateur.macro,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    detail = {p.regime: p.detail for p in resultat.pensions_par_regime}["cnavpl"]
    assert float(detail.split(" points")[0].replace(",", "")) == pytest.approx(
        points, abs=0.05)


@pytest.mark.parametrize("annee", [2023, 2024, 2025, 2026])
def test_l_assiette_minimale_valide_trois_trimestres(simulateur, annee):
    """450 SMIC horaires font trois seuils de 150 : la virgule flottante en
    rendait deux en 2025."""
    macro = simulateur.macro
    assert macro.trimestres_valides(450 * macro.smic_horaire(annee), annee) == 3
