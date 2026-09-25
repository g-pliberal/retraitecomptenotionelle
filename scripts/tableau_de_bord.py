#!/usr/bin/env python3
"""Le tableau de bord : où en est le dépôt, ce qui ne va pas encore, ce qui reste à faire.

    python scripts/tableau_de_bord.py             # réécrit docs/etat.md
    python scripts/tableau_de_bord.py --verifier  # échoue si docs/etat.md est périmé
    python scripts/tableau_de_bord.py --cout      # le coût du travail, relevé sur git

Ce qu'il fait
-------------

``docs/etat.md`` répond à trois questions, et à elles seules : où en est-on, ce
qui ne va pas encore, ce qui reste à faire (``docs/architecture.md``, § 9.1).
Personne ne l'écrit à la main : ce script le fabrique depuis les registres
d'aujourd'hui — la veille, l'inventaire des régimes et leurs effectifs, les
exemples officiels, les réformes, les sources à explorer, la feuille de route —
et chaque nombre de la page est calculé ici. Une correction ne demande donc
qu'un geste : corriger le registre, puis relancer le script.
``tests/test_prose.py`` refuse une copie périmée.

À la phase 2, le tableau passera à la carte des règles, sans changer de
questions. Il part de la maquette qui a éprouvé l'architecture
(``docs/decisions/0001/tableau_de_bord.py``, § 14.7 de la note 0001).

Ce qu'il n'écrit pas
--------------------

Le coût du travail se relève sur l'historique git : ses chiffres changent à
chaque commit, et une page qui les porterait serait périmée dès le suivant. Il
s'affiche à la demande, par ``--cout``, et n'entre pas dans ``docs/etat.md``.
La page ne porte pas non plus sa date de fabrication : son histoire est celle
que git garde.
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import re
import statistics
import subprocess
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
PAGE = RACINE / "docs" / "etat.md"

#: Les caisses de l'enquête EACR de la DREES, rattachées aux régimes de
#: l'inventaire : c'est ce qui pèse la couverture par les retraités.
CAISSES = {
    "regime_general": ["cnav"], "msa_salaries": ["msa_salaries"],
    "agirc_arrco": ["agirc_arrco"], "ircantec": ["ircantec"], "cnracl": ["cnracl"],
    "fspoeie": ["fspoeie"], "rafp": ["erafp"],
    "fonction_publique_etat": ["fonction_publique_etat_civile",
                               "fonction_publique_etat_militaire"],
    "sncf": ["sncf", "sncf_coordination"], "ratp": ["ratp", "ratp_coordination"],
    "ieg": ["cnieg"], "marins": ["enim"], "mines": ["canssm"], "crpcen": ["crpcen"],
    "banque_de_france": ["banque_de_france"], "cavimac": ["cavimac"],
    "rci": ["rci_complementaire"], "cnavpl": ["cnavpl"], "cnbf": ["cnbf"],
    "cnbf_complementaire": ["cnbf_complementaire"],
    "msa_non_salaries": ["msa_exploitants"],
    "msa_rco": ["msa_exploitants_complementaire"],
}
#: Les sections complémentaires des libéraux sont de couverture mêlée : comptées à part.
MELEES = {"cnavpl_complementaire"}

#: Les limites de la veille, de la plus grave à la moins grave.
ORDRE_DES_LIMITES = {"manque": 0, "hors_modele": 1, "a_verifier": 2, "approximation": 3}

#: Les registres que le coût du travail compte comme écrits à la main.
REGISTRES = {
    "data/reference/legislation/veille.yaml",
    "data/reference/legislation/frontiere_contributive.yaml",
    "data/reference/prose/zones.yaml", "data/reference/site/affirmations.yaml",
    "data/reference/regimes/inventaire.yaml", "data/reference/legislation/reformes.yaml",
    "data/reference/regimes/pivots.yaml",
}
#: Les quatre fichiers que presque tout changement du moteur touche.
LOURDS = ["docs/feuille_de_route.md", "docs/limites.md",
          "data/reference/legislation/veille.yaml", "README.md"]


# --------------------------------------------------------------------------
# Lire.
# --------------------------------------------------------------------------


def lire_yaml(chemin: str):
    return yaml.safe_load((RACINE / chemin).read_text(encoding="utf-8"))


def lire_csv(chemin: str) -> list[dict]:
    """Les lignes d'un CSV du dépôt, sans les commentaires de son en-tête."""
    texte = (RACINE / chemin).read_text(encoding="utf-8")
    lignes = "".join(l for l in texte.splitlines(keepends=True) if not l.startswith("#"))
    return list(csv.DictReader(io.StringIO(lignes)))


def phrase(texte, n: int = 170) -> str:
    """La première phrase d'un texte de registre, coupée à n signes."""
    t = " ".join(str(texte or "").split())
    t = re.split(r"(?<=[.;])\s", t, maxsplit=1)[0].rstrip(" ;")
    if t.endswith(":"):
        t = t[:-1].rstrip() + " …"
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def premiere(texte) -> str:
    """La première proposition d'un texte, jusqu'au premier point, point-virgule ou deux-points."""
    return re.split(r"(?<=[.;:])\s", " ".join(str(texte or "").split()), maxsplit=1)[0]


def grandeur(v) -> str:
    """Une grandeur d'exemple officiel, telle qu'une cellule la montre."""
    if isinstance(v, dict):
        return ", ".join(f"{k} {grandeur(x)}" for k, x in v.items())
    if isinstance(v, bool):
        return "oui" if v else "non"
    if isinstance(v, float):
        return f"{v:g}".replace(".", ",")
    return str(v)


def pct(a: float, b: float) -> str:
    return f"{100 * a / b:.0f} %" if b else "—"


def milliers(n: float) -> str:
    """Un effectif, les milliers séparés par l'espace fine insécable, comme la maquette."""
    return f"{n:,.0f}".replace(",", "\u202f")


def virgule(x: float, decimales: int = 1) -> str:
    return f"{x:.{decimales}f}".replace(".", ",")


# --------------------------------------------------------------------------
# La page.
# --------------------------------------------------------------------------


def page() -> str:
    """``docs/etat.md``, tel que les registres le disent aujourd'hui."""
    veille = lire_yaml("data/reference/legislation/veille.yaml")["entrees"]
    inventaire = lire_yaml("data/reference/regimes/inventaire.yaml")["inventaire"]
    exemples = lire_yaml("tests/temoins/exemples_officiels.yaml")["exemples"]
    reformes = lire_yaml("data/reference/legislation/reformes.yaml")["reformes"]
    sources = lire_yaml("data/sources_a_explorer.yaml")["sources"]
    effectifs = lire_csv("data/reference/regimes/effectifs_retraites.csv")
    parts_derives = lire_csv("data/reference/macro/part_droits_derives.csv")
    feuille = (RACINE / "docs" / "feuille_de_route.md").read_text(encoding="utf-8")
    # Les actions closes sont dans l'archive de la feuille de route (§ 9.3).
    archive = RACINE / "docs" / "archives" / "feuille_de_route.md"
    closes = archive.read_text(encoding="utf-8") if archive.is_file() else ""

    # Les effectifs de la dernière année, par caisse (DREES, EACR).
    annee_eff = max(r["annee"] for r in effectifs)
    eff = {r["caisse"]: float(r["effectifs"]) for r in effectifs if r["annee"] == annee_eff}
    par_code = {r["code"]: r for r in inventaire}
    # Un code renommé dans l'inventaire ne fait pas tomber la page : il y est dit.
    caisses = {code: cs for code, cs in CAISSES.items() if code in par_code}
    codes_perdus = sorted(set(CAISSES) - set(caisses))
    rattachees = {c for cs in caisses.values() for c in cs}

    # ---- 1. l'avancement
    couv = collections.Counter(r["couverture"] for r in inventaire)
    poids = collections.Counter()
    for code, cs in caisses.items():
        for c in cs:
            poids[par_code[code]["couverture"]] += eff.get(c, 0)
    for c in MELEES:
        poids["mêlée"] += eff.get(c, 0)
    non_rattachees = sorted(set(eff) - rattachees - MELEES - {"tous_regimes"})
    total_caisses = sum(poids.values())

    etat = collections.Counter(r["etat"] for r in veille)
    avec_exemple = sum(1 for r in veille if r.get("temoins"))
    # Un exemple que le modèle ne reproduit pas entre quand même, en écart
    # connu (docs/architecture.md, § 9.2).
    ecarts_connus = [e for e in exemples if e.get("ecart_connu")]
    code_source = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for motif in ("src/**/*.py", "moteur/js/*.js") for p in sorted(RACINE.glob(motif)))
    citees = sum(1 for r in veille if r["id"] in code_source)

    actions = re.findall(r"^### (\d+)\. (.*?) — `([^`]*)`", closes + "\n" + feuille, re.M)
    statuts_actions = collections.Counter(s for _, _, s in actions)

    # La part de la réversion la même année que les effectifs.
    derniere_part = next(r for r in parts_derives if r["annee"] == annee_eff)

    # ---- 2. les limites
    partiels = sorted(
        ((sum(eff.get(c, 0) for c in cs), par_code[code])
         for code, cs in caisses.items() if par_code[code]["couverture"] == "partiel"),
        key=lambda x: -x[0])
    partiels_sans_effectif = [r for r in inventaire
                              if r["couverture"] == "partiel" and r["code"] not in caisses]
    limites_veille = sorted((r for r in veille if r["etat"] in ORDRE_DES_LIMITES),
                            key=lambda r: (ORDRE_DES_LIMITES[r["etat"]], r["id"]))
    non_appliquees = [r for r in reformes if r.get("non_appliquee")]
    approchees = [r for r in veille if r["etat"] == "approximation"]
    # Un effet écrit à l'imparfait raconte l'erreur corrigée, pas ce qui reste.
    a_l_imparfait = [r["id"] for r in approchees
                     if re.search(r"\b\w+(ait|aient)\b", premiere(r.get("effet")))]

    # ---- 3. ce qui reste à faire
    statut_sources = collections.Counter(s["statut"] for s in sources)
    a_explorer = [s for s in sources if s["statut"] == "a_explorer"]
    couverture_de = {r["code"]: r["couverture"] for r in inventaire}
    utiles = collections.defaultdict(list)       # sources qui touchent un régime partiel
    for s in a_explorer:
        for reg in s.get("regimes") or []:
            if couverture_de.get(reg) == "partiel":
                utiles[reg].append(s["id"])
    sans_regime = sum(1 for s in a_explorer if not s.get("regimes"))
    n_utiles = len({i for ids in utiles.values() for i in ids})
    en_cours = [(n, t) for n, t, s in actions if s == "en cours"]
    hors_champ = [r for r in inventaire if r["couverture"] == "hors_champ"]

    L: list[str] = []
    w = L.append
    w("# État du dépôt")
    w("")
    w("*Le tableau de bord (`docs/architecture.md`, § 9.1). Fabriqué par "
      "`scripts/tableau_de_bord.py` depuis les registres d'aujourd'hui : aucun nombre "
      "n'y est écrit à la main. Pour le corriger, on corrige le registre, puis on relance "
      "le script ; un test refuse une copie périmée.*")
    w("")
    w("## 1. Où en est-on")
    w("")
    w("**Les régimes.** L'inventaire en compte "
      f"{len(inventaire)} : {couv['modelise']} modélisés, {couv['partiel']} partiels, "
      f"{couv['hors_champ']} hors champ, {couv['routage']} routages.")
    w("")
    w(f"Pesés par leurs retraités de droit direct ({annee_eff}, enquête EACR de la DREES, "
      "où un polypensionné compte dans chacune de ses caisses) :")
    w("")
    w("| Couverture | Retraités-caisses | Part |")
    w("|---|---|---|")
    for cle, nom in (("modelise", "régime modélisé"), ("partiel", "régime partiel"),
                     ("mêlée", "sections libérales, couverture mêlée")):
        w(f"| {nom} | {milliers(poids[cle])} | {pct(poids[cle], total_caisses)} |")
    w("")
    w(f"*Modélisé ne veut pas dire exact* : les {etat.get('approximation', 0)} règles "
      "approchées de la veille touchent aussi des régimes modélisés (section 2).")
    w("")
    if non_rattachees:
        w(f"Caisses de l'enquête non rattachées à l'inventaire : {', '.join(non_rattachees)}.")
        w("")
    if codes_perdus:
        w("Régimes rattachés à l'enquête que l'inventaire ne porte plus : "
          f"{', '.join(codes_perdus)}.")
        w("")
    w(f"**Les règles suivies en veille** : {len(veille)}.")
    w("")
    w("| État | Règles |")
    w("|---|---|")
    for cle, nom in (("conforme", "conformes"), ("transcrit", "transcrites"),
                     ("approximation", "approchées"), ("hors_modele", "hors modèle"),
                     ("manque", "manquantes"), ("a_verifier", "à vérifier")):
        w(f"| {nom} | {etat.get(cle, 0)} |")
    w("")
    w(f"- Confrontées à au moins un exemple officiel : **{avec_exemple} sur {len(veille)}** "
      f"({len(exemples)} exemples : {len(exemples) - len(ecarts_connus)} reproduits, "
      + (f"{len(ecarts_connus)} en écart connu, section 2)." if ecarts_connus
         else "aucun en écart connu)."))
    w(f"- Citées dans le code par leur identifiant : **{citees} sur {len(veille)}**. "
      "Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.")
    w(f"- Réformes du calendrier : {len(reformes)}, dont {len(non_appliquees)} déclarées "
      "non appliquées.")
    w("")
    w("**Ce qui est hors du modèle.** La réversion, par exemple, pèse "
      f"{virgule(100 * float(derniere_part['part']))} % de la masse des prestations en "
      f"{derniere_part['annee']} (COR), et le modèle n'en calcule aucune.")
    w("")
    w(f"**La feuille de route** compte {len(actions)} actions : "
      + ", ".join(f"{n} {s}" for s, n in statuts_actions.most_common()) + ". "
      "Les closes sont dans son archive, `docs/archives/feuille_de_route.md` ; ce qui "
      "reste à faire est ailleurs, dispersé.")
    w("")
    w("## 2. Ce qui ne va pas encore")
    w("")
    w("**Les régimes partiels, du plus peuplé au moins peuplé**")
    w("")
    w("| Régime | Retraités | Ce qui manque |")
    w("|---|---|---|")
    for n, r in partiels:
        w(f"| {r['nom']} | {milliers(n)} | {phrase(r.get('manque'))} |")
    w("")
    w(f"Et {len(partiels_sans_effectif)} régimes partiels sans effectif dans l'enquête "
      "(outre-mer, sections libérales, régimes fermés…).")
    w("")
    w("**Les règles approchées, absentes ou à vérifier**, avec ce que le registre dit "
      "de leur effet :")
    w("")
    w("| Règle | État | Qui est touché |")
    w("|---|---|---|")
    for r in limites_veille:
        w(f"| `{r['id']}` | {r['etat']} | {phrase(r.get('effet'), 140)} |")
    w("")
    w(f"**Un état peut-être périmé.** Pour {len(a_l_imparfait)} des {len(approchees)} "
      "règles approchées, l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans "
      "dire ce qui reste. Le tableau ne peut pas savoir si elles sont encore approchées : "
      "la fiche séparera l'effet actuel de l'historique.")
    w("")
    if ecarts_connus:
        w("**Les exemples officiels que le modèle ne reproduit pas**, entrés en écart "
          "connu, avec la règle qui le déclare :")
        w("")
        w("| Exemple | Grandeur | Publié | Modèle | Règle |")
        w("|---|---|---|---|---|")
        for e in ecarts_connus:
            ecart = e["ecart_connu"]
            for cle, valeur in ecart["modele"].items():
                w(f"| `{e['id']}` | {cle} | {grandeur(e['attendu'][cle])} | "
                  f"{grandeur(valeur)} | `{ecart['veille']}` |")
    else:
        w("**Aucun exemple officiel en écart connu** : le modèle reproduit tous ceux que "
          "le dépôt a transcrits. Un exemple qu'il ne reproduirait pas entrerait quand même, "
          "et se lirait ici.")
    w("")
    w("## 3. Ce qui reste à faire, et par quoi commencer")
    w("")
    w(f"- **Les {len(en_cours)} actions en cours** de la feuille de route :")
    for n, t in en_cours:
        w(f"  - {n}. {t if len(t) <= 150 else t[:149].rstrip() + '…'}")
    w(f"- **Les sources à exploiter** : {statut_sources['a_explorer']} à explorer sur "
      f"{len(sources)} ({statut_sources['explore']} explorées, "
      f"{statut_sources['epuise']} épuisées). {n_utiles} d'entre elles visent un régime "
      "partiel, et pourraient le compléter :")
    for reg, ids in sorted(utiles.items(), key=lambda x: (-len(x[1]), x[0])):
        w(f"  - {par_code[reg]['nom']} : {len(ids)} source(s) "
          f"({', '.join(ids[:3])}{'…' if len(ids) > 3 else ''})")
    w(f"  - et {sans_regime} sources sans régime désigné.")
    w(f"- **Les règles sans exemple officiel** : {len(veille) - avec_exemple}.")
    w(f"- **Les régimes hors champ** : {len(hors_champ)}, chacun avec sa raison dans "
      "l'inventaire.")
    w("")
    w("## 4. Ce que ce tableau ne sait pas encore dire")
    w("")
    w("- **L'effet chiffré de chaque limite.** Les registres le disent en mots. Le pilote "
      "le mesurera, en neutralisant la règle sur les cas types pondérés.")
    w("- **La part des pensions qui ne passent que par des règles conformes.** Il faut "
      "pour cela que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit "
      "aux phases 4 et 5.")
    w("- **Ce que personne n'a encore noté.** Le dénominateur est aujourd'hui la mémoire "
      "des registres ; la liste de contrôle des textes (phase 2) en fera la loi elle-même.")
    w("- **La réorganisation.** Les règles du code qui ont leur fiche, et les registres "
      "devenus des vues, se compteront quand la carte existera (phase 2).")
    w("- **Les limites propres à une simulation.** Le site les montrera avec chaque "
      "résultat.")
    w("- **Le coût du travail** se relève sur l'historique git, et change à chaque "
      "commit : il s'affiche à la demande, par `python scripts/tableau_de_bord.py --cout`, "
      "avec la taille du dépôt — ses lignes, ses tests —, que la prose ne porte plus.")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# Le coût du travail, à la demande.
# --------------------------------------------------------------------------


def a_la_main(fichier: str) -> bool:
    """De la prose ou un registre, écrits à la main."""
    return (fichier.endswith(".md") and fichier != "docs/chiffrage_plf.md"
            or fichier in REGISTRES)


def cout(n: int = 400) -> str:
    """Ce que coûte un changement, relevé sur les ``n`` derniers commits."""
    journal = subprocess.run(
        ["git", "-C", str(RACINE), "log", "--format=@@%H", "--name-only", "-n", str(n)],
        capture_output=True, text=True, encoding="utf-8", check=True).stdout
    changes = [[l for l in b.strip().split("\n")[1:] if l] for b in journal.split("@@")[1:]]
    changes = [c for c in changes if c]
    L: list[str] = []
    w = L.append
    w("## Le coût du travail")
    w("")
    if not changes:
        w("Aucun commit à relever.")
        return "\n".join(L) + "\n"
    moteur = [c for c in changes if "src/retraite_notionnelle/scenarios/actuel.py" in c]
    w(f"Relevé sur les {len(changes)} derniers commits :")
    w("")
    w(f"- un commit touche en médiane {statistics.median(len(c) for c in changes):.0f} "
      "fichiers ;")
    if moteur:
        med = statistics.median(len(c) for c in moteur)
        main = virgule(statistics.mean(sum(1 for f in c if a_la_main(f)) for c in moteur))
        w(f"- un commit qui change le moteur du scénario 1 en touche {med:.0f} en médiane, "
          f"dont {main} de prose ou de registres écrits à la main (moyenne, sur "
          f"{len(moteur)} commits) ;")
    for f in LOURDS[:2]:
        touches = sum(1 for c in changes if f in c)
        w(f"- `{f}` est modifié dans {pct(touches, len(changes))} des commits ;")
    presents = [f for f in LOURDS if (RACINE / f).exists()]
    poids = sum((RACINE / f).stat().st_size for f in presents)
    w(f"- les {len(presents)} fichiers que presque tout changement du moteur touche "
      f"({', '.join('`' + f + '`' for f in presents)}) pèsent ensemble "
      f"{virgule(poids / 1e6)} Mo : aucune session ne peut les lire en entier.")
    return "\n".join(L) + "\n"


def taille() -> str:
    """Les chiffres qui décrivent le dépôt lui-même : la prose ne les porte
    plus, puisqu'ils changent à chaque session (docs/architecture.md, § 9.3)."""
    sys.path.insert(0, str(RACINE / "scripts"))
    from verifier_prose import sonde_lignes, sonde_tests

    moteur = sonde_lignes("src/retraite_notionnelle/scenarios/actuel.py")
    portage = sonde_lignes("moteur/js/*.js")
    return "\n".join([
        "## La taille du dépôt",
        "",
        f"- le moteur du scénario 1 : {milliers(moteur)} lignes dans "
        "`src/retraite_notionnelle/scenarios/actuel.py`, et "
        f"{milliers(portage)} dans le portage `moteur/js/` ; chaque changement du "
        "modèle se paie des deux côtés, puis dans les témoins ;",
        f"- la suite : {milliers(sonde_tests())} tests (`python -m pytest`).",
    ]) + "\n"


# --------------------------------------------------------------------------


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="échoue si docs/etat.md est périmé, sans rien écrire")
    analyseur.add_argument("--cout", action="store_true",
                           help="imprime le coût du travail, relevé sur l'historique git, "
                                "et la taille du dépôt")
    arguments = analyseur.parse_args()

    if arguments.cout:
        print(cout() + "\n" + taille(), end="")
        return 0
    voulu = page()
    actuel = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    if arguments.verifier:
        if voulu != actuel:
            print("docs/etat.md est périmé : lancer python scripts/tableau_de_bord.py",
                  file=sys.stderr)
            return 1
        print("le tableau de bord est à jour")
        return 0
    if voulu != actuel:
        PAGE.write_text(voulu, encoding="utf-8", newline="\n")
        print("docs/etat.md réécrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
