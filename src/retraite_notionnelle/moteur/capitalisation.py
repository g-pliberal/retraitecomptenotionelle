"""Le pilier de capitalisation obligatoire : accumulation, rente, transmission.

Ce compartiment n'est PAS un compte notionnel, et tout le module tient à cette
différence. Le compte notionnel est virtuel : rien n'y est placé, la
revalorisation est une règle collective, et ce que l'assuré n'a pas consommé à
sa mort revient à la collectivité. Ici, un capital existe vraiment : il est
placé, il rapporte un taux de marché, il supporte des frais, et il **se
transmet** si l'assuré meurt avant d'avoir liquidé. Les deux compartiments sont
donc tenus séparément, affichés séparément, et ne s'additionnent qu'au dernier
moment, sur la ligne « total ».

Cinq décisions le définissent, et chacune est un endroit où le modèle peut être
contesté.

**1. Ce qui l'alimente.** Un taux unique — 5 % — appliqué, à compter de l'année
de bascule, à la MÊME assiette que la cotisation notionnelle de l'année. Le
même prélèvement, sur la même base, en plus : la proposition ajoute cinq points
d'effort, elle n'en redéploie pas. Les années antérieures à la bascule
n'alimentent rien, et qui a liquidé avant n'a pas de pilier du tout.

**2. Où il est placé.** Sur des titres sans risque à plusieurs maturités, selon
une règle d'horizon : longues tant que le départ est loin, courtes à l'approche
— c'est l'allocation par « glide path » que toute épargne retraite à échéance
pratique. Aucune ligne ne dépasse la date de départ (:func:`repartition`), et
les taux sont ceux de la courbe et de ses forwards
(:class:`~retraite_notionnelle.donnees.taux.CourbeTauxSansRisque`).

**3. Ce qu'il coûte.** Les trois frais du PER tel qu'il est vendu aujourd'hui :
sur chaque versement, sur l'encours chaque année, sur chaque arrérage de rente.

**4. Ce qu'il sert.** Une rente viagère, et rien d'autre : ni capital, ni sortie
anticipée. Elle est calculée avec la table de mortalité du modèle et le même
diviseur que la pension notionnelle, de sorte que les deux compartiments soient
comparables au centime — c'est le mécanisme du PER, dont le taux technique est
le plus souvent nul.

**5. Ce qu'il transmet.** Le capital acquis, intégralement, si l'assuré meurt
avant la liquidation. Après elle, la rente viagère s'éteint avec le rentier :
c'est ce que le pilier échange contre son montant. Les deux faits sont portés
par :class:`Capitalisation`, parce qu'aucun des deux ne s'en déduit tout seul.

CONVENTION DE DATE, ET POURQUOI C'EST LA MÊME QUE CELLE DU COMPTE NOTIONNEL.
Le versement d'une année est crédité à la FIN de cette année : il rapporte donc
de l'année suivante jusqu'à l'année de liquidation incluse, soit exactement les
années où le compte notionnel le revaloriserait (voir
``Indexation.coefficient``). Sans cette symétrie, l'écart entre les deux
compartiments contiendrait une année de rendement offerte à l'un des deux, et
le lecteur la prendrait pour un effet de la capitalisation.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Parametres, TableConversion
from ..donnees.chargement import Fiabilite
from ..donnees.mortalite import DonneesMortalite
from ..donnees.taux import CourbeTauxSansRisque
from .conversion import CoefficientConversion, Convertisseur

#: Les trois maturités de l'échelle, en années : courte, moyenne, longue. Trois
#: suffisent à porter la règle d'horizon, et chacune est un point coté de la
#: courbe — ni interpolé, ni extrapolé, tant que l'horizon reste dans la courbe.
MATURITES = (2, 10, 30)

#: Horizon à partir duquel la part longue est à son maximum, et horizon en
#: deçà duquel la part courte l'est. Entre les deux, les deux parts glissent
#: linéairement, et la maturité moyenne prend ce qu'elles laissent.
HORIZON_LONG = 30
HORIZON_PIVOT = 10
HORIZON_COURT = 2

#: Part maximale d'une seule maturité. Elle vaut 3/4, et non 1 : une épargne
#: obligatoire ne se concentre pas sur un seul point de la courbe, même quand
#: l'horizon y invite. En début de carrière l'allocation est donc
#: PRINCIPALEMENT longue, jamais exclusivement ; à l'approche du départ elle
#: est principalement courte, et de toute façon plafonnée par la date de
#: départ, qui ramène toutes les maturités à l'horizon restant.
PART_MAXIMALE = 0.75

#: Fiabilité du barème de frais. Les trois valeurs viennent du rapport annuel
#: de l'Observatoire des produits d'épargne financière, que le dépôt n'a pas su
#: récupérer automatiquement : elles sont SAISIES, et la règle du manifeste
#: plafonne à ``haute`` ce qui n'a pas été confronté au document du producteur.
#: Elle qualifie donc tout résultat du pilier, comme n'importe quelle série.
FIABILITE_FRAIS = Fiabilite.HAUTE


def _borner(valeur: float) -> float:
    return min(1.0, max(0.0, valeur))


def repartition(horizon: int) -> tuple[tuple[int, float], ...]:
    """Maturités et poids d'un versement placé à ``horizon`` années du départ.

    La règle tient en trois lignes, et sa monotonie est vérifiée par un test :
    la part longue croît avec l'horizon, la part courte décroît, et aucune
    maturité ne dépasse l'horizon — un titre qui arriverait à échéance après le
    départ devrait être vendu avant terme, donc à un prix qui n'est plus sans
    risque.

    Les poids sont rendus par maturité EFFECTIVE, donc fusionnés lorsque le
    plafonnement fait coïncider deux maturités : à deux ans du départ, les
    trois lignes de l'échelle sont la même.
    """
    if horizon <= 0:
        return ()
    part_longue = PART_MAXIMALE * _borner(
        (horizon - HORIZON_PIVOT) / (HORIZON_LONG - HORIZON_PIVOT)
    )
    part_courte = PART_MAXIMALE * _borner(
        (HORIZON_PIVOT - horizon) / (HORIZON_PIVOT - HORIZON_COURT)
    )
    poids = (part_courte, 1.0 - part_courte - part_longue, part_longue)

    cumul: dict[int, float] = {}
    for maturite, part in zip(MATURITES, poids):
        if part <= 0:
            continue
        effective = min(maturite, horizon)
        cumul[effective] = cumul.get(effective, 0.0) + part
    return tuple(sorted(cumul.items()))


@dataclass
class _Ligne:
    """Une ligne de l'échelle : un montant placé jusqu'à une année donnée."""

    montant: float
    #: Dernière année où la ligne porte intérêt. Elle est replacée au début de
    #: l'année suivante.
    annee_fin: int
    taux: float


@dataclass(frozen=True)
class AnneeCapitalisation:
    """Une année du compte capitalisé, de l'ouverture à la clôture.

    Tout y est en euros courants de l'année : c'est un capital réel, pas un
    solde notionnel, et la page qui l'affiche doit pouvoir montrer la ligne
    d'un relevé.
    """

    annee: int
    age: float
    #: Années restant à courir jusqu'à la liquidation, au moment du versement.
    horizon: int
    assiette: float
    versement_brut: float
    frais_versement: float
    versement_net: float
    encours_ouverture: float
    interets: float
    frais_gestion: float
    #: Encours de clôture, net de tous frais : c'est le capital qui serait
    #: transmis si l'assuré mourait cette année-là.
    encours: float
    #: Taux moyen pondéré des lignes vivantes pendant l'année.
    taux_moyen: float
    #: Répartition du versement de l'année par maturité, en euros.
    placements: tuple[tuple[int, float], ...] = ()

    @property
    def capital_transmissible(self) -> float:
        return self.encours


@dataclass(frozen=True)
class Capitalisation:
    """Le pilier capitalisé d'une carrière : ce qu'il accumule, sert et transmet."""

    #: Année d'ouverture du pilier — celle de la bascule, ou l'entrée dans la
    #: vie active si elle est postérieure.
    annee_ouverture: int
    annee_liquidation: int
    taux_cotisation: float
    annees: tuple[AnneeCapitalisation, ...]

    #: Capital au départ, net de tous frais.
    capital: float
    #: Le même capital si l'enveloppe ne prélevait rien. L'écart avec le
    #: précédent est le coût complet des frais : les prélèvements eux-mêmes, et
    #: les intérêts qu'ils n'ont pas produits.
    capital_hors_frais: float

    #: Diviseur actuariel de la rente — celui du compte notionnel quand le taux
    #: technique est nul, ce qui est le réglage par défaut.
    conversion: CoefficientConversion
    frais_arrerages: float
    #: Rente viagère annuelle servie, nette des frais sur arrérages.
    rente_annuelle: float

    #: Probabilité de mourir avant d'avoir liquidé, vue de l'ouverture du
    #: pilier, sur la table du modèle.
    probabilite_deces_avant_liquidation: float
    #: Espérance du capital transmis, vue de l'ouverture du pilier : chaque
    #: année de décès possible pèse l'encours de cette année-là.
    esperance_capital_transmis: float

    #: Date de la courbe de taux employée, telle que la BCE la publie. Portée
    #: ici pour que la page qui affiche un capital puisse dire de quel jour
    #: sont les taux qui l'ont produit, sans relire le fichier.
    date_courbe: str = ""

    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    @property
    def actif(self) -> bool:
        """Le pilier a-t-il seulement reçu quelque chose ?"""
        return self.capital > 0

    @property
    def rente_mensuelle(self) -> float:
        return self.rente_annuelle / 12.0

    @property
    def versements(self) -> float:
        """Somme des versements bruts, en euros courants, sans revalorisation."""
        return sum(a.versement_brut for a in self.annees)

    @property
    def frais_versement(self) -> float:
        return sum(a.frais_versement for a in self.annees)

    @property
    def frais_gestion(self) -> float:
        return sum(a.frais_gestion for a in self.annees)

    @property
    def interets(self) -> float:
        return sum(a.interets for a in self.annees)

    @property
    def frais_preleves(self) -> float:
        """Frais effectivement prélevés, en euros courants cumulés.

        Les frais sur arrérages n'y sont pas : ils seront prélevés sur la
        rente, année après année, et non sur le capital.
        """
        return self.frais_versement + self.frais_gestion

    @property
    def cout_des_frais(self) -> float:
        """Ce que les frais retirent au capital, intérêts perdus compris."""
        return self.capital_hors_frais - self.capital

    @property
    def annees_cotisees(self) -> int:
        return sum(1 for a in self.annees if a.versement_brut > 0)

    @property
    def rendement_cumule(self) -> float:
        """Capital rapporté aux versements bruts."""
        return self.capital / self.versements if self.versements else 0.0

    @property
    def taux_rendement_annuel(self) -> float:
        """Taux de rendement interne du pilier, frais compris.

        C'est le taux constant qui, appliqué aux versements bruts aux mêmes
        dates, donnerait le même capital. Il se lit contre les taux de la
        courbe : l'écart est le prix de l'enveloppe.
        """
        return _taux_interne(
            [(a.annee, a.versement_brut) for a in self.annees if a.versement_brut > 0],
            self.annee_liquidation,
            self.capital,
        )


def _taux_interne(versements: list[tuple[int, float]], annee_finale: int,
                  capital: float, tolerance: float = 1e-10) -> float:
    """Taux constant qui mène des versements au capital, par dichotomie.

    La fonction est strictement croissante en le taux dès qu'un versement est
    positif : la dichotomie converge donc, et sans dérivée. Les bornes sont
    larges — de −99 % à +100 % — parce qu'un pilier ouvert un an avant le
    départ peut afficher un rendement négatif du seul fait des frais.
    """
    if not versements or capital <= 0:
        return 0.0

    def valeur(taux: float) -> float:
        return sum(
            montant * (1.0 + taux) ** (annee_finale - annee)
            for annee, montant in versements
        ) - capital

    bas, haut = -0.99, 1.0
    if valeur(bas) > 0 or valeur(haut) < 0:
        # Un seul cas le produit : tous les versements tombent l'année de la
        # liquidation, où ils ne rapportent rien et où les frais les amputent.
        # Aucun taux ne relie alors les uns à l'autre — l'exposant est nul —, et
        # zéro est rendu plutôt qu'un NaN, qui ne s'écrit pas en JSON et qui
        # n'est égal à rien, pas même à lui-même. La page, elle, ne parle pas
        # de rendement dans ce cas : elle dit que le pilier n'a pas eu d'année
        # pour rapporter.
        return 0.0
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if valeur(milieu) < 0:
            bas = milieu
        else:
            haut = milieu
        if haut - bas < tolerance:
            break
    return 0.5 * (bas + haut)


class ConstructeurCapitalisation:
    """Construit le pilier capitalisé d'une carrière.

    Les entrées sont volontairement minces : les assiettes annuelles du compte
    notionnel, l'âge et la date de liquidation. Le compartiment ne connaît donc
    ni les régimes, ni l'indexation, ni les droits acquis — il ne peut pas les
    contredire.
    """

    def __init__(self, courbe: CourbeTauxSansRisque, mortalite: DonneesMortalite,
                 convertisseur: Convertisseur, parametres: Parametres) -> None:
        # Le convertisseur reçu est celui du TAUX TECHNIQUE de la rente, qui
        # n'est pas forcément celui de la pension notionnelle : le simulateur
        # le dérive de ``taux_technique_rente_capitalisation``. Au réglage par
        # défaut — taux technique nul — les deux coïncident, et c'est voulu.
        self.courbe = courbe
        self.mortalite = mortalite
        self.convertisseur = convertisseur
        self.parametres = parametres

    # -- placement -----------------------------------------------------------

    def placer(self, montant: float, annee: int, annee_liquidation: int,
               lignes: list[_Ligne]) -> tuple[tuple[int, float], ...]:
        """Place ``montant``, disponible à la fin de ``annee``, sur l'échelle.

        Rend la répartition en euros, par maturité, pour que la page puisse
        montrer où va un versement. Un montant disponible l'année même de la
        liquidation ne se place plus : il n'a plus d'années devant lui, et le
        compte notionnel ne revalorise pas davantage sa dernière cotisation.
        """
        horizon = annee_liquidation - annee
        if montant <= 0:
            return ()
        if horizon <= 0:
            lignes.append(_Ligne(montant=montant, annee_fin=annee, taux=0.0))
            return ()
        detail: list[tuple[int, float]] = []
        for maturite, poids in repartition(horizon):
            part = montant * poids
            if part <= 0:
                continue
            taux = self.courbe.placement(annee, maturite)
            lignes.append(
                _Ligne(montant=part, annee_fin=annee + maturite, taux=taux.taux)
            )
            detail.append((maturite, part))
        return tuple(detail)

    def _fiabilite_placements(self, annee_ouverture: int,
                              annee_liquidation: int) -> Fiabilite:
        """Le plus bas niveau atteint par un taux effectivement employé."""
        niveau = Fiabilite.CERTIFIEE
        for annee in range(annee_ouverture, annee_liquidation):
            for maturite, _ in repartition(annee_liquidation - annee):
                niveau = min(niveau, self.courbe.placement(annee, maturite).fiabilite)
        return niveau

    # -- accumulation --------------------------------------------------------

    def _accumuler(self, assiettes: dict[int, float], annee_ouverture: int,
                   annee_liquidation: int, annee_naissance: int,
                   avec_frais: bool) -> list[AnneeCapitalisation]:
        frais_versement = (
            self.parametres.frais_versement_capitalisation if avec_frais else 0.0
        )
        frais_gestion = (
            self.parametres.frais_gestion_capitalisation if avec_frais else 0.0
        )
        taux_cotisation = self.parametres.taux_capitalisation_obligatoire

        lignes: list[_Ligne] = []
        annees: list[AnneeCapitalisation] = []

        for annee in range(annee_ouverture, annee_liquidation + 1):
            ouverture = sum(l.montant for l in lignes)

            # 1. Intérêts de l'année, ligne par ligne, au taux bloqué le jour
            #    du placement. C'est ce que « porter jusqu'à l'échéance » veut
            #    dire : le taux d'une ligne ne change plus.
            interets = sum(l.montant * l.taux for l in lignes)
            for ligne in lignes:
                ligne.montant *= 1.0 + ligne.taux

            # 2. Frais de gestion, prélevés sur l'encours de fin d'année, au
            #    prorata de chaque ligne. Le versement de l'année n'y est pas
            #    encore : il n'a pas passé l'année dans l'enveloppe.
            prelevement = (ouverture + interets) * frais_gestion
            if prelevement:
                for ligne in lignes:
                    ligne.montant *= 1.0 - frais_gestion

            # 3. Échéances : ce qui arrive à terme est replacé pour ce qu'il
            #    reste d'horizon.
            echues = sum(l.montant for l in lignes if l.annee_fin == annee)
            lignes = [l for l in lignes if l.annee_fin != annee]
            if echues:
                self.placer(echues, annee, annee_liquidation, lignes)

            # 4. Versement de l'année, crédité en fin d'année.
            assiette = assiettes.get(annee, 0.0)
            brut = assiette * taux_cotisation
            frais = brut * frais_versement
            net = brut - frais
            placements = self.placer(net, annee, annee_liquidation, lignes)

            encours = sum(l.montant for l in lignes)
            annees.append(AnneeCapitalisation(
                annee=annee,
                age=annee - annee_naissance,
                horizon=annee_liquidation - annee,
                assiette=assiette,
                versement_brut=brut,
                frais_versement=frais,
                versement_net=net,
                encours_ouverture=ouverture,
                interets=interets,
                frais_gestion=prelevement,
                encours=encours,
                taux_moyen=(interets / ouverture) if ouverture > 0 else 0.0,
                placements=placements,
            ))
        return annees

    # -- transmission --------------------------------------------------------

    def _transmission(self, annees: list[AnneeCapitalisation], age_ouverture: float,
                      annee_ouverture: int, sexe: str | None) -> tuple[float, float]:
        """Probabilité de mourir avant le départ, et espérance du capital transmis.

        Vues de l'OUVERTURE du pilier, et non de la naissance : ce qui est en
        jeu est le capital de ce compte-là, qui n'existe pas avant. Chaque
        année de décès possible pèse l'encours MOYEN de l'année — celui du
        début et celui de la fin —, parce qu'un décès ne choisit pas son mois.

        L'année de la liquidation elle-même n'est pas comptée : le modèle
        calcule une pension pour un assuré qui atteint son départ, et compter
        cette année-là ferait servir la rente et transmettre le capital à la
        fois.
        """
        courbe = self.mortalite.courbe(
            age_ouverture, float(annee_ouverture), sexe,
            self.parametres.table_generation,
        )
        esperance = 0.0
        deces = 0.0
        for indice, annee in enumerate(annees[:-1]):
            if indice + 1 >= len(courbe):
                break
            probabilite = courbe[indice] - courbe[indice + 1]
            moyen = 0.5 * (annee.encours_ouverture + annee.encours)
            esperance += probabilite * moyen
            deces += probabilite
        return deces, esperance

    # -- assemblage ----------------------------------------------------------

    def construire(self, assiettes: dict[int, float], annee_naissance: int,
                   age_liquidation: float, annee_liquidation: int,
                   mois_liquidation: int = 1, sexe: str | None = None) -> Capitalisation:
        """Le pilier d'une carrière, de son ouverture à sa rente.

        ``assiettes`` porte, année par année, l'assiette sur laquelle la
        cotisation notionnelle a été prélevée : le pilier s'appuie sur elle et
        n'en construit pas une autre.
        """
        ouverture = max(
            self.parametres.annee_debut_capitalisation,
            min(assiettes) if assiettes else self.parametres.annee_debut_capitalisation,
        )
        conversion = self.convertisseur.coefficient(
            age_liquidation, annee_liquidation,
            None if self.parametres.table_conversion is TableConversion.UNISEXE else sexe,
            mois_liquidation,
        )

        if annee_liquidation < ouverture or not self.parametres.capitalisation_obligatoire:
            return Capitalisation(
                annee_ouverture=ouverture,
                annee_liquidation=annee_liquidation,
                taux_cotisation=self.parametres.taux_capitalisation_obligatoire,
                annees=(),
                capital=0.0,
                capital_hors_frais=0.0,
                conversion=conversion,
                frais_arrerages=self.parametres.frais_arrerages_capitalisation,
                rente_annuelle=0.0,
                probabilite_deces_avant_liquidation=0.0,
                esperance_capital_transmis=0.0,
                date_courbe=self.courbe.date,
                fiabilite=conversion.fiabilite,
            )

        annees = self._accumuler(
            assiettes, ouverture, annee_liquidation, annee_naissance, avec_frais=True
        )
        sans_frais = self._accumuler(
            assiettes, ouverture, annee_liquidation, annee_naissance, avec_frais=False
        )
        capital = annees[-1].encours if annees else 0.0

        # La rente du PER : capital divisé par le diviseur actuariel, puis
        # amputé des frais sur arrérages, qui sont prélevés sur chaque
        # versement de rente et non sur le capital qui la constitue.
        frais_arrerages = self.parametres.frais_arrerages_capitalisation
        rente = capital / conversion.diviseur * (1.0 - frais_arrerages)

        deces, transmis = self._transmission(
            annees, ouverture - annee_naissance, ouverture,
            None if self.parametres.table_conversion is TableConversion.UNISEXE else sexe,
        )

        return Capitalisation(
            annee_ouverture=ouverture,
            annee_liquidation=annee_liquidation,
            taux_cotisation=self.parametres.taux_capitalisation_obligatoire,
            annees=tuple(annees),
            capital=capital,
            capital_hors_frais=sans_frais[-1].encours if sans_frais else 0.0,
            conversion=conversion,
            frais_arrerages=frais_arrerages,
            rente_annuelle=rente,
            probabilite_deces_avant_liquidation=deces,
            esperance_capital_transmis=transmis,
            date_courbe=self.courbe.date,
            fiabilite=min(
                conversion.fiabilite,
                self._fiabilite_placements(ouverture, annee_liquidation),
                FIABILITE_FRAIS,
            ),
        )
