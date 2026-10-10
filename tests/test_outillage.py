"""L'outillage qui accélère un changement de résultats (feuille de route, action
135) : le script qui régénère tout, celui qui résume ce que les témoins ont
bougé, la mémoire des calculs lourds et le précalcul des chiffres ancrés.
Aucun de ces tests ne lance un calcul du modèle : le premier script se lit dans
sa table d'étapes et s'exerce sur des étapes simulées, le second sur des
témoins écrits pour l'occasion, la mémoire et le précalcul sur des calculs
factices qui se comptent."""

from __future__ import annotations

import multiprocessing
import os
import pickle
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

import pytest

from retraite_notionnelle import memoire

#: La vraie, que ``memoire_isolee`` remplace pour les calculs factices.
_CODE_HORS_DU_MODELE = memoire._code_hors_du_modele

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import mesures_prose  # noqa: E402
import regenerer  # noqa: E402
import resumer_temoins  # noqa: E402
import verifier_prose  # noqa: E402

# -- la régénération -----------------------------------------------------------


def test_chaque_fichier_fabrique_a_son_etape():
    """Les fichiers que ``.gitattributes`` déclare fabriqués — ceux qui ne se
    fusionnent pas et se relancent — ont chacun l'étape qui les écrit : la
    liste et le script ne peuvent pas diverger. Le verdict de la suite, que
    GitHub écrit après elle, a pour étape ``scripts/publier_fabrique.sh``."""
    fabriques = [ligne.split()[0]
                 for ligne in (RACINE / ".gitattributes").read_text(encoding="utf-8")
                 .splitlines()
                 if ligne.strip() and not ligne.startswith("#")
                 and ligne.split()[-1] == "-merge"]
    ecrits = " ".join(etape.ecrit for etape in regenerer.etapes())
    ecrits += (RACINE / "scripts" / "publier_fabrique.sh").read_text(encoding="utf-8")
    assert fabriques
    assert [f for f in fabriques if f not in ecrits] == []


def test_une_suite_rouge_n_est_pas_publiee_verte(tmp_path):
    """L'étape de la suite passe la sortie de pytest dans ``tee``. Sous le
    ``bash -e`` que GitHub prend quand l'étape ne nomme pas son shell, l'issue
    du tube est celle de ``tee`` : le 7 octobre 2026, onze courses rouges ont
    été publiées vertes. L'étape se joue ici sous le shell que GitHub lui
    donnerait, pytest remplacé par un échec, et doit échouer."""
    import yaml

    flux = yaml.safe_load((RACINE / ".github" / "workflows" / "tests.yml")
                          .read_text(encoding="utf-8"))
    etape = next(e for e in flux["jobs"]["suite"]["steps"] if e.get("id") == "suite")
    # Les shells de GitHub : `shell: bash` est `bash --noprofile --norc -eo
    # pipefail {0}` ; sans `shell`, c'est `bash -e {0}`.
    shell = (["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c"]
             if etape.get("shell") == "bash" else ["bash", "-e", "-c"])
    script = etape["run"].replace("python -m pytest", "false")
    assert script != etape["run"], "l'étape ne lance plus `python -m pytest`"
    issue = subprocess.run([*shell, script], capture_output=True,
                           env={**os.environ, "RUNNER_TEMP": str(tmp_path)})
    assert issue.returncode != 0


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
    """Et une étape simulée ne se retient pas : la mémoire des fabrications
    (``fabrique.py``) dispenserait sinon la suite de vérifier ce que personne
    n'a fabriqué."""
    _simuler(monkeypatch, set())
    retenues = []
    monkeypatch.setattr(regenerer.fabrique, "retenir", retenues.append)
    assert regenerer.regenerer() == 0
    assert "tout est régénéré" in capsys.readouterr().out
    assert retenues == []


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


def test_une_page_mise_en_morceaux_n_a_pas_change():
    """Le témoin garde le HTML en morceaux depuis le 7 octobre 2026, une
    révision antérieure en une chaîne : la même page sous les deux formes ne
    change pas ; un mot de plus, si, comme une page nouvelle."""
    avant = {"accueil": {"corps": "<p>un</p>\n<p>deux</p>"}, "cout": {"corps": "<p>trois</p>"}}
    apres = {"accueil": {"corps": ["<p>un</p>\n", "<p>deux</p>"]},
             "cout": {"corps": ["<p>trois mots</p>"]}, "methode": {"corps": ["<p>neuf</p>"]}}
    resume = resumer_temoins.resumer({}, {}, avant, apres)
    assert resume.pages_changees == ["cout", "methode"]


def test_un_pourcentage_s_ecrit_comme_la_prose():
    assert resumer_temoins.pourcent(0.0024) == "+0,24 %"
    assert resumer_temoins.pourcent(-0.0265) == "−2,65 %"


# -- la mémoire des calculs ----------------------------------------------------


def _compteur(faits: list, genre: str, valeur: float):
    """Un calcul factice qui se compte, et se garde comme les vrais."""
    def calcul():
        faits.append(genre)
        return valeur
    return calcul


def test_un_calcul_se_garde_tant_que_l_empreinte_est_la_meme(monkeypatch, memoire_isolee):
    faits = []
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    assert memoire_isolee.memoriser(("essai", 3), _compteur(faits, "a", 30.0)) == 30.0
    monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})     # un autre processus
    assert memoire_isolee.memoriser(("essai", 3), _compteur(faits, "a", 30.0)) == 30.0
    assert faits == ["a"]
    # Une source a bougé : tout se refait, sous la nouvelle empreinte.
    monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e2")
    memoire_isolee.memoriser(("essai", 3), _compteur(faits, "a", 30.0))
    assert faits == ["a", "a"]
    assert sorted(d.name for d in memoire_isolee.DOSSIER.iterdir()) == ["e1", "e2"]


def test_chaque_lecture_rend_un_objet_neuf(monkeypatch, memoire_isolee):
    """Comme ``charger_yaml`` rend une copie : ce qu'un appelant fait de son
    objet ne touche pas le suivant."""
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    premier = memoire_isolee.memoriser(("liste",), lambda: [1, 2])
    premier.append(3)
    assert memoire_isolee.memoriser(("liste",), lambda: [9]) == [1, 2]


def test_un_calcul_pendant_lequel_une_source_bouge_ne_se_garde_pas(monkeypatch,
                                                                   memoire_isolee):
    empreintes = iter(["avant", "après"])
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: next(empreintes))
    memoire_isolee.memoriser(("essai",), lambda: 1.0)
    assert not list(memoire_isolee.DOSSIER.rglob("*.pickle"))


def test_un_calcul_fait_apres_une_retouche_du_code_ne_se_garde_pas(monkeypatch,
                                                                   memoire_isolee):
    """Le processus a peut-être calculé avec l'ancien code, que l'empreinte ne
    lit plus."""
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    monkeypatch.setattr(memoire_isolee, "_code_retouche", lambda: True)
    memoire_isolee.memoriser(("essai",), lambda: 1.0)
    assert not list(memoire_isolee.DOSSIER.rglob("*.pickle"))


def test_une_memoire_illisible_se_refait_et_l_on_peut_s_en_passer(monkeypatch,
                                                                  memoire_isolee):
    faits = []
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    dossier = memoire_isolee.DOSSIER / "e1"
    dossier.mkdir(parents=True)
    garde = dossier / f"{memoire_isolee.nom(('essai', 1))}.pickle"
    garde.write_bytes(b"tronqu")
    assert memoire_isolee.memoriser(("essai", 1), _compteur(faits, "a", 10.0)) == 10.0
    assert pickle.loads(garde.read_bytes()) == 10.0          # refait, et gardé
    monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})
    monkeypatch.setenv(memoire_isolee.SANS_MEMOIRE, "1")
    memoire_isolee.memoriser(("essai", 1), _compteur(faits, "a", 10.0))
    memoire_isolee.memoriser(("essai", 2), _compteur(faits, "b", 20.0))
    assert faits == ["a", "a", "b"]                         # rien de relu…
    assert list(dossier.glob("*.pickle")) == [garde]         # …ni d'écrit


def test_sous_un_modele_modifie_la_memoire_se_tait(monkeypatch, memoire_isolee):
    """Un contexte qui remplace une fonction du modèle ne lit pas le coût du
    modèle intact, et n'y écrit pas le sien."""
    faits = []
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    memoire_isolee.memoriser(("essai",), _compteur(faits, "intact", 1.0))
    with memoire_isolee.modele_modifie():
        assert memoire_isolee.memoriser(("essai",), _compteur(faits, "remplacé", 2.0)) == 2.0
        with pytest.raises(memoire_isolee.Absent), memoire_isolee.lecture_seule():
            memoire_isolee.memoriser(("essai",), _compteur(faits, "remplacé", 2.0))
    assert memoire_isolee.memoriser(("essai",), _compteur(faits, "intact", 1.0)) == 1.0
    assert faits == ["intact", "remplacé"]


def test_les_contextes_qui_remplacent_le_modele_font_taire_la_memoire():
    import proposition_prospective

    assert memoire._active()
    with proposition_prospective.PropositionProspective():
        assert not memoire._active()
    assert memoire._active()


def test_un_test_qui_remplace_quelque_chose_n_a_pas_de_memoire(monkeypatch):
    """``tests/conftest.py`` fait taire la mémoire sous ``monkeypatch``."""
    assert not memoire._active()


def test_la_memoire_ne_garde_que_les_empreintes_recentes(monkeypatch, memoire_isolee):
    for rang in range(memoire_isolee.EMPREINTES_GARDEES + 2):
        monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})
        monkeypatch.setattr(memoire_isolee, "empreinte", lambda rang=rang: f"e{rang}")
        memoire_isolee.memoriser(("essai",), lambda: 1.0)
        os.utime(memoire_isolee.DOSSIER / f"e{rang}", (1000 + rang, 1000 + rang))
    restent = sorted(d.name for d in memoire_isolee.DOSSIER.iterdir())
    assert restent == sorted(f"e{rang}"
                             for rang in range(2, memoire_isolee.EMPREINTES_GARDEES + 2))


def test_un_calcul_ne_se_fait_qu_une_fois_a_la_fois(monkeypatch, memoire_isolee):
    """Deux demandeurs du même calcul en même temps — deux workers, deux
    sessions : le second attend le premier, puis relit son calcul."""
    import threading
    import time

    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    faits, rendus = [], []
    commence = threading.Event()

    def calcul():
        faits.append("lent")
        commence.set()
        time.sleep(0.5)
        return 42.0

    def demander():
        rendus.append(memoire_isolee.memoriser(("essai", 7), calcul))

    premier = threading.Thread(target=demander)
    premier.start()
    commence.wait(10)
    monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})     # un autre processus
    demander()
    premier.join()
    assert faits == ["lent"]
    assert rendus == [42.0, 42.0]


def test_un_verrou_qui_ne_se_leve_pas_n_empeche_pas_de_calculer(monkeypatch, memoire_isolee):
    """Au-delà de l'attente permise, chacun calcule pour soi, comme avant."""
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    monkeypatch.setattr(memoire_isolee, "ATTENTE_MAX", 0.3)
    nom_ = memoire_isolee.nom(("essai", 8))
    dossier = memoire_isolee.DOSSIER / "e1"
    dossier.mkdir(parents=True)
    tenu = os.open(dossier / f".{nom_}.verrou", os.O_RDWR | os.O_CREAT)
    try:
        assert memoire_isolee._verrouiller(tenu)
        assert memoire_isolee.memoriser(("essai", 8), lambda: 8.0) == 8.0
    finally:
        memoire_isolee._deverrouiller(tenu)
        os.close(tenu)


def test_un_calcul_ecrit_hors_du_modele_se_garde_sous_son_code(
        monkeypatch, memoire_isolee, tmp_path):
    """Un calcul écrit dans un test ou un script — ici par
    ``outils_portage.moitie_python`` — porte son code dans sa clé : un même
    calcul ne se refait pas ; un autre argument, son fichier récrit ou un
    fichier qu'il importe à côté de lui le refont ; retouché depuis le
    chargement du modèle, il se fait sans mémoire. Un calcul du modèle n'en
    porte pas : l'empreinte le couvre."""
    import time

    import retraite_notionnelle
    from outils_portage import moitie_python

    monkeypatch.setattr(memoire_isolee, "_code_hors_du_modele", _CODE_HORS_DU_MODELE)
    monkeypatch.setattr(memoire_isolee, "empreinte", lambda: "e1")
    monkeypatch.setattr(retraite_notionnelle, "CHARGE_A", time.time() + 3600)
    fichier, voisin = tmp_path / "test_factice.py", tmp_path / "outils_factices.py"
    voisin.write_text("TAUX = 2\n", encoding="utf-8")
    faits = []

    def charger(texte: str):
        fichier.write_text(texte, encoding="utf-8")
        espace = {"__name__": "test_factice", "FAITS": faits}
        exec(compile(texte, str(fichier), "exec"), espace)
        return espace["calcul"]

    texte = ("def calcul(x):\n    if False:\n        import outils_factices\n"
             "    FAITS.append(x)\n    return [x]\n")
    calcul = charger(texte)
    assert moitie_python(calcul, 1) == [1]
    monkeypatch.setattr(memoire_isolee, "_EN_MEMOIRE", {})     # un autre processus
    assert moitie_python(calcul, 1) == [1]
    assert faits == [1]
    moitie_python(calcul, 2)
    assert faits == [1, 2]
    voisin.write_text("TAUX = 3\n", encoding="utf-8")            # ce qu'il importe
    moitie_python(calcul, 1)
    assert faits == [1, 2, 1]
    calcul = charger(texte + "# retouché\n")                     # son propre texte
    moitie_python(calcul, 1)
    assert faits == [1, 2, 1, 1]
    monkeypatch.setattr(retraite_notionnelle, "CHARGE_A", 0.0)  # retouché depuis le chargement
    moitie_python(calcul, 3)
    moitie_python(calcul, 3)
    assert faits == [1, 2, 1, 1, 3, 3]
    assert memoire_isolee._code_hors_du_modele(memoire_isolee.nom) == ()


def test_aucun_calcul_garde_ne_lit_ce_que_l_empreinte_ignore():
    """L'empreinte de la mémoire ignore ce qu'aucun calcul gardé ne lit
    (``memoire.HORS_DU_MODELE``) : deux simulations par statut, le coût agrégé
    et les avantages, relevés dans un processus neuf, n'en ouvrent, n'en
    listent ni n'en chargent rien. Le relevé prend une minute ; il se garde
    sous l'empreinte du modèle et ne se refait que quand celui-ci bouge."""
    import lectures_du_modele

    releve = memoire.memoriser(("lectures_du_modele",), lectures_du_modele.relever)
    assert len(releve["lus"]) > 100
    assert any(c.startswith("data/reference/regimes/") for c in releve["lus"])
    hors = [c for cle in ("lus", "listes", "modules") for c in releve[cle]
            if lectures_du_modele.hors_du_modele(c)]
    assert not hors, f"lu par un calcul gardé, et pourtant hors de l'empreinte : {hors}"


def test_les_worktrees_partagent_la_memoire_du_depot_principal(tmp_path):
    """La clé et l'empreinte disent tout d'un calcul : un worktree neuf relit
    ce que le dépôt principal, ou un autre worktree, a déjà calculé."""
    depot = tmp_path / "depot"
    subprocess.run(["git", "init", "-q", str(depot)], check=True)
    subprocess.run(["git", "-C", str(depot), "-c", "user.name=Essai",
                    "-c", "user.email=essai@exemple.fr", "commit", "-q",
                    "--allow-empty", "-m", "amorce"], check=True)
    branche = tmp_path / "ailleurs" / "branche"
    subprocess.run(["git", "-C", str(depot), "worktree", "add", "-q", "--detach",
                    str(branche)], check=True)
    attendu = (depot / ".cache" / "calculs").resolve()
    assert memoire.dossier_commun(depot).resolve() == attendu
    assert memoire.dossier_commun(branche).resolve() == attendu
    seul = tmp_path / "seul"
    seul.mkdir()
    assert memoire.dossier_commun(seul) == seul / ".cache" / "calculs"


def test_l_empreinte_suit_les_sources_que_git_voit(monkeypatch, memoire_isolee, tmp_path):
    """Un fichier suivi, ou nouveau, change l'empreinte ; ce que git ignore, ou
    ce qu'aucun calcul ne lit, ne la change pas. Hors d'un dépôt, pas
    d'empreinte, et rien ne se garde."""
    depot = tmp_path / "depot"
    (depot / "src").mkdir(parents=True)
    (depot / "data" / "brut").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(depot)], check=True)
    (depot / ".gitignore").write_text("data/brut/*\n", encoding="utf-8")
    (depot / "src" / "modele.py").write_text("TAUX = 1\n", encoding="utf-8")
    monkeypatch.setattr(memoire_isolee, "RACINE_PROJET", depot)
    premiere = memoire_isolee.empreinte()
    assert premiere
    (depot / "data" / "brut" / "gros.csv").write_text("ignoré", encoding="utf-8")
    assert memoire_isolee.empreinte() == premiere
    for chemin in ("scripts/outil.py", "data/reference/legislation/journal_de_veille/e.yaml",
                   "data/sources.yaml", "data/CLAUDE.md"):
        (depot / chemin).parent.mkdir(parents=True, exist_ok=True)
        (depot / chemin).write_text("hors du modèle", encoding="utf-8")
    assert memoire_isolee.empreinte() == premiere
    (depot / "data" / "reference" / "regimes").mkdir(parents=True)
    (depot / "data" / "reference" / "regimes" / "r.yaml").write_text("taux: 1\n", encoding="utf-8")
    assert memoire_isolee.empreinte() != premiere
    (depot / "src" / "modele.py").write_text("TAUX = 2\n", encoding="utf-8")
    assert memoire_isolee.empreinte() != premiere
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    monkeypatch.setattr(memoire_isolee, "RACINE_PROJET", ailleurs)
    assert memoire_isolee.empreinte() is None


def test_une_option_par_defaut_ecrite_ou_non_est_le_meme_cout(monkeypatch, memoire_isolee):
    """La clé du coût porte chaque option avec son défaut : « convention_recette »
    écrite ou non, c'est le même calcul ; une option inconnue est refusée."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.cout import CONVENTION_ASSIETTE

    cles = []
    monkeypatch.setattr(memoire_isolee, "memoriser",
                        lambda cle, calcul: cles.append(memoire_isolee.nom(cle)))
    memoire_isolee.cout(Parametres())
    memoire_isolee.cout(Parametres(), convention_recette=CONVENTION_ASSIETTE)
    memoire_isolee.cout(Parametres(), comptes=False)
    assert cles[0] == cles[1] != cles[2]
    with pytest.raises(TypeError, match="options inconnues"):
        memoire_isolee.cout(Parametres(), assiete=False)


def test_le_contexte_du_site_lit_ses_couts_dans_la_memoire(monkeypatch, memoire_isolee):
    """La page Coût, les affirmations et le paquet lisent le coût du contexte :
    c'est celui que la mémoire garde, sous les règles du contexte, dérivé ou non."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.contexte import Contexte

    demandes = []
    monkeypatch.setattr(memoire_isolee, "cout", lambda p: demandes.append(("cout", p)) or "c")
    monkeypatch.setattr(memoire_isolee, "avantages",
                        lambda p: demandes.append(("avantages", p)) or "a")
    contexte = Contexte()
    assert (contexte.cout(), contexte.avantages(), contexte.cout()) == ("c", "a", "c")
    derive = Parametres(taux_cotisation_liberal=0.2)
    assert contexte.pour(derive).cout() == "c"
    assert demandes == [("cout", contexte.base), ("avantages", contexte.base),
                        ("cout", derive)]


# -- l'instantané des données ---------------------------------------------------


def _table(chemin: Path, valeur: str) -> None:
    chemin.write_text(f"cle,annee,valeur,fiabilite\nx,2000,{valeur},haute\n",
                      encoding="utf-8")


def test_un_instantane_voit_les_donnees_de_son_debut(tmp_path):
    """Dans un instantané, un chargeur ne regarde le disque qu'une fois ; le
    calcul suivant relit ce qui a changé."""
    from retraite_notionnelle.donnees import chargement

    chemin = tmp_path / "table.csv"
    _table(chemin, "1.0")

    def lire():
        return chargement.charger_table_csv(chemin, ("cle", "annee"), "valeur")[0][("x", "2000")]

    with chargement.instantane():
        assert lire() == 1.0
        _table(chemin, "2.50")
        assert lire() == 1.0
        with chargement.instantane():            # imbriqué : celui du dehors
            assert lire() == 1.0
    assert lire() == 2.5


def test_un_instantane_ne_vaut_que_pour_son_fil(tmp_path):
    from concurrent.futures import ThreadPoolExecutor as Fils
    from retraite_notionnelle.donnees import chargement

    chemin = tmp_path / "table.csv"
    _table(chemin, "1.0")

    def lire():
        return chargement.charger_table_csv(chemin, ("cle", "annee"), "valeur")[0][("x", "2000")]

    with chargement.instantane():
        assert lire() == 1.0
        _table(chemin, "2.50")
        with Fils(1) as fil:
            assert fil.submit(lire).result() == 2.5
        assert lire() == 1.0


def test_un_chargeur_garde_sous_instantane_s_appelle_comme_avant_hors_de_lui():
    """Des arguments qui ne se hachent pas, ou nommés : l'appel passe tel quel."""
    from retraite_notionnelle.donnees import chargement

    appels = []

    @chargement.une_fois_par_instantane
    def chargeur(*args, **kwargs):
        appels.append((args, kwargs))
        return len(appels)

    assert chargeur(1) == 1 and chargeur(1) == 2            # hors d'un instantané
    with chargement.instantane():
        assert chargeur(1) == 3 and chargeur(1) == 3
        assert chargeur([1]) == 4 and chargeur([1]) == 5    # ne se hache pas
        assert chargeur(1, nom=2) == 6 and chargeur(1, nom=2) == 7
    assert chargeur(1) == 8


# -- le précalcul des chiffres ancrés -------------------------------------------


def _factices(monkeypatch) -> list[tuple]:
    """Deux calculs « lourds » qui se comptent et se gardent comme les vrais,
    et des mesures qui les lisent. Rend la liste des calculs faits."""
    faits = []

    def lourd_a(x):
        return memoire.memoriser(("factice_a", x),
                                 lambda: (faits.append(("a", x)), float(x) * 10)[1])

    def lourd_b():
        return memoire.memoriser(("factice_b",), lambda: (faits.append(("b",)), 10.0)[1])

    def qui_rattrape(**_):
        # Une mesure qui rattrape ses erreurs ne prend pas l'attente du
        # précalcul pour une réponse.
        try:
            return mesures_prose._lourd("_lourd_b")
        except Exception:        # noqa: BLE001
            return -1.0

    monkeypatch.setattr(mesures_prose, "_lourd_a", lourd_a, raising=False)
    monkeypatch.setattr(mesures_prose, "_lourd_b", lourd_b, raising=False)
    monkeypatch.setattr(mesures_prose, "MESURES", {
        "simple": lambda **r: float(r["n"]),
        "avec_a": lambda **r: mesures_prose._lourd("_lourd_a", r["x"]) * 2,
        "avec_deux": lambda **_: (mesures_prose._lourd("_lourd_a", "1")
                                  + mesures_prose._lourd("_lourd_b")),
        "qui_rattrape": qui_rattrape,
    })
    monkeypatch.setattr(mesures_prose, "_FAITS", {})
    monkeypatch.setattr(memoire, "empreinte", lambda: "e1")
    return faits


def test_une_campagne_fait_chaque_calcul_lourd_une_fois_et_d_avance(monkeypatch,
                                                                    memoire_isolee):
    """Les calculs lourds se découvrent et se font avant que le contrôle ne
    demande la première mesure ; une mesure qui en attend deux les a tous les
    deux, et aucune ne se calcule deux fois."""
    faits = _factices(monkeypatch)
    arguments = ["simple?n=4", "avec_a?x=1", "avec_a?x=2", "avec_deux", "qui_rattrape",
                 "avec_a?x=1"]
    with ThreadPoolExecutor(2) as pool, mesures_prose.campagne(arguments, pool):
        assert sorted(faits) == [("a", "1"), ("a", "2"), ("b",)]
        valeurs = [mesures_prose.mesurer(a) for a in arguments]
    assert valeurs == [4.0, 20.0, 40.0, 20.0, 10.0, 20.0]
    assert len(faits) == 3
    assert mesures_prose._VALEURS is None
    assert len(list((memoire_isolee.DOSSIER / "e1").glob("*.pickle"))) == 3


def test_ce_que_la_memoire_garde_ne_passe_pas_par_le_precalcul(monkeypatch, memoire_isolee):
    """Un calcul gardé se relit ici : le précalcul ne lance un processus que
    pour ce qui manque."""
    faits = _factices(monkeypatch)
    memoire.memoriser(("factice_b",), lambda: 10.0)
    soumis = []

    class Executeur(ThreadPoolExecutor):
        def submit(self, fonction, *arguments):
            soumis.append(arguments)
            return super().submit(fonction, *arguments)

    with Executeur(2) as pool, mesures_prose.campagne(["avec_deux"], pool):
        assert mesures_prose.mesurer("avec_deux") == 20.0
    assert soumis == [("_lourd_a", ("1",))]
    assert faits == [("a", "1")]


def test_un_calcul_qui_echoue_se_dit_a_la_demande(monkeypatch, memoire_isolee):
    """Le précalcul n'échoue jamais : la mesure en faute le dit quand le
    contrôle la demande, avec l'erreur du modèle, et les autres répondent."""
    _factices(monkeypatch)

    def casse():
        raise ValueError("modèle cassé")

    monkeypatch.setattr(mesures_prose, "_lourd_b",
                        lambda: memoire.memoriser(("factice_b",), casse))
    with ThreadPoolExecutor(2) as pool, \
            mesures_prose.campagne(["avec_deux", "simple?n=1"], pool):
        with pytest.raises(ValueError, match="modèle cassé"):
            mesures_prose.mesurer("avec_deux")
        assert mesures_prose.mesurer("simple?n=1") == 1.0


def test_un_processus_du_precalcul_retrouve_les_mesures():
    """Le précalcul lance ses processus à neuf (``spawn``) : ils retrouvent ce
    module, y calculent par son nom, et rendent ce qu'ils ont calculé."""
    with ProcessPoolExecutor(1, mp_context=multiprocessing.get_context("spawn")) as pool:
        rendu = pool.submit(mesures_prose._executer, "_parametres", ("", "", "")).result(
            timeout=300)
    assert rendu == mesures_prose._parametres("", "", "")


def test_le_controle_de_la_prose_ouvre_une_campagne_de_ses_mesures(monkeypatch, tmp_path):
    """Le contrôle passe à la campagne les mesures que les documents citent,
    hors des blocs de code, puis corrige ce qui a dérivé."""

    class Mesures:
        campagnes: list[list[str]] = []

        @contextmanager
        def campagne(self, arguments):
            self.campagnes.append(list(arguments))
            yield

        def mesurer(self, argument):
            return 12.0

    mesures = Mesures()
    monkeypatch.setattr(verifier_prose, "_mesures", lambda: mesures)
    monkeypatch.setattr(verifier_prose, "RACINE", tmp_path)
    (tmp_path / "doc.md").write_text(
        "# Doc\n\nIl en reste <!--chiffre:mesure(reste?n=1)-->11<!--/--> %.\n\n"
        "```\n<!--chiffre:mesure(cite)-->3<!--/-->\n```\n", encoding="utf-8")
    zonage = verifier_prose.Zonage({"fichiers": {"doc.md": {"defaut": "recit"}}})
    anomalies, reecrits = verifier_prose.controler(zonage, corriger=True)
    assert mesures.campagnes == [["reste?n=1"]]
    assert reecrits == ["doc.md"]
    assert "-->12<!--/--> %" in (tmp_path / "doc.md").read_text(encoding="utf-8")
    assert [a.genre for a in anomalies] == ["derive"]
