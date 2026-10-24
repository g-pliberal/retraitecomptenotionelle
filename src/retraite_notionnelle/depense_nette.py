"""La CSG effective, et la dépense nette à la manière de l'Ageing Report.

CE QUE LES PRÉLÈVEMENTS RETIRENT VRAIMENT À LA MASSE DES PENSIONS. Au taux
plein, la CSG, la CRDS et la CASA prennent 9,1 % d'une pension depuis 2019
(8,3 + 0,5 + 0,3), et la cotisation maladie 1 % d'une complémentaire. Mais
22 % des retraités de droit direct sont exonérés de CSG, 13 % au taux réduit,
22 % au taux médian (EACR, Ancetre 2024), et les retraités qui résident hors de
France ne paient rien. Le taux qui pèse sur la MASSE se lit dans deux moyennes
que la DREES publie sur les mêmes retraités, la pension brute et la pension
nette de « la CSG, la CRDS, la Casa et la cotisation maladie sur les retraites
complémentaires » (:func:`taux_effectifs`) : 6,8 % de la pension totale en
2022, 6,2 % en 2008, 7,6 % en 2018, l'année de la hausse de la CSG que le taux
médian de 2019 a reprise en partie. Les têtes par taux de CSG n'en donnent
qu'une borne basse (:func:`borne_par_les_tetes`) : les exonérés ont les plus
petites pensions, et pèsent moins dans la masse que dans l'effectif.

Les deux séries sont dans ``tests/temoins/drees_pension_nette.json``
(``scripts/fetch/drees_pension_nette.py``) ; ce module ne les lit pas, il les
reçoit. Les montants sont aussi certifiés dans
``data/reference/macro/pensions_brutes_nettes.csv`` (24 octobre 2026) :
``DepensesRetraite.taux_effectif`` les lit, et chaque année du bilan de la page
Coût en tire la dépense nette de chaque système (``SoldeAnnuel.depense_nette``),
que la page ne montre pas encore. L'effet retour d'une baisse des pensions
(:mod:`.effet_retour`, action 138, étape 5) n'en a pas l'usage : il chiffre les
prélèvements sur la distribution des pensions, au barème de chaque année.

LA DÉPENSE NETTE DE L'AWG. L'Ageing Report publie, à côté de la dépense brute
de pensions, ce que l'État en reprend en impôts (« public pension scheme, tax
revenues ») : 1,60 point de PIB en 2022 sur 14,45, 11,1 %, une part qui ne
bouge pas jusqu'en 2070 (:func:`part_reprise_par_l_awg`). Elle est plus large
que les prélèvements sociaux : l'impôt sur le revenu y est, que la pension
nette de la DREES n'ôte pas. Le dépôt n'agrège pas encore l'impôt des
retraités ; sa dépense nette (:func:`depense_nette`) est donc nette des seuls
prélèvements sociaux, au dernier taux observé, tenu constant comme l'AWG tient
le sien (:func:`taux_projetes`). L'écart des deux parts, un peu plus de quatre
points de la dépense brute, est l'impôt sur le revenu des pensions, environ 0,6 point
de PIB : un ordre de grandeur, que l'agrégation de l'impôt (étape 5) dira.

Ce que la convention suppose, et que la proposition ne dit pas : que ses
retraités paient les mêmes prélèvements, en part de leur pension, que ceux du
droit en vigueur. C'est l'hypothèse que le site fait déjà pour la pension
nette d'une personne (« la réforme ne change pas vos prélèvements », décision
du 4 octobre 2026, étape 2) ; le taux effectif de chaque système n'en diffère
donc que par la répartition de ses pensions entre les tranches, que le modèle
ne projette pas.
"""

from __future__ import annotations

import datetime as dt
from typing import Mapping, Sequence

from .somme import somme_ordonnee

#: Les taux de CSG d'une pension, sous les noms de la feuille de l'EACR et des
#: séries de ``prelevements_historiques.yaml``. L'exonéré ne paie ni CSG, ni
#: CRDS, ni CASA ; le taux réduit paie la CRDS sans la CASA (L. 14-10-4 du code
#: de l'action sociale et des familles) ; le médian et le plein paient les
#: trois.
TAUX_CSG: tuple[str, ...] = ("reduit", "median", "plein")


def taux_effectifs(montants: Mapping[int, Mapping[str, float]],
                   pension: str = "totale") -> dict[int, float]:
    """La part de la masse brute que les prélèvements sociaux retirent, chaque
    année publiée : un moins le rapport des pensions moyennes nette et brute,
    de droit direct (``pension="directe"``) ou totale, droit dérivé et
    majoration pour trois enfants compris."""
    return {annee: 1.0 - valeurs[f"nette_{pension}"] / valeurs[f"brute_{pension}"]
            for annee, valeurs in sorted(montants.items())}


def taux_du_bareme(prelevements, jour: dt.date, taux: str) -> float:
    """La CSG, la CRDS et la CASA d'une pension au taux de CSG ``taux`` ce
    ``jour``, en part du brut ; zéro pour l'exonéré."""
    if taux == "exonere":
        return 0.0
    p = prelevements.pensions
    resultat = prelevements.taux_csg_pension(jour, taux) + p["crds"].valeur(jour)
    if taux != "reduit":
        resultat += p["casa"].valeur(jour)
    return resultat


def borne_par_les_tetes(repartition: Mapping[str, float], prelevements,
                        jour: dt.date) -> float:
    """Le taux moyen que paieraient les retraités d'une répartition par taux de
    CSG (exonérés, réduit, médian, plein, inconnu, ensemble : des effectifs) si
    leurs pensions étaient égales. Les pensions exonérées étant les plus
    petites, c'est une borne basse du taux sur la masse ; elle omet aussi la
    cotisation maladie des complémentaires. Le taux inconnu est réparti comme
    les autres."""
    connus = somme_ordonnee(repartition[taux] for taux in ("exonere", *TAUX_CSG))
    return somme_ordonnee(repartition[taux] / connus * taux_du_bareme(prelevements, jour, taux)
                          for taux in TAUX_CSG)


def taux_projetes(observes: Mapping[int, float], annees: Sequence[int]) -> dict[int, float]:
    """Le taux de chaque année : l'observé quand il l'est, le plus proche
    sinon — le dernier après la dernière année publiée, comme l'AWG tient sa
    part constante, le premier avant la première."""
    publiees = sorted(observes)
    if not publiees:
        raise ValueError("aucun taux observé")
    resultat: dict[int, float] = {}
    for annee in annees:
        if annee in observes:
            resultat[annee] = observes[annee]
        elif annee > publiees[-1]:
            resultat[annee] = observes[publiees[-1]]
        else:
            resultat[annee] = observes[publiees[0]]
    return resultat


def depense_nette(part_pib: Mapping[int, float], taux: Mapping[int, float]) -> dict[int, float]:
    """La dépense de chaque année, nette des prélèvements au taux de l'année,
    dans l'unité de ``part_pib``."""
    return {annee: valeur * (1.0 - taux[annee]) for annee, valeur in part_pib.items()}


def part_reprise_par_l_awg(series: Mapping[str, Mapping[int, float]]) -> dict[int, float]:
    """La part de la dépense brute que l'Ageing Report compte reprise en impôts
    et en prélèvements, chaque année : ``recettes_fiscales / depense_brute``,
    deux séries de son témoin (``tests/temoins/ageing_report_france.json``)."""
    brute = series["depense_brute"]
    return {annee: valeur / brute[annee]
            for annee, valeur in sorted(series["recettes_fiscales"].items())}
