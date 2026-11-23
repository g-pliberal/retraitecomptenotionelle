"""Les deux axes du fichier de régime.

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
La vue en périodes, qui portait les quatre familles ensemble, est partie à
l'étape 5 de l'amendement.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Mapping, Sequence

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
    "points_abattus_a_l_age", "duree_requise_des_annuites",
    # Les taux propres du non-salarié, que le chargeur date année par année
    # depuis `taux_cotisation_annuels.csv` : aucun fichier ne les écrit.
    "taux_cotisation_non_salarie", "taux_cotisation_deplafonnee_non_salarie",
})

#: Ce qu'une ligne porte en plus de ses champs.
BORNES = ("du", "au")
COMMENTAIRES = ("textes", "notes")


def famille(champ: str) -> str:
    """Le bloc d'un champ de paramètres : tout ce qui n'est ni de la structure,
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


def verifier_les_blocs(fiche: dict) -> None:
    """Refuse un fichier de régime dont les blocs ne tiennent pas : un champ
    hors de son bloc, une ligne sans ``du``, deux lignes au jour qui se
    chevauchent ou laissent un trou, une tranche de cotisation couverte deux
    fois, une année cotisée sans règle de liquidation, un servi écrit qui ne
    couvre pas toute la liquidation, ou des ``periodes``, qu'un fichier
    n'écrit plus."""
    code = fiche.get("code")
    if "periodes" in fiche:
        raise ValueError(f"{code} : un fichier en quatre blocs ne porte plus de `periodes`")
    structure = fiche["structure"]
    if set(structure) - STRUCTURE:
        raise ValueError(f"{code} : `structure` ne porte que {sorted(STRUCTURE)}, "
                         f"pas {sorted(set(structure) - STRUCTURE)}")
    for bloc in ("liquidation", "cotisation", "servi"):
        _verifier(code, bloc, list(fiche.get(bloc) or ()))
    # Chaque année cotisée trouve une règle de liquidation dans sa première
    # année : une liquidation qui commence plus tard en laisserait sans.
    liquidation = fiche["liquidation"]
    for ligne in fiche["cotisation"]:
        annee = _jour(ligne["du"]).year
        if not any(_jour(l["du"]) < dt.date(annee + 1, 1, 1)
                   and (_au(l) is None or _au(l) > dt.date(annee, 1, 1)) for l in liquidation):
            raise ValueError(f"{code} : aucune ligne de liquidation en {annee}, où "
                             f"commence la cotisation du {ligne['du']}")
    # Un servi écrit couvre toute la liquidation : une pension qui prend effet
    # un jour sans ligne servie n'aurait rien à assembler.
    servi = list(fiche.get("servi") or ())
    if servi:
        if _jour(servi[0]["du"]) > _jour(liquidation[0]["du"]):
            raise ValueError(f"{code} : aucune ligne de servi au {liquidation[0]['du']}, "
                             "où commence la liquidation")
        fin, terme = _au(servi[-1]), _au(liquidation[-1])
        if fin is not None and (terme is None or fin < terme):
            raise ValueError(f"{code} : aucune ligne de servi au {servi[-1]['au']}, "
                             "que la liquidation couvre encore")


def en_vigueur_au_jour(lignes: Sequence[Mapping], jour: str) -> Mapping | None:
    """La ligne au jour en vigueur ce jour-là (AAAA-MM-JJ), ou ``None``
    (``enVigueurAuJour``)."""
    for ligne in lignes:
        if ligne["du"] <= jour and (ligne["au"] is None or jour < ligne["au"]):
            return ligne
    return None


def tranches_de_l_annee(lignes: Sequence[Mapping], annee: int) -> list[Mapping]:
    """Les lignes de cotisation qui couvrent l'année, dans l'ordre : ses tranches
    (``tranchesDeLAnnee``)."""
    return [l for l in lignes if l["du"] <= annee and (l["au"] is None or annee <= l["au"])]
