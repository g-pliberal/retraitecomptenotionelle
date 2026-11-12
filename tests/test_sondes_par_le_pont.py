"""Les sondes de la prose et les mesures de l'accueil sans le moteur Python.

Le moteur d'une carrière n'aura qu'un exemplaire, en JavaScript (action 161) :
``scripts/mesures_prose.py``, que ``verifier_prose.py`` lance à chaque envoi,
et ``scripts/mesures_accueil.py`` cessent d'y entrer (lot A, seconde ligne).
Chaque règle qu'une sonde appelait une à une se demande au portage par le
pont (``pont.droit``), sous le nom de son jumeau Python ; ce fichier dit ce
que chacune rend, par le chiffre que la prose publie ou que le texte fixe, et
:func:`outils_pont.droit_et_refait` la fait refaire au jumeau, au bit près,
tant qu'il reste. Puis il fait tourner les sondes sous le relevé de
``scripts/entrees_du_moteur.py`` : plus aucune n'entre dans le moteur Python.
"""

from __future__ import annotations

import shutil
import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle.config import (PRIME_TERME_MILIEU, ModeIndexation, Parametres,
                                         SituationFoyer)

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import entrees_du_moteur  # noqa: E402
from outils_pont import droit_et_refait  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("node") is None,
                                reason="node absent : le pont ne se vérifie pas ici")


def _rendu(appels: dict[str, tuple], parametres=None) -> dict:
    """Ce que le portage rend de ces appels, son jumeau Python confronté."""
    lus, refus = droit_et_refait(appels, parametres)
    assert refus == {}
    return lus


# -- les règles appelées une à une ------------------------------------------------


def test_le_pont_rend_l_age_de_reference_d_une_annee():
    """L'âge de référence du compte est, par défaut, un âge fixe : celui des
    paramètres, quelle que soit l'année de la liquidation."""
    lus = _rendu({str(annee): ("age_reference.age", pont.SIMULATEUR, annee)
                  for annee in (1950, 1990, 2026)})
    assert set(lus.values()) == {Parametres().age_reference_fixe}


def test_le_pont_rend_ce_que_coute_un_depart_anticipe():
    """La méthodologie chiffre un départ cinq ans avant l'âge de référence, en
    2026 : 4,6 années d'espérance de vie de plus au diviseur, et une pension
    de 17,0 % plus basse à capital donné."""
    reference = Parametres().age_reference_fixe
    lus = _rendu({
        "avant": ("conversion.coefficient.esperance_residuelle", pont.SIMULATEUR,
                  reference - 5, 2026),
        "reference": ("conversion.coefficient.esperance_residuelle", pont.SIMULATEUR,
                      reference, 2026),
        "garde": ("conversion.effet_anticipation", pont.SIMULATEUR, reference - 5, reference,
                  2026),
    })
    assert round(lus["avant"] - lus["reference"], 1) == 4.6
    assert round((1 - lus["garde"]) * 100, 1) == 17.0


def test_le_pont_rend_le_cumul_d_une_regle_d_indexation():
    """Sous la règle des prix, le compte reçoit en 1981 la hausse des prix de
    l'année, 13,4 % (INSEE) ; les paramètres de la demande choisissent la
    règle."""
    prix = replace(Parametres(), mode_indexation=ModeIndexation("prix"))
    lus = _rendu({"1981": ("indexation.coefficient", pont.SIMULATEUR, 1980, 1981)}, prix)
    assert round((lus["1981"] - 1) * 100, 1) == 13.4


def test_le_pont_rend_ce_qu_un_frais_retire_a_la_reserve_d_une_rente():
    """Le frais annuel sur la réserve de la rente, celui des paramètres, retire
    7,1 % à la rente d'une liquidation à 64 ans en 2040 (méthodologie)."""
    frais = Parametres().frais_encours_rente_capitalisation
    lus = _rendu({"a": ("capitalisation.facteur_encours_rente", pont.SIMULATEUR, frais, 64.0,
                        2040)})
    assert round((1 - lus["a"]) * 100, 1) == 7.1


def test_le_pont_rend_le_salaire_moyen_d_une_annee():
    """Le salaire moyen par tête de l'année d'ancrage est son niveau certifié :
    40 897 € en 2024."""
    lus = _rendu({"2024": ("carriere.salaire_moyen_annuel", pont.SIMULATEUR, 2024)})
    assert lus["2024"] == 40_897.0


def test_le_pont_rend_le_partage_de_la_restitution():
    """En 2024, 28,0 % des impôts affectés sont assis sur une rémunération
    (méthodologie) ; les points de CSG rendus sont une fraction positive."""
    lus = _rendu({
        "part": ("restitution.part_du_poste", pont.SIMULATEUR, 2024),
        "csg": ("restitution.annuelle.points_csg", pont.SIMULATEUR, 2024),
    })
    assert round(lus["part"] * 100, 1) == 28.0
    assert 0 < lus["csg"] < 0.1


def test_le_pont_rend_la_part_retraite_seule_du_taux_de_l_etat():
    """Ce que l'État porte au compte de son taux versé : 56,3 % pour un civil,
    40,6 % pour un militaire (méthodologie) ; et, pour le militaire d'avant
    2006, sa part rapportée au taux civil."""
    lus = _rendu({"parts": ("compte.parts_retraite_seule", pont.SIMULATEUR)})
    civil, militaire, militaire_sur_taux_civil = lus["parts"]
    assert round(civil * 100, 1) == 56.3
    assert round(militaire * 100, 1) == 40.6
    assert militaire_sur_taux_civil > civil


def test_le_pont_rend_le_regime_unique_de_la_bascule():
    """Le régime unique qui naît à la bascule : ouvert à 65 ans, le taux plein
    à 67, 172 trimestres, et le taux du statut pivot du privé, 25,83 % ; sous
    un autre critère de taux, la fusion refaite."""
    bascule = Parametres().annee_bascule
    lus = _rendu({
        "modele": ("fusion.fusionner", pont.SIMULATEUR, bascule, None),
        "maximum": ("fusion.fusionner", pont.SIMULATEUR, bascule, "le_plus_eleve"),
    })
    modele = lus["modele"]
    assert (modele["age_ouverture"], modele["age_taux_plein"]) == (65.0, 67.0)
    assert modele["duree_requise_trimestres"] == 172
    assert isinstance(modele["duree_requise_trimestres"], int)
    assert round(modele["taux_cotisation_retraite"] * 100, 2) == 25.83
    assert modele["taux_cotisation_salarie"] < modele["taux_cotisation_retraite"]
    assert lus["maximum"]["taux_cotisation_retraite"] > modele["taux_cotisation_retraite"]


def test_le_pont_rend_le_taux_de_la_tranche_1_d_un_regime():
    """La tranche 1 d'un régime, cotisation déplafonnée comprise, comme la
    fusion la compte : la retenue pour pension d'un fonctionnaire de l'État
    est de 11,10 % en 2023 ; un régime sans période active est refusé."""
    lus = _rendu({"etat": ("fusion.taux_total.tranche_1", pont.SIMULATEUR,
                           "fonction_publique_etat", 2023)})
    assert round(lus["etat"] * 100, 2) == 11.10
    _, refus = droit_et_refait({"avant": ("fusion.taux_total.tranche_1", pont.SIMULATEUR,
                                          "agirc_arrco", 1900)})
    assert "période active" in refus["avant"]


# -- une carrière bâtie et simulée ----------------------------------------------------

#: L'exemple du § 3 du README, aux options de ``carriere_simple`` : une
#: fonctionnaire de l'État née en 1975, vingt pour cent de primes, partie à
#: soixante-quatre ans.
FONCTIONNAIRE = pont.CarriereSimple({
    "annee_naissance": 1975, "sexe": "F", "affiliation": "fonctionnaire_etat",
    "age_debut": 22, "age_liquidation": 64, "part_primes": 0.2,
    "profil_carriere": "ascendant"})


def test_le_pont_rend_la_simulation_d_une_carriere_d_un_seul_statut():
    """La carrière que le portage bâtit des options de ``carriere_simple``,
    simulée sous les paramètres de la demande : son résultat, tel que les
    témoins l'écrivent (``Comparaison.dictionnaire()``), relu sous la table
    des types ; et ce que les sondes lisent en plus — le diviseur de chaque
    scénario, la fiche de paie de l'année de référence sous le droit en
    vigueur et sous la proposition. L'exemple du README : la proposition lui
    retire 5,4 % de sa pension, et ajoute 25,5 % à son net d'aujourd'hui."""
    lus = _rendu({"a": ("simulateur.simuler", pont.SIMULATEUR, FONCTIONNAIRE)})
    resultat, remuneration = lus["a"]["resultat"], lus["a"]["remuneration"]
    assert resultat["assure"]["annee_naissance"] == 1975
    assert resultat["assure"]["affiliations"] == ["fonctionnaire_etat"]
    liberal = resultat["scenarios"]["notionnel_liberal"]
    assert round(liberal["variation_vs_actuel"] * 100, 1) == -5.4
    # Le scénario 2 part avec l'étalon : son écart est le rapport des deux pensions.
    retroactif = resultat["scenarios"]["notionnel_retroactif"]
    assert retroactif["variation_vs_actuel"] == (
        retroactif["pension_annuelle"] / resultat["scenarios"]["actuel"]["pension_annuelle"] - 1.0)
    assert set(lus["a"]["diviseurs"]) == set(resultat["scenarios"]) - {"actuel"}
    assert lus["a"]["diviseurs"]["notionnel_retroactif"] == resultat["conversion"]["diviseur"]
    droit_en_vigueur = remuneration["droit_en_vigueur"]
    assert round(remuneration["gain_net"] / droit_en_vigueur["net"] * 100, 1) == 25.5
    assert remuneration["gain_net"] == remuneration["proposition"]["net"] - droit_en_vigueur["net"]
    assert droit_en_vigueur["retraite_salarie"] > 0 and droit_en_vigueur["retraite_employeur"] > 0
    assert droit_en_vigueur["net"] < droit_en_vigueur["brut"]
    assert remuneration["indemnite_csg_mensuelle"] > 0


def test_le_pont_rend_une_simulation_sans_fiche_de_paie_pour_qui_a_liquide():
    """Qui a déjà liquidé ne cotise plus : sa simulation ne porte aucune fiche
    de paie, et porte ce que le système actuel lui sert aujourd'hui."""
    retraite = pont.CarriereSimple({
        "annee_naissance": 1950, "sexe": "H", "affiliation": "salarie_prive_non_cadre",
        "age_debut": 20, "age_liquidation": 62})
    lus = _rendu({"a": ("simulateur.simuler", pont.SIMULATEUR, retraite)})
    assert lus["a"]["remuneration"] is None
    assert lus["a"]["resultat"]["aujourd_hui"]["actuel"]["pension_annuelle"] > 0


def test_le_pont_rend_la_garantie_vieillesse_d_une_pension():
    """Le tableau de la proposition : à qui a 300 € de pension par mois, la
    garantie sert 500 € en couple, où chacun a son plancher de 800 €, et
    750 € à une personne seule, dont le plancher est de 1 050 € — sur une
    liquidation de l'année des euros de la garantie, à soixante-six ans."""
    parametres = Parametres()
    carriere = pont.CarriereSimple({
        "annee_naissance": parametres.annee_euros_garantie_vieillesse - 66, "sexe": "H",
        "affiliation": "salarie_prive_non_cadre", "age_debut": 20, "age_liquidation": 66})
    for situation, plancher, complement in (("couple", 800.0, 500.0), ("seul", 1050.0, 750.0)):
        lus = _rendu({"a": ("notionnel.garantie_vieillesse", pont.SIMULATEUR, carriere,
                            300 * 12.0)},
                     replace(parametres, situation_foyer=SituationFoyer(situation)))
        assert lus["a"] == {"plancher_annuel": plancher * 12, "complement": complement * 12}


def test_le_pont_rend_le_pilier_capitalise_sous_une_autre_allocation():
    """Le pilier de la carrière témoin — une assiette de 30 000 € par an à
    partir de 2030, née en 1996, partie à 64 ans en 2060 — sous la prime de
    terme du milieu de la fourchette : 31 années de versement. La règle du
    moteur adosse chaque versement à son horizon ; une autre allocation se
    décrit en données, par horizon, ses maturités et leurs poids — le moteur
    n'en porte qu'une, et aucune de ses fonctions ne se remplace. Contre un
    placement à un an renouvelé jusqu'au départ, l'adossement rapporte 6,2 %
    de capital de plus (méthodologie)."""
    parametres = replace(Parametres(), prime_terme_trente_ans=PRIME_TERME_MILIEU)
    assiettes = {annee: 30_000.0 for annee in range(2030, 2066)}
    roulement = {horizon: [[1, 1.0]] for horizon in range(1, 31)}
    lus = _rendu({
        "adosse": ("capitalisation.construire", pont.SIMULATEUR, assiettes, 1996, 64.0, 2060,
                   None),
        "roule": ("capitalisation.construire", pont.SIMULATEUR, assiettes, 1996, 64.0, 2060,
                  roulement),
    }, parametres)
    assert lus["adosse"]["annees_cotisees"] == 31
    assert isinstance(lus["adosse"]["annees_cotisees"], int)
    assert round((lus["adosse"]["capital"] / lus["roule"]["capital"] - 1) * 100, 1) == 6.2
    assert lus["adosse"]["rente_mensuelle"] > lus["roule"]["rente_mensuelle"] > 0


# -- les sondes sous le relevé ------------------------------------------------------

#: Les sondes de la prose qui appelaient une règle du moteur Python, chacune
#: sous des réglages que la prose cite : aucune n'y entre plus.
SONDES = (
    "age_reference?annee=1990&depart=50",
    "anticipation?avance=5&annee=2026&carriere=42",
    "anticipation?avance=5&annee=2026&quoi=esperance",
    "cumul_indexation?regle=pib_nominal&de=1940&a=2025",
    "conserve?regle=moyenne_trois_taux",
    "fois_prix?regle=masse_salariale",
    "taux_indexation?regle=prix&annee=1981",
    "composition_revalorisation?de=1940&a=2025",
    "ecart_openfisca",
    "frais_reserve?age=64&annee=2040",
    "salaire_moyen?annee=2024",
    "smic_annuel?annee=1970&en=multiple",
    "millieme_salaire",
    "restitution?quoi=part_du_poste&annee=2024",
    "restitution?quoi=points_csg&annee=2026",
    "retraite_seule",
    "retraite_seule?annee=2020",
    "retraite_seule?militaire=1",
    "fusion?champ=taux_cotisation_retraite",
    "fusion?champ=duree_requise_trimestres",
    "fusion?champ=taux_cotisation_retraite&critere=le_plus_eleve",
    "fusion?pivot=regime_general",
    "taux_statut?regimes=regime_general|agirc_arrco&annee=2023",
    "ecart?scenario=2&generation=1930",
    "ecart?exemple=fonctionnaire&scenario=6&contribution_etat=entiere",
    "pension?exemple=fonctionnaire&scenario=6&part=obligatoire",
    "pension?exemple=fonctionnaire&scenario=6&part=volontaire",
    "aujourd_hui?generation=1950&niveau=0.8",
    "part_employeur?exemple=fonctionnaire",
    "part_salariale_versee?exemple=litterature_prive",
    "gain_net?exemple=fonctionnaire",
    "gain_net?exemple=smic&en=mensuel",
    "fiche?exemple=salaire_moyen&quoi=total",
    "fiche?exemple=salaire_moyen&quoi=salarie&systeme=proposition",
    "indemnite_csg?exemple=fonctionnaire",
    "avance?exemple=sncf",
    "droits_acquis?generation=1975&debut=21&depart=62&quoi=diviseur_service",
    "droits_acquis?generation=1975&debut=21&depart=60&conversion=liquidation&quoi=pot",
    "droits_acquis_variation?generation=1975&debut=21&quoi=capital&de=60&a=67",
    "fourchette?generation=2000&depart=64&debut=21&quoi=amplitude",
    "fourchette?generation=2000&depart=64&debut=21&quoi=annees",
    "garantie_complement?pension=900",
    "garantie_foyer?pension=300&conjoint=1500",
    "garantie_foyer?personnes=1&quoi=plancher",
    "allocation?contre=echelle",
    "allocation?contre=roule",
    "allocation?contre=echelle&quoi=rente",
    "allocation?quoi=annees",
)

def _entrees_des_sondes(tmp_path, sondes) -> dict[str, list[str]]:
    """Ce qui entre dans le moteur Python quand ces sondes tournent, chacune
    une fois, dans un processus neuf (``entrees_du_moteur.relever``)."""
    script = tmp_path / "sondes.py"
    script.write_text(textwrap.dedent(f'''\
        import sys
        sys.path.insert(0, {str(RACINE / "scripts")!r})
        import mesures_prose

        for sonde in {list(sondes)!r}:
            mesures_prose.mesurer(sonde)
        '''), encoding="utf-8")
    return entrees_du_moteur.relever(script)


def test_les_sondes_n_entrent_plus_dans_le_moteur_python(tmp_path):
    """Chaque sonde de la prose qui appelait une règle du moteur Python — une
    carrière bâtie et simulée, ou une règle appelée seule — la demande au
    portage : le relevé de ses entrées est vide, les règles des fichiers
    mêlés que les sondes appelaient comprises (``entrees_du_moteur.PORTES``)."""
    assert _entrees_des_sondes(tmp_path, SONDES) == {}


# -- les mesures de l'accueil --------------------------------------------------------


def test_les_baremes_de_la_fusion_se_lisent_sans_le_moteur_python(tmp_path):
    """Les quatre barèmes que le solde de la fusion compare
    (``solde_fusion.hypotheses``, d'où l'accueil tire le taux du régime
    unique) : le régime unique du modèle et la moyenne des régimes s'y
    demandent au portage, sous les conventions du simulateur reçu, et rien
    n'entre plus dans le moteur Python. Le modèle retient le taux du statut
    pivot du privé : 25,83 % au taux contractuel de l'Agirc-Arrco, et
    davantage sous les conventions de la page Coût, où elle cotise au taux
    moyen des entreprises ; la moyenne de tous les régimes est plus basse."""
    script = tmp_path / "baremes.py"
    script.write_text(textwrap.dedent(f'''\
        import json
        import sys
        sys.path.insert(0, {str(RACINE / "scripts")!r})
        import solde_fusion
        from retraite_notionnelle.config import Parametres
        from retraite_notionnelle.simulateur import Simulateur

        simulateur = Simulateur(Parametres())
        lus = {{}}
        for nom, sous in (("contractuel", simulateur), ("cout", simulateur.pour_la_projection())):
            toutes = solde_fusion.hypotheses(sous, 2026)
            lus[nom] = {{lettre: [h.libelle, h.bareme] for lettre, h in toutes.items()}}
        json.dump(lus, open({str(tmp_path / "baremes.json")!r}, "w"))
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script) == {}
    import json

    lus = json.loads((tmp_path / "baremes.json").read_text())
    assert "25.83%" in lus["contractuel"]["A"][0] and lus["contractuel"]["A"][1] is None
    assert "26.35%" in lus["cout"]["A"][0]
    (plafond, taux, salarie), = lus["cout"]["D"][1]
    assert plafond is None and 0 < salarie < taux < 0.2583
