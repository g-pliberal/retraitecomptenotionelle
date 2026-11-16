"""Le salaire moyen par tête d'une année, reconstitué de la série
certifiée de l'INSEE (``macro/salaire_moyen.csv`` et
``macro/salaire_moyen_niveau.csv``) : un niveau ancré, les croissances
cumulées de part et d'autre.

Logé ici depuis ``carriere.py``, tel quel (action 161, étape 4 de
l'inventaire du retrait des règles) : la fiche de paie (``remuneration.py``)
le lit sans le moteur Python, qui le reprend. Le moteur JavaScript a le sien
(``salaireMoyenAnnuel``), que le pont sert (``pont.salaires_moyens``).
"""

from __future__ import annotations

from .macro import DonneesMacro


#: L'année dont le NIVEAU du salaire moyen par tête ancre tous les autres :
#: celle où le coût agrégé ancre aussi la masse des pensions, et celle que le
#: site donne pour repère. Le niveau, lui, n'est pas écrit ici : voir
#: :func:`ancrage_salaire_moyen`.
ANNEE_ANCRAGE_SALAIRE_MOYEN = 2024


def ancrage_salaire_moyen(macro: DonneesMacro) -> tuple[int, float]:
    """Le point d'où se cumulent les croissances du salaire moyen : son année
    et son niveau, en euros bruts annuels courants.

    Le niveau est LU dans la série certifiée de l'INSEE
    (``macro/salaire_moyen_niveau.csv``) — les salaires et traitements bruts
    (D11) sur l'emploi salarié intérieur, base 2020 —, le rapport même dont
    ``macro/salaire_moyen.csv`` garde les croissances. Il était écrit à la
    main, 40 000 € en 2024, un arrondi de 2,2 % qui plaçait tous les cas types
    trop bas face au plafond et aux minima (action 147, étapes 15 et 16).
    Il est ici, en un seul endroit, parce que le site l'affiche — dire
    « 1 = salaire moyen » sans dire combien cela fait d'euros laissait toute la
    saisie dans le flou.
    """
    annee = ANNEE_ANCRAGE_SALAIRE_MOYEN
    return annee, macro.salaire_moyen_niveau(annee)


def salaire_moyen_annuel(macro: DonneesMacro, annee: int) -> float:
    """Salaire moyen par tête d'une année, en euros BRUTS courants de cette année."""
    return indice_salaire_moyen(macro, annee, annee)[annee]


def indice_salaire_moyen(macro: DonneesMacro, debut: int, fin: int) -> dict[int, float]:
    """Salaire moyen par tête reconstitué en euros courants de chaque année.

    Le montant est un salaire **BRUT** : la série de comptes nationaux dont il
    dérive est celle des salaires et traitements bruts (D11) rapportés à
    l'emploi salarié, c'est-à-dire avant cotisations salariales, avant CSG et
    avant impôt sur le revenu, cotisations patronales exclues. C'est la même
    assiette que celle sur laquelle les régimes appellent leurs cotisations :
    le niveau de revenu saisi, les cotisations versées et les pensions
    calculées sont donc tous bruts, et se comparent directement.

    Les CROISSANCES de la série se cumulent à partir du niveau d'une année,
    lu dans la même source (:func:`ancrage_salaire_moyen`) : les niveaux
    qu'elle publie, le cumul les refait à moins d'un dix-millième près, l'écart
    des cinq décimales auxquelles les croissances sont écrites. Ce niveau
    déplace proportionnellement tous les revenus reconstitués en multiples du
    salaire moyen, mais presque pas les RAPPORTS entre scénarios, qui sont
    l'objet du modèle : seuls le plafond de la Sécurité sociale et les minima,
    qui ne le suivent pas, en tirent de petits écarts.

    Ce n'est pas le « SMPT » des cas types du COR, que lit TRAJECTOiRE : un
    revenu moyen par tête, revenu mixte des non-salariés compris, rapporté à
    l'emploi total, qui croît moins vite depuis 2000. L'écart des deux
    croissances tient à ce concept, non à la série (action 147, étape 12).
    """
    ancrage_annee, ancrage_valeur = ancrage_salaire_moyen(macro)
    valeurs = {ancrage_annee: ancrage_valeur}

    borne_haute = max(fin, ancrage_annee)
    for annee in range(ancrage_annee + 1, borne_haute + 1):
        valeurs[annee] = valeurs[annee - 1] * (1 + macro.salaire_moyen(annee))

    borne_basse = min(debut, ancrage_annee)
    for annee in range(ancrage_annee - 1, borne_basse - 1, -1):
        valeurs[annee] = valeurs[annee + 1] / (1 + macro.salaire_moyen(annee + 1))

    return valeurs
