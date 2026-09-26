"""La liquidation, le journal, l'échéancier et le pilote (docs/architecture.md,
§ 7.3 à 7.7 ; annexe C.6 à C.8).

Chaque étape se vérifie seule (§ 7.1) et écrit une donnée que son schéma
décrit (``data/reference/etapes/``) : ouvrir le droit, liquider chaque régime,
compléter tous régimes, foyer et net, faire vivre. La liquidation suit le
contrat C.6, l'événement le C.7, chaque entrée du journal le C.8.
``liquider`` est une fonction pure : elle ne lit que sa demande, son état et
son contexte, et ce qu'elle mesure par une liquidation d'essai, elle le dit.
Le journal ne s'écrit qu'en ajoutant. Le pilote date un départ sans rien
liquider. Les deux moteurs écrivent les mêmes données, et chaque témoin
déclare ses appels de ``liquider``, qu'aucun ne dépasse (§ 7.8).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle import echeancier as _echeancier
from retraite_notionnelle import journal as _journal
from retraite_notionnelle import pilote
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.droit import completer, foyer, liquidation, liquider, ouvrir, releve
from retraite_notionnelle.noyau import contrats
from retraite_notionnelle.revalorisation import actuel_aujourd_hui, faire_vivre
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, metiers: list[Metier], naissance: int = 1962,
              liquidation: float = 64, sexe: str = "H", **kwargs) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, **kwargs)


def _etape(etape: str) -> contrats.Validateur:
    return contrats.Validateur(etape, contrats.ETAPES)


def _erreurs(constats) -> list[str]:
    return [str(c) for c in constats if c.genre == "erreur"]


def _contexte(simulateur: Simulateur, *neutralisations: str) -> liquidation.Contexte:
    return liquidation.Contexte(simulateur.scenario_actuel, frozenset(neutralisations))


def _liquider(simulateur: Simulateur, carriere: Carriere, *neutralisations: str,
              journal=None) -> liquidation.Liquidation:
    return liquidation.liquider(liquidation.demande_de_depart(carriere),
                                liquidation.Etat(carriere, journal),
                                _contexte(simulateur, *neutralisations))


CARRIERES = {
    "salarie": dict(metiers=[Metier("salarie_prive_non_cadre", 22.0)]),
    # Deux enfants, et deux années d'éducation qui ouvrent l'AVPF : la
    # cascade mesure les trimestres des enfants, puis l'AVPF.
    "mere_au_foyer": dict(metiers=[Metier("salarie_prive_non_cadre", 21.0)], sexe="F",
                          nombre_enfants=2, naissance=1970,
                          interruptions={1998: "education_enfant", 1999: "education_enfant"}),
    "fonctionnaire": dict(metiers=[Metier("fonctionnaire_etat", 23.0)], part_primes=0.2),
    "artisan_puis_salarie": dict(metiers=[Metier("artisan", 20.0),
                                          Metier("salarie_prive_non_cadre", 40.0)], naissance=1960),
    # Les points gratuits de la RCO agricole : la cascade les mesure aussi.
    "chef_d_exploitation": dict(metiers=[Metier("exploitant_agricole", 20.0)], naissance=1955),
    # Parti en 2005 : l'échéance de l'année courante fait vivre sa pension.
    "retraite": dict(metiers=[Metier("salarie_prive_non_cadre", 20.0)], naissance=1945,
                     liquidation=60),
}


# -- chaque étape, seule -------------------------------------------------------

@pytest.mark.parametrize("nom", sorted(CARRIERES))
def test_chaque_etape_de_la_liquidation_suit_son_schema(simulateur, nom):
    """Ouvrir le droit, liquider chaque régime, compléter tous régimes, foyer
    et net : chaque étape, appelée seule sur le relevé, écrit une donnée que
    son schéma accepte sans une erreur."""
    actuel = simulateur.scenario_actuel
    carriere = _carriere(simulateur, **CARRIERES[nom])
    releve_ = releve.construire(actuel, carriere)
    contexte = _contexte(simulateur)
    ouverture = ouvrir.ouvrir(actuel, releve_)
    pensions = liquider.liquider_chaque_regime(actuel, releve_, ouverture, contexte)
    complements = completer.completer(actuel, releve_, ouverture, pensions, contexte)
    foyer_ = foyer.foyer_et_net(actuel, carriere.personne, ouverture.donnees()["date_effet"],
                                carriere.annee_liquidation, complements.total, True, contexte)
    for etape, objet, donnees in (
            ("ouvrir_le_droit", "ouverture", ouverture.donnees()),
            ("liquider_chaque_regime", "pensions", pensions.donnees()),
            ("completer_tous_regimes", "complements", complements.donnees()),
            ("foyer_et_net", "foyer", foyer_.donnees())):
        assert _erreurs(_etape(etape).valider(donnees, objet)) == [], etape
    assert pensions.donnees()["regimes"], "au moins une pension de régime"
    # Les pensions que l'étape « compléter » reçoit sont celles que l'étape
    # « liquider » a écrites, dans le même ordre.
    assert [p.regime for p in complements.regimes] == [p.regime for p in pensions.regimes]


@pytest.mark.parametrize("nom", sorted(CARRIERES))
def test_la_liquidation_suit_le_contrat_c6(simulateur, nom):
    """Ses composantes — une pension par régime, puis la majoration pour
    enfants —, les lignes du relevé qu'elle a lues, ses mesures : le contrat
    C.6 les accepte sans une erreur. Ce qui manque encore — les régimes que la
    demande vise — est un manque, que le tableau de bord compte."""
    carriere = _carriere(simulateur, **CARRIERES[nom])
    liquidee = _liquider(simulateur, carriere)
    donnees = liquidee.donnees()
    constats = contrats.Validateur("liquidation").valider(donnees, "liquidation")
    assert _erreurs(constats) == []
    manques = {c.chemin.rsplit(".", 1)[-1] for c in constats if c.genre == "manque"}
    assert manques <= {"regimes", "version", "texte", "fiche", "fiabilite"}, manques
    identifiants = [c["id"] for c in donnees["composantes"]]
    assert len(set(identifiants)) == len(identifiants)
    lues = {ligne["id"] for ligne in liquidee.releve.lignes()}
    assert set(donnees["lignes_consommees"]) == lues


def test_liquider_est_une_fonction_pure(simulateur):
    """La même demande, le même état, le même contexte : la même liquidation.
    Elle ne touche ni la carrière ni le journal qu'elle lit."""
    carriere = _carriere(simulateur, **CARRIERES["mere_au_foyer"])
    journal = _journal.Journal()
    avant = carriere.lignes
    un = _liquider(simulateur, carriere, journal=journal)
    deux = _liquider(simulateur, carriere, journal=journal)
    assert un.donnees() == deux.donnees()
    assert un.total == deux.total and un.fiabilite == deux.fiabilite
    assert carriere.lignes is avant and len(journal) == 0


def test_les_drapeaux_de_calculer_sont_des_neutralisations(simulateur):
    """Chaque drapeau de ``calculer`` est une neutralisation du contexte, une
    couche d'un seul calcul (§ 4.8 et 6.4) : liquider sous la neutralisation
    donne ce que la façade donne sous le drapeau."""
    actuel = simulateur.scenario_actuel
    carriere = _carriere(simulateur, **CARRIERES["mere_au_foyer"])
    for drapeaux, neutralisations in (
            # Les points gratuits suivent les avantages non contributifs, faute
            # d'un drapeau qui les dise : voir ``calculer``.
            (dict(avantages_non_contributifs=False),
             ("avantages_non_contributifs", "points_gratuits")),
            (dict(avantages_non_contributifs=False, points_gratuits=True),
             ("avantages_non_contributifs",)),
            (dict(avpf=False), ("avpf",)),
            (dict(ignorer_penalite_age=True), ("decote_surcote",)),
            (dict(liquider_successions=False), ("successions",))):
        facade = actuel.calculer(carriere, **drapeaux)
        liquidee = _liquider(simulateur, carriere, *neutralisations)
        assert liquidee.contexte.donnees()["neutralisations"] == sorted(neutralisations)
        if "avantages_non_contributifs" in neutralisations:
            # Sans avantages non contributifs, l'ASPA non plus : le total est
            # celui de la liquidation.
            assert facade.pension_annuelle == max(0.0, liquidee.total - liquidee.hors_repartition)
        assert facade.total_contributif == liquidee.total_contributif, drapeaux


def test_le_contexte_refuse_une_neutralisation_que_le_vocabulaire_ignore(simulateur):
    with pytest.raises(ValueError, match="neutralisations inconnues"):
        _contexte(simulateur, "age_legal")
    assert liquidation.NEUTRALISATIONS == {
        "avantages_non_contributifs", "avpf", "points_gratuits", "decote_surcote",
        "successions"}


def test_la_cascade_mesure_chaque_avantage_par_une_liquidation_d_essai(simulateur):
    """Les trimestres des enfants, puis l'AVPF : chacun se mesure par une
    liquidation d'essai, sous la neutralisation qui le retire, et la
    liquidation dit ce qu'elle a mesuré. Chaque essai est un appel compté,
    même quand il ne trouve rien : ici, l'essai sans l'AVPF ne déplace pas la
    pension, et seul ce qui la déplace devient une mesure."""
    carriere = _carriere(simulateur, **CARRIERES["mere_au_foyer"])
    assert any(ligne.revenu_avpf > 0 for ligne in carriere.lignes)
    avant = liquidation.appels()
    liquidee = _liquider(simulateur, carriere)
    # Le départ, puis un essai sans les trimestres des enfants, un sans l'AVPF.
    assert liquidation.appels() - avant == 3
    assert [(m.code, m.neutralisation) for m in liquidee.mesures] == [
        ("majoration_duree_assurance", "avantages_non_contributifs")]
    montants = {a.code: a.montant for a in liquidee.avantages}
    assert liquidee.mesures[0].montant == montants["majoration_duree_assurance"] > 0
    # Sous la neutralisation, plus rien à mesurer : un seul appel.
    avant = liquidation.appels()
    sans = _liquider(simulateur, carriere, "avantages_non_contributifs")
    assert liquidation.appels() - avant == 1 and sans.mesures == ()


def test_les_points_gratuits_se_mesurent_apres_l_avpf(simulateur):
    carriere = _carriere(simulateur, **CARRIERES["chef_d_exploitation"])
    liquidee = _liquider(simulateur, carriere)
    assert [m.code for m in liquidee.mesures] == ["points_gratuits_rco"]
    assert liquidee.mesures[0].neutralisation == "points_gratuits"


def test_une_demande_fictive_se_liquide_et_le_dit(simulateur):
    """La valorisation des droits acquis du scénario prospectif est une
    liquidation fictive : calculée, jamais servie (§ 7.3)."""
    carriere = _carriere(simulateur, **CARRIERES["salarie"])
    demande = liquidation.demande_de_depart(carriere, nature="fictive")
    liquidee = liquidation.liquider(demande, liquidation.Etat(carriere), _contexte(
        simulateur, "avantages_non_contributifs", "points_gratuits", "decote_surcote"))
    assert liquidee.donnees()["demande"]["nature"] == "fictive"
    facade = simulateur.scenario_actuel.calculer(
        carriere, ignorer_penalite_age=True, avantages_non_contributifs=False,
        nature="fictive")
    assert facade.pension_annuelle == max(0.0, liquidee.total - liquidee.hors_repartition)


# -- faire vivre, foyer et net ---------------------------------------------------

def test_faire_vivre_suit_son_schema_et_ne_liquide_rien(simulateur):
    """« Faire vivre » mène les pensions à l'échéance sans relancer la
    liquidation, et « foyer et net » y revoit l'ASPA : chacune écrit ce que
    son schéma décrit."""
    carriere = _carriere(simulateur, **CARRIERES["retraite"])
    au_depart = simulateur.scenario_actuel.calculer(carriere)
    annee = simulateur.parametres.annee_courante
    avant = liquidation.appels()
    vivante = faire_vivre(simulateur, carriere, au_depart, annee)
    assert liquidation.appels() == avant
    assert _erreurs(_etape("faire_vivre").valider(vivante.donnees(), "revalorisation")) == []
    assert all(r.coefficient > 1.0 for r in vivante.regimes)
    servi = actuel_aujourd_hui(simulateur, carriere, au_depart, annee)
    assert servi.regimes == vivante.regimes


# -- le journal ----------------------------------------------------------------

def _entree(ident: str, date: str, remplace: str | None = None,
            fin: str | None = None) -> _journal.Entree:
    return _journal.Entree(ident, "depart_assure", date, date, fin, "composante",
                           {"id": ident, "montant": {"annuel": 1.0, "monnaie": "EUR"}},
                           remplace=remplace)


def test_le_journal_ne_s_ecrit_qu_en_ajoutant():
    journal = _journal.Journal()
    journal.inscrire(_entree("pension_regime_general", "2020-01-01"))
    with pytest.raises(ValueError, match="déjà inscrite"):
        journal.inscrire(_entree("pension_regime_general", "2021-01-01"))
    with pytest.raises(ValueError, match="entrée inconnue"):
        journal.inscrire(_entree("pension_agirc_arrco_2021", "2021-01-01",
                                 remplace="pension_agirc_arrco"))
    assert len(journal) == 1


def test_le_journal_sert_la_derniere_entree_de_chaque_lignee():
    """Une composante et ses révisions forment une lignée : pour une période,
    le journal sert la dernière entrée dont l'effet la couvre ; à une date,
    il rend tout ce qui était inscrit ce jour-là."""
    journal = _journal.Journal()
    journal.inscrire(_entree("pension_regime_general", "2020-01-01"))
    journal.inscrire(_entree("pension_agirc_arrco", "2020-01-01", fin="2030-01-01"))
    journal.inscrire(_entree("pension_regime_general_2024", "2024-12-31",
                             remplace="pension_regime_general"))
    journal.inscrire(_entree("pension_regime_general_2025", "2025-12-31",
                             remplace="pension_regime_general_2024"))
    servi = {e.id for e in journal.servi("2026-01-01", "2026-02-01")}
    assert servi == {"pension_regime_general_2025", "pension_agirc_arrco"}
    assert {e.id for e in journal.servi("2021-01-01", "2021-02-01")} == {
        "pension_regime_general", "pension_agirc_arrco"}
    # Une période qui passe la fin d'une entrée n'est pas couverte par elle.
    assert {e.id for e in journal.servi("2029-01-01", "2031-01-01")} == {
        "pension_regime_general_2025"}
    assert {e.id for e in journal.etat_au("2024-12-31")} == {
        "pension_regime_general", "pension_agirc_arrco", "pension_regime_general_2024"}
    for entree in journal:
        assert _erreurs(contrats.Validateur("entree_journal").valider(
            entree.donnees(), "entree")) == []


# -- l'échéancier ----------------------------------------------------------------

def test_l_echeancier_inscrit_le_depart_puis_l_echeance(simulateur):
    """Parti en 2005 : le départ appelle la liquidation, puis l'ASPA du
    jour ; l'échéance de l'année courante fait vivre les pensions et revoit
    l'ASPA. Chaque composante revalorisée remplace celle du départ, et le
    journal sert, pour l'année courante, les revalorisées."""
    carriere = _carriere(simulateur, **CARRIERES["retraite"])
    annee = simulateur.parametres.annee_courante
    echeancier = _echeancier.Echeancier(simulateur)
    avant = liquidation.appels()
    journal = echeancier.parcourir(carriere, echeance=annee)
    assert liquidation.appels() - avant == 1, "une liquidation : le départ"
    sortes = [e.sorte for e in journal]
    assert sortes[:2] == ["evenement", "liquidation"]
    assert sortes.count("revalorisation") == 1 and sortes.count("foyer") == 2
    evenement = journal.entree(f"depart_{carriere.personne}").contenu
    assert _erreurs(contrats.Validateur("evenement").valider(
        evenement.donnees(), "evenement")) == []
    for entree in journal:
        assert _erreurs(contrats.Validateur("entree_journal").valider(
            entree.donnees(), "entree")) == [], entree.id
    date = f"{annee:04d}-12-31"
    servies = [e for e in journal.servi(date, sorte="composante")
               if e.id != "majoration_enfants"]
    assert servies and all(e.remplace is not None and e.id.endswith(str(annee))
                           for e in servies)
    [foyer_servi] = journal.servi(date, sorte="foyer")
    assert foyer_servi.id == f"foyer_{annee}"
    # Ce que l'échéancier sert est ce que la revalorisation calculait.
    au_depart = simulateur.scenario_actuel.calculer(carriere)
    assert echeancier.au_depart.pension_annuelle == au_depart.pension_annuelle
    assert echeancier.aujourd_hui.pension_annuelle == actuel_aujourd_hui(
        simulateur, carriere, au_depart, annee).pension_annuelle


def test_le_depart_est_un_acte_tire_de_la_carriere(simulateur):
    carriere = _carriere(simulateur, **CARRIERES["salarie"])
    depart = _echeancier.depart_de(carriere)
    assert depart.date == f"{carriere.date_liquidation.annee:04d}-" \
                          f"{carriere.date_liquidation.mois:02d}-01"
    assert depart.origine == "acte" and depart.sorte == "depart"
    assert _echeancier.SORTES["depart"]["liquider"] is True


def test_le_simulateur_fait_passer_le_scenario_1_par_l_echeancier(simulateur):
    carriere = _carriere(simulateur, **CARRIERES["mere_au_foyer"])
    comparaison = simulateur.simuler(carriere)
    liquidations = [e for e in comparaison.journal if e.sorte == "liquidation"]
    assert len(liquidations) == 1
    assert comparaison.actuel.pension_annuelle == simulateur.scenario_actuel.calculer(
        carriere).pension_annuelle


# -- le pilote -----------------------------------------------------------------

@pytest.mark.parametrize("cas", [c for c in CAS_TYPES if c.regle_liquidation != "services"][:4],
                         ids=lambda c: c.code)
def test_le_pilote_date_un_depart_sans_rien_liquider(simulateur, cas):
    """Le point fixe des cas types n'interroge que l'étape « ouvrir le
    droit » : il ne coûte aucune liquidation, et donne l'âge que les cas
    types retiennent."""
    avant = liquidation.appels()
    age = pilote.age_de_depart(simulateur, cas, 1960)
    assert liquidation.appels() == avant
    assert age == cas.age_liquidation_pour(simulateur, 1960)
    assert pilote.age_de_depart(simulateur, cas, 1960, "absolu") == cas.age_liquidation


# -- le nombre d'appels déclaré ----------------------------------------------------

def test_chaque_temoin_declare_ses_appels_de_liquider_sous_le_nombre_declare():
    """Chaque témoin compte ses appels de ``liquider``, liquidations d'essai
    comprises : ``scripts/construire_temoins.py`` les écrit, le portage
    JavaScript les refait (``tests/js/moteur.test.js``), et aucun ne dépasse
    le nombre déclaré (docs/architecture.md, § 7.8)."""
    temoins = json.loads((RACINE / "tests" / "temoins" / "simulations.json")
                         .read_text(encoding="utf-8"))
    appels = {nom: temoin.get("appels_liquider") for nom, temoin in temoins.items()}
    sans = sorted(nom for nom, n in appels.items() if not isinstance(n, int))
    assert not sans, f"témoins sans appels déclarés : {sans[:5]}"
    trop = {nom: n for nom, n in appels.items() if n > liquidation.APPELS_DECLARES}
    assert not trop, f"au-delà de {liquidation.APPELS_DECLARES} appels : {trop}"
    assert min(appels.values()) >= 1


# -- les deux moteurs ------------------------------------------------------------

#: Une requête sur cinq des témoins, comme pour l'acquisition (test_droit.py).
PAS = 5


def _requetes() -> list[dict]:
    temoins = json.loads((RACINE / "tests" / "temoins" / "simulations.json")
                         .read_text(encoding="utf-8"))
    return [temoin["requete"] for temoin in list(temoins.values())[::PAS]]


def _python(requetes: list[dict]) -> list[dict]:
    """Ce que la liquidation et l'échéancier écrivent, en Python, pour chaque
    requête : la liquidation et ses étapes, le journal, et les appels."""
    sys.path.insert(0, str(RACINE / "src"))
    from retraite_notionnelle.web.pages import Contexte, Saisie

    contexte = Contexte()
    saisies: list = []
    original = Simulateur.simuler

    def capter(self, carriere, *args, **kwargs):
        comparaison = original(self, carriere, *args, **kwargs)
        if not saisies:
            saisies.append(comparaison)
        return comparaison

    sortie = []
    Simulateur.simuler = capter
    try:
        for requete in requetes:
            saisies.clear()
            avant = liquidation.appels()
            try:
                contexte.simuler(Saisie.depuis_requete(requete))
            except Exception as erreur:  # noqa: BLE001 — le refus est comparé
                sortie.append({"erreur": str(erreur)})
                continue
            if not saisies:
                sortie.append({"erreur": "aucune carrière simulée"})
                continue
            journal = saisies[0].journal
            [liquidee] = [e.contenu for e in journal if e.sorte == "liquidation"]
            sortie.append({"ouverture": liquidee.ouverture.donnees(),
                           "pensions": liquidee.pensions.donnees(),
                           "complements": liquidee.complements.donnees(),
                           "journal": journal.donnees(),
                           "appels": liquidation.appels() - avant})
    finally:
        Simulateur.simuler = original
    return json.loads(json.dumps(sortie))


def _ecarts(obtenu, attendu, chemin: str, ecarts: list[str]) -> None:
    """Les écarts entre les deux moteurs : un milliardième au plus sur un
    nombre, comme les témoins (tests/js/comparer.mjs) ; rien ailleurs."""
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        if isinstance(attendu, dict) and isinstance(obtenu, dict):
            for cle in sorted(set(attendu) | set(obtenu)):
                _ecarts(obtenu.get(cle), attendu.get(cle), f"{chemin}.{cle}", ecarts)
        elif isinstance(attendu, list) and isinstance(obtenu, list) and len(attendu) == len(obtenu):
            for rang, (o, a) in enumerate(zip(obtenu, attendu)):
                _ecarts(o, a, f"{chemin}[{rang}]", ecarts)
        elif obtenu != attendu:
            ecarts.append(f"{chemin} : python={str(attendu)[:80]} js={str(obtenu)[:80]}")
        return
    if isinstance(obtenu, bool) or not isinstance(obtenu, (int, float)):
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")
        return
    echelle = max(abs(attendu), 1e-300)
    if abs(obtenu - attendu) / echelle > 1e-9 and abs(obtenu - attendu) > 1e-12:
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")


def test_les_deux_moteurs_liquident_et_journalisent_a_l_identique():
    """Pour une requête sur cinq des témoins, chaque étape de la liquidation
    écrit la même donnée en Python et en JavaScript, le journal a les mêmes
    entrées — la liquidation au contrat C.6, ses composantes, l'ASPA, la
    revalorisation de l'échéance —, et les deux moteurs appellent
    ``liquider`` le même nombre de fois."""
    requetes = _requetes()
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus = json.loads(execution.stdout)
    attendus = _python(requetes)
    assert len(obtenus) == len(attendus) == len(requetes)
    assert sum("journal" in a for a in attendus) > 0.9 * len(requetes)
    assert any(any(e["contenu"]["sorte"] == "revalorisation" for e in a["journal"])
               for a in attendus if "journal" in a), "au moins une échéance"
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
