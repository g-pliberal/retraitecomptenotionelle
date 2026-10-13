"""Les cas types statutaires face aux départs de 2025 que décrit le jaune pensions.

Le stock de pensions de la fonction publique au 31 décembre 2025 et le flux
de 2025, tels que le Service des retraites de l'État, la CNRACL et le FSPOEIE
les publient dans le jaune annexé au PLF 2027, sont certifiés dans
`data/reference/macro/caracteristiques_fonction_publique.csv` (action 159,
étape 4). Aucun calcul ne les lit : ils jugent le modèle, ils ne le règlent
pas. `scripts/flux_fonction_publique.py` fait partir en 2025 chacun des trois
cas types statutaires et met en regard ce que le modèle lui sert et ce que le
jaune publie des départs de son groupe.

Ce que la mesure trouve, le 13 octobre 2026 — l'écart du modèle au jaune :

| cas type | âge | durée tous régimes | taux | indice | pension |
|---|---|---|---|---|---|
| fonctionnaire sédentaire de l'État (B-4) | −0,4 an | −6,5 trim. | +12,3 % | +1,9 % | +15,3 % |
| agent actif de la CNRACL (B-5) | −3,25 ans | −37,7 trim. | −17,9 % | +21,2 % | −4,6 % |
| militaire (B-3, ancienneté) | −0,7 an | −24,5 trim. | −10,9 % | +4,9 % | −5,0 % |

Le sédentaire part à l'âge du flux et à son indice, mais au taux plein, sur
une carrière entière dans le seul régime de l'État : le civil réel n'y a que
138 trimestres de services sur 174,5 tous régimes, et sa pension est 15 % plus
basse. L'actif de la CNRACL part trois ans trop tôt, à l'âge d'ouverture, avec
une décote que les actifs ne prennent presque jamais, sur un traitement un
cinquième trop haut : deux erreurs qui se compensent, que l'action 152 avait
lues sur le jaune 2026, et que le flux de 2025 confirme. Le militaire part à
l'âge du flux, mais sans les bénéfices de campagne ni les bonifications du
service aérien que le simulateur ne saisit pas : 130 trimestres liquidables
pour 149,5. Le recalage des cas types est l'étape 5 de l'action 159.

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

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

import flux_fonction_publique as flux  # noqa: E402
from sre_jaune_pensions import incoherences_referents  # noqa: E402

CHEMIN = "data/reference/macro/caracteristiques_fonction_publique.csv"

#: L'écart relatif de chaque mesure au jaune, (modèle − jaune) / jaune, dans
#: sa fourchette déclarée. Mesuré le 13 octobre 2026 (action 159, étape 4) :
#: la valeur du jour est au milieu, à un point et demi près, et l'âge à un
#: demi-point (trois mois).
ECARTS_DECLARES = {
    ("fonctionnaire_sedentaire", "age_premiere_mise_en_paiement"): (-0.011, -0.001),
    ("fonctionnaire_sedentaire", "duree_tous_regimes_trimestres"): (-0.052, -0.022),
    ("fonctionnaire_sedentaire", "taux_liquidation"): (0.108, 0.138),
    ("fonctionnaire_sedentaire", "indice_liquidation"): (0.004, 0.034),
    ("fonctionnaire_sedentaire", "pension_principale_eur"): (0.138, 0.168),
    ("fonctionnaire_actif", "age_premiere_mise_en_paiement"): (-0.058, -0.048),
    ("fonctionnaire_actif", "duree_tous_regimes_trimestres"): (-0.224, -0.194),
    ("fonctionnaire_actif", "taux_liquidation"): (-0.194, -0.164),
    ("fonctionnaire_actif", "indice_liquidation"): (0.197, 0.227),
    ("fonctionnaire_actif", "pension_principale_eur"): (-0.061, -0.031),
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


def test_le_stock_et_le_flux_de_2025_sont_certifies_et_qu_aucun_calcul_ne_les_lit(lignes):
    """Six tableaux, 1 352 valeurs, toutes certifiées ; la clé de chacune est à
    elle. Le fichier est hors de l'empreinte du modèle : il le juge, il ne le
    règle pas."""
    assert CHEMIN in memoire.HORS_DU_MODELE
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert {l["tableau"] for l in lignes} == {"A-1", "B-1", "B-3", "B-3bis", "B-4", "B-5"}
    cles = [(l["tableau"], l["population"], l["champ"], l["indicateur"]) for l in lignes]
    assert len(cles) == len(set(cles)) == 1352


def test_le_stock_et_le_flux_se_recoupent_entre_eux_et_avec_les_bonifications(lignes):
    """Les sexes font l'effectif, ou cent pour cent ; le total de l'État, ses
    civils et ses militaires ; les motifs de départ du B-3, l'ensemble du
    B-1 ; les catégories du B-4, les départs pour ancienneté du B-3. Et les
    départs du B-1 sont ceux que `bonifications_jaune.csv` tient du même
    tableau."""
    imbrique: dict = {}
    for l in lignes:
        valeur = float(l["valeur"])
        imbrique.setdefault(l["tableau"], {}).setdefault(l["population"], {}).setdefault(
            l["champ"], {})[l["indicateur"]] = int(valeur) if valeur.is_integer() else valeur
    assert incoherences_referents(imbrique) == []

    with (RACINE / "data/reference/legislation/bonifications_jaune.csv").open(encoding="utf-8") as f:
        bonifications = list(csv.DictReader(x for x in f if not x.lstrip().startswith("#")))
    ensemble = {b["population"]: int(b["valeur"]) for b in bonifications
                if b["tableau"] == "B-1" and b["ligne"] == "ensemble_des_departs"}
    assert len(ensemble) == 8
    for population, departs in ensemble.items():
        assert imbrique["B-1"][population]["ensemble"]["departs"] == departs, population


def test_les_moyennes_du_flux_sont_celles_que_le_texte_du_jaune_ecrit(lignes):
    """La partie IV du jaune écrit, en toutes lettres, ce que ses tableaux
    annexés donnent : l'indice moyen de liquidation de 2025, 726 pour les
    civils de l'État et 484 pour la CNRACL (p. 156)."""
    valeur = {(l["tableau"], l["population"], l["champ"], l["indicateur"]): float(l["valeur"])
              for l in lignes}
    assert valeur[("B-1", "fpe_civils", "ensemble", "indice_liquidation")] == 726
    assert valeur[("B-1", "cnracl_total", "ensemble", "indice_liquidation")] == 484


def test_chaque_cas_type_statutaire_part_en_2025_face_aux_departs_de_son_groupe(mesures):
    """Trois cas types, cinq mesures chacun, chaque génération celle que le
    droit fait partir en 2025."""
    assert {(m.cas_type, m.indicateur) for m in mesures} == set(ECARTS_DECLARES)
    generations = {m.cas_type: m.generation for m in mesures}
    assert generations == {"fonctionnaire_sedentaire": 1961, "fonctionnaire_actif": 1968,
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


def test_les_deux_erreurs_de_l_actif_de_la_cnracl_se_compensent(mesures):
    """L'actif de la CNRACL part trois ans trop tôt, avec une décote, sur un
    traitement un cinquième trop haut ; sa pension tombe pourtant à moins de
    6 % de celle du flux. Que l'une des deux erreurs soit corrigée sans
    l'autre, et la pension s'en écarte : ce test le dit d'avance."""
    actif = {m.indicateur: m for m in mesures if m.cas_type == "fonctionnaire_actif"}
    assert actif["age_premiere_mise_en_paiement"].ecart < -3.0
    assert actif["taux_liquidation"].ecart_relatif < -0.15
    assert actif["indice_liquidation"].ecart_relatif > 0.15
    assert abs(actif["pension_principale_eur"].ecart_relatif) < 0.06
