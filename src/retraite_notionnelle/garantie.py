"""Ce que coûte la garantie vieillesse, chiffrée sur la distribution des pensions.

La garantie vieillesse du scénario 6 est une allocation DIFFÉRENTIELLE : elle ne
verse que ce qui manque à la pension pour atteindre un plancher — 800 € par mois,
plus 250 € d'allocation d'isolement pour qui vit seul. Son coût est donc
entièrement celui de la queue basse de la distribution des pensions, et c'est
précisément ce qu'une grille de treize cas types ne sait pas décrire : la page
« Coût » ne la voit que par ceux d'entre eux qui liquident à 65 ans ou après —
cinq pour les générations récentes, aucun pour celles d'avant 1955 —, ce qui
revient à lire un plancher sur un échantillon de cinq personnes.

Ce module applique le barème à la distribution publiée par la DREES. Il ne
simule rien : il additionne, tranche par tranche, ce qui manque à chacune.

TROIS CONVENTIONS, ET CE QU'ELLES VALENT
-----------------------------------------
1. **Uniformité dans la tranche.** Les pensions d'une tranche de cent euros sont
   supposées réparties uniformément entre ses bornes. L'erreur est bornée par la
   largeur de la tranche et joue dans les deux sens d'une tranche à l'autre.
2. **La tranche ouverte est une masse ponctuelle** à sa borne inférieure. Au-
   dessus du plancher — le cas ordinaire — elle ne coûte rien de toute façon.
3. **La situation de foyer n'est pas connue.** L'enquête dit la pension, pas
   avec qui l'on vit. On ne choisit donc pas : les deux planchers sont calculés
   et affichés, celui de qui vit à deux et celui de qui vit seul. Le coût réel
   est entre les deux, et la source qui dirait où ne serait pas celle-ci.

CE QUE LE FACTEUR FAIT, ET CE QU'IL NE FAIT PAS
------------------------------------------------
À ``facteur = 1``, le barème est appliqué aux pensions TELLES QU'ELLES SONT :
c'est ce que la garantie coûterait aujourd'hui, en remplacement de l'ASPA, et ce
chiffre ne doit rien au modèle. Un facteur inférieur à un déplace toute la
distribution dans le même rapport, pour dire ce que la garantie coûterait une
fois les pensions devenues celles du scénario 6. Cette translation est
proportionnelle et uniforme, alors que le scénario 6 ne déplace pas toutes les
carrières du même rapport : le second chiffre est un ORDRE DE GRANDEUR là où le
premier est un calcul.
"""

from __future__ import annotations

from dataclasses import dataclass

from .donnees.distribution import DistributionPensions


@dataclass(frozen=True)
class CoutGarantie:
    """Le coût annuel d'un plancher, et qui en bénéficie."""

    #: Plancher mensuel appliqué, dans les euros de la distribution.
    plancher_mensuel: float
    #: Rapport par lequel toutes les pensions ont été déplacées avant le barème.
    facteur: float
    #: Part des retraités dont la pension tombe sous le plancher.
    part_beneficiaires: float
    #: Nombre de retraités concernés.
    beneficiaires: float
    #: Complément moyen versé à un bénéficiaire, par mois.
    complement_moyen_mensuel: float
    #: Coût annuel total, en millions d'euros de la distribution.
    cout_annuel_meur: float


def _manque_moyen(borne_inferieure: float, borne_superieure: float | None,
                  plancher: float) -> tuple[float, float]:
    """Part de la tranche sous le plancher, et manque MOYEN sur toute la tranche.

    Le manque moyen est rapporté à la tranche entière et non aux seuls
    bénéficiaires : c'est lui qu'il faut multiplier par l'effectif de la tranche
    pour obtenir la dépense. Le manque moyen d'un bénéficiaire s'en déduit en
    divisant par la part concernée, et le module le fait une fois pour toutes.
    """
    if borne_superieure is None:
        # Masse ponctuelle : ou bien tout le monde est sous le plancher, ou bien
        # personne. Convention 2 du module.
        manque = max(0.0, plancher - borne_inferieure)
        return (1.0, manque) if manque > 0 else (0.0, 0.0)
    if borne_superieure <= plancher:
        return 1.0, plancher - (borne_inferieure + borne_superieure) / 2.0
    if borne_inferieure >= plancher:
        return 0.0, 0.0
    largeur = borne_superieure - borne_inferieure
    concernee = (plancher - borne_inferieure) / largeur
    # Sur la seule fraction concernée, le manque décroît linéairement de
    # ``plancher - borne_inferieure`` à zéro : sa moyenne en est la moitié.
    return concernee, concernee * (plancher - borne_inferieure) / 2.0


def cout_garantie(distribution: DistributionPensions, effectif_total: float,
                  plancher_mensuel: float, facteur: float = 1.0) -> CoutGarantie:
    """Applique un plancher différentiel à la distribution, et en tire la dépense.

    ``plancher_mensuel`` est exprimé dans les euros de la distribution : c'est à
    l'appelant de l'y ramener, parce que lui seul sait dans quels euros son
    barème est écrit.
    """
    if facteur <= 0:
        raise ValueError("le facteur de déplacement doit être strictement positif")

    part_beneficiaires = 0.0
    manque_mensuel = 0.0
    for tranche in distribution.tranches:
        superieure = (
            None if tranche.borne_superieure is None
            else tranche.borne_superieure * facteur
        )
        concernee, manque = _manque_moyen(
            tranche.borne_inferieure * facteur, superieure, plancher_mensuel
        )
        part_beneficiaires += tranche.part * concernee
        manque_mensuel += tranche.part * manque

    beneficiaires = part_beneficiaires * effectif_total
    return CoutGarantie(
        plancher_mensuel=plancher_mensuel,
        facteur=facteur,
        part_beneficiaires=part_beneficiaires,
        beneficiaires=beneficiaires,
        complement_moyen_mensuel=(
            manque_mensuel / part_beneficiaires if part_beneficiaires else 0.0
        ),
        cout_annuel_meur=manque_mensuel * effectif_total * 12.0 / 1e6,
    )


def facteurs_par_sexe(moyenne_femmes: float, moyenne_hommes: float,
                      part_femmes: float, facteur: float,
                      rapport: float) -> tuple[float, float]:
    """Les deux facteurs de déplacement, sous contrainte de masse.

    Le modèle déplace toute la distribution d'un FACTEUR UNIQUE, lu sur la
    grille de cas types. Le scénario 6 ne déplace pourtant pas toutes les
    carrières du même rapport : il retire les droits non contributifs, et les
    femmes en détiennent plus souvent. De combien, personne ne le publie, et
    la grille ne le dira pas — un seul de ses treize cas types est une femme.

    Ce que cette fonction fait n'est donc pas de supposer l'écart, mais de le
    PARAMÉTRER par le seul rapport ``r = f_F / f_H``, en imposant que la
    moyenne d'ensemble bouge du même facteur qu'avant :

        w·μ_F·f_F + (1−w)·μ_H·f_H = f·(w·μ_F + (1−w)·μ_H)

    La contrainte est ce qui fait de l'exercice une RÉPARTITION et non une
    hypothèse de plus : la grille garde le dernier mot sur l'agrégat, et il ne
    reste à décider que le partage entre les deux sexes. À ``rapport = 1``,
    les deux facteurs valent ``facteur`` et l'on retrouve la convention en
    vigueur.
    """
    if rapport <= 0.0:
        raise ValueError("le rapport des deux facteurs doit être strictement positif")
    ensemble = part_femmes * moyenne_femmes + (1.0 - part_femmes) * moyenne_hommes
    denominateur = (part_femmes * moyenne_femmes * rapport
                    + (1.0 - part_femmes) * moyenne_hommes)
    if ensemble <= 0.0 or denominateur <= 0.0:
        raise ValueError("les pensions moyennes doivent être strictement positives")
    facteur_hommes = facteur * ensemble / denominateur
    return rapport * facteur_hommes, facteur_hommes


def pension_moyenne(distribution: DistributionPensions) -> float:
    """Pension moyenne de la distribution, dans ses propres euros.

    Même convention que :func:`cout_garantie` : le milieu de chaque tranche, et
    la tranche ouverte à sa borne inférieure. Les deux moyennes en sont
    sous-estimées, celle des hommes un peu plus — ils sont plus nombreux dans
    la tranche ouverte —, mais seul leur RAPPORT entre dans la contrainte de
    :func:`facteurs_par_sexe`, et repousser la tranche ouverte de 4 500 à
    6 500 € le déplace de 0,641 à 0,624.
    """
    return sum(
        tranche.part * (
            tranche.borne_inferieure if tranche.borne_superieure is None
            else 0.5 * (tranche.borne_inferieure + tranche.borne_superieure)
        )
        for tranche in distribution.tranches
    )


def cout_garantie_par_sexe(femmes: DistributionPensions,
                           hommes: DistributionPensions,
                           part_femmes: float, effectif_total: float,
                           plancher_mensuel: float, facteur: float,
                           rapport: float) -> CoutGarantie:
    """Le barème appliqué aux deux sexes à part, chacun de son facteur.

    ``rapport`` vaut un pour la convention en vigueur, et le résultat redonne
    alors celui de :func:`cout_garantie` sur la colonne « ensemble » — à
    l'arrondi de publication près, la source arrondissant ses parts au
    centième de point. En deçà de un, les pensions des femmes tombent
    davantage, ce qui fait passer plus de monde sous le plancher : le coût de
    la convention uniforme est une borne basse, et c'est ce que cette
    fonction chiffre.
    """
    facteur_femmes, facteur_hommes = facteurs_par_sexe(
        pension_moyenne(femmes), pension_moyenne(hommes),
        part_femmes, facteur, rapport,
    )
    part = 0.0
    manque_mensuel = 0.0
    beneficiaires = 0.0
    for distribution, poids, facteur_sexe in (
        (femmes, part_femmes, facteur_femmes),
        (hommes, 1.0 - part_femmes, facteur_hommes),
    ):
        chiffre = cout_garantie(distribution, effectif_total * poids,
                                plancher_mensuel, facteur_sexe)
        part += poids * chiffre.part_beneficiaires
        beneficiaires += chiffre.beneficiaires
        manque_mensuel += poids * chiffre.complement_moyen_mensuel * chiffre.part_beneficiaires
    return CoutGarantie(
        plancher_mensuel=plancher_mensuel,
        # Le facteur rendu est celui de la contrainte, commun aux deux sexes
        # par construction : c'est lui qui a été tenu, pas ceux qu'il répartit.
        facteur=facteur,
        part_beneficiaires=part,
        beneficiaires=beneficiaires,
        complement_moyen_mensuel=manque_mensuel / part if part else 0.0,
        cout_annuel_meur=manque_mensuel * effectif_total * 12.0 / 1e6,
    )
