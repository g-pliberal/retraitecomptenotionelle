"""Le système 1 au format de « Mon estimation retraite », sur le site.

Les départs que la synthèse officielle chiffre — au plus tôt, au taux plein, au
taux plein automatique — sont datés par le pilote
(:func:`~retraite_notionnelle.pilote.ages_de_l_estimation`), liquidés étage par
étage (``_depart_estime``, dans ``contexte.py``, et ``departEstime``, son
jumeau), et la page les montre en brut mensuel, étage par étage, le net en
second, à côté du total que le lecteur recopie de son estimation
(``estimationOfficielle``, ``moteur/js/pages.js``). Ces tests tiennent les deux
moteurs d'accord, les âges au droit, et la page à ce qu'elle promet. La saisie
est celle du portage, la seule (action 161, étape 6) : le Python date et
liquide les carrières qu'il bâtit, par le pont (:func:`_departs_du_pont`). Les
carrières sont fictives.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import replace
from functools import cache
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import _depart_estime
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.pilote import DEPARTS_DE_L_ESTIMATION, ages_de_l_estimation
from retraite_notionnelle.web.site import ErreurSite, module, site
from outils_pont import RefusDuPortage, refus_de_la_saisie, saisie_du_portage
from outils_web import montants_du_portage, page, saisies  # noqa: F401 — les fixtures partagées

RACINE = Path(__file__).resolve().parents[1]

#: Des carrières fictives qui traversent les cas du bloc : un départ légal
#: confondu avec le taux plein, trois âges distincts, la carrière longue, le
#: régime intégré et l'additionnel, les enfants, un petit salaire, un relevé,
#: deux métiers ; puis ceux qui n'ont aucun départ à chiffrer.
REQUETES = {
    "defaut": {},
    "trois_ages": {"naissance": "1968-05-01", "debut": "1990-09", "liquidation": "2032-01"},
    "carriere_longue": {"naissance": "1966-02-01", "debut": "1984-09",
                        "liquidation": "2030-01"},
    # La même, coupée de deux ans de chômage indemnisé, dont D. 351-1-2 répute
    # cotisés quatre trimestres, sous chaque état du droit.
    "carriere_longue_chomage": {"naissance": "1966-02-01", "debut": "1984-09",
                                "liquidation": "2030-01",
                                "interruptions": "2008:2009:chomage_indemnise"},
    "fonctionnaire": {"naissance": "1975-01-01", "statut": "fonctionnaire_etat",
                      "debut": "1998-09", "primes": "0.2"},
    "cadre": {"naissance": "1976-04-01", "statut": "salarie_prive_cadre", "debut": "1999-09"},
    "mere": {"naissance": "1980-06-01", "sexe": "F", "enfants": "3", "debut": "2003-09"},
    "petit_salaire": {"naissance": "1985-01-01", "debut": "2010-01",
                      "unite_revenu": "euros_mois", "salaire": "1100"},
    "releve": {"naissance": "1975-01-01", "liquidation": "2039-01", "releve": "\n".join(
        f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1997)}"
        for annee in range(1997, 2026))},
    # Le même relevé, prolongé jusqu'à chaque départ, mais coupé de chômage,
    # puis d'une période en Allemagne, que la prolongation respecte.
    "releve_interrompu": {"naissance": "1975-01-01", "liquidation": "2039-01",
                          "releve": "\n".join(
                              f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1997)}"
                              for annee in range(1997, 2026)),
                          "interruptions": "2028:2029:chomage_indemnise",
                          "etranger1_pays": "DE", "etranger1_debut": "2031-01",
                          "etranger1_fin": "2033-07", "etranger1_activite": "salariee"},
    # Un relevé qui s'arrête en 2018, d'un né en 1966 : prolongé, il atteint
    # la durée requise avant 67 ans ; arrêté, il ne le faisait jamais, et le
    # taux plein attendait l'âge où il est automatique.
    "releve_ancien": {"naissance": "1966-09-01", "releve": "\n".join(
        f"{annee}:salarie_prive_cadre:{30_000 + 900 * (annee - 1990)}"
        for annee in range(1990, 2019))},
    # Le départ anticipé des assurés handicapés, une incapacité d'au moins
    # 50 % depuis le premier emploi : il ouvre le premier départ, au taux plein.
    "handicap": {"naissance": "1975-01-01", "debut": "1996-01", "handicap": "1996-01"},
    "deux_metiers": {"unite_revenu": "euros_mois", "salaire": "2900",
                     "metier2_debut": "40", "metier2_statut": "artisan",
                     "metier2_salaire": "4200"},
    "parti": {"naissance": "1955-01-01", "liquidation": "2017-01"},
    "par_pension": {"situation": "retraite", "pension": "1500"},
    # La radiation pour invalidité ouvre la pension du fonctionnaire à tout
    # âge : la saisie date elle-même ce départ.
    "radiation": {"naissance": "1975", "statut": "fonctionnaire_etat",
                  "radiation_invalidite": "2010-06", "invalidite_imputable": "oui",
                  "taux_invalidite": "60", "metier2_debut": "2010-06",
                  "metier2_statut": "salarie_prive_non_cadre"},
    # Un métier qui commence après l'âge légal : la saisie refuse la carrière à
    # cet âge, avec ses mots, et le modèle n'est pas même interrogé.
    "metier_tardif": {"naissance": "1975-01-01", "debut": "1996-01", "liquidation": "2042-01",
                      "metier2_debut": "2039-06", "metier2_statut": "salarie_prive_cadre"},
}


def _au_depart(requete: dict, age: float) -> dict:
    """La requête liquidée à ``age`` : la saisie lit un âge nu, comme ceux des
    adresses d'avant le calendrier, à sa valeur exacte."""
    return {**requete, "liquidation": repr(age)}


def _departs_du_pont(saisies, requete: dict, droit: str | None = None) -> tuple:
    """Les départs que le Python date et chiffre, sous le droit contrefactuel
    ``droit`` s'il en nomme un : son pilote (``ages_de_l_estimation``), et sa
    liquidation de chaque départ (``_depart_estime``), sur la carrière que le
    portage bâtit de la requête à chaque âge, par le pont — ce que faisait
    ``Contexte.departs_de_l_estimation`` de la saisie Python. Vide où le bloc
    se tait, ce que la saisie du portage dit : une saisie par la pension, des
    pensions qu'elle date elle-même, un départ d'une année passée, une carrière
    que la saisie ou le modèle refusent à l'un des âges."""
    saisie = saisie_du_portage(requete)
    if (saisie.par_pension or saisie.demandes or saisie.invalidite is not None
            or saisie.radiation_invalidite is not None):
        return ()
    parametres = saisies.parametres(requete)
    if droit is not None:
        parametres = parametres.avec(droit_contrefactuel=droit)
    simulateur = saisies.simulateur(parametres)
    annee = parametres.annee_courante
    if saisie.date_liquidation.annee < annee:
        return ()

    @cache
    def batir(age: float):
        return saisies.carriere(_au_depart(requete, age))

    departs = []
    try:
        ages = ages_de_l_estimation(simulateur.scenario_actuel, batir, saisie.liquidation)
        for quoi, age in (ages or {}).items():
            if departs and abs(departs[-1].age - age) < 1e-9:
                departs[-1] = replace(departs[-1], quoi=departs[-1].quoi + (quoi,))
                continue
            carriere = batir(age)
            if carriere.annee_liquidation >= annee:
                departs.append(_depart_estime(simulateur, parametres, carriere, quoi))
    except (RefusDuPortage, ValueError):
        return ()
    return tuple(departs)


def _departs(saisies, nom: str):
    return _departs_du_pont(saisies, REQUETES[nom])


def _ecarts(obtenu, attendu, chemin: str, ecarts: list[str]) -> None:
    """Un milliardième au plus sur un nombre, comme les témoins ; rien ailleurs."""
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        if isinstance(attendu, dict) and isinstance(obtenu, dict):
            for cle in sorted(set(attendu) | set(obtenu)):
                _ecarts(obtenu.get(cle), attendu.get(cle), f"{chemin}.{cle}", ecarts)
        elif isinstance(attendu, list) and isinstance(obtenu, list) and len(attendu) == len(obtenu):
            for rang, (o, a) in enumerate(zip(obtenu, attendu)):
                _ecarts(o, a, f"{chemin}[{rang}]", ecarts)
        elif obtenu != attendu:
            ecarts.append(f"{chemin} : python={str(attendu)[:80]} js={str(obtenu)[:80]}")
        return
    if isinstance(obtenu, bool) or not isinstance(obtenu, (int, float)):
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")
        return
    if abs(obtenu - attendu) / max(abs(attendu), 1e-300) > 1e-9 and abs(obtenu - attendu) > 1e-12:
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")


def _departs_du_portage(droit: str | None = None) -> list:
    """Les départs de chaque requête, datés et chiffrés par le portage, sous le
    droit contrefactuel ``droit`` s'il en nomme un
    (``tests/js/comparer-estimation.mjs``)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(list(REQUETES.values()), fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-estimation.mjs"), chemin,
             *([droit] if droit else [])],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    return json.loads(execution.stdout)


def _en_donnees(departs) -> list[dict]:
    return [{"quoi": list(depart.quoi), "age": depart.age, "date": depart.date,
             "etages": depart.etages, "total": depart.total,
             "minimum_vieillesse": depart.minimum_vieillesse,
             "trimestres": depart.trimestres,
             "trimestres_requis": depart.trimestres_requis,
             "motif_ouverture": depart.motif_ouverture,
             "assiette_maladie": depart.assiette_maladie,
             "assiette_regime_general": depart.assiette_regime_general}
            for depart in departs]


def test_les_deux_moteurs_datent_et_chiffrent_les_memes_departs(saisies):
    obtenus = _departs_du_portage()
    attendus = [_en_donnees(_departs(saisies, nom)) for nom in REQUETES]
    ecarts: list[str] = []
    for nom, obtenu, attendu in zip(REQUETES, obtenus, attendus):
        _ecarts(obtenu, attendu, nom, ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    assert sum(len(departs) for departs in attendus) >= 15


@pytest.mark.parametrize("droit", ["loi_2023_sans_suspension", "au_31_aout_2023"])
def test_les_deux_moteurs_datent_les_memes_departs_sous_chaque_droit_contrefactuel(
        saisies, droit):
    """Les droits contrefactuels du scénario 1 (action 138, étape 10) : sous la
    loi de 2023 sans la suspension, et sous le droit au 31 août 2023, les deux
    moteurs datent et chiffrent les mêmes départs. Et ce ne sont pas ceux du
    droit en vigueur pour le né en 1968, que les deux lois ont touché : sa
    première pension s'ouvre à soixante-quatre ans sous la première, à
    soixante-deux ans sous le second (``tests/test_droits_contrefactuels.py``)."""
    obtenus = _departs_du_portage(droit)
    attendus = [_en_donnees(_departs_du_pont(saisies, requete, droit))
                for requete in REQUETES.values()]
    ecarts: list[str] = []
    for nom, obtenu, attendu in zip(REQUETES, obtenus, attendus):
        _ecarts(obtenu, attendu, nom, ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    premier = attendus[list(REQUETES).index("trois_ages")][0]
    assert premier["age"] == pytest.approx(
        {"loi_2023_sans_suspension": 64.0, "au_31_aout_2023": 62.0}[droit])


def test_chaque_age_est_atteint_une_fois_dans_l_ordre_de_la_synthese(saisies):
    for nom in REQUETES:
        departs = _departs(saisies, nom)
        if not departs:
            continue
        reunis = [quoi for depart in departs for quoi in depart.quoi]
        assert tuple(reunis) == DEPARTS_DE_L_ESTIMATION, nom
        ages = [depart.age for depart in departs]
        assert ages == sorted(ages) and len(set(ages)) == len(ages), nom


def test_les_ages_sont_ceux_que_le_droit_oppose(saisies):
    """Trois âges distincts : l'âge légal avec décote, le taux plein quand la
    durée est atteinte, soixante-sept ans ; chacun est l'âge que l'étape
    « ouvrir le droit » oppose à la carrière liquidée à cet âge."""
    requete = REQUETES["trois_ages"]
    actuel = saisies.simulateur(requete).scenario_actuel
    legal, plein, automatique = _departs(saisies, "trois_ages")
    assert (legal.quoi, plein.quoi, automatique.quoi) == (
        ("legal",), ("taux_plein",), ("automatique",))

    def carriere(age):
        return saisies.carriere(_au_depart(requete, age))

    assert legal.age == pytest.approx(ouvrir.age_ouverture_droit(actuel, carriere(legal.age)))
    assert plein.age == pytest.approx(ouvrir.age_taux_plein_droit(actuel, carriere(plein.age)))
    assert automatique.age == pytest.approx(67.0)
    assert legal.trimestres < legal.trimestres_requis <= plein.trimestres
    assert legal.total < plein.total < automatique.total


def test_la_carriere_longue_part_au_taux_plein_avant_l_age_legal(saisies):
    premier, *_ = _departs(saisies, "carriere_longue")
    assert premier.quoi == ("legal", "taux_plein")
    assert premier.motif_ouverture == "carriere_longue"
    requete = REQUETES["carriere_longue"]
    actuel = saisies.simulateur(requete).scenario_actuel
    carriere = saisies.carriere(_au_depart(requete, premier.age))
    assert premier.age < min(ouvrir.age_ouverture(actuel, periode, carriere)
                             for _, periode in ouvrir.periodes_parcourues(actuel, carriere)[0])


def test_un_depart_anticipe_se_dit_par_ce_qui_l_ouvre(saisies, page):
    """La carrière longue et le handicap ouvrent le premier départ avant l'âge
    légal, au taux plein : la rangée le dit, et non « âge légal »."""
    for nom, mot in (("carriere_longue", "carrière longue"), ("handicap", "handicap")):
        premier, *_ = _departs(saisies, nom)
        assert premier.quoi == ("legal", "taux_plein"), nom
        assert premier.motif_ouverture == nom, nom
        assert f"{mot}, taux plein" in _bloc(page("/simuler", **REQUETES[nom])), nom


@pytest.mark.parametrize("nom", ["parti", "par_pension", "radiation", "metier_tardif"])
def test_sans_depart_a_choisir_le_bloc_se_tait(saisies, page, nom):
    """Qui est parti, qui saisit sa pension, dont la saisie date elle-même un
    départ, ou dont la carrière ne se bâtit pas à l'un des âges : rien à
    chiffrer, et la page calcule comme avant, sans le bloc ni un refus."""
    assert _departs(saisies, nom) == ()
    corps = page("/simuler", **REQUETES[nom])
    assert '<h2 id="estimation-officielle"' not in corps
    assert 'id="resultats"' in corps


def test_les_etages_font_la_pension_du_scenario_1_sans_le_minimum_vieillesse(saisies):
    """Chaque départ est la liquidation que la saisie ferait à cette date : ses
    étages et le minimum vieillesse font la pension du scénario 1, régimes
    provisionnés compris, en euros constants."""
    for nom in ("trois_ages", "fonctionnaire", "mere", "petit_salaire"):
        for depart in _departs(saisies, nom):
            comparaison = saisies.simuler(_au_depart(REQUETES[nom], depart.age))
            actuel = comparaison.actuel
            attendu = ((actuel.pension_annuelle + actuel.pension_hors_repartition)
                       * comparaison.coefficient_euros_constants)
            assert depart.total + depart.minimum_vieillesse == pytest.approx(attendu), nom
    fonctionnaire = _departs(saisies, "fonctionnaire")
    assert all(set(d.etages) == {"integre", "additionnel"} for d in fonctionnaire)
    assert all(d.etages["additionnel"] > 0 for d in fonctionnaire)


def test_l_estimation_recopiee_voyage_dans_l_adresse_et_n_entre_dans_aucun_calcul(saisies):
    recopie = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300.5"}
    saisie = saisie_du_portage(recopie)
    assert (saisie.estimation_legal, saisie.estimation_taux_plein,
            saisie.estimation_automatique) == (2500.0, None, 3300.5)
    adresse = dict(pair.split("=", 1) for pair in saisie.requete().split("&"))
    assert {nom: adresse.get(nom) for nom in module("saisie").CHAMPS_ESTIMATION} == {
        "estimation_legal": "2500", "estimation_taux_plein": None,
        "estimation_automatique": "3300.5"}
    assert _departs_du_pont(saisies, recopie) == _departs(saisies, "trois_ages")
    for valeur in ("0", "0.5", "-12"):
        with pytest.raises(ErreurSite, match=refus_de_la_saisie("estimation officielle")):
            saisie_du_portage({**REQUETES["trois_ages"], "estimation_taux_plein": valeur})


def _nombres(cellule: str) -> int:
    texte = re.sub(r"<[^>]+>", "", html.unescape(cellule))
    chiffres = re.sub(r"[^\d\-−]", "", texte.split("(")[0]).replace("−", "-")
    return int(chiffres)


def _bloc(corps: str) -> str:
    debut = corps.index('<h2 id="estimation-officielle"')
    return corps[debut:corps.index("</table>", debut)]


def test_la_page_montre_le_brut_par_etage_le_net_puis_l_ecart(saisies, page):
    requete = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300"}
    bloc = _bloc(page("/simuler", **requete))
    departs = _departs_du_pont(saisies, requete)
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert entetes == ["Départ", "Base", "Complémentaire", "Total brut", "Net avant impôt",
                       "Votre estimation", "Écart"]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)
    assert len(rangees) == len(departs) == 3
    # Le net de chaque âge, à SA tranche : sous la présomption, son revenu
    # fiscal est fait de cette pension seule ; et 1 % de sa propre part
    # complémentaire aux deux derniers taux (action 138, étape 2).
    montants = montants_du_portage(requete, simuler=False)
    for (tete, cellules), depart, recopie in zip(rangees, departs, (2500, None, 3300)):
        valeurs = re.findall(r"<td[^>]*>(.*?)</td>", cellules)
        base, complementaire, total, net = (_nombres(v) for v in valeurs[:4])
        assert base + complementaire == total == round(depart.total / 12)
        assert 0 < depart.assiette_maladie < depart.total
        assert net == round(montants.net_d_un_depart(
            depart.total, depart.assiette_maladie, depart.minimum_vieillesse) / 12)
        assert 'form="simulateur"' in valeurs[4]
        assert f'name="estimation_{depart.quoi[0]}"' in valeurs[4]
        if recopie is None:
            assert valeurs[5] == "—"
        else:
            assert f'value="{recopie}"' in valeurs[4]
            assert _nombres(valeurs[5]) == round(depart.total / 12 - recopie)
    assert "avec décote" in rangees[0][0] and "taux plein automatique" in rangees[2][0]


def test_sans_estimation_recopiee_la_page_n_a_pas_de_colonne_d_ecart(page):
    corps = page("/simuler", **REQUETES["trois_ages"])
    assert "Écart" not in _bloc(corps)
    assert '<form class="carte" id="simulateur"' in corps
    assert '<h2 id="estimation-officielle"' not in page("/simuler", **REQUETES["parti"])


def _ages_de_depart(corps: str) -> str:
    debut = corps.index("Partir plus tôt ou plus tard")
    return corps[debut:corps.index("</details>", debut)]


def test_plusieurs_ages_de_depart_cote_a_cote(saisies, page):
    """Le dépliant « Partir plus tôt ou plus tard » (action 138, étape 10) :
    la carrière de la saisie liquidée chaque année, de l'âge d'ouverture au
    taux plein automatique, et ses pensions nettes sous les quatre systèmes,
    puis après impôt (étape 5), celles que le portage tire de
    ``balayageDeLEstimation`` (``contexte.js``), sous l'impôt d'une personne
    seule que la bulle dit ; rien pour qui n'a pas de départ à chiffrer. Le
    cycle de vie n'a qu'un exemplaire, le portage (action 161) : le premier
    et le dernier âge se confrontent au pilote du Python
    (``ages_de_l_estimation``), sur les carrières du pont. La requête date la
    naissance au jour : aucune présomption n'y entre, et la saisie du portage
    se lit sans leur table."""
    requete = REQUETES["trois_ages"]
    saisie = module("saisie").Saisie.depuis_requete(requete, False, None)
    balayage = site().contexte.balayage_de_l_estimation(saisie)
    departs = [un.depart for un in balayage]
    ages = ages_de_l_estimation(saisies.simulateur(requete).scenario_actuel,
                                lambda age: saisies.carriere(_au_depart(requete, age)),
                                saisie.liquidation)
    assert departs[0].age == ages["legal"] and departs[-1].age == ages["automatique"]
    bloc = _ages_de_depart(page("/simuler", **REQUETES["trois_ages"]))
    tableau = bloc[:bloc.index("</table>")]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', tableau)
    assert len(rangees) == len(departs) >= 2
    systemes = ("actuel", "notionnel_retroactif", "notionnel_retroactif_employeur",
                "notionnel_liberal")
    apres = bloc[bloc.index("La pension après impôt du premier mois"):]
    rangees_apres = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>',
                               apres[:apres.index("</table>")])
    assert len(rangees_apres) == len(departs)
    for (tete, cellules), (tete_apres, cellules_apres), un in zip(
            rangees, rangees_apres, balayage):
        depart = un.depart
        assert f"en {depart.annee}" in tete and f"en {depart.annee}" in tete_apres
        for lues, pensions in ((cellules, depart.pensions_nettes),
                               (cellules_apres, depart.pensions_apres_impot)):
            valeurs = [_nombres(v) for v in re.findall(r"<td[^>]*>(.*?)</td>", lues)]
            attendus = [round(un.comparaison.en_euros_constants(
                pensions[scenario], scenario) / 12) for scenario in systemes]
            assert valeurs == attendus
    assert any(depart.pensions_apres_impot["actuel"] < depart.pensions_nettes["actuel"]
               for depart in departs)
    assert "une personne seule, sans enfant à charge" in bloc
    assert bloc.count("<table") == 4 and "rendement réel" in bloc
    assert "Partir plus tôt ou plus tard" not in page("/simuler", **REQUETES["parti"])


def _avec_ou_sans(corps: str) -> str:
    debut = corps.index("Avec ou sans la réforme de 2023")
    return corps[debut:corps.index("</details>", debut)]


def test_les_departs_sous_trois_etats_du_droit(saisies, page):
    """Le dépliant « Avec ou sans la réforme de 2023 » (action 138, étape 10) :
    au plus tôt et au taux plein, l'âge, le mois et le net du premier mois de
    la carrière saisie sous le droit qui s'applique, sous la loi de 2023 sans
    la suspension et sous le droit au 31 août 2023, avec l'écart au premier,
    et la durée requise : ceux que le Python date sous chaque droit. Le né en
    mai 1968 part au plus tôt à 63 ans et 9 mois, 3 mois plus tard sans la
    suspension, 1 an et 9 mois plus tôt sans la réforme ; rien pour qui n'a
    pas de départ à chiffrer."""
    from retraite_notionnelle.calendrier import formater_age

    bloc = _avec_ou_sans(page("/simuler", **REQUETES["trois_ages"]))
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert entetes == ["État du droit", "Au plus tôt", "Net au plus tôt", "Au taux plein",
                       "Net au taux plein", "Durée requise"]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)
    assert len(rangees) == 3
    montants = montants_du_portage(REQUETES["trois_ages"], simuler=False)

    def net(depart) -> int:
        return round(montants.net_d_un_depart(
            depart.total, depart.assiette_maladie, depart.minimum_vieillesse) / 12)

    for (_, cellules), droit in zip(rangees, (None, "loi_2023_sans_suspension",
                                               "au_31_aout_2023")):
        departs = _departs_du_pont(saisies, REQUETES["trois_ages"], droit)
        tot = next(depart for depart in departs if "legal" in depart.quoi)
        plein = next(depart for depart in departs if "taux_plein" in depart.quoi)
        valeurs = re.findall(r"<td[^>]*>(.*?)</td>", cellules)
        assert valeurs[0].startswith(formater_age(tot.age)), droit
        assert valeurs[2].startswith(formater_age(plein.age)), droit
        assert [_nombres(valeurs[1]), _nombres(valeurs[3]), _nombres(valeurs[4])] == [
            net(tot), net(plein), tot.trimestres_requis], droit
    premiers = [re.findall(r"<td[^>]*>(.*?)</td>", cellules)[0] for _, cellules in rangees]
    assert premiers[0].startswith("63 ans et 9 mois")
    assert premiers[1].startswith("64 ans") and "3 mois plus tard" in premiers[1]
    assert premiers[2].startswith("62 ans") and "1 an et 9 mois plus tôt" in premiers[2]
    assert [html.unescape(tete) for tete, _ in rangees] == [
        "Le droit qui s'applique", "La loi de 2023, sans la suspension",
        "Le droit du 31 août 2023"]
    assert "Avec ou sans la réforme de 2023" not in page("/simuler", **REQUETES["parti"])
