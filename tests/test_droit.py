"""Les étapes de l'acquisition, chacune seule, et le relevé des droits.

``docs/architecture.md``, § 7.1 et 7.2 : les étapes s'échangent des données
que décrit un schéma (``data/reference/etapes/``), chaque étape se teste seule
et se compare seule entre Python et JavaScript. La phase 4 a déplacé le
scénario 1 dans ``src/retraite_notionnelle/droit/`` (et ``moteur/js/droit/``)
sans qu'un résultat bouge : les témoins le tiennent. Ce fichier tient le
reste — ce que chaque étape écrit, qu'elle suit son schéma, que le relevé suit
le contrat C.5, et que les deux moteurs écrivent la même chose.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import acquerir, compter, coordonner, releve
from retraite_notionnelle.noyau import contrats
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


def _schema(etape: str) -> contrats.Validateur:
    return contrats.Validateur(etape, contrats.ETAPES)


def _erreurs(constats) -> list[str]:
    return [str(c) for c in constats if c.genre == "erreur"]


# -- chaque étape, seule -------------------------------------------------------

def test_coordonner_route_chaque_ligne_et_retablit(simulateur):
    """Un an à l'État en 1984, puis le privé : l'agent part sans droit à
    pension, et ses années passent au régime général et à l'Ircantec. La
    coordination le dit, ligne par ligne, et suit son schéma."""
    carriere = _carriere(simulateur, [
        Metier("salarie_prive_non_cadre", 20.0), Metier("fonctionnaire_etat", 22.0),
        Metier("salarie_prive_non_cadre", 23.0)])
    coordination = coordonner.coordonner(simulateur.scenario_actuel, carriere)
    assert len(coordination.regimes) == len(coordination.carriere.lignes)
    donnees = coordination.donnees()
    assert _erreurs(_schema("coordonner_les_affiliations").valider(donnees, "coordination")) == []
    [retablissement] = donnees["retablissements"]
    assert "fonction_publique_etat" in retablissement["regimes"]
    assert retablissement["radiation"] == "1985-01-01"
    etat = [ligne for ligne in donnees["lignes"] if ligne["affiliation"] == "fonctionnaire_etat"]
    assert etat and all(ligne["revenu_retabli"] > 0 for ligne in etat)
    assert all("regime_general" in ligne["regimes"] and "fonction_publique_etat" not in ligne["regimes"]
               for ligne in etat)


def test_coordonner_ne_touche_pas_une_carriere_sans_retablissement(simulateur):
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 22.0)])
    coordination = coordonner.coordonner(simulateur.scenario_actuel, carriere)
    assert coordination.carriere is carriere
    assert coordination.retablissements == ()


def test_compter_additionne_les_activites_d_une_annee_et_plafonne_a_la_lecture(simulateur):
    """Un salarié qui ouvre un cabinet le soir : deux activités de la même
    année versent au régime général et aux indépendants. Le compte de chaque
    régime les garde ; lus ensemble, ils ne dépassent pas quatre trimestres
    par an."""
    carriere = _carriere(simulateur, [
        Metier("salarie_prive_non_cadre", 22.0),
        Metier("artisan", 40.0, cumul=True, age_fin=45.0)], naissance=1970)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    durees = compter.compter(actuel, coordination)
    assert _erreurs(_schema("compter_les_durees").valider(durees.donnees(), "durees")) == []
    regimes = [code for code in durees.par_annee["assurance"]
               if 2010 in durees.par_annee["assurance"][code]]
    assert len(regimes) >= 2, regimes
    somme = sum(durees.par_annee["assurance"][code][2010] for code in regimes)
    assert somme > 4
    assert durees.cumul_plafonne("assurance", tuple(regimes)) <= durees.cumul_plafonne(
        "assurance", tuple(regimes[:1])) + durees.cumul_plafonne("assurance", tuple(regimes[1:]))
    annees = {annee for code in regimes for annee in durees.par_annee["assurance"][code]}
    assert durees.cumul_plafonne("assurance", tuple(regimes)) <= 4 * len(annees)


def test_compter_donne_les_trimestres_des_enfants_au_regime_que_la_priorite_designe(simulateur):
    """Une salariée, trois enfants : le régime général porte la majoration
    de durée d'assurance, huit trimestres par enfant, hors plafond annuel, et
    le relevé en fait une ligne par enfant, qui dit sa présomption."""
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 22.0)],
                         naissance=1970, sexe="F", nombre_enfants=3)
    actuel = simulateur.scenario_actuel
    releve_ = releve.construire(actuel, carriere)
    enfants = releve_.durees.enfants
    assert (enfants.regime, enfants.dispositif, enfants.trimestres) == ("regime_general", "mda", 24)
    assert releve_.durees.hors_annee["assurance"] == {"regime_general": 24}
    lignes = [ligne for ligne in releve_.lignes() if ligne["id"].startswith("enfants_")]
    assert [ligne["fait"] for ligne in lignes] == [
        "naissance_enfant_1", "naissance_enfant_2", "naissance_enfant_3"]
    assert all(ligne["droit"]["quantite"] == 8 and ligne["fiche"] == releve.FICHE_ENFANTS
               and not ligne["contributive"]
               and "naissance_des_enfants" in ligne["presomptions"] for ligne in lignes)
    sans = compter.compter(actuel, releve_.coordination, avantages_non_contributifs=False)
    assert sans.enfants is None and sans.trimestres == releve_.durees.trimestres - 24


def test_acquerir_somme_les_credits_dans_leur_ordre(simulateur):
    """Les comptes de points sont la somme des crédits, faite dans l'ordre où
    ils ont été crédités : au bit près, puisque c'est ainsi que la liquidation
    les lisait avant la phase 4."""
    carriere = _carriere(simulateur, [Metier("salarie_prive_cadre", 23.0)], naissance=1965,
                         nombre_enfants=3)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    assert _erreurs(_schema("acquerir_les_droits").valider(droits.donnees(), "droits")) == []
    assert "agirc_arrco" in droits.points_acquis
    for code, total in droits.points_acquis.items():
        somme = 0.0
        for credit, _, points, _ in droits.points:
            if credit == code:
                somme += points
        assert total == somme, code
    assert droits.majoration_points["agirc_arrco"] > 0


def test_acquerir_plafonne_la_duree_des_mines(simulateur):
    """Cent vingt trimestres au plus aux mines, sauf ceux d'avant cinquante-
    cinq ans : le mineur entré à dix-huit ans voit sa durée plafonnée, et le
    plafond réduit ses points."""
    carriere = _carriere(simulateur, [Metier("mineur", 18.0)], naissance=1950, liquidation=60)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    plafonds = {code: (total, avant, retenus) for code, total, avant, retenus in droits.plafonds}
    assert plafonds, "la durée des mines est plafonnée"
    for code, (total, avant, retenus) in plafonds.items():
        assert retenus == min(total, max(120.0, avant))


def test_acquerir_attribue_les_points_gratuits_de_la_rco(simulateur):
    """Un chef d'exploitation installé en 1975, parti en 2019 : la RCO lui
    attribue des points pour ses années d'avant 2003, sans cotisation — une
    ligne du relevé non contributive, qui cite sa fiche."""
    carriere = _carriere(simulateur, [Metier("exploitant_agricole", 20.0)], naissance=1955,
                         liquidation=64)
    actuel = simulateur.scenario_actuel
    releve_ = releve.construire(actuel, carriere)
    assert releve_.droits.gratuits, "des points gratuits"
    lignes = [ligne for ligne in releve_.lignes() if ligne["id"].startswith("gratuits_")]
    assert lignes and all(ligne["fiche"] == releve.FICHE_POINTS_GRATUITS
                          and not ligne["contributive"] for ligne in lignes)
    sans = releve.construire(actuel, carriere, points_gratuits=False)
    assert not sans.droits.gratuits


# -- le relevé -----------------------------------------------------------------

CARRIERES = {
    "salarie": dict(metiers=[Metier("salarie_prive_non_cadre", 22.0)]),
    "cadre_mere": dict(metiers=[Metier("salarie_prive_cadre", 23.0)], sexe="F", nombre_enfants=2,
                       naissance=1975),
    "fonctionnaire": dict(metiers=[Metier("fonctionnaire_etat", 23.0)], part_primes=0.2),
    "retabli": dict(metiers=[Metier("salarie_prive_non_cadre", 20.0),
                             Metier("fonctionnaire_etat", 22.0),
                             Metier("salarie_prive_non_cadre", 23.0)]),
    "artisan_puis_salarie": dict(metiers=[Metier("artisan", 20.0),
                                          Metier("salarie_prive_non_cadre", 40.0)], naissance=1960),
    "chef_d_exploitation": dict(metiers=[Metier("exploitant_agricole", 20.0)], naissance=1955),
    "interrompue": dict(metiers=[Metier("salarie_prive_non_cadre", 22.0)], naissance=1970,
                        interruptions={1998: "chomage_indemnise", 1999: "chomage_indemnise"}),
}


@pytest.mark.parametrize("nom", sorted(CARRIERES))
def test_le_releve_suit_le_contrat_c5(simulateur, nom):
    """Le relevé passe le contrat C.5 sans une erreur : ce qui manque — la
    version de la fiche, le texte appliqué, la fiche d'une règle qui n'en a
    pas encore — est un manque, que le tableau de bord compte. Chaque ligne
    d'une carrière déclarée cite le fait de la chronologie qui l'ouvre."""
    options = dict(CARRIERES[nom])
    carriere = _carriere(simulateur, **options)
    donnees = releve.construire(simulateur.scenario_actuel, carriere).donnees()
    constats = contrats.Validateur("ligne_releve").valider(donnees, "releve")
    assert _erreurs(constats) == []
    manques = {c.chemin.rsplit(".", 1)[-1] for c in constats if c.genre == "manque"}
    assert manques <= {"version", "texte", "fiche", "fiabilite"}, manques
    assert donnees["lignes"]
    faits = {f["id"] for f in carriere.chronologie["faits"]}
    for ligne in donnees["lignes"]:
        assert ligne.get("fait") in faits, ligne["id"]
    assert len({ligne["id"] for ligne in donnees["lignes"]}) == len(donnees["lignes"])


def test_le_releve_d_une_annee_interrompue_cite_l_interruption(simulateur):
    carriere = _carriere(simulateur, **CARRIERES["interrompue"])
    lignes = releve.construire(simulateur.scenario_actuel, carriere).lignes()
    de_1998 = [ligne for ligne in lignes if ligne["id"] == "assurance_regime_general_1998"]
    assert [ligne["fait"] for ligne in de_1998] == ["interruption_1998"]
    assert not de_1998[0]["contributive"]


def test_le_releve_d_un_releve_de_carriere_est_observe(simulateur):
    """Les trimestres d'un relevé de carrière déposé font foi : leurs lignes
    sont observées, non calculées."""
    from retraite_notionnelle.carriere import LigneRelevee

    carriere = Carriere.depuis_releve(
        annee_naissance=1970, sexe="H",
        releve=[LigneRelevee(annee, "salarie_prive_non_cadre", 20000.0, 4)
                for annee in range(1992, 2034)],
        age_liquidation=64, macro=simulateur.macro)
    lignes = releve.construire(simulateur.scenario_actuel, carriere).lignes()
    durees = [ligne for ligne in lignes if ligne["droit"]["unite"] == "trimestre"]
    assert durees and all(ligne["origine"] == "observee" and ligne["fait"].startswith("releve_")
                          for ligne in durees)


def test_les_groupes_du_releve_sont_ceux_de_la_liquidation(simulateur):
    """Un artisan devenu salarié, né en 1960, part après 2017 : la
    liquidation unique réunit ses régimes alignés, et le relevé écrit le
    groupe, le liquidateur en tête."""
    carriere = _carriere(simulateur, **CARRIERES["artisan_puis_salarie"])
    releve_ = releve.construire(simulateur.scenario_actuel, carriere)
    groupes = releve_.donnees()["groupes"]
    assert groupes and all(len(g["regimes"]) >= 2 for g in groupes)
    assert releve.construire(simulateur.scenario_actuel, carriere,
                             liquider_successions=False).groupes == {}


def test_la_liquidation_ne_lit_que_le_releve(simulateur):
    """``calculer`` construit le relevé et le lit : les mêmes drapeaux
    donnent le même relevé, et la pension ne dépend que de lui."""
    carriere = _carriere(simulateur, **CARRIERES["cadre_mere"])
    actuel = simulateur.scenario_actuel
    un = releve.construire(actuel, carriere)
    deux = releve.construire(actuel, carriere)
    assert un.donnees() == deux.donnees()
    assert actuel.calculer(carriere).pension_annuelle == actuel.calculer(carriere).pension_annuelle


# -- les deux moteurs ----------------------------------------------------------

#: Une requête sur cinq des témoins : tous les statuts y passent, et la
#: comparaison reste sous la minute.
PAS = 5


def _requetes() -> list[dict]:
    temoins = json.loads((RACINE / "tests" / "temoins" / "simulations.json").read_text(encoding="utf-8"))
    return [temoin["requete"] for temoin in list(temoins.values())[::PAS]]


def _python(requetes: list[dict]) -> list[dict]:
    """Ce que chaque étape écrit, en Python, pour chaque requête."""
    sys.path.insert(0, str(RACINE / "src"))
    from retraite_notionnelle.web.pages import Contexte, Saisie

    contexte = Contexte()
    saisies: list = []
    original = Simulateur.simuler

    def capter(self, carriere, *args, **kwargs):
        if not saisies:
            saisies.append((self, carriere))
        return original(self, carriere, *args, **kwargs)

    sortie = []
    Simulateur.simuler = capter
    try:
        for requete in requetes:
            saisies.clear()
            try:
                contexte.simuler(Saisie.depuis_requete(requete))
            except Exception as erreur:  # noqa: BLE001 — le refus est comparé
                sortie.append({"erreur": str(erreur)})
                continue
            if not saisies:
                sortie.append({"erreur": "aucune carrière simulée"})
                continue
            simulateur, carriere = saisies[0]
            releve_ = releve.construire(simulateur.scenario_actuel, carriere)
            sortie.append({"coordination": releve_.coordination.donnees(),
                           "durees": releve_.durees.donnees(),
                           "droits": releve_.droits.donnees(),
                           "releve": releve_.donnees()})
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


def test_les_deux_moteurs_ecrivent_les_memes_etapes():
    """Pour une requête sur cinq des témoins, chaque étape écrit la même donnée
    en Python et en JavaScript — la coordination, les durées, les droits — et
    le relevé a les mêmes lignes : chaque étape se compare seule (§ 7.1)."""
    requetes = _requetes()
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-droit.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus = json.loads(execution.stdout)
    attendus = _python(requetes)
    assert len(obtenus) == len(attendus) == len(requetes)
    assert sum("releve" in a for a in attendus) > 0.9 * len(requetes)
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
