"""Le système 1 au format de « Mon estimation retraite », sur le site.

Les départs que la synthèse officielle chiffre — au plus tôt, au taux plein, au
taux plein automatique — sont datés par le pilote
(:func:`~retraite_notionnelle.pilote.ages_de_l_estimation`), liquidés par le
contexte (:meth:`~retraite_notionnelle.contexte.Contexte.departs_de_l_estimation`),
et la page les montre en brut mensuel, étage par étage, le net en second, à côté
du total que le lecteur recopie de son estimation (``estimationOfficielle``,
``moteur/js/pages.js``). Ces tests tiennent les deux moteurs d'accord, les âges
au droit, et la page à ce qu'elle promet. Les carrières sont fictives.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Montants
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.pilote import DEPARTS_DE_L_ESTIMATION
from retraite_notionnelle.saisie import CHAMPS_ESTIMATION, ErreurSaisie, Saisie
from outils_web import contexte, page  # noqa: F401 — les fixtures partagées

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


def _departs(contexte, nom: str):
    return contexte.departs_de_l_estimation(Saisie.depuis_requete(REQUETES[nom]))


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


def test_les_deux_moteurs_datent_et_chiffrent_les_memes_departs(contexte):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    requetes = list(REQUETES.values())
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-estimation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus = json.loads(execution.stdout)
    attendus = [[{"quoi": list(depart.quoi), "age": depart.age, "date": depart.date,
                  "etages": depart.etages, "total": depart.total,
                  "minimum_vieillesse": depart.minimum_vieillesse,
                  "trimestres": depart.trimestres,
                  "trimestres_requis": depart.trimestres_requis,
                  "motif_ouverture": depart.motif_ouverture,
                  "assiette_maladie": depart.assiette_maladie,
                  "assiette_regime_general": depart.assiette_regime_general}
                 for depart in _departs(contexte, nom)] for nom in REQUETES]
    ecarts: list[str] = []
    for nom, obtenu, attendu in zip(REQUETES, obtenus, attendus):
        _ecarts(obtenu, attendu, nom, ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    assert sum(len(departs) for departs in attendus) >= 15


def test_chaque_age_est_atteint_une_fois_dans_l_ordre_de_la_synthese(contexte):
    for nom in REQUETES:
        departs = _departs(contexte, nom)
        if not departs:
            continue
        reunis = [quoi for depart in departs for quoi in depart.quoi]
        assert tuple(reunis) == DEPARTS_DE_L_ESTIMATION, nom
        ages = [depart.age for depart in departs]
        assert ages == sorted(ages) and len(set(ages)) == len(ages), nom


def test_les_ages_sont_ceux_que_le_droit_oppose(contexte):
    """Trois âges distincts : l'âge légal avec décote, le taux plein quand la
    durée est atteinte, soixante-sept ans ; chacun est l'âge que l'étape
    « ouvrir le droit » oppose à la carrière liquidée à cet âge."""
    saisie = Saisie.depuis_requete(REQUETES["trois_ages"])
    actuel = contexte.simulateur(saisie.parametres(contexte.base)).scenario_actuel
    legal, plein, automatique = contexte.departs_de_l_estimation(saisie)
    assert (legal.quoi, plein.quoi, automatique.quoi) == (
        ("legal",), ("taux_plein",), ("automatique",))

    def carriere(age):
        return contexte.carriere(replace(saisie, liquidation=age))

    assert legal.age == pytest.approx(ouvrir.age_ouverture_droit(actuel, carriere(legal.age)))
    assert plein.age == pytest.approx(ouvrir.age_taux_plein_droit(actuel, carriere(plein.age)))
    assert automatique.age == pytest.approx(67.0)
    assert legal.trimestres < legal.trimestres_requis <= plein.trimestres
    assert legal.total < plein.total < automatique.total


def test_la_carriere_longue_part_au_taux_plein_avant_l_age_legal(contexte):
    premier, *_ = _departs(contexte, "carriere_longue")
    assert premier.quoi == ("legal", "taux_plein")
    assert premier.motif_ouverture == "carriere_longue"
    saisie = Saisie.depuis_requete(REQUETES["carriere_longue"])
    actuel = contexte.simulateur(saisie.parametres(contexte.base)).scenario_actuel
    carriere = contexte.carriere(replace(saisie, liquidation=premier.age))
    assert premier.age < min(ouvrir.age_ouverture(actuel, periode, carriere)
                             for _, periode in ouvrir.periodes_parcourues(actuel, carriere)[0])


def test_un_depart_anticipe_se_dit_par_ce_qui_l_ouvre(contexte, page):
    """La carrière longue et le handicap ouvrent le premier départ avant l'âge
    légal, au taux plein : la rangée le dit, et non « âge légal »."""
    for nom, mot in (("carriere_longue", "carrière longue"), ("handicap", "handicap")):
        premier, *_ = _departs(contexte, nom)
        assert premier.quoi == ("legal", "taux_plein"), nom
        assert premier.motif_ouverture == nom, nom
        assert f"{mot}, taux plein" in _bloc(page("/simuler", **REQUETES[nom])), nom


@pytest.mark.parametrize("nom", ["parti", "par_pension", "radiation", "metier_tardif"])
def test_sans_depart_a_choisir_le_bloc_se_tait(contexte, page, nom):
    """Qui est parti, qui saisit sa pension, dont la saisie date elle-même un
    départ, ou dont la carrière ne se bâtit pas à l'un des âges : rien à
    chiffrer, et la page calcule comme avant, sans le bloc ni un refus."""
    assert _departs(contexte, nom) == ()
    corps = page("/simuler", **REQUETES[nom])
    assert '<h2 id="estimation-officielle"' not in corps
    assert 'id="resultats"' in corps


def test_les_etages_font_la_pension_du_scenario_1_sans_le_minimum_vieillesse(contexte):
    """Chaque départ est la liquidation que la saisie ferait à cette date : ses
    étages et le minimum vieillesse font la pension du scénario 1, régimes
    provisionnés compris, en euros constants."""
    for nom in ("trois_ages", "fonctionnaire", "mere", "petit_salaire"):
        saisie = Saisie.depuis_requete(REQUETES[nom])
        for depart in contexte.departs_de_l_estimation(saisie):
            comparaison = contexte.simuler(replace(saisie, liquidation=depart.age))
            actuel = comparaison.actuel
            attendu = ((actuel.pension_annuelle + actuel.pension_hors_repartition)
                       * comparaison.coefficient_euros_constants)
            assert depart.total + depart.minimum_vieillesse == pytest.approx(attendu), nom
    fonctionnaire = _departs(contexte, "fonctionnaire")
    assert all(set(d.etages) == {"integre", "additionnel"} for d in fonctionnaire)
    assert all(d.etages["additionnel"] > 0 for d in fonctionnaire)


def test_l_estimation_recopiee_voyage_dans_l_adresse_et_n_entre_dans_aucun_calcul(contexte):
    recopie = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300.5"}
    saisie = Saisie.depuis_requete(recopie)
    assert (saisie.estimation_legal, saisie.estimation_taux_plein,
            saisie.estimation_automatique) == (2500.0, None, 3300.5)
    adresse = dict(pair.split("=", 1) for pair in saisie.requete().split("&"))
    assert {nom: adresse.get(nom) for nom in CHAMPS_ESTIMATION} == {
        "estimation_legal": "2500", "estimation_taux_plein": None,
        "estimation_automatique": "3300.5"}
    sans = Saisie.depuis_requete(REQUETES["trois_ages"])
    assert contexte.departs_de_l_estimation(saisie) == contexte.departs_de_l_estimation(sans)
    for valeur in ("0", "0.5", "-12"):
        with pytest.raises(ErreurSaisie, match="estimation officielle"):
            Saisie.depuis_requete({**REQUETES["trois_ages"], "estimation_taux_plein": valeur})


def _nombres(cellule: str) -> int:
    texte = re.sub(r"<[^>]+>", "", html.unescape(cellule))
    chiffres = re.sub(r"[^\d\-−]", "", texte.split("(")[0]).replace("−", "-")
    return int(chiffres)


def _bloc(corps: str) -> str:
    debut = corps.index('<h2 id="estimation-officielle"')
    return corps[debut:corps.index("</table>", debut)]


def test_la_page_montre_le_brut_par_etage_le_net_puis_l_ecart(contexte, page):
    requete = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300"}
    bloc = _bloc(page("/simuler", **requete))
    departs = contexte.departs_de_l_estimation(Saisie.depuis_requete(requete))
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert entetes == ["Départ", "Base", "Complémentaire", "Total brut", "Net avant impôt",
                       "Votre estimation", "Écart"]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)
    assert len(rangees) == len(departs) == 3
    # Le net de chaque âge, à SA tranche : sous la présomption, son revenu
    # fiscal est fait de cette pension seule ; et 1 % de sa propre part
    # complémentaire aux deux derniers taux (action 138, étape 2).
    montants = Montants.depuis(Saisie.depuis_requete(requete), contexte.base)
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
