"""L'outillage qui accélère un changement de résultats (feuille de route, action
135) : le script qui régénère tout, et celui qui résume ce que les témoins ont
bougé. Aucun de ces tests ne lance un calcul du modèle : le premier se lit dans
sa table d'étapes et s'exerce sur des étapes simulées, le second sur des
témoins écrits pour l'occasion."""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import regenerer  # noqa: E402
import resumer_temoins  # noqa: E402

# -- la régénération -----------------------------------------------------------


def test_chaque_fichier_fabrique_a_son_etape():
    """Les fichiers que ``.gitattributes`` déclare fabriqués — ceux qui ne se
    fusionnent pas et se relancent — ont chacun l'étape qui les écrit : la
    liste et le script ne peuvent pas diverger."""
    fabriques = [ligne.split()[0]
                 for ligne in (RACINE / ".gitattributes").read_text(encoding="utf-8")
                 .splitlines()
                 if ligne.strip() and not ligne.startswith("#")
                 and ligne.split()[-1] == "-merge"]
    ecrits = " ".join(etape.ecrit for etape in regenerer.etapes())
    assert fabriques
    assert [f for f in fabriques if f not in ecrits] == []


def test_chaque_etape_a_son_script_et_sait_verifier():
    for etape in regenerer.etapes():
        script = RACINE / "scripts" / etape.script
        assert script.is_file(), etape.script
        for argument in etape.verifier:
            assert argument in script.read_text(encoding="utf-8"), (etape.script, argument)


def test_l_ordre_suit_ce_que_chaque_etape_lit():
    """L'inventaire avant tout ; les témoins après le paquet, dont ils rendent
    les pages ; le tableau de bord, qui compte les témoins, puis les chiffres
    ancrés, qui sondent tout, à la fin, et le contrôle de conservation en
    dernier."""
    premier, milieu, dernier = regenerer.TEMPS
    assert regenerer.INVENTAIRE in premier[0]
    assert (regenerer.PAQUET, regenerer.TEMOINS) in milieu
    assert dernier == ((regenerer.TABLEAU_DE_BORD, regenerer.PROSE, regenerer.CONSERVATION),)
    assert regenerer.etapes(regenerer.TEMPS_PROSE) == [
        regenerer.TABLEAU_DE_BORD, regenerer.PROSE, regenerer.CONSERVATION]


def _simuler(monkeypatch, echecs: set[str]) -> list[tuple[str, bool]]:
    """Remplace le lancement des scripts : chaque étape « réussit », sauf celles
    d'``echecs`` ; rend la liste des étapes lancées, et en quel mode."""
    lancees = []

    def lancer(etape, verifier):
        lancees.append((etape.nom, verifier))
        return regenerer.Issue(etape, 1 if etape.nom in echecs else 0, 0.0, "")

    monkeypatch.setattr(regenerer, "lancer", lancer)
    return lancees


def test_une_ecriture_qui_echoue_arrete_ce_qui_la_lit(monkeypatch, capsys):
    """Le paquet échoue : les témoins, qui le lisent, ne se lancent pas, ni le
    dernier temps ; le chiffrage et les tableaux, qui ne le lisent pas, oui."""
    lancees = _simuler(monkeypatch, {"paquet"})
    assert regenerer.regenerer(sequentiel=True) == 1
    noms = [nom for nom, _ in lancees]
    assert "paquet" in noms and "chiffrage" in noms and "tableaux" in noms
    assert "témoins" not in noms and "prose" not in noms
    assert "paquet : en échec" in capsys.readouterr().err


def test_une_verification_passe_tout_en_revue(monkeypatch, capsys):
    """Deux fichiers périmés : la vérification les dit tous les deux, et passe
    chaque étape en revue, sans rien écrire."""
    lancees = _simuler(monkeypatch, {"paquet", "prose"})
    assert regenerer.regenerer(verifier=True) == 1
    assert sorted(nom for nom, _ in lancees) == sorted(e.nom for e in regenerer.etapes())
    assert all(verifier for _, verifier in lancees)
    assert "paquet, prose : périmé" in capsys.readouterr().err


def test_tout_va_bien(monkeypatch, capsys):
    _simuler(monkeypatch, set())
    assert regenerer.regenerer() == 0
    assert "tout est régénéré" in capsys.readouterr().out


# -- le résumé des témoins -----------------------------------------------------


def _temoin(**pensions: float) -> dict:
    return {"resultat": {"scenarios": {
        scenario: {"pension_annuelle": montant} for scenario, montant in pensions.items()}}}


def test_le_resume_dit_combien_bougent_de_combien_et_lesquels():
    avant = {
        "a": _temoin(actuel=1000.0, notionnel_liberal=500.0),
        "b": _temoin(actuel=2000.0, notionnel_liberal=800.0),
        "c": _temoin(actuel=3000.0, notionnel_liberal=900.0),
        "parti": _temoin(actuel=1.0),
    }
    apres = {
        "a": _temoin(actuel=1050.0, notionnel_liberal=500.0),
        "b": _temoin(actuel=1800.0, notionnel_liberal=800.0),
        # Un milliardième de moins que le seuil : le bruit d'un arrondi.
        "c": _temoin(actuel=3000.0 * (1 + 1e-12), notionnel_liberal=900.0),
        "venu": _temoin(actuel=1.0),
    }
    resume = resumer_temoins.resumer(avant, apres)
    assert (resume.temoins, resume.bougent) == (4, 3)
    assert (resume.nouveaux, resume.disparus) == (["venu"], ["parti"])
    actuel = next(m for m in resume.mouvements if m.scenario == "actuel")
    assert (actuel.numero, actuel.compares, actuel.bougent) == (1, 3, 2)
    assert actuel.hausses == 1 and actuel.fortes_baisses == 1
    texte = resumer_temoins.ecrire(resume, "HEAD")
    assert texte.splitlines()[0] == (
        "4 témoins de simulation, dont 3 bougent depuis HEAD ; 1 nouveau, 1 disparu.")
    assert ("- scénario 1 : 2 sur 3 bougent, −2,50 % en médiane ; de −10,00 % (b) "
            "à +5,00 % (a) ; 1 hausse, 1 baisse de plus de 1 %.") in texte
    assert "- scénario 6 : aucune pension ne bouge, sur 3." in texte


def test_rien_ne_bouge_se_dit_en_une_ligne():
    temoins = {"a": _temoin(actuel=1000.0), "b": _temoin(actuel=2000.0)}
    pages = {"accueil": {"corps": "<p>un</p>"}, "cout": {"corps": "<p>deux</p>"}}
    resume = resumer_temoins.resumer(temoins, dict(temoins), pages, dict(pages))
    assert resumer_temoins.ecrire(resume, "origin/main") == (
        "2 témoins de simulation, aucun ne bouge depuis origin/main.\n"
        "2 rendus de page, aucun ne change.")


def test_les_pages_qui_changent_sont_nommees():
    avant = {nom: {"corps": "avant"} for nom in "abcdefghij"}
    apres = {nom: {"corps": "après"} for nom in "abcdefghij"}
    resume = resumer_temoins.resumer({}, {}, avant, apres)
    ligne = resumer_temoins.ecrire(resume, "HEAD").splitlines()[-1]
    assert ligne == ("10 rendus de page, dont 10 changent : a, b, c, d, e, f, g, h, "
                     "et 2 autres.")


def test_un_pourcentage_s_ecrit_comme_la_prose():
    assert resumer_temoins.pourcent(0.0024) == "+0,24 %"
    assert resumer_temoins.pourcent(-0.0265) == "−2,65 %"
