"""Les neuf contrats de données, en schémas : ``data/reference/contrats/``.

``docs/architecture.md``, § 13.1 et annexe C. Les contrats sont au noyau : un
champ n'en sort, ne change de sens ou ne devient obligatoire que par une note
de décision, et un champ facultatif s'y ajoute sans elle (§ 13.3). Ce test
tient les schémas à l'annexe, table par table ; il fait passer les deux fiches
d'exemple de l'annexe A par le validateur ; et il montre ce que le validateur
distingue : l'ERREUR, qu'un moteur refuserait, du MANQUE, qu'il compte.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.noyau import contrats

RACINE = Path(__file__).resolve().parents[1]
ARCHITECTURE = (RACINE / "docs" / "architecture.md").read_text(encoding="utf-8")

#: Pour chaque section de l'annexe C, le contrat et, dans l'ordre de ses
#: tables, les objets qu'elles décrivent.
PLAN = {
    "C.1": ("chronologie", ["chronologie", "fait", "lien"]),
    "C.2": ("fiche", ["fiche", "relation", "version"]),
    "C.3": ("table_datee", ["table_datee"]),
    "C.4": ("univers", ["couche", "univers"]),
    "C.5": ("ligne_releve", ["releve", "ligne"]),
    "C.6": ("liquidation", ["liquidation"]),
    "C.7": ("evenement", ["evenement"]),
    "C.8": ("entree_journal", ["entree"]),
    "C.9": ("surface_publique", ["surface"]),
}

_TABLE = re.compile(r"^\| Champ \| Ce qu'il porte \| Défaut \|\n\|---\|---\|---\|\n((?:\|.*\n)+)", re.M)


def _annexe_c() -> dict[str, list[str]]:
    """Les tables de l'annexe C, section par section."""
    debut = ARCHITECTURE.index("## Annexe C")
    fin = ARCHITECTURE.index("### Les deux règles d'exécution", debut)
    morceaux = re.split(r"^### (C\.\d) .*$", ARCHITECTURE[debut:fin], flags=re.M)[1:]
    return {num: _TABLE.findall(corps) for num, corps in zip(morceaux[::2], morceaux[1::2])}


def _champs_de(table: str) -> tuple[set[str], set[str]]:
    """Les champs qu'une table nomme en première colonne, et tous ceux
    qu'elle cite : « `id` … ; `remplacee_par` si elle est dépréciée »."""
    premiers, cites = set(), set()
    for ligne in table.splitlines():
        premiers |= set(re.findall(r"`([a-z_]+)`", ligne.strip("|").split("|")[0]))
        cites |= set(re.findall(r"`([a-z_]+)`", ligne))
    return premiers, cites


def _fiches_de_l_annexe_a() -> dict[str, dict]:
    debut = ARCHITECTURE.index("## Annexe A")
    fin = ARCHITECTURE.index("## Annexe B", debut)
    blocs = re.findall(r"^```yaml\n(.*?)^```", ARCHITECTURE[debut:fin], re.M | re.S)
    return {fiche["id"]: fiche for fiche in map(yaml.safe_load, blocs)}


def test_les_schemas_tiennent():
    assert contrats.controler() == []


def test_les_contrats_sont_ceux_de_l_annexe_c():
    """Neuf sections, neuf contrats, et chaque table retrouvée dans son objet :
    tout champ que l'annexe nomme est au schéma, et tout champ du schéma est
    nommé par l'annexe, ou déclaré additif avec sa raison. Le
    ``schema_version`` que chaque contrat porte est dit en tête de l'annexe."""
    tables = _annexe_c()
    assert sorted(tables) == sorted(PLAN), sorted(tables)
    assert sorted(nom for nom, _ in PLAN.values()) == sorted(contrats.NOMS)
    ecarts = []
    for num, (nom, noms_d_objets) in PLAN.items():
        assert contrats.contrat(nom)["annexe"] == num, nom
        assert len(tables[num]) == len(noms_d_objets), (num, len(tables[num]))
        schema = contrats.objets(nom)
        propres = contrats.contrat(nom)["objets"]
        for objet, table in zip(noms_d_objets, tables[num]):
            premiers, cites = _champs_de(table)
            for champ in sorted(premiers - set(schema[objet]["champs"])):
                ecarts.append(f"{num} {objet}.{champ} : dans l'annexe, pas dans le schéma")
            for champ, spec in propres[objet]["champs"].items():
                if champ not in cites | {"schema_version"} and not spec.get("additif"):
                    ecarts.append(f"{num} {objet}.{champ} : dans le schéma, pas dans l'annexe")
    assert not ecarts, "\n".join(ecarts)


def test_les_champs_du_noyau_lisent_son_vocabulaire():
    """L'étape d'une fiche lit la liste fermée des étapes ; ses dates qui
    décident et les bornes de ses versions, les dates nommées (§ 4.2)."""
    fiche = contrats.objets("fiche")["fiche"]["champs"]
    assert fiche["etape"]["valeurs"] == "etapes"
    assert fiche["dates_qui_decident"]["de"] == "date_nommee"
    assert contrats.objets("fiche")["version"]["champs"]["bornes"]["type"] == "bornes"


def test_la_fiche_complete_de_l_annexe_a_suit_le_contrat():
    """A.1 est la fiche de la fonction publique « en entier » : pas une erreur,
    pas un manque."""
    fiche = _fiches_de_l_annexe_a()["enfants_fonction_publique"]
    constats = contrats.Validateur("fiche").valider(fiche, "fiche")
    assert constats == [], "\n".join(map(str, constats))


def test_la_fiche_resumee_de_l_annexe_a_n_a_que_des_manques():
    """A.2 est un résumé : il lui manque ce qu'un résumé omet (ce qu'elle lit
    et écrit, son code), jamais un champ inconnu ni une valeur hors
    vocabulaire."""
    fiche = _fiches_de_l_annexe_a()["mda_regime_general"]
    constats = contrats.Validateur("fiche").valider(fiche, "fiche")
    erreurs = [str(c) for c in constats if c.genre == "erreur"]
    assert not erreurs, "\n".join(erreurs)
    assert {c.chemin for c in constats} >= {"fiche.lit", "fiche.ecrit", "fiche.code"}


@pytest.fixture(scope="module")
def validateur():
    return contrats.Validateur("fiche")


@pytest.fixture
def fiche():
    return copy.deepcopy(_fiches_de_l_annexe_a()["enfants_fonction_publique"])


def _constats(validateur, donnee, objet="fiche"):
    return {(c.genre, c.chemin, c.message) for c in validateur.valider(donnee, objet)}


def _genres(constats, fragment):
    return {genre for genre, chemin, message in constats if fragment in chemin or fragment in message}


def test_ce_qu_un_moteur_ne_connait_pas_est_une_erreur(validateur, fiche):
    """Un champ inconnu, une valeur hors vocabulaire, une borne sur une date
    que le vocabulaire ne nomme pas, un intervalle renversé, un contrat d'une
    autre version : autant d'erreurs."""
    fiche["couleur"] = "bleue"
    fiche["domaine"] = "licornes"
    fiche["dates_qui_decident"].append("lune.pleine")
    fiche["schema_version"] = 2
    version = fiche["versions"][0]
    version["bornes"] = {"lune.pleine": [None, "2004-01-01"],
                         "liquidation.date_effet": ["2010-01-01", "2004-01-01"]}
    version["textes"] = [{"article": "L. 12"}]
    constats = _constats(validateur, fiche)
    assert _genres(constats, "couleur") == {"erreur"}
    assert _genres(constats, "licornes") == {"erreur"}
    assert _genres(constats, "fiche.dates_qui_decident") == {"erreur"}
    assert _genres(constats, "schema_version 2") == {"erreur"}
    assert _genres(constats, "« lune.pleine », qui n'est pas une date nommée") == {"erreur"}
    assert _genres(constats, "renversé") == {"erreur"}
    assert _genres(constats, "il faut l'un de") == {"erreur"}


def test_ce_qui_n_est_pas_encore_su_est_un_manque(validateur, fiche):
    """Une fiche tirée d'un registre ne sait pas encore son étape, une version
    supposée n'a pas encore dit son hypothèse : des manques, pas des fautes."""
    del fiche["etape"]
    version = fiche["versions"][0]
    version["statut"] = "supposee"
    version.pop("hypothese", None)
    constats = _constats(validateur, fiche)
    assert _genres(constats, "fiche.etape") == {"manque"}
    assert _genres(constats, "fiche.versions[0].hypothese") == {"manque"}
    assert not _genres(constats, "fiche.versions[0].textes"), "une version supposée n'a pas à citer"


def test_un_champ_obligatoire_a_ses_conditions(validateur, fiche):
    """Une fiche approchée dit ses approximations ; une fiche pas encore
    modélisée n'a pas de code ; un choix dit sa méthode."""
    fiche["etat"] = "approchee"
    fiche.pop("approximations", None)
    assert _genres(_constats(validateur, fiche), "fiche.approximations") == {"manque"}
    fiche["etat"] = "pas_encore_modelisee"
    fiche.pop("code", None)
    assert not _genres(_constats(validateur, fiche), "fiche.code")

    relation = {**fiche, "sorte": "choix", "rang": 1,
                "fiches": [{"fiche": "a", "role": "générale"}, {"fiche": "b", "role": "exception"}]}
    assert _genres(_constats(validateur, relation, "relation"), "relation.methode") == {"manque"}
    relation["methode"] = "le montant le plus élevé à la date d'effet"
    assert not _genres(_constats(validateur, relation, "relation"), "relation.methode")


_EXEMPLES = {"identifiant": "x1", "texte": "un texte", "entier": 1, "nombre": 1.5,
             "booleen": True, "date": "2026-09-26", "intervalle": ["2026-01-01", None],
             "bornes": {"liquidation.date_effet": [None, "2026-01-01"]},
             "date_nommee": "liquidation.date_effet", "exemples": "aucun trouvé", "libre": {}}


def _minimal(validateur, objet):
    """Une donnée qui ne porte que les champs obligatoires de l'objet, chacun
    d'une valeur de son type."""

    def valeur(spec):
        if spec["type"] == "valeur":
            return sorted(validateur.listes[spec["valeurs"]])[0]
        if spec["type"] == "objet":
            return _minimal(validateur, spec["objet"])
        if spec["type"] == "liste":
            de = spec["de"]
            return [_minimal(validateur, de["objet"]) if isinstance(de, dict) else _EXEMPLES[de]]
        return _EXEMPLES[spec["type"]]

    champs = validateur.objets[objet]["champs"]
    donnee = {c: valeur(s) for c, s in champs.items() if s.get("obligatoire")}
    donnee |= {c: valeur(s) for c, s in champs.items()
               if c not in donnee and contrats.Validateur.obligatoire(s, donnee)}
    if "schema_version" in champs:
        donnee["schema_version"] = validateur.version
    for champ in validateur.objets[objet].get("un_des", [])[:1]:
        donnee[champ] = "x1"
    return donnee


def test_chaque_contrat_valide_une_donnee_minimale():
    """Pour chacun des neuf, une donnée qui ne porte que ses champs
    obligatoires, chacun d'une valeur de son type, passe sans constat : les
    schémas sont applicables tels qu'écrits."""
    for nom in contrats.NOMS:
        validateur = contrats.Validateur(nom)
        for objet in validateur.objets:
            constats = validateur.valider(_minimal(validateur, objet), objet)
            assert constats == [], f"{nom}.{objet} : " + "\n".join(map(str, constats))


#: Les quatre étapes qui construisent le relevé des droits (§ 7.2).
ACQUISITION = ("preparer_la_chronologie", "coordonner_les_affiliations",
               "compter_les_durees", "acquerir_les_droits")

#: Les trois étapes de la liquidation (§ 7.3), et les deux que l'échéancier
#: applique sans liquider (§ 7.4) : la phase 5 les écrit.
LIQUIDATION = ("ouvrir_le_droit", "liquider_chaque_regime", "completer_tous_regimes")
ECHEANCIER = ("faire_vivre", "foyer_et_net")


def test_les_schemas_des_etapes_tiennent():
    """Une étape ne lit d'une autre que des données décrites par un schéma
    (annexe C, « Les deux règles d'exécution ») : chacune des quatre de
    l'acquisition a le sien, chacune des trois de la liquidation et des deux
    de l'échéancier aussi, écrits avant leur code, et chacun tient comme un
    contrat."""
    assert contrats.controler_etapes() == []
    presents = {p.stem for p in contrats.ETAPES.glob("*.yaml")}
    attendus = set(ACQUISITION) | set(LIQUIDATION) | set(ECHEANCIER)
    assert attendus <= presents, sorted(attendus - presents)


def test_chaque_schema_d_etape_valide_une_donnee_minimale():
    """Comme un contrat, chaque schéma d'étape est applicable tel qu'écrit ;
    celui qui renvoie à un contrat — la chronologie de C.1 — n'a rien à
    décrire lui-même."""
    for chemin in sorted(contrats.ETAPES.glob("*.yaml")):
        validateur = contrats.Validateur(chemin.stem, contrats.ETAPES)
        for objet in validateur.objets:
            constats = validateur.valider(_minimal(validateur, objet), objet)
            assert constats == [], f"{chemin.stem}.{objet} : " + "\n".join(map(str, constats))


def test_le_controle_des_etapes_refuse_ce_qui_ne_tient_pas(tmp_path):
    """Un schéma qui ne porte pas le nom d'une étape, qui écrit un objet qu'il
    ne décrit pas, ou dont un champ vise une liste inconnue, est refusé."""
    (tmp_path / "rever.yaml").write_text(
        "etape: rever\nschema_version: 1\nlit: [chronologie]\necrit: songe\nobjets:\n"
        "  reve:\n    champs:\n"
        "      couleur: {porte: \"sa couleur\", type: valeur, valeurs: couleurs, obligatoire: true}\n",
        encoding="utf-8")
    erreurs = "\n".join(contrats.controler_etapes(tmp_path))
    assert "porte le nom d'une étape" in erreurs
    assert "« songe », est décrit" in erreurs
    assert "« couleurs » inconnue" in erreurs


def test_le_releve_a_son_enveloppe():
    """Le relevé d'une demande (C.5) : la personne, la date de situation, ses
    lignes, et les régimes que la coordination fait liquider ensemble."""
    validateur = contrats.Validateur("ligne_releve")
    releve = {"schema_version": 1, "personne": "assure", "date": "2039-06-01",
              "lignes": [], "groupes": [{"regimes": ["rsi", "regime_general"]}]}
    assert validateur.valider(releve, "releve") == []
    releve["groupes"] = [{"regimes": "rsi"}]
    assert [c.genre for c in validateur.valider(releve, "releve")] == ["erreur"]


def test_un_fait_presume_nomme_sa_presomption():
    """Le fait qu'une présomption pose porte son nom (§ 5.6) : sans lui, c'est
    un manque ; un nom que le vocabulaire ne connaît pas est une erreur."""
    validateur = contrats.Validateur("chronologie")
    fait = {"schema_version": 1, "id": "naissance_enfant_1", "personne": "enfant_1",
            "sorte": "naissance", "debut": "1990-01-01", "attributs": {},
            "origine": "presume", "fiabilite": "estimee"}
    assert [(c.chemin, c.genre) for c in validateur.valider(fait, "fait")] == [
        ("fait.presomption", "manque")]
    fait["presomption"] = "naissance_des_enfants"
    assert validateur.valider(fait, "fait") == []
    fait["presomption"] = "intuition"
    assert [c.genre for c in validateur.valider(fait, "fait")] == ["erreur"]
    chronologie = {"schema_version": 1, "faits": [{**fait, "presomption": "naissance_des_enfants"}],
                   "liens": []}
    assert validateur.valider(chronologie, "chronologie") == []
