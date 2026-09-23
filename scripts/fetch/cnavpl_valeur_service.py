#!/usr/bin/env python3
"""La valeur de service du point des libéraux depuis 2004, chez la CNAVPL.

    python scripts/fetch/cnavpl_valeur_service.py

Les recueils statistiques que lit ``cnavpl_recueils.py`` ne donnent la valeur
du point que depuis 2021, et sous une seule forme : « la valeur du point est
fixée à 0,6540 au 1er janvier 2025 ». La caisse publie pourtant la série
entière, depuis la création du régime en points, dans une page de son site —
« Cotiser pour sa retraite », tableau « Valeur de service du point depuis
2004 » : vingt-quatre valeurs, chacune avec sa DATE D'EFFET. Faute d'elle, le
moteur ramenait par les prix la valeur de 2021 vers toutes les liquidations
antérieures, et prolongeait celle de 2025 au-delà.

**LA DATE D'EFFET COMPTE, ET LA SÉRIE L'ÉCRIT.** La valeur a changé au
1er janvier jusqu'en 2008, au 1er septembre en 2008, au 1er avril de 2009 à
2013, au 1er octobre de 2014 à 2017, de nouveau au 1er janvier depuis 2019 —
et deux fois en 2022, le 1er janvier puis le 1er juillet, avec la
revalorisation anticipée de 4 %. Le dépôt retient pour chaque année la valeur
EN VIGUEUR AU 31 DÉCEMBRE, règle de lecture de ``valeurs_point.csv`` : c'est
0,6027 € en 2022, quand le recueil de cette année-là, qui date sa phrase du
1er janvier, en donnait 0,5795.

**DEUX RECOUPEMENTS, ET LE SCRIPT S'ARRÊTE SI L'UN ÉCHOUE.** L'article D. 643-1
du code de la sécurité sociale fixait lui-même la valeur à ses débuts —
« 0,484 Euros » dans sa rédaction de 2004 (LEGIARTI000006738137), « 0,493
euros pour les prestations servies au titre de l'année 2005 » ensuite
(LEGIARTI000006738138) — ; la page doit les rendre. Et quand
``data/brut/cnavpl_recueils.json`` est là, la valeur en vigueur au 1er janvier
de chaque recueil doit être celle que le recueil imprime. Deux publications du
même producteur, un texte réglementaire : ce qui entre ici a été lu trois fois.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_locale import lire_ou_telecharger  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = "https://www.cnavpl.fr/preparer-sa-retraite/"
SORTIE = RACINE / "data" / "brut" / "cnavpl_valeur_service.json"
RECUEILS = RACINE / "data" / "brut" / "cnavpl_recueils.json"

MOIS = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
        "novembre": 11, "décembre": 12}

#: Une ligne du tableau, une fois le HTML réduit à son texte : « Au 1er
#: septembre 2008 0.5220 ».
LIGNE = re.compile(
    r"Au\s+1(?:er)?\s+(?P<mois>[a-zéû]+)\s+(?P<annee>\d{4})\s+(?P<valeur>\d+[.,]\d+)")

#: La valeur que D. 643-1 écrivait en toutes lettres, avant que la caisse ne
#: la fixe seule.
ANCRES_REGLEMENTAIRES = {
    2004: (0.484, "D. 643-1, rédaction de 2004 (LEGIARTI000006738137)"),
    2005: (0.493, "D. 643-1, rédaction de 2005 (LEGIARTI000006738138)"),
}


def _telecharger(url: str) -> bytes:
    demande = urllib.request.Request(url, headers={"User-Agent": "retraite-notionnelle/0.1"})
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return reponse.read()


def texte_visible(page: bytes) -> str:
    """Le texte de la page, balises et scripts ôtés, espaces réduits."""
    source = page.decode("utf-8", errors="replace")
    source = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", source)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", source)))


def valeurs_datees(texte: str) -> dict[date, float]:
    """Les lignes du tableau « Valeur de service du point depuis 2004 »."""
    debut = texte.upper().find("VALEUR DE SERVICE DU POINT DEPUIS")
    if debut < 0:
        raise ValueError("le tableau « Valeur de service du point depuis 2004 » est absent")
    lu: dict[date, float] = {}
    for ligne in LIGNE.finditer(texte[debut:debut + 4000]):
        mois = MOIS.get(ligne.group("mois").lower())
        if mois is None:
            raise ValueError(f"mois illisible : {ligne.group(0)!r}")
        lu[date(int(ligne.group("annee")), mois, 1)] = float(
            ligne.group("valeur").replace(",", "."))
    if not lu:
        raise ValueError("aucune ligne lue dans le tableau")
    return lu


def en_vigueur(dates: dict[date, float], jour: date) -> float | None:
    anterieures = [d for d in dates if d <= jour]
    return dates[max(anterieures)] if anterieures else None


def controler(dates: dict[date, float]) -> list[str]:
    """Les incohérences qui empêchent d'écrire ; vide si tout concorde."""
    erreurs = []
    ordonnees = sorted(dates)
    for avant, apres in zip(ordonnees, ordonnees[1:]):
        if dates[apres] < dates[avant]:
            erreurs.append(f"la valeur recule du {avant} ({dates[avant]}) "
                           f"au {apres} ({dates[apres]})")
    for annee, (valeur, texte) in ANCRES_REGLEMENTAIRES.items():
        lue = en_vigueur(dates, date(annee, 12, 31))
        if lue is None or abs(lue - valeur) > 5e-5:
            erreurs.append(f"{annee} : la page donne {lue}, {texte} écrit {valeur}")
    if RECUEILS.exists():
        serie = json.loads(RECUEILS.read_text(encoding="utf-8"))["serie"]
        for cle, valeur in sorted(serie.items()):
            regime, annee, mesure = cle.split("|")
            if mesure != "valeur_service":
                continue
            lue = en_vigueur(dates, date(int(annee), 1, 1))
            if lue is None or abs(lue - valeur) > 5e-5:
                erreurs.append(f"1er janvier {annee} : la page donne {lue}, "
                               f"le recueil statistique {valeur}")
    return erreurs


def main() -> int:
    page = lire_ou_telecharger(URL, _telecharger, nom_local="cnavpl_preparer_sa_retraite.html")
    dates = valeurs_datees(texte_visible(page))
    erreurs = controler(dates)
    if erreurs:
        for erreur in erreurs:
            print(f"INCOHÉRENT  {erreur}", file=sys.stderr)
        print("rien n'est écrit", file=sys.stderr)
        return 1
    premiere, derniere = min(dates).year, max(dates).year
    serie = {
        f"cnavpl|{annee}|valeur_service": en_vigueur(dates, date(annee, 12, 31))
        for annee in range(premiere, derniere + 1)
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": URL,
        "recupere_le": date.today().isoformat(),
        "note": "valeur de service du point du régime de base des professions "
                "libérales, tableau « Valeur de service du point depuis 2004 » ; "
                "chaque année porte la valeur en vigueur au 31 décembre",
        "valeurs_datees": {d.isoformat(): v for d, v in sorted(dates.items())},
        "recoupe_avec": ["D. 643-1 (2004, 2005)"]
                        + (["recueils statistiques CNAVPL"] if RECUEILS.exists() else []),
        "serie": serie,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    for d, v in sorted(dates.items()):
        print(f"OK      {d:%d/%m/%Y} : {v:.4f} €")
    print(f"\n{len(serie)} valeurs annuelles ({premiere}-{derniere}) écrites dans "
          f"{SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
