"""Les fiches de régime telles qu'elles sont écrites, lues année par année.

Une fiche s'écrit en quatre blocs (``structure``, ``liquidation``,
``cotisation``, ``servi``), chacun en lignes datées. Les confrontations au
droit comparent, année après année, ce qu'elle écrit à ce que les textes
disent : :func:`periodes_ecrites` leur rend, pour chaque suite d'années où
rien ne change, ce que les lignes écrivent, valeurs telles qu'écrites (un
renvoi reste le nom de sa fiche). La ligne d'une année est celle en vigueur
au 1er janvier, comme le moteur la lit, ou, l'année où le bloc commence, sa
première ligne ; la cotisation garde une ligne par tranche.
"""

from __future__ import annotations

from datetime import date


def _jour(valeur) -> date:
    return valeur if isinstance(valeur, date) else date.fromisoformat(str(valeur))


def _ligne_de_l_annee(lignes: list[dict], annee: int) -> dict | None:
    """La ligne en vigueur au 1er janvier, ou, l'année où le bloc commence, sa
    première ligne. Une ligne sans ``au`` court jusqu'à la suivante."""
    lignes = sorted(lignes, key=lambda l: _jour(l["du"]))
    jour = date(annee, 1, 1)
    for ligne, suivante in zip(lignes, [*lignes[1:], None]):
        au = ligne.get("au") or (suivante and suivante["du"])
        if _jour(ligne["du"]) <= jour and (au is None or jour < _jour(au)):
            return ligne
    return next((l for l in lignes if _jour(l["du"]).year == annee), None)


def _champs(*lignes: dict) -> dict:
    """Les champs des lignes, la dernière l'emportant ; leurs ``textes``, qui
    datent les renvois, réunis sous ``textes_des_renvois``."""
    champs: dict = {}
    textes: dict = {}
    for ligne in lignes:
        champs.update({c: v for c, v in ligne.items()
                       if c not in ("du", "au", "notes", "textes", "tranche")})
        textes.update(ligne.get("textes") or {})
    if textes:
        champs["textes_des_renvois"] = textes
    return champs


def _structure(fiche: dict, annee: int) -> dict:
    structure = dict(fiche["structure"])
    coupes = structure.get("points_de")
    if isinstance(coupes, list):
        ligne = _ligne_de_l_annee(coupes, annee)
        structure["points_de"] = ligne and ligne.get("regime")
    return structure


def _annee(fiche: dict, annee: int) -> tuple[dict, ...]:
    """Ce que les lignes écrivent pour l'année : un dictionnaire par tranche."""
    liquidation = _ligne_de_l_annee(fiche["liquidation"], annee)
    if liquidation is None:
        return ()
    servi = _ligne_de_l_annee(fiche.get("servi") or [], annee) or {}
    return tuple(
        {**_structure(fiche, annee), **_champs(servi, liquidation, ligne)}
        for ligne in fiche["cotisation"]
        if _jour(ligne["du"]).year <= annee
        and (ligne.get("au") is None or annee < _jour(ligne["au"]).year))


def periodes_ecrites(fiche: dict) -> list[dict]:
    """Les périodes d'une fiche écrite : ``debut`` et ``fin`` en années (``fin``
    à ``None`` si la dernière reste ouverte), et les champs que ses lignes
    écrivent, une période par tranche."""
    lignes = [*fiche["liquidation"], *fiche["cotisation"], *(fiche.get("servi") or [])]
    premiere = min(_jour(l["du"]).year for l in fiche["cotisation"])
    ouverte = any(l.get("au") is None for l in fiche["cotisation"])
    # Ouverte, la fiche se lit jusqu'à l'année qui suit sa dernière ligne :
    # une ligne née en cours d'année ne vaut qu'au 1er janvier suivant.
    derniere = (max(_jour(l["du"]).year for l in lignes) + 1 if ouverte
                else max(_jour(l["au"]).year for l in fiche["cotisation"]) - 1)
    periodes: list[dict] = []
    courantes: list[dict] = []
    avant = None
    for annee in range(premiere, derniere + 1):
        ecrit = _annee(fiche, annee)
        if ecrit == avant:
            for periode in courantes:
                periode["fin"] = annee
            continue
        courantes = [{**champs, "debut": annee, "fin": annee} for champs in ecrit]
        periodes.extend(courantes)
        avant = ecrit
    if ouverte:
        for periode in courantes:
            periode["fin"] = None
    return periodes
