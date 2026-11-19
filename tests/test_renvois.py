"""Les renvois d'une version : leur forme au contrat, leur contrôle d'une fiche
à l'autre.

Note de décision 0009 et ses deux rectificatifs (``docs/decisions/``). Une
version porte ce que dit son texte : une table, que la fiche désigne dans un
fichier indexé par version ; un renvoi daté à une autre fiche, qui nomme la
fiche, la valeur qu'il y lit, de qui, l'opération et la date qui choisit la
version lue ; un renvoi à sa propre rédaction antérieure, qui nomme la version
par son identifiant. Le contrat de la fiche
(``data/reference/contrats/fiche.yaml``) en fixe la forme, et
``noyau/renvois.py`` les contrôle quand les données se fabriquent : sur toute
l'étendue des bornes de sa version, la fiche lue a une version et une seule,
et aucune chaîne ne boucle.
"""

from __future__ import annotations

import copy

import pytest
import yaml

from retraite_notionnelle.noyau import carte, contrats, renvois

EFFET = "liquidation.date_effet"


def _version(identifiant: str, debut, fin, **contenu) -> dict:
    return {"id": identifiant, "statut": "supposee", "hypothese": "fiche de poche",
            "fiabilite": "nulle", "bornes": {EFFET: [debut, fin]},
            "contenu": contenu, "exemples": "aucun trouvé"}


def _fiche(identifiant: str, *versions: dict, dates=(EFFET,)) -> dict:
    return {"schema_version": 1, "id": identifiant, "intitule": "fiche de poche",
            "domaine": "age", "regimes": ["regime_general"], "etape": "ouvrir_le_droit",
            "etat": "transcrite", "lit": [], "ecrit": [],
            "dates_qui_decident": list(dates), "versions": list(versions),
            "code": {"javascript": "aucun"}}


RENVOI = {"fiche": "age_legal", "valeur": "age", "de": "assure", "date": EFFET,
          "ajoute": {"ans": 5}}


def _age_legal() -> dict:
    """La fiche lue : une valeur jusqu'en 2011, une table ensuite."""
    return _fiche(
        "age_legal",
        _version("soixante_ans", None, "2011-07-01", parametres={"age": 60}),
        _version("par_generation", "2011-07-01", None,
                 table={"fichier": "legislation/age_legal_par_version.csv",
                        "lignes": {"entree_en_vigueur": ["2011-07-01"]},
                        "cle": "generation", "valeur": "age"}))


def _taux_plein(**renvoi) -> dict:
    """La fiche qui lit : l'âge légal augmenté de cinq années, depuis 2011."""
    return _fiche(
        "taux_plein",
        _version("soixante_cinq_ans", None, "2011-07-01", parametres={"age": 65}),
        _version("age_legal_plus_cinq", "2011-07-01", None,
                 renvois=[{**RENVOI, **renvoi}]))


def _constats(version: dict) -> list[contrats.Constat]:
    return contrats.Validateur("fiche").valider(version, "version")


# --- La forme, au contrat ---------------------------------------------------

def test_un_renvoi_date_nomme_sa_fiche_sa_valeur_de_qui_et_sa_date():
    """Les quatre sont obligatoires : il en manque un, et la version n'est pas
    mûre. « De qui » : l'âge légal de l'assuré n'est pas celui du conjoint
    survivant, et le renvoi le dit."""
    version = _taux_plein()["versions"][1]
    assert _constats(version) == []
    for champ in ("fiche", "valeur", "de", "date"):
        sans = copy.deepcopy(version)
        del sans["contenu"]["renvois"][0][champ]
        constats = _constats(sans)
        assert [(c.genre, c.chemin) for c in constats] == [
            ("manque", f"version.contenu.renvois[0].{champ}")], (champ, constats)


@pytest.mark.parametrize("champ, valeur, message", [
    ("de", "voisin", "personnes_lues"),
    ("date", "le_jour_dit", "date nommée"),
    ("fiche", "Âge légal", "identifiant"),
    ("multiplie", 2, "inconnu"),
    ("ajoute", {"semaines": 3}, "inconnu"),
    ("ajoute", {"ans": "cinq"}, "entier"),
])
def test_ce_qu_un_renvoi_ne_sait_pas_dire_est_une_erreur(champ, valeur, message):
    version = _taux_plein(**{champ: valeur})["versions"][1]
    erreurs = [c for c in _constats(version) if c.genre == "erreur"]
    assert erreurs and all(message in c.message for c in erreurs), erreurs


def test_l_operation_d_un_renvoi_ajoute_ou_retranche_une_duree_ou_nomme_sa_fonction():
    """Une durée s'ajoute ou se retranche ; toute autre opération passe par une
    fonction que le renvoi nomme, sans quoi le format devient un langage. Une
    seule des trois, ou aucune : la valeur lue telle quelle."""
    def erreurs(**renvoi):
        version = _taux_plein(**renvoi)["versions"][1]
        return [c.message for c in _constats(version) if c.genre == "erreur"]

    assert erreurs() == []
    assert erreurs(ajoute=None) == []
    assert erreurs(ajoute=None, retranche={"ans": 2, "mois": 6}) == []
    assert erreurs(ajoute=None, code="moteur/js/droit/ouvrir.js : ageTauxPlein") == []
    assert any("au plus un" in m for m in erreurs(retranche={"mois": 6})), erreurs(retranche={"mois": 6})
    assert any("au plus un" in m for m in erreurs(code="moteur/js/droit/ouvrir.js : ageTauxPlein"))


def test_un_renvoi_a_la_redaction_anterieure_nomme_la_version_par_son_identifiant():
    """« Pour les assurés nés avant le 1er septembre 1961, il est celui
    applicable en application du présent article dans sa rédaction
    antérieure » : la version nommée, et les naissances qu'elle garde."""
    version = _version("suspension", "2026-09-01", None,
                       redaction_anterieure={"version": "loi_2023",
                                             "naissance": [None, "1961-09-01"]})
    assert _constats(version) == []
    sans = copy.deepcopy(version)
    del sans["contenu"]["redaction_anterieure"]["version"]
    assert [(c.genre, c.chemin) for c in _constats(sans)] == [
        ("manque", "version.contenu.redaction_anterieure.version")]
    for champ, valeur in (("version", "Loi de 2023"), ("naissance", "avant 1961"),
                          ("generation", 1961)):
        faux = copy.deepcopy(version)
        faux["contenu"]["redaction_anterieure"][champ] = valeur
        assert [c.genre for c in _constats(faux)] == ["erreur"], champ


def test_une_version_designe_les_lignes_de_sa_table():
    """La table d'une version tient dans un fichier indexé par version : la
    version nomme le fichier, les lignes qui sont les siennes, la colonne qui
    choisit la ligne et celle de la valeur."""
    version = _age_legal()["versions"][1]
    assert _constats(version) == []
    for champ in ("fichier", "lignes", "cle", "valeur"):
        sans = copy.deepcopy(version)
        del sans["contenu"]["table"][champ]
        assert [(c.genre, c.chemin) for c in _constats(sans)] == [
            ("manque", f"version.contenu.table.{champ}")], champ
    faux = copy.deepcopy(version)
    faux["contenu"]["table"]["recopie"] = [[1955, 62]]
    assert [c.genre for c in _constats(faux)] == ["erreur"]


def test_le_reste_du_contenu_reste_libre():
    """Le contrat s'enrichit sans rien perdre : un contenu en prose, ou en
    champs que le contrat ne nomme pas, reste valide."""
    assert _constats(_version("prose", None, None) | {"contenu": "une phrase"}) == []
    assert _constats(_version("champs", None, None, droit="soixante ans",
                              parametres={"age": 60})) == []


# --- Le contrôle, d'une fiche à l'autre -------------------------------------

def test_un_renvoi_tient_quand_la_fiche_lue_a_une_version_et_une_seule():
    assert renvois.controler({"age_legal": _age_legal(), "taux_plein": _taux_plein()}) == []


def test_un_renvoi_sans_fiche_nomme_la_sienne_et_celle_qui_manque():
    erreurs = renvois.controler({"taux_plein": _taux_plein()})
    assert len(erreurs) == 1 and "taux_plein.age_legal_plus_cinq" in erreurs[0]
    assert "« age_legal »" in erreurs[0], erreurs


def test_un_trou_dans_la_fiche_lue_se_voit_sur_l_etendue_de_la_version():
    """La version lit depuis le 1er juillet 2011 ; la fiche lue n'a rien du
    1er septembre 2023 au 1er septembre 2026."""
    lue = _age_legal()
    lue["versions"][1]["bornes"][EFFET] = ["2011-07-01", "2023-09-01"]
    lue["versions"].append(_version("suspension", "2026-09-01", None, parametres={"age": 64}))
    erreurs = renvois.controler({"age_legal": lue, "taux_plein": _taux_plein()})
    assert len(erreurs) == 1, erreurs
    assert "aucune version de « age_legal »" in erreurs[0] and "2023-09-01" in erreurs[0]
    # Hors de l'étendue de la version qui lit, un trou ne la regarde pas.
    lue["versions"] = lue["versions"][1:2]
    lue["versions"][0]["bornes"][EFFET] = ["2011-07-01", None]
    assert renvois.controler({"age_legal": lue, "taux_plein": _taux_plein()}) == []


def test_deux_versions_de_la_fiche_lue_a_la_meme_date_se_voient():
    lue = _age_legal()
    lue["versions"].append(_version("doublon", "2020-01-01", None, parametres={"age": 62}))
    erreurs = renvois.controler({"age_legal": lue, "taux_plein": _taux_plein()})
    assert len(erreurs) == 1, erreurs
    assert "par_generation et doublon" in erreurs[0] and "2020-01-01" in erreurs[0]
    # Une exception déclarée prime, comme au partage.
    lue["versions"][2]["exception_de"] = "par_generation"
    assert renvois.controler({"age_legal": lue, "taux_plein": _taux_plein()}) == []


def test_la_date_du_renvoi_est_la_seule_qui_choisit_la_version_lue():
    """Une fiche qui se choisit aussi à une autre date n'a pas « une version
    et une seule » à la date que le renvoi nomme."""
    lue = _age_legal()
    lue["dates_qui_decident"] = [EFFET, "assure.generation"]
    erreurs = renvois.controler({"age_legal": lue, "taux_plein": _taux_plein()})
    assert len(erreurs) == 1 and "assure.generation" in erreurs[0], erreurs
    erreurs = renvois.controler({"age_legal": _age_legal(),
                                 "taux_plein": _taux_plein(date="pension.echeance")})
    assert len(erreurs) == 1 and "pension.echeance" in erreurs[0], erreurs


def test_la_valeur_nommee_est_portee_par_chaque_version_lue():
    """Un renvoi nomme une valeur, non la fiche entière : un paramètre de la
    version lue, ou la colonne de sa table."""
    erreurs = renvois.controler({"age_legal": _age_legal(),
                                 "taux_plein": _taux_plein(valeur="age_du_premier_alinea")})
    assert len(erreurs) == 1, erreurs
    assert "« age_du_premier_alinea »" in erreurs[0] and "age_legal.par_generation" in erreurs[0]


def test_une_chaine_de_renvois_qui_boucle_nomme_ses_fiches():
    lue = _age_legal()
    lue["versions"][1]["contenu"]["renvois"] = [
        {"fiche": "taux_plein", "valeur": "age", "de": "assure", "date": EFFET,
         "retranche": {"ans": 5}}]
    lisant = _taux_plein()
    lisant["versions"][1]["contenu"]["parametres"] = {"age": 67}
    erreurs = renvois.controler({"age_legal": lue, "taux_plein": lisant})
    assert len(erreurs) == 1, erreurs
    assert "boucle" in erreurs[0]
    assert "age_legal.par_generation" in erreurs[0] and "taux_plein.age_legal_plus_cinq" in erreurs[0]


def test_la_redaction_anterieure_est_une_autre_version_de_la_fiche_et_ne_boucle_pas():
    fiche = _age_legal()
    fiche["versions"].append(_version("suspension", "2026-09-01", None))
    fiche["versions"][1]["bornes"][EFFET] = ["2011-07-01", "2026-09-01"]
    suspension = fiche["versions"][2]["contenu"]
    suspension["redaction_anterieure"] = {"version": "par_generation",
                                          "naissance": [None, "1961-09-01"]}
    assert renvois.controler({"age_legal": fiche}) == []
    suspension["redaction_anterieure"]["version"] = "loi_de_1945"
    erreurs = renvois.controler({"age_legal": fiche})
    assert len(erreurs) == 1 and "« loi_de_1945 »" in erreurs[0], erreurs
    suspension["redaction_anterieure"]["version"] = "suspension"
    erreurs = renvois.controler({"age_legal": fiche})
    assert len(erreurs) == 1 and "elle-même" in erreurs[0], erreurs
    suspension["redaction_anterieure"]["version"] = "par_generation"
    fiche["versions"][1]["contenu"]["redaction_anterieure"] = {"version": "suspension"}
    erreurs = renvois.controler({"age_legal": fiche})
    assert len(erreurs) == 1 and "boucle" in erreurs[0], erreurs


def test_la_carte_joue_le_controle_des_renvois(tmp_path):
    """Le contrôle de la carte, que la suite et la fabrication des vues
    jouent, refuse un renvoi sans cible."""
    for fiche in (_age_legal(), _taux_plein(fiche="age_du_capitaine")):
        (tmp_path / f"{fiche['id']}.yaml").write_text(
            yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False), encoding="utf-8")
    erreurs = carte.controler(tmp_path)
    assert len(erreurs) == 1 and "« age_du_capitaine »" in erreurs[0], erreurs
