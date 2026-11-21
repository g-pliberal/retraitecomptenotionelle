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
PART DU POSTE qui est reconduite — 27,8 % en 2025, entre 26,6 et 29,2 % depuis
2019. Même règle que ``AssietteActivite.annee_de_reference``, et pour la même
raison.

LA PART DE TVA GARDÉE N'EST PAS ABANDONNÉE
-------------------------------------------
Le poste du COR compte la TVA reversée à l'Agirc-Arrco, que la proposition
GARDE (décision 79 du programme, ``donnees/tva.py``) : le coût la lui rend, à
compter de sa bascule, sur la ligne ``impots_tva_gardee``. Le partage la
retranche donc du poste avant de le couper en deux, sans quoi il distribuerait
une recette que la retraite encaisse encore — 64 Md€ partagés en 2026, quand
elle n'en perd que 53. Moitié, moitié, sur ce qui est vraiment abandonné :
le propriétaire l'a tranché le 21 novembre 2026. La part gardée se rapporte au
PIB comme le coût le fait, publié puis projeté par sa variation nominale.

LA CTA, SUPPRIMÉE, NON PLUS
---------------------------
Le poste compte aussi la contribution tarifaire d'acheminement, que la CNIEG
enregistre en impôts et taxes affectés. La proposition la supprime (décision
88) : elle revient aux ménages par leurs factures d'énergie, et la partager
la promettrait deux fois. Elle sort du partage comme la TVA gardée, à compter
de la bascule (21 novembre 2026), lue dans ``cta_ieg.csv`` : celle de 2025,
en part de PIB, que le COR reconduit dans le poste sans la baisse de taux de
la CRE du 1er février 2026.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .donnees.assiette import AssietteActivite
from .donnees.chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle
from .donnees.equilibre import ComptesRetraite
from .donnees.macro import DonneesMacro
from .donnees.tva import TvaGardee
from .somme import somme_ordonnee

#: L'année de la bascule sous les réglages de référence (``Parametres``).
ANNEE_BASCULE: int = 2026

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
    #: Les impôts et taxes que la proposition n'encaisse plus, en part de PIB :
    #: le poste du COR, moins la part de TVA qu'elle garde.
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
    #: La part de TVA que la proposition garde, et qui n'est donc pas
    #: partagée, en part de PIB ; zéro avant la bascule.
    tva_gardee: float = 0.0
    #: La CTA, que la proposition supprime et qui n'est donc pas partagée, en
    #: part de PIB ; zéro avant la bascule.
    cta_supprimee: float = 0.0


class CtaSupprimee:
    """La contribution tarifaire d'acheminement, en millions d'euros courants.

    Sur les années que ``cta_ieg.csv`` porte ; au-delà, l'année la plus
    proche, que ``part_pib`` rapporte au PIB de cette année-là : la convention
    de :class:`.tva.TvaGardee`.
    """

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "macro" / "cta_ieg.csv"
        self.serie = (charger_serie_annuelle(chemin, "montant_meur", nom="cta_ieg",
                                             filtre={"poste": "cta_recouvree"})
                      if chemin.exists() else None)

    def __bool__(self) -> bool:
        return self.serie is not None

    def _publiee(self, annee: int) -> int:
        return min(max(annee, self.serie.premiere_annee), self.serie.derniere_annee)

    def montant(self, annee: int) -> float:
        return self.serie(self._publiee(annee)) if self else 0.0

    def part_pib(self, annee: int, pib) -> float:
        if not self:
            return 0.0
        publiee = self._publiee(annee)
        produit = pib(publiee)
        return self.serie(publiee) / produit if produit else 0.0


class Restitution:
    """Le partage, année par année, des impôts que la proposition abandonne.

    Trois séries et rien d'autre : le compte du COR, qui donne le poste
    abandonné ; les deux impôts assis sur une rémunération, lus dans les
    comptes de la Sécurité sociale ; l'assiette des revenus d'activité, qui
    convertit en points de CSG ce qui reste à rendre.
    """

    def __init__(self, racine: Path, part_rendue: float = 0.5,
                 annee_bascule: int = ANNEE_BASCULE, tva_gardee: bool = True) -> None:
        macro = racine / "reference" / "macro"
        self.annee_bascule = annee_bascule
        self.gardee = TvaGardee(racine) if tva_gardee else None
        self.cta = CtaSupprimee(racine)
        self.macro = DonneesMacro(racine)
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
        return somme_ordonnee(serie(annee) for serie in self.postes.values())

    def poste_affecte(self, annee: int) -> float:
        """Les impôts et taxes affectés à la retraite, en part de PIB : le
        poste du COR, part de TVA de l'Agirc-Arrco comprise."""
        return (self.comptes.ressource(annee)
                * self.comptes.part("impots_et_taxes", annee))

    def pib_de_la_trajectoire(self, annee: int) -> float:
        """Le PIB que le coût prête à l'année, en millions d'euros : publié,
        puis le dernier publié que fait croître la variation nominale."""
        derniere = self.assiette.pib.derniere_annee
        pib = self.assiette.pib(min(annee, derniere))
        for suivante in range(derniere + 1, annee + 1):
            pib *= 1.0 + self.macro.pib_nominal(suivante)
        return pib

    def tva_gardee(self, annee: int) -> float:
        """La part de TVA que la proposition garde, en part de PIB : celle
        que le coût lui rend, à compter de sa bascule."""
        if self.gardee is None or not self.gardee or annee < self.annee_bascule:
            return 0.0
        return max(self.gardee.part_pib(annee, self.pib_de_la_trajectoire), 0.0)

    def cta_supprimee(self, annee: int) -> float:
        """La CTA que la proposition supprime, en part de PIB, à compter de
        sa bascule : elle revient aux factures, non au partage."""
        if annee < self.annee_bascule:
            return 0.0
        return max(self.cta.part_pib(annee, self.pib_de_la_trajectoire), 0.0)

    def poste_abandonne(self, annee: int) -> float:
        """Les impôts et taxes que la proposition partage, en part de PIB :
        le poste, moins la part de TVA qu'elle garde et la CTA qu'elle
        supprime."""
        return (self.poste_affecte(annee) - self.tva_gardee(annee)
                - self.cta_supprimee(annee))

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
        poste = self.poste_affecte(reference) * pib
        if poste <= 0.0:
            return 0.0
        return self.montant_remuneration(reference) / poste

    def annuelle(self, annee: int) -> RestitutionAnnuelle:
        """Le partage d'une année."""
        gardee = self.tva_gardee(annee)
        cta = self.cta_supprimee(annee)
        poste = self.poste_affecte(annee) - gardee - cta
        part = self.part_du_poste(annee)
        rendu = self.part_rendue * poste
        # Les deux impôts supprimés sont une part du poste du COR, non de ce
        # qui reste une fois la TVA gardée : elle n'en compte aucun.
        supprime = min(part * self.poste_affecte(annee), rendu)
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
            tva_gardee=gardee,
            cta_supprimee=cta,
        )


def points_csg_rendus(racine: Path, annee: int, part_rendue: float = 0.5,
                      annee_bascule: int | None = None, tva_gardee: bool = True) -> float:
    """Les points de CSG d'activité que la proposition rend cette année-là.

    Le raccourci de la fiche de paie, qui n'a besoin que de ce nombre. La
    lecture des trois séries est mémorisée : la fiche de paie d'une carrière le
    demande une fois par année cotisée.
    """
    bascule = ANNEE_BASCULE if annee_bascule is None else annee_bascule
    return _restitution(racine, part_rendue, bascule, tva_gardee).annuelle(annee).points_csg


@lru_cache(maxsize=8)
def _restitution(racine: Path, part_rendue: float, annee_bascule: int | None = None,
                 tva_gardee: bool = True) -> Restitution:
    bascule = ANNEE_BASCULE if annee_bascule is None else annee_bascule
    return Restitution(racine, part_rendue, bascule, tva_gardee)
