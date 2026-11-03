"""Les grilles indiciaires de la fonction publique de l'État (action 158, étape 2).

Deux choses sont vérifiées. La lecture du Noyau RH du CISIRH
(``scripts/fetch/cisirh_grilles.py``), sur une archive de quelques XML écrits
au format de la livraison de juillet 2026 : ce qui se garde de chaque tableau,
et sous quelle forme. Puis la donnée elle-même, sous ``data/reference/grilles/``,
confrontée à une source qui ne la recopie pas : la grille que le ministère de
l'agriculture publie pour ses techniciens supérieurs au 1er juillet 2024, avec
l'indice majoré, la durée moyenne et le traitement mensuel de chaque échelon.
Le traitement s'y recompose de trois pièces indépendantes : l'indice brut de
la grille, le barème qui le fait majoré, et la valeur du point du dépôt.
"""

from __future__ import annotations

import csv
import importlib.util
import io
import sys
import zipfile
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
GRILLES = RACINE / "data" / "reference" / "grilles" / "etat"


def _charger(nom: str):
    chemin = RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


grilles = _charger("cisirh_grilles")


# ---------------------------------------------------------------------------
# La lecture du Noyau RH
# ---------------------------------------------------------------------------

def _table(nom: str, enregistrements: str) -> bytes:
    """Un tableau du Noyau RH, tel que la livraison l'écrit : ISO-8859-15, un
    en-tête, puis un élément ``R_<TABLE>`` par ligne."""
    return (
        '<?xml version="1.0" encoding="ISO-8859-15"?>\n'
        f"<FICHIER_OGR><ENTETE><VERSION_DIFFUSION>26.00.00</VERSION_DIFFUSION> "
        f"<ID_REF>{nom}</ID_REF> <MODE_MAJ>C</MODE_MAJ></ENTETE> "
        f"<DONNEES_MAJ>{enregistrements}</DONNEES_MAJ></FICHIER_OGR>\n"
    ).encode("iso-8859-15")


CORPS = """<R_CORPS><R_FOR_IDEN05>01028</R_FOR_IDEN05> <R_FOR_DATDEB>2011-05-06</R_FOR_DATDEB>
<R_FOR_DATFIN/> <R_FOR_LIBLON>Techniciens supérieurs du ministère chargé de l'agriculture</R_FOR_LIBLON>
<R_REL_CATEGO>2</R_REL_CATEGO> <R_REL_FILIER>05</R_REL_FILIER> <R_REL_NACORP>1</R_REL_NACORP>
<R_REL_MINIST>MI120</R_REL_MINIST> <R_REL_COANTE>00633</R_REL_COANTE> <R_REL_COSUCS/>
<R_CORPS_TEXTE></R_CORPS_TEXTE> <R_CORPS_TEXTE><R_REL_IDTEXT>00000002964</R_REL_IDTEXT>
<R_REL_NATTEX>1</R_REL_NATTEX></R_CORPS_TEXTE></R_CORPS>"""

GRADE = """<R_GRADE><R_FOR_IDEN05>04026</R_FOR_IDEN05> <R_FOR_DATDEB>2022-09-01</R_FOR_DATDEB>
<R_FOR_DATFIN/> <R_FOR_LIBLOM>Technicien du ministère chargé de l'agriculture</R_FOR_LIBLOM>
<R_REL_CORPS>01028</R_REL_CORPS> <R_REL_GRIIND>03779</R_REL_GRIIND> <R_REL_CODPCS>451E</R_REL_CODPCS>
<R_REL_CODNNE>0045010</R_REL_CODNNE> <R_REL_GRANTE>03341</R_REL_GRANTE> <R_REL_GRANTE>03342</R_REL_GRANTE>
<R_REL_GRSUCS/> <R_GRADE_TEXTE><R_REL_IDTEXT>00000006120</R_REL_IDTEXT> <R_REL_NATTEX>3</R_REL_NATTEX>
</R_GRADE_TEXTE></R_GRADE>"""

GRILLE = """<R_GRILLE_IND><R_FOR_IDEN05>03779</R_FOR_IDEN05> <R_FOR_DATDEB>2022-09-01</R_FOR_DATDEB>
<R_FOR_DATFIN/> <R_FOR_LIBLON>Grille partagée du premier grade du NES B</R_FOR_LIBLON>
<R_REL_TYPIND>INBRU</R_REL_TYPIND> <R_REL_GIANTE>03341</R_REL_GIANTE> <R_REL_GISUCS/>
<R_GRILLE_TEXTE></R_GRILLE_TEXTE> <R_GRILLE_TEXTE><R_REL_IDTEXT>00000001197</R_REL_IDTEXT>
<R_REL_NATTEX>1</R_REL_NATTEX> </R_GRILLE_TEXTE> <R_GRILLE_TEXTE><R_REL_IDTEXT>00000001189</R_REL_IDTEXT>
<R_REL_NATTEX>3</R_REL_NATTEX> </R_GRILLE_TEXTE></R_GRILLE_IND>"""


def _echelon(ident: str, debut: str, fin: str, rang: str, indice: str, duree: str,
             suivant: str, stagiaire: str = "0", hors_echelle: str = "") -> str:
    return (f"<R_ECHELON><R_FOR_IDEN05>{ident}</R_FOR_IDEN05> <R_FOR_DATDEB>{debut}</R_FOR_DATDEB> "
            f"<R_FOR_DATFIN>{fin}</R_FOR_DATFIN> <R_FOR_LIBLON>{rang}e échelon</R_FOR_LIBLON> "
            f"<R_FOR_DURMIN>{duree}</R_FOR_DURMIN> <R_FOR_DURMOY>{duree}</R_FOR_DURMOY> "
            f"<R_FOR_DURMAX>{duree}</R_FOR_DURMAX> <R_REL_ECSUIV>{suivant}</R_REL_ECSUIV> "
            f"<R_ADM_ECHSTG>{stagiaire}</R_ADM_ECHSTG> <R_ADM_ECHFON>0</R_ADM_ECHFON> "
            f"<R_ADM_ECHEXC>0</R_ADM_ECHEXC> <R_ADM_ECHELV>0</R_ADM_ECHELV> <R_ADM_ECHPRO>0</R_ADM_ECHPRO> "
            f"<R_ADM_ECHIND>{indice}</R_ADM_ECHIND> <R_REL_HOECHL>{hors_echelle}</R_REL_HOECHL> "
            f"<R_REL_GRIIND>03779</R_REL_GRIIND> <R_REL_CHEVRO/> <R_REL_RANECH>{rang}</R_REL_RANECH> "
            f"<R_ECHELON_ADAGE><R_REL_ADACPT>1</R_REL_ADACPT></R_ECHELON_ADAGE></R_ECHELON>")


ECHELONS = (
    _echelon("50001", "2022-09-01", "2023-12-31", "01", "0389", "0100", "50002")
    + _echelon("50001", "2024-01-01", "", "01", "0392", "0100", "50002")
    + _echelon("50002", "2022-09-01", "", "02", "0397", "0206", "", stagiaire="1")
    + _echelon("50003", "2022-09-01", "", "03", "", "0000", "", hors_echelle="A")
)

INDICES = """<R_INDICE><R_FOR_IDEN04>1015</R_FOR_IDEN04> <R_FOR_DATDEB>2024-01-01</R_FOR_DATDEB>
<R_FOR_DATFIN/> <R_ADM_INDMAJ>0826</R_ADM_INDMAJ></R_INDICE>
<R_INDICE><R_FOR_IDEN04>0389</R_FOR_IDEN04> <R_FOR_DATDEB>2009-07-01</R_FOR_DATDEB>
<R_FOR_DATFIN>2023-12-31</R_FOR_DATFIN> <R_ADM_INDMAJ>0356</R_ADM_INDMAJ></R_INDICE>
<R_INDICE><R_FOR_IDEN04>0389</R_FOR_IDEN04> <R_FOR_DATDEB>2024-01-01</R_FOR_DATDEB>
<R_FOR_DATFIN/> <R_ADM_INDMAJ>0371</R_ADM_INDMAJ></R_INDICE>"""


def _texte(ident: str, numero: str, titre: str) -> str:
    return (f"<R_TEXTE><R_ADM_TEXIDE>{ident}</R_ADM_TEXIDE> <R_ADM_TEXDTE>2010-08-26</R_ADM_TEXDTE> "
            f"<R_ADM_TEXDEF>2010-09-01</R_ADM_TEXDEF> <R_ADM_TEXDPU>2010-08-31</R_ADM_TEXDPU> "
            f"<R_ADM_TEXFVA/> <R_ADM_TEXNUM>{numero}</R_ADM_TEXNUM> <R_ADM_TEXNOR>MENH1018555D</R_ADM_TEXNOR> "
            f"<R_ADM_TEXBIF>JORFTEXT000022752209</R_ADM_TEXBIF> <R_REL_TYPTEX>01</R_REL_TYPTEX> "
            f"<R_ADM_TEXLIB>{titre}</R_ADM_TEXLIB></R_TEXTE>")


TEXTES = (
    _texte("00000001197", "2010-1007", "Décret n° 2010-1007 du 26 août 2010 fixant l'échelonnement indiciaire")
    + _texte("00000001189", "2012-31", "Décret n° 2012-31 du 9 janvier 2012")
    + _texte("00000002964", "2011-489", "Décret n° 2011-489 du 4 mai 2011")
    + _texte("00000006120", "2022-1200", "Décret n° 2022-1200 du 31 août 2022")
    + _texte("00000009999", "2001-1", "Décret n° 2001-1 qu'aucune grille ne cite")
)


CATEGORIES = "".join(
    f"<R_CATG_STATUTAIRE><R_FOR_IDEN02>{code}</R_FOR_IDEN02> <R_FOR_LIBCOU>{libelle}</R_FOR_LIBCOU>"
    f"</R_CATG_STATUTAIRE>"
    for code, libelle in (("1", "catégorie A"), ("2", "catégorie B"), ("7", "Officier")))


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    chemin = tmp_path / "nomenclatures.zip"
    prefixe = "INGRES_C_V26.00.00_F26.00.00_P00_"
    with zipfile.ZipFile(chemin, "w") as flux:
        for nom, numero, enregistrements in (
                ("CORPS", "00024", CORPS), ("GRADE", "00030", GRADE),
                ("GRILLE_IND", "00026", GRILLE), ("ECHELON", "00029", ECHELONS),
                ("INDICE", "00027", INDICES), ("TEXTE", "00207", TEXTES),
                ("CATG_STATUTAIRE", "00013", CATEGORIES)):
            flux.writestr(f"{prefixe}{nom}_{numero}.xml", _table(nom, enregistrements))
        flux.writestr(f"{prefixe}NATU_TEXTE_00181.xml", _table("NATU_TEXTE", ""))
    return chemin


@pytest.fixture
def extrait(archive: Path) -> dict[str, list[dict[str, str]]]:
    return grilles.extraire(grilles.lire_archive(archive))


def test_les_echelons_portent_leur_indice_leurs_durees_en_mois_et_leurs_dates(extrait):
    assert extrait["echelons"] == [
        {"echelon": "50001", "debut": "2022-09-01", "fin": "2023-12-31", "grille": "03779",
         "rang": "1", "indice": "389", "hors_echelle": "", "chevron": "", "nature": "",
         "duree_min": "12", "duree_moy": "12", "duree_max": "12", "suivant": "50002"},
        {"echelon": "50001", "debut": "2024-01-01", "fin": "", "grille": "03779",
         "rang": "1", "indice": "392", "hors_echelle": "", "chevron": "", "nature": "",
         "duree_min": "12", "duree_moy": "12", "duree_max": "12", "suivant": "50002"},
        {"echelon": "50002", "debut": "2022-09-01", "fin": "", "grille": "03779",
         "rang": "2", "indice": "397", "hors_echelle": "", "chevron": "", "nature": "stagiaire",
         "duree_min": "30", "duree_moy": "30", "duree_max": "30", "suivant": ""},
        {"echelon": "50003", "debut": "2022-09-01", "fin": "", "grille": "03779",
         "rang": "3", "indice": "", "hors_echelle": "A", "chevron": "", "nature": "",
         "duree_min": "0", "duree_moy": "0", "duree_max": "0", "suivant": ""},
    ]


def test_la_grille_garde_ses_textes_et_ses_voisines(extrait):
    assert extrait["grilles"] == [
        {"grille": "03779", "debut": "2022-09-01", "fin": "",
         "libelle": "Grille partagée du premier grade du NES B", "type_indice": "brut",
         "anterieure": "03341", "suivante": "", "textes": "1197:origine 1189:modificatif"},
    ]


def test_le_grade_relie_son_corps_a_sa_grille(extrait):
    assert extrait["grades"] == [
        {"grade": "04026", "debut": "2022-09-01", "fin": "",
         "libelle": "Technicien du ministère chargé de l'agriculture", "corps": "01028",
         "grille": "03779", "pcs": "451E", "nne": "0045010", "anterieurs": "03341 03342",
         "suivants": "", "textes": "6120:modificatif"},
    ]
    assert extrait["corps"] == [
        {"corps": "01028", "debut": "2011-05-06", "fin": "",
         "libelle": "Techniciens supérieurs du ministère chargé de l'agriculture",
         "categorie": "B", "filiere": "05", "nature": "1", "ministere": "MI120",
         "anterieurs": "00633", "suivants": "", "textes": "2964:origine"},
    ]


def test_le_bareme_et_les_seuls_textes_que_les_grilles_citent(extrait):
    assert extrait["indices"] == [
        {"indice_brut": "389", "debut": "2009-07-01", "fin": "2023-12-31", "indice_majore": "356"},
        {"indice_brut": "389", "debut": "2024-01-01", "fin": "", "indice_majore": "371"},
        {"indice_brut": "1015", "debut": "2024-01-01", "fin": "", "indice_majore": "826"},
    ]
    assert [t["texte"] for t in extrait["textes"]] == ["1189", "1197", "2964", "6120"]
    assert extrait["textes"][1] == {
        "texte": "1197", "numero": "2010-1007", "date": "2010-08-26", "effet": "2010-09-01",
        "publication": "2010-08-31", "fin": "", "nor": "MENH1018555D",
        "jorf": "JORFTEXT000022752209",
        "titre": "Décret n° 2010-1007 du 26 août 2010 fixant l'échelonnement indiciaire"}


def test_le_fichier_brut_porte_les_valeurs_a_certifier(extrait):
    brut = grilles.brut(extrait, source="nomenclatures.zip")
    assert brut["source"] == "nomenclatures.zip"
    assert brut["indice"]["50001|2024-01-01"] == 392
    assert "50003|2022-09-01" not in brut["indice"]
    assert brut["duree_moy"]["50002|2022-09-01"] == 30
    assert brut["indice_majore"]["389|2024-01-01"] == 371


def test_verifier_donnees_certifie_les_echelons_et_le_bareme(extrait, tmp_path, monkeypatch):
    """La certification relit le fichier brut du récupérateur : chaque colonne
    certifiée des échelons et du barème, et elle seule, passe ``certifiee``."""
    import dataclasses
    import json

    verifier = _charger_verifier()
    monkeypatch.setattr(verifier, "BRUT", tmp_path)
    (tmp_path / "cisirh_grilles.json").write_text(
        json.dumps(grilles.brut(extrait, source="essai")), encoding="utf-8")
    dossier = tmp_path / "etat"
    grilles.ecrire_reference(extrait, dossier)
    ordre = {f: [l[grilles.COLONNES[f][0]] for l in _lire_csv(dossier / f"{f}.csv")]
             for f in grilles.CERTIFIEES}

    # Celles du Noyau RH seules : non ``grilles_etat_legi_*``, l'État lu au LEGI.
    certifications = [c for c in verifier.CERTIFICATIONS if c.nom.startswith("grilles_etat_")
                      and c.chemin.parent.name == "etat"]
    assert sorted((c.chemin.name, c.colonne) for c in certifications) == sorted(
        (f"{fichier}.csv", colonne)
        for fichier, colonnes in grilles.CERTIFIEES.items() for colonne in colonnes)
    for certification in certifications:
        assert certification.chemin.parent == GRILLES
        messages, trace = dataclasses.replace(
            certification, chemin=dossier / certification.chemin.name).confronter(appliquer=True)
        assert messages[0].startswith("OK"), messages
        assert trace["corrigees"] == trace["ajoutees"] == 0, messages
    for fichier in grilles.CERTIFIEES:
        certifie = _lire_csv(dossier / f"{fichier}.csv")
        assert {l["fiabilite"] for l in certifie} == {"certifiee"}
        # La certification ne déplace aucune ligne : l'indice brut se trie en nombre.
        assert [l[grilles.COLONNES[fichier][0]] for l in certifie] == ordre[fichier]


def _charger_verifier():
    chemin = RACINE / "scripts" / "verifier_donnees.py"
    specification = importlib.util.spec_from_file_location("verifier_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_donnees"] = module
    specification.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# La donnée, confrontée à une grille publiée
# ---------------------------------------------------------------------------

#: « Grille indiciaire et traitement brut. Données actualisées au 1er juillet
#: 2024 (Valeur du point = 4,923) », ministère de l'agriculture, corps des
#: techniciens supérieurs (infoma.agriculture.gouv.fr, grille_remu_tsma.pdf,
#: lue le 2 novembre 2026). Par grade : l'échelon, sa durée moyenne en années
#: (vide au dernier), l'indice majoré et le traitement mensuel brut, en euros.
TSMA_1ER_JUILLET_2024 = {
    "04026": """1 1 373 1836.17 | 2 1 374 1841.08 | 3 1 375 1846.08 | 4 1 376 1851.00
                | 5 2 377 1855.92 | 6 2 386 1900.17 | 7 2 401 1974.00 | 8 3 420 2067.58
                | 9 3 436 2146.33 | 10 3 446 2195.58 | 11 3 462 2274.33 | 12 4 482 2372.75
                | 13 - 508 2500.75""",
    "04027": """1 1 376 1851.00 | 2 1 377 1855.92 | 3 2 384 1890.33 | 4 2 395 1944.50
                | 5 2 406 1998.67 | 6 2 421 2072.50 | 7 3 441 2170.92 | 8 3 457 2249.75
                | 9 3 466 2294.00 | 10 3 485 2387.58 | 11 4 509 2505.67 | 12 - 539 2653.42""",
    "04028": """1 1 397 1954.33 | 2 2 409 2013.42 | 3 2 424 2087.25 | 4 2 446 2195.58
                | 5 2 470 2313.67 | 6 3 489 2407.25 | 7 3 513 2525.42 | 8 3 539 2653.42
                | 9 3 556 2737.08 | 10 3 574 2825.67 | 11 - 592 2914.25""",
}


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def _en_vigueur(lignes: list[dict[str, str]], le: str) -> list[dict[str, str]]:
    return [l for l in lignes if l["debut"] <= le and (not l["fin"] or le <= l["fin"])]


def _point_annuel(annee: int) -> float:
    chemin = RACINE / "data" / "reference" / "legislation" / "point_indice_fonction_publique.csv"
    return {int(l["annee"]): float(l["valeur"]) for l in _lire_csv(chemin)}[annee]


@pytest.mark.parametrize("grade", sorted(TSMA_1ER_JUILLET_2024))
def test_la_grille_et_le_bareme_recomposent_le_traitement_publie(grade: str):
    le = "2024-07-01"
    (ligne_grade,) = [g for g in _en_vigueur(_lire_csv(GRILLES / "grades.csv"), le)
                      if g["grade"] == grade]
    echelons = {int(e["rang"]): e for e in _en_vigueur(_lire_csv(GRILLES / "echelons.csv"), le)
                if e["grille"] == ligne_grade["grille"]}
    bareme = {int(i["indice_brut"]): int(i["indice_majore"])
              for i in _en_vigueur(_lire_csv(GRILLES / "indices.csv"), le)}
    point = _point_annuel(2024)

    publie = [ligne.split() for ligne in TSMA_1ER_JUILLET_2024[grade].split("|")]
    assert sorted(echelons) == [int(rang) for rang, *_ in publie]
    for rang, duree, majore, mensuel in publie:
        echelon = echelons[int(rang)]
        assert bareme[int(echelon["indice"])] == int(majore), (grade, rang)
        # Le traitement annuel s'arrondit à l'euro, puis se divise par douze.
        assert round(round(int(majore) * point) / 12, 2) == float(mensuel), (grade, rang)
        if duree != "-":
            assert int(echelon["duree_moy"]) == 12 * int(duree), (grade, rang)
