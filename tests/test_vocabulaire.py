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
