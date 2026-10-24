"""Ce que les trois pages qui agrègent lisent du modèle, fabriqué sous la référence.

POURQUOI CE FICHIER EXISTE. Coût, Carrières types et Droits non cotisés
croisent treize carrières types avec sept générations, et chiffrent ce que
chaque système coûterait, année par année jusqu'en 2070. Elles se calculaient
chez le lecteur, par le portage JavaScript du coût, sous les réglages de
l'adresse : de trois à huit secondes à la première visite. Le propriétaire a
retiré leurs réglages le 10 octobre 2026 (action 150) : elles ne montrent plus
que la référence depuis le lendemain. Ce qu'elles lisent du modèle est donc calculé une fois, par
``scripts/construire_donnees.py``, écrit dans ``data/derive/agregats.json``,
embarqué dans le paquet que le navigateur charge, et lu ici et dans
``moteur/js/agregats.js`` par les mêmes accesseurs.

CE QUI EST FIGÉ, ET CE QUI NE L'EST PAS. Tout ce qu'une règle du modèle
décide : la grille des cas types, l'âge auquel chacun part, ce que coûtent les
avantages non contributifs, les deux départs qui disent ce que le classement
d'un emploi ajoute. Ce qui n'est
qu'une donnée lue — les comptes du COR, les dépenses publiées, la
distribution des pensions — reste dans le paquet, où les pages la lisent
comme avant. Les lecteurs ne calculent rien qu'une règle décide : ils rendent
ce que la table porte. Une lecture qu'elle ne porte pas lève une erreur, plutôt
que de rendre un zéro : une page qui la demanderait se tromperait sans bruit.

LE PYTHON GARDE TOUS SES RÉGLAGES. La table ne vaut que pour la référence,
celle de ``Parametres()`` ; le modèle se calcule toujours sous toute autre
règle, et c'est le simulateur, sur une carrière, qui les montre au lecteur.

Chaque partie a ses deux moitiés côte à côte : ``figer_*`` écrit la table
depuis les objets du modèle, en n'y lisant que leurs accesseurs, et le lecteur
la rend sous ces mêmes accesseurs. ``tests/test_agregats.py`` vérifie que les
deux disent la même chose que le modèle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..somme import somme_ordonnee


def _lire(table: dict, cle, quoi: str):
    """``table[cle]``, ou une erreur qui dit ce que la table ne porte pas."""
    try:
        return table[cle]
    except KeyError:
        raise KeyError(f"{quoi} absent de la table figée : {cle!r}") from None


def _cle_grille(code: str, generation: int) -> str:
    """La clé d'une case de la grille dans la table, celle du portage."""
    return f"{code}|{generation}"


# -- les carrières types -------------------------------------------------------


@dataclass(frozen=True)
class CarriereFigee:
    """D'une carrière simulée, ce que les pages en lisent : l'année du départ."""

    annee_liquidation: int


@dataclass(frozen=True)
class ComparaisonFigee:
    """Une case de la grille : ce qu'en lisent les pages, sous les accesseurs
    de ``simulateur.Comparaison``."""

    carriere: CarriereFigee
    _carrieres: dict[str, CarriereFigee] = field(default_factory=dict)
    _variations: dict[str, float] = field(default_factory=dict)

    def carriere_de(self, scenario: str) -> CarriereFigee:
        return _lire(self._carrieres, scenario, "carrière du scénario")

    def variation_totale(self, scenario: str) -> float:
        return _lire(self._variations, scenario, "écart du scénario")


@dataclass(frozen=True)
class CasFige:
    """Un cas type, tel que les pages le nomment, les caisses dont il porte les
    retraités, et l'âge où chaque génération le fait partir."""

    code: str
    libelle: str
    commentaire: str
    caisses: tuple[str, ...] = ()
    _ages: dict[int, float] = field(default_factory=dict)

    def age_liquidation(self, generation: int) -> float:
        return _lire(self._ages, generation, "âge de départ de la génération")


@dataclass(frozen=True)
class CasTypesFiges:
    """La grille cas type × génération, sous les accesseurs de
    ``castypes.ResultatCasTypes``, et les cas qui la composent."""

    generations: tuple[int, ...]
    cas: tuple[CasFige, ...]
    resultats: dict[tuple[str, int], ComparaisonFigee]
    echecs: dict[tuple[str, int], str]

    def cas_type(self, code: str) -> CasFige:
        for cas in self.cas:
            if cas.code == code:
                return cas
        raise KeyError(f"cas type absent de la table figée : {code!r}")


def figer_cas_types(resultats, echecs, simulateur, cas_types, generations,
                    scenarios) -> dict:
    """La grille de ``castypes.calculer_cas_types``, et l'âge de départ de
    chaque case, pour les ``scenarios`` que les pages comparent. Le portage la
    calcule (``pont.carrieres``, action 161, étape 5) : ``resultats`` est ce
    qu'il rend de chaque case, sous ``(code, génération)``, et ``echecs`` le
    motif de celles que le droit ou le portage écartent."""
    return {
        "generations": list(generations),
        "cas": [
            {
                "code": cas.code,
                "libelle": cas.libelle,
                "commentaire": cas.commentaire,
                "caisses": list(cas.caisses),
                "ages": [cas.age_liquidation_pour(simulateur, generation)
                         for generation in generations],
            }
            for cas in cas_types
        ],
        "resultats": {
            _cle_grille(code, generation): {
                "annee_liquidation": lu["annee_liquidation"],
                "annees_liquidation": {scenario: lu["annees_liquidation"][scenario]
                                       for scenario in scenarios},
                "variations": {scenario: lu["variations"][scenario]
                               for scenario in scenarios},
            }
            for (code, generation), lu in resultats.items()
        },
        "echecs": {_cle_grille(code, generation): motif
                   for (code, generation), motif in echecs.items()},
    }


def _cas_types(brut: dict) -> CasTypesFiges:
    generations = tuple(int(generation) for generation in brut["generations"])

    def case(cle: str) -> tuple[str, int]:
        code, generation = cle.split("|")
        return code, int(generation)

    return CasTypesFiges(
        generations=generations,
        cas=tuple(
            CasFige(
                code=cas["code"], libelle=cas["libelle"],
                commentaire=cas["commentaire"], caisses=tuple(cas["caisses"]),
                _ages=dict(zip(generations, (float(age) for age in cas["ages"]))),
            )
            for cas in brut["cas"]
        ),
        resultats={
            case(cle): ComparaisonFigee(
                carriere=CarriereFigee(int(valeur["annee_liquidation"])),
                _carrieres={scenario: CarriereFigee(int(annee)) for scenario, annee
                            in valeur["annees_liquidation"].items()},
                _variations={scenario: float(ecart)
                             for scenario, ecart in valeur["variations"].items()},
            )
            for cle, valeur in brut["resultats"].items()
        },
        echecs={case(cle): motif for cle, motif in brut["echecs"].items()},
    )


# -- les avantages non contributifs --------------------------------------------


@dataclass(frozen=True)
class AnneeAvantagesFigee:
    """Une année de la décomposition, sous les accesseurs de
    ``avantages.AnneeAvantages``. Les trois sommes sont celles du modèle, dans
    son ordre d'addition : la table les porte plutôt que de les refaire."""

    annee: int
    observee: float
    lignes: dict[str, float]
    modele: dict[str, float]
    anticipees: dict[str, float]
    gratuit: float
    gratuit_modele: float
    anticipee: float


@dataclass(frozen=True)
class AvantagesFiges:
    """Ce que les avantages non contributifs coûtent, année par année, sous les
    accesseurs de ``avantages.CoutAvantages`` ; et la nomenclature sous laquelle
    la page Droits non cotisés les lit : les lignes que les comptes publient
    (``LIGNES_LUES``), les avantages mesurés par retrait (``NEUTRALISATIONS``),
    les motifs d'un départ anticipé et leur libellé."""

    annees: tuple[AnneeAvantagesFigee, ...]
    lignes: tuple[str, ...]
    lignes_modele: tuple[str, ...]
    refus: dict[str, str]
    ponderation: str
    lignes_lues: tuple[str, ...] = ()
    neutralisations: tuple[str, ...] = ()
    libelles_motifs: dict[str, str] = field(default_factory=dict)

    @property
    def motifs(self) -> tuple[str, ...]:
        return tuple(self.libelles_motifs)

    @property
    def derniere(self) -> AnneeAvantagesFigee | None:
        return self.annees[-1] if self.annees else None


def figer_avantages(cout, lignes_lues, neutralisations, libelles_motifs) -> dict:
    """Le coût des avantages de ``avantages.calculer_avantages``, et la
    nomenclature du modèle qui le décompose : ``LIGNES_LUES``, le code de
    chaque ``NEUTRALISATIONS``, ``LIBELLES_MOTIFS`` dans l'ordre des
    ``MOTIFS``."""
    return {
        "lignes_lues": list(lignes_lues),
        "neutralisations": [neutralisation.code for neutralisation in neutralisations],
        "libelles_motifs": [[motif, libelle] for motif, libelle in libelles_motifs.items()],
        "annees": [
            {
                "annee": annee.annee, "observee": annee.observee,
                "lignes": dict(annee.lignes), "modele": dict(annee.modele),
                "anticipees": dict(annee.anticipees),
                "gratuit": annee.gratuit, "gratuit_modele": annee.gratuit_modele,
                "anticipee": annee.anticipee,
            }
            for annee in cout.annees
        ],
        "lignes": list(cout.lignes),
        "lignes_modele": list(cout.lignes_modele),
        "refus": dict(cout.refus),
        "ponderation": cout.ponderation,
    }


def _avantages(brut: dict) -> AvantagesFiges:
    return AvantagesFiges(
        annees=tuple(
            AnneeAvantagesFigee(
                annee=int(annee["annee"]), observee=float(annee["observee"]),
                lignes={cle: float(valeur) for cle, valeur in annee["lignes"].items()},
                modele={cle: float(valeur) for cle, valeur in annee["modele"].items()},
                anticipees={cle: float(valeur)
                            for cle, valeur in annee["anticipees"].items()},
                gratuit=float(annee["gratuit"]),
                gratuit_modele=float(annee["gratuit_modele"]),
                anticipee=float(annee["anticipee"]),
            )
            for annee in brut["annees"]
        ),
        lignes=tuple(brut["lignes"]),
        lignes_modele=tuple(brut["lignes_modele"]),
        refus=dict(brut["refus"]),
        ponderation=brut["ponderation"],
        lignes_lues=tuple(brut["lignes_lues"]),
        neutralisations=tuple(brut["neutralisations"]),
        libelles_motifs=dict((motif, libelle) for motif, libelle in brut["libelles_motifs"]),
    )


# -- le classement de l'emploi --------------------------------------------------


@dataclass(frozen=True)
class DepartFige:
    """D'une carrière simulée, ce que la page Droits non cotisés lit du système
    actuel : sa pension, et la durée qu'il requiert."""

    pension_annuelle: float
    trimestres_requis: int


@dataclass(frozen=True)
class ClassementFige:
    """Ce que le classement d'un emploi en catégorie active change à un départ :
    le cas type ``cas`` parti à ``age``, contre la même carrière sous
    ``declassement``, partie le même jour, pour chacune des ``generations``.
    La page Droits non cotisés en tire l'écart de pension et de durée requise."""

    cas: str
    age: float
    declassement: str
    _departs: dict[int, tuple[DepartFige, DepartFige]] = field(default_factory=dict)

    @property
    def generations(self) -> tuple[int, ...]:
        return tuple(self._departs)

    def departs(self, generation: int) -> tuple[DepartFige, DepartFige]:
        """L'agent actif, puis l'agent déclassé."""
        return _lire(self._departs, generation, "départ de la génération")


def figer_departs(actif, declasse) -> list[dict]:
    """Les deux départs comparés : de chacun, la pension du système actuel et
    la durée qu'il requiert, que le portage calcule (``pont.carrieres``)."""
    return [{"pension_annuelle": lu["pension_annuelle"],
             "trimestres_requis": lu["trimestres_requis"]}
            for lu in (actif, declasse)]


def _classement(brut: dict) -> ClassementFige:
    return ClassementFige(
        cas=brut["cas"], age=float(brut["age"]), declassement=brut["declassement"],
        _departs={
            int(generation): tuple(
                DepartFige(pension_annuelle=float(depart["pension_annuelle"]),
                           trimestres_requis=int(depart["trimestres_requis"]))
                for depart in departs)
            for generation, departs in brut["departs"].items()
        },
    )


# -- le coût agrégé ------------------------------------------------------------
#
# LA PAGE COÛT LIT LE COÛT ENTIER : le passé de chaque système (``CoutAnnuel``),
# son avenir (``AvenirAnnuel``), le bilan de chaque année (``SoldeAnnuel``), la
# dette que les soldes accumulent (``DetteAnnuelle``). Chaque ligne figée porte
# les champs de la ligne du modèle que la page lit, tels quels, et ce que ses
# accesseurs rendent pour les systèmes qu'elle leur demande : les quatre que le
# site compare, la garantie vieillesse là où le modèle la compte à part, les
# deux du bilan poste par poste (``SYSTEMES_BILAN``) pour ce qui n'y sert
# qu'à lui. Le reste n'y est pas, et un accesseur qu'on interrogerait sur un
# autre système lève une erreur. Un accesseur qui prend un nombre quelconque —
# le solde moyen d'une fenêtre, le pilier à un niveau de versements, le stock
# d'une année — se rend depuis ce que la ligne porte, par la même opération que
# le modèle : une moyenne, un produit, une lecture.

#: Les champs d'une ligne de ``cout.SoldeAnnuel``, recopiés tels quels. Les
#: parts et les versements par système n'y sont pas : aucune page ne les lit.
CHAMPS_SOLDE_ANNUEL = (
    "annee", "projete", "ressources", "depenses", "rapports", "pib", "retrait",
    "rapports_recettes", "part_contributive", "part_impots", "retrait_par_impot",
    "part_subventions", "taux_prelevement", "taux_liberal", "facteur_assiette",
    "annee_bascule", "convention_recette", "part_derives", "reversion_servie",
    "reforme_en_vigueur", "tva_liberal", "garantie_liberal", "majorations_stock",
    "taux_effectif", "annee_taux_effectif",
)
#: Ses accesseurs qui prennent un système, la clé où la table les porte, et
#: s'ils ne servent qu'au bilan poste par poste.
PAR_SYSTEME_SOLDE_ANNUEL = (
    ("coefficient", "coefficients", False), ("depense", "depenses_par_systeme", False),
    ("depense_nette", "depenses_nettes_par_systeme", False),
    ("solde", "soldes", False), ("ressources_de", "ressources_par_systeme", False),
    ("solde_meur", "soldes_meur", False), ("depense_meur", "depenses_meur", False),
    ("tva_de", "tva", True), ("tva_garantie", "tva_garantie", True),
    ("postes_ressources", "postes_ressources", True),
    ("postes_depenses", "postes_depenses", True),
)
#: Les champs d'une ligne de ``cout.CoutAnnuel``.
CHAMPS_COUT_ANNUEL = (
    "annee", "observee", "coefficient_constants", "part_pib", "rapports", "pensionnes",
    "part_derives", "reversion_servie", "reforme_en_vigueur", "part_repartition",
)
#: Les champs d'une ligne de ``cout.AvenirAnnuel``. Les rapports, les masses et
#: les têtes par régime n'y sont pas : aucune page ne les lit.
CHAMPS_AVENIR_ANNUEL = (
    "annee", "projete", "base", "coefficient_constants", "pib", "dependance",
    "facteur_assiette_liberal", "part_derives", "reversion_servie",
    "reforme_en_vigueur", "part_stock", "base_modele", "facteur_reversion", "tetes",
    "salaire_reel", "derive",
)
#: Les champs de ``cout.GarantieProjetee``, et ceux de ``cout.PilierAnnuel``
#: avec ses grandeurs dérivées.
CHAMPS_GARANTIE = (
    "facteur", "effectif", "beneficiaires", "cout_constants", "ayants_droit",
    "taux_recours", "avances_liberees_constants", "reprises_constants",
    "stock_avances_constants", "taux_reel", "part_reprise", "duree_avances",
    "population_mortalite", "part_femmes", "avances_par_succession",
    "part_reprise_immediate", "report_annees", "facteur_report", "deces_en_couple",
    "duree_veuvage",
)
CHAMPS_PILIER = (
    "annee", "frais_versement", "frais_gestion", "encours", "rentes_brutes", "rentes",
    "frais_accumulation", "frais_rentes", "frais", "taux_frais_encours",
)


def _champs(objet, champs) -> dict:
    """Les ``champs`` de ``objet``, des dictionnaires recopiés."""
    return {champ: dict(valeur) if isinstance(valeur, dict) else valeur
            for champ in champs for valeur in (getattr(objet, champ),)}


def _figer_solde(solde, scenarios, bilan) -> dict:
    """``cout.Solde`` : ses lignes, et ce que ses accesseurs rendent, pour les
    ``scenarios`` comparés et, poste par poste, pour ceux du ``bilan``."""
    return {
        "premiere_annee_projetee": solde.premiere_annee_projetee,
        "premieres_annees_equilibrees": {
            scenario: solde.premiere_annee_equilibree(scenario) for scenario in scenarios},
        "annees": [
            {
                **_champs(ligne, CHAMPS_SOLDE_ANNUEL),
                **{cle: {scenario: getattr(ligne, accesseur)(scenario)
                         for scenario in (bilan if du_bilan else scenarios)}
                   for accesseur, cle, du_bilan in PAR_SYSTEME_SOLDE_ANNUEL},
                "ressources_meur": ligne.ressources_meur(),
                "recette_par_assiette": ligne.recette_par_assiette,
            }
            for ligne in solde.annees
        ],
    }


def _figer_solde_derive(solde, scenarios) -> dict:
    """Le solde de la variante dérivée, réduit à ce que la page en lit : le
    coefficient et le solde de chaque année."""
    return {
        "premiere_annee_projetee": solde.premiere_annee_projetee,
        "premieres_annees_equilibrees": {
            scenario: solde.premiere_annee_equilibree(scenario) for scenario in scenarios},
        "annees": [
            {"annee": ligne.annee, "projete": ligne.projete,
             "coefficients": {scenario: ligne.coefficient(scenario) for scenario in scenarios},
             "soldes": {scenario: ligne.solde(scenario) for scenario in scenarios}}
            for ligne in solde.annees
        ],
    }


def _figer_garantie(garantie) -> dict | None:
    return None if garantie is None else _champs(garantie, CHAMPS_GARANTIE)


def _figer_dette(dette, scenarios) -> dict:
    """``cout.Dette`` : ses lignes, et ce que ses accesseurs rendent."""
    return {
        "annee_depart": dette.annee_depart, "ecart_taux": dette.ecart_taux,
        "date_courbe": dette.date_courbe,
        "derniere_annee_cotee": dette.derniere_annee_cotee,
        "dette_publique_observee": dict(dette.dette_publique_observee),
        "annee_dette_publique": dette.annee_dette_publique,
        "horizons": {scenario: dette.horizon(scenario) for scenario in scenarios},
        "cumuls_soldes": {scenario: dette.cumul_soldes(scenario) for scenario in scenarios},
        "cumuls_interets": {scenario: dette.cumul_interets(scenario)
                            for scenario in scenarios},
        "annees": [
            {"annee": ligne.annee, "croissance": ligne.croissance, "taux": ligne.taux,
             "stocks": dict(ligne.stocks), "interets": dict(ligne.interets),
             "soldes": dict(ligne.soldes)}
            for ligne in dette.annees
        ],
    }


def _par_cas_type_affiche(poids: dict[str, float]) -> dict[str, float]:
    """Les poids de la grille du coût, rapportés aux cas types de la page
    (``castypes.cas_type_affiche``), dans leur ordre."""
    from ..castypes import cas_type_affiche

    rapportes: dict[str, list[float]] = {}
    for code, part in poids.items():
        rapportes.setdefault(cas_type_affiche(code), []).append(part)
    return {code: somme_ordonnee(parts) for code, parts in rapportes.items()}


def figer_cout(cout, scenarios, bilan, garantie: str, masse_du_scenario,
               dettes_decalees: dict, taux_tva_requis: tuple[float, int]) -> dict:
    """Le coût agrégé de ``cout.calculer_cout``.

    ``scenarios`` sont les systèmes que le site compare, ``bilan`` ceux du
    bilan poste par poste, ``garantie`` la clé de la garantie vieillesse, que
    le passé et l'avenir comptent à part ; ``masse_du_scenario`` est celle du
    modèle, qui dit la part de PIB de chaque système une année passée
    (``CoutAnnuel.part_pib_de``) ; ``dettes_decalees``, la dette recalculée
    sous un taux décalé, par écart ; ``taux_tva_requis``, ce que
    ``cout.taux_tva_requis`` rend sous la référence.
    """
    avec_garantie = (*scenarios, garantie)
    avenir = cout.avenir
    notionnels = [scenario for scenario in scenarios if scenario != "actuel"]
    liberal = [scenario for scenario in scenarios if scenario == "notionnel_liberal"]
    return {
        "annee_euros": cout.annee_euros,
        "generations": list(cout.generations),
        # Par cas type de la page : une variante de la grille du coût, l'agent
        # sédentaire de la CNRACL, compte avec celui dont elle porte le code.
        "poids": _par_cas_type_affiche(cout.poids),
        "poids_cotisants": _par_cas_type_affiche(cout.poids_cotisants),
        "cumuls": {scenario: cout.cumul(scenario) for scenario in avec_garantie},
        "cumul_observe": cout.cumul_observe(),
        "confondus_avec_actuel": list(cout.confondus_avec_actuel()),
        "annees": [
            {
                **_champs(ligne, CHAMPS_COUT_ANNUEL),
                # Du passé, la page ne lit que le facteur de la garantie : celui
                # de l'année de l'enquête sur la distribution des pensions.
                "garantie": None if ligne.garantie is None else {
                    "facteur": ligne.garantie.facteur},
                "pensions": ligne.pensions,
                "part_pib_pensions": ligne.part_pib_pensions,
                "observee_constants": ligne.observee_constants,
                "couts": {scenario: ligne.cout(scenario) for scenario in avec_garantie},
                "couts_constants": {scenario: ligne.cout_constants(scenario)
                                    for scenario in avec_garantie},
                "parts_pib": {
                    scenario: masse_du_scenario(
                        ligne.part_pib_pensions, ligne.part_derives,
                        ligne.rapports[scenario], scenario, ligne.reversion_servie,
                        ligne.reforme_en_vigueur)
                    for scenario in avec_garantie},
            }
            for ligne in cout.annees
        ],
        "avenir": {
            "premiere_annee_projetee": avenir.premiere_annee_projetee,
            "annee_bascule": avenir.annee_bascule,
            "annee_euros": avenir.annee_euros,
            "cumuls": {scenario: avenir.cumul(scenario) for scenario in avec_garantie},
            "ecarts_cumules": {scenario: avenir.ecart_cumule(scenario)
                               for scenario in notionnels},
            "cumul_reprises": avenir.cumul_reprises(),
            # La seule que la page demande : depuis la première année projetée.
            "decompositions": {
                avenir.premiere_annee_projetee: {
                    annee: list(valeurs) for annee, valeurs
                    in avenir.decomposition(avenir.premiere_annee_projetee).items()},
            },
            "annees": [
                {
                    **_champs(ligne, CHAMPS_AVENIR_ANNUEL),
                    "garantie": _figer_garantie(ligne.garantie),
                    "pilier": None if ligne.pilier is None else _champs(
                        ligne.pilier, CHAMPS_PILIER),
                    "couts_constants": {scenario: ligne.cout_constants(scenario)
                                        for scenario in avec_garantie},
                    "parts_pib_derive": {scenario: ligne.part_pib_derive(scenario)
                                         for scenario in liberal},
                    "parts_pib": {scenario: ligne.part_pib(scenario)
                                  for scenario in avec_garantie},
                    "reprises_constants": ligne.reprises_constants(),
                    "reprises": ligne.reprises(),
                    "part_pib_reprises": ligne.part_pib_reprises(),
                    "garantie_nette_constants": ligne.garantie_nette_constants(),
                }
                for ligne in avenir.annees
            ],
        },
        "solde": _figer_solde(cout.solde, scenarios, bilan),
        "solde_derive": _figer_solde_derive(cout.solde_derive, scenarios),
        "dette": _figer_dette(cout.dette, scenarios),
        # De la dette de la variante dérivée, la page ne cite que l'horizon.
        "dette_derive": {scenario: cout.dette_derive.horizon(scenario)
                         for scenario in scenarios},
        "taux_tva_requis": list(taux_tva_requis),
        # Ce que la page cite de la dette sous un taux décalé : l'horizon.
        "dettes_decalees": {
            ecart: {scenario: dette.horizon(scenario) for scenario in scenarios}
            for ecart, dette in dettes_decalees.items()},
    }


class _Ligne:
    """Une ligne figée : ses champs en attributs, ceux que la table porte, et
    ce que ses accesseurs rendent, par système, sous les clés qu'elle leur
    donne."""

    def __init__(self, brut: dict, champs) -> None:
        self._brut = brut
        for champ in champs:
            if champ in brut:
                setattr(self, champ, brut[champ])

    def _par_systeme(self, cle: str, scenario: str):
        return _lire(self._brut[cle], scenario, f"{cle} du système")


class SoldeAnnuelFige(_Ligne):
    """Une année du bilan, sous les accesseurs de ``cout.SoldeAnnuel``. Celle
    de la variante dérivée ne porte que son coefficient et son solde."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_SOLDE_ANNUEL)
        if "recette_par_assiette" in brut:
            self.recette_par_assiette = brut["recette_par_assiette"]

    def coefficient(self, scenario: str) -> float:
        return self._par_systeme("coefficients", scenario)

    def depense(self, scenario: str) -> float:
        return self._par_systeme("depenses_par_systeme", scenario)

    def depense_nette(self, scenario: str) -> float:
        return self._par_systeme("depenses_nettes_par_systeme", scenario)

    def solde(self, scenario: str) -> float:
        return self._par_systeme("soldes", scenario)

    def ressources_de(self, scenario: str) -> float:
        return self._par_systeme("ressources_par_systeme", scenario)

    def solde_meur(self, scenario: str) -> float:
        return self._par_systeme("soldes_meur", scenario)

    def depense_meur(self, scenario: str) -> float:
        return self._par_systeme("depenses_meur", scenario)

    def ressources_meur(self) -> float:
        return self._brut["ressources_meur"]

    def tva_de(self, scenario: str) -> float:
        return self._par_systeme("tva", scenario)

    def tva_garantie(self, scenario: str) -> float:
        return self._par_systeme("tva_garantie", scenario)

    def postes_ressources(self, scenario: str) -> dict[str, float]:
        return dict(self._par_systeme("postes_ressources", scenario))

    def postes_depenses(self, scenario: str) -> dict[str, float]:
        return dict(self._par_systeme("postes_depenses", scenario))


class SoldeFige:
    """Le bilan de chaque année, sous les accesseurs de ``cout.Solde``."""

    def __init__(self, brut: dict) -> None:
        self.annees = [SoldeAnnuelFige(ligne) for ligne in brut["annees"]]
        self.premiere_annee_projetee = brut["premiere_annee_projetee"]
        self._equilibrees = brut["premieres_annees_equilibrees"]

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    @property
    def derniere_annee_observee(self) -> int:
        return self.premiere_annee_projetee - 1

    def observees(self) -> list[SoldeAnnuelFige]:
        return [ligne for ligne in self.annees if not ligne.projete]

    def projetees(self) -> list[SoldeAnnuelFige]:
        return [ligne for ligne in self.annees if ligne.projete]

    def annee(self, millesime: int) -> SoldeAnnuelFige | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def solde_moyen(self, scenario: str, debut: int, fin: int) -> float:
        """La moyenne des soldes de la fenêtre, additionnés de gauche à
        droite comme ``cout.Solde.solde_moyen``."""
        lignes = [ligne for ligne in self.annees if debut <= ligne.annee <= fin]
        if not lignes:
            return 0.0
        return somme_ordonnee(ligne.solde(scenario) for ligne in lignes) / len(lignes)

    def premiere_annee_equilibree(self, scenario: str) -> int | None:
        return _lire(self._equilibrees, scenario, "première année équilibrée du système")


class GarantieFigee(_Ligne):
    """La garantie d'une année, sous les champs de ``cout.GarantieProjetee`` —
    ceux de l'avenir, et le seul facteur d'une année passée."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_GARANTIE)


class PilierFige(_Ligne):
    """Le pilier d'une année, par euro versé, sous les accesseurs de
    ``cout.PilierAnnuel``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_PILIER)

    def niveaux(self, versements: float) -> dict[str, float]:
        """Chaque grandeur au niveau des ``versements`` donnés, même unité :
        le produit de ``cout.PilierAnnuel.niveaux``."""
        return {
            "versements": versements,
            "frais_versement": self.frais_versement * versements,
            "frais_gestion": self.frais_gestion * versements,
            "frais_accumulation": self.frais_accumulation * versements,
            "encours": self.encours * versements,
            "rentes_brutes": self.rentes_brutes * versements,
            "rentes": self.rentes * versements,
            "frais_rentes": self.frais_rentes * versements,
            "frais": self.frais * versements,
        }


def _garantie(brut: dict | None) -> GarantieFigee | None:
    return None if brut is None else GarantieFigee(brut)


class CoutAnnuelFige(_Ligne):
    """Une année passée, sous les accesseurs de ``cout.CoutAnnuel``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_COUT_ANNUEL)
        self.garantie = _garantie(brut["garantie"])
        self.pensions = brut["pensions"]
        self.part_pib_pensions = brut["part_pib_pensions"]
        self.observee_constants = brut["observee_constants"]

    def cout(self, scenario: str) -> float:
        return self._par_systeme("couts", scenario)

    def cout_constants(self, scenario: str) -> float:
        return self._par_systeme("couts_constants", scenario)

    def part_pib_de(self, scenario: str) -> float:
        """La part de PIB du système cette année, règle de la réversion
        comprise (``cout.masse_du_scenario``)."""
        return self._par_systeme("parts_pib", scenario)


class AvenirAnnuelFige(_Ligne):
    """Une année projetée, sous les accesseurs de ``cout.AvenirAnnuel``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_AVENIR_ANNUEL)
        self.garantie = _garantie(brut["garantie"])
        self.pilier = None if brut["pilier"] is None else PilierFige(brut["pilier"])

    def cout_constants(self, scenario: str) -> float:
        return self._par_systeme("couts_constants", scenario)

    def part_pib_derive(self, scenario: str) -> float:
        return self._par_systeme("parts_pib_derive", scenario)

    def part_pib(self, scenario: str) -> float:
        return self._par_systeme("parts_pib", scenario)

    def reprises_constants(self) -> float:
        return self._brut["reprises_constants"]

    def reprises(self) -> float:
        return self._brut["reprises"]

    def part_pib_reprises(self) -> float:
        return self._brut["part_pib_reprises"]

    def garantie_nette_constants(self) -> float:
        return self._brut["garantie_nette_constants"]


class AvenirFige:
    """L'avenir de chaque système, sous les accesseurs de ``cout.Avenir``."""

    def __init__(self, brut: dict) -> None:
        self.annees = [AvenirAnnuelFige(ligne) for ligne in brut["annees"]]
        self.premiere_annee_projetee = brut["premiere_annee_projetee"]
        self.annee_bascule = brut["annee_bascule"]
        self.annee_euros = brut["annee_euros"]
        self._brut = brut

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    def projetees(self) -> list[AvenirAnnuelFige]:
        return [ligne for ligne in self.annees if ligne.projete]

    def annee(self, millesime: int) -> AvenirAnnuelFige | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def cumul(self, scenario: str) -> float:
        return _lire(self._brut["cumuls"], scenario, "cumul du système")

    def ecart_cumule(self, scenario: str) -> float:
        return _lire(self._brut["ecarts_cumules"], scenario, "écart cumulé du système")

    def cumul_reprises(self) -> float:
        return self._brut["cumul_reprises"]

    def decomposition(self, depuis: int) -> dict[int, tuple[float, float]]:
        table = _lire(self._brut["decompositions"], str(depuis), "décomposition depuis")
        return {int(annee): tuple(valeurs) for annee, valeurs in table.items()}


class DetteAnnuelleFigee:
    """Une année du stock, sous les accesseurs de ``cout.DetteAnnuelle``."""

    def __init__(self, brut: dict) -> None:
        self.annee = brut["annee"]
        self.croissance = brut["croissance"]
        self.taux = brut["taux"]
        self.stocks = brut["stocks"]
        self.interets = brut["interets"]
        self.soldes = brut["soldes"]

    def stock(self, scenario: str) -> float:
        return self.stocks[scenario]

    def interet(self, scenario: str) -> float:
        return self.interets[scenario]

    def solde(self, scenario: str) -> float:
        return self.soldes[scenario]


class DetteFigee:
    """Le stock que les soldes accumulent, sous les accesseurs de ``cout.Dette``."""

    def __init__(self, brut: dict) -> None:
        self.annees = [DetteAnnuelleFigee(ligne) for ligne in brut["annees"]]
        self.annee_depart = brut["annee_depart"]
        self.ecart_taux = brut["ecart_taux"]
        self.date_courbe = brut["date_courbe"]
        self.derniere_annee_cotee = brut["derniere_annee_cotee"]
        self.dette_publique_observee = {int(annee): valeur for annee, valeur
                                        in brut["dette_publique_observee"].items()}
        self.annee_dette_publique = brut["annee_dette_publique"]
        self._brut = brut

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee if self.annees else 0

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee if self.annees else 0

    @property
    def dette_publique_depart(self) -> float:
        return self.dette_publique_observee.get(self.annee_dette_publique, 0.0)

    def dette_publique(self, scenario: str, millesime: int) -> float:
        return self.dette_publique_depart + self.stock(scenario, millesime)

    def annee(self, millesime: int) -> DetteAnnuelleFigee | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def stock(self, scenario: str, millesime: int) -> float:
        ligne = self.annee(millesime)
        return ligne.stock(scenario) if ligne else 0.0

    def horizon(self, scenario: str) -> float:
        return _lire(self._brut["horizons"], scenario, "horizon du système")

    def cumul_soldes(self, scenario: str) -> float:
        return _lire(self._brut["cumuls_soldes"], scenario, "cumul des soldes du système")

    def cumul_interets(self, scenario: str) -> float:
        return _lire(self._brut["cumuls_interets"], scenario,
                     "cumul des intérêts du système")


class HorizonsFiges:
    """Une dette réduite à ce que la page en cite : son stock à l'horizon."""

    def __init__(self, horizons: dict) -> None:
        self._horizons = horizons

    def horizon(self, scenario: str) -> float:
        return _lire(self._horizons, scenario, "horizon du système")


class CoutFige:
    """Le coût agrégé de tous les systèmes, sous les accesseurs de
    ``cout.Cout``, et la dette sous un taux décalé (``dette_decalee``)."""

    def __init__(self, brut: dict) -> None:
        self.annees = [CoutAnnuelFige(ligne) for ligne in brut["annees"]]
        self.avenir = AvenirFige(brut["avenir"])
        self.solde = SoldeFige(brut["solde"])
        self.solde_derive = SoldeFige(brut["solde_derive"])
        self.dette = DetteFigee(brut["dette"])
        self.dette_derive = HorizonsFiges(brut["dette_derive"])
        self.annee_euros = brut["annee_euros"]
        self.generations = tuple(brut["generations"])
        self.poids = dict(brut["poids"])
        self.poids_cotisants = dict(brut["poids_cotisants"])
        self._brut = brut

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    def cumul(self, scenario: str) -> float:
        return _lire(self._brut["cumuls"], scenario, "cumul du système")

    def cumul_observe(self) -> float:
        return self._brut["cumul_observe"]

    def confondus_avec_actuel(self) -> tuple[str, ...]:
        return tuple(self._brut["confondus_avec_actuel"])

    def annee(self, millesime: int) -> CoutAnnuelFige | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def taux_tva_requis(self) -> tuple[float, int]:
        """Le taux de TVA unique qui couvrirait juste chaque année, garantie
        comprise, et l'année qui le fixe (``cout.taux_tva_requis``)."""
        requis, annee = self._brut["taux_tva_requis"]
        return requis, annee

    def dette_decalee(self, ecart: float) -> HorizonsFiges:
        """La dette recalculée au taux de la courbe décalé de ``ecart``
        (``cout.calculer_dette``), que la page cite à l'horizon."""
        return HorizonsFiges(_lire(self._brut["dettes_decalees"], repr(float(ecart)),
                                   "dette au taux décalé de"))


# -- le coût sous les variantes de population de l'INSEE ----------------------
#
# LA PAGE COÛT MONTRE LA RÉFÉRENCE, sous le scénario central de l'INSEE. Ce
# qu'une longévité, une fécondité ou des migrations plus basses ou plus hautes
# en feraient (action 138, étape 7) tient, pour chaque composante, en un
# tableau : la dépense de chaque système à quelques années, son solde à
# l'horizon, et son solde moyen sur les années projetées, sous chacune des
# trois hypothèses. Le coût entier n'est figé que sous le central.


def figer_variantes(couts: dict, scenarios, annees) -> dict:
    """Le coût sous chaque hypothèse d'une composante de la population
    (``couts``, par hypothèse, ``basse``, ``centrale`` et ``haute``, ce que
    ``cout.calculer_cout`` rend), pour les systèmes ``scenarios`` et les
    années ``annees`` de la dépense.

    La dépense est celle du bilan (``SoldeAnnuel.depense``), dont le solde
    est tiré : les deux se lisent ensemble. Le solde moyen court sur les
    années que le bilan projette, comme sur la page : de sa première année
    projetée à son horizon.
    """
    def fenetre(cout):
        return cout.solde.premiere_annee_projetee, cout.solde.derniere_annee
    fenetres = {fenetre(cout) for cout in couts.values()}
    if len(fenetres) != 1:
        raise ValueError(f"les hypothèses ne projettent pas les mêmes années : {fenetres}")
    debut, fin = fenetres.pop()
    return {
        "hypotheses": list(couts),
        "annees": list(annees),
        "fenetre": [debut, fin],
        "parts_pib": {
            hypothese: {scenario: {str(annee): cout.solde.annee(annee).depense(scenario)
                                   for annee in annees}
                        for scenario in scenarios}
            for hypothese, cout in couts.items()},
        "soldes": {
            hypothese: {scenario: cout.solde.annee(fin).solde(scenario)
                        for scenario in scenarios}
            for hypothese, cout in couts.items()},
        "soldes_moyens": {
            hypothese: {scenario: cout.solde.solde_moyen(scenario, debut, fin)
                        for scenario in scenarios}
            for hypothese, cout in couts.items()},
    }


class VariantesFigees:
    """Le coût sous les trois hypothèses d'une composante de la population
    (espérance de vie, fécondité, migrations), que la page Coût met côte à
    côte."""

    def __init__(self, brut: dict):
        self._brut = brut
        self.hypotheses: tuple[str, ...] = tuple(brut["hypotheses"])
        self.annees: tuple[int, ...] = tuple(int(annee) for annee in brut["annees"])
        self.premiere_annee, self.derniere_annee = (int(a) for a in brut["fenetre"])

    def part_pib(self, hypothese: str, scenario: str, annee: int) -> float:
        """La dépense d'un système une année, en part de PIB."""
        parts = _lire(_lire(self._brut["parts_pib"], hypothese, "hypothèse"),
                      scenario, "système")
        return float(_lire(parts, str(annee), "année"))

    def solde(self, hypothese: str, scenario: str) -> float:
        """Le solde d'un système à l'horizon, en part de PIB."""
        return float(_lire(_lire(self._brut["soldes"], hypothese, "hypothèse"),
                           scenario, "système"))

    def solde_moyen(self, hypothese: str, scenario: str) -> float:
        """Le solde moyen d'un système sur les années projetées, en part de PIB."""
        return float(_lire(_lire(self._brut["soldes_moyens"], hypothese, "hypothèse"),
                           scenario, "système"))


# -- le bilan du compte ----------------------------------------------------------

#: Ce que la table porte du bilan d'un système (``bilan_compte.BilanCompte``) :
#: ses champs, puis les indicateurs qu'il en tire, figés eux aussi pour que le
#: lecteur n'en refasse aucune opération.
CHAMPS_BILAN_COMPTE = (
    "cotisations", "age_cotisations", "age_pensions", "reserves", "dette", "depense",
    "ressources", "assiette", "duree_rotation", "actif_cotisation", "actif",
    "ratio_equilibre", "taux_equilibre", "taux_cotisation", "taux_cotisation_equilibre",
)


def figer_bilan_compte(bilans: dict, rendement: float | None) -> dict:
    """Le bilan du compte de chaque système (``bilans``, ce que
    ``bilan_compte.bilans_gardes`` rend, une seule année), et le rendement
    comptable des réserves cette année-là, ``None`` si le COR ne le donne
    pas."""
    annees = {bilan.annee for bilan in bilans.values()}
    if len(annees) != 1:
        raise ValueError(f"les bilans ne sont pas d'une seule année : {annees}")
    return {
        "annee": annees.pop(),
        "rendement": rendement,
        "systemes": {cle: {champ: getattr(bilan, champ) for champ in CHAMPS_BILAN_COMPTE}
                     for cle, bilan in bilans.items()},
    }


class BilanSystemeFige(_Ligne):
    """Le bilan d'un système, sous les noms de ``bilan_compte.BilanCompte``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_BILAN_COMPTE)


class BilanCompteFige:
    """Le bilan du compte notionnel de chaque système, à la manière suédoise
    (action 138, étape 19), une année : ce qu'il doit au titre des droits
    acquis, et ce que ses cotisations et ses réserves peuvent porter. La page
    Coût le met après la dette que les soldes à venir accumulent."""

    def __init__(self, brut: dict) -> None:
        self._systemes = brut["systemes"]
        self.annee: int = int(brut["annee"])
        self.rendement: float | None = brut["rendement"]

    def systeme(self, scenario: str) -> BilanSystemeFige:
        return BilanSystemeFige(_lire(self._systemes, scenario, "système"))


# -- les leviers de l'équilibre ------------------------------------------------

#: Ce que la table porte des leviers d'une année (``leviers.Leviers``) et des
#: écarts d'un horizon (``leviers.EcartsSurHorizon``), sous leurs noms.
CHAMPS_LEVIERS = ("pension", "prelevement", "age")
CHAMPS_ECARTS_HORIZON = ("pension_gap", "tax_gap")


def figer_leviers(leviers: dict) -> dict:
    """Les trois leviers qui équilibreraient chaque système chaque année, et
    ses écarts sur les horizons du COR (``leviers``, par système, ce que
    ``leviers.leviers_du_modele`` rend). Tous les systèmes ont les mêmes
    années et les mêmes horizons, qui partent tous de la même année ; l'âge
    d'une année que nul recul des bornes cherchées n'équilibre reste ``None``,
    et la table porte ces bornes."""
    from ..leviers import RECUL_MAXIMAL, RECUL_MINIMAL

    annees = {tuple(sorted(systeme.annuels)) for systeme in leviers.values()}
    horizons = {tuple(sorted(systeme.horizons)) for systeme in leviers.values()}
    debuts = {ecart.debut for systeme in leviers.values() for ecart in systeme.horizons.values()}
    if len(annees) != 1 or len(horizons) != 1 or len(debuts) != 1:
        raise ValueError(f"les systèmes n'ont pas les mêmes années : {annees}, {horizons}, "
                         f"{debuts}")
    return {
        "debut": debuts.pop(),
        "annees": list(annees.pop()),
        "horizons": list(horizons.pop()),
        "recul": [RECUL_MINIMAL, RECUL_MAXIMAL],
        "systemes": {
            scenario: {
                "annuels": {str(annee): {champ: getattr(ligne, champ)
                                         for champ in CHAMPS_LEVIERS}
                            for annee, ligne in sorted(systeme.annuels.items())},
                "horizons": {str(fin): {champ: getattr(ecart, champ)
                                        for champ in CHAMPS_ECARTS_HORIZON}
                             for fin, ecart in sorted(systeme.horizons.items())},
            }
            for scenario, systeme in leviers.items()},
    }


class LeviersAnnuelsFiges(_Ligne):
    """Les leviers d'un système une année, sous les noms de ``leviers.Leviers``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_LEVIERS)


class EcartsHorizonFiges(_Ligne):
    """Les écarts d'un système sur un horizon, sous les noms de
    ``leviers.EcartsSurHorizon``."""

    def __init__(self, brut: dict) -> None:
        super().__init__(brut, CHAMPS_ECARTS_HORIZON)


class LeviersFiges:
    """Ce que chaque levier, seul, devrait faire pour équilibrer chaque système
    chaque année — rogner la pension, relever le taux de prélèvement, reculer
    l'âge —, et l'ajustement immédiat qui l'équilibrerait en moyenne depuis
    ``debut`` jusqu'à chaque horizon du COR (action 138, étape 3). La page Coût
    les met sous le coefficient d'équilibre."""

    def __init__(self, brut: dict) -> None:
        self._systemes = brut["systemes"]
        self.debut: int = int(brut["debut"])
        self.annees: tuple[int, ...] = tuple(int(annee) for annee in brut["annees"])
        self.horizons: tuple[int, ...] = tuple(int(fin) for fin in brut["horizons"])
        #: Les bornes du recul cherché, en années, hors desquelles l'âge vaut
        #: ``None``.
        self.recul: tuple[float, float] = tuple(brut["recul"])

    def annee(self, scenario: str, annee: int) -> LeviersAnnuelsFiges:
        annuels = _lire(self._systemes, scenario, "système")["annuels"]
        return LeviersAnnuelsFiges(_lire(annuels, str(annee), "année"))

    def horizon(self, scenario: str, fin: int) -> EcartsHorizonFiges:
        horizons = _lire(self._systemes, scenario, "système")["horizons"]
        return EcartsHorizonFiges(_lire(horizons, str(fin), "horizon"))


# -- la table ------------------------------------------------------------------


@dataclass(frozen=True)
class AgregatsFiges:
    """Ce que les trois pages qui agrègent lisent, tel que la table le porte."""

    cas_types: CasTypesFiges
    avantages: AvantagesFiges
    classement: ClassementFige
    cout: CoutFige
    esperance_vie: VariantesFigees
    fecondite: VariantesFigees
    migrations: VariantesFigees
    bilan_compte: BilanCompteFige
    leviers: LeviersFiges


def depuis_dictionnaire(donnees: dict) -> AgregatsFiges:
    """Reconstruit la table, JSON du dépôt ou clé du paquet."""
    return AgregatsFiges(
        cas_types=_cas_types(donnees["cas_types"]),
        avantages=_avantages(donnees["avantages"]),
        classement=_classement(donnees["classement"]),
        cout=CoutFige(donnees["cout"]),
        esperance_vie=VariantesFigees(donnees["esperance_vie"]),
        fecondite=VariantesFigees(donnees["fecondite"]),
        migrations=VariantesFigees(donnees["migrations"]),
        bilan_compte=BilanCompteFige(donnees["bilan_compte"]),
        leviers=LeviersFiges(donnees["leviers"]),
    )


def charger_agregats(racine: Path) -> AgregatsFiges:
    """La table du dépôt. ``scripts/construire_donnees.py`` l'écrit."""
    chemin = Path(racine) / "derive" / "agregats.json"
    with chemin.open(encoding="utf-8") as fichier:
        return depuis_dictionnaire(json.load(fichier))
