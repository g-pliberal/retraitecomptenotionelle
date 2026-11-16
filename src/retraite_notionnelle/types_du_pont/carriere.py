"""L'année de carrière que le pont échange (action 161, étape 1 du retrait des
règles Python), que ``carriere.py`` réimporte le temps du retrait. ``Carriere``,
qui porte encore des méthodes de règle, sortira à une étape à elle.
"""

from __future__ import annotations

from dataclasses import dataclass



@dataclass(frozen=True)
class AnneeCarriere:
    """Une année de carrière."""

    annee: int
    #: Revenu d'activité brut de l'année, EN EUROS COURANTS DE CETTE ANNÉE-LÀ.
    revenu: float
    #: Statut d'affiliation (clé de ``legislation/affiliations.yaml``).
    affiliation: str
    #: Nature de la période.
    type_periode: str = "emploi"
    #: Quotité travaillée (1.0 = temps plein) : celle des mois de retraite
    #: progressive, en moyenne sur l'année. Les services de la fonction
    #: publique la comptent pour leur durée réelle, et le traitement de
    #: référence se lit à temps plein (``droit/progressive.py``).
    quotite: float = 1.0
    #: Trimestres validés au sens du système ACTUEL (utilisé par le seul
    #: scénario « système actuel »).
    trimestres_valides: int = 4
    #: Des cotisations retraite ont-elles réellement été versées ?
    #: C'est le seul critère qui compte pour les comptes notionnels.
    cotisations_versees: bool = True
    #: Salaire de référence d'avant l'interruption. Les régimes
    #: complémentaires attribuent des points sur cette base pendant les
    #: périodes indemnisées : payés par l'Unédic pour le chômage, attribués
    #: « sans contrepartie de cotisations » pour la maladie, la maternité,
    #: l'invalidité et l'accident du travail.
    revenu_reference: float = 0.0
    #: Familles de régimes qui attribuent des points sur ``revenu_reference``
    #: alors que l'année n'est pas travaillée : ce que le scénario 1 sert.
    familles_cotisantes: tuple[str, ...] = ()
    #: Celles d'entre elles qui ENCAISSENT de vraies cotisations pendant
    #: l'année, versées par un tiers : l'Agirc-Arrco pendant un chômage
    #: indemnisé, que l'Unédic paie. C'est ce que le compte notionnel porte,
    #: lui qui ne porte que ce qui a été versé. Vide pour la maladie : ses
    #: points sont gratuits, et le compte les portait comme payés jusqu'au
    #: 23 septembre 2026.
    familles_financees: tuple[str, ...] = ()
    #: Part de primes dans le revenu (fonction publique) : assiette du RAFP.
    part_primes: float = 0.0
    #: Part de l'année civile réellement couverte par la carrière. Vaut un
    #: partout, sauf aux deux bords : l'année d'entrée dans la vie active et
    #: celle de la liquidation sont incomplètes, et ``revenu`` ne porte alors
    #: que ce qui a été perçu pendant ces mois-là. Le plafond de la Sécurité
    #: sociale se proratise sur cette même fraction, comme le veut l'article
    #: R. 242-2 : une demi-année de travail n'ouvre qu'un demi-plafond.
    fraction_annee: float = 1.0
    #: Salaire forfaitaire porté au compte du régime de base au titre de
    #: l'assurance vieillesse des parents au foyer. Ce n'est pas un revenu
    #: d'activité — l'année n'est pas cotisée par l'assuré — mais la CNAF
    #: cotise pour lui sur cette assiette, et le salaire entre dans le salaire
    #: annuel moyen. Une période assimilée, elle, n'y entre jamais.
    revenu_avpf: float = 0.0
    #: ASSIETTE MINIMALE du régime de base d'un indépendant, en euros de
    #: l'année : l'artisan, le commerçant ou le libéral qui déclare moins
    #: cotise quand même sur ce montant (D. 633-2, D. 642-4), qui valide ses
    #: trimestres et entre dans son salaire annuel moyen ou ses points. Nulle
    #: pour tout autre statut. Voir `legislation/assiette_minimale_independants.csv`.
    assiette_minimale_base: float = 0.0
    #: Le motif qui DISPENSE la ligne de l'assiette minimale, quand le texte
    #: l'en dispense cette année-là (L. 613-11, D. 642-4 ;
    #: ``legislation/dispenses_assiette_minimale.yaml``) : le RSA, la prime
    #: d'activité, l'activité accessoire saisonnière… Vide sinon.
    #: ``assiette_minimale_base`` est alors nulle, et celle des complémentaires
    #: des libéraux tombe aussi quand le motif les couvre.
    dispense_assiette_minimale: str = ""
    #: Le barème de la Lodeom de l'employeur d'outre-mer, que la fiche de paie
    #: met à la place de la réduction générale (L. 752-3-2) ; vide sinon, et
    #: sur une année non cotisée. Il ne change aucun droit.
    lodeom: str = ""
    #: Le DÉPARTEMENT D'OUTRE-MER où l'assuré a travaillé dans l'année — une
    #: clef de :data:`~retraite_notionnelle.donnees.macro.DEPARTEMENTS_D_OUTRE_MER` —,
    #: qui donne à ses trimestres leur seuil (R. 753-21, R. 351-9) ; vide en
    #: métropole, et sur une année non cotisée.
    outre_mer: str = ""
    #: Cette année entre-t-elle dans les SERVICES d'un régime de la fonction
    #: publique ? Ce régime-là ne proratise pas sur la durée d'assurance mais
    #: sur les services et bonifications (L. 13 du code des pensions), et
    #: l'article L. 9 écarte le temps passé dans une position statutaire sans
    #: services effectifs, hors la liste qu'il énumère. Une année d'emploi en
    #: est toujours ; une année de chômage n'en est jamais — un fonctionnaire
    #: au chômage n'est d'ailleurs plus fonctionnaire.
    services_fonction_publique: bool = True
    #: Limite, en trimestres PAR ENFANT, des services que cette année ouvre.
    #: Zéro quand il n'y en a pas. Le 1° de L. 9 excepte le congé parental
    #: « dans la limite de trois ans par enfant » : le décompte se fait donc
    #: sur toute la carrière, pas année par année, et c'est le scénario qui
    #: tient le budget.
    services_plafond_trimestres_par_enfant: int = 0
    #: Nature de cette année au sens de l'article D. 351-1-2, qui la RÉPUTE
    #: COTISÉE pour la carrière longue sous la limite que sa rédaction à la
    #: date d'effet fixe (:class:`~retraite_notionnelle.scenarios.actuel.CarriereLongue`).
    #: Vide : jamais réputée cotisée.
    reputes_cotises_nature: str = ""
    #: Salaire porté au compte du régime général quand l'année est RÉTABLIE :
    #: celle d'un fonctionnaire parti sans droit à pension, que L. 65 du code
    #: des pensions rétablit au régime général et à l'Ircantec. C'est le
    #: dernier traitement soumis à retenue, sur la fraction de l'année
    #: (D. 173-16) ; le plafond de l'année s'applique ensuite. Zéro pour toute
    #: autre année : seul le scénario 1 le renseigne, sur sa propre copie de
    #: la carrière (voir `droit.coordonner.retablir`).
    revenu_retabli: float = 0.0
    #: Les jours de services que le RELEVÉ porte pour l'année : ses trimestres,
    #: fractions comprises, à quatre-vingt-dix jours le trimestre. Le code des
    #: pensions compte ses services au jour et ne les arrondit qu'au décompte
    #: final (R. 26) : « 3.33 » dit dix mois. ``None`` hors d'un relevé qui
    #: les déclare : les mois de la ligne font alors ses jours
    #: (:func:`~retraite_notionnelle.droit.compter.jours_de_la_ligne`).
    jours_de_services: int | None = None
    #: L'activité du MICRO-ENTREPRENEUR dont la ligne lit le revenu abattu
    #: (``saisie.ACTIVITES_MICRO``) ; vide hors du micro-social. Ses trimestres
    #: se valident sur le revenu que sa cotisation achète, non sur le revenu
    #: abattu (``legislation/micro_social.yaml``), et ce revenu cotisé est celui
    #: de son revenu annuel moyen (:func:`revenu_cotise`) ; l'assiette minimale
    #: ne le touche pas.
    micro: str = ""
    #: La ligne d'un CONJOINT COLLABORATEUR cotise-t-elle sur le forfait du
    #: tiers du plafond, faute d'assiette saisie (D. 633-19-2, 1° ;
    #: :func:`assiette_du_conjoint_collaborateur`) ? Sa complémentaire n'est
    #: assise sur l'avant-dernière année qu'à l'option, une fraction du revenu
    #: du chef (D. 635-10-2 ; :func:`~retraite_notionnelle.droit.acquerir.revenu_a_l_option`).
    forfait_conjoint: bool = False
    #: La ligne d'une activité que l'assuré déclare CUMULÉE à l'activité
    #: principale de l'année (:attr:`Metier.cumul`), que bâtit
    #: :func:`_lignes_du_parcours` ; faux pour l'activité principale, et sur un
    #: relevé, qui ne le dit pas : ce que la caisse y a reporté fait foi.
    cumulee: bool = False
    #: L'ACTIVITÉ ACCESSOIRE DE L'AGENT D'UN RÉGIME SPÉCIAL, de 1981 à 2014 :
    #: elle n'ouvre aucun droit au régime général (D. 171-4, rédaction du
    #: 21 décembre 1985). Faux partout ailleurs : seul le scénario 1 la marque,
    #: sur sa propre copie de la carrière
    #: (:func:`~retraite_notionnelle.droit.coordonner.ecarter_les_accessoires`).
    accessoire_d_un_regime_special: bool = False

    @property
    def cotise(self) -> bool:
        return self.cotisations_versees and self.revenu > 0

    @property
    def revenu_annualise(self) -> float:
        """Revenu ramené à l'année pleine.

        C'est le traitement en vigueur, celui que liquident les régimes servant
        sur le dernier traitement ou les six derniers mois de service — et non
        la somme réellement perçue pendant une année tronquée.
        """
        if self.fraction_annee <= 0:
            return 0.0
        return self.revenu / self.fraction_annee
