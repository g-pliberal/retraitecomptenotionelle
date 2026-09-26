#!/usr/bin/env python3
"""La liste de contrôle des textes : les rédactions d'articles qui touchent les retraites.

    python scripts/textes.py                    # la liste : par statut, par texte, et le cliquet
    python scripts/textes.py --sans-statut css  # les rédactions sans statut d'un texte
    python scripts/textes.py --inscrire         # les rédactions nouvelles de l'index, « à examiner »
    python scripts/textes.py --poser            # une fois : la liste initiale, depuis l'index

``docs/architecture.md``, § 6.6 : la carte part des textes, pas de la mémoire.
Le périmètre est déclaré dans ``data/reference/textes/perimetre.yaml`` : les
codes, aux chapitres qui touchent les retraites ; tout article dont une fiche
de la carte cite une rédaction, avec toutes ses rédactions ; et, en entier,
tout décret, loi ou arrêté dont une fiche cite une rédaction. La liste est
``redactions.csv``, une ligne par rédaction ; ``textes.csv`` donne le titre de
chaque texte sous sa clé ; ``inscription.yaml`` dit jusqu'où l'index a été lu.

Le statut d'une rédaction ne s'écrit pas ici : il se lit dans les fiches
(``src/retraite_notionnelle/noyau/textes.py``). Ce script ne fait qu'apporter
les rédactions. ``--inscrire`` ajoute celles que l'index porte et que la liste
n'a pas encore — une loi parue depuis, un texte qu'une fiche vient de citer —
datées du jour, et donc « à examiner » : le cliquet des rédactions sans statut
ne monte jamais. Il met aussi à jour la fin des rédactions qu'une suivante a
remplacées. Il lit l'index LEGI du dépôt (``scripts/fetch/dila_index.py legi
--recuperer``, puis ``--mettre-a-jour``) ; les tests, eux, ne lisent que la
liste.
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

from retraite_notionnelle.noyau import carte, textes  # noqa: E402

DOSSIER = textes.TEXTES
EN_VIGUEUR = "2999-01-01"
MOIS = {m: i for i, m in enumerate(
    ("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
     "septembre", "octobre", "novembre", "decembre"), 1)}


def _simple(texte: str) -> str:
    sans_accent = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sans_accent.lower()).strip("_")


def cle_de(titre: str) -> str:
    """La clé d'un texte, tirée de son titre : ``decret_2003_1306``,
    ``loi_2023_270``, ``arrete_1970_12_30``, ou le titre d'un code."""
    simple = _simple(titre)
    numero = re.match(r"(decret|loi|arrete|ordonnance)_n_?(\d+)_(\d+)", simple)
    if numero:
        return f"{numero.group(1)}_{numero.group(2)}_{numero.group(3)}"
    datee = re.match(r"(arrete|decret)_du_(\d+)(?:er)?_([a-z]+)_(\d{4})", simple)
    if datee and datee.group(3) in MOIS:
        return f"{datee.group(1)}_{datee.group(4)}_{MOIS[datee.group(3)]:02d}_{int(datee.group(2)):02d}"
    return simple[:60].rstrip("_")


def _cle_d_article(article: str):
    """L351-4 avant L351-10 : les nombres se comparent en nombres."""
    return [(0, int(x)) if x.isdigit() else (1, x) for x in re.split(r"(\d+)", article or "")]


def _ligne(ident, cle, article, debut, fin, inscrite_le="") -> dict:
    return {"id": ident, "texte": cle, "article": article or "", "debut": debut or "",
            "fin": "" if fin in ("", None, EN_VIGUEUR) else fin, "inscrite_le": inscrite_le}


def selection(db, perimetre: dict, fiches: dict[str, dict]) -> tuple[dict[str, dict], dict[str, str]]:
    """Les rédactions du périmètre que l'index porte, par identifiant, et le
    titre de chaque texte, par clé."""
    lignes: dict[str, dict] = {}
    titres: dict[str, str] = {}
    codes = {code["titre"]: code for code in perimetre["codes"]}
    requete = "SELECT id, num, date, fin FROM doc WHERE titre = ? AND id LIKE 'LEGIARTI%'"
    for code in perimetre["codes"]:
        titres[code["cle"]] = code["titre"]
        motif = re.compile(code["articles"]) if code.get("articles") else None
        for ident, num, debut, fin in db.execute(requete, (code["titre"],)):
            if motif is None or motif.search(num or ""):
                lignes[ident] = _ligne(ident, code["cle"], num, debut, fin)
    if perimetre.get("textes_cites"):
        for ident in sorted(textes.citations(fiches)):
            trouve = db.execute("SELECT titre, num FROM doc WHERE id = ?", (ident,)).fetchone()
            if trouve is None:
                continue
            titre, num = trouve
            if titre in codes or titre.startswith("Code "):
                cle = codes[titre]["cle"] if titre in codes else cle_de(titre)
                rangs = db.execute(requete + " AND num = ?", (titre, num))
            else:
                cle = cle_de(titre)
                rangs = db.execute(requete, (titre,))
            if titres.get(cle, titre) != titre:
                raise ValueError(f"deux textes sous la clé {cle} : {titres[cle]!r} et {titre!r}")
            titres[cle] = titre
            for autre, numero, debut, fin in rangs:
                lignes.setdefault(autre, _ligne(autre, cle, numero, debut, fin))
    return lignes, titres


def ecrire(lignes: list[dict], titres: dict[str, str], source: str, jour: str) -> None:
    lignes = sorted(lignes, key=lambda l: (l["texte"], _cle_d_article(l["article"]),
                                           l["debut"], l["id"]))
    flux = io.StringIO()
    ecrivain = csv.DictWriter(flux, fieldnames=textes.COLONNES, lineterminator="\n")
    ecrivain.writeheader()
    ecrivain.writerows(lignes)
    (DOSSIER / "redactions.csv").write_text(flux.getvalue(), encoding="utf-8", newline="\n")
    flux = io.StringIO()
    ecrivain = csv.writer(flux, lineterminator="\n")
    ecrivain.writerow(["texte", "titre"])
    ecrivain.writerows(sorted(titres.items()))
    (DOSSIER / "textes.csv").write_text(flux.getvalue(), encoding="utf-8", newline="\n")
    (DOSSIER / "inscription.yaml").write_text(
        "# Écrit par scripts/textes.py : l'index LEGI sur lequel la liste a été lue\n"
        "# en dernier, et le jour de cette lecture.\n"
        f"index: \"{source}\"\n"
        f"lu_le: {jour}\n", encoding="utf-8", newline="\n")


def poser(db, source: str, jour: str) -> int:
    if (DOSSIER / "redactions.csv").exists():
        print("la liste est déjà posée : --inscrire y apporte les rédactions nouvelles",
              file=sys.stderr)
        return 1
    lignes, titres = selection(db, textes.perimetre(), carte.fiches())
    ecrire(list(lignes.values()), titres, source, jour)
    print(f"{len(lignes)} rédactions posées, de {len(titres)} textes. Poser le cliquet :"
          f" redactions_sans_statut: {len(textes.sans_statut())}")
    return 0


def inscrire(db, source: str, jour: str) -> int:
    actuelles = {l["id"]: l for l in textes.redactions()}
    connus = textes.titres()
    lignes, titres = selection(db, textes.perimetre(), carte.fiches())
    nouvelles = sorted(set(lignes) - set(actuelles))
    remplacees = 0
    for ident, ligne in lignes.items():
        if ident in actuelles:
            ancienne = actuelles[ident]
            if (ancienne["debut"], ancienne["fin"]) != (ligne["debut"], ligne["fin"]):
                remplacees += 1
            actuelles[ident] = {**ligne, "inscrite_le": ancienne["inscrite_le"]}
        else:
            actuelles[ident] = {**ligne, "inscrite_le": jour}
    ecrire(list(actuelles.values()), {**connus, **titres}, source, jour)
    print(f"{len(nouvelles)} rédactions nouvelles inscrites « à examiner », {remplacees} "
          f"dont les dates ont changé ; index lu : {source}")
    for ident in nouvelles[:20]:
        ligne = actuelles[ident]
        print(f"  + {ligne['texte']} {ligne['article']} ({ligne['debut']}) {ident}")
    return 0


def etat(sans_statut_de: str | None) -> int:
    lignes = textes.redactions()
    statuts = textes.statuts()
    par_texte = collections.defaultdict(collections.Counter)
    for ligne in lignes:
        par_texte[ligne["texte"]][statuts[ligne["id"]] or "sans_statut"] += 1
    total = collections.Counter(s or "sans_statut" for s in statuts.values())
    ordre = list(textes.STATUTS) + ["sans_statut"]
    print(f"{len(lignes)} rédactions, de {len(par_texte)} textes : "
          + ", ".join(f"{s} {total[s]}" for s in ordre if total[s]))
    cliquet = (textes.perimetre().get("cliquet") or {}).get("redactions_sans_statut")
    print(f"Le cliquet admet {cliquet} rédactions sans statut.\n")
    titres = textes.titres()
    for cle, compte in sorted(par_texte.items(), key=lambda x: -sum(x[1].values())):
        print(f"  {cle:<22} {sum(compte.values()):>5}  "
              + ", ".join(f"{s} {compte[s]}" for s in ordre if compte[s])
              + f"  — {titres.get(cle, '?')[:70]}")
    if sans_statut_de:
        print()
        for ligne in lignes:
            if ligne["texte"] == sans_statut_de and statuts[ligne["id"]] is None:
                print(f"  {ligne['article']:<14} {ligne['debut']} → {ligne['fin'] or 'en vigueur'}"
                      f"  {ligne['id']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--poser", action="store_true", help="pose la liste initiale")
    analyseur.add_argument("--inscrire", action="store_true",
                           help="apporte les rédactions nouvelles, « à examiner »")
    analyseur.add_argument("--sans-statut", metavar="TEXTE",
                           help="liste les rédactions sans statut de ce texte")
    analyseur.add_argument("--date", help="le jour de l'inscription (AAAA-MM-JJ)")
    analyseur.add_argument("--index", help="chemin de l'index LEGI")
    args = analyseur.parse_args(argv)
    if not (args.poser or args.inscrire):
        return etat(args.sans_statut)
    from dila_index import ouvrir_lecture

    jour = args.date or date.today().isoformat()
    db, source = ouvrir_lecture("legi", args.index)
    return poser(db, source, jour) if args.poser else inscrire(db, source, jour)


if __name__ == "__main__":
    sys.exit(main())
