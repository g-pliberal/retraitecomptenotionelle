"""Le pilier de capitalisation : accumulation, rente, transmission.

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

**1. Ce qui l'alimente.** Deux cotisations, appliquées à compter de l'année de
bascule à la MÊME assiette que la cotisation notionnelle de l'année. La
première — 5 % — est OBLIGATOIRE : la proposition l'ajoute aux 18 % de
répartition, elle ne la redéploie pas. La seconde — 5 % encore — est
VOLONTAIRE, et c'est la seule pièce du modèle que personne n'impose : elle
remet au compte les cinq points que la proposition rend, de sorte que l'effort
contributif retombe sur les quelque 28 % d'aujourd'hui et que les deux systèmes
se comparent à prix égal. Le pilier ne les distingue nulle part ailleurs qu'en
proportion (:attr:`Capitalisation.part_volontaire`) : même assiette, même
placement, mêmes frais, même rente. Ce qui les sépare est sur la fiche de paie,
où l'obligatoire est partagée avec l'employeur et la volontaire pas. Les années
antérieures à la bascule n'alimentent rien, et qui a liquidé avant n'a pas de
pilier du tout.

Tout ce que le pilier produit est PROPORTIONNEL à ce taux — les frais sont des
pourcentages, l'échelle de placement ne dépend que de l'horizon, et aucun seuil
n'intervient. Le capital et la rente se partagent donc entre les deux origines
au prorata exact des taux, et un test l'exige : c'est ce qui autorise
:attr:`Capitalisation.rente_volontaire` à diviser plutôt qu'à recalculer.

**2. Où il est placé.** Sur un titre sans risque ADOSSÉ À L'HORIZON : chaque
versement achète la maturité qui arrive à échéance l'année du départ, et rien
d'autre (:func:`repartition`). Les taux sont ceux de la courbe et de ses
forwards (:class:`~retraite_notionnelle.donnees.taux.CourbeTauxSansRisque`).

C'est un changement de doctrine, et il faut dire contre quoi. Le pilier
pratiquait jusqu'en septembre 2026 une échelle de trois maturités — 2, 10 et
30 ans — glissant du long vers le court à l'approche du départ, en plafonnant
chaque ligne aux trois quarts du versement : le « glide path » que toute
épargne retraite à échéance affiche. Deux raisons l'ont fait tomber.

**Elle ne servait à rien, au centime près.** Un test l'exige désormais
(``test_sous_les_anticipations_pures_l_echelle_est_sans_effet``) : tant que
les forwards sont pris pour les taux futurs, le capital final ne dépend PAS de
la manière dont les maturités découpent l'horizon. Découper [t, T] en un 30
ans, en trois 10 ans ou en quinze 2 ans accumule exactement
:math:`e^{z(T)T - z(t)t}` dans les trois cas, parce que c'est précisément ce
que l'arbitrage impose au forward. L'échelle était donc un paramètre libre
sans effet : on pouvait l'accorder des heures sans déplacer un euro.

**Elle importait un raisonnement qui ne vaut pas ici.** Raccourcir la maturité
à l'approche du départ « dé-risque » un portefeuille d'ACTIONS, dont le prix
de vente est incertain. Le pilier n'en détient pas : il doit un capital à une
DATE, et l'actif sans risque d'une dette datée est le zéro-coupon qui tombe ce
jour-là. Rouler du court jusqu'au départ n'est pas plus prudent, c'est un pari
répété sur le taux de chaque replacement — un risque de réinvestissement que
la règle créait au lieu de le couvrir, et que le modèle ne chiffrait nulle
part. L'adossement le ramène à zéro tant que la courbe couvre l'horizon.

Les deux raisons pointent dans le même sens, et la seconde donne le chiffre :
dès que la prime de terme n'est plus ignorée
(``Parametres.prime_terme_trente_ans``), bloquer la maturité de l'horizon la
capte une fois pour toutes, là où le roulement la rachète à chaque échéance au
prix du jour. C'est ce que l'allocation vaut, et elle ne vaut que cela.

**3. Ce qu'il coûte.** Quatre frais, aux vraies moyennes du marché du PER
l'année de la bascule : sur chaque versement, sur l'encours chaque année, sur
la réserve de la rente chaque année, sur chaque arrérage. Et ils BAISSENT, par
paliers, comme partout où une épargne retraite obligatoire a mis les gérants en
concurrence ou sous plafond : chaque versement entre au tarif de son année,
qu'il garde et qui ne se rapproche du tarif des nouveaux dépôts qu'à un rythme
réglé (``Parametres.convergence_frais_stock``) ; la rente garde les frais de
l'année où elle est souscrite. Les trajectoires et leurs sources sont dans
``Parametres``.

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

#: Plus longue maturité achetable : le bout de la courbe publiée, trente ans à
#: la BCE. Au-delà, plus rien n'est coté — le taux y est prolongé à plat et
#: déclaré ``estimee`` —, et un titre qu'on ne peut pas acheter ne s'adosse à
#: rien. Un horizon plus long se couvre donc en deux temps, et cette coupure
#: est le SEUL replacement que la règle laisse subsister.
MATURITE_MAXIMALE = 30

#: Fiabilité du barème de frais. Les trois valeurs viennent du rapport annuel
#: de l'Observatoire des produits d'épargne financière, que le dépôt n'a pas su
#: récupérer automatiquement : elles sont SAISIES, et la règle du manifeste
#: plafonne à ``haute`` ce qui n'a pas été confronté au document du producteur.
#: Elle qualifie donc tout résultat du pilier, comme n'importe quelle série.
FIABILITE_FRAIS = Fiabilite.HAUTE


def repartition(horizon: int) -> tuple[tuple[int, float], ...]:
    """Maturités et poids d'un versement placé à ``horizon`` années du départ.

    Une seule ligne, et c'est tout le propos : la maturité de l'horizon,
    plafonnée à ce que la courbe cote. Un versement à dix-sept ans du départ
    achète du dix-sept ans ; à quarante ans du départ, il achète le trente ans
    du bout de courbe, et les dix années qui restent seront couvertes à
    l'échéance, par un dix ans, quand la courbe les cotera.

    Deux propriétés la ferment, et un test tient chacune. **Aucune maturité ne
    dépasse l'horizon** : un titre arrivant à échéance après le départ devrait
    être vendu avant terme, donc à un prix qui n'est plus sans risque.
    **Aucune ligne n'arrive à échéance avant le départ** tant que la courbe
    couvre l'horizon : il n'y a alors rien à replacer, donc aucun taux futur à
    deviner. C'est la définition même de l'adossement, et c'est ce qui manquait
    à l'échelle de maturités qui la précédait — voir le docstring du module.

    La maturité rendue est un ENTIER de la courbe publiée, comme avant : les
    trente maturités de la BCE sont toutes cotées, et l'adossement ne demande
    donc ni interpolation ni extrapolation en deçà de trente ans.
    """
    if horizon <= 0:
        return ()
    return ((min(horizon, MATURITE_MAXIMALE), 1.0),)


@dataclass
class _Ligne:
    """Une ligne de l'échelle : un montant placé jusqu'à une année donnée."""

    montant: float
    #: Dernière année où la ligne porte intérêt. Elle est replacée au début de
    #: l'année suivante.
    annee_fin: int
    taux: float
    #: Frais de gestion de la COHORTE dont la ligne vient : le tarif de l'année
    #: du versement, que la ligne garde à chaque replacement et qui ne se
    #: rapproche du tarif des nouveaux dépôts qu'au rythme de
    #: ``convergence_frais_stock``. C'est ce qui fait que la baisse des frais
    #: porte d'abord sur les nouveaux dépôts, et seulement un peu sur le stock.
    frais_gestion: float = 0.0


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
    #: Taux du frais sur versement appliqué au versement de l'année.
    taux_frais_versement: float = 0.0
    #: Taux moyen du frais de gestion prélevé sur l'encours de l'année : la
    #: moyenne des tarifs des cohortes, pondérée par leurs encours.
    taux_frais_gestion: float = 0.0

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
    #: Taux effectivement prélevé, les deux cotisations réunies.
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

    #: Part de :attr:`taux_cotisation` qui vient de la cotisation VOLONTAIRE —
    #: les cinq points que la proposition rend et que l'assuré choisit de
    #: remettre au compte. Zéro quand on la retire.
    taux_cotisation_volontaire: float = 0.0

    #: Frais annuel prélevé sur la RÉSERVE qui porte la rente, l'année de la
    #: liquidation, et facteur par lequel il réduit la rente : à taux technique
    #: nul, un prélèvement de ``f`` par an sur la réserve équivaut à diviser le
    #: capital par ``Σ p_t (1 − f)^(−t)`` au lieu de ``Σ p_t`` — le rapport des
    #: deux est ce facteur, exactement 1 quand le frais est nul.
    frais_encours_rente: float = 0.0
    facteur_encours_rente: float = 1.0

    @property
    def taux_cotisation_obligatoire(self) -> float:
        """Ce que la proposition impose, les points volontaires retirés."""
        return self.taux_cotisation - self.taux_cotisation_volontaire

    @property
    def part_volontaire(self) -> float:
        """Fraction du pilier qui vient du volontaire, entre 0 et 1.

        Le pilier est exactement proportionnel à son taux — aucun seuil, aucun
        frais forfaitaire —, si bien que cette seule fraction partage le
        capital, la rente et le capital transmis sans qu'il faille les
        recalculer. Le docstring du module dit pourquoi, et un test le vérifie.
        """
        if self.taux_cotisation <= 0:
            return 0.0
        return self.taux_cotisation_volontaire / self.taux_cotisation

    @property
    def capital_volontaire(self) -> float:
        return self.capital * self.part_volontaire

    @property
    def capital_obligatoire(self) -> float:
        return self.capital - self.capital_volontaire

    @property
    def rente_volontaire(self) -> float:
        """La part de la rente qui vient des cinq points rendus puis remis."""
        return self.rente_annuelle * self.part_volontaire

    @property
    def rente_volontaire_mensuelle(self) -> float:
        return self.rente_volontaire / 12.0

    @property
    def rente_obligatoire(self) -> float:
        return self.rente_annuelle - self.rente_volontaire

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
               lignes: list[_Ligne], frais_gestion: float = 0.0
               ) -> tuple[tuple[int, float], ...]:
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
            lignes.append(_Ligne(montant=montant, annee_fin=annee, taux=0.0,
                                 frais_gestion=frais_gestion))
            return ()
        detail: list[tuple[int, float]] = []
        for maturite, poids in repartition(horizon):
            part = montant * poids
            if part <= 0:
                continue
            taux = self.courbe.placement(annee, maturite)
            lignes.append(
                _Ligne(montant=part, annee_fin=annee + maturite, taux=taux.taux,
                       frais_gestion=frais_gestion)
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
        parametres = self.parametres
        taux_cotisation = parametres.taux_capitalisation_applique
        convergence = min(1.0, max(0.0, parametres.convergence_frais_stock))

        def frais(poste: str, annee: int) -> float:
            return parametres.frais_capitalisation(poste, annee) if avec_frais else 0.0

        lignes: list[_Ligne] = []
        annees: list[AnneeCapitalisation] = []

        for annee in range(annee_ouverture, annee_liquidation + 1):
            ouverture = sum(l.montant for l in lignes)
            frais_versement = frais("versement", annee)
            frais_neuf = frais("gestion", annee)

            # 0. Le tarif des cohortes déjà placées se rapproche de celui des
            #    nouveaux dépôts, d'une fraction de l'écart par an : c'est la
            #    part de la baisse qui atteint le stock.
            for ligne in lignes:
                ligne.frais_gestion += convergence * (frais_neuf - ligne.frais_gestion)

            # 1. Intérêts de l'année, ligne par ligne, au taux bloqué le jour
            #    du placement. C'est ce que « porter jusqu'à l'échéance » veut
            #    dire : le taux d'une ligne ne change plus.
            interets = sum(l.montant * l.taux for l in lignes)
            for ligne in lignes:
                ligne.montant *= 1.0 + ligne.taux

            # 2. Frais de gestion, prélevés sur l'encours de fin d'année, ligne
            #    par ligne au tarif de sa cohorte. Le versement de l'année n'y
            #    est pas encore : il n'a pas passé l'année dans l'enveloppe.
            prelevement = sum(l.montant * l.frais_gestion for l in lignes)
            for ligne in lignes:
                ligne.montant *= 1.0 - ligne.frais_gestion
            assiette_frais = ouverture + interets
            taux_gestion = (prelevement / assiette_frais) if assiette_frais > 0 else frais_neuf

            # 3. Échéances : ce qui arrive à terme est replacé pour ce qu'il
            #    reste d'horizon, cohorte par cohorte, chacune gardant son tarif.
            echues: dict[float, float] = {}
            for ligne in lignes:
                if ligne.annee_fin == annee:
                    echues[ligne.frais_gestion] = echues.get(ligne.frais_gestion, 0.0) + ligne.montant
            lignes = [l for l in lignes if l.annee_fin != annee]
            for tarif, montant in echues.items():
                self.placer(montant, annee, annee_liquidation, lignes, tarif)

            # 4. Versement de l'année, crédité en fin d'année, au tarif de
            #    l'année.
            assiette = assiettes.get(annee, 0.0)
            brut = assiette * taux_cotisation
            frais_v = brut * frais_versement
            net = brut - frais_v
            placements = self.placer(net, annee, annee_liquidation, lignes, frais_neuf)

            encours = sum(l.montant for l in lignes)
            annees.append(AnneeCapitalisation(
                annee=annee,
                age=annee - annee_naissance,
                horizon=annee_liquidation - annee,
                assiette=assiette,
                versement_brut=brut,
                frais_versement=frais_v,
                versement_net=net,
                encours_ouverture=ouverture,
                interets=interets,
                frais_gestion=prelevement,
                encours=encours,
                taux_moyen=(interets / ouverture) if ouverture > 0 else 0.0,
                placements=placements,
                taux_frais_versement=frais_versement,
                taux_frais_gestion=taux_gestion,
            ))
        return annees

    # -- transmission --------------------------------------------------------

    def _transmission(self, annees: list[AnneeCapitalisation], age_ouverture: float,
                      annee_ouverture: int, sexe: str | None,
                      population: str | None = None) -> tuple[float, float]:
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
            self.parametres.table_generation, population,
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

    def _facteur_encours_rente(self, frais: float, age_liquidation: float,
                               annee_liquidation: int, sexe: str | None,
                               population: str | None) -> float:
        """Ce qu'un frais annuel sur la réserve de la rente lui retire.

        La rente est nivelée et le taux technique nul : la réserve qui la
        porte est ``R × Σ p_t``. Prélever ``f`` par an sur cette réserve
        revient à actualiser au taux ``−f``, donc à diviser le capital par
        ``Σ p_t (1 − f)^(−t)``. Le facteur rendu est le rapport de l'ancien
        diviseur au nouveau, calculé sur la courbe de survie du modèle à la
        liquidation ; il vaut exactement 1 sans frais, et il est appliqué au
        diviseur de la conversion plutôt que substitué à lui, pour que la
        rente reste comparable au centime à la pension notionnelle.
        """
        if frais <= 0:
            return 1.0
        courbe = self.mortalite.courbe(
            age_liquidation, float(annee_liquidation), sexe,
            self.parametres.table_generation, population,
        )
        sans = sum(courbe)
        avec = sum(p / (1.0 - frais) ** t for t, p in enumerate(courbe))
        return sans / avec if avec > 0 else 1.0

    # -- assemblage ----------------------------------------------------------

    def construire(self, assiettes: dict[int, float], annee_naissance: int,
                   age_liquidation: float, annee_liquidation: int,
                   mois_liquidation: int = 1, sexe: str | None = None,
                   population: str | None = None) -> Capitalisation:
        """Le pilier d'une carrière, de son ouverture à sa rente.

        ``assiettes`` porte, année par année, l'assiette sur laquelle la
        cotisation notionnelle a été prélevée : le pilier s'appuie sur elle et
        n'en construit pas une autre.

        IL S'OUVRE À LA BASCULE, celle que la simulation a choisie. Il
        s'ouvrait jusqu'au 23 septembre 2026 à une date à lui, figée à 2026 :
        une bascule en 2040 lui laissait quatorze années de plus, prélevées
        sur l'assiette d'AVANT la bascule — la somme des assiettes des
        régimes, qui compte deux fois la première tranche d'un salarié du
        privé, régime général et Agirc-Arrco. Un cadre au salaire moyen né en
        1990 y gagnait 15 318 € de rente annuelle, contre 10 338 € sous une
        bascule en 2026 et 5 357 € sous la sienne.
        """
        bascule = self.parametres.annee_bascule
        ouverture = max(bascule, min(assiettes) if assiettes else bascule)
        conversion = self.convertisseur.coefficient(
            age_liquidation, annee_liquidation,
            None if self.parametres.table_conversion is TableConversion.UNISEXE else sexe,
            mois_liquidation, population,
        )

        # Le pilier s'éteint quand il n'a plus rien à encaisser : ni les cinq
        # points obligatoires, ni les cinq points volontaires. Retirer l'un
        # laisse l'autre debout — c'est tout l'intérêt de les avoir séparés.
        if (annee_liquidation < ouverture
                or self.parametres.taux_capitalisation_applique <= 0):
            return Capitalisation(
                annee_ouverture=ouverture,
                annee_liquidation=annee_liquidation,
                taux_cotisation=self.parametres.taux_capitalisation_applique,
                taux_cotisation_volontaire=(
                    self.parametres.taux_capitalisation_volontaire_applique),
                annees=(),
                capital=0.0,
                capital_hors_frais=0.0,
                conversion=conversion,
                frais_arrerages=self.parametres.frais_capitalisation("arrerages", annee_liquidation),
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

        # La rente du PER : capital divisé par le diviseur actuariel, réduit
        # de ce que le frais annuel sur la réserve lui retire, puis amputé des
        # frais sur arrérages, qui sont prélevés sur chaque versement de rente
        # et non sur le capital qui la constitue. Les deux tarifs sont ceux de
        # l'année de la liquidation : la rente est un contrat, elle garde les
        # frais du jour où elle est souscrite.
        sexe_table = (None if self.parametres.table_conversion is TableConversion.UNISEXE
                      else sexe)
        frais_arrerages = self.parametres.frais_capitalisation("arrerages", annee_liquidation)
        frais_encours_rente = self.parametres.frais_capitalisation(
            "encours_rente", annee_liquidation)
        facteur = self._facteur_encours_rente(
            frais_encours_rente, age_liquidation, annee_liquidation, sexe_table, population)
        rente = capital / conversion.diviseur * facteur * (1.0 - frais_arrerages)

        deces, transmis = self._transmission(
            annees, ouverture - annee_naissance, ouverture, sexe_table, population,
        )

        return Capitalisation(
            annee_ouverture=ouverture,
            annee_liquidation=annee_liquidation,
            taux_cotisation=self.parametres.taux_capitalisation_applique,
            taux_cotisation_volontaire=(
                self.parametres.taux_capitalisation_volontaire_applique),
            annees=tuple(annees),
            capital=capital,
            capital_hors_frais=sans_frais[-1].encours if sans_frais else 0.0,
            conversion=conversion,
            frais_arrerages=frais_arrerages,
            frais_encours_rente=frais_encours_rente,
            facteur_encours_rente=facteur,
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
