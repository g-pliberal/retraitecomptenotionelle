"""Une source qui refuse la session se déclare, et son document s'apporte.

`data/sources.yaml` porte un champ `blocage` sur chaque jeu qu'une session ne
peut pas atteindre ; `scripts/fetch/source_locale.py` en imprime la liste et
donne aux récupérateurs le moyen de lire un document déposé dans `data/brut/`
au lieu de le télécharger. Ces tests tiennent les deux ensemble : les valeurs
du champ sont celles que le module connaît, et le module lit bien le fichier
avant de sortir.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
FETCH = RACINE / "scripts" / "fetch"

#: Les récupérateurs qui lisent un document servi par un site — PDF, classeur —
#: et doivent donc pouvoir le lire depuis `data/brut/` quand le site refuse.
LECTEURS_DE_DOCUMENTS = (
    "agirc_arrco_valeurs_point.py",
    "erafp_valeurs_point.py",
    "cnav_revalorisation_salaires.py",
    "cnbf_baremes.py",
    "cnavpl_recueils.py",
    "insee_projections_mortalite.py",
)


def _module():
    chemin = FETCH / "source_locale.py"
    specification = importlib.util.spec_from_file_location("source_locale", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["source_locale"] = module
    specification.loader.exec_module(module)
    return module


def _jeux() -> dict[str, dict]:
    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    return {
        jeu["id"]: jeu
        for institution in manifeste["institutions"].values()
        for jeu in institution.get("jeux", [])
    }


def test_le_manifeste_n_admet_que_les_blocages_connus():
    """Une valeur inventée ne dirait rien à qui voudrait apporter le fichier."""
    module = _module()
    for ident, jeu in _jeux().items():
        if "blocage" not in jeu:
            continue
        assert jeu["blocage"] in module.BLOCAGES, (
            f"{ident} : blocage « {jeu['blocage']} » inconnu de source_locale.BLOCAGES")
        assert str(jeu.get("note", "")).strip(), (
            f"{ident} : un blocage se justifie dans la note — ce qui a été essayé, "
            "et ce qui a répondu")
        if "fichier_local" in jeu:
            assert "/" not in jeu["fichier_local"], (
                f"{ident} : fichier_local est un nom sous data/brut/, pas un chemin")


def test_fichier_local_ne_se_declare_que_sur_un_jeu_bloque():
    """Un nom de dépôt sans blocage serait une promesse que rien n'honore."""
    for ident, jeu in _jeux().items():
        if "fichier_local" in jeu:
            assert "blocage" in jeu, f"{ident} : fichier_local sans blocage"


def test_les_refus_constates_sont_declares():
    """Ce que `docs/limites.md` et les notes racontent doit être dans le champ.

    budget.gouv.fr répond 403 aux adresses de sortie du proxy ; la Banque de
    France refuse ses PDF aux clients non navigateur ; l'EIC est sous convention.
    """
    jeux = _jeux()
    assert jeux["sre_jaune_pensions"]["blocage"] == "refus"
    assert jeux["db_cas_pensions"]["blocage"] == "refus"
    assert jeux["opef_rapport_annuel"]["blocage"] == "refus"
    assert jeux["legifrance_textes"]["blocage"] == "refus"
    assert jeux["drees_eic"]["blocage"] == "convention"


def test_la_liste_des_sources_bloquees_s_imprime(capsys):
    module = _module()
    assert module.main([]) == 0
    sortie = capsys.readouterr().out
    assert "sre_jaune_pensions  [refus]" in sortie
    assert "drees_eic  [convention]" in sortie
    assert "rien à apporter" in sortie
    for nom in module.BLOCAGES:
        assert nom in sortie


def test_le_nom_du_document_vient_de_l_adresse_quand_elle_en_porte_un():
    module = _module()
    assert module.nom_du_document(
        "https://media.rafp.fr/s3fs-public/2024-02/RAFP-Evolution-valeurs-point.pdf"
    ) == "RAFP-Evolution-valeurs-point.pdf"
    assert module.nom_du_document(
        "https://www.insee.fr/fr/statistiques/fichier/8990899/hyp_mortalite.xlsx"
    ) == "hyp_mortalite.xlsx"
    assert module.nom_du_document("https://site.fr/docs/Bar%C3%A8me%202024.pdf") == "Barème 2024.pdf"
    # Ces adresses servent un fichier sans le nommer : c'est au manifeste ou
    # au récupérateur de le faire.
    assert module.nom_du_document("https://www.budget.gouv.fr/documentation/file-download/31546") is None
    assert module.nom_du_document("https://www.cnavpl.fr/documents/?wpdmdl=263987") is None
    assert module.nom_du_document("https://www.budget.gouv.fr/") is None


def test_lire_ou_telecharger_prefere_le_fichier_puis_data_brut_puis_le_site(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return b"du site"

    url = "https://exemple.fr/pub/tableau.pdf"
    # Rien en local : le site.
    assert module.lire_ou_telecharger(url, telecharger) == b"du site"
    assert appels == [url]

    # Le document déposé sous son nom dans data/brut/ : lu, sans requête.
    (tmp_path / "tableau.pdf").write_bytes(b"apporte")
    assert module.lire_ou_telecharger(url, telecharger) == b"apporte"
    assert appels == [url]

    # Un chemin explicite l'emporte sur tout.
    explicite = tmp_path / "ailleurs.pdf"
    explicite.write_bytes(b"explicite")
    assert module.lire_ou_telecharger(url, telecharger, explicite) == b"explicite"
    assert appels == [url]

    # Un chemin explicite qui n'existe pas est une erreur, pas un téléchargement.
    with pytest.raises(OSError):
        module.lire_ou_telecharger(url, telecharger, tmp_path / "absent.pdf")
    assert appels == [url]


def test_une_adresse_sans_nom_telecharge_sauf_nom_local(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return b"du site"

    url = "https://www.cnavpl.fr/documents/?wpdmdl=263987"
    (tmp_path / "cnavpl_recueil_2021.pdf").write_bytes(b"recueil")
    # Sans nom local, rien n'est cherché sous data/brut/ : on télécharge.
    assert module.lire_ou_telecharger(url, telecharger) == b"du site"
    # Avec le nom que le récupérateur attend, le dépôt répond.
    assert module.lire_ou_telecharger(url, telecharger, nom_local="cnavpl_recueil_2021.pdf") == b"recueil"
    assert appels == [url]
    with pytest.raises(ValueError):
        module.chemin_local(url, "../ailleurs.pdf")


def test_ou_deposer_suit_le_manifeste():
    module = _module()
    assert module.ou_deposer({"blocage": "convention", "url": "https://x.fr/a.pdf"}) is None
    assert module.ou_deposer({"blocage": "refus", "url": "https://www.budget.gouv.fr/"}) is None
    attendu = module.ou_deposer({"blocage": "refus",
                                 "url": "https://www.budget.gouv.fr/documentation/file-download/31546",
                                 "fichier_local": "Jaune2026_Pensions.pdf"})
    assert attendu == module.BRUT / "Jaune2026_Pensions.pdf"


def test_les_recuperateurs_de_documents_passent_par_le_module():
    """Un récupérateur qui ouvre l'adresse lui-même ne saurait pas lire un fichier apporté."""
    for nom in LECTEURS_DE_DOCUMENTS:
        source = (FETCH / nom).read_text(encoding="utf-8")
        assert "lire_ou_telecharger(" in source, f"{nom} n'appelle pas lire_ou_telecharger"


def test_un_miroir_nomme_son_fichier_et_son_empreinte_est_une_sha256():
    """Sans nom, `--recuperer` ne saurait pas où écrire ; sans empreinte, il
    ne saurait pas s'il a reçu le bon document."""
    import re

    module = _module()
    for ident, jeu in _jeux().items():
        if "miroir" not in jeu:
            continue
        assert "blocage" in jeu, f"{ident} : un miroir sans blocage n'a pas de raison d'être"
        assert module.ou_deposer(jeu) is not None, (
            f"{ident} : le miroir ne nomme pas de fichier et fichier_local est absent")
        assert re.fullmatch(r"[0-9a-f]{64}", str(jeu.get("sha256", ""))), (
            f"{ident} : un miroir se déclare avec l'empreinte SHA-256 du document")
        assert jeu["miroir"] != jeu["url"], f"{ident} : le miroir est un autre hôte"


def test_les_annexes_budgetaires_ont_leur_miroir_a_l_assemblee():
    """budget.gouv.fr refuse la session ; l'Assemblée nationale sert le même
    fichier. C'est ce qui rend ces trois documents récupérables sans personne."""
    jeux = _jeux()
    for ident in ("sre_jaune_pensions", "db_cas_pensions", "db_pap_regimes_sociaux"):
        assert "assemblee-nationale.fr" in jeux[ident]["miroir"], ident


def test_lire_ou_telecharger_essaie_le_miroir_avant_l_adresse(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return b"document"

    url = "https://www.budget.gouv.fr/documentation/file-download/31546"
    miroir = "https://questions.assemblee-nationale.fr/x/12-Jaune2026_Pensions.pdf"
    bon = module.empreinte(b"document")
    assert module.lire_ou_telecharger(url, telecharger, nom_local="j.pdf",
                                      miroir=miroir, sha256=bon) == b"document"
    assert appels == [miroir]
    # Une empreinte qui ne correspond pas : on refuse, on ne devine pas.
    with pytest.raises(ValueError):
        module.lire_ou_telecharger(url, telecharger, miroir=miroir, sha256="0" * 64)
    # Le fichier déposé sous son nom passe avant le miroir, et il est contrôlé aussi.
    (tmp_path / "j.pdf").write_bytes(b"autre")
    with pytest.raises(ValueError):
        module.lire_ou_telecharger(url, telecharger, nom_local="j.pdf", miroir=miroir, sha256=bon)
    assert module.lire_ou_telecharger(url, telecharger, nom_local="j.pdf", miroir=miroir,
                                      sha256=module.empreinte(b"autre")) == b"autre"
    assert appels == [miroir, miroir]


def test_recuperer_ecrit_verifie_et_ne_refait_rien(tmp_path, monkeypatch, capsys):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    contenu = b"%PDF le jaune"
    jeux = [
        {"id": "jaune", "blocage": "refus", "url": "https://budget.example/file-download/1",
         "fichier_local": "jaune.pdf", "miroir": "https://an.example/jaune.pdf",
         "sha256": module.empreinte(contenu)},
        {"id": "faux", "blocage": "refus", "url": "https://budget.example/file-download/2",
         "fichier_local": "faux.pdf", "miroir": "https://an.example/faux.pdf",
         "sha256": "0" * 64},
        {"id": "sans_miroir", "blocage": "refus", "url": "https://x.example/a.pdf"},
        {"id": "eic", "blocage": "convention", "url": "https://drees.example/eic"},
    ]
    appels: list[str] = []

    def telecharger(url: str) -> bytes:
        appels.append(url)
        return contenu

    faits = module.recuperer(jeux, telecharger)
    # Le jeu sans miroir déclaré est cherché sur la release du dépôt, et c'est dit.
    assert faits == [tmp_path / "jaune.pdf", tmp_path / "a.pdf"]
    assert (tmp_path / "jaune.pdf").read_bytes() == contenu
    assert not (tmp_path / "faux.pdf").exists(), "un document non reconnu n'est pas déposé"
    assert sorted(appels) == ["https://an.example/faux.pdf", "https://an.example/jaune.pdf",
                              module.url_publiee("a.pdf")]
    sortie = capsys.readouterr().out
    assert "faux : ÉCHEC" in sortie and "sans_miroir : miroir non déclaré" in sortie

    # Une seconde passe ne retélécharge pas ce qui est là et conforme.
    appels.clear()
    assert module.recuperer(jeux[:1], telecharger) == [tmp_path / "jaune.pdf"]
    assert appels == []
    # Un fichier présent mais différent est remplacé, et dit.
    (tmp_path / "jaune.pdf").write_bytes(b"perime")
    module.recuperer(jeux[:1], telecharger)
    assert (tmp_path / "jaune.pdf").read_bytes() == contenu
    assert "remplacé" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# La release du dépôt comme miroir : --publier depuis un workflow, --recuperer
# depuis une session
# ---------------------------------------------------------------------------


def _http_error(code: int, url: str = "https://x.example/doc.pdf"):
    import urllib.error

    return urllib.error.HTTPError(url, code, "refus", {}, None)


def test_tout_refus_visant_un_fichier_a_un_miroir_ou_un_document_publiable():
    """Un jeu `refus` qui vise un fichier se récupère sans personne : par un
    miroir déclaré, ou par la release que `--publier` alimente depuis son
    adresse de document. Les entrées Légifrance ne visent pas un fichier :
    leurs textes se lisent dans l'index DILA, rien n'est à apporter."""
    module = _module()
    for ident, jeu in _jeux().items():
        if jeu.get("blocage") != "refus":
            continue
        if module.ou_deposer(jeu) is None:
            assert "fichier_local" not in jeu and "document" not in jeu, (
                f"{ident} : un fichier est visé, mais l'adresse ne le nomme pas")
            continue
        assert jeu.get("miroir") or module.a_publier([jeu]), (
            f"{ident} : ni miroir, ni adresse de document que --publier sait traiter "
            "(document: quand url est une page)")


def test_le_rapport_opef_declare_son_document_a_la_banque_de_france():
    jeu = _jeux()["opef_rapport_annuel"]
    assert jeu["document"].startswith("https://www.banque-france.fr/") and jeu["document"].endswith("OPEF2026.pdf")
    assert jeu["fichier_local"] == "OPEF2026.pdf"


def test_adresse_du_document_prefere_le_champ_document_puis_une_url_qui_nomme():
    module = _module()
    assert module.adresse_du_document({"url": "https://a.fr/page", "document": "https://a.fr/f.pdf"}) == "https://a.fr/f.pdf"
    assert module.adresse_du_document({"url": "https://a.fr/f.pdf"}) == "https://a.fr/f.pdf"
    assert module.adresse_du_document({"url": "https://a.fr/page"}) is None


def test_a_publier_ne_retient_que_les_refus_sans_autre_miroir_que_la_release():
    module = _module()
    ici = module.url_publiee("f.pdf")
    assert ici == "https://github.com/g-pliberal/retraitecomptenotionelle/releases/download/documents-apportes/f.pdf"
    jeux = [
        {"id": "sans_miroir", "blocage": "refus", "url": "https://a.fr/page", "document": "https://a.fr/f.pdf",
         "fichier_local": "f.pdf"},
        {"id": "deja_ici", "blocage": "refus", "url": "https://a.fr/g.pdf", "miroir": ici, "sha256": "0" * 64},
        {"id": "ailleurs", "blocage": "refus", "url": "https://a.fr/h.pdf", "miroir": "https://an.fr/h.pdf"},
        {"id": "sans_fichier", "blocage": "refus", "url": "https://a.fr/page"},
        {"id": "reseau", "blocage": "reseau", "url": "https://a.fr/i.pdf"},
        {"id": "eic", "blocage": "convention", "url": "https://a.fr/j.pdf"},
    ]
    assert [j["id"] for j in module.a_publier(jeux)] == ["sans_miroir", "deja_ici"]


def test_telecharger_document_essaie_la_requete_simple_puis_le_navigateur(capsys):
    module = _module()
    jeu = {"id": "x", "blocage": "refus", "url": "https://a.fr/page", "document": "https://a.fr/f.pdf"}
    appels: list[tuple] = []

    def simple_ok(url):
        appels.append(("simple", url))
        return b"pdf"

    def simple_403(url):
        appels.append(("simple", url))
        raise _http_error(403, url)

    def simple_404(url):
        raise _http_error(404, url)

    def navigateur(page, document):
        appels.append(("navigateur", page, document))
        return b"pdf par chromium"

    assert module.telecharger_document(jeu, simple_ok, navigateur) == (b"pdf", "requête simple")
    assert appels == [("simple", "https://a.fr/f.pdf")]
    appels.clear()
    assert module.telecharger_document(jeu, simple_403, navigateur) == (b"pdf par chromium", "navigateur")
    assert appels == [("simple", "https://a.fr/f.pdf"), ("navigateur", "https://a.fr/page", "https://a.fr/f.pdf")]
    # Un 404 n'est pas un refus : un navigateur ne trouverait pas davantage.
    with pytest.raises(Exception) as info:
        module.telecharger_document(jeu, simple_404, navigateur)
    assert info.value.code == 404
    # Refusé, et personne pour insister.
    with pytest.raises(module.NavigateurRequis):
        module.telecharger_document(jeu, simple_403, None)
    with pytest.raises(ValueError):
        module.telecharger_document({"id": "y", "blocage": "refus", "url": "https://a.fr/page"}, simple_ok, navigateur)


class _GitHubSimule:
    """Assez de l'API des releases pour voir ce que `publier` lui demande."""

    def __init__(self, existe: bool = True, assets=(), corps: str = ""):
        self.existe = existe
        self.assets = list(assets)
        self.corps = corps
        self.appels: list[tuple] = []
        self.envoyes: dict[str, bytes] = {}

    def _release(self):
        return {"url": "https://api/releases/1", "upload_url": "https://uploads/releases/1/assets{?name,label}",
                "body": self.corps,
                "assets": [{"name": n, "url": f"https://api/assets/{n}"} for n in self.assets]}

    def __call__(self, methode, url, jeton, donnees=None, type_contenu="application/json", longueur=None):
        import json

        self.appels.append((methode, url))
        if methode == "GET":
            if not self.existe:
                raise _http_error(404, url)
            return self._release()
        if methode == "POST" and url.endswith("/releases"):
            self.existe = True
            self.corps = json.loads(donnees)["body"]
            return self._release()
        if methode == "DELETE":
            self.assets.remove(url.rsplit("/", 1)[-1])
            return {}
        if methode == "POST":
            nom = url.split("?name=")[1]
            assert type_contenu == "application/pdf" and longueur == len(donnees)
            self.envoyes[nom] = donnees
            self.assets.append(nom)
            return {"browser_download_url": f"https://github.com/x/releases/download/documents-apportes/{nom}"}
        if methode == "PATCH":
            self.corps = json.loads(donnees)["body"]
            return {}
        raise AssertionError(methode)


def test_publier_cree_la_release_depose_l_asset_et_ecrit_la_ligne(monkeypatch, capsys):
    module = _module()
    github = _GitHubSimule(existe=False)
    monkeypatch.setattr(module, "_github", github)
    contenu = b"%PDF opef"
    jeux = [
        {"id": "opef", "blocage": "refus", "url": "https://bdf.fr/page",
         "document": "https://bdf.fr/OPEF2026.pdf", "fichier_local": "OPEF2026.pdf"},
        {"id": "jaune", "blocage": "refus", "url": "https://budget.fr/x", "fichier_local": "j.pdf",
         "miroir": "https://an.fr/j.pdf", "sha256": "0" * 64},
    ]

    def simple(url):
        raise _http_error(403, url)

    etats = module.publier(jeux, simple, lambda page, doc: contenu, jeton="t")
    assert etats == {"opef": "publie"}
    assert any(m == "POST" and u.endswith("/releases") for m, u in github.appels), (
        "la release est créée quand elle n'existe pas")
    assert github.envoyes == {"OPEF2026.pdf": contenu}
    assert github.assets == ["OPEF2026.pdf"]
    lignes = [l for l in github.corps.splitlines() if l.startswith("- `OPEF2026.pdf`")]
    assert len(lignes) == 1
    assert module.empreinte(contenu) in lignes[0] and "https://bdf.fr/OPEF2026.pdf" in lignes[0]
    assert "(navigateur)" in lignes[0]
    assert "Déposés par" in github.corps.splitlines()[0]
    sortie = capsys.readouterr().out
    assert "opef : 403 à la requête simple" in sortie
    assert "opef : OPEF2026.pdf publié" in sortie and module.empreinte(contenu) in sortie

    # Seconde publication : l'asset du même nom est remplacé, la ligne aussi, pas dupliquée.
    contenu2 = b"%PDF opef v2"
    etats = module.publier(jeux[:1], lambda url: contenu2, None, jeton="t")
    assert etats == {"opef": "publie"}
    assert ("DELETE", "https://api/assets/OPEF2026.pdf") in github.appels
    assert github.assets == ["OPEF2026.pdf"] and github.envoyes["OPEF2026.pdf"] == contenu2
    lignes = [l for l in github.corps.splitlines() if l.startswith("- `OPEF2026.pdf`")]
    assert len(lignes) == 1 and module.empreinte(contenu2) in lignes[0] and "(requête simple)" in lignes[0]


def test_publier_ne_remplace_pas_un_document_dont_le_manifeste_porte_une_autre_empreinte(monkeypatch, capsys):
    module = _module()
    github = _GitHubSimule(assets=["OPEF2026.pdf"], corps="- `OPEF2026.pdf` : ancien")
    monkeypatch.setattr(module, "_github", github)
    ici = module.url_publiee("OPEF2026.pdf")
    jeu = {"id": "opef", "blocage": "refus", "url": "https://bdf.fr/page", "document": "https://bdf.fr/OPEF2026.pdf",
           "fichier_local": "OPEF2026.pdf", "miroir": ici, "sha256": module.empreinte(b"edition lue")}
    assert module.publier([jeu], lambda url: b"autre edition", None, jeton="t") == {"opef": "ecart"}
    assert github.envoyes == {} and github.corps == "- `OPEF2026.pdf` : ancien"
    assert "opef : ÉCART" in capsys.readouterr().out
    # La même édition : republiée, idempotent.
    assert module.publier([jeu], lambda url: b"edition lue", None, jeton="t") == {"opef": "publie"}
    assert github.envoyes == {"OPEF2026.pdf": b"edition lue"}


def test_publier_dit_quand_il_faut_un_navigateur_et_quand_ca_echoue(monkeypatch, capsys):
    module = _module()
    github = _GitHubSimule()
    monkeypatch.setattr(module, "_github", github)
    jeux = [
        {"id": "refuse", "blocage": "refus", "url": "https://a.fr/a.pdf"},
        {"id": "absent", "blocage": "refus", "url": "https://a.fr/b.pdf"},
        {"id": "ok", "blocage": "refus", "url": "https://a.fr/c.pdf"},
    ]

    def simple(url):
        if url.endswith("a.pdf"):
            raise _http_error(403, url)
        if url.endswith("b.pdf"):
            raise _http_error(404, url)
        return b"c"

    assert module.publier(jeux, simple, None, jeton="t") == {"refuse": "navigateur", "absent": "echec", "ok": "publie"}
    sortie = capsys.readouterr().out
    assert "refuse : NAVIGATEUR REQUIS" in sortie and "absent : ÉCHEC" in sortie
    assert github.envoyes == {"c.pdf": b"c"}
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        module.publier(jeux, simple, None)


def test_recuperer_cherche_la_release_quand_aucun_miroir_n_est_declare(tmp_path, monkeypatch, capsys):
    module = _module()
    monkeypatch.setattr(module, "BRUT", tmp_path)
    monkeypatch.setattr(module, "RACINE", tmp_path)
    jeu = {"id": "opef", "blocage": "refus", "url": "https://bdf.fr/page",
           "document": "https://bdf.fr/OPEF2026.pdf", "fichier_local": "OPEF2026.pdf"}
    ici = module.url_publiee("OPEF2026.pdf")
    appels: list[str] = []

    def rien(url):
        appels.append(url)
        raise _http_error(404, url)

    assert module.recuperer([jeu], rien) == []
    assert appels == [ici]
    assert "lancer le workflow documents-apportes.yml" in capsys.readouterr().out

    def publie(url):
        return b"%PDF"

    assert module.recuperer([jeu], publie) == [tmp_path / "OPEF2026.pdf"]
    sortie = capsys.readouterr().out
    assert f"miroir: {ici}" in sortie and f"sha256: {module.empreinte(b'%PDF')}" in sortie


def test_le_workflow_documents_apportes_publie_avec_le_droit_d_ecrire():
    """Sans `contents: write`, `--publier` ne pourrait pas déposer l'asset ; sans
    `--publier`, le workflow ne servirait à rien."""
    chemin = RACINE / ".github" / "workflows" / "documents-apportes.yml"
    workflow = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    assert workflow["permissions"] == {"contents": "write"}
    declencheurs = workflow[True] if True in workflow else workflow["on"]
    assert "workflow_dispatch" in declencheurs and "schedule" in declencheurs
    texte = chemin.read_text(encoding="utf-8")
    assert "source_locale.py --publier" in texte
    assert "playwright install" in texte
