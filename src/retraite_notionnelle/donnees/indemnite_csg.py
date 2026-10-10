"""L'indemnité compensatrice de la hausse de la CSG des agents publics, depuis
2018 (``legislation/indemnite_compensatrice_csg.yaml``) : le décret
n° 2017-1889, son article 2, qui la fixe, et son article 5, qui la réévalue.

Ce module ne connaît que des rémunérations : celles d'un agent public, année
par année, annualisées, et ce que la CES et les cotisations supprimées en 2018
lui prenaient en 2017. Ce qu'en fait la fiche de paie — l'ajouter au
traitement et aux primes, hors de l'assiette de la retenue, dans celle de la
RAFP — est dans ``remuneration.py``.

Action 138, étape 12. Jumeau : ``moteur/js/indemnite_csg.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chargement import charger_yaml, une_fois_par_instantane


@dataclass(frozen=True)
class Reevaluation:
    """Une réévaluation de l'article 5, au 1er janvier de ``annee`` (ou de
    chaque année depuis ``annee``, quand ``chaque_annee``) : elle compare les
    deux années civiles qui précèdent."""

    annee: int
    chaque_annee: bool
    #: ``hausse`` : seulement si la rémunération a progressé ; ``evolution`` :
    #: dans les deux sens.
    sens: str
    #: Le réexamen de 2019 ne vaut que pour les agents du I de l'article 2.
    seulement_remuneres_fin_2017: bool = False

    def vaut(self, annee: int) -> bool:
        return annee >= self.annee if self.chaque_annee else annee == self.annee


@dataclass(frozen=True)
class IndemniteCompensatrice:
    """Les paramètres du décret, et le montant qu'ils donnent."""

    debut: int = 2018
    familles: frozenset[str] = frozenset()
    profils: frozenset[str] = frozenset()
    annee_de_reference: int = 2017
    taux_hausse_csg: float = 0.0
    coefficient: float = 1.0
    taux_ces: float = 0.0
    plafond_ces_en_pss: float = 0.0
    seuil_ces_annuel: float = 0.0
    taux_recrutes: float = 0.0
    reevaluations: tuple[Reevaluation, ...] = ()

    def contribution_de_solidarite(self, remuneration: float, cotisations: float,
                                   traitement_net: float, plafond_annuel: float) -> float:
        """La CES de l'année de référence : 1 % de la rémunération nette de
        ses cotisations, ``remuneration − cotisations``, dans la limite de
        quatre plafonds ; rien quand le traitement, net de ses retenues,
        ``traitement_net``, reste sous l'indice majoré 313 (R. 5423-52). Les
        trois montants sont annuels."""
        if traitement_net < self.seuil_ces_annuel:
            return 0.0
        nette = max(0.0, remuneration - cotisations)
        return self.taux_ces * min(nette, self.plafond_ces_en_pss * plafond_annuel)

    def initiale(self, remuneration_reference: float, deduits: float) -> float:
        """Le montant annuel du I de l'article 2 : la rémunération de 2017 par
        1,6702 %, moins ``deduits`` — la CES, et pour un contractuel la
        maladie et le chômage —, par 1,1053 ; jamais négatif."""
        return max(0.0, self.taux_hausse_csg * remuneration_reference - deduits) * self.coefficient

    def montants(self, remunerations: dict[int, float],
                 deduits_reference: float = 0.0) -> dict[int, float]:
        """L'indemnité annuelle de chaque année où l'agent est payé, depuis
        2018, en euros de l'année.

        ``remunerations`` : la rémunération annualisée de chaque année où il
        est payé comme agent public bénéficiaire, l'indemnité non comprise ;
        ``deduits_reference`` : ce que le I déduit de celle de 2017.

        Payé en 2017, il relève du I ; sinon, sa première année d'agent public
        depuis 2018 fixe l'indemnité à 0,76 % de sa rémunération (II et III),
        la rémunération annualisée tenant lieu du premier mois complet. Chaque
        1er janvier, la réévaluation de l'année, quand les deux années qui la
        précèdent sont payées : la circulaire reporte au retour le réexamen de
        l'agent qui ne l'est pas.
        """
        reference = self.annee_de_reference
        annees = sorted(a for a in remunerations if a >= self.debut
                        and remunerations[a] > 0.0)
        if not annees:
            return {}
        fin_2017 = remunerations.get(reference, 0.0) > 0.0
        if fin_2017:
            montant = self.initiale(remunerations[reference], deduits_reference)
            depuis = self.debut
        else:
            depuis = annees[0]
            montant = self.taux_recrutes * remunerations[depuis]
        resultat: dict[int, float] = {}
        for annee in range(depuis, annees[-1] + 1):
            if annee > depuis:
                montant *= self.rapport(remunerations, annee, fin_2017)
            if annee in remunerations and remunerations[annee] > 0.0:
                resultat[annee] = montant
        return resultat

    def rapport(self, remunerations: dict[int, float], annee: int, fin_2017: bool) -> float:
        """Ce par quoi la réévaluation du 1er janvier de ``annee`` multiplie
        l'indemnité : un, quand aucune ne vaut cette année-là, ou que l'une des
        deux années comparées n'est pas payée."""
        regle = next((r for r in self.reevaluations if r.vaut(annee)), None)
        if regle is None or (regle.seulement_remuneres_fin_2017 and not fin_2017):
            return 1.0
        ecoulee = remunerations.get(annee - 1, 0.0)
        precedente = remunerations.get(annee - 2, 0.0)
        if ecoulee <= 0.0 or precedente <= 0.0:
            return 1.0
        rapport = ecoulee / precedente
        if regle.sens == "hausse" and rapport <= 1.0:
            return 1.0
        return rapport


_TABLES: dict[tuple, IndemniteCompensatrice] = {}


@une_fois_par_instantane
def charger_indemnite_csg(racine: Path) -> IndemniteCompensatrice:
    """Les paramètres du décret, gardés sur la signature du fichier ; sans
    lui, une indemnité nulle."""
    chemin = racine / "reference" / "legislation" / "indemnite_compensatrice_csg.yaml"
    if not chemin.exists():
        return IndemniteCompensatrice()
    etat = chemin.stat()
    cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    if cle in _TABLES:
        return _TABLES[cle]
    contenu = charger_yaml(chemin)
    fin_2017 = contenu["remuneres_au_31_decembre_2017"]
    ces = fin_2017["contribution_exceptionnelle_de_solidarite"]
    reevaluations = []
    for entree in contenu.get("reevaluations") or ():
        if entree["sens"] not in ("hausse", "evolution"):
            raise ValueError(f"indemnité compensatrice : sens inconnu, {entree['sens']!r}")
        reevaluations.append(Reevaluation(
            annee=int(entree.get("annee", entree.get("depuis"))),
            chaque_annee="depuis" in entree,
            sens=entree["sens"],
            seulement_remuneres_fin_2017=bool(
                entree.get("seulement_remuneres_au_31_decembre_2017", False))))
    table = IndemniteCompensatrice(
        debut=int(contenu["debut"]),
        familles=frozenset(contenu["beneficiaires"]["familles"]),
        profils=frozenset(contenu["beneficiaires"]["profils"]),
        annee_de_reference=int(fin_2017["annee_de_reference"]),
        taux_hausse_csg=float(fin_2017["taux_hausse_csg"]),
        coefficient=float(fin_2017["coefficient_neutralisation"]),
        taux_ces=float(ces["taux"]),
        plafond_ces_en_pss=float(ces["plafond_en_pss"]),
        seuil_ces_annuel=float(ces["seuil_indice_majore"]) * float(ces["valeur_annuelle_du_point"]),
        taux_recrutes=float(contenu["recrutes_depuis_2018"]["taux"]),
        reevaluations=tuple(reevaluations),
    )
    _TABLES[cle] = table
    return table
