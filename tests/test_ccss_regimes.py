"""Les tableaux « Données générales » des rapports à la CCSS
(``scripts/fetch/ccss_regimes.py``).

Les rapports collent leurs tableaux depuis Excel, en formulaires que la page
pose : la page porte le titre, le formulaire les lignes. Les cas sont
fabriqués à la main, tels que le lecteur PDF rend un rapport : ses pages, en
listes de lignes, et pour chacune les rangs des formulaires qu'elle pose.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import ccss_regimes as regimes  # noqa: E402

ENTETE = "2016 % 2017 % 2018 (p) % 2019 (p) %"


def test_un_en_tete_desordonne_se_remet_dans_l_ordre():
    """La lecture pose parfois une année d'en-tête à la fin de la ligne ; les
    lignes, elles, vont dans l'ordre des années. Une année coupée, « 2 015 »,
    se recolle ; une note qui cite trois fois 2017 n'est pas un en-tête."""
    colonnes = regimes._en_tete("% 2017 % 2018 (p) % 2019 (p) % 2016")
    assert [c for c in colonnes if c is not None] == [
        (2016, False), (2017, False), (2018, True), (2019, True)]
    assert [c[0] for c in regimes._en_tete("2 015 % 2016 % 2017 (p) % 2018 (p) %") if c] == [
        2015, 2016, 2017, 2018]
    assert regimes._en_tete("(***) Le taux T2 a été fixé à 11,81 % entre le 1er janvier 2017 "
                            "et le 30 avril 2017, puis 2017") is None


def test_des_montants_qui_se_suivent_se_partagent_entre_les_annees():
    """Sans taux entre eux, huit groupes de trois chiffres font quatre
    montants de deux groupes, et non 157, 784, 166 et 49."""
    colonnes = regimes._en_tete(ENTETE)
    ligne = "6,2 5,2 5,1 5,1 Bénéficiaires vieillesse 157 784 166 049 174 544 183 494"
    assert regimes._valeurs(ligne, "Bénéficiaires vieillesse", colonnes) == {
        2016: 157784.0, 2017: 166049.0, 2018: 174544.0, 2019: 183494.0}
    ligne = "Produits nets 1 207 2,8 1 263 4,6 1 298 2,8 1 337 3,0"
    assert regimes._valeurs(ligne, "Produits nets", colonnes) == {
        2016: 1207.0, 2017: 1263.0, 2018: 1298.0, 2019: 1337.0}


def test_un_tableau_finit_ou_un_autre_commence():
    """La ligne d'années qui ouvre le tableau suivant arrête la lecture."""
    colonnes = regimes._en_tete(ENTETE)
    lignes = [ENTETE, "Charges nettes 2 257 8,9 2 346 4,0 2 506 6,8 2 464 -1,7",
              ENTETE, "CHARGES NETTES 1 447 5,3 1 515 4,8 1 606 6,0 1 715 6,8"]
    assert regimes.lire_tableau(lignes, 0, colonnes) == {
        "Charges nettes": {2016: 2257.0, 2017: 2346.0, 2018: 2506.0, 2019: 2464.0}}


def test_chaque_titre_lit_le_formulaire_de_son_rang(monkeypatch):
    """Deux tableaux de données générales sur une page, leurs formulaires
    rangés AVANT elle dans le fichier : chaque titre lit le sien, et le même
    intitulé, « CHARGES NETTES », n'écrase pas celui de l'autre tableau. Le
    rapport de 2018 ne garde que les années closes, 2016 et 2017."""
    sommaire = ["Sommaire", "5.1 Régime des salariés agricoles ..........  163"]
    toutes = [ENTETE,
              "Cotisants vieillesse 672 075 -0,4 677 527 0,8 682 730 0,8 685 603 0,4",
              "CHARGES NETTES (hors transfert d'équilibrage) 11 345 0,6 11 532 1,6 11 909 3,3 12 230 2,7"]
    vieillesse = [ENTETE,
                  "Bénéficiaires vieillesse 2 517 500 0,4 2 514 076 -0,1 2 482 339 -1,3 2 448 446 -1,4",
                  "CHARGES NETTES (hors transfert d'équilibrage) 5 884 -0,3 5 899 0,3 5 967 1,1 6 028 1,0"]
    page = ["5 • Les autres régimes de base",
            "Tableau 1 ● Données générales – toutes branches",
            "Tableau 2 ● Données générales – branche vieillesse",
            "5.1 • Régime des salariés agricoles"]
    monkeypatch.setattr(regimes, "pages_et_formulaires",
                        lambda octets: ([sommaire, toutes, vieillesse, page], [[], [], [], [1, 2]]))
    trouves, orphelins = regimes.lire_rapport(2018, b"")
    regime = ("msa_salaries", "Régime des salariés agricoles")
    charges = "CHARGES NETTES (hors transfert d'équilibrage)"
    assert trouves == {
        (*regime, "toutes branches"): {"Cotisants vieillesse": {2016: 672075.0, 2017: 677527.0},
                                       charges: {2016: 11345.0, 2017: 11532.0}},
        (*regime, "branche vieillesse"): {"Bénéficiaires vieillesse": {2016: 2517500.0, 2017: 2514076.0},
                                          charges: {2016: 5884.0, 2017: 5899.0}},
    }, trouves
    assert orphelins == 0
