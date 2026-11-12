"""KALI, la base des conventions collectives de la DILA, dans l'index
(``scripts/fetch/dila_index.py kali``, ``dila_cherche.py kali`` ; action 184,
étape 5).

Aucun de ces tests n'accède au réseau. Le dump de poche reprend la forme et
les valeurs de fichiers lus dans ``Freemium_kali_global_20261108-140000`` :
l'article 92 de l'accord national interprofessionnel du 17 novembre 2017
(``KALIARTI000036731850``), les trois rédactions de l'article 1er de l'accord
du 10 mai 2019 sur la valeur de service du point, et un article d'un avenant
de salaires de la convention des coopératives de consommateurs (IDCC 3205).
Le « jumeau » est inventé : un second texte qui porte le titre du premier,
comme 1 543 titres de la base en couvrent plusieurs.
"""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
import shutil
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

ANI_2017 = ("Accord national interprofessionnel du 17 novembre 2017 relatif au régime "
            "AGIRC-ARRCO de retraite complémentaire")
ANI_2019 = ("Accord national interprofessionnel du 10 mai 2019 relatif au régime "
            "AGIRC-ARRCO de retraite complémentaire")
COOPERATIVES = ("Convention collective nationale des coopératives de consommateurs salariés "
                "du 23 novembre 2018 (21e édition) - Etendue par arrêté du 21 mai 2021 JORF "
                "12 juin 2021")


def _article(ident: str, num: str, etat: str, debut: str, fin: str, cid: str,
             nature: str, titre_txt: str, corps: str, conteneur: str,
             idcc: str = "", titre: str = "") -> str:
    """Un article de KALI, tel que le dump le donne : son état, le texte qui
    le porte (``TEXTE``), la convention où il se range (``CONTENEUR``)."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ARTICLE>
<META>
<META_COMMUN>
<ID>{ident}</ID>
<ORIGINE>KALI</ORIGINE>
<NATURE>Article</NATURE>
</META_COMMUN>
<META_SPEC>
<META_ARTICLE>
<NUM>{num}</NUM>
<TITRE>{titre}</TITRE>
<ETAT>{etat}</ETAT>
<DATE_DEBUT>{debut}</DATE_DEBUT>
<DATE_FIN>{fin}</DATE_FIN>
<DATE_DEB_EXT>2999-01-01</DATE_DEB_EXT>
<DATE_FIN_EXT>2999-01-01</DATE_FIN_EXT>
<TYPE>AUTONOME</TYPE>
</META_ARTICLE>
</META_SPEC>
</META>
<CONTEXTE>
<TEXTE cid="{cid}" date_publi="2999-01-01" date_signature="2017-11-17" nature="{nature}" nor="" num="" num_parution_jo="">
<TITRE_TXT c_titre_court="Régime" debut="{debut}" fin="2999-01-01" id_txt="{cid}">{titre_txt}</TITRE_TXT>
</TEXTE>
<CONTENEUR cid="KALICONT000046709421" date_publi="2019-01-01" etat="{etat}" nature="{'IDCC' if idcc else 'TI'}" num="{idcc}" titre="{conteneur}" url="conteneur/KALI/CONT/x.xml"/>
</CONTEXTE>
<BLOC_TEXTUEL>
<CONTENU>
<p align="left">{corps}</p>
</CONTENU>
</BLOC_TEXTUEL>
</ARTICLE>
"""


def _texte(ident: str, nature: str, titre: str, etat: str, debut: str, fin: str) -> str:
    """Un texte de KALI : son titre et ses signataires, sans corps — le corps
    est dans ses articles."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TEXTE_VERSION>
<META>
<META_COMMUN>
<ID>{ident}</ID>
<ORIGINE>KALI</ORIGINE>
<NATURE>{nature}</NATURE>
</META_COMMUN>
<META_SPEC>
<META_TEXTE_CHRONICLE>
<CID>{ident}</CID>
<DATE_PUBLI>2999-01-01</DATE_PUBLI>
<DATE_TEXTE>2019-05-10</DATE_TEXTE>
</META_TEXTE_CHRONICLE>
<META_TEXTE_VERSION>
<TITRE>Régime AGIRC-ARRCO ANI du 10 mai 2019</TITRE>
<TITREFULL>{titre}</TITREFULL>
<ETAT>{etat}</ETAT>
<DATE_DEBUT>{debut}</DATE_DEBUT>
<DATE_FIN>{fin}</DATE_FIN>
</META_TEXTE_VERSION>
</META_SPEC>
</META>
<SIGNATAIRES>
<SIGNPATRON><CONTENU><p>CPME ;</p><p>MEDEF ;</p><p>U2P,</p></CONTENU></SIGNPATRON>
</SIGNATAIRES>
</TEXTE_VERSION>
"""


ARTICLE_92 = _article(
    "KALIARTI000036731850", "92", "VIGUEUR_ETEN", "2019-01-01", "2999-01-01",
    "KALITEXT000036731682", "Accord national interprofessionnel", ANI_2017,
    "L'allocation est calculée en multipliant le nombre de points inscrits au compte du "
    "participant, à la date de la liquidation de ses droits, par la valeur de service du "
    "point de retraite du régime, sous réserve des dispositions des articles 84 et 85.",
    ANI_2017, titre="Calcul de l'allocation")

FIXEE = "La valeur de service du point a été fixée au 1er novembre 2018 à 1,2588 €."
PERIODE = ("Durant la période couverte par le présent accord (2019, 2020, 2021 et 2022), la "
           "valeur de service du point évolue au 1er novembre de chaque année comme le "
           "salaire annuel moyen des ressortissants du régime.")
EXERCICES = ("Pour les exercices 2019 et 2020, la valeur de service du point évolue au 1er "
             "novembre de chaque année comme le salaire annuel moyen des ressortissants du "
             "régime.")
RESERVES = ("dans le respect du maintien d'un niveau de réserves techniques au moins égal à "
            "6 mois de prestations dans la période courant jusqu'à fin 2033.")


def _premier(ident: str, etat: str, debut: str, fin: str, corps: str,
             cid: str = "KALITEXT000039097685") -> str:
    return _article(ident, "1er", etat, debut, fin, cid, "Accord", ANI_2019, corps, ANI_2019,
                    titre="Valeur de service du point")


PREMIER_2019 = _premier("KALIARTI000039097693", "REMPLACE", "2019-01-01", "2021-10-13",
                        f"{FIXEE} {PERIODE}")
PREMIER_2021 = _premier("KALIARTI000047193923", "REMPLACE", "2021-10-13", "2022-10-25",
                        f"{FIXEE} {EXERCICES}")
PREMIER_2022 = _premier("KALIARTI000047194783", "PERIME", "2022-10-25", "2022-12-31",
                        f"{FIXEE} {EXERCICES} {RESERVES}")
JUMEAU = _premier("KALIARTI000099999901", "VIGUEUR", "2020-01-01", "2999-01-01",
                  "Le présent texte porte le titre d'un autre.", cid="KALITEXT000099999900")
ACCORD_2019 = _texte("KALITEXT000039097685", "Accord", ANI_2019, "PERIME",
                     "2019-01-01", "2022-12-31")
SALAIRES = _article(
    "KALIARTI000054872351", "2", "VIGUEUR_ETEN", "2026-05-01", "2999-01-01",
    "KALITEXT000054872346", "Avenant",
    "Avenant n° 933 du 16 avril 2026 relatif aux salaires minima au 1er mai 2026",
    "Les parties signataires du présent avenant conviennent des modalités suivantes de "
    "revalorisation des salaires minima.", COOPERATIVES, idcc="3205",
    titre="Revalorisation des salaires minima")
#: Hors du champ de ``THEMATIQUE`` : ni son titre ni son texte n'en porte un mot.
CONGES = _article(
    "KALIARTI000099999902", "12", "VIGUEUR_NON_ETEN", "2020-01-01", "2999-01-01",
    "KALITEXT000099999903", "Accord", "Accord du 3 mars 2020 relatif aux congés",
    "Les congés sont pris en accord avec l'employeur.", COOPERATIVES, idcc="3205")
STRUCTURE = ('<?xml version="1.0" encoding="UTF-8"?>\n<TEXTEKALI><META><META_COMMUN>'
             "<ID>KALITEXT000039097685</ID></META_COMMUN></META></TEXTEKALI>\n")

FICHIERS = {
    "kali/global/article/KALI/ARTI/00/00/36/73/18/KALIARTI000036731850.xml": ARTICLE_92,
    "kali/global/article/KALI/ARTI/00/00/39/09/76/KALIARTI000039097693.xml": PREMIER_2019,
    "kali/global/article/KALI/ARTI/00/00/47/19/39/KALIARTI000047193923.xml": PREMIER_2021,
    "kali/global/article/KALI/ARTI/00/00/47/19/47/KALIARTI000047194783.xml": PREMIER_2022,
    "kali/global/article/KALI/ARTI/00/00/99/99/99/KALIARTI000099999901.xml": JUMEAU,
    "kali/global/article/KALI/ARTI/00/00/54/87/23/KALIARTI000054872351.xml": SALAIRES,
    "kali/global/article/KALI/ARTI/00/00/99/99/99/KALIARTI000099999902.xml": CONGES,
    "kali/global/texte/version/KALI/TEXT/00/00/39/09/76/KALITEXT000039097685.xml": ACCORD_2019,
    "kali/global/texte/struct/KALI/TEXT/00/00/39/09/76/KALITEXT000039097685.xml": STRUCTURE,
}


def _archive(chemin: Path, fichiers: dict[str, str]) -> Path:
    with tarfile.open(chemin, "w:gz") as flux:
        for nom, contenu in fichiers.items():
            octets = contenu.encode("utf-8")
            membre = tarfile.TarInfo(nom)
            membre.size = len(octets)
            flux.addfile(membre, io.BytesIO(octets))
    return chemin


@pytest.fixture
def kali(tmp_path: Path) -> Path:
    # Un nom sans horodatage : un dump daté ferait chercher à ``construire``
    # les incréments parus depuis.
    chemin = tmp_path / "kali.sqlite"
    index.construire("kali", chemin, archive=_archive(tmp_path / "kali_essai.tar.gz", FICHIERS))
    with sqlite3.connect(chemin) as db:
        db.execute("UPDATE meta SET valeur = '20261110-213159' WHERE cle = 'dernier_increment'")
    return chemin


def _ligne(chemin: Path, ident: str, colonnes: str) -> tuple:
    with sqlite3.connect(chemin) as db:
        return db.execute(f"SELECT {colonnes} FROM doc WHERE id = ?", (ident,)).fetchone()


def _ids(chemin: Path) -> set[str]:
    with sqlite3.connect(chemin) as db:
        return {ligne[0] for ligne in db.execute("SELECT id FROM doc")}


# ---------------------------------------------------------------------------
# Lire KALI
# ---------------------------------------------------------------------------

def test_lire_un_article_de_kali_avec_son_etat_son_texte_et_sa_convention():
    doc = index.lire(ARTICLE_92)
    assert (doc.id, doc.date, doc.fin, doc.num) == (
        "KALIARTI000036731850", "2019-01-01", "2999-01-01", "92")
    assert doc.nature == "Article Accord national interprofessionnel"
    assert doc.titre == ANI_2017
    assert doc.texte.startswith("L'allocation est calculée en multipliant le nombre de points")
    assert (doc.etat, doc.cid, doc.idcc, doc.convention) == (
        "VIGUEUR_ETEN", "KALITEXT000036731682", "", ANI_2017)

    salaires = index.lire(SALAIRES)
    assert (salaires.etat, salaires.cid, salaires.idcc, salaires.convention) == (
        "VIGUEUR_ETEN", "KALITEXT000054872346", "3205", COOPERATIVES)


def test_lire_un_texte_de_kali_date_de_sa_validite():
    """``DATE_PUBLI`` vaut 2999-01-01 dans KALI : c'est la validité qui date."""
    doc = index.lire(ACCORD_2019)
    assert (doc.id, doc.date, doc.fin, doc.nature, doc.num, doc.titre) == (
        "KALITEXT000039097685", "2019-01-01", "2022-12-31", "Accord", "", ANI_2019)
    assert (doc.etat, doc.cid, doc.idcc, doc.convention) == (
        "PERIME", "KALITEXT000039097685", "", "")


def test_un_document_des_autres_bases_ne_porte_rien_de_plus():
    doc = index.Document("LEGIARTI000000000004", "1972-01-01", "2014-01-01", "Article CODE",
                         "R351-9", "Code de la sécurité sociale", "Le trimestre est validé.")
    assert (doc.etat, doc.cid, doc.idcc, doc.convention) == ("", "", "", "")


# ---------------------------------------------------------------------------
# Construire, mettre à jour, récupérer, publier
# ---------------------------------------------------------------------------

def test_construire_garde_kali_entiere_sans_qu_on_le_demande(kali: Path):
    """Entière, la base pèse moins que LEGI filtré (276 Mo publiés contre 455) :
    rien ne s'y écarte, et ne rien y trouver dit que KALI ne l'a pas."""
    assert "KALIARTI000099999902" in _ids(kali)          # les congés, hors du champ social
    assert len(_ids(kali)) == 8                          # sept articles et un texte
    with sqlite3.connect(kali) as db:
        assert index.meta(db, "filtre") == "tout" and index.meta(db, "base") == "kali"


def test_l_index_de_kali_garde_l_etat_le_texte_et_la_convention(kali: Path):
    assert _ligne(kali, "KALIARTI000054872351", "etat, cid, idcc, convention") == (
        "VIGUEUR_ETEN", "KALITEXT000054872346", "3205", COOPERATIVES)
    assert _ligne(kali, "KALITEXT000039097685", "etat, cid, idcc") == (
        "PERIME", "KALITEXT000039097685", "")


def test_les_index_du_jorf_et_de_legi_gardent_leurs_sept_colonnes(tmp_path: Path):
    """Ceux que la release sert n'en ont pas d'autres : rien n'y change."""
    with index.ouvrir(tmp_path / "legi.sqlite", "legi") as db:
        assert index.colonnes(db) == ["id", "date", "fin", "nature", "num", "titre", "texte"]


def test_un_increment_de_kali_remplace_et_supprime(tmp_path: Path, kali: Path):
    abroge = PREMIER_2022.replace("<ETAT>PERIME</ETAT>", "<ETAT>ABROGE</ETAT>")
    increment = _archive(tmp_path / "KALI_20261111-213000.tar.gz", {
        "20261111-213000/kali/global/article/KALI/ARTI/00/00/47/19/47/KALIARTI000047194783.xml":
            abroge,
        "20261111-213000/kali/global/liste_suppression_kali.dat":
            "kali/global/article/KALI/ARTI/00/00/99/99/99/KALIARTI000099999901.xml\n",
    })
    db = index.ouvrir(kali, "kali")
    assert index.verser_archive(db, increment, tout=True, remplacer=True) == (1, 1)
    db.commit()
    db.close()
    assert "KALIARTI000099999901" not in _ids(kali) and len(_ids(kali)) == 7
    assert _ligne(kali, "KALIARTI000047194783", "etat, cid") == (
        "ABROGE", "KALITEXT000039097685")


@pytest.fixture
def dila(tmp_path: Path, monkeypatch):
    """Le serveur de la DILA, remplacé par un répertoire : ce qu'il liste, et
    ce qu'on y télécharge."""
    servi = tmp_path / "dila"
    servi.mkdir()
    monkeypatch.setattr(index, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(index, "_listing",
                        lambda base: sorted(p.name for p in servi.glob("*.tar.gz")))

    def telecharger(url: str, cible: Path) -> Path:
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(servi / url.rsplit("/", 1)[-1], cible)
        return cible

    monkeypatch.setattr(index, "telecharger", telecharger)
    return servi


def _sans(*idents: str) -> dict[str, str]:
    return {nom: xml for nom, xml in FICHIERS.items() if not any(i in nom for i in idents)}


def test_mettre_a_jour_applique_les_increments_parus(tmp_path: Path, dila: Path):
    _archive(dila / "Freemium_kali_global_20261108-140000.tar.gz", _sans("KALIARTI000054872351"))
    chemin = tmp_path / "kali.sqlite"
    index.construire("kali", chemin)
    assert "KALIARTI000054872351" not in _ids(chemin)
    _archive(dila / "KALI_20261109-212854.tar.gz", {
        "20261109-212854/kali/global/article/KALI/ARTI/00/00/54/87/23/KALIARTI000054872351.xml":
            SALAIRES})
    assert index.mettre_a_jour("kali", chemin) == 1
    assert "KALIARTI000054872351" in _ids(chemin)
    with sqlite3.connect(chemin) as db:
        assert index.meta(db, "dernier_increment") == "20261109-212854"
        assert index.meta(db, "dump") == "Freemium_kali_global_20261108-140000.tar.gz"


def test_mettre_a_jour_reconstruit_kali_quand_la_dila_renouvelle_le_dump(
        tmp_path: Path, dila: Path, capsys):
    """La DILA a refait ses dumps le 8 novembre 2026 et retiré les incréments
    d'avant : un index arrêté plus tôt ne peut plus rattraper ce qui a paru
    entre son dernier incrément et le dump neuf. KALI se reconstruit alors, en
    quelques minutes, plutôt que de garder un trou sans le dire."""
    ancien = _archive(dila / "Freemium_kali_global_20261101-140000.tar.gz",
                      _sans("KALIARTI000054872351", "KALIARTI000099999902"))
    chemin = tmp_path / "kali.sqlite"
    index.construire("kali", chemin)
    ancien.unlink()
    # Le dump neuf porte ce que les incréments retirés avaient apporté.
    _archive(dila / "Freemium_kali_global_20261108-140000.tar.gz", _sans("KALIARTI000099999902"))
    _archive(dila / "KALI_20261109-212854.tar.gz", {
        "20261109-212854/kali/global/article/KALI/ARTI/00/00/99/99/99/KALIARTI000099999902.xml":
            CONGES})
    index.mettre_a_jour("kali", chemin)
    assert _ids(chemin) >= {"KALIARTI000054872351", "KALIARTI000099999902"}
    with sqlite3.connect(chemin) as db:
        assert index.meta(db, "dump") == "Freemium_kali_global_20261108-140000.tar.gz"
        assert index.meta(db, "dernier_increment") == "20261109-212854"
    assert "dump renouvelé" in capsys.readouterr().err


def test_recuperer_et_publier_kali(tmp_path: Path, kali: Path, monkeypatch, capsys):
    """``--publier`` dépose ``kali.sqlite.gz`` sur la release et dit qu'aucun
    filtre ne l'a réduite ; ``--recuperer`` la rend telle quelle."""
    appels: list[tuple[str, str]] = []
    publie = tmp_path / "publie.gz"

    def github(methode, url, jeton, donnees=None, type_contenu="", longueur=None):
        appels.append((methode, url))
        if methode == "GET":
            # Les trois bases publient en même temps : entre la première
            # lecture de la release et la fin de l'envoi, LEGI a écrit sa ligne.
            lectures = sum(1 for appel in appels if appel[0] == "GET")
            return {"assets": [], "upload_url": "https://envoi/assets{?name,label}",
                    "url": "https://api/release",
                    "body": "" if lectures == 1 else "\n- `legi.sqlite.gz` : à jour au 16."}
        if methode == "POST":
            publie.write_bytes(donnees.read())
            return {"browser_download_url": "https://github/kali.sqlite.gz"}
        appels.append(("corps", donnees.decode()))
        return {}

    (tmp_path / "cache").mkdir()
    monkeypatch.setattr(index, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(index, "_github", github)
    monkeypatch.setenv("GH_TOKEN", "jeton")
    assert index.main(["kali", "--index", str(kali), "--publier"]) == 0
    assert ("POST", "https://envoi/assets?name=kali.sqlite.gz") in appels
    corps = json.loads(dict(a for a in appels if a[0] == "corps")["corps"])["body"]
    assert "`kali.sqlite.gz` : 8 documents" in corps and "filtre aucun" in corps
    assert "`legi.sqlite.gz` : à jour au 16." in corps      # la ligne de LEGI n'est pas écrasée

    monkeypatch.setattr(index, "url_publiee", lambda base: publie.as_uri())
    recu = tmp_path / "recu" / "kali.sqlite"
    assert index.main(["kali", "--index", str(recu), "--recuperer"]) == 0
    assert _ids(recu) == _ids(kali)
    assert _ligne(recu, "KALIARTI000036731850", "cid") == ("KALITEXT000036731682",)


def test_le_workflow_publie_kali_chaque_lundi_comme_les_autres_bases():
    """``index-dila.yml`` : une course par base de ``BASES``, et les étapes
    qui construisent et publient l'index ne trient pas entre elles."""
    import yaml

    flux = yaml.safe_load((Path(__file__).resolve().parents[1] / ".github" / "workflows"
                           / "index-dila.yml").read_text(encoding="utf-8"))
    travail = flux["jobs"]["index"]
    assert sorted(travail["strategy"]["matrix"]["base"]) == sorted(index.BASES)
    # PyYAML lit la clé `on` comme le booléen vrai.
    assert flux[True]["schedule"] == [{"cron": "0 4 * * 1"}]
    for commande in ("--recuperer", "--mettre-a-jour", "--publier"):
        etape = next(e for e in travail["steps"] if commande in e.get("run", ""))
        assert "if" not in etape, commande
        assert f"dila_index.py ${{{{ matrix.base }}}} {commande}" in etape["run"]


# ---------------------------------------------------------------------------
# Chercher dans KALI
# ---------------------------------------------------------------------------

def _cli(chemin: Path, *arguments: str) -> int:
    return cherche.main(["kali", "--index", str(chemin), *arguments])


def test_une_recherche_dit_l_etat_et_le_texte_de_chaque_article(kali: Path, capsys):
    assert _cli(kali, "allocation points") == 0
    assert capsys.readouterr().out.splitlines()[0] == (
        "KALIARTI000036731850  2019-01-01  Article Accord national interprofessionnel "
        f"art. 92  {ANI_2017[:110]}  (en vigueur étendu ; dans KALITEXT000036731682)")
    assert _cli(kali, "salaires minima") == 0
    assert capsys.readouterr().out.splitlines()[0].endswith(
        "(en vigueur étendu ; IDCC 3205 ; dans KALITEXT000054872346)")
    assert _cli(kali, "MEDEF") == 0          # un texte, trouvé par ses signataires
    assert capsys.readouterr().out.splitlines()[0] == (
        f"KALITEXT000039097685  2019-01-01 → 2022-12-31  Accord  {ANI_2019}  (périmé)")


def test_une_recherche_se_borne_a_un_texte_ou_a_une_convention(kali: Path, capsys):
    assert _cli(kali, "valeur de service", "--compter") == 0
    assert capsys.readouterr().out.strip() == "— 4 documents au total"
    assert _cli(kali, "valeur de service", "--dans", "KALITEXT000039097685", "--compter") == 0
    assert capsys.readouterr().out.strip() == "— 3 documents au total"
    assert _cli(kali, "employeur OR salaires", "--idcc", "3205", "--compter") == 0
    assert capsys.readouterr().out.strip() == "— 2 documents au total"


def test_une_convention_se_designe_par_un_de_ses_numeros(tmp_path: Path, capsys):
    """Le bâtiment de la région parisienne se range sous trois numéros à la
    fois : ``num="1740 1841 1843"`` dans le dump."""
    batiment = _article(
        "KALIARTI000099999904", "3", "VIGUEUR_ETEN", "2020-01-01", "2999-01-01",
        "KALITEXT000099999905", "Accord", "Accord du 3 mars 2020 relatif aux congés",
        "Les congés sont pris en accord avec l'employeur.",
        "Convention collective régionale du bâtiment de la région parisienne",
        idcc="1740 1841 1843")
    chemin = tmp_path / "kali.sqlite"
    index.construire("kali", chemin, archive=_archive(
        tmp_path / "kali_essai.tar.gz", {"kali/global/article/a.xml": batiment,
                                         "kali/global/article/b.xml": CONGES}))
    for numero, attendu in (("1841", 1), ("01740", 1), ("184", 0), ("3205", 1)):
        assert _cli(chemin, "congés", "--idcc", numero, "--compter") == 0
        assert capsys.readouterr().out.strip() == f"— {attendu} documents au total", numero


def test_un_numero_seul_ne_designe_pas_un_article_de_kali(kali: Path, capsys):
    """« Article 1er » : 24 917 textes de la base en ont un."""
    with pytest.raises(SystemExit):
        _cli(kali, "--num", "1er")
    assert "--dans" in capsys.readouterr().err


def test_l_histoire_d_un_article_de_kali_se_lit_dans_son_texte(kali: Path, capsys):
    """Par l'identifiant du texte, non par son titre, qu'un autre porte aussi."""
    assert _cli(kali, "--num", "1er", "--dans", "KALITEXT000039097685") == 0
    assert capsys.readouterr().out.splitlines() == [
        f"KALIARTI000039097693  2019-01-01 → 2021-10-13  Article Accord art. 1er  {ANI_2019}"
        "  (remplacé ; dans KALITEXT000039097685)",
        f"KALIARTI000047193923  2021-10-13 → 2022-10-25  Article Accord art. 1er  {ANI_2019}"
        "  (remplacé ; dans KALITEXT000039097685)",
        f"KALIARTI000047194783  2022-10-25 → 2022-12-31  Article Accord art. 1er  {ANI_2019}"
        "  (périmé ; dans KALITEXT000039097685)",
    ]


def test_le_titre_seul_ne_mele_pas_deux_textes_de_kali(kali: Path, capsys):
    """Deux textes du même titre : chacun son histoire, et le mot à mot ne
    compare pas l'article de l'un à celui de l'autre."""
    assert _cli(kali, "--num", "1er", "--titre", "10 mai 2019", "--diff") == 0
    lignes = capsys.readouterr().out.splitlines()
    assert [ligne[:20] for ligne in lignes if ligne.startswith("KALIARTI")] == [
        "KALIARTI000039097693", "KALIARTI000047193923", "KALIARTI000047194783",
        "KALIARTI000099999901"]
    # La rédaction de 2021 contre celle de 2019, du même texte.
    assert "€. [-Durant la période couverte par le présent accord (2019," in lignes[2]
    assert "{+Pour les exercices 2019 et+} 2020," in lignes[2]
    assert lignes[-1].startswith("KALIARTI000099999901")     # la première du jumeau : rien à comparer


def test_la_version_d_un_article_de_kali_a_une_date(kali: Path, capsys):
    assert _cli(kali, "--num", "1er", "--dans", "KALITEXT000039097685",
                "--le", "2022-11-01", "--motif", "réserves", "--autour", "20") == 0
    sortie = capsys.readouterr().out.splitlines()
    assert sortie[0].startswith("KALIARTI000047194783  2022-10-25 → 2022-12-31")
    assert "réserves techniques" in sortie[1]
    assert sortie[2] == "précédente : KALIARTI000047193923  2021-10-13 → 2022-10-25"


def test_le_texte_d_un_article_de_kali_dit_sa_convention(kali: Path, capsys):
    assert _cli(kali, "--texte", "KALIARTI000054872351") == 0
    sortie = capsys.readouterr().out.splitlines()
    assert sortie[0] == "KALIARTI000054872351  2026-05-01 → 2999-01-01  Article Avenant art. 2"
    assert sortie[1] == "Avenant n° 933 du 16 avril 2026 relatif aux salaires minima au 1er mai 2026"
    assert sortie[2] == f"en vigueur étendu ; IDCC 3205 ; dans KALITEXT000054872346 ; {COOPERATIVES}"


def test_dans_et_idcc_ne_valent_que_pour_kali(tmp_path: Path, capsys):
    legi = tmp_path / "legi.sqlite"
    index.ouvrir(legi, "legi").close()
    for filtre in (["--dans", "LEGITEXT000006073189"], ["--idcc", "3205"]):
        with pytest.raises(SystemExit):
            cherche.main(["legi", "--index", str(legi), "retraite", *filtre])
        assert "KALI" in capsys.readouterr().err


def test_l_histoire_d_un_article_de_kali_se_trouve_sans_parcourir_la_table(kali: Path):
    with sqlite3.connect(kali) as db:
        plan = " | ".join(ligne[3] for ligne in db.execute(
            "EXPLAIN QUERY PLAN SELECT id, date, fin FROM doc WHERE cid = ? ORDER BY date, id",
            ("KALITEXT000039097685",)))
    assert "SEARCH doc USING INDEX" in plan
