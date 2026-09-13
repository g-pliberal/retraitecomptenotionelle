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
             num: str, corps: str, debut: str = "2999-01-01", fin: str = "2999-01-01") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ARTICLE>
<META><META_COMMUN><ID>{ident}</ID><NATURE>Article</NATURE></META_COMMUN>
<META_SPEC><META_ARTICLE><NUM>{num}</NUM><DATE_DEBUT>{debut}</DATE_DEBUT><DATE_FIN>{fin}</DATE_FIN></META_ARTICLE></META_SPEC></META>
<CONTEXTE>
<TEXTE autorite="" cid="{cid}" date_publi="{date_publi}" date_signature="{date_publi}" ministere="" nature="{nature}" nor="">
<TITRE_TXT debut="1952-07-01" fin="2999-01-01" id_txt="{cid}">{titre_txt}</TITRE_TXT>
</TEXTE></CONTEXTE>
<BLOC_TEXTUEL><CONTENU><br/>   {corps}<br/></CONTENU></BLOC_TEXTUEL>
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
    defauts = dict(depuis=None, jusqu=None, nature=None, num=None, limite=20,
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
