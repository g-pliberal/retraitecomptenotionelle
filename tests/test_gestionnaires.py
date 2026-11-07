"""Le gestionnaire de chaque régime : la caisse, le service ou le fonds qui le gère.

Le 7 novembre 2026, le propriétaire le demande (action 188) : l'inventaire
nommait chaque régime, mais aucun fichier ne disait quel organisme le gère, et
le dépôt ne savait ni compter les caisses, ni dire laquelle gère quoi. Chaque
ligne d'inventaire porte désormais son `gestionnaire` — un code, ou plusieurs —
du référentiel `data/reference/regimes/_gestionnaires.yaml` : l'organisme qui
gère le régime aujourd'hui, ou le dernier qui l'a géré en propre, quand le
régime s'est éteint ou fondu dans un autre (`integre_dans` dit alors qui en
sert les droits). L'organisme qui en confie la gestion à un autre le dit par
son `operateur` : la Caisse des dépôts gère ainsi la CNRACL ou l'Ircantec.
"""

from __future__ import annotations

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.regimes import charger_gestionnaires, charger_inventaire

#: Les régimes dont aucune source du dépôt ne nomme l'organisme qui les gère,
#: déclarés un à un : aucun autre ne s'en dispense en silence.
A_IDENTIFIER = {
    "avts": "l'allocation de 1941 : ni la fiche ni ses textes ne disent qui la versait",
    "enseignants_prive_additionnel": (
        "la fiche dit qui cotise, l'État et les maîtres, pas qui gère ; le "
        "décret de 2005 qui organise le régime n'est pas lu"),
    "seita": (
        "la fiche dit que l'État le finance (programme 195), pas qui sert les "
        "pensions depuis la privatisation de 1995"),
}

#: Ce que les sources du dépôt disent de qui gère quoi : chaque régime, et
#: l'organisme qui le gère ou pour qui il est géré, sous la phrase qui le dit.
LUS_AUX_SOURCES = {
    # `data/sources.yaml`, jeu `cdc_ircantec_baremes` : deux CSV « publiés par
    # le gestionnaire du régime », la Caisse des dépôts.
    "ircantec": "caisse_des_depots",
    # Jeu `cdc_mines_baremes` : « Trois tableaux en PDF du gestionnaire du
    # régime », sur le site de la Caisse des dépôts.
    "mines": "caisse_des_depots",
    # La « carte des régimes, fonds et mandats gérés par la direction des
    # politiques sociales » de la Caisse des dépôts (février 2026), que ces
    # trois fiches citent.
    "atc_icna": "caisse_des_depots",
    "sudac": "caisse_des_depots",
    "elus_locaux_avant_1992": "caisse_des_depots",
    # Les fiches elles-mêmes.
    "gerants_debits_tabac": "caisse_des_depots",  # « géré par la Caisse des dépôts »
    "canssm_personnel": "caisse_des_depots",  # « la Caisse des dépôts, qui gère le régime »
    "crcgmf": "caisse_des_depots",  # « gérée par la Caisse des dépôts »
    "cnrv": "caisse_des_depots",  # « gérée par la Caisse des dépôts »
    "fspoeie": "caisse_des_depots",  # « un fonds distinct géré par la Caisse des dépôts »
    "cantonniers_etat": "caisse_des_depots",  # « fonds spéciaux que la Caisse des dépôts gère »
    "msa_salaries": "msa",  # « une gestion distincte confiée à la Mutualité sociale agricole »
    "cavimac": "cavimac",  # « géré par la CAMAVIC puis, depuis 1998, par la CAVIMAC »
    "cafat_nouvelle_caledonie": "cafat",  # « régime d'assurance vieillesse de base géré par la CAFAT »
    "ircec_raap": "ircec",  # « (RAAP), géré par l'IRCEC »
    "cnavpl": "cnavpl",  # « La caisse gère pour le compte de la CNAVPL le régime de base »
    "regies_ferroviaires_outre_mer": "etat",  # « gérés par l'État depuis 1993 »
    "ortf": "etat",  # « Régime en extinction dont l'État verse les derniers engagements »
    "cultes_alsace_moselle": "etat",  # « leur pension, servie par l'État »
    "retrep": "etat",  # « des avantages temporaires de retraite que l'État paie »
    "assemblees_parlementaires": "caisses_des_assemblees",  # « servie par la caisse de chaque assemblée »
    "fonctionnaires_pacifique": "clr_nouvelle_caledonie",  # « la fiche est celle de la Caisse locale de retraites »
    "wallis_et_futuna": "cps_wallis_et_futuna",  # « affiliés à la Caisse des prestations sociales »
    "cci_roubaix": "caisse_cci_roubaix",  # « servi par la caisse de retraites des employés de la chambre »
    "compagnie_generale_eaux": "caisse_compagnie_generale_eaux",  # « servi par la caisse de retraites de la compagnie »
}


def _organismes_de(ligne, organismes) -> set[str]:
    """Les organismes qui gèrent la ligne, et ceux qui les gèrent pour eux."""
    return set(ligne.gestionnaires) | {
        organismes[code].operateur for code in ligne.gestionnaires
        if code in organismes and organismes[code].operateur}


def test_chaque_regime_nomme_l_organisme_qui_le_gere():
    organismes = charger_gestionnaires(RACINE_DONNEES)
    inventaire = charger_inventaire(RACINE_DONNEES)
    assert {ligne.code for ligne in inventaire if not ligne.gestionnaires} == set(A_IDENTIFIER)
    inconnus = sorted((ligne.code, code) for ligne in inventaire
                      for code in ligne.gestionnaires if code not in organismes)
    assert inconnus == []


def test_chaque_organisme_du_referentiel_gere_un_regime():
    """Un organisme gère un régime au moins, ou en gère un pour un autre ; celui
    à qui il confie sa gestion est au référentiel, et ne la confie à personne."""
    organismes = charger_gestionnaires(RACINE_DONNEES)
    inventaire = charger_inventaire(RACINE_DONNEES)
    employes = {code for ligne in inventaire for code in ligne.gestionnaires}
    operateurs = {o.operateur for o in organismes.values() if o.operateur}
    assert sorted(set(organismes) - employes - operateurs) == []
    for code, organisme in organismes.items():
        assert organisme.nom.strip(), code
        if organisme.operateur:
            assert organisme.operateur in organismes, code
            assert organisme.operateur != code
            assert organismes[organisme.operateur].operateur is None, code


def test_les_gestionnaires_sont_ceux_que_les_sources_nomment():
    organismes = charger_gestionnaires(RACINE_DONNEES)
    par_code = {ligne.code: ligne for ligne in charger_inventaire(RACINE_DONNEES)}
    ecarts = {code: sorted(_organismes_de(par_code[code], organismes))
              for code, attendu in LUS_AUX_SOURCES.items()
              if attendu not in _organismes_de(par_code[code], organismes)}
    assert ecarts == {}


def test_le_document_des_regimes_compte_les_gestionnaires_et_les_nomme():
    """`docs/regimes.md` dit combien d'organismes gèrent les régimes encore en
    vie — ni éteints, ni fondus dans un autre — et les nomme chacun."""
    from pathlib import Path

    organismes = charger_gestionnaires(RACINE_DONNEES)
    vivantes = [ligne for ligne in charger_inventaire(RACINE_DONNEES)
                if ligne.extinction is None and ligne.integre_dans is None]
    actifs = {code for ligne in vivantes for code in ligne.gestionnaires}
    texte = (Path(__file__).resolve().parents[1] / "docs" / "regimes.md").read_text(encoding="utf-8")
    assert "<!-- gestionnaires:debut -->" in texte
    bloc = texte.split("<!-- gestionnaires:debut -->", 1)[1].split("<!-- gestionnaires:fin -->", 1)[0]
    assert f"**{len(actifs)} gestionnaires**" in bloc
    assert f"les {len(vivantes)} lignes" in bloc
    assert [organismes[code].nom for code in sorted(actifs)
            if organismes[code].nom not in bloc] == []


def test_un_regime_integre_garde_le_gestionnaire_qu_il_avait():
    """CANCAVA et ORGANIC ont géré les régimes des artisans et des commerçants
    jusqu'au RSI de 2006 ; leurs droits sont servis aujourd'hui par la Cnav,
    ce que la chaîne des intégrations dit, et non leur gestionnaire."""
    par_code = {ligne.code: ligne for ligne in charger_inventaire(RACINE_DONNEES)}
    assert par_code["cancava"].gestionnaires == ("cancava",)
    assert par_code["organic"].gestionnaires == ("organic",)
    assert par_code["rsi"].gestionnaires == ("rsi",)
    assert par_code["regime_general"].gestionnaires == ("cnav",)
