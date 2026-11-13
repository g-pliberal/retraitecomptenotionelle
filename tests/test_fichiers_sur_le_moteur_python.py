"""La liste, décroissante, des fichiers de tests qui exécutent encore une règle
du moteur Python (action 161, note de décision 0007).

Les tests du moteur passent au moteur JavaScript, par la façade
(``tests/facade.py``) ou par le pont, puis le jumeau Python part. Ce fichier
tient le compte de ce qui reste : un fichier de tests qui entre dans le moteur
Python y est nommé, et la liste ne fait que décroître. Un fichier qui naît n'y
entre pas : il éprouve le portage. Un fichier qui n'y entre plus s'en retire,
dans le commit qui l'a porté.

« Entrer dans le moteur Python » se lit dans les imports, sans rien lancer : le
fichier importe, des fichiers de règles — ``droit/``, ``moteur/``,
``scenarios/``, ``echeancier.py``, ``journal.py``, ``pilote.py`` — ou de ceux
qui tiennent les entrées de la façade — ``simulateur.py``, ``carriere.py`` —,
un module, une fonction, une classe qui n'est pas un type de données, ou l'une
des entrées elles-mêmes (``Simulateur``, ``ScenarioActuel``, ``Carriere``,
``reversion``). Un type de données — un dataclass, une énumération : ``Metier``,
``PensionRegime``, ``Comparaison`` —, que le pont échange, et une constante
n'y font pas entrer. La liste ne voit pas ce qu'un fichier atteint par un
outil commun (``tests/outils_pont.py``) ou par un script qu'il lance.
"""

from __future__ import annotations

import ast
import dataclasses
import enum
import importlib
import types
from pathlib import Path

#: Les fichiers de règles du moteur Python, et ceux qui tiennent les entrées
#: de la façade.
MOTEUR_PYTHON = ("retraite_notionnelle.droit", "retraite_notionnelle.moteur",
                 "retraite_notionnelle.scenarios", "retraite_notionnelle.echeancier",
                 "retraite_notionnelle.journal", "retraite_notionnelle.pilote",
                 "retraite_notionnelle.simulateur", "retraite_notionnelle.carriere")

#: Les entrées du moteur Python, que la façade sert sous les mêmes noms : les
#: importer du moteur y fait entrer, types de données ou non.
ENTREES = frozenset({"Simulateur", "ScenarioActuel", "Carriere", "reversion"})

#: Les fichiers de tests qui entrent encore dans le moteur Python. Elle ne fait
#: que décroître.
FICHIERS = (
    "test_affirmations.py", "test_age_conjoncturel.py", "test_ages_au_mois.py",
    "test_agirc_arrco_au_droit.py", "test_avantages.py", "test_bonifications_emplois.py",
    "test_caisses_du_pacifique.py", "test_capitalisation.py", "test_chomage_complementaires.py",
    "test_chronologie.py", "test_cnav_baremes.py", "test_cnav_exposes.py", "test_cnracl.py",
    "test_coefficients_agirc_1947.py", "test_contributions_equilibre.py",
    "test_controle_drees_panorama.py", "test_coupures_au_mois.py", "test_cout.py",
    "test_cout_age_depart.py", "test_cultes.py", "test_cultes_au_droit.py",
    "test_cultes_smic_du_mois.py", "test_cumul_activites.py", "test_cycle_de_vie_portage.py",
    "test_cycle_de_vie_references.py", "test_cycle_de_vie_script.py",
    "test_decompte_des_services.py", "test_departs.py", "test_destinie.py",
    "test_diviseur_exemples_officiels.py", "test_donnees.py", "test_droit.py",
    "test_droits_contrefactuels.py", "test_duree_lue_a_soixante_ans.py", "test_effet_retour.py",
    "test_emploi_retraite.py", "test_estimation_du_site.py", "test_estimation_officielle.py",
    "test_etranger.py", "test_exonerations_agirc_arrco.py", "test_facade.py",
    "test_facade_jumeau.py", "test_facteurs_depense.py", "test_fiche_date_d_entree.py",
    "test_fiche_des_liberaux.py", "test_flux_fonction_publique.py",
    "test_fonction_publique_etat.py", "test_garantie_degressive.py", "test_garantie_par_sexe.py",
    "test_grille_large.py", "test_ieg.py", "test_indemnite_csg.py", "test_independants.py",
    "test_indexation_programme.py", "test_ines.py", "test_interpenetration.py",
    "test_invalidite.py", "test_ircantec_minoration.py", "test_ircec_auteurs.py",
    "test_lectures_decision_29.py", "test_limite_age.py", "test_liquidation.py", "test_lodeom.py",
    "test_majoration_conjoint_a_charge.py", "test_majoration_enfants_a_charge.py",
    "test_majoration_enfants_agirc_1994_a_1996.py", "test_majoration_exceptionnelle.py",
    "test_marins.py", "test_mayotte.py", "test_micro_social.py", "test_mines.py",
    "test_minima_agricoles.py", "test_minimum_pension_sncf.py", "test_mortalite_population.py",
    "test_moteur.py", "test_oracle.py", "test_oracle_carriere_longue_fonction_publique.py",
    "test_oracle_categorie_active.py", "test_oracle_enfants.py", "test_oracle_familles.py",
    "test_oracle_minima.py", "test_oracle_periodes_assimilees.py",
    "test_oracle_points_enfants_arrco.py", "test_oracle_salaire_annuel_moyen.py",
    "test_outillage.py", "test_outre_mer.py", "test_ouverture_des_liberaux.py",
    "test_ouverture_des_navigants.py", "test_parents_trois_enfants.py", "test_pcv_sante.py",
    "test_pension_maximale.py", "test_pension_minimum_avant_1983.py",
    "test_periodes_assimilees.py", "test_periodes_assimilees_exemples_officiels.py",
    "test_plafond_majoration_enfants.py", "test_pont.py", "test_prelevements_historiques.py",
    "test_primes_soumises_a_retenue.py", "test_priorite_enfants.py",
    "test_proposition_prospective.py", "test_rafp.py", "test_referents.py",
    "test_regle_de_chacun.py", "test_releve_lu.py", "test_releve_prolonge.py",
    "test_remuneration.py", "test_retablissement.py", "test_retour_crpcen_ieg.py",
    "test_retraite_progressive.py", "test_revalorisation.py", "test_revenu_des_points.py",
    "test_reversion.py", "test_salaire_annuel_moyen.py", "test_scenarios_meres.py",
    "test_sections_juridiques.py", "test_sections_liberales.py", "test_sections_sante.py",
    "test_services_fonction_publique.py", "test_services_passes.py", "test_simulateur.py",
    "test_sncf_ratp.py", "test_solde_fusion.py", "test_stock_age_legal.py", "test_taux_moyens.py",
    "test_taux_plein_a_soixante_cinq_ans.py", "test_taux_plein_par_categorie.py",
    "test_temps_partiel.py", "test_trajectoire.py", "test_trimestres_enfants.py",
    "test_trimestres_utiles.py", "test_univers.py", "test_versements_uniques.py",
    "test_versions.py", "test_web.py", "test_web_saisie.py",
)


#: Les fichiers passés à la façade (``from facade import …``) qui gardent des
#: tests sur le moteur Python, sous la marque ``sur_le_moteur_python``, et le
#: nombre de ces tests. Il ne fait que décroître.
RESTES = {"test_reversion.py": 6, "test_simulateur.py": 66}


def _du_moteur(module: str) -> bool:
    return any(module == racine or module.startswith(racine + ".") for racine in MOTEUR_PYTHON)


def entrees_dans_le_moteur(source: str) -> set[str]:
    """Ce que le code ``source`` importe du moteur Python et qui y fait entrer,
    où que l'import soit écrit : un module, une fonction, une classe qui n'est
    pas un type de données, une entrée de la façade."""
    trouvees = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Import):
            trouvees |= {alias.name for alias in noeud.names if _du_moteur(alias.name)}
        elif (isinstance(noeud, ast.ImportFrom) and noeud.level == 0
              and (noeud.module or "").split(".")[0] == "retraite_notionnelle"):
            module = importlib.import_module(noeud.module)
            for alias in noeud.names:
                objet = getattr(module, alias.name, None)
                if objet is None:
                    objet = importlib.import_module(f"{noeud.module}.{alias.name}")
                if isinstance(objet, types.ModuleType):
                    if _du_moteur(objet.__name__):
                        trouvees.add(objet.__name__)
                    continue
                origine = (objet.__module__ if isinstance(objet, (type, types.FunctionType))
                           else noeud.module)
                if not _du_moteur(origine):
                    continue
                type_de_donnees = isinstance(objet, type) and (
                    dataclasses.is_dataclass(objet) or issubclass(objet, enum.Enum))
                if alias.name in ENTREES or (callable(objet) and not type_de_donnees):
                    trouvees.add(f"{origine}.{alias.name}")
    return trouvees


def les_tests_marques(source: str) -> set[str]:
    """Les tests du code ``source`` qui portent la marque
    ``sur_le_moteur_python``."""
    return {noeud.name for noeud in ast.parse(source).body
            if isinstance(noeud, ast.FunctionDef) and noeud.name.startswith("test_")
            and any("sur_le_moteur_python" in ast.unparse(decorateur)
                    for decorateur in noeud.decorator_list)}


def les_tests_dans_le_moteur(source: str) -> dict[str, str]:
    """Les tests du code ``source`` qui entrent dans le moteur Python, et par
    quoi : un import que le test fait lui-même, un nom que le fichier importe
    du moteur, ou une aide, une fixture du fichier qui y entre. Comme la liste
    des fichiers, cela se lit dans le code, sans rien lancer : une méthode de
    règle appelée sur un type de données (``carriere.prolongee``) ne s'y voit
    pas."""
    arbre = ast.parse(source)
    du_fichier = {}
    for noeud in arbre.body:
        if isinstance(noeud, (ast.Import, ast.ImportFrom)):
            for alias in noeud.names:
                seul = ast.unparse(type(noeud)(**{**vars(noeud), "names": [alias]}))
                for entree in entrees_dans_le_moteur(seul):
                    du_fichier[(alias.asname or alias.name).split(".")[0]] = entree
    fonctions = {noeud.name: noeud for noeud in arbre.body if isinstance(noeud, ast.FunctionDef)}
    lus = {nom: {n.id for n in ast.walk(fonction) if isinstance(n, ast.Name)}
           | {argument.arg for argument in fonction.args.args}
           for nom, fonction in fonctions.items()}
    par = {}
    for nom, fonction in fonctions.items():
        imports = "\n".join(ast.unparse(n) for n in ast.walk(fonction)
                            if isinstance(n, (ast.Import, ast.ImportFrom)))
        entrees = sorted(entrees_dans_le_moteur(imports)
                         | {du_fichier[lu] for lu in lus[nom] if lu in du_fichier})
        if entrees:
            par[nom] = entrees[0]
    avance = True
    while avance:
        avance = False
        for nom in fonctions:
            aides = sorted(lu for lu in lus[nom] if lu in par and lu != nom)
            if nom not in par and aides:
                par[nom] = aides[0]
                avance = True
    return {nom: raison for nom, raison in par.items() if nom.startswith("test_")}


def test_ce_qui_fait_entrer_dans_le_moteur_python_se_lit_dans_les_imports():
    """Le simulateur, un module du droit, une fonction de règle et une table du
    moteur y font entrer ; un type de données, une constante, un chargeur de
    données et la façade, non."""
    assert entrees_dans_le_moteur(
        "from retraite_notionnelle import Parametres, pont\n"
        "from retraite_notionnelle.simulateur import Simulateur\n"
        "from retraite_notionnelle.droit import liquider\n"
        "def test():\n"
        "    from retraite_notionnelle.droit.reversion import Reversion, reversion\n"
        "    from retraite_notionnelle.scenarios.actuel import AgesOuverture, ResultatActuel\n"
        "    import retraite_notionnelle.pilote\n"
    ) == {"retraite_notionnelle.simulateur.Simulateur", "retraite_notionnelle.droit.liquider",
          "retraite_notionnelle.droit.reversion.reversion",
          "retraite_notionnelle.scenarios.actuel.AgesOuverture", "retraite_notionnelle.pilote"}
    assert entrees_dans_le_moteur(
        "from retraite_notionnelle.carriere import LigneRelevee, Metier\n"
        "from retraite_notionnelle.config import Parametres\n"
        "from retraite_notionnelle.donnees.chargement import Fiabilite\n"
        "from retraite_notionnelle.droit.commun import PensionRegime\n"
        "from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Comparaison\n"
        "from facade import Carriere, Simulateur, reversion\n"
    ) == set()
    assert entrees_dans_le_moteur("from retraite_notionnelle.carriere import Carriere\n") == {
        "retraite_notionnelle.carriere.Carriere"}


def test_la_liste_des_fichiers_sur_le_moteur_python_ne_fait_que_decroitre():
    """Un fichier de tests de plus n'entre pas dans le moteur Python : il passe
    par la façade ou par le pont. Un fichier qui n'y entre plus quitte la
    liste."""
    ici = Path(__file__).parent
    dedans = {fichier.name for fichier in ici.glob("test_*.py")
              if entrees_dans_le_moteur(fichier.read_text(encoding="utf-8"))}
    de_plus = sorted(dedans - set(FICHIERS))
    assert not de_plus, (
        f"{', '.join(de_plus)} : un fichier de tests de plus entre dans le moteur Python "
        f"({sorted(entrees_dans_le_moteur((ici / de_plus[0]).read_text(encoding='utf-8')))[:3]}) "
        "— il passe par la façade (tests/facade.py) ou par le pont")
    de_moins = sorted(set(FICHIERS) - dedans)
    assert not de_moins, (
        f"{', '.join(de_moins)} : n'entre plus dans le moteur Python — le retirer de FICHIERS")
    assert list(FICHIERS) == sorted(set(FICHIERS))


# -- les fichiers passés à la façade : leurs tests restés sur le moteur Python ----------

def test_un_test_entre_dans_le_moteur_python_par_ce_qu_il_nomme():
    """Un test entre dans le moteur Python par un import qu'il fait lui-même,
    par un nom que son fichier en importe, par une aide ou une fixture qui y
    entre ; la marque se lit sur lui."""
    source = (
        "import pytest\n"
        "from retraite_notionnelle.droit import liquider\n"
        "from retraite_notionnelle.carriere import Metier\n"
        "from facade import Simulateur\n"
        "@pytest.fixture\n"
        "def simulateur(): return Simulateur()\n"
        "@pytest.fixture\n"
        "def bareme(): return liquider.bareme(2020)\n"
        "def _aide(moteur): return liquider.decote(moteur)\n"
        "def test_par_la_facade(simulateur): assert simulateur.simuler(Metier('artisan', 20))\n"
        "def test_par_un_nom(simulateur): assert liquider.decote(simulateur)\n"
        "def test_par_une_aide(simulateur): assert _aide(simulateur)\n"
        "def test_par_une_fixture(bareme): assert bareme\n"
        "@pytest.mark.sur_le_moteur_python('ouvrir.duree_requise')\n"
        "def test_par_un_import(simulateur):\n"
        "    from retraite_notionnelle.droit.ouvrir import duree_requise\n"
        "    assert duree_requise(simulateur)\n"
    )
    assert les_tests_dans_le_moteur(source) == {
        "test_par_un_nom": "retraite_notionnelle.droit.liquider",
        "test_par_une_aide": "_aide", "test_par_une_fixture": "bareme",
        "test_par_un_import": "retraite_notionnelle.droit.ouvrir.duree_requise"}
    assert les_tests_marques(source) == {"test_par_un_import"}


def test_dans_un_fichier_passe_a_la_facade_seuls_les_tests_marques_restent_sur_le_moteur_python():
    """Un fichier passé à la façade garde, sous la marque
    ``sur_le_moteur_python``, les tests qu'elle ne sait pas encore servir : leur
    nombre est tenu ici, et ne fait que décroître. Un test sans marque n'entre
    pas dans le moteur Python ; un fichier qui n'a plus de test marqué quitte
    ``RESTES``, et ``FICHIERS`` avec ses derniers imports du moteur."""
    ici = Path(__file__).parent
    for fichier, attendus in RESTES.items():
        source = (ici / fichier).read_text(encoding="utf-8")
        marques = les_tests_marques(source)
        sans_marque = sorted(set(les_tests_dans_le_moteur(source)) - marques)
        assert not sans_marque, (
            f"{fichier} : {', '.join(sans_marque[:5])} entre(nt) dans le moteur Python sans la "
            "marque sur_le_moteur_python — le test passe par la façade, ou garde sa marque")
        assert len(marques) == attendus, (
            f"{fichier} : {len(marques)} tests marqués sur_le_moteur_python, RESTES en compte "
            f"{attendus} — le nombre ne fait que décroître, et se tient ici")
    passes = {fichier.name for fichier in ici.glob("test_*.py")
              if "entrees_du_test" in fichier.read_text(encoding="utf-8")}
    assert passes - {"test_facade.py", Path(__file__).name} == set(RESTES)
