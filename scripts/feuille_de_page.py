"""Le style de chaque page : les règles de ``moteur/style.css`` qui peuvent la
toucher (action 174, proposition du 27 octobre 2026).

La feuille de style bloquait l'affichage : 37 Ko compressés à recevoir avant de
peindre, dont chaque page n'utilise que le cinquième à l'ouverture. Chaque page
porte donc en tête les règles qui peuvent la toucher, et la feuille entière suit
sans retenir l'affichage (``moteur/page.html``). ``construire_pages.py`` les y
écrit par ``feuille_de_la_page``.

Le choix se fait sans navigateur et sans dépendance. Une règle est gardée quand
l'un de ses sélecteurs peut toucher la page : chaque classe, chaque identifiant,
chaque balise et chaque nom d'attribut qu'il demande y paraît — dans le HTML de la
page, ou dans les chaînes du routeur, qui pose des classes à l'ouverture. Les
pseudo-classes, les négations et les sélecteurs fonctionnels (``:not``, ``:is``,
``:has``…) ne demandent rien : on garde trop plutôt que pas assez. Les requêtes
``@media`` et ``@supports`` gardent leur condition et leurs règles gardées ;
l'impression reste à la feuille entière, déclarée pour elle dès le départ ; les
polices sont toujours déclarées, une animation seulement quand une règle gardée
la nomme. Les règles gardées restent écrites et rangées comme dans la feuille :
la cascade est la même. ``tests/test_ecrans.py`` vérifie, dans Chromium, que
chaque page se peint avec ce seul style comme avec la feuille entière.
"""

from __future__ import annotations

import re

#: Un commentaire de feuille de style.
COMMENTAIRE = re.compile(r"/\*.*?\*/", re.S)
#: Une chaîne entre guillemets, dans un sélecteur ou une déclaration.
CHAINE = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
#: Un mot du HTML ou du code : une classe, un identifiant, une balise, un attribut.
MOT = re.compile(r"[A-Za-z_][\w-]*")


def blocs(texte: str) -> list[tuple[str, str]]:
    """La suite des règles d'un texte de feuille de style, au premier niveau :
    ``(prélude, corps)`` pour une règle à accolades, ``(instruction, None)`` pour
    une instruction close par un point-virgule (``@import``, ``@charset``)."""
    texte = COMMENTAIRE.sub("", texte)
    sortie: list[tuple[str, str]] = []
    i, n = 0, len(texte)
    while i < n:
        while i < n and texte[i].isspace():
            i += 1
        if i >= n:
            break
        debut, profondeur, ouverture = i, 0, None
        while i < n:
            caractere = texte[i]
            if caractere in "\"'":
                fin = CHAINE.match(texte, i)
                i = fin.end() if fin else i + 1
                continue
            if caractere == "{":
                profondeur += 1
                if ouverture is None:
                    ouverture = i
            elif caractere == "}":
                profondeur -= 1
                if profondeur == 0:
                    sortie.append((texte[debut:ouverture].strip(), texte[ouverture + 1:i]))
                    i += 1
                    break
            elif caractere == ";" and ouverture is None:
                sortie.append((texte[debut:i + 1].strip(), None))
                i += 1
                break
            i += 1
        else:
            if texte[debut:].strip():
                raise ValueError(f"règle inachevée : {texte[debut:debut + 80]!r}")
    return sortie


def jetons(page: str, routeur: str = "") -> set[str]:
    """Ce qui peut toucher la page : ses balises, ses noms d'attribut, ses classes
    et ses identifiants, et les mots des chaînes du routeur, qui pose des
    classes à l'ouverture."""
    trouves: set[str] = set()
    for balise in re.finditer(r"<([A-Za-z][\w-]*)([^>]*)>", page):
        trouves.add(balise.group(1).lower())
        for attribut in re.finditer(r'([\w:-]+)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+))?',
                                    balise.group(2)):
            trouves.add(attribut.group(1).lower())
            if attribut.group(1).lower() in ("class", "id") and attribut.group(2):
                trouves.update(attribut.group(2).strip("\"'").split())
    for chaine in re.finditer(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`[^`]*`', routeur):
        trouves.update(MOT.findall(chaine.group(0)))
    # Un attribut posé par `dataset` n'est écrit nulle part en toutes lettres :
    # `table.dataset.pli` pose `data-pli`, `dataset.vueCourante` `data-vue-courante`.
    for nom in re.findall(r"\bdataset(?:\.([A-Za-z]\w*)|\[\s*[\"']([\w-]+)[\"']\s*\])", routeur):
        trouves.add("data-" + re.sub(r"[A-Z]", lambda m: "-" + m.group(0).lower(), nom[0] or nom[1]))
    return trouves


def _sans_fonctions(selecteur: str) -> str:
    """Le sélecteur sans ses pseudo-classes fonctionnelles : ``:not(.x)``, ``:is(…)``
    et leurs pareilles ne demandent rien."""
    precedent = None
    while precedent != selecteur:
        precedent = selecteur
        selecteur = re.sub(r"::?[\w-]+\([^()]*\)", " ", selecteur)
    return selecteur


def _peut_toucher(selecteur: str, presents: set[str]) -> bool:
    s = _sans_fonctions(CHAINE.sub('""', selecteur))
    attributs = re.findall(r"\[\s*([\w-]+)", s)
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"::?[\w-]+", " ", s)
    demandes = re.findall(r"[.#]([\w-]+)", s) + attributs
    s = re.sub(r"[.#][\w-]+", " ", s)
    demandes += [balise.lower() for balise in MOT.findall(s)]
    return all(mot in presents for mot in demandes)


def _selecteurs(prelude: str) -> list[str]:
    """Les sélecteurs d'une liste, coupés aux virgules de premier niveau."""
    morceaux, profondeur, debut = [], 0, 0
    for i, caractere in enumerate(prelude):
        if caractere in "([":
            profondeur += 1
        elif caractere in ")]":
            profondeur -= 1
        elif caractere == "," and profondeur == 0:
            morceaux.append(prelude[debut:i])
            debut = i + 1
    morceaux.append(prelude[debut:])
    return [morceau.strip() for morceau in morceaux if morceau.strip()]


def _garder(regles: list[tuple[str, str]], presents: set[str],
            animations: dict[str, str]) -> list[str]:
    sortie = []
    for prelude, corps in regles:
        if corps is None:
            continue
        regle = prelude.lower()
        if regle.startswith("@media"):
            if re.search(r"\bprint\b", regle) and not re.search(r"\b(screen|all)\b", regle):
                continue
            dedans = _garder(blocs(corps), presents, animations)
            if dedans:
                sortie.append(f"{prelude} {{\n" + "".join(f"  {r}" for r in dedans) + "}\n")
        elif regle.startswith(("@supports", "@container", "@layer")):
            dedans = _garder(blocs(corps), presents, animations)
            if dedans:
                sortie.append(f"{prelude} {{\n" + "".join(f"  {r}" for r in dedans) + "}\n")
        elif regle.startswith("@font-face"):
            sortie.append(f"{prelude} {{{corps}}}\n")
        elif regle.startswith(("@keyframes", "@-webkit-keyframes")):
            animations[prelude.split()[-1]] = f"{prelude} {{{corps}}}\n"
        elif regle.startswith("@"):
            continue
        elif any(_peut_toucher(selecteur, presents) for selecteur in _selecteurs(prelude)):
            sortie.append(f"{prelude} {{{corps}}}\n")
    return sortie


def _depuis_la_page(texte: str, racine: str) -> str:
    """Les adresses relatives de la feuille menaient depuis ``moteur/`` : écrites
    dans la page, elles partent de sa racine."""
    return re.sub(r"url\(\s*([\"']?)(?!data:|https?:|#|/)([^\"')]+)\1\s*\)",
                  lambda m: f"url({m.group(1)}{racine}moteur/{m.group(2)}{m.group(1)})", texte)


def feuille_de_la_page(feuille: str, presents: set[str], racine: str = "") -> str:
    """Les règles de ``feuille`` qui peuvent toucher la page dont ``presents``
    porte les mots, adresses relatives à la page (``racine`` : ``""`` à la racine
    du site, ``"../"`` dans un dossier)."""
    animations: dict[str, str] = {}
    gardees = "".join(_garder(blocs(feuille), presents, animations))
    nommees = set()
    for declaration in re.finditer(r"animation(?:-name)?\s*:\s*([^;}]+)", gardees):
        nommees.update(MOT.findall(declaration.group(1)))
    gardees += "".join(texte for nom, texte in animations.items() if nom in nommees)
    return _depuis_la_page(gardees, racine)
