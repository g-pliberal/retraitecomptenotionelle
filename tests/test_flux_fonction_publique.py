"""Les cas types statutaires face aux départs de 2025 que décrit le jaune pensions.

Le stock de pensions de la fonction publique au 31 décembre 2025 et le flux
de 2025, tels que le Service des retraites de l'État, la CNRACL et le FSPOEIE
les publient dans le jaune annexé au PLF 2027, sont certifiés dans
`data/reference/macro/caracteristiques_fonction_publique.csv` (action 159,
étape 4). Aucun calcul ne les lit : ils jugent le modèle, ils ne le règlent
pas. `scripts/flux_fonction_publique.py` fait partir en 2025 chacun des trois
cas types statutaires, tel que la page Coût le pèse, et met en regard ce que
le modèle lui sert et ce que le jaune publie des départs de son groupe.

Ce que la mesure trouve, le 14 octobre 2026 — l'écart du modèle au jaune :

| cas type | âge | durée tous régimes | taux | indice | pension |
|---|---|---|---|---|---|
| fonctionnaire sédentaire de l'État (B-4) | −0,4 an | −6,5 trim. | −3,8 % | +1,9 % | −1,2 % |
| agent actif de la CNRACL (B-5) | +1,0 an | −20,7 trim. | +1,0 % | +0,5 % | −2,7 % |
| militaire (B-3, ancienneté) | −0,7 an | −24,5 trim. | −10,9 % | +4,9 % | −5,0 % |

Les deux civils sont recalés sur ce flux depuis l'étape 5 de l'action 159. Le
sédentaire entre dans l'État à vingt-huit ans, après six ans de contrat : 144
trimestres de services, pour 143,3 au jaune, services et bonifications ; son
taux, sans surcote, est celui du flux hors décote et surcote, 64,1 %. L'actif
de la CNRACL part au taux plein, à soixante-deux ans pour 61,0, à l'indice du
flux, après six ans de contrat lui aussi. Leur durée tous régimes reste en
deçà : une carrière continue, sans enfant ni temps partiel. Le 13 octobre
(étape 4), sur la carrière d'un seul statut, le sédentaire était 15 % trop
haut, et l'actif partait trois ans et quart trop tôt, à l'âge d'ouverture, sur
un traitement d'un cinquième trop haut : deux erreurs qui se compensaient. Le
militaire part à l'âge du flux, mais sans les bénéfices de campagne ni les
bonifications du service aérien que le simulateur ne saisit pas : 130
trimestres liquidables pour 149,5.

Les écarts sont DÉCLARÉS : chacun tient dans sa fourchette, et une mesure qui
en sort fait échouer la suite, qu'elle s'améliore ou qu'elle se dégrade. Qui
la déplace dit pourquoi, et récrit la fourchette et le tableau ci-dessus.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

from retraite_notionnelle import memoire
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

import flux_fonction_publique as flux  # noqa: E402

CHEMIN = "data/reference/macro/caracteristiques_fonction_publique.csv"

#: L'écart relatif de chaque mesure au jaune, (modèle − jaune) / jaune, dans
#: sa fourchette déclarée. Mesuré le 13 octobre 2026 (action 159, étape 4),
#: puis, pour les deux civils, le 14 (étape 5) : la valeur du jour est au
#: milieu, à un point et demi près, et l'âge à un demi-point (trois mois).
ECARTS_DECLARES = {
    ("fonctionnaire_sedentaire", "age_premiere_mise_en_paiement"): (-0.011, -0.001),
    ("fonctionnaire_sedentaire", "duree_tous_regimes_trimestres"): (-0.052, -0.022),
    ("fonctionnaire_sedentaire", "taux_liquidation"): (-0.053, -0.023),
    ("fonctionnaire_sedentaire", "indice_liquidation"): (0.004, 0.034),
    ("fonctionnaire_sedentaire", "pension_principale_eur"): (-0.027, 0.003),
    ("fonctionnaire_actif", "age_premiere_mise_en_paiement"): (0.011, 0.021),
    ("fonctionnaire_actif", "duree_tous_regimes_trimestres"): (-0.130, -0.100),
    ("fonctionnaire_actif", "taux_liquidation"): (-0.005, 0.025),
    ("fonctionnaire_actif", "indice_liquidation"): (-0.010, 0.020),
    ("fonctionnaire_actif", "pension_principale_eur"): (-0.042, -0.012),
    ("militaire", "age_premiere_mise_en_paiement"): (-0.019, -0.009),
    ("militaire", "duree_tous_regimes_trimestres"): (-0.174, -0.144),
    ("militaire", "taux_liquidation"): (-0.124, -0.094),
    ("militaire", "indice_liquidation"): (0.034, 0.064),
    ("militaire", "pension_principale_eur"): (-0.065, -0.035),
}


@pytest.fixture(scope="module")
def lignes():
    with (RACINE / CHEMIN).open(encoding="utf-8") as fichier:
        return list(csv.DictReader(l for l in fichier if not l.lstrip().startswith("#")))


@pytest.fixture(scope="module")
def mesures():
    return flux.mesures_du_depot(Parametres())


def test_le_stock_et_le_flux_sont_certifies_et_qu_aucun_calcul_ne_les_lit(lignes):
    """Cinquante-trois tableaux, 8 166 valeurs, toutes certifiées ; la clé de
    chacune est à elle. Le fichier est hors de l'empreinte du modèle : il le
    juge, il ne le règle pas. Ce que ses tableaux disent les uns des autres
    est à ``tests/test_sre_jaune_referents.py``."""
    assert CHEMIN in memoire.HORS_DU_MODELE
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert {l["tableau"] for l in lignes} == {f"A-{n}" for n in (1, 2, 3, 4, 5, 6, 8)} | {
        f"B-{n}" for n in range(1, 22)} | {"B-3bis"} | {
        str(n) for n in (60, 66, 67, 68, 69, 70, 73, 75, 76, 78, 79, 80, 83, 84, 85, 86,
                         *range(101, 109))}
    cles = [(l["tableau"], l["population"], l["champ"], l["modalite"], l["indicateur"])
            for l in lignes]
    assert len(cles) == len(set(cles)) == 8166


def test_les_departs_du_flux_sont_ceux_que_tiennent_les_bonifications(lignes):
    """Les départs du B-1 sont ceux que `bonifications_jaune.csv` tient du
    même tableau, lu par l'autre lecteur."""
    with (RACINE / "data/reference/legislation/bonifications_jaune.csv").open(encoding="utf-8") as f:
        bonifications = list(csv.DictReader(x for x in f if not x.lstrip().startswith("#")))
    ensemble = {b["population"]: int(b["valeur"]) for b in bonifications
                if b["tableau"] == "B-1" and b["ligne"] == "ensemble_des_departs"}
    departs = {l["population"]: float(l["valeur"]) for l in lignes
               if (l["tableau"], l["champ"], l["modalite"], l["indicateur"])
               == ("B-1", "ensemble", "ensemble", "departs")}
    assert len(ensemble) == 8
    assert departs == ensemble


def test_les_moyennes_du_flux_sont_celles_que_le_texte_du_jaune_ecrit(lignes):
    """La partie IV du jaune écrit, en toutes lettres, ce que ses tableaux
    annexés donnent : l'indice moyen de liquidation de 2025, 726 pour les
    civils de l'État et 484 pour la CNRACL (p. 156)."""
    valeur = {(l["tableau"], l["population"], l["champ"], l["modalite"], l["indicateur"]):
              float(l["valeur"]) for l in lignes}
    assert valeur[("B-1", "fpe_civils", "ensemble", "ensemble", "indice_liquidation")] == 726
    assert valeur[("B-1", "cnracl_total", "ensemble", "ensemble", "indice_liquidation")] == 484


def test_chaque_cas_type_statutaire_part_en_2025_face_aux_departs_de_son_groupe(mesures):
    """Trois cas types, cinq mesures chacun, chaque génération celle que le
    droit fait partir en 2025."""
    assert {(m.cas_type, m.indicateur) for m in mesures} == set(ECARTS_DECLARES)
    generations = {m.cas_type: m.generation for m in mesures}
    assert generations == {"fonctionnaire_sedentaire": 1961, "fonctionnaire_actif": 1963,
                           "militaire": 1977}


@pytest.mark.parametrize("cle", sorted(ECARTS_DECLARES), ids=lambda c: f"{c[0]}-{c[1]}")
def test_chaque_ecart_au_flux_de_2025_tient_dans_sa_fourchette_declaree(mesures, cle):
    """Une mesure qui sort de sa fourchette, dans un sens ou dans l'autre,
    fait échouer la suite : qui la déplace dit pourquoi, au tableau du
    module, et récrit la fourchette."""
    mesure = next(m for m in mesures if (m.cas_type, m.indicateur) == cle)
    bas, haut = ECARTS_DECLARES[cle]
    assert bas <= mesure.ecart_relatif <= haut, (
        f"{cle} : {mesure.modele} pour {mesure.jaune} au jaune, écart "
        f"{mesure.ecart_relatif:+.1%}, fourchette déclarée [{bas:+.1%}, {haut:+.1%}]")


def test_l_entree_tardive_porte_le_recalage_des_deux_civils(mesures):
    """Sur la carrière d'un seul statut que la page Cas types montre, les deux
    civils liquident six ans de services de plus que sous les conventions de
    la page Coût, et leur pension passe 14 à 15 % au-dessus du flux : le
    sédentaire à 75 % du traitement, l'actif à 72 %. C'est l'entrée tardive,
    que le jaune mesure, qui les recale ; que l'une des deux pages perde la
    convention de l'autre, et ce test le dit."""
    publies = flux.referents_publies()
    individuel = flux.confronter(flux.mesurer_le_modele(Simulateur(Parametres())), publies)
    for code in ("fonctionnaire_sedentaire", "fonctionnaire_actif"):
        seul = next(m for m in individuel
                    if (m.cas_type, m.indicateur) == (code, "pension_principale_eur"))
        tard = next(m for m in mesures
                    if (m.cas_type, m.indicateur) == (code, "pension_principale_eur"))
        assert seul.ecart_relatif > 0.10, (code, seul.ecart_relatif)
        assert abs(tard.ecart_relatif) < 0.04, (code, tard.ecart_relatif)
