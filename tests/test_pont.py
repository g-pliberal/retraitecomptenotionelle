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
conventions de projection du COR, dont les carrières se déforment en Python :
elles passent au portage en données. Ici : le pont rend au bit près ce que le
moteur Python simule, chaque nombre sous le type que le Python lui donne ; et,
sans node, il s'arrête, sans repli sur le moteur Python.
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
    CAS_TYPES, GRILLE_DU_COUT, carriere_de_la_grille, cases_de_la_grille)
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
    """Sous les conventions du COR, la carrière d'un cas type se déforme en
    Python (``primes_projetees``, l'entrée tardive) ; le portage n'en garde pas
    de copie : il la lit en données. Tous les champs de la carrière, chaque
    ligne entière et la chronologie dont elle est la vue, en JSON strict — un
    champ qui naîtrait sans passer le pont ferait échouer ce test."""
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

    assert cout._par_le_portage(Parametres())
    assert not cout._par_le_portage(replace(Parametres(), racine_donnees=tmp_path))
    with memoire.modele_modifie():
        assert not cout._par_le_portage(Parametres())


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
