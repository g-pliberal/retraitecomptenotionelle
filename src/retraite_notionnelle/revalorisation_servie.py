"""Ce que devient, année après année, une pension déjà liquidée : la lecture du coût.

Le coût agrégé sert des pensions liquidées depuis des décennies : il lui faut,
pour chaque régime, chaque année de liquidation et chaque année servie, ce que
vaut un euro de pension. :class:`RevalorisationServie` le lui dit, et ne le
dit qu'à lui : la page Coût, les facteurs de la dépense, le bilan du compte,
les contrôles et les études de la fabrique.

Sous les systèmes notionnels, la règle ne s'écrit qu'en JavaScript
(``moteur/js/revalorisation.js``, note de décision 0007), et la classe en lit
les séries au pont. Sous le scénario 1, elle calcule ici ce que le droit a
servi jusqu'au dernier barème publié, en demandant au portage, par lot, les
règles du moteur dont elle fait les moyennes.

Ce module n'importe aucune règle du moteur Python d'une carrière : il tient
sans ``revalorisation.py``, qui lui reprend les constantes et les deux
lectures de tables qu'ils partagent tant que ce jumeau vit (action 161).
"""

from __future__ import annotations

import copy
from datetime import date
from typing import Callable

from .calendrier import DateMois
from .config import RevalorisationStock
from .somme import somme_ordonnee


#: La péréquation des pensions civiles et militaires cesse à cette date : la
#: rédaction de 2003 de l'article L. 16 leur donne une revalorisation par décret.
FIN_PEREQUATION = date(2004, 1, 1)

#: À compter de cette date, les pensions civiles et militaires suivent l'article
#: L. 161-23-1 (loi n° 2008-1330, art. 79, en vigueur le 19 décembre 2008 ; la
#: première revalorisation qui en relève est celle du 1er avril 2009), et les
#: régimes spéciaux le taux des fonctionnaires (décrets de 2008).
DEBUT_REGLE_GENERALE_PUBLIC = date(2009, 1, 1)

#: Le dernier point d'indice que la péréquation a servi : celui du
#: 1er décembre 2002, resté en vigueur jusqu'au 31 décembre 2003.
DERNIERE_ANNEE_PEREQUATION = 2003

#: Les règles, telles que la page les nomme et que la sortie JSON les écrit.
REGLE_POINT = "point"
REGLE_GENERALE = "regime_general"
REGLE_FONCTION_PUBLIQUE = "fonction_publique"

#: Les régimes que l'article L. 16 du code des pensions civiles et militaires
#: revalorise, directement ou par renvoi : l'État, la CNRACL (décret
#: n° 2003-1306, art. 19) et les ouvriers de l'État (décret n° 2004-1056,
#: art. 15) — les décrets de 2004 à 2007 les nomment tous trois.
REGIMES_FONCTION_PUBLIQUE = frozenset({
    "fonction_publique_etat", "pensions_civiles_1853", "cnracl", "fspoeie",
})


def _derniere_valeur_publiee(actuel, code: str) -> int | None:
    """Dernière année dont la valeur de service est publiée, au bout de la
    chaîne des fusions que :func:`~retraite_notionnelle.droit.liquider.valeur_du_point` remonte."""
    courant = code
    for _ in range(len(actuel.catalogue) + 1):  # garde-fou : jamais de boucle
        derniere = actuel.valeurs_point.derniere_annee_servie(courant)
        if derniere is None:
            return None
        successeur = (actuel.catalogue[courant].integre_dans
                      if courant in actuel.catalogue else None)
        reprise = (actuel.conversions_points.fusion(courant, successeur)
                   if successeur else None)
        if reprise is None:
            return derniere
        courant = successeur
    return None  # pragma: no cover - chaîne de successions cyclique


def _derniere_annee(regime) -> int:
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


class RevalorisationServie:
    """Ce que devient une pension DÉJÀ LIQUIDÉE, année après année.

    UN SEUL EXEMPLAIRE DU CALCUL (note de décision 0007, action 161). La
    règle que les systèmes notionnels prêtent aux pensions servies — l'index
    du compte, déflaté des prix et rendu de son préfinancement, et la valeur
    de service convenue des régimes en points — ne s'écrit qu'en JavaScript :
    ``RevalorisationServie`` de ``moteur/js/revalorisation.js``, où son
    raisonnement est écrit en entier, et que le lecteur du site règle. Cette
    classe en demande les séries au pont, une fois par jeu de paramètres
    (:func:`~.pont.series_servies`), et ne fait plus que les lire : un
    coefficient est le rapport de deux valeurs d'une série. Quatre lectures
    gardent donc le nom de celles du portage — :meth:`coefficient`,
    :meth:`coefficient_stock`, :meth:`coefficient_points`,
    :meth:`regime_convenu` —, que
    ``test_les_lectures_python_de_la_revalorisation_servie_sont_celles_du_portage``
    (``tests/test_pont.py``) confronte à lui, au bit.

    CE QUI NE S'ÉCRIT QU'ICI est ce que le coût seul lit, et que le site n'a
    pas : ce que le droit a servi jusqu'au dernier barème publié
    (:meth:`coefficient_historique`), la rente nominale du pilier
    (:meth:`coefficient_nominal`), la proposition sous une variante
    démographique (:meth:`pour_la_proposition`), le régime sous lequel le COR
    compte une pension (:meth:`regime_de_tete`). L'histoire du droit n'appelle
    pas pour autant une règle du moteur Python : la valeur de service d'un
    point, le coefficient de l'article L. 161-23-1, les décrets de la fonction
    publique, le point d'indice et le changement d'unité d'un point, elle les
    demande au portage, d'un seul lot par règle de revalorisation
    (:meth:`_lot`, :func:`~.pont.droit`), et n'en fait que les moyennes.
    """

    def __init__(self, simulateur: Simulateur,
                 premiere_annee: int, derniere_annee: int) -> None:
        from . import pont

        #: Les prix, pour ce qui n'est revalorisé sur RIEN : voir
        #: :meth:`coefficient_nominal`.
        self._macro = simulateur.macro
        #: L'année à partir de laquelle une réforme PROSPECTIVE revalorise ce
        #: qu'elle sert : voir :data:`CLES_PROSPECTIVES`.
        self.annee_bascule = simulateur.parametres.annee_bascule
        #: Le stock à la bascule garde-t-il les prix ? Voir :meth:`coefficient_stock`.
        self.stock_sur_les_prix = (
            simulateur.parametres.revalorisation_stock is RevalorisationStock.PRIX
        )
        #: Ce que le portage a calculé sous ces paramètres : l'index du
        #: compte, en euros constants ; la valeur de service convenue de
        #: chaque régime en points, 1 jusqu'à son dernier barème publié
        #: (:meth:`coefficient_points`) ; et, de chaque régime du catalogue,
        #: celui qui sert ses points au bout de ses fusions
        #: (:meth:`regime_convenu`).
        series = pont.series_servies(simulateur.parametres, premiere_annee, derniere_annee)
        self.premiere_annee = series.premiere_annee
        self.derniere_annee = series.derniere_annee
        self._index: dict[int, float] = series.index
        self._points: dict[str, dict[int, float]] = series.points
        self._convenus: dict[str, str | None] = series.convenus
        actuel = simulateur.scenario_actuel
        self._catalogue = actuel.catalogue
        #: Ce que le droit a servi, jusqu'au dernier barème : voir
        #: :meth:`coefficient_historique`. Construit à la demande.
        self._moteur = actuel
        self._revalorisations = simulateur.revalorisations
        self._parametres = simulateur.parametres
        self._prix_reels: dict[int, float] = {}
        self._nominaux: dict[object, tuple[dict[int, float], int | None]] = {}
        #: Le changement d'unité des points de chaque barème lu, entre deux
        #: années de son histoire : voir :meth:`_nominal`.
        self._echelles: dict[str, dict[tuple[int, int], float]] = {}
        self._regles: dict[tuple[str, int], object] = {}
        self._historiques: dict[tuple[str, int, int], float] = {}

    # -- ce que le droit a servi jusqu'au dernier barème ----------------------

    #: La première revalorisation que la Cnav publie : avant, un coefficient
    #: de un.
    HISTOIRE_DEPUIS = 1949

    #: Le montant total brut mensuel de décembre 2019 qui choisit la tranche
    #: de 2020 (loi n° 2019-1446, art. 81) : celle du milieu, 0,8 %, entre le
    #: 1 % des petites retraites et le 0,3 % des grandes. Une convention, que
    #: les masses ne peuvent pas lever : elles ne connaissent pas le montant
    #: de chaque retraité.
    MENSUEL_2019 = 2004.0

    def _prix(self, annee: int) -> float:
        """Les prix de ``annee`` sur ceux de :attr:`HISTOIRE_DEPUIS`."""
        if not self._prix_reels:
            indice = 1.0
            self._prix_reels[self.HISTOIRE_DEPUIS] = indice
            for millesime in range(self.HISTOIRE_DEPUIS + 1, self.derniere_annee + 1):
                indice /= self._macro.coefficient_prix(millesime, millesime - 1)
                self._prix_reels[millesime] = indice
        borne = min(max(annee, self.HISTOIRE_DEPUIS), self.derniere_annee)
        return self._prix_reels[borne]

    #: Les règles du moteur que l'histoire demande au portage, sous le nom que
    #: le pont du droit leur donne (:data:`~.pont.LECTURES_DU_DROIT`).
    VALEUR_DU_POINT = "liquider.valeur_du_point"
    COEFFICIENT_GENERAL = "scenario_actuel.revalorisations_pensions.generale"
    DECRETS_PUBLICS = "scenario_actuel.revalorisations_pensions.retenues.fonction_publique.produit"
    POINT_D_INDICE = "scenario_actuel.minimum_garanti.ratio_point_indice"
    ECHELLE_DU_POINT = "scenario_actuel.conversions_points.echelle"

    def _lot(self, appels: dict[str, tuple]) -> dict:
        """Ce que le portage rend de chaque appel d'une règle du moteur, sous
        sa clé, d'une seule demande (:func:`~.pont.droit`), sous les
        paramètres du simulateur. Un appel qu'il refuse arrête la lecture."""
        from . import pont

        lus, refus = pont.droit(appels, self._parametres)
        for cle, motif in refus.items():
            raise ValueError(f"{cle} : {motif}")
        return lus

    def _jours(self, fin: int | None) -> list[date]:
        """Le premier jour de chaque mois de :attr:`HISTOIRE_DEPUIS` à ``fin`` :
        ceux que :meth:`_moyennes` lit."""
        if fin is None:
            return []
        return [date(annee, mois, 1)
                for annee in range(self.HISTOIRE_DEPUIS, min(fin, self.derniere_annee) + 1)
                for mois in range(1, 13)]

    def _moyennes(self, au_jour, fin: int | None) -> dict[int, float]:
        """La moyenne, mois par mois, de ``au_jour(date)`` sur chaque année de
        :attr:`HISTOIRE_DEPUIS` à ``fin`` : une masse annuelle sert douze
        mensualités, et une revalorisation d'avril n'en touche que neuf. Une
        année manque dès qu'un de ses mois n'a pas de valeur."""
        moyennes: dict[int, float] = {}
        jours = self._jours(fin)
        for rang in range(0, len(jours), 12):
            valeurs = [au_jour(jour) for jour in jours[rang:rang + 12]]
            if all(valeur is not None and valeur > 0.0 for valeur in valeurs):
                moyennes[jours[rang].year] = somme_ordonnee(valeurs) / 12.0
        return moyennes

    def _nominal(self, regle) -> tuple[dict[int, float], int | None]:
        """L'indice nominal moyen de chaque année sous ``regle``, et la
        dernière année qu'un barème publié couvre. Chaque mois de la règle se
        demande au portage d'un seul lot (:meth:`_lot`), avec, pour un régime
        en points, le changement d'unité de son point entre deux années."""
        if regle in self._nominaux:
            return self._nominaux[regle]
        from . import pont

        origine = date(self.HISTOIRE_DEPUIS - 1, 12, 31).isoformat()

        def generale(jour: date) -> tuple:
            return (self.COEFFICIENT_GENERAL, pont.MOTEUR, origine, jour.isoformat(), False,
                    self.MENSUEL_2019)

        fin_generale = max(ligne.date_effet.year for ligne in self._revalorisations.generales)
        if regle == REGLE_GENERALE:
            lus = self._lot({jour.isoformat(): generale(jour)
                             for jour in self._jours(fin_generale)})
            resultat = (self._moyennes(lambda jour: lus[jour.isoformat()][0], fin_generale),
                        fin_generale)
        elif regle == REGLE_FONCTION_PUBLIQUE:
            # La péréquation, au point d'indice, jusqu'en 2003 ; les décrets
            # de 2004 à 2008 ; la règle générale ensuite — l'ordre de
            # :meth:`PensionServie._fonction_publique`, à l'année.
            appels = {}
            for jour in (*self._jours(fin_generale), DEBUT_REGLE_GENERALE_PUBLIC):
                fin = min(jour.year, DERNIERE_ANNEE_PEREQUATION)
                appels[f"point {fin}"] = (
                    self.POINT_D_INDICE, pont.MOTEUR, DERNIERE_ANNEE_PEREQUATION, fin)
                if jour >= FIN_PEREQUATION:
                    jusqu_a = min(jour, DEBUT_REGLE_GENERALE_PUBLIC).isoformat()
                    appels[f"decrets {jusqu_a}"] = (
                        self.DECRETS_PUBLICS, pont.MOTEUR, FIN_PEREQUATION.isoformat(), jusqu_a,
                        True, None)
                if jour >= DEBUT_REGLE_GENERALE_PUBLIC:
                    appels[f"generale {jour.isoformat()}"] = generale(jour)
            lus = self._lot(appels)

            def publique(jour: date) -> float | None:
                point = lus[f"point {min(jour.year, DERNIERE_ANNEE_PEREQUATION)}"]
                if point is None:
                    return None
                if jour < FIN_PEREQUATION:
                    return point
                decrets = lus[
                    f"decrets {min(jour, DEBUT_REGLE_GENERALE_PUBLIC).isoformat()}"][0]
                suite = (lus[f"generale {jour.isoformat()}"][0]
                         / lus[f"generale {DEBUT_REGLE_GENERALE_PUBLIC.isoformat()}"][0]
                         if jour >= DEBUT_REGLE_GENERALE_PUBLIC else 1.0)
                return point * decrets * suite
            resultat = (self._moyennes(publique, fin_generale), fin_generale)
        else:
            # Un régime en points : la valeur de service du jour, le long des
            # fusions (:func:`~.droit.liquider.valeur_du_point`), et le
            # changement d'unité du point entre deux années de son histoire,
            # que :meth:`_historique` lit.
            bareme = regle[1]
            publiee = _derniere_valeur_publiee(self._moteur, bareme)
            jours = self._jours(publiee)
            annees = [jour.year for jour in jours[::12]]
            lus = self._lot({
                **{jour.isoformat(): (self.VALEUR_DU_POINT, pont.MOTEUR, bareme,
                                      DateMois(jour.year, jour.month)) for jour in jours},
                **{f"{depart} {arrivee}": (self.ECHELLE_DU_POINT, pont.MOTEUR, bareme, depart,
                                           arrivee)
                   for depart in annees for arrivee in annees if arrivee > depart}})

            def point(jour: date) -> float | None:
                valeur = lus[jour.isoformat()]
                return None if valeur is None else valeur[0]
            self._echelles[bareme] = {
                (depart, arrivee): lus[f"{depart} {arrivee}"][0]
                for depart in annees for arrivee in annees if arrivee > depart}
            resultat = (self._moyennes(point, publiee), publiee)
        self._nominaux[regle] = resultat
        return resultat

    def _regle_historique(self, regime: str, annee_liquidation: int):
        """La règle qui a revalorisé une pension de ``regime`` liquidée en
        ``annee_liquidation`` : celle de :meth:`PensionServie.coefficient`,
        lue sur la période du régime plutôt que sur la pension."""
        cle = (regime, annee_liquidation)
        if cle in self._regles:
            return self._regles[cle]
        regle = REGLE_GENERALE
        fiche = self._catalogue[regime] if regime in self._catalogue else None
        if fiche is not None:
            periode = fiche.periode(min(annee_liquidation, _derniere_annee(fiche)))
            if periode is not None and periode.type_calcul in ("points", "mixte"):
                bareme = periode.points_de or regime
                if _derniere_valeur_publiee(self._moteur, bareme) is not None:
                    regle = (REGLE_POINT, bareme)
            if regle == REGLE_GENERALE and regime in REGIMES_FONCTION_PUBLIQUE:
                regle = REGLE_FONCTION_PUBLIQUE
        self._regles[cle] = regle
        return regle

    def coefficient_historique(self, regime: str, annee_liquidation: int,
                               annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension de
        ``regime`` liquidé en ``annee_liquidation``, sous ce que le droit a
        servi jusqu'au dernier barème publié, et un au-delà.

        LE SCÉNARIO 1 N'A PAS SUIVI LES PRIX. Le régime général a gelé ses
        pensions en 2014, les a revalorisées de 0,3 % en 2019 ; l'Agirc-Arrco
        a laissé son point plusieurs années sans revalorisation : une pension
        liquidée avant 2014 vaut, en 2024, 5 % de moins que la même revalorisée
        sur les prix (action 147, étape 18). C'est le droit, que les masses de
        la page Coût servaient jusqu'au 14 octobre 2026 comme des prix
        constants. Trois règles, celles de :class:`PensionServie` : les
        coefficients de la Cnav (L. 161-23-1), pour tout ce qui n'a pas de
        texte à soi, les régimes spéciaux compris ; la péréquation puis les
        décrets de la fonction publique ; la valeur de service des régimes en
        points, changements d'échelle compris. Chacune à la moyenne de
        l'année, déflatée des prix. Les majorations forfaitaires de 1972 à
        1982, qui ne visent que certaines pensions, n'y sont pas.
        """
        cle = (regime, annee_liquidation, annee)
        if cle in self._historiques:
            return self._historiques[cle]
        # Le RAFP, hors répartition, n'est pas dans la masse du scénario 1, et
        # sa part ne s'y revalorise pas (``test_la_masse_se_decompose_regime_par_regime``).
        if regime in self._catalogue and self._catalogue[regime].hors_repartition:
            self._historiques[cle] = 1.0
            return 1.0
        regle = self._regle_historique(regime, annee_liquidation)
        coefficient = self._historique(regle, annee_liquidation, annee)
        if coefficient is None:
            coefficient = self._historique(REGLE_GENERALE, annee_liquidation, annee)
        self._historiques[cle] = coefficient
        return coefficient

    def _historique(self, regle, annee_liquidation: int, annee: int) -> float | None:
        moyennes, derniere = self._nominal(regle)
        if derniere is None:
            return None
        depart = max(annee_liquidation, self.HISTOIRE_DEPUIS)
        arrivee = min(annee, derniere, self.derniere_annee)
        if arrivee <= depart:
            return 1.0
        if depart not in moyennes or arrivee not in moyennes:
            return None
        nominal = moyennes[arrivee] / moyennes[depart]
        if regle not in (REGLE_GENERALE, REGLE_FONCTION_PUBLIQUE):
            nominal *= self._echelles[regle[1]][depart, arrivee]
        return nominal * self._prix(depart) / self._prix(arrivee)

    def regime_convenu(self, regime: str) -> str | None:
        """Le régime qui sert, au bout de ses fusions, les points de
        ``regime``, s'il a une valeur de service convenue ; ``None`` sinon.
        Lu dans la table que le portage en a rendue."""
        return self._convenus.get(regime)

    def regime_de_tete(self, regime: str) -> str:
        """Le régime qui sert, au bout de ses fusions, les droits de
        ``regime`` : celui sous lequel le COR le compte (l'Arrco et l'Agirc
        sous l'Agirc-Arrco, les pensions civiles de 1853 sous la fonction
        publique d'État)."""
        courant = regime
        for _ in range(len(self._catalogue) + 1):
            fiche = self._catalogue[courant] if courant in self._catalogue else None
            if fiche is None or not fiche.integre_dans:
                return courant
            courant = fiche.integre_dans
        return courant

    def coefficient_points(self, regime: str, annee_liquidation: int,
                           annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension
        servie en points de ``regime`` (au bout de ses fusions) liquidé en
        ``annee_liquidation`` : le rapport de la valeur de service convenue
        à celle de la liquidation, déflaté des prix. 1 pour un régime sans
        convention, et jusqu'au dernier barème publié, que la projection lit
        en euros constants comme le reste du scénario 1."""
        serie = self._points.get(regime)
        if serie is None or annee <= annee_liquidation:
            return 1.0
        def valeur(millesime: int) -> float:
            return serie[min(max(millesime, self.premiere_annee), self.derniere_annee)]
        return valeur(annee) / valeur(annee_liquidation)

    def _valeur(self, annee: int) -> float:
        borne = min(max(annee, self.premiere_annee), self.derniere_annee)
        return self._index[borne]

    #: Ce que sert la PROPOSITION : la même règle, sauf sous une variante
    #: démographique, où la masse salariale qui l'indexe est celle de la
    #: variante (:meth:`pour_la_proposition`). Lu à l'appel : un objet construit
    #: sans elle se sert lui-même.
    @property
    def proposition(self) -> "RevalorisationServie":
        return self.__dict__.get("_proposition", self)

    def pour_la_proposition(self, facteur: Callable[[int], float]
                            ) -> "RevalorisationServie":
        """Une copie dont la proposition revalorise sur la masse salariale
        multipliée, chaque année, par ``facteur`` — ce qu'une variante
        démographique change à l'emploi (action 138, étape 7,
        :meth:`~.donnees.population.Population.facteur_actifs`). Tous les
        coefficients étant des rapports de l'index à deux dates, multiplier
        l'index suffit, la règle du stock comprise. Les autres systèmes, et ce
        que le droit a servi, gardent la règle du central."""
        centrale = copy.copy(self)
        variante = copy.copy(self)
        variante._index = {annee: valeur * facteur(annee)
                           for annee, valeur in self._index.items()}
        centrale._proposition = variante
        return centrale

    def coefficient(self, annee_liquidation: int, annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension
        liquidé en ``annee_liquidation``.

        Vaut exactement 1 l'année de la liquidation et avant elle : une pension
        qui n'est pas encore servie ne se revalorise pas.
        """
        if annee <= annee_liquidation:
            return 1.0
        depart = self._valeur(annee_liquidation)
        return self._valeur(annee) / depart if depart else 1.0

    def coefficient_nominal(self, annee_liquidation: int, annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de rente
        NOMINALE et constante liquidé en ``annee_liquidation``.

        C'est la rente du pilier capitalisé : un contrat à taux technique nul,
        que rien ne revalorise. Les prix seuls la déprécient, et ce coefficient
        est leur rapport — un l'année de la liquidation, moins ensuite. Le
        compte des flux du pilier la sert ainsi ; la garantie, qui la regarde,
        la revalorisait jusqu'au 23 septembre 2026 comme une pension
        notionnelle, sur la masse salariale.
        """
        if annee <= annee_liquidation:
            return 1.0
        return self._macro.coefficient_prix(annee, annee_liquidation)

    def coefficient_stock(self, annee_liquidation: int, annee: int,
                          prospectif: bool) -> float:
        """Le même coefficient, avec la règle du STOCK à la bascule.

        Une pension liquidée à compter de la bascule suit la règle du compte
        depuis sa liquidation, dans tous les cas. Une pension liquidée AVANT :

        - sous ``PRIX``, elle garde les prix — coefficient 1 en euros
          constants — à compter de la bascule. Pour une réforme prospective,
          qui n'existait pas avant, c'est 1 depuis toujours ; pour une réforme
          rétroactive, dont le compte fictif a été revalorisé sur sa règle
          jusqu'à la bascule, le coefficient est gelé à sa valeur de la
          bascule ;
        - sous ``REINDEXE``, la réforme prospective la prend à sa règle le jour
          de la bascule (``max(liquidation, bascule)``), et la rétroactive
          l'a toujours revalorisée sur la sienne.
        """
        bascule = self.annee_bascule
        if annee_liquidation >= bascule:
            return self.coefficient(annee_liquidation, annee)
        if self.stock_sur_les_prix:
            if prospectif:
                return 1.0
            return self.coefficient(annee_liquidation, min(annee, bascule))
        if prospectif:
            return self.coefficient(bascule, annee)
        return self.coefficient(annee_liquidation, annee)
