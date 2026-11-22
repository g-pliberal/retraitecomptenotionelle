"""Les deux axes du fichier de régime, et la vue ancienne qu'on en fabrique.

Note de décision 0009, amendement du 22 novembre 2026. Un fichier de régime
range ses paramètres en quatre blocs, un par famille de champ :

- ``structure`` : ce qui décrit le régime (``type_calcul``, ``points_de``) ;
- ``liquidation`` : des lignes au jour, ``[du, au)``, choisies à la date
  d'effet de la pension — contiguës, jamais deux à la fois ;
- ``cotisation`` : des lignes choisies à l'année où le droit s'acquiert ;
  deux lignes du même jour sont deux tranches, que ``tranche`` numérote ;
- ``servi`` : des lignes au jour, les montants que le service revalorise.

Chaque ligne est complète : elle ne s'hérite pas de la précédente. Ses
``textes`` sont ceux des renvois qu'elle ouvre, ses ``notes`` la commentent.

PENDANT LE GEL (étapes 2 à 5 de l'amendement), le moteur lit encore des
périodes, qui portaient les quatre familles ensemble. :func:`vue_ancienne` les
refait : une période par ligne de cotisation, dans l'ordre du fichier, avec
la liquidation, le servi et la structure en vigueur à sa date d'effet. Elle
part avec la vue, à l'étape 5.
"""

from __future__ import annotations

import datetime as dt

#: Les quatre blocs, dans l'ordre où le fichier les écrit.
BLOCS = ("structure", "liquidation", "cotisation", "servi")

#: Ce qui décrit le régime ou découpe le fichier.
STRUCTURE = frozenset({"type_calcul", "points_de"})

#: Un montant en euros d'une année, que le service revalorise ensuite, et
#: son millésime.
SERVI = frozenset({
    "valeur_point_euros", "valeur_point_annee",
    "pension_forfaitaire_annuelle", "pension_forfaitaire_annee",
    "plafond_majoration_enfants", "plafond_majoration_annee",
})

#: Un paramètre choisi à l'année où le droit s'acquiert : l'assiette et ses
#: bornes, les taux et leurs parts, les forfaits et les classes, les points
#: que l'année ouvre et ce qui les marque, la dispense et l'exemption.
COTISATION = frozenset({
    "assiette", "assiette_annee_de_revenu", "assiette_de_debut",
    "assiette_de_debut_en_bases_mensuelles", "assiette_facteur_revenu",
    "assiette_forfaitaire", "assiette_grille", "assiette_minimale_pass",
    "assiette_plancher", "assiette_repere_smic", "smic_du_mois",
    "borne_basse_euros", "borne_basse_par_annee", "borne_haute_euros",
    "borne_haute_par_annee", "plafond_primes_traitement",
    "taux_cotisation_retraite", "perimetre_taux", "part_salariale",
    "taux_cotisation_deplafonnee", "part_salariale_deplafonnee",
    "cotisation_forfaitaire_euros", "cotisation_forfaitaire_annee",
    "cotisation_par_classes", "part_assurance_maladie_forfait",
    "part_assurance_maladie_taux", "dispense_de_debut", "exemption_passe_l_age",
    "taux_calcul_points", "points_maximum", "points_au_prorata_des_cotisations",
    "points_minimum_annuels", "points_par_trimestre_valide",
    "points_ajustement_par_forfait", "points_ajustement_maximum",
    "points_ajustement_au_plafond", "points_invalidite", "bareme_points",
    "points_abattus_a_l_age",
})

#: Ce qu'une ligne porte en plus de ses champs.
BORNES = ("du", "au")
COMMENTAIRES = ("textes", "notes")


def famille(champ: str) -> str:
    """Le bloc d'un champ de période : tout ce qui n'est ni de la structure,
    ni servi, ni de la cotisation est de la liquidation."""
    if champ in STRUCTURE:
        return "structure"
    if champ in SERVI:
        return "servi"
    if champ in COTISATION:
        return "cotisation"
    return "liquidation"


def _jour(valeur) -> dt.date:
    if isinstance(valeur, dt.date):
        return valeur
    return dt.date.fromisoformat(str(valeur))


def _au(ligne: dict) -> dt.date | None:
    return None if ligne.get("au") is None else _jour(ligne["au"])


def _premier_janvier(annee: int) -> dt.date:
    return dt.date(annee, 1, 1)


def _en_vigueur(lignes: list[dict], jour: dt.date) -> dict | None:
    for ligne in lignes:
        au = _au(ligne)
        if _jour(ligne["du"]) <= jour and (au is None or jour < au):
            return ligne
    return None


def _verifier(code: str, bloc: str, lignes: list[dict]) -> None:
    hors = {"tranche"} if bloc == "cotisation" else set()
    for ligne in lignes:
        if "du" not in ligne:
            raise ValueError(f"{code} : une ligne de `{bloc}` sans `du`")
        etrangers = sorted(c for c in ligne
                           if c not in BORNES + COMMENTAIRES and c not in hors
                           and famille(c) != bloc)
        etrangers += sorted(c for c in ligne.get("textes", {}) if famille(c) != bloc)
        if etrangers:
            raise ValueError(f"{code} : la ligne de `{bloc}` du {ligne['du']} porte "
                             f"des champs d'un autre bloc : {etrangers}")
    if bloc in ("liquidation", "servi"):
        # Au jour, contiguës, jamais deux à la fois : chaque période d'hier
        # trouve sa ligne au premier jour de sa date d'effet.
        for avant, apres in zip(lignes, lignes[1:]):
            if _jour(apres["du"]) <= _jour(avant["du"]):
                raise ValueError(f"{code} : les lignes de `{bloc}` s'écrivent dans l'ordre "
                                 f"de leurs dates, et celle du {apres['du']} suit celle du "
                                 f"{avant['du']}")
            if _au(avant) is None or _au(avant) > _jour(apres["du"]):
                raise ValueError(f"{code} : deux lignes de `{bloc}` se chevauchent "
                                 f"le {apres['du']}")
            if _au(avant) < _jour(apres["du"]):
                raise ValueError(f"{code} : un trou dans `{bloc}`, du {_au(avant)} au "
                                 f"{apres['du']}")
    if bloc == "cotisation":
        # Le passage au jour lèvera cette contrainte, non la forme.
        for ligne in lignes:
            for jour in (_jour(ligne["du"]), _au(ligne)):
                if jour is not None and (jour.month, jour.day) != (1, 1):
                    raise ValueError(f"{code} : une ligne de `cotisation` se borne au "
                                     f"1er janvier jusqu'au passage au jour, pas au {jour}")
        par_tranche: dict[int, list[dict]] = {}
        for ligne in lignes:
            par_tranche.setdefault(ligne.get("tranche", 1), []).append(ligne)
        for tranche, siennes in par_tranche.items():
            siennes = sorted(siennes, key=lambda l: _jour(l["du"]))
            for avant, apres in zip(siennes, siennes[1:]):
                if _au(avant) is None or _au(avant) > _jour(apres["du"]):
                    raise ValueError(f"{code} : deux lignes de la tranche {tranche} de "
                                     f"`cotisation` couvrent ensemble le {apres['du']}")


def _bornes_au_jour(fiche: dict, cotisation: list[dict]) -> dict[int, dt.date]:
    """Les dates d'effet qui ne tombent pas un 1er janvier, rendues à l'année
    où la période ancienne les ouvrait.

    Une période ancienne liquidait les pensions de ses années, sauf à déclarer
    ``date_effet`` : une borne au jour, à moins d'un an du 1er janvier de son
    année. Chaque borne au jour d'une ligne de liquidation, de servi ou du
    barème du point est celle d'une période : elle va à la frontière d'années
    la plus proche dont le 1er janvier n'est pas déjà une borne."""
    bornes: set[dt.date] = set()
    for bloc in ("liquidation", "servi"):
        for ligne in fiche.get(bloc) or ():
            bornes.add(_jour(ligne["du"]))
            if _au(ligne) is not None:
                bornes.add(_au(ligne))
    points_de = fiche["structure"].get("points_de")
    if isinstance(points_de, list):
        bornes |= {_jour(x["du"]) for x in points_de}
    frontieres = sorted({_jour(l["du"]).year for l in cotisation}
                        | {_au(l).year for l in cotisation if _au(l) is not None})
    attribuees: dict[int, dt.date] = {}
    for jour in sorted(bornes):
        if (jour.month, jour.day) == (1, 1) and jour.year in frontieres:
            continue
        candidates = sorted(
            (abs((jour - _premier_janvier(a)).days), a) for a in frontieres
            if _premier_janvier(a - 1) < jour < _premier_janvier(a + 1)
            and _premier_janvier(a) not in bornes and a not in attribuees)
        if not candidates:
            raise ValueError(f"{fiche.get('code')} : la borne du {jour} ne tombe à moins "
                             "d'un an d'aucune frontière d'années de la cotisation")
        if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
            raise ValueError(f"{fiche.get('code')} : la borne du {jour} est à égale "
                             "distance de deux frontières d'années")
        attribuees[candidates[0][1]] = jour
    return attribuees


def vue_ancienne(fiche: dict) -> dict:
    """La fiche en périodes, telle que le moteur la lit pendant le gel.

    Une période par ligne de cotisation, dans l'ordre du fichier : ses années
    sont celles de la ligne ; sa date d'effet, celle que les bornes au jour
    lui rendent (:func:`_bornes_au_jour`), déclarée seulement quand elle
    diffère de ses années ; ses champs, ceux de sa ligne de cotisation et des
    lignes de liquidation et de servi en vigueur au premier jour de sa date
    d'effet. Sa note est celle de sa ligne de cotisation, sinon celle de la
    ligne de liquidation, puis de servi, qui commence ce jour-là, pour la
    première période qui commence ce jour-là."""
    code = fiche.get("code")
    if "periodes" in fiche:
        raise ValueError(f"{code} : un fichier en quatre blocs ne porte plus de `periodes`")
    structure = fiche["structure"]
    liquidation = list(fiche["liquidation"])
    cotisation = list(fiche["cotisation"])
    servi = list(fiche.get("servi") or ())
    if set(structure) - STRUCTURE:
        raise ValueError(f"{code} : `structure` ne porte que {sorted(STRUCTURE)}, "
                         f"pas {sorted(set(structure) - STRUCTURE)}")
    for bloc, lignes in (("liquidation", liquidation), ("cotisation", cotisation),
                         ("servi", servi)):
        _verifier(code, bloc, lignes)
    au_jour = _bornes_au_jour(fiche, cotisation)
    points_de = structure.get("points_de")

    periodes: list[dict] = []
    debuts_vus: set[dt.date] = set()
    for ligne in cotisation:
        debut = _jour(ligne["du"]).year
        fin = None if _au(ligne) is None else _au(ligne).year - 1
        effet_debut = au_jour.get(debut, _premier_janvier(debut))
        effet_fin = None if fin is None else au_jour.get(fin + 1, _premier_janvier(fin + 1))
        periode: dict = {"debut": debut, "fin": fin}
        if (effet_debut, effet_fin) != (_premier_janvier(debut),
                                        None if fin is None else _premier_janvier(fin + 1)):
            periode["date_effet"] = [effet_debut, effet_fin]
        periode["type_calcul"] = structure["type_calcul"]
        if isinstance(points_de, list):
            emprunts = [x for x in points_de if _jour(x["du"]) <= effet_debut]
            if not emprunts:
                raise ValueError(f"{code} : `points_de` ne dit rien au {effet_debut}")
            periode["points_de"] = emprunts[-1]["regime"]
        elif points_de is not None:
            periode["points_de"] = points_de
        textes: dict = {}
        en_vigueur = [_en_vigueur(liquidation, effet_debut)]
        if servi:
            en_vigueur.append(_en_vigueur(servi, effet_debut))
        for bloc, autre in zip(("liquidation", "servi"), en_vigueur):
            if autre is None:
                raise ValueError(f"{code} : aucune ligne de {bloc} au {effet_debut}, où "
                                 f"commence la cotisation du {ligne['du']}")
        for autre in en_vigueur + [ligne]:
            periode.update({c: v for c, v in autre.items()
                            if c not in BORNES + COMMENTAIRES + ("tranche",)})
            textes.update(autre.get("textes", {}))
        if textes:
            periode["textes_des_renvois"] = textes
        premiere = effet_debut not in debuts_vus
        debuts_vus.add(effet_debut)
        if "notes" in ligne:
            periode["notes"] = ligne["notes"]
        elif premiere:
            for lignes in (liquidation, servi):
                ouvre = next((l for l in lignes if _jour(l["du"]) == effet_debut), None)
                if ouvre is not None and "notes" in ouvre:
                    periode["notes"] = ouvre["notes"]
                    break
        periodes.append(periode)

    vue = {c: v for c, v in fiche.items() if c not in BLOCS}
    vue["periodes"] = periodes
    return vue
