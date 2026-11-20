"""La carte de justesse : l'état d'une partie se calcule depuis ses preuves
(action 194, étape A).

Une partie est une règle sur une période : une version de fiche, ou la fiche
entière tant qu'elle n'est pas découpée. Son état est l'un de six, que
``noyau/justesse.py`` calcule et que personne n'écrit. Ce fichier dit, sur des
cas fabriqués, ce qui fait chaque état ; puis il tient le cliquet : une partie
prouvée ne cesse de l'être qu'en le disant.
"""

from __future__ import annotations

import copy

import pytest
import yaml

import test_cliquets_du_droit_date as cliquets_du_droit
from retraite_notionnelle.noyau import carte, justesse

from test_oracle import _charger_exemples, _confronter

CLIQUET = justesse.RACINE / "tests" / "cliquets_de_justesse" / "prouvees.yaml"

LUE = {"id": "LEGIARTI000000000001", "lu_le": "2026-11-20"}


def _fiche(etat="conforme", versions=None, **champs) -> dict:
    return {"id": "regle", "etat": etat, "regimes": ["regime_general"],
            "versions": versions if versions is not None else [
                {"id": "v1", "statut": "lue", "textes": [LUE], "exemples": "aucun trouvé"}],
            **champs}


def _grille(**champs) -> dict:
    return {"schema_version": 1, "id": "grille_de_la_regle", "sorte": "grille_independante",
            "etage": "regle", "parties": [{"fiche": "regle", "version": "v1"}],
            "source": {"auteur": "une session qui n'a pas ouvert le dépôt",
                       "reference": "code de la sécurité sociale, L. 351-1",
                       "etabli_le": "2026-11-20"},
            "independance": "Valeurs posées à la main depuis le seul texte, sans lire le code.",
            "seuils": ["l'âge légal", "la durée requise"],
            "cas": [{"id": "cas_1", "enonce": "un cas", "attendu": {"taux_liquidation": 0.5}}],
            **champs}


def _etat(fiche, exemples=(), preuves=()) -> dict:
    etats = justesse.etats({"regle": fiche}, list(exemples), list(preuves))
    return etats[("regle", fiche["versions"][0]["id"] if fiche["versions"] else None)]


# --- Les six états, sur des cas fabriqués ----------------------------------

def test_une_partie_sans_preuve_est_non_verifiee_quoi_que_dise_la_fiche():
    """« Conforme » est un mot que la fiche écrit : il ne prouve rien. Sans
    grille indépendante, la partie est non vérifiée, même lue et tracée."""
    etat = _etat(_fiche("conforme"))
    assert etat["etat"] == "non_verifiee" and etat["tracee"] is True
    assert _etat(_fiche("transcrite"))["etat"] == "non_verifiee"
    assert _etat(_fiche("a_verifier"))["etat"] == "non_verifiee"


def test_une_grille_independante_et_un_texte_trace_font_une_partie_prouvee():
    """Texte tracé et grille verte : prouvée au texte seul. Un témoin
    extérieur d'accord de plus : prouvée avec témoin."""
    assert _etat(_fiche(), preuves=[_grille()])["etat"] == "prouvee_au_texte_seul"
    fiche = _fiche()
    fiche["versions"][0]["exemples"] = ["un_exemple"]
    exemple = {"id": "un_exemple", "attendu": {"taux_liquidation": 0.5}}
    etat = _etat(fiche, [exemple], [_grille()])
    assert etat["etat"] == "prouvee_avec_temoin" and etat["temoins"] == ["un_exemple"]
    # Un témoin sans grille ne prouve pas : il rassure, sans couvrir les seuils.
    assert _etat(fiche, [exemple])["etat"] == "non_verifiee"


def test_une_grille_ne_prouve_pas_un_texte_sans_trace_ni_une_version_supposee():
    sans_trace = _fiche(versions=[{"id": "v1", "statut": "lue",
                                   "textes": [{"id": "LEGIARTI000000000001"}]}])
    assert _etat(sans_trace, preuves=[_grille()])["etat"] == "non_verifiee"
    supposee = _fiche(versions=[{"id": "v1", "statut": "supposee", "hypothese": "aucun texte",
                                 "textes": [LUE]}])
    assert _etat(supposee, preuves=[_grille()])["etat"] == "non_verifiee"


def test_un_ecart_etabli_fait_une_partie_fausse_avec_son_action():
    """Un cas de preuve en écart connu, ou un exemple officiel en écart connu,
    fait la partie fausse ; l'action est celle que la preuve nomme."""
    grille = _grille()
    grille["cas"][0]["ecart_connu"] = {
        "modele": {"taux_liquidation": 0.49}, "action": 194, "depuis": "2026-11-20",
        "explication": "le modèle sert le taux de la génération suivante, à corriger"}
    etat = _etat(_fiche(), preuves=[grille])
    assert etat["etat"] == "fausse" and etat["actions"] == [194]
    fiche = _fiche(etat="approchee", exemples=["un_exemple"], versions=[])
    exemple = {"id": "un_exemple", "attendu": {"x": 1},
               "ecart_connu": {"modele": {"x": 2}, "fiche": "regle"}}
    etat = _etat(fiche, [exemple])
    assert etat["etat"] == "fausse" and etat["actions"] == [] and etat["ecarts"] == ["un_exemple"]
    # Une règle connue et absente du modèle est fausse pour ceux qu'elle touche.
    assert _etat(_fiche("manquante"))["etat"] == "fausse"


def test_un_ecart_que_la_fiche_ne_situe_pas_touche_toutes_ses_versions():
    """Le doute profite au faux : un exemple en écart que seule la fiche cite
    marque chacune de ses versions ; un exemple d'accord, lui, ne témoigne que
    pour la version qui le cite."""
    versions = [{"id": "v1", "statut": "lue", "textes": [LUE]},
                {"id": "v2", "statut": "lue", "textes": [LUE]}]
    fiche = _fiche(versions=versions, exemples=["en_ecart", "d_accord"])
    exemples = [{"id": "en_ecart", "ecart_connu": {"modele": {"x": 2}, "fiche": "regle"}},
                {"id": "d_accord"}]
    etats = justesse.etats({"regle": fiche}, exemples, [])
    assert [etats[("regle", v)]["etat"] for v in ("v1", "v2")] == ["fausse", "fausse"]
    etats = justesse.etats({"regle": fiche}, exemples[1:], [])
    assert etats[("regle", "v1")]["temoins"] == [] == etats[("regle", "v2")]["temoins"]
    assert etats[("regle", "v1")]["temoins_a_situer"] == ["d_accord"]


def test_une_approximation_declaree_fait_une_partie_approchee_jamais_prouvee():
    """Une approximation qui nomme ses versions ne touche qu'elles ; celle
    qui n'en nomme aucune, ou une fiche approchée qui n'en déclare pas, touche
    toute la fiche."""
    versions = [{"id": "v1", "statut": "lue", "textes": [LUE]},
                {"id": "v2", "statut": "lue", "textes": [LUE]}]
    fiche = _fiche("approchee", versions=versions,
                   approximations=[{"version": ["v2"], "ecart": "e", "effet": "non mesuré"}])
    grille = _grille(parties=[{"fiche": "regle", "version": "v1"},
                              {"fiche": "regle", "version": "v2"}])
    etats = justesse.etats({"regle": fiche}, [], [grille])
    assert etats[("regle", "v1")]["etat"] == "prouvee_au_texte_seul"
    assert etats[("regle", "v2")]["etat"] == "approchee"
    for approximations in ([], [{"ecart": "e", "effet": "non mesuré"}]):
        fiche = _fiche("approchee", versions=copy.deepcopy(versions),
                       approximations=approximations)
        etats = justesse.etats({"regle": fiche}, [], [grille])
        assert {e["etat"] for e in etats.values()} == {"approchee"}


def test_une_regle_que_le_simulateur_ne_pretend_pas_calculer_est_hors_champ():
    assert _etat(_fiche("pas_encore_modelisee"))["etat"] == "hors_champ"


def test_une_fiche_non_decoupee_est_une_seule_partie_que_rien_ne_prouve():
    """Sans version, aucun texte n'est rattaché à une période : la fiche
    entière est une partie, qu'une grille ne peut pas prouver."""
    fiche = _fiche(versions=[])
    grille = _grille(parties=[{"fiche": "regle"}])
    etat = _etat(fiche, preuves=[grille])
    assert etat["etat"] == "non_verifiee" and etat["tracee"] is False


# --- Le format d'une preuve ------------------------------------------------

def test_une_preuve_dit_sa_sorte_sa_source_ses_parties_et_ses_cas():
    fiches = {"regle": _fiche()}
    assert justesse.controler_preuve(_grille(), fiches) == []
    for champ in ("sorte", "etage", "parties", "source", "cas", "independance", "seuils"):
        preuve = _grille()
        del preuve[champ]
        assert justesse.controler_preuve(preuve, fiches), champ
    assert justesse.controler_preuve(_grille(sorte="intuition"), fiches)
    assert justesse.controler_preuve(_grille(parties=[{"fiche": "inconnue"}]), fiches)
    assert justesse.controler_preuve(
        _grille(parties=[{"fiche": "regle", "version": "v9"}]), fiches)
    # Un moteur extérieur n'a pas à dire son indépendance, mais sa version.
    moteur = _grille(sorte="moteur_exterieur")
    del moteur["independance"], moteur["seuils"]
    assert justesse.controler_preuve(moteur, fiches)
    moteur["source"]["version"] = "3.3.2"
    assert justesse.controler_preuve(moteur, fiches) == []
    # Un écart connu dit la valeur du modèle, pourquoi, depuis quand, et son action.
    ecart = _grille()
    ecart["cas"][0]["ecart_connu"] = {"modele": {"taux_liquidation": 0.4}}
    assert justesse.controler_preuve(ecart, fiches)


def test_les_preuves_se_lisent_une_par_fichier_sous_le_nom_de_leur_fichier(tmp_path):
    assert justesse.preuves(tmp_path / "absent") == []
    (tmp_path / "grille_de_la_regle.yaml").write_text(
        yaml.safe_dump(_grille(), allow_unicode=True), encoding="utf-8")
    (lue,) = justesse.preuves(tmp_path)
    assert lue["id"] == "grille_de_la_regle"
    assert justesse.controler(tmp_path, {"regle": _fiche()}) == []
    (tmp_path / "autre_nom.yaml").write_text(
        yaml.safe_dump(_grille(), allow_unicode=True), encoding="utf-8")
    assert any("autre_nom" in erreur
               for erreur in justesse.controler(tmp_path, {"regle": _fiche()}))


def test_un_cas_de_preuve_se_rejoue_comme_un_exemple_officiel():
    """Un cas suit le schéma d'un exemple officiel : la même carrière
    minuscule, les mêmes grandeurs attendues, la même confrontation. Un cas
    faussé est refusé ; déclaré en écart connu avec la valeur du modèle, il
    passe, et la partie devient fausse."""
    vrai = next(e for e in _charger_exemples() if e["id"] == "sp_f19666_decote")
    assert not _confronter(vrai)
    faux = copy.deepcopy(vrai)
    faux["attendu"]["taux_liquidation"] = vrai["attendu"]["taux_liquidation"] + 0.01
    assert _confronter(faux)


# --- La carte du jour ------------------------------------------------------

def test_les_preuves_du_depot_suivent_leur_format():
    assert justesse.controler() == []


@pytest.mark.parametrize(
    "cas", [cas for preuve in justesse.preuves() for cas in preuve["cas"]],
    ids=lambda cas: cas["id"])
def test_chaque_cas_des_preuves_du_depot_est_rejoue(cas):
    """Le simulateur rend la valeur attendue de chaque cas, ou la valeur que
    son écart connu déclare : une grille verte l'est parce que ce test passe."""
    problemes = _confronter(cas)
    assert not problemes, problemes


def test_la_lecture_tracee_est_celle_du_cliquet_des_lectures_sans_trace():
    """La première colonne de la carte est le compteur des lectures sans
    trace de la note 0009 : la même règle, sur toutes les versions."""
    for nom, fiche in carte.fiches().items():
        for version in fiche.get("versions") or []:
            if isinstance(version, dict) and version.get("statut", "lue") == "lue":
                assert justesse.lecture_tracee(version) == cliquets_du_droit._lecture_tracee(
                    version), (nom, version["id"])


def test_chaque_partie_de_la_carte_a_un_etat_et_un_seul():
    fiches = carte.fiches()
    etats = justesse.etats()
    versions = sum(len(f.get("versions") or []) for f in fiches.values())
    entieres = sum(1 for f in fiches.values() if not f.get("versions"))
    assert len(etats) == versions + entieres
    assert {e["etat"] for e in etats.values()} <= set(justesse.ETATS)
    # Chaque exemple officiel en écart connu fait au moins une partie fausse.
    for exemple in _charger_exemples():
        if exemple.get("ecart_connu"):
            fiche = exemple["ecart_connu"]["fiche"]
            assert any(e["etat"] == "fausse" and exemple["id"] in e["ecarts"]
                       for (nom, _), e in etats.items() if nom == fiche), exemple["id"]


def test_le_tableau_par_famille_compte_chaque_partie_dans_chacune_de_ses_familles():
    lignes = justesse.par_famille()
    total = lignes[-1]
    assert total["famille"] == "toute la carte" and total["parties"] == len(justesse.etats())
    for ligne in lignes:
        assert ligne["parties"] == sum(ligne[etat] for etat in justesse.ETATS), ligne["famille"]
    assert {ligne["famille"] for ligne in lignes[:-1]} >= {"base_prive", "liberal", "special"}


# --- Le cliquet : une partie prouvée ne recule pas -------------------------

def test_le_cliquet_refuse_un_recul_et_demande_d_inscrire_une_avancee():
    """Sur des listes fabriquées : une partie inscrite qui n'est plus prouvée
    est un recul, sauf retirée avec sa raison ; une partie prouvée qui n'est
    pas inscrite est à inscrire."""
    assert justesse.reculs({"a / v1"}, {"prouvees": ["a / v1"], "retirees": {}}) == ([], [])
    reculs, a_inscrire = justesse.reculs(set(), {"prouvees": ["a / v1"], "retirees": {}})
    assert reculs == ["a / v1"] and a_inscrire == []
    reculs, a_inscrire = justesse.reculs({"a / v1", "b / v2"},
                                         {"prouvees": ["a / v1"], "retirees": {}})
    assert reculs == [] and a_inscrire == ["b / v2"]
    retiree = {"prouvees": [], "retirees": {"a / v1": {
        "le": "2026-11-20",
        "raison": "la grille avait lu la rédaction de 2010 pour celle de 2004, elle est refaite"}}}
    assert justesse.reculs(set(), retiree) == ([], [])
    # Une raison de trois mots n'en est pas une ; une partie retirée qui est
    # de nouveau prouvée se réinscrit.
    courte = {"prouvees": [], "retirees": {"a / v1": {"le": "2026-11-20", "raison": "grille fausse"}}}
    assert justesse.reculs(set(), courte)[0] == ["a / v1"]
    assert justesse.reculs({"a / v1"}, retiree)[1] == ["a / v1"]


def test_aucune_partie_prouvee_ne_recule():
    """Le nombre des parties prouvées ne peut que monter. Une partie inscrite
    au cliquet qui n'est plus prouvée — sa grille rougit, son texte perd sa
    trace, un écart s'y déclare — bloque l'envoi : on répare, ou on la retire
    en disant pourquoi."""
    liste = yaml.safe_load(CLIQUET.read_text(encoding="utf-8"))
    reculs, a_inscrire = justesse.reculs(justesse.prouvees(), liste)
    assert not reculs, (f"{reculs} : inscrite(s) prouvée(s) dans {CLIQUET.name}, et ne l'est "
                        "plus ; réparer, ou la retirer en disant pourquoi")
    assert not a_inscrire, f"{a_inscrire} : prouvée(s) depuis, à inscrire dans {CLIQUET.name}"


# --- Le tableau de bord ----------------------------------------------------

def test_le_tableau_de_bord_ecrit_la_carte_avec_ses_denominateurs():
    """La page dit combien de parties sont prouvées sur combien, famille par
    famille, et nomme chaque partie fausse avec son action, ou dit qu'elle
    n'en a pas encore."""
    import sys

    sys.path.insert(0, str(justesse.RACINE / "scripts"))
    import tableau_de_bord

    versions = [{"id": "v1", "statut": "lue", "textes": [LUE]},
                {"id": "v2", "statut": "lue", "textes": [LUE], "exemples": ["en_ecart"]}]
    fiches = {"regle": _fiche(versions=versions)}
    officiels = [{"id": "en_ecart", "ecart_connu": {"modele": {"x": 2}, "fiche": "regle"}}]
    grille = _grille()
    calcules = justesse.etats(fiches, officiels, [grille])
    lignes = justesse.par_famille(calcules, fiches, {"regime_general": "base_prive"})
    texte = "\n".join(tableau_de_bord.carte_de_justesse(calcules, lignes))
    assert "**1 partie prouvée sur 2**" in texte
    assert "| toute la carte | 2 | 1 | 1 | 0 | 0 | 0 | 2 | 0 |" in texte
    assert "| salariés du privé, régimes de base | 2 | 1 | 1 |" in texte
    fausses = "\n".join(tableau_de_bord.parties_fausses(calcules))
    assert "`regle / v2`" in fausses and "en_ecart" in fausses
    assert "aucune action" in fausses


def test_le_tableau_de_bord_porte_la_carte_de_justesse():
    page = (justesse.RACINE / "docs" / "etat.md").read_text(encoding="utf-8")
    total = justesse.par_famille()[-1]
    prouvees = total["prouvee_avec_temoin"] + total["prouvee_au_texte_seul"]
    assert f"sur {total['parties']}**" in page and "La carte de justesse" in page
    assert f"**{prouvees or 'Aucune'} partie" in page


# --- Les autres moteurs, quantité par quantité -----------------------------

def test_un_autre_moteur_se_lit_quantite_par_quantite(tmp_path):
    """La confrontation à un autre moteur, cas par cas, dit pour chaque
    quantité combien de cas la confrontent et combien concordent. Elle ne
    touche l'état d'aucune règle : un cas y est une carrière entière."""
    import json

    chemin = tmp_path / "ecarts.json"
    assert justesse.moteur_exterieur(chemin) is None
    chemin.write_text(json.dumps({
        "modele": "UN MOTEUR", "version": "1.2.3",
        "cas": {"a": {"quantites": {"taux": {"statut": "concorde"},
                                    "rafp": {"statut": "ecart"}}},
                "b": {"quantites": {"taux": {"statut": "ecart"}}}}}), encoding="utf-8")
    lu = justesse.moteur_exterieur(chemin)
    assert (lu["modele"], lu["version"], lu["cas"]) == ("UN MOTEUR", "1.2.3", 2)
    assert lu["quantites"] == {"rafp": (1, 0), "taux": (2, 1)}
    assert (lu["confrontees"], lu["concordent"]) == (3, 1)


def test_le_tableau_de_bord_dit_ce_que_trajectoire_confirme():
    lu = justesse.moteur_exterieur()
    page = (justesse.RACINE / "docs" / "etat.md").read_text(encoding="utf-8")
    assert f"{lu['concordent']} quantités sur {lu['confrontees']}" in page
