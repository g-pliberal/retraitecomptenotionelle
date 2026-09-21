"""Les affirmations du site, confrontées au modèle.

``tests/temoins/pages.json`` fige le texte des pages : il rend visible une
modification, il ne valide aucune affirmation. Ce fichier fait l'autre moitié
du travail, à partir du catalogue ``data/reference/site/affirmations.yaml`` —
c'est la mécanique d'``inventaire.yaml``, appliquée aux phrases du site.

Trois choses, et l'action 34 de la feuille de route dit pourquoi chacune :

* **L'extrait est encore là.** Chaque entrée porte un extrait verbatim, cherché
  dans les témoins des pages — le HTML que le portage JavaScript rend
  caractère pour caractère, donc le site. Une phrase réécrite sans repasser
  par le catalogue fait échouer le test.
* **Le contrôle passe.** Une entrée ``verifiee`` nomme un contrôle qui
  interroge le MODÈLE, jamais le texte. Une entrée ``contredite`` nomme
  l'action qui la refermera et un contrôle qui vérifie qu'elle est ENCORE
  contredite : il tombe le jour où l'action est faite, pour qu'on ne referme
  pas l'action en oubliant la phrase.
* **Rien n'échappe au catalogue.** Toute phrase forte des pages — le contenu
  des ``<strong>`` d'au moins trois mots, ou qui fait une phrase — est dans le
  catalogue, ou déclarée ``sans_portee``. Une phrase nouvelle ne peut pas
  entrer sans qu'on ait dit ce qu'elle engage.
* **Une affirmation sur le monde cite sa source.** La page Risque est une
  revue de littérature : ce que la Grèce a coupé, ce que les juges en ont
  fait. Aucun contrôle du modèle ne peut trancher cela, et ce n'est pas pour
  autant sans portée. L'état ``hors_modele`` le dit, et le test exige alors
  que la source soit citée dans la page même.

Les contrôles sont écrits ici, sous le nom que le catalogue leur donne, et
reçoivent le modèle chargé une fois pour le module. Un contrôle qui lit le
texte d'un témoin le fait pour vérifier qu'une branche du rendu SUIT le
modèle — jamais pour vérifier le texte par lui-même.
"""

from __future__ import annotations

import html
import json
import math
import re
from dataclasses import fields, replace
from functools import cached_property
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.avantages import LIGNES_LUES
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import ANCRAGE_SALAIRE_MOYEN, salaire_moyen_annuel
from retraite_notionnelle.castypes import GENERATIONS, calculer_cas_types
from retraite_notionnelle.config import (
    ModeIndexation,
    Parametres,
    RevalorisationStock,
)
from retraite_notionnelle.cout import (
    CONVENTION_RAPPORT,
    calculer_cout,
    financer,
)
from retraite_notionnelle.donnees.bilan import charger_bilan
from retraite_notionnelle.donnees.chargement import Fiabilite, journal_certification
from retraite_notionnelle.donnees.distribution import DistributionPensions, part_femmes
from retraite_notionnelle.garantie import (
    cout_garantie,
    cout_garantie_par_sexe,
)
from retraite_notionnelle.moteur.indexation import Indexation
from retraite_notionnelle.remuneration import AnneeComparee, charger_prelevements
from retraite_notionnelle.scenarios.actuel import MinimumVieillesse, _coefficient_anticipation
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web import gabarit as g
from retraite_notionnelle.web.pages import (
    CLES_MODELISATION,
    COMPOSANTE_GARANTIE,
    COR_2070,
    INDEXATIONS,
    LIGNES_DEPENSES,
    LIGNES_RECETTES,
    MARCHES_SYSTEMES,
    MODES_MONTANT,
    NATURES_PART_EMPLOYEUR,
    ORGANISMES,
    POSTES_TRANSFERTS,
    SCENARIOS_MONTRES,
    TAUX_ACTUEL_PATRONAL,
    TAUX_ACTUEL_SALARIAL,
    TAUX_ACTUEL_TOTAL,
    TITRES,
    Contexte,
    ErreurSaisie,
    Saisie,
    _cumuls_indexation,
    _deplacement_des_ecarts,
    _libelles_cascade,
    _marches_cascade,
    _options_statuts,
    _reglage_proposition,
)

RACINE = Path(__file__).resolve().parents[1]
CATALOGUE = RACINE / "data" / "reference" / "site" / "affirmations.yaml"
TEMOINS = RACINE / "tests" / "temoins" / "pages.json"
FEUILLE_DE_ROUTE = RACINE / "docs" / "feuille_de_route.md"
ETATS = ("verifiee", "contredite", "hors_modele", "sans_portee")
#: Longueur minimale d'un extrait. Elle ne vise pas la précision — c'est le
#: test de présence qui la donne — mais le hasard : une poignée de caractères
#: se retrouve dans n'importe quelle page, et l'entrée ne désignerait plus
#: rien. « En clair. » et « Réserve. » sont les deux plus courts du catalogue,
#: et leur point final les distingue.
LONGUEUR_MINIMALE_EXTRAIT = 8

# -- le texte des pages ------------------------------------------------------

_BALISE = re.compile(r"<[^>]+>")
_BLANCS = re.compile(r"\s+")
_FORT = re.compile(r"<strong[^>]*>(.*?)</strong>", re.S)
_MOT = re.compile(r"[^\W\d_]{2,}")


def normaliser(fragment: str) -> str:
    """Balises retirées, entités traduites, blancs repliés : ce qu'on lit."""
    return _BLANCS.sub(" ", html.unescape(_BALISE.sub("", fragment))).strip()


def phrase_forte(texte: str) -> bool:
    """Un ``<strong>`` qui affirme, par opposition à un chiffre ou à un mot.

    Au moins trois mots de deux lettres, ou une phrase entière — un point, un
    deux-points, une interrogation à la fin. « 26,7 ans », « réversion »,
    « Salaire net » sont des étiquettes et des nombres : le modèle les
    produit, la prose ne les affirme pas.

    Un texte d'un seul tenant, sans espace, n'est pas une phrase non plus :
    ``age_jouissance_militaire`` est le code d'une ligne du modèle, cité tel
    quel sous « ce que le modèle a refusé de mesurer ». Le mettre au catalogue
    reviendrait à y mettre des identifiants, que rien n'affirme.
    """
    if " " not in texte:
        return False
    return len(_MOT.findall(texte)) >= 3 or texte.endswith((".", ":", "?", "!"))


def _charger_temoins() -> dict[str, dict]:
    pages = json.loads(TEMOINS.read_text(encoding="utf-8"))
    temoins = {
        nom: {
            "chemin": page["chemin"],
            # La saisie qui a produit le témoin : c'est elle qui dit si la page
            # a été calculée sous d'autres règles que celles par défaut, et
            # c'est plus sûr qu'une convention de nommage.
            "parametres": page.get("parametres", {}),
            "corps": page["corps"],
            "texte": normaliser(page["corps"]),
        }
        for nom, page in pages.items()
    }
    # Le pied de page est commun à toutes et n'est pas dans les témoins : il
    # entre sous le chemin « * », que le catalogue emploie pour lui.
    temoins["*pied"] = {"chemin": "*", "parametres": {}, "corps": g.pied(),
                        "texte": normaliser(g.pied())}
    return temoins


def _charger_catalogue() -> list[dict]:
    return yaml.safe_load(CATALOGUE.read_text(encoding="utf-8"))["affirmations"]


TEMOINS_PAR_NOM = _charger_temoins()
AFFIRMATIONS = _charger_catalogue()
PAR_ID = {entree["id"]: entree for entree in AFFIRMATIONS}


def pages_de(entree: dict) -> tuple[str, ...]:
    page = entree["page"]
    return tuple(page) if isinstance(page, list) else (page,)


def textes_de(chemin: str) -> list[str]:
    """Le texte de chaque témoin rendu sous ce chemin."""
    return [t["texte"] for t in TEMOINS_PAR_NOM.values() if t["chemin"] == chemin]


# -- le modèle, chargé une fois ---------------------------------------------


class Modele:
    """Le modèle sous les règles par défaut, et quelques carrières.

    Tout est paresseux et mémorisé : un contrôle qui ne regarde qu'une
    carrière ne paie pas le coût agrégé, et le coût n'est calculé qu'une fois
    pour tous ceux qui le lisent.
    """

    def __init__(self) -> None:
        self.contexte = Contexte()
        self.sim = self.contexte.simulateur()
        self.base = self.contexte.base
        self._simulations: dict[tuple, object] = {}

    def simuler(self, **parametres):
        cle = tuple(sorted(parametres.items()))
        if cle not in self._simulations:
            self._simulations[cle] = self.contexte.simuler(Saisie(**parametres))
        return self._simulations[cle]

    def simuler_requete(self, **parametres):
        cle = ("requete",) + tuple(sorted(parametres.items()))
        if cle not in self._simulations:
            saisie = Saisie.depuis_requete({k: str(v) for k, v in parametres.items()})
            self._simulations[cle] = self.contexte.simuler(saisie)
        return self._simulations[cle]

    # Les carrières que les contrôles se partagent.
    @cached_property
    def defaut(self):
        return self.simuler()

    @cached_property
    def fonctionnaire(self):
        return self.simuler(statut="fonctionnaire_etat", primes=0.2)

    @cached_property
    def artisan(self):
        return self.simuler(statut="artisan")

    @cached_property
    def smic(self):
        return self.simuler(salaire=0.35, unite_revenu="moyen", debut=20, liquidation=67)

    @cached_property
    def smic_en_couple(self):
        return self.simuler(salaire=0.35, unite_revenu="moyen", debut=20,
                            liquidation=67, foyer="couple")

    @cached_property
    def deja_liquidee(self):
        """Une carrière liquidée en 2012, bien avant la bascule."""
        return self.simuler(statut="agent_sncf", naissance=1960, liquidation=52,
                            debut=20)

    @cached_property
    def haut_revenu(self):
        """Dix fois le salaire moyen : le plus haut revenu que le formulaire accepte."""
        return self.simuler(salaire=10, unite_revenu="moyen", naissance=1990,
                            debut=22, liquidation=64)

    @cached_property
    def cout(self):
        return self.contexte.cout()

    @cached_property
    def cout_convention_rapport(self):
        """Le même coût sous l'autre convention de recette de la proposition."""
        c = self.contexte
        return calculer_cout(self.sim, c.depenses(), c.population(), c.comptes(),
                             assiette=c.assiette(), convention_recette=CONVENTION_RAPPORT)

    @cached_property
    def grille_cas_types(self):
        """Les treize carrières croisées avec sept générations, une fois."""
        return calculer_cas_types(self.sim)

    @cached_property
    def avantages(self):
        return self.contexte.avantages()

    @cached_property
    def inventaire(self):
        return self.contexte.inventaire_avantages()

    @cached_property
    def cumuls(self) -> dict[str, float]:
        return _cumuls_indexation(self.contexte)

    @property
    def solde(self):
        return self.cout.solde

    @property
    def observe(self):
        return self.solde.annee(self.solde.derniere_annee_observee)

    @property
    def horizon(self):
        return self.solde.annee(self.solde.derniere_annee)

    @property
    def projetees(self):
        return [ligne for ligne in self.solde.annees if ligne.projete]


@pytest.fixture(scope="module")
def modele() -> Modele:
    return Modele()


# -- les contrôles ------------------------------------------------------------
#
# Chacun porte le nom que le catalogue lui donne. Il reçoit le modèle et
# affirme ; un contrôle absent du registre fait échouer le test de forme.

CONTROLES: dict[str, object] = {}


def controle(*noms: str):
    def enregistrer(fonction):
        for nom in noms:
            assert nom not in CONTROLES, nom
            CONTROLES[nom] = fonction
        return fonction
    return enregistrer


def _proche(a: float, b: float, relatif: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=relatif, abs_tol=1e-9)


def _champs(classe) -> set[str]:
    return {champ.name for champ in fields(classe)}


# .. le compte, la conversion, la pension ....................................


@controle("compte_notionnel_en_euros")
def _(m: Modele):
    compte = m.defaut.notionnel_retroactif.compte
    assert compte.capital > 0
    assert _proche(compte.cotisations_versees,
                   sum(c.cotisation for c in compte.cotisations))
    assert compte.capital > compte.cotisations_versees > 0
    assert _proche(compte.rendement_cumule, compte.capital / compte.cotisations_versees)
    assert all(c.cotisation >= 0 for c in compte.cotisations)


@controle("pension_egale_capital_sur_diviseur")
def _(m: Modele):
    retro = m.defaut.notionnel_retroactif
    assert _proche(retro.pension_annuelle * retro.conversion.diviseur,
                   retro.capital_notionnel)
    liberal = m.smic.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    complement = garantie.complement if garantie.servie_a_la_liquidation else 0.0
    assert _proche(liberal.pension_annuelle,
                   liberal.capital_notionnel / liberal.conversion.diviseur + complement)


@controle("diviseur_est_l_esperance_de_vie")
def _(m: Modele):
    conversion = m.defaut.notionnel_retroactif.conversion
    assert conversion.taux_anticipe == 0.0
    assert _proche(conversion.diviseur, conversion.esperance_residuelle)


@controle("cumul_sur_l_esperance_egale_le_capital")
def _(m: Modele):
    retro = m.defaut.notionnel_retroactif
    assert _proche(retro.pension_annuelle * retro.conversion.esperance_residuelle,
                   retro.capital_notionnel)


@controle("diviseur_par_generation")
def _(m: Modele):
    assert m.base.table_generation
    un = m.defaut.notionnel_retroactif.conversion
    autre = m.simuler(naissance=1960, liquidation=64).notionnel_retroactif.conversion
    assert "generation" in un.table
    assert un.age_liquidation == autre.age_liquidation
    assert not _proche(un.diviseur, autre.diviseur)


@controle("a_capital_egal_pension_egale")
def _(m: Modele):
    """Le diviseur ne dépend que de l'âge, de la date et de la population."""
    for comparaison in (m.defaut, m.fonctionnaire):
        resultat = comparaison.notionnel_retroactif
        carriere = comparaison.carriere
        conversion = resultat.conversion
        population = conversion.table.split("_generation_", 1)[1] \
            if "_generation_" in conversion.table else None
        refait = m.sim.convertisseur.coefficient(
            carriere.age_liquidation, carriere.annee_liquidation, carriere.sexe,
            carriere.mois_liquidation, population=population,
        )
        assert _proche(refait.diviseur, conversion.diviseur)
        assert _proche(resultat.pension_annuelle * refait.diviseur, resultat.capital_notionnel)


@controle("rendement_independant_de_la_carriere")
def _(m: Modele):
    """Une seule indexation, sans argument de carrière, pour tous les comptes."""
    import inspect
    indexation = m.sim.indexation
    assert m.sim.constructeur.indexation is indexation
    assert m.sim.constructeur_liberal.indexation is indexation
    assert m.sim.constructeur_employeur.indexation is indexation
    assert list(inspect.signature(indexation.taux).parameters) == ["annee"]


@controle("indexation_masse_salariale_par_defaut")
def _(m: Modele):
    assert m.base.mode_indexation is ModeIndexation.MASSE_SALARIALE
    assert m.sim.indexation.lissage == 1


@controle("premiere_ligne_indexation_par_defaut")
def _(m: Modele):
    assert INDEXATIONS[0][0] == Saisie.indexation == m.base.mode_indexation.value


@controle("pension_actuelle_depend_du_statut")
def _(m: Modele):
    un, autre = m.defaut.actuel.pension_annuelle, m.fonctionnaire.actuel.pension_annuelle
    assert abs(un / autre - 1) > 0.01


@controle("interruption_ne_coute_que_ses_cotisations")
def _(m: Modele):
    pleine = {c.annee: c for c in m.defaut.notionnel_retroactif.compte.cotisations}
    hachee = m.simuler(interruptions="2005:2007:education_enfant").notionnel_retroactif
    trouee = {c.annee: c for c in hachee.compte.cotisations}
    assert set(trouee) == set(pleine)
    for annee, cotisation in trouee.items():
        if 2005 <= annee <= 2007:
            assert cotisation.nulle
        else:
            assert _proche(cotisation.cotisation, pleine[annee].cotisation)
    assert _proche(hachee.pension_annuelle * hachee.conversion.diviseur,
                   hachee.capital_notionnel)


@controle("assiette_deplafonnee_apres_la_bascule")
def _(m: Modele):
    """Au plus haut revenu du formulaire, tout le revenu entre au compte.

    Ce contrôle a d'abord dit le contraire : il constatait le plafond de huit
    plafonds de la Sécurité sociale que le modèle posait par-dessus le régime
    fusionné, et tombait le jour où l'action 61 le lèverait. Elle est faite.

    La vérification porte sur la carrière la plus haute que le formulaire
    accepte — dix fois le salaire moyen —, parce que c'est la seule où la
    question se posait : en deçà de 9,2 fois le salaire moyen, aucun plafond
    n'a jamais mordu. AVANT la bascule, en revanche, les bornes des fiches
    rognent toujours, et elles le doivent : c'est le droit qui s'appliquait.
    """
    assert m.base.plafond_assiette_en_pass is None
    apres = [c for c in m.haut_revenu.notionnel_liberal.compte.cotisations
             if c.annee >= m.base.annee_bascule and not c.nulle]
    assert apres
    assert all(c.assiette_retenue >= c.revenu - 1.0 for c in apres)


# .. la bascule, le taux unique, le régime unique ...........................


@controle("taux_unique_apres_bascule")
def _(m: Modele):
    taux = m.base.taux_cotisation_liberal
    for comparaison in (m.defaut, m.fonctionnaire, m.artisan):
        apres = [c for c in comparaison.notionnel_liberal.compte.cotisations
                 if c.annee >= m.base.annee_bascule and not c.nulle]
        assert apres
        assert all(_proche(c.taux_effectif, taux) for c in apres)


@controle("regime_unique_apres_bascule")
def _(m: Modele):
    fusionne = m.sim.regime_fusionne
    assert fusionne.annee_bascule == m.base.annee_bascule
    assert fusionne.age_ouverture > 0
    assert fusionne.assiette == "deplafonnee"
    assert fusionne.taux_cotisation_retraite > 0
    assert fusionne.avantages_non_contributifs == ()


@controle("proposition_retroactive")
def _(m: Modele):
    """Une pension liquidée avant la bascule est recalculée, à la carrière comme au coût."""
    comparaison = m.deja_liquidee
    assert comparaison.carriere.annee_liquidation < m.base.annee_bascule
    assert not _proche(comparaison.notionnel_liberal.pension_annuelle,
                       comparaison.actuel.pension_annuelle, 1e-3)
    assert "notionnel_liberal" not in m.cout.confondus_avec_actuel()
    observees = [ligne for ligne in m.solde.annees if not ligne.projete]
    assert all(ligne.rapports["notionnel_liberal"] != 1.0 for ligne in observees)


@controle("quatre_systemes_meme_carriere")
def _(m: Modele):
    assert len(SCENARIOS_MONTRES) == 4 and SCENARIOS_MONTRES[0] == "actuel"
    comparaison = m.defaut
    for scenario in SCENARIOS_MONTRES:
        assert getattr(comparaison, scenario).pension_annuelle > 0
    assert comparaison.variation("notionnel_retroactif") == (
        comparaison.notionnel_retroactif.pension_annuelle
        / comparaison.actuel.pension_annuelle - 1.0)


# .. la garantie vieillesse ...................................................


@controle("garantie_individualisee")
def _(m: Modele):
    assert MinimumVieillesse.AGE_OUVERTURE == 65
    seul = m.smic.notionnel_liberal.garantie_vieillesse
    couple = m.smic_en_couple.notionnel_liberal.garantie_vieillesse
    coefficient = seul.coefficient_prix
    assert _proche(seul.base_annuelle, m.base.garantie_vieillesse_mensuelle * 12 * coefficient)
    assert _proche(seul.isolement_annuel,
                   m.base.allocation_isolement_mensuelle * 12 * coefficient)
    assert _proche(seul.plancher_annuel, seul.base_annuelle + seul.isolement_annuel)
    assert couple.isolement_annuel == 0.0
    assert _proche(couple.plancher_annuel, couple.base_annuelle)
    assert not any("conjoint" in nom for nom in _champs(Parametres))


@controle("garantie_comptee_a_part")
def _(m: Modele):
    liberal = m.smic.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    assert garantie.servie_a_la_liquidation and garantie.complement > 0
    assert _proche(liberal.pension_annuelle - garantie.complement,
                   liberal.capital_notionnel / liberal.conversion.diviseur)
    assert m.cout.cumul(COMPOSANTE_GARANTIE) > 0
    assert "garantie_vieillesse" in m.horizon.postes_depenses("notionnel_liberal")


@controle("deplacement_uniforme_borne_basse")
def _(m: Modele):
    """Le rapport est lu sur l'enquête, il vaut moins de un, et le modèle l'applique.

    La phrase affirme trois choses. Que le rapport est MESURÉ : il sort des
    caractéristiques des retraités par sexe, pas d'une hypothèse. Qu'il est
    inférieur à un : les pensions des femmes tombent plus. Et que le modèle
    l'applique : c'est ce que le calage de la trajectoire porte, et non un
    calcul de côté. Le reste se vérifie sous contrainte de masse — la moyenne
    d'ensemble reste déplacée du facteur que la grille donne, et seul le
    partage entre les deux sexes change.
    """
    mesure = m.sim.caracteristiques.rapport_deplacement()
    assert 0.5 < mesure < 1.0
    # Et c'est bien lui que la trajectoire applique.
    assert m.base.rapport_deplacement_sexe is None
    racine = m.base.racine_donnees
    millesime = m.sim.distribution.millesime
    colonnes = {
        sexe: DistributionPensions(racine, sexe=sexe, millesime=millesime)
        for sexe in ("F", "H")
    }
    poids = part_femmes(racine, millesime)
    ligne = m.cout.annee(millesime)
    assert ligne is not None and ligne.garantie is not None
    vers = m.sim.macro.coefficient_prix(
        m.base.annee_euros_garantie_vieillesse, millesime)
    plancher = (m.base.garantie_vieillesse_mensuelle
                + m.base.allocation_isolement_mensuelle) * vers
    effectif = m.sim.effectifs.effectif("tous_regimes", millesime)
    couts = [
        cout_garantie_par_sexe(colonnes["F"], colonnes["H"], poids, effectif,
                               plancher, ligne.garantie.facteur, rapport).cout_annuel_meur
        for rapport in (1.0, 0.95, 0.90, 0.85, 0.80)
    ]
    # Jamais moins : c'est une borne basse.
    assert couts == sorted(couts)
    assert couts[-1] > couts[0]
    # Et seconde : moins d'un dixième au bout de la fourchette.
    assert couts[-1] / couts[0] < 1.10


@controle("garantie_hors_masse_contributive")
def _(m: Modele):
    """La dépense du scénario 6 ne porte pas sa garantie, qui s'y AJOUTE.

    Financée par l'impôt, la garantie a quitté la masse contributive le
    19 septembre 2026. La preuve tient en une égalité : sur le passé observé,
    le scénario 6 et le scénario 4 prélèvent les mêmes taux et ne diffèrent
    que par elle — si leurs masses sont égales au centime, c'est qu'elle n'est
    dans ni l'une ni l'autre. Et elle n'est pas nulle pour autant.
    """
    passe = m.cout.annee(m.cout.derniere_annee)
    assert passe.cout_constants("notionnel_liberal") == pytest.approx(
        passe.cout_constants("notionnel_retroactif_employeur"))
    assert passe.cout_constants(COMPOSANTE_GARANTIE) > 0.0
    # À l'horizon, le taux unique les sépare — dans l'autre sens : le
    # scénario 6 coûte MOINS, sa garantie restant par-dessus le marché.
    horizon = m.cout.avenir.annee(m.cout.avenir.derniere_annee)
    assert (horizon.cout_constants("notionnel_liberal")
            < horizon.cout_constants("notionnel_retroactif_employeur"))
    assert horizon.cout_constants(COMPOSANTE_GARANTIE) > 0.0
    # Et le bilan dit la même chose de l'autre côté : la composante n'entre
    # pas dans la dépense du système, elle est portée pour mémoire.
    postes = m.horizon.postes_depenses("notionnel_liberal")
    assert postes["garantie_vieillesse"] > 0.0
    assert (postes["droits_directs"] + postes["droits_derives"]
            == pytest.approx(m.horizon.depense("notionnel_liberal")))


@controle("garantie_remplace_les_minima")
def _(m: Modele):
    assert m.sim.regime_fusionne.avantages_non_contributifs == ()
    assert m.smic.actuel.minimum_applique
    assert m.smic.notionnel_liberal.garantie_vieillesse.complement > 0
    neutralisations = _champs(type(m.base.neutralisations))
    assert {"minimum_contributif", "minimum_garanti", "minimum_vieillesse_aspa",
            "pension_majoree_reference"} <= neutralisations


@controle("garantie_compte_la_rente_volontaire")
def _(m: Modele):
    liberal = m.smic.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    assert liberal.capitalisation.rente_volontaire > 0
    assert _proche(garantie.rente_capitalisee, liberal.capitalisation.rente_annuelle)
    assert _proche(garantie.ressources,
                   garantie.pension_contributive + garantie.rente_capitalisee)


@controle("garantie_est_une_avance_reprise")
def _(m: Modele):
    avenir = m.cout.avenir
    assert avenir.cumul_reprises() > 0
    ligne = avenir.annee(avenir.derniere_annee)
    garantie = ligne.garantie
    assert garantie.avances_liberees_constants > 0
    assert _proche(ligne.reprises_constants() / garantie.avances_liberees_constants,
                   garantie.part_reprise)
    # Aucun seuil d'actif net : l'ASPA en a un, la garantie n'en a pas.
    assert not any("seuil" in nom for nom in _champs(Parametres))


@controle("avances_par_succession")
def _(m: Modele):
    """Le conjoint survivant porte souvent la sienne : la succession en affronte plus d'une.

    Et le sens compte : une avance plus grosse est MOINS bien couverte par un
    patrimoine de ménage, non mieux. La part de reprise doit donc baisser
    quand le nombre d'avances par succession monte.
    """
    garantie = m.cout.avenir.annee(m.cout.avenir.derniere_annee).garantie
    assert 1.0 < garantie.avances_par_succession < 2.0
    assert 0 < garantie.part_reprise < 1


@controle("garantie_brute_et_nette")
def _(m: Modele):
    ligne = m.cout.avenir.annee(m.cout.avenir.derniere_annee)
    assert ligne.reprises_constants() > 0
    assert _proche(ligne.garantie_nette_constants(),
                   ligne.cout_constants(COMPOSANTE_GARANTIE) - ligne.reprises_constants())


@controle("part_de_reprise_est_un_reglage")
def _(m: Modele):
    """La part couverte est LUE sur le patrimoine des retraités, ou posée.

    Elle était un réglage à un demi jusqu'au 20 septembre 2026 ; elle se
    calcule depuis sur la distribution de patrimoine, et le réglage la
    remplace quand il est donné.
    """
    assert "part_reprise_garantie" in _champs(Parametres)
    assert m.base.part_reprise_garantie is None
    part = m.cout.avenir.annee(m.cout.avenir.derniere_annee).garantie.part_reprise
    assert 0 < part < 1
    force = replace(m.base, part_reprise_garantie=1.0)
    assert force.part_reprise_garantie == 1.0


@controle("recours_un_sur_deux")
def _(m: Modele):
    assert "taux_recours_garantie" in _champs(Parametres)
    assert m.base.taux_recours_garantie == 0.5


@controle("garantie_differentielle_sur_la_queue_basse")
def _(m: Modele):
    """Seules les pensions SOUS le plancher coûtent, et d'autant moins qu'il est bas."""
    distribution = m.contexte.distribution()
    effectif = m.sim.effectifs.effectif("tous_regimes", distribution.millesime)
    vers_enquete = m.sim.macro.coefficient_prix(
        m.base.annee_euros_garantie_vieillesse, distribution.millesime)
    plancher = m.base.garantie_vieillesse_mensuelle * vers_enquete
    chiffres = [cout_garantie(distribution, effectif, plancher * part)
                for part in (0.25, 0.5, 1.0)]
    couts = [c.cout_annuel_meur for c in chiffres]
    parts = [c.part_beneficiaires for c in chiffres]
    assert couts == sorted(couts) and couts[0] < couts[-1]
    assert parts == sorted(parts) and 0 < parts[-1] < 1
    # La part des bénéficiaires est exactement celle de la distribution sous
    # le plancher : la garantie ne regarde rien au-dessus.
    assert _proche(parts[-1], distribution.part_sous(plancher), 1e-3)


@controle("facteur_de_deplacement_inferieur_a_un")
def _(m: Modele):
    millesime = m.contexte.distribution().millesime
    ligne = m.cout.annee(millesime)
    assert ligne.garantie is not None
    assert 0 < ligne.garantie.facteur < 1


@controle("distribution_brute_de_droit_direct")
def _(m: Modele):
    assert "brutes de droit direct" in (DistributionPensions.__doc__ or "")


# .. le pilier capitalisé ......................................................


@controle("pilier_capitalise_en_plus")
def _(m: Modele):
    assert m.base.capitalisation_obligatoire
    liberal = m.defaut.notionnel_liberal
    assert liberal.capitalisation is not None and liberal.capitalisation.capital > 0
    assert _proche(liberal.pension_totale,
                   liberal.pension_annuelle + liberal.rente_capitalisation_obligatoire)
    apres = [c for c in liberal.compte.cotisations
             if c.annee >= m.base.annee_bascule and not c.nulle]
    assert all(_proche(c.taux_effectif, m.base.taux_cotisation_liberal) for c in apres)


@controle("l_allocation_ne_vaut_que_sous_une_prime_de_terme")
def _(m: Modele):
    """Sous le réglage par défaut, adossement et roulement rendent le même euro.

    C'est ce que la page affirme, et c'est ce qui justifie le menu : la valeur
    de l'allocation est nulle tant que les forwards sont pris pour les taux
    futurs, et elle apparaît dès qu'une prime de terme est retirée.
    """
    import contextlib

    from retraite_notionnelle.moteur import capitalisation as module

    @contextlib.contextmanager
    def roulement_a_un_an():
        ancienne = module.repartition
        module.repartition = lambda h: ((1, 1.0),) if h > 0 else ()
        try:
            yield
        finally:
            module.repartition = ancienne

    carriere = dict(annee_naissance=2004, sexe="H",
                    affiliation="salarie_prive_non_cadre",
                    age_debut=22, age_liquidation=64)

    def capital(parametres) -> float:
        simulateur = Simulateur(parametres)
        resultat = simulateur.simuler(simulateur.carriere_simple(**carriere))
        return resultat.notionnel_liberal.capitalisation.capital

    assert m.base.prime_terme_trente_ans == 0.0, "le site publie sous les forwards"
    defaut = m.base.sous_regime_taux("forwards")
    assert defaut == m.base
    with roulement_a_un_an():
        roule = capital(defaut)
    assert _proche(capital(defaut), roule, relatif=1e-9)

    avec_prime = m.base.sous_regime_taux("prime")
    assert avec_prime.prime_terme_trente_ans > 0
    with roulement_a_un_an():
        roule_prime = capital(avec_prime)
    assert capital(avec_prime) > roule_prime


@controle("cinq_points_volontaires_separes")
def _(m: Modele):
    assert m.base.taux_capitalisation_obligatoire == 0.05
    assert m.base.taux_capitalisation_volontaire_applique == 0.05
    assert _proche(m.base.taux_capitalisation_applique, 0.10)
    pilier = m.defaut.notionnel_liberal.capitalisation
    assert _proche(pilier.taux_cotisation, m.base.taux_capitalisation_applique)
    assert pilier.rente_volontaire > 0
    assert _proche(pilier.rente_obligatoire + pilier.rente_volontaire, pilier.rente_annuelle)


@controle("rente_volontaire_proportionnelle")
def _(m: Modele):
    pilier = m.defaut.notionnel_liberal.capitalisation
    assert _proche(pilier.rente_volontaire / pilier.rente_annuelle,
                   pilier.taux_cotisation_volontaire / pilier.taux_cotisation)


@controle("effort_inchange")
def _(m: Modele):
    assert round(m.base.taux_retraite_propose * 100) == round(TAUX_ACTUEL_TOTAL * 100)
    assert _proche(m.base.taux_retraite_propose,
                   m.base.taux_cotisation_liberal + m.base.taux_capitalisation_applique)


@controle("capital_capitalise_transmissible")
def _(m: Modele):
    pilier = m.defaut.notionnel_liberal.capitalisation
    assert pilier.capital > 0
    assert 0 < pilier.probabilite_deces_avant_liquidation < 1
    assert 0 < pilier.esperance_capital_transmis < pilier.capital
    # Le compte notionnel, lui, n'a rien à transmettre : aucun champ ne le dit.
    assert not any("transmis" in nom for nom in _champs(type(m.defaut.notionnel_retroactif.compte)))


@controle("pilier_sort_en_rente")
def _(m: Modele):
    pilier = m.defaut.notionnel_liberal.capitalisation
    assert pilier.annee_liquidation == m.defaut.carriere.annee_liquidation
    attendue = (pilier.capital / pilier.conversion.diviseur
                * pilier.facteur_encours_rente * (1 - pilier.frais_arrerages))
    assert _proche(pilier.rente_annuelle, attendue)


@controle("pilier_adosse_a_la_date_du_depart")
def _(m: Modele):
    """Un versement achète la maturité de son horizon, et rien d'autre.

    L'échelle de maturités qui glissait du long vers le court est tombée le
    20 septembre 2026 : sous les anticipations pures, le découpage laissait le
    capital inchangé au centime. Deux propriétés la remplacent, et ce sont
    elles que la page affirme : aucune maturité au-delà de l'horizon, aucune
    échéance avant le départ tant que la courbe couvre l'horizon.
    """
    from retraite_notionnelle.moteur.capitalisation import MATURITE_MAXIMALE, repartition

    for horizon in (2, 10, 17, 30, 40):
        lignes = repartition(horizon)
        assert len(lignes) == 1, (horizon, lignes)
        (maturite, poids), = lignes
        assert poids == 1.0
        assert maturite == min(horizon, MATURITE_MAXIMALE)
    pilier = m.defaut.notionnel_liberal.capitalisation
    for annee in pilier.annees:
        for maturite, _ in annee.placements:
            assert maturite <= annee.horizon


@controle("pilier_place_sur_la_courbe_sans_risque")
def _(m: Modele):
    pilier = m.defaut.notionnel_liberal.capitalisation
    assert pilier.date_courbe == m.sim.courbe_taux.date
    assert pilier.annees[0].placements


@controle("rendement_du_pilier_est_le_taux_interne")
def _(m: Modele):
    pilier = m.defaut.notionnel_liberal.capitalisation
    taux = pilier.taux_rendement_annuel
    assert pilier.interets > 0
    refait = sum(a.versement_brut * (1 + taux) ** (pilier.annee_liquidation - a.annee)
                 for a in pilier.annees if a.versement_brut > 0)
    assert _proche(refait, pilier.capital, 1e-6)


@controle("pilier_sans_annee_pour_rapporter")
def _(m: Modele):
    comparaison = m.simuler_requete(
        naissance="1962-03-15", debut="1984-09", liquidation="2026-07",
        metier2_debut="2019-04", metier2_statut="chomage_indemnise")
    pilier = comparaison.notionnel_liberal.capitalisation
    assert pilier is not None and pilier.actif
    assert pilier.interets == 0.0 and pilier.taux_rendement_annuel == 0.0


@controle("frais_baissent_par_paliers")
def _(m: Modele):
    for paliers in (m.base.frais_gestion_paliers, m.base.frais_versement_paliers,
                    m.base.frais_arrerages_paliers):
        valeurs = [valeur for _, valeur in paliers]
        assert valeurs == sorted(valeurs, reverse=True)
        assert valeurs[-1] < valeurs[0]
    assert 0 < m.base.convergence_frais_stock < 1


@controle("frais_du_pilier_sources")
def _(m: Modele):
    for nom in ("frais_versement_capitalisation", "frais_gestion_capitalisation",
                "frais_arrerages_capitalisation", "frais_encours_rente_capitalisation"):
        assert getattr(m.base, nom) >= 0
    sources = (RACINE / "data" / "sources.yaml").read_text(encoding="utf-8")
    assert "Observatoire des produits d'épargne financière" in sources


@controle("sources_du_pilier")
def _(m: Modele):
    series = journal_certification(m.sim.macro.racine).get("series", {})
    assert series["courbe_taux_sans_risque"].get("niveau", "certifiee") == "certifiee"
    sources = (RACINE / "data" / "sources.yaml").read_text(encoding="utf-8")
    assert "Banque centrale européenne" in sources
    assert "Observatoire des produits d'épargne financière" in sources


# .. la fiche de paie ...........................................................


@controle("prelevement_mensuel_du_salaire_moyen")
def _(m: Modele):
    """Ce que la retraite prélève chaque mois : les deux parts de la fiche."""
    from retraite_notionnelle.web.pages import (
        DEBUT_RISQUE, LIQUIDATION_RISQUE, NAISSANCE_RISQUE, NIVEAUX_RISQUE,
    )

    _, niveau = NIVEAUX_RISQUE[1]
    comparaison = m.simuler(naissance=NAISSANCE_RISQUE,
                            statut="salarie_prive_non_cadre", debut=DEBUT_RISQUE,
                            liquidation=LIQUIDATION_RISQUE, salaire=niveau,
                            unite_revenu="moyen")
    fiche = comparaison.remuneration.reference.droit_en_vigueur
    prelevement = fiche.retraite_totale / 12.0
    assert prelevement > 0
    # Les deux parts, et c'est ce que la phrase dit : ce que verse l'employeur
    # y est. Seule la réduction générale les sépare du total prélevé.
    assert fiche.retraite_salarie > 0 and fiche.retraite_employeur > 0
    assert normaliser(g.euros(prelevement)) in TEMOINS_PAR_NOM["risque"]["texte"]


@controle("fiche_de_paie_ecart_net")
def _(m: Modele):
    """L'écart affiché est celui des deux nets, quel qu'en soit le signe.

    Il était négatif tant que les cinq points volontaires sortaient du net
    affiché ; ils en sont sortis le 20 septembre 2026, et le chiffre est
    devenu positif. La phrase, elle, ne promet qu'une différence.
    """
    remuneration = m.defaut.remuneration
    reference = remuneration.reference
    assert _proche(remuneration.gain_net_mensuel,
                   (reference.proposition.net - reference.droit_en_vigueur.net) / 12)
    assert remuneration.gain_net_mensuel != 0.0


@controle("epargne_a_votre_nom")
def _(m: Modele):
    reference = m.defaut.remuneration.reference
    lignes = [l for l in reference.proposition.lignes
              if l.code == AnneeComparee.CODE_CAPITALISATION]
    assert lignes
    assert _proche(reference.epargne_a_votre_nom,
                   sum(l.salarie + l.employeur for l in lignes))


@controle("cout_du_travail_fixe")
def _(m: Modele):
    remuneration = m.defaut.remuneration
    assert remuneration.affiche_cout_du_travail
    reference = remuneration.reference
    assert _proche(reference.proposition.cout_du_travail,
                   reference.droit_en_vigueur.cout_du_travail)


@controle("partage_des_vingt_trois_points")
def _(m: Modele):
    """La part patronale ne bouge pas, et la retenue tombe d'autant.

    Le partage était moitié-moitié jusqu'au 20 septembre 2026 ; il laisse
    désormais à l'employeur ce qu'il verse aujourd'hui, et toute la baisse va
    à la retenue du salarié. Deux propriétés le disent : la part patronale de
    la proposition égale celle du droit en vigueur, et le brut ne bouge pas.
    """
    part = m.base.part_salariale_taux_unique
    assert 0 < part < 0.5
    total = m.base.taux_cotisation_liberal + m.base.taux_capitalisation_obligatoire
    # Ce que la page écrit : la part patronale des 23 points est exactement
    # celle qu'un employeur verse aujourd'hui, et la retenue est le reste.
    assert _proche(total * (1 - part), TAUX_ACTUEL_PATRONAL, 1e-3)
    assert _proche(total * part, total - TAUX_ACTUEL_PATRONAL, 1e-3)
    assert total * part < TAUX_ACTUEL_SALARIAL
    # Et la baisse arrive sans passer par le brut : il ne bouge qu'à la marge,
    # par l'allègement recalculé, quand la retenue tombe de plus d'un tiers.
    reference = m.defaut.remuneration.reference
    avant, apres = reference.droit_en_vigueur, reference.proposition
    assert _proche(apres.cout_du_travail, avant.cout_du_travail)
    assert abs(apres.brut / avant.brut - 1) < 0.01
    assert apres.retraite_salarie < 0.75 * avant.retraite_salarie


@controle("volontaire_a_la_charge_de_l_assure")
def _(m: Modele):
    """Les cinq points rendus ne sont sur la fiche de personne, et pèsent leur montant.

    Ils étaient une ligne de la fiche jusqu'au 20 septembre 2026 ; ils sont
    devenus un virement que l'assuré décide, chiffré sur l'assiette de la
    proposition. Ce qui n'a pas changé : personne ne les cofinance, et ils ne
    déplacent ni le coût du travail, ni le brut, ni la CSG.
    """
    for comparaison in (m.defaut, m.fonctionnaire):
        reference = comparaison.remuneration.reference
        assert not any(l.code == "capitalisation_volontaire"
                       for l in reference.proposition.lignes)
        assert reference.epargne_volontaire > 0
        assert _proche(reference.epargne_volontaire,
                       reference.proposition.brut * reference.taux_epargne_volontaire)
        assert _proche(reference.net_apres_volontaire,
                       reference.proposition.net - reference.epargne_volontaire)


@controle("allegement_recalcule_sous_la_proposition")
def _(m: Modele):
    reference = m.smic.remuneration.reference
    avant, apres = reference.droit_en_vigueur, reference.proposition
    assert avant.reduction_generale > 0 and apres.reduction_generale > 0
    assert not _proche(avant.reduction_generale, apres.reduction_generale)


@controle("allegement_au_smic")
def _(m: Modele):
    """Au SMIC, le coefficient vaut la somme des taux visés : moins de retraite, moins de réduction, d'autant."""
    from retraite_notionnelle.remuneration import charger_prelevements
    reduction = charger_prelevements(m.base.racine_donnees).profil(
        "salarie_prive").reduction_generale
    assert _proche(reduction.coefficient_maximal, sum(reduction.composantes.values()))
    un, autre = 0.16, 0.09
    assert _proche(reduction.coefficient_maximal_avec(un) - reduction.coefficient_maximal_avec(autre),
                   un - autre)


@controle("fiche_sans_prelevements_annexes")
def _(m: Modele):
    codes = {l.code for l in m.defaut.remuneration.reference.proposition.lignes}
    assert not codes & {"taxe_apprentissage", "formation_professionnelle",
                        "participation_construction", "versement_mobilite",
                        "prevoyance", "mutuelle"}


@controle("independant_sans_employeur")
def _(m: Modele):
    remuneration = m.artisan.remuneration
    assert remuneration.profil == "independant"
    assert not remuneration.affiche_cout_du_travail
    reference = remuneration.reference
    assert _proche(reference.proposition.brut, reference.droit_en_vigueur.brut)
    assert all(l.employeur == 0.0 for l in reference.proposition.lignes)
    assert not m.artisan.contribution_employeur.a_un_employeur


@controle("fonctionnaire_assiette_fixe")
def _(m: Modele):
    """Aucun coût du travail affiché : ce que verse l'État est un taux d'équilibre.

    Le traitement lui-même ne se tient plus fixe depuis le 20 septembre 2026 :
    l'État cotisant 18 % comme tout employeur, la moitié de ce qu'il cesse de
    verser revient au traitement. Ce que la phrase engage, et qui n'a pas
    bougé, est le refus d'afficher un coût du travail pour ce statut.
    """
    remuneration = m.fonctionnaire.remuneration
    assert remuneration.profil == "agent_seul"
    assert not remuneration.affiche_cout_du_travail
    assert remuneration.libelle_assiette.lower().startswith("traitement")


@controle("allegement_absent_hors_prive")
def _(m: Modele):
    for comparaison in (m.fonctionnaire, m.artisan):
        reference = comparaison.remuneration.reference
        assert reference.droit_en_vigueur.reduction_generale == 0.0
        assert reference.proposition.reduction_generale == 0.0


@controle("part_employeur_publique_serie_a_part")
def _(m: Modele):
    employeur = m.fonctionnaire.contribution_employeur
    assert employeur.concerne_un_regime_public
    assert employeur.annees_par_origine
    assert set(employeur.annees_par_origine) <= set(NATURES_PART_EMPLOYEUR)


@controle("avertissement_smic")
def _(m: Modele):
    assert m.smic.remuneration.bute_sur_le_smic
    assert not m.defaut.remuneration.bute_sur_le_smic


# .. la page de résultats .....................................................


@controle("taux_de_remplacement_definition")
def _(m: Modele):
    comparaison = m.defaut
    assert comparaison.dernier_revenu_annualise > 0
    assert _proche(comparaison.taux_remplacement_actuel,
                   comparaison.actuel.pension_annuelle / comparaison.dernier_revenu_annualise)


@controle("pension_au_moment_du_depart")
def _(m: Modele):
    comparaison = m.defaut
    annee = comparaison.carriere.annee_liquidation
    assert comparaison.notionnel_retroactif.conversion.annee_liquidation == annee
    assert _proche(comparaison.coefficient_euros_constants,
                   m.sim.macro.coefficient_prix(annee, m.base.annee_euros_constants))


@controle("sous_total_contributif")
def _(m: Modele):
    actuel = m.smic.actuel
    assert actuel.avantages_appliques
    assert _proche(actuel.total_contributif + sum(a.montant for a in actuel.avantages_appliques),
                   actuel.pension_annuelle)


@controle("liquidation_non_ouverte_signalee")
def _(m: Modele):
    comparaison = m.simuler(liquidation=55, debut=30)
    assert not comparaison.actuel.liquidation_ouverte
    assert comparaison.actuel.motif_ouverture == "non_ouverte"
    assert comparaison.actuel.pension_annuelle > 0
    assert m.defaut.actuel.liquidation_ouverte


@controle("carriere_passee_sans_annee_projetee")
def _(m: Modele):
    derniere_observee = m.sim.macro.derniere_annee_observee
    annees = m.deja_liquidee.carriere.annees_cotisees
    assert annees and max(annees) <= derniere_observee
    assert max(m.defaut.carriere.annees_cotisees) > derniere_observee


@controle("carriere_lue_sur_releve")
def _(m: Modele):
    comparaison = m.simuler(
        releve="2000:salarie_prive_non_cadre:24000\n2001:artisan:25000",
        naissance=1975)
    lignes = [(l.annee, l.affiliation, l.revenu) for l in comparaison.carriere.lignes]
    assert lignes == [(2000, "salarie_prive_non_cadre", 24000.0), (2001, "artisan", 25000.0)]


@controle("saisie_hors_bornes_refusee")
def _(m: Modele):
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"naissance": "1975", "liquidation": "12"})
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"naissance": "1975", "enfants": "999"})


@controle("annee_civile_un_seul_statut")
def _(m: Modele):
    comparaison = m.simuler_requete(
        naissance="1962-03-15", debut="1984-09", liquidation="2026-07",
        metier2_debut="2019-04", metier2_statut="artisan")
    par_annee = {l.annee: l.affiliation for l in comparaison.carriere.lignes}
    assert len(par_annee) == len(comparaison.carriere.lignes)
    assert par_annee[2018] == "salarie_prive_non_cadre"
    # Avril : neuf mois d'artisan contre trois de salarié, l'année est à l'artisan.
    assert par_annee[2019] == "artisan"


@controle("statut_ferme_apres_son_recrutement")
def _(m: Modele):
    affiliations = m.sim.affiliations

    def ratp(entree: DateMois):
        for _, options in _options_statuts(affiliations, entree):
            for code, _, ouvert, attributs in options:
                if code == "agent_ratp":
                    return ouvert, attributs
        raise AssertionError("agent_ratp absent du menu")

    ouvert, attributs = ratp(DateMois(2024, 1))
    assert not ouvert and attributs.get("data-fermeture") == "2023-09"
    ouvert, _ = ratp(DateMois(2020, 1))
    assert ouvert


@controle("conversion_en_multiple_du_salaire_moyen", "revenu_saisi_en_euros_d_aujourd_hui")
def _(m: Modele):
    echelle = m.contexte.echelle(Saisie(montants="brut"))
    assert echelle.moyen > 0
    assert _proche(echelle.niveau(2500.0), 2500.0 * 12 / echelle.moyen)
    assert _proche(echelle.mensuel(echelle.niveau(2500.0)), 2500.0)
    # « Euros d'aujourd'hui » : l'échelle est celle de l'année courante du
    # modèle, non celle du départ ni celle des euros constants.
    assert Saisie.unite_revenu == "euros_mois"
    assert _proche(echelle.moyen, salaire_moyen_annuel(m.sim.macro, m.base.annee_courante))


@controle("ancrage_du_salaire_moyen")
def _(m: Modele):
    assert ANCRAGE_SALAIRE_MOYEN == (2024, 40_000.0)
    assert _proche(salaire_moyen_annuel(m.sim.macro, 2024), 40_000.0)


@controle("legende_rouge_vert")
def _(m: Modele):
    assert "162, 71, 46" in g.Cellule("x", intensite=-0.5).style()
    assert "90, 116, 80" in g.Cellule("x", intensite=0.5).style()
    assert g.Cellule("x", intensite=0.0).style() == ""


@controle("avertissement_des_reglages")
def _(m: Modele):
    """L'avertissement paraît sous d'autres réglages, et seulement là.

    LE CRITÈRE EST LA SAISIE, ET NON LE NOM DU TÉMOIN. Il l'a été jusqu'au
    21 septembre 2026 — « le nom finit par `_regles` » —, et c'était un proxy
    qui a tenu tant qu'un seul témoin agrégé portait d'autres règles. Le
    témoin de la variante de compte en porte aussi, sous un autre nom, et le
    proxy l'a dénoncé à tort. Ce qui décide est qu'une CLÉ DE MODÉLISATION
    soit saisie : `cascade` n'en est pas une — elle choisit l'année qu'on
    regarde, pas la règle qu'on applique —, et son témoin ne doit donc porter
    aucun avertissement.
    """
    extrait = PAR_ID["reglages.avertissement"]["extrait"]
    for nom, temoin in TEMOINS_PAR_NOM.items():
        if temoin["chemin"] not in ("/cas-types", "/cout", "/avantages"):
            continue
        regles = set(temoin["parametres"]) & set(CLES_MODELISATION)
        assert (extrait in temoin["texte"]) == bool(regles), nom


@controle("portage_compare_aux_temoins")
def _(m: Modele):
    assert (RACINE / "tests" / "js" / "comparer-pages.mjs").exists()
    assert (RACINE / "moteur" / "js" / "pages.js").exists()
    assert len(TEMOINS_PAR_NOM) > 10


# .. le coût, le solde, le coefficient ........................................


@controle("deux_parts_non_financees_distinctes")
def _(m: Modele):
    """Les deux « non financé » de la page Risque ne sont pas la même grandeur.

    L'un compare UNE PENSION à ce que les cotisations de cet assuré-là
    achèteraient ; l'autre compare LES DÉPENSES du système à ses recettes, une
    année donnée. Ils se lisaient tous deux « non financé », côte à côte, et
    un lecteur pouvait les additionner. Ce contrôle tient la phrase qui
    l'interdit : les deux parts existent, elles diffèrent, et la première est
    la plus grosse parce qu'elle ne compte que les cotisations.
    """
    comparaison = m.defaut
    promis = comparaison.actuel.pension_annuelle
    finance = comparaison.notionnel_retroactif_employeur.pension_annuelle
    part_promise = 1.0 - finance / promis
    ligne = m.horizon
    part_horizon = -ligne.solde("actuel") / ligne.depense("actuel")
    assert 0.0 < part_horizon < part_promise
    # Le second compte tout ce que le système encaisse, le premier les seules
    # cotisations : la part non cotisée des ressources est ce qui les sépare.
    assert ligne.part_contributive < 1.0


@controle("les_ecarts_bougent_si_chaque_systeme_s_equilibre")
def _(m: Modele):
    """Les quatre systèmes n'ont pas le même coefficient, et les écarts bougent.

    La page Cas types a affirmé pendant un temps que le coefficient
    d'équilibre « multiplierait les cases par le même facteur », et le
    catalogue la tenait pour vérifiée sous un contrôle qui vérifiait autre
    chose — que le coefficient n'est pas appliqué. La phrase était fausse deux
    fois : un facteur COMMUN laisserait ces cases inchangées, une case étant
    déjà un rapport de deux pensions ; et il n'y a pas un facteur mais quatre.
    Ce contrôle tient la phrase qui l'a remplacée.
    """
    ligne = m.horizon
    coefficients = {scenario: ligne.coefficient(scenario)
                    for scenario in SCENARIOS_MONTRES}
    assert len(set(round(valeur, 6) for valeur in coefficients.values())) == len(
        SCENARIOS_MONTRES), coefficients
    deplacement, cases = _deplacement_des_ecarts(
        m.grille_cas_types, m.solde, "notionnel_liberal")
    assert cases > 50, cases
    # « Déplacerait les écarts » n'est pas une figure de style : le
    # déplacement médian se compte en points, pas en centièmes de point.
    assert deplacement > 0.01, deplacement


@controle("coefficient_jamais_applique", "coefficient_calcule_jamais_applique")
def _(m: Modele):
    """Le coefficient est calculé ; la dépense ne le porte pas.

    Sert aux deux états : ``verifiee`` pour les phrases qui disent que le
    modèle n'applique rien, ``contredite`` pour celles qui promettent qu'un
    système notionnel se règle chaque année. L'action 11, qui appliquera le
    coefficient, ramènera la dépense à la recette : ce contrôle tombera, et
    le catalogue avec lui.
    """
    ecarts = [abs(ligne.coefficient("notionnel_liberal") - 1.0) for ligne in m.projetees]
    assert max(ecarts) > 0.01
    ligne = m.horizon
    for scenario in SCENARIOS_MONTRES:
        assert _proche(ligne.coefficient(scenario) * ligne.depense(scenario),
                       ligne.ressources_de(scenario))
    assert not _proche(ligne.depense("notionnel_liberal"),
                       ligne.ressources_de("notionnel_liberal"), 1e-3)


@controle("note_du_coefficient_suit_son_signe")
def _(m: Modele):
    """Les deux pages composent leur lecture depuis le solde, et disent son signe.

    Elles la portaient en dur : Cas types promettait « supérieur à un chaque
    année » quand le tableau de Coût chiffrait 0,92. Les deux lectures se
    calculent depuis ``_reglage_proposition`` depuis le 20 septembre 2026, et
    ce contrôle vérifie que les nombres écrits sont ceux du solde.
    """
    reglage = _reglage_proposition(m.solde)
    assert reglage["total"] > 0
    sous_un = reglage["sous_un"] == reglage["total"]
    assert sous_un == all(ligne.coefficient("notionnel_liberal") < 1.0
                          for ligne in m.projetees)
    dernier = reglage["dernier"]
    cout = TEMOINS_PAR_NOM["cout"]["texte"]
    cas_types = TEMOINS_PAR_NOM["cas_types"]["texte"]
    # La page Coût nomme l'écart du dernier coefficient, dans le bon sens.
    sens = "un manque de" if dernier < 1.0 else "une marge de"
    ecart = abs(1.0 - dernier)
    attendu = normaliser(f"de la proposition en {reglage['fin']} disent {sens} "
                         f"{g.pourcentage(ecart, decimales=0)}")
    assert attendu in cout, attendu
    # Cas types dit de quel côté de un se tient la proposition.
    cote = "inférieur à un" if sous_un else "supérieur à un"
    assert f"ce facteur est {cote}" in cas_types, cote
    for nom, texte in (("cout", cout), ("cas_types", cas_types)):
        assert normaliser(g.nombre(dernier, 2)) in texte, nom
        if sous_un:
            assert normaliser(g.nombre(reglage["minimum"], 2)) in texte, nom
            assert str(reglage["annee_minimum"]) in texte, nom


@controle("convention_comptable_est_une_hypothese")
def _(m: Modele):
    """Le déficit publié est d'APRÈS bouclage, et l'autre convention le dit.

    Sous EPR, ce que l'État verse aux régimes de fonctionnaires et aux régimes
    spéciaux suit chaque année ce qu'il faut pour les équilibrer : ces régimes
    ne montrent jamais de déficit, et le solde du système est celui des autres.
    Sous EEC, son effort est figé en part de PIB. Le COR publie les deux, et
    c'est la seule mesure française de ce qu'une convention comptable déplace.

    Trois choses tenues ici. Que l'écart CHANGE DE SIGNE : l'effort figé est
    sous le besoin tant que les régimes de fonctionnaires pèsent, au-dessus
    ensuite. Que la page écrive les deux soldes de l'année où les deux
    conventions se rejoignent. Et qu'elle nomme l'année du croisement, qui est
    ce qui empêche de lire l'écart comme un biais constant.
    """
    comptes = m.contexte.comptes()
    debut, fin = comptes.premiere_annee_eec, comptes.derniere_annee_eec
    ecarts = {annee: comptes.solde_eec(annee) - comptes.solde(annee)
              for annee in range(debut, fin + 1)}
    assert min(ecarts.values()) < 0 < max(ecarts.values()), "l'écart ne change pas de signe"
    croisement = next(annee for annee in sorted(ecarts) if ecarts[annee] >= 0)

    cout = TEMOINS_PAR_NOM["cout"]["texte"]
    assert str(croisement) in cout, croisement
    for valeur in (comptes.solde(fin), comptes.solde_eec(fin)):
        assert normaliser(g.pourcentage(valeur, signe=True, decimales=1)) in cout, valeur
    # La convention du compte principal est nommée, faute de quoi le lecteur ne
    # saurait pas laquelle des deux il lit.
    assert "équilibre permanent des régimes" in cout


@controle("compte_en_brut_et_recette_circulaire")
def _(m: Modele):
    """Le compte est en brut, et une part de sa recette sort de sa dépense.

    Deux choses que la page dit depuis le 20 septembre 2026, et que rien ne
    disait avant.

    LE BRUT. Les pensions du compte sont celles qui sont VERSÉES, avant CSG,
    CRDS et CASA. Au taux plein ces trois-là prennent 9,1 %, et la masse nette
    est donc plus basse que la masse brute d'environ un point de PIB. C'est une
    BORNE : les pensions modestes sont exonérées ou au taux réduit, et le dépôt
    ne sait pas combien le sont. Le contrôle exige que la page écrive les deux
    masses, et que le net soit sous le brut.

    LA RECETTE CIRCULAIRE. L'article L. 131-8 reverse 2,94 des 8,30 points de
    CSG d'une pension à la branche vieillesse : une part de ce que le compte
    encaisse est prélevée sur ce qu'il verse. Le contrôle exige que cette part
    soit strictement comprise entre zéro et le tiers de la CSG d'une pension,
    et que la page écrive le montant.
    """
    depenses = m.contexte.depenses()
    pensions = charger_prelevements(m.base.racine_donnees).pensions
    annee = min(depenses.pensions_droits["direct"].derniere_annee,
                depenses.derniere_annee)
    masse = sum(depenses.pensions_droit(c, annee) for c in ("direct", "derive"))
    pib = depenses.pib(annee)
    brute, nette = masse / pib, masse / pib * (1.0 - pensions.taux_total)
    assert 0.0 < nette < brute, (nette, brute)

    taux = pensions.csg_affectee_vieillesse
    assert 0.0 < taux < pensions.csg_taux_plein, taux
    # Un tiers, et pas davantage : la CSG d'une pension finance aussi la
    # maladie et la CADES, et une part qui approcherait le taux entier dirait
    # qu'on a confondu l'affectation avec le prélèvement.
    assert taux / pensions.csg_taux_plein < 0.40

    cout = TEMOINS_PAR_NOM["cout"]["texte"]
    for valeur in (brute, nette):
        assert normaliser(g.pourcentage(valeur, decimales=2)) in cout, valeur
    assert normaliser(g.nombre(taux * 100, 2)) in cout, taux


@controle("le_compte_est_un_flux_et_le_stock_existe")
def _(m: Modele):
    """Le site montre des flux ; le stock existe, il est publié, il est grand.

    Tout ce que la page Coût affiche est un flux : ce qui rentre et ce qui sort
    dans l'année. L'autre moitié d'un compte est ce que le système doit DÉJÀ,
    au titre des droits acquis, et le règlement (UE) n° 549/2013 la fait
    transmettre tous les trois ans. Elle manquait au dépôt jusqu'au
    20 septembre 2026 — ce qui est le comble pour un modèle en comptes
    notionnels, où ce stock est la somme des capitaux virtuels.

    Trois choses tenues ici. Que le stock soit d'un tout autre ORDRE que le
    flux : au moins vingt fois la dépense d'une année. Que les années soient
    celles qui ont été TRANSMISES, et non reconduites de bord en bord, faute de
    quoi la page daterait de 2024 un engagement de 2021. Et que la page écrive
    les trois valeurs, qui disent ensemble ce qu'aucune ne dit seule : un
    engagement actualisé bouge de soixante points de PIB sans qu'aucun droit
    n'ait changé.
    """
    comptes = m.contexte.comptes()
    annees = comptes.annees_engagements()
    assert len(annees) >= 3, annees
    # Une transmission tous les trois ans : des années espacées, et aucune
    # valeur reconduite entre elles.
    assert all(b - a == 3 for a, b in zip(annees, annees[1:])), annees
    assert annees[-1] < comptes.derniere_annee_observee

    for annee in annees:
        stock = comptes.engagements(annee)
        assert stock > 20 * comptes.depense(annee), (annee, stock)
        # La répartition porte tout, ou presque : la France déclare zéro au
        # titre des régimes par capitalisation.
        assert comptes.engagements(annee, "repartition") == pytest.approx(stock, abs=0.05)

    # L'écart entre transmissions, qui est ce que la page en dit.
    valeurs = [comptes.engagements(annee) for annee in annees]
    assert max(valeurs) - min(valeurs) > 0.40, valeurs

    cout = TEMOINS_PAR_NOM["cout"]["texte"]
    for annee, valeur in zip(annees, valeurs):
        assert str(annee) in cout, annee
        assert normaliser(g.pourcentage(valeur, decimales=0)) in cout, valeur


@controle("engagement_acquis_du_depot")
def _(m: Modele):
    """Le dépôt calcule son propre engagement acquis, et l'écart est un taux.

    C'EST LA GRANDEUR QU'UN COMPTE NOTIONNEL DOIT SAVOIR DIRE. Le dépôt la
    portait de l'extérieur — le tableau supplémentaire du SEC 2010 — sans
    produire la sienne. Il la produit depuis le 20 septembre 2026, sous la
    convention que le COR publie : « le taux d'actualisation est supposé égal
    chaque année à la croissance annuelle du PIB ». Actualiser au rythme du PIB
    revient à sommer des parts de PIB, et c'est ce qui rend le calcul possible
    sans décider d'un taux.

    Quatre choses tenues ici. Que l'engagement soit d'un autre ORDRE que le
    flux — au moins vingt fois la dépense d'une année. Que ses deux moitiés
    somment au total, retraités et actifs au prorata. Que l'extrapolation
    au-delà de la pyramide de l'INSEE ne porte qu'une petite part, faute de
    quoi le résultat dirait surtout la table de mortalité. Et qu'un écart de
    taux POSITIF et modeste ramène l'engagement du dépôt sur celui qu'Eurostat
    publie : c'est la démonstration que le niveau d'un engagement acquis est un
    taux, et non un droit.
    """
    engagement = m.contexte.bilan().engagements
    assert engagement is not None, "la table figée ne porte pas l'engagement"
    comptes = m.contexte.comptes()
    total = engagement.part_pib()
    assert total > 20 * comptes.depense(engagement.annee), total
    assert engagement.retraites + engagement.actifs == pytest.approx(total, rel=1e-9)
    assert 0.0 < engagement.hors_projection < 0.15 * total, engagement.hors_projection

    # La proposition promet moins, donc elle doit moins.
    assert 0.0 < engagement.part_pib("notionnel_liberal") < total

    ecart = engagement.ecart_pour(engagement.publie)
    assert ecart is not None, "la grille de sensibilité ne couvre pas le publié"
    assert 0.0 < ecart < 0.05, ecart
    # La sensibilité décroît : un taux plus élevé ne peut pas valoir plus.
    valeurs = [valeur for _, valeur in engagement.sensibilite()]
    assert valeurs == sorted(valeurs, reverse=True), valeurs

    cout = TEMOINS_PAR_NOM["cout"]["texte"]
    for valeur in (total, engagement.retraites, engagement.actifs,
                   engagement.part_pib("notionnel_liberal")):
        assert normaliser(g.pourcentage(valeur, decimales=0)) in cout, valeur


@controle("deficit_se_creuse")
def _(m: Modele):
    """Le solde du système actuel se creuse, et les pages écrivent ses nombres."""
    assert m.horizon.solde("actuel") < m.observe.solde("actuel") < 0
    risque = TEMOINS_PAR_NOM["risque"]["texte"]
    for annee in (2030, 2045, m.solde.derniere_annee):
        ligne = m.solde.annee(annee)
        # La page écrit ces soldes en POINTS de PIB, sans le signe pour cent :
        # « −0,2 point de PIB en 2030, −0,9 en 2045 et −2,4 en 2070 ».
        points = normaliser(g.nombre(abs(ligne.solde("actuel")) * 100, 1))
        assert points in risque, (annee, points)


@controle("deficit_observe_de_l_ordre_du_pas")
def _(m: Modele):
    assert 0.0005 < abs(m.observe.solde("actuel")) < 0.01


@controle("part_de_l_impot_doublee")
def _(m: Modele):
    comptes = m.contexte.comptes()
    debut, fin = comptes.premiere_annee_ventilee, comptes.derniere_annee_ventilee
    assert fin - debut >= 18
    rapport = comptes.part_groupe("impots", fin) / comptes.part_groupe("impots", debut)
    assert 1.7 <= rapport <= 2.5


@controle("depense_totale_et_repartition")
def _(m: Modele):
    depenses = m.contexte.depenses()
    derniere = depenses.derniere_annee
    assert depenses.depense(derniere) > depenses.repartition(derniere) > 0


@controle("transferts_ensemble_somme")
def _(m: Modele):
    comptes = m.contexte.comptes()
    annee = min(comptes.derniere_annee_transferts, m.solde.derniere_annee_observee)
    for organisme in ORGANISMES:
        postes = [p.code for p in POSTES_TRANSFERTS if p.organisme == organisme.code]
        assert postes
        assert _proche(comptes.transfert_organisme(organisme.code, annee),
                       sum(comptes.transfert(code, annee) for code in postes))


@controle("retrait_des_transferts")
def _(m: Modele):
    ligne = m.observe
    assert ligne.retrait > 0
    assert _proche(ligne.ressources_de("notionnel_retroactif"), ligne.ressources - ligne.retrait)
    assert m.sim.regime_fusionne.avantages_non_contributifs == ()


@controle("projection_s_ecarte_du_cor")
def _(m: Modele):
    avenir = m.cout.avenir
    assert abs(avenir.annee(avenir.derniere_annee).part_pib("actuel") - COR_2070) > 0.005


@controle("projection_du_cor")
def _(m: Modele):
    assert m.base.scenario_projection == "cor_reference"


@controle("dix_huit_pour_cent_de_l_assiette")
def _(m: Modele):
    ligne = m.horizon
    assert m.base.taux_cotisation_liberal == 0.18
    assert ligne.recette_par_assiette and ligne.taux_liberal == 0.18
    assert _proche(ligne.postes_ressources("notionnel_liberal")["cotisations"],
                   ligne.ressources * ligne.taux_liberal / ligne.taux_prelevement)


@controle("autre_convention_de_recette")
def _(m: Modele):
    """L'autre lecture est plus GÉNÉREUSE, et d'environ un point de PIB.

    Le contrôle le plus cher du fichier : il recalcule le coût agrégé sous
    l'autre convention. Il le vaut — la note affirmait le contraire, « plus
    sévère d'un point de PIB », jusqu'au 20 septembre 2026, et la convention
    retenue est justement celle qui ne reconduit ni les impôts affectés ni les
    subventions d'équilibre.
    """
    solde, autre = m.solde, m.cout_convention_rapport.solde
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    ecart = (autre.solde_moyen("notionnel_liberal", debut, fin)
             - solde.solde_moyen("notionnel_liberal", debut, fin))
    assert 0.005 <= ecart <= 0.015, ecart


@controle("postes_somment_aux_totaux")
def _(m: Modele):
    recettes = [code for code, _, rang in LIGNES_RECETTES if rang == "poste"]
    depenses = [code for code, _, rang in LIGNES_DEPENSES if rang == "poste"]
    for ligne in (m.observe, m.horizon):
        for scenario in ("actuel", "notionnel_liberal"):
            postes = ligne.postes_ressources(scenario)
            assert _proche(sum(postes[code] for code in recettes),
                           ligne.ressources_de(scenario), 1e-4)
            postes = ligne.postes_depenses(scenario)
            assert _proche(sum(postes[code] for code in depenses),
                           ligne.depense(scenario), 1e-4)


@controle("trois_postes_disparaissent")
def _(m: Modele):
    ligne = m.horizon
    disparus = ("contribution_equilibre_etat", "subventions_equilibre", "impots_et_taxes")
    proposition = ligne.postes_ressources("notionnel_liberal")
    actuel = ligne.postes_ressources("actuel")
    assert all(proposition[code] == 0.0 for code in disparus)
    assert all(actuel[code] > 0 for code in disparus)


@controle("recettes_trois_reactions")
def _(m: Modele):
    ligne = m.horizon
    assert m.observe.retrait > 0 and ligne.recette_par_assiette
    disparus = ("contribution_equilibre_etat", "subventions_equilibre", "impots_et_taxes")
    assert all(ligne.postes_ressources("notionnel_liberal")[code] == 0.0 for code in disparus)
    # « Trois postes : 27 % des ressources en 2024, 29 % en 2070 » — la prose
    # écrit ces deux parts en toutes lettres ; elles ne doivent pas dériver.
    for annee, attendu in ((2024, 0.27), (2070, 0.29)):
        parts = m.solde.annee(annee).parts
        part = sum(parts[code] for code in disparus)
        assert abs(part - attendu) <= 0.015, (annee, part)


@controle("pas_d_elasticite_d_assiette")
def _(m: Modele):
    assert not any("elasticit" in nom for nom in _champs(Parametres))


@controle("pas_de_parametre_de_couverture")
def _(m: Modele):
    assert not any("couverture" in nom for nom in _champs(Parametres))


@controle("stock_sur_les_prix")
def _(m: Modele):
    assert m.base.revalorisation_stock is RevalorisationStock.PRIX


@controle("effectifs_de_caisse_se_recoupent")
def _(m: Modele):
    effectifs = m.sim.effectifs
    annee = effectifs.serie("tous_regimes").derniere_annee
    tous = effectifs.effectif("tous_regimes", annee)
    somme = sum(effectifs.effectif(c, annee) for c in effectifs.caisses() if c != "tous_regimes")
    assert somme > tous > 0


@controle("reconstitution_mince_avant_1975")
def _(m: Modele):
    assert m.base.annee_debut_repartition == 1941
    lignes = m.cout.annees
    assert lignes[0].pensionnes * 2 < lignes[-1].pensionnes


@controle("pas_des_generations")
def _(m: Modele):
    """La grille du COÛT va de cinq en cinq — celle des cas types, de dix en dix."""
    generations = m.cout.generations
    assert {b - a for a, b in zip(generations, generations[1:])} == {5}
    assert len(generations) > len(GENERATIONS)


@controle("trois_leviers_du_meme_manque")
def _(m: Modele):
    """Les trois façons de combler le manque d'une année disent la même taille.

    La page en affiche trois — rogner les pensions, lever sur l'assiette,
    emprunter — et la phrase qu'elle met en gras promet qu'aucune n'est une
    prévision, c'est-à-dire qu'elles ne se distinguent que par l'unité. Si
    elles cessaient de se déduire l'une de l'autre, la page chiffrerait trois
    écarts différents sous un seul mot.
    """
    part = financer(m.solde, m.contexte.assiette(), "actuel", 2050,
                    tuple(1.0 for _ in range(20)))
    ligne = m.solde.annee(2050)
    assert part.manque_pib == pytest.approx(-ligne.solde("actuel"), rel=1e-12)
    assert part.manque_pib / ligne.depense("actuel") == pytest.approx(
        1 - part.coefficient_depart, rel=1e-12)
    assert part.points_assiette > part.manque_pib > 0.0
    assert part.hausse_cotisations > 0.0


@controle("bilan_fige_egale_le_modele")
def _(m: Modele):
    """La table que la page lit dit ce que le modèle calcule.

    Le coefficient d'équilibre coûte dix-huit secondes : la page des
    résultats lit une table figée plutôt que de le recalculer chez le lecteur.
    La note que ce contrôle tient dit d'où viennent ces chiffres — et ce
    serait une fausse déclaration si la table s'écartait du modèle.
    """
    bilan = charger_bilan(m.base.racine_donnees)
    assert bilan.premiere_annee == m.solde.premiere_annee
    assert bilan.derniere_annee == m.solde.derniere_annee
    for annee in (bilan.premiere_annee, 2026, 2050, bilan.derniere_annee):
        for scenario in ("actuel", "notionnel_retroactif",
                         "notionnel_retroactif_employeur", "notionnel_liberal"):
            assert bilan.annee(annee).coefficient(scenario) == pytest.approx(
                m.solde.annee(annee).coefficient(scenario), rel=1e-9)


@controle("reversion_servie_par_le_seul_systeme_actuel")
def _(m: Modele):
    assert all(not ligne.reversion_servie for ligne in m.solde.annees)
    ligne = m.horizon
    assert ligne.postes_depenses("actuel")["droits_derives"] > 0
    assert ligne.postes_depenses("notionnel_liberal")["droits_derives"] == 0.0


# .. la cascade : le compte tombe-t-il juste ? ...............................
#
# C'est la propriété qui fait toute la valeur de cette figure : les marches
# somment EXACTEMENT à l'écart des deux totaux, sinon la dernière barre ne
# retombe pas où elle devrait. Le dessin le montre à l'œil, et un écart d'un
# millième s'y verrait mal — d'où ces contrôles, qui refont la somme.


def _somme_cascade(marches) -> float:
    """Ce que les marches déplacent, totaux exclus."""
    return sum(marche.valeur for marche in marches if not marche.total)


def _cascade_de(m: Modele, ligne, base: float, part_reprise: float = 0.0):
    """Les marches d'une année, nommées sous les réglages du modèle."""
    return _marches_cascade(
        base, ligne.part_derives, ligne.rapports,
        _libelles_cascade(m.contexte, ligne.part_derives, part_reprise),
        part_reprise)


@controle("cascade_somme_exactement")
def _(m: Modele):
    for ligne, base in ((m.observe, m.observe.depense_meur("actuel")),
                        (m.horizon, m.horizon.depense_meur("actuel"))):
        marches = _cascade_de(m, ligne, base)
        arrivee = (ligne.depense_meur("notionnel_liberal")
                   + ligne.depense_meur(COMPOSANTE_GARANTIE)) / 1000
        assert _proche(base / 1000 + _somme_cascade(marches), arrivee)
        # L'ordre ne change pas le total, et c'est ce que la page affirme :
        # les marches sont additives, non composées.
        assert _proche(_somme_cascade(marches),
                       _somme_cascade(list(reversed(marches))))

    # Et la même chose sur la trajectoire, où toutes les mesures mordent : la
    # garantie y vient NETTE des reprises, qui sont une marche de plus.
    horizon = m.cout.avenir.annee(m.cout.avenir.derniere_annee)
    garantie = horizon.cout_constants(COMPOSANTE_GARANTIE)
    part_reprise = horizon.reprises_constants() / garantie
    assert 0.0 < part_reprise < 1.0
    marches = _cascade_de(m, horizon, horizon.cout_constants("actuel"), part_reprise)
    arrivee = (horizon.cout_constants("notionnel_liberal")
               + horizon.garantie_nette_constants()) / 1000
    depart = horizon.cout_constants("actuel") / 1000
    assert _proche(depart + _somme_cascade(marches), arrivee)


@controle("cascade_cotisation_unique_sans_effet_avant_la_bascule")
def _(m: Modele):
    bascule = m.base.annee_bascule
    assert m.solde.derniere_annee_observee < bascule
    # Ce que la marche vaut à l'année observée : rien, au dixième de milliard
    # que la page écrit près. Aucun retraité de cette année-là n'a acquis un
    # seul droit sous le taux unique.
    # Le libellé se DÉDUIT du réglage, comme l'étiquette de la figure : l'écrire
    # ici en toutes lettres referait l'erreur que la figure ne fait plus.
    nom = MARCHES_SYSTEMES["notionnel_liberal"][0].format(
        **_libelles_cascade(m.contexte, m.observe.part_derives, 0.0))
    marches = _cascade_de(m, m.observe, m.observe.depense_meur("actuel"))
    taux_unique = next(marche for marche in marches if marche.libelle == nom)
    assert g.signe_cascade(taux_unique.valeur, 1) == g.nombre(0.0, 1)
    # Et ce qu'elle vaut à l'horizon, quand toutes les générations sont passées
    # sous elle : la plus lourde des mesures après le recalcul lui-même.
    horizon = m.cout.avenir.annee(m.cout.avenir.derniere_annee)
    loin = _cascade_de(m, horizon, horizon.cout_constants("actuel"))
    assert next(marche for marche in loin
                if marche.libelle == nom).valeur < -1.0


@controle("cascade_ne_porte_que_la_depense")
def _(m: Modele):
    """Aucune marche ne vient des RESSOURCES, et le total est bien la dépense."""
    marches = _cascade_de(m, m.observe, m.observe.depense_meur("actuel"))
    depart = m.observe.depense_meur("actuel") / 1000
    assert not _proche(depart, m.observe.ressources_meur() / 1000)
    # La somme rejoint la DÉPENSE de la proposition, jamais son solde : si la
    # cascade portait un côté de recette, elle n'y retomberait pas.
    arrivee = (m.observe.depense_meur("notionnel_liberal")
               + m.observe.depense_meur(COMPOSANTE_GARANTIE)) / 1000
    assert _proche(depart + _somme_cascade(marches), arrivee)
    assert not _proche(arrivee, m.observe.ressources_de("notionnel_liberal")
                       * m.observe.pib / 1000)


@controle("cout_estime")
def _(m: Modele):
    assert m.cout.fiabilite is Fiabilite.ESTIMEE


@controle("fiabilite_des_trois_sources")
def _(m: Modele):
    depenses = m.contexte.depenses()
    assert depenses.fiabilite(depenses.derniere_annee) is Fiabilite.CERTIFIEE
    assert m.contexte.comptes().fiabilite(m.solde.derniere_annee_observee) is Fiabilite.HAUTE
    assert m.cout.fiabilite is Fiabilite.ESTIMEE


@controle("ponderation_par_les_effectifs")
def _(m: Modele):
    cout = m.cout
    assert cout.ponderation == "effectifs"
    assert _proche(sum(cout.poids.values()), 1.0)
    assert _proche(sum(cout.poids_cotisants.values()), 1.0)
    assert cout.poids != cout.poids_cotisants


@controle("capitalisation_hors_du_bilan")
def _(m: Modele):
    ligne = m.horizon
    for scenario in ("actuel", "notionnel_liberal"):
        cles = set(ligne.postes_ressources(scenario)) | set(ligne.postes_depenses(scenario))
        assert not any("capitalis" in cle for cle in cles)
    assert ligne.taux_liberal == m.base.taux_cotisation_liberal


# .. la dette ...................................................................


@controle("impots_abandonnes_partages_en_deux")
def _(m: Modele):
    """La recette abandonnée va moitié aux salaires, moitié à la dette."""
    from retraite_notionnelle.restitution import _restitution

    assert m.base.part_rendue_aux_salaires == 0.5
    restitution = _restitution(m.base.racine_donnees, m.base.part_rendue_aux_salaires)
    ligne = restitution.annuelle(restitution.derniere_annee)
    assert ligne.poste_abandonne > 0
    assert _proche(ligne.rendu, ligne.poste_abandonne * m.base.part_rendue_aux_salaires)
    assert _proche(ligne.rendu + ligne.eteint_de_dette, ligne.poste_abandonne)


@controle("deux_impots_sur_la_remuneration_supprimes")
def _(m: Modele):
    """Les deux impôts assis sur une rémunération sont supprimés, pas rendus par un détour."""
    from retraite_notionnelle.restitution import POSTES_REMUNERATION, _restitution

    codes = {code for code, _ in POSTES_REMUNERATION}
    assert codes == {"taxe_sur_les_salaires", "forfait_social"}
    restitution = _restitution(m.base.racine_donnees, m.base.part_rendue_aux_salaires)
    ligne = restitution.annuelle(restitution.derniere_annee)
    assert 0 < ligne.supprime_sur_la_remuneration < ligne.rendu


@controle("points_de_csg_rendus")
def _(m: Modele):
    """Le solde de la moitié rendue passe par la CSG d'activité, en points d'assiette."""
    from retraite_notionnelle.restitution import _restitution, points_csg_rendus

    restitution = _restitution(m.base.racine_donnees, m.base.part_rendue_aux_salaires)
    annee = restitution.derniere_annee
    points = points_csg_rendus(m.base.racine_donnees, annee,
                               m.base.part_rendue_aux_salaires)
    assert 0.005 < points < 0.02
    assert _proche(points, restitution.annuelle(annee).points_csg)
    attendu = normaliser(f"baisse de {g.nombre(points * 100, 2)} point")
    assert attendu in TEMOINS_PAR_NOM["programme"]["texte"], attendu


@controle("restitution_hors_du_solde")
def _(m: Modele):
    """Le partage ne touche ni les ressources ni les dépenses du bilan."""
    ligne = m.horizon
    for scenario in ("actuel", "notionnel_liberal"):
        cles = set(ligne.postes_ressources(scenario)) | set(ligne.postes_depenses(scenario))
        assert not any("restitution" in cle or "csg" in cle for cle in cles)
    assert ligne.postes_ressources("notionnel_liberal")["impots_et_taxes"] == 0.0


@controle("dette_cumule_les_soldes")
def _(m: Modele):
    dette = m.cout.dette
    assert _proche(dette.cumul_soldes("actuel"),
                   -sum(ligne.solde("actuel") for ligne in dette.annees))


@controle("dette_part_de_zero")
def _(m: Modele):
    premiere = m.cout.dette.annees[0]
    for scenario in SCENARIOS_MONTRES:
        assert _proche(premiere.stock(scenario), -premiere.solde(scenario))


@controle("dette_publique_observee")
def _(m: Modele):
    dette = m.cout.dette
    assert dette.dette_publique_observee
    assert _proche(dette.dette_publique_depart,
                   dette.dette_publique_observee[dette.annee_dette_publique])
    assert dette.dette_publique_depart > 0.5


@controle("dette_publique_tenue_a_plat")
def _(m: Modele):
    dette = m.cout.dette
    for scenario in ("actuel", "notionnel_liberal"):
        for annee in range(dette.annee_depart, dette.derniere_annee + 1):
            assert _proche(dette.dette_publique(scenario, annee) - dette.stock(scenario, annee),
                           dette.dette_publique_depart)


@controle("taux_de_la_dette_lu_sur_la_courbe")
def _(m: Modele):
    dette = m.cout.dette
    assert dette.date_courbe == m.sim.courbe_taux.date
    assert all(-0.05 < ligne.taux < 0.15 for ligne in dette.annees)


# .. les avantages non contributifs ..........................................


def _dispositifs(m: Modele):
    return [a for a in m.inventaire.avantages if a.famille != "ecarts_structurels"]


@controle("un_seul_dispositif_a_l_origine")
def _(m: Modele):
    dispositifs = _dispositifs(m)
    premiere = min(a.creation for a in dispositifs)
    assert sum(1 for a in dispositifs if a.creation == premiere) == 1


@controle("part_des_avantages_chiffres_un_cinquieme")
def _(m: Modele):
    derniere = m.avantages.derniere
    assert 0.15 <= derniere.gratuit / derniere.observee <= 0.30


@controle("modele_et_postes_lus_distincts")
def _(m: Modele):
    derniere = m.avantages.derniere
    assert derniere.gratuit_modele < derniere.gratuit
    assert set(m.avantages.lignes_modele) <= set(m.avantages.lignes)


@controle("plus_grosse_ligne_lue")
def _(m: Modele):
    lignes = m.avantages.derniere.lignes
    assert max(lignes, key=lignes.get) in LIGNES_LUES


@controle("poste_publie_remplace_le_calcul")
def _(m: Modele):
    derniere = m.avantages.derniere
    communes = set(LIGNES_LUES) & set(m.avantages.lignes_modele)
    assert communes
    for ligne in communes:
        assert not _proche(derniere.lignes[ligne], derniere.modele[ligne], 1e-3)


@controle("fenetre_des_postes_publies")
def _(m: Modele):
    lues = frozenset(LIGNES_LUES) & frozenset(m.avantages.lignes)
    publiees = [a.annee for a in m.avantages.annees if lues <= frozenset(a.lignes)]
    assert publiees
    assert len(publiees) <= 10
    assert publiees[0] > m.avantages.annees[0].annee + 40


@controle("minimum_vieillesse_s_est_eteint")
def _(m: Modele):
    parts = [(a.annee, a.modele.get("minimum_vieillesse", 0.0) / a.observee)
             for a in m.avantages.annees if a.observee]
    assert parts[0][1] > 0.2
    assert parts[-1][1] < 0.01


@controle("des_dispositifs_restent_sans_chiffre")
def _(m: Modele):
    lignes = m.avantages.derniere.lignes
    assert any(not lignes.get(a.ligne_cascade or a.code) for a in m.inventaire.avantages)


@controle("annuites_anticipees_rapportees_au_montant")
def _(m: Modele):
    """Le rapport est compté sur le modèle, et la page écrit ce compte."""
    derniere = m.avantages.derniere
    montant = sum(derniere.lignes.get(ligne, 0.0) for ligne in m.avantages.lignes_modele
                  if m.inventaire.famille_de_ligne(ligne) == "age_et_bonifications")
    assert montant > 0 and derniere.anticipee > montant
    attendu = f"soit {g.nombre(derniere.anticipee / montant, 0)} fois"
    assert attendu in TEMOINS_PAR_NOM["avantages"]["texte"]


@controle("decote_plafonnee_a_vingt_trimestres")
def _(m: Modele):
    assert _coefficient_anticipation(20, 20) is not None
    assert _coefficient_anticipation(21, 20) is None


@controle("ecarts_structurels_hors_comptage")
def _(m: Modele):
    inventaire = m.inventaire
    assert len(inventaire.par_famille("ecarts_structurels")) == 3
    assert inventaire.familles[-1].code == "ecarts_structurels"


@controle("etalon_applique_les_avantages")
def _(m: Modele):
    etats = {a.code: a.etat_modele for a in m.inventaire.avantages}
    for code in ("avpf", "majoration_duree_assurance", "minimum_contributif",
                 "minimum_garanti", "surcote_parentale", "majoration_enfants",
                 "minimum_vieillesse"):
        assert etats[code] == "chiffre", code


# .. la méthode : l'indexation ..............................................


@controle("indexation_domine_l_ecart")
def _(m: Modele):
    cumuls = m.cumuls
    assert max(cumuls.values()) / min(cumuls.values()) > 10
    pratiquee = m.simuler(indexation="revalorisation_portee_au_compte")
    prix = m.simuler(indexation="prix")
    assert abs(pratiquee.variation("notionnel_retroactif")
               - prix.variation("notionnel_retroactif")) < 0.10


@controle("triple_lock_est_un_minimum")
def _(m: Modele):
    indexation = Indexation(m.sim.macro, replace(
        m.base, mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE, lissage_indexation=1))
    for annee in (1975, 1995, 2015):
        taux = indexation.taux(annee)
        assert _proche(taux.taux, min(taux.inflation, taux.salaire_moyen, taux.productivite))


@controle("revalorisation_pratiquee_pres_de_cinq_fois_les_prix")
def _(m: Modele):
    rapport = m.cumuls["Revalorisation réellement pratiquée"] / m.cumuls["Indexation sur les prix"]
    assert 4 < rapport < 6


@controle("masse_salariale_onze_fois_les_prix")
def _(m: Modele):
    rapport = (m.cumuls["Masse salariale (règle d'équilibre)"]
               / m.cumuls["Indexation sur les prix"])
    assert 9 < rapport < 13


@controle("lissage_absorbe_la_loterie")
def _(m: Modele):
    coefficients = {}
    for lissage in (1, 5):
        indexation = Indexation(m.sim.macro, replace(
            m.base, mode_indexation=ModeIndexation.PIB_NOMINAL, lissage_indexation=lissage))
        for arrivee in (2019, 2020):
            coefficients[lissage, arrivee] = indexation.coefficient(1980, arrivee)
    assert coefficients[1, 2020] < coefficients[1, 2019]
    assert coefficients[5, 2020] >= coefficients[5, 2019]


@controle("montants_au_net_ou_au_brut")
def _(m: Modele):
    """Le pied affirme que le lecteur choisit son unité : les deux existent.

    Il affirmait « Les montants sont bruts » alors que le défaut est le NET
    depuis la bascule, et rien ne tenait la phrase : elle était fausse en bas
    de chaque page, y compris celles qu'on projette. Ce contrôle exige les
    deux modes, le net par défaut, et une conversion qui fasse bien descendre
    un brut vers un net.
    """
    assert [code for code, _ in MODES_MONTANT] == ["net", "brut"]
    assert Saisie().montants == "net"
    assert Saisie(montants="net").en_net
    assert not Saisie(montants="brut").en_net
    pensions = charger_prelevements(m.contexte.base.racine_donnees).pensions
    assert 0.0 < pensions.taux_total < 0.2
    assert pensions.net(1_000.0) < 1_000.0
    assert _proche(pensions.brut(pensions.net(1_000.0)), 1_000.0)


@controle("series_macro_certifiees")
def _(m: Modele):
    assert m.sim.macro.fiabilite_sur(1950, 2025) is Fiabilite.CERTIFIEE


# -- les tests ----------------------------------------------------------------


def _etats_des_actions() -> dict[int, str]:
    """Le numéro et l'état de chaque action de la feuille de route."""
    motif = re.compile(r"^### (\d+)\. .* — `([^`]+)`\s*$", re.M)
    return {int(numero): etat
            for numero, etat in motif.findall(FEUILLE_DE_ROUTE.read_text(encoding="utf-8"))}


def test_le_catalogue_est_bien_forme():
    assert AFFIRMATIONS, "catalogue vide"
    assert len(PAR_ID) == len(AFFIRMATIONS), "identifiants en double"
    actions = _etats_des_actions()
    chemins = set(TITRES) | {"*"}
    for entree in AFFIRMATIONS:
        ident = entree["id"]
        assert entree["etat"] in ETATS, ident
        assert set(pages_de(entree)) <= chemins, (ident, entree["page"])
        assert len(entree["extrait"]) >= LONGUEUR_MINIMALE_EXTRAIT, ident
        assert entree.get("porte"), ident
        if entree["etat"] == "sans_portee":
            assert "controle" not in entree and "action" not in entree, ident
            continue
        if entree["etat"] == "hors_modele":
            assert "controle" not in entree and "action" not in entree, ident
            assert entree.get("source"), ident
            continue
        assert entree["controle"] in CONTROLES, (ident, entree["controle"])
        if entree["etat"] == "contredite":
            action = entree["action"]
            assert isinstance(action, int) and action in actions, (ident, action)
            assert actions[action] != "fait", (
                f"{ident} : l'action {action} est faite, la phrase reste contredite"
            )


@pytest.mark.parametrize("ident", sorted(PAR_ID))
def test_l_extrait_est_encore_dans_la_page(ident):
    """Une phrase réécrite sans repasser par le catalogue : échec."""
    entree = PAR_ID[ident]
    extrait = normaliser(entree["extrait"])
    for chemin in pages_de(entree):
        textes = textes_de(chemin)
        assert textes, f"{ident} : aucun témoin sous {chemin}"
        assert any(extrait in texte for texte in textes), (
            f"{ident} : « {entree['extrait']} » n'est plus dans {chemin}"
        )


@pytest.mark.parametrize(
    "ident",
    sorted(i for i, e in PAR_ID.items() if e["etat"] in ("verifiee", "contredite")))
def test_le_controle_passe(modele, ident):
    """``verifiee`` : le modèle fait ce que la phrase dit. ``contredite`` : il ne le fait toujours pas."""
    entree = PAR_ID[ident]
    CONTROLES[entree["controle"]](modele)


def test_rien_n_echappe_au_catalogue():
    """Toute phrase forte des pages est au catalogue, ou déclarée sans portée."""
    extraits = [normaliser(e["extrait"]) for e in AFFIRMATIONS]
    echappees: list[str] = []
    vues: set[str] = set()
    for nom, temoin in TEMOINS_PAR_NOM.items():
        for brut in _FORT.findall(temoin["corps"]):
            texte = normaliser(brut)
            if texte in vues or not phrase_forte(texte):
                continue
            vues.add(texte)
            if not any(extrait in texte or texte in extrait for extrait in extraits):
                echappees.append(f"[{temoin['chemin']}] {texte}")
    assert not echappees, (
        "phrases fortes hors catalogue — les ajouter à "
        "data/reference/site/affirmations.yaml, avec un contrôle ou en sans_portee :\n"
        + "\n".join(sorted(echappees))
    )


@pytest.mark.parametrize(
    "ident", sorted(i for i, e in PAR_ID.items() if e["etat"] == "hors_modele"))
def test_l_affirmation_hors_modele_cite_sa_source(ident):
    """Le modèle ne peut pas la trancher : la page doit au moins dire d'où elle vient."""
    entree = PAR_ID[ident]
    source = normaliser(entree["source"])
    for chemin in pages_de(entree):
        assert any(source in texte for texte in textes_de(chemin)), (
            f"{ident} : « {entree['source']} » n'est pas cité dans {chemin}"
        )


def test_aucun_controle_orphelin():
    """Un contrôle que plus aucune entrée ne nomme est du code mort."""
    nommes = {e["controle"] for e in AFFIRMATIONS if "controle" in e}
    assert set(CONTROLES) == nommes, sorted(set(CONTROLES) ^ nommes)
