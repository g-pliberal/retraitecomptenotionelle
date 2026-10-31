"""Ce que les trois pages qui agrègent lisent du modèle, fabriqué sous la référence.

POURQUOI CE FICHIER EXISTE. Coût, Carrières types et Droits non cotisés
croisent treize carrières types avec sept générations, et chiffrent ce que
chaque système coûterait, année par année jusqu'en 2070. Elles se calculaient
chez le lecteur, par le portage JavaScript du coût, sous les réglages de
l'adresse : de trois à huit secondes à la première visite. Le propriétaire a
retiré leurs réglages le 10 octobre 2026 (action 150) : elles ne montrent plus
que la référence depuis le lendemain. Ce qu'elles lisent du modèle est donc
calculé une fois, par ``scripts/construire_donnees.py``, écrit dans
``data/derive/agregats.json`` par les écrivains de ce module, embarqué dans
le paquet que le navigateur charge, et lu par ``moteur/js/agregats.js``, son
seul lecteur depuis l'action 161 (note de décision 0005).

CE QUI EST FIGÉ, ET CE QUI NE L'EST PAS. Tout ce qu'une règle du modèle
décide : la grille des cas types, l'âge auquel chacun part, ce que coûtent les
avantages non contributifs, les deux départs qui disent ce que le classement
d'un emploi ajoute. Ce qui n'est
qu'une donnée lue — les comptes du COR, les dépenses publiées, la
distribution des pensions — reste dans le paquet, où les pages la lisent
comme avant. Le lecteur ne calcule rien qu'une règle décide : il rend ce que
la table porte. Une lecture qu'elle ne porte pas lève une erreur, plutôt que
de rendre un zéro : une page qui la demanderait se tromperait sans bruit.

LE PYTHON GARDE TOUS SES RÉGLAGES. La table ne vaut que pour la référence,
celle de ``Parametres()`` ; le modèle se calcule toujours sous toute autre
règle, et c'est le simulateur, sur une carrière, qui les montre au lecteur.

Chaque partie a son écrivain : ``figer_*`` écrit la table depuis les objets
du modèle, en n'y lisant que leurs accesseurs, et ``moteur/js/agregats.js``
la rend sous ces mêmes accesseurs. Les lecteurs que ce module portait aussi
ne servaient plus qu'aux tests : ils sont partis (action 161, étape 4), et
``tests/test_agregats.py`` vérifie, par le portage, que la table dit ce que
dit le modèle.
"""

from __future__ import annotations

from ..somme import somme_ordonnee


def _cle_grille(code: str, generation: int) -> str:
    """La clé d'une case de la grille dans la table, celle du portage."""
    return f"{code}|{generation}"


# -- les carrières types -------------------------------------------------------


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


# -- les avantages non contributifs --------------------------------------------


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


# -- le classement de l'emploi --------------------------------------------------


def figer_departs(actif, declasse) -> list[dict]:
    """Les deux départs comparés : de chacun, la pension du système actuel et
    la durée qu'il requiert, que le portage calcule (``pont.carrieres``)."""
    return [{"pension_annuelle": lu["pension_annuelle"],
             "trimestres_requis": lu["trimestres_requis"]}
            for lu in (actif, declasse)]


# -- le coût agrégé ------------------------------------------------------------
#
# LA PAGE COÛT LIT LE COÛT ENTIER : le passé de chaque système (``CoutAnnuel``),
# son avenir (``AvenirAnnuel``), le bilan de chaque année (``SoldeAnnuel``), la
# dette que les soldes accumulent (``DetteAnnuelle``). Chaque ligne figée porte
# les champs de la ligne du modèle que la page lit, tels quels, et ce que ses
# accesseurs rendent pour les systèmes qu'elle leur demande : les quatre que le
# site compare, la garantie vieillesse là où le modèle la compte à part, les
# deux du bilan poste par poste (``SYSTEMES_BILAN``) pour ce qui n'y sert
# qu'à lui. Le reste n'y est pas, et un accesseur du lecteur
# (``moteur/js/agregats.js``) qu'on interrogerait sur un autre système lève
# une erreur. Un accesseur qui prend un nombre quelconque — le solde moyen
# d'une fenêtre, le pilier à un niveau de versements, le stock d'une année —
# s'y rend depuis ce que la ligne porte, par la même opération que le
# modèle : une moyenne, un produit, une lecture.

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


# -- les leviers de l'équilibre ------------------------------------------------

#: Ce que la table porte des leviers d'une année (``leviers.Leviers``) et des
#: écarts d'un horizon (``leviers.EcartsSurHorizon``), sous leurs noms.
CHAMPS_LEVIERS = ("pension", "prelevement", "age")
CHAMPS_ECARTS_HORIZON = ("pension_gap", "tax_gap")


def _leviers_par_annee(annuels: dict) -> dict:
    """Les leviers de chaque année, sous leurs noms, l'année en clé."""
    return {str(annee): {champ: getattr(ligne, champ) for champ in CHAMPS_LEVIERS}
            for annee, ligne in sorted(annuels.items())}


def figer_leviers(leviers: dict) -> dict:
    """Les trois leviers qui équilibreraient chaque système chaque année, et
    ses écarts sur les horizons du COR (``leviers``, par système, ce que
    ``leviers.leviers_du_modele`` rend). Tous les systèmes ont les mêmes
    années et les mêmes horizons, qui partent tous de la même année ; l'âge
    d'une année que nul recul des bornes cherchées n'équilibre reste ``None``,
    et la table porte ces bornes. Puis les leviers de chaque solde visé, dans
    l'ordre des soldes (``soldes_vises``), aux mêmes années pour tous
    (``annees_visees``) : le solveur inverse de la page Coût."""
    from ..leviers import RECUL_MAXIMAL, RECUL_MINIMAL

    annees = {tuple(sorted(systeme.annuels)) for systeme in leviers.values()}
    horizons = {tuple(sorted(systeme.horizons)) for systeme in leviers.values()}
    debuts = {ecart.debut for systeme in leviers.values() for ecart in systeme.horizons.values()}
    soldes = {tuple(systeme.vises) for systeme in leviers.values()}
    visees = {tuple(sorted(annuels)) for systeme in leviers.values()
              for annuels in systeme.vises.values()}
    if len(annees) != 1 or len(horizons) != 1 or len(debuts) != 1:
        raise ValueError(f"les systèmes n'ont pas les mêmes années : {annees}, {horizons}, "
                         f"{debuts}")
    if len(soldes) != 1 or len(visees) > 1:
        raise ValueError(f"les systèmes n'ont pas les mêmes soldes visés : {soldes}, {visees}")
    return {
        "debut": debuts.pop(),
        "annees": list(annees.pop()),
        "horizons": list(horizons.pop()),
        "recul": [RECUL_MINIMAL, RECUL_MAXIMAL],
        "soldes_vises": list(soldes.pop()),
        "annees_visees": list(visees.pop()) if visees else [],
        "systemes": {
            scenario: {
                "annuels": _leviers_par_annee(systeme.annuels),
                "horizons": {str(fin): {champ: getattr(ecart, champ)
                                        for champ in CHAMPS_ECARTS_HORIZON}
                             for fin, ecart in sorted(systeme.horizons.items())},
                "vises": [_leviers_par_annee(annuels) for annuels in systeme.vises.values()],
            }
            for scenario, systeme in leviers.items()},
    }
