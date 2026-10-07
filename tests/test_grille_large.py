"""La grille élargie de la page Coût : ses parts viennent des sources, et sa mécanique ne triche pas.

`scripts/grille_large.py` dit ce que les treize cas types déplacent (action
136, étape 6). La mesure entière prend plusieurs minutes et ne se rejoue pas
ici ; ce qui se tient ici est ce qui la rend lisible : chaque déclinaison
reçoit la part que l'EIR ou l'INSEE lui donne, la grille du dépôt réécrite en
parts redonne la page, et l'ASPA que la page compte aux premières générations
ne touche que les années observées.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import memoire
from retraite_notionnelle.castypes import CAS_TYPES, poids_effectifs
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import grille_large as G  # noqa: E402


@pytest.fixture(scope="module")
def parametres():
    return Parametres()


@pytest.fixture(scope="module")
def simulateur(parametres):
    return Simulateur(parametres)


@pytest.fixture(scope="module")
def source(parametres):
    return G.eir(parametres.racine_donnees)


@pytest.fixture(scope="module")
def points(parametres):
    return G.multiplicateurs(G.centiles(parametres.racine_donnees)[1])


def _poids(variantes, effectifs, annee):
    cas_types, retraites, _ = G.pseudo(variantes)
    return poids_effectifs(G.EffectifsRepartis(effectifs, retraites), annee, cas_types)


def _par(variantes, poids, cle):
    sortie: dict = {}
    for v in variantes:
        sortie[cle(v)] = sortie.get(cle(v), 0.0) + poids[v.cas.code]
    return sortie


def test_la_grille_du_depot_en_parts_redonne_les_poids_de_la_page(simulateur):
    """Les pseudo-caisses ne changent rien aux poids : chaque cas type reçoit,
    année par année et des deux côtés du bilan, ce que ``poids_effectifs`` lui
    donne sur ses caisses réelles."""
    variantes = G.reference()
    cas_types, retraites, cotisants = G.pseudo(variantes)
    for effectifs, parts in ((simulateur.effectifs, retraites),
                             (simulateur.cotisants, cotisants)):
        reparti = G.EffectifsRepartis(effectifs, parts)
        for annee in (1980, 2004, 2020, 2024, 2050):
            attendu = poids_effectifs(effectifs, annee, CAS_TYPES)
            obtenu = poids_effectifs(reparti, annee, cas_types)
            for cas in CAS_TYPES:
                assert obtenu[cas.code] == pytest.approx(attendu[cas.code], abs=1e-12)


def test_chaque_groupe_recoit_sa_part_de_personnes(simulateur, source):
    """L'année de l'enquête, chaque groupe de régime principal pèse la part de
    retraités que l'EIR lui donne, et la Cnav ne compte plus les contractuels
    qu'elle comptait aussi. Les cotisants, eux, ne bougent pas."""
    variantes = G.grille("personnes", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    for groupe, part in G.parts_personnes(source).items():
        assert groupes[groupe] == pytest.approx(part, abs=1e-12), groupe
    moyen = next(v for v in variantes if v.cas.code == "salaire_moyen")
    assert moyen.retraites[0][0] == "cnav"
    assert ("ircantec", -moyen.retraites[0][1]) in moyen.retraites
    assert moyen.cotisants == next(v for v in G.reference()
                                   if v.cas.code == "salaire_moyen").cotisants


def test_les_polypensionnes_sont_dans_la_proportion_de_l_eir(simulateur, source):
    """Dans chaque groupe qui en a, la part des polypensionnés est celle de
    l'EIR, et leur carrière commence par dix années de salariat du privé. Le
    militaire et le régime général n'en ont pas : l'un parce que sa pension
    s'ouvre à une durée de services, l'autre parce que l'EIR ne dit pas son
    second régime."""
    variantes = G.grille("melees", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    polys = _par(variantes, poids, lambda v: (v.groupe, v.poly))
    for groupe, part in G.parts_poly(source).items():
        assert polys[(groupe, True)] / groupes[groupe] == pytest.approx(part, abs=1e-12)
    for groupe in set(G.GROUPES) - set(G.GROUPES_MELES):
        assert (groupe, True) not in polys, groupe
    for v in variantes:
        if v.poly:
            assert v.cas.avant == ((G.affiliation_privee(v.cas), G.ANNEES_PRIVE),)


def test_les_femmes_et_les_carrieres_courtes_suivent_l_eir(simulateur, source):
    """Chaque groupe a la part de femmes que l'EIR lui donne ; hors des
    régimes statutaires, chaque sexe a, tranche par tranche, la part de durées
    validées hors majorations que l'EIR publie ; les régimes statutaires
    gardent leurs carrières."""
    variantes = G.grille("interruptions", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    femmes = _par(variantes, poids, lambda v: (v.groupe, v.cas.sexe))
    for groupe, part in G.parts_femmes(source).items():
        assert femmes[(groupe, "F")] / groupes[groupe] == pytest.approx(part, abs=1e-12)
    tranche = {cible: nom for nom, cible in G.TRANCHES}
    for sexe in ("F", "H"):
        eligibles = [v for v in variantes
                     if v.groupe in G.GROUPES_INTERROMPUS and v.cas.sexe == sexe]
        masse = sum(poids[v.cas.code] for v in eligibles)
        for nom, part in G.parts_tranches(source, sexe).items():
            dedans = sum(poids[v.cas.code] for v in eligibles
                         if tranche.get(v.duree if v.duree in tranche else None) == nom)
            assert dedans / masse == pytest.approx(part, abs=1e-12), (sexe, nom)
    for v in variantes:
        if v.groupe not in G.GROUPES_INTERROMPUS:
            assert v.duree is None and v.assimilees == 0, v.cas.code


def test_une_carriere_courte_s_arrete_a_la_duree_de_sa_tranche(simulateur, source):
    """La carrière d'une tranche courte valide sa durée — travail et périodes
    assimilées — puis reste inactive jusqu'au départ, que le pilote date au
    taux plein."""
    variantes = G.grille("interruptions", simulateur.effectifs, source, ())
    courte = next(v for v in variantes if v.cas.code == "salaire_moyen~h~20_30")
    assert courte.duree == 25 and courte.assimilees == round(
        G.part_assimilee(source, "H") * 25)
    carriere = courte.cas.construire(simulateur, 1980)
    types = [ligne.type_periode for ligne in carriere.lignes]
    assert types.count("emploi") + types.count("chomage_indemnise") == 25
    assert types.count("chomage_indemnise") == courte.assimilees
    assert set(types[25:]) == {"inactivite"}


def test_les_salaires_gardent_la_moyenne_et_passent_la_grille_du_depot(source, simulateur,
                                                                      points):
    """Chaque cas type garde son salaire moyen, la dispersion seule s'ajoute ;
    et la grille élargie passe enfin les deux fois et demie du salaire moyen
    que la grille du dépôt ne dépassait pas (`docs/limites.md`, § 5)."""
    assert sum(part for _, part, _ in points) == pytest.approx(1.0)
    assert sum(part * facteur for _, part, facteur in points) == pytest.approx(1.0)
    variantes = G.grille("salaires", simulateur.effectifs, source, points)
    for cas in CAS_TYPES:
        siens = [v for v in variantes if v.cas.code.startswith(f"{cas.code}~")]
        assert len(siens) == len(G.CENTILES)
        poids = sum(v.retraites[0][1] for v in siens)
        moyenne = sum(v.retraites[0][1] * v.cas.niveau_salaire for v in siens) / poids
        assert moyenne == pytest.approx(cas.niveau_salaire)
    assert max(v.cas.niveau_salaire for v in variantes) > 2.5 * 3


def test_la_grille_du_depot_reecrite_redonne_la_page(parametres):
    """Les pseudo-caisses et la grille simulée à part donnent la page au
    millième : la mesure ne mesure rien d'autre que la grille."""
    page = G.indicateurs(memoire.cout(parametres))
    en_parts = G.indicateurs(G.calculer(parametres, G.reference()))
    assert G.ecart_maximal(en_parts, page) < 1e-6


def test_l_aspa_des_premieres_generations_ne_touche_que_le_passe(parametres):
    """La grille du dépôt déclenche l'ASPA aux non-salariés des premières
    générations — l'artisan né de 1885 à 1905, le libéral jusqu'en 1915,
    l'exploitant agricole jusqu'en 1920 —, que leurs régimes, nés après la
    guerre, servaient mal : la page la compte dans la masse du scénario 1,
    quand la dépense qu'elle multiplie l'exclut. Le retirer ne déplace que
    l'écart des années observées, et dans le sens d'une économie moindre ; la
    trajectoire, le solde et le coefficient ne bougent pas d'un millième,
    l'exploitant né en 1920 vivant encore, à peine, aux années où la page se
    cale."""
    page = G.indicateurs(memoire.cout(parametres))
    sans = G.indicateurs(G.calculer(G.parametres_de_la_grille(parametres), G.reference()))
    for scenario, _ in C.SCENARIOS:
        for cle in ("part_pib_horizon", "solde_moyen", "coefficient_horizon"):
            assert sans[scenario][cle] == pytest.approx(page[scenario][cle], abs=1e-3)
        assert sans[scenario]["ecart_passe"] >= page[scenario]["ecart_passe"] - 1e-9
    assert sans["notionnel_retroactif"]["ecart_passe"] > (
        page["notionnel_retroactif"]["ecart_passe"] + 0.1)


# -- la distribution de l'année de l'enquête (action 138, étape 14) -------------

def test_le_quantile_d_une_grille_est_l_un_de_ses_montants():
    """Une grille est faite d'atomes, une carrière et son montant : son quantile
    est le plus petit montant sous lequel tombe au moins le rang du poids."""
    lot = [(300.0, 2.0), (100.0, 1.0), (200.0, 1.0)]
    assert G.quantile_pondere(lot, 0.25) == 100.0
    assert G.quantile_pondere(lot, 0.5) == 200.0
    assert G.quantile_pondere(lot, 0.51) == 300.0
    assert G.part_sous(lot, 200.0) == pytest.approx(0.25)
    assert G.part_sous(lot, 250.0) == pytest.approx(0.5)


def test_la_distribution_compte_les_tetes_et_les_euros_de_la_page(parametres):
    """La distribution de l'année est la population de la page, en têtes : ses
    poids somment les têtes que ``cout._masses`` compte, et ses montants, la
    complétude des cohortes ôtée, la masse du scénario 1, des euros constants
    à ceux de l'année et au mois près."""
    from dataclasses import replace

    sans = G.parametres_de_la_grille(parametres)
    grille = G.en_tetes(sans, G.reference())
    annee = 2020
    lignes = grille.pensions(annee)
    entieres = [replace(p, completudes=()) for p in grille.pensionnes]
    masses, _, tetes = C._masses(entieres, grille.population, annee,
                                 grille.poids(annee), grille.revalorisation)
    vers = grille.macro.coefficient_prix(sans.annee_euros_constants, annee) / 12
    assert sum(p for _, p, _ in lignes) == pytest.approx(tetes[C.TETES_TOUTES], rel=1e-12)
    assert sum(m * p for m, p, _ in lignes) == pytest.approx(masses["actuel"] * vers,
                                                             rel=1e-12)
    assert {s for _, _, s in lignes} == {"F", "H"}


def test_la_mesure_appliquee_a_l_enquete_redonne_l_enquete(parametres):
    """L'enquête, mise en atomes au milieu de ses tranches de cent euros, se
    confronte à elle-même sans écart aux bornes des tranches, et ses quantiles
    redonnent ceux que la DREES publie à une tranche près — l'atome est au
    milieu de la sienne, et la soustraction des résidents à l'étranger
    (``DistributionPensions``) n'est exacte qu'à quelques dizaines d'euros :
    la mesure ne mesure que la grille."""
    from retraite_notionnelle.donnees.distribution import (DistributionPensions,
                                                           ResidenceRetraites)

    racine = parametres.racine_donnees
    residence = ResidenceRetraites(racine, 2020)
    distributions = {sexe: DistributionPensions(racine, sexe, 2020, "france")
                     for sexe in G.SEXES}
    lignes = []
    for sexe in ("F", "H"):
        effectif = residence.valeur("france", "effectifs", sexe)
        for tranche in distributions[sexe].tranches:
            milieu = (tranche.borne_inferieure + 50.0 if not tranche.ouverte
                      else tranche.borne_inferieure + 1000.0)
            lignes.append((milieu, tranche.part * effectif, sexe))
    mesure = G.confronter(lignes, residence, distributions)
    for sexe in ("F", "H"):
        lue = mesure[sexe]
        assert abs(lue["kolmogorov"]) < 1e-9, sexe
        # Les effectifs publiés sont arrondis au millier : 15 647 milliers de
        # résidents, quand les deux sexes en font 15 648.
        assert lue["part"] == pytest.approx(lue["part_eir"], rel=1e-4)
        for code, publie in lue["quantiles_eir"].items():
            assert abs(lue["quantiles"][code] - publie) < 100.0, (sexe, code)
    # L'ensemble n'est pas le mélange des deux sexes au poids des effectifs à
    # mieux que quelques dixièmes de point : les parts publiées sont arrondies.
    assert abs(mesure["ensemble"]["kolmogorov"]) < 5e-3
