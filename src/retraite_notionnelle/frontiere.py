"""Le versant inverse de l'inventaire : ce qu'on cotise sans rien acquérir.

`avantages.py` chiffre ce que le système SERT au-delà de la cotisation. Ce
module chiffre l'autre côté — ce qui est PRÉLEVÉ sans qu'aucun droit ne
s'ouvre —, et il tient la liste datée des déplacements de la frontière entre
les deux.

POURQUOI C'EST UNE GRANDEUR, ET NON UNE CURIOSITÉ. Un compte notionnel ne sert
que ce qui a été cotisé ; c'est la phrase fondatrice de ce dépôt. Elle a un
revers que personne n'énonce : une part de ce qui est cotisé ne sert jamais
rien. La cotisation vieillesse déplafonnée de l'article L. 241-3 du code de la
sécurité sociale n'ouvre aucun droit — le salaire annuel de base est borné au
plafond par R. 351-29, les trimestres à quatre par an par R. 351-9 — et elle
porte pourtant sur la TOTALITÉ de la rémunération, dès le premier euro.

L'ERREUR À NE PAS REFAIRE, et elle a été faite ici. On croit spontanément que
cette cotisation ne porte que sur la fraction du salaire au-dessus du plafond.
C'est faux, et l'écart vaut un facteur dix. Toute la difficulté du chiffrage
était là, et une fois la lecture faite il n'y en a plus : la masse est le
produit d'un taux par une assiette, et les deux sont publiés.

LES DEUX TERMES VIENNENT DE PRODUCTEURS, ET DU MÊME CHAMP. Le taux est celui
de `taux_cotisation_annuels.csv`, certifié contre les décrets. L'assiette est
celle de `masse_salariale_privee.csv`, que l'Urssaf DÉFINIT comme « l'assiette
déplafonnée des cotisations sociales » — secteur privé, régime général. Ne
jamais lui substituer les salaires bruts des comptes nationaux, qui couvrent
toute l'économie, fonction publique comprise : 726 milliards contre environ
1 050 en 2024.

CE QUE LE RÉSULTAT N'EST PAS. Il ne se soustrait de rien. Les avantages non
contributifs et les cotisations sans contrepartie sont deux grandeurs de sens
opposé, sur deux faces différentes de la même frontière, et les compenser
n'aurait aucun sens : l'une dit ce que le système donne sans qu'on ait payé,
l'autre ce qu'on paie sans rien recevoir. Elles ne se rencontrent pas dans la
même poche.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .donnees.chargement import Fiabilite, charger_serie_annuelle, charger_yaml

#: Les trois faces du mot « contributif », et ce que chacune mesure. Le
#: vocabulaire est fermé, et `docs/frontiere_contributive.md` dit pourquoi :
#: elles se déplacent séparément, et les confondre fait lire une baisse là où
#: il n'y a qu'une fin de publication.
FACES = {
    "droit": "ce que l'assuré acquiert sans avoir cotisé",
    "cotisation": "ce qu'il verse sans rien acquérir",
    "financement": "qui paie la charge, et si elle reste visible",
}


@dataclass(frozen=True)
class AnneeCotisationSterile:
    """Ce qu'une année a prélevé sans ouvrir de droit, en milliards d'euros."""

    annee: int
    assiette_md: float
    taux: float
    total_md: float
    salariale_md: float

    @property
    def patronale_md(self) -> float:
        return self.total_md - self.salariale_md

    def dictionnaire(self) -> dict:
        return {
            "annee": self.annee,
            "assiette_md": self.assiette_md,
            "taux": self.taux,
            "total_md": self.total_md,
            "salariale_md": self.salariale_md,
        }


@dataclass(frozen=True)
class TrancheComplementaire:
    """Ce qu'une tranche Agirc-Arrco prélève, et ce qu'elle en fait acquérir."""

    nom: str
    acquisitif: float
    verse_sous_plafond: float
    verse_au_dessus: float

    @property
    def part_sous_plafond(self) -> float:
        return 1.0 - self.acquisitif / self.verse_sous_plafond

    @property
    def part_au_dessus(self) -> float:
        return 1.0 - self.acquisitif / self.verse_au_dessus

    def dictionnaire(self) -> dict:
        return {
            "nom": self.nom,
            "acquisitif": self.acquisitif,
            "verse_sous_plafond": self.verse_sous_plafond,
            "verse_au_dessus": self.verse_au_dessus,
        }


@dataclass(frozen=True)
class Frontiere:
    """Le versant `cotisation` de la frontière, chiffré et en proportion."""

    annees: tuple[AnneeCotisationSterile, ...]
    tranches: tuple[TrancheComplementaire, ...]
    pourcentage_appel: float
    source_complementaire: str
    lu_le: str

    @property
    def derniere(self) -> AnneeCotisationSterile | None:
        return self.annees[-1] if self.annees else None

    def dictionnaire(self) -> dict:
        return {
            "annees": [a.dictionnaire() for a in self.annees],
            "tranches": [t.dictionnaire() for t in self.tranches],
            "pourcentage_appel": self.pourcentage_appel,
            "source_complementaire": self.source_complementaire,
            "lu_le": self.lu_le,
        }


def frontiere_depuis_paquet(lignes: dict) -> Frontiere:
    """Relit le paquet du portage — le pendant de ``inventaire_depuis_paquet``."""
    return Frontiere(
        annees=tuple(AnneeCotisationSterile(**a) for a in lignes["annees"]),
        tranches=tuple(TrancheComplementaire(**t) for t in lignes["tranches"]),
        pourcentage_appel=lignes["pourcentage_appel"],
        source_complementaire=lignes["source_complementaire"],
        lu_le=lignes["lu_le"],
    )


def charger_frontiere(racine: Path) -> Frontiere:
    """Le chiffrage, depuis les deux séries et la fiche de la complémentaire.

    UNE SEULE PORTE. Le script `scripts/frontiere_contributive.py` et la page
    du site passent tous deux par ici. Le § 4 sexies de
    `docs/avantages_non_contributifs.md` raconte ce qu'il en coûte quand ce
    n'est pas le cas : la ligne de commande annonçait 12,6 milliards quand la
    page en annonçait 93,9, et l'écart n'était pas une erreur de calcul mais
    une différence de périmètre que rien ne signalait.
    """
    assiette = charger_serie_annuelle(
        racine / "reference" / "macro" / "masse_salariale_privee.csv",
        "montant_meur", interpolation="ponctuelle")
    chemin_taux = racine / "reference" / "regimes" / "taux_cotisation_annuels.csv"
    taux = charger_serie_annuelle(
        chemin_taux, "valeur", interpolation="escalier",
        filtre={"regime": "regime_general", "mesure": "taux_deplafonne"})
    part = charger_serie_annuelle(
        chemin_taux, "valeur", interpolation="escalier",
        filtre={"regime": "regime_general", "mesure": "part_salariale_deplafonnee"})

    annees: list[AnneeCotisationSterile] = []
    for annee in range(assiette.premiere_annee, assiette.derniere_annee + 1):
        # ON NE CHIFFRE QUE CE QUE L'URSSAF A PUBLIÉ. Hors de sa fenêtre, la
        # série reconduit sa valeur de bord et retombe à `estimee` ; la
        # multiplier par un taux donnerait un milliard sans source au milieu
        # d'une colonne qui en a une.
        observee = assiette.brut(annee)
        if observee.fiabilite is not Fiabilite.CERTIFIEE:
            continue
        masse = observee.valeur / 1000.0
        applique = taux(annee)
        preleve = masse * applique
        annees.append(AnneeCotisationSterile(
            annee=annee, assiette_md=masse, taux=applique,
            total_md=preleve, salariale_md=preleve * part(annee)))

    fiche = charger_yaml(
        racine / "reference" / "legislation" / "frontiere_contributive.yaml"
    )["taux_agirc_arrco"]
    cet = fiche["contribution_equilibre_technique"]
    tranches = tuple(
        TrancheComplementaire(
            nom=t["nom"],
            acquisitif=t["taux_calcul_des_points"],
            verse_sous_plafond=t["taux_appele"] + t["contribution_equilibre_general"],
            verse_au_dessus=t["taux_appele"] + t["contribution_equilibre_general"] + cet,
        )
        for t in fiche["tranches"]
    )
    return Frontiere(
        annees=tuple(annees), tranches=tranches,
        pourcentage_appel=fiche["pourcentage_appel"],
        source_complementaire=fiche["source"], lu_le=str(fiche["lu_le"]))
