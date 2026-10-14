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

ANNÉE PAR ANNÉE, de 2016 à 2025, chaque cas type part chaque année où le droit
fait partir l'une de ses générations, face à la série de son groupe. Le
sédentaire suit les siens : son taux baisse avec celui des sédentaires partis
pour ancienneté, deux à quatre points en dessous (tableau 107), sa pension
reste à 7 % au plus de celle du flux des civils ; mais son âge ne monte que
de trois trimestres, le leur d'un an et neuf mois (tableau 101). L'actif de
la CNRACL part d'un à deux ans après les actifs (tableau 102), et son taux
s'écarte de celui du flux de sa caisse, qui baisse quand le sien monte : +4 %
en 2016, +18 % en 2025. Le militaire perd six points de taux de 2016 à 2025,
le flux réel quatre.

LE STOCK, pesé comme la page le pèse : en 2025, la page sert au sédentaire, à
l'actif et au militaire, au titre de leur régime, 1 à 3 % de moins que
l'avantage principal du stock de leur caisse (tableau A-5) ; en 2016, 10, 13
et 16 % de moins que le stock accessoires compris (tableau A-4). Le stock de
la page monte plus vite que celui du jaune : il suit les prix, que le droit a
revalorisés de 4 % de moins depuis 2016, et avec un an de retard en 2023.

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


# -- année par année, puis le stock --------------------------------------------

#: L'écart de chaque cas type à la série qui suit son groupe, la première année
#: où il part et en 2025 : l'âge en années, le reste rapporté au jaune.
#: Mesuré le 14 octobre 2026, sur les cas types de l'étape 5 : la valeur du
#: jour au milieu, à un quart d'année près pour l'âge, à un point et demi pour
#: le reste.
ECARTS_ANNUELS_DECLARES = {
    ("fonctionnaire_sedentaire", "age_premiere_mise_en_paiement", 2016): (0.40, 0.90),
    ("fonctionnaire_sedentaire", "age_premiere_mise_en_paiement", 2025): (-0.65, -0.15),
    ("fonctionnaire_sedentaire", "taux_liquidation", 2016): (-0.056, -0.026),
    ("fonctionnaire_sedentaire", "taux_liquidation", 2025): (-0.066, -0.036),
    ("fonctionnaire_sedentaire", "indice_liquidation", 2016): (0.033, 0.063),
    ("fonctionnaire_sedentaire", "indice_liquidation", 2025): (0.017, 0.047),
    ("fonctionnaire_sedentaire", "pension_principale_eur", 2016): (-0.022, 0.008),
    ("fonctionnaire_sedentaire", "pension_principale_eur", 2025): (-0.048, -0.018),
    ("fonctionnaire_actif", "age_premiere_mise_en_paiement", 2016): (0.75, 1.25),
    ("fonctionnaire_actif", "age_premiere_mise_en_paiement", 2025): (0.75, 1.25),
    ("fonctionnaire_actif", "taux_liquidation", 2016): (0.028, 0.058),
    ("fonctionnaire_actif", "taux_liquidation", 2025): (0.169, 0.199),
    ("fonctionnaire_actif", "indice_liquidation", 2016): (-0.019, 0.011),
    ("fonctionnaire_actif", "indice_liquidation", 2025): (0.040, 0.070),
    ("fonctionnaire_actif", "pension_principale_eur", 2016): (-0.101, -0.071),
    ("fonctionnaire_actif", "pension_principale_eur", 2025): (0.031, 0.061),
    ("militaire", "taux_liquidation", 2016): (-0.074, -0.044),
    ("militaire", "taux_liquidation", 2025): (-0.110, -0.080),
    ("militaire", "indice_liquidation", 2016): (-0.008, 0.022),
    ("militaire", "indice_liquidation", 2025): (0.043, 0.073),
    ("militaire", "pension_principale_eur", 2016): (0.013, 0.043),
    ("militaire", "pension_principale_eur", 2025): (0.037, 0.067),
}

#: L'écart du stock que la page sert, pesé comme elle, au stock de droit direct
#: du jaune : en 2016 et en 2025 au tableau A-4, accessoires compris, et en
#: 2025 au A-5, avantage principal seul — ce que la page sert.
ECARTS_DU_STOCK_DECLARES = {
    ("fonctionnaire_sedentaire", 2016, "A-4"): (-0.114, -0.084),
    ("fonctionnaire_sedentaire", 2025, "A-4"): (-0.061, -0.031),
    ("fonctionnaire_sedentaire", 2025, "A-5"): (-0.024, 0.006),
    ("fonctionnaire_actif", 2016, "A-4"): (-0.148, -0.118),
    ("fonctionnaire_actif", 2025, "A-4"): (-0.097, -0.067),
    ("fonctionnaire_actif", 2025, "A-5"): (-0.041, -0.011),
    ("militaire", 2016, "A-4"): (-0.174, -0.144),
    ("militaire", 2025, "A-4"): (-0.075, -0.045),
    ("militaire", 2025, "A-5"): (-0.033, -0.003),
}


@pytest.fixture(scope="module")
def annuelles():
    return flux.mesures_annuelles_du_depot(Parametres())


@pytest.fixture(scope="module")
def stock():
    return flux.stock_du_depot(Parametres())


def test_chaque_cas_type_part_chaque_annee_ou_le_droit_le_fait_partir(annuelles):
    """De 2016 à 2025, chaque cas type part chaque année où le droit fait
    partir l'une de ses générations : le sédentaire de 1960 part en 2023,
    celui de 1961 en 2025 ; l'actif de 1957 en 2017, celui de 1958 en 2019,
    celui de 1960 en 2022."""
    annees = {}
    for m in annuelles:
        annees.setdefault(m.cas_type, set()).add(m.annee)
    assert annees == {"fonctionnaire_sedentaire": set(flux.ANNEES) - {2024},
                      "fonctionnaire_actif": set(flux.ANNEES) - {2018, 2021},
                      "militaire": set(flux.ANNEES)}


@pytest.mark.parametrize("cle", sorted(ECARTS_ANNUELS_DECLARES),
                         ids=lambda c: f"{c[0]}-{c[1]}-{c[2]}")
def test_chaque_ecart_annuel_tient_dans_sa_fourchette_declaree(annuelles, cle):
    """Comme ceux du flux de 2025 : une mesure qui sort de sa fourchette fait
    échouer la suite, et qui la déplace dit pourquoi."""
    mesure = next(m for m in annuelles if (m.cas_type, m.indicateur, m.annee) == cle)
    ecart = mesure.ecart if cle[1].startswith("age") else mesure.ecart_relatif
    bas, haut = ECARTS_ANNUELS_DECLARES[cle]
    assert bas <= ecart <= haut, (
        f"{cle} : {mesure.modele} pour {mesure.jaune} au tableau {mesure.tableau}, écart "
        f"{ecart:+.3f}, fourchette déclarée [{bas:+.3f}, {haut:+.3f}]")


def test_le_sedentaire_suit_le_taux_des_sedentaires_mais_pas_leur_age(annuelles):
    """Depuis l'étape 5, le sédentaire liquide au taux du flux hors décote et
    surcote : de 2016 à 2025, son taux baisse avec celui des sédentaires
    partis pour ancienneté (tableau 107), de deux à quatre points en dessous,
    et sa pension reste à 7 % au plus de celle du flux des civils — 6,6 %
    en 2022, quand le point remonte au 1er juillet. Son âge, lui, ne
    monte que de trois trimestres, le leur d'un an et neuf mois (tableau
    101) : parti après eux en 2016, il part avant eux en 2025."""
    sedentaire = {(m.indicateur, m.annee): m for m in annuelles
                  if m.cas_type == "fonctionnaire_sedentaire"}
    taux = [m for (i, _), m in sedentaire.items() if i == "taux_liquidation"]
    assert all(-0.045 <= m.ecart <= -0.015 for m in taux), [round(m.ecart, 3) for m in taux]
    assert taux[0].modele - taux[-1].modele > 0.025
    pension = [m for (i, _), m in sedentaire.items() if i == "pension_principale_eur"]
    assert all(abs(m.ecart_relatif) < 0.07 for m in pension)
    age = {a: m for (i, a), m in sedentaire.items() if i == "age_premiere_mise_en_paiement"}
    assert age[2025].modele - age[2016].modele == pytest.approx(0.75)
    assert age[2025].jaune - age[2016].jaune == pytest.approx(1.8)
    assert age[2016].ecart > 0 > age[2025].ecart


@pytest.mark.parametrize("cle", sorted(ECARTS_DU_STOCK_DECLARES),
                         ids=lambda c: f"{c[0]}-{c[1]}-{c[2]}")
def test_chaque_ecart_du_stock_tient_dans_sa_fourchette_declaree(stock, cle):
    """Le stock pesé comme la page la pèse, face au stock du jaune."""
    code, annee, tableau = cle
    accessoires, principal = flux.stock_publie(code, flux.referents_publies())[annee]
    jaune = accessoires if tableau == "A-4" else principal
    ecart = stock[code][annee] / jaune - 1
    bas, haut = ECARTS_DU_STOCK_DECLARES[cle]
    assert bas <= ecart <= haut, (
        f"{cle} : {stock[code][annee]:.0f} € pour {jaune:.0f} € au jaune, écart "
        f"{ecart:+.1%}, fourchette déclarée [{bas:+.1%}, {haut:+.1%}]")


def test_la_page_indexe_le_stock_sur_les_prix_que_le_droit_a_suivis_avec_retard(stock):
    """La page compte en euros constants : le stock qu'elle sert suit les prix
    dès l'année où ils montent. Le droit revalorise les pensions au 1er
    janvier, sur l'inflation passée : en 2023, il ne les augmente que de
    0,8 % quand les prix montent de près de 5 %, et rattrape en 2024 (5,3 %).
    L'écart du sédentaire au jaune bondit en 2023, puis retombe."""
    publies = flux.referents_publies()
    sedentaire = flux.stock_publie("fonctionnaire_sedentaire", publies)
    ecart = {a: stock["fonctionnaire_sedentaire"][a] / sedentaire[a][0] - 1
             for a in (2022, 2023, 2024)}
    assert ecart[2023] > ecart[2022] + 0.03
    assert ecart[2024] < ecart[2023] - 0.02


def test_le_droit_a_revalorise_les_pensions_moins_vite_que_les_prix_depuis_2016():
    """De janvier 2016 à janvier 2025, le droit a revalorisé de 16,1 % une
    pension de plus de 2 014 € par mois — rien en 2016 ni en 2018, 0,3 % en
    2019 et 2020 —, quand les prix montaient de 20,7 % : la page, qui indexe
    le stock sur les prix, sert aux retraités partis avant 2016 un vingt-cinquième
    de plus que le droit."""
    from retraite_notionnelle.simulateur import Simulateur

    chemin = RACINE / "data/reference/legislation/revalorisation_pensions.csv"
    with chemin.open(encoding="utf-8") as fichier:
        lignes = list(csv.DictReader(l for l in fichier if not l.lstrip().startswith("#")))
    revalorisation = 1.0
    for ligne in lignes:
        if "2016-01-01" < ligne["date_effet"] <= "2025-01-01" and not ligne["mensuel_au_plus"]:
            revalorisation *= float(ligne["coefficient"])
    prix = Simulateur(Parametres()).macro.coefficient_prix(2016, 2025)
    assert revalorisation == pytest.approx(1.161, abs=0.001)
    assert prix == pytest.approx(1.207, abs=0.002)
    assert prix / revalorisation - 1 == pytest.approx(0.04, abs=0.005)
