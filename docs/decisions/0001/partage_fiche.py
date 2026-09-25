"""Vérifie qu'une fiche (YAML de l'annexe A) forme un partage de ses dates qui
décident, à chaque date d'observation, et fabrique ses cas de bascule.

    python docs/decisions/0001/partage_fiche.py docs/decisions/0001-architecture.md

Outil laissé par la session qui a conçu l'architecture ; il servira à la
phase 2 (voir `phase_0.md`, à côté).

- Combinaison impossible : un enfant né après la date d'effet de la pension.
- Une borne ne vaut qu'une fois connue la version qui la ferme : celle que la
  fiche déclare (`fermee_par`), sinon celle qui commence là.
- Une version est connue à la publication du texte qui la fait naître
  (`nee_de`, sinon son seul texte) ; faute de date de publication, à l'entrée
  en vigueur de ce texte. Sans texte (supposée, « sans droit »), elle l'est
  toujours.
- Deux versions qui s'appliquent ensemble sont un chevauchement, sauf si l'une
  se déclare `exception_de` l'autre.
"""
import itertools, re, sys
from datetime import date, timedelta
import yaml

BAS, HAUT = date(1850, 1, 1), date(2200, 1, 1)


def d(x):
    if x is None:
        return None
    return x if isinstance(x, date) else date.fromisoformat(str(x))


def connue_des(v):
    """La version est connue à la publication du texte qui la fait naître
    (`nee_de`) ; faute de date de publication, à son entrée en vigueur."""
    textes = [t for t in v.get("textes") or [] if isinstance(t, dict)]
    if v.get("nee_de"):
        textes = [t for t in textes if t.get("id") == v["nee_de"]]
        assert textes, f"{v['id']} : nee_de ne désigne aucun de ses textes"
    dates = [d(t.get("publie_le") or t.get("en_vigueur")) for t in textes if t.get("publie_le") or t.get("en_vigueur")]
    return min(dates) if dates else BAS


def fermantes(fiche, v, n):
    """Les versions qui ferment la borne de `v` sur la date `n` : celles que la
    fiche déclare (`fermee_par`), sinon celles qui commencent là."""
    declaree = (v.get("fermee_par") or {}).get(n)
    if declaree:
        return {declaree}
    fin = d((v.get("bornes", {}).get(n) or [None, None])[1])
    return {w["id"] for w in fiche["versions"]
            if w is not v and fin and d((w.get("bornes", {}).get(n) or [None, None])[0]) == fin}


def verifier(fiche, observation, deduire=True):
    noms = fiche["dates_qui_decident"]
    connues = {v["id"]: v for v in fiche["versions"] if connue_des(v) <= observation}
    versions = []
    for v in connues.values():
        b = {}
        for n in noms:
            deb, fin = v.get("bornes", {}).get(n) or [None, None]
            ferment = fermantes(fiche, v, n) if deduire else set()
            if fin and ferment and not ferment & set(connues):
                fin = None                      # la suivante n'est pas encore connue
            b[n] = (d(deb) or BAS, d(fin) or HAUT)
        versions.append((v["id"], v.get("exception_de"), b))
    bords = {n: sorted({BAS, HAUT} | {x for _, _, b in versions for x in b[n]}) for n in noms}

    def points(n):
        for a, z in zip(bords[n], bords[n][1:]):
            yield from {a, z - timedelta(days=1)}

    trous, chev, cas = [], [], 0
    for combo in itertools.product(*(list(points(n)) for n in noms)):
        p = dict(zip(noms, combo))
        if "enfant.naissance" in p and "liquidation.date_effet" in p \
                and p["enfant.naissance"] > p["liquidation.date_effet"]:
            continue
        cas += 1
        s = [(vid, exc) for vid, exc, b in versions if all(b[n][0] <= p[n] < b[n][1] for n in noms)]
        restent = [vid for vid, _ in s if not any(exc == vid for _, exc in s)]
        if not restent:
            trous.append(p)
        elif len(restent) > 1:
            chev.append((p, restent))
    bascules = [(n, x - timedelta(days=1), x) for n in noms for x in bords[n] if x not in (BAS, HAUT)]
    return len(connues), cas, trous, chev, bascules


def main(chemin, deduire=True):
    texte = open(chemin, encoding="utf-8").read()
    for bloc in re.findall(r"```yaml\n(.*?)```", texte, re.S):
        fiche = yaml.safe_load(bloc)
        if "dates_qui_decident" not in fiche:
            continue
        ids = {v["id"] for v in fiche["versions"]}
        for v in fiche["versions"]:
            for cible in (v.get("fermee_par") or {}).values():
                assert cible in ids, f"{v['id']} : fermee_par vise {cible}, absente"
        observations = sorted({connue_des(v) for v in fiche["versions"]} - {BAS}) + [HAUT]
        print(f"{fiche['id']} : {len(fiche['versions'])} versions, "
              f"{len(observations)} dates d'observation")
        for o in observations:
            n_v, cas, trous, chev, bascules = verifier(fiche, o, deduire)
            quand = "toutes connues" if o == HAUT else f"observée le {o}"
            print(f"   {quand:<24} {n_v} version(s), {cas:>3} situations, "
                  f"{len(trous)} trou(s), {len(chev)} chevauchement(s)")
            for p in trous[:2]:
                print("      trou", {k: str(v) for k, v in p.items()})
            for p, s in chev[:2]:
                print("      chevauchement", {k: str(v) for k, v in p.items()}, s)
        print(f"   {len(bascules)} bascules :",
              " ; ".join(f"{n} {avant}/{jour}" for n, avant, jour in bascules))


if __name__ == "__main__":
    # --sans-fermeture : les bornes valent dès l'origine, comme si l'on savait
    # d'avance qu'une version finirait (ce que faisait la version 4).
    main(sys.argv[1], deduire="--sans-fermeture" not in sys.argv)
