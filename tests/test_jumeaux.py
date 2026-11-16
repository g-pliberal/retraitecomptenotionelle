"""La carte des jumeaux (``scripts/jumeaux.py``, action 161) : ce qu'elle relève
de chaque paire Python–JavaScript, sur des dépôts miniatures, puis sur celui-ci.

Les dépôts miniatures tiennent ses règles une à une : la déclaration d'un
en-tête, un import qu'un script fait depuis son dossier, une chaîne qui nomme
un fichier, le graphe des modules depuis la page du site, le champ ``code`` des
fiches, les chiffres ancrés, les mentions, la lecture d'une couverture de V8.
Sur le dépôt, une déclaration de jumeau qui nomme un fichier disparu est une
dépendance cachée qu'un retrait a cassée : la carte la refuse.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import jumeaux  # noqa: E402


def _ecrire(racine: Path, fichiers: dict[str, str]) -> list[str]:
    for chemin, texte in fichiers.items():
        (racine / chemin).parent.mkdir(parents=True, exist_ok=True)
        (racine / chemin).write_text(texte, encoding="utf-8")
    return sorted(fichiers)


def _lecteurs(racine: Path, fichiers: list[str]):
    suffixes = jumeaux.index_des_suffixes(fichiers)
    python = jumeaux.Python(racine, fichiers, suffixes)
    return python, jumeaux.Resolveur(suffixes, python)


# -- les règles, sur des dépôts miniatures ---------------------------------------


def test_un_en_tete_declare_son_jumeau(tmp_path):
    _ecrire(tmp_path, {chemin: "" for chemin in (
        "src/retraite_notionnelle/droit/acquerir.py", "src/retraite_notionnelle/pilote.py",
        "src/retraite_notionnelle/donnees/patrimoine.py", "scripts/fetch/lecture_pdf.py")})
    cas = {
        "/**\n * Jumeau de `src/retraite_notionnelle/droit/acquerir.py`, fonction pour fonction.\n */":
            ("src/retraite_notionnelle/droit/acquerir.py", False),
        "/**\n * Ce qu'on lit — Portage d'une partie de `src/retraite_notionnelle/pilote.py`.\n */":
            ("src/retraite_notionnelle/pilote.py", True),
        "/**\n * Copie de `donnees/patrimoine.py`, qui dit les deux formes.\n */":
            ("src/retraite_notionnelle/donnees/patrimoine.py", False),
        "/**\n * Portage de ``scripts/fetch/lecture_pdf.py``, qui fait foi.\n */":
            ("scripts/fetch/lecture_pdf.py", False),
    }
    for texte, (attendu, partielle) in cas.items():
        chemin, _, est_partielle = jumeaux.declaration(tmp_path, texte)
        assert (chemin, est_partielle) == (attendu, partielle), texte
    # Une phrase qui parle d'autres fichiers ne déclare rien, ni ce qui suit le
    # premier commentaire.
    assert jumeaux.declaration(tmp_path, "/**\n * La saisie dans ``saisie.js``, portages de\n"
                               " * ``src/retraite_notionnelle/saisie.py`` et ``contexte.py``.\n */") is None
    assert jumeaux.declaration(tmp_path, "/** Le site. */\n// Portage de `pilote.py`\n") is None


def test_un_en_tete_qui_se_dit_sans_jumeau_ne_s_apparie_pas_par_le_nom(tmp_path):
    """Une paire tranchée — le Python ne garde que ce que la fabrique écrit au
    paquet, et le calcul n'est plus que dans le JavaScript (note de décision
    0005) — le dit à l'en-tête de son JavaScript : la carte cesse de
    l'apparier au Python du même nom, et chacun passe parmi les « seuls »."""
    fichiers = _ecrire(tmp_path, {
        "src/retraite_notionnelle/donnees/parts.py": "",
        "moteur/js/parts.js": "/**\n * Les parts. Sans jumeau Python : le chargeur\n"
                              " * ``src/retraite_notionnelle/donnees/parts.py`` écrit le paquet.\n */\n",
        "src/retraite_notionnelle/donnees/taux.py": "",
        "moteur/js/taux.js": "/**\n * Les taux.\n */\n",
    })
    paires, mortes = jumeaux.paires(tmp_path, fichiers)
    assert [(p.python, p.javascript) for p in paires] == [
        ("src/retraite_notionnelle/donnees/taux.py", "moteur/js/taux.js")]
    assert mortes == []


def test_un_import_se_cherche_comme_sys_path(tmp_path):
    """Un script se lance depuis son dossier : ``from lecture import lire`` y
    trouve son voisin, et un script de ``scripts/`` le trouve dans
    ``scripts/fetch/``, comme le chemin que ces scripts se donnent."""
    fichiers = _ecrire(tmp_path, {
        "src/retraite_notionnelle/__init__.py": "",
        "src/retraite_notionnelle/a.py": "from .b import f\n",
        "src/retraite_notionnelle/b.py": "def f():\n    return 1\n",
        "scripts/fetch/lecture.py": "def lire():\n    pass\n",
        "scripts/fetch/voisin.py": "from lecture import lire\n",
        "scripts/etude.py": "def faire():\n    from lecture import lire\n"
                            "    from retraite_notionnelle.a import f\n",
        "tests/test_etude.py": "import etude\n",
    })
    python, _ = _lecteurs(tmp_path, fichiers)
    assert sorted(python.importe_par["scripts/fetch/lecture.py"]) == [
        ("scripts/etude.py", 2), ("scripts/fetch/voisin.py", 1)]
    # La fermeture suit les imports relatifs, et le paquet qui les porte.
    assert python.fermeture(["scripts/etude.py"]) >= {
        "src/retraite_notionnelle/a.py", "src/retraite_notionnelle/b.py",
        "src/retraite_notionnelle/__init__.py"}
    assert python.atteint_par["src/retraite_notionnelle/b.py"] == {
        "scripts/etude.py", "tests/test_etude.py"}


def test_une_chaine_du_code_qui_nomme_un_fichier_se_releve(tmp_path):
    """Un test qui charge un script par son chemin, ou fait lire un module du
    portage à node, en dépend sans l'importer ; une docstring ne charge rien."""
    fichiers = _ecrire(tmp_path, {
        "scripts/fetch/sre.py": "",
        "moteur/js/releve-lu.js": "export const x = 1;\n",
        "tests/test_sre.py": '"""Le lecteur, ``sre.py``."""\n'
                             'CHEMIN = "scripts/fetch/sre.py"\n'
                             'JS = "./moteur/js/releve-lu.js"\n'
                             'LU = site().module("releve-lu")\n',
    })
    python, _ = _lecteurs(tmp_path, fichiers)
    assert python.par_chemin["tests/test_sre.py"] == [
        ("scripts/fetch/sre.py", 2, "scripts/fetch/sre.py")]
    assert sorted(python.vers_node["tests/test_sre.py"]) == [
        ("moteur/js/releve-lu.js", 3, "./moteur/js/releve-lu.js"),
        ("moteur/js/releve-lu.js", 4, 'module("releve-lu")')]


def test_le_site_atteint_ce_que_sa_page_importe(tmp_path):
    fichiers = _ecrire(tmp_path, {
        "index.html": '<link rel="modulepreload" href="moteur/js/seul.js">\n'
                      '<script type="module">\nimport { a } from "./moteur/js/a.js";\n'
                      'const { r } = await import("./moteur/js/r.js");\n</script>\n',
        "moteur/js/a.js": 'import { b } from "./b.js";\nexport const a = b;\n',
        "moteur/js/b.js": "export const b = 1;\n",
        "moteur/js/r.js": "export const r = 2;\n",
        "moteur/js/seul.js": "export const s = 3;\n",
    })
    js = jumeaux.JavaScript(tmp_path, fichiers)
    assert js.site == {"moteur/js/a.js", "moteur/js/b.js", "moteur/js/r.js"}
    assert js.precharges == {"moteur/js/seul.js"}
    assert js.importe_par["moteur/js/b.js"] == [("moteur/js/a.js", 1)]


def test_le_champ_code_des_fiches_se_lit_sous_ses_deux_formes(tmp_path):
    """Celui de la proposition nomme modules et fichiers ; celui du droit réel
    les écrit en clair. Un fichier qu'il nomme et qui n'existe pas est mort."""
    fichiers = _ecrire(tmp_path, {
        "src/retraite_notionnelle/__init__.py": "",
        "src/retraite_notionnelle/moteur/age_reference.py": "",
        "src/retraite_notionnelle/droit/categories.py": "",
        "moteur/js/age-reference.js": "",
        "data/reference/regles/proposition/age.yaml":
            "intitule: x\ncode:\n  python:\n"
            "    retraite_notionnelle.moteur.age_reference: [AgeReference.age]\n"
            "  javascript:\n    moteur/js/age-reference.js: [AgeReference]\n",
        "data/reference/regles/meres.yaml":
            "intitule: y\ncode:\n  python: >-\n"
            "    droit/categories.py : remplit ; droit/disparu.py : rien\n",
    })
    _, resolveur = _lecteurs(tmp_path, fichiers)
    fiches, mortes = jumeaux.code_des_fiches(tmp_path, fichiers, resolveur)
    age = "data/reference/regles/proposition/age.yaml"
    assert [(r.fichier, r.ligne) for r in fiches["src/retraite_notionnelle/moteur/age_reference.py"]] == [
        (age, 4)]
    assert [(r.fichier, r.ligne) for r in fiches["moteur/js/age-reference.js"]] == [(age, 6)]
    assert [r.fichier for r in fiches["src/retraite_notionnelle/droit/categories.py"]] == [
        "data/reference/regles/meres.yaml"]
    assert [(r.fichier, r.texte) for r in mortes] == [
        ("data/reference/regles/meres.yaml", "droit/disparu.py")]


def test_un_chiffre_ancre_qui_charge_un_module_se_releve(tmp_path):
    fichiers = _ecrire(tmp_path, {
        "src/retraite_notionnelle/__init__.py": "",
        "src/retraite_notionnelle/saisie.py": "LISSAGE_MAXIMUM = 25\n",
        "README.md": "Au plus <!--chiffre:mesure(constante?de=retraite_notionnelle.saisie"
                     "&nom=LISSAGE_MAXIMUM)-->25<!--/--> ans ; de "
                     "<!--chiffre:mesure(indexation?de=1970&a=2020)-->2<!--/--> ; et\n"
                     "<!--chiffre:mesure(constante?de=retraite_notionnelle.disparu&nom=X)-->1<!--/-->.\n",
    })
    _, resolveur = _lecteurs(tmp_path, fichiers)
    sortie, mortes = jumeaux.ancres(tmp_path, fichiers, resolveur)
    assert [(r.fichier, r.ligne, r.texte) for r in sortie["src/retraite_notionnelle/saisie.py"]] == [
        ("README.md", 1, "retraite_notionnelle.saisie")]
    # Un module disparu ne se prend pas pour le paquet qui le portait.
    assert [(r.ligne, r.texte) for r in mortes] == [(2, "retraite_notionnelle.disparu")]


def test_une_mention_se_range_en_recit_ou_a_tenir(tmp_path):
    fichiers = _ecrire(tmp_path, {
        "src/retraite_notionnelle/donnees/primes.py": "",
        "src/retraite_notionnelle/droit/primes.py": "",
        "docs/limites/1-regles.md": "Voir `droit/primes.py`.\n",
        "docs/archives/ancien.md": "Voir `primes.py`.\n",
    })
    _, resolveur = _lecteurs(tmp_path, fichiers)
    cible = "src/retraite_notionnelle/droit/primes.py"
    sortie = jumeaux.mentions(tmp_path, fichiers, resolveur, {cible})
    assert sorted((r.fichier, r.recit, r.ambigu) for r in sortie[cible]) == [
        ("docs/archives/ancien.md", True, True), ("docs/limites/1-regles.md", False, False)]


# -- la couverture ---------------------------------------------------------------


def test_une_couverture_de_v8_se_lit_ligne_a_ligne():
    """Une ligne prend le compte de la plage la plus intérieure qui la contient
    en entier ; un commentaire ne compte pas ; les décalages sont en unités
    UTF-16, comme ceux de V8, et l'émoji du commentaire en vaut deux. La ligne
    qui déclare une fonction jamais appelée n'est pas exécutée."""
    source = (
        "// 😀 le module\n"
        "export function appelee() {\n"
        "  return 1;\n"
        "}\n"
        "function jamais() {\n"
        "  return 2;\n"
        "}\n"
    )

    def position(texte: str) -> int:
        return len(source[: source.index(texte)].encode("utf-16-le")) // 2

    fin = len(source.encode("utf-16-le")) // 2
    fonctions = [
        {"ranges": [{"startOffset": 0, "endOffset": fin, "count": 1}]},
        {"ranges": [{"startOffset": position("function appelee"),
                     "endOffset": position("function jamais") - 1, "count": 3}]},
        {"ranges": [{"startOffset": position("function jamais"),
                     "endOffset": fin - 1, "count": 0}]},
    ]
    assert jumeaux.lignes_de_code_js(source) == {2, 3, 4, 5, 6, 7}
    assert jumeaux.lignes_executees_js(source, fonctions) == {2, 3, 4}


def test_une_ligne_python_compte_si_elle_porte_une_instruction():
    source = "x = 1\nif x:\n    y = 2\n# commentaire\n\ndef f():\n    return 3\n"
    lignes = jumeaux.lignes_executables(source)
    assert {1, 2, 3, 6, 7} <= lignes
    assert not lignes & {4, 5}


@pytest.mark.skipif(not hasattr(sys, "monitoring"), reason="sys.monitoring : Python 3.12 et après")
def test_la_sonde_releve_les_lignes_executees_du_depot(tmp_path):
    from retraite_notionnelle import somme

    sonde = jumeaux.Sonde(tmp_path).demarrer()
    try:
        somme.somme_ordonnee([1, 2])
    finally:
        sonde.arreter()
    sonde.ecrire()
    (ecrit,) = tmp_path.glob("py-*.json")
    lignes = json.loads(ecrit.read_text(encoding="utf-8"))["src/retraite_notionnelle/somme.py"]
    executables = jumeaux.lignes_executables(
        (RACINE / "src/retraite_notionnelle/somme.py").read_text(encoding="utf-8"))
    assert lignes and set(lignes) <= executables


def test_des_lignes_se_disent_en_plages():
    assert jumeaux.plages([7, 1, 2, 3, 5, 8]) == "1-3, 5, 7-8"
    assert jumeaux.plages([]) == ""


# -- les fonctions des deux côtés, et la liste de celles qu'on garde -------------


def test_les_fonctions_d_un_fichier_python():
    texte = (
        "def charger(x):\n    def interne():\n        pass\n"
        "def _privee():\n    pass\n"
        "class Table:\n"
        "    def __init__(self):\n        pass\n"
        "    def __post_init__(self):\n        pass\n"
        "    @property\n    def premiere_annee(self):\n        pass\n"
        "    def valeur_de(self, annee):\n        pass\n")
    assert jumeaux.fonctions_python(texte) == {"charger", "_privee", "premiere_annee", "valeur_de"}


def test_les_fonctions_d_un_fichier_javascript():
    texte = (
        "export function survie(age) {\n  const interne = (x) => x;\n  if (age) {}\n}\n"
        "function _lire(x) {}\n"
        "export async function charger() {}\n"
        "export const quantileNormal = (p) => p;\n"
        "const grille = function (n) {};\n"
        "export const LIMITE = 3;\n"
        "export class Table {\n"
        "  constructor(x) {\n    for (;;) {}\n  }\n"
        "  valeurDe(annee) {\n    if (annee) {}\n  }\n"
        "  get premiereAnnee() {}\n"
        "  static depuis(donnees) {}\n"
        "  #prive() {}\n"
        "}\n"
        "  hors(x) {}\n")
    assert jumeaux.fonctions_javascript(texte) == {
        "survie", "_lire", "charger", "quantileNormal", "grille", "valeurDe", "premiereAnnee", "depuis"}


def test_une_methode_javascript_dont_la_signature_tient_sur_deux_lignes():
    """``trimestresValides`` de ``macro.js`` coupe ses arguments sur deux
    lignes : la carte la manquait, et la liste ne la déclarait pas."""
    texte = (
        "export class DonneesMacro {\n"
        "  trimestresValides(revenu, annee, outreMer = \"\", fraction = 1,\n"
        "                    mayotte = false) {\n"
        "    if (revenu <= 0) {\n      return 0;\n    }\n"
        "  }\n"
        "  appel(x) {\n    this.autre(x,\n      2);\n  }\n"
        "}\n")
    assert jumeaux.fonctions_javascript(texte) == {"trimestresValides", "appel"}


def test_une_fonction_est_en_double_sous_le_meme_nom_au_passage_pres_en_camel():
    python = "def taux_de(a):\n    pass\ndef _calibrer():\n    pass\ndef seul():\n    pass\n"
    javascript = "export function tauxDe(a) {}\nfunction _calibrer() {}\nexport function autre() {}\n"
    assert jumeaux.en_double(python, javascript) == {"taux_de": "tauxDe", "_calibrer": "_calibrer"}


def _depot_de_la_liste(racine: Path, liste: str) -> list[str]:
    return _ecrire(racine, {
        "src/retraite_notionnelle/donnees/taux.py":
            "def placement(a):\n    pass\ndef revenu_avpf():\n    pass\ndef charger():\n    pass\n",
        "moteur/js/taux.js":
            "/**\n * Portage de `donnees/taux.py`.\n */\n"
            "export function placement(a) {}\nexport function revenuAvpf() {}\n",
        "src/retraite_notionnelle/droit/liquider.py": "from .donnees.taux import revenu_avpf\n",
        "moteur/js/droit/liquider.js": "/**\n * Portage de `droit/liquider.py`.\n */\n",
        "src/retraite_notionnelle/cout.py": "x = placement(1)\n",
        "src/retraite_notionnelle/moteur/compte.py": "x = placement(1)\n",
        "tests/test_taux.py": "def test_placement():\n    placement(1)\n",
        "scripts/jumeaux_gardees.yaml": liste,
    })


def test_la_liste_des_fonctions_gardees_se_verifie_seule(tmp_path):
    juste = (
        "src/retraite_notionnelle/donnees/taux.py:\n"
        "  gardees:\n"
        "    placement: {lecteur: src/retraite_notionnelle/cout.py, test: tests/test_taux.py::test_placement}\n"
        "  au_moteur: [revenu_avpf]\n")
    fichiers = _depot_de_la_liste(tmp_path, juste)
    assert jumeaux.ecarts_de_la_liste(tmp_path, fichiers) == []

    # Chaque faute rougit, et se dit.
    fautes = {
        # une fonction en double qui n'est pas déclarée
        "src/retraite_notionnelle/donnees/taux.py:\n  gardees:\n"
        "    placement: {lecteur: src/retraite_notionnelle/cout.py}\n": "revenu_avpf",
        # une entrée périmée
        juste + "  au_moteur_aussi: []\n": "au_moteur_aussi",
        juste.replace("[revenu_avpf]", "[revenu_avpf, disparue]"): "disparue",
        # un lecteur qui est un test, un jumeau du moteur, ou qui ne la lit pas
        juste.replace("lecteur: src/retraite_notionnelle/cout.py", "lecteur: tests/test_taux.py"):
            "tests/test_taux.py",
        juste.replace("lecteur: src/retraite_notionnelle/cout.py",
                      "lecteur: src/retraite_notionnelle/droit/liquider.py"): "droit/liquider.py",
        juste.replace("tests/test_taux.py::test_placement", "tests/test_taux.py::test_absent"):
            "test_absent",
        # une fonction gardée qu'aucun test ne confronte à son double
        juste.replace(", test: tests/test_taux.py::test_placement", ""): "sans test",
        # un lecteur qui est un fichier de règles, sans jumeau JavaScript : il
        # part avec le moteur (action 161, étape 5)
        juste.replace("lecteur: src/retraite_notionnelle/cout.py",
                      "lecteur: src/retraite_notionnelle/moteur/compte.py"): "moteur/compte.py",
        # une paire du moteur que la liste garderait : elle part avec lui
        juste + "src/retraite_notionnelle/droit/liquider.py:\n  au_moteur: []\n":
            "fichier de règles",
        # une paire déclarée qui n'en est pas une
        juste + "src/retraite_notionnelle/absent.py:\n  au_moteur: []\n": "absent.py",
    }
    for liste, mot in fautes.items():
        fichiers = _depot_de_la_liste(tmp_path, liste)
        ecarts = jumeaux.ecarts_de_la_liste(tmp_path, fichiers)
        assert ecarts and any(mot in e for e in ecarts), (liste, ecarts)


# -- le dépôt --------------------------------------------------------------------


@pytest.fixture(scope="module")
def carte():
    return jumeaux.Carte()


def test_chaque_declaration_de_jumeau_nomme_un_fichier_qui_existe(carte):
    """Retirer un jumeau Python sans récrire l'en-tête de son JavaScript laisse
    une déclaration morte : la dépendance cachée qu'un retrait casse."""
    assert not carte.declarations_mortes, carte.declarations_mortes


def test_chaque_paire_a_ses_deux_fichiers_et_sa_place_au_classement(carte):
    classement = carte.classement()
    assert len(classement) == len(carte.paires) > 0
    for fiche in classement:
        assert (RACINE / fiche["python"]).is_file(), fiche["python"]
        assert (RACINE / fiche["javascript"]).is_file(), fiche["javascript"]
    # Ce que le coût atteint vient après ce qu'il n'atteint pas.
    bloques = [fiche["cote_python"]["cout"] for fiche in classement]
    assert bloques == sorted(bloques)


def test_un_fichier_de_regles_se_reconnait_a_son_chemin():
    """Les fichiers de règles du moteur Python, que le retrait supprime (action
    161, étape 6) : ses trois dossiers et six fichiers du paquet. La carte les
    nomme elle-même, sans lire la sonde, qui part avec eux."""
    paquet = "src/retraite_notionnelle/"
    for chemin in ("droit/liquider.py", "droit/__init__.py", "moteur/compte.py",
                   "scenarios/actuel.py", "simulateur.py", "carriere.py"):
        assert jumeaux.est_une_regle(paquet + chemin), chemin
    for chemin in (paquet + "calendrier.py", paquet + "donnees/simulateur.py",
                   paquet + "cout.py", "moteur/js/droit/liquider.js", "scripts/carriere.py"):
        assert not jumeaux.est_une_regle(chemin), chemin


def test_la_carte_et_la_sonde_disent_les_memes_fichiers_de_regles():
    """Tant que la sonde du moteur Python est là, elle et la carte s'accordent."""
    sonde = pytest.importorskip("sonde_moteur_python")
    assert (jumeaux.DOSSIERS_DE_REGLES, jumeaux.FICHIERS_DE_REGLES) == (sonde.DOSSIERS, sonde.FICHIERS)


#: Les fichiers de règles que le coût et la fabrique atteignent encore, par la
#: carrière que le pont relit sous la classe des règles (action 161, dernière
#: étape avant la suppression). La liste ne peut que rétrécir.
REGLES_ENCORE_ATTEINTES = {"src/retraite_notionnelle/carriere.py",
                           "src/retraite_notionnelle/droit/__init__.py",
                           "src/retraite_notionnelle/droit/preparer.py"}


def test_ni_le_cout_ni_la_fabrique_n_atteignent_d_autre_regle_que_la_carriere(carte):
    """Depuis l'étape 4 du retrait (action 161), le coût et la fabrique se
    chargent sans règle Python, hors de la carrière que le pont relit ; le
    simulateur Python n'en est plus, et son jumeau reste chargé par le site."""
    for atteints in (carte.cout, carte.fabrique):
        assert {c for c in atteints if jumeaux.est_une_regle(c)} <= REGLES_ENCORE_ATTEINTES
    assert "moteur/js/simulateur.js" in carte.js.site


def test_aucun_chiffre_ancre_ne_charge_un_fichier_de_regles(carte):
    """Les chiffres ancrés lisent les constantes du droit au portage, qui fait
    foi, et non dans les fichiers de règles du moteur Python, que le retrait
    supprimera (action 161, étape 5)."""
    regles = {c for c in carte.ancres if jumeaux.est_une_regle(c)}
    assert not regles, {c: [(r.fichier, r.ligne) for r in carte.ancres[c]] for c in regles}


#: Les fichiers qui chargent ou nomment encore un fichier de règles par son
#: chemin : la sonde du moteur Python et le relevé de ce qui y entre, avec
#: leurs tests, dont l'objet part avec les règles (action 161, étape 6).
CHARGENT_ENCORE_UNE_REGLE = {"scripts/sonde_moteur_python.py",
                             "scripts/entrees_du_moteur.py",
                             "tests/test_sonde_moteur_python.py",
                             "tests/test_entrees_du_moteur.py"}


def test_aucun_chargement_par_chemin_ne_vise_un_fichier_de_regles(carte):
    """Hors des outils qui mesurent le moteur Python et partent avec lui, aucun
    script ni test ne charge ni ne nomme un fichier de règles par son chemin :
    la suppression ne casserait aucune lecture (action 161, étape 5)."""
    lecteurs = {(r.fichier, r.ligne, c) for c, renvois in carte.par_chemin.items()
                if jumeaux.est_une_regle(c) for r in renvois
                if r.fichier not in CHARGENT_ENCORE_UNE_REGLE}
    assert not lecteurs, sorted(lecteurs)


def test_la_carte_et_le_detail_d_une_paire_s_impriment(carte):
    assert jumeaux.imprimer_la_carte(carte)[0].startswith("La carte des jumeaux : ")
    ((rang, fiche),) = jumeaux.chercher(carte, "calendrier")
    assert "Côté Python" in jumeaux.imprimer_une_paire(carte, fiche, rang)


def test_les_fonctions_gardees_des_deux_cotes_sont_declarees_et_tenues():
    """La liste de la clôture (action 161, question 4) : dans chaque paire qui
    reste, toute fonction écrite des deux côtés est gardée — avec le fichier
    Python qui la lit, ni test ni jumeau du moteur — ou part avec le moteur."""
    ecarts = jumeaux.ecarts_de_la_liste(RACINE, jumeaux.fichiers_suivis())
    assert not ecarts, "\n".join(ecarts)


def test_les_paires_du_moteur_sont_celles_dont_le_python_est_une_regle(carte):
    """Les paires qui partent avec le moteur Python : leur Python est un fichier
    de règles. Aucune n'est dans la liste des fonctions gardées, et toutes les
    autres restent ; à la suppression, l'en-tête de chacun de leurs JavaScript
    cesse de déclarer son jumeau (action 161, étape 6)."""
    du_moteur = carte.paires_du_moteur()
    assert du_moteur and all(jumeaux.est_une_regle(p.python) for p in du_moteur)
    assert not {p.python for p in du_moteur} & set(jumeaux.lire_la_liste())
    restent = set(carte.paires) - set(du_moteur)
    assert restent and not any(jumeaux.est_une_regle(p.python) for p in restent)
