"""Tests de l'index plein texte des bases DILA (``scripts/fetch/dila_index.py``)
et de l'outil de recherche (``dila_cherche.py``).

Aucun de ces tests n'accède au réseau : le dump est une archive de quelques
XML fabriqués sur le modèle de ceux de la DILA. Ce qui est vérifié, c'est la
lecture des deux formes de document (texte, article) des deux bases, le filtre
thématique, la mécanique des incréments — remplacement et suppression, avec
l'index FTS qui doit suivre —, et ce que l'outil de recherche imprime.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import random
import sqlite3
import sys
import tarfile
from pathlib import Path

import pytest


def _charger(nom: str):
    chemin = Path(__file__).resolve().parents[1] / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


index = _charger("dila_index")
cherche = _charger("dila_cherche")


def _texte_jorf(ident: str, nature: str, date: str, titre: str, corps: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TEXTE_VERSION>
<META><META_COMMUN><ID>{ident}</ID><ORIGINE>JORF</ORIGINE><NATURE>{nature}</NATURE></META_COMMUN>
<META_SPEC><META_TEXTE_CHRONICLE><DATE_PUBLI>{date}</DATE_PUBLI></META_TEXTE_CHRONICLE>
<META_TEXTE_VERSION><TITRE>{titre[:30]}</TITRE><TITREFULL>{titre}</TITREFULL></META_TEXTE_VERSION></META_SPEC></META>
<NOTICE><CONTENU><p>{corps}</p></CONTENU></NOTICE>
</TEXTE_VERSION>
"""


def _article(ident: str, cid: str, date_publi: str, nature: str, titre_txt: str,
             num: str, corps: str, debut: str = "2999-01-01", fin: str = "2999-01-01",
             nota: str = "") -> str:
    # La NOTA précède le texte de l'article dans le dump, comme ici.
    note = f"<NOTA><CONTENU><p>{nota}</p></CONTENU></NOTA>\n" if nota else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ARTICLE>
<META><META_COMMUN><ID>{ident}</ID><NATURE>Article</NATURE></META_COMMUN>
<META_SPEC><META_ARTICLE><NUM>{num}</NUM><DATE_DEBUT>{debut}</DATE_DEBUT><DATE_FIN>{fin}</DATE_FIN></META_ARTICLE></META_SPEC></META>
<CONTEXTE>
<TEXTE autorite="" cid="{cid}" date_publi="{date_publi}" date_signature="{date_publi}" ministere="" nature="{nature}" nor="">
<TITRE_TXT debut="1952-07-01" fin="2999-01-01" id_txt="{cid}">{titre_txt}</TITRE_TXT>
</TEXTE></CONTEXTE>
{note}<BLOC_TEXTUEL><CONTENU><br/>   {corps}<br/></CONTENU></BLOC_TEXTUEL>
</ARTICLE>
"""


PLAFOND = _texte_jorf(
    "JORFTEXT000000000001", "DECRET", "1969-12-30",
    "Décret n°69-1234 du 29 décembre 1969 PORTANT FIXATION POUR L'ANNEE 1970 DU PLAFOND "
    "DES COTISATIONS DE SECURITE SOCIALE A 18 000 FRS",
    "LE PLAFOND ANNUEL DES COTISATIONS EST FIXE A 18 000 FRS &#224; compter du 01-01-1970.")
NOMINATION = _texte_jorf(
    "JORFTEXT000000000002", "ARRETE", "1970-03-04",
    "Arrêté du 3 mars 1970 portant nomination au conseil d'administration de l'Office "
    "national des forêts", "M. Dupont est nommé membre du conseil.")
ARTICLE_JORF = _article(
    "JORFARTI000000000003", "JORFTEXT000000000001", "1969-12-30", "DECRET",
    "Décret n°69-1234 du 29 décembre 1969", "1",
    "Le plafond des cotisations de sécurité sociale est fixé à 18 000 F par an.")
ARTICLE_LEGI = _article(
    "LEGIARTI000000000004", "LEGITEXT000006073189", "2999-01-01", "CODE",
    "Code de la sécurité sociale", "R351-9",
    "Le trimestre est validé sur la base de 200 heures de salaire minimum de croissance.",
    debut="1972-01-01", fin="2014-01-01")
STRUCTURE = '<?xml version="1.0" encoding="UTF-8"?>\n<STRUCTURE_TA><ID>x</ID></STRUCTURE_TA>\n'


def _archive(chemin: Path, fichiers: dict[str, str]) -> Path:
    with tarfile.open(chemin, "w:gz") as flux:
        for nom, contenu in fichiers.items():
            octets = contenu.encode("utf-8")
            membre = tarfile.TarInfo(nom)
            membre.size = len(octets)
            flux.addfile(membre, io.BytesIO(octets))
    return chemin


@pytest.fixture
def dump(tmp_path: Path) -> Path:
    return _archive(tmp_path / "dump_essai.tar.gz", {
        "jorf/global/JORF/TEXT/00/01/JORFTEXT000000000001/texte/version/JORFTEXT000000000001.xml": PLAFOND,
        "jorf/global/JORF/TEXT/00/02/JORFTEXT000000000002/texte/version/JORFTEXT000000000002.xml": NOMINATION,
        "jorf/global/JORF/ARTI/00/03/JORFARTI000000000003/article/JORFARTI000000000003.xml": ARTICLE_JORF,
        "legi/global/code_en_vigueur/LEGI/ARTI/00/04/LEGIARTI000000000004/article/LEGIARTI000000000004.xml": ARTICLE_LEGI,
        "jorf/global/struct/JORF/SCTA/JORFSCTA000000000005.xml": STRUCTURE,
        "jorf/global/eli/decret/1969/12/29/69-1234": "JORFTEXT000000000001",
    })


@pytest.fixture
def base(tmp_path: Path, dump: Path) -> Path:
    chemin = tmp_path / "jorf.sqlite"
    index.construire("jorf", chemin, archive=dump)
    return chemin


def _ids(chemin: Path) -> set[str]:
    with sqlite3.connect(chemin) as db:
        return {ligne[0] for ligne in db.execute("SELECT id FROM doc")}


def _fts(chemin: Path, requete: str) -> set[str]:
    with sqlite3.connect(chemin) as db:
        return {ligne[0] for ligne in db.execute(
            "SELECT doc.id FROM fts JOIN doc ON doc.rowid = fts.rowid WHERE fts MATCH ?",
            (requete,))}


# ---------------------------------------------------------------------------
# Lecture des XML
# ---------------------------------------------------------------------------

def test_lire_un_texte_du_jorf():
    doc = index.lire(PLAFOND)
    assert (doc.id, doc.date, doc.fin, doc.nature, doc.num) == (
        "JORFTEXT000000000001", "1969-12-30", "", "DECRET", "")
    assert doc.titre.startswith("Décret n°69-1234 du 29 décembre 1969 PORTANT FIXATION")
    # Les balises sont retirées, les entités décodées, les blancs repliés.
    assert "LE PLAFOND ANNUEL DES COTISATIONS EST FIXE A 18 000 FRS à compter" in doc.texte
    assert "<" not in doc.texte


def test_lire_un_article_du_jorf():
    doc = index.lire(ARTICLE_JORF)
    assert doc.nature == "Article DECRET"          # et non « date_signature »
    assert doc.date == "1969-12-30" and doc.fin == "" and doc.num == "1"
    assert doc.titre == "Décret n°69-1234 du 29 décembre 1969"
    assert doc.texte == "Le plafond des cotisations de sécurité sociale est fixé à 18 000 F par an."


def test_lire_un_article_de_legi():
    doc = index.lire(ARTICLE_LEGI)
    assert doc.nature == "Article CODE"
    assert (doc.date, doc.fin, doc.num) == ("1972-01-01", "2014-01-01", "R351-9")
    assert doc.titre == "Code de la sécurité sociale"


def test_lire_ignore_ce_qui_n_est_ni_texte_ni_article():
    assert index.lire(STRUCTURE) is None
    assert index.lire("JORFTEXT000000000001") is None


def test_documents_decoupe_un_flux_concatene():
    flux = io.BytesIO((PLAFOND + NOMINATION + STRUCTURE).encode("utf-8"))
    morceaux = list(index.documents(flux))
    assert len(morceaux) == 3
    assert [index.lire(m).id for m in morceaux[:2]] == ["JORFTEXT000000000001", "JORFTEXT000000000002"]


def test_documents_ne_coupe_pas_un_caractere_accentue_a_la_frontiere_de_lecture():
    """Le flux est lu par blocs de 4 Mo ; un « é » à cheval sur la frontière
    doit ressortir entier, et non en deux caractères de remplacement."""
    bloc = 1 << 22
    debut = "<?xml ?><TEXTE_VERSION><ID>JORFTEXT000000000007</ID><TITREFULL>Retraite"
    bourrage = "x" * (bloc - len(debut.encode("utf-8")) - 1)
    document = debut + bourrage + "é fin</TITREFULL></TEXTE_VERSION>"
    octets = document.encode("utf-8")
    assert octets[bloc - 1:bloc + 1] == "é".encode("utf-8")
    morceaux = list(index.documents(io.BytesIO(octets + PLAFOND.encode("utf-8"))))
    assert len(morceaux) == 2
    assert "\ufffd" not in morceaux[0]
    assert index.lire(morceaux[0]).titre.endswith("xé fin")


# ---------------------------------------------------------------------------
# Construction et filtre
# ---------------------------------------------------------------------------

def test_construire_garde_le_champ_social_et_ecarte_le_reste(base: Path):
    assert _ids(base) == {"JORFTEXT000000000001", "JORFARTI000000000003", "LEGIARTI000000000004"}
    with sqlite3.connect(base) as db:
        assert index.meta(db, "dump") == "dump_essai.tar.gz"
        assert index.meta(db, "filtre") == index.THEMATIQUE.pattern
        assert index.meta(db, "dernier_increment") == ""


def test_construire_tout_ne_filtre_pas(tmp_path: Path, dump: Path):
    chemin = tmp_path / "tout.sqlite"
    index.construire("jorf", chemin, tout=True, archive=dump)
    assert "JORFTEXT000000000002" in _ids(chemin)
    with sqlite3.connect(chemin) as db:
        assert index.meta(db, "filtre") == "tout"


#: Les textes des grilles indiciaires et des carrières des fonctionnaires, des
#: trois versants (action 158, étape 2). Un article porte le titre de son
#: texte : le titre fait entrer tous ses articles, ceux qui écrivent les indices
#: comme ceux qui fixent les durées d'échelon ou les reclassements.
GRILLES = [
    ("Décret n° 2016-604 du 12 mai 2016 fixant les différentes échelles de rémunération "
     "pour les fonctionnaires de catégorie C de la fonction publique territoriale", ""),
    ("Décret n° 2010-330 du 22 mars 2010 fixant l'échelonnement indiciaire applicable aux "
     "membres des cadres d'emplois régis par le décret n° 2010-329 du 22 mars 2010", ""),
    ("DECRET N° 87-1108 DU 30 DECEMBRE 1987 FIXANT LES DIFFERENTES ECHELLES DE REMUNERATION "
     "POUR LA CATEGORIE C DES FONCTIONNAIRES TERRITORIAUX", ""),
    ("Décret n° 2016-596 du 12 mai 2016 relatif à l'organisation des carrières des "
     "fonctionnaires de catégorie C de la fonction publique territoriale", ""),
    ("Décret n° 2006-1691 du 22 décembre 2006 portant statut particulier du cadre "
     "d'emplois des adjoints techniques territoriaux", ""),
    ("Décret n° 2009-1388 du 11 novembre 2009 portant dispositions statutaires communes à "
     "divers corps de fonctionnaires de la catégorie B de la fonction publique de l'Etat", ""),
    ("Décret n° 2009-21 du 7 janvier 2009 relatif au classement indiciaire applicable aux "
     "militaires non officiers", ""),
    ("Décret n° 82-1105 du 23 décembre 1982 relatif aux indices de la fonction publique", ""),
    ("Décret n° 93-863 du 18 juin 1993 relatif aux conditions de mise en oeuvre de la "
     "nouvelle bonification indiciaire dans la fonction publique territoriale", ""),
    # Un article qui écrit les indices au pluriel, sous un titre qui ne dit rien.
    ("Décret n° 2021-1267 du 29 septembre 2021",
     "GRADES ET ÉCHELONS INDICES BRUTS Aide-soignant de classe normale 1er échelon 356"),
]


@pytest.mark.parametrize("titre, texte", GRILLES, ids=[t[:22] for t, _ in GRILLES])
def test_le_filtre_garde_les_grilles_indiciaires_et_les_carrieres(titre: str, texte: str):
    article = index.Document("LEGIARTI000000000010", "2017-01-01", "2999-01-01",
                             "Article DECRET", "1", titre, texte)
    assert index.pertinent(article)


def test_le_filtre_laisse_les_concours_de_ces_corps():
    avis = index.Document("JORFTEXT000000000011", "2016-05-14", "", "ARRETE", "",
                          "Arrêté du 12 mai 2016 portant ouverture d'un concours externe "
                          "pour le recrutement d'adjoints techniques territoriaux",
                          "Un concours est ouvert au titre de l'année 2016.")
    assert not index.pertinent(avis)


#: D. 732-76 et D. 732-77 du code rural, dans la seule rédaction qu'ils ont eue
#: du 22 avril 2005 au 1er janvier 2026 (LEGIARTI000006597490 et
#: LEGIARTI000006597491, lus dans les incréments LEGI de la DILA des 9, 14 et
#: 15 janvier 2026, dont la liste des versions n'en a pas d'autre avant 2026) :
#: la majoration des points de chef de 1952 à 1972, pour l'action 131. Le titre
#: d'un article de code est celui du code, et leur texte ne dit que « points ».
MAJORATIONS_AGRICOLES = [
    ("LEGIARTI000006597490", "D732-76",
     "Le nombre de points acquis par les chefs d'exploitations ou d'entreprises agricoles au "
     "titre de la période comprise entre le 1er juillet 1952 et le 31 décembre 1972 est majoré "
     "de 17 % lorsque le nombre annuel moyen de points acquis par les intéressés au cours de "
     "ladite période est au moins égal à seize."),
    ("LEGIARTI000006597491", "D732-77",
     "Le nombre de points acquis par les chefs d'exploitation ou d'entreprise agricole au titre "
     "de la période comprise entre le 1er juillet 1952 et le 31 décembre 1972 est majoré de : "
     "1° 5 % lorsque le nombre annuel moyen de points acquis par les intéressés au cours de "
     "cette période est compris entre 15 et 19,51. Le taux est déterminé par la formule "
     "suivante : T % = 3,19 x P - 57,23 2° 5 à 30 % et de 30 à 45 % selon que le nombre annuel "
     "moyen de points acquis par les intéressés au cours de cette période est compris entre "
     "19,51 et 27,34 ou est supérieur à 27,34. Le taux est alors déterminé par la formule : "
     "T % = 1,93 x P - 22,74 Le terme P figurant aux formules des 1° et 2° représente le nombre "
     "annuel moyen de points acquis par l'assuré au cours de la période mentionnée au premier "
     "alinéa du présent article."),
]


@pytest.mark.parametrize("ident, num, texte", MAJORATIONS_AGRICOLES,
                         ids=[num for _, num, _ in MAJORATIONS_AGRICOLES])
def test_le_filtre_garde_d_732_76_et_d_732_77_de_2005_a_2025(ident: str, num: str, texte: str):
    article = index.Document(ident, "2005-04-22", "2026-01-01", "Article CODE", num,
                             "Code rural (nouveau)", texte)
    assert index.pertinent(article)


#: Les articles qui fixent la durée des échelons, des trois versants et des
#: militaires, de 1964 à 2025 : des extraits d'articles réels (identifiant en
#: commentaire). Ils doivent passer sur leur seul texte, car un statut ne le dit
#: pas toujours dans son titre (« portant statuts particuliers », « fixant les
#: dispositions statutaires applicables », « relatif aux emplois supérieurs »),
#: ni un article de code : les trois premiers, lus dans les incréments LEGI de la
#: DILA, étaient écartés par le filtre du 2 novembre 2026.
DUREES_D_ECHELON = [
    # Décret n° 95-370, art. 34 (LEGIARTI000034773651) : l'État.
    "La durée du temps passé dans chacun des échelons du corps des ingénieurs d'études est "
    "fixée conformément au tableau ci-après : GRADES ET ÉCHELONS DURÉE Ingénieur d'études hors "
    "classe 9e échelon - 8e échelon 3 ans 7e échelon 2 ans 6 mois",
    # Décret n° 2020-959, art. 27 (LEGIARTI000042199625) : l'hospitalière.
    "L'emploi de directeur général adjoint de l'Assistance publique-hôpitaux de Paris relevant "
    "du groupe I comprend huit échelons. La durée passée dans les deux premiers échelons est "
    "d'un an.",
    # Décret n° 99-1073, art. 13 (LEGIARTI000006513139) : les emplois de la magistrature.
    "Le temps passé dans chacun des échelons de l'emploi de chargé de formation à l'Ecole "
    "nationale de la magistrature est fixé comme suit : ECHELONS : 6e ; DUREE DE L'ECHELON : "
    "3 ans",
    # Décret n° 2003-676, art. 12 (LEGIARTI000032578323) : la territoriale.
    "La durée du temps passé dans chacun des échelons du grade de cadre de santé est fixée "
    "ainsi qu'il suit : GRADE ET ÉCHELONS DURÉE Cadre de santé 7e échelon 4 ans 6e échelon 4 ans",
    # Décret n° 2008-952, art. 6-1 (LEGIARTI000025074407) : les militaires, la gendarmerie.
    "Les conditions d'accès aux échelons du grade de gendarme sont déterminées conformément au "
    "tableau suivant : GRADE ÉCHELLE DE SOLDE ÉCHELON ANCIENNETÉ EXIGÉE dans l'échelon pour "
    "accéder à l'échelon supérieur Gendarme Echelle de solde spécifique des gendarmes 13e / 12e "
    "3 ans",
    # Décret n° 2008-938, art. 32-1 (LEGIARTI000052465302) : les militaires, la marine.
    "Le temps passé aux 1er et 2e échelons est de un an et de deux ans au 3e échelon.",
    # Décret n° 2008-931, art. 17 (LEGIARTI000052465270) : les militaires, les chefs de musique.
    "Les conditions de durée d'échelon et d'accès aux échelons exceptionnels sont déterminées "
    "par grade et par échelle de solde conformément au tableau suivant",
    # Décret n° 64-953, art. 6 (LEGIARTI000043361458).
    "durée moyenne et la durée minimum du temps de services effectifs passé dans chacun des "
    "échelons du grade de contrôleur divisionnaire sont fixées ainsi qu'il suit",
    # Décret n° 70-903, art. 18 (LEGIARTI000006563521).
    "Le temps normalement passé dans chaque échelon du grade provisoire de technicien supérieur "
    "en chef est fixé à trois ans pour les 1er, 2e et 3e échelons",
    # Décret n° 68-503, art. 4 (LEGIARTI000006571922).
    "ECHELONS AVANCEMENT au choix 30 % AVANCEMENT à l'ancienneté 70 % Du 1er au 2e échelon "
    "1 an 3 mois. 2 ans.",
    # Décret n° 89-756, art. 9 (LEGIARTI000006705072).
    "la durée moyenne donnant accès à l'échelon supérieur est de deux ans dans chacun des 1er "
    "et 2e échelons",
    # Décret n° 90-230, art. 10 (LEGIARTI000006458180).
    "La durée moyenne de service requise pour une promotion à l'échelon supérieur est d'un an "
    "dans le 1er échelon",
    # Décret n° 93-145, art. 8 (LEGIARTI000006712672).
    "L'ancienneté moyenne pour être nommé à l'échelon supérieur est de trois ans dans chacun "
    "des deux premiers échelons.",
    # Décret n° 99-314, art. 12 (LEGIARTI000006511446).
    "durées moyenne et minimale dans chaque échelon sont fixées conformément au tableau "
    "ci-après :",
    # Décret n° 2020-959, art. 28 (LEGIARTI000042199627).
    "La durée à accomplir pour accéder à l'échelon supérieur est fixée comme suit :",
    # Décret n° 96-41, art. 21 (LEGIARTI000006481651) : un tableau sans phrase qui l'annonce.
    "sont créés les grades provisoires suivants : GRADES ET ÉCHELONS provisoires DURÉE Moyenne "
    "DURÉE Minimale Technicien en chef 7e échelon - - 6e échelon 4 ans 3 ans",
    # Décret n° 92-873, art. 14 (LEGIARTI000006375774) : un tableau dessiné en caractères.
    ": :-----------------------------: : 1er échelon : 4 ans : 3 ans : : (358)",
]


@pytest.mark.parametrize("texte", DUREES_D_ECHELON, ids=[t[:28] for t in DUREES_D_ECHELON])
def test_le_filtre_garde_les_durees_d_echelon_sur_leur_seul_texte(texte: str):
    assert index.THEMATIQUE.search(texte)


#: Ce que le filtre écarte toujours, quoique ces articles disent « points » ou
#: « échelon » : d'autres sens, lus dans les incréments LEGI de la DILA de
#: décembre 2025 et janvier 2026, où le filtre du 2 novembre 2026 les écartait.
AUTRES_SENS = [
    ("LEGIARTI000020638725", "Article CODE", "L143-1", "Code de la route",
     "L'article L. 130-9 est applicable en Nouvelle-Calédonie et pour son application les "
     "mots : \" lorsqu'il a récupéré le nombre de points ayant été retirés de son permis de "
     "conduire ou \" sont supprimés."),
    ("LEGIARTI000038659119", "Article ARRETE", "9",
     "Arrêté du 17 juin 2019 fixant les règles d'organisation générale, la nature et le "
     "programme des épreuves des concours de recrutement d'adjoints administratifs principaux "
     "de 2e classe de chancellerie du ministère des affaires étrangères",
     "Si plusieurs candidats ont obtenu le même nombre de points, la priorité est accordée à "
     "celui qui a obtenu la note la plus élevée à l'épreuve d'admission."),
    ("LEGIARTI000022479466", "Article CODE", "L566-5", "Code de l'environnement",
     "II. – A l'échelon du bassin ou groupement de bassins, sur la base de l'évaluation "
     "préliminaire des risques d'inondation"),
    ("LEGIARTI000006654764", "Article CODE", "L511-44", "Code monétaire et financier",
     "Elle précise pour chaque organisme les échelons de qualité de crédit auxquelles "
     "correspondent les évaluations réalisées."),
    ("LEGIARTI000006465302", "Article CODE", "L2",
     "Code des postes et des communications électroniques",
     "dont le prix est inférieur à cinq fois le tarif applicable à un envoi de correspondance "
     "du premier échelon de poids de la catégorie normalisée la plus rapide, sont réservés à "
     "La Poste."),
]


@pytest.mark.parametrize("ident, nature, num, titre, texte", AUTRES_SENS,
                         ids=[titre[:22] for _, _, _, titre, _ in AUTRES_SENS])
def test_le_filtre_laisse_les_autres_sens_de_points_et_d_echelon(
        ident: str, nature: str, num: str, titre: str, texte: str):
    assert not index.pertinent(index.Document(ident, "2010-01-01", "2999-01-01", nature, num,
                                              titre, texte))


def test_l_index_fts_ignore_casse_et_accents(base: Path):
    assert _fts(base, "sécurité sociale") == {"JORFTEXT000000000001", "JORFARTI000000000003", "LEGIARTI000000000004"}
    assert _fts(base, "SECURITE") == _fts(base, "sécurité")
    assert _fts(base, '"200 heures"') == {"LEGIARTI000000000004"}


def test_construire_ecrase_une_base_existante(tmp_path: Path, dump: Path):
    chemin = tmp_path / "jorf.sqlite"
    index.construire("jorf", chemin, archive=dump)
    index.construire("jorf", chemin, archive=dump)
    with sqlite3.connect(chemin) as db:
        assert db.execute("SELECT count(*) FROM doc").fetchone()[0] == 3


def test_construire_refuse_un_dump_tronque_sans_laisser_d_index(tmp_path: Path):
    """Un dump coupé en route — un transfert interrompu, un disque plein —
    se lisait jusqu'à la coupure : ``tar`` échouait en silence, et l'index,
    à moitié versé, se disait construit, son dump et son dernier incrément
    écrits (action 190, étape 5). La construction échoue, et ne laisse pas
    d'index qu'un récupérateur lirait."""
    bruit = '<?xml version="1.0"?>\n<BRUIT>' + random.Random(0).randbytes(200_000).hex() + "</BRUIT>"
    entier = _archive(tmp_path / "entier.tar.gz", {
        "jorf/global/JORF/TEXT/00/01/JORFTEXT000000000001/texte/version/JORFTEXT000000000001.xml": PLAFOND,
        "jorf/global/JORF/TEXT/00/09/bruit.xml": bruit,
    })
    tronque = tmp_path / "tronque.tar.gz"
    tronque.write_bytes(entier.read_bytes()[: entier.stat().st_size // 2])
    chemin = tmp_path / "jorf.sqlite"
    with pytest.raises(RuntimeError, match="tronque.tar.gz"):
        index.construire("jorf", chemin, archive=tronque)
    assert not chemin.exists()


# ---------------------------------------------------------------------------
# Incréments
# ---------------------------------------------------------------------------

def test_un_increment_remplace_et_supprime(tmp_path: Path, base: Path):
    republie = _texte_jorf(
        "JORFTEXT000000000001", "DECRET", "1969-12-30",
        "Décret n°69-1234 du 29 décembre 1969 PORTANT FIXATION POUR L'ANNEE 1970 DU PLAFOND "
        "DES COTISATIONS DE SECURITE SOCIALE A 18 000 FRS (RECTIFICATIF)",
        "LE PLAFOND ANNUEL EST FIXE A 18 000 FRS. RECTIFICATIF AU JO DU 31-12-1969.")
    increment = _archive(tmp_path / "JORF_19700105-000000.tar.gz", {
        "19700105-000000/jorf/global/JORF/TEXT/00/01/JORFTEXT000000000001/texte/version/JORFTEXT000000000001.xml": republie,
        "19700105-000000/jorf/global/liste_suppression_jorf.dat":
            "jorf/global/JORF/ARTI/00/03/JORFARTI000000000003/article/JORFARTI000000000003.xml\n",
    })
    with sqlite3.connect(base) as db:
        db.executescript(index.SCHEMA)
        lus, gardes = index.verser_archive(db, increment, tout=False, remplacer=True)
        db.commit()
    assert (lus, gardes) == (1, 1)
    assert _ids(base) == {"JORFTEXT000000000001", "LEGIARTI000000000004"}
    # L'index plein texte a suivi : l'ancien texte n'est plus trouvable, le
    # nouveau l'est, et l'article supprimé ne répond plus.
    assert _fts(base, "compter") == set()
    assert _fts(base, "rectificatif") == {"JORFTEXT000000000001"}
    assert _fts(base, '"par an"') == set()
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM doc WHERE id = ?",
                          ("JORFTEXT000000000001",)).fetchone()[0] == 1


def test_un_increment_hors_champ_retire_un_document_devenu_hors_champ(tmp_path: Path, base: Path):
    """Un document republié sans plus rien du champ social sort de l'index."""
    republie = _texte_jorf("JORFTEXT000000000001", "DECRET", "1969-12-30",
                           "Décret n°69-1234 du 29 décembre 1969 (annulé)", "Texte abrogé.")
    increment = _archive(tmp_path / "JORF_19700106-000000.tar.gz", {
        "19700106-000000/jorf/global/JORF/TEXT/00/01/JORFTEXT000000000001/texte/version/JORFTEXT000000000001.xml": republie,
    })
    with sqlite3.connect(base) as db:
        db.executescript(index.SCHEMA)
        assert index.verser_archive(db, increment, tout=False, remplacer=True) == (1, 0)
        db.commit()
    assert "JORFTEXT000000000001" not in _ids(base)


def test_horodatage_et_tri_des_increments():
    assert index.horodatage("Freemium_jorf_global_20250713-140000.tar.gz") == "20250713-140000"
    assert index.horodatage("JORF_20260913-002329.tar.gz") == "20260913-002329"
    assert index.horodatage("dump_essai.tar.gz") == ""


def test_precharger_telecharge_chaque_increment_en_parallele(tmp_path: Path, monkeypatch):
    vus: list[str] = []
    monkeypatch.setattr(index, "CACHE", tmp_path)
    monkeypatch.setattr(index, "telecharger",
                        lambda url, cible: (vus.append(url), cible.parent.mkdir(exist_ok=True),
                                            cible.write_text("x"), cible)[-1])
    index.precharger("jorf", ["JORF_20260101-000000.tar.gz", "JORF_20260102-000000.tar.gz"])
    assert sorted(vus) == [index.RACINE + "JORF/JORF_20260101-000000.tar.gz",
                           index.RACINE + "JORF/JORF_20260102-000000.tar.gz"]
    assert (tmp_path / "increments" / "JORF_20260102-000000.tar.gz").read_text() == "x"


def test_recuperer_decompresse_l_index_publie(tmp_path: Path, dump: Path, monkeypatch, capsys):
    """Le trajet de ``--recuperer``, la release étant remplacée par un fichier
    local que curl sait lire (``file://``)."""
    import gzip
    import shutil
    origine = tmp_path / "origine.sqlite"
    index.construire("jorf", origine, archive=dump)
    publie = tmp_path / "jorf.sqlite.gz"
    with origine.open("rb") as source, gzip.open(publie, "wb") as cible:
        shutil.copyfileobj(source, cible)
    monkeypatch.setattr(index, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(index, "url_publiee", lambda base: publie.as_uri())
    cible = tmp_path / "recu" / "jorf.sqlite"
    index.recuperer("jorf", cible)
    assert _ids(cible) == _ids(origine)
    assert not (tmp_path / "cache" / "jorf.sqlite.gz").exists()
    assert "3 documents" in capsys.readouterr().err


def test_recuperer_dit_quand_rien_n_est_publie(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(index, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(index, "url_publiee", lambda base: (tmp_path / "absent.gz").as_uri())
    with pytest.raises(RuntimeError):
        index.recuperer("jorf", tmp_path / "jorf.sqlite")


# ---------------------------------------------------------------------------
# L'outil de recherche
# ---------------------------------------------------------------------------

def _options(**valeurs) -> argparse.Namespace:
    defauts = dict(depuis=None, jusqu=None, nature=None, num=None, titre=None, limite=20,
                   extrait=14, compter=False)
    defauts.update(valeurs)
    return argparse.Namespace(**defauts)


def test_chercher_rend_un_extrait_entre_crochets(base: Path):
    db = sqlite3.connect(base)
    lignes, total, soumise = cherche.chercher(db, "plafond cotisations", _options())
    assert total == 2 and soumise == "plafond cotisations"
    assert [l[0] for l in lignes] == ["JORFTEXT000000000001", "JORFARTI000000000003"]
    assert "[PLAFOND]" in lignes[0][6] and "[COTISATIONS]" in lignes[0][6]


def test_chercher_filtre_par_date_nature_et_numero(base: Path):
    db = sqlite3.connect(base)
    assert cherche.chercher(db, "plafond", _options(nature="Article"))[1] == 1
    assert cherche.chercher(db, "plafond", _options(depuis=1970))[1] == 0
    assert cherche.chercher(db, "plafond", _options(jusqu=1969))[1] == 2
    lignes, total, _ = cherche.chercher(db, "heures", _options(num="r 351-9"))
    assert total == 1 and lignes[0][0] == "LEGIARTI000000000004"


def test_chercher_reprend_en_phrase_une_requete_que_fts5_refuse(base: Path):
    db = sqlite3.connect(base)
    lignes, total, soumise = cherche.chercher(db, "fixé à 18 000 F", _options())
    assert total == 1 and soumise == "fixé à 18 000 F"
    _, total, soumise = cherche.chercher(db, "l'annee 1970", _options())
    assert soumise == '"l\'annee 1970"' and total == 1


def test_cli_recherche_et_texte(base: Path, capsys):
    assert cherche.main(["jorf", "plafond", "--index", str(base), "--limite", "1"]) == 0
    sortie = capsys.readouterr().out
    assert sortie.startswith("JORFTEXT000000000001  1969-12-30  DECRET  Décret n°69-1234")
    assert "— 2 documents au total, 1 affichés (--limite)" in sortie

    assert cherche.main(["jorf", "--index", str(base), "--texte", "JORFARTI000000000003",
                         "--motif", "18 000", "--autour", "10"]) == 0
    sortie = capsys.readouterr().out
    assert "Article DECRET art. 1" in sortie
    assert "[48] …st fixé à 18 000 F par an.…" in sortie

    assert cherche.main(["jorf", "--index", str(base), "--compter", "heures"]) == 0
    assert capsys.readouterr().out.strip() == "— 1 documents au total"

    assert cherche.main(["jorf", "--index", str(base), "--texte", "JORFTEXT000000000099"]) == 1
    assert "n'est pas dans l'index" in capsys.readouterr().err

    assert cherche.main(["jorf", "--index", str(base / "absente.sqlite"), "plafond"]) == 1
    assert "--recuperer" in capsys.readouterr().err


# -- l'index rejoué sous la forme du dump, pour les filtres des récupérateurs --


def test_le_flux_pseudo_xml_reprend_l_ordre_du_dump(base: Path):
    """« Article 3 MODIFIE 1955-01-21 1962-01-01 AUTONOME Décret … » : les
    filtres écrits pour le dump lisent cet ordre-là, balises ôtées."""
    import re

    db = sqlite3.connect(base)
    texte = " ".join(
        re.sub(r"<[^>]+>", " ", morceau.decode("utf-8"))
        for morceau in index.flux_pseudo_xml(db)
    )
    texte = re.sub(r"\s+", " ", texte)
    assert re.search(
        r"Article \S+ (?:VIGUEUR|MODIFIE) \d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2} AUTONOME ",
        texte), texte[:300]
    # Chaque document ouvre sur « <?xml », comme un fichier du dump.
    assert all(m.startswith(b"<?xml") for m in index.flux_pseudo_xml(db))


def test_filtrer_index_rejoue_un_filtre_ecrit_pour_le_dump(base: Path):
    filtre = r"""
import re, sys
tampon = ""
for bloc in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
    tampon += bloc.decode("utf-8", errors="replace")
    morceaux = tampon.split("<?xml")
    tampon = morceaux.pop()
    for morceau in morceaux:
        ident = re.search(r"<ID>(.*?)</ID>", morceau)
        if ident:
            print("@@@ " + ident.group(1))
"""
    sortie, source = index.filtrer_index("jorf", filtre, str(base))
    db = sqlite3.connect(base)
    attendus = {ligne[0] for ligne in db.execute("SELECT id FROM doc")}
    assert {l[4:] for l in sortie.splitlines() if l.startswith("@@@ ")} == attendus
    assert source.startswith("index JORF du dépôt")


# ---------------------------------------------------------------------------
# L'histoire d'un article (action 184). Ce que le dépôt lexifina/global-law
# fait mieux — l'article à une date, le mot à mot d'une version à l'autre —,
# repris sur l'index ; ce qu'il fait mal — dater par la seule entrée en
# vigueur —, corrigé par les clauses d'application que le texte donne.
# ---------------------------------------------------------------------------

#: L. 161-17-2 CSS en trois versions simplifiées : l'âge légal à 62 ans, à
#: 64 ans, puis la suspension de la LFSS 2026, que sa NOTA n'applique qu'aux
#: pensions prenant effet à compter du 1er septembre 2026. Identifiants fictifs.
AGE_62 = ("L'âge d'ouverture du droit à une pension de retraite est fixé à soixante-deux ans "
          "pour les assurés nés à compter du 1er janvier 1955.")
AGE_64 = AGE_62.replace("soixante-deux", "soixante-quatre").replace("1955.", "1968.")
AGE_64_SUSPENDU = AGE_64.replace("1968.", "1969.")
NOTA_2026 = ("Conformément au VI de l'article 105 de la loi n° 2025-1403 du 30 décembre 2025, "
             "ces dispositions s'appliquent aux pensions prenant effet à compter du "
             "1er septembre 2026.")
GARANTIE = ("L'assurance vieillesse garantit une pension de retraite à l'assuré qui en demande "
            "la liquidation à partir de l'âge mentionné à l'article L. 161-17-2.")
CHOMAGE = ("Les travailleurs involontairement privés d'emploi, aptes au travail et recherchant "
           "un emploi, ont droit à un revenu de remplacement.")


@pytest.fixture
def legi(tmp_path: Path) -> Path:
    def version(rang: int, titre: str, num: str, corps: str, debut: str,
                fin: str = "2999-01-01", nota: str = "") -> tuple[str, str]:
        ident = f"LEGIARTI{rang:012d}"
        cid = "LEGITEXT000006073189" if "sociale" in titre else "LEGITEXT000006072050"
        return (f"legi/global/code_en_vigueur/LEGI/ARTI/{ident}.xml",
                _article(ident, cid, "2999-01-01", "CODE", titre, num, corps, debut, fin, nota))

    css, travail = "Code de la sécurité sociale", "Code du travail"
    # Un nom sans horodatage : un dump daté ferait télécharger à
    # ``construire`` tous les incréments parus depuis. La date de l'index
    # s'écrit à part, comme la laisserait le dump du 13 juillet 2025.
    dump = _archive(tmp_path / "legi_essai.tar.gz", dict([
        version(101, css, "L161-17-2", AGE_62, "2012-01-01", "2023-09-01"),
        version(102, css, "L161-17-2", AGE_64, "2023-09-01", "2025-12-31"),
        version(103, css, "L161-17-2", AGE_64_SUSPENDU, "2025-12-31", nota=NOTA_2026),
        version(201, css, "L351-1", GARANTIE, "2004-01-01", "2011-07-01"),
        # Modifiée avant de prendre effet : jamais en vigueur (« mort-née »).
        version(202, css, "L351-1", GARANTIE.replace("161-17-2", "161-17-3"),
                "2011-07-01", "2011-07-01"),
        version(203, css, "L351-1", GARANTIE, "2011-07-01"),
        version(301, travail, "L351-1", CHOMAGE, "1984-03-23", "2008-05-01"),
    ]))
    chemin = tmp_path / "legi.sqlite"
    index.construire("legi", chemin, tout=True, archive=dump)
    with sqlite3.connect(chemin) as db:
        db.execute("UPDATE meta SET valeur = '20250713-140000' WHERE cle = 'dernier_increment'")
    return chemin


def _cli(chemin: Path, *arguments: str) -> int:
    return cherche.main(["legi", "--index", str(chemin), *arguments])


def test_l_histoire_d_un_article_se_lit_sans_requete(legi: Path, capsys):
    assert _cli(legi, "--num", "L. 161-17-2") == 0
    assert capsys.readouterr().out.splitlines() == [
        "LEGIARTI000000000101  2012-01-01 → 2023-09-01  Article CODE art. L161-17-2  "
        "Code de la sécurité sociale",
        "LEGIARTI000000000102  2023-09-01 → 2025-12-31  Article CODE art. L161-17-2  "
        "Code de la sécurité sociale",
        "LEGIARTI000000000103  2025-12-31  Article CODE art. L161-17-2  "
        "Code de la sécurité sociale",
    ]


def test_un_numero_absent_de_l_index_le_dit(legi: Path, capsys):
    assert _cli(legi, "--num", "L999-1") == 1
    assert "L999-1 n'est pas dans l'index" in capsys.readouterr().err


def test_la_limite_garde_les_versions_les_plus_recentes(legi: Path, capsys):
    assert _cli(legi, "--num", "L161-17-2", "--limite", "2") == 0
    sortie = capsys.readouterr().out
    assert "LEGIARTI000000000101" not in sortie
    assert "LEGIARTI000000000102" in sortie and "LEGIARTI000000000103" in sortie
    assert sortie.endswith("— 3 versions au total, 2 affichées (--limite)\n")


def test_le_titre_departage_deux_articles_du_meme_numero(legi: Path, capsys):
    assert _cli(legi, "--num", "L351-1") == 0
    sortie = capsys.readouterr().out
    assert sortie.index("Code de la sécurité sociale") < sortie.index("Code du travail")
    assert _cli(legi, "--num", "L351-1", "--titre", "securite sociale") == 0
    assert "Code du travail" not in capsys.readouterr().out
    db = sqlite3.connect(legi)
    assert cherche.chercher(db, "remplacement", _options(titre="TRAVAIL"))[1] == 1
    assert cherche.chercher(db, "remplacement", _options(titre="sécurité"))[1] == 0


def test_la_difference_se_lit_mot_a_mot():
    assert cherche.difference(AGE_62, AGE_64) == (
        "… pension de retraite est fixé à [-soixante-deux-]{+soixante-quatre+} ans pour les "
        "assurés nés à compter du 1er janvier [-1955.-]{+1968.+}")
    assert cherche.difference(AGE_64, AGE_64) == ""


def test_la_difference_ignore_le_balisage_d_un_ordinal():
    """« 1<sup>er</sup> » devient « 1 er » dans l'index, quand une version
    antérieure écrivait « 1er » : vu sur L. 161-17-2 le 31 décembre 2025, ce
    n'est pas un changement du texte."""
    assert cherche.difference("à compter du 1er janvier 1969.",
                              "à compter du 1 er janvier 1969.") == ""
    assert cherche.difference("la 1re catégorie", "la 1 re catégorie") == ""


def test_diff_montre_chaque_version_contre_la_precedente(legi: Path, capsys):
    assert _cli(legi, "--num", "L161-17-2", "--diff") == 0
    lignes = capsys.readouterr().out.splitlines()
    assert len(lignes) == 5
    assert lignes[0].startswith("LEGIARTI000000000101  2012-01-01")
    assert lignes[1].startswith("LEGIARTI000000000102")
    assert lignes[2] == "    " + cherche.difference(AGE_62, AGE_64)
    assert lignes[3].startswith("LEGIARTI000000000103")
    assert lignes[4].startswith("    {+Conformément au VI de l'article 105")
    assert lignes[4].endswith("[-1968.-]{+1969.+}")


def test_diff_dit_un_texte_inchange_et_passe_une_version_jamais_en_vigueur(legi: Path, capsys):
    """Une rédaction « sans effet » se prouve par son mot à mot
    (docs/veille_droit.md, étape 4) : ici, il est vide. Une version mort-née
    se compare à la précédente, mais la suivante se compare à la dernière qui
    a été en vigueur."""
    assert _cli(legi, "--num", "L351-1", "--titre", "sécurité sociale", "--diff") == 0
    lignes = capsys.readouterr().out.splitlines()
    assert lignes[1].startswith("LEGIARTI000000000202")
    assert lignes[1].endswith("(jamais en vigueur)")
    assert lignes[2] == "    … de l'âge mentionné à l'article L. [-161-17-2.-]{+161-17-3.+}"
    assert lignes[3].startswith("LEGIARTI000000000203")
    assert lignes[4] == "    (texte inchangé)"


def test_le_rend_la_version_en_vigueur_ce_jour_la_et_ses_dates_d_application(legi: Path, capsys):
    """La version en vigueur un jour n'est pas toujours celle qu'on applique à
    une pension prenant effet ce jour-là : la NOTA le dit, et l'outil la met
    sous les yeux, avec la version précédente."""
    assert _cli(legi, "--num", "L161-17-2", "--le", "2026-03-01") == 0
    sortie = capsys.readouterr().out
    assert sortie.startswith("LEGIARTI000000000103  2025-12-31  Article CODE")
    assert AGE_64_SUSPENDU in sortie
    assert "précédente : LEGIARTI000000000102  2023-09-01 → 2025-12-31" in sortie
    assert f"    « {NOTA_2026} »" in sortie
    assert "LEGIARTI000000000101" not in sortie


def test_le_compte_la_fin_d_une_version_comme_legi(legi: Path, capsys):
    """DATE_FIN est le premier jour de la version suivante."""
    assert _cli(legi, "--num", "L161-17-2", "--le", "2025-12-30") == 0
    sortie = capsys.readouterr().out
    assert sortie.startswith("LEGIARTI000000000102") and "s'appliquent" not in sortie
    assert _cli(legi, "--num", "L161-17-2", "--le", "2025-12-31") == 0
    assert capsys.readouterr().out.startswith("LEGIARTI000000000103")


def test_le_avant_la_premiere_version_le_dit(legi: Path, capsys):
    assert _cli(legi, "--num", "L161-17-2", "--le", "1990-01-01") == 1
    assert "la première commence le 2012-01-01" in capsys.readouterr().err


def test_le_au_dela_de_l_index_previent(legi: Path, capsys):
    assert _cli(legi, "--num", "L161-17-2", "--le", "2026-03-01") == 0
    assert "l'index s'arrête au 2025-07-13" in capsys.readouterr().err


def test_les_clauses_d_application_se_relevent_et_pas_le_reste():
    assert cherche.clauses_d_application(f"{NOTA_2026} {AGE_64_SUSPENDU}") == [NOTA_2026]
    assert cherche.clauses_d_application(AGE_64_SUSPENDU) == []
    assert cherche.clauses_d_application(
        "Ces dispositions sont applicables aux pensions de retraite prenant effet à compter "
        "du 1 er janvier 2026. Le décret entre en vigueur le 1er septembre 2023. Il est "
        "fixé à l'article L. 351-1.") == [
        "Ces dispositions sont applicables aux pensions de retraite prenant effet à compter "
        "du 1 er janvier 2026.",
        "Le décret entre en vigueur le 1er septembre 2023."]


def test_motif_suit_une_expression_de_version_en_version(legi: Path, capsys):
    assert _cli(legi, "--num", "L161-17-2", "--motif", "1955", "--autour", "12") == 0
    sortie = capsys.readouterr().out
    assert "…1er janvier 1955.…" in sortie
    assert sortie.count("    (absent)") == 2


def test_chaque_reponse_dit_la_fraicheur_de_l_index(legi: Path, capsys):
    """Une certification est vraie à une date (docs/archives/veille_droit.md) :
    la réponse dit jusqu'où va l'index, et comment le rattraper."""
    assert _cli(legi, "--num", "L161-17-2") == 0
    erreur = capsys.readouterr().err
    assert "index LEGI à jour au 2025-07-13" in erreur
    assert "python scripts/fetch/dila_index.py legi --mettre-a-jour" in erreur
    assert _cli(legi, "pension") == 0
    assert "index LEGI à jour au 2025-07-13" in capsys.readouterr().err


@pytest.mark.parametrize("arguments", [
    ["--diff"], ["--le", "2026-03-01"], ["pension", "--num", "L351-1", "--diff"],
    ["--num", "L351-1", "--le", "1er mars 2026"]])
def test_diff_et_le_suivent_un_article(legi: Path, arguments: list[str]):
    with pytest.raises(SystemExit):
        _cli(legi, *arguments)


def _plan(chemin: Path, requete: str, *valeurs: str) -> str:
    """Comment SQLite compte s'y prendre : un parcours de la table (``SCAN``),
    ou une recherche par un index (``SEARCH … USING INDEX``)."""
    with sqlite3.connect(chemin) as db:
        return " | ".join(ligne[3] for ligne in db.execute("EXPLAIN QUERY PLAN " + requete, valeurs))


def test_un_article_de_legi_se_trouve_sans_parcourir_la_table(legi: Path, tmp_path: Path,
                                                             monkeypatch):
    """``scripts/textes.py`` lit LEGI article par article, par le titre du
    texte et le numéro : un index SQL y mène, sans parcourir la table, ce qui
    coûtait plus de quatre minutes à l'inscription des rédactions. L'index
    construit le porte ; celui que la release sert sans lui le prend quand une
    session le récupère (action 184)."""
    import gzip
    import shutil
    css = "Code de la sécurité sociale"
    un_article = "SELECT id, date, fin FROM doc WHERE titre = ? AND num = ? ORDER BY date, id"
    un_texte = "SELECT id, num, date, fin FROM doc WHERE titre = ? AND id LIKE 'LEGIARTI%'"
    for requete, valeurs in ((un_article, (css, "L351-1")), (un_texte, (css,))):
        assert "SEARCH doc USING INDEX" in _plan(legi, requete, *valeurs), requete

    with sqlite3.connect(legi) as db:   # tel que publié jusqu'au 9 novembre 2026
        db.execute("DROP INDEX doc_titre_num")
    assert _plan(legi, un_article, css, "L351-1").startswith("SCAN doc")
    publie = tmp_path / "legi.sqlite.gz"
    with legi.open("rb") as source, gzip.open(publie, "wb") as cible:
        shutil.copyfileobj(source, cible)
    monkeypatch.setattr(index, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(index, "url_publiee", lambda base: publie.as_uri())
    recu = tmp_path / "recu" / "legi.sqlite"
    index.recuperer("legi", recu)
    assert "SEARCH doc USING INDEX" in _plan(recu, un_article, css, "L351-1")
