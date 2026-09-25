"""La prose du dépôt, confrontée au dépôt.

Le dépôt affirme deux mille cinq cents chiffres en prose, et une vingtaine
seulement étaient tenus par un test écrit exprès pour eux, un par un, après
coup — « 472 tests pour 485 », « 321 tests » puis « 390 », le paquet de
données. Chacun de ces tests répare une dérive constatée ; aucun n'empêche la
suivante, parce qu'il faut à chaque fois qu'un humain ait remarqué.

`scripts/verifier_prose.py` renverse la charge : c'est la prose qui porte, à
côté de chaque chiffre, la sonde qui le recalcule. Ce fichier-ci en fait une
obligation, et vérifie la mécanique elle-même — un contrôleur qui se tromperait
sur ce qu'est un chiffre serait pire qu'aucun contrôleur.

La distinction qui fonde tout est celle de l'ÉTAT et du RÉCIT. Le dépôt écrit
les deux dans les mêmes fichiers : « 263 Ko de modèle » est faux aujourd'hui et
était vrai du temps de Pyodide, une ligne plus haut. Corriger un chiffre de
récit serait réécrire l'histoire ; laisser dériver un chiffre d'état est ce qui
a donné « douze mille lignes » à un portage qui en fait 22 776. `zones.yaml`
tranche, section par section, et le cliquet fait que ce partage ne peut que
s'étendre.
"""

from __future__ import annotations

import re
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _charger():
    chemin = RACINE / "scripts" / "verifier_prose.py"
    specification = importlib.util.spec_from_file_location("verifier_prose", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_prose"] = module
    specification.loader.exec_module(module)
    return module


verifier_prose = _charger()


@pytest.fixture(scope="module")
def zonage():
    return verifier_prose.charger_zonage()


# -- ce que le dépôt doit tenir ----------------------------------------------


def test_aucun_chiffre_ancre_n_a_derive(zonage):
    """Chaque chiffre ancré est recalculé, et doit tomber juste.

    C'est le contrôle qui remplace les tests écrits un par un : là où
    `test_le_README_dit_le_vrai_nombre_de_tests` tient un chiffre et un seul,
    celui-ci tient tous ceux qu'on a ancrés, et le suivant sans rien écrire de
    plus que l'ancre.
    """
    anomalies, _ = verifier_prose.controler(zonage, corriger=False)
    derives = [a for a in anomalies if a.genre == "derive"]
    assert not derives, "\n".join(
        f"{a.fichier}:{a.ligne}: {a.message}" for a in derives
    ) + "\n\nlancer : python scripts/verifier_prose.py --corriger"


def test_aucune_zone_d_etat_ne_porte_de_chiffre_nu(zonage):
    """Une section déclarée « etat » décrit ce qui est vrai AUJOURD'HUI.

    Un chiffre nu y est une promesse que rien ne tient : c'est ainsi que la
    feuille de route a donné « plus de trois mille lignes » à un fichier qui en
    fait 4 251. La clause vaut aussi pour les chiffres écrits en toutes
    lettres, qui vieillissent exactement pareil et que l'ancre ne sait pas
    tenir — il faut les réécrire en chiffres.
    """
    anomalies, _ = verifier_prose.controler(zonage, corriger=False)
    nus = [a for a in anomalies if a.genre in ("nu", "lettres")]
    assert not nus, "\n".join(f"{a.fichier}:{a.ligne}: {a.message}" for a in nus)


def test_chaque_sonde_nommee_existe_et_repond(zonage):
    """Une ancre qui nomme une sonde inconnue, ou un fichier disparu, échoue.

    Sans quoi l'ancre deviendrait décorative : le jour où le fichier qu'elle
    interroge est déplacé, elle cesserait de tenir quoi que ce soit en silence.
    """
    anomalies, _ = verifier_prose.controler(zonage, corriger=False)
    muettes = [a for a in anomalies if a.genre == "sonde"]
    assert not muettes, "\n".join(f"{a.fichier}:{a.ligne}: {a.message}" for a in muettes)


def test_zones_yaml_ne_declare_que_des_sections_qui_existent(zonage):
    """Une section renommée doit être redéclarée, pas oubliée.

    C'est la mécanique d'`inventaire.yaml` : le catalogue et le document se
    tiennent l'un l'autre, et le divorce est une erreur, jamais un silence.
    """
    anomalies, _ = verifier_prose.controler(zonage, corriger=False)
    orphelines = [a for a in anomalies if a.genre == "section"]
    assert not orphelines, "\n".join(f"{a.fichier}: {a.message}" for a in orphelines)


def test_les_deux_cliquets_ne_remontent_jamais(zonage):
    """Ce qui fait avancer le dépôt sans qu'on y pense.

    Deux compteurs, dans `zones.yaml`, qui ne peuvent que décroître : les
    sections dont personne n'a encore dit ce qu'elles affirment, et les
    chiffres qui portent l'aveu `a_verifier`. Une section nouvelle dans un
    fichier non déclaré fait monter le premier et le test échoue jusqu'à ce
    qu'on ait tranché. Le jour où les deux tombent à zéro, plus un chiffre du
    dépôt n'est un souvenir.
    """
    anomalies = verifier_prose.controler_cliquet(zonage)
    assert not anomalies, "\n".join(a.message for a in anomalies)


def test_tout_document_du_depot_est_declare(zonage):
    """Un document neuf ne peut pas entrer sans qu'on dise ce qu'il affirme."""
    connus = set(verifier_prose.documents(zonage))
    sur_disque = {"README.md", "CLAUDE.md"} | {
        f"docs/{c.name}" for c in (RACINE / "docs").glob("*.md")
    }
    assert not sur_disque - connus, (
        f"{sorted(sur_disque - connus)} : ajouter ces documents à "
        "data/reference/prose/zones.yaml, avec leur régime"
    )


# -- la mécanique elle-même --------------------------------------------------


def test_un_nombre_dans_du_code_n_est_pas_une_affirmation():
    """Les blocs et les incises de code portent des articles, des options et
    des sorties de programme : rien n'y est une affirmation, et tout y
    ressemble. Le masquage ne déplace aucun caractère, pour que les numéros de
    ligne restent justes."""
    texte = ("Le taux est de 18 %.\n"
             "`R. 351-9` et `--limite 20` n'affirment rien.\n"
             "```\n"
             "  pension  1 234 €\n"
             "```\n")
    masque = verifier_prose._nettoyer(texte)
    assert len(masque) == len(texte)
    assert [m.group(0) for m in verifier_prose.CHIFFRE.finditer(masque)] == ["18 %"]


def test_un_chiffre_coupe_par_un_retour_a_la_ligne_est_vu():
    """« plus de trois mille / lignes » enjambait la coupe, et passait entre
    les mailles — c'est exactement le chiffre qui avait vieilli de dix mille.
    Un blanc de paragraphe, en revanche, sépare deux phrases."""
    assert verifier_prose.CHIFFRE_LETTRES.search("plus de trois mille\nlignes)")
    assert verifier_prose.CHIFFRE.search("de 89\nrégimes")
    assert not verifier_prose.CHIFFRE.search("était 89\n\nlignes de plus")


def test_une_annee_n_est_pas_un_chiffre():
    """« de 1962 à 2070 » et « §5 bis » ne sont pas des affirmations chiffrées :
    sans unité, un nombre n'est pas une grandeur qui se périme."""
    for texte in ("de 1962 à 2070", "§5 bis", "l'article R. 351-45 II"):
        assert not verifier_prose.CHIFFRE.search(texte), texte


def test_une_correction_garde_la_typographie_du_chiffre_qu_elle_remplace():
    """Le dépôt écrit « 2874 » et « 10 615 » ; une correction qui changerait
    l'un en l'autre ferait un diff que personne ne veut relire."""
    ecrire = verifier_prose._ecrire_comme
    assert ecrire(2944, "2874") == "2944"
    assert ecrire(22776, "12 000") == "22 776"
    assert ecrire(79.5, "75,9") == "79,5"
    assert ecrire(-79.5, "−75,9") == "−79,5"


def test_un_proces_verbal_enclave_reste_gele():
    """« **Ce que ça a déplacé.** » ouvre, dans une action de la feuille de
    route, un paragraphe qui date : ses chiffres sont ceux du jour où l'action
    a été faite. Les rafraîchir serait réécrire l'histoire."""
    lignes = ["### 12. Une action", "", "Le catalogue compte 72 régimes.", "",
              "**Ce que ça a déplacé.** Le cumul passait de 75,9 % à 79,5 %.",
              "et la suite du paragraphe, toujours gelée", "",
              "Le texte d'après ne l'est plus."]
    geles = verifier_prose.paragraphes_geles(lignes, ["**Ce que ça a déplacé"])
    assert geles == {5, 6}


def test_une_dette_avouee_doit_dire_pourquoi():
    """`a_verifier` est l'aveu, pas l'échappatoire : sans raison lisible, ce ne
    serait qu'un moyen commode de faire taire le contrôle."""
    with pytest.raises(ValueError):
        verifier_prose.sonde_a_verifier("plus tard")
    assert verifier_prose.sonde_a_verifier(
        "le compte demande de lancer node --test") is None


def test_un_chiffre_tenu_ailleurs_nomme_un_test_qui_existe():
    """Sinon l'ancre survivrait au test qu'elle invoque, et ne tiendrait
    plus rien en silence."""
    assert verifier_prose.sonde_tenu("test_aucun_chiffre_ancre_n_a_derive") is None
    with pytest.raises(ValueError):
        verifier_prose.sonde_tenu("test_qui_n_a_jamais_existe")


def test_les_sondes_comptent_ce_qu_elles_disent_compter():
    """Le vocabulaire est fermé, et chacun de ses mots doit être juste."""
    assert verifier_prose.sonde_lignes("README.md") == len(
        (RACINE / "README.md").read_text(encoding="utf-8").splitlines())
    inventaire = "data/reference/regimes/inventaire.yaml:inventaire"
    total = verifier_prose.sonde_entrees(inventaire)
    calcules = verifier_prose.sonde_entrees(
        f"{inventaire}?couverture=modelise|partiel")
    assert 0 < calcules < total, "le filtre ne filtre rien"
    assert verifier_prose.sonde_poids("moteur/donnees.json") > 0


def test_les_tableaux_produits_ne_sont_pas_perimes():
    """Ce que le modèle calcule ne se recopie pas à la main.

    Le site rend le tableau des règles d'indexation à chaque affichage ; la
    prose en portait deux copies, dans le README et dans la méthodologie, et
    elles donnaient le PIB nominal à 1 068,6 % quand le modèle en calcule
    1 068,3. `scripts/construire_tableaux_md.py` les écrit désormais entre
    deux repères, et ce test refuse une prose qui ne serait plus la sienne.
    """
    import subprocess

    rendu = subprocess.run(
        [sys.executable, "-X", "utf8", "scripts/construire_tableaux_md.py", "--verifier"],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    assert rendu.returncode == 0, rendu.stdout + rendu.stderr


def test_le_tableau_de_bord_n_est_pas_perime():
    """Où en est le dépôt ne s'écrit pas à la main.

    `docs/etat.md` répond à trois questions — où en est-on, ce qui ne va pas
    encore, ce qui reste à faire — et `scripts/tableau_de_bord.py` l'écrit en
    entier depuis les registres : la veille, l'inventaire et les effectifs,
    les exemples officiels, les réformes, les sources à explorer, la feuille
    de route. Une règle qui change d'état dans la veille change la page ; ce
    test refuse une page qui ne serait plus celle que les registres disent.
    """
    import subprocess

    rendu = subprocess.run(
        [sys.executable, "-X", "utf8", "scripts/tableau_de_bord.py", "--verifier"],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    assert rendu.returncode == 0, rendu.stdout + rendu.stderr


def test_le_cout_du_travail_s_affiche_a_la_demande_et_hors_de_la_page():
    """Le coût du travail se relève sur l'historique git : ses chiffres
    changent à chaque commit, et une page qui les porterait serait périmée dès
    le suivant. `--cout` l'affiche sans rien écrire ; `docs/etat.md` n'en
    porte que le renvoi."""
    import subprocess

    rendu = subprocess.run(
        [sys.executable, "-X", "utf8", "scripts/tableau_de_bord.py", "--cout"],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    assert rendu.returncode == 0, rendu.stdout + rendu.stderr
    assert rendu.stdout.startswith("## Le coût du travail"), rendu.stdout[:200]
    page = (RACINE / "docs" / "etat.md").read_text(encoding="utf-8")
    assert "## Le coût du travail" not in page
    assert "--cout" in page


def test_le_chiffrage_plf_n_est_pas_perime():
    """Un chiffrage budgétaire est le document qu'on oublie de relire.

    `docs/chiffrage_plf.md` porte les dépenses, les recettes et le solde de la
    proposition année par année, et sa prose est datée — régime `recit`. Ses
    tableaux, eux, sont ceux que le modèle calcule aujourd'hui : une
    modification du modèle les déplace, et personne ne pense à rouvrir un avis
    rendu. `scripts/chiffrage_plf.py --verifier` le refuse, document et série
    annuelle comprises.

    Le contrôle coûte deux exécutions de `calculer_cout` — la variante
    rétroactive et la prospective —, soit une trentaine de secondes, ce qui en
    fait l'un des tests les plus lents de la suite. C'est le prix d'un chiffrage
    qui ne se périme pas en silence, et xdist l'absorbe.
    """
    import subprocess

    rendu = subprocess.run(
        [sys.executable, "-X", "utf8", "scripts/chiffrage_plf.py", "--verifier"],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    assert rendu.returncode == 0, rendu.stdout + rendu.stderr


def test_un_bloc_produit_est_exempt_de_l_ancre():
    """Un tableau qu'un script écrit n'a pas à porter une ancre par cellule.

    C'est le régime `produit`, mais sur un BLOC au lieu d'une section entière,
    parce qu'un document mêle la prose et ce qui se calcule : la phrase qui
    commente le tableau reste tenue par une ancre, le tableau par son script.
    """
    lignes = ["Le pouvoir d'achat conservé :", "<!-- indexation:debut -->",
              "| Règle | ×4,9 | 1,5 % |", "<!-- indexation:fin -->",
              "et 12 lignes de prose ensuite"]
    produites = verifier_prose.lignes_produites(lignes, ["indexation"])
    assert produites == {2, 3, 4}
    assert verifier_prose.lignes_produites(lignes, []) == set()


def test_un_commentaire_de_code_n_est_pas_un_titre_de_section():
    """Le README écrit ses exemples en Python, commentaires compris.

    « # Le cas général : grille cas type × génération » est une ligne de
    programme ; le découpage y voyait un titre, et ouvrait une section
    fantôme. Elles gonflaient le cliquet — neuf pour le seul README — et
    coupaient la section réelle qui les contient : un régime déclaré sur elle
    ne valait plus que jusqu'au premier commentaire.
    """
    texte = ("## En Python\n"
             "```python\n"
             "# Le cas général : grille cas type × génération\n"
             "print(calculer_cas_types(simulateur))\n"
             "```\n"
             "## En bibliothèque\n")
    assert [s.titre for s in verifier_prose.decouper(texte)] == [
        "En Python", "En bibliothèque"]


def test_le_tableau_de_certification_dit_le_niveau_que_ses_sondes_lisent():
    """La période et le niveau d'une série doivent parler du même fichier.

    Le tableau du §1 de `limites.md` donne, série par série, la période
    couverte et le niveau de fiabilité qui y règne. Les deux sont désormais
    liés : la période se lit par une sonde qui filtre le fichier sur un
    niveau, et la colonne « Niveau » doit dire ce niveau-là. Sans ce test, une
    ligne pourrait annoncer « certifiée » en lisant les bornes des années
    estimées, et personne ne le verrait — c'est même la forme la plus probable
    de l'erreur, puisque les deux colonnes se modifient séparément.
    """
    import re

    en_clair = {"certifiee": "certifiée", "haute": "haute", "moyenne": "moyenne",
                "estimee": "estimée", "projetee": "projetée", "saisie": "saisie"}
    texte = (RACINE / "docs" / "limites.md").read_text(encoding="utf-8").split("\n")
    debut = next(i for i, l in enumerate(texte)
                 if l.startswith("## 1. État de certification"))
    fin = next(i for i, l in enumerate(texte) if i > debut and l.startswith("## 2."))

    verifiees = 0
    for ligne in texte[debut:fin]:
        if not ligne.startswith("| ") or ligne.startswith("| Donnée"):
            continue
        cases = [c.strip() for c in ligne.strip("|").split("|")]
        niveaux = set(re.findall(r"fiabilite=(\w+)", cases[1]))
        if not niveaux:
            continue
        assert len(niveaux) == 1, f"deux niveaux dans une même période : {cases[0]}"
        attendu = en_clair[niveaux.pop()]
        assert cases[2].strip("*") == attendu, (
            f"« {cases[0]} » annonce « {cases[2]} » et lit les années "
            f"« {attendu} » : les deux colonnes ne parlent pas du même fichier")
        verifiees += 1
    assert verifiees >= 30, (
        f"{verifiees} lignes du tableau lisent leur période dans les données ; "
        "le compte ne doit pas reculer")


def test_un_nombre_a_decimale_et_a_separateur_est_un_seul_nombre():
    """« 7 603,41 » se lisait comme deux nombres, 7 603 et 41.

    Le premier motif ne prévoyait pas la décimale après le séparateur de
    milliers : l'ancre refusait un montant comme celui du minimum contributif
    majoré — « elle entoure 2 nombres, il en faut un » — et une correction en
    aurait fait « 7 603 ».
    """
    import re
    assert re.findall(verifier_prose._NOMBRE, "7 603,41") == ["7 603,41"]
    assert re.findall(verifier_prose._NOMBRE, "11 975,57 €") == ["11 975,57"]
    assert re.findall(verifier_prose._NOMBRE, "4 251 lignes") == ["4 251"]


def test_les_sondes_de_csv_lisent_les_tables_de_droit():
    """Une cellule, deux bornes, un compte de valeurs différentes.

    C'est ce qui manquait pour qu'un paramètre de DROIT cesse d'être recopié à
    la main : la durée requise d'une génération vit dans une table certifiée,
    et `limites.md` la redisait de mémoire.
    """
    table = "data/reference/legislation/duree_assurance_requise.csv:trimestres"
    assert verifier_prose.sonde_cellule(f"{table}?generation=1966") == 172
    assert verifier_prose.sonde_maximum(table) == 172
    assert verifier_prose.sonde_minimum(table) < 172
    minoration = ("data/reference/legislation/coefficient_minoration.csv"
                  ":coefficient*100")
    assert verifier_prose.sonde_minimum(minoration) == pytest.approx(1.25)
    revalorisation = ("data/reference/legislation/revalorisation_salaires.csv"
                      ":date_effet")
    assert verifier_prose.sonde_distinctes(revalorisation) >= 10


def test_une_cellule_doit_etre_designee_sans_ambiguite():
    """Deux lignes pour une cellule, c'est une désignation qui se croit
    précise : le barème de la surcote porte trois lignes pour 2007, et les
    confondre donnerait le taux d'une autre règle."""
    surcote = "data/reference/legislation/surcote_baremes.csv:taux"
    with pytest.raises(ValueError):
        verifier_prose.sonde_cellule(f"{surcote}?bareme=regime_general&debut=2007")
    with pytest.raises(ValueError):
        verifier_prose.sonde_cellule(f"{surcote}?bareme=nexiste_pas")


def test_partout_refuse_une_valeur_qui_ne_l_est_plus():
    """`partout` dit « toutes les entrées portent ce nombre », et c'est une
    affirmation : le jour où l'une s'en écarte, la prose qui l'annonce une
    fois est devenue fausse, et la sonde doit le dire plutôt que choisir."""
    fiches = "data/reference/regimes/complementaires_prive.yaml:regimes"
    assert verifier_prose.sonde_partout(
        f"{fiches}.*.periodes.*.plafond_majoration_enfants") == 2367
    with pytest.raises(ValueError):
        verifier_prose.sonde_partout(f"{fiches}.*.periodes.*.debut")


def test_une_sonde_peut_traverser_un_cran_d_entrees():
    """`institutions.*.jeux` réunit les jeux de toutes les institutions.

    Le manifeste des sources range ses jeux par institution, et leur nombre —
    le seul que la méthodologie cite — ne se lit nulle part sans ce passage :
    elle en annonçait « cent vingt » en toutes lettres.
    """
    manifeste = "data/sources.yaml:institutions"
    institutions = verifier_prose.sonde_entrees(manifeste)
    jeux = verifier_prose.sonde_entrees(f"{manifeste}.*.jeux")
    assert jeux > institutions > 0


def test_une_ancre_citee_dans_un_bloc_de_code_n_est_pas_evaluee():
    """`docs/fraicheur.md` montre la forme de l'ancre dans un bloc de code.

    Le contrôle allait chercher le fichier que cette citation nomme, et
    échouait de n'y rien trouver : une documentation de la syntaxe n'est pas
    une affirmation, et n'a rien à tenir.
    """
    texte = ("```markdown\n"
             "<!--chiffre:lignes(src/.../actuel.py)-->4 251<!--/--> lignes\n"
             "```\n")
    _, anomalies = verifier_prose.verifier_ancres("exemple.md", texte)
    assert not anomalies


# --- L'outillage d'interface : la prose et le script qui l'installe --------

def test_l_outillage_annonce_les_versions_qu_il_installe():
    """`docs/outillage_interface.md` cite trois versions, et le dépôt les porte.

    C'est la dérive que l'action 41 poursuit, dans un coin où le contrôle par
    ancre ne peut rien : `verifier_prose.py` ne lit pas un numéro de version —
    « 0.1.20 » n'est pas un chiffre au sens de son motif. Les poids en
    mégaoctets que ces versions portent, eux, sont tenus par le test suivant.
    Les VERSIONS sont dans le dépôt : la compétence porte la
    sienne dans son en-tête, le moteur dans son fichier `VERSION`, et le CLI
    Playwright dans le script d'installation. Une prose qui les cite et un
    script qui en installe d'autres se seraient séparés sans bruit.
    """
    doc = (RACINE / "docs" / "outillage_interface.md").read_text(encoding="utf-8")

    skill = (RACINE / ".claude" / "skills" / "impeccable" / "SKILL.md").read_text(
        encoding="utf-8")
    competence = re.search(r"^version: (\S+)$", skill, re.MULTILINE).group(1)
    moteur = (RACINE / ".claude" / "skills" / "impeccable" / "scripts"
              / "VERSION").read_text(encoding="utf-8").strip()
    installe = (RACINE / "scripts" / "setup_ui_tools.sh").read_text(encoding="utf-8")
    playwright = re.search(r"^PLAYWRIGHT_CLI_VERSION=(\S+)$", installe,
                           re.MULTILINE).group(1)

    attendus = {
        f"{competence} (compétence), moteur {moteur}":
            "la ligne Impeccable du tableau « Ce qu'un clone frais contient déjà »",
        f"`~/.impeccable/bin/{moteur}/`":
            "le cache du moteur, versionné par son numéro",
        f"(tag `engine-v{moteur}`)":
            "le tag de la release d'où le lanceur tire le binaire",
        f"`@playwright/cli` {playwright}":
            "la ligne Playwright CLI du même tableau",
        f"**`@playwright/cli@{playwright}`**":
            "la puce « Ce qui demande le réseau »",
    }
    manquants = [f"{quoi} : « {texte} »"
                 for texte, quoi in attendus.items() if texte not in doc]
    assert manquants == [], (
        "docs/outillage_interface.md ne dit plus les versions que le dépôt "
        "porte — " + " ; ".join(manquants)
    )


#: Ce que `docs/outillage_interface.md` affirme de logiciels installés HORS du
#: dépôt, et la version figée sur laquelle chaque chiffre a été lu. Aucune
#: sonde n'atteint un binaire qu'un clone n'a pas ; mais une version publiée ne
#: change plus, et ce qu'on a mesuré sur elle reste vrai tant que le dépôt la
#: fige. Chaque ligne : la phrase du document, l'outil, la version mesurée, et
#: comment la mesure a été faite.
MESURES_HORS_DEPOT = (
    ("le moteur natif (16 Mo)", "moteur", "0.1.5",
     "16 089 424 octets, le binaire linux-x64 de ~/.impeccable/bin/0.1.5/, "
     "le 23 septembre 2026"),
    ("(« Chrome for Testing », une archive de ~190 Mo)", "playwright", "0.1.20",
     "196 289 395 octets : l'archive linux64 de Chrome for Testing "
     "154.0.8037.0, la révision 1244 que playwright-core 1.64.0-alpha-2026-09-14 "
     "attend, lue sur cdn.playwright.dev le 23 septembre 2026"),
    ("(activé, cinq constats, 8 000 caractères)", "moteur", "0.1.5",
     "`impeccable hooks status` sans configuration, le 23 septembre 2026"),
)


def test_les_chiffres_de_l_outillage_sont_ceux_des_versions_figees():
    """Trois chiffres du document décrivent des logiciels que le dépôt n'a pas.

    Le poids du moteur d'Impeccable, celui du Chromium que le CLI Playwright
    télécharge, le plafond de caractères du hook : `verifier_prose.py` ne peut
    en recalculer aucun depuis un clone, et ils sont restés trois jours dans
    des sections que personne ne déclarait. Ils ne sont pourtant pas des
    souvenirs, puisqu'ils décrivent une VERSION, et qu'une version publiée ne
    change plus. Ce test lie chacun à la sienne : il échoue dès que le dépôt
    en fige une autre, et c'est le moment de remesurer — puis d'écrire ici le
    nouveau chiffre et la nouvelle version. Le document les ancre sur lui.
    """
    doc = re.sub(r"<!--chiffre:[^>]*-->|<!--/-->", "",
                 (RACINE / "docs" / "outillage_interface.md").read_text(encoding="utf-8"))
    installe = (RACINE / "scripts" / "setup_ui_tools.sh").read_text(encoding="utf-8")
    figees = {
        "moteur": (RACINE / ".claude" / "skills" / "impeccable" / "scripts"
                   / "VERSION").read_text(encoding="utf-8").strip(),
        "playwright": re.search(r"^PLAYWRIGHT_CLI_VERSION=(\S+)$", installe,
                                re.MULTILINE).group(1),
    }
    for phrase, outil, mesuree, comment in MESURES_HORS_DEPOT:
        assert figees[outil] == mesuree, (
            f"« {phrase} » a été mesuré sur {outil} {mesuree} ({comment}), et le "
            f"dépôt fige désormais {figees[outil]} : remesurer, puis mettre à jour "
            "MESURES_HORS_DEPOT et docs/outillage_interface.md"
        )
        assert phrase in doc, f"docs/outillage_interface.md ne dit plus « {phrase} »"


def test_aucun_paragraphe_n_est_repete_a_la_suite():
    """Une résolution de conflit qui garde les deux côtés laisse deux fois le
    même paragraphe, et rien ne le voit : les chiffres ancrés de chaque copie
    sont justes, `verifier_prose.py` les corrige tous. Le 21 septembre 2026,
    deux résolutions successives ont ainsi porté à quatre exemplaires la phrase
    de la feuille de route sur le coût transversal d'un changement du modèle,
    et elle y est restée une journée entière. Quand un conflit ne porte que
    sur des chiffres ancrés, on garde UN côté et l'on relance le script."""
    doublons = []
    for chemin in [RACINE / "README.md", RACINE / "CLAUDE.md",
                   *sorted((RACINE / "docs").glob("*.md"))]:
        paragraphes = [p.strip() for p in
                       re.split(r"\n\s*\n", chemin.read_text(encoding="utf-8"))]
        for rang in range(1, len(paragraphes)):
            courant = paragraphes[rang]
            if len(courant) > 40 and courant == paragraphes[rang - 1]:
                doublons.append(f"{chemin.name} : « {courant[:60]}… »")
    assert not doublons, doublons


def test_une_action_close_passe_a_l_archive_de_la_feuille_de_route():
    """La feuille de route ne porte que ce qui vit (docs/architecture.md, § 9.3).

    Une action faite, archivée ou abandonnée passe, telle quelle, à la fin de
    `docs/archives/feuille_de_route.md` ; une action en cours reste dans la
    feuille de route, où les sessions ouvrent les leurs. Deux numéros servent
    deux fois, 37 et 38 : une action se reconnaît à son numéro et à son
    titre, et n'est jamais des deux côtés.
    """
    motif = re.compile(r"^### (\d+)\. (.*) — `([^`]+)`\s*$", re.M)
    vivantes = motif.findall(
        (RACINE / "docs" / "feuille_de_route.md").read_text(encoding="utf-8"))
    closes = motif.findall(
        (RACINE / "docs" / "archives" / "feuille_de_route.md").read_text(encoding="utf-8"))
    etats_clos = {"fait", "abandonnée", "archivée"}
    restees = [f"{n}. {t}" for n, t, etat in vivantes if etat in etats_clos]
    assert not restees, (
        f"{restees} : une action close passe, telle quelle, à la fin de "
        "docs/archives/feuille_de_route.md")
    rouvertes = [f"{n}. {t}" for n, t, etat in closes if etat not in etats_clos]
    assert not rouvertes, f"{rouvertes} : une action ouverte n'est pas dans l'archive"
    assert not {(n, t) for n, t, _ in vivantes} & {(n, t) for n, t, _ in closes}
