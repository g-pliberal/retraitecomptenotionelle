"""La pyramide des âges : combien de gens, à quel âge, quelle année.

C'est la pièce que `docs/limites.md` déclarait manquante. Sans elle, passer d'un
droit individuel à un coût collectif obligeait à supposer toutes les générations
de même taille — ce que le baby-boom dément d'un tiers, et ce qui interdisait
purement et simplement de projeter.

Une seule source, et une seule méthodologie de part et d'autre de la frontière :
le scénario central des **projections de population 2026** de l'INSEE, dont
l'onglet ``population`` porte l'effectif au 1er janvier par âge détaillé et par
année, de 1962 à 2070. L'INSEE date lui-même la frontière — estimations jusqu'en
2023, projections ensuite — et le dépôt la reprend telle quelle : ce qui est
projeté entre au niveau ``estimee``, et cette fiabilité se propage jusqu'au
résultat affiché.

Deux séries en sont tirées, qui ne servent pas à la même chose :

* ``effectif(age, annee)`` compte des **retraités** — d'où le plancher à 48 ans,
  en deçà duquel aucune pension de droit direct n'est servie ;
* ``actifs(annee)`` compte les **20-64 ans**, et ne sert qu'à projeter le
  dénominateur d'une part de PIB.

La pyramide s'arrête en 2070, et cette borne REFUSE plutôt qu'elle n'emprunte :
``_annee_bornee`` dit pourquoi, et ce que le refus a coûté d'apprendre.

Sous l'hypothèse d'espérance de vie basse ou haute
(``Parametres.hypothese_esperance_vie``, action 138, étape 7), les deux séries
sont, à partir de 2026, celles des scénarios « espérance de vie basse » et
« haute » de l'INSEE (``population_par_age_variantes.csv``,
``population_active_variantes.csv``) : la page Coût compte alors ses retraités
sous la mortalité que lisent ses diviseurs et ses survies de cohortes.

Sous une variante de fécondité ou de migrations (``demographie``, même étape),
que seule la page Coût lit — elles ne touchent pas le diviseur —, les 20-64 ans
sont ceux du scénario de l'INSEE ; sous les migrations, la pyramide aussi, et
les arrivées tardives (:class:`ArriveesTardives`). La pyramide des 48 ans et
plus de la fécondité est celle du central : ses naissances n'ont pas 48 ans en
2070. L'INSEE ne publie pas de scénario qui croise deux composantes : une
variante démographique sous une hypothèse d'espérance de vie autre que la
centrale est refusée.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import (Fiabilite, SerieAnnuelle, charger_serie_annuelle,
                         charger_table_par_generation, valeur_par_generation)
from ..somme import somme_ordonnee

#: Âge plancher de la série, et donc âge en deçà duquel ``effectif`` rend zéro.
#: Le cas type qui liquide le plus tôt, le militaire radié à 48 ans et demi
#: (action 152), part l'année de ses 48 ans. À 50 ans, jusqu'au 24 octobre
#: 2026, le plancher lui retirait ses deux premières années de pension
#: (action 138, étape 3).
AGE_MINIMAL = 48

#: Les hypothèses d'espérance de vie dont la pyramide est publiée, celles de
#: ``Parametres.hypothese_esperance_vie``.
HYPOTHESES_ESPERANCE_VIE = ("centrale", "basse", "haute")

#: Les variantes de fécondité et de migrations dont la pyramide est publiée,
#: celles de ``Population(demographie=...)``.
VARIANTES_DEMOGRAPHIQUES = ("centrale", "fecondite_basse", "fecondite_haute",
                            "migrations_basse", "migrations_haute")

#: Les variantes dont les 50 ans et plus ne sont pas ceux du central.
_AVEC_PYRAMIDE = ("migrations_basse", "migrations_haute")


def verifier_demographie(hypothese_esperance_vie: str, demographie: str) -> None:
    """Refuse une variante inconnue, ou deux composantes croisées, que
    l'INSEE ne publie pas."""
    if hypothese_esperance_vie not in HYPOTHESES_ESPERANCE_VIE:
        raise ValueError(
            f"hypothèse d'espérance de vie inconnue : {hypothese_esperance_vie!r} "
            f"(attendu : {HYPOTHESES_ESPERANCE_VIE})")
    if demographie not in VARIANTES_DEMOGRAPHIQUES:
        raise ValueError(
            f"variante démographique inconnue : {demographie!r} "
            f"(attendu : {VARIANTES_DEMOGRAPHIQUES})")
    if demographie != "centrale" and hypothese_esperance_vie != "centrale":
        raise ValueError(
            f"variante {demographie!r} sous l'espérance de vie "
            f"{hypothese_esperance_vie!r} : l'INSEE ne publie que des scénarios "
            "qui ne diffèrent du central que par une composante")


class Population:
    """Effectifs par âge et par année, observés puis projetés, sous une
    hypothèse d'espérance de vie et une variante de fécondité ou de
    migrations (``centrale`` par défaut, l'une et l'autre)."""

    def __init__(self, racine: Path, hypothese_esperance_vie: str = "centrale",
                 demographie: str = "centrale") -> None:
        verifier_demographie(hypothese_esperance_vie, demographie)
        self.hypothese_esperance_vie = hypothese_esperance_vie
        self.demographie = demographie
        macro = racine / "reference" / "macro"
        self._effectifs: dict[int, dict[int, float]] = {}
        self._fiabilites: dict[int, Fiabilite] = {}
        chemin = macro / "population_par_age.csv"
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee, age = int(ligne["annee"]), int(ligne["age"])
                self._effectifs.setdefault(annee, {})[age] = float(ligne["effectif"])
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = self._fiabilites.get(annee)
                self._fiabilites[annee] = (
                    niveau if courante is None else min(courante, niveau)
                )
        if not self._effectifs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")

        self.actifs: SerieAnnuelle = charger_serie_annuelle(
            macro / "population_active.csv", "effectif", nom="population_active"
        )
        self._actifs_centraux = self.actifs
        if hypothese_esperance_vie != "centrale":
            self._lire_variante(macro, hypothese_esperance_vie)
        elif demographie != "centrale":
            self._lire_variante(macro, demographie,
                                pyramide=demographie in _AVEC_PYRAMIDE)
        self._annees = sorted(self._effectifs)
        self.premiere_annee = self._annees[0]
        self.derniere_annee = self._annees[-1]
        self.age_maximal = max(
            age for effectifs in self._effectifs.values() for age in effectifs
        )

    @property
    def variante(self) -> str:
        """La variante de la pyramide : ``centrale``, une hypothèse
        d'espérance de vie ou une variante démographique."""
        if self.hypothese_esperance_vie != "centrale":
            return f"esperance_vie_{self.hypothese_esperance_vie}"
        return self.demographie

    def _lire_variante(self, macro: Path, hypothese: str, pyramide: bool = True) -> None:
        """Les années que la variante publie remplacent celles du central,
        âge par âge : toutes celles d'après 2025. Une variante absente est
        refusée, plutôt que de compter sous le central les retraités d'un
        diviseur qui suit la variante. Sans ``pyramide`` — la fécondité —,
        seuls les 20-64 ans sont remplacés."""
        chemin = macro / "population_par_age_variantes.csv"
        remplacees: dict[int, dict[int, float]] = {}
        if pyramide and chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    if ligne["hypothese"] != hypothese:
                        continue
                    annee, age = int(ligne["annee"]), int(ligne["age"])
                    remplacees.setdefault(annee, {})[age] = float(ligne["effectif"])
                    niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                    self._fiabilites[annee] = min(self._fiabilites.get(annee, niveau),
                                                  niveau)
        if pyramide and not remplacees:
            raise ValueError(
                f"aucune pyramide sous l'hypothèse {hypothese!r} dans {chemin}")
        self._effectifs.update(remplacees)
        chemin_actifs = macro / "population_active_variantes.csv"
        variante = charger_serie_annuelle(
            chemin_actifs, "effectif", nom=f"population_active_{hypothese}",
            filtre={"hypothese": hypothese})
        if pyramide and set(variante.annees()) != set(remplacees):
            raise ValueError(
                f"{chemin_actifs} ne couvre pas les années de la pyramide "
                f"{hypothese!r}")
        valeurs = {annee: self.actifs.brut(annee) for annee in self.actifs.annees()
                   if annee < variante.premiere_annee}
        valeurs.update({annee: variante.brut(annee) for annee in variante.annees()})
        self.actifs = SerieAnnuelle(valeurs, f"population_active_{hypothese}")

    def actifs_centraux(self, annee: int) -> float:
        """Les 20-64 ans du central, quelle que soit la variante : ce à quoi
        :meth:`facteur_actifs` les rapporte."""
        return self._actifs_centraux(annee)

    def facteur_actifs(self, annee: int) -> float:
        """Les 20-64 ans de la variante, rapportés à ceux du central : un sous
        le central, et jusqu'en 2025 sous toutes les variantes. La page Coût
        en multiplie le PIB, projeté sur l'emploi du COR, qui suit le central
        (``cout.AvenirAnnuel.facteur_pib``)."""
        if self.variante == "centrale":
            return 1.0
        return self.actifs(annee) / self.actifs_centraux(annee)

    def verifier_hypothese(self, hypothese_esperance_vie: str) -> None:
        """Refuse une pyramide d'une autre hypothèse d'espérance de vie que
        celle du simulateur : ses retraités mourraient d'une table, ses
        diviseurs et ses survies de cohortes d'une autre."""
        if hypothese_esperance_vie != self.hypothese_esperance_vie:
            raise ValueError(
                f"pyramide de l'hypothèse d'espérance de vie "
                f"{self.hypothese_esperance_vie!r}, simulateur sous "
                f"{hypothese_esperance_vie!r} : construire la population par "
                f"Population(racine, parametres.hypothese_esperance_vie)")

    # -- accès ---------------------------------------------------------------

    def _annee_bornee(self, annee: int) -> int:
        """Année ramenée dans la plage publiée, et la borne haute REFUSE.

        EN DEÇÀ, ON EMPRUNTE. La série commence en 1962, la dépense observée en
        1959 : les trois premières années empruntent la pyramide de 1962. C'est
        une approximation assumée, et elle porte sur trois années dont la
        dépense pèse un demi pour cent de celle d'aujourd'hui.

        AU-DELÀ, ON REFUSE, et l'asymétrie est le sujet de cette méthode.
        Emprunter la pyramide de 2070 pour 2085 ne décale pas une population de
        quinze ans : cela rend, sous le nom des 85 ans de 2085, l'effectif des
        85 ans de 2070, qui sont nés quinze ans plus tôt et qui seront morts.
        Une pyramide s'indexe par ÂGE, et reconduire un âge d'une année à
        l'autre change de cohorte — là où reconduire la valeur de bord d'une
        série annuelle, ce que fait ``SerieAnnuelle``, ne change rien qu'un
        niveau.

        Le refus est d'autant plus nécessaire que le chiffre emprunté est
        PLAUSIBLE : il a le bon ordre de grandeur, et rien ne le signale. Le
        20 septembre 2026, il a fait tomber l'engagement acquis du dépôt de 579
        à 478 % du PIB ; c'est une incohérence interne — la part extrapolée
        dépassait le total — qui l'a trahi, et non le chiffre lui-même.

        CE MOTIF N'EST PAS NEUF DANS LE DÉPÔT. ``StructureFinancement`` refuse
        de la même façon, et depuis plus longtemps : le classeur du COR ne
        publie la ventilation qu'à six dates, et « interpoler une structure de
        financement entre 2030 et 2040 reviendrait à inventer une trajectoire
        que personne n'a calculée ». Sa ``KeyError`` nomme les années
        disponibles ; c'est le modèle suivi ici.

        CE QU'IL FAUT FAIRE À LA PLACE. Une cohorte DÉJÀ NÉE se prolonge par sa
        propre survie : effectif à l'âge ``a + k`` en ``T + k`` égale effectif à
        l'âge ``a`` en ``T`` multiplié par la survie de cette cohorte-là. Le
        dépôt porte la table qu'il faut, et ``cout._courbes_survie`` fait
        exactement ce geste, avec la table unisexe qui sert déjà de diviseur aux
        comptes notionnels.
        """
        if annee > self.derniere_annee:
            raise ValueError(
                f"pyramide des âges demandée en {annee}, au-delà de "
                f"{self.derniere_annee} que l'INSEE projette. Emprunter la "
                f"dernière pyramide changerait de cohorte sans le dire : une "
                f"cohorte déjà née se prolonge par sa propre survie, voir "
                f"cout._courbes_survie."
            )
        return max(annee, self.premiere_annee)

    def effectif(self, age: int, annee: int) -> float:
        """Effectif d'un âge une année donnée ; zéro hors de la plage d'âges.

        Refuse au-delà de la dernière année projetée : voir ``_annee_bornee``.
        """
        return self._effectifs[self._annee_bornee(annee)].get(age, 0.0)

    def effectif_tranche(self, age_debut: int, age_fin: int, annee: int) -> float:
        """Effectif cumulé d'une tranche d'âges, bornes comprises."""
        effectifs = self._effectifs[self._annee_bornee(annee)]
        return somme_ordonnee(
            effectifs.get(age, 0.0) for age in range(age_debut, age_fin + 1)
        )

    def fiabilite(self, annee: int) -> Fiabilite:
        """Fiabilité de la pyramide d'une année.

        Hors de la plage publiée, la valeur est empruntée : elle ne peut donc
        pas valoir mieux qu'``estimee``.
        """
        if annee < self.premiere_annee or annee > self.derniere_annee:
            return Fiabilite.ESTIMEE
        return self._fiabilites[annee]

    def annees(self) -> list[int]:
        return list(self._annees)


class ArriveesTardives:
    """Ce que les arrivées après 21 ans retirent à la pension d'une génération.

    La pyramide compte des résidents, et la grille sert à chacun la pension
    d'une carrière française complète. Or une génération gagne, à l'âge
    adulte, des résidents arrivés tard, dont la carrière française est
    courte. ``arrivees_tardives.csv`` en tire, génération par génération et
    du même classeur de l'INSEE, la part de la pension d'une carrière complète
    qui lui manque à 64 ans (action 147, étape 11 ; l'en-tête du fichier dit
    comment). La page Coût multiplie par :meth:`completude` la masse de
    pensions de chaque génération, et non ses têtes : un arrivé tard est un
    retraité, à la pension plus courte.

    La série va de 1941, première génération dont la carrière commence dans la
    pyramide, à 2005, qui a 64 ans en 2070 ; en deçà et au-delà, la génération
    prend la valeur du bord.

    Sous une variante de migrations (``demographie``), le manque est celui que
    le classeur de la variante donne (``arrivees_tardives_variantes.csv``) ;
    sous toute autre, celui du central.
    """

    def __init__(self, racine: Path, demographie: str = "centrale") -> None:
        verifier_demographie("centrale", demographie)
        macro = racine / "reference" / "macro"
        propre = demographie in _AVEC_PYRAMIDE
        chemin = macro / ("arrivees_tardives_variantes.csv" if propre
                          else "arrivees_tardives.csv")
        self._manques: dict[int, float] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                if ligne["mesure"] == "manque" and (
                        not propre or ligne["hypothese"] == demographie):
                    self._manques[int(ligne["generation"])] = float(ligne["valeur"])
        if not self._manques:
            raise ValueError(f"aucun manque sous {demographie!r} dans {chemin}")
        self.premiere_generation = min(self._manques)
        self.derniere_generation = max(self._manques)

    def completude(self, generation: int) -> float:
        """La part de la pension d'une carrière complète que touche, en
        moyenne, la génération ``generation``."""
        bornee = min(max(generation, self.premiere_generation), self.derniere_generation)
        return 1.0 - self._manques[bornee]


class CarrieresIncompletes:
    """La part de la pension d'une carrière de la grille que touche, en
    moyenne, une génération : ses arrivées tardives et les carrières
    incomplètes de ses natifs (action 147, étapes 11 et 14).

    La grille fait partir chacune de ses carrières au taux plein, avec la durée
    requise de sa génération (``duree_assurance_requise.csv``). Les retraités
    de droit direct d'une génération résidant en France en ont validé, en
    moyenne, ce que publie le COR (figure 3.22 du rapport de juin 2026,
    ``duree_assurance_generations.csv``, moyenne des deux sexes, une
    génération que la figure laisse vide prenant la moyenne de ses voisines) :
    la complétude de la génération est cette durée rapportée à sa durée
    requise. Elle porte déjà les arrivées tardives, que la pyramide compte et
    que :class:`ArriveesTardives` mesure ; le reste, :meth:`natifs`, est la
    part des carrières des natifs — courtes chez les femmes nées vers 1940,
    plus longues que la durée requise de 1950 à 1965, de plus en plus courtes
    ensuite, entrées plus tard dans la vie active sous une durée requise qui
    s'allonge.

    Comme celle des arrivées, la complétude pèse les MASSES de chaque
    génération, non ses têtes, et suppose la pension proportionnelle à la
    durée : une borne, la décote coûtant davantage, la complémentaire juste
    autant. En deçà de la première génération que publie le COR et au-delà de
    la dernière, le facteur des natifs est celui du bord ; celui des arrivées
    garde le sien.
    """

    def __init__(self, racine: Path, demographie: str = "centrale") -> None:
        chemin = racine / "reference" / "macro" / "duree_assurance_generations.csv"
        par_sexe: dict[str, dict[int, float]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                par_sexe.setdefault(ligne["sexe"], {})[int(ligne["generation"])] = float(
                    ligne["trimestres"])
        if sorted(par_sexe) != ["femmes", "hommes"]:
            raise ValueError(f"{chemin} : les durées des femmes et des hommes, attendues")
        requises, generations_requises = charger_table_par_generation(
            racine / "reference" / "legislation" / "duree_assurance_requise.csv",
            "trimestres")
        # Les durées du COR comptent les arrivées du central : le facteur des
        # natifs s'en tire, et la variante de migrations ne change que celui
        # des arrivées.
        centrales = ArriveesTardives(racine)
        self.arrivees = ArriveesTardives(racine, demographie)
        premiere = max(min(serie) for serie in par_sexe.values())
        derniere = min(max(serie) for serie in par_sexe.values())
        #: Le facteur des natifs, génération par génération, sur celles que
        #: le COR publie.
        self._natifs: dict[int, float] = {}
        for generation in range(premiere, derniere + 1):
            duree = somme_ordonnee(_interpolee(serie, generation) for serie in par_sexe.values()) / 2
            requise = valeur_par_generation(requises, generations_requises, generation)
            if requise is None:
                raise ValueError(f"aucune durée requise pour la génération {generation}")
            self._natifs[generation] = (
                duree / requise[0] / centrales.completude(generation))
        self.premiere_generation = min(premiere, self.arrivees.premiere_generation)
        self.derniere_generation = max(derniere, self.arrivees.derniere_generation)

    def natifs(self, generation: int) -> float:
        """La durée validée des natifs de la génération, rapportée à sa durée
        requise : le facteur que les carrières incomplètes des natifs
        ajoutent à celui des arrivées."""
        bornee = min(max(generation, min(self._natifs)), max(self._natifs))
        return self._natifs[bornee]

    def completude(self, generation: int) -> float:
        """La part de la pension d'une carrière de la grille que touche, en
        moyenne, la génération ``generation``."""
        return self.arrivees.completude(generation) * self.natifs(generation)


def _interpolee(serie: dict[int, float], generation: int) -> float:
    """La valeur de la génération, ou, quand la série la laisse vide, celle que
    donne la droite entre ses deux voisines."""
    if generation in serie:
        return serie[generation]
    avant = max(g for g in serie if g < generation)
    apres = min(g for g in serie if g > generation)
    return serie[avant] + (serie[apres] - serie[avant]) * (generation - avant) / (apres - avant)
