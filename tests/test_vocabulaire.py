"""Le vocabulaire du noyau : les dates qui décident, et les listes de valeurs.

``docs/architecture.md``, § 4.2 et § 13.1. Les quatre sortes de dates et les
étapes nommées sont au noyau : elles ne changent que par une note de décision,
et ce test les confronte au texte même de l'architecture. Les dates nommées et
les listes de valeurs s'allongent sans décision ; ce test en tient la forme.
"""

from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path

import yaml

from retraite_notionnelle.noyau import vocabulaire

RACINE = Path(__file__).resolve().parents[1]
ARCHITECTURE = (RACINE / "docs" / "architecture.md").read_text(encoding="utf-8")


def _section(titre: str) -> str:
    debut = ARCHITECTURE.index(titre)
    fin = ARCHITECTURE.index("\n### ", debut + len(titre))
    return ARCHITECTURE[debut:fin]


def _identifiant(texte: str) -> str:
    """« compléter tous régimes » → ``completer_tous_regimes``."""
    sans_accent = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]+", "_", sans_accent.lower()).strip("_")


def test_le_vocabulaire_tient():
    assert vocabulaire.controler() == []


def test_les_quatre_sortes_de_dates_sont_celles_de_l_architecture():
    """Le § 4.2 les nomme dans son tableau, dans cet ordre : la date d'un fait,
    d'un lien, d'une liquidation, et une date dérivée. La liste est fermée."""
    tableau = _section("### 4.2 Les dates qui décident")
    lues = re.findall(r"^\| \*\*(.+?)\*\*", tableau, re.M)
    assert lues == ["la date d'un fait", "la date d'un lien",
                    "la date d'une liquidation", "une date dérivée"], lues
    assert vocabulaire.SORTES_DE_DATES == ("fait", "lien", "liquidation", "derivee")
    assert tuple(vocabulaire.dates()["sortes"]) == vocabulaire.SORTES_DE_DATES


def test_les_dates_que_l_architecture_nomme_sont_au_vocabulaire():
    """`enfant.naissance`, `conjoint.deces`, `liquidation.date_effet` : le
    § 4.2 les donne en exemple, et l'annexe A borne ses versions sur deux
    d'entre elles."""
    nommees = re.findall(r"`([a-z_]+\.[a-z_]+)`", _section("### 4.2 Les dates qui décident"))
    assert nommees, "le § 4.2 ne nomme plus de date"
    manquantes = sorted(set(nommees) - set(vocabulaire.dates_nommees()))
    assert not manquantes, manquantes


def test_les_etapes_sont_celles_du_moteur():
    """Les étapes nommées sont au noyau (§ 13.1) : celles que les § 7.2 à 7.4
    décrivent, et l'échéancier lui-même, où vivent l'ordre et l'inscription
    des événements. Une étape s'y écrit en gras et en minuscules, en tête de
    puce : « L'état est un journal », en gras aussi, n'en est pas une."""
    decrites = set()
    for titre in ("### 7.2 Acquérir", "### 7.3 Liquider", "### 7.4 L'échéancier"):
        decrites |= {_identifiant(nom) for nom in
                     re.findall(r"^- \*\*([a-zé][^*]+)\*\* :", _section(titre), re.M)}
    assert len(decrites) == 9, decrites
    assert vocabulaire.liste("etapes") == decrites | {"echeancier"}


def test_une_liste_inconnue_est_une_erreur():
    import pytest

    with pytest.raises(KeyError):
        vocabulaire.liste("sortes_de_licornes")


def test_le_controle_refuse_ce_qui_sortirait_du_noyau(tmp_path):
    """Une cinquième sorte de date, une dérivée sans origine, une date bornée
    sur un nom inconnu, une valeur muette : le contrôle les dit toutes."""
    shutil.copytree(vocabulaire.VOCABULAIRE, tmp_path, dirs_exist_ok=True)
    dates = yaml.safe_load((tmp_path / "dates.yaml").read_text(encoding="utf-8"))
    dates["sortes"]["intuition"] = "une date qu'on devine"
    dates["dates"]["assure.retraite_revee"] = {"sorte": "derivee", "dit": "le jour qu'on voudrait"}
    dates["combinaisons_impossibles"].append({"date": "licorne.naissance", "apres": "assure.naissance"})
    (tmp_path / "dates.yaml").write_text(yaml.safe_dump(dates, allow_unicode=True), encoding="utf-8")
    valeurs = yaml.safe_load((tmp_path / "valeurs.yaml").read_text(encoding="utf-8"))
    valeurs["listes"]["faces"]["valeurs"]["muette"] = ""
    (tmp_path / "valeurs.yaml").write_text(yaml.safe_dump(valeurs, allow_unicode=True), encoding="utf-8")

    erreurs = vocabulaire.controler(tmp_path)
    assert any("sortes de dates" in e for e in erreurs), erreurs
    assert any("assure.retraite_revee" in e and "dérivée" in e for e in erreurs), erreurs
    assert any("licorne.naissance" in e for e in erreurs), erreurs
    assert any("muette" in e for e in erreurs), erreurs


#: Les présomptions que le § 5.6 donne pour celles d'aujourd'hui, et leur nom
#: au vocabulaire. La liste s'allonge sans décision ; celles-ci n'en sortent
#: que par une décision, puisque les résultats d'aujourd'hui en dépendent.
PRESOMPTIONS_DU_5_6 = {
    "enfants nés aux": "naissance_des_enfants",
    "radiation au 1er janvier suivant": "radiation_au_1er_janvier_suivant",
    "agent présumé en activité": "agent_en_activite",
    "pas d'accord des parents": "pas_d_accord_des_parents",
    "enfant élevé neuf ans": "enfant_eleve_neuf_ans",
    "interruption d'activité remplie par la mère seule": "interruption_d_activite_par_la_mere",
    "validation de l'Ircantec présumée demandée": "validation_ircantec_demandee",
}


def test_les_presomptions_du_5_6_sont_au_vocabulaire():
    """Chaque présomption que le § 5.6 énumère a son nom, sa valeur et sa
    raison au vocabulaire, et le § 5.6 n'en énumère pas d'autre."""
    section = _section("### 5.6 Les présomptions")
    puces = re.findall(r"^  - (.+?)(?: ;| \.|\.)?$", section, re.M)
    assert len(puces) == len(PRESOMPTIONS_DU_5_6), puces
    for debut, nom in PRESOMPTIONS_DU_5_6.items():
        assert any(p.startswith(debut) for p in puces), (debut, puces)
        assert nom in vocabulaire.presomptions(), nom


def test_une_presomption_pose_un_fait_ou_dit_qui_l_applique(tmp_path):
    """Sans valeur, sans raison, ni fait posé ni code qui l'applique, ou
    appliquée sans l'étape où son fait entrera : le contrôle le dit."""
    shutil.copytree(vocabulaire.VOCABULAIRE, tmp_path, dirs_exist_ok=True)
    valeurs = yaml.safe_load((tmp_path / "valeurs.yaml").read_text(encoding="utf-8"))
    liste = valeurs["listes"]["presomptions"]["valeurs"]
    liste["muette"] = {"dit": "une présomption sans rien"}
    liste["bavarde"] = {"dit": "une présomption qui fait tout", "valeur": 1,
                        "raison": "parce qu'il faut bien une raison écrite",
                        "pose": {"sorte": "naissance", "personne": "enfant"},
                        "appliquee_par": "partout"}
    liste["orpheline"] = {"dit": "une présomption appliquée", "valeur": 1,
                          "raison": "parce qu'il faut bien une raison écrite",
                          "appliquee_par": "quelque part"}
    liste["licorne"] = {"dit": "une présomption fantaisiste", "valeur": 1,
                        "raison": "parce qu'il faut bien une raison écrite",
                        "pose": {"sorte": "envol", "personne": "assure"}}
    (tmp_path / "valeurs.yaml").write_text(yaml.safe_dump(valeurs, allow_unicode=True),
                                           encoding="utf-8")
    erreurs = vocabulaire.controler(tmp_path)
    assert any("muette : sans valeur" in e for e in erreurs), erreurs
    assert any("muette : une présomption dit sa raison" in e for e in erreurs), erreurs
    assert any("bavarde" in e and "l'un des deux" in e for e in erreurs), erreurs
    assert any("orpheline" in e and "entrera_a" in e for e in erreurs), erreurs
    assert any("licorne" in e and "sorte du vocabulaire" in e for e in erreurs), erreurs
