"""Combien de retraités touchent combien : la distribution des pensions.

Le modèle calcule des pensions individuelles et les agrège par cas types. Cela
suffit à comparer des systèmes — un rapport de masses est robuste — mais pas à
chiffrer un PLANCHER. Une allocation différentielle ne coûte que ce que coûte la
queue basse de la distribution, et treize carrières de référence ne la décrivent
pas : la page « Coût » voit la garantie vieillesse du scénario 6 par les seuls
cas types qui liquident à 65 ans ou après — cinq sur treize aux générations
récentes, aucun aux plus anciennes.

L'échantillon interrégimes de retraités de la DREES apparie tous les quatre ans
les fichiers de toutes les caisses sur un même échantillon d'individus. C'est la
seule source française qui publie la répartition — par tranches de cent euros —
et non la seule moyenne d'un régime.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path

from .chargement import Fiabilite

#: Les quantiles que la DREES publie de la pension de droit direct, sous le
#: code du fichier de résidence et leur rang.
QUANTILES_PUBLIES: tuple[tuple[str, float], ...] = (
    ("d1", 0.10), ("d2", 0.20), ("q1", 0.25), ("d3", 0.30), ("d4", 0.40),
    ("mediane", 0.50), ("d6", 0.60), ("d7", 0.70), ("q3", 0.75), ("d8", 0.80),
    ("d9", 0.90),
)

#: Les deux lectures de la distribution. ``tous`` est le tableau de l'enquête,
#: tel quel ; ``france`` en retire les retraités qui résident à l'étranger.
RESIDENCES = ("tous", "france")


class ResidenceRetraites:
    """Les retraités selon leur lieu de résidence, pour un millésime d'EIR.

    Trois colonnes — ``etranger``, ``france``, ``ensemble`` — et, dans
    chacune, l'effectif, les deux pensions moyennes de droit direct et les
    onze quantiles publiés de la seconde, par sexe.
    """

    def __init__(self, racine: Path, millesime: int | None = None) -> None:
        chemin = racine / "reference" / "macro" / "pensions_residence.csv"
        valeurs: dict[int, dict[tuple[str, str, str], float]] = {}
        fiabilites: dict[int, Fiabilite] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee = int(ligne["annee"])
                valeurs.setdefault(annee, {})[
                    (ligne["residence"], ligne["indicateur"], ligne["sexe"])
                ] = float(ligne["valeur"])
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = fiabilites.get(annee)
                fiabilites[annee] = niveau if courante is None else min(courante, niveau)
        if not valeurs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")
        self.millesime = max(valeurs) if millesime is None else millesime
        if self.millesime not in valeurs:
            raise KeyError(f"millésime absent de {chemin.name} : {self.millesime}")
        self._valeurs = valeurs[self.millesime]
        self.fiabilite = fiabilites[self.millesime]

    def valeur(self, residence: str, indicateur: str, sexe: str) -> float:
        return self._valeurs[(residence, indicateur, sexe)]

    def repartition_etranger(self, sexe: str) -> tuple[list[float], list[float]]:
        """La répartition des pensions des résidents à l'étranger, en points.

        Linéaire entre deux quantiles publiés, de zéro au premier décile. Au-delà
        du neuvième, la borne haute est celle qui redonne la moyenne publiée :
        c'est tout ce que l'enquête dit de la queue.

        LA GRANDEUR EST CELLE DU TABLEAU DE LA DISTRIBUTION, et ce n'est pas
        celle des quantiles. Ceux-ci décrivent la pension de droit direct
        « dont les majorations pour enfants » ; la moyenne du tableau de la
        distribution — 1 432 € en 2020 — est celle de la « pension de retraite
        de droit direct », 1 435 €, et non celle-là, 1 476 €. Les quantiles
        sont donc ramenés à la première par le rapport des deux moyennes. Le
        contrôle le justifie : les déciles des résidents en France que la
        soustraction produit retombent à une vingtaine d'euros près sur ceux
        que la DREES publie, là où ils s'en écartaient de 2 à 3 % sans lui.
        """
        moyenne = self.valeur("etranger", "pension_droit_direct", sexe)
        echelle = moyenne / self.valeur("etranger", "pension_droit_direct_majorations", sexe)
        points = [0.0] + [self.valeur("etranger", code, sexe) * echelle
                          for code, _ in QUANTILES_PUBLIES]
        rangs = [0.0] + [rang for _, rang in QUANTILES_PUBLIES]
        fixe = sum((rangs[i + 1] - rangs[i]) * (points[i] + points[i + 1]) / 2.0
                   for i in range(len(points) - 1))
        haut = 2.0 * (moyenne - fixe) / (1.0 - rangs[-1]) - points[-1]
        if haut <= points[-1]:
            raise ValueError(f"moyenne de l'étranger incompatible avec ses déciles ({sexe})")
        return points + [haut], rangs + [1.0]


def _rang(points: list[float], rangs: list[float], montant: float) -> float:
    """La fonction de répartition linéaire par morceaux, en un montant."""
    if montant <= points[0]:
        return 0.0
    for i in range(len(points) - 1):
        if montant <= points[i + 1]:
            return rangs[i] + (rangs[i + 1] - rangs[i]) * (
                (montant - points[i]) / (points[i + 1] - points[i]))
    return 1.0


@dataclass(frozen=True)
class Tranche:
    """Une tranche de cent euros de pension mensuelle, et ce qu'elle pèse."""

    #: Borne inférieure, en euros par mois de l'année de l'enquête.
    borne_inferieure: float
    #: Borne supérieure ; ``None`` pour la dernière, que l'enquête laisse ouverte.
    borne_superieure: float | None
    #: Part des retraités qui tombent dans la tranche, en FRACTION et non en
    #: pour cent — le fichier est en pour cent, la conversion est faite ici.
    part: float

    @property
    def ouverte(self) -> bool:
        return self.borne_superieure is None


class DistributionPensions:
    """Répartition des pensions brutes de droit direct, pour un millésime d'EIR.

    Le millésime le plus récent est retenu par défaut : chaque enquête décrit un
    état de la population à sa date, et elles ne se complètent pas — elles se
    remplacent.
    """

    def __init__(self, racine: Path, sexe: str = "ensemble",
                 millesime: int | None = None, residence: str = "tous") -> None:
        if residence not in RESIDENCES:
            raise ValueError(f"résidence inconnue : {residence!r}")
        chemin = racine / "reference" / "macro" / "distribution_pensions.csv"
        parts: dict[int, dict[float, float]] = {}
        fiabilites: dict[int, Fiabilite] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                if ligne["sexe"] != sexe:
                    continue
                annee = int(ligne["annee"])
                parts.setdefault(annee, {})[float(ligne["borne_mensuelle"])] = (
                    float(ligne["part_pct"]) / 100.0
                )
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = fiabilites.get(annee)
                fiabilites[annee] = (
                    niveau if courante is None else min(courante, niveau)
                )
        if not parts:
            raise ValueError(f"aucune ligne exploitable dans {chemin} (sexe={sexe!r})")

        self.sexe = sexe
        self.millesime = max(parts) if millesime is None else millesime
        if self.millesime not in parts:
            raise KeyError(f"millésime absent de {chemin.name} : {self.millesime}")
        self.fiabilite = fiabilites[self.millesime]

        bornes = sorted(parts[self.millesime])
        self.tranches: tuple[Tranche, ...] = tuple(
            Tranche(
                borne_inferieure=borne,
                borne_superieure=bornes[rang + 1] if rang + 1 < len(bornes) else None,
                part=parts[self.millesime][borne],
            )
            for rang, borne in enumerate(bornes)
        )
        #: Ce que la distribution décrit, sur les retraités de l'enquête : un
        #: pour le tableau tel quel, la part des résidents en France sinon.
        self.residence = residence
        self.part_residents = 1.0
        if residence == "france":
            self._garder_les_residents(racine)

    def _garder_les_residents(self, racine: Path) -> None:
        """Retire du tableau les retraités qui résident à l'étranger.

        LA GARANTIE NE LES SERT PAS. Elle remplace l'ASPA, et en garde la
        condition de résidence stable et régulière en France (article
        L. 815-1). Or le tableau de la distribution les compte — sa note dit
        « résidants en France ou à l'étranger » —, et ils pèsent sur la queue
        basse plus que partout : 5,5 % des retraités en 2020, mais une pension
        française moyenne de 437 € brut par mois, leur carrière française ayant
        été courte. Le coût de la garantie les servait jusqu'au 23 septembre
        2026, et s'en trouvait gonflé d'un sixième environ.

        L'enquête ne publie pas la distribution par tranches des résidents ;
        elle publie leur effectif et leurs quantiles, et ceux des résidents à
        l'étranger. On retire donc de chaque tranche ce que la répartition des
        seconds y met — linéaire entre deux quantiles, calée sur leur moyenne
        au-delà du neuvième décile —, et le contrôle est externe : les déciles
        des résidents en France que cette soustraction produit sont ceux que
        la DREES publie, à une vingtaine d'euros près.
        """
        residence = ResidenceRetraites(racine, self.millesime)
        sexe = self.sexe
        etranger = residence.valeur("etranger", "effectifs", sexe)
        tous = residence.valeur("ensemble", "effectifs", sexe)
        points, rangs = residence.repartition_etranger(sexe)
        comptes = []
        for tranche in self.tranches:
            haut = (1.0 if tranche.borne_superieure is None
                    else _rang(points, rangs, tranche.borne_superieure))
            partis = etranger * (haut - _rang(points, rangs, tranche.borne_inferieure))
            comptes.append(max(0.0, tranche.part * tous - partis))
        total = sum(comptes)
        self.tranches = tuple(replace(tranche, part=compte / total)
                              for tranche, compte in zip(self.tranches, comptes))
        self.part_residents = residence.valeur("france", "effectifs", sexe) / tous
        #: La part des femmes parmi les résidents : celle que la garantie pèse.
        self.part_femmes_residents = (
            residence.valeur("france", "effectifs", "F")
            / residence.valeur("france", "effectifs", "ensemble"))
        self.fiabilite = min(self.fiabilite, residence.fiabilite, Fiabilite.HAUTE)

    def part_sous(self, montant_mensuel: float) -> float:
        """La part des retraités dont la pension est inférieure à un montant,
        en euros du millésime : le rang d'une pension parmi les retraités.

        Linéaire à l'intérieur d'une tranche de cent euros. Dans la dernière,
        ouverte, le rang est celui de son seuil : au-delà, la distribution ne
        dit plus rien, et personne ne saurait dire si 6 000 € est au-dessus
        de 5 000. Vaut zéro sous la première borne, un au-dessus de la dernière
        tranche fermée plus sa part.
        """
        cumul = 0.0
        for tranche in self.tranches:
            if montant_mensuel < tranche.borne_inferieure:
                return cumul
            if tranche.borne_superieure is None or montant_mensuel < tranche.borne_superieure:
                if tranche.borne_superieure is None:
                    return cumul
                largeur = tranche.borne_superieure - tranche.borne_inferieure
                return cumul + tranche.part * (montant_mensuel - tranche.borne_inferieure) / largeur
            cumul += tranche.part
        return cumul

    @property
    def somme_des_parts(self) -> float:
        """Doit valoir un, aux arrondis de publication près.

        La DREES publie ses parts arrondies au centième de point : leur somme
        vaut 100,01 % et non 100 %. L'écart est réel, il ne se corrige pas —
        redresser les parts reviendrait à inventer une précision que la source
        ne donne pas — et il est trop petit pour peser sur quoi que ce soit.
        """
        return sum(tranche.part for tranche in self.tranches)


def part_femmes(racine: Path, millesime: int | None = None,
                tolerance: float = 5e-4) -> float:
    """La part des femmes dans la population que l'enquête décrit, lue sur elle.

    POURQUOI ELLE NE SE DEVINE PAS AILLEURS. Chiffrer la garantie par sexe
    demande de peser les deux distributions l'une par rapport à l'autre, et le
    dépôt ne porte aucun effectif de retraités par sexe : ni la pyramide des
    âges de l'INSEE, qui ignore la retraite, ni les effectifs de la DREES, qui
    ignorent le sexe. Le modèle prenait donc les courbes de survie à 65 ans et
    en tirait, en population stationnaire, une part de femmes parmi les 65 ans
    et plus — 56,0 %.

    ELLE SE LIT POURTANT DANS LE FICHIER, et exactement. L'enquête publie TROIS
    colonnes — les femmes, les hommes, et l'ensemble — et la troisième est le
    mélange des deux premières : il existe un poids, et un seul, tel que
    ``w·F + (1−w)·H`` redonne l'ensemble, tranche par tranche. Ce poids EST la
    part des femmes dans la population de l'enquête. Les quarante-six tranches
    de 2020 le donnent toutes entre 0,52 et 0,53, l'écart étant celui de
    l'arrondi au centième de point de la publication ; les moindres carrés le
    fixent à **52,8 %**.

    ET L'ÉCART COMPTAIT. Peser les sexes à 56,0 % quand l'enquête dit 52,8 %
    faisait dire au modèle deux choses différentes sur la même population :
    58,99 % de retraités sous le plancher majoré aux pensions du scénario 6 en
    recomposant les deux sexes, 58,03 % en lisant directement la colonne
    « ensemble », qui est celle dont le coût est tiré. C'est cette
    contradiction que ``tolerance`` interdit désormais — et non la valeur du
    poids, qui n'est le sujet d'aucune hypothèse une fois le fichier lu.

    ``tolerance`` borne le résidu du mélange, en fraction : 5·10⁻⁴ est cinq
    fois l'arrondi de la source, assez large pour l'absorber et assez étroit
    pour refuser un fichier dont les trois colonnes ne se répondraient plus.
    """
    colonnes = {
        sexe: DistributionPensions(racine, sexe=sexe, millesime=millesime)
        for sexe in ("F", "H", "ensemble")
    }
    femmes, hommes, ensemble = (
        [tranche.part for tranche in colonnes[sexe].tranches]
        for sexe in ("F", "H", "ensemble")
    )
    if not (len(femmes) == len(hommes) == len(ensemble)):
        raise ValueError(
            "les trois colonnes de la distribution n'ont pas le même découpage"
        )
    # Moindres carrés sur le seul inconnu : le poids qui mélange les deux sexes.
    numerateur = sum((e - h) * (f - h)
                     for e, f, h in zip(ensemble, femmes, hommes))
    denominateur = sum((f - h) ** 2 for f, h in zip(femmes, hommes))
    if denominateur <= 0.0:
        raise ValueError(
            "les distributions des deux sexes sont identiques : aucun poids "
            "ne s'en déduit"
        )
    poids = numerateur / denominateur
    residu = max(abs(poids * f + (1.0 - poids) * h - e)
                 for e, f, h in zip(ensemble, femmes, hommes))
    if residu > tolerance:
        raise ValueError(
            f"la colonne « ensemble » n'est pas le mélange des deux sexes : "
            f"résidu de {residu:.2e}, au-delà de {tolerance:.0e}"
        )
    return poids
