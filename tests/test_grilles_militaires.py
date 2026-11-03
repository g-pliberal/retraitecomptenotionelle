"""Les grilles des militaires, leurs indices de solde, lues au LEGI (action 158, étape des militaires).

Le propriétaire l'a décidé le 2 novembre 2026 : les grilles des militaires, qui
ont leur barème, les indices de solde, entrent au périmètre. Leurs textes sont
dans l'index LEGI du dépôt — les décrets n° 2009-17 à 2009-23 du 7 janvier 2009,
le n° 2011-388 pour la gendarmerie, le n° 2011-1235 pour l'armement, des
arrêtés d'avant 2009 —, et ``scripts/fetch/dila_legi_grilles.py`` les relit
comme ceux de la territoriale et de l'hospitalière, avec ce que leurs tableaux
écrivent en plus : l'échelle de solde sous son grade, l'échelon unique,
particulier ou provisoire, les échelons exceptionnels numérotés. Ces règles ne
lisent que les textes des militaires. Les textes des essais sont ceux de
l'index, recopiés tels quels ou abrégés de quelques lignes ; chaque attendu se
lit dans le texte de l'essai. Puis la donnée, sous
``data/reference/grilles/militaires/``, confrontée au Noyau RH de l'État, que
le CISIRH publie, et qui ne la recopie pas.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _charger(nom: str, chemin: Path | None = None):
    chemin = chemin or RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


grilles = _charger("dila_legi_grilles")


def _valeurs(tableau, groupe: str, colonne: str = "") -> dict[str, int | str | None]:
    """L'échelon et sa valeur, pour un groupe et une colonne du tableau lu."""
    return {c.echelon: (c.hors_echelle or c.indice) for c in tableau.cellules
            if c.groupe == groupe and c.date == colonne}


def _rangs(tableau, groupe: str) -> dict[str, int]:
    return {c.echelon: c.rang for c in tableau.cellules if c.groupe == groupe}


# ---------------------------------------------------------------------------
# La lecture des tableaux des militaires
# ---------------------------------------------------------------------------

#: Décret n° 2009-21, article 2, version du 1er janvier 2009
#: (LEGIARTI000020091040), abrégé des adjudants-chefs et des sergents : chaque
#: grade nomme sa première échelle de solde ; la suivante, écrite seule, est
#: encore la sienne.
SOUS_OFFICIERS_2009 = (
    "L'échelonnement indiciaire applicable aux sous-officiers, officiers mariniers et corps "
    "assimilés, régis par les décrets n°s 2008-930, 2008-931, 2008-953, 2008-954 et 2008-961 "
    "du 12 septembre 2008 susvisés, est fixé comme suit : GRADE ÉCHELLE DE SOLDE ÉCHELON "
    "INDICE BRUT Major. Echelle de solde des majors Echelon exceptionnel (1) 634 5e échelon "
    "600 4e échelon 585 3e échelon 573 2e échelon 562 1er échelon 542 Adjudant ou premier "
    "maître. Echelle de solde n° 4 8e échelon 527 7e échelon 513 6e échelon 510 5e échelon "
    "491 4e échelon 486 3e échelon 468 2e échelon 448 1er échelon 441 Echelle de solde n° 3 "
    "3e échelon 387 2e échelon 374 1er échelon 365 Sergent-chef ou maître. Echelle de solde "
    "n° 4 6e échelon 505 5e échelon 486 4e échelon 463 3e échelon 440 2e échelon 420 1er "
    "échelon 392 Echelle de solde n° 3 6e échelon 374 5e échelon 365 4e échelon 359 3e "
    "échelon 353 2e échelon 346 1er échelon 333 (1) Echelon exceptionnel attribué dans la "
    "limite de 18 % de l'effectif des majors pour l'année 2009.")


def test_l_echelle_de_solde_est_celle_du_grade_ecrit_avant_elle():
    tableau = grilles.lire_tableau(SOUS_OFFICIERS_2009, militaire=True)
    assert tableau.refus == ""
    assert tableau.groupes == [
        "Major – Echelle de solde des majors",
        "Adjudant ou premier maître – Echelle de solde n° 4",
        "Adjudant ou premier maître – Echelle de solde n° 3",
        "Sergent-chef ou maître – Echelle de solde n° 4",
        "Sergent-chef ou maître – Echelle de solde n° 3"]
    assert _valeurs(tableau, "Major – Echelle de solde des majors") == {
        "exceptionnel": 634, "5": 600, "4": 585, "3": 573, "2": 562, "1": 542}
    assert _rangs(tableau, "Major – Echelle de solde des majors")["exceptionnel"] == 6
    assert _valeurs(tableau, "Adjudant ou premier maître – Echelle de solde n° 3") == {
        "3": 387, "2": 374, "1": 365}
    assert _valeurs(tableau, "Sergent-chef ou maître – Echelle de solde n° 3") == {
        "6": 374, "5": 365, "4": 359, "3": 353, "2": 346, "1": 333}


#: Décret n° 2009-20, article 1er, version du 1er janvier 2009
#: (LEGIARTI000020129975), tel quel : l'échelon unique, en lettre de
#: hors-échelle ou en indice ; deux échelons exceptionnels numérotés ; l'échelon
#: provisoire, sous le premier.
OFFICIERS_2009 = (
    "L'échelonnement indiciaire applicable aux militaires régis par les décrets du 5 novembre "
    "1976, du 4 janvier 1977 et du 12 septembre 2008 susvisés est fixé comme suit : GRADE "
    "ÉCHELON INDICE BRUT Général de division ou vice-amiral. Echelon unique HE D Général de "
    "brigade ou contre-amiral. Echelon unique HE C Colonel ou capitaine de vaisseau. Echelon "
    "exceptionnel (1) HE B 3e échelon HE A 2e échelon 1015 1er échelon 966 Lieutenant-colonel "
    "ou capitaine de frégate. 2e échelon exceptionnel (1) 1015 1er échelon exceptionnel (1) "
    "1015 4e échelon 966 3e échelon 884 2e échelon 844 1er échelon 797 Commandant ou capitaine "
    "de corvette. 2e échelon exceptionnel (1) 904 1er échelon exceptionnel (1) 878 4e échelon "
    "751 3e échelon 743 2e échelon 710 1er échelon 700 Capitaine ou lieutenant de vaisseau. "
    "Echelon exceptionnel (1) 746 5e échelon 699 4e échelon 665 3e échelon 630 2e échelon 597 "
    "1er échelon 574 Lieutenant ou enseigne de vaisseau de 1re classe. 4e échelon 573 3e "
    "échelon 539 2e échelon 509 1er échelon 457 Echelon provisoire (2) 389 Sous-lieutenant ou "
    "enseigne de vaisseau de 2e classe. Echelon unique 389 (1) Echelon exceptionnel attribué "
    "dans les conditions prévues par le statut particulier du corps. (2) Echelon provisoire "
    "attribué dans les conditions prévues par le décret n° 2008-931 susvisé.")


def test_l_echelon_unique_les_echelons_exceptionnels_numerotes_et_le_provisoire():
    tableau = grilles.lire_tableau(OFFICIERS_2009, militaire=True)
    assert tableau.refus == ""
    assert tableau.groupes[0] == "Général de division ou vice-amiral"
    assert _valeurs(tableau, "Général de division ou vice-amiral") == {"unique": "D"}
    assert _valeurs(tableau, "Colonel ou capitaine de vaisseau") == {
        "exceptionnel": "B", "3": "A", "2": 1015, "1": 966}
    colonel = "Lieutenant-colonel ou capitaine de frégate"
    assert _valeurs(tableau, colonel) == {
        "exceptionnel-2": 1015, "exceptionnel-1": 1015, "4": 966, "3": 884, "2": 844, "1": 797}
    assert _rangs(tableau, colonel) == {
        "exceptionnel-2": 6, "exceptionnel-1": 5, "4": 4, "3": 3, "2": 2, "1": 1}
    lieutenant = "Lieutenant ou enseigne de vaisseau de 1re classe"
    assert _valeurs(tableau, lieutenant) == {"4": 573, "3": 539, "2": 509, "1": 457,
                                             "provisoire": 389}
    assert _rangs(tableau, lieutenant)["provisoire"] == 0
    assert _valeurs(tableau, "Sous-lieutenant ou enseigne de vaisseau de 2e classe") == {
        "unique": 389}
    assert _rangs(tableau, "Sous-lieutenant ou enseigne de vaisseau de 2e classe") == {
        "unique": 1}


#: Décret n° 2011-388, article 2, version du 1er août 2023
#: (LEGIARTI000047909272), abrégé des adjudants-chefs, des maréchaux des
#: logis-chefs et des gendarmes : l'échelon exceptionnel du major, supprimé au
#: 1er janvier 2024 (« -(2) »), et l'échelon particulier de l'élève gendarme.
GENDARMERIE_2023 = (
    "Conformément à l’article 3 du décret n° 2023-678 du 28 juillet 2023, ces dispositions "
    "entrent en vigueur le premier jour du mois suivant celui de sa publication, soit le 1 er "
    "août 2023. L'échelonnement indiciaire applicable aux militaires du corps des "
    "sous-officiers de gendarmerie, régis par le décret n° 2008-952 du 12 septembre 2008 "
    "susvisé , est fixé comme suit : GRADE ECHELON A COMPTER du 1er août 2023 A COMPTER du "
    "1er janvier 2024 Indice brut Indice brut Major Exceptionnel (1) 712 -(2) 6e échelon 691 "
    "739 5e échelon 678 691 4e échelon 659 675 3e échelon 641 652 2e échelon 614 633 1er "
    "échelon 587 607 Adjudant 7e échelon 629 629 6e échelon 601 601 5e échelon 578 578 4e "
    "échelon 554 554 3e échelon 529 529 2e échelon 504 504 1er échelon 484 484 Elève "
    "gendarme Echelon particulier 367 367 (1) Echelon exceptionnel attribué dans la limite "
    "de 25 % de l'effectif des majors. (2) Echelon supprimé à compter du 1er janvier 2024.")


def test_la_case_vide_que_suit_son_renvoi_et_l_echelon_particulier():
    tableau = grilles.lire_tableau(GENDARMERIE_2023, militaire=True)
    assert tableau.refus == ""
    assert tableau.groupes == ["Major", "Adjudant", "Elève gendarme"]
    assert tableau.dates == ["2023-08-01", "2024-01-01"]
    assert _valeurs(tableau, "Major", "2023-08-01") == {
        "exceptionnel": 712, "6": 691, "5": 678, "4": 659, "3": 641, "2": 614, "1": 587}
    assert _valeurs(tableau, "Major", "2024-01-01") == {
        "6": 739, "5": 691, "4": 675, "3": 652, "2": 633, "1": 607}
    assert _valeurs(tableau, "Elève gendarme", "2024-01-01") == {"particulier": 367}


#: Décret n° 2011-388, article 2-1, version du 1er août 2023
#: (LEGIARTI000047905548), tel quel : le groupe n'est nommé que par la phrase,
#: « afférent » et non « applicable ».
CLASSE_FONCTIONNELLE_MAJOR = (
    "Conformément à l’article 3 du décret n° 2023-678 du 28 juillet 2023, ces dispositions "
    "entrent en vigueur le premier jour du mois suivant celui de sa publication, soit le 1 er "
    "août 2023. L'échelonnement indiciaire afférent à la classe fonctionnelle du grade de "
    "major définie à l'article 9-1 du décret du 12 septembre 2008 susvisé est fixé comme suit "
    ": Echelon A COMPTER DU 1er JANVIER 2024 Indice brut 4e échelon 837 3e échelon 797 2e "
    "échelon 772 1er échelon 744")


def test_le_groupe_afferent_que_la_phrase_introduit():
    tableau = grilles.lire_tableau(CLASSE_FONCTIONNELLE_MAJOR, militaire=True)
    assert tableau.groupes == ["classe fonctionnelle du grade de major"]
    assert _valeurs(tableau, "classe fonctionnelle du grade de major", "2024-01-01") == {
        "4": 837, "3": 797, "2": 772, "1": 744}


#: Arrêté du 26 décembre 2007 fixant les indices de solde applicables aux
#: majors, article 1er (LEGIARTI000019430204), abrégé : l'échelon se gagne aux
#: années de services, deux colonnes de durées pour une d'indices.
MAJORS_2007 = (
    "Les indices afférents aux divers échelons des majors sont fixés comme suit : DURÉE DES "
    "SERVICES OUVRANT DROIT AUX ÉCHELONS Personnel navigant de l'armée de l'air Autres "
    "personnels INDICES BRUTS attribués à compter du 1er janvier 2007 Echelon exceptionnel (1) "
    "Echelon exceptionnel (1) 634 Après 26 ans Après 31 ans 595 Après 24 ans Après 29 ans 585 "
    "Après 22 ans Après 26 ans 573 Avant 14 ans Avant 15 ans 485")


def test_les_echelons_comptes_en_annees_de_services_sont_refuses():
    assert grilles.lire_tableau(MAJORS_2007, militaire=True).refus == (
        "échelons comptés en années de services, non lus")


#: Décret n° 91-840, article 1er, version du 1er avril 2008 (LEGIARTI000018520062),
#: tel quel : un texte de la territoriale, que sa certification a vu refusé.
CONSERVATEURS_TERRITORIAUX_2008 = (
    "L'échelonnement indiciaire applicable au cadre d'emplois des conservateurs territoriaux "
    "du patrimoine est fixé ainsi qu'il suit : GRADES ET ÉCHELONS INDICES BRUTS Conservateur "
    "en chef : 6e echelon HEA 5e echelon 1015 4e echelon 966 3e echelon 871 2e echelon 780 1er "
    "echelon 701 Conservateur : 7e échelon 852 6e échelon 777 5e échelon 701 4e échelon 648 3e "
    "échelon 593 2e échelon 540 1er échelon 499 Echelons de stage : Echelon unique 459 Echelon "
    "d'élèves : 2e echelon 459 1er echelon 416")


def test_les_regles_des_militaires_ne_lisent_que_leurs_textes():
    """« Echelon unique » ouvrirait à la territoriale des tableaux que sa
    certification n'a pas vus : hors des textes des militaires, il reste un mot."""
    assert grilles.lire_tableau(CONSERVATEURS_TERRITORIAUX_2008).refus.startswith(
        "valeurs hors des lignes")
    assert grilles.lire_tableau(SOUS_OFFICIERS_2009).refus.startswith("échelon")


@pytest.mark.parametrize("titre, versant", [
    ("Décret n° 2009-21 du 7 janvier 2009 fixant les indices de solde applicables à certains "
     "militaires non officiers", "militaires"),
    ("Décret n° 2011-388 du 13 avril 2011 fixant les indices de solde applicables aux corps "
     "militaires de la gendarmerie nationale", "militaires"),
    ("Arrêté du 14 juin 2004 fixant l'échelonnement indiciaire applicable aux praticiens des "
     "armées", "militaires"),
    ("Arrêté du 27 juillet 1994 fixant l'échelonnement indiciaire applicable aux membres du "
     "corps militaire du contrôle général des armées", "militaires"),
    ("Décret n° 2021-1761 du 22 décembre 2021 modifiant l'échelonnement indiciaire applicable "
     "aux militaires du rang, aux militaires du rang de la brigade de sapeurs-pompiers de Paris "
     "et aux aspirants", "militaires"),
    # Les personnels civils et militaires ensemble, ce sont tous ceux de l'État.
    ("Décret n° 2008-385 du 23 avril 2008 relatif à l'échelonnement indiciaire des corps et "
     "emplois des personnels civils et militaires de l'Etat", ""),
    # Des corps civils dont le nom dit « officier » ou « militaire ».
    ("Arrêté du 13 mars 1989 fixant l'échelonnement indiciaire applicable au corps des "
     "officiers contrôleurs en chef de la circulation aérienne et au corps des officiers "
     "contrôleurs de la circulation aérienne", ""),
    ("Arrêté du 7 mars 1985 relatif à l'échelonnement indiciaire de certains personnels de "
     "l'enseignement supérieur (école militaire de SAINT-CYR et autres écoles de COETQUIDAN)", ""),
])
def test_le_versant_des_militaires_se_lit_au_titre(titre, versant):
    assert grilles.versant(titre) == versant
    assert grilles.TITRE_GRILLE.search(titre)


# ---------------------------------------------------------------------------
# L'extraction et la certification
# ---------------------------------------------------------------------------

EN = "2999-01-01"

#: Décret n° 2009-21, article 1er, versions du 1er janvier 2009
#: (LEGIARTI000020091038) et du 1er janvier 2022 (LEGIARTI000044620578), telles
#: quelles : les aspirants.
ASPIRANTS_2009 = (
    "L'échelonnement indiciaire applicable aux aspirants, mentionné à l'article R. 4131-13 du "
    "code susvisé, est fixé comme suit : GRADE ÉCHELLE DE SOLDE ÉCHELON INDICE BRUT Aspirant. "
    "Echelle de solde n° 4 7e échelon 558 6e échelon 529 5e échelon 505 4e échelon 486 3e "
    "échelon 460 2e échelon 441 1er échelon 419 Echelle de solde n° 3 5e échelon 396 4e "
    "échelon 385 3e échelon 374 2e échelon 366 1er échelon 362 Echelle de solde n° 2 2e "
    "échelon 355 1er échelon 320")
ASPIRANTS_2022 = (
    "Conformément à l'article 3 du décret n° 2021-1761 du 22 décembre 2021, ces dispositions "
    "entrent en vigueur le 1er janvier 2022. L'échelonnement indiciaire applicable aux "
    "aspirants, mentionné à l'article R. 4131-13 du code susvisé, est fixé comme suit : GRADE "
    "ÉCHELLE DE SOLDE ÉCHELON INDICE BRUT Aspirant Echelle de solde n° 4 7e échelon 558 6e "
    "échelon 529 5e échelon 505 4e échelon 486 3e échelon 460 2e échelon 441 1er échelon 419 "
    "Echelle de solde n° 3 5e échelon 396 4e échelon 385 3e échelon 374 2e échelon 371 1er "
    "échelon 370 Echelle de solde n° 2 2e échelon 368 1er échelon 367")


@pytest.fixture
def index(tmp_path: Path) -> Path:
    """Un index LEGI de quelques documents, au schéma de ``dila_index.py`` : le
    décret n° 2009-21 et deux versions de son article 1er ; un décret des
    personnels civils et militaires de l'État, qui ne compte pas."""
    dila = _charger("dila_index")
    chemin = tmp_path / "legi.sqlite"
    db = dila.ouvrir(chemin)
    titre = ("Décret n° 2009-21 du 7 janvier 2009 fixant les indices de solde applicables à "
             "certains militaires non officiers")
    lignes = [
        ("LEGITEXT000020091010", "2009-01-01", EN, "DECRET", "", titre, "Le Premier ministre…"),
        ("LEGIARTI000020091038", "2009-01-01", "2022-01-01", "Article DECRET", "1", titre,
         ASPIRANTS_2009),
        ("LEGIARTI000044620578", "2022-01-01", EN, "Article DECRET", "1", titre, ASPIRANTS_2022),
        ("LEGITEXT000018689331", "2008-04-25", EN, "DECRET", "",
         "Décret n° 2008-385 du 23 avril 2008 relatif à l'échelonnement indiciaire des corps et "
         "emplois des personnels civils et militaires de l'Etat", "…"),
    ]
    db.executemany("INSERT INTO doc VALUES (?,?,?,?,?,?,?)", lignes)
    db.execute("INSERT INTO meta VALUES ('dump', 'Freemium_legi_global_20250713-140000.tar.gz')")
    db.execute("INSERT INTO meta VALUES ('dernier_increment', '20261102-213929')")
    db.commit()
    db.close()
    return chemin


def test_l_extraction_ecrit_les_grilles_des_militaires(index, tmp_path):
    extrait = grilles.extraire(index)
    assert extrait["territoriale"]["textes"] == extrait["hospitaliere"]["textes"] == []
    militaires = extrait["militaires"]
    (texte,) = militaires["textes"]
    assert (texte["texte"], texte["numero"], texte["signature"], texte["articles_lus"]) == (
        "LEGITEXT000020091010", "2009-21", "2009-01-07", "2")
    assert [g["grille"] for g in militaires["grilles"]] == [
        "aspirant-echelle-de-solde-n-2", "aspirant-echelle-de-solde-n-3",
        "aspirant-echelle-de-solde-n-4"]
    premier = [(e["debut"], e["fin"], e["indice"], e["article"]) for e in militaires["echelons"]
               if e["grille"] == "aspirant-echelle-de-solde-n-2" and e["echelon"] == "1"]
    assert premier == [("2009-01-01", "2021-12-31", "320", "LEGIARTI000020091038"),
                       ("2022-01-01", "", "367", "LEGIARTI000044620578")]
    brut = grilles.brut(extrait, source="essai")
    cle = "LEGITEXT000020091010|aspirant-echelle-de-solde-n-4|7|2009-01-01"
    assert (brut["militaires"]["indice"][cle], brut["militaires"]["rang"][cle]) == (558, 7)

    grilles.ecrire_reference(extrait, tmp_path / "grilles")
    with (tmp_path / "grilles" / "militaires" / "echelons.csv").open(encoding="utf-8") as flux:
        entete = [l for l in flux if l.startswith("#")]
    assert any("source_id: dila_legi_grilles" in l for l in entete)


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def test_verifier_donnees_certifie_les_grilles_des_militaires(index, tmp_path, monkeypatch):
    import dataclasses
    import json

    verifier = _charger("verifier_donnees", RACINE / "scripts" / "verifier_donnees.py")
    monkeypatch.setattr(verifier, "BRUT", tmp_path)
    extrait = grilles.extraire(index)
    (tmp_path / "dila_legi_grilles.json").write_text(
        json.dumps(grilles.brut(extrait, source="essai")), encoding="utf-8")
    dossier = tmp_path / "grilles"
    grilles.ecrire_reference(extrait, dossier)

    certifications = [c for c in verifier.CERTIFICATIONS if c.nom.startswith("grilles_militaires_")]
    assert sorted(c.nom for c in certifications) == sorted(
        f"grilles_militaires_{serie}"
        for serie in ("rang", "indice", "rang_presume", "indice_presume"))
    for certification in certifications:
        assert certification.chemin == RACINE / "data" / "reference" / "grilles" / "militaires" / \
            "echelons.csv"
        messages, trace = dataclasses.replace(
            certification, chemin=dossier / "militaires" / "echelons.csv").confronter(
                appliquer=True)
        assert messages[0].startswith(("OK", "RIEN")), messages
    assert {l["fiabilite"] for l in _lire_csv(dossier / "militaires" / "echelons.csv")} == {
        "certifiee"}


# ---------------------------------------------------------------------------
# La donnée, confrontée au Noyau RH de l'État
# ---------------------------------------------------------------------------

GRILLES = RACINE / "data" / "reference" / "grilles"


def _en_vigueur(lignes: list[dict[str, str]], le: str) -> list[dict[str, str]]:
    return [l for l in lignes if l["debut"] <= le and (not l["fin"] or le <= l["fin"])]


def _hauteurs(lignes: list[dict[str, str]]) -> list[str]:
    """Les indices d'une grille, ou ses lettres de hors-échelle, du plus bas au
    plus haut : le noyau ne numérote pas comme le texte les échelons
    exceptionnels (le rang 7 deux fois pour les caporaux-chefs), mais l'indice
    ne baisse jamais quand l'échelon monte."""
    return sorted((l["indice"] or f"HE{l['hors_echelle']}") for l in lignes)


def _legi(texte: str, grille: str, le: str) -> list[dict[str, str]]:
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / "militaires" / "echelons.csv"), le)
              if l["texte"] == texte and l["grille"] == grille]
    assert lignes and all(l["fiabilite"] == "certifiee" for l in lignes), (grille, le)
    return lignes


def _noyau(grille: str, le: str) -> list[dict[str, str]]:
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / "etat" / "echelons.csv"), le)
              if l["grille"] == grille]
    assert lignes, (grille, le)
    return lignes


#: Des grilles du Noyau RH de l'État (CISIRH, juillet 2026 : ``grilles/etat/``),
#: par son identifiant, et celles du LEGI qui leur répondent, par leur texte et
#: leur clé, aux dates où les deux doivent dire la même chose — jusqu'au
#: 14 décembre 2024 pour les adjudants-chefs, jusqu'au 14 décembre 2025 pour les
#: officiers, que le noyau n'a pas encore suivis (plus bas).
NOYAU = {
    ("03479", "LEGITEXT000020091010", "aspirant-echelle-de-solde-n-2"):
        ("2009-06-01", "2018-06-01", "2026-06-01"),
    ("03481", "LEGITEXT000020091010", "aspirant-echelle-de-solde-n-4"):
        ("2009-06-01", "2018-06-01", "2026-06-01"),
    ("03613", "LEGITEXT000020091010", "sergent-chef-ou-maitre-echelle-de-solde-n-4"):
        ("2009-06-01", "2016-06-01", "2026-06-01"),
    ("03615", "LEGITEXT000020091010", "sergent-ou-second-maitre-echelle-de-solde-n-4"):
        ("2010-06-01", "2020-06-01", "2026-06-01"),
    ("03610", "LEGITEXT000020091010", "adjudant-chef-ou-maitre-principal-echelle-de-solde-n-4"):
        ("2012-06-01", "2020-06-01", "2024-06-01"),
    ("03627", "LEGITEXT000020091010",
     "caporal-chef-ou-quartier-maitre-de-1re-classe-echelle-de-solde-n-3"):
        ("2009-06-01", "2024-06-01"),
    ("03619", "LEGITEXT000023855580", "adjudant-chef"): ("2012-06-01", "2026-06-01"),
    ("03622", "LEGITEXT000023855580", "gendarme"): ("2017-06-01", "2026-06-01"),
    ("03484", "LEGITEXT000020129955", "capitaine-ou-lieutenant-de-vaisseau"):
        ("2009-06-01", "2020-06-01", "2025-06-01"),
    ("03606", "LEGITEXT000023855580", "capitaine-article-1"): ("2012-06-01", "2025-06-01"),
    ("03704", "LEGITEXT000020129945", "medecin"): ("2009-06-01", "2025-06-01"),
}


@pytest.mark.parametrize("noyau, texte, grille", sorted(NOYAU))
def test_les_grilles_des_militaires_redonnent_celles_du_noyau_rh(noyau, texte, grille):
    for le in NOYAU[(noyau, texte, grille)]:
        assert _hauteurs(_legi(texte, grille, le)) == _hauteurs(_noyau(noyau, le)), le


def test_le_decret_2014_1257_vaut_au_1er_novembre_2014():
    """Le décret n° 2014-1257 entre en vigueur le premier jour du mois qui suit
    sa publication (article 3), le 1er novembre 2014 : le décret n° 2015-1041,
    qui le portait au 1er janvier 2014, a été retiré par le n° 2015-1304. Le LEGI
    l'a gardé au 1er janvier pour l'article 2 du décret n° 2009-21 seul ; ses
    articles 3, et 1er du n° 2009-23, disent bien le 1er novembre. Les majors
    passent, eux, au décret n° 2014-988 le 1er septembre 2014."""
    lignes = _lire_csv(GRILLES / "militaires" / "echelons.csv")

    def periodes(grille: str) -> list[tuple[str, str, str, str]]:
        return [(l["debut"], l["fin"], l["indice"], l["article"]) for l in lignes
                if l["texte"] == "LEGITEXT000020091010" and l["grille"] == grille
                and l["echelon"] == "1" and "2014-01-01" <= l["debut"] <= "2014-12-31"]

    assert periodes("sergent-ou-second-maitre-echelle-de-solde-n-2") == [
        ("2014-11-01", "2014-12-31", "308", "LEGIARTI000029672106")]
    assert periodes("soldat-ou-matelot-echelle-de-solde-n-2") == [
        ("2014-11-01", "2014-12-31", "307", "LEGIARTI000029672102")]
    assert periodes("major-echelle-de-solde-n-4") == [
        ("2014-09-01", "2015-11-30", "548", "LEGIARTI000029415839")]


def test_le_noyau_rh_n_a_pas_encore_les_grilles_du_decret_2024_1121():
    """Écart connu : le décret n° 2024-1121 relève au 15 décembre 2024 les
    indices des majors (article 2 du décret n° 2009-21, LEGIARTI000050741889 :
    « Echelon exceptionnel 772 6e échelon 739 5e échelon 725 4e échelon 699 3e
    échelon 672 2e échelon 640 1er échelon 607 »), que le noyau de juillet 2026
    n'a pas encore pris. S'il les prend, ce test le dira : la confrontation
    pourra courir au-delà de décembre 2024."""
    legi = _legi("LEGITEXT000020091010", "major-echelle-de-solde-n-4", "2025-06-01")
    assert _hauteurs(legi) == ["607", "640", "672", "699", "725", "739", "772"]
    assert _hauteurs(_noyau("03609", "2025-06-01")) != _hauteurs(legi)
