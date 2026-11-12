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

#: Les deux exemples du README, que ``construire_tableaux_md.py`` demande aux
#: sondes de la prose (``mesures_prose._comparaison_de``) : elles bâtissent et
#: simulent encore leur carrière en Python, et le titre du second lit l'écart
#: à l'âge de référence sur ce qu'elles rendent. La ligne suivante du lot A.
EXEMPLES_DU_README = {
    "scripts/construire_tableaux_md.py": (
        "moteur/age_reference.py:EcartAge.anticipe", "moteur/age_reference.py:EcartAge.ecart"),
    "scripts/mesures_prose.py": (
        "simulateur.py:Simulateur.carriere_simple", "simulateur.py:Simulateur.simuler"),
}

#: Ce que les sondes de la prose appellent encore du moteur Python quand
#: ``verifier_prose.py`` les lance toutes : leurs carrières bâties et simulées,
#: et les règles qu'elles appellent une à une ; une étude de la mortalité, qui
#: simule ; les cas types, qui datent et bâtissent leur carrière en Python
#: pour une sonde. La ligne suivante du lot A.
SONDES_DE_LA_PROSE = {
    "scripts/mesures_prose.py": (
        "droit/liquider.py:salaire_de_reference",
        "moteur/age_reference.py:AgeReference.age",
        "moteur/capitalisation.py:Capitalisation.annees_cotisees",
        "moteur/capitalisation.py:Capitalisation.rente_mensuelle",
        "moteur/capitalisation.py:ConstructeurCapitalisation.__init__",
        "moteur/capitalisation.py:ConstructeurCapitalisation._facteur_encours_rente",
        "moteur/capitalisation.py:ConstructeurCapitalisation.construire",
        "moteur/compte.py:ConstructeurCompte.parts_retraite_seule",
        "moteur/conversion.py:Convertisseur.__init__",
        "moteur/conversion.py:Convertisseur.coefficient",
        "moteur/conversion.py:Convertisseur.effet_anticipation",
        "moteur/fusion.py:_taux_total",
        "moteur/fusion.py:fusionner",
        "moteur/indexation.py:Indexation.__init__",
        "moteur/indexation.py:Indexation.coefficient",
        "scenarios/notionnel.py:ScenarioNotionnel._garantie_vieillesse",
        "simulateur.py:Simulateur.carriere_simple",
        "simulateur.py:Simulateur.simuler"),
    "scripts/mortalite_population.py": ("simulateur.py:Simulateur.simuler",),
    "src/retraite_notionnelle/castypes.py": (
        "moteur/conversion.py:niveau_relatif", "pilote.py:age_de_depart",
        "simulateur.py:Simulateur.carriere_simple"),
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
    # Le solde de la fusion des régimes, que l'accueil cite : une étude du
    # lot B.
    "mesures_accueil.py": {"scripts/solde_fusion.py": ("moteur/fusion.py:fusionner",)},
    "construire_temoins.py": {},
    "construire_pages.py": {},
    "chiffrage_plf.py": {},
    "construire_tableaux_md.py": EXEMPLES_DU_README,
    "tableau_de_bord.py": {},
    "verifier_prose.py": SONDES_DE_LA_PROSE,
    "conservation.py": {},
}


def _sans_node() -> bool:
    return shutil.which("node") is None


def test_la_sonde_ne_retient_que_ce_qui_entre_du_dehors(tmp_path):
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
    assert entrees_du_moteur.relever(script) == {"essai.py": [
        "simulateur.py:Simulateur.carriere_simple", "simulateur.py:Simulateur.simuler"]}


def test_la_sonde_nomme_le_module_du_modele_qui_entre_pour_le_script(tmp_path):
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
    assert entrees_du_moteur.relever(script) == {"src/retraite_notionnelle/castypes.py": [
        "pilote.py:age_de_depart", "simulateur.py:Simulateur.carriere_simple"]}


def test_la_sonde_ne_releve_pas_ce_que_fait_un_calcul_garde(tmp_path):
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
    assert entrees_du_moteur.relever(script) == {"essai.py": [
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
