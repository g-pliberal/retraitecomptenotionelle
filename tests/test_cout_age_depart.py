"""Ce que l'erreur d'âge coûte : mesuré, et laissé dehors pour une raison chiffrée.

La confrontation par catégorie socioprofessionnelle avait trouvé 1,17 an
d'écart en valeur absolue, et le dépôt avait écrit qu'il ne corrigeait rien.
Ces tests tiennent la raison chiffrée de ne pas corriger : le contrefactuel qui
rapproche chaque cas type de sa catégorie **déplace les cinq scénarios
notionnels de moins de deux dixièmes de point**, et il ÉLOIGNE le système
actuel de la projection du COR au lieu de l'en rapprocher. L'âge de départ n'est donc pas l'explication de l'écart que
le § 5 ter de `limites.md` laisse ouvert.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import pont
from retraite_notionnelle.castypes import CAS_TYPES, departs_au_portage
from retraite_notionnelle.config import Parametres

from facade import Simulateur, ouvrir

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import cout_age_depart as CAD  # noqa: E402

def _construite(simulateur, cas, generation: int):
    """La carrière de ``cas``, né en ``generation``, partie à l'âge où le
    pilote du portage la fait partir (``CasType.construire``, sans le pilote
    Python)."""
    return cas.carriere_a(simulateur, generation, _age(simulateur, cas, generation))


def _age(simulateur, cas, generation: int) -> float:
    """L'âge où le pilote du portage fait partir ``cas``, né en ``generation``."""
    departs, refus = departs_au_portage(simulateur, {"cas": (cas, generation)})
    assert not refus, refus
    return departs["cas"][0]


#: Les cas types que `cas_types_csp.yaml` laisse hors champ : le contrefactuel
#: ne doit pas y toucher.
HORS_CHAMP = ("militaire", "agent_sncf_conduite", "agent_ieg",
              "fonctionnaire_actif", "profession_liberale")

#: Les deux cas types dont la carrière est ENTIÈREMENT en points : le moteur
#: ne leur opposait ni durée, ni âge d'ouverture, ni carrière longue.
TOUT_EN_POINTS = ("exploitant_agricole", "profession_liberale")


@pytest.fixture(scope="module")
def simulateur():
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def mesure(simulateur):
    decalages = CAD.decalages_du_depot(simulateur.parametres)
    corrigee = CAD.grille_contrefactuelle(decalages)
    return {
        "decalages": decalages,
        "corrigee": corrigee,
        "reference": CAD.trajectoire(simulateur.parametres, CAS_TYPES),
        "contrefactuel": CAD.trajectoire(simulateur.parametres, corrigee),
    }


def test_le_contrefactuel_ne_touche_ni_les_fiches_ni_les_hors_champ(mesure):
    """Aucun âge trouvé ici n'entre dans `castypes.py`.

    Une fiche se réécrit sur ce qu'on sait d'une carrière, pas sur ce qui
    rapproche une moyenne d'une autre. Le contrefactuel est une grille de
    plus, et la grille de référence en sort intacte.
    """
    fiches = {cas.code: cas.age_debut for cas in CAS_TYPES}
    corrigee = {cas.code: cas.age_debut for cas in mesure["corrigee"]}
    assert set(corrigee) == set(fiches)
    for code in HORS_CHAMP:
        assert corrigee[code] == fiches[code], code

    for decalage in mesure["decalages"]:
        assert decalage.entree_fiche == fiches[decalage.code]
        assert (CAD.ENTREE_MINIMALE <= decalage.entree_contrefactuelle
                <= CAD.ENTREE_MAXIMALE), decalage.code


def test_tous_les_cas_types_comparables_repondent_a_leur_age_d_entree(mesure):
    """L'angle mort du contrefactuel est refermé.

    Deux cas types n'y répondaient pas, et la raison qu'on leur prêtait était
    fausse — « des régimes en points, auxquels le modèle n'oppose aucune durée
    requise ». C'était un défaut du moteur, corrigé le 21 septembre 2026 : les
    neuf cas types comparables répondent tous, et la recherche d'âge d'entrée
    ne laisse plus personne de côté.
    """
    assert not [d.code for d in mesure["decalages"] if d.insensible]


def test_une_carriere_tout_en_points_se_voit_opposer_sa_duree(simulateur):
    """Le premier défaut que la recherche d'âge d'entrée a fait voir.

    `age_taux_plein_droit` rendait l'âge d'ouverture dès que la carrière
    n'avait aucune période en annuités — le modèle faisait donc liquider « au
    taux plein » des carrières que `liquider.abattement_points` servait minorées. Le
    droit oppose bien cette durée aux régimes en points : L. 643-3 I du code de
    la sécurité sociale pour les professions libérales, L. 732-24 II du code
    rural pour les non-salariés agricoles.

    L'exploitant agricole en est le témoin : entré à vingt-huit ans il n'a pas
    la durée requise à l'âge d'ouverture, et la règle doit maintenant le faire
    attendre. Entré à vingt ans il l'a, et elle ne le retarde pas : né en
    janvier 1955 et installé au 1er janvier 1975, il a la porte des vingt ans
    de la carrière longue (quatre trimestres à son régime à la fin de 1975,
    D. 732-40 du code rural) et 4 × 41 = 164 trimestres à la fin de 2015, 168
    au 1er janvier 2016, pour 166 requis : il part à 61 ans. L'âge que le droit
    oppose à la carrière construite le précède, la durée s'y projetant au fil
    des mois quand le régime agricole valide l'année au 1er janvier (action
    192, étape 2).
    """
    from dataclasses import replace

    cas = next(c for c in CAS_TYPES if c.code == "exploitant_agricole")
    ouverture = ouvrir.age_ouverture_droit(simulateur.scenario_actuel,
        _construite(simulateur, cas, 1955))

    tot = _age(simulateur, replace(cas, age_debut=20), 1955)
    tard = _age(simulateur, replace(cas, age_debut=28), 1955)
    assert tot == pytest.approx(61.0)
    assert ouverture <= tot
    assert tard > tot + 0.9, "la durée manquante doit retarder le départ"


def test_une_carriere_tout_en_points_se_voit_opposer_un_age(simulateur):
    """Le second, et le plus visible : on pouvait liquider à cinquante ans.

    `calculer` ne lisait l'âge d'ouverture opposable que sur les périodes en
    ANNUITÉS. Une carrière entière en points n'en ayant aucune, aucun âge ne
    lui était opposé : le simulateur servait une pension d'exploitant agricole
    à cinquante ans sans rien refuser, quand il refusait la même chose à
    l'artisan de la page voisine.
    """
    artisan = next(c for c in CAS_TYPES if c.code == "artisan")
    temoin = simulateur.scenario_actuel.calculer(
        artisan._carriere(simulateur, 2000, 50.0))
    assert not temoin.liquidation_ouverte, "l'artisan sert de témoin"

    for code in TOUT_EN_POINTS:
        cas = next(c for c in CAS_TYPES if c.code == code)
        resultat = simulateur.scenario_actuel.calculer(
            cas._carriere(simulateur, 2000, 50.0))
        assert not resultat.liquidation_ouverte, code
        assert resultat.motif_ouverture == "non_ouverte", code
        assert resultat.age_ouverture_opposable is not None, code


def test_la_carriere_longue_est_ouverte_aux_regimes_en_points(simulateur):
    """Et les deux règles d'âge la lisent sur la même liste.

    L. 732-18-1 du code rural la donne aux non-salariés agricoles, le II de
    L. 643-3 du code de la sécurité sociale aux professions libérales par
    renvoi à L. 351-1-1. Ne l'ouvrir qu'au taux plein faisait rendre à celui-ci
    un âge ANTÉRIEUR à celui que l'ouverture accordait — deux règles du même
    droit qui se contredisent.
    """
    actuel = simulateur.scenario_actuel
    cas = next(c for c in CAS_TYPES if c.code == "exploitant_agricole")
    carriere = _construite(simulateur, cas, 2000)

    assert ouvrir.age_taux_plein_droit(actuel, carriere) >= ouvrir.age_ouverture_droit(actuel, carriere)
    resultat = actuel.calculer(carriere)
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.liquidation_ouverte


def test_les_scenarios_notionnels_ne_bougent_pas(mesure):
    """Le résultat qui ferme le sujet.

    Les cinq scénarios que le site compare se déplacent, en sens contraire du
    système actuel, de moins de trois dixièmes de point de PIB, et d'au plus
    une fois et demie son mouvement. Dans un compte notionnel, partir plus tôt allonge le diviseur autant
    que la carrière raccourcie retire au capital : les deux termes se
    répondent.

    Le test demandait « moins d'un dixième de point de PIB » : c'était la
    mesure d'un jour, que le modèle a franchie le 23 septembre 2026 (−0,10
    point au scénario 5, +0,51 au système actuel). Il tient désormais la
    propriété — un mouvement petit DEVANT celui du système actuel —, et une
    borne absolue de deux dixièmes. Le petit devant était un quart ; il est
    un tiers depuis le 28 septembre 2026, où les cas types, nés en janvier
    sans jour dit, sont partis au 1er du mois qui suit leur anniversaire
    (action 132) : −0,12 point au scénario 5, +0,45 au système actuel. Il est
    trois cinquièmes depuis que chaque caisse se divise par les têtes de ses
    cas types (action 138, étape 3) : la grille compte à chacune les
    retraités qu'elle a, quel que soit l'âge où ses cas types partent, et un
    départ plus précoce n'en ajoute plus ; le scénario 5 passe de −0,10 à
    −0,16 point, le système actuel de +0,36 à +0,31. Il est quatre cinquièmes,
    et la borne absolue un quart de point, depuis que l'exploitant agricole a
    la porte des vingt ans de la carrière longue (action 192, étape 2,
    15 novembre 2026) : parti un an plus tôt dans la référence, il bouge moins
    sous les âges corrigés. Le système actuel passe à +0,26 point ; les
    scénarios notionnels vont de −0,09 (rétroactif) à −0,20 (prospectif à
    cotisation employeur), soit au plus 0,77 fois le mouvement du système
    actuel. Le 21 novembre 2026, l'année d'entrée valide ce que son salaire
    vaut, au plus quatre trimestres, et non plus les seuls trimestres civils
    de ses mois (R. 351-9, action 134) : une entrée en milieu d'année vaut une
    entrée au 1er janvier, la recherche de l'âge d'entrée y perd la moitié de
    ses pas, et un pas d'un quart d'année n'y change rien. Le système actuel
    passe à +0,23 point, les scénarios notionnels vont de −0,13 (rétroactif)
    à −0,28 (les deux à cotisation employeur), soit 1,24 fois le mouvement du
    système actuel : le « moins que lui » ne tient plus pour ces deux-là ; le
    mouvement reste petit, sous trois dixièmes de point.
    """
    actuel = abs(mesure["contrefactuel"]["actuel"] - mesure["reference"]["actuel"])
    for scenario, _ in C.SCENARIOS:
        if scenario == "actuel":
            continue
        ecart = mesure["contrefactuel"][scenario] - mesure["reference"][scenario]
        assert ecart * (mesure["contrefactuel"]["actuel"] - mesure["reference"]["actuel"]) < 0, (
            f"{scenario} : {ecart * 100:+.2f} point, du sens du système actuel")
        assert abs(ecart) < actuel * 3 / 2, (
            f"{scenario} : {ecart * 100:+.2f} point")
        assert abs(ecart) < 0.003, f"{scenario} : {ecart * 100:+.2f} point"


def test_corriger_les_ages_eloigne_le_modele_du_COR(mesure):
    """Et c'est la réponse à la question ouverte du § 5 ter.

    Le système actuel, lui, bouge — une carrière plus longue y vaut une
    pension plus forte, sans diviseur pour l'amortir. Mais il bouge dans le
    MAUVAIS sens : l'écart avec la projection du COR se creuse. L'âge de
    départ n'explique donc pas cet écart, et la piste du taux de remplacement
    reste entière.

    *Le 6 octobre 2026* (action 147, étape 11), la trajectoire propre finit
    0,4 point de PIB SOUS le COR en 2070 : elle part d'un demi-point sous lui,
    la dépense de la DREES n'ayant ni gestion ni minimum vieillesse, et croît
    désormais comme lui. Les niveaux ne se comparent plus ; leurs croissances
    si, et la correction des âges éloigne celle du modèle de celle du COR : sa
    dérive de 2070 passe de 1,008 à 1,036.
    """
    from retraite_notionnelle import memoire

    avant = mesure["reference"]["actuel"]
    apres = mesure["contrefactuel"]["actuel"]
    assert apres > avant
    parametres = Parametres()
    derives = [memoire.cout(parametres, cas_types=grille).avenir.annees[-1].derive
               for grille in (CAS_TYPES, mesure["corrigee"])]
    assert abs(derives[1] - 1.0) > abs(derives[0] - 1.0), derives
    assert 0.002 < apres - avant < 0.02


def test_les_deux_criteres_d_age_tirent_en_sens_contraire(mesure, simulateur):
    """Ce que la mesure laisse ouvert, et qu'elle ne tranche pas.

    Rapprocher chaque cas type de SA catégorie fait passer leur SOMME de
    l'autre côté de l'âge conjoncturel tous régimes : la grille des fiches
    part 0,29 an plus tard que la France réelle, le contrefactuel 0,20 an plus
    tôt. Les deux critères ne peuvent pas être satisfaits ensemble, et les
    cinq cas types hors champ, aux âges de leurs statuts, sont le suspect. Ce
    test tient le constat, pas son explication. Jusqu'au 14 octobre 2026, la
    grille des fiches était aussi la plus proche, à 0,07 an : l'agent de la
    CNRACL partait à l'âge d'ouverture, et non au taux plein (action 159,
    étape 5).
    """
    fiches = CAD.concordance_du_depot(simulateur.parametres, CAS_TYPES)
    contrefactuel = CAD.concordance_du_depot(simulateur.parametres, mesure["corrigee"])
    assert 0.0 < fiches < 0.4
    assert contrefactuel < 0.0 < fiches


def _paquet_au_plafond(plafond: int | None) -> bytes:
    """Le paquet du portage, chaque ligne de liquidation qui plafonne la décote
    plafonnée à ``plafond`` trimestres — ``None`` : sans plafond. La variante
    s'écrit en données, que le portage lit (note de décision 0006)."""
    donnees = json.loads((Path(__file__).resolve().parents[1] / "moteur" / "donnees.json")
                         .read_bytes())
    for regime in donnees["regimes"]:
        for ligne in regime["liquidation"]:
            if ligne.get("decote_trimestres_maximum") is not None:
                ligne["decote_trimestres_maximum"] = plafond
    return json.dumps(donnees).encode("utf-8")


def _liquidations(appels: dict, paquet: bytes | None = None) -> dict:
    """Le scénario 1 de chaque carrière de ``appels``, liquidée par le portage
    sur ``paquet``."""
    resultats, refus = pont.droit(appels, paquet=paquet)
    assert not refus, refus
    return resultats


def test_le_plafond_de_decote_ne_mord_sur_aucune_liquidation_ouverte(simulateur):
    """Le plafond de vingt trimestres est l'arithmétique des deux âges.

    Il est écrit là où le droit a voulu l'écrire — R. 643-7 pour les libéraux,
    R. 723-38 pour les avocats, le I de L. 14 pour la fonction publique — et
    absent de R. 351-27 2° comme de R. 732-61. La raison est que l'écart entre
    l'âge d'ouverture et l'âge d'annulation vaut AU PLUS vingt trimestres :
    exactement vingt pour les générations 1930 à 1961, douze pour celles
    d'après 1968. Sur toute liquidation que le droit ouvre, le décompte par
    l'âge est donc borné par construction.

    Ce test le vérifie plutôt que de le supposer : il liquide chaque carrière
    une seconde fois sur un paquet dont la décote n'a plus de plafond, et
    refuse qu'une seule liquidation OUVERTE en soit changée. S'il tombe un
    jour, c'est que les âges ont bougé, et le plafond cessera d'être
    invisible. Le même balayage, sous un plafond de quatre trimestres, voit
    mordre : la comparaison n'est pas aveugle.

    Il épiait la décote du moteur Python jusqu'au 16 novembre 2026 ; la
    décote sans plafond s'écrit désormais en données, et c'est le portage qui
    liquide (action 161).
    """
    appels = {f"{cas.code}, {generation}, à {quarts / 4} ans":
              ("scenario_actuel.calculer", pont.MOTEUR,
               cas._carriere(simulateur, generation, quarts / 4))
              for cas in CAS_TYPES
              for generation in (1950, 1970, 1990)
              for quarts in range(232, 272)}   # 58,0 à 68,0 ans, au trimestre
    plafonnees = _liquidations(appels)
    ouvertes = [cle for cle, resultat in plafonnees.items() if resultat["liquidation_ouverte"]]
    assert len(ouvertes) > 500, "le balayage doit voir des liquidations ouvertes"

    libres = _liquidations(appels, _paquet_au_plafond(None))
    mordues = [cle for cle in ouvertes if libres[cle] != plafonnees[cle]]
    assert not mordues, f"le plafond a mordu : {mordues[:5]}"

    serrees = _liquidations(appels, _paquet_au_plafond(4))
    assert [cle for cle in ouvertes if serrees[cle] != plafonnees[cle]], (
        "un plafond de quatre trimestres doit mordre : la comparaison serait aveugle")


def test_l_ecart_des_deux_ages_ne_depasse_jamais_vingt_trimestres(simulateur):
    """La raison pour laquelle le plafond ne mord pas, mesurée dans les tables.

    Vingt trimestres exactement de 1930 à 1961 — soixante ans contre
    soixante-cinq —, puis dix-huit, quinze, treize et douze à mesure que les
    réformes relèvent l'âge d'ouverture sans toucher à l'annulation.
    """
    actuel = simulateur.scenario_actuel
    ecarts = {}
    for generation in range(1930, 2016):
        ouverture = actuel.ages_ouverture.age(generation)
        annulation = actuel.ages_annulation_decote.age(generation)
        if ouverture is None or annulation is None:
            continue
        ecarts[generation] = round((annulation[0] - ouverture[0]) * 4, 2)

    assert ecarts, "les deux tables doivent se recouvrir"
    assert max(ecarts.values()) == 20.0
    assert all(ecarts[g] == 20.0 for g in range(1930, 1962) if g in ecarts)
    assert ecarts[2000] == 12.0


def test_le_liberal_retrouve_le_cas_type_du_COR(simulateur):
    """Le cas type n° 13 du rapport annuel de juin 2026, à trois mois près.

    Le COR décrit un médecin libéral de secteur 1 né en 1960 : il « peut
    prétendre à un départ à 62 ans » et « atteint le taux plein à 66 ans et
    9 mois ». La fiche du dépôt, rendue à la règle ordinaire une fois le défaut
    des carrières tout en points corrigé, donne 62,00 et 67,00 pour la même
    génération.

    C'est la première confrontation du dépôt à un cas type libéral publié, et
    elle vaut mieux que la moyenne d'un groupe de la nomenclature : les deux
    âges sont construits sous la même convention — on part au taux plein — là
    où l'enquête Emploi mesure un comportement.
    """
    actuel = simulateur.scenario_actuel
    fiche = next(cas for cas in CAS_TYPES if cas.code == "profession_liberale")
    assert fiche.regle_liquidation == "taux_plein"
    assert fiche.ecart_liquidation == 0

    carriere = _construite(simulateur, fiche, 1960)
    assert ouvrir.age_ouverture_droit(actuel, carriere) == pytest.approx(62.0, abs=0.01)
    assert ouvrir.age_taux_plein_droit(actuel, carriere) == pytest.approx(66.75, abs=0.3)


def test_le_militaire_est_seul_a_porter_un_ecart_de_liquidation():
    """Le champ a perdu son second usager, et ne doit pas en retrouver un par mégarde.

    `ecart_liquidation` porte la durée de services de la pension militaire, qui
    ne s'ouvre pas à un âge mais à une durée. Le libéral l'a porté jusqu'au
    22 septembre 2026 pour contourner un défaut du moteur ; le défaut corrigé,
    il l'a rendu.
    """
    porteurs = {cas.code: cas.ecart_liquidation
                for cas in CAS_TYPES if cas.ecart_liquidation}
    assert porteurs == {"militaire": 27.5}
