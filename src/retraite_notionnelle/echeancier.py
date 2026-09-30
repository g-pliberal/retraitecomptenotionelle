"""L'échéancier (docs/architecture.md, § 7.4).

Il parcourt les ÉVÉNEMENTS dans l'ordre des dates, et ceux d'une même date
dans l'ordre de leur rang. Aux événements qui ouvrent, révisent ou
transforment un droit, il appelle ``liquider`` : le vocabulaire dit, pour
chaque sorte, si elle l'appelle, et avec quel motif et quelle nature
(``sortes_d_evenement``) ; la demande se construit à partir de l'événement.
Puis, après les liquidations du jour, et à l'échéance qu'on lui demande, il
applique les deux étapes qui ne liquident rien : « faire vivre »
(:func:`~retraite_notionnelle.revalorisation.faire_vivre`) et « foyer et
net » (:func:`~retraite_notionnelle.droit.foyer.foyer_et_net`).

Tout ce qu'il calcule s'inscrit au JOURNAL (:mod:`.journal`), qui est
l'état : on y ajoute, on n'efface jamais, et chaque entrée porte son
inscription et son effet. Une composante revalorisée remplace, dans sa
lignée, celle que la liquidation avait écrite.

Aujourd'hui, le départ, tiré de la carrière — un par date quand les régimes
ne liquident pas tous ensemble (:mod:`.droit.departs`) —, et, quand la
chronologie les dit, le décès de l'assuré et la réversion qu'il ouvre à son
conjoint (:mod:`.droit.reversion`) : les autres sortes sont réservées
(§ 13.5). Un
conjoint sans décès déclaré reçoit une réversion d'essai, pour un décès
supposé juste après le départ, qui ne s'inscrit pas au journal.
L'échéance est l'année courante, et « faire vivre » y applique d'un coup les
revalorisations publiées depuis le départ, dans l'ordre où
:mod:`~retraite_notionnelle.revalorisation` les compose : une revalorisation
par date, que chaque fiche inscrirait à la sienne, changerait l'ordre des
produits, donc les derniers chiffres des pensions. Elle viendra avec les
fiches.

Chaque événement suit le contrat C.7 (``data/reference/contrats/evenement.yaml``).
Son jumeau est ``moteur/js/echeancier.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from . import chronologie as chrono
from .droit import cumul as _cumul
from .droit import departs as _departs
from .droit import foyer as _foyer
from .droit import liquidation as _liquidation
from .droit import progressive as _progressive
from .droit import reversion as _reversion
from .droit import seconde as _seconde
from .droit.commun import date_d_effet
from .journal import Entree, Journal
from .noyau import vocabulaire
from .revalorisation import aujourd_hui, faire_vivre, foyer_a_l_echeance
from .scenarios.actuel import (MinimumVieillesse, etat_du_depart, progressive_servie,
                               resultat_actuel, resultat_des_departs)

if TYPE_CHECKING:
    from .carriere import Carriere
    from .donnees.chargement import Fiabilite
    from .revalorisation import ActuelAujourdhui
    from .scenarios.actuel import ResultatActuel
    from .simulateur import Simulateur

#: La version du contrat C.7 que :meth:`Evenement.donnees` suit.
SCHEMA_VERSION = 1

#: Ce que chaque sorte d'événement appelle : ``liquider``, avec quel motif et
#: quelle nature (vocabulaire, liste ``sortes_d_evenement``).
SORTES = {nom: dict(sorte) for nom, sorte in
          vocabulaire.valeurs()["listes"]["sortes_d_evenement"]["valeurs"].items()}


@dataclass(frozen=True)
class Evenement:
    """Un événement (contrat C.7)."""

    id: str
    #: Sa date (AAAA-MM-JJ).
    date: str
    #: Les personnes concernées.
    personnes: tuple[str, ...]
    #: Ce qu'il vise : un régime, une liquidation, une allocation.
    vise: dict
    sorte: str = "depart"
    #: ``acte``, ``simule``, ``observe``, ``induit`` ou ``publication``.
    origine: str = "acte"
    condition: object | None = None
    #: L'ordre dans la journée.
    rang: int = 0

    def donnees(self) -> dict:
        """L'événement, tel que le contrat C.7 le décrit."""
        donnee = {"schema_version": SCHEMA_VERSION, "id": self.id, "date": self.date,
                  "sorte": self.sorte, "personnes": list(self.personnes),
                  "vise": self.vise, "origine": self.origine, "rang": self.rang}
        if self.condition is not None:
            donnee["condition"] = self.condition
        return donnee


def depart_de(carriere: Carriere) -> Evenement | None:
    """Le départ que la carrière déclare, à sa date d'effet : un acte de la
    personne, ou le choix du pilote quand la chronologie le dit simulé."""
    date = date_d_effet(carriere)
    if date is None:
        return None
    fait = (chrono.depart(carriere.chronologie, carriere.personne)
            if carriere.chronologie else None)
    origine = "simule" if fait is not None and fait.get("origine") == "simule" else "acte"
    return Evenement(id=f"depart_{carriere.personne}", date=date,
                     personnes=(carriere.personne,), vise={"regimes": "tous"},
                     origine=origine)


class Echeancier:
    """L'échéancier du droit réel, pour une personne."""

    def __init__(self, simulateur: Simulateur) -> None:
        self.simulateur = simulateur
        self.moteur = simulateur.scenario_actuel
        self.journal = Journal()
        #: Le scénario 1 à la date d'effet du départ : la liquidation, puis
        #: l'ASPA de ce jour-là.
        self.au_depart: ResultatActuel | None = None
        #: Le scénario 1 à l'échéance : ce que le droit sert l'année courante.
        self.aujourd_hui: ActuelAujourdhui | None = None
        #: La réversion que le décès de l'assuré ouvre à son conjoint, quand la
        #: chronologie les dit.
        self.reversion: _reversion.Reversion | None = None
        #: La retraite progressive que la carrière demande, sa liquidation
        #: provisoire, et, ouverte, le plancher que les départs gardent.
        self.progressive: _progressive.Progressive | None = None
        self.provisoire = None
        self.plancher: tuple | None = None
        #: Les composantes servies par la retraite progressive, que celles de
        #: la pension complète remplacent dans leur lignée.
        self._progressives: dict[str, str] = {}

    def parcourir(self, carriere: Carriere, echeance: int | None = None) -> Journal:
        """Les événements de ``carriere``, dans l'ordre, puis, s'il y en a une,
        l'échéance ``echeance`` (une année), à laquelle les pensions liquidées
        sont menées. Une retraite progressive vient d'abord ; le départ qui
        la suit est celui de la pension définitive."""
        self._progresser(carriere)
        departs = _departs.departs(self.moteur, carriere)
        if len(departs) > 1:
            self._partir(carriere, departs)
        else:
            evenements = [e for e in (depart_de(carriere),) if e is not None]
            if self.plancher is not None:
                evenements = [replace(e, sorte="pension_definitive") for e in evenements]
            for evenement in sorted(evenements, key=lambda e: (e.date, e.rang)):
                self._traiter(evenement, carriere)
        if self.au_depart is not None and self.progressive is not None:
            self.au_depart = replace(self.au_depart, retraite_progressive=progressive_servie(
                self.progressive, self.provisoire, carriere.date_liquidation))
        if self.au_depart is not None and carriere.conjoint is not None:
            if carriere.deces is not None:
                self._reverser(carriere)
            else:
                self._reverser_a_l_essai(carriere)
        if echeance is not None and self.au_depart is not None:
            self._echeance(carriere, echeance)
        if self.au_depart is not None and carriere.emploi_retraite is not None:
            self._cumuler(carriere)
            self._constituer(carriere)
        return self.journal

    def _constituer(self, carriere: Carriere) -> None:
        """Les droits de l'activité exercée après le départ
        (:mod:`.droit.seconde`) : éteints, ou constitués en une nouvelle
        pension, inscrite à sa date d'effet dans une lignée à elle."""
        droits = _seconde.droits(self.moteur, carriere, self.au_depart, self.au_depart.cumul)
        self.au_depart = replace(self.au_depart, droits_apres_depart=droits)
        pensions = [p for p in droits.pensions if p.montant > 0]
        if not pensions:
            return
        date = _cumul.jour(pensions[0].date_effet)
        evenement = Evenement(
            id=f"seconde_pension_{carriere.personne}", date=date,
            personnes=(carriere.personne,),
            vise={"regimes": [p.regime for p in pensions]}, sorte="seconde_pension")
        self._inscrire(evenement, evenement.id, "evenement", evenement, date)
        for pension in pensions:
            ident = f"seconde_{pension.regime}"
            detail = (f"nouvelle pension, {pension.trimestres} trimestres sur "
                      f"{pension.salaire_mensuel:,.2f} € par mois"
                      if pension.points == 0 else
                      f"seconde retraite complémentaire, {pension.points:,.2f} points")
            self._inscrire(evenement, ident, "composante", {
                "id": ident, "beneficiaire": carriere.personne, "regime": pension.regime,
                "montant": {"annuel": pension.montant, "monnaie": "EUR"}, "debut": date,
                "detail": detail}, date)

    def _cumuler(self, carriere: Carriere) -> None:
        """L'activité exercée après le départ (:mod:`.droit.cumul`) : ce que
        chaque pension en garde, mois par mois, que le résultat du départ porte.
        Une pension réduite, suspendue ou non due s'inscrit pour les mois où
        elle l'est, dans sa lignée : ce qui est servi pendant ces mois-là, et
        seulement eux. Les pensions y sont celles que « faire vivre » mène à
        chaque année de l'activité."""
        def pensions_de(annee: int) -> tuple[dict, float]:
            vivante = faire_vivre(self.simulateur, carriere, self.au_depart, annee)
            return ({r.regime: r.aujourd_hui for r in vivante.regimes},
                    vivante.majoration_enfants * vivante.coefficient_majoration)

        cumul = _cumul.cumuler(self.moteur, carriere, self.au_depart, pensions_de,
                               self.simulateur.parametres.annee_courante)
        self.au_depart = replace(self.au_depart, cumul=cumul)
        emploi = carriere.emploi_retraite
        debut = Evenement(
            id=f"emploi_retraite_{carriere.personne}", date=_cumul.jour(cumul.debut),
            personnes=(carriere.personne,),
            vise={"periode": "emploi_retraite", "affiliation": emploi["affiliation"],
                  "employeur": emploi["employeur"]},
            sorte="debut_de_periode")
        self._inscrire(debut, debut.id, "evenement", debut, debut.date)
        for tranche in cumul.tranches:
            depuis, jusqu_a = _cumul.jour(tranche.debut), _cumul.jour(tranche.fin)
            for pension in tranche.par_regime:
                if pension.reduction <= 0:
                    continue
                ident = f"cumul_{pension.regime}_{depuis}"
                self.journal.inscrire(Entree(
                    ident, debut.id, debut.date, depuis, jusqu_a, "composante",
                    {"id": ident, "regime": pension.regime,
                     "montant": {"annuel": (pension.montant - pension.reduction) * 12.0,
                                 "monnaie": "EUR"},
                     "debut": depuis, "fin": jusqu_a,
                     "detail": (f"cumul emploi-retraite, {pension.statut} "
                                f"({pension.regle}) : {pension.reduction:,.2f} € par mois "
                                "non servis")},
                    remplace=f"pension_{pension.regime}"))
        fin = Evenement(
            id=f"fin_emploi_retraite_{carriere.personne}", date=_cumul.jour(cumul.fin),
            personnes=(carriere.personne,), vise={"periode": "emploi_retraite"},
            sorte="fin_de_periode")
        self._inscrire(fin, fin.id, "evenement", fin, fin.date)

    def _reverser(self, carriere: Carriere) -> None:
        """Le décès de l'assuré, puis la réversion qu'il ouvre à son conjoint,
        dans les régimes de sa liquidation (§ 7.3) : sa pension y est menée
        jusqu'à l'année du décès — l'année courante pour un décès à venir, où
        s'arrêtent les revalorisations publiées ; jamais avant le départ, dont
        les montants sont les euros."""
        deces = Evenement(id=f"deces_{carriere.personne}", date=carriere.deces,
                          personnes=(carriere.personne,), vise={}, sorte="deces")
        self._inscrire(deces, deces.id, "evenement", deces, deces.date)
        annee, pensions = self._pensions_au_deces(carriere, carriere.deces)
        self.reversion = _reversion.reversion(self.moteur, pensions, carriere, annee)
        survivant = carriere.conjoint.personne
        evenement = Evenement(id=f"reversion_{survivant}", date=_reversion.mois_suivant(
            carriere.deces), personnes=(survivant,), vise={"regimes": "du défunt"},
            sorte="reversion")
        self._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date)
        self._inscrire(evenement, f"liquidation_{evenement.id}", "reversion",
                       self.reversion, evenement.date)

    def _reverser_a_l_essai(self, carriere: Carriere) -> None:
        """Sans décès déclaré, la réversion d'un décès supposé juste après le
        départ, ou au 1er janvier de l'année courante pour qui est déjà parti
        (présomption ``deces_apres_le_depart``) : ce que le conjoint
        recevrait. Elle ne s'inscrit pas au journal, qui ne tient que ce qui
        arrive."""
        depart = (f"{carriere.date_liquidation.annee:04d}"
                  f"-{carriere.date_liquidation.mois:02d}-01")
        deces = max(depart, f"{self.simulateur.parametres.annee_courante:04d}-01-01")
        annee, pensions = self._pensions_au_deces(carriere, deces)
        self.reversion = _reversion.reversion(self.moteur, pensions, carriere, annee,
                                              deces_suppose=deces)

    def _pensions_au_deces(self, carriere: Carriere,
                           deces: str) -> tuple[int, list[tuple[str, float, Fiabilite]]]:
        """Les pensions du défunt menées à l'année du décès — l'année courante
        pour un décès à venir, où s'arrêtent les revalorisations publiées ;
        jamais avant le départ, dont les montants sont les euros —, et cette
        année."""
        annee = max(carriere.annee_liquidation,
                    min(int(deces[:4]), self.simulateur.parametres.annee_courante))
        vivante = faire_vivre(self.simulateur, carriere, self.au_depart, annee)
        servies = [(r.regime, r.au_depart * r.coefficient, r.fiabilite)
                   for r in vivante.regimes]
        # Une pension qu'un régime ne sert pas encore au décès est celle que le
        # défunt « eût obtenue » : la réversion la lit, au montant du départ
        # déclaré (:mod:`.droit.departs`).
        vues = {regime for regime, _, _ in servies}
        return annee, servies + [(p.regime, p.montant, p.fiabilite)
                                 for p in self.au_depart.pensions_par_regime
                                 if p.regime not in vues]

    def _progresser(self, carriere: Carriere) -> None:
        """La retraite progressive que la carrière demande : examinée, et,
        ouverte, liquidée à titre provisoire et inscrite, chaque composante
        pour la fraction qu'elle sert (:mod:`.droit.progressive`)."""
        progressive = _progressive.examiner(self.moteur, carriere)
        self.progressive = progressive
        if progressive is None or not progressive.ouverte:
            return
        contexte = _liquidation.Contexte(self.moteur)
        provisoire = _progressive.liquider(self.moteur, carriere, contexte, progressive,
                                           self.journal)
        progressive = _progressive.avec_la_duree(progressive, provisoire)
        self.progressive, self.provisoire = progressive, provisoire
        if not progressive.ouverte:
            return
        self.plancher = (progressive, provisoire)
        evenement = Evenement(
            id=f"retraite_progressive_{carriere.personne}", date=progressive.date_effet,
            personnes=(carriere.personne,), vise={"regimes": sorted(progressive.regimes)},
            sorte="retraite_progressive")
        self._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date)
        self._inscrire(evenement, f"liquidation_{evenement.id}", "liquidation", provisoire,
                       evenement.date)
        pourcent = f"{progressive.fraction * 100:.0f}"
        for composante in provisoire.composantes():
            entiere = composante["montant"]["annuel"]
            servie = dict(composante, id=f"progressive_{composante['id']}",
                          montant={"annuel": entiere * progressive.fraction, "monnaie": "EUR"},
                          detail=(f"{composante['detail']} ; retraite progressive : "
                                  f"{pourcent} % de {entiere:,.2f} €"))
            self._inscrire(evenement, servie["id"], "composante", servie, evenement.date)
            cle = ("majoration_enfants" if composante["id"].startswith("majoration_enfants")
                   else composante["id"])
            self._progressives[cle] = servie["id"]

    def _composantes(self, evenement: Evenement, liquidation) -> None:
        """Les composantes d'une liquidation définitive, inscrites : celles
        qu'une retraite progressive servait déjà sont remplacées dans leur
        lignée."""
        for composante in liquidation.composantes():
            cle = ("majoration_enfants" if composante["id"].startswith("majoration_enfants")
                   else composante["id"])
            self._inscrire(evenement, composante["id"], "composante", composante,
                           evenement.date, remplace=self._progressives.pop(cle, None))

    def _traiter(self, evenement: Evenement, carriere: Carriere) -> None:
        sorte = SORTES[evenement.sorte]
        self._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date)
        if not sorte.get("liquider"):
            return
        demande = _liquidation.Demande(
            personne=evenement.personnes[0], date_effet=evenement.date,
            evenement=evenement.sorte, date_evenement=evenement.date,
            motif=sorte.get("motif", "vieillesse"), nature=sorte.get("nature", "definitive"))
        contexte = _liquidation.Contexte(self.moteur)
        liquidation = _liquidation.liquider(
            demande, etat_du_depart(self.moteur, carriere, self.plancher, self.journal),
            contexte)
        liquidee = liquidation.carriere
        foyer = _foyer.foyer_et_net(
            self.moteur, liquidee.personne, evenement.date, liquidee.annee_liquidation,
            liquidation.total,
            (liquidee.age_liquidation or 0.0) >= MinimumVieillesse.AGE_OUVERTURE, contexte)
        self.au_depart = resultat_actuel(liquidation, foyer)
        self._inscrire(evenement, f"liquidation_{evenement.id}", "liquidation", liquidation,
                       evenement.date)
        self._composantes(evenement, liquidation)
        self._inscrire(evenement, f"foyer_{evenement.id}", "foyer", foyer, evenement.date)

    def _partir(self, carriere: Carriere, departs: tuple[_departs.Depart, ...]) -> None:
        """Un départ par date, quand les régimes ne liquident pas tous
        ensemble : chacun liquide ses régimes, en voyant servies les pensions
        des précédents, et s'inscrit au journal ; le scénario 1 du départ
        déclaré les réunit (:func:`~.scenarios.actuel.resultat_des_departs`),
        l'ASPA de ce jour-là comprise."""
        declare = depart_de(carriere)
        contexte = _liquidation.Contexte(self.moteur)
        liquidations = _departs.liquider_les_departs(
            self.moteur, carriere, contexte, liste=departs, journal=self.journal,
            progressive=self.plancher)
        for depart, liquidation in zip(departs, liquidations):
            evenement = Evenement(
                id=f"depart_{carriere.personne}_{depart.date_effet}", date=depart.date_effet,
                personnes=(carriere.personne,), vise={"regimes": sorted(depart.regimes)},
                # Le départ déclaré est un acte ; les autres dates, la
                # présomption depart_de_chaque_regime les induit.
                origine=declare.origine if depart.date_effet == declare.date else "induit")
            self._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date)
            self._inscrire(evenement, f"liquidation_{evenement.id}", "liquidation",
                           liquidation, evenement.date)
            self._composantes(evenement, liquidation)
        self.au_depart = resultat_des_departs(
            self.moteur, carriere, departs, liquidations, contexte)
        foyer = _foyer.foyer_et_net(
            self.moteur, carriere.personne, declare.date, carriere.annee_liquidation,
            sum(p.montant for p in self.au_depart.pensions_par_regime) + sum(
                a.montant for a in self.au_depart.avantages_appliques
                if a.code == "majoration_enfants"),
            (carriere.age_liquidation or 0.0) >= MinimumVieillesse.AGE_OUVERTURE, contexte)
        self._inscrire(declare, f"foyer_{declare.id}", "foyer", foyer, declare.date)

    def _echeance(self, carriere: Carriere, annee: int) -> None:
        """Faire vivre, puis foyer et net, à l'échéance : les composantes
        revalorisées remplacent celles du départ, dans leur lignée."""
        date = f"{annee:04d}-12-31"
        ident = f"echeance_{annee}"
        vivante = faire_vivre(self.simulateur, carriere, self.au_depart, annee)
        foyer = foyer_a_l_echeance(self.simulateur, carriere, vivante)
        self.aujourd_hui = aujourd_hui(vivante, foyer, self.au_depart)
        self.journal.inscrire(Entree(f"revalorisation_{annee}", ident, date, date, None,
                                     "revalorisation", vivante))
        for regime in vivante.regimes:
            origine = f"pension_{regime.regime}"
            self.journal.inscrire(Entree(
                f"{origine}_{annee}", ident, date, date, None, "composante",
                {"id": f"{origine}_{annee}", "regime": regime.regime,
                 "montant": {"annuel": regime.aujourd_hui, "monnaie": "EUR"},
                 "debut": date, "detail": f"× {regime.coefficient:.6f}, règle {regime.regle}"},
                remplace=origine))
        depart = next(e for e in self.journal if e.sorte == "foyer")
        self.journal.inscrire(Entree(f"foyer_{annee}", ident, date, date, None, "foyer",
                                     foyer, remplace=depart.id))

    def _inscrire(self, evenement: Evenement, ident: str, sorte: str, contenu,
                  debut: str, remplace: str | None = None) -> None:
        self.journal.inscrire(Entree(ident, evenement.id, evenement.date, debut, None,
                                     sorte, contenu, remplace=remplace))
