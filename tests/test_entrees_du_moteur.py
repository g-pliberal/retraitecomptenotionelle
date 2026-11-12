"""Ce qui entre encore dans le moteur Python d'une carrière depuis la fabrique.

Le moteur d'une carrière n'aura qu'un exemplaire, en JavaScript (action 161) :
son jumeau Python part quand plus rien n'y entre. La fabrique — les scripts
que ``scripts/regenerer.py`` lance à chaque envoi — y entrait par trois
scripts à l'inventaire du 9 novembre 2026 ; ce fichier tient la liste de ce
qui y entre encore, relevée par ``scripts/entrees_du_moteur.py`` en faisant
tourner chaque étape, et la liste ne peut que décroître : une entrée de plus
rougit, une entrée déclarée qui n'entre plus aussi.
"""

from __future__ import annotations

import shutil
import sys
import textwrap
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import entrees_du_moteur  # noqa: E402
import regenerer  # noqa: E402

#: Les deux exemples du README : ``construire_tableaux_md.py`` les écrit par
#: ``Comparaison.tableau()``, une mise en forme qui n'existe qu'en Python, et
#: bâtit et simule donc encore leur carrière au moteur Python. Ce que le § 3
#: du README doit montrer quand ce moteur part est une question laissée au
#: propriétaire (``docs/feuille_de_route/161/2026-11-12-lot-a-les-sondes-par-le-pont.md``).
EXEMPLES_DU_README = {
    "scripts/construire_tableaux_md.py": (
        "simulateur.py:Simulateur.carriere_simple", "simulateur.py:Simulateur.simuler"),
}

#: Par étape de la fabrique, sous le nom de son script, ce qui entre encore
#: dans le moteur Python d'une carrière : le fichier qui appelle, et chaque
#: règle du moteur qu'il appelle du dehors (``entrees_du_moteur.relever``).
#: Une étape sans entrée ne porte rien. La liste ne fait que décroître : une
#: entrée s'en retire dans le commit qui fait passer son appelant par le pont
#: (``retraite_notionnelle.pont``), et aucune ne s'y ajoute — un calcul neuf
#: sur une carrière se demande au portage.
ENTREES_DE_LA_FABRIQUE: dict[str, dict[str, tuple[str, ...]]] = {
    "construire_inventaire.py": {},
    "construire_regimes_md.py": {},
    # Le chargeur des âges de référence, que le paquet écrit : il passe sous
    # ``donnees/`` au retrait de son jumeau (note de décision 0006).
    "construire_donnees.py": {
        "scripts/construire_donnees.py": ("moteur/age_reference.py:_charger_ages",)},
    "mesures_accueil.py": {},
    "construire_temoins.py": {},
    "construire_pages.py": {},
    "chiffrage_plf.py": {},
    "construire_tableaux_md.py": EXEMPLES_DU_README,
    "tableau_de_bord.py": {},
    # Les sondes de la prose : leurs carrières se bâtissent et se simulent au
    # portage, leurs règles s'y appellent une à une (``pont.droit``,
    # ``tests/test_sondes_par_le_pont.py``), l'étude de la mortalité comprise,
    # dont une sonde lit la mesure (``tests/test_mortalite_population.py``).
    "verifier_prose.py": {},
    "conservation.py": {},
}


def _sans_node() -> bool:
    return shutil.which("node") is None


@pytest.fixture(params=[False, True], ids=["surveillance", "trace"])
def par_trace(request) -> bool:
    """Les deux façons dont la sonde relève : par ``sys.monitoring``, là où il
    existe, et par ``sys.settrace``, la seule sous Python 3.11, que GitHub
    lance — où les deux cas prennent donc la seconde. Le relevé est le même."""
    return request.param


def test_la_sonde_ne_retient_que_ce_qui_entre_du_dehors(tmp_path, par_trace):
    """Un script qui bâtit une carrière et la simule entre dans le moteur
    Python par deux portes, ``carriere_simple`` et ``simuler`` : la sonde les
    retient sous le nom du fichier qui appelle, et rien d'autre — ni le
    simulateur qui charge ses données, ni les règles que la simulation fait
    tourner à l'intérieur du moteur."""
    script = tmp_path / "essai.py"
    script.write_text(textwrap.dedent('''\
        from retraite_notionnelle.simulateur import Simulateur

        simulateur = Simulateur()
        simulateur.macro
        carriere = simulateur.carriere_simple(
            annee_naissance=1970, sexe="F", affiliation="salarie_prive_non_cadre",
            age_debut=22, age_liquidation=64)
        simulateur.simuler(carriere)
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script, par_trace=par_trace) == {"essai.py": [
        "simulateur.py:Simulateur.carriere_simple", "simulateur.py:Simulateur.simuler"]}


def test_la_sonde_nomme_le_module_du_modele_qui_entre_pour_le_script(tmp_path, par_trace):
    """Un cas type qui bâtit sa carrière en Python (``CasType.construire``)
    demande son âge au pilote, puis sa carrière au simulateur : le script n'a
    nommé aucune fonction du moteur, et la sonde dit que ``castypes.py`` y
    entre pour lui, par ces deux portes."""
    script = tmp_path / "essai.py"
    script.write_text(textwrap.dedent('''\
        from retraite_notionnelle.castypes import CAS_TYPES
        from retraite_notionnelle.simulateur import Simulateur

        CAS_TYPES[0].construire(Simulateur(), 1970)
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script, par_trace=par_trace) == {
        "src/retraite_notionnelle/castypes.py": [
            "pilote.py:age_de_depart", "simulateur.py:Simulateur.carriere_simple"]}


def test_la_sonde_retient_les_regles_des_fichiers_meles_declarees_portes(tmp_path, par_trace):
    """Dans un fichier où le moteur se mêle aux chargeurs et aux types, une
    règle appelée directement ne se relève que déclarée porte : le salaire
    moyen d'une année, le partage de la restitution et la fiche de paie d'une
    simulation, que les sondes de la prose appelaient, le sont."""
    script = tmp_path / "essai.py"
    script.write_text(textwrap.dedent('''\
        from retraite_notionnelle.carriere import salaire_moyen_annuel
        from retraite_notionnelle.restitution import Restitution
        from retraite_notionnelle.simulateur import Simulateur

        simulateur = Simulateur()
        salaire_moyen_annuel(simulateur.macro, 2024)
        Restitution(simulateur.parametres.racine_donnees).part_du_poste(2024)
        carriere = simulateur.carriere_simple(
            annee_naissance=1980, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=22, age_liquidation=64)
        simulateur.simuler(carriere).remuneration.reference.gain_net
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script, par_trace=par_trace) == {"essai.py": [
        "carriere.py:salaire_moyen_annuel",
        "remuneration.py:AnneeComparee.gain_net", "remuneration.py:RemunerationActif.reference",
        "restitution.py:Restitution.part_du_poste",
        "simulateur.py:Simulateur.carriere_simple", "simulateur.py:Simulateur.simuler"]}


def test_la_sonde_ne_releve_pas_ce_que_fait_un_calcul_garde(tmp_path, par_trace):
    """Un calcul que la mémoire des calculs garde (``memoire.memoriser``) ne
    se refait pas quand il est déjà fait : ce qu'il appelle du moteur ne se
    relève pas, mémoire pleine ou vide, et le relevé ne dépend pas d'elle. La
    carrière bâtie hors de lui entre, la simulation gardée non."""
    script = tmp_path / "essai.py"
    script.write_text(textwrap.dedent('''\
        from retraite_notionnelle import memoire
        from retraite_notionnelle.simulateur import Simulateur

        simulateur = Simulateur()
        carriere = simulateur.carriere_simple(
            annee_naissance=1970, sexe="F", affiliation="salarie_prive_non_cadre",
            age_debut=22, age_liquidation=64)
        memoire.memoriser(("essai", "entrees_du_moteur"),
                          lambda: simulateur.simuler(carriere).actuel.pension_annuelle)
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script, par_trace=par_trace) == {"essai.py": [
        "simulateur.py:Simulateur.carriere_simple"]}


def test_chaque_etape_de_la_fabrique_declare_ses_entrees():
    """Une étape de plus dans ``regenerer.py`` déclare ce qui entre par elle
    dans le moteur Python, fût-ce rien ; une étape partie s'en retire."""
    assert set(ENTREES_DE_LA_FABRIQUE) == {etape.script for etape in regenerer.etapes()}


@pytest.mark.parametrize("script", sorted(ENTREES_DE_LA_FABRIQUE))
def test_la_fabrique_n_entre_dans_le_moteur_python_que_par_sa_liste(script):
    """Chaque étape de la fabrique, lancée sans rien écrire sous la sonde,
    n'entre dans le moteur Python d'une carrière que par ce que la liste
    déclare (:data:`ENTREES_DE_LA_FABRIQUE`), et par tout ce qu'elle déclare :
    une entrée de plus se demande au pont, une entrée qui n'est plus se retire
    de la liste (action 161, lot A)."""
    if _sans_node():
        pytest.skip("node absent : la fabrique ne tourne pas sans lui")
    etape = next(etape for etape in regenerer.etapes() if etape.script == script)
    relevees = entrees_du_moteur.relever(RACINE / "scripts" / script, etape.verifier)
    declarees = {appelant: sorted(entrees)
                 for appelant, entrees in ENTREES_DE_LA_FABRIQUE[script].items()}
    assert relevees == declarees, (
        f"{script} : ce qui entre dans le moteur Python n'est plus ce que la liste déclare — "
        "une entrée de plus se demande au pont (retraite_notionnelle.pont), une entrée "
        "partie se retire de ENTREES_DE_LA_FABRIQUE")
