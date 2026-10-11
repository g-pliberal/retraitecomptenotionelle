"""La persistance au voisinage du Smic : lue dans le PDF, certifiée dans un CSV.

`persistance_smic.csv` est écrit par `scripts/verifier_donnees.py` depuis les
tableaux que `scripts/fetch/dgtresor_trajectoires_smic.py` lit dans le
document de travail de la DG Trésor n° 2018/3. Le document, que sa licence ne
permet pas de republier, n'est pas dans le dépôt : le lecteur se teste sur des
lignes rendues comme celles du PDF, et ses contrôles sur le fichier certifié,
qui doit les passer tous.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
CSV = RACINE / "data" / "reference" / "macro" / "persistance_smic.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import dgtresor_trajectoires_smic as recuperateur  # noqa: E402

#: La composition par sexe de la cohorte de 2007, au tableau 1 du document.
COMPOSITION = {"H": 38.1, "F": 61.9}


def _serie() -> dict[str, float]:
    with CSV.open(encoding="utf-8") as flux:
        lignes = csv.DictReader(ligne for ligne in flux if not ligne.startswith("#"))
        return {"|".join((ligne["origine"], ligne["sexe"], ligne["age"], ligne["annee"],
                          ligne["etat"])): float(ligne["part"]) for ligne in lignes}


def test_les_nombres_que_le_lecteur_coupe_se_recollent():
    """« 4 6,5 » est 46,5 : le lecteur du dépôt glisse des espaces dans les
    nombres du document, jamais entre deux valeurs sans virgule."""
    assert recuperateur.valeurs("22,8 30,7 4 6,5 13,9 20,7 8,0 4,0") == [
        22.8, 30.7, 46.5, 13.9, 20.7, 8.0, 4.0]
    assert recuperateur.valeurs("18 - 24 ans 21,4 22,6") == [21.4, 22.6]


def test_le_tableau_par_sexe_se_lit_comme_le_pdf_le_rend():
    pages = [[
        "Tableau 1 : Caracté ristiques des salariés au voisinage du Smic",
        "Hommes 38,1 37,2 37,1 37,3 37 37,2 36,9",
        "Femmes 61,9 62,8 62,9 62,7 63 62,8 63,1",
        "Source : Insee Panel DADS 2007 à 2013.",
    ], [
        "T ableau B : Répartition des individus selon leur rémunération en 2007",
        "Individus au voisinage du Smic en 2007",
        "Hommes",
        "2 012 39,6 11,1 49,3 6,8 20,3 13,7 8,5",
        "Femmes",
        "2012 37,5 19,0 4 3,5 9,2 19,7 9,6 5,0",
        "Source : Insee panel DADS 2007 - 2013 .",
    ]]
    serie, composition = recuperateur.lire(pages)
    assert composition == COMPOSITION
    assert serie["voisinage|H|ensemble|2012|voisinage"] == 11.1
    assert serie["voisinage|F|ensemble|2012|superieur"] == 43.5
    assert len(serie) == 2 * len(recuperateur.ETATS)


def test_une_ligne_mal_lue_arrete_tout():
    pages = [["Tableau B : Répartition", "Hommes", "2012 39,6 11,1 49,3 6,8 20,3"]]
    with pytest.raises(ValueError, match="5 valeurs"):
        recuperateur.lire(pages)


def test_le_fichier_certifie_tient_les_comptes_du_document():
    """Trois tableaux, six années, sept états : 336 valeurs, dont chaque ligne
    fait 100 et redonne son total au-dessus du Smic, et dont les sexes,
    pondérés par la cohorte, redonnent l'ensemble."""
    serie = _serie()
    assert len(serie) == 336
    assert recuperateur.controler(serie, COMPOSITION) == []


def test_des_sexes_intervertis_ne_passeraient_pas():
    serie = _serie()
    inversee = {
        cle.replace("|H|", "|X|").replace("|F|", "|H|").replace("|X|", "|F|"): valeur
        for cle, valeur in serie.items()
    }
    assert any("par sexe" in e for e in recuperateur.controler(inversee, COMPOSITION))


def test_les_femmes_restent_plus_souvent_au_smic_que_les_hommes():
    """Ce que le document dit dans son texte, et que ses tableaux portent :
    six ans après, 78 % des femmes restées dans le champ sont au-dessus du
    Smic, 87 % des hommes."""
    serie = _serie()
    for annee in range(2008, 2014):
        femmes = serie[f"voisinage|F|ensemble|{annee}|voisinage"]
        hommes = serie[f"voisinage|H|ensemble|{annee}|voisinage"]
        assert femmes > hommes, annee
    for sexe, au_dessus in (("F", 0.78), ("H", 0.87)):
        reste = serie[f"voisinage|{sexe}|ensemble|2013|voisinage"]
        monte = serie[f"voisinage|{sexe}|ensemble|2013|superieur"]
        assert round(monte / (monte + reste), 2) == au_dessus, sexe
