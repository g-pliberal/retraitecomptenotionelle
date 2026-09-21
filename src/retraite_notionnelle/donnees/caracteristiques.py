"""Ce que les carrières des femmes et des hommes doivent aux droits non cotisés.

La garantie vieillesse du scénario 6 est chiffrée en déplaçant la distribution
des pensions de l'EIR. Le scénario ne déplace pourtant pas toutes les carrières
du même rapport : il retire les droits NON COTISÉS, et les femmes en détiennent
plus souvent. Le dépôt le disait, savait le sens de son erreur, et n'en
connaissait pas la taille.

Ce module lit ce qui la donne. Le même échantillon interrégimes qui porte la
distribution porte aussi, dans un autre classeur du même millésime, les
caractéristiques des retraités par sexe : les effectifs, la pension moyenne
avec et sans les majorations pour enfants, la part de la durée validée qui n'a
pas été cotisée.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite


class CaracteristiquesRetraites:
    """Les indicateurs de l'EIR par sexe, pour un millésime.

    Le millésime le plus récent est retenu par défaut, comme pour la
    distribution : chaque enquête décrit un état de la population à sa date, et
    elles ne se complètent pas — elles se remplacent.
    """

    def __init__(self, racine: Path, millesime: int | None = None) -> None:
        chemin = racine / "reference" / "macro" / "caracteristiques_retraites.csv"
        valeurs: dict[int, dict[tuple[str, str], float]] = {}
        fiabilites: dict[int, Fiabilite] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee = int(ligne["annee"])
                valeurs.setdefault(annee, {})[
                    (ligne["indicateur"], ligne["sexe"])
                ] = float(ligne["valeur"])
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = fiabilites.get(annee)
                fiabilites[annee] = (
                    niveau if courante is None else min(courante, niveau)
                )
        if not valeurs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")

        self.millesime = max(valeurs) if millesime is None else millesime
        if self.millesime not in valeurs:
            raise KeyError(f"millésime absent de {chemin.name} : {self.millesime}")
        self._valeurs = valeurs[self.millesime]
        self.fiabilite = fiabilites[self.millesime]

    def valeur(self, indicateur: str, sexe: str) -> float:
        """Un indicateur pour un sexe — ``F``, ``H`` ou ``ensemble``."""
        try:
            return self._valeurs[(indicateur, sexe)]
        except KeyError:
            raise KeyError(
                f"indicateur inconnu pour {self.millesime} : "
                f"{indicateur!r} / {sexe!r}"
            ) from None

    @property
    def part_femmes(self) -> float:
        """La part des femmes parmi les retraités, LUE et non plus ajustée.

        Le dépôt l'obtenait en cherchant le poids qui recompose la colonne
        « ensemble » de la distribution à partir de ses deux colonnes de sexe —
        un ajustement juste, mais un ajustement. L'enquête publie l'effectif de
        chaque sexe, et les deux se répondent au dix-millième :
        ``test_les_deux_sexes_recomposent_la_colonne_dont_le_cout_est_tire``
        tient le raccord.
        """
        ensemble = self.valeur("effectifs", "ensemble")
        return self.valeur("effectifs", "F") / ensemble if ensemble else 0.0

    def part_non_cotisee(self, sexe: str) -> float:
        """La part de la durée validée qui n'a pas été cotisée, en fraction."""
        return self.valeur("duree_validee_non_cotisee", sexe) / 100.0

    def part_majorations(self, sexe: str) -> float:
        """Ce que la majoration pour enfants pèse dans la pension, en fraction.

        Elle est proportionnelle à la pension — dix pour cent pour trois
        enfants —, si bien qu'elle pèse un peu MOINS chez les femmes, dont les
        pensions sont plus basses. Le terme joue donc à l'envers de
        l'intuition, et c'est pourquoi il vaut mieux le lire que le supposer.
        """
        avec = self.valeur("pension_droit_direct_majorations", sexe)
        sans = self.valeur("pension_droit_direct", sexe)
        return (avec - sans) / avec if avec else 0.0

    def part_minimum_pension(self, sexe: str) -> float:
        """La part des retraités qui touchent un minimum de pension.

        Elle ne sert à aucun calcul : l'enquête publie la part des
        bénéficiaires et non ce que le minimum leur apporte, si bien que le
        retirer ne se chiffre pas ici. Elle dit dans quel SENS le rapport
        ci-dessous se trompe, et c'est à ce titre que la page la cite.
        """
        return self.valeur("part_minimum_pension", sexe) / 100.0

    def rapport_deplacement(self) -> float:
        """``r = f_F / f_H`` : de combien les femmes tombent plus que les hommes.

        DEUX TERMES, ET ILS NE JOUENT PAS DANS LE MÊME SENS.

        **La durée non cotisée domine.** Un compte notionnel ne crédite que ce
        qui a été cotisé : une année validée sans cotisation n'y porte rien,
        qu'elle vienne de l'assurance vieillesse des parents au foyer, du
        chômage, de la maladie ou d'une majoration de durée. Le capital est
        donc proportionnel à la part COTISÉE de la carrière — 74,0 % chez les
        femmes, 89,1 % chez les hommes en 2020 —, et leur rapport est le gros
        du déplacement différentiel.

        **La majoration pour enfants joue à l'envers, et de peu.** Elle vaut
        dix pour cent de la pension pour trois enfants, donc davantage
        d'euros à qui a la pension la plus haute : 3,0 % de celle des hommes
        contre 2,6 % de celle des femmes. La retirer coûte donc un peu plus
        aux hommes, et corrige le premier terme de moins d'un demi-point.

        CE QUE CE RAPPORT SUPPOSE, et il faut le dire. Le salaire porté au
        compte est supposé le même d'une année cotisée à l'autre, faute de quoi
        la part cotisée de la carrière ne serait pas celle du capital. Et les
        minima de pension n'y sont pas : l'enquête donne la PART de leurs
        bénéficiaires — 46,5 % des femmes contre 26,1 % des hommes — et non ce
        qu'ils leur apportent. Les retirer creuserait l'écart, si bien que ce
        rapport est lui-même une borne HAUTE, et le coût qui en découle une
        borne basse.
        """
        cotisee = {
            sexe: 1.0 - self.part_non_cotisee(sexe) for sexe in ("F", "H")
        }
        majorees = {sexe: 1.0 - self.part_majorations(sexe) for sexe in ("F", "H")}
        if cotisee["H"] <= 0.0 or majorees["H"] <= 0.0:
            raise ValueError("les parts des hommes doivent être strictement positives")
        return (cotisee["F"] / cotisee["H"]) * (majorees["F"] / majorees["H"])
