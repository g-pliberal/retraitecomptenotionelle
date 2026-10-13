"""Les tableaux référents du jaune pensions annexé au PLF 2027, lus case par case.

Les annexes A et B du jaune (action 159, étape 4) : le stock de pensions de la
fonction publique au 31 décembre 2025 (A-1 à A-6, A-8) et le flux de 2025, avec
ses séries depuis 2016 (B-1 à B-22). C'est ce que
``scripts/fetch/sre_jaune_pensions.py`` lit en plus des bonifications, et que
``scripts/verifier_donnees.py`` certifie dans
``data/reference/macro/caracteristiques_fonction_publique.csv`` — le B-22, les
bonifications du flux, dans ``legislation/bonifications_jaune.csv``, avec le
tableau 50. L'A-7 est lu par ``sre_jaune_pensions.py`` depuis l'étape 2.

**UNE CASE VIDE NE LAISSE RIEN DANS LE TEXTE D'UNE LIGNE.** Pas de total de
l'État sur la plupart des lignes du tableau B-1, pas de militaires sur celles
de la surcote : lue en texte, une ligne a six nombres pour huit colonnes, et
rien ne dit lesquels manquent. Chaque ligne se lit donc en fragments, chacun
à son abscisse (``lecture_pdf.fragments_par_page``). La première ligne du
tableau, qui a une case par colonne, place les colonnes ; une case de toute
autre ligne va à la colonne dont le milieu est le plus proche.

**CHAQUE TABLEAU A SON GABARIT** (:class:`Gabarit`) : ses colonnes, et ses
lignes dans l'ordre du document, chacune reconnue à son intitulé — que la
ligne porte, ou que portent les lignes d'intitulé qui l'encadrent, le jaune
posant certains intitulés au-dessus de leurs cases, d'autres en dessous,
d'autres de part et d'autre. Une ligne prise pour une autre, une ligne qui
manque, une case sans colonne font échouer la lecture plutôt qu'une valeur
rangée sous un autre nom ; une ligne de cases que le gabarit n'attend pas
aussi, sur la page de sa dernière ligne. Le tableau finit à la ligne
« Source », au titre d'un autre, ou avec sa page : le jaune pose certains
corps de tableau sur une page à eux, leurs titres et leurs sources sur une
autre.

**LA CLÉ D'UNE VALEUR** a quatre dimensions, que la colonne et la ligne
donnent ensemble, la ligne l'emportant :

* ``population`` : le régime ou la partie de régime (``fpe_civils``,
  ``fpe_militaires``, ``cnracl_total``…) ;
* ``champ`` : le droit (``droit_direct``, ``droit_derive``), le motif de
  départ, la catégorie ou le grade ; ``ensemble`` sinon ;
* ``modalite`` : ce que le tableau détaille encore — l'année d'une série,
  l'âge ou la tranche d'âge, le sexe, la catégorie hiérarchique, le grade — ;
  ``ensemble`` sinon ;
* ``indicateur`` : ce que la case mesure, dans son unité (l'en-tête du fichier
  certifié les énumère).

Ce que les tableaux disent les uns des autres se recoupe
(:func:`incoherences_referents`) : les sexes font l'effectif, les régimes leur
total, les âges, les catégories et les grades leur ensemble, et chaque case
que le document imprime deux fois l'est à l'identique. Sauf en douze points,
où le document se contredit : ses cases restent telles qu'il les imprime, et
chaque incohérence est déclarée (:data:`INCOHERENCES_DU_DOCUMENT`).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from lecture_pdf import texte_de_ligne

#: Les quatre dimensions de la clé d'une valeur, dans l'ordre du fichier.
DIMENSIONS = ("population", "champ", "modalite", "indicateur")
Cle = tuple[str, str, str, str]

#: Ce qui sépare deux mots ou deux cases ; l'insécable, elle, tient les
#: milliers d'un nombre.
ESPACES = re.compile(r"[ \t\r\n\f\v]+")
#: Les fragments d'un même mot se suivent à moins de six points : les
#: chiffres posés un à un, à la même abscisse, ou le signe moins, deux points
#: avant les siens. Au-delà, un nouveau mot commence — sauf de part et
#: d'autre d'une insécable, qui tient les milliers d'un nombre quelle que
#: soit la taille de ses chiffres : quatorze points et demi de « 343 » à
#: l'insécable qui le suit, au tableau A-1.
ECART_DANS_UN_MOT = 6.0
INSECABLES = "\u00a0\u202f"
#: Un renvoi à une note : « (5) », « (10) ».
RENVOI = re.compile(r"^\(\d+\)$")
#: Une case vide de sens : « n.d. », « n.d », « n.p. », « n.s. », renvoi
#: collé ou non, ou le tiret seul d'une case sans objet.
ABSENCE = re.compile(r"^(?:n\.?[dps]\.?(?:\(\d+\))?|-)$", re.IGNORECASE)
#: Un nombre de case : milliers tenus par l'insécable, ou collés (« 1230 »,
#: au tableau B-5), décimales à virgule, signe et « % » collés — « +0,60% »,
#: l'évolution annuelle moyenne d'une série.
NOMBRE_CASE = re.compile(r"^[-+]?(?:\d{1,3}(?:\u00a0\d{3})+|\d+)(?:,\d+)?%?$")
#: La largeur moyenne d'un caractère des tableaux, en points : de quoi
#: trouver le milieu d'une case centrée. « 39 146 » s'étend sur vingt
#: points, le tiret d'une case sans objet sur deux.
LARGEUR_CARACTERE = 3.5


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte)
                   if unicodedata.category(c) != "Mn").lower()


def _jetons(rangee: list[tuple[float, str]]) -> list[tuple[float, str]]:
    """Les mots d'une ligne de fragments (abscisse, texte), chacun avec
    l'abscisse où il commence.

    Un mot s'arrête à une espace ordinaire, que le document pose au bord de
    chaque case, ou à un saut de plus de :data:`ECART_DANS_UN_MOT` points
    hors d'une insécable. Ainsi les chiffres posés un à un se rejoignent,
    « 39 », l'insécable et « 146 » font « 39 146 », et le signe moins posé
    deux points avant ses chiffres fait un nombre négatif ; le tiret d'une
    case sans objet, que suit l'espace de sa case, reste seul."""
    jetons: list[list] = []
    ouvert = False
    precedente: float | None = None
    for x, morceau in rangee:
        insecable = ouvert and (jetons[-1][1][-1] in INSECABLES or morceau[:1] in INSECABLES)
        if precedente is not None and x - precedente > ECART_DANS_UN_MOT and not insecable:
            ouvert = False
        precedente = x
        for rang, partie in enumerate(ESPACES.split(morceau)):
            if rang:
                ouvert = False
            if not partie:
                continue
            if ouvert:
                jetons[-1][1] += partie
            else:
                jetons.append([x, partie])
                ouvert = True
    return [(x, re.sub(f"[{INSECABLES}]+", "\u00a0", texte)) for x, texte in jetons]


def _cases(rangee: list[tuple[float, str]], seuil: float) -> tuple[str, list[tuple[float, str]]]:
    """(intitulé, cases) d'une ligne. Les mots dont le milieu tombe avant
    ``seuil`` font l'intitulé ; après lui, les nombres et les marques
    d'absence sont les cases, chacune à l'abscisse de son milieu, le « % »
    détaché rendu à son nombre, les renvois écartés. Le milieu, et non le
    début : « 8 110 », centré dans la première colonne du tableau A-2,
    commence six points avant le « 37 » de sa ligne de référence."""
    mots: list[str] = []
    cases: list[tuple[float, str]] = []
    for x, jeton in _jetons(rangee):
        if x + LARGEUR_CARACTERE * len(jeton) / 2 < seuil:
            mots.append(jeton)
        elif RENVOI.match(jeton):
            continue
        elif jeton in ("%", "€") and cases and NOMBRE_CASE.match(cases[-1][1]):
            if jeton == "%":
                cases[-1] = (cases[-1][0], cases[-1][1] + "%")
        elif NOMBRE_CASE.match(jeton) or ABSENCE.match(jeton):
            cases.append((x, jeton))
        else:
            mots.append(jeton)
    return " ".join(mots), [(x + LARGEUR_CARACTERE * len(texte) / 2, texte)
                            for x, texte in cases]


def _valeur_case(jeton: str) -> float | int | None:
    """« 23 780 » → 23780 ; « 1230 » → 1230 ; « 64,2 » → 64.2 ; « 41,5% » →
    0.415 ; « -212,2 » → -212.2 ; « n.d. », le tiret seul → None."""
    if ABSENCE.match(jeton):
        return None
    if not NOMBRE_CASE.match(jeton):
        raise ValueError(f"pas une case du tableau : {jeton!r}")
    propre = jeton.rstrip("%").replace("\u00a0", "")
    nombre = float(propre.replace(",", "."))
    if jeton.endswith("%"):
        return round(nombre / 100, 6)
    return nombre if "," in propre else int(nombre)


@dataclass(frozen=True)
class Gabarit:
    """Ce qu'un tableau du jaune porte : ses colonnes, et ses lignes dans
    l'ordre du document.

    Chaque colonne est un dictionnaire des dimensions qu'elle fixe ; chaque
    ligne, un couple (dimensions, motif) : le motif reconnaît l'intitulé,
    sans accents — la police du document en perd —, que la ligne porte ou
    que portent les lignes d'intitulé qui l'encadrent ; ses dimensions
    l'emportent sur celles de la colonne. Une ligne d'en-tête (``entete``)
    se reconnaît sans se ranger : la ligne des années d'une série, qui place
    les colonnes. ``defaut`` donne les dimensions de tout le tableau ;
    ``rang`` dit quelle ligne de référence suivre après le titre — la
    seconde, pour un second bloc comme le droit dérivé du tableau A-1."""

    numero: str
    titre: str
    colonnes: tuple[dict, ...]
    lignes: tuple[tuple[dict, str], ...]
    rang: int = 0
    defaut: dict = field(default_factory=dict)
    #: Le motif de la ligne qui place les colonnes, quand ce n'est pas la
    #: première : au tableau B-10, l'État n'a pas de catégorie
    #: « indéterminée », et ses lignes n'ont pas toutes les colonnes.
    reference: str | None = None


def _l(motif: str, indicateur: str | None = None, **dimensions) -> tuple[dict, str]:
    """Une ligne de gabarit : son motif, et les dimensions qu'elle fixe —
    l'indicateur d'abord, quand la ligne le dit et non sa colonne."""
    if indicateur is not None:
        dimensions["indicateur"] = indicateur
    return dimensions, motif


def _cle(gabarit: Gabarit, colonne: dict, ligne: dict) -> Cle | None:
    """La clé d'une case : le défaut du tableau, puis sa colonne, puis sa
    ligne. ``None`` pour une ligne d'en-tête, qui ne se range pas."""
    if ligne.get("entete"):
        return None
    dimensions = {"champ": "ensemble", "modalite": "ensemble", **gabarit.defaut,
                  **colonne, **ligne}
    correspondance = dimensions.pop("indicateurs", None)
    if correspondance is not None:
        # Une ligne qui mesure autre chose que ses colonnes : l'âge moyen, sous
        # des colonnes de départs, dit à chacune ce qu'elle devient.
        dimensions["indicateur"] = correspondance[colonne["indicateur"]]
    elif "indicateur" in colonne:
        # L'indicateur d'une colonne l'emporte, lui : la colonne d'évolution
        # d'une série ne mesure pas ce que mesurent ses années.
        dimensions["indicateur"] = colonne["indicateur"]
    manquantes = [d for d in DIMENSIONS if not dimensions.get(d)]
    if manquantes:
        raise ValueError(f"{gabarit.numero} : dimensions manquantes {manquantes}")
    return tuple(str(dimensions[d]) for d in DIMENSIONS)


def _pages_apres_le_titre(positionnees: list[list[list[tuple[float, str]]]], titre: str
                          ) -> list[list[list[tuple[float, str]]]]:
    """Les pages qui suivent le titre d'un tableau, la sienne commençant
    après lui. Le titre se reconnaît à la ligne entière : « Tableau n°B - 3 »
    n'est pas « Tableau n°B - 3bis »."""
    for rang_page, page in enumerate(positionnees):
        for rang, rangee in enumerate(page):
            if sans_accents(texte_de_ligne(rangee)) == titre:
                return [page[rang + 1:], *positionnees[rang_page + 1:]]
    raise LookupError(f"le titre « {titre} » n'est sur aucune page")


def _apres_le_titre(positionnees: list[list[list[tuple[float, str]]]], titre: str
                    ) -> list[list[tuple[float, str]]]:
    """Les lignes qui suivent le titre d'un tableau, page après page."""
    return [rangee for page in _pages_apres_le_titre(positionnees, titre) for rangee in page]


def _etrangere(page: list[list[tuple[float, str]]], seuil: float, milieux: list[float],
               pas: float) -> bool:
    """Une page d'un autre tableau : sa première ligne de cases ne tient pas
    dans les colonnes de celui-ci. Le corps du tableau B-6 s'intercale ainsi,
    dans l'ordre de lecture, entre les deux moitiés du B-7, que coupe une
    page."""
    for rangee in page:
        _, cases = _cases(rangee, seuil)
        if cases:
            return len(cases) > len(milieux) or any(
                min(abs(m - x) for m in milieux) > pas / 2 for x, _ in cases)
    return False


def _contexte(zone: list[tuple[str, list]], k: int) -> str:
    """L'intitulé d'une ligne de cases : le sien, et ceux des lignes
    d'intitulé qui l'encadrent."""
    avant = zone[k - 1][0] if k > 0 and not zone[k - 1][1] else ""
    apres = zone[k + 1][0] if k + 1 < len(zone) and not zone[k + 1][1] else ""
    return " ".join(filter(None, (avant, zone[k][0], apres)))


def tableau_referent(positionnees: list[list[list[tuple[float, str]]]],
                     gabarit: Gabarit) -> dict[Cle, float | int | None]:
    """Un tableau référent, à plat : {(population, champ, modalite,
    indicateur): valeur}, une case sans objet valant ``None``.

    LA LIGNE DE RÉFÉRENCE PLACE LES COLONNES. C'est la première du gabarit :
    elle a une case par colonne, et le milieu de chacune. Une case de toute
    autre ligne va à la colonne dont le milieu est le plus proche. Puis
    chaque ligne de cases prend, dans l'ordre, la ligne que le gabarit
    attend, pourvu que son intitulé la reconnaisse. La lecture s'arrête à la
    ligne « Source » ; elle passe d'une page à la suivante, dont elle saute
    le numéro.
    """
    pages = _pages_apres_le_titre(positionnees, gabarit.titre)
    lignes = [rangee for page in pages for rangee in page]
    nombre = len(gabarit.colonnes)
    premier = gabarit.reference or gabarit.lignes[0][1]
    vues = 0
    for debut, rangee in enumerate(lignes):
        mots, cases = _cases(rangee, float("-inf"))
        # Une ligne de référence a une case pleine par colonne ; avant que
        # le seuil soit connu, le tiret d'un intitulé (« FPE - Pensions
        # civiles ») passerait pour une case sans objet.
        cases = [case for case in cases if NOMBRE_CASE.match(case[1])]
        if len(cases) != nombre:
            continue
        voisins = [lignes[j] for j in (debut - 1, debut + 1) if 0 <= j < len(lignes)]
        contexte = " ".join([mots] + [texte_de_ligne(v) for v in voisins
                                      if not _cases(v, float("-inf"))[1]])
        if re.search(premier, sans_accents(contexte)):
            if vues == gabarit.rang:
                break
            vues += 1
    else:
        raise LookupError(f"{gabarit.numero} : aucune ligne « {premier} » à {nombre} cases")
    milieux = [x for x, _ in cases]
    pas = min(b - a for a, b in zip(milieux, milieux[1:])) if nombre > 1 else 100.0
    if pas <= 0:
        raise ValueError(f"{gabarit.numero} : colonnes dans le désordre {milieux}")
    # Le bord gauche de la première colonne : un intitulé finit avant lui,
    # une case a son milieu après.
    seuil = milieux[0] - pas / 2
    if gabarit.reference is not None:
        # La lecture commence à la première ligne du gabarit, avant la
        # ligne de référence.
        debut = next(k for k, rangee in enumerate(lignes)
                     if _cases(rangee, seuil)[1] and re.search(
                         gabarit.lignes[0][1], sans_accents(_cases(rangee, seuil)[0])))

    if debut > 0 and not _cases(lignes[debut][:], seuil)[0] \
            and not _cases(lignes[debut - 1], seuil)[1]:
        # L'intitulé de la première ligne, quand elle n'en porte pas et qu'il
        # est posé au-dessus de ses cases (« Pensions civiles hors La Poste
        # et », au tableau B-12).
        debut -= 1
    zone: list[tuple[str, list[tuple[float, str]]]] = []
    page_de: list[int] = []
    avant = debut
    for rang_page, page in enumerate(pages):
        if avant >= len(page):
            avant -= len(page)
            continue
        suite = page[avant:]
        if avant == 0 and zone and _etrangere(suite, seuil, milieux, pas):
            continue
        avant = 0
        for rangee in suite:
            texte = sans_accents(texte_de_ligne(rangee))
            if texte.startswith("source") or re.match(r"tableau n\W", texte):
                break
            if re.fullmatch(r"\d{1,3}", texte):
                continue
            zone.append(_cases(rangee, seuil))
            page_de.append(rang_page)
        else:
            continue
        break

    # Un bloc que suit un autre bloc du même tableau — le droit direct du
    # A-1, que suit son droit dérivé — finit à sa dernière ligne. Le dernier
    # finit à la ligne « Source », au titre d'un autre tableau, ou avec sa
    # page : le jaune pose certains tableaux sur une page à eux, leur titre
    # et leurs sources sur une autre, et le corps du suivant vient ensuite.
    # Une ligne de cases au-delà de ce que le gabarit attend, sur la page de
    # sa dernière ligne, est une ligne qu'il oublie.
    suivi = any(g.numero == gabarit.numero and g.rang > gabarit.rang for g in GABARITS)
    lu: dict[Cle, float | int | None] = {}
    attendues = iter(gabarit.lignes)
    attendue = next(attendues)
    derniere = 0
    for k, (_, cases) in enumerate(zone):
        if not cases:
            continue
        contexte = _contexte(zone, k)
        if attendue is None:
            if suivi or page_de[k] != page_de[derniere]:
                break
            raise ValueError(f"{gabarit.numero} : « {contexte} », une ligne que le gabarit "
                             f"n'attend pas")
        dimensions, motif = attendue
        if not re.search(motif, sans_accents(contexte)):
            raise ValueError(f"{gabarit.numero} : « {contexte} » là où « {motif} » "
                             f"était attendu")
        rangs: dict[int, float | int | None] = {}
        for x, jeton in cases:
            colonne = min(range(nombre), key=lambda j: abs(milieux[j] - x))
            if abs(milieux[colonne] - x) > pas / 2 or colonne in rangs:
                raise ValueError(f"{gabarit.numero}, « {motif} » : la case « {jeton} » "
                                 f"n'a pas de colonne à elle")
            rangs[colonne] = _valeur_case(jeton)
        for colonne, valeur in rangs.items():
            cle = _cle(gabarit, gabarit.colonnes[colonne], dimensions)
            if cle is None:
                continue
            if cle in lu:
                # Une ligne au champ imposé ne prend qu'une case par
                # population : « Départ avec bénéfice d'une catégorie
                # active » n'en a qu'aux départs pour ancienneté.
                raise ValueError(f"{gabarit.numero} : deux cases pour {cle}")
            lu[cle] = valeur
        attendue = next(attendues, None)
        derniere = k
    if attendue is not None:
        raise ValueError(f"{gabarit.numero} : la ligne « {attendue[1]} » manque")
    return lu


# -- les gabarits ----------------------------------------------------------------

def _effectifs(motif: str, **dimensions) -> tuple[tuple[dict, str], ...]:
    """Un effectif de départs, et la part de chaque sexe."""
    return (_l(motif, "departs", **dimensions), _l(r"\bhommes", "part_hommes", **dimensions),
            _l(r"\bfemmes", "part_femmes", **dimensions))


#: Ce que les tableaux du flux disent de chaque colonne, dans l'ordre du
#: document : âges, durées, décote et surcote, taux et indice de
#: liquidation, minimum garanti, majoration pour enfants, pension.
CARACTERISTIQUES_DU_FLUX = tuple(_l(motif, indicateur) for indicateur, motif in (
    ("age_radiation", r"radiation des cadres"),
    ("age_premiere_mise_en_paiement", r"premi\w* mise en paiement"),
    ("part_remuneres_avant_liquidation", r"encore r\w*mun"),
    ("services_trimestres", r"services acquis"),
    ("bonifications_trimestres", r"bonifications acquises"),
    ("duree_tous_regimes_trimestres", r"assurance tous r"),
    ("part_decote", r"pensions avec d\w*cote"),
    ("perte_decote_eur", r"perte mensuelle"),
    ("taux_decote", r"taux moyen de d\w*cote"),
    ("cout_decote_meur", r"induit par la d\w*cote"),
    ("part_surcote", r"pensions avec surcote"),
    ("gain_surcote_eur", r"n\w*fice mensuel"),
    ("taux_surcote", r"taux moyen de surcote"),
    ("cout_surcote_meur", r"induit par la surcote"),
    ("taux_liquidation", r"taux moyen de liquidation(?! hors)"),
    ("taux_liquidation_hors_decote_surcote", r"liquidation hors"),
    ("part_taux_plein", r"taux plein"),
    ("part_taux_80", r"taux de 80"),
    ("indice_liquidation", r"indice moyen"),
    ("part_minimum_garanti", r"au minimum garanti"),
    ("majoration_enfants_eur", r"suppl\w*ment apport|majoration de pension pour"),
    ("part_majoration_enfants", r"cette majoration"),
    ("pension_principale_eur", r"avantage principal(?! et)"),
    ("pension_avec_accessoires_eur", r"avantage principal et accessoires"),
))

#: Les colonnes du flux de 2025 (tableau B-1) et du stock (tableau A-1).
POPULATIONS_B1 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires", "fpe_total",
                  "ouvriers_etat", "fpt", "fph", "cnracl_total")
POPULATIONS_A1 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires",
                  "ouvriers_etat", "fpt", "fph", "cnracl_total")
MOTIFS_DE_DEPART = ("anciennete", "motifs_familiaux", "invalidite")
SEXES = ("hommes", "femmes")
PENSION_DU_STOCK = (_l(r"avantage principal(?! et)", "pension_principale_eur"),
                    _l(r"avantage principal et accessoires", "pension_avec_accessoires_eur"))


def _colonnes(populations, champs=("ensemble",), **dimensions) -> tuple[dict, ...]:
    """Les colonnes d'un tableau : chaque population, et dans chacune chaque
    champ, dans l'ordre du document."""
    return tuple({"population": p, "champ": c, **dimensions} for p in populations for c in champs)


def _series(premiere: int, derniere: int, periode: str | None = None) -> tuple[dict, ...]:
    """Les colonnes d'une série : une par année, puis, si le tableau les
    donne, l'évolution sur la période et sa moyenne annuelle."""
    annees = tuple({"modalite": str(a)} for a in range(premiere, derniere + 1))
    if periode is None:
        return annees
    return annees + ({"modalite": periode, "indicateur": "evolution"},
                     {"modalite": periode, "indicateur": "evolution_annuelle"})


#: Les colonnes du flux par âge (tableaux B-6, B-8, B-9) : les départs pour
#: ancienneté ou motifs familiaux, de chaque sexe, dont les carrières longues,
#: les motifs familiaux et la catégorie active ; puis les départs pour
#: invalidité, de chaque sexe.
COLONNES_PAR_AGE = (
    {"champ": "anciennete_familiaux", "indicateur": "departs"},
    {"champ": "anciennete_familiaux", "indicateur": "departs_hommes"},
    {"champ": "anciennete_familiaux", "indicateur": "departs_femmes"},
    {"champ": "carriere_longue", "indicateur": "departs"},
    {"champ": "motifs_familiaux", "indicateur": "departs"},
    {"champ": "categorie_active", "indicateur": "departs"},
    {"champ": "invalidite", "indicateur": "departs"},
    {"champ": "invalidite", "indicateur": "departs_hommes"},
    {"champ": "invalidite", "indicateur": "departs_femmes"},
)
#: L'âge moyen, sous des colonnes de départs.
AGE_MOYEN = {"departs": "age_moyen", "departs_hommes": "age_moyen_hommes",
             "departs_femmes": "age_moyen_femmes"}


def _par_age(premier: int, dernier: int) -> tuple[tuple[dict, str], ...]:
    """Les lignes d'un tableau par âge : le total, chaque âge du premier au
    dernier, ceux d'avant et d'après, puis l'âge moyen."""
    return (_l(r"^total\b|\btotal$", modalite="ensemble"),
            _l(rf"^< ?{premier} ans", modalite=f"moins_de_{premier}"),
            *(_l(rf"^{age} ans", modalite=str(age)) for age in range(premier, dernier + 1)),
            _l(rf"^> ?{dernier} ans", modalite=f"plus_de_{dernier}"),
            _l(r"age moyen", indicateurs=AGE_MOYEN))


#: Ce que devient une colonne sur une ligne d'un seul sexe.
PAR_SEXE = {sexe: {"departs": f"departs_{sexe}",
                   "pension_principale_eur": f"pension_principale_{sexe}_eur",
                   "pension_avec_accessoires_eur": f"pension_avec_accessoires_{sexe}_eur"}
            for sexe in ("hommes", "femmes")}
#: Les catégories hiérarchiques des tableaux B-16 et B-17, l'ensemble d'abord.
CATEGORIES_HIERARCHIQUES = (("ensemble", r"^ensemble"), ("a", r"cat\w*gorie a\b"),
                            ("b", r"cat\w*gorie b\b"), ("c", r"cat\w*gorie c\b"),
                            ("indetermine", r"ind\w*termin"))
#: Les grades des militaires (tableaux B-18 et B-19) ; dans chaque sexe, le
#: document réunit officiers généraux et supérieurs.
GRADES_MILITAIRES = (("ensemble", r"^ensemble"), ("officiers_generaux", r"officiers g"),
                     ("officiers_superieurs", r"officiers sup"),
                     ("officiers_subalternes", r"officiers subalternes"),
                     ("sous_officiers", r"sous ?-officiers"), ("caporaux_soldats", r"caporaux"))
GRADES_MILITAIRES_PAR_SEXE = (("ensemble", None), ("officiers_generaux_superieurs", r"et sup"),
                              ("officiers_subalternes", r"officiers subalternes"),
                              ("sous_officiers", r"sous ?-officiers"),
                              ("caporaux_soldats", r"caporaux"))
#: Les populations du flux de 2024 et 2025 (tableau B-15) : sans l'ensemble de
#: la CNRACL.
POPULATIONS_B15 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires",
                   "ouvriers_etat", "fpt", "fph")
#: Les bonifications du flux (tableau B-22), avec le code du tableau 50, et le
#: motif de leur intitulé.
BONIFICATIONS_B22 = (("depaysement", r"hors d.europe"), ("enfant", r"pour enfant"),
                     ("campagne", r"campagne"), ("service_aerien_sous_marin", r"riens ou sous"),
                     ("enseignement_technique", r"enseignement technique"),
                     ("cinquieme_l12", r"cinqui"), ("hors_l12", r"l12"))


def _par_categorie(categories, par_sexe=None) -> tuple[tuple[dict, str], ...]:
    """Les lignes d'un tableau par catégorie et par sexe : chaque catégorie,
    puis, dans chaque sexe, chaque catégorie — la même liste, ou celle que le
    document donne aux sexes."""
    if par_sexe is None:
        lignes = []
        for modalite, motif in categories:
            lignes += [_l(motif, modalite=modalite),
                       *(_l(rf"\b{sexe}", modalite=modalite, indicateurs=PAR_SEXE[sexe])
                         for sexe in ("hommes", "femmes"))]
        return tuple(lignes)
    lignes = [_l(motif, modalite=modalite) for modalite, motif in categories]
    for sexe in ("hommes", "femmes"):
        lignes += [_l(motif or rf"\b{sexe}", modalite=modalite, indicateurs=PAR_SEXE[sexe])
                   for modalite, motif in par_sexe]
    return tuple(lignes)


#: Les tranches d'âge du stock (tableau A-2).
TRANCHES_A2 = ("moins_de_35", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69",
               "70-74", "75-79", "80-84", "85-89", "90-94", "plus_de_94", "ensemble")
#: L'intitulé de chaque population quand il ouvre sa ligne, sans accents.
INTITULES_A1 = (r"hors la poste et orange", r"toutes pensions civiles", r"pensions militaires",
                r"ouvriers d", r"\bfpt\b", r"\bfph\b", r"ensemble des pensions de la cnracl")
#: Les populations des déciles (tableau A-8) : les ouvriers de l'État n'y sont pas.
POPULATIONS_A8 = ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires", "fpt", "fph",
                  "cnracl_total")


GABARITS = (
    # Le stock au 31 décembre 2025.
    Gabarit("A-1", "tableau n°a - 1", _colonnes(POPULATIONS_A1, ("droit_direct",)), (
        _l(r"^effectif\b", "effectif"),
        _l(r"\bhommes", "effectif_hommes"),
        _l(r"\bfemmes", "effectif_femmes"),
        _l(r"age moyen(?! de)", "age_moyen"),
        _l(r"premi\w* mise en paiement", "age_premiere_mise_en_paiement"),
        _l(r"services acquis", "services_trimestres"),
        _l(r"taux moyen de liquidation", "taux_liquidation"),
        _l(r"indice moyen", "indice_liquidation"),
        *PENSION_DU_STOCK)),
    Gabarit("A-1", "tableau n°a - 1", _colonnes(POPULATIONS_A1, ("droit_derive",)), (
        _l(r"^effectif\b", "effectif"),
        _l(r"\bhommes", "effectif_hommes"),
        _l(r"\bfemmes", "effectif_femmes"),
        _l(r"orphelins", "effectif_orphelins"),
        _l(r"age moyen(?! de)", "age_moyen"),
        _l(r"premi\w* mise en paiement", "age_premiere_mise_en_paiement"),
        *PENSION_DU_STOCK), rang=1),
    # Le flux de 2025, en entier, par motif de départ, par catégorie et par grade.
    Gabarit("B-1", "tableau n°b - 1", _colonnes(POPULATIONS_B1), (
        *_effectifs(r"ensemble des d"),
        *_effectifs(r"pour invalidit", champ="invalidite"),
        *_effectifs(r"carri\w*re longue", champ="carriere_longue"),
        *_effectifs(r"motifs familiaux", champ="motifs_familiaux"),
        *_effectifs(r"cat\w*gorie active", champ="categorie_active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-2", "tableau n°b - 2", tuple(
        {"population": p, "modalite": s} for p in POPULATIONS_A1 for s in SEXES), (
        _l(r"ensemble des d", "departs"),
        _l(r"pour invalidit", "departs", champ="invalidite"),
        _l(r"carri\w*re longue", "departs", champ="carriere_longue"),
        _l(r"motifs familiaux", "departs", champ="motifs_familiaux"),
        _l(r"cat\w*gorie active", "departs", champ="categorie_active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-3", "tableau n°b - 3", _colonnes(
        ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires"), MOTIFS_DE_DEPART), (
        *_effectifs(r"ensemble des d"),
        *_effectifs(r"cat\w*gorie active", champ="categorie_active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-3bis", "tableau n°b - 3bis", _colonnes(
        ("fpt", "fph", "cnracl_total"), MOTIFS_DE_DEPART), (
        *_effectifs(r"ensemble des d"),
        *_effectifs(r"cat\w*gorie active", champ="categorie_active"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-4", "tableau n°b - 4", (
        *_colonnes(("fpe_civils_hors_poste_orange", "fpe_civils"),
                   ("sedentaire", "active_57", "active_52", "carriere_longue")),
        *_colonnes(("militaires_terre_mer_air", "militaires_gendarmerie"),
                   ("non_officiers", "officiers"))), (
        *_effectifs(r"ensemble des d"),
        *CARACTERISTIQUES_DU_FLUX)),
    Gabarit("B-5", "tableau n°b - 5", _colonnes(
        ("fpt", "fph", "cnracl_total"), ("sedentaire", "active", "carriere_longue")), (
        *_effectifs(r"ensemble des d"),
        *CARACTERISTIQUES_DU_FLUX)),
    # Le stock par tranche d'âge, ses effectifs et ses pensions moyennes
    # depuis 2016, celles de 2024 et de 2025, sa part au minimum garanti
    # depuis 2010, ses déciles.
    Gabarit("A-2", "tableau n°a - 2", tuple({"modalite": t} for t in TRANCHES_A2), tuple(
        ligne for population, orphelins in zip(POPULATIONS_A1, (True,) * 3 + (False,) * 4)
        for ligne in (
            _l(r"droit direct", "effectif", population=population, champ="droit_direct"),
            _l(r"\bhommes", "effectif_hommes", population=population, champ="droit_direct"),
            _l(r"\bfemmes", "effectif_femmes", population=population, champ="droit_direct"),
            _l(r"invalidit", "effectif_invalidite", population=population, champ="droit_direct"),
            _l(r"droit d\w*riv", "effectif", population=population, champ="droit_derive"),
            _l(r"\bhommes", "effectif_hommes", population=population, champ="droit_derive"),
            _l(r"\bfemmes", "effectif_femmes", population=population, champ="droit_derive"),
            *((_l(r"orphelins", "effectif_orphelins", population=population,
                  champ="droit_derive"),) if orphelins else ())))),
    Gabarit("A-3", "tableau n°a - 3", _series(2016, 2025, "2019-2025"), tuple(
        ligne for population in POPULATIONS_A1 for ligne in (
            _l(r"\btotal\b", "effectif", population=population),
            _l(r"droit direct", "effectif", population=population, champ="droit_direct"),
            _l(r"droit d\w*riv", "effectif", population=population, champ="droit_derive")))),
    Gabarit("A-4", "tableau n°a - 4", _series(2016, 2025, "2020-2025"), tuple(
        ligne for population, motif in zip(POPULATIONS_A1, INTITULES_A1) for ligne in (
            _l(motif, "pension_avec_accessoires_eur", population=population),
            _l(r"droit direct", "pension_avec_accessoires_eur", population=population,
               champ="droit_direct"),
            _l(r"droit d\w*riv", "pension_avec_accessoires_eur", population=population,
               champ="droit_derive")))),
    *(Gabarit("A-5", "tableau n°a - 5", tuple(
        {"population": p, "modalite": str(a)} for p in POPULATIONS_A1 for a in (2024, 2025)), (
        _l(r"^effectifs", "effectif"),
        _l(r"avantage principal", "pension_principale_eur"),
        _l(r"retraite totale", "pension_avec_accessoires_eur"),
        _l(r"\bhommes", "pension_avec_accessoires_hommes_eur"),
        _l(r"\bfemmes", "pension_avec_accessoires_femmes_eur")),
        rang=rang, defaut={"champ": champ})
      for rang, champ in enumerate(("droit_direct", "droit_derive"))),
    Gabarit("A-6", "tableau n°a - 6", tuple({"modalite": str(a)} for a in range(2010, 2026)),
            tuple(_l(motif, "part_minimum_garanti", population=population)
                  for population, motif in zip(POPULATIONS_A1, INTITULES_A1)),
            defaut={"champ": "droit_direct"}),
    # Le flux de 2025 par âge, et par sexe : l'État, ses militaires, la
    # territoriale, l'hospitalière.
    Gabarit("B-6", "tableau n°b - 6", (
        *(dict(population=p, **c) for p in ("fpe_civils_hors_poste_orange", "fpe_civils")
          for c in COLONNES_PAR_AGE),
        {"population": "fpe_civils", "indicateur": "departs"}), _par_age(40, 65)),
    Gabarit("B-7", "tableau n°b - 7", (
        {"indicateur": "departs"},
        *({"champ": grade, "indicateur": "departs"}
          for grade in ("caporaux_soldats", "sous_officiers", "officiers", "invalidite"))),
        _par_age(30, 58), defaut={"population": "fpe_militaires"}),
    *(Gabarit(numero, titre, (*COLONNES_PAR_AGE, {"indicateur": "departs"}), _par_age(40, 65),
              defaut={"population": population})
      for numero, titre, population in (("B-8", "tableau n°b - 8", "fpt"),
                                        ("B-9", "tableau n°b - 9", "fph"))),
    # Le flux de 2025 par administration, catégorie hiérarchique et sexe.
    Gabarit("B-10", "tableau n°b - 10", (
        *({"modalite": categorie, "indicateur": f"departs_{sexe}"}
          for categorie in ("a", "b", "c", "indetermine") for sexe in SEXES),
        {"indicateur": "departs"}), tuple(
        _l(motif, population=population, champ=champ) for motif, population, champ in (
            (r"^pensions civiles\b", "fpe_civils", "ensemble"),
            (r"hors la poste", "fpe_civils_hors_poste_orange", "ensemble"),
            (r"\baffaires\b", "fpe_civils", "affaires_etrangeres"),
            (r"agriculture", "fpe_civils", "agriculture"),
            (r"culture et communication", "fpe_civils", "culture"),
            (r"\(civils\)", "fpe_civils", "defense"),
            (r"cologie", "fpe_civils", "ecologie"),
            (r"aviation civile", "fpe_civils", "aviation_civile_meteo_france"),
            (r"budget, comptes publics", "fpe_civils", "economie_finances"),
            (r"enseignement sup", "fpe_civils", "education_nationale"),
            (r"recherche", "fpe_civils", "recherche"),
            (r"outre ?-mer", "fpe_civils", "interieur"),
            (r"\bjustice\b", "fpe_civils", "justice"),
            (r"premier ministre", "fpe_civils", "premier_ministre"),
            (r"travail, emploi", "fpe_civils", "travail_sante"),
            (r"\bla poste\b", "fpe_civils", "la_poste"),
            (r"\borange\b", "fpe_civils", "orange"),
            (r"\bmilitaires\b", "fpe_militaires", "ensemble"),
            (r"officiers g", "fpe_militaires", "officiers_generaux"),
            (r"officiers sup", "fpe_militaires", "officiers_superieurs"),
            (r"officiers subalternes", "fpe_militaires", "officiers_subalternes"),
            (r"sous ?-officiers", "fpe_militaires", "sous_officiers"),
            (r"caporaux", "fpe_militaires", "caporaux_soldats"),
            (r"gendarmes", "fpe_militaires", "gendarmerie"),
            (r"des arm", "fpe_militaires", "armees"),
            (r"territoriale et hospitali", "cnracl_total", "ensemble"),
            (r"de la fpt", "fpt", "ensemble"),
            (r"\br\w*gions\b", "fpt", "regions"),
            (r"partements", "fpt", "departements"),
            (r"tropoles", "fpt", "metropoles"),
            (r"\bcommunes\b", "fpt", "communes"),
            (r"sdis", "fpt", "sdis"),
            (r"action sociale", "fpt", "centres_action_sociale"),
            (r"urbaines", "fpt", "communautes_urbaines"),
            (r"\bsyndicats\b", "fpt", "syndicats"),
            (r"de communes", "fpt", "communautes_de_communes"),
            (r"offices publics", "fpt", "offices_habitation"),
            (r"autres collectivit\w* territoriales", "fpt", "autres_collectivites"),
            (r"de la fph", "fph", "ensemble"),
            (r"hospitaliers r", "fph", "centres_hospitaliers_regionaux"),
            (r"hospitaliers g", "fph", "centres_hospitaliers_generaux"),
            (r"pitaux locaux", "fph", "hopitaux_locaux"),
            (r"hospitaliers sp", "fph", "centres_hospitaliers_specialises"),
            (r"centres de soins", "fph", "centres_de_soins"),
            (r"sanitaire et social", "fph", "etablissements_sanitaires_sociaux"),
            (r"personnes", "fph", "hebergement_personnes_agees"),
            (r"autres collectivit\w* hospitali", "fph", "autres_collectivites"))),
        reference=r"territoriale et hospitali"),
    # Les pensions de réversion entrées en paiement en 2025.
    Gabarit("B-11", "tableau n°b - 11", tuple(
        {"population": p, "modalite": m} for p in POPULATIONS_B1
        for m in ("deces_en_activite", "deces_en_retraite")), (
        _l(r"^effectifs", "effectif"),
        _l(r"\bhommes", "effectif_hommes"),
        _l(r"\bfemmes", "effectif_femmes"),
        _l(r"orphelins", "effectif_orphelins"),
        _l(r"premi\w* mise", "age_premiere_mise_en_paiement"),
        *PENSION_DU_STOCK), defaut={"champ": "droit_derive"}),
    # Les pensions entrées en paiement chaque année depuis 2016.
    Gabarit("B-12", "tableau n°b - 12", _series(2016, 2025, "2020-2025"), tuple(
        ligne for population, motif in zip(POPULATIONS_B1, (
            r"hors la poste", r"^pensions civiles\b", r"pensions militaires",
            r"ensemble du r\w*gime de la fpe", r"ouvriers d", r"territoriale", r"hospitali",
            r"fpt et fph"))
        for ligne in (
            _l(motif, "entrees", population=population),
            _l(r"droit direct", "entrees", population=population, champ="droit_direct"),
            _l(r"droit d\w*riv", "entrees", population=population, champ="droit_derive")))),
    # Les décès de pensionnés en 2025, et la durée de perception des décédés.
    Gabarit("B-13", "tableau n°b - 13", tuple(
        {"champ": c, "modalite": m} for c in ("droit_direct", "droit_derive")
        for m in ("ensemble", *SEXES)), tuple(
        ligne for population, motif in (
            ("fpe_civils", r"fpe civils"), ("fpe_militaires", r"fpe militaires"),
            ("ouvriers_etat", r"ouvriers d"), ("fpt", r"fpt affili"), ("fph", r"fph affili"),
            ("cnracl_total", r"ensemble affili"))
        for ligne in (
            _l(motif, "deces", population=population),
            _l(r"dur\w*e moyenne de perception", "duree_perception_ans",
               population=population)))),
    # La pension, l'indice et le taux de liquidation du flux, de 2016 à 2025.
    Gabarit("B-14", "tableau n°b - 14", _series(2016, 2025), (
        _l(r"annees d.admission", entete=True),
        *(ligne for population in ("fpe_civils_hors_poste_orange", "fpe_civils",
                                   "fpe_militaires", "ouvriers_etat", "fpt", "fph",
                                   "cnracl_total")
          for ligne in (
              _l(r"pension mensuelle", "pension_avec_accessoires_eur", population=population,
                 champ="droit_direct"),
              _l(r"indice de liquidation", "indice_liquidation", population=population,
                 champ="droit_direct"),
              _l(r"taux de liquidation \(en %\)", "taux_liquidation", population=population,
                 champ="droit_direct"),
              *((_l(r"liquidation hors", "taux_liquidation_hors_decote_surcote",
                    population=population, champ="droit_direct"),)
                if population in ("ouvriers_etat", "fpt", "fph", "cnracl_total") else ()),
              _l(r"pension mensuelle", "pension_avec_accessoires_eur", population=population,
                 champ="droit_derive"))),
        # La valeur du point qui ramène les traitements à leur indice.
        _l(r"point d.indice", "valeur_point_annuelle_eur", population="fonction_publique"))),
    # Les pensions moyennes du flux de 2024 et de 2025.
    *(Gabarit("B-15", "tableau n°b - 15", tuple(
        {"population": p, "modalite": str(a)} for p in POPULATIONS_B15 for a in (2024, 2025)), (
        _l(r"^effectifs", "effectif"),
        _l(r"avantage principal", "pension_principale_eur"),
        _l(r"retraite totale", "pension_avec_accessoires_eur"),
        _l(r"\bhommes", "pension_avec_accessoires_hommes_eur"),
        _l(r"\bfemmes", "pension_avec_accessoires_femmes_eur"),
        *((_l(r"surcote", "gain_surcote_eur"), _l(r"d\w*cote", "perte_decote_eur"))
          if champ == "droit_direct" else ())),
        rang=rang, defaut={"champ": champ})
      for rang, champ in enumerate(("droit_direct", "droit_derive"))),
    # Les pensions du flux par catégorie hiérarchique et par sexe, hors
    # invalidité puis pour invalidité ; celles des militaires par grade.
    *(Gabarit(numero, titre, tuple(
        {"population": p, "indicateur": i}
        for p in ("fpe_civils_hors_poste_orange", "fpe_civils", "fpt", "fph", "cnracl_total")
        for i in ("departs", "pension_avec_accessoires_eur")),
        _par_categorie(CATEGORIES_HIERARCHIQUES), defaut={"champ": champ})
      for numero, titre, champ in (("B-16", "tableau n°b - 16", "hors_invalidite"),
                                   ("B-17", "tableau n°b - 17", "invalidite"))),
    *(Gabarit(numero, titre, tuple(
        {"indicateur": i} for i in ("departs", "pension_principale_eur",
                                    "pension_avec_accessoires_eur")),
        _par_categorie(GRADES_MILITAIRES, GRADES_MILITAIRES_PAR_SEXE),
        defaut={"population": "fpe_militaires", "champ": champ})
      for numero, titre, champ in (("B-18", "tableau n°b - 18", "hors_invalidite"),
                                   ("B-19", "tableau n°b - 19", "invalidite"))),
    # Les déciles du flux, sa part au minimum garanti depuis 2016, ses
    # bonifications.
    *(Gabarit("B-20", "tableau n°b - 20", tuple(
        {"population": p, "modalite": s} for p in POPULATIONS_A8
        for s in ("ensemble", "hommes", "femmes")), (
        _l(r"^effectifs", "effectif"),
        *(_l(rf"^{d}(er|e) d\w*cile", f"decile_{d}_eur") for d in range(1, 10))),
        rang=rang, defaut={"champ": champ})
      for rang, champ in enumerate(("droit_direct", "droit_derive"))),
    Gabarit("B-21", "tableau n°b - 21", _series(2016, 2025),
            tuple(_l(motif, "part_minimum_garanti", population=population)
                  for population, motif in zip(POPULATIONS_A1, (
                      r"hors la poste", r"toutes pensions civiles", r"pensions militaires",
                      r"ouvriers d", r"\bfpt\b", r"\bfph\b",
                      r"ensemble des pensions de la cnracl"))),
            defaut={"champ": "droit_direct"}),
    Gabarit("B-22", "tableau n°b - 22", tuple(
        {"population": p} for p in ("fpe_civils_hors_poste_orange", "fpe_civils",
                                    "fpe_militaires", "fpt", "fph")), (
        _l(r"effectif de pensions", "effectif"),
        *(ligne for code, motif in BONIFICATIONS_B22 for ligne in (
            _l(rf"(?=.*ficiaires)(?=.*{motif})", "beneficiaires", champ=code),
            _l(r"dur\w*e moyenne", "duree_trimestres", champ=code))))),
    *(Gabarit("A-8", "tableau n°a - 8", tuple(
        {"population": p, "modalite": s} for p in POPULATIONS_A8
        for s in ("ensemble", "hommes", "femmes")), (
        _l(r"^effectifs", "effectif"),
        *(_l(rf"^{d}(er|e) d\w*cile", f"decile_{d}_eur") for d in range(1, 10))),
        rang=rang, defaut={"champ": champ})
      for rang, champ in enumerate(("droit_direct", "droit_derive"))),
)


def referents(positionnees: list[list[list[tuple[float, str]]]]) -> dict[str, dict[Cle, object]]:
    """Les tableaux référents, par numéro ; les blocs d'un même tableau — le
    droit direct et le droit dérivé du A-1 — se rangent sous son numéro."""
    lu: dict[str, dict[Cle, object]] = {}
    for gabarit in GABARITS:
        tableau = lu.setdefault(gabarit.numero, {})
        for cle, valeur in tableau_referent(positionnees, gabarit).items():
            if cle in tableau:
                raise ValueError(f"{gabarit.numero} : deux blocs pour {cle}")
            tableau[cle] = valeur
    return lu


def en_json(lu: dict[str, dict[Cle, object]]) -> dict[str, list[list]]:
    """Les tableaux, pour le JSON : une liste de [population, champ,
    modalité, indicateur, valeur] par numéro."""
    return {numero: [[*cle, valeur] for cle, valeur in tableau.items()]
            for numero, tableau in lu.items()}


def depuis_json(tables: dict[str, list[list]]) -> dict[str, dict[Cle, object]]:
    return {numero: {tuple(ligne[:4]): ligne[4] for ligne in lignes}
            for numero, lignes in tables.items()}


# -- ce que les tableaux disent les uns des autres -----------------------------------

def _pourcent(part: float) -> str:
    return f"{part * 100:.1f} %".replace(".", ",")


#: Les tableaux dont les modalités partagent l'ensemble — les tranches d'âge
#: du stock, les âges du flux — : leurs cases font la ligne ou la colonne
#: « ensemble ».
PARTITIONS = frozenset({"A-2", "A-8", "B-6", "B-7", "B-8", "B-9", "B-13", "B-16", "B-17",
                        "B-18", "B-19", "B-20"})
#: Les indicateurs qui se somment : des comptes, non des moyennes.
COMPTES = ("effectif", "departs", "deces", "entrees")


#: Les régimes qui font un total, dans tout tableau qui les donne : l'État,
#: ses civils et ses militaires ; la CNRACL, la territoriale et
#: l'hospitalière.
REGIMES = {"fpe_total": ("fpe_civils", "fpe_militaires"), "cnracl_total": ("fpt", "fph")}


#: Les tableaux dont chaque ligne a son total, et ses parts par modalité et
#: par sexe : les catégories hiérarchiques du tableau B-10.
LIGNES_PAR_SEXE = frozenset({"B-10"})


def _recoupements() -> list[tuple[tuple, list[tuple]]]:
    """(total, parts) : chaque case que le document imprime deux fois, ou
    comme la somme d'autres, avec ses parts — clés à cinq dimensions, le
    tableau d'abord."""
    def depart(tableau, population, champ):
        return (tableau, population, champ, "ensemble", "departs")

    liste = [
        (depart("B-1", "fpe_civils", "ensemble"),
         [depart("B-3", "fpe_civils", m) for m in MOTIFS_DE_DEPART]),
        (depart("B-1", "fpe_militaires", "ensemble"),
         [depart("B-3", "fpe_militaires", m) for m in MOTIFS_DE_DEPART]),
        (depart("B-1", "cnracl_total", "ensemble"),
         [depart("B-3bis", "cnracl_total", m) for m in MOTIFS_DE_DEPART]),
        (depart("B-3", "fpe_civils", "anciennete"),
         [depart("B-4", "fpe_civils", c)
          for c in ("sedentaire", "active_57", "active_52", "carriere_longue")]),
    ]
    # Le flux par âge : ses totaux sont les départs du B-1 et du B-3.
    for population in ("fpe_civils_hors_poste_orange", "fpe_civils"):
        liste += [
            (depart("B-6", population, "anciennete_familiaux"),
             [depart("B-3", population, "anciennete"),
              depart("B-3", population, "motifs_familiaux")]),
            (depart("B-6", population, "invalidite"), [depart("B-3", population, "invalidite")]),
            *((depart("B-6", population, champ), [depart("B-1", population, champ)])
              for champ in ("carriere_longue", "motifs_familiaux", "categorie_active")),
        ]
    liste += [
        (depart("B-1", "fpe_civils", "ensemble"), [depart("B-6", "fpe_civils", "ensemble")]),
        (depart("B-1", "fpe_militaires", "ensemble"), [depart("B-7", "fpe_militaires", "ensemble")]),
        (depart("B-1", "fpe_militaires", "invalidite"),
         [depart("B-7", "fpe_militaires", "invalidite")]),
        (depart("B-7", "fpe_militaires", "ensemble"),
         [depart("B-7", "fpe_militaires", grade)
          for grade in ("caporaux_soldats", "sous_officiers", "officiers")]),
    ]
    liste += [(depart("B-1", population, "ensemble"), [depart("B-10", population, "ensemble")])
              for population in ("fpe_civils", "fpe_civils_hors_poste_orange", "fpe_militaires",
                                 "fpt", "fph", "cnracl_total")]
    # Les entrées de chaque année font leur droit direct et leur droit
    # dérivé, et celles de 2025 sont les départs du B-1 ; la série du flux,
    # en 2025, est la colonne du B-1.
    for population in POPULATIONS_B1:
        for annee in map(str, range(2016, 2026)):
            liste.append((("B-12", population, "ensemble", annee, "entrees"),
                          [("B-12", population, "droit_direct", annee, "entrees"),
                           ("B-12", population, "droit_derive", annee, "entrees")]))
        liste.append((depart("B-1", population, "ensemble"),
                      [("B-12", population, "droit_direct", "2025", "entrees")]))
    for population in ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires",
                       "ouvriers_etat", "fpt", "fph", "cnracl_total"):
        for indicateur in ("pension_avec_accessoires_eur", "indice_liquidation",
                           "taux_liquidation", "taux_liquidation_hors_decote_surcote")[
                :3 if population.startswith("fpe") else 4]:
            liste.append((("B-1", population, "ensemble", "ensemble", indicateur),
                          [("B-14", population, "droit_direct", "2025", indicateur)]))
    for tableau, population in (("B-8", "fpt"), ("B-9", "fph")):
        liste += [
            *((depart("B-1", population, champ), [depart(tableau, population, champ)])
              for champ in ("ensemble", "invalidite", "carriere_longue", "motifs_familiaux",
                            "categorie_active")),
            (depart(tableau, population, "ensemble"),
             [depart(tableau, population, "anciennete_familiaux"),
              depart(tableau, population, "invalidite")]),
        ]
    for population in POPULATIONS_A1:
        for champ in ("droit_direct", "droit_derive"):
            def a1(indicateur):
                return ("A-1", population, champ, "ensemble", indicateur)
            liste += [
                (a1("effectif"), [("A-2", population, champ, "ensemble", "effectif")]),
                (a1("effectif"), [("A-3", population, champ, "2025", "effectif")]),
                (a1("effectif"), [("A-5", population, champ, "2025", "effectif")]),
                (a1("pension_principale_eur"),
                 [("A-5", population, champ, "2025", "pension_principale_eur")]),
                (a1("pension_avec_accessoires_eur"),
                 [("A-5", population, champ, "2025", "pension_avec_accessoires_eur")]),
                (a1("pension_avec_accessoires_eur"),
                 [("A-4", population, champ, "2025", "pension_avec_accessoires_eur")]),
                (("A-3", population, champ, "2024", "effectif"),
                 [("A-5", population, champ, "2024", "effectif")]),
            ]
        for champ in ("ensemble", "invalidite", "carriere_longue", "motifs_familiaux",
                      "categorie_active"):
            liste.append((depart("B-1", population, champ),
                          [("B-2", population, champ, sexe, "departs") for sexe in SEXES]))
        for annee in map(str, range(2016, 2026)):
            liste.append((("A-3", population, "ensemble", annee, "effectif"),
                          [("A-3", population, "droit_direct", annee, "effectif"),
                           ("A-3", population, "droit_derive", annee, "effectif")]))
        # La part au minimum garanti du flux, en 2025, est celle du B-1.
        liste.append((("B-1", population, "ensemble", "ensemble", "part_minimum_garanti"),
                      [("B-21", population, "droit_direct", "2025", "part_minimum_garanti")]))
    # Les pensions du flux de 2024 et de 2025 : leurs effectifs sont les
    # entrées du B-12, leurs moyennes la série du B-14 et la colonne du B-1.
    for population in POPULATIONS_B15:
        for champ in ("droit_direct", "droit_derive"):
            for annee in ("2024", "2025"):
                liste += [
                    (("B-15", population, champ, annee, "effectif"),
                     [("B-12", population, champ, annee, "entrees")]),
                    (("B-15", population, champ, annee, "pension_avec_accessoires_eur"),
                     [("B-14", population, champ, annee, "pension_avec_accessoires_eur")]),
                ]
        liste.append((("B-1", population, "ensemble", "ensemble", "pension_principale_eur"),
                      [("B-15", population, "droit_direct", "2025", "pension_principale_eur")]))
    # Le flux par catégorie (B-16, B-17) et par grade (B-18, B-19), hors
    # invalidité puis pour invalidité : ses totaux sont les motifs de départ du
    # B-3, du B-3 bis, des B-8 et B-9 ; ses déciles (B-20), hors invalidité
    # aussi, en ont les effectifs, sexe par sexe ; ses bonifications (B-22),
    # l'effectif du B-1.
    hors_invalidite = {
        "fpe_civils_hors_poste_orange": [depart("B-3", "fpe_civils_hors_poste_orange", m)
                                         for m in ("anciennete", "motifs_familiaux")],
        "fpe_civils": [depart("B-3", "fpe_civils", m) for m in ("anciennete", "motifs_familiaux")],
        "fpt": [depart("B-8", "fpt", "anciennete_familiaux")],
        "fph": [depart("B-9", "fph", "anciennete_familiaux")],
        "cnracl_total": [depart("B-3bis", "cnracl_total", m)
                         for m in ("anciennete", "motifs_familiaux")],
    }
    for population, termes in hors_invalidite.items():
        liste += [
            (depart("B-16", population, "hors_invalidite"), termes),
            (depart("B-17", population, "invalidite"), [depart("B-1", population, "invalidite")]),
        ]
    liste += [
        (depart("B-18", "fpe_militaires", "hors_invalidite"),
         [depart("B-3", "fpe_militaires", m) for m in ("anciennete", "motifs_familiaux")]),
        (depart("B-19", "fpe_militaires", "invalidite"),
         [depart("B-1", "fpe_militaires", "invalidite")]),
    ]
    for population in POPULATIONS_A8:
        tableau = "B-18" if population == "fpe_militaires" else "B-16"
        for sexe, suffixe in (("ensemble", ""), ("hommes", "_hommes"), ("femmes", "_femmes")):
            liste.append((("B-20", population, "droit_direct", sexe, "effectif"),
                          [(tableau, population, "hors_invalidite", "ensemble",
                            f"departs{suffixe}")]))
    for population in ("fpe_civils_hors_poste_orange", "fpe_civils", "fpe_militaires", "fpt",
                       "fph"):
        liste.append((depart("B-1", population, "ensemble"),
                      [("B-22", population, "ensemble", "ensemble", "effectif")]))
    return liste


def incoherences_referents(lu: dict[str, dict[Cle, object]]) -> list[str]:
    """Ce que les tableaux référents disent contre eux-mêmes, ou contre leurs
    voisins : une colonne lue de travers, une ligne prise pour une autre, s'y
    verraient. Les hommes et les femmes font l'effectif, ou cent pour cent ;
    le total de l'État, ses civils et ses militaires ; celui de la CNRACL, la
    territoriale et l'hospitalière ; les motifs de départ du tableau B-3,
    l'ensemble des départs du B-1 ; les catégories des civils partis pour
    ancienneté au B-4, leur colonne du B-3."""
    messages: list[str] = []
    for tableau, valeurs in lu.items():
        groupes: dict[tuple[str, str, str], dict[str, object]] = {}
        for (population, champ, modalite, indicateur), valeur in valeurs.items():
            groupes.setdefault((population, champ, modalite), {})[indicateur] = valeur
        for (population, champ, modalite), indicateurs in groupes.items():
            hommes, femmes = indicateurs.get("part_hommes"), indicateurs.get("part_femmes")
            if hommes is not None and femmes is not None and abs(hommes + femmes - 1) > 0.0015:
                messages.append(f"{tableau}, {population}, {champ}, {modalite} : "
                                f"{_pourcent(hommes)} d'hommes et {_pourcent(femmes)} de femmes")
            for compte, autres in (("effectif", ("effectif_orphelins",)), ("departs", ())):
                total = indicateurs.get(compte)
                parts = [indicateurs.get(f"{compte}_{sexe}") for sexe in SEXES]
                if total is None or None in parts:
                    continue
                somme = sum(parts) + sum(indicateurs.get(a) or 0 for a in autres)
                if somme != total:
                    messages.append(f"{tableau}, {population}, {champ}, {modalite} : les "
                                    f"sexes font {somme}, pour {total} ({compte})")

    for tableau, valeurs in lu.items():
        for (population, champ, modalite, indicateur), total in valeurs.items():
            parties = REGIMES.get(population)
            if parties is None or total is None or not indicateur.startswith(COMPTES):
                continue
            termes = [valeurs.get((p, champ, modalite, indicateur)) for p in parties]
            if None not in termes and abs(sum(termes) - total) > 1e-6:
                messages.append(f"{tableau}, {population}, {champ}, {modalite}, {indicateur} : "
                                f"{total}, et {sum(termes)} dans {' et '.join(parties)}")
    for tableau in PARTITIONS & set(lu):
        totaux: dict[tuple[str, str, str], list] = {}
        for (population, champ, modalite, indicateur), valeur in lu[tableau].items():
            if not indicateur.startswith(COMPTES):
                continue
            entree = totaux.setdefault((population, champ, indicateur), [None, 0, 0])
            if modalite == "ensemble":
                entree[0] = valeur
            elif valeur is not None:
                entree[1] += valeur
                entree[2] += 1
        for (population, champ, indicateur), (ensemble, somme, parts) in totaux.items():
            if ensemble is not None and parts and abs(somme - ensemble) > 1e-6:
                messages.append(f"{tableau}, {population}, {champ}, {indicateur} : "
                                f"{ensemble} au total, {somme} dans ses modalités")
    for tableau in LIGNES_PAR_SEXE & set(lu):
        lignes: dict[tuple[str, str], list] = {}
        for (population, champ, modalite, indicateur), valeur in lu[tableau].items():
            entree = lignes.setdefault((population, champ), [None, 0])
            if modalite == "ensemble" and indicateur == "departs":
                entree[0] = valeur
            elif indicateur in ("departs_hommes", "departs_femmes") and valeur is not None:
                entree[1] += valeur
        for (population, champ), (total, somme) in lignes.items():
            if total is not None and total != somme:
                messages.append(f"{tableau}, {population}, {champ} : {total} départs, "
                                f"{somme} dans ses catégories et ses sexes")
    for total, termes in _recoupements():
        if not {total[0], *(terme[0] for terme in termes)} <= set(lu):
            # Un tableau que la lecture n'a pas rendu : rien à recouper.
            continue
        attendu = lu[total[0]].get(total[1:])
        trouves = [lu[terme[0]].get(terme[1:]) for terme in termes]
        if attendu is None:
            # Le total que le document ne donne pas — les carrières longues
            # des militaires, la catégorie active des ouvriers de l'État —
            # ne se recoupe pas.
            continue
        if None in trouves:
            messages.append(f"{' / '.join(total)} : une case manque pour le recoupement")
        elif abs(sum(trouves) - attendu) > 1e-6:
            messages.append(f"{' / '.join(total)} : {attendu}, et {sum(trouves)} dans "
                            f"{', '.join(t[0] for t in termes)}")
    return messages


#: CE QUE LE DOCUMENT DIT CONTRE LUI-MÊME, tel qu'il l'imprime : chaque
#: incohérence de l'édition 2027, par le motif des messages qu'elle donne,
#: avec ce qu'on en sait. Les cases restent telles que le jaune les imprime,
#: comme celle du tableau 50 ; une incohérence qui n'est pas ici est une
#: lecture de travers, et une incohérence d'ici que la lecture ne trouve plus,
#: une case qui a changé.
INCOHERENCES_DU_DOCUMENT: tuple[tuple[str, str], ...] = (
    (r"^tableau 50, fpe_civils : l'ensemble ",
     "Au tableau 50, 4,0 % des civils de l'État liquidants portent la bonification pour "
     "enfant, quand l'ensemble est à 56,7 % et que le B-22 en compte 20 736 sur 47 104, "
     "44,0 % : un chiffre manque à la case (``sre_jaune_pensions.incoherences_50``)."),
    (r"^B-11, ouvriers_etat, droit_derive, deces_en_(activite|retraite) : les sexes font",
     "Au B-11, l'effectif des réversions des ouvriers de l'État ne compte pas leurs "
     "orphelins (10 et 2), quand celui des autres régimes les compte : 416 et 832, pour "
     "426 et 834 avec eux."),
    (r"^B-2, cnracl_total, categorie_active, (hommes|femmes), departs : "
     r"|^B-1 / cnracl_total / categorie_active / ensemble / departs : ",
     "Au B-2, la CNRACL compte 13 237 départs en catégorie active (3 434 hommes, 9 803 "
     "femmes), quand sa territoriale et son hospitalière en comptent 10 597, comme le B-1."),
    (r"^B-13, cnracl_total, droit_direct, (ensemble, )?deces : ",
     "Au B-13, la CNRACL compte 30 726 décès de pensionnés de droit direct, un de plus "
     "que ses sexes et que sa territoriale et son hospitalière."),
    (r"^B-17, (fph|cnracl_total), invalidite, departs(_hommes)? : ",
     "Au B-17, les catégories des départs pour invalidité de l'hospitalière font 604 "
     "hommes, deux de moins que leur total (606)."),
    (r"^B-6, fpe_civils_hors_poste_orange, categorie_active, departs : ",
     "Au B-6, les âges des départs en catégorie active des civils hors La Poste et "
     "Orange font 8 129, deux de plus que leur total (8 127)."),
    (r"^B-8, fpt, .* dans ses modalités$",
     "Au B-8, les âges ne font, dans chaque colonne, que les neuf dixièmes du total : "
     "42 018 départs de la territoriale, pour 46 897."),
    (r"^B-9, fph, .* dans ses modalités$",
     "Au B-9, les âges ne font, dans chaque colonne, que les neuf dixièmes du total : "
     "19 986 départs de l'hospitalière, pour 22 753."),
    (r"^B-8 / fpt / ensemble / ensemble / departs : ",
     "Au B-8, le total des départs de la territoriale, 46 897 comme au B-1, dépasse de "
     "102 ses départs pour ancienneté ou motifs familiaux et pour invalidité (46 795)."),
    (r"^B-9 / fph / ensemble / ensemble / departs : ",
     "Au B-9, le total des départs de l'hospitalière, 22 753 comme au B-1, dépasse de "
     "16 ses départs pour ancienneté ou motifs familiaux et pour invalidité (22 737)."),
    (r"^B-16 / cnracl_total / hors_invalidite / ensemble / departs : ",
     "La CNRACL compte 57 670 départs hors invalidité au B-16, la somme des B-8 et B-9, "
     "et 57 756 au B-3 bis, dont les départs pour invalidité (11 894) ne sont pas ceux "
     "du B-1 (11 862)."),
    (r"^B-20 / (fpt|fph|cnracl_total) / droit_direct / \w+ / effectif : ",
     "Au B-20, les effectifs de la territoriale et de l'hospitalière ne sont pas ceux "
     "de leurs départs hors invalidité (B-8, B-9, B-16) : 38 301 et 19 363, pour 38 279 "
     "et 19 391."),
    (r"^B-1 / ouvriers_etat / ensemble / ensemble / taux_liquidation",
     "Les ouvriers de l'État partis en 2025 ont un taux de liquidation de 61,1 % au B-1, "
     "de 60,9 % dans la série du B-14 ; hors décote et surcote, 60,4 % et 60,2 %."),
)


def incoherences_declarees(messages: list[str]) -> tuple[list[str], list[str]]:
    """(inattendues, disparues) : les messages qu'aucune incohérence déclarée
    n'explique, et les incohérences déclarées qu'aucun message ne montre
    plus."""
    inattendues = [m for m in messages
                   if not any(re.search(motif, m) for motif, _ in INCOHERENCES_DU_DOCUMENT)]
    disparues = [explication for motif, explication in INCOHERENCES_DU_DOCUMENT
                 if not any(re.search(motif, m) for m in messages)]
    return inattendues, disparues
