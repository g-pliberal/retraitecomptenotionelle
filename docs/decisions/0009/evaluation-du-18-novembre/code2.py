import glob, re, yaml
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
fiches = {}
for p in sorted(glob.glob("data/reference/regles/*.yaml")):
    d = yaml.load(open(p), Loader=Loader); fiches[d["id"]] = d
def texte(motifs):
    t = ""
    for m in motifs:
        for p in glob.glob(m, recursive=True):
            try: t += open(p, encoding="utf-8").read()
            except Exception: pass
    return t
def cites(t):
    return {i for i in fiches if re.search(r"(?<![A-Za-z0-9_])" + re.escape(i) + r"(?![A-Za-z0-9_])", t)}
js = cites(texte(["moteur/js/**/*.js"]))
sans_pages = cites(texte([p for p in glob.glob("moteur/js/**/*.js", recursive=True) if not p.endswith(("pages.js", "gabarit.js", "routeur.js", "adresses.js"))]))
py = cites(texte(["src/**/*.py"]))
scripts = cites(texte(["scripts/**/*.py"]))
print("moteur/js :", len(js), "; moteur/js hors site :", len(sans_pages), "; src python :", len(py), "; js ou python :", len(js | py), "; js, python ou scripts :", len(js | py | scripts), "; sur", len(fiches))
print("fiches avec un champ code :", sum(1 for d in fiches.values() if d.get("code")), "; avec code.javascript :", sum(1 for d in fiches.values() if isinstance(d.get("code"), dict) and d["code"].get("javascript")))
