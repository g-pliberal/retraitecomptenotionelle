"""Les univers de droit : la proposition, écrite en couches sur le droit réel.

``docs/architecture.md``, § 4.8 et annexe C.4. Chaque scénario est un univers
(``data/reference/univers/``), une pile de couches (``data/reference/couches/``)
posée sur la carte des règles. Ce test tient le contrat et les règles de la
pile ; il fixe ce que le moteur tire de chaque univers, qui est ce que le
simulateur calculait avant la phase 7 ; il montre ce que le moteur refuse ; et
il fabrique, pour chaque univers de la proposition, la liste des fiches du
droit réel qu'aucune couche ne décide (§ 4.8, § 6.7).
"""

from __future__ import annotations

import dataclasses
import importlib
import re
import shutil
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import (
    RACINE_DONNEES,
    Parametres,
    PartCotisation,
    SourceCotisations,
)
from retraite_notionnelle.noyau import carte, univers
from retraite_notionnelle.scenarios import univers as moteur

RACINE = Path(__file__).resolve().parents[1]
REFERENCE = RACINE_DONNEES / "reference"
PROPOSITION = ("notionnel_retroactif", "notionnel_prospectif",
               "notionnel_retroactif_employeur", "notionnel_prospectif_employeur",
               "notionnel_liberal")
#: Ce que la liquidation fictive des droits acquis neutralisait avant la phase 7
#: (``calculer(ignorer_penalite_age=True, avantages_non_contributifs=False)``) :
#: les points gratuits suivaient les avantages non contributifs.
CONTRIBUTIF_SEUL = frozenset({"avantages_non_contributifs", "points_gratuits", "decote_surcote"})


@pytest.fixture(scope="module")
def tous():
    return univers.charger()


@pytest.fixture(scope="module")
def calculs(tous):
    parametres = Parametres()
    return {cle: moteur.calcul_notionnel(u, parametres)
            for cle, u in tous.items() if not u.est_le_droit_reel}


def _copie(tmp_path: Path) -> tuple[Path, Path]:
    """Les univers et les couches, copiés pour qu'un test les fausse."""
    shutil.copytree(REFERENCE / "univers", tmp_path / "univers")
    shutil.copytree(REFERENCE / "couches", tmp_path / "couches")
    return tmp_path / "univers", tmp_path / "couches"


def _ecrire(dossier: Path, donnee: dict) -> None:
    (dossier / f"{donnee['id']}.yaml").write_text(
        yaml.safe_dump(donnee, allow_unicode=True, sort_keys=False), encoding="utf-8")


# -- ce qui tient ----------------------------------------------------------------

def test_les_univers_tiennent():
    """Le contrat C.4 sans erreur ni manque, les règles de la pile, et chaque
    passage que cite une couche ou une fiche de la proposition retrouvé mot
    pour mot dans le texte de la proposition (§ 3.1)."""
    assert univers.controler() == []


def test_les_six_scenarios_sont_six_univers(tous):
    """Le droit réel, puis les cinq univers de la proposition, dans l'ordre de
    leurs numéros ; la liste que le tableau, la page et l'API citent en est
    tirée."""
    from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS

    assert list(tous) == ["actuel", *PROPOSITION]
    assert [u.numero for u in tous.values()] == [1, 2, 3, 4, 5, 6]
    assert tous["actuel"].est_le_droit_reel and tous["actuel"].couches == ("droit_reel",)
    assert SCENARIOS_NOTIONNELS == tuple((u.id, u.numero, u.nom)
                                         for u in univers.de_la_proposition())


def test_les_couches_se_composent_comme_les_scenarios(tous):
    """Le scénario 4 est le 2 plus la part patronale, le 5 est le 3 plus la
    même part ; le 6 est le 4 jusqu'à la bascule, puis ses propres règles
    (§ 4.8). Le prospectif est le rétroactif posé sur la transition, et la
    couche du seul calcul est juste sous elle."""
    assert tous["notionnel_retroactif_employeur"].couches == (
        *tous["notionnel_retroactif"].couches, "part_patronale")
    assert tous["notionnel_prospectif_employeur"].couches == (
        *tous["notionnel_prospectif"].couches, "part_patronale")
    assert tous["notionnel_liberal"].couches[:3] == tous["notionnel_retroactif_employeur"].couches
    assert tous["notionnel_prospectif"].couches == (
        "droit_reel", "contributif_seul", "valorisation_des_droits_acquis",
        *tous["notionnel_retroactif"].couches[1:])


def test_chaque_univers_se_calcule_comme_avant_la_phase_7(calculs):
    """Ce que le moteur tire de chaque univers est ce que le simulateur codait
    en dur : le compte et ses paramètres, la transition et ce que sa
    liquidation fictive neutralise, le pilier, la garantie, l'âge légal."""
    totale = (("part_cotisation", PartCotisation.TOTALE),)
    attendus = {
        "notionnel_retroactif": (False, (), False, False, False, frozenset()),
        "notionnel_prospectif": (True, (), False, False, False, CONTRIBUTIF_SEUL),
        "notionnel_retroactif_employeur": (False, totale, False, False, False, frozenset()),
        "notionnel_prospectif_employeur": (True, totale, False, False, False, CONTRIBUTIF_SEUL),
        "notionnel_liberal": (False, (
            ("part_cotisation", PartCotisation.TOTALE),
            ("source_cotisations", SourceCotisations.TAUX_HISTORIQUES_PUIS_UNIFORME),
            ("taux_cotisation_uniforme", Parametres().taux_cotisation_liberal),
        ), True, True, True, frozenset()),
    }
    for cle, (prospectif, modifications, capitalisation, garantie, age_legal,
              neutralisations) in attendus.items():
        calcul = calculs[cle]
        assert (calcul.prospectif, calcul.modifications, calcul.capitalisation,
                calcul.garantie, calcul.age_legal, calcul.neutralisations) == (
            prospectif, modifications, capitalisation, garantie, age_legal,
            neutralisations), cle


def test_un_parametre_qui_se_lit_ailleurs_suit_son_reglage(tous):
    """Le taux unique vaut ce que vaut ``taux_cotisation_liberal`` : un réglage
    du site le déplace sans toucher la couche."""
    calcul = moteur.calcul_notionnel(tous["notionnel_liberal"],
                                     Parametres(taux_cotisation_liberal=0.2))
    assert dict(calcul.modifications)["taux_cotisation_uniforme"] == 0.2


# -- les fiches de la proposition --------------------------------------------------

def test_chaque_fiche_de_la_proposition_est_ajoutee_et_connue_du_moteur(tous):
    """Une fiche de la proposition entre dans un univers au moins, et le
    moteur sait l'appliquer ; il n'en connaît pas qui n'ait sa fiche."""
    fiches = set(carte.fiches_de_la_proposition())
    ajoutees = {f for u in tous.values() for f in u.ajoutees}
    assert fiches == ajoutees == set(moteur.FICHES_DU_MOTEUR)


def test_chaque_fiche_de_la_proposition_est_lue_et_datee():
    """Ce que la veille exige d'une fiche du droit réel, la proposition
    l'exige des siennes, sur son propre texte (§ 3.1) : un intitulé, une
    version qui cite le README, une lecture datée et la suivante, un effet."""
    for nom, fiche in carte.fiches_de_la_proposition().items():
        assert len(str(fiche["intitule"]).split()) >= 6, nom
        assert fiche["etat"] == "transcrite", nom
        textes = [t for v in fiche["versions"] for t in v.get("textes") or []]
        assert any(str(t.get("reference", "")).startswith("README.md") and t.get("citation")
                   for t in textes), nom
        sources = fiche["sources"]
        assert str(sources["prochaine_relecture"]) > str(sources["lu_le"]), nom
        assert len(str(fiche.get("effet") or "").split()) >= 3, nom


def test_chaque_fiche_de_la_proposition_dit_son_code():
    """« Chaque règle du code a sa fiche, et chaque fiche a son code » (§ 6.7) :
    les fonctions Python existent, leurs jumelles JavaScript sont dans les
    fichiers nommés, les paramètres sont ceux du simulateur, les tests
    existent."""
    champs = {f.name for f in dataclasses.fields(Parametres)}
    for nom, fiche in carte.fiches_de_la_proposition().items():
        code = fiche["code"]
        for module, fonctions in code["python"].items():
            objet_module = importlib.import_module(module)
            for chemin in fonctions:
                objet = objet_module
                for morceau in chemin.split("."):
                    objet = getattr(objet, morceau)
        for fichier, noms in code["javascript"].items():
            texte = (RACINE / fichier).read_text(encoding="utf-8")
            for fonction in noms:
                assert re.search(rf"\b{re.escape(fonction)}\b", texte), (nom, fichier, fonction)
        assert set(code["parametres"]) <= champs, (nom, set(code["parametres"]) - champs)
        for test in code["tests"]:
            assert (RACINE / test).exists(), (nom, test)


def test_le_compte_garde_les_regles_de_cotisation_qu_il_applique():
    """Les interrupteurs que le compte lit dans les périodes des régimes
    renvoient à des fiches du droit réel : le compte les applique, et la
    couche des comptes notionnels le dit en les gardant. Aucune couche ne les
    neutralise."""
    from retraite_notionnelle.donnees.regimes import fichiers_de_regimes

    lus = ("assiette_plancher", "assiette_forfaitaire", "cotisation_par_classes")
    source = (RACINE / "src" / "retraite_notionnelle" / "moteur" / "compte.py").read_text(
        encoding="utf-8")
    assert all(re.search(rf"\b{champ}\b", source) for champ in lus)
    designees = {periode[champ] for _, donnee in fichiers_de_regimes(RACINE_DONNEES)
                 for periode in donnee.get("periodes") or () for champ in lus
                 if periode.get(champ)}
    couche = univers.Couche.lue(univers.couches()["comptes_notionnels"])
    gardees = {o.fiche for o in couche.operations if o.operation == "garder"}
    assert designees and designees <= gardees
    fiches = carte.fiches()
    for cle, u in univers.charger().items():
        for _, operation in u.decisions:
            if operation.operation == "neutraliser":
                assert not univers.fiches_visees(operation.vise, fiches) & designees, (
                    cle, str(operation))


# -- les fiches sans décision ------------------------------------------------------

def test_chaque_univers_de_la_proposition_liste_ses_fiches_sans_decision(tous):
    """Pour chaque univers de la proposition, les fiches du droit réel
    qu'aucune couche ne garde, ne remplace ni ne neutralise : les domaines
    sans décision (§ 8). Aucune n'est décidée, toutes sont du droit réel ;
    le droit réel n'en a pas, il est la carte."""
    fiches = carte.fiches()
    assert univers.sans_decision(tous["actuel"]) == []
    for cle in PROPOSITION:
        reste = univers.sans_decision(tous[cle])
        assert reste and set(reste) <= set(fiches), cle
        decidees = set()
        for _, operation in tous[cle].decisions:
            decidees |= univers.fiches_visees(operation.vise, fiches)
        assert not decidees & set(reste), cle
        assert "reversion" not in reste and "decote_regime_general" not in reste, cle


def test_une_fiche_ajoutee_au_droit_reel_apparait_sans_decision(tmp_path):
    """Une fiche ajoutée demain au droit réel apparaît d'elle-même dans la
    liste, au lieu de se glisser sans qu'on le voie dans les scénarios 2, 4 et
    6 ; si elle dit une étape que la proposition neutralise, elle est décidée."""
    regles = tmp_path / "regles"
    shutil.copytree(carte.REGLES, regles)
    fiche = yaml.safe_load((carte.REGLES / "reversion.yaml").read_text(encoding="utf-8"))
    for nom, etape in (("regle_de_demain", None), ("decote_de_demain", "liquider_chaque_regime")):
        _ecrire(regles, {**fiche, "id": nom, **({"etape": etape} if etape else {})})
    tous = univers.charger(REFERENCE / "univers", REFERENCE / "couches", regles)
    for cle in PROPOSITION:
        reste = univers.sans_decision(tous[cle], carte.fiches(regles))
        assert "regle_de_demain" in reste and "decote_de_demain" not in reste, cle


# -- ce que la pile refuse ----------------------------------------------------------

def test_deux_couches_qui_touchent_la_meme_fiche_sans_ordre_sont_refusees(tmp_path):
    """Deux couches ne décident pas autrement la même fiche, ne changent pas
    le même paramètre, n'ajoutent pas deux fois la même fiche (§ 4.8)."""
    dossier, couches = _copie(tmp_path)
    _ecrire(couches, {"schema_version": 1, "id": "garde_la_decote", "nom": "Garde la décote",
                      "operations": [{"operation": "garder", "vise": "decote_regime_general"}]})
    _ecrire(couches, {"schema_version": 1, "id": "salariale", "nom": "Part salariale",
                      "operations": [{"operation": "changer_un_parametre",
                                      "vise": "compte_notionnel",
                                      "parametre": "part_cotisation", "valeur": "salariale"}]})
    _ecrire(couches, {"schema_version": 1, "id": "encore_le_compte", "nom": "Encore le compte",
                      "operations": [{"operation": "ajouter", "vise": "compte_notionnel"}]})
    for nom, pile in (("decote", ["garde_la_decote"]), ("parametre", ["part_patronale", "salariale"]),
                      ("double", ["encore_le_compte"])):
        _ecrire(dossier, {"schema_version": 1, "id": nom, "nom": nom,
                          "couches": ["droit_reel", "comptes_notionnels", *pile]})
    erreurs = univers.controler(dossier, couches)
    assert any(e.startswith("univers decote : decote_regime_general") for e in erreurs), erreurs
    assert any(e.startswith("univers parametre : compte_notionnel.part_cotisation")
               for e in erreurs), erreurs
    assert any(e.startswith("univers double : compte_notionnel : ajoutée") for e in erreurs), erreurs


def test_la_pile_a_ses_regles(tmp_path):
    """Le droit réel en bas et seulement là ; une couche qui existe ; une
    couche d'un seul calcul sous une transition ; une fiche de la proposition
    changée après qu'une couche d'en dessous l'a ajoutée."""
    dossier, couches = _copie(tmp_path)
    for nom, pile in (("sans_base", ["comptes_notionnels"]),
                      ("inconnue", ["droit_reel", "licorne"]),
                      ("calcul_seul", ["droit_reel", "contributif_seul", "comptes_notionnels"]),
                      ("trop_tot", ["droit_reel", "part_patronale", "comptes_notionnels"])):
        _ecrire(dossier, {"schema_version": 1, "id": nom, "nom": nom, "couches": pile})
    erreurs = "\n".join(univers.controler(dossier, couches))
    assert "univers sans_base : le droit réel est en bas" in erreurs
    assert "univers inconnue : couches inconnues : licorne" in erreurs
    assert "univers calcul_seul : la couche contributif_seul ne vaut que pour un calcul" in erreurs
    assert "univers trop_tot : part_patronale" in erreurs


def test_une_couche_dit_ce_qu_elle_vise(tmp_path):
    """Une fiche que la carte n'a pas, un sélecteur inconnu, la contributivité
    hors d'un calcul, un paramètre que la fiche ne lit pas, une date qui n'est
    pas nommée, une citation qui n'est pas dans le texte de la proposition."""
    dossier, couches = _copie(tmp_path)
    _ecrire(couches, {"schema_version": 1, "id": "fautive", "nom": "Fautive",
                      "depuis": {"date": "bascule", "valeur": {"parametre": "annee_bascule"}},
                      "operations": [
                          {"operation": "neutraliser", "vise": "chimere"},
                          {"operation": "neutraliser", "vise": {"humeur": "sombre"}},
                          {"operation": "neutraliser", "vise": {"contributivite": "avpf"}},
                          {"operation": "changer_un_parametre", "vise": "compte_notionnel",
                           "parametre": "age_legal_liberal", "valeur": 60},
                          {"operation": "garder", "vise": "avpf",
                           "motif": "« une promesse que la proposition ne fait pas »"}]})
    erreurs = "\n".join(univers.controler(dossier, couches))
    for fragment in ("aucune fiche de la carte ne s'appelle ainsi",
                     "sélecteur « humeur » inconnu",
                     "la contributivité ne se résout pas en fiches",
                     "ne lit pas « age_legal_liberal »",
                     "« bascule » n'est pas une date nommée",
                     "« une promesse que la proposition ne fait pas » n'est pas dans README.md"):
        assert fragment in erreurs, fragment


# -- ce que le moteur refuse ----------------------------------------------------------

def _univers(tous, cle, *couches_ajoutees: univers.Couche, sans: tuple[str, ...] = ()) -> univers.Univers:
    base = tous[cle]
    pile = tuple(c for c in base.pile if c.id not in sans) + couches_ajoutees
    return dataclasses.replace(base, pile=pile)


def test_le_moteur_refuse_ce_qu_il_ne_sait_pas_faire(tous):
    """Une fiche ajoutée depuis une autre date que la sienne, un paramètre du
    compte qu'il ne sait pas changer, la garantie sur un compte ouvert à la
    bascule, le pilier sans la garantie, une neutralisation qu'aucune
    liquidation ne connaît : chacun l'arrête (§ 6.7)."""
    parametres = Parametres()
    pilier = univers.Couche.lue(univers.couches()["capitalisation_obligatoire"])
    garantie = univers.Couche.lue(univers.couches()["garantie_vieillesse"])
    cas = {
        "depuis": _univers(tous, "notionnel_retroactif",
                           dataclasses.replace(pilier, depuis="origine"), garantie),
        "parametre": _univers(tous, "notionnel_retroactif", univers.Couche(
            "etat", "L'État", (univers.Operation("changer_un_parametre", "compte_notionnel",
                                                 "contribution_etat", "entiere"),))),
        "prospectif": _univers(tous, "notionnel_prospectif", garantie),
        "pilier": _univers(tous, "notionnel_retroactif", pilier),
        "neutralisation": _univers(tous, "notionnel_prospectif", univers.Couche(
            "minima", "Sans minima", (univers.Operation("neutraliser", ("domaine", "minima")),),
            portee="calcul")),
        "sans_compte": _univers(tous, "notionnel_liberal", sans=("comptes_notionnels",)),
    }
    messages = {
        "depuis": "le moteur applique capitalisation_obligatoire depuis",
        "parametre": "ne sait pas changer compte_notionnel.contribution_etat",
        "prospectif": "ni le pilier ni la garantie sur un compte ouvert à la bascule",
        "pilier": "le pilier se sert avec la garantie",
        "neutralisation": "aucune liquidation ne sait « neutraliser {domaine: minima} »",
        "sans_compte": "ne calcule la proposition que sur le compte notionnel",
    }
    for nom, u in cas.items():
        with pytest.raises(ValueError, match=re.escape(messages[nom])):
            moteur.calcul_notionnel(u, parametres)
    with pytest.raises(ValueError, match="le droit réel se calcule par l'échéancier"):
        moteur.calcul_notionnel(tous["actuel"], parametres)


def test_le_simulateur_partage_ce_que_les_univers_partagent():
    """Deux univers qui changent les mêmes paramètres partagent leur compte,
    comme 2 et 3, ou 4 et 5 ; le pilier n'est construit que pour l'univers
    qui l'ajoute."""
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur()
    compte = {cle: simulateur.scenario_de(calcul).constructeur
              for cle, calcul in simulateur.calculs.items()}
    assert compte["notionnel_retroactif"] is compte["notionnel_prospectif"] is simulateur.constructeur
    assert (compte["notionnel_retroactif_employeur"] is compte["notionnel_prospectif_employeur"]
            is simulateur.constructeur_employeur)
    assert compte["notionnel_liberal"] is simulateur.constructeur_liberal
    assert [cle for cle, calcul in simulateur.calculs.items()
            if simulateur.scenario_de(calcul).capitalisation is not None] == ["notionnel_liberal"]


# -- le portage -----------------------------------------------------------------------

def _node(script: str) -> object:
    """Ce que le portage rend, lu par ``node`` depuis la racine du dépôt."""
    import json
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sortie = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                            capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(sortie.stdout)


def test_le_paquet_porte_les_univers_resolus(tous):
    """Le site ne résout pas les couches : la fabrication l'a fait (§ 13.5).
    Le paquet porte chaque univers et ce que le moteur en tire, un paramètre
    qui se lit ailleurs restant un renvoi que le site lit sous ses réglages."""
    import json

    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    assert [u["id"] for u in paquet["univers"]] == list(tous)
    for porte in paquet["univers"]:
        u = tous[porte["id"]]
        assert (porte["numero"], porte["nom"], porte["couches"]) == (u.numero, u.nom,
                                                                     list(u.couches))
        attendu = None if u.est_le_droit_reel else moteur.calcul_notionnel(u, None).donnees()
        assert porte["calcul"] == attendu, u.id
    liberal = next(u for u in paquet["univers"] if u["id"] == "notionnel_liberal")
    assert liberal["calcul"]["modifications"]["taux_cotisation_uniforme"] == {
        "parametre": "taux_cotisation_liberal"}


def test_les_deux_moteurs_tirent_la_meme_chose_des_univers(calculs):
    """Le portage résout les renvois sous ses réglages comme le Python sous
    les siens, bâtit les mêmes scénarios, partage les mêmes comptes, et range
    les mêmes univers parmi les prospectifs de la page Coût."""
    from retraite_notionnelle import cout
    from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS

    lu = _node(
        'import { readFileSync } from "node:fs";'
        'import { Simulateur } from "./moteur/js/simulateur.js";'
        'import { CLES_PROSPECTIVES } from "./moteur/js/cout.js";'
        'const s = new Simulateur(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));'
        'const c = s.calculs;'
        "process.stdout.write(JSON.stringify({"
        "  scenarios: s.scenarios,"
        "  calculs: Object.fromEntries(Object.entries(c).map(([k, v]) => ["
        "    k, { ...v, neutralisations: [...v.neutralisations].sort() }])),"
        "  partages: ["
        "    s.scenarioDe(c.notionnel_prospectif).constructeur === s.constructeur,"
        "    s.scenarioDe(c.notionnel_prospectif_employeur).constructeur === s.constructeurEmployeur,"
        "    s.scenarioLiberal.capitalisation !== null,"
        "    s.scenarioNotionnel.capitalisation === null],"
        "  prospectives: [...CLES_PROSPECTIVES].sort(),"
        "}));")
    assert [tuple(s) for s in lu["scenarios"]] == list(SCENARIOS_NOTIONNELS)
    for cle, calcul in calculs.items():
        attendu = calcul.donnees()
        attendu["neutralisations"] = sorted(calcul.neutralisations)
        assert lu["calculs"][cle] == attendu, cle
    assert lu["partages"] == [True, True, True, True]
    assert lu["prospectives"] == sorted(cout.CLES_PROSPECTIVES)
