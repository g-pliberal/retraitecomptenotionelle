"""La TVA à taux unique que la proposition affecte à sa retraite.

Quatre choses s'y vérifient, et elles n'ont pas le même statut.

D'abord que l'ASSIETTE est celle du Trésor : les points publiés, le taux moyen
qu'ils donnent — le taux unique à recette constante — et le coût des taux
réduits, qu'un autre producteur, le Conseil des prélèvements obligatoires,
chiffrait du même ordre.

Ensuite que le PARTAGE est celui qui a été décidé : la TVA paie la garantie
vieillesse d'abord, le régime ensuite, et ne va à aucun autre système que la
proposition. C'est ce qui interdit de la compter deux fois.

Puis que ZÉRO rend l'ancienne convention, où la TVA n'était pas réformée.

Enfin que le défaut NE RÉFORME PAS la TVA : depuis le 24 septembre 2026, la
proposition garde les quatre taux d'aujourd'hui, et rien de la TVA ne va aux
retraites. Le mécanisme reste, comme variante, et les tests du partage le
tiennent sur des taux posés à la main.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.cout import DONT_IMPOTS, SoldeAnnuel
from retraite_notionnelle.donnees.tva import AssietteTva


@pytest.fixture(scope="module")
def tva() -> AssietteTva:
    return AssietteTva(RACINE_DONNEES)


# -- l'assiette ----------------------------------------------------------------


def test_les_assiettes_sont_le_centuple_des_points_publies(tva):
    """8,9 Md€ par point à 20 % : 890 Md€ d'assiette. Le point NET retire la
    TVA que paient les administrations, et il est plus petit partout."""
    assert tva.annee == 2025
    assert tva.assiettes(nette=False)[0.20] == pytest.approx(890_000.0)
    assert tva.assiettes()[0.20] == pytest.approx(750_000.0)
    for taux, nette in tva.assiettes().items():
        assert nette <= tva.assiettes(nette=False)[taux]


def test_le_taux_unique_a_recette_constante_est_sous_seize_pour_cent(tva):
    """Supprimer les taux réduits suffit à ce qu'un taux unique bien plus bas
    que 20 % rapporte autant que les quatre : 15,46 % sur l'assiette nette, à
    peine plus sur la brute. Les arrondis du Trésor laissent 15,3 à 15,6 %."""
    assert 0.153 < tva.taux_moyen() < 0.156
    assert 0.153 < tva.taux_moyen(nette=False) < 0.157
    assert tva.recette_supplementaire(tva.taux_moyen()) == pytest.approx(0.0, abs=1e-12)


def test_le_cout_des_taux_reduits_recoupe_celui_du_cpo(tva):
    """Tout aligner sur 20 % rapporterait 52 Md€ nets en 2025 ; le Conseil des
    prélèvements obligatoires chiffrait ce coût à 47 Md€ en 2021, et les
    recettes de TVA ont crû d'un peu plus d'un dixième depuis."""
    cout = sum((0.20 - taux) * assiette for taux, assiette in tva.assiettes().items())
    assert 50_000 < cout < 55_000


def test_l_assiette_nette_pese_un_peu_moins_de_quarante_pour_cent_du_pib(tva):
    assert 0.37 < tva.part_pib() < 0.40
    assert tva.recette_supplementaire(0.20) == pytest.approx(
        (0.20 - tva.taux_moyen()) * tva.part_pib())


# -- le partage ----------------------------------------------------------------


def _ligne(**champs) -> SoldeAnnuel:
    """Une année du bilan réduite à ce que la TVA regarde."""
    valeurs = dict(
        annee=2030, projete=True, ressources=0.14, depenses=0.14,
        rapports={"actuel": 1.0, "notionnel_liberal": 0.7,
                  "garantie_vieillesse_liberal": 0.03},
        pib=0.0, part_contributive=0.77, part_impots=0.15,
        annee_bascule=2026, parts={"impots_et_taxes": 0.15},
        tva_liberal=0.02, garantie_liberal=0.005,
    )
    valeurs.update(champs)
    return SoldeAnnuel(**valeurs)


def test_la_tva_paie_la_garantie_d_abord_et_le_regime_ensuite():
    ligne = _ligne()
    assert ligne.tva_garantie("notionnel_liberal") == pytest.approx(0.005)
    assert ligne.tva_de("notionnel_liberal") == pytest.approx(0.015)
    sans = replace(ligne, tva_liberal=0.0)
    assert (ligne.ressources_de("notionnel_liberal")
            - sans.ressources_de("notionnel_liberal")) == pytest.approx(0.015)


def test_quand_la_tva_ne_suffit_pas_le_regime_n_en_recoit_rien():
    ligne = _ligne(tva_liberal=0.003, garantie_liberal=0.005)
    assert ligne.tva_garantie("notionnel_liberal") == pytest.approx(0.003)
    assert ligne.tva_de("notionnel_liberal") == 0.0


def test_la_tva_ne_va_qu_a_la_proposition_et_seulement_apres_la_bascule():
    ligne = _ligne()
    for scenario in ("actuel", "notionnel_retroactif", "notionnel_prospectif_employeur"):
        assert ligne.tva_de(scenario) == 0.0
        assert ligne.tva_garantie(scenario) == 0.0
    avant = _ligne(annee=2025)
    assert avant.tva_de("notionnel_liberal") == 0.0
    assert avant.tva_garantie("notionnel_liberal") == 0.0


def test_une_baisse_de_tva_ne_se_prend_pas_sur_la_retraite():
    ligne = _ligne(tva_liberal=-0.01)
    assert ligne.tva_de("notionnel_liberal") == 0.0
    assert ligne.tva_garantie("notionnel_liberal") == 0.0


def test_la_tva_a_sa_ligne_dans_les_impots_affectes():
    """Les « dont » de l'impôt somment au poste, TVA comprise."""
    ligne = _ligne()
    for scenario in ("actuel", "notionnel_liberal"):
        postes = ligne.postes_ressources(scenario)
        assert sum(postes[code] for code in DONT_IMPOTS) == pytest.approx(
            postes["impots_et_taxes"])
    assert ligne.postes_ressources("notionnel_liberal")["impots_tva"] == pytest.approx(0.015)
    assert ligne.postes_ressources("actuel")["impots_tva"] == 0.0


# -- l'ancienne convention -----------------------------------------------------


def test_zero_rend_l_ancienne_convention(tva):
    """Zéro veut dire « la TVA n'est pas réformée », et non « une TVA à zéro »."""
    parametres = replace(Parametres(), taux_tva_liberal=0.0)
    assert tva.recette_supplementaire(parametres.taux_tva_liberal) == 0.0
    ligne = _ligne(tva_liberal=tva.recette_supplementaire(parametres.taux_tva_liberal))
    assert ligne.tva_de("notionnel_liberal") == 0.0
    assert ligne.tva_garantie("notionnel_liberal") == 0.0


def test_le_taux_par_defaut_est_celui_que_le_parti_a_decide():
    """Zéro : la proposition ne réforme pas la TVA (24 septembre 2026)."""
    assert Parametres().taux_tva_liberal == 0.0


def test_l_accueil_cite_ce_que_la_tva_rapporte(tva):
    """Les points de blocage de l'accueil citent ce que la TVA rapporte de plus
    que les quatre taux d'aujourd'hui, à la précision où ils l'écrivent : zéro
    quand elle n'est pas réformée, et l'accueil n'en dit alors rien."""
    from retraite_notionnelle.web.pages import MESURES_BLOCAGES

    rapporte = tva.recette_supplementaire(Parametres().taux_tva_liberal) * 100
    assert round(rapporte, 1) == MESURES_BLOCAGES["tva_affectee"]
