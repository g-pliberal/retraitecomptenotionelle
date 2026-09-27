"""Le pont par lequel le Python lit le site : ``retraite_notionnelle.web.site``.

Le texte du site n'est écrit qu'une fois, en JavaScript (docs/architecture.md,
§ 8). Les tests des pages, les témoins de pages, les sondes de la prose le
lisent par ce pont : ce fichier tient ce qu'ils en supposent.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.web.site import (
    Donnee,
    ErreurSite,
    ObjetJS,
    disponible,
    module,
    nom_js,
    rendre,
    site,
)

pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le site ne se lit pas sans lui")


@pytest.mark.parametrize(("python", "portage"), [
    ("fraction_en_mots", "fractionEnMots"),
    ("_VUES_DE_PAGE", "VUES_DE_PAGE"),
    ("TITRES", "TITRES"),
    ("Serie", "Serie"),
    ("_champs_modelisation", "champsModelisation"),
    ("depuis_requete", "depuisRequete"),
])
def test_un_nom_python_se_lit_sous_celui_du_portage(python, portage):
    assert nom_js(python) == portage


def test_une_page_se_rend_par_le_site():
    titre, corps = rendre("/cout", {})
    assert titre == module("pages").TITRES["/cout"]
    assert '<section class="cle" id="cout-flux"' in corps
    # La page entière est celle que le navigateur assemble.
    page = site().page("/cout", {})
    assert page.startswith(module("gabarit").entete("/cout")) and corps in page


def test_les_arguments_nommes_vont_a_leur_place():
    g = module("gabarit")
    assert g.pourcentage(0.25, decimales=0) == g.pourcentage(0.25, False, 0) == "25 %"
    with pytest.raises(ErreurSite, match="n'a pas de paramètre « inconnu »"):
        g.pourcentage(0.25, inconnu=1)


def test_une_instance_part_par_reference_et_revient_telle_quelle():
    g = module("gabarit")
    serie = g.Serie("Essai", [1.0, 2.0, 3.0], "var(--serie-1)")
    assert isinstance(serie, ObjetJS)
    assert serie.libelle == "Essai" and serie.valeurs == [1, 2, 3]
    figure = g.graphique("Un essai", [2000, 2001, 2002], [serie])
    assert "Un essai" in figure and "Essai" in figure


def test_une_methode_statique_et_une_methode_s_appellent():
    saisie = module("saisie").Saisie.depuis_requete({"naissance": "1975"})
    assert saisie.naissance == 1975
    assert "naissance=1975" in saisie.requete()


def test_une_donnee_se_lit_en_attributs_et_revient_avec_ses_tables():
    """Un objet de données revient comme un dictionnaire ; rendu en argument,
    c'est l'objet du portage qui repart, ses ``Map`` comprises."""
    contexte = site().contexte
    compte = module("pages").compte_flux(contexte, 2026)
    assert isinstance(compte, Donnee) and compte.pib == compte["pib"] > 0
    reglage = module("pages").reglage_proposition(contexte.cout().solde)
    assert reglage["sous_un"] == reglage.sous_un == reglage["sousUn"]


def test_ce_que_le_portage_n_exporte_pas_ne_se_lit_pas():
    with pytest.raises(AttributeError, match="n'exporte pas"):
        module("pages").CE_NOM_N_EXISTE_PAS  # noqa: B018


def test_une_erreur_du_portage_remonte_avec_son_message():
    with pytest.raises(ErreurSite, match="Niveau de revenu attendu"):
        module("saisie").Saisie.depuis_requete({"unite_revenu": "moyen", "salaire": "99"})


def test_un_objet_du_modele_ne_part_pas_dans_le_portage():
    """Le portage a ses propres objets : un objet Python recopié au hasard de ses
    champs s'y lirait de travers, et le pont le refuse."""
    from retraite_notionnelle.saisie import Saisie

    with pytest.raises(TypeError):
        module("pages").champs_modelisation(Saisie())
