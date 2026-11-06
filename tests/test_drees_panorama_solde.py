"""Le solde du suivi du panorama de la DREES, édition 2026 (action 178, étape 7).

Les feuilles des classeurs que les étapes 2 à 6 n'avaient pas lues, lues
à la source et recoupées à ce que le dépôt porte déjà : les comptes de la
protection sociale (fiche 10), l'EACR, son cadrage et sa table C (fiches 1 et
3), l'enquête sur les allocations du minimum vieillesse, que l'INSEE
rediffuse (fiche 28), les séries par génération (fiche 17) et le cumul
emploi-retraite (fiche 23).

LE TÉMOIN, ``tests/temoins/drees_panorama_2026_solde.json`` : chaque valeur
recopiée de sa cellule, dans le classeur de sa fiche, et les phrases du PDF que
les tests citent, à leur page imprimée (le folio est la page du fichier moins
un). ``test_chaque_valeur_du_temoin_est_celle_de_sa_cellule`` et
``test_chaque_citation_du_temoin_est_dans_le_pdf`` le relisent aux classeurs et
au PDF quand ``data/brut/`` les porte
(``python scripts/fetch/source_locale.py --recuperer``).

Un écart ne se corrige pas ici : il se déclare dans le test qui le mesure,
borné, pour qu'un écart qui bouge se voie. La note de l'étape est
``docs/feuille_de_route/178/2026-11-06-etape-7-solde-du-suivi.md``.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import lecture_xlsx  # noqa: E402
import source_locale  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "drees_panorama_2026_solde.json"
EACR = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"
MACRO = RACINE / "data" / "reference" / "macro"
EFFECTIFS = RACINE / "data" / "reference" / "regimes" / "effectifs_retraites.csv"
SUIVI = RACINE / "data" / "reference" / "drees_panorama_2026.yaml"


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def eacr() -> dict:
    return json.loads(EACR.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def effectifs() -> dict[tuple[int, str], float]:
    return {(int(l["annee"]), l["caisse"]): float(l["effectifs"]) for l in _lire(EFFECTIFS)}


def _v(temoin: dict, cle: str, *chemin: str):
    """La valeur de la cellule que le témoin range sous ``cle`` et ``chemin``."""
    noeud = temoin["valeurs"][cle]
    for pas in chemin:
        noeud = noeud[pas]
    return noeud["valeur"]


# --- Le témoin -----------------------------------------------------------------


def _cellules(noeud):
    """Les cellules du témoin : une feuille de sa cellule, ou un bloc (« plage »),
    déplié cellule par cellule."""
    if isinstance(noeud, dict) and "plage" in noeud:
        debut, fin = noeud["plage"].split(":")
        (l0, c0), (l1, c1) = _indices(debut), _indices(fin)
        assert len(noeud["valeurs"]) == l1 - l0 + 1
        for ligne, valeurs in zip(range(l0, l1 + 1), noeud["valeurs"]):
            assert len(valeurs) == c1 - c0 + 1
            for colonne, valeur in zip(range(c0, c1 + 1), valeurs):
                yield {"classeur": noeud["classeur"], "feuille": noeud["feuille"],
                       "indices": (ligne, colonne), "valeur": valeur}
    elif isinstance(noeud, dict) and "classeur" in noeud:
        yield {**noeud, "indices": _indices(noeud["cellule"])}
    elif isinstance(noeud, dict):
        for valeur in noeud.values():
            yield from _cellules(valeur)


def _indices(reference: str) -> tuple[int, int]:
    lettres, ligne = re.fullmatch(r"([A-Z]+)(\d+)", reference).groups()
    colonne = 0
    for lettre in lettres:
        colonne = colonne * 26 + ord(lettre) - ord("A") + 1
    return int(ligne) - 1, colonne - 1


def _depose(ident: str) -> Path | None:
    """Le document du manifeste dans ``data/brut/``, s'il y est et porte son empreinte."""
    jeu = next(j for j in source_locale.jeux_bloques() if j["id"] == ident)
    chemin = source_locale.ou_deposer(jeu)
    if chemin is None or not chemin.is_file():
        return None
    if jeu.get("sha256") and source_locale.empreinte(chemin.read_bytes()) != jeu["sha256"]:
        return None
    return chemin


def test_chaque_valeur_du_temoin_est_celle_de_sa_cellule(temoin):
    """Chaque valeur du témoin est celle que le classeur de sa fiche porte, à la
    cellule que le témoin nomme, au bit près."""
    archive = _depose("drees_panorama_retraites_2026_classeurs")
    if archive is None:
        pytest.skip("classeurs absents de data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    cellules = list(_cellules(temoin["valeurs"]))
    assert len(cellules) > 2800
    grilles: dict = {}
    with zipfile.ZipFile(archive) as classeurs:
        for cellule in cellules:
            cle = (cellule["classeur"], cellule["feuille"])
            if cle not in grilles:
                grilles[cle] = lecture_xlsx.feuilles(
                    classeurs.read(cellule["classeur"]), (cellule["feuille"],))[cellule["feuille"]]
            assert grilles[cle].get(cellule["indices"]) == cellule["valeur"], cellule


def test_chaque_citation_du_temoin_est_dans_le_pdf(temoin):
    """Les phrases que les tests citent sont celles du PDF, lu dans l'ordre de
    lecture, césures et espaces mis à part, et à la page imprimée que le témoin
    nomme."""
    pdf = _depose("drees_panorama_retraites_2026")
    if pdf is None or shutil.which("pdftotext") is None:
        pytest.skip("PDF absent de data/brut/, ou pdftotext absent")
    pages = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, check=True,
                           text=True).stdout.replace("­", "").split("\f")
    plat = [" ".join(re.sub(r"-\n(?=\w)", "", page).split()) for page in pages]
    assert temoin["citations"]
    for cle, bloc in temoin["citations"].items():
        for phrase in bloc["textes"]:
            attendue = " ".join(phrase.split())
            assert attendue in plat[bloc["page"]], (cle, bloc["page"], phrase)


def _bloc(temoin: dict, cle: str, *chemin: str) -> list[list]:
    """Les valeurs d'un bloc du témoin, ``[ligne][colonne]``."""
    noeud = temoin["valeurs"][cle]
    for pas in chemin:
        noeud = noeud[pas]
    return noeud["valeurs"]


# --- Fiche 10 : les masses financières ---------------------------------------


def test_les_pensions_de_droit_direct_et_de_droit_derive_de_l_encadre_1_sont_celles_du_depot(temoin):
    """Fiche 10, encadré 1 (folio 99), feuille « F10_Tableau encadré 1 » : en 2024,
    426,7 milliards d'euros de prestations du risque vieillesse-survie, dont
    359,7 de pensions de droit direct (C7) et 41,7 de droit dérivé (C17). Le dépôt
    porte le risque entier (``depenses_retraite.csv``, poste E11-2 : 426 665,3
    millions) et les deux sous-postes (``pensions_droits.csv``, E11-21.1 et
    E11-22.1 : 359 717,10 et 41 709,29). Leur somme, 401,4, est celle que les
    en-têtes des deux fichiers écrivent."""
    droits = {l["categorie"]: float(l["montant_meur"]) for l in _lire(MACRO / "pensions_droits.csv")
              if l["annee"] == "2024"}
    depenses = {int(l["annee"]): float(l["depenses_meur"]) for l in _lire(MACRO / "depenses_retraite.csv")}
    direct, derive = _v(temoin, "10_encadre_1", "direct"), _v(temoin, "10_encadre_1", "derive")
    assert droits["direct"] / 1000 == pytest.approx(direct, abs=0.05)
    assert droits["derive"] / 1000 == pytest.approx(derive, abs=0.05)
    assert depenses[2024] / 1000 == pytest.approx(_v(temoin, "10_encadre_1", "cps_total"), abs=0.05)
    assert direct + derive == pytest.approx(401.4)
    assert (droits["direct"] + droits["derive"]) / 1000 == pytest.approx(401.4, abs=0.05)


def test_le_champ_des_pensions_de_retraite_fait_93_pour_cent_du_risque_vieillesse_survie(temoin):
    """Fiche 10, folio 99 : « le champ des pensions de retraite des régimes
    légalement obligatoires français (PRRO) [...] correspond à 93 % des
    prestations du risque vieillesse-survie en 2024 ». L'encadré 1 le redonne :
    395,3 / 426,7 = 0,9264, 93 % arrondi (feuille « F10_Tableau encadré 1 », D5
    et C5)."""
    part = 100 * _v(temoin, "10_encadre_1", "prro_total") / _v(temoin, "10_encadre_1", "cps_total")
    assert part == pytest.approx(92.64, abs=0.005)
    assert round(part) == 93
    assert "93 %" in temoin["citations"]["10_encadre_1"]["textes"][0]
    # Ses deux sous-postes : 354,2 de droit direct et 41,1 de droit dérivé font 395,3.
    assert (_v(temoin, "10_encadre_1", "direct_prro") + _v(temoin, "10_encadre_1", "derive_prro")
            == pytest.approx(_v(temoin, "10_encadre_1", "prro_total")))


def test_le_pib_du_panorama_est_celui_du_depot_jusqu_en_2022_et_s_en_ecarte_ensuite(temoin):
    """Fiche 10, graphique 1 (feuille « F10_Graphique1 », ligne 9, « PIB en valeur
    (en milliards) ») : de 1990 à 2022, le PIB du panorama est, au million
    d'euros, celui de ``pib_courant.csv`` (INSEE, comptes nationaux, base 2020).
    En 2023 et en 2024 il est plus bas, de 0,26 et de 0,52 % : 2 826,542 contre
    2 833,826, et 2 919,900 contre 2 935,236. La source ne dit pas le millésime
    de son PIB (« Drees, CPS, données semi-définitives pour 2023 et provisoires
    pour 2024 », folio 100) : l'écart est déclaré, non expliqué. Il ne change
    pas les parts publiées, 13,1 % en 2023 et 13,5 % en 2024, qu'avec le PIB du
    dépôt on retrouve à l'arrondi (13,07 et 13,47)."""
    pib = {int(l["annee"]): float(l["pib_meur"]) for l in _lire(MACRO / "pib_courant.csv")}
    for annee in range(1990, 2023):
        assert pib[annee] / 1000 == pytest.approx(_v(temoin, "10_graphique_1", "pib", str(annee)),
                                                  abs=0.0006), annee
    ecart = {a: 100 * (_v(temoin, "10_graphique_1", "pib", str(a)) / (pib[a] / 1000) - 1)
             for a in (2023, 2024)}
    assert ecart[2023] == pytest.approx(-0.26, abs=0.01)
    assert ecart[2024] == pytest.approx(-0.52, abs=0.01)
    for annee, publie in ((2023, _v(temoin, "10_tableau_1", "part_pib_2023")),
                          (2024, _v(temoin, "10_tableau_1", "part_pib_2024"))):
        masse = _v(temoin, "10_graphique_1", "pensions", str(annee))
        du_depot = 100 * masse / pib[annee]
        assert round(du_depot, 1) == publie, annee
        # Avec son propre PIB, la source retrouve la cellule de la part, au centième.
        sien = _v(temoin, "10_graphique_1", "pib", str(annee))
        assert 100 * (masse / 1000) / sien == pytest.approx(
            _v(temoin, "10_graphique_1", "part_pib", str(annee)), abs=0.0005), annee


def test_la_part_du_pib_de_la_comparaison_europeenne_utilise_le_pib_du_panorama_et_les_regimes_verseurs_font_le_total(temoin):
    """Fiche 10, encadré 1, graphique « Prestations du risque vieillesse-survie en
    Europe en 2024 » (feuille « F10_Graphique encadré 1 », ligne 29 pour la France
    : 13,07 % du PIB pour la vieillesse et 1,54 pour la survie, 14,61 en tout) :
    « 14,6 % du PIB en France en 2024 ; [...] 17,0 % du PIB en Italie et 12,3 % du
    PIB en Allemagne » (folio 100). Les 426 665,3 millions du poste E11-2 du dépôt
    sur le PIB du graphique 1, 2 919,9 milliards, font 14,612 %, soit la cellule ;
    sur celui du dépôt, 2 935,2, 14,536 : la comparaison européenne et la part des
    pensions de la fiche 10 ont le même PIB, celui qui s'écarte de ``pib_courant.csv``
    de 0,52 % en 2024. La feuille « F10_Graphique 2 » (répartition par régime
    verseur, en milliards, colonnes K à M pour 2022 à 2024) : les cinq lignes font
    le total, à deux milliards près, l'arrondi de cinq termes (141 + 100 + 92 + 20 + 1 = 354
    pour 353 en 2022, 372 pour 370 en 2023, 159 + 110 + 104 + 22 + 1 = 396 pour 395 en 2024),
    et le total arrondit la masse du graphique 1 (352,66, 370,47, 395,34) ; le
    régime général verse 159 / 395 = 40,3 %, les « 40 % » du texte."""
    depenses = {int(l["annee"]): float(l["depenses_meur"]) for l in _lire(MACRO / "depenses_retraite.csv")}
    pib = {int(l["annee"]): float(l["pib_meur"]) for l in _lire(MACRO / "pib_courant.csv")}
    publie = _v(temoin, "10_graphique_encadre_1", "france_somme")
    assert 100 * depenses[2024] / 1000 / _v(temoin, "10_graphique_1", "pib", "2024") == pytest.approx(publie, abs=0.005)
    assert 100 * depenses[2024] / pib[2024] == pytest.approx(14.536, abs=0.001)
    assert abs(100 * depenses[2024] / pib[2024] - publie) > 0.05
    assert (_v(temoin, "10_graphique_encadre_1", "france_vieillesse")
            + _v(temoin, "10_graphique_encadre_1", "france_survie")) == pytest.approx(publie, abs=0.011)
    assert round(publie, 1) == 14.6
    assert round(_v(temoin, "10_graphique_encadre_1", "italie_somme"), 1) == 17.0
    assert round(_v(temoin, "10_graphique_encadre_1", "allemagne_somme"), 1) == 12.3
    montants = _bloc(temoin, "10_graphique_2", "montants")
    for k, annee in enumerate(("2022", "2023", "2024")):
        assert sum(montants[i][k] for i in range(5)) - montants[5][k] == (1, 2, 1)[k], annee
        assert montants[5][k] == round(_v(temoin, "10_graphique_1", "pensions", annee) / 1000), annee
    assert 100 * montants[0][2] / montants[5][2] == pytest.approx(40.3, abs=0.05)
    assert _v(temoin, "10_graphique_2", "regime_general_2024_pour_cent") == 40


def test_les_evolutions_du_tableau_2_sont_celles_de_la_serie_du_graphique_1(temoin):
    """Fiche 10, tableau 2 (folio 101) : « les dépenses totales relatives aux
    pensions augmentent de 6,7 % en euros courants [en 2024], après +5,0 % en
    2023 ». La série du graphique 1 (millions d'euros, lignes 5 à 7) les redonne :
    370 465,23 / 352 661,25 − 1 = 5,05 % (5,0 publié), 395 338,73 / 370 465,23 − 1
    = 6,71 % ; le droit direct 5,18 et 6,95 % (5,2 et 6,9), le droit dérivé 3,93 et
    4,76 % (3,9 et 4,8) ; de 1990 à 2024, (395 338,73 / 105 934,19)^(1/34) − 1 =
    3,95 % (3,9), le droit direct 4,24 (4,2), le droit dérivé 2,19 (2,2). La
    cellule D7 du tableau 2, 5,0, est du texte (« 5,0 »), non un nombre."""
    def serie(ligne: str, annee: str) -> float:
        return _v(temoin, "10_graphique_1", ligne, annee)

    cas = (("pensions", "pensions"), ("direct", "direct"), ("derive", "derive"))
    for ligne, nom in cas:
        annuelle_23 = 100 * (serie(ligne, "2023") / serie(ligne, "2022") - 1)
        annuelle_24 = 100 * (serie(ligne, "2024") / serie(ligne, "2023") - 1)
        moyenne = 100 * ((serie(ligne, "2024") / serie(ligne, "1990")) ** (1 / 34) - 1)
        assert round(annuelle_23, 1) == float(str(_v(temoin, "10_tableau_2", f"{nom}_2022_2023")).replace(",", ".")), nom
        assert round(annuelle_24, 1) == _v(temoin, "10_tableau_2", f"{nom}_2023_2024"), nom
        assert round(moyenne, 1) == _v(temoin, "10_tableau_2", f"{nom}_1990_2024"), nom
    assert _v(temoin, "10_tableau_2", "pensions_2022_2023") == "5,0"
    assert isinstance(_v(temoin, "10_tableau_2", "pensions_2022_2023"), str)
    assert isinstance(_v(temoin, "10_tableau_2", "pensions_2023_2024"), float)


# --- Fiches 1 et 3 : les effectifs de retraités -------------------------------


def _retraites_par_age(eacr: dict, sexe: str) -> tuple[dict[int, float], float]:
    """Les retraités de droit direct de fin 2024 de la table C de l'EACR, par âge,
    et leur total ; ``plus de 95`` est ce que les âges isolés ne comptent pas."""
    serie = eacr["droits_directs_par_age"]["series"]["ddir"][sexe]
    ages = {int(a): v[0] for a, v in serie.items() if a.isdigit() and v[0]}
    ages[999] = serie["plus de 95"][0]
    return ages, serie["Ensemble"][0]


def _bande(ages: dict[int, float], bas: int, haut: int) -> float:
    return sum(v for a, v in ages.items() if bas <= a <= haut)


BANDES_DE_LA_PYRAMIDE = {
    "moins_de_50": (0, 49), "50_54": (50, 54), "55_59": (55, 59), "60_64": (60, 64),
    "65_69": (65, 69), "70_74": (70, 74), "75_79": (75, 79), "80_84": (80, 84),
    "85_89": (85, 89), "90_et_plus": (90, 999),
}


def test_la_pyramide_des_ages_de_la_fiche_1_est_celle_de_la_table_c(temoin, eacr):
    """Fiche 1, graphique 4 (folio 27, feuille « F01_Graphique 4 », C5:D14) :
    la part de chaque sexe et de chaque classe d'âge dans les 17 298 245
    retraités de droit direct de fin 2024. La table C de l'EACR (Ancetre 2024)
    les compte, âge par âge : chaque cellule est retrouvée au dixième près
    (l'arrondi de la source), et les dix classes de chaque sexe font son total,
    53,1 % de femmes."""
    total = eacr["droits_directs_par_age"]["series"]["ddir"]["ensemble"]["Ensemble"][0]
    assert total == pytest.approx(17_298_245)
    somme = 0.0
    for sexe in ("F", "H"):
        ages, effectif = _retraites_par_age(eacr, sexe)
        for classe, (bas, haut) in BANDES_DE_LA_PYRAMIDE.items():
            part = 100 * _bande(ages, bas, haut) / total
            assert part == pytest.approx(_v(temoin, "01_graphique_4", sexe, classe), abs=0.0501), (sexe, classe)
            somme += part
        # Les âges isolés et « plus de 95 » font le total à six personnes près (hommes) :
        # un arrondi de la table.
        assert _bande(ages, 0, 999) == pytest.approx(effectif, abs=10)
    assert somme == pytest.approx(100, abs=1e-3)
    assert 100 * _retraites_par_age(eacr, "F")[1] / total == pytest.approx(53.1, abs=0.05)


def test_les_caisses_du_tableau_2_complementaire_de_la_fiche_1_sont_celles_du_cadrage(temoin, effectifs):
    """Fiche 1, feuille « F01_Tableau 2 compl » : les retraités de droit direct de
    fin 2024 de 17 caisses et du total, en milliers, et leur évolution de 2023 à
    2024, de 2020 à 2024 et de 2014 à 2024. Le cadrage de l'EACR
    (``effectifs_retraites.csv``) les redonne : l'effectif à mille près, chaque
    évolution à un dixième de point près. Quatre cellules de 2014-2024 ne se
    recoupent pas : le cadrage n'a pas 2014 pour l'Agirc-Arrco (deux caisses
    alors), la Banque de France, la CANSSM et l'Enim, et la source écrit 0 pour les
    trois dernières (la CANSSM aurait dû croître de 30,7 % entre 2014 et 2020
    pour que 2014 et 2024 s'égalent, 1 / 0,765 = 1,307, quand elle perd 23,5 % de
    2020 à 2024 : un 0 de cellule non disponible, non une évolution nulle ; à ne pas
    citer). Enfin le régime général : 13,2 % publiés contre 14,1 au cadrage pour
    2014-2024, 0,9 point d'écart que le renvoi de la source (« intégration de la
    SSI au régime général ») ne chiffre pas."""
    sans_2014 = {"agirc_arrco", "banque_de_france", "canssm", "enim"}
    caisses = [c for c in temoin["valeurs"]["01_tableau_2_compl"]]
    assert len(caisses) == 19
    for caisse in caisses:
        ligne = temoin["valeurs"]["01_tableau_2_compl"][caisse]
        cadrage = "tous_regimes" if caisse == "tous_regimes" else caisse
        e24 = effectifs[(2024, cadrage)]
        assert e24 / 1000 == pytest.approx(ligne["effectifs"]["valeur"], abs=0.5001), caisse
        for cle, annee in (("evolution_2023_2024", 2023), ("evolution_2020_2024", 2020)):
            refait = 100 * (e24 / effectifs[(annee, cadrage)] - 1)
            assert refait == pytest.approx(ligne[cle]["valeur"], abs=0.0501), (caisse, cle)
        publiee = ligne["evolution_2014_2024"]["valeur"]
        if caisse in sans_2014:
            assert (2014, cadrage) not in effectifs, caisse
            if caisse != "agirc_arrco":
                assert publiee == 0.0, caisse
        elif caisse == "cnav":
            refait = 100 * (e24 / effectifs[(2014, cadrage)] - 1)
            assert refait == pytest.approx(14.1, abs=0.05)
            assert publiee == pytest.approx(13.2)
        else:
            refait = 100 * (e24 / effectifs[(2014, cadrage)] - 1)
            assert refait == pytest.approx(publiee, abs=0.0501), caisse
    canssm = temoin["valeurs"]["01_tableau_2_compl"]["canssm"]["evolution_2020_2024"]["valeur"]
    assert 1 / (1 + canssm / 100) == pytest.approx(1.307, abs=0.001)
    assert "intégration de la SSI au régime général" in temoin["citations"]["01_tableau_2"]["textes"][0]


def test_les_flux_de_la_fiche_1_se_deduisent_du_stock_et_les_primo_liquidants_sont_718_mille(temoin, eacr):
    """Fiche 1, graphique 2 (folio 22, feuille « F01_Graphique 2 ») : la variation
    annuelle du nombre de retraités est la différence de leur stock (feuille
    « F01_Tableau 1 », colonne E), à un millier près ; son taux, rapporté au stock
    de l'année d'avant, au dixième près ; 2018 à 2020 sont « nd » (la source en
    note : des fragilités et une rupture). Les nouveaux retraités de 2024, 717,6
    mille (C24), font les « 718 000 primo-liquidants » du texte (folio 29), sur
    les « 858 000 » liquidants de tous régimes : 857 880 à la table C, 140,28 mille
    de plus, des assurés qui avaient déjà liquidé un autre droit direct."""
    stock = {a: _v(temoin, "01_tableau_1", str(a)) for a in range(2004, 2025)}
    for annee in range(2005, 2025):
        ligne = temoin["valeurs"]["01_graphique_2"][str(annee)]
        variation, taux = ligne["variation"]["valeur"], ligne["evolution"]["valeur"]
        if annee in (2018, 2019, 2020):
            assert (variation, taux) == ("nd", "nd"), annee
            continue
        assert variation == pytest.approx(stock[annee] - stock[annee - 1], abs=1.0), annee
        assert taux == pytest.approx(100 * variation / stock[annee - 1], abs=0.0601), annee
    primo = _v(temoin, "01_graphique_2", "2024", "nouveaux")
    assert primo == pytest.approx(717.6)
    assert round(primo) == 718
    liquidants = eacr["droits_directs_par_age"]["series"]["nl_ddir"]["ensemble"]["Ensemble"][0]
    assert liquidants == pytest.approx(857_880)
    assert liquidants / 1000 - primo == pytest.approx(140.28, abs=0.01)
    assert "718 000" in temoin["citations"]["01_flux"]["textes"][0]


def test_le_tableau_3_de_la_fiche_1_se_recoupe_et_ses_polypensionnes_sont_ceux_du_tableau_2_complementaire(temoin):
    """Fiche 1, feuille « F01_Tableau 3 » (folio 25) : 17 300 milliers de retraités
    de droit direct, dont 17 140 d'un régime de base et 160 « autres », arrondis
    à la dizaine ; les quatre lignes du régime principal font 17 130 (12 130 + 3
    990 + 820 + 190), comme les 12 700 monopensionnés et 4 430 polypensionnés de
    la cellule G19 et G20 : dix de moins que les 17 140, l'arrondi. La part de
    polypensionnés, 25,6 % (H20), est 4 430 / 17 300 ; la feuille « F01_Tableau 2
    compl » l'arrondit à 26 (F6)."""
    def t3(cle):
        return _v(temoin, "01_tableau_3", cle)

    assert t3("regime_de_base") + t3("autres") == t3("tous")
    quatre = t3("regime_general") + t3("autre_salarie") + t3("autre_non_salarie") + t3("aucun_regime_principal")
    assert quatre == 17_130
    assert abs(quatre - t3("regime_de_base")) <= 20
    assert t3("monopensionnes") + t3("polypensionnes") == 17_130
    assert 100 * t3("polypensionnes") / t3("tous") == pytest.approx(25.6, abs=0.05)
    assert t3("part_polypensionnes") == pytest.approx(25.6)
    assert round(t3("part_polypensionnes")) == _v(temoin, "01_tableau_2_compl", "tous_regimes", "polypensionnes")
    assert t3("tous") == pytest.approx(_v(temoin, "01_tableau_1", "2024"), abs=5)


def test_les_ages_des_retraites_de_droit_direct_du_tableau_3_de_la_fiche_3_sont_ceux_de_la_table_c(temoin, eacr):
    """Fiche 3, feuille « F03_Tableau 3 » (folio 38), colonne F, « Ensemble des
    bénéficiaires d'une pension de droit direct » : 17 298 milliers, 53,1 % de
    femmes, et par âge 1,2 (moins de 60 ans), 11,2 (60 à 64), 43,1 (65 à 74), 30,5
    (75 à 84) et 14,0 % (85 ans ou plus). La table C de l'EACR (Ancetre 2024) les
    redonne au dixième près."""
    total = eacr["droits_directs_par_age"]["series"]["ddir"]["ensemble"]["Ensemble"][0]
    ages = {}
    for sexe in ("F", "H"):
        for age, effectif in _retraites_par_age(eacr, sexe)[0].items():
            ages[age] = ages.get(age, 0) + effectif
    bandes = {"moins_de_60": (0, 59), "60_64": (60, 64), "65_74": (65, 74), "75_84": (75, 84),
              "85_et_plus": (85, 999)}
    for classe, (bas, haut) in bandes.items():
        part = 100 * _bande(ages, bas, haut) / total
        assert part == pytest.approx(_v(temoin, "03_tableau_3", "ages_droit_direct", classe), abs=0.0501), classe
    assert 100 * _retraites_par_age(eacr, "F")[1] / total == pytest.approx(
        _v(temoin, "03_tableau_3", "femmes_droit_direct"), abs=0.0501)
    assert _v(temoin, "03_tableau_3", "effectifs", "droit_direct") == pytest.approx(total / 1000, abs=0.5)


def test_les_effectifs_de_la_reversion_se_recoupent_d_une_feuille_a_l_autre(temoin):
    """Fiche 3 : le dépôt ne garde de la réversion que sa masse
    (``droits_derives.csv``), les effectifs ne se recoupent donc qu'entre les
    feuilles. En 2024 (tableau 1, ligne 26) : 3 836,17 mille femmes et 570,46 mille
    hommes font 4 406,64 (E26, le dernier centième près), dont 886,13 de droit
    dérivé seul (F26) ; les tableaux 2 (E6), 2 complémentaire (E6) et 3 (E5 : 4
    407, D5 : 886, C5 + D5 = 3 521 + 886) les redonnent. Les 3 861,5 mille qui
    résident en France (I26) en font 87,63 %, que le tableau 3 écrit 87,6 (E9). Le
    graphique 1 (variation annuelle, nouveaux retraités du droit dérivé, 258,6 mille
    en 2024) est la différence des stocks de la ligne E, au dixième près, et son
    taux la variation rapportée au stock de l'année d'avant. Le graphique 3, la
    pyramide, fait 100 et retrouve les parts du tableau 3 : les femmes de droit dérivé
    seul, 886 × 95,3 % / 4 407 = 19,2 % ; les femmes et les hommes cumulants, 3 521 ×
    85 % / 4 407 = 67,9 et 3 521 × 15 % / 4 407 = 12,0 %. Dans le tableau 2, les
    évolutions de la CNRACL et de l'Ircantec sont des fractions (0,016 pour 1,6 %,
    -0,01 pour -1 %), quand la feuille complémentaire les écrit en pour cent."""
    ens = {a: temoin["valeurs"]["03_tableau_1"][str(a)] for a in range(2004, 2025)}
    for annee, ligne in ens.items():
        assert ligne["femmes"]["valeur"] + ligne["hommes"]["valeur"] == pytest.approx(
            ligne["ensemble"]["valeur"], abs=0.0201), annee
    e24 = ens[2024]["ensemble"]["valeur"]
    assert e24 == pytest.approx(4406.64)
    assert e24 == _v(temoin, "03_tableau_2", "ensemble") == _v(temoin, "03_tableau_2_compl", "ensemble")
    assert ens[2024]["seul"]["valeur"] == _v(temoin, "03_tableau_2", "seul") == _v(temoin, "03_tableau_2_compl", "seul")
    t3 = temoin["valeurs"]["03_tableau_3"]
    assert round(e24) == t3["effectifs"]["ensemble"]["valeur"]
    assert round(ens[2024]["seul"]["valeur"]) == t3["effectifs"]["seul"]["valeur"]
    assert t3["effectifs"]["cumul"]["valeur"] + t3["effectifs"]["seul"]["valeur"] == t3["effectifs"]["ensemble"]["valeur"]
    assert 100 * ens[2024]["france"]["valeur"] / e24 == pytest.approx(t3["france_ensemble"]["valeur"], abs=0.0501)
    for annee in range(2005, 2025):
        flux = temoin["valeurs"]["03_graphique_1"][str(annee)]
        difference = ens[annee]["ensemble"]["valeur"] - ens[annee - 1]["ensemble"]["valeur"]
        assert flux["variation"]["valeur"] == pytest.approx(difference, abs=0.0601), annee
        assert flux["evolution"]["valeur"] == pytest.approx(
            100 * difference / ens[annee - 1]["ensemble"]["valeur"], abs=0.0601), annee
    assert _v(temoin, "03_graphique_1", "2024", "nouveaux") == pytest.approx(258.6)
    entete = " ".join(l.lstrip("# ") for l in (MACRO / "droits_derives.csv").read_text(encoding="utf-8").splitlines()
                      if l.startswith("#"))
    assert "contre 4,4 au « Tous régimes »" in entete
    assert round(e24 / 1000, 1) == 4.4
    pyramide = {col: sum(abs(v["valeur"]) for v in temoin["valeurs"]["03_graphique_3"][col].values())
                for col in "CDEF"}
    assert sum(pyramide.values()) == pytest.approx(100, abs=0.2)
    base = t3["effectifs"]["ensemble"]["valeur"]
    attendu = {
        "C": t3["effectifs"]["seul"]["valeur"] * t3["femmes_seul"]["valeur"] / 100 / base * 100,
        "D": t3["effectifs"]["cumul"]["valeur"] * t3["femmes_cumul"]["valeur"] / 100 / base * 100,
        "E": t3["effectifs"]["cumul"]["valeur"] * (100 - t3["femmes_cumul"]["valeur"]) / 100 / base * 100,
    }
    for col, valeur in attendu.items():
        assert pyramide[col] == pytest.approx(valeur, abs=0.15), col
    assert pyramide["C"] == pytest.approx(19.2, abs=0.05)
    for periode in ("2023_2024", "2019_2024", "2014_2024"):
        brut = _v(temoin, "03_tableau_2", f"cnracl_{periode}")
        pour_cent = _v(temoin, "03_tableau_2_compl", f"cnracl_{periode}")
        assert brut * 100 == pytest.approx(pour_cent, abs=0.06), periode
    assert _v(temoin, "03_tableau_2", "ircantec_2023_2024") * 100 == pytest.approx(
        _v(temoin, "03_tableau_2_compl", "ircantec_2023_2024"), abs=0.06)


# --- Fiche 28 : les allocataires du minimum vieillesse -----------------------


def _allocataires_2024() -> dict[tuple[str, str, str], float]:
    return {(l["tranche"], l["sexe"], l["menage"]): float(l["milliers"])
            for l in _lire(MACRO / "allocataires_minimum_vieillesse.csv") if l["annee"] == "2024"}


CLASSES_DE_LA_FICHE_28 = {"62_64": "61-64", "65_69": "65-69", "70_74": "70-74", "75_79": "75-79",
                          "80_84": "80-84", "85_89": "85-89", "90_et_plus": "90+"}


def test_les_allocataires_par_age_de_la_fiche_28_sont_ceux_du_classeur_de_l_insee_du_depot(temoin):
    """Fiche 28, feuille « F28_Tableau 1 » (folio 232), colonne G, « Effectifs
    d'allocataires » de l'ASV ou de l'Aspa fin 2024 : 753 900 au total (G14), dont
    691 100 de 65 ans ou plus (G15), arrondis à la centaine. Le classeur de l'INSEE
    que le dépôt lit (``allocataires_minimum_vieillesse.csv``, enquête de la DREES
    sur les allocations du minimum vieillesse) les redonne, classe d'âge par
    classe d'âge, femmes et hommes ensemble, à cinquante près : 62,831 mille de
    62 à 64 ans, 208,574, 200,523, 129,514, 70,277, 45,744 et 36,445 ; total 753,908.
    Ce n'est pas le total que la DREES compte à ses caisses, 754 460 (fiche 27,
    552 de plus) : deux comptages d'un même stock."""
    donnees = _allocataires_2024()
    total = 0.0
    for classe, tranche in CLASSES_DE_LA_FICHE_28.items():
        milliers = donnees[(tranche, "F", "ensemble")] + donnees[(tranche, "H", "ensemble")]
        total += milliers
        publie = _v(temoin, "28_tableau_1", "effectifs", classe)
        assert 1000 * milliers == pytest.approx(publie, abs=50.0001), classe
    assert 1000 * total == pytest.approx(_v(temoin, "28_tableau_1", "ensemble_62_et_plus"), abs=50.0001)
    assert 1000 * (total - donnees[("61-64", "F", "ensemble")] - donnees[("61-64", "H", "ensemble")]) == pytest.approx(
        _v(temoin, "28_tableau_1", "ensemble_65_et_plus"), abs=50.0001)
    assert 754_460 - 1000 * total == pytest.approx(552, abs=1)
    assert "Insee, estimation de la population (France) au 1er janvier 2025" in temoin["citations"]["28_tableau_1"]["textes"][0]


def test_la_repartition_des_allocataires_par_sexe_et_situation_de_la_fiche_28_est_celle_du_depot(temoin):
    """Fiche 28, feuille « F28_Tableau 2 » (folio 232) : la part de chaque sexe et
    de chaque situation conjugale dans les allocataires de chaque classe d'âge
    (lignes 7 à 13) et dans leur ensemble (ligne 15), en %. Le classeur de l'INSEE
    du dépôt les redonne au centième : 77,04 % de personnes seules, 56,36 % de
    femmes, 50,64 % de femmes seules. Les effectifs de la ligne 14 sont ceux du
    classeur à cinquante près (381 700 femmes seules, 199 100 hommes seuls)."""
    donnees = _allocataires_2024()

    def somme(sexe: str, menage: str, tranches) -> float:
        return sum(donnees[(t, s, menage)] for t in tranches for s in sexe)

    tout = list(CLASSES_DE_LA_FICHE_28.values())
    for classe, tranche in list(CLASSES_DE_LA_FICHE_28.items()) + [("ensemble", None)]:
        tranches = tout if tranche is None else [tranche]
        base = somme("FH", "ensemble", tranches)
        publie = (temoin["valeurs"]["28_tableau_2"]["ensemble"] if tranche is None
                  else temoin["valeurs"]["28_tableau_2"]["parts"][classe])
        refait = {
            "femmes_seules": somme("F", "isoles", tranches), "hommes_seuls": somme("H", "isoles", tranches),
            "seuls": somme("FH", "isoles", tranches),
            "femmes_couple": somme("F", "couple", tranches), "hommes_couple": somme("H", "couple", tranches),
            "couple": somme("FH", "couple", tranches),
            "femmes": somme("F", "ensemble", tranches), "hommes": somme("H", "ensemble", tranches),
        }
        for cle, milliers in refait.items():
            assert 100 * milliers / base == pytest.approx(publie[cle]["valeur"], abs=0.0051), (classe, cle)
    effectifs = temoin["valeurs"]["28_tableau_2"]["effectifs"]
    for cle, sexe, menage in (("femmes_seules", "F", "isoles"), ("hommes_seuls", "H", "isoles"),
                              ("femmes_couple", "F", "couple"), ("hommes_couple", "H", "couple"),
                              ("femmes", "F", "ensemble"), ("hommes", "H", "ensemble")):
        assert 1000 * somme(sexe, menage, tout) == pytest.approx(effectifs[cle]["valeur"], abs=50.0001), cle
    assert effectifs["ensemble"]["valeur"] == _v(temoin, "28_tableau_1", "ensemble_62_et_plus")


def test_la_part_des_allocataires_dans_la_population_depend_d_une_population_que_le_depot_n_a_pas(temoin):
    """Fiche 28, feuille « F28_Tableau 1 », colonne F : la part des allocataires
    dans la population du même âge, qui est (note de la feuille, folio 232)
    « Insee, estimation de la population (France) au 1er janvier 2025 ». Le dépôt
    n'a pour 2025 qu'une projection (``population_par_age.csv``, fiabilité
    ``estimee``) : 753,9 mille sur 17,29 millions (1er janvier 2024) font 4,36 %,
    sur 17,58 millions (projection au 1er janvier 2025) 4,29 %, quand la source
    publie 4,32 % (F14), entre les deux ; de même les 65 ans ou plus, 4,68 et 4,59 %
    pour 4,63 (F15). Par classe d'âge la source s'écarte de la projection d'au plus
    0,25 point (90 ans ou plus : 3,82 contre 3,60) : le dénominateur n'est pas
    celui du dépôt, l'écart est déclaré."""
    pop = {(int(l["annee"]), int(l["age"])): float(l["effectif"]) for l in _lire(MACRO / "population_par_age.csv")}

    def population(annee: int, bas: int, haut: int) -> float:
        return sum(v for (a, age), v in pop.items() if a == annee and bas <= age <= haut)

    for cle, bas, nom in (("part_2024_62_et_plus", 62, "ensemble_62_et_plus"), ("part_2024_65_et_plus", 65, "ensemble_65_et_plus")):
        effectif = _v(temoin, "28_tableau_1", nom)
        part_2024 = 100 * effectif / population(2024, bas, 200)
        part_2025 = 100 * effectif / population(2025, bas, 200)
        assert part_2025 < _v(temoin, "28_tableau_1", cle) < part_2024, cle
    classes = {"62_64": (62, 64), "65_69": (65, 69), "70_74": (70, 74), "75_79": (75, 79), "80_84": (80, 84),
               "85_89": (85, 89), "90_et_plus": (90, 200)}
    for classe, (bas, haut) in classes.items():
        effectif = _v(temoin, "28_tableau_1", "effectifs", classe)
        part_2025 = 100 * effectif / population(2025, bas, haut)
        assert part_2025 == pytest.approx(_v(temoin, "28_tableau_1", "part_2024", classe), abs=0.25), classe


# --- Fiches 15 et 16 : le taux de retraités par âge ---------------------------


#: Le taux de la table C moins celui de la source, en points, de 62 à 67 ans.
ECARTS_A_LA_TABLE_C = {62: 0.45, 63: 0.78, 64: 1.05, 65: 1.34, 66: 1.53, 67: 2.13}


def test_le_taux_de_retraites_par_age_est_le_meme_d_une_feuille_a_l_autre_et_proche_de_la_table_c(temoin, eacr):
    """Fiche 16, graphique 1 (folio 146, feuille « F16_Graphique 1 », lignes 8 et
    9, de 62 à 67 ans), fiche 15, graphique 4 (feuille « F15_Graphique 4 », lignes
    25 et 26) et graphique 3 (feuille « F15_Graphique 3 », colonnes V et W) : le
    taux de retraités à chaque âge, en 2023 et en 2024, est le même chiffre dans
    les trois feuilles (48,12 % à 62 ans en 2024, 55,6 en 2023). Les taux de
    nouveaux retraités primo-liquidants de la ligne 15 du graphique 1 sont ceux de
    la colonne W (2024) du graphique 2, de 50 à 70 ans ; ceux de 2023 non (voir
    plus bas). La table C de l'EACR, rapportée à la population du 1er janvier 2025
    du dépôt (une projection), donne des taux plus hauts, de 0,45 point à 62 ans
    à 2,13 à 67 ans, l'écart croissant avec l'âge : la source compte les personnes
    résidant en France (champ de la feuille ; « Sources > Drees, modèle ANCETRE ;
    Insee, bilan démographique »), la table C tous les retraités, dont 5 % à
    l'étranger (folio 38). L'écart est déclaré, non expliqué."""
    for annee in ("2024", "2023"):
        for age in range(62, 68):
            g1 = _v(temoin, "16_graphique_1", f"stock_ensemble_{annee}", str(age))
            assert g1 == _v(temoin, "15_graphique_4", annee, str(age)), (annee, age)
            assert g1 == _bloc(temoin, "15_graphique_3")[age - 50][int(annee) - 2004], (annee, age)
    ecarts = {}
    for annee in ("2024", "2023"):
        for age in range(50, 71):
            g1 = _v(temoin, "16_graphique_1", f"primo_ensemble_{annee}", str(age))
            g2 = _v(temoin, "16_graphique_2", annee, str(age))
            if g1 != g2:
                ecarts[(annee, age)] = round(g1 - g2, 2)
    # 2024 : identiques. 2023 : la ligne « Ensemble (2023) » du graphique 1 et la
    # colonne 2023 du graphique 2 diffèrent à 19 âges sur 21, de 0,01 à 0,60 point
    # (30,53 contre 29,93 % à 62 ans) : deux millésimes du modèle ANCETRE, peut-être ;
    # la source ne le dit pas, et ne départage pas.
    assert [cle for cle in ecarts if cle[0] == "2024"] == []
    assert len(ecarts) == 19
    assert max(abs(e) for e in ecarts.values()) == pytest.approx(0.60)
    assert ecarts[("2023", 62)] == pytest.approx(0.60)
    pop = {int(l["age"]): float(l["effectif"]) for l in _lire(MACRO / "population_par_age.csv")
           if l["annee"] == "2025"}
    s = eacr["droits_directs_par_age"]["series"]["ddir"]["ensemble"]
    for age in range(62, 68):
        refait = 100 * s[str(age)][0] / pop[age]
        ecart = refait - _v(temoin, "16_graphique_1", "stock_ensemble_2024", str(age))
        assert ecart == pytest.approx(ECARTS_A_LA_TABLE_C[age], abs=0.01), age


def test_l_age_conjoncturel_de_la_fiche_15_est_50_plus_les_parts_de_non_retraites_du_graphique_3(temoin):
    """Fiche 15, graphique 1 (feuille « F15_Graphique 1 », lignes 5 à 7, de 2004 à
    2024) : l'âge conjoncturel moyen de départ, « l'âge moyen de départ d'une
    génération fictive qui aurait, à chaque âge fin entre 50 et 70 ans, la même
    probabilité d'être à la retraite que les générations ayant atteint ces âges au
    cours de l'année d'observation » (folio 139 à 144). C'est 50 plus la somme, de
    50 à 70 ans, de la part des non-retraités à chaque âge, lue aux feuilles
    « F15_Graphique 3 » (ensemble) et « F15_Graphique 3 compl » (femmes, lignes 7
    à 27, hommes, lignes 32 à 52) : 2024, ensemble, 50 + 20,951 ... = 62,951 pour
    62,95 publié ; 2004, 60,584 pour 60,58 ; 2014, 61,357 pour 61,36. Les 63 âges
    (21 années, deux sexes et l'ensemble) sont retrouvés au demi-centième près
    (l'arrondi de la publication), le plus éloigné à 0,0049."""
    publie = _bloc(temoin, "15_graphique_1")
    taux = {0: _bloc(temoin, "15_graphique_3_compl", "F"), 1: _bloc(temoin, "15_graphique_3_compl", "H"),
            2: _bloc(temoin, "15_graphique_3")}
    ecart_max = 0.0
    for ligne, parts in taux.items():
        for k in range(21):
            refait = 50 + sum(1 - parts[age - 50][k] / 100 for age in range(50, 71))
            ecart_max = max(ecart_max, abs(refait - publie[ligne][k]))
            assert refait == pytest.approx(publie[ligne][k], abs=0.00501), (ligne, 2004 + k)
    assert ecart_max == pytest.approx(0.0049, abs=0.0001)
    refait_2024 = 50 + sum(1 - _bloc(temoin, "15_graphique_3")[age - 50][20] / 100 for age in range(50, 71))
    assert refait_2024 == pytest.approx(62.951, abs=0.0005)


def test_le_bloc_ensemble_du_complement_du_graphique_3_differe_en_2023_et_le_depot_garde_le_millesime_du_portail(temoin):
    """Deux défauts de la source, déclarés. (1) Dans « F15_Graphique 3 compl », le
    bloc « Ensemble » (lignes 57 à 77) est celui de « F15_Graphique 3 » pour toutes
    les années sauf 2023, où seize âges sur vingt et un sont plus hauts de 0,01 à
    0,32 point (62 ans : 55,79 contre 55,60 %, que trois autres feuilles donnent :
    ``F15_Graphique 3``, ``F15_Graphique 4``, ``F16_Graphique 1``). L'âge de 2023
    qu'on en tire, 62,733, n'est pas le publié, 62,75 (62,754 avec « F15_Graphique
    3 ») : le bloc du complément est d'un autre calcul, à ne pas citer. (2) Le
    dépôt (``age_conjoncturel_depart.csv``) porte, de 2004 à 2022, l'âge du portail
    de données de la DREES, non celui du panorama : ils diffèrent d'au plus 0,10
    an, le panorama plus bas (femmes, 2013 : -0,10) ; en 2023 et 2024 le dépôt a
    celui du panorama."""
    g3 = _bloc(temoin, "15_graphique_3")
    compl = _bloc(temoin, "15_graphique_3_compl", "ensemble")
    differences = {(50 + i, 2004 + k): round(compl[i][k] - g3[i][k], 2)
                   for i in range(21) for k in range(21) if compl[i][k] != g3[i][k]}
    assert {annee for _, annee in differences} == {2023}
    assert len(differences) == 16
    assert min(differences.values()) == pytest.approx(0.01)
    assert max(differences.values()) == pytest.approx(0.32)
    assert differences[(62, 2023)] == pytest.approx(0.19)
    assert compl[12][19] == pytest.approx(55.79) and g3[12][19] == pytest.approx(55.6)
    publie_2023 = _bloc(temoin, "15_graphique_1")[2][19]
    depuis_compl = 50 + sum(1 - compl[i][19] / 100 for i in range(21))
    depuis_g3 = 50 + sum(1 - g3[i][19] / 100 for i in range(21))
    assert depuis_g3 == pytest.approx(publie_2023, abs=0.00501)
    assert depuis_compl == pytest.approx(62.733, abs=0.0005)
    assert abs(depuis_compl - publie_2023) > 0.015
    portail = {(int(l["annee"]), l["sexe"]): float(l["age"]) for l in _lire(MACRO / "age_conjoncturel_depart.csv")}
    lignes = {"F": 0, "H": 1, "ensemble": 2}
    ecarts = {}
    for (annee, sexe), age in portail.items():
        ecarts[(annee, sexe)] = _bloc(temoin, "15_graphique_1")[lignes[sexe]][annee - 2004] - age
    assert max(abs(e) for e in ecarts.values()) == pytest.approx(0.10, abs=0.0011)
    assert ecarts[(2013, "F")] == pytest.approx(-0.10, abs=0.0011)
    for sexe in lignes:
        for annee in (2023, 2024):
            if (annee, sexe) in ecarts:
                assert ecarts[(annee, sexe)] == pytest.approx(0, abs=1e-9), (annee, sexe)


# --- Fiche 17 : le taux de liquidation ----------------------------------------


#: Les lignes de la feuille « F17_ Graphique 3 compl » et leur libellé dans
#: ``retraites_generations.csv`` (champ ``taux_liquidation``).
MODALITES_DE_LA_FICHE_17 = {
    "decote": "decote", "taux_plein": "taux_plein", "decote_non_applicable": "decote_non_applicable",
    "taux_plein_age": "taux_plein_age", "ex_invalidite": "ex_invalidite", "inapte": "inaptitude",
    "taux_plein_autre_motif": "autre_motif", "taux_plein_duree": "taux_plein_duree", "surcote": "surcote",
}


def test_le_complement_du_graphique_3_de_la_fiche_17_encadre_l_ensemble_du_depot(temoin):
    """Fiche 17, feuille « F17_ Graphique 3 compl » : la répartition des retraités
    de douze générations (1928 à 1952) selon le taux de liquidation, femmes
    (lignes 6 à 15) et hommes (lignes 21 à 30). Le dépôt porte l'ensemble
    (``retraites_generations.csv``, graphique 3) : pour chaque génération et chaque
    modalité, l'ensemble est compris entre les parts des deux sexes, à 0,1 point
    près, comme l'est une moyenne pondérée ; et pour chaque sexe la décote, le
    taux plein et la surcote font 100, à 0,35 point près (la source arrondit : 99,8
    à 100,2 pour les hommes)."""
    ensemble = {(l["generation"], l["modalite"]): float(l["valeur"]) for l in _lire(MACRO / "retraites_generations.csv")
                if l["champ"] == "taux_liquidation" and l["regime"] == "tous_regimes" and l["sexe"] == "ensemble"}
    vus = 0
    for generation in temoin["valeurs"]["17_graphique_3_compl"]["F"]["decote"]:
        for libelle, modalite in MODALITES_DE_LA_FICHE_17.items():
            femmes = temoin["valeurs"]["17_graphique_3_compl"]["F"][libelle].get(generation)
            hommes = temoin["valeurs"]["17_graphique_3_compl"]["H"][libelle].get(generation)
            if femmes is None or hommes is None:
                continue
            f, h = femmes["valeur"], hommes["valeur"]
            e = ensemble[(generation, modalite)]
            assert min(f, h) - 0.1 <= e <= max(f, h) + 0.1, (generation, modalite, f, h, e)
            vus += 1
    assert vus >= 100
    for sexe in ("F", "H"):
        for generation, cellule in temoin["valeurs"]["17_graphique_3_compl"][sexe]["decote"].items():
            somme = sum(temoin["valeurs"]["17_graphique_3_compl"][sexe][m][generation]["valeur"]
                        for m in ("decote", "taux_plein", "surcote"))
            assert somme == pytest.approx(100, abs=0.35), (sexe, generation)


def test_le_graphique_2_de_la_fiche_17_recoupe_les_parts_par_regime_de_la_generation_1957_a_quelques_ecarts_pres(temoin):
    """Fiche 17, feuille « F17_Graphique 2 » (folio 156), la génération née en
    1957 : la décote, le taux plein et la surcote de cinq régimes, qui font 100.
    Le dépôt porte, pour la même génération, la décote et la surcote par régime
    (graphiques 4 et 5, ``retraites_generations.csv``). Ils concordent à 0,1 point
    pour le régime général (13,2 et 13,1 ; 16,2 et 16,1), la CNRACL (8,1 et 17,3) et
    la MSA non-salariés (6,6). Ils s'écartent pour les fonctionnaires civils de
    l'État (décote 16,6 contre 15,8 ; surcote 25,6 contre 28,2) et la MSA salariés
    (décote 5,9 contre 5,1). Le champ le dit autrement : le graphique 2, des
    retraités « ayant au moins un droit direct dans un régime de base » (le mot
    « secteur privé » du champ est contredit par les colonnes de la fonction
    publique), vivants fin 2024 ; les graphiques 4 et 5, des retraités « ayant un
    droit direct dans le régime, vivants au 31 décembre de l'année de leurs 67
    ans », soit 2024 pour 1957. Les deux lectures ne sont pas départagées par la
    source."""
    depot = {(l["regime"], l["champ"]): float(l["valeur"]) for l in _lire(MACRO / "retraites_generations.csv")
             if l["generation"] == "1957" and l["champ"] in ("decote", "surcote") and l["sexe"] == "ensemble"}
    regimes = {"regime_general": "regime_general", "fpe_civils": "fonction_publique_etat_civile",
               "cnracl": "cnracl", "msa_non_salaries": "msa_exploitants", "msa_salaries": "msa_salaries"}
    ecarts = {}
    for cle, regime in regimes.items():
        colonne = temoin["valeurs"]["17_graphique_2"][cle]
        assert (colonne["decote"]["valeur"] + colonne["taux_plein"]["valeur"] + colonne["surcote"]["valeur"]
                == pytest.approx(100, abs=0.15)), cle
        for champ in ("decote", "surcote"):
            if (regime, champ) in depot:
                ecarts[(cle, champ)] = round(colonne[champ]["valeur"] - depot[(regime, champ)], 1)
    assert ecarts == {
        ("regime_general", "decote"): 0.1, ("regime_general", "surcote"): 0.1,
        ("fpe_civils", "decote"): 0.8, ("fpe_civils", "surcote"): -2.6,
        ("cnracl", "decote"): 0.0, ("cnracl", "surcote"): 0.0,
        ("msa_non_salaries", "decote"): 0.0, ("msa_salaries", "decote"): 0.8,
    }


def test_les_taux_de_nouveaux_retraites_avant_62_ans_par_type_de_regime_de_la_fiche_16_se_somment_et_ceux_de_50_a_56_ans_des_femmes_sont_ceux_du_graphique_1(temoin):
    """Fiche 16, graphique 4 (feuille « F16_Graphique 4 », C6:N10, au 31 décembre
    2024) : le taux de nouveaux retraités par âge jusqu'à 62 ans selon le type de
    régime, en quatre lignes et un total, pour les femmes, les hommes et
    l'ensemble ; pour 50-56 ans et 57-59 ans, la somme des taux de chaque âge. Les
    quatre lignes font le total, au centième près de la source (0,02). Les femmes de
    50 à 56 ans font 0,48 % au total, comme la somme de leurs taux du graphique 1
    (0,03 + 0,03 + 0,08 + 0,03 + 0,07 + 0,07 + 0,17). À 60 et 61 ans le total du
    graphique 4 s'écarte de la ligne du graphique 1 (femmes 60 ans : 2,22 contre
    2,43) de 0,02 à 0,27 point : le champ du graphique 4 (« seules les personnes
    bénéficiant d'une pension de droit direct sous forme de rente ») n'est pas
    énoncé au graphique 1. L'écart est déclaré, non expliqué."""
    g4 = _bloc(temoin, "16_graphique_4")
    for colonne in range(12):
        assert sum(g4[ligne][colonne] for ligne in range(4)) == pytest.approx(g4[4][colonne], abs=0.0201), colonne
    femmes = sum(_v(temoin, "16_graphique_1", "primo_femmes_2024", str(age)) for age in range(50, 57))
    assert femmes == pytest.approx(g4[4][0], abs=0.011)
    assert femmes == pytest.approx(0.48, abs=0.0001)
    ecarts = {}
    for nom, colonne, ligne in (("F", 2, "primo_femmes_2024"), ("H", 6, "primo_hommes_2024"),
                                ("ensemble", 10, "primo_ensemble_2024")):
        for decalage, age in ((0, 60), (1, 61)):
            ecarts[(nom, age)] = round(g4[4][colonne + decalage] - _v(temoin, "16_graphique_1", ligne, str(age)), 2)
    assert ecarts == {("F", 60): -0.21, ("F", 61): -0.02, ("H", 60): -0.27, ("H", 61): 0.26,
                      ("ensemble", 60): -0.23, ("ensemble", 61): 0.11}


def test_le_graphique_5_complementaire_de_la_fiche_16_retrouve_le_tableau_1_de_la_generation_1953_a_un_point_pres(temoin):
    """Fiche 16, feuille « F16_Graphique 5 compl » (colonne O pour les femmes, AD
    pour les hommes, la génération 1953) : la part des retraités par âge à la
    première liquidation, en %, en neuf classes qui font 100. Le dépôt porte la
    même génération (``retraites_generations.csv``, ``age_premiere_liquidation``,
    tableau 1, en dix classes). À l'entier près de la source, un point, les deux
    concordent ; six classes s'écartent d'un point : femmes, 60 ans (12 contre 11) et
    61 ans (45 contre 44), 66 ans ou plus (13 contre 13 + 1) ; hommes, 60 ans (21
    contre 20), 63 à 65 ans (8 + 4 contre 13), 66 ans ou plus (8 contre 8 + 1) :
    deux millésimes du calcul, ou l'arrondi, que la source ne départage pas."""
    depot = {(l["modalite"], l["sexe"]): float(l["valeur"]) for l in _lire(MACRO / "retraites_generations.csv")
             if l["generation"] == "1953" and l["champ"] == "age_premiere_liquidation"
             and l["indicateur"] == "part_pct"}
    classes = ["moins_55", "55", "56_59", "60", "61", "62", "63_64", "65", "66_plus"]
    ecarts = {}
    for sexe, cle in (("F", "femmes"), ("H", "hommes")):
        colonne = {c: _bloc(temoin, "16_graphique_5_compl", cle)[i][12] for i, c in enumerate(classes)}
        assert sum(colonne.values()) == pytest.approx(100, abs=1.001), sexe
        regroupe = {"moins_55": colonne["moins_55"], "55": colonne["55"], "56_59": colonne["56_59"],
                    "60": colonne["60"], "61": colonne["61"], "62": colonne["62"],
                    "63_65": colonne["63_64"] + colonne["65"], "66_plus": colonne["66_plus"]}
        attendu = {c: depot[(c, sexe)] for c in ("moins_55", "55", "56_59", "60", "61", "62", "63_65")}
        attendu["66_plus"] = depot[("66", sexe)] + depot[("67_plus", sexe)]
        for classe, valeur in regroupe.items():
            assert abs(valeur - attendu[classe]) <= 1.0 + 1e-9, (sexe, classe)
            if valeur != attendu[classe]:
                ecarts[(sexe, classe)] = valeur - attendu[classe]
    assert ecarts == {("F", "60"): 1.0, ("F", "61"): 1.0, ("F", "66_plus"): -1.0,
                      ("H", "60"): 1.0, ("H", "63_65"): -1.0, ("H", "66_plus"): -1.0}


def test_les_trimestres_de_decote_et_de_surcote_de_la_fiche_17_sont_compatibles_avec_leur_ventilation(temoin):
    """Fiche 17, feuilles « F17_Tableau compl - Decote » et « - Surcote » (lignes 6
    à 15, dix caisses) : la part des nouveaux retraités de 2024 partis avec une
    décote ou une surcote (colonne C, recoupée à la table H pour quatre caisses à
    l'étape 2), le nombre moyen de trimestres (D) et sa ventilation en classes (E
    et suivantes, en %). Les classes font 100, à un point près de l'arrondi. La
    décote : un départ à 1 à 9 trimestres, 10 à 18, 19 ou plus (et 20 au plus) ; la
    moyenne est comprise entre les bornes que la ventilation permet, (E×1 + F×10 + G×19) /
    100 et (E×9 + F×18 + G×20) / 100 : régime général, 10,3 entre 6,04 et 13,48. La
    surcote : 1, 2 à 4, 5 à 9 trimestres, 10 ou plus ; la moyenne dépasse la borne
    basse (E×1 + F×2 + G×5 + H×10) / 100, et la moyenne de la dernière classe qu'elle
    implique est d'au moins 10 : régime général, 7,7 contre 5,15 au moins, et 12,7
    trimestres dans la classe de dix ou plus. Le dépôt n'en tire aucun calcul."""
    decote = _bloc(temoin, "17_tableau_decote")
    surcote = _bloc(temoin, "17_tableau_surcote")
    assert len(decote) == len(surcote) == 10
    for caisse, (part, moyenne, e, f, g) in enumerate(decote):
        assert e + f + g == pytest.approx(100, abs=1.001), caisse
        bas, haut = (e * 1 + f * 10 + g * 19) / 100, (e * 9 + f * 18 + g * 20) / 100
        assert bas <= moyenne <= haut, (caisse, bas, moyenne, haut)
    for caisse, (part, moyenne, e, f, g, h) in enumerate(surcote):
        assert e + f + g + h == pytest.approx(100, abs=1.001), caisse
        bas = (e * 1 + f * 2 + g * 5 + h * 10) / 100
        assert moyenne >= bas, (caisse, bas, moyenne)
        assert (moyenne - (e * 1 + f * 4 + g * 9) / 100) / (h / 100) >= 10, caisse
    rg_decote, rg_surcote = decote[0], surcote[0]
    assert (rg_decote[2] * 1 + rg_decote[3] * 10 + rg_decote[4] * 19) / 100 == pytest.approx(6.04)
    assert (rg_decote[2] * 9 + rg_decote[3] * 18 + rg_decote[4] * 20) / 100 == pytest.approx(13.48)
    assert (rg_surcote[1] - (rg_surcote[2] + rg_surcote[3] * 4 + rg_surcote[4] * 9) / 100) / (rg_surcote[5] / 100) == pytest.approx(12.7, abs=0.05)


def test_les_feuilles_de_travail_de_la_fiche_12_sont_l_edition_precedente_et_le_depot_a_celle_de_2026(temoin):
    """Fiche 12, feuilles « Graphique 1 (2) » à « Graphique 5 (2) » et « Synthese » :
    les copies de travail de la DREES. « Synthese » (A9) définit le champ de l'EIC
    au 31/12/2017 ; elle dit, pour chacune des cinq figures, la version retenue :
    l'alternative pour les figures 1, 3 et 4 (B7, D7, E7), « A DECIDER » pour les
    figures 2 et 5 (C7, F7), sans que le classeur dise la décision. « Graphique 1
    (2) » est le graphique 1 de l'édition précédente (« avant ou en 2017 ») : la
    génération 1946 y compte 37,6 trimestres validés à 30 ans pour les femmes, 44,1
    pour les hommes et 41,0 pour l'ensemble, contre 37,4, 44,0 et 40,7 dans la
    feuille publiée (« F12_Graphique 1 », ligne 8, « avant ou en 2021 »). Le dépôt
    (``durees_validees_actifs.csv``) porte la seconde ; les feuilles (2) ne sont
    pas tirées."""
    publie = _bloc(temoin, "12_graphique_1", "publie_1946")[0]
    avant = _bloc(temoin, "12_graphique_1", "edition_precedente_1946")[0]
    depot = {l["sexe"]: float(l["valeur"]) for l in _lire(MACRO / "durees_validees_actifs.csv")
             if l["generation"] == "1946" and l["champ"] == "cumul" and l["groupe"] == "30"
             and l["modalite"] == "toutes" and l["indicateur"] == "trimestres"}
    assert [depot["F"], depot["H"], depot["ensemble"]] == publie == [37.4, 44.0, 40.7]
    assert avant == [37.6, 44.1, 41.0]
    synthese = temoin["valeurs"]["12_graphique_1"]["synthese"]
    assert "31/12/2017" in synthese["champ_eic"]["valeur"]
    for figure in ("figure_1", "figure_3", "figure_4"):
        assert synthese[figure]["valeur"].startswith("VERSION ALTERNATIVE"), figure
    assert synthese["figure_2"]["valeur"].startswith("A DECIDER")
    assert synthese["figure_5"]["valeur"] == "A DECIDER"


def test_les_revisions_du_graphique_1_de_la_fiche_21_sont_la_difference_des_deux_editions(temoin):
    """Fiche 21, feuille « F21_Graphique 1 REVISIONS » : « DONNEES PANORAMA 2025 »
    (colonnes D à K), « REVISIONS ENTRE PANORAMA 2026 ET 2025 » (N à U), pour six
    générations et huit situations à 59 ans, femmes (lignes 8 à 13), hommes (18 à 23)
    et ensemble (28 à 33). La valeur de 2025 plus la révision est, pour les 144
    cellules, celle de la feuille publiée « F21_Graphique 1 » (C à J), à la poussière
    de calcul près (3e-17) : 1946, absence, 15,47 - 0,34 = 15,13. La révision
    la plus forte est de 1,34 point, les « 1,3 point d'écart, surtout pour hommes »
    de la feuille « Synthese » (B2) : les chiffres de l'édition 2025 ne se mêlent pas
    à ceux de 2026, que le dépôt (``fins_de_carriere.csv``) porte seuls."""
    plus_forte = 0.0
    cellules = 0
    for sexe, blocs in temoin["valeurs"]["21_graphique_1_revisions"].items():
        for ligne in range(6):
            for colonne in range(8):
                avant = blocs["edition_2025"]["valeurs"][ligne][colonne]
                revision = blocs["revisions"]["valeurs"][ligne][colonne]
                assert avant + revision == pytest.approx(blocs["edition_2026"]["valeurs"][ligne][colonne],
                                                         abs=1e-9), (sexe, ligne, colonne)
                plus_forte = max(plus_forte, abs(revision))
                cellules += 1
    assert cellules == 144
    assert plus_forte == pytest.approx(1.34, abs=0.005)
    assert temoin["valeurs"]["21_synthese"]["graphique_1"]["valeur"].startswith("Jusqu a 1,3 point")
    assert temoin["valeurs"]["21_graphique_1_revisions"]["femmes"]["edition_2025"]["valeurs"][1][0] == pytest.approx(15.47)
    assert temoin["valeurs"]["21_graphique_1_revisions"]["femmes"]["revisions"]["valeurs"][1][0] == pytest.approx(-0.34)


def test_l_encadre_2_de_la_fiche_21_se_somme_et_se_decompose(temoin):
    """Fiche 21, encadré 2 (feuilles « F21_Graphique encadré 2 » et « F21_Tableau
    encadré 2 »), les personnes ni en emploi ni à la retraite (NERP) de 53 à 69 ans,
    de l'enquête Emploi : la part de chacun des 17 âges de 53 à 69 ans, de 2005 à
    2024 (C4:V20), dont la ligne « Somme » (21) est le total, à deux centièmes près
    ; et le revenu disponible de leur ménage (C5:C16) : revenus individuels 27,97 +
    revenus du conjoint 46,51 + autres revenus initiaux 24,23 + prestations sociales
    14,69 - impôts directs 13,4 = 100 ; les revenus individuels, 27,97, sont les 9,11
    d'activité, 7,56 d'allocations chômage ou de préretraite et 11,29 de pensions, à
    un centième près, et les prestations, 14,69, les 3,78 + 5,97 + 4,94. Aucun fichier de
    ``data/reference/`` ne lit les NERP : l'encadré est lu, non porté."""
    parts = _bloc(temoin, "21_encadre_2", "parts_par_age")
    assert len(parts) == 18 and len(parts[0]) == 20
    for annee in range(20):
        assert sum(parts[age][annee] for age in range(17)) == pytest.approx(parts[17][annee], abs=0.0201), annee
    revenu = [ligne[0] for ligne in _bloc(temoin, "21_encadre_2", "revenu")]
    assert revenu[0] + revenu[4] + revenu[5] + revenu[6] + revenu[10] == pytest.approx(100, abs=1e-9)
    assert revenu[0] == pytest.approx(revenu[1] + revenu[2] + revenu[3], abs=0.011)
    assert revenu[6] == pytest.approx(revenu[7] + revenu[8] + revenu[9], abs=1e-9)
    assert revenu[11] == 100


# --- Fiche 23 : le cumul emploi-retraite --------------------------------------


def test_le_cumul_par_sexe_encadre_le_regime_general_de_la_fiche_23(temoin):
    """Fiche 23, feuille « F23_Graphique 1 compl. » (femmes en C, hommes en F, de 61
    à 80 ans, en 2022) : la part des retraités de droit direct en cumul
    emploi-retraite au sein du régime général. La colonne C de « F23_Graphique 1 »
    (CNAV, 2022, « dernière année connue » selon la note, folio 204) est comprise
    entre les deux sexes à 0,05 point près, à chaque âge. Les deux feuilles ne
    datent pas l'intégration de la SSI de la même année : 2020 (note de « F23_Graphique
    1 », folio 204) et 2021 (note du complément), et la seconde restreint le régime
    général aux salariés : à citer avec précaution."""
    for age in range(61, 81):
        f = _v(temoin, "23_graphique_1_compl", "femmes", str(age))
        h = _v(temoin, "23_graphique_1_compl", "hommes", str(age))
        e = _v(temoin, "23_graphique_1", "regime_general", str(age))
        assert min(f, h) - 0.05 <= e <= max(f, h) + 0.05, (age, f, h, e)
    assert "ex-SSI depuis 2020" in temoin["citations"]["23_graphique_1"]["textes"][0]


# --- Le suivi ---------------------------------------------------------------


FICHES_DU_SOLDE = ["01", "03", "10", "12", "15", "16", "17", "21", "22", "23", "25", "27", "28"]


def test_les_fiches_du_solde_disent_leur_solde_au_suivi_et_nomment_leurs_recoupements():
    """Au suivi, chaque fiche que l'étape 7 solde dit ce qu'elle a lu le 6
    novembre 2026 et ce que le dépôt en tire (``solde``), et nomme les tests de
    ce module qui la recoupent (``recoupe_par``) ; chacun existe."""
    suivi = yaml.safe_load(SUIVI.read_text(encoding="utf-8"))["fiches"]
    module = sys.modules[__name__]
    assert sorted(n for n, ligne in suivi.items() if "solde" in ligne) == FICHES_DU_SOLDE
    for numero in FICHES_DU_SOLDE:
        ligne = suivi[numero]
        assert len(" ".join(str(ligne["solde"]).split())) > 80, numero
        for nom in ligne.get("recoupe_par", []):
            assert nom.startswith("test_") and callable(getattr(module, nom, None)), (numero, nom)
    recoupees = {n for n in FICHES_DU_SOLDE if suivi[n].get("recoupe_par")}
    assert recoupees == {"01", "03", "10", "12", "15", "16", "17", "21", "23", "28"}
