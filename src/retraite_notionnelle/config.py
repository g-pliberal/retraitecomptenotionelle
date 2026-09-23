"""Paramètres de configuration du modèle.

Toutes les décisions de modélisation contestables sont réunies ici, en un seul
endroit, pour qu'on puisse les faire varier sans toucher au moteur. Les valeurs
par défaut suivent le cahier des charges, à une exception près et une seule :
l'indexation, où le défaut est la règle d'ÉQUILIBRE et non la règle DEMANDÉE.
Un défaut est ce qu'on retient faute d'instruction contraire, pas ce qu'on
cherche à démontrer ; la règle demandée reste à un paramètre de distance.

* indexation par la croissance de la masse salariale — le taux d'équilibre de
  la répartition. Le « triple lock inversé » qui a donné son cahier des charges
  au modèle reste disponible, avec ses variantes (médiane, moyenne, tout en
  nominal), ainsi que la revalorisation réellement pratiquée par le régime
  général ;
* âge de référence à cliquet ;
* neutralisation intégrale des droits non contributifs ;
* fusion des régimes au cas le plus défavorable à compter de l'année de bascule.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path


RACINE_PROJET = Path(__file__).resolve().parents[2]
RACINE_DONNEES = RACINE_PROJET / "data"


#: Fenêtre de lissage de la règle italienne, en années. Ce n'est pas un défaut
#: du modèle : c'est la valeur qu'il faut donner à ``lissage_indexation``, avec
#: ``ModeIndexation.PIB_NOMINAL``, pour reproduire la règle italienne.
LISSAGE_ITALIEN = 5


class ModeIndexation(str, Enum):
    """Règle de revalorisation des comptes et des pensions."""

    #: min(inflation, croissance du salaire moyen nominal, productivité réelle).
    #: C'est la règle demandée, littéralement. Elle mêle un taux réel
    #: (productivité) à deux taux nominaux : en période de forte inflation, le
    #: minimum est presque toujours la productivité réelle, ce qui écrase la
    #: valeur réelle des comptes et des pensions. Effet voulu, mais massif :
    #: cf. docs/methodologie.md §3 et docs/limites.md §2.
    TRIPLE_LOCK_INVERSE = "triple_lock_inverse"

    #: Variante homogène : les trois termes sont ramenés en nominal
    #: (productivité réelle + inflation) avant de prendre le minimum.
    #: Fournie pour mesurer l'effet du mélange nominal/réel, pas par défaut.
    TRIPLE_LOCK_INVERSE_NOMINAL = "triple_lock_inverse_nominal"

    #: Médiane des trois mêmes termes, au lieu de leur minimum. Le terme retenu
    #: reste l'un des trois, mais celui du milieu : la règle cesse d'être
    #: gouvernée par la série la plus basse — en pratique la productivité réelle
    #: dès que l'inflation monte — sans pour autant retenir la plus haute.
    #: Variante moins sévère que la règle littérale, et défendable : c'est un
    #: choix robuste au sens statistique, insensible à une série aberrante.
    MEDIANE_TROIS_TAUX = "mediane_trois_taux"

    #: Moyenne arithmétique des trois mêmes termes. Elle donne un poids égal à
    #: chacun, y compris à la série la plus haute, et n'est donc plus une règle
    #: d'austérité. Deux réserves : la moyenne n'est pas un taux observé — aucun
    #: agrégat économique ne progresse à ce rythme —, et elle importe un tiers
    #: du mélange nominal/réel dans le résultat de CHAQUE année, là où le
    #: minimum et la médiane ne le font que les années où le terme réel gagne.
    #: Fournie parce qu'elle a été demandée, avec ce que ce fondement a de
    #: fragile.
    MOYENNE_TROIS_TAUX = "moyenne_trois_taux"

    #: Croissance de la MASSE SALARIALE — l'assiette des cotisations. C'est le
    #: taux de rendement interne d'un système en répartition (Samuelson 1958,
    #: Aaron 1966) : le seul qui laisse le système en équilibre sans toucher au
    #: taux de cotisation, et donc le taux d'indexation que la théorie des
    #: comptes notionnels désigne. Il vaut salaire moyen + emploi salarié, ce
    #: qui le rend NETTEMENT PLUS GÉNÉREUX que toutes les autres règles sur la
    #: période observée : l'emploi salarié a doublé depuis 1950. Ce n'est pas
    #: une règle d'austérité, c'est une règle d'équilibre.
    MASSE_SALARIALE = "masse_salariale"

    #: Croissance du PIB nominal. Assiette plus large que la masse salariale :
    #: elle capte le déplacement de la valeur ajoutée vers les revenus non
    #: salariaux, que la masse salariale, elle, subit. C'est l'assiette que
    #: retient l'Italie pour ses comptes notionnels — mais l'Italie la LISSE sur
    #: cinq ans, et le lissage n'est pas un mode : c'est le paramètre
    #: ``lissage_indexation``, qui s'applique à n'importe laquelle de ces
    #: règles. La règle italienne s'écrit donc
    #: ``--indexation pib_nominal --lissage 5``.
    PIB_NOMINAL = "pib_nominal"

    #: Revalorisation RÉELLEMENT PRATIQUÉE par le régime général : les
    #: coefficients des arrêtés annuels, tels que le scénario 1 les applique
    #: aux salaires portés au compte (les salaires jusqu'en 1986, les prix
    #: depuis, hors de la plage publiée). C'est le seul mode qui ne suppose
    #: rien : il demande ce qu'aurait donné le compte notionnel s'il avait
    #: rapporté exactement ce que le droit en vigueur a accordé. C'est donc
    #: LUI, et non ``PRIX``, qui neutralise l'indexation quand on veut isoler
    #: l'effet propre des comptes notionnels.
    REVALORISATION_PORTEE_AU_COMPTE = "revalorisation_portee_au_compte"

    #: Indexation sur les seuls prix (règle en vigueur depuis 1993). Ce n'est
    #: la règle du régime général que DEPUIS 1987 : avant, les arrêtés
    #: suivaient les salaires. Prendre cette ligne pour celle du droit positif
    #: sur toute la période est une erreur — voir le mode ci-dessus.
    PRIX = "prix"

    #: Indexation sur le salaire moyen (règle antérieure à 1987).
    SALAIRES = "salaires"


class SourceCotisations(str, Enum):
    """Origine du flux qui alimente le compte notionnel."""

    #: Taux de cotisation retraite effectivement en vigueur dans le régime
    #: d'affiliation, année par année (fidèle au principe « seules les
    #: cotisations comptent »).
    TAUX_HISTORIQUES = "taux_historiques"

    #: Taux unique appliqué à toute la carrière, quel que soit le régime : un
    #: TAUX D'ACQUISITION COMMUN, public et privé confondus. Ce qui a été
    #: prélevé au-delà — le surplus du compte d'affectation spéciale, le taux
    #: d'appel des complémentaires, la contribution d'équilibre d'un régime
    #: spécial — finance alors les engagements hérités du passé et n'ouvre aucun
    #: droit nouveau. Le taux est prélevé UNE FOIS sur la rémunération, et non
    #: une fois par régime : les régimes qui découpent la même tranche voient
    #: leurs assiettes réunies, pas additionnées. Les scénarios 2 à 5 ne
    #: l'emploient pas — il sert à isoler l'effet des règles de liquidation de
    #: celui des différences de taux entre régimes.
    TAUX_UNIFORME = "taux_uniforme"

    #: Les taux historiques JUSQU'À la bascule, le taux uniforme À COMPTER
    #: d'elle. C'est le flux du scénario 6 : ce qui a été cotisé sous le
    #: système actuel est porté au compte tel qu'il a été prélevé, comme dans
    #: le scénario 4, et c'est seulement à partir de la bascule que le taux
    #: unique de 18 % remplace ceux des régimes — voir
    #: ``Parametres.taux_cotisation_liberal``. Une personne née en 1975 cotise
    #: donc aux taux réels de 1996 à 2025, puis à 18 % de 2026 à son départ.
    TAUX_HISTORIQUES_PUIS_UNIFORME = "taux_historiques_puis_uniforme"


class ModeAgeReference(str, Enum):
    """Construction de l'âge auquel une liquidation est réputée « à l'heure »."""

    #: Cliquet sur l'âge du taux plein du régime général : l'âge de référence
    #: ne redescend jamais. Un départ à 60 ans en 1990 est donc traité comme
    #: une anticipation de 5 ans par rapport à l'âge de référence de 65 ans.
    CLIQUET_LEGAL = "cliquet_legal"

    #: Cliquet légal jusqu'à l'année de bascule, puis indexation sur
    #: l'espérance de vie de façon à stabiliser le ratio durée de
    #: retraite / durée de carrière.
    CLIQUET_PUIS_ESPERANCE_VIE = "cliquet_puis_esperance_vie"

    #: Âge du taux plein en vigueur l'année de liquidation, sans cliquet.
    #: Reproduit le droit positif ; sert de contrefactuel.
    LEGAL_SANS_CLIQUET = "legal_sans_cliquet"

    #: Cliquet légal jusqu'à l'année de bascule, puis un âge FIXE —
    #: ``Parametres.age_reference_fixe``, soit 64 ans, l'âge légal d'ouverture
    #: des droits que la loi du 14 avril 2023 atteint en 2030. C'est le défaut :
    #: le système proposé ne reconduit pas le taux plein à 67 ans, qui est une
    #: condition de durée d'assurance, notion qu'un compte notionnel n'a pas.
    #: Avant la bascule, le cliquet reste seul en vigueur : 64 ans n'existait
    #: dans aucun droit, et une liquidation de 1990 se mesure à son époque.
    FIXE_APRES_BASCULE = "fixe_apres_bascule"


class PartCotisation(str, Enum):
    """Quelle part de la cotisation retraite alimente le compte notionnel.

    Une cotisation retraite a deux parts : ce que l'assuré supporte et ce que
    son employeur verse. Les porter toutes deux au compte, ou n'y porter que la
    première, ne répond pas à la même question — et le modèle sait maintenant
    faire les deux **symétriquement**, public et privé.

    Il ne l'a pas toujours su. Les fiches de régime ne stockent pas la même
    grandeur selon le secteur : pour le privé, ``taux_cotisation_retraite`` est
    le total salarié + employeur ; pour la fonction publique et les régimes
    spéciaux, c'est la seule retenue de l'agent. Les comparer directement
    opposait un effort entier à un demi-effort, et faisait apparaître entre un
    fonctionnaire et un salarié de même rémunération un écart de 37 % qui ne
    traduisait rien de réel. Faute de mieux, le modèle prêtait alors au public
    la part employeur du privé.

    Deux séries l'en dispensent désormais : ``part_salariale`` dans les fiches,
    qui dit quelle fraction du taux l'assuré supporte, et
    ``legislation/contribution_employeur_public.csv``, qui porte ce que verse un
    employeur public. Les trois valeurs ci-dessous s'appuient sur elles.

    * ``SALARIALE`` (défaut, scénarios 2 et 3) — seule la part que l'assuré
      supporte lui-même alimente le compte. Pour un non-salarié, qui n'a pas
      d'employeur, c'est toute sa cotisation. Aucune convention, aucun emprunt :
      la comparaison public/privé porte sur la même grandeur des deux côtés.
    * ``TOTALE`` (scénarios 4 et 5) — salariale et patronale. La part patronale
      du privé est dans la fiche ; celle du public est celle qui a été
      réellement versée, décret par décret.
    * ``TOTALE_ALIGNEE`` — salariale et patronale, mais la part patronale du
      public est empruntée au statut pivot privé. C'est l'ancienne convention,
      conservée comme contrefactuel : elle répond à « à effort contributif égal,
      que donnerait la règle notionnelle ? », question légitime mais différente.

    Ce que ``TOTALE`` ne dit pas. Les taux employeur publics sont des taux
    d'ÉQUILIBRE, fixés pour que le compte tombe juste : 82,28 % en 2026 ne
    signifie pas qu'un fonctionnaire acquiert 82 % de son traitement en droits
    nouveaux, mais qu'il faut aujourd'hui cette contribution pour payer les
    pensions d'aujourd'hui.
    """

    SALARIALE = "salariale"
    TOTALE = "totale"
    TOTALE_ALIGNEE = "totale_alignee"


class AgeConversionDroitsAcquis(str, Enum):
    """Âge auquel les droits figés à la bascule sont convertis en capital.

    Le scénario prospectif transforme une pension déjà acquise en capital
    notionnel d'ouverture, en la multipliant par un diviseur. Reste à choisir
    l'âge auquel ce diviseur est pris — et le choix n'est pas neutre, puisque le
    capital sera ensuite redivisé par le diviseur de l'âge réel de liquidation.

    * ``REFERENCE`` valorise au diviseur de l'âge de référence. Un assuré qui
      liquide avant cet âge subit donc, sur ses droits déjà ouverts, un
      abattement égal au rapport des deux diviseurs — de l'ordre de 10 % pour
      trois ans d'écart. C'est la lecture stricte : dans un système notionnel,
      l'âge de départ se paie, y compris sur le passé.
    * ``LIQUIDATION`` valorise au diviseur de l'âge effectif de départ, pris à
      l'année de bascule. La conversion devient alors neutre : le passage aux
      comptes notionnels ne retire rien à des droits déjà ouverts, que le
      système actuel aurait servis sans décote. C'est la convention qu'une
      réforme réelle retiendrait, et le contrefactuel qui mesure ce que coûte
      l'autre.

    Dans les deux cas, l'écart de longévité entre l'année de bascule et l'année
    de liquidation subsiste : c'est un effet de table, pas une pénalité d'âge.
    """

    REFERENCE = "reference"
    LIQUIDATION = "liquidation"


class TableConversion(str, Enum):
    """Table de mortalité servant au coefficient de conversion."""

    #: Table unisexe (moyenne pondérée hommes/femmes). Choix par défaut :
    #: c'est la pratique des systèmes notionnels suédois et italien, et une
    #: table sexuée ferait mécaniquement baisser la pension des femmes de
    #: 8 à 12 % à capital notionnel identique.
    UNISEXE = "unisexe"

    #: Table par sexe. Actuariellement exacte, juridiquement inapplicable en
    #: France (principe de non-discrimination). Fournie pour mesurer l'écart.
    PAR_SEXE = "par_sexe"


class RevalorisationStock(str, Enum):
    """Ce que deviennent, à la bascule, les pensions DÉJÀ SERVIES.

    ``PRIX`` : elles gardent la revalorisation que le droit leur a promise,
    l'indice des prix (L. 161-23-1), jusqu'à leur extinction ; seuls les comptes
    ouverts sous le nouveau régime suivent sa règle. ``REINDEXE`` : la réforme
    fait passer tout le stock à la règle du compte le jour de la bascule, ce
    que faisait le modèle jusqu'au 20 septembre 2026. Ne joue que sur la page
    Coût et sur la pension d'aujourd'hui d'un retraité, et que pour les
    systèmes 2 à 6 : le système 1 est le droit.
    """

    PRIX = "prix"
    REINDEXE = "reindexe"


#: La valeur de ``population_conversion`` qui rattache chaque carrière au
#: vingtile de niveau de vie où son salaire la place : le diviseur suit alors
#: la mortalité de ce vingtile (tables de l'INSEE), et non celle de la
#: population générale.
POPULATION_PAR_NIVEAU_DE_VIE = "niveau_de_vie"

#: Comment une carrière est rattachée à son vingtile de niveau de vie.
RATTACHEMENT_SALAIRE = "salaire"
RATTACHEMENT_PENSION = "pension"
RATTACHEMENTS_NIVEAU_DE_VIE = (RATTACHEMENT_SALAIRE, RATTACHEMENT_PENSION)


class SituationFoyer(str, Enum):
    """Situation de foyer retenue pour la garantie vieillesse du scénario 6.

    La garantie est INDIVIDUALISÉE : chaque personne est comparée à son propre
    plancher, et les revenus du conjoint n'entrent jamais dans le calcul. La
    situation ne change donc qu'une chose — l'allocation d'isolement, qui
    s'ajoute au plancher d'une personne vivant seule. À deux, chacun a la
    sienne, sans que l'une regarde la pension de l'autre.
    """

    SEUL = "seul"
    COUPLE = "couple"


@dataclass(frozen=True)
class Neutralisations:
    """Droits retirés du calcul, conformément au principe « seules les
    cotisations comptent ».

    **Ceci est une DÉCLARATION, pas une commande.** Aucun de ces drapeaux n'est
    lu par le moteur, et il ne peut pas l'être : dans un compte notionnel, la
    suppression de ces droits n'est pas une option qu'on active, elle est la
    conséquence mécanique de la règle d'accumulation — une année sans
    cotisation n'ajoute rien au compte, un trimestre gratuit n'est pas une
    cotisation, un minimum n'est pas un capital. Remettre l'un d'eux
    supposerait de sortir du modèle. La classe existe pour DIRE, en un seul
    endroit et de façon vérifiable, ce que les scénarios notionnels retirent au
    droit en vigueur ; ``retraite-notionnelle`` l'affiche, la documentation la
    reprend, et un test vérifie que le scénario « système actuel », lui, sert
    bien chacune des lignes qu'il est censé servir.

    Le mettre à faux ne change donc aucun résultat, et le docstring ci-dessous
    ne promet plus le contraire.

    **Ce que le scénario 1 sert vraiment**, et il ne l'a pas toujours fait :
    minimum contributif, minimum garanti, minimum vieillesse, majoration pour
    enfants, majoration de durée d'assurance et bonification pour enfants de la
    fonction publique, AVPF, périodes assimilées, garantie minimale de points,
    carrière longue, décote et surcote.

    **La catégorie active est désormais servie**, et les âges de la pension
    militaire avec elle : le classement de l'emploi ne se devine pas d'un revenu
    et d'un régime, mais il se DÉCLARE, et sept statuts de
    ``legislation/affiliations.yaml`` le portent — catégorie active et
    super-active des trois fonctions publiques, ouvriers de l'État, militaires
    officiers et non officiers. Le scénario 1 leur oppose l'âge anticipé ou
    minoré de l'article L. 24, l'âge d'annulation de décote de l'article
    L. 14 bis et, pour les militaires, la durée de services qui ouvre leur
    pension. La ligne ``categorie_active`` ci-dessous dit donc, comme les
    autres, ce que les scénarios notionnels retirent à un droit que l'étalon,
    lui, sert.

    **Ce qu'il ne sert pas**, et qu'il ne peut donc pas retirer : la réversion,
    qui concerne le conjoint survivant et non l'assuré ; les bonifications de
    SERVICE — dépaysement, campagne militaire, cinquième —, qui supposent de
    connaître le corps d'appartenance et le détail des services, la bonification
    pour ENFANTS étant, elle, servie depuis qu'elle est datée ; la limite d'âge
    de grade, qui ouvre la pension militaire quelle que soit la durée
    accomplie ; la pension majorée de référence du régime agricole ; les
    coefficients de solidarité et majorants de l'Agirc-Arrco, dispositif éteint
    dont l'effet temporaire serait représenté faussement par un modèle qui ne
    calcule qu'une pension annuelle unique. Voir ``docs/limites.md``.
    """

    minimum_contributif: bool = True
    minimum_garanti: bool = True
    minimum_vieillesse_aspa: bool = True
    pension_majoree_reference: bool = True
    majoration_enfants: bool = True
    majoration_duree_assurance: bool = True
    assurance_vieillesse_parents_au_foyer: bool = True
    reversion: bool = True
    bonifications: bool = True
    categorie_active: bool = True
    periodes_assimilees: bool = True
    garantie_minimale_points: bool = True
    carriere_longue: bool = True
    decote_surcote: bool = True
    coefficient_solidarite: bool = True

    def actives(self) -> list[str]:
        return [nom for nom, valeur in self.__dict__.items() if valeur]


#: Le frais sur arrérages du PER TEL QU'IL EST VENDU en 2025 : la moyenne
#: publiée par l'OPEF, qui ne porte que sur les neuf assureurs sur vingt qui
#: facturent. Le calcul retient la moyenne sur les vingt (0,99 %) ; celle-ci
#: ne sert qu'au régime de frais ``detail``, qui redit l'ancien réglage. Un
#: test la tient égale à la valeur publiée du fichier de frais.
FRAIS_ARRERAGES_VENDU = 0.0220

#: Les régimes de frais que le site propose, dans l'ordre du menu. Le premier
#: est le défaut ; ``Parametres.sous_regime_frais`` dit ce que chacun fait.
REGIMES_FRAIS: tuple[str, ...] = ("paliers", "plafond", "contrats", "figes", "detail", "aucun")

#: La prime de terme à trente ans sous les deux régimes qui la retirent : le
#: milieu et le haut de la fourchette que la littérature retient pour les
#: maturités longues quand la courbe est ascendante (0,3 à 1 point), et que
#: ``docs/limites.md`` porte en réserve n° 1 du pilier capitalisé.
PRIME_TERME_MILIEU = 0.005
PRIME_TERME_HAUTE = 0.010

#: Les régimes de taux que le site propose, dans l'ordre du menu. Le premier
#: est le défaut ; ``Parametres.sous_regime_taux`` dit ce que chacun fait.
REGIMES_TAUX: tuple[str, ...] = ("forwards", "prime", "prime_haute")


def taux_au(niveau: float, paliers: tuple[tuple[int, float], ...], annee: int) -> float:
    """Le taux en vigueur en ``annee`` : ``niveau`` avant le premier palier,
    puis le taux du dernier palier atteint. Les paliers sont lus dans l'ordre
    des années, quel que soit celui du tuple."""
    taux = niveau
    for debut, valeur in sorted(paliers):
        if annee >= debut:
            taux = valeur
    return taux


@dataclass(frozen=True)
class Parametres:
    """Jeu complet de paramètres d'une simulation."""

    # --- Bornes temporelles -------------------------------------------------
    #: Année d'origine du système par répartition. 1941 = allocation aux vieux
    #: travailleurs salariés, premier mécanisme financé par les cotisations des
    #: actifs. Mettre 1945 pour partir des ordonnances créant la Sécurité sociale.
    annee_debut_repartition: int = 1941

    #: Année de bascule : la première du régime fusionné. Les droits acquis
    #: jusqu'à l'année qui la PRÉCÈDE sont calculés selon les règles actuelles,
    #: ceux de l'année de bascule et des suivantes selon le compte notionnel —
    #: le compte y bascule dès le 1er janvier (``annee >= annee_bascule``).
    #: C'est aussi la première année de cotisation au pilier capitalisé de la
    #: proposition, pour qu'elle change tout le même jour. Un paramètre à part,
    #: ``annee_debut_capitalisation``, a tenu cette date jusqu'au 23 septembre
    #: 2026 : figé à 2026, il ouvrait le pilier en 2026 quelle que fût la
    #: bascule choisie, et sur la somme des assiettes des régimes d'avant elle.
    annee_bascule: int = 2026

    #: Dernière année disponible dans les séries macroéconomiques.
    annee_courante: int = 2026

    #: Année dans les euros de laquelle les résultats sont exprimés. Sans cette
    #: conversion, comparer une pension liquidée en 1975 à une pension de 2064
    #: n'a aucun sens : l'écart de niveau des prix dépasse largement l'effet de
    #: la réforme simulée.
    annee_euros_constants: int = 2026

    #: Scénario de projection macroéconomique au-delà de la dernière observation
    #: (clé de ``data/reference/macro/hypotheses_projection.yaml``).
    scenario_projection: str = "cor_reference"

    #: Trajectoire de l'emploi au-delà de la dernière observation (clé de
    #: ``trajectoires_emploi`` dans le même fichier). Elle ne touche que la
    #: MASSE SALARIALE et le PIB projetés — salaire moyen composé avec
    #: l'emploi — donc l'indexation des comptes notionnels, que seuls les
    #: systèmes 2 à 6 lisent : le système 1 ne lit ni l'une ni l'autre. Le
    #: défaut est le scénario de référence du COR de juin 2026 ; ``constant``
    #: retrouve la convention d'avant le 20 septembre 2026.
    trajectoire_emploi: str = "cor_2026"

    #: Les pensions déjà servies à la bascule : sur les prix, comme le droit le
    #: leur promet, ou réindexées sur la règle du compte. Le défaut retire aux
    #: retraités de la bascule un demi-point par an qu'ils n'ont pas cotisé, et
    #: efface la bosse que la page Coût montrait de 2026 à 2040 ; il ne change
    #: rien à l'horizon, le stock étant éteint. Voir ``RevalorisationStock``.
    revalorisation_stock: RevalorisationStock = RevalorisationStock.PRIX

    # --- Indexation ---------------------------------------------------------
    #: Le défaut est la règle d'ÉQUILIBRE — la croissance de l'assiette des
    #: cotisations —, et non le triple lock inversé qui a donné son cahier des
    #: charges au modèle. Raison : le triple lock inversé est une règle
    #: proposée, la masse salariale est celle que la théorie de la répartition
    #: désigne, et un défaut doit être ce qu'on retient faute d'instruction
    #: contraire, pas ce qu'on veut démontrer. La règle demandée reste à un
    #: paramètre de distance : ``--indexation triple_lock_inverse``.
    mode_indexation: ModeIndexation = ModeIndexation.MASSE_SALARIALE

    #: Nombre d'années de la moyenne glissante appliquée au taux d'indexation.
    #: 1 = aucun lissage, le taux de l'année est appliqué tel quel.
    #:
    #: Le lissage est ORTHOGONAL à la règle : il s'applique au taux que la règle
    #: produit, quelle que soit la règle. Ce qu'il vise n'est pas le niveau mais
    #: la LOTERIE DE COHORTE — deux carrières identiques à un an d'écart ne
    #: doivent pas diverger parce qu'une année d'inflation, ou un trou comme
    #: 2020, est tombé d'un côté ou de l'autre de la liquidation. C'est le
    #: mécanisme de la règle italienne (cinq ans sur le PIB nominal), et rien
    #: n'oblige à le réserver à elle.
    #:
    #: Une réserve, écrite dans docs/methodologie.md : sur un cumul de plusieurs
    #: décennies, une moyenne glissante n'est pas neutre. Elle revient à mesurer
    #: la croissance depuis une base reculée d'environ la moitié de la fenêtre,
    #: ce qui gonfle le coefficient cumulé. Sur une carrière l'effet est faible ;
    #: sur les tableaux 1941-2025, il vaut une vingtaine de pour cent à cinq ans.
    lissage_indexation: int = 1

    #: Plancher éventuel appliqué au taux d'indexation. ``None`` = aucun
    #: plancher : le triple lock inversé peut être négatif, ce qui est sa
    #: conséquence logique et non un défaut.
    plancher_indexation: float | None = None

    # NOTE : il n'y a pas de paramètre « indexer les pensions liquidées ». Le
    # moteur ne calcule qu'une pension AU MOMENT DE LA LIQUIDATION, dans les
    # euros de cette année-là, pour les six scénarios ; il n'existe aucune
    # phase postérieure à revaloriser. Le drapeau qui figurait ici ne servait à
    # rien et laissait croire le contraire. Ce que la règle d'indexation fait
    # aux pensions déjà liquidées reste hors du modèle, et `docs/limites.md` le
    # dit maintenant.

    # --- Cotisations --------------------------------------------------------
    source_cotisations: SourceCotisations = SourceCotisations.TAUX_HISTORIQUES

    #: Taux utilisé si ``source_cotisations == TAUX_UNIFORME``. 25,31 % est
    #: l'effort contributif retraite total — salarié et employeur — d'un salarié
    #: du privé non cadre sous le plafond en 2025 : le taux que le privé
    #: supporte déjà. Aucun des scénarios 2 à 5 ne l'emploie ; c'est un
    #: contrefactuel, à activer explicitement. Le scénario 6 emploie, lui,
    #: ``taux_cotisation_liberal`` — à compter de la bascule seulement.
    taux_cotisation_uniforme: float = 0.2531

    # NOTE : il n'y a pas non plus de paramètre « le taux d'appel ouvre-t-il des
    # droits ». Le compte notionnel porte ce qui a été PRÉLEVÉ, taux d'appel
    # compris — c'est la lecture directe de « seules les cotisations comptent »,
    # et c'est la seule que le moteur sache faire. Le drapeau qui figurait ici
    # n'était lu nulle part : le mettre à faux ne changeait rien.

    #: Part de la cotisation portée au compte : celle de l'assuré seul, ou
    #: celle de l'assuré et de son employeur. Voir :class:`PartCotisation`.
    #: Le défaut est celui des scénarios 2 et 3 ; les scénarios 4 et 5 le font
    #: varier, et rien d'autre.
    part_cotisation: PartCotisation = PartCotisation.SALARIALE

    #: Statut dont les taux servent de référence quand la part employeur du
    #: public est empruntée au privé (``TOTALE_ALIGNEE``), ou quand aucune série
    #: employeur n'est publiée pour le régime (``TOTALE``).
    statut_pivot_cotisations: str = "salarie_prive_non_cadre"

    #: Plafonnement de l'assiette notionnelle, en multiples du plafond annuel de
    #: la Sécurité sociale. ``None`` = assiette déplafonnée, et c'est le défaut.
    #:
    #: Il a valu 8,0 — le plafond de la tranche B puis C de l'Agirc, que les
    #: fiches portent —, sans qu'aucune décision l'ait posé. Ce plafond-là ne
    #: mordait qu'APRÈS LA BASCULE : avant elle, les fiches portent leurs
    #: propres bornes et ce sont elles qui rognent, ce qui est le droit. Après,
    #: le régime fusionné est déclaré ``assiette: deplafonnee`` — « la plus
    #: large : tout revenu cotise » —, et le paramètre le démentait au-delà de
    #: 8 plafonds, soit 9,2 fois le salaire moyen, 32 040 € par mois en 2026.
    #: Le site, lui, promet en deuxième geste du calcul « au premier euro, sans
    #: plafond » : c'était faux pour les plus hauts revenus du formulaire, qui
    #: perdaient 12 à 14 % de pension, et le catalogue des affirmations le
    #: disait — entrée ``accueil.on_inscrit``, action 61 de la feuille de route.
    #:
    #: Le lever ne déplace AUCUN agrégat : la grille des cas types plafonne à
    #: 2,5 fois le salaire moyen, si bien que ni le coût, ni le solde, ni les
    #: coefficients d'équilibre ne changent d'un centime. Ce que cela déplace
    #: tient dans le simulateur, au-delà de 9,2 fois le salaire moyen.
    plafond_assiette_en_pass: float | None = None

    # --- Âge de référence ---------------------------------------------------
    mode_age_reference: ModeAgeReference = ModeAgeReference.FIXE_APRES_BASCULE

    #: Âge de référence servi à partir de la bascule en mode
    #: FIXE_APRES_BASCULE. 64 ans : l'âge légal d'ouverture des droits.
    age_reference_fixe: float = 64.0

    #: Ratio cible durée de retraite / durée de carrière, utilisé seulement en
    #: mode CLIQUET_PUIS_ESPERANCE_VIE.
    ratio_cible_retraite_carriere: float = 0.50

    # --- Conversion en rente ------------------------------------------------
    table_conversion: TableConversion = TableConversion.UNISEXE

    #: Population dont la mortalité entre dans le diviseur, à la place de
    #: celle de la population générale. C'EST L'INTERRUPTEUR, et il n'y en a
    #: qu'un :
    #:
    #: - ``POPULATION_PAR_NIVEAU_DE_VIE`` (le défaut depuis le 21 septembre
    #:   2026) : chaque carrière est rattachée au vingtile de niveau de vie où
    #:   son salaire la place, et son diviseur suit la mortalité de ce
    #:   vingtile, lue chez l'INSEE. Le stock est compris : les scénarios
    #:   rétroactifs recalculent tout le monde ainsi.
    #: - ``None`` : la table COMMUNE, la même pour tout le monde. C'est ce
    #:   qu'il faut poser pour désactiver la mesure, et ce que les scripts de
    #:   mesure posent pour la chiffrer.
    #: - une clé de ``esperances_vie_populations.csv`` ou un vingtile nommé
    #:   (``fonctionnaires_civils_etat``, ``niveau_de_vie_v01``…) : la même
    #:   population pour toutes les carrières, pour mesurer.
    #:
    #: Ce que la mesure vaut et ce qu'elle suppose est dans
    #: ``docs/methodologie.md`` §5 et ``docs/limites.md`` §5 (action 14).
    population_conversion: str | None = POPULATION_PAR_NIVEAU_DE_VIE

    #: Par quoi la carrière est rattachée à son vingtile, quand
    #: ``population_conversion`` vaut ``POPULATION_PAR_NIVEAU_DE_VIE`` :
    #: ``salaire`` — son salaire rapporté au salaire moyen, appliqué au niveau
    #: de vie moyen des vingtiles ; ``pension`` — le RANG de sa pension brute
    #: parmi les retraités, dans la distribution des pensions de la DREES,
    #: le vingtile étant celui de ce rang. Le second est circulaire sous un
    #: compte notionnel — la pension dépend du diviseur — et se résout par
    #: point fixe (``Convertisseur.resoudre``).
    rattachement_niveau_de_vie: str = RATTACHEMENT_SALAIRE

    #: Taux de préfinancement (« front-loading ») incorporé au diviseur.
    #: 0 signifie : le diviseur est l'espérance de vie résiduelle actualisée au
    #: même taux que l'indexation, les deux se compensant exactement. C'est le
    #: choix par défaut, le plus lisible.
    taux_anticipe_conversion: float = 0.0

    #: Âge auquel les droits figés à la bascule sont convertis en capital
    #: d'ouverture, dans le scénario prospectif. ``REFERENCE`` applique aux
    #: droits déjà acquis la sanction du départ anticipé ; ``LIQUIDATION`` rend
    #: la conversion neutre. Voir :class:`AgeConversionDroitsAcquis`.
    age_conversion_droits_acquis: AgeConversionDroitsAcquis = (
        AgeConversionDroitsAcquis.REFERENCE
    )

    #: Table de génération (mortalité prospective) plutôt que table du moment.
    #: Une table du moment sous-estime la longévité des générations récentes et
    #: surestime donc leur pension.
    table_generation: bool = True

    # NOTE : l'âge terminal des tables de mortalité n'est pas un paramètre de
    # simulation mais une constante du module qui les construit —
    # ``donnees.mortalite.AGE_TERMINAL``. Le champ qui figurait ici la doublait
    # sans jamais l'atteindre.

    # --- Fusion des régimes -------------------------------------------------
    #: À compter de ``annee_bascule``, tous les régimes sont remplacés par un
    #: régime unique dont les paramètres sont les plus défavorables de
    #: l'ensemble des régimes existants.
    fusion_au_plus_defavorable: bool = True

    # --- Scénario « système actuel » ----------------------------------------
    #: Le minimum vieillesse (ASPA) fait-il partie de l'étalon ?
    #:
    #: C'est une décision de modélisation, pas un détail technique. L'ASPA est
    #: le dernier plancher du système actuel et le seul qui ne suppose aucune
    #: cotisation : l'omettre sous-estime le système en vigueur là même où
    #: l'écart avec un compte notionnel est le plus grand. Mais ce n'est pas une
    #: pension — elle est soumise à condition d'âge (65 ans), de ressources DU
    #: FOYER, et de demande, avec un non-recours que la DREES estime à la
    #: moitié des ayants droit ; elle est en outre récupérable sur les
    #: successions.
    #:
    #: Elle est donc servie par défaut, sous le barème d'une personne seule
    #: sans autre ressource — le cas le plus favorable —, et toujours comme une
    #: LIGNE SÉPARÉE de la cascade, de sorte qu'on puisse la retrancher d'un
    #: coup d'œil. Mettre ce paramètre à ``False`` la retire du calcul.
    minimum_vieillesse_dans_le_scenario_actuel: bool = True

    # --- Scénario 6 : la proposition libérale --------------------------------
    #: Le scénario 6 est le scénario 4 — compte rétroactif, cotisation salariale
    #: et patronale confondues, mêmes âges, même indexation, même liquidation —
    #: à deux différences près, qui sont les deux termes de la proposition du
    #: Parti libéral français.
    #:
    #: La première : un TAUX UNIQUE À COMPTER DE LA BASCULE, le même pour tous
    #: les statuts, parts salariale et patronale additionnées, prélevé une
    #: fois sur la rémunération. Avant la bascule, le compte est celui du
    #: scénario 4 : ce qui a été cotisé sous le système actuel y est porté tel
    #: qu'il a été prélevé, aux taux réels de chaque régime — une personne née
    #: en 1975 cotise aux taux réels de 1996 à 2025, puis à 18 % de 2026 à son
    #: départ. Qui a liquidé avant la bascule retrouve donc, sur ce point, le
    #: scénario 4. Voir ``SourceCotisations.TAUX_HISTORIQUES_PUIS_UNIFORME``.
    taux_cotisation_liberal: float = 0.18

    #: Partage du taux unique entre l'assuré et son employeur. La proposition
    #: dit « 18 %, salariale et patronale additionnées » et ne dit pas qui
    #: porte quoi ; **le programme a tranché le 20 septembre 2026 : la part
    #: PATRONALE ne bouge pas, et toute la baisse va au salarié.**
    #:
    #: Un salarié du privé verse aujourd'hui 11,31 points sur sa fiche et son
    #: employeur 16,67, contributions d'équilibre comprises, soit 27,98 en
    #: tout. La proposition en prélève 23 : l'employeur garde ses 16,67, et la
    #: part salariale tombe à 6,33 — d'où ``0,0633 / 0,23``, écrit ainsi pour
    #: qu'on lise d'où il vient. Les 18 % et les 5 % capitalisés suivent la
    #: même clé : 4,95 + 1,38 pour l'assuré, 13,05 + 3,62 pour l'employeur.
    #:
    #: **Pourquoi celui-là**, et ``scripts/partage_taux_unique.py`` le mesure
    #: (action 56 de la feuille de route) : c'est le seul partage dont la
    #: baisse arrive en entier le lendemain de la réforme, sans hypothèse
    #: d'incidence, et le seul qui rende quelque chose au voisinage du SMIC.
    #: Une baisse de la part patronale, elle, profite d'abord à l'employeur,
    #: puis remonte dans le brut sur plusieurs années — et en remontant, elle
    #: grossit l'assiette de la CSG et des autres branches, qui en reprennent
    #: le quart. Le coût du travail, lui, ne bouge pas : c'est ce que le
    #: partage retenu garantit à tous les niveaux de salaire sauf au SMIC, où
    #: la part patronale du pilier capitalisé, hors du périmètre de la
    #: réduction générale, le fait monter de 66 € par mois.
    #:
    #: Ce paramètre ne touche à AUCUNE pension : le compte notionnel porte la
    #: somme des deux parts, et le partage lui est indifférent. Il ne sert qu'à
    #: la fiche de paie de `remuneration.py` — mais il y compte, et beaucoup :
    #: la CSG est assise sur le BRUT, que le partage déplace, et la réduction
    #: générale n'efface que des cotisations PATRONALES. Plus la part patronale
    #: est grosse, plus le salaire net est élevé à coût du travail donné, et
    #: plus il faut attendre pour le toucher. Voir le docstring de
    #: `remuneration.py`.
    #:
    #: Le dépôt a partagé MOITIÉ-MOITIÉ jusqu'au 20 septembre 2026, faute
    #: d'avoir mesuré : ce partage faisait MONTER la part salariale, de 11,31
    #: à 11,50 points, et la fiche de paie du lendemain baissait.
    part_salariale_taux_unique: float = 0.0633 / 0.23

    #: Ce que la proposition REND aux salaires sur ce qu'elle cesse d'affecter
    #: à la retraite. Décision du Parti libéral, 20 septembre 2026.
    #:
    #: La proposition ne reconduit pas les impôts et taxes affectés — 63,9 Md€
    #: en 2025 — ni la contribution d'équilibre de l'État — 82,28 % du
    #: traitement d'un fonctionnaire d'État en 2026. `cout.py` dit pourquoi :
    #: un compte notionnel ne crédite que ce qui est assis sur un revenu
    #: d'activité. Le dépôt s'arrêtait là, et ne disait pas ce que devenait
    #: cette recette — ce qui revenait à la laisser au budget, c'est-à-dire à
    #: la consacrer TOUT ENTIÈRE au déficit.
    #:
    #: Ce paramètre est la réponse, et c'est un PARTAGE :
    #:
    #:     la moitié est rendue aux salaires, la moitié éteint de la dette.
    #:
    #: Il s'applique en deux endroits, et la même moitié vaut pour les deux :
    #:
    #: 1. Les impôts affectés. Ce qui est assis sur une rémunération — la taxe
    #:    sur les salaires et le forfait social, 28 % du poste — est SUPPRIMÉ ;
    #:    le solde de la moitié rendue revient par une baisse de la CSG sur les
    #:    revenus d'activité, un peu plus d'un point. Voir `restitution.py`, et
    #:    surtout ce qu'il dit de cette CSG : elle ne finance aujourd'hui
    #:    AUCUNE retraite.
    #: 2. La contribution d'équilibre de l'employeur public. La moitié de ce
    #:    qu'il cesse de verser remonte dans le traitement, l'autre moitié paie
    #:    la dette de pensions qu'elle finançait. C'est `Incidence.PARTAGEE`,
    #:    et le docstring de `remuneration.py` dit pourquoi ce n'est ni
    #:    l'incidence intégrale ni l'assiette fixe.
    #:
    #: Zéro rend l'ancienne convention, où rien n'était rendu : un test le
    #: vérifie. Un donne la baisse d'impôt intégrale.
    part_rendue_aux_salaires: float = 0.5

    #: La seconde : une GARANTIE VIEILLESSE, allocation différentielle qui
    #: remplace l'ASPA et en garde l'âge (65 ans) et le principe — porter les
    #: ressources à un plancher —, mais individualise le plancher. Chacun est
    #: comparé au sien, sans regarder la pension du conjoint : 300 € et 1 500 €
    #: dans un couple ouvrent 500 € au premier et rien au second, là où l'ASPA
    #: actuelle, qui regarde le foyer, ne sert rien. Financée par l'impôt, non
    #: par les cotisations : la page Coût la sort du compte des cotisants.
    #:
    #: Montants MENSUELS, en euros de ``annee_euros_garantie_vieillesse``,
    #: ramenés à l'année de liquidation par l'indice des prix.
    garantie_vieillesse_mensuelle: float = 800.0

    #: Allocation d'isolement : s'ajoute au plancher d'une personne vivant
    #: seule. 800 + 250 = 1 050 € par mois seul, 800 € par personne à deux.
    allocation_isolement_mensuelle: float = 250.0

    #: Année dans les euros de laquelle les deux montants ci-dessus sont fixés.
    annee_euros_garantie_vieillesse: int = 2026

    #: Part des ayants droit qui RÉCLAMENT la garantie. Le programme retient,
    #: depuis le 20 septembre 2026, l'hypothèse que la DREES mesure sur l'ASPA :
    #: une personne seule éligible sur deux ne la demande pas (dossier n° 97,
    #: mai 2022, sur 2016), la crainte de la reprise sur succession étant le
    #: premier motif donné à la Cnav. La garantie étant une avance reprise dès
    #: le premier euro, elle ne se réclamera pas davantage. Ne joue que sur le
    #: COÛT lu sur la distribution (page Coût) : qui réclame la reçoit en
    #: entier, et le simulateur d'une carrière ne connaît pas ce taux. Un rend
    #: le recours complet.
    taux_recours_garantie: float = 0.5

    #: RAPPORT DES DEUX FACTEURS DE DÉPLACEMENT, ``r = f_F / f_H``. La garantie
    #: est chiffrée en déplaçant la distribution des pensions vers celles du
    #: scénario 6 ; le scénario ne déplace pourtant pas toutes les carrières du
    #: même rapport, puisqu'il retire les droits NON COTISÉS et que les femmes
    #: en détiennent plus souvent.
    #:
    #: ``None`` — le défaut depuis le 21 septembre 2026 — fait LIRE ce rapport
    #: sur l'enquête, où il vaut 0,834 en 2020 : la part cotisée de la carrière
    #: est de 74,0 % chez les femmes contre 89,1 % chez les hommes, et la
    #: majoration pour enfants, proportionnelle à la pension, corrige de moins
    #: d'un demi-point dans l'autre sens. Voir
    #: ``donnees.caracteristiques.CaracteristiquesRetraites.rapport_deplacement``.
    #:
    #: ``1.0`` restitue l'ANCIENNE convention — un facteur unique pour tous —,
    #: gardée pour mesurer ce qu'elle valait : elle sous-estimait le coût de la
    #: garantie d'environ 5 %. Un nombre quelconque remplace la mesure.
    rapport_deplacement_sexe: float | None = None

    #: Part de l'avance d'un bénéficiaire que sa SUCCESSION couvre. La garantie
    #: est une avance reprise sur la succession dès le premier euro, avec
    #: intérêts ; ce que les successions en rendent dépend du patrimoine des
    #: bénéficiaires. ``None``, le défaut, la fait CALCULER sur le patrimoine
    #: des ménages retraités selon leur revenu (COR, enquête Patrimoine 2018,
    #: ``donnees/patrimoine.py``) : les plus petites pensions au quart le plus
    #: modeste, les autres à l'ensemble des retraités — voir
    #: ``cout._reprises_successions``. Une part entre zéro et un remplace ce
    #: calcul : zéro éteint la reprise, un suppose que toute avance est
    #: remboursée. Ne joue que sur la page Coût, à partir de la bascule.
    part_reprise_garantie: float | None = None

    # --- Les trois règles de la reprise (action 47) --------------------------
    #: Elles ne jouent que sur la couverture CALCULÉE (``part_reprise_garantie``
    #: à ``None``) ; voir ``cout._recouvrement``, qui dit comment chacune entre
    #: dans le calcul, et ``docs/limites.md``. Chacune se coupe, pour mesurer ce
    #: qu'elle déplace ; les trois coupées, et l'assurance-vie ramenée à zéro,
    #: rendent la couverture d'avant le 22 septembre 2026.
    #:
    #: 1. LE LOGEMENT ATTEND LE DÉCÈS DU CONJOINT SURVIVANT QUI L'OCCUPE, les
    #: intérêts courant entre-temps. Au premier décès d'un couple, la créance
    #: n'est prise que sur ce qui n'est pas le logement ; le reste attend le
    #: survivant, capitalisé au taux réel, et n'est pris que sur le logement.
    reprise_report_logement: bool = True
    #: La part du patrimoine d'un ménage PROPRIÉTAIRE que son logement
    #: représente. Hypothèse : le COR (document n° 3 du 16 décembre 2021)
    #: donne 63,5 % d'immobilier dans le patrimoine brut des ménages
    #: retraités, tous biens et tous ménages confondus, locataires compris.
    part_logement_proprietaires: float = 0.75
    #: Le patrimoine à partir duquel un ménage est tenu pour propriétaire de
    #: son logement, en euros de l'enquête (2018). Hypothèse : sur l'ensemble
    #: des ménages retraités, il laisse 30 % de locataires, et le COR en
    #: compte 30,5 % (69,5 % de propriétaires).
    patrimoine_minimal_proprietaire: float = 80_000.0
    #: L'écart d'âge entre conjoints, le mari étant le plus âgé : 2,6 ans
    #: (INSEE, 2017). Il dit à quel âge le survivant entre en veuvage, et donc
    #: combien de temps la reprise du logement attend.
    ecart_age_couple: float = 2.6
    #:
    #: 2. LES DONATIONS FAITES DEPUIS L'OUVERTURE, OU DANS LES DIX ANS QUI L'ONT
    #: PRÉCÉDÉE, SONT RÉINTÉGRÉES : la créance se poursuit contre le donataire,
    #: à hauteur de ce qu'il a reçu. Le patrimoine de l'enquête est celui qui
    #: RESTE après les donations déjà faites ; la règle lui rend, chez les
    #: ménages donateurs, la part des donations qu'elle atteint.
    reprise_donations: bool = True
    #: La part des ménages retraités qui ont déjà fait une donation : 7,0 %
    #: parmi les 40 % les moins dotés, 15,8 % sur l'ensemble (COR, document
    #: n° 7 du 16 décembre 2021, tableau 1, enquête Patrimoine 2018 ;
    #: l'ensemble est la moyenne des cinq colonnes pesée par leur largeur).
    part_donateurs_modestes: float = 0.07
    part_donateurs_retraites: float = 0.158
    #: Ce qu'un ménage donateur a donné, en euros de l'enquête (2018).
    #: Hypothèses : le COR ne publie pas de montant, seulement que la moitié
    #: des donations des 70-79 ans dépasse 100 000 € (graphique 5).
    donation_moyenne_modestes: float = 60_000.0
    donation_moyenne_retraites: float = 100_000.0
    #: La part de ces donations que la règle atteint : celles qui tombent dans
    #: la fenêtre (dix ans avant l'ouverture, et après), et que l'administration
    #: connaît — un don manuel non déclaré lui échappe. Hypothèses.
    part_donations_fenetre: float = 0.85
    part_donations_connues: float = 0.8
    #:
    #: 3. L'ASSURANCE-VIE EST HORS SUCCESSION (L. 132-12 du code des
    #: assurances), mais le patrimoine de l'enquête la compte. La règle en
    #: reprend les primes versées dans la même fenêtre que les donations —
    #: depuis l'ouverture, ou dans les dix ans qui l'ont précédée —, contre
    #: leur bénéficiaire ; le reste, primes antérieures et intérêts, échappe.
    #: Sans la règle, tout échappe. ``L. 132-8`` CASF, pour l'aide sociale, ne
    #: reprend que les primes versées après 70 ans.
    reprise_assurance_vie: bool = True
    #: La part de l'assurance-vie et de l'épargne retraite dans le patrimoine
    #: des ménages : 10 % pour les 50 % les moins dotés (Banque de France,
    #: comptes distributionnels de patrimoine, deuxième trimestre 2023).
    #: Zéro rend l'ancienne convention, où tout le patrimoine était saisissable.
    part_assurance_vie_patrimoine: float = 0.10
    #: La part du capital d'assurance-vie au décès que les primes de la fenêtre
    #: représentent. Hypothèse : le reste vient des primes versées avant et des
    #: intérêts.
    part_assurance_vie_reprise: float = 0.6

    #: Seul ou à deux. Ne joue que sur l'allocation d'isolement : la garantie
    #: est individualisée, et le conjoint n'entre pas dans le calcul. Le défaut
    #: est la personne seule, comme pour l'ASPA du scénario 1, de sorte que les
    #: deux planchers se comparent.
    situation_foyer: SituationFoyer = SituationFoyer.SEUL

    # --- Pilier de capitalisation obligatoire (proposition) ------------------
    #: La troisième pièce de la proposition, après le taux unique et la garantie
    #: vieillesse : une cotisation OBLIGATOIRE, placée et non mutualisée, qui
    #: s'ajoute au compte notionnel au lieu de s'y substituer. Elle ne change
    #: rien à ce que la répartition sert — le compte notionnel est calculé sans
    #: elle et affiché sans elle —, et c'est pour cela qu'elle est tenue dans un
    #: compartiment distinct, ``moteur/capitalisation.py``.
    #:
    #: Mettre à ``False`` retire le pilier sans toucher au reste : la
    #: proposition redevient exactement ce qu'elle était avant lui, ce qu'un
    #: test vérifie.
    capitalisation_obligatoire: bool = True

    #: Taux de la cotisation capitalisée, prélevé sur la MÊME assiette que la
    #: cotisation notionnelle de l'année, EN PLUS d'elle : l'effort contributif
    #: monte de cinq points à compter de la bascule, il n'est pas redéployé.
    taux_capitalisation_obligatoire: float = 0.05

    #: Les frais du PER l'année de la bascule, tels que le marché les pratique
    #: en 2025 d'après le rapport 2026 de l'Observatoire des produits d'épargne
    #: financière, support en euros — le seul qui corresponde à un placement
    #: sans risque. Leur source, leurs réserves et leur distribution sont dans
    #: ``data/reference/macro/frais_epargne_retraite.yaml``, et un test refuse
    #: que les deux divergent.
    #:
    #: Quatre postes, et ce sont les VRAIES MOYENNES DU MARCHÉ, pas celles des
    #: seuls assureurs qui facturent. Sur versement et sur encours, les
    #: moyennes de l'OPEF sont déjà pondérées par les primes et par l'encours.
    #: Sur arrérages, l'OPEF ne publie que la moyenne des neuf assureurs sur
    #: vingt qui facturent (2,20 %) ; sur les vingt, c'est 0,99 %, et la
    #: médiane est nulle. Le quatrième poste, que l'OPEF ne mesure pas, est le
    #: prélèvement annuel sur la RÉSERVE de la rente, que le CCSF relevait sur
    #: 22 contrats sur 34 en 2021, de 0,60 à 1 % par an : 0,80 % au milieu de
    #: la fourchette, sur 22/34 des contrats, soit 0,52 % en moyenne. Il pèse
    #: bien plus que les arrérages : au diviseur du modèle, 0,52 % par an sur
    #: la réserve valent quelque 7 % de rente — la méthodologie le recalcule
    #: (``frais_reserve`` dans ``scripts/mesures_prose.py``).
    frais_versement_capitalisation: float = 0.0109
    frais_gestion_capitalisation: float = 0.0076
    frais_arrerages_capitalisation: float = 0.0099
    frais_encours_rente_capitalisation: float = 0.0052

    #: LES FRAIS BAISSENT AVEC LE TEMPS, et pas en ligne droite. Partout où une
    #: épargne retraite obligatoire existe, la concurrence ou la règle ont fait
    #: tomber les frais bien au-dessous de ceux d'un produit vendu au détail,
    #: et par à-coups : un plafond réglementaire (Royaume-Uni, 0,75 % en 2015,
    #: 0,48 % constaté en 2020), un appel d'offres périodique (Chili, la
    #: commission du gagnant passe de 1,14 % à 0,77 %, 0,47 %, 0,41 % d'une
    #: adjudication à l'autre, et remonte en 2018), une remise imposée aux
    #: gérants (Suède, 0,31 % net en 2013, 0,21 % en 2020, 0,11 % en 2026). Là
    #: où seule la concurrence joue, la baisse est continue : les fonds
    #: américains sont passés de 1,04 % à 0,40 % en vingt-neuf ans, soit 3,3 %
    #: de baisse par an, et les fonds des plans 401(k) de 0,76 % à 0,26 %.
    #:
    #: Chaque poste a donc sa TRAJECTOIRE : des paliers ``(année, taux)``, le
    #: taux valant de cette année jusqu'au palier suivant, et le niveau
    #: ci-dessus valant avant le premier palier. Des paliers, et non une pente,
    #: parce que c'est ainsi que les frais ont bougé ailleurs — une décision,
    #: puis un plateau. Les paliers retenus suivent le rythme américain, le
    #: seul observé sur trente ans, par marches de dix ans, jusqu'au plancher
    #: que l'ERAFP retient pour ses propres frais (0,20 % des encours) ; le
    #: frais sur versement rejoint l'assurance-vie d'aujourd'hui, puis le
    #: contrat de capitalisation, puis zéro, comme partout où la cotisation
    #: est prélevée sur la paie ; le frais sur arrérages, dont la médiane est
    #: déjà nulle, s'éteint en vingt ans. Un tuple vide fige le poste à son
    #: niveau de départ, et c'est ce que font les tests d'identité.
    frais_versement_paliers: tuple[tuple[int, float], ...] = (
        (2031, 0.0055), (2036, 0.0019), (2046, 0.0),
    )
    frais_gestion_paliers: tuple[tuple[int, float], ...] = (
        (2036, 0.0054), (2046, 0.0039), (2056, 0.0028), (2066, 0.0020),
    )
    frais_arrerages_paliers: tuple[tuple[int, float], ...] = (
        (2036, 0.0050), (2046, 0.0),
    )
    frais_encours_rente_paliers: tuple[tuple[int, float], ...] = (
        (2036, 0.0037), (2046, 0.0027), (2056, 0.0019), (2066, 0.0014),
    )

    #: LA BAISSE PORTE SURTOUT SUR LES NOUVEAUX DÉPÔTS, un peu sur le stock.
    #: Un frais de gestion est contractuel : le versement d'une année entre au
    #: tarif de son année et le garde. L'OPEF le montre — en deux ans, le frais
    #: sur versement du PER, mesuré sur les primes de l'année, a baissé de
    #: 1,20 % à 1,09 %, et celui de l'assurance-vie de 0,75 % à 0,55 %, quand
    #: le frais de gestion, mesuré sur tout l'encours, n'a pas bougé (0,73 %,
    #: 0,77 %, 0,76 %). Mais un plafond ou une remise imposée touchent le stock
    #: d'un coup, comme au Royaume-Uni et en Suède. Entre les deux, chaque
    #: cohorte de versements referme chaque année cette fraction de l'écart
    #: entre son tarif et celui des nouveaux dépôts : à 0,10, la moitié de
    #: l'écart en sept ans. Zéro fige chaque cohorte à son tarif d'entrée, un
    #: aligne tout le stock sur le tarif du jour.
    convergence_frais_stock: float = 0.10

    def sous_regime_frais(self, regime: str) -> "Parametres":
        """Les mêmes paramètres, sous l'un des régimes de frais du site.

        C'est le réglage « Frais du pilier capitalisé » du simulateur et des
        pages qui agrègent, et il n'existe qu'ici : les deux portages
        l'appliquent, aucun ne le redéfinit. ``paliers`` est le réglage par
        défaut, tel quel. ``plafond`` et ``contrats`` gardent les paliers et
        déplacent la convergence du stock aux deux bornes : tout le stock suit
        d'un coup, ou chaque cohorte garde son tarif. ``figes`` fige les
        moyennes de 2025 sans aucune baisse. ``detail`` est le PER tel qu'il
        est vendu, sans baisse ni frais sur la réserve, et 2,20 % d'arrérages,
        la moyenne des seuls assureurs qui facturent : l'ancien réglage du
        modèle, gardé pour dire ce qu'il valait. ``aucun`` retire tout.
        """
        figes = dict(frais_versement_paliers=(), frais_gestion_paliers=(),
                     frais_arrerages_paliers=(), frais_encours_rente_paliers=())
        regimes = {
            "paliers": {},
            "plafond": dict(convergence_frais_stock=1.0),
            "contrats": dict(convergence_frais_stock=0.0),
            "figes": figes,
            "detail": dict(frais_arrerages_capitalisation=FRAIS_ARRERAGES_VENDU,
                           frais_encours_rente_capitalisation=0.0, **figes),
            "aucun": dict(frais_versement_capitalisation=0.0,
                          frais_gestion_capitalisation=0.0,
                          frais_arrerages_capitalisation=0.0,
                          frais_encours_rente_capitalisation=0.0, **figes),
        }
        if regime not in regimes:
            raise ValueError(f"régime de frais inconnu : {regime!r} "
                             f"(attendu : {tuple(regimes)})")
        return self.avec(**regimes[regime])

    def sous_regime_taux(self, regime: str) -> "Parametres":
        """Les mêmes paramètres, sous l'un des régimes de taux du site.

        C'est le réglage « Taux futurs du pilier capitalisé », et il n'existe
        qu'ici : les deux portages l'appliquent, aucun ne le redéfinit. Il ne
        touche qu'une chose, ``prime_terme_trente_ans``, mais cette chose
        gouverne à elle seule ce que l'ALLOCATION des maturités peut valoir.

        ``forwards`` est le défaut et vaut zéro : les versements futurs se
        placent aux taux à terme que la courbe du jour implique, hypothèse des
        anticipations pures. Elle est explicite, arbitrée, et elle flatte le
        pilier. Elle a surtout un effet que ce menu est fait pour montrer :
        sous elle, **aucune allocation de maturités n'en vaut une autre**, et
        le titre adossé à la date du départ rapporte exactement ce que
        rapporterait un roulement à un an.

        ``prime`` et ``prime_haute`` la retirent, au milieu puis au haut de la
        fourchette de la littérature. Le pilier baisse — c'est le prix de
        l'hypothèse — et l'adossement se met à rapporter, parce qu'il capte la
        prime une fois pour toutes là où un roulement la rachète à chaque
        échéance.
        """
        regimes = {
            "forwards": 0.0,
            "prime": PRIME_TERME_MILIEU,
            "prime_haute": PRIME_TERME_HAUTE,
        }
        if regime not in regimes:
            raise ValueError(f"régime de taux inconnu : {regime!r} "
                             f"(attendu : {tuple(regimes)})")
        return self.avec(prime_terme_trente_ans=regimes[regime])

    # --- Capitalisation volontaire : les cinq points rendus ------------------
    #: Le quatrième terme, et le seul que personne n'impose. Le système actuel
    #: prélève près de 28 % du salaire pour la retraite ; la proposition en
    #: prélève 23 — 18 de répartition, 5 capitalisés d'office. Elle rend donc
    #: CINQ POINTS, et la question que tout le monde pose ensuite est la même :
    #: et si on les remettait au même endroit ?
    #:
    #: Ce paramètre y répond. Il ajoute au pilier capitalisé une cotisation
    #: VOLONTAIRE, de même taux, sur la même assiette, la même année : l'effort
    #: contributif revient alors exactement à ce qu'il est aujourd'hui, et le
    #: site peut montrer, à taux égal cotisé, ce que la proposition sert contre
    #: ce que le système actuel sert. C'est la seule comparaison où les deux
    #: colonnes coûtent le même prix.
    #:
    #: Elle est volontaire, et cela a deux conséquences que le modèle tient.
    #: Sur la FICHE DE PAIE, elle est entièrement à la charge de l'assuré :
    #: aucun employeur ne verse une épargne que son salarié décide seul, et le
    #: coût du travail ne bouge donc pas d'un centime quand on l'active. Sur la
    #: PENSION, elle se confond avec le pilier obligatoire — même placement,
    #: mêmes frais, même rente, même transmission —, et le compartiment garde
    #: la trace de ce qui vient d'elle : voir ``Capitalisation.part_volontaire``.
    #:
    #: Mettre à ``False`` la retire sans toucher au reste, et la proposition
    #: redevient 18 + 5, ce qu'un test vérifie.
    capitalisation_volontaire: bool = True

    #: Taux de la cotisation capitalisée volontaire. Cinq points : exactement
    #: ce que la proposition rend, à la décimale près de ce que le système
    #: actuel prélève en moyenne. Le mettre ailleurs déplace le total cotisé, et
    #: la comparaison « à taux égal » cesse d'en être une.
    taux_capitalisation_volontaire: float = 0.05

    #: Taux technique de la rente viagère servie par le pilier. Nul par défaut,
    #: comme dans la plupart des PER : la rente n'anticipe alors aucun
    #: rendement futur, et son diviseur est EXACTEMENT celui de la pension
    #: notionnelle — les deux compartiments deviennent comparables au centime.
    #: Un taux positif verse davantage au début et moins ensuite, à espérance
    #: de coût inchangée, comme ``taux_anticipe_conversion`` pour la
    #: répartition.
    taux_technique_rente_capitalisation: float = 0.0

    #: Prime de terme retirée des forwards de la courbe sans risque, exprimée à
    #: trente ans et en rythme continu. **Zéro par défaut**, et c'est le
    #: réglage sous lequel le site publie : les versements futurs se placent
    #: aux forwards de la courbe du jour, hypothèse des anticipations pures.
    #:
    #: Ce que le paramètre ouvre. La littérature situe la prime de terme entre
    #: 0,3 et 1 point sur les maturités longues quand la courbe est ascendante,
    #: et le pilier est d'autant flatté (``docs/limites.md``, réserve 1 du
    #: pilier capitalisé). La mettre à 0,005 retire donc une demi-hypothèse au
    #: modèle : le capital baisse, et l'ADOSSEMENT À L'HORIZON se met à
    #: rapporter, parce que bloquer la maturité du départ capte la prime une
    #: fois pour toutes là où le roulement la rachète à chaque échéance. Sous
    #: les anticipations pures, aucune allocation n'en vaut une autre : c'est
    #: l'arbitrage qui fixe le forward, et un test l'exige.
    #:
    #: Elle ne porte QUE sur la courbe du pilier capitalisé
    #: (``Simulateur.courbe_taux_pilier``), et non sur celle que lit le taux
    #: d'emprunt de la dette du chiffrage. La prime est bien une propriété du
    #: marché, et le coût de rouler une dette courte se pose dans les mêmes
    #: termes ; mais c'est une AUTRE question, qui a ses propres réserves, et
    #: un réglage nommé « taux futurs du pilier capitalisé » n'est pas
    #: l'endroit d'où la trancher. Portée sur la courbe commune, elle
    #: déplaçait le stock de dette de TOUS les systèmes, jusqu'à dix points de
    #: PIB sur le système actuel, qui n'a pas de pilier du tout.
    prime_terme_trente_ans: float = 0.0

    # --- Neutralisations ----------------------------------------------------
    neutralisations: Neutralisations = field(default_factory=Neutralisations)

    # --- Compartiments hors répartition -------------------------------------
    #: Les régimes marqués ``hors_repartition`` (RAFP, ex-assurances sociales)
    #: sont isolés et ne sont jamais convertis en capital notionnel.
    isoler_capitalisation: bool = True

    # --- Contrôle qualité des données ---------------------------------------
    #: Niveau de fiabilité minimal exigé des séries utilisées. En dessous, la
    #: simulation lève une erreur au lieu de produire un chiffre trompeur.
    #: Valeurs : "estimee" (tout accepter), "moyenne", "haute", "certifiee".
    fiabilite_minimale: str = "estimee"

    # --- Chemins ------------------------------------------------------------
    racine_donnees: Path = RACINE_DONNEES

    def frais_capitalisation(self, poste: str, annee: int) -> float:
        """Le taux d'un poste de frais du pilier l'année ``annee``.

        ``poste`` est ``versement``, ``gestion``, ``arrerages`` ou
        ``encours_rente``. Le niveau de départ vaut avant le premier palier ;
        ensuite, le dernier palier dont l'année est atteinte.
        """
        niveau = getattr(self, f"frais_{poste}_capitalisation")
        paliers = getattr(self, f"frais_{poste}_paliers")
        return taux_au(niveau, paliers, annee)

    @property
    def taux_capitalisation_volontaire_applique(self) -> float:
        """Les cinq points volontaires, ou zéro quand on les a retirés."""
        return (self.taux_capitalisation_volontaire
                if self.capitalisation_volontaire else 0.0)

    @property
    def taux_capitalisation_applique(self) -> float:
        """Ce que le pilier capitalisé encaisse en tout, obligatoire et volontaire.

        Un seul taux en sort, parce que le placement, les frais et la rente ne
        distinguent pas les deux origines : ce qui les distingue est sur la
        fiche de paie, où l'une est partagée avec l'employeur et l'autre pas,
        et dans ce que la page en dit. Le compartiment, lui, garde la
        proportion (``Capitalisation.part_volontaire``).
        """
        obligatoire = (self.taux_capitalisation_obligatoire
                       if self.capitalisation_obligatoire else 0.0)
        return obligatoire + self.taux_capitalisation_volontaire_applique

    @property
    def taux_retraite_propose(self) -> float:
        """Tout ce que la proposition prélève sur la rémunération, en un taux.

        C'est le nombre qui se compare aux quelque 28 % d'aujourd'hui, et la
        raison d'être des cinq points volontaires : 18 et 5 en font 23, les
        cinq derniers ramènent à 28.
        """
        return self.taux_cotisation_liberal + self.taux_capitalisation_applique

    def avec(self, **modifications) -> "Parametres":
        """Retourne une copie modifiée (les paramètres sont immuables)."""
        return replace(self, **modifications)


#: Configuration de référence. Elle suit le cahier des charges partout sauf sur
#: l'indexation, où elle retient le taux d'équilibre de la répartition ; la
#: lecture littérale du cahier des charges est
#: ``PARAMETRES_DEFAUT.avec(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)``.
PARAMETRES_DEFAUT = Parametres()
