"""Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.

La proposition du Parti libéral ne reconduit pas les impôts et taxes affectés
à la retraite — 63,9 Md€ en 2025, 15,3 % de ses ressources. ``cout.py`` dit
pourquoi : un compte notionnel ne crédite que ce qui est assis sur un revenu
d'activité, et un impôt affecté n'ouvre de droit à personne.

Restait une question que le dépôt ne posait pas, et qui n'est pas comptable :
**cette recette, qui ne va plus à la retraite, va où ?** Ne rien dire, c'est la
laisser au budget de l'État, c'est-à-dire la consacrer tout entière au déficit.
La décision du 20 septembre 2026 tranche autrement, et en deux moitiés :

    la MOITIÉ est rendue aux salaires, la MOITIÉ éteint de la dette.

C'est ``Parametres.part_rendue_aux_salaires``, et le partage n'est pas une
commodité d'écriture : le mettre à un ferait de la proposition une baisse
d'impôt intégrale, le mettre à zéro en ferait un transfert au budget.

CE QUI EST RENDU, ET DANS QUEL ORDRE
-------------------------------------
Rendre « aux salaires » n'a de sens que pour ce qui en sort. Le droit désigne
ce qui en sort, et il en désigne deux — c'est la lecture du 20 septembre 2026,
faite dans l'index LEGI du dépôt :

* la **taxe sur les salaires** (article 231 du code général des impôts), dont
  l'article L. 131-8, 1° du code de la sécurité sociale verse 58,35 % à la
  branche vieillesse. Elle est due par les employeurs qui ne sont pas
  assujettis à la TVA — hôpitaux, banques, assurances, associations ;
* le **forfait social** (article L. 137-15), assis sur les rémunérations
  exonérées de cotisations — intéressement, participation, épargne salariale —,
  dont l'article L. 241-3, 1° donne le produit ENTIER à l'assurance vieillesse.

Ensemble, 17,8 Md€ en 2025, soit 28 % du poste — une part remarquablement
stable depuis 2019. La proposition les SUPPRIME, purement et simplement : ce
sont les seuls impôts du poste qu'un employeur verse au titre d'une
rémunération, et les rendre par un autre canal serait un détour.

Le solde de la moitié rendue — ce qui reste une fois ces deux impôts
supprimés — revient au salarié par la **CSG sur les revenus d'activité**, dont
le taux baisse d'autant. Un peu plus d'un point : 1,12 en 2025.

ET C'EST ICI QU'IL FAUT DIRE CE QUE LA CSG D'ACTIVITÉ N'EST PAS
-----------------------------------------------------------------
**Elle ne finance aucune retraite.** Ses 9,20 points se répartissent, à
l'article L. 131-8, 3° du code de la sécurité sociale dans sa rédaction en
vigueur depuis le 1er février 2026 : Caisse nationale des allocations
familiales 0,95, régimes obligatoires d'assurance maladie 4,25, Caisse
d'amortissement de la dette sociale 0,45, Unédic 1,47, Caisse nationale de
solidarité pour l'autonomie 2,08. Neuf virgule vingt exactement, et rien pour
la branche vieillesse. Ce que la retraite encaisse en CSG est assis sur le
capital (6,67 points sur 10,6, L. 131-8, 3° bis) et sur les pensions (2,94
points, L. 131-8, 3° e).

La baisse de CSG d'activité n'est donc PAS la restitution d'un prélèvement
retraite : c'est une baisse d'impôt financée par une recette que la retraite
abandonne. La proposition l'assume comme telle, et le site l'écrit — sans quoi
le lecteur croirait qu'on lui rend ce qu'on lui prenait, ce qui serait faux.

CE QUI EST RECONDUIT, ET CE QUI NE PEUT PAS L'ÊTRE
----------------------------------------------------
Le POSTE suit le compte du COR, projections comprises. Les deux impôts assis
sur la rémunération, eux, ne sont publiés que de 2019 à 2025 : reconduire un
montant en euros courants jusqu'en 2070 ne voudrait rien dire, et c'est leur
PART DU POSTE qui est reconduite — 27,8 % en 2025, entre 26,6 et 28,9 % depuis
2019. Même règle que ``AssietteActivite.annee_de_reference``, et pour la même
raison.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .donnees.assiette import AssietteActivite
from .donnees.chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle
from .donnees.equilibre import ComptesRetraite

#: Les deux impôts du poste qui sont assis sur une rémunération, et que la
#: proposition supprime. Voir le docstring : c'est le droit qui les désigne,
#: pas une appréciation.
POSTES_REMUNERATION: tuple[tuple[str, str], ...] = (
    ("taxe_sur_les_salaires", "Taxe sur les salaires"),
    ("forfait_social", "Forfait social"),
)


@dataclass(frozen=True)
class RestitutionAnnuelle:
    """Le partage d'une année, en part de PIB sauf mention contraire."""

    annee: int
    #: Les impôts et taxes que la proposition n'encaisse plus, en part de PIB.
    poste_abandonne: float
    #: La moitié rendue aux salaires, en part de PIB.
    rendu: float
    #: Ce qui est rendu en SUPPRIMANT la taxe sur les salaires et le forfait
    #: social, en part de PIB.
    supprime_sur_la_remuneration: float
    #: Ce qui reste à rendre par la CSG, en points de l'assiette des revenus
    #: d'activité — une fraction, 0,0112 pour 1,12 point.
    points_csg: float
    #: La moitié qui éteint de la dette, en part de PIB.
    eteint_de_dette: float
    #: Celle des deux séries d'impôts qui vaut le moins, l'année où la part est
    #: mesurée. Les parts de PIB, elles, valent ce que vaut le compte du COR.
    fiabilite: Fiabilite


class Restitution:
    """Le partage, année par année, des impôts que la proposition abandonne.

    Trois séries et rien d'autre : le compte du COR, qui donne le poste
    abandonné ; les deux impôts assis sur une rémunération, lus dans les
    comptes de la Sécurité sociale ; l'assiette des revenus d'activité, qui
    convertit en points de CSG ce qui reste à rendre.
    """

    def __init__(self, racine: Path, part_rendue: float = 0.5) -> None:
        macro = racine / "reference" / "macro"
        chemin = macro / "impots_retraite_remuneration.csv"
        self.part_rendue = part_rendue
        self.postes: dict[str, SerieAnnuelle] = {}
        if chemin.exists():
            self.postes = {
                code: charger_serie_annuelle(
                    chemin, "montant_meur", nom=f"impots_remuneration_{code}",
                    filtre={"poste": code},
                )
                for code, _ in POSTES_REMUNERATION
            }
        self.assiette = AssietteActivite(racine)
        self.comptes = ComptesRetraite(racine)

    def __bool__(self) -> bool:
        return bool(self.postes) and bool(self.comptes)

    @property
    def derniere_annee(self) -> int:
        """Dernière année où les deux impôts sont publiés."""
        return min(serie.derniere_annee for serie in self.postes.values())

    def montant_remuneration(self, annee: int) -> float:
        """Taxe sur les salaires et forfait social, en millions d'euros courants."""
        return sum(serie(annee) for serie in self.postes.values())

    def poste_abandonne(self, annee: int) -> float:
        """Les impôts et taxes que la proposition n'encaisse plus, en part de PIB."""
        return (self.comptes.ressource(annee)
                * self.comptes.part("impots_et_taxes", annee))

    def part_du_poste(self, annee: int) -> float:
        """La part du poste qui est assise sur une rémunération.

        Mesurée sur l'année demandée tant que les deux impôts sont publiés, sur
        la dernière publiée ensuite : c'est un TAUX qui se reconduit, jamais un
        montant en euros courants. Le poste est pris la MÊME année que les deux
        impôts, sans quoi on rapporterait deux millésimes l'un à l'autre.
        """
        if not self.postes:
            return 0.0
        reference = min(annee, self.derniere_annee)
        pib = self.assiette.pib(reference)
        poste = self.poste_abandonne(reference) * pib
        if poste <= 0.0:
            return 0.0
        return self.montant_remuneration(reference) / poste

    def annuelle(self, annee: int) -> RestitutionAnnuelle:
        """Le partage d'une année."""
        poste = self.poste_abandonne(annee)
        part = self.part_du_poste(annee)
        rendu = self.part_rendue * poste
        supprime = min(part * poste, rendu)
        reference = self.assiette.annee_de_reference(annee)
        part_assiette = self.assiette.part_pib(reference)
        reste = max(0.0, rendu - supprime)
        return RestitutionAnnuelle(
            annee=annee,
            poste_abandonne=poste,
            rendu=rendu,
            supprime_sur_la_remuneration=supprime,
            points_csg=reste / part_assiette if part_assiette else 0.0,
            eteint_de_dette=(1.0 - self.part_rendue) * poste,
            fiabilite=min(
                (serie.fiabilite(min(annee, self.derniere_annee))
                 for serie in self.postes.values()),
                default=Fiabilite.ESTIMEE,
            ),
        )


def points_csg_rendus(racine: Path, annee: int, part_rendue: float = 0.5) -> float:
    """Les points de CSG d'activité que la proposition rend cette année-là.

    Le raccourci de la fiche de paie, qui n'a besoin que de ce nombre. La
    lecture des trois séries est mémorisée : la fiche de paie d'une carrière le
    demande une fois par année cotisée.
    """
    return _restitution(racine, part_rendue).annuelle(annee).points_csg


@lru_cache(maxsize=8)
def _restitution(racine: Path, part_rendue: float) -> Restitution:
    return Restitution(racine, part_rendue)
