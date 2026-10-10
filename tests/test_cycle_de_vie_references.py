"""Les indicateurs de cycle de vie confrontés au COR, à TRAJECTOiRE et à l'OCDE.

Le dépôt calcule depuis l'action 138 (étape 9) la durée de retraite, le taux de
récupération, le rendement interne et le patrimoine retraite de ses carrières
(``retraite_notionnelle.cycle_de_vie`` ; définitions dans
``tests/test_cycle_de_vie.py``). Trois références en publient, chacune sous ses
conventions, et ce module les refait sous les mêmes :

* LE COR, rapport annuel de juin 2026 (``tests/temoins/cor_cycle_de_vie.json``,
  ``scripts/fetch/cor_cycle_de_vie.py``) : l'espérance de vie à 60 ans de chaque
  génération, celle des projections de l'INSEE, et le rendement interne net du
  cas type n° 2, sur les carrières que TRAJECTOiRE a bâties pour lui ;
* TRAJECTOiRE, exécuté à part (``tests/temoins/trajectoire.json``) : sa durée de
  retraite rapportée à la carrière, son taux d'annuité, son taux de
  cotisation, sur les mêmes carrières ;
* L'OCDE, *Pensions at a Glance 2025* (``tests/temoins/ocde_pensions.json``,
  ``scripts/fetch/ocde_pensions.py``) : le taux de remplacement et le patrimoine
  retraite d'un salarié entré à 22 ans en 2024, sous ses hypothèses
  macroéconomiques (jeu ``ocde_2025``).

Chaque grandeur concorde à sa tolérance, ou son écart est DÉCLARÉ avec sa cause
et sa borne ; un écart déclaré qui rentrerait dans la tolérance fait échouer le
test, comme dans ``tests/test_trajectoire.py``.

Ce que la première confrontation a montré, le 7 octobre 2026 :

* **Concordent** — l'espérance de vie à 60 ans des générations 1960 à 2000,
  à 0,02 an près par sexe depuis l'étape 7, publiée le même soir : les tables
  du dépôt sont celles de l'INSEE ; la
  durée de retraite rapportée à la carrière de TRAJECTOiRE, exactement, sur
  ses cas types du COR, avec un âge de décès par génération ; le rendement
  interne net du cas type n° 2, à 0,3 point près, et son profil décroissant ;
  l'écart de rendement du cadre au non-cadre de la génération 2000 ; le
  coefficient de rente de l'OCDE des hommes.
* **Contre le dépôt** — la génération 1941, dont les quotients observés sont
  de 5 à 10 % sous ceux de ses voisines à chaque âge de 60 à 83 ans : son
  espérance de vie à 60 ans dépasse celle de l'INSEE de 0,3 an pour les
  hommes et de 0,2 pour les femmes, et son diviseur en hérite. À reprendre
  avec les données.
* **Des conventions** — le dépôt ne porte pas les contributions d'équilibre
  de l'Agirc-Arrco (AGFF, CEG, CET), que TRAJECTOiRE compte, et cotise à
  l'Arrco au taux minimal, TRAJECTOiRE au taux moyen des entreprises : son
  taux de cotisation du privé est inférieur de 10 à 12 %. Pour l'État, le dépôt
  compte la part de la contribution que la Cour des comptes rattache à la
  retraite de l'agent, TRAJECTOiRE et le COR la seule retenue. L'Agirc-Arrco
  que l'OCDE projette sert un quart de plus que celui du dépôt, sous la
  convention du COR. La mortalité de l'ONU fait vivre les femmes plus
  longtemps que celle de l'INSEE.

Ce que le 9 octobre 2026 a changé : le dépôt compte les contributions
d'équilibre (``contributions_equilibre.py``). Son taux de cotisation du privé
est celui de TRAJECTOiRE à 0,4 % près, aux taux moyens de l'Arrco ; le COR les
compte aussi, ce que montre le rendement de chaque régime de la génération
2000. Le rendement du cas type n° 2 en perd 0,22 à 0,25 point, et l'écart au
COR des générations 1963 à 1970, que l'oubli compensait, apparaît : commun au
régime général et à l'Agirc-Arrco, sa cause reste à trouver.

Ce que le 10 octobre 2026 a trouvé : la cause est au COR. Le rendement brut du
dépôt retrouve, pente comprise, la série brute que le COR publiait en juin
2025 ; sa série nette de 2026 n'en est pas la version nette, il l'a révisée
d'autre chose, qu'il ne dit pas, négative ou nulle pour les générations 1955
et 1960, croissante ensuite. Ni ses projections, ni les carrières, ni les
cotisations ne referment l'écart.

Le même jour, aux données : la marche de la génération 1941 n'était pas dans
sa mortalité, mais dans la table d'Eurostat, qui suppose que chaque
génération passe une demi-année dans chaque carré de Lexis : la génération
1940, née plutôt en début d'année, et celle de 1941, plutôt en fin, le
démentent. Les quotients observés se calculent désormais génération par
génération, comme l'INSEE (``scripts/fetch/eurostat_mortalite.py``) : son
espérance de vie à 60 ans rejoint celle de l'INSEE à 0,06 an près, et celle
des générations 1940 à 1959 à moins de 0,08 an.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.castypes import CAS_TYPES, CasType
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.cout import coefficient_actuel
from retraite_notionnelle.donnees.prelevements_historiques import (
    charger_prelevements_historiques,
)
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
TEMOINS = RACINE / "tests" / "temoins"


def _temoin(nom: str) -> dict:
    return json.loads((TEMOINS / nom).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cor() -> dict:
    return _temoin("cor_cycle_de_vie.json")


@pytest.fixture(scope="module")
def trajectoire() -> dict:
    return _temoin("trajectoire.json")


@pytest.fixture(scope="module")
def ocde() -> dict:
    return _temoin("ocde_pensions.json")


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


@pytest.fixture(scope="module")
def simulateur(contexte) -> Simulateur:
    return contexte.simulateur()


# ---------------------------------------------------------------------------
# Le COR : l'espérance de vie à 60 ans, le rendement interne
# ---------------------------------------------------------------------------

#: Les générations dont l'espérance de vie à 60 ans s'écarte de celle de
#: l'INSEE, la cause, et la borne de l'écart (en années, par sexe). Aucune
#: depuis le 10 octobre 2026 : la génération 1941, qui la dépassait de 0,32 an
#: pour les hommes et de 0,22 pour les femmes, devait sa marche à la table
#: d'Eurostat, non à sa mortalité (``test_donnees.py``).
ECARTS_ESPERANCE: dict[int, tuple[str, float, float]] = {}


def test_l_esperance_de_vie_a_60_ans_des_generations_est_celle_de_l_insee(cor, simulateur):
    """Le COR publie, avec sa durée de retraite, l'espérance de vie à 60 ans de
    chaque génération de 1940 à 2000, par sexe, du scénario central des
    projections de l'INSEE (figure 3.6, données complémentaires). Le dépôt la
    retrouve sur ses tables de génération : à 0,05 an près dès la génération
    1960, dont il lit les quotients projetés de l'INSEE depuis l'étape 7 ; à
    0,1 an près avant, où ses quotients observés, calculés comme ceux de
    l'INSEE sur les décès et les populations d'Eurostat depuis le 10 octobre
    2026, ne sont pas exactement ceux que l'INSEE retient."""
    mortalite = simulateur.mortalite
    esperances = cor["duree_retraite"]["esperance_60"]
    for generation in range(1940, 2001):
        for sexe, qui in (("H", "hommes"), ("F", "femmes")):
            ecart = (mortalite.esperance_residuelle(60.0, generation + 60.0, sexe)
                     - esperances[qui][str(generation)])
            if generation in ECARTS_ESPERANCE:
                _, bas, haut = ECARTS_ESPERANCE[generation]
                assert bas <= ecart <= haut, (generation, sexe, ecart)
            else:
                tolerance = 0.05 if generation >= 1960 else 0.10
                assert abs(ecart) <= tolerance, (generation, sexe, ecart)


#: Les cas types n° 2 du COR que TRAJECTOiRE a bâtis pour le témoin.
GENERATIONS_CAS_TYPE_2 = (1955, 1960, 1963, 1964, 1970)


@pytest.fixture(scope="module")
def cas_type_2(trajectoire, contexte, simulateur) -> dict[int, object]:
    return {generation: contexte.simuler(Saisie.depuis_requete(
                dict(trajectoire["cas"][f"cor_2_{generation}"]["requete"])))
            for generation in GENERATIONS_CAS_TYPE_2}


#: Les générations dont le rendement du cas type n° 2 s'écarte de celui du COR
#: de juin 2026 au-delà de la tolérance, et les bornes de l'écart, dépôt moins
#: COR. La cause est la même pour toutes : la série de 2026 n'est pas celle de
#: 2025, que le dépôt retrouve, rendue nette ; le COR l'a révisée d'autre chose
#: (:data:`REVISION_DE_2026`), que ni son rapport ni son annexe ne disent.
ECARTS_RENDEMENT = {1963: (-0.0040, -0.0020), 1964: (-0.0045, -0.0025),
                    1970: (-0.0060, -0.0040)}

#: Ce que le COR a changé au rendement du cas type n° 2 entre juin 2025 et juin
#: 2026, au-delà du passage au net : sa série de 2026 moins celle de 2025, moins
#: ce que les prélèvements retirent au rendement du dépôt (0,30 point pour
#: chacune). Bornes, en points de rendement, par génération : −0,14 pour 1955,
#: rien pour 1960, puis croissante — +0,17 pour 1963, +0,31 pour 1964, +0,44
#: pour 1970 (mesures du 10 octobre 2026).
REVISION_DE_2026 = {1955: (-0.0020, 0.0000), 1960: (-0.0010, 0.0010),
                    1963: (0.0010, 0.0025), 1964: (0.0025, 0.0040),
                    1970: (0.0035, 0.0050)}


def test_le_rendement_interne_du_cas_type_2_est_celui_du_cor(cor, cas_type_2, simulateur):
    """Le COR publie le rendement interne net de son cas type n° 2, flux
    actualisés selon le salaire moyen (figure 3.7). Sous ses conventions —
    les deux sexes réunis, le décès à 60 ans plus l'espérance de vie à 60 ans
    de la génération, la pension nette au taux plein, les cotisations seules,
    contributions d'équilibre de l'Agirc-Arrco comprises, comme lui (test du
    rendement par régime) — et sur les carrières que TRAJECTOiRE a bâties
    pour lui, le dépôt le retrouve à 0,2 point près pour les générations 1955
    et 1960, et décroissant comme lui de 1955 à 1970.

    Mais il décroît plus vite : de 0,9 point de 1955 à 1970, le COR de 0,4.
    La cause est au COR (test suivant) : le rendement brut du dépôt retrouve,
    pente comprise, la série brute que le COR publiait en juin 2025, et sa
    série nette de 2026 n'en est pas la version nette ; il l'a révisée d'autre
    chose, qui croît avec la génération (:data:`REVISION_DE_2026`). Ni sa
    trajectoire du salaire moyen (+0,02 à +0,03 point), ni ses conventions de
    l'Agirc-Arrco, taux moyen et valeur de service (−0,02 à −0,05), ni les
    carrières refaites sur le profil qu'il décrit (−0,03 à +0,04) ne
    referment l'écart ; il compte les cotisations comme le dépôt (figure 3.1 :
    27,9 % en 2025), et, selon son annexe, sans les allègements (note du 10
    octobre 2026)."""
    publie = cor["rendement_cas_type_2"]
    calcules = {}
    for generation, comparaison in cas_type_2.items():
        flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
        calcules[generation] = cycle_de_vie.indicateurs(
            flux, simulateur, cycle_de_vie.convention_cor(simulateur, comparaison)
        ).rendement_smpt
        ecart = calcules[generation] - publie[str(generation)]
        if generation in ECARTS_RENDEMENT:
            bas, haut = ECARTS_RENDEMENT[generation]
            assert bas <= ecart <= haut and abs(ecart) > 0.002, (generation, ecart)
        else:
            assert abs(ecart) <= 0.002, (generation, calcules[generation],
                                         publie[str(generation)])
    rangs = list(GENERATIONS_CAS_TYPE_2)
    assert all(calcules[a] > calcules[b] for a, b in zip(rangs, rangs[1:]))
    assert all(publie[str(a)] > publie[str(b)] for a, b in zip(rangs, rangs[1:]))
    assert ((calcules[1955] - calcules[1970])
            > 2.0 * (publie["1955"] - publie["1970"]))


def test_le_rendement_brut_du_cas_type_2_est_celui_du_cor_de_2025(cor, cas_type_2, simulateur):
    """Jusqu'en juin 2025, le COR publiait le rendement interne BRUT de son
    cas type n° 2 : il « était évalué à partir des rémunérations brutes »
    (rapport de juin 2026, note 140). Sous les mêmes conventions, pension
    brute, le dépôt le retrouve à 0,2 point près pour les cinq générations, et
    sa pente avec lui : de 1955 à 1970, 0,90 point de baisse au dépôt, 0,94
    au COR. Ce qui reste, 0,17 point au plus, tient au salaire moyen : le COR
    actualise selon sa rémunération moyenne par tête — revenu mixte et
    salaires sur l'emploi total —, qui a crû de 0,26 point par an de moins que
    le salaire moyen des salariés, celui du dépôt, de 2004 à 2024 ; déflaté par
    elle, le dépôt le retrouve à 0,07 point près.

    Le passage au net retire 0,30 point au rendement du dépôt, à chaque
    génération. La série de 2026 n'est pas celle de 2025 moins autant : le
    COR l'a révisée d'autre chose (:data:`REVISION_DE_2026`) : −0,14 point
    pour 1955, rien pour 1960, de +0,17 à +0,44 de 1963 à 1970, +0,6 pour la
    génération 2000 — l'écart déclaré du test précédent, à ce reste près. Ni
    la mortalité (l'Insee de 2026 retire 0,7 an à l'espérance de vie à 60 ans
    de la génération 2000), ni la productivité (0,7 % les deux années), ni les
    taux de cotisation ne l'expliquent ; les allègements généraux, que le
    rapport de 2026 fait jouer pour le SMIC et les cas types genrés, quand son
    annexe dit les cotisations « sans les allègements », en sont le seul
    candidat trouvé, et pour une part seulement (note du 10 octobre 2026)."""
    brut_2025 = cor["rendement_cas_type_2_brut_2025"]
    net_2026 = cor["rendement_cas_type_2"]
    bruts = {}
    for generation, comparaison in cas_type_2.items():
        flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
        convention = cycle_de_vie.convention_cor(simulateur, comparaison)
        net = cycle_de_vie.indicateurs(flux, simulateur, convention).rendement_smpt
        bruts[generation] = cycle_de_vie.indicateurs(
            flux, simulateur, replace(convention, prelevement=0.0, prelevements=None)
        ).rendement_smpt
        cle = str(generation)
        assert abs(bruts[generation] - brut_2025[cle]) <= 0.002, (generation, bruts[generation])
        assert -0.0035 <= net - bruts[generation] <= -0.0025, (generation, net - bruts[generation])
        revision = (net_2026[cle] - brut_2025[cle]) - (net - bruts[generation])
        bas, haut = REVISION_DE_2026[generation]
        assert bas <= revision <= haut, (generation, revision)
    assert abs((bruts[1955] - bruts[1970])
               - (brut_2025["1955"] - brut_2025["1970"])) <= 0.001


#: Les régimes que le COR range sous l'Agirc-Arrco.
REGIMES_AGIRC_ARRCO = {"arrco", "arrco_tranche_2", "agirc", "agirc_arrco"}


def _rendements_par_regime(simulateur, comparaison) -> dict[str, float]:
    """Le rendement interne net de la Cnav et celui de l'Agirc-Arrco, avec et
    sans les contributions d'équilibre, sous les conventions du COR : chacun
    sur ses cotisations et sa pension. La carrière part après l'année
    courante : la pension de la Cnav suit les prix, celle de l'Agirc-Arrco la
    règle de :func:`cycle_de_vie.niveaux_actuels`, les prix aussi sous le
    simulateur individuel, qui n'a pas la valeur de service que le COR
    projette (``Parametres.conventions_cor``)."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
    carriere = comparaison.carriere
    liquidation = carriere.annee_liquidation
    assert liquidation > simulateur.parametres.annee_courante
    compte = simulateur.constructeur_employeur.construire(
        carriere, annee_liquidation=liquidation, annee_debut=carriere.premiere_annee)
    cotisations: dict[str, dict[int, float]] = {"cnav": {}, "agirc_arrco": {}}
    for ligne in compte.cotisations:
        for regime, montant in ligne.par_regime:
            famille = cotisations["agirc_arrco" if regime in REGIMES_AGIRC_ARRCO else "cnav"]
            famille[ligne.annee] = famille.get(ligne.annee, 0.0) + montant
    avec = dict(cotisations["agirc_arrco"])
    for annee, montant in cycle_de_vie.contributions_d_une_carriere(simulateur, carriere).items():
        avec[annee] = avec.get(annee, 0.0) + montant
    pensions = {"cnav": 0.0, "agirc_arrco": 0.0}
    for pension in comparaison.actuel.pensions_par_regime:
        pensions["agirc_arrco" if pension.regime in REGIMES_AGIRC_ARRCO else "cnav"] += (
            pension.montant)
    revalorisation = cycle_de_vie._revalorisation(simulateur, max(flux.niveaux))
    prix = {annee: simulateur.macro.coefficient_prix(liquidation, annee) for annee in flux.niveaux}
    points = {annee: coefficient_actuel({"agirc_arrco": 1.0}, revalorisation, liquidation, annee)
              for annee in flux.niveaux}
    convention = cycle_de_vie.convention_cor(simulateur, comparaison)

    def rendement(versees: dict[int, float], niveaux: dict[int, float]) -> float:
        return cycle_de_vie.indicateurs(replace(flux, cotisations=versees, niveaux=niveaux),
                                        simulateur, convention).rendement_smpt

    return {
        "cnav": rendement(cotisations["cnav"],
                          {a: pensions["cnav"] * prix[a] for a in flux.niveaux}),
        **{cle: rendement(versees, {a: pensions["agirc_arrco"] * prix[a] * points[a]
                                    for a in flux.niveaux})
           for cle, versees in (("agirc_arrco", avec),
                                ("agirc_arrco_sans_contributions", cotisations["agirc_arrco"]))},
    }


def test_le_cor_compte_les_contributions_d_equilibre_comme_des_cotisations(cor, simulateur):
    """Le COR ne compte que « les cotisations » ; les contributions
    d'équilibre de l'Agirc-Arrco en sont-elles ? Il publie, pour la
    génération 2000, le rendement de chaque régime (figure 3.A). Le dépôt est
    sous lui au régime général seul, de 0,43 point pour le salarié au salaire
    moyen et de 0,65 pour le cadre — ce qui ne doit rien à la complémentaire.
    À l'Agirc-Arrco, avec les contributions d'équilibre, il est sous lui
    d'autant, à 0,3 point près (0,08 et 0,24) ; sans elles, il serait
    au-dessus de lui, à 0,8 point de l'écart du régime général. Le COR les
    compte donc, comme
    TRAJECTOiRE, dont il tient ses cas types, et le dépôt les compte depuis le
    9 octobre 2026 (``contributions_equilibre.py``)."""
    publie = cor["rendement_generation_2000"]
    for code, profil in (("salaire_moyen", "non_cadre"), ("cadre", "cadre")):
        cas = next(c for c in CAS_TYPES if c.code == code)
        rendements = _rendements_par_regime(
            simulateur, simulateur.simuler(cas.construire(simulateur, 2000)))
        cnav = rendements["cnav"] - publie[profil]["cnav"]
        avec = rendements["agirc_arrco"] - publie[profil]["agirc_arrco"]
        sans = rendements["agirc_arrco_sans_contributions"] - publie[profil]["agirc_arrco"]
        assert cnav < -0.003, (profil, cnav)
        assert abs(avec - cnav) <= 0.003, (profil, cnav, avec)
        assert sans - cnav >= 0.007, (profil, cnav, sans)


def test_le_rendement_du_cadre_est_sous_celui_du_non_cadre_comme_au_cor(cor, simulateur):
    """Génération 2000 (figure 3.A) : le cadre rend 0,04 %, le non-cadre
    0,83 %, parce qu'une part de la rémunération du cadre cotise au-dessus du
    plafond sans ouvrir de droit au régime général. Sous les mêmes
    conventions, le cadre et le salarié au salaire moyen de la grille
    s'écartent d'autant, à 0,25 point près : de 0,97 point, contre 0,78. Ils
    s'écartaient de 0,86 point avant que le dépôt compte les contributions
    d'équilibre, que le cadre verse au taux de la tranche 2 sur une plus
    grande part de sa rémunération ; les cas types de la grille ne sont pas
    ceux du COR."""
    publie = cor["rendement_generation_2000"]
    ecart_publie = publie["cadre"]["total"] - publie["non_cadre"]["total"]
    rendements = {}
    for code in ("cadre", "salaire_moyen"):
        cas = next(c for c in CAS_TYPES if c.code == code)
        comparaison = simulateur.simuler(cas.construire(simulateur, 2000))
        flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
        rendements[code] = cycle_de_vie.indicateurs(
            flux, simulateur, cycle_de_vie.convention_cor(simulateur, comparaison)
        ).rendement_smpt
    ecart = rendements["cadre"] - rendements["salaire_moyen"]
    assert ecart < 0.0 and ecart_publie < 0.0
    assert abs(ecart - ecart_publie) <= 0.0025, (ecart, ecart_publie)


# ---------------------------------------------------------------------------
# TRAJECTOiRE : la durée, le flux des pensions, la cotisation
# ---------------------------------------------------------------------------

#: L'âge de décès des cas types du COR dans TRAJECTOiRE, par génération :
#: ``round(60 + e60)`` de la table du COR (``casTypesCOR.R``, l. 94), plus les
#: six mois que son calcul ajoute (``fonctionsCalculsPensions.R``, l. 4692).
AGES_DE_DECES_TRAJECTOIRE = {1955: 86.5, 1960: 87.5, 1963: 87.5, 1964: 87.5, 1970: 88.5}

#: Les cas dont TRAJECTOiRE compte d'autres années de carrière que le dépôt,
#: et la cause ; l'âge de décès qu'on en déduirait s'écarte alors du sien.
CARRIERES_COMPTEES_AUTREMENT = {
    "cor_3_1955": "une année de chômage, que TRAJECTOiRE compte comme une année "
                  "de carrière quand son script lui donne un revenu",
    "cor_4_1955": "des années d'AVPF, dont TRAJECTOiRE multiplie l'assiette par "
                  "douze et qu'il compte comme des années de carrière",
    "cor_4_1963": "des années d'AVPF, comptées par TRAJECTOiRE",
    "cor_4_1964": "des années d'AVPF, comptées par TRAJECTOiRE",
}


def _cas_du_cor(trajectoire: dict) -> list[tuple[str, int, dict]]:
    cas = []
    for cle, contenu in sorted(trajectoire["cas"].items()):
        if contenu.get("jeu") == "cas_types_cor" and contenu["trajectoire"].get("indicateurs"):
            cas.append((cle, int(contenu["generation"]), contenu))
    return cas


@pytest.fixture(scope="module")
def flux_trajectoire(trajectoire, contexte, simulateur) -> dict[str, tuple]:
    """Chaque carrière du témoin rejouée, et le flux du scénario 1."""
    rejoues = {}
    for cle, contenu in sorted(trajectoire["cas"].items()):
        if "requete" not in contenu or not contenu["trajectoire"].get("indicateurs"):
            continue
        comparaison = contexte.simuler(Saisie.depuis_requete(dict(contenu["requete"])))
        rejoues[cle] = (comparaison,
                        cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"])
    return rejoues


def test_la_duree_de_retraite_rapportee_a_la_carriere_est_celle_de_trajectoire(
        trajectoire, flux_trajectoire):
    """TRAJECTOiRE rapporte la durée de retraite au nombre d'années de
    carrière (``dureeRetraiteRelativeDureeCotisation``). Le dépôt compte les
    mêmes années et liquide à la même date : sur chaque cas type du COR,
    l'âge de décès que son rapport implique est celui de la génération, au
    mois près, sauf où l'un compte des années que l'autre ne compte pas."""
    for cle, generation, contenu in _cas_du_cor(trajectoire):
        _, flux = flux_trajectoire[cle]
        rapport = contenu["trajectoire"]["indicateurs"]["dureeRetraiteRelativeDureeCotisation"]
        implicite = flux.age + rapport * flux.duree_carriere
        attendu = AGES_DE_DECES_TRAJECTOIRE[generation]
        if cle in CARRIERES_COMPTEES_AUTREMENT:
            assert abs(implicite - attendu) > 1.0 / 12.0, cle
        else:
            assert implicite == pytest.approx(attendu, abs=1.0 / 24.0), cle


#: Les carrières d'un seul statut à la fois : TRAJECTOiRE compte jusqu'à seize
#: fois le revenu d'une année partagée entre deux états (``test_trajectoire``),
#: ce qui fausse son taux d'annuité ailleurs ; ses âges et durées des emplois
#: actifs et super-actifs sont les siens.
UN_SEUL_STATUT = ("cor_2_", "cor_2bis_", "cor_5_", "cor_6_", "cor_7_", "cor_10_",
                  "cor_11_", "rg_", "fp_", "loi_2023_")


def _pension_de_trajectoire(contenu: dict) -> float:
    """La pension annuelle au départ, hors RAFP, que le dépôt sert à part."""
    return 12.0 * sum(caisse["pension_mensuelle"]
                      for nom, caisse in contenu["trajectoire"]["caisses"].items()
                      if nom != "Rafp")


def _convention_trajectoire(contenu: dict, flux) -> cycle_de_vie.Convention:
    """Le décès que le rapport de TRAJECTOiRE implique, les deux sexes réunis."""
    rapport = contenu["trajectoire"]["indicateurs"]["dureeRetraiteRelativeDureeCotisation"]
    return cycle_de_vie.Convention(age_deces=flux.age + rapport * flux.duree_carriere,
                                   unisexe=True)


def test_le_flux_des_pensions_a_l_allure_de_celui_de_trajectoire(trajectoire, flux_trajectoire,
                                                                  simulateur):
    """Le taux d'annuité de TRAJECTOiRE (``txAnnuite``) rapporte la somme des
    pensions de la retraite à celle des revenus de la carrière, en salaire
    moyen. La pension de départ des deux modèles est confrontée ailleurs
    (``test_trajectoire``) ; recalée sur celle de TRAJECTOiRE, celle du dépôt
    en garde l'allure : 0,88 à 1,05 fois son taux d'annuité.

    Ce qui reste : TRAJECTOiRE projette le salaire moyen à 1 % de croissance
    réelle, le dépôt à 0,7 % ; il projette ses paramètres depuis 2024, et
    revalorise la pension au mois, le dépôt à l'année, au niveau du 31
    décembre ; il sert la RAFP, que le dépôt sert à part."""
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(UN_SEUL_STATUT):
            continue
        contenu = trajectoire["cas"][cle]
        rapport = _pension_de_trajectoire(contenu) / flux.niveaux[flux.annee_liquidation]
        recale = replace(flux, niveaux={annee: niveau * rapport
                                        for annee, niveau in flux.niveaux.items()})
        annuite = cycle_de_vie.indicateurs(
            recale, simulateur, _convention_trajectoire(contenu, flux)).taux_annuite
        ratio = annuite / contenu["trajectoire"]["indicateurs"]["txAnnuite"]
        assert 0.88 <= ratio <= 1.05, (cle, ratio)


#: Les carrières du privé, non cadres, d'un seul statut.
PRIVE_NON_CADRE = ("cor_2_", "cor_2bis_", "rg_salaire_moyen", "rg_bas_salaire",
                   "rg_pere_trois_enfants", "rg_ne_en_octobre", "loi_2023_salaire_moyen")


def _taux_de_cotisation(indicateurs) -> float:
    """Cotisations sur revenus, en salaire moyen : le taux d'annuité divisé
    par le taux de récupération."""
    return indicateurs.taux_annuite / indicateurs.taux_recuperation


def _taux_moyens_arrco(trajectoire: dict) -> dict[int, float]:
    """Le rapport du taux contractuel moyen de l'Arrco au taux minimal, par
    année, sous le plafond : les paramètres que le témoin garde."""
    rapports = {}
    for ligne in trajectoire["parametres_trajectoire"]["annuels"]:
        valeurs = dict(re.findall(r"(\w+)=([\d.]+)", ligne))
        if "txCotMIN_ARRCOsalempl_t1" in valeurs:
            rapports[int(ligne.split()[0])] = (float(valeurs["txCotARRCOsalempl_t1"])
                                               / float(valeurs["txCotMIN_ARRCOsalempl_t1"]))
    return rapports


def test_le_taux_de_cotisation_du_prive_est_celui_de_trajectoire_aux_conventions_pres(
        trajectoire, flux_trajectoire, simulateur):
    """TRAJECTOiRE compte, comme le dépôt depuis le 9 octobre 2026, les
    contributions d'équilibre de l'Agirc-Arrco — l'ASF de 1984 au 31 mars
    2001, l'AGFF jusqu'en 2018, la CEG depuis 2019 —, que le compte
    notionnel ne porte pas, par un choix que les limites déclarent, mais que
    la paie supporte. Il ne cotise plus davantage que pour une raison : il
    prend à l'Arrco le taux contractuel moyen des entreprises — 5,42 % de
    1960 à 1998, contre 4 % au minimum. Le taux de cotisation du dépôt est de
    3 à 5 % sous le sien ; aux taux moyens de TRAJECTOiRE, il est le sien à
    0,4 % près. Le 7 octobre, sans les contributions d'équilibre, il était de
    10 à 12 % sous le sien, et de 7 à 8 % aux taux moyens."""
    moyens = _taux_moyens_arrco(trajectoire)
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(PRIVE_NON_CADRE):
            continue
        contenu = trajectoire["cas"][cle]
        convention = _convention_trajectoire(contenu, flux)
        publie = (contenu["trajectoire"]["indicateurs"]["txAnnuite"]
                  / contenu["trajectoire"]["indicateurs"]["txRecuperation"])
        rapport = _taux_de_cotisation(cycle_de_vie.indicateurs(flux, simulateur, convention)) / publie
        assert 0.94 <= rapport <= 0.98, (cle, rapport)
        carriere = comparaison.carriere
        compte = simulateur.constructeur_employeur.construire(
            carriere, annee_liquidation=carriere.annee_liquidation,
            annee_debut=carriere.premiere_annee)
        aux_taux_moyens: dict[int, float] = {}
        for ligne in compte.cotisations:
            for regime, montant in ligne.par_regime:
                if regime in ("arrco", "agirc_arrco"):
                    montant *= moyens.get(ligne.annee, 1.0)
                aux_taux_moyens[ligne.annee] = aux_taux_moyens.get(ligne.annee, 0.0) + montant
        for annee, montant in cycle_de_vie.contributions_d_une_carriere(simulateur, carriere).items():
            aux_taux_moyens[annee] = aux_taux_moyens.get(annee, 0.0) + montant
        refait = _taux_de_cotisation(cycle_de_vie.indicateurs(
            replace(flux, cotisations=aux_taux_moyens), simulateur, convention)) / publie
        assert refait - rapport >= 0.02, (cle, rapport, refait)
        assert 0.99 <= refait <= 1.005, (cle, refait)


#: Les fonctionnaires de l'État des cas types du COR et du témoin de Destinie.
ETAT = ("cor_5_", "cor_6_", "cor_7_", "fp_", "loi_2023_fp_etat")
REGIMES_ETAT = {"fonction_publique_etat", "fonction_publique_etat_civile",
                "fonction_publique_etat_militaire"}


def test_pour_l_etat_trajectoire_ne_compte_que_la_retenue_de_l_agent(
        trajectoire, flux_trajectoire, simulateur):
    """TRAJECTOiRE ne compte, pour l'État, aucune contribution d'employeur
    (``fonctionsCalculsDivers.R``, l. 403-407), comme le COR, pour qui elle
    « ne reflète que le montant de la contribution qui permet de garantir en
    dernier ressort l'équilibre du régime ». Le dépôt en compte la part que
    la Cour des comptes rattache à la retraite de l'agent : son taux de
    cotisation est trois à six fois celui de TRAJECTOiRE. Réduit à la seule
    retenue les années à l'État, il est le sien à la RAFP près, que
    TRAJECTOiRE compte et que le dépôt sert à part."""
    salariale = simulateur.constructeur_de(simulateur.calculs["notionnel_retroactif"])
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(ETAT):
            continue
        contenu = trajectoire["cas"][cle]
        convention = _convention_trajectoire(contenu, flux)
        publie = (contenu["trajectoire"]["indicateurs"]["txAnnuite"]
                  / contenu["trajectoire"]["indicateurs"]["txRecuperation"])
        rapport = _taux_de_cotisation(cycle_de_vie.indicateurs(flux, simulateur, convention)) / publie
        assert 3.0 <= rapport <= 6.0, (cle, rapport)
        carriere = comparaison.carriere
        bornes = dict(annee_liquidation=carriere.annee_liquidation,
                      annee_debut=carriere.premiere_annee)
        retenues = salariale.construire(carriere, **bornes).cotisations
        entieres = simulateur.constructeur_employeur.construire(carriere, **bornes).cotisations
        refaites: dict[int, float] = {}
        for retenue, entiere in zip(retenues, entieres):
            assert retenue.annee == entiere.annee
            etat = any(regime in REGIMES_ETAT for regime in entiere.regimes)
            refaites[entiere.annee] = (refaites.get(entiere.annee, 0.0)
                                       + (retenue.cotisation if etat else entiere.cotisation))
        refait = _taux_de_cotisation(cycle_de_vie.indicateurs(
            replace(flux, cotisations=refaites), simulateur, convention)) / publie
        assert 0.74 <= refait <= 0.97, (cle, refait)


# ---------------------------------------------------------------------------
# TRAJECTOiRE : le taux de remplacement net
# ---------------------------------------------------------------------------

#: La catégorie de CSG que TRAJECTOiRE donne à la pension de chaque cas, et le
#: taux de l'histoire des prélèvements qui lui répond.
CATEGORIES_CSG = {"Normal": "plein", "mediane": "median", "reduit": "reduit"}

#: Les caisses dont TRAJECTOiRE retient la cotisation maladie de la pension,
#: quelle que soit la catégorie de CSG (``calculePensionNette``).
CAISSES_MALADIE = ("Agirc-Arrco", "Arrco", "Agirc")

#: L'écart admis au taux de remplacement net en euros constants, et en salaire
#: moyen, que les séries de salaire moyen des deux modèles écartent encore.
TOLERANCE_REMPLACEMENT_NET = 0.015
TOLERANCE_REMPLACEMENT_NET_SMPT = 0.02

#: Les écarts déclarés au taux de remplacement net de TRAJECTOiRE, par cas
#: type, leur cause, et les bornes du rapport, dépôt sur TRAJECTOiRE.
ECARTS_REMPLACEMENT_NET = {
    "cor_8_": (
        "TRAJECTOiRE ne prélève au policier ni la retenue supplémentaire de 1 % de la "
        "bonification du cinquième (loi n° 57-444, article 3) ni la majoration de 1,2 "
        "point de l'indemnité de sujétions spéciales (article 6 bis), que le dépôt "
        "prélève depuis le 10 octobre 2026 (fiche indemnite_sujetions_speciales_police) : "
        "il multiplie son taux txISS par les autres primes et par la retenue ordinaire, "
        "« (remuneration + txISS*primes) * txCotFP_sal » ; son net est plus haut de "
        "2,2 % du traitement et de l'indemnité", 1.01, 1.03),
    "cor_9_": (
        "TRAJECTOiRE prélève la retenue de la prime spéciale de sujétion, ordinaire et "
        "supplémentaire, sur les autres primes de l'aide-soignante, « partIS*primes*"
        "(txCotFP_sal + txSurcotIS_sal) », quand son script des cas types range la prime "
        "avec le traitement, qui paie déjà la retenue ordinaire : son net est plus bas, "
        "d'autant plus que la part des primes croît. La retenue supplémentaire de 1,5 % "
        "de la prime, que le dépôt prélève depuis le 10 octobre 2026 (fiche "
        "prime_speciale_sujetion_aides_soignants), ne déplace le rapport que d'un "
        "millième", 0.94, 0.99),
}

#: Les cas dont TRAJECTOiRE lit le revenu de l'année d'avant le départ même
#: chômée : son taux en salaire moyen s'en écarte, non celui en euros
#: constants. Le dépôt lit la dernière année travaillée en entier.
SMPT_INCOMPARABLE = ("cor_3_",)


def test_le_remplacement_net_de_trajectoire_se_retrouve_aux_prelevements_de_l_annee(
        trajectoire, flux_trajectoire, simulateur):
    """TRAJECTOiRE rapporte la pension nette du départ, RAFP comprise, au revenu
    net de l'année d'avant (``txRemplacementNet``, en euros constants ;
    ``txRemplacementNetSmpt``, en salaire moyen), chacun aux prélèvements de
    son année, la pension à ceux de sa catégorie de CSG. Sa pension, nette des
    mêmes prélèvements (l'histoire que l'IPP retrace,
    ``prelevements_historiques.yaml``), rapportée au revenu net que le dépôt
    tire de la même carrière (``cycle_de_vie.remplacement_net``), retrouve son
    taux à 1,5 % près sur 65 des 75 cas du témoin ; le policier et
    l'aide-soignante sont déclarés, dont TRAJECTOiRE prélève autrement les
    retenues de l'indemnité et de la prime. Jusqu'au 9 octobre 2026, les deux
    nets étaient aux taux de 2026, et les départs d'avant 2018 s'écartaient de
    1,2 à 3,7 %."""
    historique = charger_prelevements_historiques(simulateur.parametres.racine_donnees)
    pensions = historique.pensions
    ecarts: dict[str, list[float]] = {prefixe: [] for prefixe in ECARTS_REMPLACEMENT_NET}
    concordants = 0
    for cle, (comparaison, _) in flux_trajectoire.items():
        contenu = trajectoire["cas"][cle]
        liquidation = contenu["trajectoire"]["liquidation"]
        jour = dt.date.fromisoformat(liquidation["date"] + "-01")
        taux = CATEGORIES_CSG[liquidation["categorie_csg"]]
        caisses = contenu["trajectoire"]["caisses"]
        brute = 12.0 * sum(caisse["pension_mensuelle"] for caisse in caisses.values())
        maladie = 12.0 * sum(caisses[nom]["pension_mensuelle"] for nom in CAISSES_MALADIE
                             if nom in caisses)
        prelevement = (historique.taux_csg_pension(jour, taux) + pensions["crds"].valeur(jour)
                       + (pensions["casa"].valeur(jour) if taux != "reduit" else 0.0))
        nette = (brute * (1.0 - prelevement)
                 - maladie * pensions["maladie_complementaires"].valeur(jour))
        carriere = comparaison.carriere
        remplacement = cycle_de_vie.remplacement_net(
            simulateur, carriere, cycle_de_vie.revenus_nets(simulateur, carriere), nette)
        indicateurs = contenu["trajectoire"]["indicateurs"]
        rapport = remplacement.constants / indicateurs["txRemplacementNet"]
        declare = next((prefixe for prefixe in ECARTS_REMPLACEMENT_NET
                        if cle.startswith(prefixe)), None)
        if declare is not None:
            _, bas, haut = ECARTS_REMPLACEMENT_NET[declare]
            assert bas <= rapport <= haut, (cle, rapport)
            ecarts[declare].append(rapport)
            continue
        concordants += 1
        assert rapport == pytest.approx(1.0, abs=TOLERANCE_REMPLACEMENT_NET), (cle, rapport)
        if not cle.startswith(SMPT_INCOMPARABLE):
            assert remplacement.salaire_moyen / indicateurs["txRemplacementNetSmpt"] == (
                pytest.approx(1.0, abs=TOLERANCE_REMPLACEMENT_NET_SMPT)), cle
    assert concordants == 65
    for prefixe, rapports in ecarts.items():
        assert abs(sum(rapports) / len(rapports) - 1.0) > TOLERANCE_REMPLACEMENT_NET, prefixe


# ---------------------------------------------------------------------------
# L'OCDE : le taux de remplacement et le patrimoine retraite
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def simulateur_ocde() -> Simulateur:
    return Simulateur(Parametres(scenario_projection="ocde_2025"))


@pytest.fixture(scope="module")
def carrieres_ocde(ocde, simulateur_ocde) -> dict[tuple[str, str], object]:
    """Le salarié de l'OCDE : né en 2002, entré à 22 ans, toute sa carrière
    au même multiple du salaire moyen de l'OCDE, parti à l'âge qu'elle lui
    donne, et non cadre — l'Agirc-Arrco ne distingue plus depuis 2019."""
    macro = simulateur_ocde.macro
    age = ocde["age_de_depart"]["futur"]["hommes"]
    salaire_moyen = ocde["salaire_moyen"] / macro.salaire_moyen_niveau(2024)
    carrieres = {}
    for sexe in ("H", "F"):
        for multiple in ("0.5", "1", "2"):
            carriere = simulateur_ocde.carriere_simple(
                annee_naissance=2002, sexe=sexe, affiliation="salarie_prive_non_cadre",
                age_debut=22, age_liquidation=age,
                niveau_salaire=float(multiple) * salaire_moyen, profil_carriere="plat")
            carrieres[(sexe, multiple)] = simulateur_ocde.simuler(carriere)
    return carrieres


def test_le_salarie_de_l_ocde_part_au_taux_plein_a_l_age_qu_elle_lui_donne(ocde, simulateur_ocde):
    """Entré à 22 ans en 2024, il atteint les 172 trimestres à 65 ans : l'âge
    que l'OCDE écrit (``FRPLF22``), et celui où le pilote du dépôt le fait
    partir au taux plein."""
    cas = CasType(code="ocde", libelle="Salarié de l'OCDE", affiliation="salarie_prive_non_cadre",
                  age_debut=22, age_liquidation=64, niveau_salaire=1.0, profil_carriere="plat")
    assert cas.age_liquidation_pour(simulateur_ocde, 2002) == ocde["age_de_depart"]["futur"]["hommes"]


def _part_complementaire(comparaison) -> float:
    return sum(p.montant for p in comparaison.actuel.pensions_par_regime
               if p.regime.startswith(("agirc", "arrco"))) / comparaison.dernier_revenu_annualise


def test_le_taux_de_remplacement_brut_de_l_ocde_se_retrouve_a_l_agirc_arrco_pres(
        ocde, carrieres_ocde):
    """Au salaire moyen, le régime général du dépôt sert 42,7 % du dernier
    salaire : la moitié d'un salaire annuel moyen revalorisé sur les prix,
    quand les salaires réels montent de 1,25 % par an. L'écart à l'OCDE —
    2,7 points au salaire moyen, 4,9 à deux fois — est celui de
    l'Agirc-Arrco : il est, aux deux niveaux, le même quart de la pension
    complémentaire du dépôt, dont la valeur de service suit la convention du
    COR — le salaire moyen moins 1,16 point jusqu'en 2037, moins 0,86 ensuite
    — sous la valeur d'achat. À la moitié du salaire moyen, le minimum
    contributif, indexé sur le SMIC depuis 2023, relève le dépôt d'un point
    au-dessus de l'OCDE, dont le taux est celui du salaire moyen."""
    publies = ocde["taux_remplacement_brut"]["hommes"]
    facteurs = {}
    for multiple in ("0.5", "1", "2"):
        comparaison = carrieres_ocde[("H", multiple)]
        taux = 100.0 * comparaison.taux_remplacement_actuel
        assert abs(taux - publies[multiple]) <= 5.5, (multiple, taux, publies[multiple])
        if multiple != "0.5":
            facteurs[multiple] = ((publies[multiple] - taux) / 100.0
                                  / _part_complementaire(comparaison))
    assert 0.15 <= facteurs["1"] <= 0.35
    assert facteurs["2"] == pytest.approx(facteurs["1"], abs=0.05)
    assert 100.0 * carrieres_ocde[("H", "0.5")].taux_remplacement_actuel > publies["0.5"]


def test_le_patrimoine_retraite_de_l_ocde_se_retrouve_a_la_mortalite_pres(
        ocde, carrieres_ocde, simulateur_ocde):
    """Le patrimoine retraite est le taux de remplacement multiplié par la
    valeur d'un euro de rente : celle-ci, à 1,5 % réel sur la survie de
    génération, est celle de l'OCDE à 3 % près pour les hommes. Pour les
    femmes, la mortalité de l'ONU que l'OCDE retient les fait vivre plus
    longtemps que celle de l'INSEE que le dépôt suit : leur rente vaut 3 à
    8 % de moins au dépôt."""
    for sexe, qui, bas, haut in (("H", "hommes", -0.03, 0.03),
                                 ("F", "femmes", -0.08, -0.03)):
        for multiple in ("0.5", "1"):
            comparaison = carrieres_ocde[(sexe, multiple)]
            flux = cycle_de_vie.flux_des_systemes(simulateur_ocde, comparaison)["actuel"]
            patrimoine = cycle_de_vie.indicateurs(flux, simulateur_ocde).patrimoine
            rente = patrimoine / comparaison.taux_remplacement_actuel
            rente_publiee = (ocde["patrimoine_brut"][qui][multiple]
                             / (ocde["taux_remplacement_brut"][qui][multiple] / 100.0))
            ecart = rente / rente_publiee - 1.0
            assert bas <= ecart <= haut, (sexe, multiple, ecart)
