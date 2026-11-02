"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

La note de décision 0003 veut que le coût, la fabrique et les études fassent
tourner le moteur JavaScript au lieu du moteur Python, sous six conditions
(action 161, étape 5). La première lecture qui passe le pont est la grille des
carrières types de la table des agrégats, avec les deux départs que compare
Droits non cotisés (``scripts/construire_donnees.py``) ; ``test_agregats.py``
exige, à l'égalité exacte, que la table soit ce que le moteur Python calcule.
Puis le bilan figé : la même grille, dont il tire les écarts médians, et les
carrières d'exemple de « Pourquoi changer », simulées comme le site simule une
saisie ; ``test_cout.py`` et le contrôle de ``test_affirmations.py`` exigent
de même la table du moteur Python. Puis la grille du coût, sous les
conventions de projection du COR, que le portage date, bâtit et simule : le
Python ne lui passe que ce que chaque cas type décrit (action 161, étape 6).
Ici : le pont rend au bit près ce que le moteur Python date, bâtit et simule,
chaque nombre sous le type que le Python lui donne ; et, sans node, il
s'arrête, sans repli sur le moteur Python.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import fields, replace

import pytest

from retraite_notionnelle import Parametres, pont
from retraite_notionnelle.droit import liquidation
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.castypes import (
    CAS_TYPES, GENERATIONS, GRILLE_DU_COUT, carriere_de_la_grille, cases_de_la_grille)
from retraite_notionnelle.config import RACINE_PROJET
from retraite_notionnelle.simulateur import Simulateur

from outils_pont import TOLERANCE_DU_MOTEUR_PYTHON, Saisies, ecarts_d_ecriture

SCENARIOS = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

#: Des cases de la grille où passe ce que le pont fait traverser : un profil au
#: SMIC, des interruptions, des primes, la catégorie active, un non-salarié, un
#: exploitant ; plusieurs s'écartaient au dernier bit avant que le portage
#: calcule ses exponentielles comme la libm de Linux.
CASES = (("smic_carriere_complete", 1970), ("carriere_interrompue", 1970),
         ("fonctionnaire_actif", 1960), ("fonctionnaire_sedentaire", 2000),
         ("profession_liberale", 1960), ("exploitant_agricole", 2000), ("cadre", 2000))

#: Des saisies comme celles que le bilan figé simule : la carrière d'exemple de
#: « Pourquoi changer » au SMIC, et un cadre à deux fois le salaire moyen.
SAISIES = (
    {"naissance": 1990, "statut": "salarie_prive_non_cadre", "debut": 22, "liquidation": 64,
     "salaire": 0.55, "unite_revenu": "moyen", "demandee": True},
    {"naissance": 1975, "statut": "salarie_prive_cadre", "debut": 24, "liquidation": 65,
     "salaire": 2.0, "unite_revenu": "moyen", "demandee": True},
)


def _aujourd_hui(aujourd_hui) -> dict | None:
    """Ce que les écarts médians lisent de la pension d'aujourd'hui d'un
    retraité, ou rien pour qui n'est pas encore parti."""
    if aujourd_hui is None:
        return None
    return {
        "pension_annuelle": aujourd_hui.pension("actuel"),
        "pensions_totales": {scenario: aujourd_hui.pension_totale(scenario)
                             for scenario in SCENARIOS},
        "rente_capitalisee_volontaire": aujourd_hui.rente_capitalisee_volontaire,
    }


def test_le_pont_rend_au_bit_pres_ce_que_le_moteur_python_simule():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    simulateur = Simulateur(Parametres())
    demandes, attendus = [], {}
    for code, generation in CASES:
        cas = next(cas for cas in CAS_TYPES if cas.code == code)
        carriere = carriere_de_la_grille(simulateur, cas, generation)
        comparaison = simulateur.simuler(carriere)
        cle = f"{code}|{generation}"
        demandes.append({"cle": cle, "options": cas.options(generation, carriere.age_liquidation)})
        attendus[cle] = {
            "annee_liquidation": comparaison.carriere.annee_liquidation,
            "annees_liquidation": {scenario: comparaison.carriere_de(scenario).annee_liquidation
                                   for scenario in SCENARIOS},
            "variations": {scenario: comparaison.variation_totale(scenario)
                           for scenario in SCENARIOS},
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "trimestres_requis": comparaison.actuel.trimestres_requis,
            # Ce que les écarts médians du bilan lisent d'une case.
            "pensions_totales": {scenario: comparaison.pension_totale(scenario)
                                 for scenario in SCENARIOS},
            "rentes_volontaires": {scenario: comparaison.rente_capitalisee_volontaire(scenario)
                                   for scenario in SCENARIOS},
            "aujourd_hui": _aujourd_hui(comparaison.aujourd_hui),
        }
    resultats, echecs = pont.carrieres(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    # Les deux sortes de cases : celles qui partiront, celles déjà parties.
    assert {lu["aujourd_hui"] is None for lu in resultats.values()} == {True, False}
    for lu in resultats.values():
        assert type(lu["annee_liquidation"]) is int
        assert type(lu["trimestres_requis"]) is int
        assert type(lu["pension_annuelle"]) is float
        for lecture in ("variations", "pensions_totales", "rentes_volontaires"):
            assert all(type(nombre) is float for nombre in lu[lecture].values()), lecture
        if lu["aujourd_hui"] is not None:
            assert type(lu["aujourd_hui"]["pension_annuelle"]) is float
            assert type(lu["aujourd_hui"]["rente_capitalisee_volontaire"]) is float
            assert all(type(nombre) is float
                       for nombre in lu["aujourd_hui"]["pensions_totales"].values())


def test_le_pont_simule_une_saisie_comme_le_site_au_bit_pres_du_moteur_python():
    """Les carrières d'exemple du bilan figé sont des saisies, que le portage
    simule comme le site (``Contexte.simuler``, ``contexte.js``) : de chacune,
    la fiche de paie de l'année de référence sous le droit en vigueur, le
    passage aux euros constants, et la pension de chaque système demandé, au
    bit près de ce que le moteur Python simule de la carrière que le portage
    bâtit de la même saisie — la saisie n'a que son exemplaire (action 161,
    étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    demandes = [{"cle": str(rang), "saisie": saisie} for rang, saisie in enumerate(SAISIES)]
    carrieres, refus = pont.carrieres_des_saisies(demandes)
    assert not refus
    attendus = {}
    for cle, (parametres, carriere) in carrieres.items():
        comparaison = Simulateur(parametres).simuler(carriere)
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        attendus[cle] = {
            "fiche": {"annee": fiche.annee, "brut": fiche.brut, "net": fiche.net,
                      "retraite_totale": fiche.retraite_totale,
                      "retraite_employeur": fiche.retraite_employeur},
            "coefficient_euros_constants": comparaison.coefficient_euros_constants,
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "pensions": {scenario: getattr(comparaison, scenario).pension_annuelle
                         for scenario in SCENARIOS},
        }
    resultats, echecs = pont.saisies(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    for lu in resultats.values():
        assert type(lu["fiche"]["annee"]) is int
        assert all(type(lu["fiche"][champ]) is float
                   for champ in ("brut", "net", "retraite_totale", "retraite_employeur"))
        assert type(lu["coefficient_euros_constants"]) is float
        assert type(lu["pension_annuelle"]) is float
        assert all(type(pension) is float for pension in lu["pensions"].values())


def test_chaque_case_passe_au_portage_partant_a_l_age_que_le_pilote_fixe():
    """Le Python fixe l'âge de chaque départ et écarte ce que le droit écarte
    (``carriere_de_la_grille``) ; le portage simule. Sous les conventions du
    COR, la carrière d'un cas type se déforme en Python : rien ne passe."""
    simulateur = Simulateur(Parametres())
    types = tuple(cas for cas in CAS_TYPES if cas.code in ("cadre", "carriere_interrompue"))
    options, echecs = cases_de_la_grille(simulateur, types, (1940, 2000))
    assert set(options) | set(echecs) == {(cas.code, generation)
                                         for cas in types for generation in (1940, 2000)}
    for cas in types:
        for generation in (1940, 2000):
            if (cas.code, generation) in options:
                carriere = carriere_de_la_grille(simulateur, cas, generation)
                assert options[(cas.code, generation)] == cas.options(
                    generation, carriere.age_liquidation)
    with pytest.raises(ValueError, match="COR"):
        cases_de_la_grille(simulateur.pour_la_projection(), types, (2000,))


#: Des cohortes de la grille du coût où passe chaque chemin du pilote : le point
#: fixe qui monte ; la règle de l'ouverture, celle des services ; l'inaptitude ;
#: les primes des fonctionnaires, que les conventions du COR projettent ; et la
#: descente d'un an en un an (``pilote.descendre``), que prennent l'agent de
#: conduite né en 1879, l'actif né en 1884, l'artisan né en 1911, l'exploitant
#: né en 1925 et le contractuel né en 1884.
DEPARTS_D_ESSAI = (("salaire_moyen", 1960), ("smic_carriere_complete~inapte", 1965),
                   ("agent_sncf_conduite", 1879), ("agent_ieg", 2000), ("militaire", 1980),
                   ("fonctionnaire_sedentaire", 1990), ("fonctionnaire_actif", 1884),
                   ("fonctionnaire_sedentaire~super_actif", 1970), ("artisan", 1911),
                   ("exploitant_agricole", 1925), ("contractuel_public", 1884))


def _ages_au_portage(simulateur, cohortes, variante: str = "droit"):
    """Les âges que le portage fixe aux ``cohortes``, ``(cas type, génération)``,
    sous les paramètres de ``simulateur`` (:func:`pont.ages_de_depart`)."""
    from retraite_notionnelle.castypes import primes_projetees_en_donnees

    return pont.ages_de_depart(
        [{"cle": f"{cas.code}|{generation}", **cas.pour_le_portage(simulateur, generation)}
         for cas, generation in cohortes],
        simulateur.parametres, primes_projetees_en_donnees(simulateur), variante)


def test_le_portage_date_les_cas_types_au_bit_pres_du_pilote_python():
    """Le coût fait dater ses cas types au portage (``ageDeDepart`` de
    ``moteur/js/pilote.js`` ; action 161, étape 6), sur la carrière d'un seul
    statut que leurs options décrivent, ses primes projetées sous les
    conventions du COR (``castypes.primes_projetees``) : chaque cohorte part à
    l'âge que le pilote Python lui fixe (``pilote.age_de_depart``), au bit
    près, sous les paramètres de référence comme sous ceux de la projection ;
    l'âge écrit sous la variante ``absolu``."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import pilote

    cohortes = [(next(cas for cas in GRILLE_DU_COUT if cas.code == code), generation)
                for code, generation in DEPARTS_D_ESSAI]
    for simulateur in (Simulateur(Parametres()), Simulateur(Parametres()).pour_la_projection()):
        ages, refus = _ages_au_portage(simulateur, cohortes)
        assert not refus
        attendus = {f"{cas.code}|{generation}": float(pilote.age_de_depart(simulateur, cas,
                                                                            generation))
                    for cas, generation in cohortes}
        assert ages == attendus
        assert all(type(age) is float for age in ages.values())
        # La descente : un an plus tôt que l'âge écrit, et plus.
        assert ages["artisan|1911"] == 62.0 and ages["contractuel_public|1884"] == 61.0
    absolus, _ = _ages_au_portage(simulateur, cohortes, "absolu")
    assert absolus == {f"{cas.code}|{generation}": float(cas.age_liquidation)
                       for cas, generation in cohortes}


def test_le_portage_fait_attendre_l_annulation_et_descendre_a_la_carriere_longue():
    """Les deux chemins du pilote que la grille ne prend pas, que
    ``tests/test_liquidation.py`` tire du texte, refaits au portage. Né en 1955,
    entré à vingt ans et sans activité après quarante et une années, un salarié
    a 164 trimestres des 166 de sa génération et les garde : sa règle le fait
    attendre le taux plein de l'âge d'annulation de la décote, 67 ans
    (L. 351-8, 1°). Né en 1966, entré à seize ans et sans activité depuis ses
    59 ans, il a ses 172 trimestres cotisés à la fin de 2024 : la carrière
    longue lui ouvre le départ à 60 ans (L. 351-1-1, D. 351-1-1), sous la règle
    du taux plein comme sous celle de l'ouverture."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    salarie = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen")
    inactif = replace(salarie, code="salaire_moyen~inactif", age_debut=20,
                      interruptions_relatives=tuple((decalage, "inactivite")
                                                    for decalage in range(41, 51)))
    longues = [replace(salarie, code=f"salaire_moyen~inactif_a_59_ans~{regle}", age_debut=16,
                       regle_liquidation=regle,
                       interruptions_relatives=tuple((decalage, "inactivite")
                                                     for decalage in range(43, 64)))
               for regle in ("taux_plein", "ouverture")]
    ages, refus = _ages_au_portage(Simulateur(Parametres()),
                                   [(inactif, 1955), *((longue, 1966) for longue in longues)])
    assert not refus
    assert ages == {"salaire_moyen~inactif|1955": 67.0,
                    "salaire_moyen~inactif_a_59_ans~taux_plein|1966": 60.0,
                    "salaire_moyen~inactif_a_59_ans~ouverture|1966": 60.0}


#: Des cohortes de la grille du coût où passe ce que le portage bâtit : deux
#: cases que le droit écarte, chacune sous son motif ; l'entrée tardive et les
#: primes projetées d'un fonctionnaire, sous les conventions du COR ; le
#: super-actif, entré dans son corps après des années de privé ; l'inaptitude ;
#: la règle des services ; la descente ; un départ que l'âge légal de la
#: proposition reporte, et un autre, à 67 ans, qu'il ne reporte pas.
CARRIERES_D_ESSAI = (("salaire_moyen", 1879), ("agent_ieg", 1886),
                     ("fonctionnaire_sedentaire", 1990),
                     ("fonctionnaire_sedentaire~super_actif", 1970),
                     ("smic_carriere_complete~inapte", 1965), ("militaire", 1980),
                     ("artisan", 1911), ("salaire_moyen", 1975), ("profession_liberale", 1980))


def test_le_portage_bat_les_carrieres_de_la_grille_comme_le_python():
    """Le coût fait bâtir au portage la carrière de chaque case de sa grille,
    partie à l'âge que le portage lui fixe (action 161, étape 6) : sous les
    conventions du COR, l'entrée tardive d'un fonctionnaire, que le Python
    décrit en métiers, et ses primes projetées ; les cases que le droit écarte,
    sous le motif du Python ; et les deux carrières que l'âge légal de la
    proposition en dérive, poursuivie jusqu'à lui ou attendue sans activité.
    Chacune revient sous les types du Python, égale à celle qu'il bâtit
    (``castypes.carriere_de_la_grille``, ``Carriere.prolongee``) ; d'une cohorte
    voisine, l'année et le mois de son départ seulement."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.castypes import primes_projetees_en_donnees

    simulateur = Simulateur(Parametres()).pour_la_projection()
    macro, age_legal = simulateur.macro, simulateur.parametres.age_legal_liberal
    cohortes = {f"{code}|{generation}": (next(cas for cas in GRILLE_DU_COUT if cas.code == code),
                                         generation)
                for code, generation in CARRIERES_D_ESSAI}
    lus, refus = pont.carrieres_de_la_grille(
        [{"cle": f"{cle}|{rendre}", **cas.pour_le_portage(simulateur, generation),
          "rendre": rendre}
         for cle, (cas, generation) in cohortes.items() for rendre in ("carriere", "depart")],
        simulateur.parametres, primes_projetees_en_donnees(simulateur), "droit")
    assert refus == {f"salaire_moyen|1879|{rendre}": "liquidation antérieure à la répartition"
                     for rendre in ("carriere", "depart")} | {
        f"agent_ieg|1886|{rendre}": "aucun régime actif sur la période"
        for rendre in ("carriere", "depart")}
    for cle, (cas, generation) in cohortes.items():
        if f"{cle}|carriere" in refus:
            with pytest.raises(ValueError, match=refus[f"{cle}|carriere"]):
                carriere_de_la_grille(simulateur, cas, generation)
            continue
        carriere = carriere_de_la_grille(simulateur, cas, generation)
        bati = lus[f"{cle}|carriere"]
        assert type(bati["carriere"]) is Carriere
        assert bati["carriere"] == carriere, cle
        assert bati["age"] == float(carriere.age_liquidation), cle
        reportee = carriere.prolongee(age_legal, macro)
        if reportee is carriere:
            assert (bati["reportee"], bati["attente"]) == (None, None), cle
        else:
            assert bati["reportee"] == reportee, cle
            assert bati["attente"] == carriere.prolongee(age_legal, macro,
                                                         attente_travaillee=False), cle
        assert lus[f"{cle}|depart"] == {"age": bati["age"], "annee": carriere.annee_liquidation,
                                        "mois": carriere.mois_liquidation}, cle
    # Ce que les cohortes font traverser : l'entrée tardive, un report et un
    # départ que l'âge légal ne reporte pas.
    batis = [lu for cle, lu in lus.items() if cle.endswith("|carriere")]
    assert any(len({ligne.affiliation for ligne in lu["carriere"].lignes}) > 1 for lu in batis)
    assert {lu["reportee"] is None for lu in batis} == {True, False}


#: Les jumeaux Python par lesquels une grille se datait et se bâtissait : le
#: pilote, l'ouverture du droit qu'il interroge, les constructeurs de
#: carrières, leurs prolongations, la projection des primes.
def _jumeaux_qui_datent_et_batissent():
    from retraite_notionnelle import castypes, pilote
    from retraite_notionnelle.droit import ouvrir

    return ((pilote, "age_de_depart"), (pilote, "point_fixe"), (pilote, "descendre"),
            (ouvrir, "age_ouverture_droit"), (ouvrir, "age_taux_plein_droit"),
            (ouvrir, "age_annulation_droit"), (Simulateur, "carriere_simple"),
            (Simulateur, "carriere_parcours"), (Carriere, "prolongee"),
            (castypes, "primes_projetees"))


def _interdire(monkeypatch, jumeaux) -> None:
    """Les jumeaux Python nommés, ``(objet, nom)``, qu'on empêche de calculer."""
    def interdit(*_, **__):
        raise AssertionError("un jumeau Python date ou bâtit ce que le portage doit rendre")

    for objet, nom in jumeaux:
        monkeypatch.setattr(objet, nom, interdit)


def test_la_grille_des_carrieres_types_se_date_au_portage_sans_les_jumeaux(memoire_isolee,
                                                                           monkeypatch):
    """La grille des carrières types de la table (``castypes.cases_de_la_grille``)
    et les âges qu'en écrit ``figer_cas_types`` (``castypes.ages_de_la_grille``)
    se datent au portage (action 161, étape 6) : le pilote Python, l'ouverture
    du droit et les constructeurs de carrières, qu'on empêche ici de calculer,
    n'y entrent pas. Chaque case et chaque motif sont ceux du Python, et chaque
    âge l'est sous son type : l'âge écrit, un entier, quand le droit ne le
    déplace pas — la table l'écrit sans décimale —, un flottant sinon."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import memoire
    from retraite_notionnelle.castypes import ages_de_la_grille

    simulateur = Simulateur(Parametres())
    # Les générations de la table, et deux que le droit écarte en partie.
    generations = (1880, 1885, *GENERATIONS)
    with memoire.modele_modifie():
        en_python = cases_de_la_grille(simulateur, CAS_TYPES, generations)
        ages_en_python = ages_de_la_grille(simulateur)
    _interdire(monkeypatch, _jumeaux_qui_datent_et_batissent())
    assert cases_de_la_grille(simulateur, CAS_TYPES, generations) == en_python
    ages = ages_de_la_grille(simulateur)
    assert ages == ages_en_python
    assert _types(ages) == _types(ages_en_python)
    assert {type(age) for age in ages.values()} == {int, float}
    assert set(en_python[1].values()) == {"liquidation antérieure à la répartition",
                                          "aucun régime actif sur la période"}


def test_les_departs_des_facteurs_de_la_depense_se_datent_au_portage_sans_les_jumeaux(
        memoire_isolee, monkeypatch):
    """Les dates des départs que comptent les facteurs de la dépense
    (``facteurs_depense.dates_des_departs``) se datent au portage (action 161,
    étape 6), sous chacune de leurs formes : la grille, l'entrée dans l'emploi
    décalée comme celle de l'EIC, le départ dès l'ouverture du droit. Le pilote
    Python et les constructeurs de carrières, qu'on empêche ici de calculer,
    n'y entrent pas ; chaque date est celle du Python, cohorte par cohorte, et
    une case que le droit écarte n'en a aucune."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import memoire
    from retraite_notionnelle.facteurs_depense import dates_des_departs

    cas = tuple(cas for cas in GRILLE_DU_COUT if cas.code in (
        "salaire_moyen", "fonctionnaire_sedentaire", "militaire", "agent_ieg"))
    formes = ({}, {"entree_depuis": 1960}, {"a_l_ouverture": True})

    def dates():
        return [dates_des_departs(Parametres(), cas_types=cas, generations=(1880, 1965, 2000),
                                  **forme) for forme in formes]

    with memoire.modele_modifie():
        en_python = dates()
    _interdire(monkeypatch, _jumeaux_qui_datent_et_batissent())
    au_portage = dates()
    assert au_portage == en_python
    # L'entrée décalée et le départ dès l'ouverture déplacent des dates ; la
    # grille écarte des cases de la génération 1880.
    assert au_portage[1] != au_portage[0] and au_portage[2] != au_portage[0]
    assert len(au_portage[0]) < len(cas) * 3 * 5


def test_sans_node_le_pont_s_arrete_sans_repli(monkeypatch):
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.carrieres([{"cle": "cadre|2000", "options": {}}], SCENARIOS)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.saisies([{"cle": "0", "saisie": SAISIES[0]}], SCENARIOS)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.grille_du_cout([], SCENARIOS, Parametres())
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.scenario_actuel([{"cle": "a", "requete": REQUETE}])
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.droit({"a": ("ouvrir.duree_requise", pont.MOTEUR, pont.Periode("regime_general", 2020),
                          _carriere_d_openfisca({"code": "a", "debut": 1980, "liquidation": 2020,
                                                 "naissance": 1958, "salaire": 20_000.0}))})


# -- sans paquet, le pont reste ouvert --------------------------------------------

#: Une requête du simulateur : un salarié du privé né en 1965.
REQUETE = {"naissance": "1965-03-15", "statut": "salarie_prive_non_cadre",
           "debut": "1987-09", "liquidation": "2029-04", "salaire": "2500",
           "unite_revenu": "euros_mois"}


def _lancements(monkeypatch) -> list:
    """Les node que le pont lance désormais, sur un pont refermé : chacun se
    compte, et le pont d'une seule demande est interdit."""
    pont.fermer()
    lances, reel = [], subprocess.Popen

    def lancer(commande, *arguments, **options):
        lances.append(commande)
        return reel(commande, *arguments, **options)

    def interdit(*_arguments, **_options):
        raise AssertionError("sans paquet, le pont ne se lance pas pour une seule demande")

    monkeypatch.setattr(subprocess, "Popen", lancer)
    monkeypatch.setattr(subprocess, "run", interdit)
    return lances


def test_sans_paquet_le_pont_reste_ouvert_d_une_demande_a_l_autre(monkeypatch):
    """Les tests demandent au pont une carrière à la fois (action 161,
    étape 6) : sur le paquet du dépôt, node ne se lance qu'une fois, et ne lit
    le paquet qu'une fois, au lieu de trois dixièmes de seconde par demande ;
    ce qu'il rend est ce que rend le pont lancé pour une seule demande."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    paquet = (RACINE_PROJET / "moteur" / "donnees.json").read_bytes()
    seul, _ = pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}], paquet)
    lances = _lancements(monkeypatch)
    premier, _ = pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
    autre, refus = pont.carrieres_des_saisies(
        [{"cle": "b", "requete": {**REQUETE, "salaire": "3000"}},
         {"cle": "c", "requete": {**REQUETE, "statut": "inconnu"}}])
    try:
        assert len(lances) == 1 and lances[0][-1] == "--servir"
        assert premier["a"][0] == seul["a"][0]
        assert (json.dumps(pont.carriere_en_donnees(premier["a"][1]))
                == json.dumps(pont.carriere_en_donnees(seul["a"][1])))
        assert list(autre) == ["b"] and "inconnu" in refus["c"]
    finally:
        pont.fermer()


def test_une_saisie_par_la_pension_passe_le_pont_par_la_carriere_que_l_inversion_trouve():
    """Sa carrière vient de la pension, que le contexte inverse en la
    simulant (``Contexte.simuler``, ``contexte.js``) : le pont rend celle que
    l'inversion trouve, que le site simule, et non une carrière au revenu de
    la saisie."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.web.site import module, site

    par_pension = {**REQUETE, "saisie_par": "pension", "pension": "1500"}
    lus, refus = pont.carrieres_des_saisies([{"cle": "pension", "requete": par_pension},
                                             {"cle": "revenu", "requete": REQUETE}])
    assert not refus
    (parametres, carriere), (_, au_revenu) = lus["pension"], lus["revenu"]
    saisie = module("saisie").Saisie.depuis_requete(
        par_pension, False, site().contexte.paquet.presomptions)
    assert (Simulateur(parametres).simuler(carriere).actuel.pension_annuelle
            == site().contexte.simuler(saisie).actuel.pension_annuelle)
    assert ([ligne.revenu for ligne in carriere.lignes]
            != [ligne.revenu for ligne in au_revenu.lignes])


# -- le scénario 1 des confrontations ----------------------------------------------

#: Un relevé que l'appelant prolonge à sa façon (``scripts/estimation_officielle.py``) :
#: une mère de trois enfants, salariée du privé de 2002 à 2025, qui part en juin 2033.
RELEVE_A_PROLONGER = {
    "naissance": "1966-05-12", "sexe": "F", "liquidation": "2033-06", "enfants": "3",
    "euros": "2026",
    "releve": ",".join(f"{annee}:salarie_prive_non_cadre:{18_300 + 600 * (annee - 2002)}"
                       for annee in range(2002, 2026)),
}


def test_le_pont_sert_le_scenario_actuel_au_bit_pres_du_moteur_python():
    """Les confrontations aux références extérieures — l'estimation officielle,
    Destinie 2 — lisent du scénario 1 ce qu'aucun témoin n'écrit : la part de
    chaque régime dans la majoration pour enfants, la durée validée, le taux.
    Le portage le sert (:func:`pont.scenario_actuel`), chaque nombre sous le
    type que le Python lui donne, et le moteur Python, qui garde ses jumeaux,
    le refait au bit près sous Linux x86_64 (:data:`TOLERANCE_DU_MOTEUR_PYTHON`).
    Un relevé que l'appelant a prolongé à sa façon s'en tient à ses années."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    destinie = json.loads((RACINE_PROJET / "tests" / "temoins" / "destinie_2.json")
                          .read_text(encoding="utf-8"))["cas"]
    cas = [{"cle": "veuf", "requete": destinie["reversion_trois_enfants"]["requete"]},
           {"cle": "metiers", "requete": REQUETE},
           {"cle": "prolonge", "requete": RELEVE_A_PROLONGER},
           {"cle": "tel_quel", "requete": RELEVE_A_PROLONGER, "prolonger": False}]
    servis, refus = pont.scenario_actuel(cas)
    assert refus == {}
    refaits, refus = Saisies().scenario_actuel(cas)
    assert refus == {}
    for cle, servi in servis.items():
        assert ecarts_d_ecriture(refaits[cle], servi,
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], cle
    veuf = servis["veuf"]
    (majoration,) = (avantage for avantage in veuf["actuel"]["avantages_appliques"]
                     if avantage["code"] == "majoration_enfants")
    assert "regime_general" in {regime for regime, _ in majoration["par_regime"]}
    assert veuf["reversion"]["regimes"] and servis["metiers"]["reversion"] is None
    # Tel quel, le relevé s'arrête en 2025 ; prolongé, il court jusqu'au départ.
    assert (servis["tel_quel"]["actuel"]["trimestres_valides"]
            < servis["prolonge"]["actuel"]["trimestres_valides"])
    assert (servis["tel_quel"]["annee_liquidation"],
            servis["tel_quel"]["mois_liquidation"]) == (2033, 6)
    for servi in servis.values():
        actuel = servi["actuel"]
        assert type(servi["annee_liquidation"]) is int and type(servi["mois_liquidation"]) is int
        assert type(actuel["trimestres_valides"]) is int
        assert all(type(nombre) is float for nombre in (
            servi["coefficient_euros_constants"], actuel["pension_annuelle"],
            actuel["pension_hors_repartition"], actuel["taux_liquidation"]))
        assert all(type(pension["montant"]) is float for pension in actuel["pensions_par_regime"])
        assert all(type(avantage["montant"]) is float and type(part) is float
                   for avantage in actuel["avantages_appliques"]
                   for _, part in avantage["par_regime"])


# -- le droit, fonction par fonction -------------------------------------------------

def _carriere_d_openfisca(profil: dict) -> Carriere:
    """La carrière exacte d'un profil d'OpenFisca au régime général, bâtie à
    la main comme ``tests/test_oracle.py`` la bâtit (``_notre_calcul``)."""
    lignes = [AnneeCarriere(annee=annee, revenu=profil["salaire"],
                            affiliation="salarie_prive_non_cadre", trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])]
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"])


def test_le_pont_fait_appeler_les_fonctions_du_droit_au_bit_pres_de_leur_jumeau():
    """Les exemples d'OpenFisca et des caisses (``tests/test_oracle.py``)
    éprouvent le droit fonction par fonction, sur des carrières bâties à la
    main : le pont les fait appeler au portage (:func:`pont.droit`), la carrière
    passée en données, le moteur du scénario 1 et la période d'un régime
    désignés, et rend ce que chacune rend sous le type de son jumeau Python
    (:data:`pont.LECTURES_DU_DROIT`) — au bit près de lui sous Linux x86_64,
    sur chaque profil d'OpenFisca au régime général. Une fonction que le pont
    ne sait pas relire est refusée avant node."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import actuel_en_donnees
    from retraite_notionnelle.donnees.chargement import Fiabilite
    from retraite_notionnelle.droit import liquider, ouvrir

    profils = json.loads((RACINE_PROJET / "tests" / "temoins" / "openfisca_regime_general.json")
                         .read_text(encoding="utf-8"))["profils"]
    simulateur = Simulateur(Parametres())
    scenario = simulateur.scenario_actuel
    for code, temoin in profils.items():
        profil = temoin["profil"]
        carriere, depart = _carriere_d_openfisca(profil), profil["liquidation"]
        age = float(depart - profil["naissance"])
        periode = simulateur.catalogue["regime_general"].periode(depart)
        requis, _ = ouvrir.duree_requise(scenario, periode, carriere)
        _, annulation, _ = liquider.decote_opposable(scenario, periode, carriere, depart)
        resultat = scenario.calculer(carriere)
        # Ce que rend chaque jumeau Python, relu sous le type que le pont
        # déclare : « 2 » que le jumeau rend pour des trimestres de décote,
        # flottants, s'y relit « 2.0 », comme le zéro d'une somme vide des témoins.
        attendus = {cle: pont.relu_du_droit(fonction, rendu) for cle, (fonction, rendu) in {
            "requis": ("ouvrir.duree_requise", ouvrir.duree_requise(scenario, periode, carriere)),
            "proratisation": ("liquider.duree_proratisation", liquider.duree_proratisation(
                scenario, periode, carriere, requis)),
            "decote": ("liquider.decote_opposable", liquider.decote_opposable(
                scenario, periode, carriere, depart)),
            "salaire": ("liquider.salaire_de_reference", liquider.salaire_de_reference(
                scenario, "regime_general", carriere, periode, depart, True,
                profil["naissance"], True)),
            "manquants": ("liquider.trimestres_de_decote", liquider.trimestres_de_decote(
                scenario, periode, carriere, resultat.trimestres_valides, requis, age,
                annulation)),
            "resultat": ("scenario_actuel.calculer", actuel_en_donnees(resultat)),
        }.items()}
        rg = pont.Periode("regime_general", depart)
        lus, echecs = pont.droit({
            "requis": ("ouvrir.duree_requise", pont.MOTEUR, rg, carriere),
            "proratisation": ("liquider.duree_proratisation", pont.MOTEUR, rg, carriere, requis),
            "decote": ("liquider.decote_opposable", pont.MOTEUR, rg, carriere, depart),
            "salaire": ("liquider.salaire_de_reference", pont.MOTEUR, "regime_general", carriere,
                        rg, depart, True, profil["naissance"], True),
            "manquants": ("liquider.trimestres_de_decote", pont.MOTEUR, rg, carriere,
                          resultat.trimestres_valides, requis, age, annulation),
            "resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
        })
        assert echecs == {}, code
        for cle, attendu in attendus.items():
            assert ecarts_d_ecriture(lus[cle], attendu,
                                     tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], (code, cle)
        assert type(lus["requis"]) is tuple and type(lus["requis"][0]) is int
        assert lus["requis"][1] is None or type(lus["requis"][1]) is Fiabilite
        assert type(lus["decote"][1]) is float and type(lus["salaire"]) is float
        assert type(lus["manquants"]) is float
        assert lus["resultat"]["trimestres_valides"] == attendus["resultat"]["trimestres_valides"]
    with pytest.raises(ValueError, match="liquider.inconnue"):
        pont.droit({"a": ("liquider.inconnue", pont.MOTEUR)})


def test_le_controle_du_droit_voit_un_ulp_deplace_dans_le_jumeau_python(monkeypatch):
    """Les exemples d'OpenFisca et des caisses font appeler le droit au
    portage, et son jumeau Python le refait tant qu'il reste (action 161) :
    :func:`outils_pont.droit_et_refait` rend ce que le portage rend, chaque
    fonction refaite par son jumeau (``JUMEAUX_DU_DROIT``, un par fonction que
    le pont relit), et arrête la confrontation sur un ulp qu'on y déplace —
    au-delà de la tolérance hors de Linux x86_64."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    import math

    from outils_pont import JUMEAUX_DU_DROIT, droit_et_refait

    assert set(JUMEAUX_DU_DROIT) == set(pont.LECTURES_DU_DROIT)
    profil = {"code": "a", "debut": 1980, "liquidation": 2016, "naissance": 1954,
              "salaire": 31_000.0}
    carriere, rg = _carriere_d_openfisca(profil), pont.Periode("regime_general", 2016)
    appels = {
        "salaire": ("liquider.salaire_de_reference", pont.MOTEUR, "regime_general", carriere,
                    rg, 2016, True, 1954, True),
        "resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
    }
    lus, refus = droit_et_refait(appels)
    assert refus == {} and lus == pont.droit(appels)[0]
    jumeau = JUMEAUX_DU_DROIT["liquider.salaire_de_reference"]

    def deplace(*arguments):
        rendu = jumeau(*arguments)
        return (math.nextafter(rendu, math.inf) if TOLERANCE_DU_MOTEUR_PYTHON == 0.0
                else rendu * (1 + 1e-9))

    monkeypatch.setitem(JUMEAUX_DU_DROIT, "liquider.salaire_de_reference", deplace)
    with pytest.raises(AssertionError, match="salaire"):
        droit_et_refait(appels)


def test_le_pont_bat_une_carriere_de_ses_options_sans_la_faire_passer():
    """Les exemples officiels cherchent la carrière qui rend leurs trimestres,
    un âge de début après l'autre : chaque essai se liquide sur la carrière
    que ``simulateur.carriere_simple`` bâtit de ses options
    (``pont.CarriereSimple``), que le portage bâtit lui-même, sans qu'elle
    passe le pont. Liquidée, elle rend ce que rend la même carrière bâtie,
    écrite en données et relue ; le jumeau Python la bâtit et la refait au bit
    près (``droit_et_refait``)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import droit_et_refait

    options = {"annee_naissance": 1962, "sexe": "F", "affiliation": "salarie_prive_non_cadre",
               "age_debut": 21.5, "age_liquidation": 64.25, "nombre_enfants": 2,
               "interruptions": {1990: "chomage_indemnise"}, "temps_partiel": {2000: 0.8}}
    lus, echecs = droit_et_refait({
        "carriere": ("simulateur.carriere_simple", pont.SIMULATEUR, options),
        "par_options": ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple(options)),
    })
    assert echecs == {}
    relue = pont.carriere_des_donnees(lus["carriere"])
    par_donnees, _ = pont.droit({"resultat": ("scenario_actuel.calculer", pont.MOTEUR, relue)})
    assert lus["par_options"] == par_donnees["resultat"]


def test_le_pont_prete_une_table_au_moteur_du_portage(monkeypatch):
    """Un test prête au moteur Python une de ses tables par une autre
    (``monkeypatch.setattr``) — celle des indépendants par celle du régime
    général, pour lire ce que la règle des artisans ajoute à leur pension : le
    pont prête la même au moteur du portage (``pont.MOTEUR.pretant``), sur
    une copie, au bit près du moteur Python sous le même prêt ; le moteur sans
    prêt n'en garde rien, et une table que le moteur ne porte pas arrête
    l'appel. L'artisan né en 1949 en est la mesure : vingt et une années
    retenues (R. 634-1-1), vingt-cinq au régime général."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import actuel_en_donnees

    carriere = Carriere(
        annee_naissance=1949, sexe="H", age_liquidation=62.0, identifiant="artisan_1949",
        lignes=[AnneeCarriere(annee=annee, revenu=12_000.0 + 900.0 * (annee - 1973),
                              affiliation="artisan", trimestres_valides=4)
                for annee in range(1973, 2011)])
    pretant = pont.MOTEUR.pretant("annees_revenu_independants", "annees_salaire_reference")
    lus, echecs = pont.droit({
        "sans": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
        "prete": ("scenario_actuel.calculer", pretant, carriere),
        "apres": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
    })
    assert echecs == {}
    actuel = Simulateur(Parametres()).scenario_actuel
    sans = pont.relu_du_droit("scenario_actuel.calculer", actuel_en_donnees(actuel.calculer(carriere)))
    monkeypatch.setattr(actuel, "annees_revenu_independants", actuel.annees_salaire_reference)
    prete = pont.relu_du_droit("scenario_actuel.calculer",
                               actuel_en_donnees(actuel.calculer(carriere)))
    assert ecarts_d_ecriture(lus["prete"], prete, tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []
    assert ecarts_d_ecriture(lus["sans"], sans, tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []
    assert lus["apres"] == lus["sans"]
    assert lus["prete"]["pension_annuelle"] < lus["sans"]["pension_annuelle"]
    _, echecs = pont.droit({"inconnue": (
        "scenario_actuel.calculer",
        pont.MOTEUR.pretant("table_inconnue", "annees_salaire_reference"), carriere)})
    assert "tableInconnue" in echecs["inconnue"]


def test_le_pont_ouvert_se_relance_quand_le_paquet_du_depot_change(monkeypatch):
    """Le paquet du dépôt se récrit à chaque fabrique : le pont ouvert sur
    l'ancien se referme, et le suivant lit le nouveau."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    lances = _lancements(monkeypatch)
    pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
    signature = pont._signature_du_paquet()
    monkeypatch.setattr(pont, "_signature_du_paquet", lambda: (*signature, "récrit"))
    try:
        pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
        assert len(lances) == 2
    finally:
        pont.fermer()


def test_sous_la_garde_des_presomptions_le_portage_les_lit_decalees(monkeypatch):
    """La garde des présomptions (``PRESOMPTIONS_DECALEES``, ``tests/conftest.py`` ;
    action 135, levier 2) fait dire au vocabulaire du Python d'autres valeurs :
    le portage lit les mêmes dans son paquet, celui du dépôt comme celui d'une
    demande, pour qu'un test qui en écrit une en dur échoue d'un côté comme de
    l'autre. Le pont ouvert sans la garde se relance sous elle, et
    inversement."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from conftest import DECALAGES, PRESOMPTIONS_DECALEES

    paquet = (RACINE_PROJET / "moteur" / "donnees.json").read_bytes()
    du_paquet = {nom: json.loads(paquet)["presomptions"][nom]["valeur"] for nom in DECALAGES}
    assert du_paquet != DECALAGES
    appels = {nom: ("chronologie.valeur", nom) for nom in DECALAGES}
    pont.fermer()
    monkeypatch.delenv(PRESOMPTIONS_DECALEES, raising=False)
    try:
        assert pont.droit(appels) == (du_paquet, {})
        monkeypatch.setenv(PRESOMPTIONS_DECALEES, "1")
        assert pont.droit(appels) == (DECALAGES, {})
        assert pont.droit(appels, paquet=paquet) == (DECALAGES, {})
        monkeypatch.delenv(PRESOMPTIONS_DECALEES)
        assert pont.droit(appels) == (du_paquet, {})
    finally:
        pont.fermer()


# -- la grille du coût : ses carrières passent en données ------------------------

#: Des cases de la grille du coût où passe ce que les conventions de projection
#: du COR déforment en Python : l'entrée tardive dans le régime de l'État et
#: dans celui de la CNRACL, la part des primes que le décrochage du traitement
#: porte, l'inaptitude reconnue ; et, sans déformation, une carrière de mère de
#: deux enfants interrompue, déjà partie, et le salarié que l'âge légal de la
#: proposition reporte.
CASES_DU_COUT = (("fonctionnaire_sedentaire", 1990), ("fonctionnaire_actif", 1975),
                 ("militaire", 1980), ("smic_carriere_complete~inapte", 1960),
                 ("smic_carriere_complete~ex_invalide", 1965),
                 ("carriere_interrompue", 1950), ("salaire_moyen", 1970))


def _carriere_du_cout(simulateur, code: str, generation: int):
    return carriere_de_la_grille(
        simulateur, next(cas for cas in GRILLE_DU_COUT if cas.code == code), generation)


def _types(valeur):
    """La structure de ``valeur``, chaque nombre remplacé par son type : deux
    lectures égales dont un entier serait ici un flottant ne s'écrivent pas de
    même dans un fichier fabriqué."""
    if isinstance(valeur, dict):
        return {cle: _types(lu) for cle, lu in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return type(valeur)(_types(lu) for lu in valeur)
    return type(valeur).__name__


def test_une_carriere_passe_en_donnees_champ_par_champ():
    """La carrière d'un cas type, déformée sous les conventions du COR
    (``primes_projetees``, l'entrée tardive), passe au portage en données pour
    qu'il la simule (``pont.grille_du_cout``) : tous les champs de la carrière,
    chaque ligne entière et la chronologie dont elle est la vue, en JSON strict
    — un champ qui naîtrait sans passer le pont ferait échouer ce test."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    carriere = _carriere_du_cout(simulateur, "fonctionnaire_sedentaire", 1990)
    donnees = pont.carriere_en_donnees(carriere)
    assert set(donnees) == {champ.name for champ in fields(Carriere)}
    for ligne in donnees["lignes"]:
        assert set(ligne) == {champ.name for champ in fields(AnneeCarriere)}
    assert json.loads(json.dumps(donnees, allow_nan=False)) == donnees
    assert donnees["chronologie"] == carriere.chronologie
    # Déformée : entrée tard dans le régime de l'État, après des années de
    # contractuel, sa part des primes portée par le décrochage du traitement.
    assert {ligne["affiliation"] for ligne in donnees["lignes"]} == {
        "contractuel_public", "fonctionnaire_etat"}
    assert donnees["dates_entree"]["fonctionnaire_etat"] == [
        carriere.dates_entree["fonctionnaire_etat"].annee,
        carriere.dates_entree["fonctionnaire_etat"].mois]
    assert len({ligne["part_primes"] for ligne in donnees["lignes"]
                if ligne["affiliation"] == "fonctionnaire_etat"}) > 1


def _construire_temoins():
    """Le module de ``scripts/construire_temoins.py``."""
    import importlib.util

    chemin = RACINE_PROJET / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _echantillon(temoins: dict) -> list[str]:
    """Des témoins de chaque forme : la base, un relevé, un conjoint, un décès,
    l'étranger, un emploi après le départ."""
    formes = ("releve", "conjoint", "deces", "etranger1_pays", "emploi_retraite")
    return ["base"] + [next(nom for nom, temoin in temoins.items() if forme in temoin["requete"])
                       for forme in formes]


def _au_moteur_python(requetes: dict[str, dict]) -> dict[str, dict]:
    """Chaque requête, sous le nom de son témoin, simulée au moteur Python comme
    ``scripts/construire_temoins.py`` la simulait jusqu'au 31 octobre 2026 : la
    carrière que le portage bâtit de sa saisie, la seule
    (:func:`pont.carrieres_des_saisies`), simulée par le jumeau Python, un
    simulateur par jeu de paramètres ; son résultat écrit sous la table des
    types (:func:`pont.resultat_des_donnees`), et ses appels de ``liquider``,
    liquidations d'essai comprises."""
    fini = _construire_temoins()._fini
    carrieres, refusees = pont.carrieres_des_saisies(
        [{"cle": nom, "requete": requete} for nom, requete in requetes.items()])
    assert refusees == {}
    simulateurs = {}
    refaits = {}
    for nom, requete in requetes.items():
        parametres, carriere = carrieres[nom]
        if parametres not in simulateurs:
            simulateurs[parametres] = Simulateur(parametres)
        avant = liquidation.appels()
        resultat = simulateurs[parametres].simuler(carriere).dictionnaire()
        refaits[nom] = {"requete": requete,
                        "resultat": pont.resultat_des_donnees(fini(resultat)),
                        "appels_liquider": liquidation.appels() - avant}
    return refaits


def test_les_temoins_se_simulent_par_le_portage_sans_le_moteur_python(monkeypatch):
    """``scripts/construire_temoins.py`` fait simuler ses témoins au portage
    (:func:`pont.simulations`), le moteur qui fait foi (note de décision
    0005) : le moteur Python, qu'on empêche ici de simuler, n'y entre pas, et
    des témoins de chaque forme reviennent tels que le fichier les porte, à
    l'octet."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    module = _construire_temoins()
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    monkeypatch.setattr(module, "_cas", lambda: [{"nom": nom, "requete": temoins[nom]["requete"]}
                                                  for nom in noms])

    def interdit(*_, **__):
        raise AssertionError("le moteur Python simule un témoin")

    monkeypatch.setattr(Simulateur, "simuler", interdit)
    simulations = module._simulations()
    assert list(simulations) == noms
    for nom in noms:
        assert ecarts_d_ecriture(simulations[nom], temoins[nom]) == [], nom


def test_le_moteur_python_refait_des_temoins_de_chaque_forme():
    """Le moteur Python garde ses jumeaux jusqu'à leur retrait (action 161), et
    les témoins, que le portage calcule, le confrontent : sur des témoins de
    chaque forme, la carrière que le portage bâtit, simulée au moteur Python
    et écrite sous la table des types, redonne ce que porte le fichier, appels
    de ``liquider`` compris (:data:`TOLERANCE_DU_MOTEUR_PYTHON`)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    refaits = _au_moteur_python({nom: temoins[nom]["requete"] for nom in noms})
    for nom in noms:
        assert ecarts_d_ecriture(refaits[nom], temoins[nom],
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], nom


def _comme_node(valeur):
    """Une valeur telle que node l'écrit en JSON : un flottant entier sans sa
    décimale, « 2 » pour 2.0."""
    if isinstance(valeur, float) and valeur.is_integer():
        return int(valeur)
    if isinstance(valeur, dict):
        return {cle: _comme_node(element) for cle, element in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_comme_node(element) for element in valeur]
    return valeur


def _temoins_de_simulations() -> tuple[str, dict]:
    """Le texte de ``tests/temoins/simulations.json``, et ce qu'il porte."""
    texte = (RACINE_PROJET / "tests" / "temoins" / "simulations.json").read_text(encoding="utf-8")
    return texte, json.loads(texte)


def test_la_table_des_types_relit_chaque_temoin_ecrit_comme_node_l_ecrirait():
    """Node n'écrit qu'un type de nombre, « 2 » pour 2.0 : le pont relit le
    résultat d'une simulation que le portage a écrit sous la table des types
    qu'il déclare champ par champ (:func:`pont.resultat_des_donnees`). Les
    témoins s'écrivent sous la même table : le zéro d'un champ flottant
    « 0.0 », même quand le moteur Python le rend entier, d'une somme vide
    (décision du propriétaire, 31 octobre 2026). Chaque témoin, écrit comme
    node l'écrirait, en revient donc à l'octet. Un champ numérique qui naît
    dans le résultat sans son type déclaré fait échouer ce test, et la
    relecture avec lui."""
    _, temoins = _temoins_de_simulations()
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(
                  pont.resultat_des_donnees(_comme_node(temoin["resultat"])),
                  temoin["resultat"])]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_la_table_des_types_refuse_le_nombre_qu_elle_ne_declare_pas():
    """Un nombre sous un champ que la table ne déclare pas arrête la relecture,
    au lieu d'en deviner le type, et un entier qui n'en est pas un aussi. Un
    nombre non fini, que node écrit « null » comme ``_fini`` l'écrit, reste
    ``None`` ; un texte et un booléen restent ce qu'ils sont. Les clés d'un
    dictionnaire déclaré — les régimes du capital, les origines des années
    d'une part employeur — sont libres. Le zéro d'un champ flottant s'écrit
    « 0.0 », quel que soit le chemin du calcul qui l'a rendu."""
    with pytest.raises(ValueError, match="assure.nouveau"):
        pont.resultat_des_donnees({"assure": {"nouveau": 1}})
    with pytest.raises(TypeError, match="entier"):
        pont.resultat_des_donnees({"assure": {"annee_naissance": 1970.5}})
    relu = pont.resultat_des_donnees({
        "assure": {"annee_naissance": 1970, "age_liquidation": 64, "sexe": "F",
                   "affiliations": ["salarie_prive_non_cadre"]},
        "scenarios": {
            "actuel": {"pension_annuelle": 12000, "pension_hors_repartition": 0,
                       "taux_remplacement": None, "liquidation_ouverte": True,
                       "droits_apres_depart": {"montant": 0, "pensions": [
                           {"montant": 0, "trimestres": 4}]}},
            "notionnel_liberal": {
                "capital_par_regime": {"un_regime_de_plus": 3},
                "annees_part_employeur": {"appelee": 2},
                "capitalisation": {"interets": 0, "versements": 0, "annees_cotisees": 0}},
            "notionnel_retroactif": {"capitalisation": {"interets": 12}}},
        "aujourd_hui": {"actuel": {"majoration_enfants": 0, "pension_hors_repartition": 0}},
    })
    assert json.dumps(relu, sort_keys=True) == json.dumps({
        "assure": {"annee_naissance": 1970, "age_liquidation": 64.0, "sexe": "F",
                   "affiliations": ["salarie_prive_non_cadre"]},
        "scenarios": {
            "actuel": {"pension_annuelle": 12000.0, "pension_hors_repartition": 0.0,
                       "taux_remplacement": None, "liquidation_ouverte": True,
                       "droits_apres_depart": {"montant": 0.0, "pensions": [
                           {"montant": 0.0, "trimestres": 4}]}},
            "notionnel_liberal": {
                "capital_par_regime": {"un_regime_de_plus": 3.0},
                "annees_part_employeur": {"appelee": 2},
                "capitalisation": {"interets": 0.0, "versements": 0.0, "annees_cotisees": 0}},
            "notionnel_retroactif": {"capitalisation": {"interets": 12.0}}},
        "aujourd_hui": {"actuel": {"majoration_enfants": 0.0, "pension_hors_repartition": 0.0}},
    }, sort_keys=True)


def test_le_pont_simule_des_temoins_comme_le_portage_les_simule():
    """Les témoins simulés par le portage (:func:`pont.simulations`), comme
    ``tests/js/moteur.test.js`` les simule : sur des témoins de chaque forme —
    un relevé, un conjoint, un décès, l'étranger, un emploi après le départ —,
    les appels de ``liquider`` que porte le fichier, et son résultat, relu par
    la table des types, à l'octet."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    resultats, echecs = pont.simulations([{"cle": nom, "requete": temoins[nom]["requete"]}
                                          for nom in noms])
    assert (list(resultats), echecs) == (noms, {})
    for nom in noms:
        assert set(resultats[nom]) == {"resultat", "appels_liquider"}, nom
        assert resultats[nom]["appels_liquider"] == temoins[nom]["appels_liquider"], nom
        assert ecarts_d_ecriture(resultats[nom]["resultat"], temoins[nom]["resultat"]) == [], nom


def test_le_portage_relu_par_la_table_redonne_les_temoins_a_l_octet():
    """Tous les témoins de simulations, simulés par le portage
    (:func:`pont.simulations`), relus par la table des types et écrits comme
    ``scripts/construire_temoins.py`` les écrit : le fichier revient à l'octet,
    appels de ``liquider`` compris. C'est la preuve que les témoins peuvent se
    simuler par le portage sans qu'un octet change (action 161, étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    texte, temoins = _temoins_de_simulations()
    resultats, echecs = pont.simulations([{"cle": nom, "requete": temoin["requete"]}
                                          for nom, temoin in temoins.items()])
    assert echecs == {}
    relus = {nom: {"requete": temoin["requete"], **resultats[nom]}
             for nom, temoin in temoins.items()}
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(relus[nom], temoin)]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    assert json.dumps(relus, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == texte


def test_le_moteur_python_refait_chaque_temoin():
    """Tous les témoins, simulés au moteur Python sur la carrière que le portage
    bâtit, écrits sous la table des types : le fichier, que le portage calcule,
    revient à l'octet sous Linux x86_64, appels de ``liquider`` compris
    (:data:`TOLERANCE_DU_MOTEUR_PYTHON`). C'est la concordance des deux
    moteurs, que ``tests/js/moteur.test.js`` tenait quand les témoins se
    simulaient au Python : une règle portée d'un seul côté, ou dans un autre
    ordre d'addition, la rougit (note de décision 0005)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    texte, temoins = _temoins_de_simulations()
    refaits = _au_moteur_python({nom: temoin["requete"] for nom, temoin in temoins.items()})
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(refaits[nom], temoin,
                                             tolerance=TOLERANCE_DU_MOTEUR_PYTHON)]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    if not TOLERANCE_DU_MOTEUR_PYTHON:
        assert json.dumps(refaits, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == texte


def test_le_python_relit_une_carriere_ecrite_par_node_sous_ses_types():
    """Ce que node écrit, le Python le relit sous ses types : un flottant entier
    redevient flottant, dans les champs comme dans les nombres libres de la
    chronologie qu'il écrit en flottants, quand les trimestres d'un relevé
    gardent le type que JSON leur rend. Un champ qu'il ne connaît pas, ou un
    entier qui n'en est pas un, arrête la relecture au lieu de se perdre."""
    simulateur = Simulateur(Parametres())
    carriere = simulateur.carriere_simple(annee_naissance=1970, sexe="F",
                                          affiliation="salarie_prive_non_cadre",
                                          age_debut=22.0, age_liquidation=64.0)
    ecrite = pont.carriere_en_donnees(carriere)
    relue = pont.carriere_des_donnees(_comme_node(ecrite))
    assert json.dumps(pont.carriere_en_donnees(relue)) == json.dumps(ecrite)
    with pytest.raises(ValueError, match="champs"):
        pont.carriere_des_donnees({**_comme_node(ecrite), "nouveau": 1})
    premiere, *suivantes = _comme_node(ecrite)["lignes"]
    with pytest.raises(ValueError, match="AnneeCarriere"):
        pont.carriere_des_donnees({**_comme_node(ecrite),
                                   "lignes": [{**premiere, "nouveau": 1}, *suivantes]})
    with pytest.raises(TypeError, match="entier"):
        pont.carriere_des_donnees({**_comme_node(ecrite), "annee_naissance": 1970.5})
    parametres = pont.parametres_des_donnees(_comme_node(pont.parametres_en_donnees(Parametres())))
    assert (json.dumps(pont.parametres_en_donnees(parametres))
            == json.dumps(pont.parametres_en_donnees(Parametres())))
    chronologie = pont.carriere_des_donnees({**_comme_node(ecrite), "chronologie": {
        "schema_version": 1, "liens": [], "faits": [
            {"attributs": {"age": 64, "trimestres": 4, "taux": 50}, "montant": {"mensuel": 100}},
            {"attributs": {"trimestres": 2.5, "revenu": 1500}}]}}).chronologie
    assert [json.dumps(fait) for fait in chronologie["faits"]] == [
        '{"attributs": {"age": 64.0, "trimestres": 4, "taux": 50}, "montant": {"mensuel": 100.0}}',
        '{"attributs": {"trimestres": 2.5, "revenu": 1500.0}}']


def test_les_parametres_passent_en_donnees_sous_les_noms_du_portage():
    """Tous les paramètres du Python, sauf la racine des données, dont le
    paquet tient lieu ; ceux de référence sont, valeur pour valeur, ceux du
    portage (``PARAMETRES_DEFAUT`` de ``moteur/js/config.js``)."""
    donnees = pont.parametres_en_donnees(Parametres())
    assert set(donnees) == {champ.name for champ in fields(Parametres)} - {"racine_donnees"}
    assert json.loads(json.dumps(donnees, allow_nan=False)) == donnees
    projection = pont.parametres_en_donnees(Simulateur(Parametres()).pour_la_projection().parametres)
    assert (projection["conventions_cor"],
            projection["minimum_vieillesse_dans_le_scenario_actuel"]) == (True, False)
    if shutil.which("node") is None:
        pytest.skip("node absent : les paramètres du portage ne se lisent pas ici")
    lus = subprocess.run(
        ["node", "--input-type=module", "-e",
         'const m = await import("./moteur/js/config.js");'
         "process.stdout.write(JSON.stringify(m.PARAMETRES_DEFAUT));"],
        cwd=RACINE_PROJET, capture_output=True, check=True).stdout
    assert donnees == json.loads(lus)


def test_la_grille_du_cout_passe_le_pont_au_bit_pres_du_moteur_python():
    """Ce que le coût lit de chaque case de sa grille — la pension de chaque
    système en euros constants ; la proposition sur la carrière où elle se
    calcule, sa garantie, son compte et son pilier ; le report de l'âge légal ;
    ce que le droit en vigueur prélève, année par année ; la part de chaque
    régime ; la population de sa mortalité — et la proposition seule sur les
    carrières qu'il en dérive : le portage le rend, sur des carrières passées
    en données et sous les paramètres de la projection, au bit près de ce que
    le moteur Python calcule (``cout._simulations_en_python``), chaque nombre
    sous son type."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    simulateur = Simulateur(Parametres()).pour_la_projection()
    macro = simulateur.macro
    age_legal = simulateur.parametres.age_legal_liberal
    cas = []
    for code, generation in CASES_DU_COUT:
        carriere = _carriere_du_cout(simulateur, code, generation)
        cas.append({"cle": f"{code}|{generation}", "carriere": carriere, "propositions": {
            "sans_report": carriere,
            "reportee": carriere.prolongee(age_legal, macro),
            "attente": carriere.prolongee(age_legal, macro, attente_travaillee=False)}})
    scenarios = [cle for cle, _ in cout.SCENARIOS]
    attendus, refus = cout._simulations_en_python(simulateur, cas, scenarios)
    assert not refus
    resultats, echecs = pont.grille_du_cout(cas, scenarios, simulateur.parametres,
                                            pont.paquet_des_donnees())
    assert not echecs
    assert _types(resultats) == _types(attendus)
    assert resultats == attendus
    # Ce que les cases font traverser : un report, un départ déjà pris, un
    # pilier, une population de mortalité, une pension de deux régimes.
    lus = resultats.values()
    assert {lu["depart_reporte"] for lu in lus} == {True, False}
    assert any(lu["liberal"]["pilier"] is not None for lu in lus)
    assert any(lu["liberal"]["pilier"] is None for lu in lus)
    assert any(lu["population"] is not None for lu in lus)
    assert any(len(lu["pensions_par_regime"]) > 1 for lu in lus)


def test_les_parametres_du_cout_passent_le_pont():
    """Une variante de la projection — la bascule en 2030 — se simule sous ses
    paramètres, non sous ceux de référence : le pilier ne s'ouvre qu'à elle."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    variante = replace(Parametres(), annee_bascule=2030)
    scenarios = ["actuel", "notionnel_liberal"]
    lus = {}
    for parametres in (Parametres(), variante):
        simulateur = Simulateur(parametres).pour_la_projection()
        carriere = _carriere_du_cout(simulateur, "salaire_moyen", 1975)
        cas = [{"cle": "salaire_moyen|1975", "carriere": carriere, "propositions": {}}]
        attendus, _ = cout._simulations_en_python(simulateur, cas, scenarios)
        resultats, _ = pont.grille_du_cout(cas, scenarios, simulateur.parametres,
                                           pont.paquet_des_donnees())
        assert resultats == attendus
        lus[parametres.annee_bascule] = resultats["salaire_moyen|1975"]
    assert min(lus[2026]["liberal"]["pilier"]["annees"]) == 2026
    assert min(lus[2030]["liberal"]["pilier"]["annees"]) == 2030
    assert lus[2030]["pensions"]["notionnel_liberal"] != lus[2026]["pensions"]["notionnel_liberal"]


# -- le coût branché sur le pont --------------------------------------------------

#: Une grille d'essai où passe ce que le coût lit en profondeur : l'entrée
#: tardive et les primes projetées, l'inaptitude, le report de l'âge légal, la
#: bascule qui passe entre les cohortes d'une génération.
GRILLE_D_ESSAI = tuple(cas for cas in GRILLE_DU_COUT if cas.code in (
    "fonctionnaire_sedentaire", "salaire_moyen", "smic_carriere_complete~inapte"))


def test_le_cout_simule_sa_grille_par_le_portage_sans_repli(memoire_isolee, monkeypatch):
    """Le modèle intact, sur les données du dépôt, la grille du coût se simule
    par le portage (action 161, étape 5) : sans node, elle s'arrête, sans
    repli sur le moteur Python."""
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1970,))
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")


def test_le_cout_date_et_bat_sa_grille_par_le_portage_sans_les_jumeaux(memoire_isolee,
                                                                        monkeypatch):
    """Le modèle intact, sur les données du dépôt, le coût fait dater et bâtir
    sa grille au portage, comme il la fait simuler (action 161, étape 6) : le
    pilote Python, l'ouverture du droit qu'il interroge, les constructeurs de
    carrières, la projection des primes et le moteur Python, qu'on empêche ici
    de calculer, n'y entrent pas — ni dans ses cohortes nées toute l'année.
    Couple pour couple, la grille est celle que le Python date, bâtit et simule
    sous un modèle modifié."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import castypes, cout, memoire, pilote
    from retraite_notionnelle.droit import ouvrir

    monkeypatch.setattr(cout, "generations", lambda: (1965, 2000))
    simulateur = Simulateur(Parametres())
    with memoire.modele_modifie():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
        nees_en_python = cout._nees_toute_l_annee(simulateur, GRILLE_D_ESSAI, en_python[0],
                                                  "droit")

    def interdit(*_, **__):
        raise AssertionError("un jumeau Python date, bâtit ou simule la grille du coût")

    for objet, nom in ((pilote, "age_de_depart"), (pilote, "point_fixe"), (pilote, "descendre"),
                       (ouvrir, "age_ouverture_droit"), (ouvrir, "age_taux_plein_droit"),
                       (ouvrir, "age_annulation_droit"), (Simulateur, "carriere_simple"),
                       (Simulateur, "carriere_parcours"), (Simulateur, "simuler"),
                       (Simulateur, "proposition"), (Carriere, "prolongee"),
                       (castypes, "primes_projetees")):
        monkeypatch.setattr(objet, nom, interdit)
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert par_le_portage == en_python
    assert _types([vars(p) for p in par_le_portage[0]]) == _types([vars(p) for p in en_python[0]])
    assert cout._nees_toute_l_annee(simulateur, GRILLE_D_ESSAI, par_le_portage[0],
                                    "droit") == nees_en_python
    # Ce que la grille d'essai fait traverser : un report de l'âge légal, la
    # bascule entre les cohortes d'une génération.
    assert any(p.propre.annee_liquidation > p.annee_liquidation for p in par_le_portage[0])
    assert any(p.autre is not None for p in par_le_portage[0])


def test_sous_un_modele_modifie_le_cout_simule_sa_grille_en_python(memoire_isolee, monkeypatch):
    """Un contexte qui remplace une fonction du moteur Python
    (``memoire.modele_modifie``, ``scripts/solde_fusion.py``) ne la remplace pas
    dans le portage : la grille se simule alors par le moteur Python, le seul
    qui la voie. Le modèle laissé tel quel, elle rend ce que le portage rend,
    couple pour couple, chaque nombre au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout, memoire

    monkeypatch.setattr(cout, "generations", lambda: (1950, 1965, 1975, 2000))
    simulateur = Simulateur(Parametres())
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with memoire.modele_modifie():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert en_python == par_le_portage
    assert _types([vars(p) for p in en_python[0]]) == _types([vars(p) for p in par_le_portage[0]])
    pensionnes = par_le_portage[0]
    assert len(pensionnes) == len(GRILLE_D_ESSAI) * 4
    assert any(p.autre is not None for p in pensionnes)
    assert any(p.propre.annee_liquidation > p.annee_liquidation for p in pensionnes)


def test_sur_des_donnees_d_ailleurs_le_cout_simule_sa_grille_en_python(tmp_path):
    """Le portage calcule sur le paquet des données du dépôt
    (``pont.paquet_des_donnees``) : des données d'ailleurs — une copie que
    l'on a retouchée (``scripts/facteurs_depense.py --sans-suspension``) — se
    simulent par le moteur Python, comme un modèle qu'un contexte modifie."""
    from retraite_notionnelle import cout, memoire

    assert pont.par_le_portage(Parametres())
    assert not pont.par_le_portage(replace(Parametres(), racine_donnees=tmp_path))
    with memoire.modele_modifie():
        assert not pont.par_le_portage(Parametres())


def test_le_paquet_du_jour_suit_les_sources(monkeypatch, tmp_path):
    """Le paquet du jour se bâtit une fois par état des sources de la mémoire
    des calculs, et non une fois par processus : une donnée retouchée pendant
    qu'un processus calcule entre dans le paquet de son calcul suivant, et la
    mémoire ne garde pas, sous l'empreinte des données nouvelles, une grille
    simulée sur le paquet des anciennes."""
    from retraite_notionnelle import memoire

    depot = tmp_path / "depot"
    (depot / "data").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(depot)], check=True)
    donnee = depot / "data" / "taux.csv"
    donnee.write_text("annee,taux\n2026,1\n", encoding="utf-8")
    monkeypatch.setattr(memoire, "RACINE_PROJET", depot)
    reel, batis = subprocess.run, []

    def batir(commande, *arguments, **options):
        if commande[0] != sys.executable:
            return reel(commande, *arguments, **options)
        batis.append(commande)
        return subprocess.CompletedProcess(commande, 0, f"paquet {len(batis)}".encode(), b"")

    monkeypatch.setattr(subprocess, "run", batir)
    assert pont.paquet_des_donnees() == b"paquet 1"
    assert pont.paquet_des_donnees() == b"paquet 1"
    donnee.write_text("annee,taux\n2026,1.5\n", encoding="utf-8")
    assert pont.paquet_des_donnees() == b"paquet 2"
