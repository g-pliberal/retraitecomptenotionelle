"""Maquette du tableau de bord : l'avancement, les limites, ce qui reste à faire.

Fabriqué depuis les registres d'aujourd'hui, sans rien écrire dans le dépôt :
la veille, l'inventaire des régimes et leurs effectifs, les exemples
officiels, les réformes, les sources à explorer, la feuille de route. Chaque
nombre de la page est calculé ici ; aucun n'est écrit à la main.

    python docs/decisions/0001/tableau_de_bord.py . > /tmp/etat.md

Maquette laissée par la session qui a conçu l'architecture : la phase 0 en
tire `scripts/tableau_de_bord.py` (voir `phase_0.md`, à côté).
"""
import collections, csv, io, re, sys
from pathlib import Path
import yaml

DEPOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
DATE = sys.argv[2] if len(sys.argv) > 2 else "2026-09-25"


def lire_yaml(chemin):
    with open(DEPOT / chemin, encoding="utf-8") as f:
        return yaml.safe_load(f)


def lire_csv(chemin):
    with open(DEPOT / chemin, encoding="utf-8") as f:
        return list(csv.DictReader(io.StringIO("".join(l for l in f if not l.startswith("#")))))


def phrase(texte, n=170):
    """La première phrase d'un texte de registre, coupée à n signes."""
    t = " ".join(str(texte or "").split())
    t = re.split(r"(?<=[.;])\s", t, maxsplit=1)[0].rstrip(" ;")
    if t.endswith(":"):
        t = t[:-1].rstrip() + " …"
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def pct(a, b):
    return f"{100 * a / b:.0f} %" if b else "—"


def milliers(n):
    return f"{n:,.0f}".replace(",", " ")


# ---- les registres -----------------------------------------------------------
veille = lire_yaml("data/reference/legislation/veille.yaml")["entrees"]
inventaire = lire_yaml("data/reference/regimes/inventaire.yaml")["inventaire"]
exemples = lire_yaml("tests/temoins/exemples_officiels.yaml")["exemples"]
reformes = lire_yaml("data/reference/legislation/reformes.yaml")["reformes"]
sources = lire_yaml("data/sources_a_explorer.yaml")["sources"]
effectifs = lire_csv("data/reference/regimes/effectifs_retraites.csv")
parts_derives = lire_csv("data/reference/macro/part_droits_derives.csv")
feuille = (DEPOT / "docs/feuille_de_route.md").read_text(encoding="utf-8")

# Les effectifs de la dernière année, par caisse (DREES, EACR).
annee_eff = max(r["annee"] for r in effectifs)
eff = {r["caisse"]: float(r["effectifs"]) for r in effectifs if r["annee"] == annee_eff}

# Les caisses de l'enquête, rattachées aux régimes de l'inventaire.
CAISSES = {
    "regime_general": ["cnav"], "msa_salaries": ["msa_salaries"], "agirc_arrco": ["agirc_arrco"],
    "ircantec": ["ircantec"], "cnracl": ["cnracl"], "fspoeie": ["fspoeie"], "rafp": ["erafp"],
    "fonction_publique_etat": ["fonction_publique_etat_civile", "fonction_publique_etat_militaire"],
    "sncf": ["sncf", "sncf_coordination"], "ratp": ["ratp", "ratp_coordination"], "ieg": ["cnieg"],
    "marins": ["enim"], "mines": ["canssm"], "crpcen": ["crpcen"], "banque_de_france": ["banque_de_france"],
    "cavimac": ["cavimac"], "rci": ["rci_complementaire"], "cnavpl": ["cnavpl"],
    "cnbf": ["cnbf"], "cnbf_complementaire": ["cnbf_complementaire"],
    "msa_non_salaries": ["msa_exploitants"], "msa_rco": ["msa_exploitants_complementaire"],
}
par_code = {r["code"]: r for r in inventaire}
rattachees = {c for cs in CAISSES.values() for c in cs}
# Les sections complémentaires des libéraux sont de couverture mêlée : comptées à part.
MELEES = {"cnavpl_complementaire"}

# ---- 1. l'avancement ---------------------------------------------------------
couv = collections.Counter(r["couverture"] for r in inventaire)
poids = collections.Counter()
for code, caisses in CAISSES.items():
    for c in caisses:
        poids[par_code[code]["couverture"]] += eff.get(c, 0)
for c in MELEES:
    poids["mêlée"] += eff.get(c, 0)
non_rattachees = sorted(set(eff) - rattachees - MELEES - {"tous_regimes"})
total_caisses = sum(poids.values())

etat = collections.Counter(r["etat"] for r in veille)
avec_exemple = sum(1 for r in veille if r.get("temoins"))
code_source = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                        for motif in ("src/**/*.py", "moteur/js/*.js") for p in DEPOT.glob(motif))
citees = sum(1 for r in veille if r["id"] in code_source)

actions = re.findall(r"^### (\d+)\. (.*?) — `([^`]*)`", feuille, re.M)
statuts_actions = collections.Counter(s for _, _, s in actions)

# La part de la réversion la même année que les effectifs (la série va jusqu'en 2070).
derniere_part = next(r for r in parts_derives if r["annee"] == annee_eff)

# ---- 2. les limites ----------------------------------------------------------
partiels = []
for code, caisses in CAISSES.items():
    r = par_code[code]
    if r["couverture"] == "partiel":
        partiels.append((sum(eff.get(c, 0) for c in caisses), r))
partiels.sort(key=lambda x: -x[0])
partiels_sans_effectif = [r for r in inventaire if r["couverture"] == "partiel" and r["code"] not in CAISSES]

ORDRE = {"manque": 0, "hors_modele": 1, "a_verifier": 2, "approximation": 3}
limites_veille = sorted((r for r in veille if r["etat"] in ORDRE), key=lambda r: (ORDRE[r["etat"]], r["id"]))
non_appliquees = [r for r in reformes if r.get("non_appliquee")]
# Un effet écrit à l'imparfait raconte l'erreur corrigée, pas ce qui reste.
def premiere(texte):
    return re.split(r"(?<=[.;:])\s", " ".join(str(texte or "").split()), maxsplit=1)[0]
approchees = [r for r in veille if r["etat"] == "approximation"]
a_l_imparfait = [r["id"] for r in approchees if re.search(r"\b\w+(ait|aient)\b", premiere(r.get("effet")))]

# ---- 3. ce qui reste à faire --------------------------------------------------
statut_sources = collections.Counter(s["statut"] for s in sources)
a_explorer = [s for s in sources if s["statut"] == "a_explorer"]
couverture_de = {r["code"]: r["couverture"] for r in inventaire}
utiles = collections.defaultdict(list)          # sources qui touchent un régime partiel
for s in a_explorer:
    for reg in s.get("regimes") or []:
        if couverture_de.get(reg) == "partiel":
            utiles[reg].append(s["id"])
sans_regime = sum(1 for s in a_explorer if not s.get("regimes"))
n_utiles = len({i for ids in utiles.values() for i in ids})
en_cours = [(n, t) for n, t, s in actions if s == "en cours"]
hors_champ = [r for r in inventaire if r["couverture"] == "hors_champ"]

# ---- la page -----------------------------------------------------------------
L = []
w = L.append
w(f"# État du dépôt — maquette du tableau de bord, fabriquée le {DATE}")
w("")
w("*Tous les nombres sont calculés par `tableau_de_bord.py` depuis les registres "
  "d'aujourd'hui ; aucun n'est écrit à la main. Rien n'a été écrit dans le dépôt.*")
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
for cle, nom in (("modelise", "régime modélisé"), ("partiel", "régime partiel"), ("mêlée", "sections libérales, couverture mêlée")):
    w(f"| {nom} | {milliers(poids[cle])} | {pct(poids[cle], total_caisses)} |")
w("")
w(f"*Modélisé ne veut pas dire exact* : les {etat.get('approximation', 0)} règles approchées de la "
  "veille touchent aussi des régimes modélisés (section 2).")
w("")
if non_rattachees:
    w(f"Caisses de l'enquête non rattachées à l'inventaire : {', '.join(non_rattachees)}.")
    w("")
w(f"**Les règles suivies en veille** : {len(veille)}.")
w("")
w("| État | Règles |")
w("|---|---|")
for cle, nom in (("conforme", "conformes"), ("transcrit", "transcrites"), ("approximation", "approchées"),
                 ("hors_modele", "hors modèle"), ("manque", "manquantes"), ("a_verifier", "à vérifier")):
    w(f"| {nom} | {etat.get(cle, 0)} |")
w("")
w(f"- Confrontées à au moins un exemple officiel : **{avec_exemple} sur {len(veille)}** "
  f"({len(exemples)} exemples, tous reproduits : le test n'admet pas d'exemple qui échoue).")
w(f"- Citées dans le code par leur identifiant : **{citees} sur {len(veille)}**. "
  "Le lien entre une règle et le code qui l'applique n'existe pas encore pour les autres.")
w(f"- Réformes du calendrier : {len(reformes)}, dont {len(non_appliquees)} déclarées non appliquées.")
w("")
part_rev = f"{100 * float(derniere_part['part']):.1f}".replace(".", ",")
w("**Ce qui est hors du modèle.** La réversion, par exemple, pèse "
  f"{part_rev} % de la masse des prestations en {derniere_part['annee']} "
  "(COR), et le modèle n'en calcule aucune.")
w("")
w(f"**La feuille de route** compte {len(actions)} actions : "
  + ", ".join(f"{n} {s}" for s, n in statuts_actions.most_common()) + ". "
  "Elle raconte ce qui a été fait ; ce qui reste à faire est ailleurs, dispersé.")
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
w(f"Et {len(partiels_sans_effectif)} régimes partiels sans effectif dans l'enquête (outre-mer, "
  "sections libérales, régimes fermés…).")
w("")
w("**Les règles approchées, absentes ou à vérifier**, avec ce que le registre dit de leur effet :")
w("")
w("| Règle | État | Qui est touché |")
w("|---|---|---|")
for r in limites_veille:
    w(f"| `{r['id']}` | {r['etat']} | {phrase(r.get('effet'), 140)} |")
w("")
w(f"**Un état peut-être périmé.** Pour {len(a_l_imparfait)} des {len(approchees)} règles approchées, "
  "l'effet raconte à l'imparfait l'erreur qui a été corrigée, sans dire ce qui reste. Le tableau ne "
  "peut pas savoir si elles sont encore approchées : la fiche séparera l'effet actuel de l'historique.")
w("")
w("## 3. Ce qui reste à faire, et par quoi commencer")
w("")
w(f"- **Les {len(en_cours)} actions en cours** de la feuille de route :")
for n, t in en_cours:
    w(f"  - {n}. {t if len(t) <= 150 else t[:149].rstrip() + '…'}")
w(f"- **Les sources à exploiter** : {statut_sources['a_explorer']} à explorer sur {len(sources)} "
  f"({statut_sources['explore']} explorées, {statut_sources['epuise']} épuisées). "
  f"{n_utiles} d'entre elles visent un régime partiel, et pourraient le compléter :")
for reg, ids in sorted(utiles.items(), key=lambda x: -len(x[1])):
    nom = par_code[reg]["nom"]
    w(f"  - {nom} : {len(ids)} source(s) ({', '.join(ids[:3])}{'…' if len(ids) > 3 else ''})")
w(f"  - et {sans_regime} sources sans régime désigné.")
w(f"- **Les règles sans exemple officiel** : {len(veille) - avec_exemple}.")
w(f"- **Les régimes hors champ** : {len(hors_champ)}, chacun avec sa raison dans l'inventaire.")
w("")
# ---- le coût du travail, relevé sur l'historique git ------------------------------
import statistics, subprocess
journal = subprocess.run(["git", "-C", str(DEPOT), "log", "--format=@@%H", "--name-only", "-n", "400"],
                         capture_output=True, text=True).stdout
changes = [[l for l in b.strip().split("\n")[1:] if l] for b in journal.split("@@")[1:]]
changes = [c for c in changes if c]
REGISTRES = {"data/reference/legislation/veille.yaml", "data/reference/legislation/frontiere_contributive.yaml",
             "data/reference/prose/zones.yaml", "data/reference/site/affirmations.yaml",
             "data/reference/regimes/inventaire.yaml", "data/reference/legislation/reformes.yaml",
             "data/reference/regimes/pivots.yaml"}
def a_la_main(f):
    return f.endswith(".md") and f != "docs/chiffrage_plf.md" or f in REGISTRES
moteur = [c for c in changes if "src/retraite_notionnelle/scenarios/actuel.py" in c]
lourds = ["docs/feuille_de_route.md", "docs/limites.md", "data/reference/legislation/veille.yaml", "README.md"]
poids_lourds = sum((DEPOT / f).stat().st_size for f in lourds)
w("## 4. Le coût du travail")
w("")
w(f"Relevé sur les {len(changes)} derniers commits :")
w("")
w(f"- un commit touche en médiane {statistics.median(len(c) for c in changes):.0f} fichiers ;")
if moteur:
    med = statistics.median(len(c) for c in moteur)
    main = f"{statistics.mean(sum(1 for f in c if a_la_main(f)) for c in moteur):.1f}".replace(".", ",")
    w(f"- un commit qui change le moteur du scénario 1 en touche {med:.0f} en médiane, dont {main} de prose "
      f"ou de registres écrits à la main (moyenne, sur {len(moteur)} commits) ;")
for f in lourds[:2]:
    n = sum(1 for c in changes if f in c)
    w(f"- `{f}` est modifié dans {pct(n, len(changes))} des commits ;")
mo = f"{poids_lourds / 1e6:.1f}".replace(".", ",")
w(f"- les quatre fichiers que presque tout changement du moteur touche ({', '.join('`' + f + '`' for f in lourds)}) "
  f"pèsent ensemble {mo} Mo : aucune session ne peut les lire en entier ;")
temps = Path(__file__).resolve().parent.parent / "pytest_temps.txt"
if temps.exists():
    reel = next((l.split()[1] for l in temps.read_text().splitlines() if l.startswith("real")), None)
    if reel:
        minutes, secondes = reel.rstrip("s").split("m")
        w(f"- la suite complète des tests a pris {int(minutes)} min {round(float(secondes)):02d} (mesure du 25 septembre 2026).")
w("")
w("## 5. Ce que ce tableau ne sait pas encore dire")
w("")
w("- **L'effet chiffré de chaque limite.** Les registres le disent en mots. Le pilote le "
  "mesurera, en neutralisant la règle sur les cas types pondérés.")
w("- **La part des pensions qui ne passent que par des règles conformes.** Il faut pour cela "
  "que chaque ligne du relevé cite sa fiche, ce que l'architecture prévoit aux phases 4 et 5.")
w("- **Ce que personne n'a encore noté.** Le dénominateur est aujourd'hui la mémoire des "
  "registres ; la liste de contrôle des textes (phase 2) en fera la loi elle-même.")
w("- **Les limites propres à une simulation.** Le site les montrera avec chaque résultat.")
print("\n".join(L))
