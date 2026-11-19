"""Les constantes nommées du moteur, et celles qui portent une année ou une date.

Le relevé qui donne son dénominateur au cinquième cliquet de la note 0009
(« les chiffres de la loi dans le code des règles »). Il ne modifie rien.

    python constantes.py            # les comptes
    python constantes.py --liste    # et chaque constante datée du code des règles

Une constante nommée : une déclaration `const` ou `static` dont le nom est en
majuscules (trois caractères au moins). Elle est datée quand sa valeur porte
un `DateMois(`, une année de 1900 à 2099 ou une date « AAAA-MM-JJ ». Le code
des règles : `moteur/js/droit/*.js`, `regimes.js` et `scenario-actuel.js`.
Le site (`pages.js`, `gabarit.js`, `routeur.js`, `adresses.js`) est écarté.
"""
import glob
import re
import sys

SITE = ("pages.js", "gabarit.js", "routeur.js", "adresses.js")
DECLARATION = re.compile(r"^(?:export )?(?:const|static) ([A-Z][A-Z0-9_]{2,}) = (.*)$")
DATEE = re.compile(r"DateMois\(|\b(19|20)\d\d\b|\"\d{4}-\d{2}-\d{2}\"")
ANNEE = re.compile(r"\b(19|20)\d\d\b")


def constantes(chemin):
    """Les constantes nommées d'un fichier : (nom, valeur, ligne)."""
    lignes = open(chemin, encoding="utf-8").read().split("\n")
    for i, ligne in enumerate(lignes):
        trouve = DECLARATION.match(ligne.strip())
        if not trouve:
            continue
        valeur, j = trouve.group(2), i
        while not valeur.rstrip().endswith(";") and j + 1 < len(lignes) and j - i < 6:
            j += 1
            valeur += " " + lignes[j].strip()
        yield trouve.group(1), valeur, i + 1


def compter(fichiers):
    total, datees = 0, []
    for chemin in sorted(fichiers):
        for nom, valeur, ligne in constantes(chemin):
            total += 1
            if DATEE.search(valeur):
                datees.append((chemin, ligne, nom))
    return total, datees


def annees_en_clair(fichiers):
    """Les lignes de code, hors déclarations de constantes et commentaires,
    qui portent une année écrite en clair."""
    trouvees = []
    for chemin in sorted(fichiers):
        dans_un_commentaire = False
        suite = 0
        for numero, ligne in enumerate(open(chemin, encoding="utf-8"), 1):
            nue = ligne.strip()
            if dans_un_commentaire:
                if "*/" in nue:
                    dans_un_commentaire = False
                continue
            if nue.startswith("/*"):
                dans_un_commentaire = "*/" not in nue
                continue
            if nue.startswith("//") or nue.startswith("*"):
                continue
            if DECLARATION.match(nue):
                suite = 0 if nue.rstrip().endswith(";") else 6
                continue
            if suite:
                suite = 0 if nue.rstrip().endswith(";") else suite - 1
                continue
            code = nue.split("//")[0]
            if ANNEE.search(code):
                trouvees.append((chemin, numero, code[:90]))
    return trouvees


if __name__ == "__main__":
    moteur = [p for p in glob.glob("moteur/js/**/*.js", recursive=True)
              if not p.endswith(SITE)]
    regles = glob.glob("moteur/js/droit/*.js") + [
        "moteur/js/regimes.js", "moteur/js/scenario-actuel.js"]
    total, datees = compter(moteur)
    print(f"moteur hors site : {len(moteur)} fichiers, {total} constantes nommées, "
          f"dont {len(datees)} datées")
    total, datees = compter(regles)
    print(f"code des règles : {len(regles)} fichiers, {total} constantes nommées, "
          f"dont {len(datees)} datées, dans {len({c for c, _, _ in datees})} fichiers")
    clair = annees_en_clair(regles)
    print(f"code des règles : {len(clair)} lignes de code portent une année en clair, "
          f"hors constantes et commentaires, dans {len({c for c, _, _ in clair})} fichiers")
    if "--liste" in sys.argv:
        for chemin, ligne, nom in datees:
            print(f"  {chemin}:{ligne} {nom}")
        print("--- années en clair")
        for chemin, ligne, code in clair:
            print(f"  {chemin}:{ligne} {code}")
