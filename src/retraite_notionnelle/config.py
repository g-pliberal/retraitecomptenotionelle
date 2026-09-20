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
    Coût, et que pour les systèmes 2 à 6 : le système 1 est le droit.
    """

    PRIX = "prix"
    REINDEXE = "reindexe"


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


@dataclass(frozen=True)
class Parametres:
    """Jeu complet de paramètres d'une simulation."""

    # --- Bornes temporelles -------------------------------------------------
    #: Année d'origine du système par répartition. 1941 = allocation aux vieux
    #: travailleurs salariés, premier mécanisme financé par les cotisations des
    #: actifs. Mettre 1945 pour partir des ordonnances créant la Sécurité sociale.
    annee_debut_repartition: int = 1941

    #: Année de bascule du scénario prospectif : les droits acquis jusqu'à cette
    #: année incluse sont calculés selon les règles actuelles, les droits
    #: postérieurs selon le compte notionnel du régime fusionné.
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
    #: la Sécurité sociale. ``None`` = assiette déplafonnée.
    plafond_assiette_en_pass: float | None = 8.0

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

    #: Population dont la mortalité remplace celle de la population générale
    #: dans le diviseur — une clé de
    #: ``data/reference/mortalite/esperances_vie_populations.csv``, telle
    #: ``fonctionnaires_civils_etat``. ``None``, le défaut, est la table
    #: commune : un système qui trierait ses rentes par population ne serait
    #: pas défendable. La variante existe pour MESURER ce que le diviseur
    #: commun transfère à qui vit plus longtemps (action 14).
    population_conversion: str | None = None

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
    #: porte quoi ; le dépôt partage MOITIÉ-MOITIÉ — 9 % et 9 % —, et de même
    #: pour les 5 % capitalisés.
    #:
    #: Ce paramètre ne touche à AUCUNE pension : le compte notionnel porte la
    #: somme des deux parts, et le partage lui est indifférent. Il ne sert qu'à
    #: la fiche de paie de `remuneration.py` — mais il y compte, et beaucoup :
    #: la CSG est assise sur le BRUT, que le partage déplace, et la réduction
    #: générale n'efface que des cotisations PATRONALES. Plus la part patronale
    #: est grosse, plus le salaire net est élevé à coût du travail donné. Voir
    #: le docstring de `remuneration.py`.
    part_salariale_taux_unique: float = 0.5

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

    #: Première année de cotisation au pilier. Les années antérieures gardent
    #: les taux qui étaient les leurs et ne versent rien : qui a liquidé avant
    #: n'a pas de pilier, et qui liquide après n'en a que les années d'après.
    #: C'est l'année de bascule, pour que la proposition change tout le même
    #: jour.
    annee_debut_capitalisation: int = 2026

    #: Les trois frais du PER, tels que l'Observatoire des produits d'épargne
    #: financière les mesure pour 2025 sur le support en euros — le seul qui
    #: corresponde à un placement sans risque. Leur source et leurs réserves
    #: sont dans ``data/reference/macro/frais_epargne_retraite.yaml``, et un
    #: test refuse que les deux divergent.
    #:
    #: Ce sont les frais d'un produit VENDU À DES VOLONTAIRES, contrat par
    #: contrat : la commission du réseau qui le place est l'essentiel du frais
    #: sur versement, et elle n'a pas d'objet quand la cotisation est
    #: obligatoire. Les retenir tels quels est donc une borne haute, assumée.
    frais_versement_capitalisation: float = 0.0109
    frais_gestion_capitalisation: float = 0.0076
    frais_arrerages_capitalisation: float = 0.0220

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
