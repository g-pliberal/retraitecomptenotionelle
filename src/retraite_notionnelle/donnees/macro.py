"""Séries macroéconomiques : prix, salaires, productivité, plafond."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle, charger_yaml

#: Première année où les salaires portés au compte sont revalorisés sur les
#: PRIX et non plus sur les salaires. Avant elle, les arrêtés annuels de
#: revalorisation suivaient l'évolution des salaires ; à partir de 1987 ils
#: suivent celle des prix, ce que la loi du 22 juillet 1993 a ensuite inscrit
#: dans le code en retenant l'indice hors tabac. C'est une date de droit, pas
#: un choix de modélisation : elle est isolée ici pour être lisible d'un coup
#: d'œil et déplaçable d'un seul geste si la source venait à la préciser.
ANNEE_REVALORISATION_SUR_LES_PRIX = 1987

#: L'assurance vieillesse des parents au foyer naît le 1er juillet 1972 (loi
#: n° 72-8 du 3 janvier 1972) : aucune assiette avant.
ANNEE_CREATION_AVPF = 1972

#: Heures de SMIC de l'assiette MENSUELLE de l'AVPF, « 169 fois le salaire
#: horaire minimum de croissance en vigueur au 1er juillet de l'année civile
#: précédente » (R. 381-3, rédactions de 2002 et de 2023).
HEURES_AVPF_PAR_MOIS = 169

#: Une année de SMIC à temps complet sur 35 heures : 35 heures pendant 52
#: semaines, les « 151,67 heures par mois » du SMIC mensualisé, que l'INSEE
#: et le barème calculent sur 151,666… et non sur leur arrondi. C'est la durée
#: qui prolonge ``smic_annuel.csv`` au-delà de la dernière année publiée.
HEURES_ANNUELLES_SMIC = 35 * 52


def lire_smic_releve(racine: Path, annee: int) -> tuple[int, float] | None:
    """Le dernier relèvement du SMIC en cours d'``annee``, lu sur le fichier."""
    import csv

    chemin = racine / "reference" / "macro" / "smic_horaire_releves.csv"
    if not chemin.exists():
        return None
    dernier: tuple[int, float] | None = None
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            an, mois, _ = (int(x) for x in ligne["date_effet"].split("-"))
            if an == annee and mois > 1 and (dernier is None or mois >= dernier[0]):
                dernier = (mois, float(ligne["smic_horaire"]))
    return dernier


@dataclass
class DonneesMacro:
    """Accès unifié aux séries annuelles servant à l'indexation et aux assiettes.

    Au-delà de la dernière année observée, les séries sont prolongées par le
    scénario de projection choisi (``reference/macro/hypotheses_projection.yaml``)
    et non par la dernière valeur connue. Les années projetées portent la
    fiabilité la plus basse, ce qui se propage jusqu'au résultat final.
    """

    racine: Path
    scenario_projection: str | None = None
    #: Trajectoire de l'emploi au-delà de la dernière observation (clé de
    #: ``trajectoires_emploi``) ; ``None`` prend le défaut du fichier.
    trajectoire_emploi: str | None = None

    @cached_property
    def _hypotheses(self) -> dict:
        return charger_yaml(
            self.racine / "reference" / "macro" / "hypotheses_projection.yaml"
        )

    @cached_property
    def projection(self) -> dict:
        hypotheses = self._hypotheses
        nom = self.scenario_projection or hypotheses.get("scenario_par_defaut")
        scenarios = hypotheses.get("scenarios", {})
        if nom not in scenarios:
            raise KeyError(
                f"scénario de projection inconnu : {nom!r}. Disponibles : "
                + ", ".join(sorted(scenarios))
            )
        return {**scenarios[nom], "code": nom,
                "fin": int(hypotheses.get("annee_fin_projection", 2100))}

    @cached_property
    def trajectoire(self) -> dict:
        """La trajectoire d'emploi retenue, telle que le fichier la décrit."""
        hypotheses = self._hypotheses
        nom = self.trajectoire_emploi or hypotheses.get(
            "trajectoire_emploi_par_defaut", "constant")
        trajectoires = hypotheses.get("trajectoires_emploi", {})
        if nom not in trajectoires:
            raise KeyError(
                f"trajectoire d'emploi inconnue : {nom!r}. Disponibles : "
                + ", ".join(sorted(trajectoires))
            )
        return {**(trajectoires[nom] or {}), "code": nom}

    def _prolonger(self, serie: SerieAnnuelle, cle: str) -> SerieAnnuelle:
        return serie.prolongee(float(self.projection[cle]), self.projection["fin"])

    @cached_property
    def emploi(self) -> SerieAnnuelle:
        """Croissance annuelle de l'EMPLOI, sur les seules années projetées.

        Nulle partout sous la trajectoire ``constant`` ; lue dans le fichier de
        la trajectoire sinon, et nulle au-delà de sa dernière année — 2070 pour
        le COR, qui n'y projette rien. La série ne commence qu'à la première
        année projetée : avant, l'emploi est dans les séries observées.
        """
        from .chargement import ValeurAnnuelle

        debut = self.annee_derniere_observation_declaree + 1
        fin = self.projection["fin"]
        valeurs = {
            annee: ValeurAnnuelle(annee, 0.0, Fiabilite.ESTIMEE)
            for annee in range(debut, fin + 1)
        }
        fichier = self.trajectoire.get("fichier")
        if fichier:
            serie = charger_serie_annuelle(
                self.racine / "reference" / "macro" / fichier,
                colonne_valeur="croissance_emploi",
                nom="croissance_emploi",
            )
            for annee in serie.annees():
                if debut <= annee <= fin:
                    valeurs[annee] = ValeurAnnuelle(
                        annee, serie(annee), min(serie.fiabilite(annee),
                                                 Fiabilite.ESTIMEE))
        return SerieAnnuelle(valeurs, "croissance_emploi", "escalier")

    def _prolonger_avec_emploi(self, serie: SerieAnnuelle, cle: str) -> SerieAnnuelle:
        """Prolonge une assiette : le taux du scénario COMPOSÉ avec l'emploi.

        ``(1 + taux) × (1 + emploi de l'année) − 1``, année par année. Le taux
        du fichier d'hypothèses est celui du salaire moyen, à emploi constant ;
        c'est ici que l'emploi entre, et nulle part ailleurs.
        """
        from .chargement import ValeurAnnuelle

        valeurs = {annee: serie.brut(annee) for annee in serie.annees()}
        base = float(self.projection[cle])
        premiere_projetee = self.annee_derniere_observation_declaree + 1
        for annee in range(serie.derniere_annee + 1, self.projection["fin"] + 1):
            emploi = self.emploi(annee) if annee >= premiere_projetee else 0.0
            valeurs[annee] = ValeurAnnuelle(
                annee, (1 + base) * (1 + emploi) - 1, Fiabilite.ESTIMEE)
        return SerieAnnuelle(valeurs, serie.nom, serie.interpolation)

    @cached_property
    def derniere_annee_observee(self) -> int:
        """Dernière année dont l'indexation ne doit rien à une hypothèse.

        Déduite des séries elles-mêmes — la dernière année que les trois
        assiettes portent au-dessus de ``estimee`` — et non lue dans le fichier
        d'hypothèses, qui la DÉCLARE de son côté. Les deux doivent coïncider, et
        un test le vérifie : une déclaration qui ne se contrôle pas finit par
        mentir, et celle-ci sert à dire au lecteur du site à partir de quelle
        année son résultat repose sur un scénario.
        """
        return min(
            max(a for a in serie.annees() if serie.fiabilite(a) > Fiabilite.ESTIMEE)
            for serie in (self.inflation, self.salaire_moyen, self.masse_salariale)
        )

    @property
    def annee_derniere_observation_declaree(self) -> int:
        """Ce que le fichier d'hypothèses annonce, à confronter à l'observé."""
        return int(self._hypotheses["annee_derniere_observation"])

    @cached_property
    def inflation(self) -> SerieAnnuelle:
        """Variation annuelle de l'indice des prix à la consommation."""
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "ipc_annuel.csv",
            colonne_valeur="variation",
            nom="inflation",
        )
        return self._prolonger(serie, "inflation")

    @cached_property
    def salaire_moyen(self) -> SerieAnnuelle:
        """Variation annuelle NOMINALE du salaire moyen par tête."""
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "salaire_moyen.csv",
            colonne_valeur="variation_nominale",
            nom="salaire_moyen_nominal",
        )
        return self._prolonger(serie, "salaire_moyen_nominal")

    @cached_property
    def salaire_moyen_niveau(self) -> SerieAnnuelle:
        """Le salaire moyen par tête EN NIVEAU, en euros bruts annuels courants,
        des années que les comptes nationaux publient.

        Le même rapport que :attr:`salaire_moyen`, qui n'en garde que les
        variations : le modèle les cumule à partir du niveau d'une année, lu
        ici (:func:`~retraite_notionnelle.carriere.ancrage_salaire_moyen`).
        """
        return charger_serie_annuelle(
            self.racine / "reference" / "macro" / "salaire_moyen_niveau.csv",
            colonne_valeur="salaire_moyen_annuel",
            nom="salaire_moyen_niveau",
        )

    @cached_property
    def _smic_annuel_publie(self) -> SerieAnnuelle:
        return charger_serie_annuelle(
            self.racine / "reference" / "macro" / "smic_annuel.csv",
            colonne_valeur="smic_annuel",
            nom="smic_annuel",
        )

    def smic_annuel(self, annee: int) -> float:
        """Le salaire minimum brut d'une année ENTIÈRE à temps complet, en
        euros de cette année : le revenu du cas type « au niveau du SMIC ».

        Publié par l'INSEE de 1951 à la dernière année complète
        (``smic_annuel.csv``) : le barème moyen de l'année fois la durée légale
        — 40 heures par semaine jusqu'en 1981, 39 ensuite, 35 depuis 2000.
        Au-delà, 1 820 heures du barème horaire du modèle, mois par mois :
        celui de janvier, puis, l'année du dernier relèvement connu, celui-ci à
        compter de son mois (``smic_horaire_releves.csv``). Avant le premier
        SMIG, le rapport de 1951 au salaire moyen, faute de minimum légal :
        c'est la seule hypothèse qui n'invente rien.
        """
        publie = self._smic_annuel_publie
        if annee < publie.premiere_annee:
            premiere = publie.premiere_annee
            return publie(premiere) * self.coefficient_salaire_moyen(premiere, annee)
        if annee <= publie.derniere_annee:
            return publie(annee)
        janvier = self.smic_horaire(annee)
        derniere, releve = self._smic_publie
        if annee == derniere and releve is not None:
            mois, valeur = releve
            horaire_moyen = (janvier * (mois - 1) + valeur * (13 - mois)) / 12
        else:
            horaire_moyen = janvier
        return HEURES_ANNUELLES_SMIC * horaire_moyen

    @cached_property
    def masse_salariale(self) -> SerieAnnuelle:
        """Variation annuelle NOMINALE de la masse salariale — l'assiette.

        Salaires et traitements bruts du total des branches, pris en niveau :
        le produit du salaire moyen par l'emploi salarié. C'est le taux de
        rendement qu'un système en répartition peut servir sans changer son
        taux de cotisation, et donc, dans la théorie des comptes notionnels, le
        taux d'indexation de référence.

        Au-delà de la dernière observation, le salaire moyen du scénario est
        composé avec la trajectoire d'emploi : voir :attr:`emploi`.
        """
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "masse_salariale.csv",
            colonne_valeur="variation_nominale",
            nom="masse_salariale_nominale",
        )
        return self._prolonger_avec_emploi(serie, "masse_salariale_nominale")

    @cached_property
    def pib_nominal(self) -> SerieAnnuelle:
        """Variation annuelle NOMINALE du produit intérieur brut.

        Assiette plus large que la masse salariale : elle capte le déplacement
        de la valeur ajoutée vers les revenus non salariaux, que la masse
        salariale subit. C'est celle que l'Italie retient pour revaloriser les
        comptes notionnels, lissée sur cinq ans — le lissage est appliqué par
        :class:`~retraite_notionnelle.moteur.indexation.Indexation`, pas ici.
        """
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "pib_nominal.csv",
            colonne_valeur="variation_nominale",
            nom="pib_nominal",
        )
        return self._prolonger_avec_emploi(serie, "pib_nominal")

    @cached_property
    def productivite(self) -> SerieAnnuelle:
        """Variation annuelle RÉELLE de la productivité du travail par tête."""
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "productivite.csv",
            colonne_valeur="variation_reelle",
            nom="productivite_reelle",
        )
        return self._prolonger(serie, "productivite_reelle")

    @cached_property
    def smic_horaire(self) -> SerieAnnuelle:
        """SMIC horaire brut, en euros courants, barème du 1er janvier.

        Sert à la validation des trimestres : un trimestre s'acquiert par un
        montant cotisé, pas par le temps qui passe. Au-delà de la dernière
        valeur publiée, le SMIC suit la croissance du salaire moyen — c'est son
        indexation légale, à laquelle s'ajoutent des coups de pouce que le
        modèle ne prétend pas anticiper.
        """
        from .chargement import ValeurAnnuelle

        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "smic_horaire.csv",
            colonne_valeur="smic_horaire",
            nom="smic_horaire",
        )
        valeurs = {a: serie.brut(a) for a in serie.annees()}
        courant = serie(serie.derniere_annee)
        croissance = float(self.projection["salaire_moyen_nominal"])
        releve = self.smic_horaire_releve(serie.derniere_annee)
        for annee in range(serie.derniere_annee + 1, self.projection["fin"] + 1):
            if releve is not None and annee == serie.derniere_annee + 1:
                # UN SMIC NE BAISSE PAS : janvier suivant part du dernier
                # relèvement en vigueur, porté au même rythme sur les mois qui
                # restent — voir ``smic_horaire_releves.csv``.
                mois, valeur = releve
                courant = valeur * (1 + croissance) ** ((13 - mois) / 12)
            else:
                courant *= 1 + croissance
            valeurs[annee] = ValeurAnnuelle(annee, courant, Fiabilite.ESTIMEE)
        return SerieAnnuelle(valeurs, "smic_horaire", "escalier")

    def smic_horaire_releve(self, annee: int) -> tuple[int, float] | None:
        """Le dernier relèvement du SMIC en cours d'``annee`` : (mois, valeur).

        ``None`` si l'année n'en a pas connu après son barème de janvier, ou si
        le fichier n'existe pas. Seul le dernier compte : c'est lui qui est en
        vigueur au 31 décembre.
        """
        return lire_smic_releve(self.racine, annee)

    @cached_property
    def _smic_publie(self) -> tuple[int, tuple[int, float] | None]:
        """La dernière année du barème du SMIC, et son dernier relèvement."""
        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "smic_horaire.csv",
            colonne_valeur="smic_horaire",
            nom="smic_horaire",
        )
        return serie.derniere_annee, self.smic_horaire_releve(serie.derniere_annee)

    def smic_horaire_au_1er_juillet(self, annee: int) -> float:
        """Le SMIC horaire en vigueur le 1er juillet de cette année.

        Le barème de janvier, ou, la dernière année publiée, le relèvement
        d'avant juillet qui l'a remplacé (``smic_horaire_releves.csv``) — le
        portage n'en connaît pas d'autre, et le Python s'aligne sur lui.
        """
        derniere, releve = self._smic_publie
        if annee == derniere and releve is not None and releve[0] <= 7:
            return releve[1]
        return self.smic_horaire(annee)

    @cached_property
    def assiette_avpf(self) -> tuple[tuple[str, float], ...]:
        """L'assiette forfaitaire MENSUELLE de l'assurance vieillesse des
        parents au foyer, à chaque date du barème de la Cnav, du 1er juillet
        1972 au dernier publié (``legislation/assiette_avpf.csv``)."""
        import csv

        chemin = self.racine / "reference" / "legislation" / "assiette_avpf.csv"
        if not chemin.exists():
            return ()
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            return tuple(sorted((ligne["date_effet"], float(ligne["assiette_mensuelle"]))
                                for ligne in csv.DictReader(lignes)))

    @cached_property
    def _revenus_avpf(self) -> dict[int, float]:
        return {}

    def revenu_avpf(self, annee: int) -> float:
        """Le salaire qu'une année ENTIÈRE d'assurance vieillesse des parents
        au foyer porte au compte, en euros de cette année.

        La somme des assiettes mensuelles de ses douze mois, telles que la Cnav
        les a fixées : rien avant le 1er juillet 1972, où l'AVPF naît (loi du
        3 janvier 1972). Au-delà du barème, la règle de l'article R. 381-3 :
        169 heures par mois du SMIC en vigueur au 1er juillet de l'année
        précédente. Le modèle portait 1 820 heures du SMIC de janvier de
        l'année, 9 à 10 % de trop peu depuis 1982, 12,5 % avant.
        """
        connu = self._revenus_avpf.get(annee)
        if connu is not None:
            return connu
        datees = self.assiette_avpf
        if datees and annee <= int(datees[-1][0][:4]):
            total = 0.0
            for mois in range(1, 13):
                rang = bisect_right(datees, (f"{annee:04d}-{mois:02d}-01", float("inf")))
                if rang:
                    total += datees[rang - 1][1]
        elif annee < ANNEE_CREATION_AVPF:
            total = 0.0
        else:
            total = (12 * HEURES_AVPF_PAR_MOIS
                     * self.smic_horaire_au_1er_juillet(annee - 1))
        self._revenus_avpf[annee] = total
        return total

    @cached_property
    def heures_par_trimestre(self) -> SerieAnnuelle:
        """Heures de SMIC à cotiser pour valider un trimestre, par année.

        200 heures depuis 1972, 150 depuis 2014. Avant 1972 la validation ne
        dépendait pas du montant : la série ne commence donc qu'en 1972, et
        l'appelant valide quatre trimestres par année travaillée en deçà.
        """
        return charger_serie_annuelle(
            self.racine / "reference" / "legislation" / "validation_trimestres.csv",
            colonne_valeur="heures",
            nom="heures_par_trimestre",
        )

    def trimestres_valides(self, revenu: float, annee: int) -> int:
        """Trimestres qu'un revenu d'activité valide dans l'année.

        Quatre au plus, et zéro si le revenu n'atteint pas le seuil du premier.
        Avant 1972, aucun seuil de montant n'existait : une année travaillée
        vaut quatre trimestres.
        """
        if revenu <= 0:
            return 0
        heures = self.heures_par_trimestre
        if annee < heures.premiere_annee:
            return 4
        seuil = heures(annee) * self.smic_horaire(annee)
        if seuil <= 0:
            return 4
        # UN REVENU QUI TOMBE PILE SUR LE SEUIL LE VALIDE. L'assiette minimale
        # des indépendants vaut 450 SMIC horaires, trois seuils exactement ;
        # mais 450 × 11,88 / (150 × 11,88) donne 2,999… en virgule flottante,
        # et la division entière rendait deux trimestres en 2025 là où la
        # CNAVPL et la CAVAMAC en écrivent trois.
        return max(0, min(4, int(revenu / seuil + 1e-9)))

    @cached_property
    def plafond_securite_sociale(self) -> SerieAnnuelle:
        """Plafond annuel de la Sécurité sociale, en euros courants.

        Au-delà de la dernière valeur publiée, le plafond suit la croissance du
        salaire moyen, conformément à l'article L. 241-3 du code de la sécurité
        sociale.
        """
        from .chargement import ValeurAnnuelle

        serie = charger_serie_annuelle(
            self.racine / "reference" / "macro" / "plafond_securite_sociale.csv",
            colonne_valeur="pass_eur",
            nom="pass",
        )
        if not self._hypotheses.get("plafond_suit_salaire_moyen", True):
            return serie

        valeurs = {a: serie.brut(a) for a in serie.annees()}
        courant = serie(serie.derniere_annee)
        croissance = float(self.projection["salaire_moyen_nominal"])
        for annee in range(serie.derniere_annee + 1, self.projection["fin"] + 1):
            courant *= 1 + croissance
            valeurs[annee] = ValeurAnnuelle(annee, courant, Fiabilite.ESTIMEE)
        return SerieAnnuelle(valeurs, "pass", "escalier")

    # -- grandeurs dérivées --------------------------------------------------

    def productivite_nominale(self, annee: int) -> float:
        """Productivité réelle ramenée en nominal : (1+ρ)(1+π) - 1."""
        return (1 + self.productivite(annee)) * (1 + self.inflation(annee)) - 1

    def coefficient_prix(self, annee_depart: int, annee_arrivee: int) -> float:
        """Coefficient de passage d'euros de ``annee_depart`` en euros de ``annee_arrivee``.

        Sert à exprimer tous les résultats dans une unité comparable — sans quoi
        confronter une pension liquidée en 1975 à une pension de 2026 n'a aucun
        sens.
        """
        if annee_arrivee == annee_depart:
            return 1.0
        if annee_arrivee > annee_depart:
            coefficient = 1.0
            for annee in range(annee_depart + 1, annee_arrivee + 1):
                coefficient *= 1 + self.inflation(annee)
            return coefficient
        return 1.0 / self.coefficient_prix(annee_arrivee, annee_depart)

    def coefficient_salaire_moyen(self, annee_depart: int, annee_arrivee: int) -> float:
        """Coefficient de passage par le salaire moyen par tête, d'une année à
        l'autre : le produit de ses croissances nominales.

        Prolonge un barème que son texte indexe sur les salaires : la valeur
        d'achat du point Agirc-Arrco, au-delà du dernier barème publié
        (``regimes/prolongement_points.csv``).
        """
        if annee_arrivee == annee_depart:
            return 1.0
        if annee_arrivee > annee_depart:
            coefficient = 1.0
            for annee in range(annee_depart + 1, annee_arrivee + 1):
                coefficient *= 1 + self.salaire_moyen(annee)
            return coefficient
        return 1.0 / self.coefficient_salaire_moyen(annee_arrivee, annee_depart)

    @cached_property
    def _traitement_relatif(self) -> tuple[int, dict[int, float]]:
        """Le traitement indiciaire relatif au salaire moyen, année par année,
        de l'année de base à la fin du raccord : voir
        :meth:`traitement_indiciaire_relatif`."""
        regle = self._hypotheses.get("traitement_indiciaire")
        if not regle:
            return 0, {}
        base = int(regle["annee_base"])
        nominal, reel, raccord = regle["nominal"], regle["reel"], regle["raccord"]
        fin = int(raccord["jusqu_a"])
        relatif = {base: 1.0}
        indice = 1.0
        for annee in range(base + 1, fin + 1):
            salaire = 1.0 + self.salaire_moyen(annee)
            prix = 1.0 + self.inflation(annee)
            borne_reelle = (1.0 + float(reel["taux"])) * prix
            if int(nominal["depuis"]) <= annee <= int(nominal["jusqu_a"]):
                traitement = 1.0 + float(nominal["taux"])
            elif int(reel["depuis"]) <= annee <= int(reel["jusqu_a"]):
                traitement = borne_reelle
            elif int(raccord["depuis"]) <= annee:
                duree = fin - int(raccord["depuis"]) + 1
                part = (annee - int(raccord["depuis"]) + 1) / duree
                traitement = borne_reelle + (salaire - borne_reelle) * part
            else:
                traitement = salaire
            indice *= traitement / salaire
            relatif[annee] = indice
        passe = regle.get("passe")
        if passe:
            for annee, traitement, revenu in zip(passe["annees"], passe["traitement"],
                                                 passe["revenu_moyen"]):
                if int(annee) < base:
                    relatif[int(annee)] = float(traitement) / float(revenu)
        return base, relatif

    def traitement_indiciaire_relatif(self, annee: int) -> float:
        """Le traitement indiciaire des fonctionnaires rapporté au salaire
        moyen, 1 l'année de base (``traitement_indiciaire`` de
        ``macro/hypotheses_projection.yaml``).

        C'est la convention du COR (annexe méthodologique du rapport de juin
        2026, note 40) : le traitement croît de 0,1 % en euros courants en
        2026 et 2027, de 0,1 % en euros constants de 2028 à 2032, puis
        rejoint en cinq ans le salaire moyen, qu'il suit dès 2038. Il décroche
        donc du salaire moyen, et la part des primes monte d'autant
        (:meth:`~retraite_notionnelle.castypes.CasType.construire`). La
        dernière valeur au-delà du raccord.

        Avant l'année de base, le décrochage déjà fait (``passe``) : le
        traitement moyen rapporté au revenu moyen d'activité, que le COR publie
        de 2019 à 2024 (figure 1.14 du même rapport), le premier reconduit
        avant lui ; 1 sans ``passe`` (action 147, étape 9).
        """
        base, relatif = self._traitement_relatif
        if not relatif or annee == base:
            return 1.0
        if annee < base:
            passe = [a for a in relatif if a < base]
            if not passe:
                return 1.0
            return relatif.get(annee, relatif[min(passe)] if annee < min(passe) else 1.0)
        return relatif[min(annee, max(relatif))]

    def delai_entree_fonction_publique(self, generation: int) -> float:
        """Les années qu'un fonctionnaire de l'État né en ``generation`` passe
        sous un autre statut avant d'entrer dans le régime
        (``entree_fonction_publique`` de ``macro/hypotheses_projection.yaml``,
        action 147, étape 11).

        Deux pour la génération qui part en ce moment, d'après l'EIC 2013 que
        cite l'annexe méthodologique du COR (« un à trois ans »), huit pour la
        génération 2000, la durée de services retenue pour la proratisation
        baissant « d'environ 6 ans » (rapport de juin 2026, note 69) ; en ligne
        droite entre les points du fichier, la valeur du bord au-delà, zéro
        sans fichier. Seuls les cas types la lisent, sous les conventions du
        COR (:meth:`~retraite_notionnelle.castypes.CasType.construire`).
        """
        points = sorted((int(point["generation"]), float(point["annees"]))
                        for point in self._hypotheses.get("entree_fonction_publique") or ())
        if not points:
            return 0.0
        if generation <= points[0][0]:
            return points[0][1]
        for (debut, avant), (fin, apres) in zip(points, points[1:]):
            if generation <= fin:
                return avant + (apres - avant) * (generation - debut) / (fin - debut)
        return points[-1][1]

    def coefficient_smic(self, annee_depart: int, annee_arrivee: int) -> float:
        """Coefficient de passage par le SMIC, d'une année à l'autre.

        Plusieurs montants du droit positif ne suivent ni les prix ni les
        salaires mais **le salaire minimum de croissance** : le plafond
        d'écrêtement du minimum contributif depuis février 2014, les deux
        montants du minimum lui-même depuis la réforme du 14 avril 2023. Les
        revaloriser sur les prix, comme le faisait le modèle, les décrochait
        d'autant que le SMIC a progressé plus vite.
        """
        depart = self.smic_horaire(annee_depart)
        return self.smic_horaire(annee_arrivee) / depart if depart > 0 else 1.0

    @cached_property
    def revalorisation_portee_au_compte(self) -> list[tuple[int, int, dict[int, float]]]:
        """Colonnes de revalorisation publiées par la Cnav, par date d'effet.

        Une colonne par circulaire : année de la date d'effet, MOIS de cette
        date, et le coefficient par année de perception. Triées par date.

        Le mois n'était pas conservé — seul un drapeau disait si la date était
        le 1er janvier. Or les circulaires ne prennent pas toutes effet au
        1er janvier, et deux d'entre elles portent la même année : la
        revalorisation exceptionnelle du 1er juillet 2022 dépasse celle du
        1er janvier de 3,9 %. Sans le mois, toutes les liquidations de 2022
        lisaient la colonne de janvier, y compris celles du second semestre,
        auxquelles la caisse oppose celle de juillet.

        Le coefficient entre deux années se lit dans UNE colonne, par rapport de
        deux de ses valeurs. Une seule colonne suffirait donc en théorie ; en
        pratique la caisse arrondit sa table à trois décimales et repart chaque
        année de la précédente, si bien que reconstruire une colonne depuis une
        autre dérive avec la distance — 0,02 % à deux ans, 0,16 % à sept.
        """
        return self._colonnes_de_revalorisation("revalorisation_salaires.csv")

    @cached_property
    def revalorisation_portee_au_compte_anciennes(
            self) -> list[tuple[int, int, dict[int, float]]]:
        """Les colonnes de la Cnav d'AVANT octobre 2017, par date d'effet.

        Quatre-vingt-huit, de l'arrêté du 14 mai 1946 à la colonne d'octobre
        2015 (``revalorisation_salaires_anciennes.csv``). Elles ne servent qu'à
        la date où elles sont en vigueur
        (:meth:`colonne_de_revalorisation_en_vigueur`), jamais par rapport de
        deux de leurs valeurs : avant 1952, l'arrêté fixait un coefficient par
        année de perception, et ce rapport n'y vaut pas revalorisation.
        Jusqu'au 5 octobre 2026, le modèle reconstruisait toute liquidation
        d'avant 2017 depuis la colonne d'octobre 2017, et ``docs/limites.md``
        disait la dérive « invérifiable ».
        """
        return self._colonnes_de_revalorisation("revalorisation_salaires_anciennes.csv")

    def _colonnes_de_revalorisation(self, fichier: str
                                    ) -> list[tuple[int, int, dict[int, float]]]:
        import csv

        chemin = self.racine / "reference" / "legislation" / fichier
        if not chemin.exists():
            return []
        colonnes: dict[str, dict[int, float]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                colonnes.setdefault(ligne["date_effet"], {})[
                    int(ligne["annee_perception"])
                ] = float(ligne["coefficient"])
        return sorted(
            (int(effet[:4]), int(effet[5:7]), table)
            for effet, table in colonnes.items()
        )

    @cached_property
    def _colonnes_en_vigueur(self) -> tuple[list[tuple[int, int]],
                                            list[tuple[dict[int, float], int]]]:
        """Toutes les colonnes publiées, anciennes et récentes, triées par date
        d'effet : leurs dates, et chacune avec sa dernière année de perception."""
        toutes = sorted(self.revalorisation_portee_au_compte_anciennes
                        + self.revalorisation_portee_au_compte,
                        key=lambda colonne: (colonne[0], colonne[1]))
        return ([(annee, mois) for annee, mois, _ in toutes],
                [(table, max(table)) for _, _, table in toutes])

    def colonne_de_revalorisation_en_vigueur(
            self, annee: int, mois: int = 1) -> tuple[dict[int, float], int] | None:
        """La colonne que la caisse oppose à une liquidation du premier jour de
        ce mois, et sa dernière année de perception.

        La plus récente dont la date d'effet ne lui est pas postérieure : une
        colonne vaut jusqu'à la suivante — celle d'avril 1953 jusqu'en mars
        1955, celle d'octobre 2017 jusqu'à la fin de 2018. ``None`` avant la
        première, et après l'année de la dernière, qui ne dit rien des
        revalorisations suivantes.
        """
        dates, colonnes = self._colonnes_en_vigueur
        rang = bisect_right(dates, (annee, mois)) - 1
        if rang < 0:
            return None
        if rang == len(dates) - 1 and annee > dates[rang][0]:
            return None
        return colonnes[rang]

    def coefficient_revalorisation_portee_au_compte(self, annee_depart: int,
                                                    annee_arrivee: int,
                                                    mois_arrivee: int = 1) -> float:
        """Revalorisation d'un salaire PORTÉ AU COMPTE, telle que l'arrêté la fixe.

        C'est la grandeur qui commande le salaire annuel moyen : la moyenne
        porte sur les N MEILLEURES années, et « meilleures » se juge sur des
        salaires revalorisés — changer les coefficients ne déplace donc pas
        seulement le niveau de chaque année, cela change lesquelles sont
        retenues. Le modèle l'approchait par « les salaires jusqu'en 1986, les
        prix depuis », ce qui SUR-revalorisait les salaires anciens de 12 % sur
        quarante ans.

        Le coefficient est d'abord celui de la colonne EN VIGUEUR à la date de
        liquidation (:meth:`colonne_de_revalorisation_en_vigueur`), que la
        caisse oppose sans calcul ; depuis que le dépôt lit toutes ses
        colonnes, de 1946 à 2026, c'est le cas de toute liquidation de ces
        années-là. C'est le mois qui désigne la colonne : un départ du
        1er août 2022 relève de la circulaire du 1er juillet, un départ du
        1er mars 2022 de celle du 1er janvier, et les deux diffèrent de 3,9 %.
        Un salaire plus récent que la colonne n'a encore reçu aucune
        revalorisation : coefficient 1.

        Sinon — un salaire d'avant 1947, que les colonnes anciennes ne portent
        pas, ou une liquidation postérieure à la dernière colonne —, le rapport
        de deux valeurs de la colonne récente la plus proche
        (:meth:`coefficient_revalorisation_par_rapport`). ``docs/limites.md``
        dit ce que chacun coûte.
        """
        if annee_arrivee == annee_depart:
            return 1.0
        if annee_arrivee < annee_depart:
            return 1.0 / self.coefficient_revalorisation_portee_au_compte(
                annee_arrivee, annee_depart
            )
        en_vigueur = self.colonne_de_revalorisation_en_vigueur(annee_arrivee, mois_arrivee)
        if en_vigueur is not None:
            table, derniere = en_vigueur
            if annee_depart in table:
                return table[annee_depart]
            if annee_depart > derniere:
                return 1.0
        return self.coefficient_revalorisation_par_rapport(
            annee_depart, annee_arrivee, mois_arrivee)

    def coefficient_revalorisation_par_rapport(self, annee_depart: int,
                                               annee_arrivee: int,
                                               mois_arrivee: int = 1) -> float:
        """La revalorisation de ``annee_depart`` à ``annee_arrivee``, lue par
        RAPPORT de deux valeurs d'une colonne récente, de 2017 ou après.

        Trois chemins, du plus sûr au moins sûr :

        1. la colonne récente de l'année d'arrivée, en vigueur à son mois ;
        2. sinon la colonne récente la PLUS PROCHE, par rapport de deux de ses
           valeurs. Ancrer sur la plus proche plutôt que sur la plus récente
           réduit la dérive que les arrondis de la caisse accumulent, beaucoup
           en moyenne, deux fois au pire ;
        3. hors de toute colonne, l'ancienne approximation, ancrée sur la borne
           connue quand il y en a une.

        C'est aussi le taux annuel que lit le mode d'indexation
        ``revalorisation_portee_au_compte`` : le rapport de deux années
        consécutives. Il ne lit que les colonnes récentes, qui sont
        multiplicatives ; les anciennes ne servent qu'en vigueur.
        """
        if annee_arrivee == annee_depart:
            return 1.0
        if annee_arrivee < annee_depart:
            return 1.0 / self.coefficient_revalorisation_par_rapport(
                annee_arrivee, annee_depart
            )
        colonnes = self.revalorisation_portee_au_compte
        if not colonnes:
            return self.coefficient_revalorisation_salaires(annee_depart, annee_arrivee)

        en_vigueur = [
            table for annee, mois, table in colonnes
            if annee == annee_arrivee and mois <= mois_arrivee
            and annee_depart in table
        ]
        if en_vigueur:
            return en_vigueur[-1][annee_depart]

        # La colonne la plus proche qui porte les deux années. Une colonne dont
        # la date d'effet est POSTÉRIEURE à la liquidation ne peut pas servir
        # pour l'année de celle-ci : son millésime porte déjà une revalorisation
        # que l'assuré n'a pas connue.
        candidates = [
            (abs(annee - annee_arrivee), table)
            for annee, mois, table in colonnes
            if annee_depart in table and annee_arrivee in table
            and (annee != annee_arrivee or mois <= mois_arrivee)
        ]
        if candidates:
            _, table = min(candidates, key=lambda c: c[0])
            return table[annee_depart] / table[annee_arrivee]

        # Au-delà de la dernière colonne, on ANCRE sur elle et on n'approche que
        # le bout du chemin : une liquidation en 2030 lit les circulaires
        # jusqu'en 2026 et n'approche que quatre années, au lieu de tout
        # approcher. En deçà de la première année publiée, il n'y a rien sur
        # quoi ancrer.
        derniere, _, table = colonnes[-1]
        if annee_arrivee > derniere and annee_depart in table:
            return table[annee_depart] * self.coefficient_revalorisation_salaires(
                derniere, annee_arrivee
            )
        return self.coefficient_revalorisation_salaires(annee_depart, annee_arrivee)

    @cached_property
    def derniere_liquidation_revalorisee(self) -> int | None:
        """Dernière année de liquidation que les circulaires publiées couvrent."""
        colonnes = self.revalorisation_portee_au_compte
        return colonnes[-1][0] if colonnes else None

    def coefficient_revalorisation_salaires(self, annee_depart: int,
                                            annee_arrivee: int) -> float:
        """Revalorisation d'un salaire porté au compte, de ``annee_depart`` à
        ``annee_arrivee``.

        Ce n'est pas l'indice des prix. Les salaires inscrits au compte d'un
        assuré sont revalorisés chaque année par un coefficient fixé par
        arrêté, et cet arrêté n'a pas toujours suivi les prix : jusqu'au milieu
        des années 1980, il suivait **l'évolution des salaires**. La bascule
        date de 1987, la loi du 22 juillet 1993 l'ayant ensuite inscrite dans
        la loi et rattachée à l'indice des prix hors tabac.

        L'écart n'est pas un détail de méthode. Sur les Trente Glorieuses, les
        salaires ont crû nettement plus vite que les prix : appliquer la règle
        des prix à ces années-là, comme le faisait le modèle, ramenait au
        compte des salaires anciens très en dessous de ce que le droit y a
        réellement inscrit, et minorait d'autant le salaire de référence des
        carrières commencées avant 1987.

        **Cette règle n'est plus qu'un REPLI.** Les coefficients des arrêtés
        eux-mêmes sont désormais dans le dépôt, et
        :meth:`coefficient_revalorisation_portee_au_compte` les sert là où ils
        existent — c'est-à-dire partout où le salaire de référence est calculé
        sur des années réellement portées au compte. Cette approximation ne vaut
        plus que hors de leur plage, et pour les régimes qui ne portent pas de
        salaire à un compte.
        """
        if annee_arrivee == annee_depart:
            return 1.0
        if annee_arrivee < annee_depart:
            return 1.0 / self.coefficient_revalorisation_salaires(
                annee_arrivee, annee_depart
            )
        coefficient = 1.0
        for annee in range(annee_depart + 1, annee_arrivee + 1):
            if annee >= ANNEE_REVALORISATION_SUR_LES_PRIX:
                coefficient *= 1 + self.inflation(annee)
            else:
                coefficient *= 1 + self.salaire_moyen(annee)
        return coefficient

    def fiabilite_sur(self, debut: int, fin: int) -> Fiabilite:
        """Fiabilité du maillon le plus faible des séries macro sur la plage."""
        return min(
            self.inflation.fiabilite_minimale_sur(debut, fin),
            self.salaire_moyen.fiabilite_minimale_sur(debut, fin),
            self.productivite.fiabilite_minimale_sur(debut, fin),
        )
