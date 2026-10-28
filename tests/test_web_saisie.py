"""Tests de la saisie du site : ce que l'adresse et le formulaire acceptent
ou refusent, dans les deux unités de revenu, par la pension, par le relevé,
métier par métier.

Détachés de ``test_web.py`` le 30 septembre 2026, pour qu'une retouche de la
saisie se vérifie seule ; ce qu'ils partagent avec lui est dans
``outils_web.py``. La saisie est celle du portage, la seule que le site lit
(action 161, étape 6) : ce qui l'éprouve elle-même la lit par ``site()`` ;
ce qui éprouve une règle du moteur par une saisie simule au moteur Python la
carrière que le pont bâtit (``outils_pont``).
"""

from __future__ import annotations

import html
import re
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle import chronologie
from retraite_notionnelle.carriere import Affiliations
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.chargement import charger_periodes_non_travaillees
from retraite_notionnelle.web.site import ErreurSite, disponible, module, rendre, site
from outils_pont import refus_de_la_saisie, saisie_du_portage
from outils_web import (
    _echelle, _prose, contexte, montants_du_portage, page, pages, saisies,
)


#: Le site, en JavaScript : ses pages et ses modules se lisent par node
#: (``web/site.py``), le Python ne les rendant plus depuis la phase 8. Sans
#: node, rien du site ne se lit, et ses tests sont sautés.
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le site ne se lit pas sans lui")
#: La saisie du portage : ses bornes, ses menus, sa classe.
SAISIE = module("saisie")
#: Toute saisie qu'un refus du portage arrête, quel que soit son motif.
REFUSEE = refus_de_la_saisie("")


# -- saisie ------------------------------------------------------------------


def test_saisie_par_defaut_est_valide():
    SAISIE.Saisie().verifier()


@pytest.mark.parametrize("champs", [
    {"naissance": "1700"},
    {"debut": "12"},
    {"liquidation": "120"},
    {"naissance": "1980", "debut": "30", "liquidation": "25"},
    {"salaire": "50"},
])
def test_saisies_refusees(champs):
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage(champs)


@pytest.mark.parametrize("champ", ["bascule", "euros"])
@pytest.mark.parametrize("valeur", ["1800", "9999", "-5", "0"])
def test_les_annees_hors_bornes_sont_refusees(champ, valeur):
    """Une adresse forgée à la main ne doit pas franchir les bornes du champ.

    Elles n'existaient que sur le formulaire, donc opposables au navigateur
    seulement. « ?euros=9999 » traversait toute la chaîne sans erreur et
    faisait afficher des pensions à soixante chiffres, l'année des euros
    servant d'exposant à l'inflation cumulée.
    """
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage({champ: valeur})


@pytest.mark.parametrize("champ", ["bascule", "euros"])
def test_les_annees_aux_bornes_sont_acceptees(champ):
    for valeur in (SAISIE.ANNEE_MINIMALE, SAISIE.ANNEE_MAXIMALE):
        assert getattr(
            saisie_du_portage({champ: str(valeur)}), champ
        ) == valeur


def test_le_nombre_d_enfants_reste_borne():
    """Les majorations du scénario 1 en dépendent : le champ n'était borné que
    dans le formulaire, et « ?enfants=999 » gonflait la pension de référence."""
    assert saisie_du_portage(
        {"enfants": str(SAISIE.ENFANTS_MAXIMUM)}
    ).enfants == SAISIE.ENFANTS_MAXIMUM
    for refuse in ("-1", str(SAISIE.ENFANTS_MAXIMUM + 1), "999"):
        with pytest.raises(ErreurSite, match=REFUSEE):
            saisie_du_portage({"enfants": refuse})


#: Une mère de trois enfants, dont deux ont leur naissance dite, et ce qui
#: prolonge leur charge (action 138, étape 4), séparé comme on l'écrit.
_CHARGE = {"naissance": "1960", "sexe": "F", "enfants": "3", "naissances": "1990-03, 1993",
           "charge_enfants": " 1:etudes:2009-07 ; 2:Apprentissage:2012-09, 2:infirmité "}


def test_la_saisie_dit_l_enfant_etudiant_apprenti_ou_infirme_et_jusqu_a_quand(saisies):
    """L'enfant étudiant, apprenti ou infirme reste à charge jusqu'à vingt ans
    (R. 313-12, R. 161-4) : le champ « charge_enfants » dit, pour chaque enfant
    dont la naissance est dite, son rang, son motif — etudes, apprentissage ou
    infirmite, écrit avec ses accents ou sans — et le mois où ses études ou
    son apprentissage cessent, s'il le dit. La carrière que le portage bâtit en
    porte les faits, que le modèle lit (``prolongations_de_la_charge``) ;
    l'adresse et le formulaire le gardent tel qu'il est écrit."""
    carriere = saisies.carriere(_CHARGE)
    assert [chronologie.prolongations_de_la_charge(carriere.chronologie, enfant)
            for enfant in ("enfant_1", "enfant_2", "enfant_3")] == [
        [("1990-03-01", "2009-07-01")],
        [("1993-01-01", "2012-09-01"), ("1993-01-01", None)], []]
    ecrit = _CHARGE["charge_enfants"].strip()
    assert dict(parse_qsl(saisie_du_portage(_CHARGE).requete()))["charge_enfants"] == ecrit
    sans = {cle: valeur for cle, valeur in _CHARGE.items() if cle != "charge_enfants"}
    assert "charge_enfants" not in dict(parse_qsl(saisie_du_portage(sans).requete()))
    assert chronologie.prolongations_de_la_charge(
        saisies.carriere(sans).chronologie, "enfant_1") == []
    champ = re.search(r'<input[^>]*name="charge_enfants"[^>]*>', rendre("/simuler", _CHARGE)[1])
    assert champ, "le formulaire ne demande pas la charge des enfants"
    assert f'value="{html.escape(ecrit)}"' in champ.group(0)


@pytest.mark.parametrize("charge, motif", [
    ("1-etudes", "« 1-etudes » : attendu en rang:motif ou rang:motif:fin, par exemple "
                 "1:etudes:2009-07."),
    ("1:etudes:2009:07", "« 1:etudes:2009:07 » : attendu en rang:motif ou rang:motif:fin"),
    ("0:etudes", "« 0:etudes » : vous déclarez 3 enfants."),
    ("4:infirmite", "« 4:infirmite » : vous déclarez 3 enfants."),
    ("3:etudes", "« 3:etudes » : dites d'abord sa naissance, dans « Naissance des enfants »."),
    ("1:chomage", "« 1:chomage » : son motif est etudes, apprentissage ou infirmite."),
    ("2:infirmite:2010", "« 2:infirmite:2010 » : l'infirmité ne finit pas ; seules les études "
                         "et l'apprentissage se datent."),
    ("1:etudes:2009-13", "« 1:etudes:2009-13 » : sa fin attendue en AAAA, AAAA-MM ou "
                         "AAAA-MM-JJ, par exemple 2009-07."),
    ("1:etudes:1990-03", "« 1:etudes:1990-03 » : elle finit avant sa naissance."),
    ("1:etudes:2009-07, 1:études", "« 1:études » : ce motif est déjà dit pour l'enfant n° 1."),
])
def test_une_charge_d_enfant_mal_dite_est_refusee(charge, motif):
    """Chaque entrée du champ se refuse avec ce qui ne va pas : sa forme, un
    rang hors des enfants déclarés, un enfant sans naissance dite, un motif
    inconnu, une infirmité datée, une fin illisible ou qui précède la
    naissance, un motif dit deux fois pour le même enfant."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(
            re.escape(f"Enfant aux études, apprenti ou infirme {motif}"))):
        saisie_du_portage({**_CHARGE, "charge_enfants": charge})


def test_toute_borne_du_formulaire_est_opposable_hors_du_navigateur():
    """Aucun champ numérique ne doit être borné dans le seul HTML.

    Le formulaire porte des attributs « min » et « max » ; le navigateur les
    respecte, une adresse partagée non. Ce test relit le formulaire rendu et
    vérifie que chaque borne déclarée est bien refusée par le modèle.
    """
    formulaire = rendre("/simuler", {})[1]
    champs = re.findall(
        r'<input type="number" id="([a-z_0-9]+)" name="[^"]*" value="[^"]*"'
        r'(?: min="(-?[0-9.]+)")?(?: max="(-?[0-9.]+)")?',
        formulaire,
    )
    assert champs, "le formulaire ne déclare plus aucun champ numérique"
    for nom, minimum, maximum in champs:
        for borne, pas in ((minimum, -1), (maximum, +1)):
            if not borne:
                continue
            dehors = float(borne) + pas
            valeur = str(int(dehors)) if float(borne).is_integer() else str(dehors)
            with pytest.raises(ErreurSite, match=refus_de_la_saisie(".")):
                saisie_du_portage({nom: valeur})


def test_les_bornes_des_calendriers_sont_opposables_hors_du_navigateur():
    """Même exigence pour les dates que pour les nombres.

    Un calendrier s'ouvre sur les seules dates que le modèle accepte — « min »
    et « max » sont posés depuis la date de naissance saisie —, mais une adresse
    forgée à la main ne passe par aucun calendrier. Ce test relit les champs
    date du formulaire rendu et vérifie que le mois d'à côté est refusé.
    """
    formulaire = rendre("/simuler", {})[1]
    champs = re.findall(
        r'<input type="date" id="([a-z_0-9]+)"[^>]*?'
        r' min="(\d{4}-\d{2})-\d{2}" max="(\d{4}-\d{2})-\d{2}"',
        formulaire,
    )
    assert champs, "le formulaire ne déclare plus aucun calendrier"
    for nom, minimum, maximum in champs:
        for borne, pas in ((minimum, -1), (maximum, +1)):
            annee, mois = (int(part) for part in borne.split("-"))
            rang = annee * 12 + mois - 1 + pas
            dehors = f"{rang // 12:04d}-{rang % 12 + 1:02d}"
            # Une ligne de métier ne se lit qu'entière : sans statut, elle est
            # refusée pour cette raison-là, et ne dirait rien de sa borne.
            requete = {nom: dehors}
            if nom.startswith("metier"):
                requete[f"{nom.split('_')[0]}_statut"] = "artisan"
            with pytest.raises(ErreurSite, match=refus_de_la_saisie(".")):
                saisie_du_portage(requete)


def test_le_depart_le_plus_tardif_se_convertit_encore_en_rente():
    """La saisie accepte un départ jusqu'au dernier âge entier que les tables de
    mortalité convertissent en rente (action 151). À cet âge, pour la
    génération la plus ancienne comme pour la plus jeune, le diviseur du compte
    notionnel est encore positif ; un an plus tard, à l'âge terminal des
    tables, il est nul, et le moteur refuse de diviser."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.moteur.conversion import Convertisseur
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    convertisseur = Convertisseur(simulateur.mortalite, simulateur.parametres)
    maximal = SAISIE.AGE_LIQUIDATION_MAXIMAL
    for naissance in (SAISIE.NAISSANCE_MINIMALE, SAISIE.NAISSANCE_MAXIMALE):
        depart = naissance + maximal
        assert convertisseur.coefficient(maximal, depart).diviseur > 0
        with pytest.raises(ValueError, match="diviseur nul"):
            convertisseur.coefficient(maximal + 1, depart + 1)


def test_le_site_simule_le_depart_le_plus_tardif(page):
    """Né en janvier 2020 et parti au dernier âge que la saisie accepte : la
    carrière court jusqu'en 2139, au-delà de toutes les projections, et le
    site la calcule comme une autre (action 151)."""
    naissance, maximal = SAISIE.NAISSANCE_MAXIMALE, SAISIE.AGE_LIQUIDATION_MAXIMAL
    depart = f"{naissance + maximal}-02"
    texte = page("/simuler", naissance=f"{naissance}-01-15",
                 debut=f"{naissance + 22}-09", liquidation=depart)
    assert "Saisie refusée" not in texte
    assert f"à {maximal} ans" in texte


def test_la_page_dit_la_limite_d_age_et_ses_exceptions_presumees(page):
    """Le départ saisi passe la limite d'âge (``droit/limite_age.js``, action
    151) : la page dit à quel âge l'emploi prend fin, dans les mots de son
    statut, la limite, et chaque exception, de droit ou présumée demandée et
    accordée ; puis que ce qui suit peut être un métier de plus."""
    def lire(naissance=1975, **parametres):
        return re.sub(r"\s+", " ", page("/simuler", naissance=naissance, debut=21, **parametres))

    texte = lire(statut="fonctionnaire_etat", liquidation=75, enfants=3)
    assert "Votre emploi a une limite d'âge, et votre départ la passe." in texte
    assert "La limite d'âge de votre emploi est de 67 ans." in texte
    assert "La loi la recule de droit : le recul d'un an du parent de trois enfants, " \
        "à 68 ans." in texte
    assert "Nous présumons que vous avez demandé et obtenu le maintien en fonctions " \
        "jusqu'à 70 ans" in texte
    assert "Ainsi la loi vous radie des cadres à 70 ans" in texte
    assert "déclarez-les comme un métier de plus" in texte
    texte = lire(statut="policier", liquidation=70)
    assert "la prolongation pour carrière incomplète jusqu'à 59 ans et 6 mois, puis la " \
        "prolongation de l'actif jusqu'à la limite des sédentaires, 67 ans" in texte
    texte = lire(statut="militaire_officier", liquidation=70)
    assert "la plus haute de votre catégorie : votre grade n'est pas saisi" in texte
    for statut, naissance, fin in (
            ("contractuel_public", 1975, "votre contrat prend fin à 70 ans"),
            ("agent_sncf", 1960, "vous êtes mis à la retraite à 70 ans")):
        assert f"Ainsi {fin}" in lire(naissance, statut=statut, liquidation=75)
    # Parti avant sa limite, rien n'en est dit.
    assert "La limite d'âge de votre emploi" not in lire(
        statut="fonctionnaire_etat", liquidation=64)


def test_la_page_dit_la_fin_de_l_emploi_dans_les_mots_de_chaque_statut(page):
    """À sa limite, l'agent des industries électriques et gazières « est mis
    en inactivité » (statut national, annexe, article 4, depuis 2008), et,
    avant le 28 novembre 2007, son « admission à la retraite est prononcée
    d'office » (décret n° 54-50, article 2) ; « la cessation des fonctions »
    du personnel de l'Opéra « est prononcée » (décret n° 2008-240, article 2) ;
    l'agent de la SEITA « est obligatoirement retraité » (décret n° 62-766,
    article 111) ; celui de la Banque de France doit « prendre [sa] retraite »
    (statut du personnel, article 241). Né en 1975, l'agent des IEG a pour
    limite soixante-sept ans, et le maintien jusqu'à soixante-dix ans, présumé ;
    né en 1945 et entré à vingt et un ans, il a ses vingt-cinq ans de services
    à cinquante-cinq ans, l'âge où l'actif ouvre son droit. Né en 1975, l'agent
    de l'Opéra a soixante-sept ans ; né en 1940, celui de la SEITA, soixante-cinq
    ans, sans exception ; né en 1960, celui de la Banque, soixante-sept ans
    (action 151, étapes 6, 8 et 9)."""
    for statut, naissance, depart, fin in (
            ("agent_ieg", 1975, 75, "vous êtes mis en inactivité à 70 ans"),
            ("agent_ieg", 1945, 68, "vous êtes admis d'office à la retraite à 55 ans"),
            ("personnel_opera", 1975, 75, "vos fonctions cessent à 67 ans"),
            ("agent_seita", 1940, 68, "vous êtes mis à la retraite à 65 ans"),
            ("agent_banque_de_france", 1960, 72, "vous devez prendre votre retraite à 67 ans")):
        texte = re.sub(r"\s+", " ", page("/simuler", naissance=naissance, debut=21,
                                         statut=statut, liquidation=depart))
        assert f"Ainsi {fin} : ce qui suit" in texte, (statut, naissance)


def test_les_adresses_d_avant_le_calendrier_valent_toujours():
    """Le formulaire demande des dates ; les adresses déjà partagées portaient
    des âges, en deux champs. Les deux doivent décrire la même carrière, et se
    réécrire de la même façon — sans quoi tout lien envoyé mentirait.
    L'ancienne ne disait pas le jour : il est présumé le 15, et le départ à
    64 ans et 7 mois tombe au 1er mai 2040, du mois qui suit l'anniversaire."""
    ancienne = saisie_du_portage({
        "naissance": "1975", "naissance_mois": "9",
        "debut": "22", "debut_mois": "3",
        "liquidation": "64", "liquidation_mois": "7",
    })
    nouvelle = saisie_du_portage({
        "naissance": "1975-09-15", "debut": "1997-12", "liquidation": "2040-05",
    })
    assert ancienne.requete() == nouvelle.requete()
    assert nouvelle.mois_de(nouvelle.debut) == "1997-12"
    assert nouvelle.mois_de(nouvelle.liquidation, depart=True) == "2040-05"
    # Et l'âge décimal d'avant les mois, que personne n'écrit plus mais que
    # certaines adresses portent encore.
    assert saisie_du_portage({"liquidation": "64.5"}).liquidation == 64.5


def test_un_metier_peut_commencer_le_mois_qui_precede_le_depart():
    """Né le 15 mars 1962, on a 64 ans et 3 mois révolus au 1er juillet 2026,
    et juin 2026 est encore travaillé : un métier qui y commence est accepté.
    Celui qui commence en juillet, au mois du départ, ne l'est pas. Les deux
    dates se comparent sur la même origine, celle du départ (R. 351-37)."""
    commun = {"naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
              "metier2_statut": "artisan"}
    saisie = saisie_du_portage({**commun, "metier2_debut": "2026-06"})
    assert saisie.mois_de(saisie.liquidation, depart=True) == "2026-07"
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage({**commun, "metier2_debut": "2026-07"})


def test_valeur_non_numerique_est_refusee_proprement():
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage({"naissance": "mille-neuf-cent"})


def test_virgule_decimale_acceptee():
    assert saisie_du_portage({"salaire": "1,5"}).salaire == 1.5


def test_la_fenetre_de_lissage_se_saisit_librement_mais_reste_bornee():
    """Fenêtre libre, et non plus un choix entre trois valeurs.

    La borne haute est un garde-fou de sens, pas une limite du moteur : au-delà
    d'une trentaine d'années la moyenne couvre presque toute une carrière.
    """
    for annees in (1, 2, 7, 17, SAISIE.LISSAGE_MAXIMUM):
        assert saisie_du_portage({"lissage": str(annees)}).lissage == annees
    assert saisie_du_portage({}).lissage == 1

    for refusee in ("0", "-3", str(SAISIE.LISSAGE_MAXIMUM + 1)):
        with pytest.raises(ErreurSite, match=REFUSEE):
            saisie_du_portage({"lissage": refusee})
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage({"lissage": "au jugé"})


def test_option_inconnue_retombe_sur_le_defaut():
    saisie = saisie_du_portage({"indexation": "au_doigt_mouille"})
    assert saisie.indexation == "masse_salariale"


def test_interruptions_analysees():
    saisie = SAISIE.Saisie({"interruptions": "1995:1997:education_enfant, 2001:2001:maladie"})
    plages = saisie.interruptions_analysees()
    assert plages[1995] == "education_enfant"
    assert plages[1997] == "education_enfant"
    assert plages[2001] == "maladie"
    assert 1998 not in plages


def test_interruption_mal_formee_est_refusee():
    with pytest.raises(ErreurSite, match=REFUSEE):
        SAISIE.Saisie({"interruptions": "1995-1997"}).interruptions_analysees()


@pytest.mark.parametrize("plage", [
    "0:999999999:chomage_indemnise",
    "1:2147483647:maladie",
    "1200:1300:maladie",
    "1990:{maximale_plus_un}:maladie",
    "{minimale_moins_un}:1990:maladie",
])
def test_une_plage_d_interruption_hors_de_toute_carriere_est_refusee(plage):
    """La boucle reprenait les deux années telles quelles.

    Le calcul se fait chez le lecteur et l'adresse EST la saisie :
    « ?interruptions=0:999999999:chomage_indemnise » remplissait la mémoire de
    l'onglet et le figeait — et le lien partagé figeait celui d'un autre. Aucune
    carrière ne sort de la fenêtre contrôlée ici, et le refus est immédiat.
    """
    plage = plage.format(maximale_plus_un=SAISIE.ANNEE_CARRIERE_MAXIMALE + 1,
                         minimale_moins_un=SAISIE.ANNEE_CARRIERE_MINIMALE - 1)
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("carrière possible")):
        SAISIE.Saisie({"interruptions": plage}).interruptions_analysees()


def test_une_plage_d_interruption_aux_bornes_reste_acceptee():
    minimale, maximale = SAISIE.ANNEE_CARRIERE_MINIMALE, SAISIE.ANNEE_CARRIERE_MAXIMALE
    plages = SAISIE.Saisie(
        {"interruptions": f"{minimale}:{maximale}:maladie"}
    ).interruptions_analysees()
    assert plages[minimale] == "maladie"
    assert plages[maximale] == "maladie"


def test_une_plage_d_interruption_a_l_envers_est_refusee():
    """« 2004:2003 » ne décrivait rien : la boucle ne tournait pas."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("avant de commencer")):
        SAISIE.Saisie({"interruptions": "2004:2003:maladie"}).interruptions_analysees()


def _motifs() -> list[str]:
    """Les motifs des périodes non travaillées des données, que la saisie du
    portage reçoit du paquet."""
    return list(charger_periodes_non_travaillees(Parametres().racine_donnees))


def test_un_motif_d_interruption_inconnu_est_refuse():
    """Une faute de frappe retombait sur « sans_activite », donc sur zéro
    trimestre au lieu de quatre : elle changeait la pension sans un mot."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("motif inconnu")):
        SAISIE.Saisie({"interruptions": "1998:2002:educaton_enfant"}) \
            .interruptions_analysees(_motifs())


def test_les_motifs_acceptes_sont_ceux_que_le_moteur_sait_traiter():
    """Ni plus — une liste écrite à la main aurait dérivé des données — ni
    moins : chaque motif du paquet doit rester saisissable."""
    motifs = _motifs()
    assert motifs, "le paquet ne porte plus aucune période non travaillée"
    for motif in motifs:
        plages = SAISIE.Saisie(
            {"interruptions": f"1998:1999:{motif}"}
        ).interruptions_analysees(motifs)
        assert plages[1998] == motif


def test_le_motif_n_est_controle_que_si_les_donnees_sont_fournies():
    """Une saisie ne connaît pas les données : sans elles, le motif passe."""
    assert SAISIE.Saisie({"interruptions": "1998:1999:peu_importe"}).interruptions_analysees()


@pytest.mark.parametrize("champ", ["naissance", "salaire", "primes", "euros"])
@pytest.mark.parametrize("valeur", ["nan", "inf", "-inf", "1e400", "1_975"])
def test_un_nombre_non_fini_ou_exotique_est_refuse(champ, valeur):
    """``float`` et ``Number`` ne lisent pas le même langage.

    « nan » et « 1_975 » sont des nombres pour Python, pas pour JavaScript :
    les deux lectures se seraient séparées sur une adresse forgée. « 1e400 »,
    lui, passe des deux côtés et vaut l'infini, que le calcul propage sans
    jamais échouer — le simulateur affichait « Ce revenu vaut inf fois le
    salaire moyen », et « ?naissance=inf » levait un OverflowError nu.
    """
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage({"unite_revenu": "euros_mois", champ: valeur})


# -- l'unité des revenus saisis ----------------------------------------------


def test_le_formulaire_vierge_demande_des_euros():
    """C'est la question qui revenait : personne ne connaît son salaire en ratio."""
    saisie = saisie_du_portage({})
    assert saisie.unite_revenu == "euros_mois"
    assert saisie.revenu_en_euros is True


def test_un_salaire_mensuel_devient_un_multiple():
    """2 500 € par mois contre 40 000 € annuels d'ancrage, à l'échelle de 2026."""
    # En brut : ce test mesure la conversion euros → multiple, et le mode
    # net y ajouterait la conversion net → brut, qui a son propre test.
    saisie = saisie_du_portage({"unite_revenu": "euros_mois",
                                "salaire": "2500", "montants": "brut"})
    echelle = _echelle()
    assert saisie.niveaux(echelle) == pytest.approx([2500 * 12 / echelle.moyen])
    assert saisie.parcours(echelle)[0].niveau_salaire == pytest.approx(
        saisie.niveaux(echelle)[0]
    )


def test_le_multiple_reste_disponible():
    saisie = saisie_du_portage({"unite_revenu": "moyen", "salaire": "1.4"})
    assert saisie.revenu_en_euros is False
    assert saisie.parcours(_echelle())[0].niveau_salaire == 1.4


def test_une_adresse_d_avant_les_euros_reste_lue_en_multiples():
    """Un « salaire » nu vaut un multiple : le lire en euros en ferait un euro."""
    saisie = saisie_du_portage({"naissance": "1975", "salaire": "1.4"})
    assert saisie.unite_revenu == "moyen"
    assert saisie.parcours(_echelle())[0].niveau_salaire == 1.4


def test_l_unite_s_ecrit_toujours_dans_l_adresse():
    """C'est ce qui distingue une adresse neuve d'une adresse d'avant les euros."""
    for unite in ("euros_mois", "moyen"):
        requete = saisie_du_portage({"unite_revenu": unite, "salaire": "1"}).requete()
        assert f"unite_revenu={unite}" in requete


def test_un_salaire_hors_bornes_est_refuse_en_euros():
    """Le refus doit dire quoi corriger, donc redire les bornes en euros."""
    saisie = saisie_du_portage({"unite_revenu": "euros_mois", "salaire": "200"})
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("bruts par mois")):
        saisie.parcours(_echelle())


def test_un_salaire_negatif_ou_nul_est_refuse():
    for montant in ("0", "-1500"):
        with pytest.raises(ErreurSite, match=REFUSEE):
            saisie_du_portage({"unite_revenu": "euros_mois", "salaire": montant})


def test_l_unite_vaut_pour_tous_les_metiers():
    echelle = _echelle()
    saisie = saisie_du_portage({
        "unite_revenu": "euros_mois", "salaire": "2500", "montants": "brut",
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "5000",
    })
    premier, second = saisie.niveaux(echelle)
    assert second == pytest.approx(2 * premier)


def _lien_de_bascule(parametres):
    """L'adresse que porte le lien « saisir plutôt … », lue comme une requête."""
    corps = rendre("/simuler", parametres)[1]
    # La bascule d'unité écrit ses deux états ; celui qui s'applique n'est pas
    # un lien. On cherche donc la branche PROPOSÉE, dans la bascule « Unité ».
    bloc = re.search(r'<div class="bascule" role="group" aria-label="Unité">'
                     r'.*?</div>', corps, re.S)
    assert bloc, "le formulaire ne porte plus de bascule d'unité"
    lien = re.search(r'<a href="\./#([^"]*)">([^<]*)</a>', bloc.group(0))
    assert lien, "la bascule d'unité ne propose aucun autre état"
    return dict(parse_qsl(html.unescape(lien.group(1)))), html.unescape(lien.group(2))


def test_la_bascule_d_unite_convertit_les_montants():
    """Le piège que ce lien existe pour éviter.

    Un menu HTML ne convertit rien : basculer l'unité sans retoucher le nombre
    aurait fait lire « 3 500 » comme 3 500 fois le salaire moyen, et la page
    aurait refusé la saisie au lieu de la traduire. Le lien, lui, porte les
    montants déjà convertis.
    """
    suite, libelle = _lien_de_bascule({"naissance": "1975", "montants": "brut"})
    assert libelle == "× salaire moyen"
    assert suite["unite_revenu"] == "moyen"
    # 3 500 € par mois, à l'échelle d'un salaire moyen de 3 475 € : environ 1.
    assert float(suite["salaire"]) == pytest.approx(1.0, abs=0.05)
    # Et la page qui suit ce lien calcule, au lieu de refuser.
    corps = rendre("/simuler", suite)[1]
    assert "Saisie refusée" not in corps


def test_la_bascule_revient_au_meme_revenu():
    """Aller et retour : de combien le revenu décrit peut-il bouger ?

    Pas de zéro : le multiple s'écrit au millième, et un millième de salaire
    moyen vaut environ trois euros cinquante par mois. L'écart est donc borné
    par un demi-pas, plus l'arrondi à l'euro — et cette borne est CALCULÉE
    depuis le pas du champ, pour qu'elle suive si le pas change un jour. Le
    balayage porte sur tout le domaine accepté : sur trois valeurs choisies, un
    aller-retour semble exact alors qu'il ne l'est pas. L'échelle est celle
    du portage, que la bascule applique ; ses deux conversions se gardent sous
    la main, chacune une demande à node.
    """
    echelle = site().contexte.echelle(SAISIE.Saisie())
    mensuel, niveau = echelle.mensuel, echelle.niveau
    borne = mensuel(pages.PAS_MULTIPLE) / 2 + 1

    def aller_retour(euros: int) -> int:
        return round(mensuel(round(niveau(euros), pages.DECIMALES_MULTIPLE)))

    plancher, plafond = round(mensuel(0.1)), round(mensuel(10))
    pire = max(abs(aller_retour(euros) - euros)
               for euros in range(plancher, plafond + 1))
    assert pire <= borne, f"{pire} € d'écart, au-delà des {borne:.2f} € admis"
    # Et l'ordre de grandeur, pour que la borne ne se relâche pas en silence.
    assert pire == 2


def test_la_bascule_ne_fait_jamais_sortir_des_bornes():
    """Un revenu accepté doit le rester une fois converti.

    Sinon le lien mènerait à une page qui refuse ce qu'elle affichait juste
    avant — l'arrondi peut faire franchir 0,1 ou 10 à un revenu qui les frôle.
    L'échelle est celle du portage, que la bascule applique.
    """
    echelle = site().contexte.echelle(SAISIE.Saisie())
    mensuel, niveau, dans_les_bornes = (echelle.mensuel, echelle.niveau,
                                        echelle.euros_dans_les_bornes)
    for euros in range(dans_les_bornes(0.1), dans_les_bornes(10) + 1):
        multiple = round(niveau(euros), pages.DECIMALES_MULTIPLE)
        assert 0.1 <= multiple <= 10, f"{euros} € donne {multiple}"
    # Vers les euros, la bascule prend l'euro le plus proche, sauf aux bords :
    # 0,1 fois le salaire moyen fait 355,34 € en 2026, et 355 € serait refusé.
    for millieme in range(100, 10001):
        euros = dans_les_bornes(millieme / 1000)
        assert abs(euros - mensuel(millieme / 1000)) < 1
        assert 0.1 <= niveau(euros) <= 10, f"{millieme / 1000} donne {euros} €"


def test_les_bornes_annoncees_par_le_refus_sont_acceptees():
    """Un message d'erreur ne doit pas nommer un montant qu'il refuserait.

    Il dit « de 348 à 34 754 € » : les deux valeurs sont arrondies, et un
    arrondi du mauvais côté nommerait une borne hors bornes.
    """
    # En brut : les bornes que le message nomme sont des bornes de BRUT,
    # puisque c'est l'unité du modèle. En net, le nombre saisi est converti
    # avant d'être borné, et le test porterait sur autre chose.
    echelle = _echelle()
    for borne in (echelle.euros_dans_les_bornes(0.1), echelle.euros_dans_les_bornes(10)):
        saisie = saisie_du_portage({
            "unite_revenu": "euros_mois", "salaire": str(borne),
            "montants": "brut",
        })
        saisie.parcours(echelle)  # ne doit pas lever


def test_la_bascule_convertit_tous_les_metiers():
    suite, _ = _lien_de_bascule({
        "naissance": "1975", "unite_revenu": "euros_mois", "salaire": "2900",
        "montants": "brut",
        "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "5800",
    })
    assert float(suite["metier2_salaire"]) == pytest.approx(
        2 * float(suite["salaire"]), rel=0.01
    )


def test_les_valeurs_du_lien_tombent_sur_le_pas_des_champs():
    """Un navigateur refuse de soumettre un nombre qui rate le pas déclaré.

    Le lien écrit des valeurs arrondies ; si le champ annonçait un pas plus
    grossier, la page d'arrivée serait impossible à valider.
    """
    for parametres in ({"naissance": "1975"},
                       {"naissance": "1975", "unite_revenu": "moyen", "salaire": "1.2"}):
        suite, _ = _lien_de_bascule(parametres)
        corps = rendre("/simuler", suite)[1]
        champ = re.search(r'id="salaire"[^>]*value="([^"]*)"[^>]*step="([^"]*)"', corps)
        valeur, pas = float(champ.group(1)), float(champ.group(2))
        assert round(valeur / pas) == pytest.approx(valeur / pas, abs=1e-9)


def test_le_formulaire_renvoie_l_unite_qu_il_affiche():
    """L'unité n'est plus un champ visible : le formulaire doit la porter caché.

    Sans cela, valider le formulaire après avoir suivi le lien de bascule
    retomberait dans l'unité par défaut, avec des nombres de l'autre.
    """
    for unite in ("euros_mois", "moyen"):
        salaire = "3500" if unite == "euros_mois" else "1"
        corps = rendre("/simuler", {"unite_revenu": unite, "salaire": salaire})[1]
        assert f'<input type="hidden" name="unite_revenu" value="{unite}">' in corps


def test_un_refus_garde_l_unite_de_saisie():
    """Une faute de frappe ailleurs ne doit pas changer d'unité sous les doigts."""
    corps = rendre("/simuler", {
        "naissance": "1700", "unite_revenu": "moyen", "salaire": "1.2",
    })[1]
    assert "Saisie refusée" in corps
    assert '<input type="hidden" name="unite_revenu" value="moyen">' in corps
    assert "Niveau de revenu" in corps


def test_le_formulaire_dit_brut_ou_net_et_donne_l_echelle():
    """La question posée — « brut ou net ? » — trouve sa réponse sur le champ.

    Et elle la trouve DANS LE MODE COURANT : demander un « revenu brut » sous
    une bascule qui annonce le net ferait taper l'un pour l'autre, et le modèle
    lirait sans broncher un net comme un brut. Les repères chiffrés suivent
    aussi — un SMIC net n'est pas un SMIC brut.
    """
    for mode, ligne in (("brut", "la ligne « brut » de la fiche de paie"),
                        ("net", "la ligne « net à payer avant impôt » de la fiche de paie")):
        _, corps = rendre("/simuler", {"montants": mode})
        assert f"Revenu d&#x27;activité {mode} mensuel" in corps
        assert ligne in corps
        # L'échelle est chiffrée : « 1 = salaire moyen » ne dit rien à personne.
        assert "SMIC" in corps and "salaire moyen" in corps
        # Et pas de « plafond » sous le champ : le mot s'y lit comme le maximum
        # que le champ accepte, ce que le plafond de la Sécurité sociale n'est pas.
        assert not re.search(r"plafond [\d\u202f]+\u202f€", corps)

    # Et les deux repères sont bien convertis, non recopiés : le SMIC net d'un
    # salarié du privé vaut environ 79 % de son brut.
    _, brut = rendre("/simuler", {"montants": "brut"})
    _, net = rendre("/simuler", {"montants": "net"})
    def smic(corps):
        return float(re.search(r"SMIC ([\d\u202f]+)\u202f€", corps)
                     .group(1).replace("\u202f", ""))
    assert 0.75 < smic(net) / smic(brut) < 0.85


def test_le_champ_de_revenu_ecarte_la_pension():
    """Un retraité ne doit pas pouvoir y écrire sa pension sans être averti.

    « Revenu mensuel », sous une date de départ déjà passée, se lit comme « ce
    que vous touchez aujourd'hui ». Le montant serait alors cotisé comme un
    salaire, et la pension rendue serait fausse sans rien avoir l'air de l'être
    — d'où le mot « d'activité » dans le LIBELLÉ, qui se lit sans rien ouvrir,
    et la conduite à tenir dans le complément, dans les deux unités de saisie.
    """
    for unite, libelle in (("euros_mois", "Revenu d&#x27;activité"),
                           ("moyen", "Niveau de revenu d&#x27;activité")):
        _, corps = rendre("/simuler", {"unite_revenu": unite})
        assert libelle in corps
        assert "Jamais une pension" in corps
        assert "déposez votre relevé" in corps


# -- la saisie par la pension ------------------------------------------------


def _pension_affichee(corps: str) -> float:
    """Le montant que la page écrit sur la barre du système actuel.

    Lu sur le HTML et non recalculé : c'est ce que le lecteur voit qui doit
    valoir ce qu'il a tapé, et un contrôle qui relancerait le modèle ne dirait
    rien de la chaîne d'affichage — mensualisation, net, euros constants — que
    l'inversion doit traverser À L'ENVERS pour poser sa cible.

    À l'euro depuis le 23 septembre 2026, comme toute la vue des résultats :
    une pension saisie en euros ronds s'y relit donc à l'identique.
    """
    depart = corps.find("1. Système de répartition actuel")
    assert depart >= 0, "la barre du système actuel a disparu de la page"
    montant = re.search(
        r'<span class="chiffre principal">.*?'
        r'<span class="somme">([\d\u202f]+)</span>',
        corps[depart:], re.S,
    )
    assert montant, f"aucun montant lisible : {corps[depart:depart + 300]}"
    return float(montant.group(1).replace("\u202f", ""))


@pytest.mark.parametrize("pension,mode", [
    (1500, "net"), (2400, "net"), (1100, "net"), (2000, "brut"),
])
def test_la_pension_saisie_est_celle_que_le_systeme_actuel_sert(pension, mode):
    """L'aller-retour, qui est tout l'objet de la fonctionnalité.

    On saisit une pension ; la page doit afficher CETTE pension sur la barre du
    système actuel, au centime près. Si elle affichait autre chose, le revenu
    déduit ne serait le revenu de personne, et les trois autres systèmes
    seraient calculés sur une carrière qui n'est pas celle du lecteur.
    """
    _, corps = rendre("/simuler", {
        "saisie_par": "pension", "pension": str(pension), "montants": mode,
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Saisie refusée" not in corps
    assert abs(_pension_affichee(corps) - pension) < 0.5


def test_le_revenu_deduit_est_annonce_avant_les_quatre_montants():
    """La réponse à la question posée passe devant la réponse aux autres."""
    _, corps = rendre("/simuler", {
        "saisie_par": "pension", "pension": "1500",
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Le revenu que votre pension suppose" in corps
    assert corps.index("Le revenu que votre pension suppose") < corps.index(
        "Système de répartition actuel"
    )


def test_le_lien_de_reprise_decrit_la_meme_carriere():
    """Reprendre en saisissant le revenu doit rendre la même pension.

    C'est le seul endroit où la bascule de saisie traduit : elle ne le peut pas
    d'elle-même, faute de connaître le résultat d'un calcul qui n'a pas encore
    eu lieu, et c'est la page de résultats qui porte le nombre trouvé. Si ce
    lien perdait le revenu, le lecteur qui veut corriger sa carrière repartirait
    de la valeur par défaut sans que rien ne le dise.
    """
    _, corps = rendre("/simuler", {
        "saisie_par": "pension", "pension": "1500",
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    # DANS LE BLOC DU REVENU DÉDUIT, et nulle part ailleurs : la bascule du
    # formulaire porte elle aussi « saisie_par=revenu », mais sans le nombre
    # trouvé — elle ne peut pas le connaître. Chercher le premier lien venu
    # aurait mesuré la bascule en croyant mesurer la reprise.
    bloc = re.search(r'<div class="carte revenu-deduit">(.*?)</div>', corps, re.S)
    assert bloc, "le bloc du revenu déduit a disparu de la page"
    lien = re.search(r'href="\./#([^"]*saisie_par=revenu[^"]*)"',
                     bloc.group(1))
    assert lien, "la page ne propose pas de reprendre la carrière en revenu"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["saisie_par"] == "revenu"
    _, repris = rendre("/simuler", requete)
    assert "Saisie refusée" not in repris
    # L'arrondi à l'euro du revenu écrit dans le lien déplace la pension de
    # quelques euros : c'est la même carrière, pas le même centime.
    assert abs(_pension_affichee(repris) - 1500) < 15


@pytest.mark.parametrize("pension,phrase", [
    ("9000", "plafonne à"),
    ("1", "font ce plancher"),
])
def test_une_pension_que_nulle_carriere_ne_sert_est_refusee(pension, phrase):
    """Les refus disent une règle du droit, jamais une limite du calcul.

    Au-dessus du plafond de tranche, cotiser n'acquiert plus rien ; au-dessous
    du minimum contributif, le droit sert un montant qu'aucun revenu ne fait
    descendre. Rendre malgré tout un revenu approché aurait été le pire des
    trois choix : un chiffre faux, vraisemblable, et que rien ne signale.
    """
    _, corps = rendre("/simuler", {
        "saisie_par": "pension", "pension": pension,
        "naissance": "1955-06-01", "debut": "1975-01", "liquidation": "2017-06",
    })
    assert "Saisie refusée" in corps
    assert phrase in corps


def test_la_situation_est_la_premiere_question_et_commande_la_saisie():
    """« En activité ou à la retraite » vient avant tout, et décide du reste.

    C'est la question qui a remplacé « je saisis : mon revenu / ma pension » —
    une question de modélisation posée à quelqu'un qui n'est pas venu
    modéliser. Elle doit donc arriver AVANT le premier champ, et emporter avec
    elle ce que le formulaire demande : un actif ne connaît pas sa pension, un
    retraité ne se souvient pas de son salaire.
    """
    _, actif = rendre("/simuler", {})
    assert "Vous êtes" in actif
    assert actif.index("Vous êtes") < actif.index('id="naissance"'), (
        "la situation ne vient plus avant le premier champ"
    )
    assert 'id="salaire"' in actif and 'id="pension"' not in actif

    _, retraite = rendre("/simuler", {"situation": "retraite"})
    assert 'id="pension"' in retraite and 'id="salaire"' not in retraite

    # Le lien de la bascule porte les DEUX réglages : cliquer reconfigure le
    # formulaire d'un coup, sans passer par un second contrôle.
    lien = re.search(r'aria-label="Vous êtes".*?href="\./#([^"]*)"',
                     actif, re.S)
    assert lien, "la bascule de situation ne mène nulle part"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["situation"] == "retraite"
    assert requete["saisie_par"] == "pension"


def test_une_adresse_qui_ne_dit_que_la_situation_ouvre_la_bonne_saisie():
    """Le défaut suit la situation ; l'explicite l'emporte.

    Une adresse partagée à la main — « ?situation=retraite » — doit ouvrir le
    formulaire sur la pension, sans qu'on ait à écrire le second réglage. Mais
    un retraité qui a choisi de saisir ce qu'il gagnait garde son choix, parce
    que son adresse le dit.
    """
    assert saisie_du_portage({"situation": "retraite"}).saisie_par == "pension"
    assert saisie_du_portage({"situation": "actif"}).saisie_par == "revenu"
    assert saisie_du_portage(
        {"situation": "retraite", "saisie_par": "revenu"}).saisie_par == "revenu"


def test_le_desaccord_de_situation_est_dit_et_non_corrige():
    """La situation et la date peuvent se contredire, et c'est sans danger.

    Le modèle ne lit QUE la date : aucun chiffre ne dépend de la situation
    déclarée. Corriger la date effacerait une carrière saisie, refuser la
    saisie arrêterait quelqu'un sur un réglage qui ne change aucun résultat —
    le formulaire le dit, et laisse la date décider.
    """
    # L'exemple par défaut est celui d'un actif : se déclarer retraité le
    # contredit, et c'est le premier clic de qui vient pour sa pension.
    _, incoherent = rendre("/simuler", {"situation": "retraite"})
    assert "Vous vous dites à la retraite" in incoherent
    assert "Saisie refusée" not in incoherent

    # Et dans l'autre sens.
    _, inverse = rendre("/simuler", {
        "situation": "actif", "naissance": "1955-06-01", "debut": "1975-01",
        "liquidation": "2017-06"})
    assert "Vous vous dites en activité" in inverse

    # Une situation cohérente ne dit rien du tout.
    _, coherent = rendre("/simuler", {
        "situation": "retraite", "naissance": "1955-06-01",
        "debut": "1975-01", "liquidation": "2017-06"})
    assert "Vous vous dites" not in coherent


def test_un_retraite_peut_encore_saisir_ce_qu_il_gagnait():
    """L'échappatoire est offerte là où elle sert, et dans ce sens-là seul.

    Un retraité qui a gardé ses fiches de paie doit pouvoir donner son revenu ;
    une bascule permanente aurait remis à tout le monde la question qu'on vient
    de retirer, une ligne sous le champ suffit. Le chemin inverse — un actif
    qui vise une pension — n'est pas offert sur le formulaire de tout le monde :
    il passe par la situation, et la page dit alors que c'est la date qui
    compte.
    """
    _, retraite = rendre("/simuler", {"situation": "retraite"})
    # PAR SON TEXTE, et non par le premier lien venu : la bascule de situation
    # porte elle aussi « saisie_par=revenu », mais elle change de situation en
    # même temps. Chercher au plus court aurait mesuré la bascule.
    lien = re.search(
        r'href="\./#([^"]*)">Ou saisir ce que vous gagniez\.</a>',
        retraite)
    assert lien, "un retraité ne peut plus saisir ce qu'il gagnait"
    requete = dict(parse_qsl(html.unescape(lien.group(1))))
    assert requete["situation"] == "retraite" and requete["saisie_par"] == "revenu"
    _, repris = rendre("/simuler", requete)
    assert 'id="salaire"' in repris and 'id="pension"' not in repris

    # En activité, aucune ligne de ce genre : le formulaire reste nu.
    _, actif = rendre("/simuler", {})
    assert "Ou saisir" not in actif


def test_la_bascule_net_brut_traduit_la_pension_saisie():
    """Changer d'affichage ne doit pas changer la carrière qu'on a décrite.

    Le nombre du formulaire est un NET en mode net. Le recopier tel quel dans
    l'autre mode le ferait relire comme un brut — une pension plus petite d'un
    dixième —, et la page reviendrait en décrivant une autre carrière que celle
    qu'on venait de calculer, sans un mot. C'est le bogue que la bascule évite
    depuis toujours pour les salaires ; la pension l'avait rouvert.
    """
    # En net, que la page ne prend plus par défaut depuis le 4 octobre 2026.
    base = {"saisie_par": "pension", "pension": "1800", "montants": "net",
            "naissance": "1975-01-01", "debut": "1996-01",
            "liquidation": "2039-01"}
    _, corps = rendre("/simuler", base)
    bloc = re.search(r'<div class="bascule"[^>]*aria-label="Montants".*?</div>',
                     corps, re.S)
    assert bloc, "la bascule des montants a disparu"
    lien = re.search(r'href="\./#([^"]*)"', bloc.group(0))
    assert lien, "la bascule ne mène nulle part"
    vers_brut = dict(parse_qsl(html.unescape(lien.group(1))))
    assert vers_brut["montants"] == "brut"
    # 1 800 € nets valent le brut que le taux du foyer laisse : sa tranche de
    # CSG, présumée sur ses seules pensions, et la cotisation maladie de sa
    # part complémentaire (action 138, étape 2) : les montants du portage, que
    # la bascule applique.
    taux = montants_du_portage(base).taux_pension
    assert float(vers_brut["pension"]) == pytest.approx(1800 / (1 - taux), abs=1.0), (
        f"la pension n'a pas été traduite : {vers_brut['pension']}"
    )
    # Et la carrière est la même des deux côtés : le revenu déduit en brut est
    # celui du net, converti par la fiche de paie du statut.
    _, en_brut = rendre("/simuler", vers_brut)
    assert abs(_pension_affichee(en_brut)
               - float(vers_brut["pension"])) < 1.5


def test_les_deux_revenus_de_la_page_ne_se_contredisent_pas():
    """La page en affiche deux, et elle doit dire pourquoi ils diffèrent.

    Le bloc du haut donne le revenu du MILIEU de carrière — celui que le
    formulaire demande —, les barres donnent ce que la carrière paie l'année de
    référence des fiches de paie. Le profil de carrière fait monter le revenu
    avec l'âge : les deux nombres diffèrent, et les lire à quelques centimètres
    l'un de l'autre sans explication faisait douter des deux.
    """
    commun = {"saisie_par": "pension", "pension": "1800",
              "naissance": "1975-01-01", "debut": "1996-01",
              "liquidation": "2039-01"}
    _, ascendant = rendre("/simuler", commun)
    assert "Les barres en portent un second" in ascendant
    deduit = re.search(r'<p class="cle-chiffre">([\d\u202f]+)', ascendant)
    paie = re.search(r'<span class="chiffre salaire">.*?'
                     r'<span class="somme">([\d\u202f]+)', ascendant, re.S)
    assert deduit and paie, "un des deux revenus a disparu de la page"
    assert deduit.group(1) != paie.group(1), (
        "les deux revenus coïncident : la phrase qui les distingue n'a plus "
        "lieu d'être, et ce test ne mesure plus rien"
    )

    # Sous un profil PLAT, le revenu ne bouge pas avec l'âge : les deux
    # tombent sur le même euro, et la phrase se tait plutôt que d'expliquer
    # une différence qui n'existe pas.
    _, plat = rendre("/simuler", {**commun, "profil": "plat"})
    assert "Les barres en portent un second" not in plat


def test_le_formulaire_de_pension_retire_les_revenus():
    """Les deux nombres ne peuvent pas compter à la fois.

    Laisser les champs de revenu à côté du champ de pension ferait croire que
    la carrière porte les deux, alors que l'un est saisi et l'autre cherché.
    """
    _, revenu = rendre("/simuler", {"saisie_par": "revenu"})
    _, pension = rendre("/simuler", {
        "saisie_par": "pension", "pension": "1500"})
    assert 'id="salaire"' in revenu and 'id="pension"' not in revenu
    assert 'id="pension"' in pension and 'id="salaire"' not in pension
    # L'unité de saisie ne gouverne plus aucun nombre : elle s'efface avec eux.
    assert "× salaire moyen" in revenu and "× salaire moyen" not in pension


def test_le_multiple_est_traduit_en_euros():
    _, corps = rendre("/simuler", {"unite_revenu": "moyen", "salaire": "1"})
    assert "1 = salaire moyen, soit" in corps


# -- le relevé de carrière ---------------------------------------------------


def _releve(premiere: int, derniere: int,
            statut: str = "salarie_prive_non_cadre") -> str:
    """Un relevé plausible, une ligne par année, quatre trimestres chacune."""
    return ",".join(
        f"{annee}:{statut}:{14000 + 500 * (annee - premiere)}:4"
        for annee in range(premiere, derniere + 1)
    )


def test_le_releve_est_lu_ligne_a_ligne():
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "64",
        "releve": "1998:salarie_prive_non_cadre:14200:4\n"
                  "1999:salarie_prive_cadre:19800",
    })
    assert saisie.releve_actif
    lignes = saisie.releve_analyse()
    assert [(l.annee, l.affiliation, l.revenu, l.trimestres) for l in lignes] == [
        (1998, "salarie_prive_non_cadre", 14200.0, 4),
        # Le quatrième champ manque : le modèle déduira les trimestres du
        # montant cotisé, comme il le fait d'une carrière paramétrique.
        (1999, "salarie_prive_cadre", 19800.0, None),
    ]


def test_le_releve_remplace_la_carriere_parametrique(saisies):
    """Deux simulations, mêmes bornes : le relevé n'emprunte rien au profil."""
    commun = {"naissance": "1975", "liquidation": "64", "debut": "23",
              "statut": "salarie_prive_non_cadre", "unite_revenu": "moyen",
              "salaire": "1"}
    lue = saisies.simuler({**commun, "releve": _releve(1998, 2038)})
    reconstituee = saisies.simuler(commun)
    assert lue.carriere.annee_liquidation == reconstituee.carriere.annee_liquidation
    # Les années du relevé, puis janvier 2039, que le site lui ajoute avant le
    # départ du 1er février : celles de la carrière reconstituée.
    assert [ligne.annee for ligne in lue.carriere.lignes] == list(range(1998, 2040))
    assert ([ligne.annee for ligne in lue.carriere.lignes]
            == [ligne.annee for ligne in reconstituee.carriere.lignes])
    # Les revenus sont ceux du relevé, en euros de chaque année, et non ceux
    # qu'un niveau relatif et un profil auraient fabriqués.
    assert lue.carriere.ligne(1998).revenu == 14000.0
    assert lue.carriere.ligne(1998).revenu != reconstituee.carriere.ligne(1998).revenu


def test_les_trimestres_declares_l_emportent_sur_le_montant(saisies):
    """Le relevé fait foi : un temps partiel ne se lit sur aucun salaire."""
    carriere = saisies.simuler({
        "naissance": "1975", "liquidation": "64",
        "releve": "2000:salarie_prive_non_cadre:30000:2",
    }).carriere
    assert carriere.ligne(2000).trimestres_valides == 2


def test_l_annee_du_depart_est_tronquee_par_la_liquidation(saisies):
    """Le relevé donne l'année ; la date de liquidation dit jusqu'où elle compte."""
    carriere = saisies.simuler({
        "naissance": "1975", "liquidation": "64", "liquidation_mois": "7",
        "releve": _releve(1998, 2039),
    }).carriere
    assert carriere.ligne(2038).fraction_annee == 1.0
    # Né en janvier 1975, présumé le 15 : départ à 64 ans et 7 mois, donc au
    # 1er septembre 2039 — du mois qui suit l'anniversaire —, huit mois
    # travaillés.
    assert carriere.ligne(2039).fraction_annee == 8 / 12
    # Huit mois : deux trimestres civils au plus, quoi qu'en dise la ligne du
    # relevé, qui en déclare quatre.
    assert carriere.ligne(2039).trimestres_valides == 2


def test_les_interruptions_valent_encore_sur_un_releve(saisies):
    """Le relevé ne dit pas la NATURE de l'année ; le champ des motifs, si."""
    carriere = saisies.simuler({
        "naissance": "1975", "liquidation": "64",
        "releve": _releve(1998, 2038),
        "interruptions": "2005:2006:chomage_indemnise",
    }).carriere
    chomage = carriere.ligne(2005)
    assert chomage.type_periode == "chomage_indemnise"
    assert not chomage.cotisations_versees
    assert chomage.revenu == 0.0
    # Le revenu de la ligne devient le salaire de référence sur lequel les
    # régimes complémentaires continuent d'acquérir des points.
    assert chomage.revenu_reference == 17500.0
    assert carriere.ligne(2007).cotisations_versees


def test_un_releve_vide_laisse_la_carriere_parametrique():
    assert not saisie_du_portage({"releve": "   "}).releve_actif


@pytest.mark.parametrize("ligne", [
    "2005:salarie_prive_non_cadre",          # trois champs exigés
    "2005:salarie_prive_non_cadre:1:2:3",    # quatre au plus
    "deux-mille:salarie_prive_non_cadre:1:4",
    "2005::24000:4",                         # statut manquant
    "2005:salarie_prive_non_cadre:abc:4",
    "2005:salarie_prive_non_cadre:-1:4",
    "2005:salarie_prive_non_cadre:24000:5",
    "2005:salarie_prive_non_cadre:24000:-1",
    "2005:salarie_prive_non_cadre:24000:4, 2005:artisan:9000:4",
    "{minimale_moins_un}:salarie_prive_non_cadre:1:4",
    "{maximale_plus_un}:salarie_prive_non_cadre:1:4",
    "1970:salarie_prive_non_cadre:1:4",      # avant les quatorze ans de l'assuré
    "2040:salarie_prive_non_cadre:1:4",      # après le départ, au 1er février 2039
])
def test_une_ligne_de_releve_fautive_est_refusee(ligne):
    ligne = ligne.format(minimale_moins_un=SAISIE.ANNEE_CARRIERE_MINIMALE - 1,
                         maximale_plus_un=SAISIE.ANNEE_CARRIERE_MAXIMALE + 1)
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "64", "releve": ligne,
    })
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie.releve_analyse()


def test_un_releve_demesure_est_refuse():
    """L'adresse EST la saisie : un relevé forgé dans un lien figeait l'onglet.

    Le refus tombe sur le NOMBRE de lignes, avant que la première ne soit lue :
    c'est ce qui le rend gratuit. Compter les lignes analysées ferait payer au
    lecteur tout le relevé qu'on voulait justement lui épargner.
    """
    lignes = ",".join(
        f"{annee}:salarie_prive_non_cadre:100:4"
        for annee in range(1930, 1930 + SAISIE.RELEVE_MAXIMUM + 1)
    )
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "64", "releve": lignes,
    })
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("au plus")):
        saisie.releve_analyse()


def test_aucune_carriere_n_atteint_la_borne_du_releve():
    """La borne du relevé est au-dessus de ce que la fenêtre des âges permet.

    Une carrière tient entre l'âge de début minimal et l'âge de liquidation
    maximal ; une année ne s'y déclare qu'une fois. La borne doit rester
    au-dessus de ce compte, faute de quoi elle refuserait une carrière que le
    reste du formulaire accepte.
    """
    assert SAISIE.RELEVE_MAXIMUM > SAISIE.AGE_LIQUIDATION_MAXIMAL - SAISIE.AGE_DEBUT_MINIMAL


def test_un_statut_ferme_est_refuse_aussi_sur_un_releve():
    """Le refus parle d'années déclarées, non d'un « métier n° 2 » inexistant."""
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "64",
        "releve": "2015:mineur:24000:4",
    })
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("première année déclarée")):
        site().contexte.simuler(saisie)


def test_un_statut_inconnu_du_releve_est_refuse():
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "64",
        "releve": "2005:cosmonaute:24000:4",
    })
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("cosmonaute")):
        site().contexte.simuler(saisie)


def test_le_releve_voyage_dans_l_adresse():
    """Il est un paramètre comme les autres : un lien décrit la carrière entière."""
    saisie = saisie_du_portage({"releve": _releve(2000, 2002)})
    parametres = dict(parse_qsl(saisie.requete()))
    assert parametres["releve"] == _releve(2000, 2002)
    assert saisie_du_portage(parametres).releve == saisie.releve


def test_la_page_dit_que_la_carriere_a_ete_lue(page):
    texte = page("/simuler", naissance=1975, liquidation=64, releve=_releve(1998, 2038))
    assert "lue sur un relevé" in texte
    assert "41 années de 1998 à 2038" in texte
    # Le dépliant est ouvert : sinon l'adresse porterait une carrière que la
    # page ne montrerait pas.
    assert '<details class="releve" open>' in texte


def test_le_releve_est_le_premier_mode_de_remplissage(page):
    """Le dépôt du relevé ouvre le formulaire, avant la naissance et les
    périodes, et hors de tout dépliant : il était replié sous les métiers, où
    il passait pour une option, et la carrière qu'il écrit est la plus exacte
    (le propriétaire, le 20 octobre 2026). La saisie à la main du même relevé
    reste repliée, sous lui ; le champ du revenu y renvoie plus haut."""
    texte = page("/simuler")
    assert texte.index('id="releve-fichier"') < texte.index('id="naissance"') \
        < texte.index('class="metiers"')
    hors_depliants = re.sub(r"<details\b.*?</details>", "", texte, flags=re.S)
    assert 'id="releve-fichier"' in hors_depliants
    assert "<strong>Déposez votre relevé de carrière</strong>" in hors_depliants
    assert '<a href="https://www.info-retraite.fr/">' in hors_depliants
    assert 'name="releve"' not in hors_depliants, "la saisie à la main reste repliée"
    assert "Ou déposez votre relevé, plus haut" in texte


def test_la_page_dit_ce_qu_elle_ajoute_au_releve_jusqu_au_depart(page):
    """Le relevé se prolonge jusqu'au départ (``Contexte.releveProlonge``) : la
    page le dit, avec la ligne qui l'en dispense à qui ne travaille plus ; une
    fois cette ligne écrite, elle dit ce qu'elle en a fait."""
    texte = page("/simuler", naissance=1975, liquidation=64, releve=_releve(1998, 2024))
    assert "Après 2024, votre dernière année se poursuit de 2025 à 2039" in texte
    assert "<code>2025:2039:sans_activite</code>" in texte
    texte = page("/simuler", naissance=1975, liquidation=64, releve=_releve(1998, 2024),
                 interruptions="2025:2039:sans_activite")
    assert "Après 2024, vous restez sans emploi de 2025 à 2039, comme vous le déclarez." in texte
    texte = page("/simuler", naissance=1975, liquidation=64, releve=_releve(1998, 2024),
                 interruptions="2030:2031:chomage_indemnise")
    assert "2 de ces années restent sans emploi" in texte


# -- plusieurs métiers -------------------------------------------------------


def test_les_metiers_suivants_sont_lus_dans_la_requete():
    saisie = saisie_du_portage({
        "statut": "salarie_prive_non_cadre", "salaire": "0.9",
        "metier2_debut": "35", "metier2_statut": "fonctionnaire_etat",
        "metier2_salaire": "1.2",
        "metier3_debut": "50", "metier3_statut": "artisan",
    })
    assert [(m.debut, m.statut, m.salaire) for m in saisie.metiers] == [
        (35.0, "fonctionnaire_etat", 1.2),
        # Le niveau non renseigné est celui du métier précédent : changer de
        # statut n'est pas changer de revenu.
        (50.0, "artisan", 1.2),
    ]
    parcours = saisie.parcours(_echelle())
    assert len(parcours) == 3
    assert parcours[0].affiliation == "salarie_prive_non_cadre"
    assert parcours[0].niveau_salaire == 0.9
    assert parcours[2].affiliation == "artisan"


def test_une_adresse_sans_metier_decrit_une_carriere_d_un_seul_metier():
    """Toutes les adresses déjà partagées doivent continuer de valoir."""
    saisie = saisie_du_portage({"naissance": "1960", "statut": "mineur"})
    assert saisie.metiers == []
    assert [metier.affiliation for metier in saisie.parcours(_echelle())] == ["mineur"]


def test_une_ligne_de_metier_a_moitie_remplie_est_refusee():
    """La ligne vide du formulaire ne décrit rien ; à moitié remplie, elle ment."""
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("date à laquelle il commence")):
        saisie_du_portage({"metier2_statut": "artisan"})
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("statut d'affiliation")):
        saisie_du_portage({"metier2_debut": "40"})


@pytest.mark.parametrize("champs", [
    # Un métier antérieur au précédent : les périodes se recouvriraient.
    {"debut": "21", "metier2_debut": "20", "metier2_statut": "artisan"},
    # Un métier postérieur au départ à la retraite.
    {"liquidation": "64", "metier2_debut": "70", "metier2_statut": "artisan"},
    # Deux métiers commençant la même année.
    {"metier2_debut": "40", "metier2_statut": "artisan",
     "metier3_debut": "40", "metier3_statut": "marin"},
    # Un niveau de revenu hors bornes.
    {"metier2_debut": "40", "metier2_statut": "artisan", "metier2_salaire": "40"},
])
def test_metiers_incoherents_sont_refuses(champs):
    with pytest.raises(ErreurSite, match=REFUSEE):
        saisie_du_portage(champs)


def test_un_metier_de_statut_inconnu_est_refuse():
    saisie = saisie_du_portage({
        "naissance": "1975", "metier2_debut": "40", "metier2_statut": "astronaute",
    })
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("astronaute")):
        site().contexte.simuler(saisie)


def test_changer_de_metier_change_le_resultat(saisies):
    commun = {"naissance": "1975", "debut": "21", "liquidation": "64"}
    seul = saisies.simuler(commun).dictionnaire()
    reconverti = saisies.simuler({
        **commun, "metier2_debut": "42", "metier2_statut": "artisan",
    }).dictionnaire()

    assert reconverti["assure"]["affiliations"] == [
        "salarie_prive_non_cadre", "artisan",
    ]
    assert (reconverti["scenarios"]["notionnel_retroactif"]["pension_annuelle"]
            != seul["scenarios"]["notionnel_retroactif"]["pension_annuelle"])


def test_le_formulaire_offre_toujours_une_ligne_de_metier_de_plus(page):
    """C'est ainsi qu'on ajoute un métier : sans une ligne de JavaScript.

    La ligne de plus est REPLIÉE : elle ne coûte qu'un résumé tant qu'on ne
    veut pas s'en servir. Les périodes déjà décrites, elles, restent des
    groupes de champs, et leur rang en est la légende.
    """
    vierge = page("/simuler")
    assert vierge.count('<legend class="rang">') == 1
    assert vierge.count("<span>Ajouter une période") == 1
    assert 'name="metier2_debut" value=""' in vierge

    rempli = page("/simuler", naissance=1975, metier2_debut=40, metier2_statut="artisan")
    assert rempli.count('<legend class="rang">') == 2
    assert rempli.count("<span>Ajouter une période") == 1
    assert 'name="metier3_debut" value=""' in rempli


def test_le_formulaire_s_arrete_au_nombre_maximal_de_metiers(page):
    champs, maximum = {"naissance": 1960, "liquidation": 64}, SAISIE.METIERS_MAXIMUM
    for rang in range(2, maximum + 1):
        champs[f"metier{rang}_debut"] = 30 + rang
        champs[f"metier{rang}_statut"] = "artisan"
    texte = page("/simuler", **champs)
    assert texte.count('<legend class="rang">') == maximum
    assert "<span>Ajouter une période" not in texte
    assert f'name="metier{maximum + 1}_debut"' not in texte


def test_la_page_recapitule_le_parcours(page):
    texte = page("/simuler", naissance=1975, debut=21, liquidation=64,
                 metier2_debut=42, metier2_statut="artisan")
    assert "Carrière en 2 périodes" in texte
    assert "Artisan de 42 ans à 64 ans" in texte


def test_les_motifs_du_menu_existent_dans_la_table_des_periodes():
    """Le menu ne peut pas proposer un motif que le moteur ne connaîtrait pas.

    ``_ligne_annuelle`` rabat tout motif inconnu sur « sans activité » : un code
    mal orthographié dans le formulaire validerait zéro trimestre au lieu de
    quatre, et changerait la pension sans un mot.
    """
    table = _motifs()
    for code, _ in SAISIE.SANS_EMPLOI:
        assert code in table, f"motif proposé par le formulaire et absent de la table : {code}"


def test_une_periode_sans_emploi_vaut_l_interruption_qu_elle_decrit(saisies):
    """Une ligne « sans emploi » et le champ « Interruptions » disent la même
    chose : c'est le même chemin dans le moteur, et les chiffres doivent l'être
    aussi, jusqu'au dernier."""
    base = {"naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
            "unite_revenu": "euros_mois", "salaire": "2600"}
    par_ligne = saisies.simuler({
        **base, "metier2_debut": "2020-03", "metier2_statut": "chomage_indemnise",
    }).dictionnaire()
    par_champ = saisies.simuler({
        **base, "interruptions": "2020:2026:chomage_indemnise",
    }).dictionnaire()
    assert par_ligne == par_champ


def test_la_fin_d_activite_retire_les_annees_qu_elle_couvre(saisies):
    """Le défaut que la ligne comble : sans elle, le calcul suppose qu'on a
    travaillé jusqu'au mois du départ."""
    base = {"naissance": "1962-03-15", "debut": "1984-09", "liquidation": "2026-07",
            "unite_revenu": "euros_mois", "salaire": "2600"}
    continu = saisies.simuler(base)
    arrete = saisies.simuler({
        **base, "metier2_debut": "2020-03", "metier2_statut": "sans_activite",
    })
    assert arrete.actuel.pension_mensuelle < continu.actuel.pension_mensuelle
    assert (arrete.notionnel_retroactif.pension_mensuelle
            < continu.notionnel_retroactif.pension_mensuelle)
    # Six années de moins au compte : celles que la ligne couvre.
    cotisees = lambda comparaison: sum(  # noqa: E731
        1 for ligne in comparaison.carriere.lignes if ligne.cotise
    )
    assert cotisees(continu) - cotisees(arrete) == 7


@pytest.mark.parametrize("debut, premiere_annee_creuse", [
    # Sept mois sans emploi sur douze : l'année revient à ce qui l'occupe le
    # plus, c'est-à-dire au creux.
    ("2020-06", 2020),
    # Six mois partout : à égalité, l'année reste travaillée.
    ("2020-07", 2021),
    ("2020-08", 2021),
])
def test_l_annee_ou_l_activite_s_arrete_revient_au_plus_grand_nombre_de_mois(
    debut, premiere_annee_creuse,
):
    """La même convention que pour un changement de métier : le moteur ne
    connaît qu'un statut par année civile, et c'est le plus long qui l'emporte."""
    saisie = saisie_du_portage({
        "naissance": "1962-01-01", "debut": "1984-09", "liquidation": "2026-07",
        "metier2_debut": debut, "metier2_statut": "sans_activite",
    })
    assert min(saisie.interruptions_de_carriere()) == premiere_annee_creuse


def test_une_periode_sans_emploi_ne_demande_pas_de_revenu(page):
    """Elle n'en paie aucun : le champ disparaît plutôt que de demander un
    nombre dont rien ne serait fait."""
    avec_metier = page("/simuler", naissance="1975-01-01", debut="1996-01",
                       liquidation="2039-01", metier2_debut="2020-01",
                       metier2_statut="artisan")
    assert 'name="metier2_salaire"' in avec_metier
    sans_emploi = page("/simuler", naissance="1975-01-01", debut="1996-01",
                       liquidation="2039-01", metier2_debut="2020-01",
                       metier2_statut="chomage_indemnise")
    assert 'name="metier2_salaire"' not in sans_emploi
    assert "Deuxième période, sans emploi" in sans_emploi


def test_aucun_menu_ne_propose_deux_fois_la_meme_valeur(page):
    """Deux options de même valeur dans un menu, c'est une saisie qui ne revient
    pas : le navigateur choisit la première, et la seconde est inatteignable.
    Le risque est né avec les périodes sans emploi, dont « sans activité » est
    AUSSI une affiliation."""
    texte = page("/simuler")
    for menu in re.findall(r"<select\b.*?</select>", texte, re.S):
        valeurs = re.findall(r'<option value="([^"]*)"', menu)
        doublons = {valeur for valeur in valeurs if valeurs.count(valeur) > 1}
        assert not doublons, f"valeurs proposées deux fois : {doublons}"


def test_le_premier_metier_reste_une_affiliation():
    """« sans_activite » est aussi une affiliation — celle de qui n'a jamais
    travaillé —, et les adresses qui la portent en premier métier ne doivent pas
    changer de sens."""
    saisie = saisie_du_portage({"statut": "sans_activite"})
    assert [ligne.sans_emploi for ligne in saisie.lignes_carriere] == [False]
    assert saisie.interruptions_de_carriere() == {}
    assert [metier.affiliation for metier in saisie.parcours(_echelle())] == [
        "sans_activite"
    ]
    # Et le menu de la première ligne la propose toujours sous son nom de
    # statut, quand celui des lignes suivantes la range avec les creux.
    texte = rendre("/simuler", {})[1]
    premier = texte.split('name="metier2_statut"')[0]
    assert '<option value="sans_activite">Sans activité professionnelle' in premier


def test_la_page_recapitule_une_periode_sans_emploi(page):
    """Une ligne peut ne pas être un métier : le résumé la nomme comme les
    autres, et dit à quel âge l'activité s'est arrêtée."""
    texte = page("/simuler", naissance=1975, debut=21, liquidation=64,
                 metier2_debut=58, metier2_statut="chomage_indemnise")
    assert "Carrière en 2 périodes" in texte
    assert "chômage indemnisé de 58 ans à 64 ans" in texte


def test_requete_reconstruit_les_metiers():
    requete = saisie_du_portage({
        "naissance": "1975-01-01", "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "1.5",
    }).requete()
    # Quarante ans, pour qui est né en janvier 1975, c'est janvier 2015 :
    # l'adresse porte la date, le formulaire la rend au calendrier.
    assert "metier2_debut=2015-01" in requete
    assert "metier2_statut=artisan" in requete
    assert "metier2_salaire=1.5" in requete
    assert "metier3_debut" not in requete


def test_requete_reconstruit_les_parametres():
    requete = SAISIE.Saisie({"naissance": 1960, "statut": "mineur"}).requete()
    assert "naissance=1960" in requete
    assert "statut=mineur" in requete


def test_la_situation_de_foyer_traverse_l_adresse_et_le_modele(saisies):
    """« foyer=couple » retire l'allocation d'isolement du scénario 6, et rien
    d'autre : l'adresse la porte, le formulaire la relit, le modèle la reçoit,
    par le pont."""
    from retraite_notionnelle.config import SituationFoyer

    saisie = saisie_du_portage({"foyer": "couple"})
    assert saisie.foyer == "couple"
    assert "foyer=couple" in saisie.requete()
    assert saisies.parametres({"foyer": "couple"}).situation_foyer is SituationFoyer.COUPLE
    assert saisie_du_portage({"foyer": "n'importe quoi"}).foyer == "seul"


def test_la_page_detaille_la_garantie_vieillesse_du_scenario_6(page):
    """À 65 ans et à petit salaire, la garantie est servie et la page dit
    combien l'impôt en finance ; à 62 ans, elle dit pourquoi rien n'est servi."""
    texte = page("/simuler", naissance=1958, liquidation=65, salaire=1300,
                 unite_revenu="euros_mois")
    assert "Le système 4 : un taux pour tous" in texte
    assert "Garantie vieillesse" in texte
    assert "rente du pilier capitalisé" in texte
    assert "l'impôt en finance" in texte
    assert "personne seule, 300\u00a0€" in texte
    texte = page("/simuler", naissance=1958, liquidation=62, salaire=1300,
                 unite_revenu="euros_mois")
    assert "avant les 65 ans" in texte


def test_la_page_ecrit_les_cinq_points_volontaires_partout_ou_ils_pesent(page):
    """Les cinq points rendus se lisent sur la pension ET sur la fiche de paie.

    La règle de ce bloc : nulle part le site n'additionne en silence une
    épargne facultative à une cotisation obligatoire. Le total du système 4
    est annoncé comme un PLAFOND — « retraite jusqu'à » —, la ligne sous lui
    écrit le plancher qu'on touche sans rien ajouter et ce que les cinq points
    rendus ajoutent si on les place ; et sur la fiche de paie, le net affiché
    est le net PLEIN — la fiche ne retient pas ce que personne n'impose —,
    puis le placement et ce qui reste à qui le fait.
    """
    texte = page("/simuler", naissance=1995, liquidation=64, salaire=3000,
                 unite_revenu="euros_mois")
    plat = " ".join(texte.split())
    # Le grand nombre du système 4 dit qu'il est un plafond, et lui seul : les
    # trois premiers systèmes ne dépendent d'aucune décision de l'assuré.
    assert "retraite jusqu'à" in texte
    assert texte.count("retraite jusqu'à") == 1
    # Sous la barre, le plancher puis ce qui s'y ajoute, et à quelle condition.
    assert "de rente capitalisée obligatoire" in texte
    assert "par mois sans rien ajouter" in plat
    assert "de plus si vous placez les cinq points rendus, sans risque" in plat
    # Le dépliant du pilier dit ce que chacune des deux sert.
    assert "que vous versez librement" in texte
    # Le chiffre de tête est le net plein, et la phrase le dit.
    assert "C'est votre salaire net plein" in plat
    assert "pas une retenue" in plat
    # La fiche de paie porte le placement SOUS le net, et ce qui reste après.
    assert "Placé volontairement sur un compte à votre nom" in texte
    assert "restant si vous les placez" in texte
    assert "ne sont sur la fiche de paie de personne" in plat


def test_la_proposition_se_compare_a_taux_egal_cotise(contexte):
    """Les 18 + 5 + 5 valent les 28 % d'aujourd'hui, et les pages le disent.

    C'est la raison d'être des cinq points volontaires : sans eux, le site
    opposerait deux systèmes qui ne coûtent pas le même prix.
    """
    base = contexte.base
    assert base.taux_retraite_propose == pytest.approx(
        round(pages.TAUX_ACTUEL_TOTAL, 2))
    programme = _prose(rendre("/", {})[1])
    assert "que personne ne vous impose" in programme
    # La ligne du total est une ligne de TABLEAU, que `_prose` retire : on la
    # cherche donc dans le corps rendu, et la phrase qui la commente en prose.
    cout = rendre("/cout", {})[1]
    assert "Total versé si les points rendus sont replacés" in cout
    assert "le simulateur, lui, montre la seconde ligne du total" in (
        _prose(cout).lower())
    methode = _prose(rendre("/methode", {})[1])
    assert "convention de comparaison" in methode


# LE MICRO-ENTREPRENEUR SAISI PAR SON CHIFFRE D'AFFAIRES (action 138, étape 12 ;
# fiche micro_social_abattement) : son activité abat le chiffre d'affaires de
# 71, 50 ou 34 % (L. 613-7, II), au seuil du modèle, dans la saisie du
# portage, la seule (action 161, étape 6) ; la Cipav route la période vers les
# régimes du libéral.
_MICRO = {"statut": "micro_entrepreneur", "naissance": "1975", "debut": "2009-01",
          "unite_revenu": "euros_mois", "salaire": "3000"}


@pytest.mark.parametrize("micro,statut,part", [
    ("", "micro_entrepreneur", 1.0), ("vente", "micro_entrepreneur", 0.29),
    ("services", "micro_entrepreneur", 0.50), ("liberal", "micro_entrepreneur", 0.66),
    ("cipav", "profession_liberale", 0.66),
])
def test_le_chiffre_d_affaires_s_abat_selon_l_activite(micro, statut, part):
    saisie = saisie_du_portage({**_MICRO, "micro": micro})
    echelle = site().contexte.echelle(saisie)
    [metier] = saisie.parcours(echelle)
    assert metier.affiliation == statut
    assert metier.niveau_salaire == pytest.approx(echelle.niveau(3000.0) * part)


def test_l_activite_du_micro_entrepreneur_revient_dans_l_adresse():
    champs = {**_MICRO, "micro": "cipav"}
    assert "micro=cipav" in saisie_du_portage(champs).requete()
    assert "micro" not in dict(parse_qsl(saisie_du_portage(_MICRO).requete()))
    # Une activité inconnue retombe, comme tout menu, sur le défaut.
    assert saisie_du_portage({**_MICRO, "micro": "agricole"}).micro == ""


def test_le_chiffre_d_affaires_ne_se_convertit_pas_en_net():
    """Ni brut ni net : en mode net, le chiffre d'affaires se lit tel quel, et
    seule la ligne salariée remonte au brut."""
    champs = {**_MICRO, "micro": "vente", "montants": "net",
              "metier2_debut": "2020-01", "metier2_statut": "salarie_prive_non_cadre",
              "metier2_salaire": "3000"}
    saisie = saisie_du_portage(champs)
    echelle = site().contexte.echelle(saisie)
    micro, salarie = saisie.parcours(echelle)
    assert micro.niveau_salaire == pytest.approx(echelle.niveau(3000.0) * 0.29)
    assert salarie.niveau_salaire > echelle.niveau(3000.0)


def test_un_chiffre_d_affaires_trop_petit_se_refuse_en_chiffre_d_affaires():
    saisie = saisie_du_portage({**_MICRO, "micro": "vente", "salaire": "1000"})
    with pytest.raises(ErreurSite,
                       match=refus_de_la_saisie("Ce chiffre d'affaires, abattu à 29 %")):
        saisie.parcours(site().contexte.echelle(saisie))


# L'INDICE MAJORÉ (action 138, étape 10 ; registre, `simulateur_sud_education`,
# chantier 138.10) : le fonctionnaire titulaire, civil ou militaire, de l'État,
# de la territoriale ou de l'hospitalière dit le revenu de ses périodes par
# l'indice majoré de son bulletin de paie. Son traitement brut est cet indice
# fois la valeur du point, 5 907,34 € par an pour cent points en 2026 (décret
# n° 85-1148 du 24 octobre 1985, article 3) ; ses primes s'y ajoutent, à la part
# que la saisie en dit, que le traitement laisse (1 − part). L'indice 500 vaut
# ainsi 2 461,39 € bruts par mois, 3 076,74 € avec 20 % de primes ; l'indice
# 600, 2 953,67 € : posés à la main.
_INDICE = {"statut": "fonctionnaire_etat", "naissance": "1975", "debut": "1998-09",
           "unite_revenu": "euros_mois", "montants": "brut", "indice": "majore",
           "salaire": "500"}


@pytest.mark.parametrize("champs,mensuel", [
    ({}, 2461.39),
    ({"primes": "0.2"}, 3076.74),
    ({"statut": "fonctionnaire_territorial_hospitalier"}, 2461.39),
    ({"statut": "militaire_officier"}, 2461.39),
    # Ni brut ni net, et sans unité : l'indice se lit tel quel.
    ({"montants": "net"}, 2461.39),
    ({"unite_revenu": "moyen"}, 2461.39),
], ids=["etat", "primes", "territorial", "militaire", "net", "multiples"])
def test_l_indice_majore_vaut_le_traitement_qu_il_paie(champs, mensuel):
    saisie = saisie_du_portage({**_INDICE, **champs})
    echelle = site().contexte.echelle(saisie)
    [metier] = saisie.parcours(echelle)
    assert metier.niveau_salaire == pytest.approx(echelle.niveau(mensuel), rel=1e-5)


def test_seules_les_periodes_payees_a_l_indice_le_lisent():
    """Le salarié et l'agent non titulaire gardent leurs euros ; le fonctionnaire
    territorial qui suit lit le sien."""
    saisie = saisie_du_portage({
        **_INDICE,
        "metier2_debut": "2008-01", "metier2_statut": "salarie_prive_cadre",
        "metier2_salaire": "4000",
        "metier3_debut": "2014-01", "metier3_statut": "contractuel_public",
        "metier3_salaire": "2500",
        "metier4_debut": "2018-01", "metier4_statut": "fonctionnaire_territorial_hospitalier",
        "metier4_salaire": "600",
    })
    echelle = site().contexte.echelle(saisie)
    niveaux = [metier.niveau_salaire for metier in saisie.parcours(echelle)]
    assert niveaux == pytest.approx(
        [echelle.niveau(mensuel) for mensuel in (2461.39, 4000.0, 2500.0, 2953.67)],
        rel=1e-5)


def test_les_statuts_payes_a_l_indice_sont_ceux_de_l_etat_et_de_la_cnracl():
    """La liste de la saisie se recoupe aux affiliations : les statuts dont le
    régime de base est, l'année du modèle, celui de l'État ou la CNRACL. Ni
    l'ouvrier de l'État (FSPOEIE), ni le fonctionnaire de Nouvelle-Calédonie,
    ni l'agent non titulaire."""
    parametres = Parametres()
    affiliations = Affiliations(parametres.racine_donnees)
    attendus = {code for code in affiliations.codes
                if {"fonction_publique_etat", "cnracl"}
                & set(affiliations.regimes(code, parametres.annee_courante))}
    assert len(attendus) == 12
    assert set(SAISIE.STATUTS_A_L_INDICE) == attendus


def test_un_indice_hors_des_bornes_se_refuse_en_indice():
    """Le refus redit les bornes du revenu en indices, le nombre que le champ
    porte ; les deux indices qu'il nomme passent, leurs voisins non."""
    saisie = saisie_du_portage({**_INDICE, "salaire": "50"})
    echelle = site().contexte.echelle(saisie)
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("Cet indice majoré")) as refus:
        saisie.parcours(echelle)
    bornes = re.search(r"soit un indice majoré de ([\d ]+) à ([\d ]+)",
                       str(refus.value))
    assert bornes, str(refus.value)
    bas, haut = (int(borne.replace(" ", "")) for borne in bornes.groups())
    for indice in (bas, haut):
        saisie_du_portage({**_INDICE, "salaire": str(indice)}).parcours(echelle)
    for indice in (bas - 1, haut + 1):
        with pytest.raises(ErreurSite, match=refus_de_la_saisie("Cet indice majoré")):
            saisie_du_portage({**_INDICE, "salaire": str(indice)}).parcours(echelle)
    with pytest.raises(ErreurSite, match=refus_de_la_saisie("indice majoré")):
        saisie_du_portage({**_INDICE, "salaire": "0"})


def test_l_indice_majore_revient_dans_l_adresse():
    assert "indice=majore" in saisie_du_portage(_INDICE).requete()
    sans = {cle: valeur for cle, valeur in _INDICE.items() if cle != "indice"}
    assert "indice" not in dict(parse_qsl(saisie_du_portage(sans).requete()))
    # Un choix inconnu retombe, comme tout menu, sur le défaut.
    assert saisie_du_portage({**_INDICE, "indice": "brut"}).indice == ""


def test_l_activite_d_apres_le_depart_d_un_fonctionnaire_se_dit_en_indice():
    """Sans revenu à elle, elle prend celui du dernier métier : un indice, qui
    vaut son traitement, et non autant d'euros."""
    saisie = saisie_du_portage({**_INDICE, "liquidation": "2039-10",
                                "emploi_retraite": "2040-01",
                                "emploi_retraite_fin": "2041-01"})
    echelle = site().contexte.echelle(saisie)
    emploi = saisie.emploi_retraite_declare(echelle)
    assert emploi.niveau_salaire == pytest.approx(echelle.niveau(2461.39), rel=1e-5)


def test_le_menu_de_l_indice_ne_parait_qu_avec_une_periode_payee_a_l_indice():
    """Comme celui du micro-entrepreneur : avec une période de fonctionnaire, ou
    un choix déjà dit, que le formulaire garde d'une saisie à l'autre."""
    sans = {cle: valeur for cle, valeur in _INDICE.items() if cle != "indice"}
    sans["salaire"] = "2800"
    assert 'name="indice"' in rendre("/simuler", sans)[1]
    salarie = {**sans, "statut": "salarie_prive_non_cadre"}
    assert 'name="indice"' not in rendre("/simuler", salarie)[1]
    assert 'name="indice"' in rendre("/simuler", {**salarie, "indice": "majore"})[1]


def test_le_champ_du_fonctionnaire_demande_son_indice_et_en_dit_le_traitement():
    corps = rendre("/simuler", {**_INDICE, "primes": "0.2"})[1]
    assert "Saisie refusée" not in corps
    assert re.search(r'<label for="salaire">Indice majoré', corps)
    # Le traitement de l'indice 500 au point de 2026, et la rémunération que la
    # part de primes en tire.
    assert "traitement de 2 461 € bruts par mois" in corps
    assert "3 077 € primes comprises" in corps


def _lien_des_montants(corps):
    bloc = re.search(r'<div class="bascule"[^>]*aria-label="Montants".*?</div>',
                     corps, re.S)
    assert bloc, "la bascule des montants a disparu"
    lien = re.search(r'href="\./#([^"]*)"', bloc.group(0))
    return dict(parse_qsl(html.unescape(lien.group(1))))


def test_les_bascules_laissent_l_indice_tel_quel():
    """Un indice n'a ni unité, ni brut, ni net : les deux bascules le passent tel
    quel, et traduisent le revenu des autres périodes."""
    champs = {**_INDICE, "metier2_debut": "2010-01",
              "metier2_statut": "salarie_prive_cadre", "metier2_salaire": "4000"}
    vers_les_multiples, _ = _lien_de_bascule(champs)
    assert vers_les_multiples["unite_revenu"] == "moyen"
    assert vers_les_multiples["salaire"] == "500"
    assert float(vers_les_multiples["metier2_salaire"]) == pytest.approx(
        _echelle().niveau(4000.0), abs=0.001)
    vers_le_net = _lien_des_montants(rendre("/simuler", champs)[1])
    assert vers_le_net["montants"] == "net"
    assert vers_le_net["salaire"] == "500"
    assert float(vers_le_net["metier2_salaire"]) < 4000


def test_le_revenu_que_la_pension_suppose_se_dit_en_indice():
    """Saisi par sa pension, le fonctionnaire lit l'indice que le revenu trouvé
    suppose, au point de l'année, et le lien de reprise l'écrit."""
    corps = rendre("/simuler", {**_INDICE, "naissance": "1958-03-15",
                                "debut": "1981-09", "liquidation": "2021-04",
                                "saisie_par": "pension", "pension": "2200"})[1]
    assert "Saisie refusée" not in corps
    phrase = re.search(r"Soit l&#x27;indice majoré ([\d ]+)|Soit l'indice majoré "
                       r"([\d ]+)", corps)
    assert phrase, "le revenu déduit ne dit pas son indice"
    indice = int(next(groupe for groupe in phrase.groups() if groupe).replace(" ", ""))
    reprise = re.search(r'<a href="\./#([^"]*)">Reprendre cette carrière', corps)
    suite = dict(parse_qsl(html.unescape(reprise.group(1))))
    assert suite["saisie_par"] == "revenu"
    assert int(suite["salaire"]) == indice


# LA DATE D'ENTRÉE DANS LA SAISIE EN NET (action 138, étape 9 ; note « la date
# d'entrée dans la fiche de paie ») : un régime fermé ne l'est qu'aux nouveaux
# entrants, et la saisie ne déclare un statut fermé qu'avant sa fermeture. Le
# net remonte donc au brut par la fiche de la date d'entrée dans le statut, que
# la carrière datera : l'ouverture du premier métier qui le porte, ou janvier de
# la première année du relevé. Celle de l'agent de la SNCF entré avant 2020 (loi
# du 27 juin 2018) retient 10,85 % du traitement, puis la CSG, 9,2 %
# (L. 136-8, I, 1°), et la CRDS, 0,5 % (ordonnance n° 96-50, art. 19), sur
# 98,25 % (L. 136-1-1, III, 1°) : 2 653,99 € nets par mois font 3 333,33 €
# bruts, posés à la main. Sans la date, la saisie remontait par la fiche d'un
# nouvel entrant, celle d'un salarié du privé : 3 352,62 €.
_PART_NETTE_SNCF = 1.0 - 0.1085 - (0.092 + 0.005) * 0.9825
_NET_SNCF = f"{40_000.0 * _PART_NETTE_SNCF / 12:.2f}"
_SNCF = {"naissance": "1975", "statut": "agent_sncf", "debut": "1996-09",
         "unite_revenu": "euros_mois", "montants": "net", "salaire": _NET_SNCF}


def _bruts(champs):
    """Le revenu de chaque métier, remonté au brut mensuel."""
    saisie = saisie_du_portage(champs)
    echelle = site().contexte.echelle(saisie)
    return [echelle.mensuel(niveau) for niveau in saisie.niveaux(echelle)]


def test_le_net_remonte_au_brut_par_la_fiche_de_la_date_d_entree():
    """L'agent de la SNCF entré en 1996 ; celui qui y entre en 2015, après
    dix-huit ans dans le privé, dont seul le métier de la SNCF remonte par sa
    retenue ; l'activité exercée après le départ dans le même statut."""
    assert _bruts(_SNCF) == pytest.approx([3333.33], abs=0.01)
    [prive] = _bruts({**_SNCF, "statut": "salarie_prive_non_cadre"})
    assert _bruts({**_SNCF, "statut": "salarie_prive_non_cadre",
                   "metier2_debut": "2015-01", "metier2_statut": "agent_sncf",
                   "metier2_salaire": _NET_SNCF}) == pytest.approx([prive, 3333.33], abs=0.01)
    saisie = saisie_du_portage({**_SNCF, "liquidation": "62", "emploi_retraite": "63",
                                "emploi_retraite_fin": "65"})
    echelle = site().contexte.echelle(saisie)
    emploi = saisie.emploi_retraite_declare(echelle)
    assert echelle.mensuel(emploi.niveau_salaire) == pytest.approx(3333.33, abs=0.01)


def test_le_liberal_non_reglemente_remonte_par_la_fiche_de_son_installation():
    """Le statut reste ouvert, mais le régime change à l'installation : le
    libéral non réglementé installé avant le 1er janvier 2019 « reste
    affilié » à la CNAVPL et à la Cipav (loi n° 2017-1836, art. 15), et son
    net remonte par la fiche de la profession libérale réglementée, qui les a
    aussi ; installé depuis, il relève du régime général et du RCI, comme un
    commerçant (L. 640-1, rédaction du 1er janvier 2018)."""
    champs = {"naissance": "1985", "unite_revenu": "euros_mois", "montants": "net",
              "salaire": "3000"}

    def brut(statut, debut):
        [mensuel] = _bruts({**champs, "statut": statut, "debut": debut})
        return mensuel

    assert brut("liberal_non_reglemente", "2018-12") == pytest.approx(
        brut("profession_liberale", "2018-12"), abs=0.01)
    assert brut("liberal_non_reglemente", "2019-01") == pytest.approx(
        brut("commercant", "2019-01"), abs=0.01)
    assert brut("profession_liberale", "2018-12") != pytest.approx(
        brut("commercant", "2019-01"), abs=1.0)


@pytest.mark.parametrize("champs", [
    {"naissance": "1975", "statut": "agent_sncf", "debut": "1996-09"},
    {"naissance": "1975", "statut": "salarie_prive_non_cadre", "debut": "1996-09",
     "metier2_debut": "2015-01", "metier2_statut": "agent_sncf"},
    # La ligne du micro-entrepreneur de la Cipav porte l'affiliation du libéral.
    {"naissance": "1985", "statut": "micro_entrepreneur", "micro": "cipav",
     "debut": "2009-01", "metier2_debut": "2020-01",
     "metier2_statut": "profession_liberale"},
    {"naissance": "1975", "liquidation": "62",
     "releve": ",".join(f"{annee}:agent_sncf:30000:4" for annee in range(1996, 2026))},
], ids=["un-metier", "deux-metiers", "micro-cipav", "releve"])
def test_la_saisie_date_l_entree_comme_la_carriere(champs):
    """La date d'entrée que la saisie donne à la fiche est celle que la
    carrière bâtie de la même saisie retient, affiliation par affiliation."""
    saisie = saisie_du_portage({**champs, "unite_revenu": "moyen", "salaire": "1"})
    carriere = site().contexte.carriere(saisie)
    for code in {ligne.affiliation for ligne in carriere.lignes}:
        attendue, lue = carriere.date_entree(code), saisie.date_entree(code)
        assert (lue.annee, lue.mois) == (attendue.annee, attendue.mois), code


def test_le_releve_date_l_entree_de_l_activite_apres_le_depart():
    """Sur un relevé, l'entrée est la première année qui porte le statut,
    comme la carrière la date, et non le métier du formulaire, que le relevé
    remplace : l'agent de la SNCF depuis 1996 qui travaille après son départ
    dans le même statut y garde sa retenue."""
    releve = ",".join(f"{annee}:agent_sncf:30000:4" for annee in range(1996, 2026))
    saisie = saisie_du_portage({
        "naissance": "1975", "liquidation": "62", "releve": releve,
        "unite_revenu": "euros_mois", "montants": "net", "emploi_retraite": "63",
        "emploi_retraite_fin": "65", "emploi_retraite_statut": "agent_sncf",
        "emploi_retraite_salaire": _NET_SNCF})
    echelle = site().contexte.echelle(saisie)
    emploi = saisie.emploi_retraite_declare(echelle)
    assert echelle.mensuel(emploi.niveau_salaire) == pytest.approx(3333.33, abs=0.01)


def test_un_releve_illisible_se_refuse_aussi_en_net():
    """La date d'entrée se lit dans le relevé, que le champ du revenu convertit
    avant que la simulation ne le refuse : illisible, il ne date rien, et la
    page dit son refus au lieu de tomber."""
    corps = rendre("/simuler", {**_SNCF, "liquidation": "62", "releve": "1996:agent_sncf"})[1]
    assert "Saisie refusée" in corps


def test_la_page_traduit_le_net_par_la_fiche_de_la_date_d_entree():
    """Ce que la page dit du net de l'agent de la SNCF entré en 1996 : le lien
    vers le brut porte 3 333 € pour 2 654 € nets, celui qui en revient
    2 654 €, et les repères du champ sont les nets de sa fiche — le SMIC et le
    salaire moyen, moins sa retenue, la CSG et la CRDS."""
    corps = html.unescape(rendre("/simuler", {**_SNCF, "salaire": "2654"})[1])
    lien = re.search(r'<a href="\./#([^"]*)">brut</a>', corps)
    assert lien, "la page ne porte pas de branche « brut »"
    vers_brut = dict(parse_qsl(lien.group(1)))
    assert vers_brut["salaire"] == "3333"
    retour = html.unescape(rendre("/simuler", vers_brut)[1])
    lien = re.search(r'<a href="\./#([^"]*)">net avant impôt</a>', retour)
    assert lien, "la page ne porte pas de branche « net »"
    assert dict(parse_qsl(lien.group(1)))["salaire"] == "2654"
    reperes = re.search(r"Repères : SMIC ([^€]+)€, salaire moyen ([^€]+)€", corps)
    assert reperes, "le champ du revenu ne donne plus ses repères"
    smic, moyen = (int(re.sub(r"\D", "", chiffre)) for chiffre in reperes.groups())
    echelle = site().contexte.echelle(saisie_du_portage(_SNCF))
    assert smic == round(echelle.smic * _PART_NETTE_SNCF)
    assert moyen == round(echelle.mensuel(1) * _PART_NETTE_SNCF)


# LES DATES DE PENSION DU FORMULAIRE (action 138, étape 9 ; note « la date
# d'entrée dans la saisie en net », « Trouvé en chemin ») : le formulaire
# propose la date de chaque pension de base que la carrière porte, quand elle
# en porte plusieurs. Il la lit comme elle, sous l'affiliation de chaque
# métier, à la date d'entrée dans cette affiliation : le micro-entrepreneur
# des professions que la Cipav garde relève de la CNAVPL et de la Cipav
# (D. 613-4, b ; fiche micro_social_abattement), et le libéral non réglementé
# affilié avant le 1er janvier 2019 à la CNAVPL et à la Cipav « reste
# affilié » à ces régimes (loi n° 2017-1836, art. 15), même si un second
# métier du formulaire dit, en 2020, que son revenu change.
@pytest.mark.parametrize("champs, pensions", [
    # De 2009 à 2014 à la Cipav, salarié ensuite : la CNAVPL, puis le régime
    # général. Le formulaire proposait le RSI, le régime du statut.
    ({"statut": "micro_entrepreneur", "micro": "cipav", "debut": "2009-01",
      "metier2_debut": "2015-01", "metier2_statut": "salarie_prive_non_cadre"},
     ["cnavpl", "regime_general"]),
    # Installé en 2010, un revenu qui change en 2020 : la CNAVPL seule, dont
    # le départ dit la date. Le formulaire datait le second métier de 2020,
    # et proposait aussi le régime général.
    ({"statut": "liberal_non_reglemente", "debut": "2010-01",
      "metier2_debut": "2020-01", "metier2_statut": "liberal_non_reglemente"},
     []),
], ids=["micro-cipav", "liberal-installe-en-2010"])
def test_le_formulaire_date_les_pensions_que_la_carriere_porte(champs, pensions):
    """Les champs de date des pensions, dans l'ordre des métiers. La naissance
    se déclare entière ; ni son jour ni le sexe ne changent les régimes."""
    corps = rendre("/simuler", {"naissance": "1985-03-15", **champs})[1]
    assert "Saisie refusée" not in corps
    assert 'id="progressive"' in corps, "le bloc des dates des pensions manque"
    assert re.findall(r'<input type="date" id="demande_(\w+)"', corps) == pensions
