#!/usr/bin/env python3
"""Le scénario 1 confronté à TRAJECTOiRE (DREES), versions 3, de bout en bout.

    python scripts/confronter_trajectoire.py            # exécute R, confronte, vérifie
    python scripts/confronter_trajectoire.py --sorties DOSSIER   # relit des sorties de R
    python scripts/confronter_trajectoire.py --figer    # récrit la référence
    python scripts/confronter_trajectoire.py --epingle  # imprime le commit épinglé

À quoi il sert. `scripts/fetch/trajectoire.py` a figé, le 5 octobre 2026, les
sorties de TRAJECTOiRE 1.1.2 dans `tests/temoins/trajectoire.json`, depuis le
poste du propriétaire. Ce script-ci rejoue la même confrontation sur une
version 3 (la 3.3.2 du 20 novembre 2026, qui porte la loi du 30 décembre 2025,
les cas types 12 et 13 du COR — l'exploitant agricole et le médecin libéral —,
la complémentaire de la CARMF en points et l'ASV), sans poste : le workflow
`.github/workflows/trajectoire.yml` installe R et TRAJECTOiRE à part, lance ce
script chaque semaine, et prévient quand un accord se rompt — qu'une version
nouvelle de TRAJECTOiRE s'écarte du dépôt, ou que le dépôt s'écarte d'elle.

Ce qu'il fait. Il écrit les carrières du dépôt en tables de TRAJECTOiRE, lance
`scripts/fetch/trajectoire_3.R`, en tire le témoin (`trajectoire.temoin`),
rejoue chaque requête dans le scénario 1 et mesure l'écart de chaque quantité
avec les fonctions de `tests/test_trajectoire.py`, étendues aux régimes que les
versions 3 ont fait naître. Chaque quantité est `concorde`, à sa tolérance, ou
`ecart`. Il compare ensuite à la référence, `tests/temoins/trajectoire_3/
ecarts.json` : une quantité qui concordait et s'écarte est une RUPTURE, et le
script sort en erreur.

Ce qu'il ne fait pas. Il ne tranche rien : un écart avec TRAJECTOiRE n'est pas
une erreur du dépôt, seul le texte tranche (registre, `trajectoire`). Il ne
touche pas au témoin d'octobre ni à son test. Le code de TRAJECTOiRE n'entre
pas au dépôt (EUPL) : seules ses sorties, avec leur origine.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
sys.path.insert(0, str(RACINE / "tests"))
sys.path.insert(0, str(RACINE / "src"))

import trajectoire  # noqa: E402  (les tables d'entrée et le témoin)
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

DOSSIER = RACINE / "tests" / "temoins" / "trajectoire_3"
REFERENCE = DOSSIER / "ecarts.json"
TEMOIN = DOSSIER / "temoin.json"
SCRIPT_R = RACINE / "scripts" / "fetch" / "trajectoire_3.R"

#: La version épinglée : celle de la référence. Le workflow l'installe, et
#: installe aussi la dernière étiquette publiée quand elle en diffère.
ETIQUETTE = "v3.3.2"
COMMIT = "ce13fe743f138388d6944589033bb7f3f99e8700"
VERSION_COMMIT = "trajectoire v3.3.2 (20 novembre 2026)"
LEGISLATION = ("celle que la version 3.3.2 porte : la loi du 14 avril 2023 et la loi du "
               "30 décembre 2025, qui en suspend le calendrier ; paramètres projetés "
               "au-delà des valeurs connues, sur les hypothèses du COR de 2026")

#: Les caisses que les versions 3 ajoutent, rangées sous le régime du dépôt.
CAISSES_AJOUTEES = {
    "CNAVPL": "cnavpl",
    "CARMF complementaire": "carmf_complementaire",
    "CARMF sur-complementaire": "asv_conventionnes",
    "MSA exploitant": "msa_non_salaries",
    "MSA exploitant complementaire": "msa_rco",
}
#: Les familles que `test_trajectoire.ecarts_du_cas` confronte déjà, ou dont il
#: confronte les points et la valeur plutôt que le montant.
FAMILLES_D_OCTOBRE = ("regime_general", "fonction_publique", "rafp", "complementaires")
#: La tolérance des quantités ajoutées : celle des montants d'octobre, 0,5 %.
TOLERANCE_AJOUTEE = 0.005
#: En deçà, un écart qui bouge n'a pas bougé.
SEUIL_DEPLACEMENT = 0.002


# ---------------------------------------------------------------------------
# R, une fois
# ---------------------------------------------------------------------------

def executer(dossier: Path) -> Path:
    """Les tables d'entrée, puis `trajectoire_3.R` : le dossier de ses sorties."""
    salaires = trajectoire.destinie_2.salaires_des_cas(trajectoire.CARRIERES)
    for nom, lignes in trajectoire.tables_depot(salaires).items():
        trajectoire._ecrire_csv(dossier / f"{nom}.csv", lignes, trajectoire.COLONNES[nom])
    (dossier / "options.json").write_text(json.dumps({
        "generations": list(trajectoire.GENERATIONS), "hypSmpt": trajectoire.HYP_SMPT,
    }), encoding="utf-8")
    sorties = dossier / "sorties"
    print("TRAJECTOiRE : les cas types du COR et les carrières du dépôt…", flush=True)
    # R se lance hors du dépôt : le paquet écrit sa configuration à la racine
    # du projet qu'il trouve.
    fini = subprocess.run(["Rscript", str(SCRIPT_R), str(dossier), str(sorties)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=dossier)
    if fini.returncode != 0:
        raise RuntimeError(f"TRAJECTOiRE a échoué :\n{fini.stdout[-3000:]}\n"
                           f"{fini.stderr[-3000:]}")
    return sorties


def temoin_des_sorties(sorties: Path) -> dict:
    """Le témoin de `trajectoire.py`, sous la version que R dit avoir chargée."""
    tables = {f.stem: trajectoire._lire_csv(f) for f in sorted(sorties.glob("*.csv"))}
    versions = json.loads((sorties / "versions.json").read_text(encoding="utf-8"))
    document = trajectoire.temoin(tables, versions)
    installee = versions["trajectoire"]
    epinglee = installee == ETIQUETTE.removeprefix("v")
    document["commit"] = COMMIT if epinglee else "voir la version"
    document["version"] = (f"{installee} (DESCRIPTION)"
                           + (f" ; commit « {VERSION_COMMIT} »" if epinglee else ""))
    document["origine"] = (
        "Sorties de TRAJECTOiRE, exécuté à part par scripts/confronter_trajectoire.py et "
        "scripts/fetch/trajectoire_3.R ; le code de TRAJECTOiRE n'entre pas au dépôt. Les "
        "chiffres ci-dessous sont ses résultats, publiés sous sa licence, avec leur "
        "origine. Les cas types du COR sont construits par la fonction que le paquet "
        "exporte (lancerCasTypesCor), sur les hypothèses du COR qu'il livre.")
    document["legislation"]["dit"] = LEGISLATION if epinglee else "celle de la version"
    document["options"]["mode"] = "cas-types (lancerCasTypesCor, sans rapport ni classeur)"
    # La date de l'exécution ferait un témoin différent chaque semaine.
    del document["execute_le"]
    return document


# ---------------------------------------------------------------------------
# Les écarts
# ---------------------------------------------------------------------------

def _statut(test, quantite: str, ecart: float) -> str:
    if quantite in test.TOLERANCES or quantite.removeprefix("points_") in test.ECARTS_DES_POINTS:
        return "ecart" if test._hors_de(quantite, ecart) else "concorde"
    return "ecart" if abs(ecart) > TOLERANCE_AJOUTEE + 1e-12 else "concorde"


def _arrondi(ecart: float) -> float | None:
    """L'écart au dix-millième ; aucun, quand TRAJECTOiRE ne sert rien là où le
    dépôt sert (l'écart relatif n'a pas de sens, le statut reste « ecart »)."""
    return None if ecart in (float("inf"), float("-inf")) else round(ecart, 4)


def _signe(ecart: float | None) -> str:
    return "sans objet" if ecart is None else f"{ecart:+.4f}"


def _mensuel(annuel: float) -> float:
    return round(annuel / 12, 2)


def confronter(document: dict) -> dict:
    """Chaque quantité de chaque cas : les deux valeurs quand ce sont des
    montants (mensuels, bruts), l'écart et son statut."""
    import test_trajectoire as test  # (pytest et le pont : à l'usage seulement)

    test.CAISSES.update(CAISSES_AJOUTEES)
    saisies = test.Saisies()
    cas_confrontes: dict[str, dict] = {}
    for code, cas in document["cas"].items():
        depot = test.mesures_du_depot(saisies, cas["requete"])
        traj = test.mesures_de_trajectoire(cas)
        montants = test.montants_confrontes(cas)
        # Le dépôt ne dit ni durée requise ni taux à qui n'a de base qu'en
        # points : ces deux quantités ne s'y confrontent pas.
        en_points = not depot["trimestres_requis"]
        ecarts = test.ecarts_du_cas(depot, traj, montants)
        if en_points:
            ecarts.pop("trimestres_requis", None)
            ecarts.pop("taux", None)
        quantites = {q: {"ecart": _arrondi(e), "statut": _statut(test, q, e)}
                     for q, e in ecarts.items()}
        # Ce que la confrontation à la version 1.1.2 avait déclaré, avec sa
        # cause (`test_trajectoire.ECARTS`) : l'écart y est-il encore ?
        for quantite, valeur in quantites.items():
            if (code, quantite) in test.ECARTS:
                bas, haut, _ = test.ECARTS[code, quantite]
                valeur["declare_en_octobre"] = (
                    "dans sa borne" if bas - 1e-9 <= ecarts[quantite] <= haut + 1e-9
                    else "hors de sa borne")
        if montants:
            familles = sorted(set(depot["montants"]) | set(traj["montants"]))
            for famille in familles:
                d, t = depot["montants"].get(famille, 0.0), traj["montants"].get(famille, 0.0)
                if famille in quantites:
                    quantites[famille].update(depot=_mensuel(d), trajectoire=_mensuel(t))
                elif famille not in FAMILLES_D_OCTOBRE:
                    ecart = test._relatif(d, t)
                    quantites[famille] = {
                        "depot": _mensuel(d), "trajectoire": _mensuel(t),
                        "ecart": _arrondi(ecart), "statut": _statut(test, famille, ecart)}
            for caisse, regime in CAISSES_AJOUTEES.items():
                if caisse in traj["points"] and regime in depot["points"]:
                    ecart = test._relatif(depot["points"][regime], traj["points"][caisse])
                    quantites[f"points_{regime}"] = {
                        "depot": round(depot["points"][regime], 2),
                        "trajectoire": round(traj["points"][caisse], 2),
                        "ecart": _arrondi(ecart),
                        "statut": _statut(test, f"points_{regime}", ecart)}
            total_d = somme_ordonnee(depot["montants"].values()) + somme_ordonnee(depot["majorations"].values())
            total_t = somme_ordonnee(traj["montants"].values()) + somme_ordonnee(traj["majorations"].values())
            ecart = test._relatif(total_d, total_t)
            quantites["pension_totale"] = {
                "depot": _mensuel(total_d), "trajectoire": _mensuel(total_t),
                "ecart": _arrondi(ecart), "statut": _statut(test, "pension_totale", ecart)}
        cas_confrontes[code] = {
            "objet": cas["objet"],
            "depart": cas["trajectoire"]["liquidation"]["date"],
            "montants_confrontes": montants,
            "quantites": dict(sorted(quantites.items())),
        }
    return {
        "modele": "TRAJECTOiRE",
        "version": document["version"],
        "lecture": (
            "ecart : dépôt moins TRAJECTOiRE, en trimestres pour les durées, en années "
            "pour l'âge, relatif pour le reste (voir tests/test_trajectoire.py, "
            "ecarts_du_cas) ; depot et trajectoire : pensions mensuelles brutes, hors "
            "majoration pour enfants, en euros du départ. Un écart n'est pas une erreur "
            "du dépôt : seul le texte tranche."),
        "cas": cas_confrontes,
    }


def comparer(reference: dict, mesure: dict) -> dict[str, list[str]]:
    """Ce qui a bougé depuis la référence : les ruptures (une quantité qui
    concordait s'écarte, ou n'est plus mesurée), les accords nouveaux, les
    écarts déplacés, ce qui est nouveau."""
    bilan: dict[str, list[str]] = {"ruptures": [], "accords": [], "deplaces": [], "nouveaux": []}
    for code, cas in mesure["cas"].items():
        avant = reference["cas"].get(code)
        if avant is None:
            bilan["nouveaux"].append(f"{code} : cas nouveau")
            continue
        for quantite, valeur in cas["quantites"].items():
            ancien = avant["quantites"].get(quantite)
            ligne = f"{code}, {quantite} : {_signe(valeur['ecart'])}"
            if ancien is None:
                bilan["nouveaux"].append(ligne + f" ({valeur['statut']})")
            elif ancien["statut"] == "concorde" and valeur["statut"] == "ecart":
                bilan["ruptures"].append(ligne + f", concordait ({_signe(ancien['ecart'])})")
            elif ancien["statut"] == "ecart" and valeur["statut"] == "concorde":
                bilan["accords"].append(ligne + f", s'écartait ({_signe(ancien['ecart'])})")
            elif None in (valeur["ecart"], ancien["ecart"]):
                if valeur["ecart"] != ancien["ecart"]:
                    bilan["deplaces"].append(ligne + f", était {_signe(ancien['ecart'])}")
            elif abs(valeur["ecart"] - ancien["ecart"]) > SEUIL_DEPLACEMENT:
                bilan["deplaces"].append(ligne + f", était {_signe(ancien['ecart'])}")
    for code, avant in reference["cas"].items():
        apres = mesure["cas"].get(code, {"quantites": {}})["quantites"]
        for quantite, ancien in avant["quantites"].items():
            if quantite not in apres and ancien["statut"] == "concorde":
                bilan["ruptures"].append(f"{code}, {quantite} : n'est plus mesuré, concordait")
    return bilan


TITRES = {
    "ruptures": "Accords rompus",
    "accords": "Accords nouveaux",
    "deplaces": "Écarts déplacés",
    "nouveaux": "Quantités nouvelles",
}


def rapport(mesure: dict, bilan: dict[str, list[str]] | None) -> str:
    """Le compte rendu, en Markdown : le bilan contre la référence, puis les
    écarts de chaque cas."""
    lignes = [f"# Le scénario 1 confronté à TRAJECTOiRE {mesure['version']}", ""]
    total = somme_ordonnee(len(c["quantites"]) for c in mesure["cas"].values())
    hors = somme_ordonnee(v["statut"] == "ecart" for c in mesure["cas"].values()
               for v in c["quantites"].values())
    lignes += [f"{len(mesure['cas'])} cas, {total} quantités : {total - hors} concordent, "
               f"{hors} s'écartent.", ""]
    if bilan is not None:
        for cle, titre in TITRES.items():
            lignes += [f"## {titre} depuis la référence : {len(bilan[cle])}", ""]
            lignes += [f"- {ligne}" for ligne in bilan[cle]] + [""] * bool(bilan[cle])
    lignes += ["## Les écarts, cas par cas", "",
               "| cas | départ | quantité | dépôt | TRAJECTOiRE | écart |",
               "|---|---|---|---:|---:|---:|"]
    for code, cas in mesure["cas"].items():
        for quantite, v in cas["quantites"].items():
            if v["statut"] == "ecart":
                lignes.append(f"| {code} | {cas['depart']} | {quantite} | {v.get('depot', '')} "
                              f"| {v.get('trajectoire', '')} | {_signe(v['ecart'])} |")
    return "\n".join(lignes) + "\n"


def _ecrire(chemin: Path, document: dict) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True,
                       allow_nan=False) + "\n"
    chemin.write_bytes(texte.encode("utf-8"))


def main(arguments: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--sorties", type=Path, metavar="DOSSIER",
                         help="relit les sorties de R d'une exécution gardée")
    lecteur.add_argument("--figer", action="store_true",
                         help="récrit la référence et le témoin au lieu de vérifier")
    lecteur.add_argument("--resultats", type=Path, metavar="DOSSIER",
                         help="y écrit ecarts.json, temoin.json et rapport.md")
    lecteur.add_argument("--epingle", action="store_true",
                         help="imprime l'étiquette et le commit épinglés, sans rien exécuter")
    options = lecteur.parse_args(arguments)
    if options.epingle:
        print(ETIQUETTE, COMMIT)
        return 0
    dossier = None
    if options.sorties is None:
        if shutil.which("Rscript") is None:
            print("Rscript est introuvable : installer R et TRAJECTOiRE (voir le workflow "
                  "trajectoire.yml).", file=sys.stderr)
            return 2
        dossier = Path(tempfile.mkdtemp(prefix="trajectoire_"))
    try:
        document = temoin_des_sorties(options.sorties or executer(dossier))
    finally:
        if dossier is not None:
            shutil.rmtree(dossier, ignore_errors=True)
    mesure = confronter(document)
    bilan = None
    if REFERENCE.exists() and not options.figer:
        bilan = comparer(json.loads(REFERENCE.read_text(encoding="utf-8")), mesure)
    texte = rapport(mesure, bilan)
    if options.resultats:
        _ecrire(options.resultats / "ecarts.json", mesure)
        _ecrire(options.resultats / "temoin.json", document)
        (options.resultats / "rapport.md").write_text(texte, encoding="utf-8")
    if options.figer:
        _ecrire(REFERENCE, mesure)
        _ecrire(TEMOIN, document)
        print(f"{REFERENCE} : {len(mesure['cas'])} cas, référence récrite")
        return 0
    print(texte if bilan is None else texte.split("## Les écarts, cas par cas")[0])
    return 1 if bilan and bilan["ruptures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
