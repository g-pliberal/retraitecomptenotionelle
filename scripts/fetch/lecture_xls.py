"""Lecteur de classeurs Excel 97 (BIFF8), sans dépendance.

Pendant de ``lecture_pdf.py``, et pour la même raison : une source publie ses
séries dans un format que la bibliothèque standard ne sait pas ouvrir, et le
dépôt s'interdit toute dépendance hors PyYAML. On écrit donc le lecteur.

Un classeur Excel 97 est un fichier composite OLE2 — un système de fichiers
miniature — dont le flux ``Workbook`` contient des enregistrements BIFF. Seuls
les NOMBRES sont extraits : quatre types d'enregistrements suffisent (NUMBER,
RK, MULRK et le résultat en cache d'une FORMULA), et c'est tout ce dont on a
besoin pour reprendre une grille de quotients de mortalité.
"""

from __future__ import annotations

import struct


def _flux(donnees: bytes, nom_cible: str) -> bytes:
    """Extrait un flux nommé d'un fichier composite OLE2."""
    if donnees[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        raise ValueError("ce n'est pas un fichier composite OLE2")
    taille = 1 << struct.unpack_from("<H", donnees, 30)[0]
    taille_mini = 1 << struct.unpack_from("<H", donnees, 32)[0]
    premier_repertoire = struct.unpack_from("<i", donnees, 48)[0]
    premier_mini = struct.unpack_from("<i", donnees, 60)[0]
    premier_difat = struct.unpack_from("<i", donnees, 68)[0]
    nb_difat = struct.unpack_from("<I", donnees, 72)[0]

    def secteur(indice: int) -> bytes:
        debut = (indice + 1) * taille
        return donnees[debut:debut + taille]

    # DIFAT : 109 entrées dans l'en-tête, puis des secteurs chaînés.
    difat = list(struct.unpack_from("<109i", donnees, 76))
    suivant = premier_difat
    for _ in range(nb_difat):
        if suivant < 0:
            break
        bloc = secteur(suivant)
        entrees = struct.unpack(f"<{taille // 4}i", bloc)
        difat.extend(entrees[:-1])
        suivant = entrees[-1]

    fat: list[int] = []
    for indice in difat:
        if indice < 0:
            continue
        fat.extend(struct.unpack(f"<{taille // 4}i", secteur(indice)))

    def chaine(depart: int, longueur: int | None = None) -> bytes:
        morceaux, indice = [], depart
        while indice >= 0 and len(morceaux) * taille < (longueur or 1 << 40):
            morceaux.append(secteur(indice))
            indice = fat[indice] if indice < len(fat) else -1
        contenu = b"".join(morceaux)
        return contenu[:longueur] if longueur else contenu

    repertoire = chaine(premier_repertoire)
    entrees = []
    for debut in range(0, len(repertoire), 128):
        entree = repertoire[debut:debut + 128]
        if len(entree) < 128:
            break
        longueur_nom = struct.unpack_from("<H", entree, 64)[0]
        nom = entree[:max(0, longueur_nom - 2)].decode("utf-16-le", "replace")
        entrees.append((nom, entree[66], struct.unpack_from("<i", entree, 116)[0],
                        struct.unpack_from("<I", entree, 120)[0]))

    racine = next(e for e in entrees if e[1] == 5)
    cible = next((e for e in entrees if e[0] == nom_cible), None)
    if cible is None:
        raise LookupError(f"flux {nom_cible!r} absent : {[e[0] for e in entrees]}")
    _, _, depart, longueur = cible
    if longueur >= 4096:
        return chaine(depart, longueur)

    # Petit flux : il vit dans le mini-FAT, lui-même stocké dans le flux racine.
    mini_fat: list[int] = []
    indice = premier_mini
    while indice >= 0:
        mini_fat.extend(struct.unpack(f"<{taille // 4}i", secteur(indice)))
        indice = fat[indice] if indice < len(fat) else -1
    conteneur = chaine(racine[2])
    morceaux, indice = [], depart
    while indice >= 0 and len(morceaux) * taille_mini < longueur:
        morceaux.append(conteneur[indice * taille_mini:(indice + 1) * taille_mini])
        indice = mini_fat[indice] if indice < len(mini_fat) else -1
    return b"".join(morceaux)[:longueur]


def _rk(brut: int) -> float:
    """Décode un nombre RK : entier ou double tronqué, éventuellement centième."""
    entier = bool(brut & 0x02)
    centieme = bool(brut & 0x01)
    if entier:
        valeur = float(brut >> 2 if brut < 0x80000000 else (brut >> 2) - (1 << 30))
    else:
        valeur = struct.unpack("<d", struct.pack("<Q", (brut & 0xFFFFFFFC) << 32))[0]
    return valeur / 100 if centieme else valeur


def _chaines_partagees(morceaux: list[bytes]) -> list[str]:
    """Décode la table des chaînes partagées (SST), coupures comprises.

    C'EST LE SEUL ENDROIT DÉLICAT DU LECTEUR, et la difficulté n'est pas
    l'encodage : c'est la COUPURE. Un enregistrement BIFF ne dépasse pas
    8 224 octets, si bien qu'une table de plusieurs milliers de chaînes se
    poursuit dans des enregistrements ``CONTINUE``. La coupure peut tomber au
    milieu d'une chaîne — et, quand elle tombe au milieu de ses CARACTÈRES, la
    suite recommence par un octet de drapeau qui redit leur largeur : une même
    chaîne peut donc être coupée en latin-1 et reprendre en UTF-16, parce
    qu'Excel choisit la largeur morceau par morceau.

    D'où la forme retenue : un tampon unique, et la liste des positions où un
    morceau succède à un autre. Les en-têtes et les queues traversent ces
    frontières sans rien consommer ; seuls les caractères y lisent un drapeau.

    Une table mal décodée ne lève pas d'erreur, elle DÉCALE : toutes les
    chaînes suivantes deviennent fausses d'une case, et un libellé se retrouve
    sous une autre ligne. C'est pour cela que le test synthétique de
    `tests/test_verification.py` force une coupure au milieu d'un mot.
    """
    tampon = b"".join(morceaux)
    frontieres, position = set(), 0
    for morceau in morceaux[:-1]:
        position += len(morceau)
        frontieres.add(position)

    position = 0

    def prendre(nombre: int) -> bytes:
        """Lit des octets bruts : un en-tête ou une queue ignore les coupures."""
        nonlocal position
        brut = tampon[position:position + nombre]
        position += nombre
        return brut

    def caracteres(compte: int, large: bool) -> str:
        """Lit les caractères, en relisant la largeur à chaque coupure."""
        nonlocal position
        morceaux_lus: list[str] = []
        restant = compte
        while restant > 0:
            prochaine = min((f for f in frontieres if f > position),
                            default=len(tampon))
            taille = 2 if large else 1
            possible = (prochaine - position) // taille
            pris = min(restant, possible)
            if pris > 0:
                brut = tampon[position:position + pris * taille]
                position += pris * taille
                morceaux_lus.append(
                    brut.decode("utf-16-le" if large else "latin-1", "replace"))
                restant -= pris
            if restant > 0:
                # On bute sur une coupure : l'octet suivant redit la largeur.
                position = prochaine
                if position >= len(tampon):
                    break
                large = bool(tampon[position] & 0x01)
                position += 1
                frontieres.discard(prochaine)
        return "".join(morceaux_lus)

    if len(tampon) < 8:
        return []
    uniques = struct.unpack_from("<I", tampon, 4)[0]
    position = 8
    chaines: list[str] = []
    for _ in range(uniques):
        if position + 3 > len(tampon):
            break
        compte = struct.unpack_from("<H", tampon, position)[0]
        drapeaux = tampon[position + 2]
        position += 3
        riche = bool(drapeaux & 0x08)
        phonetique = bool(drapeaux & 0x04)
        runs = struct.unpack_from("<H", tampon, position)[0] if riche else 0
        position += 2 if riche else 0
        extra = struct.unpack_from("<I", tampon, position)[0] if phonetique else 0
        position += 4 if phonetique else 0
        chaines.append(caracteres(compte, bool(drapeaux & 0x01)))
        prendre(runs * 4 + extra)
    return chaines


def _chaine_courte(corps: bytes, decalage: int) -> str:
    """Une chaîne BIFF8 non partagée, telle que la porte un LABEL."""
    compte = struct.unpack_from("<H", corps, decalage)[0]
    large = bool(corps[decalage + 2] & 0x01)
    debut = decalage + 3
    brut = corps[debut:debut + compte * (2 if large else 1)]
    return brut.decode("utf-16-le" if large else "latin-1", "replace")


def feuilles(donnees: bytes) -> dict[str, dict[tuple[int, int], float | str]]:
    """Cellules de chaque feuille, indexées (ligne, colonne).

    Un ``float`` pour un nombre, une ``str`` pour un texte, comme le rend
    ``lecture_xlsx`` pour les classeurs modernes : les deux lecteurs se lisent
    de la même façon, et un appelant peut passer de l'un à l'autre.

    LE TEXTE A LONGTEMPS ÉTÉ IGNORÉ, et c'était un choix défendable tant que ce
    lecteur ne servait qu'à reprendre une grille de quotients de mortalité.
    Il a cessé de l'être devant le tableur du jaune budgétaire « Pensions de
    retraite de la fonction publique » : sa feuille des bonifications rendait
    trente-sept nombres et pas un libellé, donc trente-sept nombres dont on ne
    savait pas ce qu'ils comptaient. Un nombre sans son intitulé n'est pas une
    donnée.
    """
    flux = _flux(donnees, "Workbook")
    noms: list[tuple[int, str]] = []
    partagees: list[str] = []
    position = 0
    while position + 4 <= len(flux):
        type_, longueur = struct.unpack_from("<HH", flux, position)
        corps = flux[position + 4:position + 4 + longueur]
        if type_ == 0x0085 and len(corps) >= 8:  # BOUNDSHEET
            debut = struct.unpack_from("<I", corps, 0)[0]
            taille_nom = corps[6]
            large = corps[7] & 0x01
            brut = corps[8:8 + taille_nom * (2 if large else 1)]
            nom = brut.decode("utf-16-le" if large else "latin-1", "replace")
            noms.append((debut, nom))
        elif type_ == 0x00FC:  # SST, suivie de ses CONTINUE
            morceaux = [corps]
            suite = position + 4 + longueur
            while suite + 4 <= len(flux):
                type_suite, longueur_suite = struct.unpack_from("<HH", flux, suite)
                if type_suite != 0x003C:  # CONTINUE
                    break
                morceaux.append(flux[suite + 4:suite + 4 + longueur_suite])
                suite += 4 + longueur_suite
            partagees = _chaines_partagees(morceaux)
        position += 4 + longueur

    resultat: dict[str, dict[tuple[int, int], float | str]] = {}
    for indice, (debut, nom) in enumerate(noms):
        fin = noms[indice + 1][0] if indice + 1 < len(noms) else len(flux)
        cellules: dict[tuple[int, int], float | str] = {}
        position = debut
        while position + 4 <= fin:
            type_, longueur = struct.unpack_from("<HH", flux, position)
            corps = flux[position + 4:position + 4 + longueur]
            if type_ == 0x0203 and len(corps) >= 14:  # NUMBER
                ligne, colonne = struct.unpack_from("<HH", corps, 0)
                cellules[(ligne, colonne)] = struct.unpack_from("<d", corps, 6)[0]
            elif type_ == 0x027E and len(corps) >= 10:  # RK
                ligne, colonne = struct.unpack_from("<HH", corps, 0)
                cellules[(ligne, colonne)] = _rk(
                    struct.unpack_from("<I", corps, 6)[0])
            elif type_ == 0x00BD and len(corps) >= 6:  # MULRK
                ligne, premiere = struct.unpack_from("<HH", corps, 0)
                nombre = (len(corps) - 6) // 6
                for k in range(nombre):
                    brut = struct.unpack_from("<I", corps, 4 + k * 6 + 2)[0]
                    cellules[(ligne, premiere + k)] = _rk(brut)
            elif type_ == 0x00FD and len(corps) >= 10:  # LABELSST
                ligne, colonne = struct.unpack_from("<HH", corps, 0)
                indice_chaine = struct.unpack_from("<I", corps, 6)[0]
                if indice_chaine < len(partagees):
                    cellules[(ligne, colonne)] = partagees[indice_chaine]
            elif type_ == 0x0204 and len(corps) >= 9:  # LABEL, chaîne non partagée
                ligne, colonne = struct.unpack_from("<HH", corps, 0)
                cellules[(ligne, colonne)] = _chaine_courte(corps, 6)
            elif type_ == 0x0006 and len(corps) >= 20:  # FORMULA, résultat en cache
                ligne, colonne = struct.unpack_from("<HH", corps, 0)
                cache = corps[6:14]
                if cache[6:8] != b"\xff\xff":
                    cellules[(ligne, colonne)] = struct.unpack("<d", cache)[0]
            position += 4 + longueur
        resultat[nom] = cellules
    return resultat
